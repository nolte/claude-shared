# Pull Request Workflow

Status: draft

## Context
Pull requests (PRs, equivalent to GitLab merge requests / MRs) are the sole path for changes into the `develop` integration branch defined in the branching-model spec. Two recurring problems motivate this spec: (1) PR descriptions vary in shape, which makes review harder and degrades the release-drafter output that summarizes `develop` activity, and (2) PRs occasionally reach `develop` before CI has reported green, undermining the "always-green develop" assumption that the release flow relies on. This spec defines how PRs are authored and which gates they must pass before merging into `develop`. It complements — and does not restate — the branching-model spec, which declares the target branch and the automerge workflow, and the project-structure spec, which declares the `.github/settings.yml` mechanics.

## Goals
- Every PR into `develop` follows a single, consistent description structure so reviewers, release-drafter, and AI agents see the same shape
- No PR reaches `develop` unless every required CI check has reported success
- Preconditions (branch naming, target branch, title form) are fully declared in code and enforceable via branch protection
- Humans and AI agents authoring PRs against these repositories produce artifacts that match the same standard without per-repo onboarding

## Non-Goals
- Target-branch policy and release flow (covered by the branching-model spec)
- Branch-protection declaration mechanics via `.github/settings.yml` (covered by the project-structure spec; this spec only states which rules must be declared)
- Automerge workflow internals (covered by `nolte/gh-plumbing` reusable-automerge and referenced from the branching-model spec)
- Release-notes / changelog content (handled by release-drafter)
- Code-review approval policy (who reviews, how many approvals) — not in scope here

## Requirements

### PR preconditions
- **MUST** target `develop` as the base branch
- **MUST** originate from a branch whose name starts with one of the prefixes `feat/`, `fix/`, `chore/`, `docs/`, or `exp/` (as declared by the branching-model spec)
- **MUST** use a PR title in Conventional Commits form `<type>(<scope>)?: <summary>`, where `<type>` is literally identical to the branch prefix (prefix `feat/` → type `feat`, `fix/` → `fix`, `chore/` → `chore`, `docs/` → `docs`, `exp/` → `exp`); no translation or aliasing is permitted
- **MUST** keep a single PR scoped to one logical change; unrelated changes are split into separate PRs — the sole exception is an `exp/` PR, which **MAY** bundle loosely related exploratory changes that share an iteration timeframe, because that is the whole purpose of the experimental branch type declared in the branching-model spec
- **SHOULD** link at least one related issue via `Closes #<n>` or `Refs #<n>` in the description when a tracking issue exists

### Branch freshness
- **MUST** ensure the feature branch contains every commit of the current `develop` tip before the PR is opened, so the CI run reflects the state that will exist on `develop` after merge; this is achieved by either merging `develop` into the feature branch or rebasing the feature branch onto `develop`
- **MUST** re-synchronize the feature branch with `develop` whenever `develop` advances while the PR is open, before the PR is moved out of Draft or before automerge is allowed to act; a PR whose branch lags behind `develop` is not considered ready for merge
- **MUST** enable the GitHub "require branches to be up to date before merging" option for `develop` in `.github/settings.yml` (in `protection.required_status_checks.strict: true`, directly or via the `nolte/gh-plumbing` commons extension), so the platform enforces this precondition in addition to the client-side workflow
- **MAY** choose rebase or merge to perform the sync; the spec does not prescribe which, but the chosen operation **MUST** leave `develop` fully contained in the feature branch before the PR is opened or re-requested for review

### PR description structure
A pull-request template **MUST** exist at `.github/pull_request_template.md` and **MUST** contain the following sections, in this exact order and with these exact headings:

1. **Summary** — one to three sentences stating *what* the PR changes and *why*
2. **Changes** — bulleted list of user-visible or reviewer-relevant changes
3. **Linked issues** — `Closes #…` / `Refs #…` entries, or the literal text `None`
4. **Testing** — how the change was verified (commands run, manual steps, screenshots)
5. **Risk / rollout notes** — risk class, migrations, feature flags, or the literal text `None`

- **MUST** retain every required template section in the PR body; sections are never deleted, even when empty
- **MUST NOT** leave Summary, Changes, or Testing empty; Linked issues and Risk / rollout notes **MAY** use the literal text `None`
- **MAY** add repository-specific sections *below* the five required sections; additional sections **MUST** appear after all five required sections and **MUST NOT** be interleaved between them
- **SHOULD** use imperative mood in Summary and Changes (`Add …`, `Fix …`, not `Added …`)
- **SHOULD** link to the relevant spec file under `spec/` when the change implements or modifies a spec

### PR lint workflow
- **MUST** include a workflow under `.github/workflows/` (e.g. `pr-lint.yml`) that lints PR title and body on the `pull_request` events `opened`, `edited`, `synchronize`, and `ready_for_review`
- **MUST** register this workflow's job as a required status check for `develop` in `.github/settings.yml`
- **MUST** fail the check if the PR title does not match the Conventional Commits form `<type>(<scope>)?: <summary>` with `<type>` ∈ {`feat`, `fix`, `chore`, `docs`, `exp`}
- **MUST** fail the check if the PR body does not contain all five required section headings in the declared order
- **MUST** fail the check if Summary, Changes, or Testing is empty or contains only the literal text `None`
- **MUST NOT** fail the check when the body contains additional repository-specific sections appended after the five required sections, so long as the required sections themselves are present, in order, and non-empty where required
- **SHOULD** implement the linter as a reusable workflow under `nolte/gh-plumbing` (for example `reusable-pr-lint.yaml`) so every repository inherits one implementation rather than forking local copies that drift

### CI gate into `develop`
- **MUST** declare the full set of required status checks for `develop` as code in `.github/settings.yml` (directly or via the `nolte/gh-plumbing` commons extension); the GitHub UI is **NOT** an acceptable place to add or remove required checks
- **MUST** require every declared check to report success before a PR can merge into `develop`
- **MUST** configure the `automerge.yaml` workflow so it only merges a PR when every required check reports success and the PR is approved
- **MUST** set `enforce_admins: true` for `develop` branch protection so that admin overrides cannot bypass a failing required check; the CI gate has no exception path, and a waiver is not permitted — if a required check is persistently broken, the correct remedy is a PR against `.github/settings.yml` (which itself passes the gate) to remove or replace the check, not a one-off bypass
- **SHOULD** block merge while any review explicitly requests changes, even after CI becomes green

### Merge strategy
- **MUST** merge PRs into `develop` using squash-merge; the resulting commit on `develop` is a single commit per PR carrying the Conventional-Commits-compliant PR title as its message
- **MUST** declare squash-merge as the only enabled merge option in `.github/settings.yml` for repositories following this spec: `allow_squash_merge: true`, `allow_merge_commit: false`, `allow_rebase_merge: false`
- **SHOULD** keep the PR title as the default squash-commit message so the `develop` history is a linear stream of Conventional-Commits messages, directly consumable by release-drafter

### Draft and work-in-progress PRs
- **SHOULD** open PRs as Draft while work is ongoing and mark them ready for review only once CI is expected to pass and the description is complete
- **MUST NOT** mark a PR ready for review when any required section of the description is missing or empty in violation of the rules above

## Acceptance Criteria
- [ ] `.github/pull_request_template.md` exists and its section headings match the five headings listed in "PR description structure", in order
- [ ] `.github/settings.yml` declares required status checks for `develop` (directly or via the `nolte/gh-plumbing` commons extension)
- [ ] `enforce_admins` is `true` for the `develop` branch protection rule; no waiver mechanism exists in the repository
- [ ] For the last 10 PRs merged into `develop`, every required status check was green at merge time (spot-check via `gh pr list --state merged --base develop --limit 10 --json number,title,mergedAt,statusCheckRollup`)
- [ ] For the same 10 PRs, titles match the Conventional Commits form and the `type` corresponds to the branch prefix
- [ ] The source branches of the same 10 PRs used one of the prefixes `feat/`, `fix/`, `chore/`, `docs/`, `exp/`, and the PR title type matched the prefix verbatim
- [ ] A sample of recent PR bodies shows all five required sections present, with only Linked issues and Risk / rollout notes allowed to contain the literal `None`; any repository-specific sections appear *after* the required five, never interleaved
- [ ] `.github/workflows/pr-lint.yml` (or an equivalently-named workflow) exists and its job is declared as a required status check for `develop` in `.github/settings.yml`
- [ ] `.github/settings.yml` sets `allow_squash_merge: true`, `allow_merge_commit: false`, `allow_rebase_merge: false` for the repository
- [ ] The last 10 first-parent commits on `develop` (via `git log --first-parent develop -n 10`) each correspond to exactly one squash-merged PR and carry a Conventional-Commits-compliant message
- [ ] `.github/settings.yml` sets `required_status_checks.strict: true` for the `develop` branch protection (directly or via the `nolte/gh-plumbing` commons extension) so that GitHub enforces the branch-up-to-date precondition

## Open Questions
- _None at this time; all drafting questions have been resolved._
