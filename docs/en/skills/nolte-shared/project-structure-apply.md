---
title: project-structure-apply
audience: [maintainer]
content_mode: reference
track: developer-docs
last_updated: generated
---

# project-structure-apply

> Audits a repository against the project-structure spec and scaffolds missing artefacts (README, .github/, Renovate, Taskfile, MkDocs, .claude/).

_Audits a repository against the canonical-language file under spec/project/project-structure/ and scaffolds or patches missing artefacts: README, top-level orientation file, .gitignore, .pre-commit-config.yaml, Renovate config, Taskfile, MkDocs setup, .claude/ directory, and the full .github/ layout (workflows, settings.yml, release-drafter.yml, boring-cyborg.yml, stale.yml) with the portfolio-wide Probot extends pointers. Verifies via the GitHub API that the backing GitHub Apps (Probot apps `settings`, `boring-cyborg`, `stale`, plus Renovate) are installed; for Renovate also points at the Mend dashboard when the App is installed but no activity is visible. Invoke when the user asks to audit project structure, scaffold missing GitHub configs, generate release-drafter config, check Probot/Renovate app installation, or equivalent German-language requests. Supports resume on re-invocation per `spec/claude/resumable-work/`._

- **Plugin:** `nolte-shared`
- **Phase:** 3 Design (`design`)
- **Tags:** `scaffolding`
- **Source:** [skills/project-structure-apply/SKILL.md](https://github.com/nolte/claude-shared/blob/main/skills/project-structure-apply/SKILL.md)

## Use when

- you want to audit the project structure of a repo
- you want to scaffold missing GitHub configs (settings, release-drafter, boring-cyborg, stale)
- you want to check that the backing GitHub Apps (Probot, Renovate) are installed

## Don't use when

- **You want to wire the skill-and-agent catalog on top of MkDocs** → [`skill-agent-catalog-apply`](skill-agent-catalog-apply.md)
- **You want to scaffold issue-template forms specifically** → [`github-issue-templates-apply`](github-issue-templates-apply.md)

## See also

- [`mkdocs-structure-apply`](mkdocs-structure-apply.md)
- [`github-issue-templates-apply`](github-issue-templates-apply.md)
- [`skill-agent-catalog-apply`](skill-agent-catalog-apply.md)

## Referenced by

- [`project-structure-reviewer`](../../agents/nolte-shared/project-structure-reviewer.md)
- [`github-issue-templates-apply`](github-issue-templates-apply.md)
- [`skill-agent-catalog-apply`](skill-agent-catalog-apply.md)

---

## Project Structure Apply

Audits and repairs a repository so it matches the Repository Project Structure spec at `spec/project/project-structure/<canonical_language>.md`. The skill both reports findings and—with explicit per-item user consent—writes the missing files in place.

### Why this is a skill, not an agent

- **Per-item user approval is the contract.** Every scaffolded file (`.github/settings.yml`, `Taskfile.yml`, `renovate.json5`, …) is written only with explicit per-change confirmation; the audit is read-only and the apply step is a sequence of approvals an agent's fire-and-forget shape can't carry.
- **Output flows back into the main conversation.** The audit table, the per-item proposals, and the GitHub-App-installation status all surface in the conversation so the user can decide; isolating them in a structured-report boundary would obscure the per-file approval surface.
- **Network-side calls require user gating.** Probot-app installation checks read GitHub API state, but app installation itself is intentionally a human-approved action; mid-flow interactivity is load-bearing here.
- Counter-dimension considered: a narrower agent could specialize on file-template generation and gain on context-window protection, but the high-impact part is the per-item approval dialogue, not the boilerplate; skill wins.

When the spec isn't present in the target repository, fall back to the copy shipped by the `nolte-shared` plugin (read it at runtime from the plugin install path, or from the `nolte/claude-shared` repository). Never invent requirements that aren't in the spec.

### User-language policy

Detect the user's language and respond in it. Generated file contents (`.github/*.yml`, `Taskfile.yml`, `CLAUDE.md`, `renovate.json5`, workflow YAML, and equivalents) are always written in English so automation and cross-project consistency stay predictable. Comments inside generated files are English as well.

### Preconditions

Before doing anything:

- Confirm the working directory is a git repository (`git rev-parse --is-inside-work-tree`).
- Locate a `spec/project/project-structure/` folder—either in the target repo or via the nolte-shared plugin. If neither is reachable, stop and ask the user which spec source to use.
- Check for uncommitted changes in paths the skill may touch (`.github/`, `docs/`, `spec/`, `tests/`, root configs). If the tree is dirty in those paths, report and ask whether to stash, commit, or abort—never overwrite uncommitted work.

### Operations

Read `references/operations.md` when executing any of the operations below in detail.

#### 1. Audit

Walk through the spec's Acceptance Criteria one item at a time; classify each finding as `pass`, `missing`, or `drift`. Report grouped by spec area (Top-level files, Claude integration, CI and automation, GitHub repository configuration, Documentation, Specifications, Project planning artefacts, Tests, Source layout, Python development, Home Assistant, Containerization). Audit is read-only—never autofix.

#### 2. GitHub App installation check

Verify that the Probot apps (`settings`, `boring-cyborg`, `stale`) and Renovate are installed on the repository via `gh api` against the installations accessible to the owner. Only check apps whose backing config the audit classified as **pass**. Handle 403/404 token-scope errors gracefully; never attempt to install an app programmatically.

#### 3. Apply

For each **missing** or **drift** item, confirm per item before writing. Scaffold missing top-level files, Renovate config, `.claude/` directory, `.github/` Probot configs, required release-management workflows, Taskfile targets, docs stub, `spec/` / `tests/` placeholders, and Python dev layout. Route planning-artefact and source-layout decisions back to the user. Re-run the affected audit check after each write.

#### 4. Re-audit

Re-run Operations 1 and 2 end-to-end after the user finishes approving changes; present a fresh grouped summary calling out any remaining **missing**, **drift**, or uninstalled-app items.

### Examples

- Read `examples/01-fresh-python-app-scaffolding.md` when scaffolding project structure for a new Python application from scratch.
- Read `examples/02-claude-plugin-github-config.md` when auditing or generating GitHub config files for a Claude plugin repository.
- Read `examples/03-renovate-app-not-installed.md` when the Renovate App installation check fails and you need to see the expected report shape.

### Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/project-structure-apply/<run-id>.yml` after every successful user-approval gate and after each named phase boundary. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope (`schema_version`, `run_id`, `inputs`, `phase`, `decisions[]`, `status`, ...) and the fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

### Hard rules

- **Never** overwrite an existing file without explicit per-item confirmation. Merge into existing YAML or JSON configs rather than replacing them wholesale.
- **Never** manage repository settings through the GitHub UI or `gh repo edit`. `.github/settings.yml` is the source of truth, driven by the Probot Settings app.
- **Never** write a `.github/settings.yml` without an `_extends:` pointing at `nolte/gh-plumbing:.github/commons-settings.yml` (or the short form `gh-plumbing:.github/commons-settings.yml` inside the `nolte` org). Same applies to release-drafter, boring-cyborg, and stale.
- **Never** copy plugin-owned skills into `.claude/skills/`. Distribution is the plugin mechanism's job.
- **Never** automatically move source files out of the repository root. Report the drift and let the user decide.
- **Never** scaffold or rewrite content inside the `project/` planning tree (`project/roadmap.md`, `project/goals.md`, `project/sprints/`, `project/features/`, `project/release-artifacts/`, `project/mission.md`). The audit verifies the layout only; per-file authoring is delegated to the planning skills ([`roadmap-init`](roadmap-init.md), [`sprint-plan`](sprint-plan.md), [`feature-decompose`](feature-decompose.md), [`mission-define`](mission-define.md)) per the matching specs.
- **Never** commit a real `.env`. When creating `.env.example`, simultaneously ensure `.env` is listed in `.gitignore`.
- **Always** ensure `.gitignore` carries a `/.resume/` entry per `spec/claude/resumable-work/` §Persistence location, so the in-flight resume state of resumable skills and agents stays out of version control.
- **Never** attempt to install a GitHub App programmatically. Report the install status and link to the app's marketplace page so a human can approve the install.
- When `spec/project/project-structure/` disagrees with this skill's instructions, the spec wins. Propose updating this skill rather than silently diverging.
- When the Probot app installation check can't run because the token lacks scope, report that explicitly: **never** treat an API error as "app is installed."

### Gotchas

Per `spec/claude/skill-management/` §Gotchas: concrete corrections to non-obvious environment facts the executing agent would otherwise get wrong.

- **Probot Settings App sync isn't atomic with `.github/settings.yml` edits.** A repository can carry `delete_branch_on_merge: true` in the file and the platform still leaves merged feature branches behind, because the Settings App pulls on its own webhook cadence. After a `settings.yml` edit, expect a manual catch-up on the first one or two merges and surface that to the user instead of treating the file's intent as the platform's actual state.
- **Token scope for the installation check is `read:user` (user-owned repos) or `admin:org` (org-owned).** A `gh api /user/installations` call returning HTTP 403 means the token lacks the scope, **not** that the apps aren't installed. Route the user at `https://github.com/<owner>/settings/installations` (user) or `https://github.com/organizations/<owner>/settings/installations` (org) for manual verification rather than reporting that apps are missing.
- **Renovate App installed differs from Renovate App active.** A repository can have the Renovate App granted access and still produce zero PRs and zero Dependency-Dashboard issues; the App's own runs are queued separately on Mend's side. When the install check passes but no Renovate activity is visible, point the user at `https://developer.mend.io/github/<owner>/<repo>` rather than re-checking the App permissions.
- **Renovate config file naming is `renovate.json5` by default in this portfolio**, but Renovate also reads `renovate.json` and `.renovaterc` and a few other variants. When auditing, check for the active variant first; when scaffolding for a new repo, default to `renovate.json5` per `spec/project/project-structure/`.
