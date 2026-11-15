# Shipped JSON Schemas

Every YAML-encoded JSON Schema document this repository ships, per
`spec/project/yaml-json-schema/` §Documentation and discovery. Schemas live
next to the data they govern: repo-wide schemas here, portfolio-data schemas
under `portfolio/schemas/`. All are meta-validated by
`scripts/validate_schemas.py` (wired into `task lint` and pre-commit).

| Schema file | Title | `$id` | Consuming spec |
| --- | --- | --- | --- |
| [`schemas/spec-config-v1.0.schema.yaml`](spec-config-v1.0.schema.yaml) | Spec Configuration | `https://github.com/nolte/claude-shared/blob/main/schemas/spec-config-v1.0.schema.yaml` | `spec/project/portfolio-inherited-spec-layer/` (governs `spec/.spec-config.yml`) |
| [`schemas/image-declaration-v1.0.schema.yaml`](image-declaration-v1.0.schema.yaml) | Image Declaration | `https://github.com/nolte/claude-shared/blob/main/schemas/image-declaration-v1.0.schema.yaml` | `spec/project/linux-image-best-practices/` (governs `image-declaration.yaml` next to each image definition in a consumer repository) |
| [`schemas/image-declaration-v1.1.schema.yaml`](image-declaration-v1.1.schema.yaml) | Image Declaration | `https://github.com/nolte/claude-shared/blob/main/schemas/image-declaration-v1.1.schema.yaml` | `spec/project/linux-image-best-practices/` (v1.1 adds `image.architectures` and `image.firmware`; a declaration names its version in `schema_version`) |
| [`schemas/image-declaration-v1.2.schema.yaml`](image-declaration-v1.2.schema.yaml) | Image Declaration | `https://github.com/nolte/claude-shared/blob/main/schemas/image-declaration-v1.2.schema.yaml` | `spec/project/linux-image-best-practices/` (v1.2 adds the `qemu-fw-cfg` switch type, the switch transport for U-Boot images under QEMU per `spec/project/image-boot-verification/` §H) |
| [`schemas/image-boot-protocol-v1.0.schema.yaml`](image-boot-protocol-v1.0.schema.yaml) | Image Boot Protocol | `https://github.com/nolte/claude-shared/blob/main/schemas/image-boot-protocol-v1.0.schema.yaml` | `spec/project/image-boot-verification/` §G (governs the `protocol.json` a boot verification run writes) |
| [`schemas/image-boot-protocol-v1.1.schema.yaml`](image-boot-protocol-v1.1.schema.yaml) | Image Boot Protocol | `https://github.com/nolte/claude-shared/blob/main/schemas/image-boot-protocol-v1.1.schema.yaml` | `spec/project/image-boot-verification/` §G (v1.1 lets a `fail` scenario carry no report line, the missing-report case of §F; a run writes v1.1, and a consumer still accepts a v1.0 protocol against the v1.0 schema) |
| [`schemas/skill-agent-frontmatter-v1.0.schema.yaml`](skill-agent-frontmatter-v1.0.schema.yaml) | Skill and Agent Frontmatter | `https://github.com/nolte/claude-shared/blob/main/schemas/skill-agent-frontmatter-v1.0.schema.yaml` | `spec/claude/skill-agent-frontmatter/` (governs SKILL.md and `agents/*.md` frontmatter) |
| [`portfolio/schemas/tech-stack-v1.0.schema.yaml`](../portfolio/schemas/tech-stack-v1.0.schema.yaml) | Portfolio Tech Stack Manifest | `https://github.com/nolte/claude-shared/blob/main/portfolio/schemas/tech-stack-v1.0.schema.yaml` | `spec/portfolio/tech-stack/` (governs `portfolio/tech-stack.yml`) |
