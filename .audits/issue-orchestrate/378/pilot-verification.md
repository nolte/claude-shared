# R-10 MCP pilot verification — F-13 acceptance-3

Work package **P6** (feature **F-13**): the `portfolio-inflight-collector` agent is the
Tier-1 pilot proving the optional-GitHub-MCP pattern end-to-end. This file records the
run-both-and-diff identical-output proof that satisfies F-13 **acceptance-3** (the
`verifies_sprint_value` criterion) and the P3 convention's normative invariant
(`spec/claude/mcp-tool-preference/` §Optionality and fallback: "the same inputs MUST
produce identical artefacts and decisions on either path").

## Server-name resolution (load-bearing precondition)

The connected GitHub MCP server is registered under the server name **`github`** (hosted
endpoint `https://api.githubcopilot.com/mcp/`, per-machine PAT). Verified live in-session:
`get_me` → `login: nolte`, and every exposed tool is named `mcp__github__*`. Claude Code
couples the tool prefix hard and silently to the server name, so `mcp__github__*` matches
and `mcp__GitHubMCP__*` would fail without warning. All artefacts were therefore
standardised on `github`, and the already-merged specs/skills/agents that referenced the
server as `GitHubMCP:` were drift-fixed to `github:` (prose `ServerName:tool_name` form).

## Method

Same repo set for both runs: `nolte/claude-shared` (single-repo targeted collection).
For each data source the collector's deterministic payload was captured twice — once via the
**MCP-preferred** read tool, once via the **`gh`-only** fallback — reduced to the identifiers
the collector keys on, then canonicalised (`jq -S -c`, sorted keys, compact) and diffed.
The per-run `Collected:` timestamp header and the rate-limit footer are excluded from the
diff, exactly as F-13 acceptance-3 scopes it.

| Data source | MCP-preferred read | `gh` fallback | Diff |
| --- | --- | --- | --- |
| Open issues | `mcp__github__list_issues` | `gh issue list` | **identical** (4 issues: 371, 376, 378, 382) |
| Open PRs incl. drafts | `mcp__github__list_pull_requests` | `gh pr list` | **identical** (1 PR: 387, draft) |
| Branches | `mcp__github__list_branches` | `gh api …/branches` | **identical** (4: develop, feat/r10-mcp-feature-decompose, gh-pages, main) |
| release-drafter drafts | `mcp__github__list_releases` | `gh api …/releases` | **identical** (1 draft: v0.1.10) |

Result: **the deterministic collection payload is byte-identical across the MCP-preferred and
`gh`-only paths** for every data source where the two paths genuinely differ. acceptance-3 met.

A structural note surfaced and was normalised away, not hidden: MCP `list_issues` wraps its
result as `{"issues":[…]}` while `gh issue list` returns a bare array — the collector's
reduction to a canonical per-source summary is exactly what makes the two paths equivalent.

## Data sources that stay on `gh` on both paths (OQ-D)

These contribute identically to both runs by construction, so they neither strengthen nor
weaken the diff; they are the documented `gh`-stays cases the pilot deliberately exercises:

- **4a — review-thread `isResolved` state:** no clean MCP tool for the
  `pullRequest.reviewThreads.isResolved` flag → `gh api graphql` on both paths.
- **Repository default branch:** no clean single-purpose MCP equivalent → `gh` on both paths.
- **4b — open Discussions:** the hosted `api.githubcopilot.com/mcp/` endpoint used in this
  pilot did **not** expose the discussions toolset (`list_discussions` /
  `get_discussion_comments` / `list_discussion_categories` / `get_discussion` are all absent
  from the connected catalogue), so data source 4b fell back to `gh api graphql` here — a
  correct silent degradation. A self-hosted `github-mcp-server` with the discussions toolset
  enabled would take the MCP path. The allowlist and P3 documentation keep the discussions
  read tools listed because the reference server exposes them; their absence on this endpoint
  is the graceful-degradation contract working as designed, not a gap.

## Acceptance status

- **acceptance-1** (prefers MCP when present) — met: MCP reads used for issues/PRs/branches/releases.
- **acceptance-2** (`gh` completes when absent) — met: the `gh` fallback path produced the full collection.
- **acceptance-3** (identical deterministic payload) — **met** (this proof).
- **acceptance-4** (cites `spec/claude/mcp-tool-preference/`) — met: agent body §GitHub MCP-preferred reads.

## Tier-1/2/3 rollout (F-14 / F-15 / F-16)

The optional-MCP pattern was broadened from the pilot to the rest of the GitHub-touching
artefacts. Skills run in the main session and inherit its MCP tools + allowlist, so they
gain a body tooling-note + P3 citation only; the two collector **agents** additionally get
additive `tools:` grants. The allowlist grew by four live-verified read tools
(`search_pull_requests`, `get_file_contents`, `get_latest_release`, `get_release_by_tag`).

Adoption per artefact (verdict from the read/write mapping against the live catalogue):

- **F-14 Tier-1 remainder:** `issue-orchestrate` (issue/PR comprehension → `list_issues`,
  `issue_read`, `search_pull_requests`, `list_pull_requests`); `portfolio-manifest-collector`
  agent (manifest fetch → `get_file_contents`); `workflow-health-triage` — **no MCP reads**:
  its entire GitHub read surface is Actions/workflow-run data, absent on the connected server,
  so it stays on `gh` (server-agnostic OQ-D note).
- **F-15 Tier-2:** `vocab-drift-scanner` agent (`get_file_contents`, `get_latest_release`),
  `vocab-drift-audit` (`get_latest_release`), `release-notes-curate` (`list_releases`,
  `get_release_by_tag`), `pull-request-merge` (`pull_request_read`, `list_pull_requests`,
  `list_branches`), `continuous-improvement-triage` (`list_pull_requests`, `pull_request_read`
  plus the already-wired trust reads), `sprint-review` (`get_release_by_tag`);
  `portfolio-audit` / `portfolio-inflight-triage` inherit their collector agents;
  `project-structure-apply` — **no MCP reads** (its only read is the GitHub-App install check,
  no MCP tool → `gh`, OQ-D).
- **F-16 Tier-3 (per-artefact go/no-go):** both **GO (narrow)** — `pull-request-create`
  migrates the open-PR collision read (`list_pull_requests`); `release-publish-trigger`
  migrates draft resolution (`list_releases`) and the post-publish verify (`get_release_by_tag`).
  The `gh pr create` / `gh workflow run` dispatches, the required-check-runs gate, all
  workflow-run status reads, and the git-plumbing (push/rebase/reachability) stay on `gh`/git.

Rollout spot-verification (in addition to the pilot's four sources):

- `get_latest_release` (nolte/vale-style) → `v0.1.17`, identical to `gh api …/releases/latest`.
- `get_file_contents` (nolte/claude-shared `project/portfolio.yml`) → identical content and YAML
  fields to the `gh api …/contents/…` fetch.
- **Evidence-driven scope correction:** `search_repositories` was initially mapped as the
  MCP-preferred read for the manifest collector's Portfolio-Member enumeration, then **removed**
  — `nolte` is a user account (`gh api orgs/nolte/repos` 404s), the enumeration is a repo
  *list*, and a ranked eventually-consistent search is not a deterministic list equivalent
  (it could miss a fresh member and break the identical-output invariant). The enumeration
  stays on `gh` (OQ-D), mirroring the pilot collector; `search_repositories` is not allowlisted.

Recurring OQ-D `gh`-stays gaps documented across the rollout: Actions/workflow-run reads
(`gh run`/`gh workflow`, check-run rollup `gh pr checks`), `gh label list` (only single
`get_label` exists), single-repo default-branch reads (`gh repo view --json defaultBranchRef`),
GitHub-App install checks (`gh api /user/installations`), `gh api rate_limit`, and the
Portfolio-Member enumeration. All writes and git-plumbing stay on `gh`/git by contract.

Refs #378, #382.
