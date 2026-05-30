# Continuous Improvement

Status: draft

## Context
The portfolio already declares **how** specifications and implementation are reconciled (`spec-drift-audit` for periodic deep audits, `workflow-health` for continuous GitHub Actions hygiene) and **how** specialized Claude Agents and skills are authored (`agent-management`, `skill-management`). The `workflow-health` spec, for its narrow slice, already requires that remediation work is dispatched to the most specialized available agent rather than handled by a generalist. What's missing is a portfolio-wide rule that generalizes this dispatch pattern across **every** audit source—spec-drift audits, project-structure audits, vocabulary drift, Renovate findings, prose-style drift, manual review—and that frames the full loop (audit → finding → specialist remediation → merge → next audit) as a single, closed, permanently running improvement cycle. Without this umbrella spec, specialist dispatch is workflow-health-only, spec-drift findings are routinely handled by a generalist even when a matching specialist exists, and portfolio gaps in the specialist roster stay invisible.

## Goals
- Every audit finding across the portfolio is routed to the most specialized Claude Agent or skill whose description matches it, not absorbed by a generalist out of convenience
- The generalist's role is triage, dispatch, and verification—not hands-on remediation when a specialist exists
- Gaps in the specialist roster become visible automatically: a recurring finding class without a matching specialist triggers authoring a new one, so the specialist catalog grows in step with observed failure modes
- The audit-to-fix-to-next-audit loop is an explicit, permanent cycle whose throughput can be observed in PR history, not an ad-hoc reaction to individual problems
- Every remediation PR explicitly names which specialist produced the fix (or records that none existed) so portfolio-level coverage gaps are discoverable from merged history alone

## Non-Goals
- Internal mechanics of any individual audit: `spec-drift-audit`, `project-structure-apply`, `vocab-drift-audit`, `workflow-health`, and equivalents remain authoritative for their own scope and triggers
- Authoring standards for skills and agents: `skill-management` and `agent-management` remain authoritative
- Pull-request gating, branch protection, and merge rules: `pull-request-workflow` and `branching-model` remain authoritative; this spec flows through those gates, it doesn't replace them
- Release cadence, sprint rituals, or project-management practices defined by `sprint`, `feature`, `release-artifact`, or `roadmap`: this spec is event-driven (audit outcome) and calendar-driven (quarterly review); it runs in parallel to those sprint-side cadences and neither replaces nor is replaced by them
- Mandating a specific agent for a specific finding class—the dispatching Claude selects the match from the available specialist catalog at the time of dispatch, and the catalog itself is expected to evolve
- Replacing the `workflow-health` specialized-agent-dispatch rules—this spec generalizes the same pattern to non-workflow findings; `workflow-health` remains the authority for workflow-scoped remediation

## Requirements

### Finding sources in scope
- **MUST** treat as a "finding" subject to this spec any `fail`, `blocked`, or equivalent negative outcome produced by a portfolio audit, including at least:
  - a `spec-drift-audit` per-criterion `fail` result
  - a `workflow-health` triage classification of `defect`, `stale pin`, or `secret / credential drift`
  - a `project-structure-apply` reconciliation gap (missing or diverging artifact)
  - a `vocab-drift-audit` report of locally-added entries that are already upstream, or local entries that should be PR'd upstream
  - a `portfolio-inflight-triage` Findings-Report entry of `Critical` or `Warning` severity per `spec/portfolio/portfolio-inflight-management/` §Findings-Report shape
  - a `portfolio-audit` Findings-Report entry of `Critical` or `Warning` severity per `spec/portfolio/portfolio-management/`
  - a `dependency-audit` `critical` or `high` finding per `spec/project/dependency-audit/`
  - a `prose-style` or `markdown-formatting` lint failure on a tracked file
  - any manual review finding recorded as a GitHub Issue, commit note, or audit artifact
- **MUST** also cover ad-hoc findings discovered outside a scheduled audit (a contributor notices drift during unrelated work) once they're captured as a GitHub Issue or tracked remediation PR—capture is the trigger, not the original audit source
- **MAY** exclude findings that are already closed by a merged fix at the moment the finding would be logged; such self-healed drift doesn't need a dispatch decision

### Specialist dispatch (generalization of `workflow-health`)
- **MUST** dispatch the hands-on remediation work of every in-scope finding to the most specialized available Claude Agent or skill whose `description` matches the finding class, via `Agent(subagent_type=<name>)` (per `agent-management`) or via a matching skill invocation (per `skill-management`); the dispatching Claude chooses from the catalog that exists at the time of dispatch
- **MUST NOT** have the dispatching Claude perform specialist remediation work itself when a matching specialist exists; the generalist triages, dispatches, and verifies, and **MAY** additionally coordinate multi-step chains—it doesn't replace the specialist
- **MAY** chain multiple specialists in sequence when one remediation crosses responsibilities, for example `spec` skill to amend a spec, then `pull-request-create` skill to open the fix PR, then `review` skill for a second-pass review; each specialist in the chain obeys its own declared tool scope and its own spec
- **MUST NOT** permit a dispatched specialist to bypass any gate from `pull-request-workflow`, `branching-model`, or any other spec; specialists ship their change through the standard PR flow, with all required checks green and no admin override
- **SHOULD** prefer a plugin-distributed specialist (`distribution: plugin` per `agent-management`, or a skill shipped via the `nolte-shared` plugin per `skill-management`) over a project-local one, so the remediation expertise travels with the plugin rather than being duplicated per repository

### Portfolio gap closure (the loop stays alive)
- **MUST** treat any finding class that has been handled by a generalist **three or more times** without a matching specialist as a portfolio gap requiring action: either author a new agent per `agent-management` or a new skill per `skill-management`, or extend an existing specialist's `description` so future findings of the same class route to it automatically
- **MAY** propose the creation of a new specialist **before** the three-recurrence threshold is reached when the finding class is obviously high-impact—security, release-blocker, or correctness regression—so urgency of impact is a legitimate reason to act early; the hard MUST trigger stays at three recurrences, and the early-creation path **MUST** record the high-impact justification in the authoring PR so it isn't used to bypass the recurrence-based discipline
- **SHOULD** track finding classes with **one or two** generalist-handled recurrences as candidates for the same treatment, so the portfolio reacts before the threshold is reached rather than only at it
- **SHOULD** prefer extending an existing specialist's `description` over authoring a new one when the finding class is a near-neighbour of an existing responsibility, so the specialist catalog stays focused rather than fragmenting
- **MUST** plugin-distribute any specialist that gap closure creates in response to a finding class observed in **two or more repositories** of the portfolio: a new agent **MUST** declare `distribution: plugin` (per `agent-management`) and a new skill **MUST** be shipped via the `nolte-shared` plugin (per `skill-management`); a project-local specialist isn't an acceptable closure in the cross-repository case
- **MAY** keep a newly created specialist as project-local (`distribution: project` for agents, project-local skill for skills) when the finding class is confined to a single repository; if the same class is later observed in a second repository, the cross-repository rule above applies and the specialist **MUST** be promoted to plugin distribution as its own, separately recorded closure decision—existing project-local specialists aren't retroactively relabelled until that second-repository observation triggers the promotion
- **MUST** document the gap-closure decision (new specialist authored / existing specialist extended / specialist promoted from project-local to plugin / decision deferred with reason) in the triggering finding's remediation PR or in a linked follow-up PR, so the closure is traceable from the finding that caused it

### Traceability in remediation artifacts
- **MUST** record in the **Risk / rollout notes** section of every remediation PR (per `pull-request-workflow`) either the specialized agent or skill that produced the fix, or an explicit note that no matching specialist existed and a generalist handled it—this is the primary signal for portfolio-level coverage gaps
- **MUST** name the originating finding source (`spec-drift-audit` entry, `workflow-health` incident, `project-structure-apply` report, manual review Issue, etc.) in the same section, so the PR is traceable back to the audit entry that triggered it
- **MUST NOT** collapse multiple unrelated findings into a single remediation PR merely to reduce paperwork; one PR per finding class keeps the dispatch record meaningful, and related findings of the same class **MAY** still be grouped when the fix is genuinely atomic

### Continuous loop and quarterly coverage review
- **MUST** treat audit → finding → specialist remediation → merged fix → next audit as a closed loop that runs permanently; the loop cadence is the union of the cadences declared by the in-scope audit specs (quarterly for `spec-drift-audit`, continuous for `workflow-health`, event-driven for `project-structure-apply` and `vocab-drift-audit`)
- **MUST** perform a **specialist-coverage review** at least once per calendar quarter: scan the last quarter's merged remediation PRs, identify finding classes that were generalist-handled, and check each against the gap-closure rule above; the review outcome **MUST** be recorded in the same artifact form the repository uses for `spec-drift-audit` results (commit, Issue, or audit file)
- **SHOULD** fold the specialist-coverage review into the quarterly `spec-drift-audit` run by default, to reduce ritual cost and keep both quarterly cadences in one artifact
- **MAY** keep the specialist-coverage review as a standalone artifact when the repository consciously prefers that separation—for example to keep a clean cross-quarter history of specialist coverage alone—provided the quarterly-cadence rule above still holds
- **MUST**, when the coverage review is folded into the drift-audit artifact, present it as a named, dedicated section (for example `## Specialist coverage review`) rather than merging it into the drift-audit narrative, so the review remains findable by name in the artifact and in the repository's audit history
- **MUST** keep the specialist-coverage review at **full portfolio scope** even when the hosting `spec-drift-audit` run is narrowed to a thematic partial audit; partial-audit narrowing applies to drift, not to coverage, and a narrowed drift audit that suppresses the quarterly coverage review is itself a finding under this spec for the next audit
- **MUST NOT** silently defer an in-scope finding past the response window declared by its originating audit spec; the response-window rules of `spec-drift-audit` and `workflow-health` apply transitively under this spec, and missed windows are themselves a finding under the next audit

### Relationship to existing specs
- **MUST** treat `spec-drift-audit` as the authority for audit scope, triggers, and feedback-loop decisions; this spec extends, it doesn't override
- **MUST** treat `workflow-health`'s "Specialized-agent dispatch for remediation" as the canonical pattern this spec generalizes; the workflow-scoped rules there remain binding in their scope, and identical rules (not weaker ones) apply to other finding sources under this spec
- **MUST** treat `agent-management` and `skill-management` as the authority for authoring new specialists when gap closure demands it; this spec triggers the authoring, it doesn't prescribe the shape
- **MUST** treat the sibling specs `sprint`, `feature`, `release-artifact`, and `roadmap` as parallel cadences that **MUST NOT** substitute the quarterly coverage review or audit-driven dispatch defined here: sprint-review is per-sprint closure with a value-delivery gate, not a portfolio-coverage review, and a successfully closed sprint doesn't satisfy this spec's quarterly review; conversely, this spec's findings **MUST NOT** be folded into a sprint's `## Review notes` as a substitute for the audit-side artifact form mandated above. Cross-references between the two layers are documentation; both cadences remain independently mandatory
- **MUST NOT** be used as justification to weaken any other spec—a finding whose remediation would require violating another spec is an Open Question, not a shortcut

## Acceptance Criteria
- [ ] For the last 10 merged remediation PRs across the repository that addressed an in-scope audit finding, the **Risk / rollout notes** section names either the dispatched specialist (agent or skill) or explicitly records that no matching specialist existed and a generalist handled it
- [ ] For the same 10 PRs, the **Risk / rollout notes** section names the originating finding source (audit entry, workflow incident, project-structure report, manual review Issue, etc.), so each PR is traceable back to its trigger
- [ ] No in-scope finding from the most recent `spec-drift-audit` run is recorded as "no specialist considered"—each has either a dispatched specialist or an explicit "no matching specialist exists" note
- [ ] For every finding class that has been generalist-handled three or more times in the last two calendar quarters, either a specialist now exists in the portfolio (agent per `agent-management` or skill per `skill-management`) or an open Issue tracks its creation with a named owner
- [ ] The repository contains at least one recorded specialist-coverage review per calendar quarter since this spec was introduced, either as a standalone artifact or as a distinct section inside the quarterly `spec-drift-audit` artifact
- [ ] No merged remediation PR for an in-scope finding shows a branch-protection override, an `enforce_admins: false` exception, or a required-check bypass—the standard PR gate was used in every case
- [ ] When the same finding class has been routed to multiple specialists across different PRs, a portfolio-level decision (consolidate on one specialist / extend one specialist's `description` / keep both with a documented split) has been recorded rather than leaving the routing ambiguous
- [ ] Every remediation PR whose finding originated outside a scheduled audit (ad-hoc contributor observation) links the capturing Issue or note, so ad-hoc findings are treated with the same traceability as scheduled ones
- [ ] Every specialist created before the three-recurrence threshold records in its authoring PR an explicit high-impact justification (security, release-blocker, correctness regression); no pre-threshold specialist exists without such a note
- [ ] When the quarterly specialist-coverage review is folded into the `spec-drift-audit` artifact, that artifact contains a section whose heading identifies it as the coverage review (for example `## Specialist coverage review`); when kept standalone, at least one coverage-review artifact exists per calendar quarter since this spec was introduced
- [ ] No thematically partial `spec-drift-audit` run suppresses the quarterly specialist-coverage review—for every calendar quarter, either the (partial or full) drift-audit artifact carries the full-scope coverage-review section, or a separate full-scope coverage-review artifact exists for the same quarter
- [ ] Every specialist created or promoted in response to a finding class observed in two or more repositories of the portfolio declares plugin distribution (`distribution: plugin` for agents, shipped via the `nolte-shared` plugin for skills); no such cross-repository gap closure has resulted in a project-local specialist
- [ ] Every specialist-promotion decision (project-local → plugin-distributed, triggered by a second repository observing the same finding class) is recorded in the triggering finding's remediation PR or a linked follow-up PR, naming the triggering cross-repository observation

## Open Questions
- _None at this time; all drafting questions have been resolved._
