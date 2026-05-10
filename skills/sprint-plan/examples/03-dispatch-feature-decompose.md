# Example 03 — Dispatch `feature-decompose` for undecomposed roadmap items

Hybrid orchestration scenario for operation 5 of `SKILL.md`. The roadmap items
targeting the new sprint exist and are `fine`-detail, but no corresponding
`project/features/*.md` files have been authored yet. The skill MUST surface
the gap, offer to dispatch `feature-decompose` for each affected roadmap item,
then resume `sprint-plan` at operation 5 once the features land.

## Input prompt

> Plane Sprint 5. Value statement: "End-users can search the published
> portfolio by capability tag and land on the owning repository in one
> click."

## Input files

`project/sprints/` contains `0001` through `0004`; the highest `number` is
`4`. The next sprint number resolves to `5`.

`project/roadmap.md` (excerpt):

```markdown
- id: R-7
  title: Capability-tag search index
  outcomes: [O-1]
  status: proposed
  target_sprint: 5
  detail: fine
  mvp: true
- id: R-8
  title: Capability-to-repository click-through
  outcomes: [O-1]
  status: proposed
  target_sprint: 5
  detail: fine
  mvp: true
```

`project/features/` exists but contains no file whose `roadmap_item` field
equals `R-7` or `R-8`. (Other features for earlier sprints exist and are
unrelated.)

`project/goals.md` declares `O-1`. `project/audiences.md` exists.

## Expected behaviour

1. Skill replies in German (matches the user's language); the sprint
   markdown stays in EN.
2. Operations 1–4 proceed normally:
   - Number resolves to `5`, filename
     `project/sprints/0005-search-portfolio-by-capability-tag.md`
     proposed.
   - `value_statement` accepted (no operator-internal verb).
   - `roadmap.md` walk collects `R-7` and `R-8`; user confirms
     `[R-7, R-8]`.
3. Operation 5 — for each roadmap item the skill walks
   `project/features/` looking for a feature whose `roadmap_item` matches
   and whose `sprint` is null or `5`:
   - `R-7` → no matching feature found.
   - `R-8` → no matching feature found.
4. Skill surfaces the gap explicitly: lists `R-7` and `R-8` as missing
   feature decompositions, names `feature-decompose` as the canonical
   skill that decomposes a roadmap item into one or more features per
   `spec/project/feature/`, and asks the user to confirm dispatching
   `feature-decompose` for each item. Skill does NOT fabricate features
   inline.
5. User confirms. Skill dispatches `feature-decompose` for `R-7`. That
   skill returns control with one or more new features written under
   `project/features/`, each carrying `roadmap_item: R-7`, `sprint: null`
   (or `5`), and `status: ready`. Skill then dispatches
   `feature-decompose` for `R-8` and receives the same shape of result.
6. Skill resumes operation 5 with the freshly written features in scope,
   collects their `id` values into the `features` candidate list, and
   continues to operation 6 (naming the value-verifying feature) and
   operation 7 (rendering the sprint markdown).
7. Alternative path — if the user declines decomposition for `R-8`, the
   skill drops `R-8` from `roadmap_items` and proceeds with only `R-7`.
   The decline is reported in the final summary so the operator knows
   `R-8` remains un-sprinted.
8. The dispatched `feature-decompose` runs are not silent: each
   dispatch is announced before the call and each return is summarised
   (which feature `id`s were created) before sprint-plan resumes, so the
   operator can intervene between decomposition and sprint composition.
9. No `project/sprints/0005-*.md` file is written until the feature
   decompositions are in place AND operation 6 has named exactly one
   verifying feature with its `acceptance-<n>` identifier.
