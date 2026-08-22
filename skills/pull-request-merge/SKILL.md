---
name: pull-request-merge
description: Promotes an open draft pull request on the current branch to a merged state on `develop`, applying repository-declared labels and passing every gate from the pull-request-workflow spec. Invoke when the user asks to promote the draft PR, ship the PR, merge the draft, or bring the PR over the finish line. Also handles equivalent German-language requests. Delegates pre-merge review to the `review` skill (and `security-review` when the diff touches security-sensitive paths), derives labels from the Conventional-Commits type and touched paths, flips draft → ready, triggers automerge by applying the `automerge` label so the repository's automerge workflow squash-merges the PR once every required check is green, and verifies the merge commit landed on `develop`. Supports resume on re-invocation per `spec/claude/resumable-work/`.
tags: [pull-request]
phase: review
summary: "Promotes a draft PR to merged on develop, passing every pull-request-workflow gate."
summary_de: "Befördert einen Draft-PR auf develop und durchläuft jeden Pull-Request-Workflow-Gate."
use_when:
  - "you want to merge the open draft PR on this branch"
  - "you want to ship the current PR to develop"
  - "you want to apply automerge and let the squash-merge workflow land the PR"
dont_use_when:
  - situation: "You want to create or open the PR in the first place"
    alternative: pull-request-create
see_also:
  - pull-request-create
  - workflow-health-triage
examples:
  - prompt: "Merge the open PR"
    outcome: "Ready PR squash-merged onto develop; merge commit verified."
resumable: true
---

# Pull Request Merge

Promotes an open draft pull request (typically the one opened by `pull-request-create`) to a merged state on `develop`. This skill is the counterpart to `pull-request-create`: that skill opens the PR; this skill lands it. It honors `spec/project/pull-request-workflow/<canonical_language>.md`, `spec/project/branching-model/<canonical_language>.md`, and `spec/project/workflow-health/<canonical_language>.md` end-to-end: `enforce_admins: true` is respected, `--squash` is the only merge strategy, and failing required checks route to workflow-health triage rather than to a waiver.

## Why this is a skill, not an agent

Read `references/skill-vs-agent-rationale.md` when reviewing or challenging the artifact-type choice — in short: externally-visible PR mutations (draft → ready, `automerge` label, fallback merge) gate on mid-flow user confirmation, the skill orchestrates `review`/`security-review`/`workflow-health`, and wait mode needs a visible per-round status line, all of which default the orchestrator to skill form.

## User-language policy

Detect the user's language and respond in it. All `git` and `gh` invocations, as well as labels applied to the PR, remain English so that portfolio automation (release-drafter, boring-cyborg, the `nolte/gh-plumbing` reusable-automerge) stays consistent across repositories.

## Preconditions

Before running any `git` or `gh` command, confirm:

- Current working directory is inside a git repository and the current branch **isn't** `develop` or `main`.
- `gh` is authenticated (`gh auth status`) and the remote resolves to a GitHub repository.
- A pull request is associated with the current branch (`gh pr view --json number,state,isDraft,baseRefName`). The PR is **open**, **draft**, and targets **`develop`**. If it's already non-draft, already merged, closed, or targets a different base, stop and report—a different operation is needed.
- Working tree is clean (`git status --porcelain` returns no lines). Uncommitted changes block the skill; commit, stash, or hand back to the user.
- The feature branch contains `origin/develop`'s tip (`git fetch origin develop && git merge-base --is-ancestor origin/develop HEAD`). If the branch lags, report the lag and hand back to the user; the skill doesn't silently rebase or merge `develop` into the feature branch.

## Sequential merge of multiple ready PRs

This skill merges **one** PR — the one on the current branch. When several PRs are ready at the same time, it's invoked once per PR, serially, never in parallel, per `spec/project/pull-request-workflow/<canonical_language>.md` §"Sequential merge of multiple open PRs":

- Merge in **dependency order** when one ready PR builds on another — the prerequisite PR first; where no dependency exists, the operator picks the order among the remaining ready PRs.
- The Preconditions lag-check (`git merge-base --is-ancestor origin/develop HEAD`) is the enforcement point for the spec's rebase-between-merges rule: once a sibling PR lands on `develop`, every other ready PR's branch lags, so this skill stops and hands back until the operator rebases that PR onto the new `develop` tip and its required checks report green again on the rebased head (a green signal recorded before the rebase doesn't authorize the merge).
- Step 9 surfaces any remaining open, ready sibling PRs after a merge so the operator can rebase and re-invoke for the next one in order.

## Operations

### 1. Inspect the PR and environment

Run in parallel:

- `gh pr view --json number,title,state,isDraft,baseRefName,headRefName,labels,url,mergeable,mergeStateStatus`
- `gh pr checks --json name,state,conclusion,bucket`
- `gh pr diff --name-only`
- `gh label list --limit 200 --json name`

**Tooling (optional GitHub MCP):** prefer `github:pull_request_read` for the PR-state reads and `github:list_pull_requests` / `github:list_branches` for the sibling-PR and branch-existence checks, falling back to the `gh` commands shown, per `spec/claude/mcp-tool-preference/`. `gh pr checks` (check rollup) and `gh label list` have no MCP tool and stay `gh` (OQ-D); every merge/label/ready/delete write stays `gh`/git. `gh` stays authoritative; output identical.

Confirm the PR is open, draft, targets `develop`, and reports `mergeable: MERGEABLE`. If `mergeable: CONFLICTING`, stop and hand back to the user—conflicts are resolved in the working tree, not by this skill.

### 2. Delegate pre-merge review

Invoke the `review` skill with the PR number so it performs a final review of the diff (`Skill(skill="review")`). Wait for its report. If the review raises any blocking finding, surface it to the user verbatim and stop—don't flip the draft or merge until the user resolves the finding or explicitly overrides it.

If the diff touches a security-sensitive path—any of `.github/workflows/`, `.github/settings.yml`, `**/*.sh`, files that contain `secret` / `token` / `password` references, auth or signing code—additionally invoke the `security-review` skill. Block on any blocking finding from that skill the same way.

Both built-ins compose their diff from fixed `git ... origin/HEAD...` substitutions that take no path argument, so they read **this session's** working directory rather than any path you pass them. Run them from a working copy that actually holds the change, and check the reported file list against `git diff --stat origin/develop...HEAD` before believing a clean result. A clean report over an empty diff is a failed gate rather than a pass, per `spec/project/issue-orchestration/` §Verification and traceability. This matters most when the branch was produced by `issue-orchestrate`, whose worktree isolation puts the change somewhere the session isn't.

### 3. Derive and apply labels

Build a candidate label set and intersect it with the labels that actually exist in the repository (collected in step 1). **Never create a new label**; a candidate label that doesn't exist is reported as a portfolio gap to close via `.github/settings.yml` (directly or via `nolte/gh-plumbing:.github/commons-settings.yml`), not silently added.

Read `references/label-derivation.md` when deriving the candidate set — it carries the full candidate table (the type-label Conventional-Commits prefix map and the touched-path → area-label rows), the single `gh pr edit --add-label` apply call, and the rule to report both applied labels and skipped candidates.

### 4. Verify required checks

Re-run `gh pr checks <number>` after the label edit. Require **every** required status check declared for `develop` in `.github/settings.yml` to report `SUCCESS`. Three outcomes:

- **All green** → proceed to step 5.
- **At least one pending** → default behavior is to report the pending checks and stop; the user reruns the skill once checks complete. When the user opts in to **wait mode** (see "Wait mode" below), re-check the same `gh pr checks` call under the bounded caps in `references/wait-mode.md` until every required check is green; on timeout, stop and report the still-pending checks just like the default path. **Polling is permitted only inside wait mode**; outside wait mode, the no-poll rule still applies.
- **At least one failed** → don't flip draft and don't merge, even in wait mode. Hand off to the `workflow-health-triage` skill (which implements `spec/project/workflow-health/<canonical_language>.md`): classify the failure (`defect` / `flake` / `infra` / `stale pin` / `secret drift` / `other`) and route the fix through a separate PR. Never retry the merge by re-running failed checks blindly—that's drift per the workflow-health spec.

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

The `automerge.yaml` workflow exits `SUCCESS` even when `pascalgn/automerge-action`'s internal `mergeResult` is `merge_failed` (for example when the reusable workflow's `MERGE_METHOD` default doesn't match the repo's allowed strategy, or when the `uses:` tag points to a `nolte/gh-plumbing` version that lacks the `MERGE_METHOD: squash` override). A green check rollup is **not** proof the merge happened. Verify in two passes:

**7a. Confirm PR and `develop` state directly.**

```
gh pr view <number> --json state,mergedAt,mergeCommit,url
git fetch origin develop
git log --oneline -1 origin/develop
```

If `state == MERGED` and `mergeCommit.oid` appears on `origin/develop`, report back and proceed to step 8. If `state == OPEN` and at least one required check is still running, the default behavior is to report the outstanding checks and stop—the merge will complete automatically once `pascalgn/automerge-action` sees green required checks. When the user opts in to **wait mode** (see "Wait mode" below), re-check `gh pr view --json state,mergedAt,mergeCommit` under the bounded caps in `references/wait-mode.md` until `state == MERGED`; on timeout, stop and report the still-`OPEN` state plus the most recent `gh pr checks` snapshot.

**7b. Audit the automerge workflow when the PR is `OPEN` with all required checks green and the `automerge` label applied.** Read `references/automerge-verification.md` when 7a leaves the PR `OPEN` with green required checks — it carries the runbook that pulls the workflow's internal `mergeResult` out of the run logs, the `merge_failed` classification (a `workflow-health` incident, **not** a retryable label-apply — never re-apply `automerge` or re-run the workflow blindly), and the common `stale pin` cause with its bump target.

Report back: PR URL, merged-at timestamp, merge commit SHA on `origin/develop`, the labels that were applied, and—if 7b caught a silent no-op—the workflow-health classification and the remediation the user needs to take next.

### 8. Close referenced tracking issues

GitHub's `Closes #<n>` / `Fixes #<n>` / `Resolves #<n>` autolinks fire only on default-branch merges. Per `spec/project/pull-request-workflow/<canonical_language>.md` §"Linked-issue closure on develop merge", a squash-merge into `develop` leaves referenced tracking issues `OPEN`; this step closes them with operator confirmation rather than waiting for the next `release-cd-refresh-master.yml` fast-forward of `main`.

Run only when step 7a confirmed `state == MERGED`. If the PR body carries no closing-keyword references, skip this step.

Read `references/issue-closure.md` when the merged PR body carries closing-keyword references — it carries the closing-keyword regex (and the `Refs #<n>` exclusion), the per-issue already-`CLOSED` skip check, the operator-confirmation gate before any close, and the exact `gh issue close` cross-reference comment. **Never** close a referenced tracking issue without explicit operator confirmation in the merging session.

### 9. Clean up local state

Once the PR is merged, offer (don't automatically execute) the following cleanup to the user:

- `git checkout develop && git pull --ff-only`: update the local integration branch
- `git branch -d <feature-branch>`: delete the local feature branch (safe delete; refuses to remove a branch whose commits aren't on `develop`)

The **remote** branch is the platform's job, not this skill's: `delete_branch_on_merge: true` removes it after the squash-merge, and step 7 confirms it by expecting a `404` from the ref. Never delete it manually without explicit user confirmation, and never fold that into the automatic flow.

Finally, surface what's still queued (`gh pr list --state open --base develop`) so the operator can continue the serial flow per §"Sequential merge of multiple ready PRs". Every remaining PR now lags the advanced `develop` tip and **must** be rebased and go green again before this skill runs for it. Don't rebase or re-invoke automatically.

`references/branch-cleanup.md` carries the confirmation call, the one-off catch-up case when the branch survives, and why the serial flow stays operator-driven.

## Wait mode

The skill is single-shot by default: when step 4 finds pending checks or step 7a finds the PR still `OPEN`, the skill reports and stops; the user re-invokes once GitHub is in the next state. **Wait mode** is an opt-in that lets the skill wait for state transitions inside a single invocation, bounded by hard caps (interval ≥60s, wall-clock ≤15 min, ≤10 retries per wait point, visible status line per round, failure short-circuits to workflow-health). Read `references/wait-mode.md` when the user opts in via `--wait` or an unambiguous "wait until X" instruction in the prompt — the reference covers activation, every cap with its rationale, the per-step implementation pattern (step 4 vs. step 7a), and the prompt-cache trade-off that justifies the bounds.

## Examples

- Read `examples/01-clean-merge-via-automerge-label.md` when promoting a ready PR through the automerge label on the first end-to-end run.
- Read `examples/02-pending-checks-reports-and-stops.md` when required checks are still pending and the skill reports state instead of proceeding.
- Read `examples/03-wait-mode-with-explicit-flag.md` when the user opts into wait mode via `--wait` and you need to see the polling loop behaviour.

## Gotchas

Read `references/gotchas.md` when a `gh` call or merge signal behaves unexpectedly — the exact-spelling `automerge` label, `automerge.yaml` `SUCCESS` not proving the merge, the required-checks list living in `.github/settings.yml` (not the UI), and `Closes #N` autolinks not firing on `develop` merges. The load-bearing versions are also in the Hard rules and the numbered steps.

## Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/pull-request-merge/<run-id>.yml` after every successful user-approval gate and after each named phase boundary. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope (`schema_version`, `run_id`, `inputs`, `phase`, `decisions[]`, `status`, ...) and the fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

## Hard rules

- **Never** flip a draft to ready while any required check is pending or failing. Failures route to the `workflow-health` triage flow, not to a waiver.
- **Never** pass `--admin` to `gh pr merge`. `enforce_admins: true` on `develop` has no exception path.
- **Never** use a merge strategy other than `--squash`. Squash-merge is mandated by the `pull-request-workflow` spec.
- **Never** create a new GitHub label from this skill. Label candidates that don't exist in the repository are reported as a gap, not silently added.
- **Never** skip the `review` skill delegation. A final review is the cheapest pre-merge gate; only an explicit user override bypasses it.
- **Never** rebase or merge `develop` into the feature branch silently to fix a lag. Branch-freshness gaps return control to the user, consistent with `pull-request-create`.
- **Never** merge multiple ready PRs in parallel. Per the pull-request-workflow spec they merge one at a time; after each merge every remaining ready PR lags `develop` and must be rebased onto the new tip (enforced by the Preconditions lag-check) before this skill proceeds, in dependency order where one PR builds on another.
- **Never** poll, sleep, or loop waiting for checks to complete **unless the user has opted in to wait mode** (see "Wait mode" below). Outside wait mode, report the outstanding state and stop; the user re-invokes the skill when ready. Inside wait mode, polling is permitted but bounded by the documented retry / interval / timeout caps and **never** silently in the background — every wait round produces a visible status line.
- **Never** treat the `automerge.yaml` workflow's `SUCCESS` conclusion as proof the merge happened. `pascalgn/automerge-action` exits 0 on `mergeResult: 'merge_failed'`. Always confirm `state == MERGED` on the PR itself (step 7a), and when the PR is still open with green checks, audit the action's logs for `merge_failed` (step 7b) before declaring the merge complete.
- **Never** delete the remote feature branch as part of the automatic merge flow. Post-merge branch cleanup is the platform's job via `delete_branch_on_merge: true`; a manual `gh api -X DELETE` call is only a one-off catch-up and requires explicit user confirmation.
- **Never** close a referenced tracking issue without explicit operator confirmation in the merging session. Issue closure is externally-visible and the operator may have closed the issue through another path; step 8 always lists the open candidates and waits for approval before invoking `gh issue close`.
- When `spec/project/pull-request-workflow/`, `spec/project/branching-model/`, or `spec/project/workflow-health/` disagrees with this skill, the spec wins. Propose a skill update rather than silently diverging.
