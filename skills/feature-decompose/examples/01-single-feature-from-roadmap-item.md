# Example 01 — Single feature from a small roadmap item

A narrow, well-scoped roadmap item that the operator agrees should
decompose into exactly **one** feature. Exercises the smallest valid
decomposition path: confirm the split is N=1, gather the per-feature
inputs, run a clean consistency check, write one file with
`status: draft`.

## Input prompt

> Decompose R-12 into features.

## Input files

`project/roadmap.md` (excerpt — only the relevant item shown):

```yaml
- id: R-12
  title: Surface the active sprint banner on the docs landing page
  outcomes: [O-3]
  detail: fine
  target_sprint: 7
  mvp: false
  status: planned
```

`project/goals.md` resolves `O-3` cleanly, `project/mission.md` exists
with an audience artefact under `project/audiences.md`, and the
`feature-consistency-reviewer` agent is reachable in the current plugin
runtime. No existing feature under `project/features/` mentions a
sprint banner, a docs landing page widget, or `R-12`.

## Expected behaviour

1. **Preconditions pass.** The skill confirms `spec/project/feature/`
   exists, `R-12` resolves with `detail: fine`, `O-3` resolves in
   `goals.md`, the audience artefact exists, the agent is reachable,
   and the next free `F-<n>` is computed by scanning
   `project/features/`.
2. **Restate the roadmap item back to the operator** — title,
   outcomes, detail, target sprint, MVP flag — and propose a one-feature
   split (N=1) with a candidate title like *"Active-sprint banner on
   docs landing page"*. The operator confirms.
3. **Per-feature gathering** runs once: title confirmed; slug
   `active-sprint-banner` proposed and the path
   `project/features/active-sprint-banner.md` verified free; one to
   three description paragraphs drafted with the operator; three to
   seven acceptance criteria collected as
   `- [ ] **acceptance-<n>** …` bullets, each user-visible (no
   "PR merged" / "CI green" criteria); one test hook per acceptance
   criterion in `- **acceptance-<n>** — <mechanism> — pending` shape.
4. **Value-verifier choice.** The operator is asked whether this
   single feature carries `verifies_sprint_value`. Because `R-12` is
   not the MVP-closer (`mvp: false`), the operator may leave it
   `null`; if they pick a criterion, it must be one of the bullets
   gathered in step 3.
5. **Consistency check dispatched.** The skill confirms
   `git rev-parse --is-inside-work-tree`, computes
   `git rev-parse --short HEAD`, and dispatches
   `feature-consistency-reviewer` with the draft frontmatter, body,
   resolved `roadmap_item: R-12`, the slug, and the short revision.
   The agent returns a single `kind: clean` finding.
6. **Findings persisted in both places.** Frontmatter
   `consistency_check` is populated with `performed_at`,
   `agent_version` (the agent's id, **not** a `manual-…` token), and
   the one-element `findings` list `[{kind: clean, target: <repo
   root>, resolution: proceed}]`. The body's `## Consistency notes`
   carries one paragraph restating the clean result and the
   `proceed` resolution.
7. **Single file written** at
   `project/features/active-sprint-banner.md` with the nine
   frontmatter fields in declared order
   (`id`, `title`, `status: draft`, `roadmap_item: R-12`,
   `sprint: null`, `created`, `ended: null`, `verifies_sprint_value`,
   `consistency_check`) and the five required body sections in
   declared order (`## Description`, `## Acceptance criteria`,
   `## Test hooks`, `## Consistency notes`, `## Risks`).
8. **Closing message** confirms the path back in the operator's
   language and reminds them that `draft → ready` is owned by
   `sprint-plan`, not by this skill — no status flip happens here.
