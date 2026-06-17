# API Error-Handling Conformance

Status: draft

## Context

A web API answers failures with HTTP error responses. Three weaknesses accumulate silently as the surface grows: the error body shape drifts endpoint to endpoint (one returns `{"detail": "..."}`, another a bare string, a third a rich object), so clients can't parse failures uniformly; the wrong HTTP status code is returned (a missing entity answered `200` with an empty body, a validation failure answered `500`), so clients can't branch on the status line; and internal detail leaks into the response (a stack trace, a raw database driver message, a rendered SQL/AQL query, a secret in a log-and-return path), which is both a usability defect and a security exposure. None of these is caught by a type-checker or the happy-path test suite, and they surface as brittle client integrations and as findings in a security review.

This spec governs a focused, **read-only conformance check** of a web API's error-handling surface against the project's own declared error contract, operationalised by the `api-error-check` skill (`nolte-engineering` plugin). It's the generalised successor to a project-local checker that hard-coded one application's framework (FastAPI), error-response model, requirement ID, and persistence-driver exception strings. The portfolio form discovers the API framework, the error-response contract, and the error-handling standard from the project instead of assuming a single stack.

Readers: skill authors maintaining the checker; reviewers verifying its findings; developers who run it after adding or changing endpoints, before a release, or inside a pre-PR check.

## Goals

- Surface the three error-handling drifts—non-uniform error body shape, wrong HTTP status code, and internal-detail leakage—as a single severity-sorted report
- Stay framework-agnostic in the core checks (uniform error shape, status-code semantics, leakage scan) while adapting the call-site patterns to the project's actual web framework
- Measure the API against the project's **own** declared error contract when one exists, and fall back to documented HTTP defaults (RFC 9457 problem details, standard status-code semantics) only when none is declared
- Stay strictly read-only: the check reports and recommends, it never edits handler code
- Make the check cheap to re-run repeatedly within a sprint, because it's side-effect-free
- Draw a clear boundary to the broad code-security audit and to general code review, so the skill is invoked only for error-handling conformance

## Non-Goals

- Implementing or repairing error handlers—the check reports gaps; a developer fixes them
- The whole-codebase OWASP security audit owned by `spec/project/code-security-audit/`; this spec is the narrow error-response slice, and a leakage finding here is a pointer into that broader audit, not a substitute for it
- General code-quality or correctness review (owned by the `review` skill); this check judges only the error-handling contract
- Defining a project's error contract: the check measures against whatever contract the project declares, it doesn't impose a canonical schema on projects that have none
- Runtime fault injection or live API probing; the check is static (reads source, doesn't call the running API)
- Localisation of error messages (owned by `spec/project/i18n-completeness/`)

## Requirements

### Inputs and discovery

- **MUST** accept a target that's either an explicit handler/router file or directory path, or a requirement/feature identifier the project uses to group endpoints (for example `REQ-013`); when given an identifier, resolve it to the owning handler files via the project's own layout rather than a hard-coded path
- **MUST** discover the project's **error-handling standard** rather than assuming a requirement ID: look for a non-functional requirement or spec document that governs error responses (for example under `spec/`, `docs/`, or an ADR), and when one exists, measure conformance against it; report which document was used
- **MUST** discover the project's **error-response contract** (the canonical error body model) rather than hard-coding one application's schema: locate the error-schema definition (a shared error model module, a framework exception handler, an OpenAPI `components.schemas` error type, or equivalent) and treat its fields as the required shape; report where the contract was found
- **MUST** detect the **web framework** from project signals (dependency manifest plus import/decorator patterns—FastAPI/Starlette, Flask, Django REST Framework, Express/NestJS, Spring, and comparable) and adapt the handler and exception-raising call-site patterns accordingly; when the framework can't be determined, state the assumed pattern set in the report
- **MUST** report, per resolved input, whether the value came from an operator argument, a discovered standard/contract document, or a documented default
- **MAY** read an optional repository-local config file declaring the standard document, the error-contract location, the handler roots, and the framework; when present its values take precedence over discovery, when absent per-invocation discovery is the documented default

### Conformance dimensions

- **MUST** check **error-body uniformity**: every error path returns the project's declared error-contract shape (or, absent a declared contract, a single consistent shape across the surface); report each endpoint whose error response diverges from that shape
- **MUST** check the **required fields** of the declared error contract are populated on each error path—including, when the contract declares them, a unique error/correlation identifier, a stable machine-readable error code, a human-readable message, optional field-level details, and request context (path, method, timestamp)
- **MUST** verify that a declared **unique error identifier is generated dynamically** (per-occurrence, for example a fresh UUID) and never emitted as a static or hard-coded constant, since a constant identifier defeats log correlation
- **MUST** check **HTTP status-code semantics** against the situation the handler is responding to, using standard semantics as the baseline:

  | Situation | Expected status |
  |---|---|
  | Resource not found | 404 |
  | Request/validation error | 400 or 422 (per the framework's convention) |
  | Unauthenticated | 401 |
  | Authenticated but forbidden | 403 |
  | Domain/business-rule violation | 409 or 422 (per the project's convention) |
  | Duplicate / conflicting state | 409 |
  | Unhandled server error | 5xx (with no internal detail in the body) |

  Report each handler whose status code contradicts the situation, with a file:line attribution.
- **MUST** run a **leakage scan** for internal detail reaching the response body: raw exception/stringified-driver messages, stack traces, rendered database queries, internal host/path/config values, and secrets. Each hit is a security-relevant finding (**critical**), attributed to file:line, and flagged as a pointer into `spec/project/code-security-audit/`
- **MUST** treat statically-undecidable error paths (a status code or body assembled from a runtime variable the check can't resolve) as a noted caveat—report them as "dynamic, not statically verifiable" so they neither inflate nor silently disappear from the finding counts
- **SHOULD** report endpoints whose **error paths have no coverage** at all (a handler with no failure branch and no framework-level exception handler backing it), since an unhandled error path falls through to the framework default, which commonly leaks a stack trace

### Output and side effects

- **MUST** be strictly read-only: never edit handler code, the error-contract module, or any other file; the single output is a report
- **MUST** emit a single severity-sorted report ordered **critical** (internal-detail leakage; unhandled error paths that fall through to a leaking default), then **warning** (wrong status code; missing required contract field; static error identifier), then **info** (body-shape drift where a contract isn't declared; dynamic, not statically verifiable), led by a summary table (endpoints checked, conforming, diverging, leakage hits, dynamic-skipped)
- **MUST** cap per-category output (show the first N entries and summarise the remainder as "… and {n} more") so a large drift doesn't produce an unreadable wall of findings
- **MUST** attribute each finding to a source location (file and line) so it's actionable
- **MUST** report which target, framework, error-handling standard document, and error-response contract it used, so the check's scope is auditable and reproducible
- **MUST**, when no project error contract is discoverable, state the HTTP default it fell back to (uniform shape plus standard status-code semantics, RFC 9457 problem-details as the recommended baseline) rather than silently inventing a project-specific schema

## Acceptance Criteria

- [ ] Running the check on a target with diverging error responses produces a severity-sorted report whose summary table lists endpoints checked, conforming, diverging, leakage hits, and dynamic-skipped counts
- [ ] An endpoint whose error body diverges from the declared error contract is reported with a file:line attribution
- [ ] An error path that returns a status code contradicting the situation (for example `500` for a not-found) is reported as a warning with file:line
- [ ] A handler that returns a raw exception message, stack trace, or rendered database query in the response body is reported as a critical leakage finding pointing at `spec/project/code-security-audit/`
- [ ] A declared unique error identifier emitted as a static constant is reported as a warning
- [ ] A statically-undecidable error path is reported as "dynamic, not statically verifiable" and excluded from the conforming/diverging counts
- [ ] The report states the resolved target, detected framework, error-handling standard document, and error-response contract location, and whether each came from an argument, discovery, or a default
- [ ] When no project error contract is discoverable, the report states the HTTP default it measured against
- [ ] The skill makes no file modifications (read-only)
- [ ] The skill cites this spec in its body or `description`

## References

- [R1] Skill authoring rules this skill conforms to: `spec/claude/skill-management/`
- [R2] Skill-vs-agent decision rule and rationale-section requirement: `spec/claude/skill-vs-agent/`
- [R3] Adjacent whole-codebase security audit (delimited against this spec; leakage findings point here): `spec/project/code-security-audit/`
- [R4] Review-plan / audit-output conventions for severity-sorted reports: `spec/claude/review-plan/`
- [R5] RFC 9457—Problem Details for HTTP APIs (recommended default error contract): <https://www.rfc-editor.org/rfc/rfc9457>

## Open Questions

_None at this time._
