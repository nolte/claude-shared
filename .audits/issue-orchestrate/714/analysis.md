---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "714"
classification: "spec-change"
secondary-classes: [docs]
route: "direct"
status: approved
created: "2026-11-11"
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #714 — Encode 'fix small in-scope findings directly, don't file follow-up issues' in issue-orchestrate and the issue-orchestration spec
- **Labels**: enhancement, spec, skills
- **Prior art checked**: spec/project/issue-batch-integration/en.md:114 (§F finding triage, group rule), skills/issue-batch-orchestrate/references/finding-triage.md, spec/project/defect-class-guards/en.md:52, spec/claude/dispatch-brief/en.md

## Classification

- **Primary class**: spec-change — **Secondary**: docs
- **Rationale**: Neue normative Regel in spec/project/issue-orchestration/ plus Skill-Anwendung.
- **Requirements gate**: Operator-Override 2026-11-11 (Issue trägt Vorschlag in 5 Punkten, Akzeptanzkriterien und Vorlage §F); kein requirements-elicit.
- **Asserted cause verified**:
  - confirmed: kein Einzel-Issue-Triage-Pendant; `skills/issue-orchestrate/SKILL.md:239` „becomes its own referenced issue“.
  - zusätzlich gefunden (nicht im Issue): `spec/project/issue-orchestration/en.md:392` MUSS Class-Sweep-Rest (`Repaired < Hits`) als eigene Issues filen — muss mit der Regel abgestimmt werden.
  - refuted (Punkt 5): `spec/claude/dispatch-brief/en.md` regelt nur die Refutations-Klausel (Z. 24 Non-Goal: restlicher Brief-Inhalt), kein „nur auflisten“-Default → keine Änderung, höchstens Querverweis.
  - Token-Budget: issue-orchestrate Body ~4496 est. Tokens (Warnband 4500, Cap 5000) → Regeltext in references/, SKILL.md netto nicht wachsen; issue-batch-orchestrate ~4004.

## Scope

- **In scope**: Spec-Regel (EN kanonisch + DE) inkl. Checklisten-AC und Abgleich mit Class-Sweep-MUST; issue-orchestrate SKILL.md (netto-neutral) + neue references/finding-triage.md + dispatch-matching.md Brief-Klausel; je eine Zeile backlog-delivery-orchestrate / issue-backlog-partition; Querverweis issue-batch-orchestrate; skill-review grün.
- **Out of scope**: defect-class-guards bleibt inhaltlich (große Guards → eigenes Issue); Löschen des Consumer-Memory-Eintrags (Consumer-Repo).

## Route

- **Decision**: direct — ein Ergebnis, ein PR-Strang.

## Work packages

### P1 — Spec issue-orchestration: Finding-Triage für Einzel-Issue-Läufe
- **AC**: Neuer Requirement-Block (fix directly bei (a) Touch-Surface oder Same-Pattern-Geschwister, (b) keine Operator-Entscheidung, Bounded Verdict/Plan bleibt gültig, (c) reproduziert; sonst eigenes Issue; „neues Issue für reproduzierten kleinen In-Scope-Fix ist falsches Ergebnis“); Class-Sweep-MUST (en.md:392) so umformuliert, dass Geschwister, die (a)–(c) erfüllen, repariert werden und nur der Rest gefiled wird; AC-Checklistenpunkt; DE synchron.
- **Specialist**: skill `nolte-shared:spec` (Spec-Authoring/Übersetzung)
- **Depends on**: none

### P2 — issue-orchestrate wendet die Regel an
- **AC**: references/finding-triage.md (Regel-Anwendung, Brief-Klausel „fix small related findings directly and list them“, Abgrenzung zu großen Guards); SKILL.md Op. 5 + Op. 6 verweisen darauf, Body netto ≤ heute; dispatch-matching.md Brief-Abschnitt; validate_skills ohne neuen Befund.
- **Specialist**: nolte-claude-dev:claude-plugin-developer
- **Depends on**: P1

### P3 — Lanes: backlog-delivery-orchestrate / issue-backlog-partition / issue-batch-orchestrate
- **AC**: je eine Zeile „Lanes wenden die Triage an; die Partition wächst nicht durch In-Lane-Kleinfunde“; Querverweis in issue-batch-orchestrate auf die Einzelregel; Descriptions unverändert (Headroom knapp).
- **Specialist**: nolte-claude-dev:claude-plugin-developer
- **Depends on**: P1

### P4 — Verifikation
- **AC**: skill-review für issue-orchestrate ohne Critical/Warning; task lint/test grün; Vale grün auf Spec EN.
- **Specialist**: nolte-claude-dev:skill-review
- **Depends on**: P2, P3

## Dependency ordering

P1 → (P2, P3) → P4

## Risks

- Token-Cap issue-orchestrate → Detail in references/.
- Regel zu weit gefasst (große Fixes laufen „klein“ rein) → Bedingung (b) bindet an Plan/Verdict; Größe nicht in Zeilen, sondern „keine Operator-Entscheidung, Plan bleibt gültig“ wie §F.

## Open questions

none

## Dispatch log

- P1 → skill nolte-shared:spec (in-session): Triage-Regel + Class-Sweep-Abgleich + AC, EN/DE, Vale grün.
- P2/P3 → nolte-claude-dev:claude-plugin-developer: finding-triage.md, SKILL.md netto −4 Zeichen (4494 Tokens), dispatch-matching/closeout/Template, Lane-Zeilen; validate_skills unverändert.
- P4 → skill nolte-claude-dev:skill-review (eingeschränkt auf geänderte Teile): 1 Warning ("never a guard" widersprach defect-class-guards G1) → behoben; keine offenen Befunde.
