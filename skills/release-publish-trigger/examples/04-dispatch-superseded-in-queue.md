# Example 04: the dispatch is superseded in the queue

Every gate passed and the dispatch landed, but the run never executed. This is the path
that used to be reported as a success.

## Transcript shape

```
$ gh workflow run release-publish.yml --ref develop -f tag=v0.1.12
✓ Created workflow_dispatch event for release-publish.yml at develop

$ gh run list --workflow=release-publish.yml --limit 1 \
    --json databaseId,status,conclusion,url,headSha
[{"databaseId":17442119883,"status":"queued","conclusion":null,
  "url":"https://github.com/nolte/claude-shared/actions/runs/17442119883",
  "headSha":"8baa835…"}]
```

`queued`, not `in_progress`. The run is holding for the `release-draft` lane, so the
skill keeps checking rather than reporting.

```
[round 1, +90s]  status=queued       still waiting for the release-draft lane
[round 2, +180s] status=cancelled    conclusion=cancelled
```

## What the skill reports

> **The publish did not happen. The dispatch was superseded.**
>
> Run 17442119883 was cancelled while still queued, without executing. It was waiting
> for the `release-draft` concurrency lane, and a newer `release-drafter` run queued
> into the same lane and displaced it. A merge to `develop` is what triggers that.
>
> This is **not** a workflow failure: there's no red check, and `workflow-health`
> triage would find nothing.
>
> **Next action: re-dispatch.** Operation 3 runs again first, because `develop` has
> moved by definition — the merge that superseded this run is on it.
>
> Release `v0.1.12` is still a draft. Verified: `gh release view v0.1.12 --json isDraft`
> returns `{"isDraft": true}`.

## What must not happen

- Reporting the run URL and stopping. `gh workflow run` exited zero and the run URL is
  real, but nothing was published.
- Routing to `workflow-health`. A cancellation under a shared lane isn't a defect in
  the workflow.
- Re-dispatching without re-running the gates. The gates are derived from live state.

## The neighbouring case

If the caps run out while the run is still `queued`, the report says **unresolved**,
not superseded and not successful: the run hasn't started, it can still be superseded,
and here's the URL. Reporting an unresolved dispatch as a success is the same defect in
a different costume.

Mechanism: `references/supersession.md`.
