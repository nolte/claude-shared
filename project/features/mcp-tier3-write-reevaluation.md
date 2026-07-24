---
id: F-16
title: Tier-3 write/action MCP re-evaluation
status: draft
roadmap_item: R-10
sprint: null
created: 2026-07-13
ended: null
verifies_sprint_value: null
consistency_check:
  performed_at: 2026-07-13
  agent_version: feature-consistency-reviewer@90d0141
  findings:
    - kind: prior-art
      target: spec/claude/mcp-tool-preference/en.md
      resolution: proceed
    - kind: drift
      target: spec/project/feature/en.md
      resolution: proceed
---

## Description

The write/action artefacts are re-evaluated for whether optional MCP buys them anything: `pull-request-create` (the create step) and `release-publish-trigger` (the dispatch step). Git-plumbing operations stay on `gh` / git regardless. Edits are made only where the outcome is net-positive, and the `gh` / git fallback is never removed. This feature is gated behind the Tier-1 / Tier-2 learnings (F-14, F-15).

Unlike the earlier adoption features, this is a per-artefact go/no-go rather than automatic adoption — reflecting the hard non-goal from #378 that git plumbing and the `gh` fallback are preserved.

## Acceptance criteria

- [ ] **acceptance-1** Each Tier-3 artefact (`pull-request-create`, `release-publish-trigger`) documents, in its own body, a clear go/no-go outcome on MCP adoption with its rationale — a reader can see per artefact whether MCP is adopted or the artefact stays on `gh` / git.
- [ ] **acceptance-2** Where the outcome is "go", the artefact prefers MCP and produces output identical to its `gh`-only run; where "no-go", the artefact is left unchanged.
- [ ] **acceptance-3** The `gh` / git fallback is never removed from any Tier-3 artefact.
- [ ] **acceptance-4** Git-plumbing operations remain on `gh` / git and are not migrated to MCP.

## Test hooks

- **acceptance-1** — manual: open each artefact; confirm a documented go/no-go outcome with rationale — `pending`
- **acceptance-2** — manual/diff: for each "go", confirm MCP-preferred reads and identical output; for each "no-go", confirm the artefact is unchanged — `pending`
- **acceptance-3** — manual: confirm the `gh` / git fallback path is intact in each artefact — `pending`
- **acceptance-4** — manual: confirm git-plumbing operations stay on `gh` / git — `pending`

## Consistency notes

The consistency check ran via the `feature-consistency-reviewer` agent (`agent_version: feature-consistency-reviewer@90d0141`) and returned two non-blocking findings. Neither is `overlap` or `duplication`, so the `draft → ready` gate is not blocked.

- **prior-art** (`spec/claude/mcp-tool-preference/en.md` §Reads-versus-writes; resolution `proceed`): the convention already settles the constraint F-16 lives under — writes and git plumbing stay on `gh` / git by default, and "adopting an MCP write tool is a per-case, separately justified decision, never the default of this convention" (en.md:44), with Non-Goals reserving fallback preservation and git-plumbing. F-16 *schedules* exactly that per-case decision; its non-goals mirror the spec's rather than straying into them.
- **drift** (`spec/project/feature/en.md` §Acceptance-criteria contract; resolution `proceed`): the reviewer flagged that a "decision record exists" criterion grazes the §Acceptance-criteria MUST NOT against workflow-gate criteria. This is a borderline, low-confidence flag — the feature's audience is the maintainer (like F-8's tooling criteria). Following the reviewer's recommendation, acceptance-1 is reworded toward the observable artefact state (a reader can see, per artefact, the documented go/no-go outcome and whether MCP is adopted), and acceptance-2/3/4 already carry the observable behaviour checks (prefers MCP, identical output, fallback intact, git-plumbing unmigrated). `drift` never blocks the gate; the reword is recorded here for the audit trail.

## Risks

- **Judgement-call outcome.** The go/no-go per artefact is a judgement bound by the P3 §Reads-versus-writes rule; a "go" that later proves net-negative should be reversible without removing the `gh` / git fallback (acceptance-3 guarantees the fallback stays).

## References

- Roadmap item R-10 (`project/roadmap.md`).
- Work package P9 in the issue #378 pre-analysis (retired to git history).
- GitHub issue #378; tracking issue #382.
