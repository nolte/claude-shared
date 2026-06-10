# Graphic Prompt: Sloth Mascot Character

> **Type:** illustration
> **Generator (compiled for):** cloudflare flux-1-schnell
> **Variants:** Light + Dark
> **Target size:** 1024×1024px (master)
> **Format:** PNG (transparent) after post-processing
> **Authoring model:** canonical description below → compiled per `_compile-for-model.md`
> **Seed:** unset (fix after the reproducible seed round — see Consistency workflow)

## Context
The full character expression of the heraldic animal: a friendly, approachable
sloth mascot for hero images, onboarding, empty states, and social cards. It
carries the brand's personality — calm, clever, unhurried — and must share the
exact visual register of the logo emblem so the two read as one family.

This document has two layers per `_compile-for-model.md`: the **canonical description**
(model-agnostic, the source of truth — edit the figure here, reuse it for any AI) and
the **compiled prompt** (distilled for flux-1-schnell's limits, ready to send).

## Canonical description (model-agnostic)

The complete figure. Any generator or human can work from this; the compiled block is
derived from it. Keep these recognition anchors exact — word drift is character drift.

- Chibi cartoon **three-toed sloth**, sitting upright, facing the viewer,
  **near-symmetrical** — the figure reads symmetrical except for one deliberate break,
  the silver-grey side streak (below). Body roughly egg-shaped, a touch wider at the base.
- **Large round head about half the body height**, topped by a **small jagged tuft**
  of two or three short fur spikes (a cowlick).
- A single distinctive **cool silver-grey fur streak** — the mascot's signature
  "**grey lock**" — running down **one side of the head** (canonically the viewer's
  right), starting in the jagged tuft and tapering down past the temple and cheek toward
  the jaw. It lies on the indigo fur **beside** the cream mask and **never crosses onto
  it**; it is a **cool neutral silver-grey** (clearly cooler and greyer than the warm
  cream mask, so the two never read as one patch), about one-and-a-half fur-spikes wide
  at the top and narrowing to a point. This is the **only intentional asymmetry** of the
  figure and the strongest recognition cue after the diagonal eye-stripes.
- A big **heart-shaped cream warm-bone-white face mask** with a small V-notch at the
  top middle, enclosing both eyes, the nose and the mouth.
- **Two broad dark charcoal-indigo diagonal stripes** running from the top center of
  the mask outward and downward across each eye like an eye-mask, the bridge between
  the eyes left pale — the strongest recognition cue.
- Two large round **dark-brown eyes**, each with a single small white highlight dot at
  the upper right, sitting just below the stripes.
- A small rounded **dark-indigo nose** centered between the eyes; directly below it a
  thin dark gently-curved closed smile.
- **Two small round coral-orange blush patches**, one on each cheek.
- **Deep slate blue-indigo fur** (muted, desaturated indigo; `#5B5FC7` / slate
  `#4A4E6B`) with a single soft cel-shading step, slightly darker at the body sides.
  In **dark mode** the fur lightens to soft cobalt-violet (`#8E92E6`).
- **The cream is ONLY on the face mask. The whole body — chest, belly, back and
  sides — is solid indigo with NO belly patch.** The only cream areas besides the mask are
  the claws; the only other non-indigo marking anywhere is the cool silver-grey side
  streak on the head (which is grey, never cream — do not extend the cream into it).
- Compact rounded body, **no visible neck**, short arms resting at the sides.
- Two stubby feet at the front, each showing **exactly three** pale cream claws.
- **Bold even-weight dark-indigo outline** throughout (warm-bone outline in dark mode);
  a small flat soft-grey oval shadow directly beneath the body.
- Style: modern flat-design kawaii vector cartoon, matte fills, generous negative
  space, isolated on a flat warm bone-white background (deep warm charcoal `#20222A`
  in dark mode). Eyes near-black-brown `#3A2A22`, cheeks coral-orange `#E8825A`, signature
  side streak cool silver-grey `#AEB2BE` (light) / `#C9CDD6` (dark).

## Compiled — flux-1-schnell (≤256 tok, hex-free, anchors first)

> ⏳ Render-verification of these compiled blocks is pending (Cloudflare daily quota
> was exhausted during authoring). The long originals rendered correctly; these are
> the trimmed, truncation-safe equivalents.

**Light Mode**

```
A chibi cartoon three-toed sloth sitting upright facing the viewer, near-symmetrical, with deep blue-indigo plush fur (a blue-violet indigo, definitely NOT brown). A big heart-shaped cream face mask with a small V-notch holds two large round dark-brown eyes; two broad dark diagonal stripes cross over the eyes like a mask, pale between them. Small dark nose, a gentle closed smile, two round coral-orange blush cheeks, a small jagged head tuft on top. A single cool silver-grey streak of fur runs down one side of the head beside the mask, from the tuft past the cheek — a grey lock, the only asymmetry, grey not cream. The cream is only on the face — the whole body is solid indigo with no belly patch. Exactly three pale cream claws on each hand and foot. Bold even dark outline, smooth matte fills with soft cel-shading, flat warm bone-white background, soft oval shadow beneath. Modern flat kawaii vector cartoon style.
```

**Dark Mode**

```
A chibi cartoon three-toed sloth sitting upright facing the viewer, near-symmetrical, with soft cobalt-violet plush fur (a light blue-violet, definitely NOT brown), styled for dark mode. A big heart-shaped cream face mask with a small V-notch holds two large round dark-brown eyes; two broad dark diagonal stripes cross over the eyes like a mask, pale between them. Small dark nose, a gentle closed smile, two round coral-orange blush cheeks, a small jagged head tuft on top. A single pale silver-grey streak of fur runs down one side of the head beside the mask, from the tuft past the cheek — a grey lock, the only asymmetry, grey not cream. The cream is only on the face — the whole body is solid cobalt-violet with no belly patch. Exactly three pale cream claws on each hand and foot. Bold even warm-bone outline so it stays crisp, smooth matte fills with soft cel-shading, flat deep warm charcoal background, soft shadow beneath. Modern flat kawaii vector cartoon style.
```

## Pose variants (append after "near-symmetrical" in the Light prompt)

Already short; reuse the compiled Light prompt and insert one phrase.

- **Waving:** `one short arm raised in a friendly wave`
- **Portrait:** `as a head-and-shoulders portrait`
- **Sleeping:** `curled up asleep, eyes closed as two soft curved lines`
- **Optional brand prop:** `holding one small warm moss green leaf in one claw`
  (FLUX often drops small props — verify or add in post)

## Avoidance (positive assertions — FLUX has no negative prompt)
The compiled prompts already encode the key ones: fur is blue-indigo (not brown); the
body is solid indigo (no belly patch); face cream only; one cool-grey side streak (not
cream, not mirrored to both sides). Also avoid: embedded text, other companies' logos,
watermark, photorealism, 3D/gradients, a raised single eyebrow, **an asymmetric face**
(the eyes, mask and stripes stay symmetric — the *only* intended asymmetry is the grey
side streak), extra limbs or claws beyond three, teal-cyan / pure-red / neon.

## Consistency workflow
1. **Reproducible seed round:** render the Light prompt with explicit `--seed` values
   (Cloudflare doesn't return the seed when unset — a fixed seed is the only repeatable
   path; the `.meta.json` sidecar mis-logs it as None, so track it via the filename).
2. **Pick the one closest to the canonical description** and record its seed above.
3. **Generate the rest** (Dark, poses, scenes) with that seed for one consistent character.
4. Compare every render against the **Canonical description**, point by point.

## Post-processing checklist
- [ ] Remove the flat background → real transparency via `png-to-transparent-svg`
- [ ] Confirm body is fully indigo with no stray belly patch; fur reads blue-indigo
- [ ] Verify the three-claws + diagonal eye-stripe cues survived
- [ ] Confirm the cool silver-grey side streak is present on **one** side only, reads as
      cool grey (not warm cream), sits beside the mask, and is the only asymmetry
- [ ] Keep typography / wordmark as a separate overlay — never rendered here
