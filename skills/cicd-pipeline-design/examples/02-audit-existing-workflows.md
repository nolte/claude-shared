# Example 02 — `audit` an existing pipeline

## Input prompt

> "Prüf mal unsere Workflows durch, bevor wir das Release rausgeben."

## Input state

`.github/workflows/ci.yml` containing, among other things:

```yaml
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: tj-actions/changed-files@v44
      - run: echo "Title: ${{ github.event.pull_request.title }}"
      - uses: actions/cache@v4
        with:
          key: deps
      - run: pytest || true
```

## Expected behaviour

1. Dispatches `cicd-pipeline-reviewer` for detection rather than sweeping the tree inline.
2. Applies severity and reports, most severe first:
   - **Critical** — `tj-actions/changed-files@v44` and `actions/checkout@v4` are tag references, not commit digests (`github-actions-best-practices` §A). Names the March 2025 incident as the reason tags aren't immutable.
   - **Critical** — the pull-request title is interpolated straight into a `run` script (§C). Remedy: bind it to an intermediate environment variable.
   - **Critical** — `pytest || true` means the test stage can't fail (`continuous-integration` §B, §E).
   - **Critical** — no `permissions` block, so the job inherits the repository default (§B).
   - **Warning** — cache key `deps` carries none of the content that determines the cached data, so it can never invalidate (`continuous-integration` §D, `github-actions-best-practices` §G).
   - **Warning** — no concurrency group, so superseded runs race (§F).
3. Offers to fix the mechanical ones as individually-approved diffs: the digest pins, the `permissions` block, the cache key, the concurrency group.
4. Does **not** silently fix `pytest || true`; removing the escape changes what the gate reports, so it's shown as its own diff with the consequence stated.

## What would be wrong

- Reporting the runtime of the pipeline as a finding. Efficiency is a guide, not a gate.
- Reporting that `release-drafter.yml` is missing — that belongs to `branching-model` and `project-structure-apply`.
- Triaging a red run rather than the workflow definition; that's `workflow-health-triage`.
