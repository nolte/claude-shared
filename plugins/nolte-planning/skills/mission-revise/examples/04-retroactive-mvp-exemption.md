# Example 04 — Operation 2: retroactive-MVP exemption allows `achieved → stabilised`

A configuration repository adopted the planning suite after its core
capabilities had already shipped. The `mission-define` backfill cascade
wrote the mission in one commit, together with the roadmap and sprint
0001: it recorded the MVP retroactively, so the mission's first
committed version opened at `mvp_status: achieved` and sprint 0001 was
recorded as already `closed`. Sprint 0002 is `planned` and carries only
`mvp: false` items, so it can't start while `mvp_status` is `achieved`.
Exercises the retroactive-MVP exemption in `spec/project/mission/`
§Stabilisation gate: the "one full subsequent sprint" condition is
waived, every other condition is still checked from the artefacts and
their git history, and the operator writes the rationale.

## Input prompt

> Das MVP wurde rückwirkend erfasst — flippe `mvp_status` auf
> `stabilised`, damit Sprint 2 starten kann.

## Input files

`project/mission.md` (current state — relevant excerpts only):

```yaml
---
mvp_status: achieved
time_bound:
  kind: mvp_completion
created: 2026-07-02
revised_at: null
---

## Source

- **Authored by**: the `mission-define` cascade (mission-authoring
  backfill), 2026-07-02. The cascade models the minimum viable product
  retroactively. The repository's three capabilities already shipped
  when it adopted the planning suite, so the roadmap records R-1
  through R-3 as `status: done` and opens `mvp_status` at `achieved`
  rather than `defining`.
```

`project/roadmap.md` shows every `mvp: true` item (`R-1`, `R-2`,
`R-3`) at `status: done`. `project/sprints/0001-shared-cicd-baseline.md`
is the MVP-closing sprint (`status: closed`, `started: 2026-07-02`,
`ended: 2026-07-02`, `roadmap_items: [R-1, R-2, R-3]`).
`project/sprints/0002-verifiable-release-archives.md` is
`status: planned` and lists only `R-4` (`mvp: false`). No defect-fix
feature against an MVP item is `in_progress`.

## Expected behaviour

1. **Preconditions pass** as in example 01. Operator selects operation
   2 and the target `stabilised`.
2. **Conditions 1 and 2** pass: `R-1` to `R-3` are `done`, and sprint 1
   is `closed`. Both are shown inline as evidence.
3. **Condition 3: no subsequent sprint has closed.** Sprint
   `1 + 1 = 2` is `planned`, so the skill runs the exemption check
   instead of blocking immediately:
   - **Retroactive test.** The skill runs
     `git log --diff-filter=A --format=%H -- project/mission.md | tail -1`,
     which returns the backfill commit (say `5ffdca5`), then
     `git show 5ffdca5:project/mission.md`. That version already carries
     `mvp_status: achieved`, so the mission was recorded retroactively.
     `created` and `revised_at` aren't consulted.
   - **Scope.** Sprint 2 is `planned`, so the exemption can still apply.
   - **No regression.** The skill runs
     `git log -p --since=2026-07-02 -- project/roadmap.md` and confirms
     that no diff changes a `status:` line of `R-1`, `R-2`, or `R-3` to
     `active`.
   The skill reports condition 3 as satisfied **via the retroactive-MVP
   exemption** and lists this evidence.
4. **Condition 4 (no defect-fix work in flight)** passes.
5. **Operator confirmation.** The skill asks for an explicit "yes".
   The satisfied conditions never make the decision.
6. **Rationale gate.** The skill asks for a one-paragraph rationale
   that names the exemption, and it refuses to draft one. The operator
   supplies it, possibly in a later session. In that case the resumed
   run re-verifies every gate condition before writing.
7. **Write.** After the skill re-verifies the gate and the operator
   approves the diff:
   - `mvp_status: achieved → stabilised`
   - `revised_at: null → <today>`
   - `## Source` gets exactly two additions. The first is the one-line
     transition entry. The second is the operator's rationale paragraph
     with its evidence: sprint 1 and its `ended` date 2026-07-02, commit
     `5ffdca5` first added `project/mission.md` with
     `mvp_status: achieved`, and the operator decision date.
   - `created` stays untouched.
8. **Closing message.** It notes that R-4 and sprint 2 may now start
   through `sprint-execute`. It also warns that if an MVP item
   re-opens, `mvp_status` reverts to `in_progress` per the regression
   path.
