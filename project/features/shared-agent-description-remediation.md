---
id: F-7
title: Shared agent-description remediation
status: done
roadmap_item: R-9
sprint: 5
created: 2026-07-11
ended: 2026-07-19
verifies_sprint_value: null
consistency_check:
  performed_at: 2026-07-11
  agent_version: feature-consistency-reviewer@5784336
  findings:
    - kind: prior-art
      target: PR #329 (.audits/issue-orchestrate/371/analysis.md) and agents/*.md, plugins/nolte-engineering/agents/*.md, plugins/nolte-media/agents/*.md
      resolution: proceed
    - kind: overlap
      target: F-8 (agent-description-budget-guardrail)
      resolution: proceed
---

## Description

Every consumer of `claude-shared` regains agent-description headroom because the shared plugins' descriptions are normalised to the F-6 contract. The shared side loads ~9k of Claude Code's ~15k routing budget today; this feature is the hands-on trim that brings that number down without loss of routing correctness, so a consumer like `kamerplanter` keeps room for its own agents.

Every shared agent `description` across the three plugins (`nolte-shared`, `nolte-engineering`, `nolte-media`) is rewritten to the F-6 contract shape, embedded example/commentary blocks are removed, and routing is spot-checked so no agent becomes mis-selected. The post-remediation per-plugin aggregate token weight is measured — using the single method F-5's analysis documents — and recorded as the baseline that F-8's guardrail then freezes.

## Acceptance criteria

- [x] **acceptance-1** Every shared agent `description` (across `nolte-shared`, `nolte-engineering`, and `nolte-media`) conforms to the F-6 contract shape.
- [x] **acceptance-2** No shared agent `description` contains an embedded `user:`/`assistant:`/`<commentary>` example or commentary block.
- [x] **acceptance-3** Routing correctness is preserved: the affected agents are spot-checked via `agent-review` and no routing regression is recorded.
- [x] **acceptance-4** The post-remediation per-plugin aggregate agent-description token weight is measured using F-5's documented method and recorded as the guardrail baseline consumed by F-8.

## Test hooks

- **acceptance-1** — manual: sample descriptions across all three plugins; assert each matches the F-6 contract shape — `passing`
- **acceptance-2** — CLI/grep: search every shared agent `description` for `user:`/`assistant:`/`<commentary>`; assert zero hits — `passing`
- **acceptance-3** — skill: run `agent-review` on the remediated agents; assert no routing regression finding — `passing`
- **acceptance-4** — manual: confirm the recorded per-plugin baseline number and that it was produced by F-5's documented method — `passing`

## Consistency notes

The consistency check ran via the `feature-consistency-reviewer` agent (`agent_version: feature-consistency-reviewer@5784336`) and returned two findings — one non-blocking, one blocking.

- **prior-art** (PR #329 per `analysis.md`, and the shared agent files under `agents/`, `plugins/nolte-engineering/agents/`, `plugins/nolte-media/agents/`; resolution `proceed`): PR #329 applied an ad-hoc −30% trim; the existing 23 + 28 + 2 shared agent descriptions are the *input* F-7 remediates, not prior work that already achieves F-7's contract-driven normalisation. `proceed` is correct; this is `prior-art`, not `duplication`.
- **overlap → F-8** (resolution `proceed`, blocking — **rationale below clears the `draft → ready` gate**): F-7's acceptance-4 ("post-remediation per-plugin aggregate measured and recorded as the guardrail baseline") shares its measurement subject with F-8's acceptance-1 ("holds the post-remediation baseline, fails on regression"). This is a genuine, non-redundant handoff in the P1→P3→P4 dependency chain — F-7 *produces* the baseline number and F-8 *freezes and enforces* it — not duplicate scope, so `merge-into` would wrongly collapse two atomic deliverables and is rejected. **Committed resolution:** F-7 measures the post-remediation aggregate using the single tokenization method F-5's analysis documents (per requirement A4) — a 4-characters-per-token estimate over the concatenated `description` frontmatter values of every agent under each plugin's `agents/` root, reusing the same char-based helper `scripts/validate_skills.py` already applies to its existing caps. F-8's guardrail reuses that exact method and freezes the exact number F-7 records, so the enforced ceiling, the recorded baseline, and F-5's published analysis figure all reconcile. With this single-method commitment written here and mirrored in F-8, the blocking overlap is resolved and F-7 may leave `draft`.

## Risks

- **Routing regression from over-trim.** Aggressive trimming can silently degrade specialist selection (requirement R6/A2). Mitigation: the F-6 contract keeps the "when to activate / don't use for X → use Y" routing signal mandatory, and acceptance-3 spot-checks affected agents via `agent-review`.
- **Baseline locks in a mediocre value.** Because F-8 freezes whatever F-7 achieves (A3), an under-delivered remediation would set a weak baseline. Mitigation: measure and record the baseline only after the full remediation pass, and surface the number in F-5's analysis for review.
