# Example 01 — Fresh mission for a new Claude plugin project

A first-write of `project/mission.md` against a freshly bootstrapped
Claude Code plugin repo. Exercises the full SMART walk one letter at a
time, the per-audience tailoring loop with a single audience, and the
final compose-confirm-write cycle that lands the file with
`mvp_status: defining`.

## Input prompt

> Define the mission for this project.

## Input files

`project/goals.md` (excerpt — Vision plus three outcomes):

```markdown
## Vision

Give nolte-portfolio repos a single Claude-driven path to a
spec-conformant release.

## Outcomes

- **O-1** — Release notes are curated against the audience artefact
  before publish.
- **O-2** — Every release-bearing PR passes the same quality gate
  locally and in CI.
- **O-3** — Release publishing is a one-command operation that refuses
  to run when any pre-publish gate is red.
```

`AUDIENCES.md` (excerpt — single audience, `confirmed`):

```markdown
## Direct consumers

- **portfolio-maintainers** — _confirmed_ — repo maintainers who run
  the release skills end-to-end against a `develop` tip and expect a
  green publish or an actionable refusal.
```

`project/roadmap.md` resolves three items flagged `mvp: true`
(`R-1` curate-notes, `R-2` quality-gate-skill, `R-3` publish-trigger),
each with `detail: fine` and `target_sprint` set (sprints 3, 4, 5).
`project/features/release-publish-trigger.md` exists with
`acceptance-2` reading "Dispatching `release-publish.yml` succeeds when
every required check on `develop` is green and refuses with a verbatim
error otherwise." `git config user.name` returns `nolte`.
`project/mission.md` does **not** yet exist.

## Expected behaviour

1. **Preconditions pass.** The skill confirms it sits inside a git
   work tree, `git` is on `PATH`, `project/mission.md` is absent,
   `project/goals.md` parses with three `O-<n>` outcomes, the audience
   artefact is found at `AUDIENCES.md` (not hard-coded — discovered
   via the audience-identification precedent), and at least one feature
   under `project/features/` exposes a candidate `acceptance-<n>`.
2. **Inputs read.** The skill loads the three outcomes (`O-1`, `O-2`,
   `O-3`), the single audience identifier `portfolio-maintainers`, the
   three `mvp: true` roadmap items, and the feature menu (with
   `release-publish-trigger.md:acceptance-2` among the choices).
3. **SMART walked one letter at a time, never batched.**
   - **Specific** — proposes a single-sentence `mission_statement`
     naming both the *what* and the *for whom*; iterates with the
     operator until the sentence resolves the audience identifier
     `portfolio-maintainers` explicitly (no "for users").
   - **Measurable** — presents the feature menu and asks the operator
     to pick exactly one `<feature-id>:acceptance-<n>` pair; the
     operator picks `F-3:acceptance-2`; the skill verifies the feature
     file and the acceptance ID both resolve.
   - **Achievable** — restates the three `mvp: true` items, confirms
     each carries `detail: fine` and a non-null `target_sprint`, and
     notes the scope (3 items across sprints 3-5) sits inside the
     "two-to-five sprints' worth" guidance; refuses to mark every
     roadmap item `mvp: true` (none requested here).
   - **Relevant** — asks which outcome IDs the mission ties to;
     operator picks `[O-1, O-3]`; both resolve in `goals.md`; the
     skill nudges that one or two is the sweet spot and proceeds.
   - **Time-bound** — offers the two legal shapes; operator picks
     `{ kind: mvp_completion }`; the skill rejects and re-prompts if
     the operator volunteers a calendar date instead.
4. **Audience walk runs once** for the single identifier
   `portfolio-maintainers`. Operator drafts a three-to-five-sentence
   paragraph naming the audience and stating what the MVP delivers to
   them specifically (a green publish or an actionable refusal). A
   bare audience name without the paragraph is refused.
5. **Compose step renders the full draft** with the eight frontmatter
   fields in declared order (`mission_statement`, `relevant_outcomes`,
   `audiences`, `verifies_via`, `time_bound`, `mvp_status: defining`,
   `created: 2026-05-10`, `revised_at: null`) plus the four required
   body sections in declared order (`## Statement` with the SMART
   five-line decomposition, `## Audiences`, `## Verification` quoting
   `acceptance-2` verbatim, `## Source` carrying `AUDIENCES.md` plus
   its last-commit SHA from `git log -n 1 --format=%H -- AUDIENCES.md`,
   the consulted `project/goals.md` path, and
   `operator: nolte via mission-define skill, commit-pending`).
6. **Confirm and write.** The full draft is presented back in the
   operator's language; only after explicit approval is
   `project/mission.md` written. No partial writes.
7. **Closing message** confirms the path, reminds the operator that
   `defining → in_progress` is owned by `mission-revise` (flipped once
   the first MVP item enters `status: active`), and that `mvp: true`
   flags on roadmap items are mutated via `roadmap-refine`, never
   inline-edited from this skill.
