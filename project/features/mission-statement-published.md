---
id: F-1
title: Mission statement published
status: draft
roadmap_item: R-1
sprint: null
created: 2026-05-09
ended: null
verifies_sprint_value: acceptance-1
consistency_check:
  performed_at: 2026-05-09
  agent_version: manual-2026-05-09
  findings:
    - kind: clean
      target: n/a
      resolution: proceed
---

## Description

The `claude-shared` repository carries a complete, spec-compliant `project/mission.md` so the plugin proves it can dogfood its own planning-suite specs end to end. The mission statement names what the plugin is and for whom (the audiences from `AUDIENCES.md`), references the outcomes from `project/goals.md`, and pins its measurability to a concrete acceptance criterion on this feature. A reader walking the repo's `project/` tree finds an example of the planning suite they can directly model their own adoption against.

## Acceptance criteria

- [ ] **acceptance-1** `project/mission.md` exists with all eight required frontmatter fields (`mission_statement`, `relevant_outcomes`, `audiences`, `verifies_via`, `time_bound`, `mvp_status`, `created`, `revised_at`) and the four required level-2 sections (`Statement`, `Audiences`, `Verification`, `Source`) in the declared order per `spec/project/mission/`.
- [ ] **acceptance-2** Every audience identifier in the `mission.md` `audiences` frontmatter resolves to an entry in `AUDIENCES.md`, and every audience listed in frontmatter has a tailored paragraph in the `## Audiences` body section.
- [ ] **acceptance-3** `relevant_outcomes` is non-empty and references at least one `O-<n>` outcome defined in `project/goals.md`.
- [ ] **acceptance-4** `verifies_via` resolves to a feature file under `project/features/` whose declared `acceptance-<n>` identifier exists on that feature.
- [ ] **acceptance-5** `time_bound` is one of `{ kind: outcome, ref: O-<n> }` or `{ kind: mvp_completion }`; no calendar-date or free-text deadline is present.

## Test hooks

- **acceptance-1** — manual: open `project/mission.md` and verify the eight frontmatter keys plus four section headings are present in the declared order — `pending`
- **acceptance-2** — manual: extract `audiences` from `mission.md` frontmatter and `## Audiences` paragraphs; cross-reference every identifier against `AUDIENCES.md` — `pending`
- **acceptance-3** — manual: extract `relevant_outcomes` from `mission.md`; grep `project/goals.md` for each `O-<n>` and confirm the outcome exists — `pending`
- **acceptance-4** — manual: parse `verifies_via` (pattern `<feature-id>:acceptance-<n>`); confirm `project/features/<slug>.md` exists with the named acceptance-criterion identifier — `pending`
- **acceptance-5** — manual: parse `time_bound` from frontmatter; assert the `kind` is one of `outcome` or `mvp_completion`, and that no ISO date or natural-language deadline appears — `pending`

## Consistency notes

The consistency check ran as a manual fallback because the running plugin runtime hadn't yet loaded the `feature-consistency-reviewer` agent as a slash command at the time of authoring (the agent was merged on `develop` minutes before this feature was decomposed; a `/reload-plugins` would lift the fallback in a future invocation).

Investigation surfaces:

- **Feature corpus** under `project/features/`: empty before this file, so no overlap or duplication is possible. After this write the corpus carries exactly one feature.
- **Source-code surface** (recognised primary roots per `spec/project/project-structure/` for a Claude plugin: `skills/<name>/`, `agents/<name>.md`, `.claude-plugin/`): the feature targets `project/mission.md`, which doesn't yet exist; no prior art that re-implements this behaviour was found.
- **Spec corpus** under `spec/`: `spec/project/mission/` is the spec this feature implements. The feature's acceptance criteria mirror the spec's frontmatter and body-section requirements without contradicting any MUST or straying into a Non-Goal.

Result: a single `kind: clean` finding, `resolution: proceed`. The feature is cleared for `draft → ready` once the sprint-side `sprint` field is assigned.

## Risks

- The mission statement's audience-tailoring section grows with the audience list; every audience added later forces a mission revision (per the bidirectional validation between `audiences` frontmatter and `## Audiences` paragraphs). This is a hygiene reminder, not a delivery risk.
- The `verifies_via` field on the mission must point at exactly this feature plus exactly one of these acceptance criteria; renaming the slug after `draft` is forbidden by the feature spec, so the slug `mission-statement-published` is locked once this feature leaves `draft`.
