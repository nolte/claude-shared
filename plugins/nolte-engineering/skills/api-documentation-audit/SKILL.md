---
name: api-documentation-audit
description: 'Audits a repository''s OpenAPI documentation against spec/project/api-documentation/ and produces a severity-classified audit artifact. Dispatches the read-only api-documentation-scanner agent to discover every OpenAPI document (checked in at a conventional location or exportable via a documented command), then classifies findings on the Critical/Warning/Suggestion/Info ladder — presence and 3.x version floor, info completeness, per-operation contract (operationId, tags, summary, parameters, request bodies), response and schema hygiene, security documentation, and the lint/drift wiring. An HTTP-API repo with no discoverable document is the report''s most severe finding; the audit continues, never aborts. Invoke to audit API documentation, check an OpenAPI document for completeness, or run an API-docs gate; also German. Don''t use for error-response conformance (api-error-check) or general code review (source-code-review). Supports resume.'
tags: [audit]
phase: quality
summary: "Audits a repo's OpenAPI documentation against the spec (presence, version floor, per-operation contract, response/schema hygiene, security docs, lint/drift wiring) and reports per-document findings."
summary_de: "Auditiert die OpenAPI-Dokumentation eines Repos gegen die Spec (Präsenz, Versions-Floor, Operations-Vertrag, Response-/Schema-Hygiene, Security-Doku, Lint-/Drift-Verdrahtung); Findings pro Dokument."
use_when:
  - "you want to audit a repo's OpenAPI documentation for completeness and conformance"
  - "you want a pre-PR or pre-release API-documentation gate"
  - "you want to confirm an HTTP-API repo ships a discoverable, machine-readable contract"
dont_use_when:
  - situation: "You want the error-handling surface checked against the error contract"
    alternative: api-error-check
  - situation: "You want a holistic code-level review (API contracts are one dimension of it)"
    alternative: source-code-review
  - situation: "You want a dependency CVE / vulnerability scan"
    alternative: dependency-audit
see_also:
  - api-documentation-scanner
  - api-error-check
resumable: true
---

# API Documentation Audit

Audit a repository's OpenAPI documentation against the portfolio contract and produce a single severity-classified audit artifact. The audit is **advisory**: it reports and recommends; it never edits the OpenAPI document, the code, or the CI wiring — remediation is documentation work the operator owns.

Implements `spec/project/api-documentation/` — the spec defines the document-presence and format rules, the info-completeness floor, the per-operation contract, response and schema hygiene, the security-documentation rules, the lint-gate and drift SHOULDs, and the audit behaviour (no-document handling, per-document reporting). This skill binds those rules to the on-disk procedure and owns policy, severity, and the report. Severity vocabulary comes from `spec/claude/review-plan/` §Severity scale.

## German trigger phrases

This skill also triggers on equivalent German-language requests, including:

- "API-Dokumentation auditieren" / "OpenAPI-Doku prüfen"
- "OpenAPI-Spec auf Vollständigkeit prüfen"
- "Ist die API vollständig dokumentiert?"

## User-language policy

Detect the user's language from their message and respond in it. The audit artifact uses English section headings (so downstream tooling can parse it reliably); prose around the report is localised.

## Inputs

- **Repo root**: default is the current working directory.
- **Document scope** (optional): an explicit OpenAPI document path or list to narrow the audit. Default: the scanner discovers all documents.
- **Severity floor** (optional): defaults to `Info` (report every finding). Caller may narrow to `Warning` or `Critical` to de-noise a release gate.

## Operations

### `audit` (default and only operation, read-only)

1. **Dispatch the read-only scan agent.** Dispatch `api-documentation-scanner` (Agent) for the detection pass: it detects whether the repository ships an HTTP API, discovers every OpenAPI document (checked in at a conventional location, or exportable via a documented export command in a code-first repository), audits each document against the spec's dimensions, checks the CI lint-gate and drift wiring, and returns a structured per-document findings inventory recording each document's path, OpenAPI version, detected flavour (spec-first or code-first), and discovery method. Wait for its inventory before triaging.

2. **Classify severities.** Map every scanner finding onto the four-level ladder of `spec/claude/review-plan/` §Severity scale — MUST violations are **Critical**, SHOULD violations are **Warning**, MAY-class opportunities are **Suggestion**, observations are **Info**. Never invent additional levels and never re-tier without a spec change. The Critical set per `spec/project/api-documentation/`:
   - **No discoverable OpenAPI document** while the repository ships an HTTP API — neither checked in nor exportable. Per spec §Audit behaviour this is the report's **most severe finding, listed first**; the audit still completes with the repository-level checks.
   - A **Swagger 2.0** document (version floor is OpenAPI 3.0).
   - A `$ref`-split document whose entry point is not discoverable or does not bundle into a single valid document.
   - A code-first repository with **no reproducible export command** for the published document.
   - Missing or empty `info.title`, `info.version`, or `info.description` (or a placeholder version).
   - An operation missing a unique `operationId`, a tag (or a used tag undeclared in top-level `tags` with a `description`), or a `summary`.
   - A parameter without a `description` or `schema`, or with an incorrect `required` marking where statically decidable; a request body without a schema.
   - A success response the operation returns without a documented response schema; an actually-returned error status code undocumented. The error **body shape** is owned by `spec/project/api-error-handling/` — point the finding there (and at `api-error-check`), never duplicate its rules.
   - An API that authenticates callers with no `components.securitySchemes` or no `security` requirements referencing them; a deliberately public operation not recognisable as such (for example via an explicit `security: []`).
   - A real credential, token, or secret embedded in an example.

   The Warning set (SHOULDs): not targeting OpenAPI 3.1; missing `info.contact` / `info.license`; missing `servers` entries with per-environment descriptions; missing request/response examples for primary success responses; repeated inline schemas instead of named `components.schemas`; no CI lint gate over the document; no opt-in to the "API reference vs code" docs-freshness category or (code-first) no CI re-export diff. Suggestions cover MAY-class items such as project-specific lint-rule extensions. Flavour, discovery method, and linter availability are Info.

3. **Render the report** (see Report shape). Sort per-document, severities in ladder order (Critical → Warning → Suggestion → Info), findings within a severity by document path, so the rendered report diffs cleanly across runs.

4. **Persist the audit artifact.** Write the full audit to `.audits/api-documentation-audit/api-documentation-YYYY-MM-DD.md`. The artifact MUST record: date; trigger (pre-PR / pre-release / periodic); scope (documents audited with their OpenAPI version, detected flavour, and discovery method; what was skipped and why); the linter version when one ran; the per-document verdict with each Critical reason; and the Git revision audited. Link to the prior artifact so the progression stays traceable.

## Report shape

```text
# API Documentation Audit

Scope: <repo root>, HTTP API: <detected | none>, <n> OpenAPI documents (skipped: <list with reasons>)
Trigger: <pre-PR | pre-release | periodic>
Linter: <spectral <version> | none available — static checks only>
Severity floor: <level>
Git revision: <sha>

## Verdict
<pass | fail> — Critical: <count>, Warning: <count>, Suggestion: <count>, Info: <count>

## Repository level
- Document presence: <ok | CRITICAL: HTTP API shipped, no discoverable OpenAPI document (checked-in or exportable)>
- Export command (code-first): <documented: <command> | n/a (spec-first) | CRITICAL: missing>
- CI lint gate: <present: <workflow/target> | Warning: absent>
- Drift wiring (docs-freshness "API reference vs code" / CI re-export diff): <present | Warning: absent>

## <path/to/document>  (OpenAPI <version>, <spec-first | code-first>, discovered via <convention | docs declaration | export>)
### Critical
- <finding> [<path.to.operation | file:line>]
### Warning
- <finding> [<...>]
### Suggestion
- <finding> [<...>]
### Info
- <finding>

## Health
- Documents audited: <list>; skipped (with reason): <list or none>
- Discovery methods used: <list>
- Linter: <version | not installed>
```

Omit a severity subsection only when it has zero items.

## Gotchas

- **A missing document is the top finding, never an abort.** Per spec §Audit behaviour, an HTTP-API repository with no discoverable OpenAPI document gets the most severe (Critical) finding **and the audit continues** with the repository-level checks (export command, lint gate, drift wiring). Never end the run with "nothing to audit", and never silently skip the case.
- **Flavour neutrality is load-bearing.** Spec-first (hand-written) and code-first (framework-generated) documents are equally first-class; every quality requirement applies to the published artifact regardless of how it was produced. Never grade a generated document lower for being generated — but a code-first repository without a reproducible export command fails the presence contract, because the auditable artifact can't be reproduced.
- **The error-shape check is a pointer, not a rule set.** This audit checks that error responses are *documented per status code*; whether the error **body** matches the project's contract is owned by `spec/project/api-error-handling/` and checked by `api-error-check`. Point the finding there; never duplicate its rules.
- **Multiple documents get per-document reports.** A repository with one document per service is audited per document, each with its own version, flavour, and findings — never merged into a single blended verdict line.
- **An explicit `security: []` is signal, not noise.** It marks an operation deliberately public, distinguishing it from an operation whose security requirement was forgotten. Flag its *absence* on an unauthenticated-looking operation of an authenticated API; never flag its presence.
- **The lint gate is advisory at the repository level.** Spectral is the reference linter — a reference, never a requirement; any linter enforcing equivalent rules satisfies the SHOULD, and whether the gate blocks CI stays a per-repository decision. Report the gap as Warning; never demand Spectral by name as a Critical.
- **Schema-authoring questions that aren't OpenAPI-specific route elsewhere.** General JSON Schema conventions stay with `spec/project/yaml-json-schema/`; only OpenAPI Schema Object conventions are judged here.

## Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/api-documentation-audit/<run-id>.yml` after each named phase boundary (detection, triage, artifact-persist). On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope (`schema_version`, `run_id`, `inputs`, `phase`, `decisions[]`, `status`, ...) and the fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

## Hard rules

- **Never** modify the OpenAPI document, the application code, or the CI wiring; there is no `apply`. The audit reports and recommends only.
- **Never** abort or skip the audit when no OpenAPI document is discoverable in an HTTP-API repository; record it as the most severe (Critical) finding and complete the repository-level checks.
- **Never** blend multiple documents into one verdict; audit and report each document independently.
- **Never** duplicate the error-body rules of `spec/project/api-error-handling/`; check documentation presence per status code and point the shape question at that spec and `api-error-check`.
- **Never** promote a SHOULD finding to Critical, demote a MUST finding, or invent a severity level outside the `spec/claude/review-plan/` ladder, without a spec change.
- **Never** penalise a document for its production flavour; spec-first and code-first are equally first-class.
- **Always** record each document's path, OpenAPI version, detected flavour, and discovery method in the report and artifact.
- **Always** persist the audit artifact under `.audits/api-documentation-audit/` with the per-document verdict, Critical reasons, and Git revision.
- When `spec/project/api-documentation/` and this skill disagree, the spec wins; this skill needs the update.

## Why this is a skill, not an agent

This skill follows the hybrid pattern: the read-only detection phase is delegated to the `api-documentation-scanner` agent (context-window isolation, tool restriction), while policy, severity, and the report stay in the skill.

- **Orchestration role**: typical callers run this as one step inside a larger flow (pre-PR gate, release cut, periodic docs review); the output flows back into the main conversation so the operator can triage.
- **Mid-flow interactivity**: confirming the discovery scope (which documents, which services) and deciding what to remediate are operator-facing decisions that favour the skill side.
- **Persistent artifact**: the deliverable is an on-disk audit artifact under `.audits/api-documentation-audit/`; skills own persistent state.
- **Counter-dimension**: the detection half (discover documents, parse a large OpenAPI tree operation by operation, check the CI wiring) is self-contained and verbose — exactly the context-window pressure that favours an agent. That pull is honoured, but only for the scan half, delegated to `api-documentation-scanner`; the operator-facing triage and the persistent artifact keep the orchestrating surface a skill.
