# Requirements — Provider-side frontend testability / stable-identifier spec

<!--
Produced via the `requirements-elicit` skill, following
spec/project/requirements-elicitation/.
Do not record a requirement before declaring the bounded context below.
`c_d` is an uncertainty proxy (self-consistency-derived), not a calibrated
probability. A requirement is `confirmed` only after an explicit teach-back.
-->

## Bounded context

- **What is being built:** a new **portfolio spec** `spec/frontend/testability-identifiers/`
  (EN canonical + DE translation) that norms the **provider side** of E2E testability — the
  contract obliging a frontend to *provide* stable, unique identifiers on all test-relevant
  elements and pages. It is the missing complement to `spec/project/e2e-test-automation/`, which
  norms only the **consumer side** (how tests *select*) and explicitly scopes provisioning out.
- **Shape (load-bearing):** mirrors the e2e spec — a **framework-neutral normative core** plus a
  clearly delimited **"Web reference profile"** carrying the concrete `data-testid`/DOM rules; no
  web specific rule leaks into the core. Non-web framework profiles (Flutter, native) are deferred
  until a consumer forces them, exactly as e2e defers non-Selenium profiles.
- **Content template:** kamerplanter PR #581 / `UI-NFR-022` (R-001..R-025), de-domained
  (`species-*` → `<entity>-*`); no plant/domain leakage.
- **For whom:** audience `nolte-engineering` (code-bearing repos). Addressed providers are frontend
  implementers **and** the UX/usability role (the `frontend-usability-optimizer` agent; secondarily
  the UX domain of the `webview-ui-expert` review). The `/spec` skill authors it; e2e-test-automation
  consumers benefit indirectly via cross-reference.
- **Explicitly out of scope:**
  - the **selection/consumer side** — owned by `e2e-test-automation` §Locator strategy;
  - **non-web framework profiles** — deferred until a consumer forces them;
  - the **component-tier philosophy** (user-facing-query-first) — intentionally different, noted as
    a delimitation, not a contradiction;
  - **naming a concrete linter/enforcement tool** — enforcement is a non-binding MAY only (OQ2).

## Understanding KPI

- Thresholds: `τ_low = 0.4`, `τ_high = 0.8`, self-consistency `k = 2`, question budget = `~6`
  (spec defaults; unchanged).
- `U_gate = min_d c_d` over required dimensions = **0.82**. The foundational plan
  (`.resume/frontend-testability-spec/plan.md`) had already researched and framed the bounded
  context, the 7 rule groups, and the three load-bearing open questions (OQ1–OQ3). The interview
  confirmed the bounded context by teach-back ("ja passt"), resolved OQ1–OQ3 by AskUserQuestion
  (slug `testability-identifiers`; enforcement = non-binding MAY, no linter; e2e §37 forward
  pointer added), confirmed the acceptance-criteria + edge-case completeness contract by teach-back
  ("ja das passt"), and captured one new operator requirement — the UX role as a bound actor with
  identifier-preservation on usability edits — confirmed by teach-back ("das passt").
- Termination: **saturation.** The three framing decisions are settled, the completeness contract
  and negative-scenario list are teach-back-confirmed, and the residuals below carry no
  positive-EVPI operator question (they are authoring choices routed to the `/spec` step).

### Gap matrix

| Dimension | Applicable | `c_d` | Uncertainty source | Evidence event |
|---|---|---|---|---|
| `functional` | yes | 0.85 | interpretation | 7 rule groups (plan §3) + AC1–AC3 teach-back "ja das passt" |
| `non_functional` | yes | 0.85 | interpretation | Neutral core + delimited Web profile, EN+DE sync, Vale, MAY enforcement; OQ2 + teach-back |
| `constraints` | yes | 0.85 | interpretation | Plan §5 invariants + de-domaining + distribution-contract; OQ decisions |
| `domain_objects` | yes | 0.85 | interpretation | Page markers, `form-field-<name>`, business-key lists, naming schema; AC3 teach-back |
| `actors` | yes | 0.85 | authoritative | Frontend implementers + UX role (`frontend-usability-optimizer`); operator "der UX Experte sollte das auch beachten" |
| `acceptance_criteria` | yes | 0.85 | interpretation | AC1–AC7 reflected and confirmed by teach-back "ja das passt" |
| `edge_cases` | yes | 0.82 | interpretation | Business-key lists, state changes, non-deterministic IDs, a11y overlap; teach-back "ja das passt" |
| `scope_boundaries` | yes | 0.85 | specification→resolved | OQ1–OQ3 (AskUserQuestion) + four explicit out-of-scope lines; bounded-context teach-back |

## Requirements

<!-- EARS/CNL form; tagged confirmed/assumed with traceability. -->

### The spec's shape and scope

- **R1** — The spec SHALL define a **framework-neutral normative core** expressing the provider
  obligation — provide stable, unique identifiers on all test-relevant elements and pages — with no
  web/React specifics in the core.
  - _dimension_: `functional`, `non_functional` · _status_: `confirmed` · _source_: AC1 teach-back "ja das passt"
- **R2** — The spec SHALL carry a delimited **"Web reference profile"** section holding the concrete
  `data-testid`/DOM rules; no web-specific rule SHALL leak into the neutral core, and non-web
  framework profiles SHALL be deferred until a consumer forces them.
  - _dimension_: `non_functional`, `scope_boundaries` · _status_: `confirmed` · _source_: AC2 + bounded-context teach-back
- **R3** — WHEN authored, the topic SHALL live at **`spec/frontend/testability-identifiers/`**
  (EN canonical + DE), alongside `spec/frontend/webview-ui-optimization/`.
  - _dimension_: `constraints`, `scope_boundaries` · _status_: `confirmed` · _source_: OQ1 (AskUserQuestion) = `testability-identifiers`

### Normative core — the 7 rule groups (de-domained from UI-NFR-022)

- **R4** — The core SHALL state the **grundprinzip and the provisioning-vs-selection split**
  (R-001..004): the frontend *provides* identifiers, tests *select* by them; and it SHALL cross-reference
  `e2e-test-automation` §Locator strategy as the consumer sibling.
  - _dimension_: `functional`, `scope_boundaries` · _status_: `confirmed` · _source_: AC3/AC4 teach-back
- **R5** — The core SHALL require **page-level markers** `<entity>-<view>-page` and a shared
  `loading-skeleton` marker for the loading state (R-005..008).
  - _dimension_: `functional`, `domain_objects` · _status_: `confirmed` · _source_: AC3 teach-back
- **R6** — The core SHALL require **element-level provisioning** on interactive elements, form fields
  (`form-field-<name>`), dialogs, and test-relevant status/result displays (R-009..013).
  - _dimension_: `functional`, `domain_objects` · _status_: `confirmed` · _source_: AC3 teach-back
- **R7** — WHEN an element is a repeated **list/table** row, it SHALL be addressable by a stable
  **business key**, never by index/position (R-014..016).
  - _dimension_: `functional`, `edge_cases` · _status_: `confirmed` · _source_: AC3 + edge-case teach-back
- **R8** — The core SHALL fix a **naming schema**: kebab-case, English (R-017..020).
  - _dimension_: `domain_objects`, `constraints` · _status_: `confirmed` · _source_: AC3 teach-back
- **R9** — The core SHALL establish **stability-as-contract**: identifiers are deterministic, stable
  across element states, and MUST NOT be silently renamed or removed (R-021..023). Framework
  auto-generated or hashed identifiers do NOT satisfy the contract (non-deterministic / non-speaking).
  - _dimension_: `functional`, `edge_cases` · _status_: `confirmed` · _source_: AC3 + negative-scenario teach-back
- **R10** — The core SHALL position accessibility hooks (`role`/`aria-label`) as a **secondary**
  anchor that complements but never replaces the primary test hook (R-024..025).
  - _dimension_: `functional`, `edge_cases` · _status_: `confirmed` · _source_: AC3 + edge-case teach-back

### Cross-references and delimitations

- **R11** — WHEN the spec is authored, `e2e-test-automation` §37 (the provisioning scope-out line)
  SHALL receive a **one-line forward pointer** to this spec (symmetric with the consumer/provider
  split PR #581 established downstream). The new spec references e2e; e2e references back one line.
  - _dimension_: `scope_boundaries`, `non_functional` · _status_: `confirmed` · _source_: OQ3 (AskUserQuestion) = forward pointer
- **R12** — The spec SHALL note the **component-tier delimitation**: E2E provisioning (this spec,
  test-hook-first) differs *by design* from component tests (`test-tier-component`, user-facing-query
  first) — an intentional difference, not a contradiction.
  - _dimension_: `scope_boundaries` · _status_: `confirmed` · _source_: AC6 teach-back
- **R13** — The spec SHALL mention an **optional enforcement hook** (a lint/review rule à la
  UI-NFR-022 DoD "a new interactive component ships a `data-testid`") as a **non-binding MAY**, without
  naming a concrete linter.
  - _dimension_: `non_functional`, `constraints` · _status_: `confirmed` · _source_: OQ2 (AskUserQuestion) = MAY, no tool

### UX role as bound actor

- **R14** — The spec SHALL bind the **UX/usability role** as an addressed provider (concretely the
  `frontend-usability-optimizer` agent; secondarily the UX domain of the `webview-ui-expert` review),
  and SHALL require that WHEN this role reshapes an existing element (form, dialog, list/table, detail
  page, or its loading/error/empty states), the frontend **preserves** the element's stable identifier —
  a usability edit MUST NOT silently rename or drop a provided identifier (a special case of R9).
  - _dimension_: `actors`, `edge_cases` · _status_: `confirmed` · _source_: operator "der UX Experte sollte dieses Regelwerk auch beachten" + teach-back "das passt"

### Process / quality (this authoring effort)

- **R15** — The spec SHALL be **EN-canonical** with a strictly synchronized DE translation, SHALL be
  **Vale-clean** (spaced em-dashes; contractions resolved in the EN file), and the `spec/README.md`
  index SHALL be regenerated after authoring.
  - _dimension_: `non_functional`, `constraints` · _status_: `confirmed` · _source_: plan §5/§7 invariants
- **R16** — The spec content SHALL be **de-domained** — kamerplanter's `species-*` examples
  genericised to `<entity>-*`; no plant/domain leakage; the audience note (nolte-engineering / code
  repos) is descriptive, not a plugin copy (distribution-contract discipline).
  - _dimension_: `constraints`, `scope_boundaries` · _status_: `confirmed` · _source_: plan §5 invariants

## Surviving assumptions / open risks

**Resolved (settled by operator sign-off + teach-back):**

- ✅ **Topic slug:** `spec/frontend/testability-identifiers/` (R3, OQ1).
- ✅ **Enforcement altitude:** non-binding MAY, no linter named (R13, OQ2).
- ✅ **Cross-ref direction:** forward pointer added to e2e §37 (R11, OQ3).
- ✅ **Completeness contract:** AC1–AC7 + negative-scenario list teach-back-confirmed (R1–R10, R12).
- ✅ **UX role bound:** identifier preservation on usability edits (R14).

**Assumed (not `confirmed` — surfaced for later confirmation):**

- **A1 — Agent wiring is a separate follow-up.** Adding a reference to this spec into the
  `frontend-usability-optimizer` `description`/`use_when` (and the `webview-ui-expert` UX domain) is an
  **optional follow-up**, explicitly *not* part of this spec-authoring scope (operator confirmed the
  spec declares the binding; the wiring is deferred). If later wanted, it becomes a distinct PR.
- **A2 — Special mounting contexts covered by the general rule.** Iframes / shadow-DOM /
  portals / toasts / overlays were offered as candidate edge cases; the operator confirmed the list as
  sufficient without adding them, so they are treated as **covered by the general element-provisioning
  rule (R6)** — any test-relevant element is in scope regardless of mounting context. The authored spec
  SHOULD state this generality in one sentence rather than enumerate contexts.

**Residual authoring choices (no positive-EVPI operator question now; routed to the `/spec` step):**

- Exact section ordering and heading names inside the core vs. the Web reference profile.
- Whether the deferred non-web profiles get a named placeholder section or a single deferral sentence.
- The precise wording of the optional-enforcement MAY (R13) so it reads as guidance, not a mandate.

**Constraint reminders (confirmed, not risks):** framework-neutral core with a delimited Web profile;
EN-canonical + DE-synced, Vale-clean; de-domained (no plant leakage); portfolio spec shipped with no
plugin; primary checkout stays on `develop`, all work in this worktree.
