# REST API and URL Design

Status: draft

## Context

A web API that lasts is an API whose URLs, methods, status codes, versioning, and error bodies stay predictable as the surface grows. When those decisions are made ad hoc, four failures accumulate silently: URLs drift between verb-style and resource-style (`/getUser` next to `/users/{id}`), between languages (`/ki-assistent` next to `/ai`), and between casing conventions, so consumers can't guess the next endpoint from the last one; the same situation answers with different HTTP status codes across handlers, so clients can't branch on the status line; a breaking change ships inside an unversioned URL and silently breaks every existing client; and the error body shape differs endpoint to endpoint, so no client can parse failures uniformly. None of these is caught by a type-checker or the happy-path tests, and each one hardens into a compatibility contract the moment a third party integrates.

This spec defines how an HTTP API is designed—the shape of its URLs, the semantics of its methods and status codes, its versioning and deprecation strategy, its collection conventions (filtering, sorting, pagination, field selection), its canonical error body, and its baseline transport security—so that a reviewer can judge conformance and a consumer can predict the surface. It's the missing third member of a trio: `spec/project/api-documentation/` owns **how** the API is documented (its Non-Goals defer design quality here), and `spec/project/api-error-handling/` owns the read-only **conformance check** of the error surface (its Non-Goals defer defining the canonical error contract here). This spec owns the design itself, including the portfolio's canonical error-body shape that the other two reference.

Where the industry's major guideline works agree (resource-oriented nouns, plural collections, RFC 9110 method semantics, HTTPS, no secrets in URLs), this spec adopts the consensus. Where they diverge—property casing and versioning axis, chiefly—this spec makes one explicit portfolio choice and states it, because the one hard rule all guidelines share is *be consistent within an API*.

Readers: developers designing or extending an HTTP API; reviewers checking a design against this standard; skill and agent authors building design-review tooling on top of it.

## Goals

- One predictable URL and method vocabulary across every API-shipping repository, so a consumer can infer an unseen endpoint from the ones it knows
- A single, explicit answer to each of the industry's divergence points (property casing, versioning axis, error-body shape), chosen once and applied consistently
- A versioning and deprecation strategy that lets an API evolve without silently breaking existing clients, and that never forces a retroactive rewrite of a shipped major version
- One canonical, machine-readable error body for the portfolio, referenced by the API-documentation and error-handling specs instead of re-invented per project
- A baseline of transport and URL security (HTTPS, no credentials in the URL, auth in headers) that holds regardless of framework
- A scope rule that makes the standard adoptable incrementally: binding for new APIs and the next major version, never a big-bang retrofit of a live one

## Non-Goals

- **How the API is documented**: the OpenAPI contract, completeness, and drift detection are owned by `spec/project/api-documentation/`; this spec governs the design that document describes
- **The read-only error-handling conformance check**: owned by `spec/project/api-error-handling/`; this spec defines the canonical error body, that spec checks a codebase against whatever contract it declares
- **Non-REST API styles**: GraphQL, gRPC, AsyncAPI, and message-queue contracts are out of scope; each warrants its own spec when a repository needs it
- **Authentication and authorization mechanism design**: token issuance, session models, scope taxonomies, and identity providers; this spec only requires that credentials travel in headers over HTTPS, not how they're minted
- **Wire-level data-model and JSON-Schema conventions** beyond casing and error shape—owned by `spec/project/yaml-json-schema/` and, for OpenAPI Schema Objects, by `spec/project/api-documentation/`
- **Localization of response content and error messages**: owned by `spec/project/i18n-completeness/`; this spec fixes the language of URLs and identifiers (English), not of human-readable payload text
- **Implementing or migrating an existing API**: this spec is the target standard; a repository's migration is its own scheduled work

## Requirements

### Scope of applicability

- **MUST** bind for every **newly created** HTTP API and for every **new major version** of an existing API; a major version that has already shipped is **grandfathered**: it's not required to be retrofitted to this standard, and a retrofit MUST NOT be forced onto a live major version
- **MUST** treat a repository's next major version bump (for example `/v1` → `/v2`) as the point at which the full standard applies, so migration cost is paid deliberately at a version boundary rather than as an in-place break
- **SHOULD**, within a grandfathered major version, still apply the additive and non-breaking rules of this spec to **new** endpoints where doing so doesn't contradict the version's established conventions (for example a new endpoint uses resource-oriented plural nouns even if older siblings don't)

### URL and resource structure

- **MUST** model the API as resources named with **nouns**, not actions: `POST /orders`, not `POST /createOrder`; the HTTP method carries the verb
- **MUST** name collections in the **plural** and address a member by an identifier appended as a path segment: `/plant-instances` (collection), `/plant-instances/{plantInstanceId}` (member)
- **MUST** express containment as alternating collection/identifier path segments (`/species/{speciesId}/cultivars/{cultivarId}`) and **SHOULD** limit sub-resource nesting to about three levels; deeper relationships are expressed as top-level resources with a filter rather than further nesting
- **MUST** use the path to identify resources and the **query string** to filter, sort, paginate, or shape a collection—never to select which resource is addressed
- **MUST** express an operation that genuinely doesn't fit resource CRUD as a **custom method** using colon notation on the resource (`POST /orders/{orderId}:cancel`), rather than inventing a verb path segment; custom methods are the documented exception, not the default
- **SHOULD** keep a resource's canonical URL stable across versions and releases; a resource's identity is part of its contract

### Language and casing

- **MUST** write all URL path segments, query-parameter names, and JSON property names in **English**, using **US-ASCII only**: no umlauts or non-ASCII characters, which the URI syntax would otherwise force into unreadable, error-prone `%XX` escapes
- **MUST** write path segments in **lowercase `kebab-case`** (`/care-reminders`, not `/CareReminders` or `/care_reminders`); paths are case-sensitive per RFC 3986, so lowercase is fixed to avoid `/Users` ≠ `/users` collisions
- **MUST** write JSON body property names and query-parameter names in **`camelCase`** (`birthYear`, `includeDetached`)—the portfolio's chosen convention among the valid industry alternatives (the Google/Microsoft ecosystem style); it's applied uniformly and never mixed with `snake_case` within an API
- **MUST** write enumeration values in `UPPER_SNAKE_CASE` (`status: "IN_PROGRESS"`) so they're unambiguous constants distinct from free text
- **SHOULD** name boolean properties as an affirmative predicate (`isActive`, not `disabled`) and timestamp properties with an `At` suffix carrying an RFC 3339 / ISO 8601 UTC value (`createdAt`)
- **MUST** name HTTP headers in conventional `Title-Case` (`If-None-Match`) and **MUST NOT** introduce an `X-` prefix for custom headers (per RFC 6648)

### HTTP method semantics

- **MUST** use HTTP methods per their RFC 9110 semantics: `GET` reads (safe, cacheable), `POST` creates or triggers non-idempotent processing, `PUT` fully replaces or creates at a known URL, `PATCH` partially modifies, `DELETE` removes
- **MUST** keep `GET`, `HEAD`, and `OPTIONS` **safe** (no observable state change) and keep `GET`, `HEAD`, `PUT`, and `DELETE` **idempotent**; `POST` and `PATCH` aren't required to be idempotent
- **MUST** use `PATCH` (not `PUT`) for a partial update, because a `PUT` that omits fields replaces the whole resource and would clear them
- **SHOULD** offer an idempotency mechanism for non-idempotent creation where duplicate submission is a real risk—a client-supplied `Idempotency-Key` request header replayed to the same result, or a natural secondary key—rather than relying on the client never retrying

### HTTP status codes

- **MUST** return the most specific status code consistent with the situation, using standard semantics as the baseline:

  | Situation | Status |
  |---|---|
  | Success with body | 200 |
  | Resource created | 201 (+ `Location` of the new resource) |
  | Accepted for async processing | 202 |
  | Success, no body | 204 |
  | Conditional GET, unchanged | 304 |
  | Malformed / unparseable request | 400 |
  | Unauthenticated (no or invalid credentials) | 401 |
  | Authenticated but forbidden | 403 |
  | Resource not found | 404 |
  | Method not allowed on resource | 405 |
  | Duplicate / conflicting state | 409 |
  | Precondition (`If-Match`) failed | 412 |
  | Semantic validation failure on a syntactically valid body | 422 |
  | Rate limit exceeded | 429 |
  | Unhandled server error | 5xx (no internal detail in the body) |

- **MUST** distinguish a **malformed** request (unparseable body, wrong content type) as `400` from a **semantically invalid** one (parses correctly but violates a business or field rule) as `422`
- **MUST NOT** answer a failure with a `2xx` status and an error payload; the status line is the primary, machine-readable failure signal
- **SHOULD**, when hiding the existence of a resource matters for authorization, return `404` rather than `403` so the response doesn't leak that the resource exists

### Versioning and compatibility

- **MUST** carry the API version as a **major-version segment in the URI path** (`/v1/...`), the portfolio's chosen versioning axis; the segment carries the **major only** (`/v1`, never `/v1.0` or `/v1.1`)
- **MUST NOT** encode a version in each individual operation path beyond the single leading major segment, and MUST NOT mix the URI-path axis with header- or query-based versioning within one API
- **MUST** preserve backward compatibility within a major version: a change is **breaking** (and therefore requires a new major version) if it removes or renames a field or endpoint, changes a field's type or a default, adds a new required request field, tightens validation, or changes a resource's identifier or URL
- **MUST** treat as **non-breaking** (and therefore shippable within the current major version) purely additive change: new optional fields, new endpoints, new enum values, new optional query parameters
- **MUST** design clients—and document the expectation for third-party clients—to **ignore unknown response fields**, so additive change stays non-breaking in practice
- **SHOULD** apply Semantic Versioning to the API's published specification (the OpenAPI document) even though only the major axis appears in the URL, so minor/patch spec evolution is trackable

### Deprecation and sunset

- **SHOULD** signal a deprecated resource or version with the `Deprecation` HTTP header (RFC 9745) and, once a removal date is set, the `Sunset` header (RFC 8594), accompanied by a `Link` relation pointing at migration documentation
- **MUST NOT** set a `Sunset` date earlier than the `Deprecation` date (RFC 9745 §4)
- **MUST** mirror any deprecation in the API's published specification (`spec/project/api-documentation/`), so the documented surface and the runtime signal agree
- **SHOULD** monitor usage of a deprecated surface before its sunset and, for a removed version, answer with `410 Gone` rather than a silent `404`

### Collections: Filtering, sorting, pagination, field selection

- **MUST** paginate any collection whose size is unbounded, and **SHOULD** prefer **cursor-based** pagination (an opaque, URL-safe `cursor` token plus a `limit`) over offset-based pagination for large or frequently-changing collections, because a cursor is stable under concurrent inserts
- **MUST** treat a pagination cursor as **opaque** to the client and carry no authorization in it; the client follows a server-supplied cursor or navigation link and never constructs a pagination URL itself
- **SHOULD** return pagination navigation as server-supplied links (for example a `next` link or link header) rather than requiring the client to assemble the next page's URL
- **SHOULD** use conventional query parameters for collection shaping: `sort` for ordering, `fields` for sparse field selection, and a `filter` expression (or discrete field filters) for narrowing, keeping the parameter vocabulary consistent across the whole API
- **SHOULD** avoid computing an exact total count by default when the underlying store makes it expensive; offer it as an explicit opt-in rather than a guaranteed field

### Error body

- **MUST** return errors as **RFC 9457 Problem Details** with the media type `application/problem+json`, using the standard members `type` (a URI identifying the problem class, documented), `title`, `status`, `detail`, and `instance`
- **MUST** include a stable, machine-readable error code as the `camelCase` extension member `code` (an `UPPER_SNAKE_CASE` string enum that's part of the API contract), so clients branch on `code` rather than parsing `detail`; the code MAY additionally be mirrored in a response header
- **MUST** report field-level validation failures in an `errors` extension array, each entry carrying a **JSON Pointer** into the request body (`pointer: "#/emailAddress"`), a per-field `code`, and a human-readable `detail`; the JSON Pointer inherits the body's `camelCase` property names, keeping the reference consistent
- **MUST** name every error extension member in `camelCase` and starting with a letter (RFC 9457 §3.2), so the body is uniformly cased and remains a valid Problem Details document
- **MUST NOT** place a stack trace, a raw driver or exception message, a rendered database query, an internal host or path, or any secret into an error body—a leakage finding that also points into `spec/project/code-security-audit/`
- **SHOULD** return a fresh, per-occurrence correlation identifier (for example `traceId`) as an extension member so a client-reported failure is findable in server logs, and MUST NOT emit it as a static constant

### Transport and URL security

- **MUST** serve the API over **HTTPS only**; credentials, tokens, and API keys travel encrypted in transit
- **MUST NOT** place passwords, tokens, API keys, or other secrets in the URL path or query string, where they leak into server logs, browser history, proxy logs, and the `Referer` header; secrets travel in a request header (for example `Authorization: Bearer <token>`) or the body
- **MUST** secure every endpoint with authentication and authorization appropriate to the resource; a public endpoint is a deliberate, documented exception, not a default
- **SHOULD** validate request `Content-Type` and enforce a method allowlist per resource (answering `405` / `415` appropriately), and **SHOULD** apply rate limiting (answering `429` with a `Retry-After` header) to protect against unrestricted resource consumption

### Hypermedia

- **MUST** reach Richardson Maturity Level 2 (proper resources, methods, and status codes); **full HATEOAS (Level 3) isn't required**
- **SHOULD** include pragmatic navigation links where they remove client-side URL construction (a `next` pagination link, a created-resource `Location`, a related-resource link), without adopting a full hypermedia control vocabulary

## Acceptance Criteria

- [ ] A new endpoint uses a plural, resource-oriented, English, lowercase `kebab-case` path with no verb segment, and a non-CRUD operation uses colon custom-method notation
- [ ] JSON body and query-parameter names are `camelCase`; enum values are `UPPER_SNAKE_CASE`; no `snake_case` appears in the wire contract
- [ ] The API is reachable under a single `/v{major}` path segment carrying the major version only
- [ ] A reviewer can classify a proposed change as breaking or non-breaking against the spec's breaking-change list, and a breaking change is routed to a new major version rather than shipped in place
- [ ] A grandfathered shipped major version isn't flagged for retroactive conformance, while a new major version is held to the full standard
- [ ] Each situation in the status-code table maps to the listed code in a sample handler set; a semantic validation failure returns `422`, a malformed request returns `400`, and no failure returns a `2xx`
- [ ] An error response is `application/problem+json`, carries `type`/`title`/`status`/`detail`/`instance` plus a `camelCase` `code`, and a validation error lists field failures in an `errors` array with JSON Pointers
- [ ] An error body contains no stack trace, raw exception, rendered query, or secret; a correlation identifier, when present, is generated per occurrence
- [ ] The API is served over HTTPS and no endpoint accepts a credential via the URL or query string
- [ ] A deprecated surface, when signalled, uses `Deprecation`/`Sunset` headers with a `Sunset` date not earlier than the `Deprecation` date, and a removed version answers `410 Gone`

## References

- [R1] Sister spec—how the API is documented (defers design quality here): `spec/project/api-documentation/`
- [R2] Sister spec—read-only error-handling conformance check (measures against the error contract defined here): `spec/project/api-error-handling/`
- [R3] Whole-codebase security audit (error-body leakage findings point here): `spec/project/code-security-audit/`
- [R4] Wire-level JSON-Schema conventions outside casing/error shape: `spec/project/yaml-json-schema/`
- [R5] Localization of human-readable payload text: `spec/project/i18n-completeness/`
- [R6] RFC 3986—URI Generic Syntax (ASCII, case-sensitivity): <https://www.rfc-editor.org/rfc/rfc3986>
- [R7] RFC 9110—HTTP Semantics (methods, most status codes, 422 §15.5.21, `Retry-After`): <https://www.rfc-editor.org/rfc/rfc9110>
- [R8] RFC 4918 §11.2—original 422 definition; RFC 6585 §4—429 definition (neither owned by RFC 9110): <https://www.rfc-editor.org/rfc/rfc4918> · <https://www.rfc-editor.org/rfc/rfc6585>
- [R9] RFC 9457—Problem Details for HTTP APIs (canonical error body): <https://www.rfc-editor.org/rfc/rfc9457>
- [R10] RFC 9745—the `Deprecation` header; RFC 8594—the `Sunset` header: <https://www.rfc-editor.org/rfc/rfc9745> · <https://www.rfc-editor.org/rfc/rfc8594>
- [R11] OWASP REST Security Cheat Sheet; OWASP API Security Top 10 (2023): <https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html> · <https://owasp.org/API-Security/editions/2023/en/0x11-t10/>
- [R12] Consensus source guidelines—Microsoft Azure, Google AIP, Zalando, JSON:API: <https://github.com/microsoft/api-guidelines> · <https://google.aip.dev/> · <https://opensource.zalando.com/restful-api-guidelines/> · <https://jsonapi.org/format/>

## Open Questions

- Should this spec be promoted from `Portfolio-Scope: local` to `portfolio` so it's inherited portfolio-wide (per `spec/project/portfolio-inherited-spec-layer/`)? It's authored as a portfolio-wide standard, but promotion is an explicit maintainer act and its two sister specs are currently `local`; left `local` until promoted deliberately.
- Should a read-only design-review capability (a `rest-api-design-scanner` agent and/or an overlay in `spec/project/source-code-review/`) be added to check conformance mechanically, mirroring the `api-documentation` / `api-error-handling` tooling pattern? Deferred to a follow-up.
- Should the canonical error body be offered as a reusable OpenAPI `components.schemas` fragment (Problem Details + the `code`/`errors` extensions) so projects import rather than re-declare it?
