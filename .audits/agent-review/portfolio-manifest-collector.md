---
review-type: agent-review
target: "agents/portfolio-manifest-collector.md"
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

# Agent Review: portfolio-manifest-collector

## Scope

Target: `agents/portfolio-manifest-collector.md` (frontmatter + full body; no external referenced assets).
Specs applied: `agent-management`, `skill-vs-agent`, `review-plan`, `agent-review` (revisions recorded in frontmatter).
Narrowing: none — full review in the `agent-review` §Review procedure order (frontmatter → description/triggers → distribution → model → tools/scope → prompt structure → rationale → referenced assets → duplicate-prevention → Info).
Tool-use convention applied: a declared tool counts as used when the body names it in a procedure step or states it as the working method; a tool never named anywhere in the body is recorded as dead permission per `agent-review` §Tool-scope checks.
Model-form rule applied at the widened revision — alias, full model ID, and `inherit` are all conformant.
Explicitly out of scope: runtime behaviour of the agent, Vale/markdown style (agent files aren't Vale-gated), and the dispatching skill's own conformance.
Read-only classification: read-only (collector, detection only), so `Bash` is assessed under the narrow exception.
Model check: `model: sonnet` is declared and justified.

## Summary

- Critical: 0
- Warning: 1
- Suggestion: 0
- Info: 1

Go/no-go: PASS — no Critical findings.
Next concrete action: Add the missing negative trigger to `description`.

## Findings

### Warning

- [ ] [agent-management.Description contract] `description` carries no negative trigger against `portfolio-inflight-collector`, the sibling read-only nolte-portfolio collector — the two are the most confusable pair in this plugin's agent surface and neither one names the other.
      Where: `agents/portfolio-manifest-collector.md:3`.
      Fix: Append a short `Don't use for …` cross-reference to `portfolio-inflight-collector`.
      Verify: `description` names the peer; the reciprocal fix lands on `portfolio-inflight-collector` in the same batch.

### Info

- [ ] [agent-management.Tool access] `Bash` on a read-only agent, downgraded from Critical to Info because the narrow exception is satisfied.
      Where: `agents/portfolio-manifest-collector.md:5` and `## Read-only Bash justification` at lines 38-48.
      Fix: n/a (observation) — the section enumerates the read-only `gh api` calls and forbids every mutating verb.
      Verify: n/a.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
