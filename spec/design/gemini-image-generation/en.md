# Gemini Image Generation

Status: draft

## Context

Google's native Gemini image model, `gemini-3.1-flash-image` ("Nano Banana 2"), is the portfolio's path when an asset needs Gemini-specific strengths: legible in-image text, conversational multi-turn editing, and multi-image composition. It's reached through the `image-generation` tool's `gemini` provider. Gemini is natively multimodal and built on deep language comprehension, so—like FLUX, unlike SDXL—it rewards narrative, descriptive prose over comma-separated tag lists. It goes further: it also rewards a stated intent or purpose and understands multi-step instructions inside a single prompt. Treating a Gemini prompt like a FLUX or SDXL tag list leaves quality on the table.

A prompt isn't model-portable: the same string yields materially different results across FLUX, Gemini, and Imagen, so prompts must be optimised for the target model. This spec is the Gemini half of that contract; `spec/design/flux-image-generation/` is the FLUX half.

This spec is the **model-level generation baseline** for Gemini: the verified prompting practices and the hard invariants that bind every Gemini image call. It's consumed by `spec/design/graphic-prompt-authoring/` (which assembles brand-conformant prompts and must target the chosen generator correctly) and by `spec/tools/image-generation/` (whose `gemini` provider calls `gemini-3.1-flash-image`). It doesn't own the brand color contract (`corporate-design-colors`), the tool mechanics (`image-generation`), or the prompt-document format (`graphic-prompt-authoring`); it supplies the model facts those specs build on.

Readers: prompt authors and skill/agent authors targeting Gemini; operators tuning generation; reviewers verifying that Gemini calls use Gemini's strengths rather than ported FLUX or SDXL habits.

## Goals

- One verified baseline for prompting optimally with the native Gemini image model, distinct from the FLUX baseline.
- The model's strengths (in-image text, conversational editing, multi-image composition) and its hard caveats (no negative-prompt parameter, always-on SynthID watermark, billing) written down once, where both the prompt-authoring spec and the tool can cite them.
- A clear boundary between the governed model (`gemini-3.1-flash-image`), its Pro and Lite siblings (`gemini-3-pro-image`, `gemini-3.1-flash-lite-image`), and Imagen, so tier-specific limits aren't misapplied.

## Non-Goals

- The brand color system, descriptive-color vocabulary, and style-reference contract—owned by `spec/design/corporate-design-colors/`.
- Tool mechanics (CLI, provider selection, sidecar, credentials)—owned by `spec/tools/image-generation/`.
- Prompt-document format and brand sourcing—owned by `spec/design/graphic-prompt-authoring/`.
- Non-Gemini models (FLUX, SDXL)—owned by `spec/design/flux-image-generation/` and any sibling.
- Imagen (`imagen-*`): a different model family with different limits (480-token prompt, text kept to roughly 25 characters); the tool spec pins it out of reach, and it's referenced here only as a boundary so its limits aren't applied to the native Gemini model.
- The sibling tiers `gemini-3-pro-image` ("Nano Banana Pro": a reasoning core, studio-grade 4K layout and typography) and `gemini-3.1-flash-lite-image` ("Nano Banana 2 Lite": ultra-low latency at lower cost) as generation targets; they're named only as boundaries so their limits and prices aren't applied to the governed model.

## Requirements

### Model selection
- **MUST** treat `gemini-3.1-flash-image` ("Nano Banana 2") as the model this baseline governs; the `image-generation` tool pins exactly this ID.
- **MUST** pin the stable ID, never `gemini-3.1-flash-image-preview`. Google's deprecation table names the preview ID as the successor of `gemini-2.5-flash-image` ([E8]), while the model catalogue publishes `gemini-3.1-flash-image` as stable ([E9]); a preview ID carries no stability contract and isn't something a tool pins to.
- **MUST** record that Gemini produced an asset; the tool's sidecar `model` field satisfies this.
- **MUST NOT** apply this baseline's limits to Imagen (`imagen-*`), to `gemini-3-pro-image`, or to `gemini-3.1-flash-lite-image`; the tiers differ in output ceiling, reasoning behaviour, and price, and version drift in third-party guides is common (see Anti-patterns).
- **MUST** treat `gemini-2.5-flash-image` as retired for new work: it shuts down 2026-10-02 ([E8], [E11], [E12]). Prompting advice written for it carries over only where this baseline restates it against the successor's own documentation.

### Prompting (describe the scene)
- **MUST** write prompts as narrative, descriptive sentences—"describe the scene, don't list keywords"; Gemini's language comprehension rewards prose over comma-separated tag lists, the same as FLUX.
- **SHOULD** state the asset's intent or purpose, not only its contents (`a logo for a high-end, minimalist skincare brand` beats a bare subject); stated intent is a Gemini lever that FLUX lacks.
- **SHOULD** follow the order subject, then action, location or context, composition, and style, front-loading the subject.
- **SHOULD** open the prompt with a strong verb naming the primary operation (`Create`, `Transform`, `Remove`) so the model knows the task.
- **SHOULD** be hyper-specific about material and texture (`navy blue tweed` over `suit jacket`; `ornate elven plate armor etched with silver leaf` over `armor`); granular description is the largest single quality lever.
- **SHOULD** control composition with photographic and cinematic language (`wide-angle`, `macro`, `low-angle`, `85mm portrait lens`, `f/1.8 shallow depth of field`, `Dutch angle`) and direct lighting and color grading explicitly (`three-point softbox`, `chiaroscuro`, `golden-hour backlighting`; `as if on 1980s color film, slightly grainy`; `muted teal color grading`).

### Use-case templates
- **SHOULD** use the per-use-case prompt shapes as starting points:
  - Photorealistic: `A photorealistic [shot type] of [subject], [action], set in [environment], illuminated by [lighting] creating a [mood] atmosphere, captured with [camera/lens] emphasizing [textures].`
  - Sticker or illustration: `A [style] sticker of [subject], featuring [characteristics] and a [palette], with [line style] and [shading]. White background.`
  - Text or logo: `Create a [image type] for [brand] with text '[exact text]' in a [font style], [style], [color scheme].`
  - Product: `A studio-lit product photograph of [product] on [background], lighting [setup] to [purpose], camera angle [angle] showcasing [feature], sharp focus on [detail].`
  - Minimalist or negative-space: `A minimalist composition of a single [subject] in the [location], on a vast empty [color] canvas with significant negative space, [lighting].`
  - Comic panel: `A single comic panel in [art style]. Foreground: [character/action]. Background: [setting]. Caption box with text '[text]'. Lighting creates [mood].`

### Text rendering (a Gemini strength)
- **MUST** enclose the literal target words in quotes (`"URBAN EXPLORER"`); quoting is what makes Gemini render the exact string. This is the same quoting rule as FLUX, but Gemini renders longer, more complex text reliably.
- **SHOULD** name the font or typographic style (`bold white sans-serif`, `Century Gothic`), and **MAY** specify per-line styling for multi-line layouts.
- **MAY** render text in another language by writing the prompt in one language and naming the target language for the rendered words.
- **MAY** use the text-first approach—have the model produce the text content conversationally first, then ask for an image that renders it—for tricky copy.
- **MUST NOT** assume Imagen's roughly-25-character text limit applies; the native Gemini model renders longer strings, though very complex typography can still need iteration. Where a layout genuinely needs studio-grade typography, that's the case for `gemini-3-pro-image`, not for stretching this model.

### Editing and multi-image
- **SHOULD** iterate by conversational, multi-turn editing—the recommended path—changing one thing per turn (`keep everything the same, but make the lighting warmer`) rather than regenerating from scratch.
- **SHOULD** edit a region by semantic masking: name only the element to change and instruct the model to keep the rest identical, preserving stated aspects (`change only the [element] to [new]; keep everything else identical, preserving the lighting and composition`).
- **MAY** compose from up to 14 reference images: up to 10 for object fidelity plus up to 4 for character consistency ([E2]). Name which element comes from which input.
- **MAY** request an output size and aspect ratio explicitly through the tool's provider rather than in prose. The model accepts `1K`, `2K` and `4K` (uppercase `K` is required; a lowercase `1k` is rejected) and the ratios `1:1`, `3:2`, `2:3`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9` ([E2]). Whether the tool exposes them is a tool-mechanics question owned by `spec/tools/image-generation/`.
- **MUST** account for aspect-ratio inheritance: an edit inherits the input image's aspect ratio, and with multiple inputs it adopts the last input's ratio; for a new generation, state the desired aspect ratio (or `do not change the input aspect ratio`) explicitly.

### Negative prompts
- **MUST NOT** use `no X` negative phrasing or assume a negative-prompt parameter; Gemini exposes none. Express unwanted attributes by describing the desired state positively (`an empty, deserted street with no signs of traffic` over `no cars`)—the same semantic-positive rule as FLUX.

### Output and licensing (hard invariants)
- **MUST** treat the SynthID watermark as always present: every Gemini-generated image carries it. For branding, commercial, or blog assets this is a material difference from the FLUX-on-Cloudflare path (no watermark) and **MUST** be weighed when choosing the provider.
- **MUST** treat Gemini as billing-required: no image-generation model on the Gemini Developer API carries a free tier, and a call without billing fails against a zero-valued free-tier quota metric ([E5], [E6], [E7]). That's a provider property, not a prompt concern, but it bears on provider choice (owned by `spec/tools/image-generation/`).

### Anti-patterns
- **MUST NOT** port a FLUX or SDXL comma-tag prompt verbatim to Gemini; rewrite it as narrative prose with stated intent.
- **MUST NOT** use `no X` negatives, prompt weights (`(word:1.3)`, `++`), or emphasis brackets.
- **MUST NOT** apply Imagen's 480-token or roughly-25-character text limits to the native Gemini model, nor carry `gemini-3-pro-image`'s reasoning-core and studio-typography behaviour over to this tier, nor assume `gemini-3.1-flash-lite-image`'s price applies here.
- **MUST NOT** copy prompting advice written for `gemini-2.5-flash-image` without checking it against this baseline; the model IDs differ, and third-party guides published before the 2026-10-02 shutdown target the retired one.
- **MUST NOT** ship a Gemini image as a watermark-free commercial asset; SynthID is always embedded.

## Acceptance Criteria

- [ ] A Gemini prompt under review reads as narrative sentences, not a comma-tag list, and states the asset's intent.
- [ ] In-image text is enclosed in quotes and its font or style is named.
- [ ] Unwanted attributes are phrased positively; no negative-prompt parameter or `no X` tag is used.
- [ ] Editing prompts use conversational or semantic-masking phrasing (`change only X, keep the rest identical`) and account for aspect-ratio inheritance.
- [ ] The prompt targets `gemini-3.1-flash-image` (the stable ID, not the `-preview` one) and applies neither Imagen's nor the Pro and Lite tiers' limits.
- [ ] The generating tool's sidecar records that Gemini produced the asset.
- [ ] Provider choice for a commercial or blog asset accounts for the always-present SynthID watermark.

## References

The billing, watermark, and model-currency assertions in §"Output and licensing (hard invariants)" are author-time external assertions triangulated per `spec/claude/research-triangulate/` §Author-time assertions (author-time tier: at least three independent sources, ordered Primary-first). Retrieval date: 2026-07-24 for [E1], [E3], [E4], [E6] and [E7]; 2026-09-12 for [E2], [E5] and [E8]-[E13], which were retrieved or re-checked during the migration to `gemini-3.1-flash-image`.

- [R1] Prompt-document authoring that targets the chosen generator: `spec/design/graphic-prompt-authoring/`
- [R2] The tool whose `gemini` provider calls `gemini-3.1-flash-image`: `spec/tools/image-generation/`
- [R3] The sibling model baseline for the default FLUX path: `spec/design/flux-image-generation/`
- [R4] Brand color contract the prompts must satisfy: `spec/design/corporate-design-colors/`
- [E1] How to prompt Gemini Flash Image for the best results (use-case templates, best practices; written for the 2.5 generation, retained for the prompting shapes this baseline restates rather than for its model facts): <https://developers.googleblog.com/en/how-to-prompt-gemini-2-5-flash-image-generation-for-the-best-results/>
- [E2] Nano Banana image generation, official API docs (examples, aspect ratios, SynthID watermark): <https://ai.google.dev/gemini-api/docs/image-generation>
- [E3] Ultimate prompting guide for Nano Banana (frameworks, text-rendering rules, camera and lighting): <https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana>
- [E4] Imagen prompt guide, the boundary case whose 480-token and roughly-25-character text limits the native Gemini model doesn't inherit: <https://ai.google.dev/gemini-api/docs/imagen>
- [E5] Gemini Developer API pricing, whose free-tier row reads "Not available" for every image model, `gemini-3.1-flash-image` included, and which prices its image output at 60 USD per million tokens against the Lite tier's 30 and the Pro tier's 120 (Primary): <https://ai.google.dev/gemini-api/docs/pricing>
- [E6] Home Assistant core issue #157289, an independent consumer reporting `generate_content_free_tier_requests, limit: 0` on Gemini image generation (Secondary): <https://github.com/home-assistant/core/issues/157289>
- [E7] `googleapis/js-genai` issue #1322, the same zero-valued free-tier quota metric raised through Google's own JavaScript SDK (Secondary): <https://github.com/googleapis/js-genai/issues/1322>
- [E8] Gemini API model deprecations, giving `gemini-2.5-flash-image` a shutdown date of 2026-10-02 and naming `gemini-3.1-flash-image-preview` as its replacement (Primary): <https://ai.google.dev/gemini-api/docs/deprecations>
- [E9] Gemini API model catalogue, publishing `gemini-3.1-flash-image` ("Nano Banana 2"), `gemini-3.1-flash-lite-image` and `gemini-3-pro-image` as stable (Primary): <https://ai.google.dev/gemini-api/docs/models>
- [E10] The legacy `generateContent` image-generation surface, whose examples call `https://generativelanguage.googleapis.com/v1/models/gemini-3.1-flash-image:generateContent`, send `contents` alone in the minimal call, and pass `responseFormat.image.aspectRatio` and `imageSize` inside `generationConfig` (Primary): <https://ai.google.dev/gemini-api/docs/generate-content/image-generation>
- [E11] An independent retirement tracker recording the 2026-10-02 shutdown and the migration target (Secondary): <https://vorplabs.com/models/google-model-retirements>
- [E12] An independent migration write-up recording the same shutdown date and flagging that the deprecation table's named replacement is a preview ID (Secondary): <https://www.aifreeapi.com/en/posts/gemini-2-5-flash-image-replacement>
- [E13] An independent write-up recording `gemini-3.1-flash-image` as Google's recommended replacement for the retired Imagen 4 endpoints and as its current general-purpose image model (Secondary): <https://aicybr.com/blog/imagen-4-api-shutdown-migrate-gemini-image>

Verified 2026-09-12 on the migration to `gemini-3.1-flash-image`: the billing invariant holds—Google publishes no free-tier allowance for any Gemini image model, and the zero-valued quota metric reproduces across independent consumers ([E5]–[E7]). The always-on SynthID watermark likewise remains documented on the primary image-generation page for the successor ([E2], "All generated images include a SynthID watermark"), with no opt-out documented anywhere. The model identity itself is triangulated across four independent domain roots: Google's own catalogue and deprecation table ([E8], [E9]) plus three unaffiliated trackers ([E11]-[E13]). Two qualifications: Google no longer publishes a numeric per-model free-tier request table, so the pricing page's "Not available" row is the durable evidence rather than a quota figure; and a `limit: 0` response body doesn't by itself prove a project lacks billing, since paid projects were reported hitting the same metric on image models in February 2026.

## Open Questions

- **Exact prompt-token limit.** Google publishes no hard token cap for `gemini-3.1-flash-image` comparable to FLUX's 256 or Imagen's 480. Treat the practical limit as generous but not primary-documented until a figure is published.
- **Whether `candidateCount` and `seed` reach the image path.** The `generateContent` image examples don't show either field ([E10]), while the tool still sends both, carried over from the `v1beta` 2.5 call. Whether the `v1` surface accepts, ignores, or rejects them is unverified here because it needs a billed call. It's a tool-mechanics question owned by `spec/tools/image-generation/`; until it's settled, `--n` and `--seed` on the `gemini` provider are unproven rather than known-good. The tool deliberately sends no `responseModalities`: the documented minimal `v1` call sends `contents` alone ([E10]), so a plain call carries no field the endpoint could reject.
- **Interactions instead of `generateContent`.** Google now leads its image-generation documentation with the Interactions API and describes `generateContent` as legacy, while still documenting it for image models ([E10]). This baseline stays on `generateContent` because the migration it accompanies was driven by a shutdown date, and folding an API-surface rewrite into a deadline fix widens the blast radius. Revisit when `generateContent` gets a deprecation date of its own.

<!-- Resolved by the 2026-09-12 migration: the successor-model question (settled on the stable
`gemini-3.1-flash-image`), the reference-image count (14 = 10 objects + 4 characters, [E2]), and
the output-resolution question (1K/2K/4K with an uppercase K, [E2]). -->
