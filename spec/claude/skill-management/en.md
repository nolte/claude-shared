# Claude Skill Authoring

Status: draft

## Context
The claude-shared repository collects reusable Claude Code skills and agents that downstream projects consume. A skill has two lives: a **source** form in this repository (under `skills/`), and a **runtime** form in a consuming project (under `.claude/skills/` or `~/.claude/skills/`) where Claude Code actually loads it. Without a consistent shape, skills drift in naming, trigger descriptions, and internal structure, which makes reuse fragile and maintenance harder. This spec defines how new skills are authored, where they live in both forms, and what existing skills must conform to.

## Goals
- Every skill has the same predictable shape on disk
- Skills are discoverable by Claude through precise, trigger-oriented descriptions
- Skills are portable across any project that consumes claude-shared, with no hidden dependencies
- Authors have a clear checklist and template to start from

## Non-Goals
- Plugin packaging and distribution (covered separately)
- Downstream project setup and `.claude/` configuration
- Prescribing specific skill contents beyond structural rules

## Requirements

### Structure
- **MUST** be authored as a folder named `<name>/` where `<name>` is ASCII kebab-case
- **MUST** contain a `SKILL.md` at the root of the skill folder
- **MUST** include YAML frontmatter in `SKILL.md` with `name` and `description` fields
- **MUST** set `name` to match the folder name exactly
- **MUST** write a `description` that names concrete user triggers, not abstract capabilities, so Claude can reliably decide when to invoke
- **MUST** keep instructions inside `SKILL.md` in English for token efficiency; the skill may still instruct Claude to respond to the user in the user's language
- **MUST** be self-contained — any supporting assets (templates, references, examples) live inside the skill folder

### Source location (claude-shared repository)
- **MUST** live at `skills/<name>/` in the claude-shared source tree, so it can be copied, symlinked, or bundled into a plugin for distribution

### Runtime location (consuming project)
- **MUST** be loadable by Claude Code from one of the standard locations:
  - `.claude/skills/<name>/` — project-level installation
  - `~/.claude/skills/<name>/` — user-level installation
  - the plugin's designated skills path when delivered as part of a plugin
- **MUST NOT** assume a particular install location; all internal paths stay relative to the skill folder and work in any of the above

### Recommendations
- **SHOULD** include a "Hard rules" section listing invariants that must never be broken
- **SHOULD** keep `SKILL.md` under roughly 150 lines; move long-form content into referenced files
- **SHOULD** place supporting files in conventional subfolders: `templates/`, `references/`, `examples/`
- **MAY** include example user prompts and expected behavior in `examples/`
- **MAY** include a small config schema when the skill requires per-project configuration

## Acceptance Criteria
- [ ] Source folder exists at `skills/<name>/` in claude-shared with `<name>` in ASCII kebab-case
- [ ] Skill can be deployed to `.claude/skills/<name>/` (or `~/.claude/skills/<name>/`) in a consuming project and is loaded by Claude Code from there
- [ ] `SKILL.md` parses with valid YAML frontmatter containing `name` and `description`
- [ ] `name` in frontmatter equals the folder name
- [ ] `description` mentions the concrete user phrasings that should trigger the skill
- [ ] Skill works when invoked in a downstream project that does not contain claude-shared-specific context
- [ ] No hard-coded absolute paths; all internal paths are relative to the skill folder or the project the skill operates on
- [ ] If the skill writes files, the target locations and preconditions are documented

## Open Questions
- Should the folder name be required to match any user-facing slash-command name, or may they differ?
- Do skills need version or compatibility metadata as they evolve?
- Where is the boundary between a skill and an agent? When should a capability be one versus the other?
- Is there a maximum nesting depth for supporting subfolders, or does that stay loose?
