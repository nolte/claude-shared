# Example 02: Run that finds a weakened probe

## Input prompt

"Run the reach probes again."

## Input files (optional)

- `project/reach-probes/*.yml` — a committed probe set from an earlier `derive`; `project/reach-probes/endpoint-scan-workflow-dispatch-runs.yml` received a second commit that lowered `expected.value` from `300` to `10` without a new `derived_from`.
- `project/reach-probes/_not-constructible.yml` — the committed manifest, two entries.
- `.audits/capability-reach/` — the previous report.

## Expected behaviour

1. Confirm the working copy and the resume scan, then invoke the runner exactly as `python3 "${CLAUDE_PLUGIN_ROOT}/skills/capability-reach-audit/scripts/reach_audit.py" --repo <path>` without `--include-t2`, because the operator didn't ask for T2.
2. The runner exits `4`. Read `references/runner-exit-codes.md`, then open the report it wrote under `.audits/capability-reach/<today>.md`.
3. Lead with the Findings section: `weakened endpoint-scan-workflow-dispatch-runs`, quoting the runner's reason (the commit that changed the probe after its derivation was recorded). State that the probe was withheld, not executed, and never read as not reached.
4. Then quote the headline exactly as written (`Not probed: <n> of <total> entries, 2 of them not constructible.`), the Provenance section, and the reach-per-tier table; don't recompute any ratio.
5. Offer the two legitimate fixes: revert the probe file to its approved text, or re-run `derive` with the entry filter set to the probe's `declaration.path` (`.github/workflows/scan.yml`), which records a new `derived_from`. Never offer to edit the probe file, and never edit the report.
6. Record T2 probes as `not probed` with reason `tier T2 not requested` when they appear, and offer `--include-t2` only as a question, not as an action.
