# Gotchas — issue-orchestrate

Per `spec/claude/skill-management/` §Gotchas — concrete corrections to non-obvious
environment facts the executing agent would otherwise get wrong.

- **An `infra` issue about a red workflow is not decomposed here.** A CI-failure
  issue is `workflow-health-triage`'s domain; decomposing it into work packages
  duplicates that skill's classification. Hand it over and stop.
- **A `question`-class issue produces no work packages.** Answering it and recording
  the answer is the whole job; manufacturing packages for a question is drift.
- **"Bounded" is about planning shape, not effort.** An issue that touches many files
  but is one coherent outcome with a single PR strand and no new roadmap item is
  bounded and implemented directly. An issue that spans two goal outcomes is *not*
  bounded even if each is small — it routes to the pipeline.
- **The pre-analysis artifact is the gate, not a by-product — and not a
  deliverable.** Skipping the write to "save a step" and dispatching from memory
  removes the reviewable hand-off contract; leaving it in place past the merge ships
  a process file to the default branch. It must exist and be approved before any
  dispatch, and be gone before the PR merges.
- **A specialist named in the artifact must come from the live catalog.** A package
  pointing at a renamed or removed specialist is a dispatch failure waiting to
  happen; re-resolve by `Glob` at dispatch time, not from a stale artifact name.
