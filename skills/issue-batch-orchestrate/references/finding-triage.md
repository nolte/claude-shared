# Finding triage and the per-member verification pass

Loaded by operation 5, after a member's result is recorded. It says what happens to a
finding that a reviewer, a verification pass, or a check raises against a member's change.

## The per-member verification pass

Before a dependent member starts, verify the member's slice with a context that didn't
produce the change: a read-only reviewer agent matched from the runtime catalog, or a
separate session. The member's row of the completeness matrix is the slice. Run it at
Tier 2 as well as Tier 3. A green gate on the member's own checks isn't this pass; the
pass exists because the author's context shares the author's blind spots.

Run the built-in review skills from a working copy that holds the change, and compare
their file list with `git diff --stat origin/develop...HEAD`; a clean report over an empty
diff is a failed pass.

## The triage

Every finding lands in exactly one of two outcomes.

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
