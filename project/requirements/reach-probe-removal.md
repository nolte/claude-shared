# Requirements — Removing a capability-reach probe: detection and explicit retirement

<!--
Produced via the `requirements-elicit` skill, following
spec/project/requirements-elicitation/.
`c_d` is an uncertainty proxy (self-consistency-derived), not a calibrated
probability. A requirement is `confirmed` only after an explicit teach-back.
-->

## Bounded context

- **What is being built:** an extension of the capability-reach audit (`spec/project/capability-reach-audit/`,
  the `capability-reach-audit` skill and its runner `reach_audit.py` in `nolte-engineering`) that detects a
  probe that disappeared from the probe set and accepts only an explicit, approved retirement as the
  legitimate exit. Today the spec defines no rule for a vanished probe and the runner judges each probe file
  on its own history only, so a probe can be retired and replaced by a weaker one without a finding.
- **For whom:** the operator who runs the audit in a repository, and the reviewer of a pull request that
  changes probes.
- **Trigger:** nolte/claude-shared#704, follow-up of #701 (merge edits, fixed in #703) and #702 (an origin
  inside a merge, fixed in #705).
- **Out of scope:** how probes are derived or executed; the weakening rules of #701/#702; re-verification of
  declarations.

## Understanding KPI

- Thresholds: `τ_low = 0.4`, `τ_high = 0.8`, self-consistency `k = 2`, question budget = 10 (spec defaults)
- `U_gate = min_d c_d` over required dimensions = **0.8**
- Termination: `saturation` (9 questions used; teach-back of the full set confirmed on 2026-11-10, one
  contradiction found in the teach-back and resolved by Q9)

### Gap matrix

| Dimension | Applicable | `c_d` | Uncertainty source | Evidence event |
|---|---|---|---|---|
| `functional` | yes | 0.9 | specification | operator decision before the interview (finding + explicit exit); Q2 identity by id; Q6/Q7 edge cases; teach-back confirmed |
| `non_functional` | yes | 0.8 | interpretation | assumption (a) HEAD history only, confirmed in teach-back; history scan cost not measured (risk) |
| `constraints` | yes | 0.85 | interpretation | spec EN canonical + DE; schema under `schemas/` embedded in the runner with a drift test (precedent `reach-not-constructible-v1.0`); one PR (R8, chosen before the interview) |
| `domain_objects` | yes | 0.85 | specification | Q4 `_retired.yml` + `reach-retired-v1.0` fields; Q5 approval block; teach-back |
| `actors` | yes | 0.9 | — | Q1 bounded context (operator, PR reviewer); runner detects, skill operation `retire` writes (Q8) |
| `acceptance_criteria` | yes | 0.8 | specification | derived from R1–R10 and confirmed with the teach-back; k=2 sketches agreed on the test shapes |
| `edge_cases` | yes | 0.85 | specification | Q6 package (contradiction, unknown id, deleted superseded file, reappearance); Q7 exchange under the same id; Q9 R2/R4 resolution |
| `scope_boundaries` | yes | 0.9 | specification | Q1 (also never-approved probes count), Q3 (whole history + one-time migration) |

## Requirements

- **R1** — WHEN an id that was carried by a committed file under `project/reach-probes/` in any commit of
  HEAD's history (approved or not) is carried by no probe file at HEAD and has no effective retire entry,
  the runner SHALL report it as a finding in the new state `removed` (exit 4), naming the last commit in
  which the id existed.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: operator decision "Finding, Ausstieg nur
    expliziter"; Q1 "Auch ungeprüfte Probes"; Q3 "Gesamte Historie + Migration"
- **R2** — WHEN an id is carried at HEAD by a file whose followed history did not carry that id earlier,
  while another file that no longer exists carried it earlier (an exchange under the same id), the runner
  SHALL report the earlier probe as `removed`; the HEAD file is judged on its own rules independently.
  - _dimension_: `edge_cases` · _status_: `confirmed` · _source_: Q7 "Finding, außer per Retire" as
    narrowed by Q9
- **R3** — The identity of a probe SHALL be its `id` field: a rename of the file that keeps the id is no
  removal; a changed id in a kept file is a removal of the old id plus a new probe.
  - _dimension_: `domain_objects` · _status_: `confirmed` · _source_: Q2 "Nach id"
- **R4** — A retirement SHALL be recorded only as an entry in `project/reach-probes/_retired.yml`
  (schema `reach-retired-v1.0`), each entry carrying `id`, a closed reason code (initial set:
  `capability-removed`, `declaration-removed`, `duplicate`, `derived-in-error`), a free-text `detail`,
  `recorded_at`, the last commit in which the probe existed, and an `approval` block like a probe's. Only an
  entry with a valid approval is effective; only an effective entry lifts R1.
  - _dimension_: `domain_objects` · _status_: `confirmed` · _source_: Q4 "Eigenes Manifest _retired.yml";
    Q5 "Approval + immer im Report"
- **R5** — WHEN a retire entry names an id that a probe file carries at HEAD, the runner SHALL report a
  contradiction finding; a retire entry therefore never legitimises an exchange under the same id (R2):
  the replacement takes a new id and the old id is retired, or the old file is restored and superseded.
  - _dimension_: `edge_cases` · _status_: `confirmed` · _source_: Q6 (2); Q9 "R4 gilt, neue id nötig"
- **R6** — WHEN a retire entry names an id that no committed probe file in HEAD's history ever carried, the
  runner SHALL report it as an invalid entry (finding).
  - _dimension_: `edge_cases` · _status_: `confirmed` · _source_: Q6 (3)
- **R7** — WHEN a superseded probe's file is deleted, the runner SHALL treat its id under R1; the documented
  rule "never delete a superseded file" becomes enforced, with retirement as the only exit.
  - _dimension_: `edge_cases` · _status_: `confirmed` · _source_: Q6 (4)
- **R8** — Every report SHALL list each retired id with its reason in Provenance and mark the entries that
  are new since the manifest's previous commit, so a reviewer sees a retirement in the change that adds it.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: Q5 "Approval + immer im Report"
- **R9** — The `capability-reach-audit` skill SHALL offer an operation `retire` that reads the `removed`
  findings, proposes one entry per id (last commit, reason code to choose) and writes it to `_retired.yml`
  with an approval block only after a per-id operator approval; the runner itself writes nothing.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: Q8 "Skill-Operation `retire`"
- **R10** — The change SHALL land as one pull request: the spec first (`spec/project/capability-reach-audit/`
  EN canonical + DE), then schema, runner, skill operation, and references.
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: orchestration gate "requirements-elicit, 1 PR"
- **R11** — The runner SHALL read history from HEAD only (no other branches), and SHALL read a probe's id
  from its YAML `id` field, falling back to the file name stem when the file doesn't parse.
  - _dimension_: `non_functional` · _status_: `confirmed` · _source_: teach-back assumptions (a) and (b)
    confirmed

### Acceptance criteria

- [ ] An approved probe deleted in a plain commit reads `removed` (exit 4) naming the deleting side's last commit; with an approved retire entry for it, the run is clean and Provenance lists the retirement, marked new.
- [ ] A never-approved probe file deleted later reads `removed` the same way.
- [ ] A retire entry without a valid approval takes no effect: the id stays `removed`.
- [ ] A probe deleted from path A and re-added dissimilar under the same id at path B (one commit, or two) reports the old probe `removed`; a retire entry for that id is a contradiction.
- [ ] A rename that keeps the id (followed by `--follow`) is no removal; editing the id in a kept file reports the old id `removed`.
- [ ] A retire entry for an id still carried at HEAD is a contradiction; one for an id never seen is invalid.
- [ ] Deleting a superseded probe's file reports it `removed`.
- [ ] `retire` proposes entries for the current `removed` ids and writes only approved ones.
- [ ] Spec EN/DE carry the rule and its acceptance criteria; the schema ships under `schemas/` with the runner's embedded copy guarded by a drift test.

## Surviving assumptions / open risks

- **History scan cost** (`non_functional`, 0.8): reading every id ever carried under `project/reach-probes/`
  needs a walk over the directory's whole history; not measured. Mitigation: one `git log --name-status`
  over the directory plus `git show` per distinct blob; measure on the reference consumer before release.
- **Ids from unparseable historic revisions** fall back to the file name stem (R11); a stem that collides
  with a real id elsewhere could mask or invent a removal. Accepted by the operator in the teach-back.
- **Breaking for consumers**: repositories that already deleted probes get `removed` findings on the first
  run after the update until they run `retire` (one-time migration, Q3).
