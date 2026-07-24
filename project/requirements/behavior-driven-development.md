# Requirements — Behavior-Driven Development methodology spec (tool-neutral)

<!--
Produced via the `requirements-elicit` skill, following
spec/project/requirements-elicitation/.
Elicited 2026-07-24 in worktree feat/bdd-spec as the plan-mandated gate (step 1)
before authoring. `c_d` is an uncertainty proxy (self-consistency-derived), not a
calibrated probability. A requirement is `confirmed` only after an explicit
teach-back / authoritative operator choice.
-->

## Bounded context

- **What:** One new, tool-neutral normative spec `spec/project/behavior-driven-development/`
  (EN canonical + DE translation), authored via `/nolte-shared:spec`. It owns BDD
  as a whole — collaborative example discovery (Example Mapping, Three Amigos),
  the Gherkin / Given-When-Then scenario language, declarative scenario design,
  ubiquitous language, living documentation, and step-definition principles —
  **plus** the derivation path *test-case document → executable BDD scenarios*.
  The normative core stays tier-neutral; an illustrative, non-prescriptive
  Gherkin/Cucumber reference profile makes it concrete.
- **For whom:** Written as the normative foundation a later `nolte-engineering`
  skill consumes to design and implement a BDD E2E test from a test-case
  document. On-page readers are test/feature authors in the nolte portfolio and
  that future consuming skill. E2E is the primary application; the core is tier-
  neutral so BDD scenarios can also drive integration/component tiers.
- **Out of scope:** the consuming skill/agent itself (separate follow-on work,
  not scaffolded in this worktree); *when* in the process examples are discovered
  (stays with `test-cycle-case-determination`); abstract black-box TC derivation
  (stays with `test-case-derivation`); execution mechanics — page objects, waits,
  screenshots, traceability plumbing (stays with `e2e-test-automation`); the
  selector contract (stays with `testability-identifiers`). This is a **spec-only
  PR** — no skill, no agent, no version bump, no `marketplace.json` change.
- **Origin:** operator-authored worktree plan `.resume/bdd-spec/plan.md`; the two
  load-bearing design choices (standalone tool-neutral spec; illustrative
  reference profile) were settled with the operator before work, and the three
  non-blocking plan open questions (§3) are confirmed in this elicitation.

## Understanding KPI

- Thresholds: `τ_low = 0.4`, `τ_high = 0.8`, self-consistency `k = 2`, question
  budget = `6` (1 teach-back turn + 1 tightly-coupled 4-question group; spec
  defaults, unchanged)
- `U_gate = min_d c_d` over required dimensions = **0.80**
- Termination: `saturation` (all eight dimensions ≥ `τ_high` via the operator-
  authored plan plus authoritative operator choices Q1–Q4 and the uncorrected
  bounded-context teach-back; no positive-EVPI question remains)

### Gap matrix

| Dimension | Applicable | `c_d` | Uncertainty source | Evidence event |
|---|---|---|---|---|
| `functional` | yes | 0.85 | specification | Plan §1/§4 coverage list + invocation brief fix the BDD surface; Q1 operator choice ("normative step-workflow") fixes the derivation-path depth |
| `non_functional` | yes | 0.82 | interpretation | Plan §5 invariants: EN-canonical + DE lockstep, frontmatter-less plaintext-header format, Vale error-level + LIX prose gates over `spec/**/en.md` — CI-enforced repo conventions |
| `constraints` | yes | 0.85 | specification | Q4 default block confirmed (slug, DE-now, `Portfolio-Scope: portfolio`) + plan §5 "spec-only, no skill/agent, no version bump"; uncorrected context teach-back |
| `domain_objects` | yes | 0.85 | specification | Gherkin vocabulary is a fixed, well-known lexicon; Q2 choice (appendix + `templates/`) fixes how it is instantiated illustratively |
| `actors` | yes | 0.80 | interpretation | Context teach-back (uncorrected): test/feature authors + the future consuming `nolte-engineering` BDD skill as readers; `Readers:` line target |
| `acceptance_criteria` | yes | 0.82 | specification | Plan §6 step 6 + sibling-spec acceptance pattern: Vale-clean EN, LIX readability, `task test` + prose/link checks green, neighbour-format match |
| `edge_cases` | yes | 0.82 | specification | k≥2 self-consistency check on "edge cases for a methodology spec" converged on anti-pattern coverage (imperative/UI-coupled scenarios, assertions-in-Gherkin, scenario-per-method); plan §4 names "anti-patterns" |
| `scope_boundaries` | yes | 0.88 | specification | Plan §3 boundary paragraph (4 neighbour specs) + Q3 operator choice (SHOULD-line edit + full reciprocal cross-refs) fix the exact blast radius |

## Requirements

- **R1** — The capability SHALL be delivered as a **spec-only** change in one PR:
  `spec/project/behavior-driven-development/en.md` (canonical) + `de.md`
  (translation), authored via `/nolte-shared:spec`. It SHALL NOT scaffold the
  consuming skill/agent, bump any version, or touch `marketplace.json`.
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: plan §5 invariants + uncorrected context teach-back
- **R2** — The spec SHALL be a standalone, **tool-neutral** BDD methodology spec
  whose normative core is **tier-neutral** (E2E is the primary application, but
  scenarios may also drive integration/component tiers). Its `Portfolio-Scope:`
  SHALL be `portfolio` (methodology is portfolio-wide, like `quality-gate`).
  - _dimension_: `scope_boundaries` · _status_: `confirmed` · _source_: plan §3 design decision + Q4 default block
- **R3** — The requirement catalog SHALL cover the BDD methodology surface,
  grouped thematically: collaborative discovery (Example Mapping, Three Amigos);
  scenario language (Gherkin, Given-When-Then, declarative vs imperative, one
  behaviour per scenario, `Background`, `Scenario Outline`, tags); ubiquitous
  language; living documentation; and step-definition design (thin steps, reuse,
  no assertions in Gherkin).
  - _dimension_: `functional` · _status_: `confirmed` · _source_: invocation brief + plan §4 step 2
- **R4** — The derivation path *test-case document → executable BDD scenarios*
  SHALL be a **normative ordered workflow** with MUST/SHOULD steps: mapping a
  TC's fields onto Gherkin elements, one scenario per TC-level behaviour, and
  explicit traceability between the TC-ID and the scenario (e.g. a tag), so the
  consuming skill inherits a fixed procedure rather than re-deriving one.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: Q1 operator choice "Normativer Schritt-Workflow"
- **R5** — The spec SHALL consume a test-case document as **input** and SHALL NOT
  re-derive abstract black-box test cases; that derivation stays the concern of
  `spec/project/test-case-derivation/`.
  - _dimension_: `scope_boundaries` · _status_: `confirmed` · _source_: plan §3 boundary paragraph
- **R6** — The Non-Goals section SHALL draw and link the four neighbour
  boundaries: `test-cycle-case-determination` (owns *when* examples are
  discovered), `test-case-derivation` (owns abstract TC derivation),
  `e2e-test-automation` (owns execution mechanics), and
  `testability-identifiers` (owns the selector contract).
  - _dimension_: `scope_boundaries` · _status_: `confirmed` · _source_: plan §3 boundary paragraph
- **R7** — The spec SHALL include an **illustrative, explicitly non-prescriptive**
  reference profile delivered as BOTH a `## Reference profile` appendix section
  AND a `templates/` directory carrying a real `.feature` file plus a
  step-definition skeleton (one Cucumber-family flavour), mirroring the
  `e2e-test-automation` `templates/` precedent. The normative core SHALL remain
  tool-neutral regardless of the profile.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: Q2 operator choice "Appendix + templates/-Dir"
- **R8** — The same PR SHALL edit neighbour specs (EN + DE in lockstep):
  (a) extend the existing BDD/Specification-by-Example **SHOULD** line in
  `test-cycle-case-determination` to point at this spec, and (b) add reciprocal
  `[Rn]` cross-reference pointers in `test-case-derivation` and
  `e2e-test-automation`.
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: Q3 operator choice "SHOULD-Zeile + volle Cross-Refs"
- **R9** — The spec SHALL address the **BDD-on-E2E** specifics as its primary
  application: the scenario/spec layer sits *above* the E2E execution layer
  (page objects, waits, selectors), which it references rather than re-specifies.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: invocation brief "E2E ist primärer Anwendungsfall" + plan §4 step 2
- **R10** — The spec SHALL name BDD **anti-patterns** as explicit guidance
  (imperative/UI-coupled scenarios, assertions leaking into Gherkin,
  scenario-per-method, conjunctive/incidental-detail steps), so the consuming
  skill can avoid them.
  - _dimension_: `edge_cases` · _status_: `confirmed` · _source_: plan §4 step 2 "anti-patterns" + k≥2 self-consistency check
- **R11** — The spec SHALL follow the repository's authoring conventions:
  frontmatter-less plaintext-header format matching the neighbour specs
  (`# Title` / `Status: draft` / `Portfolio-Scope:` / `## Context` with a
  "Relationship to the existing specs" paragraph and a `Readers:` line / `## Goals`
  / `## Non-Goals` / `## Requirements` / `## References` `[Rn]` / `## Open Questions`),
  `**MUST**/**SHOULD**/**MAY**` requirement bullets, and backtick-path + `[Rn]`
  cross-references.
  - _dimension_: `non_functional` · _status_: `confirmed` · _source_: plan §5 invariants + neighbour-spec precedent
- **R12** — The named readers/actors SHALL be: test/feature authors in the
  portfolio, and the future `nolte-engineering` BDD skill that consumes this spec
  to turn a test-case document into a runnable BDD E2E test.
  - _dimension_: `actors` · _status_: `confirmed` · _source_: uncorrected context teach-back
- **R13** — Acceptance for the change SHALL be: EN is Vale-clean under the CI
  `lint:prose` error-level rules, LIX readability holds, `task test` and the
  prose/link checks pass, DE is generated and kept strictly in sync via `/spec`,
  and the touched specs are autolinked by `/nolte-shared:pull-request-create`.
  - _dimension_: `acceptance_criteria` · _status_: `confirmed` · _source_: plan §6 steps 5–7 + sibling-spec acceptance pattern

### Domain objects

`Feature`, `Scenario`, `Scenario Outline` / `Examples`, `Background`, the
`Given`/`When`/`Then`/`And`/`But` steps, `step definition`, feature file
(`.feature`), `tag`, Example Mapping cards (rule / example / question), Three
Amigos, ubiquitous language, living documentation, declarative-vs-imperative
scenario, the test-case document (input), TC-ID ↔ scenario traceability, the
Cucumber family (Cucumber-JVM / pytest-bdd / behave / Cucumber.js).

## Surviving assumptions / open risks

- **A1 (assumed)** — Slug `behavior-driven-development` (US spelling "behavior"
  for Vale); EN canonical + DE shipped in the same PR via `/spec` driven by
  `spec/.spec-config.yml`; `Portfolio-Scope: portfolio`. These are the three
  plan-§3 defaults, confirmed as a block (Q4) — recorded here as the operative
  settings, mechanically re-checkable at authoring time.
- **A2 (assumed)** — The `templates/` step-definition skeleton (R7) uses the
  **pytest-bdd** flavour, following the repo's Python/pytest reference-profile
  precedent (`e2e-test-automation` uses Selenium + pytest). The concrete family
  is an authoring-time detail; the choice does not change the tool-neutral core.
- **A3 (assumed)** — Standard prose gates apply as to every spec: EN-canonical
  (`.spec-config.yml`), DE in the same PR, Vale error-level rules (contractions,
  unspaced em-dashes not adjacent to code/bold, punctuation inside quotes, US
  spelling), LIX readability. Local Vale is unsyncable → `--no-verify` + CI
  authoritative.
- **Open risk (non-blocking)** — Whether `test-pyramid-foundation` /
  `test-tier-*` should gain reciprocal pointers to the new spec is left to
  authoring-time judgment; the plan names them as adjacent prior art (structure
  axis) but not as mandated cross-references (R8 fixes the mandated set).
- **Open risk (non-blocking)** — The exact new `[Rn]` reference IDs and the
  precise wording of the extended SHOULD line in `test-cycle-case-determination`
  (R8) are settled during authoring; the elicitation fixes the *set* of edits,
  not their final prose.
