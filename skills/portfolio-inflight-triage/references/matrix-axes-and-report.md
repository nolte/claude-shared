# Matrix-Axes Detection MUSTs and Findings-Report Shape

## Table of contents

- Matrix-axis detection MUSTs (step 5 of `SKILL.md` operation Run)
- Severity mapping (step 6 of `SKILL.md` operation Run)
- Findings-Report shape (step 9 of `SKILL.md` operation Run)
- Spec anchors recap

Detailed reference content split out of `SKILL.md` per `spec/claude/skill-management/` §"Authoring quality" to keep `SKILL.md` under the 5,000-token compaction-survival cap. Load when running step 5, step 6, or step 9 of the Run operation.

## Matrix-axis detection MUSTs (step 5)

Derive the four matrix axes per `spec/portfolio/portfolio-inflight-management/` §Classification and prioritisation for every stalled item. Detection MUSTs are non-negotiable:

- **`security_relevance: true`** — a CVE indicator in the repository's dependency surface (cross-reference the collected PR labels and any dependency-audit signal the operator supplied), a supply-chain advisory referenced by the lockfile, or a secret-scanning leaked-credential alert. Default `false` when no signal is present.
- **`release_blocking: true`** — detected when either (a) the PR carries a `release-blocker` label (case-insensitive match against the collected `labels` field), OR (b) the PR's `headRefOid` appears in the body of an open `release-drafter` draft on the same repository (the collector returned the draft list under `Open release-drafter drafts`; match the PR's head SHA against each draft's `draftHeadShas`). Repositories without `release-drafter` configured rely on the label signal alone. No inference, no fuzzy matching.
- **`age_multiplier`** — the ratio of the item's age (or last-activity gap, whichever drives the threshold) to the applied threshold value: `< 1×` for sub-threshold items the operator chose to surface, `1×–2×` for items past threshold, `> 2×` for the `Warning` driver from §Classification and prioritisation.
- **`cross_repo_blocking: true`** — scan every *other* Portfolio-Member's `project/roadmap.md` and every `project/sprints/*.md` in the source tree (via `Read` against the active `claude-shared` checkout — the collector intentionally doesn't perform this scan per its own scope boundaries; the read-only text scan is the skill's job). Look for the finding's short cross-reference (`nolte/<repo>#<number>`) or the full GitHub URL (`https://github.com/nolte/<repo>/(issues|pull)/<number>`). Exact-string match only; no inference, no fuzzy matching, per the §Classification and prioritisation `MUST` on `cross_repo_blocking` detection.

## Severity mapping (step 6)

Classify into the canonical four severities per `spec/portfolio/portfolio-inflight-management/` §Classification and prioritisation and `spec/claude/review-plan/` §Severity scale:

- **`Critical`** — `security_relevance: true` OR `release_blocking: true` OR `cross_repo_blocking: true`.
- **`Warning`** — `age_multiplier > 2×` (stalled past 2× the threshold), OR blocking a non-release sprint feature, OR PR with `mergeable: CONFLICTING` against `develop`.
- **`Suggestion`** — `age_multiplier` between `1×` and `2×` and not blocking, OR a branch-without-PR older than 30 days, OR an unresolved review-comment thread older than 7 days on a non-blocking PR.
- **`Info`** — observation worth recording but not action-requiring: per-source opt-out marker, a recently stalled item still inside the noise window, an item closed since the previous audit, persisted `Critical` from the previous audit per §Integration with continuous-improvement `MAY`.

When an item matches multiple rows, pick the higher severity per §Classification and prioritisation `SHOULD`. Never invent a severity outside the canonical four — `BLOCKER`, `HIGH`, `MEDIUM`, ALL-CAPS variants are explicitly forbidden per §Classification and prioritisation `MUST NOT` and would themselves be a `review-plan` violation in the rendered report.

## Findings-Report shape (step 9)

Write the Findings-Report at `.audits/portfolio-inflight/<YYYY-MM-DD>.md` in the `claude-shared` repository, conforming to `spec/claude/review-plan/`. Required structure:

- **Frontmatter** per `spec/claude/review-plan/` §Frontmatter: `review-type: portfolio-inflight`, `target: .` (the whole portfolio), `target-kind: portfolio`, `specs-applied: [{slug: portfolio-inflight-management, sha: <current-git-sha>}]`, `repo-revision: <current-git-sha>`, `created: <YYYY-MM-DD>`, `status: open`.
- **`## Scope`** — one paragraph naming the resolved Portfolio-Member set (count + opt-outs), the four data sources collected, the threshold-override decisions confirmed in step 3, and any explicitly out-of-scope concerns (private repositories, archived repositories, non-`nolte/*` forks).
- **`## Summary`** — per-severity bullet counts (`Critical: <n>, Warning: <n>, Suggestion: <n>, Info: <n>`), per-repository counts table (recommended `SHOULD` from §Findings-Report shape), single-line go/no-go statement.
- **`## Findings`** — structured **first by severity** (`### Critical` → `### Warning` → `### Suggestion` → `### Info`, omitting empty subsections), **within each severity by repository name alphabetical**, **within each per-repository block by data source** (issues → PRs → branches → review-comments → discussions), **within each data source by ascending finding identifier**. Per-finding format follows `spec/claude/review-plan/` §Findings format (four-line checkbox structure: opening statement + `Where` / `Fix` / `Verify`). The bracketed prefix cites the originating spec rule verbatim, for example `[portfolio-inflight-management §Classification and prioritisation]`. Per-finding fields enumerated by §Findings-Report shape `MUST`: identifier `<repo>/<source>/<id>`, data-source label, staleness measure (days open, days since last activity), recommended specialist slug (or "no specialist matches" with roster-gap note), recommended-action sentence with slash-command verbatim when applicable, severity classification with all four matrix-axes input values (for example `security_relevance: false, release_blocking: true, age_multiplier: 3×, cross_repo_blocking: false`).
- **`## Processing log`** — append-only; seed with the audit-run line `<YYYY-MM-DD>—audit-run—collected from <n> repositories—<actor>` and the per-confirmation-gate decisions from steps 3 and 7.

## Spec anchors recap

The rules this reference distils are owned by:

- `spec/portfolio/portfolio-inflight-management/` §Classification and prioritisation — the four matrix axes, the detection MUSTs, the severity mapping, the higher-severity tie-break, the `MUST NOT` on invented severities
- `spec/portfolio/portfolio-inflight-management/` §Findings-Report shape — the write path, the structure rules, the per-finding required fields, the bracketed spec citation, the `MUST NOT` on raw-body inclusion
- `spec/claude/review-plan/` §Severity scale — the canonical four-stage vocabulary (`Critical` / `Warning` / `Suggestion` / `Info`)
- `spec/claude/review-plan/` §Frontmatter, §Plan body structure, §Findings format — the artefact frame this report fits into

When the spec disagrees with this reference, the spec wins. Propose a skill update rather than silently diverging.
