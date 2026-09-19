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

- In-painting and multi-turn refinement—the tool generates in one terminal call. Reference-image conditioned generation on the `cloudflare` model `flux-2-klein-4b` **is** in scope (that model unifies generation and editing in one endpoint); an iterative editing workflow isn't.
- Batch pipelines (n prompts per job)—one prompt per invocation (`-n` requests multiple images of the **same** prompt).
- A local/self-hosted provider (`stable-diffusion.cpp`)—a planned follow-up, out of scope for this iteration.
- Guaranteeing any provider stays free—quotas are the providers' to change.
- Midjourney as a provider—it has no scriptable text-to-image API reachable from the terminal, so it's deliberately absent from the fixed `--provider` registry. `spec/design/graphic-prompt-authoring/` may author a Midjourney-targeted prompt document, but this tool never generates against Midjourney; the two specs meet only at the prompt artifact, not at a shared backend.

## Requirements

### Provider-agnostic (shared layer)
- **MUST** select the provider via `--provider` from a fixed registry; the default **MUST** be `cloudflare`.
- **MUST** read every provider credential only from environment variables; **MUST NOT** accept a key via CLI flag or config file, and **MUST NOT** log, echo, or write any credential (including in errors and sidecars).
- **MUST** require an explicit target path (`--out`); no silent default to the working directory. **MUST** refuse to overwrite an existing target without explicit confirmation (`--force`).
- **MUST** write a `<image>.meta.json` sidecar next to every image, containing at least `provider`, `model`, `source`, `prompt`, `timestamp` (RFC 3339 UTC), and `mime_type`. `model` **MUST** carry the concrete model ID the call actually used (for `cloudflare`, the full `@cf/…` ID), never a provider-level alias.
- **MUST**, when the invocation supplied reference images, add a `reference_images` list to the sidecar holding each image's basename and SHA-256 digest, so the conditioning inputs are auditable; the sidecar **MUST NOT** carry the image bytes or an absolute path.
- **MUST** treat HTTP 429 as terminal for the invocation (no automatic retry) and **MUST** distinguish a `limit: 0` / billing-required condition (retrying never helps) from a temporary rate-limit, with an actionable message either way.
- **MUST** surface the provider's actual error-response body (not only the status code) in the operator-facing message.
- **MUST** treat HTTP 401/403 as a terminal auth error pointing at the provider's credential page; any other failure (network, DNS, filesystem, malformed response) **MUST** produce a readable message and a non-zero exit, never a raw stack trace as the only output.
- **SHOULD** derive the format from the target extension and warn (not fail) on a MIME mismatch; the image is still written, because the quota was already spent.
- **MUST** offer a one-time, digest-versioned acknowledgement mechanism, keyed **per provider** under `$XDG_STATE_HOME/nolte-shared/image-generate/<provider>/ack`, for providers that declare a notice.
- **MUST** invoke the bundled script through `${CLAUDE_PLUGIN_ROOT}` rather than a repo-relative path, so the skill works from any consumer repository that installs the plugin (the script lives in the installed plugin directory, not the consumer's working tree); only data paths (`--out`, `--from-prompt-doc`) stay relative to the consumer's working directory.

### `cloudflare` (default)
- **MUST** call Cloudflare Workers AI using `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID`; absence of either yields a setup hint naming both and the free-tier neuron budget. No data/licence notice is required.
- **MUST** offer exactly two models, selected via `--model`: `flux-1-schnell` → `@cf/black-forest-labs/flux-1-schnell` (the default) and `flux-2-klein-4b` → `@cf/black-forest-labs/flux-2-klein-4b`. Both carry Apache-2.0 model weights (see §Sources); an unknown `--model` value is a usage error.
- **MUST NOT** offer `flux-2-klein-9b` or `flux-2-dev`: both carry the FLUX Non-Commercial License. The licence split runs *inside* the Klein family, so the Apache-2.0 property is a property of a model ID, never of the `cloudflare` provider, and every document that claims it **MUST** name the model it applies to.
- **MUST** keep `flux-1-schnell` as the default until a live call has confirmed Klein 4B's response shape (see §Open Questions) and the operator accepts its higher neuron cost: on the pricing in force, a 1024×1024 image costs ≈ 58 neurons on schnell (4 tiles × 4.80 + 4 steps × 9.60) and ≈ 104 neurons on Klein 4B (4 output tiles × 26.05), so the free 10,000-neuron day yields roughly 170 versus 95 images.
- **MUST**, on the `flux-1-schnell` path, post the JSON body (`prompt`, `steps`, optional `seed`) and decode the base64 `result.image`; this endpoint exposes no `width`/`height`, so the tool **MUST** warn on stderr when the operator passes a non-default size and **MUST NOT** silently pretend it was honoured.
- **MUST**, on the `flux-2-klein-4b` path, send `multipart/form-data` (the only input shape the schema accepts) carrying `prompt`, `width`, `height` (each 256–1920 per the changelog; the endpoint's defaults are 1024×768), and an optional `seed`; **MUST NOT** send `steps`, which the endpoint fixes at 4. The encoder stays stdlib-only (`urllib`, no `requests`).
- **MUST** accept both documented response shapes on the Klein 4B path, branching on the response `Content-Type`: a JSON envelope with base64 `result.image` (the output the raw schema declares) and raw `image/*` bytes (the description in the changelog); the MIME type for the base64 form is sniffed from the magic bytes.
- **MAY** accept up to four reference images on the Klein 4B path via a repeatable `--ref-image <path>` flag, sent as the multipart file parts `input_image_0` … `input_image_3` (each < 512×512 per the changelog). The flag **MUST** be rejected as a usage error, before any network call, on `flux-1-schnell` and on every other provider; an unreadable path is a runtime error before any network call. The tool **MUST NOT** enforce the dimension limit client-side; the endpoint's error body is surfaced verbatim per the shared layer. Reference images are uploaded to Cloudflare, and the skill's documentation **MUST** say so.
- **SHOULD** follow the model-level FLUX invariants in `spec/design/flux-image-generation/` for this provider: natural-language prompts (no SDXL comma-tags or prompt weights), `guidance = 0`, `steps ≤ 8`, and no negative prompts (unwanted attributes phrased positively).

### `pollinations`
- **MUST** force `private=true` on every request (opt out of the public feed) and **MUST NOT** expose a CLI flag to disable it.
- **MUST** present a one-time disclaimer, requiring acknowledgement before first use, covering: the public-feed default; that `private=true` is a feed opt-out only and **not** a non-storage guarantee (response caches persist, per the provider's privacy policy); and that the Terms grant **no explicit output licence** (deferring to the underlying model's licence).
- **MUST NOT** be the default provider.
- **MUST** send a browser-style `User-Agent`; the default `urllib` UA is rejected by Pollinations' Cloudflare bot protection (HTTP 403, error 1010).

### `gemini`
- **MUST** pin the stable model ID `gemini-3.1-flash-image` and the `v1` generativelanguage endpoint, never the `-preview` ID Google's deprecation table names as the successor; paid `imagen-*` models and Vertex AI endpoints (`*-aiplatform.googleapis.com`) **MUST** be unreachable.
- **MUST** make the billing requirement explicit (no Gemini image model carries a free tier) in both the setup hint and the one-time notice, and **MUST** name the always-present SynthID watermark there too.
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
- [ ] `--provider cloudflare --model flux-2-klein-4b --width 1280 --height 720` sends a `multipart/form-data` body carrying `prompt`, `width=1280`, `height=720` and no `steps`; the sidecar's `model` is `@cf/black-forest-labs/flux-2-klein-4b`; both a base64-JSON and a raw-bytes response produce an image file.
- [ ] With `--model` omitted the `cloudflare` call is byte-identical to the pre-#638 schnell JSON body; a non-default `--width`/`--height` on schnell prints a stderr warning and leaves the body unchanged.
- [ ] Two `--ref-image` files on Klein 4B become the multipart parts `input_image_0` and `input_image_1` carrying the file bytes, and the sidecar's `reference_images` lists both with their SHA-256; `--ref-image` on schnell or on `pollinations` exits with the usage code without a network call; a fifth `--ref-image` is a usage error.
- [ ] `grep -rn -i "apache" plugins/ docs/ spec/tools spec/design` finds no line that attributes Apache-2.0 to the `cloudflare` provider as a whole; every hit names `flux-1-schnell` or `flux-2-klein-4b`.

## Open Questions

- A local/self-hosted provider (`stable-diffusion.cpp`: zero running cost, full privacy, no rate limits) is the planned next backend; deferred here because of its build/model-download/GPU setup surface.
- **Klein 4B response shape is unestablished live.** Cloudflare's raw model schema declares the output as a base64 `image` string, while its launch changelog describes raw image bytes; no live call was made when this requirement was written (no Cloudflare credentials were available in that session). The tool accepts both shapes; the settling observation is one authenticated `curl` against the endpoint, which also decides whether Klein 4B may become the default.
- **Cloudflare's handling of uploaded reference images** (retention, training exclusion) wasn't re-read for #638; the requirement therefore adds no consent notice and instead obliges the documentation to state plainly that reference images are uploaded. Revisit if Cloudflare's "Your Data and Workers AI" page changes or a consumer needs the guarantee spelled out.
- Pollinations' output licence and prompt-retention remain externally undocumented (upstream issue #8741 unresolved). The safeguard (forced `private=true` + disclaimer) is the mitigation; revisit if Pollinations publishes formal terms.
- Whether `candidateCount` and `seed` reach the image path is unverified: the `v1` `generateContent` image examples show neither field, while the provider still sends both, carried over from the `v1beta` call against the retired model. Settling it needs a billed call, so `-n` and `--seed` on the `gemini` provider are unproven rather than known-good. A plain call sends `contents` alone, as the documented minimal `v1` call does, so it carries no field the endpoint could reject. Google also now leads its image documentation with the Interactions API and calls `generateContent` legacy while still documenting it for image models; moving surfaces is deferred, because this migration was driven by a shutdown date.

## Sources

The Gemini billing assertions in §Context and §`gemini` are author-time external assertions triangulated per `spec/claude/research-triangulate/` §Author-time assertions (author-time tier: at least three independent sources, ordered Primary-first). They earn the stricter treatment because an earlier revision of this capability was built on the inverse premise. Retrieval date: 2026-07-24 for the two GitHub issue sources; 2026-09-12 for every Google page, re-checked during the migration to `gemini-3.1-flash-image`, and for the two independent trackers added with it.

- **No Gemini image-generation model on the Gemini Developer API carries a free tier; `gemini-3.1-flash-image` calls without billing fail against a zero-valued free-tier quota metric**: Google, "Gemini Developer API pricing," whose free-tier row reads "Not available" for every image model (Primary), <https://ai.google.dev/gemini-api/docs/pricing>; Home Assistant core issue #157289 (Secondary), <https://github.com/home-assistant/core/issues/157289>; `googleapis/js-genai` issue #1322 (Secondary), <https://github.com/googleapis/js-genai/issues/1322>.
- **The previous pin is retired: `gemini-2.5-flash-image` shuts down on 2026-10-02, and the provider now pins the stable `gemini-3.1-flash-image`**: Google, "Gemini API model deprecations," which names `gemini-3.1-flash-image-preview` as the replacement (Primary), <https://ai.google.dev/gemini-api/docs/deprecations>; Google, "Gemini API models," which publishes `gemini-3.1-flash-image` as stable (Primary), <https://ai.google.dev/gemini-api/docs/models>; an independent retirement tracker recording the same date (Secondary), <https://vorplabs.com/models/google-model-retirements>; an independent migration write-up flagging that the named replacement is a preview ID (Secondary), <https://www.aifreeapi.com/en/posts/gemini-2-5-flash-image-replacement>.

The `cloudflare` model assertions in §`cloudflare` (model IDs, licences, request shape, parameters, pricing) were read directly from the primary pages on 2026-09-19 for #638, after the issue's own analysis had to rely on search summaries:

- **`@cf/black-forest-labs/flux-2-klein-4b` exists on Workers AI, takes `multipart/form-data` only, and declares a base64 `image` output**: Cloudflare model page and raw schema (`required: ["multipart"]`; output `image: "Generated image as Base64 string."`) (Primary), <https://developers.cloudflare.com/workers-ai/models/flux-2-klein-4b/>.
- **Parameters `prompt`, `width`/`height` 256–1920, `seed`, `guidance`, `input_image_0`–`input_image_3` (< 512×512), `steps` fixed at 4; the launch post describes raw image bytes as the response**: Cloudflare changelog 2026-01-15 (Primary), <https://developers.cloudflare.com/changelog/post/2026-01-15-flux-2-klein-4b-workers-ai/>.
- **FLUX.2 Klein 4B weights are Apache-2.0 ("Open weights available for commercial use under the Apache 2.0 license")**: Hugging Face model card (Primary), <https://huggingface.co/black-forest-labs/FLUX.2-Klein-4B>.
- **Free allocation of 10,000 neurons/day with no model-level exclusion; Klein 4B at 5.37 neurons per input tile and 26.05 per output tile, schnell at 4.80 per tile plus 9.60 per step; Klein 9B and dev priced separately**: Cloudflare Workers AI pricing (Primary), <https://developers.cloudflare.com/workers-ai/platform/pricing/>.
- **`flux-1-schnell` carries no deprecation notice and still accepts `prompt` (1–2048), `steps` (≤ 8, default 4), `seed`, returning base64 JSON**: Cloudflare model page (Primary), <https://developers.cloudflare.com/workers-ai/models/flux-1-schnell/>.
- **Klein 9B and FLUX.2 [dev] carry the FLUX Non-Commercial License**: carried forward from the issue's sources (`black-forest-labs/flux2` issue #32 and `LICENSE-FLUX-DEV`), not re-read on 2026-09-19; the requirement rests on it only negatively (neither model is offered).

Verified 2026-07-24 and re-checked 2026-09-12 on the migration, with two qualifications the requirements above deliberately keep out of the operator-facing message. First, Google no longer publishes a numeric per-model free-tier request table, so the durable evidence is the pricing page's "Not available" row rather than a quota figure. Second, a `limit: 0` body isn't proof that a project lacks billing: in February 2026 paid Tier-1 projects were reported hitting the same zero-valued free-tier quota metric on image models (<https://discuss.ai.google.dev/t/bug-paid-tier-1-account-getting-free-tier-requests-limit-0-on-image-generation-models-gemini-2-5-flash-image-gemini-3-pro-image-preview/123906>), so the §"Provider-agnostic (shared layer)" requirement to surface the upstream `error.message` verbatim is what keeps that case diagnosable.
