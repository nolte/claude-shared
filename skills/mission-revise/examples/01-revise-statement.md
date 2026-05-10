# Example 01 — Operation A: revise `mission_statement` and `audiences`

The operator wants to refine the mission statement (sharper "what for
whom" wording) and add a newly-identified audience to the existing
mission file. Exercises operation A's two most common surfaces: a
prose edit on `mission_statement` and a structural change on
`audiences` that demands a new per-audience paragraph in
`## Audiences`. `mvp_status` stays at `in_progress`, so branch C does
**not** apply.

## Input prompt

> Überarbeite die Mission: das Statement soll präziser klären, dass
> wir Plugin-Autoren bedienen, und füge `plugin-reviewers` als
> zusätzliche Audience hinzu.

## Input files

`project/mission.md` (current state — relevant excerpts only):

```yaml
---
mission_statement: "Provide a stable scaffolding layer for Claude Code
  plugin authors so that new skills land in production within one
  sprint."
mvp_status: in_progress
audiences: [plugin-authors]
verifies_via: F-7:acceptance-2
relevant_outcomes: [O-1, O-3]
time_bound: { kind: mvp_completion }
created: 2026-02-14
revised_at: 2026-04-22
---

## Statement

Provide a stable scaffolding layer for Claude Code plugin authors so
that new skills land in production within one sprint.

## Audiences

### plugin-authors

Plugin authors are engineers building Claude Code plugins for the
nolte portfolio. The MVP delivers them … (existing paragraph).

## Verification

Acceptance criterion `F-7:acceptance-2` — "A freshly-scaffolded skill
passes `task lint` and `task test` without manual edits."

## Source

- 2026-02-14 — created.
- 2026-04-22 — `defining → in_progress` after R-2 entered `status: active`.
```

`project/audiences.md` lists both `plugin-authors` and
`plugin-reviewers` (the latter was added in a previous audience-revision
sweep but not yet referenced from the mission). `project/goals.md`
resolves `O-1` and `O-3`. `project/features/F-7.md` exists with
`acceptance-2` checked.

## Expected behaviour

1. **Preconditions pass.** Skill confirms it is in a git work tree,
   `project/mission.md` parses (eight frontmatter fields, four body
   sections in declared order), `project/audiences.md` and
   `project/goals.md` are reachable, and reads `project/roadmap.md` plus
   `project/sprints/` so cross-spec invariants are available even
   though branch B isn't selected.
2. **Operation routing.** Skill asks which of A / B / C is intended;
   the user picks A. Skill enumerates which fields they want to
   change — `mission_statement` and `audiences` — and walks them one
   at a time.
3. **`mission_statement` walk-through.** Skill re-applies the Specific
   check: the new statement must still name "what" and "for whom".
   The proposed wording (e.g. *"Provide a stable scaffolding layer
   that lets Claude Code plugin authors and plugin reviewers ship a
   new skill — built, reviewed, and merged — within one sprint."*)
   names both audiences explicitly; skill confirms neither audience
   identifier from the new `audiences` list is dropped.
4. **`audiences` walk-through.** Skill resolves
   `plugin-reviewers` against `project/audiences.md` (it exists), then
   **gathers a per-audience paragraph** with the operator (three to
   five sentences, naming the audience and what the MVP delivers to
   *that* audience specifically). Skill rejects an empty paragraph and
   rejects any wording that re-uses the `plugin-authors` text
   verbatim.
5. **Bidirectional sync check.** After the walk, skill verifies that
   `audiences: [plugin-authors, plugin-reviewers]` matches the body's
   `## Audiences` headings exactly — both surfaces in lockstep, no
   stragglers either way.
6. **No `mvp_status` change.** Skill explicitly leaves `mvp_status: in_progress`
   untouched and confirms branch C does **not** trigger (current
   status is not `stabilised`).
7. **`revised_at` bump.** Skill sets `revised_at: 2026-05-10`, leaves
   `created: 2026-02-14` untouched.
8. **Diff presentation and write.** Skill shows the frontmatter delta
   (`mission_statement`, `audiences`, `revised_at`) plus the body
   delta (new `## Statement` prose, new `### plugin-reviewers`
   subsection) in German per the operator's language, iterates until
   approval, then writes `project/mission.md` in place. No `## Source`
   entry is appended for an operation-A revision (only B and C touch
   `## Source`).
9. **Closing message** confirms the path and reminds the operator
   that `mvp_status` is unchanged and that adding the new audience to
   the mission does **not** retroactively change feature acceptance —
   `F-7:acceptance-2` still verifies the MVP.
