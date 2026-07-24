# Claude Code Permission Allowlist Maintenance

Status: draft
Portfolio-Scope: portfolio

## Context
Claude Code (CLI, plugin, and Agent SDK runs) prompts the user for confirmation on any shell or MCP tool call that isn't either autoallowed by the harness or listed in the current project's permission allowlist. Without a curated, committed allowlist, authors confirm the same handful of read-only `git` / `gh` / `task` invocations again and again during day-to-day work, which erodes attention and conditions humans to accept confirmation prompts reflexively. Every repository in the portfolio therefore ships a version-controlled `.claude/settings.json` with an explicit `permissions.allow` list covering the small, well-understood set of read-only commands whose prompts add no safety value. The list is a living artifact that needs a defined maintenance process so it neither ossifies (missing commands that have since become common) nor silently sprawls (inheriting dangerous wildcards from developer-local configs).

## Goals
- Every repository in the portfolio ships a committed `.claude/settings.json` whose `permissions.allow` list covers the read-only commands that are demonstrably frequent in that repository
- The allowlist is updated deliberately and at documented triggers, not through ad-hoc one-off entries that slip in unreviewed
- Selection criteria, forbidden pattern classes, and the interplay with `fewer-permission-prompts` / `update-config` skills are written down so humans and AI agents agree on what belongs in the file
- Entries can never escalate privilege or bypass a spec rule—in particular, no pattern on the committed list may undermine the pull-request-workflow `Automerge trigger protocol` or the `CI gate into develop` requirements

## Non-Goals
- User-global configuration at `~/.claude/settings.json`: that belongs to the individual developer and is out of scope
- Developer-local overrides in `.claude/settings.local.json`: these are deliberately ungoverned, reflecting per-developer risk appetite, and are out of scope
- Hooks, environment variables, or any `.claude/settings.json` field other than `permissions.allow`: those are covered by the `update-config` skill and potentially future specs, not here
- Portfolio-wide distribution of a shared base allowlist (whether via an `_extends`-style mechanism like `.github/settings.yml`). Default (revisit): each repository owns its `.claude/settings.json` allowlist; there's no central or `_extends`-style base list, because the Claude Code harness has no inheritance mechanism. Revisit only when a `portfolio-audit` run flags the allowlist block under `portfolio-management` §Cross-repository copy-paste smell (the same base block across three or more Portfolio-Member repos), at which point a generator or sync skill—not an `_extends` config edit—becomes the candidate solution.

## Requirements

### Scope and location
- **MUST** keep the committed, authoritative allowlist in `.claude/settings.json` at the repository root; `.claude/settings.local.json` is explicitly out of scope (stays developer-owned and isn't committed)
- **MUST** track `.claude/settings.json` in Git; the file **MUST NOT** appear in `.gitignore`
- **MUST NOT** include non-read-only patterns, interpreter wildcards, or task-runner wildcards (`Bash(task *)`, `Bash(npm run *)`, `Bash(bun run *)`, and equivalents) in `.claude/settings.json`; exact task targets such as `Bash(task lint)` are permitted

### Selection criteria for new entries
- **MUST** ensure every new pattern satisfies all three conditions below:
  1. is documented as frequently occurring in a defensible sample—multiple recent sessions, multiple repositories, or a traceable spec requirement such as pull-request-workflow §Pre-push verification
  2. is read-only in the sense that it doesn't change remote state, secrets, or shared infrastructure; local filesystem writes are only acceptable as a side effect of a read-only operation (for example `git fetch` updating local refs, or `task docs` running `mkdocs build` into `site/`) and **MUST** be justified explicitly when in doubt
  3. isn't already covered by the Claude Code autoallowed list (see the `fewer-permission-prompts` skill, step 4); redundant entries are omitted
- **SHOULD** choose the narrowest pattern form that still covers observed usage: the exact form (`Bash(git fetch)`) when one invocation dominates, the prefix form (`Bash(git fetch *)`) only when flag variance has been observed
- **MAY** list both the exact and prefix forms in parallel when both variants genuinely occur in observed usage
- **SHOULD** treat a recurring read-only GitHub MCP read tool the same way as a read-only `gh` command: it's read-only, occurs frequently in GitHub-touching skills and agents, and belongs in the allowlist so it doesn't prompt, evaluated against the same three conditions above. The reference server is registered under the server name `github`, so a tool is written `github:<tool>` in prose (the `ServerName:tool_name` syntax from `spec/claude/skill-management/`) and `mcp__github__<tool>` as a `.claude/settings.json` allowlist entry. The least-privilege read set is: `github:get_me` and `github:list_repository_collaborators` (the trust-resolution reads `spec/claude/trusted-author-injection-guard/` requires), plus `github:list_issues`, `github:issue_read`, `github:search_issues`, `github:list_pull_requests`, `github:pull_request_read`, `github:search_pull_requests`, `github:list_branches`, `github:list_commits`, `github:get_file_contents`, `github:list_releases`, `github:get_latest_release`, `github:get_release_by_tag`, `github:list_discussions`, `github:get_discussion_comments`, and `github:list_discussion_categories`
- **MUST NOT** allowlist a write-capable GitHub MCP tool (issue or pull-request create/update, merge, file writes, review submission) on the committed list—only read tools qualify, mirroring the mutation-capable-`gh`-wildcard exclusion above; a write tool stays off the list so it still prompts

### Maintenance cadence and triggers
- **MUST** review the allowlist at the latest after any significant refactor of the project's Claude workflow or when new skills, new Taskfile targets, or new automation commands are introduced—event-driven, not calendar-driven
- **SHOULD** run a drift check at least once per quarter (or on the next significant spec update, whichever comes first) via the `fewer-permission-prompts` skill to add newly common read-only patterns and prune obsolete entries
- **MUST** state the reason for any pattern removal in the commit message (for example "upstreamed into the Claude Code autoallow list," "command is no longer used")

### Authoring flow integration
- **MUST** run every change to `.claude/settings.json` through the regular pull-request-workflow process—no direct commits to `develop`, no bypass via `settings.local.json`
- **SHOULD** use a Conventional Commits type of `chore` or `docs` according to the nature of the change: `chore` for pure allowlist maintenance, `docs` when the companion spec is touched alongside
- **MUST** run `task lint` locally before every push, as required by pull-request-workflow §Pre-push verification

### Relationship to `settings.local.json` and `~/.claude/settings.json`
- **MAY** keep broader patterns in `.claude/settings.local.json` or `~/.claude/settings.json` at the developer's own risk; those files are out of scope for this spec
- **MUST NOT** copy a broad pattern from `settings.local.json` or `~/.claude/settings.json` into the committed `.claude/settings.json` without re-evaluating it against the selection criteria above—in particular, mutation-capable wildcards such as `Bash(git *)`, `Bash(gh api *)`, or `Bash(gh pr *)` stay out of the committed file
- **MUST NOT** treat this committed file as the place to enable autonomous or background agents: a non-interactive agent that needs mutation-capable commands (`git commit` / `git push`, `gh pr create`, a task runner) to act inside a worktree is authorized through the session `/permissions` grant or `.claude/settings.local.json` per `spec/project/parallel-working-copies/` §Harness-initiated and agent-initiated worktrees, never by adding those patterns here

### Governance
- **MUST** resolve any discrepancy between this spec and `.claude/settings.json` by editing the committed file—not by silently relaxing the spec
- **SHOULD** reference the `fewer-permission-prompts` skill as the tool that *proposes* candidates; the decision to accept, narrow, or reject a candidate belongs to the author applying the criteria above

## Acceptance Criteria
- [ ] `.claude/settings.json` exists at the repository root and contains at least one `permissions.allow` array
- [ ] No entry in `.claude/settings.json` matches one of the forbidden pattern classes from §Scope and location (interpreter wildcards, task-runner wildcards, mutation-capable gh/git wildcards)
- [ ] `.claude/settings.local.json` is either not committed or is explicitly listed in `.gitignore`
- [ ] For the last 5 PRs merged into `develop` that touched `.claude/settings.json`, the PR body justified each change (new candidates, removed entries with their reason): spot-check via `gh pr list --state merged --base develop --search '.claude/settings.json' --json number,title,body`
- [ ] No spec-internal MUST rule is undermined by an entry in `.claude/settings.json`: in particular, no entry permits `gh pr merge *` or an equivalent that would bypass the pull-request-workflow `Automerge trigger protocol`

## Open Questions

_All previously deferred open questions were settled on 2026-06-06: each provisional default is now the standing rule. The per-item decisions and rationale are preserved in git history (decision log, 2026-06-06)._
