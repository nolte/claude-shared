# Example 01 — bounded bug, direct orchestration, multi-package DAG

Demonstrates the happy-path direct route: a bounded bug issue carrying two small
defects is comprehended, classified `bug`, decomposed into two work packages with a
dependency between them, dispatched to specialists resolved by runtime lookup in DAG
order, verified through `quality-gate`, and landed as a single open PR with the full
audit trail. The orchestration stops before merge.

## Input prompt

> Bitte Issue #312 end-to-end orchestrieren. Da sind zwei kleine Defekte drin: der
> Spec-Verweis in der `lektorat-apply`-Doku zeigt auf den falschen Pfad, und die
> SKILL.md selbst hat einen veralteten `see_also`-Eintrag. Ein PR reicht.

## Input files

Repository state when the skill is invoked:

- `spec/project/issue-orchestration/en.md` — present (canonical).
- Issue #312 `bug`-labelled: body names two defects in `skills/lektorat-apply/` and a
  stale `spec/project/lektorat/` path reference; no linked PRs; no milestone.
- `skills/lektorat-apply/SKILL.md` — present; `see_also` lists a renamed skill.
- `skills/` and `agents/` populated; at runtime the candidate walk discovers, among
  others, `skills/spec/SKILL.md` (`description:` names multilingual spec authoring)
  and `agents/claude-plugin-developer.md` (`description:` names spec-conformant
  authoring of skills, agents, plugin manifests).
- `gh auth status` — authenticated.

## Expected behaviour

1. **Preconditions pass.** The skill confirms the repo is a git repository, `gh auth
   status` is authenticated, and `spec/project/issue-orchestration/en.md` exists.
2. **Acquire.** The skill runs the parallel `gh issue view 312 --json …`,
   `--comments`, and linked-PR calls, then scans `skills/lektorat-apply/` and the
   referenced `spec/project/lektorat/` path, and checks `project/features/` and open
   PRs for prior art (none). It confirms the acquired issue and scope with the
   operator in German before proceeding.
3. **Classify `bug`.** One primary class, rationale "two concrete defects in shipped
   skill files". No operator confirmation gate is mandatory for `bug` (only
   `security` / `spec-change` require it), but the skill still surfaces the class.
4. **Decompose into two packages.**
   - `P1` — fix the stale `spec/project/lektorat/` path reference; acceptance: the
     reference resolves to an existing file and `task docs` builds; touches the spec
     pointer in the skill doc; specialist resolved to `nolte-shared:spec`.
   - `P2` — fix the stale `see_also` entry in `skills/lektorat-apply/SKILL.md`;
     acceptance: `task test` (`validate_skills.py`) passes and the named skill
     exists; touches `SKILL.md`; specialist resolved to
     `nolte-shared:claude-plugin-developer`; **depends on** `P1` (same file region).
5. **Write the pre-analysis artifact.** The skill instantiates
   `templates/analysis.template.md` to `.audits/issue-orchestrate/312/analysis.md`
   with both packages, the DAG ordering `P1 → P2`, the risks, and the route, and
   presents it for operator approval. It does not dispatch until approved.
6. **Route `direct`.** One coherent outcome (fix the two defects), a single PR
   strand, no new roadmap item → bounded → direct. Recorded as an operator-confirmed
   gate in the artifact.
7. **Runtime specialist lookup.** The skill `Glob`s every distribution root —
   `${CLAUDE_PLUGIN_ROOT}/skills/*/SKILL.md` and `${CLAUDE_PLUGIN_ROOT}/agents/*.md`
   (where the `nolte-shared` specialists resolve in a consumer repo), the project-local
   `skills/*/SKILL.md` and `agents/*.md`, and `~/.claude/agents/*.md` — reads each
   `description:`, and confirms the `P1 → spec` and `P2 → claude-plugin-developer`
   matches by stated responsibility, not by name. No specialist names are frozen in the
   skill body.
8. **Dispatch in DAG order.** `P1` first: `Agent(subagent_type="nolte-shared:spec")`
   — wait for its report, record the result in the artifact's dispatch log. Then
   `P2`: `Agent(subagent_type="nolte-shared:claude-plugin-developer")`. Each dispatch
   gates on operator confirmation.
9. **Verify.** The skill runs `quality-gate` green; no security-sensitive path is
   touched, so no `code-security-reviewer` run is required. It chains
   `pull-request-create` with **Risk / rollout notes** pre-populated:
   - `Issue: #312 — classification: bug`
   - `P1 dispatched specialist: nolte-shared:spec`
   - `P2 dispatched specialist: nolte-shared:claude-plugin-developer`
   and `Closes #312` in the body. The operator confirms title and body before push.
10. **Stop before merge.** The skill posts the artifact summary back to #312 as a
    comment (operator-confirmed), then reports the issue number, classification
    (`bug`), route (`direct`), the two dispatched specialists, the artifact path, the
    PR URL, and the next-action hint "invoke `pull-request-merge` after CI is green".
    It does **not** merge.
