---
review-type: agent-review
target: "agents/mermaid-diagram-reviewer.md"
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

# Agent Review: mermaid-diagram-reviewer

## Scope

Target: `agents/mermaid-diagram-reviewer.md` (frontmatter + full body; no external referenced assets).
Specs applied: `agent-management`, `skill-vs-agent`, `review-plan`, `agent-review` (revisions recorded in frontmatter).
Narrowing: none — full review in the `agent-review` §Review procedure order (frontmatter → description/triggers → distribution → model → tools/scope → prompt structure → rationale → referenced assets → duplicate-prevention → Info).
Tool-use convention applied: a declared tool counts as used when the body names it in a procedure step or states it as the working method; a tool never named anywhere in the body is recorded as dead permission per `agent-review` §Tool-scope checks.
Model-form rule applied at the widened revision — alias, full model ID, and `inherit` are all conformant.
Explicitly out of scope: runtime behaviour of the agent, Vale/markdown style (agent files aren't Vale-gated), and the dispatching skill's own conformance.
Read-only classification: read-only; no `Bash`, no write tools.
Tool-use: `Grep` is stated as the working method in the rationale section ("greps for Mermaid fences"), so the declared-vs-used check passes.
Model check: `model` absent — the agent inherits the caller's model; the MAY-Info wasn't raised.

## Summary

- Critical: 0
- Warning: 0
- Suggestion: 1
- Info: 1

Go/no-go: PASS — no Critical or Warning findings.
Next concrete action: Make the severity vocabulary internally consistent across the three places that declare it.

## Findings

### Suggestion

- [ ] [review-plan.Severity scale] The findings block's `severity:` enum offers all four canonical levels, but the Summary table has no `Suggestion` column and `## Severity assignment` defines only three — a `Suggestion`-severity finding has nowhere to be counted or explained.
      Where: `agents/mermaid-diagram-reviewer.md:72` (enum) against `:56-62` (Summary table) and `:157-161` (`## Severity assignment`).
      Fix: Add the `Suggestion` column to the Summary table and a matching `Suggestion` line to `## Severity assignment`.
      Verify: All three declarations of the severity vocabulary list the same levels.

### Info

- [ ] [agent-management.Description contract] The negative trigger against the twin `diagram-opportunity-reviewer` lives in `dont_use_when` and the body rather than in `description`, which is acceptable because the twin's own `description` carries the delimitation ("Twin of `mermaid-diagram-reviewer`") and the tight-chain SHOULD prefers not to repeat routing tokens.
      Where: `agents/mermaid-diagram-reviewer.md:3` and `:19-20`, against `agents/diagram-opportunity-reviewer.md:3`.
      Fix: n/a (deliberate design).
      Verify: n/a.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
