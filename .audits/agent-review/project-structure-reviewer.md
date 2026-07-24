---
review-type: agent-review
target: "agents/project-structure-reviewer.md"
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

# Agent Review: project-structure-reviewer

## Scope

Target: `agents/project-structure-reviewer.md` (frontmatter + full body; no external referenced assets).
Specs applied: `agent-management`, `skill-vs-agent`, `review-plan`, `agent-review` (revisions recorded in frontmatter).
Narrowing: none — full review in the `agent-review` §Review procedure order (frontmatter → description/triggers → distribution → model → tools/scope → prompt structure → rationale → referenced assets → duplicate-prevention → Info).
Tool-use convention applied: a declared tool counts as used when the body names it in a procedure step or states it as the working method; a tool never named anywhere in the body is recorded as dead permission per `agent-review` §Tool-scope checks.
Model-form rule applied at the widened revision — alias, full model ID, and `inherit` are all conformant.
Explicitly out of scope: runtime behaviour of the agent, Vale/markdown style (agent files aren't Vale-gated), and the dispatching skill's own conformance.
Read-only classification: read-only; `Read` and `Glob` only, so the read-only invariant holds by construction.
Model check: `model` absent — the agent inherits the caller's model; the MAY-Info wasn't raised.

## Summary

- Critical: 0
- Warning: 0
- Suggestion: 1
- Info: 0

Go/no-go: PASS — no Critical or Warning findings.
Next concrete action: Make the severity vocabulary internally consistent and title-case the stray token.

## Findings

### Suggestion

- [ ] [review-plan.Severity scale] The severity vocabulary is declared inconsistently: the findings enum offers all four canonical levels, the Summary table has no `Suggestion` column, `## Severity assignment` defines only three, and one surface rule writes `critical` in lowercase.
      Where: `agents/project-structure-reviewer.md:70` (enum), `:52-60` (Summary table), `:165-169` (`## Severity assignment`), `:141` (lowercase token).
      Fix: Add the `Suggestion` column plus a matching `## Severity assignment` line, and title-case the stray token.
      Verify: All declarations of the severity vocabulary agree and a grep for lowercase severity tokens in the body returns nothing.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
