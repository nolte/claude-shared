# Operations — yaml-json-schema

Detailed step-by-step procedures for each operation. Loaded on demand when executing any operation.

## Table of Contents

1. [Operation 1: Author a new schema](#1-author-a-new-schema-slug-v10schemayaml)
2. [Operation 2: Audit existing schemas](#2-audit-existing-schemas)
3. [Operation 3: Refactor (apply audit findings)](#3-refactor-apply-audit-findings)
4. [Operation 4: Meta-validation (schema-against-meta-schema)](#4-meta-validation-schema-against-meta-schema)
5. [Operation 5: Data validation (data-against-schema)](#5-data-validation-data-against-schema)
6. [Operation 6: Lifecycle bump (revise an existing schema)](#6-lifecycle-bump-revise-an-existing-schema)
7. [Operation 7: Re-audit](#7-re-audit)

---

## 1. Author a new schema (`<slug>-v1.0.schema.yaml`)

Bootstrap a brand-new schema in the repository.

1. Ask for: the **slug** (kebab-case, no version suffix — the skill appends `-v1.0`), the **target object** the schema describes (one short noun phrase, used for `title`), the **consuming spec path** (the `Refs spec/<topic>/<slug>/` anchor that goes into `description`), and the **on-disk location** (defaults to `<owner-path>/schemas/` next to the data; the spec forbids `spec/` as a location).
2. Compose the `$id` URI deterministically: `https://github.com/nolte/<repo>/blob/main/<owner-path>/schemas/<slug>-v1.0.schema.yaml`. Read `<repo>` from the `repository` field of the nearest manifest (`pyproject.toml`, `package.json`, `.claude-plugin/plugin.json`) or — when no manifest declares it — from the `origin` remote URL trailing path segment. `<owner-path>` is the repository-relative directory the `schemas/` subdirectory sits under (for example `project/features` for feature frontmatter, `.github/workflows` for workflow inputs); the URI's path after `/blob/main/` matches the file's actual on-disk path.
3. Draft the file with exactly the ten top-level entries from the spec's §Document skeleton, in the declared order:
   - `$schema: https://json-schema.org/draft/2020-12/schema`
   - `$id: <composed URI>`
   - `title: <object name>`
   - `description: |\n  <one to three sentences>. Refs spec/<topic>/<slug>/.`
   - `type: object` (default; offer `array` or `oneOf`-at-top-level when the target shape demands it)
   - `required: []` (alphabetised once populated)
   - `additionalProperties: false` (default; flip to `true` only on explicit user request and require a `description` justification)
   - `properties: {}` (filled in step 4)
   - `$defs:` is added only when step 5 produces an entry
   - `examples: []` (filled in step 6)
4. Walk the property list one at a time. For each property ask for: name (snake_case unless the data is externally camelCase), `type`, one-sentence `description`, and any type-specific constraint the user supplies. Surface the spec's "property sub-schema skeleton" checklist after each addition so missed fields are flagged before the next property.
5. After the property pass, scan for shapes that are repeated more than once and propose extraction into `$defs` (PascalCase names: `SemverString`, `ISODate`, `FeatureSlug`). Ask for approval before rewriting the duplicates as `$ref: '#/$defs/<Name>'`.
6. Ask for at least one fully-valid example. Run meta-validation on the draft (operation 4) inline; refuse to write the file if the example doesn't validate.
7. Show the proposed file content. Only write after explicit approval. After write, run the repository's quality gate (`task lint` or the configured equivalent) and surface the result.
8. Update the repository README or `schemas/README.md` to list the new schema with its `$id`, `title`, and consuming spec. Do this as a separate proposed edit with its own approval — never bundle the README touch with the schema write.

---

## 2. Audit existing schemas

Read-only walk. Never write during audit.

Scan every file matching `**/*.schema.yaml`. For each file, classify each spec requirement as:

- **pass**: the file matches the spec.
- **missing**: a required key, file, or section is absent.
- **drift**: present but diverges (wrong format, wrong order, dialect mix, inline duplicate, relative `$ref`, missing description).

Report findings grouped by file, then by spec section. Items the audit checks per file:

- Dialect: `$schema` is the first keyed entry and exactly `https://json-schema.org/draft/2020-12/schema`.
- Identity: `$id` is the second keyed entry, under `https://github.com/nolte/<repo>/blob/main/`, with a `-v<major>.<minor>.schema.yaml` suffix; the URI's path after `/blob/main/` matches the file's repository-relative on-disk path.
- Skeleton order: the ten top-level entries appear in the spec's declared order; no top-level key outside the allowlist.
- File layout: filename matches the trailing slug of `$id`; double extension `.schema.yaml`; file lives outside `spec/`.
- Description anchor: `description` contains the literal substring `Refs spec/`.
- Property descriptions: every top-level entry under `properties` carries a `description`.
- `$ref` shape: every `$ref` is either `#/$defs/<Name>` or an absolute `https://github.com/nolte/…` URI; no relative paths, no dialect mix.
- `$defs` naming: every `$defs` entry name is PascalCase; no empty `$defs:` map.
- Inline duplication: no object shape appears verbatim more than once outside `$defs` (heuristic: structural fingerprint of `type`+`required`+`properties.keys()`).
- Examples: at least one entry in `examples`; the entry validates against the schema (operation 4).
- Readme listing: the schema is enumerated in the repository's README or in a `schemas/README.md`.

Also run operation 4 against every schema and report any meta-validation failure as a separate finding.

---

## 3. Refactor (apply audit findings)

Walk audit findings one at a time. For each finding, propose the minimal fix and ask for confirmation before writing:

- **`$schema` missing or wrong dialect**: replace with the canonical URI. If the existing dialect is an older draft and properties are draft-specific (`format` semantics differ), call that out and ask before flipping the dialect silently.
- **`$id` missing or unversioned**: propose a composed URI and a `-v1.0` suffix; if the schema is already referenced from outside the repo (grep the portfolio for the would-be URI's slug as a sanity check), warn that introducing a new `$id` is a major-version event.
- **Skeleton out of order**: rewrite the top-level entries into the spec's declared order. Preserve every comment block's positional intent — comments that document a specific entry travel with that entry, not with the line number they occupied before.
- **Inline duplicate**: extract the duplicate into a new `$defs/<Name>` entry, rewrite every duplicate occurrence as `$ref: '#/$defs/<Name>'`, and propose the `<Name>` to the user (PascalCase). Never extract a duplicate without explicit approval; the cost of a wrong-name `$defs` entry is a follow-up rename PR.
- **Relative `$ref`**: rewrite to an absolute `$id`-based reference. If the target file's `$id` is missing, queue a separate finding for the target file first; never invent an absolute URI for a target that doesn't declare one.
- **Missing property `description`**: propose a one-sentence description based on the property name and any surrounding `examples` / `pattern` hints. Always show the proposal; never write a description silently.
- **Forbidden top-level key (`x-…` or other)**: stop and ask. The spec allows a single `vendorExtensions` escape hatch, but routing into it is an operator decision.
- **`additionalProperties: true` without justification**: ask whether to flip to `false` or to add the justification into `description`.

After every successful write, re-run the affected check so the user sees the item flip to **pass**. Never batch silent writes.

---

## 4. Meta-validation (schema-against-meta-schema)

Validate every `*.schema.yaml` file against the JSON Schema 2020-12 meta-schema. The skill prefers, in order:

1. `task lint` if the Taskfile target wraps the same validator the skill would call directly; record in the report that the target was used.
2. `check-jsonschema --check-metaschema <file>` (Python ecosystem default).
3. `ajv compile --spec=draft2020 -s <file>` (Node ecosystem default).
4. `python -m jsonschema --instance <file> <meta-schema>` as a last resort.

For each file, report:

- **pass**: validator exits zero.
- **fail**: validator exits non-zero; surface the validator's error output verbatim.
- **skipped**: validator binary not installed; surface the install hint and treat the gate as **blocked**, not **pass** (per spec §Meta-validation and data validation).

The skill never silences a meta-validation failure with `--no-fail` or equivalent flags. A failing schema is a stop-and-fix event.

---

## 5. Data validation (data-against-schema)

Validate every data file (`*.yaml`, `*.yml`, `*.json`) the skill can associate with a schema. Association is resolved, in order:

1. **Sidecar comment**: a `# yaml-language-server: $schema=<path-or-uri>` line in the first 10 lines of the data file. The skill resolves the path relative to the data file or matches the URI against an `$id` in the repo.
2. **Refs comment**: a `# Refs https://github.com/nolte/<repo>/blob/main/<owner-path>/schemas/<slug>-v<major>.<minor>.schema.yaml` line, matching the `$id` form the spec mandates. Same resolution as the sidecar comment.
3. **Repo mapping**: a `.schemas-config.yaml` at the repo root with a `mappings:` list of `{path: <glob>, schema: <path-or-id>}` entries.

For each association, run the validator and report **pass** / **fail** / **skipped** with the same semantics as operation 4. Refuse to invent associations; data files with no resolvable schema are reported as **unassociated** rather than silently skipped.

---

## 6. Lifecycle bump (revise an existing schema)

When the user wants to revise an existing schema:

1. Diff the proposed change against the current file. Classify the change:
   - **Minor (backwards-compatible)**: new optional property, relaxed constraint, additional `examples` entry.
   - **Major (breaking)**: renamed property, removed property, narrowed type, tightened `required` list.
2. Compose the new filename and `$id` segment: `<slug>-v<major>.<minor+1>` for minor, `<slug>-v<major+1>.0` for major.
3. Write the new file alongside the previous one (never edit in place if the schema's `$id` is referenced from anywhere by absolute URI — grep the portfolio for the URI string as a sanity check).
4. Surface every consumer that pins the previous `$id` and propose, but do not perform, the migration edits. The actual consumer migrations are tracked as a separate to-do for the operator; the spec forbids in-place edits to externally-referenced schemas, not consumer migration in the same PR.
5. Add a release-note entry under a `Schema` heading via the `release-notes-curate` skill (delegate, don't duplicate). Stop and route the user there.

---

## 7. Re-audit

When the user has finished approving fixes, re-run operations 2, 4, and 5 end-to-end and present a fresh grouped summary. Items still **missing**, **drift**, **fail**, or **unassociated** must be called out so the user knows what remains and why.
