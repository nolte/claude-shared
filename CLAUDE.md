# CLAUDE.md

Orientation for Claude Code and contributors working inside this repository.

## What this repo is

`claude-shared` is a single Claude Code plugin published as `nolte-shared`. It bundles reusable skills, agents, and specifications so Claude Code workflows stay consistent across the nolte portfolio.

## Layout

- `.claude-plugin/plugin.json` — plugin manifest (name, version, author)
- `.claude-plugin/marketplace.json` — marketplace catalog (downstream install source)
- `skills/<name>/SKILL.md` — reusable skills; each folder is one skill
- `agents/<name>.md` — reusable sub-agents (when present)
- `spec/` — bilingual specifications that govern skill/agent authoring and project conventions
- `docs/` — MkDocs source, bilingual (`docs/de/`, `docs/en/`)

Plugin skills are namespaced by plugin name — e.g. `/nolte-shared:spec`, `/nolte-shared:skill-management`.

## Command entry points

Local automation runs through `Taskfile.yml`:

- `task setup` — install pre-commit hooks (run once after cloning)
- `task lint` — pre-commit checks
- `task test` — validate every skill/agent frontmatter (`scripts/validate_skills.py`)
- `task docs` — build the MkDocs site
- `task plugin:reload` — launch Claude Code with this repo loaded as a plugin (dogfooding)

## Dogfooding

When developing inside this repository, launch Claude Code with the plugin pointed at the repo root:

```bash
claude --plugin-dir .
```

Use `/reload-plugins` inside the session to pick up changes without restarting.

## Conventions

- New skills are scaffolded via `/nolte-shared:skill-management`.
- Specs are authored and translated via `/nolte-shared:spec`.
- Project-structure drift is checked via `/nolte-shared:project-structure-apply`.
- Pull requests are created via `/nolte-shared:pull-request-create` following `spec/project/pull-request-workflow/`.

## Authoring rules

- Keep `CLAUDE.md`, `spec/`, and the plugin manifest in sync with what the repo actually ships.
- Never copy plugin-owned skills into a consumer's `.claude/skills/` — distribution happens via the plugin marketplace.
- All generated configuration files (`.github/*.yml`, `Taskfile.yml`, workflow YAML) are written in English for portfolio consistency, regardless of the language used in conversation.

## Parallel working copies (worktrees)

`spec/project/parallel-working-copies/` is the single source of truth. Two operational reminders for any session running inside this repository:

- Create worktrees under `~/repos/.worktrees/claude-shared/<slug>/` (or, for harness-/agent-initiated worktrees, `~/repos/.worktrees/claude-shared/agents/<slug>/`). Never nest a worktree under `.claude/worktrees/` — the spec's §Path layout forbids it explicitly.
- Before the first `Agent({isolation: "worktree"})` call in a session, set `CLAUDE_AGENT_WORKTREE_ROOT` (or the equivalent Claude Code settings hook) to a spec-conformant root if the harness default would otherwise materialize the worktree under `.claude/worktrees/`.

## Crash recovery / resuming interrupted work

A notebook crash, terminal close, or session expiry does **not** destroy in-flight work — Claude Code persists every top-level session transcript under `~/.claude/projects/<encoded-cwd>/`. Two on-disk safety nets make recovery routine:

- **Session-level (covers everything, including free-form work):** run `task resume` in the affected working copy to list its resumable sessions newest-first with their opening prompt, then `claude --resume <id>` (or `claude --continue` for the most recent). This is the first thing to reach for after a crash.
- **Always-on journal:** `scripts/wip_journal.py` is wired as a `SessionStart` / `PostToolUse` / `PreCompact` hook in `.claude/settings.json` and appends a "where was I" trail to the gitignored `.resume/session-journal.md`. `cat .resume/session-journal.md` shows the last files touched and when, per session.
- **Skill-level (structured decision log):** in-scope skills/agents checkpoint to `.resume/<name>/<run-id>.yml` per `spec/claude/resumable-work/`; re-invoking a resumable skill with the same inputs surfaces the resume prompt.

Operational rule: prefer running long feature work as a **top-level session inside the worktree** (`cd <worktree> && claude`) over a dispatched worktree-isolated subagent — only top-level sessions can be `claude --resume`'d; a subagent's transcript lives under its parent and cannot be resumed on its own.

For multi-source **research** that must survive a crash, prefer the Workflow harness over the built-in `deep-research` skill: a Workflow run persists every dispatched agent transcript and supports `resumeFromRunId`, whereas `deep-research` (a sealed harness built-in) holds fetched sources and verified claims only in conversation context and writes nothing to disk until its final report.

## Blog-author trigger (feature → done)

Per `spec/project/blog-author-trigger/` §Consumer contract, this repository declares its trigger roles:

- **Source consumer:** `nolte/claude-shared` (this repository). It hosts features under `project/features/<slug>.md` and drives transitions via `/nolte-shared:sprint-execute`. The `in_progress → done` transition is the trigger event.
- **Blog consumer:** `nolte/blog` (the bilingual Astro blog), clone path `~/repos/github/blog`. It receives derived briefings; the portfolio mapping (`nolte/claude-shared` → `portfolioProject: claude-shared`) is declared in the blog consumer's own `CLAUDE.md`.

`sprint-execute` Operation C step 6 automatically dispatches `/nolte-shared:blog-author-trigger` after marking a feature `done`; the operator then chooses new post / update / defer. Deferrals are written under `project/blog-triggers/<feature-slug>.yml`. Cross-repository writes into `~/repos/github/blog` require explicit operator confirmation — the trigger never writes there silently.
