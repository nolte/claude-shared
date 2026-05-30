# Brand Vocabulary

> **Status:** v0 anchor (draft) — bootstrap palette for the first brand assets.
> Governed by `spec/design/corporate-design-colors/` §AI image color contract.
> The exact `brand-primary` OKLCH triplet is the brand owner's deferred decision
> (see that spec's Open Questions); the values below adopt the spec's recommended
> **muted indigo** anchor and may be precision-validated when the full DTCG token
> bundle (12-step ramps, WCAG-AA measurements, exports) lands.

This file lists the approved descriptive color phrases a diffusion model can parse,
each paired with the OKLCH triplet (canonical) and the rounded sRGB hex (derived
reinforcement). Agents and prompt documents read this file; they never invent hues.

## Brand identity slots

| Slot              | Role                                                        | Descriptive phrase(s)                  | OKLCH (canonical)        | Hex (derived) |
| ----------------- | ----------------------------------------------------------- | -------------------------------------- | ------------------------ | ------------- |
| `brand-primary`   | Single identity hue (one per portfolio)                     | "muted indigo"                         | `oklch(0.55 0.13 275)`   | `#5B5FC7`     |
| `brand-secondary` | Harmonic axis — split-complementary of primary (~145°)      | "warm moss green", "soft fern green"   | `oklch(0.62 0.11 150)`   | `#4F9D69`     |
| `brand-accent`    | Functional emphasis only (eyes, highlights, CTA)            | "warm amber", "honey gold"             | `oklch(0.78 0.13 75)`    | `#E0A23C`     |
| `brand-complement`| True 180° complement — chart / illustration accents only    | "soft yellow-green"                    | `oklch(0.80 0.10 110)`   | `#B7C24F`     |

`brand-secondary` is derived as a **split-complementary** of `brand-primary`
(primary hue 275° → 180° complement 95° → −30° ≈ 150°), which keeps the natural,
foliage-friendly green that suits the sloth heraldic animal while staying
spec-conformant. No fifth brand identity slot name is introduced.

## Neutrals (warm family, chroma ≤ 0.01)

| Phrase                  | Role                              | OKLCH (canonical)       | Hex (derived) |
| ----------------------- | --------------------------------- | ----------------------- | ------------- |
| "warm bone white"       | Light-mode surface                | `oklch(0.95 0.008 90)`  | `#F4F1EA`     |
| "deep warm charcoal"    | Dark-mode surface (never #000000) | `oklch(0.25 0.008 275)` | `#20222A`     |

## Light / dark derivation (re-pull per mode, never invert)

| Phrase                  | Mode | Use                                       | OKLCH (canonical)       | Hex (derived) |
| ----------------------- | ---- | ----------------------------------------- | ----------------------- | ------------- |
| "muted indigo"          | light| Primary fills, outlines                   | `oklch(0.55 0.13 275)`  | `#5B5FC7`     |
| "soft cobalt-violet"    | dark | Primary fills in dark mode (lighter/lower chroma per spec §Light/dark) | `oklch(0.72 0.10 275)`  | `#8E92E6`     |
| "warm moss green"       | light| Secondary foliage accents                 | `oklch(0.62 0.11 150)`  | `#4F9D69`     |
| "soft fern green"       | dark | Secondary foliage accents in dark mode    | `oklch(0.72 0.10 150)`  | `#6FBF8A`     |

## Canonical style reference

- **Generator class:** Cloudflare FLUX.1-schnell (and other generators without a
  Midjourney `--sref` mechanism) use the **per-model equivalent**: a fixed canonical
  style paragraph (and, once approved, a fixed reference image) per
  `corporate-design-colors` §AI image color contract.
- **Current reference:** `BRAND-STYLE-REF v1` — the canonical figure is defined
  **textually** by the CHARACTER block in `../prompts/illustration_sloth-mascot.md`
  (self-contained; no external reference image is stored in the repo). The style block
  is repeated verbatim inside each prompt document so a batch stays one visual register.
  A later reference refresh is a major brand-version bump.
- **Key identity rule:** the cream warm-bone is **only on the face mask**; the entire
  body (chest, belly, back, sides) is solid indigo — there is **no belly patch**. The
  only other pale areas are the three claws per hand/foot.
- **Observed render note:** FLUX.1-schnell rendered the fur a touch darker and bluer
  than the `brand-primary` token (`#5B5FC7`) — closer to a deep slate-indigo
  (`~#4A4E6B`). The token stays canonical; prompts describe the observed look so new
  renders match v1.

## Follow-ups (out of scope for this bootstrap)

- Full DTCG token bundle: 12-step primary/secondary/tertiary/neutral ramps, semantic
  layer, light/dark per-token resolution, WCAG-2.2-AA contrast measurements, DTCG export,
  Mermaid theme pair (per `corporate-design-colors` Acceptance Criteria).
- `brand-prompt-library.md` alongside this file: one row per *published* hero image
  (model+version, style reference, seed, descriptive phrases, hex reinforcements).
