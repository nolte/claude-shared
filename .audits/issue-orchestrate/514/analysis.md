---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: 514
classification: "spec-change"
secondary-classes: ["docs"]
route: "direct"
status: approved
created: "2026-07-26"
---

# Issue Orchestration — Pre-analysis

<!-- Run-scoped artifact: committed on feat/e2e-failure-diagnosis-spec, removed with a
     fix-forward `git rm` before the PR merges. Durable facts go into the PR Risk / rollout
     notes and the issue comment first. -->

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #514 — spec(e2e): author an E2E failure-diagnosis and remediation spec — with per-topic research mandates
- **URL**: https://github.com/nolte/claude-shared/issues/514
- **Labels**: none
- **Linked items**: companion #503 (responsive/viewport hazards, merged), #517 (test-falsifiability, merged), #523 (coordinate-based clicking, merged). No open PR references this issue.
- **Prior art checked**: no `project/features/` entry, no `project/roadmap.md` item, no open PR. Grounded in `nolte/kamerplanter` #768 campaign (external evidence).

## Classification

- **Primary class**: spec-change
- **Secondary class(es)**: docs (consumer-agent wiring)
- **Rationale**: the work order is to author/extend specifications governing the E2E failure-diagnosis discipline; the primary spec-change character drives routing. Operator confirmed classification.

## Scope

- **In scope**:
  - A new spec `spec/project/e2e-failure-diagnosis/` (EN canonical + DE) covering the diagnostic discipline: §§1–5, 7, 9 of the issue body, §6 as a library-hazard-catalog *methodology* (how to build/maintain per-library catalogs, not one hard-coded catalog), plus comment findings **F** (xfail-outcome artefact blind spot → evidence channels) and **G** (search-before-fixing after proving a mechanism).
  - Extension of `spec/project/e2e-test-stability/` §F (stabilization loop) with issue §8 (cost model, batching, stop/escalate) and comment findings **A** (green-window-per-commit + record SHA), **B** (verify each package against the most sensitive profile), **C** (CI matrix as the verification loop; matrix-must-cover-declared-scope), **D** (marker removal verified on the removing commit); and §A/§B (isolation) with comment **E** (scope an audit to the resource + every path, not one helper name).
  - Cross-reference from `spec/project/test-cycle-result-analysis/` (Classification / Root-cause) into the new spec's §1/§9.
  - A dispatch-brief requirement from comment **H** (specialists explicitly authorised to refute the brief) placed where the portfolio governs dispatch briefs.
  - Discharge of every per-topic research mandate with recorded sources, or an explicitly tracked open question — none silently dropped (operator chose full multi-agent research).
  - Wiring `test-result-analyzer`, `e2e-test-reviewer`, `e2e-result-reviewer` (nolte-engineering) to the new spec, **body-only** (agent descriptions are near the routing-budget cap).
  - Explicit delimitation against #503 (§G responsive hazards), #523 (§C coordinate clicking), #517 (test-falsifiability), with no duplicated rules.
- **Out of scope**:
  - Re-deriving the responsive-hazard catalog (#503 §G owns it), the coordinate-clicking strategy matrix (#523 §C owns it), and the suite-shape / testability-hook contract (`e2e-test-automation`, `frontend/testability-identifiers`).
  - Any change to the kamerplanter suite itself (external repo; the campaign is the evidence source, not a deliverable).
  - An AST-linter / mutation-testing *implementation* (issue §4 research mandate). The spec defines the detection procedure; a follow-up tooling issue is the natural home for an implemented linter — recorded as a tracked open question, not built here.

## Route

- **Decision**: direct
- **Rationale**: one coherent outcome (author the E2E failure-diagnosis capability), a single PR strand, no new or retargeted roadmap item. This mirrors the sibling spec-authoring issues #503 / #517 / #523 / #524, each landed as one direct PR. Not a pipeline candidate: it does not span multiple goal outcomes.
- **Pipeline hand-off**: n/a

## Work packages

### P1 — Discharge the research mandates (multi-agent research dossier)

- **Problem statement**: every issue topic carries a research mandate (fault-tree / differential-diagnosis / `git bisect` formalisation for §1; per-framework diagnostic channels — Playwright trace/video/CDP/HAR, Cypress, Selenium Grid — for §2; rich-failure-context tooling for §3; AST-linting / mutation-testing / assertion-outcome-coverage for §4; dual/triple/quadruple-channel generalisation for §5; component-library-catalog maintenance method for §6; Playwright/Cypress actionability semantics for §7; real stabilization-campaign numbers for §8; ordered decision procedure for §9). The operator chose to discharge them in full.
- **Acceptance criteria**: a dossier records, per mandate, sourced findings (framework docs, library source, discipline references) **or** an explicit "carried as tracked open question" with a revisit condition; the per-framework equivalents demanded by §2 and §7 are named concretely; sources are citeable so the spec's References/Open Questions can carry them. No mandate silently dropped.
- **Touched files / artifacts**: `.audits/issue-orchestrate/514/research-dossier.md` (working artifact, removed with this analysis); citations flow into the spec bodies in P2/P3.
- **Specialist**: no matching specialised agent — orchestrator-run multi-agent research (Workflow), per the operator's explicit multi-agent opt-in. Read-only web/library research; results returned as structured data and persisted by the main session.
- **Depends on**: none

### P2 — Author the new spec `e2e-failure-diagnosis` (EN canonical + DE)

- **Problem statement**: author the diagnostic-discipline spec covering §§1–5, 7, 9 + §6 catalog methodology + comment F, G, with the delimitation section.
- **Acceptance criteria**: `spec/project/e2e-failure-diagnosis/{en,de}.md` exist and are index-registered; each topic §1–5, 7, 9 is specified **or** explicitly deferred with a reason; every rule is testable (an agent can tell whether it was followed); the §2 evidence-channel table exists and names the concrete artefact per major framework; the §4 vacuous-assertion / silent-empty-reader category has a stated detection procedure (mechanical or manual); a delimitation subsection references #503 §G, #523 §C, #517 with no restated rules; `task test` (frontmatter) and Vale on `en.md` pass.
- **Touched files / artifacts**: `spec/project/e2e-failure-diagnosis/en.md`, `.../de.md`, the spec index.
- **Specialist**: `nolte-shared:spec`
- **Depends on**: P1

### P3 — Extend `e2e-test-stability` §F + §A/§B (EN + DE)

- **Problem statement**: fold issue §8 into §F and place comment findings A, B, C, D (§F) and E (§A/§B) at their evidence-backed homes; the "CI matrix must cover declared scope" rule (C) may also touch `quality-gate`.
- **Acceptance criteria**: §F carries — a green window is valid only for the exact commit it ran on (record SHA); "no intervention between the two runs" covers every tree change including unrelated packages; run every profile on one commit before declaring the matrix stabilized; verify each shared-infra/layout package against the most sensitive profile before the next; use the CI matrix as the verification loop where one exists and treat a scope-vs-matrix gap as a finding; marker removal is verified by a green window on the removing commit. §A/§B carries the resource-enumeration audit-scoping rule. No rule duplicates the new spec (cross-reference instead). EN + DE in sync; `task test` + Vale green.
- **Touched files / artifacts**: `spec/project/e2e-test-stability/en.md`, `.../de.md`; possibly a one-line pointer in `spec/project/quality-gate/` (evaluate; only if it does not duplicate).
- **Specialist**: `nolte-shared:spec`
- **Depends on**: P1 (cost-model numbers from §8 mandate)

### P4 — Cross-reference `test-cycle-result-analysis` + place the dispatch-brief requirement (comment H)

- **Problem statement**: link the result-analysis Classification/Root-cause sections to the new spec's §1/§9 (classify-before-touching, prove-the-mechanism, search-before-fixing), and state the "specialist is authorised to refute the brief" requirement (comment H) where the portfolio governs dispatch briefs — H is explicitly *not* E2E-specific.
- **Acceptance criteria**: `test-cycle-result-analysis` references the new spec without duplicating its rules; the dispatch-brief-refutation requirement exists at a single authoritative home (the new spec's §5 dual-channel/dispatch section, cross-referenced from the dispatch-brief locus) and is testable; EN + DE in sync.
- **Touched files / artifacts**: `spec/project/test-cycle-result-analysis/{en,de}.md`; the dispatch-brief locus (resolved during authoring — new spec §5 as the anchor).
- **Specialist**: `nolte-shared:spec`
- **Depends on**: P2

### P5 — Wire the three consumer agents to the new spec (body-only)

- **Problem statement**: `test-result-analyzer`, `e2e-test-reviewer`, `e2e-result-reviewer` (nolte-engineering) must reference `e2e-failure-diagnosis` so the classifier and reviewers apply it.
- **Acceptance criteria**: each of the three agents' **body** references the new spec (descriptions unchanged — near the routing budget); `task test` (`validate_skills.py`) stays green (frontmatter budgets respected); the AC-7 requirement of the issue ("`test-result-analyzer`, `e2e-test-reviewer` and `e2e-result-reviewer` reference the new content") is met.
- **Touched files / artifacts**: `plugins/nolte-engineering/agents/{test-result-analyzer,e2e-test-reviewer,e2e-result-reviewer}.md`.
- **Specialist**: `nolte-claude-dev:claude-plugin-developer` (agent-artifact authoring; drafts-and-returns, main session writes to the worktree) — or a minimal orchestrator edit if the change is a single body pointer.
- **Depends on**: P2

### P6 — Verify and open the PR

- **Problem statement**: gate the change green, remove the pre-analysis artifact, open the PR.
- **Acceptance criteria**: `quality-gate` (or `task lint` + `task test` + Vale on touched `en.md`) passes; the delimitation-vs-#503/#523/#517 check confirms no duplicated rules; the pre-analysis artifact and research dossier are removed with a fix-forward `git rm`; the PR (via `pull-request-create`) links `Closes #514`, carries the five-section body and a **Risk / rollout notes** section with the issue reference, the classification verbatim, and the per-package specialist; the issue receives the summary comment.
- **Touched files / artifacts**: PR on `feat/e2e-failure-diagnosis-spec`.
- **Specialist**: `nolte-engineering:quality-gate` (verify) + `nolte-shared:pull-request-create` (PR).
- **Depends on**: P2, P3, P4, P5

## Dependency ordering

P1 → P2 → { P4, P5 } ; P1 → P3 ; then P2·P3·P4·P5 → P6.
(P3 depends only on P1 and runs in parallel with the P2→P4/P5 strand; P6 joins all.)

## Risks

- **Delimitation drift / duplicated rules** vs #503 §G, #523 §C, #517 — the highest-probability defect, since §4/§7/§8 overlap existing rules. Mitigation: an explicit delimitation subsection that *references* rather than restates; a dedicated verify check in P6 grepping for restated MUSTs.
- **Research mandate scope explosion** (9 + comment mandates, full depth). Mitigation: time-box each mandate; any mandate not decisively settled becomes a tracked open question with a revisit condition — which the AC explicitly permits.
- **Agent description budget** — adding spec references could push descriptions over the routing budget. Mitigation: body-only wiring; `validate_skills.py` is the token authority and gates P5.
- **Vale strictness** — CI pins Vale 3.15.2 (stricter than local shims); run the CI-pinned binary locally. No security-sensitive paths are touched, so no `code-security-reviewer` / `security-review` requirement applies.

## Open questions

- **Dispatch-brief requirement (comment H) home**: H is "not E2E-specific." Provisional placement is the new spec's §5 dispatch section as the single authoritative statement, cross-referenced from the E2E dispatch locus. If authoring reveals a better cross-cutting home (e.g. a `spec/claude/` dispatch-brief note), P4 records the decision. Not a blocker.
- **`quality-gate` touch for comment C** ("matrix must cover declared scope"): include only if it does not duplicate the §F statement. Decided during P3.

## Dispatch log

<!-- Appended during operation 5. -->
