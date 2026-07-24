---
review-type: agent-review
target: "agents/audience-doc-author.md"
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

# Agent Review: audience-doc-author

## Scope

Target: `agents/audience-doc-author.md` (frontmatter + full body; no external referenced assets).
Specs applied: `agent-management`, `skill-vs-agent`, `review-plan`, `agent-review` (revisions recorded in frontmatter).
Narrowing: none — full review in the `agent-review` §Review procedure order (frontmatter → description/triggers → distribution → model → tools/scope → prompt structure → rationale → referenced assets → duplicate-prevention → Info).
Tool-use convention applied: a declared tool counts as used when the body names it in a procedure step or states it as the working method; a tool never named anywhere in the body is recorded as dead permission per `agent-review` §Tool-scope checks.
Model-form rule applied at the widened revision — alias, full model ID, and `inherit` are all conformant.
Explicitly out of scope: runtime behaviour of the agent, Vale/markdown style (agent files aren't Vale-gated), and the dispatching skill's own conformance.
Read-only classification: **write-capable** (drafts and refines docs in place), so the read-only tool bans don't apply and `Bash` is assessed under the write-capable clause.
Model check: `model` absent — the agent inherits the caller's model; the MAY-Info wasn't raised.

## Summary

- Critical: 0
- Warning: 0
- Suggestion: 1
- Info: 1

Go/no-go: PASS — no Critical or Warning findings.
Next concrete action: Fix the stale directional cross-reference in the working procedure.

## Findings

### Suggestion

- [ ] [agent-management.Recommendations] The working procedure's closing step points at the output contract as "the structure below", but `## Output contract` sits above it — a reader following the procedure is sent the wrong way.
      Where: `agents/audience-doc-author.md:115` against `## Output contract` at lines 70-83.
      Fix: Change the pointer to name the section explicitly (`## Output contract`, above).
      Verify: The procedure's final step resolves to the section that actually declares the output shape.

### Info

- [ ] [agent-management.Tool access] `Bash` is documented under a neutral `## Bash justification` rather than `## Read-only Bash justification`, which is the correct form for a write-capable agent.
      Where: `agents/audience-doc-author.md:42-48`.
      Fix: n/a (observation) — the section explicitly records that `task lint` isn't side-effect-free because pre-commit auto-fixers mutate tracked files.
      Verify: n/a.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
