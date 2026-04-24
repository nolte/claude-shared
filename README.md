# claude-shared

[![ci](https://github.com/nolte/claude-shared/actions/workflows/ci.yml/badge.svg?branch=develop)](https://github.com/nolte/claude-shared/actions/workflows/ci.yml)

The `ci` workflow bundles the three required status checks that gate `develop`: `lint`, `test`, and `docs`. A green badge means all three passed on the latest `develop` commit.

A shared foundation of [Claude Code](https://docs.claude.com/en/docs/claude-code) agents and skills, intended to be reused across multiple software development projects.

## Purpose

Software teams usually want a consistent baseline when working with Claude Code: the same review habits, the same coding guidelines, the same helper agents. Rebuilding that baseline in every repository leads to drift and duplicated effort.

This repository provides a single source for:

- **Agents**: specialized sub-agents with focused tool access and instructions (for example code reviewers, explorers, planners).
- **Skills**: reusable slash commands and workflows invoked via the `Skill` tool.
- **Conventions**: shared guidance (`CLAUDE.md` snippets, prompt fragments) that projects can compose into their own setup.

## What this plugin ships

The plugin is distributed as a single bundle. After install, every skill below is callable as `/nolte-shared:<name>`. Agents are dispatched by skills, or directly via the `Task` tool when the caller knows which agent it wants.

### Skills

| Skill | Purpose |
| --- | --- |
| `spec` | Create, translate, index and drift-check multilingual specifications under `spec/`. |
| `skill-management` | Scaffold or revise a Claude Code skill under `skills/<name>/` per the authoring specs. |
| `skill-review` | Audit an existing skill against the authoring specs; persist findings as an actionable review plan. |
| `agent-review` | Audit a Claude Code agent against the authoring specs; persist findings as an actionable review plan. |
| `pull-request-create` | Create a GitHub PR that conforms to the repository's pull-request-workflow spec. |
| `pull-request-merge` | Promote an open draft PR to merged on `develop`, applying repository-declared labels and every workflow gate. |
| `quality-gate` | Run lint + typecheck + test in parallel and tabulate the results, so failures surface before a commit or PR. |
| `dependency-audit` | Scan the dependency tree for known CVEs (and optionally license issues) and produce a severity-sorted report. |
| `project-structure-apply` | Audit the repo against the project-structure spec and scaffold or patch missing artefacts (README, `.github/*`, Taskfile, Renovate, …). |
| `skill-agent-catalog-apply` | Wire up the MkDocs catalog that lists every skill and agent in a plugin repo. |
| `vocab-drift-audit` | Diff repository-local Vale vocabulary against the pinned `nolte/vale-style` release. |
| `audience-identify` | Identify the audiences of a bounded context and write a reviewable audience artifact. |

### Agents

| Agent | Purpose |
| --- | --- |
| `claude-plugin-developer` | Draft a new plugin skill or agent for `nolte-shared`, strictly conforming to every spec under `spec/claude/`. |
| `audience-doc-author` | Draft or refine an audience-tailored documentation artifact (README, release notes, …) against an existing audience artifact. |
| `audience-review` | Read-only review of an existing audience artifact against the audience-identification spec. |
| `spec-readiness-reviewer` | Audit specs for contradictions, audience fit, and Requirements-vs-Acceptance-Criteria completeness. |
| `docs-freshness-checker` | Audit MkDocs documentation for language parity, dead internal links, stale path references, ADR hygiene and placeholder markers. |
| `prose-vale-curator` | Rephrase prose until it passes Vale, preferring terms the shipped vocabularies already accept. |
| `png-to-transparent-svg` | Convert a PNG with baked-in checkerboard transparency into a clean SVG with real alpha. |

## Usage

This repository is packaged as a single [Claude Code plugin](https://docs.claude.com/en/docs/claude-code/plugins) named `nolte-shared`. The plugin manifest lives at `.claude-plugin/plugin.json`; skills under `skills/<name>/`; agents under `agents/<name>.md`.

### Consume in a downstream project

Add this repository as a plugin marketplace, then install the `nolte-shared` plugin:

```bash
/plugin marketplace add nolte/claude-shared
/plugin install nolte-shared@nolte-shared
```

For local testing without the marketplace flow, load the plugin directly from a checkout:

```bash
claude --plugin-dir /path/to/claude-shared
```

Plugin skills are namespaced by plugin name—for example `/nolte-shared:spec`, `/nolte-shared:skill-management`.

### Work on the plugin itself (dogfooding)

When developing inside this repository, launch Claude Code with the plugin pointed at the repo root so the skills are discovered without duplicating files:

```bash
claude --plugin-dir .
```

Use `/reload-plugins` to pick up changes during a session without restarting.

### Notes

- **Self-hosted marketplace source**: The plugin entry in `marketplace.json` uses `"source": "."` (relative path). This works when the marketplace is added via git (GitHub shorthand like `nolte/claude-shared`, or a `.git` URL). It doesn't work if a downstream user points directly at the raw `marketplace.json` over HTTP.
- **Contact**: No email is published in `plugin.json` or `marketplace.json`. Use the GitHub repository (`https://github.com/nolte/claude-shared`) for issues and contact.
- **Dogfooding requires `--plugin-dir .`**: There is no autoload for a plugin that lives in the same repository Claude Code is launched from. Without the flag, `/skills` in this repo won't list the bundled skills.

## Structure

```
.
├── .claude-plugin/
│   ├── plugin.json         # plugin manifest (name, version, author)
│   └── marketplace.json    # marketplace catalog (downstream install source)
├── skills/                 # reusable skills
│   └── <name>/SKILL.md
├── agents/                 # reusable sub-agents
│   └── <name>.md
├── spec/                   # bilingual specifications governing the content
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

- **No SLA.** Skills and agents are best-effort automation. Release quality, code quality and security posture of a downstream project remain the accountability of that project's maintainers.
- **No warranty on recommendations.** Outputs from `quality-gate`, `dependency-audit`, and review-style skills are advisory. A clean report isn't a guarantee that the reviewed change is safe to ship.
- **No support contract.** Issues and pull requests are triaged on a best-effort basis (see [`CONTRIBUTING.md`](CONTRIBUTING.md)). There is no published response-time commitment.
- **Vulnerability handling** follows [`SECURITY.md`](SECURITY.md); the plugin's threat scope is limited to what this repository itself ships, not to downstream use of its outputs.

## License

[MIT](LICENSE): Copyright (c) 2026 nolte.
