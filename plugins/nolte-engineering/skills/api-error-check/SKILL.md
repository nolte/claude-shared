---
name: api-error-check
description: Statically checks a web API's error-handling surface for conformance against the project's own declared error contract — uniform error-body shape, populated required fields, a dynamically-generated error/correlation id, correct HTTP status-code semantics, and no internal-detail leakage (stack traces, raw driver messages, rendered queries, secrets). Detects the web framework (FastAPI / Flask / Django REST / Express / NestJS / Spring and comparable) and the error contract from project signals, falling back to RFC 9457 defaults only when none is declared. Invoke after adding or changing endpoints, before a release, or as a pre-PR error-handling gate; also on requests like "check the API error handling", "audit error responses", or equivalent German-language requests. Read-only: reports and recommends, never edits handler code. Don't use for the whole-codebase security audit (code-security-reviewer) or general code review (review skill).
tags: [review]
phase: quality
summary: "Read-only conformance check of a web API's error-handling surface (body shape, status codes, internal-detail leakage) against the project's declared error contract."
summary_de: "Read-only-Konformitätsprüfung der Fehlerbehandlungs-Oberfläche einer Web-API (Body-Form, Status-Codes, Leckage interner Details) gegen den deklarierten Fehler-Contract des Projekts."
use_when:
  - "you added or changed API endpoints and want to confirm their error handling conforms"
  - "you want a pre-PR or pre-release error-handling conformance gate"
  - "you want to confirm error responses don't leak stack traces, driver messages, or queries"
dont_use_when:
  - situation: "You want a whole-codebase OWASP security audit"
    alternative: code-security-reviewer
  - situation: "You want a general correctness / code-quality review of the diff"
    alternative: review
see_also:
  - code-security-reviewer
---

# API Error-Handling Conformance Check

Statically check a web API's error-handling surface against the project's own error contract, and produce a single severity-sorted report. This skill reports and recommends; it never edits handler code.

Implements `spec/project/api-error-handling/` — the spec defines the conformance dimensions, severity mapping, and discovery rules. This skill binds those rules to the on-disk procedure. When the spec and this skill disagree, the spec wins.

## German trigger phrases

This skill also triggers on equivalent German-language requests, including:

- "API-Fehlerbehandlung prüfen"
- "Fehlerantworten auditieren"
- "Leaken die Endpunkte interne Details?"

## User-language policy

Detect the user's language from their message and respond in it. The report itself uses English section headings (so downstream tooling can parse it reliably); prose around the report is localised.

## Inputs

- **Target**: an explicit handler/router file or directory path, or a requirement/feature identifier the project uses to group endpoints (for example `REQ-013`). Default is the current working directory's API source root.
- **Severity floor**: defaults to `info` (report every finding). Caller may narrow to `warning` or `critical` to de-noise a release gate.

## Operations

### 1. Resolve the target and discover project conventions

- If the target is a path, read it directly. If it is a requirement/feature identifier, resolve it to the owning handler files through the project's own layout (locate handler/router files and filter by the module the identifier names) — never assume a hard-coded path.
- **Detect the web framework** from the dependency manifest plus import/decorator signals:

  | Signal | Framework | Handler / raise patterns |
  |---|---|---|
  | `fastapi`, `starlette`; `@router.<verb>`, `APIRouter` | FastAPI/Starlette | `raise HTTPException(...)`, `@app.exception_handler` |
  | `flask`; `@app.route`, `abort(...)` | Flask | `abort(code)`, `@app.errorhandler` |
  | `djangorestframework`; `APIView`, `@api_view` | Django REST | `raise <APIException>`, custom `exception_handler` |
  | `express`; `app.<verb>(...)`, `next(err)` | Express | `res.status(c).json(...)`, error middleware |
  | `@nestjs/common`; `@Controller`, `throw new HttpException` | NestJS | exception filters |
  | `spring-web`; `@RestController`, `@ExceptionHandler` | Spring | `@ControllerAdvice` |

  When the framework can't be determined, state the assumed pattern set in the report and continue.

- **Discover the error-handling standard**: look for a spec/NFR/ADR/doc that governs error responses (under `spec/`, `docs/`, or ADRs). Record which document was used; absent one, fall back to the HTTP defaults below.
- **Discover the error-response contract** (the canonical error-body model): a shared error-model module, a global exception handler, or an OpenAPI `components.schemas` error type. Record where it was found and treat its fields as the required shape. Absent one, the contract is "a single consistent shape across the surface," with RFC 9457 problem-details as the recommended baseline.
- Record, per resolved input, whether the value came from an argument, discovery, or a default.

### 2. Check error-body uniformity and required fields

For every error path (each `raise` / `abort` / `res.status(...)` / thrown exception):

- Confirm the response body matches the declared contract shape; flag divergence.
- Confirm the contract's required fields are populated. A common contract has: a unique error/correlation id, a stable machine-readable error code, a human-readable message, optional field-level details, and request context (path, method, timestamp). Only check fields the project's contract actually declares.
- Confirm any declared **unique error id is generated dynamically** (per-occurrence, e.g. a fresh UUID), never a static constant — a constant id defeats log correlation.

### 3. Check HTTP status-code semantics

Compare each handler's status code against the situation it responds to:

| Situation | Expected status |
|---|---|
| Resource not found | 404 |
| Request / validation error | 400 or 422 (per framework convention) |
| Unauthenticated | 401 |
| Authenticated but forbidden | 403 |
| Domain / business-rule violation | 409 or 422 (per project convention) |
| Duplicate / conflicting state | 409 |
| Unhandled server error | 5xx (no internal detail in the body) |

Report each contradiction with a file:line attribution.

### 4. Run the leakage scan (security-relevant)

Search the error paths for internal detail reaching the response body. Anti-patterns:

```python
# ❌ stack trace / traceback in the response
raise HTTPException(detail=traceback.format_exc())
# ❌ raw driver / DB exception message exposed
raise HTTPException(detail=str(db_exception))
# ❌ rendered query or internal config in the response
raise HTTPException(detail=f"query failed: {sql_query}")
# ❌ bare framework default — no error handler, falls through and leaks
```

Each hit is **critical**, attributed to file:line, and flagged as a pointer into `spec/project/code-security-audit/` (this skill is not a substitute for the whole-codebase security audit). Also report handlers whose **error paths have no coverage** at all — an unhandled path falls through to the framework default, which commonly leaks a stack trace.

Treat statically-undecidable error paths (status or body assembled from an unresolvable runtime variable) as `dynamic, not statically verifiable` — neither conforming nor diverging.

### 5. Render the report

```
# API Error-Handling Conformance: <target>

Framework: <detected | assumed pattern set>
Error-handling standard: <doc path | "HTTP defaults (RFC 9457)">
Error-response contract: <module/schema path | "none — single-shape baseline">
Inputs resolved from: <argument | discovery | default> (per input)
Severity floor: <level>

## Summary
| Endpoints checked | Conforming | Diverging | Leakage hits | Dynamic-skipped |
|---|---|---|---|---|
| <n> | <n> | <n> | <n> | <n> |

## Findings (critical → warning → info)

### critical — <count>
- **<METHOD> <path>** (file:line): <internal-detail leakage | unhandled error path falling through to a leaking default> → see spec/project/code-security-audit/

### warning — <count>
- **<METHOD> <path>** (file:line): <wrong status code (got X, expected Y) | missing required contract field <field> | static error id>

### info — <count>
- **<METHOD> <path>** (file:line): <body-shape drift (no contract declared) | dynamic, not statically verifiable>

## Verdict
- ✅ Conformant / ❌ <n> findings (<c> critical, <w> warning, <i> info)
```

Cap each category at the first N entries and summarise the remainder as "… and {n} more". Sort findings by severity, then by file path, so the report diffs cleanly across runs.

## Gotchas

- **The error contract is project-specific, not the Kamerplanter NFR-006 model.** Don't assume an `error_id` / `error_code` / `details[]` shape — discover the project's actual contract first and check against that. Falling back to a fixed schema produces false "missing field" findings on a project that legitimately uses a different shape.
- **A clean happy-path test suite says nothing about error paths.** The whole point of this check is the branch the tests don't cover; never infer conformance from "tests pass."
- **A missing error handler is worse than a wrong one.** A handler with no failure branch falls through to the framework default, which in most frameworks renders a stack trace in non-production mode and a generic 500 in production — report the absence as critical, not as "no findings."
- **Status `422` vs `400` is framework-convention, not a defect.** FastAPI/Starlette uses `422` for request validation; many other stacks use `400`. Read the project's convention from existing handlers before flagging a status code.
- **This skill is static.** It reads source; it does not call the running API. A leakage path guarded by a runtime debug flag is still reported (the flag can be misconfigured in production), but mark it as conditional.

## Hard rules

- **Never** edit handler code, the error-contract module, or any other file. This skill reports; fixes are a follow-up step the developer owns.
- **Always** discover the project's own error contract and framework before checking; never hard-code one application's schema, requirement ID, or driver-exception strings.
- **Always** attribute every finding to a file:line so it is actionable.
- **Always** treat an internal-detail leakage hit as `critical` and point it at `spec/project/code-security-audit/`; this check surfaces leakage, it does not replace the whole-codebase security audit.
- **Always** report a statically-undecidable error path as `dynamic, not statically verifiable` rather than guessing conformance.
- **Never** report findings below the requested severity floor; keep the report signal-heavy.
- **Always** state which standard document and error contract the check measured against (or the default it fell back to), so the scope is reproducible.
- When `spec/project/api-error-handling/` and this skill disagree, the spec wins; this skill needs the update.

## Why this is a skill, not an agent

Per `spec/claude/skill-vs-agent/`, this capability stays a skill rather than an agent:

- **Invocation shape**: it is a developer-invoked, slash-command conformance gate run as one step inside a larger flow (after implementing endpoints, pre-PR, pre-release) — the same shape as the sibling `quality-gate` and `dependency-audit` skills, whose report flows back into the main conversation for triage.
- **Target argument**: it takes a caller-supplied target (a path or a requirement identifier) and tailors the run to it, which is the skill-style argument-driven interaction rather than an autonomous fan-out.
- **Counter-dimension**: the read-only, summary-returning shape pulls toward an agent (context-window isolation), as it does for the adjacent `code-security-reviewer` and `i18n-completeness-checker` agents. That pull is real, but the check's output is short (a single severity-sorted report, not a verbose scan dump), so the isolation benefit is small, while the slash-command, targeted, in-the-main-flow usage outweighs it. If the leakage scan later grows context-heavy, splitting that phase into a helper agent (the hybrid pattern `dependency-audit` uses) is the documented escape hatch.
