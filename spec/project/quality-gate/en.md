# Quality Gate

Status: draft

## Context
Every repository in the portfolio runs lint, type-check, and test commands in some form, but the when, the what, and the shape of the output diverge across projects. Some repositories wire it all into a single `task check` target; others expect contributors to remember four separate commands; still others run parts of the gate only in CI and never locally. The cost is twofold: contributors can't tell whether the repo is shippable from their terminal, and CI becomes the first place failures surface—slowing feedback and burning review cycles on issues a local gate would have caught. This spec defines the contract the gate has to meet so the same invocation works anywhere in the portfolio, the output shape is parseable, and Taskfile conventions plus tool-specific ignore lists remain in charge of the details.

## Goals
- A contributor in any portfolio repository can run one recognisable gate (a Taskfile target) before a commit, a PR, or a release and get a parseable pass/fail result
- The gate's composition (lint + type-check + tests) is the same across repositories; only the tools change per language
- Taskfile targets remain the authoritative local entry point—repository conventions and ignore lists aren't second-guessed by a higher-level runner
- The output of the gate is deterministic enough that diffs of the rendered result stay stable across runs, so CI logs and PR comments are comparable
- The gate is clearly distinct from continuous CI (`workflow-health`) and from security scanning (`dependency-audit`); each concern owns its own surface

## Non-Goals
- Picking the specific linting / typechecking / testing tool for a given language (ruff vs flake8, mypy vs pyright, vitest vs jest): that's a per-repository decision
- Defining the content of any given test suite or lint rule set—those live in the repositories' own configs
- Replacing CI: the gate is a local-or-invocable pre-check that mirrors what CI will also run; CI remains the source of truth for merge protection
- Declaring operational details of the skill that implements the gate (`skills/quality-gate/`)—those can evolve without a spec change

## Requirements

### Composition
- **MUST** include three categories when the repository has relevant code for each: lint, type-check, tests; categories without relevant code (for example type-check in a pure shell repo) aren't required
- **MUST** run every category the repository does have; partial gates that silently drop a category **MUST NOT** report `pass`
- **SHOULD** compose the gate from existing Taskfile targets (`task lint`, `task test`, `task typecheck`, or a single `task check` that wraps all three); adding a new top-level target that duplicates the work is redundant
- **MAY** extend the gate with additional categories when the repository's nature warrants it (schema validation for a data project, Helm lint for an infra project); additions **MUST** be declared explicitly in the Taskfile and visible in the gate's output

### Invocation contract
- **MUST** run the gate identically from a local workstation and from CI—no environment branching that makes one stricter than the other
- **MUST** honour Taskfile targets when they exist; direct tool invocation is a fallback for repositories without a Taskfile, not a bypass of project-specific ignore lists
- **MUST NOT** apply repository-local ignore rules (lint exclusions, coverage thresholds) that aren't declared in the repository's own configs; the gate runs the tools as the repository has configured them
- **SHOULD** run the three categories in parallel when the ecosystem permits it; sequential fallback is acceptable when a category produces inputs another category consumes (rare in practice)

### Output shape
- **MUST** produce a single table with columns `Check`, `Status`, `Runner`, `Details` (one row per category) so consumers can parse the result mechanically
- **MUST** use one of the statuses `pass`, `fail`, `skipped`, `timeout` per row; no other values
- **MUST NOT** report `pass` for a category that was `skipped` because its tooling wasn't detected; `skipped` stays distinct in the output
- **MUST** record in the `Runner` column the exact command that was invoked (`task lint`, `ruff check .`, `pnpm lint`) so the run is reproducible
- **SHOULD** append, below the table, a bounded excerpt (≤10 lines) of the first failure per `fail` / `timeout` row so a reviewer can triage without re-running
- **MUST** include an overall verdict line: green summary when every row is `pass`, red summary naming the failing rows otherwise, and an explicit note when any row is `skipped`

### Timeouts and failure handling
- **MUST** apply a bounded timeout per category: lint ≤ 2 minutes, type-check ≤ 5 minutes, tests ≤ 10 minutes; a longer timeout is acceptable only when the repository's own Taskfile target documents the longer runtime
- **MUST** report a timeout as `timeout`, not as `fail`; the distinction matters because a timeout is a triage signal (tests hang vs tests fail)
- **MUST NOT** retry a timed-out category automatically; retry is a human decision once the root cause is known
- **SHOULD** surface the exit code of the underlying tool in the `Details` column so consumers can tell the difference between "lint found 3 errors" (exit 1) and "lint crashed" (exit > 1)

### Triggers
- **MUST** be runnable at three distinct points, even if the invocation looks the same: (a) a contributor's local pre-commit / pre-PR step, (b) CI on every push to a PR branch, (c) release gating before a tag
- **SHOULD** be invocable from a pre-commit hook when the repository uses pre-commit; repositories that don't use pre-commit rely on the contributor's explicit invocation
- **MUST NOT** gate the gate itself behind a CI-only runner (for example a self-hosted GPU runner needed for the tests); if a suite truly can't run locally, split it out of the gate and document the split in the repository's README

### Delimitation
- **MUST** stay separate from `spec/project/workflow-health/`: workflow-health covers the continuous CI state over time (flake triage, trend), the gate is the per-invocation pass/fail
- **MUST** stay separate from `spec/project/dependency-audit/`: vulnerability scanning has its own cadence and severity scale; the gate doesn't assume responsibility for it
- **MUST** be independent of `spec/project/release-automation/` in the sense that a green gate is a precondition for a release cut, not a replacement for the release workflow

### Monorepo and subroot behaviour
- **MUST** scope each category to the subroots that actually own the relevant manifest (for example run `ruff` in `backend/` only, `eslint` in `frontend/` only) when the repository is a monorepo; a monolithic invocation that walks the whole tree would pick up unrelated code
- **SHOULD** expose per-subroot Taskfile targets (`task lint:backend`, `task test:frontend`) alongside the aggregate targets so contributors can scope fast
- **MUST** aggregate subroot results under the corresponding category row in the output table rather than exploding the table into a row per subroot; the per-subroot detail goes into the `Details` column

## Acceptance Criteria
- [ ] Every repository with lint / type-check / test code has a Taskfile target (`task check`, or a combination of `task lint`, `task test`, `task typecheck`) that runs the full gate
- [ ] The documented invocation for the gate is identical between the repository's README and its CI workflow
- [ ] The gate's output table uses the `Check` / `Status` / `Runner` / `Details` column contract across every invocation path
- [ ] No repository reports the gate as `pass` while silently skipping a category the repository has relevant code for
- [ ] The gate's overall timeout budget per category doesn't exceed the limits in §Timeouts, or the Taskfile target explicitly documents a longer runtime
- [ ] Monorepos scope each category to the owning subroot (not the repo root) and expose at least one aggregate Taskfile target covering every subroot
- [ ] The repository's README names the gate target and the expected output shape, so new contributors can reproduce it on their first day
- [ ] The skill `skills/quality-gate/` invokes the repository's Taskfile targets first and falls back to native tooling detection only when no matching target exists

## Open Questions
- Should the spec mandate a single top-level target name (`task check`) across the portfolio, or is the per-repository choice between `task check`, `task gate`, and equivalent acceptable?
- Does the gate need a documented `--fast` mode (lint + type-check, skip tests) for use inside pre-commit hooks where the full test suite would be prohibitive, or does pre-commit scope stay the repository's decision?
- Should coverage thresholds live inside the gate (a failing threshold is a `fail` row) or outside it (threshold checks are a separate step in CI), given that local test runs rarely compute coverage?
- When a monorepo has divergent language stacks per subroot, should the gate's output show one row per category-and-subroot for readability, or does the current "one row per category with subroot detail in `Details`" stay?
