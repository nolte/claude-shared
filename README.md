# `claude-shared`

[![CI](https://github.com/nolte/claude-shared/actions/workflows/ci.yml/badge.svg?branch=develop)](https://github.com/nolte/claude-shared/actions/workflows/ci.yml)

A shared foundation of [Claude Code](https://docs.claude.com/en/docs/claude-code) agents and skills, intended to be reused across multiple software development projects.

The `ci` workflow bundles the four required status checks that gate `develop`: `lint`, `test`, `docs`, and `links`. A green badge means all four passed on the latest `develop` commit.

## Purpose

Software teams usually want a consistent baseline when working with Claude Code: the same review habits, the same coding guidelines, the same helper agents. Rebuilding that baseline in every repository leads to drift and duplicated effort.

This repository provides a single source for:

- **Agents**: specialized sub-agents with focused tool access and instructions (for example code reviewers, explorers, planners).
- **Skills**: reusable slash commands and workflows invoked via the `Skill` tool.
- **Conventions**: shared guidance (`CLAUDE.md` snippets, prompt fragments) that projects can compose into their own setup.

The plugin's primary readers are **`downstream-user`** (Claude Code users in portfolio projects who install this plugin), **`dogfooding-author`** (the plugin author developing it in this repo), plus **`maintainer`** and **`external-contributor`** for the codebase itself. The full audience list—with criticality, expectations, and per-audience track—lives in [`AUDIENCES.md`](AUDIENCES.md).

**When to use this plugin** (typical scenarios):

- Enforce a consistent pull-request workflow across multiple repositories in the same portfolio.
- Apply a uniform pre-merge review baseline (`review`, `security-review`) before shipping.
- Bootstrap or refresh a project's MkDocs documentation skeleton with audience-track frontmatter.
- Run a portfolio-wide `dependency-audit` / `docs-freshness` / `vocab-drift` pass on a recurring schedule.

Out-of-scope cases are listed under [§Scope & guarantees](#scope--guarantees). In short, the plugin ships tooling, not a managed service, and it doesn't own downstream release accountability.

## What these plugins ship

This repository is a **plugin monorepo** shipping four plugins: **`nolte-shared`** (the common delivery-lifecycle bundle, at the repo root), **`nolte-media`** (image generation and media processing, under `plugins/nolte-media/`), **`nolte-engineering`** (implementation, test, and code-audit capabilities for code repositories, under `plugins/nolte-engineering/`), and **`nolte-claude-dev`** (Claude Code skill and agent authoring, under `plugins/nolte-claude-dev/`). After install, every skill is callable as `/<plugin>:<name>`, for example `/nolte-shared:spec`, `/nolte-media:image-generate`, `/nolte-engineering:quality-gate`, or `/nolte-claude-dev:skill-management`. Agents are dispatched by skills, or directly via Claude Code's `Task` tool when the caller knows which agent it wants.

### Skills

| Skill | Purpose |
| --- | --- |
| `spec` | Create, translate, index and drift-check multilingual specifications under `spec/`. |
| `spec-drift-audit` | Reconcile every spec against the repository implementation and persist a traceable audit artifact. |
| `requirements-elicit` | Run the elicitation interview that captures a requirement precisely before anything is built. |
| `issue-orchestrate` | Take a raw GitHub issue end-to-end to an open, audit-trailed pull request. |
| `pull-request-create` | Create a GitHub PR that conforms to the repository's pull-request-workflow spec. |
| `pull-request-merge` | Promote an open draft PR to merged on `develop`, applying repository-declared labels and every workflow gate. |
| `project-structure-apply` | Audit the repo against the project-structure spec and scaffold or patch missing artefacts (README, `.github/*`, Taskfile, Renovate, …). |
| `lektorat-apply` | Review Markdown prose against the six editorial dimensions and apply the agreed revisions. |
| `vocab-drift-audit` | Diff repository-local Vale vocabulary against the pinned `nolte/vale-style` release. |
| `audience-identify` | Identify the audiences of a bounded context and write a reviewable audience artifact. |

### Agents

| Agent | Purpose |
| --- | --- |
| `audience-doc-author` | Draft or refine an audience-tailored documentation artifact (README, release notes, …) against an existing audience artifact. |
| `audience-review` | Read-only review of an existing audience artifact against the audience-identification spec. |
| `spec-readiness-reviewer` | Audit specs for contradictions, audience fit, and Requirements-vs-Acceptance-Criteria completeness. |
| `docs-freshness-checker` | Audit MkDocs documentation for language parity, dead internal links, stale path references, ADR (Architecture Decision Record) hygiene and placeholder markers. |
| `prose-vale-curator` | Rephrase prose until it passes Vale, preferring terms the shipped vocabularies already accept. |

### `nolte-media` (image generation & media processing)

A separate plugin because it needs external image-generation credentials and binaries that most `nolte-shared` consumers don't have. It's split out on a distribution-contract difference per `spec/claude/plugin-scoping/`.

| Capability | Type | Purpose |
| --- | --- | --- |
| `image-generate` | skill | Generate an image from a prompt via a swappable provider backend (Cloudflare FLUX / Pollinations / Gemini). |
| `gemini-image-handoff` | skill | Semi-automatic Gemini handoff: author a prompt, then guide the operator through the Gemini web UI (no API billing). |
| `graphic-prompt-generator` | agent | Turn a brief into a brand-conformant, generator-ready image prompt document. |
| `png-to-transparent-svg` | agent | Convert a PNG with baked-in checkerboard transparency into a clean SVG with real alpha. |

### `nolte-engineering` (implementation, test & code audits)

A separate plugin for code-bearing projects, split on a different consumer audience per `spec/claude/plugin-scoping/`: code repos adopt it on top of `nolte-shared`, while non-code repos (docs, content, config) take `nolte-shared` alone. Ships `fullstack-developer`; the full unit / component / integration / contract / E2E test-tier generator + reviewer suite plus the test-cycle agents (`test-result-analyzer`, `test-code-adapter`, `test-case-extractor`); the `quality-gate`, `test-cycle-orchestrate`, and `test-pyramid-check` skills; frontend optimization (`webview-ui-optimize`, `webview-ui-expert`, `frontend-usability-optimizer`, `i18n-completeness-checker`); and code-supply-chain audits (`code-security-reviewer`, `dependency-audit`, `license-check`).

### `nolte-claude-dev` (skill & agent authoring)

A separate plugin for the authoring slice, split on a different consumer audience per `spec/claude/plugin-scoping/`: most consumers install `nolte-shared` for the delivery lifecycle and never author a skill or agent, so they shouldn't carry this slice's skill-list weight. Adopters who do author them install it on top of `nolte-shared`. Ships the `skill-management`, `skill-review`, `agent-review`, `skills-agents-sweep`, and `skill-agent-catalog-apply` skills plus the `claude-plugin-developer` agent. The `spec/claude/` corpus that governs authoring stays repo-wide and doesn't move into this plugin.

## Usage

This repository packages four [Claude Code plugins](https://docs.claude.com/en/docs/claude-code/plugins), each with its own `.claude-plugin/plugin.json` and `skills/` + `agents/`: `nolte-shared` (repo root), `nolte-media` (`plugins/nolte-media/`), `nolte-engineering` (`plugins/nolte-engineering/`), and `nolte-claude-dev` (`plugins/nolte-claude-dev/`). All four are listed in `.claude-plugin/marketplace.json`.

### Consume in a downstream project

Add this repository as a plugin marketplace, then install whichever plugins you need:

```bash
/plugin marketplace add nolte/claude-shared
/plugin install nolte-shared@nolte-shared
/plugin install nolte-engineering@nolte-shared   # code repos: implementation + test + code audits
/plugin install nolte-media@nolte-shared         # optional; needs image-generation credentials/binaries
/plugin install nolte-claude-dev@nolte-shared     # optional; only if you author Claude Code skills or agents
```

For local testing without the marketplace flow, load the plugins directly from a checkout (pass `--plugin-dir` once per plugin):

```bash
claude --plugin-dir /path/to/claude-shared --plugin-dir /path/to/claude-shared/plugins/nolte-media --plugin-dir /path/to/claude-shared/plugins/nolte-engineering --plugin-dir /path/to/claude-shared/plugins/nolte-claude-dev
```

Plugin skills are namespaced by plugin name—for example `/nolte-shared:spec`, `/nolte-claude-dev:skill-management`, `/nolte-media:image-generate`.

### Work on the plugin itself (dogfooding)

When developing inside this repository, launch Claude Code with all in-repo plugins pointed at their roots so the skills are discovered without duplicating files:

```bash
claude --plugin-dir . --plugin-dir ./plugins/nolte-media --plugin-dir ./plugins/nolte-engineering --plugin-dir ./plugins/nolte-claude-dev
```

Use `/reload-plugins` to pick up changes during a session without restarting.

Install the [pre-commit](https://pre-commit.com) hooks once after cloning so that the prose-lint, frontmatter-validation, and formatting hooks fire on every `git commit`:

```bash
task setup    # alias for: pre-commit install
```

Without this step those checks don't run locally, so style and frontmatter issues surface only in CI instead of being caught before the commit. (The skill/agent catalog is no longer regenerated on commit: it's generated by the `gen_catalog.py` `on_pre_build` hook during `mkdocs build`, not committed. See `spec/claude/skill-agent-catalog/` §Generation mechanism.)

### Running the quality gate

Run the develop quality gate locally before a commit or a pull request with a single Taskfile target:

```bash
task check
```

`task check` runs the `lint` and `test` categories. The `docs` category stays a separate CI job, because it gates documentation freshness rather than the code itself. The target exits zero on a clean tree and non-zero when any category fails.

For a parseable result, invoke the `/nolte-engineering:quality-gate` skill. It renders a single table with the columns `Check`, `Status`, `Runner`, and `Details`, one row per category. Each `Status` is one of `pass`, `fail`, `skipped`, or `timeout`, and the `Runner` column records the exact command that ran (for example `task lint`) so the result stays reproducible.

The `ci` workflow gates the same three categories on `develop` as separate required status checks. This is where each category is covered locally:

| Category (`ci.yml` job) | Local coverage |
| --- | --- |
| `lint` | covered by pre-commit (run `task setup` once, then the hooks fire on every `git commit`) |
| `test` | contributor-invoked (`task test`, a placeholder until a runtime test suite lands) |
| `docs` | contributor-invoked (`task docs` builds the MkDocs site with `--strict`; the catalog regenerates via the `gen_catalog.py` `on_pre_build` hook during the build) |

### Notes

- **Self-hosted marketplace source**: `marketplace.json` lists four plugins: `nolte-shared` at `"source": "."`, `nolte-media` at `"source": "./plugins/nolte-media"`, `nolte-engineering` at `"source": "./plugins/nolte-engineering"`, and `nolte-claude-dev` at `"source": "./plugins/nolte-claude-dev"` (relative paths). This works when the marketplace is added via git (GitHub shorthand like `nolte/claude-shared`, or a `.git` URL). It doesn't work if a downstream user points directly at the raw `marketplace.json` over HTTP.
- **Contact**: No email is published in `plugin.json` or `marketplace.json`. Use the GitHub repository (`https://github.com/nolte/claude-shared`) for issues and contact.
- **Dogfooding requires `--plugin-dir` per plugin**: There is no autoload for a plugin that lives in the same repository Claude Code is launched from, and each in-repo plugin needs its own flag (`--plugin-dir . --plugin-dir ./plugins/nolte-media --plugin-dir ./plugins/nolte-engineering --plugin-dir ./plugins/nolte-claude-dev`). Without them, `/skills` in this repo won't list the bundled skills.
- **Workflow cascade constraint**: GitHub Actions doesn't cascade workflow runs from events produced by a `GITHUB_TOKEN`-authenticated step. In this repo that means `release-drafter.yml` doesn't fire after an `automerge.yaml` squash-merge, and `release-cd-refresh-master.yml` doesn't fire after a `release-publish.yml` publish. The constraint is documented in `spec/project/workflow-health/` §Known platform constraints; the portfolio-level fix lives in `nolte/gh-plumbing` (tracking: [`nolte/gh-plumbing#330`](https://github.com/nolte/gh-plumbing/issues/330), the portfolio App/PAT for the `GITHUB_TOKEN` cascade gap). Until that ships, a user-authored commit re-fires `release-drafter`, and `main` is fast-forwarded manually after a publish.
- **Changelog**: The authoritative per-release content lives on the [GitHub Releases page](https://github.com/nolte/claude-shared/releases); no Markdown changelog is kept in git.

## Structure

```
.
├── .claude-plugin/
│   ├── plugin.json         # nolte-shared manifest (name, version, author)
│   └── marketplace.json    # marketplace catalog listing all four plugins
├── skills/                 # nolte-shared skills
│   └── <name>/SKILL.md
├── agents/                 # nolte-shared sub-agents
│   └── <name>.md
├── plugins/
│   ├── nolte-media/        # second plugin: own .claude-plugin/, skills/, agents/
│   ├── nolte-engineering/  # third plugin: own .claude-plugin/, skills/, agents/
│   └── nolte-claude-dev/   # fourth plugin: own .claude-plugin/, skills/, agents/
├── spec/                   # bilingual specifications governing all four plugins
└── README.md
```

Conventions for authoring skills and agents are defined in `spec/claude/skill-management/` and `spec/claude/agent-management/`.

## Related repositories

This plugin is part of a small portfolio of shared foundations. The specs in `spec/project/` reference these repositories directly, and downstream projects are expected to pin them:

- [`nolte/gh-plumbing`](https://github.com/nolte/gh-plumbing): shared GitHub plumbing: reusable Actions workflows (release-drafter, automerge, `main` fast-forward on release, MkDocs publishing) and a commons `settings.yml` extended via the Probot Settings app. Anchors the branching-model and PR-workflow specs.
- [`nolte/vale-style`](https://github.com/nolte/vale-style): canonical Vale prose-style package: shared vocabularies (including language-scoped ones like `technical-de/`) and rules that repositories compose with Microsoft + RedHat styles. Anchors the prose-style spec.
- [`nolte/taskfiles`](https://github.com/nolte/taskfiles): shared [Task](https://taskfile.dev) include snippets (for example `taskfile-include-mkdocs.yaml`, `taskfile-include-pre-commit.yaml`) that downstream `Taskfile.yml`s pull in via `TASK_COLLECTION_BASE`, so MkDocs and pre-commit wiring stays uniform across repositories.

## Status

Early stage—the repository currently serves as the anchor point for consolidating agents and skills that were previously scattered across individual projects.

## Scope & guarantees

This plugin ships tooling—skills, agents, specs—not a managed service. It helps maintainers of downstream projects keep their workflows consistent, but it doesn't take responsibility for downstream outcomes:

- **No service-level agreement (SLA).** Skills and agents are best-effort automation. Release quality, code quality and security posture of a downstream project remain the accountability of that project's maintainers.
- **No warranty on recommendations.** Outputs from `quality-gate`, `dependency-audit`, and review-style skills are advisory. A clean report isn't a guarantee that the reviewed change is safe to ship.
- **No support contract.** Issues and pull requests are triaged on a best-effort basis (see [`CONTRIBUTING.md`](CONTRIBUTING.md)). There is no published response-time commitment.
- **Vulnerability handling** follows [`SECURITY.md`](SECURITY.md); the plugin's threat scope is limited to what this repository itself ships, not to downstream use of its outputs.

## License

[MIT](LICENSE): Copyright (c) 2026 nolte.
