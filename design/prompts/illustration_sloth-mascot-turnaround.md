# Graphic Prompt: Sloth Mascot — Turnaround & Pose Model Sheet

> **Type:** illustration (model sheet)
> **Generator:** cloudflare flux-1-schnell
> **Variants:** Light (default) — dark-mode swaps per `illustration_sloth-mascot.md`
> **Target size:** 1024×1024px per view
> **Style reference:** `BRAND-STYLE-REF v1.1`, anchored by `design/brand/mascot/mascot-front-light.svg` (see `../brand/brand-vocabulary.md` §Canonical style reference); the per-view CHARACTER blocks below carry it as text
> **Seed:** pass an explicit `--seed` (Cloudflare honours it; the sidecar mis-logs it as None)

## Context
This sheet generates the mascot from **any angle** and in **any pose** while keeping
the same recognizable character: deep blue-indigo fur, heart-shaped cream face mask,
two diagonal eye-stripes, jagged head tuft, the cool silver-grey signature side streak,
coral cheeks, three cream claws per limb.

**Signature streak across views.** The mascot has one cool silver-grey fur streak down
one side of the head (the "grey lock"). FLUX won't reliably honour a left/right
instruction, so each view below asks for the streak on the **visible** side of the head;
pick the renders where it lands on a consistent side and treat that as canonical for the
set (per the cross-asset note in `_index.md`). In the strict back view the streak belongs
to the head's side and stays mostly hidden — keep the back clean.

## How to use this sheet (important — learned from test renders)

FLUX.1-schnell **does not obey a camera instruction appended as a "VIEW:" line** — if
the description reads as a front-facing character, every render comes out front-facing.
Each view therefore has its **own complete prompt** below, where the body text itself
describes the angle and (for side/back) explicitly hides the face. Front, side and back
are **verified working**; the three-quarter angles are **experimental** — FLUX often
snaps them back to front, so generate a few seeds and keep the ones that turned.

**Negations are weak in FLUX.1-schnell.** "No cream patch on the back" alone won't stop
a bad seed from painting a pale patch onto the back — so the back block also gives a
*positive* centre detail (a faint darker-indigo seam) to occupy that space. Still,
generate 2–4 seeds per rear view and discard any that put a pale patch on the back.

Two recurring traps, both handled in the prompts below:
- **Colour drift to brown:** "sloth" pulls FLUX toward natural brown fur. Every prompt
  states the indigo fur positively, early in the colour description. If a render is brown, re-roll the seed —
  never weaken the colour wording.
- **Pose vs. view:** poses (wave, hang, sleep…) work best in the **front** or
  **three-quarter** blocks; side/back read most cleanly as a calm standing/sitting body.

---

## View 1 — Front (verified ✅, canonical)
Append a POSE phrase (see Poses) after "near-symmetrical." for variants.

```
modern flat-design kawaii vector cartoon, bold even-weight clean dark outlines, rounded geometric friendly shapes, smooth matte fills with a single soft cel-shading step, generous negative space, centered and isolated on a flat warm bone-white background.

a stylised chibi cartoon sloth plush-toy with DEEP BLUE-INDIGO fur, a desaturated blue-grey-violet. Front view, facing the viewer, near-symmetrical. Large round head, half the body height, with a small jagged fur tuft. A big heart-shaped cream face mask with a V-notch. Two broad dark navy-charcoal diagonal stripes cross each eye, pale between them. A cool silver-grey fur streak runs down one side of the head from the tuft past the cheek, beside the mask, the only asymmetry. Two large round near-black eyes with white highlights, a small dark nose, a thin closed smile, two coral-orange blush cheeks. Cream only on the face mask; chest, belly and sides are solid deep blue-indigo. Compact rounded body joined straight to the head, short arms, exactly three pale cream claws per hand and foot. Bold dark-indigo outline, soft-grey oval shadow beneath.

Fur deep blue-indigo #4A529D / observed slate #4A4E6B, mask warm bone white #F4F1EA, cheeks coral orange #E8825A, eyes near-black, side streak cool silver-grey #AEB2BE.
```

## View 2 — Side profile (verified ✅)

```
modern flat-design kawaii vector cartoon, bold even-weight clean dark outlines, rounded geometric friendly shapes, smooth matte fills with a single soft cel-shading step, generous negative space, centered and isolated on a flat warm bone-white background.

a stylised chibi cartoon sloth plush-toy in STRICT SIDE PROFILE facing left, in a gentle forward-leaning crouch, head low at the front, rounded back arching up toward the rear, as if ambling on all fours. Deep blue-indigo fur, a desaturated cool blue-violet. Cream ONLY as a small face mask on the snout and around the eye; the ENTIRE body, back, side, belly and rear, is solid deep blue-indigo. A cool silver-grey fur streak runs down the visible side of the head from the tuft past the cheek. One round near-black eye with a white highlight, a bold dark diagonal stripe back from the eye, a short snout pointing left, a small closed smile, a small jagged head tuft. The near front leg reaches the ground showing three pale cream claws. Bold dark-indigo outline, resting on the ground over a soft-grey oval shadow. Strict profile.

Fur deep blue-indigo #4A529D / observed slate #4A4E6B. Cream warm bone white #F4F1EA ONLY on the face mask.
```

## View 3 — Back (verified ✅)

```
modern flat-design kawaii vector cartoon, bold even-weight clean dark outlines, rounded geometric friendly shapes, smooth matte fills with a single soft cel-shading step, generous negative space, centered and isolated on a flat warm bone-white background.

a stylised chibi cartoon sloth plush-toy seen STRICTLY FROM BEHIND, the camera directly behind it, facing away. We see only its back, covered ENTIRELY in solid deep blue-indigo fur, a desaturated cool blue-violet indigo. The whole back and the back of the head form one continuous uniformly indigo surface whose only marking is a faint soft vertical seam of slightly darker indigo down the middle. The face, cream mask, eyes, nose and mouth all sit on the hidden front side. The back of the round head carries a small jagged indigo tuft, two short arms rest at the sides, and only the tips of three pale cream claws peek out at each side. The cool silver-grey head streak stays on the side of the head, at most a faint sliver at one edge. Bold dark-indigo outline. The character rests flat on the ground with a small soft-grey oval shadow touching its base. Rear view only.

Fur deep blue-indigo #4A529D / observed slate #4A4E6B.
```

## View 4 — Three-quarter front (experimental ⚠️ — re-roll seeds)

```
modern flat-design kawaii vector cartoon, bold even-weight clean dark outlines, rounded geometric friendly shapes, smooth matte fills with a single soft cel-shading step, generous negative space, centered and isolated on a flat warm bone-white background.

a stylised chibi cartoon sloth plush-toy seen from a THREE-QUARTER FRONT angle, the head and body turned about 35 degrees to the left so we see mostly the front plus one side of the head and body. Deep blue-indigo fur, a desaturated cool blue-violet throughout. The heart-shaped cream face mask and the two navy diagonal eye-stripes are visible but foreshortened, the far eye smaller than the near eye, the snout angled to one side. A single cool silver-grey streak of fur runs down the near side of the head from the tuft past the cheek, a grey lock. Small jagged indigo tuft on top, two coral-orange cheeks, near-black eyes, three pale cream claws per limb. Compact rounded body, bold dark-indigo outline, soft-grey oval shadow beneath. Turned three-quarter view with foreshortened, uneven sides.

Fur deep blue-indigo #4A529D / observed slate #4A4E6B, mask warm bone white #F4F1EA, cheeks coral orange #E8825A.
```

## View 5 — Three-quarter back (experimental ⚠️ — re-roll seeds)

```
modern flat-design kawaii vector cartoon, bold even-weight clean dark outlines, rounded geometric friendly shapes, smooth matte fills with a single soft cel-shading step, generous negative space, centered and isolated on a flat warm bone-white background.

a stylised chibi cartoon sloth plush-toy seen from a THREE-QUARTER BACK angle, from behind and slightly to the left. Mostly we see its rounded back and the back of its round head with the small jagged tuft; the back is uniformly solid deep blue-indigo right across its centre, and only a thin sliver of the cream face-mask edge shows on the far side where the face turns away. Deep blue-indigo fur, a desaturated cool blue-violet throughout. A faint sliver of the cool silver-grey head streak may show on the near side of the head where it turns away; the rest of the back stays solid indigo. Short arms at the sides, three pale cream claws per limb. Bold dark-indigo outline, the character resting flat on the ground with a soft-grey oval shadow touching its base. Rear three-quarter view, face mostly hidden.

Fur deep blue-indigo #4A529D / observed slate #4A4E6B, mask warm bone white #F4F1EA.
```

---

## Poses (append to the **Front** or **3/4-front** block, after the view sentence)

FLUX renders poses most reliably from the front / three-quarter-front angle. Insert one
phrase right after "facing the viewer, near-symmetrical." (front) and adjust as needed.

| Pose | Phrase to insert |
| ---- | ---------------- |
| **Sitting (canonical)** | `sitting upright, calm friendly content expression.` |
| **Standing** | `standing upright on two short legs, arms relaxed at the sides.` |
| **Waving** | `sitting upright, one short arm raised in a friendly wave, gentle smile.` |
| **Thumbs-up** | `sitting upright, one arm raised giving a thumbs-up, cheerful closed-eye smile.` |
| **Hanging** | `hanging by both arms from a short horizontal branch, body dangling relaxed, sleepy expression.` |
| **Climbing** | `climbing, both arms reaching upward to grip a vertical branch, looking up.` |
| **Sleeping** | `curled up asleep, eyes closed as two soft downward curved lines, head resting on the arms.` |
| **Lying / relaxed** | `lying on its belly, chin propped on both hands, feet up behind, relaxed expression.` |

## Generation notes
- Save a composed prompt to a file and run:
  `image_generate.py --provider cloudflare --prompt-file <f> --seed <n> --out design/assets/<name>.jpg`
- Generate 2–4 seeds per view; keep the on-brand indigo ones that actually turned.
- `--seed` is honoured by Cloudflare (deterministic); the `.meta.json` sidecar mis-logs
  it as `None`, so track the seed via the filename.
- The per-view CHARACTER blocks above are the canonical reference — compare each
  render against them point by point (no external reference image is needed).

## Avoidance (positive assertions — FLUX has no negative prompt)
Encode every exclusion as what the image *is*: the artwork is **purely pictorial**
(shape-only meaning, free of lettering, numerals, third-party marks, or signatures);
the fur reads **blue-indigo throughout** (the brand's muted indigo, never a natural
brown/tan/beige animal coat); the rendering is **flat vector-style with smooth
stylised shapes and solid matte fills** (no photographic fur detail, gradients, or
glossy 3D); the background is a **single plain field**; the anatomy is **exactly the
canonical figure** (three claws per hand and foot, symmetric limbs); no distorted
or asymmetric face (front view) — the eyes, mask and stripes stay symmetric, the **only**
intended asymmetry is the single cool-grey side streak, which is grey (never cream) and
must never be mirrored onto both sides; **on back / rear views: no cream or pale patch on the
back or back of the head — the cream is on the face mask only and the body is fully indigo; the character rests
on the ground, never floating**; avoid teal-cyan, pure red, or neon.

## Post-processing checklist
- [ ] Remove the flat background → transparency via `png-to-transparent-svg`
- [ ] Confirm fur read as blue-indigo (reject brown drifts)
- [ ] Verify the three-claw + diagonal eye-stripe + head-tuft cues survived per view
- [ ] Confirm the silver-grey side streak is present (front/side/3-4), on a consistent
      side across kept renders, reads cool grey not cream, and is absent/clean on the back
- [ ] Keep a consistent register across the turnaround set
