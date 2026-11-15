# Example 04 — Operation 2: retroactive-MVP exemption allows `achieved → stabilised`

A configuration repository adopted the planning suite after its core
capabilities had already shipped. Its mission wasn't written through
`mission-define`'s first-write path, which always opens a new mission at
`defining`. A portfolio backfill wrote it outside the skill instead, in
one commit together with the roadmap and sprint 0001. That backfill
recorded the MVP retroactively, so the first committed version of the
mission opened at `mvp_status: achieved` and sprint 0001 was recorded as
already `closed`. Sprint 0002 is `planned` and carries only `mvp: false`
items, so it can't start while `mvp_status` is `achieved`.

This example exercises the retroactive-MVP exemption in
`spec/project/mission/` §Stabilisation gate. The "one full subsequent
sprint" condition is waived. Every other condition is still checked
against the artefacts and their full git history, and the operator
writes the rationale.

## Input prompt

> Das MVP wurde rückwirkend erfasst — flippe `mvp_status` auf
> `stabilised`, damit Sprint 2 starten kann.

## Input files

`project/mission.md` (current state — relevant excerpts only). The
`## Source` text below is the consumer's own wording, written by the
backfill. Despite the label it uses, the backfill ran outside
`mission-define`'s first-write path:

```yaml
---
mvp_status: achieved
time_bound:
  kind: mvp_completion
created: 2026-07-02
revised_at: null
---

## Source

- **Authored by**: the `mission-define` cascade (issue
  nolte/claude-shared#262 mission-authoring backfill), 2026-07-02. The
  cascade models the minimum viable product retroactively. […] the
  roadmap records R-1 through R-3 as `status: done` and opens
  `mvp_status` at `achieved` rather than `defining`.
```

`project/roadmap.md` shows every `mvp: true` item (`R-1`, `R-2`,
`R-3`) at `status: done`. `project/sprints/0001-shared-cicd-baseline.md`
is the MVP-closing sprint (`status: closed`, `ended: 2026-07-02`,
`roadmap_items: [R-1, R-2, R-3]`).
`project/sprints/0002-verifiable-release-archives.md` is
`status: planned` and lists only `R-4` (`mvp: false`). No defect-fix
feature against an MVP item is `in_progress`.

## Expected behaviour

1. **Preconditions pass** as in example 01. The operator selects
   operation 2 and the target `stabilised`.
2. **Conditions 1 and 2 pass.** `R-1` to `R-3` are `done` and sprint 1
   is `closed`; the skill shows both inline as evidence.
3. **Condition 3: no subsequent sprint has closed.** Sprint
   `1 + 1 = 2` is `planned`, so the skill runs the exemption checks
   instead of blocking immediately:
   - **History guard.** `git rev-parse --is-shallow-repository` prints
     `false`. A `true` here would block the flip.
   - **Retroactive test.**
     `git log --follow --diff-filter=A --format=%H -- project/mission.md | tail -1`
     returns the backfill commit (say `5ffdca5`), and
     `git show 5ffdca5:project/mission.md` shows `mvp_status: achieved`.
     `## Source` says the MVP is recorded retroactively. The skill
     doesn't consult `created` or `revised_at`.
   - **Never stabilised before.**
     `git log --follow -G '^mvp_status: *stabilised' --format=%H -- project/mission.md`
     prints nothing.
   - **Scope at the time of the flip.** Sprint 2 is `planned`.
   - **No regression since closure.**
     `git log --follow --reverse --format=%H -- project/sprints/0001-shared-cicd-baseline.md`
     shows that `5ffdca5` is the oldest version with `status: closed`.
     The skill reads `project/roadmap.md` at `5ffdca5` and at every
     commit from `git log --format=%H 5ffdca5..HEAD -- project/roadmap.md`.
     It parses each item's YAML block and confirms that, by ID, `R-1`,
     `R-2`, and `R-3` never carry `status: active`.

   The skill reports condition 3 as satisfied **via the retroactive-MVP
   exemption** and lists this evidence.
4. **Condition 4 (no defect-fix work in flight) passes.**
5. **Operator confirmation.** The skill asks for an explicit "yes".
   The satisfied conditions never make the decision.
6. **Rationale gate.** The skill asks for a one-paragraph rationale
   that names the exemption, and it refuses to draft one. The operator
   supplies it.
7. **Re-verify, then write.** Immediately before writing, the skill
   re-runs every check from steps 2 to 4, as it does before any write.
   If sprint 2 had become `active` in the meantime, the write would be
   blocked. All checks still pass, and after the operator approves the
   diff the skill writes:
   - `mvp_status: achieved → stabilised`
   - `revised_at: null → <today>`
   - exactly two additions to `## Source`:
     - the one-line transition entry;
     - the operator's rationale paragraph with its evidence: sprint 1
       ended 2026-07-02, commit `5ffdca5` first added
       `project/mission.md` with `mvp_status: achieved`, and the
       operator decision date.
   - `created` stays untouched.
8. **Closing message.** It notes that R-4 and sprint 2 may now start
   through `sprint-execute`. If an MVP item re-opens later,
   `mvp_status` reverts to `in_progress`, and the exemption can't be
   used again because a committed version now carries `stabilised`.
