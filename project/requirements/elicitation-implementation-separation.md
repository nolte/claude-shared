# Requirements — Elicitation–implementation separation (working-method spec change)

<!--
Produced via the `requirements-elicit` skill, following
spec/project/requirements-elicitation/.
Do not record a requirement before declaring the bounded context below.
`c_d` is an uncertainty proxy (self-consistency-derived), not a calibrated
probability. A requirement is `confirmed` only after an explicit teach-back.
-->

## Bounded context

- **What is being built:** a **meta-change to the "working-method" specs** (under `spec/project/`)
  that anchors a two-phase way of working which cleanly separates **requirements elicitation
  (*Bearbeitung*)** from **implementation (*Umsetzung*)** — including the concrete flow:
  a dedicated working copy for elicitation only → a PR that lands only the requirements document
  into the default branch → a tracking issue (with a reference to the document) in the
  implementation-owning repo → implementation by specialists (who assess the necessary changes
  and keep the affected docs current).
- **Nature of the rule (load-bearing):** the separation is an **optional, named working mode**, not
  a mandatory gate. A contributor MAY choose it when they want to split elicitation from
  implementation. **When** the mode is chosen, the four-step flow is the prescribed sequence within
  the mode. The spec says "*this* is how you separate cleanly", not "you *must* always separate".
- **For whom:** everyone working under the portfolio's working-method — the elicitor, the PR
  reviewer, and the implementing specialists — across all adopting repos.
- **Deliverable of *this* working copy:** **only** the requirements document
  (`project/requirements/elicitation-implementation-separation.md`), landed via PR to `develop`,
  followed by a tracking issue that references it. **Not** in this working copy: the spec authoring
  / the implementation itself (that is step 4 — later, tracking-issue-driven work by specialists).
- **Explicitly out of scope / deliberately deferred:** the spec change's **placement** — a new
  standalone spec (e.g. `spec/project/elicitation-implementation-separation/`) versus an
  amendment / cross-reference inside existing working-method specs — is only **named and framed**
  here; it is **resolved during implementation**, not in this working copy.

## Understanding KPI

- Thresholds: `τ_low = 0.4`, `τ_high = 0.8`, self-consistency `k = 2`, question budget = `~6`
  (spec defaults; unchanged).
- `U_gate = min_d c_d` over required dimensions = **0.80**. The plan
  (`.resume/work-impl-separation/plan.md`) had already framed the bounded context and the six
  load-bearing open questions; the interview resolved scope (portfolio-wide), the optional-mode
  character (a reframe from the plan's MUST/SHOULD framing — confirmed by teach-back "ja das passt"),
  the tracking-issue target and minimal contract (sign-off + teach-back "passt"), and the
  doc-currency acceptance criterion (sign-off), and confirmed the two delimitations (placement
  deliberately deferred; complementary to `issue-orchestration`) by teach-back "ja".
- Termination: **saturation.** The four load-bearing decisions are settled; the placement decision
  is deliberately framed-and-deferred to implementation, and the narrow residuals below carry no
  positive-EVPI operator question.

### Gap matrix

| Dimension | Applicable | `c_d` | Uncertainty source | Evidence event |
|---|---|---|---|---|
| `functional` | yes | 0.86 | interpretation | Optional-mode reframe + four-step flow; teach-back "ja das passt" |
| `non_functional` | yes | 0.83 | interpretation | Portfolio-wide spec, EN-canonical, DRY vs `issue-orchestration` (complementary); teach-back "ja" |
| `constraints` | yes | 0.85 | interpretation | Scope = portfolio-wide (AskUserQuestion); opt-in not MUST; this-WC-only-elicitation; placement deferred |
| `domain_objects` | yes | 0.87 | interpretation | Requirements doc, tracking issue + minimal contract, working copy, two phases, permalink; teach-back "passt" |
| `actors` | yes | 0.84 | interpretation | Elicitor / PR reviewer / implementing specialists distinguished; teach-back |
| `acceptance_criteria` | yes | 0.84 | interpretation | Issue carries permalink + fields; docs updated in same implementation PR, reviewer-checked (AskUserQuestion) |
| `edge_cases` | yes | 0.80 | specification | Opt-in dissolves the trivial-exemption need; "no specialist exists" / "how substantial warrants the mode" left to contributor discretion |
| `scope_boundaries` | yes | 0.86 | interpretation | Placement framed-not-resolved (A) + `issue-orchestration` complementary (B); both teach-back "ja" |

## Requirements

<!-- EARS/CNL form; tagged confirmed/assumed with traceability. -->

### The working mode and its flow

- **R1** — The working-method spec change SHALL establish an **optional, named working mode**
  ("elicitation–implementation separation") — **not** a mandatory gate — that a contributor MAY
  choose when they want to separate requirements elicitation (*Bearbeitung*) from implementation
  (*Umsetzung*).
  - _dimension_: `functional`, `constraints` · _status_: `confirmed` · _source_: teach-back "ja das passt" (optionaler Modus, nicht Zwang)
- **R2** — WHEN the separation mode is chosen, the spec SHALL prescribe a **four-step flow** as the
  binding sequence *within the mode*: (1) requirements elicitation in a dedicated working copy;
  (2) a PR that lands only the requirements document into the default branch; (3) a tracking issue
  referencing the merged document, in the implementation-owning repo; (4) implementation by
  specialists.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: teach-back "wenn man diesen Weg wählt, ist der Ablauf vorgegeben" → "ja das passt"
- **R3** — WHEN the spec is authored, its scope SHALL be **portfolio-wide** — a spec under
  `spec/project/` inherited by adopting repos — describing the mode as a portfolio way of working,
  not a claude-shared-local convention.
  - _dimension_: `constraints`, `scope_boundaries` · _status_: `confirmed` · _source_: AskUserQuestion "Portfolio-weit"

### Step 1 — Elicitation in a dedicated working copy

- **R4** — WHEN the mode is chosen, requirements elicitation SHALL happen in its **own dedicated
  working copy** (worktree) whose **sole deliverable** is the requirements document
  (`project/requirements/<slug>.md`); no implementation occurs in that working copy. (Ties into
  `spec/project/parallel-working-copies/`.)
  - _dimension_: `functional`, `domain_objects` · _status_: `confirmed` · _source_: bounded-context teach-back

### Step 2 — PR of the requirements document

- **R5** — WHEN step 2 runs, a pull request SHALL land **only the requirements document** into the
  default branch (`develop`) **before any implementation begins** — the merged, permalinkable
  document is the hand-off artefact.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: bounded-context teach-back

### Step 3 — Tracking issue with reference

- **R6** — WHEN the tracking issue is created, it SHALL be created in **the repo that owns the
  artefact to be implemented** (the implementation repo) — for this meta-change, `claude-shared`
  itself; generalised: "the repo that owns the artefact to be implemented".
  - _dimension_: `domain_objects`, `scope_boundaries` · _status_: `confirmed` · _source_: AskUserQuestion "Repo der Umsetzung"
- **R7** — WHEN the tracking issue is created, it SHALL carry at minimum: (a) a **commit-stable
  permalink to the merged requirements document** (the load-bearing reference); (b) a short
  **title/description** of the change to implement; (c) a pointer to the **responsible
  specialist(s)** / expected implementation approach; (d) the **charge to keep affected docs
  current** (the bridge to step 4).
  - _dimension_: `domain_objects`, `acceptance_criteria` · _status_: `confirmed` · _source_: teach-back "passt" (Minimalkontrakt)

### Step 4 — Implementation by specialists

- **R8** — WHEN step 4 runs, implementation SHALL be performed by **specialists** (not the elicitor),
  who assess the necessary changes and carry them out.
  - _dimension_: `actors`, `scope_boundaries` · _status_: `confirmed` · _source_: bounded-context teach-back
- **R9** — WHEN specialists implement, they SHALL update **every affected doc/spec in the same PR as
  the implementation**, and the PR reviewer SHALL verify this as part of approval — documentation
  drift is not admitted. (This is the concrete, acceptance-testable meaning of "keep the docs
  current".)
  - _dimension_: `acceptance_criteria` · _status_: `confirmed` · _source_: AskUserQuestion "Doku im selben Umsetzungs-PR"

### Delimitation and deferred decision

- **R10** — WHEN the spec is authored, it SHALL position this mode as **complementary to**
  `spec/project/issue-orchestration/` — which already separates analysis/elicitation from
  implementation *within a single orchestrated run* — by lifting the same separation to a
  **standalone, opt-in cross-working-copy / cross-PR workflow** (elicitation as a separate, merged
  artefact before any implementation) that orchestration MAY build on; it SHALL NOT be framed as a
  competing rule.
  - _dimension_: `scope_boundaries`, `non_functional` · _status_: `confirmed` · _source_: teach-back (B) "ja"
- **R11** — The spec change's **placement** — a new standalone spec (e.g.
  `spec/project/elicitation-implementation-separation/`) versus an amendment / cross-reference
  inside existing working-method specs — SHALL be **named and framed as an open question in this
  document** and **resolved during implementation (step 4)**, NOT decided in this working copy.
  - _dimension_: `scope_boundaries`, `constraints` · _status_: `confirmed` (as deliberately deferred) · _source_: teach-back (A) "ja"

### Process / quality (this working copy)

- **R12** — This working copy SHALL deliver **only** the requirements document; specs are
  EN-canonical; the primary checkout stays on `develop`; all work happens in this worktree
  (`feat/working-method-implementation-separation`). No spec authoring or implementation happens
  here.
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: plan §5 invariants + bounded context

## Surviving assumptions / open risks

**Resolved (settled by operator sign-off + teach-back):**

- ✅ **Character of the rule:** an **optional** working mode, not a mandatory always-separate gate
  (R1) — a reframe from the plan's MUST/SHOULD framing, confirmed by "ja das passt".
- ✅ **Scope:** portfolio-wide spec under `spec/project/` (R3).
- ✅ **Tracking-issue target + minimal contract:** implementation-owning repo (R6), carrying the
  permalink + fields (R7).
- ✅ **Doc-currency acceptance criterion:** affected docs updated in the same implementation PR,
  reviewer-verified (R9).
- ✅ **Delimitation to `issue-orchestration`:** complementary, not competing (R10).

**Deliberately deferred to implementation (framed here, NOT a gap in this artefact):**

- **Placement of the spec change** — new standalone spec vs amendment of existing working-method
  specs (R11). This is the one structural decision this working copy intentionally does not make;
  the implementation step resolves it.

**Remaining residual risk (narrow; carries no positive-EVPI operator question now, routed to the implementation step):**

- **"No specialist exists" for a given implementation** — the flow assumes a suitable specialist is
  available for step 4; the fallback (self-implementation, or routing back) is left to the
  implementation-step authoring.
- **What counts as "substantial enough" to warrant the mode** — because the mode is opt-in, no
  trivial-change exemption is needed; the threshold for choosing it is left to contributor
  discretion. Worth an explicit sentence in the authored spec, not an operator decision here.
- **Exact tracking-issue mechanics** — whether a fixed issue template / labels back the R7 minimal
  contract is left to the implementation step (the operator confirmed the field set, not a template).

**Constraint reminders (confirmed, not risks):** portfolio-wide; opt-in (never a forced gate);
EN-canonical specs; this working copy delivers only the requirements document; primary checkout stays
on `develop` (all work in this worktree); placement decision deliberately deferred to implementation.
