# Example 06 — Empty in-flight surface yields a zero-findings report

A scheduled portfolio in-flight audit run from inside `claude-shared`
finds nothing stalled anywhere: every open PR is fresh and green,
every open issue is recently triaged, no feature branch has drifted,
and no Discussion is unrouted. The audit still writes a valid
Findings-Report with the four mandated sections and explicit
per-severity zero counts — not "no report at all". Exercises the
acceptance criterion "running the audit against an empty in-flight
surface (zero stalled items across the portfolio) produces a valid
Findings-Report with zero findings under each severity rather than no
report at all" from
`spec/portfolio/portfolio-inflight-management/`.

## Contents

- [Input prompt](#input-prompt)
- [Input files](#input-files)
- [Expected behaviour](#expected-behaviour)

## Input prompt

> Run the in-flight triage.

## Input files

The active checkout is `claude-shared`; detection passes because
`.claude-plugin/plugin.json` and
`spec/portfolio/portfolio-inflight-management/` both exist.

The resolved Portfolio-Member set returned by
`gh api orgs/nolte/repos --paginate` contains three repositories —
`nolte/gh-plumbing`, `nolte/vale-style`, `nolte/sensor-bridge` — none
carrying a `portfolio: excluded` opt-out marker in `CLAUDE.md`.

The `portfolio-inflight-collector` agent fans out across all four data
sources (issues, pull requests, feature branches, Discussions) for
every resolved repository and returns an empty stalled-set for each:

```yaml
# returned for every resolved repository
issues: []          # no issue past the untriaged staleness threshold
pull_requests: []   # every open PR is < 7 days old with green required checks
branches: []        # no feature branch drifted from develop without a PR
discussions: []     # no Discussion left unrouted past threshold
```

Each repository's threshold defaults apply; no `project/inflight.yml`
override is present in any of them.

## Expected behaviour

1. **Repository-role detection passes** for `claude-shared` and the
   Run operation is selected.
2. **Portfolio-Member set resolved + collector dispatched** as in
   Example 01. The collector returns an empty stalled-set per data
   source per repository; the orchestrating conversation receives only
   the pre-reduced (empty) structured summaries.
3. **Stalling threshold evaluation.** For every (repository ×
   data-source) pair the audit confirms nothing crosses its staleness
   threshold. No matrix-axis evaluation is required because no finding
   is raised.
4. **Findings-Report still written.** The skill writes a valid
   Findings-Report at `.audits/portfolio-inflight/2026-05-23.md` with
   the four `review-plan`-mandated sections in declared order —
   `## Scope`, `## Summary`, `## Findings`, `## Processing log`. The
   report is produced even though there is nothing to report: a
   zero-findings run is a valid result, not a skipped run.
   - `## Scope` names the audit, the run date, and the resolved
     Portfolio-Member set (`nolte/gh-plumbing`, `nolte/vale-style`,
     `nolte/sensor-bridge`) plus the four scanned data sources.
   - `## Summary` states explicit per-severity zero counts:
     `Critical: 0`, `Warning: 0`, `Suggestion: 0`, `Info: 0`.
   - `## Findings` carries a single explicit "no findings" line rather
     than being empty or omitted, for example:

     ```text
     No in-flight findings: every resolved Portfolio-Member's open issues,
     pull requests, feature branches, and Discussions are within their
     staleness thresholds at this audit-run snapshot.
     ```

   - `## Processing log` records the resolved member set, the data
     sources scanned, the thresholds applied (all defaults; no
     `project/inflight.yml` override found), and the empty result per
     pair, so a later reader can confirm the run actually inspected the
     surface rather than short-circuiting.
5. **Per-severity counts confirmed.** The closing message in the
   operator's language reports the path of the new Findings-Report
   (`.audits/portfolio-inflight/2026-05-23.md`) and the all-zero
   per-severity counts, and notes there is no specialist dispatch to
   recommend this cycle.
6. **Hard rules honoured.** No issue closed, no PR merged, no branch
   deleted, no Discussion closed, no review comment resolved; no file
   modified in any Portfolio-Member repository; the audit's only write
   target is `.audits/portfolio-inflight/2026-05-23.md` in
   `claude-shared`; no mutating `gh api` call issued; severities are
   written exactly in Title Case.
