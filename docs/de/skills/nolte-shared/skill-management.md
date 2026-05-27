---
title: skill-management
audience: [maintainer]
content_mode: reference
track: developer-docs
last_updated: generated
---

# skill-management

> Scaffoldet oder überarbeitet einen nolte-shared Claude-Code-Skill-Ordner.

_Author or revise Claude Code skills in the nolte-shared plugin source tree. Invoke when the user asks to create a new skill, scaffold a skill for a given purpose, add a skill to this repo, or revise the authoring shape of an existing skill (rewriting a weak description, adding a Hard rules section, trimming overly long instructions). Also handles equivalent German-language requests. Scaffolds the target skill's folder under skills/ (distribution happens via the plugin mechanism, not via .claude/skills copies) and writes SKILL.md with valid frontmatter. Do NOT use for reviewing or auditing an existing skill against the spec — that produces a persistent, spec-cited review plan and belongs to [`skill-review`](skill-review.md). Do NOT bump the plugin version in a skill-change PR — `release-automation` owns that via the release workflow. For a full spec-conformant draft of a new skill or agent, this skill chains to claude-plugin-developer after name and purpose decisions. Supports resume on re-invocation per `spec/claude/resumable-work/`._

- **Plugin:** `nolte-shared`
- **Phase:** 3 Design (`design`)
- **Tags:** `scaffolding`
- **Quelle:** [skills/skill-management/SKILL.md](https://github.com/nolte/claude-shared/blob/main/skills/skill-management/SKILL.md)

## Anwenden wenn

- you want to create a new skill in the nolte-shared plugin
- you want to revise a weak description or restructure an existing skill
- you want to scaffold SKILL.md with valid frontmatter before writing the body

## Nicht anwenden wenn

- **You want to review an existing skill against the spec and emit a review plan** → [`skill-review`](skill-review.md)
- **You want a full spec-conformant draft (skill or agent), not just the scaffold** → [`claude-plugin-developer`](../../agents/nolte-shared/claude-plugin-developer.md)

## Siehe auch

- [`skill-review`](skill-review.md)
- [`claude-plugin-developer`](../../agents/nolte-shared/claude-plugin-developer.md)

## Beispiele

- **Prompt:** Create a new skill for X
  - **Ergebnis:** skills/x/SKILL.md scaffolded with valid frontmatter; chained to claude-plugin-developer for the spec-conformant draft.

---

## Skill Management

Scaffolds and revises Claude Code skills. Applies the authoring rules from `spec/claude/skill-management/<canonical_language>.md` when that spec is present in the current project; otherwise falls back to the conventions embedded here. Review of an existing skill against the spec is a separate concern — invoke [`skill-review`](skill-review.md) for that; it produces a persistent plan under `.audits/skill-review/` that this skill does not.

### Why this is a skill, not an agent

- **Mid-flow interactivity** — collecting purpose, triggers, and name from the user, plus per-step confirmation when files get written, is interactive by nature; an agent's fire-and-forget contract would lose those checkpoints.
- **Output flows back into the main conversation** — the created folder, the proposed `SKILL.md`, and the follow-up "remember to release the plugin" reminder are all part of the user's working context; isolating them in an agent's structured-report boundary would obscure the path-by-path approval the skill requires.
- **Orchestrator role** — this skill is one step in a broader "ship a new capability" flow that often chains into [`pull-request-create`](pull-request-create.md); the skill-orchestrates pattern (per `skill-vs-agent`) defaults the orchestrator to skill form.
- Counter-dimension considered: a narrower system prompt focused purely on YAML-frontmatter generation could sharpen the output, but the high-impact part is the human conversation about triggers and naming, not the YAML mechanics — interactivity wins.

### User-language policy

Detect the user's language and respond in it. Skill files themselves (`SKILL.md`, frontmatter, internal instructions) are always written in English for token efficiency—regardless of the user's language.

### Target location

This skill is intended to run inside the **claude-shared plugin source tree** (a repo that contains `.claude-plugin/plugin.json` and a top-level `skills/` directory). There, skills always live at `skills/<name>/`. Detection: if `.claude-plugin/plugin.json` exists at the repo root, treat the repo as the source tree and use `skills/<name>/`.

If you're invoked in a project that's **not** a Claude Code plugin source tree, stop and ask the user whether they want:
- to author a **project-local** skill under `.claude/skills/<name>/` (outside the `nolte-shared` plugin scope—this spec doesn't govern it, and the skill won't be shared across projects), or
- to instead author the skill in the `nolte-shared` repository so it can be distributed via the plugin.

Never create a `.claude/skills/<name>/` entry that duplicates a skill already shipped by the `nolte-shared` plugin, and never set up symlinks or copies to make a plugin skill appear under `.claude/skills/`. Distribution to consuming projects is the plugin mechanism's job—see `spec/claude/skill-management/` for the rules.

After creating a skill in the source tree, remind the user that a new plugin release is needed so consumers can pick the skill up through the normal marketplace-install / update flow. The release workflow (see `release-automation` §Plugin manifest alignment) writes the version into `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` automatically at publish time — do **not** bump the version in the skill-creation PR, that is explicitly forbidden by the updated `skill-management` spec.

### Operations

#### 1. Create a new skill

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

#### 2. Revise

Targeted edits to an existing skill — for example rewriting a weak `description`, adding a Hard rules section, trimming overly long instructions, moving long-form content into `templates/` or `references/`. After a revise, invoke [`skill-review`](skill-review.md) to verify the revised skill still conforms to the spec; this skill does not perform its own validation pass.

#### Review / audit

Out of scope. Invoke [`skill-review`](skill-review.md) — it applies every MUST / SHOULD / MAY from `spec/claude/skill-management/` and `spec/claude/skill-vs-agent/`, maps findings to severities (Critical / Warning / Suggestion / Info), and writes a persistent plan to `.audits/skill-review/<name>.md` per `spec/claude/review-plan/`.

### Gotchas

- **The plugin tree is detected by `.claude-plugin/plugin.json`**, not by `skills/` folder presence. A repository with `skills/` but no `plugin.json` isn't a Claude Code plugin source tree; the skill refuses to scaffold there and routes the operator to [`project-structure-apply`](project-structure-apply.md) first.
- **Never bump `version` in `.claude-plugin/plugin.json` from this skill.** Plugin versioning is owned exclusively by the release workflow (per `release-automation` §Version-bearing files); a skill-change PR that touches the version field will conflict with the release workflow's own update. The release workflow runs from `develop` after the alignment commit lands.
- **The `## Reserved-token rationale` exception** added to `skill-management` §Frontmatter validation in 2026-Q2 is a `nolte-shared` plugin-specific narrowing — the upstream Anthropic platform validator rejects names containing `claude` / `anthropic` regardless. When scaffolding for a project that submits skills through Anthropic's intake path (rather than the `nolte-shared` plugin marketplace), don't apply the exception. The local `scripts/validate_skills.py` validator honours it, but the upstream one doesn't.
- **`description` length is measured in characters, not bytes.** The 1024-character cap counts grapheme clusters; multi-byte UTF-8 sequences (German umlauts, em-dashes) count as one character each, not as their byte length. `len(description)` in Python and the local validator both use the character count; don't surprise the operator with a "1024-byte cap" framing.
- **Folder name and `name` frontmatter MUST match exactly.** A typo in either is a `Critical` per spec. The skill verifies the match before any write; renaming a skill is a coordinated rename of the folder, the frontmatter, and every cross-reference (`grep -RIn '<old-name>' spec/ skills/ agents/ docs/ project/`).

### Examples

- Read `examples/01-scaffold-new-skill.md` when scaffolding a brand-new skill from scratch.
- Read `examples/02-revise-existing-frontmatter.md` when revising frontmatter fields on an already-existing skill.
- Read `examples/03-route-to-skill-review.md` when the user asks for a skill review and this skill routes them to [`skill-review`](skill-review.md).

### Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/skill-management/<run-id>.yml` after every successful user-approval gate and after each named phase boundary. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope (`schema_version`, `run_id`, `inputs`, `phase`, `decisions[]`, `status`, ...) and the fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

### Hard rules

- Never create a skill at a non-standard path. Inside a plugin source tree the only accepted location is `skills/<name>/`; everywhere else, stop and ask the user whether to switch to the plugin repository instead.
- Never distribute a plugin-owned skill by copying it into a consuming project's `.claude/skills/`, by symlinking, or by any other out-of-band path. Distribution is the plugin mechanism's job.
- Never write a vague `description` like "helps with X" or "for Y tasks." It must enumerate concrete user phrasings so Claude's routing is reliable.
- Never assume the user's purpose—if triggers aren't stated, ask.
- When `spec/claude/skill-management/` disagrees with this skill's instructions, the spec wins. Propose updating this skill rather than silently diverging.
- Never leave a skill half-written. Either all required files are present, or none.
- Don't scaffold empty subfolders or placeholder files "just in case."
