# Running under a group process

Loaded when `issue-batch-orchestrate` delegates this run and passes `authorised_by`, or
`requirement_artifact`, or both. A run started without them follows the body unchanged.

Authority: `spec/project/issue-batch-integration/` §F and this skill's own spec,
`spec/project/issue-orchestration/` §"Resumption and operator gating" and §"Issue
acquisition and comprehension".

## `authorised_by: <group-id>/plan-approval`

The group's operator approval already covered this member, so the run records the
reference as its decision instead of asking, for:

- the member dispatch and each package-boundary dispatch (operation 5)
- the decomposition approval (operation 3), **while** the decomposition stays inside the
  member's row of the group's completeness matrix
- the classification confirmation (operation 2), unless the class is `security`

It never covers a change outside that row, a pull request, or a merge. A group-delegated
run posts no issue comment at all; the group's closure comments carry the trail.

Resolve the reference before trusting it: the group artifact at
`.audits/issue-batch-integration/<group-id>/analysis.md` in the group's working copy must
exist, carry the plan approval, and list this member. A reference that doesn't resolve is
no authorisation, and the run asks as it would without one.

When the decomposition leaves the member's matrix row, don't dispatch. That is a structural
regression of the group, so report it back with the files that fell outside the row and
stop; the group returns to its plan and renews or withholds the authorisation.

## `requirement_artifact: project/requirements/<slug>.md`

The group elicited one requirement for its single logical change. Meet the requirements
gate by **re-checking**, not by trusting:

1. every acceptance condition of this issue traces to a requirement in the artifact
2. the artifact's `U_gate` meets `τ_high`

Covered: record the coverage check in the pre-analysis artifact and don't elicit again.
Not covered, because the issue states a requirement the artifact lacks: dispatch
`requirements-elicit` for this issue alone, and report back which requirement it added so
the group artifact can record the fallback.

## Checkpoint

Record `authorised_by` and, where present, the coverage check as the decision entries for
the confirmations this run didn't ask. A run that asked for something the reference covers
is a defect in the run.
