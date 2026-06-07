---
title: image-generate
audience: [maintainer]
content_mode: reference
track: developer-docs
last_updated: generated
---

# image-generate

> Erzeugt aus einem Text-Prompt ein Bild über ein austauschbares Provider-Backend (Cloudflare/Pollinations/Gemini) und schreibt Bild plus Metadaten-Sidecar an einen gewählten Pfad.

_Generates an image from a text prompt via a pluggable provider backend, writing the image plus a `<image>.meta.json` sidecar to an operator-chosen path. Backends are swappable via `--provider`: cloudflare (Cloudflare Workers AI FLUX.1-schnell, real free tier, DEFAULT), pollinations (auth-free, but public-feed/undocumented-licence — the tool forces private=true and shows a disclaimer), gemini (gemini-2.5-flash-image, requires billing). Wraps the bundled, stdlib-only `scripts/image_generate.py`. Invoke when the user asks to \"generate an image\", \"create a hero image or icon from a prompt\", \"render this prompt to a PNG\", \"turn a graphic-prompt-generator document into an image\", or equivalent German-language requests. Don't use for image editing, in-painting, or multi-turn refinement; for batch pipelines; or to author the prompt itself (use graphic-prompt-generator). Supports resume is not applicable: a generation is a single terminal call._

- **Plugin:** `nolte-shared`
- **Phase:** 4 Build (`build`)
- **Tags:** `design`
- **Quelle:** [skills/image-generate/SKILL.md](https://github.com/nolte/claude-shared/blob/main/skills/image-generate/SKILL.md)

## Anwenden wenn

- you want to generate an image from a text prompt to a chosen file path
- you want a free, terminal-driven text-to-image call without a chat UI
- you want to render a graphic-prompt-generator prompt document into an image

## Nicht anwenden wenn

- **You want to author the prompt rather than render it** → [`graphic-prompt-generator`](../../agents/nolte-shared/graphic-prompt-generator.md)
- **You want to remove a fake-transparency background or vectorise the result** → [`png-to-transparent-svg`](../../agents/nolte-shared/png-to-transparent-svg.md)

## Siehe auch

- [`graphic-prompt-generator`](../../agents/nolte-shared/graphic-prompt-generator.md)
- [`png-to-transparent-svg`](../../agents/nolte-shared/png-to-transparent-svg.md)

## Referenziert von

- [`graphic-prompt-generator`](../../agents/nolte-shared/graphic-prompt-generator.md)
- [`gemini-image-handoff`](gemini-image-handoff.md)

---

## Image Generate

Turns a text prompt into an image file on disk — no chat UI, scriptable into any pipeline — by driving the bundled, stdlib-only `scripts/image_generate.py`. Backends are **swappable via `--provider`** so the capability is not locked to one vendor's pricing or availability.

### Why this is a skill, not an agent

- **Operator-invoked slash command.** Reached as `/nolte-shared:image-generate` with a prompt, a provider, and a target path; the operator drives it directly rather than a parent dispatching a fire-and-forget worker.
- **Mid-flow confirmation is part of the contract.** Some providers surface a one-time data/licence notice the operator must acknowledge, and an existing target file must not be overwritten without confirmation. Those are interactive gates an agent's structured-report shape can't carry.
- **The result flows back into the conversation.** Written image and sidecar paths land in the operator's context so the next step (vectorising via [`png-to-transparent-svg`](../../agents/nolte-shared/png-to-transparent-svg.md), embedding) can follow inline.
- Counter-dimension: the generation itself is a single deterministic script call; that engine is isolated in the bundled script, while the load-bearing dimensions (operator invocation, the acknowledgement/overwrite gates) make this a skill.

### German trigger phrases

- „erzeuge ein Bild aus diesem Prompt", „generiere ein Hero-Bild / Icon", „rendere diesen Prompt als PNG", „mach aus dem graphic-prompt-generator-Dokument ein Bild"

### Providers

| `--provider` | Auth | Free? | Notes |
|---|---|---|---|
| `cloudflare` (default) | `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID` | Yes — 10k neurons/day, no credit card | FLUX.1-schnell (Apache-2.0), no watermark, no feed |
| `pollinations` | none (opt. `POLLINATIONS_API_TOKEN`) | Yes, auth-free | Operated by Myceli.AI OU (Estonia, GDPR). **Public feed by default — the tool forces `private=true`** (feed opt-out only, *not* a non-storage guarantee). The Terms grant **no explicit output licence** ("verify the model licence"); `safe` filter is off by default. One-time disclaimer; never the default. |
| `gemini` | `GEMINI_API_KEY` | **No — requires billing** (free-tier quota is 0 for this model) | `gemini-2.5-flash-image`; data-use notice shown |

### Inputs

- A **prompt**: inline `--prompt`, a `--prompt-file`, or a `--from-prompt-doc` graphic-prompt-generator document (`--variant light|dark` selects a section).
- A **target path** (`--out`), always explicit — never a silent default.
- The selected provider's credentials in the environment (none for pollinations).

### Operations

#### 1. `run`

Generate one image (or `n`) from the resolved prompt to the target path.

1. **Resolve prompt, provider, and path.** Default provider is `cloudflare`. If `--out` is missing, ask the operator — never invent a default.
2. **Pre-flight obvious failures in conversation.** If the provider's credentials are unset, relay the script's setup hint and stop. If the target file exists, confirm overwrite before passing `--force`.
3. **Run the bundled engine:**

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/image-generate/scripts/image_generate.py" \
       --provider <cloudflare|pollinations|gemini> --prompt "<prompt>" --out <path> \
       [--from-prompt-doc <doc> --variant <light|dark>] [-n <N>] [--seed <S>] \
       [--width <W> --height <H>] [--force]
   ```

   On the **first use of a provider that has a notice** (pollinations, gemini), the script prints a one-time disclaimer and requires acknowledgement; relay it and only pass `--accept-data-policy` once the operator has explicitly acknowledged it (a SHA-256 digest is persisted per provider, so they are not re-prompted until the notice text changes).
4. **Report the result.** On success, report each written image path and its `<image>.meta.json` sidecar (which records `provider`, `model`, `source`, `prompt`, `timestamp`, `mime_type`). On a non-zero exit, relay the script's actionable message and the exit code (`3` = quota/rate-limit or billing-required, `4` = auth failure, `1` = other, `2` = usage).

### Hard rules

- **Never** disable Pollinations' `private=true` — it is hard-coded in the script to keep prompts and images out of the public feed; do not work around it.
- **Never** pass `--accept-data-policy` before the operator has seen and acknowledged the provider's notice.
- **Never** pass `--force` to overwrite an existing file without explicit operator confirmation in the same turn.
- **Never** pass any provider's API key/token on the command line or echo it into the conversation; credentials travel only through environment variables.
- **Never** retry automatically on an HTTP 429 / billing-required (`limit: 0`) — surface the message and stop.
- For confidential or commercial work, prefer `cloudflare` (Cloudflare grants output ownership + FLUX.1-schnell is Apache-2.0, no feed) over `pollinations` (Terms grant no explicit output licence — they defer to the model's licence — and `private=true` is feed-opt-out only, not a non-storage guarantee).

### Gotchas

- **Pollinations returns JPEG.** Use a `.jpg` target to avoid the extension/MIME-mismatch warning (the image is still written either way).
- **Per-provider, digest-versioned consent.** Acks live at `$XDG_STATE_HOME/nolte-shared/image-generate/<provider>/ack`; each provider is acknowledged independently, and a changed notice re-prompts automatically.
- **`n>1` writes `<stem>-1`, `<stem>-2`, …** with one sidecar each; the `prompt` is identical across all.
- **Cloudflare needs both** `CLOUDFLARE_API_TOKEN` (scope: Workers AI) **and** `CLOUDFLARE_ACCOUNT_ID`.
- **`${CLAUDE_PLUGIN_ROOT}` is load-bearing — don't "simplify" it to a repo-relative path.** The bundled script lives in the installed plugin directory, not the consumer repo's working tree; `${CLAUDE_PLUGIN_ROOT}` resolves to the plugin root in every context (marketplace install and `claude --plugin-dir .` dogfooding). A bare `skills/image-generate/scripts/…` path only works inside `claude-shared` itself and breaks the skill in every consumer repo. Data paths (`--out`, `--from-prompt-doc`) stay relative to the consumer's working directory — only the script path is plugin-rooted.

### Examples

- Read `examples/01-cloudflare-default.md` for the default free-tier path (Cloudflare token + account id → PNG).
- Read `examples/02-pollinations-disclaimer.md` for the auth-free path and the public-feed/licence disclaimer.
- Read `examples/03-from-prompt-doc.md` for rendering a [`graphic-prompt-generator`](../../agents/nolte-shared/graphic-prompt-generator.md) document's Dark-Mode section.
