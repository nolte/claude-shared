---
review-type: agent-review
target: "plugins/nolte-engineering/agents/test-case-extractor.md"
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

# Agent Review: test-case-extractor

## Scope

Target: `plugins/nolte-engineering/agents/test-case-extractor.md` (frontmatter + full body; no external referenced assets).
Specs applied: `agent-management`, `skill-vs-agent`, `review-plan`, `agent-review` (revisions recorded in frontmatter).
Narrowing: none — full check set.
Read-only classification: **write-capable** (writes test-case documents); the read-only tool bans don't apply. `Bash` is deliberately absent, so no shell justification is required, and the dedicated `## Write preconditions` section documents the write targets and their preconditions as `agent-management`'s acceptance criterion requires.
Model-choice check applied under the widened rule (PR #480): `model: sonnet` with an explicit `## Model pin` rationale — conformant.
Explicitly out of scope: runtime behavior, Vale/markdown style.

## Summary

- Critical: 0
- Warning: 0
- Suggestion: 1
- Info: 0

Go/no-go: PASS
Next concrete action: author narrows one `dont_use_when` entry to the artefact that actually owns the excluded work.

## Findings

### Suggestion

- [ ] [skill-agent-catalog.use-case-metadata] The first `dont_use_when` entry bundles three excluded activities — "run the test suite, classify failures, or fix test code" — behind a single alternative (`quality-gate`), but only the first belongs to `quality-gate`: failure classification is `test-result-analyzer`'s and test repair is the tier reviewers'. A reader routed by that entry lands on the wrong artefact for two of the three cases.
      Where: `plugins/nolte-engineering/agents/test-case-extractor.md:15-16`.
      Fix: narrow the situation text to "you want to run the test suite" so the entry matches its `quality-gate` alternative; the `description`'s own negative triggers already carry the rest.
      Verify: the entry names only the run-the-suite case; `python3 scripts/validate_skills.py` stays green.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
