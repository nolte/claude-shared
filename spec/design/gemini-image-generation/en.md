# Gemini Image Generation

Status: draft

## Context

Google's native Gemini image model, `gemini-2.5-flash-image` ("Nano Banana"), is the portfolio's path when an asset needs Gemini-specific strengths: legible in-image text, conversational multi-turn editing, and multi-image composition. It's reached through the `image-generation` tool's `gemini` provider. Gemini is natively multimodal and built on deep language comprehension, so—like FLUX, unlike SDXL—it rewards narrative, descriptive prose over comma-separated tag lists. It goes further: it also rewards a stated intent or purpose and understands multi-step instructions inside a single prompt. Treating a Gemini prompt like a FLUX or SDXL tag list leaves quality on the table.

A prompt isn't model-portable: the same string yields materially different results across FLUX, Gemini, and Imagen, so prompts must be optimised for the target model. This spec is the Gemini half of that contract; `spec/design/flux-image-generation/` is the FLUX half.

This spec is the **model-level generation baseline** for Gemini: the verified prompting practices and the hard invariants that bind every Gemini image call. It's consumed by `spec/design/graphic-prompt-authoring/` (which assembles brand-conformant prompts and must target the chosen generator correctly) and by `spec/tools/image-generation/` (whose `gemini` provider calls `gemini-2.5-flash-image`). It doesn't own the brand color contract (`corporate-design-colors`), the tool mechanics (`image-generation`), or the prompt-document format (`graphic-prompt-authoring`); it supplies the model facts those specs build on.

Readers: prompt authors and skill/agent authors targeting Gemini; operators tuning generation; reviewers verifying that Gemini calls use Gemini's strengths rather than ported FLUX or SDXL habits.

## Goals

- One verified baseline for prompting optimally with the native Gemini image model, distinct from the FLUX baseline.
- The model's strengths (in-image text, conversational editing, multi-image composition) and its hard caveats (no negative-prompt parameter, always-on SynthID watermark, billing) written down once, where both the prompt-authoring spec and the tool can cite them.
- A clear boundary between the native Gemini model (`gemini-2.5-flash-image`), the newer Nano-Banana-Pro and Nano-Banana-2 tiers, and Imagen, so version-specific limits aren't misapplied.

## Non-Goals

- The brand color system, descriptive-color vocabulary, and style-reference contract—owned by `spec/design/corporate-design-colors/`.
- Tool mechanics (CLI, provider selection, sidecar, credentials)—owned by `spec/tools/image-generation/`.
- Prompt-document format and brand sourcing—owned by `spec/design/graphic-prompt-authoring/`.
- Non-Gemini models (FLUX, SDXL)—owned by `spec/design/flux-image-generation/` and any sibling.
- Imagen (`imagen-*`): a different model family with different limits (480-token prompt, text kept to roughly 25 characters); the tool spec pins it out of reach, and it's referenced here only as a boundary so its limits aren't applied to the native Gemini model.
- The newer Nano-Banana-Pro and Nano-Banana-2 ("Gemini 3 Pro/Flash Image") tiers as a generation target; their expanded limits (larger context, 4K output, more reference images) are noted only to prevent misapplication.

## Requirements

### Model selection
- **MUST** treat `gemini-2.5-flash-image` ("Nano Banana") as the model this baseline governs; the `image-generation` tool pins exactly this ID.
- **MUST** record that Gemini produced an asset; the tool's sidecar `model` field satisfies this.
- **MUST NOT** apply this baseline's limits to Imagen (`imagen-*`), nor assume the newer Nano-Banana-Pro or Nano-Banana-2 limits apply to `gemini-2.5-flash-image`; version drift in third-party guides is common (see Anti-patterns).

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
- **MUST NOT** assume Imagen's roughly-25-character text limit applies; the native Gemini model renders longer strings, though very complex typography can still need iteration.

### Editing and multi-image
- **SHOULD** iterate by conversational, multi-turn editing—the recommended path—changing one thing per turn (`keep everything the same, but make the lighting warmer`) rather than regenerating from scratch.
- **SHOULD** edit a region by semantic masking: name only the element to change and instruct the model to keep the rest identical, preserving stated aspects (`change only the [element] to [new]; keep everything else identical, preserving the lighting and composition`).
- **MAY** compose from multiple reference images, naming which element comes from which input.
- **MUST** account for aspect-ratio inheritance: an edit inherits the input image's aspect ratio, and with multiple inputs it adopts the last input's ratio; for a new generation, state the desired aspect ratio (or `do not change the input aspect ratio`) explicitly.

### Negative prompts
- **MUST NOT** use `no X` negative phrasing or assume a negative-prompt parameter; Gemini exposes none. Express unwanted attributes by describing the desired state positively (`an empty, deserted street with no signs of traffic` over `no cars`)—the same semantic-positive rule as FLUX.

### Output and licensing (hard invariants)
- **MUST** treat the SynthID watermark as always present: every Gemini-generated image carries it. For branding, commercial, or blog assets this is a material difference from the FLUX-on-Cloudflare path (no watermark) and **MUST** be weighed when choosing the provider.
- **MUST** treat Gemini as billing-required: `gemini-2.5-flash-image` reports a Free-Tier quota of `limit: 0`. That's a provider property, not a prompt concern, but it bears on provider choice (owned by `spec/tools/image-generation/`).

### Anti-patterns
- **MUST NOT** port a FLUX or SDXL comma-tag prompt verbatim to Gemini; rewrite it as narrative prose with stated intent.
- **MUST NOT** use `no X` negatives, prompt weights (`(word:1.3)`, `++`), or emphasis brackets.
- **MUST NOT** apply Imagen's 480-token or roughly-25-character text limits to the native Gemini model, nor assume Nano-Banana-Pro or Nano-Banana-2 limits (larger context, 4K output, more reference images) for `gemini-2.5-flash-image`.
- **MUST NOT** ship a Gemini image as a watermark-free commercial asset; SynthID is always embedded.

## Acceptance Criteria

- [ ] A Gemini prompt under review reads as narrative sentences, not a comma-tag list, and states the asset's intent.
- [ ] In-image text is enclosed in quotes and its font or style is named.
- [ ] Unwanted attributes are phrased positively; no negative-prompt parameter or `no X` tag is used.
- [ ] Editing prompts use conversational or semantic-masking phrasing (`change only X, keep the rest identical`) and account for aspect-ratio inheritance.
- [ ] The prompt targets `gemini-2.5-flash-image` and applies neither Imagen nor Nano-Banana-Pro/2 limits.
- [ ] The generating tool's sidecar records that Gemini produced the asset.
- [ ] Provider choice for a commercial or blog asset accounts for the always-present SynthID watermark.

## References

- [R1] Prompt-document authoring that targets the chosen generator: `spec/design/graphic-prompt-authoring/`
- [R2] The tool whose `gemini` provider calls `gemini-2.5-flash-image`: `spec/tools/image-generation/`
- [R3] The sibling model baseline for the default FLUX path: `spec/design/flux-image-generation/`
- [R4] Brand color contract the prompts must satisfy: `spec/design/corporate-design-colors/`
- [E1] How to prompt Gemini 2.5 Flash Image for the best results (use-case templates, best practices): <https://developers.googleblog.com/en/how-to-prompt-gemini-2-5-flash-image-generation-for-the-best-results/>
- [E2] Nano Banana image generation, official API docs (examples, aspect ratios, SynthID watermark): <https://ai.google.dev/gemini-api/docs/image-generation>
- [E3] Ultimate prompting guide for Nano Banana (frameworks, text-rendering rules, camera and lighting): <https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana>
- [E4] Imagen prompt guide, the boundary case whose 480-token and roughly-25-character text limits the native Gemini model doesn't inherit: <https://ai.google.dev/gemini-api/docs/imagen>

## Open Questions

- **`gemini-2.5-flash-image` exact prompt-token limit.** The native model has no published hard token cap comparable to FLUX's 256 or Imagen's 480; the large context windows cited in guides (131K/65K) belong to the newer Nano-Banana-Pro and Nano-Banana-2 tiers. Treat the 2.5 model's practical limit as generous but not primary-documented until Google publishes a figure.
- **Reference-image count on 2.5.** The "up to 14 reference images" figure is documented for the Nano-Banana-Pro/2 tiers; the supported count for `gemini-2.5-flash-image` specifically isn't primary-verified here. Revisit if Google documents it.
- **Output resolution of the tool's gemini path.** Newer tiers emit 1K/2K/4K; what `gemini-2.5-flash-image` returns by default through the pinned `v1beta` endpoint is a tool-mechanics concern owned by `spec/tools/image-generation/` and isn't restated here.
