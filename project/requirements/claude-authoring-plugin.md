# Requirements — Fourth optional plugin carving the Claude authoring slice out of `nolte-shared` (re-opens F-18)

<!--
Produced via the `requirements-elicit` skill, following
spec/project/requirements-elicitation/.
Do not record a requirement before declaring the bounded context below.
`c_d` is an uncertainty proxy (self-consistency-derived), not a calibrated
probability. A requirement is `confirmed` only after an explicit teach-back.
-->

## Bounded context

- **What:** Extract the Claude skill/agent **authoring slice** (plus its
  documentation-generation capability) out of `nolte-shared` into a new,
  **fourth optional plugin** named **`nolte-claude-dev`**, structured like
  `plugins/nolte-media/` (own `.claude-plugin/plugin.json`, `skills/`, `agents/`),
  versioned in lockstep, listed as the fourth entry in the root
  `.claude-plugin/marketplace.json`. This **re-opens and flips decision F-18**
  (the F-18 carve-out decision (retired to git history),
  verdict `keep-and-watch`).
- **For whom:** every downstream repository that installs the `claude-shared`
  marketplace. The split's beneficiary is the **majority of consumers who never
  author a skill/agent** (docs / content / config repos) — they stop loading the
  authoring slice's skill-list weight. Secondary actor: plugin/skill authors, who
  now adopt `nolte-claude-dev` on top of `nolte-shared`.
- **Split justification (the load-bearing gate):** **consumer-audience**, per
  `spec/claude/plugin-scoping/` — never topic/specialisation/count. The operator
  decided (2026-07-22) that the **standing ~10.4 % skill-list overhead** every
  non-authoring consumer carries is worth the fourth-plugin cost, reversing F-18's
  "not worth it yet" judgment. Anticipated growth of the authoring slice is a
  documented **amplifier**, not the load-bearing reason.
- **Explicitly out of scope:** (1) the `spec/claude/` corpus does **not** move —
  it is repo-wide and shipped with no plugin; (2) the `cookiecutter-template-*`
  adjacency pair stays in `nolte-shared` (F-18 "adjacency, not core"); (3) no
  net-new documentation capability is built — the "documentation" goal is served
  by the existing `skill-agent-catalog-apply` moving with the slice; (4) no change
  to the `nolte-media` / `nolte-engineering` boundaries; (5) no edit to any
  consumer's local `.claude/`.

## Understanding KPI

- Thresholds: `τ_low = 0.4`, `τ_high = 0.8`, self-consistency `k = 2`, question budget = `7` (spec defaults; unchanged)
- `U_gate = min_d c_d` over required dimensions = **0.8**
- Termination: `saturation` — every required dimension ≥ `τ_high` after the load-bearing gate (F-18 trigger + split justification) was resolved by an authoritative operator decision and the two design questions (capability set, name) were answered. No positive-EVPI question remained; residual items are downstream implementation details (exact reference-update surface, `release-automation.yml` transform wiring) resolved during the work itself.

### Gap matrix

| Dimension | Applicable | `c_d` | Uncertainty source | Evidence event |
|---|---|---|---|---|
| `functional` | yes | 0.9 | specification | Operator answer "Core-Slice: 6 Artefakte" (2026-07-22) — the F-18-defined 5 skills + agent `claude-plugin-developer`; documentation = existing `skill-agent-catalog-apply` |
| `non_functional` | yes | 0.85 | interpretation | Plan §5 invariants + CLAUDE.md: lockstep versioning, routing correctness preserved, ~10.4 % skill-list weight removed for non-authoring consumers |
| `constraints` | yes | 0.9 | interpretation | **GATE** — teach-back confirmed (2026-07-22): split is consumer-audience, NOT topic; `spec/claude/` stays; `git mv` not copy; EN-canonical config; lockstep bump. Live measurement (2026-07-22) grounded the decision |
| `domain_objects` | yes | 0.95 | interpretation | Plan §2 + measured inventory (2026-07-22): the 6 slice artefacts, `plugin.json`, `marketplace.json`, `release-automation.yml`, `docs/catalog-sources.yml`, `CLAUDE.md`; name `nolte-claude-dev` fixed |
| `actors` | yes | 0.9 | interpretation | Non-authoring consumers (beneficiary), plugin/skill authors (adopt new plugin), Claude Code skill-list router |
| `acceptance_criteria` | yes | 0.8 | specification | Plan §4 work-steps refined by the confirmed decisions; teach-back on the split justification (2026-07-22) |
| `edge_cases` | yes | 0.8 | interpretation | F-18's own counter-points now operator-accepted: ad-hoc `skill-review`/`agent-review` becomes an install decision; namespaced-reference breakage; permanent manual lockstep-bump surface |
| `scope_boundaries` | yes | 0.9 | specification | Operator answers: core-6 only, cookiecutter stays, no net-new capability; `spec/claude/` does not move (2026-07-22) |

## Requirements

- **R1 — Re-open F-18 with measured evidence.** WHEN this work begins, the
  deliverable SHALL include a decision-revision artifact under
  `.audits/shared-plugin-analysis/` that measures the current authoring slice
  against the F-18 baseline (10.4 %) and records the flip `keep → split` together
  with the trigger that fired.
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: Plan §4 step 2 + operator gate decision (2026-07-22)

- **R2 — The fired trigger is consumer-audience overhead, operator-decided.** The
  re-open SHALL be justified by a **consumer-audience** distribution-contract
  difference per `spec/claude/plugin-scoping/` — specifically the operator's
  decision that the **standing ~10.4 % skill-list overhead** borne by every
  non-authoring consumer is worth the fourth-plugin cost — and SHALL NOT be
  justified by topic, specialisation, coherence, or count.
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: Operator: "Schon der heutige Overhead reicht" + "Es ist mit einer erweiterung der Claude Plugins spezifischen skills zu rechnen was einen overhead bei anderen projekten erzeugen würde" (2026-07-22); teach-back confirmed

- **R3 — Amend F-18's revision triggers.** The revision artifact SHALL amend
  F-18's trigger list to record this new trigger (operator judges the standing
  non-authoring-consumer overhead worth the fourth-plugin cost), so the decision
  history stays honest that neither original trigger — (a) a skill-list budget
  warning, (b) measured slice growth past ~10 % — was the basis.
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: Operator "Neuer/dritter Grund" (2026-07-22) + live measurement showing trigger (b) not fired (10.43 % ≈ 10.4 %)

- **R4 — Exact capability set to migrate.** The new plugin SHALL contain exactly
  the **core slice of 6 artefacts**: skills `skill-management`, `skill-review`,
  `agent-review`, `skills-agents-sweep`, `skill-agent-catalog-apply`, and agent
  `claude-plugin-developer`. The `cookiecutter-template-*` pair SHALL remain in
  `nolte-shared`.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: Operator "Core-Slice: 6 Artefakte (Recommended)" (2026-07-22)

- **R5 — "Documentation" = existing catalog generation.** The "documentation of
  skills/agents" goal SHALL be satisfied by migrating the existing
  `skill-agent-catalog-apply` capability with the slice; NO net-new
  documentation-authoring capability SHALL be built in this scope.
  - _dimension_: `scope_boundaries` · _status_: `confirmed` · _source_: Operator declined "Core + net-new Doc-Capability"; chose core-6 (2026-07-22)

- **R6 — Plugin name.** The new plugin SHALL be named **`nolte-claude-dev`**.
  - _dimension_: `domain_objects` · _status_: `confirmed` · _source_: Operator answer "nolte-claude-dev" (2026-07-22)

- **R7 — Migrate, never duplicate.** WHEN the slice is moved, each skill/agent
  SHALL be `git mv`'d from `nolte-shared` into `plugins/nolte-claude-dev/`
  (never copied), and every namespaced reference (`/nolte-shared:skill-management`
  → `/nolte-claude-dev:skill-management`, etc.) across `spec/`, `docs/`, and
  cross-skill mentions SHALL be updated.
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: CLAUDE.md §Authoring rules ("Never copy plugin-owned skills") + Plan §4 step 4

- **R8 — `spec/claude/` stays repo-wide.** The `spec/claude/` corpus SHALL NOT
  move into the new plugin; it remains repo-wide and shipped with no plugin.
  - _dimension_: `scope_boundaries` · _status_: `confirmed` · _source_: Plan §2 + §5 invariant; teach-back on scope (2026-07-22)

- **R9 — Repo wiring for a fourth plugin.** The deliverable SHALL add the fourth
  `plugins[]` entry to `.claude-plugin/marketplace.json`; declare the new
  `plugin.json` `version` as a version-bearing file in
  `.github/release-automation.yml`; register the subtree in
  `docs/catalog-sources.yml`; update `CLAUDE.md` (roster, split justification,
  lockstep paragraph, dogfooding `--plugin-dir ./plugins/nolte-claude-dev`); and
  confirm `scripts/validate_skills.py` auto-discovers the plugin.
  - _dimension_: `domain_objects` · _status_: `confirmed` · _source_: Plan §2 "Repo-wide wiring" + §4 step 5

- **R10 — Lockstep versioning preserved.** The new plugin's `plugin.json`
  `version` SHALL equal the repository release tag and be aligned by the
  `chore(release)` bump; the added manual-bump surface is an accepted, recorded
  cost of this flip.
  - _dimension_: `non_functional` · _status_: `confirmed` · _source_: CLAUDE.md §What this repo is (lockstep) + Plan §5 invariant

- **R11 — Routing correctness preserved.** WHEN references and namespaces change,
  the migrated skills/agents SHALL remain functionally correct and correctly
  discoverable/routed; the split SHALL NOT degrade Claude Code's ability to select
  the right specialist.
  - _dimension_: `non_functional` · _status_: `confirmed` · _source_: Analogous to R6 of `shared-plugin-restructure.md`; Plan §5

- **R12 — Green gates before PR.** WHEN migration and wiring are complete,
  `task test` (frontmatter), `task lint` (pre-commit), and `task docs` (catalog
  build) SHALL pass before the PR is opened via `/nolte-shared:pull-request-create`.
  - _dimension_: `acceptance_criteria` · _status_: `confirmed` · _source_: Plan §4 steps 6–7

## Surviving assumptions / open risks

- **A1 (assumed) — Growth amplifier, not measured evidence.** The operator's
  expectation of "an expansion of the Claude-plugin-specific skills" is recorded
  as an amplifier of the audience decision, not as measured evidence. F-18's
  "splitting to pre-empt a limit that has not appeared is speculative" caveat
  stays visible: the load-bearing justification is the **present** standing
  overhead (R2), which the operator authoritatively weighed — not the future.
- **A2 (risk) — Namespaced-reference breakage.** Renaming `/nolte-shared:<skill>`
  → `/nolte-claude-dev:<skill>` across `spec/`, `docs/`, cross-skill mentions, and
  any consumer docs risks stragglers. Mitigation: grep the full tree for each
  moved skill/agent name after `git mv`; `task docs` catalog build surfaces
  dangling catalog sources.
- **A3 (risk) — Permanent manual lockstep-bump surface.** F-18's decisive
  against-argument (a fourth plugin adds a per-release manual version-bump step,
  marketplace `plugins[].version` deliberately absent) is now an **accepted**
  standing cost. Mitigation: `.github/release-automation.yml` lists the new
  `plugin.json` version so the pre-publish alignment gate catches drift.
- **A4 (risk) — Ad-hoc review becomes an install decision.** An occasional
  non-authoring consumer that wants a single `skill-review`/`agent-review` must
  now install `nolte-claude-dev`. F-18 raised this against the split; the operator
  accepted it as the intended audience boundary.
- **A5 (open, low-EVPI) — `release-automation.yml` transform.** The exact
  transform/path for the new version-bearing file mirrors the existing plugin
  entries; a downstream implementation detail confirmed against the file's schema
  during the work.
