# Brand Vocabulary

> **Status:** v1 anchor — palette aligned with the decided canonical values.
> Governed by `spec/design/corporate-design-colors/` §AI image color contract.
> The `brand-primary` OKLCH triplet was decided by the brand owner on
> **2026-06-06** as `oklch(0.47 0.12 276)` / `#4A529D` (recorded in that spec's
> §Brand harmony axes); every derived entry below is recomputed from that
> anchor (reconciled 2026-07-25, 2026-Q3 audit, #494). The full DTCG token
> bundle (12-step ramps, WCAG-AA measurements, exports) remains a follow-up.

This file lists the approved descriptive color phrases a diffusion model can parse,
each paired with the OKLCH triplet (canonical) and the rounded sRGB hex (derived
reinforcement). Agents and prompt documents read this file; they never invent hues.

## Brand identity slots

| Slot              | Role                                                        | Descriptive phrase(s)                  | OKLCH (canonical)        | Hex (derived) |
| ----------------- | ----------------------------------------------------------- | -------------------------------------- | ------------------------ | ------------- |
| `brand-primary`   | Single identity hue (one per portfolio)                     | "muted indigo"                         | `oklch(0.47 0.12 276)`   | `#4A529D`     |
| `brand-secondary` | Harmonic axis — split-complementary of primary (126°)       | "warm moss green", "soft fern green"   | `oklch(0.62 0.11 126)`   | `#769244`     |
| `brand-accent`    | Functional emphasis only (eyes, highlights, CTA)            | "warm amber", "honey gold"             | `oklch(0.78 0.13 75)`    | `#E0A23C`     |
| `brand-complement`| True 180° complement — chart / illustration accents only    | "soft yellow-green"                    | `oklch(0.80 0.10 96)`    | `#D1BE71`     |

`brand-secondary` is derived as a **split-complementary** of `brand-primary`
(primary hue 276° → 180° complement 96° → the two split angles 96° ± 30° =
66° and 126°; the chosen axis is **126°**), which keeps the natural,
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
| "muted indigo"          | light| Primary fills, outlines                   | `oklch(0.47 0.12 276)`  | `#4A529D`     |
| "soft cobalt-violet"    | dark | Primary fills in dark mode (lighter/lower chroma per spec §Light/dark) | `oklch(0.72 0.10 276)`  | `#939FE3`     |
| "warm moss green"       | light| Secondary foliage accents                 | `oklch(0.62 0.11 126)`  | `#769244`     |
| "soft fern green"       | dark | Secondary foliage accents in dark mode    | `oklch(0.72 0.10 126)`  | `#95B06A`     |
| "cool silver-grey"      | light| Signature grey fur streak (figure marking, not a brand fill) | `oklch(0.74 0.010 275)` | `#AEB2BE`     |
| "pale silver"           | dark | Signature grey fur streak in dark mode    | `oklch(0.84 0.008 275)` | `#C9CDD6`     |

## Canonical style reference

- **Generator class:** Cloudflare FLUX.1-schnell (and other generators without a
  Midjourney `--sref` mechanism) use the **per-model equivalent**: a fixed canonical
  style paragraph (and, once approved, a fixed reference image) per
  `corporate-design-colors` §AI image color contract.
- **Current reference:** `BRAND-STYLE-REF v1.1` — the canonical figure is anchored by a
  **fixed canonical reference image**: `design/brand/mascot/mascot-front-light.svg`
  (the approved, committed vector master; dark-mode counterpart
  `mascot-front-dark.svg`), per the settled `corporate-design-colors` rule that a
  generator without `--sref` needs a fixed image because a free-text style paragraph
  drifts between runs. The CHARACTER block in `../prompts/illustration_sloth-mascot.md`
  remains the textual companion (repeated verbatim inside each prompt document so a
  batch stays one visual register), but the image is authoritative on conflict.
  A later reference refresh is a major brand-version bump. **v1.0 → v1.1** added the cool
  silver-grey signature side streak (see §Signature marking below); the committed
  `design/assets/` renders predate it and are re-render-pending.
- **Key identity rule:** the cream warm-bone is **only on the face mask**; the entire
  body (chest, belly, back, sides) is solid indigo — there is **no belly patch**. The
  only other pale areas are the three claws per hand/foot.
- **Signature marking (since v1.1):** a single **cool silver-grey fur streak** — the
  "grey lock" — runs down **one side of the head** (from the tuft, past temple and cheek
  toward the jaw), lying on the indigo fur **beside** the cream mask, never across it. It
  is the only intentional asymmetry of the figure and the strongest recognition cue after
  the diagonal eye-stripes. The streak is a **cool neutral silver-grey** (`#AEB2BE`
  light / `#C9CDD6` dark) — clearly cooler and greyer than the warm cream mask so the two
  never read as one patch.
- **Observed render note:** FLUX.1-schnell rendered the v1 fur as a deep slate-indigo
  (`~#4A4E6B`) — darker and bluer than the *bootstrap* token then in force (`#5B5FC7`),
  and close to the since-decided canonical `brand-primary` (`#4A529D`). The decided
  token is canonical; the committed renders therefore sit near-on-token and the earlier
  divergence note is resolved history, kept only to explain the v1 prompt wording.

## Follow-ups (out of scope for this bootstrap)

- Full DTCG token bundle: 12-step primary/secondary/tertiary/neutral ramps, semantic
  layer, light/dark per-token resolution, WCAG-2.2-AA contrast measurements, DTCG export,
  Mermaid theme pair (per `corporate-design-colors` Acceptance Criteria).
- ~~`brand-prompt-library.md` alongside this file~~ — created 2026-07-25 (#494), one
  row per *published* hero image; keep it updated with every new published asset.
