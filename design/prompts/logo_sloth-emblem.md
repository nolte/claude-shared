# Graphic Prompt: Sloth Heraldic Emblem (Logo Mark)

> **Type:** logo
> **Generator:** cloudflare flux-1-schnell
> **Variants:** Light + Dark
> **Target size:** 1024×1024px (master); must read at 32×32px favicon
> **Format:** PNG (transparent) after post-processing
> **Style reference:** BRAND-STYLE-REF v0 (bootstrap) — canonical style paragraph, see below
> **Seed:** unset

## Context
The portfolio's primary mark: a compact, geometric sloth emblem used as the
heraldic animal across favicons, app icons, README badges, and the docs header.
It must read instantly at small sizes and feel modern, friendly, and unmistakably
the same brand as the mascot illustration.

## Prompt — Light Mode
```
BRAND-STYLE-REF v0 (bootstrap): modern flat-design comic / vector cartoon, bold even-weight clean outlines, rounded geometric friendly shapes, smooth matte fills with a single soft cel-shading step, generous negative space, subject centered and isolated on a plain flat background, designed to stay legible at small sizes.

A minimalist geometric emblem of a cute sloth hanging from a short horizontal branch, front-facing, simplified to a few bold rounded shapes that form a clean badge-like mark. Dominant body color muted indigo, branch and a single leaf in warm moss green, eyes and claws picked out in warm amber, cream warm-bone-white face mask. Thick uniform indigo outline. Symmetrical, iconic, balanced, lots of padding around the mark. Flat warm bone-white background.

Brand color reinforcement: muted indigo #5B5FC7, warm moss green #4F9D69, warm amber #E0A23C, warm bone white #F4F1EA. Seed: unset.
```

## Prompt — Dark Mode
```
BRAND-STYLE-REF v0 (bootstrap): modern flat-design comic / vector cartoon, bold even-weight clean outlines, rounded geometric friendly shapes, smooth matte fills with a single soft cel-shading step, generous negative space, subject centered and isolated on a plain flat background, designed to stay legible at small sizes.

A minimalist geometric emblem of a cute sloth hanging from a short horizontal branch, front-facing, simplified to a few bold rounded shapes that form a clean badge-like mark. Dominant body color soft cobalt-violet, branch and a single leaf in soft fern green, eyes and claws picked out in warm amber, cream warm-bone-white face mask. Thick uniform warm-bone outline so the mark stays crisp on a dark surface. Symmetrical, iconic, balanced, lots of padding around the mark. Flat deep warm charcoal background.

Brand color reinforcement: soft cobalt-violet #8E92E6, soft fern green #6FBF8A, warm amber #E0A23C, deep warm charcoal #20222A. Seed: unset.
```

## Avoidance clause
No embedded text, letters, or numbers; no other companies' logos or trademarks;
no watermark or signature; no photorealism or detailed fur texture; no harsh
gradients or glossy 3D rendering; no busy or cluttered background; no extra limbs
or distorted anatomy; avoid off-brand colors (no teal-cyan, no pure red, no neon).

## Post-processing checklist
- [ ] Remove the flat background → real transparency via `png-to-transparent-svg`
- [ ] Scale-check at 192×192, 48×48, and 32×32; simplify claws/leaf if they muddy
- [ ] Verify it reads as one silhouette (squint test) — the heraldic-animal payload
- [ ] Pair with the wordmark typography as a separate overlay — never rendered here
- [ ] If approved, promote this render to `BRAND-STYLE-REF v1` (fixed reference image)
