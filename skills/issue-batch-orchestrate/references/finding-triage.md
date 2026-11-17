# Finding triage and the per-member verification pass

Loaded by operation 5, after a member's result is recorded and before the bundle opens.
It says what happens to a finding that a reviewer, a verification pass, the
integration-branch diff review, or a check raises against the group's change.

## The per-member verification pass

Before a dependent member starts, verify the member's slice with a context that didn't
produce the change: a read-only reviewer agent matched from the runtime catalog, or a
separate session. The member's row of the completeness matrix is the slice. Run it at
Tier 2 as well as Tier 3. A green gate on the member's own checks isn't this pass; the
pass exists because the author's context shares the author's blind spots.

Run the built-in review skills from a working copy that holds the change, and compare
their file list with `git diff --stat origin/develop...HEAD`; a clean report over an empty
diff is a failed pass.

## The integration-branch diff review

After the per-member passes and the green `quality-gate` on the integration branch tip,
and before the bundle opens or a lane returns `committed-locally`, review the whole
group's diff once more: `git -C <worktree> diff origin/develop...HEAD` on the
integration branch, by a read-only agent that produced none of it, briefed for security
when the diff touches a security-sensitive path. With no pull request yet, only those
read-only lanes apply (no PR number for `code-review`). The lanes, the agent brief, and the
failed-gate rule are `pull-request-merge`'s `references/pre-merge-review.md`; don't
restate them here. The member passes don't replace this review: they each saw one slice,
and the bundle is what merges.

Record its source as `diff review @ <head-sha>` (the `git -C <worktree> rev-parse HEAD`
it covered), with a `no findings` row when it raised none, and carry the head SHA, the
`--stat` file list, the lanes, and the findings into the bundle's Risk / rollout notes
(as a lane: the returned payload). A finding fixed after the review adds a commit, so
review the new head again; only the bundle's `git rm` of `.audits/` artifacts may follow
the reviewed head, which `pull-request-merge`'s confirmation accepts.

## The triage

Every finding lands in exactly one of two outcomes. A single-issue run applies the same
triage shape (in scope, plan stays valid, reproduced) with its conditions scoped to the
issue, per `spec/project/issue-orchestration/` §"Verification and traceability"; the
spec carries each rule's exact wording.

**Fix directly**, recorded as a local adaptation, when **all three** hold:

| Condition | Test |
|---|---|
| (a) in scope | the finding lies in the member's files or the group's shared touch surface |
| (b) plan stays valid | fixing it needs no new matrix column and invalidates no admission predicate, the mode, or the ordering |
| (c) reproduced | the artifact can record a command with its actual output, or a `file:line` that shows it |

**Otherwise file it as its own issue**, referencing the group id, and name it in the
bundle's Risk / rollout notes. Never widen the bundle to carry it: that is the "unrelated
changes in one pull request" case the admission predicates exist to prevent.

A finding that is asserted but not reproduced is filed or dismissed together with the
observation that would settle it. It is never fixed on the reviewer's word alone: an
unreproduced finding that gets fixed adds a change nobody has shown to be needed.

## Recording

Add one row per finding to the group artifact's `## Findings` table:

| Finding | Source | Outcome | Reproduction | Issue |
|---|---|---|---|---|
| `SKILL.md:88` paging claim | pre-merge review | fixed directly | `gh issue list --help` shows only `--limit` | — |
| `<path>:<line>` claim a reviewer made | member verification pass | filed | `<command>` and its output | #nnn |

A directly fixed finding gets the same proving check the matrix demands of any change, run
and recorded with its actual output. The fix is committed on the integration branch like
any other member change; the authorisation of operation 5 already covers it, because
condition (b) guarantees it stays inside the approved plan.
