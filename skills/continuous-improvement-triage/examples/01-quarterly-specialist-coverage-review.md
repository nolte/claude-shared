# Example 01 — Quarterly specialist-coverage review, findings dispatched to specialised agents

Demonstrates the `audit` operation: the user invokes the skill for the 2026-Q2 quarterly review on `nolte/claude-shared`. The skill scans the last quarter's merged remediation PRs, identifies two finding classes handled by a generalist, matches one to an existing specialist and surfaces the other as a portfolio gap. Findings are dispatched and the triage artifact is written.

## Input prompt

> Führe den Q2-2026 Specialist-Coverage-Review für dieses Repo durch. Letzte Audits haben ein paar Findings generalistisch behandelt — bitte prüfen, ob passende Spezialisten existieren, und ggf. dispatchen.

## Input files

Repository state when the skill is invoked:

- `spec/project/continuous-improvement/en.md` — present (canonical).
- `gh auth status` — authenticated as `nolte`.
- `gh pr list --state merged --limit 50 --json number,title,body,labels` returns 12 merged PRs from the last quarter. Three of them contain **Risk / rollout notes** that reference in-scope finding sources:
  - PR #108: source `spec-drift-audit`, dispatched specialist `nolte-shared:spec` — correctly traced.
  - PR #112: source `project-structure-apply`, `Dispatched specialist:` field reads "no matching specialist existed — generalist handled".
  - PR #115: source `vocab-drift-audit`, `Dispatched specialist:` field reads "no matching specialist existed — generalist handled". This is the second such vocab-drift occurrence this quarter; combined with one from Q1, the recurrence count for `vocab-drift` is now 3.
  - PR #117: source `workflow-health` incident, dispatched specialist `nolte-shared:workflow-health-triage` — correctly traced.
- `agents/` directory at runtime (discovered via `Glob`):
  - `agents/claude-plugin-developer.md` — description mentions "spec-conformant authoring of Claude Code skills, agents, and plugin manifests".
  - `agents/audience-doc-author.md` — description mentions "audience-aware MkDocs documentation prose".
- `~/.claude/agents/` empty.
- No `.audits/continuous-improvement/` directory yet.

## Expected behaviour

1. **Preconditions pass.** The skill confirms `spec/project/continuous-improvement/en.md` exists, `gh auth status` authenticated, triage template readable.

2. **Scan merged PRs.** The skill runs `gh pr list --state merged --limit 50 --json number,title,body,labels` and identifies the three PRs with traceable **Risk / rollout notes**. PR #108 and #117 are already correctly dispatched; no action needed. PRs #112 and #115 carry generalist notes—these become findings.

3. **Build the finding list.**
   - **F1 — project-structure-apply gap**: PR #112, 1 generalist-handled occurrence, first observed 2026-Q2. Below threshold.
   - **F2 — vocab-drift-audit gap**: PR #115 (plus Q1 precedent), 3 generalist-handled occurrences, threshold met.

4. **Resolve the runtime specialist catalog.** The skill `Glob`s `agents/*.md` and `~/.claude/agents/*.md`, reads every `description:` line, and builds the `(name, description)` table.

5. **Match F1 (project-structure-apply).** Walking the candidates: `claude-plugin-developer`'s description names "spec-conformant authoring of Claude Code skills, agents, and plugin manifests"—no explicit mention of project-structure. `audience-doc-author` covers documentation prose only. **No match.** Recurrence = 1; below the 3-threshold. Record as candidate for monitoring.

6. **Match F2 (vocab-drift-audit).** The spec `nolte-shared:vocab-drift-audit` skill exists (confirmed via `ls skills/vocab-drift-audit/`). The skill's description names "audit repository-local Vale vocabularies against the pinned upstream release". **Match found.** Routing correction: `nolte-shared:vocab-drift-audit` should have been used in PR #115 and its Q1 predecessor.

7. **Present findings and confirm decisions with the user.** In German: F1 deferred (below threshold, no specialist); F2 dispatched to `nolte-shared:vocab-drift-audit` for the current vocab-drift finding.

8. **Initialise triage artifact.** Propose `.audits/continuous-improvement/2026-Q2.md` from `templates/triage.template.md`. User confirms. Populate `## Findings` with F1 and F2, `## Processing log` with the `audit` entry dated 2026-05-21. Ask whether to fold into the Q2 `spec-drift-audit` artifact or keep standalone; user chooses standalone.

9. **Dispatch F2.** Call `Agent(subagent_type="nolte-shared:vocab-drift-audit")` with the finding (vocab-drift entries in local Accept/Reject that are already upstream in `nolte/vale-style`). Wait for agent report.

10. **Record decisions.** After agent report, append D1 to `## Decisions` in the triage artifact: finding F2, dispatched to `nolte-shared:vocab-drift-audit`, fix PR to be opened. The fix PR's **Risk / rollout notes** must contain:
    - Originating source: `vocab-drift-audit` finding from PRs #115 (2026-Q2) and Q1 predecessor.
    - Dispatched specialist: `nolte-shared:vocab-drift-audit`.

11. **Report back.** Triage artifact at `.audits/continuous-improvement/2026-Q2.md`, 2 findings: 1 dispatched (F2), 1 deferred-below-threshold (F1). Next review due 2026-Q3.
