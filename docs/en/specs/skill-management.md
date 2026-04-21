# Skill Authoring

This page summarizes the specification at `spec/claude/skill-management/en.md` (canonical source).

**Status:** draft

## Context

The claude-shared repository collects reusable Claude Code skills and agents that downstream projects consume. A skill has two lives:

- **Source form** in this repository: `skills/<name>/`
- **Runtime form** in a consuming project: `.claude/skills/<name>/` or `~/.claude/skills/<name>/`

Without a consistent shape, skills drift in naming, trigger descriptions, and internal structure — reuse becomes fragile and maintenance harder.

## Goals and Non-Goals

**Goals**

- Every skill has the same predictable shape on disk
- Skills are discoverable by Claude through precise, trigger-oriented descriptions
- Skills are portable across any project that consumes claude-shared
- Authors have a clear checklist and template

**Non-Goals**

- Plugin packaging and distribution (covered separately)
- `.claude/` configuration in downstream projects
- Prescribing specific skill contents beyond structural rules

## Requirements (excerpt)

### Structure

- **MUST** be authored as a folder `<name>/` in ASCII kebab-case
- **MUST** contain `SKILL.md` at the folder root
- **MUST** include YAML frontmatter with `name` and `description`
- **MUST** set `name` to match the folder name exactly
- **MUST** write a `description` that names concrete user triggers, not abstract capabilities
- **MUST** keep instructions in `SKILL.md` in English for token efficiency
- **MUST** be self-contained — supporting assets live inside the skill folder

### Locations

Source: `skills/<name>/` in claude-shared. Runtime: `.claude/skills/<name>/`, `~/.claude/skills/<name>/`, or the plugin path. No hard-coded absolute paths.

### Recommendations

- **SHOULD** include a "Hard rules" section for invariants
- **SHOULD** keep `SKILL.md` under roughly 150 lines
- **SHOULD** group supporting files in `templates/`, `references/`, `examples/`

## Acceptance Criteria

- [ ] Source folder exists at `skills/<name>/` with `<name>` in ASCII kebab-case
- [ ] Skill is loadable in a consuming project from `.claude/skills/<name>/`
- [ ] `SKILL.md` parses with valid YAML frontmatter (`name`, `description`)
- [ ] `name` in frontmatter equals the folder name
- [ ] `description` mentions concrete user phrasings that trigger the skill
- [ ] Skill works in a downstream project without claude-shared-specific context
- [ ] No hard-coded absolute paths; all internal paths relative to the skill folder
- [ ] If the skill writes files, target locations and preconditions are documented

## Open Questions

- Should the folder name be required to match the user-facing slash-command name?
- Do skills need version or compatibility metadata?
- Where is the boundary between a skill and an agent?
- Is there a maximum nesting depth for supporting subfolders?

## Full text

- Canonical (EN): `spec/claude/skill-management/en.md`
- Translation (DE): `spec/claude/skill-management/de.md`
