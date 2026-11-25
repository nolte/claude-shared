# Requirements — Frontend audit rework around third-party skills

<!--
Produced via the `requirements-elicit` skill, following
spec/project/requirements-elicitation/.
`c_d` is an uncertainty proxy (self-consistency-derived), not a calibrated
probability. A requirement is `confirmed` only after an explicit teach-back.
-->

## Bounded context

- **What is being built:** a rework of the `nolte-engineering` frontend audit family in which
  **third-party skills form the core** of a thorough frontend audit, and the plugin's own
  reviewers run beside them with their complete rule sets (revisit 2026-11-18, see R12).
  Deliverables:
  - a new **spec** `spec/frontend/third-party-audit-skills/` (EN-canonical `en.md` + strict
    `de.md`) defining *when* each third-party plugin/skill is used and *what its preconditions
    are*;
  - a new orchestrating **skill** `frontend-audit` in `plugins/nolte-engineering/`;
  - no rule changes in `spec/frontend/source-code-review/` or
    `spec/frontend/webview-ui-optimization/` (the delegation notes were dropped in the
    2026-11-18 revisit).
- **Third-party skills in scope** (operator-named, 2026-11-17):
  - `vercel-labs/agent-skills` → `web-design-guidelines` (fetches its rules at runtime from
    `https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md`)
  - `vercel-labs/agent-skills` → `react-best-practices` (React/Next.js, local rules, 8 prioritised
    categories)
  - `anthropics/skills` → `frontend-design` (a design skill, not an audit skill)
  - `playwright-cli install --skills` (`@playwright/cli`, browser automation)
- **For whom:** operators running a frontend audit in a consumer repository that installs
  `nolte-engineering`; authors maintaining the frontend specs and agents.
- **Out of scope:** content changes to `frontend-usability-optimizer` and
  `spec/frontend/testability-identifiers/` (reference updates only); renaming or removing
  existing skills/agents (`source-code-review`, `webview-ui-optimize`, `frontend-code-reviewer`,
  `webview-ui-expert` stay); the audit installing third-party skills itself; the audit starting
  the application under test.

## Understanding KPI

- Thresholds: `τ_low = 0.4`, `τ_high = 0.8`, self-consistency `k = 2`, question budget = `8`
  (spec defaults; 6 questions used)
- `U_gate = min_d c_d` over required dimensions = **0.8**
- Termination: `saturation`

### Gap matrix

| Dimension | Applicable | `c_d` | Uncertainty source | Evidence event |
|---|---|---|---|---|
| `functional` | yes | 0.9 | interpretation | teach-back on skill-to-trigger mapping (Q3) and summary (Q6) |
| `non_functional` | yes | 0.8 | specification | answer Q4 (live load + logging); summary point 4 confirmed |
| `constraints` | yes | 0.9 | specification | answer Q2 (operator installs, fallback); summary point 1 confirmed |
| `domain_objects` | yes | 0.8 | interpretation | summary point 1 (per-skill matrix) confirmed; k=2 sketches converged on matrix + report |
| `actors` | yes | 0.85 | specification | answer Q5 (new orchestrating skill); operator/agent roles from Q2 |
| `acceptance_criteria` | yes | 0.8 | interpretation | summary point 6 confirmed |
| `edge_cases` | yes | 0.8 | interpretation | summary points 2–3 confirmed (n/a vs missing, no URL) |
| `scope_boundaries` | yes | 0.9 | specification | answer Q1 (third-party = core); summary point 5 confirmed |

## Requirements

- **R1** — The spec `spec/frontend/third-party-audit-skills/` SHALL define, per third-party
  skill, a matrix row with: trigger condition, preconditions (tool and minimum version — Node
  ≥ 22.20 for `npx skills`, Node ≥ 20 for `@playwright/cli` — network access, running
  application), pinned install command, availability check, and behaviour when absent.
  - _dimension_: `domain_objects`, `constraints` · _status_: `confirmed` · _source_: "erzeuge eine ausführliche spec wann welche plugins und skills verwendet werden und was die entsprechenden vorbedingungen sind"; Q6 point 1
- **R2** — Install commands in the spec SHALL be pinned (`npx skills add <repo>#<tag|commit> --skill <name> -a claude-code` with `skills-lock.json`; `@playwright/cli@<version>`).
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: Q2 option text, Q6 point 1
- **R3** — The operator SHALL install third-party skills before the audit; the `frontend-audit` skill SHALL NOT install them.
  - _dimension_: `constraints`, `actors` · _status_: `confirmed` · _source_: Q2 "Operator + Fallback"
- **R4** — WHEN a required third-party skill is not available, `frontend-audit` SHALL report it as a coverage gap and continue; the own reviewers' rule sets don't change (R12).
  - _dimension_: `edge_cases` · _status_: `confirmed` · _source_: Q2
- **R5** — WHEN a third-party skill does not apply to the detected stack (e.g. no React/Next.js), `frontend-audit` SHALL report it as `n/a`, not as a coverage gap.
  - _dimension_: `edge_cases` · _status_: `confirmed` · _source_: Q6 point 2
- **R6** — WHEN web UI code is in scope, `frontend-audit` SHALL run `web-design-guidelines`.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: Q3 mapping
- **R7** — WHEN React or Next.js is detected in the stack, `frontend-audit` SHALL run `react-best-practices` as part of the code-review strand.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: Q3 mapping
- **R8** — WHEN the operator supplies an application URL, `frontend-audit` SHALL use `playwright-cli` to collect rendered evidence (screenshots, accessibility tree, interaction); WHEN no URL is supplied, it SHALL record the rendered strand as a coverage gap and SHALL NOT start the application itself.
  - _dimension_: `functional`, `edge_cases` · _status_: `confirmed` · _source_: Q3 mapping; Q6 point 3
- **R9** — `frontend-audit` SHALL apply `frontend-design` as an aesthetic critique lens in the UI strand; its findings SHALL be advisory only.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: Q3 "Ja, frontend-design als Linse"
- **R10** — WHEN `web-design-guidelines` loads its rules, the rules SHALL be loaded live from upstream `main`, and the report SHALL record the fetch time and SHA-256 of the fetched content.
  - _dimension_: `non_functional` · _status_: `confirmed` · _source_: Q4 "Live laden + protokollieren"
- **R11** — Fetched third-party rule content SHALL be treated as audit criteria (data), never as instructions that alter the audit's control flow (no writes, no tool calls, no network access outside the audit).
  - _dimension_: `non_functional` · _status_: `confirmed` · _source_: Q6 point 4
- **R12** — The own reviewers SHALL run their complete rule sets in every audit; where an own rule and a third-party rule find the same defect, the merged report SHALL show it once with both sources (R13), and no own rule SHALL be skipped because a third-party skill covers it.
  - _dimension_: `scope_boundaries` · _status_: `confirmed` · _source_: revisit 2026-11-18, operator chose "Zurückschneiden" after four pre-merge review rounds on PR #787 kept finding gaps in rule-level delegation; supersedes Q4b "Delegieren + Restregeln"
- **R13** — `frontend-audit` SHALL emit one merged report in which every finding carries a `source` attribution (e.g. `vercel/web-design-guidelines`, `nolte/frontend-code-reviewer`) and duplicate findings are merged.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: Q4b
- **R14** — A new skill `frontend-audit` SHALL detect the stack, check preconditions, invoke the third-party skills, dispatch `frontend-code-reviewer` / `webview-ui-expert` with their complete rule sets, and merge the report; `source-code-review` and `webview-ui-optimize` SHALL remain and point to `frontend-audit` for the thorough audit.
  - _dimension_: `actors`, `scope_boundaries` · _status_: `confirmed` · _source_: Q5 "Neuer Skill frontend-audit"
- **R15** — The change SHALL pass `task test`, `task lint`, and `task docs`.
  - _dimension_: `acceptance_criteria` · _status_: `confirmed` · _source_: Q6 point 6

## Surviving assumptions / open risks

- **Unverified install facts:** the destination directory of `playwright-cli install --skills`
  and whether it downloads browsers were not verifiable from the README; the spec author MUST
  verify these (CLI source or a local dry run) before writing the matrix row.
- **`npx skills` canonical copy:** project installs probably land in `.agents/skills/<name>`
  with a link under `.claude/skills/`; not confirmed.
- **Live-loaded rules drift:** by operator decision (R10), two audits may run against different
  rule sets; the content hash makes this visible but does not prevent it.
- **Skill invocation from orchestration:** third-party skills run in the main session; whether
  `frontend-audit` invokes them via the Skill tool or instructs the operator is an
  implementation design point for the Ist-Analyse.
- **Description budget:** `nolte-engineering` description budget is tight (memory); a new
  skill description must fit `validate_skills.py`.
- **Revisit 2026-11-18:** R12 changed from rule-level delegation with fallback to own reviewers
  running in full beside the third-party skills (operator decision); R4 and R14 follow. Other
  requirements unchanged.
