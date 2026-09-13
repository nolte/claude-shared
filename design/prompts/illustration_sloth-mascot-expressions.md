# Graphic Prompt: Sloth Mascot — Expression Sheet (Mimik)

> **Type:** illustration (expression sheet)
> **Generator:** cloudflare flux-1-schnell
> **Variants:** Light (default) — dark-mode swaps per `illustration_sloth-mascot.md`
> **Target size:** 1024×1024px per expression
> **Style reference:** `BRAND-STYLE-REF v1.1`, anchored by `design/brand/mascot/mascot-front-light.svg` (see `../brand/brand-vocabulary.md` §Canonical style reference); the HEAD + TAIL blocks below carry it as text
> **Seed:** pass an explicit `--seed`; keep one seed across a set for body consistency

## Context
Defines the mascot's facial expressions (Mimik) for use across the portfolio's UI and
content states. The body, mask, eye-stripes, head tuft, the cool silver-grey side streak,
indigo fur and three claws stay invariant; only the **eyes, mouth, brows and blush**
change per expression. Compose: `STYLE + HEAD block + EXPRESSION slot + TAIL block + COLOR LOCK`.

## Fixed blocks (verbatim)

**STYLE:**

```
modern flat-design kawaii vector cartoon, bold even-weight clean dark outlines, rounded geometric friendly shapes, smooth matte fills with a single soft cel-shading step, generous negative space, centered and isolated on a flat warm bone-white background.
```

**HEAD (invariant identity, up to the face):**

```
a chibi cartoon sloth plush-toy with DEEP BLUE-INDIGO fur, a cool blue-violet indigo. Front view, near-symmetrical. Large round head with a small jagged fur tuft. A big heart-shaped cream face mask with a V-notch. Two broad dark navy-charcoal diagonal stripes cross each eye, pale between them, a small dark nose. A cool silver-grey fur streak runs down one side of the head from the tuft past the cheek, beside the mask.
```

**TAIL (invariant body):**

```
Cream only on the face mask; the whole body solid deep blue-indigo. Compact rounded body right under the head, short arms, exactly three pale cream claws per hand and foot. Bold dark-indigo outline, soft-grey oval shadow beneath.
```

**COLOR LOCK:**

```
Fur deep blue-indigo #4A529D / observed slate #4A4E6B, mask warm bone white #F4F1EA, cheeks coral orange #E8825A, eyes near-black, side streak cool silver-grey #AEB2BE.
```

## Expressions (insert one slot between HEAD and TAIL)

| Expression | EXPRESSION slot (insert verbatim) | UI / content state |
| ---------- | --------------------------------- | ------------------ |
| **Content** (canonical) | `Two large round near-black eyes each with a small white highlight, a thin gently-curved closed smile, two small coral-orange blush patches, a calm content expression.` | Idle / default |
| **Happy** ✅ | `Two large shiny near-black eyes, a wide open cheerful smile, two coral-orange blush patches, a bright happy expression.` | Success / done |
| **Excited** ⚠️ | `Two big sparkling near-black eyes each with several small white star-like highlights, a wide open beaming smile, happy raised brows, bigger coral-orange blush patches, a delighted excited expression.` | Big win / celebration |
| **Sleepy** ✅ | `Two half-closed droopy eyes with the eyelids lowered halfway, a tiny relaxed smile, soft coral-orange blush, a calm drowsy sleepy expression.` | Loading / waiting |
| **Sleeping** ✅ | `Head tilted gently to one side, both eyes fully closed as two soft downward curved lines, a small peaceful content smile, soft coral-orange blush, a calm sleeping expression.` | Sleep / offline |
| **Surprised** ⚠️ | `Two very large wide-open near-black eyes, high raised brows, a small round open o-shaped mouth, a surprised wow expression.` | New / notification |
| **Curious** ✅ | `Head tilted slightly to one side, one eye slightly narrowed and the other round, a small thoughtful closed mouth, one short arm raised with a claw near the chin, a curious thinking expression.` | Thinking / processing |
| **Winking** ✅ | `One eye open and round with a highlight, the other eye closed as a downward curved line in a wink, a playful smile, coral-orange blush, a cheeky expression.` | Tip / playful hint |
| **Sad** ✅ | `Two large glossy near-black eyes, brows angled up toward the middle in worry, a small downturned frown, a sad downcast expression.` | Error / failure |
| **Embarrassed** ✅ | `Two eyes glancing to the side, large bright coral-orange blush across both cheeks, a small bashful awkward smile, an embarrassed shy expression.` | Oops / apology |
| **Proud** ✅ | `Two eyes closed as upward happy curves, a wide satisfied grin, head tilted slightly up, coral-orange blush, a proud content expression.` | Achievement / streak |
| **Love** ✅ | `Two eyes each shaped like a small coral-pink heart, a sweet adoring open smile, big coral-orange blush patches, a loving adoring expression.` | Like / favorite |

✅ = verified working · ⚠️ = harder for FLUX, generate a few seeds and keep the best

**Surprised note:** FLUX.1-schnell won't render an open "O"/gasp mouth — it keeps the
smile. The best approximation is the wide-round-eyes + raised-brows variant
(the wide-round-eyes + raised-brows variant); accept it or add the open mouth in post.

## Worked example (Happy)

```
modern flat-design kawaii vector cartoon, bold even-weight clean dark outlines, rounded geometric friendly shapes, smooth matte fills with a single soft cel-shading step, generous negative space, centered and isolated on a flat warm bone-white background.

a chibi cartoon sloth plush-toy with DEEP BLUE-INDIGO fur, a cool blue-violet indigo. Front view, near-symmetrical. Large round head with a small jagged fur tuft. A big heart-shaped cream face mask with a V-notch. Two broad dark navy-charcoal diagonal stripes cross each eye, pale between them, a small dark nose. A cool silver-grey fur streak runs down one side of the head from the tuft past the cheek, beside the mask. Two large shiny near-black eyes, a wide open cheerful smile, two coral-orange blush patches, a bright happy expression. Cream only on the face mask; the whole body solid deep blue-indigo. Compact rounded body right under the head, short arms, exactly three pale cream claws per hand and foot. Bold dark-indigo outline, soft-grey oval shadow beneath.

Fur deep blue-indigo #4A529D / observed slate #4A4E6B, mask warm bone white #F4F1EA, cheeks coral orange #E8825A, eyes near-black, side streak cool silver-grey #AEB2BE.
```

## Generation notes
- Save a composed prompt to a file and run:
  `image_generate.py --provider cloudflare --prompt-file <f> --seed <n> --out design/assets/<name>.jpg`
- Keep ONE seed across an expression set so the body/pose stays constant and only the
  face changes — that reads as a true expression sheet.
- Star-eyes, heart-eyes and winks are the least reliable (FLUX simplifies them); re-roll.
- Verify fur stays blue-indigo; re-roll any brown drift.

## Avoidance (positive assertions — FLUX has no negative prompt)
Encode every exclusion as what the image *is*: every panel is **purely pictorial**
(a dream bubble stays an empty shape; all surfaces free of lettering, marks, or
watermarks); the fur reads **blue-indigo throughout** (never a natural brown/tan/
beige coat); the rendering is **flat vector-style with solid matte fills** (stylised
rather than photographic, flat rather than gradient or 3D); the background is a
**single plain field**; the anatomy is **exactly the canonical figure** (three claws
per hand and foot); every hue comes from the brand vocabulary (indigo/cream/amber/
moss family only).

## Post-processing checklist
- [ ] Remove the flat background → transparency via `png-to-transparent-svg`
- [ ] Confirm fur read as blue-indigo
- [ ] Verify mask + eye-stripe + head-tuft cues survived in every expression
- [ ] Confirm the silver-grey side streak survived on a consistent side, reads cool grey
      (not cream), and is never mirrored to both sides
- [ ] Keep one seed across the set for body consistency
