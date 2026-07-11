# Requirements — Restructure shared plugins to fit the agent-description token budget

<!--
Produced via the `requirements-elicit` skill, following
spec/project/requirements-elicitation/.
Source: GitHub issue nolte/claude-shared#371.
`c_d` is an uncertainty proxy (self-consistency-derived), not a calibrated
probability. A requirement is `confirmed` only after an explicit teach-back /
authoritative operator answer.
-->

## Bounded context

- **What:** Reduce and cap the aggregate agent-`description` token weight that the
  `claude-shared` marketplace loads into every consumer's main context on every
  turn, and decide (with a documented rationale) whether the `nolte-shared` plugin
  boundary should change. Claude Code counts the `description` frontmatter of
  **every enabled agent** — project-local plus all plugin agents — against an
  undocumented ~15k-token routing budget; the three shared plugins alone contribute
  **~8,988 tokens** (measured 2026-07-11: `nolte-shared` 23 agents/14,298 chars,
  `nolte-engineering` 28/20,424, `nolte-media` 2/1,232), i.e. ~60% of the budget,
  leaving a consumer like `nolte/kamerplanter` only ~6k before it trips the warning.
- **For whom:** every downstream repository that installs the `claude-shared`
  marketplace (the trimming buys headroom for all consumers at once); the triggering
  consumer is `nolte/kamerplanter` (warning observed 2026-07-10). Secondary actor:
  plugin authors who must keep new agent descriptions inside the budget.
- **This pipeline run delivers** (operator decision, 2026-07-11): (1) a written
  structural analysis with measured token costs, (2) the documented plugin-boundary
  decision, (3) an agent-description **contract** plus the remediation that brings the
  shared descriptions under it, and (4) a **regression guardrail** in the test gate.
- **Explicitly out of scope for this run:** the deeper agent/skill **rework**
  (merge / split / retire / rewrite of individual agents or skills beyond their
  descriptions) — that is derived as separate roadmap items / features by the formal
  pipeline this issue routes into. Also out of scope: changing the `nolte-media` or
  `nolte-engineering` boundaries unless the analysis explicitly flags a
  distribution-contract reason; and any edit to a consumer repo's own local
  `.claude/agents/` (each consumer owns its local share).

## Understanding KPI

- Thresholds: `τ_low = 0.4`, `τ_high = 0.8`, self-consistency `k = 2`, question budget = 6 (spec defaults; unchanged)
- `U_gate = min_d c_d` over required dimensions = **0.8**
- Termination: `saturation` — every required dimension ≥ `τ_high` after two focused decision turns; no positive-EVPI question remained (residual items below are low-EVPI design details the downstream feature-decompose resolves).

### Gap matrix

| Dimension | Applicable | `c_d` | Uncertainty source | Evidence event |
|---|---|---|---|---|
| `functional` | yes | 0.9 | specification | Issue body §"Scope of this work" + operator decision "Analyse + Slim + Guardrail zuerst" (2026-07-11) |
| `non_functional` | yes | 0.85 | specification | Operator decision "regression-only guardrail, enforced in validate_skills.py + task test/CI" (2026-07-11) |
| `constraints` | yes | 0.9 | interpretation | CLAUDE.md + `spec/claude/plugin-scoping/` distribution-contract split rule; lockstep versioning; EN-canonical descriptions; teach-back on the split constraint (2026-07-11) |
| `domain_objects` | yes | 0.95 | interpretation | Measured inventory 2026-07-11 (agents, `description` frontmatter, `marketplace.json`, `validate_skills.py`) |
| `actors` | yes | 0.9 | interpretation | Issue §Context (kamerplanter consumer) + routing-engine + plugin-author roles |
| `acceptance_criteria` | yes | 0.85 | specification | Issue §"Acceptance criteria" (5 explicit) refined by the two operator decisions |
| `edge_cases` | yes | 0.8 | interpretation | Routing-regression-from-over-trim and baseline-drift risks named and accepted |
| `scope_boundaries` | yes | 0.9 | specification | Operator decisions on rework depth (this-run vs. spawned features) + boundary openness (2026-07-11) |

## Requirements

- **R1 — Structural analysis.** WHEN this work is executed, the deliverable SHALL
  include a written structural analysis of the current marketplace / plugin / agent /
  skill layout with **measured** per-plugin agent-description token costs and a map of
  capability overlap and delimitation cross-references, reusing the existing
  `agent-review`, `skill-review`, and `skills-agents-sweep` outputs rather than
  redoing them from scratch.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: Issue §"Analysis" checkbox + "Reuse the existing agent-review, skill-review, skills-agents-sweep skills where they fit"

- **R2 — Plugin-boundary decision, openly reasoned.** WHEN the analysis is complete,
  it SHALL state and justify a decision on the `nolte-shared` boundary — split into
  finer, independently-enableable plugins **vs.** keep the monolith and slim it —
  with **no operator pre-commitment**; the decision weighs both freely and documents
  the rationale.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: Operator answer "Analyse entscheidet voll offen" (2026-07-11)

- **R3 — Split-justification constraint.** WHEN R2 concludes in favour of any split,
  the split SHALL be justified by a genuine **distribution-contract** difference
  (runtime/dependency or consumer-audience) per `spec/claude/plugin-scoping/`, and
  SHALL NOT be justified by topic, domain, or agent count alone.
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: CLAUDE.md §"What this repo is" + teach-back on the split rule (2026-07-11)

- **R4 — Agent-description contract.** The shared plugins' agent descriptions SHALL
  conform to a **documented, minimal contract** — a consistent "what it does / when to
  activate / don't use for X → use Y" shape, EN-canonical — with **no embedded
  `user:`/`assistant:`/`<commentary>` example blocks** in any `description` (those
  belong in the agent body), and tightened delimitation chains where a cheaper
  cross-reference suffices.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: Issue §"Agent-description remediation" + §"Observations" 2 & 3

- **R5 — Description remediation.** WHEN the contract (R4) exists, the shared agent
  descriptions SHALL be reduced and normalized to it, trimming **as much as is
  sensible without loss of routing correctness** (no fixed numeric target); the
  achieved aggregate is measured and recorded as the guardrail baseline (R7).
  - _dimension_: `functional` · _status_: `confirmed` · _source_: Operator answer "Nur Regressions-Guardrail, kein fixes Ziel" (2026-07-11)

- **R6 — Routing correctness preserved.** WHEN any agent or skill description is
  trimmed, merged, or reworked, it SHALL remain functionally correct and correctly
  routed — the trim must not degrade Claude Code's ability to select the right
  specialist.
  - _dimension_: `non_functional` · _status_: `confirmed` · _source_: Issue §"Acceptance criteria" bullet 4 ("remain functionally correct and correctly routed")

- **R7 — Regression guardrail in the test gate.** The deliverable SHALL add a check
  in `scripts/validate_skills.py` that measures the aggregate agent-description token
  weight **per plugin**, freezes the post-remediation value as a baseline, and
  **fails** when a plugin's aggregate regresses above that baseline; the check SHALL
  run inside `task test` and therefore the existing CI gate (no new standalone
  workflow required).
  - _dimension_: `non_functional` · _status_: `confirmed` · _source_: Operator answers "regression guardrail" + "In validate_skills.py + task test/CI" (2026-07-11)

- **R8 — Pipeline routing of the deep rework.** WHEN the analysis identifies agents
  or skills warranting merge / split / retire / rewrite **beyond** their descriptions,
  those SHALL be captured as separate roadmap items / features (via the formal
  `roadmap-plan` / `feature-decompose` pipeline), NOT implemented inline in this run.
  - _dimension_: `scope_boundaries` · _status_: `confirmed` · _source_: Operator answer "Analyse + Slim + Guardrail zuerst" (2026-07-11)

## Surviving assumptions / open risks

- **A1 (assumed) — Contract home.** The R4 description contract is *assumed* to be
  documented by extending an existing spec (`spec/claude/skill-agent-frontmatter/`
  or `spec/claude/agent-management/`) rather than a new spec; the exact home is a
  design detail deferred to `feature-decompose`. Below-threshold only on placement,
  not on the contract's existence.
- **A2 (risk) — Routing regression from over-trim.** Aggressive description trimming
  can silently degrade specialist selection (R6). Mitigation expectation: the
  contract keeps the "when to activate / don't use for X → use Y" routing signal;
  spot-check routing on affected agents.
- **A3 (risk) — Guardrail baseline drift.** A regression-only guardrail (R7) freezes
  whatever value remediation achieves; if remediation under-delivers, the baseline
  locks in a mediocre value. Mitigation expectation: set the baseline only *after*
  remediation, and record the measured number in the analysis so it is reviewable.
- **A4 (open, low-EVPI) — Measurement method.** The exact tokenization proxy for the
  guardrail (char/4 estimate vs. a real tokenizer) is left to the implementing
  feature; the analysis records the method it used so the guardrail is reproducible.
