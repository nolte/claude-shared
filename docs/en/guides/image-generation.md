---
title: Image Generation
audience: [maintainer, external-contributor]
content_mode: how-to
track: developer-docs
last_updated: 2026-05-30
---

# Image Generation

The `image-generate` skill turns a text prompt into an image file on disk, fully from the command line, so it drops into any pipeline. It has **swappable provider backends** (selected with `--provider`) so the capability isn't locked to one vendor's pricing or availability.

The deterministic engine is a stdlib-only script, `skills/image-generate/scripts/image_generate.py`; the skill is the operator-facing wrapper.

## Providers at a glance

| `--provider` | Credentials needed | Free? | Output licence | Use it for |
|---|---|---|---|---|
| `cloudflare` (**default**) | `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID` | Yes, real free tier (no card) | FLUX.1-schnell, Apache-2.0; you own the output | Blog and production images |
| `pollinations` | none (optional `POLLINATIONS_API_TOKEN`) | Yes, auth-free | No explicit licence (defers to the model); public-feed default | Quick throwaway images |
| `gemini` | `GEMINI_API_KEY` | No, **requires billing** | Commercial use allowed | Only if you already pay for it |

**Recommendation:** use `cloudflare` for anything you publish. It's free, carries no watermark or public feed, and FLUX.1-schnell is Apache-2.0, so the generated images are clearly yours to use. `pollinations` is fine for disposable images but grants no explicit output licence; `gemini` needs a billed project (its free-tier quota for this image model is zero).

## Which token does each provider need?

### Cloudflare (default, recommended)

Cloudflare Workers AI runs FLUX.1-schnell on a real recurring free tier (10,000 neurons/day, no credit card). You need a **token** and your **account id**:

1. Create a free account at <https://dash.cloudflare.com/sign-up> (no card required).
2. In the dashboard go to **AI → Workers AI → "Use REST API"**.
3. Click **"Create a Workers AI API Token"**. Cloudflare pre-fills the right permissions:
   - `Account` · `Workers AI` · **Read**
   - `Account` · `Workers AI` · **Edit** (this one is required, because generating an image is a `run`/Edit action)
4. Create the token and copy it (shown only once).
5. Copy your **Account ID** from the same page.

Then export both (the tool reads them only from the environment, never as a flag):

```bash
export CLOUDFLARE_API_TOKEN="your_token"
export CLOUDFLARE_ACCOUNT_ID="your_account_id"
```

The free tier resets daily; FLUX.1-schnell costs ~4.8 neurons per 512x512 tile, so 10,000 neurons/day is roughly hundreds of images.

### Pollinations (auth-free)

No token is required. Optionally set `POLLINATIONS_API_TOKEN` to remove the watermark that anonymous requests carry. The first run prints a one-time disclaimer (public feed, no explicit output licence) that you must acknowledge.

### Gemini (billing required)

Set `GEMINI_API_KEY` from <https://aistudio.google.com/apikey>. Note that `gemini-2.5-flash-image` **isn't** on the free tier (its free-tier quota is `0`); the project must have billing enabled or every call returns a billing-required error.

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

Useful flags: `--from-prompt-doc <doc> --variant light|dark` (render a `graphic-prompt-generator` document), `-n <N>` (several images of the same prompt), `--seed`, `--width`/`--height`, `--force` (overwrite an existing file).

!!! tip
    Cloudflare and Pollinations both return JPEG. Use a `.jpg` target to avoid the extension/MIME-mismatch warning (the image is still written either way).

## Using it in another repo

When the `nolte-shared` plugin is installed in another repository, this capability is reachable there as `/nolte-shared:image-generate`; nothing is copied into the consumer repo. The skill invokes the bundled script through `${CLAUDE_PLUGIN_ROOT}`, which resolves to the installed plugin's directory in any context (marketplace install and `claude --plugin-dir .` dogfooding), so the same command works everywhere:

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
