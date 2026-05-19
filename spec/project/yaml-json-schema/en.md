# YAML JSON Schema

Status: draft

## Context

Readers: schema authors (the primary subject of every MUST rule below), CI / quality-gate maintainers (who wire meta-validation and data-conformance into `task lint`), and schema consumers across the portfolio (who pin `$id` values in their own `$ref` targets).

Across the portfolio, configuration, manifests, and structured data formats are increasingly described by schemas—frontmatter shapes for `project/features/`, the per-repo `project/portfolio.yml` envelope, GitHub Actions inputs, MkDocs plugin configuration, custom Ansible inventory layouts, and the JSON-Schema descriptors that ship next to them. The portfolio convention is to author those schemas as **JSON Schema 2020-12 documents in YAML notation** rather than in JSON: YAML carries comments, supports multi-line literal strings, and reads better than the JSON equivalent for the size of schema documents authored by hand.

Without a binding convention, hand-authored schema files drift along several axes: which `$schema` dialect URI is canonical, whether `$id` is required, where reusable sub-schemas live (inline `properties` vs `$defs` vs separate files), whether keywords follow `snake_case` or `camelCase`, whether examples and `default` values are kept, and which validator a CI gate is allowed to assume. The drift isn't catastrophic in isolation but becomes catastrophic across a portfolio: two repositories describing the "same" object end up with two incompatible schemas, and a consumer can't reason about the wider shape without re-reading both.

This spec defines, for every YAML-encoded JSON Schema document the portfolio authors:

1. **the dialect** it claims (`$schema`),
2. **the structural skeleton** that file must carry,
3. **the reference rules** that govern `$ref`, `$defs`, and external `$id` boundaries,
4. **the validation contract** that lets a CI gate prove the schema is itself valid and that any companion data files conform to it,
5. **the on-disk layout** that makes the schema discoverable next to the data it describes.

The spec deliberately scopes itself to **JSON Schema 2020-12 in YAML**. JSON-encoded schemas, OpenAPI Schema Objects, and AsyncAPI Schema Objects are out of scope—they have their own governing specs (OpenAPI 3.x §Schema Object, AsyncAPI 3.x §Schema Object) which intentionally diverge from pure JSON Schema and warrant their own portfolio rule when the need arises.

## Goals

- Every YAML-encoded JSON Schema document in the portfolio is recognisable by file extension, header keywords, and on-disk location—no guessing required.
- Every schema declares its dialect (`$schema`) and identity (`$id`) so a validator can resolve it deterministically across repositories without bespoke configuration.
- Reusable sub-schemas live in `$defs` and are referenced via `$ref`; inline duplication of complex object shapes is forbidden so a refactor never has to chase two copies.
- Every schema is itself validated against its declared dialect's meta-schema as part of the repository's quality gate; a schema that doesn't pass meta-validation is broken regardless of whether downstream consumers cope.
- Every data file the schema governs (`*.yaml`, `*.yml`, `*.json` companions) is validated against that schema by the same skill that authored the schema, so authoring and validation aren't two unrelated practices.
- The conventions are operationalised by exactly one skill (`nolte-shared:yaml-json-schema`) that covers authoring, auditing, refactoring, and data validation. Operators don't shop between half-overlapping skills.

## Non-Goals

- Choosing a single JSON Schema validator implementation. The choice between `check-jsonschema`, `ajv-cli`, `python-jsonschema`, and `jsonschema-rs` stays a per-repo decision driven by the language ecosystem the project already uses.
- Defining OpenAPI 3.x Schema Object or AsyncAPI Schema Object conventions. Those formats inherit *most* of JSON Schema but diverge in well-known ways (`nullable`, `discriminator`, `example` vs `examples`) and need their own spec.
- Authoring schemas as JSON-encoded files (`*.json` or `*.schema.json`). The portfolio's authoring rule is YAML-only, and `*.schema.yaml` is the only authoring form this spec recognises. JSON-encoded schemas remain forbidden until a separate spec governs them; downstream consumers that need a JSON artefact derive it at build time via `yq -o json` (or an equivalent transform) from the YAML source.
- Replacing `spec/project/feature/` (which governs the *content* of feature frontmatter) with a schema spec. This spec is about the shape and lifecycle of schema files; the frontmatter spec stays authoritative for what feature frontmatter contains.
- Centralising frequently-shared schemas in a portfolio-wide registry directory. The portfolio policy is repo-local placement; cross-repository sharing is solved through `$id` discipline and absolute `$ref` URI targets into the owning repo's GitHub path, not through a shared directory under `spec/portfolio/<topic>/schemas/`.
- Mandating code-generation from schemas (`Pydantic` models, TypeScript types, Go structs). Generation is permitted but stays out of this spec's MUST/SHOULD/MAY surface—that's a future spec.

## Requirements

### Dialect

- **MUST** declare `$schema` as the first keyed entry of every schema file, with the value `https://json-schema.org/draft/2020-12/schema`. The portfolio standardises on JSON Schema 2020-12 (the most recent stable draft as of authoring). Other draft identifiers (`draft-07`, `draft/2019-09`) aren't accepted; if an upstream consumer requires an older draft, that consumer's repository declares it locally and documents the deviation in its README.
- **MUST NOT** mix dialects within a single schema document. A `$ref` into a draft-07 schema from a 2020-12 document is forbidden; if the referenced schema is draft-07 by necessity (external vendor), copy or transcribe the relevant sub-schema into the 2020-12 document and record the transcription source in a `description`.
- **SHOULD** declare `$schema` even in `$defs` sub-schemas embedded inside another document only when the embedded schema is intended to be lifted into its own file later; otherwise the parent's `$schema` declaration covers the whole document tree.

### Identity

- **MUST** declare `$id` as the second keyed entry of every schema file, with an absolute URI under the `https://github.com/nolte/` namespace following the pattern `https://github.com/nolte/<repo>/blob/main/<owner-path>/schemas/<slug>-v<major>.<minor>.schema.yaml`. The URI mirrors the schema file's repository-relative on-disk path inside the GitHub-hosted owning repository, which makes it unique across the portfolio by construction. JSON Schema treats `$id` as a logical identifier; the URI doesn't have to resolve through a `fetch` call, but the file the URI points at MUST exist on `main` once the schema is merged.
- **MUST** bump the `<minor>` segment of the `$id` whenever the schema gains a backwards-compatible field, and the `<major>` segment whenever an existing field is renamed, removed, or its type narrowed. Schemas without versioned `$id` segments fail meta-validation.
- **MUST NOT** reuse a `$id` URI across two unrelated schemas. The repo-rooted GitHub path pattern (`…/<repo>/blob/main/<owner-path>/schemas/<slug>-v<major>.<minor>.schema.yaml`) keeps uniqueness automatic as long as no two schemas share the same filename in the same on-disk directory.
- **SHOULD** treat the `$id`'s GitHub path as authoritative for the on-disk location of each schema: a schema with `$id: https://github.com/nolte/claude-shared/blob/main/project/features/schemas/feature-frontmatter-v1.0.schema.yaml` lives at exactly `project/features/schemas/feature-frontmatter-v1.0.schema.yaml` inside the repository checkout. The trailing path segment of the URI matches the filename so `grep` and `gh search` find the file from either side.

### File layout and extension

- **MUST** name every schema file with the suffix `.schema.yaml` (lower-case, double extension). The double extension is the unambiguous on-disk signal that the file is a schema, not a data file. `*.schema.yml` (single-`l`) is forbidden—the portfolio normalises on `.yaml`.
- **MUST** store schemas next to the data they govern under a `schemas/` directory: `<repo>/<owner-path>/schemas/<slug>-v<major>.<minor>.schema.yaml`. For example, `project/features/schemas/feature-frontmatter-v1.0.schema.yaml`, or `.github/workflows/schemas/inputs-v1.0.schema.yaml`.
- **MUST NOT** store schemas under `spec/`. The `spec/` tree is reserved for governance documents (this one included), not for machine-readable schemas the governance documents prescribe.
- **MUST NOT** lift a schema into a portfolio-shared location (`spec/portfolio/<topic>/schemas/`). Cross-repository sharing happens through `$id` URI discipline and absolute `$ref` into the owning repo's GitHub path; centralising schemas under `spec/portfolio/` would duplicate the source of truth and is forbidden.

### Document skeleton

Every schema file MUST be readable as YAML, parseable as JSON Schema 2020-12, and structured as exactly the following ordered keyed entries at the top level:

1. `$schema`: the dialect URI (see §Dialect).
2. `$id`: the identity URI (see §Identity).
3. `title`: a short human-readable noun phrase naming the object the schema describes (for example `Feature Frontmatter`).
4. `description`: one to three sentences explaining what the schema governs and where the schema is consumed. The description **MUST** name the consuming spec (`Refs spec/<topic>/<slug>/`) so the schema is traceable to its governing spec.
5. `type`: the JSON Schema type keyword. For schemas describing objects, the value is `object`; for schemas describing arrays, `array`. Schemas that describe a union of types use `oneOf` or `anyOf` at the top level instead and omit the top-level `type`.
6. `required`: the list of required property names, alphabetised. Omitted for schemas whose top-level type isn't `object`.
7. `additionalProperties`: explicit `false` or an inline schema. The portfolio default is `false` for closed object shapes; `true` is permitted only when the description of the schema explains why the object is intentionally extensible.
8. `properties`: the per-property sub-schemas, in the order the consuming spec lists them. Property names use **`snake_case`** unless the data they describe is itself `camelCase` by external standard (for example GitHub Actions inputs).
9. `$defs`: the reusable sub-schema map. Present only when at least one entry is referenced via `$ref` from elsewhere in the document; never present empty.
10. `examples`: a list of at least one fully-valid example object. The example **MUST** validate against the schema; the meta-validation gate proves it.

- **MUST NOT** introduce additional top-level keyed entries beyond the ten listed above. Implementation-specific extension keywords (`x-…`) are forbidden at the top level; if a vendor extension is genuinely needed, it lives under a single top-level `vendorExtensions` object documented in the schema file's `description`.
- **SHOULD** carry a one-line YAML comment immediately above the file's first non-comment line in the form `# Schema for <object name>; consumed by <consumer>` so a reader knows the scope without parsing.

### Property sub-schemas

Inside `properties` and inside `$defs`, every individual property sub-schema MUST itself follow a reduced skeleton:

- `type`: the JSON Schema type keyword (`string`, `integer`, `number`, `boolean`, `array`, `object`, or `null`); never omitted unless the property uses `oneOf`/`anyOf`/`enum` to constrain shape.
- `description`: one sentence explaining what the property means and why it exists; never omitted on top-level `properties`. For trivial enum members inside a nested array of strings, omit is permitted.
- Type-specific constraints (`enum`, `pattern`, `minimum`, `maximum`, `minLength`, `maxLength`, `format`, `items`, `properties`, …) follow JSON Schema 2020-12 directly with no portfolio-specific renaming.
- `default`: present only when the consuming spec defines a default; never invented to "be helpful." A `default` keyword inside the schema is documentation, not coercion.
- `examples`: present on properties whose meaning isn't obvious from name and `description` alone (free-form strings, complex objects, regex-constrained values).

### References (`$ref` and `$defs`)

- **MUST** extract a sub-schema into `$defs` and reference it via `$ref` when the same shape is repeated more than once in the same schema document. Inline duplication of object schemas is the most common drift cause across schema files and is forbidden.
- **MUST** name each `$defs` entry in `PascalCase` (`SemverString`, `ISODate`, `FeatureSlug`). The naming intentionally diverges from the `snake_case` used in `properties` so a `$ref` reader sees at a glance that the target is a reusable definition, not a property name.
- **MUST** address `$ref` targets inside the same document using the JSON-Pointer fragment form `#/$defs/<Name>`. Other fragment shapes (`#/properties/foo`, anchor-based refs without `$anchor`) are forbidden.
- **MAY** reference an external schema by absolute `$id` URI (`$ref: https://github.com/nolte/<repo>/blob/main/<owner-path>/schemas/<slug>-v<major>.<minor>.schema.yaml`) when the external schema lives in another `https://github.com/nolte/`-namespaced repository and its file is committed to that repository's `main` branch. The validator config of the consuming repository is responsible for mapping the URI to a retrievable file path—typically by mirroring the file under a local `vendor/schemas/` directory or by cloning the owning repo as a build-time dependency.
- **MUST NOT** use relative-path `$ref` targets (`$ref: ../other.schema.yaml#/$defs/Foo`). Relative paths break the moment the schema is imported by `$id` from a different working directory.

### Documentation and discovery

- **MUST** name the consuming spec of each schema in the top-level `description` using the literal string `Refs spec/<topic>/<slug>/`. This is the same `Refs` form used in pull-request bodies (per `spec/project/pull-request-workflow/`) and pulls schema files into the same traceability graph.
- **SHOULD** carry a header YAML comment block (lines beginning with `#` followed by a space) above `$schema` summarising the purpose of the schema for a human reader, especially when the schema is more than ~30 lines.
- **MUST** list every schema file in the repository's README or in a `schemas/README.md` placed alongside the schemas, so a reader landing in the repo without prior knowledge can enumerate the schemas without filesystem grep.

### Meta-validation and data validation

- **MUST** validate every `*.schema.yaml` file in the repository against the JSON Schema 2020-12 meta-schema as part of the repository's quality gate (`task lint` or equivalent). A file under `*.schema.yaml` that fails meta-validation fails the quality gate; there is no soft-fail path.
- **MUST** validate every data file (any `*.yaml` or `*.json` file under a path the schema declares it governs, established via a sidecar `# yaml-language-server: $schema=…` comment, an `# Refs schema://…` comment, or a repository-level `.schemas-config.yaml` mapping) against its declared schema as part of the same quality gate.
- **SHOULD** prefer `check-jsonschema --check-metaschema` for meta-validation in Python-leaning repos and `ajv compile --spec=draft2020` in Node-leaning repos; the choice is per-repo and recorded in the repo's `Taskfile.yml`.
- **MUST NOT** treat absence of a validator as a passing gate. If the chosen validator isn't installed, the gate fails with an install hint; silent skip is forbidden.

### Lifecycle

- **MUST** introduce a new schema (a new `<slug>-v1.0.schema.yaml`) through the `nolte-shared:yaml-json-schema` skill so the dialect, identity, layout, and meta-validation invariants are applied without operator drift.
- **MUST** revise an existing schema by writing a new file `<slug>-v<major>.<minor+1>.schema.yaml` (minor bump) or `<slug>-v<major+1>.0.schema.yaml` (major bump) and updating consumers to address the new `$id`. The previous file stays in place until every consumer has migrated; it's removed in a follow-up commit when no consumer references it.
- **MUST NOT** edit a schema file in place once it has been referenced from outside its own repository by `$id`. In-place edits to externally-referenced schemas break consumers that pin the `$id` URI.
- **SHOULD** record each schema bump in the repository's release notes under a `Schema` heading; the `release-notes-curate` skill recognises the heading and surfaces it.

### Delimitation

- **MUST** keep this spec distinct from `spec/project/feature/`: the feature spec governs *which* fields a feature frontmatter carries; this spec governs *how* the schema describing those fields is written.
- **MUST** keep this spec distinct from `spec/project/project-structure/`: the structure spec governs the repository layout; this spec governs schemas placed inside that layout's `schemas/` directories.
- **MUST NOT** be invoked to validate OpenAPI Schema Objects, AsyncAPI Schema Objects, or JSON-encoded JSON Schema documents. Those formats have or will have their own specs.

## Acceptance Criteria

- [ ] Every file in the repository matching `**/*.schema.yaml` declares `$schema: https://json-schema.org/draft/2020-12/schema` as its first keyed entry and an `$id` under `https://github.com/nolte/<repo>/blob/main/` as its second; the path segment of the URI after `/blob/main/` matches the file's actual repository-relative path.
- [ ] Every `*.schema.yaml` file passes JSON Schema 2020-12 meta-validation through `task lint`; the lint step explicitly exits non-zero on at least one synthetic broken schema introduced during the gate's regression test.
- [ ] Every `*.schema.yaml` file's `description` carries the literal string `Refs spec/`, naming at least one governing spec.
- [ ] Every data file under a path declared schema-governed validates against its schema in the same lint step; introducing a synthetic invalid data file is detected.
- [ ] No `*.schema.yaml` file uses relative-path `$ref` targets; `grep -R '\$ref:.*\.\./' -- '**/*.schema.yaml'` returns empty.
- [ ] No `*.schema.yaml` file mixes dialects; every `$ref` resolves either to `#/$defs/…` inside the same document or to an absolute `https://github.com/nolte/…` URI.
- [ ] Every property sub-schema inside top-level `properties` carries a `description`; the meta-validation gate fails on missing descriptions.
- [ ] The `nolte-shared:yaml-json-schema` skill exists and its `SKILL.md` cites this spec by `spec/project/yaml-json-schema/`.
- [ ] The repository's README (or a `schemas/README.md`) enumerates every shipped `*.schema.yaml` file with its `$id`, title, and consuming spec.
- [ ] Every `*.schema.yaml` file carries the ten top-level keys from §Document skeleton in the declared order; the lint step rejects a file with an out-of-order key, a missing required key, or an extra top-level key (for example any `x-…` extension) with a non-zero exit code.
- [ ] Every property sub-schema inside top-level `properties` carries either a `type` keyword or a `oneOf` / `anyOf` / `enum` composition that constrains its shape; sub-schemas with neither are reported by the lint step (the JSON Schema meta-schema doesn't enforce this on its own).
- [ ] No `*.schema.yaml` file is edited in place after its first commit; every revision appears in the diff as a new file `<slug>-v<major>.<minor+1>.schema.yaml` (minor bump) or `<slug>-v<major+1>.0.schema.yaml` (major bump) alongside the previous file, and the previous file is removed only in a follow-up commit once no consumer still pins its `$id`.

## Open Questions

- Should the spec mandate `unevaluatedProperties: false` in addition to `additionalProperties: false` for closed object schemas with `allOf` composition, or is the simpler rule sufficient until composition becomes common?
- Should code generation from schemas (`Pydantic`, TypeScript, Go) become a SHOULD in a follow-up revision, and which generator becomes the portfolio default?

## References

- JSON Schema 2020-12 specification: <https://json-schema.org/draft/2020-12/release-notes>
- JSON Schema 2020-12 meta-schema: <https://json-schema.org/draft/2020-12/schema>
- JSON Schema core (`$schema`, `$id`, `$ref`, `$defs`): <https://json-schema.org/draft/2020-12/json-schema-core>
- JSON Schema validation keywords: <https://json-schema.org/draft/2020-12/json-schema-validation>
- `yaml-language-server` schema-association comment (`# yaml-language-server: $schema=…`): <https://github.com/redhat-developer/yaml-language-server#using-inlined-schema>
- `spec/project/feature/`: example consumer; feature frontmatter is a candidate schema target.
- `spec/project/pull-request-workflow/`: origin of the `Refs spec/<topic>/<slug>/` traceability pattern.
- `spec/project/quality-gate/`: gate that runs meta-validation and data validation in CI.
- `spec/project/spec-driven-development/`: the umbrella principle this spec inherits from.
