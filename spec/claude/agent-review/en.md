# Claude Agent Review

Status: draft

## Context
<!-- Why does this spec exist? What problem, user need, or constraint drives it? -->

The `agent-management` spec defines how an agent is *authored*: filename, YAML frontmatter (`name`, `description`, `distribution`), tool scoping, system-prompt shape, source and runtime locations. What it doesn't define is how an agent is *reviewed*: which rules a reviewer checks, in which order, and what deliverable the review leaves behind. Without a shared review procedure, two reviewers of the same agent produce incomparable results, the `skill-vs-agent` rationale rule erodes silently, tool-scope drift accumulates without being caught, and plugin developers consuming the review output can't script against a stable shape. This spec defines the binding review procedure for agents in the `nolte-shared` plugin; it points at `agent-management` and `skill-vs-agent` as the authoritative sources of findings, and hands the output-format contract to `review-plan`. An agent review produces exactly one `review-plan` artifact under `.audits/agent-review/<agent-name>.md`; once every item is processed the plan is deleted, leaving its git history as the audit trail.

## Goals
<!-- What this spec aims to achieve. Bullet points, outcome-oriented. -->
- Every agent review applies the same set of checks derived from `agent-management` and `skill-vs-agent`, in the same order, with the same severity mapping
- Review output is a `review-plan` artifact—parseable, actionable, and traceable back to a specific spec requirement per finding
- Agent authors can run the review on their own work before proposing it, and a reviewer (human or LLM) can run it later with identical results on the same source tree
- Plugin developers can script against the review output (parse plan files, gate merges on open `Critical`s, count open reviews) without modelling per-reviewer conventions
- The review enforces agent-specific invariants that don't apply to skills—minimal `tools` scoping, read-only agents rejecting write/edit/execution tools, `distribution` declared exactly once, no Skill-tool dispatch inside the agent body—so they don't quietly regress over time

## Non-Goals
<!-- Explicitly out of scope. Prevents creep. -->
- Defining what an agent *is* on disk: `agent-management` owns that
- Deciding whether a capability should have been a skill or an agent in the first place: `skill-vs-agent` owns that; this spec only checks that the choice has been *documented*
- Prescribing the output file format: `review-plan` owns that
- Reviewing skills: `skill-review` covers that with symmetric structure
- Replacing quarterly portfolio-wide reconciliation: `spec-drift-audit` owns that
- Linter and markdown-style checks already enforced by `task lint` / Vale / pre-commit hooks—those stay with their own tooling
- Runtime or behavioral correctness of the agent (whether dispatching the agent actually produces the claimed report shape when invoked)—this spec reviews the **authored artifact**, not a live execution—including whether a negative trigger named in `description` actually causes the calling Claude to *not* dispatch the agent for the excluded case; the review verifies only that the negative trigger is present and names an existing peer artifact (see §"Description quality and proactive-delegation intent" and §"Checks derived from `skill-vs-agent`"), not its routing effect

## Requirements
<!-- Use RFC 2119 keywords: MUST, SHOULD, MAY. One atomic requirement per bullet. -->

### Review scope

- **MUST** take a single agent as input, identified by the path `agents/<name>.md` in a `nolte-shared`-style source tree, or the equivalent runtime path `.claude/agents/<name>.md` / `~/.claude/agents/<name>.md` when reviewing a consumer's copy
- **MUST** treat the following as the review surface, in this order: YAML frontmatter, the markdown body (role, output format, procedure, rationale), and any external supporting asset referenced from the body (examples, long-form references, prompt fragments living outside the `agents/` tree). A companion markdown file in a sibling `agents/<name>/` folder is itself a finding—recursive discovery registers it as a phantom agent (see `agent-management` §Structure)—not a legitimate part of the surface
- **MUST NOT** review more than one agent per plan; parallel reviews of multiple agents emit one `review-plan` per target
- **MAY** narrow the scope to a specific aspect (frontmatter only, tools only, rationale only) when the review is triggered by a focused change, and **MUST** record the narrowing in the plan's `## Scope` section

### Checks derived from `agent-management`

- **MUST** run a check for every MUST / SHOULD / MAY rule in the canonical `agent-management` spec, producing one finding per failed check with the originating rule cited in the bracketed prefix per `review-plan`
- **MUST** map severity as follows and **MUST NOT** deviate without a documented exception:
  - A failed MUST → `Critical`
  - A failed SHOULD → `Warning`
  - A failed MAY that the agent clearly would benefit from → `Suggestion`
  - An observation that no rule covers but that a future reviewer would want to know → `Info`
- **MUST** specifically verify these agent-only invariants, each as its own check:
  - Filename matches `<name>.md` in ASCII kebab-case
  - `name` in frontmatter equals the filename without `.md`
  - `description` names concrete triggers (positive triggers at minimum; negative triggers SHOULD be present when overlap with other artifacts is plausible)
  - `distribution` is exactly `plugin` or `project`: no other value, no missing field
  - `tools` is either absent (full tool surface justified in body) or scoped to the minimum set needed for the stated responsibility
  - Read-only agents (agents whose stated responsibility is research, review, audit, or reporting) have **no** write, edit, or execution tools—the presence of any of Edit, Write, Bash, NotebookEdit in a read-only agent's `tools` list is a `Critical`. **Narrow exception** per `agent-management` §Tool access: `Bash` on a read-only agent is downgraded from `Critical` to `Info` when the agent body carries a `## Read-only Bash justification` section that names the exact subset of side-effect-free commands the agent invokes (typically `git log`, `git rev-parse`, `git ls-files`, `gh api ... --jq` against read-only endpoints) and explicitly forbids any write or mutation. `Edit`, `Write`, and `NotebookEdit` remain unconditional `Critical`s; the exception is `Bash`-only. Read-only status is detected from the responsibility verbs in `description` / system prompt (review, audit, research, lint, report); no `read-only` frontmatter flag exists. When the classification is genuinely ambiguous, the reviewer records the call in the plan's `## Scope`
  - Agent body **never** invokes the Skill tool on behalf of the user—detected by grepping the body for `Skill(`, `Skill tool`, or equivalent dispatch phrasings; any match is a `Critical` per `skill-vs-agent`
  - No hard-coded absolute paths in the body or in sibling assets
  - Frontmatter field names and technical identifier values (`name`, `distribution`, `tools`, `model`, `tags`) are English; the `description` value and the system-prompt body comply with `agent-management.Structure`: English by default, with a project-language exception for `distribution: project` agents whose consuming project declares a non-English documentation language and authorizes it for agent prose. Verify the project authorization (typically `CLAUDE.md`) is present before downgrading what would otherwise be a `Critical` to `Info`

### Model-choice checks

- **MUST** verify, when the frontmatter declares a `model` field, that its value is exactly one of `opus`, `sonnet`, or `haiku` per `agent-management`; any other value is a `Critical`
- **MUST** verify, when a `model` is pinned, that the system prompt or an accompanying comment states a rationale for the choice; its absence is a `Warning`, reflecting the SHOULD in `agent-management`
- **SHOULD** run a plausibility check on the pinned `model`: a read-only or reporting agent pinned to `opus` without a stated rationale produces a `Suggestion`; a complex audit or planning agent pinned to `haiku` without a stated rationale produces a `Suggestion`
- **MAY** record an `Info` finding when the `model` field is absent, noting that the agent inherits the caller's model per `agent-management`

### Checks derived from `skill-vs-agent`

- **MUST** confirm the agent body contains a **rationale section** that names at least one decisive dimension for the agent-over-skill choice; its absence is a `Critical`
- **SHOULD** verify that at least one counter-dimension is named when the decision was a close call—absence is a `Suggestion`, not a `Critical`, consistent with the SHOULD formulation in `skill-vs-agent`
- **MUST** run a duplicate-capability check: grep every other `agents/*.md` and `skills/*/SKILL.md` `description` line for semantic overlap; any plausible overlap produces a `Warning` naming the peer artifact and the overlap, so the author can propose a merge, rename, or clearer split before landing. The check is scoped to the source tree under review (in-repo `agents/*.md` and `skills/*/SKILL.md`); cross-plugin equivalence is explicitly tolerated per `skill-vs-agent` §Duplicate prevention and isn't a finding

### Checks derived from spec-driven-development

- **MUST** run a spec-anchor check: verify the agent body contains at least one reference to a `spec/...` path. An agent without any spec citation is a `Critical` finding per `spec/project/spec-driven-development/` MUST
- **MAY** suppress this check with a documented exception in the plan's `## Scope` section when an agent is explicitly classified as "implementation-only"; suppression must be anchored in a spec or a recorded project decision
- Rationale: this check operationalises the MUST from spec-driven-development that has so far been operator-only

### Tool-scope checks

- **MUST** verify, for every tool declared in `tools`, that the agent body demonstrably uses that tool in its procedure (the agent's working method, not merely an illustrative example section)—a tool that appears only inside an example is dead permission and a `Warning`; tools declared but not used are `Warning` findings (dead permission)
- **MUST** verify, for every tool the agent body clearly needs, that it's declared in `tools`: tools used but not declared are `Critical` findings (the agent will fail to run)
- **MUST** verify the agent **doesn't omit** the `tools` field unintentionally: an absent `tools` field grants the inherited full tool surface, which is permission sprawl. If the agent's responsibility is "research" / "review" / "audit" / "report" and `tools` is absent, that's a `Critical`; for any other agent the absence is a `Warning` unless the body explicitly justifies inheriting all tools ([R5](#references), [R6](#references))
- **SHOULD** prefer dedicated tools (`Read`, `Grep`, `Glob`, `Edit`) over `Bash` equivalents; an agent using `Bash` for operations a dedicated tool covers gets a `Warning` unless the body justifies the choice
- **MUST** verify, when both `tools` and `disallowedTools` are declared, that no tool name appears in both lists (the runtime applies deny then allow, so a double-listed tool is silently removed) and that the resolved set is non-empty; either condition is a `Warning`

### Plugin-distribution constraint checks

Mirrors `agent-management` §"Plugin-distribution security constraints"; cite the originating rule when a finding pins one.

- **MUST** verify, when `distribution: plugin` is declared, that the frontmatter **doesn't** set `hooks`, `mcpServers`, or `permissionMode`; any of those fields is a `Critical` (the runtime silently ignores them for plugin agents and the author is being misled into thinking they're active) ([R5](#references))
- **MUST**, when `distribution: project` is declared, accept those fields as valid; their presence **isn't** a finding for project-distributed agents
- **SHOULD**, when an agent declares `distribution: plugin` AND its body describes behavior that obviously requires `hooks` / `mcpServers` / `permissionMode` (for example "this agent installs a PreToolUse hook," "this agent connects to its own MCP server," "this agent runs in plan mode"), flag a `Warning` even if the fields are absent—the description and the distribution are inconsistent
- **SHOULD** verify, when `distribution: project` is declared, that the body references no plugin-co-located asset (`${CLAUDE_PLUGIN_ROOT}` or paths under the plugin source tree's own `agents/` or `skills/` tree, marketplace-relative assets) that would not resolve in a project runtime; such a reference is a `Warning`

### Subagent-boundary checks

Mirrors `agent-management` §"Subagent boundaries" and `skill-vs-agent` §"Hybrid pattern"; cite the originating rule when a finding pins one.

- **MUST** verify the agent body **never** dispatches another subagent—grep the body for `Agent(`, `subagent_type`, `Task(`, or equivalent dispatch phrasings; any match is a `Critical` (Claude Code subagents can't spawn subagents) ([R5](#references))
- **MUST** verify the agent body **never** invokes the Skill tool on behalf of the user—grep the body for `Skill(`, `Skill tool`, or equivalent skill-dispatch phrasings; any match is a `Critical` per `skill-vs-agent`

### Description quality and proactive-delegation intent

- **MUST** verify, when the `description` contains the phrase "use proactively" (or the equivalent "use this proactively," "should be used proactively," "invoke proactively"), that the agent's responsibility actually warrants Claude offering it without explicit user request—signs a check passes: the agent solves a class of problem the user is unlikely to name explicitly (security review on every PR, audit on every commit). Signs the check fails: the agent has destructive side effects, requires credentials, or makes commitments to external systems. A "proactively" claim on a destructive or credential-bearing agent is a `Critical` ([R5](#references))
- **SHOULD** verify, when the agent has clear overlap with another existing artifact (skill or agent), that `description` names the overlap as a **negative trigger** ("don't use for X, use the `<peer>` agent / skill instead"); absence of the negative is a `Warning` ([R5](#references)). The check verifies only that the negative trigger is *present* and names an existing peer; whether it actually causes the calling Claude to skip the agent for the excluded case is dispatch-time routing behavior and is deliberately out of scope (see §Non-Goals)

### Prompt-structure checks

- **MUST** verify that the system prompt scopes the agent to a single responsibility per the MUST in `agent-management`; absence is a `Critical`
- **MUST** verify that the system prompt names the expected output shape per the MUST in `agent-management`; absence is a `Critical`
- **MUST** verify that the system prompt opens with the agent's role and boundaries, then the expected output format, then the working method per the SHOULD in `agent-management`; deviation is a `Warning`
- **MUST** verify that the system prompt explicitly declares whether the agent writes code or only researches per the SHOULD in `agent-management`; absence is a `Warning`
- **SHOULD** flag agent bodies that exceed the soft length target named in `agent-management` (~200 lines) as a `Warning`, reflecting the SHOULD in `agent-management`; the remedy is tighter prose or moving genuinely oversized assets outside the `agents/` tree, never a sibling `agents/<name>/` folder
- **SHOULD** verify, when the agent is authored to write files or cause side effects (its `tools` list includes any of `Edit`, `Write`, `Bash`, or `NotebookEdit`), that the system prompt documents the goals and preconditions of those effects per the `agent-management` acceptance criterion; absence is a `Warning`

### Review procedure

- **MUST** begin by reading the canonical `agent-management`, `skill-vs-agent`, and `review-plan` specs before producing any finding; findings without an anchor in one of those specs aren't valid output of this procedure
- **MUST** produce findings in this order: frontmatter → description/triggers → distribution → model → tools/scope → prompt structure → rationale section → referenced assets → duplicate-prevention check → INFO observations
- **MUST** emit exactly one `review-plan` file at `.audits/agent-review/<agent-name>.md`; the reviewer **MUST** follow every lifecycle rule from `review-plan`, including the single-plan-per-target invariant and the deletion-commit message format
- **SHOULD** embed, in the plan's `## Scope` section, the git SHAs of the spec versions applied so a later re-review can tell whether findings may have become outdated by a spec revision
- **MAY** fold purely stylistic observations (Vale, markdown linting) into `Info` findings when they aid the author, but **MUST NOT** promote them to `Warning` or `Critical`: those stay with their own tooling

### Relationship to other specs

- **MUST** reference `review-plan` for the output format; don't restate its requirements here
- **MUST NOT** re-specify anything already covered by `agent-management` or `skill-vs-agent`; when this spec and one of those diverge, the authoring spec wins and this spec is the one that needs updating
- **SHOULD**, when the agent under review is dispatched by a named skill, trigger a companion `skill-review` for that skill only if the skill hasn't been reviewed against its current source revision—record the decision in the plan's `## Scope` so downstream actors know whether the dispatching skill has been covered

## Acceptance Criteria
<!-- Testable, checkable conditions. A reviewer should be able to mark each as done/not done. -->
- [ ] A worked example exists applying this review procedure to one agent in `nolte-shared` (for instance `audience-review`) and producing a conforming plan under `.audits/agent-review/`; `audience-review` is reviewed as an ordinary single-target run—the reviewer named `agent-review` is a skill, not a self-reviewing agent, so no recursion-termination logic is required
- [ ] Every agent in `agents/` has been reviewed against the current `agent-management` revision at least once since this spec was adopted, verifiable by either an open plan under `.audits/agent-review/` or a closing commit in `git log` matching the `review-plan` deletion pattern
- [ ] No agent in `agents/` lacks a rationale section; running the rationale-section check across all agents produces zero `Critical`s
- [ ] No agent in `agents/` invokes the Skill tool on behalf of the user; a grep for `Skill(` across all agent body files returns zero matches
- [ ] No read-only agent in `agents/` declares `Edit`, `Write`, `Bash`, or `NotebookEdit` in its `tools` list
- [ ] No two agents in `agents/` share an equivalent capability statement, verified by a spot-check of every plan's duplicate-prevention finding
- [ ] Every declared tool in every agent's `tools` list is used at least once in the agent's body; every tool used in the body is declared—both directions pass spot-check
- [ ] Every agent in `agents/` whose frontmatter pins a `model` has a rationale for that choice stated in the system prompt or in an adjacent comment
- [ ] No open plan under `.audits/agent-review/` carries a prompt-structure-order finding at `Critical` severity without citing a corresponding MUST rule in `agent-management`
- [ ] Every agent in `agents/` whose `tools` list includes `Edit`, `Write`, `Bash`, or `NotebookEdit` documents the goals and preconditions of those write effects in its system prompt
- [ ] Every open plan under `.audits/agent-review/` conforms to `review-plan`'s four-section structure and YAML frontmatter
- [ ] The `agent-management` spec's acceptance criteria cross-reference this spec for the review side of its authoring rules
- [ ] A spot-check of three closed plan deletions in `git log` shows the commit message format `review(agent-review): close <agent>—<counts>` exactly
- [ ] No plan under `.audits/agent-review/` closes with an unresolved `Critical` for `distribution: plugin` agents declaring `hooks`, `mcpServers`, or `permissionMode`
- [ ] Every plan under `.audits/agent-review/` runs the subagent-boundary checks (no agent-spawning, no Skill-tool invocation) against the target agent
- [ ] Every plan under `.audits/agent-review/` runs the proactive-delegation-intent check against any agent whose `description` contains "use proactively" or an equivalent phrase
- [ ] No agent omits the `tools` field while declaring a research / review / audit / report responsibility (zero `Critical`s on the new permission-sprawl check)

## References

Sources for the additional checks above. Cite the relevant entry in finding bracketed prefixes when a check pins a specific upstream rule.

- [R1] Agent management spec (this plugin): `spec/claude/agent-management/`
- [R2] Skill vs. agent decision (this plugin): `spec/claude/skill-vs-agent/`
- [R3] Skill management spec (this plugin, for cross-format alignment): `spec/claude/skill-management/`
- [R4] Review plan spec (output format): `spec/claude/review-plan/`
- [R5] Create custom subagents, Claude Code docs: <https://code.claude.com/docs/en/sub-agents>
- [R6] Best practices for Claude Code subagents, PubNub Engineering: <https://www.pubnub.com/blog/best-practices-for-claude-code-sub-agents/>

## Open Questions
<!-- Unresolved decisions, known unknowns, things that need a stakeholder answer. -->
_None at this time._
