---
name: skill-management
description: Author or revise Claude Code skills in the nolte-shared plugin source tree. Invoke when the user asks to create a new skill, scaffold a skill for a given purpose, add a skill to this repo, or revise the authoring shape of an existing skill (rewriting a weak description, adding a Hard rules section, trimming overly long instructions). Also handles equivalent German-language requests. Scaffolds the folder under skills/<name>/ (distribution happens via the plugin mechanism, not via .claude/skills copies) and writes SKILL.md with valid frontmatter. Do NOT use for reviewing or auditing an existing skill against the spec — that produces a persistent, spec-cited review plan and belongs to `skill-review`. Do NOT bump the plugin version in a skill-change PR — `release-automation` owns that via the release workflow.
tags: [scaffolding]
---

# Skill Management

Scaffolds and revises Claude Code skills. Applies the authoring rules from `spec/claude/skill-management/<canonical_language>.md` when that spec is present in the current project; otherwise falls back to the conventions embedded here. Review of an existing skill against the spec is a separate concern — invoke `skill-review` for that; it produces a persistent plan under `.audits/skill-review/` that this skill does not.

## Why this is a skill, not an agent

- **Mid-flow interactivity** — collecting purpose, triggers, and name from the user, plus per-step confirmation when files get written, is interactive by nature; an agent's fire-and-forget contract would lose those checkpoints.
- **Output flows back into the main conversation** — the created folder, the proposed `SKILL.md`, and the follow-up "remember to release the plugin" reminder are all part of the user's working context; isolating them in an agent's structured-report boundary would obscure the path-by-path approval the skill requires.
- **Orchestrator role** — this skill is one step in a broader "ship a new capability" flow that often chains into `pull-request-create`; the skill-orchestrates pattern (per `skill-vs-agent`) defaults the orchestrator to skill form.
- Counter-dimension considered: a narrower system prompt focused purely on YAML-frontmatter generation could sharpen the output, but the high-impact part is the human conversation about triggers and naming, not the YAML mechanics — interactivity wins.

## User-language policy

Detect the user's language and respond in it. Skill files themselves (`SKILL.md`, frontmatter, internal instructions) are always written in English for token efficiency—regardless of the user's language.

## Target location

This skill is intended to run inside the **claude-shared plugin source tree** (a repo that contains `.claude-plugin/plugin.json` and a top-level `skills/` directory). There, skills always live at `skills/<name>/`. Detection: if `.claude-plugin/plugin.json` exists at the repo root, treat the repo as the source tree and use `skills/<name>/`.

If you're invoked in a project that's **not** a Claude Code plugin source tree, stop and ask the user whether they want:
- to author a **project-local** skill under `.claude/skills/<name>/` (outside the `nolte-shared` plugin scope—this spec doesn't govern it, and the skill won't be shared across projects), or
- to instead author the skill in the `nolte-shared` repository so it can be distributed via the plugin.

Never create a `.claude/skills/<name>/` entry that duplicates a skill already shipped by the `nolte-shared` plugin, and never set up symlinks or copies to make a plugin skill appear under `.claude/skills/`. Distribution to consuming projects is the plugin mechanism's job—see `spec/claude/skill-management/` for the rules.

After creating a skill in the source tree, remind the user that a new plugin release is needed so consumers can pick the skill up through the normal marketplace-install / update flow. The release workflow (see `release-automation` §Plugin manifest alignment) writes the version into `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` automatically at publish time — do **not** bump the version in the skill-creation PR, that is explicitly forbidden by the updated `skill-management` spec.

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

### 2. Revise

Targeted edits to an existing skill — for example rewriting a weak `description`, adding a Hard rules section, trimming overly long instructions, moving long-form content into `templates/` or `references/`. After a revise, invoke `skill-review` to verify the revised skill still conforms to the spec; this skill does not perform its own validation pass.

### Review / audit

Out of scope. Invoke `skill-review` — it applies every MUST / SHOULD / MAY from `spec/claude/skill-management/` and `spec/claude/skill-vs-agent/`, maps findings to severities (BLOCKER / WARNING / SUGGESTION / INFO), and writes a persistent plan to `.audits/skill-review/<name>.md` per `spec/claude/review-plan/`.

## Hard rules

- Never create a skill at a non-standard path. Inside a plugin source tree the only accepted location is `skills/<name>/`; everywhere else, stop and ask the user whether to switch to the plugin repository instead.
- Never distribute a plugin-owned skill by copying it into a consuming project's `.claude/skills/`, by symlinking, or by any other out-of-band path. Distribution is the plugin mechanism's job.
- Never write a vague `description` like "helps with X" or "for Y tasks." It must enumerate concrete user phrasings so Claude's routing is reliable.
- Never assume the user's purpose—if triggers aren't stated, ask.
- When `spec/claude/skill-management/` disagrees with this skill's instructions, the spec wins. Propose updating this skill rather than silently diverging.
- Never leave a skill half-written. Either all required files are present, or none.
- Don't scaffold empty subfolders or placeholder files "just in case."
