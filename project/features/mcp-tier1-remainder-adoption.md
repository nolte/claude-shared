---
id: F-14
title: Tier-1 remainder MCP adoption
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
    - kind: overlap
      target: F-13, F-15, F-16
      resolution: proceed
    - kind: drift
      target: plugins/nolte-engineering/agents/dependency-audit-scanner.md
      resolution: revisit-after OQ-D-per-artefact-coverage-confirmed
    - kind: prior-art
      target: skills/issue-orchestrate/SKILL.md
      resolution: proceed
---

## Description

Once the F-13 pilot proves the optional-MCP pattern, this feature extends it to the rest of Tier 1's GitHub-reading artefacts: `issue-orchestrate`, `workflow-health-triage`, and `portfolio-manifest-collector`. Each prefers MCP reads when the server is present and falls back to `gh` when absent, with output identical either way.

`dependency-audit-scanner` — originally listed under Tier 1 in the #378 analysis — is **not** in this feature's binding set: it reads no GitHub data (its read surface is the local auditors `pip-audit` / `npm audit` / `govulncheck` / `cargo audit`, and `gh api` sits on its MUST-NOT list), so the "prefer GitHub MCP reads" contract has nothing to apply to. Its inclusion is deferred to an OQ-D-gated go/no-go (see `## Open questions`).

## Acceptance criteria

- [ ] **acceptance-1** Each of the three in-scope artefacts (`issue-orchestrate`, `workflow-health-triage`, `portfolio-manifest-collector`) prefers GitHub MCP reads when the server is present.
- [ ] **acceptance-2** Each falls back to `gh` and completes when the server is absent.
- [ ] **acceptance-3** Each produces the same output on the MCP-present run as on the `gh`-only run (identical deterministic output, excluding any per-run non-deterministic envelope).
- [ ] **acceptance-4** Each references the P3 convention (`spec/claude/mcp-tool-preference/`); for `issue-orchestrate`, the reference is added alongside its existing injection-guard citation.

## Test hooks

- **acceptance-1** — manual: per artefact, confirm MCP reads are preferred when the server is present — `pending`
- **acceptance-2** — manual: per artefact, confirm the `gh` fallback completes when the server is absent — `pending`
- **acceptance-3** — diff: per artefact, MCP-present vs `gh`-only output identical over the deterministic payload — `pending`
- **acceptance-4** — manual: per artefact, confirm the citation of `spec/claude/mcp-tool-preference/` — `pending`

## Consistency notes

The consistency check ran via the `feature-consistency-reviewer` agent (`agent_version: feature-consistency-reviewer@90d0141`) and returned three findings; the `overlap` is a blocking-kind finding resolved `proceed` with the paragraph rationale below.

- **overlap** (`F-13`, `F-15`, `F-16` — R-10 sibling drafts; resolution `proceed`): F-13/F-14/F-15/F-16 share the same R-10 scope and the same identical-output verification pattern. **Rationale (one paragraph, as required for a `proceed` on an `overlap` finding):** the artefact sets are genuinely **disjoint** — F-13 pilots `portfolio-inflight-collector`; F-14 covers `issue-orchestrate`, `workflow-health-triage`, `portfolio-manifest-collector`; F-15 covers the Tier-2 skills; F-16 re-evaluates the two write/action skills — and none of those sets intersects F-14's three artefacts, so no sibling covers F-14's work end-to-end. The #378 analysis mandates the staging `P6 (pilot) → P7 → P8 → P9`: prove the pattern once on the pilot, then broaden tier by tier over disjoint targets. F-14 is explicitly gated behind the F-13 pilot. `merge-into F-13` would be wrong — it would collapse the deliberate pilot-then-broaden staging and start the remainder before the pilot proves the pattern. What the tier features share is a *proven pattern* reused over disjoint artefacts, not a shared *scope*.
- **drift** (`plugins/nolte-engineering/agents/dependency-audit-scanner.md`; resolution `revisit-after OQ-D-per-artefact-coverage-confirmed`): the #378 analysis placed `dependency-audit-scanner` in Tier 1, but the P3 convention is scoped to artefacts that read from GitHub, and this scanner reads none — its entire read surface is the local vulnerability auditors, and `gh api` appears only in its "MUST NOT invoke" list. A uniform "prefers GitHub MCP reads" / identical-output criterion is therefore *unsatisfiable* for it, and routing it through a GitHub-advisory source would change its data source and violate the identical-output invariant. Resolution: it is removed from F-14's binding artefact set (leaving the three genuinely GitHub-reading artefacts) and deferred to an OQ-D-gated go/no-go recorded in `## Open questions` — no separate feature is opened, keeping the R-10 package→feature mapping intact, and no unsatisfiable acceptance criterion is left in F-14. The spec is the oracle here; the analysis is a planning artefact.
- **prior-art** (`skills/issue-orchestrate/SKILL.md`; resolution `proceed`): the skill already references `GitHubMCP:get_me` and `GitHubMCP:list_repository_collaborators` for the trusted-author injection-guard authorship check — not for read preference. Its issue/comment comprehension reads still shell out to `gh` and are genuinely unimplemented for MCP. Implementation note (carried into acceptance-4): reuse the existing `GitHubMCP:` server prefix, and satisfy acceptance-4 by adding the `mcp-tool-preference` citation alongside the existing injection-guard reference. Not a blocker.

## Risks

- **OQ-D residue.** `dependency-audit-scanner` (and any other artefact whose GitHub-read surface is unclear) is unresolved until OQ-D coverage is confirmed; the go/no-go is parked as an open question rather than forced into a binding criterion.
- **Prerequisite.** This feature is not startable until the F-13 pilot proves the pattern (`P6 → P7`).

## Open questions

- **OQ-D go/no-go for `dependency-audit-scanner`** — the scanner reads no GitHub data today; if OQ-D coverage work ever gives it a GitHub-advisory read path, revisit whether it adopts the optional-MCP contract. Until then it stays entirely on its local auditors and is out of F-14's binding set.

## References

- Roadmap item R-10 (`project/roadmap.md`).
- Work package P7 in `.audits/issue-orchestrate/378/analysis.md` (Tier-1 remainder); OQ-D at analysis §Open questions.
- GitHub issue #378; tracking issue #382.
