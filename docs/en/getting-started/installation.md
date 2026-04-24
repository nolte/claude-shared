# Installation

`claude-shared` is packaged as a single Claude Code plugin named **`nolte-shared`**. The plugin manifest lives at `.claude-plugin/plugin.json`, the marketplace descriptor at `.claude-plugin/marketplace.json`, skills under `skills/<name>/`, agents under `agents/<name>.md`.

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
/nolte-shared:skill-management
```

!!! tip "Symlink instead of copying"
    To use claude-shared alongside your own `.claude/` directory, symlink individual skills:
    ```bash
    ln -s /path/to/claude-shared/skills/<name> .claude/skills/<name>
    ```
    They show up in the `/skills` dialog and survive `claude --plugin-dir` switches.

## Work on the plugin itself (dogfooding)

When developing inside the `claude-shared` repo, launch Claude Code with the plugin pointing at the repo root so skills are discovered without duplicating files:

```bash
claude --plugin-dir .
```

Reload changes during a session with:

```
/reload-plugins
```

## Verify the plugin loaded

After startup, `/skills` should list entries from this repo (for example `nolte-shared:spec`, `nolte-shared:skill-management`). If something is missing, check:

1. `.claude-plugin/plugin.json` is valid JSON
2. Each folder contains `skills/<name>/SKILL.md` with valid frontmatter
3. Claude Code was started with the correct `--plugin-dir`
