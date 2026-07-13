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

Refs #378, #382.
