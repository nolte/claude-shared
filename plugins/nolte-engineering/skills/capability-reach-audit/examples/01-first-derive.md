# Example 01: First derive on a repository with declarations and no probe set

## Input prompt

"Audit the capability reach of ~/repos/github/kamerplanter."

## Input files (optional)

- `~/repos/github/kamerplanter/.git` — a local working copy with history; no `project/reach-probes/` yet.
- `~/repos/github/kamerplanter/project/requirements/*.md`, `.github/workflows/*.yml`, `README.md`, `project/portfolio.yml` — the four declaration sources the scanner reads.
- `spec/project/capability-reach-audit/en.md` — the governing spec, from the installed `nolte-shared` plugin.

## Expected behaviour

1. Confirm the target is a local working copy (a directory, `.git` at its root, `git rev-parse --show-toplevel` resolves to it) and scan `.resume/capability-reach-audit/` for an `in_progress` run; none matches, so start a fresh run.
2. Run the runner once as `python3 "${CLAUDE_PLUGIN_ROOT}/skills/capability-reach-audit/scripts/reach_audit.py" --repo ~/repos/github/kamerplanter`; it exits `3` (no probe set), so route to `derive` and say why.
3. Dispatch `capability-reach-scanner` with the path and wait for its payload; checkpoint `phase: derived` with the payload under `state:`.
4. Summarise before asking: the four sources' `presence`, the entry count, the drafted count, and the not-constructible count grouped by reason code.
5. Present the drafts batched by source in the order requirement → endpoint → capability → inventory, at most twelve rows per table, and read the answers exactly per the vocabulary: `approve all`, `approve <ids>`, `reject <ids>` (the rest stays open), `skip`. Checkpoint `approved-<source>-<k>` after each answered batch.
6. Write only the approved drafts to `project/reach-probes/<id>.yml`, each with a quoted `approved_at` and `approved_by` from `git config user.name`; write `project/reach-probes/_not-constructible.yml` with the scanner's not-constructible entries (or `entries: []`), then checkpoint `phase: persisted`.
7. Propose the `missing_environment_target` and `missing_observation_helper` entries as work in the target repository, and tell the operator to commit `project/reach-probes/` before the next `run`; don't commit, don't run the probes, don't compare anything.
