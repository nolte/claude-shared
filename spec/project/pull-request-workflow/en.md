# Pull Request Workflow

Status: draft

## Context
Pull requests (PRs, equivalent to GitLab merge requests / MRs) are the sole path for changes into the `develop` integration branch defined in the branching-model spec. Two recurring problems motivate this spec: (1) PR descriptions vary in shape, which makes review harder and degrades the release-drafter output that summarizes `develop` activity, and (2) PRs occasionally reach `develop` before CI has reported green, undermining the "always-green develop" assumption that the release flow relies on. This spec defines how PRs are authored and which gates they must pass before merging into `develop`. It complements—and doesn't restate—the branching-model spec, which declares the target branch and the automerge workflow, and the project-structure spec, which declares the `.github/settings.yml` mechanics.

## Goals
- Every PR into `develop` follows a single, consistent description structure so reviewers, release-drafter, and AI agents see the same shape
- No PR reaches `develop` unless every required CI check has reported success
- Preconditions (branch naming, target branch, title form) are fully declared in code and enforceable via branch protection
- Humans and AI agents authoring PRs against these repositories produce artifacts that match the same standard without per-repo onboarding
- Authors and AI agents catch prose, format, and YAML errors locally before pushing, so CI feedback loops are reserved for logic failures that only CI can surface
- Red required checks are resolved fix-forward on the same branch, preserving review context and ensuring automerge only reacts to the current head commit
- Automerge triggering is explicit (label + non-draft) so humans and automation agree on when a PR is ready to merge

## Non-Goals
- Target-branch policy and release flow (covered by the branching-model spec)
- Branch-protection declaration mechanics via `.github/settings.yml` (covered by the project-structure spec; this spec only states which rules must be declared)
- Automerge workflow internals (covered by `nolte/gh-plumbing` reusable-automerge and referenced from the branching-model spec)
- Release-notes / changelog content (handled by release-drafter)
- Code-review approval policy (who reviews, how many approvals): not in scope here

## Requirements

### PR preconditions
- **MUST** target `develop` as the base branch
- **MUST** originate from a branch whose name starts with one of the prefixes `feat/`, `fix/`, `chore/`, `docs/`, or `exp/` (as declared by the branching-model spec)
- **MUST** use a PR title in Conventional Commits form `<type>(<scope>)?: <summary>`, where `<type>` is literally identical to the branch prefix (prefix `feat/` → type `feat`, `fix/` → `fix`, `chore/` → `chore`, `docs/` → `docs`, `exp/` → `exp`); no translation or aliasing is permitted
- **MUST** keep a single PR scoped to one logical change; unrelated changes are split into separate PRs—the sole exception is an `exp/` PR, which **MAY** bundle loosely related exploratory changes that share an iteration time frame, because that's the whole purpose of the experimental branch type declared in the branching-model spec
- **SHOULD** link at least one related issue via `Closes #<n>` or `Refs #<n>` in the description when a tracking issue exists

### Branch freshness
- **MUST** ensure the feature branch contains every commit of the current `develop` tip before the PR is opened, so the CI run reflects the state that will exist on `develop` after merge; this is achieved by rebasing the feature branch onto `develop` (rebase is the spec-mandated synchronization method per the MUST below in this section, not a contributor preference)
- **MUST** re-synchronize the feature branch with `develop` whenever `develop` advances while the PR is open, before the PR is moved out of Draft or before automerge is allowed to act; a PR whose branch lags behind `develop` isn't considered ready for merge
- **MUST** enable the GitHub "require branches to be up to date before merging" option for `develop` in `.github/settings.yml` (in `protection.required_status_checks.strict: true`, directly or via the `nolte/gh-plumbing` commons extension), so the platform enforces this precondition in addition to the client-side workflow
- **MUST** use rebase (not merge) to perform the synchronization with `develop`; rebase produces a linear feature-branch history that lands as a single squash-commit on `develop` per `### Merge strategy`, ensures every PR's CI run reflects the merge-time `develop` tip without an intermediate merge bubble, and standardises the path from feature branch into `develop` so reviewers see one shape across every PR. The synchronization **MUST** leave `develop` fully contained in the feature branch before the PR is opened or re-requested for review; force-with-lease pushes that follow the rebase are governed by §Fix-forward on red checks

### PR description structure
A pull-request template **MUST** exist at `.github/pull_request_template.md` and **MUST** contain the following sections, in this exact order and with these exact headings:

1. **Summary**: one to three sentences stating *what* the PR changes and *why*
2. **Changes**: bulleted list of user-visible or reviewer-relevant changes
3. **Linked issues**: `Closes #…` / `Refs #…` entries, or the literal text `None`
4. **Testing**: how the change was verified (commands run, manual steps, screenshots)
5. **Risk / rollout notes**: risk class, migrations, feature flags, or the literal text `None`

- **MUST** retain every required template section in the PR body; sections are never deleted, even when empty
- **MUST NOT** leave Summary, Changes, or Testing empty; Linked issues and Risk / rollout notes **MAY** use the literal text `None`
- **MAY** add repository-specific sections *below* the five required sections; additional sections **MUST** appear after all five required sections and **MUST NOT** be interleaved between them
- **SHOULD** use imperative mood in Summary and Changes (`Add …`, `Fix …`, not `Added …`)
- **SHOULD** link to the relevant spec file under `spec/` when the change implements or modifies a spec

### PR lint workflow
- **MUST** include a workflow under `.github/workflows/` (for example `pr-lint.yml`) that lints PR title and body on the `pull_request` events `opened`, `edited`, `synchronize`, and `ready_for_review`
- **MUST** register this workflow's job as a required status check for `develop` in `.github/settings.yml`
- **MUST** fail the check if the PR title doesn't match the Conventional Commits form `<type>(<scope>)?: <summary>` with `<type>` ∈ {`feat`, `fix`, `chore`, `docs`, `exp`}
- **MUST** fail the check if the PR body doesn't contain all five required section headings in the declared order
- **MUST** fail the check if Summary, Changes, or Testing is empty or contains only the literal text `None`
- **MUST NOT** fail the check when the body contains additional repository-specific sections appended after the five required sections, so long as the required sections themselves are present, in order, and non-empty where required
- **SHOULD** implement the linter as a reusable workflow under `nolte/gh-plumbing` (for example `reusable-pr-lint.yaml`) so every repository inherits one implementation rather than forking local copies that drift

### CI gate into `develop`
- **MUST** declare the full set of required status checks for `develop` as code in `.github/settings.yml` (directly or via the `nolte/gh-plumbing` commons extension); the GitHub UI **MUST NOT** be used to add or remove required checks
- **MUST** require every declared check to report success before a PR can merge into `develop`
- **MUST** configure the `automerge.yaml` workflow so it merges a PR only when every required status check on the PR's head commit reports success and every review-related protection rule configured for `develop` (for example `required_approving_review_count` or Code Owner reviews) is satisfied; the workflow **MUST NOT** bypass any protection rule, and repositories that don't require approving reviews (`required_approving_review_count: 0`) still merge only once every required status check on the head commit is green
- **MUST** set `enforce_admins: true` for `develop` branch protection so that admin overrides can't bypass a failing required check; the CI gate has no exception path, and a waiver isn't permitted—if a required check is persistently broken, the correct remedy is a PR against `.github/settings.yml` (which itself passes the gate) to remove or replace the check, not a one-off bypass
- **SHOULD** block merge while any review explicitly requests changes, even after CI becomes green

### Merge strategy
- **MUST** merge PRs into `develop` using squash-merge; the resulting commit on `develop` is a single commit per PR carrying the Conventional-Commits-compliant PR title as its message
- **MUST** declare squash-merge as the only enabled merge option in `.github/settings.yml` for repositories following this spec: `allow_squash_merge: true`, `allow_merge_commit: false`, `allow_rebase_merge: false`
- **SHOULD** keep the PR title as the default squash-commit message so the `develop` history is a linear stream of Conventional-Commits messages, directly consumable by release-drafter

### Post-merge branch cleanup
- **MUST** set `delete_branch_on_merge: true` in `.github/settings.yml`: directly or via the `nolte/gh-plumbing` commons extension—so that GitHub deletes the feature branch on the remote once its PR is merged into `develop`; merged branches **MUST NOT** linger on the remote
- **SHOULD** rely on the platform setting rather than on client-side `--delete-branch` flags passed to `gh pr merge`; when automerge handles the merge, only the platform setting fires, so the platform is the authoritative path
- **MAY** delete residual remote branches manually via `gh api -X DELETE repos/<owner>/<repo>/git/refs/heads/<branch>` as a one-off catch-up when the platform setting was enabled only later—not as a routine operation

### Linked-issue closure on develop merge
- **MUST** treat `Closes #<n>` / `Fixes #<n>` / `Resolves #<n>` keywords in the PR body as advisory on a `develop` merge; GitHub's reference-closing autolink fires only on the repository's **default branch** (`main` under this branching model), so a squash-merge into `develop` leaves referenced tracking issues `OPEN`. The issues close implicitly only when `release-cd-refresh-master.yml` fast-forwards `main` to the released commit (per `branching-model`).
- **SHOULD** close each referenced tracking issue manually after a `develop` merge, with a cross-reference comment naming the merging PR and the merge-commit SHA on `develop`, rather than waiting for the next release-fast-forward to close it implicitly; `skills/pull-request-merge/SKILL.md` operationalises this as a post-merge step that lists open referenced issues and waits for operator confirmation before invoking `gh issue close --reason completed`
- **MUST NOT** close a referenced issue without explicit operator confirmation in the merging session—issue closure is an externally-visible action and the operator may have closed the issue through another path already

### Draft and work-in-progress PRs
- **SHOULD** open PRs as Draft while work is ongoing and mark them ready for review only once CI is expected to pass and the description is complete
- **MUST NOT** mark a PR ready for review when any required section of the description is missing or empty in violation of the rules above

### Pre-push verification
- **MUST** run the repository's local lint target (`task lint`) on the feature branch before pushing a new commit to a PR branch, whenever the repository provides a `Taskfile.yml` with a `lint` target **or** a `.pre-commit-config.yaml`; the CI `lint` check exists as a backstop, not as the primary place to discover prose-style, YAML, or formatting errors
- **SHOULD** run the equivalent local lint tooling before every push even when neither a Taskfile `lint` target nor a pre-commit configuration is present, using whatever linting the repository provides
- **MUST** resolve every local lint failure before pushing; intentionally pushing a commit that's known to fail locally and relying on CI to report it's a spec violation

### Fix-forward on red checks
- **MUST** resolve a red required status check by pushing a new commit to the same branch; amending a commit that was already pushed (`git commit --amend` after the push) isn't permitted because it destroys review context and breaks comment anchoring
- **MUST NOT** use `git push --force` or `git push --force-with-lease` on a branch that's visible through an open non-draft PR, except when the force-push is explicitly part of a rebase onto the advanced `develop` tip (as required by §Branch freshness) and the author documents the rebase in a PR comment
- **MUST** move the PR back to Draft (or keep it as Draft) while any required check is red or while a fix is in flight; the PR is only taken out of Draft once the required checks on the head commit are green again and the body still satisfies §PR description structure
- **MUST NOT** trigger merge (applying the `automerge` label or running `gh pr merge` manually) based on a status that no longer reflects the current head commit; the green signal must originate from the most recent commit on the branch

### Automerge trigger protocol
- **MUST** trigger automerge by applying the repository label `automerge` to the PR; the `automerge.yaml` workflow is driven by this label through the `nolte/gh-plumbing` reusable automerge workflow and doesn't act on unlabeled PRs
- **MUST** mark the PR as ready for review (not Draft) before applying the label or before the action is expected to merge; the reusable automerge workflow ignores Draft PRs by design
- **MUST** ensure every required status check on the head commit is green before applying the label; applying it on a red or pending head leaves the PR queued for automerge without progress and is misleading to reviewers
- **SHOULD** remove the `automerge` label when the author decides to pause automerge (for example to wait for additional review) and re-apply it when ready, rather than leaving the label on a PR that's no longer intended to automerge
- **MAY** use `gh pr merge --squash` manually instead of the label-driven automerge workflow when repository policy allows a maintainer to merge directly; the merge strategy (§Merge strategy) still applies

## Acceptance Criteria
- [ ] `.github/pull_request_template.md` exists and its section headings match the five headings listed in "PR description structure," in order
- [ ] `.github/settings.yml` declares required status checks for `develop` (directly or via the `nolte/gh-plumbing` commons extension)
- [ ] `enforce_admins` is `true` for the `develop` branch protection rule; no waiver mechanism exists in the repository
- [ ] For the last 10 PRs merged into `develop`, every required status check was green at merge time (spot-check via `gh pr list --state merged --base develop --limit 10 --json number,title,mergedAt,statusCheckRollup`)
- [ ] For the same 10 PRs, titles match the Conventional Commits form and the `type` corresponds to the branch prefix
- [ ] The source branches of the same 10 PRs used one of the prefixes `feat/`, `fix/`, `chore/`, `docs/`, `exp/`, and the PR title type matched the prefix verbatim
- [ ] A sample of recent PR bodies shows all five required sections present, with only Linked issues and Risk / rollout notes allowed to contain the literal `None`; any repository-specific sections appear *after* the required five, never interleaved
- [ ] A sample of recent `develop` merges whose PR bodies carried `Closes #<n>` keywords shows each referenced tracking issue either closed manually with a cross-reference comment naming the merging PR and the merge-commit SHA, or still open pending the next `release-cd-refresh-master.yml` fast-forward of `main`; the autolink **MUST NOT** have closed any of them silently on the `develop` merge
- [ ] `.github/workflows/pr-lint.yml` (or an equivalently-named workflow) exists and its job is declared as a required status check for `develop` in `.github/settings.yml`
- [ ] `.github/settings.yml` sets `allow_squash_merge: true`, `allow_merge_commit: false`, `allow_rebase_merge: false` for the repository
- [ ] The last 10 first-parent commits on `develop` (via `git log --first-parent develop -n 10`) each correspond to exactly one squash-merged PR and carry a Conventional-Commits-compliant message
- [ ] `.github/settings.yml` sets `required_status_checks.strict: true` for the `develop` branch protection (directly or via the `nolte/gh-plumbing` commons extension) so that GitHub enforces the branch-up-to-date precondition
- [ ] For the last 10 PRs merged into `develop`, no PR was moved out of Draft while a required status check was red or pending on the head commit (spot-check via PR timeline events)
- [ ] For the same 10 PRs, the `automerge` label was only present on PRs that were already marked ready for review; the label didn't persist on PRs later withdrawn from automerge
- [ ] For the same 10 PRs, no force-push appears in the branch history between leaving Draft and merge (spot-check via `gh api repos/<owner>/<repo>/pulls/<number>/commits`: no rewritten commits after the PR was ready for review)
- [ ] In repositories that provide a `Taskfile.yml` with a `lint` target or a `.pre-commit-config.yaml`, a spot-check of recent PRs shows that the first push of the head commit that was merged didn't introduce a CI `lint` regression that local tooling would have caught
- [ ] The `automerge.yaml` workflow is configured so that the reusable automerge workflow only merges when every required status check on the head commit is green and every review-related branch-protection rule on `develop` is satisfied, regardless of whether `required_approving_review_count` is 0 or higher
- [ ] `.github/settings.yml` sets `delete_branch_on_merge: true` for the repository (directly or via the `nolte/gh-plumbing` commons extension), and a spot-check of `git branch -r` shows no merged-PR feature branches lingering on the remote beyond the automation window

## Open Questions
- _None at this time; all drafting questions have been resolved._
