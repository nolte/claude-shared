# Automerge-workflow verification runbook

The step-7b audit for `pull-request-merge`, reached when step 7a leaves the PR `OPEN` with all required checks green and the `automerge` label applied. The most recent `automerge.yaml` run on the head SHA is suspect—treat its `SUCCESS` conclusion as unverified until the logs say otherwise, because `pascalgn/automerge-action` exits `0` even when its internal `mergeResult` is `merge_failed`.

## Surface the internal `mergeResult`

Run the following commands (execute, not read-as-reference) to pull the workflow's internal `mergeResult` out of the run logs:

```
RUN_ID=$(gh run list --workflow automerge.yaml --commit <head_sha> \
  --limit 1 --json databaseId --jq '.[0].databaseId')
JOB_ID=$(gh api repos/<owner>/<repo>/actions/runs/$RUN_ID/jobs \
  --jq '.jobs[0].id')
gh api repos/<owner>/<repo>/actions/jobs/$JOB_ID/logs \
  | grep -E "mergeResult: 'merge_failed'|Failed to merge PR" || true
```

## Classify a silent no-op

If the logs contain `mergeResult: 'merge_failed'` or `Failed to merge PR: …`, this is a **`workflow-health` incident, not a retryable label-apply**. Do not re-apply the `automerge` label and do not re-run the workflow blindly. Classify per `spec/project/workflow-health/<canonical_language>.md`; the common cause here is **`stale pin`**—the `uses:` tag in `.github/workflows/automerge.yaml` points to a `reusable-automerge.yaml` version that lacks the necessary override (typically `MERGE_METHOD: squash`). Surface the log excerpt and the bump target to the user, and hand off the pin bump as a separate PR per the workflow-health spec.
