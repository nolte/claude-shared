---
name: deployment-chart-manage
description: "Provisions and maintains a Helm application chart on the bjw-s `common` library, applying spec/project/bjw-s-common-chart-deployment/ and spec/project/kubernetes-deployment-best-practices/. Two operations: `provision` generates a complete best-practice chart greenfield; `reconcile` is the change-noticing process that detects what an application change (for example from `fullstack-developer`) requires the chart to gain, presents the gaps, and on approval extends the chart and re-audits. Dispatches `deployment-change-analyzer`, `bjw-common-deployment-generator`, and `deployment-bestpractices-reviewer`, and owns the chart files plus the README manual-steps section. Invoke to provision a deployment chart or reconcile one after the app changed; also German requests. Don't use to write application code (`fullstack-developer`) or run the CI quality gate (`quality-gate`). Supports resume per `spec/claude/resumable-work/`."
argument-hint: "[app to provision, or the app whose chart to reconcile after a change]"
tags: [scaffolding, orchestrate]
phase: build
summary: "Provisions a best-practice bjw-s common deployment chart and reconciles it when the app changes, orchestrating the change-analyzer, generator, and best-practices reviewer."
summary_de: "Stellt ein Best-Practice-bjw-s-common-Deployment-Chart bereit und gleicht es ab, wenn sich die App ändert; orchestriert Change-Analyzer, Generator und Best-Practices-Reviewer."
use_when:
  - "you want a deployment chart provisioned on the bjw-s common library, following the best practices"
  - "you want a chart reconciled after an application change (new env vars, an added service/worker)"
dont_use_when:
  - situation: "you want to write or change the application's own source code"
    alternative: fullstack-developer
  - situation: "you want to run the lint/typecheck/test quality gate"
    alternative: quality-gate
see_also:
  - bjw-common-deployment-generator
  - deployment-change-analyzer
  - deployment-bestpractices-reviewer
  - fullstack-developer
resumable: true
---

# Deployment Chart Manage: $ARGUMENTS

Provision or reconcile the Helm application chart for `$ARGUMENTS`, built on the bjw-s `common` library. This skill **orchestrates**; the heavy work is done by three dispatched agents, and their results flow back here so you drive the gates and own the chart on disk.

Governed by `spec/project/bjw-s-common-chart-deployment/` (chart structure and the README manual-steps contract) and `spec/project/kubernetes-deployment-best-practices/` (the security-and-scalability bar, with network policies and the security context as mandatory pillars). Don't restate those specs; the dispatched agents read them.

## Why this is a skill, not an agent

- **Orchestrator that chains other capabilities:** the flow dispatches `deployment-change-analyzer`, `bjw-common-deployment-generator`, and `deployment-bestpractices-reviewer`; the skill-orchestrates pattern (per `skill-vs-agent`) defaults the orchestrator to skill form.
- **Mid-flow gating lives in the conversation:** confirming the provisioning inputs (image, exposure, ingress host, secrets, storage), approving *which* drift gaps to apply during reconcile, and deciding whether a best-practice finding blocks are per-turn user-visible gates an agent's fire-and-forget shape would lose.
- **Owns a persistent on-disk artifact:** the chart files and the README manual-steps section are the deliverable; skills own persistent state.
- Counter-dimension considered: each phase (detect, generate, audit) is a self-contained agent; the loop that sequences them and gates on the operator is the orchestration, which stays a skill.

## Operations

### 1. `provision` (greenfield)

Generate a complete, best-practice chart for an app that has none.

1. **Confirm the inputs.** Establish the app's image coordinates, exposure (internal-only vs. an ingress host + class), required secrets, storage needs, and chart location. When these are ambiguous or unknown, elicit them (the `requirements-elicit` skill) rather than guessing; record any explicit assumption for the README.
2. **Generate.** Dispatch `bjw-common-deployment-generator` (provision mode) with the confirmed inputs. It writes `Chart.yaml`, `values.yaml`, the loader `templates/`, and the README, applying both specs, and verifies the chart renders.
3. **Audit.** Dispatch `deployment-bestpractices-reviewer` on the generated chart. On any Critical/Warning finding, hand it back to the generator to fix and re-audit; loop until the verdict is go.
4. **Surface manual steps.** Present the README's irreducible operator steps (image tag, ingress host, secrets, storage class, `helm dependency build`) and report the chart location.

### 2. `reconcile` (the change-noticing process)

Notice that the application changed — often through a `fullstack-developer` edit that added a config value or a new endpoint — and extend the chart to match.

1. **Detect drift.** Dispatch `deployment-change-analyzer` on the app and its existing chart. It returns a per-gap report: newly read env vars, new ports, an added controller (worker/cron), new persistence, new secrets, new egress, or a changed image.
2. **Gate on the gaps.** Present the gap list to the operator and get approval on which to apply. Never apply a gap the operator hasn't confirmed, and never remove a stale declaration without explicit confirmation.
3. **Extend.** Dispatch `bjw-common-deployment-generator` (extend mode) with the approved gaps. It makes the smallest correct change (usually new `env`/`envFrom` keys or an added `controllers.<id>`), preserving the chart's shape and never regressing an in-place best practice, and verifies it still renders.
4. **Re-audit and update the README.** Dispatch `deployment-bestpractices-reviewer`; loop on findings. Update the README manual-steps section for any new operator input (a new secret, a new host), and report what changed.

## Hard rules

1. **Never skip the best-practices audit** before declaring a chart done: every `provision` and every `reconcile` ends with a green `deployment-bestpractices-reviewer` verdict, or the outstanding findings are surfaced to the operator.
2. **The two mandatory pillars always hold** — a default-deny network policy and a hardened, `restricted`-profile security context — on both the provisioned and the reconciled chart.
3. **Never apply a drift gap or remove a stale declaration without operator approval;** the gap gate in `reconcile` is a user-visible decision, not an automatic one.
4. **Never commit a plaintext secret** into the chart; secrets are wired by reference and recorded as a manual README step.
5. **Never write the chart yourself or restate the specs here** — dispatch the agents (`deployment-change-analyzer`, `bjw-common-deployment-generator`, `deployment-bestpractices-reviewer`); when a spec disagrees with this skill, the spec wins, and propose a skill update rather than diverging.
6. **No commits, pushes, or cluster mutations** (`helm install`/`upgrade`, `kubectl apply`) — this skill produces and audits the chart; landing it and deploying it belong to the caller and the delivery pipeline.

## Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/deployment-chart-manage/<run-id>.yml` after every successful user-approval gate (input confirmation, gap approval, audit go/no-go) and after each named phase boundary. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope and the fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.
