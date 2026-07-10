---
name: kpi-derive
description: Derives a business application's project-specific KPIs from its goals, requirement documents, and source code, writing a human-readable artifact to project/kpis/<slug>.md per spec/project/kpi-definition-process/. The `derive` operation dispatches the read-only kpi-signal-scanner agent, walks a GQM refinement (goal to question to metric), selects the key metrics as KPIs with the operator, and defines each against the SMART gate with a leading/lagging class; `revisit` re-derives against changed goals. Consumes an existing project/requirements/<slug>.md under a soft gate (warns and recommends requirements-elicit when absent, never blocks). Determination and definition only — never measurement, instrumentation, telemetry, or dashboarding. Invoke to derive KPIs, determine an app's KPIs, or define its key metrics; also German requests. Don't use to elicit requirements (requirements-elicit) or to build instrumentation or dashboards (fullstack-developer). Supports resume per spec/claude/resumable-work/.
tags: [requirements]
phase: plan
summary: "Derives a business application's KPIs from its goals, requirements, and source code via GQM+SMART, and writes project/kpis/<slug>.md — definition only, never measurement."
summary_de: "Leitet die KPIs einer Business-Anwendung aus Zielen, Requirements und Quellcode via GQM+SMART ab und schreibt project/kpis/<slug>.md — nur Definition, nie Messung."
use_when:
  - "you want to determine and define the KPIs of a business application from its goals and code"
  - "you have an elicited requirement artifact and want the KPIs that verify its business goals"
  - "you want to re-derive KPIs after the business goals or requirements changed"
dont_use_when:
  - situation: "You want to elicit the business requirements/goals themselves"
    alternative: requirements-elicit
  - situation: "You want to implement metric instrumentation, telemetry, or a dashboard"
    alternative: fullstack-developer
  - situation: "You want to decompose a roadmap item into features"
    alternative: feature-decompose
see_also:
  - kpi-signal-scanner
  - requirements-elicit
resumable: true
---

# KPI Derive

Determine and define the project-specific KPIs of a business application: which handful of indicators are the *key* ones for this application, and how each is defined. The output is a single human-readable artifact at `project/kpis/<slug>.md` that a reader can follow and challenge. This skill determines and defines KPIs — it never instruments, collects, computes, stores, or displays them.

Implements `spec/project/kpi-definition-process/` — the spec defines the GQM-based determination process, the per-KPI definition contract, the SMART gate, the KPI-vs-metric selection rule, the leading/lagging classification, the requirements soft-gate, and the hard measurement boundary. This skill binds those rules to the on-disk procedure and owns the interactive selection, the definition, and the write.

## German trigger phrases

This skill also triggers on equivalent German-language requests, including:

- "KPIs ableiten" / "die KPIs für diese App bestimmen"
- "unsere Schlüsselkennzahlen definieren"
- "KPIs aus den Anforderungen herleiten"
- "die KPIs nach der Zieländerung neu ableiten" (→ `revisit`)

## User-language policy

Detect the user's language from their message and conduct the interview in it — KPI selection is a dialogue. The written artifact uses the surrounding repository's primary language (English by default; follow the precedent of the existing `project/` docs). The per-KPI contract field keys (`id`, `name`, `definition`, `formula-intent`, `unit`, `target`, `type`, `owner`, `goal-linkage`, `data-source-pointer`, `rationale`) and the `leading|lagging` values stay verbatim from the spec.

## The hard boundary (load-bearing)

This skill stops at *definition*. It records `formula-intent` (the intended computation, in plain terms) and `data-source-pointer` (where the data would come from), never a wired-up query, a metrics client, an emitted counter, a collection pipeline, a stored series, or a dashboard. A request to "add the metric" or "build the dashboard" is out of scope — hand it to `fullstack-developer` with the KPI definition as its input. Per `spec/project/kpi-definition-process/` §Non-Goals, crossing this boundary is a spec violation.

## Inputs

- **Application scope**: the app/module whose KPIs are being derived, and a `<slug>` for the artifact (default: mirror the requirement artifact's slug when one exists).
- **Operation**: `derive` (default) or `revisit` (re-derive against changed goals).
- **Goal sources** (gathered in priority order, per the spec's soft gate):
  1. an existing `project/requirements/<slug>.md` artifact (the primary business-goal source);
  2. `project/goals.md` and `project/mission.md`;
  3. source-code signals (from the scanner).

## Operations

### `derive` (default)

1. **Soft-gate the goal source.** Look for `project/requirements/<slug>.md`. When it is **absent**, warn that goal linkage will be weaker, recommend running `requirements-elicit` first, and — only if the operator chooses to proceed — continue with `goals.md`/`mission.md` plus source signals, recording the caveat in the artifact header. Never block (spec §"Input sources", the deliberate soft-gate carve-out from `requirements-elicitation` §"H. Consumer contract").

2. **Dispatch the read-only scanner.** Dispatch `kpi-signal-scanner` (Agent) for the detection pass: it mines both the source tree and the requirement/goal documents and returns a structured inventory of **candidate** KPI signals, each keyed to a goal or requirement where one is discernible. Wait for the inventory before selecting.

3. **Refine goals into questions (GQM).** For each business goal, frame it with GQM's coordinates — *purpose* (improve/increase/reduce), *issue* (the outcome focus), *object* (the feature/process/journey), *viewpoint* (whose goal) — then derive the questions that characterise the goal's achievement. Ladder each scanner candidate back to a question and a goal; a candidate that ladders to nothing is a bottom-up artefact and is set aside, not published.

4. **Select the key KPIs (interactive — KPI vs metric).** Present the laddered candidates and select, *with the operator*, the few that are **key** (tied to a business goal). This is the judgement step the skill exists for; do not auto-promote every candidate. Record why each selected KPI earned selection (its `rationale`) and why notable candidates were rejected.

5. **Define each KPI against the contract + SMART gate.** For each selected KPI, fill every contract field and check the SMART gate (Specific, Measurable → `formula-intent`+`unit`, Achievable, Relevant → `goal-linkage`, Time-bound → a `target` horizon; Assignable → `owner`). A candidate that fails any SMART letter is recorded as a **not-yet-defined** open item, never published as a KPI. Classify each as `leading` or `lagging`; flag an all-lagging set.

6. **Confirm and write the artifact.** Reflect the KPI set back to the operator for confirmation, then write `project/kpis/<slug>.md` (see Artifact shape). Confirm the path back.

### `revisit` (re-derive on changed goals)

Triggered when the business goals or `project/requirements/<slug>.md` changed after the KPI artifact was written. Re-run steps 2–6 as a **diff** against the existing artifact: show which KPIs still hold, which need re-validation (reset their definition), and which have become irrelevant. Persist only after the operator accepts each diff item (spec §"The determination process": re-runnability).

## Artifact shape

`project/kpis/<slug>.md`, mirroring the layout of `project/requirements/`:

```text
# KPIs — <application / scope>

## Source
- requirements: project/requirements/<slug>.md   (or: none — derived from goals+source, caveat)
- goals: project/goals.md · mission: project/mission.md
- frameworks applied: GQM (goal→question→metric), SMART gate, leading/lagging

## K1 — <name>
- definition: <one sentence>
- formula-intent: <intended computation in plain terms — NOT a query>
- unit: <% | count | seconds | currency | ratio>   ·   target: <value/band + horizon>
- type: <leading | lagging>   ·   owner: <role>
- goal-linkage: <requirement id / goals.md outcome id / mission verifies_via>
- data-source-pointer: <where the data would come from — NOT wired up>
- rationale: <why this KPI is key to the goal; why it beat other candidates>

## Not-yet-defined candidates (open items)
- <candidate> — fails SMART <letter>: <what is missing>
```

## Gotchas

- **KPI ≠ metric.** The scanner surfaces many candidate metrics; only the few *key* ones tied to a goal become KPIs. A flat dump of every measurable quantity is the failure mode this skill exists to prevent — select, don't list.
- **Source code is a signal source, never a goal source.** A candidate mined from code still has to ladder back to a business goal from the requirements/goals to be selected; never invent a business goal from code alone.
- **The soft gate is not the hard gate.** Unlike `roadmap-plan`/`feature-decompose`/`issue-orchestrate`, this skill proceeds without a requirement artifact (with a recorded caveat) and needs no operator override — but goal linkage is weaker, so say so in the artifact.
- **`formula-intent` is intent, not instrumentation.** If you find yourself writing a SQL query, a PromQL expression, or a metrics-client call, you have crossed the measurement boundary — stop and record the plain-language intent instead.
- **An all-lagging KPI set can only report the past.** Flag it and pair the lagging outcomes with the leading inputs that move them; a healthy set has both.

## Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/kpi-derive/<run-id>.yml` after every operator-confirmation gate and at each named phase boundary (soft-gate, scan, selection, definition, write), carrying the selected-KPI set and the pending candidates so an interrupted derivation resumes without re-selecting confirmed KPIs. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot (the `<slug>` and scope) matches the current invocation; if one matches, prompt `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope and fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

## Hard rules

- **Never** cross the measurement boundary: no instrumentation, metrics client, emitted counter, collection pipeline, stored series, or dashboard — determination and definition only. Hand implementation to `fullstack-developer`.
- **Never** publish a candidate as a KPI unless it ladders back to a business goal (`goal-linkage` resolves to a real goal/requirement) and passes every SMART letter; otherwise record it as a not-yet-defined open item.
- **Never** auto-promote every scanner candidate; KPI selection is an interactive judgement call reserved to the operator.
- **Never** hard-block on a missing requirement artifact; warn, recommend `requirements-elicit`, and proceed with a recorded caveat.
- **Never** invent a business goal from source code alone; code yields candidate signals, goals come from the requirements/goals/mission.
- **Always** write the KPI set to `project/kpis/<slug>.md` in the contract shape, one block per KPI, with a source header naming the goal sources consumed.
- When `spec/project/kpi-definition-process/` and this skill disagree, the spec wins; this skill needs the update.

## Why this is a skill, not an agent

This skill follows the hybrid pattern: the read-only detection phase is delegated to the `kpi-signal-scanner` agent (context isolation, tool restriction), while the goal→question refinement, the KPI selection, the definition, and the write stay in the skill.

- **Mid-flow interactivity is the contract**: selecting the *key* KPIs out of many candidates and confirming each definition is a per-turn judgement dialogue with the operator; an agent's fire-and-forget contract would lose it.
- **Persistent on-disk artifact**: the deliverable is `project/kpis/<slug>.md`, read by downstream consumers; skills own persistent state.
- **Counter-dimension**: the signal-mining half (walk the source tree, read the requirement docs, cluster candidate signals) is self-contained and verbose — the context-window pressure that favours an agent. That pull is honoured, but only for the scan half, delegated to `kpi-signal-scanner`; the selection judgement and the persistent artifact keep the orchestrating surface a skill.
