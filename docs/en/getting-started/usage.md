---
title: Usage
audience: [maintainer, external-contributor]
content_mode: how-to
track: user-docs
last_updated: 2026-05-19
---

# Usage

Once the plugin is loaded, its skills appear as slash commands in the Claude Code prompt. This page covers the common invocation patterns and the namespace.

## Invoking skills

Skills are invocable by name—with or without the plugin prefix:

```
/nolte-shared:spec
/nolte-shared:skill-management
```

They also appear under `/skills` where Tab-completion works.

## Which skill for what

| Skill | Purpose | Typical triggers |
|-------|---------|-----------------|
| [`skill-management`](../skills/nolte-shared/skill-management.md) | Scaffold new skills; validate existing ones against the spec | "create a new skill," "scaffold a skill for X," "validate this skill" |
| [`spec`](../skills/nolte-shared/spec.md) | Write, translate, index and drift-check multilingual specs | "write a spec for X," "is X already covered?," "regenerate the index" |

## Response language

Skill files themselves are kept in English to keep Claude's processing cost low. Claude detects the user's language from their message. It then responds in that language—German in gets German out.

## Namespace collisions

A project may ship its own skill of the same name. Even then, the plugin version remains reachable. Use the namespaced form `/nolte-shared:<skill>` to resolve ambiguity.

## Next

- [Skill Management](../skills/nolte-shared/skill-management.md) in depth
- [Spec skill](../skills/nolte-shared/spec.md) in depth
- [Specifications](../references/specs/index.md): the authoring rules
