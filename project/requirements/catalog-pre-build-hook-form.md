# Requirements — Catalog `on_pre_build` hook form (DRY multi-surface generator)

<!--
Produced via the `requirements-elicit` skill, following
spec/project/requirements-elicitation/.
`c_d` is an uncertainty proxy (self-consistency-derived), not a calibrated
probability. A requirement is `confirmed` only after an explicit teach-back.
-->

## Bounded context

- **What is being built:** A revision of the `skill-agent-catalog` spec
  (`spec/claude/skill-agent-catalog/en.md` canonical + `de.md` translation) that documents the MkDocs
  **`on_pre_build` hook** form of the catalog generator as a first-class (or preferred) **third invocation
  surface**, alongside the existing two forms — the `mkdocs-gen-files` plugin script and the standalone
  Taskfile pre-build step. **Plus** (scope expanded at elicitation — see Q4) the **in-repo migration** of this
  repository's own generator and docs wiring to that hook form as dogfooding.
- **For whom:** catalog-generator implementors (`scripts/docs/gen_catalog.py`),
  `skill-agent-catalog-apply` skill authors (consumer-side wiring), spec readers, and — for the in-repo
  migration — this repository's MkDocs deploy pipeline.
- **Load-bearing architecture grounding (DRY):** ONE generator module with a single rendering core, exposed
  through up to three *invocation surfaces*; never three forked generators or duplicated per-form MUST-lists.
  Proven by the reference impl `gen_catalog.py` in nolte/claude-home-assistant#6, where `on_pre_build()` and
  the `__main__` block both call the same render function.
- **Explicitly out of scope:** redefining the catalog entry schema or the on-disk skill/agent shape (owned by
  `skill-management` / `agent-management`); other plugins' generators; MkDocs theme/typography. The change is
  **additive** — the two existing forms stay valid; it is not a fork.

## Understanding KPI

- Thresholds: `τ_low = 0.4`, `τ_high = 0.8`, self-consistency `k = 2`, question budget = `~6` (spec defaults;
  unchanged).
- `U_gate = min_d c_d` over required dimensions = **0.80** (after deep-research + Q1–Q3 operator sign-off
  raised `edge_cases` 0.55→0.80 and `acceptance_criteria` 0.70→0.85). Was 0.55 at interview close.
- Termination: **saturation reached after the research gate.** The two formerly below-`τ_high` dimensions were
  *specification uncertainty* the operator routed to the deep-research step; the Workflow run
  (`research-findings.md`, both load-bearing claims CONFIRMED) plus the Q1–Q3 operator sign-off settled them.
  Only implementation-time verifications remain (this repo's actual `--strict` build; deploy checkout of source
  roots for R9) — narrow, named residual risks, not open design questions.

### Gap matrix

| Dimension | Applicable | `c_d` | Uncertainty source | Evidence event |
|---|---|---|---|---|
| `functional` | yes | 0.90 | interpretation | Teach-back confirmed ("Ja, exakt so") + plan §1/§3 |
| `non_functional` | yes | 0.85 | interpretation | DRY teach-back confirmed; plan §3/§5 invariants |
| `constraints` | yes | 0.85 | interpretation | Spec house rules + plan §5; `.spec-config.yml` (EN canonical) |
| `domain_objects` | yes | 0.90 | interpretation | Verified on disk (gen_catalog.py, mkdocs.yml, Taskfile.yml, committed catalog tree) |
| `actors` | yes | 0.85 | interpretation | spec §Readers (L8); in-repo wiring inspection |
| `acceptance_criteria` | yes | 0.85 | specification | Research + Q1–Q3 sign-off settled normative shape; only impl-time verification remains |
| `edge_cases` | yes | 0.80 | specification | research-findings.md: ordering + deploy-firing CONFIRMED; SQ2/SQ4 gaps noted, non-blocking |
| `scope_boundaries` | yes | 0.80 | interpretation | Q4 teach-back: operator chose **Spec + in-repo migration** |

## Requirements

<!-- EARS/CNL form; tagged confirmed/assumed with traceability. -->

### Spec revision (EN canonical + DE in sync)

- **R1** — WHEN the `skill-agent-catalog` spec describes the catalog generator's invocation surfaces, it SHALL
  present them as ONE DRY generator core exposed through up to three surfaces (`mkdocs-gen-files` script;
  standalone Taskfile/`__main__` pre-build step; `on_pre_build` hook registered via `hooks:`), never as forked
  per-form generators or duplicated per-form MUST-lists.
  - _dimension_: `functional`, `non_functional` · _status_: `confirmed` · _source_: teach-back "Ja, exakt so" + plan §3
- **R2** — WHEN the spec enumerates generator forms at L114 (§Generation mechanism) and L117 (the central
  `MAY`), it SHALL list the `on_pre_build` hook as a first-class invocation surface so it is not accidentally
  non-conformant.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: plan §2 (L114/L117) + teach-back
- **R3** — WHEN the spec sets the normative strength of the hook form, it SHALL name the hook form the
  **recommended default for repos on `mkdocs-static-i18n` folder mode**, with the standalone Taskfile pre-build
  step kept **equally-valid and explicitly supported**; the change stays additive (all existing forms valid).
  - _dimension_: `functional` · _status_: `confirmed` (Q1 resolved: "Bevorzugt bei static-i18n folder", research-backed) · _source_: Q1 sign-off + research-findings.md
- **R4** — WHEN the spec states the `task docs` regeneration `MUST` (L119–L120), it SHALL be reframed to a
  goal-level output-identity invariant ("the catalog MUST regenerate automatically as part of the normal docs
  build with no separate manual step, such that local and CI output are identical") with THREE conformant
  realizations (hook / Taskfile dependency / gen-files), so the hook form is conformant without a `task docs`
  dependency.
  - _dimension_: `functional` · _status_: `confirmed` (Q2 resolved: "Goal-Level-Invariante + 3 Realisierungen") · _source_: Q2 sign-off + research-findings.md
- **R5** — WHEN the spec documents the committed-catalog freshness-gate fallback (L115) and the conformance
  checklist (L178/L181), it SHALL note the hook form as the way to exit the committed-catalog fallback and add
  the hook as a first-class branch in both checklist items, while keeping the fallback documented for repos
  still on `mkdocs-gen-files`.
  - _dimension_: `functional` · _status_: `confirmed` (Q3 resolved: "Ja, bedingt") · _source_: Q3 sign-off + research-findings.md
- **R6** — WHEN the canonical `en.md` is revised, the `de.md` translation SHALL be brought into strict sync via
  the `/nolte-shared:spec` translation path, with the spec parity/drift check passing (EN is canonical per
  `.spec-config.yml`).
  - _dimension_: `constraints`, `non_functional` · _status_: `confirmed` · _source_: plan §5 invariants

### In-repo migration (dogfooding — scope expanded via Q4)

- **R7** — WHEN this repository's catalog generator (`scripts/docs/gen_catalog.py`) is migrated, it SHALL gain
  an `on_pre_build(config, **kwargs)` entry point that calls the SAME physical-file-writing render core as the
  existing `main()`/`__main__` path (no forked generator), and the hook SHALL be registered via `hooks:` in
  `mkdocs.yml`.
  - _dimension_: `functional`, `non_functional` · _status_: `confirmed` · _source_: Q4 "Spec + In-Repo-Migration" + disk inspection
- **R8** — WHEN the hook form is wired in this repo, a `mkdocs build --strict` SHALL produce both the `docs/en/`
  and `docs/de/` catalog trees with every skill/agent entry present and the language switcher intact (parity
  with the reference impl claude-home-assistant#6), given this repo runs `mkdocs-static-i18n` with
  `docs_structure: folder`.
  - _dimension_: `acceptance_criteria`, `edge_cases` · _status_: `assumed` (ordering vs. static-i18n gated on research) · _source_: disk (mkdocs.yml L62) + plan §2
- **R9** — WHEN the hook form is confirmed (by research) to fire inside the actual gh-pages deploy build
  (`mkdocs-deploy-gh-pages` running bare `mkdocs build`), this repo SHALL retire the committed-catalog tree,
  the CI freshness gate (`ci.yml`), and the `docs-catalog-fresh` pre-commit hook, since the hook regenerates
  the catalog on every build including the deploy. IF research cannot confirm the hook fires in that deploy,
  the committed-catalog fallback SHALL be kept and R9 reduced to "add the hook alongside."
  - _dimension_: `scope_boundaries`, `edge_cases` · _status_: `assumed` (retire-decision gated on Q3 + deploy verification) · _source_: disk (ci.yml comment, committed tree) + Q3

### Process / quality

- **R10** — WHEN the change is prepared for review, `task test` (`validate_skills.py`) SHALL be green,
  `spec-readiness-reviewer` SHALL report no contradictions or ghost references, and the changed prose SHALL be
  Vale/lektorat clean; the PR SHALL autolink the touched spec and close nolte/claude-shared#337.
  - _dimension_: `acceptance_criteria` · _status_: `confirmed` · _source_: plan §6 steps 6–7

## Surviving assumptions / open risks

**Resolved (was gated; now settled by deep-research + Q1–Q3 operator sign-off):**

- ✅ **Q1 (normative strength, R3):** RESOLVED → hook form is the recommended default for `static-i18n` folder
  mode; Taskfile form equally-valid. (Ordering CONFIRMED.)
- ✅ **Q2 (`task docs` MUST reframing, R4):** RESOLVED → goal-level output-identity invariant + three
  conformant realizations.
- ✅ **Q3 (committed-catalog fallback exit, R5/R9):** RESOLVED → hook fires in `mkdocs gh-deploy` (deploy
  verdict CONFIRMED); spec documents the fallback-exit, in-repo retires the gate conditionally.
- ✅ **Hook ordering vs. `mkdocs-static-i18n folder` (R8):** CONFIRMED — `get_files()` runs after
  `on_pre_build`, so physical `docs/<lang>/` files are collected and localized (#263 distinguishes them from
  dropped gen-files virtual files).

**Remaining residual risks (implementation-time, narrow):**

- **R8 `--strict` / serve-loop (impl):** SQ4 sub-agent failed; writing into `docs_dir` during `on_pre_build`
  can trip `mkdocs serve` rebuild loops / `--strict`. Mirror the verified claude-home-assistant#6 pattern;
  make the generator idempotent (rewrite only on change) and verify `mkdocs build --strict` is green on both
  trees during the migration.
- **R9 deploy checkout (impl):** before deleting this repo's committed catalog + freshness gate, verify the
  `mkdocs-deploy-gh-pages` deploy checks out the full repo so the generator's source roots (`skills/`,
  `agents/`, `plugins/*/`, `docs/catalog-sources.yml`) are present and importable.
- **Constraint reminders (confirmed, not risks):** EN canonical; primary checkout stays on `develop` (all work
  in this worktree); additive not a fork; generated config files in English.
