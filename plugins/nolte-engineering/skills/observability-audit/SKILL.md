---
name: observability-audit
description: Audits an app's observability against spec/project/monitoring-observability/ and produces a severity-classified audit artifact plus an implementation plan for the gaps. The default `audit` operation dispatches the read-only observability-audit-scanner agent, then hard-fails on any missing-or-unwired mandatory pillar (metrics, structured logs, distributed traces, health + SLO + alert), the frontend and third-party floors, and the cardinality and PII-redaction guardrails; runtime-only behaviour is documented verify-at-runtime. The `plan` operation dispatches implementation-plan-author with the findings so a specialist (fullstack-developer) implements the instrumentation — there is no mechanical apply. Invoke to audit observability, check OTel instrumentation, or run an observability best-practices gate; also German. Don't use for Kubernetes probe wiring (deployment-bestpractices-reviewer), the PII/GDPR verdict (gdpr-data-protection-reviewer), or Dockerfile labels (dockerfile-audit). Supports resume.
tags: [audit]
phase: quality
summary: "Audits an app's observability against the spec (four pillars + frontend/third-party floors + cardinality/PII guardrails), reports findings, and hands the gaps to a specialist as a plan."
summary_de: "Auditiert die App-Observability gegen die Spec (vier Säulen + Frontend-/Third-Party-Böden + Kardinalitäts-/PII-Guardrails), meldet Findings und übergibt die Lücken als Plan an einen Spezialisten."
use_when:
  - "you want to audit a running app's OTel instrumentation against the observability contract"
  - "you want a pre-PR or pre-release observability best-practices gate"
  - "you want the observability gaps turned into a specialist-ready implementation plan"
dont_use_when:
  - situation: "You want the Kubernetes probe wiring that consumes a health endpoint reviewed or written"
    alternative: deployment-bestpractices-reviewer
  - situation: "You want the PII-class definition or the GDPR audit verdict on a leak"
    alternative: gdpr-data-protection-reviewer
  - situation: "You want a dependency CVE / vulnerability scan"
    alternative: dependency-audit
  - situation: "You want to audit Dockerfile OCI labels and build hardening"
    alternative: dockerfile-audit
see_also:
  - observability-audit-scanner
  - implementation-plan-author
  - fullstack-developer
resumable: true
---

# Observability Audit

Audit a running application's observability against the portfolio contract, produce a single severity-classified audit artifact, and hand the gaps to a specialist as an implementation plan. The default `audit` operation reports and recommends; the `plan` operation turns the findings into specialist-mapped work packages. **There is no mechanical `apply`** — OTel instrumentation is real code work, so remediation is a plan a specialist implements, not an in-place rewrite.

Implements `spec/project/monitoring-observability/` — the spec defines the four mandatory pillars, the frontend and third-party floors, the two mandatory guardrails, the vendor-neutral (OTel/OTLP) core, and the static-vs-runtime carve-out. This skill binds those rules to the on-disk procedure and owns policy, severity, the report, and the plan handover.

## German trigger phrases

This skill also triggers on equivalent German-language requests, including:

- "Observability auditieren" / "Observability-Best-Practices prüfen"
- "OTel-Instrumentierung prüfen" / "Tracing/Logging/Metriken-Abdeckung prüfen"
- "Beobachtbarkeit gegen die Spec prüfen"

## User-language policy

Detect the user's language from their message and respond in it. The audit artifact uses English section headings (so downstream tooling and the plan author can parse it reliably); prose around the report is localised.

## Inputs

- **Repo root**: default is the current working directory.
- **Operation**: `audit` (default, read-only) or `plan` (dispatches the plan author against an existing audit artifact). Never author a plan without an audit artifact to ground it.
- **Standard/version anchors**: per `spec/project/monitoring-observability/` §"Version and standard anchors", an audit MUST pin the specific standard/tool versions it checks against, because semantic-convention areas and rule sets drift. Default to the spec's anchors — OTel Semantic Conventions **1.x line** (current 1.43.0; stable convention areas gate as MUST, development/RC areas as SHOULD), OTLP 1.10.0, OTel Logs Data Model v1.53.0, W3C Trace Context L1. Record the exact versions in the artifact. A project on an older stable SemConv line is audited against that line with the drift noted, not hard-failed for not being on the newest release.

## Operations

### `audit` (default, read-only)

1. **Dispatch the read-only scan agent.** Dispatch `observability-audit-scanner` (Agent) for the detection pass: it detects the services/frontend/critical-dependencies, then the static presence/wiring of the four pillars, the frontend and third-party floors, and the two guardrails, tagging every finding `[static]` or `[runtime-verify]`, and returns a structured per-service findings inventory. Wait for its inventory before triaging.

2. **Apply the hard-fail policy.** Per `spec/project/monitoring-observability/`, mark a service **fail** when any **static** mandatory requirement is missing or only partly wired; otherwise **pass** (advisory findings and `[runtime-verify]` items never flip a pass to fail):
   - **Metrics** — no OTLP-exportable metric exporter/registry wired; a request-driven service without RED (rate/errors/a duration **histogram**); a constrained resource without USE coverage.
   - **Structured logs** — a free-text-only primary log surface; `trace_id`/`span_id` not injected into request-scoped logs; no severity mapping to the OTel `SeverityNumber` ranges.
   - **Distributed traces** — W3C Trace Context propagation registered on only **one** of the inbound/outbound boundaries (both are required); neither present.
   - **Health, SLO and alerting** — no health-signal endpoint declared; no well-formed SLO (an SLI as good/valid events + a target + an evaluation window distinct from the aggregation interval); no burn-rate alert bound to the SLO.
   - **Frontend floor** (when a browser frontend ships) — missing either the `error`/`unhandledrejection` listeners or browser→backend trace propagation.
   - **Third-party floor** — a **critical** dependency (on the request path or startup-blocking) with **no** signal (neither a black-box probe nor white-box client instrumentation). A non-critical or opt-out-marked dependency never fails.
   - **Guardrails** — an unbounded-cardinality metric label value; no PII-redaction processor wired at/before the emission boundary.

3. **Score the advisory pillars and document runtime-verify.** SHOULD items (OTel Semantic-Convention attribute conformance, span attributes, a stable log field schema, full RUM/Core Web Vitals with **INP** not FID, combining black-box + white-box for a critical dependency, moving high-cardinality dimensions to logs/traces) are scored and surfaced, never promoted to a hard fail. `[runtime-verify]` items (real metric values, an actually-unbroken end-to-end trace, an alert actually firing) are **documented as verify-at-runtime**, never counted as a static pass or fail.

4. **Render the report** (see Report shape). Sort per-service, mandatory pillars before floors before guardrails before advisory, so the rendered report diffs cleanly across runs.

5. **Persist the audit artifact.** Write the full audit to `.audits/observability-audit/observability-YYYY-MM-DD.md`. The artifact MUST record: date; trigger (pre-PR / pre-release / periodic); scope (services audited, frontend presence, the critical-dependency list with the criterion applied, what was skipped and why); the pinned standard/tool versions checked against; the per-service pass/fail verdict with each hard-fail reason; the runtime-verify items surfaced for a live check; and the Git revision audited. Link to the prior artifact so the progression stays traceable.

### `plan` (turns the findings into a specialist-ready implementation plan)

Run when the caller wants the gaps turned into work. This operation performs **no** code change itself — it produces a plan a specialist implements.

- **Dispatch `implementation-plan-author`** (Agent) with the persisted audit artifact as its **grounded input** (its observability-audit findings-report input mode), rather than a GitHub issue. The agent decomposes the failing/at-risk findings into atomic, testable work packages, each mapped to the specialist that implements it.
- **Map instrumentation work to `fullstack-developer`** — wiring an OTel SDK/exporter, a trace-propagation middleware on both boundaries, a structured-log formatter with `trace_id`/`span_id` injection, an SLO/alert-rules file, or a redaction processor are all real code changes the `fullstack-developer` owns. A neighbour-owned gap is routed out, not planned here: probe *wiring* → `deployment-bestpractices-reviewer` / `bjw-common-deployment-generator`; a PII-class/leak verdict → `gdpr-data-protection-reviewer`.
- **Leave `[runtime-verify]` items as explicit plan caveats** — a live-trace continuity check or an alert-firing test is verification work noted for the operator, not a static remediation package.
- The plan author writes its own pre-analysis artifact and returns the work-package table; this skill does **not** dispatch the specialists or open a PR (the operator or `issue-orchestrate` owns that gate).

## Report shape

```text
# Observability Audit

Scope: <repo root>, <n> services, frontend: <present | none> (skipped: <list with reasons>)
Trigger: <pre-PR | pre-release | periodic>
Standard anchors: OTel SemConv <1.x, ver>, OTLP <ver>, W3C Trace Context L1 (drift: <none | project on older line>)
Git revision: <sha>

## Verdict
<pass | fail> — services failing: <count>, advisory findings: <count>, runtime-verify items: <count>

## <service path>  (<language/framework>) — <PASS | FAIL>
### Mandatory (hard-fail on any static FAIL)
- Metrics (RED/USE): <PASS | FAIL: <what>> [<file:line>]
- Structured logs (parseable + trace_id/span_id + severity): <PASS | FAIL: <what>> [<file:line>]
- Distributed traces (inbound + outbound propagation): <PASS | FAIL: <direction absent>> [<file:line>]
- Health + SLO + bound burn-rate alert: <PASS | FAIL: <what>> [<file:line>]
### Floors
- Frontend (error/unhandledrejection + browser→backend propagation): <PASS | FAIL | n/a> [<file:line>]
- Third-party (≥1 signal per critical dep): <PASS | FAIL: <dep>> [<file:line>]
### Guardrails
- High-cardinality labels: <PASS | FAIL: <label>> [<file:line>]
- PII redaction wired at emission: <PASS | FAIL> [<file:line>]  (PII verdict → gdpr-data-protection-reviewer)
### Advisory (scored) & runtime-verify (documented)
- <check> (<advisory | runtime-verify>) — <note> [<file:line>]

## Health
- Services audited: <list>; skipped (with reason): <list or none>
- Standard/tool versions pinned: <list>
- Runtime-verify items surfaced: <count>
```

## Gotchas

- **Presence/wiring is static; values/continuity/firing are runtime.** The mandatory floor is that the exporter, the log correlation, both propagation boundaries, the SLO/alert-rules file, and the redaction processor are **wired**. Whether real values flow, a trace is actually unbroken end-to-end, or an alert actually fires is `[runtime-verify]` — document it, never statically hard-fail it, per spec §"Static verification and delimitation".
- **The traces pillar needs both boundaries.** Propagation registered on inbound-only or outbound-only breaks a trace at a hop; report it FAIL. One-sided propagation is the common silent gap.
- **A health endpoint's *semantics* are yours; the probe *wiring* is not.** This skill checks that a health endpoint is declared and reports the right thing; the readiness/liveness probe that consumes it is owned by `spec/project/kubernetes-deployment-best-practices/` — route it to `deployment-bestpractices-reviewer`, never restate it.
- **You check that PII redaction is *wired*, not the PII verdict.** Whether a specific field is personal data and whether a leak occurred is owned by `gdpr-data-protection-reviewer` (`spec/project/gdpr-audit-process/`, reported at `file:line`). This skill audits the producing side (a redaction processor is present, preferably fail-closed allow-list); it never renders the GDPR verdict.
- **"Critical" is a testable predicate.** The third-party floor applies only to a dependency on the request path or startup-blocking (in the availability chain); a best-effort/offline dependency is not critical, and an explicit opt-out marker excludes one. Don't fail a service for an un-instrumented non-critical dependency.
- **Pin the standard versions.** SemConv areas and tool rule sets drift; a floating anchor gives non-reproducible audits. Record the exact SemConv/OTLP/Trace-Context versions in the artifact, and audit a project on an older stable line against that line with the drift noted.
- **INP, not FID.** Core Web Vitals use INP (stable since 2024-03-12); a finding citing FID is stale. RUM/Core Web Vitals are advisory, never the mandatory frontend floor.
- **No mechanical apply.** Unlike `dockerfile-audit`, this skill never rewrites the target to fix a finding — the remediation is instrumentation code owned by a specialist, dispatched through the `plan` operation.

## Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/observability-audit/<run-id>.yml` after each named phase boundary (detection, triage, artifact-persist, plan-handover). On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope (`schema_version`, `run_id`, `inputs`, `phase`, `decisions[]`, `status`, ...) and the fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

## Hard rules

- **Never** modify the target application in any operation; there is no mechanical `apply`. Remediation is a specialist-implemented plan produced by the `plan` operation.
- **Never** statically hard-fail a `[runtime-verify]` behaviour (a real value, an actually-unbroken end-to-end trace, an alert actually firing); document it for a live check.
- **Never** pass the distributed-traces pillar when propagation is registered on only one boundary; both inbound and outbound are required.
- **Never** render the PII-class/leak verdict (owned by `gdpr-data-protection-reviewer`) or review the Kubernetes probe wiring (owned by `deployment-bestpractices-reviewer`); audit only the producing side.
- **Never** fail a service for a non-critical or opt-out-marked third-party dependency; the floor is per **critical** dependency (request-path or startup-blocking).
- **Never** promote an advisory (SHOULD) finding to a hard fail, and never demote a mandatory pillar/guardrail to advisory, without a spec change.
- **Always** pin and record the standard/tool versions audited against; a floating anchor gives non-reproducible audits.
- **Always** persist the audit artifact under `.audits/observability-audit/` with the per-service verdict, hard-fail reasons, runtime-verify items, and Git revision, and ground the `plan` operation in that artifact.
- When `spec/project/monitoring-observability/` and this skill disagree, the spec wins; this skill needs the update.

## Why this is a skill, not an agent

This skill follows the hybrid pattern: the read-only detection phase is delegated to the `observability-audit-scanner` agent (context-window isolation, tool restriction), while policy, severity, the report, and the plan handover stay in the skill.

- **Orchestration role**: typical callers run this as one step inside a larger flow (pre-PR gate, release cut, periodic observability review); the output flows back into the main conversation so the operator can triage and decide whether to author the plan.
- **Mid-flow interactivity**: the `plan` operation's handoff — confirming the gaps to remediate and grounding the plan author — is an operator-gated decision favouring the skill side; the specialist dispatch and any PR stay with the operator or `issue-orchestrate`.
- **Persistent artifact**: the deliverable is an on-disk audit artifact under `.audits/observability-audit/`; skills own persistent state.
- **Counter-dimension**: the detection half (detect services, parse instrumentation wiring across languages, classify static vs runtime) is self-contained and verbose — exactly the context-window pressure that favours an agent. That pull is honoured, but only for the scan half, delegated to `observability-audit-scanner`; the interactivity of the plan handoff and the persistent artifact keep the orchestrating surface a skill.
