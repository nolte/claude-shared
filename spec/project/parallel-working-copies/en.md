# Parallel Working Copies

Status: draft

## Context
A single primary checkout of a repository can hold only one branch at a time. As soon as a contributor (human or AI agent) wants to advance two or more feature branches in parallel (for example, drafting a spec on `feat/parallel-working-copies` while a long-running build runs on `feat/mermaid-diagrams`), switching branches in place destroys the working tree of whichever branch is paused: uncommitted edits collide, build outputs invalidate, IDE indexes thrash, and any tooling that has cached the cwd (Claude Code sessions, language servers, watchers) is forced to re-bootstrap.

`git worktree` solves this without cloning: it adds a second working tree that shares the same `.git` object database but has its own independent index, working files, and `HEAD`. This spec defines the conventions under which the portfolio uses worktrees so that parallel feature work is reliable, auditable, and consistent with the existing branching, project-structure, and pull-request specs.

Readers: contributors (human and AI agents) doing parallel feature work in this portfolio's repositories, plus reviewers who verify worktree hygiene before merge.

## Goals
- Allow a contributor to advance two or more feature branches in parallel without the working tree of one branch overwriting another
- Provide stable conventions for worktree paths, branch-to-worktree mapping, and lifecycle (create, use, retire) so the layout is predictable across repositories and contributors
- Define how Claude Code sessions are scoped to worktrees so `CLAUDE.md` resolution, current-working-directory assumptions, and plugin loading remain coherent
- Reserve the primary checkout for the integration role (sitting on `develop`) so that it remains available for integration tasks (rebases, conflict resolution, release inspection) even while feature work is in flight; the operative rule is the SHOULD in Requirements §Branch-to-worktree mapping

## Non-Goals
- Branch naming and protection rules—defined in `spec/project/branching-model/`
- Pull-request creation, review, and merge mechanics—defined in `spec/project/pull-request-workflow/` and the `pull-request-create` / `pull-request-merge` skills
- Release automation, version bumping, and `main` refresh—defined in `spec/project/release-automation/` and `spec/project/branching-model/`
- Repository scaffolding (`Taskfile.yml`, `.github/`, MkDocs)—defined in `spec/project/project-structure/`
- IDE-specific multi-root workspaces, devcontainer setups, or remote-development tooling
- Resolution of merge conflicts between feature branches—a normal `git merge` / `git rebase` concern, unaffected by whether the work happened in a worktree
- CI runners and ephemeral cloud development environments that clone a fresh workspace per run—those start from a clean state by construction and don't require worktree conventions; this spec governs persistent local working copies

## Requirements

### Path layout
- **MUST** place every additional worktree outside the primary checkout's directory tree; a worktree path **MUST NOT** be nested under the primary repository directory
- **SHOULD** name worktrees as a sibling of the primary checkout in the form `<repo>-<short-slug>/` (for example, the primary checkout `~/repos/github/claude-shared/` plus the worktree `~/repos/github/claude-shared-mermaid/`); the `<short-slug>` is a kebab-case abbreviation of the feature, not necessarily identical to the branch name
- **MAY** instead place worktrees under a centralized layout `~/repos/.worktrees/<repo>/<short-slug>/` when a contributor prefers a single root for all worktrees; mixing both layouts within one machine is permitted but **SHOULD** be avoided per repository
- **MUST NOT** place a worktree path inside another repository's working tree, inside `node_modules/`, inside `.venv/`, or inside any other directory that a tool may delete or rewrite wholesale

### Branch-to-worktree mapping
- **MUST** check out exactly one branch per worktree; a worktree **MUST NOT** be left in a detached-HEAD state for ongoing feature work (detached HEAD is acceptable only for short-lived inspection tasks such as `git worktree add --detach` for a bisect)
- **MUST** ensure that no branch is checked out in two locations simultaneously; the primary checkout and any worktree together **MUST** present each branch at most once (this is a property `git` enforces—the spec restates it because violations indicate a process error, not a tooling error)
- **SHOULD** keep the primary checkout on `develop` whenever parallel feature work is active, so the primary checkout remains available for integration tasks (rebases, conflict resolution, release inspection) without forcing a worktree teardown
- **MAY** retain a feature branch in the primary checkout when only one feature is in flight; the moment a second feature starts, that feature **SHOULD** move into a worktree rather than displacing the existing branch

### Lifecycle: Create
- **MUST** create new worktrees with `git worktree add -b <branch> <path> <base-ref>` so the branch is created as part of the worktree command and the base ref is explicit
- **SHOULD** use `origin/develop` (after `git fetch origin develop`) as the base ref rather than the local `develop`, so the worktree starts from the remote tip and the primary checkout's local `develop` is irrelevant to the worktree's starting point
- **MUST** follow the branch-prefix rules from `spec/project/branching-model/` (`feat/`, `fix/`, `chore/`, `docs/`, `exp/`); the worktree's path slug **MAY** drop the prefix for brevity but the branch itself **MUST NOT**

### Lifecycle: Retire
- **MUST** remove a worktree with `git worktree remove <path>` once its pull request is merged or abandoned; deleting the directory with `rm -rf` is forbidden because it leaves the worktree registered in `.git/worktrees/` and produces "missing" entries in `git worktree list`
- **MUST** delete the local branch (`git branch -d <branch>` or `-D` if the branch was merged via squash) after the worktree is removed, so stale local branches don't accumulate
- **SHOULD** run `git worktree prune` periodically (or after a forced removal) to reap administrative entries for worktrees whose directories disappeared
- **MUST NOT** retire the primary checkout via `git worktree remove`; the primary checkout is the linked-worktree root, not a removable worktree

### Uncommitted changes between worktrees
- **MUST NOT** copy uncommitted changes between worktrees through the filesystem (`cp`, `rsync`, editor "save as"); each worktree's working tree is independent and a filesystem copy bypasses the git index and produces silently divergent state
- **MUST** transfer uncommitted work between worktrees through git: `git stash push` in the source worktree, then `git stash apply` (or `pop`) in the target worktree, or via a temporary commit pushed to a shared remote ref
- **SHOULD** prefer a temporary commit over `git stash` when the work needs to survive a long delay, so the change is durable on disk via a commit object rather than the stash reflog

### Claude Code session scoping
- **SHOULD** start one Claude Code session per worktree, launched from the worktree's root directory (`cd <worktree>; claude`) so that `CLAUDE.md` hierarchy resolution, the auto memory project namespace, and current-working-directory defaults all bind to the worktree
<!-- vale Microsoft.Contractions = NO -->
- **MAY** continue using a single session across worktrees by passing absolute paths to file-reading tools and prefixing shell commands with `cd <worktree> && …`; this is supported but **SHOULD NOT** be the default, because the harness resets the shell `cwd` between bash invocations and `CLAUDE.md` resolution remains anchored to the original session's launch directory
<!-- vale Microsoft.Contractions = YES -->
- **MUST NOT** edit a file via a Claude Code session whose launch directory is a different worktree without using the absolute path, because relative-path tooling will resolve to the wrong working tree
- **MUST NOT** run `task plugin:reload` (or any equivalent plugin-development command from `claude-shared`) in two sessions that target the same plugin source root simultaneously; each Claude Code session loads its own plugin image, but two sessions reloading the same source root concurrently produce races on file watchers and reload semantics

### Local state and untracked configuration
- **MUST** treat untracked, machine-local configuration files (`.env`, `.claude/settings.local.json`, IDE workspace files, build caches, `node_modules/`, `.venv/`) as worktree-local; each worktree maintains its own copy
- **MUST NOT** symlink machine-local configuration from a worktree back to the primary checkout or to another worktree; symlinks across worktrees create hidden coupling that breaks the isolation guarantee this spec exists to provide
- **SHOULD** rebuild language-specific environments (`uv sync`, `npm install`, `task setup`) inside each worktree on first use rather than reusing the primary checkout's `.venv/` or `node_modules/`

### Interaction with other portfolio specs
- **MUST** continue to follow `spec/project/pull-request-workflow/` for PR creation from a worktree; the worktree's branch is pushed and the PR opened identically to a primary-checkout branch
- **MUST** keep `spec/project/branching-model/`'s rule that `main` is presentation-only; a worktree **MUST NOT** be created against `main` for feature work
- **MUST** apply `spec/project/quality-gate/` inside each worktree before opening or marking a PR ready, because the worktree has its own working tree and a green gate in a different worktree isn't evidence for this one

## Acceptance Criteria
- [ ] `git worktree list` lists the primary checkout plus one entry per active feature branch and no entries marked `prunable`
- [ ] No worktree path is nested under the primary checkout's directory
- [ ] No branch appears in more than one worktree-list entry
- [ ] When two or more features are in flight, the primary checkout is on `develop`
- [ ] After a PR is merged, neither `git worktree list` nor `git branch --list` mentions the retired branch
- [ ] No worktree contains a symlink that resolves to a path inside another worktree or the primary checkout (excluding shared `.git` administrative links, which `git worktree` manages itself)
- [ ] Claude Code sessions opened against a worktree resolve the worktree's own `CLAUDE.md` (verifiable by inspecting the session's loaded project instructions)
- [ ] Each worktree carries its own `.venv/`, `node_modules/`, or other ecosystem-local environment when one is required to run the project's quality gate
- [ ] No active feature worktree (one whose registered branch starts with `feat/`, `fix/`, `chore/`, `docs/`, or `exp/`) is in a detached-HEAD state, as listed by `git worktree list --porcelain`
- [ ] No worktree's registered branch is `main`, as listed by `git worktree list --porcelain`
- [ ] Every PR opened from a worktree-originated branch shows a passing project quality-gate check on its own branch tip (verified in the PR's checks tab, not inherited from another worktree)
- [ ] The primary checkout is still listed as the root entry in `git worktree list` (its path matches the primary repository directory and it carries no `bare` annotation), so that the §Lifecycle: Retire `MUST NOT` against removing the primary checkout hasn't been violated

Notes on coverage: Enforcement of the `MUST follow spec/project/pull-request-workflow/` requirement under §Interaction with other portfolio specs is delegated to that spec's own acceptance criteria and is intentionally not duplicated here. The `MUST remove a worktree with git worktree remove` retirement rule is tested authoritatively by AC5 (post-merge, no `git worktree list` or `git branch --list` mention); AC1's `prunable` clause is a supplemental hygiene check that also exercises the SHOULD-level `git worktree prune` rule. The MUST at §Lifecycle: Create requiring `git worktree add -b <branch> <path> <base-ref>` with an explicit base ref is a creation-time convention with no stable post-hoc observable; it's enforced by contributor practice rather than a mechanical AC. The MUSTs at §Uncommitted changes between worktrees (no filesystem copy of uncommitted changes; transfer only via `git stash` or a temporary commit) are likewise contributor-behaviour conventions, analogous to the dual-`task plugin:reload` prohibition under §Claude Code session scoping; no stable post-hoc observable AC is provided.

## Open Questions
- Should this spec prescribe automated cleanup (for example, a `git` alias or shell hook that removes a worktree on PR-merge notification), or is manual cleanup after merge sufficient?
- For repositories where the primary checkout has historically held a long-running feature branch (rather than `develop`), should there be a documented migration path that moves the feature into a worktree and resets the primary checkout to `develop`?
- Is there a portfolio convention for the maximum number of concurrent worktrees per repository before review burden outweighs the parallelism benefit, or is that left to contributor judgment?
- Should the readiness gates from `spec/project/spec-readiness/` and the freshness gates from `spec/project/docs-freshness/` reference this spec when they describe "the working copy under audit," to disambiguate which working tree they mean on a multi-worktree machine?
