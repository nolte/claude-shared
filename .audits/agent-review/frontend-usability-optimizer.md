---
review-type: agent-review
target: "plugins/nolte-engineering/agents/frontend-usability-optimizer.md"
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

# Agent Review: frontend-usability-optimizer

## Scope

Target: `plugins/nolte-engineering/agents/frontend-usability-optimizer.md` (frontmatter, body, no external assets referenced).
Specs applied: `agent-management`, `skill-vs-agent`, `review-plan`, `agent-review` (revisions recorded in frontmatter).
Narrowing: none — full frontmatter + body review.
Model-choice check applied at the widened rule (PR #480): a model alias, a full model ID, and `inherit` are all conformant forms.
Explicitly out of scope: the agent's runtime behaviour (the artifact is reviewed, never dispatched), Vale / markdown style (not a gated path for agent files), and the dispatching skill beyond confirming the dispatch direction.

## Summary

- Critical: 0
- Warning: 2
- Suggestion: 0
- Info: 1

Go/no-go: CONDITIONAL — both warnings land with this plan.
Next concrete action: author aligns the `Bash` envelope and anchors the checklist to the governing frontend spec.

## Findings

### Warning

- [ ] [agent-management.tool-access] The `## Bash justification` section names the repository's build and test commands (bundler build, unit/a11y test runners), while `## Writes vs. researches`, Step 4, and Hard rule 8 all confine `Bash` to the project's type checker and linter in check mode.
      Where: `plugins/nolte-engineering/agents/frontend-usability-optimizer.md:51` versus :63, :126 and :163.
      Fix: Rewrite the section so the commands it names are the ones the procedure actually runs.
      Verify: The section, `## Writes vs. researches`, Step 4, and Hard rule 8 describe the same `Bash` envelope.
- [ ] [skill-vs-agent.duplicate-prevention] The inlined usability checklist covers accessibility (WCAG 2.x AA), i18n, and UX ground that `spec/frontend/webview-ui-optimization/` owns and that the peer agent `webview-ui-expert` grades against, but the body names neither the spec nor the overlap — so the split between the writing optimizer and the read-only reviewer rests on the `description` alone.
      Where: `plugins/nolte-engineering/agents/frontend-usability-optimizer.md:104-123` (`#### Stack-agnostic usability checklist`).
      Fix: Name `spec/frontend/webview-ui-optimization/` in the body as the spec that governs the same ground, state that it binds where the spec tree is present, and keep the inlined checklist as the consumer-install fallback.
      Verify: The body cites the spec and states the precedence order, matching how the E2E agents frame their own inlined fallback.

### Info

- [ ] [agent-review.subagent-boundary] Hard rule 11 is the only body text a mechanical `Skill(` / `Agent(` dispatch grep matches; it is a prohibition, not an invocation.
      Where: `plugins/nolte-engineering/agents/frontend-usability-optimizer.md:166`.
      Fix: n/a (observation) — recorded so a later mechanical sweep does not misread the hit as a `Critical`.
      Verify: n/a.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
