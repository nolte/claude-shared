# CLAUDE.md

Orientation for Claude Code and contributors working inside this repository.

## What this repo is

`claude-shared` is a Claude Code **plugin monorepo**: it ships four plugins from one repository, sharing one `spec/` corpus, one Taskfile, and one CI pipeline. Each split is justified by a **distribution-contract** difference per `spec/claude/plugin-scoping/` §"When to split into a separate plugin" — never by topic or count.

- **`nolte-shared`** (repo root) — the common delivery-lifecycle plugin: planning, specs, PR & release workflow, docs/prose, and portfolio. Every adopting repo installs it.
- **`nolte-media`** (`plugins/nolte-media/`) — brand-aware image generation and media processing. Split on a different **runtime/dependency** requirement: it needs external image-generation credentials and binaries (Cloudflare / Gemini / Pollinations API access, `vtracer`) that most consumers neither have nor want.
- **`nolte-engineering`** (`plugins/nolte-engineering/`) — engineering capabilities for code-bearing projects: full-stack implementation, the test-tier and test-cycle suite, the quality gate, frontend/web-UI optimization, and code-security / dependency / license auditing. Split on a different **consumer audience**: code repositories adopt it on top of `nolte-shared`, while non-code repos (docs, content, config) take `nolte-shared` alone.
- **`nolte-claude-dev`** (`plugins/nolte-claude-dev/`) — Claude Code skill/agent authoring: `skill-management`, `skill-review`, `agent-review`, `skills-agents-sweep`, `skill-agent-catalog-apply`, and the `claude-plugin-developer` agent. Split on a different **consumer audience** (F-18 flip 2026-07-22, `.audits/shared-plugin-analysis/2026-07-22-authoring-carve-out-reopen.md`): the majority of consumers install `nolte-shared` for the delivery lifecycle and **never author a skill or agent**, so they should stop carrying the authoring slice's skill-list weight. Adopters who do author skills/agents install it on top of `nolte-shared`. The `spec/claude/` corpus that governs authoring stays repo-wide — it does not move into this plugin.

All four plugins version in **lockstep** — one release line equal to the repository's release tag (the splits are about install-time audience/dependencies, not release cadence). `.github/release-automation.yml` declares each plugin's `plugin.json` `version` plus `marketplace.json` `metadata.version` as the version-bearing files the pre-publish gate aligns; the `chore(release): <tag>` alignment bumps all of them together. Marketplace `plugins[].version` entries are intentionally absent — plugin-version resolution takes each plugin's own `plugin.json` first.

## Layout

- `.claude-plugin/plugin.json` — `nolte-shared` plugin manifest (name, version, author)
- `.claude-plugin/marketplace.json` — marketplace catalog listing **all four** plugins (downstream install source)
- `skills/<name>/SKILL.md` — `nolte-shared` skills; each folder is one skill
- `agents/<name>.md` — `nolte-shared` sub-agents
- `plugins/nolte-media/`, `plugins/nolte-engineering/`, `plugins/nolte-claude-dev/` — the second, third, and fourth plugins: each with its own `.claude-plugin/plugin.json`, `skills/`, and `agents/`, scoped to that root
- `spec/` — bilingual specifications governing all four plugins' skill/agent authoring and project conventions (repo-wide; not shipped with any plugin)
- `docs/` — MkDocs source, bilingual (`docs/de/`, `docs/en/`); the catalog renders each plugin under its own `{skills,agents}/<plugin>/` subtree, configured in `docs/catalog-sources.yml`
- `project/` — this repo's own planning surface: `mission.md`, `goals.md`, `roadmap.md`, plus `features/`, `sprints/`, and `blog-triggers/` (driven by `sprint-execute`, `feature-decompose`, `roadmap-plan`)
- `portfolio/` — portfolio-level data (`tech-stack.yml`, `aggregate.yml`, `schemas/`)
- `scripts/` — repo automation behind the Taskfile targets (`validate_skills.py`, `wip_journal.py`, `check_links.py`, `worktree_add.sh`, …); `validate_skills.py` auto-discovers every in-repo plugin under `plugins/`
- `.claude/` — this repo's own Claude Code config (not shipped with any plugin): `settings.json` wires the journal/guard/validate hooks and permission allowlist; `rules/*.md` are session-loaded instruction rules — a rule with no `paths:` loads every session like `CLAUDE.md`, a `paths:`-scoped rule loads only when a matching file is touched

Plugin skills are namespaced by plugin name — e.g. `/nolte-shared:spec`, `/nolte-media:image-generate`, `/nolte-engineering:quality-gate`, `/nolte-claude-dev:skill-management`.

## Command entry points

Local automation runs through `Taskfile.yml`:

- `task setup` — install pre-commit hooks (run once after cloning)
- `task lint` — pre-commit checks
- `task test` — validate every skill/agent frontmatter (`scripts/validate_skills.py`)
- `task docs` — build the MkDocs site
- `task plugin:reload` — launch Claude Code with this repo loaded as a plugin (dogfooding)
- `task worktree:add -- <branch> [slug]` — create a spec-conformant worktree off `origin/develop` (see §Parallel working copies)
- `task resume` — list this working copy's resumable Claude Code sessions (see §Crash recovery)

## Dogfooding

When developing inside this repository, launch Claude Code with **all** in-repo plugins loaded — the root plugin plus each subdirectory plugin:

```bash
claude --plugin-dir . --plugin-dir ./plugins/nolte-media --plugin-dir ./plugins/nolte-engineering --plugin-dir ./plugins/nolte-claude-dev
```

`task plugin:reload` runs exactly this. Use `/reload-plugins` inside the session to pick up changes without restarting.

## Conventions

- New skills are scaffolded via `/nolte-claude-dev:skill-management`.
- Specs are authored and translated via `/nolte-shared:spec`.
- Project-structure drift is checked via `/nolte-shared:project-structure-apply`.
- Pull requests are created via `/nolte-shared:pull-request-create` following `spec/project/pull-request-workflow/`.

## Authoring rules

- Keep `CLAUDE.md`, `spec/`, and the plugin manifest in sync with what the repo actually ships.
- Never copy plugin-owned skills into a consumer's `.claude/skills/` — distribution happens via the plugin marketplace.
- All generated configuration files (`.github/*.yml`, `Taskfile.yml`, workflow YAML) are written in English for portfolio consistency, regardless of the language used in conversation.

## Parallel working copies (worktrees)

`spec/project/parallel-working-copies/` is the single source of truth. The core rule and the operational reminders for any session running inside this repository:

- **The primary checkout (`~/repos/github/claude-shared/`) is for integration only and MUST stay on `develop` at all times.** Never create, switch to, or commit a feature branch (`feat/`, `fix/`, `chore/`, `docs/`, `exp/`) here — not even when only one feature is in flight. *Every* change to specs, skills, agents, or docs happens in a dedicated worktree that branches off `develop`; the primary checkout is the stable launchpad you branch *from* and merge *into*, never the place you work in. This is the MUST in the spec's §Branch-to-worktree mapping. If you find the primary checkout on a feature branch, that is drift to repair (migrate the branch into a worktree, reset the primary checkout to `origin/develop`), not a state to extend.
- Create worktrees under the per-machine-configurable root `${NOLTE_WORKTREE_ROOT:-~/repos/.worktrees}/claude-shared/<slug>/` (or, for harness-/agent-initiated worktrees, `${NOLTE_WORKTREE_ROOT:-~/repos/.worktrees}/claude-shared/agents/<slug>/`). The root is read from the `NOLTE_WORKTREE_ROOT` environment variable — each machine sets it freely — and defaults to `~/repos/.worktrees`. The conformant way to create one is `task worktree:add -- <branch> [slug]`, which reads that variable, derives the repo from the `origin` remote, and branches off `origin/develop`. Never nest a worktree under `.claude/worktrees/` — the spec's §Path layout forbids it explicitly.
- **Plan before work, then work in a fresh resumable session.** Before any substantive work begins in a newly created worktree, a foundational implementation plan **MUST** be on disk inside it at `.resume/<slug>/plan.md` (gitignored) — `task worktree:add` seeds a stub there for you to fill in. Then do the work in a **fresh top-level session started from the worktree** (`cd <worktree> && claude`), not a dispatched subagent or Workflow run, so it stays recoverable via `task resume` / `claude --resume`. This is the spec's §Lifecycle: Plan before work plus §Claude Code session scoping, and the same operational rule restated under §Crash recovery below.
- Before the first `Agent({isolation: "worktree"})` call in a session, set `CLAUDE_AGENT_WORKTREE_ROOT` (or the equivalent Claude Code settings hook) to a spec-conformant root — pointing it under the same `${NOLTE_WORKTREE_ROOT:-~/repos/.worktrees}/claude-shared/agents/` root — if the harness default would otherwise materialize the worktree under `.claude/worktrees/`.
- This rule is enforced at two layers: a `PreToolUse` hook (`scripts/guard_feature_branch_hook.py`, wired in `.claude/settings.json`) refuses any `git checkout`/`switch`/`branch` onto a `feat/ fix/ chore/ docs/ exp/` branch *in the primary checkout* before it runs, and the `guard-primary-checkout` pre-commit hook (`scripts/guard_primary_checkout.sh`) blocks a commit if the primary checkout is somehow off `develop`. Both no-op inside linked worktrees, where feature branches are correct.

## Crash recovery / resuming interrupted work

A notebook crash, terminal close, or session expiry does **not** destroy in-flight work — Claude Code persists every top-level session transcript under `~/.claude/projects/<encoded-cwd>/`. Two on-disk safety nets make recovery routine:

- **Session-level (covers everything, including free-form work):** run `task resume` in the affected working copy to list its resumable sessions newest-first with their opening prompt, then `claude --resume <id>` (or `claude --continue` for the most recent). This is the first thing to reach for after a crash.
- **Always-on journal:** `scripts/wip_journal.py` is wired as a `SessionStart` / `PostToolUse` / `PreCompact` hook in `.claude/settings.json` and appends a "where was I" trail to the gitignored `.resume/session-journal.md`. `cat .resume/session-journal.md` shows the last files touched and when, per session.
- **Skill-level (structured decision log):** in-scope skills/agents checkpoint to `.resume/<name>/<run-id>.yml` per `spec/claude/resumable-work/`; re-invoking a resumable skill with the same inputs surfaces the resume prompt.

Operational rule: prefer running long feature work as a **top-level session inside the worktree** (`cd <worktree> && claude`) over a dispatched worktree-isolated subagent — only top-level sessions can be `claude --resume`'d; a subagent's transcript lives under its parent and cannot be resumed on its own. This pairs with the **plan-before-work gate** (§Parallel working copies): the foundational plan at `.resume/<slug>/plan.md` records where the work stands, and the resumable session reopens the context that produced it — together they make an interrupted feature recoverable rather than reconstructed.

For multi-source **research** that must survive a crash, prefer the Workflow harness over the built-in `deep-research` skill: a Workflow run persists every dispatched agent transcript and supports `resumeFromRunId`, whereas `deep-research` (a sealed harness built-in) holds fetched sources and verified claims only in conversation context and writes nothing to disk until its final report.

## Blog-author trigger (feature → done)

This repository's blog-author trigger roles (source consumer, blog consumer, the `in_progress → done` trigger event, and the cross-repo write rule) are documented in `.claude/rules/blog-author-trigger.md`, a path-scoped rule that loads automatically while working under `project/features/`, `project/sprints/`, or `project/blog-triggers/`. The authoritative contract is `spec/project/blog-author-trigger/`.
