# Requirements — Portfolio-scoped Monitoring/Observability spec (OTel-neutral core + optional reference profile)

<!--
Produced via the `requirements-elicit` skill, following
spec/project/requirements-elicitation/.
`c_d` is an uncertainty proxy (self-consistency-derived), not a calibrated
probability. A requirement is `confirmed` only after an explicit teach-back.
-->

## Bounded context

- **What is being built:** a **spec** `spec/project/monitoring-observability/` (EN-canonical
  `en.md` + strict `de.md` translation, **`Portfolio-Scope: portfolio`**) that defines a
  vendor-neutral, mandatory observability contract for portfolio applications. The verbatim
  binding core anchors on **OpenTelemetry** (semantic conventions, OTLP export) as the
  vendor-neutral anchor; an **optional, non-binding reference profile** names concrete tooling
  (Prometheus / Grafana / Loki / Tempo / OTel-Collector). Audits check the neutral contract; the
  profile is illustrative.
- **Four mandatory pillars** run through **three component dimensions** (backend, frontend,
  third-party): **Metrics** (app + runtime, RED/USE), **Structured Logs** (trace-correlated,
  level-disciplined, no PII), **Distributed Traces** (end-to-end context propagation across
  service *and* third-party boundaries), **Health + SLO/Alerting** (health-signal semantics +
  SLO definition + bound alert). The rest is advisory/recommended.
- **For whom:** portfolio-member repositories that adopt the spec by-reference (the audit
  consumers), the **future audit-scanner agent / audit skill / implementation-specialist agent**
  authors who operationalise it, and the spec readers. It is the fourth **sibling** in the
  best-practices→spec→engineering-artefact family, alongside
  `spec/project/dockerfile-best-practices/`, `spec/project/kubernetes-deployment-best-practices/`,
  and `spec/project/bjw-s-common-chart-deployment/` — matching their shape (mandatory pillars,
  version anchors, static-checkability ACs, non-binding reference tooling, deep-research grounding).
- **Explicitly out of scope:**
  - **The agent/skill family itself** (scanner agent, audit skill, remediation specialist) — that
    is follow-up work in its own working copies; **this worktree ships only the spec**.
  - **Kubernetes deployment mechanics** — probe *wiring* (readiness gates traffic, liveness
    restarts, probe targets a real endpoint) stays owned by `kubernetes-deployment-best-practices`;
    this spec references it and owns only the health-signal *semantics* (what the endpoint reports).
  - **The GDPR audit verdict** — `gdpr-audit-process` remains the authority on *what class* counts
    as PII and on the detect/report verdict; this spec references it and adds only the producing-side
    emission-time redaction control.
  - Dashboards / visualisation UI, concrete numeric SLO targets, and specific vendor deployment.
  - The change is **additive** — not a fork of any existing spec (the observability space is greenfield;
    no monitoring/OTel/SLO spec exists in the corpus).

## Understanding KPI

- Thresholds: `τ_low = 0.4`, `τ_high = 0.8`, self-consistency `k = 2`, question budget = `~7`
  (spec defaults; unchanged).
- `U_gate = min_d c_d` over required dimensions = **0.82** (weakest = `edge_cases`). The seven open
  questions (plan §3) were posed as decision-eliciting choices grounded in the two sibling
  best-practices specs (their exact AC-checkability pattern, the `Portfolio-Scope`/`[locked]` mechanics,
  the k8s probe boundary, and the GDPR detection-only finding); **all seven resolved on the recommended
  default** and were confirmed by the consolidated plan-approval teach-back. `edge_cases` stays the
  binding constraint (0.82) because the precise "critical dependency" criterion and the exact
  static-vs-runtime carve-out wording are settled *in principle* but finalised during spec authoring
  (mirroring the `dockerfile-audit` precedent, which also closed at `U_gate = 0.82`).
- Termination: **saturation.** No candidate question retains positive net EVPI — the remaining items are
  narrow spec-authoring details routed to `/nolte-shared:spec`, not operator decisions.

### Gap matrix

| Dimension | Applicable | `c_d` | Uncertainty source | Evidence event |
|---|---|---|---|---|
| `functional` | yes | 0.88 | specification | Q1–Q7 sign-off (4 pillars × 3 dimensions, mandatory vs advisory) + plan-approval teach-back |
| `non_functional` | yes | 0.85 | specification | Q1 (static-checkability), Q5 (cardinality/cost guardrail), Q6 (PII redaction) + teach-back |
| `constraints` | yes | 0.90 | specification | OTel-neutral core, `Portfolio-Scope: portfolio`, EN-canonical + DE-sync, references-not-duplication (plan §5) |
| `domain_objects` | yes | 0.85 | specification | The four pillars, the three dimensions, "signal per critical dep", SLO shape (SLI+target+window) — Q2/Q3/Q4 |
| `actors` | yes | 0.85 | specification | Teach-back on consumer set: adopting repos, future scanner/skill/specialist authors, spec readers, three component dimensions |
| `acceptance_criteria` | yes | 0.85 | specification | Q1 static-presence-first AC formulation; self-consistency check (k=2, below) on scanner-checkability confirmed the reading |
| `edge_cases` | yes | 0.82 | specification | Q3 ("critical" dep), Q2 (frontend-optional/heavyweight-RUM boundary), Q1 (runtime-only carve-out) settled in principle; exact wording → spec author |
| `scope_boundaries` | yes | 0.88 | specification | Q6 (GDPR seam) + Q7 (k8s seam) + out-of-scope agent/skill family + greenfield finding; teach-back |

**Self-consistency note (k = 2, per §D):** for `acceptance_criteria` I privately generated two independent
readings of "make the mandatory criteria checkable" — (a) ACs assert the spec *declares* each rule with
RFC-2119 keywords and a scanner checks *presence/wiring* statically; (b) ACs assert *runtime behaviour*
(traces actually propagate, alerts actually fire) as hard requirements. The two diverge materially on what a
read-only scanner can hard-fail. Q1's "Static-presence-first" answer collapses the divergence onto reading (a),
raising `c_d` on evidence rather than self-report.

## Requirements

<!-- EARS/CNL form; tagged confirmed/assumed with traceability. -->

### Spec shape and anchoring

- **R1** — WHEN the `monitoring-observability` spec is authored, it SHALL exist as
  `spec/project/monitoring-observability/en.md` (canonical) + `de.md` (strict translation) carrying
  **`Portfolio-Scope: portfolio`** on the canonical file directly under `Status:`, mirroring the sibling
  best-practices specs (mandatory pillars, version anchors, static-checkability ACs, deep-research grounding).
  - _dimension_: `constraints`, `functional` · _status_: `confirmed` · _source_: plan §3.3 + grounding (scope mechanism)
- **R2** — WHEN the spec defines its binding contract, it SHALL anchor the mandatory core on **OpenTelemetry**
  (semantic conventions + OTLP export) as the vendor-neutral contract, and SHALL present concrete tooling
  (Prometheus / Grafana / Loki / Tempo / OTel-Collector) only as an **optional, explicitly non-binding
  reference profile**; audits check the neutral contract, never the profile.
  - _dimension_: `constraints`, `scope_boundaries` · _status_: `confirmed` · _source_: plan §3.1 (operator-fixed)

### The four mandatory pillars (× backend / frontend / third-party dimensions)

- **R3 (Metrics)** — WHEN a service is audited, it SHALL expose application and runtime metrics following the
  RED (rate/errors/duration) and USE (utilisation/saturation/errors) method through a vendor-neutral registry
  and exporter (OTLP or a Prometheus-compatible surface); the presence and wiring of the metric registry/exporter
  is the statically-checkable mandatory floor.
  - _dimension_: `functional`, `domain_objects` · _status_: `confirmed` · _source_: plan §3.2 + Q1
- **R4 (Structured Logs)** — WHEN a service emits logs, they SHALL be **structured** (machine-parseable),
  carry **trace/span correlation IDs**, and observe level discipline; the presence of a structured-log
  formatter with trace-context correlation is the statically-checkable mandatory floor. (PII discipline: R10.)
  - _dimension_: `functional`, `domain_objects` · _status_: `confirmed` · _source_: plan §3.2 + Q1
- **R5 (Distributed Traces)** — WHEN a request crosses a service or third-party boundary, trace context SHALL
  be **propagated end-to-end** (W3C Trace Context or an OTel-supported propagator); the presence of
  trace-propagation instrumentation/middleware on inbound and outbound boundaries is the statically-checkable
  mandatory floor, while actual end-to-end continuity is a runtime-verifiable SHOULD.
  - _dimension_: `functional`, `edge_cases` · _status_: `confirmed` · _source_: plan §3.2 + Q1
- **R6 (Health + SLO/Alerting)** — WHEN a service is audited, it SHALL (a) expose health/readiness **signal
  semantics** — what the health endpoint reports (dependency health, build/version info) — and (b) define at
  least one **SLO** (an SLI + target + evaluation window) with at least one **alert bound to it**. The
  *existence and well-formed shape* of the health-signal contract and the SLO+alert definition is mandatory and
  statically checkable; the concrete numeric targets and alert routing are project-defined. Probe **wiring** is
  out of scope (owned by the k8s sibling — R12).
  - _dimension_: `functional`, `acceptance_criteria` · _status_: `confirmed` · _source_: Q4 + Q7

### Cross-cutting mandatory floors and guardrails

- **R7 (Frontend floor)** — WHEN a project ships a frontend, it SHALL mandate **browser error/exception
  capture** (feeding the structured-logs/errors pillar) and **frontend→backend trace-context propagation**
  (keeping the traces pillar coherent across the browser boundary); full **RUM / Core Web Vitals /
  sourcemap-resolved stack traces** SHALL be advisory (SHOULD), not mandatory.
  - _dimension_: `functional`, `edge_cases` · _status_: `confirmed` (Q2: "errors + trace-propagation floor") · _source_: Q2
- **R8 (Third-party floor)** — WHEN a project depends on a **critical** third-party/external dependency, that
  dependency SHALL carry at least one observability signal — either a health/availability probe
  (synthetic/blackbox) **or** outbound-call instrumentation (client-side spans + error/latency metrics on the
  calling side); the *presence of some signal* per critical dependency is the mandatory floor, and the mechanism
  is the project's choice.
  - _dimension_: `functional`, `edge_cases` · _status_: `confirmed` (Q3: "one signal per critical dep, mechanism free") · _source_: Q3
- **R9 (Cardinality / cost guardrail)** — WHEN a project designs metrics and their labels, it SHALL NOT use
  **unbounded-cardinality dimensions** as metric labels (no raw user IDs, request IDs, full URLs, or timestamps
  as labels); the guardrail is a mandatory **rule**, while the concrete cardinality budget is project-defined/advisory.
  - _dimension_: `non_functional`, `edge_cases` · _status_: `confirmed` (Q5: "rule mandatory, number project-defined") · _source_: Q5
- **R10 (PII redaction — `[locked]`)** — WHEN a service emits logs or traces, it SHALL NOT emit personal data
  (PII) into them; redaction SHALL happen at the logging/telemetry emission boundary with an explicit field
  allow/deny discipline. This requirement SHALL be marked **`[locked]`** (consumers may tighten, never weaken),
  and SHALL **reference `gdpr-audit-process`** as the authority on what class counts as PII and for the audit
  verdict — this spec owns *prevention at emission*, GDPR owns *detection/verdict*, with no duplication of the
  PII-class definition.
  - _dimension_: `non_functional`, `scope_boundaries` · _status_: `confirmed` (Q6: "complementary split") · _source_: Q6 + grounding (GDPR detection-only)

### Checkability and delimitation

- **R11 (Static-checkability AC formulation)** — WHEN the spec writes its Acceptance Criteria, every **mandatory**
  criterion SHALL be phrased so a future **read-only scanner** can verify it by **static presence/wiring**
  (SDK/exporter config, log formatter, metric registry, trace-propagation middleware, health endpoint, SLO/alert
  rules file present and wired), closing with a "a reviewer can hold a real application against this checklist"
  clause per the sibling AC pattern; runtime-only behaviours (real values, actual end-to-end continuity, alert
  firing) SHALL be captured as advisory SHOULD or explicit "verify at runtime" notes rather than hard-failing MUSTs.
  - _dimension_: `acceptance_criteria`, `non_functional` · _status_: `confirmed` (Q1: "static-presence-first") · _source_: Q1 + grounding (sibling AC pattern)
- **R12 (k8s delimitation)** — WHEN the spec addresses health/readiness, it SHALL **reference**
  `kubernetes-deployment-best-practices` for probe **wiring** (readiness gates traffic, liveness restarts, probe
  targets a real endpoint) rather than restating it, and SHALL own only the health-signal **semantics** (what the
  endpoint reports) plus the SLO/alerting layer — no duplication of the probe requirements.
  - _dimension_: `scope_boundaries` · _status_: `confirmed` (Q7: "ownership seam") · _source_: Q7 + grounding (k8s owns wiring only)
- **R13 (Non-binding reference profile)** — WHEN the spec names concrete tooling, it SHALL confine it to a
  dedicated **reference-profile / version-and-tool-anchors** section marked explicitly non-normative (illustrative,
  not required to be present), so audits bind only to the OTel-neutral contract (R2).
  - _dimension_: `scope_boundaries`, `constraints` · _status_: `confirmed` · _source_: plan §3.1 + grounding (sibling reference-tooling pattern)

### Process / quality

- **R14** — WHEN the change is prepared for review, the canonical `en.md` and its `de.md` translation SHALL be
  kept in strict sync via the `/nolte-shared:spec` path (EN canonical per `.spec-config.yml`, drift/parity check
  green), the changed spec prose SHALL be Vale/lektorat clean (Vale run **from the worktree**; EN only, DE not in
  Vale scope), the spec SHALL pass `spec-readiness-reviewer` (contradictions / audience-fit / AC-coverage), the
  spec index SHALL be regenerated, and the PR SHALL be opened via `/nolte-shared:pull-request-create` — **this
  worktree ships the spec only** (no agents/skills authored, no PR merge).
  - _dimension_: `constraints`, `acceptance_criteria` · _status_: `confirmed` · _source_: plan §4 steps 4–8 + §5 invariants

## Surviving assumptions / open risks

**Resolved (settled by operator sign-off Q1–Q7 + consolidated plan-approval teach-back):**

- ✅ **Q1 (static vs runtime checkability):** static-presence-first — mandatory ACs phrased for scanner-checkable
  presence/wiring; runtime-only behaviours advisory. → **R11**.
- ✅ **Q2 (frontend depth):** mandatory floor = browser error capture + frontend→backend trace propagation;
  RUM/CWV/sourcemap advisory. → **R7**.
- ✅ **Q3 (third-party contract):** ≥1 signal per *critical* dependency (probe **or** client instrumentation);
  mechanism free. → **R8**.
- ✅ **Q4 (SLO concreteness):** SLO+alert *shape* mandatory (SLI+target+window, ≥1 bound alert); numbers
  project-defined. → **R6**.
- ✅ **Q5 (cardinality governance):** unbounded-label *rule* mandatory; numeric budget project-defined. → **R9**.
- ✅ **Q6 (PII boundary):** complementary split — own `[locked]` emission-time redaction contract + reference
  `gdpr-audit-process` for the PII-class definition/verdict (no producing-side redaction contract exists in the
  corpus today, so this fills a real gap, not a duplicate). → **R10**.
- ✅ **Q7 (k8s delimitation):** ownership seam — semantics here, probe wiring referenced from the k8s sibling. → **R12**.

**Remaining residual risk (narrow spec-authoring detail; routed to `/nolte-shared:spec`, NOT to the operator):**

- **Precise "critical dependency" criterion** for R8 (what makes a third-party dependency in-scope for the
  mandatory signal) — settle during authoring with a checkable definition (e.g. on the request path / in the
  availability chain).
- **Exact static-vs-runtime carve-out wording** for R3/R5/R11 — which sub-clauses hard-fail statically vs are
  documented as runtime-verify.
- **OTel semantic-convention version to anchor** (R2) — pin a specific convention version in the
  version-and-tool-anchors section, per the sibling precedent; may warrant the box-2 research pass.
- **Exact metric/label taxonomy and health-endpoint field set** (R3/R6) — the minimal reported fields.

These are settled-in-principle by the confirmed requirements above; the spec author fixes exact wording, and the
box-2 research pass (OTel conventions, RED/USE, SLO/SRE practice, RUM, synthetic monitoring) makes the numbers
and version anchors defensible.

**Constraint reminders (confirmed, not risks):** EN canonical + DE in strict sync; `Portfolio-Scope: portfolio`
with the PII rule `[locked]`; primary checkout stays on `develop` (all work in this worktree); **spec only** —
the scanner agent / audit skill / remediation specialist are follow-up work in their own working copies; no
duplication of the k8s (probe wiring) or GDPR (PII-class/verdict) specs; all generated spec/config prose is
English (DE is the translation).
