# Example 03 — Refusal when `project/mission.md` already exists

A precondition-driven refusal path. `mission-define` is first-write
only; once the file exists, every subsequent edit (statement rewording,
audience addition, `mvp_status` flip, post-stabilisation rationale)
belongs to the sibling `mission-revise` skill. This example exercises
the early-stop guard and the routing message back to the operator.

## Input prompt

> Define the mission for this project — I want to reword the statement
> and flip `mvp_status` to `in_progress` because the first MVP item
> just went active.

## Input files

`project/mission.md` already exists with a valid frontmatter block:

```yaml
---
mission_statement: >
  Give portfolio maintainers a one-command path to a spec-conformant
  release for every nolte-portfolio repo.
relevant_outcomes: [O-1, O-3]
audiences: [portfolio-maintainers]
verifies_via: F-3:acceptance-2
time_bound:
  kind: mvp_completion
mvp_status: defining
created: 2026-04-22
revised_at: null
---
```

`project/goals.md`, `AUDIENCES.md`, the roadmap, and the named
verifying feature all exist and resolve cleanly. The operator's
intent — a statement reword plus a `defining → in_progress` lifecycle
flip — is one of the operations explicitly owned by `mission-revise`.

## Expected behaviour

1. **Preconditions check halts at the first failing precondition.**
   The skill confirms it sits inside a git work tree and `git` is on
   `PATH`, then immediately checks for `project/mission.md`. The file
   exists, so the skill stops here — it does **not** continue to the
   goals / audience / feature precondition checks, because those are
   irrelevant once the first-write guard has fired.
2. **No drafting work begins.** The SMART walk does not start, the
   audience artefact is not parsed, the feature menu is not built, no
   draft frontmatter is composed, and no file is written or modified.
   In particular, the existing `project/mission.md` is **not** read,
   diffed, or touched in any way by this skill.
3. **Refusal message** is returned in the operator's language and
   names the spec rule explicitly: `mission-define` is first-write
   only; `project/mission.md` already exists at `project/mission.md`
   with `created: 2026-04-22` and `mvp_status: defining`.
4. **Routing pointer to `mission-revise`** maps the operator's two
   stated intents to the correct sibling-skill operations:
   - statement reword → `mission-revise` operation A (revise the
     statement, audiences, verifying-feature pointer, or `time_bound`);
     a `revised_at` bump and a fresh `## Source` audit line will be
     written by that skill.
   - `defining → in_progress` flip → `mission-revise` operation B
     (flip `mvp_status` along the legal lifecycle), gated on at least
     one MVP roadmap item carrying `status: active`.
   The pointer names the skill by its exact identifier
   (`mission-revise`) so the operator can invoke it directly.
5. **No partial state left behind.** Because no draft was started, no
   temp files exist, no scratch frontmatter sits in the conversation,
   and the operator's next invocation of `mission-revise` runs against
   a clean working tree exactly as if `mission-define` had never been
   called.
6. **Closing message** does **not** offer to "fall through" or "do it
   anyway"; the first-write guard is a hard rule from the skill's
   `## Hard rules` section ("**Never** create `project/mission.md`
   when one already exists. First-write only.") and the spec's
   directory-layout rule ("exactly one file per project, never
   split"). Bypassing it would silently corrupt the audit trail
   (`created` would be overwritten, `## Source` history would be
   lost), so the refusal is final until the operator switches skills.
