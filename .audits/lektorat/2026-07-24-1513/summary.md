# Lektorat full audit — 2026-07-24-1513 (issue #441)

Full-scope run: docs/en/ (28) + docs/de/ (28) + top-level Markdown (README.md, CONTRIBUTING.md,
SECURITY.md, AUDIENCES.md; CLAUDE.md excluded as an LLM-instruction artifact). All six dimensions
evaluated (`dimensions_evaluated: [D1, D2, D3, D4, D5, D6]`, no remainder). Readability via
`readability_lix.py` v1.1.0 (recorded in `pipeline_metadata`). DE pipeline: LanguageTool HTTP API
(public endpoint), 2048 raw matches reduced to 8 genuine findings — zero protected-term-candidate,
strip-artifact, dangling-hyphen-compound, or emoji-shortcode false positives (issue #441 AC met).

## Infrastructure conditions

- `content-mode-missing` — `docs/en/privacy.md` and `docs/de/privacy.md` carry no YAML frontmatter;
  D1 skipped, D5 fell back to the whole audience set. Not auto-patchable here; same drift is
  independently recorded by the 2026-Q3 spec-readiness run (docs-freshness phase-6b/6c validation)
  for a dedicated `docs-freshness-checker` pass.

## Findings by severity

Counts: critical 0 · warning 20 (14 EN, 6 DE) · suggestion 2 (DE). Every critical+warning finding
carries a disposition below (issue #441 AC met).

### Warning — fixed (14; disposition: patch, autonomous approval recorded)

| ID | File | Dim | Fix |
|---|---|---|---|
| ce563c08d8 | docs/en/references/specs/skill-management.md | D2 | RFC expanded on first use |
| d5ee8fcad0 | docs/en/references/specs/agent-management.md | D2 | RFC expanded on first use |
| 04491ea609 | docs/en/guides/architecture.md | D2 | ADRs expanded on first use |
| d71cd770e2 | docs/en/guides/agents-concept.md | D2 | ADR expanded (table cell) |
| 3a4ca614e7 | README.md | D2 | ADR expanded on first use |
| 295fdd4b51 | docs/en/guides/development-lifecycle.md | D2 | ADR expanded on first use |
| 19ab915b83 | docs/en/guides/development-lifecycle.md | D2 | CVEs expanded on first use |
| a361293394 | docs/en/guides/skills-concept.md | D2 | CVEs expanded (table cell) |
| d09aa22eb9 | CONTRIBUTING.md | D2 | SLA expanded on first use |
| 0219d94011 | docs/en/by-task.md | D2 | AC spelled out on first use |
| 6dfd7306e3 | docs/en/getting-started/usage.md | D5 | `track: user-docs` → `developer-docs` (matches declared audience; DE counterpart carried the identical drift and was fixed for parity) |
| lekt-d229c2aeec | docs/de/guides/development-lifecycle.md | D3 | "einen neuen Agent" → "einen neuen Agenten" |
| lekt-263614f178 | docs/de/guides/test-automation.md | D3 | "einen Agent" → "einen Agenten" |
| lekt-6a78d5ca2a | docs/de/guides/development-lifecycle.md | D2 | MVP expanded on first use |

### Warning — skip-and-record (6; dismissal recorded, rationale per finding)

- **7d39414ca2** (docs/en/portfolio/index.md, D1, LIX 59 vs warn 55): per-file corridor override —
  the page is auto-generated verbatim from `portfolio/aggregate.yml`; its long-word density comes
  from member mission/capability summaries. Hand-editing the rendered page is forbidden
  (idempotent generator); shortening source manifests is a portfolio-content decision, tracked
  with the portfolio workstream (#462/#463 context). Corridor override rationale: table-heavy
  generated reference page, explicitly anticipated by issue #441.
- **b29619db11 / 495b462492** (references/specs pages, D4 mixed heading case): the Title Case
  headings ("Goals and Non-Goals", "Acceptance Criteria", "Open Questions") mirror the canonical
  spec section names verbatim — a deliberate mirroring convention; normalizing them would break
  the visual identity with the spec corpus. Recorded as accepted convention.
- **lekt-44b1502b7a** (DE du-vs-Sie register, 11 pages): the informal "du" address is used
  consistently (never mixed) across the whole DE tree and matches common German OSS developer-doc
  register. Recorded as the accepted portfolio convention override of the spec's Sie-default;
  follow-up recommendation: pin the override in Lektorat-local config so future audits stop
  flagging it.
- **lekt-c65f60ac1a / lekt-10cd200d73** (docs/de/portfolio/index.md, D3/D5 untranslated EN in
  generated DE page): root cause is the generator pulling English source fields
  (mission_statement/description) verbatim; the fix belongs at the source-data/generator layer,
  not the rendered page. Recorded for the portfolio-rendering workstream (#457 triggers / #462
  tech_stack backlog); out of Lektorat's remit.

### Suggestion — recorded (2, disposition optional per severity floor)

- lekt-cfd8e740c6 (DE agents-concept, ADR unexpanded) — glossary-entry candidate.
- lekt-39371cb95c (DE usage.md "Deutsch fragen ergibt...") — low-confidence LanguageTool style
  hint; phrasing is idiomatic enough, left as-is.

## Processing log

- 2026-07-24-1513—audit-run—60 files scanned (2 batched scanner dispatches: EN 32, DE 28)—claude
  (autonomous orchestrator session, operator-mandated processing of issue #441).
- 2026-07-24—patch-phase—14 warnings fixed (one finding, one edit each; approvals recorded as
  autonomous decisions under the operator's issue-backlog mandate); 6 warnings dismissed
  skip-and-record with rationale; 2 suggestions recorded.
- 2026-07-24—final disposition counts: fixed 14 · skip-and-record 6 · recorded 2 · critical 0.
  Run closed.
