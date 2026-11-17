---
artifact-type: issue-orchestration-analysis
repo: ""
issue: ""
classification: ""
secondary-classes: []
route: ""
status: draft
created: ""
---

# Issue Orchestration — Pre-analysis

<!-- Replace <N> with the issue number; this artifact lives at .audits/issue-orchestrate/<N>/analysis.md -->
<!-- Write the prose body in the issue's language; keep the machine-readable fields
     (classification label, specialist subagent_type, finding source) in English. -->
<!-- Run-scoped artifact: committed on the run's feature branch, then removed with a
     fix-forward `git rm` before the PR merges, per spec/project/issue-orchestration/
     §Pre-analysis artifact lifecycle. Anything worth keeping after the merge goes into
     the PR's Risk / rollout notes or the issue comment first. -->

## Issue metadata

- **Repository**: <!-- owner/repo -->
- **Issue**: <!-- #<N> — title -->
- **URL**: <!-- https://github.com/owner/repo/issues/N -->
- **Labels**: <!-- comma-separated -->
- **Linked items**: <!-- linked issues / PRs, or "none" -->
- **Prior art checked**: <!-- features / roadmap items / open PRs reviewed, or "none found" -->
- **Working copy**: <!-- <worktree path>; detect=<0 | 200 | 104 | 109 | no-taskfile | other code>; created via `task worktree:add` | via fallback `git worktree add -b`; ignore check `git check-ignore -q` on this path: ignored=1 -->
<!-- See references/working-copy.md. The ignore check runs before this file is written; an ignored path stops the run, so a written artifact always records "not ignored". -->

## Classification

- **Primary class**: <!-- bug | feature-request | spec-change | security | docs | refactor | question | infra -->
- **Secondary class(es)**: <!-- none | <class>, ... -->
- **Rationale**: <!-- one line -->
- **Asserted cause verified**: <!-- none asserted | confirmed: <file:line / command output> | refuted: <measurement that showed the divergence> -->

## Scope

- **In scope**: <!-- what this orchestration will deliver -->
- **Out of scope**: <!-- explicitly excluded, with a pointer if it routes elsewhere -->

## Route

- **Decision**: <!-- direct | pipeline -->
- **Rationale**: <!-- one coherent outcome + single PR strand + no new roadmap item → direct;
                     spans outcomes / multiple PR strands / new-or-retargeted roadmap item → pipeline -->
- **Pipeline hand-off** (pipeline route only): <!-- feature-decompose <roadmap-item> | roadmap-plan <new outcome> -->

## Work packages

<!-- One block per package. Each MUST carry a testable acceptance criterion.
     A package that cannot state one is a routing signal to the pipeline, not a package. -->

<!--
### P<k> — <short title>

- **Problem statement**: <!-- the sub-problem this package solves -->
- **Acceptance criteria**: <!-- testable, user-observable; how "done" is verified -->
- **Touched files / artifacts**: <!-- paths -->
- **Specialist**: <!-- <plugin>:<skill-or-agent> resolved by runtime Glob, or
                       "no matching specialised agent — generalist remediation" -->
- **Depends on**: <!-- P<j>, ... | none -->
-->

## Existing installations / upgrade / rollback

<!-- Required when the repository ships a deployable artefact: resolve the detected
     project type against spec/project/release-artifact/ §"Artefact taxonomy"; an OS or
     appliance image or a Helm chart the taxonomy doesn't name yet counts too. One row
     per package that changes what an installation runs. Prove it with an update test
     from the previous release, never a fresh install, which carries none of its state.
     No update health gate (a Claude plugin, a library or package consumed by version):
     write "health gate: none (<artefact kind>)" and name the state surfaces the installed
     version reads — persisted state (checkpoint schemas under .resume/<skill>/), consumer
     configuration keys or files, invocation names (skill/agent names, CLI flags),
     artifact paths — with a check proving compatibility (resume a previous-release
     checkpoint, validate_skills, a config-parse test).
| Package | Upgraded state | Update health gate | What a rollback restores and what it can't | Proving check |
|---|---|---|---|---|
| P<k> | <state of an installation updated from the previous release> | <gate name: passes / fails, or none (<artefact kind>) + surfaces read> | <restored state; what it can't restore> | <update boot / migration / compatibility test command> |
     A package that can't reach an installation: "P<k>: not applicable — <reason>".
     Without a health gate the only valid reason is "P<k>: not applicable — touches no
     persisted state, consumer configuration key, invocation name or artifact path".
     No deployable artefact: replace the table with
     "not applicable — the repository ships no deployable artefact (<project type>)". -->

## Dependency ordering

<!-- The DAG dispatch order, e.g. P1 → P2 → P4 ; P3 (independent). -->

## Risks

<!-- Each risk with a one-line mitigation. Security-sensitive paths MUST note the
     code-security-reviewer surface scoping and the security-briefed read-only diff
     review required before the PR (security-review only from a session rooted in
     the worktree). -->

## Open questions

<!-- Questions for the operator that block or shape dispatch, or "none". -->

## Findings

<!-- One row per finding raised beside the work packages (operation 6 diff review as
     "diff review @ <head-sha>", with a "no findings" row when it raised none;
     verification pass, class sweep, specialist result), triaged per
     references/finding-triage.md.
     Outcome: fixed directly (listed under the PR's Changes) | filed (referenced in
     Risk / rollout notes) | dismissed (unreproduced, with the settling observation).
| Finding | Source | Outcome | Reproduction | Issue |
|---|---|---|---|---|
-->

## Dispatch log

<!-- Appended during operation 5; one line per package once its specialist reports.
     <YYYY-MM-DD> P<k> dispatched to <subagent_type> — <result one-liner> -->
