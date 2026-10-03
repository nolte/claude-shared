# Partitioning and sequencing

Loaded by operation 3 (`partition`) and operation 4 (`sequence`).

## The candidate graph

Nodes are the surveyed issues whose outcome is not `excluded` and whose `bounded` is true.
An unbounded issue is never a node: it goes to the pipeline outcome before the graph is
built, whatever it shares with a bounded issue.

An edge between two nodes exists only where one of the three predicates of
`spec/project/issue-batch-integration/` §A holds **with evidence** in the records:

| Predicate | Edge test | Strong evidence | Weak evidence (not enough alone) |
|---|---|---|---|
| thematic coupling | both change the same capability or the same spec topic | both bodies name the same spec path, command, or component | a shared label; similar wording |
| shared touch surface | their `touch_surface` sets intersect | the intersecting path is `named in body` or `linked PR touched it` on both sides | the path is `inferred from feature area` on either side |
| dependency chain | one issue's change has to land before the other's | one body references the other as prerequisite, or the records show one adds what the other consumes | they were opened by the same person in sequence |

Record each edge with its predicate and evidence. Weak evidence on both sides is no edge.

## Growing clusters

1. Take the connected components of the graph. Each component is a **candidate cluster**.
2. For each candidate, write its single logical change in one sentence. The sentence has
   to describe what the bundle PR will do, in the form a reviewer would accept as one
   change. "Fix #812, #815 and #819" is an enumeration, not a sentence.
3. Where the sentence can't be written, the component is too wide. Cut it at its weakest
   edge (weak evidence, or the only dependency-chain edge joining two otherwise unrelated
   halves) and retry on each half. Record each cut and its reason.
4. A component of size one is a **single**. A candidate that dissolved completely is
   recorded under "Dissolved candidates" with the reason, so the operator sees it was
   considered.
5. Where a component is reviewable in one sitting is a judgement §A leaves as SHOULD;
   when a component is large, prefer two groups with a dependency edge between them over
   one group whose bundle no one will read.

For each surviving group record the provisional **cluster kind** — symptom (several
issues, one likely root cause: the edges are mostly shared-touch-surface on one file or
one component) or class (several issues of one recurring defect class: the edges are
mostly thematic coupling across different files) — and the proposed **Conventional-Commits
type** from the dominant member class (`bug` → `fix`, `feature-request` → `feat`,
`docs` → `docs`, `refactor` → `refactor`, `spec-change`/`infra` → `chore` unless the
change ships user-facing behaviour). Both are provisional; the group run's own analysis
confirms or overturns them and says which.

## Sequencing

Groups are ordered against each other on two tests:

- **Overlap test:** compute each group's `touch_surface_union`. Two groups whose unions
  share a path, or where one's path is a prefix of the other's (a directory against a file
  inside it), are **serial**; record which goes first (the one the other depends on, else
  the smaller one) and the shared path as the reason. Their integration branches would
  otherwise collide at rebase.
- **Dependency test:** a group that consumes what another produces **follows** it. The
  evidence is the same kind as a dependency-chain edge, lifted to group level.

Groups that pass both tests against each other are **independent** and may run in
separate worktrees concurrently. Mark independence explicitly; an unmarked pair reads as
"not checked", not as "independent".

Singles are not sequenced against groups here; `issue-orchestrate` runs them on their own
branches and `pull-request-workflow` §"Sequential merge of multiple open PRs" handles the
merge order.

## When the survey forms no group

Say so with the evidence: the per-issue table with every node and the statement that the
graph has no edge with strong evidence. That is a result the operator can challenge row by
row. An empty "Groups" section without the table is an absence, not a statement.
