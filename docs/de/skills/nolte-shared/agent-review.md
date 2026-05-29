---
title: agent-review
audience: [maintainer]
content_mode: reference
track: developer-docs
last_updated: generated
---

# agent-review

> Prüft einen Claude-Code-Agent gegen die Spec und erzeugt einen umsetzbaren Review-Plan unter .audits/agent-review/.

_Review a Claude Code agent against spec/claude/agent-management/ and spec/claude/skill-vs-agent/, and emit an actionable review plan per spec/claude/review-plan/ under .audits/agent-review/ keyed by the target agent's name. Invoke when the user asks "review this agent", "audit a specific agent file", "check whether this agent is spec-compliant", or "agent review for a specific agent". Also handles closing an existing review plan once every item is addressed — "close the agent review plan for a specific agent". Also handles equivalent German-language requests. Do NOT use for skill review (use skill-review) or for pull-request-level review (`review` skill). Supports resume on re-invocation per `spec/claude/resumable-work/`._

- **Plugin:** `nolte-shared`
- **Phase:** 5 Review (`review`)
- **Tags:** `review`
- **Quelle:** [skills/agent-review/SKILL.md](https://github.com/nolte/claude-shared/blob/main/skills/agent-review/SKILL.md)

## Anwenden wenn

- you want to review a specific agent file for spec compliance
- you want an actionable review plan for an agent
- you want to close an existing agent-review plan once every item is addressed

## Nicht anwenden wenn

- **You want to review a skill (SKILL.md), not an agent** → [`skill-review`](skill-review.md)

## Siehe auch

- [`skill-review`](skill-review.md)

---

## Agent Review Skill

Operationalizes `spec/claude/agent-review/` — reviews one Claude Code agent against its authoring specs and persists the result as a processable plan under `.audits/agent-review/`. The plan is the deliverable; the skill is the procedure that produces and, later, retires it.

### German trigger phrases

This skill also triggers on equivalent German-language requests, including:

- "prüfe diesen Agent"
- "Agent-Review für X"
- "Audit von agents/"
- "ist dieser Agent spec-konform"
- "schließe den Agent-Review-Plan"

### Why this is a skill, not an agent

- **Mid-flow interactivity** — scope confirmation (which agent, narrowed aspect?) and item-closure decisions happen with the user in the loop; an agent's fire-and-forget contract would lose that.
- **Persistent on-disk output is the contract** — the `review-plan` artifact under `.audits/` must survive past the current turn and be worked off incrementally; skills own persistent state, agents return structured reports.
- **Orchestrator, potentially chains to other skills** — after the plan is closed, the user may run [`pull-request-create`](pull-request-create.md) in the same thread; the skill-orchestrates pattern (see `skill-vs-agent`) defaults the orchestrator to skill form.
- Counter-dimension considered: *context-window impact* from reading three specs plus the target agent would bias toward an agent, but an agent file is a single markdown and each spec is one file — the read volume is bounded and the user wants visibility.
- This skill is the sibling of [`skill-review`](skill-review.md); the two share the `review-plan` output shape and differ only in which authoring spec drives the checks.

### User-language policy

- Detect the user's language from their message and reply in that language.
- The **plan file** uses English section headings (`## Scope`, `## Summary`, `## Findings`, `## Processing log`) regardless of conversation language — `review-plan` requirement so downstream tooling can grep deterministically.
- Finding prose (the one-line statement, `Where`, `Fix`, `Verify`) may follow the conversation language.
- Commit messages produced by this skill stay in English for portfolio consistency.

### Preconditions

Before any operation, verify with `Read` that these files exist in the current repository:

- `spec/claude/agent-management/<canonical>.md`
- `spec/claude/skill-vs-agent/<canonical>.md`
- `spec/claude/review-plan/<canonical>.md`
- `spec/claude/agent-review/<canonical>.md`

`<canonical>` comes from `spec/.spec-config.yml` (`canonical_language`); fall back to `en` if the config is absent. If any of the four is missing, stop and tell the user — the specs are the input; without them there is nothing to review against. Do not improvise replacements, do not read a translation when the canonical file exists.

Also verify `.audits/` exists and is tracked by git. If absent, create `.audits/agent-review/.gitkeep` as part of the first plan write so the folder is not lost.

### Operations

#### 1. `run <agent-name>` — produce a review plan

Interactive. Confirm each decision with the user before acting on it.

1. **Resolve the target.** Accept `agents/<name>.md` or a runtime path `.claude/agents/<name>.md` / `~/.claude/agents/<name>.md`. If the user gave only a name without a path prefix, default to `agents/<name>.md`. If multiple candidates match, list them back and ask.
2. **Check for an existing plan** at `.audits/agent-review/<name>.md`. If present:
   - If `status` is `open` or `in-progress`, tell the user a live plan exists and ask: resume it, supersede it (overwrite), or abort. Do not silently overwrite.
   - If `status` is `complete`, ask whether to rerun (overwrite — per `review-plan` one-plan-per-target invariant).
3. **Narrow scope if the user asks** ("frontmatter only", "tools only", "rationale only"). Record the narrowing verbatim — it goes into the plan's `## Scope`.
4. **Read the review surface** in this order: YAML frontmatter → markdown body (role, output format, procedure, rationale) → any external supporting asset referenced from the body. Agents are single self-contained files: per `agent-management` §Structure there is no `agents/<name>/` sibling folder, and a nested companion markdown file is itself a finding (recursive discovery registers it as a phantom agent). A missing referenced file is a finding, not a stop.
5. **Apply the checks from `spec/claude/agent-review/`**, in the spec's declared order:
   1. Frontmatter fields: `name` matches filename, `description` names concrete triggers, `distribution` is exactly `plugin` or `project`.
   2. `tools` scoping: declared-vs-used bidirectional check (declared-unused → `Warning`, used-undeclared → `Critical`), read-only-agent invariant (if the `description` verbs are review / audit / research / lint / report, `tools` must NOT contain `Edit`, `Write`, `Bash`, or `NotebookEdit` → otherwise `Critical`).
   3. System-prompt body: single responsibility, output shape stated, no hard-coded absolute paths, English-only frontmatter and body.
   4. No-Skill-dispatch check: `Grep` the body for `Skill(`, `Skill tool`, or equivalent phrasings → any match is a `Critical` per `skill-vs-agent`.
   5. Rationale section: at least one decisive dimension named → absence is `Critical`; at least one counter-dimension named → absence is `Suggestion`.
   6. Referenced assets exist.
   7. Duplicate-prevention: `Grep` the `description:` line of every other `agents/*.md` and `skills/*/SKILL.md` for semantic overlap with the target — keyword hits are candidates, not verdicts; read each candidate and judge.
   8. Info observations for body-length or asset-factoring opportunities.
6. **Map severities.** MUST failure → `Critical`, SHOULD failure → `Warning`, applicable MAY → `Suggestion`, observation without a rule → `Info`. The severity vocabulary itself is fixed by `spec/claude/review-plan/` §Severity scale — Title Case, no abbreviations, no portfolio-local extensions. Never promote Vale / markdown-style observations above `Info`.
7. **Draft the plan** from `templates/plan.template.md`, filling every field. `repo-revision` is `git rev-parse HEAD` (or `unknown`). `created` is today's ISO date.
8. **Write the plan** to `.audits/agent-review/<name>.md`. Confirm the path back to the user. Do not mark any item `- [x]` on creation.
9. **Stage and commit** only if the user asks; otherwise leave as a working-tree change.

#### 2. `update <agent-name>` — check off processed items

When the user reports closures:

1. **Read** `.audits/agent-review/<name>.md`.
2. **Verify** each claimed closure by re-running the specific check (re-read the file, re-grep, re-inspect `tools` list). If verification fails, leave the item `- [ ]` and say so.
3. **Mark verified items** `- [x]` in place.
4. **Append one line to `## Processing log`** per closure: `YYYY-MM-DD — <item-shorthand> — <action> — verified: <method>`.
5. **Flip `status`** to `in-progress` on the first closure if it was `open`.
6. **Do not commit automatically** — show the diff and let the user commit.

#### 3. `close <agent-name>` — delete the plan after full processing

1. **Read** `.audits/agent-review/<name>.md`.
2. **Refuse if any open `- [ ]` `Critical` remains.** `Warning` / `Suggestion` / `Info` may be closed via `→ deferred: <issue-url>`. Offer to help open tracking issues if missing.
3. **Count findings at creation time** per severity (from `## Summary`, not current state).
4. **Delete the plan file.**
5. **Compose the deletion commit message** exactly: `review(agent-review): close <agent-name>—<C>C/<W>W/<S>S/<I>I` in the subject; body lists deferred-issue URLs and the `repo-revision`. No hook bypass, no signing skip.
6. **Run the commit only if the user confirms.** Show the message first.

### Output — plan shape

Reference `spec/claude/review-plan/<canonical>.md` for the authoritative format. Never restate its rules in the plan itself. The template at `templates/plan.template.md` is the starting point. Every finding uses the four-line structure (statement + `Where` / `Fix` / `Verify`) and cites a spec requirement in the bracketed prefix.

### Examples

- Read `examples/01-fresh-review.md` when running the first end-to-end `run` on a new agent target.
- Read `examples/02-update-after-fix.md` when closing individual findings after the author has pushed fixes.
- Read `examples/03-close-plan.md` when all items are resolved and you are ready to delete the plan.

### Gotchas

- **Plan file is local-only until committed**: the `.audits/agent-review/<name>.md` plan survives only in the working tree until the user explicitly commits it; if the session ends or the branch is switched before committing, the plan is silently lost — stage and commit early or remind the user.
- **Declared-vs-used check requires the current file version**: the bidirectional tools check (declared-unused → `Warning`, used-undeclared → `Critical`) must be run against the on-disk agent file at review time; stale cached reads produce false positives or missed `Critical` findings — always re-read the agent file immediately before running step 5.2.
- **`spec/.spec-config.yml` must be read first**: `<canonical>` depends on `canonical_language` in that file; skipping the read and defaulting to `en` silently misroutes reviews in repos where the canonical language differs — read the config before resolving any spec path.

### Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/agent-review/<run-id>.yml` after every successful user-approval gate and after each named phase boundary. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope (`schema_version`, `run_id`, `inputs`, `phase`, `decisions[]`, `status`, ...) and the fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

### Hard rules

- **One plan per target.** A rerun supersedes; never edit a previous run's plan into a new one.
- **No finding without a spec citation.** Real issues that no `agent-management` / `skill-vs-agent` rule covers are recorded as `Info` with a note that the spec may need to grow — never promoted to `Warning` / `Critical`.
- **Never delete a plan with an open Critical.** `Warning` / `Suggestion` / `Info` may be deferred; `Critical` must land or be downgraded (which requires a spec change, not a reviewer's choice).
- **No invention in frontmatter.** Unknown git SHA → `unknown`. Missing reference → the finding describes the gap.
- **English section headings, English commit messages.** Prose inside findings may follow the user's language; the structural contract stays English-only.
- **No cross-target batching.** One agent per plan, one plan per run. For "review all agents", loop and emit one plan each.
- **This skill reviews the agent artifact, not its live behavior.** Do not dispatch the agent under review to see what it does — out of scope and risks side effects.
- **Tool-scope check is bidirectional and strict.** Declared-but-unused is a `Warning`; used-but-undeclared is a `Critical` (the agent will fail to run). Do not soften either side.
