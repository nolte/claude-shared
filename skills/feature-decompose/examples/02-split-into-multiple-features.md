# Example 02 — Split a large roadmap item into three features

A substantial roadmap item targeted at the next sprint that decomposes
into **three** features. Exercises the multi-feature path, the
at-most-one-per-sprint `verifies_sprint_value` invariant, and the
choice of which feature carries it when the roadmap item is the
MVP-closer.

## Input prompt

> Break R-7 down into features for the upcoming sprint.

## Input files

`project/roadmap.md` (excerpt):

```yaml
- id: R-7
  title: First-class search across docs, skills, and agents catalogue
  outcomes: [O-1, O-4]
  detail: fine
  target_sprint: 9
  mvp: true
  status: planned
```

`project/mission.md` declares `R-7` as the MVP-closer via
`verifies_via: R-7` and `mvp_status: in_progress`. Sprint 9 is the
upcoming sprint and currently `planned` with `value_statement: "An
end user can find any docs page, skill, or agent in one search box."`
No feature under `project/features/` currently sets
`verifies_sprint_value` for sprint 9. The
`feature-consistency-reviewer` agent is reachable.

## Expected behaviour

1. **Preconditions pass** the same way as in Example 01;
   additionally, the skill resolves `mission.md` and notices that
   `R-7` is the MVP-closer.
2. **Restate the roadmap item** and **propose a three-feature
   split** based on the item's body checklist (or its prose):
   - F-A — Search index build pipeline over docs + skills + agents.
   - F-B — Search box UI on the docs landing page.
   - F-C — Search result ranking and snippet rendering.
   The operator may rename, merge, or add titles before any
   gathering begins.
3. **Per-feature gathering runs three times.** For each of F-A, F-B,
   F-C the skill collects title, slug (verifying each path under
   `project/features/<slug>.md` is free), description, three to
   seven acceptance criteria as
   `- [ ] **acceptance-<n>** …` bullets, and one test hook per
   criterion as `- **acceptance-<n>** — <mechanism> — pending`. The
   skill rejects any process-internal criterion ("PR merged",
   "deployed to staging") and asks for a user-visible rephrasing.
4. **Value-verifier choice is mandatory and singular.** Because
   `R-7` closes the MVP per `mission.md`, exactly one of F-A / F-B /
   F-C **MUST** carry `verifies_sprint_value: acceptance-<n>`
   pointing at the criterion that proves the sprint's
   `value_statement`. The skill walks the operator through the
   choice — typically F-B (the search box on the landing page is
   what an end user can directly experience) with
   `verifies_sprint_value: acceptance-2` (e.g. *"Typing a query in
   the docs search box returns results from docs, skills, and
   agents in a single ranked list"*). The other two features remain
   `verifies_sprint_value: null`. The skill refuses to set the
   field on more than one of the three.
5. **Consistency check dispatched once per draft feature** (three
   dispatches), each with its own assembled frontmatter and body,
   the resolved `roadmap_item: R-7`, its own slug, and the short
   git revision. Clean findings are persisted on each feature with
   the one-element `kind: clean` `findings` array and a matching
   one-paragraph `## Consistency notes` entry.
6. **Three files written** under `project/features/`, each with the
   nine frontmatter fields in declared order and the five required
   body sections in declared order. Only the feature chosen in
   step 4 carries a non-null `verifies_sprint_value`; the other
   two have `verifies_sprint_value: null`.
7. **Closing message** lists the three paths back to the operator
   in their language, names which feature carries
   `verifies_sprint_value` and which acceptance criterion it points
   at, and reminds the operator that `sprint-plan` will flip the
   three drafts to `ready` once it assigns `sprint: 9`.
