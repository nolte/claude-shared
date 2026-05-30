# Prompt Documents — Index

Brand assets for the portfolio's heraldic-animal identity (a sloth), authored per
`spec/design/graphic-prompt-authoring/`. All prompts share one visual register
(`BRAND-STYLE-REF v1`, defined textually in the CHARACTER blocks) and the palette in
`../brand/brand-vocabulary.md`, so every asset reads as a single brand family. The
prompt documents are **self-contained** — the figure is fully described in text, so no
external reference image is needed (and none is committed to the repo).

| Document                                  | Type           | Subject                              | Status               |
| ----------------------------------------- | -------------- | ------------------------------------ | -------------------- |
| `illustration_sloth-mascot.md`            | illustration   | Full sloth mascot (front, light/dark) | character verified ✅ |
| `illustration_sloth-mascot-turnaround.md` | model sheet    | All angles (front/side/back/3-4) + poses | front/side/back verified ✅ |
| `illustration_sloth-mascot-expressions.md`| expression sheet | 12 facial expressions + UI mapping  | 11 verified ✅        |
| `illustration_sloth-coding.md`            | scene          | Sloth coding at a laptop (tech-twist) | verified ✅          |
| `logo_sloth-emblem.md`                    | logo           | Compact heraldic sloth mark          | prompt ready ⬜       |

## The canonical figure (one-line recall)

A chibi cartoon three-toed sloth: deep slate **blue-indigo fur**, a **heart-shaped
cream face mask** (with a V-notch) carrying **two diagonal dark eye-stripes**, two
**dark-brown eyes**, a small dark nose, a gentle closed smile, **two coral-orange
cheeks**, a small **jagged head tuft**, and **exactly three cream claws** per limb.
The cream is **only on the face** — the whole body is solid indigo, **no belly patch**.

## Cross-asset consistency notes

- Same outline treatment (bold, even-weight dark-indigo), same matte fills + single
  cel-shading step, flat warm-bone background, isolated subject.
- Same palette roles: **indigo body** (`#5B5FC7` / slate `#4A4E6B`), **cream face mask
  only** (`#F4F1EA`), **coral-orange cheeks** (`#E8825A`), **dark-brown eyes**
  (`#3A2A22`), dark navy eye-stripes.
- Light vs. dark: re-pull per-mode tokens (indigo → soft cobalt-violet `#8E92E6`,
  dark-indigo outline → warm-bone outline on charcoal) — never RGB inversion.
- Two recurring FLUX.1-schnell traps, handled in every prompt: colour drift to brown
  (assert indigo, negate brown) and a stray cream patch on the body (assert face-only).
- All renders isolated on a flat background for a clean `png-to-transparent-svg` cutout.
