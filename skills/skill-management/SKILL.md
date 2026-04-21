---
name: skill-management
description: Author new Claude Code skills and validate existing ones against the skill-management spec. Invoke when the user says things like "create a new skill", "scaffold a skill for X", "add a skill to this repo", "neuen Skill anlegen", "Skill für X erstellen", "validate this skill", or "check if this skill follows our conventions". Scaffolds the folder under skills/<name>/ (source) or .claude/skills/<name>/ (runtime), writes SKILL.md with valid frontmatter, and audits existing skills for structural compliance with the spec at spec/claude/skill-management/.
---

# Skill Management

Scaffolds and validates Claude Code skills. Applies the rules from `spec/claude/skill-management/<canonical_language>.md` when that spec is present in the current project; otherwise falls back to the conventions embedded here.

## User-language policy

Detect the user's language and respond in it. Skill files themselves (`SKILL.md`, frontmatter, internal instructions) are always written in English for token efficiency — regardless of the user's language.

## Target location

Before writing, decide where the skill should live:

- **claude-shared source tree** (repo contains top-level `skills/` and README referencing "claude-shared"): `skills/<name>/`
- **Consuming project, project-level**: `.claude/skills/<name>/`
- **Consuming project, user-level**: `~/.claude/skills/<name>/`

Detection: if the repo root contains `skills/` and a README referencing `claude-shared`, treat it as the source tree and use `skills/<name>/`. Otherwise, ask the user whether to install project-level or user-level. Default to project-level.

After writing to the source tree, remind the user that for Claude Code's `/skills` dialog to show the skill, it must additionally live at one of the runtime locations (typically via symlink from `skills/<name>/` to `.claude/skills/<name>/`).

## Operations

### 1. Create a new skill

1. Collect from the user (in any language):
   - **Purpose** — what the skill does, one or two sentences.
   - **Triggers** — concrete user phrasings or situations that should invoke it. If vague, ask for examples until you have at least three distinct ones.
   - **Name** — if not given, propose an ASCII-kebab-case name derived from the purpose.
2. Check the target path doesn't already exist. If it does, stop and report.
3. Write `SKILL.md` with:
   - YAML frontmatter: `name` matches folder; `description` enumerates triggers explicitly.
   - A brief body covering: purpose, user-language policy (if relevant), operations, hard rules.
4. Create subfolders (`templates/`, `references/`, `examples/`) only if the user actually needs them. Do not scaffold empty placeholders.
5. Confirm in the user's language with the created paths and the follow-up needed for runtime discovery.

### 2. Validate a skill

Run this checklist against the canonical rules:

- [ ] Folder name is ASCII kebab-case
- [ ] `SKILL.md` exists at folder root
- [ ] Frontmatter parses; contains `name` and `description`
- [ ] `name` equals folder name
- [ ] `description` enumerates concrete user triggers (not abstract capabilities)
- [ ] Instructions body is in English
- [ ] No hard-coded absolute paths inside the skill
- [ ] Supporting assets live inside the skill folder
- [ ] `SKILL.md` is under roughly 150 lines (soft limit)

Report pass/fail per item. Offer to fix mechanical issues (frontmatter mismatch, absolute paths, missing hard rules section) in place.

### 3. Revise

Targeted edits to an existing skill — e.g. rewriting a weak `description`, adding a Hard rules section, trimming overly long instructions. Always re-run validation after a revise operation.

## Hard rules

- Never create a skill at a non-standard path. The only accepted locations are those listed under "Target location".
- Never write a vague `description` like "helps with X" or "for Y tasks". It must enumerate concrete user phrasings so Claude's routing is reliable.
- Never assume the user's purpose — if triggers aren't stated, ask.
- When `spec/claude/skill-management/` disagrees with this skill's instructions, the spec wins. Propose updating this skill rather than silently diverging.
- Never leave a skill half-written. Either all required files are present, or none.
- Do not scaffold empty subfolders or placeholder files "just in case".
