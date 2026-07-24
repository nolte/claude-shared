---
id: F-17
title: Candidate-surfacing sweep for shared-plugin deep rework
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
      target: spec/claude/skills-agents-sweep/ (skills/skills-agents-sweep/SKILL.md)
      resolution: proceed
    - kind: overlap
      target: F-18 (authoring-slice-carve-out-decision)
      resolution: proceed
---

## Description

Maintainers of `claude-shared` get an evidence-based list of shared agents and skills that warrant rework *beyond their descriptions* — merge, split, retire, or rewrite — produced by a fresh full `skills-agents-sweep`. This is the analysis gate for R-11's deep-rework strand: F-5's focused analysis (the F-5 structural analysis (retired to git history)) deliberately ran only a frontmatter-level pass and found no duplicate capabilities and clean family clusters, so deep rework is candidate-driven, not a blanket sweep. This feature runs the full per-artefact pass that F-5 skipped, so concrete candidates surface with evidence before any rework (the deferred P2 strand of R-11) is decomposed.

The value is honest either way: if the full pass surfaces rework candidates, R-11's P2 features act on them; if it confirms none warrant rework, that is a valid, recorded outcome that closes the deep-rework strand.

## Acceptance criteria

- [x] **acceptance-1** A consolidated `skills-agents-sweep` report exists under `.audits/skills-agents-sweep/`, conforming to `spec/claude/skills-agents-sweep/` (mandatory report sections and the single-open-sweep lifecycle), covering every shared agent and skill across the three plugins.
- [x] **acceptance-2** Each rework candidate is listed with the observed issue (overlap / dead capability / drift) and a proposed action (merge / split / retire / rewrite), or the report explicitly records that none warrant rework.
- [x] **acceptance-3** Each candidate cites evidence from the per-artefact `agent-review` / `skill-review` findings — the full pass F-5's focused sweep skipped — not only frontmatter heuristics.
- [x] **acceptance-4** Any candidate action that touches a plugin boundary is bound by `spec/claude/plugin-scoping/`; no candidate is justified by topic, domain, or artefact count alone.

## Test hooks

- **acceptance-1** — manual: open the sweep report; confirm it conforms to `spec/claude/skills-agents-sweep/` and covers all three plugins' agents and skills — `passing`
- **acceptance-2** — manual: confirm each candidate carries an observed issue + proposed action, or an explicit "none warrant rework" record — `passing`
- **acceptance-3** — manual: confirm each candidate cites per-artefact `agent-review` / `skill-review` evidence — `passing`
- **acceptance-4** — manual: confirm no boundary-touching candidate is justified by topic/domain/count alone; each cites `spec/claude/plugin-scoping/` — `passing`

## Consistency notes

The consistency check ran via the `feature-consistency-reviewer` agent (`agent_version: feature-consistency-reviewer@e8f78f7`) and returned three findings for this feature — two `overlap` (blocking, resolved below) and one `prior-art` (non-blocking).

- **overlap → F-5** (`project/features/shared-plugin-structural-analysis.md`; resolution `proceed`): F-17's acceptance-1/2 re-survey the shared agent/skill inventory F-5 acceptance-2 already mapped, and F-5's focused sweep already reached a "nothing warrants rework" conclusion within its scope. The work is non-redundant: F-5's sweep was deterministic/frontmatter-only (the 2026-07-19 sweep report (retired to git history) §Scope note explicitly "does not run the full per-artefact skill-review / agent-review pass"), whereas F-17 acceptance-3 demands evidence from the full per-artefact pass the sweep spec mandates and requirement R8 reserves for a separate feature. `merge-into F-5` is wrong (F-5 is `done`/closed and its sweep is a bounded artefact); `supersede F-5` is wrong (F-17 extends, does not replace, F-5's verdict). The load-bearing tension the operator should weigh: F-5's focused sweep found *no* rework candidates, so F-17's value depends on the full pass surfacing what the focused pass could not — and "none surfaced" is itself an accepted outcome (see §Description). `proceed`.
- **overlap → F-18** (sibling draft `authoring-slice-carve-out-decision`; resolution `proceed`, mirrored into both features à la F-7↔F-8): a `split` candidate for the authoring slice is exactly F-18's subject, so F-17's general sweep may surface the authoring carve-out as one rework candidate while F-18 is the dedicated decision on it, on a different (skill-budget) axis. This is a producer→consumer chain within one decomposition, not duplication; `merge-into` would collapse a broad sweep into a single-decision feature and `split-out` is moot (already split). `proceed`.
- **prior-art → `spec/claude/skills-agents-sweep/`** (+ `skills/skills-agents-sweep/SKILL.md`; resolution `proceed`, non-blocking): F-17 does not re-implement the sweep — the skill and its spec exist — and contradicts no MUST, so this is `prior-art`. acceptance-1 has been tightened to bind the report to `spec/claude/skills-agents-sweep/` (its mandatory sections + single-open-sweep lifecycle), mirroring how acceptance-4 binds to `plugin-scoping`.

## Risks

- **The full pass may also find nothing.** F-5's focused sweep found no rework candidates; the full per-artefact pass may confirm that. Mitigation: acceptance-2 makes "none warrant rework" a first-class, recorded outcome — the feature delivers the evidence-based *decision*, not a guaranteed candidate list.
- **Sweep-lifecycle collision.** `spec/claude/skills-agents-sweep/` allows only one open sweep at a time. Mitigation: acceptance-1 binds to that lifecycle; close any prior open sweep before this one.
