# Example 03: Retarget R-3 to sprint 9 and promote detail to fine

## Input prompt

> Bitte `R-3` von Sprint 7 auf Sprint 9 umziehen und dabei den Detailgrad von `coarse` auf `fine` heben.

## Input files (optional)

- `project/roadmap.md` contains `R-3` with `target_sprint: 7`, `detail: coarse`, `status: proposed`, `outcomes: [O-1]`.
- `project/sprints/0007-…md` exists with `status: closed`; `0008-…md` with `status: active` (current sprint); `0009-…md` with `status: planned` (next sprint).
- `project/goals.md` declares `O-1`.
- `project/mission.md` exists; `R-3` carries `mvp: false`.

## Expected behaviour

1. Locate `R-3`. Resolve the new `target_sprint: 9` against `project/sprints/`: file exists, `status: planned` (not terminal) — accept. Note that the current sprint is 8 and the next sprint is 9, so the detail-level invariant requires `detail: fine` after the retarget.
2. Recognise that the user requested both operations in one turn. Sequence them safely: run `promote` first (`coarse → fine`) so the post-write detail invariant holds, then `retarget` to sprint 9. Refuse to write the retarget alone, since landing `target_sprint: 9` while `detail` is still `coarse` would violate the invariant.
3. Draft the `fine`-shaped body for `R-3`: a paragraph stating the user-visible change plus a feature checklist (titles only; full feature schemas remain `feature-decompose`'s job). Show the diff (YAML field flip plus body expansion) and request confirmation.
4. Show the retarget diff (`target_sprint: 7 → 9`) and confirm separately so the user sees each mutation. Re-run end-to-end validation: outcomes resolve, target sprint not terminal, detail invariant holds, all seven YAML keys present in declared order, IDs unique.
5. Write both changes in a single atomic operation; refuse the whole write and report the failing check if any validation step trips.
