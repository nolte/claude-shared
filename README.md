# claude-shared

A shared foundation of [Claude Code](https://docs.claude.com/en/docs/claude-code) agents and skills, intended to be reused across multiple software development projects.

## Purpose

Software teams usually want a consistent baseline when working with Claude Code: the same review habits, the same coding guidelines, the same helper agents. Rebuilding that baseline in every repository leads to drift and duplicated effort.

This repository provides a single source for:

- **Agents** — specialized sub-agents with focused tool access and instructions (e.g. code reviewers, explorers, planners).
- **Skills** — reusable slash commands and workflows invoked via the `Skill` tool.
- **Conventions** — shared guidance (CLAUDE.md snippets, prompt fragments) that projects can compose into their own setup.

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

Plugin skills are namespaced by plugin name — e.g. `/nolte-shared:spec`, `/nolte-shared:skill-management`.

### Work on the plugin itself (dogfooding)

When developing inside this repository, launch Claude Code with the plugin pointed at the repo root so the skills are discovered without duplicating files:

```bash
claude --plugin-dir .
```

Use `/reload-plugins` to pick up changes during a session without restarting.

### Notes

- **Self-hosted marketplace source**: The plugin entry in `marketplace.json` uses `"source": "."` (relative path). This works when the marketplace is added via git (GitHub shorthand like `nolte/claude-shared`, or a `.git` URL). It does not work if a downstream user points directly at the raw `marketplace.json` over HTTP.
- **Contact**: No email is published in `plugin.json` or `marketplace.json`. Use the GitHub repository (`https://github.com/nolte/claude-shared`) for issues and contact.
- **Dogfooding requires `--plugin-dir .`**: There is no auto-load for a plugin that lives in the same repository Claude Code is launched from. Without the flag, `/skills` in this repo will not list the bundled skills.

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

## Status

Early stage — the repository currently serves as the anchor point for consolidating agents and skills that were previously scattered across individual projects.

## License

To be decided.
