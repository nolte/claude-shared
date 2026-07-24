---
review-type: agent-review
target: "plugins/nolte-engineering/agents/integration-test-generator.md"
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

# Agent Review: integration-test-generator

## Scope

Target: `plugins/nolte-engineering/agents/integration-test-generator.md` (frontmatter + full body; no external referenced assets).
Specs applied: `agent-management`, `skill-vs-agent`, `review-plan`, `agent-review` (revisions recorded in frontmatter).
Narrowing: none — full check set.
Read-only classification: **write-capable** scaffolding agent; the read-only tool bans don't apply and the neutral `## Bash justification` heading is the correct form.
Model-choice check applied under the widened rule (PR #480): `model: opus` with an explicit `## Model pin` rationale — conformant.
Duplicate-prevention: the four sibling tier generators (`unit`, `component`, `contract`, `e2e`) share this agent's shape by design; each is delimited by its own tier spec and named in the others' negative triggers, so the overlap is a deliberate per-tier split, not a duplicate.
Explicitly out of scope: runtime behavior, Vale/markdown style.

## Summary

- Critical: 0
- Warning: 0
- Suggestion: 1
- Info: 0

Go/no-go: PASS
Next concrete action: author tightens one boilerplate clause in the Bash justification.

## Findings

### Suggestion

- [ ] [agent-management.tool-access] The `## Bash justification` block is shared boilerplate across the tier generators and reviewers and says the test command runs "against the tests this agent just wrote **or repaired**"; this agent never repairs (repair is `integration-test-reviewer`'s mandate), so the section over-states the command's effect surface.
      Where: `plugins/nolte-engineering/agents/integration-test-generator.md:40`.
      Fix: drop the `or repaired` clause so the justification names only this agent's own write effect.
      Verify: `grep -n 'or repaired' <file>` returns nothing; the section still names the test command and the read-only git introspection.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
