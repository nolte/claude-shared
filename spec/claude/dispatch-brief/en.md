# Dispatch Brief

Status: draft
Portfolio-Scope: portfolio

## Context

When a skill dispatches analysis or remediation to a specialist, it composes a **dispatch brief**: the problem statement, the scope, and often a *hypothesis* about what's wrong, why, or how to fix it. A brief that carries a hypothesis states the best guess the orchestrator has, while the specialist has the code, the artefact, or the evidence in front of it. When the guess is wrong and the brief doesn't say so, the specialist optimises for completing the stated task, which is the correct default. A wrong hypothesis then silently becomes a wrong fix that a later run has to re-diagnose.

A full-suite E2E stabilization campaign (`nolte/kamerplanter#768`) made the cost concrete: dispatched specialists corrected the brief they were given roughly ten times, and the corrections were substantive rather than cosmetic. A stated root cause that didn't hold for the installed library version. A "give X the same constraints as Y" instruction that was a no-op because Y had no such constraints either. A `minWidth: 0` fix that would have reintroduced the defect it was meant to cure. Each correction came from one explicit sentence in the dispatch: *if the evidence contradicts this, say so and change nothing rather than forcing the fix to fit.*

That rule first lived in `spec/project/e2e-failure-diagnosis/` §E, but it isn't E2E-specific. It applies to every skill that dispatches analysis or remediation with a stated hypothesis: `issue-orchestrate`, `workflow-health-triage`, `source-code-review`, `dependency-audit`, `observability-audit`, the test-tier reviewers, and the security reviewers. `spec/claude/` already owns the cross-cutting agent and skill conventions (`agent-management`, `skill-management`, `skill-vs-agent`); a brief-composition convention belongs here too. This spec owns the refutation rule portfolio-wide so that domain specs and dispatching skills reference it instead of each restating it.

## Goals

- Make refutation authorisation a **routine, checkable property** of every hypothesis-bearing dispatch brief, rather than a habit the orchestrator has to remember.
- Specify the **shape of a valid refutation** so a refutation is actionable, not a bare "I disagree."
- Give the rule a **stable, citable home** that domain specs (`e2e-failure-diagnosis`) and dispatching skills point at instead of duplicating.

## Non-Goals

- Governing the rest of a dispatch brief's content (problem statement, scope, acceptance criteria); this spec governs only the refutation clause and its deliverable shape.
- The skill-versus-agent format choice for a capability; that stays with `spec/claude/skill-vs-agent/`.
- The routing and dispatch mechanics of the Claude Code runtime itself; this spec governs how a brief is composed, not how the runtime delivers it.

## Requirements

- A **hypothesis-bearing brief** is a dispatch brief that asserts a *cause*, a *mechanism*, or a *remediation shape*: any claim the receiving specialist could confirm or refute against the evidence in front of it. A brief that only scopes a detection task ("scan this surface and report findings") without asserting a cause or a fix isn't hypothesis-bearing.
- A hypothesis-bearing brief **MUST** state its hypothesis *and* explicitly authorise and expect the specialist to refute it. The authorisation **MUST** be explicit in the brief, not left implicit; the canonical form is: *if the evidence contradicts this, say so and change nothing rather than forcing the fix to fit.*
- The brief **MUST** frame a refutation as a **valid, expected deliverable**, not as a failure to complete the task. A specialist that returns a refutation with its evidence has completed its dispatch.
- A refutation **MUST** contain both:
  1. **The evidence that contradicts the brief.** A concrete anchor a reviewer can check: a `file:line`, or a command and the output that settles it. A bare "I disagree" or an unanchored assertion is non-conformant.
  2. **What the specialist did instead.** Exactly one of: changed nothing, applied a narrower fix (only the part with a real gap), or applied a different fix. The specialist **MUST NOT** invent bounds, constraints, or scope the evidence doesn't support merely to satisfy the brief.
- The orchestrator **MUST** treat a returned refutation as a first-class outcome: record it in the run's audit trail, and reconcile the hypothesis against it before dispatching any dependent work. It **MUST NOT** silently discard a refutation to preserve the original hypothesis.
- A hypothesis-bearing brief that omits the refutation authorisation **is a defect**. A reviewer can check a brief against this rule by asking whether it asserts a cause, a mechanism, or a remediation, and if so whether it authorises refutation in the deliverable shape above.
- A non-hypothesis brief (pure detection or scoping) **MAY** carry the clause but isn't required to; the rule binds where a claim exists to be refuted.
- A domain or scope-specific spec that needs this rule **MUST** cross-reference this spec rather than restate the rule's body, and **MAY** add only its scope-specific application (for example, which evidence channels a brief must carry).

## Acceptance Criteria

- [ ] The rule lives in this cross-cutting spec under `spec/claude/`, not in a domain spec.
- [ ] "Hypothesis-bearing brief" is defined so a reviewer can decide whether a given brief is in scope.
- [ ] The refutation authorisation is stated as a `MUST` a reviewer can check against an actual brief.
- [ ] The shape of a valid refutation is specified: contradicting evidence (a `file:line` or a command with output) **and** what was done instead (nothing, a narrower fix, or a different fix).
- [ ] Framing a refutation as an expected deliverable (not a task failure) is required.
- [ ] The obligation on the orchestrator to record and reconcile a refutation is stated.
- [ ] `e2e-failure-diagnosis` cross-references this spec instead of carrying its own copy of the rule.
- [ ] The dispatching skills that state hypotheses reference this spec.

## References

- [R1] The E2E-scoped application this rule was lifted from, which now cross-references here: `spec/project/e2e-failure-diagnosis/` §E and §Binding into agents and skills.
- [R2] The highest-volume hypothesis-bearing dispatcher, whose pre-analysis brief carries a decomposition hypothesis per work package: `spec/project/issue-orchestration/`.
- [R3] Conflict handling when independent channels disagree (compose, don't vote; stop-and-surface): `spec/claude/research-triangulate/`.
- [R4] The skill-orchestrates-agent-executes pattern whose dispatch step this rule governs: `spec/claude/skill-vs-agent/`.
- [R5] The agent-authoring conventions this brief convention sits alongside: `spec/claude/agent-management/`.
- [R6] The source work order and campaign evidence: issue #528, derived from `nolte/kamerplanter#768` (filed here as #514).

## Open Questions

- None load-bearing. The precise set of dispatching skills that assert hypotheses is maintained at the skills that reference this spec, not frozen here; a new hypothesis-bearing dispatcher inherits the rule by definition.
