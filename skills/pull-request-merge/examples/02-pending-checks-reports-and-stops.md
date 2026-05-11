# Example 02 — Pending checks, no wait mode → skill reports and stops

Default single-shot path: required checks on the PR are still
running, the user has **not** opted in to wait mode, so the skill
must report the pending state and stop. No draft flip, no label
apply, no polling. The user re-invokes the skill once GitHub
reports green.

## Input prompt

> Bring the draft PR over the finish line.

(Note: no `--wait` argument; no "wait until checks pass" phrasing.
Default single-shot behavior wins.)

## Input files

Repository state assumed by the harness when this prompt fires:

- Current branch: `fix/release-notes-marker-drift` (not `develop`,
  not `main`).
- Working tree: clean.
- `gh auth status`: authenticated.
- One open PR is associated with the current branch:
  - `state: OPEN`, `isDraft: true`, `baseRefName: develop`.
  - `title: fix(release-notes): correct stale marker on rerun`.
  - `mergeable: MERGEABLE`, `mergeStateStatus: BLOCKED` (blocked
    by both the draft flag and pending checks).
  - Touched paths: `skills/release-notes-curate/SKILL.md`,
    `skills/release-notes-curate/references/markers.md`.
- Feature branch contains `origin/develop`'s tip.
- `gh pr checks` reports a mixed status:
  - `lint`: `bucket: pass` / `state: SUCCESS`.
  - `markdownlint`: `bucket: pass` / `state: SUCCESS`.
  - `commitlint`: `bucket: pass` / `state: SUCCESS`.
  - `test`: `bucket: pending` / `state: IN_PROGRESS`.
  - `docs-build`: `bucket: pending` / `state: QUEUED`.
- `gh label list` includes `type:fix`, `area:skill`, and
  `automerge`.
- Repository ships `.github/workflows/automerge.yaml` and the
  `automerge` label (so the primary path would apply when checks
  eventually go green — but only on a future invocation).

## Expected behaviour

1. **Preconditions pass silently.** Branch ≠ `develop`/`main`,
   clean tree, authenticated `gh`, freshness check passes.
2. **Step 1 inspection runs in parallel.** The skill notes the
   mixed check-bucket result up front: 3 green, 2 pending, 0
   failed.
3. **Step 2 delegates to `review`.** No security-sensitive paths
   are touched, so `security-review` is **not** invoked. The
   `review` skill returns no blocking findings — but this still
   doesn't unlock anything downstream because step 4 will gate.
4. **Step 3 is deferred (not executed).** The skill does **not**
   apply labels yet, because step 4 is going to stop the run and
   re-invocation will repeat step 1 anyway. (Equivalently: even if
   the implementation applies labels first, step 4 still gates the
   draft flip.) The example treats the conservative
   defer-until-green ordering as the expected behavior.
5. **Step 4 detects pending checks.** `gh pr checks <number>`
   confirms `test` and `docs-build` are still running. Decision
   tree:
   - At least one **pending**, zero **failed**.
   - User has **not** opted in to wait mode (no `--wait` flag, no
     unambiguous "wait until X" instruction in the prompt).
   - Therefore: **report and stop**. No polling, no sleep, no
     loop.
6. **Steps 5, 6, 7, 8 do NOT run.** Specifically:
   - The skill does **not** call `gh pr ready <number>` (draft
     stays draft).
   - The skill does **not** apply the `automerge` label.
   - The skill does **not** call `gh pr merge --squash --auto`.
   - The skill does **not** offer local cleanup (nothing has
     merged).
7. **Final report (in German per global user-language policy)**
   contains:
   - The PR URL, number, title, and current draft + mergeable
     state.
   - The full check rollup with each check's name and bucket
     (`SUCCESS` / `IN_PROGRESS` / `QUEUED`), so the user can see
     which checks are blocking.
   - An explicit "no wait mode active — re-invoke this skill once
     all required checks report SUCCESS" instruction.
   - A pointer to wait mode as an opt-in for next time
     (`--wait` flag or an unambiguous "wait until checks pass"
     instruction in the prompt) with the hard caps cited
     verbatim: interval ≥60s, wall-clock ≤15min, ≤10 retries,
     visible status line per round.
   - No workflow-health classification is attached because
     nothing failed — only pending checks.

Hard-rule compliance to verify in this scenario:

- The skill did **not** flip draft → ready while a required
  check was pending.
- The skill did **not** poll, sleep, or loop waiting for checks
  outside wait mode.
- The skill did **not** apply the `automerge` label on a pending
  head commit.
- No workflow-health route was triggered, because the failure
  mode here is "pending", not "failed".
- The skill did **not** silently retry the merge by re-running
  pending checks.
