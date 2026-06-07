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

## Issue metadata

- **Repository**: <!-- owner/repo -->
- **Issue**: <!-- #<N> — title -->
- **URL**: <!-- https://github.com/owner/repo/issues/N -->
- **Labels**: <!-- comma-separated -->
- **Linked items**: <!-- linked issues / PRs, or "none" -->
- **Prior art checked**: <!-- features / roadmap items / open PRs reviewed, or "none found" -->

## Classification

- **Primary class**: <!-- bug | feature-request | spec-change | security | docs | refactor | question | infra -->
- **Secondary class(es)**: <!-- none | <class>, ... -->
- **Rationale**: <!-- one line -->

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

## Dependency ordering

<!-- The DAG dispatch order, e.g. P1 → P2 → P4 ; P3 (independent). -->

## Risks

<!-- Each risk with a one-line mitigation. Security-sensitive paths MUST note the
     code-security-reviewer / security-review requirement before PR. -->

## Open questions

<!-- Questions for the operator that block or shape dispatch, or "none". -->

## Dispatch log

<!-- Appended during operation 5; one line per package once its specialist reports.
     <YYYY-MM-DD> P<k> dispatched to <subagent_type> — <result one-liner> -->
