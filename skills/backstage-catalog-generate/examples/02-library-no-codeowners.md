# Scenario 02 — Python library with no CODEOWNERS

## Input prompt

"Onboard this repo into Backstage."

## Repo fixture (signals)

- `pyproject.toml` with `name = "acme-retry"`, no web framework → structure = library
- `git remote origin` → `https://github.com/acme/acme-retry.git`
- **no** `CODEOWNERS`, **no** API definition files, **no** colocated docs
- repo name slug would be `acme-retry` (already valid)

## Expected behaviour

- Emits a single `Component` at the repo root:
  - `apiVersion: backstage.io/v1alpha1`, `kind: Component`, `metadata.name: acme-retry`
  - `spec.type: library` *inferred*, `spec.lifecycle` **needs-confirm**, `spec.owner` **needs-confirm**
- Because there is no CODEOWNERS, the skill **does not invent an owner** — it flags `spec.owner` as operator-action-required (a Component without a resolvable owner is incomplete) rather than emitting a dangling reference.
- Annotations: `github.com/project-slug: acme/acme-retry`, `backstage.io/source-location: url:https://github.com/acme/acme-retry/`. No `techdocs-ref` (no colocated docs).
- No `providesApis` (no API definitions found); no guessed `system`/`dependsOn`.
- Report clearly separates the one *inferred* field (`type`) from the two *needs-confirm* fields (`lifecycle`, `owner`).
