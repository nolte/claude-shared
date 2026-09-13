# Graphic Prompt: Sloth Heraldic Emblem (Logo Mark)

> **Type:** logo
> **Generator:** cloudflare flux-1-schnell
> **Variants:** Light + Dark
> **Target size:** 1024×1024px (master); must read at 32×32px favicon
> **Format:** PNG (transparent) after post-processing
> **Style reference:** BRAND-STYLE-REF v1.1 — canonical style paragraph, see below. The prompt blocks keep the paragraph's original `BRAND-STYLE-REF v0 (bootstrap):` label verbatim, because that label is part of the text the committed v1.1 renders were generated from; the paragraph content is the v1.1 one
> **Seed:** **light 8521 · dark 8505** (canonical v1.1 — the matched "hanging from a horizontal branch" pair)

## Context
The portfolio's primary mark: a compact, geometric sloth emblem used as the
heraldic animal across favicons, app icons, README badges, and the docs header.
It must read instantly at small sizes and feel modern, friendly, and unmistakably
the same brand as the mascot illustration.

## Prompt — Light Mode

```
BRAND-STYLE-REF v0 (bootstrap): modern flat-design comic vector cartoon, bold even-weight clean outlines, rounded geometric friendly shapes, smooth matte fills with one soft cel-shading step, generous negative space, centered and isolated on a plain flat background, designed to stay legible at small sizes.

Minimalist geometric emblem of a cute sloth hanging from a short horizontal branch, front-facing, bold rounded shapes forming a clean badge-like mark. Muted indigo body, moss green branch and leaf, warm amber eyes and claws, cream face mask, one short cool silver-grey signature streak on one side of the head. Thick indigo outline. Iconic, balanced, near-symmetrical apart from the streak. Flat warm bone-white background.

Brand color reinforcement: indigo #4A529D, moss #769244, amber #E0A23C, bone #F4F1EA, streak #AEB2BE. Seed: unset.
```

## Prompt — Dark Mode

```
BRAND-STYLE-REF v0 (bootstrap): modern flat-design comic vector cartoon, bold even-weight clean outlines, rounded geometric friendly shapes, smooth matte fills with one soft cel-shading step, generous negative space, centered and isolated on a plain flat background, designed to stay legible at small sizes.

Minimalist geometric emblem of a cute sloth hanging from a short horizontal branch, front-facing, bold rounded shapes forming a clean badge-like mark. Soft cobalt-violet body, fern green branch and leaf, warm amber eyes and claws, cream face mask, one short pale silver-grey signature streak on one side of the head. Thick warm-bone outline, crisp on dark. Iconic, balanced, near-symmetrical apart from the streak. Flat deep warm charcoal background.

Brand color reinforcement: violet #939FE3, fern #95B06A, amber #E0A23C, streak #C9CDD6, charcoal #20222A. Seed: unset.
```

## Rendered v1.1 asset (committed)

The emblem ships as transparent SVG vectors:

- `../brand/logo/logo-emblem-light.svg` and `../brand/logo/logo-emblem-dark.svg`
  (the matched "hanging from a horizontal branch" pair).

Reproduction:

1. Render the Light/Dark prompt block above with a **plain solid pure-white** (light) /
   **deep warm charcoal** (dark) background and `no shadow, no ground plane` for a clean
   cutout, at seed **8521** (light) / **8505** (dark).
2. Vectorise with the committed pipeline `../brand/vectorize.py` at threshold **60**
   (light) / **18** (dark — the lower value keeps the charcoal flood from leaking into
   the dark figure and fragmenting it).

At a ≤32 px favicon the silver-grey streak and the branch/leaf collapse to a few pixels;
that is expected — the emblem is designed to still read as a dark sloth silhouette there.

## Avoidance (positive assertions — FLUX has no negative prompt)
Encode every exclusion as what the image *is*: the emblem is **purely pictorial**
(all meaning carried by shape alone, free of any lettering, numerals, or marks);
it is an **original heraldic figure** owing nothing to any existing logo and
carrying a clean, unsigned surface; the rendering is **flat vector-style with
crisp matte fills** (stylised smooth shapes rather than photographic fur, solid
color fields rather than gradients or glossy 3D); the background is a **single
plain field** so the silhouette stands alone; the anatomy is **exactly the
canonical figure** (two arms, two legs, three claws each); every color comes
from the brand vocabulary (indigo/cream/amber family throughout).

## Post-processing checklist
- [ ] Remove the flat background → real transparency via `png-to-transparent-svg`
- [ ] Scale-check at 192×192, 48×48, and 32×32; simplify claws/leaf if they muddy
- [ ] Signature streak: keep it at master/large sizes; at ≤32 px favicon, simplify it to
      a single short grey notch in the tuft or drop it if it muddies the silhouette
- [ ] Verify it reads as one silhouette (squint test) — the heraldic-animal payload
- [ ] Pair with the wordmark typography as a separate overlay — never rendered here
- [x] Fixed reference image designated (2026-07-25, #494): `design/brand/mascot/mascot-front-light.svg` anchors `BRAND-STYLE-REF` — see `../brand/brand-vocabulary.md` §Canonical style reference
