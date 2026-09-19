---
title: Image Generation
audience: [maintainer, external-contributor]
content_mode: how-to
track: developer-docs
last_updated: 2026-09-19
---

# Image Generation

The `image-generate` skill turns a text prompt into an image file on disk, fully from the command line, so it drops into any pipeline. It has **swappable provider backends** (selected with `--provider`) so the capability isn't locked to one vendor's pricing or availability.

The deterministic engine is a stdlib-only script, `plugins/nolte-media/skills/image-generate/scripts/image_generate.py`; the skill is the operator-facing wrapper.

## Providers at a glance

| `--provider` | Credentials needed | Free? | Output licence | Use it for |
|---|---|---|---|---|
| `cloudflare` (**default**) | `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID` | Yes, real free tier (no card) | FLUX.1-schnell (default) or FLUX.2 Klein 4B via `--model`, both Apache-2.0; you own the output | Blog and production images; Klein 4B for non-square sizes and reference images |
| `pollinations` | none (optional `POLLINATIONS_API_TOKEN`) | Yes, auth-free | No explicit licence (defers to the model); public-feed default | Quick throwaway images |
| `gemini` | `GEMINI_API_KEY` | No, **requires billing** | Commercial use allowed | Only if you already pay for it |

**Recommendation:** use `cloudflare` for anything you publish. It's free, carries no watermark or public feed, and both of its models, FLUX.1-schnell and FLUX.2 Klein 4B, are Apache-2.0, so the generated images are clearly yours to use. The licence is a property of the model, not of the provider: Cloudflare also hosts `flux-2-klein-9b` and `flux-2-dev` under the FLUX Non-Commercial License, and the tool deliberately doesn't offer them. `pollinations` is fine for disposable images but grants no explicit output licence; `gemini` needs a billed project (its free-tier quota for this image model is zero).

## Which token does each provider need?

### Cloudflare (default, recommended)

Cloudflare Workers AI runs FLUX.1-schnell and FLUX.2 Klein 4B on a real recurring free tier (10,000 neurons/day, no credit card). You need a **token** and your **account id**:

1. Create a free account at <https://dash.cloudflare.com/sign-up> (no card required).
2. In the dashboard go to **AI → Workers AI → "Use REST API"** (REST is Representational State Transfer).
3. Click **Create a Workers AI API Token**. Cloudflare pre-fills the right permissions:
   - `Account` · `Workers AI` · **Read**
   - `Account` · `Workers AI` · **Edit** (this one is required, because generating an image is a `run`/Edit action)
4. Create the token and copy it (shown only once).
5. Copy your **Account ID** from the same page.

Then export both (the tool reads them only from the environment, never as a flag):

```bash
export CLOUDFLARE_API_TOKEN="your_token"
export CLOUDFLARE_ACCOUNT_ID="your_account_id"
```

The free tier resets daily. FLUX.1-schnell costs about 58 neurons per 1024x1024 image (4.8 per 512x512 tile plus 9.6 per step), FLUX.2 Klein 4B about 104 (26 per output tile), so 10,000 neurons/day is roughly 170 schnell images or 95 Klein 4B images.

### Pollinations (auth-free)

No token is required. Optionally set `POLLINATIONS_API_TOKEN` to remove the watermark that anonymous requests carry. The first run prints a one-time disclaimer (public feed, no explicit output licence) that you must acknowledge.

### Gemini (billing required)

Set `GEMINI_API_KEY` from <https://aistudio.google.com/apikey>. Note that no Gemini image model **is** on the free tier (the free-tier quota is `0`), `gemini-3.1-flash-image` included; the project must have billing enabled or every call returns a billing-required error.

## Generate an image

The default provider is `cloudflare`, so no `--provider` is needed for it:

```bash
# via the Taskfile (pass script args after --)
task image:generate -- --prompt "a minimalist teal fox icon, flat" --out fox.jpg

# or directly
python3 "${CLAUDE_PLUGIN_ROOT}/skills/image-generate/scripts/image_generate.py" \
    --prompt "a minimalist teal fox icon, flat" --out fox.jpg
```

Switch backends with `--provider`:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/image-generate/scripts/image_generate.py" \
    --provider pollinations --prompt "a tree, comic style" --out tree.jpg --accept-data-policy
```

Every run writes the image plus a `<image>.meta.json` sidecar recording `provider`, `model`, `source`, `prompt`, `timestamp`, and `mime_type`.

Useful flags: `--from-prompt-doc <doc> --variant light|dark` (render a `graphic-prompt-generator` document), `-n <N>` (several images of the same prompt), `--seed`, `--width`/`--height`, `--model` and `--ref-image` (Cloudflare only, see below), `--force` (overwrite an existing file).

## Choosing the Cloudflare model

`--provider cloudflare` offers two models, selected with `--model`:

| `--model` | Licence | Size control | Reference images | Cost per 1024x1024 image |
|---|---|---|---|---|
| `flux-1-schnell` (**default**) | Apache-2.0 | none: always about 1024x1024, `--width`/`--height` are ignored with a warning | no | about 58 neurons |
| `flux-2-klein-4b` | Apache-2.0 | `--width`/`--height` honoured, 256 to 1920 each | up to four `--ref-image` files, each under 512x512 | about 104 neurons |

Render a wide hero image and condition it on a reference image:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/image-generate/scripts/image_generate.py" \
    --model flux-2-klein-4b --width 1280 --height 720 \
    --ref-image design/mascot-ref.png \
    --prompt "the mascot waving in front of a sunrise, flat illustration" --out hero.png
```

The sidecar then records `model: @cf/black-forest-labs/flux-2-klein-4b` and a `reference_images` list with each file's name and SHA-256 digest. Reference images are uploaded to Cloudflare as part of the request; keep confidential material out of them. `--model` and `--ref-image` are rejected with a usage error on every other provider, and `--ref-image` also on `flux-1-schnell`.

`flux-1-schnell` stays the default because it costs about half as much per image and its response format is long verified; Klein 4B's response handling covers both shapes Cloudflare documents (base64 JSON and raw bytes) but hasn't been confirmed against a live call yet.

!!! tip
    FLUX.1-schnell and Pollinations both return JPEG. Use a `.jpg` target to avoid the extension/MIME-mismatch warning (MIME is Multipurpose Internet Mail Extensions) (the image is still written either way). Klein 4B's format is detected from the response, so match the extension to what the sidecar's `mime_type` reports.

## Using it in another repo

When the `nolte-media` plugin is installed in another repository, this capability is reachable there as `/nolte-media:image-generate`; nothing is copied into the consumer repo. The skill invokes the bundled script through `${CLAUDE_PLUGIN_ROOT}`, which resolves to the installed plugin's directory in any context (marketplace install and `claude --plugin-dir ./plugins/nolte-media` dogfooding), so the same command works everywhere:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/image-generate/scripts/image_generate.py" \
    --prompt "a teal fox icon, flat" --out fox.jpg
```

Only the *script* path is plugin-rooted; data paths (`--out`, `--from-prompt-doc`) stay relative to the consumer's working directory. The `task image:generate` shortcut is `claude-shared`-local (it runs the repo-relative script outside Claude); consumer repos use the slash command instead.

## Fits a pipeline

The tool closes a three-step asset pipeline:

1. `graphic-prompt-generator` (agent) authors a brand-conformant prompt document under `design/prompts/`.
2. `image-generate` renders it: `--from-prompt-doc design/prompts/hero.md --variant dark --out hero.jpg`.
3. `png-to-transparent-svg` (agent) turns the result into a vector for an icon or logo.

## Exit codes

`0` success · `1` runtime error (network, filesystem, malformed response) · `2` usage error · `3` rate limit / quota / billing-required · `4` authentication failure. Nothing is retried automatically on `429`.
