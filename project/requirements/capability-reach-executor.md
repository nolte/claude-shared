# Requirements — Capability-reach-audit executor (skill + scanner agent)

<!--
Produced via the `requirements-elicit` skill, following
spec/project/requirements-elicitation/.
`c_d` is an uncertainty proxy (self-consistency-derived), not a calibrated
probability. A requirement is `confirmed` only after an explicit teach-back.
-->

## Bounded context

- **What is being built:** the executor for `spec/project/capability-reach-audit/`, which
  today has 26 requirements and nothing that runs them. Two coupled artefacts in the
  `nolte-engineering` plugin, following the shape of the four existing audits there
  (`observability-audit`, `dockerfile-audit`, `error-tracking-audit`, `api-documentation-audit`):
  1. a **skill** that derives candidate probes from a target repository's declarations,
     presents them for operator approval, persists the approved set into the target
     repository, executes the stored set on later runs, detects changed declarations and
     weakened probes, and renders the report;
  2. a read-only **scanner agent** that builds the declaration inventory (the audited set)
     and drafts candidate probes, returning them to the skill for the approval gate.
- **Key difference from the four precedents:** all four are stateless reporters. This
  executor owns a **durable, versioned probe set** in the audited repository and
  **executes** probes, including ones that stand up a container (T1) or a full stack
  with seeded data (T2). No existing audit in this repository does either.
- **For whom:** the operator, running locally, against a **local working copy** of any
  `nolte/*` repository. Read-only remote access is insufficient because two of the three
  tiers execute against the audited system.
- **Out of scope:** changing the governing spec; a merge gate or required check; a
  scheduled or unattended run; auditing a repository that is not checked out locally;
  the report as a maintained document (it is regenerated on every run).

## Understanding KPI

- Thresholds: `τ_low = 0.4`, `τ_high = 0.8`, self-consistency `k = 2`, question budget = `12`
  (spec defaults, not overridden)
- `U_gate = min_d c_d` over required dimensions = **0.80**
- Termination: `saturation` after 10 of 12 questions; no remaining question had an expected
  information gain that outweighed one more turn

### Gap matrix

| Dimension | Applicable | `c_d` | Uncertainty source | Evidence event |
|---|---|---|---|---|
| `functional` | yes | 0.85 | specification | Q3 (probe format chosen from three divergent sketches) + Q4a teach-back confirmed with one amendment (git history, not a stored hash) |
| `non_functional` | yes | 0.80 | specification | Q4b (T2 only on explicit opt-in); Q5a bounds environment runtime to what the target repository already declares |
| `constraints` | yes | 0.85 | specification | Q5a (environment via Taskfile targets); Q2 teach-back (local working copy required) |
| `domain_objects` | yes | 0.85 | interpretation | Q4a teach-back fixed the probe file's fields; Q6a fixed the on-disk paths; declaration sources come from the spec |
| `actors` | yes | 0.85 | specification | Q1 answer + Q2 teach-back confirmed |
| `acceptance_criteria` | yes | 0.85 | interpretation | Q5c teach-back: five issue criteria plus four interview criteria, with the T2 rows proven by a dogfooding run rather than a gate here |
| `edge_cases` | yes | 0.80 | specification | Q5b (external anchors); issue AC4 (no declarations); container start failure recorded `assumed` below |
| `scope_boundaries` | yes | 0.85 | specification | orchestration gate (all three tiers); Q6b (plugin placement); spec non-goals (not a merge gate) |

Self-consistency check that produced the lowest initial score: for `functional`, the two
independent sketches were a declarative probe file interpreted by a runner versus a generated
executable script per probe. They diverged on the one property the governing spec treats as
load-bearing, whether the artefact under audit can assert its own success, which set
`c_d = 0.35` and made the question mandatory.

## Requirements

### Probe format and lifecycle

- **R1** — The probe SHALL be a file with a declarative head and an observation step, where the
  head carries the probe id, the declaration anchor, the tier, the expected observation as a
  count or a set, and approval metadata, and the observation step emits **raw observation
  only**. The comparison that yields reached, partially reached, not reached, or not probed
  SHALL happen in the runner, never in the probe.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: "Deklarativer Kopf, Runner
    vergleicht" (Q3); teach-back Q4a "Ja, aber ohne Hash"
- **R2** — WHEN a probe is derived from a declaration file inside the target repository, the
  executor SHALL record that file's git blob hash (`derived_from: blob:<sha1>`), and SHALL
  detect a changed declaration by comparing the recorded blob against the file's content at
  HEAD. A commit recorded before this amendment stays valid and is compared through the
  repository's history as before.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: Q4a "Git-Historie reicht"
  - _amended 2026-09-25 by #668 (operator decision)_: the commit anchor could not survive the
    squash merge the portfolio mandates, so a probe re-derived in the same pull request as its
    declaration read `unresolved` after the merge; the blob is the content git already stores,
    not a separately maintained hash.
- **R3** — WHEN the probe file has changed since the commit that recorded its derivation while the
  declaration file has not, the executor SHALL surface the probe as **weakened** and report it
  as a finding rather than executing it as approved, whether or not the two changed in the
  same commit.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: Q4a teach-back; governing
    spec §"Derivation, approval, and durability"
- **R4** — WHEN the executor derives candidate probes, it SHALL present them to the operator
  for approval before persisting any of them, and SHALL persist only the approved set.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: governing spec; Q1 (a local
    operator makes the gate possible)
- **R5** — WHEN a run finds a persisted probe set, the executor SHALL execute the stored
  probes and SHALL NOT re-derive them, except for probes whose declaration changed per R2.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: governing spec; Q4a
- **R6** — WHEN a declaration is inherited from `claude-shared` through
  `spec/.spec-config.yml`, the executor SHALL treat a change of the pinned `ref` as the
  declaration change for R2. WHEN a declaration anchor lies outside the target repository and
  is not an inherited spec, the executor SHALL mark the probe **unmonitored for change** and
  re-derive it only on operator request.
  - _dimension_: `edge_cases` · _status_: `confirmed` · _source_: Q5b "Vererbte Specs über
    den gepinnten Ref, Rest markieren"

### Tiers and environment

- **R7** — Every probe SHALL declare exactly one tier from T0, T1, T2 as the governing spec
  defines them.
  - _dimension_: `domain_objects` · _status_: `confirmed` · _source_: governing spec; gate
    "Alle drei Stufen in einem Zug"
- **R8** — WHEN invoked without the T2 opt-in flag, the executor SHALL execute T0 and T1
  probes only, and SHALL report every T2 probe as **not probed** with the reason `tier T2 not
  requested`. WHEN invoked with the flag, it SHALL execute T2 probes as well.
  - _dimension_: `non_functional` · _status_: `confirmed` · _source_: Q4b "Nur auf
    ausdrücklichen Opt-in"
- **R9** — WHEN a T1 or T2 probe needs an environment, its observation step SHALL obtain it by
  invoking **Taskfile targets the target repository declares**, and the executor SHALL bring no
  container runtime, compose file, or seed data of its own. WHEN the target repository declares
  no suitable target, the probe SHALL be reported as not probed with the reason naming the
  missing target.
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: Q5a "Über Taskfile-Targets
    des Zielrepos"
- **R10** — WHEN an environment target fails to come up, the executor SHALL report the probe as
  not probed with the target's output as the reason, and SHALL NOT report it as not reached.
  - _dimension_: `edge_cases` · _status_: `assumed` · _source_: derived from R9 and the spec's
    rule that not looking is a reported number; not taught back

### Placement in the target repository

- **R11** — The probe set SHALL live under `project/reach-probes/` in the audited repository,
  as a maintained artefact beside requirements and features, and SHALL be committed there.
  - _dimension_: `domain_objects` · _status_: `confirmed` · _source_: Q6a "Proben unter
    project/, Bericht unter .audits/"; Q2 teach-back (probe set in the audited repository)
- **R12** — The report SHALL be written under `.audits/capability-reach/<YYYY-MM-DD>.md` in
  the audited repository and SHALL be regenerated on every run; it is never edited by hand.
  - _dimension_: `domain_objects` · _status_: `confirmed` · _source_: Q6a
- **R13** — The executor SHALL require a **local working copy** of the target repository and
  SHALL refuse to run against a repository reachable only through the GitHub API, naming the
  reason.
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: Q2 teach-back "Ja, so ist
    es gemeint"

### Reporting

- **R14** — The report SHALL lead with the count of not-probed entries, SHALL state the
  audited set's provenance (which declaration sources were read and which were unavailable),
  and SHALL express every reach as a ratio with the observation step that produced it.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: governing spec §Reporting;
    Q5c teach-back
- **R15** — WHEN the target repository declares nothing in any of the four declaration
  sources, the executor SHALL report that as the result and SHALL NOT render an empty audit as
  a clean one.
  - _dimension_: `edge_cases` · _status_: `confirmed` · _source_: issue #662 acceptance
    criterion 4; Q5c teach-back
- **R16** — Every report entry SHALL carry the timestamp of its probe's last execution and the
  probe's recorded derivation anchor (`derived_from`).
  - _dimension_: `functional` · _status_: `confirmed` · _source_: governing spec; Q4a
  - _amended 2026-09-25 by #668_: "derivation commit" became "derivation anchor", which is a
    blob for an in-repository declaration (R2).

### Plugin placement and process

- **R17** — The skill and the scanner agent SHALL ship in the `nolte-engineering` plugin.
  - _dimension_: `scope_boundaries` · _status_: `confirmed` · _source_: Q6b
    "nolte-engineering"
- **R18** — The scanner agent SHALL be read-only, SHALL declare only `Read`, `Grep`, `Glob`
  and `Bash` for read-only inspection, and SHALL return the declaration inventory and
  candidate probes to the skill without writing anything.
  - _dimension_: `actors` · _status_: `assumed` · _source_: shape of the four precedents;
    not taught back
- **R19** — The executor SHALL be able to produce all five probes named in the governing spec's
  §"Worked acceptance: The five defects". Of those, the T0 probe (scan lane) and the T1 probe
  (ranking service) SHALL be executed as part of this change's verification; the three T2
  probes SHALL be proven by a dogfooding run in `nolte/kamerplanter` linked from the pull
  request, not by a check in this repository.
  - _dimension_: `acceptance_criteria` · _status_: `confirmed` · _source_: Q5c "Alle fünf
    erzeugen, T0 und T1 ausführen, T2 gegen kamerplanter belegen"
- **R20** — Both artefacts SHALL pass `nolte-claude-dev:skill-review` and
  `nolte-claude-dev:agent-review`, and the skill SHALL cite the governing spec and
  `spec/claude/resumable-work/` with a checkpoint after the approval gate.
  - _dimension_: `acceptance_criteria` · _status_: `confirmed` · _source_: issue #662
    acceptance criterion 5; repository authoring rules

## Surviving assumptions / open risks

- **R10 is assumed.** A failed environment target is reported as not probed rather than not
  reached. The distinction matters because the second reading would blame the capability for
  an infrastructure failure. Not taught back; the decomposition should treat it as a decision
  to confirm at its first gate.
- **R18 is assumed.** The skill-plus-read-only-scanner split follows the four precedents, but
  derivation is a judgement task, and it is possible the drafting belongs in the skill rather
  than the agent. The `k = 2` sketches agreed on the split, so the confidence is real, but no
  operator utterance names it.
- **The T2 rows are proven outside this repository.** R19 makes the dogfooding run in
  `nolte/kamerplanter` the evidence for three of the five acceptance rows. If that run cannot
  happen before the pull request closes, those rows are unproven, and the pull request must
  say so rather than imply otherwise.
- **The probe format is the largest design surface and has no precedent here.** R1 to R3 fix
  its fields and its change-detection mechanism, but the concrete schema, the observation-step
  contract (how raw output is emitted and parsed), and the approval metadata are left to the
  implementation plan. A schema under `schemas/` with `validate_schemas.py` coverage would
  turn R1 into something checkable.
- **Git history as change detection covers only committed declarations.** An uncommitted edit
  to a declaration is invisible to R2 until it lands. The interview accepted this in exchange
  for not maintaining a stored hash. _Amended 2026-09-25 by #668:_ R2 now records the
  declaration's git blob, which git maintains itself, and the runner reads an uncommitted
  declaration edit as stale.

Refs: `nolte/claude-shared#662`, `nolte/claude-shared#660`, `spec/project/capability-reach-audit/`.
