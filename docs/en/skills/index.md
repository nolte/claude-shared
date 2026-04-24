# Skills

Skills are reusable workflows Claude Code invokes via the `Skill` tool. In the claude-shared source tree they live at `skills/<name>/SKILL.md`; at runtime in a consuming project under `.claude/skills/<name>/` or `~/.claude/skills/<name>/`: or, as here, bundled inside the `nolte-shared` plugin.

## Bundled skills

| Skill | Description |
|-------|-------------|
| [`spec`](spec.md) | Manage multilingual specs (DE/EN), detect drift, maintain the index |
| [`skill-management`](skill-management.md) | Scaffold or revise a skill under `skills/<name>/` |
| `skill-review` | Audit an existing skill against the authoring spec; persist findings as a review plan |
| `agent-review` | Audit an existing agent against the authoring spec; persist findings as a review plan |
| `pull-request-create` | Open a PR that conforms to the `pull-request-workflow` spec |
| `pull-request-merge` | Promote an open draft PR to merged on `develop`, applying labels and workflow gates |
| `quality-gate` | Run lint + typecheck + tests in parallel and tabulate the results |
| `dependency-audit` | Scan dependencies for known CVEs (optionally licenses) |
| `project-structure-apply` | Audit the repo against the `project-structure` spec and scaffold missing artefacts |
| `skill-agent-catalog-apply` | Wire up the MkDocs catalog that lists every skill and agent in a plugin repo |
| `vocab-drift-audit` | Diff repository-local Vale vocabulary against the pinned `nolte/vale-style` release |
| `audience-identify` | Identify the audiences of a bounded context and write a reviewable audience artifact |

Detail pages currently exist for `skill-management` and `spec`; more are being added. The authoritative source per skill is `skills/<name>/SKILL.md` in the source tree.

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
