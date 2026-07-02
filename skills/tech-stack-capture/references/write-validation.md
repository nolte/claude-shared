# Step 8 local validation checklist

The pre-write validation checklist referenced from `SKILL.md` §Operations step 8 (Compose and write). Run every check against the composed `tech_stack:` block before writing `project/portfolio.yml`; reject or block the write on any failure and surface the offending entry.

- Every `additions[]` entry carries the five mandatory fields (`name`, `kind`, `group`, `role`, `status`); reject malformed entries with the missing-field name surfaced.
- No `additions[]` entry shadows an inherited entry without a corresponding `overrides:` record on the same `name`. Shadow-without-override is a `Critical` per the schema spec — block the write.
- Every `overrides[]` record has a non-empty `rationale` and `inherit: false`.
- Every `regroup[]` record carries a `group` distinct from the inherited entry's `group` and a non-empty `rationale`, and isn't paired with an `overrides[]` record on the same `name`.
- All `kind:` values are within the closed 12-value enum; all `group:` values are within the closed 5-value enum; all `status:` values are within `active` / `experimental` / `deprecated`; all `lifecycle:` values (when present) are within `development` / `build` / `runtime` / `all`.

These checks reproduce the schema-spec MUSTs in `spec/portfolio/tech-stack/<canonical_language>.md`; when this file disagrees with the spec, the spec wins.
