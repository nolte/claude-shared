---
review-type: agent-review
target: "plugins/nolte-engineering/agents/frontend-code-reviewer.md"
target-kind: agent
specs-applied:
  - slug: agent-management
    revision: "94231d2ec957b4af1a3fb7feba72188b19b64504"
  - slug: skill-vs-agent
    revision: "66d6513791380914c73b78c360b5740c29ef13ba"
  - slug: review-plan
    revision: "e75ffbbafaf33cd55ae46dda966894add3ae01e4"
  - slug: agent-review
    revision: "94231d2ec957b4af1a3fb7feba72188b19b64504"
repo-revision: "f46a3ef2ade001cadf956779a062992e8795c93a"
created: "2026-08-21"
status: open
---

# Agent Review: frontend-code-reviewer

## Scope

Target: `plugins/nolte-engineering/agents/frontend-code-reviewer.md` (181 lines, single self-contained file).
Specs applied: `agent-management`, `skill-vs-agent`, `review-plan`, `agent-review` (revisions in frontmatter).
Narrowing: none — full review.
Explicitly out of scope: runtime behavior, Vale/markdown style, the dispatching `source-code-review` skill.

Context: phase 1 of the skills-agents sweep 2026-08.

## Summary

- Critical: 0
- Warning: 0
- Suggestion: 0
- Info: 1

Go/no-go: PASS
Next concrete action: none.

## Findings

### Info

- [ ] [agent-review.duplicate-prevention] All four `dont_use_when` delimitations are one-directional: none of the four named alternatives names this agent back.
      Where: `plugins/nolte-engineering/agents/frontend-code-reviewer.md` `dont_use_when` names `frontend-usability-optimizer`, `webview-ui-expert`, `code-security-reviewer`, and `fullstack-developer`. All four exist (no ghost references), but a grep for `frontend-code-reviewer` across every plugin root returns only this file and `plugins/nolte-engineering/skills/source-code-review/SKILL.md` (its dispatcher).
      Fix: n/a for this target — this artefact carries its half, and it carries it well: the `## The UX boundary (read this before filing anything)` section states the split in prose and routes UX-class observations to `Info` rather than filing them. The missing mirrors live in non-target artefacts and are routed to the sweep's boundary matrix, where the pair is the unit of analysis.
      Verify: n/a.

## Verified conformant

- `tools: Read, Grep, Glob` — read-only invariant holds. `## Writes vs researches` states it explicitly: "You are **read-only**. `Read`, `Grep`, `Glob` serve only to discover and read code and configuration."
- `model: opus` carries a dedicated `## Model pin` section with a stated rationale (cross-file judgment; a client-side rule the server must own is only visible across files). The implausible-pin Suggestion does not apply to a cross-file review agent with a stated reason.
- `distribution: plugin` with no `hooks`, `mcpServers`, or `permissionMode`.
- No `Skill(` dispatch, no `Agent(` / `subagent_type` / `Task(` dispatch, no hard-coded absolute paths.
- Spec-anchor: cites `spec/frontend/source-code-review/`, `spec/project/source-code-review/`, `spec/project/test-falsifiability/`, `spec/claude/claim-provenance/`, `spec/claude/review-plan/`, `spec/claude/agent-management/`.
- Rationale names a dominant decisive dimension (context-window protection) plus two supporting ones, and an explicit counter-dimension (interactivity) with the reason it is outweighed.
- Output shape is stated concretely, including the finding-id scheme and the work-package cut along slice boundaries.
- Body length 181 lines against an inventory median of 149 (n=61, max 354); no line cap exists for agents.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
