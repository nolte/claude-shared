# Corporate Design—Color System

Status: draft

## Context

Every artifact this portfolio ships—web applications, documentation sites, blog posts, README badges, Mermaid diagrams, and AI-generated hero imagery—must read as part of one recognizable brand. Color is the load-bearing axis: a reader scanning a release-notes page, a hero image at the top of a marketing post, and a Mermaid sequence diagram in a spec should all feel like the same product family before any text registers. This spec governs that color axis: it fixes one master brand, codifies how complementary, split-complementary, analog, and tertiary hues relate to it, and turns the result into a portable token set that human authors and Claude-driven skills/agents can both consume.

The spec is intentionally narrow: it covers color only. Typography, spacing, iconography, imagery composition, and voice are explicitly out of scope and will land as sibling specs under `spec/design/` later. The work here is the load-bearing pre-requisite for those follow-ups, so it must be defensible on its own and provide the token contract the later specs will plug into.

Readers: brand implementers picking the concrete OKLCH values; skill and agent authors who generate token bundles, Mermaid themes, README badges, or AI hero images; and reviewers verifying that downstream artifacts conform to the published palette.

## Goals

- One master brand identity governs every nolte/* repository; no per-project sub-brand forks
- Color decisions are reproducible across three artifact classes (web/docs UI, AI hero imagery, ancillary visuals like badges and diagrams)
- Complementary, split-complementary, and tertiary hue relationships are explicit and named, not implicit operator taste
- WCAG 2.2 AA contrast is the enforced baseline; APCA Lc-thresholds ride along as a forward-compatible quality gate
- The published token set survives ingestion by CSS, Tailwind v4, Figma, Mermaid, and Style Dictionary without per-platform divergence
- AI image generation reproduces the brand color signature deterministically enough that two heroes generated months apart still read as the same brand

## Non-Goals

- Typography, spacing scale, iconography, imagery composition, motion, and voice (each becomes its own `spec/design/…` sibling)
- Per-project sub-brand systems, white-label theming, or end-user theme customisation
- Marketing-creative direction beyond the color signature (illustration style, photo treatment lives in a future imagery spec)
- Choice of build tooling for the token export pipeline (the *format* is normative, the *builder* isn't)

## Requirements

### Color space and source of truth

- **MUST** store every primitive color token in `oklch(L C H)` notation; OKLCH is the canonical source, hex and sRGB are derived outputs ([Tailwind v4 release notes—OKLCH default](https://tailwindcss.com/blog/tailwindcss-v4), [Evil Martians—OKLCH in CSS](https://evilmartians.com/chronicles/oklch-in-css-why-quit-rgb-hsl))
- **MUST NOT** use HSL or HSV as the canonical color space because HSL-lightness isn't perceptually uniform—identical L-values across hues produce visibly different brightness ([Evil Martians—OKLCH in CSS](https://evilmartians.com/chronicles/oklch-in-css-why-quit-rgb-hsl), [CSS-Tricks article on `oklch()`](https://css-tricks.com/almanac/functions/o/oklch/))
- **MUST** document every primitive token with both its canonical OKLCH triplet and the rounded sRGB hex equivalent so downstream consumers without OKLCH support stay legal
- **SHOULD** simulate every semantic token against the three common color-vision-deficiency profiles (protan, deutan, tritan) using Adobe Leonardo or an equivalent CVD-aware generator before the token is promoted to canonical ([adobe.design—Leonardo](https://adobe.design/toolkit/leonardo))

### Token architecture

- **MUST** organise tokens in three layers, in this order: `primitive` (raw OKLCH ramp steps, hue-named only), `semantic` (role-named, for example `color.background.surface`, `color.text.primary`), and `component` (only when a component-unique decision genuinely can't be expressed semantically) ([Atlassian Design Tokens](https://atlassian.design/foundations/tokens/design-tokens), [IBM Carbon—Color Overview](https://carbondesignsystem.com/elements/color/overview/), [Contentful—Design Token System](https://www.contentful.com/blog/design-token-system/))
- **MUST** name semantic tokens by role and context, never by hue or numeric step (`color.surface.elevated` is legal; `color.indigo.500` isn't at the semantic layer)
- **MUST NOT** consume a primitive token directly from application code; consumers reference semantic (or component) tokens, never primitives
- **SHOULD** keep the semantic layer flat enough that any new token is reviewable in one screen; if the semantic layer crosses ~120 tokens, split by sub-domain (`color.text.*`, `color.background.*`) before adding more
- **MUST** treat the same semantic token name as mode-resolving: `color.background.surface` resolves to different OKLCH values in light vs. dark mode but keeps one name ([Primer—Color usage](https://primer.style/foundations/color/), [Radix—Dark mode](https://www.radix-ui.com/themes/docs/theme/dark-mode))

### Brand harmony axes

The brand identity vocabulary defines four slot names: `brand-primary`, `brand-secondary`, `brand-accent`, and `brand-complement`. All four are derived from a single anchor (`brand-primary`) via the geometric or functional relationship specified per slot below. `brand-tertiary` is an optional functional hue, defined as a separate MAY-slot below, and isn't part of the four-slot brand identity vocabulary. Operator choices are constrained to the per-slot relationships below.

- **MUST** define exactly one `brand-primary` hue. The primary key color is the single recognizable signature of the portfolio and never changes per repository. **Canonical value (brand-owner decision, 2026-06-06): `oklch(0.47 0.12 276)`, sRGB hex `#4A529D`, a muted indigo.** Chroma 0.12 sits well inside the sRGB gamut (peak ~0.29 at this lightness and hue), leaving headroom for the peak-chroma ramp Step 9 and for the +60° tertiary and 180° complement derivations
- **MUST** define the `brand-secondary` axis as either **split-complementary** (`brand-primary` hue ± 30° from the 180° complement, two angles) or **analog** (`brand-primary` hue ± 30°). True 180° complement is forbidden as the brand secondary because it produces eye-strain when used on large surfaces and is difficult to use for body text ([Figma—Complementary Colors](https://www.figma.com/resource-library/what-are-split-complementary-colors/), [Sketch—Color Combination Guide](https://www.sketch.com/blog/color-combination-guide/))
- **MAY** introduce a `brand-tertiary` hue—an optional functional hue outside the four-slot brand identity vocabulary—derived via a +60° hue rotation from `brand-primary` at tone 40, with chroma set to the peak the +60° hue's gamut admits per §Ramp structure (not a fixed numeric chroma). This follows Material 3's tertiary derivation geometry, but Material 3's chroma 24 is a non-binding starting anchor that the peak-chroma-per-gamut rule overrides. Use it when charts, illustrations, or marketing genuinely need a third functional axis ([Material 3—Color roles](https://m3.material.io/styles/color/roles), [Material Color Utilities—dynamic color scheme](https://github.com/material-foundation/material-foundation-material-color-utilities))
- **MAY** use the true 180° complement of `brand-primary` only as a **punctual accent** (single-element emphasis: a chart highlight, a callout band, a CTA on a low-saturation surface). It MUST NOT be promoted to body, surface, large flat fills, or running text
- **MUST** maintain vocabulary hygiene. Four slots are defined and no other slot name is legal in skills, agents, or downstream documentation:
  - `brand-primary`: single identity hue (one per portfolio)
  - `brand-secondary`: the harmonic axis derived from primary per the rule above (`split-complementary` or `analog`)
  - `brand-accent`: functional emphasis only (CTA, active state); can't be promoted to surface, body, or large flat fills
  - `brand-complement`: true 180° complement of primary, restricted to chart and illustration accents

  Skills, agents, and downstream documentation MUST use these four terms with this precise meaning and MUST NOT introduce a fifth brand identity slot name. `brand-tertiary` is the only legal name outside this set and is governed by the optional-functional-hue rule above ([Vercel Geist—Colors](https://vercel.com/geist/colors), [Supabase—Color usage](https://supabase.com/design-system/docs/color-usage))

### Ramp structure

- **MUST** generate every chromatic ramp (primary, secondary, tertiary, danger, success, warning, info) as a 12-step scale with the following functional slot assignment, mirroring Radix' palette composition ([Radix—Understanding the Scale](https://www.radix-ui.com/colors/docs/palette-composition/understanding-the-scale)):

  | Steps  | Role                                                            |
  | ------ | --------------------------------------------------------------- |
  | 1–2    | App background (page surface; subtle surface)                   |
  | 3–5    | Component background, hover state, active/pressed state         |
  | 6–8    | Borders, dividers, focus rings                                  |
  | 9      | Solid (peak chroma; brand fill, primary button background)      |
  | 10     | Solid hover                                                     |
  | 11     | Low-contrast accessible text on Step 1/2                        |
  | 12     | High-contrast accessible text / iconography on Step 1/2         |

- **MUST** generate the neutral ramp (`neutral.1` … `neutral.12`) with chroma ≤ 0.01 in OKLCH so the brand reads as one warm or one cool family throughout; mixed neutrals are forbidden
- **MUST** keep Step 9 of each chromatic ramp at the peak chroma the hue's gamut admits, not at a uniform numeric chroma, because OKLCH gamut clipping varies per hue
- **SHOULD** apply Stripe's step-distance heuristic as a quick contrast check before measuring exact ratios: pair any two same-ramp steps with at least 5 steps of distance for text-on-background, and at least 4 steps of distance for icon-on-background or large-text-on-background ([Stripe—Accessible Color Systems](https://stripe.com/blog/accessible-color-systems)). The heuristic doesn't relax the WCAG gates in §Contrast gates; failing the heuristic but passing WCAG is legal, the heuristic is only a quick filter

### Light/dark mode pairing

- **MUST** ship every semantic token in both `light` and `dark` mode variants; dark mode isn't optional
- **MUST** derive the dark-mode `brand-primary` solid (Step 9 in dark) from the light-mode Step 4–6 range (lower chroma, higher lightness) rather than by HSL or RGB inversion of the light-mode value ([Material—Dark theme](https://design.google/library/material-design-dark-theme), [Inkbot Design—Dark Mode](https://inkbotdesign.com/dark-mode/))
- **MUST NOT** use pure `#000000` (`oklch(0 0 0)`) as the dark-mode root surface; the darkest legal surface is `oklch(0.16 0 <hue>)` or higher (≈ Material's `#121212` baseline), with the neutral hue carried into the dark surface to keep the brand-warm or brand-cool signature consistent ([Material—Dark theme](https://design.google/library/material-design-dark-theme), [Webheads United—Dark mode palette principles](https://webheadsunited.com/guide-to-dark-mode-color-palette-principles/))
- **SHOULD** keep both modes derivable from one parametric algorithm (one OKLCH lightness curve per mode) so adding a new chromatic ramp produces a balanced light/dark pair without per-step tuning

### Contrast gates

The published palette MUST pass these gates at the semantic-token layer, not only at the primitive layer.

- **MUST** meet WCAG 2.2 AA SC 1.4.3 *Contrast (Minimum)*: 4.5:1 for normal text, 3:1 for large text (≥18pt regular or ≥14pt bold), measured pair-wise on every semantic text-on-background combination the design system declares legal ([W3C—SC 1.4.3](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html))
- **MUST** meet WCAG 2.2 AA SC 1.4.11 *Non-text Contrast*: 3:1 for UI component state visuals (focus rings, active state borders, form-control outlines) and for graphical objects required to understand content (chart fills, icon-only buttons) against adjacent color ([W3C—SC 1.4.11](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html))
- **MUST NOT** round contrast ratios up to meet the threshold; a measured 4.49:1 fails 4.5:1
- **SHOULD** additionally validate against APCA Lc thresholds for forward-compatibility with WCAG 3.0: body text Lc ≥ 75, microcopy Lc ≥ 90, large headlines Lc ≥ 60. APCA fails count as `SHOULD-fail`, not `MUST-fail`, until APCA becomes normative ([APCA in a Nutshell](https://git.apcacontrast.com/documentation/APCA_in_a_Nutshell.html), [Radix—Understanding the Scale](https://www.radix-ui.com/colors/docs/palette-composition/understanding-the-scale))
- **MAY** exempt the brand wordmark, logo glyphs, and decorative hero imagery from the contrast gates per WCAG SC 1.4.3's logotype carve-out; functional UI components (buttons, links, form controls, icons that carry meaning) MUST still meet the gates above ([W3C—SC 1.4.3](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html))

### Composition heuristic (60-30-10)

- **SHOULD** apply a 60 % neutral surface / 30 % `brand-secondary` / 10 % `brand-accent` distribution as a starting point for hero compositions, marketing pages, and high-density UI views, and only deviate with a documented reason. The 60-30-10 rule is interior-design folklore mapped onto UI design, not a normatively-proven invariant, so it stays SHOULD and never becomes MUST ([Apartment Therapy—60-30-10 explained](https://www.apartmenttherapy.com/interior-design-rule-60-30-10-explained-37504313))

### Per-artifact application

Each artifact class binds to the semantic-token layer. Skills and agents that generate these artifacts read the semantic tokens, never primitives or component tokens.

- **MUST** consume the semantic token set in web applications and documentation sites via CSS Custom Properties or framework-native theming (Tailwind v4 `@theme` block, MUI `createTheme`, Mantine theme object, shadcn/ui `:root` block) ([shadcn/ui—Theming](https://ui.shadcn.com/docs/theming), [Tailwind v4 release notes](https://tailwindcss.com/blog/tailwindcss-v4))
- **MUST** publish a Mermaid theme mapping that resolves the Mermaid theme variables (`primaryColor`, `primaryTextColor`, `primaryBorderColor`, `lineColor`, `secondaryColor`, `tertiaryColor`, `background`, `mainBkg`, `secondBkg`, `tertiaryBkg`) to semantic tokens, so diagrams in MkDocs and READMEs inherit the brand without per-diagram styling
- **MUST** publish the Mermaid theme mapping as a **light/dark pair** bound to the mode-resolving semantic tokens (per §Light/dark mode pairing), never as a single mode-agnostic theme, because the Material light/dark theme bridge that `spec/project/mermaid-diagrams/` mandates swaps theme variables per mode and a mode-agnostic theme would break dark-mode rendering
- **MUST** inject this theme mapping through a single global configuration (one MkDocs hook or `extra_javascript` entry that sets the Mermaid theme config once for the whole site), never through per-diagram `%%{init: … }%%` overrides; per-diagram overrides are the inline styling that `spec/project/mermaid-diagrams/` forbids. The wiring rule lives in `spec/project/mermaid-diagrams/` §MkDocs setup
- **MUST** treat all README badge colors (`shields.io` `color=` and `labelColor=` parameters, custom SVG badges) as bound to the semantic token set; ad-hoc `color=blue` style values are forbidden
- **MUST** version-lock a brand-themed favicon palette and a brand-themed social-card (Open Graph image) palette as semantic tokens, so a docs site, a blog post share, and a GitHub repo card share one color signature
- **SHOULD** prepare a print/PDF fallback palette (CMYK approximations of the canonical OKLCH values) so generated PDFs—release notes, hand-outs, slide decks exported to PDF—don't silently drift
- **MUST**, when a CMYK fallback palette exists per the rule above, regenerate it whenever the canonical OKLCH for any of its bound semantic tokens changes; CMYK conversion is lossy and stale conversions silently drift apart from screen output

### AI image color contract

This subsection governs hero images, social cards, and any other AI-generated imagery. The contract has to be tight enough that two heroes generated months apart read as the same brand.

- **MUST** maintain one fixed Midjourney `--sref <code>` (or per-model equivalent) as the canonical brand style reference, version it like a token (named, approved, brand-version-tagged), and store it in the same publication artifact as the color tokens ([Midjourney—Style Reference](https://docs.midjourney.com/hc/en-us/articles/32180011136653-Style-Reference), [Numonic—Midjourney brand consistency](https://www.numonic.ai/blog/midjourney-brand-consistency-guide))
- **MUST** define the per-model equivalent for generators without an `--sref` mechanism (for example Gemini) as a **fixed canonical reference image**: image-conditioning is the closest functional analog to `--sref` and survives across regenerations, whereas a free-text style paragraph drifts between runs. Version and store this reference image exactly like the `--sref` code. This contract owns the per-model equivalent; consuming specs (for example `graphic-prompt-authoring`) **MUST NOT** redefine it generator-by-generator
- **MUST** assemble every brand-aware AI image prompt in this fixed order: (1) the canonical `--sref <code>`, (2) descriptive color phrases pulled from the brand vocabulary (for example "muted indigo," "warm off-white," "deep neutral charcoal"), (3) the hex values appended as final reinforcement at the end of the prompt, (4) a recorded `--seed` for reproducibility ([Midjourney—Style Reference](https://docs.midjourney.com/hc/en-us/articles/32180011136653-Style-Reference), [CometAPI—colors in Midjourney v7](https://www.cometapi.com/how-to-get-specific-colors-in-midjourney-v7/))
- **MUST NOT** rely solely on hex codes in the prompt body to enforce brand color; pure hex parsing is unreliable in every current diffusion model ([CometAPI—colors in Midjourney v7](https://www.cometapi.com/how-to-get-specific-colors-in-midjourney-v7/), [Skywork—lock brand colors](https://skywork.ai/blog/how-to-lock-brand-colors-prompt-constraints-guide/))
- **MUST** maintain a `brand-vocabulary.md` of approved descriptive color phrases (the names a diffusion model can parse: "muted teal," "cobalt," "warm bone," "deep forest"), paired with the OKLCH triplet they resolve to in the canonical palette; agents read this file when composing prompts
- **MUST** record the full prompt stack (model + version, `--sref`, seed, style weight, descriptive phrases, hex reinforcements) for every published hero image in a versioned `brand-prompt-library.md`, kept as a separate file alongside `brand-vocabulary.md` (one row per published hero image), so a regenerate-with-tweaks operation is reproducible
- **MUST** house both `brand-vocabulary.md` and `brand-prompt-library.md` under `design/brand/` in the bundle-producer repository, parallel to the `design/prompts/` convention that `spec/design/graphic-prompt-authoring` fixes for prompt documents; the relative path is normative even while the bundle-producer repository isn't yet selected (that deferral is recorded in `.audits/decisions/2026-06-06-settle-open-questions.md`)
- **SHOULD** prefer the descriptive-color-name slot over the hex-reinforcement slot for primary brand colors; reserve the hex reinforcement for the punctual accent or for hues whose descriptive name is ambiguous ([Numonic—Midjourney brand consistency](https://www.numonic.ai/blog/midjourney-brand-consistency-guide))
- **MAY** maintain alternate `--sref` codes (or per-model equivalents) for sub-contexts (technical-illustration, photographic-product, abstract-marketing) under one brand family; alternate sref codes MUST share the same descriptive-color vocabulary so the brand signature survives the context switch

### Publication and export

- **MUST** publish the canonical token set in W3C Design Tokens Community Group format (DTCG 2025.10 or later): `$type: "color"`, `$value` object with `colorSpace`, `components`, optional `alpha`, optional `hex`; group references use the `{group.token}` curly-brace syntax; circular references are forbidden ([DTCG Format Module](https://www.designtokens.org/tr/drafts/format/), [W3C—DTCG first stable announcement](https://www.w3.org/community/design-tokens/2025/10/28/design-tokens-specification-reaches-first-stable-version/))
- **MUST** export the canonical set to, at minimum, (a) CSS Custom Properties under `:root` and `[data-theme="dark"]`, (b) Tailwind v4 `@theme` block, (c) Figma Variables (JSON), and (d) Mermaid theme variables, from a single build step. Style Dictionary is the recommended builder; the build tool isn't normative, the output set is ([Style Dictionary—Examples](https://styledictionary.com/getting-started/examples/), [Tokens Studio—Token format](https://docs.tokens.studio/manage-settings/token-format))
- **MUST** version the token bundle with semantic versioning; a hue change in the primary or secondary axis is a major-version bump, a non-perceptible reorganisation is a patch, every other token-set change is a minor bump
- **MUST** ship the published token bundle as a portfolio-versioned artifact that downstream repositories pin (in the same way that `nolte/vale-style` is pinned by every prose-linting repo per `spec/project/prose-style/`); ad-hoc copy-paste of the palette into a consumer repo is forbidden

### Governance and change control

- **MUST NOT** introduce a new primitive color step without verifying it's reachable from `brand-primary` via the documented hue offsets (0°, ±30°, ±60°, 180°); ad-hoc hex picks by hue intuition are forbidden
- **MUST** route every change to a chromatic ramp through this spec's review: the change request names the affected ramp, the OKLCH delta, the resulting contrast deltas at every legal text-on-background pair, and the resulting Lc deltas for APCA
- **SHOULD** keep a brand-change log inside the published token bundle documenting every major or minor change with the rationale and the contrast deltas at the time of the change
- **MUST NOT** silently re-derive the AI image `--sref` codes when refreshing the brand; refreshing the sref is a major-version bump because every previously generated hero is now off-brand

## Acceptance Criteria

- [ ] One `brand-primary` OKLCH triplet is declared canonical, with its hex equivalent and gamut footprint
- [ ] The `brand-secondary` axis is declared as either `split-complementary` or `analog` with the explicit hue offsets and rationale
- [ ] `brand-tertiary` is either declared with the +60°/tone-40/peak-chroma derivation rule (Material 3 geometry, peak chroma per §Ramp structure) or explicitly omitted with reasoning
- [ ] Every chromatic ramp has 12 steps with the Radix-style functional slot assignment documented in a table
- [ ] Step 9 of every chromatic ramp sits within 2 chroma units of the OKLCH gamut boundary for its hue (peak-chroma rule), not at a uniform numeric chroma
- [ ] Every neutral step has OKLCH chroma ≤ 0.01
- [ ] The four-slot brand identity vocabulary table (`brand-primary`, `brand-secondary`, `brand-accent`, `brand-complement`) is present and no fifth brand identity slot name appears anywhere in the published bundle or its consumer documentation; `brand-tertiary` is permitted under the optional-functional-hue rule and isn't counted as a fifth identity slot
- [ ] Light and dark mode resolve every semantic token; no semantic token is single-mode
- [ ] No dark-mode surface uses `oklch(0 0 0)`
- [ ] Every legal text-on-background semantic-token pair has a recorded WCAG-2.2-AA contrast ratio at or above the SC 1.4.3 / SC 1.4.11 thresholds, with the raw (un-rounded) measurement preserved
- [ ] Every legal interactive-state semantic-token pair has a recorded APCA Lc value; out-of-range values are listed as SHOULD-fails with a remediation plan
- [ ] The published token bundle validates against DTCG 2025.10 schema
- [ ] The bundle exports cleanly to CSS Custom Properties, Tailwind v4 `@theme`, Figma Variables JSON, and a Mermaid theme mapping from one build step
- [ ] A favicon palette token set and a social-card (Open Graph image) palette token set exist in the published bundle, are versioned, and bind to semantic tokens
- [ ] No README badge across the consuming portfolio repositories uses a literal color value in the `shields.io` `color=` or `labelColor=` parameter; every badge color traces to a semantic token in the published bundle
- [ ] One canonical Midjourney `--sref` code (or per-model equivalent) is declared, versioned, and referenced from the bundle
- [ ] A `brand-vocabulary.md` exists, lists every approved descriptive color phrase, and pairs each phrase to a semantic or primitive token
- [ ] A versioned `brand-prompt-library.md` exists alongside `brand-vocabulary.md` as a separate file and carries one entry per published hero image with model+version, `--sref`, seed, style weight, descriptive phrases, and hex reinforcements
- [ ] The published bundle is consumed by at least one downstream repository via a pinned version pointer (not copy-paste)
- [ ] Every merged PR that modifies a chromatic ramp token carries a change-request body naming the affected ramp, the OKLCH delta, the contrast deltas at every legal text-on-background pair, and the Lc deltas for APCA
- [ ] A change-log entry exists for every major or minor brand-version bump, with the contrast and Lc deltas at the time of the change

## Open Questions

_All open questions are resolved. The `brand-primary` anchor was decided by the brand owner on 2026-06-06 as a muted indigo `oklch(0.47 0.12 276)` / `#4A529D` (recorded in §Brand harmony axes); the token-bundle-registry, CMYK, and imagery-style hand-off deferrals were settled the same day. See `.audits/decisions/2026-06-06-settle-open-questions.md` for the full record._
