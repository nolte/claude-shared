---
id: F-12
title: Additive agent tools grants + routing-budget re-check
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
    - kind: prior-art
      target: project/features/agent-description-budget-guardrail.md
      resolution: proceed
---

## Description

In-scope agents reach MCP tools only if those tool names are granted in their `tools:` frontmatter. This feature adds the needed GitHub MCP read tool names to the in-scope agents' `tools:` lists — strictly additively, with no existing tool removed — and re-measures the aggregate agent-description / tool-routing budget so the grants (and any description text they require) stay within the guardrail governed by the R-9 chain (F-8).

Granting the tools is distinct from adopting them: this feature makes the tools reachable; the per-tier adoption features (F-13–F-16) are where an agent is actually taught to prefer MCP.

## Acceptance criteria

- [ ] **acceptance-1** In-scope agents' `tools:` lists include the required GitHub MCP read tool names, added additively (no existing tool — for example `Bash` — removed).
- [ ] **acceptance-2** `scripts/validate_skills.py` (via `task test`) stays green after the grants.
- [ ] **acceptance-3** The aggregate agent-description routing budget is re-measured and remains within its guardrail (per the R-9 / F-8 governance).
- [ ] **acceptance-4** No agent gains a write-capable MCP tool beyond the least-privilege read set fixed by the F-9 decision.

## Test hooks

- **acceptance-1** — manual: diff agent frontmatter; confirm additive MCP tool grants with prior tools preserved — `pending`
- **acceptance-2** — CLI: `task test` — `pending`
- **acceptance-3** — manual: re-run the F-8 aggregate-budget measurement; confirm within guardrail — `pending`
- **acceptance-4** — manual: confirm no write-capable MCP tool granted beyond the read set — `pending`

## Consistency notes

The consistency check ran via the `feature-consistency-reviewer` agent (`agent_version: feature-consistency-reviewer@90d0141`) and returned two non-blocking findings. Neither is `overlap` or `duplication`, so the `draft → ready` gate is not blocked.

- **prior-art** (`spec/claude/mcp-tool-preference/en.md` §Expression; resolution `proceed`): the convention already fixes the exact rule this feature executes — "an agent that calls MCP tools MUST have those tool names granted in its `tools:` frontmatter (additive), and the grant MUST stay within the agent-description and tool-routing budget governance" (en.md:50). acceptance-1 (additive grant), acceptance-3 (within budget), and acceptance-4 (read-only, honouring §Reads-versus-writes) map one-to-one onto the spec; F-12 operationalises the settled MUST rather than contradicting it.
- **prior-art** (`project/features/agent-description-budget-guardrail.md`, F-8; resolution `proceed`): F-8 builds the per-plugin aggregate-description regression check inside `task test`; F-12 acceptance-3 **consumes** that guardrail by re-running it after granting tools. The two features do not share build scope — F-8 builds and freezes the measurement, F-12 re-runs it — so this is a deliberate consume-not-duplicate cross-reference, not overlap.

## Risks

- **F-8 sequencing dependency.** acceptance-3 is only executable once F-8's aggregate-description budget check actually ships in `scripts/validate_skills.py`. F-8 is currently `ready`, not `done`, and the check is not yet present in the script; F-12's budget re-check cannot run until it lands.
- **Shared edit target with F-13.** `agents/portfolio-inflight-collector.md` is edited by both F-12 (frontmatter `tools:` grant) and F-13 (body prefer-MCP logic). This is an execution-coordination note, not a consistency conflict; the current `tools: [Bash]` value confirms acceptance-1's "additive, no existing tool removed" premise is satisfiable (Bash is preserved alongside the new MCP names).

## References

- Roadmap item R-10 (`project/roadmap.md`); ties to R-9 (agent-description budget governance).
- Work package P5 in the issue #378 pre-analysis (retired to git history).
- GitHub issue #378; tracking issue #382.
