---
review-type: agent-review
target: "agents/prose-vale-curator.md"
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

# Agent Review: prose-vale-curator

## Scope

Target: `agents/prose-vale-curator.md` (frontmatter + full body; no external referenced assets).
Specs applied: `agent-management`, `skill-vs-agent`, `review-plan`, `agent-review` (revisions recorded in frontmatter).
Narrowing: none — full review in the `agent-review` §Review procedure order (frontmatter → description/triggers → distribution → model → tools/scope → prompt structure → rationale → referenced assets → duplicate-prevention → Info).
Tool-use convention applied: a declared tool counts as used when the body names it in a procedure step or states it as the working method; a tool never named anywhere in the body is recorded as dead permission per `agent-review` §Tool-scope checks.
Model-form rule applied at the widened revision — alias, full model ID, and `inherit` are all conformant.
Explicitly out of scope: runtime behaviour of the agent, Vale/markdown style (agent files aren't Vale-gated), and the dispatching skill's own conformance.
Read-only classification: **write-capable** (rephrases prose and extends `accept.txt` via `Edit`), so the read-only tool bans don't apply and `Bash` is assessed under the write-capable clause.
Write effects are documented with goals and preconditions per the `agent-management` acceptance criterion.
Model check: `model` absent — the agent inherits the caller's model; the MAY-Info wasn't raised.

## Summary

- Critical: 0
- Warning: 1
- Suggestion: 0
- Info: 0

Go/no-go: PASS — no Critical findings.
Next concrete action: Name `Grep` at the procedure step that runs the regex heuristics.

## Findings

### Warning

- [ ] [agent-review.Tool-scope checks] `Grep` is declared but never named in any procedure step — the preconditions attribute discovery to `Read`, `Bash`, and `Glob`, so the declaration reads as dead permission.
      Where: `agents/prose-vale-curator.md:5` (declaration) against `:141` (preconditions) and `:161-169` (step 5a, where the voice-and-tone regex heuristics actually run).
      Fix: Name `Grep` in step 5a, which is the regex scan across the target files the tool performs.
      Verify: The body names `Grep` in a procedure step, so the declared-vs-used check passes in both directions.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
