# KPI Definition Process

Status: draft
Portfolio-Scope: portfolio

## Context

A business application can be measured in a hundred ways—request counts, row counts, click rates, error totals—and most of them are noise. A team that picks metrics bottom-up, from whatever the code happens to expose, ends up with a dashboard of vanity numbers that answer no business question; a team that picks none flies blind. What's missing is a **top-down, goal-oriented process** that decides *which* handful of indicators are the **key** ones for this specific application and *how each is defined*, before anyone wires up a single measurement.

This spec defines that process: how to **determine** the project-specific KPIs of a business application (from its business goals, its requirement documents, and its source code) and how to **define** each one precisely (name, definition, formula intent, unit, target, classification, owner, goal linkage, data-source pointer, rationale). It's grounded in the established measurement literature—the **Goal/Question/Metric** paradigm (Basili, Caldiera, Rombach) as the derivation basis, the **SMART** criteria (Doran, 1981) as the per-KPI quality gate, the **leading vs lagging** indicator distinction as a classification axis, and the **KPI-vs-metric** boundary that forces selection of the few key indicators out of the many possible metrics.

The spec draws a **hard boundary**: it governs *determination and definition only*. The moment a KPI is defined, the process stops. How that KPI is instrumented, collected, computed at runtime, stored, or displayed is **measurement**, and measurement is out of scope (see §Non-Goals). GQM itself makes this seam explicit: its later steps—"select data collection techniques, tools and procedures … develop the data collection mechanisms, including validation and analysis"—are exactly the measurement stage this spec excludes. This spec adopts GQM's Goal→Question→Metric *derivation* and stops before its data-collection stage.

It's the fourth sibling of the methodology-spec family alongside `spec/project/dockerfile-best-practices/`, `spec/project/kubernetes-deployment-best-practices/`, and `spec/project/bjw-s-common-chart-deployment/`: like them it states a normative process a downstream `nolte-engineering` skill enforces. It differs on two axes—it's `Portfolio-Scope: portfolio` (inheritable by consumer repos that derive their own KPIs, per `spec/project/portfolio-inherited-spec-layer/`), and it grounds a tool whose read-only scanner reads **two** input surfaces (source code *and* requirement documents). It's the definition-side complement to `spec/project/requirements-elicitation/` (which captures business goals) and `spec/project/mission/` (whose `verifies_via` pointer names how a mission is judged): those supply the goals; this spec turns goals into defined KPIs.

Readers: teams and repositories that need to determine the meaningful KPIs of their business application; the authors of the future `kpi-derive` skill and its read-only scanner agent; consumer repositories that inherit this spec by reference. Every load-bearing framework claim was verified against primary sources (see §Framework anchors).

## Goals

- A business application's KPI set is **derived top-down** from its business goals and requirements via a GQM-style Goal→Question→candidate-KPI refinement, never assembled bottom-up from whatever the code exposes
- Each KPI is **defined completely** against a fixed contract (id, name, definition, formula intent, unit, target/threshold, `leading|lagging` type, owner, goal linkage, data-source pointer, rationale) so two readers interpret it identically
- Every KPI **passes a SMART gate** (Specific, Measurable, Achievable, Relevant, Time-bound); a KPI that fails any letter is flagged not-yet-defined rather than published
- The process **selects the key few**: it surfaces many candidate metrics but distinguishes a **KPI** (a key metric tied to a business goal) from a plain metric, and only the selected, goal-linked ones become KPIs
- Each KPI is **traceable back to the goal or requirement** that motivated it, so the KPI set can be re-derived and audited when goals change
- The process **consumes an existing requirement artifact** when present (`project/requirements/<slug>.md`) as the primary goal source, and **degrades gracefully** to `goals.md` / `mission.md` and source-code signals when it's absent
- The derived KPI definitions land in a **human-readable, judgement-legible artifact** (`project/kpis/<slug>.md`) mirroring the requirements artifact, because KPI selection is a judgement call, not a machine dump
- The process is **portfolio-inheritable**: a consumer repository references this spec at a pinned hub release and derives its own application's KPIs against the same contract

## Non-Goals

- **Measurement, instrumentation, and telemetry.** Emitting a counter, adding a metrics client, wiring OpenTelemetry/Prometheus/StatsD, computing a KPI at runtime, or standing up a collection pipeline is out of scope. The `data-source-pointer` field names *where the data would come from*; it doesn't wire it up. This is the load-bearing boundary of the whole spec
- **Storage, aggregation, and dashboarding.** Time-series retention, roll-ups, alerting thresholds firing, and any dashboard/report surface (Grafana, a BI tool, an in-app analytics page) belong to the measurement stage and are excluded
- **GQM's data-collection stage.** This spec adopts GQM's Goal→Question→Metric *definition* levels; GQM's subsequent "develop the data collection mechanisms, including validation and analysis" step is exactly the measurement work excluded above
- **Eliciting the business goals themselves.** Capturing what the business is trying to achieve is owned by `spec/project/requirements-elicitation/`, `spec/project/mission/`, and `spec/project/roadmap/`; this spec *consumes* those goals, it doesn't elicit them
- **OKRs, SLAs, and SLOs as such.** Objectives-and-Key-Results, service-level objectives/agreements, and error budgets are adjacent target-setting frameworks; this spec names the KPI-vs-KRI/KBI/OKR boundary for delimitation but doesn't define an OKR or SLO process
- **A fixed, universal KPI catalogue.** This spec defines the *process* to derive project-specific KPIs, not a canned list of "the 10 KPIs every app needs"; the KPIs are always derived from *this* application's goals

## Requirements

### The determination process (GQM-based derivation)

- The process **MUST** derive KPIs **top-down** from business goals, following the Goal/Question/Metric refinement: from each goal, derive the **questions** that characterise the goal's achievement, then from each question derive the **candidate metrics** that would answer it. A KPI that can't be laddered back to a question and a goal is a bottom-up artefact and **MUST NOT** be published as a KPI
- Each derived goal **SHOULD** be framed with GQM's goal coordinates: a **purpose** (for example improve, increase, or reduce), an **issue** (the quality or outcome focus such as conversion, retention, or latency-as-experienced), an **object** (the product feature, business process, or user journey being measured), and a **viewpoint** (the business owner, the end user, or the operator), so the derived questions are well-scoped
- The process **MUST** treat the resulting metrics as **candidates** and apply a **selection step** (see §"KPI vs metric") before any candidate becomes a KPI; surfacing candidates is mechanical, selecting the key ones is a judgement call reserved to the operator
- The process **MUST** be re-runnable: when the source goals change, re-derivation **SHOULD** show which KPIs still hold, which need re-validation, and which have become irrelevant, rather than silently replacing the set

### The per-KPI definition contract

- Every defined KPI **MUST** carry all of these fields; a KPI missing any field is **not yet defined**:
  - `id`: a stable short identifier (for example `K1`) for cross-reference and traceability
  - `name`: a human-readable name
  - `definition`: a one-sentence plain-language statement of what the KPI measures
  - `formula-intent`: the *intended* computation in plain terms (for example "paid checkouts ÷ started checkouts"); it expresses intent, **MUST NOT** be a wired-up query or metric expression (that's measurement)
  - `unit`: the unit of the result (%, count, seconds, currency, ratio)
  - `target` / `threshold`: the value or band that counts as success, with its time horizon
  - `type`: exactly one of `leading` or `lagging` (see §"Leading vs lagging")
  - `owner`: the role accountable for the KPI (the SMART "Assignable" letter)
  - `goal-linkage`: a reference back to the originating goal or requirement (for example a `project/requirements/<slug>.md` requirement id, a `goals.md` outcome id, or a mission `verifies_via` pointer)
  - `data-source-pointer`: a plain-language pointer to *where the underlying data would come from* (for example the orders table, or the auth service login events); it names provenance, **MUST NOT** define collection
  - `rationale`: why this KPI matters for the business goal, and why it earned selection over other candidates
- Each defined KPI **MUST** pass a **SMART** gate (Specific, Measurable, Achievable, Relevant, Time-bound), and the definition **SHOULD** make each letter checkable: Measurable maps to `formula-intent` + `unit`, Relevant to `goal-linkage`, Assignable to `owner`, Time-bound to a `target` horizon. A candidate that fails any SMART letter **MUST** be recorded as a not-yet-defined open item, not published as a KPI

### KPI vs metric, leading vs lagging

- The process **MUST** enforce the **KPI-vs-metric** distinction: every KPI is a metric, but a metric becomes a **KPI** only when it's key, tied to a business goal and selected as one of the few indicators that matter. The scanner may surface many metrics; the artifact **MUST** contain only the selected, goal-linked KPIs, with the rejected-candidate reasoning available as rationale, not a flat dump of every measurable quantity
- Every KPI **MUST** be classified as **leading** (a predictive input that changes *before* an outcome—adoption, activation, pipeline) or **lagging** (an output that reports what already happened—revenue, churn, retention). A KPI set that's **all lagging** **SHOULD** be flagged, because it can only report the past and can't guide action; a healthy set pairs lagging outcomes with the leading inputs that move them
- The spec **MAY** support a **north-star** structuring convention—one primary lagging KPI plus the supporting leading KPIs that drive it—but **MUST NOT** mandate it; north-star is an optional organising lens, not a required field
- Adjacent indicator types (**KRI** for risk, **KBI** for behaviour, and **OKR** key results) **SHOULD** be named only to delimit them; the process defines KPIs, and a candidate that's really a risk or behaviour indicator is recorded as such and set aside

### Input sources and requirements coupling

- The process **MUST** gather inputs in this priority order: (1) an existing `project/requirements/<slug>.md` artifact (the primary business-goal source), (2) `project/goals.md` and `project/mission.md`, (3) source-code signals (domain events, aggregatable entities, state transitions, funnels, error surfaces)
- When **no** requirement artifact is present, the process **MUST NOT** block: it **MUST** warn that goal linkage will be weaker and **SHOULD** recommend running `requirements-elicit` first, then proceed to derive from the remaining sources. This is a **soft gate**: a code-only repository can still derive KPIs from its goals and source, it just derives them with a recorded caveat. Unlike the hard-gate consumers named in `spec/project/requirements-elicitation/` §"H. Consumer contract" (`roadmap-plan`, `feature-decompose`, `issue-orchestrate`), which **MUST** dispatch `requirements-elicit` or record an explicit operator override before proceeding, `kpi-derive` is a **deliberate soft-gate carve-out**: it proceeds on the recorded caveat alone with no operator override required, because a code-and-goals repository can still derive a useful KPI set
- Source code is a **candidate-signal source, never a goal source**: the process **MUST NOT** invent a business goal from code alone; code signals populate candidate metrics that still **MUST** ladder back to a goal from (1) or (2) to be selected

### The output artifact

- The derived KPIs **MUST** be written to `project/kpis/<slug>.md`, mirroring the layout of `project/requirements/`: a bounded-context/source header (naming the goal sources consumed) followed by one structured block per KPI carrying every field of §"The per-KPI definition contract"
- The artifact **MUST** be **human-readable Markdown**, not a bare data dump, because KPI selection and rationale are judgement content a reader must be able to follow and challenge; each KPI's `goal-linkage` **MUST** resolve to a real originating goal/requirement (a ghost linkage is a defect)
- The artifact **SHOULD** state, in its header, the framework parameters used (that GQM/SMART were applied) and list any not-yet-defined candidates as named open items, so the derivation is auditable

### Tooling shape (skill + read-only scanner)

- The process **MUST** be operationalised as an **interactive skill** (working name `kpi-derive`) plus **one read-only dual-source scanner agent**: the scanner performs **detection only** (mining both the source tree and the requirement/goal documents for candidate KPI signals), and the skill owns candidate **selection**, KPI **definition**, the **operator confirmation**, and the **write**. The skill **MUST** stay interactive because selecting the key KPIs and confirming each definition is a judgement call; the scanner **MUST** stay read-only and side-effect-free
- The tooling **MUST** live in the `nolte-engineering` plugin (its audience is code-bearing repositories, because it reads source code), while this spec remains repo-wide under `spec/`. It **SHOULD** be a single dual-source scanner rather than a scanner pair, to respect the agent-description routing budget

### Portfolio scope and inheritance

- This spec carries `Portfolio-Scope: portfolio` and **MUST** remain inheritable by reference per `spec/project/portfolio-inherited-spec-layer/`: a consumer repository declares `inherits:` at a pinned hub `ref` and derives its own application's KPIs against this contract, never copying the spec text
- The spec's normative content **MUST** be application-agnostic: it prescribes the *process and contract*, never a fixed KPI list, so any business application in the portfolio can inherit it and derive its own project-specific KPIs

### Framework anchors

- The spec's normative content **MUST** be read against these grounded sources (verified 2026-07-10): the **GQM** paradigm (Basili, Caldiera, Rombach, *The Goal Question Metric Approach*; goal coordinates purpose/issue/object/viewpoint; three levels Goal→Question→Metric; metrics objective or subjective; business-driven goals as input) for the derivation basis and the measurement-stage boundary; **SMART** (G. T. Doran, "There's a S.M.A.R.T. way to write management's goals and objectives," *Management Review*, 1981) for the per-KPI gate; the **leading vs lagging** indicator distinction (leading = predictive inputs, lagging = realised outputs) for classification; and the **KPI-vs-metric** boundary (a KPI is a *key* metric tied to a business outcome) for selection
- A `kpi-derive` implementation **MUST** ground every derivation in these frameworks and **MUST NOT** cross the measurement boundary: it defines KPIs, it never emits instrumentation, a metrics client, or a collection pipeline
- Each framework attribution above is an author-time external assertion and **MUST** be triangulated to at least three independent sources per `spec/claude/research-triangulate/` §"Author-time assertions"; the source list (URL, source class, retrieval date, Primary-first) is recorded in §Sources

## Acceptance Criteria

- [ ] `spec/project/kpi-definition-process/` exists with `en.md` (canonical) and `de.md` (translation), carries `Portfolio-Scope: portfolio`, and is listed in `spec/README.md`
- [ ] The determination process is stated as a **top-down GQM refinement** (goal → question → candidate metric) with the goal coordinates (purpose/issue/object/viewpoint) and a mandatory selection step
- [ ] The process's **re-runnability on changed goals** is a stated requirement, and re-derivation surfaces which KPIs still hold, which need re-validation, and which became irrelevant (rather than silently replacing the set)
- [ ] The **per-KPI definition contract** lists every mandatory field (id, name, definition, formula-intent, unit, target/threshold, type, owner, goal-linkage, data-source-pointer, rationale) with RFC 2119 keywords, and `formula-intent`/`data-source-pointer` are explicitly *intent/provenance only*, not wired-up measurement
- [ ] The **SMART** gate is mandatory per KPI, with each letter mapped to a contract field, and a failing candidate is recorded as not-yet-defined rather than published
- [ ] The **KPI-vs-metric** selection rule and the mandatory **`leading|lagging`** classification are stated, with the all-lagging flag and the optional (non-mandated) north-star convention
- [ ] The **KRI/KBI/OKR delimitation** (named only, then set aside) is stated so an adjacent-indicator candidate is recorded as such rather than mis-published as a KPI
- [ ] The **input priority** (requirements → goals/mission → source code) and the **soft-gate** behaviour on a missing requirement artifact (warn + recommend, don't block) are stated, and source code is barred as a goal source
- [ ] The **output artifact** `project/kpis/<slug>.md` is specified: human-readable, mirroring `project/requirements/`, one block per KPI, goal-linkage resolving to a real goal
- [ ] The output artifact's **header** is specified to state the framework parameters used (GQM/SMART applied) and to list any not-yet-defined candidates as named open items, so the derivation is auditable
- [ ] The **tooling shape** is specified: an interactive `kpi-derive` skill + one read-only dual-source scanner agent in `nolte-engineering`, with the skill owning selection/definition/write and the scanner read-only
- [ ] The **hard measurement boundary** (no instrumentation, telemetry, collection, storage, aggregation, dashboarding; GQM's data-collection stage excluded) is stated in §Non-Goals and reinforced in the requirements
- [ ] The **framework anchors** are pinned: GQM (Basili/Caldiera/Rombach), SMART (Doran 1981), leading/lagging, KPI-vs-metric—and §Sources records at least three independent sources per attribution with URL, source class, and retrieval date per `spec/claude/research-triangulate/`
- [ ] The spec is **application-agnostic and portfolio-inheritable**: it prescribes process and contract, not a fixed KPI list, and remains referenceable per `spec/project/portfolio-inherited-spec-layer/`

## Open Questions

- **Scanner signal taxonomy.** The exact catalogue of what counts as a KPI signal in source code (domain events, aggregatable entities, state transitions, funnel steps, error surfaces) versus in requirement documents (acceptance criteria, non-functional targets, business outcomes) is enumerated when the `kpi-derive` scanner is authored; this spec fixes the two source surfaces and the goal-linkage rule, not the per-signal heuristics
- **Exact skill/agent names.** Working names `kpi-derive` (skill) and `kpi-signal-scanner` (agent) are confirmed against `<object-noun>-<action>` naming and catalogue discoverability at skill-authoring time
- **north-star enforcement.** Whether a repository may *opt in* to requiring a declared north-star KPI (one primary lagging + supporting leading) via a local override, given the spec keeps it optional by default
- **Cross-artifact drift.** When `project/requirements/<slug>.md` changes after `project/kpis/<slug>.md` is written, whether a drift check between the two (analogous to the translation-vs-canonical drift check) should be a `kpi-derive` operation or delegated to a broader freshness audit

## Sources

The framework attributions in §"Framework anchors" are author-time external assertions triangulated per `spec/claude/research-triangulate/` (author-time tier: at least three independent sources, ordered Primary-first). Retrieval date for every source below: 2026-07-10.

- **GQM (Goal/Question/Metric)**: V. R. Basili, G. Caldiera, H. D. Rombach, *The Goal Question Metric Approach* (Primary), `https://www.cs.umd.edu/users/mvz/handouts/gqm.pdf`; R. van Solingen, E. Berghout, *The Goal/Question/Metric Method: A Practical Guide* (Secondary, Wiley), `https://onlinelibrary.wiley.com/doi/10.1002/0471028959.sof142`; *GQM* (Tertiary, Wikipedia), `https://en.wikipedia.org/wiki/GQM`
- **SMART**: G. T. Doran, "There's a S.M.A.R.T. way to write management's goals and objectives," *Management Review* 70(11), 1981 (Primary, historical origin article); *SMART criteria* (Tertiary, Wikipedia), `https://en.wikipedia.org/wiki/SMART_criteria`; *SMART Goals* (Secondary, MindTools), `https://www.mindtools.com/a4wo118/smart-goals/`; *SMART goals* (Secondary, TechTarget WhatIs), `https://www.techtarget.com/whatis/definition/SMART-SMART-goals`
- **Leading vs lagging indicators**: *Leading vs Lagging Indicators* (Secondary, BMC), `https://www.bmc.com/blogs/leading-vs-lagging-indicators/`; *Leading vs. Lagging Indicators* (Secondary, Amplitude), `https://amplitude.com/blog/leading-lagging-indicators`; *Leading and Lagging Indicators* (Secondary, Klipfolio), `https://www.klipfolio.com/blog/leading-and-lagging-indicators`
- **KPI vs metric**: *Leading vs Lagging / KPI vs metric* (Secondary, BSC Designer), `https://bscdesigner.com/leading-vs-lagging.htm`; *Leading vs. Lagging KPIs* (Secondary, SuccessCOACHING), `https://successcoaching.co/blog/leading-vs-lagging-kpis`; *Metrics and KPIs* (Secondary, Geckoboard), `https://www.geckoboard.com/blog/leading-lagging-or-lost-how-to-find-the-right-key-performance-indicators-for-your-sales-team/`
