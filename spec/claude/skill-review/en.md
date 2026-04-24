# Claude Skill Review

Status: draft

## Context
<!-- Why does this spec exist? What problem, user need, or constraint drives it? -->

The `skill-management` spec defines how a skill is *authored* — on-disk shape, frontmatter, templates, distribution form. What it does not define is how a skill is *reviewed*: which requirements a reviewer checks, in which order, and what deliverable the review leaves behind. Without a shared review procedure, two reviewers of the same skill produce incomparable results, the `skill-vs-agent` rationale-documentation rule slips silently, and plugin developers consuming the review output have to reverse-engineer each reviewer's private shape. This spec defines the binding review procedure for skills in the `nolte-shared` plugin, points at `skill-management` and `skill-vs-agent` as the sources of truth for what counts as a finding, and hands the output-format contract to `review-plan`. A skill review produces exactly one `review-plan` artifact under `.audits/skill-review/<skill-name>.md`; once every item is processed the plan is deleted, leaving its git history as the audit trail.

## Goals
<!-- What this spec aims to achieve. Bullet points, outcome-oriented. -->
- Every skill review applies the same set of checks derived from `skill-management` and `skill-vs-agent`, in the same order, with the same severity mapping
- Review output is a `review-plan` artifact — parseable, actionable, and traceable back to a specific spec requirement per finding
- Skill authors can run the review on their own work before proposing it, and a reviewer (human or LLM) can run it later with identical results on the same source tree
- Plugin developers can script against the review output (parse plan files, gate merges on open `BLOCKER`s, count open reviews) without having to model per-reviewer conventions
- The review distinguishes **authoring-spec compliance** (`skill-management` rules) from **decision-rule compliance** (`skill-vs-agent` rationale) without conflating the two into a single pass/fail

## Non-Goals
<!-- Explicitly out of scope. Prevents creep. -->
- Defining what a skill *is* on disk — `skill-management` owns that
- Deciding whether a capability should have been a skill or an agent in the first place — `skill-vs-agent` owns that; this spec only checks that the choice has been *documented*
- Prescribing the output file format — `review-plan` owns that
- Reviewing agents — `agent-review` covers that with symmetric structure
- Replacing quarterly portfolio-wide reconciliation — `spec-drift-audit` owns that
- Linter and markdown-style checks already enforced by `task lint` / Vale / pre-commit hooks — those stay with their own tooling
- Runtime or behavioral correctness of the skill (whether the skill actually does what its description promises when invoked) — this spec reviews the **authored artifact**, not a live execution

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
  - A failed MUST → `BLOCKER`
  - A failed SHOULD → `WARNING`
  - A failed MAY that the skill clearly would benefit from → `SUGGESTION`
  - An observation that no rule covers but that a future reviewer would want to know → `INFO`
- **MUST** explicitly cover these high-impact areas even when the corresponding rule in `skill-management` is expressed only as a SHOULD: frontmatter field presence (`name`, `description`), description-contains-concrete-triggers, absence of hard-coded absolute paths in referenced assets, existence of every template the skill references
- **SHOULD** flag as `INFO` any part of the skill body that could be factored into a sibling file to keep the main prompt under the soft length target named in `skill-management`

### Checks derived from `skill-vs-agent`

- **MUST** confirm the skill body contains a **rationale section** that names at least one decisive dimension for the skill-over-agent choice; its absence is a `BLOCKER`
- **MUST** verify the skill does not dispatch the Skill tool on behalf of an agent (not applicable in this direction, but the reverse direction — a skill calling an agent via the Agent tool — is expected and is not a finding)
- **MUST** run a duplicate-capability check: grep every other `skills/*/SKILL.md` and `agents/*.md` `description` line for semantic overlap; any plausible overlap produces a `WARNING` naming the peer artifact and the overlap, so the author can propose a merge, rename, or clearer split before landing

### Checks derived from the multilingual-template default

- **MUST** confirm that frontmatter and system-prompt content are in English, regardless of the conversation language in which the skill was authored; any non-English frontmatter or body content is a `BLOCKER` (the user-facing response language is a runtime choice documented inside the body and is not covered by this rule)

### Review procedure

- **MUST** begin by reading the canonical `skill-management`, `skill-vs-agent`, and `review-plan` specs before producing any finding; findings without an anchor in one of those specs are not valid output of this procedure
- **MUST** produce findings in this order: frontmatter → description/triggers → system-prompt body → rationale section → referenced assets → duplicate-prevention check → INFO observations
- **MUST** emit exactly one `review-plan` file at `.audits/skill-review/<skill-name>.md`; the reviewer **MUST** follow every lifecycle rule from `review-plan`, including the single-plan-per-target invariant and the deletion-commit message format
- **SHOULD** embed, in the plan's `## Scope` section, the git SHA of the spec versions applied so a later re-review can tell whether findings may have become outdated by a spec revision
- **MAY** fold purely stylistic observations (Vale, markdown linting) into `INFO` findings when they aid the author, but **MUST NOT** promote them to `WARNING` or `BLOCKER` — those stay with their own tooling

### Relationship to other specs

- **MUST** reference `review-plan` for the output format; do not restate its requirements here
- **MUST NOT** re-specify anything already covered by `skill-management` or `skill-vs-agent`; when this spec and one of those diverge, the authoring spec wins and this spec is the one that needs updating
- **SHOULD**, when the skill under review dispatches an agent, trigger a companion `agent-review` for that agent only if the agent has not been reviewed against its current source revision — record the decision in the plan's `## Scope` so downstream actors know whether the dispatched agent has been covered

## Acceptance Criteria
<!-- Testable, checkable conditions. A reviewer should be able to mark each as done/not done. -->
- [ ] A worked example exists applying this review procedure to one skill in `nolte-shared` (for instance `audience-identify`) and producing a conforming plan under `.audits/skill-review/`
- [ ] Every skill in `skills/` has been reviewed against the current `skill-management` revision at least once since this spec was adopted, verifiable by either an open plan under `.audits/skill-review/` or a closing commit in `git log` matching the `review-plan` deletion pattern
- [ ] No skill in `skills/` lacks a rationale section; running the rationale-section check across all skills produces zero `BLOCKER`s
- [ ] No two skills in `skills/` share an equivalent capability statement, verified by a spot-check of every plan's duplicate-prevention finding
- [ ] Every open plan under `.audits/skill-review/` conforms to `review-plan`'s four-section structure and YAML frontmatter
- [ ] The `skill-management` spec's acceptance criteria cross-reference this spec for the review side of its authoring rules
- [ ] A spot-check of three closed plan deletions in `git log` shows the commit message format `review(skill-review): close <skill> — <counts>` exactly

## Open Questions
<!-- Unresolved decisions, known unknowns, things that need a stakeholder answer. -->
- Should the duplicate-prevention check read agent descriptions from `agents/*.md` in the same repository only, or should it also query the MkDocs-rendered catalog across installed plugins when a consumer reviews a downstream copy?
- Does the review distinguish "new skill being proposed" from "existing skill being revised"? The same requirements apply to both, but the severity of a duplicate-capability finding differs (blocker vs. warning) depending on whether the peer pre-exists or is being introduced alongside.
- Should the rationale-section check also validate that at least one *counter-dimension* is named, per `skill-vs-agent`'s SHOULD rule, or is the current "at least one decisive dimension" bar sufficient for skill review?
- When the skill under review depends on a template or asset file that does not yet exist, is the finding a `BLOCKER` (broken reference) or a `WARNING` (template to be added before merge)?
- How is this spec invoked — as a `review` skill run from the main conversation, as a sub-agent comparable to `audience-review`, or both? The output is the same plan either way, but the entry point affects whether the review persists automatically.
- Should reviewing a skill also verify that the skill's `description` triggers do not overlap with a runtime slash command or a Claude Code built-in command, and if so against which authoritative list?
