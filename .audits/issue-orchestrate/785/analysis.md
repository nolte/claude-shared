---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "785"
classification: "feature-request"
secondary-classes: []
route: "direct"
status: draft
created: "2026-11-18"
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #785 — Add a specialist agent for Renovate preset and config authoring
- **URL**: https://github.com/nolte/claude-shared/issues/785
- **Labels**: enhancement, agents
- **Linked items**: nolte/gh-plumbing#439, #447, #454, #467 (closed issues), #483 (PR); `spec/project/continuous-improvement/` §Portfolio gap closure
- **Prior art checked**: no open PR (`gh pr list --state open` → empty); no agent or skill named for Renovate authoring (`grep -rli renovate agents plugins/*/agents skills/*/SKILL.md plugins/*/skills/*/SKILL.md` → 14 mentions, none an owner); no Renovate spec under `spec/` (`ls spec/project | grep -i renov` → empty); no roadmap item
- **Working copy**: `/home/nolte/repos/.worktrees/claude-shared/785-renovate-config-author`; created via `task worktree:add` off `5de7cd07`; ignore check `git check-ignore -q` on this path: ignored=1 (not ignored)
- **Lane**: `lane: true`, last lane of the 2026-11-18 backlog partition; returns `committed-locally`
- **Requirements gate**: operator override, 2026-11-18 ("Alle Empfehlungen"): the issue states scope, owned verification, boundary, discoverability, and two acceptance criteria; no `requirements-elicit` run

## Classification

- **Primary class**: feature-request
- **Secondary class(es)**: none
- **Rationale**: a new agent as a new capability; closes a portfolio gap per `spec/project/continuous-improvement/en.md:49`.
- **Asserted cause verified**: confirmed for this repository (the grep above). The four recurrences exist as closed gh-plumbing issues with Renovate preset work (`gh api repos/nolte/gh-plumbing/issues/<n>` → 439, 447, 454, 467 closed; 483 is a pull request). Who handled each (generalist or `fullstack-developer`) is unestablished; reading those issues' PR notes would settle it, and nothing in this lane rests on it.

## Scope

- **In scope**: one new agent `renovate-config-author` in `nolte-shared` (`agents/renovate-config-author.md`; operator decision 2026-11-18: every repository carries a Renovate config, including non-code repositories that don't install `nolte-engineering`), written to `spec/claude/`; whatever registration the repository requires for a new agent (README listing, description-budget baseline if the validator demands it); the two acceptance checks.
- **Out of scope**: a Renovate spec under `spec/`; changes to `nolte/gh-plumbing` or its preset; scaffolding the pointer file (`project-structure-apply`), CVE triage (`dependency-audit`), merging bot pull requests (the merge train); a real `issue-orchestrate` run in another repository.

### Measured constraints

- Agent description budget for `agents/` (nolte-shared): 9413 chars used, ceiling 10824, 1411 free (`AGENT_DESC_BASELINE_CHARS` and `AGENT_DESC_BUDGET_HEADROOM` in `scripts/validate_skills.py`). A description of 500–600 chars fits without touching the baseline.
- The agent catalog under `docs/<lang>/agents/` is generated at build time and gitignored (`git check-ignore docs/en/agents/nolte-shared/index.md` → ignored); a new agent appears through `scripts/docs/gen_catalog.py`, not through a tracked page.
- develop carries the delegation guard: "the `x` skill" / "`x`-Skill" must name a shipped skill or a harness built-in.

## Route

- **Decision**: direct
- **Rationale**: one coherent outcome, one PR strand, no roadmap item.

## Work packages

### P1 — Author the agent

- **Problem statement**: no specialist owns Renovate preset and `renovate.json` authoring, so `issue-orchestrate` routes it to a generalist.
- **Acceptance criteria**:
  1. `agents/renovate-config-author.md` exists with frontmatter and body conforming to `spec/claude/agent-management/`, `skill-agent-frontmatter`, `skill-agent-naming`, `skill-vs-agent`.
  2. Its description names "Renovate preset" and "renovate.json", states the boundary (not the pointer scaffold, not CVE triage, not merging bot pull requests), and keeps `agents/` under the description ceiling.
  3. The body covers the scope of the issue (managers, regex `customManagers` with both `matchStringsStrategy` values, `packageRules`, grouping, schedules, automerge rules, major-version migrations, preset-versus-repo-local scope) and owns the four validation steps (`renovate-config-validator --strict`; matchStrings run against the real files with the captures listed; `renovate --platform=local --dry-run=lookup` with the preset inlined; the group-branch check) plus a consumer-impact section for the PR's Risk / rollout notes, saying that `gh search code` can't measure consumer impact.
  4. Every command or option the agent prescribes is established against Renovate's documentation or marked as needing verification at run time; nothing is asserted from memory.
  5. `python3 scripts/validate_skills.py` exits 0; `python3 -m pytest tests -q` passes.
- **Touched files / artifacts**: `agents/renovate-config-author.md` (new); `README.md` and `scripts/validate_skills.py` only if the repository's registration rules require it (measured by the specialist, not assumed)
- **Specialist**: `nolte-claude-dev:claude-plugin-developer` (draft-and-return; the orchestrating session applies the returned files unchanged)
- **Depends on**: none

### P2 — Review and routing check

- **Problem statement**: the issue's acceptance asks that the agent passes `agent-review` and that `issue-orchestrate` resolves Renovate work to it.
- **Acceptance criteria**:
  1. `agent-review` on the new agent leaves no Critical or Warning open; its findings are fixed through P1's specialist.
  2. A runtime lookup as `issue-orchestrate` operation 5 performs it (the `description:` lines of every agent and skill in the four roots, matched against a package "change `renovate-configs/common.json`: add a regex custom manager and a package-rule group") resolves to `renovate-config-author` and to no other candidate with an equal claim; the candidates compared are recorded.
  3. `mkdocs` catalog generation lists the agent (`python3 scripts/docs/gen_catalog.py` or the docs build), recorded with the command output.
- **Touched files / artifacts**: none beyond P1's, plus the review plan `agent-review` writes under `.audits/agent-review/`
- **Specialist**: `nolte-claude-dev:agent-review` (skill)
- **Depends on**: P1

## Existing installations / upgrade / rollback

health gate: none (Claude plugin). Surfaces: invocation names — one agent name is added, none renamed or removed (`git diff --name-status` shows an addition under `agents/`); no persisted state, no consumer configuration key, no artifact path.

- P1: an installation updated from the previous release gains the agent; a rollback removes it and loses nothing. Proving check: `name:` set of `agents/*.md` is a superset of the previous one.
- P2: not applicable — touches no persisted state, consumer configuration key, invocation name or artifact path.

## Dependency ordering

P1 → P2.

## Risks

- The agent prescribes Renovate options from memory that don't exist or changed → criterion P1.4; the diff review checks the named options against Renovate's documentation.
- A new description that also claims work `project-structure-apply`, `dependency-audit` or `cicd-pipeline-design` own blurs routing → criterion P2.2 compares the candidates.
- No governing spec exists for Renovate authoring; if `agent-management` requires one for a rule-bearing agent, that widens the scope and stops for the operator.
- The aggregate description weight of `agents/` grows by one description; measured headroom covers it.
- No security-sensitive path is touched; the agent itself writes Renovate configs in consumer repositories, so its tool list and its confirmation behaviour are part of the diff review.

## Open questions

none

## Findings

| Finding | Source | Outcome | Reproduction | Issue |
|---|---|---|---|---|

## Dispatch log
