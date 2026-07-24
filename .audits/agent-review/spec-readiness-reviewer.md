---
review-type: agent-review
target: "agents/spec-readiness-reviewer.md"
target-kind: agent
specs-applied:
  - slug: agent-management
    revision: "92086e1803ec5667da892807749636461de55b39"
  - slug: skill-vs-agent
    revision: "92086e1803ec5667da892807749636461de55b39"
  - slug: review-plan
    revision: "e75ffbbafaf33cd55ae46dda966894add3ae01e4"
  - slug: agent-review
    revision: "e75ffbbafaf33cd55ae46dda966894add3ae01e4"
repo-revision: "e75ffbbafaf33cd55ae46dda966894add3ae01e4"
created: "2026-07-24"
status: open
---

# Agent Review: spec-readiness-reviewer

## Scope

Target: `agents/spec-readiness-reviewer.md` (frontmatter + full body; no external referenced assets).
Specs applied: `agent-management`, `skill-vs-agent`, `review-plan`, `agent-review` (revisions recorded in frontmatter).
Narrowing: none — full review in the `agent-review` §Review procedure order (frontmatter → description/triggers → distribution → model → tools/scope → prompt structure → rationale → referenced assets → duplicate-prevention → Info).
Tool-use convention applied: a declared tool counts as used when the body names it in a procedure step or states it as the working method; a tool never named anywhere in the body is recorded as dead permission per `agent-review` §Tool-scope checks.
Model-form rule applied at the widened revision — alias, full model ID, and `inherit` are all conformant.
Explicitly out of scope: runtime behaviour of the agent, Vale/markdown style (agent files aren't Vale-gated), and the dispatching skill's own conformance.
Read-only classification: read-only (verbs audit / review / report), so the read-only tool bans apply and `Bash` is assessed under the narrow exception.
Model check: `model: sonnet` is declared and justified; the MAY-Info for an absent model doesn't apply.

## Summary

- Critical: 0
- Warning: 1
- Suggestion: 0
- Info: 2

Go/no-go: PASS — no Critical findings; the single Warning is a body-length SHOULD.
Next concrete action: Body-length Warning deferred to #460; no rework needed on this agent.

## Findings

### Warning

- [ ] [agent-management.Recommendations] System-prompt body is 274 lines, past the ~200-line soft target the spec names.
      Where: `agents/spec-readiness-reviewer.md:33-305` (body after the frontmatter fence).
      Fix: Tighten prose — `## Hard rules` largely restates `## Scope and boundaries` "You don't" plus the per-phase classification tables.
      Verify: Body line count (total minus frontmatter) is at or near 200.
      → deferred: <https://github.com/nolte/claude-shared/issues/460> (prose-trimming a working agent changes behaviour-bearing text; it belongs in a focused per-agent change, not a bulk edit inside a 20-agent review batch)

### Info

- [ ] [agent-management.Tool access] `Bash` on a read-only agent, downgraded from Critical to Info because the narrow exception is satisfied.
      Where: `agents/spec-readiness-reviewer.md:5` and `## Read-only Bash justification` at lines 46-54.
      Fix: n/a (observation) — the section names the exact `git rev-parse` subset and forbids mutation.
      Verify: n/a.
- [ ] [agent-management.Model selection] `model: sonnet` is pinned and justified in the rationale section, satisfying the SHOULD.
      Where: `agents/spec-readiness-reviewer.md:6` and the `Model pin (sonnet)` bullet at line 43.
      Fix: n/a (observation).
      Verify: n/a.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
