# Group authorisation and the group requirement artifact

Loaded by operation 3 (when the plan gate is prepared) and operation 5 (when a member is
dispatched). It carries what the plan approval authorises, what it doesn't, what revokes
it, and how a class cluster is elicited once instead of once per member.

## The two gates

A group asks the operator for two confirmations before the merge, however many members it
has, plus one confirmation to close the member issues afterwards:

| Gate | What the operator approves | What it authorises |
|---|---|---|
| **Plan gate** | the group artifact: membership, mode, member order, completeness matrix | the dispatch of every member the artifact lists, in the recorded order |
| **Bundle gate** | the bundle pull request, opened from the integration branch tip | the pull request only; the merge stays with `pull-request-merge` |
| **Closure** | the set of open member issues, named | closing exactly those issues |

Before this rule a group asked `4 + 2n` times. A member dispatch, the package dispatches
inside it, and the mode decision no longer ask on their own; the artifact records the mode
and the approval covers it.

## What the authorisation covers

The artifact records `authorised_by: <group-id>/plan-approval`. The hand-off to
`issue-orchestrate` carries it, and the delegated run records it as its decision for:

- the member dispatch and each package-boundary dispatch inside the member's run
- the member's decomposition approval, while the decomposition stays inside the member's
  row of the completeness matrix
- the classification confirmation, for every member **not** classified `security`

## What it doesn't cover

- the classification confirmation of a `security` member: misclassification costs most
  there, so that member still asks once
- any change outside the member's matrix row: that is a **structural regression**, the
  run stops and reports back instead of dispatching
- a pull request or a merge: the delegated run never opens one
- issue comments: a group-delegated run posts none, so there is nothing to authorise; the
  closure comments of operation 7 carry the trail

## What revokes it

A structural regression (an admission predicate, the mode, or the ordering is invalidated,
or a member's work leaves its matrix row) revokes the authorisation for every member not
yet dispatched. Re-approval of the recomputed artifact renews it. A local adaptation leaves
it in force. A dropped member is removed from the artifact; the remaining members keep the
authorisation they were approved under.

## The group requirement artifact (class cluster only)

A class cluster is several issues of one defect class: one logical change, so one
requirement. Eliciting it per member runs `requirements-elicit` `n` times for one thing.

1. After the structural analysis (operation 2) and before the plan gate, dispatch
   `requirements-elicit` once for the group's single logical change. The artifact lands
   under `project/requirements/<slug>.md` per `spec/project/requirements-elicitation/` §G.
2. Record its path and `U_gate` in the group artifact. The plan gate then approves the
   requirement together with the plan.
3. Pass the path to each delegated run as `requirement_artifact`. The run **re-checks**
   coverage: each of the member's acceptance conditions traces to a requirement in the
   artifact, and `U_gate` meets `τ_high`. A covered member isn't elicited again.
4. A member whose issue states a requirement the artifact doesn't cover falls back to its
   own elicitation. Record in the group artifact which members were covered and which fell
   back, and for each fallback the requirement it added.

A symptom cluster keeps per-member elicitation, because its members can state different
requirements around one cause. The exception: when the root cause the plan targets *is* the
single requirement, one artifact for that cause serves the group, recorded the same way.

The dispatch count is then checkable: one for the group, plus one per fallback member.
