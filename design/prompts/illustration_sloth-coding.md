# Graphic Prompt: Sloth Mascot — Coding at a Laptop (scene)

> **Type:** illustration (scene)
> **Generator:** cloudflare flux-1-schnell
> **Variants:** Light (default)
> **Target size:** 1024×1024px
> **Style reference:** the prompt below — self-contained, no external image needed
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
modern flat-design kawaii vector cartoon, bold clean dark outlines, smooth matte fills with a single soft cel-shading step, simple flat shapes.

A cute chibi cartoon sloth sitting on the floor behind a small low wooden table, viewed from the front and centered, typing on an open laptop that stands on the table. The sloth leans forward and rests both small three-clawed hands on the laptop keyboard. The laptop is a chunky matte DARK CHARCOAL-GREY laptop with a plain smooth lid and rounded corners — a generic dark laptop, definitely not a silver metal laptop, with no logo, no apple, no emblem and no text on it. A small cream mug sits on the floor to the right of the table. The sloth's two clawed feet peek out below the table. Happy focused expression.

The sloth has DEEP BLUE-INDIGO fur (a blue-violet indigo, NOT brown), a large round head with a small jagged head tuft, a heart-shaped cream face mask with two broad dark diagonal eye-stripes, a single cool silver-grey streak of fur running down one side of the head beside the mask (a grey lock, cool grey not cream, the only asymmetry), two big round dark eyes with small white highlights, a small dark nose, a gentle closed smile, two coral-orange blush cheeks. Its body is solid indigo with no belly patch.

Flat warm bone-white background, a soft oval shadow under the whole scene. Fur indigo #4A529D / observed slate #4A4E6B (NOT brown), cream face mask #F4F1EA, coral cheeks #E8825A, signature side streak cool silver-grey #AEB2BE, dark charcoal laptop, warm wood-brown table.
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
