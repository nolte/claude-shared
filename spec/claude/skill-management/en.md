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

### Source location (claude-shared repository)
- **MUST** live at `skills/<name>/` in the claude-shared source tree
- **MUST** be shipped as part of the `nolte-shared` Claude Code plugin declared by this repository's `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`; no skill in this repository exists outside the plugin scope

### Distribution
- **MUST** reach consuming projects exclusively via the Claude Code plugin mechanism—the plugin is installed from the marketplace entry, and Claude Code discovers the skill from the plugin's `skills/<name>/` path
- **MUST NOT** be distributed by copying the folder into a consuming project's `.claude/skills/<name>/`, by symlinking, by vendoring, or by any other out-of-band path; such copies drift from the source and defeat the point of a shared plugin
- **MUST NOT** manually bump the plugin version in `.claude-plugin/plugin.json` or the corresponding marketplace entry as part of a PR that adds, renames, removes, or materially changes a skill; the version is derived from the published GitHub Release tag and updated on the default branch exclusively by the release workflow—see `release-automation` §Version-bearing file alignment for the mechanism (including the fallback path where a maintainer opens a dedicated `chore(release): <tag>` PR)
- **MAY** coexist in a consuming project alongside project-local skills under that project's own `.claude/skills/`; such project-local skills are outside the scope of this spec and **MUST NOT** reuse a name already owned by the `nolte-shared` plugin

### Runtime discovery (consuming project)
- **MUST** be loadable by Claude Code from the plugin's skills path once the plugin is installed; the skill surfaces to the user as `nolte-shared:<name>`
- **MUST NOT** assume any specific absolute or project-relative runtime path; all internal paths stay relative to the skill folder and work wherever Claude Code extracts or mounts the plugin

### Recommendations
- **SHOULD** include a "Hard rules" section listing invariants that must never be broken
- **SHOULD** keep `SKILL.md` under roughly 150 lines as a soft target; move long-form content into referenced files
- **SHOULD** place supporting files in conventional subfolders: `templates/` (or `assets/`), `references/`, `examples/`, `scripts/`
- **MAY** include example user prompts and expected behavior in `examples/`
- **MAY** include a small config schema when the skill requires per-project configuration

### Authoring quality (per Anthropic skill-creation best practices)

Tracks the public guidance at <https://agentskills.io/skill-creation/best-practices>; cite the source slug when a finding pins a specific rule.

- **MUST** keep `SKILL.md` under 500 lines and 5,000 tokens (the upstream hard cap); content beyond that **MUST** move into `references/`, `templates/`/`assets/`, or `scripts/` and **MUST** carry an explicit load-trigger phrase ("Read X when Y", "use template Z for output Q") in `SKILL.md` so progressive disclosure works as designed
- **SHOULD** include a **Gotchas** section listing concrete corrections to non-obvious environment facts the agent would otherwise get wrong; this is distinct from the **Hard rules** section (invariants) and from generic advice
- **SHOULD** match specificity to fragility (give the agent freedom plus the *why* for flexible tasks; be prescriptive for fragile or sequential operations), **provide a clear default** rather than a menu of equal options, and **favor procedures over declarations** (teach how to approach a class of problem, not what to produce for one instance)
- **SHOULD** ground the skill in real expertise — extract from a hands-on task or synthesize from project-specific artifacts (runbooks, code-review comments, version history, failure cases) rather than from generic LLM output alone
- **MAY** bundle reusable scripts in `scripts/` when iteration shows the agent re-inventing the same logic each run, and **MAY** add a **Validation loop** or **Plan-validate-execute** subsection when the skill performs batch or destructive operations

## Acceptance Criteria
- [ ] Source folder exists at `skills/<name>/` in claude-shared with `<name>` in ASCII kebab-case
- [ ] Repository contains a valid `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` that expose this skill as part of the `nolte-shared` plugin
- [ ] Skill is discoverable in a consuming project solely by installing the `nolte-shared` plugin from the marketplace—no manual copy or symlink into `.claude/skills/` is needed or permitted
- [ ] Plugin version in `.claude-plugin/plugin.json` equals the latest published GitHub Release tag (maintained per `release-automation` §Version-bearing file alignment, not by skill-change PRs); no diff to the `version` field appears in any PR whose sole purpose is adding, renaming, or removing a skill
- [ ] `SKILL.md` parses with valid YAML frontmatter containing `name` and `description`
- [ ] `name` in frontmatter equals the folder name
- [ ] `description` mentions the concrete user phrasings that should trigger the skill
- [ ] If `tags` is declared in frontmatter, every entry is a lowercase ASCII kebab-case string ≤30 characters and the list contains at most 5 entries
- [ ] Skill works when invoked in a downstream project that doesn't contain claude-shared-specific context, loaded through the plugin
- [ ] No hard-coded absolute paths; all internal paths are relative to the skill folder or the project the skill operates on
- [ ] If the skill writes files, the target locations and preconditions are documented
- [ ] Reviewing an individual skill against this spec follows `spec/claude/skill-review/`; review output conforms to `spec/claude/review-plan/` and lives under `.audits/skill-review/<name>.md`
- [ ] Every skill's `SKILL.md` is under 500 lines and 5,000 tokens, and every referenced asset under `references/` / `templates/` / `assets/` / `scripts/` is paired with an explicit load-trigger phrase in `SKILL.md`

## Open Questions
- Should the folder name be required to match any user-facing slash-command name, or may they differ?
- Do skills need version or compatibility metadata as they evolve?
- Where's the boundary between a skill and an agent? When should a capability be one versus the other?
- Is there a maximum nesting depth for supporting subfolders, or does that stay loose?
