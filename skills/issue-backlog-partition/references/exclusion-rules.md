# Exclusion rules

Loaded by operation 1 (`collect`). An issue leaves the survey only when one of these rules
fires, and the artifact records which one. The rules are mechanical on purpose: each is a
predicate over data `gh` returns, so two operators running the survey on the same day
exclude the same set. Anything that needs a judgement about the issue's value is not an
exclusion rule; that issue stays in and ends up **single** at worst.

| Rule id | Predicate | Typical case | Evidence to record |
|---|---|---|---|
| `X-QUESTION` | Primary class is `question` (established in operation 2, applied retroactively) | "How do I…?" issues | the class rationale |
| `X-BOT` | `author.is_bot` is true, or the login matches a known app account (`renovate[bot]`, `dependabot[bot]`, `github-actions[bot]`) | Dependency Dashboard | the author login |
| `X-TEMPLATE` | The label set and title pattern match a recurring template the repository ships (a quarterly audit, a release checklist) | "Quarterly portfolio audit — 2026 Q4" | the matching label set and the title pattern |
| `X-RESOLVED` | `closedByPullRequestsReferences` names a **merged** pull request whose diff covers the issue | fixed but not closed, autolink didn't fire | the PR number and merge SHA |
| `X-INFLIGHT` | An **open** pull request already references and carries the issue | someone is on it | the PR number and its branch |

How to apply:

- Run `X-BOT` and `X-TEMPLATE` on the list output of operation 1; they need no per-issue
  fetch. Run `X-RESOLVED` and `X-INFLIGHT` from the linked-PR data operation 2 collects.
  `X-QUESTION` is applied once the class is known.
- `X-TEMPLATE` needs the template to be identifiable from the repository itself: an issue
  template under `.github/ISSUE_TEMPLATE/`, a scheduled workflow that opens it, or a title
  pattern that recurs across closed issues (`gh issue list --state closed --search
  "<pattern>"`). A pattern asserted from memory doesn't qualify.
- `X-RESOLVED` is a claim about a diff, not about a reference: a merged PR that *mentions*
  the issue without covering it doesn't fire the rule. Read the PR's file list against the
  issue's touch surface before recording it. When in doubt, the issue stays in as single;
  `issue-orchestrate`'s acquisition re-checks self-resolution anyway.
- `X-INFLIGHT` keeps the survey from forming a group around work someone else is already
  landing. Record the PR so the operator can decide whether to wait for it.

What is **not** a rule:

- Age, staleness, or missing activity — that's `portfolio-inflight-triage`'s dimension.
- Missing labels or an unassigned issue.
- The operator's sense that the issue is low value. Record the sense as a note on the row
  if useful; the row stays in the partition.
