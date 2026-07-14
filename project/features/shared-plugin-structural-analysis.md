---
id: F-5
title: Structural analysis + plugin-boundary decision
status: ready
roadmap_item: R-9
sprint: 5
created: 2026-07-11
ended: null
verifies_sprint_value: null
consistency_check:
  performed_at: 2026-07-11
  agent_version: feature-consistency-reviewer@5784336
  findings:
    - kind: prior-art
      target: .audits/issue-orchestrate/371/analysis.md (PR #329 trim; .audits/skills-agents-sweep/2026-07-01.md)
      resolution: proceed
---

## Description

Maintainers of `claude-shared` get a written, measured map of the shared marketplace/plugin/agent/skill layout, plus a documented decision on whether the `nolte-shared` plugin boundary should change. Today the three shared plugins load roughly 9k of Claude Code's ~15k agent-description routing budget into every consumer's context on every turn, but there is no data-grounded picture of where that weight sits or whether the monolith should be split. This feature produces that picture so the downstream remediation (F-7) and guardrail (F-8) act on evidence rather than guesswork.

The analysis measures per-plugin aggregate agent-description token weight, maps capability overlap and delimitation cross-references, and reaches a boundary decision — split `nolte-shared` into finer, independently-enableable plugins, or keep the monolith and slim it — whose rationale is explicitly bound by the distribution-contract rule in `spec/claude/plugin-scoping/` (a split is justified only by a runtime/dependency or consumer-audience difference, never by topic or count). It reuses the existing `agent-review`, `skill-review`, and `skills-agents-sweep` outputs rather than re-deriving them.

The boundary decision **MUST** evaluate one named candidate on its merits: extracting the **plugin/skill-authoring capabilities** — the skills and agents whose consumers are only repositories that themselves author Claude Code plugins or skills (for example `skill-management`, `claude-plugin-developer`, `skill-review`, `agent-review`, `skills-agents-sweep`, `skill-agent-catalog-apply`) — into their own plugin. This is a genuine **consumer-audience** distribution contract under `spec/claude/plugin-scoping/`, not a topic split: most portfolio consumers install `nolte-shared` for the delivery lifecycle and never author a plugin, so they would never need the authoring slice. The analysis assesses whether this carve-out is worth its own plugin (the routing-budget saving for the majority audience versus the cost of a fourth plugin and lockstep versioning) and records the verdict; executing any such split is deferred to a follow-on feature (R-9 / P5), not this sprint.

## Acceptance criteria

- [ ] **acceptance-1** A written analysis artifact records the measured per-plugin aggregate agent-description token weight for all three shared plugins (`nolte-shared`, `nolte-engineering`, `nolte-media`), with the measurement method stated explicitly so the number is reproducible.
- [ ] **acceptance-2** The artifact maps capability overlap and delimitation (`don't use for X → use Y`) cross-references across the shared agents and skills.
- [ ] **acceptance-3** The artifact states a plugin-boundary decision (split vs. keep-and-slim) with a rationale explicitly bound by the distribution-contract rule in `spec/claude/plugin-scoping/`; the rationale does not justify any split by topic, domain, or agent count alone.
- [ ] **acceptance-4** The artifact reuses and cites the existing `agent-review`, `skill-review`, and `skills-agents-sweep` outputs rather than re-deriving their conclusions.

## Test hooks

- **acceptance-1** — manual: open the analysis artifact; confirm a per-plugin token-weight table covering all three shared plugins and a stated measurement method — `pending`
- **acceptance-2** — manual: confirm the artifact contains a capability-overlap and delimitation cross-reference map — `pending`
- **acceptance-3** — manual: confirm the boundary-decision section names the decision and cites `spec/claude/plugin-scoping/`; assert no topic/count-only justification — `pending`
- **acceptance-4** — manual: confirm citations to the `agent-review`, `skill-review`, and `skills-agents-sweep` outputs — `pending`

## Consistency notes

The consistency check ran via the `feature-consistency-reviewer` agent (`agent_version: feature-consistency-reviewer@5784336`) and returned one non-blocking finding for this feature.

- **prior-art** (`.audits/issue-orchestrate/371/analysis.md` — PR #329 trim and the `skills-agents-sweep` artifact; resolution `proceed`): earlier work touched agent descriptions — PR #329 applied a one-off −30% two-tier trim — and the `skills-agents-sweep/2026-07-01.md` artifact ran a qualitative sweep whose 5k-token cap targets the skill *body* axis (the axis `scripts/validate_skills.py` already enforces at lines 427–447), which is orthogonal to the per-agent *description*-token routing budget this feature measures. Neither produced F-5's measured per-plugin analysis or the plugin-boundary decision, so `proceed` is correct: F-5 is net-new analysis, not a re-run. No sibling feature (F-1 mission, F-2 release, F-3 quality-gate docs, F-4 reviewer-agent coverage) claims this scope. `prior-art` is a non-blocking kind, so it does not gate `draft → ready`.

This feature is the **measurement-method source** for the R-9 chain: the tokenization method it documents under acceptance-1 is the single method that F-7's recorded baseline and F-8's enforced guardrail both reuse verbatim (see F-7 and F-8 consistency notes). Because F-5's own measurement is self-contained, the reviewer raised no blocking overlap on F-5; the shared-method commitment is recorded downstream where the values must reconcile.

**2026-07-11 — within-scope refinement (no re-run findings block).** After the initial check, the `## Description` gained a named candidate for the boundary decision: extracting the plugin/skill-authoring capabilities (`skill-management`, `claude-plugin-developer`, `skill-review`, `agent-review`, `skills-agents-sweep`, `skill-agent-catalog-apply`) into their own plugin on a consumer-audience distribution contract. This sharpens *what* F-5's boundary decision (acceptance-3) must evaluate; it does not change F-5's scope relative to the feature corpus, the source roots, or the spec corpus, and introduces no new overlap, duplication, or drift — it strengthens the existing `plugin-scoping` alignment the reviewer already found clean. No new blocking finding results; a formal agent re-run can be dispatched on request if a fuller audit trail is wanted before this feature enters `in_progress`.

## Risks

- **Untracked dependency.** Acceptance-4 reuses the `skills-agents-sweep` output, but `.audits/skills-agents-sweep/2026-07-01.md` is currently **untracked and absent from this worktree**. The analysis cannot reuse an output that is not checked out; the feature must either regenerate the sweep (via `skills-agents-sweep`) or record its absence and reuse only the `agent-review` / `skill-review` outputs. Flagged by the consistency reviewer as a delivery risk.
- **Contested boundary decision.** The split-vs-slim decision is a judgement call bound by `spec/claude/plugin-scoping/`; a decision that later proves wrong would ripple into F-6/F-7. Mitigation: the decision records its distribution-contract rationale so it is reviewable and reversible before remediation begins.
