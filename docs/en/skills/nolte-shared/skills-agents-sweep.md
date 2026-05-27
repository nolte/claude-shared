---
title: skills-agents-sweep
audience: [maintainer]
content_mode: reference
track: developer-docs
last_updated: generated
---

# skills-agents-sweep

> Orchestrates a portfolio-wide sweep audit of all skills and agents with cross-cutting findings and a wave-based roadmap.

_Orchestrates a portfolio-wide audit of all skills and agents in the plugin inventory, producing a consolidated sweep report under .audits/skills-agents-sweep/ with cross-cutting findings (boundary conflicts, spec-induced gaps, operations-vocabulary drift, classification errors) and a wave-based implementation roadmap. Invoke when the user asks to "run a portfolio-wide skills and agents sweep audit", "check cross-cutting drift between skills and agents", "consolidate per-artefact reviews into a single sweep report", or "plan a wave-based implementation roadmap for sweep findings". Also handles equivalent German-language requests. Do NOT use for per-artefact reviews (use skill-review or agent-review for those); do NOT use for spec-versus-implementation reconciliation (use spec-drift-audit). Supports resume on re-invocation per `spec/claude/resumable-work/`._

- **Plugin:** `nolte-shared`
- **Phase:** 5 Review (`review`)
- **Tags:** `audit`
- **Source:** [skills/skills-agents-sweep/SKILL.md](https://github.com/nolte/claude-shared/blob/main/skills/skills-agents-sweep/SKILL.md)

## Use when

- you want to run a portfolio-wide skills-and-agents sweep audit
- you want to check cross-cutting drift between skills and agents
- you want a wave-based implementation roadmap for sweep findings

## Don't use when

- **You want a per-artefact review (single skill or agent)** → [`skill-review`](skill-review.md)
- **You want spec-versus-implementation reconciliation** → [`spec-drift-audit`](spec-drift-audit.md)

## See also

- [`skill-review`](skill-review.md)
- [`agent-review`](agent-review.md)
- [`spec-drift-audit`](spec-drift-audit.md)

---

## Skills and Agents Sweep Skill

Implements `spec/claude/skills-agents-sweep/` — the spec defines triggers, scope, phases, and lifecycle. This skill binds those rules to the on-disk procedure.

The sweep supplements per-artefact reviews with cross-cutting analysis that no single per-artefact review can surface: boundary conflicts between two skills only emerge when both are reviewed together, spec-induced gaps (phantom skills) are invisible to a review of existing artefacts, and operations-vocabulary drift accumulates across the inventory without any individual finding calling it out.

### Why this is a skill, not an agent

- **Mid-flow interactivity** — scope confirmation (full inventory vs. narrowed subset by phase or tag), wave-decision sign-offs (implement vs. defer vs. retire), and consolidated-report approval all require user input at multiple checkpoints. An agent's fire-and-forget contract loses that deliberation loop.
- **Persistent on-disk output is the contract** — the consolidated report under `.audits/skills-agents-sweep/` must survive past the current turn and be referenced by every downstream implementation PR as its evidence source. Skills own persistent artefacts; agents return ephemeral reports.
- **Orchestration role** — this skill dispatches [`skill-review`](skill-review.md) and [`agent-review`](agent-review.md) as sub-procedures for phase 1 and chains to [`pull-request-create`](pull-request-create.md) when waves are committed. The skill-orchestrates pattern defaults the orchestrator to skill form per `spec/claude/skill-vs-agent/`.
- Counter-dimension considered: *context-window load* from reading 30-plus skill files plus cross-cutting analysis could bias toward an agent. However, the sweep is inherently interactive — the user controls which artefacts are in scope, approves the consolidated report before phase 4 begins, and decides per-wave. The incremental, user-confirmed structure rules out fire-and-forget agent execution.

### German trigger phrases

This skill also triggers on equivalent German-language requests, including:

- "Portfolio-weiter Skills-und-Agents-Sweep durchführen"
- "Cross-Cutting-Drift zwischen Skills und Agents prüfen"
- "Per-Artefakt-Reviews zu einem Sweep-Report konsolidieren"
- "Wellenbasierte Umsetzungs-Roadmap für Sweep-Findings planen"
- "Sweep-Cycle abschließen"

### Preconditions

Before any operation, verify:

1. `spec/.spec-config.yml` is present — read it to determine `canonical_language` (fall back to `en`).
2. `spec/claude/skills-agents-sweep/<canonical_language>.md` is present — this is the governing spec; stop if missing.
3. `spec/claude/skill-review/<canonical_language>.md` and `spec/claude/agent-review/<canonical_language>.md` are present — the sweep dispatches these procedures; without them phase 1 cannot run.
4. `.audits/skills-agents-sweep/` exists or can be created. Check `git ls-files .audits/skills-agents-sweep/.gitkeep`; create `.gitkeep` if the folder is absent.
5. No other consolidated sweep report exists under `.audits/skills-agents-sweep/` with `status: open` — the spec requires exactly one open sweep at a time. If one is open, tell the user and offer to resume (`update`) or close it first.

### Operations

#### 1. `audit` — produce the consolidated sweep report

Interactive. Confirm scope with the user before proceeding.

1. **Determine scope.** Ask (or infer from message): full inventory sweep, or narrowed to a lifecycle phase or frontmatter tag? Record the scope; if narrowed, note which artefacts are excluded in the report's `## Scope` section.
2. **Record the repository revision.** Run `git rev-parse HEAD`; record as `repo-revision` in report frontmatter.
3. **Inventory the artefacts.** Walk `skills/<name>/SKILL.md` and `agents/<name>.md`; count each group. Record counts in frontmatter (`scope:`).
4. **Phase 1 — per-artefact reviews.** For each skill, invoke `skill-review run <name>` to produce a plan under `.audits/skill-review/<name>.md`. For each agent, invoke `agent-review run <name>` to produce a plan under `.audits/agent-review/<name>.md`. Record `per-artefact-plans` count in frontmatter. Per the governing spec, phase 2 should not begin until phase 1 plans exist — confirm with the user before proceeding to phase 2 if any plans are missing.
5. **Phase 2 — cross-cutting analysis.** Analyse these dimensions in order, drawing on the per-artefact plans from phase 1:
   - **Boundary matrix**: for every pair whose descriptions address overlapping trigger phrases, record overlap, propose resolution (merge / rename / bidirectional "Don't use for" clause), and classify as conflict, adjacent, or chain.
   - **Spec-induced gaps**: for every `spec/` path referenced in any skill or agent body that lacks a corresponding skill or agent, record the gap, the referencing artefacts, and a proposed resolution.
   - **Adoption friction**: setup friction (external tools not in `## Preconditions`), prerequisite chains, and discovery issues.
   - **Skill-vs-agent classification**: for every artefact, verify the rationale section justifies the chosen type using `spec/claude/skill-vs-agent/`; record mismatches.
   - **Operations-vocabulary consistency**: detect non-standard operation headings or verbs against the vocabulary defined in `spec/claude/skill-management/`.
   - **Naming consistency**: detect artefacts whose names deviate from the dominant convention in their lifecycle cluster.
6. **Classify each finding by wave**: mechanical sweep (automated or near-automated edit), spec extension (requires a spec change before implementation), or structural new artefact (requires authoring a new skill or agent). Distinguish release-blocking findings (failed MUST, Critical per `review-plan`) from deferrable findings (failed SHOULD, Warning or Suggestion).
7. **Phase 3 — draft the consolidated report.** Use `templates/sweep-report.template.md`. Fill every frontmatter field. Sections in order: YAML frontmatter, executive summary with top-findings table and go/no-go recommendation, artefact inventory table, boundary matrix, spec-induced gap inventory, adoption-friction analysis, skill-vs-agent classification findings, wave-based implementation roadmap, and processing log.
8. **Phase 3 — write the report.** Path: `.audits/skills-agents-sweep/<ISO-date>-<slug>.md`. Confirm the path with the user. Do not begin phase 4 before the report file exists on disk.
9. **Phase 4 — implementation planning.** Present the wave roadmap. For each wave, propose PRs sorted by effort times impact, making the ordering rationale explicit. Distinguish mechanical sweep PRs, spec-extension PRs, and structural new-artefact PRs. Express ordering constraints between waves.
10. **Stage and commit.** Offer to commit the report file only; do not commit implementation changes here.

Read `examples/01-baseline-sweep.md` when running a full-scope portfolio sweep for the first time.

#### 2. `update` — record wave decisions

When the user reports that a wave has been implemented, deferred (with a tracking issue), or retired:

1. **Read** `.audits/skills-agents-sweep/<slug>.md`.
2. **Verify** each claimed wave closure by checking the referenced PR URL or issue URL resolves to a real, merged or open item. If a PR URL is missing, ask for it.
3. **Update** the wave row in the roadmap section: annotate the row with `→ implemented: <PR-URL>`, `→ deferred: <issue-URL>`, or `→ retired: <rationale>`.
4. **Append one log line** to `## Processing log`: `YYYY-MM-DD — <wave-id> — <decision> — verified: <method>`.
5. **Flip `status`** in frontmatter to `in-progress` on the first wave closure if it was `open`.
6. **Show the diff.** Do not commit automatically.

Read `examples/03-wave-implementation.md` for a worked closure cycle.

#### 3. `close` — seal the sweep cycle

1. **Read** the open consolidated report under `.audits/skills-agents-sweep/`.
2. **Refuse** if any wave lacks a decision. Each wave row must be annotated with `implemented`, `deferred`, or `retired` before close is allowed.
3. **Verify** that every `deferred` wave has a live tracking-issue URL in its annotation; offer to open issues for any that lack one.
4. **Delete** the consolidated report file.
5. **Compose the deletion commit message** exactly: `sweep(skills-agents-sweep): close <slug>--<wave-summary>` in the subject, where `<wave-summary>` is a comma-separated list like `W1-W3-implemented,W4-deferred`. Body lists deferred-issue URLs and `repo-revision`.
6. **Run the commit only with explicit user confirmation.** Show the message first.

### Examples

- Read `examples/01-baseline-sweep.md` for a full-scope portfolio sweep: dispatching per-artefact reviews, running cross-cutting analysis, and producing the consolidated report.
- Read `examples/02-cross-cutting-discovery.md` for finding a spec-induced gap (phantom skill) during cross-cutting analysis in phase 2.
- Read `examples/03-wave-implementation.md` for recording wave decisions and closing a completed sweep cycle.

### Gotchas

- **One open sweep at a time.** The governing spec is strict: a second sweep must not be opened until the previous one is closed. Always check for an existing open report before running `audit`. A stale open report (no processing-log entry for six months) should be explicitly closed or resumed, not silently overwritten.
- **Phase ordering is mandatory.** The consolidated report must exist on disk before phase 4 implementation begins. Do not propose PRs based on in-memory analysis — the on-disk report is the evidence source every implementation PR references.
- **Per-artefact reviews are phase 1, not optional.** Cross-cutting findings in phase 2 are only as reliable as the per-artefact plans feeding them. If [`skill-review`](skill-review.md) or [`agent-review`](agent-review.md) plans are missing for any in-scope artefact, record the gap in the report's `## Scope` section.
- **Cross-cutting analysis covers only what per-artefact reviews cannot.** Do not restate per-artefact findings in the consolidated report body. Cite the plan path; do not reproduce the findings inline.
- **`spec/.spec-config.yml` must be read before resolving any spec path.** The canonical language for all spec paths depends on `canonical_language` in that config; defaulting to `en` without reading the config silently misroutes in repos with a different canonical language.

### Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/skills-agents-sweep/<run-id>.yml` after every successful user-approval gate and after each named phase boundary. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope (`schema_version`, `run_id`, `inputs`, `phase`, `decisions[]`, `status`, ...) and the fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

### Hard rules

- **Never open a second sweep while one is open.** Check for `status: open` in every file under `.audits/skills-agents-sweep/` before running `audit`.
- **No phase 4 before the report file exists on disk.** Implementation PRs must cite the report; a report that exists only in memory cannot be cited.
- **Every wave decision must be documented.** Silent deferrals violate the governing spec. `→ deferred` without a tracking-issue URL is not a valid decision.
- **No cross-cutting finding without a cited spec path.** If an issue is real but no spec covers it, record it as `Info` with a note that the spec may need to grow — never promote an opinion to `Warning` or `Critical`.
- **English section headings, English commit messages.** Prose inside findings and the consolidated report may follow the user's language; structural headings and commit messages stay English.
- **When `spec/claude/skills-agents-sweep/` and this skill disagree, the spec wins.** Raise the discrepancy rather than silently following the skill.

### Multi-model testing

Operations and examples in this skill are verified on Claude Sonnet 4.6 as the default model. Full-scope sweeps over large inventories (30-plus artefacts) benefit from Opus 4.7 for deeper cross-spec reasoning in phase 2. Haiku 4.5 is appropriate for the `update` and `close` operations on an already-complete report. The skill has no model-specific assumptions beyond standard tool-call semantics.
