---
title: Skills
audience: [maintainer]
content_mode: meta
track: developer-docs
last_updated: 2026-05-19
---

# Skills

Skills are reusable workflows Claude Code invokes via the `Skill` tool. In the `claude-shared` source tree they live at `skills/<name>/SKILL.md`; at runtime in a consuming project under `.claude/skills/<name>/` or `~/.claude/skills/<name>/`: or, as here, bundled inside the `nolte-shared` plugin.

## Bundled skills

| Skill | Description |
|-------|-------------|
| [`spec`](spec.md) | Manage multilingual specs (DE/EN), detect drift, maintain the index |
| [`skill-management`](skill-management.md) | Scaffold or revise a skill under `skills/<name>/` |
| `skill-review` | Audit an existing skill against the authoring spec; persist findings as a review plan |
| `agent-review` | Audit an existing agent against the authoring spec; persist findings as a review plan |
| `pull-request-create` | Open a PR that conforms to the `pull-request-workflow` spec |
| `pull-request-merge` | Promote an open draft PR to merged on `develop`, applying labels and workflow gates |
| `release-notes-curate` | Augment the open release-drafter draft with a project-context section (per `release-skill-layer`) |
| `release-publish-trigger` | Validate pre-publish gates and dispatch `release-publish.yml` for the open draft on `develop` |
| `quality-gate` | Run lint + typecheck + tests in parallel and tabulate the results |
| `dependency-audit` | Scan dependencies for known CVEs (optionally licenses) |
| `project-structure-apply` | Audit the repo against the `project-structure` spec and scaffold missing artefacts |
| `github-issue-templates-apply` | Scaffold or update `.github/ISSUE_TEMPLATE/` per the `github-issue-templates` spec |
| `skill-agent-catalog-apply` | Wire up the MkDocs catalog that lists every skill and agent in a plugin repo |
| `mermaid-diagrams-apply` | Audit the MkDocs Mermaid setup against the `mermaid-diagrams` spec and emit spec-compliant diagrams |
| `vocab-drift-audit` | Diff repository-local Vale vocabulary against the pinned `nolte/vale-style` release |
| `workflow-health-triage` | Triage a failing GitHub Actions workflow per `workflow-health` spec; classify, dispatch a specialised agent, route the fix through the standard PR flow |
| `permission-allowlist-maintain` | Curate the committed `.claude/settings.json` `permissions.allow` list per `permission-allowlist` spec; user-gated per-entry approval |
| `audience-identify` | Identify the audiences of a bounded context and write a reviewable audience artifact |
| `mission-define` | First-write `project/mission.md` walking SMART one letter at a time |
| `mission-revise` | Edit `project/mission.md` and flip `mvp_status` lifecycle per the `mission` spec |
| `roadmap-init` | Scaffold initial `project/goals.md` and `project/roadmap.md` (Vision plus Outcomes plus empty queue) |
| `roadmap-refine` | Enforce the detail-level invariant in `project/roadmap.md` with structured violation reports |
| `roadmap-plan` | Add, promote, re-target roadmap items; flip the `mvp` flag |
| `feature-decompose` | Decompose a roadmap item into `project/features/<slug>.md` with `feature-consistency-reviewer` dispatch |
| `sprint-plan` | Create `project/sprints/<NNNN>-<slug>.md` with `value_statement` and `verifies_sprint_value` |
| `sprint-execute` | Drive the sprint lifecycle: `planned → active`, feature transitions, `last_commit` updates |
| `sprint-review` | Close a sprint with artefact validation, optionally chain into the release skill layer |

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

Full rules and acceptance criteria: [Skill Authoring](../references/specs/skill-management.md).
