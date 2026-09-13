# Graphic Prompt: Sloth Mascot — Coding at a Laptop (scene)

> **Type:** illustration (scene)
> **Generator:** cloudflare flux-1-schnell
> **Variants:** Light (default)
> **Target size:** 1024×1024px
> **Style reference:** `BRAND-STYLE-REF v1.1`, anchored by `design/brand/mascot/mascot-front-light.svg`, a v1.0-figure render that is re-render-pending for the v1.1 streak (see `../brand/brand-vocabulary.md` §Canonical style reference); the prompt below carry it as text
> **Seed:** pass an explicit `--seed`; verified-good seeds listed below

## Context
The "working / coding" scene of the mascot — the heraldic sloth sitting at a low
table, typing on a laptop, a mug beside it. A friendly tech-twist for the portfolio
landing, an "about / dev" section, or a 404/build page. Composition derived from an
approved render: full-body sloth, centered, behind a low wooden table, flat
warm-bone background (easy to cut out).

## ⚠️ Two FLUX traps this scene hits (both handled below)

1. **Scene ignored when the character leads.** A long character description makes
   FLUX render just the isolated mascot and drop the laptop/desk entirely. **Fix:
   lead with the action** ("a sloth sitting behind a table typing on a laptop"),
   then add the character details as modifiers. (Scene-first, the same lesson as
   view-first in the turnaround sheet.)
2. **Silver laptop → Apple logo.** A silver-grey laptop triggers FLUX's strong
   "Apple MacBook" association and it paints an Apple logo on the lid — a third-party
   trademark, unusable for a brand asset. Negation ("no logo") only works ~75 % of
   the time, and a "coral dot" just becomes a coral Apple. **Fix: make the laptop a
   matte DARK CHARCOAL laptop** — that breaks the Apple association at the source.

## Prompt (scene-first, dark-charcoal laptop — verified)

```
flat kawaii vector cartoon, bold clean dark outlines, matte fills, one soft cel-shading step.

Cute chibi cartoon sloth sits behind a small low wooden table, front view, centered, typing on an open laptop, three-clawed hands on the keyboard. Chunky matte DARK CHARCOAL-GREY laptop with plain blank lid. Small cream mug right of the table; two clawed feet peek out below. Happy focused expression.

Sloth has deep blue-indigo fur, large round head with small jagged tuft, heart-shaped cream face mask with two broad dark diagonal eye-stripes, cool silver-grey fur streak down one side of the head beside the mask, big round dark eyes with white highlights, small dark nose, closed smile, coral-orange blush cheeks. Whole body solid indigo.

Flat warm bone-white background, soft oval shadow. Fur #4A529D, mask #F4F1EA, cheeks #E8825A, streak #AEB2BE.
```

## Generation notes
- Run: `image_generate.py --provider cloudflare --prompt-file <f> --seed <n> --out design/assets/<name>.jpg`
- **Verified-good seeds** (logo-free, on-composition): `9121`, `9122` (these used a
  silver laptop), and the dark-charcoal prompt clears even the stubborn Apple seeds
  (`9123` came out fully logo-free).
- Generate 2–4 seeds and keep the cleanest. If any render still shows an Apple shape,
  re-roll the seed — it is seed-specific, not a wording problem.
- Want the silver-laptop look of the original? Swap "matte DARK CHARCOAL-GREY laptop …
  not a silver metal laptop" for "silver-grey laptop with a plain blank lid", but
  expect ~1 in 4 seeds to paint an Apple logo — discard those.

## Avoidance (positive assertions — FLUX has no negative prompt)
Encode every exclusion as what the image *is*: the laptop screen is a **plain soft
glow** (an empty light surface, free of code, lettering, or numerals) and the lid is
a **completely blank surface** (an unbranded, generic device — any seed that paints
a fruit or other mark on it is discarded); the artwork carries **no lettering or
watermark anywhere**; the fur reads **blue-indigo throughout** (never a natural
brown/tan/beige coat) with the **cream confined to the face mask** (the chest and
belly stay solid indigo); the anatomy is **exactly the canonical figure** (three
claws per hand and foot); the rendering is **flat vector-style with solid matte
fills**; every hue comes from the brand vocabulary (indigo/cream/amber/moss family
only).

## Post-processing checklist
- [ ] Remove the flat background → transparency via `png-to-transparent-svg`
- [ ] Confirm the laptop lid carries no logo or trademark
- [ ] Confirm fur reads blue-indigo and the face mask + eye-stripes survived
- [ ] Confirm the cool silver-grey side streak is present on one side and reads grey, not cream
- [ ] If the screen is visible, confirm it shows no text
