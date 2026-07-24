# Optional GitHub MCP Tool Preference

Status: draft
Portfolio-Scope: local

## Context

Skills and agents that read from GitHub reach it today by shelling out to the `gh` CLI and parsing its text output. A connected GitHub MCP server exposes the same operations as typed, paginated, structured tools that are cheaper and more reliable to consume than scraped CLI text, especially for read-heavy comprehension: an issue with its comments and linked items, a workflow run with its logs, or issues and pull requests collected across the whole portfolio.

This spec defines the **authoring convention** for adopting that path: how a skill or agent expresses "prefer the GitHub MCP server when it's present, and always fall back to `gh`." The convention is strictly optional and strictly additive. An MCP server may be absent in headless, cron, or CI runs, so nothing may start to *require* it, and no behaviour may change on either path.

It's complementary to three existing rules, and restates none of them: `spec/claude/skill-management/` and `spec/claude/agent-management/` already fix **how** an MCP tool is named in artefact prose (the fully-qualified `ServerName:tool_name` syntax) and note that the `mcpServers` frontmatter field is ignored for plugin-distributed agents; `spec/claude/permission-allowlist/` owns the **allowlist** that keeps the tool calls from prompting. This spec governs only **whether and when** a GitHub-touching artefact prefers an MCP read over `gh`.

Readers: skill and agent authors in `claude-shared` who maintain GitHub-touching artefacts and the reviewers who verify them.

## Goals

- State one convention every GitHub-touching skill or agent references for the optional MCP-preferred read path.
- Guarantee headless and CI safety: the `gh`/git fallback always works, so an absent MCP server never breaks an artefact.
- Preserve behaviour: the same inputs produce identical artefacts and decisions whether the MCP path or the `gh` path runs.
- Delimit MCP-preferred reads from writes and git plumbing, which stay on `gh`/git.
- Compose cleanly with the MCP-tool naming rule (`skill-management`/`agent-management`) and the allowlist rule (`permission-allowlist`) without restating either.

## Non-Goals

- Mandating the MCP server or any MCP tool: the convention is optional, and `gh`/git remains authoritative.
- Removing or weakening the `gh`/git fallback in any artefact.
- Specifying the MCP server's installation, authentication, or configuration surface: provisioning is a separate concern and a consumer choice.
- Rewriting git plumbing (push, rebase, merge) or deliberate write actions as MCP calls.
- Owning the permission-allowlist entries themselves (`permission-allowlist`) or the MCP-tool naming syntax (`skill-management`, `agent-management`).

## Requirements

### Optionality and fallback

- A skill or agent that reads from GitHub **SHOULD** prefer an available GitHub MCP read tool over parsing `gh` CLI output when a GitHub MCP server is connected.
- It **MUST** retain a working `gh`/git fallback and **MUST NOT** require the MCP server; with no server connected, the artefact **MUST** complete via `gh`/git alone.
- It **MUST** degrade gracefully: detect availability and fall back silently. Missing MCP tools **MUST NOT** cause a blocking prompt, an error, or an abandoned run.
- The MCP-preferred path **MUST NOT** change behaviour: the same inputs **MUST** produce identical artefacts and decisions on either path. This is the acceptance-testable invariant an adopting artefact is verified against (run once with the server present, once with `gh` only, and diff the result).

### Reads versus writes

- Reads (get, list, search, run logs) are the MCP-preferred surface.
- Writes and git plumbing (`git push`/`rebase`/`merge`, pull-request create/merge/label, `gh workflow run`) **MUST** stay on `gh`/git by default; adopting an MCP write tool is a per-case, separately justified decision, never the default of this convention.

### Expression in the artefact

- An adopting skill or agent **MUST** state the optional path in its body in one short place (for example a tooling note) and **MUST** reference this spec, so a reader knows the MCP path exists and that `gh`/git stays authoritative.
- When an artefact references an MCP tool in its prose, it **MUST** use the fully-qualified `ServerName:tool_name` syntax required by `spec/claude/skill-management/` and `spec/claude/agent-management/`; this spec doesn't restate that rule but depends on it.
- An agent that calls MCP tools **MUST** have those tool names granted in its `tools:` frontmatter (additive), and the grant **MUST** stay within the agent-description and tool-routing budget governance; the `mcpServers` frontmatter field is ignored for plugin-distributed agents, so the server is provided by the consumer's project configuration, not the agent.
- The MCP tool names an artefact uses **MUST** appear in the allowlist per `spec/claude/permission-allowlist/` so no per-call confirmation prompt occurs.

### Server and tool catalogue

- This spec **MUST NOT** mandate a specific MCP server; the reference server is GitHub's official `github-mcp-server`, which a consumer **MAY** replace.
- Because MCP tool catalogues evolve across server versions, an adopting artefact **MUST** verify the exact tool names against the pinned server version rather than hard-coding an unversioned assumption.

## Acceptance Criteria

- [ ] The convention is stated as optional: SHOULD prefer, MUST fall back, MUST NOT require.
- [ ] Headless/CI safety is a MUST, with an explicit `gh`-only completion guarantee.
- [ ] The identical-output invariant is normative and phrased as a run-both-and-diff check.
- [ ] The reads-versus-writes/git-plumbing delimitation is explicit.
- [ ] The expression rules are all present: body note plus spec reference, qualified `ServerName:tool_name` naming (by reference), additive `tools:` grant within budget, and allowlist membership (by reference).
- [ ] The spec is server-agnostic with `github-mcp-server` named as the reference, and it requires tool-name verification against the pinned server version.
- [ ] The spec restates neither the MCP-tool naming rule nor the allowlist mechanism; it references them.

## References

- [R1] MCP-tool naming syntax and the skill-side authoring rules: `spec/claude/skill-management/`
- [R2] Agent frontmatter, `tools:` grants, and the ignored `mcpServers` field for plugin-distributed agents: `spec/claude/agent-management/`
- [R3] The allowlist that keeps shell and MCP tool calls from prompting: `spec/claude/permission-allowlist/`
- [R4] Agent-description and tool-routing budget governance the `tools:` grants must respect: roadmap item R-9
- [R5] Provenance and the staged adoption plan (work packages P1-P9): issue #378; pre-analysis retired to git history

## Open Questions

- **Portfolio scope**: this convention ships as `local`. If downstream consumers begin authoring their own GitHub-touching skills/agents against MCP, promoting it to `Portfolio-Scope: portfolio` (as the paired `permission-allowlist` already is) is a deliberate maintainer act, not an automatic one.
- **Provisioning surface**: whether the reference server is shipped as a repo-root `.mcp.json` or documented per consumer is owned by the provisioning work package (P1/P2 of issue #378), not by this convention.
- **Non-GitHub MCP servers**: this spec is scoped to the GitHub MCP server; a general "prefer MCP for external-service reads" convention is deferred until a second server forces the question.
