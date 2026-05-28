# portfolio-inflight-collector — Output shape

The full structure of the in-flight collection report the agent returns. One entry per in-scope Portfolio-Member repository, structured by data source, plus an aggregated overview at the top. The calling `portfolio-inflight-triage` skill parses this shape, so the field set and ordering are load-bearing.

## Contents

- Top-level header (collected timestamp, scope counts, opt-out list)
- Per-repository data sources: open issues, open PRs, branches without active PR, unresolved review threads, open discussions, open release-drafter drafts
- Aggregated overview totals

## Template

```text
# Portfolio In-Flight Collection

Collected: <ISO-8601 timestamp>
Repositories in scope: <n>
Repositories opted out (portfolio: excluded): <n>
Per-source opt-outs honoured: <list of <repo>:<source> or "none">

## Per-Repository Data Sources

### <repo-name>

- inflight.yml override present: yes | no
- inflight.yml raw content: <verbatim YAML string or "absent">

#### Open issues (`issue`)
- <repo-name>/issue/<number>
  - title: <title>
  - createdAt: <ISO-8601>
  - updatedAt: <ISO-8601>
  - daysOpen: <n>
  - daysSinceLastActivity: <n>
  - assignees: <list or "none">
  - labels: <list or "none">
  - hasMaintainerCommentLast30d: yes | no
  - excludedByLabel: false (or true with label name; included only when caller requests excluded-items audit trail)
- ...

#### Open pull requests (`pr`)
- <repo-name>/pr/<number>
  - title: <title>
  - isDraft: yes | no
  - createdAt: <ISO-8601>
  - updatedAt: <ISO-8601>
  - daysOpen: <n>
  - daysSinceLastReviewerActivity: <n>
  - headRefName: <branch>
  - headRefOid: <sha>
  - baseRefName: <branch>
  - mergeable: MERGEABLE | CONFLICTING | UNKNOWN
  - requiredChecksState: SUCCESS | FAILURE | PENDING | NEUTRAL
  - reviewDecision: APPROVED | CHANGES_REQUESTED | REVIEW_REQUIRED | null
  - labels: <list or "none">
- ...

#### Branches without active PR to develop (`branch`)
- <repo-name>/branch/<branch-name>
  - lastPushAt: <ISO-8601>
  - daysSinceLastPush: <n>
  - isDefaultBranch: no (default branch entries are pre-filtered)
  - hasOpenPRToDevelop: no (entries with an open PR to develop are pre-filtered)
- ...

#### Unresolved review-comment threads (`review-thread`)
- <repo-name>/review-thread/<pr-number>:<thread-id>
  - prNumber: <number>
  - threadId: <id>
  - lastCommentAt: <ISO-8601>
  - daysSinceLastComment: <n>
  - hasMaintainerReply: yes | no
  - isResolved: false (resolved threads are pre-filtered)
- ...

#### Open Discussions (`discussion`)
- <repo-name>/discussion/<number>
  - title: <title>
  - createdAt: <ISO-8601>
  - updatedAt: <ISO-8601>
  - daysOpen: <n>
  - lastCommentAt: <ISO-8601 or null>
  - lastCommentAuthor: <login or null>
  - daysSinceLastMaintainerReply: <n or "never">
- ...

#### Open release-drafter drafts (collected on request, for `release_blocking` matrix-axis)
- draft-<id>
  - name: <name>
  - draftHeadShas: <list of SHAs referenced in the draft body or "none">
- ...

### <repo-name>
...

## Aggregated Overview

- Total issues collected: <n>
- Total PRs collected: <n>
- Total branches-without-PR collected: <n>
- Total unresolved review-threads collected: <n>
- Total open discussions collected: <n>
- Total open release-drafter drafts collected: <n>
- Repositories opted out (portfolio: excluded): <list or "none">
- Per-source opt-outs honoured: <list of <repo>:<source> or "none">
- Repositories with project/inflight.yml override: <list or "none">
- Fetch errors encountered: <list of <repo>:<source>:<error> or "none">
- Rate-limit status at collection end: remaining <n> / reset <ISO-8601>
```
