# Example 03 — Operation B: stabilisation gate **blocks** `achieved → stabilised`

The operator believes the MVP is stabilised and asks for the flip,
but the subsequent sprint (the one whose `number` is
`MVP-closing-sprint-number + 1`) has not yet reached `status: closed`.
Exercises the spec's hard rule that the gate's "one full subsequent
sprint" condition cannot be silently inferred — the skill must report
the gate as unsatisfied and refuse to write.

## Input prompt

> Wir sind durch die Stabilisierungsphase — flippe `mvp_status` von
> `achieved` auf `stabilised`.

## Input files

`project/mission.md` (current state — relevant excerpts only):

```yaml
---
mission_statement: "Provide a stable scaffolding layer for Claude Code
  plugin authors so that new skills land in production within one
  sprint."
mvp_status: achieved
audiences: [plugin-authors, plugin-reviewers]
verifies_via: F-7:acceptance-2
relevant_outcomes: [O-1, O-3]
time_bound: { kind: mvp_completion }
created: 2026-02-14
revised_at: 2026-05-10
---

## Source

- 2026-02-14 — created.
- 2026-04-22 — `defining → in_progress` after R-2 entered `status: active`.
- 2026-05-02 — added `plugin-reviewers` audience.
- 2026-05-10 — in_progress → achieved (R-2, R-5, R-9 all done; F-7:acceptance-2 checked).
```

`project/roadmap.md` confirms `R-2`, `R-5`, `R-9` (every
`mvp: true` item) at `status: done`. The MVP-closing sprint is
`project/sprints/0006-cross-skill-consistency.md` (`status: closed`,
carried the final `mvp: true` item R-9). `project/sprints/`
**also** contains `0007-post-mvp-polish.md` with
`status: active` — the planned post-MVP sprint is in flight, not yet
closed. No defect-fix feature against an MVP item is currently
`in_progress`.

## Expected behaviour

1. **Preconditions pass.** Skill confirms it is in a git work tree,
   `project/mission.md` parses, audience and goals artefacts resolve,
   and reads `project/roadmap.md` plus the full contents of
   `project/sprints/`.
2. **Operation routing.** Operator selects B. Skill enumerates the
   legal targets from `achieved`: `stabilised` (forward) is the only
   option (regression `→ in_progress` requires an actual MVP item to
   re-open; none has). Operator picks `stabilised`.
3. **Stabilisation gate verification — condition 1 (every
   `mvp: true` item is `status: done`).** Skill walks the roadmap and
   confirms `R-2`, `R-5`, `R-9` are all `done`. Inline evidence is
   shown to the operator. Condition met.
4. **Stabilisation gate verification — condition 2 (MVP-closing
   sprint is `status: closed`).** Skill identifies sprint 6 as the
   MVP-closing sprint (it carried the *final* `mvp: true` transition,
   R-9), reads `project/sprints/0006-cross-skill-consistency.md`, and
   confirms `status: closed`. Condition met.
5. **Stabilisation gate verification — condition 3 (one full
   subsequent sprint closed without regression) — FAILS.** Skill
   walks by `number`, **not** by `ended` date, and looks for the
   sprint whose `number` is `6 + 1 = 7`.
   `project/sprints/0007-post-mvp-polish.md` exists but is
   `status: active`. The sprint is **not** `closed`, so the
   subsequent-sprint condition is unsatisfied. Skill does **not**
   accept "we're nearly done" or any operator framing as a substitute
   — the spec's "never silently infer satisfaction" rule applies.
6. **Block the flip with a verbatim error.** Skill emits a
   structured-message in German (operator's language) along the lines
   of:
   > Stabilisierungs-Gate **nicht erfüllt**: Sprint 7
   > (`0007-post-mvp-polish`) ist `status: active`, nicht `closed`.
   > Die Bedingung "ein vollständiger Folge-Sprint ist ohne
   > Regression geschlossen" verlangt `status: closed` (oder
   > `cancelled` mit `## Review notes`-Begründung "no-fault-of-MVP").
   > Der Flip nach `stabilised` wird verweigert, bis Sprint 7 in den
   > Status `closed` übergeht.
   Skill cites the spec rule and does not present a "force-write"
   override.
7. **Stabilisation gate verification — condition 4 (no defect-fix
   work in flight) is reported.** Even though condition 3 already
   blocks, the skill still notes that condition 4 currently passes
   (no feature against an `mvp: true` item is `status: in_progress`)
   so the operator gets a complete gate readout for the audit trail.
8. **No write.** `project/mission.md` is left untouched.
   `mvp_status` stays `achieved`. `revised_at` is **not** bumped (no
   mutation occurred). No entry is appended to `## Source`.
9. **Closing message** confirms zero file mutations, restates the
   single failing condition (sprint 7 not `closed`), and tells the
   operator to re-invoke this skill **after**
   `0007-post-mvp-polish.md` reaches `status: closed` via
   `sprint-review`. Skill explicitly does **not** offer to wait,
   poll, or auto-retry — the next attempt is operator-initiated.
