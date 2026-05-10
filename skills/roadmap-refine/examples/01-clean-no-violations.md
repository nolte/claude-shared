# Example 01 — Clean walk, no violations

A roadmap whose every item targeting the current or next sprint already
carries `detail: fine`. The skill resolves the sprint window, walks the
queue, finds nothing to flag, and exits zero without proposing any fix.

## Input prompt

> Bitte prüfe die Roadmap-Detailstufen — ist der nächste Sprint vorbereitet?

## Input files

`project/sprints/` (the only sprint files present):

- `0006-docs-relaunch.md` — frontmatter `status: closed`, `number: 6`.
- `0007-active-sprint-banner.md` — frontmatter `status: active`, `number: 7`.
- `0008-release-pipeline.md` — frontmatter `status: planned`, `number: 8`.
- `0009-portfolio-rollout.md` — frontmatter `status: planned`, `number: 9`.

`project/roadmap.md` (excerpt — only the items relevant to the audit
window shown):

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
  detail: fine
  target_sprint: 8
  mvp: true
  status: planned
- id: R-13
  title: Portfolio capability inventory rendered under docs/
  outcomes: [O-4]
  detail: coarse
  target_sprint: 9
  mvp: false
  status: planned
- id: R-14
  title: Sprint cadence retrospective tooling
  outcomes: [O-1]
  detail: backlog
  target_sprint: null
  mvp: false
  status: proposed
```

`project/goals.md` and `project/mission.md` exist; both `O-2` and `O-3`
resolve cleanly. The working tree is clean on `develop`.

## Expected behaviour

1. **Language detection** — the skill detects German from the user's
   prompt and from the prose already in `project/roadmap.md`; every
   status update, the sprint-window echo, and the final report are in
   German. Schema strings (`detail: fine`, `target_sprint`, `R-<n>`,
   `active`, `planned`, `closed`) stay in their canonical English form.
2. **Preconditions pass.** The skill confirms `project/roadmap.md` and
   `project/goals.md` exist, confirms `project/sprints/` is non-empty,
   and parses every roadmap item without error.
3. **Sprint-window resolution.** The skill applies the spec's exact
   resolution rule: current sprint is the only `active` one (`0007`,
   number `7`); next sprint is the lowest-numbered `planned` sprint
   strictly greater than `7`, which is `0008` (number `8`). The skill
   echoes the resolution back to the user before walking items:

   ```
   Current sprint: 0007 (active)
   Next sprint:    0008 (planned)
   ```

4. **Walk the roadmap.** The skill iterates every item in roadmap order:
   - `R-11` — `target_sprint: 7` matches the current sprint;
     `detail: fine` — compliant, no record emitted.
   - `R-12` — `target_sprint: 8` matches the next sprint;
     `detail: fine` — compliant, no record emitted.
   - `R-13` — `target_sprint: 9` is two sprints out (neither current nor
     next); skipped per spec, no record emitted even though
     `detail: coarse`.
   - `R-14` — `target_sprint: null`; skipped per spec.
5. **No violation records.** Nothing is written to stderr beyond the
   sprint-window echo and a final summary line. The skill **MUST NOT**
   emit a violation record for `R-13` despite its coarse detail —
   the invariant only applies to the current and the next sprint.
6. **No fix walk.** Because no violation surfaced, the skill skips the
   per-item fix-proposal phase entirely; no `roadmap-planner` dispatch,
   no in-place edit to `project/roadmap.md`.
7. **Final report.** The skill reports `0 violations found`,
   `0 fixed`, `0 deferred`, `0 skipped`, and exits with code `0`. The
   user gets a one-line confirmation in German that the queue is
   compliant for the current sprint window.
8. **No file mutation.** `project/roadmap.md` is byte-identical before
   and after the run; `git status` reports a clean working tree.
