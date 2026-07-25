---
name: source-code-review
description: Runs a holistic senior-engineer source-code review of production and test code against spec/project/source-code-review/ plus its frontend extension spec/frontend/source-code-review/, and persists a severity-classified report whose disjoint work packages are parallel-dispatchable to specialists. The default `review` operation detects each language and surface and dispatches the matching read-only reviewer agent (`python-code-reviewer`, `frontend-code-reviewer`; anything unprofiled is reported unsupported), then persists the report under .audits/source-code-review/. The `plan` operation hands that report to implementation-plan-author. Invoke to review a codebase like an experienced developer, find domain-knowledge duplication, or find business logic leaking into the client; also German. Don't use for the deep OWASP audit (code-security-reviewer), UX judgment (frontend-usability-optimizer), single-tier test conformance (tier reviewers), or to run lint and tests (quality-gate). Supports resume.
tags: [review, audit]
phase: quality
summary: "Holistic senior-engineer review of production and test code: detects each language and surface, dispatches the matching reviewer, persists the classified report, routes its parallel work packages."
summary_de: "Ganzheitliches Senior-Engineer-Review von Produktiv- und Testcode: erkennt Sprache und Oberfläche, dispatcht den passenden Reviewer, persistiert den Report und routet dessen parallele Work-Packages."
use_when:
  - "you want a senior-engineer review of production and test code beyond lint and types"
  - "you want domain-knowledge duplication found and consolidated"
  - "you want frontend components reviewed for business logic, missing error paths, or design-system bypasses"
  - "you want a persisted review report whose work packages specialists remediate in parallel"
dont_use_when:
  - situation: "you want a diff-scoped review of an open pull request (the review leg of the PR flow)"
    alternative: pull-request-merge
  - situation: "You want a deep whole-codebase OWASP security audit"
    alternative: code-security-reviewer
  - situation: "you want a usability, visual-design, or content-quality judgment on a rendered UI"
    alternative: frontend-usability-optimizer
  - situation: "You want a CVE / dependency vulnerability scan"
    alternative: dependency-audit
  - situation: "You want one test tier checked against its tier checklist"
    alternative: unit-test-reviewer
  - situation: "You want the mechanical lint / typecheck / test gate run"
    alternative: quality-gate
see_also:
  - python-code-reviewer
  - frontend-code-reviewer
  - maturity-assess
  - implementation-plan-author
  - code-security-reviewer
  - fullstack-developer
resumable: true
---

# Source Code Review

Run a holistic senior-engineer source-code review over production **and** test code, persist one severity-classified report, and hand its work packages to specialists for parallel remediation. The default `review` operation detects and dispatches; the `plan` operation turns the persisted report into a specialist-mapped implementation plan. **There is no apply** — remediation is real code work owned by specialists, never an in-place rewrite from this skill.

Implements `spec/project/source-code-review/` — the spec defines the language-agnostic core dimensions (D1–D10), the language profiles, the tooling-first rule, and the report contract with disjoint work packages — plus its **frontend surface extension** `spec/frontend/source-code-review/`, which overlays the frontend dimensions (F1–F11), the component-slice review unit, the framework profiles, the implementation-proposal requirement, and the delimitation from the UX review. This skill binds those rules to the on-disk procedure and owns detection, persistence, and the plan handover; the review judgment itself lives in the dispatched reviewer agent.

## German trigger phrases

This skill also triggers on equivalent German-language requests, including:

- "Code-Review durchführen" / "Source-Code-Review wie ein erfahrener Entwickler"
- "fachliche Duplizierung finden" / "doppelte Geschäftslogik aufspüren"
- "Testcode-Qualität reviewen" / "Produktiv- und Testcode prüfen"
- "Frontend-Components reviewen" / "Geschäftslogik im Frontend finden"

## User-language policy

Detect the user's language from their message and respond in it. The review artifact uses English section headings so downstream tooling and the plan author parse it reliably; prose around the report is localised.

## Inputs

- **Repo root**: default is the current working directory.
- **Target**: default is the whole source tree (production plus test roots); an explicit narrower target (package, module set, directory) is accepted and recorded in the report.
- **Operation**: `review` (default) or `plan` (dispatches the plan author against an existing report). Never author a plan without a persisted report to ground it.

## Operations

### `review` (default)

1. **Detect the language(s) and the surface(s).** From build metadata (`pyproject.toml`, `package.json`, `go.mod`, …), determine the in-scope languages, then check whether any of them renders a **browser surface** — a frontend framework dependency plus a bundler or framework config, a component tree, a router, a style pipeline. Route each detected unit to its reviewer:

   | Detected | Reviewer | Governing specs |
   |---|---|---|
   | Python | `python-code-reviewer` | core + Python profile |
   | Browser-rendered code on a profiled framework (React / TypeScript today) | `frontend-code-reviewer` | core + `spec/frontend/source-code-review/` overlay |
   | Anything else | — | recorded **unsupported** in the report header |

   A language or framework without a profile is recorded as unsupported — never reviewed ad hoc. A polyglot or full-stack repository gets one dispatch per supported unit, never a blended review: a Python API plus a React client is two dispatches, and their findings land in one report under separate scope headers.

2. **Dispatch the read-only reviewer.** Pass the resolved target scope. The reviewer discovers roots and the tooling baseline, applies the core dimensions with its profile under the tooling-first rule, reviews production and test code with equal rigour, and returns the severity-classified findings inventory with work packages. The frontend reviewer additionally reports the four baselines it judged against (framework profile, design-token or theme source, i18n layer, data-access layer) and reviews the **component slice** — component, hooks, styles, tests, translation keys — as one unit. Wait for its report before persisting.

3. **Verify the report contract.** Confirm the severity vocabulary (Critical / Warning / Suggestion / Info from `spec/claude/review-plan/` §Severity scale), the per-finding file:line + dimension ID + `production|test` marker + confirmed/suspected flag, and that the work packages have **disjoint file sets** with routing targets and explicit dependencies. For a frontend dispatch also confirm: exactly one dimension ID per finding (no D and F on the same finding), an implementation proposal on every Critical and Warning finding, the four recorded baselines, and that no finding above Info rests on a rendered impression. A contract violation goes back to the reviewer for one repair pass, not into the artifact.

4. **Persist the artifact.** Write the report to `.audits/source-code-review/<target-slug>.md` (`<target-slug>` is the repo name for whole-tree runs, else the target path slug). A re-run overwrites the canonical file. Record the commit under review, the applied language and framework profile(s), and any unsupported language or framework.

5. **Surface the triage summary.** Show the operator the per-dimension counts, the Critical findings, and the work-package table, and offer the `plan` operation.

### `plan` (turns the report into a specialist-ready implementation plan)

- **Dispatch `implementation-plan-author`** with the persisted review artifact as its grounded input (its source-code-review findings-report input mode). The agent decomposes the Critical and Warning work packages into atomic, testable work packages mapped to specialists.
- **Respect the report's routing:** production-code remediation belongs to `fullstack-developer`; tier-conformance findings to the owning tier reviewer (`unit-test-reviewer`, `integration-test-reviewer`, …); D10 and F9 route-out floors to the owning audit (`code-security-reviewer`, `dependency-audit`, `observability-audit`) — a floor is dispatched as that audit, never planned as a code fix here. From a frontend report additionally: accessibility-conformance questions to `webview-ui-expert`, translation coverage to `i18n-completeness-checker`, and the Info-level UX entries to `frontend-usability-optimizer` — the last as a separate operator decision, never as a work package.
- **Preserve parallelism:** the report's disjoint file sets and declared dependencies carry into the plan unchanged, so undeclared-dependency packages stay concurrently dispatchable (for example one worktree-isolated specialist per package). A frontend report's packages are cut along component slices; keep that cut, because a slice's component, styles, and tests must move together.
- **Carry the implementation proposals through:** a frontend finding already names its target layer, change shape, acceptance signal, and risk. The plan author refines them into work packages; it doesn't re-derive them.
- The plan author writes its own artifact and returns the work-package table; this skill does **not** dispatch the specialists or open a PR (the operator or `issue-orchestrate` owns that gate).

## Gotchas

- **Tooling-first is load-bearing.** A report that restates `ruff`/`mypy` output is noise and a contract violation; a missing baseline is exactly one adoption finding. Route "run the gate" requests to `quality-gate`.
- **Test code is a subject, not an annex.** A review that only covered production code is incomplete — send it back for the test pass rather than persisting it.
- **D4 means semantic duplication.** Two textually similar blocks with independent domain meaning aren't a finding; two different-looking implementations of one business rule are. The reviewer names all sites and one single-source-of-truth proposal.
- **Disjoint work packages are the parallelism guarantee.** If two packages touch one file, remediation serialises or conflicts; verify disjointness before persisting.
- **Floors route, never deepen.** An obvious security or observability smell becomes a route-out entry to the owning audit; duplicating that audit's depth here breaks the delimitation.
- **Unsupported language or framework ≠ silent skip.** A detected language or framework without a profile appears in the report header as unsupported, so the operator knows the coverage boundary.
- **A full-stack repository is two dispatches, not one.** `package.json` next to `pyproject.toml` means a Python dispatch *and* a frontend dispatch. Blending them loses the profile the tooling-first rule and the dimension catalog depend on.
- **The frontend review judges code, never taste.** UX, visual-design, and copy-quality observations are Info entries routed to `frontend-usability-optimizer` and never enter the work packages. A report where a usability opinion carries Warning or Critical is a contract violation — send it back.
- **`package.json` alone isn't a browser surface.** A Node CLI or a build script ships one too. Require a frontend framework dependency plus a component tree or router before dispatching `frontend-code-reviewer`; otherwise record the language as unsupported.

## Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/source-code-review/<run-id>.yml` after each named phase boundary (detection, reviewer-dispatch, contract-verify, artifact-persist, plan-handover); with more than one detected unit the dispatch checkpoint records which units are already reviewed, so a resumed run doesn't re-dispatch a completed reviewer. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope and fail-closed semantics live in the spec; don't duplicate them here.

## Hard rules

- **Never** modify the reviewed code in any operation; there is no apply. Remediation belongs to the specialists the work packages route to.
- **Never** persist a report that violates the contract (severity vocabulary, per-finding attribution, disjoint work packages); one repair pass with the reviewer, then escalate to the operator.
- **Never** review a language or framework without a profile ad hoc; record it as unsupported.
- **Never** persist a frontend finding above Info that rests on a rendered impression (wording, aesthetics, discoverability, perceived speed); the code-side twin or nothing.
- **Never** deepen a D10 or F9 floor finding; dispatch the owning audit instead.
- **Always** review production and test code with equal rigour, and keep the `production|test` marker on every finding.
- **Always** ground the `plan` operation in the persisted artifact, and leave specialist dispatch and the PR to the operator or `issue-orchestrate`.
- When `spec/project/source-code-review/` or its frontend extension `spec/frontend/source-code-review/` and this skill disagree, the spec wins; this skill needs the update.

## Why this is a skill, not an agent

This skill follows the hybrid pattern: the read-heavy review judgment is delegated to the reviewer agents (context-window isolation, read-only tool restriction), while language and surface detection, contract verification, persistence, and the plan handover stay in the skill.

- **Orchestration role**: callers run this as one step in a larger flow (post-feature review, pre-release pass); the triage summary flows back into the main conversation for the operator's decision.
- **Mid-flow interactivity**: choosing the target scope, accepting the triage, and opting into `plan` are operator-gated decisions favouring the skill side.
- **Persistent artifact**: the deliverable is an on-disk report under `.audits/source-code-review/`; skills own persistent state.
- **Counter-dimension**: the review itself is self-contained and verbose — exactly the context pressure that favours an agent. That pull is honoured for the review half, delegated to `python-code-reviewer` and `frontend-code-reviewer`; interactivity and persistence keep the orchestrating surface a skill.
