# Claude Skill Review

Status: draft

## Context
<!-- Why does this spec exist? What problem, user need, or constraint drives it? -->

The `skill-management` spec defines how a skill is *authored*: on-disk shape, frontmatter, templates, distribution form. What it doesn't define is how a skill is *reviewed*: which requirements a reviewer checks, in which order, and what deliverable the review leaves behind. Without a shared review procedure, two reviewers of the same skill produce incomparable results, the `skill-vs-agent` rationale-documentation rule slips silently, and plugin developers consuming the review output have to reverse-engineer each reviewer's private shape. This spec defines the binding review procedure for skills in the `nolte-shared` plugin, points at `skill-management` and `skill-vs-agent` as the sources of truth for what counts as a finding, and hands the output-format contract to `review-plan`. A skill review produces exactly one `review-plan` artifact under `.audits/skill-review/<skill-name>.md`; once every item is processed the plan is deleted, leaving its git history as the audit trail.

## Goals
<!-- What this spec aims to achieve. Bullet points, outcome-oriented. -->
- Every skill review applies the same set of checks derived from `skill-management` and `skill-vs-agent`, in the same order, with the same severity mapping
- Review output is a `review-plan` artifact—parseable, actionable, and traceable back to a specific spec requirement per finding
- Skill authors can run the review on their own work before proposing it, and a reviewer (human or LLM) can run it later with identical results on the same source tree
- Plugin developers can script against the review output (parse plan files, gate merges on open `Critical`s, count open reviews) without having to model per-reviewer conventions
- The review distinguishes **authoring-spec compliance** (`skill-management` rules) from **decision-rule compliance** (`skill-vs-agent` rationale) without conflating the two into a single pass/fail

## Non-Goals
<!-- Explicitly out of scope. Prevents creep. -->
- Defining what a skill *is* on disk: `skill-management` owns that
- Deciding whether a capability should have been a skill or an agent in the first place: `skill-vs-agent` owns that; this spec only checks that the choice has been *documented*
- Prescribing the output file format: `review-plan` owns that
- Reviewing agents: `agent-review` covers that with symmetric structure
- Replacing quarterly portfolio-wide reconciliation: `spec-drift-audit` owns that
- Linter and markdown-style checks already enforced by `task lint` / Vale / pre-commit hooks—those stay with their own tooling
- Runtime or behavioral correctness of the skill (whether the skill actually does what its description promises when invoked)—this spec reviews the **authored artifact**, not a live execution

## Requirements
<!-- Use RFC 2119 keywords: MUST, SHOULD, MAY. One atomic requirement per bullet. -->

### Review scope

- **MUST** take a single skill as input, identified by the path `skills/<name>/` in a `nolte-shared`-style source tree, or the equivalent runtime path `.claude/skills/<name>/` when reviewing a consumer's installed copy
- **MUST** treat the following files as the review surface, in this order: `SKILL.md` (frontmatter and body), every file referenced by a relative path from `SKILL.md` (templates, assets, example fragments), and any sibling `agents/<name>.md` the skill dispatches to (to confirm the orchestration direction)
- **MUST NOT** review more than one skill per plan; parallel reviews of multiple skills emit one `review-plan` per target
- **MAY** narrow the scope to a specific aspect (frontmatter only, templates only) when the review is triggered by a focused change, and **MUST** record the narrowing in the plan's `## Scope` section

### Checks derived from `skill-management`

- **MUST** run a check for every MUST / SHOULD / MAY rule in the canonical `skill-management` spec, producing one finding per failed check with the originating rule cited in the bracketed prefix per `review-plan`
- **MUST** map severity as follows and **MUST NOT** deviate without a documented exception:
  - A failed MUST → `Critical`
  - A failed SHOULD → `Warning`
  - A failed MAY that the skill clearly would benefit from → `Suggestion`
  - An observation that no rule covers but that a future reviewer would want to know → `Info`
- **MUST** explicitly cover these high-impact areas even when the corresponding rule in `skill-management` is expressed only as a SHOULD: frontmatter field presence (`name`, `description`), description-contains-concrete-triggers, absence of hard-coded absolute paths in referenced assets, existence of every template the skill references—a referenced template/asset that doesn't exist is a `Critical` (broken reference); intent to add it before merge is tracked by the plan item remaining open, not by a lower severity
- **SHOULD** flag as `Info` any part of the skill body that could be factored into a sibling file to keep the main prompt under the soft length target named in `skill-management`

### Checks derived from `skill-vs-agent`

- **MUST** confirm the skill body contains a **rationale section** that names at least one decisive dimension for the skill-over-agent choice; its absence is a `Critical`
- **SHOULD** verify at least one counter-dimension is named when the decision was a close call; absence is a `Suggestion`, consistent with the SHOULD in `skill-vs-agent` and symmetric with the matching rule in `agent-review`
- **MUST** verify the skill doesn't dispatch the Skill tool on behalf of an agent (not applicable in this direction, but the reverse direction—a skill calling an agent via the Agent tool—is expected and isn't a finding)
- **MUST** run a duplicate-capability check: grep every other `skills/*/SKILL.md` and `agents/*.md` `description` line **in the current repository only** for semantic overlap; any plausible overlap produces a `Warning` naming the peer artifact and the overlap, so the author can propose a merge, rename, or clearer split before landing. Cross-plugin overlap is out of scope here—the `skill-vs-agent` duplicate-prevention rule is scoped to this plugin, and portfolio-wide reconciliation across installed plugins is owned by `spec-drift-audit` / `portfolio-audit`. The duplicate-capability severity is `Warning` irrespective of whether the target is a new or revised skill; the new-vs-revision context is recorded in the plan's `## Scope`, not encoded in severity

### Checks derived from the multilingual-template default

- **MUST** confirm that frontmatter and system-prompt content are in English, regardless of the conversation language in which the skill was authored; any non-English frontmatter or body content is a `Critical` (the user-facing response language is a runtime choice documented inside the body and isn't covered by this rule)

### Checks derived from external skill-structure validation

- **MUST** run an external skill-structure validator that checks `SKILL.md` frontmatter, body shape, and referenced-asset reachability before emitting the plan; Anthropic's `skills-ref` CLI is the canonical example, but the requirement isn't bound to a specific binary
- **MUST** map any error reported by the validator to a `Critical` finding and any warning to a `Warning` finding, citing the validator's rule identifier in the bracketed prefix per `review-plan`
- **MUST** record in the plan's `## Scope` section which validator and which version was used, so a later re-review can detect validator drift the same way it detects spec drift; the validator and its version are provisioned by repository tooling (for this repo, the Taskfile `validate:skills` target as the `skills-ref` stop-gap) and recorded per-review in `## Scope`, and this spec deliberately pins no specific binary or version
- **MUST NOT** skip this check on the grounds that other checks in this spec already cover overlapping ground; the external validator runs in addition to the spec-derived checks because it catches structural issues a spec-reading reviewer can miss
- **MAY** suppress an individual validator finding only by recording an explicit override in the plan's `## Scope` with a one-line justification anchored in another spec or a documented project decision

### Checks derived from skill-creation best practices

Mirrors the authoring requirements added to `skill-management` §"Authoring quality" (per <https://agentskills.io/skill-creation/best-practices> and <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices>); cite the upstream rule slug when a finding pins one.

- **MUST** verify `SKILL.md` is under 500 lines and 5,000 tokens; over-cap is a `Critical`
- **MUST** verify every asset referenced under `references/` / `templates/` / `assets/` / `scripts/` carries a load-trigger phrase in `SKILL.md` ("Read X when Y," "use template Z for output Q"); un-triggered references are a `Warning`
- **SHOULD** check for a **Gotchas** section when the skill operates against a non-obvious environment; absence is a `Warning` only when the skill clearly addresses such an environment, otherwise a `Suggestion`
- **SHOULD** flag menu-without-default phrasing (multiple equal-weight options without one designated default) and one-shot declarations where reusable procedures fit; both are `Suggestion`s

### Checks derived from frontmatter validation (Anthropic platform limits)

Mirrors `skill-management` §"Frontmatter validation"; cite the originating rule when a finding pins one.

- **MUST** verify `name` is 1–64 characters, lowercase ASCII letters/digits/hyphens only, doesn't start or end with `-`, and contains no `--`; any violation is a `Critical`
- **MUST** verify neither `name` nor any other frontmatter value contains the reserved tokens `anthropic` or `claude`; a violation is a `Critical` (the upstream platform validator rejects the skill)
- **MUST** verify neither `name` nor `description` contains XML tags; a violation is a `Critical`
- **MUST** verify `description` is non-empty and ≤1024 characters; over-cap or empty is a `Critical`
- **MUST** verify `description` is written in **third person**: presence of the pronouns "I," "you," or "we" (or other non-third-person markers) in the description text is a `Critical`. Citation: `skill-management` §Frontmatter validation, derived from the upstream platform best practices ([R5](#references))
- **MUST** verify `description` names both *what the skill does* and *when to use it*; absence of trigger phrases is a `Warning` (skill becomes hard to discover)
- **SHOULD**, when `when_to_use` is set, verify combined `description` + `when_to_use` text stays under 1,536 characters; over-cap is a `Warning` (runtime truncates and typically eats the trigger phrases)
- **SHOULD** verify the skill name follows a consistent form across this plugin (gerund preferred; verb-noun acceptable; mixed forms within one repository are a `Suggestion`-grade smell)
- **MUST** flag generic names (`helper`, `utils`, `tools`, `documents`, `data`, `files`) as `Critical`s; they defeat skill discovery

### Checks derived from progressive disclosure & file references

Mirrors `skill-management` §"Progressive disclosure & file references"; cite the originating rule when a finding pins one.

- **MUST** verify file references inside `SKILL.md` are at most one level deep (no `SKILL.md` → `A.md` → `B.md` chains); a chain is a `Warning` (Claude tends to partial-read nested references)
- **MUST** verify every supporting file longer than 100 lines opens with a table of contents; absence is a `Warning`
- **MUST** verify every script reference makes execution intent explicit ("Run X to …" vs. "See X for the algorithm of …"); ambiguous wording is a `Warning`
- **MUST** verify every path in `SKILL.md` and supporting files uses forward slashes; backslash paths are a `Critical` on Unix
- **MUST** verify every MCP-tool reference uses the fully qualified `ServerName:tool_name` form; bare tool names are a `Warning`
- **MUST** flag time-sensitive information not enclosed in an `## Old patterns` section; "use the new API after August 2025" inline is a `Warning`

### Checks derived from runtime & lifecycle

Mirrors `skill-management` §"Runtime & lifecycle awareness"; cite the originating rule when a finding pins one.

- **MUST** verify the skill body holds up as **standing instructions for the rest of the session**; one-time-step phrasing ("now do X," "as a first step …") that would lose its meaning after compaction is a `Warning`. Citation: skill content stays in context across turns and isn't re-read ([R4](#references))
- **SHOULD** estimate the token-count of `SKILL.md` (rough: 4 chars per token) and flag a `Suggestion` if the skill body exceeds 5,000 tokens since automatic compaction will silently truncate everything beyond that mark on re-attach ([R4](#references))
- **SHOULD** verify `allowed-tools`, when present, expresses a deliberate pre-approval contract documented in the body (so a future maintainer understands what the skill granted itself); silent `allowed-tools` declarations are a `Suggestion`
- **SHOULD** verify `disable-model-invocation: true` skills aren't also referenced by any subagent's `skills:` preload list (they would be silently skipped at runtime with only a debug-log warning) ([R4](#references))

### Checks derived from evaluation discipline

Mirrors `skill-management` §"Evaluation discipline"; cite the originating rule when a finding pins one.

- **SHOULD** verify the skill has at least three evaluation scenarios (input prompt, optional input files, expected behavior) under `examples/` or a sibling folder; absence is a `Suggestion` for new skills, a `Warning` for skills that have been edited more than three times since the last evaluation ([R3](#references))
- **MAY** record an `Info` finding when no evidence of multi-model testing exists (no comment, no example output, no test rubric mentioning Haiku / Sonnet / Opus) ([R3](#references))

### Checks derived from spec-driven-development

- **MUST** run a spec-anchor check: verify the SKILL.md body contains at least one reference to a `spec/...` path. A skill without any spec citation is a `Critical` finding per `spec/project/spec-driven-development/` MUST
- **MAY** suppress this check with a documented exception in the plan's `## Scope` section when a skill is explicitly classified as "implementation-only" (for example, `dependency-audit`, `quality-gate`); but the suppression itself must be anchored in a spec or a recorded project decision
- Rationale: this check operationalises the MUST from spec-driven-development that has so far been operator-only

### Review procedure

- **MUST** begin by reading the canonical `skill-management`, `skill-vs-agent`, and `review-plan` specs before producing any finding; findings without an anchor in one of those specs aren't valid output of this procedure
- **MUST** produce findings in this order: external-validator findings → frontmatter → description/triggers → system-prompt body → rationale section → referenced assets → duplicate-prevention check → best-practices checks → INFO observations
- **MUST** emit exactly one `review-plan` file at `.audits/skill-review/<skill-name>.md`; the reviewer **MUST** follow every lifecycle rule from `review-plan`, including the single-plan-per-target invariant and the deletion-commit message format
- **SHOULD** embed, in the plan's `## Scope` section, the git SHA of the spec versions applied so a later re-review can tell whether findings may have become outdated by a spec revision
- **MAY** fold purely stylistic observations (Vale, markdown linting) into `Info` findings when they aid the author, but **MUST NOT** promote them to `Warning` or `Critical`: those stay with their own tooling

This procedure is delivered as a skill (`skills/skill-review/`), per `skill-vs-agent`'s orchestrator-is-a-skill rule; the plan persists to `.audits/skill-review/` regardless of entry point per `review-plan`.

### Relationship to other specs

- **MUST** reference `review-plan` for the output format; don't restate its requirements here
- **MUST NOT** re-specify anything already covered by `skill-management` or `skill-vs-agent`; when this spec and one of those diverge, the authoring spec wins and this spec is the one that needs updating
- **SHOULD**, when the skill under review dispatches an agent, trigger a companion `agent-review` for that agent only if the agent hasn't been reviewed against its current source revision—record the decision in the plan's `## Scope` so downstream actors know whether the dispatched agent has been covered

## Acceptance Criteria
<!-- Testable, checkable conditions. A reviewer should be able to mark each as done/not done. -->
- [ ] A worked example exists applying this review procedure to one skill in `nolte-shared` (for instance `audience-identify`) and producing a conforming plan under `.audits/skill-review/`
- [ ] Every skill in `skills/` has been reviewed against the current `skill-management` revision at least once since this spec was adopted, verifiable by either an open plan under `.audits/skill-review/` or a closing commit in `git log` matching the `review-plan` deletion pattern
- [ ] No skill in `skills/` lacks a rationale section; running the rationale-section check across all skills produces zero `Critical`s
- [ ] No two skills in `skills/` share an equivalent capability statement, verified by a spot-check of every plan's duplicate-prevention finding
- [ ] Every open plan under `.audits/skill-review/` conforms to `review-plan`'s four-section structure and YAML frontmatter
- [ ] The `skill-management` spec's acceptance criteria cross-reference this spec for the review side of its authoring rules
- [ ] A spot-check of three closed plan deletions in `git log` shows the commit message format `review(skill-review): close <skill>—<counts>` exactly
- [ ] Every plan under `.audits/skill-review/` records the external skill-structure validator and version that was run, and no plan closes with an unresolved validator-reported `Critical`
- [ ] Every plan under `.audits/skill-review/` runs the best-practices checks from §"Checks derived from skill-creation best practices" against the target skill
- [ ] Every plan under `.audits/skill-review/` runs the frontmatter-validation, progressive-disclosure, runtime-lifecycle, and evaluation-discipline checks newly added to this spec, citing `skill-management` §<section> as the rule anchor

## References

Sources for the additional checks above. Cite the relevant entry in finding bracketed prefixes when a check pins a specific upstream rule.

- [R1] Skill management spec (this plugin): `spec/claude/skill-management/`
- [R2] Skill vs. agent decision (this plugin): `spec/claude/skill-vs-agent/`
- [R3] Skill authoring best practices, Anthropic platform docs: <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices>
- [R4] Extend Claude with skills, Claude Code docs: <https://code.claude.com/docs/en/skills>
- [R5] Best practices for skill creators, agentskills.io: <https://agentskills.io/skill-creation/best-practices>
- [R6] Agent Skills, formal specification: <https://agentskills.io/specification>

## Open Questions
<!-- Unresolved decisions, known unknowns, things that need a stakeholder answer. -->
- Should reviewing a skill also verify that the skill's `description` triggers don't overlap with a runtime slash command or a Claude Code built-in command, and if so against which authoritative list? Unblock when EITHER (a) the Claude Code harness exposes a queryable, versioned built-in-/reserved-command list this repo can pin and grep against (watch the slash-commands surface in Claude Code docs, <https://code.claude.com/docs/en/slash-commands>)—the §Goals reproducibility bar ("identical results on the same source tree") can't be met against an unpinned, evolving list; OR (b) `skill-vs-agent` §Open Questions resolves slash commands as a first-class artifact class, at which point this spec inherits a defined command namespace to check description-trigger overlap against. Neither has occurred: #228 resolved 178 questions but explicitly left the `skill-vs-agent` third-artifact-class question open, and no reserved-command catalog exists in `spec/`, `scripts/`, or `.claude-plugin/`.
