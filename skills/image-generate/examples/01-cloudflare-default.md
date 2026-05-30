# Example 1 — Cloudflare (default, free tier) → PNG

The default provider. Cloudflare Workers AI runs FLUX.1-schnell (Apache-2.0) with a
real recurring free tier (10,000 neurons/day, no credit card) and no watermark or
public feed.

## Setup (one-time)

Create a free Cloudflare account, then an API token scoped to **Workers AI**, and
note your **Account ID** (Workers & Pages → right sidebar):

```bash
export CLOUDFLARE_API_TOKEN="…"     # scope: Workers AI
export CLOUDFLARE_ACCOUNT_ID="…"
```

## Generate

```bash
python3 skills/image-generate/scripts/image_generate.py \
    --prompt "a minimalist teal fox icon, flat, thick outlines" \
    --out assets/fox.png
```

(`--provider cloudflare` is implied by default.)

## Expected result

```
wrote assets/fox.png (… bytes) + fox.png.meta.json [cloudflare]
```

The sidecar `assets/fox.png.meta.json` records `provider: cloudflare`,
`model: @cf/black-forest-labs/flux-1-schnell`, the prompt, an RFC-3339 timestamp,
and the MIME type. No consent prompt — Cloudflare's output licence is clear.

## Failure modes

- **Missing `CLOUDFLARE_API_TOKEN` / `CLOUDFLARE_ACCOUNT_ID`** → setup hint naming both
  variables and the free-tier neuron budget; exit code 1, no network call.
- **HTTP 429** → quota/rate-limit message, exit code 3, never retried.
