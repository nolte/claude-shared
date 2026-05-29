# Whole-Codebase Security Audit

Status: draft

## Context

Two security-review surfaces already exist for the portfolio's day-to-day flow, and both are deliberately narrow: the `security-review` CLI skill reviews the **diff** of the current branch, and `code-review` reviews changed lines for correctness. Neither performs a deep, whole-repository OWASP audit that correlates findings *across* files—the authentication layer against the access-control guards, the data-access layer against the injection surface, the secret-handling against the logging paths, the AI/RAG pipeline against prompt-injection and SSRF. A diff review can't see a missing tenant filter in an endpoint that the current branch never touched; a whole-codebase audit can.

This spec governs that deeper audit, operationalised by the `code-security-reviewer` agent (`distribution: plugin`). The agent is the generalised, **read-only** successor to a project-local reviewer that hard-coded one app's framework (FastAPI/ArangoDB/pgvector), its spec-document references, its tenant-key convention, and—critically—also *edited source files to apply fixes*. The portfolio form drops the fix responsibility (single-responsibility: it audits and reports; a human or a follow-up skill applies fixes) and discovers the stack rather than assuming one.

Readers: agent authors maintaining the auditor; reviewers who consume its report; developers who run a full security pass after a feature lands or before a release.

## Goals

- Provide a whole-codebase OWASP-aligned security audit that correlates findings across files, complementing—not duplicating—the diff-scoped `security-review` and `code-review`
- Stay strictly read-only: the audit finds and reports, it never edits source, suppresses findings, or changes behaviour
- Stay stack-agnostic in its methodology while adapting concrete patterns to the project's detected backend and frontend stack
- Produce a severity-classified, cross-file-correlated report a human can act on, with a file:line attribution per finding
- Draw an explicit boundary to the diff review, the dependency/CVE audit, and the requirements/spec security review, so the agent is invoked only for the whole-codebase code audit

## Non-Goals

- Diff-scoped review of the current branch's changes—owned by the `security-review` CLI skill; this audit is whole-repository
- CVE / dependency / lockfile vulnerability scanning—owned by `spec/project/dependency-audit/`; this audit is about the project's own code, not its dependencies' known CVEs
- Security review of *requirements or specifications* (the intended security posture) rather than implemented code—a separate concern; this audit reads code, not the spec's security requirements
- **Applying fixes**: the project-local predecessor edited source; the portfolio agent is read-only and the fix step belongs to a human or a separate skill, so the audit stays single-responsibility
- Running third-party SAST tooling (`semgrep`, `bandit`, `CodeQL`)—the agent performs LLM-driven pattern analysis; this stays out of scope here. A future `sast-runner` skill may emit findings the operator supplies to this agent as additional context—the read-only agent never executes the runner itself

## Requirements

### Read-only contract

- **MUST** be strictly read-only: declare only read and search tools (`Read`, `Grep`, `Glob`), declare no `Edit`, `Write`, `NotebookEdit`, and apply no fixes; the single output is the audit report
- **MUST NOT** suppress, downgrade, or annotate findings in the source (no `# nosec` / `# noqa` / `eslint-disable` insertion); reporting is the only action
- **MUST** return the report in its final message; persisting it to `.audits/` (per `spec/claude/review-plan/`) is the calling skill's or operator's responsibility, not the read-only agent's. When persisted by a calling skill, the report lives at `.audits/code-security-audit/<target-slug>.md` per `spec/claude/review-plan/` §File location and naming; a re-run overwrites the single canonical file rather than accumulating timestamped snapshots

### Discovery and stack adaptation

- **MUST** discover the backend and frontend source roots rather than hard-coding one project's paths, and report which roots and globs it scanned
- **MUST** detect the project's stack (web framework, data-access layer, frontend framework) and adapt concrete vulnerability patterns to it—the methodology (OWASP categories) is fixed, the example patterns are stack-specific
- **MUST**, when a security-relevant convention is declared by the project (a multi-tenant isolation key, an error-handling contract, an auth scheme), audit the code against that declared posture; absent a declared posture, audit against OWASP defaults and state the assumption

### Audit coverage

- **MUST** cover the OWASP Top 10 categories, correlating across files rather than per-file: injection (SQL/NoSQL/AQL/command/path-traversal, and frontend XSS), broken authentication (token validation, password hashing, session handling), broken access control (authorization on every state-changing endpoint, **multi-tenant isolation**, IDOR), insecure configuration (CORS, security headers, debug flags, information disclosure in error responses), cryptographic failures (hashing strength, secret storage), and software/data-integrity concerns
- **MUST** audit **secret handling** across the whole tree: hard-coded credentials, secrets in source / compose / chart values / seed data, secrets in logs or error responses, weak default secrets
- **MUST** audit **input validation** (schema validation on request bodies, field bounds, file-upload validation, pagination/sort allowlist enforcement) and **rate limiting** on sensitive endpoints (login, registration, password reset)
- **SHOULD** audit **AI/LLM/RAG security** when the project has such a pipeline: prompt injection (user input must not reach the system prompt as instructions), SSRF via embedding/model service URLs, API-key handling, and resource-exhaustion limits (`max_tokens`, top-k, query-length caps)
- **SHOULD** audit **frontend-specific** security: token storage (access token not in long-lived `localStorage`; refresh token as HttpOnly cookie), sensitive data in client state, XSS via `dangerouslySetInnerHTML` / output that isn't escaped, and route-level auth guards
- **MUST** treat the multi-tenant isolation check, when the project is multi-tenant, as a first-class correlated check: every tenant-scoped data path filters by the tenant identifier, and cross-tenant access returns not-found rather than forbidden (no existence leak)

### Output

- **MUST** emit a single severity-classified report using the portfolio-wide severity vocabulary from `spec/claude/review-plan/` §Severity scale (Critical / Warning / Suggestion / Info, verbatim Title Case)—it MUST NOT invent a P0–P3 or critical/high/medium/low scale; each finding carries a title, an OWASP category, a file:line attribution, the problem, and a concrete remediation recommendation (described, not applied)
- **MUST** lead with an overall assessment table (per OWASP category: rating + finding count) and, for multi-tenant projects, a tenant-isolation matrix (endpoint group × tenant-filter × authorization-check × status)
- **MUST** state the audit scope (scanned roots, globs, detected stack, declared posture or OWASP-default assumption) so the audit is reproducible
- **SHOULD** distinguish confirmed findings from suspected-but-uncertain ones so the consumer can triage; an uncertain finding is reported, not silently dropped
- **MUST** cite this spec in the agent body or `description`

## Acceptance Criteria

- [ ] The agent declares only `Read`, `Grep`, `Glob` (no write/edit/execution tools) and applies no source edits and inserts no finding-suppression comments
- [ ] Running the audit produces a report classified by the `spec/claude/review-plan/` §Severity scale vocabulary (Critical / Warning / Suggestion / Info) whose findings each carry a title, OWASP category, file:line, problem, and a described (not applied) remediation
- [ ] The report leads with a per-OWASP-category assessment table and states the scanned roots, globs, and detected stack
- [ ] A multi-tenant project's report includes a tenant-isolation matrix and flags any tenant-scoped path missing a tenant filter as Critical
- [ ] A hard-coded credential or a secret in source / config / logs is reported as Critical with a file:line
- [ ] An injection-prone data-access call (string-interpolated query) is reported with the parameterised remediation described
- [ ] A project with an AI/RAG pipeline has prompt-injection and SSRF checks represented in the report; a project without one omits them without a spurious finding
- [ ] The report distinguishes confirmed from suspected findings
- [ ] The audit is delimited from `security-review` (diff scope), `dependency-audit` (CVE scope), and requirements-level security review, and the agent's `description` states these negative cases

## References

- [R1] Agent authoring rules and read-only tool discipline: `spec/claude/agent-management/`
- [R2] Skill-vs-agent decision rule and rationale-section requirement: `spec/claude/skill-vs-agent/`
- [R3] CVE / dependency vulnerability audit (delimited against this spec): `spec/project/dependency-audit/`
- [R4] Review-plan / audit-output persistence conventions: `spec/claude/review-plan/`
- [R5] OWASP Top 10 (2021): <https://owasp.org/Top10/>
- [R6] Canonical portfolio-wide severity vocabulary (Critical / Warning / Suggestion / Info): `spec/claude/review-plan/` §Severity scale

## Open Questions

- Where's the boundary between this whole-codebase audit and a future architecture-level threat-modeling spec that reasons about trust boundaries and data flows rather than code patterns?
