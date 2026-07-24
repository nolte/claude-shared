---
review-type: agent-review
target: "plugins/nolte-engineering/agents/webview-ui-expert.md"
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

# Agent Review: webview-ui-expert

## Scope

Target: `plugins/nolte-engineering/agents/webview-ui-expert.md` (frontmatter + body + the two `${CLAUDE_PLUGIN_ROOT}`-relative asset sets it falls back to).
Specs applied: `agent-management`, `skill-vs-agent`, `review-plan`, `agent-review` (revisions recorded in frontmatter).
Narrowing: none — full check set.
Read-only classification: read-only deep reviewer holding `Bash` under the narrow exception; the `## Read-only Bash justification` section limits it to exactly one command (`git rev-parse --is-inside-work-tree`) and forbids everything else — the otherwise-`Critical` finding is downgraded and not raised.
Model-choice check applied under the widened rule (PR #480): `model: sonnet`, rationale stated inline in the rationale section — conformant.
Referenced-asset check: both plugin-relative fallbacks resolve — `plugins/nolte-engineering/skills/webview-ui-optimize/references/spec/webview-ui-optimization.md` and `.../references/research-notes/{performance,security,accessibility,i18n,ux}.md` all exist. The `${CLAUDE_PLUGIN_ROOT}` reference is correct for a `distribution: plugin` agent (the project-distribution warning doesn't apply).
Body length: 183 lines excluding frontmatter — inside the ~200-line soft target.
Explicitly out of scope: runtime behavior, Vale/markdown style, and the `webview-ui-optimize` skill's own conformance.

## Summary

- Critical: 0
- Warning: 0
- Suggestion: 1
- Info: 1

Go/no-go: PASS
Next concrete action: author rewords the ambiguous-input branch so it doesn't promise an interactive turn.

## Findings

### Suggestion

- [ ] [skill-vs-agent.hybrid-pattern] The ambiguous-input branch says "ask once for a target and stop" — an agent runs in an isolated subagent context with no stable channel for surfacing a question mid-flow, so the wording promises an interaction the runtime can't deliver. The `and stop` clause means the intent is already the conformant one (return and let the caller re-dispatch); only the phrasing reads interactive.
      Where: `plugins/nolte-engineering/agents/webview-ui-expert.md:84`.
      Fix: reword to return-shaped prose — "return a request for a concrete target and stop; don't invent one" — so the contract matches what a subagent can actually do.
      Verify: the line no longer describes asking the user mid-run; `dont_use_when` and the caller-follow-ups section still route re-dispatch through `webview-ui-optimize`.

### Info

- [ ] [agent-review.plugin-distribution] The agent is the only one in this batch that reads bundled, plugin-co-located assets, and it does so correctly: `${CLAUDE_PLUGIN_ROOT}`-relative paths under `distribution: plugin`, with a repo-local `spec/` tree preferred first and a documented degradation ("research notes unavailable") that never suppresses a spec-grounded finding.
      Where: `plugins/nolte-engineering/agents/webview-ui-expert.md:91-92`.
      Fix: n/a (observation — conformant).
      Verify: n/a.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
