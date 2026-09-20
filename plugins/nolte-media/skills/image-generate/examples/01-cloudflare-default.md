# Example 1 — Cloudflare (default, free tier) → PNG

The default provider. Cloudflare Workers AI offers two FLUX models here, both with
Apache-2.0 model weights: **FLUX.1-schnell** (`--model flux-1-schnell`, the default)
and **FLUX.2 Klein 4B** (`--model flux-2-klein-4b`). Both draw on the same real
recurring free tier (10,000 neurons/day, no credit card) and carry no watermark or
public feed.

## Setup (one-time)

Create a free Cloudflare account, then an API token scoped to **Workers AI**, and
note your **Account ID** (Workers & Pages → right sidebar):

```bash
export CLOUDFLARE_API_TOKEN="…"     # scope: Workers AI
export CLOUDFLARE_ACCOUNT_ID="…"
```

## Generate (schnell, default)

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/image-generate/scripts/image_generate.py" \
    --prompt "a minimalist teal fox icon, flat, thick outlines" \
    --out assets/fox.png
```

(`--provider cloudflare --model flux-1-schnell` is implied by default.)

## Expected result

```
wrote assets/fox.png (… bytes) + fox.png.meta.json [cloudflare]
```

The sidecar `assets/fox.png.meta.json` records `provider: cloudflare`,
`model: @cf/black-forest-labs/flux-1-schnell`, the prompt, an RFC-3339 timestamp,
and the MIME type. No consent prompt — Cloudflare's output licence is clear.

FLUX.1-schnell always renders 1024×1024. Passing `--width`/`--height` to it prints
`warning: flux-1-schnell ignores --width/--height and always renders 1024x1024; pass
--model flux-2-klein-4b to control width and height.` on stderr and proceeds unchanged.

## Klein 4B: non-square image with reference images

FLUX.2 Klein 4B honours `--width`/`--height` (256–1920 each) and accepts up to four
`--ref-image` files (each meant to be under 512×512; the endpoint, not the tool,
enforces that). **Reference images are uploaded to Cloudflare.** It costs ≈ 1.8× as
many neurons per image as schnell (≈ 104 versus ≈ 58 for 1024×1024), so the same
free day yields roughly 95 instead of 170 images.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/image-generate/scripts/image_generate.py" \
    --model flux-2-klein-4b --width 1280 --height 720 \
    --ref-image ref.png \
    --prompt "the same teal fox as a wide hero banner, flat, thick outlines" \
    --out assets/fox-hero.png
```

Expected result:

```
wrote assets/fox-hero.png (… bytes) + fox-hero.png.meta.json [cloudflare]
```

The sidecar `assets/fox-hero.png.meta.json` now carries
`model: @cf/black-forest-labs/flux-2-klein-4b` and, because a reference image was
supplied, a `reference_images` list:

```json
{
  "provider": "cloudflare",
  "model": "@cf/black-forest-labs/flux-2-klein-4b",
  "reference_images": [
    {"name": "ref.png", "sha256": "<hex digest of ref.png>"}
  ],
  "prompt": "the same teal fox as a wide hero banner, flat, thick outlines",
  "…": "source, timestamp, mime_type as for schnell"
}
```

The response shape of the Klein 4B endpoint isn't live-verified yet; the tool
accepts both a base64 JSON envelope and raw image bytes and sniffs the MIME type
(PNG/JPEG/WEBP) from the bytes.

## Failure modes

- **Missing `CLOUDFLARE_API_TOKEN` / `CLOUDFLARE_ACCOUNT_ID`** → setup hint naming both
  variables and the free-tier neuron budget; exit code 1, no network call.
- **HTTP 429** → quota/rate-limit message, exit code 3, never retried.
- **`--ref-image` on schnell** (or on any other provider) → `--ref-image requires
  --provider cloudflare --model flux-2-klein-4b; 'flux-1-schnell' does not accept
  reference images`; exit code 2, no network call. A fifth `--ref-image` → `--ref-image
  accepts at most 4 images (got 5)`, exit code 2.
- **Unreadable `--ref-image` path** → `cannot read --ref-image: <OSError>`; exit code 1,
  no network call.
- **`--ref-image` that is not a regular file** (directory, device, FIFO) → `--ref-image
  '<path>' is not a regular file. Directories, devices, and FIFOs cannot be uploaded —
  pass the path of an image file.`; exit code 2, no network call.
- **`--ref-image` with an unsupported extension** (`.gif`, or none) → `--ref-image '<path>'
  has an unsupported extension '.gif'. Supported: .jpeg, .jpg, .png, .webp.` plus the
  convert-or-rename hint; exit code 2, no network call — the file is never uploaded under
  an unknown type.
- **`--ref-image` above 20 MiB** → `--ref-image '<path>' is <size> bytes, above the 20 MiB
  read cap (MAX_REF_IMAGE_BYTES).` plus the downscale hint; exit code 2, no network call.
- **Response body above 64 MiB** → `the provider response body exceeds the 64 MiB safety
  cap (MAX_RESPONSE_BYTES); the response was discarded and nothing was written.`; exit
  code 1, no file written.
- **`--model` on `pollinations` or `gemini`** → `--model is only supported by the
  cloudflare provider, not '<provider>'`; exit code 2.
