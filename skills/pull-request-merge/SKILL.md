---
name: pull-request-merge
description: Promote an open draft pull request on the current branch to a merged state on `develop`, applying repository-declared labels and passing every gate from the pull-request-workflow spec. Invoke when the user asks to promote the draft PR, ship the PR, merge the draft, or bring the PR over the finish line. Also handles equivalent German-language requests. Delegates pre-merge review to the `review` skill (and `security-review` when the diff touches security-sensitive paths), derives labels from the Conventional-Commits type and touched paths, flips draft → ready, triggers automerge by applying the `automerge` label so the repository's automerge workflow squash-merges the PR once every required check is green, and verifies the merge commit landed on `develop`.
---

# Pull Request Merge

Promotes an open draft pull request (typically the one opened by `pull-request-create`) to a merged state on `develop`. This skill is the counterpart to `pull-request-create`: that skill opens the PR; this skill lands it. It honors `spec/project/pull-request-workflow/<canonical_language>.md`, `spec/project/branching-model/<canonical_language>.md`, and `spec/project/workflow-health/<canonical_language>.md` end-to-end: `enforce_admins: true` is respected, `--squash` is the only merge strategy, and failing required checks route to workflow-health triage rather than to a waiver.

## User-language policy

Detect the user's language and respond in it. All `git` and `gh` invocations, as well as labels applied to the PR, remain English so that portfolio automation (release-drafter, boring-cyborg, the `nolte/gh-plumbing` reusable-automerge) stays consistent across repositories.

## Preconditions

Before running any `git` or `gh` command, confirm:

- Current working directory is inside a git repository and the current branch **isn't** `develop` or `main`.
- `gh` is authenticated (`gh auth status`) and the remote resolves to a GitHub repository.
- A pull request is associated with the current branch (`gh pr view --json number,state,isDraft,baseRefName`). The PR is **open**, **draft**, and targets **`develop`**. If it's already non-draft, already merged, closed, or targets a different base, stop and report—a different operation is needed.
- Working tree is clean (`git status --porcelain` returns no lines). Uncommitted changes block the skill; commit, stash, or hand back to the user.
- The feature branch contains `origin/develop`'s tip (`git fetch origin develop && git merge-base --is-ancestor origin/develop HEAD`). If the branch lags, report the lag and hand back to the user; the skill doesn't silently rebase or merge `develop` into the feature branch.

## Operations

### 1. Inspect the PR and environment

Run in parallel:

- `gh pr view --json number,title,state,isDraft,baseRefName,headRefName,labels,url,mergeable,mergeStateStatus`
- `gh pr checks --json name,state,conclusion,bucket`
- `gh pr diff --name-only`
- `gh label list --limit 200 --json name`

Confirm the PR is open, draft, targets `develop`, and reports `mergeable: MERGEABLE`. If `mergeable: CONFLICTING`, stop and hand back to the user—conflicts are resolved in the working tree, not by this skill.

### 2. Delegate pre-merge review

Invoke the `review` skill with the PR number so it performs a final review of the diff (`Skill(skill="review")`). Wait for its report. If the review raises any blocking finding, surface it to the user verbatim and stop—don't flip the draft or merge until the user resolves the finding or explicitly overrides it.

If the diff touches a security-sensitive path—any of `.github/workflows/`, `.github/settings.yml`, `**/*.sh`, files that contain `secret` / `token` / `password` references, auth or signing code—additionally invoke the `security-review` skill. Block on any blocking finding from that skill the same way.

### 3. Derive and apply labels

Build a candidate label set and intersect it with the labels that actually exist in the repository (collected in step 1). **Never create a new label**; a candidate label that doesn't exist is reported as a portfolio gap to close via `.github/settings.yml` (directly or via `nolte/gh-plumbing:.github/commons-settings.yml`), not silently added.

Candidate sources:

- **Type label** from the PR title's Conventional-Commits prefix: `feat` → candidates `type:feat`, `kind:feat`, `feat`; same pattern for `fix`, `chore`, `docs`. Take the first candidate that exists.
- **Area labels** from touched paths (case-insensitive match against existing labels):
  - paths under `spec/` → candidates `area:spec`, `spec`
  - paths under `skills/` → candidates `area:skill`, `skills`
  - paths under `agents/` → candidates `area:agent`, `agents`
  - paths under `.github/workflows/` or `.github/settings.yml` → candidates `area:ci`, `ci`, `github-actions`
  - paths under `docs/` or `mkdocs.yml` → candidates `area:docs`, `documentation`
  - paths under `.claude/`, `.claude-plugin/`, or `CLAUDE.md` → candidates `area:claude`, `claude-code`

Apply the surviving set in a single call:

```
gh pr edit <number> --add-label <label1> --add-label <label2> …
```

Report the labels that were applied and any candidates that were skipped because no matching label existed.

### 4. Verify required checks

Re-run `gh pr checks <number>` after the label edit. Require **every** required status check declared for `develop` in `.github/settings.yml` to report `SUCCESS`. Three outcomes:

- **All green** → proceed to step 5.
- **At least one pending** → report the pending checks and stop. The user can rerun this skill once checks complete; don't poll or sleep here.
- **At least one failed** → don't flip draft and don't merge. Hand off to the `workflow-health` triage flow documented in `spec/project/workflow-health/<canonical_language>.md`: classify the failure (`defect` / `flake` / `infra` / `stale pin` / `secret drift` / `other`) and route the fix through a separate PR. Never retry the merge by re-running failed checks blindly—that's drift per the workflow-health spec.

### 5. Flip draft → ready

Once every required check is green:

```
gh pr ready <number>
```

Verify the flip (`gh pr view --json isDraft` returns `false`).

### 6. Trigger automerge

Apply the repository label `automerge` so that the `automerge.yaml` workflow (backed by the `nolte/gh-plumbing` reusable-automerge workflow and `pascalgn/automerge-action`) squash-merges the PR as soon as every required status check on the head commit is green and every branch-protection rule for `develop` is satisfied. This is the primary path per `spec/project/pull-request-workflow/<canonical_language>.md` §Automerge trigger protocol.

```
gh api -X POST repos/<owner>/<repo>/issues/<number>/labels -f "labels[]=automerge"
```

(`gh pr edit <number> --add-label automerge` is equivalent on most repositories, but sometimes fails with a deprecated-Projects GraphQL warning where Projects Classic is still enabled; the REST call avoids that noise.)

- The `automerge` label must exist in the repository (collected via `gh label list` in step 1) and the PR must already be non-draft (step 5). Applying the label on a red or pending head commit is a spec violation—re-verify checks in step 4 before this step.
- **Fallback (MAY path)**: if the repository doesn't ship the `automerge.yaml` workflow or lacks the `automerge` label, fall back to GitHub native automerge and report the missing automation to the user as a portfolio gap to close via `.github/settings.yml`:

  ```
  gh pr merge <number> --squash --auto
  ```

- `--squash` is mandatory per `spec/project/pull-request-workflow/<canonical_language>.md` (`allow_squash_merge: true` is the only enabled merge option).
- Never pass `--admin`. There is no admin-override path: `enforce_admins: true` on `develop` has no exception per the pull-request-workflow spec.
- Never pass `--merge` or `--rebase`. Those merge strategies are explicitly disabled in `.github/settings.yml` for repositories under this spec.

### 7. Verify the merge landed

Confirm that the PR reached `MERGED` state and `origin/develop` advanced:

```
gh pr view <number> --json state,mergedAt,mergeCommit,url
git fetch origin develop
git log --oneline -1 origin/develop
```

Report back to the user: PR URL, merged-at timestamp, merge commit SHA on `origin/develop`, and the labels that were applied. If the PR isn't yet in `MERGED` state because automerge is still waiting on checks, report the outstanding checks and tell the user the merge will complete automatically—don't poll or sleep.

### 8. Clean up local state

Once the PR is merged, offer (don't automatically execute) the following cleanup to the user:

- `git checkout develop && git pull --ff-only`: update the local integration branch
- `git branch -d <feature-branch>`: delete the local feature branch (safe delete; refuses to remove a branch whose commits aren't on `develop`)

The remote feature branch is handled by the platform per `spec/project/pull-request-workflow/<canonical_language>.md` §Post-merge branch cleanup: `delete_branch_on_merge: true` in `.github/settings.yml` (directly or via the `nolte/gh-plumbing` commons extension) lets GitHub remove it automatically right after the squash-merge. Confirm this in step 7 by checking that the remote branch is gone: `gh api repos/<owner>/<repo>/git/refs/heads/<feature-branch>` returns `404`. If the branch is still there, the platform setting is either missing or was enabled only later; in that one-off catch-up case, offer the manual REST call and only act with explicit user confirmation:

```
gh api -X DELETE repos/<owner>/<repo>/git/refs/heads/<feature-branch>
```

Never run `git push origin --delete …` or `gh api -X DELETE` without explicit user confirmation. Never make remote-branch deletion part of the automatic merge flow—the platform setting is the routine path, manual deletion is only a catch-up.

## Hard rules

- **Never** flip a draft to ready while any required check is pending or failing. Failures route to the `workflow-health` triage flow, not to a waiver.
- **Never** pass `--admin` to `gh pr merge`. `enforce_admins: true` on `develop` has no exception path.
- **Never** use a merge strategy other than `--squash`. Squash-merge is mandated by the `pull-request-workflow` spec.
- **Never** create a new GitHub label from this skill. Label candidates that don't exist in the repository are reported as a gap, not silently added.
- **Never** skip the `review` skill delegation. A final review is the cheapest pre-merge gate; only an explicit user override bypasses it.
- **Never** rebase or merge `develop` into the feature branch silently to fix a lag. Branch-freshness gaps return control to the user, consistent with `pull-request-create`.
- **Never** poll, sleep, or loop waiting for checks to complete. Report the outstanding state and stop; the user re-invokes the skill when ready.
- **Never** delete the remote feature branch as part of the automatic merge flow. Post-merge branch cleanup is the platform's job via `delete_branch_on_merge: true`; a manual `gh api -X DELETE` call is only a one-off catch-up and requires explicit user confirmation.
- When `spec/project/pull-request-workflow/`, `spec/project/branching-model/`, or `spec/project/workflow-health/` disagrees with this skill, the spec wins. Propose a skill update rather than silently diverging.
