---
review-type: agent-review
target: "agents/vocab-drift-scanner.md"
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

# Agent Review: vocab-drift-scanner

## Scope

Target: `agents/vocab-drift-scanner.md` (frontmatter + full body; no external referenced assets).
Specs applied: `agent-management`, `skill-vs-agent`, `review-plan`, `agent-review` (revisions recorded in frontmatter).
Narrowing: none — full review in the `agent-review` §Review procedure order (frontmatter → description/triggers → distribution → model → tools/scope → prompt structure → rationale → referenced assets → duplicate-prevention → Info).
Tool-use convention applied: a declared tool counts as used when the body names it in a procedure step or states it as the working method; a tool never named anywhere in the body is recorded as dead permission per `agent-review` §Tool-scope checks.
Model-form rule applied at the widened revision — alias, full model ID, and `inherit` are all conformant.
Explicitly out of scope: runtime behaviour of the agent, Vale/markdown style (agent files aren't Vale-gated), and the dispatching skill's own conformance.
Read-only classification: read-only (scanner, detection only), so `Bash` is assessed under the narrow exception.
Model check: `model: sonnet` is declared and justified.

## Summary

- Critical: 0
- Warning: 0
- Suggestion: 0
- Info: 1

Go/no-go: PASS — no Critical, Warning, or Suggestion findings.
Next concrete action: No rework required; close the plan.

## Findings

### Info

- [ ] [agent-management.Tool access] `Bash` on a read-only agent, downgraded from Critical to Info because the narrow exception is satisfied.
      Where: `agents/vocab-drift-scanner.md:5` and `## Read-only Bash justification` at lines 34-46.
      Fix: n/a (observation) — the section enumerates the read-only `gh api` upstream fetches plus `git ls-files`, and the rationale section explains why `Glob`/`Grep` stay undeclared.
      Verify: n/a.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
