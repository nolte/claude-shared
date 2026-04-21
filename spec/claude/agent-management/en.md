# Claude Agent Authoring

Status: draft

## Context
The claude-shared repository collects reusable Claude Code skills and agents that downstream projects consume. An agent has two lives: a **source** form in this repository (under `agents/`), and a **runtime** form in a consuming project (under `.claude/agents/` or `~/.claude/agents/`) where Claude Code actually loads it and the `Agent` tool dispatches to it via `subagent_type`. Without a consistent shape, agents drift in naming, trigger descriptions, tool scoping, and system-prompt quality, which makes reuse fragile and routing unreliable. This spec defines how new agents are authored, where they live in both forms, and what existing agents must conform to.

## Goals
- Every agent has the same predictable shape on disk
- Agents are routable by Claude through precise, trigger-oriented descriptions
- Agents have the minimum necessary tool access to do their job
- Agents are portable across any project that consumes claude-shared, with no hidden dependencies
- Authors have a clear checklist and template to start from

## Non-Goals
- Plugin packaging and distribution (covered separately)
- Downstream project setup and `.claude/` configuration
- Prescribing specific agent behavior beyond structural rules
- The orchestration logic inside the calling Claude (which agent to pick when)

## Requirements

### Structure
- **MUST** be authored as a single markdown file named `<name>.md` where `<name>` is ASCII kebab-case
- **MUST** include YAML frontmatter with the fields `name` and `description`
- **MUST** set `name` to match the filename without the `.md` suffix
- **MUST** write a `description` that names concrete user-facing triggers and task shapes ("use when the user asks X", "invoke for Y") rather than abstract capabilities, so the calling Claude can reliably decide when to dispatch
- **MUST** contain a system prompt in the markdown body that scopes the agent to a single responsibility and states its expected output shape
- **MUST** keep frontmatter and system-prompt content in English for token efficiency; the agent may still be instructed to respond to the user in the user's language
- **MUST** be self-contained — any supporting assets (references, examples, prompt fragments) live alongside the agent file in a sibling folder `agents/<name>/` and are referenced by relative path

### Tool access
- **MUST** declare a `tools` field in frontmatter when the agent should be restricted; omit the field only when the agent genuinely needs the full tool surface
- **MUST** scope `tools` to the minimum set needed for the agent's responsibility (principle of least authority); read-only agents MUST NOT receive write, edit, or execution tools
- **SHOULD** prefer dedicated tools (`Read`, `Grep`, `Glob`, `Edit`) over `Bash` equivalents when both would work

### Model selection
- **MAY** declare a `model` field in frontmatter (`opus`, `sonnet`, `haiku`) when the agent has a clear cost/quality trade-off; omit the field to inherit the caller's model
- **SHOULD** justify a pinned `model` in the system prompt or a comment so future readers understand why it was fixed

### Source location (claude-shared repository)
- **MUST** live at `agents/<name>.md` in the claude-shared source tree, so it can be copied, symlinked, or bundled into a plugin for distribution
- **MAY** have a sibling folder `agents/<name>/` for supporting files when needed

### Runtime location (consuming project)
- **MUST** be loadable by Claude Code from one of the standard locations:
  - `.claude/agents/<name>.md` — project-level installation
  - `~/.claude/agents/<name>.md` — user-level installation
  - the plugin's designated agents path when delivered as part of a plugin
- **MUST NOT** assume a particular install location; all internal references stay relative to the agent file or to the project the agent operates on

### Recommendations
- **SHOULD** begin the system prompt with the agent's role and boundaries, then the expected output format, then the working procedure
- **SHOULD** state explicitly in the system prompt whether the agent writes code or only researches, since the calling Claude is responsible for that distinction at dispatch time
- **SHOULD** keep the system prompt focused; if it grows past roughly 200 lines, move long-form references into `agents/<name>/` files
- **SHOULD** include in `description` both positive triggers ("use when…") and common negative cases ("do not use for…") when overlap with other agents is likely
- **MAY** include example invocations and expected reports in a sibling `agents/<name>/examples/` folder

## Acceptance Criteria
- [ ] Source file exists at `agents/<name>.md` in claude-shared with `<name>` in ASCII kebab-case
- [ ] Agent can be deployed to `.claude/agents/<name>.md` (or `~/.claude/agents/<name>.md`) in a consuming project and is dispatchable via `subagent_type: <name>`
- [ ] Frontmatter parses as valid YAML and contains at minimum `name` and `description`
- [ ] `name` in frontmatter equals the filename without `.md`
- [ ] `description` names concrete triggers the calling Claude can match against user requests
- [ ] If `tools` is set, the listed tools are sufficient for the agent's stated responsibility and contain no unused entries
- [ ] Read-only agents have no write/edit/execution tools in their `tools` list
- [ ] Agent works when invoked in a downstream project that does not contain claude-shared-specific context
- [ ] No hard-coded absolute paths; all internal references are relative to the agent file or the project it operates on
- [ ] If the agent writes files or performs side effects, the targets and preconditions are documented in the system prompt

## Open Questions
- Should the filename (and thus `name`) match the `subagent_type` string exactly, or is a mapping layer allowed?
- Do agents need version or compatibility metadata as they evolve, or is the git history of the agent file sufficient?
- Where is the boundary between a skill and an agent? When should a capability be one versus the other?
- Should agents declare which other agents they may delegate to, or is delegation left entirely to the calling Claude?
- Is there a shared convention for how agents report back (structured vs. free-form summary), or is that per-agent?
