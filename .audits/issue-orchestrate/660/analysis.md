# Pre-analysis: nolte/claude-shared#660

status: awaiting-approval
classification: spec-change
route: implement directly
run: 20260921T150000Z-cra1

## Issue

"Requirement: an audit that establishes what a capability DOES by executing it, not
what it looks like by reading it." Author `nolte`, the repository owner, so the body is
trusted input per `spec/claude/trusted-author-injection-guard/`.

## Classification and its rationale

`spec-change`. The acceptance criterion is literally "a draft spec under `spec/project/`
that a reader can use to answer, for the five defects in the table above: would this
audit have found it, and by what measurement?" Confirmed with the operator, as the
class requires.

Secondary class `feature-request`: the spec implies a skill. That skill is deliberately
**out of scope** here and becomes its own issue, so this run stays one PR strand.

## Requirements gate

No artefact for this issue exists under `project/requirements/` — established by listing
that directory; the only audit-named entries are `dockerfile-audit.md` and
`observability-audit-tooling.md`. **Operator override recorded** rather than dispatching
`requirements-elicit`: the issue already carries six MUST-level behaviours, explicit
non-goals, and a falsifiable acceptance criterion. What was missing was not the
requirements but the five design decisions the issue itself names, and those were taken
at the gate below.

## Decisions taken at the operator gate

| # | Question | Decision |
|---|---|---|
| D1 | Unit of audit | Four declaration sources: requirement document, specified endpoint, documented capability, declared inventory. Each carries its own probe shape. Chosen because the five defects in the issue's table distribute across exactly those four. |
| D2 | Environment a probe may assume | Tiered. Every probe declares its tier: no environment, ephemeral container, full stack with seeded data. The report states reach per tier, so running only the cheap tier shows up as unprobed remainder rather than as a pass. |
| D3 | Who derives the probe | The skill derives it from the declaration, the operator approves it at a gate, and it then persists as a versioned artefact. Later runs execute the stored probes instead of re-deriving them, which is what turns run two into a diff. |
| D4 | Where the output lives, and what stops drift | The durable artefact is the **probe set**, not the report. A later run executes the probes and regenerates the report, so a quoted report is visibly stale because it lacks current execution timestamps. This is the direct answer to the removed audit layer, whose deliverable was a document. |

## Measured findings that shape the spec

- **The issue's quotation of the maturity spec is exact.** `spec/project/capability-maturity-assessment/en.md:72` says the scanner "**MAY** surface signals … but **MUST NOT** assign the Axis A tier". Read, not inferred.
- **`gdpr-audit-process` is strictly read-only.** Its §"Read-only contract" declares only `Read`, `Grep`, `Glob` and forbids `Edit`/`Write`. Its "code-verifiable" class means confirmed or refuted *from the repository*. So the new audit is **beside** it, not a generalisation of it: the verification mechanism is the opposite one. This answers the issue's open question 5 by measurement.
- **What the new spec should borrow from it** is its honesty boundary. `gdpr-audit-process` forces every finding into exactly one of code-verifiable or legal-review-required and forbids reporting the latter as a pass. That is structurally the issue's requirement 5 about `unprobed`, and reusing the shape keeps the portfolio consistent.
- **Two of the five defects sit in the GDPR domain** that a read-only audit already covers, and it did not find them. That is the strongest available evidence for the requirement, and it comes from the issue's own table rather than from a new claim.

## Scope

**In scope**: one bilingual spec at `spec/project/capability-reach-audit/{en,de}.md`, the
cross-references that make it reachable from the specs it delimits against, and the
regenerated `spec/README.md` row.

**Out of scope**: the skill or agent that executes the audit; any probe implementation;
any change to the five specs' own rules beyond adding a pointer.

**Slug**: `capability-reach-audit`. No collision — `ls spec/project/` shows
`capability-maturity-assessment`, `code-security-audit`, `dependency-audit`,
`gdpr-audit-process`, `spec-drift-audit`, and no `reach` entry. The name is chosen to
keep it distinct from the maturity spec, which grades, where this one measures reach.

## Work packages

| id | Problem | Acceptance | Files | Specialist | Depends on |
|---|---|---|---|---|---|
| P1 | Author the canonical spec carrying D1–D4, the six MUST behaviours, the non-goals, and the delimitation against the five named specs | The spec answers, for each of the five defects, whether the audit finds it and by which probe; EN and DE structurally identical | `spec/project/capability-reach-audit/{en,de}.md`, `spec/README.md` | skill: `nolte-shared:spec` | — |
| P2 | Make the new spec reachable from the specs it delimits against | `capability-maturity-assessment`, `defect-class-guards` and `gdpr-audit-process` each carry one pointer naming what the new spec does that they do not | those three specs, both languages | skill: `nolte-shared:spec` | P1 |
| P3 | Independent readiness review and repair | No Critical finding remains; the five-defect table survives an adversarial read | draft under review | agent: `nolte-shared:spec-readiness-reviewer` | P1, P2 |

**Ordering**: P1 → P2 → P3, strictly sequential. P2 cannot name a section of a spec that
does not exist yet, and P3 must read the finished pair.

## The failure mode this spec must not repeat

The issue records that a previous static audit layer was removed because it counted
scaffolds as complete. The spec is therefore required to state, in its own body, why it
does not repeat that — the operator's words: "Any skill built for this requirement must
be able to state why it would not repeat that." Carried into P1's acceptance as a named
section rather than left to the author's discretion.

## Risks

- **The five-defect table is the acceptance test and is easy to satisfy vaguely.** A spec
  can claim it would catch all five without naming a probe. P3 exists to attack exactly
  that, and P1's acceptance names the probe per defect, not the verdict per defect.
- **D2's tiering can become an excuse.** If every probe declares the cheapest tier, the
  audit degenerates into the static one it replaces. The spec must make the unprobed
  count a headline number, per the issue's requirement 5.
- **Scope creep into the skill.** The spec describes behaviour an executor must have; it
  must not start specifying the executor's implementation. The out-of-scope line above is
  the guard.

## Defect-class decision

Not a defect-closing run, so `spec/project/defect-class-guards/` G1 does not apply and the
PR carries no `## Class sweep`: the Conventional-Commits type is `feat`, and that section
is forbidden on any type but `fix`.
