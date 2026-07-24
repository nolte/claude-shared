# Issue Orchestration

Status: draft

## Context

Readers: skill and agent authors implementing the orchestrator, and operators who
invoke it to take an issue end-to-end. The operator approves seven gates—issue scope,
the requirements-understanding check (whether to elicit or override), classification
(for `security` / `spec-change`), the pre-analysis decomposition, the route decision,
each specialist dispatch, and the PR—before a merge is reached. All of the
orchestration's on-disk work happens in a dedicated worktree off `develop`, never in
the primary checkout.

The portfolio already declares a full planning pipeline—`roadmap-plan` queues
outcomes, `feature-decompose` breaks a roadmap item into testable features,
`sprint-plan` pulls features into a sprint, and `sprint-execute` / `sprint-review`
drive them to `done`. It also declares an orchestrator pattern for hands-on
remediation: `workflow-health-triage` classifies a red CI run and dispatches the
most specialized agent; `continuous-improvement-triage` generalizes that dispatch
across every audit source. What's missing is an **entry point for a raw GitHub
issue**. Today an issue becomes work only when a human manually rewrites it into a
roadmap item, a feature, or an ad-hoc branch—there is no process that *fully
comprehends* an issue, decomposes it into specialist-ready work packages, and
orchestrates the existing specialists (skills and agents) through to a pull
request.

Without this spec, issue intake is undisciplined: the same issue is analysed
differently by every contributor, the decomposition lives only in someone's head,
specialist coverage is used inconsistently (a security issue gets a generalist
fix instead of `code-security-reviewer`), and the link from a merged PR back to the
motivating issue is informal. This spec defines a single orchestration
process—analyse, decompose, route, dispatch, verify—whose quality-bearing core
is a **run-scoped pre-analysis artifact** that prepares each sub-problem so a
specialist can implement it completely and to a high standard. That artifact is a
process artifact rather than a deliverable: it's reviewable while the run is open
and removed again before the pull request merges, so what outlives the run is the
pull request's audit-trail section and the issue thread, not a file on the default
branch (see §Pre-analysis artifact lifecycle). The orchestrator is
a generalist: it never performs the specialist remediation itself when a matching
specialist exists.

## Goals
- A raw GitHub issue is comprehended in full before any code is written: body,
  comments, labels, linked issues and PRs, and the repository surface it touches
- Every issue is decomposed into atomic, testable work packages, each mapped to the
  most specialized available skill or agent, and the decomposition is persisted for
  the run as a reviewable artifact rather than living only in conversation
- Process artifacts don't accumulate on the default branch: the decomposition is
  committed so it's reviewable inside the pull request, then removed before the
  merge, and the audit trail that survives is the pull request's **Risk / rollout
  notes** plus the issue comment
- The role of the orchestrator is to analyse, decompose, route, dispatch, and
  verify—not hands-on remediation when a specialist exists; specialists do the
  editing through the standard PR gate
- An issue that's too large for direct implementation is routed into the formal
  `roadmap → feature → sprint` pipeline instead of being decomposed ad-hoc, so the
  planning layer is never bypassed
- Every pull request the orchestration produces is traceable back to the issue,
  carries the issue classification, and names the specialist that produced each
  part of the fix, so coverage gaps are discoverable from merged history
- Specialist selection is resolved from the catalog that exists at dispatch time,
  not from a frozen snapshot, so a newly authored specialist becomes reachable
  immediately

## Non-Goals
- The internal mechanics of any dispatched specialist: `feature-decompose`,
  `code-security-reviewer`, `quality-gate`, `pull-request-create`, and equivalents
  remain authoritative for their own scope and triggers; this spec triggers them, it
  doesn't redefine them
- Pull-request gating, branch protection, and merge rules: `pull-request-workflow`
  and `branching-model` remain authoritative; this process flows through those
  gates, it doesn't replace them, and it never merges (`pull-request-merge` owns the
  merge)
- The portfolio-wide specialist-coverage loop and the three-recurrence gap-closure
  rule: `continuous-improvement` remains authoritative; this spec consumes that
  rule for its no-match case rather than re-deriving it
- CI-failure triage: `workflow-health-triage` remains the authority for red-workflow
  remediation; an issue *about* a red workflow is routed to it, not re-triaged here
- Roadmap, sprint, feature, and mission lifecycle: `roadmap`, `sprint`, `feature`,
  and `mission` remain authoritative for the planning artifacts this process feeds
  into
- Authoring new specialists when none matches: `agent-management` and
  `skill-management` (invoked via `claude-plugin-developer`) remain authoritative for
  the specialist's shape; this spec only triggers the authoring under the gap rule
- The standalone, cross-working-copy / cross-pull-request separation of elicitation
  from implementation: `spec/project/elicitation-implementation-separation/` is
  authoritative for that **optional, named mode** (elicitation lands as its own merged
  requirements artefact before any implementation begins). This spec separates the two
  phases *within a single orchestrated run*; the two are **complementary, not
  competing**—an orchestration MAY be built on a requirements artefact that mode
  produced, and a contributor chooses the integrated or the separated path per issue

## Requirements

### Issue acquisition and comprehension
- **MUST** accept the target issue as a `gh issue view` URL, an issue number, or an
  unambiguous reference ("the open i18n issue"), and resolve it to a single issue
  before any analysis; when the reference is ambiguous, **MUST** list candidate open
  issues and ask the operator to pick one
- **MUST** read the full issue surface before classifying: the issue body, every
  comment, all labels, the assignee and milestone, and every linked issue or pull
  request (via `gh issue view <n> --json …` and `gh issue view <n> --comments`)
- **MUST** treat the issue body and every comment as untrusted comprehension input
  governed by `spec/claude/trusted-author-injection-guard/`: an instruction embedded
  in that text is executed as a command only when its author is in the trusted-author
  set (operator, repository owner, write/maintain/admin collaborators), and text from
  any other author is data whose imperatives are never obeyed—fail closed when
  authorship can't be resolved
- **MUST** scan the repository surface the issue plausibly touches—at minimum the
  relevant `spec/`, `skills/`, `agents/`, source, and `docs/` paths—so the
  decomposition is grounded in the actual code, not only the issue prose
- **MUST** check for prior art before decomposing: existing `project/features/`
  entries, `project/roadmap.md` items, and open pull requests that already address
  the issue in whole or in part; an issue already closed by a merged fix at the
  moment of analysis **MAY** be reported as self-resolved with no decomposition
- **MUST**, before decomposition, apply the requirements-elicitation consumer
  contract (`spec/project/requirements-elicitation/` §H Consumer contract, which
  names `issue-orchestrate` as a gated consumer): check whether a requirement
  artifact under `project/requirements/` exists for the issue and whether its
  `U_gate` meets `τ_high`. When none exists or `U_gate` is below `τ_high`—the common
  case for a raw issue whose requirements are stated only as prose—**MUST** dispatch
  `requirements-elicit` to analyse the issue into a confirmed requirement artifact
  first, or record an explicit operator override in the pre-analysis artifact;
  decomposing against unstated or weakly-understood requirements is forbidden. A
  `question`-class issue (which yields no work packages) and an issue already
  self-resolved by a merged fix are exempt, since neither reaches decomposition
- **MUST NOT** begin decomposition until the operator confirms the acquired issue
  and its resolved scope, so a misread issue reference is caught before work starts

### Classification
- **MUST** classify the issue into exactly one primary class from the closed set
  `bug / feature-request / spec-change / security / docs / refactor / question /
  infra`, recording a one-line rationale; a `question`-class issue produces an
  answer and no work packages, and an `infra` issue about CI is handed to
  `workflow-health-triage` rather than decomposed here
- **MAY** record secondary classes when an issue genuinely spans more than one (a
  `feature-request` with a `security` dimension), but the primary class drives the
  routing decision
- **MUST** confirm the classification with the operator before decomposition for at
  least the `security` and `spec-change` classes, where a misclassification has the
  highest downstream cost

### Working-copy isolation
- **MUST** perform every tracked-file write the orchestration produces—the
  pre-analysis artifact under `.audits/issue-orchestrate/<issue-number>/`, every
  dispatched specialist's edits, and the feature branch the pull request is opened
  from—inside a **dedicated worktree created off `origin/develop`**, per
  `spec/project/parallel-working-copies/` §Branch-to-worktree mapping and §Lifecycle:
  Create; the reference creation path is `task worktree:add -- <branch> [slug]`. The
  primary checkout **MUST** stay on `develop` and **MUST NOT** be switched onto the
  feature branch, even for a single-package issue
- **MUST** establish the worktree before the first tracked-file write, so no
  orchestration output ever lands in the primary checkout; the pre-analysis artifact
  is that first write. When the issue is routed to the formal pipeline instead of
  implemented directly, the downstream planning skill's own working-copy discipline
  governs the artifacts it writes
- **MAY** carry out the issue processing inside a **dedicated worktree-isolated agent
  that takes the issue id as its parameter** (`Agent(..., isolation: "worktree")`), as
  a sanctioned alternative to the fresh-top-level-session default of
  `spec/project/parallel-working-copies/` §Claude Code session scoping. When it does,
  it **MUST** point the agent's worktree root at the spec-conformant
  `${NOLTE_WORKTREE_ROOT:-~/repos/.worktrees}/<repo>/agents/` path per §Path layout
  (never under `.claude/worktrees/`), and it accepts the trade-off that a
  subagent transcript can't be independently resumed—so the per-run
  checkpoint under `.resume/issue-orchestrate/` (see §Resumption and operator gating)
  remains the recovery anchor. The operator-approval gates stay with the orchestrating
  skill regardless; the dedicated agent executes the hands-on work, it doesn't
  absorb the gates

### Decomposition into work packages (the pre-analysis core)
- **MUST** decompose the issue into atomic, independently testable work packages;
  each package **MUST** record: a stable package id, a problem statement, its
  acceptance criteria, the files or artifacts it touches, the specialist that should
  implement it (resolved per *Specialist dispatch* below), and its dependencies on
  other packages (a directed acyclic ordering)
- **MUST** ground the decomposition in the **confirmed requirement artifact** the
  requirements gate produced (§Issue acquisition; the `requirements-elicit` output
  under `project/requirements/`), not in the raw issue prose—the elicited,
  `τ_high`-confirmed requirements are the decomposition's input, so every work package
  traces to an understood requirement rather than a guess
- **MAY** delegate the decomposition itself to a **dedicated planning agent** (the
  dedicated-agent path of §Working-copy isolation), resolved by capability at dispatch
  time: it takes the issue id, consumes the requirement artifact and the repository
  surface, and returns the specialist-mapped work-package plan for the **specialised
  implementation agents** to build. This makes the pipeline explicit—`requirements-elicit`
  analyses the issue into a confirmed requirement artifact, the planning agent authors
  the implementation plan from it, and the implementation specialists execute each
  package—while the operator-approval gate below stays with the orchestrating skill and
  the planning agent never dispatches, implements, or opens a PR itself
- **MUST** keep each package small enough that a single specialist invocation can
  complete it to a verifiable acceptance criterion; a package that can't be stated
  with a testable acceptance criterion is a signal the issue belongs in the formal
  pipeline (see *Routing*), not a package to dispatch
- **MUST** persist the decomposition as a pre-analysis artifact at
  `.audits/issue-orchestrate/<issue-number>/analysis.md`, carrying the issue
  metadata, the classification and rationale, the in/out-of-scope boundary, the
  work-package table, the cross-package dependency ordering, the risks, and any open
  questions for the operator; the artifact is run-scoped and removed again before
  the merge, per §Pre-analysis artifact lifecycle
- **MUST** present the pre-analysis artifact for operator approval before any
  dispatch; the artifact is the reviewable hand-off contract, and dispatch on an
  unapproved decomposition is forbidden
- **SHOULD** write the pre-analysis artifact in the issue's own language; the
  machine-readable audit-trail fields that later land in a PR (classification label,
  specialist `subagent_type`, finding source) stay English so the trail is grep-able
  portfolio-wide

### Pre-analysis artifact lifecycle (transient)

The pre-analysis artifact is a **process artifact, not a deliverable**. It earns
its keep as the reviewable decomposition gate while the run is open, and it has no
readership once the capability it describes is implemented, verified, and merged.

- **MUST** treat `.audits/issue-orchestrate/<issue-number>/analysis.md` as
  run-scoped: written and committed on the run's feature branch, kept there while
  the packages are dispatched and their results recorded, and removed with a
  fix-forward `git rm` on that same branch before the pull request merges. The
  artifact **MUST NOT** reach the default branch
- **MUST NOT** remove the artifact before every dispatched work package is
  implemented and the §Verification and traceability gate is green; the removal is
  the run's last content change, not a cleanup that races the specialists
- **MUST** perform the removal as a **fix-forward commit on the feature branch**,
  never as a history rewrite, so the pull request's commit trail still carries an
  artifact a reviewer can read while the squashed merge commit carries none of it
- **MUST NOT** conceal the artifact behind a `.gitignore` entry instead. An ignored
  artifact never appears in the pull request, which hollows out the
  operator-approval gate §Decomposition makes load-bearing, and
  `spec/claude/review-plan/` §File location and naming already fixes `.audits/` as
  tracked-not-ignored territory portfolio-wide. Tracked-then-removed is the same
  lifecycle that spec gives a review plan—create, work off, delete, and let the git
  history be the trail—applied to this artifact
- **MUST** land the durable audit trail outside the file before it goes: the pull
  request's **Risk / rollout notes** section (per §Verification and traceability)
  and the issue comment recording the classification, package count, and route
  taken. A fact worth keeping after the merge belongs in one of those two places
- **MUST NOT** extend this transience to the requirement artifact under
  `project/requirements/<slug>.md`. That artifact stays durable like its siblings:
  it's the confirmed input every work package traces back to, it stays readable
  after the merge, and `spec/project/requirements-elicitation/` §G owns its
  lifecycle
- **MUST NOT** treat the removal as a resumption concern: the recovery anchor is
  the checkpoint under `.resume/issue-orchestrate/` per §Resumption and operator
  gating, and the artifact still exists at every phase boundary a resume can land
  on, because the removal follows the last of them
<!-- vale Microsoft.Contractions = NO -->
- **SHOULD NOT** generalise this rule to every `.audits/` path. Dated, accumulating
  audit records keep the non-disposable lifecycle their own specs give them (the
  enumerated set in `spec/claude/review-plan/` §Relationship to other specs); this
  section is scoped to the pre-analysis artifact this process writes
<!-- vale Microsoft.Contractions = YES -->

### Specialist dispatch (reuse over reinvention)
- **MUST** resolve the specialist for each work package by a runtime lookup of the
  catalog that exists at dispatch time, with a `Glob` over every distribution root: the
  plugin's own specialists at `${CLAUDE_PLUGIN_ROOT}/skills/*/SKILL.md` and
  `${CLAUDE_PLUGIN_ROOT}/agents/*.md` (where the `nolte-shared` specialists live when
  the orchestrator runs inside a consumer repository), the consumer project's local
  `skills/*/SKILL.md` and `agents/*.md`, and the project-distributed
  `~/.claude/agents/*.md`; then match each package against the candidates'
  `description` lines on the basis of stated responsibility, not on the candidate's
  name. The catalog **MUST NOT** be frozen as an inline snapshot in any implementing
  skill. A bare `skills/*/SKILL.md` glob that omits `${CLAUDE_PLUGIN_ROOT}` is a
  defect: in a consumer repository it silently misses every plugin-distributed
  specialist
- **MUST NOT** have the orchestrator perform a work package's hands-on editing itself
  when a matching specialist exists; the orchestrator analyses, decomposes,
  dispatches via `Agent(subagent_type=<name>)` or a matching skill invocation, and
  verifies, and **MAY** additionally chain multiple specialists when one package
  crosses responsibilities
- **SHOULD** treat the following as illustrative dispatch anchors—well-known
  portfolio specialists for common classes, each still re-resolved by description
  match at dispatch time and never hard-coded as a frozen table: a `spec-change`
  package through the spec-authoring specialist (the `spec` skill); a documentation
  package through the audience-targeted documentation specialist; a feature-shaped
  package through `feature-decompose`. A `security` package follows the
  audit→fix→verify chain defined in *Verification* below rather than a single
  dispatch: the read-only `code-security-reviewer` agent scopes the surface, a
  coding-capable specialist (or, absent a match, the generalist under the gap rule)
  authors the fix, and the built-in `security-review` skill verifies the diff
- **MUST** treat a work package for which no specialist matches as a portfolio gap
  governed by `continuous-improvement` §Portfolio gap closure: the orchestrator
  records the no-match, applies the three-recurrence rule, and **MAY** dispatch
  `claude-plugin-developer` to author a new specialist when the rule (or a recorded
  high-impact justification) is satisfied; until then the generalist may handle the
  package, and the PR records the explicit "no matching specialised agent" note
- **MUST** dispatch work packages in their dependency order, gating on operator
  confirmation at each package boundary, and **MUST** collect and record each
  specialist's result before dispatching a dependent package

### Routing to the formal pipeline (no planning bypass)
- **MUST** route an issue into the formal `roadmap → feature → sprint` pipeline,
  rather than decomposing it for direct implementation, when it spans more than one
  goal outcome, requires more than a single coherent PR strand, or would create or
  retarget a roadmap item; the routing decision **MUST** be an explicit,
  operator-confirmed gate recorded in the pre-analysis artifact
- **MUST**, when routing to the pipeline, hand the issue to `feature-decompose`
  (for an existing roadmap item) or to `roadmap-plan` (when a new outcome or item is
  needed) rather than drafting features or roadmap items inline, so the planning
  specs stay authoritative
- **MAY** implement a bounded issue directly through the dispatch-and-verify path
  defined above. *Bounded* means, operationally: one coherent goal outcome; a single
  PR strand (every work package lands on one feature branch as one pull request); and
  no new or retargeted roadmap item. The moment the work needs a second independent
  feature branch, or touches a second goal outcome, the issue is unbounded and routes
  to the pipeline
- **MUST NOT** mix the two routes for one issue: an issue is either implemented
  directly or routed to the pipeline; a partial direct implementation that silently
  leaves the rest unplanned is forbidden

### Verification and traceability
- **MUST** require `quality-gate` to pass green on the produced change before the
  pull request opens, and **MUST**, for any package touching a security-sensitive
  path, run the read-only `code-security-reviewer` agent to scope the surface and the
  built-in `security-review` skill to verify the produced diff before the PR opens.
  (`security-review` is the Claude Code harness built-in, not a `nolte-shared`
  plugin agent; it's invoked as the `security-review` skill, not via
  `Agent(subagent_type="nolte-shared:security-review")`.)
- **MUST** ensure every pull request the orchestration produces links the issue
  (`Closes #<n>` or the repository's linking convention) and carries, in its **Risk /
  rollout notes** section per `pull-request-workflow`: the issue reference, the issue
  classification verbatim, and, per work package, the dispatched specialist
  (`subagent_type` literal) or the explicit "no matching specialised
  agent—generalist remediation" note
- **MUST** remove the pre-analysis artifact from the feature branch per
  §Pre-analysis artifact lifecycle once every package is implemented and the gate
  above is green, and before the pull request is handed to `pull-request-merge`, so
  the merge can't carry it onto the default branch; the **Risk / rollout notes**
  section and the issue comment are what survive the merge
- **MUST NOT** merge the pull request; the orchestration stops at an open,
  audit-trailed PR and hands the merge to `pull-request-merge`, which re-validates the
  gate
- **MUST NOT** bypass any gate from `pull-request-workflow` or `branching-model`: no
  `--admin` override, no `continue-on-error` masking of a required check, no
  required-check removal
- **SHOULD** post the pre-analysis artifact's summary (classification, package
  count, route taken) back to the issue as a comment when the operator confirms, so
  the issue thread records how the work was structured

### Resumption and operator gating
- **MUST** be resumable per `spec/claude/resumable-work/`: state is saved to a
  checkpoint after every operator-approval gate and every named phase boundary (acquire,
  analyze, decompose, route, orchestrate, verify), so a crash mid-orchestration
  resumes from the last checkpoint rather than re-running dispatched specialists
- **MUST** gate every externally-visible action (the pre-analysis artifact write,
  each specialist dispatch, the issue comment, the PR creation) on operator
  confirmation; the orchestrator never fires a mutating step without a recorded "yes"

## Acceptance Criteria
- [ ] For an acquired issue, the pre-analysis artifact at
  `.audits/issue-orchestrate/<issue-number>/analysis.md` existed on the run's feature
  branch at dispatch time—recoverable after the fact with
  `git log --diff-filter=A -- .audits/issue-orchestrate/<issue-number>/` on that
  branch—and recorded the issue
  metadata, the single primary classification with rationale, the in/out-of-scope
  boundary, and a work-package table where every package names a problem statement,
  acceptance criteria, touched files, a specialist, and its dependencies
- [ ] For every orchestration run classified `security` or `spec-change`, the
  pre-analysis artifact records an explicit operator classification-confirmation step
  taken before the work-package table was populated
- [ ] For every decomposed issue, a requirement artifact meeting `τ_high` existed
  before decomposition, or the pre-analysis artifact records an explicit operator
  override of the requirements-elicitation consumer gate
- [ ] Every work package in a pre-analysis artifact traces to the confirmed requirement
  artifact the requirements gate produced, not to raw issue prose; where a dedicated
  planning agent authored the decomposition, it consumed that artifact and neither
  dispatched a specialist nor opened a PR
- [ ] For every issue the orchestration implemented directly, every tracked-file
  write it produced (the pre-analysis artifact, the dispatched edits, the feature
  branch) lived in a dedicated worktree off `develop`, and the primary checkout was
  never switched off `develop`
- [ ] No work package in any pre-analysis artifact lacks a testable acceptance
  criterion; a package that can't state one is instead recorded as a routing signal
  to the formal pipeline
- [ ] The default branch's tree carries no `.audits/issue-orchestrate/` path
  (`git ls-tree -r --name-only develop -- .audits/issue-orchestrate/` returns
  nothing), and no commit reachable from the default branch adds one
  (`git log --diff-filter=A --name-only develop -- .audits/issue-orchestrate/` is
  empty)
- [ ] For every pull request this orchestration produced, the feature branch carries
  both the artifact's creation commit and its removal commit, the removal commit
  post-dates the last specialist result recorded in the artifact, and `.gitignore`
  carries no `.audits/issue-orchestrate/` entry
- [ ] For every merged orchestration run, the requirement artifact under
  `project/requirements/<slug>.md` that grounded the decomposition is still present
  on the default branch after the merge
- [ ] Every specialist named in a work package was resolved by a runtime catalog
  lookup at analysis time, and no implementing skill carries a frozen inline list of
  specialist names as its dispatch table
- [ ] For every issue routed to the formal pipeline, the pre-analysis artifact
  records the routing rationale and the hand-off target (`feature-decompose` or
  `roadmap-plan`), and no roadmap item or feature was drafted inline by the
  orchestrator
- [ ] For the last 10 pull requests produced by this orchestration, each links its
  originating issue and its **Risk / rollout notes** names the issue classification
  and, per package, the dispatched specialist or the explicit "no matching
  specialised agent" note
- [ ] Every pull request produced by this orchestration carries `Closes #<n>` (or the
  repository's configured linking keyword) in its body; per `pull-request-workflow`
  the issue closure fires on the `main` fast-forward, not on the `develop` merge
- [ ] No pull request produced by this orchestration was merged by the orchestration
  itself, and none shows a branch-protection override, an `enforce_admins: false`
  exception, or a required-check bypass
- [ ] For every `security`-class issue, the read-only `code-security-reviewer` agent
  and the built-in `security-review` skill both ran before the PR opened (audit, then
  diff verification), recorded in the artifact and the PR notes
- [ ] For every work package whose finding class has been generalist-handled three
  or more times without a matching specialist, either a specialist now exists or an
  open issue tracks its creation with a named owner, per `continuous-improvement`
- [ ] Every orchestration run that was interrupted mid-flow and re-invoked with the
  same issue resumed from its last checkpoint rather than re-dispatching an
  already-completed work package
- [ ] For each completed orchestration run, the checkpoint state under
  `.resume/issue-orchestrate/` records a decision entry for every externally-visible
  gate—the artifact write, each specialist dispatch, the issue comment, and the PR
  creation

## Open Questions
- §Routing now defines *bounded* operationally (one goal outcome, one feature branch
  / one PR strand, no new or retargeted roadmap item). Whether to additionally harden
  it with a quantitative threshold (for example a maximum work-package count) is
  deferred until enough runs exist to calibrate it.
- Whether a directly-implemented multi-package issue should land as one pull request
  or one PR per coherent package set is left to the operator per issue; the default
  is a single PR strand per issue. A firmer rule is deferred.
- Whether the pre-analysis artifact should additionally be mirrored into the issue
  thread by default (rather than only on operator confirmation) is deferred pending
  operator preference across real runs.
