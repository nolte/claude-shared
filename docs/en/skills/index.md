# Skills

Skills are reusable workflows Claude Code invokes via the `Skill` tool. In the claude-shared source tree they live at `skills/<name>/SKILL.md`; at runtime in a consuming project under `.claude/skills/<name>/` or `~/.claude/skills/<name>/` — or, as here, bundled inside the `nolte-shared` plugin.

## Bundled skills

| Skill | Description |
|-------|-------------|
| [Skill Management](skill-management.md) | Scaffold new skills; validate existing ones against the spec |
| [Spec](spec.md) | Manage multilingual specs (DE/EN), detect drift, maintain the index |

## Skill anatomy

```
skills/<name>/
├── SKILL.md              # YAML frontmatter + instructions
├── templates/            # optional
├── references/           # optional
└── examples/             # optional
```

The frontmatter of every skill contains at minimum:

```yaml
---
name: <folder-name>
description: Concrete trigger phrases, not abstract capabilities.
---
```

Full rules and acceptance criteria: [Skill Authoring](../specs/skill-management.md).
