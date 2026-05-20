# Claude Skill Authoring

Status: draft

## Context
The `claude-shared` repository collects reusable Claude Code skills and agents that downstream projects consume. A skill has two lives: a **source** form in this repository (under `skills/`) and a **runtime** form in a consuming project, where Claude Code actually loads it. The only supported runtime-distribution path is the Claude Code plugin mechanism: this repository is itself a Claude Code plugin (`.claude-plugin/plugin.json` plus a marketplace entry), and consuming projects pick up skills by installing the plugin. Without a consistent shape and a single distribution path, skills drift in naming, trigger descriptions, and internal structure, and consumers end up with ad-hoc copies or symlinks that diverge over time. This spec defines how new skills are authored, how they're distributed, and what existing skills must conform to.

## Goals
- Every skill has the same predictable shape on disk
- Skills are discoverable by Claude through precise, trigger-oriented descriptions
- Skills are portable across any project that consumes `claude-shared`, with no hidden dependencies
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
- **MUST** include a `phase` field in YAML frontmatter whose value is exactly one identifier from the eight-value vocabulary declared in `skill-agent-catalog` §Phase classification (`vision`, `plan`, `design`, `build`, `review`, `quality`, `close-release`, `cross-cutting`); the catalog generator fails the docs build when `phase` is missing or out of vocabulary

### Frontmatter validation (Agent Skills spec & Anthropic platform limits)

Tracks the formal Agent Skills specification ([R1](#references)) and Anthropic's published validation rules ([R2](#references)); cite the source slug when a finding pins a specific limit.

- **MUST** keep `name` between 1 and 64 characters, contain only lowercase ASCII letters, digits, and hyphens, **MUST NOT** start or end with a hyphen, and **MUST NOT** contain consecutive hyphens (`--`)
- **MUST NOT** use the reserved words `anthropic` or `claude` as the value of `name` or anywhere within `name`, per the upstream platform validator. The reserved-word rule **applies only to `name`**: descriptive fields like `description` may legitimately mention `claude` (for example "Claude Code skill for X") and many existing skills do, so restricting `description` would force unnatural circumlocutions ("the assistant" / "the agent runtime") without any platform-validator gain
  - **Narrow exception** for artefacts whose primary responsibility is authoring or maintaining a Claude Code or Anthropic platform surface (for example a `claude-plugin-developer` agent that exists to scaffold Claude Code plugins): the reserved-token ban **MAY** be waived when the artefact body carries a `## Reserved-token rationale` section that names the platform surface and cites this exception. The local validator (`scripts/validate_skills.py`) honours the exception by suppressing the `frontmatter-name-reserved` Critical when that body section is present; the upstream Anthropic platform validator doesn't honour it, so consumers who route the artefact through the upstream intake path **MUST** rename it. This exception trades platform-validator-mirror parity for the discovery anchor that the reserved token provides; don't introduce new artefacts under this exception unless the responsibility genuinely targets the Claude or Anthropic surface itself
- **MUST NOT** include XML tags inside the `name` or `description` values
- **MUST** keep `description` non-empty and **MUST NOT** exceed 1024 characters
- **MUST** write `description` in **third person** ("Generates …," "Reviews …"), never first or second person ("I help …," "You can use this to …"), because the description is injected into Claude's system prompt and inconsistent point-of-view degrades skill discovery ([R2](#references))
- **MUST** include in `description` both *what the skill does* and *when to use it*, the two halves of the discovery contract; pure capability statements without trigger phrases fail the discovery half
- **SHOULD**, when also using Claude Code's optional `when_to_use` field ([R3](#references)), keep the combined `description` + `when_to_use` text under 1,536 characters; the runtime truncates anything beyond that cap and the truncation typically eats the trigger phrases
- **SHOULD** prefer the **gerund form** for the skill name (verb + `-ing`: `processing-pdfs`, `analyzing-spreadsheets`, `managing-databases`) per Anthropic's published convention; verb-noun (`process-pdfs`) and noun phrases (`pdf-processing`) are acceptable alternatives, mixed forms across one repository aren't ([R2](#references))
  - **`nolte-shared` plugin choice**: this repository ships every skill in **verb-noun form** (`pull-request-create`, `roadmap-init`, `feature-decompose`, `dependency-audit`, `quality-gate`, plus the rest of the surface). The choice is recorded here so a reviewer doesn't flag the convention on every iteration. Renaming the existing surface to gerund form would be a breaking change for every downstream consumer's `subagent_type:` callers and isn't planned. New skills in this plugin **MUST** follow the verb-noun convention; mixing in a gerund-form name would itself violate the "mixed forms across one repository aren't acceptable" half of the upstream rule. A future coordinated portfolio rename (with a deprecation period) **MAY** flip the choice; until that ships, verb-noun is the rule
- **MUST NOT** use vague or generic names like `helper`, `utils`, `tools`, `documents`, `data`, or `files`; they defeat discovery because Claude can't tell what the skill does from its name alone ([R2](#references))

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

### Source location (`claude-shared` repository)
- **MUST** live at `skills/<name>/` in the `claude-shared` source tree
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

Tracks the public guidance at <https://agentskills.io/skill-creation/best-practices> ([R4](#references)) and the official Anthropic skill-authoring page ([R2](#references)); cite the source slug when a finding pins a specific rule.

- **MUST** keep `SKILL.md` under 500 lines and 5,000 tokens (the upstream hard cap, restated identically in the formal spec ([R1](#references)) and the best-practices page ([R2](#references))); content beyond that **MUST** move into `references/`, `templates/`/`assets/`, or `scripts/` and **MUST** carry an explicit load-trigger phrase ("Read X when Y," "use template Z for output Q") in `SKILL.md` so progressive disclosure works as designed
- **SHOULD** include a **Gotchas** section listing concrete corrections to non-obvious environment facts the agent would otherwise get wrong; this is distinct from the **Hard rules** section (invariants) and from generic advice ([R4](#references))
- **SHOULD** match specificity to fragility (give the agent freedom plus the *why* for flexible tasks; be prescriptive for fragile or sequential operations), **provide a clear default** rather than a menu of equal options, and **favor procedures over declarations** (teach how to approach a class of problem, not what to produce for one instance) ([R4](#references))
- **SHOULD** ground the skill in real expertise—extract from a hands-on task or synthesize from project-specific artifacts (runbooks, code-review comments, version history, failure cases) rather than from generic LLM output alone ([R4](#references))
- **SHOULD** apply the **Default assumption: Claude is already very smart** test before adding any explanatory paragraph—challenge each piece of content with "Does Claude really need this explanation? Does this paragraph justify its token cost?" and cut content that fails the test ([R2](#references))
- **SHOULD** use **consistent terminology** throughout the skill: pick one term for each concept ("API endpoint" vs. "URL" vs. "API route") and stick to it; mixed terminology measurably degrades instruction-following ([R2](#references))
- **MUST NOT** include time-sensitive information that will become wrong (for example "before August 2025, use the old API"); historical context belongs inside an explicit `## Old patterns` collapsible section, never inline ([R2](#references))
- **MUST** use forward-slash paths (`scripts/helper.py`, `references/guide.md`) in every reference inside the skill, never Windows-style backslashes—Unix paths work everywhere; Windows-style paths break on Unix ([R2](#references))
- **MUST**, when referencing MCP tools from skill prose, use fully qualified `ServerName:tool_name` syntax (`BigQuery:bigquery_schema`, not `bigquery_schema`); without the server prefix the runtime fails to locate the tool when multiple MCP servers are present ([R2](#references))
- **MAY** bundle reusable scripts in `scripts/` when iteration shows the agent re-inventing the same logic each run, and **MAY** add a **Validation loop** or **Plan-validate-execute** subsection when the skill performs batch or destructive operations ([R2](#references), [R4](#references))
- **SHOULD**, when bundling scripts, **solve don't punt**: the script handles its own error cases (missing file → create with default; permission denied → fall back gracefully) instead of failing and leaving Claude to recover ([R2](#references))
- **SHOULD** justify every configuration constant the script declares; "voodoo constants" (`TIMEOUT = 47`, `RETRIES = 5`) without an inline comment explaining the value are a `Warning`-grade authoring smell ([R2](#references))
- **MUST**, in any prose that mentions a script, make the **execution intent explicit**: write either "Run `analyze_form.py` to extract fields" (execute) or "See `analyze_form.py` for the field extraction algorithm" (read as reference); ambiguity here causes Claude to make the wrong choice and waste tokens ([R2](#references))

### Operations vocabulary

Skills with multiple named operations use a `## Operations` block. This section governs the naming and heading form of that block so that skill authors, reviewers, and the sweep tooling share a consistent vocabulary.

- **MUST** use `## Operations` (plural) as the heading for the operations block; singular `## Operation` is non-conformant
- **MUST** name each operation with one verb from the closed vocabulary: `audit` (read-only check), `scaffold` (greenfield create), `patch` (additive fix), `apply` (audit + scaffold + patch in one flow), `migrate` (brownfield → conforming), `run` (default verb for skills with one operation), `update` (mutate an existing artefact), `close` (terminate a lifecycle)
- **MUST NOT** introduce new operation verbs without amending this list
- **MUST** title sub-operations as `### N. <verb>` (numbered) or `### `<verb>`` (backtick-quoted command); alphabetic letters (`A.`/`B.`/`C.`) and `### Step N` are non-conformant
- **SHOULD** retain operation names short (single word) and consistent within a skill cluster (e.g. lifecycle skills should align verbs)

### Progressive disclosure & file references

Skills are loaded in three stages by Claude—metadata at startup (~100 tokens per skill), full `SKILL.md` body when triggered, supporting files only when explicitly read ([R5](#references), [R1](#references)). The on-disk shape **MUST** support that loading model.

- **MUST** keep file references inside `SKILL.md` **at most one level deep**: `SKILL.md` → `references/foo.md` is fine; `SKILL.md` → `references/foo.md` → `references/bar.md` is forbidden, because Claude tends to use partial reads (`head -100`) on nested references and then misses content ([R2](#references))
- **MUST** include a **table of contents** at the top of any reference file longer than 100 lines, so partial-read previews still surface the file's full scope ([R2](#references))
- **MUST**, every time `SKILL.md` references a supporting file, name **what the file contains** and **when to load it** (for example "Read `references/api-errors.md` if the API returns a non-200 status code"); generic "see `references/` for details" defeats progressive disclosure because Claude has no signal for *when* to load ([R2](#references), [R4](#references))
- **MUST** carry an explicit load-trigger phrase in `SKILL.md` for every asset under `references/`, `templates/`, `assets/`, `scripts/`, or `examples/`. Pattern: `"Read <relative-path> when <trigger condition>"` or `"See <relative-path> for <specific concern>"` (with an explicit "when" or "for" clause). Implicit references without a load-trigger are non-conformant since Claude won't surface the asset under progressive disclosure.
- **SHOULD** organize supporting files by **domain** when the skill spans multiple subjects (`reference/finance.md`, `reference/sales.md`, `reference/product.md`), so each user query loads only the relevant slice ([R2](#references))
- **SHOULD** keep skill scope to a **single coherent unit of work** (function-level coherence): a skill that "queries the database and formats the results" is one unit; a skill that "queries the database, formats the results, and administers the database" is two units that should be split ([R4](#references))

### Runtime & lifecycle awareness (Claude Code)

Skills shipped by this plugin run inside Claude Code; understanding the runtime contract avoids authoring mistakes that surface only at session-time.

- **MUST** write the body so its content holds up as **standing instructions for the rest of the session**, not as one-time steps: once a skill is invoked, its rendered `SKILL.md` content enters the conversation as a single message and stays there for the rest of the session—Claude Code **never** re-reads the file on later turns ([R3](#references))
- **MUST** survive automatic compaction: after the conversation is compacted, Claude Code re-attaches the most recent invocation of each skill keeping only the **first 5,000 tokens** of each, with a combined re-attached budget of **25,000 tokens** across all invoked skills; SKILL.md content beyond the 5,000-token mark is silently dropped ([R3](#references)). The 5,000-token authoring cap and the 5,000-token re-attach window aren't coincidental—the skill is designed to survive compaction whole only if it stays under that limit
- **MAY** declare any of the optional Claude Code-specific frontmatter fields ([R3](#references)) when they apply: `when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `model`, `effort`, `context: fork`, `agent`, `hooks`, `paths`, `shell`. These extend the formal Agent Skills spec ([R1](#references)) but aren't portable to non-Claude-Code runtimes
- **MUST** treat `allowed-tools` as a **permission grant** (pre-approved tool calls when the skill is active), not as a tool restriction; it doesn't narrow what the skill can call—it widens what runs without prompting the user. Project-level skills with `allowed-tools` only take effect after the user accepts workspace trust ([R3](#references))
- **MUST**, when setting `disable-model-invocation: true` for a skill that should only run on explicit user request, accept the consequence that the skill can't be **preloaded into subagents** via a subagent's `skills:` field—Claude Code skips disabled skills there and logs a warning ([R3](#references))
- **MAY** declare a `model` override on a skill (`model: opus`, `model: haiku`, `model: inherit`); the override applies for the rest of the current turn and **isn't saved to settings**, so the session model resumes on the next prompt ([R3](#references))
- **MAY** use `context: fork` together with `agent: <type>` to run the skill in a forked subagent context (skill content becomes the prompt, the named agent type provides tools and model). This is the **inverse** of a subagent's `skills:` preload field; both arrive at the same composition through different ownership ([R3](#references)). When to choose it over an `agents/<name>.md` file is governed by `skill-vs-agent`

### Evaluation discipline

- **SHOULD** **build evaluations before extensive documentation**: identify gaps by running Claude on representative tasks without the skill, document the specific failures, then write only the instructions that close those gaps ([R2](#references))
- **SHOULD** ship at least **three evaluation scenarios** per non-trivial skill (input prompt, optional input files, expected behavior) under `examples/` or a sibling location, so iteration is grounded in observable behavior rather than authoring intuition ([R2](#references))
- **SHOULD** **test the skill against every model the skill is intended to be used with**, namely Haiku, Sonnet, and Opus; what works for Opus may not provide enough guidance for Haiku, and what's clear for Haiku may over-explain for Opus ([R2](#references))
- **MAY** validate skill structure with the upstream `skills-ref` reference validator (`skills-ref validate ./skills/<name>`) before opening a PR; the validator catches frontmatter and naming issues this spec doesn't enumerate exhaustively ([R1](#references))

## Acceptance Criteria
- [ ] Source folder exists at `skills/<name>/` in `claude-shared` with `<name>` in ASCII kebab-case
- [ ] Repository contains a valid `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` that expose this skill as part of the `nolte-shared` plugin
- [ ] Skill is discoverable in a consuming project solely by installing the `nolte-shared` plugin from the marketplace—no manual copy or symlink into `.claude/skills/` is needed or permitted
- [ ] Plugin version in `.claude-plugin/plugin.json` equals the latest published GitHub Release tag (maintained per `release-automation` §Version-bearing file alignment, not by skill-change PRs); no diff to the `version` field appears in any PR whose sole purpose is adding, renaming, or removing a skill
- [ ] `SKILL.md` parses with valid YAML frontmatter containing `name` and `description`
- [ ] `name` in frontmatter equals the folder name
- [ ] `description` mentions the concrete user phrasings that should trigger the skill
- [ ] If `tags` is declared in frontmatter, every entry is a lowercase ASCII kebab-case string ≤30 characters and the list contains at most 5 entries
- [ ] Frontmatter declares a `phase` field whose value is one of `vision`, `plan`, `design`, `build`, `review`, `quality`, `close-release`, or `cross-cutting`
- [ ] Skill works when invoked in a downstream project that doesn't contain `claude-shared`-specific context, loaded through the plugin
- [ ] No hard-coded absolute paths; all internal paths are relative to the skill folder or the project the skill operates on
- [ ] If the skill writes files, the target locations and preconditions are documented
- [ ] Reviewing an individual skill against this spec follows `spec/claude/skill-review/`; review output conforms to `spec/claude/review-plan/` and lives under `.audits/skill-review/<name>.md`
- [ ] Every skill's `SKILL.md` is under 500 lines and 5,000 tokens, and every referenced asset under `references/` / `templates/` / `assets/` / `scripts/` is paired with an explicit load-trigger phrase in `SKILL.md`
- [ ] `name` is 1–64 characters, lowercase ASCII letters/digits/hyphens, doesn't start or end with `-`, contains no `--`, and contains no occurrence of the reserved tokens `anthropic` or `claude`
- [ ] `description` is non-empty, ≤1024 characters, written in third person, and names both *what* the skill does and *when* to use it
- [ ] Combined `description` + `when_to_use` text is under 1,536 characters
- [ ] No file reference inside `SKILL.md` chains through another file (every reference is at most one hop from `SKILL.md`)
- [ ] Every reference file longer than 100 lines opens with a table of contents
- [ ] Every script reference makes execution intent explicit ("Run X to …" vs. "See X for the algorithm of …")
- [ ] All paths in `SKILL.md` and supporting files use forward slashes
- [ ] No skill in `skills/` references an MCP tool without the `ServerName:tool_name` qualifier
- [ ] No `SKILL.md` declares a `name` containing the reserved tokens `anthropic` or `claude`; other frontmatter fields (`description`, `tags`, `when_to_use`, etc.) MAY mention these terms

## References

- [R1] Agent Skills, formal specification: <https://agentskills.io/specification>
- [R2] Skill authoring best practices, Anthropic platform docs: <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices>
- [R3] Extend Claude with skills, Claude Code docs: <https://code.claude.com/docs/en/skills>
- [R4] Best practices for skill creators, agentskills.io: <https://agentskills.io/skill-creation/best-practices>
- [R5] Equipping agents for the real world with Agent Skills, Anthropic engineering, 2025-10-16: <https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills>
- [R6] anthropics/skills (canonical Anthropic skill repository): <https://github.com/anthropics/skills>

## Open Questions
- Should the folder name be required to match any user-facing slash-command name, or may they differ?
- Do skills need version or compatibility metadata as they evolve?
- Where's the boundary between a skill and an agent? When should a capability be one versus the other?
- Is there a maximum nesting depth for supporting subfolders, or does that stay loose?
