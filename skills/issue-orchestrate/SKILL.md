---
name: issue-orchestrate
description: "Orchestrates a raw GitHub issue to an open, audit-trailed pull request per `spec/project/issue-orchestration/`. Comprehends the issue (body, comments, labels, linked items, repo surface), classifies it (`bug / feature-request / spec-change / security / docs / refactor / question / infra`), decomposes it into atomic specialist-ready work packages persisted as a pre-analysis artifact, routes large issues into the formal roadmap→feature→sprint pipeline, dispatches each package to the most specialised available skill or agent resolved by runtime lookup, and verifies via `quality-gate` and the standard PR flow. Invoke when the user asks to \"analyse this issue\", \"orchestrate issue #N\", \"take this issue end-to-end\", or equivalent German requests. Don't use to merge the PR (use `pull-request-merge`), to triage a red CI run (use `workflow-health-triage`), or to decompose an existing roadmap item (use `feature-decompose`). Supports resume per `spec/claude/resumable-work/`."
tags: [triage, audit]
phase: plan
disable-model-invocation: true
summary: "Takes a raw GitHub issue end-to-end: comprehend, classify, decompose into specialist-ready work packages, route or dispatch, and verify to an open PR."
summary_de: "Führt ein rohes GitHub-Issue end-to-end: durchdringen, klassifizieren, in spezialisten-gerechte Arbeitspakete zerlegen, routen oder dispatchen und bis zu einem offenen PR verifizieren."
use_when:
  - "you want to take a raw GitHub issue from intake to an open pull request"
  - "you want a deep pre-analysis that decomposes an issue into specialist-ready work packages"
  - "you want each sub-problem dispatched to the most specialised available skill or agent"
  - "you want a large issue routed into the formal roadmap→feature→sprint pipeline instead of ad-hoc work"
dont_use_when:
  - situation: "You want to merge the pull request the orchestration produced"
    alternative: pull-request-merge
  - situation: "You want to triage a failing CI workflow run, not an issue"
    alternative: workflow-health-triage
  - situation: "You already have a roadmap item and just want it decomposed into features"
    alternative: feature-decompose
  - situation: "You want to triage portfolio audit findings rather than a single issue"
    alternative: continuous-improvement-triage
see_also:
  - feature-decompose
  - roadmap-plan
  - requirements-elicit
  - pull-request-create
  - workflow-health-triage
resumable: true
---

# Issue Orchestration

Implements `spec/project/issue-orchestration/`. The skill is the generalist
orchestrator that comprehends a raw GitHub issue, decomposes it into atomic
specialist-ready work packages, dispatches the hands-on work to the most
specialised available Claude skill or agent, and verifies the result through the
standard pull-request gate. It never performs a work package's editing itself when
a matching specialist exists; the quality-bearing core is the persistent
pre-analysis artifact that prepares each sub-problem so a specialist can implement
it completely.

## Why this is a skill, not an agent

- **Externally-visible mutations gate on operator confirmation.** Issue-scope
  confirmation, the classification call, the pre-analysis approval, the route
  decision, each specialist dispatch, and the PR title / body are mid-flow operator
  dialogues; an agent's fire-and-forget shape would miss them.
- **Orchestrator pattern (per `skill-vs-agent`).** The work is *analyse, decompose,
  route, dispatch, verify*; the dispatched specialist does the editing. The
  orchestrator stays in the main thread and chains other skills (`feature-decompose`
  or `roadmap-plan` for the pipeline route, `quality-gate`, `pull-request-create`).
- **Multi-phase state accumulates across prompts.** A decomposition, a route
  decision, and a sequence of per-package dispatches span many turns; a skill's
  persistent instruction context and the resumable-work envelope fit this naturally.
- Counter-dimension considered: a narrow agent could own the decomposition step in
  isolation and gain context-window protection, but every downstream lane (routing,
  dispatch, verification, PR annotation) is interactive — keeping the whole flow in
  one orchestrating skill is simpler than splitting at the decomposition boundary.

## User-language policy

Detect the operator's language and respond in it. All `git`, `gh`, and
`Agent(subagent_type=…)` invocations stay English, and the pre-analysis artifact's
machine-readable audit-trail fields (classification label, specialist
`subagent_type`, finding source) stay English so the PR trail is grep-able
portfolio-wide. The artifact's prose body is written in the issue's own language.

## German trigger phrases

- „dieses Issue analysieren und umsetzen"
- „Issue #N end-to-end orchestrieren"
- „dieses Issue für die Spezialisten aufbereiten"
- „das Issue in Arbeitspakete zerlegen"

## Preconditions

Before any operation:

- Confirm the working directory is a git repository and `gh auth status` reports
  authenticated.
- Confirm `spec/project/issue-orchestration/<canonical_language>.md` exists in the
  current project. If missing, stop and report — without it the classifications and
  routing rules are ad-hoc; this skill is the spec's implementer, not its
  replacement.
- The operator supplies the target issue (a `gh issue view <n>` URL, an issue
  number, or an unambiguous reference). If nothing is supplied, run
  `gh issue list --state open --limit 20` and ask which issue to orchestrate. If the
  reference is ambiguous, list the candidate open issues and ask the operator to pick
  one.
- When the issue describes a feature or change whose requirements are not yet
  precisely stated, a requirement artefact under `project/requirements/` should
  exist before decomposition, per `spec/project/requirements-elicitation/`
  § Consumer contract. If the issue body is vague and no artefact exists (so
  `U_gate` would be below `τ_high`), dispatch `requirements-elicit` first, or
  record an explicit operator override, rather than decomposing against guesses.

## Operations

The six operations are a forward pipeline: each gates on the previous one's
operator approval. State checkpoints at every gate per *Resumability*.

### 1. acquire

Comprehend the full issue surface before classifying. Run in parallel:

- `gh issue view <n> --json number,title,body,labels,assignees,milestone,state,url`
- `gh issue view <n> --comments`
- `gh issue view <n> --json closedByPullRequestsReferences` (resolve linked PRs);
  `gh search prs --json …` or `gh pr list` to find open PRs that reference the issue

Then ground the issue in the repository: scan the `spec/`, `skills/`, `agents/`,
source, and `docs/` paths the issue plausibly touches, and check for prior art —
existing `project/features/` entries, `project/roadmap.md` items, and open PRs that
already address it in whole or in part. If a merged fix already closes the issue,
report it as self-resolved and stop. Confirm the acquired issue and its resolved
scope with the operator before proceeding.

### 2. analyze (classify)

Assign exactly one primary class from the closed set
`bug / feature-request / spec-change / security / docs / refactor / question /
infra`, with a one-line rationale. Record any genuine secondary class, but the
primary class drives routing. Two classes short-circuit the pipeline:

- `question` → produce an answer, no work packages; stop after recording it.
- `infra` about CI → hand to `workflow-health-triage` rather than decompose here.

Confirm the classification with the operator before decomposition for at least the
`security` and `spec-change` classes, where misclassification has the highest cost.

### 3. decompose (the pre-analysis core)

Decompose the issue into atomic, independently testable work packages. Each package
records a stable id, a problem statement, its acceptance criteria, the files or
artifacts it touches, the specialist that should implement it (resolved per
operation 5's runtime lookup), and its dependencies on other packages as a directed
acyclic ordering. A package that cannot be stated with a testable acceptance
criterion is a routing signal to the formal pipeline (operation 4), not a package to
dispatch.

Instantiate `templates/analysis.template.md` and write the pre-analysis artifact to
`.audits/issue-orchestrate/<issue-number>/analysis.md`, carrying the issue metadata,
the classification and rationale, the in/out-of-scope boundary, the work-package
table, the dependency ordering, the risks, and any open questions. Present the
artifact for operator approval before any dispatch. **Hard:** dispatch on an
unapproved decomposition is forbidden.

### 4. route

Decide, as an explicit operator-confirmed gate recorded in the artifact, whether the
issue is implemented directly or routed to the formal pipeline:

- **Route to the pipeline** when the issue spans more than one goal outcome, needs
  more than a single coherent PR strand, or would create or retarget a roadmap item.
  Hand it to `feature-decompose` (existing roadmap item) or `roadmap-plan` (new
  outcome or item) — never draft features or roadmap items inline. After hand-off,
  the orchestration stops; the planning skills own the rest.
- **Implement directly** when the issue is bounded — one coherent outcome, a single
  PR strand, no new roadmap item — proceeding to operation 5.

Never mix the two routes for one issue: a partial direct implementation that
silently leaves the rest unplanned is forbidden.

### 5. orchestrate (dispatch)

Resolve the specialist for each work package by a runtime lookup of the catalog that
exists now; never freeze a snapshot of "which specialists exist" inside this skill
body.

1. **Resolve the candidate set.** `Glob` every distribution root: the plugin's own
   specialists at `${CLAUDE_PLUGIN_ROOT}/skills/*/SKILL.md` and
   `${CLAUDE_PLUGIN_ROOT}/agents/*.md` (where the `nolte-shared` specialists live when
   this skill runs inside a consumer repository), the consumer project's local
   `skills/*/SKILL.md` and `agents/*.md`, and `~/.claude/agents/*.md` for the
   project-distributed half. Then `Read` the `description:` line of every candidate and
   build a (`name`, `kind`, `description`) table; the table is the runtime inventory. A
   bare `skills/*/SKILL.md` glob that omits `${CLAUDE_PLUGIN_ROOT}` silently misses
   every plugin-distributed specialist in a consumer repo — the same
   `${CLAUDE_PLUGIN_ROOT}` rule the portfolio applies to bundled scripts.
2. **Match each package to a candidate** on the basis of its stated responsibility,
   not its name: a `spec-change` package maps to whichever skill's description names
   spec authoring (the `spec` skill); a documentation package to whichever agent names
   an audience-targeted documentation responsibility; a feature-shaped package to
   `feature-decompose`. A `security` package is not a single dispatch — it follows the
   audit→fix→verify chain in operation 6: the read-only `code-security-reviewer` agent
   scopes the surface, a coding-capable specialist (or the generalist under the gap
   rule) authors the fix, and the built-in `security-review` skill verifies the diff.
   These are illustrative anchors — re-resolve by description match each run, never
   from this list.
3. **No match is a portfolio gap.** When no candidate matches, apply
   `continuous-improvement` §Portfolio gap closure: record the no-match, count
   generalist-handled recurrences of the class, and at three or more (or with a
   recorded high-impact justification) offer to dispatch
   `Agent(subagent_type="nolte-shared:claude-plugin-developer")` to author a new
   specialist. Until the gap closes, the generalist may handle the package and the PR
   records the explicit "no matching specialised agent — generalist remediation"
   note.
4. **Dispatch in dependency order.** Walk the packages in their DAG ordering. For
   each, gate on operator confirmation, then dispatch via
   `Agent(subagent_type="<plugin>:<agent>")` or the matching skill invocation,
   passing the package's problem statement, acceptance criteria, touched files, and
   the issue reference. Collect and record each specialist's result in the artifact
   before dispatching a dependent package.

The dynamic-lookup design means a specialist that lands in any distribution root
becomes dispatchable immediately, and a renamed or removed one stops being a target
the next time the skill runs, with no stale snapshot to mislead the dispatch.

### 6. verify

Before any PR opens, require `quality-gate` to pass green on the produced change, and
for any package touching a security-sensitive path run the read-only
`code-security-reviewer` agent to scope the surface and the built-in `security-review`
skill to verify the produced diff. (`security-review` is the Claude Code harness
built-in, invoked as the `security-review` skill — not
`Agent(subagent_type="nolte-shared:security-review")`, which does not exist.) Then
open the PR via `pull-request-create` (the operator confirms title and body per that
skill's externally-visible-action gate) with:

- the issue linked (`Closes #<n>` or the repository's linking convention), and
- a **Risk / rollout notes** section per `pull-request-workflow` carrying the issue
  reference, the issue classification verbatim, and per work package the dispatched
  specialist (`subagent_type` literal) or the explicit "no matching specialised
  agent — generalist remediation" note.

When the operator confirms, post the artifact's summary (classification, package
count, route taken) back to the issue as a comment. The orchestration then stops at
an open, audit-trailed PR. The merge belongs to `pull-request-merge`, which
re-validates the gate. Report back the issue number, the classification, the route
taken, the dispatched specialists, the artifact path, the PR URL, and the one-line
"next action: invoke `pull-request-merge` after CI is green".

## Examples

- Read `examples/01-bounded-bug-direct-orchestration.md` when a bounded bug issue is
  decomposed and dispatched directly to specialists, ending at an open PR.
- Read `examples/02-feature-request-to-pipeline.md` when a large feature-request
  issue is routed into the formal `feature-decompose` / `roadmap-plan` pipeline.
- Read `examples/03-security-issue-specialist-dispatch.md` when a `security`-class
  issue dispatches `code-security-reviewer` and runs `security-review` before the PR.

## Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is
persisted to `.resume/issue-orchestrate/<run-id>.yml` after every successful
operator-approval gate and after each named phase boundary (`acquire`, `analyze`,
`decompose`, `route`, `orchestrate`, `verify`). On re-invocation, scan that
directory for files with `status: in_progress` whose `inputs:` snapshot (the issue
number and repository) matches the current invocation; if one matches, prompt the
operator with `Resume run <run_id> from phase <phase> (last checkpoint
<last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope
(`schema_version`, `run_id`, `inputs`, `phase`, `decisions[]`, `status`, ...) and the
fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't
duplicate those rules here. A resumed run never re-dispatches a work package whose
result is already recorded in the artifact.

## Hard rules

- **Never** begin decomposition before the operator confirms the acquired issue and
  its resolved scope; a misread issue reference must be caught before work starts.
- **Never** dispatch on an unapproved pre-analysis artifact; the artifact is the
  reviewable hand-off contract.
- **Never** perform a work package's hands-on editing inline when a matching
  specialist exists; analyse, decompose, dispatch, verify.
- **Never** freeze an inline snapshot of specialist names as a dispatch table; the
  catalog is resolved by runtime `Glob` each run.
- **Never** decompose an issue that belongs in the formal pipeline (more than one
  outcome, more than one PR strand, or a new/retargeted roadmap item) for direct
  implementation; route it to `feature-decompose` or `roadmap-plan` instead.
- **Never** mix the direct and pipeline routes for one issue, and never leave the
  remainder of a partially-implemented issue silently unplanned.
- **Never** classify an issue outside the closed set
  `bug / feature-request / spec-change / security / docs / refactor / question /
  infra`.
- **Never** open a PR whose **Risk / rollout notes** don't carry the issue
  reference, the classification, and the per-package specialist (or the explicit
  "no matching specialised agent" note).
- **Never** merge the PR (`pull-request-merge` owns that), pass `--admin`, mask a
  required check with `continue-on-error`, or remove a required check.
- **Always** prefer a plugin-distributed specialist over the generalist when one
  matches; the spec's §Specialist dispatch makes this a hard contract for the
  dispatch step.
- When `spec/project/issue-orchestration/` disagrees with this skill, the spec wins.
  Propose updating this skill rather than silently diverging.

## Gotchas

Per `spec/claude/skill-management/` §Gotchas — concrete corrections to non-obvious
environment facts the executing agent would otherwise get wrong.

- **An `infra` issue about a red workflow is not decomposed here.** A CI-failure
  issue is `workflow-health-triage`'s domain; decomposing it into work packages
  duplicates that skill's classification. Hand it over and stop.
- **A `question`-class issue produces no work packages.** Answering it and recording
  the answer is the whole job; manufacturing packages for a question is drift.
- **"Bounded" is about planning shape, not effort.** An issue that touches many files
  but is one coherent outcome with a single PR strand and no new roadmap item is
  bounded and implemented directly. An issue that spans two goal outcomes is *not*
  bounded even if each is small — it routes to the pipeline.
- **The pre-analysis artifact is the gate, not a by-product.** Skipping the artifact
  write to "save a step" and dispatching from memory removes the reviewable hand-off
  contract the spec makes load-bearing; the artifact must exist and be approved
  before any dispatch.
- **A specialist named in the artifact must come from the live catalog.** A package
  pointing at a specialist that no longer exists (renamed or removed) is a dispatch
  failure waiting to happen; re-resolve by `Glob` at dispatch time, not from the
  artifact's stale name if the catalog moved between analysis and dispatch.

## Multi-model testing

Examples and operations in this skill are verified on Claude Sonnet 4.6 as the
default model; spot-checked on Haiku 4.5 for cost-sensitive intake runs; Opus 4.7
is appropriate for high-stakes issues (security, spec-change, or wide-blast-radius
decompositions) that require deeper reasoning. The skill body has no model-specific
assumptions beyond standard tool-call semantics.
