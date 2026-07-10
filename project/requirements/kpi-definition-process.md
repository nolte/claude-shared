# Requirements — KPI determination & definition process (portfolio spec + nolte-engineering skill + read-only scanner)

<!--
Produced via the `requirements-elicit` skill, following
spec/project/requirements-elicitation/.
`c_d` is an uncertainty proxy (self-consistency-derived), not a calibrated
probability. A requirement is `confirmed` only after an explicit teach-back.
-->

## Bounded context

- **What is being built:** two coupled artefacts —
  1. a **methodology spec** `spec/project/kpi-definition-process/` (EN-canonical + DE translation,
     **`Scope: portfolio`**) that defines the **process for determining and defining project-specific
     KPIs** of a business application — which KPIs matter for a given project and how each is defined
     (name, definition, formula intent, unit, target/threshold, leading/lagging, owner, business-goal
     linkage, data-source pointer, rationale). It grounds KPI quality in an established framework
     (GQM as the derivation backbone, SMART as the per-KPI quality gate, leading/lagging classification,
     an explicit KPI-vs-metric boundary); and
  2. a **`nolte-engineering` plugin skill** (`kpi-derive`, working name) plus **one read-only
     dual-source scanner agent** that mines a concrete application's **source code** *and* its
     **requirement documents** for candidate KPIs, and — under operator confirmation — writes the
     derived KPI-definition artefact to `project/kpis/<slug>.md`.
- **For whom:** teams/repos that need to determine the meaningful KPIs of their business application
  (the derivation consumers); the spec readers; the skill/agent authors; and — because the spec is
  `portfolio` — consumer repos that inherit it by-reference to derive their own KPIs.
- **The fourth sibling** in the methodology-spec → skill → engineering-artefact family, alongside
  `spec/project/dockerfile-best-practices/`, `spec/project/kubernetes-deployment-best-practices/`, and
  `spec/project/bjw-s-common-chart-deployment/` — matching their shape (skill orchestrates + owns the
  gate/write, read-only scanner agent mines the repo, deep-research grounding). It differs on two axes:
  it is **`portfolio`** (inheritable), not `local`, and its scanner reads **two** input surfaces.
- **Hard out-of-scope boundary (load-bearing):** **measurement, instrumentation, telemetry,
  collection, and dashboarding.** The process ends at *which KPIs count and how each is defined* — never
  *how they are recorded, computed at runtime, or displayed*. The spec MUST call this boundary out
  explicitly. The `data-source-pointer` field names *where the data would come from*, not a wired-up
  metric.

## Understanding KPI

- Thresholds: `τ_low = 0.4`, `τ_high = 0.8`, self-consistency `k = 2`, question budget = `~6`
  (spec defaults; unchanged). Self-consistency was applied per decision cluster by offering the divergent
  readings as discrete options (rounds 1–2) rather than an open "can you clarify?".
- `U_gate = min_d c_d` over required dimensions = **0.80** (weakest link: `edge_cases`, at threshold).
  All six plan open questions (A–F) were settled by explicit operator sign-off across two structured
  decision rounds, then a consolidated teach-back confirmed with **"passt"**.
- Termination: **saturation.** A–F are resolved; only narrow spec-authoring detail remains (exact
  skill/agent names, exact GQM/SMART wording after the grounding research), routed to the `/nolte-shared:spec`
  authoring step and the framework-research step — not to the operator. Listed below as residual risk.

### Gap matrix

| Dimension | Applicable | `c_d` | Uncertainty source | Evidence event |
|---|---|---|---|---|
| `functional` | yes | 0.90 | interpretation | E sign-off (skill + 1 dual-source scanner; derive + write) + A sign-off (output shape) + teach-back "passt" |
| `non_functional` | yes | 0.86 | interpretation | DRY skill/scanner split, interactive-skill vs read-only-scanner, routing budget, portfolio distribution (plan §5); teach-back |
| `constraints` | yes | 0.88 | interpretation | C sign-off (`Scope: portfolio` + inheritance affordance), EN-canonical+DE, marketplace-only, `<object>-<action>` naming, Vale-from-worktree, `task test` |
| `domain_objects` | yes | 0.88 | interpretation | A + F sign-off: per-KPI field contract (R2) + GQM/SMART/leading-lagging/KPI≠metric framework (R3) |
| `actors` | yes | 0.85 | interpretation | Teach-back confirmed (KPI-determining teams; spec readers; skill authors; consumer repos inheriting by-reference) |
| `acceptance_criteria` | yes | 0.85 | interpretation | A/D/process sign-off: output to `project/kpis/<slug>.md`, soft-gate input behaviour, process gates (R7/R8/R11) |
| `edge_cases` | yes | 0.80 | specification | D sign-off settles missing-requirement fallback; code-only repo, KPI-vs-metric false positives, portfolio-inheritance resolution settled in principle, exact wording at authoring |
| `scope_boundaries` | yes | 0.90 | interpretation | Explicit hard out-of-scope boundary (no measurement/instrumentation/telemetry/dashboarding) confirmed in teach-back; B sign-off (plugin home) |

## Requirements

<!-- EARS/CNL form; tagged confirmed/assumed with traceability. -->

### Spec (EN canonical + DE in sync)

- **R1** — WHEN the `kpi-definition-process` spec is authored, it SHALL define the **process for
  determining and defining** project-specific KPIs of a business application, and SHALL declare a **hard
  out-of-scope boundary** excluding measurement, instrumentation, telemetry, collection, and dashboarding
  — the process ends at *which KPIs count and how each is defined*.
  - _dimension_: `functional`, `scope_boundaries` · _status_: `confirmed` · _source_: plan §1 + teach-back "passt"
- **R2** — WHEN the spec defines the per-KPI output contract, it SHALL mandate the fields
  `id, name, definition, formula-intent, unit, target/threshold, type (leading|lagging), owner,
  goal-linkage, data-source-pointer, rationale`; `formula-intent` and `data-source-pointer` capture
  *intent and provenance*, never a wired-up runtime metric (keeps the out-of-scope boundary honest).
  - _dimension_: `domain_objects`, `acceptance_criteria` · _status_: `confirmed` (round 1 Q-A) · _source_: A sign-off + teach-back
- **R3** — WHEN the spec grounds KPI quality, it SHALL canonise **GQM (Goal→Question→Metric)** as the
  derivation backbone (business goals / requirements → questions → candidate KPIs), **SMART** as the
  per-KPI quality gate, **leading vs lagging** as a classification axis, and an explicit
  **KPI-vs-metric** distinction (north-star optional). The exact framework wording SHALL be verified via
  a short deep-research/Workflow grounding pass, as the sibling specs were.
  - _dimension_: `domain_objects`, `non_functional` · _status_: `confirmed` (round 2 Q-F) · _source_: F sign-off + teach-back
- **R4** — WHEN the spec is authored `Scope: portfolio`, it SHALL carry the portfolio-inheritance
  affordance per `spec/project/portfolio-inherited-spec-layer/` (HYBRID precedence, `inherits:` key,
  `${CLAUDE_PLUGIN_ROOT}/spec/` by-reference resolution) so a consumer repo can inherit the KPI process
  and derive its own KPIs without copying the spec.
  - _dimension_: `constraints` · _status_: `confirmed` (round 1 Q-C: portfolio) · _source_: C sign-off + teach-back
- **R5** — WHEN the canonical `en.md` is authored, the `de.md` translation SHALL be kept in strict sync
  via the `/nolte-shared:spec` translation path, EN canonical per `.spec-config.yml`, drift check passing.
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: plan §5 invariants

### Skill + scanner agent (nolte-engineering plugin)

- **R6** — WHEN the tooling is authored, it SHALL take the form of a **`kpi-derive` skill** (working name)
  plus **one read-only dual-source scanner agent** (working name `kpi-signal-scanner`): the scanner
  performs detection only — mining **both** the app's source code (`src/`) and its requirement documents
  (`project/requirements/`, `project/goals.md`, `project/mission.md`) for candidate KPI signals — and the
  skill owns KPI selection, definition, the operator confirmation, and the write. Never a lone
  self-contained skill and never a scanner pair (single dual-source scanner, to respect the agent
  routing-budget).
  - _dimension_: `functional`, `non_functional` · _status_: `confirmed` (round 1 Q-E) · _source_: E sign-off + teach-back
- **R7** — WHEN the skill writes its result, it SHALL emit **`project/kpis/<slug>.md`** mirroring the
  layout of `project/requirements/` — a bounded-context/source header plus one structured block per KPI
  carrying the R2 fields — and each KPI's `goal-linkage` SHALL point back to the originating requirement /
  goal (traceability).
  - _dimension_: `functional`, `acceptance_criteria` · _status_: `confirmed` (round 1 Q-A) · _source_: A sign-off + teach-back
- **R8** — WHEN the skill gathers inputs, it SHALL apply a **consume-if-present / soft-gate** priority:
  (1) an existing `project/requirements/<slug>.md` artefact, (2) `project/goals.md` / `project/mission.md`,
  (3) source-code signals. WHEN no requirement artefact is present it SHALL **warn and recommend running
  `requirements-elicit` first**, but SHALL NOT block derivation (a code-only repo can still derive from
  goals + source).
  - _dimension_: `edge_cases`, `acceptance_criteria` · _status_: `confirmed` (round 2 Q-D) · _source_: D sign-off + teach-back
- **R9** — WHEN the tooling runs, the **skill SHALL be interactive** (KPI selection/definition is a
  judgement call requiring operator confirmation before the artefact is written), and the **scanner agent
  SHALL be read-only and fire-and-forget** (mirroring `dockerfile-audit-scanner` / `test-case-extractor`).
  - _dimension_: `non_functional` · _status_: `confirmed` · _source_: plan §3/§5 + teach-back
- **R10** — WHEN the skill and agent are authored, they SHALL ship **only via the plugin marketplace**
  under `plugins/nolte-engineering/`, follow `<object-noun>-<action>` naming, keep the agent `description`
  ≤ 1024 / `summary` ≤ 200, point `see_also`/`dont_use_when` only at existing catalog-discoverable
  targets, and respect the agent-description routing-budget ceiling (the added scanner counts against it).
  - _dimension_: `constraints`, `non_functional` · _status_: `confirmed` · _source_: plan §5 + B/E sign-off

### Process / quality

- **R11** — WHEN the change is prepared for review, `task test` (`validate_skills.py`: frontmatter +
  naming + description budget) SHALL be green, the changed spec prose SHALL be Vale/lektorat clean (Vale
  run **from the worktree**), `task docs` SHALL regenerate the catalog/i18n cleanly, the plugin SHALL
  dogfood-load to smoke-test the skill, and the PR (via `/nolte-shared:pull-request-create`) SHALL
  autolink the new spec.
  - _dimension_: `acceptance_criteria` · _status_: `confirmed` · _source_: plan §4 steps 4–8

## Surviving assumptions / open risks

**Resolved (operator sign-off across two structured rounds A–F + consolidated teach-back "passt"):**

- ✅ **A (output artefact):** Markdown `project/kpis/<slug>.md` mirroring `project/requirements/`,
  per-KPI structured block (R2), linked back to the requirement artefact.
- ✅ **B (plugin home):** `nolte-engineering` (tool reads source code → code-bearing audience);
  the spec itself is repo-wide under `spec/project/`.
- ✅ **C (spec scope):** **`portfolio`** (inheritable by-reference), not `local` — the one deliberate
  deviation from the three sibling best-practice specs. Carries the portfolio-inheritance affordance (R4).
- ✅ **D (requirements coupling):** consume-if-present **soft-gate** — warn + recommend `requirements-elicit`
  when absent, never block (R8).
- ✅ **E (decomposition):** skill + **one dual-source** read-only scanner (source code + requirement docs),
  not a scanner pair and not a separate definer agent (R6).
- ✅ **F (framework grounding):** GQM backbone + SMART per-KPI gate + leading/lagging classification +
  explicit KPI-vs-metric boundary; exact canon research-verified (R3).

**Remaining residual risk (narrow authoring detail; routed to research + `/nolte-shared:spec`, NOT to the operator):**

- **Exact skill/agent names** — working names `kpi-derive` (skill) / `kpi-signal-scanner` (agent);
  confirm against `<object-noun>-<action>` and catalog-discoverability at skill-authoring time.
- **Exact GQM/SMART wording + north-star inclusion** — settled in principle (R3); the framework-grounding
  research fixes the authoritative phrasing and citations before the spec canonises them.
- **Portfolio-inheritance resolution mechanics** — reuse the existing `portfolio-inherited-spec-layer`
  pattern verbatim (HYBRID precedence, `inherits:`, `${CLAUDE_PLUGIN_ROOT}/spec/`); no new mechanism.
- **Scanner signal taxonomy** — what concretely counts as a KPI signal in source code (domain events,
  aggregatable entities, state transitions, funnels) vs in requirement docs (acceptance criteria,
  non-functional targets, business goals); enumerated during spec authoring, grounded by the research.

**Constraint reminders (confirmed, not risks):** EN canonical + DE in sync; primary checkout stays on
`develop` (all work in this worktree); the skill/agent ship via the marketplace, never copied into a
consumer's `.claude/skills/`; all generated spec/config prose is English (DE is the translation); the
hard out-of-scope boundary (no measurement/instrumentation/telemetry/dashboarding) is non-negotiable.
