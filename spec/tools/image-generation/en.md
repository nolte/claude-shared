# Image Generation (Multi-Provider)

Status: draft

## Context

Image generation should be reachable from the terminal—a prompt in, an image file on disk out—without opening a chat UI, and scriptable into any pipeline. No single vendor is a safe long-term bet: pricing, free-tier quotas, and model availability change without notice. This spec therefore governs a **multi-provider** capability with swappable backends, implemented by the `image-generate` skill driving the bundled `scripts/image_generate.py`.

This spec supersedes the earlier "Gemini Image Generation (Free-Tier)" spec, whose central premise proved false: `gemini-2.5-flash-image` reports a Free-Tier quota of `limit: 0` and **requires billing** (verified live; see the project history around the `image-generate` work). "Free tier" is therefore a **per-provider property, not a guarantee of the tool**, and model-ID pinning can't by itself guarantee zero cost—the same model is free or paid depending on the project's billing status.

Three constraints shape the design:

1. **No vendor lock-in.** The provider is selected at call time (`--provider`); adding or removing a backend must not touch the shared CLI, output, or sidecar contract.
2. **Safe defaults.** The default provider must have a real, documented free tier and a clear output licence. A provider with privacy or licensing risk must never be the default and must surface those risks before first use.
3. **Honest failures.** Provider error bodies must be surfaced, not swallowed; a permanent `limit: 0` / billing-required condition must be distinguished from a temporary rate-limit.

## Goals

- One invocation turns a text prompt into an image file at an operator-chosen path, via any configured provider.
- The default provider (`cloudflare`) needs no billing and carries a clear output licence.
- Each generated image carries a sidecar with enough metadata to reproduce or audit the call, including which provider produced it.
- Privacy- or licence-risky providers are usable only behind explicit, acknowledged safeguards.

## Non-Goals

- Image editing / in-painting / multi-turn refinement—text-to-image only.
- Batch pipelines (n prompts per job)—one prompt per invocation (`-n` requests multiple images of the **same** prompt).
- A local/self-hosted provider (`stable-diffusion.cpp`)—a planned follow-up, out of scope for this iteration.
- Guaranteeing any provider stays free—quotas are the providers' to change.
- Midjourney as a provider—it has no scriptable text-to-image API reachable from the terminal, so it's deliberately absent from the fixed `--provider` registry. `spec/design/graphic-prompt-authoring/` may author a Midjourney-targeted prompt document, but this tool never generates against Midjourney; the two specs meet only at the prompt artifact, not at a shared backend.

## Requirements

### Provider-agnostic (shared layer)
- **MUST** select the provider via `--provider` from a fixed registry; the default **MUST** be `cloudflare`.
- **MUST** read every provider credential only from environment variables; **MUST NOT** accept a key via CLI flag or config file, and **MUST NOT** log, echo, or write any credential (including in errors and sidecars).
- **MUST** require an explicit target path (`--out`); no silent default to the working directory. **MUST** refuse to overwrite an existing target without explicit confirmation (`--force`).
- **MUST** write a `<image>.meta.json` sidecar next to every image, containing at least `provider`, `model`, `source`, `prompt`, `timestamp` (RFC 3339 UTC), and `mime_type`.
- **MUST** treat HTTP 429 as terminal for the invocation (no automatic retry) and **MUST** distinguish a `limit: 0` / billing-required condition (retrying never helps) from a temporary rate-limit, with an actionable message either way.
- **MUST** surface the provider's actual error-response body (not only the status code) in the operator-facing message.
- **MUST** treat HTTP 401/403 as a terminal auth error pointing at the provider's credential page; any other failure (network, DNS, filesystem, malformed response) **MUST** produce a readable message and a non-zero exit, never a raw stack trace as the only output.
- **SHOULD** derive the format from the target extension and warn (not fail) on a MIME mismatch; the image is still written, because the quota was already spent.
- **MUST** offer a one-time, digest-versioned acknowledgement mechanism, keyed **per provider** under `$XDG_STATE_HOME/nolte-shared/image-generate/<provider>/ack`, for providers that declare a notice.
- **MUST** invoke the bundled script through `${CLAUDE_PLUGIN_ROOT}` rather than a repo-relative path, so the skill works from any consumer repository that installs the plugin (the script lives in the installed plugin directory, not the consumer's working tree); only data paths (`--out`, `--from-prompt-doc`) stay relative to the consumer's working directory.

### `cloudflare` (default)
- **MUST** call Cloudflare Workers AI FLUX.1-schnell (Apache-2.0 output) using `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID`; absence of either yields a setup hint naming both and the free-tier neuron budget. No data/licence notice is required.
- **SHOULD** follow the model-level FLUX invariants in `spec/design/flux-image-generation/` for this provider: natural-language prompts (no SDXL comma-tags or prompt weights), `guidance = 0`, `steps ≤ 8`, and no negative prompts (unwanted attributes phrased positively).

### `pollinations`
- **MUST** force `private=true` on every request (opt out of the public feed) and **MUST NOT** expose a CLI flag to disable it.
- **MUST** present a one-time disclaimer, requiring acknowledgement before first use, covering: the public-feed default; that `private=true` is a feed opt-out only and **not** a non-storage guarantee (response caches persist, per the provider's privacy policy); and that the Terms grant **no explicit output licence** (deferring to the underlying model's licence).
- **MUST NOT** be the default provider.
- **MUST** send a browser-style `User-Agent`; the default `urllib` UA is rejected by Pollinations' Cloudflare bot protection (HTTP 403, error 1010).

### `gemini`
- **MUST** pin the model ID `gemini-2.5-flash-image` and the `v1beta` generativelanguage endpoint; paid `imagen-*` models and Vertex AI endpoints (`*-aiplatform.googleapis.com`) **MUST** be unreachable.
- **MUST** make the billing requirement explicit (the model's Free-Tier quota is 0) in both the setup hint and the one-time notice.
- **SHOULD** follow the model-level Gemini invariants in `spec/design/gemini-image-generation/` for this provider: narrative prompts with stated intent (not SDXL comma-tags), unwanted attributes phrased positively (no negative-prompt parameter exists), quoted literals for in-image text, and awareness that every output carries a SynthID watermark.

## Manual UI-handoff path (no API call)

The `gemini` provider above requires billing. A **semi-automatic alternative** sidesteps the API entirely and is owned by the `gemini-image-handoff` skill: a Gemini-optimised prompt is authored, then the operator pastes it into the Gemini web UI (the Gemini app or AI Studio) and downloads the image from the chat. This path:

- **MUST NOT** make any API call; it therefore carries no billing requirement and needs no `GEMINI_API_KEY`.
- **MUST** author the prompt to the model baseline in `spec/design/gemini-image-generation/`; the automated half is the prompt, the manual half is the operator's UI step.
- writes **no** image file and **no** sidecar; file placement and provenance are the operator's responsibility, and the sidecar contract above binds only the API-backed providers.
- **MUST** surface the SynthID-watermark caveat (every Gemini UI output is watermarked) so a commercial or blog asset choice is informed.
- **MUST NOT** be conflated with the `gemini` API provider above; it's a distinct, no-network path.

## Acceptance Criteria

- [ ] `--provider` defaults to `cloudflare`; an unknown provider is a usage error.
- [ ] Static inspection shows no `imagen-*` literal and no `*-aiplatform.googleapis.com` call in the executable code.
- [ ] Every generated image has a `<image>.meta.json` sidecar carrying the six required keys, including the correct `provider`; no credential appears in any sidecar.
- [ ] With the selected provider's credentials unset, the tool prints a setup hint naming the required variables and exits non-zero without a network call (cloudflare, gemini).
- [ ] A simulated HTTP 429 with `limit: 0` yields a billing-required message (not "retry later"); a 429 without it yields a rate-limit message; neither retries.
- [ ] A provider HTTP error surfaces the upstream `error.message` text in the operator-facing message.
- [ ] Every `pollinations` request URL contains `private=true`, and there is no flag to disable it; the first `pollinations` run prints the feed/licence disclaimer and requires acknowledgement.
- [ ] Invocation without `--out` is a usage error; invocation over an existing file is rejected unless `--force`.
- [ ] The acknowledgement path contains the provider name; two providers acknowledge independently; rewriting a stored digest re-prompts.
- [ ] The manual UI-handoff path makes no network call and writes no image or sidecar; it emits a prompt conforming to the Gemini baseline plus the UI entry and download steps, and states the SynthID caveat.

## Open Questions

- A local/self-hosted provider (`stable-diffusion.cpp`: zero running cost, full privacy, no rate limits) is the planned next backend; deferred here because of its build/model-download/GPU setup surface.
- Pollinations' output licence and prompt-retention remain externally undocumented (upstream issue #8741 unresolved). The safeguard (forced `private=true` + disclaimer) is the mitigation; revisit if Pollinations publishes formal terms.
