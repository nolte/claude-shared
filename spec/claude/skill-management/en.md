# Claude Skill Authoring

Status: draft

## Context
The claude-shared repository collects reusable Claude Code skills and agents that downstream projects consume. A skill has two lives: a **source** form in this repository (under `skills/`) and a **runtime** form in a consuming project, where Claude Code actually loads it. The only supported runtime-distribution path is the Claude Code plugin mechanism: this repository is itself a Claude Code plugin (`.claude-plugin/plugin.json` plus a marketplace entry), and consuming projects pick up skills by installing the plugin. Without a consistent shape and a single distribution path, skills drift in naming, trigger descriptions, and internal structure, and consumers end up with ad-hoc copies or symlinks that diverge over time. This spec defines how new skills are authored, how they're distributed, and what existing skills must conform to.

## Goals
- Every skill has the same predictable shape on disk
- Skills are discoverable by Claude through precise, trigger-oriented descriptions
- Skills are portable across any project that consumes claude-shared, with no hidden dependencies
- Authors have a clear checklist and template to start from

## Non-Goals
- Downstream project setup and `.claude/` configuration beyond installing the plugin
- Prescribing specific skill contents beyond structural rules
- The exact Claude Code marketplace / plugin-installation UX (owned by Claude Code itself, not by this repository)

## Requirements

### Structure
- **MUST** be authored as a folder named `<name>/` where `<name>` is ASCII kebab-case
- **MUST** contain a `SKILL.md` at the root of the skill folder
- **MUST** include YAML frontmatter in `SKILL.md` with `name` and `description` fields
- **MUST** set `name` to match the folder name exactly
- **MUST** write a `description` that names concrete user triggers, not abstract capabilities, so Claude can reliably decide when to invoke
- **MUST** keep instructions inside `SKILL.md` in English for token efficiency; the skill may still instruct Claude to respond to the user in the user's language
- **MUST** be self-contained—any supporting assets (templates, references, examples) live inside the skill folder

### Source location (claude-shared repository)
- **MUST** live at `skills/<name>/` in the claude-shared source tree
- **MUST** be shipped as part of the `nolte-shared` Claude Code plugin declared by this repository's `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`; no skill in this repository exists outside the plugin scope

### Distribution
- **MUST** reach consuming projects exclusively via the Claude Code plugin mechanism—the plugin is installed from the marketplace entry, and Claude Code discovers the skill from the plugin's `skills/<name>/` path
- **MUST NOT** be distributed by copying the folder into a consuming project's `.claude/skills/<name>/`, by symlinking, by vendoring, or by any other out-of-band path; such copies drift from the source and defeat the point of a shared plugin
- **MUST** bump the plugin version in `.claude-plugin/plugin.json` (and the corresponding marketplace entry) whenever a skill is added, renamed, removed, or materially changes its contract, so consumers can pin a compatible version
- **MAY** coexist in a consuming project alongside project-local skills under that project's own `.claude/skills/`; such project-local skills are outside the scope of this spec and **MUST NOT** reuse a name already owned by the `nolte-shared` plugin

### Runtime discovery (consuming project)
- **MUST** be loadable by Claude Code from the plugin's skills path once the plugin is installed; the skill surfaces to the user as `nolte-shared:<name>`
- **MUST NOT** assume any specific absolute or project-relative runtime path; all internal paths stay relative to the skill folder and work wherever Claude Code extracts or mounts the plugin

### Recommendations
- **SHOULD** include a "Hard rules" section listing invariants that must never be broken
- **SHOULD** keep `SKILL.md` under roughly 150 lines; move long-form content into referenced files
- **SHOULD** place supporting files in conventional subfolders: `templates/`, `references/`, `examples/`
- **MAY** include example user prompts and expected behavior in `examples/`
- **MAY** include a small config schema when the skill requires per-project configuration

## Acceptance Criteria
- [ ] Source folder exists at `skills/<name>/` in claude-shared with `<name>` in ASCII kebab-case
- [ ] Repository contains a valid `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` that expose this skill as part of the `nolte-shared` plugin
- [ ] Skill is discoverable in a consuming project solely by installing the `nolte-shared` plugin from the marketplace—no manual copy or symlink into `.claude/skills/` is needed or permitted
- [ ] Plugin version in `.claude-plugin/plugin.json` has been bumped relative to the previous release whenever a skill is added, renamed, removed, or its contract materially changes
- [ ] `SKILL.md` parses with valid YAML frontmatter containing `name` and `description`
- [ ] `name` in frontmatter equals the folder name
- [ ] `description` mentions the concrete user phrasings that should trigger the skill
- [ ] Skill works when invoked in a downstream project that doesn't contain claude-shared-specific context, loaded through the plugin
- [ ] No hard-coded absolute paths; all internal paths are relative to the skill folder or the project the skill operates on
- [ ] If the skill writes files, the target locations and preconditions are documented

## Open Questions
- Should the folder name be required to match any user-facing slash-command name, or may they differ?
- Do skills need version or compatibility metadata as they evolve?
- Where's the boundary between a skill and an agent? When should a capability be one versus the other?
- Is there a maximum nesting depth for supporting subfolders, or does that stay loose?
