---
review-type: skill-review
target: "skills/{{skill-name}}/SKILL.md"
target-kind: skill
specs-applied:
  - slug: skill-management
    revision: "{{skill-management-sha}}"
  - slug: skill-vs-agent
    revision: "{{skill-vs-agent-sha}}"
  - slug: review-plan
    revision: "{{review-plan-sha}}"
  - slug: skill-review
    revision: "{{skill-review-sha}}"
repo-revision: "{{repo-sha}}"
created: "{{iso-date}}"
status: open
---

# Skill Review: {{skill-name}}

## Scope

Target: `skills/{{skill-name}}/` ({{SKILL.md + referenced-files-summary}}).
Specs applied: `skill-management`, `skill-vs-agent`, `review-plan`, `skill-review` (revisions recorded in frontmatter).
Validator: {{validator-name}}@{{validator-version}}
<!-- If the external skill-structure validator isn't provisioned in this repository, replace the line above with: "Validator: override — <one-line justification anchored in another spec or a documented project decision>" per `skill-review` §Checks derived from external skill-structure validation. -->
Narrowing: {{none | frontmatter-only | rationale-only | …}}.
Explicitly out of scope: runtime behavior of the skill, Vale/markdown style (handled by `task lint`), dispatched agents beyond confirming the orchestration direction.

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
