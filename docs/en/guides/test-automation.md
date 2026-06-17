---
title: Test Automation
audience: [maintainer]
content_mode: explanation
track: developer-docs
last_updated: 2026-06-13
---

# Test Automation

The plugin ships a coherent family of test-automation capabilities: a set of specs that define the discipline, and a layer of skills and agents that develop, run, analyse, and audit tests against those specs. This guide is the map. It explains how the pieces fit together and when to reach for each one; the per-artifact reference lives in the generated [Skills](../skills/index.md) and [Agents](../agents/index.md) catalog.

## Two axes

Test automation here is organised along two orthogonal axes. Keeping them separate is what keeps the family coherent.

- **The pyramid: _what_ to test at which level.** A closed, ordered tier taxonomy (static analysis → unit → component → integration → contract → end-to-end) owned by the `test-pyramid-foundation` spec. Each tier has its own spec and a generator/reviewer agent pair.
- **The cycle: _how_ to develop a test.** An iterative determine → execute → analyse → adapt loop (a generalised red-green-refactor) owned by the `test-cycle-foundation` spec, driven by the `test-cycle-orchestrate` skill.

A concrete test lives at one tier (the pyramid axis) and is brought into existence through the cycle (the process axis). The cross-cutting capabilities (running the gate and auditing tier completeness) sit across both.

## The pyramid: What to test at which tier

The tier taxonomy is closed and ordered. Each functional tier (below static analysis) has a generator agent that scaffolds spec-conformant tests and a reviewer agent that audits existing ones against the tier spec.

| Tier | Generator agent | Reviewer agent | Tier spec |
|------|-----------------|----------------|-----------|
| Static analysis | _(lint + typecheck via the gate, no test agent)_ | n/a | `test-tier-static-analysis` |
| Unit | `unit-test-generator` | `unit-test-reviewer` | `test-tier-unit` |
| Component | `component-test-generator` | `component-test-reviewer` | `test-tier-component` |
| Integration | `integration-test-generator` | `integration-test-reviewer` | `test-tier-integration` |
| Contract | `contract-test-generator` | `contract-test-reviewer` | `test-tier-contract` |
| End-to-end | `e2e-test-generator` | `e2e-test-reviewer` | `e2e-test-automation` |

The end-to-end tier adds `e2e-result-reviewer`, which inspects a run's screenshots and protocol visually against the requirement and UI specs, a check the other tiers don't need.

To check whether a feature actually covers the tiers it should, run the **`test-pyramid-check`** skill: it audits a feature's tier completeness against the `test-pyramid-foundation` taxonomy and surfaces gaps and the ice-cream-cone anti-pattern.

## The cycle: How to develop a test

The `test-cycle-orchestrate` skill drives the iterative loop. Each phase has a realising spec and, where the work is specialised, an agent. The loop returns from phase 4 to phase 2 (re-execute) and feeds phase 3 back into phase 1 (a discovered defect becomes a new regression case); it terminates only on an explicit exit condition, never by weakening a test to force a pass.

| Phase | Capability | Phase spec |
|-------|------------|------------|
| 1 · Determine (red) | `test-case-extractor` agent (derives traceable, framework-agnostic cases from a requirement) | `test-cycle-case-determination`, `test-case-derivation` |
| 2 · Execute | `quality-gate` skill (runs the gate) | `test-cycle-execution`, `quality-gate` |
| 3 · Analyse | `test-result-analyzer` agent (classifies results into defect / flake / test-bug / infra) | `test-cycle-result-analysis` |
| 4 · Adapt (green) | `test-code-adapter` agent (minimal correct production change under the no-cheating rule) | `test-cycle-code-adaptation` |

## Running and auditing

Two cross-cutting capabilities apply at every tier:

- **`quality-gate`** (skill) runs the project's lint + typecheck + test gate in parallel and tabulates which checks failed. It's phase 2 of the cycle and the executable form of the static-analysis tier.
- **`quality-gate-enforcer`** (agent) reviews the gate _wiring_ (the Taskfile targets, pre-commit config, CI workflow, and timeouts) for spec conformance, rather than running the gate itself.

## End-to-end: Putting it together

A typical pass for a new feature:

1. **Derive cases** from the requirement with `test-case-extractor` (phase 1), then decide which tier each case belongs to using the pyramid taxonomy.
2. **Scaffold** the tests at each tier with the matching `*-test-generator` agent, and have the `*-test-reviewer` agent audit them.
3. **Run** the suite through the `quality-gate` skill (phase 2).
4. **Analyse** failures with `test-result-analyzer`, plus `e2e-result-reviewer` for E2E runs (phase 3).
5. **Adapt** the production code with `test-code-adapter` under the no-cheating rule, then re-execute (phase 4 → phase 2).
6. **Audit completeness** with `test-pyramid-check` before the feature is considered done.

`test-cycle-orchestrate` ties phases 1–4 into the iterative loop so the steps above run as one disciplined cycle rather than ad-hoc.

## Reference

- Per-skill pages in the [Skills catalog](../skills/index.md): `quality-gate`, `test-pyramid-check`, `test-cycle-orchestrate`.
- Per-agent pages in the [Agents catalog](../agents/index.md): the tier generator/reviewer pairs and the cycle agents.
- The governing specs live under `spec/project/` (`test-pyramid-foundation`, `test-cycle-foundation`, the per-tier and per-phase specs).
