# Example 03 — Walk the fix proposals: promote two, retarget one

Three items in the audit window violate the invariant. The operator
walks the fix queue end-to-end: two items are promoted to `fine`
in-place (the skill drafts the missing body shape and the operator
accepts), and one item is retargeted via a `roadmap-plan` dispatch.
The walk re-resolves the sprint window after each individual fix and
ends with a clean exit.

## Input prompt

> Roadmap-Detailstufen prüfen und gleich mitziehen — wir wollen Sprint 0008 sauber haben.

## Input files

`project/sprints/`:

- `0006-docs-relaunch.md` — frontmatter `status: closed`, `number: 6`.
- `0007-active-sprint-banner.md` — frontmatter `status: active`, `number: 7`.
- `0008-release-pipeline.md` — frontmatter `status: planned`, `number: 8`.
- `0009-portfolio-rollout.md` — frontmatter `status: planned`, `number: 9`.
- `0010-cleanup-sweep.md` — frontmatter `status: planned`, `number: 10`.

`project/roadmap.md` (excerpt — only items in the audit window shown):

```yaml
- id: R-11
  title: Active-sprint banner on docs landing page
  outcomes: [O-3]
  detail: fine
  target_sprint: 7
  mvp: false
  status: active
- id: R-12
  title: Release-publish trigger skill rolled out across portfolio
  outcomes: [O-2]
  detail: coarse
  target_sprint: 8
  mvp: true
  status: planned
- id: R-13
  title: Portfolio capability inventory rendered under docs/
  outcomes: [O-4]
  detail: coarse
  target_sprint: 8
  mvp: false
  status: planned
- id: R-14
  title: Sprint cadence retrospective tooling
  outcomes: [O-1]
  detail: backlog
  target_sprint: 8
  mvp: false
  status: proposed
```

`project/goals.md` resolves `O-1`, `O-2`, `O-3`, `O-4`. `project/mission.md`
exists. The `roadmap-plan` skill is reachable in the current plugin
runtime. No item currently targets sprint `9` or `10`.

## Expected behaviour

1. **Language detection.** German prompt, German prose throughout —
   sprint-window echo, three violation records, three per-item fix
   dialogues, the drafted body paragraphs, and the final report are all
   German. Schema strings stay English.
2. **Preconditions pass.** Roadmap, goals, mission, and the sprints
   directory parse; every audit-window item parses cleanly.
3. **Sprint-window resolution.** Current sprint `0007` (active, `7`);
   next sprint `0008` (planned, `8`). The echo is printed before the
   walk.
4. **Violation detection.** The walk yields exactly three violations,
   each emitted as a machine-readable record on stderr in roadmap
   order:

   ```
   violation id=R-12 target_sprint=8 current_detail=coarse resolved_current_sprint=7 resolved_next_sprint=8 hint="Promote to detail: fine and add feature checklist"
   violation id=R-13 target_sprint=8 current_detail=coarse resolved_current_sprint=7 resolved_next_sprint=8 hint="Promote to detail: fine and add feature checklist"
   violation id=R-14 target_sprint=8 current_detail=backlog resolved_current_sprint=7 resolved_next_sprint=8 hint="Split into a fine slice and a coarse follow-up, or retarget"
   ```

   `R-11` is compliant and produces no record.
5. **Per-item fix walk — `R-12` (promote in place).**
   - The skill shows `R-12`'s heading, YAML, and current body to the
     operator alongside the violation record.
   - The operator picks **promote to `fine`**.
   - The skill drafts the missing body shape: one German paragraph
     naming the user-visible change ("Operatorinnen können den
     `release-publish-trigger`-Skill auf jedem Portfolio-Repo
     auslösen …") and a feature checklist
     (`- [ ] feature: <slug>` bullets) covering the rollout steps.
   - The operator confirms verbatim. The skill flips
     `detail: coarse → fine` in the YAML block and writes the new body
     in-place. No `roadmap-plan` dispatch (direct edit is the
     spec-allowed path for promotion).
   - The skill re-resolves the sprint window from disk; `7` / `8`
     unchanged.
6. **Per-item fix walk — `R-13` (promote in place).**
   - Same flow as `R-12`: the operator picks **promote to `fine`**, the
     skill drafts paragraph plus feature checklist, the operator
     accepts, the YAML flips and the body is written.
   - Sprint window re-resolved; still `7` / `8`.
7. **Per-item fix walk — `R-14` (retarget via dispatch).**
   - The skill shows `R-14` and offers the three paths.
   - The operator picks **retarget the sprint** to `0010` because
     `R-14` does not fit the sprint-`0008` value-statement.
   - The skill **MUST NOT** edit `target_sprint` directly. It dispatches
     `roadmap-plan` with the requested change
     (`R-14.target_sprint: 8 → 10`), letting the planner validate
     outcome resolution, sprint resolution, and the lifecycle
     constraints declared in the roadmap and mission specs.
   - `roadmap-plan` returns success with the YAML rewritten.
     `R-14`'s `target_sprint` is now `10`; `detail` stays `backlog`
     (allowed because sprint `10` is two out from the current sprint).
   - The skill re-resolves the sprint window; still `7` / `8`.
8. **Re-walk after every fix.** After all three fixes, the skill walks
   the audit window once more from disk to confirm nothing slipped
   back: `R-11` compliant, `R-12` compliant, `R-13` compliant, `R-14`
   no longer in the window. No new records on stderr.
9. **Final report.** The skill reports `3 violations found`,
   `3 fixed` (two promotions, one retarget), `0 deferred`,
   `0 skipped`, and exits with code `0`. The German confirmation line
   tells the operator the queue is now compliant for sprints `0007`
   and `0008`.
10. **File mutation contract.** `project/roadmap.md` is the only file
    touched on disk. The diff contains exactly: (a) `R-12` flipped
    from `coarse` to `fine` plus the new body; (b) `R-13` flipped
    from `coarse` to `fine` plus the new body; (c) `R-14`'s
    `target_sprint` rewritten by `roadmap-plan`. The skill
    **MUST NOT** demote any `fine` item, and **MUST NOT** flip an
    `mvp` flag — both are owned by `roadmap-plan` under explicit
    user intent only.
