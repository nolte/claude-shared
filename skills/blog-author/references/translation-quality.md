# Translation quality: calque avoidance and the adversarial naturalness pass

Detail moved from `SKILL.md` Step 4 (write the DE draft) and Step 5 (per-pair self-check). Load this file when composing or self-checking the German draft.

## Native re-expression, not clause-by-clause translation (Step 4)

Compose each German paragraph from the EN paragraph's *meaning*, as a German author would write it from scratch. Never map EN sentence structure onto German word-for-word — that is exactly what produces calques, the failure class the D6 dimension in `spec/project/lektorat/` detects. Example calque to avoid: „Was die Kosten kaufen, ist Eigentum." mirroring „What the costs buy is ownership."

Typography and idiom rules (from §Bilingual typography in `post-writing-style`):

- German quotes `„…"`, em-dash with spaces, no ASCII substitutes for `ä/ö/ü/ß`, technical identifiers byte-identical.
- Idiom-for-idiom, not word-for-word — replace an EN idiom with a German equivalent or rewrite the sentence, never render it literally; no calque.
- Host-language gender for loanwords — „die Bridge", not „das Bridge".

After each section, re-read the German **with the English covered** and rewrite any sentence whose word order or collocation still echoes the English.

## Adversarial naturalness pass (Step 5)

Read the DE body as a skeptical German native speaker who *assumes it was machine-translated*, and hunt for the D6 tells:

- calques,
- loanword-gender slips (for example „das Bridge" for „die Bridge"),
- unidiomatic collocations,
- awkward `-bar` coinages,
- literally-rendered idioms.

Rewrite every tell into idiomatic German.

For any passage you remain unsure about, **optionally back-translate it to English and diff against the canonical EN body** — a large semantic divergence flags either a calque or a content drift. This EN↔DE comparison legitimately lives here (and only here), because the downstream lektor's D6 dimension is monolingual and will not perform it.

This self-pass is **prevention, not the gate**: the independent detection gate is the D6 dimension of the `lektorat-apply` audit at Step 7.
