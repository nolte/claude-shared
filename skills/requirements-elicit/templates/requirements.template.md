# Requirements — {{Subject}}

<!--
Produced via the `requirements-elicit` skill, following
spec/project/requirements-elicitation/.
Do not record a requirement before declaring the bounded context below.
`c_d` is an uncertainty proxy (self-consistency-derived), not a calibrated
probability. A requirement is `confirmed` only after an explicit teach-back.
-->

## Bounded context

<!-- What is being built, for whom, and what is explicitly out of scope.
     One short paragraph or a bullet list. Required before any requirement. -->

-

## Understanding KPI

- Thresholds: `τ_low = {{0.4}}`, `τ_high = {{0.8}}`, self-consistency `k = {{2}}`, question budget = `{{n}}`
  <!-- spec defaults; override here with a one-line rationale if changed -->
- `U_gate = min_d c_d` over required dimensions = **{{0.0}}**
- Termination: `{{saturation | question-budget-capped}}`

### Gap matrix

| Dimension | Applicable | `c_d` | Uncertainty source | Evidence event |
|---|---|---|---|---|
| `functional` | {{yes / n/a — reason}} | {{0.0}} | {{specification / interpretation}} | {{answer / teach-back / confirmed assumption}} |
| `non_functional` | | | | |
| `constraints` | | | | |
| `domain_objects` | | | | |
| `actors` | | | | |
| `acceptance_criteria` | | | | |
| `edge_cases` | | | | |
| `scope_boundaries` | | | | |

## Requirements

<!-- Each requirement in EARS/CNL form, tagged confirmed/assumed, with
     traceability to the user utterance(s) that produced it. A requirement that
     resists normalization is recorded as "not-yet-understood" instead. -->

- **R1** — WHEN {{trigger}}, the {{system}} SHALL {{response}}.
  - _dimension_: `{{functional}}` · _status_: `{{confirmed|assumed}}` · _source_: "{{user utterance}}"

## Surviving assumptions / open risks

<!-- Every `assumed` entry and every below-`τ_high` cell, named as a risk.
     On a budget-capped stop, this section MUST list each below-threshold
     dimension explicitly rather than treating it as understood. -->

-
