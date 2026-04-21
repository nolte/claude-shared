# Specifications

The specifications under `spec/` define the binding rules for skill and agent authors. They are **multilingual**: canonical in English, translated to German, kept structurally and semantically in sync via the [Spec skill](../skills/spec.md).

## Existing specs

| Topic | Slug | Title (DE) | Title (EN) | Status |
|-------|------|-----------|-----------|--------|
| claude | [agent-management](agent-management.md) | Claude-Agent-Autorenschaft | Claude Agent Authoring | draft |
| claude | [skill-management](skill-management.md) | Claude-Skill-Autorenschaft | Claude Skill Authoring | draft |

The live index is maintained in `spec/README.md` and updated by the Spec skill.

## RFC 2119 conventions

Normative statements use RFC 2119 keywords. Translations keep the English form as a gloss:

- **MUST** → `MUSS [MUST]`
- **MUST NOT** → `DARF NICHT [MUST NOT]`
- **SHOULD** → `SOLLTE [SHOULD]`
- **SHOULD NOT** → `SOLLTE NICHT [SHOULD NOT]`
- **MAY** → `KANN [MAY]`

## Contributing to specs

New spec or change? Always go through the [Spec skill](../skills/spec.md) — that's the only way canonical, translations and index stay in sync. Direct edits to translations are the single most common drift source and will be flagged at the next drift check.
