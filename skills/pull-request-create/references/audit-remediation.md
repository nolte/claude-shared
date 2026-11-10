# Audit-triggered remediation PRs

Read when the branch name, commit log, or a linked audit artifact indicates that the PR remediates an in-scope finding from a portfolio audit.

## The two extra lines

When this PR remediates an in-scope finding from a portfolio audit (`spec-drift-audit`, `workflow-health`, `project-structure-apply`, `vocab-drift-audit`, `portfolio-audit`, `portfolio-inflight-triage`, `dependency-audit`, `prose-style`/`markdown-formatting` lint, or a manual review Issue), `spec/project/continuous-improvement/<canonical_language>.md` §"Traceability in remediation artifacts" **MUST**-requires **Risk / rollout notes** to additionally record both lines:

- `Originating source: <named finding source>`: the finding source listed above that triggered the fix (with a link where available), so the PR is traceable back to its trigger.
- `Dispatched specialist: <display-name> (subagent_type: <plugin>:<agent> | skill: <name>)`: the specialised agent or skill that produced the fix; or, when none matched, the literal `no matching specialist existed — generalist handled`.

Ask the user for both values whenever the branch name, commit log, or a linked audit artifact indicates an audit-triggered remediation; never invent them. Non-audit PRs omit both lines.

## Checklist (tick before `gh pr create`)

On such a PR, confirm all three before opening it, so both grep-stable fields are present by construction:

- [ ] **Risk / rollout notes** carries an `Originating source:` line naming the finding source.
- [ ] **Risk / rollout notes** carries a `Dispatched specialist:` line naming the specialist, or the literal `no matching specialist existed — generalist handled`.
- [ ] Both lines use those exact field labels verbatim, so they stay grep-stable portfolio-wide.
