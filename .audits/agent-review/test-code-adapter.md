---
review-type: agent-review
target: "plugins/nolte-engineering/agents/test-code-adapter.md"
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

# Agent Review: test-code-adapter

## Scope

Target: `plugins/nolte-engineering/agents/test-code-adapter.md` (frontmatter + full body; no external referenced assets).
Specs applied: `agent-management`, `skill-vs-agent`, `review-plan`, `agent-review` (revisions recorded in frontmatter).
Narrowing: none — full check set.
Read-only classification: **write-capable** (edits production code in place); the read-only tool bans don't apply and the neutral `## Bash justification` heading is the correct form.
Model-choice check applied under the widened rule (PR #480): `model: opus` with an explicit `## Model pin` rationale (holding the no-cheating invariant together with the simplest-change rule) — conformant.
Explicitly out of scope: runtime behavior, Vale/markdown style.

## Summary

- Critical: 0
- Warning: 1
- Suggestion: 0
- Info: 0

Go/no-go: CONDITIONAL — passes once the write-effect documentation describes this agent's real write surface.
Next concrete action: author replaces the tier-scaffolding boilerplate with the production-code adaptation contract.

## Findings

### Warning

- [ ] [agent-management.tool-access] The `## Bash justification` block is boilerplate carried over from the tier generators and misdescribes this agent's write surface in both directions: it says the test command runs "against the tests this agent just wrote or repaired" (this agent adapts **production** code and hard rule 5 forbids editing an existing test), and its **Write preconditions** paragraph claims "writes touch only the tier's declared test tree" — the opposite of §Writes vs researches, which has the agent editing production code in place. `agent-management` §Tool access requires the section to name the commands and **their effects**, and its acceptance criteria require write targets and preconditions to be documented accurately.
      Where: `plugins/nolte-engineering/agents/test-code-adapter.md:41-45` versus `:65` (§Writes vs researches) and `:91` (hard rule 5).
      Fix: rewrite the section for this agent — `Bash` re-runs the affected tests to verify green-with-no-regression plus read-only `git status` / `git diff`; write preconditions become "a confirmed real failure with its evidence and a failing case that reproduces it exist; writes touch the production code under test, plus at most a new failing regression case, never an existing test".
      Verify: the section no longer claims writes are confined to the test tree; it agrees with §Writes vs researches and with hard rules 1 and 5.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
