# Dispatch matching: resolving a specialist for a work package

Operation 5 carries the rules. This file carries the trap that makes step 1 fail
silently, and the worked anchors for step 2 that must never become a lookup table.

## The glob trap (step 1)

A bare `skills/*/SKILL.md` glob that omits `${CLAUDE_PLUGIN_ROOT}` **silently misses
every plugin-distributed specialist** when this skill runs inside a consumer
repository. The candidate set then looks small and plausible, and the run falls
through to the generalist for packages a shipped specialist would have handled.

Glob all four roots, every run:

- `${CLAUDE_PLUGIN_ROOT}/skills/*/SKILL.md` and `${CLAUDE_PLUGIN_ROOT}/agents/*.md` —
  where the `nolte-shared` specialists live in a consumer repo
- the consumer project's own `skills/*/SKILL.md` and `agents/*.md`
- `~/.claude/agents/*.md` for the project-distributed half

This is the same `${CLAUDE_PLUGIN_ROOT}` rule the portfolio applies to bundled
scripts.

## Worked anchors for matching (step 2)

**Read these as examples of the reasoning, never as a table to look up.** Matching is
by the package's stated responsibility against a candidate's `description:` line,
re-resolved from the runtime inventory each run. A specialist added since this file
was written must be reachable, and a specialist named here that no longer exists must
not be dispatched.

| Package shape | Reasoning that finds the specialist |
|---|---|
| `spec-change` | whichever skill's description names spec authoring (today: the `spec` skill) |
| documentation | whichever agent names an audience-targeted documentation responsibility |
| feature-shaped | whichever skill names roadmap-item decomposition (today: `feature-decompose`) |
| `security` | **not a single dispatch** — follows the audit → fix → verify chain in operation 6 |

If you find yourself matching on a specialist's *name* rather than on what its
description says it does, the match is wrong even when the name looks right.

## When nothing matches

That's a portfolio gap, not a reason to improvise. Operation 5 step 3 carries the
rule (`continuous-improvement` §Portfolio gap closure, the three-recurrence
threshold, and the explicit "no matching specialised agent — generalist remediation"
note the pull request must record).
