# Example 01: `audit` across a bilingual MkDocs repository

## Input prompt

"Auditiere die Lesbarkeit und Audience-Fit aller Docs in diesem Repo, EN und DE."

## Input files (optional)

- `docs/en/` and `docs/de/` — parallel MkDocs trees populated per `spec/project/docs-multilingual-authoring/`, with `audience` / `track` / `content_mode` frontmatter per `spec/project/docs-audience-tracks/`
- `AUDIENCES.md` — audience artefact at the repo root per `spec/project/audience-identification/`
- `spec/.spec-config.yml` — declares `canonical_language: en` and `languages: [en, de]`
- `.vale.ini` — pins `nolte/vale-style@<tag>` for EN-text mechanics; no DE Vale config (per `prose-style` scope)
- No `Taskfile.yml` Lektorat target declared yet

## Expected behaviour

1. Resolve the target set as every Markdown file under `docs/en/` and `docs/de/`, then filter through `spec/project/lektorat/` §Scope and applicability — exclude any path under `spec/`, `skills/`, `agents/`; exclude `_`-prefixed snippet folders (reviewed with their hosting page); include top-level repository Markdown (`README.md`, `ONBOARDING.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `SECURITY.md`) as the operator asked for "all Docs".
2. Resolve languages via the priority chain — `docs/en/**` → EN, `docs/de/**` → DE, top-level Markdown → repository default from `spec/.spec-config.yml` (`canonical_language: en`). Never auto-detect from text content.
3. Resolve audiences — read `AUDIENCES.md` from the repo root; for each in-scope file apply the audience-binding priority chain: frontmatter `audience:` wins where present, artefact-type defaults apply for top-level Markdown (`README.md` → every audience; `CONTRIBUTING.md` → `developer-docs`-track audiences only), whole audience set as fallback. Stop with the spec's single-sentence error if `AUDIENCES.md` and all alternate locations are missing.
4. Dispatch `lektorat-scanner` (Agent) with the resolved (file, language, audiences, content_mode, audience-artefact) tuples, severity floor `suggestion` (the user did not narrow). Batch the dispatch as a single agent run since the repository fits comfortably in one agent context; split per-file only when an artefact set exceeds the context budget.
5. Wait for the agent's structured findings inventory — per-finding JSON entries with stable `id`, `severity` (`critical|warning|suggestion`), `dimension` (`D1|D2|D3|D4|D5`), `file`, `line_start` / `line_end`, `message`, `rule` (for example `lektorat §D1 Readability — FRE corridor`), `language`, `audience`, `evidence` (≤240 chars), `suggested_resolution` (≤240 chars).
6. Render `findings.json` under `.audits/lektorat/2026-05-21-1430/` with the verbatim shape from `spec/project/lektorat/` §Outputs §Findings report (machine-readable); include the top-level `language_summary` (for example `[{"language": "en", "files": 14}, {"language": "de", "files": 14}]`).
7. Render `summary.md` in the same folder — severity-sorted (`critical` first), within severity grouped by file then dimension, with the offending sample, the named rule or metric value (FRE / FKGL for EN, WSTF / LIX for DE), the resolution hint, and the audience IDs cited. Use English section headings; surrounding prose in German per the user-language policy.
8. Record the run configuration in `run.json` — operation `audit`, severity floor `suggestion`, the resolved scope summary, the `ran_at` UTC timestamp. (The resolved pipeline metadata is not recorded here; it lives in the `findings.json` `pipeline_metadata` block per `spec/project/lektorat/` §Outputs.)
9. Confirm in German with the audit-trail folder path, per-severity counts (for example "12 critical, 47 warning, 134 suggestion"), and a next-step hint — `patch` for interactive fixes on the `critical` items first, or no action when the operator runs this as a gate check.
10. **Never write outside `.audits/lektorat/`**, **never edit any in-scope artefact**, and **never dispatch any mutating tool** during `audit`. Re-running the same invocation against an unchanged repository produces a byte-identical `findings` array (modulo `ran_at`).
