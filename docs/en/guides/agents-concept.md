---
title: Agents
audience: [maintainer]
content_mode: explanation
track: developer-docs
last_updated: 2026-05-19
---

# Agents

Agents are specialized sub-agents with focused tool access and a system prompt. Claude dispatches them via the `Agent` tool with `subagent_type: <name>`. In the `claude-shared` source tree they live at `agents/<name>.md`. At runtime Claude Code loads them from three places: `.claude/agents/<name>.md`, `~/.claude/agents/<name>.md`, or the `nolte-shared` plugin.

## Bundled agents

| Agent | Purpose |
|-------|---------|
| `claude-plugin-developer` | Drafts spec-conforming plugin skills and agents for `nolte-shared` |
| `audience-doc-author` | Drafts or refines audience-driven documentation against an existing audience artifact |
| `audience-review` | Reviews audience artifacts produced by `audience-identify` (read-only) |
| `spec-readiness-reviewer` | Audits specs for contradictions, audience fit, and Requirement-vs-Acceptance completeness |
| `docs-freshness-checker` | Audits MkDocs documentation for language parity, dead links, stale path references, ADR (Architecture Decision Record) hygiene |
| `prose-vale-curator` | Curates prose to pass Vale without altering technical claims |
| `png-to-transparent-svg` | Converts a PNG image with baked-in checkerboard transparency into an SVG file with real alpha |
| `feature-consistency-reviewer` | Reviews a draft feature against the feature corpus, source roots, and spec corpus for overlap, duplication, drift, and prior art |

All agents follow the same specification ([Agent Authoring](../references/specs/agent-management.md)). Canonical source per agent: `agents/<name>.md` in the source tree.

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

Frontmatter `name` must match the filename without `.md`. Omit `tools` for the full surface; otherwise list the minimum. Read-only agents must **never** receive write/edit/execution tools.

## Source vs. runtime location

| Context | Path |
|---------|------|
| `claude-shared` source tree | `agents/<name>.md` |
| Consuming project, project-level | `.claude/agents/<name>.md` |
| Consuming project, user-level | `~/.claude/agents/<name>.md` |
| Delivered via plugin | the plugin's designated agents path |

Agents must not assume a particular install location. All internal references stay relative to the agent file or the project it operates on.

## Authoring rules

Full rules, acceptance criteria and open questions:

- [Agent Authoring (Spec)](../references/specs/agent-management.md)
- Canonical (EN): `spec/claude/agent-management/en.md`
- Translation (DE): `spec/claude/agent-management/de.md`
