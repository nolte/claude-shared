---
title: backstage-catalog-generate
audience: [maintainer]
content_mode: reference
track: developer-docs
last_updated: generated
---

# backstage-catalog-generate

> Generates a schema-valid Backstage catalog-info.yaml from an existing project by inferring per-kind MUST-floor fields from repo signals, confirming the rest with the operator, and self-validating.

_Generates a schema-valid Backstage catalog-info.yaml from an existing software project, conforming to spec/project/backstage-catalog-generation/. Inspects the repo (language/structure, remote slug, CODEOWNERS, OpenAPI/AsyncAPI/GraphQL/gRPC specs, colocated docs), infers the per-kind MUST-floor fields, confirms what it cannot infer (owner, spec.system, dependsOn, lifecycle) with the operator, writes the descriptor at the repo root, and self-validates. Invoke when the user asks to \"generate a catalog-info.yaml\", \"onboard this repo into Backstage\", \"create a Backstage Software Catalog entity\", \"add this service to our developer portal\", or German equivalents (\"erzeuge eine catalog-info.yaml\", \"nimm dieses Repo in Backstage auf\"). Optionally emits a Tech Radar TechRadarLoaderResponse JSON (never a catalog entity). Don't use to configure a Backstage backend / catalog.providers, install the Tech Radar UI plugin, or ingest Group/User org entities. Single-shot; resume not applicable._

- **Plugin:** `nolte-shared`
- **Phase:** 4 Build (`build`)
- **Tags:** `scaffolding`
- **Source:** [skills/backstage-catalog-generate/SKILL.md](https://github.com/nolte/claude-shared/blob/main/skills/backstage-catalog-generate/SKILL.md)

## Use when

- you want to onboard an existing repository into a Backstage Software Catalog
- you want a schema-valid catalog-info.yaml inferred from a project's signals
- you want a Tech Radar TechRadarLoaderResponse JSON generated from a tech inventory

## See also

- [`project-structure-apply`](project-structure-apply.md)

---

## Backstage Catalog Generate

Turns an existing software project into a schema-valid Backstage `catalog-info.yaml` at the repository root — inferring what the repo reveals, asking the operator for what it does not, and self-validating before it presents the result. The authoritative rules live in **`spec/project/backstage-catalog-generation/`**; this skill operationalises that spec. When the spec and this body disagree, the spec wins.

### Why this is a skill, not an agent

- **Operator-invoked, conversational.** Reached as `/nolte-shared:backstage-catalog-generate` against the current repo; the operator drives it directly.
- **Mid-flow confirmation is the contract.** Owner resolution, `spec.system`, `dependsOn`, and an uncertain `lifecycle` cannot be inferred safely from one repo; the skill surfaces each as a confirmation gate rather than guessing. An agent's fire-and-forget shape would lose those gates.
- **The result flows back into the conversation.** The written descriptor path and the list of inferred-vs-confirmed values land in the operator's context for the next step (committing, opening the register-component PR).
- Counter-dimension: the repo inspection could run as an isolated reader, but the load-bearing dimensions — operator invocation and the per-field confirmation gates — make this a skill.

### German trigger phrases

- „erzeuge eine catalog-info.yaml", „nimm dieses Repo in Backstage auf", „erzeuge einen Backstage-Catalog-Eintrag für dieses Projekt", „füge diesen Service unserem Developer-Portal hinzu", „generiere ein Tech-Radar-JSON"

### Repo signals → fields

The skill reads these signals and maps them to descriptor fields (every inferred value is recorded as *inferred*, distinct from *confirm*):

| Signal | Field | Notes |
|---|---|---|
| repo / project name | `metadata.name` | slugify, strip leading/trailing non-alphanumerics, cap 63 → must satisfy `isValidObjectName` |
| primary language / structure | `spec.type` | `service` / `website` / `library` (Component); convention, not a fixed enum |
| `git remote` slug | `github.com/project-slug`, `backstage.io/source-location` | `org/repo`; source-location is `url:…/<repo>/` with trailing slash |
| `CODEOWNERS` / team slug | `spec.owner` | bare slug → Group; an individual needs an explicit `user:` prefix |
| `openapi.yaml` / `asyncapi.yaml` / `*.graphql` / `*.proto` | an API entity + `spec.providesApis` | API `spec.definition` via `$text: ./<relative-path>`, `spec.type` = `openapi`/`asyncapi`/`graphql`/`grpc` |
| colocated `docs/` / `mkdocs.yml` | `backstage.io/techdocs-ref: dir:.` | only when docs are colocated |
| `README` description / `package.json` etc. | `metadata.description`, `metadata.tags` | tags match `^[a-z0-9:+#]+(\-[a-z0-9:+#]+)*$` |

`spec.lifecycle`, `spec.system`, `spec.dependsOn`, and `spec.domain` are **never inferred silently** — default `lifecycle` only on a justifying signal, otherwise confirm; `system`/`dependsOn`/`domain` always require operator input.

### Operations

#### Generate a catalog-info.yaml (default)

1. **Inspect.** Read the repo signals above. Determine the entity kind(s) — almost always a single `Component`, plus an `API` entity when an interface definition is found. Consult the per-kind tables in `spec/project/backstage-catalog-generation/` §"Entity kinds" for the required/optional fields of any other kind.
2. **Infer.** Fill the MUST-floor for each kind. For a Component that is: `apiVersion: backstage.io/v1alpha1`, `kind: Component`, a valid `metadata.name`, `spec.type`, `spec.lifecycle`, `spec.owner`. Mark each value *inferred* or *needs-confirm*.
3. **Confirm.** Present the inferred descriptor and the open questions (owner resolution, `lifecycle`, optional `system`/`dependsOn`) to the operator in one pass. Never emit a guessed `system`/`dependsOn`/`domain`; never emit an owner that cannot be confirmed to resolve — flag it as operator-action-required instead.
4. **Emit.** Write `catalog-info.yaml` at the **repository root** (matching the discovery default path). Use multi-entity `---` separators when emitting a Component plus its API. Quote any numeric/boolean-looking annotation value so it stays a string.
5. **Self-validate.** Run the offline `@roadiehq/backstage-entity-validator` when available (`npx @roadiehq/backstage-entity-validator catalog-info.yaml`); otherwise apply the §Hard rules checklist below as a deterministic pre-flight. Treat reference-target existence (owner/system/API) as **unverified** by the offline check — surface those references as claims to confirm, not validated facts.
6. **Report.** Tell the operator the written path, the inferred-vs-confirmed split, and any references still requiring an existing Group/User/System in the target catalog.

#### Generate a Tech Radar JSON (optional secondary)

When the operator asks for a Tech Radar output: emit a `TechRadarLoaderResponse` JSON (`quadrants`, `rings`, `entries`) per `spec/project/backstage-catalog-generation/` §"The Tech Radar data model" — **not** a `catalog-info.yaml`, and **never** modelled as a catalog entity. Express each entry's ring placement through its `timeline` (a snapshot with `ringId` and a coercible `date`), not as a direct field. Target the `@backstage-community` package model; never reference the deprecated `@backstage` Tech Radar package or the dead `backstage.io/docs/features/techradar/` URLs.

### Gotchas

Backstage's real validation is stricter and less obvious than its prose docs — these are the quirks that bite a generator:

- **The offline validator does not check reference-target existence.** `@roadiehq/backstage-entity-validator` validates schema and field-format only; an `owner`/`system`/API reference can pass and still dangle at processing time. Always surface references as claims to confirm against the target catalog, never as validated facts.
- **Numeric/boolean-looking annotation values must be YAML-quoted.** Annotation values are checked as `typeof string`; an unquoted `github.com/user-id: 123456` or `backstage.io/orphan: true` parses as a number/bool and fails. Quote them.
- **`metadata.name` is stricter than "alphanumerics separated by `[-_.]`".** The first and last character must be alphanumeric — a slug that ends in `-` (common after naive slugification) is rejected by `FieldFormatEntityPolicy` at processing time, after it passed coarse ingestion.
- **`Resource` has no `lifecycle`** even though `Component` and `API` do — emitting it is invalid. Symmetrically, `Group.children` and `User.memberOf` must be present even when empty (`[]`).
- **There is no official `backstage-cli` validate command.** Validation is either the `@roadiehq` validator or a `POST` to a running backend's `/api/catalog/validate-entity` (where `location` goes in the JSON body, not an HTTP header).
- **The Tech Radar moved to `@backstage-community`.** The old `@backstage` Tech Radar package and the `backstage.io/docs/features/techradar/` URLs are dead — never cite them.

### Hard rules

- **Never author auto-set or output-only fields:** `backstage.io/managed-by-location`, `backstage.io/managed-by-origin-location`, `backstage.io/orphan`, `metadata.uid`, `metadata.etag`, `relations`, `status`.
- **Never emit `spec.lifecycle`** on Resource, System, Domain, Group, or User — only Component and API carry it.
- **Always include empty-but-required keys:** `spec.children: []` on a Group with no known children; `spec.memberOf: []` on a User with no known memberships.
- **API entities must carry a non-empty `spec.definition`**, supplied via a `$text:` placeholder, and the providing Component lists the API under `providesApis`.
- **`metadata.name` must satisfy `isValidObjectName`:** length 1–63, first and last character alphanumeric, separators `[-_.]` interior only. `metadata.namespace` is a DNS label (lowercase, no underscore/dot).
- **Owner disambiguation:** a bare owner reference resolves to a **Group**; emit an explicit `user:`-prefixed reference for an individual. Prefer the full `kind:namespace/name` form for cross-system robustness.
- **Never use a deprecated annotation:** `backstage.io/github-actions-id` → `github.com/project-slug`; `backstage.io/definition-at-location` → placeholder substitution; `jenkins.io/github-folder` → `jenkins.io/job-full-name`.
- **Never branch on the old-vs-new frontend system** — `catalog-info.yaml` is a backend, frontend-agnostic concern.
- **Distinguish inferred from confirmed** in every output; never silently emit a value the operator must own.
- When `spec/project/backstage-catalog-generation/` disagrees with this body, the spec wins; propose updating this skill rather than diverging.
