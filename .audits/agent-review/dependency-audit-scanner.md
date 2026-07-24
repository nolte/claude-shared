---
review-type: agent-review
target: "plugins/nolte-engineering/agents/dependency-audit-scanner.md"
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

# Agent Review: dependency-audit-scanner

## Scope

Target: `plugins/nolte-engineering/agents/dependency-audit-scanner.md` (frontmatter, body, no external assets referenced).
Specs applied: `agent-management`, `skill-vs-agent`, `review-plan`, `agent-review` (revisions recorded in frontmatter).
Narrowing: none — full frontmatter + body review.
Model-choice check applied at the widened rule (PR #480): a model alias, a full model ID, and `inherit` are all conformant forms.
Explicitly out of scope: the agent's runtime behaviour (the artifact is reviewed, never dispatched), Vale / markdown style (not a gated path for agent files), and the dispatching skill beyond confirming the dispatch direction.

## Summary

- Critical: 1
- Warning: 1
- Suggestion: 0
- Info: 3

Go/no-go: FAIL — one open `Critical` blocks closure until the spec anchor lands.
Next concrete action: author anchors the agent to `spec/project/dependency-audit/` and adds the description's negative trigger.

## Findings

### Critical

- [ ] [spec-driven-development.artefact-spec-citation] The body cites no spec the agent implements: its only `spec/` reference is `spec/claude/agent-management/`, the authoring spec. `spec/project/dependency-audit/` owns the severity scale, the per-ecosystem auditor set, and the response model this agent hard-codes, and is referenced nowhere.
      Where: `plugins/nolte-engineering/agents/dependency-audit-scanner.md:24-54` (opening and `## Read-only Bash justification`).
      Fix: Anchor the opening to `spec/project/dependency-audit/` the way every sibling scanner in this plugin anchors to its governing spec, and route the severity scale to that spec instead of restating it as the agent's own rule.
      Verify: `grep -c 'spec/project/dependency-audit/'` on the agent file returns a non-zero count and the severity scale is attributed to the spec.

### Warning

- [ ] [agent-review.description-quality] The `description` carries no negative trigger even though overlap with the dispatching `dependency-audit` skill and with `license-check-scanner` is real enough that `dont_use_when` already records both.
      Where: `plugins/nolte-engineering/agents/dependency-audit-scanner.md:3`.
      Fix: Append one tight negative-trigger clause naming the two peers the `dont_use_when` block already lists.
      Verify: The `description` ends with a `Don't use for …` clause naming both peers, and stays the shortest description in the batch.

### Info

- [ ] [agent-management.tool-access] Read-only scanner declares `Bash`; the narrow exception applies because the body carries the required justification section, including the sanctioned advisory-database network-read class.
      Where: `plugins/nolte-engineering/agents/dependency-audit-scanner.md:37-54`.
      Fix: n/a (observation) — the section enumerates every auditor invocation and explicitly bounds the cache-fetch exception.
      Verify: n/a.
- [ ] [review-plan.severity-scale] The output shape uses the lowercase CVE ladder `critical / high / medium / low`, which `spec/project/dependency-audit/` §Severity classification mandates but which the `review-plan` editorial sub-scale carve-out does not name.
      Where: `plugins/nolte-engineering/agents/dependency-audit-scanner.md:89-104`.
      Fix: n/a (observation) — the agent follows its governing spec; reconciling the two specs is a spec change, not a reviewer's call, and the spec may need to grow the carve-out list.
      Verify: n/a.
- [ ] [agent-management.recommendations] `## Output shape` precedes `## Inputs`, `## Preconditions`, and `## Working procedure`, unlike the sibling scanners which close with the output contract.
      Where: `plugins/nolte-engineering/agents/dependency-audit-scanner.md:77-181`.
      Fix: n/a (observation) — declaring the output shape before the working method is explicitly conformant; the note records the house-style divergence only.
      Verify: n/a.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
