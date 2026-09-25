---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "671"
classification: "spec-change"
secondary-classes: []
route: "direct"
status: approved
created: "2026-09-25"
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #671 — error-tracking: decide whether an explicitly-off legacy PII flag satisfies default-PII off when the SDK still collects categories
- **URL**: <https://github.com/nolte/claude-shared/issues/671>
- **Labels**: spec
- **Linked items**: #664, #670 (merged `958e8fae`, which introduced the current legacy-flag PASS)
- **Prior art checked**: no open PR; the rule sites on `develop` at `958e8fae` are `spec/project/error-tracking/en.md:52` and `de.md:52` ("a legacy boolean flag set explicitly off where the pinned SDK still honours it"), `plugins/nolte-engineering/agents/error-tracking-audit-scanner.md:155,:157,:199` (`PASS: legacy flag off` plus the informational still-collected note), `plugins/nolte-engineering/skills/error-tracking-audit/SKILL.md:106` (PASS row).
- **Trusted author**: `nolte` (repository owner); the issue was filed in this session from #670's operator decision.

## Classification

- **Primary class**: spec-change
- **Secondary class(es)**: none
- **Rationale**: the issue asks for a decision on what the spec's MUST accepts as evidence; scanner and skill follow the spec. Confirmed with the operator on 2026-09-25.
- **Asserted cause verified**: confirmed at source (re-measured this run, not inherited from #670):
  - `@sentry/core@10.75.3` `defaultPiiToCollectionOptions(false)`: `userInfo: false`, `cookies`, `httpHeaders.request/response`, `urlQueryParams` = `{deny: PII_HEADER_SNIPPETS}` with `PII_HEADER_SNIPPETS = ["forwarded", "-ip", "remote-", "via", "-user"]`, `httpBodies: []`, `graphQL: {document: true, variables: true}`, `genAI` off, `databaseQueryData: false`, `stackFrameVariables: true`.
  - `sentry-sdk` 2.70.0 `_map_from_send_default_pii(send_default_pii=False)`: `user_info` False, `cookies`, `http_headers.request`, `url_query_params` = denylist with the same five terms, `http_bodies` = all body types, `graphql`/`gen_ai`/`database_query_data`/`queues` False, `stack_frame_variables = include_local_variables` (default True).
  - Both SDKs always filter keys matching a sensitive list regardless of the flag (JS `shouldFilterDataKey` with `SENSITIVE_KEY_SNIPPETS` = auth, token, secret, session, password, …; Python `_SENSITIVE_DENYLIST`). So auth headers and session cookies are masked in either case; other cookies, and on Python all request bodies, are still sent.

## Decision (operator, 2026-09-25)

**One measure for both spellings: judge the legacy flag by its effect, exactly like the structured block.** PASS only when no PII category is still collected. An explicitly-off legacy flag counts only for the categories it actually switches off; the categories it leaves on or deny-listed are findings under the existing per-category rulings (`ON` and `RESTRICTED` are Critical).

## Requirements gate

No `project/requirements/` artifact. **Operator override**: the decision above is the requirement; acceptance is checkable per package.

## Scope

- **In scope**: the spec sentence (EN/DE), the scanner's legacy-flag path, the skill ruling, the report shape.
- **Out of scope**: vendor SDKs other than Sentry JS and Python; consumer repositories (kamerplanter and others will see new findings, see Risks).

## Route

- **Decision**: direct — one outcome, one PR strand, no roadmap item.

## Work packages

### P1 — Spec: the legacy flag is evidence only for what it switches off

- **Problem statement**: `spec/project/error-tracking/en.md:52` accepts "a legacy boolean flag set explicitly off where the pinned SDK still honours it" as evidence. Hypothesis: reword so the evidence is the resolved per-category effect of whichever spelling the pinned SDK honours; an explicitly-off legacy flag counts only for the categories it switches off, because on current SDKs it still leaves some collected (name the measured example: request bodies on Python). Mirror in `de.md`. Walk restatements (AC, check set at `:118`).
- **Acceptance criteria**: EN and DE carry the same meaning; structure parity; `pre-commit run --files` on both → Passed.
- **Touched files**: `spec/project/error-tracking/en.md`, `de.md`
- **Specialist**: skill `nolte-shared:spec`
- **Depends on**: none

### P2 — Scanner: resolve the legacy flag into per-category states

- **Problem statement**: `error-tracking-audit-scanner.md:155,:157,:199` report `PASS: legacy flag off` plus an informational note. Hypothesis: on an SDK that honours the legacy flag, resolve an explicit `false` into per-category states through the SDK's own mapping (installed source `defaultPiiToCollectionOptions` / `_map_from_send_default_pii`, or the dated table with the measured values above, including `include_local_variables`); deny-listed categories report `RESTRICTED`, collected ones `ON`. Retire the overall token `PASS: legacy flag off` and the informational note; the overall state becomes `PASS: every category OFF` or `NOT ALL OFF: <categories>` with `evidence: legacy flag`. The specialist may refute if an SDK line exists where the legacy flag alone resolves every category off, and keep a PASS path for it.
- **Acceptance criteria**: no remaining `PASS: legacy flag off` / "informational" note in the agent; the dated table carries the legacy-off mappings for JS 10 and Python; `python3 scripts/validate_skills.py plugins/nolte-engineering/agents/` → no Critical, no budget finding; frontmatter unchanged.
- **Touched files**: `plugins/nolte-engineering/agents/error-tracking-audit-scanner.md`
- **Specialist**: `nolte-claude-dev:claude-plugin-developer`
- **Depends on**: none (P3 depends on its vocabulary)

### P3 — Skill: drop the legacy PASS row

- **Problem statement**: `SKILL.md:106` passes `PASS: legacy flag off`. Hypothesis: remove that token from the PASS row; nothing else changes because the categories flow into the existing Critical row. Update `references/report-shape.md` if it names the token. Body stays ≤ current (~4814 tokens).
- **Acceptance criteria**: grep for `legacy flag off` in the skill and its references → only in a "retired" note or nowhere; validator no Critical; body not larger.
- **Touched files**: `plugins/nolte-engineering/skills/error-tracking-audit/SKILL.md`, `references/report-shape.md`
- **Specialist**: `nolte-claude-dev:claude-plugin-developer`
- **Depends on**: P2

## Dependency ordering

P1 ; P2 → P3.

## Risks

- **Consumer impact**: every component relying on the legacy flag alone (Sentry JS ≤ 10, Python without `data_collection`) moves from PASS to per-category Critical findings. The remedy on both SDKs is a structured block with every category off (JS 10.75.3 already ships `dataCollection`; Python `data_collection` with `{"mode": "off"}` for key-value categories). This is intended, and the PR must say so.
- **SKILL.md body** is near the 5,000-token cap; P3 only removes text.

## Open questions

none

## Dispatch log
2026-09-25 P1 via skill nolte-shared:spec (operation 2, update) — spec/project/error-tracking/en.md:52 and de.md:52: evidence = every collected personal-data category resolves off; an explicitly-off legacy flag counts only for the categories it switches off (Python still sends request bodies); where both forms are set the honoured one decides. Restatements walked (AC and check set phrase "default-PII off"; no other "legacy" mention in the spec); structure EN/DE 69 bullets, 11 AC, 15 headings; vale --output=line on en.md empty.
2026-09-25 P2 dispatched to nolte-claude-dev:claude-plugin-developer — legacy rows resolved through the SDK mappings; `PASS: legacy flag off` and the informational note retired; hypothesis confirmed (no SDK line reaches all-off through the flag alone: JS 10 keeps graphQL and stackFrameVariables on, Python keeps http_bodies). Overall vocabulary: PASS: every category OFF | NOT ALL OFF | EXPLICIT TRUE | UNSET. validate_skills 39 artifacts 0C/0W/0S/1I.
2026-09-25 P3 dispatched to nolte-claude-dev:claude-plugin-developer — SKILL.md:106 PASS row now `PASS: every category OFF` only; remaining ruling rows verified against the scanner; body ~4814 → ~4796 tokens; validate_skills 0C.
2026-09-25 Independent verification (Explore, read-only, against SDK sources): 0 Critical, 2 Warnings (absent flag rated milder than explicit false for an identical effect; no reachable PASS on legacy-only SDKs and no remedy stated), 3 Suggestions. Fixed by nolte-claude-dev:claude-plugin-developer: absent flag resolves through the same mapping (identical severity), remedy note in references/report-shape.md, non-literal include_local_variables → UNSET→UNKNOWN, graphQL document-redaction note. SKILL.md body ~4796 → ~4781 tokens.
