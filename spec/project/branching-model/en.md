# Branching Model

Status: draft

## Context
Repositories in this portfolio use `main` as a presentation-only branch that always reflects the most recently published GitHub Release. Active development happens on `develop`; feature branches target `develop` via pull request. When a GitHub Release is published, reusable workflows from [`nolte/gh-plumbing`](https://github.com/nolte/gh-plumbing) fast-forward `main` to the released tag, so `main` remains a mechanically-maintained, read-only view of the last shipped artifact. Humans and AI agents that look at `main` see exactly what was released — never a work-in-progress state.

## Goals
- `main` always equals the last published GitHub Release, nothing else
- No manual commits, pushes, or merges land on `main` — every change flows through `develop` and a release
- The promotion from `develop` to `main` is automated, auditable, and triggered only by a published release
- Branch roles are unambiguous for humans and AI agents reading the repository

## Non-Goals
- Tag naming scheme (handled by release-drafter configuration)
- Changelog generation (handled by release-drafter)
- Publication to external registries (HACS, PyPI, container registries)
- Project-level Taskfile / CI target contents (covered by the project-structure spec)

## Requirements

### Branch roles
- **MUST** designate `develop` as the integration branch where all feature work lands via pull request
- **MUST** designate `main` as a release-presentation branch reflecting the most recently published GitHub Release
- **MUST NOT** allow manual commits, pushes, or merges directly to `main`; the branch is written to only by the release automation
- **MUST** use feature branches named with one of the prefixes `feat/`, `fix/`, `chore/`, or `docs/` and target `develop` in their pull request; these prefixes are identical to the Conventional Commits types used in PR titles so that the branch name and the commit type align without translation

### Branch protection
- **MUST** declare all branch-protection rules as code in `.github/settings.yml` (directly or via `_extends: nolte/gh-plumbing:.github/commons-settings.yml`) and synchronize them through the [Probot Settings app](https://probot.github.io/apps/settings/); protection rules **MUST NOT** be configured ad-hoc in the GitHub UI
- **MUST** protect `main` so that direct pushes from humans are blocked and only the release workflow (via `GITHUB_TOKEN`) can update it
- **SHOULD** protect `develop` so that pull requests require passing CI before merge
- **SHOULD** require linear history on `main` so the fast-forward from release tags stays clean

### Release flow
- **MUST** cut GitHub Releases from tags created on the `develop` branch — release-drafter maintains the draft, a human publishes it
- **MUST** update `main` exclusively through the release workflow on `release: [published]`
- **MUST** derive `main` content mechanically from the release; editing files directly on `main` is a bug
- **SHOULD** keep the default pull-request base set to `develop`, not `main`

### Required GitHub workflows
The repository **MUST** include the following workflows under `.github/workflows/`, each wired to the corresponding reusable workflow from `nolte/gh-plumbing`:

- **`release-drafter.yml`** — triggers on `push: [develop]`; uses `nolte/gh-plumbing/.github/workflows/reusable-release-drafter.yml` to maintain the draft GitHub Release that collects the next version's changes
- **`release-cd-refresh-master.yml`** — triggers on `release: [published]`; uses `nolte/gh-plumbing/.github/workflows/reusable-release-cd-refresh-master.yml` with `target_branch: main` to fast-forward `main` to the released commit; requires `contents: write` permission
- **`automerge.yaml`** — triggers on pull-request / review / check-suite events; uses `nolte/gh-plumbing/.github/workflows/reusable-automerge.yaml` so approved, green pull requests against `develop` merge automatically

The repository **SHOULD** also include, where applicable:

- **`release-cd-deliver-docs.yml`** — on `release: [published]`; publishes MkDocs output via `nolte/gh-plumbing/.github/workflows/reusable-mkdocs.yaml`
- Any additional `release: [published]` packaging workflow (for example `release.yml` producing an HACS ZIP) specific to the repository's delivery artifact

### Workflow integrity
- **MUST** keep the three required workflows (`release-drafter.yml`, `release-cd-refresh-master.yml`, `automerge.yaml`) in every repository that follows this branching model
- **SHOULD** pin the `nolte/gh-plumbing` reusable-workflow reference to a tag (for example `@v1.1.12`) rather than a moving branch, so the refresh behavior of `main` is reproducible

## Acceptance Criteria
- [ ] `develop` exists and is the default pull-request base
- [ ] `main` exists and is branch-protected so that humans cannot push directly
- [ ] Branch-protection rules for `main` and `develop` are declared in `.github/settings.yml` (directly or via the `nolte/gh-plumbing` commons extension), not only through the GitHub UI
- [ ] `.github/workflows/release-drafter.yml` is present and triggers on `push: [develop]`
- [ ] `.github/workflows/release-cd-refresh-master.yml` is present, triggers on `release: [published]`, and sets `target_branch: main`
- [ ] `.github/workflows/automerge.yaml` is present and invokes the `nolte/gh-plumbing` reusable automerge workflow
- [ ] The HEAD of `main` corresponds to a published GitHub Release tag (`git tag --points-at main` returns a release tag)
- [ ] There are no human-authored commits on `main` between two consecutive releases — only commits introduced by the refresh workflow
- [ ] Feature branches in the repository use one of the prefixes `feat/`, `fix/`, `chore/`, `docs/`
- [ ] If MkDocs is used, `.github/workflows/release-cd-deliver-docs.yml` is present and triggers on `release: [published]`

## Open Questions
- How should emergency hotfixes be handled — branch off `main`, merge back to both `main` and `develop`, or always cycle through `develop` plus a new patch release?
- Should `target_branch` remain `main` uniformly, even for HACS integrations whose historical convention was `master`?
- Is there a portfolio-wide policy for which `nolte/gh-plumbing` version tag to pin across all repositories, and how is it bumped?
- Should this spec prescribe a tag naming scheme (`v1.2.3` vs `1.2.3`) or leave that to release-drafter configuration per repository?
- Should the automerge workflow be mandatory, or optional when a repository prefers manual merges?
