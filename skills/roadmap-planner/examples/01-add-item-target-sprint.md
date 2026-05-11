# Example 01: Add new roadmap item targeting the next sprint

## Input prompt

> Bitte einen neuen Roadmap-Eintrag anlegen: Titel "Audit-Bundle Inventar export", Outcome `O-2`, target_sprint 8, detail fine. Das ist ein MVP-Item.

## Input files (optional)

- `project/goals.md` declares outcomes `O-1`, `O-2`, `O-3`.
- `project/roadmap.md` already contains items `R-1` … `R-7` (highest used ID is `R-7`).
- `project/sprints/0007-…md` exists with `status: closed` (current sprint) and `project/sprints/0008-…md` exists with `status: planned` (next sprint).
- `project/mission.md` exists with `mvp_status: in_progress`.

## Expected behaviour

1. Detect German user language; respond in German. Confirm preconditions: `roadmap.md`, `goals.md`, `sprints/`, and `mission.md` are reachable; the existing roadmap parses end-to-end.
2. Resolve cross-references: `O-2` exists in `goals.md` (accept); `target_sprint: 8` resolves to `0008-…md` in `status: planned` (accept, not terminal); `mvp_status` is `in_progress` so `mvp: true` is permitted.
3. Assign `id: R-8` (monotonic next after `R-7`, never reused) and check the detail-level invariant: `target_sprint: 8` is the next sprint, so `detail: fine` is required and satisfied.
4. Draft the YAML block with the seven required keys in declared order plus a `fine`-shaped body (paragraph describing the user-visible change plus a feature checklist with titles only). Show the draft and request explicit confirmation before writing.
5. On approval, append the item to `project/roadmap.md` in one atomic write; refuse and report the failing check if any end-to-end validation step would fail.
