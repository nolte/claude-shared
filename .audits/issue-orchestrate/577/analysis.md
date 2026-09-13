---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "577"
classification: "feature-request"
secondary-classes: ["infra"]
route: "direct"
status: draft
created: "2026-09-13"
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #577 — ci: upstream the PR body check to gh-plumbing as reusable-pr-lint.yaml
- **URL**: https://github.com/nolte/claude-shared/issues/577
- **Labels**: enhancement
- **Linked items**: nolte/gh-plumbing#418 (merged, `f6d74ea5`), #620, #621 (merged); status comment on #577 (2026-09-13T18:09Z) ticks AC 1–3
- **Prior art checked**: `gh search code reusable-pr-lint.yaml --owner nolte` → only claude-shared and gh-plumbing itself reference it (established, command output 2026-09-13); no other portfolio repo has a pr-lint workflow (`gh api …/contents/.github/workflows` for 5 repos, no `pr-lint` file)

## Classification

- **Primary class**: feature-request
- **Secondary class(es)**: infra
- **Rationale**: the remaining AC demonstrates reuse by adopting an existing reusable workflow in a second repository and cutting a release to pin against; no failing CI is being triaged.

## Scope

- **In scope** (operator decision 2026-09-13: „Übernahme + gh-plumbing-Release"):
  - publish gh-plumbing `v2.0.1` (draft already lists #418, established: `gh release view v2.0.1`)
  - adopt `reusable-pr-lint.yaml@v2.0.1` in `nolte/claude-home-assistant` with `pr-body / PR Lint` as required develop context
  - repin claude-shared's `pr-body` job from the commit SHA to `@v2.0.1`
  - close #577 with evidence
- **Out of scope**: adoption in `nolte/blog` (13/30 replayed PRs use title type `post`, outside the closed vocabulary — needs a vocabulary decision first); the other open gh-plumbing PR #422 (another session's work; not waited on)
- **Requirements gate**: no `project/requirements/` artefact exists for #577; operator override recorded 2026-09-13 („Override festhalten") — the issue's acceptance criteria are concrete and testable.

## Route

- **Decision**: direct
- **Rationale**: one outcome (reuse demonstrated), one PR per touched repository in a single dependency chain, no roadmap item created or retargeted.

## Work packages

### P1 — Publish gh-plumbing v2.0.1

- **Problem statement**: consumers pin gh-plumbing reusables to tags (claude-home-assistant pins `@v1.1.23`, established: `automerge.yaml:22`); `f6d74ea5` is on develop but unreleased (compare `v2.0.0...f6d74ea5` → ahead 2, established).
- **Acceptance criteria**: `gh release view v2.0.1 -R nolte/gh-plumbing` → `isDraft=false`; tag `v2.0.1` contains `f6d74ea5` (`compare v2.0.1...f6d74ea5` → behind/identical); `release-publish.yml` run conclusion `success`.
- **Touched files / artifacts**: gh-plumbing release `v2.0.1` (no file change expected; gh-plumbing has no `.github/release-automation.yml`, established: contents API 404)
- **Specialist**: nolte-shared skill `release-publish-trigger`
- **Depends on**: none

### P2 — Adopt reusable-pr-lint in claude-home-assistant

- **Problem statement**: AC 4 — at least one other portfolio repository adopts the reusable workflow.
- **Acceptance criteria**: (a) `.github/workflows/pr-lint.yml` calls `nolte/gh-plumbing/.github/workflows/reusable-pr-lint.yaml@v2.0.1` on the four `pull_request` events the spec names, least-privilege permissions; (b) `.github/settings.yml` develop contexts gain `pr-body / PR Lint`; (c) the adoption PR shows `pr-body / PR Lint` green on a conformant body and red when its title is switched to a `fix` type without a class sweep (then restored); (d) post-merge `branch_protection_audit.py --branch develop nolte/claude-home-assistant` → 4 contexts enforced, `ok`.
- **Touched files / artifacts**: claude-home-assistant `.github/workflows/pr-lint.yml` (new), `.github/settings.yml`
- **Specialist**: nolte-shared skill `cicd-pipeline-design`; review by `nolte-shared:cicd-pipeline-reviewer`
- **Depends on**: P1

### P3 — Repin claude-shared to the release tag

- **Problem statement**: claude-shared pins the commit SHA with a `# develop, nolte/gh-plumbing#418` comment (`.github/workflows/pr-lint.yml:69`); the release makes a tag pin available and matches the portfolio pin convention.
- **Acceptance criteria**: `pr-lint.yml:69` uses `@v2.0.1`; `pr-body / PR Lint` runs green on the PR; no other file names the SHA (`git grep f6d74ea5` → 0 hits, checked against the known positive before the edit).
- **Touched files / artifacts**: `.github/workflows/pr-lint.yml`
- **Specialist**: nolte-shared skill `cicd-pipeline-design`
- **Depends on**: P1

### P4 — Close #577

- **Problem statement**: develop merges don't autoclose; the issue needs the AC-4 evidence.
- **Acceptance criteria**: #577 closed with a comment linking P1 release, P2 PR + run URLs for both directions, P3 PR.
- **Touched files / artifacts**: issue #577
- **Specialist**: no matching specialised agent — generalist remediation
- **Depends on**: P2, P3

## Dependency ordering

P1 → (P2 ; P3, independent of each other) → P4

## Risks

- `.github/workflows/` and `.github/settings.yml` are security-sensitive paths → `cicd-pipeline-reviewer` plus the built-in `security-review` from the worktree before each PR.
- Required context `pr-body / PR Lint` in claude-home-assistant blocks merges on non-conformant bodies; replay of 40 PRs found 14 red, all from rules newer than those PRs (9 × missing class sweep, 5 × missing sections on #53–#57) — established by running the pinned checker locally. Mitigation: all new PRs go through `pull-request-create`.
- Settings sync lands ~5 min after merge; verify with the audit, not the merge.
- Publishing a release triggers `release-cd-refresh-master` on gh-plumbing; v2.0.0 ran the same path successfully (run 2026-08-02, established).

## Open questions

none

## Dispatch log

- 2026-09-13 P1 dispatched to skill `release-publish-trigger` — all 5 gates PASS on develop tip `6eeab5f4` (#423 by another session; draft also carries #422); `release-publish.yml` run 34782068029 `success`, v2.0.1 published 20:51:58Z, contains `f6d74ea5`. Cascade: deliver-docs `success`; refresh-master `failure` — pre-existing since v2.0.0 (`allow_force_pushes=false` on master, gh-plumbing#414), recurrence documented there; not in #577 scope.
- 2026-09-13 P2 dispatched to skill `cicd-pipeline-design` — hypothesis confirmed; refinement: tag pin recorded per github-actions-best-practices §A (MAY + MUST record); `spec-anchor` kept default (unmeasured on this repo). actionlint 1.7.12 clean, pre-commit green; committed `c519cf1` in claude-home-assistant worktree.
- 2026-09-13 P3 dispatched to skill `cicd-pipeline-design` — repin `@v2.0.1` with recorded tag choice.
