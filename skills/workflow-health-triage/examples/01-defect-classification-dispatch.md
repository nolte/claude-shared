# Example 01 — `defect` classification, dynamic agent dispatch

Demonstrates the happy-path triage flow: a failing `mkdocs build` step on `develop` references a markdown file the head commit just modified, the skill classifies the failure as `defect`, runtime-`Glob`s `agents/*.md` to discover the candidate set, picks the agent whose `description:` line names "spec-conformant authoring of skills/agents", dispatches it, and pre-populates the fix PR's Risk / rollout notes with the classification plus the dispatched agent name.

## Input prompt

> Triage diesen roten Workflow-Run auf `develop`: <https://github.com/nolte/claude-shared/actions/runs/9988111222>. Der `docs.yml`-Build ist gefailt, ich glaube nach meinem letzten Skill-Edit. Bitte den Fix dispatchen.

## Input files

Repository state when the skill is invoked:

- `spec/project/workflow-health/en.md` — present (canonical), declares the six classifications and §Specialised-agent dispatch contract.
- `.github/workflows/docs.yml` — required check on `develop`, conclusion `failure`, failing step is `Build MkDocs site`.
- `gh run view 9988111222 --log-failed` excerpt:

  ```

  ERROR    -  Config value 'nav': Reference to non-existent file 'skills/workflow-health-triage/SKILL.md'

  ```

- `git log --oneline -1 <headSha>` resolves to commit `feat(skills): rename workflow-health-triage SKILL frontmatter`, which renamed `skills/workflow-health-triage/skill.md` → `skills/workflow-health-triage/SKILL.md` casing-only.
- `agents/` directory contains (at runtime — exact set is discovered, not hard-coded):
  - `agents/claude-plugin-developer.md` with `description:` mentioning *"spec-conformant authoring and revision of Claude Code skills, agents, and plugin manifest files"*.
  - `agents/audience-doc-author.md` with `description:` mentioning *"audience-aware MkDocs documentation prose"*.
  - `agents/feature-consistency-reviewer.md` with `description:` mentioning *"feature-spec acceptance-criterion consistency review"*.
- `gh auth status` — authenticated.

## Expected behaviour

1. **Preconditions pass.** The skill confirms `spec/project/workflow-health/en.md` exists, that the run is on `develop` with `conclusion: failure`, and that the user supplied the run URL — no clarifying question needed.
2. **Inspect in parallel.** The skill issues the four documented calls (`gh run view --json …`, `gh api …/jobs`, `gh run view --log-failed`, `git log --oneline -1 <headSha>`) in a single batched tool call.
3. **Classify as `defect`.** The failing step references `skills/workflow-health-triage/SKILL.md`, which the head commit's diff renamed; per the spec's first row this is `defect`. The skill confirms the classification with the user in German (per the user-language policy) before dispatch, because `defect` is one of the three high-cost classes.
4. **Dynamic candidate discovery.** The skill `Glob`s `agents/*.md` plus `~/.claude/agents/*.md`, `Read`s the `description:` line of every hit, and builds a runtime `(name, description)` table. No agent name is hard-coded in the skill body — the table is rebuilt this invocation.
5. **Match on description, not on name.** Walking the candidates: `audience-doc-author` covers documentation prose (no match — the file is a skill manifest, not docs prose), `feature-consistency-reviewer` covers feature-spec consistency (no match), `claude-plugin-developer`'s description names "spec-conformant authoring of skills" — best match for a `defect` in a skill manifest. The skill picks `claude-plugin-developer`.
6. **Dispatch.** `Agent(subagent_type="nolte-shared:claude-plugin-developer", …)` with the classification (`defect`), the run URL, the failing-step excerpt (`Reference to non-existent file 'skills/workflow-health-triage/SKILL.md'`), and a fix-PR-title hint (`fix(skills): restore mkdocs nav reference for workflow-health-triage`). The skill waits for the agent's report before continuing.
7. **Open the fix PR with audit trail pre-populated.** The skill chains `pull-request-create` with the Risk / rollout notes pre-populated as:
   - `Triage classification: defect`
   - `Dispatched agent: nolte-shared:claude-plugin-developer`
   The user still confirms title and body before push.
8. **Stop after PR open.** The skill does **not** merge. Final report includes the run ID, classification, dispatched agent name, fix-PR URL, and the literal next-action hint *"invoke `pull-request-merge` after CI is green"*.
9. **Hard rules respected.** No `gh run rerun` is called before classification is recorded. No `--admin` flag, no `continue-on-error` proposal, no required-check removal. The dispatched-agent name (literal `subagent_type` argument) appears in the fix PR's Risk / rollout notes — not the human-friendly nickname.
10. **User-language policy.** All user-facing dialogue is in German; every `git`, `gh`, and `Agent(subagent_type=…)` invocation stays English so the audit trail is grep-able portfolio-wide.
