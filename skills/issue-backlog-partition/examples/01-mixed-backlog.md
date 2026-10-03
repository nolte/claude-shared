# Example 1: a mixed backlog yields two groups, singles, one pipeline issue, and exclusions

Illustrative repository with 11 open issues on survey day 2026-10-03.

## collect

The paginated `gh api` read of the open issues, pull requests filtered out, returns 11 rows. Mechanical exclusions on the list output:

- Issue 393 "Dependency Dashboard" — `user.login` is `renovate[bot]` → `X-BOT`.
- Issue 676 "Quarterly portfolio audit — 2026 Q4" — labels `chore,audit`, title matches
  the pattern that `.github/workflows/quarterly-audit.yml` opens → `X-TEMPLATE`.

Nine issues go to classification.

## classify

One exploration agent per three issues, briefed with the record schema from
`references/handoff-payload.md`. The condensed records come back; the relevant fields:

| Issue | Class | Bounded | Touch surface (basis) |
|---|---|---|---|
| 812 | bug | yes | `.github/settings.yml` (named in body) |
| 815 | bug | yes | `.github/settings.yml` (named in body) |
| 819 | bug | yes | `.github/settings.yml`, `spec/project/repository-settings/` (named in body) |
| 821 | docs | yes | `docs/en/guides/release.md` (named in body) |
| 822 | docs | yes | `docs/de/guides/release.md` (linked PR touched it) |
| 830 | feature-request | **no** — two outcomes, needs a roadmap item | `src/sync/` (inferred) |
| 833 | refactor | yes | `scripts/check_links.py` (named in body) |
| 834 | bug | yes | `scripts/validate_skills.py` (named in body); asserted cause: "`relative_to(REPO)` breaks outside the clone" — verified by running the script from `/tmp`, output recorded |
| 840 | bug | yes | `.github/workflows/ci.yml` (named in body); `closedByPullRequestsReferences` names merged PR 838 whose diff covers it → `X-RESOLVED` |

Issue 830 goes to the **pipeline** outcome before the graph is built. Issue 840 is excluded
late, with PR 838's merge SHA as evidence.

## partition

Edges with strong evidence:

- 812 — 815: shared touch surface (`.github/settings.yml` named in both bodies).
- 812 — 819: dependency chain (819's body: "needs the `topics` key 812 adds").
- 821 — 822: thematic coupling (same guide, EN and DE; 822's linked PR touched the EN file).

No edge touches 833 or 834: their paths don't intersect anything, and "both are scripts
under `scripts/`" is a directory, not a touch surface named by either issue.

Candidate clusters: {812, 815, 819}, {821, 822}, {833}, {834}.

- `2026-10-03-settings-drift` — "Repair the repository-settings surface so the declared
  topics, branch protection, and spec stay in agreement." Provisional kind: symptom (one
  file). Proposed type: `fix`. Order inside: 812 → 819 → 815.
- `2026-10-03-release-guide-parity` — "Bring the DE release guide back into parity with
  the EN guide." Provisional kind: class (bilingual drift). Proposed type: `docs`.
- 833 and 834 are **singles**.

## sequence

- Overlap test: the two groups' touch-surface unions are disjoint —
  `.github/settings.yml` and `spec/project/repository-settings/` on one side,
  `docs/{en,de}/guides/release.md` on the other.
- Dependency test: neither consumes the other's output.
- Result: **independent**; both may run in separate worktrees concurrently.

## approve

The artifact at `.audits/issue-backlog-partition/2026-10-03.md` carries 11 rows
(reconciliation 11 − 11 = 0), two groups, two singles, one pipeline issue, three exclusions.
One `AskUserQuestion` presents membership, outcomes, and ordering together. The operator
approves, with one note: "834 could be the start of a class — watch for it." Recorded as an
open question, not a change to the partition.

## dispatch

- `issue-batch-orchestrate` receives `2026-10-03-settings-drift` with its three member
  records; its operation 1 re-checks the predicates against the records instead of
  re-fetching the issues.
- `issue-batch-orchestrate` receives `2026-10-03-release-guide-parity` the same way.
- `issue-orchestrate` receives 833, then 834, each with its record; 834's verified cause
  arrives with the command output attached.
- `roadmap-plan` receives 830 with `bounded: false` and the two-outcome rationale.

Each hand-off is appended to the checkpoint before the next starts. The skill stops; no
branch, no pull request.
