# Development

This section is for contributors working on the `claude-shared` repository itself — adding new skills, new agents, or maintaining the specifications.

- [Project Structure](projektstruktur.md) — where things live and why
- [Contributing](beitragen.md) — workflow, conventions, commits

## Dogfooding

When working on the repo, launch Claude Code with the plugin pointing at the repo root:

```bash
claude --plugin-dir .
```

`/reload-plugins` picks up changes during a session.

## Read the spec first

Before writing a new skill or agent, read the relevant specification:

- [Skill Authoring](../specs/skill-management.md)
- [Agent Authoring](../specs/agent-management.md)

Create new skills through the [Skill Management](../skills/skill-management.md) skill itself — that guarantees conformance.
