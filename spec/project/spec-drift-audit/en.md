# Spec Drift Audit

Status: draft

## Context
The portfolio maintains a growing set of specifications under `spec/<topic>/<slug>/`. At the same time, the actual repository state changes through pull requests, dependency bumps, platform evolution (GitHub, Claude Code, Taskfiles) and ad-hoc hotfixes, and it does so faster than specs are kept current. Without a binding reconciliation process, silent drift builds up in both directions: either repositories diverge from their specs (spec MUST rules are not implemented) or specs document a target state that practice has, for good reason, moved past. Both forms of drift undermine the whole point of using specs as a trustworthy reference for humans and AI agents. This spec therefore defines the binding, recurring audit process: when it runs, which scope it covers, how results are handled, and how the feedback loop returns as either a spec revision or an implementation fix.

## Goals
- Every repository in the portfolio runs a spec-versus-implementation reconciliation at documented trigger intervals
- Findings are either fixed in code or config, or intentionally lifted into a spec revision, within a documented response window — no "known bug, next quarter" limbo
- The audit ties existing specialized checkers (skills, linters, actions) together into a single view of reality, instead of letting them run in isolation
- New specs arrive with a testable audit strategy (who checks, how often, with which tool) from day one
- The audit history is visible inside the repository (a short audit note as commit, issue, or audit file) so iterative improvement is traceable

## Non-Goals
- Internal mechanics of the individual audits themselves — for example how `project-structure-apply` operates or how `vocab-drift-audit` compares upstream vocabularies (each covered by its own skill or spec)
- Replacement of existing linters and CI checks — they remain the continuous guardrail; this audit is the periodic deep dive
- Release-cadence policy or sprint rituals — not prescribed here; audits are event-driven or quarterly, fitted to the repository context
- Mandating a concrete tooling pipeline — the spec requires documented execution, not any particular technology

## Requirements

### Audit scope
- **MUST** treat "implementation" for the purpose of this spec as covering: source code (`src/`, `skills/`, `agents/`), configuration files (`.github/`, `.claude/`, `Taskfile.yml`, `mkdocs.yml`, `pyproject.toml` / `package.json` / equivalents), documentation (`docs/`, `README.md`, `CLAUDE.md`), and workflows plus hooks
- **MUST** include every spec under `spec/<topic>/<slug>/<canonical_language>.md` that carries a non-empty `## Requirements` or `## Acceptance Criteria` section; specs with `Status: draft` are **not** exempt
- **MAY** narrow the scope to one thematic area when the audit trigger is itself narrow (for example a `pull-request-workflow`-only audit triggered by a change to that spec); the narrowing **MUST** be recorded in the audit result

### Triggers and cadence
- **MUST** perform a full-scope audit at least once per calendar quarter; the audit calendar follows calendar quarters, not individual availability
- **MUST** additionally trigger a thematically matching partial audit whenever a spec changes significantly (a new MUST rule, a modified acceptance criterion, a shift in scope boundaries) — at the latest in the follow-up merge after the spec update
- **SHOULD** include the spec coupling of every newly introduced skill or agent in the same audit cycle, so new artifacts do not start their life already drifting

### Execution
- **MUST** run each audit reproducibly: the audit result **MUST** name the tools used (`project-structure-apply`, `vocab-drift-audit`, `task lint`, and equivalents) and the exact Git revision of the repository under audit
- **MUST** produce a testable outcome per spec acceptance criterion: `pass`, `fail`, `blocked` (for example missing tooling installation), or `not-applicable` (the criterion does not apply to this repository, with a reason given)
- **SHOULD** hand automatable parts (Vale drift, project-structure reconciliation, branch-protection queries via the GitHub API) to a skill or workflow; manual checks are permitted, but their results **MUST** be recorded in the same structure

### Feedback loop — handling findings
- **MUST** address every `fail` finding within a documented response window: critical findings (security, release blockers) immediately, other findings at the latest by the next quarter
- **MUST** record one of three decisions per finding: (a) adjust the implementation so it satisfies the spec, (b) adjust the spec because reality has a good reason to diverge, or (c) document the finding as an Open Question when the decision needs outside input; the decision **MUST** be captured in writing
- **MUST NOT** silently ignore a `fail`, defer it to an unbounded future, or let it fall between audits; the audit history in the repository has to make every decision traceable
- **SHOULD** address repeating findings at the same location with a structural fix (an automated check, a stricter pre-commit rule, a spec clarification) after the second occurrence, instead of shipping another one-off fix

### Audit result artifact
- **MUST** persist the result of every audit as a commit or issue in the repository (a PR body counts only when the PR is merged); the artifact location **SHOULD** be chosen consistently per repository (for example always `docs/audits/YYYY-Q<n>.md`, or a GitHub issue with label `audit`)
- **MUST** record at least: date, trigger (quarterly, spec-change, new skill), scope, tools executed, per-criterion results, and the decisions taken per §Feedback loop

### Delimitation from other specs and skills
- **MUST** treat `spec/project/workflow-health/` as the *continuous* health check (keeping CI consistently green, triaging flakes) while this spec is the *periodic* deep audit; the two complement each other and **MUST NOT** be conflated
- **SHOULD** run the skills `project-structure-apply` and `vocab-drift-audit` as partial auditors inside the audit, while noting that each of them covers only one slice of the overall surface
- **MUST NOT** use this audit process as a justification to undermine other specs (for example `pull-request-workflow`) at the spec level — audit findings flow through the regular pull-request process

## Acceptance Criteria
- [ ] The repository contains a traceable audit history (commits, issues, or audit files) with at least one entry per calendar quarter since this spec was introduced — or a documented exception stating why a given quarter was skipped
- [ ] The most recent audit entry covers every spec under `spec/<topic>/<slug>/` whose `## Requirements` or `## Acceptance Criteria` section is non-empty, or explicitly lists which specs were omitted and why
- [ ] No `fail` finding from the most recent audit sits in the repository without a documented decision (adjust implementation / adjust spec / open question)
- [ ] Every significant spec change (new MUST rule or modified acceptance criterion) has a thematically matching partial audit recorded in its follow-up merge or a follow-up PR
- [ ] Audit entries reference the Git revision of the audited repository state and the version of the audit skills used, so the audit can be reproduced

## Open Questions
- Should the audit artifact form be standardized portfolio-wide (a shared Markdown template under `docs/audits/` in every repository) or remain per-repository choice? Intentionally left open for a later decision.
- Does the portfolio need a central, cross-repository audit run (for example a cron-triggered action in `nolte/gh-plumbing`), or does the audit stay local per repository? Depends on whether central aggregation justifies the overhead.
