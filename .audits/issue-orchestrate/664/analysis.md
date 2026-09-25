---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "664"
classification: "bug"
secondary-classes: [spec-change]
route: "direct"
status: approved
created: "2026-09-25"
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #664 — error-tracking-audit-scanner: recognise Sentry 11's `dataCollection` as the PASS form for default-PII off — `sendDefaultPii` no longer exists
- **URL**: <https://github.com/nolte/claude-shared/issues/664>
- **Labels**: spec
- **Linked items**: nolte/kamerplanter#1685, nolte/kamerplanter#1678 (consumer trigger); nolte/claude-shared#660 (same shape: spelling instead of effect). No PR references #664 (`closedByPullRequestsReferences` = 0).
- **Prior art checked**: no open PR; no `project/features/` entry; `grep -rn 'sendDefaultPii\|send_default_pii\|dataCollection'` over the tracked corpus → exactly one site, `plugins/nolte-engineering/agents/error-tracking-audit-scanner.md:134`.
- **Trusted author**: `nolte` (repository owner).

## Classification

- **Primary class**: bug
- **Secondary class(es)**: spec-change
- **Rationale**: the scanner reports a false red (UNSET → Critical) for a component that is measurably stricter than before; the spec text is tightened as secondary work.
- **Asserted cause verified**: confirmed, and extended.
  - `error-tracking-audit-scanner.md:134` accepts only the literals `send_default_pii=False` / `sendDefaultPii: false` as PASS (read at `92d08204`).
  - `SKILL.md:102` escalates UNSET to Critical once the pinned SDK's default is established as PII-on.
  - `@sentry/core@11.0.0` (npm `latest`, packed 2026-09-25): `grep -rl sendDefaultPii build/types` → 0 files (10.75.3: 6 files). `build/types/types/datacollection.d.ts` declares `DataCollection` with `userInfo, cookies, httpHeaders, httpBodies, urlQueryParams, graphQL{document,variables}, genAI{inputs,outputs}, databaseQueryData, queues, stackFrameVariables, frameContextLines`. `CollectBehavior = boolean | {allow} | {deny}`.
  - `build/esm/utils/data-collection/resolveDataCollectionOptions.js`: each category resolves `dc.<cat> ?? DEFAULTS.<cat>`, and `DEFAULTS` is **on for every PII category** (`userInfo: true, cookies: true, httpHeaders {true,true}, httpBodies [all four], urlQueryParams: true, graphQL {true,true}, genAI {true,true}, databaseQueryData: true, queues: true, stackFrameVariables: true`). So an absent block, and every omitted category of a partial block, is established PII-on.
  - **Beyond the issue:** `sentry-sdk` 2.70.0 (PyPI latest) keeps `send_default_pii` but adds `data_collection`, documented in `consts.py` as "superseding `send_default_pii` … omitted fields use their defaults (most categories are collected) … If `send_default_pii` is also set, `data_collection` takes precedence." Key-value categories use the string modes `"off" | "denylist" | "allowlist"`. Consequence: `send_default_pii=False` next to a partial `data_collection` dict is **not** PII-off, and the current rule would wrongly PASS it.
  - `defaultIntegrations` (the other SDK-option spelling the scanner keys on, `:72`) is unchanged in 11.0.0 (`options.d.ts:592: defaultIntegrations?: false | Integration[]`) and in sentry-sdk 2.70.0.

## Requirements gate

No `project/requirements/` artifact exists for #664. **Operator override** granted at the approval gate (2026-09-25): the issue is the maintainer's precise defect report with its target behaviour, and every acceptance criterion below is checkable.

## Scope

- **In scope**: the scanner's default-PII check (Phase 5 and its output line), the skill's default-PII ruling, and the effect-plus-evidence wording in `spec/project/error-tracking/{en,de}.md`.
- **Out of scope**: the before-send scrubbing check (unchanged); other SDK vendors; kamerplanter's own configuration (#1685 lives there); a mechanical guard (see Risks).

## Route

- **Decision**: direct
- **Rationale**: one outcome, one PR strand, no roadmap item.

## Work packages

### P1 — Scanner recognises the effect, not a spelling

- **Problem statement**: `error-tracking-audit-scanner.md:134` (Phase 5) and the output line `:176`. Hypothesis: the check reports a state **per PII category**. It resolves the category set and each default from the pinned SDK's own source in the working copy when present (`node_modules/@sentry/core/build/types/types/datacollection.d.ts` plus `resolveDataCollectionOptions.js`; `site-packages/sentry_sdk/data_collection.py` and `consts.py`), and otherwise from a per-major table it carries for the two SDKs measured here. PASS = the legacy flag explicitly off with **no** data-collection block present, or a data-collection block whose every PII category is explicitly off (`false` / `[]` / `"off"`). A block that names some categories reports each omitted one as UNSET-per-category. An allow/deny-restricted category reports as RESTRICTED. When both the legacy flag and a block are present, the block wins (Python precedence). The specialist may refute the source-reading step if it is not statically decidable and keep the per-major table alone.
- **Acceptance criteria**: (a) Phase 5 states the effect-based rule, both spellings, the precedence, and the per-category states; (b) the output line reports per-category states and the SDK major the categories came from; (c) `frameContextLines` is excluded as a non-PII category; (d) `python3 scripts/validate_skills.py plugins/nolte-engineering/agents/` → no Critical, no `agent-description-budget` finding; the `description:` stays unchanged.
- **Touched files / artifacts**: `plugins/nolte-engineering/agents/error-tracking-audit-scanner.md`
- **Specialist**: `nolte-claude-dev:claude-plugin-developer`
- **Depends on**: none

### P2 — Skill ruling for the new states

- **Problem statement**: `plugins/nolte-engineering/skills/error-tracking-audit/SKILL.md:102`. Hypothesis: add the rulings: all-off block → PASS; UNSET-per-category where the pinned SDK's default is established on (Sentry JS ≥ 11, sentry-sdk with `data_collection`) → Critical per category, else Warning; RESTRICTED → Warning, because deny-lists leave the rest collected and the scrubbing hook remains its own check; legacy flag off plus a partial block → rule on the block. Body-only; the skill's `description:` stays unchanged.
- **Acceptance criteria**: the ruling covers every state P1 can emit; `python3 scripts/validate_skills.py plugins/nolte-engineering/skills/error-tracking-audit/` → no Critical; body-token band not worsened.
- **Touched files / artifacts**: `plugins/nolte-engineering/skills/error-tracking-audit/SKILL.md` (and `references/check-policy.md` only if it restates the ruling — today it defers to SKILL.md)
- **Specialist**: `nolte-claude-dev:claude-plugin-developer`
- **Depends on**: P1 (state vocabulary)

### P3 — Spec names the effect and both spellings as evidence

- **Problem statement**: `spec/project/error-tracking/en.md:52` already requires the effect ("default-PII behaviour stays off"). Hypothesis: add one sentence saying the evidence is SDK-version-dependent — a legacy boolean flag or a structured per-category data-collection option with every PII category off — and that a partial structured block counts only for the categories it names, so the next SDK rename does not repeat this. Translate the delta into `de.md`.
- **Acceptance criteria**: EN and DE carry the same sentence; `pre-commit run --files spec/project/error-tracking/en.md spec/project/error-tracking/de.md` → Passed (Vale, section refs).
- **Touched files / artifacts**: `spec/project/error-tracking/en.md`, `spec/project/error-tracking/de.md`
- **Specialist**: `nolte-shared:spec` (skill)
- **Depends on**: none

## Dependency ordering

P3 ; P1 → P2 (P3 independent).

## Class sweep (for the fix PR)

- **Predicate**: `grep -n -E '`[A-Za-z_]+(=|: )(False|false|True|true|None|null|[0-9.]+)`' plugins/*/agents/*scanner*.md agents/*scanner*.md`: a scanner check keyed on a literal option assignment.
- **Hits**: 7 (run 2026-09-25). 4 are output-schema fields (`guard-coverage-scanner.md:97,:132`, `lektorat-scanner.md:214,:218`). 1 is a GitHub Action input (`dockerfile-audit-scanner.md:114`, `push: true`). 2 are SDK option spellings: `error-tracking-audit-scanner.md:134` (defective) and `:72` (`defaultIntegrations: false`, verified unchanged in 11.0.0 and sentry-sdk 2.70.0).
- **Repaired**: 1.
- **Guard**: none mechanical — the checks are natural-language instructions to an agent, with no executable selector to pin. The durable guard is the rule itself: resolve the category set from the pinned SDK's source, and state the spec in terms of effect.

## Risks

- **Agent description budget**: the `nolte-engineering` agents headroom was 1389 chars on 2026-09-25 before #666 took 56. Keep the description unchanged.
- **Static decidability**: reading `node_modules`/`site-packages` works only when installed in the working copy. The per-major table is the fallback and must be dated.
- **Allow-list judgement**: RESTRICTED → Warning, decided by the operator on 2026-09-25.

## Open questions

none — resolved 2026-09-25: RESTRICTED categories (allow or deny list) rule as **Warning** (operator decision).

## Dispatch log

2026-09-25 P3 via skill nolte-shared:spec (operation 2, update) — evidence sentence added to spec/project/error-tracking/en.md:52 and de.md:52; restatements walked (AC :103 and check set :118 phrase "default-PII off" and stay consistent; no count changed); structure EN/DE 69 bullets, 11 AC, 15 headings each; pre-commit Vale 0 errors, markdownlint Passed.
2026-09-25 P1 dispatched to nolte-claude-dev:claude-plugin-developer — Phase 5 judges the effect per PII category with a dated per-major table (JS ≤ 10, JS ≥ 11, Python with/without data_collection) and installed-source resolution; new output vocabulary. **Refutation recorded:** rule (a) "legacy flag off and no block → PASS" is a false PASS on Sentry JS ≥ 11, where `sendDefaultPii` is removed and ignored; restricted to SDKs that still honour the flag (JS ≤ 10, Python), JS ≥ 11 reports the flag as ignored and UNSET; new hard rule. Spec sentence (P3) aligned: "where the pinned SDK still honours it". validate_skills 39 artifacts 0C/0W/0S/1I, pre-commit Passed.
2026-09-25 P2 dispatched to nolte-claude-dev:claude-plugin-developer — default-PII ruling rewritten as a state→severity table covering every scanner state (PASS ×2; EXPLICIT TRUE / ON / UNSET→ON Critical; RESTRICTED Warning; UNSET→UNKNOWN Warning + operator action; legacy-flag-only UNSET Warning); restatement in references/report-shape.md:31 updated. **Partial refutation recorded:** overall UNSET cannot occur with a structured block (scanner reports NOT ALL OFF then); ruling split accordingly. validate_skills 0C/1W/0S/1I — the Warning is the pre-existing body-token-approaching band (~4762 → ~4810 tokens, about 190 below the 5,000 cap). pre-commit Passed.
2026-09-25 Independent verification (Explore, read-only, against the unpacked SDK sources): 2 Critical (C1 `@sentry/core@10.75.3` already ships `dataCollection` and a present block resolves omitted categories ON; C2 Python key-value categories take `{"mode": "off"}`, `cookies=False` resolves to denylist = collected), 6 Warnings (Python defaults unnamed; sub-fields; empty deny list = ON; legacy-flag SDK UNSET rows; non-literal values; legacy flag leaves categories collected), 1 Suggestion (.js over .d.ts). C1 and C2 re-verified by the orchestrator at source. Operator decision on the legacy-flag finding: stays PASS, still-collected categories recorded as an informational note. Fixes by nolte-claude-dev:claude-plugin-developer; partial refutation: the Python still-collected list also includes url_query_params (denylist) and stack_frame_variables unless include_local_variables=False; `_experiments={"data_collection": …}` is read when the top-level option is absent. validate_skills 0C, SKILL.md body ~4810 → ~4825 tokens.
