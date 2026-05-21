# Example: Full-Scope Baseline Sweep

This walkthrough covers a complete portfolio-wide sweep of the `nolte-shared` plugin from
scope confirmation through consolidated report authoring.

---

## Turn 1 — user invokes the sweep

> "Run a portfolio-wide skills and agents sweep audit."

**Skill response:**

The skill checks preconditions:

- `spec/.spec-config.yml` present — canonical language: `en`
- `spec/claude/skills-agents-sweep/en.md` present
- `spec/claude/skill-review/en.md` and `spec/claude/agent-review/en.md` present
- `.audits/skills-agents-sweep/` exists (`.gitkeep` tracked)
- No existing open sweep report found

Inventory: 34 skills under `skills/`, 9 agents under `agents/`.

> Scope confirmed: full inventory (34 skills, 9 agents).
> Repository revision recorded: `b1b4d0b48e406f63ccc235b052cf80aef3cf02ae`
>
> Proceeding to Phase 1: per-artefact reviews.

---

## Turn 2 — phase 1: per-artefact reviews

The skill dispatches `skill-review run <name>` for each of the 34 skills in lifecycle-phase
order (plan → develop → review → release → operate). For each agent it dispatches
`agent-review run <name>`.

After all 43 plan files are written to `.audits/skill-review/` and `.audits/agent-review/`:

> Phase 1 complete. 43 plan files written:
> - 34 under `.audits/skill-review/`
> - 9 under `.audits/agent-review/`
>
> Proceeding to Phase 2: cross-cutting analysis.

---

## Turn 3 — phase 2: cross-cutting analysis

The skill reads all 43 plan files and analyses the six cross-cutting dimensions.

**Boundary matrix excerpt:**

- `skill-management` vs. `claude-plugin-developer`: both trigger on "create a new skill".
  Classified as **conflict**. Proposed resolution: bidirectional "Don't use for" clauses.
- `portfolio-audit` vs. `tech-stack-capture`: "Discover tech stack" overlaps.
  Classified as **overlap**. Proposed resolution: restrict `portfolio-audit` to
  cross-portfolio scope.

**Spec-induced gap identified:**

- `spec/project/spec-drift-audit/en.md` is spec-complete with MUST rules.
  No `spec-drift-audit` skill or agent exists.
  Three per-artefact plans reference a non-existent `spec-drift-audit` target.

**Classification findings:**

- `vocab-drift-audit`: read-only scan, no mid-flow approval during scan. Agent-bias
  per `spec/claude/skill-vs-agent/` primary decision rule. Recommended: hybrid pattern.
- All 9 agents missing `phase:` frontmatter field. Critical per `agent-management`.

**Wave classification summary:**

- Wave 1: 6 mechanical Critical sweeps, parallelisable
- Wave 2: 3 description/boundary sweep PRs
- Wave 3: 4 spec-extension PRs (precondition for Wave 4)
- Wave 4: 5 structural new-artefact PRs

> Phase 2 complete. 10 top findings identified, 4 waves proposed.
> Ready to draft the consolidated report?

---

## Turn 4 — phase 3: write consolidated report

> "Yes, write the report."

The skill reads `templates/sweep-report.template.md`, fills every field, and writes:

`.audits/skills-agents-sweep/2026-05-20-baseline.md`

> Report written. Frontmatter:
>
> ```yaml
> audit-type: skills-agents-sweep
> target: claude-shared (nolte-shared plugin)
> scope: all 34 skills + 9 agents
> repo-revision: b1b4d0b48e406f63ccc235b052cf80aef3cf02ae
> created: 2026-05-20
> status: open
> per-artefact-plans: 43
> ```
>
> Go/no-go: FAIL for release promotion without addressing Critical clusters.
>
> Wave 1 contains all mechanically fixable Criticals and can begin immediately.
> Shall I stage and commit the report?

---

## Turn 5 — commit

> "Yes, commit the report."

The skill stages and commits with:

```
chore(audit): open skills-agents-sweep 2026-05-20-baseline

Portfolio-wide sweep of 34 skills and 9 agents at b1b4d0b.
43 per-artefact plans produced. 4 implementation waves proposed.
Go/no-go: FAIL — Critical clusters W1.1–W1.4 must be addressed.
```
