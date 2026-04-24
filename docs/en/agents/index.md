# Agents

Agents are specialized sub-agents with focused tool access and a system prompt. Claude dispatches them via the `Agent` tool with `subagent_type: <name>`. In the claude-shared source tree they will live at `agents/<name>.md`; at runtime under `.claude/agents/<name>.md` or `~/.claude/agents/<name>.md`: or bundled inside the `nolte-shared` plugin.

!!! note "Status"
    This repository currently ships four maintained agents: `claude-plugin-developer` (drafts spec-conforming plugin skills and agents), `audience-doc-author` (generates audience-driven documentation against the relevant doc-type spec), `audience-review` (reviews audience artifacts produced by `audience-identify`), and `prose-vale-curator` (curates prose to pass Vale while preserving technical claims). Further agents follow the same specification ([Agent Authoring](../specs/agent-management.md)).

## Agent anatomy

An agent is a single Markdown file with YAML frontmatter and a system prompt in the body:

```markdown
---
name: <kebab-case-name>
description: Concrete triggers ("use when …"): not abstract capabilities.
tools: [Read, Grep, Glob]   # optional, principle of least authority
model: sonnet               # optional
---

# System Prompt

Role and boundaries. Output format. Procedure.
```

Frontmatter `name` must match the filename without `.md`. Omit `tools` only when the agent genuinely needs the full surface; otherwise list the minimum. Read-only agents must **never** receive write/edit/execution tools.

## Source vs. runtime location

| Context | Path |
|---------|------|
| claude-shared source tree | `agents/<name>.md` |
| Consuming project, project-level | `.claude/agents/<name>.md` |
| Consuming project, user-level | `~/.claude/agents/<name>.md` |
| Delivered via plugin | the plugin's designated agents path |

Agents must not assume a particular install location; all internal references stay relative to the agent file or the project it operates on.

## Authoring rules

Full rules, acceptance criteria and open questions:

- [Agent Authoring (Spec)](../specs/agent-management.md)
- Canonical (EN): `spec/claude/agent-management/en.md`
- Translation (DE): `spec/claude/agent-management/de.md`
