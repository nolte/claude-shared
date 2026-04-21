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
- **MUST** originate from a branch whose name starts with one of the prefixes `feat/`, `fix/`, `chore/`, or `docs/` (as declared by the branching-model spec)
- **MUST** use a PR title in Conventional Commits form `<type>(<scope>)?: <summary>`, where `<type>` is literally identical to the branch prefix (prefix `feat/` → type `feat`, `fix/` → `fix`, `chore/` → `chore`, `docs/` → `docs`); no translation or aliasing is permitted
- **MUST** keep a single PR scoped to one logical change; unrelated changes are split into separate PRs
- **SHOULD** link at least one related issue via `Closes #<n>` or `Refs #<n>` in the description when a tracking issue exists

### PR description structure
A pull-request template **MUST** exist at `.github/pull_request_template.md` and **MUST** contain the following sections, in this exact order and with these exact headings:

1. **Summary** — one to three sentences stating *what* the PR changes and *why*
2. **Changes** — bulleted list of user-visible or reviewer-relevant changes
3. **Linked issues** — `Closes #…` / `Refs #…` entries, or the literal text `None`
4. **Testing** — how the change was verified (commands run, manual steps, screenshots)
5. **Risk / rollout notes** — risk class, migrations, feature flags, or the literal text `None`

- **MUST** retain every template section in the PR body; sections are never deleted, even when empty
- **MUST NOT** leave Summary, Changes, or Testing empty; Linked issues and Risk / rollout notes **MAY** use the literal text `None`
- **SHOULD** use imperative mood in Summary and Changes (`Add …`, `Fix …`, not `Added …`)
- **SHOULD** link to the relevant spec file under `spec/` when the change implements or modifies a spec

### CI gate into `develop`
- **MUST** declare the full set of required status checks for `develop` as code in `.github/settings.yml` (directly or via the `nolte/gh-plumbing` commons extension); the GitHub UI is **NOT** an acceptable place to add or remove required checks
- **MUST** require every declared check to report success before a PR can merge into `develop`
- **MUST** configure the `automerge.yaml` workflow so it only merges a PR when every required check reports success and the PR is approved
- **SHOULD** set `enforce_admins: true` for `develop` branch protection so that admin overrides cannot bypass a failing check; any repository that waives this **MUST** record the reason in the repository's `README.md` or an explicit `.github/BRANCH_PROTECTION.md`
- **SHOULD** block merge while any review explicitly requests changes, even after CI becomes green

### Draft and work-in-progress PRs
- **SHOULD** open PRs as Draft while work is ongoing and mark them ready for review only once CI is expected to pass and the description is complete
- **MUST NOT** mark a PR ready for review when any required section of the description is missing or empty in violation of the rules above

## Acceptance Criteria
- [ ] `.github/pull_request_template.md` exists and its section headings match the five headings listed in "PR description structure", in order
- [ ] `.github/settings.yml` declares required status checks for `develop` (directly or via the `nolte/gh-plumbing` commons extension)
- [ ] `enforce_admins` is `true` for the `develop` branch protection rule, or a waiver is documented in `README.md` or `.github/BRANCH_PROTECTION.md`
- [ ] For the last 10 PRs merged into `develop`, every required status check was green at merge time (spot-check via `gh pr list --state merged --base develop --limit 10 --json number,title,mergedAt,statusCheckRollup`)
- [ ] For the same 10 PRs, titles match the Conventional Commits form and the `type` corresponds to the branch prefix
- [ ] The source branches of the same 10 PRs used one of the prefixes `feat/`, `fix/`, `chore/`, `docs/`, and the PR title type matched the prefix verbatim
- [ ] A sample of recent PR bodies shows all five required sections present, with only Linked issues and Risk / rollout notes allowed to contain the literal `None`

## Open Questions
- Should the squash-merge vs. merge-commit policy for PRs into `develop` be declared here or kept in the branching-model spec?
- Is `enforce_admins: true` a hard **MUST** across the portfolio, or is case-by-case opt-out via a documented waiver acceptable in perpetuity?
- Should the PR template section list be strictly identical across the portfolio, or may a repository add repository-specific sections below the five required ones?
- Do we need an automated linter (e.g. a reusable workflow) that fails a PR whose body or title violates this spec, rather than relying on reviewer discipline?
