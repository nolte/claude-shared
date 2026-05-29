# Graphic Prompt Authoring

Status: draft

## Context

Across the portfolio, AI image generation needs a prompt before it can produce an asset: a hero image for a blog post, an empty-state illustration for a web app, an app icon, a social card. Writing those prompts ad hoc produces two failure modes. First, the prompts drift off-brand—each author reaches for different color words, ignores the published style reference, or hard-codes a hue intuition the `corporate-design-colors` spec forbids. Second, the prompts aren't reproducible: there is no durable artifact recording what was asked for, so regenerating "the same image but wider" months later is guesswork.

This spec governs how a Claude Code agent (the `graphic-prompt-generator` agent, `distribution: plugin`) turns a short graphic brief into a **brand-conformant, generator-ready prompt document on disk**. It's the authoring half of the AI-imagery pipeline: this spec produces the prompt; `spec/tools/gemini-image-generation/` consumes a prompt and emits an image file; `spec/claude/png-to-transparent-svg/` cleans a generated raster into a vector when transparency is needed. The color contract those prompts must satisfy is owned by `spec/design/corporate-design-colors/` §AI image color contract; this spec doesn't restate it, it operationalises it for the prompt-authoring step and extends it to generators beyond Midjourney.

The capability is the generalised successor to a project-local `gemini-graphic-prompt-generator` agent that hard-coded one project's palette, mascot, and file paths. The portfolio form reads the brand from the consuming repository's published design tokens instead of carrying any project's brand in its body.

Readers: skill and agent authors who maintain the prompt-authoring agent; reviewers verifying generated prompt documents conform to the brand; operators who brief the agent and later regenerate assets.

## Goals

- A single graphic brief in, a structured, copy-paste-ready prompt document on disk out—one durable artifact per requested asset
- Every authored prompt is brand-conformant by construction: it consumes the published brand tokens and descriptive color vocabulary rather than re-deriving color from intuition
- Prompts are reproducible: the document records enough (target generator, style reference, descriptive phrases, hex reinforcement, seed slot, target dimensions) to regenerate or tweak the asset later
- The contract is generator-agnostic in shape while letting each prompt target one concrete generator's syntax (Gemini, Midjourney, or a successor) explicitly
- The boundary to the adjacent specs (color contract, image generation, transparency cleanup) is explicit, so the agent isn't invoked outside its authoring envelope

## Non-Goals

- Defining the brand color system, the descriptive-color vocabulary, the canonical style reference (`--sref` or per-model equivalent), or the prompt-assembly color order—all owned by `spec/design/corporate-design-colors/` §AI image color contract; this spec references that contract and must not contradict it
- Actually calling an image generator or writing an image file (owned by `spec/tools/gemini-image-generation/` and any future per-generator sibling)
- Post-processing generated rasters—background cleanup and vectorisation are owned by `spec/claude/png-to-transparent-svg/`
- Non-color imagery axes (composition, lighting, photographic-vs-illustrative register) beyond what a single brief specifies; a future `spec/design/imagery-style/` owns the portfolio-wide treatment
- Maintaining the `brand-prompt-library.md` ledger of *published* hero images (that's a post-generation record owned by `corporate-design-colors`); this spec governs pre-generation prompt documents

## Requirements

### Brand sourcing

- **MUST** resolve the brand from the consuming repository's published design-token bundle and the `brand-vocabulary.md` of approved descriptive color phrases declared by `spec/design/corporate-design-colors/`; the agent **MUST NOT** carry any project's concrete palette, mascot, or brand assets in its own body
- **MUST**, when no published brand bundle or `brand-vocabulary.md` is discoverable in the consuming repository, stop and report the missing brand source rather than inventing color values; an off-brand prompt is worse than no prompt
- **MUST** consume color at the descriptive-phrase and semantic-token layer, never by picking a raw hue; hex values appear in the prompt only as the reinforcement slot defined by the color contract, never as the sole color signal ([corporate-design-colors §AI image color contract](../corporate-design-colors/en.md))
- **MAY** read additional read-only project context (theme token files, an existing style-reference image, prior prompt documents) to keep a batch visually consistent

### Prompt assembly

- **MUST** assemble every brand-aware prompt in the order mandated by `corporate-design-colors` §AI image color contract: (1) the canonical style reference (`--sref` code for Midjourney, or the per-model equivalent for generators without an sref mechanism), (2) descriptive color phrases drawn from `brand-vocabulary.md`, (3) hex values appended as final reinforcement, (4) a recorded seed slot for reproducibility
- **MUST** treat the per-model style-reference equivalent for sref-less generators (a fixed reference image or a canonical style paragraph) as owned by `corporate-design-colors` §AI image color contract; this spec consumes whatever that contract pins and **MUST NOT** decide the equivalent generator-by-generator on its own
- **MUST** target exactly one named generator per prompt and use that generator's prompt syntax; a prompt document **MUST** name its target generator (for example `gemini-2.5-flash-image`, `midjourney-v7`) so a downstream consumer knows which tool the prompt is valid for
- **MUST** include an explicit negative-prompt / avoidance clause (for example: no embedded text, no other companies' logos, no watermark) appropriate to the target generator, because generated text and stray marks are unreliable across current diffusion models
- **MUST NOT** embed legible text or typography as the asset's payload in the prompt; text is added in post-processing, and the prompt document records this as a post-step rather than asking the generator to render copy
- **SHOULD** produce a light-mode and a dark-mode prompt variant whenever the asset will render against both surfaces, deriving the dark variant by re-pulling the dark-mode brand tokens rather than by inverting the light-mode colors
- **SHOULD** include scalability guidance for size-sensitive asset types (icons, favicons, badges): note the smallest target size and what to simplify so the motif stays legible

### Prompt document output

- **MUST** write one Markdown prompt document per requested asset; the agent's value is the durable on-disk artifact, not a chat-only answer
- **MUST** write prompt documents under a single configurable design-prompts directory, defaulting to `design/prompts/` in the consuming repository, and **MUST NOT** hard-code any one project's path (the project-local predecessor wrote to `spec/design/`, which isn't portable)
- **MUST** create the configured design-prompts directory if it doesn't exist (it's an output location, not a precondition), and **MUST NOT** place prompt documents under the `docs/` tree, which is reserved for published audience-facing pages
- No separate pre-generation ledger is maintained; the per-asset document (plus the batch index document below) is the durable pre-generation record. The post-generation `brand-prompt-library.md` remains owned by `corporate-design-colors`
- **MUST** name each document `<asset-type>_<slug>.md` where `<asset-type>` is one of a documented type vocabulary (for example `app-icon`, `logo`, `nav-icon`, `illustration`, `empty-state`, `onboarding`, `hero`, `badge`, `pattern`, `diagram`) and `<slug>` is a kebab-case description (this asset-type vocabulary is provisionally normative here; if `spec/design/imagery-style/` lands it owns non-color imagery axes such as composition and lighting, and the two specs settle whether the file-naming type vocabulary migrates or stays—see §Open Questions)
- **MUST** include in every document: the asset type, target generator, intended variants (light/dark/neutral), target dimensions and file format, the copy-paste-ready prompt blocks, and a post-processing checklist (for example: remove background via `png-to-transparent-svg`; scale and check legibility at 48 px)
- **MUST** record the seed slot (even if empty/`unset`) and the style-reference identifier used, so a later regenerate-with-tweaks is reproducible
- **SHOULD**, when a single brief asks for multiple assets, write an index document and enforce cross-asset visual consistency (same style register, stroke weight, color distribution, perspective) across the batch
- **SHOULD** keep the prompt body free of project-internal jargon a generator can't parse; describe the subject in concrete visual terms

### Write effects and tool surface

- **MUST** restrict writes to Markdown prompt documents under the configured design-prompts directory; the agent **MUST NOT** modify source code, theme tokens, the brand bundle, `brand-vocabulary.md`, or any image asset
- **MUST** treat the brand bundle, `brand-vocabulary.md`, theme tokens, and any style-reference asset as read-only inputs
- **MUST NOT** require network access; prompt authoring is a local read-and-write operation, and the actual generation call is a separate downstream tool

## Acceptance Criteria

- [ ] Briefing the agent for one asset produces exactly one Markdown prompt document under the configured design-prompts directory (default `design/prompts/`), named `<asset-type>_<slug>.md`
- [ ] The authored prompt assembles the four slots in the mandated order (style reference, descriptive phrases, hex reinforcement, seed) and the descriptive phrases all trace to entries in the consuming repository's `brand-vocabulary.md`
- [ ] Invoking the agent in a repository with no published brand bundle or `brand-vocabulary.md` stops with a clear "missing brand source" report and writes no prompt document with invented colors
- [ ] Each prompt document names exactly one target generator and uses that generator's prompt syntax
- [ ] Each prompt document contains a negative-prompt / avoidance clause and a post-processing checklist, and records the seed slot and style-reference identifier
- [ ] A light/dark asset produces two prompt variants whose colors are re-pulled per mode (not RGB-inverted)
- [ ] A multi-asset brief produces an index document and the per-asset prompts share one visual register
- [ ] The agent writes only Markdown under the design-prompts directory; static inspection shows no edits to source, tokens, the brand bundle, or image assets, and no hard-coded single-project path or palette in the agent body
- [ ] The agent declares the minimum tool set (read + write + search) with no execution or network tools, and cites this spec in its body or `description`

## References

- [R1] AI image color contract, descriptive-color vocabulary, style-reference and prompt-assembly order: `spec/design/corporate-design-colors/` §AI image color contract
- [R2] Downstream image-generation tool (prompt in, image file out): `spec/tools/gemini-image-generation/`
- [R3] Post-processing for transparency cleanup and vectorisation: `spec/claude/png-to-transparent-svg/`
- [R4] Agent authoring rules this agent conforms to: `spec/claude/agent-management/`
- [R5] Skill-vs-agent decision rule and rationale-section requirement: `spec/claude/skill-vs-agent/`

## Open Questions

- The per-model style-reference equivalent for sref-less generators is owned by `corporate-design-colors` §AI image color contract; this spec consumes whatever that contract pins. Pending in that spec: `corporate-design-colors` must declare whether the equivalent is a fixed reference image (recommended) or a canonical style paragraph.
- Default: the asset-type vocabulary stays provisionally normative here because the file-naming MUST needs it now; `spec/design/imagery-style/` is scoped to non-color imagery axes (composition, lighting, photographic-vs-illustrative register), so the expected outcome is that the naming vocabulary stays here. Revisit when: a file appears under the `spec/design/imagery-style/` path—at that moment, confirm explicitly whether the file-naming type vocabulary migrates to `imagery-style` or stays here as a naming-only taxonomy.
