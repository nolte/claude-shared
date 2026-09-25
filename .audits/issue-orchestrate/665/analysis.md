---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "665"
classification: "bug"
secondary-classes: []
route: "direct"
status: approved-pending
created: "2026-09-25"
---

# Issue Orchestration — Pre-analysis

Group context: `issue-batch-orchestrate` run `20260925T071908Z-b7c2`, group
`2026-09-25-consumer-reachability`, integration branch `feat/2026-09-25-consumer-reachability`.
This run does not open a pull request; the bundle does.

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #665 — requirements-elicit: not runnable in a consumer repository (no plugin-root spec fallback, spec not portfolio-scoped)
- **URL**: <https://github.com/nolte/claude-shared/issues/665>
- **Labels**: none
- **Linked items**: none (`closedByPullRequestsReferences` = 0); consumer trigger `nolte/claude-goose` feature 005 R5
- **Prior art checked**: no open PR references #665; no `project/features/` entry; the 11 sibling skills carrying the fallback (`grep -rln 'CLAUDE_PLUGIN_ROOT}/spec' skills/*/SKILL.md`)
- **Trusted author**: `nolte` (repository owner) — the issue's proposal is executable input

## Classification

- **Primary class**: bug
- **Secondary class(es)**: none
- **Rationale**: a shipped skill cannot run in the context it is distributed to; the plugin contract (`spec/claude/skill-management/` §Runtime discovery) promises consumer-side runnability
- **Asserted cause verified**: confirmed — `skills/requirements-elicit/SKILL.md:53` requires the spec "in the current project" with no `${CLAUDE_PLUGIN_ROOT}` alternative; `spec/project/requirements-elicitation/en.md` head carries `Status: draft` and no `Portfolio-Scope:` line; `spec/README.md:104` lists the spec as `local`; `spec/project/portfolio-inherited-spec-layer/en.md:73` defaults a header-less spec to `local`, `:66` forbids a tracked copy in the consumer

## Requirements gate

No `project/requirements/` artifact exists for #665. **Operator override** recorded at the
group write gate (2026-09-25): the issue is the maintainer's own precise two-option
proposal, the operator chose option 1, and the acceptance criterion is mechanical
(precondition text carries the fallback; validator green). No elicitation dispatched.

## Scope

- **In scope**: the §Precondition of `skills/requirements-elicit/SKILL.md` gains the plugin-root fallback in the sibling wording
- **Out of scope**: `Portfolio-Scope: portfolio` for the spec (operator decision: option 1 only); any change to the spec text; the consumer's `recipe-requirements-elicit` skill

## Route

- **Decision**: direct
- **Rationale**: one outcome, one file, no roadmap item

## Work packages

### P1 — Plugin-root fallback in the precondition

- **Problem statement**: `SKILL.md:53` stops when `spec/project/requirements-elicitation/<canonical_language>.md` is absent from the current project. Hypothesis: adding the `${CLAUDE_PLUGIN_ROOT}/spec/project/requirements-elicitation/<canonical_language>.md` fallback (wording of `skills/github-issue-templates-apply/SKILL.md:49`: target repo first, then the copy shipped inside the installed `nolte-shared` plugin, else stop and ask) makes the skill runnable in a consumer. The specialist may refute this if the precondition is read elsewhere (e.g. a hook) — `grep -rn 'requirements-elicit' .claude/settings.json scripts/*.py` returned nothing, so no second site is known.
- **Acceptance criteria**: (a) §Precondition names both locations and the stop-and-ask fallback; (b) `python3 scripts/validate_skills.py skills/requirements-elicit/` exits 0 with no Critical; (c) the `description:` is unchanged (999/1024 chars, body-only change); (d) `grep -c 'CLAUDE_PLUGIN_ROOT' skills/requirements-elicit/SKILL.md` ≥ 1
- **Touched files / artifacts**: `skills/requirements-elicit/SKILL.md`
- **Specialist**: `nolte-claude-dev:claude-plugin-developer` (description: "Drafts or refines a plugin artifact (skill or agent) … in strict conformance with every spec under spec/claude/")
- **Depends on**: none

## Dependency ordering

P1 only.

## Risks

- Wording drift from the 11 siblings — mitigated by citing `github-issue-templates-apply:49` verbatim as the pattern.
- The body-token estimate of the skill rises slightly; check the validator's `body-token-approaching` band does not trip (currently not reported for this skill).

## Open questions

none

## Dispatch log
