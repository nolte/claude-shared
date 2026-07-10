# Claude Agent Authoring

Status: draft

## Context
The `claude-shared` repository collects reusable Claude Code skills and agents that downstream projects consume. An agent has two lives: a **source** form in this repository (under `agents/`), and a **runtime** form in a consuming project (under `.claude/agents/` or `~/.claude/agents/`) where Claude Code actually loads it and the `Agent` tool dispatches to it via `subagent_type`. Without a consistent shape, agents drift in naming, trigger descriptions, tool scoping, and system-prompt quality, which makes reuse fragile and routing unreliable. This spec defines how new agents are authored, where they live in both forms, and what existing agents must conform to.

For a consolidated cross-artifact reference of every skill- and agent-frontmatter field, its provenance (portable Claude Code standard versus nolte-local invention), and its normative owner, see `spec/claude/skill-agent-frontmatter/`. That reference maps and points back to this spec; it doesn't restate the rules here.

## Goals
- Every agent has the same predictable shape on disk
- Agents are routable by Claude through precise, trigger-oriented descriptions
- Agents have the minimum necessary tool access to do their job
- Agents are portable across any project that consumes `claude-shared`, with no hidden dependencies
- Authors have a clear checklist and template to start from

## Non-Goals
- Plugin packaging and distribution (covered separately)
- Plugin-level scoping—when a capability belongs in this plugin versus a separate one, and how the plugin stays scannable as its agent count grows (covered by `plugin-scoping`)
- Downstream project setup and `.claude/` configuration
- Prescribing specific agent behavior beyond structural rules
- The orchestration logic inside the calling Claude (which agent to pick when)

## Requirements

### Structure
- **MUST** be authored as a single markdown file named `<name>.md` where `<name>` is ASCII kebab-case
- **MUST** include YAML frontmatter with the fields `name`, `description`, and `distribution`
- **MUST** set `name` to match the filename without the `.md` suffix
  - **`nolte-shared` plugin choice**: this repository names every agent in **object-role form**—`<subject>-<role-noun>`, where the trailing token is the role the agent plays over the leading subject (`code-security-reviewer`, `feature-consistency-reviewer`, `portfolio-manifest-collector`, `vocab-drift-scanner`, `lektorat-scanner`). This is the agent-side counterpart to skill-management's verb-noun convention for skills; the choice is recorded here so a reviewer doesn't flag it on every iteration. New agents in this plugin **MUST** follow the object-role convention, keeping the naming pattern consistent across the whole agent surface (mixing in a verb-noun or gerund agent name would itself be the discoverability anti-pattern `plugin-scoping` §Namespace and naming coherence warns against). A future coordinated portfolio rename (with a deprecation period) **MAY** flip the choice; until that ships, object-role is the rule
    - **Role-noun morphology and documented exceptions**: the trailing role-noun almost always carries `-er`/`-or`/`-ist` morphology (`-reviewer`, `-checker`, `-scanner`, `-collector`, `-curator`, `-enforcer`, `-extractor`, `-generator`, `-author`, `-developer`); an actor noun that names a role without that morphology is still conformant—`webview-ui-expert` (`expert`) is the standing case, carried in `AGENT_ROLE_NOUNS` in `scripts/validate_skills.py`. Two established agent names don't fit `<subject>-<role-noun>` at all and are deliberately left as-is: `png-to-transparent-svg` (a transformation phrase with no role token) and `audience-review` (whose trailing `review` names an action, not an actor—its object-role sibling would be `audience-reviewer`). Renaming either would break every `subagent_type:` call site; the breakage cost outweighs the coherence gain. A reviewer **MUST NOT** flag these two names as object-role violations. The exception is closed: it covers exactly `png-to-transparent-svg` and `audience-review`, mirrored as `AGENT_NAME_FORM_EXCEPTIONS` in `scripts/validate_skills.py` (which flags any other non-role-noun agent name as a `Suggestion`), and every *new* agent **MUST** still follow the object-role convention
- **MUST NOT** use the reserved words `anthropic` or `claude` as the value of `name` or anywhere within `name`, per the upstream platform validator. The same narrow-exception clause from `skill-management` §Frontmatter validation applies: an agent whose primary responsibility is authoring or maintaining a Claude Code or Anthropic platform surface (for example a `claude-plugin-developer` agent) **MAY** waive the ban when the agent body carries a `## Reserved-token rationale` section that names the platform surface
- **MUST** write a `description` that names concrete user-facing triggers and task shapes ("use when the user asks X," "invoke for Y") rather than abstract capabilities, so the calling Claude can reliably decide when to dispatch
- **MUST** set `distribution` to exactly one of `plugin` or `project`, declaring the intended delivery form (see "Distribution" below); the author chooses this consciously at creation time and changes it only by re-authoring the agent for the new form
- **MUST** contain a system prompt in the markdown body that scopes the agent to a single responsibility and states its expected output shape
- **MUST** keep frontmatter field names and technical identifier values in English: `name`, `distribution`, `tools` entries, `model`, and `tags` entries stay English regardless of the project's documentation language
- **SHOULD** keep the `description` value and the system-prompt body in English for token efficiency and portability across teams; agents authored with `distribution: project` for a project that declares a non-English documentation language in its root-level convention file (typically `CLAUDE.md`) **MAY** instead author the `description` and the body in the project's primary documentation language. Agents authored with `distribution: plugin` **MUST** stay English-only in description and body because they ship across multiple downstream projects with possibly different languages
- The agent **MAY** still be instructed to respond to the user in the user's language regardless of where the body is authored
- **MUST** be self-contained: an agent is exactly one top-level markdown file `agents/<name>.md`. Inline any supporting material (references, examples, prompt fragments, output-shape templates) directly into the agent body. **MUST NOT** place a companion markdown file in a sibling folder `agents/<name>/`, because Claude Code's default agent discovery scans `agents/` **recursively**: every nested `.md` is registered as a phantom, scope-prefixed agent (`<name>:<file>`) and, lacking frontmatter, inherits the full tool surface with no `tools` restriction. When a supporting asset is genuinely too large to inline, place it **outside** the recursively-scanned `agents/` tree (for example under a top-level `agent-assets/<name>/`) and reference it by relative path
- **MAY** include an optional `tags` field in YAML frontmatter: a list of lowercase ASCII kebab-case strings, each ≤30 characters, with no more than 5 entries; tags provide thematic grouping so the catalog (`skill-agent-catalog`) and peer-cluster lookups (`skill-vs-agent` §Portfolio-wide consistency) can browse by topic
- **MUST NOT** declare a `tags` entry that begins with `_` (underscore); the underscore prefix is reserved for catalog-generator-emitted auto-tags such as `_translation-pending`
- **MUST** include a `phase` field in YAML frontmatter whose value is exactly one identifier from the eight-value vocabulary declared in `skill-agent-catalog` §Phase classification (`vision`, `plan`, `design`, `build`, `review`, `quality`, `close-release`, `cross-cutting`); the catalog generator fails the docs build when `phase` is missing or out of vocabulary
- **MAY** include an optional `summary` field plus a `summary_<lang>` field per additional docs language; both are short (≤200 character) plain strings the catalog renders as a scannable subtitle above the routing `description`. Resolution and fallback rules live in `skill-agent-catalog` §Per-language short summary
- **MAY** include any of the optional use-case fields `use_when`, `dont_use_when`, `see_also`, or `examples`; the detailed schema and validation rules live in `skill-agent-catalog` §Use-case metadata. Authors **SHOULD** declare them whenever overlap with other artefacts is likely, so the catalog stays scannable and the cross-linking pass can connect related artefacts

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

### Distribution
An agent is authored for exactly one of two delivery forms. The choice is made up front and written into the `distribution` field:

- `plugin`: shipped as part of a Claude Code plugin. The agent is expected to be installed and updated through the plugin mechanism, alongside other agents/skills of the same plugin, and may assume the plugin's conventions and co-located resources.
- `project`: direct reuse in a single project or user environment. The agent is copied or symlinked into the consuming setup and stands alone, without assuming any plugin context.

Every agent declares this intent so authors, reviewers, and consumers all see from the file itself whether it belongs to a plugin bundle or is meant for standalone project use.

Agents carry no per-file version metadata; versioning is handled at the plugin level (`.claude-plugin/plugin.json`) and via git history. A per-agent `version` frontmatter field is deferred until the distribution mechanism supports independent per-agent pinning (see `plugin-scoping`).

### Tool access
- **MUST** declare a `tools` field in frontmatter when the agent should be restricted; omit the field only when the agent genuinely needs the full tool surface, because **omitting `tools` implicitly grants every tool inherited from the caller**, which is a permission-sprawl trap, not a safe default ([R1](#references), [R3](#references))
- **MUST** scope `tools` to the minimum set needed for the agent's responsibility (principle of least authority); read-only agents MUST NOT receive write, edit, or execution tools
  - **Narrow exception** for read-only audit / review agents whose audit surface genuinely requires a side-effect-free shell capability that no dedicated tool covers (typically `git log`, `git rev-parse`, `git ls-files`, `gh api ... --jq` against read-only endpoints): `Bash` **MAY** appear in `tools` when the agent body carries a `## Read-only Bash justification` section that names the exact subset of read-only commands the agent invokes and explicitly forbids anything else (writes, network mutations, package installs, file edits). The agent still **MUST NOT** declare `Edit`, `Write`, or `NotebookEdit`; those tools are unconditionally banned for read-only agents. The `agent-review` checks honour the exception when the body section is present and downgrade the otherwise-`Critical` finding to `Info`; without the section, `Bash` on a read-only agent stays a `Critical`
  - **Write-capable agents that also need `Bash`**: an agent that legitimately holds `Edit`/`Write` (a drafting or repair agent) and additionally runs shell commands (typically `task lint`, a build, or a test run) documents that shell usage under a neutral `## Bash justification` section, **not** `## Read-only Bash justification`, whose side-effect-free promise doesn't apply to a write-capable agent and would be a false claim. The section names the commands the agent invokes and their effects. Note that `task lint` (and `pre-commit run`) isn't side-effect-free: it runs automatic fixers (trailing-whitespace, end-of-file, formatters) that mutate tracked files, so an agent invoking it MUST NOT describe it as side-effect-free.
  - **Network-read surface (`WebSearch` / `WebFetch`)**: a read-only agent MAY hold `WebSearch` or `WebFetch` when its audit surface genuinely requires reading external sources (for example resolving an SPDX identifier or checking upstream release notes). Because these tools send the query to a remote service and fetch remote content (a data-flow effect the side-effect-free framing for `Bash` doesn't cover), such an agent **SHOULD** carry a `## Network-read justification` section that names why the network read is needed and forbids using it to mutate remote state. This keeps the least-authority audit trail symmetric with the `Bash` exception.
  - **Reviewer review-and-repair classification**: an agent whose single responsibility is a review that *includes* applying the fix it found (a review-and-repair or lint-and-fix agent) is legitimately write-capable rather than read-only; the read-only tool bans above don't apply to it. Read-only status is inferred from the responsibility verbs (review, audit, research, lint, report) in `description` / system prompt, and that verb heuristic must not be applied so literally that a genuine repair agent is misclassified as read-only holding write tools. When the classification is genuinely ambiguous, state the intended mode (read-only or review-and-repair) explicitly in the system prompt.
- **SHOULD** prefer dedicated tools (`Read`, `Grep`, `Glob`, `Edit`) over `Bash` equivalents when both would work
- **MAY** instead declare `disallowedTools` (denylist, subtractive against the inherited set) when the agent should keep most tools but lose a small specific subset—if both `tools` and `disallowedTools` are set, the runtime applies `disallowedTools` first, then resolves `tools` against the remaining pool, so a tool listed in both is removed ([R1](#references))
- **MUST NOT** list `Agent` in the `tools` field—Claude Code subagents can't spawn other subagents, so the tool would be inert, and declaring it misleads readers into believing nested fan-out is possible. The one supported nested pattern remains *skill orchestrates, agent executes* ([R1](#references), and `skill-vs-agent` §Hybrid pattern)

### Model selection
- **MAY** declare a `model` field in frontmatter; allowed values per Claude Code are a model alias (`sonnet`, `opus`, `haiku`), a full model ID (for example `claude-opus-4-7`, `claude-sonnet-4-6`), or the literal `inherit` ([R1](#references))
- **The default is `inherit`**, not a specific model—if the field is omitted the agent runs on the caller's model. This matters for cost auditing: a "no `model` field" agent still inherits whatever the caller pays for; only an explicit alias pins the cost contract
- **SHOULD** justify a pinned `model` in the system prompt or a comment so future readers understand why it was fixed
- **MAY** rely on the runtime resolution order (`CLAUDE_CODE_SUBAGENT_MODEL` env var → per-invocation `model` parameter → frontmatter `model` → caller's model) when an operator wants to override per-session ([R1](#references))

### Optional Claude Code frontmatter fields

Beyond `name`, `description`, `tools`, and `model`, Claude Code recognizes additional fields. Authors **MAY** use these when they apply; reviewers **MUST** treat unfamiliar fields not in this list as authoring smells worth flagging.

- `disallowedTools`: denylist of tools to subtract from the inherited or specified set ([R1](#references))
- `permissionMode`: one of `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan`. **Ignored for plugin-distributed agents**, see "Plugin-distribution security constraints" below ([R1](#references))
- `maxTurns`: caps how many agentic turns the subagent runs before stopping ([R1](#references))
- `skills`: list of skill names to **preload into the subagent's context at startup**; the full skill content is injected, not just the description, so the subagent has the rules in scope without discovery cost. Skills with `disable-model-invocation: true` can't be preloaded; Claude Code skips them and logs a warning ([R1](#references))
- `mcpServers`: MCP servers available to this subagent only; supports inline definitions and string references to already-configured servers. **Ignored for plugin-distributed agents** ([R1](#references))
- `hooks`: lifecycle hooks scoped to this subagent. **Ignored for plugin-distributed agents** ([R1](#references))
- `memory`: `user`, `project`, or `local`; gives the subagent a persistent directory across sessions. When set, Read/Write/Edit are automatically enabled and the system prompt is augmented with memory-curation instructions ([R1](#references))
- `background`: `true` to always run as a background task; the runtime pre-approves needed permissions before launch and automatically denies anything not pre-approved ([R1](#references))
- `effort`: `low` / `medium` / `high` / `xhigh` / `max`; overrides the session effort for this subagent ([R1](#references))
- `isolation: worktree`: runs the subagent in a temporary git worktree so its file edits don't touch the main checkout; the worktree is cleaned up if the subagent makes no changes ([R1](#references))
- `color`: display color in the task list (`red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan`) ([R1](#references))
- `initialPrompt`: prepended as the first user turn when this agent runs as the main session via `--agent` ([R1](#references))

### Plugin-distribution security constraints

For security reasons, Claude Code **silently ignores** the `hooks`, `mcpServers`, and `permissionMode` frontmatter fields when an agent is loaded from a plugin (that is, authored with `distribution: plugin` here) ([R1](#references)). Authoring the fields anyway misleads future readers and creates audit drift, so this spec hardens the constraint:

- **MUST NOT**, when `distribution: plugin` is declared, set `hooks`, `mcpServers`, or `permissionMode` in the frontmatter—the runtime ignores them and a future reader has no signal to distinguish "intentionally absent" from "silently dropped"
- **MAY**, when `distribution: project` is declared, use any of those fields freely; the constraint is exclusively on plugin-distributed agents
- **SHOULD**, when an agent genuinely needs `hooks`, `mcpServers`, or `permissionMode`, either author it as `distribution: project` from the start or explicitly note in the body that the plugin form sacrifices those features and document the workaround for plugin consumers (for example asking the consumer to copy the agent file into `.claude/agents/` to regain the fields)

### Subagent boundaries (Claude Code runtime)

- **MUST NOT** assume an agent can spawn a further subagent—Claude Code subagents **can't spawn other subagents** ([R1](#references)). The single supported nested-orchestration pattern remains *skill orchestrates, agent executes* (governed by `skill-vs-agent`); the skill stays in the main thread and can dispatch agents in sequence or in parallel
- **MUST NOT** invoke the Skill tool from inside an agent body to delegate skill-shaped work back to the parent—the agent runs in an isolated context window and has no stable channel for skill-level interactivity ([R3](#references), and `skill-vs-agent` §Hybrid pattern)
- **MAY**, when the agent is intended to be picked up by Claude **proactively** (without the user naming it explicitly), include the phrase **"use proactively"** in the `description` field; the runtime treats this phrase as an opt-in signal for proactive delegation ([R1](#references)). Conversely, if the agent should only run when the user explicitly names it, **MUST NOT** include "use proactively" in `description`
- **SHOULD** apply **single-responsibility design** to every agent: one clear goal, one input shape, one output shape, one handoff rule. Agents that conflate multiple responsibilities (review + fix, audit + remediate) regress quickly because the dispatching Claude can't reliably match the description to a request ([R6](#references))
- **SHOULD** keep the plugin's agent surface lean and each agent's `description` sharply scoped: Claude's automatic delegation degrades as the number of similar or overlapping agents grows, so an oversupply of agents harms routing even when each one is individually well-formed ([R1](#references)). When routing is ambiguous, prefer explicit invocation over relying on automatic delegation, and resolve overlap per `skill-vs-agent` §Duplicate prevention and the plugin-boundary rules in `plugin-scoping`

### Source location (`claude-shared` repository)
- **MUST** live at `agents/<name>.md` in the `claude-shared` source tree, so it can be copied, symlinked, or bundled into a plugin for distribution
- **MUST NOT** introduce a sibling folder `agents/<name>/` for supporting markdown; recursive agent discovery would register it as a phantom agent (see §Structure). Supporting assets too large to inline live outside the `agents/` tree (for example `agent-assets/<name>/`) and are referenced by relative path

### Runtime location (consuming project)
Runtime location follows the declared `distribution`:

- If `distribution: plugin`, the agent **MUST** be loadable from the plugin's designated agents path once the plugin is installed in a consuming project. It **MUST NOT** require any manual drop into `.claude/agents/` or `~/.claude/agents/` to work.
- If `distribution: project`, the agent **MUST** be loadable by Claude Code from one of:
  - `.claude/agents/<name>.md`: project-level installation
  - `~/.claude/agents/<name>.md`: user-level installation

In both cases the agent **MUST NOT** assume a particular absolute install location; all internal references stay relative to the agent file or to the project the agent operates on.

### Recommendations
- **SHOULD** begin the system prompt with the agent's role and boundaries up front, and state the expected output format either before the working procedure **or** as an explicit terminal "Report" / output-contract phase that closes the working procedure. The house template across this plugin's agents places the output contract as that closing phase (a "Report" or "Output" step after the analysis phases); this is a deliberate, conformant house convention, not an ordering deviation, because the reader still meets the role and boundaries first and the output shape is unambiguously declared. What's **not** conformant is leaving the output shape implicit or scattering it through the procedure
- **SHOULD** state explicitly in the system prompt whether the agent writes code or only researches, since the calling Claude is responsible for that distinction at dispatch time
- Each agent declares its own output contract in the system prompt (already required by §Structure); there is no single repo-wide report schema. Review, audit, and research agents **SHOULD** return a structured report (for example severity-classified findings or a coverage map) and **SHOULD** close with an explicit caller follow-ups / handoff section; free-form summaries are acceptable only for trivial single-fact responses
- **SHOULD** keep the system prompt focused; if it grows past roughly 200 lines, tighten the prose rather than splitting it out—an agent stays a single file (see §Structure), so long-form material stays inline or, only when genuinely too large, moves outside the `agents/` tree (for example `agent-assets/<name>/`). The ~200-line figure is a local `nolte-shared` convention; Anthropic documents no agent-file size budget, in contrast to the soft ~500-line `SKILL.md` guideline that `skill-management` codifies for skills
- **SHOULD** include in `description` both positive triggers ("use when…") and common negative cases ("don't use for…") when overlap with other agents is likely
- **MAY** include example invocations and expected reports inline in the agent body; when they're too large to inline, place them outside the `agents/` tree (for example `agent-assets/<name>/examples/`) and reference them by relative path—never in a sibling `agents/<name>/` folder, which recursive discovery would register as a phantom agent

### Resumable runs
- **MUST** declare `resumable: true` in the agent's frontmatter when the agent internally spans more than one named phase that produces an intermediate artefact the operator would otherwise lose on interruption, and follow `spec/claude/resumable-work/` for the on-disk envelope, checkpoint cadence, re-invocation prompt, and lifecycle; the load-bearing rules live in that spec and aren't duplicated here
- **MUST** mention resume support in the agent's `description` text whenever `resumable: true` is set, so the calling Claude can route accordingly
<!-- vale Microsoft.Contractions = NO -->
- **SHOULD NOT** declare `resumable: true` for fire-and-forget agents whose contract is a single read-only pass cheap to restart
<!-- vale Microsoft.Contractions = YES -->

## Acceptance Criteria
- [ ] Source file exists at `agents/<name>.md` in `claude-shared` with `<name>` in ASCII kebab-case
- [ ] No supporting markdown file exists in a sibling folder `agents/<name>/`; recursive agent discovery would register it as a phantom, all-tools agent. Supporting assets too large to inline live outside the `agents/` tree (verifiable with `find agents -mindepth 2 -name '*.md'` returning no results)
- [ ] Frontmatter parses as valid YAML and contains at minimum `name`, `description`, and `distribution`
- [ ] `name` in frontmatter equals the filename without `.md`
- [ ] `description` names concrete triggers the calling Claude can match against user requests
- [ ] If `tags` is declared in frontmatter, every entry is a lowercase ASCII kebab-case string ≤30 characters and the list contains at most 5 entries
- [ ] No `tags` entry begins with `_` (underscore-prefixed tags are reserved for catalog-generator auto-tagging)
- [ ] Frontmatter declares a `phase` field whose value is one of `vision`, `plan`, `design`, `build`, `review`, `quality`, `close-release`, or `cross-cutting`
- [ ] If `summary` or any `summary_<lang>` is declared, the value is a non-empty plain string ≤200 characters
- [ ] If `use_when`, `dont_use_when`, `see_also`, or `examples` is declared, the value conforms to the schema in `skill-agent-catalog` §Use-case metadata
- [ ] `distribution` is exactly `plugin` or `project`: no other value, no missing field
- [ ] If `distribution: plugin`, the agent is dispatchable via `subagent_type: <name>` in a project where the containing plugin is installed, without manually copying the file
- [ ] If `distribution: project`, the agent is dispatchable via `subagent_type: <name>` after being deployed to `.claude/agents/<name>.md` or `~/.claude/agents/<name>.md`, with no plugin required
- [ ] If `tools` is set, the listed tools are sufficient for the agent's stated responsibility and contain no unused entries
- [ ] Read-only agents have no write/edit/execution tools in their `tools` list
- [ ] Agent works when invoked in a downstream project that doesn't contain `claude-shared`-specific context
- [ ] No hard-coded absolute paths; all internal references are relative to the agent file or the project it operates on
- [ ] If the agent writes files or performs side effects, the targets and preconditions are documented in the system prompt
- [ ] Frontmatter field names and technical identifier values (`name`, `distribution`, `tools`, `model`, `tags`) are English; `description` and the system-prompt body are English by default, unless the agent declares `distribution: project` and the consuming project's root-level convention file (typically `CLAUDE.md`) declares a non-English documentation language and authorizes that language for agent prose
- [ ] Reviewing an individual agent against this spec follows `spec/claude/agent-review/`; review output conforms to `spec/claude/review-plan/` and lives under `.audits/agent-review/<name>.md`
- [ ] No agent declared `distribution: plugin` sets any of the fields `hooks`, `mcpServers`, `permissionMode` in frontmatter (those fields are silently dropped by the runtime for plugin-distributed agents)
- [ ] No agent body invokes another subagent via the Agent tool or any equivalent dispatch phrasing (subagents can't spawn subagents in Claude Code)
- [ ] No agent lists `Agent` in its `tools` field (subagents can't spawn subagents, so the entry would be inert)
- [ ] Every agent whose `description` contains the phrase "use proactively" actually warrants proactive delegation; agents that should only run on explicit user request **MUST NOT** include the phrase
- [ ] Every agent that pins `model` to a value other than `inherit` either justifies the pin in the system prompt or carries a comment explaining the cost/quality trade-off
- [ ] Every agent's responsibility is single—one goal, one input shape, one output shape; an agent whose `description` reads as "X and Y" or "X plus Z" is split or has a documented reason for the conflation
- [ ] If `tools` and `disallowedTools` are both declared, no tool appears in both lists, and the resolved set (deny-then-allow) is non-empty

## References

- [R1] Create custom subagents, Claude Code docs: <https://code.claude.com/docs/en/sub-agents>
- [R2] Agent Skills, formal specification (for cross-format alignment): <https://agentskills.io/specification>
- [R3] Skill vs. agent decision (this plugin): `spec/claude/skill-vs-agent/`
- [R4] Building Effective AI Agents, Anthropic engineering: <https://www.anthropic.com/research/building-effective-agents>
- [R5] Equipping agents for the real world with Agent Skills, Anthropic engineering, 2025-10-16: <https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills>
- [R6] Best practices for Claude Code subagents, PubNub Engineering: <https://www.pubnub.com/blog/best-practices-for-claude-code-sub-agents/>

## Open Questions
_None at this time._
