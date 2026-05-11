# Example 01 — Clean close of a Claude-plugin sprint with operator skipping the release chain

Exercises the happy path through every step of the skill on a Claude-plugin
project: `active → review → closed` with a valid `artifact_ref` (a published
git tag that resolves through `.claude-plugin/marketplace.json`), the
`verifies_sprint_value` acceptance criterion checked, and the operator
explicitly **declining** the `release-skill-layer` chain. Confirms the
artefact-validation transcript and the operator's chain decision are both
recorded verbatim in `## Review notes` per `spec/project/sprint/`
§Acceptance Criteria.

## Input prompt

> Schließe Sprint `0011` ab — der `v0.11.0`-Tag ist gecuttet und im
> Marketplace gelistet. Die Release-Notes habe ich gestern manuell
> kuratiert, also keinen Chain in `release-notes-curate` oder
> `release-publish-trigger` — wir publizieren den Draft separat.

## Input files

`project/sprints/0011-skill-orchestration.md` (the sprint to close):

```markdown
---
id: 0011
slug: skill-orchestration
status: active
value_statement: Plugin-Authoren können einen Skill-Orchestrator-Flow
  innerhalb eines Sprints in Production bringen.
roadmap_items: [R-14, R-15]
features: [F-22, F-23, F-24]
verifies_sprint_value: F-22
started: 2026-04-26
ended: null
last_commit: 9a1c4e2b7f
artifact_ref: v0.11.0
---

# Sprint 0011 — Skill orchestration

## Features

- [F-22](../features/orchestrator-skill-shape.md) — done
- [F-23](../features/chain-dispatch-helper.md) — done
- [F-24](../features/orchestrator-failure-mode-tests.md) — done
```

`project/features/orchestrator-skill-shape.md` (the `verifies_sprint_value`
feature; relevant excerpt only):

```markdown
---
id: F-22
slug: orchestrator-skill-shape
status: done
sprint: 0011
roadmap_item: R-14
verifies_sprint_value: acceptance-3
---

## Acceptance criteria

- [x] **acceptance-1** — Skill-Frontmatter enthält `tags: [scaffolding]`.
- [x] **acceptance-2** — `## Hard rules`-Block ist vorhanden.
- [x] **acceptance-3** — Ein End-to-End-Lauf gegen `examples/01-*.md`
      promoviert einen Sprint von `active` nach `closed`.
- [x] **acceptance-4** — Frontmatter-Schema validiert per
      `tools/validate-frontmatter.py`.
```

`project/features/chain-dispatch-helper.md` and
`project/features/orchestrator-failure-mode-tests.md` are both
`status: done`, both carry `verifies_sprint_value: null`.

`.claude-plugin/plugin.json` exists (project type: Claude plugin).

`.claude-plugin/marketplace.json` (at HEAD) lists the plugin at version
`0.11.0`. The git tag `v0.11.0` exists locally and points at commit
`9a1c4e2b7f` (matches the sprint's `last_commit` exactly).

No `.github/release-skill-layer.yml` override file.

## Expected behaviour

1. **Preconditions.** Skill confirms it is in a git work tree,
   `project/sprints/0011-skill-orchestration.md` parses, sprint status is
   `active`, the `features` list is non-empty, every listed feature's
   frontmatter `status` is `done`, `last_commit` is non-null, and
   `artifact_ref` is non-null. All pass.
2. **Operation 1 — `active → review`.** Skill writes
   `status: review` on the sprint frontmatter (does **not** set `ended`
   yet) and surfaces the sprint summary verbatim: number `0011`, slug,
   `value_statement`, the three-feature list with each feature's
   `verifies_sprint_value` field, and the current `artifact_ref: v0.11.0`.
3. **Operation 2 — project-type detection.** Skill detects
   `.claude-plugin/plugin.json` and resolves the project type as **Claude
   plugin** per `spec/project/release-artifact/` §Project-type detection.
   No override file present.
4. **Operation 3 — artefact validation.** Skill parses `artifact_ref` as
   the single string `v0.11.0`. Per the Claude-plugin rule, the skill
   runs both verification commands:
   - `git rev-parse v0.11.0` → exit 0, prints `9a1c4e2b7f...`.
   - Marketplace-resolution probe: reads `.claude-plugin/marketplace.json`
     at HEAD, confirms the plugin version `0.11.0` is listed.
   Skill confirms the resolved tag commit equals the sprint's
   `last_commit` (`9a1c4e2b7f`) — exact match. Records the verification
   transcript (commands, exit codes, key output lines) for step 6.
5. **Operation 4 — `verifies_sprint_value` confirmation.** Skill walks
   the three feature files, finds exactly one (`F-22`) with a non-null
   `verifies_sprint_value` field (`acceptance-3`), reads
   `features/orchestrator-skill-shape.md`, locates the
   `- [x] **acceptance-3** …` bullet, confirms it is checked.
6. **Operation 5 — release-skill-layer chain (operator declines).**
   Skill asks the user explicitly whether to chain into
   `release-notes-curate` and `release-publish-trigger`. Operator's
   prompt already declined verbatim ("keinen Chain … wir publizieren den
   Draft separat"). Skill prepares the verbatim record for
   `## Review notes`:
   > Skipped: release-notes-curate; reason: Notes wurden gestern manuell
   > kuratiert.
   > Skipped: release-publish-trigger; reason: Operator publiziert den
   > Draft separat.
   Skill does **not** dispatch either downstream skill.
7. **Operation 6 — `review → closed`.** Skill writes
   `status: closed` and `ended: 2026-05-10` on the sprint frontmatter.
   Populates `## Review notes` with: the verification transcript from
   step 4 (both commands plus their outputs), the verifying-feature
   pointer (`features/orchestrator-skill-shape.md` plus
   `acceptance-3`), and the operator's chain decision recorded verbatim
   from step 6.
8. **Roadmap-item lifecycle.** Skill checks `R-14` and `R-15`. If every
   feature owned by each roadmap item is `done` and falls inside this
   sprint, skill flips the roadmap item to `status: done` per
   `spec/project/roadmap/` §Lifecycle. (Out of scope to model the
   roadmap file here; behaviour to confirm: skill **does** make this
   pass.)
9. **Closing summary.** Skill surfaces: path to the closed sprint,
   `ended: 2026-05-10`, `artifact_ref: v0.11.0`, the verifying feature
   (`F-22:acceptance-3`), and the chain decision (skipped, reason
   recorded).

Failure modes that **MUST** be surfaced instead of silently succeeding:

- If `git rev-parse v0.11.0` exits non-zero, route to step 7
  (cancellation) — do **not** proceed to step 5.
- If the marketplace probe finds no `0.11.0` entry, route to step 7.
- If the resolved tag commit doesn't match (or isn't reachable from)
  `last_commit`, refuse closure verbatim per
  `spec/project/release-artifact/` §Validation at sprint closure.
- If the operator's chain decision is not recorded verbatim in
  `## Review notes`, the close fails the
  `spec/project/sprint/` §Acceptance Criteria check.
- Skill **MUST NOT** call `gh release edit --draft=false` at any point
  in this flow.
