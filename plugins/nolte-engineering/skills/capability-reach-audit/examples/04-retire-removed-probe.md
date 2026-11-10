# Example 04: Run that reports a removed probe, then `retire`

## Input prompt

"Run the reach probes; I dropped the CSV export last week."

## Input files (optional)

- `project/reach-probes/*.yml`: a committed, approved probe set. An earlier commit deleted `project/reach-probes/csv-export-populated.yml` together with the CSV export it measured; no `project/reach-probes/_retired.yml` exists.
- `project/reach-probes/_not-constructible.yml`: the committed manifest.

## Expected behaviour

1. Invoke the runner as in `run`; it exits `4`. Read `references/runner-exit-codes.md`, then lead with the Findings section: `removed csv-export-populated`, quoting the reason `no probe file carries this id any more; it last existed in project/reach-probes/csv-export-populated.yml at <full hash>; no retirement record accounts for it`. Quote the headline with its `removed` clause and the Provenance line `No retirement manifest …: no probe id is retired.`
2. Offer `retire` for that id and read `references/retirement.md`. Don't restore or delete any probe file yourself.
3. Show one proposal: `id: csv-export-populated`; a `reason` proposed from the operator's words (`capability-removed`) and confirmed by them; a `detail` naming the change that removed the export; a quoted `recorded_at`; `last_revision` set to the full hash from the reason, not its short form; an `approval` block with a quoted `approved_at` and `approved_by` from `git config user.name`.
4. Write `project/reach-probes/_retired.yml` only after the answer `retire csv-export-populated`; checkpoint `retired-csv-export-populated`. Without that answer, write nothing.
5. Tell the operator to commit `_retired.yml` (the deletion is already committed, so a later commit is fine) and that the next run lists the record in Provenance as `new since the manifest's previous commit`. Don't commit and don't rerun on their behalf.
6. Had the finding read `exchange under the same id: …`, propose no record: name the two exits the reason states, a new id for the replacement plus `retire` for the old id, or restoring the earlier file and superseding it.
