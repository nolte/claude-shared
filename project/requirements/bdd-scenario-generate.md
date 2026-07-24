# Requirements — BDD scenario-generation capability (`bdd-scenario-generate`)

<!--
Produced via the `requirements-elicit` skill, following
spec/project/requirements-elicitation/. Elicited 2026-07-24 as the requirements
gate of an issue-orchestrate run for GitHub issue #459, in worktree
feat/bdd-scenario-generate. `c_d` is an uncertainty proxy (self-consistency-
derived), not a calibrated probability. A requirement is `confirmed` only after an
explicit teach-back / authoritative operator choice.
-->

## Bounded context

- **What:** One `nolte-engineering` capability delivered in one PR: a generator
  **skill** `bdd-scenario-generate` plus a read-only **reviewer agent**, which
  derive readable, English, lektor-checked BDD scenarios from an abstract
  test-case document, grounded in `spec/project/behavior-driven-development/` and
  `spec/project/bdd-page-object-integration/`, focused on the BDD layer.
- **For whom:** Portfolio code repositories that turn a test-case document into a
  BDD E2E suite, and the operator invoking the capability.
- **Out of scope:** implementing or modifying page objects, selectors, or
  application/infra code (delegated to specialists); deriving the test cases
  (input, owned by `test-case-derivation`); the E2E execution mechanics (owned by
  `e2e-test-automation`).
- **Origin:** GitHub issue #459 (operator-authored; enriched 2026-07-24). This
  artifact is the issue-orchestrate requirements gate; the pre-analysis
  decomposition consumes it.

## Understanding KPI

- Thresholds: `τ_low = 0.4`, `τ_high = 0.8`, self-consistency `k = 2`, question
  budget = `5` (1 teach-back + one tightly-coupled 4-question group; spec
  defaults, unchanged)
- `U_gate = min_d c_d` over required dimensions = **0.80**
- Termination: `saturation` (all eight dimensions ≥ `τ_high` via the operator-
  authored issue plus authoritative operator choices Q1–Q4 and the uncorrected
  bounded-context teach-back; no positive-EVPI question remains)

### Gap matrix

| Dimension | Applicable | `c_d` | Uncertainty source | Evidence event |
|---|---|---|---|---|
| `functional` | yes | 0.85 | specification | Issue #459 scope + the two merged specs fix the derivation workflow; Q1/Q2 fix the lektor step, Q3 the delegation, Q4 the artifact set |
| `non_functional` | yes | 0.80 | interpretation | Sibling-capability conventions (validate_skills, `skill-agent-naming`, description budget, EN-canonical prose gates) — CI-enforced repo norms |
| `constraints` | yes | 0.85 | specification | Q4 (skill + reviewer agent, one PR), issue hard constraints (English-only `.feature`, focus-on-BDD with delegation), grounded in two existing specs |
| `domain_objects` | yes | 0.85 | specification | Gherkin vocabulary is fixed and owned by `behavior-driven-development`; the test-case document + work-package + lektorat-finding vocab are named in the issue |
| `actors` | yes | 0.80 | interpretation | Uncorrected teach-back: consumer code repos, operator, the reviewer agent, and the delegated specialists (fullstack-developer, e2e-test-generator, test-case-extractor, lektorat-apply) |
| `acceptance_criteria` | yes | 0.82 | specification | Issue draft AC list + Q1–Q4 choices + sibling-capability acceptance pattern (validator-clean, `task test`/prose gates green) |
| `edge_cases` | yes | 0.82 | specification | k≥2 self-consistency: non-normalizable test case (report back), page-object gap (work-package list, Q3), unresolved lektor findings (advisory, Q2), no non-BDD tests present |
| `scope_boundaries` | yes | 0.88 | specification | Q3 (delegation boundary) + the four neighbour ownerships (both BDD specs, test-case-derivation, e2e-test-automation) already drawn in the merged specs |

## Requirements

- **R1** — The capability SHALL be delivered as two artifacts in one PR under
  `plugins/nolte-engineering/`: a generator skill `bdd-scenario-generate` and a
  read-only reviewer agent, mirroring the generator/reviewer pairing of the
  test-tier suite.
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: Q4 "Generator-Skill + read-only Reviewer-Agent"
- **R2** — The generator SHALL consume an abstract test-case document (TC-IDs +
  behaviors, as produced by `test-case-derivation` / `test-case-extractor`) as
  input and SHALL NOT re-derive the cases.
  - _dimension_: `scope_boundaries` · _status_: `confirmed` · _source_: issue #459 "Input" + teach-back
- **R3** — WHEN generating scenarios, the skill SHALL apply the ordered workflow of
  `spec/project/behavior-driven-development/`: group test cases by capability into
  a `Feature`, derive one `Scenario` per distinct TC-level behavior, map
  precondition→`Given` / action→`When` / expected result→`Then`, tag each scenario
  with its `@TC-<id>`, lift shared preconditions into `Background`, and collapse
  data sets into a `Scenario Outline`.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: issue #459 + the merged BDD spec workflow
- **R4** — The skill SHALL emit English Gherkin `.feature` files plus **thin**
  step-definition skeletons that honor `spec/project/bdd-page-object-integration/`:
  steps stay thin and delegate to the page-object layer, page objects remain
  BDD-independent, and assertions live only in the `Then` binding.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: issue #459 + bdd-page-object-integration decoupling contract
- **R5** — The generated `.feature` files MUST be English regardless of the
  consuming repository's primary language; step-definition docstrings SHOULD also
  be English.
  - _dimension_: `constraints` · _status_: `confirmed` (`.feature` hard rule) / `assumed` (docstrings SHOULD) · _source_: issue #459 "English-only" + A1
- **R6** — The skill SHALL run an editorial (lektor) review of the readable
  scenario wording: it SHALL extract the natural-language lines (`Feature`/`Scenario`
  titles and the Given-When-Then step text) into a temporary Markdown document,
  dispatch `lektorat-apply` in `audit` mode over it, and map the findings back to
  the `.feature` lines. The review is **advisory**: findings SHOULD be resolved
  before completion but a residual finding SHALL NOT hard-block generation.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: Q1 "Extraktion → lektorat-apply" + Q2 "Advisory"
- **R7** — The skill SHALL focus on the BDD layer: it authors scenarios and thin
  step glue only, and SHALL NOT implement or modify page objects, selectors, or
  application/infra code. WHEN it detects a needed page-model or dependency change,
  it SHALL emit a structured **work-package list** (target specialist, touched
  files, goal) for the operator to route, and SHALL NOT dispatch the specialist
  itself.
  - _dimension_: `scope_boundaries` · _status_: `confirmed` · _source_: Q3 "Gemeldete Work-Package-Liste" + issue #459 focus-on-BDD
- **R8** — WHEN a test case cannot be normalized into a single declarative,
  observable behavior, the skill SHALL report it back rather than force a misshapen
  scenario.
  - _dimension_: `edge_cases` · _status_: `confirmed` · _source_: behavior-driven-development derivation workflow
- **R9** — The reviewer agent SHALL be read-only (Read/Grep/Glob): it reviews
  existing BDD scenarios and their thin steps against both BDD specs, returns a
  severity-classified findings report, and applies no edits.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: Q4 (read-only reviewer)
- **R10** — Both artifacts SHALL be spec-conformant: pass `scripts/validate_skills.py`,
  follow `spec/claude/skill-agent-naming/`, keep the agent `description` within the
  CI-guarded budget, and cite both BDD specs in their bodies. The same PR SHALL add
  cross-references where warranted.
  - _dimension_: `non_functional` · _status_: `confirmed` · _source_: sibling-capability conventions (CI-enforced)
- **R11** — The reference profile SHALL be Gherkin + `pytest-bdd`, matching the
  reference profiles of both BDD specs; the core stays tool-neutral.
  - _dimension_: `domain_objects` · _status_: `assumed` · _source_: A2 (single-skeleton default, low EVPI)
- **R12** — The primary actors are: consumer code repositories (invoke the
  capability), the operator (routes the emitted work-package list), the read-only
  reviewer agent, and the delegated specialists (`fullstack-developer`,
  `e2e-test-generator`) plus `lektorat-apply` and `test-case-extractor`.
  - _dimension_: `actors` · _status_: `confirmed` · _source_: uncorrected teach-back

### Domain objects

`test-case document`, `TC-ID`, `Feature`, `Scenario`, `Scenario Outline`,
`Background`, `Given`/`When`/`Then`, feature file (`.feature`), `step definition`,
`page object` (delegated), `lektorat finding`, `work-package` (specialist / files
/ goal), `reviewer findings report`, `@TC-<id>` tag.

## Surviving assumptions / open risks

- **A1 (assumed)** — English enforcement covers the `.feature` files as a hard
  rule; step-definition docstrings SHOULD also be English but are not part of the
  lektor gate. Cheap to confirm at authoring time.
- **A2 (assumed)** — The reference profile ships a single `pytest-bdd` skeleton
  (matching both specs' reference profiles); a second Cucumber-family flavor is a
  possible later addition, not part of this PR.
- **A3 (assumed)** — Artifact names: skill `bdd-scenario-generate`
  (`<object-noun>-<action>`), reviewer agent e.g. `bdd-scenario-reviewer`
  (`<subject>-<role-noun>`), to be validated against `spec/claude/skill-agent-naming/`
  during authoring.
- **A4 (assumed)** — Standard prose gates apply (EN-canonical, Vale error-level,
  LIX); CI authoritative where local Vale is unsyncable.
- **Open risk (for decomposition)** — Whether this capability needs its **own new
  spec** or purely operationalizes the two existing BDD specs. Lean: no new
  methodology spec (the two specs already own the normative content); the skill +
  agent reference them. To be confirmed in the pre-analysis decomposition.
- **Open risk (non-blocking)** — The lektor extraction/back-mapping (R6) is a
  novel mechanism; the exact temp-document shape and finding-line mapping are an
  authoring-time detail, not a requirement.
