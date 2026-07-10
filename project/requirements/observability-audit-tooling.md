# Requirements — Observability-audit tooling (skill + scanner agent + plan handover)

<!--
Produced via the `requirements-elicit` skill, following
spec/project/requirements-elicitation/.
`c_d` is an uncertainty proxy (self-consistency-derived), not a calibrated
probability. A requirement is `confirmed` only after an explicit teach-back.
-->

## Bounded context

- **What is being built:** an **observability-audit family** in the `nolte-engineering` plugin that
  read-only audits an existing implementation against `spec/project/monitoring-observability/`
  (presence/wiring of the four mandatory pillars × three dimensions + two guardrails) and whose
  deliverable is an **audit artifact plus an implementation plan** — the actual instrumentation work
  is done by a specialist. Two coupled artefacts:
  1. a read-only `observability-audit-scanner` **agent** that detects presence/wiring per required
     requirement × dimension and returns a structured findings inventory with `file:line`;
  2. an `observability-audit` **skill** that dispatches the scanner, applies the hard-fail policy
     (mandatory pillars/guardrails vs advisory; static vs runtime), renders and persists the audit
     artifact, and hands the findings to a plan author for a specialist-mapped implementation plan.
- **Key difference from the `dockerfile-audit` sibling:** there is **no mechanical `apply` step**.
  OTel instrumentation (SDK/exporter wiring, trace-propagation middleware, structured logging,
  SLO/alert rules, PII-redaction processor) is real code work, so the remediation output is an
  **implementation plan → specialist** (`fullstack-developer`), not an in-place file rewrite.
- **For whom:** repositories adopting the `nolte-engineering` plugin that run a live application and
  want it made observable to the portfolio contract (the audit consumers); the skill/agent authors.
- **The fourth sibling** in the best-practices→spec→engineering-artefact family, realising the
  `monitoring-observability` spec's own Open Question (§"`observability-audit` skill/agent family"),
  which prefigures "a read-only scanner agent, the audit skill, and the remediation specialist …
  mirroring the `dockerfile-audit` sibling".
- **Explicitly out of scope:** the actual instrumentation code (the specialist's job); probe
  **wiring** (owned by `spec/project/kubernetes-deployment-best-practices/`); the PII-class/verdict
  (owned by `spec/project/gdpr-audit-process/` — the scanner checks only the producer side, that
  redaction is wired); runtime verification of real values / uninterrupted traces / actually-firing
  alerts (marked runtime-verify, never statically hard-failed); demoting a mandatory requirement to
  advisory or vice-versa without a spec change. The change is **additive**.

## Understanding KPI

- Thresholds: `τ_low = 0.4`, `τ_high = 0.8`, self-consistency `k = 2`, question budget = `~6`
  (spec defaults; unchanged).
- `U_gate = min_d c_d` over required dimensions = **0.83**. The plan (`.resume/observability-audit-tooling/plan.md`)
  had already resolved the bounded context, the tool shape (sibling mirror), and the mandatory-pillar
  contract from the merged `monitoring-observability` spec; the interview settled the three
  load-bearing architecture decisions (F1 plan authorship, F2 scanner count, F4 critical-dependency
  criterion) by explicit operator sign-off, and the consequential F1 coupling change plus the
  settled-in-principle F3/F5/F6/F7 by an explicit teach-back confirmed with "passt".
- Termination: **saturation.** F1–F7 (plan §3) are resolved. Only per-clause spec-authoring detail
  (the exact static-vs-runtime split, SemConv release-pinning wording, report field layout) remains,
  routed to the agent/skill authoring step and listed under residual risk below.

### Gap matrix

| Dimension | Applicable | `c_d` | Uncertainty source | Evidence event |
|---|---|---|---|---|
| `functional` | yes | 0.88 | interpretation | F1/F2 sign-off (scanner detects; skill applies policy + dispatches plan author) + teach-back "passt" |
| `non_functional` | yes | 0.85 | interpretation | DRY skill/scanner split + reuse of `implementation-plan-author` + routing-budget + plugin distribution (plan §5); teach-back |
| `constraints` | yes | 0.88 | interpretation | `nolte-engineering`-only, marketplace distribution, `<object>-<action>` naming, read-only scanner, spec-wins, `task test` (plan §5) |
| `domain_objects` | yes | 0.87 | interpretation | Spec pillars × dimensions + F4 critical-dependency definition sign-off; findings-report + work-package objects |
| `actors` | yes | 0.85 | interpretation | Teach-back confirmed (adopting repos with a live app; the specialist `fullstack-developer`; skill authors) |
| `acceptance_criteria` | yes | 0.85 | interpretation | Hard-fail policy (mandatory pillars/guardrails present-and-wired) + `task test` green; teach-back |
| `edge_cases` | yes | 0.83 | specification | F3 static-vs-runtime carve-out settled in principle (presence/wiring = static, values/continuity/firing = runtime); per-clause split routed to authoring |
| `scope_boundaries` | yes | 0.86 | interpretation | F7 sign-off (producer-side only; probe-wiring → k8s, PII-verdict → gdpr) + no-`apply` boundary; teach-back |

## Requirements

<!-- EARS/CNL form; tagged confirmed/assumed with traceability. -->

### Scanner agent (nolte-engineering plugin)

- **R1** — WHEN the tooling is authored, it SHALL take the form of a read-only
  `observability-audit-scanner` **agent** (tools `Read, Bash, Glob, Grep`, `model: sonnet`, no
  `Edit`/`Write`) plus an `observability-audit` **skill**, mirroring the `dockerfile-audit` /
  `dependency-audit` sibling shape — never a lone self-contained skill or a lone reviewer agent.
  - _dimension_: `functional`, `non_functional` · _status_: `confirmed` (plan §3 + teach-back) · _source_: plan §3 sign-off
- **R2** — WHEN the scanner runs, it SHALL be a **single** `observability-audit-scanner` that walks the
  three dimensions (Backend, Frontend-floor, Third-party-floor) as internal **phases**, not three
  separate per-dimension agents — one object against the description routing budget.
  - _dimension_: `functional`, `non_functional` · _status_: `confirmed` (F2: "ein Scanner, Dimensionen als Phasen") · _source_: F2 sign-off
- **R3** — WHEN the scanner detects, it SHALL check **presence and wiring** of each mandatory
  requirement × dimension of `spec/project/monitoring-observability/` — the four pillars (Metrics
  RED+USE with a neutral exporter; Structured Logs carrying `trace_id`/`span_id` + severity;
  Distributed Traces with W3C Trace Context on inbound **and** outbound; Health + SLO shape + a bound
  burn-rate alert), the Frontend floor (browser `error`+`unhandledrejection` capture + browser→backend
  trace propagation), the Third-party floor, and the two guardrails (high-cardinality; PII-redaction
  wired) — detecting the stack at runtime (OTel SDK per language, log formatter, propagation
  middleware, SLO/alert-rules file, redaction processor) and reporting each finding with `file:line`.
  - _dimension_: `functional`, `domain_objects` · _status_: `confirmed` · _source_: spec pillars + plan §3
- **R4** — WHEN a requirement's satisfaction can only be established at runtime (a real metric value, an
  actually-uninterrupted trace, an actually-firing alert), the scanner SHALL mark it **runtime-verify**
  and SHALL NOT statically hard-fail it; only presence/wiring is decided statically. (Per-clause split
  finalised at authoring; principle: presence/wiring = static, values/continuity/firing = runtime.)
  - _dimension_: `edge_cases`, `scope_boundaries` · _status_: `confirmed` (F3 in principle) · _source_: F3 teach-back + spec §"Static-vs-runtime carve-out"
- **R5** — WHEN the Third-party floor is evaluated, a dependency SHALL count as **critical** iff it is on
  the synchronous request path **or** startup-blocking (in the availability chain); best-effort/offline
  dependencies do not count. The scanner SHALL honour an explicit per-dependency **opt-out marker**, and
  SHALL require at least one signal (black-box probe or white-box client instrumentation) per critical
  dependency.
  - _dimension_: `domain_objects`, `edge_cases` · _status_: `confirmed` (F4: "Request-Pfad/Availability-Chain + Opt-out") · _source_: F4 sign-off
- **R6** — WHEN the scanner reaches a neighbour-owned concern, it SHALL check **only the producer side**
  and delegate the rest: probe **wiring** to `spec/project/kubernetes-deployment-best-practices/`, and
  the PII-class/verdict to `spec/project/gdpr-audit-process/` (it checks that redaction is wired, never
  the GDPR verdict). The delegation SHALL be explicit in the agent's `see_also`/`dont_use_when`.
  - _dimension_: `scope_boundaries` · _status_: `confirmed` (F7) · _source_: F7 teach-back + spec §"Neighbour delimitation"

### Skill (nolte-engineering plugin)

- **R7** — WHEN the `observability-audit` skill runs its `audit` operation, it SHALL dispatch the
  scanner, apply the **hard-fail policy** (any missing-or-unwired mandatory pillar/guardrail fails;
  advisory items are scored; runtime-verify items are documented not failed), render a
  severity-classified findings report with `file:line`, and **persist** the audit artifact under
  `.audits/observability-audit/<timestamp>/`.
  - _dimension_: `functional`, `acceptance_criteria` · _status_: `confirmed` · _source_: plan §3 + teach-back
- **R8** — WHEN the skill produces the remediation output, it SHALL **dispatch the existing
  `implementation-plan-author` agent** with the audit findings-report as the grounded input (rather
  than authoring plan logic itself or performing a mechanical `apply`); the agent decomposes the
  findings into atomic, testable work packages, each mapped to the specialist that implements it
  (`fullstack-developer` for instrumentation code).
  - _dimension_: `functional`, `scope_boundaries` · _status_: `confirmed` (F1: "implementation-plan-author dispatchen") · _source_: F1 sign-off
- **R9** — WHEN R8 is realised, `implementation-plan-author` SHALL gain a **second sanctioned grounded
  input mode** — an `observability-audit` findings-report (`.audits/observability-audit/…`) — as an
  alternative to its current (GitHub-issue + `requirements-elicit` artifact) input, via an edit to
  `implementation-plan-author.md` (description, Preconditions, Step 1) that stays within the
  description routing budget and does not break its existing issue-driven path.
  - _dimension_: `functional`, `constraints` · _status_: `confirmed` (F1 coupling teach-back "passt") · _source_: F1 consequence sign-off
- **R10** — WHEN the skill pins what it audits against, it SHALL record the specific standard/tool
  versions it checks (anchoring on the SemConv 1.x line with per-convention stability gating a MUST vs
  SHOULD, per spec §pinned-standards / §SHOULD-pin), and SHALL be authored `resumable: true` with the
  mandatory Hybrid rationale, Gotchas, and Hard-rules sections. (Exact release pin + older-stable-line
  handling finalised at authoring.)
  - _dimension_: `non_functional`, `constraints` · _status_: `confirmed` (in principle) · _source_: F5 teach-back + spec §version-pinning

### Process / quality

- **R11** — WHEN the change is prepared for review, `task test` (`validate_skills.py`: frontmatter +
  `<object-noun>-<action>` naming + description budget) SHALL be green, `summary`/`summary_de` SHALL be
  ≤200 chars, the catalog SHALL regenerate cleanly (gitignored), the agent `see_also`/`dont_use_when`
  SHALL point only at existing objects, and the change SHALL live only under `plugins/nolte-engineering/`
  (nothing in the root plugin). All work stays in this worktree; the primary checkout stays on `develop`.
  - _dimension_: `acceptance_criteria`, `constraints` · _status_: `confirmed` · _source_: plan §5 invariants

## Surviving assumptions / open risks

**Resolved (settled by operator sign-off F1/F2/F4 + a consolidated teach-back "passt"):**

- ✅ **F1 (plan authorship):** dispatch the existing `implementation-plan-author` (R8), extending it to
  accept an audit findings-report as a second grounded input (R9) — reuse over a bespoke plan operation.
- ✅ **F2 (scanner count):** a single `observability-audit-scanner`, the three dimensions as phases (R2).
- ✅ **F4 (critical-dependency criterion):** on the request path or startup-blocking, with a per-dependency
  opt-out marker (R5).
- ✅ **No mechanical `apply`:** the deliverable is audit artifact + implementation plan; the specialist
  (`fullstack-developer`) writes the instrumentation code — the load-bearing difference from `dockerfile-audit`.

**Remaining residual risk (narrow authoring detail; routed to the scanner/skill authoring step, NOT to the operator):**

- **F3 exact static-vs-runtime split** — the per-clause assignment of which metrics/traces/health
  sub-clauses hard-fail statically vs are documented runtime-verify (spec Open Question §"Static-vs-runtime");
  settled in principle (presence/wiring = static, values/continuity/firing = runtime), exact wording at authoring.
- **F5 SemConv release-pinning wording** — whether the skill pins one exact SemConv release per portfolio
  cycle and how it treats a project on an older stable line (spec Open Question §"version-pinning policy").
- **F6 report/plan format + `.audits/observability-audit/` layout** — mirror the sibling convention; exact
  field set and the findings→work-package handover shape fixed at authoring.
- **Minimal health-endpoint field set and metric/label taxonomy** — spec Open Question, left to authoring.

**Constraint reminders (confirmed, not risks):** `nolte-engineering`-only; the scanner is read-only
(no `Edit`/`Write`); the skill writes nothing into target code — its deliverable is the audit artifact
+ the implementation plan; spec wins on any conflict (no demoting mandatory→advisory without a spec
change); primary checkout stays on `develop` (all work in this worktree); ships via the marketplace,
never copied into a consumer's `.claude/skills/`.
