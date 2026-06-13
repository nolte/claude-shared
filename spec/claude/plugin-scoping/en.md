# Claude Plugin Scoping

Status: draft

## Context
Claude Code packages reusable capabilities—skills, agents, slash commands, hooks, MCP/LSP servers—as **plugins**. This repository ships exactly one such plugin, `nolte-shared`, which today bundles 40+ skills and 25+ agents spanning every delivery-lifecycle phase. Three existing specs each answer a different scoping question: `skill-vs-agent` decides the artifact **type** (skill or agent), `skill-management` and `agent-management` decide each artifact's on-disk **shape**, and `skill-agent-catalog` decides the **discovery** surface. None of them answers the question that sits above all three: **what bounds a plugin itself?** When does a set of capabilities belong in *one* plugin versus split across *several*, and how does a single plugin stay scannable ("übersichtlich") and purpose-fit as it grows?

Without a rule, authors drift toward one of two failure modes: a "kitchen-sink" plugin nobody can navigate, or premature fragmentation that scatters a single user workflow across many installs. A research pass against the authoritative Anthropic sources ([R1](#references) through [R4](#references)) found that Anthropic decides plugin boundaries **purely by distribution and reuse**, documents **no** upper limit on capabilities per plugin, and gives **no** thematic-cohesion rule for what belongs in one plugin versus many. The popular intuition that Anthropic's own first-party plugins are each scoped to a single workflow or domain was investigated and **not supported**. This spec therefore codifies the distribution-keyed rule as the authoritative core, and marks every breadth- or split-related rule beyond it explicitly as a local `nolte-shared` convention rather than Anthropic guidance.

Readers: plugin authors deciding where a new capability lives, reviewers checking whether a proposed plugin split is justified, and portfolio maintainers weighing whether `nolte-shared` should ever become more than one plugin.

## Goals
- A deterministic rule for **plugin membership**: which capabilities ship inside one plugin versus a separate one
- A clear separation between what Anthropic actually documents (the distribution-keyed boundary) and what's a local `nolte-shared` convention (everything about breadth, splits, and scannability)
- Keep a deliberately broad plugin scannable and purpose-fit through *intra*-plugin organization, not through splitting for breadth's sake
- Name the real anti-patterns: capability overlap that degrades routing, and topic-driven fragmentation that splinters one workflow across multiple plugins
- Give reviewers a checkable basis for accepting or rejecting a proposed second plugin in the portfolio

## Non-Goals
- The artifact-type choice between a skill and an agent (owned by `skill-vs-agent`)
- The on-disk shape, frontmatter, and naming of individual skills or agents (owned by `skill-management` and `agent-management`)
- The MkDocs catalog, phase classification, and tag vocabulary that render a plugin browsable (owned by `skill-agent-catalog`)
- Marketplace mechanics and the plugin-version bump (owned by `release-automation` and the manifest specs)
- Runtime loading, namespace resolution, and routing behavior of Claude Code itself
- Whether a given capability should be a plugin artifact at all versus a project-local `.claude/` artifact (a distribution decision owned by `skill-management` / `agent-management`)

## Requirements

### The plugin boundary is the distribution unit, not the theme
- **MUST** decide plugin membership by the **distribution contract**, not by topic or count: a capability belongs in a plugin when it shares that plugin's release cadence, marketplace entry, version line, and the consumer's single install decision. This is the only plugin-boundary criterion Anthropic documents—the "When to use plugins vs standalone configuration" guidance keys entirely on sharing with a team, reusing across projects, versioned updates, and marketplace distribution ([R1](#references))
- **MUST NOT** treat thematic breadth or capability count as a reason to split a plugin: Anthropic documents no upper limit on capabilities per plugin and no thematic-cohesion rule for what belongs in one plugin versus many ([R1](#references)). A broad, multi-theme plugin like `nolte-shared` is conformant **by design** as long as its members share one distribution contract
- **MUST NOT** cite "Anthropic scopes its plugins by theme/domain/workflow" as a justification for any rule in this portfolio—the claim that Anthropic's first-party plugins are each single-workflow-scoped was investigated against the source and not supported, so it's not a basis for local rules
- A plugin **MAY** bundle heterogeneous component types (skills, agents, commands, hooks, MCP/LSP servers, settings) under one `.claude-plugin/plugin.json`; the manifest, not any single component type, is the scoping boundary ([R1](#references))

### When to split into a separate plugin
This section is a **local `nolte-shared` convention** derived from the distribution-keyed rule above; Anthropic gives no first-party split criterion.

- **MUST** split a subset of capabilities into its own plugin only when that subset has a genuinely different **distribution contract**, for example:
  - a different consumer audience (some consumers want subset A but never B)
  - a different release cadence or stability guarantee (experimental capabilities versus the stable surface)
  - a different runtime or dependency requirement that not all consumers can satisfy
  - a different ownership, licensing, or access boundary
- **MUST NOT** split a plugin merely because its members address different topics or lifecycle phases; a topic-only split fragments a single end-to-end user workflow across multiple installs and forces a consumer to discover, install, and version-track N plugins to obtain one coherent flow
- **MUST** name the concrete distribution-contract difference in the splitting PR's description; a split whose rationale reduces to "these are different topics" or "the plugin is getting large" doesn't satisfy this spec
- **SHOULD** prefer one plugin per distribution contract even when that plugin spans many lifecycle phases; the catalog's `phase` classification ([R5](#references)), not the plugin boundary, is the axis that organizes a plugin by lifecycle
- **SHOULD** record each plugin's single distribution contract in its `project/portfolio.yml` capability rationale (per `portfolio-management`), so the rendered portfolio inventory surfaces every plugin's distribution contract and makes split decisions portfolio-auditable rather than visible only per-PR; the `skill-agent-catalog` consumer mode catalogs artifacts for discovery and **isn't** where distribution contracts are recorded

### Scannability is an intra-plugin concern
This section is a **local `nolte-shared` convention**.

- **MUST** keep a growing plugin scannable through the *intra*-plugin organization layers rather than through splitting: `phase` classification, `tags`, per-section index pages, and task-oriented landing pages (all owned by `skill-agent-catalog` [R5](#references)), plus the naming discipline owned by `skill-management` and `agent-management`
- **MUST** treat the duplicate-prevention invariant (one capability per artifact, per `skill-vs-agent` §Duplicate prevention) as the primary defense of a plugin's clarity: capability **overlap**, not capability **count**, is what erodes navigability
- **SHOULD** treat the catalog's task-oriented landing pages as the human entry point that keeps a broad plugin navigable by user intent ("I want to publish a release") rather than by browsing dozens of artifacts
- **SHOULD**, when a reviewer perceives the plugin as hard to navigate, first look for missing or weak `phase`/`tags`/landing-page coverage and for duplicate-capability drift, before entertaining a plugin split

### Discoverability is the real scaling pressure
- **MUST** recognize that the binding scaling limit of a growing plugin is **routing and discovery**, not the plugin manifest: at startup Claude preloads only each artifact's `name` plus `description` metadata to route across potentially 100+ skills, so an oversupply of overlapping or vaguely described artifacts degrades automatic selection and delegation ([R2](#references), [R3](#references))
- **MUST** therefore operationalize "scoping discipline" as **description-quality and overlap-elimination discipline** (governed by `skill-management`, `agent-management`, and `skill-vs-agent`), never as a target number of plugins or artifacts
- **SHOULD**, when routing reliability visibly degrades as the plugin grows, first sharpen the `description` fields (third-person, what + when) and remove capability overlap; consider a distribution-contract split only if one genuinely exists
- **SHOULD** prefer explicit invocation over relying on automatic delegation for agents whose routing is ambiguous, because automatic delegation degrades as the number of similar agents grows ([R3](#references))
- **SHOULD** avoid adopting a soft, self-imposed artifact ceiling as a review trigger; `nolte-shared` attaches no number to its scoping discipline and relies purely on observed routing-quality and overlap signals. The periodic `skills-agents-sweep` ([R5](#references)) is the review trigger, driven by routing-quality and overlap signals rather than by a count, and never read as a split criterion

### Namespace and naming coherence
- **MUST** choose a plugin `name` that's a stable, collision-resistant **namespace**: plugin skills are always namespaced as `/<plugin-name>:<skill-name>`, and the `plugin.json` `name` field *is* the skill namespace ([R1](#references))
- **MUST** keep artifact naming consistent across the **whole** plugin—one naming convention per artefact type. For this plugin that means **verb-noun (`<object-noun>-<action>`) for skills** (per `skill-management` §Frontmatter validation) and **object-role (`<subject>-<role-noun>`) for agents** (per `agent-management` §Structure); each artefact type stays internally consistent and neither type mixes conventions. Inconsistent naming patterns within a single collection are a documented discoverability anti-pattern ([R2](#references))
- **MUST NOT** rename the plugin namespace casually: the namespace prefix is part of every consumer's `subagent_type:` and `/<plugin>:<skill>` call sites, so a namespace change is a breaking change governed by the same deprecation discipline `skill-vs-agent` §Portfolio-wide consistency applies to artifact reclassification

## Acceptance Criteria
- [ ] Every plugin in the portfolio is justified by a single distribution contract (shared release cadence + marketplace entry + consumer install decision), recorded in its README or top-level orientation file
- [ ] No plugin split in the portfolio is justified solely by topic, lifecycle phase, or artifact count; every split's PR description names a concrete distribution-contract difference from the four enumerated reasons (or a documented equivalent)
- [ ] `nolte-shared` remains a single plugin spanning multiple lifecycle phases; its scannability rests on `phase`/`tags`/catalog/landing-page coverage, verifiable in the built docs site, not on a reduced artifact count
- [ ] The duplicate-prevention invariant holds: no two artifacts in any one plugin share an equivalent capability statement (cross-checked per `skill-vs-agent`)
- [ ] The plugin `name` in `.claude-plugin/plugin.json` is a unique, valid skill namespace, and every plugin skill routes as `/<plugin-name>:<name>`
- [ ] Artifact naming is consistent across the whole plugin—no mix of verb-noun and gerund (or other) conventions in one plugin
- [ ] No requirement in this spec or in any rule citing it asserts "Anthropic scopes plugins by theme"; every breadth/split rule beyond the distribution-contract rule is marked as a local convention
- [ ] A reviewer can decide a proposed second plugin by reading this spec alone: accept when a distribution-contract difference is named, reject when only topic/breadth is cited

## References

- [R1] Plugins, Claude Code docs (plugin-vs-standalone decision keys on sharing/reuse/versioning/marketplace; `plugin.json` `name` is the skill namespace; skills always namespaced as `/<plugin>:<skill>`): <https://code.claude.com/docs/en/plugins>
- [R2] Skill authoring best practices, Anthropic platform docs (`description` drives selection across 100+ skills; vague/generic names and inconsistent intra-collection naming are anti-patterns): <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices>
- [R3] Create custom subagents, Claude Code docs (automatic delegation keys on the `description`; focused single-responsibility subagents): <https://code.claude.com/docs/en/sub-agents>
- [R4] Equipping agents for the real world with Agent Skills, Anthropic engineering, 2025-10-16 (progressive disclosure; install many skills without context penalty): <https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills>
- [R5] `skill-vs-agent`, `skill-management`, `agent-management`, `skill-agent-catalog` (this plugin): the artifact-type, on-disk-shape, and catalog specs this spec sits above

## Open Questions

_All previously deferred open questions were settled on 2026-06-06: each provisional default is now the standing rule. See `.audits/decisions/2026-06-06-settle-open-questions.md` for the per-item decisions and rationale._
