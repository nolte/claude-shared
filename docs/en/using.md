---
title: Using nolte-shared
audience: [downstream-user]
content_mode: explanation
track: user-docs
last_updated: 2026-05-30
---

# Using nolte-shared

This page is for **downstream Claude Code users** who want to consume the
`nolte-shared` plugin in their own projects. If you instead want to *develop*
the plugin itself, start at the [developer documentation](getting-started/index.md).

## Why adopt nolte-shared

Software teams usually want a consistent Claude Code baseline across every
repository: the same review habits, the same coding guidelines, the same helper
agents. Rebuilding that baseline per repository causes drift and duplicated
effort. `nolte-shared` packages the baseline once, with reusable **skills**
(slash commands and workflows) and **agents** (focused sub-agents), plus shared
**conventions**, so every project that installs the plugin gets the same
spec-compliant workflows without rebuilding them.

## Who this is for

- **Downstream Claude Code users** (`downstream-user`): developers who invoke
  the plugin's slash commands (for example `/nolte-shared:spec`,
  `/nolte-claude-dev:skill-management`, `/nolte-shared:pull-request-create`) and its
  sub-agents inside their own portfolio projects. You get stable command names,
  reproducible outputs, and consistent review and release discipline.
- **End users of downstream projects** (`downstream-end-user`): you never call
  the plugin directly; you only see the downstream product. The plugin shapes
  that product's code quality and release discipline indirectly, but takes no
  responsibility for end-user outcomes.

The audience identifiers reference the project's audience artefact,
[`AUDIENCES.md`](https://github.com/nolte/claude-shared/blob/develop/AUDIENCES.md).

## What you can do with it

The plugin is designed for these scenarios:

- Apply a uniform **pull-request workflow** (`/nolte-shared:pull-request-create`,
  `/nolte-shared:pull-request-merge`) across repositories.
- Run a consistent **quality gate** and **dependency audit** before committing
  or releasing (`/nolte-engineering:quality-gate`, `/nolte-engineering:dependency-audit`).
- Run a **planning cadence** in `project/`—mission, roadmap, features, sprints
  (`/nolte-planning:sprint-plan`, `/nolte-planning:roadmap-plan`)—when your
  repository plans that way; repositories that track work as issues skip this
  plugin entirely.
- Author and review **skills, agents, and specs** against shared authoring rules
  (`/nolte-claude-dev:skill-management`, `/nolte-shared:spec`, and the review skills).
- Keep **project structure, documentation, and release automation** aligned with
  the portfolio baseline.

Explicitly **out of scope**: `nolte-shared` is tooling, not a managed service. It
ships no service-level agreement (SLA), gives no warranty on its advisory outputs (a clean report isn't a
guarantee that a change is safe to ship), and offers no support contract.
Release, code, and security accountability stay with your project.

## Install it in your project

Add this repository as a plugin marketplace, then install the `nolte-shared`
plugin from within Claude Code:

```bash
/plugin marketplace add nolte/claude-shared
/plugin install nolte-shared@nolte-shared
```

The companion plugins are optional and installed the same way, on top of
`nolte-shared`, only if your project needs them:

```bash
/plugin install nolte-engineering@nolte-shared  # code repositories
/plugin install nolte-planning@nolte-shared     # repositories that plan in project/
/plugin install nolte-media@nolte-shared        # needs image-generation credentials
/plugin install nolte-claude-dev@nolte-shared   # only if you author skills or agents
```

After install, every skill is callable as `/<plugin>:<name>` (for example
`/nolte-shared:spec`, `/nolte-planning:sprint-plan`); agents are dispatched by
skills, or directly via the `Task` tool when you know which agent you want. You don't need a clone of this
repository or its local toolchain to consume the plugin: installation happens
entirely inside your own Claude Code environment.
