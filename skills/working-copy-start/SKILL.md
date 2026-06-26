---
name: working-copy-start
description: Orchestrates the start of a new parallel working copy (git worktree) and makes it ready for work, per spec/project/parallel-working-copies/. Invoke when the user asks to "start a new working copy", "set up a worktree for feature X", "spin up a worktree and a plan", "begin work on a new branch in its own working copy", or equivalent German-language requests. Creates the worktree via `task worktree:add -- <branch> [slug]` (off origin/develop, keeping the primary checkout on develop), walks the operator through filling the seeded `.resume/<slug>/plan.md` plan-before-work stub (goal, current state, design decision with open questions, work steps, invariants, resume-anchor checklist), then hands off to do the substantive work in a fresh top-level session started from the worktree so it stays `claude --resume`-able, emitting the launch command and a ready-to-paste kickoff prompt. Does not do the feature work itself or open the PR (use `pull-request-create`). Supports resume per `spec/claude/resumable-work/`.
tags: [scaffolding]
phase: plan
summary: "Creates a spec-conformant worktree, fills its plan-before-work stub, and hands off to a fresh resumable session with a launch command and a kickoff prompt that leads with requirements-elicit."
summary_de: "Legt einen spec-konformen Worktree an, befüllt dessen Plan-Stub und übergibt an eine frische, wiederaufnehmbare Session mit Start-Befehl und einem Kickoff-Prompt, der mit requirements-elicit beginnt."
use_when:
  - "you want to start feature work in its own parallel working copy"
  - "you want a worktree plus a foundational plan before any substantive work begins"
  - "you want to begin a new branch in an isolated working copy and hand off to a fresh session"
dont_use_when:
  - situation: "You already have a worktree with finished work and just need to open a PR"
    alternative: pull-request-create
  - situation: "You want to author or scaffold a new skill or agent rather than start feature work"
    alternative: skill-management
see_also:
  - requirements-elicit
  - pull-request-create
examples:
  - prompt: "Start a new working copy for feat/parser-fix"
    outcome: "Worktree created off origin/develop, plan.md filled in, and a hand-off printing the launch command plus a kickoff prompt that leads with requirements-elicit before resuming the plan."
resumable: true
---

# Working Copy Start

Orchestrates the **start** of a parallel working copy: it creates a git worktree, satisfies the plan-before-work gate, and hands the work off to a fresh, resumable top-level session. It operationalises `spec/project/parallel-working-copies/` — specifically §Lifecycle: Create, §Lifecycle: Plan before work, and §Claude Code session scoping. It does **not** perform the substantive feature work in the worktree (that happens in the handed-off session) and it does **not** open the pull request (that is `pull-request-create`).

## Why this is a skill, not an agent

- **Mid-flow interactivity is the contract** — confirming the branch/slug, then filling the plan's load-bearing design decision and its open questions, are per-step operator dialogues; an agent's fire-and-forget contract would lose them.
- **Persistent on-disk artefacts are the deliverable** — the worktree and its `.resume/<slug>/plan.md` are durable state the operator carries into the next session; skills own persistent state.
- **Orchestrator role** — this is the first step of a "ship a feature" flow that later chains into `pull-request-create`; per `spec/claude/skill-vs-agent/` the orchestrator defaults to skill form.

## User-language policy

Detect the operator's language and respond in it. The plan stub and any committed configuration stay in English; the operator's free-form plan content may be in their own language.

## Guardrails

- **The primary checkout stays on `develop`.** Never switch it onto a feature branch. The worktree is the place the work happens; the primary checkout is only the launchpad it branches from. This is enforced by the `guard-primary-checkout` pre-commit hook and the `PreToolUse` feature-branch guard — do not work around them.
- **Create only via the conformant path.** Use `task worktree:add -- <branch> [slug]`, which branches off `origin/develop` with an explicit base ref and places the worktree under `${NOLTE_WORKTREE_ROOT:-~/repos/.worktrees}/<repo>/<slug>/`. Never `git worktree add` to an ad-hoc path, and never nest a worktree under `.claude/`.
- **The plan gate is documentary, not mechanical.** Fill the stub; do not add a hard-blocking hook. The value is the plan existing before work, not an enforced abort.

## Operations

### Start a working copy

1. **Collect the branch and optional slug.** The branch MUST carry an allowed prefix (`feat/`, `fix/`, `chore/`, `docs/`, `exp/`) per `spec/project/branching-model/`. Propose a kebab-case slug if the operator does not give one (defaults to the branch name minus its prefix).
2. **Create the worktree.** Run `task worktree:add -- <branch> [slug]`. This branches off `origin/develop`, seeds `.resume/<slug>/plan.md` with a plan stub, and prints the worktree path. Confirm the worktree path back to the operator.
3. **Fill the plan-before-work stub.** Open the seeded `.resume/<slug>/plan.md` inside the new worktree and walk the operator through completing every section: the goal, the researched current state, the load-bearing design decision **with the open questions to confirm before work starts**, the ordered work steps, the invariants and guardrails carried over from `CLAUDE.md` and the governing specs, and a status/resume-anchor checklist whose first unchecked box is where the next session resumes. Do not start the substantive work — capturing the plan is the gate.
4. **Hand off to a fresh resumable session.** Instruct the operator to do the substantive work in a **fresh top-level session started from the worktree** (`cd <worktree> && claude`), not a dispatched subagent or Workflow run, because only a top-level session's transcript is `claude --resume`-able (recoverable later via `task resume`). Emit both halves of the hand-off so the operator can paste them straight through:
   - the **launch command**, with the concrete worktree path filled in:

     ```
     cd <worktree-path> && claude
     ```

   - a ready-to-paste **kickoff prompt** for that fresh session. It **MUST** lead with an invocation of `/nolte-shared:requirements-elicit`, so the substantive work begins by capturing the working copy's requirement precisely (the same upstream gate `roadmap-plan`, `feature-decompose`, and `issue-orchestrate` rely on) rather than by acting on the first plausible guess; only then does it pick the work up from the plan. Use this shape:

     ```
     /nolte-shared:requirements-elicit capture the requirement for this working
     copy. Once the requirement artifact is at or above threshold, read the plan
     at .resume/<slug>/plan.md and begin the work from the first unchecked
     resume-anchor box, keeping the plan's status/resume-anchor checklist up to
     date as you go.
     ```

   Substitute the real `<worktree-path>` and `<slug>` so the operator copies a working command and prompt, not placeholders.

## Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/working-copy-start/<run-id>.yml` after every successful user-approval gate (worktree created, plan filled) and after each named phase boundary. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope and fail-closed semantics on schema or YAML errors are load-bearing in the spec; do not duplicate those rules here.

## Hard rules

- Never switch the primary checkout off `develop`; all feature work happens in the worktree.
- Always create the worktree through `task worktree:add`; never an ad-hoc `git worktree add` path, and never nested under `.claude/`.
- Never skip the plan gate: the plan at `.resume/<slug>/plan.md` MUST be filled before the substantive work begins.
- Never do the substantive feature work or open the PR from this skill; prepare and hand off only.
- When `spec/project/parallel-working-copies/` disagrees with this skill, the spec wins; propose updating this skill rather than diverging.
