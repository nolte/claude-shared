---
id: F-18
title: Authoring-slice plugin carve-out decision
status: done
roadmap_item: R-11
sprint: null
created: 2026-07-20
ended: 2026-07-20
verifies_sprint_value: null
consistency_check:
  performed_at: 2026-07-20
  agent_version: feature-consistency-reviewer@e8f78f7
  findings:
    - kind: overlap
      target: F-5 (project/features/shared-plugin-structural-analysis.md)
      resolution: proceed
    - kind: prior-art
      target: spec/claude/plugin-scoping/ (F-5 structural analysis §3, in git history)
      resolution: proceed
    - kind: overlap
      target: F-17 (shared-plugin-rework-candidate-sweep)
      resolution: proceed
---

## Description

Maintainers get a documented decision on whether the plugin/skill-authoring slice — `skill-management`, `skill-review`, `agent-review`, `skills-agents-sweep`, `skill-agent-catalog-apply`, and the `claude-plugin-developer` agent — should be carved into its own plugin so consumers who never author a plugin or skill stop loading it. F-5 declined this carve-out **for the agent-description budget** (the slice is five skills plus one ~122-token agent, so it barely moves the agent budget), but explicitly left it open on a different axis. This feature re-evaluates it on the **skill-mechanism-budget / consumer-audience** axis: most portfolio consumers install `nolte-shared` for the delivery lifecycle and never author a plugin, yet still load the authoring slice's *skill* descriptions into their skill list every turn.

The decision is bound by the distribution-contract rule in `spec/claude/plugin-scoping/` and inherits F-5 §3's settled inputs (the consumer-audience category is legitimate — not a topic/count split — and the fourth-plugin lockstep-versioning cost), re-weighing them on the skill axis rather than re-arguing them. It is independent of the rework sweep (F-17): a keep/split answer here does not wait on the candidate list.

## Acceptance criteria

- [x] **acceptance-1** A written decision (split vs. keep) with rationale, bound by `spec/claude/plugin-scoping/` and inheriting F-5 §3's settled inputs, justified by skill-mechanism budget and consumer audience — never by topic, domain, or artefact count.
- [x] **acceptance-2** The decision measures the authoring slice's aggregate *skill*-description weight with a stated, reproducible method (analogous to F-5's agent-description measurement); the F-8 guardrail in `scripts/validate_skills.py` measures agent descriptions only, so this skill-axis measurement is net-new.
- [x] **acceptance-3** The decision weighs a split against the standing cost of a fourth lockstep-versioned plugin (version alignment in `.github/release-automation.yml`; the CLAUDE.md lockstep rule).
- [x] **acceptance-4** If the decision is to split, a follow-on execution feature is identified (execution deferred, per `plugin-scoping`); if the decision is to keep, the recorded rationale closes the carve-out question.

## Test hooks

- **acceptance-1** — manual: open the decision doc; confirm a split/keep verdict bound by `plugin-scoping/`, inheriting F-5 §3, with no topic/count justification — `passing`
- **acceptance-2** — manual: confirm a stated, reproducible skill-description-weight measurement of the authoring slice — `passing`
- **acceptance-3** — manual: confirm the fourth-plugin lockstep-versioning cost is weighed against the saving — `passing`
- **acceptance-4** — manual: confirm the decision either identifies a deferred split-execution feature or records a keep rationale that closes the question — `passing`

## Consistency notes

The consistency check ran via the `feature-consistency-reviewer` agent (`agent_version: feature-consistency-reviewer@e8f78f7`) and returned three findings for this feature — two `overlap` (blocking, resolved below) and one `prior-art` (non-blocking).

- **overlap → F-5** (`project/features/shared-plugin-structural-analysis.md`; resolution `proceed`): F-18 acceptance-1 (a written plugin-boundary decision bound by `plugin-scoping`) matches F-5 acceptance-3 at the criterion level — both produce a boundary decision citing the same spec. It is not duplication: F-5 decided only the **agent-description** axis (the carve-out removes ~122 t; §3 fact 1) and explicitly re-opened the skill axis (the F-5 structural analysis (retired to git history) §3 "must be justified by *skill*-mechanism budget … **not** by the agent-description budget"), which F-18 acceptance-2 measures for the first time — confirmed net-new because the F-8 guardrail (`scripts/validate_skills.py`) measures agent descriptions only. `merge-into F-5` / `supersede F-5` both fail (F-5 is closed and its agent-axis verdict stands; F-18 complements it); `revisit-after` fails (the deferral event, R-9 delivery, has already happened). `proceed`.
- **overlap → F-17** (sibling draft `shared-plugin-rework-candidate-sweep`; resolution `proceed`, mirrored into both features à la F-7↔F-8): F-17's general sweep may surface the authoring carve-out as one `split` candidate, while F-18 is the dedicated decision on it carrying its own skill-budget measurement method. Producer→consumer chain, not redundancy; `merge-into` would collapse a single pre-known decision into a broad sweep. `proceed`.
- **prior-art → `spec/claude/plugin-scoping/`** (+ the F-5 structural analysis (retired to git history) §3; resolution `proceed`, non-blocking): F-5 §3 already established that the consumer-audience category is legitimate (not topic/count) and named the fourth-plugin lockstep cost. F-18 inherits these — acceptance-1/3 cite F-5 §3 and re-weigh the cost on the skill axis rather than re-litigating category legitimacy.

### Lifecycle deviation record (2026-Q3 spec-drift audit)

This feature breached `spec/project/feature/` §Lifecycle: created `status: draft` in `97048dd8` and flipped directly to `status: done` in `9db74fe` (#420), with `sprint: null` throughout, so the `ready → in_progress` gate (non-null sprint) never fired (finding `project-feature.f17-f18-direct-draft-to-done`, tracked in #498). The git history is immutable; this note is the standing acknowledgement rather than a rewrite. Rationale for the deviation as it happened: R-11's two features were executed ad hoc and operator-driven in a single sitting on 2026-07-20, outside any sprint (R-11 stayed Backlog), so the intermediate states were skipped, not misrepresented — the work, its evidence, and its outcome are fully recorded above. The standing rule going forward is enforcement at write time: `feature-decompose`, `sprint-execute`, and `roadmap-plan` refuse a `status: done` write whose prior on-disk status isn't the legal predecessor; an operator-decided exception is recorded as a deviation note like this one *before* the write.

## Risks

- **Re-litigating settled inputs.** Re-arguing F-5's category legitimacy instead of re-weighing on the skill axis would waste the decision. Mitigation: acceptance-1 inherits F-5 §3 as the settled basis.
- **Marginal saving vs. standing cost.** A fourth plugin's permanent lockstep-versioning cost could outweigh a small skill-budget saving. Mitigation: acceptance-2/3 quantify both sides before the verdict, so "keep" stays a legitimate, evidence-backed outcome.
