# Agent Authoring

This page summarizes the specification at `spec/claude/agent-management/en.md` (canonical source).

**Status:** draft

## Context

The claude-shared repository collects reusable Claude Code skills and agents. An agent has two lives: a **source form** here (`agents/`) and a **runtime form** in a consuming project (`.claude/agents/` or `~/.claude/agents/`) where Claude Code loads it and the `Agent` tool dispatches via `subagent_type`.

Without a consistent shape, agents drift in naming, trigger descriptions, tool scoping, and system-prompt quality — reuse becomes fragile and routing unreliable.

## Goals and Non-Goals

**Goals**

- Consistent shape on disk
- Routable through precise, trigger-oriented `description`s
- Minimum necessary tool access (principle of least authority)
- Portable across projects, no hidden dependencies
- Clear checklist and template

**Non-Goals**

- Plugin packaging
- Downstream `.claude/` configuration
- Specific agent behavior beyond structural rules
- Orchestration logic in the calling Claude

## Requirements (excerpt)

### Structure

- **MUST** be a single Markdown file `<name>.md` in ASCII kebab-case
- **MUST** include YAML frontmatter with `name` and `description`
- **MUST** set `name` to match the filename without `.md`
- **MUST** write a `description` naming concrete triggers ("use when …") — not abstract capabilities
- **MUST** include a system prompt in the body scoped to a single responsibility and stating its output shape
- **MUST** keep frontmatter and system prompt in English (token efficiency)
- **MUST** be self-contained — supporting assets in `agents/<name>/`

### Tool access

- **MUST** declare `tools` when restricted; omit only when the agent genuinely needs full access
- **MUST** scope `tools` to the minimum set required (principle of least authority)
- **MUST NOT** give read-only agents write/edit/execution tools
- **SHOULD** prefer dedicated tools (`Read`, `Grep`, `Glob`, `Edit`) over `Bash` equivalents when either would work

### Model selection

- **MAY** declare `model` (`opus`, `sonnet`, `haiku`)
- **SHOULD** justify a pinned `model` in a comment or the system prompt

### Locations

- **MUST** place source at `agents/<name>.md`
- **MUST** be loadable at runtime from `.claude/agents/<name>.md`, `~/.claude/agents/<name>.md`, or the plugin path
- **MUST NOT** assume a particular install location

### Recommendations

- **SHOULD** order the system prompt: role/boundaries → output format → procedure
- **SHOULD** state explicitly whether the agent writes code or only researches
- **SHOULD** keep the system prompt under ~200 lines
- **SHOULD** list positive triggers and — when overlap is likely — negative cases in `description`

## Acceptance Criteria

- [ ] Source file exists at `agents/<name>.md` with `<name>` in ASCII kebab-case
- [ ] Agent dispatchable in a downstream project via `subagent_type: <name>`
- [ ] Frontmatter parses as valid YAML; at minimum `name` and `description`
- [ ] `name` in frontmatter == filename without `.md`
- [ ] `description` names concrete triggers
- [ ] If `tools` is set, the list is sufficient and has no unused entries
- [ ] Read-only agents have no write/edit/execution tools
- [ ] Agent works without claude-shared-specific context
- [ ] No absolute paths
- [ ] Side-effect targets and preconditions documented when applicable

## Open Questions

- Should the filename match the `subagent_type` string exactly?
- Do agents need version/compatibility metadata?
- Where is the boundary between skill and agent?
- Should agents declare delegation targets?
- Is there a shared reporting convention (structured vs. free-form)?

## Full text

- Canonical (EN): `spec/claude/agent-management/en.md`
- Translation (DE): `spec/claude/agent-management/de.md`
