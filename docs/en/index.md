---
title: Home
audience: [maintainer, downstream-user]
content_mode: meta
track: developer-docs
last_updated: 2026-05-19
---

# Home

`claude-shared` is a shared foundation of [Claude Code](https://docs.claude.com/en/docs/claude-code) **agents** and **skills**, intended to be reused across multiple projects. It's packaged as the **`nolte-shared`** plugin so teams get the same review habits, coding guidelines and helper workflows everywhere—without rebuilding them in every repository.

### Distribution path: from source repo to consumer projects

How does the `nolte-shared` plugin get from this repository into the projects that use it?

<!-- diagram-source: user-described — claude-shared source repo packaged as the nolte-shared plugin, delivering skills/agents/specs to downstream consumer projects -->
```mermaid
flowchart LR
    CS["claude-shared\nsource repo"] -->|"bundled as"| PL["nolte-shared\nplugin"]
    PL -->|"delivers"| S["Skills\nslash commands"]
    PL -->|"delivers"| A["Agents\nsubagent_type"]
    PL -->|"references"| SP["Specs\nconventions"]
    S --> P1["Project A"]
    A --> P1
    S --> P2["Project B"]
    A --> P2
```

| Aspect | Details |
|--------|---------|
| **Repository** | [`nolte/claude-shared`](https://github.com/nolte/claude-shared) |
| **Plugin name** | `nolte-shared` |
| **Slash namespace** | `/nolte-shared:<skill>` |
| **Skills source** | `skills/<name>/` |
| **Agents source** | `agents/<name>.md` |
| **Specifications** | `spec/claude/<topic>/<lang>.md` |
| **Status** | Actively developed; interfaces may change |

## What's included

- :jigsaw: **Skills**: reusable slash commands and workflows invoked via the `Skill` tool
- :robot: **Agents**: specialized sub-agents with focused tool access and system prompts
- :scroll: **Specifications**: structural rules for skills and agents, multilingual (DE/EN)
- :hammer_and_wrench: **Conventions**: shared `CLAUDE.md` snippets and prompt fragments

!!! info "What this repo is *not*"
    It isn't an end-user app, not a framework, and not a replacement for Claude Code. It's a **collection of shared configuration** that plugs into Claude Code.

## Next

If you want to **consume** the plugin in your own project, start at [Using nolte-shared](using.md). If you want to **develop** this repository, start at [Getting Started](getting-started/index.md).

- [Using nolte-shared](using.md): install and use the plugin downstream — _audience:_ `downstream-user`
- [Getting Started](getting-started/index.md): load the plugin and use the skills — _audience:_ `downstream-user`, `dogfooding-author`
- [Skills](skills/index.md): overview of bundled skills — _audience:_ `downstream-user`, `maintainer`
- [Agents](agents/index.md): overview of bundled agents — _audience:_ `downstream-user`, `maintainer`
- [Specifications](references/specs/index.md): authoring rules — _audience:_ `maintainer`, `external-contributor`
- [Development](guides/development.md): work on this repository — _audience:_ `external-contributor`, `maintainer`
