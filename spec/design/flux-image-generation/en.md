# FLUX Image Generation

Status: draft

## Context

FLUX (Black Forest Labs) is the image model behind the portfolio's default generation path: **FLUX.1-schnell via Cloudflare Workers AI** (Apache-2.0, free tier), with FLUX.1-dev and the API-only pro/ultra tiers as alternatives. FLUX has model-specific behaviours that generic prompt advice gets wrong. It's built on a **T5-XXL** text encoder, so it rewards natural-language descriptions, not SDXL-style comma-separated tags; and the **schnell** variant is guidance- and step-distilled, so it runs without classifier-free guidance and has no working negative prompts. Treating FLUX like SDXL produces washed-out, off-target images.

This spec is the **model-level generation baseline**: the verified FLUX prompting practices and the hard parameter invariants that bind every FLUX call. It's consumed by `spec/design/graphic-prompt-authoring/` (which assembles brand-conformant prompts and must target FLUX correctly) and by `spec/tools/image-generation/` (whose `cloudflare` provider runs FLUX.1-schnell). It **doesn't** own the brand color contract (`corporate-design-colors`), the tool mechanics (`image-generation`), or the prompt-document format (`graphic-prompt-authoring`); it supplies the model facts those specs build on.

Readers: prompt authors and skill/agent authors targeting FLUX; operators tuning generation; reviewers verifying that FLUX calls don't carry SDXL habits.

## Goals

- One verified baseline for generating optimally with FLUX, so prompts and parameters don't drift into SDXL habits.
- The hard model invariants (guidance, steps, token limits, negative-prompt absence) written down once, where both the prompt-authoring spec and the tool can cite them.
- The default path (FLUX.1-schnell via Cloudflare) fully specified, including the constraints the Cloudflare schema imposes.

## Non-Goals

- The brand color system, descriptive-color vocabulary, and style-reference contract—owned by `spec/design/corporate-design-colors/`.
- Tool mechanics (CLI, provider selection, sidecar, credentials)—owned by `spec/tools/image-generation/`.
- Prompt-document format and brand sourcing—owned by `spec/design/graphic-prompt-authoring/`.
- Non-FLUX models (SDXL, Gemini image, Imagen)—a sibling model spec would own those.
- Image editing, in-painting, ControlNet, or LoRA fine-tuning.

## Requirements

### Model selection
- **MUST** treat **FLUX.1-schnell** as the default model: Apache-2.0 (commercial use of both the model and its outputs permitted), few-step distilled, billed in Neurons on Cloudflare Workers AI and therefore drawn from its free daily Neuron allocation.
- **MUST** treat **FLUX.1-dev** as licence-restricted at the *model* level rather than at the output level: the FLUX [dev] Non-Commercial License requires a separate Black Forest Labs licence for commercial use of the model itself and obliges the operator to run content filtering, while the generated outputs may be used for any purpose including commercial ones (the one output restriction is training a competing model). Because the commercial-use question therefore attaches to the generating run and not to the asset, FLUX.1-dev **MUST NOT** be the default for blog or commercial assets; use it only for non-commercial or evaluation work.
- **MUST** record which FLUX variant produced an asset; the `image-generation` tool's sidecar `model` field satisfies this.

### Prompting (natural language)
- **MUST** write prompts as natural-language descriptive sentences, not comma-separated SDXL-style tag lists; FLUX's T5-XXL encoder rewards descriptive phrasing (`a sign with green text` over `sign, green`).
- **SHOULD** follow Black Forest Labs' prompt order—subject, then location/setting, style/medium, camera, lighting, colors, effect, additional elements—leading with the subject (front-loading the most important content).
- **MUST** render any in-image text by quoting the literal string (for example `"OPEN"`) and keep such strings short; T5-XXL makes FLUX strong at legible text, but only when the literal is quoted.
- **MUST NOT** use prompt weights (`(word:1.3)`, `++`, emphasis brackets); FLUX ignores them, so express emphasis in words (`with emphasis on the foreground`).
- **SHOULD** describe a style rather than stack artist names; a described style (`epic fantasy concept art, warm lighting, dramatic composition`) is more reliable than `by <artist>`.
- **SHOULD** prefer English prompts for the most precise results.

### Token and length limits
- **MUST** keep FLUX.1-schnell prompts within **256 tokens** (the model's hard cap); text beyond is truncated. FLUX.1-dev allows roughly 512 tokens.
- Cloudflare additionally caps the prompt **string** at 2048 characters; the 256-token model cap is the tighter, binding limit for schnell, so dense, front-loaded prompts beat long ones.

### Negative prompts
- **MUST NOT** rely on negative prompts with FLUX.1-schnell: it runs without classifier-free guidance (guidance ≈ 0), so a negative prompt has no effect, and the Cloudflare schema exposes no `negative_prompt` parameter.
- **MUST** express unwanted attributes positively instead: `a clean, uncluttered background` rather than `no clutter`; `a clear blue sky` rather than `no clouds`.

### Parameters (hard invariants)
- **MUST** set `guidance_scale = 0.0` for FLUX.1-schnell. This is mandatory for the distilled model; the commonly-cited `3.5` applies to FLUX.1-dev and is **wrong** for schnell. FLUX.1-dev uses guidance ≈ 3.5.
- **MUST** keep `steps` within the distilled range: schnell **1–4** (Cloudflare hard cap **8**; more steps add latency and cost without quality), dev 28–50.
- **SHOULD** pass an explicit `seed` when reproducibility matters; an identical seed plus identical parameters and prompt reproduces the image.
- **SHOULD** target 1024×1024 (~1 MP) or a familiar aspect ratio (1:1, 16:9, 9:16, 3:2), with pixel dimensions divisible by 16.

### Cloudflare Workers AI path (default)
- The `@cf/black-forest-labs/flux-1-schnell` endpoint accepts only `prompt` (≤ 2048 characters), `steps` (≤ 8), and `seed`; it exposes **no** `width`, `height`, `negative_prompt`, or `guidance`. Output is base64-encoded JPEG.
- **MUST NOT** assume resolution control on this path: `width`/`height` aren't parameters, so the output size is fixed by the endpoint (≈ 1024×1024; see Open Questions). Aspect-ratio or resolution control requires a provider that exposes those parameters (dev/pro endpoints), not the Cloudflare schnell path.

### Anti-patterns
- **MUST NOT** use SDXL-style comma-tag spam, prompt weights, or negative prompts on schnell.
- **MUST NOT** stack artist names in place of description, combine contradictory terms (`wide-angle extreme close-up`, `bright dark`), or raise `steps` above the cap expecting more quality.

## Acceptance Criteria

- [ ] A FLUX prompt under review reads as natural-language sentences, not a comma-tag list.
- [ ] No prompt weights (`(word:1.3)`, `++`) appear in FLUX prompts.
- [ ] A schnell call sets guidance to `0` and `steps ≤ 8`, and passes no `negative_prompt`.
- [ ] In-image text is quoted in the prompt.
- [ ] Unwanted attributes are phrased positively, not as negative prompts.
- [ ] FLUX.1-dev isn't the default for commercial or published assets; its non-commercial licence is respected.
- [ ] The generating tool's sidecar records the FLUX variant used.
- [ ] A FLUX.1-schnell prompt stays within 256 tokens.

## References

The model-licensing and hosting assertions in §"Model selection" are author-time external assertions triangulated per `spec/claude/research-triangulate/` §Author-time assertions (author-time tier: at least three independent sources, ordered Primary-first). Retrieval date for every external source below: 2026-07-24.

- [R1] Prompt-document authoring that targets FLUX: `spec/design/graphic-prompt-authoring/`
- [R2] The tool whose `cloudflare` provider runs FLUX.1-schnell: `spec/tools/image-generation/`
- [R3] Brand color contract the prompts must satisfy: `spec/design/corporate-design-colors/`
- [E1] Black Forest Labs prompting guide: <https://docs.bfl.ai/guides/prompting_unified_basics>
- [E2] FLUX.1-schnell model card (`guidance_scale=0.0`, `max_sequence_length=256`): <https://huggingface.co/black-forest-labs/FLUX.1-schnell>
- [E3] FLUX.1-dev model card (`guidance_scale=3.5`, `max_sequence_length=512`): <https://huggingface.co/black-forest-labs/FLUX.1-dev>
- [E4] Cloudflare `@cf/black-forest-labs/flux-1-schnell` schema (`steps` max 8, `prompt` max 2048, no width/height/negative_prompt): <https://developers.cloudflare.com/workers-ai/models/flux-1-schnell/>
- [E5] FLUX [dev] Non-Commercial License v2.0, the licence text Black Forest Labs currently publishes (last updated 2025-11-25; its scope clause names FLUX.1 [dev]), granting Output use "for any purpose (including for commercial purposes)" (Primary): <https://bfl.ai/legal/non-commercial-license-terms>
- [E6] `LICENSE-FLUX1-dev` v1.1.1, the licence version still shipped in the `flux` inference repository, requiring a company licence "for a commercial activity" around the model (Primary): <https://github.com/black-forest-labs/flux/blob/main/model_licenses/LICENSE-FLUX1-dev>
- [E7] Black Forest Labs' own clarification that the short-lived v1.1 wording dropping the commercial-output grant was reverted in v1.1.1 (Primary, vendor statement in a third-party forum): <https://huggingface.co/black-forest-labs/FLUX.1-Kontext-dev/discussions/6>
- [E8] Cloudflare Workers AI pricing, the 10,000-Neurons-per-day free allocation FLUX.1-schnell's per-tile and per-step rates are billed against (Primary, independent redistributor): <https://developers.cloudflare.com/workers-ai/platform/pricing/>
- [E9] Independent overview of the schnell (Apache-2.0) / dev (source-available, non-commercial) / pro (proprietary) split, including that users keep ownership of the outputs (Tertiary): <https://en.wikipedia.org/wiki/Flux_(text-to-image_model)>

Verified 2026-07-24: FLUX.1-dev's restriction sits on the model, not on the output. An earlier revision of this spec stated that the licence forbids commercial use of *outputs*; the licence text in force contradicts that ([E5], [E6], [E7]), so §"Model selection" is corrected above rather than merely cited. Two licence versions circulate in parallel—v2.0 on Black Forest Labs' legal site and v1.1.1 in the inference repository and on the model card—and they agree on the output grant. Black Forest Labs has since shipped the FLUX.2 family under the same consolidated non-commercial terms; this spec still governs the FLUX.1 models the `image-generation` tool reaches.

## Open Questions

- **Cloudflare fixed output resolution.** The schnell schema omits `width`/`height`, so the endpoint's fixed output size isn't primary-documented (≈ 1024×1024 is assumed, observed at 1024×1024 in practice, but not stated in the schema). Revisit if Cloudflare publishes the output dimensions or adds size parameters.
- **Pixel divisor 16 vs 64.** A divisor of 16 is widely documented for FLUX latents; whether the binding constraint is strictly 16 or a conservative 64 isn't primary-verified. Moot on the Cloudflare path (no size control); relevant only for dev/pro providers.
- **FLUX.1-dev token limit.** The HF dev example uses 512 tokens; the hard T5 cap is higher. 512 is treated here as the recommended ceiling pending a primary statement of the true maximum.
