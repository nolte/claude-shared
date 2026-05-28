---
title: Skill Management
audience: [maintainer]
content_mode: explanation
track: developer-docs
last_updated: 2026-05-19
---

# Skill management

The `skill-management` skill scaffolds and validates Claude Code skills. It lives at `skills/skill-management/SKILL.md` and follows the [Skill Authoring](../references/specs/skill-management.md) spec.

## When to use

- "create a new skill," "scaffold a skill for X," "add a skill to this repo"
<!-- vale Vale.Spelling = NO -->
- "neuen Skill anlegen," "Skill für X erstellen"
<!-- vale Vale.Spelling = YES -->
- "validate this skill," "check if this skill follows the project conventions"

## Deciding the target location

Before writing, the skill picks where to place the new files:

| Context | Target path |
|---------|-------------|
| `claude-shared` source tree (top-level `skills/`, README mentions `claude-shared`) | `skills/<name>/` |
| Consuming project, project-level | `.claude/skills/<name>/` |
| Consuming project, user-level | `~/.claude/skills/<name>/` |

After writing into the source tree, the skill reminds you that the `/skills` dialog additionally needs a runtime location—typically via symlink from `skills/<name>/` to `.claude/skills/<name>/`.

## Operations

### 1. Create a new skill

1. Collect from the user: **Purpose**, **Triggers** (at least three concrete phrasings), **Name** (ASCII kebab-case).
2. Check the target path doesn't already exist.
3. Write `SKILL.md` with frontmatter (`name`, `description`) and a short body (purpose, language policy, operations, hard rules).
4. Create subfolders (`templates/`, `references/`, `examples/`) only when actually needed—no empty placeholders.
5. Confirm in the user's language with the created paths.

### 2. Validate

Checklist the skill runs:

- [ ] Folder name is ASCII kebab-case
- [ ] `SKILL.md` exists at the folder root
- [ ] Frontmatter parses; contains `name` and `description`
- [ ] `name` equals the folder name
- [ ] `description` enumerates concrete user triggers (not abstract capabilities)
- [ ] Instructions body is in English
- [ ] No hard-coded absolute paths
- [ ] Supporting assets live inside the skill folder
- [ ] `SKILL.md` under roughly 150 lines (soft limit)

Pass/fail per item. Mechanical issues (frontmatter mismatch, absolute paths, missing hard-rules section) can be autofixed on request.

### 3. Revise

Targeted edits to an existing skill: sharpen a weak `description`, add a Hard Rules section, trim overly long instructions. Validation re-runs after every revision.

## Hard rules

- Never scaffold at a non-standard path.
- Never write a vague `description` like "helps with X."
- Never assume the user's intent—if triggers aren't stated, ask.
- When the spec disagrees with this skill's instructions, the spec wins; propose updating the skill rather than silently diverging.
- Never leave a skill half-written.

## Sources

- Skill file: `skills/skill-management/SKILL.md`
- Specification: [`spec/claude/skill-management/`](../references/specs/skill-management.md)
