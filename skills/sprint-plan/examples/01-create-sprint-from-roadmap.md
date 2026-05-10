# Example 01 — Create sprint 0008 from roadmap items

Happy-path scaffolding of a new `planned` sprint when roadmap items already
carry `target_sprint: 8` and decomposed features exist in `project/features/`.
Exercises operations 1, 2, 3, 4, 5, 6, 7, 8 of `SKILL.md` end-to-end.

## Input prompt

> Plane den nächsten Sprint. Value statement: "Reviewers can subscribe to a
> roadmap item and receive a notification the moment its sprint closes."

## Input files

`project/sprints/0007-curate-release-notes.md` (existing, `status: closed`):

```markdown
---
number: 7
status: closed
started: 2026-04-12
ended: 2026-04-26
value_statement: Maintainers ship release notes audiences can actually read.
artifact_ref: v0.7.0
last_commit: 9c1f4a2
roadmap_items: [R-12]
features: [F-31, F-32]
---
```

`project/sprints/` contains sprints `0001` through `0007`; the highest
`number` is `7`.

`project/roadmap.md` (excerpt):

```markdown
- id: R-14
  title: Roadmap-item subscription notifications
  outcomes: [O-3]
  status: proposed
  target_sprint: 8
  detail: fine
  mvp: false
- id: R-15
  title: Notification delivery channel selection
  outcomes: [O-3]
  status: proposed
  target_sprint: 8
  detail: fine
  mvp: false
- id: R-16
  title: Bulk-import historical reviewers
  outcomes: [O-4]
  status: proposed
  target_sprint: 9
  detail: coarse
  mvp: false
```

`project/features/subscribe-to-roadmap-item.md` (excerpt):

```markdown
---
id: F-33
roadmap_item: R-14
sprint: null
status: ready
verifies_sprint_value: null
acceptance:
  - id: acceptance-1
    text: A reviewer can subscribe to R-<n> from the roadmap UI.
  - id: acceptance-2
    text: A subscribed reviewer receives a notification within 60s of the
      hosting sprint flipping to `closed`.
---
```

`project/features/pick-notification-channel.md` (excerpt):

```markdown
---
id: F-34
roadmap_item: R-15
sprint: null
status: ready
verifies_sprint_value: null
acceptance:
  - id: acceptance-1
    text: A reviewer can pick email, in-app, or webhook as the delivery
      channel for their subscriptions.
---
```

## Expected behaviour

1. Skill detects the user is writing in German and replies in German;
   the sprint markdown itself stays in the project's primary language (EN).
2. Operation 1 — reads every `project/sprints/*.md` frontmatter `number`,
   resolves max as `7`, sets the new sprint's `number: 8`, formatted as
   `0008` for the filename.
3. Operation 2 — accepts the supplied `value_statement` (begins with
   "Reviewers can subscribe …"; no operator-internal verb triggered).
4. Operation 3 — slugifies to `roadmap-item-subscription-notifications`
   (≤6 words after trimming) and proposes
   `project/sprints/0008-roadmap-item-subscription-notifications.md`.
5. Operation 4 — reads `project/roadmap.md`, collects `R-14` and `R-15`
   (both `target_sprint: 8`), excludes `R-16` (`target_sprint: 9`).
   Presents `[R-14, R-15]` to the user; user confirms.
6. Operation 5 — walks `project/features/`, finds `F-33` linked to `R-14`
   and `F-34` linked to `R-15`, both with `sprint: null`. Both are
   collected; no `feature-decompose` dispatch needed.
7. Operation 6 — neither `F-33` nor `F-34` declares
   `verifies_sprint_value`; the skill asks the user which feature carries
   the sprint's value-verification, and which `acceptance-<n>` is the
   verifying criterion. User picks `F-33` / `acceptance-2` (the
   "notification within 60s of `closed`" criterion). Skill writes
   `verifies_sprint_value: acceptance-2` into `F-33`'s frontmatter in the
   same write transaction.
8. Operation 7 — emits the planned-sprint file with frontmatter in the
   declared key order, `status: planned`, `started: null`, `ended: null`,
   `roadmap_items: [R-14, R-15]`, `features: [F-33, F-34]`, plus the four
   body sections (`## Goal`, `## Features`, `## Out of scope`,
   `## Review notes`). The `## Features` bullet list mirrors the
   `features` frontmatter list exactly.
9. Operation 8 — diffs the planned file back to the user, highlights
   `F-33` as the verifying feature, and only writes after explicit
   approval. Each affected feature file is updated to set its `sprint`
   field to `8` in the same write batch.
10. Final report names the path written
    (`project/sprints/0008-roadmap-item-subscription-notifications.md`),
    the sprint number `8`, and the verifying feature `F-33` /
    `acceptance-2`.
