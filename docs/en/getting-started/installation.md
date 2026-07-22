---
title: Installation
audience: [maintainer, external-contributor]
content_mode: how-to
track: developer-docs
last_updated: 2026-05-19
---

# Installation

`claude-shared` ships as a single Claude Code plugin named **`nolte-shared`**. Layout:

- Plugin manifest: `.claude-plugin/plugin.json`
- Marketplace descriptor: `.claude-plugin/marketplace.json`
- Skills: `skills/<name>/`
- Agents: `agents/<name>.md`

## Prerequisites

- [Claude Code](https://docs.claude.com/en/docs/claude-code) installed
- A local checkout of this repository (or a location Claude Code can access)

## Load in a downstream project

Add this repository as a marketplace and install the plugin:

```bash
/plugin marketplace add nolte/claude-shared
/plugin install nolte-shared@nolte-shared
```

For local testing without the marketplace flow, load the plugin directly from a local path:

```bash
claude --plugin-dir /path/to/claude-shared
```

Skills from the plugin are invocable under their namespace:

```
/nolte-shared:spec
/nolte-claude-dev:skill-management
```

!!! tip "Symlink instead of copying"
    Optionally symlink individual skills. That keeps `claude-shared` alongside your own `.claude/` directory:
    ```bash
    ln -s /path/to/claude-shared/skills/<name> .claude/skills/<name>
    ```
    They show up in the `/skills` dialog and survive `claude --plugin-dir` switches.

## Work on the plugin itself (dogfooding)

When you develop inside the `claude-shared` repo, point Claude Code at the repo root. Claude Code then discovers the skills in place—no file duplication needed:

```bash
claude --plugin-dir .
```

Reload changes during a session with:

```
/reload-plugins
```

## Verify the plugin loaded

After startup, `/skills` lists the entries from this repo—for example `nolte-shared:spec` and `nolte-claude-dev:skill-management`. If something is missing, check:

1. `.claude-plugin/plugin.json` is valid JSON
2. Each folder contains `skills/<name>/SKILL.md` with valid frontmatter
3. Claude Code was started with the correct `--plugin-dir`
