---
name: skill-review
description: Review a Claude Code skill against spec/claude/skill-management/ and spec/claude/skill-vs-agent/, and emit an actionable review plan per spec/claude/review-plan/ under .audits/skill-review/ keyed by the target skill's name. Invoke when the user asks "review this skill", "audit a specific skill folder", "check whether this skill is spec-compliant", or "skill review for a specific skill". Also handles closing an existing review plan once every item is addressed — "close the skill review plan for a specific skill". Also handles equivalent German-language requests. Do NOT use for agent review (use `agent-review`) or for pull-request-level review (`review` skill). Supports resume on re-invocation per `spec/claude/resumable-work/`.
tags: [review]
phase: review
summary: "Reviews a Claude Code skill against the spec and emits an actionable review plan under .audits/skill-review/."
summary_de: "Prüft einen Claude-Code-Skill gegen die Spec und erzeugt einen umsetzbaren Review-Plan unter .audits/skill-review/."
use_when:
  - "you want to review a specific skill folder for spec compliance"
  - "you want an actionable review plan for a skill"
  - "you want to close an existing skill-review plan once every item is addressed"
dont_use_when:
  - situation: "You want to review an agent file rather than a skill"
    alternative: agent-review
see_also:
  - agent-review
  - skill-management
resumable: true
---

# Skill Review Skill

Operationalizes `spec/claude/skill-review/` — reviews one Claude Code skill against its authoring specs and persists the result as a processable plan under `.audits/skill-review/`. The plan is the deliverable; the skill is the procedure that produces and, later, retires it.

## German trigger phrases

This skill also triggers on equivalent German-language requests, including:

- "prüfe diesen Skill"
- "Skill-Review für X"
- "Audit von skills/"
- "ist dieser Skill spec-konform"
- "schließe den Skill-Review-Plan"

## Why this is a skill, not an agent

- **Mid-flow interactivity** — scope confirmation (which skill, narrowed aspect?) and item-closure decisions happen with the user in the loop; an agent's fire-and-forget contract would lose that.
- **Persistent on-disk output is the contract** — the `review-plan` artifact under `.audits/` must survive past the current turn and be worked off incrementally; skills own persistent state, agents return structured reports.
- **Orchestrator of specs + (potentially) dispatches agents** — this skill may chain to `pull-request-create` in the same thread after the plan is closed; the skill-orchestrates-agent-executes pattern (see `skill-vs-agent`) defaults the orchestrator to skill form.
- Counter-dimension considered: *context-window impact* from reading three specs plus the target skill would bias toward an agent, but the read volume is bounded (each spec is one file, the target skill is one folder) and the user wants visibility into progress — inline reading wins.

## User-language policy

- Detect the user's language from their message and reply in that language.
- The **plan file** uses English section headings (`## Scope`, `## Summary`, `## Findings`, `## Processing log`) regardless of conversation language — this is a `review-plan` requirement so downstream tooling can grep deterministically.
- Finding prose (the one-line statement, `Where`, `Fix`, `Verify`) may follow the conversation language.
- Commit messages produced by this skill stay in English for portfolio consistency.

## Preconditions

Before any operation, verify with `Read` that these files exist in the current repository:

- `spec/claude/skill-management/<canonical>.md`
- `spec/claude/skill-vs-agent/<canonical>.md`
- `spec/claude/review-plan/<canonical>.md`
- `spec/claude/skill-review/<canonical>.md`

`<canonical>` comes from `spec/.spec-config.yml` (`canonical_language`); fall back to `en` if the config is absent. If any of the four is missing, stop and tell the user — the specs are the input; without them there is nothing to review against. Do not improvise replacements, do not read a translation when the canonical file exists.

Also verify `.audits/` exists and is tracked by git (`git ls-files .audits/.gitkeep` or an existing plan). If absent, create `.audits/skill-review/.gitkeep` as part of the first plan write so the folder is not lost.

## Operations

### 1. `run <skill-name>` — produce a review plan

Interactive. Confirm each decision with the user before acting on it.

1. **Resolve the target.** Accept `skills/<name>/` or a runtime path `.claude/skills/<name>/`. If the user gave only a name without a path prefix, default to `skills/<name>/`. If multiple candidates match (rare), list them back and ask.
2. **Check for an existing plan** at `.audits/skill-review/<name>.md`. If present:
   - If its `status` is `open` or `in-progress`, tell the user a live plan exists and ask: resume it, supersede it (overwrite), or abort. Do not silently overwrite.
   - If its `status` is `complete`, tell the user and ask whether to rerun (which will overwrite — per `review-plan` one-plan-per-target invariant).
3. **Narrow scope if the user asks.** The user may request "frontmatter only", "rationale only", etc. Record the narrowing verbatim — it goes into the plan's `## Scope`.
4. **Read the review surface** in this order: `SKILL.md` (frontmatter + body), every file referenced by relative path from `SKILL.md`, sibling `agents/<name>.md` the skill dispatches to (if any). Stop if a referenced file is missing — that is already a finding to record, but note the broken reference before walking further.
5. **Run the external skill-structure validator** over `skills/<name>/SKILL.md`. The canonical example is Anthropic's `skills-ref` CLI, but the requirement isn't bound to a specific binary — accept any validator that checks frontmatter, body shape, and referenced-asset reachability. Capture the validator's name, version, and the full set of reported errors and warnings; map errors to `Critical` and warnings to `Warning` per `skill-review` §Checks derived from external skill-structure validation, citing each rule identifier in the bracketed prefix. If the validator isn't provisioned in the current repository, record an explicit override in the plan's `## Scope` with a one-line justification anchored in another spec or a documented project decision rather than silently skipping the check.
6. **Apply the checks from `spec/claude/skill-review/`**, in the spec's declared order: external-validator findings → frontmatter → description/triggers → system-prompt body → rationale section → referenced assets → duplicate-prevention check → best-practices checks → spec-anchor check → Info observations. The **spec-anchor check** (per `skill-review` §"Checks derived from spec-driven-development") verifies the `SKILL.md` body cites at least one `spec/...` path; a skill with no spec citation is a `Critical` per `spec/project/spec-driven-development/`.
   - For the duplicate check, `Grep` the `description:` line of every other `skills/*/SKILL.md` and `agents/*.md` for semantic overlap with the target — keyword hits are candidates, not verdicts; read each candidate and judge. The best-practices checks come from `skill-review` §"Checks derived from skill-creation best practices" and verify the 500-line / 5,000-token cap, load-trigger phrases for referenced assets, the optional Gotchas section, and the defaults-not-menus / procedures-over-declarations style.
7. **Map severities.** MUST failure → `Critical`, SHOULD failure → `Warning`, applicable MAY → `Suggestion`, observation without a rule → `Info`. The severity vocabulary itself is fixed by `spec/claude/review-plan/` §Severity scale — Title Case, no abbreviations, no portfolio-local extensions. External-validator findings carry their own mapping (error → `Critical`, warning → `Warning`) per `skill-review` §Checks derived from external skill-structure validation. Do not promote Vale/markdown-style observations above `Info` — they stay with their own tooling.
8. **Draft the plan** from `templates/plan.template.md`, filling every field. The frontmatter `repo-revision` is `git rev-parse HEAD` (or `unknown` if the repo is clean but detached / untracked). `created` is today's ISO date. In `## Scope`, populate the `Validator:` line with the name and version captured in step 5; if step 5 recorded an override instead, write `Validator: override — <justification>` in place of the version.
9. **Write the plan** to `.audits/skill-review/<name>.md`. Confirm the path back to the user. Do **not** mark any item `- [x]` on creation — everything starts open.
10. **Stage and commit** the plan only if the user asks; otherwise leave it as a working-tree change so the user can review before committing.

### 2. `update <skill-name>` — check off processed items

When the user reports "I fixed items 3 and 5":

1. **Read** `.audits/skill-review/<name>.md`.
2. **Verify** each claimed closure by re-running the specific check that produced the finding — do not take the user's word alone when verification is cheap (re-read the file, re-grep). If verification fails, leave the item `- [ ]` and say so.
3. **Mark verified items** `- [x]` in place.
4. **Append one line to `## Processing log`** per closure, in the form `YYYY-MM-DD — <item-shorthand> — <action> — verified: <method>`.
5. **Flip `status`** to `in-progress` on the first closure, if it was `open`.
6. **Do not commit automatically** — show the diff and let the user commit.

### 3. `close <skill-name>` — delete the plan after full processing

1. **Read** `.audits/skill-review/<name>.md`.
2. **Refuse if any open `- [ ]` `Critical` remains.** `Warning` / `Suggestion` / `Info` items may be closed via `→ deferred: <issue-url>` annotation on the item, per `review-plan`. Offer to help the user open the tracking issues if they are missing.
3. **Count findings at creation time** per severity (re-read the `## Summary` counts, not the current state — the commit message records the original review scale, not what is still open now).
4. **Delete the plan file.**
5. **Compose the deletion commit message** exactly: `review(skill-review): close <skill-name>—<C>C/<W>W/<S>S/<I>I` in the subject, and in the body list any deferred-issue URLs the plan referenced plus the `repo-revision` the review was taken at. Do not bypass hooks; do not skip signing.
6. **Run the commit only if the user confirms.** Show the message first.

## Output — plan shape

Reference `spec/claude/review-plan/<canonical>.md` for the authoritative format. Never restate its rules in the plan itself. The template at `templates/plan.template.md` is the starting point. Every finding uses the four-line structure (statement + `Where` / `Fix` / `Verify`) and cites a spec requirement in the bracketed prefix — inventions without a citation are rejected at draft time.

See `examples/walkthrough.md` for an end-to-end transcript covering the create, update, defer, and close turns.

## Examples

- Read `examples/01-fresh-review.md` when running a first-time review that scaffolds the plan and runs the skill-structure validator.
- Read `examples/02-update-after-fix.md` when marking review-plan items off after fixes land on develop.
- Read `examples/03-close-plan.md` when every plan item is addressed and the plan is closed with a deletion commit.

## Gotchas

- **`skills-ref` validator is not provisioned in most repos**: the external skill-structure validator (step 5) may not be installed; when it's absent, record an explicit override in the plan's `## Scope` with a one-line justification rather than silently skipping the check — an undocumented skip is itself a `Warning` finding per `skill-review` §Checks derived from external skill-structure validation.
- **`spec/.spec-config.yml` must be read before resolving any spec path**: `<canonical>` for the four required spec files depends on `canonical_language` in that config; defaulting to `en` without reading the config silently misroutes reviews in repos with a different canonical language.
- **Plan file is local-only until committed**: `.audits/skill-review/<name>.md` exists only in the working tree until the user commits it; if the session ends before the user stages and commits, the plan is lost — remind the user to commit early or offer to stage immediately after writing.

## Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/skill-review/<run-id>.yml` after every successful user-approval gate and after each named phase boundary. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope (`schema_version`, `run_id`, `inputs`, `phase`, `decisions[]`, `status`, ...) and the fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

## Hard rules

- **One plan per target.** A rerun supersedes; never edit a previous run's plan into a new one.
- **No finding without a spec citation.** If an issue is real but no `skill-management` / `skill-vs-agent` rule covers it, record it as `Info` with a note that the spec itself may need to grow — never promote an opinion to `Warning` or `Critical`.
- **Never delete a plan with an open Critical.** `Warning` / `Suggestion` / `Info` may be deferred to tracked issues; `Critical` must land or be downgraded (which requires a spec change, not a reviewer's choice).
- **No invention in frontmatter.** Unknown git SHA → `unknown`. Missing reference → the finding describes the gap; do not paper over it.
- **English section headings, English commit messages.** Prose inside findings may follow the user's language; the structural contract with downstream tooling stays English-only.
- **No cross-target batching.** One skill per plan, one plan per run. If the user asks for "review all skills", loop and emit one plan each; do not merge.
- **This skill reviews the skill artifact, not its live behavior.** Do not run the skill under review to see what it does — that is out of scope and risks side effects.
