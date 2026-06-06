# Example 04 — Security relevance lifts a finding to Critical

A scheduled portfolio in-flight audit run from inside `claude-shared`
finds an open pull request in `nolte/sensor-bridge` that has been open
for 5 days — under the 7-day red-check threshold — but whose CI surface
carries a dependency-audit CVE indicator: a required `dependency-audit`
check is red and its annotation names a known CVE in a transitive
dependency. The `security_relevance` matrix axis trips on the CVE
indicator alone, lifting the finding straight to `Critical` without the
staleness threshold having to fire. Exercises the `security_relevance`
evaluation requirement from
`spec/portfolio/portfolio-inflight-management/` §Classification and
prioritisation (Critical row, security-relevant trigger) and the
acceptance criterion "a synthetic security trigger fed into the audit
produces a finding carrying `security_relevance: true`".

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
`gh api orgs/nolte/repos --paginate` contains `nolte/sensor-bridge`,
which carries no `portfolio: excluded` opt-out marker in `CLAUDE.md`
and no `inflight: skip-pull-requests` marker.

The `portfolio-inflight-collector` agent returns, among other entries,
this PR summary for `nolte/sensor-bridge`:

```yaml
pull_requests:
  - id: 88
    title: "chore(deps): widen paho-mqtt range for the 2.x line"
    state: open
    is_draft: false
    age_days: 5
    last_reviewer_activity_days: 4
    required_checks_red: true
    failing_checks: [dependency-audit]
    dependency_audit_cve: "CVE-2025-12345 (transitive: example-lib < 2.3.1)"
    conflicts_against_develop: false
    labels: [dependencies]
    review_threads_unresolved: 0
```

The collector's `dependency_audit_cve` field is the synthetic security
trigger: the red `dependency-audit` required check names a CVE in a
transitive dependency referenced by the repository's lockfile.

No `release-blocker` label is set; the PR head SHA does not appear in
any open `release-drafter` draft; no sibling Portfolio-Member's
`project/roadmap.md` or `project/sprints/*.md` references
`nolte/sensor-bridge#88`.

No `project/inflight.yml` override exists in `sensor-bridge`, so the
audit applies the spec defaults.

## Expected behaviour

1. **Repository-role detection passes** for `claude-shared` and the
   Run operation is selected.
2. **Portfolio-Member set resolved + collector dispatched** as in
   Example 01. The orchestrating conversation receives only the
   pre-reduced structured summary; raw PR bodies stay inside the agent.
3. **Stalling threshold check.** PR #88 is 5 days old, under the
   7-day red-check threshold. Under the normal stalling rule this PR
   would not surface — but the §Stalling thresholds sub-threshold
   escalation clause permits surfacing when a matrix axis demands it.
   The skill defers the surface-or-suppress decision to step 4.
4. **Matrix axes derived.** For PR #88:
   - `security_relevance: true` per the §Classification and
     prioritisation evaluation: the red `dependency-audit` required
     check names a CVE in a transitive dependency referenced by the
     lockfile (one of the three in-scope security signals — a
     dependency-audit CVE indicator).
   - `release_blocking: false` (no `release-blocker` label, no open
     `release-drafter` draft membership)
   - `age_multiplier: 0.7×` (5 days open ÷ 7-day threshold; below 1×
     does not normally surface, but is irrelevant once
     `security_relevance` fires)
   - `cross_repo_blocking: false` (no roadmap or sprint reference scan hit)
5. **Severity assigned.** `security_relevance: true` triggers the
   `Critical` row of the matrix. The §Classification and
   prioritisation higher-severity-tie-break rule applies — `Critical`
   wins over any lower row the same finding might also match.
6. **Specialist recommendation applied.** Per §Specialist
   recommendation the matching specialist is named verbatim by slug:
   `dependency-audit` (the CVE in the dependency surface is the
   actionable driver). The recommended-action line carries the
   verbatim slash-command invocation:
   `/nolte-shared:dependency-audit against nolte/sensor-bridge (CVE-2025-12345; security-blocking, prioritise over non-security findings)`.
7. **Findings-Report written** at
   `.audits/portfolio-inflight/2026-05-23.md` with the four
   `review-plan`-mandated sections in declared order — `## Scope`,
   `## Summary`, `## Findings`, `## Processing log` — and Title-Case
   severities only. The finding reads roughly:

   ```text
   [portfolio-inflight-management §Classification and prioritisation]
   Critical — sensor-bridge/pr/88
   driver: security_relevance (dependency-audit CVE indicator: CVE-2025-12345, transitive example-lib < 2.3.1)
   axes: security_relevance=true, release_blocking=false,
         age_multiplier=0.7×, cross_repo_blocking=false
   staleness: 5d open, 4d since last reviewer activity (sub-threshold; escalated by security_relevance)
   recommend: /nolte-shared:dependency-audit against nolte/sensor-bridge (CVE-2025-12345; security-blocking)
   ```

8. **Tracking-issue offer.** Per §Integration with
   continuous-improvement the skill `SHOULD` offer to open a tracking
   issue in `nolte/sensor-bridge` for this `Critical` finding. The
   skill presents this as an opt-in offer and never opens the issue
   automatically — operator authority remains intact.
9. **Per-severity counts confirmed.** The closing message in the
   operator's language reports the path of the new Findings-Report
   (`.audits/portfolio-inflight/2026-05-23.md`), the per-severity
   counts (`Critical: 1`, `Warning: 0`, `Suggestion: 0`, `Info: 0`),
   and points the operator at the recommended `dependency-audit`
   dispatch as the next step.
10. **Hard rules honoured.** No PR closed, no PR merged, no branch
    deleted, no review comment resolved; no file modified in
    `nolte/sensor-bridge`; the audit's only write target is
    `.audits/portfolio-inflight/2026-05-23.md` in `claude-shared`; no
    mutating `gh api` call issued; `Critical` is written exactly in
    Title Case (no `CRITICAL`).
