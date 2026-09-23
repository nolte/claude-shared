# Capability Reach Audit

Status: draft

## Context

Over two days of measured issue work in one repository, five defects of a single shape were found. None of them was being looked for. Each surfaced as a side effect of unrelated work: a documentation repair, a CVE pin, a security question, a query fix.

| Capability | Declared | Actually reached |
|---|---|---|
| Data export | 15 collections and 8 edges | 0 |
| Erasure finalisation | erase or redact 26 collections | 0 deleted, 0 redacted |
| Ranking service | a working ranking endpoint | `/ready` answers 503 forever while `HEALTHCHECK` reports healthy |
| On-demand scan lane | scan on demand | 0 of 300 `pull_request` runs executed |
| Personal-data inventory | one enumeration | two declared inventories, and the maintained one isn't the executing one |

Earlier instances from the same repository: a permission helper specified and wired nowhere, several guards implemented and inert, and a guard disarmed by its own allowlist entry.

The common shape isn't unfinished work. It's an artefact that exists, type-checks, carries tests, and reports success, while reaching none of the scope it declares. Every instance passed code review. Several passed a green continuous-integration gate. Line coverage was high in all of them.

The cost isn't only the defects. It's that finding them is a function of what somebody happened to touch, so coverage is accidental.

That repository previously carried a static audit layer, and it was removed because it counted scaffolds as complete. That's the same failure: it asked whether the artefact exists and got the wrong answer to the only question that mattered. This spec exists because the question has to be answered by execution instead, and §"Why this doesn't repeat the removed audit layer" states what makes the difference structural rather than a matter of care.

## Goals

- Establish, per declared capability, whether the executing path reaches the scope the capability declares, by running something rather than by reading something.
- Replace accidental coverage with a deliberate, enumerable audited set.
- Make the audit's own blind spots a reported number rather than a silence.
- Make the second run a diff, so the audit stays cheap enough to repeat.

## Non-Goals

- Not a replacement for `spec/project/capability-maturity-assessment/`. That grades quality on three axes. This establishes one fact that the grading currently takes on trust.
- Not a merge gate. This is a periodic, whole-system measurement. A class it uncovers becomes a guard under `spec/project/defect-class-guards/`; the audit itself blocks nothing.
- Not a test suite. It doesn't assert that behaviour is correct, only that behaviour occurs at all.
- Not a coverage metric. Line coverage was high in every defect above.
- Not a specification of the executor. This spec says what an audit must establish and report, not how a skill or agent implements it.

## Requirements

### The audited set

- **MUST** derive the audited set from what the project **declares it does**, drawn from four declaration sources, each of which carries its own probe shape:
  1. a **requirement document**, including a specification, a feature record, or a regulatory article the project claims to satisfy;
  2. a **specified endpoint**, including an API contract, a documented route, a scheduled job, or a workflow trigger;
  3. a **documented capability**, including a README claim, a published page, or a skill or agent description;
  4. a **declared inventory**, meaning an enumeration the project maintains about itself, such as a personal-data inventory, a collection list, or a registry of supported providers.
- **MUST NOT** derive the audited set from what the source tree happens to contain. An inventory built from the code can't contain a capability the code never implemented, which is the most important case.
- **MUST** report a capability that's declared and wholly absent as the most severe class of finding, never as a gap in the inventory.
- **MUST** record, per entry, the declaration source and the exact `file:line` or document location that declared it, so a reader can dispute the entry rather than the verdict.

### The probe

- **MUST** define, per entry, an observation that distinguishes **reached** from **not reached**, and that observation **MUST** be produced by executing something: a request and its response body, a container that becomes ready and answers, a file the export actually wrote, rows a deletion actually removed, a platform's record of runs that actually happened.
- **MUST** place the observation point **outside the artefact under audit**. This is the load-bearing rule of this spec, and every defect in §Context defeats an audit that ignores it. The evidence is the archive the export produced, not the status field the export set. It's the rows remaining in the database, not the value the erasure returned. It's the body of a ranking response, not the container's own health report.
- **MUST** record the probe's **actual output** as the evidence. A recorded pass whose probe never ran reads as evidence and is worse than no record at all.
- **MUST NOT** accept a self-reported success as a measurement of reach. Each of the following was, in one of the defects above, exactly the signal that lied: a status field reading `completed`, an HTTP 2xx, a green build, a passing `HEALTHCHECK`, a zero exit code on its own, and a log line the artefact writes about itself.
- **MUST NOT** let the presence of the artefact contribute to reach. A scaffold scores zero because its probe observes nothing, not because a marker was found in it. No defect in §Context carries an unimplemented marker, a `TODO`, a stub return, or a feature flag.
- **MUST** report an entry for which no probe can be constructed at any tier as **not probed**, never as reached and never by dropping it from the set, and **MUST** record the reason no probe could be constructed. Without this the classification exists only in prose, and an implementor has no rule forcing it.
- **SHOULD** express the expected observation as a count or a set where the declaration is itself a count or a set, because `0 of 15 collections` is a finding and `the export ran` isn't.

### Environment tiers

- **MUST** declare exactly one environment tier per probe:
  - **T0**, no environment: the probe runs against a record or an interface that already exists, such as a platform's run history or a published artefact.
  - **T1**, one ephemeral dependency: the probe stands up a container or a temporary service and observes it.
  - **T2**, full stack with seeded data: the probe needs a running system holding data it placed there.
- **MUST** report reach **per tier**, plus the not probed remainder, so that running only the cheap tiers is visible in the output rather than indistinguishable from a clean result.
- **MUST NOT** let a lower tier stand in for a higher one. When a capability's declared scope can only be observed at T2, a T0 probe for it counts as **not probed**, never as passed. Without this rule the tiering becomes a way to report a green audit that measured nothing, which is the failure this spec exists to prevent.
- **MUST** treat T0 as execution, not as static reading. Querying a platform for which runs actually executed is an observation of an effect. Reading the workflow file that was supposed to cause them isn't, and the on-demand scan lane in §Context is exactly that distinction. T0 establishes that something ran, never that it works, so a T0 result alone never ratifies correctness.

### Derivation, approval, and durability

- **MUST** derive candidate probes from the declaration, present them for operator approval, and persist the approved set as a **versioned artefact under version control**.
- **MUST** execute the stored probes on every later run rather than re-deriving them. Re-derivation is what makes the first run expensive; execution is what makes the second run a diff.
- **MUST** re-derive a probe when its declaration changes, and **MUST** detect that change rather than waiting for somebody to notice. A probe still passing against a declaration that has moved is a false pass.
- **MUST** make the **probe set** the durable deliverable. The report is regenerated by executing it, and is never itself the artefact that's maintained.
- **MUST** report, per run, which probes changed since the previous run and in which change. A probe weakened since the declaration it checks last changed **MUST** be surfaced as a finding rather than accepted, whether or not both changed together. Restricting this to a single change would miss a weakening split across two, which is the ordinary shape rather than the exotic one. The probe set lives in the audited repository so it's reviewable alongside the change that invalidates it, which also makes it editable by that change: that's the shape which disarmed a guard through its own allowlist entry, and this rule is what keeps co-location safe rather than merely convenient.
- **MUST** carry, per report entry, the timestamp at which that probe last executed. A report quoted after it stopped being true is then visibly stale, which is the concrete answer to the removed audit layer whose deliverable was a document.

### Reporting

- **MUST** classify every entry into exactly one of: **reached**, **partially reached**, **not reached**, **not probed**.
- **MUST** express reach as a **ratio with the measurement that produced it**, such as `0/15 collections, measured by <command>`. A grade isn't actionable, and a bare verdict hides whether anybody looked.
- **MUST NOT** emit a tier or a grade as the primary output. Grading **MAY** consume this audit's result; it never replaces it.
- **MUST** lead the report with the **not probed count**. That number is the honest measure of the audit's own coverage, and burying it turns an audit that measured a third of the surface into one that looks complete.
- **MUST** state the audited set's provenance: which declaration sources were read, which were unavailable, and what the audit therefore can't speak about.

### Delimitation

The audit is defined as much by what already exists as by what it adds. Each row names the reason the neighbouring spec can't answer this question.

| Spec | What it does | Why it doesn't establish reach |
|---|---|---|
| `spec/project/capability-maturity-assessment/` | Grades completeness, quality, and test depth | Its Axis A is a judgement input by design, and its scanner surfaces markers. No defect in §Context carries a marker; each has a docstring, a plausible signature, passing tests, and a normal return. |
| `spec/project/quality-gate/` | A local or invocable pre-check that mirrors what CI runs over the fast tiers | Four of the five defects shipped through those checks while they were green. Its own non-goals say it doesn't replace CI and that CI stays the source of truth for merge protection, so it doesn't claim to be the gate either. |
| `spec/project/spec-drift-audit/` | Reconciles specification against implementation | It reads both. That catches a spec naming a config key that doesn't exist; it doesn't catch a function whose body reaches nothing. |
| `spec/project/defect-class-guards/` | Refuses a defect class once the class is named | Reactive by construction. It's the right answer after a finding, and it can't produce coverage. |
| `spec/project/test-falsifiability/` | Asks whether a test proves what it claims | Necessary, and it settled several of these once somebody looked. It doesn't say where to look. |
| `spec/project/gdpr-audit-process/` | Audits one domain end to end | Strictly read-only by its own §"Read-only contract" section, and its code-verifiable class means confirmed from the repository. Two defects in §Context sit in its domain and it didn't find them. This audit sits **beside** it with the opposite mechanism, and borrows its honesty boundary: exactly one class per finding, and an unverifiable item is never reported as a pass. |

## Worked acceptance: The five defects

A reader **MUST** be able to answer, for each defect in §Context, whether this audit finds it and by which measurement. The table is the acceptance test of this spec, and each row names the probe rather than the verdict.

| Defect | Declaration source | Probe, and the observation point outside the artefact | Tier | Measurement |
|---|---|---|---|---|
| Data export reaches 0 collections | requirement document (right of access) | Export for a seeded subject, then open the produced archive and count the **records per collection**, comparing each against what was seeded. Counting the collections present would measure presence again, and an export writing 15 empty files would pass. Not the job's status field. | T2 | `0/15 collections, 0/8 edges` |
| Erasure finalisation deletes nothing | requirement document (right to erasure) | Seed a subject across all 26 collections, run erasure, then count rows still matching the subject and rows whose values changed. Not the recorded `status`. | T2 | `0/26 erased, 0/26 redacted` |
| Ranking service never becomes ready | documented capability | Start the container, then poll the ranking endpoint itself with a timeout to decide when to fire, never either status signal. Post two requests whose correct orderings differ and assert the response bodies differ accordingly; a constant answer must fail, or a stub would pass. Not `HEALTHCHECK`, and not `/ready`, which disagreed with each other. | T1 | `0/1 endpoints answer` |
| Scan lane never executes | specified endpoint (workflow trigger) | Query the platform for executions of that job across the last 300 events of its declared trigger. Not the workflow file that declares the trigger. | T0 | `0/300 runs executed` |
| Two personal-data inventories, one executing | declared inventory | Execute the enumeration the code actually calls and capture what it returns, then diff that against each declared inventory. | T2 | `1 of 2 declared inventories matches the executing one` |

Every row observes an effect the capability's declared scope entails, at a place the capability doesn't itself author. Any spec derived from this one that can't fill this table for all five rows hasn't addressed the requirement.

## Why this doesn't repeat the removed audit layer

The removed layer counted scaffolds as complete because existence was its unit of measurement. Three rules here make that outcome unreachable rather than merely discouraged:

1. **Presence contributes nothing.** Reach is a function of an observed effect only, so a scaffold scores zero by construction. There's no path by which an artefact's existence raises its number.
2. **The observation point lies outside the artefact.** Every self-report the artefact can emit is excluded by name, so an artefact can't pass its own audit by claiming to have worked.
3. **Not looking is a reported number, not a silence.** §"The probe" requires an entry with no constructible probe at any tier to be reported `not probed` with its reason, and §Reporting requires that count to lead the report, so an audit that measured little can't read as an audit that found little.

The removed layer failed on all three. It measured presence, it trusted the artefact's own surface, and a capability it couldn't assess simply didn't lower its percentage.

## Acceptance Criteria

- [ ] The audited set is built from the four declaration sources, and each entry names the source and the location that declared it.
- [ ] A capability that's declared and wholly absent appears as the most severe class, not as a missing entry.
- [ ] Every entry carries a probe whose output was produced by execution, and the report records that output rather than an assertion about it.
- [ ] No entry's verdict rests on a status field, an HTTP 2xx, a green build, a `HEALTHCHECK`, an exit code alone, or a log line the artefact writes about itself.
- [ ] Every probe declares exactly one of T0, T1, T2, and a capability observable only at a higher tier is reported `not probed` when probed at a lower one.
- [ ] An entry with no constructible probe at any tier appears as `not probed` with the reason recorded, and counts toward the headline.
- [ ] A run reports which probes changed since the previous run, and a probe weakened since its declaration last changed is surfaced rather than accepted, whether or not both changed together.
- [ ] The report leads with the not probed count and states the audited set's provenance.
- [ ] Reach is expressed as a ratio with the command that produced it; no grade appears as the primary output.
- [ ] The probe set is under version control, later runs execute it rather than re-derive it, and each report entry carries its probe's execution timestamp.
- [ ] A declaration that changed since its probe was approved is detected, and its probe is re-derived rather than re-run.
- [ ] The §"Worked acceptance: The five defects" table answers, for all five defects, both whether the audit finds it and by which measurement.

## Open Questions

- **What bounds the cost of T2?** A full stack with seeded data is the tier that catches the most severe defects and the tier most likely to be skipped. Whether the bound is a time budget, a sampled subset of entries, or a slower cadence for T2 alone is unsettled.
- **What probes a capability whose effect is external?** When the declared effect lands in a third-party system, the observation point outside the artefact may be unreachable in an audit environment. Such an entry is `not probed` today, which is honest but may be a large share of the set.
- **What cadence keeps the set current without re-deriving it?** The spec requires detecting a changed declaration, and doesn't yet say how often that detection runs.

## Sources

- The five defects and the removed static audit layer: `nolte/kamerplanter#1645`, `#1609`, `#1607`, `#1622`, `#1614`, recorded in `nolte/claude-shared#660`.
- Axis A as a judgement input: the §"Machine-derivable vs. judgement inputs" section of `spec/project/capability-maturity-assessment/en.md`.
- The read-only contract and the verifiability boundary this spec borrows: the §"Read-only contract" and §"Code-verifiable versus legal-review boundary" sections of `spec/project/gdpr-audit-process/en.md`.
- Severity vocabulary: the §"Severity scale" section of `spec/claude/review-plan/`.
