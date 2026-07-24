# Backstage `catalog-info.yaml` Generation

Status: draft

## Context

[Backstage](https://backstage.io) is the open-source developer-portal framework Spotify donated to the CNCF. Its central feature is the **Software Catalog**: a graph of software and organisational entities described in YAML descriptor files—conventionally one `catalog-info.yaml` at the root of each repository—that Backstage ingests, validates, and stitches into a navigable model of *what software exists, who owns it, what it depends on, and what APIs it exposes*. A second, separate feature, the **Tech Radar**, visualises an organisation's technology choices (adopt / trial / assess / hold) and is frequently bundled into the same portal, though it's wired to its own data source and not to the catalog.

The onboarding of an existing software project into a Backstage portal means writing a descriptor that's correct on three axes at once: it must satisfy Backstage's per-kind JSON schema and field-format validators; it must reference owners, systems, and APIs that actually resolve; and it should carry the well-known annotations that light up the portal's integrations (source links, CI, TechDocs, GitHub). Done by hand this is error-prone—the validation rules are stricter than the prose docs imply, several required fields are non-obvious (an empty-but-present `spec.children` on a Group, no `lifecycle` on a Resource), and a class of metadata must **not** be authored because the catalog sets it automatically.

This spec captures that body of knowledge as a normative reference and as a set of obligations for an automated generator. It's the **foundation for a later skill** that reads an existing software project and emits a fitting `catalog-info.yaml`. Per the project owner's scope it covers the **full entity kernel** (Component, API, Resource, System, Domain, Group, User, Location, and Template) with **particular focus on the Software Catalog and the Tech Radar**. It's grounded in a 146-source research pass over `backstage.io/docs` and the `backstage/backstage` and `backstage/community-plugins` source trees; the load-bearing source URLs are catalogued in §Sources.

The spec is deliberately two-layered, matching how the knowledge decomposes: **§The Backstage catalog model** states what a conformant descriptor (and the Tech Radar data file) must satisfy—the normative substrate, true regardless of any generator; **§Generator requirements** states what an automated generator built on that substrate must do, infer, emit, and refuse to emit. The Acceptance Criteria are written against a generator so the later skill has a testable target.

## Goals

- A generator can read an existing repository and emit a `catalog-info.yaml` that passes Backstage's schema, field-format, and policy validation deterministically, with no manual repair needed for the required floor.
- The full entity kernel is specified once, precisely: per-kind `apiVersion`/`kind`, required-vs-optional `spec` fields, the convention enums, and the derived relations—so the generator (and a human reviewer) has a single authoritative table rather than the scattered, sometimes-contradictory upstream prose.
- The generator emits the **MUST floor** for each kind plus a **safe MAY set** it can justify from repository signals, and it **never authors** the metadata Backstage sets automatically.
- Naming, reference, and format constraints are stated at their true (stricter) strength, so generated names and references never fail `FieldFormatEntityPolicy` at processing time.
- The Tech Radar data model is captured as a first-class, **separate** concern: its `TechRadarLoaderResponse` shape, its ring/quadrant/timeline model, its custom-data wiring, and the fact that it isn't a catalog entity and shares no model with the catalog.
- Validation and tooling are specified so the generator can self-check its output and so the practice slots into CI.
- Version and edition caveats (descriptor `apiVersion` strings, the new vs. legacy backend system, the Tech Radar package relocation) are pinned, so a generator doesn't branch on the wrong axis or target a deprecated format.

## Non-Goals

- **Building the generator skill itself.** This spec is the substrate; the skill is authored separately (via `skill-management` → `claude-plugin-developer`) against these requirements.
- **Operating or configuring a Backstage backend.** App-config wiring (`catalog.locations`, `catalog.providers.*`, the Tech Radar backend `techRadar.url`) is described only as the onboarding context the generated descriptor lands in; this spec doesn't own backend configuration.
- **Installing or theming the Tech Radar UI plugin.** The data model is in scope; the React install, routing, and styling aren't.
- **Authoring custom entity kinds, processors, or field-format validators.** The generator targets the core kernel and the default policy chain; extending the model is explicitly out of scope (and tracked as an Open Question only where it bounds generator behaviour).
- **Ingesting or creating Group and User entities.** Owner references must *resolve*, but populating the org graph (from an SCM org via `GitHubOrgEntityProvider` and friends) is an operator/SCM concern; the generator emits owner references and flags unresolved ones, it doesn't manufacture the owners.
- **Resolving cross-repository topology.** `spec.system`, `spec.dependsOn`, and `spec.domain` generally require knowledge the single repository doesn't carry; the generator proposes them only from explicit signals and otherwise defers to operator input.

## Requirements

The requirements are organised in two layers. **§The Backstage catalog model** is the normative substrate: every bullet states what Backstage itself requires of a conformant descriptor or Tech Radar data file, independent of any generator. **§Generator requirements** states what an automated generator built on that substrate MUST, SHOULD, and MAY do. A generator is conformant to this spec only when it satisfies the generator layer *and* every descriptor it emits satisfies the model layer.

### The Backstage catalog model

#### Entity envelope

- Every catalog entity **MUST** be a YAML object with exactly these authored root keys: `apiVersion` (string), `kind` (string, capitalised), `metadata` (object), and `spec` (object, kind-specific).
- `relations` (array of `{type, targetRef}`) and `status` (object with `items[]` of `{type, level, message, error?}`) are **read-only, catalog-derived** output fields. A descriptor **MUST NOT** author them; they're listed here only so a generator and reviewer recognise them as off-limits. The only documented `status.items[].type` is `backstage.io/catalog-processing` (with `level` one of `info`/`warning`/`error`); the status model is explicitly in active development and its format may change unexpectedly, so nothing should build on it.
- Multiple entities **MAY** share one file, separated by the standard YAML document separator `---`.
- The `metadata` block is common to all kinds. `metadata.name` is **required**; `metadata.namespace` is optional (defaults to `default`); `metadata.uid` and `metadata.etag` are output-only and **MUST NOT** be authored. Optional authored metadata: `title`, `description`, `labels` (key→value map), `annotations` (key→value map), `tags` (list of strings), `links` (array of `{url (required), title, icon, type}`). A link `icon` value consists of alphanumerics optionally separated by one of `[-_.]`.

#### Entity kinds

The kernel comprises nine kinds. Their `spec.type` and `spec.lifecycle` values are **conventions, not enforced enums** that are extensible per organisation; the per-kind JSON schema enforces only the `required` arrays and the string/array shapes. A conformant descriptor **MUST** carry every `required` field for its kind and **MUST** use the documented `apiVersion`/`kind` strings.

| Kind | `apiVersion` | Required `spec` | Optional `spec` | Convention enums | Notes |
| --- | --- | --- | --- | --- | --- |
| Component | `backstage.io/v1alpha1` | `type`, `lifecycle`, `owner` | `system`, `subcomponentOf`, `providesApis`, `consumesApis`, `dependsOn`, `dependencyOf` | type: `service`/`website`/`library`; lifecycle: `experimental`/`production`/`deprecated` | The primary generator target. |
| API | `backstage.io/v1alpha1` | `type`, `lifecycle`, `owner`, `definition` | `system` | type: `openapi`/`asyncapi`/`graphql`/`grpc` | `definition` MUST be a non-empty string; supply via `$text:` placeholder pointing at the spec file. |
| Resource | `backstage.io/v1alpha1` | `type`, `owner` | `system`, `dependsOn`, `dependencyOf` | type org-defined (`database`, `s3-bucket`, …) | **No `lifecycle` field.** Emitting `lifecycle` is invalid. |
| System | `backstage.io/v1alpha1` | `owner` | `type`, `domain` | type org-defined (`product`, `service`, …) | No `lifecycle`. |
| Domain | `backstage.io/v1alpha1` | `owner` | `type`, `subdomainOf` | type org-defined | No `lifecycle`. `subdomainOf` enables nested domains. |
| Group | `backstage.io/v1alpha1` | `type`, `children` | `profile` (`{displayName, email, picture}`), `parent`, `members` | type org-defined (`team`, `business-unit`, `root`) | `children` MUST be present; **may be an empty list `[]`** but the key can't be omitted. |
| User | `backstage.io/v1alpha1` | `memberOf` | `profile` | — | `memberOf` MUST be present; **may be `[]`** but the key can't be omitted. No type/lifecycle/owner. |
| Location | `backstage.io/v1alpha1` | — | `type`, `target` *or* `targets`, `presence` (`required`/`optional`, default `required`) | type, for example `url`/`file` | A pointer to more entity data, not a real-world thing. Use `target` or `targets`; an omitted `type` is inherited from the parent location. Spawned entities are tracked via the `backstage.io/managed-by-location` annotations. |
| Template | `scaffolder.backstage.io/v1beta3` | `type`, `owner` | `parameters`, `steps`, `output`, `secrets`, `presentation` | — | Current descriptor is `v1beta3`; `v1beta2` and the original `v1alpha1` scaffolder format are older/deprecated. Consumed by the Scaffolder, not part of the software-entity relation graph. Notable optional metadata annotation: `backstage.io/time-saved` (an ISO-8601 duration such as `PT4H`). |

- A descriptor **MUST NOT** emit `spec.lifecycle` on Resource, System, Domain, Group, or User—only Component and API carry it.
- A Group descriptor **MUST** include `spec.children` and a User descriptor **MUST** include `spec.memberOf`, even when empty (`[]`), or schema validation fails.
- The derived **relations** a generator should understand (authored indirectly, via the `spec` reference fields, never directly): `ownedBy`/`ownerOf`, `partOf`/`hasPart`, `dependsOn`/`dependencyOf`, `providesApi`/`apiProvidedBy`, `consumesApi`/`apiConsumedBy`, `parentOf`/`childOf`, `memberOf`/`hasMember`. Note the asymmetry: `spec` field names are plural (`providesApis`, `consumesApis`) while the derived relation type strings are singular (`providesApi`, `consumesApi`). The system-model overview page loosely writes `implementsApi`/`exposesApi`; the canonical relation type strings are the `providesApi`/`consumesApi` family from the well-known-relations page.

#### Naming and format constraints

The field-format validators (`KubernetesValidatorFunctions` / `CommonValidatorFunctions`) are **stricter than the prose docs**; a conformant descriptor (and therefore a generator) **MUST** satisfy them at their true strength:

- **`metadata.name`** (`isValidObjectName`): length **1–63**; the **first and last character MUST be alphanumeric**; the separators `[-_.]` are allowed only in interior positions. A leading or trailing separator is invalid. Names are case-insensitively unique per `(kind, namespace)`; mixed case is permitted by the default rule (the lowercase-and-dashes convention is stylistic, not enforced).
- **`metadata.namespace`** (`isValidDnsLabel`): lowercase alphanumerics in hyphen-separated groups, length 1–63; **no underscore, no dot, no uppercase**, which is stricter than `name`.
- **Label keys**: optional DNS-subdomain prefix (≤253 chars) + `/` + a name part following the entity-name rule. The `backstage.io/` prefix is reserved. **Label values**: empty string OR the entity-name rule.
- **Annotation keys**: same shape as label keys. **Annotation values**: arbitrary strings of any length and charset—only a `typeof string` check. Consequently a descriptor **MUST** YAML-quote any numeric- or boolean-looking annotation value (`github.com/user-id: '123456'`, `backstage.io/orphan: 'true'`) so it remains a string.
- **`tags`**: each tag matches `^[a-z0-9:+#]+(\-[a-z0-9:+#]+)*$` (lowercase `[a-z0-9:+#]` groups, hyphen-separated, length 1–63).
- The catalog rejects unknown root-level fields (`NoForeignRootFieldsEntityPolicy`): only `apiVersion`, `kind`, `metadata`, `spec`, `relations`, `status` are permitted at the root.

#### Entity references and owner resolution

- A reference in a `spec` field is a string `[<kind>:][<namespace>/]<name>` (1–3 parts). When a part is omitted: the **kind** defaults per the field's context, the **namespace** defaults to `default`. A compound object form `{ kind, namespace, name }` also exists; cross-system communication should use the full three-part string form, and the catalog-derived `relations[].targetRef` always carries the fully normalised three-part form.
- The per-field default kind a generator MUST apply when emitting a bare reference:

  | Field | Default kind |
  | --- | --- |
  | `owner` | Group |
  | `system` | System |
  | `subcomponentOf` | Component |
  | `providesApis` / `consumesApis` | API |
  | `dependsOn` / `dependencyOf` | Component (on a Component); Component or Resource (on a Resource) |
  | `domain` (System) | Domain |
  | `subdomainOf` (Domain) | Domain |
  | `parent` / `children` (Group) | Group |
  | `members` (Group) | User |
  | `memberOf` (User) | Group |

- **Owner disambiguation**: `spec.owner` accepts both Group and User, but a *bare* reference defaults to **Group**. To point ownership at a person, a descriptor **MUST** emit an explicit `user:`-prefixed reference; a bare `owner` that matches only a User of that name dangles.
- A reference resolves only if a matching entity already exists in the catalog. References are validated for *grammar* at the schema layer (the per-kind schema enforces only `string`/`minLength: 1` on reference fields) and for *target existence* downstream during processing—so a grammatically valid descriptor can still produce a dangling relation.

#### Well-known annotations and labels

Backstage documents a registry of well-known annotations. They split into two classes a generator must treat differently:

- **Authored (emit when the signal exists)**: the core registry plus integration annotations namespaced by the integrating system's domain (`backstage.io/` is reserved for what Backstage itself ships):

  | Key | Value shape | Purpose |
  | --- | --- | --- |
  | `backstage.io/source-location` | `url:https://github.com/org/repo/` (trailing slash for a directory) | Source-code root |
  | `backstage.io/view-url` / `backstage.io/edit-url` | URL | Canonical view / source-edit URLs for the entity file |
  | `backstage.io/source-template` | `template:default/create-react-app-template` | Scaffolder Template the entity was created from |
  | `backstage.io/techdocs-ref` | `dir:.` or a `url:` reference | Where the TechDocs source lives |
  | `backstage.io/techdocs-entity` / `-entity-path` | `component:default/example` / a docs path | External entity owning the docs, and the path within it |
  | `backstage.io/code-coverage` | `scm-only` / `enabled` | Code-coverage plugin |
  | `github.com/project-slug` | `org/repo` | Wires GitHub features |
  | `github.com/team-slug` | `org/team` | GitHub team mapping |
  | `github.com/user-login` | login name | GitHub user login |
  | `github.com/user-id` / `gitlab.com/user-id` | `'123456'` (quoted, immutable) | Numeric SCM user ids |
  | `gitlab.com/project-slug` | `org/repo` | GitLab project |
  | `graph.microsoft.com/tenant-id` (and siblings) | string | Microsoft Graph directory mapping |
  | `jenkins.io/job-full-name` | `folder-name/job-name` | Full CI job path |
  | `gocd.org/pipelines` | comma-separated names | CI pipelines |
  | `circleci.com/project-slug` | `github/org/repo` | CI project |
  | `sonarqube.org/project-key` | project key | Static-analysis project |
  | `sentry.io/project-slug` / `rollbar.com/project-slug` | `org/project` | Error-tracking projects |
  | `periskop.io/service-name` | service name | Exception aggregation |
  | `vault.io/secrets-path` | `test/backstage` | Secrets path |
  | `backstage.io/ldap-rdn` / `-uuid` / `-dn` | string | Directory-service ids |

- **Plugin-page annotations (not on the central registry)**: integration annotations whose plugin lives outside core are documented on their plugin pages, because the central page covers only core-shipped annotations. Kubernetes: `backstage.io/kubernetes-id` (matched against a `backstage.io/kubernetes-id` *label* on the cluster resources), `backstage.io/kubernetes-namespace` (restricts lookup), `backstage.io/kubernetes-label-selector` (a `kubectl`-style selector that takes precedence over `-id`), `backstage.io/kubernetes-cluster` (pins one named cluster). PagerDuty: `pagerduty.com/integration-key` (preferred when both are present) and `pagerduty.com/service-id` (alternative with reduced function). Jira keys originate from community plugins, not core (see Open Questions).
- **Field substitutions**: `$text:`, `$json:`, and `$yaml:` embed external file content into a descriptor field.
- **Set automatically (a descriptor MUST NOT author these)**: `backstage.io/managed-by-location`, `backstage.io/managed-by-origin-location`, `backstage.io/orphan`. The catalog derives them during ingestion; authoring them is wrong.
- **Deprecated mappings** a generator MUST avoid: `backstage.io/github-actions-id` → use `github.com/project-slug`; `backstage.io/definition-at-location` → use placeholder substitution (`$text:`/`$json:`/`$yaml:`); `jenkins.io/github-folder` → use `jenkins.io/job-full-name`.

#### Ingestion and onboarding context

A generated descriptor lands in a catalog through one of three ingestion paths. Operating the backend stays a Non-Goal; this context is recorded because it bounds what a generator may assume:

- **Static locations** (`catalog.locations` app-config entries with `type: url` or `type: file`): `file` targets are for local development only, and statically configured locations can't be removed through the catalog API.
- **The register-an-existing-component UI** (`@backstage/plugin-catalog-import`, route `/catalog-import`): paste a descriptor or repository URL, analyse, import. When no descriptor is found the wizard opens a pull request adding an example `catalog-info.yaml` (default filename `catalog-info.yaml`, default PR branch `backstage-integration`); upstream issue #22162 tracks the wizard erroneously opening a PR although a root descriptor already exists.
- **Automatic discovery providers** (`catalog.providers.*`): scheduled entity providers that crawl an organisation, group, or workspace and emit a Location per discovered descriptor.

  | | GitHub | GitLab | Bitbucket Cloud |
  | --- | --- | --- | --- |
  | Provider class | `GithubEntityProvider` | `GitlabDiscoveryEntityProvider` | `BitbucketCloudEntityProvider` |
  | Backend module | `@backstage/plugin-catalog-backend-module-github` | `@backstage/plugin-catalog-backend-module-gitlab` | `@backstage/plugin-catalog-backend-module-bitbucket-cloud` |
  | Config key | `catalog.providers.github.<id>` | `catalog.providers.gitlab.<id>` | `catalog.providers.bitbucketCloud.<id>` |
  | Required scope | `organization` | `host`, `group` | `workspace` |
  | Descriptor path key | `catalogPath` (default `/catalog-info.yaml`, leading slash; `*`/`**` globs) | `entityFilename` (default `catalog-info.yaml`, no slash) | `catalogPath` (default `/catalog-info.yaml`) |
  | Filters | `filters.branch` / `repository` (regex) / `topic` / `visibility`; `allowArchived` (default false) | `branch`, `projectPattern` (regex) | `filters.projectKey` / `filters.repoSlug` (regex) |

- GitHub discovery recommends a schedule frequency around 35 minutes to respect the 5000-requests-per-hour API limit, and integrates with `@backstage/plugin-events-backend-module-github` for webhook-driven updates.
- **`catalog.rules` bounds what a catalog accepts**: the default allow-list admits only the kinds `Component`, `API`, and `Location`; an empty `rules` array rejects everything, and per-location rules can override the global set. A descriptor of any other kind (System, Domain, Group, User, Resource, Template) is rejected at ingestion until the operator extends the rules, so a generator emitting those kinds should surface that operator dependency.
- Entity providers sit at the catalog edge and emit `full` or `delta` mutations (each entity carrying a `locationKey`); processors sit mid-pipeline and can only add or update. Provider-emitted entities must carry `backstage.io/managed-by-location` and `backstage.io/managed-by-origin-location` or they're dropped with warnings; these are the same annotations a hand-authored descriptor MUST NOT contain, because the ingesting machinery adds them.
- Owner resolution presupposes an ingested org graph: `GitHubOrgEntityProvider` (module `@backstage/plugin-catalog-backend-module-github-org`, config `catalog.providers.githubOrg`) turns organisation teams into Group entities and members into User entities.

#### The Tech Radar data model

The Tech Radar is a **standalone frontend plugin**, **not** wired into the Software Catalog and **not** consuming catalog entities. Its entries aren't catalog entities—they carry no `apiVersion`/`kind`/`metadata`/`spec` envelope and are never registered as `catalog-info.yaml`. The two share no data model and no entity references out of the box.

- The data contract a Tech Radar data source **MUST** satisfy is `TechRadarLoaderResponse`, with three required arrays: `quadrants` (`RadarQuadrant[]`), `rings` (`RadarRing[]`), `entries` (`RadarEntry[]`).
- Interface shapes:

  | Interface | Fields |
  | --- | --- |
  | `RadarQuadrant` | `id` (string), `name` (string) |
  | `RadarRing` | `id`, `name`, `color`, `description?` |
  | `RadarEntry` | `key`, `id`, `quadrant` (a quadrant id), `title`, `url?`, `timeline` (`RadarEntrySnapshot[]`), `description?`, `links?` (`RadarEntryLink[]`) |
  | `RadarEntryLink` | `url`, `title` |
  | `RadarEntrySnapshot` | `date` (a JS `Date`), `ringId`, `description?`, `moved?` (`MovedState`) |
  | `enum MovedState` | `Down = -1`, `NoChange = 0`, `Up = 1` |

- **Rings** encode adoption maturity (sample data: `adopt`/`trial`/`assess`/`hold`); **quadrants** encode technology categories (sample data: Languages/Frameworks/Infrastructure/Process). Both are data-driven: ring and quadrant count and names come from the data arrays, not from fixed enums. The original announcement described the ring semantics as: Use/Adopt means recommended for most teams, Trial means evaluated with clear benefits, Assess means worth exploring, Hold means don't invest further; adopt-vs-use is sample-vs-announcement naming drift, and ring names are an org-configurable convention.
- An entry's **current ring isn't a field on the entry**; instead it's derived from the entry's `timeline` snapshots (latest-by-date is the strong, sample-data-backed assumption; the exact selection rule is an Open Question). `date` is a JS `Date` in the in-memory model, so JSON date strings **MUST** be converted (`new Date(...)`) when a custom client loads the data; the backend's Zod parser uses `z.coerce.date()`.
- Wiring: the extension point is `techRadarApiRef` (`interface TechRadarApi { load(id?: string): Promise<TechRadarLoaderResponse> }`). Three sourcing paths exist: the default client (`DefaultTechRadarApi`, fetches `<backend>/data`, validates with `TechRadarLoaderResponseParser`, falls back to mock data on failure); a custom client implementing `TechRadarApi` registered via `createApiFactory(techRadarApiRef, new MyClient())` (takes precedence over a backend when both exist); and the `plugin-tech-radar-backend`, which reads a JSON file from a URL declared under the top-level `techRadar.url` app-config key (through Backstage's URL Reader, so the file can live in a git repository) and serves it at `/data`. The default client attaches an `Authorization: Bearer <idToken>` header when one is available.
- **Package relocation**: as of mid-2026 the plugin lives in `backstage/community-plugins` under the `@backstage-community` scope, split into `plugin-tech-radar` (frontend), `plugin-tech-radar-common` (`model.ts`, `schema.ts`, and `sampleTechRadarResponse.json`, the canonical model source), and `plugin-tech-radar-backend`. The old `@backstage` package name and the old `backstage.io/docs/features/techradar/` URLs are deprecated / 404. A spec or generator **MUST** reference the `@backstage-community` packages.

#### Validation, schema, and the policy chain

- There is **no** official `backstage-cli` subcommand to validate a descriptor on disk (`config:check`/`print`/`schema` apply to app-config, not catalog entities).
- The canonical server-side validation path is `POST <backend>/api/catalog/validate-entity` (for example `http://localhost:7007/api/catalog/validate-entity`; OpenAPI `operationId: ValidateEntity`, auth an optional JWT Bearer token). The JSON request body requires **both** `location` (string) and `entity` (object); note that `location` is in the body, not an HTTP header. Responses: `200` (no body) on success; `400` with `{ "errors": [ { "name", "message" } ] }` on failure. An older docs page renders the path as `POST /entities/validate`; the source-of-truth OpenAPI uses `/validate-entity`.
- The de-facto offline / CI linter is the community `@roadiehq/backstage-entity-validator` (CLI binary `validate-entity`, a `RoadieHQ/backstage-entity-validator` GitHub Action pinned by tag, for example `@v0.3.11`, and a Docker image). It defaults to `catalog-info.yaml` at the repository root, accepts comma-separated lists and globs (flags: `-q` minimal output, `-i` STDIN, `-l` custom schema file), runs Backstage's own structural validation plus well-known-annotation checks, and treats custom schemas as additive (they can only tighten). It **doesn't** check entity-reference target existence.
- Canonical JSON schemas (draft-07) live in `packages/catalog-model/src/schema/` (`Entity`, `EntityEnvelope`, `EntityMeta`, and per-kind files under `kinds/`, plus newer specialised variants such as `API.v1alpha1.mcp-server.schema.json` and the `AiResource.v1alpha1.*` schemas). The default policy chain (`CatalogBuilder.buildEntityPolicy()`) is `allOf(SchemaValidEntityPolicy, DefaultNamespaceEntityPolicy, NoForeignRootFieldsEntityPolicy, FieldFormatEntityPolicy)`.
- `@backstage/catalog-model` exports `entityKindSchemaValidator<T>(schema)` (returns `false` only on a `kind`/`apiVersion` mismatch and throws on any other schema violation) and `entityEnvelopeSchemaValidator()` (envelope presence and shape), both built on `Ajv` draft-07. The field-format validators (`isValidApiVersion`, `isValidKind`, `isValidEntityName`, `isValidNamespace`, `isValidLabelKey`, `isValidLabelValue`, `isValidAnnotationKey`, `isValidAnnotationValue`, `isValidTag`) come from `makeValidator(overrides)` and can be overridden via `CatalogBuilder.setFieldFormatValidators(...)` or, in the new backend system, `catalogModelExtensionPoint.setFieldValidators(...)`.
- A processor signals a broken entity by emitting `generalError`/`inputError` through `processingResult`; the entity is marked invalid and dropped while the prior error-free version is retained, and the errors surface in the entity `status` and in the validate-entity `errors[]`.
- Validation happens in three stages: **ingestion** (coarse: `kind`, `metadata.name`, `metadata.namespace` presence only), **processing** (full schema + policy + field-format + processor emission), and **stitching**. A descriptor that passes ingestion can still be rejected at processing time.

#### Versioning and edition caveats

- Descriptor `apiVersion`: `backstage.io/v1alpha1` for Component, API, Resource, System, Domain, Group, User, Location; `scaffolder.backstage.io/v1beta3` for Template (current).
- Catalog discovery and org-ingestion install via the **new backend system** (`backend.add(import('<module>'))`), replacing the legacy `CatalogBuilder.addEntityProvider()`/`addProcessor()`. A spec/generator targeting onboarding **SHOULD** describe the entity-provider path, not the deprecated discovery-processor path.
- **Frontend-system invariance**: `catalog-info.yaml` content and catalog ingestion config are backend, frontend-agnostic concerns. A generator **MUST NOT** branch on the old-vs-new frontend system when producing a descriptor.

### Generator requirements

These requirements bind the later generator skill. A generator is conformant only when each descriptor it emits also satisfies §The Backstage catalog model.

#### MUST-emit / MAY-emit floor

- For each kind, the generator **MUST** emit the envelope (`apiVersion`, `kind`, valid `metadata.name`, `spec`) plus every `required` `spec` field from the per-kind table, and it **MUST NOT** emit a field the kind doesn't define (notably never `lifecycle` on Resource/System/Domain/Group/User).
- The generator **MUST** emit the empty-but-required keys where they apply: `spec.children: []` on a Group with no known children, `spec.memberOf: []` on a User with no known memberships.
- For Component (the primary target), the MUST floor is: `apiVersion: backstage.io/v1alpha1`, `kind: Component`, a valid `metadata.name`, `spec.type`, `spec.lifecycle`, `spec.owner`. Everything else is MAY.
- For API, the generator **MUST** emit a non-empty `spec.definition`, preferably via a `$text:` placeholder pointing at the discovered spec file rather than inlining the whole document.
- The generator **MAY** emit an optional `spec` field only when it can justify the value from a concrete repository signal (see §Inference); it **MUST NOT** emit a guessed `system`, `dependsOn`, or `domain`.

#### Inference from an existing project

The generator **SHOULD** infer the following from repository signals, and **MUST** record (for example as a comment or a sidecar note) which values were inferred vs. require operator confirmation:

- **`metadata.name`**: slugify the repository/project name, then strip leading/trailing non-alphanumerics and cap at 63 characters so the result satisfies `isValidObjectName`.
- **`spec.type`**: infer from the primary language/structure (`service`/`website`/`library` for Component; `openapi`/`asyncapi`/`graphql`/`grpc` for API), treating the value as a convention, not a fixed enum.
- **`spec.lifecycle`**: default to a conservative value (for example `experimental` or `production`) only with a justifying signal; otherwise flag for operator input.
- **`spec.owner`**: derive from `CODEOWNERS` or a team slug; emit a bare slug only for a Group, and an explicit `user:`-prefixed reference for an individual.
- **APIs**: when an OpenAPI/AsyncAPI/GraphQL/gRPC definition is present, emit an API entity with `spec.definition: { $text: ./<relative-path> }` and add the API to the Component's `providesApis`.
- **Annotations**: emit `github.com/project-slug` (from the remote), `backstage.io/source-location` (`url:.../<repo>/`, trailing slash), and `backstage.io/techdocs-ref: dir:.` when docs are colocated.

#### Fields set automatically that the generator MUST NOT author

- The generator **MUST NOT** author `backstage.io/managed-by-location`, `backstage.io/managed-by-origin-location`, or `backstage.io/orphan` (catalog-derived), nor `metadata.uid`/`metadata.etag` (output-only), nor `relations`/`status` (read-only).
- The generator **MUST NOT** emit any deprecated annotation listed in §Well-known annotations; it uses the replacement instead.

#### Descriptor placement and owner resolution

- The generator **MUST** place the descriptor at the repository root as `catalog-info.yaml`, matching the discovery providers' default path (`catalogPath` `/catalog-info.yaml` for GitHub/Bitbucket, `entityFilename` `catalog-info.yaml` for GitLab).
- The generator **MUST** emit references (especially `owner`) in a form that resolves: it **SHOULD** prefer the full three-part `kind:namespace/name` form for cross-system robustness, and **MUST** use an explicit `user:` prefix for individual owners.
- When an owner can't be confirmed to resolve (no matching Group/User in the target catalog), the generator **MUST** flag it as requiring operator action rather than silently emitting a dangling reference; populating the org graph (Groups/Users) is out of scope (see Non-Goals).

#### Tech Radar generation

- A Tech Radar generator path (optional second target) **MUST** emit a `TechRadarLoaderResponse` JSON file (`quadrants`, `rings`, `entries`) conforming to the §Tech Radar data model, **not** a `catalog-info.yaml`; it **MUST NOT** model radar entries as catalog entities.
- It **MUST** express each entry's ring placement through the entry's `timeline` (a snapshot with `ringId` and a `date`), not as a direct field, and **MUST** emit `date` values a consumer can coerce to a JS `Date`.
- It **SHOULD** target the `@backstage-community` package model and **MUST NOT** reference the deprecated `@backstage` Tech Radar package or the dead `backstage.io/docs/features/techradar/` URLs.

#### Generator self-validation

- The generator **SHOULD** validate every emitted descriptor before presenting it—at minimum against the offline `@roadiehq/backstage-entity-validator` (or an equivalent stdlib check of the schema floor and field-format rules), and **MAY** additionally POST to a running backend's `/api/catalog/validate-entity` when one is reachable.
- The generator **MUST** treat reference-target existence as unverified by the offline validator and surface owner/system/API references as claims to confirm, not as validated facts.

## Acceptance Criteria

- [ ] The spec table lists all nine kinds with their `apiVersion`, required and optional `spec` fields, and convention enums, and a reviewer can derive the MUST floor for any kind from it.
- [ ] A generator built to this spec emits a Component `catalog-info.yaml` whose required floor (`apiVersion`, `kind`, valid `metadata.name`, `spec.type`/`lifecycle`/`owner`) passes `@roadiehq/backstage-entity-validator` with no manual edit.
- [ ] A generated Resource descriptor never contains `spec.lifecycle`; a generated Group descriptor always contains `spec.children` (possibly `[]`); a generated User descriptor always contains `spec.memberOf` (possibly `[]`).
- [ ] A generated `metadata.name` always satisfies `isValidObjectName` (1–63 chars, first/last alphanumeric, interior `[-_.]` only) even when the source repo name has leading/trailing separators.
- [ ] A generated API entity carries a non-empty `spec.definition` supplied via a `$text:` placeholder, and the providing Component lists it under `providesApis`.
- [ ] No generated descriptor authors `backstage.io/managed-by-location`, `backstage.io/managed-by-origin-location`, `backstage.io/orphan`, `metadata.uid`, `metadata.etag`, `relations`, or `status`.
- [ ] No generated descriptor uses a deprecated annotation (`backstage.io/github-actions-id`, `backstage.io/definition-at-location`, `jenkins.io/github-folder`).
- [ ] Numeric- or boolean-looking annotation values in generated descriptors are YAML-quoted strings.
- [ ] An individual owner is emitted with an explicit `user:` prefix; a bare owner reference is only ever used for a Group.
- [ ] The descriptor is written to the repository root as `catalog-info.yaml`.
- [ ] A Tech Radar output (when generated) is a `TechRadarLoaderResponse` JSON file with `quadrants`/`rings`/`entries`, encodes ring placement via the entry `timeline`, references the `@backstage-community` model, and is never modelled as a catalog entity.
- [ ] Inferred field values are distinguishable from operator-confirmation-required values in the generator's output.

## Open Questions

Carried forward from the research pass (see §Sources); each bounds or refines generator behaviour and should be resolved before or during skill authoring.

1. **Template current descriptor**: confirm the full optional `spec` field list (`parameters`, `steps`, `output`, `secrets`, `presentation`) for `scaffolder.backstage.io/v1beta3` against the live `software-templates/writing-templates` docs for the targeted release.
2. **`additionalProperties` on per-kind `spec`**: whether the per-kind JSON schemas set `additionalProperties: false` on `spec` (that is, whether emitting an unknown `spec` field on a known kind is rejected or merely ignored). Governs whether a generator may add custom `spec` fields without a custom kind.
3. **Owner Group/User precedence**: the exact rule when a bare `owner` matches both a Group and a User of the same name in the same namespace (warn vs. silently prefer Group). The generator sidesteps this by always prefixing owners, but the rule should be pinned.
4. **catalog-import app-config keys**: confirm whether the register-component flow keys are `catalog.import.entityFilename` (default `catalog-info.yaml`) and `catalog.import.pullRequestBranchName` (default `backstage-integration`), against `plugin-catalog-import` source.
5. **`validate-entity` scope**: whether the endpoint runs the full custom-processor chain or only envelope + kind schema + default policies (that is, whether reference-target existence and custom-kind validity are checked there).
6. **First-party offline validator**: whether any current `@backstage/cli`/`@backstage/repo-tools` version ships an offline `catalog-info.yaml` validate subcommand (none found at research time).
7. **`validate-entity` `location` semantics**: confirmed required in the JSON body; confirm no version also accepts/requires an HTTP `Location` header.
8. **New-vs-legacy extension migration**: whether `CatalogBuilder.setFieldFormatValidators`/`addProcessor` are deprecated in favour of `catalogModelExtensionPoint.setFieldValidators` / `catalogProcessingExtensionPoint.addProcessor` for the targeted release.
9. **Enumerated validation error messages**: the exact wording emitted by `SchemaValidEntityPolicy` / `NoForeignRootFieldsEntityPolicy` / `FieldFormatEntityPolicy`, useful for the generator's self-validation reporting.
10. **Relation array element schema**: the exact schema of a `relations[]` element (string `targetRef` vs. structured `target {kind,namespace,name}`); off-limits to authoring, but relevant to reading existing descriptors.
11. **Jira annotation keys**: confirm whether `jira/project-key`, `jira/component` originate from a specific community plugin (for example RoadieHQ) rather than core.
12. **Status model instability**: additional status types beyond `backstage.io/catalog-processing` may exist in newer releases; the status format is explicitly in-development. Annotation introduction/deprecation release versions are unpinned.
13. **`metadata.title`/`description` length caps**: not stated upstream; only `name`, `namespace`, label/annotation keys, tags, and icons carry explicit constraints.
14. **Source-annotation automatic population**: which processor (likely `AnnotateLocationEntityProcessor`) derives `source-location`/`edit-url`/`view-url`/`project-slug` automatically when reading from a GitHub URL vs. which must be hand-authored. Bounds which annotations the generator should emit vs. leave to the catalog.
15. **GitLab/Bitbucket onboarding specifics**: `useSearch`, `catalogFile` vs. `entityFilename`, subgroup handling, `GitlabFillerProcessor`, and whether they default to the repo default branch like GitHub.
16. **Tech Radar per-item Zod field rules**: stricter constraints (color regex, non-empty, whether `links` is validated) in `plugin-tech-radar-common/src/schema.ts`, read line-by-line.
17. **Tech Radar backend refresh/headers**: whether `plugin-tech-radar-backend` supports a refresh/schedule or custom request headers/caching for `techRadar.url`; app-config keys beyond `techRadar.url`.
18. **Tech Radar canonical docs location**: whether backstage.io still hosts a Tech Radar feature page under a relocated path, or whether canonical docs live only in the community-plugins README.
19. **Tech Radar current-ring selection rule**: confirm latest-by-date selection and tie/ordering handling from the rendering component source.

## Sources

The 2026-06-07 research pass (146 sources over `backstage.io/docs` and the `backstage/backstage` and `backstage/community-plugins` source trees) grounds this spec. The load-bearing URLs, grouped:

**Software Catalog: descriptor format, system model, references**

- <https://backstage.io/docs/features/software-catalog/descriptor-format>
- <https://backstage.io/docs/features/software-catalog/system-model>
- <https://backstage.io/docs/features/software-catalog/references>
- <https://backstage.io/docs/features/software-catalog/well-known-relations>

**Well-known annotations and statuses**

- <https://backstage.io/docs/features/software-catalog/well-known-annotations>
- <https://backstage.io/docs/features/software-catalog/well-known-statuses>
- <https://backstage.io/docs/features/kubernetes/configuration/>
- <https://pagerduty.github.io/backstage-plugin-docs/getting-started/backstage/>

**Catalog onboarding, configuration, integrations**

- <https://backstage.io/docs/features/software-catalog/configuration>
- <https://backstage.io/docs/features/software-catalog/external-integrations>
- <https://backstage.io/docs/integrations/github/discovery>
- <https://backstage.io/docs/integrations/gitlab/discovery>
- <https://backstage.io/docs/integrations/bitbucketCloud/discovery>
- <https://backstage.io/docs/integrations/github/org>
- <https://backstage.io/docs/getting-started/register-a-component/>

**Tech Radar (community-plugins workspace `tech-radar`)**

- <https://github.com/backstage/community-plugins/tree/main/workspaces/tech-radar/plugins/tech-radar>
- <https://github.com/backstage/community-plugins/blob/main/workspaces/tech-radar/plugins/tech-radar/README.md>
- <https://github.com/backstage/community-plugins/blob/main/workspaces/tech-radar/plugins/tech-radar-backend/README.md>
- `plugin-tech-radar-common` sources: `src/model.ts`, `src/schema.ts`, `src/sampleTechRadarResponse.json`
- <https://backstage.io/blog/2020/05/14/tech-radar-plugin/>
- <https://www.npmjs.com/package/@backstage-community/plugin-tech-radar>

**Validation, schema, tooling**

- <https://backstage.io/docs/features/software-catalog/software-catalog-api/>
- <https://github.com/backstage/backstage/blob/master/plugins/catalog-backend/src/schema/openapi.yaml>
- <https://backstage.io/docs/tooling/cli/commands/>
- <https://github.com/backstage/backstage/tree/master/packages/catalog-model/src/schema>
- `packages/catalog-model/src/validation/` sources: `KubernetesValidatorFunctions.ts`, `CommonValidatorFunctions.ts`, `makeValidator.ts`
- <https://github.com/backstage/backstage/blob/master/plugins/catalog-backend/src/service/CatalogBuilder.ts>
- <https://backstage.io/docs/features/software-catalog/extending-the-model/>
- <https://backstage.io/docs/features/software-catalog/life-of-an-entity>
- <https://github.com/RoadieHQ/backstage-entity-validator>

**Frontend-system invariance**

- <https://backstage.io/docs/frontend-system/building-apps/migrating/>
- <https://backstage.io/docs/features/software-catalog/catalog-customization/>
