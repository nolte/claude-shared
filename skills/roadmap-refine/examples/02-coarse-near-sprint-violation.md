# Example 02 — Coarse item targeting the current sprint

A roadmap item whose `target_sprint` matches the current (`active`)
sprint while still carrying `detail: coarse`. The skill emits exactly
one violation record on stderr, walks a single fix proposal with the
operator, and exits with the contract's non-zero code if the operator
defers the fix.

## Input prompt

> Roadmap verfeinern, bevor wir Sprint 0007 starten.

## Input files

`project/sprints/`:

- `0006-docs-relaunch.md` — frontmatter `status: closed`, `number: 6`.
- `0007-active-sprint-banner.md` — frontmatter `status: active`, `number: 7`.
- `0008-release-pipeline.md` — frontmatter `status: planned`, `number: 8`.

`project/roadmap.md` (excerpt — only the items in the audit window
shown):

```yaml
- id: R-11
  title: Active-sprint banner on docs landing page
  outcomes: [O-3]
  detail: coarse
  target_sprint: 7
  mvp: false
  status: planned

  Banner soll der Operatorin im Docs-Header zeigen, welcher Sprint
  gerade läuft. Konkrete Akzeptanzkriterien stehen noch nicht.
- id: R-12
  title: Release-publish trigger skill rolled out across portfolio
  outcomes: [O-2]
  detail: fine
  target_sprint: 8
  mvp: true
  status: planned
```

`project/goals.md` resolves both `O-2` and `O-3`; `project/mission.md`
exists. No other items target sprints `7` or `8`.

## Expected behaviour

1. **Language detection.** The user wrote German; every prose response,
   sprint-window echo, violation record, and remediation hint is in
   German. The drafted body paragraph and feature checklist that the
   skill proposes for `R-11` are in German. Schema strings stay
   English.
2. **Preconditions pass.** Roadmap, goals, mission, and the sprints
   directory all parse; `R-11` and `R-12` parse cleanly.
3. **Sprint-window resolution.** Current sprint is `0007` (active,
   number `7`); next sprint is `0008` (planned, number `8`). The
   echo line is printed before the walk.
4. **Violation detection.** The walk yields exactly one violation
   (`R-11` — `target_sprint: 7` matches the current sprint and
   `detail: coarse` violates the invariant). `R-12` is compliant
   (`detail: fine` for the next sprint) and produces no record.
5. **Stderr violation record.** The skill emits one machine-readable
   record to stderr in the spec's shape:

   ```
   violation id=R-11 target_sprint=7 current_detail=coarse resolved_current_sprint=7 resolved_next_sprint=8 hint="Promote to detail: fine and add feature checklist"
   ```

   The record **MUST NOT** be suppressed on the contract that the
   operator promises to fix it interactively.
6. **Per-item fix proposal.** The skill shows `R-11`'s heading, YAML
   block, and current body to the operator and offers the three
   canonical paths from the spec: promote to `fine` (skill drafts the
   missing body shape — one paragraph naming the user-visible change
   plus a feature checklist), retarget the sprint via
   `roadmap-planner` dispatch, or drop the sprint anchor by setting
   `target_sprint: null` directly. The skill does **not** silently
   pick a path.
7. **Operator defers the fix.** In this scenario the operator says
   *"Lass uns das morgen machen"* (the fix is deferred). The skill
   **MUST NOT** mutate `project/roadmap.md` and **MUST NOT** demote
   the violation to a passing run.
8. **Final report.** The skill reports `1 violation found`, `0 fixed`,
   `1 deferred`, `0 skipped`, and exits **non-zero**. The exit code
   is the load-bearing contract for any automation watching this
   skill — a deferred fix keeps CI red.
9. **No file mutation.** `project/roadmap.md` is byte-identical before
   and after the run; `git status` reports a clean working tree.
10. **No `roadmap-planner` dispatch.** Because the operator deferred
    rather than picking the retarget path, no skill-to-skill dispatch
    happens; the violation record is the sole persistent artefact of
    the run (on stderr and in the user's transcript).
