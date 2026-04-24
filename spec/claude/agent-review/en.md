# Claude Agent Review

Status: draft

## Context
<!-- Why does this spec exist? What problem, user need, or constraint drives it? -->

The `agent-management` spec defines how an agent is *authored* — filename, YAML frontmatter (`name`, `description`, `distribution`), tool scoping, system-prompt shape, source and runtime locations. What it does not define is how an agent is *reviewed*: which rules a reviewer checks, in which order, and what deliverable the review leaves behind. Without a shared review procedure, two reviewers of the same agent produce incomparable results, the `skill-vs-agent` rationale rule erodes silently, tool-scope drift accumulates without being caught, and plugin developers consuming the review output cannot script against a stable shape. This spec defines the binding review procedure for agents in the `nolte-shared` plugin; it points at `agent-management` and `skill-vs-agent` as the authoritative sources of findings, and hands the output-format contract to `review-plan`. An agent review produces exactly one `review-plan` artifact under `.audits/agent-review/<agent-name>.md`; once every item is processed the plan is deleted, leaving its git history as the audit trail.

## Goals
<!-- What this spec aims to achieve. Bullet points, outcome-oriented. -->
- Every agent review applies the same set of checks derived from `agent-management` and `skill-vs-agent`, in the same order, with the same severity mapping
- Review output is a `review-plan` artifact — parseable, actionable, and traceable back to a specific spec requirement per finding
- Agent authors can run the review on their own work before proposing it, and a reviewer (human or LLM) can run it later with identical results on the same source tree
- Plugin developers can script against the review output (parse plan files, gate merges on open `BLOCKER`s, count open reviews) without modelling per-reviewer conventions
- The review enforces agent-specific invariants that do not apply to skills — minimal `tools` scoping, read-only agents rejecting write/edit/execution tools, `distribution` declared exactly once, no Skill-tool dispatch inside the agent body — so they do not quietly regress over time

## Non-Goals
<!-- Explicitly out of scope. Prevents creep. -->
- Defining what an agent *is* on disk — `agent-management` owns that
- Deciding whether a capability should have been a skill or an agent in the first place — `skill-vs-agent` owns that; this spec only checks that the choice has been *documented*
- Prescribing the output file format — `review-plan` owns that
- Reviewing skills — `skill-review` covers that with symmetric structure
- Replacing quarterly portfolio-wide reconciliation — `spec-drift-audit` owns that
- Linter and markdown-style checks already enforced by `task lint` / Vale / pre-commit hooks — those stay with their own tooling
- Runtime or behavioral correctness of the agent (whether dispatching the agent actually produces the claimed report shape when invoked) — this spec reviews the **authored artifact**, not a live execution

## Requirements
<!-- Use RFC 2119 keywords: MUST, SHOULD, MAY. One atomic requirement per bullet. -->

### Review scope

- **MUST** take a single agent as input, identified by the path `agents/<name>.md` in a `nolte-shared`-style source tree, or the equivalent runtime path `.claude/agents/<name>.md` / `~/.claude/agents/<name>.md` when reviewing a consumer's copy
- **MUST** treat the following as the review surface, in this order: YAML frontmatter, the markdown body (role, output format, procedure, rationale), every sibling asset under `agents/<name>/` referenced from the body (examples, long-form references, prompt fragments)
- **MUST NOT** review more than one agent per plan; parallel reviews of multiple agents emit one `review-plan` per target
- **MAY** narrow the scope to a specific aspect (frontmatter only, tools only, rationale only) when the review is triggered by a focused change, and **MUST** record the narrowing in the plan's `## Scope` section

### Checks derived from `agent-management`

- **MUST** run a check for every MUST / SHOULD / MAY rule in the canonical `agent-management` spec, producing one finding per failed check with the originating rule cited in the bracketed prefix per `review-plan`
- **MUST** map severity as follows and **MUST NOT** deviate without a documented exception:
  - A failed MUST → `BLOCKER`
  - A failed SHOULD → `WARNING`
  - A failed MAY that the agent clearly would benefit from → `SUGGESTION`
  - An observation that no rule covers but that a future reviewer would want to know → `INFO`
- **MUST** specifically verify these agent-only invariants, each as its own check:
  - Filename matches `<name>.md` in ASCII kebab-case
  - `name` in frontmatter equals the filename without `.md`
  - `description` names concrete triggers (positive triggers at minimum; negative triggers SHOULD be present when overlap with other artifacts is plausible)
  - `distribution` is exactly `plugin` or `project` — no other value, no missing field
  - `tools` is either absent (full tool surface justified in body) or scoped to the minimum set needed for the stated responsibility
  - Read-only agents (agents whose stated responsibility is research, review, audit, or reporting) have **no** write, edit, or execution tools — the presence of any of Edit, Write, Bash, NotebookEdit in a read-only agent's `tools` list is a `BLOCKER`
  - Agent body does **not** invoke the Skill tool on behalf of the user — detected by grepping the body for `Skill(`, `Skill tool`, or equivalent dispatch phrasings; any match is a `BLOCKER` per `skill-vs-agent`
  - No hard-coded absolute paths in the body or in sibling assets
  - Frontmatter and system-prompt content are in English, regardless of the conversation language in which the agent was authored

### Model-choice checks

- **MUST** verify, when the frontmatter declares a `model` field, that its value is exactly one of `opus`, `sonnet`, or `haiku` per `agent-management`; any other value is a `BLOCKER`
- **MUST** verify, when a `model` is pinned, that the system prompt or an accompanying comment states a rationale for the choice; its absence is a `WARNING`, reflecting the SHOULD in `agent-management`
- **SHOULD** run a plausibility check on the pinned `model`: a read-only or reporting agent pinned to `opus` without a stated rationale produces a `SUGGESTION`; a complex audit or planning agent pinned to `haiku` without a stated rationale produces a `SUGGESTION`
- **MAY** record an `INFO` finding when the `model` field is absent, noting that the agent inherits the caller's model per `agent-management`

### Checks derived from `skill-vs-agent`

- **MUST** confirm the agent body contains a **rationale section** that names at least one decisive dimension for the agent-over-skill choice; its absence is a `BLOCKER`
- **SHOULD** verify that at least one counter-dimension is named when the decision was a close call — absence is a `SUGGESTION`, not a `BLOCKER`, consistent with the SHOULD formulation in `skill-vs-agent`
- **MUST** run a duplicate-capability check: grep every other `agents/*.md` and `skills/*/SKILL.md` `description` line for semantic overlap; any plausible overlap produces a `WARNING` naming the peer artifact and the overlap, so the author can propose a merge, rename, or clearer split before landing

### Tool-scope checks

- **MUST** verify, for every tool declared in `tools`, that the agent body demonstrably uses that tool in its procedure — tools declared but not used are `WARNING` findings (dead permission)
- **MUST** verify, for every tool the agent body clearly needs, that it is declared in `tools` — tools used but not declared are `BLOCKER` findings (the agent will fail to run)
- **SHOULD** prefer dedicated tools (`Read`, `Grep`, `Glob`, `Edit`) over `Bash` equivalents; an agent using `Bash` for operations a dedicated tool covers gets a `WARNING` unless the body justifies the choice

### Prompt-structure checks

- **MUST** verify that the system prompt scopes the agent to a single responsibility per the MUST in `agent-management`; absence is a `BLOCKER`
- **MUST** verify that the system prompt names the expected output shape per the MUST in `agent-management`; absence is a `BLOCKER`
- **MUST** verify that the system prompt opens with the agent's role and boundaries, then the expected output format, then the working method per the SHOULD in `agent-management`; deviation is a `WARNING`
- **MUST** verify that the system prompt explicitly declares whether the agent writes code or only researches per the SHOULD in `agent-management`; absence is a `WARNING`
- **SHOULD** flag agent bodies that exceed the soft length target named in `agent-management` (~200 lines) without factoring supporting material into `agents/<name>/` sibling files as a `WARNING`, reflecting the SHOULD in `agent-management`
- **SHOULD** verify, when the agent is authored to write files or cause side effects (its `tools` list includes any of `Edit`, `Write`, `Bash`, or `NotebookEdit`), that the system prompt documents the goals and preconditions of those effects per the `agent-management` acceptance criterion; absence is a `WARNING`

### Review procedure

- **MUST** begin by reading the canonical `agent-management`, `skill-vs-agent`, and `review-plan` specs before producing any finding; findings without an anchor in one of those specs are not valid output of this procedure
- **MUST** produce findings in this order: frontmatter → description/triggers → distribution → model → tools/scope → prompt structure → rationale section → referenced assets → duplicate-prevention check → INFO observations
- **MUST** emit exactly one `review-plan` file at `.audits/agent-review/<agent-name>.md`; the reviewer **MUST** follow every lifecycle rule from `review-plan`, including the single-plan-per-target invariant and the deletion-commit message format
- **SHOULD** embed, in the plan's `## Scope` section, the git SHAs of the spec versions applied so a later re-review can tell whether findings may have become outdated by a spec revision
- **MAY** fold purely stylistic observations (Vale, markdown linting) into `INFO` findings when they aid the author, but **MUST NOT** promote them to `WARNING` or `BLOCKER` — those stay with their own tooling

### Relationship to other specs

- **MUST** reference `review-plan` for the output format; do not restate its requirements here
- **MUST NOT** re-specify anything already covered by `agent-management` or `skill-vs-agent`; when this spec and one of those diverge, the authoring spec wins and this spec is the one that needs updating
- **SHOULD**, when the agent under review is dispatched by a named skill, trigger a companion `skill-review` for that skill only if the skill has not been reviewed against its current source revision — record the decision in the plan's `## Scope` so downstream actors know whether the dispatching skill has been covered

## Acceptance Criteria
<!-- Testable, checkable conditions. A reviewer should be able to mark each as done/not done. -->
- [ ] A worked example exists applying this review procedure to one agent in `nolte-shared` (for instance `audience-review`) and producing a conforming plan under `.audits/agent-review/`
- [ ] Every agent in `agents/` has been reviewed against the current `agent-management` revision at least once since this spec was adopted, verifiable by either an open plan under `.audits/agent-review/` or a closing commit in `git log` matching the `review-plan` deletion pattern
- [ ] No agent in `agents/` lacks a rationale section; running the rationale-section check across all agents produces zero `BLOCKER`s
- [ ] No agent in `agents/` invokes the Skill tool on behalf of the user; a grep for `Skill(` across all agent body files returns zero matches
- [ ] No read-only agent in `agents/` declares `Edit`, `Write`, `Bash`, or `NotebookEdit` in its `tools` list
- [ ] No two agents in `agents/` share an equivalent capability statement, verified by a spot-check of every plan's duplicate-prevention finding
- [ ] Every declared tool in every agent's `tools` list is used at least once in the agent's body; every tool used in the body is declared — both directions pass spot-check
- [ ] Every agent in `agents/` whose frontmatter pins a `model` has a rationale for that choice stated in the system prompt or in an adjacent comment
- [ ] No open plan under `.audits/agent-review/` carries a prompt-structure-order finding at `BLOCKER` severity without citing a corresponding MUST rule in `agent-management`
- [ ] Every agent in `agents/` whose `tools` list includes `Edit`, `Write`, `Bash`, or `NotebookEdit` documents the goals and preconditions of those write effects in its system prompt
- [ ] Every open plan under `.audits/agent-review/` conforms to `review-plan`'s four-section structure and YAML frontmatter
- [ ] The `agent-management` spec's acceptance criteria cross-reference this spec for the review side of its authoring rules
- [ ] A spot-check of three closed plan deletions in `git log` shows the commit message format `review(agent-review): close <agent> — <counts>` exactly

## Open Questions
<!-- Unresolved decisions, known unknowns, things that need a stakeholder answer. -->
- Should the duplicate-prevention check read skill descriptions from `skills/*/SKILL.md` in the same repository only, or should it also query the MkDocs-rendered catalog across installed plugins when a consumer reviews a downstream copy?
- How is "read-only agent" detected mechanically — by the verbs in the `description` (review, audit, research, lint, report), by an explicit `read-only: true` flag in frontmatter that does not yet exist, or by a human judgement captured in the plan's `## Scope`?
- Should the tools-used-vs-tools-declared check tolerate the case where a tool appears only in an example section of the body and not in the procedure itself, or is example-only usage a sign of dead permission?
- When `distribution: project` is declared, should the review verify anything beyond the value itself — for example that the agent does not reference plugin-co-located assets, which would break project-level use?
- Should reviewing an agent whose `description` names negative triggers also verify those negatives actually exclude the named cases — and if so, how is that verified without running the agent?
- How does this spec invocation interact with `audience-review` — the first agent in the portfolio — since reviewing a review-agent is a recursion case worth explicit handling: is the first-ever plan written by the review or by a human, and how is the recursion terminated?
