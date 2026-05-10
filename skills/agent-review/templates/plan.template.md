---
review-type: agent-review
target: "agents/{{agent-name}}.md"
target-kind: agent
specs-applied:
  - slug: agent-management
    revision: "{{agent-management-sha}}"
  - slug: skill-vs-agent
    revision: "{{skill-vs-agent-sha}}"
  - slug: review-plan
    revision: "{{review-plan-sha}}"
  - slug: agent-review
    revision: "{{agent-review-sha}}"
repo-revision: "{{repo-sha}}"
created: "{{iso-date}}"
status: open
---

# Agent Review: {{agent-name}}

## Scope

Target: `agents/{{agent-name}}.md` ({{frontmatter + body + referenced-assets-summary}}).
Specs applied: `agent-management`, `skill-vs-agent`, `review-plan`, `agent-review` (revisions recorded in frontmatter).
Narrowing: {{none | frontmatter-only | tools-only | rationale-only | …}}.
Explicitly out of scope: runtime behavior of the agent, Vale/markdown style (handled by `task lint`), the orchestrating skill beyond confirming the dispatch direction.

## Summary

- Critical: {{B}}
- Warning: {{W}}
- Suggestion: {{S}}
- Info: {{I}}

Go/no-go: {{PASS | FAIL | CONDITIONAL — <condition>}}
Next concrete action: {{one-liner — typically "author addresses BLOCKERs in <area>"}}

## Findings

### Critical

- [ ] [{{spec-slug}}.{{requirement-shorthand}}] {{one-line statement of what is wrong}}.
      Where: {{file:line or section reference}}.
      Fix: {{concrete action — one line}}.
      Verify: {{how to confirm the fix — one line}}.

### Warning

- [ ] [{{spec-slug}}.{{requirement-shorthand}}] {{…}}.
      Where: {{…}}.
      Fix: {{…}}.
      Verify: {{…}}.

### Suggestion

- [ ] [{{spec-slug}}.{{requirement-shorthand}}] {{…}}.
      Where: {{…}}.
      Fix: {{…}}.
      Verify: {{…}}.

### Info

- [ ] [{{spec-slug}}.{{requirement-shorthand}}] {{…}}.
      Where: {{…}}.
      Fix: n/a (observation).
      Verify: n/a.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
