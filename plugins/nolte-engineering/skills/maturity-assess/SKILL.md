---
name: maturity-assess
description: Assesses the build maturity of an application's capabilities per spec/project/capability-maturity-assessment/, writing project/maturity/<slug>.md to surface where implementation quality is lacking. The `assess` operation inventories business-facing capabilities top-down (never bottom-up from directories), maps each to an audience-identification audience, dispatches the read-only capability-maturity-scanner, then grades each on three axes — completeness, code quality, test coverage — into Bronze/Silver/Gold with a weakest-link overall tier and improvement lever; `reassess` re-grades as a diff. Consumes AUDIENCES.md under a soft gate (warns, never blocks). Grading only — never a merge gate, prioritisation, or dashboard. Invoke to assess capability maturity, grade an app's functions, or produce the maturity matrix; also German. Don't use for the binary PR gate (quality-gate), to define audiences (audience-identify), or KPIs (kpi-derive). Supports resume per spec/claude/resumable-work/.
tags: [audit, quality-gate]
phase: quality
summary: "Grades an app's capabilities on three axes (completeness, code quality, test coverage) as Bronze/Silver/Gold plus a weakest-link overall, writing project/maturity/<slug>.md — advisory, not a gate."
summary_de: "Bewertet App-Funktionen auf drei Achsen (Vollständigkeit, Code-Qualität, Testabdeckung) als Bronze/Silber/Gold plus Weakest-Link-Gesamtstufe, schreibt project/maturity/<slug>.md — beratend, kein Gate."
use_when:
  - "you want to grade how complete, well-built, and tested each of your application's functions is, and for whom"
  - "you want a checked-in maturity matrix that guides development by showing where implementation quality is weakest"
  - "you want to re-grade capability maturity after the application changed (which held, moved up, or regressed)"
dont_use_when:
  - situation: "You want the binary pass/fail decision on whether a PR may merge"
    alternative: quality-gate
  - situation: "You want to enumerate and characterise the application's audiences"
    alternative: audience-identify
  - situation: "You want to define the application's business KPIs"
    alternative: kpi-derive
see_also:
  - capability-maturity-scanner
  - quality-gate
  - test-pyramid-check
  - audience-identify
resumable: true
---

# Maturity Assess

Grade the **build maturity** of a business application's capabilities: for each user-meaningful function the app performs, how *fully* it is built (Axis A), how *well* the code is built (Axis B), and how *trustworthily* it is verified by tests (Axis C) — each on a Bronze / Silver / Gold scale, plus a separate weakest-link **overall** tier and the single **improvement lever** that would raise it. The output is one human-readable, checked-in artifact at `project/maturity/<slug>.md` that a reader can follow and challenge, and that **guides further development by making visible exactly where implementation quality is lacking**.

Implements `spec/project/capability-maturity-assessment/` — the spec defines the top-down inventory method, the audience-mapping soft gate, the three axes and their Bronze/Silver/Gold rubrics, the machine-derivable-vs-judgement split, the weakest-link overall rule, the artifact contract, and the project-configurable thresholds. This skill binds those rules to the on-disk procedure and owns the inventory, the audience mapping, the judgement axes, the tier assignment, the operator confirmation, and the write.

## German trigger phrases

This skill also triggers on equivalent German-language requests, including:

- "Reifegrad der Funktionen bewerten" / "die Capabilities einstufen"
- "Reifegrad-Matrix erstellen" / "wo mangelt es an der Umsetzungsqualität?"
- "bewerte, wie vollständig und getestet unsere Funktionen sind"
- "den Reifegrad nach den Änderungen neu bewerten" (→ `reassess`)

## User-language policy

Detect the user's language from their message and conduct the assessment dialogue in it — inventory, audience mapping, and completeness are judgement calls made with the operator. The written artifact uses the surrounding repository's primary language (English by default; follow the precedent of the existing `project/` docs). The contract field keys (`id`, `name`, `description`, `audiences`, `axis-a`, `axis-b`, `axis-c`, `overall`, `improvement-lever`, `rationale`) and the tier values (`Bronze | Silver | Gold | Unrated`) stay verbatim from the spec.

## The hard boundary (load-bearing)

This skill produces an **advisory graded classification**, never a gate. It grades the current state; it never blocks a merge, fails CI, refuses a release, decides *which* Bronze capability to promote next, or renders a dashboard. The pass/fail merge decision stays owned by `quality-gate`; prioritisation stays with `roadmap-plan` / `sprint-plan`; dashboarding is out of scope. A request to "block the PR until this is Silver" or "build the maturity dashboard" crosses the boundary — decline and point at the owning tool. Per `spec/project/capability-maturity-assessment/` §Non-Goals, crossing this boundary is a spec violation.

## Inputs

- **Application scope**: the app/module whose capabilities are assessed, and a `<slug>` for the artifact (default: mirror the requirement or audience artifact's slug when one exists).
- **Operation**: `assess` (default) or `reassess` (re-grade against a changed application, as a diff).
- **Audience source**: `spec/project/audience-identification/`'s artifact (`AUDIENCES.md` or its ratified alternative) — consumed, never re-derived.
- **Capability sources** (top-down, in priority order): `project/features/`, `project/requirements/<slug>.md`, the user-facing surface (routes, commands, UI entry points) — never the directory structure.
- **Thresholds**: the project-configured coverage bands (lower/middle/upper), complexity ceiling, and duplication bound. When unset, use the spec's reference defaults and record that in the artifact header.

## Operations

### `assess` (default)

1. **Soft-gate the audience artifact.** Look for the `audience-identification` artifact. When it is **absent**, warn that audience mapping is unavailable, recommend running `audience-identify` first, and — only if the operator chooses to proceed — continue with audience mapping recorded as an open item in the header. Never block (spec §Audience mapping, the soft-gate mirroring the sibling KPI spec).

2. **Inventory the capabilities top-down (interactive).** With the operator, enumerate the **business-facing capabilities** — user-meaningful functions a named audience recognises ("record a harvest", "detect a climate zone"), each traceable to a requirement or acceptance criterion. Draw them from `project/features/`, the requirement artifact, and the user-facing surface — **never** bottom-up from modules/classes/endpoints (those are the *evidence* a capability is graded against, not the unit). Assign each a stable short id (`C1`, `C2`, …), a name, and a one-sentence description of what it does for its audience. A candidate that cannot ladder back to something a user wants is a code artifact — set it aside.

3. **Map each capability to at least one audience.** From the consumed artifact, map every capability to ≥1 audience; a capability serving no identifiable audience is a defect (either the audience list is incomplete or the capability is dead — surface it). Where maturity **materially diverges by audience** (Gold for the primary audience, a Bronze stub for a secondary path), record the per-audience divergence rather than flatten it.

4. **Dispatch the read-only scanner.** Dispatch `capability-maturity-scanner` (Agent) with the inventoried capability list and the configured thresholds. It returns per-capability **machine-derivable signals** for Axis B and Axis C with a `proposed` tier for each, plus Axis A **evidence markers** (never an Axis A tier). Wait for the inventory before grading.

5. **Grade the three axes per capability.**
   - **Axis A — Implementation completeness (judgement; the skill assigns).** Grade against the capability's acceptance criteria / requirement (consume `test-case-derivation` and `spec-driven-development` where present; else state the completeness baseline used). Bronze = core happy path reachable, primary AC satisfied, gaps/TODOs permitted; Silver = all documented ACs satisfied, principal error/validation paths handled, no known gaps on the primary path, complete across its surface (API+UI+i18n) for that path; Gold = Silver plus edge/failure cases, applicable NFRs met, no open defects/TODOs, end-user docs for every mapped audience. The scanner's evidence markers inform, but never set, this tier.
   - **Axis B — Code quality (largely machine-derivable; confirm the proposal).** Take the scanner's proposed tier and confirm or override it against ISO/IEC 25010 maintainability and the static-analysis tier. Bronze = builds and passes static analysis with no errors (warnings ok); Silver = no warnings, style guide fully followed, layering respected, complexity under the configured ceiling, duplication under the bound, typed where the stack supports it; Gold = Silver plus documented public interfaces, no remaining smells/debt markers, SAST clean, low complexity throughout, and **human review passed** (confirm this — the scanner cannot).
   - **Axis C — Test coverage across tiers (largely machine-derivable; confirm the proposal).** Consume the Test-Pyramid tiers (never redefine one). Bronze = passing unit tests on core logic, static green, coverage clears the lower band; Silver = plus component/integration tests and contract tests on any service boundary, coverage clears the middle band, every tier green in CI; Gold = plus ≥1 E2E test through a mapped audience's real workflow, failure/edge cases tested, coverage clears the upper band, each test traceable to the capability. Honour **coverage-as-a-guide**: the bands are advisory, never a merge gate; report mutation score alongside coverage where available. Confirm that a Gold E2E genuinely exercises the *mapped audience's* workflow (the scanner cannot).

6. **Derive the overall tier (weakest-link) and the improvement lever.** The `overall` tier is the **minimum** of the three axis tiers (Gold only when every axis is Gold; Bronze when any axis is Bronze; Unrated when any axis is below Bronze). A strong axis **must not** compensate for a weak one. Report all three axis tiers **and** the overall tier — never collapse to the overall alone. Where the axes diverge, record the **improvement lever**: the single axis that, if raised, would raise the overall tier. This is the "where is implementation quality lacking" answer the assessment exists to give.

7. **Confirm and write the artifact.** Reflect the graded matrix back to the operator for confirmation, then write `project/maturity/<slug>.md` (see Artifact shape). Confirm the path back.

### `reassess` (re-grade on change)

Triggered when the application changed after the matrix was written. Re-run steps 2–7 as a **diff** against the existing artifact: show which capabilities **held** their tier, which **moved up**, and which **regressed**, rather than silently replacing the matrix (spec §The capability inventory, re-runnability). Persist only after the operator accepts each diff item.

## Artifact shape

`project/maturity/<slug>.md`, mirroring the layout of `project/kpis/`:

```text
# Capability Maturity — <application / scope>

## Assessment context
- audience artifact: <path>   (or: none — mapping recorded as open item, caveat)
- capability sources: project/features/ · project/requirements/<slug>.md · user-facing surface
- thresholds: coverage bands <lower/middle/upper> · complexity ceiling <n> · duplication bound <n>  (source: <configured | spec defaults>)
- frameworks: OpenSSF Bronze/Silver/Gold · ISO/IEC 25010 (Axis B) · Test Pyramid (Axis C)

## C1 — <name>
- description: <one sentence — what it does for its audience>
- audiences: <audience id(s) from the consumed artifact>
- axis-a (completeness): <Bronze|Silver|Gold|Unrated>
- axis-b (code quality): <Bronze|Silver|Gold|Unrated>
- axis-c (test coverage): <Bronze|Silver|Gold|Unrated>
- overall (weakest-link): <Bronze|Silver|Gold|Unrated>
- improvement-lever: <the one axis to raise next to lift the overall tier>
- rationale: <why each axis earned its tier — defensible, per axis>
- per-audience divergence: <audience → tier, only where maturity materially diverges>

## Open items
- <capability> — Axis A ungradeable: <no acceptance criteria; baseline used / recommend spec-driven-development>
- <capability> — no audience mapped: <audience list incomplete or capability dead?>
```

## Gotchas

Per `spec/claude/skill-management/` §Gotchas: concrete corrections to non-obvious environment facts the executing agent would otherwise get wrong.

- **A capability is not a code artifact.** A module, class, or endpoint is *evidence* a capability is graded against — never the unit of grading. If the inventory reads like the `src/` tree, it was assembled bottom-up; re-derive it top-down from what an audience recognises.
- **The axes do not compensate.** Gold code (Axis B) does not offset an untested capability (Axis C Bronze). The overall tier is the *minimum*, and the axis divergence is the actionable content — report all three axis tiers, never just the overall.
- **The scanner proposes B and C; it never sets A or the overall tier.** Axis A (completeness against acceptance criteria) and the weakest-link overall tier are the skill's judgement; take the scanner's B/C proposals and confirm or override them, don't rubber-stamp.
- **Coverage bands grade, they never gate.** Clearing the upper band lifts Axis C toward Gold; missing it lowers the grade — it never blocks a merge. If you find yourself failing CI on a band, you have crossed into `quality-gate`'s territory.
- **The soft gate is not the hard gate.** Unlike `roadmap-plan`/`issue-orchestrate`, this skill proceeds without an audience artifact (mapping recorded as an open item, with a header caveat) and needs no operator override — but the mapping is weaker, so say so.
- **Thresholds are the project's, not the spec's.** The coverage bands, complexity ceiling, and duplication bound are project-configurable and must satisfy `Bronze ≤ Silver ≤ Gold`; a config that inverts or flattens a band is invalid — record the numbers used in the header so the grade is auditable.

## Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/maturity-assess/<run-id>.yml` after every operator-confirmation gate and at each named phase boundary (soft-gate, inventory, audience-mapping, scan, grading, write), carrying the inventoried capabilities and their assigned per-axis tiers so an interrupted assessment resumes without re-inventorying or re-grading confirmed capabilities. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot (the `<slug>` and scope) matches the current invocation; if one matches, prompt `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope and fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

## Hard rules

- **Never** turn a maturity tier into a gate: no merge block, CI failure, release refusal, prioritisation decision, or dashboard — advisory grading only. Point gating at `quality-gate`, prioritisation at `roadmap-plan`/`sprint-plan`.
- **Never** inventory capabilities bottom-up from the directory structure; the inventory is top-down and every capability ladders back to a requirement/acceptance criterion and at least one audience.
- **Never** let a strong axis compensate for a weak one; the overall tier is the weakest-link minimum, and all three axis tiers plus the overall tier are reported explicitly.
- **Never** let the scanner assign the Axis A or overall tier; the scanner proposes Axis B and C from machine-derivable signals, the skill assigns Axis A, confirms B/C, and derives the overall.
- **Never** re-derive or invent audiences; consume the `audience-identification` artifact, and hard-block on nothing — warn, recommend `audience-identify`, and proceed with the mapping as a recorded open item.
- **Never** turn a coverage band into a merge gate; the bands are advisory grading signals (coverage-as-a-guide), and mutation score is reported as the stronger signal where available.
- **Always** write the graded matrix to `project/maturity/<slug>.md` in the contract shape, one block per capability with all three axis tiers, the overall tier, the improvement lever, and a per-axis rationale.
- When `spec/project/capability-maturity-assessment/` and this skill disagree, the spec wins; this skill needs the update.

## Why this is a skill, not an agent

This skill follows the hybrid pattern: the read-only detection phase is delegated to the `capability-maturity-scanner` agent (context isolation, tool restriction), while the top-down inventory, the audience mapping, the Axis A judgement, the confirmation of the B/C proposals, the weakest-link derivation, and the write stay in the skill.

- **Mid-flow interactivity is the contract**: inventorying capabilities top-down, mapping each to an audience, and judging completeness against acceptance criteria are per-turn judgement dialogues with the operator; an agent's fire-and-forget contract would lose them.
- **Persistent on-disk artifact**: the deliverable is `project/maturity/<slug>.md`, a checked-in matrix read by downstream planning; skills own persistent state.
- **Counter-dimension**: the signal-mining half (run static analysis, read coverage/mutation reports, walk the source tree per capability) is self-contained and verbose — the context-window pressure that favours an agent. That pull is honoured, but only for the machine-derivable scan, delegated to `capability-maturity-scanner`; the judgement axes, the weakest-link tiering, and the persistent artifact keep the orchestrating surface a skill.
