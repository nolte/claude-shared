# Why a landed dispatch proves nothing

Read this when operation 6 reports a `cancelled` run, an unresolved dispatch, or when
someone proposes splitting the shared concurrency lane.
`spec/project/release-skill-layer/` §Skill B owns the rules; this file carries the
mechanism.

## The shared lane, and why it is correct

`release-publish.yml` and `release-drafter.yml` declare the same literal concurrency
group, `release-draft`. That is deliberate. `reusable-release-publish.yml` sets the
release's `target_commitish` well before it flips `draft: false`, and a drafter run
landing inside that window can move the target. The result would be a tag cut from a
commit the publish never verified against its gates.

**Don't split the lane to buy visibility.** The race it prevents is worse than the
cost it imposes, and the cost is now handled by following the run instead.

## The cost the lane imposes

`release-drafter.yml` fires on `push` to `develop`. So:

1. The operator dispatches `release-publish.yml`. `gh workflow run` exits zero.
2. The run goes **pending**, because a drafter run holds the lane.
3. Someone merges to `develop`. A new drafter run queues into the same group.
4. GitHub supersedes the **pending** publish run. It ends `cancelled`, having never
   executed.

The release doesn't happen. Step 1 already reported success. The window is every merge
to `develop`.

## The distinction that keeps being misread

`cancel-in-progress: false` does **not** prevent this. GitHub supersedes a *pending*
run regardless of that flag; the flag governs only whether an already *running* run is
cancelled. This was corrected twice during the review rounds of #554, so treat it as
load-bearing rather than a detail.

The useful consequence: **a run that has reached `in_progress` can no longer be
superseded** while `cancel-in-progress` stays false. That is why operation 6 follows
the run only until it leaves the queue, rather than to completion. Leaving the queue is
the point where a single-shot report becomes honest, and waiting for completion would
cost far more for no additional safety.

## Reporting a superseded run

A `cancelled` conclusion is distinguishable from a `failure`, and the two need
different reports:

| Conclusion | What it means | Next action |
|---|---|---|
| `cancelled` | superseded in the queue; nothing ran | re-run the gates, then re-dispatch |
| `failure` | the workflow ran and failed | `workflow-health` triage, no blind retry |

Routing a `cancelled` run to `workflow-health` sends the operator to look for a red
check that doesn't exist. Say "superseded, re-dispatch" instead.

Re-run operation 3 before re-dispatching: every gate is derived from live state, and
`develop` has moved by definition, since a merge to `develop` is what superseded the
run in the first place.
