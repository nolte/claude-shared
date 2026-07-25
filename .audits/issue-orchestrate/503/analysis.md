---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "503"
classification: "spec-change"
secondary-classes: []
route: "direct"
status: approved
created: "2026-07-25"
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #503 — spec(e2e-test-stability): add responsive/viewport hazard section and mobile testability-hook contract
- **URL**: <https://github.com/nolte/claude-shared/issues/503>
- **Labels**: none
- **Linked items**: none (source evidence: nolte/kamerplanter#768, branch `fix/e2e-full-run-stabilization`)
- **Prior art checked**: no open PRs reference #503; no `project/features/` or roadmap item covers viewport hazards; `spec/project/e2e-test-stability/` contains only §A–F (the word "responsive/viewport" is absent from the EN normative text); `spec/project/e2e-test-automation/` §Locator strategy has no role-scoping rule; `spec/frontend/testability-identifiers/` has no layout-parity or interactive-child placement rule.

## Requirements gate

- No requirement artefact under `project/requirements/` covers this issue.
- **Operator override recorded (2026-07-25)**: Issue #503 itself serves as the requirements source — it carries fully drafted MUST-rules, a six-row evidence table (141→72→8→5 failures across four runs), blast-radius data, and an explicit scope rationale. `requirements-elicit` skipped per `spec/project/issue-orchestration/` §Issue acquisition override path.

## Classification

- **Primary class**: `spec-change`
- **Secondary class(es)**: none
- **Rationale**: The issue requests exclusively normative additions to existing specs (new §G + §F evidence-list addition + product-side testability contract); no code, agent, or skill changes are in scope. Operator confirmed 2026-07-25.

## Scope

- **In scope**:
  - New **§G "Responsive and viewport-dependent hazards"** in `spec/project/e2e-test-stability/` (EN canonical + DE), covering: unscoped structural/ARIA-role locators, layout-switch readers that must assert their layout and fail loudly, key-based (never position-based) access, fallback-click soundness, open-verification for menu/select helpers, viewport-conditional affordances, harness animation-disable, single-stack-per-grid, valid-baseline coverage rule.
  - **§F addition**: request-count diffing joins screenshots/logs/protocol in the run-evidence list.
  - Consumer-side locator tightening in `spec/project/e2e-test-automation/` §Locator strategy (EN+DE): role/structural selectors never unscoped.
  - Product-side testability contract (identifier on the interaction-receiving element, layout-parity of key-based hooks, per-layout list discriminability) — placement per open question OQ-1 below.
  - Updated Goals/Acceptance Criteria/References in the touched specs; kamerplanter mobile runs (`20260725_010046`, `030325`, `055859`, `073849`) recorded as source experience.
- **Out of scope**: updating the consuming agents (`e2e-test-generator`, `e2e-test-reviewer`, page-object related agents) to enforce §G — follow-up work, operator-confirmed; any kamerplanter-side code or page-object fixes (live in nolte/kamerplanter).

## Route

- **Decision**: direct
- **Rationale**: one coherent outcome (viewport-hazard rules become normative), a single PR strand, no new or retargeted roadmap item. Operator confirmed 2026-07-25.
- **Pipeline hand-off**: n/a

## Work packages

### P1 — §G + §F extension in e2e-test-stability

- **Problem statement**: §A–F are viewport-agnostic; six evidenced mobile-run root causes (dialog-role collision with hidden drawer, table→card reader returning `[]`, wrapper-testid click offset, mousedown-less JS click fallback, popover repositioning race, collapsed affordances) recur for any team following the spec to the letter, and most fail silently.
- **Acceptance criteria**: `spec/project/e2e-test-stability/en.md` and `de.md` contain a §G with normative MUST rules for (locators) no unscoped structural/ARIA-role selectors; (readers) layout-asserting, loudly-failing, key-based access; (interaction) sound-or-loud fallbacks, verified open-steps, contract-managed viewport affordances; (harness) suite-wide animation disable, one app stack per browser grid; (coverage) a matrix profile counts as covered only after one valid baseline run. §F's evidence list names request-count diffing. Acceptance Criteria and References updated; EN/DE in sync; Vale ≥3.14 and markdownlint green.
- **Touched files / artifacts**: `spec/project/e2e-test-stability/en.md`, `spec/project/e2e-test-stability/de.md`
- **Specialist**: skill: `nolte-shared:spec` (runtime lookup: only candidate whose description names spec authoring/translation/drift)
- **Depends on**: none

### P2 — Locator-strategy tightening in e2e-test-automation

- **Problem statement**: §Locator strategy ranks role selectors mid-hierarchy but never forbids using them unscoped; hazard #1 (112 tests against a hidden drawer with `role="dialog"`) is a direct consequence.
- **Acceptance criteria**: `spec/project/e2e-test-automation/en.md` + `de.md` §Locator strategy adds a MUST NOT for unscoped structural/ARIA-role locators (scope to the owning container or address a test hook), with a cross-reference to e2e-test-stability §G; EN/DE in sync; lint green.
- **Touched files / artifacts**: `spec/project/e2e-test-automation/en.md`, `spec/project/e2e-test-automation/de.md`
- **Specialist**: skill: `nolte-shared:spec`
- **Depends on**: P1 (cross-reference target §G must exist)

### P3 — Product-side testability contract (placement per OQ-1)

- **Problem statement**: §G's rules are only satisfiable when the product emits the right hooks: the identifier must sit on the interaction-receiving element (not a wrapper whose geometry is breakpoint-dependent), components with per-breakpoint DOM shapes must emit the same key-based hooks in every layout, and every list/section must be discriminable in every layout.
- **Acceptance criteria**: the provider-side rules exist exactly once, in the spec chosen under OQ-1, phrased library-agnostically; both e2e specs reference (never restate) them; EN/DE in sync; lint green.
- **Touched files / artifacts**: per OQ-1 — either `spec/frontend/testability-identifiers/{en,de}.md` (ownership-correct) or a new section in `spec/project/e2e-test-automation/{en,de}.md` (issue verbatim)
- **Specialist**: skill: `nolte-shared:spec`
- **Depends on**: P1

## Dependency ordering

P1 → P2 ; P1 → P3 (P2 and P3 mutually independent; single specialist dispatch walks P1, P2, P3 sequentially in one worktree).

## Risks

- **Cross-spec contradiction / ownership drift**: e2e-test-stability §Non-Goals explicitly assigns provider-side testability hooks to `spec/frontend/testability-identifiers/`; placing the product-side contract verbatim into e2e-test-automation would contradict that boundary. Mitigation: OQ-1 settles placement before dispatch; references instead of restatement.
- **EN/DE divergence**: three spec topics × two languages. Mitigation: `spec` skill's translation-sync discipline; per-file diff review before commit.
- **Prose-lint regressions**: Vale (Microsoft style) on `spec/**/en.md`. Mitigation: direct Vale 3.14.1 run per file before commit (asdf shim is 3.0.1 and too old; task lint:prose needs TTY).
- **Security**: no security-sensitive paths touched → no `code-security-reviewer`/`security-review` pass required.

## Open questions

- **OQ-1 (blocks P3)**: Where does the product-side testability contract live? (a) `spec/frontend/testability-identifiers/` — ownership-correct per e2e-test-stability §Non-Goals, referenced from §G and e2e-test-automation; (b) new section in `spec/project/e2e-test-automation/` — the issue's literal wording. Recommendation: (a).
  **RESOLVED (operator, 2026-07-25): (a)** — the provider-side rules land in `spec/frontend/testability-identifiers/`; both E2E specs reference them. Deliberate deviation from the issue's literal wording, to be noted in the PR and the issue comment.

## Dispatch log

- 2026-07-25 P1 dispatched to skill:nolte-shared:spec — §G (9 MUST rules) + §F request-count evidence + Context/Goals/AC/References landed in e2e-test-stability {en,de}.md; EN/DE structure-synced (15/15 headings, 65/65 bullets, 10/10 checkboxes)
- 2026-07-25 P2 dispatched to skill:nolte-shared:spec — unscoped-role-locator MUST NOT + [R9] cross-ref landed in e2e-test-automation {en,de}.md §Locator strategy
- 2026-07-25 P3 dispatched to skill:nolte-shared:spec — interaction-receiving-element placement rule + new §Responsive layout parity + AC + [R6] landed in testability-identifiers {en,de}.md (OQ-1 option a)
- 2026-07-25 verify — Vale 3.14.1 direct: 0 errors on all three en.md; pre-commit green (vale-prose wrapper fails on known task-TTY issue only); validate_skills.py OK; 9 technical terms added to .github/styles/config/vocabularies/claude-shared/accept.txt (upstream candidates for nolte/vale-style per vocab-drift-audit)
