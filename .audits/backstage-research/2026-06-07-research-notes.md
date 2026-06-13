# Backstage Software Catalog & Tech Radar — Research Notes

## 1. Executive summary

Backstage's Software Catalog models software and organizations as YAML "entities" that share a common Kubernetes-style envelope (`apiVersion`, `kind`, `metadata`, `spec`, plus read-only `relations` and `status`) [1]. The kernel comprises nine core kinds: **Component, API, Resource, System, Domain, Group, User, Location, and Template**. Core software/ecosystem kinds carry an open-ended `spec.type`; Component and API additionally carry `spec.lifecycle`; almost all carry a required `spec.owner` [1][3]. Inter-entity links are declared in `spec` fields using string entity references of the form `[<kind>:][<namespace>/]<name>`; the catalog processor derives bidirectional, read-only `relations` (e.g. `ownedBy`/`ownerOf`, `partOf`/`hasPart`) [1][2][5].

A critical correction from source: `spec.type` and `spec.lifecycle` enums are **conventions, not enforced enums** — extensible per organization [1][3]. The per-kind JSON schemas enforce only the `required` field arrays and string/array shapes; reference grammar is validated downstream during processing [16][17].

The **Tech Radar** is a separate, standalone frontend plugin that is **not** wired into the catalog and does **not** consume catalog entities — it consumes its own `TechRadarLoaderResponse` JSON model (quadrants/rings/entries) [11][12]. As of mid-2026 it lives in `backstage/community-plugins` under the `@backstage-community` scope; the old seed URLs 404 [13].

Validation happens at multiple layers. There is **no** official `backstage-cli` subcommand to validate a descriptor on disk [8]; the canonical server-side path is `POST /api/catalog/validate-entity` [6], and the de-facto offline/CI linter is the community `@roadiehq/backstage-entity-validator` [10].

For a catalog-info.yaml-generation skill, the MUST/MAY floor is now derivable per kind from the JSON-schema `required` arrays; entity-name validation is stricter than the prose form (first and last char must be alphanumeric) [16]. Crucially, the old-vs-new frontend system does **not** affect catalog-info.yaml or ingestion config — both are backend, frontend-agnostic concerns [15].

## 2. Software Catalog system model (entity kernel)

### 2.1 Entity envelope (common to all kinds)

Every entity is a YAML object with four authored root fields plus two read-only/output-only fields [1]:

| Field | Type | Notes |
| --- | --- | --- |
| `apiVersion` | string | Required. Together with `kind`, enough for a parser to interpret the contents. |
| `kind` | string | Required. Capitalized kind name (e.g. `Component`). |
| `metadata` | object | Common to all kinds (see §3). |
| `spec` | object | Kind-specific. |
| `relations` | array of `{type, targetRef}` | **Read-only**, derived by the catalog processor — never authored. |
| `status` | object with `items[]` of `{type, level, message, error?}` | **Read-only**; common type `backstage.io/catalog-processing`; `level` ∈ `info`/`warning`/`error`. |

### 2.2 apiVersion strings per kind

- Component, API, Group, User, Resource, System, Domain, Location → `backstage.io/v1alpha1` [1][2].
- Template → `scaffolder.backstage.io/v1beta3` (current). Older docs/tables show `backstage.io/v1beta2`; the original `backstage.io/v1alpha1` scaffolder format is deprecated [16][18].

### 2.3 Per-kind required/optional spec, enums, and relations

#### Component

apiVersion `backstage.io/v1alpha1`, kind `Component` [1].

| | Field | Notes |
| --- | --- | --- |
| Required | `type` | Recommended values: `service`, `website`, `library` (extensible) |
| Required | `lifecycle` | Recommended: `experimental`, `production`, `deprecated` (extensible) |
| Required | `owner` | Ref to Group or User |
| Optional | `system` | Ref to System |
| Optional | `subcomponentOf` | Ref to parent Component |
| Optional | `providesApis` | Array of API refs |
| Optional | `consumesApis` | Array of API refs |
| Optional | `dependsOn` | Array of Component/Resource refs |
| Optional | `dependencyOf` | Array of Component/Resource refs |

JSON schema: `owner`, `system`, `subcomponentOf` are `string` with `minLength: 1`; `providesApis`, `consumesApis`, `dependsOn`, `dependencyOf` are arrays of `string` (each item `minLength: 1`), **no regex pattern** on the items [16].

Derived relations: `ownedBy` (→owner), `partOf` (→System and/or parent Component), `hasPart` (inverse), `providesApi`/`consumesApi` (→API), `dependsOn`/`dependencyOf` [1][2].

#### API

apiVersion `backstage.io/v1alpha1`, kind `API` [1].

| | Field | Notes |
| --- | --- | --- |
| Required | `type` | Recommended: `openapi`, `asyncapi`, `graphql`, `grpc` (extensible) |
| Required | `lifecycle` | Same enum as Component |
| Required | `owner` | Ref to Group/User |
| Required | `definition` | The actual API spec; `string`, `minLength: 1` — see note |
| Optional | `system` | Ref to System |

`spec.definition` is **required** and is a plain string; it is typically supplied via placeholder substitution (`$text:` pointing at a relative file path) which the catalog inlines at processing time (the documented replacement for the deprecated `backstage.io/definition-at-location` annotation). An API entity is not schema-valid without a non-empty `definition` [16].

Derived relations: `ownedBy`, `partOf` (→System), `apiProvidedBy` (inverse of a Component's `providesApi`), `apiConsumedBy` (inverse of `consumesApi`) [1][2].

#### Resource

apiVersion `backstage.io/v1alpha1`, kind `Resource`. Represents runtime infrastructure (databases, S3 buckets, Pub/Sub topics, CDNs, Kubernetes clusters) [1][3].

| | Field | Notes |
| --- | --- | --- |
| Required | `type` | NO fixed enum; org-defined. Examples: `database`, `s3-bucket`, `kubernetes-cluster` |
| Required | `owner` | |
| Optional | `system` | Ref to System |
| Optional | `dependsOn` | Array of refs |
| Optional | `dependencyOf` | Array of refs |

**Resource has NO `lifecycle` field** — confirmed against the Resource v1alpha1 schema (`required: [type, owner]`, no `lifecycle` property anywhere). This closes the prior open question [16].

Derived relations: `ownedBy`, `partOf` (→System), `dependsOn`/`dependencyOf` [1][3].

#### System

apiVersion `backstage.io/v1alpha1`, kind `System`. A collection of Components and Resources exposing one or more public APIs, hiding implementation [1][3].

| | Field | Notes |
| --- | --- | --- |
| Required | `owner` | |
| Optional | `domain` | Ref to Domain |
| Optional | `type` | No fixed enum; examples `product`, `service`, `feature-set` |

No `lifecycle`. Derived relations: `ownedBy`, `partOf` (→Domain), `hasPart` (inverse — Components/Resources/APIs whose `spec.system` points here) [1][3].

#### Domain

apiVersion `backstage.io/v1alpha1`, kind `Domain`. Groups Systems sharing terminology, domain models, business purpose [1][3].

| | Field | Notes |
| --- | --- | --- |
| Required | `owner` | |
| Optional | `subdomainOf` | Ref to parent Domain (nested domains) |
| Optional | `type` | No fixed enum; examples `product-area`, `product-group`, `bundle` |

No `lifecycle`. Derived relations: `ownedBy`, `hasPart` (inverse — Systems whose `spec.domain` points here), `parentOf`/`childOf` (via `subdomainOf`) [1][3].

#### Group

apiVersion `backstage.io/v1alpha1`, kind `Group`. An org entity (team, business unit) [1][2].

| | Field | Notes |
| --- | --- | --- |
| Required | `type` | No fixed enum; examples `team`, `business-unit`, `product-area`, `root` |
| Required | `children` | List of Group refs; **may be empty `[]` but the key MUST be present** |
| Optional | `profile` | `{displayName, email, picture}` |
| Optional | `parent` | Ref to parent Group |
| Optional | `members` | List of User refs |

Derived relations: `parentOf`/`childOf` (Group↔Group), `hasMember` (→Users; inverse of `User.memberOf`), `ownerOf` [1][2].

#### User

apiVersion `backstage.io/v1alpha1`, kind `User`. A person [1][2].

| | Field | Notes |
| --- | --- | --- |
| Required | `memberOf` | List of Group refs; **may be empty `[]` but the key MUST be present** |
| Optional | `profile` | `{displayName, email, picture}` |

No type/lifecycle/owner. Derived relations: `memberOf` (→Group), `ownerOf` [1][2].

#### Location

apiVersion `backstage.io/v1alpha1`, kind `Location`. A marker pointing the catalog to other places to read entity data (NOT a real-world thing) [1].

| | Field | Notes |
| --- | --- | --- |
| Optional | `type` | e.g. `url` / `file`; inherited from parent location if omitted |
| Optional | `target` | Single string target, relative or absolute |
| Optional | `targets` | List of target strings |
| Optional | `presence` | `required` / `optional` (default `required`) — controls whether a missing target is an error |

Use `target` OR `targets`. Locations spawn entities, recorded via `backstage.io/managed-by-location` annotations [1].

#### Template (version caveat)

apiVersion `scaffolder.backstage.io/v1beta3`, kind `Template` [18].

| | Field | Notes |
| --- | --- | --- |
| Required | `type` | |
| Required | `owner` | |
| Optional | `parameters` | Form step(s) — JSON Schema with `ui:`-prefixed extensions |
| Optional | `steps` | Array of scaffolder actions executed sequentially |
| Optional | `output` | Links/text shown on completion |
| Optional | `secrets` | Schema for programmatically passed secrets |
| Optional | `presentation` | Button-label customization |

**Correction:** required spec is **only `type` and `owner`** — not `type` + `parameters` + `steps` as some older summaries claim [18]. Notable optional metadata annotation: `backstage.io/time-saved` (ISO-8601 duration, e.g. `PT4H`). Template lives in the catalog but is consumed by the Scaffolder plugin; it is not part of the software-entity relations graph in the same way.

### 2.4 Well-known relations (full paired list)

Derived, read-only relation **type strings** (always bidirectional pairs) [2][3]:

| Forward | Reverse | Edge (typical) |
| --- | --- | --- |
| `ownedBy` | `ownerOf` | any entity ↔ User/Group |
| `partOf` | `hasPart` | Component→Component, Component/API/Resource→System, System→Domain, Domain→Domain |
| `dependsOn` | `dependencyOf` | any ↔ any |
| `providesApi` | `apiProvidedBy` | Component or System ↔ API |
| `consumesApi` | `apiConsumedBy` | Component or System ↔ API |
| `parentOf` | `childOf` | Group↔Group; Domain↔Domain (via `subdomainOf`) |
| `memberOf` | `hasMember` | User↔Group |

**Naming asymmetry to preserve:** `spec`-field names are plural (`providesApis`, `consumesApis`, `memberOf`) but the derived relation type strings are singular (`providesApi`, `consumesApi`). The system-model overview page loosely uses `implementsApi`/`exposesApi`, but the canonical type strings on the well-known-relations page are `providesApi`/`consumesApi`/`apiProvidedBy`/`apiConsumedBy` [2][3].

### 2.5 Entity reference format

References in `spec` fields are strings `[<kind>:][<namespace>/]<name>` (1–3 parts) [5]. Defaults when a part is omitted: kind inferred from field context; namespace falls back to `default`. Examples: `group:pet-managers` → `group:default/pet-managers`; `internal/streetlights` in `providesApis` → `api:internal/streetlights`; bare `hello-world` in `providesApis` → `api:default/hello-world`. A compound object form `{ kind, namespace, name }` also exists. Recommendation: cross-system communication should use the full three-part string form; `relations[].targetRef` always uses the full normalized form [5][1].

#### Exact per-field default-kind table

| Field | Default kind when prefix omitted |
| --- | --- |
| `owner` | Group (may be User — see disambiguation) |
| `system` | System |
| `subcomponentOf` | Component |
| `providesApis` | API |
| `consumesApis` | API |
| `dependsOn` | Component (on a Component); Component or Resource (on a Resource) |
| `dependencyOf` | same as `dependsOn` |
| `domain` (System) | Domain |
| `subdomainOf` (Domain) | Domain |
| `parent` (Group) | Group |
| `children` (Group) | Group |
| `members` (Group) | User |
| `memberOf` (User) | Group |

Namespace always defaults to `default`. **Owner disambiguation:** `owner` accepts both Group and User, but a bare reference defaults to **Group**, so to point owner at a person a generator MUST emit an explicit `user:`-prefixed reference; a bare `owner` resolves to a Group and dangles if only a User of that name exists [1][5].

## 3. The catalog-info.yaml descriptor format

### 3.1 Envelope and multi-entity files

Four root keys: `apiVersion`, `kind`, `metadata`, `spec` [1][4]. Multiple entities live in one file using the standard YAML document separator `---` between each block [4].

### 3.2 Metadata block

| Field | Required? | Format / notes |
| --- | --- | --- |
| `name` | **Required** | See naming constraints below |
| `namespace` | Optional | Default `default` |
| `uid` | Output-only | Globally unique, generated |
| `etag` | Output-only | Generated |
| `title` | Optional | Free display string |
| `description` | Optional | Human-readable summary |
| `labels` | Optional | Key→value map (see below) |
| `annotations` | Optional | Key→value map; values arbitrary strings |
| `tags` | Optional | List of single-valued strings |
| `links` | Optional | Array of `{url(req), title, icon, type}` |
| `relations` | Read-only | Array of `{targetRef, type}` |
| `status` | Read-only | Object with `items[]` of `{type, level, message, error?}` |

`links` icon format: `[a-z0-9A-Z]` possibly separated by one of `[-_.]`. Example link entry: `- url: https://admin.example-org.com / title: Admin Dashboard / icon: dashboard / type: admin-dashboard` [1].

### 3.3 Naming and format constraints (corrected from source)

**`metadata.name`** — the canonical validator `KubernetesValidatorFunctions.isValidObjectName` matches an optional leading run that **starts with an alphanumeric**, may contain `[-_.]` or alphanumerics interiorly, and **always ends in an alphanumeric**, length **1–63** [16]. This is stricter than the prose "alphanumerics separated by `[-_.]`":
- First and last character MUST be alphanumeric.
- Separators `[-_.]` are allowed only interiorly.
- A length-1 name must be a single alphanumeric.
- A leading or trailing separator is **invalid**.

Names are case-insensitively unique per `(kind, namespace)`. Mixed case is allowed by the default rule; the lowercase-and-dashes advice in the Spotify onboarding guide is stylistic, not enforced [16][1].

**`metadata.namespace`** (`isValidNamespace` → `isValidDnsLabel`): lowercase alphanumerics in hyphen-separated groups, length 1–63, **no underscore, no dot, no uppercase** — stricter than name [15][16].

**Label keys** (`isValidLabelKey`): optional DNS-subdomain prefix (≤253 chars) + `/` + a required name part (same rule as entity name). `backstage.io/` prefix reserved. **Label values**: empty string OR the entity-name rule [1][16]. Example: `example.com/custom: custom_label_value`.

**Annotation keys**: same key format as labels (optional ≤253-char prefix + `/` + ≤63-char name part). **Annotation values** (`isValidAnnotationValue`): **arbitrary strings, any length, any charset** — only a `typeof string` check [4][16]. Consequence: numeric or boolean-looking values MUST be YAML-quoted to remain strings (e.g. `backstage.io/orphan: 'true'`, `github.com/user-id: '123456'`).

**`tags`**: lowercase `[a-z0-9:+#]` inside groups, hyphen-separated, length 1–63; regex `^[a-z0-9:+#]+(\-[a-z0-9:+#]+)*$` [16][4].

### 3.4 Fully annotated Component example (verbatim)

```yaml
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: artist-web
  description: The place to be, for great artists
  labels:
    example.com/custom: custom_label_value
  annotations:
    example.com/service-discovery: artistweb
    circleci.com/project-slug: github/example-org/artist-website
  tags:
    - java
  links:
    - url: https://admin.example-org.com
      title: Admin Dashboard
      icon: dashboard
      type: admin-dashboard
spec:
  type: website
  lifecycle: production
  owner: artist-relations-team
  system: public-websites
```

Component `spec` with all relationship fields (verbatim) [1]:

```yaml
spec:
  type: website
  lifecycle: production
  owner: artist-relations-team
  system: artist-engagement-portal
  subcomponentOf: spotify-ios-app
  providesApis:
    - artist-api
  consumesApis:
    - artist-api
  dependsOn:
    - resource:default/artists-db
  dependencyOf:
    - component:default/artist-web-lookup
```

## 4. Well-known annotations & labels

Backstage documents three "well-known" registries: annotations, relations (§2.4), and statuses (§7). Keys SHOULD be namespaced; `backstage.io/*` is reserved for things Backstage itself ships; integration annotations are namespaced by the integrating system's domain [4][5]. **Kubernetes, PagerDuty, and Jira annotations are NOT on the central annotations page** — they live on their respective plugin pages, because the central page covers only core-shipped annotations [5][7].

| Key | Value format / example | Purpose | Source |
| --- | --- | --- | --- |
| `backstage.io/managed-by-location` | `url:http://github.com/.../catalog-info.yaml` | Source location the entity was fetched from (auto-set) | [5] |
| `backstage.io/managed-by-origin-location` | same format | Root of the location chain that created the entity (auto-set) | [5] |
| `backstage.io/orphan` | `'true'` (quoted) | Catalog-set when no active location references the entity | [5] |
| `backstage.io/source-location` | `url:https://github.com/my-org/my-service/` (trailing slash for dir) | Points at source-code root | [5] |
| `backstage.io/view-url` | URL | Canonical view URL for the entity file | [5] |
| `backstage.io/edit-url` | URL | Source-edit URL | [5] |
| `backstage.io/source-template` | `template:default/create-react-app-template` | Scaffolder Template the entity was created from | [5] |
| `backstage.io/techdocs-ref` | `dir:.` or `url:` reference | Where TechDocs source lives | [5] |
| `backstage.io/techdocs-entity` | `component:default/example` | External entity owning the docs | [5] |
| `backstage.io/techdocs-entity-path` | `/path/to/this/component` | Path within that external entity's docs | [5] |
| `backstage.io/code-coverage` | `scm-only` / `enabled` | Code-coverage plugin | [5] |
| `github.com/project-slug` | `backstage/backstage` (org/repo) | Wires GitHub features | [5] |
| `github.com/team-slug` | `backstage/maintainers` (org/team) | GitHub team mapping | [5] |
| `github.com/user-login` | `freben` | GitHub user login | [5] |
| `github.com/user-id` | `'123456'` (quoted, immutable) | GitHub numeric user id | [5] |
| `gitlab.com/user-id` | `'123456'` (quoted) | GitLab numeric user id | [5] |
| `gitlab.com/project-slug` | org/repo form | GitLab project (mentioned in onboarding) | [9] |
| `graph.microsoft.com/tenant-id` etc. | string | Microsoft Graph (Entra/Azure AD) | [5] |
| `jenkins.io/job-full-name` | `folder-name/job-name` | Full Jenkins job path | [5] |
| `gocd.org/pipelines` | `backstage,backstage-pr,...` (comma-sep) | GoCD pipelines | [5] |
| `circleci.com/project-slug` | `github/spotify/pump-station` | CircleCI project | [5] |
| `sonarqube.org/project-key` | `pump-station` | SonarQube/SonarCloud | [5] |
| `sentry.io/project-slug` | `backstage/pump-station` | Sentry | [5] |
| `rollbar.com/project-slug` | `backstage/pump-station` | Rollbar | [5] |
| `periskop.io/service-name` | `pump-station` | Periskop | [5] |
| `vault.io/secrets-path` | `test/backstage` | Vault | [5] |
| `backstage.io/ldap-rdn`, `-uuid`, `-dn` | string | LDAP | [5] |

**Deprecated annotations** [5]:

| Deprecated | Replacement |
| --- | --- |
| `backstage.io/github-actions-id` | `github.com/project-slug` |
| `backstage.io/definition-at-location` | placeholder substitution (`$text`/`$json`/`$yaml`) |
| `jenkins.io/github-folder` | `jenkins.io/job-full-name` |

**Plugin-page annotations (not core)** [7]:

| Key | Example | Notes | Source |
| --- | --- | --- | --- |
| `backstage.io/kubernetes-id` | `dice-roller` | Matched against a `backstage.io/kubernetes-id` LABEL on K8s resources | [7] |
| `backstage.io/kubernetes-namespace` | `dice-space` | Restricts lookup to a namespace | [7] |
| `backstage.io/kubernetes-label-selector` | `'app=my-app,component=front-end'` | kubectl-style selector; **takes precedence over `-id`** | [7] |
| `backstage.io/kubernetes-cluster` | `dice-cluster` | Pins to one named cluster (singleTenant) | [7] |
| `pagerduty.com/integration-key` | Events API v2 key | Links entity to PagerDuty service; preferred when both present | [7a] |
| `pagerduty.com/service-id` | PagerDuty service ID | Alternative; 'Create Incident' disabled by default with this alone | [7a] |

**Field substitutions in descriptors:** `$text:`, `$json:`, `$yaml:` embed external file content [1][5].

## 5. Onboarding existing projects into the catalog

### 5.1 Three ingestion paths

1. **Static `catalog.locations`** — declarative app-config entries, each with `type` (`url` for remote YAML behind a configured integration; `file` for local paths, dev/testing only) and `target`. The global `catalog.rules` key controls allowed kinds (default allowed: `Component`, `API`, `Location`; empty `rules` array rejects all). Per-location rules can override. Statically configured locations cannot be removed via the catalog API [19].
2. **Register an existing component UI** (`@backstage/plugin-catalog-import`, route `/catalog-import`) — paste a descriptor URL or repo root URL → ANALYZE → IMPORT. When entities are found they are added as Locations; when none are found, the plugin **opens a PR adding an example `catalog-info.yaml`**. Configurable entity filename (default `catalog-info.yaml`) and PR branch (default `backstage-integration`). Known issue #22162: the wizard can erroneously open a PR even when a root descriptor already exists [21].
3. **Automatic discovery entity providers** (`catalog.providers.*`) — crawl an org/group/workspace on a schedule and emit a Location per discovered `catalog-info.yaml`.

### 5.2 Discovery vs. static, providers vs. processors

`catalog.locations` are static, config-driven, immutable-via-API sources. `catalog.providers.*` are integration-driven discovery mechanisms (entity providers). An **EntityProvider** sits at the catalog edge, runs decoupled (scheduled/webhook), and emits mutations via `connection.applyMutation()` with type `full` (replace whole bucket) or `delta` (per-entity upsert/delete); each mutation entity carries a `locationKey`. A **CatalogProcessor** sits mid-pipeline, runs on a fixed loop, can only upsert. Base classes come from `@backstage/plugin-catalog-node`; registered via `builder.addEntityProvider()` / `builder.addProcessor()` (legacy) or the new backend system. All provider-emitted entities must carry `backstage.io/managed-by-location` and `backstage.io/managed-by-origin-location` or they are dropped with warnings [20].

### 5.3 GitHub / GitLab / Bitbucket Cloud providers

| | GitHub | GitLab | Bitbucket Cloud |
| --- | --- | --- | --- |
| Provider class | `GithubEntityProvider` | `GitlabDiscoveryEntityProvider` | `BitbucketCloudEntityProvider` |
| Backend module | `@backstage/plugin-catalog-backend-module-github` | `@backstage/plugin-catalog-backend-module-gitlab` | `@backstage/plugin-catalog-backend-module-bitbucket-cloud` |
| Config key | `catalog.providers.github.<id>` | `catalog.providers.gitlab.<id>` | `catalog.providers.bitbucketCloud.<id>` |
| Required scope | `organization` | `host`, `group` | `workspace` |
| Descriptor path key | `catalogPath` (default `/catalog-info.yaml`, leading slash; supports `*`/`**`) | `entityFilename` (default `catalog-info.yaml`, **no slash**) | `catalogPath` (default `/catalog-info.yaml`) |
| Filters | `filters.branch`/`repository`(regex)/`topic`/`visibility`; `allowArchived` (default false) | `branch`, `projectPattern` (regex) | `filters.projectKey` (regex), `filters.repoSlug` (regex) |
| Schedule | `schedule.frequency`/`timeout`/`initialDelay`/`scope` (required) | `schedule` | `schedule` |

GitHub recommended frequency ~35 min to respect the 5000 req/hr limit; integrates with `@backstage/plugin-events-backend-module-github` for webhooks [22][23][24]. **Naming asymmetry:** GitHub/Bitbucket use `catalogPath` (leading slash), GitLab uses `entityFilename` (no slash).

### 5.4 Minimal-viable Component and `catalog-info.yaml` convention

Convention: a `catalog-info.yaml` at the **repo root** (matching the discovery default `catalogPath /catalog-info.yaml`). Minimal functional Component: `apiVersion: backstage.io/v1alpha1`, `kind: Component`, `metadata.name`, `spec.type`, `spec.lifecycle`, `spec.owner` (optional `spec.system`) [1][20].

### 5.5 Owner resolution and ingesting Groups/Users

`spec.owner` is a string reference `[kind:][namespace/]name`; omitted kind defaults to **Group**, omitted namespace to `default`. So `owner: artist-relations-team` → `group:default/artist-relations-team`; a person is `owner: user:default/jdoe`. Resolution succeeds **only if a matching Group/User entity already exists** — owners are validated references, not free text that auto-creates groups [1].

To make owners resolve, ingest Groups/Users from the SCM org. GitHub: `GitHubOrgEntityProvider`, module `@backstage/plugin-catalog-backend-module-github-org`, config under `catalog.providers.githubOrg` (list of `{id, githubUrl, orgs, schedule.initialDelay/frequency/timeout}`). Org teams become Group entities; org members become User entities [25].

### 5.6 Annotations that make an onboarded Component fully functional

`backstage.io/managed-by-location` and `-origin-location` (auto-set on ingestion); `backstage.io/source-location` (`url:.../my-service/` with trailing slash); `github.com/project-slug` (`org/repo`, GitLab equivalent `gitlab.com/project-slug`); `backstage.io/techdocs-ref` (`dir:.`); `backstage.io/techdocs-entity`; `backstage.io/view-url` / `backstage.io/edit-url` [5].

### 5.7 Version caveat (backend system)

Current discovery/org providers install via the **new backend system** (`backend.add(import('<module>'))` in `packages/backend/src/index.ts`), replacing the legacy `builder.addEntityProvider()` / `builder.addProcessor()` against a `CatalogBuilder`. Earlier GitHub onboarding used a discovery **processor** (`GithubDiscoveryProcessor`) rather than the current `GithubEntityProvider`; specs should target the entity-provider path [22][20].

## 6. Tech Radar

### 6.1 What it visualizes

A standalone Zalando-style radar that summarizes an organization's technology choices [12]. Entries are placed in concentric **rings** (adoption maturity) across **quadrants** (technology categories); each entry carries a **timeline** of snapshots so its **movement** between rings over time is shown.

### 6.2 Rings, quadrants, and data-driven naming

- **Rings** (sample data, four, `id`/`name`/`color`): ADOPT (`adopt`, `#5BA300`), TRIAL (`trial`, `#009EB0`), ASSESS (`assess`, `#C7BA00`), HOLD (`hold`, `#E09B96`). Ring count/names are data-driven via the `rings` array. The 2020 announcement blog used Use/Trial/Assess/Hold (Use = recommended for most teams; Trial = evaluated with clear benefits; Assess = potential; Hold = don't invest further) — adopt-vs-use is a sample/version naming drift; ring names are an org-configurable convention [11][12].
- **Quadrants** (sample data, four, `id`/`name`): Languages, Frameworks, Infrastructure, Process. Data-driven via the `quadrants` array; the frontend README notes data should contain four quadrants; the 2020 blog says organizations pick whatever works best [11][12][14].

### 6.3 Data interfaces (TypeScript model, from `plugin-tech-radar-common/src/model.ts`)

`TechRadarLoaderResponse` (top-level shape the `TechRadarApi.load()` must resolve to) has three required arrays: `quadrants` (`RadarQuadrant[]`), `rings` (`RadarRing[]`), `entries` (`RadarEntry[]`) [11a].

| Interface | Fields |
| --- | --- |
| `RadarEntry` | `key` (string), `id` (string), `quadrant` (string id), `title` (string), `url?` (string), `timeline` (`RadarEntrySnapshot[]`), `description?` (string), `links?` (`RadarEntryLink[]`) |
| `RadarRing` | `id` (string), `name` (string), `color` (string), `description?` (string) |
| `RadarQuadrant` | `id` (string), `name` (string) |
| `RadarEntryLink` | `url` (string), `title` (string) |
| `RadarEntrySnapshot` | `date` (Date), `ringId` (string), `description?` (string), `moved?` (`MovedState`) |
| `enum MovedState` | `Down = -1`, `NoChange = 0`, `Up = 1` |

Precision notes: an entry's **ring placement is NOT a field on the entry** — it is derived from the timeline snapshots (latest-by-date is the strong assumption — see Open questions). `date` is a JS `Date` object in the in-memory model, so raw JSON date strings (e.g. `2020-08-06`) must be converted to `Date` when loading [11a][11].

### 6.4 Validation schema (zod, `src/schema.ts`)

`TechRadarLoaderResponseParser` is a `z.object` with `quadrants = z.array(RadarQuadrantParser)`, `rings = z.array(RadarRingParser)`, `entries = z.array(RadarEntryParser)`. Snapshot validation: `date = z.coerce.date()` (JSON date strings coerced), `ringId = string`, `description` optional string, `moved = z.nativeEnum(MovedState).optional()` [11b].

### 6.5 Custom data source wiring

The extension point is `techRadarApiRef` (`createApiRef`, id `plugin.techradar.service`); `interface TechRadarApi` has a single method `load(id: string | undefined): Promise<TechRadarLoaderResponse>`. The `id` is the optional prop on `TechRadarComponent`/`TechRadarPage` for distinguishing multiple radars [12a].

- **Default**: `DefaultTechRadarApi` discovers the backend base URL via `discoveryApi.getBaseUrl('tech-radar')`, fetches `apiUrl + /data` (with `Authorization: Bearer <idToken>` when available), validates with `TechRadarLoaderResponseParser.safeParse(...)`; on validation failure OR a missing backend it returns hardcoded MOCK data (e.g. `new Date('2020-08-06')`) [12a][14].
- **Custom client**: implement `TechRadarApi` (e.g. `class MyOwnClient implements TechRadarApi`), fetch a JSON URL, spread the data and map each entry's `timeline` to convert `timeline.date` via `new Date(timeline.date)` (mandatory because the model `date` is a `Date`), and register in `app/src/apis.ts` via `createApiFactory(techRadarApiRef, new MyOwnClient())`. If both a backend and a custom client exist, the **custom client takes precedence** [14].
- **New (alpha) frontend system**: wire via `ApiBlueprint.make` (name `techRadarApi`, `params.factory = createApiFactory(techRadarApiRef, new MyOwnClient())`) + `createFrontendModule` (pluginId `'app'`, `extensions: [techRadarApi]`), instead of the `apis` `AnyApiFactory[]` array [14].
- **Static JSON via backend**: install `plugin-tech-radar-backend`; it uses Backstage's URL Reader to fetch a definition file from a URL declared in `app-config.yaml` under the top-level `techRadar` key with a `url` subkey. The referenced file must be JSON matching `TechRadarLoaderResponse`; the backend serves it at `/data`. So static JSON can live in a git repo (read by the backend) OR be fetched directly by a custom frontend client [14a][14].

Installation/props: `TechRadarComponentProps` exposes `width`, `height`, `svgProps`, `id`; `TechRadarPageProps` extends it with `title`, `subtitle`, `pageTitle` [14].

### 6.6 Relation to the catalog

Tech Radar is a **separate, standalone visualization plugin**, NOT part of and NOT wired into the Software Catalog [26][12]. Tech Radar entries are **not catalog entities**: no `apiVersion`/`kind`/`metadata`/`spec` envelope, not registered as `catalog-info.yaml`. The two share no data model and no entity references out of the box; deriving radar entries from catalog data would happen inside a custom `TechRadarApi.load()` implementation [11a].

### 6.7 Package relocation (seed URLs dead)

The old seed URLs (`backstage.io/docs/features/techradar/`, `/getting-started`, `github.com/backstage/backstage/tree/master/plugins/tech-radar`) return 404 as of June 2026. The plugin moved into `backstage/community-plugins` under `workspaces/tech-radar/`, split into three `@backstage-community` packages: `plugin-tech-radar` (frontend; `src/api.ts`, `src/defaultApi.ts`), `plugin-tech-radar-common` (`model.ts`, `schema.ts`, `sampleTechRadarResponse.json` — canonical data-model source of truth), `plugin-tech-radar-backend` (URL/git data loader). The old `@backstage` scoped name is deprecated; a spec must reference the `@backstage-community` packages [13][14b].

## 7. Validation & tooling

### 7.1 Canonical server-side validation endpoint

`POST <backend.baseUrl>/api/catalog/validate-entity` (e.g. `http://localhost:7007/api/catalog/validate-entity`). OpenAPI: path `/validate-entity`, `operationId: ValidateEntity`, tag `Entity` [6]. Request body (`application/json`, required) requires BOTH `location` (string) and `entity` (object) — note `location` is in the **body**, not an HTTP header. Responses: `200` Ok (no body); `400` with `{ "errors": [ { "name": string, "message": string } ] }`. Auth: optional JWT Bearer. An older docs reference renders the path as `POST /entities/validate`, but the source-of-truth OpenAPI uses `/validate-entity` [6].

### 7.2 No official backstage-cli validate command

The official `backstage-cli` has **no** catalog/entity validation subcommand; `config:check`/`config:print`/`config:schema` apply to app-config, not catalog entities. Offline/file-based validation goes through the Roadie validator or POSTing to a running backend [8].

### 7.3 Canonical JSON schemas (draft-07)

Live in `packages/catalog-model/src/schema/`: `Entity.schema.json`, `EntityEnvelope.schema.json`, `EntityMeta.schema.json`; per-kind files under `kinds/` (`API.v1alpha1.schema.json`, `Component.v1alpha1.schema.json`, `Domain…`, `Group…`, `Location…`, `Resource…`, `System…`, `User…`), plus newer specialized variants (`API.v1alpha1.mcp-server.schema.json`, `AiResource.v1alpha1.{rule,skill}.schema.json`). Kind schemas use `$ref` to `Entity`/`EntityEnvelope`/`EntityMeta`/`common#<id>` [16a].

### 7.4 Schema validators and the default policy chain

`@backstage/catalog-model` exports `entityKindSchemaValidator<T>(schema)` (base schema check for a kind; special-cases `kind`/`apiVersion`, returns `false` iff those mismatch, throws on other schema errors; does NOT account for custom policies/processors) and `entityEnvelopeSchemaValidator()` (generic envelope: presence/shape of `apiVersion`, `kind`, `metadata` incl. `metadata.name`). Both build on Ajv draft-07 [27].

`CatalogBuilder.buildEntityPolicy()` combines via `EntityPolicies.allOf(...)`: `SchemaValidEntityPolicy`, `DefaultNamespaceEntityPolicy`, `NoForeignRootFieldsEntityPolicy` (rejects unknown root fields beyond `apiVersion`/`kind`/`metadata`/`spec`/`relations`/`status`), and `FieldFormatEntityPolicy` (runs the field-format `Validators`). Helpers: `allOf()` (AND), `oneOf()` (OR). An `EntityPolicy` implements `enforce(entity): Promise<Entity | undefined>` [16b][28].

Field-format `Validators` (`packages/catalog-model/src/validation/makeValidator.ts`, `makeValidator(overrides)`): `isValidApiVersion`, `isValidKind`, `isValidEntityName` (→`isValidObjectName`), `isValidNamespace`, `isValidLabelKey`, `isValidLabelValue`, `isValidAnnotationKey`, `isValidAnnotationValue`, `isValidTag` (regex `^[a-z0-9:+#]+(\-[a-z0-9:+#]+)*$`). Override via `CatalogBuilder.setFieldFormatValidators(...)` or new-backend `catalogModelExtensionPoint.setFieldValidators({...})` [16c][16][28].

### 7.5 Custom kinds/processors and how failures are signalled

Implement `CatalogProcessor` (from `@backstage/plugin-catalog-node`): `getProcessorName()`, `validateEntityKind(entity)`, `preProcessEntity(...)`, `postProcessEntity(entity, location, emit)`. For a custom kind, wrap a JSON schema with `entityKindSchemaValidator(fooSchema)` and call it inside `validateEntityKind`. Register via the new backend system with `createBackendModule({ pluginId: 'catalog', moduleId, register(env){ env.registerInit({ deps: { catalog: catalogProcessingExtensionPoint }, async init({ catalog }){ catalog.addProcessor(new FooProcessor()); } }); } })`; older docs use `CatalogBuilder.addProcessor(...)` [27].

`@backstage/plugin-catalog-node` exports `processingResult` with `generalError(atLocation, message)`, `inputError(...)`, `notFoundError(...)`, `location(...)`, `entity(...)`, `relation(...)`, `refresh(...)`. Emitting `generalError`/`inputError` via the `CatalogProcessorEmit` callback marks the entity invalid and drops it (the prior error-free version is retained); these surface in the entity `status` and the validate-entity `errors[]` [29][27].

### 7.6 Where validation happens (lifecycle)

Three stages [30]: (1) **Ingestion** — providers seed raw entities; only COARSE validation (`kind`, `metadata.name`, `metadata.namespace` present). (2) **Processing** — full schema validation, EntityPolicy enforcement, field-format checks, processor mutation/error emission. (3) **Stitching** — final assembly. Implication: a descriptor that passes ingestion can still be rejected at processing time.

### 7.7 Well-known statuses

Status entries live under `status.items[]` (the object is "left unrestricted, except for the `items` field"). The only documented type is `backstage.io/catalog-processing`. Each item: `type`, `level` (`info`/`warning`/`error`), `message`, optional `error` (`{name, message, stack}`). Modelled as `EntityStatusItem[]` on `EntityStatus`. **The status feature is explicitly in active development, non-exhaustive, with a format that "will change unexpectedly"** — don't depend on it in production [31][32].

### 7.8 Community CI/offline linter

`@roadiehq/backstage-entity-validator`. CLI binary `validate-entity`; flags `-h`, `-q` (minimal output), `-i` (STDIN), `-l` (custom schema file). Defaults to `catalog-info.yaml` at repo root; accepts comma-separated lists and globs (`services/*/catalog-info.yaml`). GitHub Action: `- uses: RoadieHQ/backstage-entity-validator@v0.3.11` with `with: { path: 'catalog-info.yaml' }` (+ `validationSchemaFileLocation:`). Docker: `docker run --rm -v $(pwd):/workdir roadiehq/backstage-entity-validator catalog-info.yaml`. Runs Backstage's own structural validation (required fields, valid kind, per-kind spec shape, draft-07) PLUS well-known-annotation checks; custom schemas are additive (stricter only). **It does NOT check entity-reference validity** (e.g. whether the `owner` target exists) [10].

### 7.9 Common errors

- Leading/trailing separator in `metadata.name` → `FieldFormatEntityPolicy` rejection [16].
- Unknown root-level field → `NoForeignRootFieldsEntityPolicy` rejection [16b].
- Numeric/boolean-looking annotation value not YAML-quoted → coerced to non-string → validation fails [16].
- Empty `spec.definition` on API, or missing `spec.children`/`spec.memberOf` keys on Group/User → schema failure [16].

## 8. Implications for the catalog-info.yaml-generation skill

### 8.1 MUST emit vs MAY emit (per-kind floor from JSON-schema `required` arrays)

Envelope MUST for all kinds: `apiVersion`, `kind`, `metadata` (with `metadata.name` inside), `spec` [16].

| Kind | MUST emit in `spec` | MAY emit |
| --- | --- | --- |
| Component | `type`, `lifecycle`, `owner` | `system`, `subcomponentOf`, `providesApis`, `consumesApis`, `dependsOn`, `dependencyOf` |
| API | `type`, `lifecycle`, `owner`, `definition` (non-empty; use `$text:` placeholder) | `system` |
| Resource | `type`, `owner` — **NEVER `lifecycle`** | `system`, `dependsOn`, `dependencyOf` |
| System | `owner` | `type`, `domain` |
| Domain | `owner` | `type`, `subdomainOf` |
| Group | `type`, `children` (key MUST be present, may be `[]`) | `profile`, `parent`, `members` |
| User | `memberOf` (key MUST be present, may be `[]`) | `profile` |

Caution: omitting the empty-but-required keys (`Group.spec.children`, `User.spec.memberOf`) fails schema validation. Never emit `spec.lifecycle` on Resource/System/Domain/Group/User [16].

For Component (the primary generator target), the floor is: `apiVersion: backstage.io/v1alpha1`, `kind: Component`, a valid `metadata.name`, `spec.type`, `spec.lifecycle`, `spec.owner`. Everything else is MAY [16].

### 8.2 What can be inferred from a repo

- **Name**: slugify the repo/project name, then **strip leading/trailing non-alphanumerics and cap at 63 chars** (first/last char must be alphanumeric) [16].
- **`spec.type`**: infer from primary language/structure (`service`/`website`/`library` for Component; `openapi`/`asyncapi`/`graphql`/`grpc` for API) — but these are conventions, not enforced [1][3].
- **`spec.owner`**: from CODEOWNERS / team slug; emit a bare team slug for a Group, but emit an explicit `user:`-prefixed reference for an individual (bare owner defaults to Group and dangles if only a User exists) [1][5].
- **APIs**: detect OpenAPI/AsyncAPI/GraphQL files and emit an API entity with `spec.definition: { $text: ./<relative-path> }` plus `providesApis` on the Component [16].
- **Annotations**: `github.com/project-slug` (`org/repo` from the remote), `backstage.io/source-location` (`url:.../<repo>/` with trailing slash), `backstage.io/techdocs-ref: dir:.` if docs are colocated. Do NOT author `managed-by-location`/`-origin-location`/`orphan` (catalog-set/auto-derived) [5][33].
- **`spec.system`/`dependsOn`**: generally require operator input; not safely inferable from a single repo.

### 8.3 Decision points

- **Reference form**: emit the **full three-part** `kind:namespace/name` for cross-system robustness, though bare names are schema-valid (the per-kind schema enforces only `string`/`minLength: 1`; reference grammar is checked downstream) [16][5].
- **Owner kind**: explicit `user:` vs bare (Group) per §2.5 disambiguation.
- **YAML-quote** any numeric/boolean-looking annotation value [16].
- **Frontend-system invariance**: the generator MUST NOT branch on old-vs-new frontend system — catalog-info.yaml and ingestion config are backend, frontend-agnostic concerns [15].

### 8.4 Risks

- Slugified names with leading/trailing separators silently fail `FieldFormatEntityPolicy` [16].
- An auto-generated API entity with empty `definition` is schema-invalid [16].
- A bare `owner` resolving to a non-existent Group dangles (no error at schema time, broken relation at processing) [1].
- Whether the generator may add unknown `spec` fields depends on `additionalProperties` on each per-kind schema (see Open questions) — adding custom spec fields without a custom kind may be rejected [open].
- The validate-entity endpoint likely checks schema-only (not reference-target existence or custom-kind validity) — generated references must be validated separately [open].

## 9. Open questions

Carried forward (deduplicated):

1. **Template authoritative current descriptor** — current is `scaffolder.backstage.io/v1beta3` with required `spec` = `type`, `owner` only; confirm the full optional field list (`parameters`, `steps`, `output`, `secrets`, `presentation`) against the live `software-templates/writing-templates` docs for the targeted release [18].
2. **`additionalProperties` on per-kind `spec`** — whether the per-kind JSON schemas set `additionalProperties: false` on `spec` (i.e. whether emitting an unknown `spec` field on a known kind is rejected by `entityKindSchemaValidator` or merely ignored). Required arrays are confirmed; the open/closed nature was not read verbatim. Governs whether a generator may safely add custom `spec` fields without a custom kind.
3. **Owner Group/User precedence** — the exact rule when a short `owner` matches both a Group and a User of the same name in the same namespace (docs say bare defaults to Group, but warn-vs-silent-prefer was not confirmed). A generator should sidestep by always emitting explicit kind prefixes for owners.
4. **catalog-import app-config keys** — whether they are `catalog.import.entityFilename` (default `catalog-info.yaml`) and `catalog.import.pullRequestBranchName` (default `backstage-integration`); the plugin README was previously 403-blocked. Confirm against `plugin-catalog-import` source.
5. **validate-entity scope** — whether the endpoint runs the full custom-processor chain or only envelope + kind schema + default policies (docs phrasing "no errors in schema" implies schema-only, which would mean reference-target existence and custom-kind validity are not checked there).
6. **First-party offline validator** — whether any current `@backstage/cli`/`@backstage/repo-tools` version ships an offline `catalog-info.yaml` validate subcommand; the commands reference shows none.
7. **validate-entity `location` semantics** — confirmed required in the JSON body; confirm no version also accepts/requires an HTTP `Location` header.
8. **New-vs-legacy extension migration** — whether `CatalogBuilder.setFieldFormatValidators`/`addProcessor` are deprecated in favor of `catalogModelExtensionPoint.setFieldValidators`/`catalogProcessingExtensionPoint.addProcessor` for the targeted release.
9. **Enumerated validation error `message` strings** — exact wording emitted by `SchemaValidEntityPolicy`/`NoForeignRootFieldsEntityPolicy`/`FieldFormatEntityPolicy` is not documented; would require reading policy source.
10. **Relation array element schema** — exact JSON/YAML schema of `relations[]` element (string `targetRef` vs structured `target {kind,namespace,name}`) is defined in descriptor-format docs and `@backstage/catalog-model` `EntityRelation`, not on the well-known-relations page; not fetched verbatim.
11. **Jira annotation keys** — commonly cited `jira/project-key`, `jira/component` originate from community plugins (e.g. RoadieHQ), not Backstage-core; confirm against the specific plugin's README.
12. **Status model instability** — additional status types beyond `backstage.io/catalog-processing` may exist in newer releases; re-verify before treating as canonical. Annotation introduction/deprecation release versions are also unpinned (e.g. `backstage.io/kubernetes-cluster` singleTenant-only).
13. **`metadata.title`/`description` length caps** — not stated; only `name`, `namespace`, label/annotation keys, tags, and icons carry explicit constraints.
14. **Source-annotation auto-population mechanism** — which processor (likely `AnnotateLocationEntityProcessor`) auto-derives `source-location`/`edit-url`/`view-url`/`project-slug` vs which must be hand-authored, when read from a GitHub URL.
15. **GitLab/Bitbucket additional fields & default-branch behavior** — GitLab `useSearch`, `catalogFile` vs `entityFilename`, subgroup handling, `GitlabFillerProcessor` were only partially captured; whether GitLab/Bitbucket default to the repo default branch like GitHub is unconfirmed.
16. **Tech Radar per-item zod field rules** — stricter constraints (color regex, non-empty, whether `links` is validated) were inferred from a model-driven summary, not read line-by-line from `src/schema.ts`.
17. **Tech Radar backend refresh/headers** — whether `plugin-tech-radar-backend` supports a refresh/schedule (TaskScheduler/cron) or custom request headers/caching for `techRadar.url`; app-config keys beyond `techRadar.url` are unconfirmed.
18. **Tech Radar canonical docs location** — whether backstage.io still hosts a Tech Radar feature/getting-started page under a relocated path (old `/docs/features/techradar/` 404s) or whether canonical docs live only in the community-plugins README.
19. **Tech Radar current-ring selection rule** — latest-by-date is the strong assumption from sample data, but newest-wins selection and tie/ordering handling were not read from the rendering component source.

## 10. Sources

**Software Catalog — descriptor format, system model, references**
- [1] https://backstage.io/docs/features/software-catalog/descriptor-format
- [3] https://backstage.io/docs/features/software-catalog/system-model
- [5] https://backstage.io/docs/features/software-catalog/references
- [2] https://backstage.io/docs/features/software-catalog/well-known-relations

*(Note: in §2–3 the inline `[4]` denotes the descriptor-format page cited as the catalog-info.yaml dimension source — same URL as [1]: https://backstage.io/docs/features/software-catalog/descriptor-format.)*

**Well-known annotations & statuses**
- https://backstage.io/docs/features/software-catalog/well-known-annotations (cited inline as [5])
- [31] https://backstage.io/docs/features/software-catalog/well-known-statuses
- [32] https://backstage.io/api/stable/variables/_backstage_catalog-model.index.ANNOTATION_LOCATION.html
- [7] https://backstage.io/docs/features/kubernetes/configuration/
- [7a] https://pagerduty.github.io/backstage-plugin-docs/getting-started/backstage/ ; https://github.com/backstage/backstage/issues/11667

**Onboarding / configuration / integrations**
- [19] https://backstage.io/docs/features/software-catalog/configuration
- [20] https://backstage.io/docs/features/software-catalog/external-integrations
- [22] https://backstage.io/docs/integrations/github/discovery
- [23] https://backstage.io/docs/integrations/gitlab/discovery
- [24] https://backstage.io/docs/integrations/bitbucketCloud/discovery
- [21] https://backstage.io/docs/getting-started/register-a-component/ ; https://github.com/backstage/backstage/issues/22162
- [25] https://backstage.io/docs/integrations/github/org

**Tech Radar**
- [11] https://raw.githubusercontent.com/backstage/community-plugins/main/workspaces/tech-radar/plugins/tech-radar-common/src/sampleTechRadarResponse.json
- [11a] https://raw.githubusercontent.com/backstage/community-plugins/main/workspaces/tech-radar/plugins/tech-radar-common/src/model.ts
- [11b] https://raw.githubusercontent.com/backstage/community-plugins/main/workspaces/tech-radar/plugins/tech-radar-common/src/schema.ts
- [12] https://backstage.io/blog/2020/05/14/tech-radar-plugin/
- [12a] https://raw.githubusercontent.com/backstage/community-plugins/main/workspaces/tech-radar/plugins/tech-radar/src/api.ts
- [14] https://github.com/backstage/community-plugins/blob/main/workspaces/tech-radar/plugins/tech-radar/README.md
- [14a] https://github.com/backstage/community-plugins/blob/main/workspaces/tech-radar/plugins/tech-radar-backend/README.md
- [13] https://github.com/backstage/community-plugins/tree/main/workspaces/tech-radar/plugins/tech-radar
- [14b] https://www.npmjs.com/package/@backstage-community/plugin-tech-radar
- [26] https://backstage.io/docs/features/software-catalog/

**Validation, schema, tooling**
- [6] https://github.com/backstage/backstage/blob/master/plugins/catalog-backend/src/schema/openapi.yaml ; https://backstage.io/docs/features/software-catalog/api/validate-entity/ ; https://backstage.io/docs/features/software-catalog/software-catalog-api/
- [8] https://backstage.io/docs/tooling/cli/commands/
- [16a] https://github.com/backstage/backstage/tree/master/packages/catalog-model/src/schema ; https://github.com/backstage/backstage/tree/master/packages/catalog-model/src/schema/kinds
- [27] https://backstage.io/docs/reference/catalog-model.entitykindschemavalidator/ ; https://backstage.io/docs/features/software-catalog/extending-the-model/
- [16b] https://github.com/backstage/backstage/blob/master/plugins/catalog-backend/src/service/CatalogBuilder.ts
- [16c] https://github.com/backstage/backstage/blob/master/packages/catalog-model/src/validation/makeValidator.ts
- [29] https://backstage.io/docs/reference/plugin-catalog-node.processingresult/
- [30] https://backstage.io/docs/features/software-catalog/life-of-an-entity
- [10] https://github.com/RoadieHQ/backstage-entity-validator ; https://roadie.io/docs/catalog/validator/ ; https://www.npmjs.com/package/@roadiehq/backstage-entity-validator

**Gap-closure (catalog-model source files & frontend-system docs)**
- [16] https://github.com/backstage/backstage/blob/master/packages/catalog-model/src/validation/KubernetesValidatorFunctions.ts ; .../CommonValidatorFunctions.ts ; .../makeValidator.ts ; .../schema/kinds/{Component,API,Resource,Group,User}.v1alpha1.schema.json
- [33] https://backstage.io/docs/features/software-catalog/well-known-annotations/
- [18] https://backstage.io/docs/features/software-templates/writing-templates/
- [15] https://backstage.io/docs/features/software-catalog/configuration/ ; https://backstage.io/docs/features/software-catalog/catalog-customization/ ; https://backstage.io/docs/frontend-system/building-apps/migrating/ ; https://backstage.io/docs/frontend-system/architecture/migrations/
