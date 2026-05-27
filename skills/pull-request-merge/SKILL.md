---
name: pull-request-merge
description: Promote an open draft pull request on the current branch to a merged state on `develop`, applying repository-declared labels and passing every gate from the pull-request-workflow spec. Invoke when the user asks to promote the draft PR, ship the PR, merge the draft, or bring the PR over the finish line. Also handles equivalent German-language requests. Delegates pre-merge review to the `review` skill (and `security-review` when the diff touches security-sensitive paths), derives labels from the Conventional-Commits type and touched paths, flips draft → ready, triggers automerge by applying the `automerge` label so the repository's automerge workflow squash-merges the PR once every required check is green, and verifies the merge commit landed on `develop`. Supports resume on re-invocation per `spec/claude/resumable-work/`.
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
examples:
  - prompt: "Merge the open PR"
    outcome: "Ready PR squash-merged onto develop; merge commit verified."
resumable: true
---

# Pull Request Merge

Promotes an open draft pull request (typically the one opened by `pull-request-create`) to a merged state on `develop`. This skill is the counterpart to `pull-request-create`: that skill opens the PR; this skill lands it. It honors `spec/project/pull-request-workflow/<canonical_language>.md`, `spec/project/branching-model/<canonical_language>.md`, and `spec/project/workflow-health/<canonical_language>.md` end-to-end: `enforce_admins: true` is respected, `--squash` is the only merge strategy, and failing required checks route to workflow-health triage rather than to a waiver.

## Why this is a skill, not an agent

- **Externally-visible mutations gate on user confirmation** — flipping draft → ready, applying the `automerge` label, and (in the fallback path) calling `gh pr merge --squash --auto` all act on a shared GitHub PR; mid-flow user gating is core to the contract and would be lost in an agent's fire-and-forget shape.
- **Orchestrator that chains other skills** — this skill dispatches `review` and (conditionally) `security-review` mid-flow, then conditionally hands off to `workflow-health` triage on failure; the skill-orchestrates pattern (per `skill-vs-agent`) defaults the orchestrator to skill form.
- **Wait mode requires visible status updates per round** — bounded polling for required-check completion has a hard "every wait round produces a visible status line" rule, which only works inside a skill that stays in the main conversation.
- Counter-dimension considered: a tool-restricted agent (read + a single `gh` Bash) could perform the verification half (steps 1, 4, 7) cleanly, but the externally-visible-mutation half (steps 5, 6) needs the user in the loop — keeping the whole flow in one skill is simpler than a forced split.

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
  - paths under `.github/workflows/` or `.github/settings.yml` → candidates `cicd`
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
- **At least one pending** → default behavior is to report the pending checks and stop; the user reruns the skill once checks complete. When the user opts in to **wait mode** (see "Wait mode" below), re-check the same `gh pr checks` call at the configured interval (≥60s) until every required check is green or the configured wall-clock timeout (≤15min) is reached. On timeout, stop and report the still-pending checks just like the default path. **Polling is permitted only inside wait mode**; outside wait mode, the no-poll rule still applies.
- **At least one failed** → don't flip draft and don't merge, even in wait mode. Hand off to the `workflow-health` triage flow documented in `spec/project/workflow-health/<canonical_language>.md`: classify the failure (`defect` / `flake` / `infra` / `stale pin` / `secret drift` / `other`) and route the fix through a separate PR. Never retry the merge by re-running failed checks blindly—that's drift per the workflow-health spec.

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

If `state == MERGED` and `mergeCommit.oid` appears on `origin/develop`, report back and proceed to step 8. If `state == OPEN` and at least one required check is still running, the default behavior is to report the outstanding checks and stop—the merge will complete automatically once `pascalgn/automerge-action` sees green required checks. When the user opts in to **wait mode** (see "Wait mode" below), re-check `gh pr view --json state,mergedAt,mergeCommit` at the configured interval (≥60s) until `state == MERGED` or the configured wall-clock timeout (≤15min) is reached. On timeout, stop and report the still-`OPEN` state plus the most recent `gh pr checks` snapshot.

**7b. Audit the automerge workflow when the PR is `OPEN` with all required checks green and the `automerge` label applied.** The most recent `automerge.yaml` run on the head SHA is suspect—treat its `SUCCESS` conclusion as unverified until the logs say otherwise. Run the following commands (execute, not read-as-reference) to surface the workflow's internal `mergeResult`:

```
RUN_ID=$(gh run list --workflow automerge.yaml --commit <head_sha> \
  --limit 1 --json databaseId --jq '.[0].databaseId')
JOB_ID=$(gh api repos/<owner>/<repo>/actions/runs/$RUN_ID/jobs \
  --jq '.jobs[0].id')
gh api repos/<owner>/<repo>/actions/jobs/$JOB_ID/logs \
  | grep -E "mergeResult: 'merge_failed'|Failed to merge PR" || true
```

If the logs contain `mergeResult: 'merge_failed'` or `Failed to merge PR: …`, this is a **`workflow-health` incident, not a retryable label-apply**. Do not re-apply the `automerge` label and do not re-run the workflow blindly. Classify per `spec/project/workflow-health/<canonical_language>.md`; the common cause here is **`stale pin`**—the `uses:` tag in `.github/workflows/automerge.yaml` points to a `reusable-automerge.yaml` version that lacks the necessary override (typically `MERGE_METHOD: squash`). Surface the log excerpt and the bump target to the user, and hand off the pin bump as a separate PR per the workflow-health spec.

Report back: PR URL, merged-at timestamp, merge commit SHA on `origin/develop`, the labels that were applied, and—if 7b caught a silent no-op—the workflow-health classification and the remediation the user needs to take next.

### 7c. Close referenced tracking issues

GitHub's `Closes #<n>` / `Fixes #<n>` / `Resolves #<n>` autolinks fire only on default-branch merges. Per `spec/project/pull-request-workflow/<canonical_language>.md` §"Linked-issue closure on develop merge", a squash-merge into `develop` leaves referenced tracking issues `OPEN`; this step closes them with operator confirmation rather than waiting for the next `release-cd-refresh-master.yml` fast-forward of `main`.

Run only when step 7a confirmed `state == MERGED`. If the PR body carries no closing-keyword references, skip this step.

1. Scan the PR body for closing-keyword references — case-insensitive `(?:close|closes|closed|fix|fixes|fixed|resolve|resolves|resolved)\s+#(\d+)`. Deduplicate by issue number. `Refs #<n>` is **not** a closing keyword and is ignored on purpose.

2. For each referenced issue, read its current state:

   ```
   gh issue view <n> --json state,title --jq .
   ```

   Skip when `state == CLOSED` — the autolink may have fired (for example because `main` was fast-forwarded between the merge and this step), or another path closed it already.

3. Present the remaining `OPEN` list to the operator, one line per issue (`#<n> <title>`), and require explicit confirmation before any close call. The operator **MAY** select all, a subset, or none.

4. For each confirmed issue, close with a cross-reference comment that names the merging PR and the merge-commit SHA on `develop`:

   ```
   gh issue close <n> --reason completed --comment "Resolved by #<pr> (merged to \`develop\` as \`<merge_sha>\`). The \`Closes #<n>\` autolink fires only on default-branch merges; this repo's default is \`main\`, fast-forwarded from \`develop\` via \`release-cd-refresh-master\` — closing manually now rather than waiting for that promotion."
   ```

Report back which issues were closed, which were skipped because they were already closed, and which the operator declined.

### 8. Clean up local state

Once the PR is merged, offer (don't automatically execute) the following cleanup to the user:

- `git checkout develop && git pull --ff-only`: update the local integration branch
- `git branch -d <feature-branch>`: delete the local feature branch (safe delete; refuses to remove a branch whose commits aren't on `develop`)

The remote feature branch is handled by the platform per `spec/project/pull-request-workflow/<canonical_language>.md` §Post-merge branch cleanup: `delete_branch_on_merge: true` in `.github/settings.yml` (directly or via the `nolte/gh-plumbing` commons extension) lets GitHub remove it automatically right after the squash-merge. Confirm this in step 7 by checking that the remote branch is gone: `gh api repos/<owner>/<repo>/git/refs/heads/<feature-branch>` returns `404`. If the branch is still there, the platform setting is either missing or was enabled only later; in that one-off catch-up case, offer the manual REST call and only act with explicit user confirmation:

```
gh api -X DELETE repos/<owner>/<repo>/git/refs/heads/<feature-branch>
```

Never run `git push origin --delete …` or `gh api -X DELETE` without explicit user confirmation. Never make remote-branch deletion part of the automatic merge flow—the platform setting is the routine path, manual deletion is only a catch-up.

## Wait mode

The skill is single-shot by default: when step 4 finds pending checks or step 7a finds the PR still `OPEN`, the skill reports and stops; the user re-invokes once GitHub is in the next state. **Wait mode** is an opt-in that lets the skill wait for state transitions inside a single invocation, bounded by hard caps (interval ≥60s, wall-clock ≤15 min, ≤10 retries per wait point, visible status line per round, failure short-circuits to workflow-health). Read `references/wait-mode.md` when the user opts in via `--wait` or an unambiguous "wait until X" instruction in the prompt — the reference covers activation, every cap with its rationale, the per-step implementation pattern (step 4 vs. step 7a), and the prompt-cache trade-off that justifies the bounds.

## Examples

- Read `examples/01-clean-merge-via-automerge-label.md` when promoting a ready PR through the automerge label on the first end-to-end run.
- Read `examples/02-pending-checks-reports-and-stops.md` when required checks are still pending and the skill reports state instead of proceeding.
- Read `examples/03-wait-mode-with-explicit-flag.md` when the user opts into wait mode via `--wait` and you need to see the polling loop behaviour.

## Gotchas

- **`automerge` label must be spelled exactly**: the label name `automerge` is case-sensitive and must already exist in the repository's label set; applying a near-miss (`auto-merge`, `AutoMerge`) creates a new label silently or fails — always verify the label exists via the `gh label list` call in step 1 before applying it.
- **`automerge.yaml` `SUCCESS` does not mean the merge happened**: `pascalgn/automerge-action` exits 0 even on `mergeResult: 'merge_failed'`; always confirm `state == MERGED` via `gh pr view` (step 7a) and, when the PR stays `OPEN` with green checks, audit the workflow logs for `merge_failed` (step 7b) before declaring completion.
- **Required checks list is read from `.github/settings.yml`, not from the GitHub UI**: the UI shows all checks; the spec gates only on checks declared as required in `.github/settings.yml` (directly or via the `nolte/gh-plumbing` commons extension) — use that file as the authoritative source when deciding whether all required checks are green.
- **`Closes #N` autolinks don't fire on `develop` merges**: GitHub's reference-closing keywords (`Closes`, `Fixes`, `Resolves`) fire only when the merge lands on the repository's default branch. Under this branching model the default is `main`, but PRs target `develop`; referenced issues therefore stay `OPEN` after a `develop` squash-merge and close only when `release-cd-refresh-master.yml` fast-forwards `main`. Step 7c closes them manually with operator confirmation rather than waiting for the promotion.

## Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/pull-request-merge/<run-id>.yml` after every successful user-approval gate and after each named phase boundary. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope (`schema_version`, `run_id`, `inputs`, `phase`, `decisions[]`, `status`, ...) and the fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

## Hard rules

- **Never** flip a draft to ready while any required check is pending or failing. Failures route to the `workflow-health` triage flow, not to a waiver.
- **Never** pass `--admin` to `gh pr merge`. `enforce_admins: true` on `develop` has no exception path.
- **Never** use a merge strategy other than `--squash`. Squash-merge is mandated by the `pull-request-workflow` spec.
- **Never** create a new GitHub label from this skill. Label candidates that don't exist in the repository are reported as a gap, not silently added.
- **Never** skip the `review` skill delegation. A final review is the cheapest pre-merge gate; only an explicit user override bypasses it.
- **Never** rebase or merge `develop` into the feature branch silently to fix a lag. Branch-freshness gaps return control to the user, consistent with `pull-request-create`.
- **Never** poll, sleep, or loop waiting for checks to complete **unless the user has opted in to wait mode** (see "Wait mode" below). Outside wait mode, report the outstanding state and stop; the user re-invokes the skill when ready. Inside wait mode, polling is permitted but bounded by the documented retry / interval / timeout caps and **never** silently in the background — every wait round produces a visible status line.
- **Never** treat the `automerge.yaml` workflow's `SUCCESS` conclusion as proof the merge happened. `pascalgn/automerge-action` exits 0 on `mergeResult: 'merge_failed'`. Always confirm `state == MERGED` on the PR itself (step 7a), and when the PR is still open with green checks, audit the action's logs for `merge_failed` (step 7b) before declaring the merge complete.
- **Never** delete the remote feature branch as part of the automatic merge flow. Post-merge branch cleanup is the platform's job via `delete_branch_on_merge: true`; a manual `gh api -X DELETE` call is only a one-off catch-up and requires explicit user confirmation.
- **Never** close a referenced tracking issue without explicit operator confirmation in the merging session. Issue closure is externally-visible and the operator may have closed the issue through another path; step 7c always lists the open candidates and waits for approval before invoking `gh issue close`.
- When `spec/project/pull-request-workflow/`, `spec/project/branching-model/`, or `spec/project/workflow-health/` disagrees with this skill, the spec wins. Propose a skill update rather than silently diverging.
