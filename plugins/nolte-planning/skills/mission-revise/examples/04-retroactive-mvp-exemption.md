# Example 04 — Operation 2: retroactive-MVP exemption allows `achieved → stabilised`

The project recorded its mission after the MVP had already shipped:
the mission file was written on the day the MVP-closing sprint ended.
The next sprint is `planned` and carries only `mvp: false` items, so it
can never start while `mvp_status` is `achieved`. Exercises the
retroactive-MVP exemption in `spec/project/mission/` §Stabilisation
gate: the "one full subsequent sprint" condition is waived, every other
condition is still checked, and the operator writes the rationale.

## Input prompt

> Das MVP war schon vor der Mission ausgeliefert — flippe `mvp_status`
> auf `stabilised`.

## Input files

`project/mission.md` (current state — relevant excerpts only):

```yaml
---
mvp_status: achieved
created: 2026-07-02
revised_at: 2026-07-02
---

## Source

- 2026-07-02 — created; MVP items R-1 to R-3 recorded as already done.
```

`project/roadmap.md` confirms every `mvp: true` item (`R-1`, `R-2`,
`R-3`) at `status: done`; no MVP item has re-opened since. The
MVP-closing sprint is `project/sprints/0001-mvp-baseline.md`
(`status: closed`, `ended: 2026-07-02`, carried the final MVP item
R-3). `project/sprints/0002-post-mvp-extensions.md` is
`status: planned` and lists only `mvp: false` roadmap items. No
defect-fix feature against an MVP item is `in_progress`.

## Expected behaviour

1. **Preconditions pass** as in example 01. Operator selects operation
   2 and the target `stabilised`.
2. **Condition 1 (every `mvp: true` item `done`) and condition 2
   (MVP-closing sprint `closed`)** pass, with `R-1` to `R-3` and sprint
   1 shown inline as evidence.
3. **Condition 3 — no subsequent sprint has closed.** Sprint
   `1 + 1 = 2` is `planned`. Instead of blocking immediately, the
   skill checks the exemption: mission `created: 2026-07-02` is on or
   after sprint 1's `ended: 2026-07-02`, and no MVP item has re-opened
   to `status: active` since sprint 1 closed. The skill reports the
   condition as satisfied **via the retroactive-MVP exemption** and
   shows both dates.
4. **Condition 4 (no defect-fix work in flight)** passes.
5. **Operator confirmation.** The skill asks for an explicit "yes";
   the satisfied conditions never make the decision.
6. **Rationale gate.** Before writing, the skill asks the operator for
   the one-paragraph rationale naming the exemption and refuses to
   draft it. The operator supplies, for example: *"Retroactive-MVP
   exemption: the MVP shipped in sprint 1 before this mission was
   recorded, and sprint 2 holds only post-MVP work that can't start
   until the MVP is stabilised."*
7. **Write.** On approval of the diff:
   - `mvp_status: achieved → stabilised`
   - `revised_at: 2026-07-02 → <today>`
   - append to `## Source` the one-line flip entry, the operator's
     rationale paragraph, and the evidence: sprint 1, `ended`
     2026-07-02; mission `created` 2026-07-02; operator decision on
     `<today>`.
   - `created` stays untouched.
8. **Closing message** notes that post-MVP items in sprint 2 may now
   start through `sprint-execute`, and that any MVP item re-opening
   reverts `mvp_status` to `in_progress` per the regression path.
