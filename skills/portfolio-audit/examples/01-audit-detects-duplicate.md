# Example 01 — Audit detects a fresh cross-repository duplicate

A scheduled portfolio audit run from inside `claude-shared` collects
every Portfolio-Member's `project/portfolio.yml`, finds two
repositories declaring semantically overlapping capabilities for the
first time this audit cycle, and emits a `Warning` finding (not yet
`Critical`, because the duplicate has not survived a full closed
sprint). Exercises the primary path of Operation 1 and the
duplicate-detection rule from `spec/portfolio/portfolio-management/`
§Cross-repository duplicate detection.

## Input prompt

> Audit the portfolio.

## Input files

The active checkout is `claude-shared`; detection passes because
`.claude-plugin/plugin.json` and
`spec/portfolio/portfolio-management/` both exist.

The resolved Portfolio-Member set returned by
`gh api orgs/nolte/repos --paginate` contains, among others,
`nolte/release-tooling` and `nolte/changelog-bot`. Neither carries
the `portfolio: excluded` opt-out marker in `CLAUDE.md`.

`nolte/release-tooling` `project/portfolio.yml` (excerpt):

```yaml
capabilities:
  - name: github-release-publisher
    description: >
      Publishes a GitHub release for the current tag, derives the
      release notes from the merged PRs since the previous tag, and
      attaches the build artefacts produced by the release workflow.
    audience: [release-engineer]
    status: active
    rationale: >
      Owns the `release-publish.yml` workflow used by every Python
      project in the portfolio.
```

`nolte/changelog-bot` `project/portfolio.yml` (excerpt):

```yaml
capabilities:
  - name: release-note-generator
    description: >
      Generates a GitHub release entry for the current tag from the
      merged pull requests since the previous tag and posts it as a
      published release.
    audience: [release-engineer]
    status: active
    rationale: >
      Centralises release-note formatting across the portfolio.
```

The previous Findings-Report under
`.audits/portfolio/2026-04-26.md` does **not** mention any duplicate
between `release-tooling` and `changelog-bot`; this is the first
audit cycle in which both manifests carry the overlapping
capabilities. No closed sprint sits between the previous audit and
this one.

## Expected behaviour

1. **Repository-role detection passes.** The skill confirms it is
   inside `claude-shared` (plugin manifest plus
   `spec/portfolio/portfolio-management/` both present) and selects
   the full Audit operation rather than Bootstrap.
2. **Portfolio-Member set resolved.** The skill calls
   `gh api orgs/nolte/repos --paginate --jq '.[] | select(.archived==false and .private==false) | .name'`,
   cross-checks each candidate for the `portfolio: excluded` marker
   in `CLAUDE.md`, records excluded repositories with their rationale,
   and freezes the resulting set for this audit run.
3. **Manifests collected inline.** For each repository in the
   resolved set the skill fetches `project/portfolio.yml` via
   `gh api repos/nolte/<repo>/contents/project/portfolio.yml`,
   reduces the YAML to a structured per-repository summary
   (declared capabilities, audiences, peer references), and discards
   the raw YAML. Repositories without the file are recorded as
   `missing-manifest` rather than aborting the run.
4. **Four checks executed.** Manifest presence, manifest validity,
   cross-repository duplicate detection (semantic overlap on
   `description`, **not** keyword overlap), and the three gap
   sub-classes all run against the collected summary.
5. **Duplicate surfaced.** The semantic-overlap comparison flags the
   pair
   (`release-tooling:github-release-publisher`,
   `changelog-bot:release-note-generator`) as overlapping: both
   describe publishing a GitHub release for the current tag with
   notes derived from merged PRs since the previous tag. The skill
   classifies this as a **fresh** duplicate because the previous
   Findings-Report did not record it, and assigns severity `Warning`
   per the spec's tolerance window (`Critical` is reserved for
   duplicates that survive one closed sprint).
6. **Findings-Report written** at
   `.audits/portfolio/2026-05-10.md` with the four
   `review-plan`-mandated sections in declared order — `## Scope`,
   `## Summary`, `## Findings`, `## Processing log` — and Title-Case
   severities only. The duplicate finding reads roughly:
   `[portfolio-management §Cross-repository duplicate detection] Warning — release-tooling:github-release-publisher overlaps with changelog-bot:release-note-generator …`
   and includes the resolution path quoted from the spec (operator
   opens a cross-repo PR; the skill never consolidates).
7. **Per-severity counts confirmed.** The closing message in the
   operator's language reports the path of the new Findings-Report
   (`/.audits/portfolio/2026-05-10.md`), the per-severity counts
   (e.g. `Critical: 0`, `Warning: 1`, `Suggestion: 0`, `Info: 0`),
   and points the operator at `continuous-improvement`'s
   specialist-dispatch loop as the next step.
8. **Hard rules honoured.** No `project/portfolio.yml` modified in
   any Portfolio-Member repository; no PR opened against
   `release-tooling` or `changelog-bot`; no capability marked
   `deprecated` from the audit side; the `Warning` severity is
   written exactly in Title Case (no `WARNING`); the Findings-Report
   lives only under `claude-shared/.audits/portfolio/`.
