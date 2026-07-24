# Skill vs. Agent Decision

Status: draft

## Context
Claude Code offers two reusable-capability formats in this plugin: **skills** (authored under `skills/<name>/SKILL.md`) and **agents** (authored under `agents/<name>.md`). The `skill-management` spec governs the on-disk shape of skills; the `agent-management` spec does the same for agents. Neither answers the prior question: **which format fits a given capability?** Without a shared decision rule, portfolio authors drift—the same class of task appears as a skill in one repository and as an agent in another, or the same capability is shipped twice because nobody could decide. The `workflow-health` spec's "Specialized-agent dispatch for remediation" subsection already presupposes a skill-orchestrates-agent-executes pattern; this spec codifies the rule that makes that presupposition consistent across the portfolio.

## Goals
- Every new Claude Code capability in this plugin is authored as either a skill or an agent, never both, based on a deterministic decision rule
- Similar tasks in different repositories land on the same artifact type—no drift between "skill here, agent there" for equivalent work
- The choice is documented in the artifact itself so future readers understand why it was made rather than having to guess
- The skill-as-orchestrator / agent-as-executor pattern is a first-class, explicitly described option rather than an ad-hoc coincidence
- Boundary cases surface as open questions in this spec rather than as quiet drift in the artifact tree

## Non-Goals
- On-disk structure, naming, frontmatter, or templates for either artifact (covered by `skill-management` and `agent-management`)
- Plugin distribution and marketplace mechanics (covered by those specs)
- Plugin-level scoping—when capabilities belong in one plugin versus several, and how a single plugin stays scannable as it grows (covered by `plugin-scoping`)
- Which specific tools a given agent declares in its `tools` field (a per-agent scope decision, not a portfolio-wide rule)
- Discovery and catalog rendering in the MkDocs site (covered by `skill-agent-catalog`)
- The routing behavior of the Claude Code runtime itself—this spec governs authoring choices, not runtime dispatch

## Requirements

### Decision dimensions
Every candidate capability is evaluated along the dimensions below. Each dimension has a natural bias toward one artifact type, captured in the second and third columns. An authored artifact's format choice **MUST** be defensible against this table.

| Dimension | Skill bias | Agent bias |
|---|---|---|
| **Context access** | Needs the main conversation's state (open PR, recent diffs, prior user turns) | Self-contained input; no conversation history required |
| **Interactivity** | User approval or intermediate confirmations are expected mid-flow | Fire-and-forget—parent dispatches once and consumes a structured report |
| **Parallelism** | Sequential, one at a time in the main thread | Multiple instances can run in parallel when sent in a single tool-call batch |
| **Tool surface** | The invoking Claude's full tool surface is adequate | A narrower, declared `tools` scope is preferable (principle of least authority) |
| **Context-window impact** | Output contributes to the main conversation naturally | Heavy reads / searches would pollute the main context; isolation is a win |
| **Specialization** | General procedure; a focused system prompt wouldn't measurably change quality | A narrow system prompt noticeably sharpens output quality |
| **Lifecycle** | Persists across the conversation—may be invoked more than once | Single-shot task with a clear completion criterion |
| **Latency** | Fast turnaround matters; a subagent's separate context window adds spin-up and round-trip overhead | Latency isn't critical; the task can run out-of-band and report back when done |
| **Change scope** | A quick, targeted change in the current context | A larger self-contained unit of work with a well-defined input and output |

These dimensions track Anthropic's official "Choose between subagents and the main conversation" guidance ([R5](#references)): route work to the **main conversation** (a skill) when it needs frequent back-and-forth, when multiple phases share significant context, when the change is **quick and targeted**, or when **latency** matters; route it to a **subagent** (an agent) when the task emits verbose output the orchestrator doesn't need, when tool or permission restriction is wanted, or when the work is self-contained and returns a summary. The **Latency** and **Change scope** rows carry the two criteria the rest of the table didn't already capture. Of the agent-side dimensions, Anthropic frames **parallelism and context management as the two *primary* drivers** for moving work into a subagent (specialization and tool restriction are sub-cases of context management) ([R6](#references)); the **Parallelism** and **Context-window impact** rows are therefore the load-bearing ones when an agent is chosen.

### Primary decision rule
- **MUST** choose a **skill** when the capability satisfies any of:
  - The procedure is one step in a larger human-driven workflow (creating a PR, landing a PR, scaffolding a project, running an audit)
  - Mid-flow user approval is required at least once
  - The output is expected to flow back into the main conversation's context naturally, without a structured report boundary
  - The procedure itself dispatches one or more agents—the orchestrator is always a skill
- **MUST** choose an **agent** when the capability satisfies any of:
  - The task is self-contained with a well-defined input and a well-defined output shape
  - The task is a candidate for parallel execution alongside other independent work
  - Context-window protection matters because the task performs large-volume reads, searches, or file traversals
  - Tool restriction is desired (read-only research, lint-only, refactor-only) and would measurably improve safety or behavior
  - A specialized, narrow system prompt measurably improves the task's output quality
- **MUST** default to a **skill** when the criteria above are contradictory or genuinely ambiguous; the rationale is that skills remain the human-visible surface and can dispatch agents later without restructuring consumer workflows, whereas an agent can't become a skill without losing its isolation contract
- **MUST**, when tool restriction **and** mid-flow interactivity both apply, author a **skill** and declare `allowed-tools` (per `skill-management`) for voluntary tool discipline; an agent with a pause/resume protocol is **forbidden** because an agent runs in an isolated subagent context with no stable way to surface skill-level interactivity back to the parent conversation (see §Hybrid pattern). This is a direct consequence of the default-to-skill rule above, not a separate escape hatch.

### Hybrid pattern: Skill orchestrates, agent executes
- **MUST** model implementation work that sits inside a broader workflow as `skill → Agent(subagent_type=<agent>)` rather than as a monolithic skill whenever at least one agent-side criterion (context-window protection, parallelism, tool restriction, specialization) applies to the implementation step
- **MUST NOT** invert this pattern—an agent **MUST NOT** invoke the Skill tool on behalf of the user, because agents run in an isolated subagent context and have no stable way to surface skill-level interactivity back to the parent conversation
- **MUST NOT** assume an agent can spawn a further subagent—Claude Code subagents **can't spawn other subagents** ([R1](#references)). The skill remains the only level at which fan-out happens; an agent that needs sub-work either folds the work into its own context or returns control to the calling skill
- **SHOULD** keep the skill's role limited to orchestration, user interaction, and validation of the agent's output; the agent does the hands-on reading, editing, or researching
- **SHOULD** chain multiple agents sequentially from a skill when the responsibilities split naturally (for example: a YAML-fix agent, then a git-commit agent, then the `pull-request-create` skill—calling another skill from a skill in the same thread is allowed)
- The `workflow-health` spec's "Specialized-agent dispatch for remediation" subsection is the canonical portfolio-level instance of this pattern; changes to that subsection **MUST** stay consistent with the rule declared here

### Forked skills: A third option, not a fourth artifact

Claude Code supports running a skill itself in an isolated subagent context by setting `context: fork` plus `agent: <type>` in the skill's frontmatter ([R2](#references)). The skill's body becomes the prompt that drives the forked subagent; the skill's own tool surface is replaced by the named agent type's tools and model. This is the **inverse** of a subagent's `skills:` preload field—both arrive at the same composition through different ownership.

- **MAY** ship a capability as a skill with `context: fork` instead of a separate agent file when the capability is naturally **single-shot, fits the subagent isolation contract, AND** would otherwise duplicate orchestration logic an existing skill already owns
- **MUST NOT** treat `context: fork` as a way to bypass the skill-vs-agent rule—the choice is still governed by the decision dimensions table; the fork only changes *how* a chosen skill executes, not whether the capability should have been a skill in the first place
- **SHOULD**, when the choice is between "new agent" and "existing skill grows a `context: fork` mode," prefer the latter only if the new mode shares non-trivial logic with the skill's existing behavior; otherwise the new agent stays a separate artifact and `skill-vs-agent`'s decision rule applies normally

### Duplicate prevention
- **MUST NOT** ship a skill and an agent that provide equivalent capabilities within the `nolte-shared` plugin; one artifact per capability is the invariant
- **MUST**, before authoring a new artifact, check the existing skills under `skills/` and agents under `agents/` for an equivalent or near-equivalent capability (read every `description` line; don't rely on name similarity alone)
- The canonical audit-time mechanism for this in-plugin capability-equivalence check is the `skills-agents-sweep` skill's boundary-matrix step: a **semantic read of every `description` line** that classifies each overlapping pair as conflict, adjacent, or chain. Keyword intersection or embedding similarity **MAY** serve only as an optional pre-filter that narrows candidate pairs for the semantic read; neither **MAY** stand in for the decision itself
- **SHOULD**, when the boundary is genuinely blurry between an existing artifact and a proposed new one, propose a merge, a rename, or a clearer split as part of the authoring PR—never silently ship a third overlapping artifact
- **MAY** tolerate equivalent-looking artifacts across **different** plugins; this rule is scoped to `nolte-shared`, and downstream plugins own their own de-duplication

### Decision process for authors
1. **State the capability in one sentence.** If a one-sentence statement is impossible, the capability is too broad—split it before applying the rule.
2. **Walk the decision dimensions table** and record the bias for each dimension. A dimension's bias carries more weight when the dimension is load-bearing for the task (parallelism matters if the task genuinely runs multiple times; tool restriction matters if the task touches credentials).
3. **Apply the primary decision rule.** If both paths fit, default to a skill.
4. **Check for duplicates** against existing skills and agents. Stop if an equivalent artifact already exists; extend, rename, or supersede it rather than shipping a new one.
5. **Author the artifact** per `skill-management` or `agent-management`.
6. **Document the choice** in the artifact body (see "Rationale documentation" below).

### Rationale documentation
- **MUST** include a short rationale section in the artifact body (not only in the frontmatter `description`): one short paragraph or a two-to-four-bullet list naming the decisive dimensions that led to the skill-vs-agent choice
- **SHOULD** name at least one dimension that pointed the other way and the reason it was outweighed; absence of a counter-dimension note implies the choice was uncontested
- The one-dimension floor is intentional and deliberately a hard **MUST**, while the two-dimension structure (a second named dimension plus a counter-dimension) is deliberately only a **SHOULD**: forcing two named dimensions on a genuinely one-sided choice produces filler prose rather than a sharper audit, so the floor isn't raised
- **MAY** reference a specific sibling artifact as precedent (for example: "follows the same orchestrator pattern as `pull-request-create`")
- The placement within the body is at the author's discretion; sensible locations are directly under the top-level heading or as a short footer just before the hard rules

### Rationale section heading
- **MUST** for skills use exactly the heading `## Why this is a skill, not an agent` for the rationale section; alternative phrasings (for example, `## Rationale (why a skill, not an agent)`, `## Rationale`) are non-conformant
- **MUST** for agents use exactly the heading `## Why this is an agent, not a skill` for the rationale section
- **MAY** add additional rationale sub-headings if a particular skill or agent has a topic-specific rationale dimension (for example, `## Why this is one skill, not three` is acceptable as an additional H2 alongside the mandatory `## Why this is a skill, not an agent`), but the mandatory heading MUST be present
- Rationale: deterministic heading enables `grep`-based portfolio audits, single source of truth for the section semantic

### Portfolio-wide consistency
- **MUST**, when a capability class recurs across three or more consuming repositories, ship it as a plugin-level artifact rather than as project-local copies; the three-recurrence constant is owned by the `continuous-improvement` spec (the most general statement of the rule), and `workflow-health`, `portfolio-management`, and this spec all defer to it. The threshold changes only in lockstep across all four specs—this spec **MUST NOT** diverge to a different number. The decision rule above still determines whether the plugin-level artifact is a skill or an agent
- **SHOULD** align a new artifact with the artifact type used by existing peers in the same functional cluster (PR management, audit, lint, release tooling): when every existing peer is a skill, the new one is a skill unless a dimension forces the other way
- **SHOULD** use the optional `tags` field (per `skill-management` / `agent-management`) as the machine-checkable signal for peer-cluster membership—artifacts sharing a tag form a cluster in the catalog's tag index, so cluster alignment is verifiable from frontmatter rather than relying on name similarity
- **MAY** propose reclassification of an existing artifact (skill → agent or vice versa) when repeated usage reveals the initial choice was wrong; such a reclassification is a breaking change for consumers and **MUST** be shipped as a new artifact plus a deprecation note on the old one, never as a silent format flip

## Acceptance Criteria
- [ ] Every skill under `skills/` in this plugin contains a rationale section in `SKILL.md` that names at least one decisive dimension for the skill-over-agent choice
- [ ] Every agent under `agents/` in this plugin contains a rationale section in its markdown body that names at least one decisive dimension for the agent-over-skill choice
- [ ] No two artifacts in this plugin (any mix of skill and agent) share an equivalent capability statement—an audit that reads every `description` line finds no equivalents
- [ ] No agent in this plugin invokes the Skill tool on behalf of the user, verifiable by grepping agent system-prompt bodies for `Skill(` or equivalent skill-dispatch phrasings
- [ ] For every capability that recurs in three or more consuming repositories, exactly one `nolte-shared` artifact exists (skill or agent) covering it
- [ ] Every reclassification of an existing artifact (skill ↔ agent) ships as a new artifact plus a deprecation note on the old one, never as an in-place format swap
- [ ] The `workflow-health` spec's "Specialized-agent dispatch for remediation" subsection stays consistent with the hybrid-pattern rule declared here; any future divergence is resolved in favor of this spec
- [ ] No agent in this plugin attempts to spawn another subagent (verifiable by grepping agent bodies for `Agent(`, `subagent_type`, or equivalent dispatch phrasings)
- [ ] Every skill that declares `context: fork` documents in its rationale section why the fork variant is preferable to a sibling agent file
- [ ] The decision-dimensions table is consistent with the official Anthropic guidance on when to use the main conversation versus a subagent ([R3](#references), [R5](#references)); divergences are resolved in favor of this spec but explained in `## Open Questions`
- [ ] The decision-dimensions table includes the **Latency** and **Change scope** dimensions that reflect Anthropic's "Choose between subagents and the main conversation" criteria ([R5](#references))

## References

- [R1] Create custom subagents, Claude Code docs (subagents can't spawn subagents): <https://code.claude.com/docs/en/sub-agents>
- [R2] Extend Claude with skills, Claude Code docs (`context: fork`): <https://code.claude.com/docs/en/skills>
- [R3] Building Effective AI Agents, Anthropic engineering: <https://www.anthropic.com/research/building-effective-agents>
- [R4] Equipping agents for the real world with Agent Skills, Anthropic engineering, 2025-10-16: <https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills>
- [R5] Create custom subagents, Claude Code docs, "Choose between subagents and the main conversation" section (use the main conversation for quick targeted changes / when latency matters; use a subagent for verbose output, tool restriction, self-contained work): <https://code.claude.com/docs/en/sub-agents>
- [R6] Subagents in the Claude Agent SDK (four benefits—context isolation, parallelism, specialized instructions, tool restrictions—with parallelism and context management as the two primary drivers): <https://code.claude.com/docs/en/agent-sdk/subagents>

## Open Questions

_All previously deferred open questions were settled on 2026-06-06: each provisional default is now the standing rule. The per-item decisions and rationale are preserved in git history (decision log, 2026-06-06)._
