# Prompt Documents — Index

Brand assets for the portfolio's heraldic-animal identity (a sloth), authored per
`spec/design/graphic-prompt-authoring/`. All prompts share one visual register
(`BRAND-STYLE-REF v1.1`, defined textually in the CHARACTER blocks) and the palette in
`../brand/brand-vocabulary.md`, so every asset reads as a single brand family. The
prompt documents are **self-contained** — the figure is fully described in text, so no
external reference image is needed (and none is committed to the repo).

> **v1.1 figure change:** the canonical figure gained a **cool silver-grey signature
> streak** down one side of the head (see one-line recall below). All prompt documents
> carry the v1.1 wording. The **front mascot** and the **logo emblem** are rendered at
> their canonical seeds and ship as committed transparent-SVG vectors under
> `../brand/mascot/` and `../brand/logo/`. The remaining sheets (turnaround, expressions,
> coding) carry the v1.1 wording but are **re-render-pending** — their gitignored
> `design/assets/` renders still show the v1.0 figure without the streak.

| Document                                  | Type           | Subject                              | Status (v1.1)        |
| ----------------------------------------- | -------------- | ------------------------------------ | -------------------- |
| `illustration_sloth-mascot.md`            | illustration   | Full sloth mascot (front, light/dark) | rendered + vectorised ✅ (seed 8505) |
| `illustration_sloth-mascot-turnaround.md` | model sheet    | All angles (front/side/back/3-4) + poses | prompt updated · re-render pending ⬜ |
| `illustration_sloth-mascot-expressions.md`| expression sheet | 12 facial expressions + UI mapping  | prompt updated · re-render pending ⬜ |
| `illustration_sloth-coding.md`            | scene          | Sloth coding at a laptop (tech-twist) | prompt updated · re-render pending ⬜ |
| `logo_sloth-emblem.md`                    | logo           | Compact heraldic sloth mark          | rendered + vectorised ✅ (seed 8521/8505) |

## The canonical figure (one-line recall)

A chibi cartoon three-toed sloth: deep slate **blue-indigo fur**, a **heart-shaped
cream face mask** (with a V-notch) carrying **two diagonal dark eye-stripes**, two
**dark-brown eyes**, a small dark nose, a gentle closed smile, **two coral-orange
cheeks**, a small **jagged head tuft**, a **single cool silver-grey streak down one side
of the head** (the signature "grey lock", the figure's only intentional asymmetry), and
**exactly three cream claws** per limb. The cream is **only on the face** — the whole
body is solid indigo, **no belly patch**.

## Cross-asset consistency notes

- Same outline treatment (bold, even-weight dark-indigo), same matte fills + single
  cel-shading step, flat warm-bone background, isolated subject.
- Same palette roles: **indigo body** (`#5B5FC7` / slate `#4A4E6B`), **cream face mask
  only** (`#F4F1EA`), **coral-orange cheeks** (`#E8825A`), **dark-brown eyes**
  (`#3A2A22`), dark navy eye-stripes, **cool silver-grey side streak** (`#AEB2BE` light /
  `#C9CDD6` dark).
- **Signature streak placement is fixed across the family:** always one side only (the
  same side per asset), running from the head tuft past temple and cheek, on the indigo
  fur **beside** the cream mask — never crossing onto the mask, never mirrored to both
  sides. It is a cool neutral grey, distinctly cooler than the warm cream so the two
  never merge. In a head-on logo/favicon at ≤32 px it may be simplified to a single short
  grey notch in the tuft, or dropped if it muddies the silhouette (see the logo doc).
- Light vs. dark: re-pull per-mode tokens (indigo → soft cobalt-violet `#8E92E6`,
  dark-indigo outline → warm-bone outline on charcoal) — never RGB inversion.
- Two recurring FLUX.1-schnell traps, handled in every prompt: colour drift to brown
  (assert indigo, negate brown) and a stray cream patch on the body (assert face-only).
- All renders isolated on a flat background for a clean `png-to-transparent-svg` cutout.
