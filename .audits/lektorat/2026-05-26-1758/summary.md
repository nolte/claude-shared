# Lektorat audit — claude-shared

- **Operation**: `audit`
- **Operation version**: `1`
- **Ran at**: 2026-05-26T17:58:00Z
- **Severity floor**: `suggestion`
- **Scope**: 33 files (16 DE under `docs/de/`, 16 EN under `docs/en/`, plus `README.md` resolved EN via repository default)
- **Audience artefact**: `AUDIENCES.md` (9 audiences)
- **EN pipeline**: `vale` 3.14.1 (`.vale.ini`)
- **DE pipeline**: `languagetool-http` (build 2026-05-12, `https://api.languagetool.org/v2`)

## Totals

- **Total findings**: 37
- **Severity**: critical 5 · warning 23 · suggestion 9
- **Dimension**: D1 10 · D2 3 · D3 22 · D4 2 · D5 0
- **Inventory findings**: 0
- **Files with findings**: 19 of 33 (14 clean)

## Top files by finding count

| File | Count |
| --- | --- |
| README.md | 6 |
| docs/en/lifecycle.md | 4 |
| docs/de/planning-suite.md | 3 |
| docs/en/development/projektstruktur.md | 3 |
| docs/en/planning-suite.md | 3 |
| docs/de/specs/agent-management.md | 2 |
| docs/en/concepts/skills/skill-management.md | 2 |
| docs/en/specs/agent-management.md | 2 |
| docs/en/specs/skill-management.md | 2 |

## Infrastructure conditions

None. Both pipelines (Vale EN, LanguageTool HTTP API DE) resolved cleanly. Every in-scope file's language, content_mode, and audiences resolved without ambiguity.

## Critical findings (5)

### `docs/en/specs/agent-management.md` — D1 Readability (FRE+FKGL)

- **Line**: 1–100
- **Rule**: `lektorat §D1 Readability (FRE+FKGL)`
- **Message**: FRE 15.4 (crit < 30) and FKGL 21.9 (crit > 18) both cross the critical corridor for content_mode reference.
- **Evidence**: FRE=15.4 (crit corridor <30), FKGL=21.9 (crit corridor >18). Longest passage: 383 words in one continuous table/list run.
- **Resolution hint**: Break the combined Goals/Requirements/Acceptance-Criteria table run into separate subsections with shorter prose bridges.

### `docs/en/specs/skill-management.md` — D1 Readability (FRE+FKGL)

- **Line**: 1–83
- **Rule**: `lektorat §D1 Readability (FRE+FKGL)`
- **Message**: FRE 30.2 below warn corridor (<45) and FKGL 16.6 above warn corridor (>14) for content_mode reference.
- **Evidence**: FRE=30.2 (warn corridor <45, crit <30), FKGL=16.6 (warn corridor >14). Longest run: 135-word Requirements+Recommendations block.
- **Resolution hint**: Split the stacked MUST/SHOULD requirement bullets into prose sentences to lift FRE above 45.

### `docs/de/specs/agent-management.md` — D1 Readability (WSTF+LIX)

- **Line**: 1–100
- **Rule**: `lektorat §D1 Readability (WSTF+LIX)`
- **Message**: WSTF 12.1 (warn>10, crit>13) and LIX 71.5 (crit>70) cross the critical corridor for content_mode reference.
- **Evidence**: WSTF=12.1, LIX=71.5 (crit>70). Avg sentence length 33.6 words; longest passage spans the Requirements excerpt block.
- **Resolution hint**: Shorten compound requirement sentences; avoid chains of dependent clauses in normative bullets.

### `docs/de/specs/skill-management.md` — D1 Readability (WSTF+LIX)

- **Line**: 1–83
- **Rule**: `lektorat §D1 Readability (WSTF+LIX)`
- **Message**: LIX 65.3 above warn corridor (>60) and WSTF 11.0 above warn corridor (>10) for content_mode reference.
- **Evidence**: WSTF=11.0 (warn>10), LIX=65.3 (warn>60). Avg sentence 27.8 words; Requirements block has dense stacked MUSS-bullets.
- **Resolution hint**: Break stacked normative requirement bullets into separate short sentences with a transitional intro clause.

### `README.md` — D2 Comprehensibility (unexplained-abbreviation, published-surface escalation)

- **Line**: 34
- **Rule**: `lektorat §D2 Comprehensibility (unexplained-abbreviation, published-surface escalation)`
- **Audience**: `downstream-user`
- **Message**: Abbreviation 'CVE' appears in a table row with no expansion on first use in a published artefact with non-operator audience.
- **Evidence**: `` | `dependency-audit` | Scan the dependency tree for known CVEs (and optionally license issues) ``
- **Resolution hint**: Expand CVE on first use: 'Common Vulnerabilities and Exposures (CVE)' in the table cell or a preceding sentence.

## Warning findings (23)

### D1 Readability (6)

| File | Metric snapshot | Resolution hint |
| --- | --- | --- |
| docs/en/getting-started/installation.md (L1–67) | FRE 45.3 (warn <60), FKGL 11.7 (warn >10) | Split the 58-word Prerequisites run; reduce the introductory sentence to under 20 words. |
| docs/en/planning-suite.md (L1–96) | FRE 41.4 (warn <45), FKGL 12.3 | Add a prose lead-in before the Skill-to-stage table; shorten adoption list items. |
| docs/en/development/projektstruktur.md (L1–68) | FRE 34.7 (warn <45), FKGL 12.7 | Add short introductory prose before each table. |
| docs/de/getting-started/installation.md (L1–67) | WSTF 8.5 (warn >7), LIX 51.0 (warn >50) | Split Überprüfen and Dogfooding intro sentences; target avg sentence length < 18. |
| docs/de/planning-suite.md (L1–96) | WSTF 9.5, LIX 56.0; longest sentence 86+ words | Break the 86-word adoption paragraph (line 86) at the em-dash. |
| docs/de/concepts/agents/index.md (L1–65) | LIX 60.2 (warn >60), WSTF 10.1 | Split opening compound sentence at the semicolons. |

### D2 Comprehensibility (2)

- `README.md` (L132) — Abbreviation **SLA** without expansion in `**No SLA.**`. Hint: `**No service-level agreement (SLA).**`
- `docs/en/lifecycle.md` (L13) — Abbreviation **MVP** without expansion on first use. Hint: `minimum viable product (MVP)`.

### D3 Spelling/Grammar — EN Microsoft.Terms `agent`/`Agent` (8)

Vale flags `agent`/`Agent` as a non-accepted term across 8 EN files. All resolve to a single vocabulary fix:

> Add `agent` and `Agent` to the claude-shared Vale accept vocabulary (`.github/styles/config/vocabularies/claude-shared/accept.txt`). One change suppresses all 8 findings.

Affected files / lines: `README.md` (21), `docs/en/concepts/agents/index.md` (15), `docs/en/development/beitragen.md` (13), `docs/en/development/index.md` (28), `docs/en/development/projektstruktur.md` (53), `docs/en/lifecycle.md` (15), `docs/en/planning-suite.md` (11), `docs/en/specs/agent-management.md` (9).

### D3 Spelling/Grammar — DE LanguageTool (6)

| File | Line | Rule | Sample | Hint |
| --- | --- | --- | --- | --- |
| docs/de/planning-suite.md | 58 | GERMAN_SPELLER_RULE | `\| Stage \| Skill \| Schreibt / liest \| Govering Spec \|` | Correct **Govering → Governing**. |
| docs/de/planning-suite.md | 11 | DE_AGREEMENT | `die Sammlung von Skills und einem Agent, mit der ein Repository …` | Rephrase as `mit denen …` (plural antecedent). |
| docs/de/development/beitragen.md | 23 | DE_CASE | `Read-only = keine Schreib-Tools.` | Lowercase or gloss: `Nur-Lese-Zugriff (Read-only) = …`. |
| docs/de/concepts/skills/skill-management.md | 21 | DE_AGREEMENT | `wo die neue Skill-Dateien landen` | `die neuen Skill-Dateien` (plural agreement). |
| docs/de/specs/agent-management.md | 17 | DE_AGREEMENT | `… aus der Claude Code den Agent lädt` | Rephrase: `… von der aus Claude Code den Agent lädt`. |
| docs/de/lifecycle.md | 94 | DOPPELPUNKT_GROSS | `… ein: wem das Projekt dient …` | Capitalise: `… ein: Wem das Projekt dient …`. |

### D4 Writing Style (1)

- `docs/en/concepts/skills/skill-management.md` (L19) — Vale Microsoft.We flags first-person plural `our` in `check if this skill follows our conventions`. Hint: `the project conventions` or `the authoring spec` to keep second-person register.

## Suggestion findings (9)

### D3 Microsoft.Headings — EN sentence-case headings (5)

| File | Line | Sample | Hint |
| --- | --- | --- | --- |
| docs/en/development/projektstruktur.md | 9 | `# Project Structure` | `# Project structure` |
| docs/en/lifecycle.md | 92 | `### 7 Close and Release` (and peers) | `### 7 Close and release` (sentence-case across phase headings) |
| docs/en/planning-suite.md | 9 | `# Planning Suite` | `# Planning suite` |
| docs/en/specs/skill-management.md | 9, 24 | `# Skill Authoring`, `## Goals and Non-Goals` | `# Skill authoring`, `## Goals and non-goals` |
| docs/en/concepts/skills/skill-management.md | 9 | `# Skill Management` | `# Skill management` |

### D3 Microsoft.Acronyms — EN first-use expansion (3)

- `README.md` (L132) — `**No SLA.**` → `**No service-level agreement (SLA).**`
- `README.md` (L139) — `[MIT](LICENSE)` → `[MIT license](LICENSE)` (advisory; well-known)
- `docs/en/lifecycle.md` (L13) — `MVP` → `minimum viable product (MVP)`

### D4 Microsoft.Passive — EN active-voice nudge (1)

- `README.md` (L7) — `… intended to be reused across multiple software development projects.` → `… that teams reuse across multiple projects.`

## D5 Audience-fit

No D5 findings. All 33 in-scope files declare a `developer-docs`-track audience (`[maintainer]` or `[maintainer, external-contributor]`) and the content registers match. `README.md` (whole-audience surface by §Audience binding rule 2) serves all 9 audiences appropriately; no register mismatch detected.

## Next steps

- For interactive fixes finding-by-finding, run `/nolte-shared:lektorat-apply` with operation `patch` (one finding, one diff, one approval).
- For a per-file full rewrite addressing all `critical` + `warning` findings, run with operation `revise` (full-artefact rewrite with diff review; one file per invocation).
- The 8 `Microsoft.Terms` `agent`/`Agent` warnings collapse into **one** vocabulary edit at `.github/styles/config/vocabularies/claude-shared/accept.txt` — consider that first to clear noise before further work.
- D1 critical findings are concentrated in the four `specs/*-management.md` mirror pages; their density mirrors the underlying spec source (which is out of scope for Lektorat per §Scope and applicability and per the skill's hard rules).
