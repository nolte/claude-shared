---
review-type: skill-review
target: "skills/cicd-pipeline-design/SKILL.md"
target-kind: skill
specs-applied:
  - slug: skill-management
    revision: "94231d2ec957b4af1a3fb7feba72188b19b64504"
  - slug: skill-vs-agent
    revision: "66d6513791380914c73b78c360b5740c29ef13ba"
  - slug: review-plan
    revision: "e75ffbbafaf33cd55ae46dda966894add3ae01e4"
  - slug: skill-review
    revision: "94231d2ec957b4af1a3fb7feba72188b19b64504"
repo-revision: "f46a3ef2ade001cadf956779a062992e8795c93a"
created: "2026-08-21"
status: open
---

# Skill Review: cicd-pipeline-design

## Scope

Target: `skills/cicd-pipeline-design/` (SKILL.md, 133 lines / ~3311 tokens, plus three referenced examples — all three resolve).
Specs applied: `skill-management`, `skill-vs-agent`, `review-plan`, `skill-review` (revisions recorded in frontmatter).
Validator: override — `skills-ref` is not provisioned in this repository (`command -v skills-ref` returns nothing); the structural checks it would cover are partially served by `scripts/validate_skills.py`, which runs in CI via `task test` per `spec/project/quality-gate/`. The coverage gap that leaves is itself recorded as an Info finding below.
Narrowing: none — full review.
Explicitly out of scope: runtime behavior of the skill, Vale/markdown style (handled by `task lint`), dispatched agents beyond confirming the orchestration direction.

Context: phase 1 of the skills-agents sweep 2026-08, narrowed to the five artefacts that landed since the 2026-07-25 sweep closed.

## Summary

- Critical: 1
- Warning: 1
- Suggestion: 0
- Info: 2

Go/no-go: CONDITIONAL — the Critical is a one-line frontmatter addition; everything else is deferrable.
Next concrete action: add `resumable: true` to the frontmatter.

## Findings

### Critical

- [ ] [skill-management.resumable-frontmatter] The skill declares three named operations and ships a `## Resumability` section, but its frontmatter carries no `resumable: true`.
      Where: `skills/cicd-pipeline-design/SKILL.md` frontmatter (lines 1–29); `## Resumability` at line 120; `description` closes with "Supports resume on re-invocation per `spec/claude/resumable-work/`".
      Fix: add `resumable: true` to the frontmatter.
      Verify: `grep -c '^resumable: true' skills/cicd-pipeline-design/SKILL.md` returns 1.

### Warning

- [ ] [skill-review.duplicate-capability] The `audit` operation overlaps `quality-gate-enforcer` on `ci.yml`, and neither artefact delimits against the other.
      Where: `skills/cicd-pipeline-design/SKILL.md` §Delimitation (lines 97–103) names `workflow-health-triage`, `quality-gate`, `release-publish-trigger`, `deployment-chart-manage`, and `project-structure-apply`, but not `quality-gate-enforcer`; that agent's description names `quality-gate`, `workflow-health-triage`, and `dependency-audit`, but not this skill.
      Fix: add a bidirectional delimitation — one `## Delimitation` bullet here splitting by question (this skill owns stage sequence, pinning, permissions, caching; the enforcer owns quality-gate wiring conformance), and the mirror clause in the agent. Keep the addition in the body, not the `description`: at 931 of 1024 characters the description has little headroom, and lengthening it trades a Warning for a routing-budget regression.
      Verify: both artefacts name each other; `grep -c quality-gate-enforcer skills/cicd-pipeline-design/SKILL.md` returns at least 1 and the mirror grep on the agent likewise.

### Info

- [ ] [skill-management.section-vocabulary] The skill heads its precondition block `## Precondition` (singular); 33 of 36 skills in the inventory use `## Preconditions`.
      Where: `skills/cicd-pipeline-design/SKILL.md:54`. The other two singular users are `skills/audience-identify/` and `skills/requirements-elicit/`.
      Fix: n/a (observation). `skill-management` §Operations vocabulary mandates the plural form only for `## Operations` (line 129); no rule covers the precondition heading, so this cannot be promoted above Info. The spec may need to grow a general section-heading rule — routed to the sweep's operations-vocabulary dimension.
      Verify: n/a.

- [ ] [skill-review.validator-coverage] `scripts/validate_skills.py` does not check the `resumable: true` MUST, so the Critical above passes `task test` undetected.
      Where: `scripts/validate_skills.py` reports only description-headroom `Info` entries across the whole inventory at `f46a3ef`; the Critical above is invisible to it.
      Fix: n/a (observation). Candidate for the sweep's mechanical wave: extend the validator with the `## Resumability`-present-but-`resumable`-absent check, which is a two-condition grep.
      Verify: n/a.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
