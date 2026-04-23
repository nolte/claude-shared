---
name: skill-management
description: Author new Claude Code skills and validate existing ones against the skill-management spec. Invoke when the user asks to create a new skill, scaffold a skill for a given purpose, add a skill to this repo, validate a skill, or check that a skill follows project conventions. Also handles equivalent German-language requests. Scaffolds the folder under skills/<name>/ inside the claude-shared plugin source tree (distribution happens via the plugin mechanism, not via .claude/skills copies), writes SKILL.md with valid frontmatter, and audits existing skills for structural compliance with the spec at spec/claude/skill-management/.
---

# Skill Management

Scaffolds and validates Claude Code skills. Applies the rules from `spec/claude/skill-management/<canonical_language>.md` when that spec is present in the current project; otherwise falls back to the conventions embedded here.

## User-language policy

Detect the user's language and respond in it. Skill files themselves (`SKILL.md`, frontmatter, internal instructions) are always written in English for token efficiency—regardless of the user's language.

## Target location

This skill is intended to run inside the **claude-shared plugin source tree** (a repo that contains `.claude-plugin/plugin.json` and a top-level `skills/` directory). There, skills always live at `skills/<name>/`. Detection: if `.claude-plugin/plugin.json` exists at the repo root, treat the repo as the source tree and use `skills/<name>/`.

If you're invoked in a project that's **not** a Claude Code plugin source tree, stop and ask the user whether they want:
- to author a **project-local** skill under `.claude/skills/<name>/` (outside the `nolte-shared` plugin scope—this spec doesn't govern it, and the skill won't be shared across projects), or
- to instead author the skill in the `nolte-shared` repository so it can be distributed via the plugin.

Never create a `.claude/skills/<name>/` entry that duplicates a skill already shipped by the `nolte-shared` plugin, and never set up symlinks or copies to make a plugin skill appear under `.claude/skills/`. Distribution to consuming projects is the plugin mechanism's job—see `spec/claude/skill-management/` for the rules.

After creating a skill in the source tree, remind the user to:
1. bump the plugin version in `.claude-plugin/plugin.json` (and `.claude-plugin/marketplace.json`) whenever a skill is added, renamed, removed, or its contract materially changes, and
2. publish a new plugin release so consumers can pick the skill up through the normal marketplace-install / update flow.

## Operations

### 1. Create a new skill

1. Collect from the user (in any language):
   - **Purpose**: what the skill does, one or two sentences.
   - **Triggers**: concrete user phrasings or situations that should invoke it. If vague, ask for examples until you have at least three distinct ones.
   - **Name**: if not given, propose an ASCII-kebab-case name derived from the purpose.
2. Check the target path doesn't already exist. If it does, stop and report.
3. Write `SKILL.md` with:
   - YAML frontmatter: `name` matches folder; `description` enumerates triggers explicitly.
   - A brief body covering: purpose, user-language policy (if relevant), operations, hard rules.
4. Create subfolders (`templates/`, `references/`, `examples/`) only if the user actually needs them. Don't scaffold empty placeholders.
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
- [ ] Repository that hosts the skill declares `.claude-plugin/plugin.json` and a marketplace entry, meaning the skill is part of a Claude Code plugin, not a loose `.claude/skills/` copy

Report pass/fail per item. Offer to fix mechanical issues (frontmatter mismatch, absolute paths, missing hard rules section) in place.

### 3. Revise

Targeted edits to an existing skill—for example rewriting a weak `description`, adding a Hard rules section, trimming overly long instructions. Always re-run validation after a revise operation.

## Hard rules

- Never create a skill at a non-standard path. Inside a plugin source tree the only accepted location is `skills/<name>/`; everywhere else, stop and ask the user whether to switch to the plugin repository instead.
- Never distribute a plugin-owned skill by copying it into a consuming project's `.claude/skills/`, by symlinking, or by any other out-of-band path. Distribution is the plugin mechanism's job.
- Never write a vague `description` like "helps with X" or "for Y tasks." It must enumerate concrete user phrasings so Claude's routing is reliable.
- Never assume the user's purpose—if triggers aren't stated, ask.
- When `spec/claude/skill-management/` disagrees with this skill's instructions, the spec wins. Propose updating this skill rather than silently diverging.
- Never leave a skill half-written. Either all required files are present, or none.
- Don't scaffold empty subfolders or placeholder files "just in case."
