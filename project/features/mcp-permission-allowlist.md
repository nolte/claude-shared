---
id: F-11
title: Permission-allowlist the GitHub MCP tools
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
      target: spec/claude/permission-allowlist/en.md
      resolution: proceed
    - kind: prior-art
      target: spec/claude/mcp-tool-preference/en.md
      resolution: proceed
---

## Description

The GitHub MCP tool names are added to the permission allowlist so MCP tool calls do not prompt per-call, mirroring how read-only `gh` calls are already allowlisted. The allowlist stays scoped to the least-privilege read-only tool set fixed by the F-9 decision; no write-capable MCP tool is allowlisted.

Without this, every MCP tool call would trigger a permission prompt and the optional-MCP path would be unusably noisy — so the allowlist extension is what makes the pilot (F-13) and the tiered adoption (F-14–F-16) practical to run.

## Acceptance criteria

- [ ] **acceptance-1** `spec/claude/permission-allowlist/` (EN + DE) documents the GitHub MCP read tool names as allowlisted, extending the two already-documented tools (`github:get_me`, `github:list_repository_collaborators`) to the full least-privilege read set from the F-9 decision.
- [ ] **acceptance-2** The project `.claude/settings.json` allowlist includes the GitHub MCP read tool names.
- [ ] **acceptance-3** A dry check shows no per-call permission prompt for the allowlisted MCP tools.
- [ ] **acceptance-4** The allowlisted entries are scoped to the read-only tool set from the F-9 decision; no write-capable MCP tool is allowlisted beyond that set.

## Test hooks

- **acceptance-1** — manual: open `spec/claude/permission-allowlist/{en,de}.md`; confirm the MCP read tool names present in both languages — `pending`
- **acceptance-2** — manual: inspect `.claude/settings.json`; confirm the `github:` read tool names in the allowlist — `pending`
- **acceptance-3** — manual: invoke an allowlisted MCP tool; confirm no permission prompt fires — `pending`
- **acceptance-4** — manual: confirm the allowlist matches the least-privilege read set; assert no write MCP tool is present — `pending`

## Consistency notes

The consistency check ran via the `feature-consistency-reviewer` agent (`agent_version: feature-consistency-reviewer@90d0141`) and returned two non-blocking findings. Neither is `overlap` or `duplication`, so the `draft → ready` gate is not blocked.

- **prior-art** (`spec/claude/permission-allowlist/en.md` + `de.md`; resolution `proceed`): the §Selection-criteria bullet already establishes that read-only GitHub MCP read tools belong in the allowlist and enumerates two of them (`github:get_me`, `github:list_repository_collaborators`, sourced from the trusted-author injection-guard spec) in both languages. F-11 **extends** that documented set to the full least-privilege read set from F-9 rather than creating the mechanism. Following the reviewer's recommendation, acceptance-1 is scoped to the *delta* beyond the two already-documented tools, so settled entries are not re-documented.
- **prior-art** (`spec/claude/mcp-tool-preference/en.md`; resolution `proceed`): allowlist membership for any MCP tool an artefact uses is already a MUST in the P3 convention (en.md:51). F-11 operationalises that MUST; it does not contradict it. acceptance-4's read-only / no-write scoping aligns with the P3 §Reads-versus-writes rule and the allowlist spec's §Relationship (mutation-capable wildcards stay out) — so there is no drift.

## Risks

- **Tool-name accuracy.** The allowlist entries must match the exact tool names of the F-9-pinned server version; a name mismatch would silently re-introduce per-call prompts. Mitigation: verify names against the pinned catalog when F-9 lands.

## References

- Roadmap item R-10 (`project/roadmap.md`).
- Work package P4 in `.audits/issue-orchestrate/378/analysis.md`.
- GitHub issue #378; tracking issue #382.
