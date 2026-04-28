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
- **MUST** include YAML frontmatter with the fields `name`, `description`, and `distribution`
- **MUST** set `name` to match the filename without the `.md` suffix
- **MUST** write a `description` that names concrete user-facing triggers and task shapes ("use when the user asks X," "invoke for Y") rather than abstract capabilities, so the calling Claude can reliably decide when to dispatch
- **MUST** set `distribution` to exactly one of `plugin` or `project`, declaring the intended delivery form (see "Distribution" below); the author chooses this consciously at creation time and changes it only by re-authoring the agent for the new form
- **MUST** contain a system prompt in the markdown body that scopes the agent to a single responsibility and states its expected output shape
- **MUST** keep frontmatter field names and technical identifier values in English: `name`, `distribution`, `tools` entries, `model`, and `tags` entries stay English regardless of the project's documentation language
- **SHOULD** keep the `description` value and the system-prompt body in English for token efficiency and portability across teams; agents authored with `distribution: project` for a project that declares a non-English documentation language in its root-level convention file (typically `CLAUDE.md`) **MAY** instead author the `description` and the body in the project's primary documentation language. Agents authored with `distribution: plugin` **MUST** stay English-only in description and body because they ship across multiple downstream projects with possibly different languages
- The agent **MAY** still be instructed to respond to the user in the user's language regardless of where the body is authored
- **MUST** be self-contained—any supporting assets (references, examples, prompt fragments) live alongside the agent file in a sibling folder `agents/<name>/` and are referenced by relative path
- **MAY** include an optional `tags` field in YAML frontmatter: a list of lowercase ASCII kebab-case strings, each ≤30 characters, with no more than 5 entries; tags provide thematic grouping so the catalog (`skill-agent-catalog`) and peer-cluster lookups (`skill-vs-agent` §Portfolio-wide consistency) can browse by topic

### Tag vocabulary
- **SHOULD** prefer a term from the starter vocabulary below when one applies, so artifacts in the same functional cluster share the same tag string
- **MAY** introduce a new tag that follows the normalization rule above when no starter term fits; avoid proliferation by reusing an existing tag whenever the fit is reasonable

Starter vocabulary:
- `pull-request`: PR authoring, labeling, landing
- `review`: spec-, skill-, agent-, or PR-level review
- `audit`: drift, compliance, vocabulary, dependency audits
- `scaffolding`: project-structure, catalog wiring, skill/agent scaffolding
- `prose`: Vale-style curation, writing guidance, documentation prose
- `audience`: audience identification and downstream doc shaping
- `release`: release-automation, changelogs, versioning
- `quality-gate`: lint, typecheck, test
- `dependency`: CVE scans, license compliance, lockfile hygiene

### Distribution
An agent is authored for exactly one of two delivery forms. The choice is made up front and written into the `distribution` field:

- `plugin`: shipped as part of a Claude Code plugin. The agent is expected to be installed and updated through the plugin mechanism, alongside other agents/skills of the same plugin, and may assume the plugin's conventions and co-located resources.
- `project`: direct reuse in a single project or user environment. The agent is copied or symlinked into the consuming setup and stands alone, without assuming any plugin context.

Every agent declares this intent so authors, reviewers, and consumers all see from the file itself whether it belongs to a plugin bundle or is meant for standalone project use.

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
Runtime location follows the declared `distribution`:

- If `distribution: plugin`, the agent **MUST** be loadable from the plugin's designated agents path once the plugin is installed in a consuming project. It **MUST NOT** require any manual drop into `.claude/agents/` or `~/.claude/agents/` to work.
- If `distribution: project`, the agent **MUST** be loadable by Claude Code from one of:
  - `.claude/agents/<name>.md`: project-level installation
  - `~/.claude/agents/<name>.md`: user-level installation

In both cases the agent **MUST NOT** assume a particular absolute install location; all internal references stay relative to the agent file or to the project the agent operates on.

### Recommendations
- **SHOULD** begin the system prompt with the agent's role and boundaries, then the expected output format, then the working procedure
- **SHOULD** state explicitly in the system prompt whether the agent writes code or only researches, since the calling Claude is responsible for that distinction at dispatch time
- **SHOULD** keep the system prompt focused; if it grows past roughly 200 lines, move long-form references into `agents/<name>/` files
- **SHOULD** include in `description` both positive triggers ("use when…") and common negative cases ("don't use for…") when overlap with other agents is likely
- **MAY** include example invocations and expected reports in a sibling `agents/<name>/examples/` folder

## Acceptance Criteria
- [ ] Source file exists at `agents/<name>.md` in claude-shared with `<name>` in ASCII kebab-case
- [ ] Frontmatter parses as valid YAML and contains at minimum `name`, `description`, and `distribution`
- [ ] `name` in frontmatter equals the filename without `.md`
- [ ] `description` names concrete triggers the calling Claude can match against user requests
- [ ] If `tags` is declared in frontmatter, every entry is a lowercase ASCII kebab-case string ≤30 characters and the list contains at most 5 entries
- [ ] `distribution` is exactly `plugin` or `project`: no other value, no missing field
- [ ] If `distribution: plugin`, the agent is dispatchable via `subagent_type: <name>` in a project where the containing plugin is installed, without manually copying the file
- [ ] If `distribution: project`, the agent is dispatchable via `subagent_type: <name>` after being deployed to `.claude/agents/<name>.md` or `~/.claude/agents/<name>.md`, with no plugin required
- [ ] If `tools` is set, the listed tools are sufficient for the agent's stated responsibility and contain no unused entries
- [ ] Read-only agents have no write/edit/execution tools in their `tools` list
- [ ] Agent works when invoked in a downstream project that doesn't contain claude-shared-specific context
- [ ] No hard-coded absolute paths; all internal references are relative to the agent file or the project it operates on
- [ ] If the agent writes files or performs side effects, the targets and preconditions are documented in the system prompt
- [ ] Frontmatter field names and technical identifier values (`name`, `distribution`, `tools`, `model`, `tags`) are English; `description` and the system-prompt body are English by default, unless the agent declares `distribution: project` and the consuming project's root-level convention file (typically `CLAUDE.md`) declares a non-English documentation language and authorizes that language for agent prose
- [ ] Reviewing an individual agent against this spec follows `spec/claude/agent-review/`; review output conforms to `spec/claude/review-plan/` and lives under `.audits/agent-review/<name>.md`

## Open Questions
- Should the filename (and thus `name`) match the `subagent_type` string exactly, or is a mapping layer allowed?
- Do agents need version or compatibility metadata as they evolve, or is the git history of the agent file sufficient?
- Where's the boundary between a skill and an agent? When should a capability be one versus the other?
- Should agents declare which other agents they may delegate to, or is delegation left entirely to the calling Claude?
- Is there a shared convention for how agents report back (structured vs. free-form summary), or is that per-agent?
