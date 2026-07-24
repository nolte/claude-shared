---
review-type: agent-review
target: "plugins/nolte-engineering/agents/kpi-signal-scanner.md"
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

# Agent Review: kpi-signal-scanner

## Scope

Target: `plugins/nolte-engineering/agents/kpi-signal-scanner.md` (frontmatter + full body; no external referenced assets).
Specs applied: `agent-management`, `skill-vs-agent`, `review-plan`, `agent-review` (revisions recorded in frontmatter).
Narrowing: none — full check set.
Read-only classification: read-only detection scanner; `tools` is `Read, Glob, Grep` — no write or execution tool, so no `Bash` exception is needed and the body's "not a `Bash` `find`" instruction actively enforces the dedicated-tool preference.
Model-choice check applied under the widened rule (PR #480): `model: sonnet`, rationale stated inline as a bullet in the rationale section rather than in a `## Model pin` heading — the spec requires a stated rationale, not a specific heading, so this is conformant.
Companion `skill-review`: the dispatching `kpi-derive` skill is out of this plan's scope and unreviewed at this revision.
Explicitly out of scope: runtime behavior, Vale/markdown style.

## Summary

- Critical: 0
- Warning: 0
- Suggestion: 1
- Info: 1

Go/no-go: PASS
Next concrete action: author drops the unresolvable delimitation clause from the `description`.

## Findings

### Suggestion

- [ ] [agent-management.description-contract] The `description`'s final negative trigger — "or scan Dockerfiles/dependencies (other scanners)" — points at no named peer, so it spends routing tokens without routing anywhere; `agent-management` §Description contract asks for tight delimitation and prefers dropping a clause over an enumerated chain that doesn't help the reader.
      Where: `plugins/nolte-engineering/agents/kpi-signal-scanner.md:3` (end of `description`).
      Fix: drop that clause — the two preceding negatives (`kpi-derive`, `requirements-elicit`) already route every plausible confusion.
      Verify: `description` ends at the `requirements-elicit` clause; `python3 scripts/validate_skills.py` stays green and the description shrinks rather than grows.

### Info

- [ ] [agent-management.tag-vocabulary] The `tags: [requirements]` entry is outside the starter vocabulary in `agent-management` §Tag vocabulary, which permits a new tag when no starter term fits; `requirements` is already established portfolio-wide (3 artefacts carry it), so the cluster signal is real rather than a one-off.
      Where: `plugins/nolte-engineering/agents/kpi-signal-scanner.md:7`.
      Fix: n/a (observation — conformant under the MAY).
      Verify: n/a.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
