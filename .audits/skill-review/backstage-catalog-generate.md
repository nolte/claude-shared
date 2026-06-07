---
review-type: skill-review
target: "skills/backstage-catalog-generate/SKILL.md"
target-kind: skill
specs-applied:
  - slug: skill-management
    revision: "01575faf0ba2b75333191cfad81d32c258833f6c"
  - slug: skill-vs-agent
    revision: "f84b38cea237fa4af4e4926559cdb1922fbdc61c"
  - slug: review-plan
    revision: "fb5ddba2328b68fbf6837dc4951a96d5b3fdb95b"
  - slug: skill-review
    revision: "01575faf0ba2b75333191cfad81d32c258833f6c"
repo-revision: "004c8f73311d2144581c8fdb4e56435a10525509"
created: "2026-06-07"
status: in-progress
---

# Skill Review: backstage-catalog-generate

## Scope

Target: `skills/backstage-catalog-generate/` (single `SKILL.md`, ~110 lines; no `templates/`, `references/`, `examples/`, or `scripts/` subfolders).
Specs applied: `skill-management`, `skill-vs-agent`, `review-plan`, `skill-review` (revisions recorded in frontmatter).
Validator: `scripts/validate_skills.py`@89a7102 (2026-06-02) — the repository's `skills-ref` stop-gap, run via `task test` / `validate:skills`. Result: 0 findings for this skill (the Warnings/Info in the full run belong to pre-existing peer skills/agents). No external `skills-ref` binary is provisioned; this validator is the documented project substitute per `skill-review` §Checks derived from external skill-structure validation.
Narrowing: none (full review).
Context: new skill, first spec-conformance pass; authored directly in the main session rather than via `claude-plugin-developer` (worktree-path access for subagents is unreliable). Governing domain spec: `spec/project/backstage-catalog-generation/` (authored in the same change).
Author-time triangulation gate (`research-triangulate` §Author-time assertions): evaluated — see Info findings. The skill's repo-external Backstage assertions are backed by the in-change research report `.audits/backstage-research/2026-06-07-research-notes.md` (146 sources, ≥1 Primary: `backstage.io/docs` + `github.com/backstage` source), referenced from the cited domain spec; gate considered satisfied (no Critical).
Explicitly out of scope: runtime behavior of the skill, Vale/markdown style (handled by `task lint`), dispatched agents (this skill dispatches none).

## Summary

- Critical: 0
- Warning: 1 (closed)
- Suggestion: 2 (1 closed, 1 open)
- Info: 3

Go/no-go: PASS — no Critical findings; the skill is mergeable. W1 and S1 were addressed in this session (Gotchas section added, three `examples/` scenarios seeded). S2 remains open as optional tightening; the three Info items are observations.
Next concrete action: commit Spec + Skill + plan together; S2 may be deferred.

## Findings

### Critical

<!-- none -->

### Warning

- [x] [skill-review.best-practices-gotchas] No `## Gotchas` section though the skill clearly operates against a non-obvious environment (Backstage's stricter-than-prose validation: `Resource` has no `lifecycle`, empty-but-required `Group.children`/`User.memberOf`, numeric/boolean annotation values must be YAML-quoted, the offline validator does not verify reference-target existence, `validate-entity`'s `location` sits in the request body not a header).
      Where: `skills/backstage-catalog-generate/SKILL.md` — body has `## Hard rules` and a signal table but no `## Gotchas` heading.
      Fix: add a `## Gotchas` section gathering the non-obvious environment quirks (several are currently implicit in Hard rules / the signal table); or record a downgrade rationale that the Hard-rules coverage suffices.
      Verify: `grep -n '## Gotchas' SKILL.md` returns a hit, or the plan item carries a `→ deferred:` / downgrade annotation.

### Suggestion

- [x] [skill-review.evaluation-scenarios] No `examples/` evaluation scenarios (input prompt + expected behaviour); for a new skill this is a `Suggestion` per `skill-review` §Checks derived from evaluation discipline.
      Where: `skills/backstage-catalog-generate/` — no `examples/` folder.
      Fix: add ≥3 scenarios (e.g. a Node service with an OpenAPI spec → Component+API; a library with no CODEOWNERS → owner flagged needs-confirm; a Tech Radar JSON request).
      Verify: `ls skills/backstage-catalog-generate/examples/` lists ≥3 scenario files.

- [ ] [skill-management.drift-surface] The body restates several repo-external Backstage facts inline (in Hard rules / signal table) that also live in the domain spec, creating a drift surface if Backstage or the spec changes.
      Where: `SKILL.md` `## Hard rules` and `## Repo signals → fields`.
      Fix: keep only the generation-critical invariants inline and lean on the cited spec as single source of truth; the existing "when the spec disagrees, the spec wins" rule already mitigates, so this is optional tightening.
      Verify: inline facts are minimised or each carries an explicit "per spec §…" pointer.

### Info

- [ ] [research-triangulate.author-time-assertions] Author-time triangulation gate evaluated and considered satisfied: the skill's repo-external Backstage assertions (field rules, `@roadiehq/backstage-entity-validator`, `@backstage-community` package, well-known/deprecated annotations) are not Model-memory-only — they trace through the cited domain spec to `.audits/backstage-research/2026-06-07-research-notes.md` (146 sources, ≥1 Primary), shipped in the same change. Recorded for transparency so a re-reviewer sees the gate was considered.
      Where: `SKILL.md` body (external assertions) → `spec/project/backstage-catalog-generation/` → research report.
      Fix: n/a (observation).
      Verify: n/a.

- [ ] [skill-review.multi-model-testing] No evidence of multi-model testing (no example output or rubric mentioning Haiku/Sonnet/Opus).
      Where: `skills/backstage-catalog-generate/`.
      Fix: n/a (observation); optionally capture an eval rubric alongside S1's examples.
      Verify: n/a.

- [ ] [skill-management.name-form] Name `backstage-catalog-generate` is noun-phrase + verb (verb-last), not the preferred gerund form; consistent with the sibling `image-generate`, so not a smell — recorded only as an observation.
      Where: `SKILL.md` frontmatter `name`.
      Fix: n/a (observation); the form matches an established peer.
      Verify: n/a.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
2026-06-07 — W1 gotchas-section — added `## Gotchas` to SKILL.md consolidating the non-obvious Backstage validation quirks — verified: `grep -n '## Gotchas' SKILL.md` hits; `validate_skills.py` still 0 findings; 89 lines (<500)
2026-06-07 — S1 evaluation-scenarios — seeded examples/ with 01-node-service-with-openapi, 02-library-no-codeowners, 03-tech-radar-json — verified: `ls examples/` lists 3 scenario files
