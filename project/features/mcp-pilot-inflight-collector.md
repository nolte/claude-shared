---
id: F-13
title: Tier-1 MCP pilot — portfolio-inflight-collector
status: draft
roadmap_item: R-10
sprint: null
created: 2026-07-13
ended: null
verifies_sprint_value: acceptance-3
consistency_check:
  performed_at: 2026-07-13
  agent_version: feature-consistency-reviewer@90d0141
  findings:
    - kind: prior-art
      target: agents/portfolio-inflight-collector.md
      resolution: proceed
    - kind: overlap
      target: F-14
      resolution: proceed
    - kind: drift
      target: spec/claude/mcp-tool-preference/en.md
      resolution: proceed
---

## Description

The `portfolio-inflight-collector` agent — the richest read-heavy, cross-repo GitHub collector in the portfolio — becomes the end-to-end pilot that proves the optional-MCP pattern before it is broadened. When a GitHub MCP server is present the agent prefers MCP reads; when the server is absent it falls back to `gh`. This is the MVP strand of R-10: the P3 convention (already shipped) plus this single pilot.

The demonstrable, user-visible value is that the two read paths are indistinguishable in what they produce — running the collector with MCP present and with only `gh` yields the identical deterministic collection. That equivalence is the sprint value-verifier (acceptance-3).

## Acceptance criteria

- [ ] **acceptance-1** `portfolio-inflight-collector` prefers GitHub MCP reads when the server is present.
- [ ] **acceptance-2** With the server absent, it completes the same collection via `gh`.
- [ ] **acceptance-3** Running the collector once with the MCP server present and once with only `gh` produces the identical deterministic collection payload — the collected inventory (excluding the per-run `Collected:` timestamp header and the rate-limit footer) MUST be identical across the two runs.
- [ ] **acceptance-4** The agent references the P3 convention (`spec/claude/mcp-tool-preference/`) for the optional / fallback contract.

## Test hooks

- **acceptance-1** — manual: run with the MCP server present; confirm MCP reads are preferred — `pending`
- **acceptance-2** — manual: run with the server absent; confirm the `gh` fallback completes the collection — `pending`
- **acceptance-3** — diff: capture both runs' collections and assert the deterministic payload (excluding the `Collected:` timestamp header and rate-limit footer) is identical — `pending`
- **acceptance-4** — manual: confirm the agent body cites `spec/claude/mcp-tool-preference/` — `pending`

## Consistency notes

The consistency check ran via the `feature-consistency-reviewer` agent (`agent_version: feature-consistency-reviewer@90d0141`) and returned three findings; one is a blocking-kind `overlap` resolved `proceed` with the rationale below.

- **prior-art** (`agents/portfolio-inflight-collector.md`; resolution `proceed`): the agent already declares `tools: [Bash]` and gathers its four data sources through read-only `gh` calls, so the acceptance-2 `gh`-fallback baseline already exists. F-13's net-new work is the MCP-preferred path (acceptance-1), the identical-output proof (acceptance-3), and the P3 reference (acceptance-4) — strictly additive, not a re-implementation. Note the correctly-staged dependency: acceptance-1 cannot function until F-12 (P5) grants the MCP tool names in the agent's `tools:` frontmatter (today `Bash` only) and F-11 (P4) adds them to the allowlist; both are declared prerequisites.
- **overlap** (`F-14`, the Tier-1 remainder sibling; resolution `proceed`): F-13 and F-14 share the same optional/fallback + identical-output pattern, which is the `overlap` signal. **Rationale (one paragraph, as required for a `proceed` on an `overlap` finding):** this is deliberate MVP-first staging, not redundant work. The #378 analysis mandates proving the pattern end-to-end on a *single* Tier-1 pilot (P6 → this feature) before broadening to the rest of Tier 1 (P7 → F-14) and then to Tier 2 / Tier 3 (F-15 / F-16); the dependency ordering `P6 (pilot) → P7 → P8 → P9` is explicit. The artefact sets are genuinely **disjoint** — F-13's `portfolio-inflight-collector` appears in no sibling's set — so no sibling covers F-13's work, and F-14/F-15/F-16 are each gated behind this pilot proving the pattern first. `merge-into F-14` would be the wrong resolution: it would collapse the pilot gate and start broadening before the pattern is proven, defeating the whole MVP design of R-10. The shared *pattern* across the tier features is intentional reuse of a proven approach over disjoint targets, not a shared *scope*.
- **drift** (`spec/claude/mcp-tool-preference/en.md`; resolution `proceed`): the collector's own output emits a per-run `Collected:` ISO-8601 timestamp and a rate-limit footer, so a naive byte-identical diff over the full report would fail regardless of MCP-vs-`gh` correctness. The P3 invariant is semantic ("the same inputs MUST produce identical artefacts and decisions", verified by run-both-and-diff), not byte-level. Following the reviewer, acceptance-3 and its test hook are scoped to the **deterministic collection payload**, excluding the `Collected:` header and the rate-limit footer — this keeps the value-verifier trustworthy at sprint review while honouring the spec's semantic-equivalence intent.

## Risks

- **Value-verifier reliability.** acceptance-3 is this feature's `verifies_sprint_value` criterion; its diff must exclude the non-deterministic per-run envelope (timestamp, rate-limit footer) or it would fail on correct runs. Mitigation: the criterion and its hook are scoped to the deterministic payload (see the drift finding above).
- **Prerequisite chain.** The pilot is not runnable until F-11 (allowlist) and F-12 (`tools:` grant) land; both are declared dependencies (P2, P3, P4, P5 → P6).

## References

- Roadmap item R-10 (`project/roadmap.md`).
- Work package P6 in the issue #378 pre-analysis (retired to git history) (the MVP-carrying pilot).
- GitHub issue #378; tracking issue #382.
