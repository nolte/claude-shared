# Finding triage in a single-issue run

Loaded by operation 5 before the first dispatch, and by operation 6 whenever a reviewer,
a verification pass, the class sweep, or a specialist's result raises a finding beside
the issue's own work packages. The rule is `spec/project/issue-orchestration/`
§"Verification and traceability"; this file says how the orchestrator applies it. It's
the same triage `issue-batch-orchestrate` runs per member
(`spec/project/issue-batch-integration/` §F), scoped to one issue. When the two disagree,
the spec wins.

## The two outcomes

Every finding lands in exactly one outcome.

**Fix directly** in the same change when **all three** hold:

| Condition | Test |
|---|---|
| (a) in scope | the finding lies in the files or artifacts the issue's work packages touch, or it's a same-pattern sibling of the defect the run fixes |
| (b) plan stays valid | fixing it needs no operator decision and leaves the bounded scope, the route, and the approved decomposition valid |
| (c) reproduced | the run records a command with its actual output, or a `file:line` that shows it, per `spec/claude/claim-provenance/` |

**Otherwise file it as its own issue** and reference it in the pull request's
**Risk / rollout notes**.

Filing a reproduced finding that meets (a) to (c) is the wrong outcome, not the cautious
one. Each such issue later costs a partition row, a lane, a pull request, and a close for
a change this run could have carried.

A finding that's **asserted but not reproduced** is filed or dismissed together with the
observation that would settle it. Never fix it on a reviewer's word alone: a fix nobody
has shown to be needed is a change without evidence.

## Who makes the fix

The fix is part of the package whose touched files it lies in, so the specialist that
owns that package makes it. The dispatch brief already authorises it (next section), and
condition (b) keeps it inside the approved decomposition, so it needs no new package and
no new confirmation. A finding raised after the package returned goes back to the same
specialist with the finding and its reproduction. A same-pattern sibling outside every
package's touched files goes to the specialist of the package that fixed the defect, and
the artifact adds the file to that package's touched files; that keeps the approved
decomposition valid, because the package's problem statement already covers the class.
The generalist fixes it only where the package itself had no matching specialist.

## Under group delegation

When `issue-batch-orchestrate` delegates the run (`references/group-delegation.md`), the
group rule governs instead: `spec/project/issue-batch-integration/` §F conditions (a) and
(b) bind, so the fix stays inside the member's matrix row. A sibling outside that row is
reported back to the group run, never fixed here, and a filed issue references the group
id. The delegated run has no pull request of its own; its findings go into its result.

## The dispatch-brief clause

Every brief carries this clause beside the refutation clause of
`spec/claude/dispatch-brief/`:

> Fix small related findings that meet conditions (a) to (c) directly, and list each
> one in your result with its reproduction (the command and its actual output, or the
> `file:line`). List anything else unfixed, with why it fails (a), (b), or (c).

Without the clause a specialist reads its package as a fence and returns findings as a
list, and each listed item turns into an issue nobody needed.

## The class-sweep remainder

On a `fix` run, when `Repaired` is less than `Hits`, triage the remaining sites the same
way: repair in this change every site that meets (a) to (c) and count it in `Repaired`.
Where no guard holds what's left, file those sites as their own issues and reference them
under the four `## Class sweep` fields before the run closes.

A guard that fits the change belongs in it already, per G1 of
`spec/project/defect-class-guards/`. Only a **guard too large for the change** stays its
own issue, referenced from the closing one.

## Recording

Add one row per finding to the pre-analysis artifact's `## Findings` table:

| Finding | Source | Outcome | Reproduction | Issue |
|---|---|---|---|---|
| stale comment at `<path>:<line>` | specialist result | fixed directly | `<command>` and its output | none |
| sibling call site at `<path>:<line>` | class sweep | filed | `<command>` and its output | #nnn |

The pull request lists each directly fixed finding under **Changes** with its
reproduction, and references each filed one in **Risk / rollout notes**. The artifact is
removed at closeout, so the pull request carries the record that survives the merge. A
filed issue resting on this run's measurement waits for the green gate; see
§"Externally-visible artefacts wait for the gate" in `references/measurement-discipline.md`.

## As a lane

A lane applies the same triage. It fixes what meets (a) to (c) in its own branch and
files the rest as new issues. Those issues don't join the running partition; a later
survey picks them up.
