---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "459"
classification: "feature-request"
secondary-classes: []
route: "direct"
status: draft
created: "2026-07-24"
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #459 — feat(nolte-engineering): BDD scenario-generation skill — readable English BDD tests from a test-case document, lektor-checked
- **URL**: <https://github.com/nolte/claude-shared/issues/459>
- **Labels**: enhancement, feat
- **Linked items**: none (0 comments, no linked/closing PRs)
- **Prior art checked**: no existing `bdd-scenario`/`gherkin` skill or agent under `plugins/nolte-engineering/`; both grounding specs merged (`behavior-driven-development` #451, `bdd-page-object-integration` #474); no `project/features/` or roadmap item for this capability

## Classification

- **Primary class**: feature-request
- **Secondary class(es)**: none
- **Rationale**: builds a new `nolte-engineering` capability (a generator skill + a read-only reviewer agent) operationalizing two merged specs; not a bug/spec-change/security issue.

## Requirements gate

- **Artifact**: `project/requirements/bdd-scenario-generate.md` (elicited via `requirements-elicit`, this run)
- **U_gate**: 0.80 (≥ τ_high = 0.80), termination `saturation`; all eight dimensions confirmed via issue #459 + operator choices Q1–Q4
- **Decisions locked**: (Q1) lektor via extraction → `lektorat-apply` on temp Markdown, findings mapped back; (Q2) lektor is **advisory**, not a hard gate; (Q3) page-model gaps emitted as a **work-package list**, no self-dispatch; (Q4) two artifacts — generator **skill** + read-only reviewer **agent**

## Scope

- **In scope**: a generator skill `bdd-scenario-generate` and a read-only reviewer agent under `plugins/nolte-engineering/`, delivered in one PR, that derive readable **English** BDD scenarios (Gherkin `.feature` + thin steps) from a test-case document per the two BDD specs, run an advisory lektor review of the wording, and emit a work-package list for page-model/dependency gaps.
- **Out of scope**: implementing/modifying page objects, selectors, or app code (delegated); deriving the test cases (owned by `test-case-derivation`); the E2E execution mechanics (owned by `e2e-test-automation`); a **new methodology spec** — the two merged BDD specs already own the normative content, so this capability is tooling only (no third spec).

## Route

- **Decision**: direct
- **Rationale**: one coherent capability outcome, a single PR strand, no new/retargeted roadmap item — bounded per the spec's route rule. The two artifacts are the generator/reviewer pair of one capability, not two goal outcomes. No new methodology spec is created (operationalizes existing specs), so no pipeline hand-off is warranted.
- **Pipeline hand-off**: n/a

## Work packages

### P1 — Author the generator skill `bdd-scenario-generate`

- **Problem statement**: author `plugins/nolte-engineering/skills/bdd-scenario-generate/SKILL.md` (plus any bundled reference/templates) that: consumes a test-case document; applies the ordered workflow of `behavior-driven-development` (Feature grouping, one scenario per TC behavior, precondition/action/result → Given/When/Then, `@TC-<id>` tags, Background, Scenario Outline); emits **English** `.feature` files + **thin** step skeletons honoring the `bdd-page-object-integration` decoupling contract; runs the advisory lektor review (extract wording → temp Markdown → dispatch `lektorat-apply` audit → map findings back); emits a structured **work-package list** for page-model/dependency gaps without self-dispatching; and reports non-normalizable test cases.
- **Acceptance criteria**: SKILL.md passes `scripts/validate_skills.py`; name conforms to `spec/claude/skill-agent-naming/` (`<object-noun>-<action>`); body cites both BDD specs; the skill's documented behavior covers R2–R8, R10, R11 of the requirement artifact; `.feature` English rule and the delegation-not-dispatch boundary are explicit.
- **Touched files / artifacts**: `plugins/nolte-engineering/skills/bdd-scenario-generate/` (SKILL.md + optional references/)
- **Specialist**: `nolte-claude-dev:claude-plugin-developer`
- **Depends on**: none

### P2 — Author the read-only reviewer agent `bdd-scenario-reviewer`

- **Problem statement**: author `plugins/nolte-engineering/agents/bdd-scenario-reviewer.md`, a read-only (Read/Grep/Glob) agent that reviews existing BDD scenarios and their thin steps against both BDD specs (declarative one-behavior scenarios, `@TC-<id>` traceability, thin steps, page-object BDD-independence, assertions only in the `Then` binding, English `.feature`) and returns a severity-classified findings report, applying no edits.
- **Acceptance criteria**: agent file passes `scripts/validate_skills.py`; name conforms to `spec/claude/skill-agent-naming/` (`<subject>-<role-noun>`); `description` within the CI-guarded budget; tools are read-only; body cites both BDD specs and delimits against the generator skill (R9, R10).
- **Touched files / artifacts**: `plugins/nolte-engineering/agents/bdd-scenario-reviewer.md`
- **Specialist**: `nolte-claude-dev:claude-plugin-developer`
- **Depends on**: none

### P3 — Consistency, cross-references, and validation

- **Problem statement**: after P1+P2, reconcile the pair (shared naming, mutual delimitation, no description-budget regression), add reciprocal see-also/body pointers between the new artifacts and the two BDD specs where warranted, and confirm the catalog/marketplace picks them up.
- **Acceptance criteria**: `scripts/validate_skills.py` green across the repo; agent-`description` budget not regressed; the generator and reviewer mutually delimit; `task test` + prose/link gates green.
- **Touched files / artifacts**: the two new artifacts; possibly `spec/project/behavior-driven-development/` and `spec/project/bdd-page-object-integration/` (minor reciprocal pointer, EN+DE lockstep)
- **Specialist**: `nolte-shared:spec` (for any spec-file cross-ref edit) / generalist for the mechanical validation
- **Depends on**: P1, P2

## Dependency ordering

P1 and P2 are independent (parallelizable) → P3 (after both).

## Risks

- **Novel lektor extraction mechanism (R6)**: `lektorat-apply` is Markdown-only; the extract→audit→map-back design is new. Mitigation: keep it advisory (Q2) and document the temp-document shape in the SKILL body; a residual finding never hard-blocks.
- **Description-budget pressure**: adding one agent grows the `nolte-engineering` agent-`description` sum. Mitigation: P3 re-checks the CI-guarded budget; trim if near the cap.
- **No security-sensitive paths touched** (skills/agents/specs only), so no `code-security-reviewer` / `security-review` requirement before PR.

## Open questions

- none blocking. (The "own new spec?" risk is resolved in Scope: no new spec — operationalizes the two existing specs.)

## Dispatch log

- 2026-07-24 P1 dispatched to `nolte-claude-dev:claude-plugin-developer` — DRAFTED, validate_skills 0 findings (description 941 chars); awaiting verbatim re-emit to persist. NOTE: reviewer omitted from `see_also`/`dont_use_when` at draft time (P2 didn't exist yet, gen_catalog refuses unresolved refs) → P3 adds it now that P2 exists.
- 2026-07-24 P2 dispatched to `nolte-claude-dev:claude-plugin-developer` — DRAFTED + PERSISTED to `plugins/nolte-engineering/agents/bdd-scenario-reviewer.md` (read-only, description 725 chars).
- 2026-07-24 P1 PERSISTED to `plugins/nolte-engineering/skills/bdd-scenario-generate/SKILL.md` (description 941 chars; validate_skills 0 findings).
- 2026-07-24 P3 done: added `bdd-scenario-reviewer` to the skill's `see_also` + `dont_use_when` (now resolvable); reciprocal spec-name pointers deferred (specs already reference the consumer conceptually — avoids a Vale-gated spec touch this PR). Agent-`description` budget: aggregate ~20032 < ceiling 21315 (15% headroom) → no re-baseline needed. `scripts/validate_skills.py` green; pre-commit green (markdownlint URL fixed).
- verify: quality gate = validate_skills + pre-commit green; no security-sensitive path → no security-review. PR next.
