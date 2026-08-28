# Example 05 — Cross-repository blocking lifts a finding to Critical

A scheduled portfolio in-flight audit run from inside `claude-shared`
finds an open issue in `nolte/gh-plumbing` that has sat untriaged for
21 days. On its own the staleness would yield at most a `Suggestion`,
but a sibling Portfolio-Member's sprint file references the issue's
GitHub identifier: `nolte/sensor-bridge`'s `project/sprints/0004.md`
contains the short cross-reference `nolte/gh-plumbing#312` as a
declared blocker for its current sprint. The `cross_repo_blocking`
matrix axis trips on that read-only text-scan hit, lifting the finding
to `Critical`. Exercises the `cross_repo_blocking` detection MUST from
`spec/portfolio/portfolio-inflight-management/` §Classification and
prioritisation (read-only scan of every Portfolio-Member's
`project/roadmap.md` and `project/sprints/*.md` for `nolte/<repo>#<number>`
or full GitHub URL references) and the acceptance criterion "a synthetic
cross-reference produces a finding carrying `cross_repo_blocking: true`".

## Contents

- [Input prompt](#input-prompt)
- [Input files](#input-files)
- [Expected behaviour](#expected-behaviour)

## Input prompt

> Audit the portfolio in-flight.

## Input files

The active checkout is `claude-shared`; detection passes because
`.claude-plugin/plugin.json` and
`spec/portfolio/portfolio-inflight-management/` both exist.

The resolved Portfolio-Member set returned by
`gh api orgs/nolte/repos --paginate` contains both `nolte/gh-plumbing`
and `nolte/sensor-bridge`; neither carries a `portfolio: excluded`
opt-out marker in `CLAUDE.md`, and neither carries an
`inflight: skip-issues` marker.

The `portfolio-inflight-collector` agent returns, among other entries,
this issue summary for `nolte/gh-plumbing`:

```yaml
issues:
  - id: 312
    title: "reusable-release-drafter: expose tag-input passthrough"
    state: open
    is_draft: false
    age_days: 21
    last_activity_days: 21
    labels: [enhancement]
    assignees: []
```

The collector's read-only cross-reference scan over every resolved
Portfolio-Member's `project/roadmap.md` and `project/sprints/*.md`
returns one hit: `nolte/sensor-bridge`'s `project/sprints/0004.md`
contains the literal token `nolte/gh-plumbing#312` in its blockers
list. This is the synthetic cross-reference. The match is exact
(short cross-reference form `nolte/<repo>#<number>`); no fuzzy
matching is applied.

No `release-blocker` label is set and no security signal is present.

No `project/inflight.yml` override exists in `gh-plumbing`, so the
audit applies the spec defaults.

## Expected behaviour

1. **Repository-role detection passes** for `claude-shared` and the
   Run operation is selected.
2. **Portfolio-Member set resolved + collector dispatched** as in
   Example 01. The orchestrating conversation receives only the
   pre-reduced structured summary; raw issue bodies stay inside the
   agent.
3. **Stalling threshold check.** Issue #312 is 21 days untriaged,
   crossing the untriaged-issue staleness threshold. The skill records
   the staleness measure (`21 days open, 21 days since last activity`)
   and proceeds to classification.
4. **Cross-reference scan performed.** As part of axis evaluation the
   audit runs the read-only text scan over every Portfolio-Member's
   `project/roadmap.md` and `project/sprints/*.md` for
   `nolte/gh-plumbing#312` or its full GitHub URL form
   (`https://github.com/nolte/gh-plumbing/issues/312`). The scan hits
   the short cross-reference in `nolte/sensor-bridge`'s
   `project/sprints/0004.md`.
5. **Matrix axes derived.** For issue #312:
   - `security_relevance: false`
   - `release_blocking: false`
   - `age_multiplier: 1.0×` (21 days ÷ the 21-day untriaged-issue
     threshold)
   - `cross_repo_blocking: true` per the §Classification and
     prioritisation detection MUST: another Portfolio-Member's sprint
     file references the finding's identifier via the short
     cross-reference form. The referencing file path
     (`nolte/sensor-bridge:project/sprints/0004.md`) is recorded for
     traceability.
6. **Severity assigned.** `cross_repo_blocking: true` triggers the
   `Critical` row of the matrix (cross-portfolio blocking). The
   higher-severity-tie-break rule keeps `Critical` over the
   `Suggestion` the bare staleness would otherwise have produced.
7. **Specialist recommendation applied.** The issue is an untriaged
   enhancement request that another repo's sprint depends on; per
   §Specialist recommendation the matching specialist is named verbatim
   by slug — `feature-decompose` — to turn the blocking request into
   actionable feature files. The recommended-action line carries the
   verbatim slash-command invocation:
   `/nolte-planning:feature-decompose for nolte/gh-plumbing#312 (blocks nolte/sensor-bridge sprint 0004)`.
8. **Findings-Report written** at
   `.audits/portfolio-inflight/2026-05-23.md` with the four
   `review-plan`-mandated sections in declared order. The finding reads
   roughly:

   ```text
   [portfolio-inflight-management §Classification and prioritisation]
   Critical — gh-plumbing/issue/312
   driver: cross_repo_blocking (referenced by nolte/sensor-bridge:project/sprints/0004.md as `nolte/gh-plumbing#312`)
   axes: security_relevance=false, release_blocking=false,
         age_multiplier=1.0×, cross_repo_blocking=true
   staleness: 21d open, 21d since last activity
   recommend: /nolte-planning:feature-decompose for nolte/gh-plumbing#312 (blocks nolte/sensor-bridge sprint 0004)
   ```

9. **Per-severity counts confirmed.** The closing message reports the
   path of the new Findings-Report, the per-severity counts
   (`Critical: 1`, `Warning: 0`, `Suggestion: 0`, `Info: 0`), and
   points the operator at the recommended `feature-decompose` dispatch
   as the next step.
10. **Hard rules honoured.** No issue closed, no label added or
    removed by the audit; no file modified in `nolte/gh-plumbing` or
    `nolte/sensor-bridge` (the cross-reference scan is read-only); the
    only write target is `.audits/portfolio-inflight/2026-05-23.md` in
    `claude-shared`; no mutating `gh api` call issued; `Critical` is
    written exactly in Title Case (no `CRITICAL`).
