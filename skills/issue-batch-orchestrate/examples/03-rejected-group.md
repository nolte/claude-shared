# Example 03 — candidates that do not form a group

## Operator prompt

> "Take everything still open from this sprint as one batch: #910, #914, #915, #920."

## 1. admit — and decline

The candidates are tested against the three predicates, one at a time:

| Issue | Thematic coupling | Shared touch surface | Dependency chain |
|---|---|---|---|
| #910 | docs typo in the README | `README.md` | none |
| #914 | new export endpoint | `api/export.py` | none |
| #915 | CI cache key drift | `.github/workflows/ci.yml` | none |
| #920 | question about deployment | — | none |

No predicate holds across the set. What they share is a sprint — and **a shared time
window is not a predicate**. Admitting on it would produce exactly the "unrelated
changes in one pull request" bundle that `spec/project/pull-request-workflow/`
§"PR preconditions" forbids outside an `exp/` branch.

The one-sentence test confirms it: no single sentence describes the group's logical
change without degrading into "the open issues from this sprint", which names a
container, not a change.

Two further rejections apply independently:

- **#920 is `question`-class** and yields no work packages by construction.
- **#914 is unbounded** — a new export endpoint creates a roadmap item, so it routes to
  the planning pipeline rather than into any group.

## What the skill does instead

It reports the decision with its reasons and stops. It does **not** form a smaller group
opportunistically, because none of the remaining pairs shares a predicate either.

The operator is offered the conformant alternatives:

- #910 and #915 individually via `issue-orchestrate`
- #914 via `feature-decompose` after a roadmap item exists
- #920 answered directly; no branch, no pull request

## Why this example exists

A skill that never declines is a skill whose admission rules are decorative. The
predicates only mean something if there is a case they reject — and "everything open in
this sprint" is the most common request that must be refused, because it looks like a
group and is only a queue.
