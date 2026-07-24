# API Documentation Best Practices

Status: draft

## Context

A repository that ships an HTTP API owes its consumers a machine-readable contract. Without one, three failure modes accumulate: consumers reverse-engineer endpoints from source code or trial requests; the documentation that does exist drifts silently away from the running API; and downstream capabilities that consume a published contract—contract testing, catalog generation, client generation—have nothing reliable to build on. `spec/project/yaml-json-schema/` explicitly excludes OpenAPI Schema Object conventions and defers them to a dedicated portfolio rule; this spec is that rule.

This spec defines how an API-shipping repository documents its HTTP API with an OpenAPI document so that a review can check conformance mechanically. It's tool-agnostic in its core: it names Spectral as the reference linter but never requires it. The spec is operationalised by the `api-documentation-audit` skill and the read-only `api-documentation-scanner` agent (`nolte-engineering` plugin), following the same capability pattern as `dockerfile-best-practices` and `monitoring-observability`. It's the sister spec to `spec/project/api-error-handling/`: that spec owns the error-response contract, this one owns the documentation surface that publishes it.

Readers: developers documenting an API; reviewers and the audit tooling checking conformance; skill authors maintaining the audit capability. Requirement provenance: `project/requirements/api-documentation.md` (elicited 2026-07-24).

## Goals

- One canonical, machine-readable API contract (an OpenAPI document) per API-shipping repository, discoverable at a conventional location
- Completeness: every operation is navigable and understandable from the document alone, without reading handler source code
- Flavour neutrality: spec-first (hand-written) and code-first (framework-generated) documents are equally first-class; every quality requirement applies to the published artifact regardless of how it's produced
- Auditability: a read-only scanner can establish conformance mechanically and report findings per document
- Drift visibility: divergence between the published document and the running API surfaces through the repository's docs-freshness checks instead of rotting silently

## Non-Goals

- AsyncAPI, GraphQL, and gRPC documentation—out of scope for this spec's normative core; each warrants its own profile or spec when a portfolio repository needs it
- Authoring the documentation content itself, or the prose developer-portal layer around it—this spec governs the contract artifact, not tutorials or guides
- REST API design quality (resource modelling, versioning strategy, pagination conventions)—this spec judges how the API is documented, not how it's designed
- Defining the error-response contract: `spec/project/api-error-handling/` owns the error body shape; this spec only requires that error responses are documented against it
- General JSON Schema authoring conventions outside OpenAPI documents—those stay with `spec/project/yaml-json-schema/`; OpenAPI Schema Object conventions live here
- Rendering and publishing infrastructure (Swagger UI, Redoc, hosting)—a per-repository choice

## Requirements

### Document presence and format

- **MUST** publish an OpenAPI document for every HTTP API the repository ships: either checked into the repository or reproducibly exportable from the code (see the flavour rules below)
- **MUST** use OpenAPI 3.0 or higher; a Swagger 2.0 document is a finding
- **SHOULD** target OpenAPI 3.1
- **MUST** make a canonical entry-point document discoverable: at a conventional location (for example `openapi.yaml`, `openapi.json`, or under `docs/` or `api/`) or declared in the repository's documentation; splitting the document into multiple files via `$ref` is permitted, but the entry point **MUST** bundle into a single valid document
- **MUST**, in a code-first repository, provide a reproducible export command (for example a Taskfile target or documented CLI invocation) that regenerates the published document from the code, so the scanner and CI can audit the same artifact consumers see
- Spec-first and code-first are equally acceptable flavours; no requirement in this spec depends on which flavour produced the document

### Info completeness

- **MUST** fill `info.title`, `info.version`, and `info.description` with non-empty, meaningful values; `info.version` reflects the actual API version, not a placeholder
- **SHOULD** declare `info.contact` and `info.license`
- **SHOULD** declare `servers` entries with a `description` per environment

### Per-operation contract

- **MUST** give every operation a unique, stable `operationId`
- **MUST** assign every operation at least one tag, and declare every used tag in the top-level `tags` array with a `description`
- **MUST** give every operation a `summary`; a longer `description` **SHOULD** be present where the summary alone doesn't explain behaviour
- **MUST** document every parameter with a `description` and a `schema`, and mark `required` correctly
- **MUST** document every request body with a schema; a request example **SHOULD** be present

### Response and schema hygiene

- **MUST** document every success response an operation returns, with a response schema
- **MUST** document the error responses the API actually returns, per status code; the error body schema follows the project's error contract per `spec/project/api-error-handling/` and isn't redefined here
- **SHOULD** provide response examples for the primary success response of each operation
- **SHOULD** define shared shapes as named `components.schemas` entries instead of repeating inline schemas; for schema-authoring questions that aren't OpenAPI-specific, `spec/project/yaml-json-schema/` applies

### Security documentation

- **MUST**, when the API authenticates callers, document the authentication mechanisms as `components.securitySchemes` and reference them in per-operation (or top-level) `security` requirements
- **MUST** make deliberately public operations recognisable (for example an explicit empty `security: []`) so a missing requirement is distinguishable from an open endpoint
- **MUST NOT** embed real credentials, tokens, or secrets in examples—placeholder values only

### Lint gate and drift

- **SHOULD** run a lint gate over the OpenAPI document in CI; Spectral with its default OpenAPI ruleset is the reference linter—a reference, never a requirement, and any linter that enforces equivalent rules satisfies this
- **MAY** extend the reference ruleset with project-specific lint rules
- **SHOULD** opt into the optional "API reference vs code" repository-level category of `spec/project/docs-freshness/`, so drift between the published document and the implementation is checked; a code-first repository **SHOULD** re-export the document in CI and fail on an unexplained diff

### Audit behaviour

- **MUST** (audit tooling): when the audited repository ships an HTTP API but no OpenAPI document is discoverable—neither checked in nor exportable—record this as the report's most severe (critical) finding and continue the audit; never abort and never silently skip
- **MUST** (audit tooling): when multiple OpenAPI documents exist in one repository (for example one per service), audit each document and report findings per document
- The audit is advisory: it reports and recommends; whether the lint gate blocks CI stays a per-repository decision under the SHOULD above

## Acceptance Criteria

- [ ] A repository shipping an HTTP API with a checked-in or exportable OpenAPI 3.x document passes the presence check; a Swagger 2.0 document produces a finding
- [ ] An operation missing an `operationId`, tag, or `summary` is reported as a finding attributed to its path and method
- [ ] A parameter without a `description` or `schema` is reported
- [ ] A documented status code without a response schema is reported; the error-shape check points to `spec/project/api-error-handling/` instead of duplicating its rules
- [ ] An API that authenticates callers but declares no `components.securitySchemes` produces a finding
- [ ] A repository with an HTTP API but no discoverable OpenAPI document produces a critical finding while the audit still completes
- [ ] A repository with multiple OpenAPI documents gets a per-document report
- [ ] A `$ref`-split document with a discoverable entry point bundles cleanly; a multi-file document without a discoverable entry point produces a finding
- [ ] The audit report names the documents checked, the OpenAPI version, the detected flavour (spec-first or code-first), and how each document was discovered
- [ ] The audit skill and scanner agent cite this spec in their body or `description`

## References

- [R1] Error-response contract this spec's error-documentation rules defer to: `spec/project/api-error-handling/`
- [R2] Drift anchor—optional repository-level "API reference vs code" category: `spec/project/docs-freshness/`
- [R3] JSON Schema authoring conventions and the boundary this spec completes: `spec/project/yaml-json-schema/`
- [R4] Code-level review dimension D8 (API contracts and documentation): `spec/project/source-code-review/`
- [R5] Contract-testing consumer of a published OpenAPI document: `spec/project/test-tier-contract/`
- [R6] Catalog consumer of OpenAPI files as API entities: `spec/project/backstage-catalog-generation/`
- [R7] Severity scale for audit reports: `spec/claude/review-plan/`
- [R8] OpenAPI Specification: <https://spec.openapis.org/oas/latest.html>
- [R9] Spectral (reference linter): <https://github.com/stoplightio/spectral>

## Open Questions

_None at this time—the load-bearing decisions (protocol scope, version floor, flavour stance, lint-gate strength) were resolved in the requirements elicitation of 2026-07-24._
