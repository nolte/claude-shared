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
- **A claim read from a mutable ref is a snapshot, not a state.** `gh api
  …/contents/<path>?ref=master`, `git show develop:<path>`, or a registry `latest`
  answers for the moment it ran. Two such reads minutes apart can disagree, and two
  fields quoted from one read can silently come from different revisions if the read
  is repeated. Resolve the ref to a SHA or digest and re-read at it before the value
  becomes load-bearing, per `spec/claude/claim-provenance/` §B.
- **The harness built-ins inspect the session's working directory, not the
  orchestration worktree.** `security-review` and the diff-scoped review skills
  resolve "the current branch" from where the session started — the primary checkout,
  still on `develop`. Invoked from an orchestration whose work lives in a worktree,
  they see an empty diff and report no findings, which reads exactly like a clean
  pass. Check the reported branch and file list before believing the verdict, and
  scope the review explicitly when they disagree with the worktree.
