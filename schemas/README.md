# Shipped JSON Schemas

Every YAML-encoded JSON Schema document this repository ships, per
`spec/project/yaml-json-schema/` §Documentation and discovery. Schemas live
next to the data they govern: repo-wide schemas here, portfolio-data schemas
under `portfolio/schemas/`. All are meta-validated by
`scripts/validate_schemas.py` (wired into `task lint` and pre-commit).

| Schema file | Title | `$id` | Consuming spec |
| --- | --- | --- | --- |
| [`schemas/spec-config-v1.0.schema.yaml`](spec-config-v1.0.schema.yaml) | Spec Configuration | `https://github.com/nolte/claude-shared/blob/main/schemas/spec-config-v1.0.schema.yaml` | `spec/project/portfolio-inherited-spec-layer/` (governs `spec/.spec-config.yml`) |
| [`schemas/skill-agent-frontmatter-v1.0.schema.yaml`](skill-agent-frontmatter-v1.0.schema.yaml) | Skill and Agent Frontmatter | `https://github.com/nolte/claude-shared/blob/main/schemas/skill-agent-frontmatter-v1.0.schema.yaml` | `spec/claude/skill-agent-frontmatter/` (governs SKILL.md and `agents/*.md` frontmatter) |
| [`portfolio/schemas/tech-stack-v1.0.schema.yaml`](../portfolio/schemas/tech-stack-v1.0.schema.yaml) | Portfolio Tech Stack Manifest | `https://github.com/nolte/claude-shared/blob/main/portfolio/schemas/tech-stack-v1.0.schema.yaml` | `spec/portfolio/tech-stack/` (governs `portfolio/tech-stack.yml`) |
