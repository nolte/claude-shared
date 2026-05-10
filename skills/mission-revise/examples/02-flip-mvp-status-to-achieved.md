# Example 02 — Operation B: flip `mvp_status: in_progress → achieved`

Every `mvp: true` roadmap item has reached `status: done` and the
`verifies_via` acceptance criterion is checked on its feature. The
operator asks for the lifecycle flip. Exercises branch B's evidence
walk for the `in_progress → achieved` transition (which is **not**
the stabilisation gate — that's example 03).

## Input prompt

> Der MVP ist erreicht — flippe `mvp_status` auf `achieved`.

## Input files

`project/mission.md` (current state — relevant excerpts only):

```yaml
---
mission_statement: "Provide a stable scaffolding layer for Claude Code
  plugin authors so that new skills land in production within one
  sprint."
mvp_status: in_progress
audiences: [plugin-authors, plugin-reviewers]
verifies_via: F-7:acceptance-2
relevant_outcomes: [O-1, O-3]
time_bound: { kind: mvp_completion }
created: 2026-02-14
revised_at: 2026-05-02
---

## Source

- 2026-02-14 — created.
- 2026-04-22 — `defining → in_progress` after R-2 entered `status: active`.
- 2026-05-02 — added `plugin-reviewers` audience.
```

`project/roadmap.md` (excerpt — only `mvp: true` items shown):

```yaml
- id: R-2
  title: Skill scaffolding command
  mvp: true
  status: done
  target_sprint: 4
- id: R-5
  title: Mission file authoring flow
  mvp: true
  status: done
  target_sprint: 5
- id: R-9
  title: Cross-skill consistency check
  mvp: true
  status: done
  target_sprint: 6
```

`project/features/F-7.md` exists; the `## Acceptance criteria`
checklist shows `- [x] **acceptance-2** A freshly-scaffolded skill
passes \`task lint\` and \`task test\` without manual edits.`
`project/sprints/0006-cross-skill-consistency.md` is `status: closed`
(it carried R-9, the final `mvp: true` item).

## Expected behaviour

1. **Preconditions pass** as in example 01.
2. **Operation routing.** Operator selects B. Skill enumerates the
   legal targets from `in_progress`: `achieved` is the only forward
   move (regression to `defining` is illegal). Operator picks
   `achieved`.
3. **Trigger verification — every `mvp: true` item is `done`.** Skill
   walks `project/roadmap.md`, lists `R-2`, `R-5`, `R-9` with their
   statuses inline so the operator can see the evidence. All three
   are `status: done`; condition met.
4. **Trigger verification — `verifies_via` criterion is checked.**
   Skill opens `project/features/F-7.md`, locates `acceptance-2`, and
   confirms the bullet is `- [x]` (not `- [ ]`). Skill reproduces the
   criterion text inline so the operator sees what is being verified.
5. **Stabilisation gate is *not* run.** Skill explicitly notes that
   the gate (sprint-after-MVP, no in-flight defect-fix work) belongs
   to the *next* transition (`achieved → stabilised`) and is **not** a
   precondition for `in_progress → achieved`. No `project/sprints/`
   walk-by-`number+1` happens here.
6. **Operator confirmation.** Skill asks for an explicit "yes" before
   mutating the file — the satisfied conditions justify the decision
   but never make it. If the operator hesitates, the skill stops and
   leaves the file untouched.
7. **Write.** On confirmed yes:
   - `mvp_status: in_progress → achieved`
   - `revised_at: 2026-05-02 → 2026-05-10`
   - append to `## Source`:
     `- 2026-05-10 — in_progress → achieved (R-2, R-5, R-9 all done; F-7:acceptance-2 checked).`
   - `created: 2026-02-14` stays untouched.
8. **Diff presentation.** Skill shows the frontmatter delta plus the
   single-line `## Source` append, iterates until approval, then
   writes the file in place. Branch C is **not** triggered (current
   status was `in_progress`, not `stabilised`).
9. **Closing message** confirms the path, restates that
   `achieved → stabilised` requires the full §Stabilisation gate
   (one full subsequent sprint closed without regression, no
   defect-fix work in flight), and reminds the operator that no
   automatic future-flip will happen — the next transition is also an
   explicit operator decision.
