# Brand Prompt Library

> **Status:** v1 — created 2026-07-25 (2026-Q3 audit, #494), backfilling one row per
> *published* hero image from the per-asset `.meta.json` sidecars and the prompt
> documents under `../prompts/`. Governed by `spec/design/corporate-design-colors/`
> §AI image color contract, which requires a versioned ledger recording the full
> prompt stack for every published hero image. Add a row in the same change that
> publishes a new asset; never delete rows (supersede with a note instead).

Column notes: the **prompt stack** is resolved by reading the named prompt document
at the named variant — the documents carry the full compiled prompt text, the
CHARACTER block, and the per-mode color phrases, so this ledger stays a pointer, not
a copy that could drift. **Style reference** names the `BRAND-STYLE-REF` version in
force at render time (see `brand-vocabulary.md` §Canonical style reference).
Descriptive phrases / hex reinforcements are the brand-vocabulary rows the variant
compiles in.

| Published asset | Model + version | Style reference | Seed | Prompt stack (document · variant) | Descriptive phrases → hex reinforcement | Post-processing |
| --- | --- | --- | --- | --- | --- | --- |
| `design/brand/mascot/mascot-front-light.svg` | Cloudflare `@cf/black-forest-labs/flux-1-schnell` | BRAND-STYLE-REF v1.0 (textual; renders predate the v1.1 grey streak and are re-render-pending) | 8505 | `design/prompts/illustration_sloth-mascot.md` · Compiled Light Mode (vector-master cutout variant) | "muted indigo", "warm bone white", "warm amber" → `#4A529D`* / `#F4F1EA` / `#E0A23C` | `vectorize.py`, threshold 60; committed 2026-06-11 |
| `design/brand/mascot/mascot-front-dark.svg` | Cloudflare `@cf/black-forest-labs/flux-1-schnell` | BRAND-STYLE-REF v1.0 (textual; re-render-pending as above) | 8505 | `design/prompts/illustration_sloth-mascot.md` · Compiled Dark Mode (vector-master cutout variant) | "soft cobalt-violet", "deep warm charcoal", "warm amber" → `#939FE3`* / `#20222A` / `#E0A23C` | `vectorize.py`, threshold 18; committed 2026-06-11 |
| `design/brand/logo/logo-emblem-light.svg` | Cloudflare `@cf/black-forest-labs/flux-1-schnell` | BRAND-STYLE-REF v1.0 (textual) | 8521 | `design/prompts/logo_sloth-emblem.md` · Light Mode | "muted indigo", "warm bone white" → `#4A529D`* / `#F4F1EA` | `vectorize.py`, threshold 60; committed 2026-06-11 |
| `design/brand/logo/logo-emblem-dark.svg` | Cloudflare `@cf/black-forest-labs/flux-1-schnell` | BRAND-STYLE-REF v1.0 (textual) | 8505 | `design/prompts/logo_sloth-emblem.md` · Dark Mode | "soft cobalt-violet", "deep warm charcoal" → `#939FE3`* / `#20222A` | `vectorize.py`, threshold 18; committed 2026-06-11 |

\* The four renders above were generated against the **bootstrap** palette
(`brand-primary` `#5B5FC7` / dark `#8E92E6`) that predates the 2026-06-06 canonical
decision; the hex column shows today's canonical reinforcement values so a re-render
lands on-token. The observed v1 fur (`~#4A4E6B`) already sits close to the decided
`#4A529D` (see `brand-vocabulary.md` §Canonical style reference, observed render
note). All four assets remain **re-render-pending** for the v1.1 grey streak; when
re-rendered, supersede these rows rather than editing them.

## Licensing / provenance

All four assets: `source: ai-generated-then-vectorised`, provider Cloudflare
Workers AI, output license Apache-2.0, vectorised by `design/brand/vectorize.py`.
The authoritative machine-readable provenance is each asset's `.meta.json` sidecar;
this ledger adds the prompt-stack view the sidecars don't carry.
