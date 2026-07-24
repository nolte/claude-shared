---
review-type: agent-review
target: "plugins/nolte-engineering/agents/integration-test-reviewer.md"
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

# Agent Review: integration-test-reviewer

## Scope

Target: `plugins/nolte-engineering/agents/integration-test-reviewer.md` (frontmatter + full body; no external referenced assets).
Specs applied: `agent-management`, `skill-vs-agent`, `review-plan`, `agent-review` (revisions recorded in frontmatter).
Narrowing: none — full check set.
Read-only classification: **review-and-repair**, explicitly the carve-out `agent-management` §Tool access names ("an agent whose single responsibility is a review that *includes* applying the fix"); the read-only tool bans therefore don't apply to its `Edit` / `Bash` grant, and the body states the mode explicitly.
Model-choice check applied under the widened rule (PR #480): `model: sonnet` with an explicit `## Model pin` rationale — conformant.
Explicitly out of scope: runtime behavior, Vale/markdown style.

## Summary

- Critical: 0
- Warning: 1
- Suggestion: 0
- Info: 0

Go/no-go: CONDITIONAL — passes once the Bash/write documentation stops describing a scaffolding agent.
Next concrete action: author reconciles the boilerplate `## Bash justification` block with this agent's actual mandate.

## Findings

### Warning

- [ ] [agent-management.tool-access] The `## Bash justification` block is scaffolding-agent boilerplate and contradicts the rest of the file: it claims the test command runs "against the tests this agent just **wrote** or repaired" and attaches a **Write preconditions** paragraph about "scaffolding infrastructure" and "the tier's declared test tree", while the agent declares no `Write` and §Writes vs researches restricts `Bash` to "read-only checks (collection and syntax)". `agent-management` §Tool access requires the section to name the commands the agent invokes **and their effects**, so an inaccurate section is a SHOULD failure.
      Where: `plugins/nolte-engineering/agents/integration-test-reviewer.md:38-42` versus `:63` (§Writes vs researches) and `:5` (`tools:` without `Write`).
      Fix: rewrite the section to this agent's real surface — `Bash` verifies the repaired tests still collect and run, plus read-only `git status` / `git diff`; replace the write-precondition paragraph with an edit-precondition one (the tests and the seam under test exist; edits touch only existing test files, never new ones and never the seam).
      Verify: the section no longer says "wrote", "scaffolding", or "writes touch"; it agrees with §Writes vs researches and with the `Write`-free `tools:` list.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
