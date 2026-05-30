# Lektorat audit — `nolte/claude-shared`

- **Run timestamp**: 2026-05-30T07:26:09Z
- **Repository**: nolte/claude-shared
- **Operation**: `audit` (operation_version `1`)
- **In-scope files**: 39 (EN: 20; DE: 19)
- **Pipelines**: EN `vale 3.14.1`; DE `languagetool-http 6.9-SNAPSHOT (build 2026-05-26)`

**Severity totals**: critical=24, warning=128, suggestion=546  
**Dimension totals**: D1=36, D3=578, D4=84; D2 / D5 not yet evaluated (need scanner-agent dispatch).

## Infrastructure conditions (19)

- `content-mode-missing` (en) — README.md — README.md hat kein content_mode-Frontmatter; D1 wird übersprungen (Spec §D1 verlangt einen bekannten Modus).
- `language-pipeline-missing` (de) — docs/de/by-task.md — DE-Pipeline meldete 13 TYPOGRAPHY-Matches, die Markdown-Strip-Artefakte sind; eine markdown-bewusste Vorverarbeitung fehlt.
- `language-pipeline-missing` (de) — docs/de/getting-started/index.md — DE-Pipeline meldete 1 TYPOGRAPHY-Matches, die Markdown-Strip-Artefakte sind; eine markdown-bewusste Vorverarbeitung fehlt.
- `language-pipeline-missing` (de) — docs/de/getting-started/installation.md — DE-Pipeline meldete 15 TYPOGRAPHY-Matches, die Markdown-Strip-Artefakte sind; eine markdown-bewusste Vorverarbeitung fehlt.
- `language-pipeline-missing` (de) — docs/de/getting-started/nutzung.md — DE-Pipeline meldete 4 TYPOGRAPHY-Matches, die Markdown-Strip-Artefakte sind; eine markdown-bewusste Vorverarbeitung fehlt.
- `language-pipeline-missing` (de) — docs/de/guides/agents-concept.md — DE-Pipeline meldete 26 TYPOGRAPHY-Matches, die Markdown-Strip-Artefakte sind; eine markdown-bewusste Vorverarbeitung fehlt.
- `language-pipeline-missing` (de) — docs/de/guides/contributing.md — DE-Pipeline meldete 7 TYPOGRAPHY-Matches, die Markdown-Strip-Artefakte sind; eine markdown-bewusste Vorverarbeitung fehlt.
- `language-pipeline-missing` (de) — docs/de/guides/development-lifecycle.md — DE-Pipeline meldete 96 TYPOGRAPHY-Matches, die Markdown-Strip-Artefakte sind; eine markdown-bewusste Vorverarbeitung fehlt.
- `language-pipeline-missing` (de) — docs/de/guides/development.md — DE-Pipeline meldete 2 TYPOGRAPHY-Matches, die Markdown-Strip-Artefakte sind; eine markdown-bewusste Vorverarbeitung fehlt.
- `language-pipeline-missing` (de) — docs/de/guides/index.md — DE-Pipeline meldete 1 TYPOGRAPHY-Matches, die Markdown-Strip-Artefakte sind; eine markdown-bewusste Vorverarbeitung fehlt.
- `language-pipeline-missing` (de) — docs/de/guides/project-structure.md — DE-Pipeline meldete 14 TYPOGRAPHY-Matches, die Markdown-Strip-Artefakte sind; eine markdown-bewusste Vorverarbeitung fehlt.
- `language-pipeline-missing` (de) — docs/de/guides/skill-management.md — DE-Pipeline meldete 22 TYPOGRAPHY-Matches, die Markdown-Strip-Artefakte sind; eine markdown-bewusste Vorverarbeitung fehlt.
- `language-pipeline-missing` (de) — docs/de/guides/skills-concept.md — DE-Pipeline meldete 65 TYPOGRAPHY-Matches, die Markdown-Strip-Artefakte sind; eine markdown-bewusste Vorverarbeitung fehlt.
- `language-pipeline-missing` (de) — docs/de/guides/spec.md — DE-Pipeline meldete 25 TYPOGRAPHY-Matches, die Markdown-Strip-Artefakte sind; eine markdown-bewusste Vorverarbeitung fehlt.
- `language-pipeline-missing` (de) — docs/de/index.md — DE-Pipeline meldete 8 TYPOGRAPHY-Matches, die Markdown-Strip-Artefakte sind; eine markdown-bewusste Vorverarbeitung fehlt.
- `language-pipeline-missing` (de) — docs/de/project/index.md — DE-Pipeline meldete 67 TYPOGRAPHY-Matches, die Markdown-Strip-Artefakte sind; eine markdown-bewusste Vorverarbeitung fehlt.
- `language-pipeline-missing` (de) — docs/de/references/specs/agent-management.md — DE-Pipeline meldete 41 TYPOGRAPHY-Matches, die Markdown-Strip-Artefakte sind; eine markdown-bewusste Vorverarbeitung fehlt.
- `language-pipeline-missing` (de) — docs/de/references/specs/index.md — DE-Pipeline meldete 17 TYPOGRAPHY-Matches, die Markdown-Strip-Artefakte sind; eine markdown-bewusste Vorverarbeitung fehlt.
- `language-pipeline-missing` (de) — docs/de/references/specs/skill-management.md — DE-Pipeline meldete 26 TYPOGRAPHY-Matches, die Markdown-Strip-Artefakte sind; eine markdown-bewusste Vorverarbeitung fehlt.

## Critical findings (24)

### `README.md` — 1 finding(s)

**D3** (1):

- L113 `vale:Microsoft.GeneralURL` — For a general audience, use 'address' rather than 'URL'. _(audience: —)_
  > `URL`

### `docs/de/getting-started/installation.md` — 1 finding(s)

**D1** (1):

- L1 `lektorat §D1 Readability WSTF1` — Wiener Sachtextformel V1 = 10.3 über 7 (warn) / 10 (crit) für content_mode=how-to. _(audience: maintainer, external-contributor)_
  > `Voraussetzungen  Claude Code installiert Lokaler Checkout dieses Repositorys (oder ein Ort, auf den Claude Code Zugriff `

### `docs/de/getting-started/nutzung.md` — 1 finding(s)

**D1** (1):

- L1 `lektorat §D1 Readability WSTF1` — Wiener Sachtextformel V1 = 10.6 über 7 (warn) / 10 (crit) für content_mode=how-to. _(audience: maintainer, downstream-user)_
  > `Welcher Skill für was  | Skill | Zweck | Typische Trigger | |-------|-------|-----------------| |   | Neue Skills anlege`

### `docs/de/guides/agents-concept.md` — 1 finding(s)

**D1** (1):

- L1 `lektorat §D1 Readability WSTF1` — Wiener Sachtextformel V1 = 13.3 über 10 (warn) / 13 (crit) für content_mode=explanation. _(audience: maintainer)_
  > `Enthaltene Agents  | Agent | Zweck | |-------|-------| |   | Entwirft spec-konforme Plugin-Skills und -Agents für   | | `

### `docs/de/guides/contributing.md` — 1 finding(s)

**D1** (1):

- L1 `lektorat §D1 Readability WSTF1` — Wiener Sachtextformel V1 = 12.1 über 7 (warn) / 10 (crit) für content_mode=how-to. _(audience: external-contributor)_
  > `Konventionen  **Namen**: ASCII-Kebab-Case. **Beschreibungen**: konkrete User-Trigger ("einsetzen, wenn der Nutzer X sagt`

### `docs/de/guides/development-lifecycle.md` — 2 finding(s)

**D1** (2):

- L1 `lektorat §D1 Readability WSTF1` — Wiener Sachtextformel V1 = 16.4 über 10 (warn) / 13 (crit) für content_mode=explanation. _(audience: maintainer)_
  > `Drei Agents stützen diese Phase:   für Spec-Gates,   für neue Plugin-Artefakte und   für audience-getriebene Doku-Entwür`
- L1 `lektorat §D1 Readability LIX` — LIX = 82.6 über 60 (warn) / 70 (crit) für content_mode=explanation. _(audience: maintainer)_
  > `Drei Agents stützen diese Phase:   für Spec-Gates,   für neue Plugin-Artefakte und   für audience-getriebene Doku-Entwür`

### `docs/de/guides/project-structure.md` — 1 finding(s)

**D1** (1):

- L1 `lektorat §D1 Readability WSTF1` — Wiener Sachtextformel V1 = 14.4 über 10 (warn) / 13 (crit) für content_mode=reference. _(audience: external-contributor, maintainer)_
  > `        Projektstruktur  Aktueller Top-Level-Aufbau:                             Geplant, aber noch nicht angelegt:     `

### `docs/de/references/specs/agent-management.md` — 2 finding(s)

**D1** (2):

- L1 `lektorat §D1 Readability WSTF1` — Wiener Sachtextformel V1 = 17.6 über 10 (warn) / 13 (crit) für content_mode=reference. _(audience: maintainer)_
  > `Ziele und Nicht-Ziele  **Ziele**  Einheitliche Form auf der Festplatte Routbar über präzise, trigger-orientierte   Minim`
- L1 `lektorat §D1 Readability LIX` — LIX = 83.4 über 60 (warn) / 70 (crit) für content_mode=reference. _(audience: maintainer)_
  > `Ziele und Nicht-Ziele  **Ziele**  Einheitliche Form auf der Festplatte Routbar über präzise, trigger-orientierte   Minim`

### `docs/de/references/specs/skill-management.md` — 2 finding(s)

**D1** (2):

- L1 `lektorat §D1 Readability WSTF1` — Wiener Sachtextformel V1 = 14.9 über 10 (warn) / 13 (crit) für content_mode=reference. _(audience: maintainer)_
  > `Ziele und Nicht-Ziele  **Ziele**  Jeder Skill hat dieselbe vorhersehbare Form auf der Festplatte Skills sind durch präzi`
- L1 `lektorat §D1 Readability LIX` — LIX = 71.8 über 60 (warn) / 70 (crit) für content_mode=reference. _(audience: maintainer)_
  > `Ziele und Nicht-Ziele  **Ziele**  Jeder Skill hat dieselbe vorhersehbare Form auf der Festplatte Skills sind durch präzi`

### `docs/en/getting-started/installation.md` — 1 finding(s)

**D1** (1):

- L1 `lektorat §D1 Readability FRE` — Flesch Reading Ease 41.5 below 60 (warn) / 45 (crit) for content_mode=how-to. _(audience: maintainer, external-contributor)_
  > `Prerequisites  Claude Code installed A local checkout of this repository (or a location Claude Code can access)  Load in`

### `docs/en/guides/agents-concept.md` — 1 finding(s)

**D1** (1):

- L1 `lektorat §D1 Readability FRE` — Flesch Reading Ease 22.2 below 45 (warn) / 30 (crit) for content_mode=explanation. _(audience: maintainer)_
  > `Bundled agents  | Agent | Purpose | |-------|---------| |   | Drafts spec-conforming plugin skills and agents for   | | `

### `docs/en/guides/contributing.md` — 1 finding(s)

**D1** (1):

- L1 `lektorat §D1 Readability FRE` — Flesch Reading Ease 39.8 below 60 (warn) / 45 (crit) for content_mode=how-to. _(audience: external-contributor)_
  > `Conventions  **Names**: ASCII kebab-case. **Descriptions**: concrete user triggers ("use when the user says X"), not abs`

### `docs/en/guides/development-lifecycle.md` — 2 finding(s)

**D1** (2):

- L1 `lektorat §D1 Readability FRE` — Flesch Reading Ease 7.5 below 45 (warn) / 30 (crit) for content_mode=explanation. _(audience: maintainer)_
  > `Three agents support this phase:   for spec gates,   for new plugin artefacts, and   for audience-driven documentation d`
- L1 `lektorat §D1 Readability FKGL` — Flesch-Kincaid Grade Level 24.5 above 14 (warn) / 18 (crit) for content_mode=explanation. _(audience: maintainer)_
  > `Three agents support this phase:   for spec gates,   for new plugin artefacts, and   for audience-driven documentation d`

### `docs/en/guides/project-structure.md` — 2 finding(s)

**D1** (2):

- L1 `lektorat §D1 Readability FRE` — Flesch Reading Ease 16.4 below 45 (warn) / 30 (crit) for content_mode=reference. _(audience: external-contributor, maintainer)_
  > `        Project structure  Current top-level layout:                             Planned but not yet created:      What `
- L1 `lektorat §D1 Readability FKGL` — Flesch-Kincaid Grade Level 18.6 above 14 (warn) / 18 (crit) for content_mode=reference. _(audience: external-contributor, maintainer)_
  > `        Project structure  Current top-level layout:                             Planned but not yet created:      What `

### `docs/en/references/specs/agent-management.md` — 2 finding(s)

**D1** (2):

- L1 `lektorat §D1 Readability FRE` — Flesch Reading Ease 2.5 below 45 (warn) / 30 (crit) for content_mode=reference. _(audience: maintainer)_
  > `Goals and Non-Goals  **Goals**  Consistent shape on disk Routable through precise, trigger-oriented  s Minimum necessary`
- L1 `lektorat §D1 Readability FKGL` — Flesch-Kincaid Grade Level 24.9 above 14 (warn) / 18 (crit) for content_mode=reference. _(audience: maintainer)_
  > `Goals and Non-Goals  **Goals**  Consistent shape on disk Routable through precise, trigger-oriented  s Minimum necessary`

### `docs/en/references/specs/index.md` — 1 finding(s)

**D3** (1):

- L24 `vale:Microsoft.HeadingAcronyms` — Avoid using acronyms in a title or heading. _(audience: maintainer)_
  > `RFC`

### `docs/en/references/specs/skill-management.md` — 2 finding(s)

**D1** (2):

- L1 `lektorat §D1 Readability FRE` — Flesch Reading Ease 21.5 below 45 (warn) / 30 (crit) for content_mode=reference. _(audience: maintainer)_
  > `Goals and Non-Goals  **Goals**  Every skill has the same predictable shape on disk Skills are discoverable by Claude thr`
- L1 `lektorat §D1 Readability FKGL` — Flesch-Kincaid Grade Level 18.3 above 14 (warn) / 18 (crit) for content_mode=reference. _(audience: maintainer)_
  > `Goals and Non-Goals  **Goals**  Every skill has the same predictable shape on disk Skills are discoverable by Claude thr`

## Warning findings (128)

### `README.md` — 1 finding(s)

**D4** (1):

- L44 `vale:Microsoft.Adverbs` — Remove 'strictly' if it's not important to the meaning of the statement. _(audience: —)_
  > `strictly`

### `docs/de/by-task.md` — 3 finding(s)

**D3** (3):

- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `autolinkt`
- L1 `languagetool:ZUSAMMENGESETZTE_VERBEN` — Bitte prüfen Sie die Getrenntschreibung. _(audience: maintainer)_
  > `unter   schreiben`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `dedupliziert`

### `docs/de/getting-started/index.md` — 1 finding(s)

**D3** (1):

- L1 `languagetool:CHECK_OUT` — 'Check-out' _(audience: maintainer, external-contributor)_
  > `Checkout`

### `docs/de/getting-started/installation.md` — 3 finding(s)

**D1** (1):

- L1 `lektorat §D1 Readability LIX` — LIX = 54.9 über 50 (warn) / 60 (crit) für content_mode=how-to. _(audience: maintainer, external-contributor)_
  > `Voraussetzungen  Claude Code installiert Lokaler Checkout dieses Repositorys (oder ein Ort, auf den Claude Code Zugriff `

**D3** (2):

- L1 `languagetool:CHECK_OUT` — 'Check-out' _(audience: maintainer, external-contributor)_
  > `Checkout`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer, external-contributor)_
  > `tip`

### `docs/de/getting-started/nutzung.md` — 2 finding(s)

**D1** (1):

- L1 `lektorat §D1 Readability LIX` — LIX = 55.0 über 50 (warn) / 60 (crit) für content_mode=how-to. _(audience: maintainer, downstream-user)_
  > `Welcher Skill für was  | Skill | Zweck | Typische Trigger | |-------|-------|-----------------| |   | Neue Skills anlege`

**D3** (1):

- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer, downstream-user)_
  > `namespaced`

### `docs/de/guides/agents-concept.md` — 3 finding(s)

**D1** (1):

- L1 `lektorat §D1 Readability LIX` — LIX = 62.1 über 60 (warn) / 70 (crit) für content_mode=explanation. _(audience: maintainer)_
  > `Enthaltene Agents  | Agent | Zweck | |-------|-------| |   | Entwirft spec-konforme Plugin-Skills und -Agents für   | | `

**D3** (2):

- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `zielgruppengetriebene`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `stale`

### `docs/de/guides/contributing.md` — 2 finding(s)

**D1** (1):

- L1 `lektorat §D1 Readability LIX` — LIX = 55.0 über 50 (warn) / 60 (crit) für content_mode=how-to. _(audience: external-contributor)_
  > `Konventionen  **Namen**: ASCII-Kebab-Case. **Beschreibungen**: konkrete User-Trigger ("einsetzen, wenn der Nutzer X sagt`

**D3** (1):

- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: external-contributor)_
  > `Validierungsmodus`

### `docs/de/guides/development-lifecycle.md` — 25 finding(s)

**D3** (25):

- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `phasenagnostische`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `bounded`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `context`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `retargeten`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `Scaffolds`
- L1 `languagetool:ZUSAMMENGESETZTE_VERBEN` — Bitte prüfen Sie die Getrenntschreibung. _(audience: maintainer)_
  > `unter   schreiben`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `deduplizieren`
- L1 `languagetool:DE_AGREEMENT` — Evtl. passen Wörter grammatisch nicht zusammen. _(audience: maintainer)_
  > `einen neuen Agent`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `Taskfile`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `authoren`
- _… 15 more D3 finding(s) at this severity (see `findings.json`)_

### `docs/de/guides/development.md` — 1 finding(s)

**D3** (1):

- L1 `languagetool:DE_AGREEMENT` — Evtl. passen Wörter grammatisch nicht zusammen. _(audience: external-contributor, maintainer)_
  > `das garantiert Konformität`

### `docs/de/guides/project-structure.md` — 2 finding(s)

**D1** (1):

- L1 `lektorat §D1 Readability LIX` — LIX = 66.1 über 60 (warn) / 70 (crit) für content_mode=reference. _(audience: external-contributor, maintainer)_
  > `        Projektstruktur  Aktueller Top-Level-Aufbau:                             Geplant, aber noch nicht angelegt:     `

**D3** (1):

- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: external-contributor, maintainer)_
  > `Refs`

### `docs/de/guides/skill-management.md` — 13 finding(s)

**D1** (1):

- L1 `lektorat §D1 Readability WSTF1` — Wiener Sachtextformel V1 = 11.6 über 10 (warn) / 13 (crit) für content_mode=explanation. _(audience: maintainer)_
  > `Wann einsetzen  "neuen Skill anlegen", "Skill für X erstellen" "create a new skill", "scaffold a skill for X", "add a sk`

**D3** (12):

- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `create`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `new`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `skill`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `scaffold`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `skill`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `for`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `add`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `skill`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `to`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `the`
- _… 2 more D3 finding(s) at this severity (see `findings.json`)_

### `docs/de/guides/skills-concept.md` — 10 finding(s)

**D3** (10):

- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `Findings`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `Findings`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `Lint`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `Typecheck`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `Repo`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `diffen`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `Failing`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `Bounded`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `Contexts`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `chainen`

### `docs/de/guides/spec.md` — 20 finding(s)

**D1** (1):

- L1 `lektorat §D1 Readability WSTF1` — Wiener Sachtextformel V1 = 12.3 über 10 (warn) / 13 (crit) für content_mode=explanation. _(audience: maintainer)_
  > `Wann einsetzen  "schreib eine Spec für X", "neue Spezifikation" "ist X schon abgedeckt?" (Duplikat-Check) "übersetz die `

**D3** (19):

- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `regenerate`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `the`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `spec`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `index`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `Topic`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `Defaults`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `Defaults`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `Create`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `nie teilfertig`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `Mismatches`
- _… 9 more D3 finding(s) at this severity (see `findings.json`)_

### `docs/de/index.md` — 8 finding(s)

**D3** (8):

- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer, downstream-user)_
  > `nolte`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer, downstream-user)_
  > `jigsaw`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer, downstream-user)_
  > `robot`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer, downstream-user)_
  > `scroll`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer, downstream-user)_
  > `hammer`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer, downstream-user)_
  > `and`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer, downstream-user)_
  > `wrench`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer, downstream-user)_
  > `info`

### `docs/de/project/index.md` — 10 finding(s)

**D3** (10):

- L1 `languagetool:DE_AGREEMENT` — Evtl. passen Wörter grammatisch nicht zusammen. _(audience: maintainer)_
  > `den einzigen Agent`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `Governing`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `enforced`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `Violations`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `dispatcht`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `Finding`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `chainen`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `Sections`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `chained`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `skipped`

### `docs/de/references/index.md` — 2 finding(s)

**D3** (2):

- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `References`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `katalogweite`

### `docs/de/references/specs/agent-management.md` — 6 finding(s)

**D3** (6):

- L1 `languagetool:DE_AGREEMENT` — Evtl. passen Wörter grammatisch nicht zusammen. _(audience: maintainer)_
  > `den Agent`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `dispatcht`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `Routbar`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `genestete`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `dispatchbar`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `freitextlich`

### `docs/de/references/specs/index.md` — 2 finding(s)

**D3** (2):

- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `Topic`
- L1 `languagetool:GERMAN_SPELLER_RULE` — Rechtschreibfehler _(audience: maintainer)_
  > `Slug`

### `docs/en/getting-started/installation.md` — 1 finding(s)

**D1** (1):

- L1 `lektorat §D1 Readability FKGL` — Flesch-Kincaid Grade Level 13.5 above 10 (warn) / 14 (crit) for content_mode=how-to. _(audience: maintainer, external-contributor)_
  > `Prerequisites  Claude Code installed A local checkout of this repository (or a location Claude Code can access)  Load in`

### `docs/en/getting-started/nutzung.md` — 2 finding(s)

**D1** (2):

- L1 `lektorat §D1 Readability FRE` — Flesch Reading Ease 49.5 below 60 (warn) / 45 (crit) for content_mode=how-to. _(audience: maintainer, downstream-user)_
  > `Which skill for what  | Skill | Purpose | Typical triggers | |-------|---------|-----------------| |   | Scaffold new sk`
- L1 `lektorat §D1 Readability FKGL` — Flesch-Kincaid Grade Level 11.4 above 10 (warn) / 14 (crit) for content_mode=how-to. _(audience: maintainer, downstream-user)_
  > `Which skill for what  | Skill | Purpose | Typical triggers | |-------|---------|-----------------| |   | Scaffold new sk`

### `docs/en/guides/agents-concept.md` — 1 finding(s)

**D1** (1):

- L1 `lektorat §D1 Readability FKGL` — Flesch-Kincaid Grade Level 16.5 above 14 (warn) / 18 (crit) for content_mode=explanation. _(audience: maintainer)_
  > `Bundled agents  | Agent | Purpose | |-------|---------| |   | Drafts spec-conforming plugin skills and agents for   | | `

### `docs/en/guides/contributing.md` — 1 finding(s)

**D1** (1):

- L1 `lektorat §D1 Readability FKGL` — Flesch-Kincaid Grade Level 11.9 above 10 (warn) / 14 (crit) for content_mode=how-to. _(audience: external-contributor)_
  > `Conventions  **Names**: ASCII kebab-case. **Descriptions**: concrete user triggers ("use when the user says X"), not abs`

### `docs/en/guides/project-structure.md` — 1 finding(s)

**D4** (1):

- L71 `vale:Microsoft.Adverbs` — Remove 'lightly' if it's not important to the meaning of the statement. _(audience: external-contributor, maintainer)_
  > `lightly`

### `docs/en/guides/skill-management.md` — 3 finding(s)

**D1** (1):

- L1 `lektorat §D1 Readability FRE` — Flesch Reading Ease 44.0 below 45 (warn) / 30 (crit) for content_mode=explanation. _(audience: maintainer)_
  > `When to use  "create a new skill," "scaffold a skill for X," "add a skill to this repo"  "neuen Skill anlegen," "Skill f`

**D4** (2):

- L55 `vale:Microsoft.Adverbs` — Remove 'roughly' if it's not important to the meaning of the statement. _(audience: maintainer)_
  > `roughly`
- L68 `vale:Microsoft.Adverbs` — Remove 'silently' if it's not important to the meaning of the statement. _(audience: maintainer)_
  > `silently`

### `docs/en/guides/spec.md` — 3 finding(s)

**D1** (1):

- L1 `lektorat §D1 Readability FRE` — Flesch Reading Ease 31.1 below 45 (warn) / 30 (crit) for content_mode=explanation. _(audience: maintainer)_
  > `When to use  "write a spec for X," "new specification" "is X already covered?" (duplicate check) "translate the spec" "r`

**D4** (2):

- L94 `vale:Microsoft.Adverbs` — Remove 'partially' if it's not important to the meaning of the statement. _(audience: maintainer)_
  > `partially`
- L100 `vale:Microsoft.Adverbs` — Remove 'silently' if it's not important to the meaning of the statement. _(audience: maintainer)_
  > `silently`

### `docs/en/references/specs/skill-management.md` — 2 finding(s)

**D4** (2):

- L35 `vale:Microsoft.Adverbs` — Remove 'separately' if it's not important to the meaning of the statement. _(audience: maintainer)_
  > `separately`
- L58 `vale:Microsoft.Adverbs` — Remove 'roughly' if it's not important to the meaning of the statement. _(audience: maintainer)_
  > `roughly`

## Suggestion findings (546)

### `README.md` — 27 finding(s)

**D3** (5):

- L54 `vale:Microsoft.Semicolon` — Try to simplify this sentence. _(audience: —)_
  > `;`
- L54 `vale:Microsoft.Semicolon` — Try to simplify this sentence. _(audience: —)_
  > `;`
- L89 `vale:Microsoft.Semicolon` — Try to simplify this sentence. _(audience: —)_
  > `;`
- L152 `vale:Microsoft.Acronyms` — 'SLA' has no definition. _(audience: —)_
  > `SLA`
- L159 `vale:Microsoft.Acronyms` — 'MIT' has no definition. _(audience: —)_
  > `MIT`

**D4** (22):

- L7 `vale:Microsoft.Passive` — 'be reused' looks like passive voice. _(audience: —)_
  > `be reused`
- L21 `vale:Microsoft.Passive` — 'is distributed' looks like passive voice. _(audience: —)_
  > `is distributed`
- L21 `vale:Microsoft.Passive` — 'are dispatched' looks like passive voice. _(audience: —)_
  > `are dispatched`
- L29 `vale:Microsoft.Vocab` — Verify your use of 'against' with the A-Z word list. _(audience: —)_
  > `against`
- L29 `vale:Microsoft.Vocab` — Verify your use of 'actionable' with the A-Z word list. _(audience: —)_
  > `actionable`
- L30 `vale:Microsoft.Vocab` — Verify your use of 'against' with the A-Z word list. _(audience: —)_
  > `against`
- L30 `vale:Microsoft.Vocab` — Verify your use of 'actionable' with the A-Z word list. _(audience: —)_
  > `actionable`
- L35 `vale:Microsoft.Vocab` — Verify your use of 'against' with the A-Z word list. _(audience: —)_
  > `against`
- L37 `vale:Microsoft.Vocab` — Verify your use of 'against' with the A-Z word list. _(audience: —)_
  > `against`
- L45 `vale:Microsoft.Vocab` — Verify your use of 'against' with the A-Z word list. _(audience: —)_
  > `against`
- _… 12 more D4 finding(s) at this severity (see `findings.json`)_

### `docs/de/by-task.md` — 23 finding(s)

**D3** (23):

- L1 `lektorat §D3 protected-term-candidate` — Token 'Agents' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Agents`
- L1 `languagetool:DE_CASE` — Großschreibung von Nomen und substantivierten Verben _(audience: maintainer)_
  > `Bislang`
- L1 `lektorat §D3 protected-term-candidate` — Token 'pilot-migrierten' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `pilot-migrierten`
- L1 `lektorat §D3 protected-term-candidate` — Token 'phasen-gruppierten' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `phasen-gruppierten`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Agents-Index' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Agents-Index`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Conventional-Commits-Titel' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Conventional-Commits-Titel`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Specs' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Specs`
- L1 `languagetool:DE_CASE` — Großschreibung von Nomen und substantivierten Verben _(audience: maintainer)_
  > `Bereits`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Pre-Merge-Review' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Pre-Merge-Review`
- L1 `lektorat §D3 protected-term-candidate` — Token 'draft' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `draft`
- _… 13 more D3 finding(s) at this severity (see `findings.json`)_

### `docs/de/getting-started/installation.md` — 14 finding(s)

**D3** (14):

- L1 `languagetool:UPPERCASE_SENTENCE_START` — Groß-/Kleinschreibung _(audience: maintainer, external-contributor)_
  > `ist`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Agents' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer, external-contributor)_
  > `Agents`
- L1 `languagetool:DE_CASE` — Großschreibung von Nomen und substantivierten Verben _(audience: maintainer, external-contributor)_
  > `Lokaler`
- L1 `languagetool:DOPPELTES_AUSRUFEZEICHEN` — mehrere Ausrufezeichen etc. _(audience: maintainer, external-contributor)_
  > `!!!`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Symlink' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer, external-contributor)_
  > `Symlink`
- L1 `lektorat §D3 protected-term-candidate` — Token 'claude-shared' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer, external-contributor)_
  > `claude-shared`
- L1 `languagetool:BINDESTRICH_SUBSTANTIV` — Ungewollter Bindestrich '-Aufgabe' _(audience: maintainer, external-contributor)_
  > `-Ordner`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Symlink' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer, external-contributor)_
  > `Symlink`
- L1 `languagetool:BINDESTRICH_SUBSTANTIV` — Ungewollter Bindestrich '-Aufgabe' _(audience: maintainer, external-contributor)_
  > `-Dialog`
- L1 `languagetool:BINDESTRICH_SUBSTANTIV` — Ungewollter Bindestrich '-Aufgabe' _(audience: maintainer, external-contributor)_
  > `-Wechsel`
- _… 4 more D3 finding(s) at this severity (see `findings.json`)_

### `docs/de/getting-started/nutzung.md` — 6 finding(s)

**D3** (6):

- L1 `lektorat §D3 protected-term-candidate` — Token 'Plugin-Prefix' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer, downstream-user)_
  > `Plugin-Prefix`
- L1 `languagetool:PRP_WAS_WO` — Standardsprache: 'woran' statt 'an was' _(audience: maintainer, downstream-user)_
  > `für was`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Spec' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer, downstream-user)_
  > `Spec`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Spec' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer, downstream-user)_
  > `Spec`
- L1 `languagetool:FRAGE_KLEIN` — eine frage (Frage) _(audience: maintainer, downstream-user)_
  > `fragen`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Spec-Skill' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer, downstream-user)_
  > `Spec-Skill`

### `docs/de/guides/agents-concept.md` — 26 finding(s)

**D3** (26):

- L1 `lektorat §D3 protected-term-candidate` — Token 'Agents' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Agents`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Agents' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Agents`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Sub-Agents' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Sub-Agents`
- L1 `languagetool:BINDESTRICH_SUBSTANTIV` — Ungewollter Bindestrich '-Aufgabe' _(audience: maintainer)_
  > `-Tool`
- L1 `languagetool:BINDESTRICH_SUBSTANTIV` — Ungewollter Bindestrich '-Aufgabe' _(audience: maintainer)_
  > `-Plugins`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Agents' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Agents`
- L1 `lektorat §D3 protected-term-candidate` — Token 'spec-konforme' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `spec-konforme`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Agents' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Agents`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Specs' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Specs`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Requirement-vs-Acceptance-Vollständigkeit' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Requirement-vs-Acceptance-Vollständigkeit`
- _… 16 more D3 finding(s) at this severity (see `findings.json`)_

### `docs/de/guides/contributing.md` — 20 finding(s)

**D3** (20):

- L1 `lektorat §D3 protected-term-candidate` — Token 'Spec' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: external-contributor)_
  > `Spec`
- L1 `lektorat §D3 protected-term-candidate` — Token 'scaffolden' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: external-contributor)_
  > `scaffolden`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Frontmatter' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: external-contributor)_
  > `Frontmatter`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Spec' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: external-contributor)_
  > `Spec`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Spec-Skill' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: external-contributor)_
  > `Spec-Skill`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Frontmatter-Mismatch' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: external-contributor)_
  > `Frontmatter-Mismatch`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Hard-Rules' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: external-contributor)_
  > `Hard-Rules`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Specs' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: external-contributor)_
  > `Specs`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Spec-Skill' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: external-contributor)_
  > `Spec-Skill`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Agents' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: external-contributor)_
  > `Agents`
- _… 10 more D3 finding(s) at this severity (see `findings.json`)_

### `docs/de/guides/development-lifecycle.md` — 89 finding(s)

**D3** (89):

- L1 `lektorat §D3 protected-term-candidate` — Token 'Agents' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Agents`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Cross-cutting' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Cross-cutting`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Frontmatter' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Frontmatter`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Agents-Katalog-Seiten' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Agents-Katalog-Seiten`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Agents' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Agents`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Agents' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Agents`
- L1 `lektorat §D3 protected-term-candidate` — Token 'mid-flow' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `mid-flow`
- L1 `lektorat §D3 protected-term-candidate` — Token 'dispatched' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `dispatched`
- L1 `lektorat §D3 protected-term-candidate` — Token 'scaffolden' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `scaffolden`
- L1 `languagetool:BINDESTRICH_SUBSTANTIV` — Ungewollter Bindestrich '-Aufgabe' _(audience: maintainer)_
  > `-Dateien`
- _… 79 more D3 finding(s) at this severity (see `findings.json`)_

### `docs/de/guides/development.md` — 5 finding(s)

**D3** (5):

- L1 `lektorat §D3 protected-term-candidate` — Token 'Agents' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: external-contributor, maintainer)_
  > `Agents`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Dogfooding' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: external-contributor, maintainer)_
  > `Dogfooding`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Repo-Root' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: external-contributor, maintainer)_
  > `Repo-Root`
- L1 `languagetool:UPPERCASE_SENTENCE_START` — Groß-/Kleinschreibung _(audience: external-contributor, maintainer)_
  > `übernimmt`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Spec' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: external-contributor, maintainer)_
  > `Spec`

### `docs/de/guides/index.md` — 4 finding(s)

**D3** (4):

- L1 `lektorat §D3 protected-term-candidate` — Token 'How-tos' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer, external-contributor)_
  > `How-tos`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Agents' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer, external-contributor)_
  > `Agents`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Spec' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer, external-contributor)_
  > `Spec`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Agents' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer, external-contributor)_
  > `Agents`

### `docs/de/guides/project-structure.md` — 3 finding(s)

**D3** (3):

- L1 `lektorat §D3 protected-term-candidate` — Token 'Spec-Config' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: external-contributor, maintainer)_
  > `Spec-Config`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Spec-Index' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: external-contributor, maintainer)_
  > `Spec-Index`
- L1 `lektorat §D3 protected-term-candidate` — Token 'auto-generiert' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: external-contributor, maintainer)_
  > `auto-generiert`

### `docs/de/guides/skill-management.md` — 16 finding(s)

**D3** (16):

- L1 `lektorat §D3 protected-term-candidate` — Token 'claude-shared' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `claude-shared`
- L1 `lektorat §D3 protected-term-candidate` — Token 'top-level' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `top-level`
- L1 `lektorat §D3 protected-term-candidate` — Token 'README' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `README`
- L1 `languagetool:BINDESTRICH_SUBSTANTIV` — Ungewollter Bindestrich '-Aufgabe' _(audience: maintainer)_
  > `-Dialog`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Symlink' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Symlink`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Frontmatter' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Frontmatter`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Frontmatter' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Frontmatter`
- L1 `languagetool:DE_CASE` — Großschreibung von Nomen und substantivierten Verben _(audience: maintainer)_
  > `Keine`
- L1 `languagetool:DE_CASE` — Großschreibung von Nomen und substantivierten Verben _(audience: maintainer)_
  > `Unterstützende`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Frontmatter-Mismatch' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Frontmatter-Mismatch`
- _… 6 more D3 finding(s) at this severity (see `findings.json`)_

### `docs/de/guides/skills-concept.md` — 34 finding(s)

**D3** (34):

- L1 `languagetool:BINDESTRICH_SUBSTANTIV` — Ungewollter Bindestrich '-Aufgabe' _(audience: maintainer)_
  > `-Tool`
- L1 `languagetool:BINDESTRICH_SUBSTANTIV` — Ungewollter Bindestrich '-Aufgabe' _(audience: maintainer)_
  > `-Plugins`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Autoren-Spec' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Autoren-Spec`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Autoren-Spec' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Autoren-Spec`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Spec' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Spec`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Release-Drafter-Draft' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Release-Drafter-Draft`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Pre-Publish-Gates' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Pre-Publish-Gates`
- L1 `lektorat §D3 protected-term-candidate` — Token 'dispatchen' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `dispatchen`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Spec' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Spec`
- L1 `lektorat §D3 protected-term-candidate` — Token 'scaffolden' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `scaffolden`
- _… 24 more D3 finding(s) at this severity (see `findings.json`)_

### `docs/de/guides/spec.md` — 23 finding(s)

**D3** (23):

- L1 `lektorat §D3 protected-term-candidate` — Token 'Spec' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Spec`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Spec' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Spec`
- L1 `languagetool:UPPERCASE_SENTENCE_START` — Groß-/Kleinschreibung _(audience: maintainer)_
  > `schreib`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Spec' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Spec`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Spec' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Spec`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Topic-Ordner' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Topic-Ordner`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Specs' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Specs`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Topic-Nesting' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Topic-Nesting`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Spec' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Spec`
- L1 `languagetool:LEERZEICHEN_VOR_AUSRUFEZEICHEN_ETC` — Falsches Leerzeichen vor Ausrufezeichen etc. _(audience: maintainer)_
  > `via  :`
- _… 13 more D3 finding(s) at this severity (see `findings.json`)_

### `docs/de/index.md` — 11 finding(s)

**D3** (11):

- L1 `languagetool:UPPERCASE_SENTENCE_START` — Groß-/Kleinschreibung _(audience: maintainer, downstream-user)_
  > `ist`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Agents' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer, downstream-user)_
  > `Agents`
- L1 `languagetool:FRAGEZEICHEN_STATT_PUNKT` — Fragezeichen statt eines Punkts am Ende einer Frage _(audience: maintainer, downstream-user)_
  > `.`
- L1 `languagetool:KOMMA_INFINITIVGRUPPEN` — Komma vor Infinitivgruppen mit 'als', 'anstatt', 'außer', 'ohne', 'statt', 'um' _(audience: maintainer, downstream-user)_
  > ` ohne`
- L1 `lektorat §D3 protected-term-candidate` — Token 'claude-shared' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer, downstream-user)_
  > `claude-shared`
- L1 `languagetool:BINDESTRICH_SUBSTANTIV` — Ungewollter Bindestrich '-Aufgabe' _(audience: maintainer, downstream-user)_
  > `-Tool`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Agents' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer, downstream-user)_
  > `Agents`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Sub-Agents' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer, downstream-user)_
  > `Sub-Agents`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Agents' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer, downstream-user)_
  > `Agents`
- L1 `languagetool:DOPPELTES_AUSRUFEZEICHEN` — mehrere Ausrufezeichen etc. _(audience: maintainer, downstream-user)_
  > `!!!`
- _… 1 more D3 finding(s) at this severity (see `findings.json`)_

### `docs/de/project/index.md` — 33 finding(s)

**D3** (33):

- L1 `lektorat §D3 protected-term-candidate` — Token 'Specs' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Specs`
- L1 `languagetool:BINDESTRICH_SUBSTANTIV` — Ungewollter Bindestrich '-Aufgabe' _(audience: maintainer)_
  > `-Verzeichnis`
- L1 `lektorat §D3 protected-term-candidate` — Token 'On-disk-Artefakte' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `On-disk-Artefakte`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Dispatch-' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Dispatch-`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Spec' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Spec`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Stabilisierungs-Gate' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Stabilisierungs-Gate`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Per-sprint' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Per-sprint`
- L1 `lektorat §D3 protected-term-candidate` — Token 'cycle' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `cycle`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Per-sprint' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Per-sprint`
- L1 `lektorat §D3 protected-term-candidate` — Token 'cycle' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `cycle`
- _… 23 more D3 finding(s) at this severity (see `findings.json`)_

### `docs/de/references/index.md` — 2 finding(s)

**D3** (2):

- L1 `lektorat §D3 protected-term-candidate` — Token 'Agents' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Agents`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Agents' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Agents`

### `docs/de/references/specs/agent-management.md` — 39 finding(s)

**D3** (39):

- L1 `lektorat §D3 protected-term-candidate` — Token 'draft' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `draft`
- L1 `lektorat §D3 protected-term-candidate` — Token 'claude-shared' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `claude-shared`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Agents' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Agents`
- L1 `languagetool:BINDESTRICH_SUBSTANTIV` — Ungewollter Bindestrich '-Aufgabe' _(audience: maintainer)_
  > `-Tool`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Agents' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Agents`
- L1 `lektorat §D3 protected-term-candidate` — Token 'trigger-orientierte' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `trigger-orientierte`
- L1 `languagetool:DE_CASE` — Großschreibung von Nomen und substantivierten Verben _(audience: maintainer)_
  > `Minimal`
- L1 `languagetool:DE_CASE` — Großschreibung von Nomen und substantivierten Verben _(audience: maintainer)_
  > `Nachgelagerte`
- L1 `languagetool:DE_CASE` — Großschreibung von Nomen und substantivierten Verben _(audience: maintainer)_
  > `Konkretes`
- L1 `lektorat §D3 protected-term-candidate` — Token 'MUST' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `MUST`
- _… 29 more D3 finding(s) at this severity (see `findings.json`)_

### `docs/de/references/specs/index.md` — 11 finding(s)

**D3** (11):

- L1 `lektorat §D3 protected-term-candidate` — Token 'Agents' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Agents`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Spec-Skill' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Spec-Skill`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Specs' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Specs`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Spec-Skill' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Spec-Skill`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Specs' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Specs`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Agents' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Agents`
- L1 `lektorat §D3 protected-term-candidate` — Token 'MUST' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `MUST`
- L1 `lektorat §D3 protected-term-candidate` — Token 'SHOULD' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `SHOULD`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Specs' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Specs`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Spec' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Spec`
- _… 1 more D3 finding(s) at this severity (see `findings.json`)_

### `docs/de/references/specs/skill-management.md` — 25 finding(s)

**D3** (25):

- L1 `lektorat §D3 protected-term-candidate` — Token 'draft' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `draft`
- L1 `lektorat §D3 protected-term-candidate` — Token 'claude-shared' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `claude-shared`
- L1 `lektorat §D3 protected-term-candidate` — Token 'Agents' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `Agents`
- L1 `lektorat §D3 protected-term-candidate` — Token 'trigger-orientierte' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `trigger-orientierte`
- L1 `lektorat §D3 protected-term-candidate` — Token 'claude-shared' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `claude-shared`
- L1 `languagetool:DE_CASE` — Großschreibung von Nomen und substantivierten Verben _(audience: maintainer)_
  > `Konkrete`
- L1 `lektorat §D3 protected-term-candidate` — Token 'MUST' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `MUST`
- L1 `lektorat §D3 protected-term-candidate` — Token 'MUST' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `MUST`
- L1 `lektorat §D3 protected-term-candidate` — Token 'MUST' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `MUST`
- L1 `lektorat §D3 protected-term-candidate` — Token 'YAML-Frontmatter' als Tippfehler gemeldet — wahrscheinlich Jargon; protected-terms-Liste fehlt. _(audience: maintainer)_
  > `YAML-Frontmatter`
- _… 15 more D3 finding(s) at this severity (see `findings.json`)_

### `docs/en/by-task.md` — 5 finding(s)

**D3** (2):

- L11 `vale:Microsoft.Semicolon` — Try to simplify this sentence. _(audience: maintainer)_
  > `;`
- L31 `vale:Microsoft.SentenceLength` — Try to keep sentences short (< 30 words). _(audience: maintainer)_
  > `When`

**D4** (3):

- L20 `vale:Microsoft.Vocab` — Verify your use of 'Author' with the A-Z word list. _(audience: maintainer)_
  > `Author`
- L22 `vale:Microsoft.Vocab` — Verify your use of 'against' with the A-Z word list. _(audience: maintainer)_
  > `against`
- L25 `vale:Microsoft.Vocab` — Verify your use of 'Author' with the A-Z word list. _(audience: maintainer)_
  > `Author`

### `docs/en/getting-started/index.md` — 1 finding(s)

**D3** (1):

- L9 `vale:Microsoft.Headings` — 'Getting Started' should use sentence-style capitalization. _(audience: maintainer, external-contributor)_
  > `Getting Started`

### `docs/en/getting-started/installation.md` — 2 finding(s)

**D4** (2):

- L49 `vale:Microsoft.Passive` — 'are discovered' looks like passive voice. _(audience: maintainer, external-contributor)_
  > `are discovered`
- L67 `vale:Microsoft.Passive` — 'was started' looks like passive voice. _(audience: maintainer, external-contributor)_
  > `was started`

### `docs/en/getting-started/nutzung.md` — 3 finding(s)

**D4** (3):

- L11 `vale:Microsoft.Passive` — 'is loaded' looks like passive voice. _(audience: maintainer, downstream-user)_
  > `is loaded`
- L28 `vale:Microsoft.Vocab` — Verify your use of 'against' with the A-Z word list. _(audience: maintainer, downstream-user)_
  > `against`
- L33 `vale:Microsoft.Passive` — 'are kept' looks like passive voice. _(audience: maintainer, downstream-user)_
  > `are kept`

### `docs/en/guides/agents-concept.md` — 7 finding(s)

**D3** (4):

- L11 `vale:Microsoft.Semicolon` — Try to simplify this sentence. _(audience: maintainer)_
  > `;`
- L45 `vale:Microsoft.Semicolon` — Try to simplify this sentence. _(audience: maintainer)_
  > `;`
- L47 `vale:Microsoft.Headings` — 'Source vs. runtime location' should use sentence-style capitalization. _(audience: maintainer)_
  > `Source vs. runtime location`
- L56 `vale:Microsoft.Semicolon` — Try to simplify this sentence. _(audience: maintainer)_
  > `;`

**D4** (3):

- L11 `vale:Microsoft.Passive` — 'are specialized' looks like passive voice. _(audience: maintainer)_
  > `are specialized`
- L18 `vale:Microsoft.Vocab` — Verify your use of 'against' with the A-Z word list. _(audience: maintainer)_
  > `against`
- L24 `vale:Microsoft.Vocab` — Verify your use of 'against' with the A-Z word list. _(audience: maintainer)_
  > `against`

### `docs/en/guides/contributing.md` — 3 finding(s)

**D3** (2):

- L14 `vale:Microsoft.Acronyms` — 'ASCII' has no definition. _(audience: external-contributor)_
  > `ASCII`
- L21 `vale:Microsoft.Acronyms` — 'ASCII' has no definition. _(audience: external-contributor)_
  > `ASCII`

**D4** (1):

- L15 `vale:Microsoft.Passive` — 'is regenerated' looks like passive voice. _(audience: external-contributor)_
  > `is regenerated`

### `docs/en/guides/development-lifecycle.md` — 36 finding(s)

**D3** (18):

- L13 `vale:Microsoft.Acronyms` — 'MVP' has no definition. _(audience: maintainer)_
  > `MVP`
- L15 `vale:Microsoft.SentenceLength` — Try to keep sentences short (< 30 words). _(audience: maintainer)_
  > `Every`
- L15 `vale:Microsoft.Semicolon` — Try to simplify this sentence. _(audience: maintainer)_
  > `;`
- L88 `vale:Microsoft.Semicolon` — Try to simplify this sentence. _(audience: maintainer)_
  > `;`
- L92 `vale:Microsoft.Headings` — '1 Vision' should use sentence-style capitalization. _(audience: maintainer)_
  > `1 Vision`
- L94 `vale:Microsoft.Acronyms` — 'MVP' has no definition. _(audience: maintainer)_
  > `MVP`
- L99 `vale:Microsoft.Acronyms` — 'SMART' has no definition. _(audience: maintainer)_
  > `SMART`
- L101 `vale:Microsoft.Headings` — '2 Plan' should use sentence-style capitalization. _(audience: maintainer)_
  > `2 Plan`
- L110 `vale:Microsoft.Acronyms` — 'MVP' has no definition. _(audience: maintainer)_
  > `MVP`
- L116 `vale:Microsoft.Headings` — '3 Design' should use sentence-style capitalization. _(audience: maintainer)_
  > `3 Design`
- _… 8 more D3 finding(s) at this severity (see `findings.json`)_

**D4** (18):

- L11 `vale:Microsoft.Passive` — 'are designed' looks like passive voice. _(audience: maintainer)_
  > `are designed`
- L13 `vale:Microsoft.Passive` — 'be revised' looks like passive voice. _(audience: maintainer)_
  > `be revised`
- L94 `vale:Microsoft.Passive` — 'is entered' looks like passive voice. _(audience: maintainer)_
  > `is entered`
- L98 `vale:Microsoft.Vocab` — Verify your use of 'Author' with the A-Z word list. _(audience: maintainer)_
  > `Author`
- L103 `vale:Microsoft.Passive` — 'is dispatched' looks like passive voice. _(audience: maintainer)_
  > `is dispatched`
- L114 `vale:Microsoft.Vocab` — Verify your use of 'against' with the A-Z word list. _(audience: maintainer)_
  > `against`
- L118 `vale:Microsoft.Passive` — 'are written' looks like passive voice. _(audience: maintainer)_
  > `are written`
- L122 `vale:Microsoft.Vocab` — Verify your use of 'Author' with the A-Z word list. _(audience: maintainer)_
  > `Author`
- L124 `vale:Microsoft.Vocab` — Verify your use of 'Author' with the A-Z word list. _(audience: maintainer)_
  > `Author`
- L132 `vale:Microsoft.Wordiness` — Consider using 'remove' instead of 'extract'. _(audience: maintainer)_
  > `extract`
- _… 8 more D4 finding(s) at this severity (see `findings.json`)_

### `docs/en/guides/project-structure.md` — 1 finding(s)

**D4** (1):

- L71 `vale:Microsoft.Passive` — 'is called' looks like passive voice. _(audience: external-contributor, maintainer)_
  > `is called`

### `docs/en/guides/skill-management.md` — 2 finding(s)

**D3** (2):

- L37 `vale:Microsoft.Acronyms` — 'ASCII' has no definition. _(audience: maintainer)_
  > `ASCII`
- L47 `vale:Microsoft.Acronyms` — 'ASCII' has no definition. _(audience: maintainer)_
  > `ASCII`

### `docs/en/guides/skills-concept.md` — 9 finding(s)

**D3** (3):

- L11 `vale:Microsoft.Semicolon` — Try to simplify this sentence. _(audience: maintainer)_
  > `;`
- L35 `vale:Microsoft.Acronyms` — 'SMART' has no definition. _(audience: maintainer)_
  > `SMART`
- L45 `vale:Microsoft.Semicolon` — Try to simplify this sentence. _(audience: maintainer)_
  > `;`

**D4** (6):

- L19 `vale:Microsoft.Vocab` — Verify your use of 'against' with the A-Z word list. _(audience: maintainer)_
  > `against`
- L20 `vale:Microsoft.Vocab` — Verify your use of 'against' with the A-Z word list. _(audience: maintainer)_
  > `against`
- L27 `vale:Microsoft.Vocab` — Verify your use of 'against' with the A-Z word list. _(audience: maintainer)_
  > `against`
- L30 `vale:Microsoft.Vocab` — Verify your use of 'against' with the A-Z word list. _(audience: maintainer)_
  > `against`
- L31 `vale:Microsoft.Vocab` — Verify your use of 'against' with the A-Z word list. _(audience: maintainer)_
  > `against`
- L45 `vale:Microsoft.Passive` — 'being added' looks like passive voice. _(audience: maintainer)_
  > `being added`

### `docs/en/guides/spec.md` — 8 finding(s)

**D3** (5):

- L11 `vale:Microsoft.Semicolon` — Try to simplify this sentence. _(audience: maintainer)_
  > `;`
- L32 `vale:Microsoft.Semicolon` — Try to simplify this sentence. _(audience: maintainer)_
  > `;`
- L59 `vale:Microsoft.Acronyms` — 'RFC' has no definition. _(audience: maintainer)_
  > `RFC`
- L77 `vale:Microsoft.Semicolon` — Try to simplify this sentence. _(audience: maintainer)_
  > `;`
- L100 `vale:Microsoft.Acronyms` — 'ASCII' has no definition. _(audience: maintainer)_
  > `ASCII`

**D4** (3):

- L32 `vale:Microsoft.Passive` — 'is allowed' looks like passive voice. _(audience: maintainer)_
  > `is allowed`
- L59 `vale:Microsoft.Passive` — 'are glossed' looks like passive voice. _(audience: maintainer)_
  > `are glossed`
- L91 `vale:Microsoft.Wordiness` — Consider using 'remove' instead of 'Extract'. _(audience: maintainer)_
  > `Extract`

### `docs/en/index.md` — 2 finding(s)

**D4** (2):

- L11 `vale:Microsoft.Passive` — 'be reused' looks like passive voice. _(audience: maintainer, downstream-user)_
  > `be reused`
- L34 `vale:Microsoft.Passive` — 'being consolidated' looks like passive voice. _(audience: maintainer, downstream-user)_
  > `being consolidated`

### `docs/en/project/index.md` — 9 finding(s)

**D3** (4):

- L56 `vale:Microsoft.Semicolon` — Try to simplify this sentence. _(audience: maintainer)_
  > `;`
- L56 `vale:Microsoft.Semicolon` — Try to simplify this sentence. _(audience: maintainer)_
  > `;`
- L75 `vale:Microsoft.Semicolon` — Try to simplify this sentence. _(audience: maintainer)_
  > `;`
- L84 `vale:Microsoft.Acronyms` — 'MUST' has no definition. _(audience: maintainer)_
  > `MUST`

**D4** (5):

- L13 `vale:Microsoft.Passive` — 'are invoked' looks like passive voice. _(audience: maintainer)_
  > `are invoked`
- L15 `vale:Microsoft.Passive` — 'is untouched' looks like passive voice. _(audience: maintainer)_
  > `is untouched`
- L84 `vale:Microsoft.Passive` — 'be recorded' looks like passive voice. _(audience: maintainer)_
  > `be recorded`
- L88 `vale:Microsoft.Passive` — 'being done' looks like passive voice. _(audience: maintainer)_
  > `being done`
- L97 `vale:Microsoft.Passive` — 'are invoked' looks like passive voice. _(audience: maintainer)_
  > `are invoked`

### `docs/en/references/specs/agent-management.md` — 23 finding(s)

**D3** (22):

- L9 `vale:Microsoft.Headings` — 'Agent Authoring' should use sentence-style capitalization. _(audience: maintainer)_
  > `Agent Authoring`
- L21 `vale:Microsoft.Headings` — 'Goals and Non-Goals' should use sentence-style capitalization. _(audience: maintainer)_
  > `Goals and Non-Goals`
- L42 `vale:Microsoft.Acronyms` — 'MUST' has no definition. _(audience: maintainer)_
  > `MUST`
- L42 `vale:Microsoft.Acronyms` — 'ASCII' has no definition. _(audience: maintainer)_
  > `ASCII`
- L43 `vale:Microsoft.Acronyms` — 'MUST' has no definition. _(audience: maintainer)_
  > `MUST`
- L44 `vale:Microsoft.Acronyms` — 'MUST' has no definition. _(audience: maintainer)_
  > `MUST`
- L45 `vale:Microsoft.Acronyms` — 'MUST' has no definition. _(audience: maintainer)_
  > `MUST`
- L46 `vale:Microsoft.Acronyms` — 'MUST' has no definition. _(audience: maintainer)_
  > `MUST`
- L47 `vale:Microsoft.Acronyms` — 'MUST' has no definition. _(audience: maintainer)_
  > `MUST`
- L48 `vale:Microsoft.Acronyms` — 'MUST' has no definition. _(audience: maintainer)_
  > `MUST`
- _… 12 more D3 finding(s) at this severity (see `findings.json`)_

**D4** (1):

- L82 `vale:Microsoft.Passive` — 'is set' looks like passive voice. _(audience: maintainer)_
  > `is set`

### `docs/en/references/specs/index.md` — 8 finding(s)

**D3** (5):

- L15 `vale:Microsoft.Semicolon` — Try to simplify this sentence. _(audience: maintainer)_
  > `;`
- L22 `vale:Microsoft.Semicolon` — Try to simplify this sentence. _(audience: maintainer)_
  > `;`
- L24 `vale:Microsoft.Headings` — 'RFC 2119 conventions' should use sentence-style capitalization. _(audience: maintainer)_
  > `RFC 2119 conventions`
- L24 `vale:Microsoft.Acronyms` — 'RFC' has no definition. _(audience: maintainer)_
  > `RFC`
- L26 `vale:Microsoft.Acronyms` — 'RFC' has no definition. _(audience: maintainer)_
  > `RFC`

**D4** (3):

- L15 `vale:Microsoft.Passive` — 'is maintained' looks like passive voice. _(audience: maintainer)_
  > `is maintained`
- L22 `vale:Microsoft.Passive` — 'being added' looks like passive voice. _(audience: maintainer)_
  > `being added`
- L36 `vale:Microsoft.Passive` — 'be flagged' looks like passive voice. _(audience: maintainer)_
  > `be flagged`

### `docs/en/references/specs/skill-management.md` — 16 finding(s)

**D3** (13):

- L9 `vale:Microsoft.Headings` — 'Skill Authoring' should use sentence-style capitalization. _(audience: maintainer)_
  > `Skill Authoring`
- L24 `vale:Microsoft.Headings` — 'Goals and Non-Goals' should use sentence-style capitalization. _(audience: maintainer)_
  > `Goals and Non-Goals`
- L43 `vale:Microsoft.Acronyms` — 'MUST' has no definition. _(audience: maintainer)_
  > `MUST`
- L43 `vale:Microsoft.Acronyms` — 'ASCII' has no definition. _(audience: maintainer)_
  > `ASCII`
- L44 `vale:Microsoft.Acronyms` — 'MUST' has no definition. _(audience: maintainer)_
  > `MUST`
- L45 `vale:Microsoft.Acronyms` — 'MUST' has no definition. _(audience: maintainer)_
  > `MUST`
- L46 `vale:Microsoft.Acronyms` — 'MUST' has no definition. _(audience: maintainer)_
  > `MUST`
- L47 `vale:Microsoft.Acronyms` — 'MUST' has no definition. _(audience: maintainer)_
  > `MUST`
- L48 `vale:Microsoft.Acronyms` — 'MUST' has no definition. _(audience: maintainer)_
  > `MUST`
- L49 `vale:Microsoft.Acronyms` — 'MUST' has no definition. _(audience: maintainer)_
  > `MUST`
- _… 3 more D3 finding(s) at this severity (see `findings.json`)_

**D4** (3):

- L43 `vale:Microsoft.Passive` — 'be authored' looks like passive voice. _(audience: maintainer)_
  > `be authored`
- L70 `vale:Microsoft.Passive` — 'are documented' looks like passive voice. _(audience: maintainer)_
  > `are documented`
- L74 `vale:Microsoft.Passive` — 'be required' looks like passive voice. _(audience: maintainer)_
  > `be required`

_(Suggestion bucket truncated in `summary.md`; full inventory in `findings.json`.)_

