# Runner exit codes and not-probed routing

Loaded by `capability-reach-audit` `run` step 2. The runner is `scripts/reach_audit.py` (invoked only as `python3 "${CLAUDE_PLUGIN_ROOT}/skills/capability-reach-audit/scripts/reach_audit.py" --repo <path>`); its exit codes and reason strings are the contract this file maps to an operator-facing next step. Nothing here re-derives a verdict: the report's classes and ratios are quoted, never recomputed.

## Exit codes

| Exit | Runner meaning | What the skill does next |
|---|---|---|
| `0` | report written, no findings | run `report`; the headline may still say `Not probed: <n> of <total>`, which is a coverage fact to surface, not a pass |
| `1` | runtime error (unreadable probe set, report not writable, git failure) | relay stderr verbatim; don't retry blind; the fix is in the target's state, not in the invocation |
| `2` | usage error or non-local target | relay the message verbatim; a remote address, a missing directory, a missing `.git`, a subdirectory, a bare repository, or a repository with no commit is refused by design; never route around it |
| `3` | no probe file: `project/reach-probes/` is absent, empty, or holds only the manifest; nothing was executed | **not** a clean result. Without a manifest the report says "no probe set"; with manifest entries it is a full report in which every entry is not probed. Either way route to `derive` (with a manifest, the actionable entries are the work to do first) |
| `4` | report written with findings (weakened or invalid probes, contradictions, manifest defects); takes precedence over 3 | run `report` leading with the Findings section, then the headline; see §Findings |
| `5` | PyYAML or jsonschema missing | relay the runner's `pip install` hint verbatim and stop; never parse or validate probes yourself |

A negative or zero `--environment-timeout` also exits `2` before anything runs.

## Findings (exit 4)

- **weakened** `<id>`: the probe file changed after the commit that recorded its `derived_from`, or has uncommitted changes. The probe was **withheld** (`not probed`, reason `weakened: …`), never executed as approved. Lead with these. The operator either reverts the change (restoring the approved text) or re-derives the entry (`derive` with the entry filter), which records a new `derived_from` and a new baseline. Editing the file again is never the fix.
- **invalid probe** `<file>`: the file fails the probe schema. Quote the runner's error list. The fix is a re-derive of that entry; a hand edit to satisfy the schema would itself be a weakening.
- **contradiction** `<id>`: the id is both a probe file and a manifest entry; the probe is **not executed** and the row is not probed. The manifest is stale from a round that turned the entry into a probe: re-run `derive` with the entry filter for that id, which rewrites the manifest without it; never delete the probe file to resolve it.
- **invalid manifest** (`_not-constructible.yml`): the file is unparseable or fails the schema above `entries/<i>`; none of its entries is counted and the headline says so. The fix is a re-run of `derive`, which rewrites the manifest from the scanner's payload; never repair it by hand.
- **invalid manifest entry** `<id>`: one entry fails the schema (a bad reason code, a missing `derived_from`, an unquoted `recorded_at`); it still counts as not probed. Re-run `derive` for that entry.
- **duplicate manifest id** `<id>`: listed more than once, counted once. Re-run `derive`; the scanner's ids are unique per payload, so a duplicate means two rounds were merged by hand.

## Not-probed reasons and their routing

The runner writes every not-probed reason into the report's Probes table. These are the ones that call for a next step from the skill:

| Reason (as written by the runner) | Meaning | Next step |
|---|---|---|
| `declaration changed since derivation: …` | the declaration's latest commit, its uncommitted edit, or a moved inherited `ref` postdates `derived_from` (stale, R2) | offer `derive` with the entry filter set to exactly these ids (R5) |
| `probe file is not committed; …` | the approved set isn't under version control yet (R11) | the operator commits `project/reach-probes/`, then `run` again |
| `not approved` | a probe file without an `approval` block, for example a copied example | the file was never approved through the gate; remove it or re-derive and approve the entry |
| `tier T2 not requested` | T2 probes withheld by default (R8) | say so; add `--include-t2` only on the operator's explicit request |
| `not constructible: <code>` | a manifest entry: no probe exists at any tier, counted in the headline | `missing_environment_target` and `missing_observation_helper` are work in the target repository (the `detail` names it), after which `derive` turns the entry into a probe; the other three codes stay counted until the declaration or the environment changes |
| `environment target <name> failed (…)` | the Taskfile target didn't come up (R10) | relay the target's output; this is infrastructure, never "not reached" |
| `observation step exited <n>: …` / `observation step timed out …` | the observe argv failed or hung | relay; the probe's argv or the host's tooling (`gh` auth, `psql`) needs attention in the target |
| `anchor … lies outside the repository; change is not monitored` | external anchor (R6) | inform the operator; re-derive only on their request |
| `derived_from … is not a commit of the target repository` / `… not in the history of HEAD` | the recorded commit doesn't resolve in this clone (shallow clone, rewritten history) | fetch full history or re-derive; never edit `derived_from` by hand |

Every other reason is quoted as written and needs no routing.
