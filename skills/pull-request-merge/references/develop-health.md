# Develop health pre-flight

Read before a lane is handed on, a branch is promoted, or a pull request is merged. Rule owner: `spec/project/pull-request-workflow/` §"Serial pull-request flow"; classification belongs to `spec/project/workflow-health/`. One procedure, three callers, each pointing here:

| Caller | Where it runs |
|---|---|
| `pull-request-merge` | step 1, before the step 2 review |
| `backlog-delivery-orchestrate` | before each lane round (operation 3) and in each merge-train turn before the bot drain and before each promotion (`references/merge-train.md`) |
| `issue-backlog-partition` | operation 6, before each group or single is handed on as a lane |

`develop` is the base every lane rebases onto and every pull request is tested against. A red `develop` otherwise surfaces as a red check on the next pull request and is blamed on it.

## Read

1. List the active workflows: `gh workflow list --json id,name,path,state` (disabled workflows are out of scope).
2. For each, read its recent `develop` runs:

   ```bash
   gh run list --branch develop --workflow <id> --limit 20 \
     --json databaseId,event,status,conclusion,headSha,createdAt,url
   ```

   Keep only runs whose `event` is `push`, `schedule`, or `workflow_dispatch`: those build or test `develop` itself. Event-driven automation that GitHub also files under `develop` (`check_suite`, `issues`, `issue_comment`, `workflow_run`) says nothing about the code and is dropped. A workflow with no remaining run doesn't run on `develop` and is out of scope; every other workflow counts, **required or not**.
3. The **verdict run** is the newest run with `status: completed` and a verdict conclusion:
   - `success` → green
   - `failure`, `timed_out`, `startup_failure` → red
   - `cancelled`, `skipped`, `neutral`, `stale`, `action_required` → no verdict: a cancelled run is usually superseded by a newer push, so walk back to the next run
4. A newer run still `queued` or `in_progress` doesn't replace the verdict: a red verdict stays red until a newer run completes green, so a fix in flight is reported with its run id and the gate still stops.
5. No verdict run among the 20 → report the workflow as `no-verdict` with the run ids; it doesn't stop the gate on its own, and a majority of cancelled runs is the lane-level case of `workflow-health-triage` operation 1.

Report one line per workflow: workflow, verdict run id, event, `headSha`, conclusion, verdict. Re-read on every invocation and every resume; a recorded result is never reused.

## Red: stop

When any verdict is red, a non-required workflow included:

- stop before the next lane, promotion, or merge, and leave every branch and pull request as it is;
- hand each red run to `workflow-health-triage`, naming its run id or URL; it compares the first red run with the last green one and treats a recurring failure as a defect;
- report the red runs and the triage's result.

"Not required" isn't a pass: a red end-to-end or VM test on `develop` that nothing requires is exactly what lets a broken base reach the next pull request.

## Override

A lane or merge continues past a red `develop` only on an explicit operator override, given for the named run in the current session. Record it in the run's checkpoint under `decisions:` before continuing:

```yaml
- gate: develop-health
  run_id: 19283746        # the red verdict run
  workflow: .github/workflows/vm-tests.yml
  head_sha: c7ce51a
  reason: "known base-image regression, tracked in its own issue; unrelated to the lanes"
  decided_at: 2026-11-17T09:12:00Z
```

- An override covers that run id only. A newer red run of the same or another workflow needs its own.
- The pull request that fixes the red run is the expected override case: the gate stops it too, and the operator overrides it naming the red run it repairs, and the override records that run id.
- A standing authorisation, a partition approval, or a plan approval never covers it.
- A skill invoked by an orchestrated run (`pull-request-merge` under `backlog-delivery-orchestrate`) honours an override the caller recorded for the same run id; the caller names it in its brief.
- Under an override, `pull-request-merge` step 4 still classifies a red check on the head; the same check red in the overridden `develop` run is the evidence that it isn't the pull request's own.
