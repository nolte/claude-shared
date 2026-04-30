# Lokale Release-Skill-Schicht

Status: draft

## Context

Zwei bestehende Specs rahmen den Release-Ablauf im Portfolio ein. `release-automation` definiert, **wie** der Draft → Published-Übergang abläuft (ein `workflow_dispatch`-getriggertes `release-publish.yml`, das einen `release-drafter`-Draft konsumiert) und verbietet Body-Edits innerhalb dieses Workflows explizit: laut §Operational contract **MÜSSEN** Body-Edits via `gh release edit` außerhalb des Workflows erfolgen oder über `release-drafter`-Re-Runs. `release-notes-audience-analysis` definiert, **was** der Body enthalten soll, indem die Audience-Identification-Methode auf den bounded context "Release Notes eines GitHub Releases" angewendet wird. Keine der beiden Specs deckt die operative Schicht ab, die im Terminal des Operators sitzt: ein lokales Verfahren, das den offenen Draft liest, dessen Body um projekt-kontext-bezogene Sections aus dem Audience-Artefakt und der Repo-Architektur anreichert, plus ein separates lokales Verfahren, das alle Pre-Publish-Gates validiert, bevor `release-publish.yml` dispatched wird. Diese Spec definiert genau diese Schicht als zwei wiederverwendbare Skills, die aus diesem Plugin ausgeliefert werden, sodass jedes adoptierende Repo denselben lokalen Einstiegspunkt für die Release-Entscheidung erhält, ohne den Audit-Trail des Workflows zu umgehen.

## Goals

- Einen lokalen Skill (Skill A) bereitstellen, der den offenen `release-drafter`-Draft um projekt-kontext-bezogene Sections aus Projekttyp und Audience-Artefakt anreichert, idempotent bei Re-Runs.
- Einen lokalen Skill (Skill B) bereitstellen, der jedes Pre-Publish-Gate lokal validiert und `release-publish.yml` via `gh workflow run` dispatched, niemals `gh release edit --draft=false` direkt.
- Die Projekttyp-Taxonomie wiederverwenden, die `github-issue-templates-apply` bereits etabliert hat (Claude-Plugin, Python-Anwendung, Python-Bibliothek, Node-/TypeScript, CLI-Tool, reines Doku-Repo), damit Skill-Verhalten portfolio-weit konsistent bleibt.
- Kuratierten Inhalt am Audience-Artefakt aus `release-notes-audience-analysis` verankern, sodass jede vom Skill geschriebene Section auf eine dokumentierte Audience-Anforderung zurückführbar ist.
- Portfolio-wiederverwendbar bleiben: jedes Repo, das `release-drafter.yml` und `release-publish.yml` ausliefert, kann diese Skill-Schicht ohne weitere Repo-Konfiguration adoptieren — über das vorhandene Audience-Artefakt hinaus.

## Non-Goals

- Ersatz für `release-drafter`. Die Conventional-Commits-Kategorisierung, Versions-Ableitung und Tag-Erzeugung bleiben Workflow-Aufgabe.
- Ersatz für `release-publish.yml`. Der Workflow ist und bleibt der Audit-Trail-Punkt für den Draft → Published-Übergang.
- Direktes Aufrufen von `gh release edit --draft=false` aus einem lokalen Skill. Verboten durch `release-automation` und hier explizit out of scope; der einzige zulässige Publish-Pfad ist der Workflow-Dispatch.
- Generieren von Release Notes aus dem Nichts. Skill A reichert vorhandenen `release-drafter`-Output an; er ersetzt ihn nicht.
- Versionierungs-Policy. Wird aus der `release-drafter`-Konfiguration in `nolte/gh-plumbing:.github/commons-release-drafter.yml` geerbt.
- Post-Publish-Operationen (`release-cd-refresh-master.yml`, Packaging-Workflows). Sind nachgelagert zu `release-publish.yml`.
- Audiences identifizieren. `release-notes-audience-analysis` (und ihre Eltern-Spec `audience-identification`) sind dafür zuständig; Skill A konsumiert das Artefakt, erfindet niemals Einträge.

## Requirements

### Skill-Aufteilung und gemeinsame Form

- **MUSS [MUST]** als zwei eigenständige Skills unter `skills/<name>/SKILL.md` gemäß `skill-management` ausgeliefert werden, nicht als ein kombinierter Skill: ein Curation-Skill (Skill A) und ein Publish-Trigger-Skill (Skill B). Die Aufteilung ist gerechtfertigt, weil die zwei Operationen unterschiedliche Blast-Radien haben (Body-Edit ist reversibel; Workflow-Dispatch löst eine extern sichtbare Publish-Kette aus), unterschiedliche Precondition-Surfaces (Audience-Artefakt vs. Version-Bearing-File-Alignment) und natürlicherweise unterschiedliche Punkte der Release-Entscheidung bedienen (Review-and-Shape vs. Commit-to-Ship).
- **MUSS [MUST]** in beiden Fällen die Projekttyp-Detection-Signale aus `github-issue-templates-apply` befolgen: `.claude-plugin/plugin.json` für Claude-Plugin, `pyproject.toml`-Form für Python-Anwendung vs. -Bibliothek, `package.json` für Node/TypeScript, deklarierter CLI-Entry für CLI-Tool, `mkdocs.yml` / Vergleichbares für reines Doku-Repo.
- **KANN [MAY]** ein Repo-spezifisches Override unter `.github/release-skill-layer.yml` unterstützen, wenn die Auto-Detection danebenliegt (Hybrid-Repos, Monorepos mit mehreren Package-Roots).

### Skill A: Draft-Notes-Kuratierung

#### Operativer Kontrakt

- **MUSS [MUST]** den offenen `release-drafter`-Draft auf dem Default-Branch (`develop`) via `gh release list --json isDraft,tagName,targetCommitish,createdAt` identifizieren und auf den Draft filtern, dessen `targetCommitish` `develop` (oder der deklarierte Default-Branch) ist.
- **MUSS [MUST]** die Operation verweigern, wenn kein Draft existiert, mehrere Drafts mit mehrdeutigen Tags vorhanden sind, oder der Draft-Tag vom Default-Branch nicht erreichbar ist; jeden Fehlerfall mit einem konkreten Remediation-Pfad benennen.
- **MUSS [MUST]** das Audience-Artefakt aus `release-notes-audience-analysis` konsumieren (typisch `AUDIENCES.md`, eine "Audiences"-Section in `README.md`, oder ein dediziertes `docs/release-audiences.md`); wenn kein Audience-Artefakt vorhanden ist, den `audience-identify`-Skill dispatchen, bevor weitergearbeitet wird.
- **DARF NICHT [MUST NOT]** Audience-Einträge inline erfinden; die Spec verbietet das. Fehlende Audiences werden im kuratierten Body als einzelner Open-Question-Hinweis vermerkt, nicht als fabrizierter Inhalt.
- **MUSS [MUST]** projekt-kontext-bezogene Sections aus dem erkannten Projekttyp ableiten. Konkrete Bündel:
  - **Claude-Code-Plugin**: `Skills changed` (hinzugefügt / umbenannt / entfernt unter `skills/`), `Agents changed` (unter `agents/`), `Specs changed` (unter `spec/`), `Breaking changes for plugin consumers` (umbenannte Slash-Commands, entfernte Skills, Plugin-Manifest-Versionssprung), `Required plugin re-install` (nur wenn Skill-/Agent-Artefakte verschoben oder umbenannt wurden).
  - **Python-Anwendung** (mit Hardware-Variante gemäß `github-issue-templates-apply` references): `Hardware support` (Änderungen an unterstützten Geräten, Sensoren, Firmware-Version-Constraints), `Runtime requirements` (Python-Version, OS, Container-Base-Image), `Migration notes for operators` (Konfig-Änderungen, brechende Umbenennungen von Environment-Variablen).
  - **Python-Bibliothek**: `API changes`, `Compatibility breaks` (semver-major-Änderungen), `Deprecations` (mit Removal-Target).
  - **Node-/TypeScript-Bibliothek oder -App**: `API changes`, `Compatibility breaks`, `Runtime requirements` (Node-Version, Package-Manager-Pin), wenn das Package sie deklariert.
  - **CLI-Tool**: `Command-line changes` (neue Commands, umbenannte Flags), `Flag deprecations`, `Default-value changes`.
  - **Reines Doku-Repo**: `Restructured pages` (Pfad-Verschiebungen), `Removed pages`, `New translations`.
- **SOLLTE [SHOULD]** jeden Section-Eintrag auf einen konkreten Commit-SHA, eine PR-Nummer oder einen berührten Pfad zurückführen, sodass Reviewer ohne erneute `git log`-Wanderung validieren können.
- **MUSS [MUST]** die geplante Anreicherung dem Nutzer vor jedem Schreibvorgang offenlegen (Diff-Form mit existierendem Draft-Body, Ergänzungen und Marker-Grenzen), und den Schreibvorgang bis zur Bestätigung blockieren.
- **MUSS [MUST]** den angereicherten Body via `gh release edit <tag> --notes <body>` schreiben. **DARF NICHT [MUST NOT]** `gh release edit --draft=false` aufrufen, niemals; dieser Pfad ist `release-publish.yml` vorbehalten.

#### Re-Run-Sicherheit und Marker

- **MUSS [MUST]** die Projekt-Kontext-Anreicherung in stabile HTML-Kommentar-Marker einrahmen, exakt: `<!-- release-skill-layer:project-context-start -->` und `<!-- release-skill-layer:project-context-end -->`. Die Marker sind der Kontrakt, der Re-Runs erlaubt, in-place zu erkennen und zu aktualisieren.
- **MUSS [MUST]** existierende Marker bei jedem Lauf erkennen und den Inhalt zwischen ihnen ersetzen; **DARF NICHT [MUST NOT]** ein zweites Marker-Paar erzeugen, außerhalb der Marker anhängen oder Sections duplizieren.
- **DARF NICHT [MUST NOT]** Inhalt außerhalb der Marker-Grenzen bei Re-Runs verändern. `release-drafter` besitzt den Body oberhalb der Marker; der Skill besitzt nur den Anreicherungs-Block.
- **MUSS [MUST]** nach jedem Schreibvorgang verifizieren, dass der resultierende Body weiterhin genau ein Marker-Paar enthält; Erfolg verweigern, wenn nicht.

#### Inhalts-Platzierung

- **MUSS [MUST]** den Anreicherungs-Block **unterhalb** der `release-drafter`-Conventional-Commits-Sections platzieren, getrennt durch einen klaren Divider (eine horizontale Linie plus eine Level-2-Heading wie `## Project context` ist die empfohlene Form).
- **SOLLTE [SHOULD]** eine `## Audiences served`-Subsection an den Anfang des Anreicherungs-Blocks setzen, wenn das Audience-Artefakt primäre Audiences listet, und jede primäre Audience auf die Sections des kuratierten Bodys mappen, die ihre Content-Dimensions gemäß `release-notes-audience-analysis` adressieren.
- **KANN [MAY]** eine abschließende `## Open questions`-Subsection innerhalb des Anreicherungs-Blocks enthalten, wenn Audience-Coverage-Lücken erkannt wurden; Lücken sind Inhalte, die der Skill produziert hätte, wenn das Audience-Artefakt vollständiger gewesen wäre.

### Skill B: Release-Publish-Trigger

#### Pre-Dispatch-Validierung

- **MUSS [MUST]** lokal jedes Gate aus `release-automation` §Pre-publish verification vor dem Dispatch validieren:
  - genau ein offener `release-drafter`-Draft existiert auf `develop`;
  - der Draft-Tag ist vom aktuellen `develop`-Tip erreichbar;
  - jedes Version-Bearing File aus `release-automation` §Version-bearing files (Default-Tabelle pro Repo-Typ oder Override unter `.github/release-automation.yml`) entspricht dem Target-Tag am `target_commitish` des Drafts unter der deklarierten Transformation;
  - der Alignment-Commit auf `develop` (sofern vorhanden) hat den Subject-Prefix `chore(release): <tag>`;
  - jeder Required Status Check auf dem HEAD-Commit von `develop` ist `SUCCESS`;
  - `.github/workflows/release-publish.yml` existiert im Repo.
- **MUSS [MUST]** den Dispatch verweigern, wenn eines der obigen Gates versagt. Die Verweigerungs-Nachricht **MUSS [MUST]** das gescheiterte Gate benennen und auf den Remediation-Pfad zeigen (`chore(release): <tag>`-PR für Fallback-Alignment, `release-drafter`-Re-Run für fehlenden Draft, etc.).
- **MUSS [MUST]** den validierten Stand dem Nutzer präsentieren (Tag, Target-SHA, Version-Bearing-File-Diff-Summary, Audience-Coverage-Summary falls Skill A auf dem Draft gelaufen ist), und vor dem Dispatch eine explizite Bestätigung verlangen.

#### Dispatch

- **MUSS [MUST]** `release-publish.yml` via `gh workflow run release-publish.yml --ref develop -f tag=<tag>` dispatchen; das `tag`-Input ist gemäß `release-automation` §Operational contract verpflichtend, unabhängig davon, wie viele Drafts offen sind.
- **DARF NICHT [MUST NOT]** `gh release edit --draft=false`, `gh api -X PATCH /repos/.../releases/<id>` mit `draft=false` oder irgendeine andere Body-Operation aufrufen, die den Draft-Status außerhalb des Workflows kippt. Es gibt keinen Admin-Override-Pfad; das ist im Geist identisch zur `enforce_admins: true`-Regel von `pull-request-merge`.
- **SOLLTE [SHOULD]** einen `--dry-run`-Modus unterstützen, der jede Precondition-Validierung ausführt und mit `dry_run=true`-Workflow-Input gemäß `release-automation` §Operational contract dispatched.
- **SOLLTE [SHOULD]** nach dem Dispatch verifizieren, dass der Workflow-Run gestartet ist (`gh run list --workflow=release-publish.yml --limit 1 --json status,conclusion,url`), und die Run-URL plus den aktuellen Status melden; **DARF NICHT [MUST NOT]** außerhalb eines expliziten Wait-Modes bis zum Abschluss pollen (entspricht dem Wait-Mode-Kontrakt von `pull-request-merge`).

#### Failure-Routing

- **MUSS [MUST]**, wenn eine Pre-Dispatch-Validierung fehlschlägt, weil ein Required Check auf `develop` rot ist, an die `workflow-health`-Triage routen statt den Dispatch zu retryen, selbes Protokoll wie `pull-request-merge` Schritt 4.
- **MUSS [MUST]**, wenn der Workflow-Run nach erfolgreichem Dispatch selbst fehlschlägt, an `release-automation` §Observability and audit und `workflow-health` delegieren statt einen zweiten Dispatch aus dem Skill heraus zu versuchen.

### Komposition

- **MUSS [MUST]** zulassen, dass Skill A unabhängig von Skill B läuft (Curation ohne Publish) und Skill B auf einem Draft läuft, der nicht angereichert wurde (Publish ohne Curation). Keiner der beiden Skills ist eine Precondition des anderen in dieser Spec; der Operator entscheidet die Reihenfolge.
- **SOLLTE [SHOULD]**, wenn Skill B einen Draft ohne `release-skill-layer:project-context-start`-Marker erkennt, einen non-blocking Hinweis zeigen und anbieten, Skill A zuerst zu dispatchen; der Operator **KANN [MAY]** ohne Curation fortfahren.
- **KANN [MAY]** Skill A → Skill B in einer einzelnen Operator-Anfrage verketten, wenn der Operator "kuratieren und publishen" sagt; die Kette sind zwei sequenzielle Skill-Aufrufe, kein dritter kombinierter Skill.

## Acceptance Criteria

- [ ] Zwei Skills existieren unter `skills/release-notes-curate/` und `skills/release-publish-trigger/` (oder äquivalente ASCII-kebab-case-Namen), ausgeliefert vom `nolte-shared`-Plugin; jeder hat einen bestandenen `skill-review`-Plan unter `.audits/skill-review/` zum Adoptionszeitpunkt.
- [ ] Das Frontmatter-`description` jedes Skills listet konkrete Trigger-Phrasen (EN + DE) und explizite Anti-Trigger gegen die Workflows, die er nicht ersetzt.
- [ ] Beide Skills erkennen den Projekttyp über dieselben Signale wie `github-issue-templates-apply`, verifizierbar über die Detection-Sektion jeder `SKILL.md`.
- [ ] Skill A konsumiert das `release-notes-audience-analysis`-Artefakt, wenn vorhanden, und dispatcht `audience-identify`, wenn nicht; verifizierbar im Operator-Transcript auf einem frischen Repo.
- [ ] Skill As Anreicherung ist in jedem produzierten Draft-Body in `<!-- release-skill-layer:project-context-start -->`- und `<!-- release-skill-layer:project-context-end -->`-Marker eingerahmt.
- [ ] Ein Re-Run von Skill A auf einem bereits kuratierten Draft erzeugt keinen Diff im Anreicherungs-Block, wenn keine neuen Commits seit dem letzten Lauf gelandet sind; die Marker sind genau einmal vorhanden.
- [ ] Skill A verändert nie Inhalt außerhalb seiner Marker-Grenzen, verifizierbar durch Diff des Bodys vor und nach einem Lauf.
- [ ] Skill B verweigert den Dispatch, wenn irgendein `release-automation` §Pre-publish verification-Gate versagt, und benennt das gescheiterte Gate wörtlich.
- [ ] Skill Bs Run-Transcript zeigt `gh workflow run release-publish.yml ...` als einzige Mutation; ein Grep des Transcripts auf `gh release edit --draft=false` findet keinen Treffer.
- [ ] Skill B meldet die Workflow-Run-URL nach dem Dispatch und zeigt den aktuellen Run-Status, ohne bis zum Abschluss zu pollen (außer der Operator hat sich für Wait-Mode entschieden, analog zu `pull-request-merge`).
- [ ] `release-automation` §Non-Goals (oder §Relationship to other specs) verlinkt diese Spec als lokales Skill-Pendant für Body-Curation und Dispatch-Ergonomie.
- [ ] Die Acceptance-Criteria-Zeile von `release-notes-audience-analysis` "Reviewer kann Primary-Audience-Coverage vor `release-publish.yml`-Dispatch verifizieren" wird durch die `## Audiences served`-Subsection von Skill A erfüllt.

## Open Questions

- Sollen Skill A und Skill B einen gemeinsamen "Release-Context-Loader"-Helper (Projekttyp + Audience-Artefakt + offener Draft) in `references/release-context.md` extrahieren oder unabhängig bleiben? Das Duplikations-Risiko ist real, aber klein (≈40 Zeilen); nach erstem Adoptions-Pärchen neu bewerten.
- Sollen Pre-Release-Tags (`v0.2.0-rc.1`, `v0.2.0-beta.3`) ein anderes Projekt-Kontext-Bündel erhalten als stabile Releases (zum Beispiel eine "Release-Candidate Testing Checklist"-Section, die auf stabilen Tags nicht erscheint)? Auf den ersten Pre-Release im Portfolio verschieben.
- Wie verhält sich Skill A, wenn `release-drafter` nach Skill A erneut läuft und den Body überschreibt? Das Marker-Paar sollte überleben, weil `release-drafter` nur die Conventional-Commits-Sections oberhalb des Dividers generiert, aber ein realer Test gegen `nolte/gh-plumbing`s `reusable-release-drafter.yml` ist nötig, um zu bestätigen, dass der Marker-Block nicht entfernt wird; als `workflow-health`-Open-Item nachhalten.
- Soll Skill Bs `--dry-run`-Modus zusätzlich einen "would-publish"-Kommentar in den Draft-Body schreiben, damit er reviewbar wird, oder strikt seitenwirkungsfrei bleiben? Seitenwirkungsfrei ist der sicherere Default; revisited, wenn Operatoren den Kommentar nachfragen.
- Soll die Tabelle der Projekt-Kontext-Bündel pro Repo-Erweiterungen (ein HACS-Integrations-spezifisches Bündel, ein OCI-Image-spezifisches Bündel) inline in dieser Spec leben, in `references/<project-type>-bundles.md` neben dem Curate-Skill, oder in einer separaten `release-skill-layer-bundles`-Spec? Aufschieben, bis ein dritter Projekttyp eine Auslagerung rechtfertigt.
- Wenn das Audience-Artefakt und der auto-detektierte Projekttyp uneinig sind (Audience-Artefakt listet "Downstream-Python-Integratoren", aber das Repo wird als Claude-Plugin erkannt), wer hat Vorrang? Tendenz zum Audience-Artefakt, weil es das menschlich bestätigte Signal ist, aber den Konflikt in der `## Open questions`-Subsection des kuratierten Bodys vermerken.
