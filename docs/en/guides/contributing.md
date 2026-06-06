---
title: Contributing
audience: [external-contributor]
content_mode: how-to
track: developer-docs
last_updated: 2026-05-19
---

# Contributing

**Prerequisite:** plugin loaded locally (see [Installation](../getting-started/installation.md)). Skills `skill-management` and `spec` become available only after that.

## Workflow

1. **Read the spec first**: every skill or agent follows a [specification](../references/specs/index.md).
2. **Create the skill/agent**: use the [Skill Management](../skills/nolte-shared/skill-management.md) skill. It scaffolds lowercase-kebab-case folders, writes valid frontmatter, and prevents the usual mistakes.
3. **Adjust the spec if needed**: via the [Spec skill](../skills/nolte-shared/spec.md). Never edit translations directly. The English canonical (the authoritative EN source file) is the source of truth; everything else is regenerated from it.
4. **Validate**: `skill-management` in validation mode. Mechanical defects (frontmatter mismatch, absolute paths, missing hard-rules) can be autofixed on request.
5. **Update the index**: after spec changes, regenerate `spec/README.md` through the Spec skill.

## Conventions

- **Names**: ASCII kebab-case.
- **Descriptions**: concrete user triggers ("use when the user says X"), not abstract capabilities.
- **Agent tool access**: principle of least authority. Read-only = no write tools.
- **No absolute paths** inside skill or agent content.
- **Content language**: skills and agents in English, user response in the user's language.

## Commits

- Short, imperative subject lines ("add spec skill template").
- One logical change per commit. Spec changes (all languages + index update) stay **together** in a single commit so the English canonical never lands on a branch without its translations.

## Pull requests

- Link the affected spec.
- Describe which skills/agents are new or changed.
- Mention what you tested (for example "loaded plugin via `claude --plugin-dir .`, `/nolte-shared:spec` shows up in the `/skills` dialog").

## Common pitfalls

- **Edited a translation directly** → drift. Change the canonical and regenerate.
- **Created placeholder subfolders** → the skill-management skill forbids empty "just in case" folders.
- **`description` too vague** → Claude can't route reliably. At least three concrete phrasings.
- **`tools` too generous on an agent** → read-only agents get no write/execution tools, not even "for later."
