# Changelog

The authoritative release history lives on the [GitHub Releases page](https://github.com/nolte/claude-shared/releases); this changelog summarizes the headlines per version.

## 0.2.0 (in preparation — first published release)

### Highlights

- First publicly published release of the `nolte-shared` plugin
- 12 skills and 7 agents bundled (see [Skills](../skills/index.md), [Agents](../agents/index.md))
- Review infrastructure: `skill-review`, `agent-review`, `spec-readiness-reviewer`, `docs-freshness-checker`
- Release infrastructure: `release-automation` spec (draft → published without manual CLI), interim local `release-publish.yml` workflow
- Audience infrastructure: `audience-identification` spec, `audience-identify` skill, `audience-doc-author` and `audience-review` agents
- PR lifecycle: `pull-request-create` and `pull-request-merge` skills aligned with `pull-request-workflow`
- Quality gates: `quality-gate`, `dependency-audit`, `vocab-drift-audit`

### Skills (new vs. 0.1.0)

`skill-review`, `agent-review`, `pull-request-create`, `pull-request-merge`, `quality-gate`, `dependency-audit`, `project-structure-apply`, `skill-agent-catalog-apply`, `vocab-drift-audit`, `audience-identify`

### Agents (new vs. 0.1.0)

`claude-plugin-developer`, `audience-doc-author`, `audience-review`, `spec-readiness-reviewer`, `docs-freshness-checker`, `prose-vale-curator`, `png-to-transparent-svg`

### Specs (new vs. 0.1.0)

`skill-vs-agent`, `skill-review`, `agent-review`, `review-plan`, `skill-agent-catalog`, `permission-allowlist`, `pull-request-workflow`, `branching-model`, `release-automation`, `release-notes-audience-analysis`, `project-structure`, `quality-gate`, `dependency-audit`, `workflow-health`, `docs-freshness`, `readme-structure`, `prose-style`, `spec-drift-audit`, `spec-readiness`, `audience-identification`, `continuous-improvement`

## 0.1.0 (unreleased — bootstrap)

### Plugin

- `.claude-plugin/plugin.json`: `nolte-shared` v0.1.0 plugin manifest

### Skills

- `skill-management`: scaffold and validate skills
- `spec`: manage multilingual specs (DE/EN), drift check, index regeneration

### Specifications

- `spec/claude/skill-management/`: Claude Skill Authoring (draft)
- `spec/claude/agent-management/`: Claude Agent Authoring (draft)

### Documentation

- MkDocs setup with `mkdocs-material` and `mkdocs-static-i18n`
- German and English
- Sections: Home, Getting Started, Skills, Agents, Specifications, Development, Changelog
