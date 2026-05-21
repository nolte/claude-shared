# Gemini Image Generation (Free-Tier)

Status: draft

## Context

Image generation should be reachable from the terminal — a prompt in, an image file on disk out — without opening a chat UI. Google's Gemini API offers a Free-Tier image-generation model (`gemini-2.5-flash-image`) that satisfies this need without billing setup or risk of accidental paid usage.

This spec governs how that capability is operationalised inside this repository. A future skill or agent (working title: `gemini-image-generate`) will implement it. The spec exists first so the skill/agent can be validated against it (see `spec/claude/skill-management/` and `spec/claude/agent-management/`).

Two constraints shape every decision here:

1. **Free-Tier only.** No call path may invoke a paid Gemini model (`imagen-*`, Vertex AI). This is enforced in code, not just by convention.
2. **Free-Tier prompts are used for model training.** The operator MUST be informed before their first image is sent.

Additionally, the model ID `gemini-2.5-flash-image` is deliberately version-pinned in this spec; a future Free-Tier successor model will require a spec revision before the implementation may adopt it.

## Goals

- A skill/agent can turn a text prompt into an image file at an operator-chosen path with one invocation.
- Calls are restricted to the Free-Tier-eligible model; paid models are unreachable through this code path.
- Failures (missing key, rate limit, auth) produce actionable messages — never silent crashes, never automatic quota-burning retries.
- Each generated image carries a sidecar with enough metadata to reproduce or audit the call.
- The operator is informed once, explicitly, that Free-Tier inputs feed model training.

## Non-Goals

- Imagen models (`imagen-3.0-*`, `imagen-4.0-*`) — paid only, out of scope for this spec.
- Vertex AI endpoints — paid, requires GCP project setup, out of scope.
- Image editing / in-painting / multi-turn refinement — separate feature space; this spec is text-to-image only.
- Batch pipelines (n images across many prompts in one job) — may be a follow-up spec; the skill/agent here handles one prompt per invocation.
- Self-hosted alternatives (Stable Diffusion, local diffusers) — different operational model.

## Requirements

- **MUST** use `gemini-2.5-flash-image` as the only model ID. The model ID is a hardcoded allowlist constant in the implementation, not a free-form parameter.
- **MUST** call exclusively the Google AI Studio Generative Language endpoint `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent`. Vertex AI endpoints (`*-aiplatform.googleapis.com`) are forbidden.
- **MUST** read the API key from the environment variable `GEMINI_API_KEY`. No CLI flag, no config file, no prompting the operator to paste a key into the conversation.
- **MUST** never log, echo, or write the API key — including in error messages, traces, or sidecar files.
- **MUST** treat HTTP 429 (rate limit / quota exhausted) as a terminal error for the current invocation: surface a clear message to the operator and exit. Automatic retry is forbidden because each retry burns more Free-Tier quota.
- **MUST** treat HTTP 401 / 403 (auth failure) as a terminal error with a message that points at `https://aistudio.google.com/apikey`.
- **MUST** surface an actionable error message and exit with a non-zero code for any failure not covered by the specific HTTP error rules above — including network errors, DNS resolution failures, malformed API responses, filesystem permission errors, and missing parent directories.
- **MUST** require the operator to specify the target file path explicitly. No silent default to the current working directory.
- **MUST** refuse to overwrite an existing target file without explicit operator confirmation in the same invocation.
- **MUST** present a one-time data-protection notice before the first successful generation in a given environment:
  > "Free-Tier prompts and generated images are used by Google to train and improve their models. Do not submit confidential or personal data. To opt out, enable billing on this API key — see https://ai.google.dev/gemini-api/terms."
  The acknowledgement MUST be persisted at `$XDG_STATE_HOME/nolte-shared/gemini-image-generation/ack` (falling back to `$HOME/.local/state/nolte-shared/gemini-image-generation/ack` when `XDG_STATE_HOME` is unset) so the operator is not prompted again on the same machine across sessions.
- **MUST** write a sidecar metadata file next to every generated image, named `<image>.meta.json`, containing at minimum:
  - `prompt` — the verbatim prompt that was submitted
  - `model` — the model ID used (`gemini-2.5-flash-image`)
  - `endpoint` — the full URL called
  - `timestamp` — RFC 3339 UTC timestamp of the response
  - `mime_type` — the MIME type returned by the API
- **SHOULD** derive the image format from the target file extension (`.png`, `.jpg`, `.webp`) and validate it against the MIME type returned by the API; mismatch is a warning, not a failure.
- **SHOULD** emit a friendly setup hint when `GEMINI_API_KEY` is missing, pointing at `https://aistudio.google.com/apikey` and explaining that Free-Tier requires no billing setup.
- **SHOULD** surface the current Free-Tier rate-limit ceiling in the 429 error message so the operator understands what was hit.
- **MAY** accept an optional `n` parameter for multiple images per call when the model supports it; each image gets its own sidecar (the prompt is duplicated across sidecars by design — this is a known consequence of the per-image-sidecar convention).
- **MAY** accept an optional seed parameter when the model supports deterministic generation, and record it in the sidecar.

## Acceptance Criteria

- [ ] Static inspection of the implementation shows `gemini-2.5-flash-image` as the only model ID literal; no `imagen-*` strings appear.
- [ ] Static inspection shows no calls to `*-aiplatform.googleapis.com` or any Vertex AI SDK.
- [ ] The API key is read only from `GEMINI_API_KEY`; grep for the key value in stdout, logs, sidecar JSON, and error traces returns no hits.
- [ ] Invoking with `GEMINI_API_KEY` unset produces a setup hint that names the variable, links to `https://aistudio.google.com/apikey`, and explains that Free-Tier usage requires no billing setup; exit code is non-zero.
- [ ] A simulated HTTP 429 response causes a single error message ("Free-Tier quota exhausted…") and exit; no retry attempts are observed in HTTP traces.
- [ ] The HTTP 429 error message contains a quantitative rate-limit figure (e.g. "10 requests per minute" or "100 requests per day").
- [ ] A simulated HTTP 401 response causes an auth-failure message linking to the key-management page; exit code is non-zero.
- [ ] An induced network / DNS / filesystem failure produces a human-readable error message and a non-zero exit code; no silent crash, no traceback dump as the only operator-visible output.
- [ ] First successful invocation in a clean environment prints the data-protection notice and requires explicit acknowledgement; subsequent invocations — including in a fresh shell session on the same machine — do not re-prompt, and the acknowledgement file exists at the path declared in the MUST.
- [ ] Invocation without a target path is rejected with a usage error.
- [ ] Invocation against an existing file path is rejected unless the operator confirms overwrite in the same call.
- [ ] A scenario where the target file extension and the returned MIME type disagree produces a warning message but still writes the file.
- [ ] Every generated image has a `<image>.meta.json` sidecar containing the five required keys.
- [ ] The sidecar JSON does not contain the API key under any field name.

## Open Questions

- Should the skill/agent expose an optional default target directory (e.g. `$XDG_PICTURES_DIR/gemini/`) when the operator omits the path, or is the explicit-path requirement absolute? The current MUST is the safer default; revisit if it proves friction in practice.
- Does the implementation language bind us to a specific SDK (Python `google-genai`, Node `@google/generative-ai`, plain `curl`)? The endpoint is fixed; the SDK choice is an implementation detail that belongs to the operationalising skill/agent, not this spec.
