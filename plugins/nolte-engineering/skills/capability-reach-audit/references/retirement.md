# Retirement records

Contents: §Source and eligibility · §Reason codes · §Proposal and approval · §Record shape · §Commit rule · §Retirement findings · §One-time migration

Loaded by `capability-reach-audit` `retire`. Governing rule: `spec/project/capability-reach-audit/` §"Derivation, approval, and durability" (the removal and retirement-record bullets) and executor requirement R9 of `project/requirements/reach-probe-removal.md`. The schema is `schemas/reach-retired-v1.0.schema.yaml` (closed objects, no verdict field); the runner embeds it. The runner reads `project/reach-probes/_retired.yml` and writes nothing; `retire` is the only writer, and only after an answer naming the id.

## Source and eligibility

The input is the `removed` findings of the latest report, each a line `` - **removed** `<id>` (<file>): <reason> ``. When the report predates the deletion or HEAD moved since, invoke the runner first (as in `run`) and read the fresh report. Never derive the list of removed ids yourself: only the runner walks the history.

What `retire` does depends on the reason; match on the reason's first part and on its last part, `<why>`:

| Reason (as written by the runner) | What `retire` does |
|---|---|
| `exchange under the same id: …` | **Never** a record: one is a `retirement contradiction`, since a file carries the id now. Quote the runner's exit: give the replacement a new id (derive and approve it) and retire the old id once no file carries it, or restore the earlier file and supersede it (`references/runner-exit-codes.md` §Re-baseline rule) |
| `…; no retirement record accounts for it` | propose a new record |
| `…; its retirement record carries no approval, so it takes no effect` | show the record as it stands and propose it again with an approval block; on the answer, replace it in place |
| `…; its retirement record is invalid (see Findings), so it takes no effect` | quote the `invalid retirement record` finding, then propose a corrected record that replaces it |
| `…; the retirement manifest is unreadable (see Findings), so no record in it takes effect` | write nothing into the file. When HEAD's committed manifest is readable, the operator restores it (`git -C <target> checkout -- project/reach-probes/_retired.yml`) and `retire` starts over; otherwise re-propose every record it held, each approved again. Never reconstruct a record by guessing |
| `…; its retirement record is not committed, so it takes no effect` | nothing to write: the operator commits the manifest (§Commit rule) |
| `…, and its removal is not committed; …` | a record may be proposed and written now, but it takes effect only once the deletion is committed: commit both together |
| `…; its retirement record was already in project/reach-probes/_retired.yml at <sha12>, before the removal in <sha12>, so it can't account for that removal` | the probe was restored and removed again: propose a new record (new `recorded_at`, the new `last_revision`, a new approval) that replaces the old one |
| `…; project/reach-probes/_retired.yml can't be read at <sha12>, before the removal in <sha12>, so it can't be shown that the record postdates that removal` | write nothing: the manifest was unparseable at the last commit that still carried the probe, the runner fails closed, and no later record can change that commit. Tell the operator the id can't be retired; the exits are restoring the probe or leaving the `removed` finding standing with a stated reason |
| `…; no commit that removed it was found; …` | the reason names no commit, so `last_revision` has no source: ask the operator for the commit and check it with `git -C <target> rev-parse --verify '<hash>^{commit}'`; never fill it from memory |

## Reason codes

The operator chooses exactly one code per id; propose one from the evidence, never decide it alone.

| Code | Use when |
|---|---|
| `capability-removed` | the capability the probe measured is gone from the system |
| `declaration-removed` | the declaration the probe answered to is gone (a dropped requirement, a withdrawn README claim, a deleted inventory entry) |
| `duplicate` | another probe checks the same thing; `detail` names that probe's id |
| `derived-in-error` | the probe should never have been derived: wrong entry, wrong declaration, or a file committed by mistake (an unapproved copy included) |

None of them fits a probe that was deleted because it failed, was weakened, or was inconvenient, nor a replacement under the same id: there is no record then. Say so and route to the fix the probe's own finding names (restore the file; a weakened probe is superseded, never retired).

## Proposal and approval

1. Per id, show the proposal as the YAML it would write (§Record shape), with the finding's reason quoted above it, so the operator sees which commit `last_revision` comes from.
2. Read the answer: `retire <id>` writes that record; one answer may name several ids, but each must be named, there is no `retire all`. `skip <id>` writes nothing, and the id stays `removed`. A changed code or detail is shown again before it's written.
3. On `retire <id>`, merge the record into `<target>/project/reach-probes/_retired.yml`: create the file when absent; keep every other record byte for byte; append the new record, or replace the one with the same id in place (an id appears once). Checkpoint `retired-<id>` with the answer in `decisions[]`.
4. After the last answer, state the commit rule and that the next run lists each new record in Provenance marked `new since the manifest's previous commit`.

## Record shape

```yaml
# Retirement manifest; written by capability-reach-audit retire, read by the runner.
# A record takes effect only with an approval, once committed with or after the deletion.
entries:
  - id: <id exactly as the finding names it>
    reason: <capability-removed | declaration-removed | duplicate | derived-in-error>
    detail: "<the operator's words: which change removed it, or which probe it duplicates>"
    recorded_at: "<UTC ISO 8601, quoted>"
    last_revision: <the full commit hash the finding's reason names after `at` or `at HEAD`>
    approval:
      approved_at: "<UTC ISO 8601, quoted>"
      approved_by: "<git config user.name; ask when empty>"
```

- `last_revision` is the full 40- or 64-hex object id, never the twelve-character short form; the runner checks only its format, since a squash merge may drop the commit.
- `approved_by` follows the probe rule: `git -C <target> config user.name`, and when that's empty, ask; never an empty string or a generic label.
- Write no `observation_digest` or `mode`: the schema's `Approval` requires only `approved_at` and `approved_by`, and since a retirement executes nothing, the runner reads neither field. The probe rule that every approval carries a digest doesn't apply here.
- `entries: []` is valid and means no id is retired; don't create the file only to hold it.

## Commit rule

- Commit `_retired.yml` in the same commit as the deletion, or in a later one, never before it: a record that was already in the manifest at the last commit that still carried the probe can't account for that removal.
- An uncommitted record takes no effect; the run reports `its retirement record is not committed, so it takes no effect` until it is.
- A probe restored and deleted again needs a new record; the old one predates the new removal.
- A record committed in a pull request shows in that pull request's report as new, which is how a reviewer sees the retirement.

## Retirement findings

`retire` also resolves the retirement findings, each only on an answer naming the id:

- `retirement contradiction` `<id>`: a probe file still carries the id. Remove the record. When the probe is meant to go, the operator deletes the file, and `retire` replaces the record with a fresh one (new `recorded_at` and approval) committed with the deletion or after it; the old record, already in the manifest before the removal, would never take effect.
- `invalid retirement record` `<id>` with `no committed probe file under project/reach-probes/ in the history of HEAD ever carried this id`: usually a mistyped id; remove the record and, when a `removed` finding names the right id, propose a record for that one.
- `invalid retirement record` `<id>` with `listed more than once; only the first record is read`: keep one record, re-approved when the two differ.
- `invalid retirement record` `<id>` with `fails the retirement schema: …`: replace it with a corrected, re-approved record.
- `invalid retirement manifest` (`not parseable as YAML: …`, `refused and not read: …` for a symlink or a path outside the repository, or a schema error above `entries/<i>`): as the unreadable-manifest row of §Source and eligibility; the manifest must be a regular file.

## One-time migration

A repository that deleted probes before the runner checked for removals reads every such id as `removed` on its first run with this version. The deletions are long committed, so each record goes in a later commit; `last_revision` is the commit the finding names. Walk the ids with the operator in the order the Findings section lists them; an id whose deletion was a mistake is restored rather than retired.
