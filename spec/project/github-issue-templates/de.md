# GitHub-Issue-Templates

Status: draft

## Context

GitHub-Repositorys im nolte-Portfolio decken sehr unterschiedliche Projekttypen ab — Claude-Code-Plugins (Skills, Agents, Specs), Python-Anwendungen (zum Beispiel kamerplanter), CLIs, Bibliotheken, reine Dokumentations-Repos. Ein einziges generisches "bug report"-/"feature request"-Template liefert Triage und Beitragenden zu wenig Kontext: Ein Bug in einem Claude-Plugin braucht die Plugin-Version und den betroffenen Skill-Namen; ein Bug in kamerplanter braucht das Kamera-Modell, die Firmware-Version und den fehlschlagenden Pflanzschritt. Ohne projektspezifische Fragen landen Issues unterspezifiziert und der Triage-Aufwand steigt.

Die `project-structure`-Spec lässt diese Lücke explizit offen: Community-Health-Dateien (Issue-Templates, CODEOWNERS) sind noch nicht vorgeschrieben. Diese Spec schließt die Issue-Template-Hälfte dieser Lücke und definiert eine Methodik — kein fixes Template — die ein nachgelagerter Skill auf ein beliebiges Repo anwenden kann, um die für den Projekttyp passenden Templates zu erzeugen.

## Goals

- Wiederholbares Verfahren definieren, um projektspezifische Issue-Templates aus dem Projekttyp und dem Audience-Profil eines Repos abzuleiten.
- Eine Mindestbasis festlegen (welche Template-Arten jedes Repo ausliefern MUSS [MUST]) und eine strukturierte Möglichkeit, projektspezifische Felder darüber hinaus zu ergänzen.
- Auf GitHub Issue Forms (YAML) standardisieren, damit Triage-Daten strukturiert, validiert und abfragbar sind, statt Fließtext.
- Genug Detail bereitstellen, damit ein Skill Templates für ein frisches Repo scaffolden und Templates für ein bestehendes Repo inkrementell aktualisieren kann, ohne dass ein Mensch jede Datei einzeln autort.
- Im Einklang mit der `audience-identification`-Spec bleiben — Issue-Templates sind ein Dokumentationsartefakt, das auf identifizierte Zielgruppen (Reporter, Triager, Maintainer) gerichtet ist.

## Non-Goals

- Pull-Request-Templates. Dafür ist `pull-request-workflow` zuständig.
- Konkrete Templates für jeden denkbaren Projekttyp autoren. Diese Spec definiert die *Methode*; die Templates selbst werden je Repo scaffoldet.
- Discussion-Templates (`.github/DISCUSSION_TEMPLATE/`). Out of Scope; kann eine Folge-Spec werden.
- Lokalisierung der Issue-Templates. Die GitHub-Issue-UI ist in der Praxis englisch; Templates bleiben unabhängig von der Dokumentationssprache des Repos auf Englisch.
- CODEOWNERS, SECURITY.md, SUPPORT.md. Werden separat unter den Open Questions von `project-structure` geführt.

## Requirements

### Ablage und Format

- **MUSS [MUST]** jedes Issue-Template unter `.github/ISSUE_TEMPLATE/` im Repo-Root ablegen.
- **MUSS [MUST]** GitHub Issue Forms (`.yml`, Top-Level-Schlüssel `name`, `description`, `body`, optional `title`, `labels`, `assignees`, `projects`, `type`) für jedes Template verwenden, das strukturierte Information abfragt. Freiform-Markdown-Templates (`.md`) sind rein informativen Stubs vorbehalten und **SOLLTEN NICHT [SHOULD NOT]** sonst eingesetzt werden.
- **MUSS [MUST]** eine `.github/ISSUE_TEMPLATE/config.yml` mit mindestens `blank_issues_enabled: false` enthalten, sofern der Projekttyp Blank-Issues nicht explizit erlaubt.
- **MUSS [MUST]** alle Template-Inhalte in Englisch halten, unabhängig von der Dokumentationssprache des Repos, weil die GitHub-Issue-UI nicht übersetzt.

### Basis-Templates

Jedes Repo **MUSS [MUST]** mindestens ausliefern:

- **`bug_report.yml`** — erfasst beobachtetes vs. erwartetes Verhalten, Reproduktionsschritte, Umgebung.
- **`feature_request.yml`** — erfasst die vorgeschlagene Änderung, das dahinterliegende User-Bedürfnis und die geprüften Alternativen.

Repos **SOLLTEN [SHOULD]** weitere Templates nur ergänzen, wenn die Audience-Analyse oder der Projekttyp sie tragend macht. Häufige Ergänzungen:

- `documentation.yml` — für Repos, deren primäres Liefer-Artefakt Dokumentation ist oder deren Doku schwer wiegt.
- `question.yml` — nur wenn GitHub Discussions nicht aktiv sind; sonst über `config.yml` an Discussions weiterleiten.
- `chore.yml` / `maintenance.yml` — für Repos mit häufigen Dependency- oder Housekeeping-Issues.

### Projekttyp-getriebene Ableitung

Ein Template-erzeugender Skill **MUSS [MUST]** dieses Ableitungsverfahren in der angegebenen Reihenfolge ausführen:

1. **Projekttyp identifizieren.** Das Repository inspizieren und klassifizieren. Vorgeschlagene Signale (nicht abschließend):
   - Claude-Code-Plugin → `.claude-plugin/plugin.json` vorhanden, `skills/` und/oder `agents/` vorhanden.
   - Python-Anwendung → `pyproject.toml` mit Anwendungs-Entrypoint, ohne Bibliotheks-Distributions-Metadaten.
   - Python-Bibliothek → `pyproject.toml` mit deklariertem distributablen Paket.
   - Node-/TypeScript-Bibliothek oder -App → `package.json` mit `main` / `exports` (Bibliothek) versus `bin` / `scripts.start` (App).
   - CLI-Tool → deklarierter CLI-Entrypoint in `pyproject.toml` / `package.json` / `Cargo.toml`.
   - Reines Doku-Repo → `mkdocs.yml`, `docusaurus.config.*` oder Vergleichbares vorhanden, kein Anwendungscode.
2. **Audience-Profil auflösen.** Existiert bereits ein Audience-Artefakt nach `audience-identification`, dieses lesen; sonst zuerst den `audience-identify`-Skill auf das Repo anwenden. Issue-Templates werden für die *Reporter*- und die *Triager*-Audience geschrieben; beide müssen identifiziert sein.
3. **Triage-Fragen ableiten.** Für jedes Basis-Template plus etwaige projekttyp-spezifische Zusätze die Fragen auflisten, die ein Triager innerhalb von fünf Minuten nach Eingang des Issues stellen wird. Diese Fragen werden zu Pflichtfeldern. Beispiele:
   - Claude-Plugin-Bug: welcher Skill oder Agent, Plugin-Version, Claude-Code-Version, Kommando-Transkript.
   - Python-Anwendungs-Bug: OS, Python-Version, Installationsmethode, Kommando / Transkript, Traceback.
   - Bibliotheks-API-Bug: Bibliotheks-Version, minimaler Reproduzierer, Runtime-Version.
   - Anwendungs-Feature: welches User-Goal es bedient, welches Audience-Segment, geprüfte Alternativen.
4. **Fragen als Issue-Forms-Komponenten kodieren.** Die einfachste Komponente verwenden, die passt:
   - Kurzer String → `input`.
   - Langer Freitext → `textarea` (mit `render: shell` für Logs / Tracebacks).
   - Eine-aus-vielen → `dropdown` mit den tatsächlich gültigen Werten, kein "Other / please specify".
   - Mehrere-aus-vielen → `checkboxes`.
   - Bestätigungsgates (Code of Conduct, Suchprüfung) → `checkboxes` mit `required: true`.
5. **Labels und Assignees setzen.** `labels:` aus der Label-Taxonomie des Projekts vorbelegen (häufig `.github/labels.yml` oder Probot `settings.yml`). `assignees:` nur dann vorbelegen, wenn das Repo einen stabilen Triage-Owner hat.
6. **Den Chooser verdrahten.** `.github/ISSUE_TEMPLATE/config.yml` mit `contact_links` für externe Ziele (Discussions, Support-Forum, Security-Policy) ergänzen, damit der Chooser sie neben den Templates anzeigt.

### Feld-Hygiene

Bug-Reports und Feature-Requests teilen sich denselben Speichermechanismus (`.github/ISSUE_TEMPLATE/*.yml` als Issue Forms), **DÜRFEN ABER NICHT [MUST NOT]** dasselbe Strenge-Profil bei den Feldern teilen. Bug-Reports tragen triage-kritische strukturierte Daten und sind bewusst streng; Feature-Requests brauchen Raum für unscharf formulierte Ideen und sind bewusst nachgiebig. Die Regeln darunter teilen sich entsprechend auf.

#### Gemeinsam für jedes Template

- **MUSS [MUST]** auf jedem Template eine Suchen-vor-Anlegen-Bestätigung enthalten (ein einzelner Pflicht-`checkboxes`-Eintrag, der auf den Issue-Tracker verweist).
- **SOLLTE [SHOULD]** jedes Template unter zehn Komponenten halten; längere Formulare senken die Abschlussrate.
- **KANN [MAY]** den Issue-Titel über den Top-Level-Schlüssel `title:` des Forms vorbelegen, wenn der Projekttyp eine strikte Titel-Konvention hat (zum Beispiel `[bug] <area>: <summary>` oder `[feat] `).

#### Bug-Reports — bewusst streng

- **MUSS [MUST]** jedes Feld, das Triager vor jeder Aktion brauchen, mit `validations: required: true` markieren.
- **SOLLTE NICHT [SHOULD NOT]** ein Freitext-"additional context"-Feld als einziges strukturiertes Feld haben — mindestens ein strukturiertes Feld pro Template muss triage-kritische Daten erfassen.
- **KANN [MAY]** `dropdown` und `checkboxes` großzügig nutzen, um konkrete operative Auswahlen (Installationsmethode, Runtime, OS) aufzuzählen, damit Triage über die Werte filtern kann.

#### Feature-Requests — bewusst nachgiebig

Ein Feature-Request kommt oft als halbgegorener Gedanke an, der Raum für Diskussion und Verfeinerung braucht, bevor er sich auf eine Form festlegt. Strikte Pflichtfeld-Gates schrecken vom Einreichen ab und erzwingen frühzeitige Festlegung auf eine Lösung; die Spec biased Feature-Templates daher in Richtung Offenheit:

- **MUSS [MUST]** die Anzahl der Pflichtfelder auf `feature_request.yml` bei höchstens zwei halten: die Suchen-vor-Anlegen-Bestätigung plus genau ein inhaltliches Eingabefeld.
- **MUSS [MUST]** für das inhaltliche Pflicht-Eingabefeld ein `textarea` verwenden (kein `dropdown`, kein `checkboxes`), damit der Reporter die Idee in eigenen Worten ausdrücken kann, statt aus einer vordefinierten Taxonomie zu wählen.
- **DARF NICHT [MUST NOT]** vom Reporter verlangen, aus einer geschlossenen Taxonomie zu wählen (Severity, Priority, Target-Release, Milestone, Owner). Das sind Triage-Entscheidungen, die Maintainer nach dem Lesen des Issues treffen, nicht der Reporter beim Anlegen.
- **SOLLTE [SHOULD]** projekttyp-spezifische Zusatzfelder (Target-Artefakt, Audience-Segment, Scope-Hinweis, …) als optionale Felder offenlegen statt als verpflichtend, selbst wenn dasselbe Feld auf der zugehörigen `bug_report.yml` verpflichtend wäre.
- **SOLLTE [SHOULD]** höchstens ein optionales `textarea` für zusätzlichen Kontext anbieten statt drei separater optionaler Felder ("Alternativen", "Screenshots", "frühere Diskussion") — weniger leere Felder hält das Formular scannbar und signalisiert, dass der Reporter Maintainer keinen ausgereiften Vorschlag schuldet.

### Skill-Kontrakt

Ein nachgelagerter Skill, der diese Spec anwendet, **MUSS [MUST]**:

- den Projekttyp gemäß dem obigen Verfahren erkennen.
- das Audience-Artefakt vor dem Generieren von Templates lesen oder erzeugen.
- seine Ableitung (Projekttyp, Audiences, gewählte Template-Arten, projektspezifische Felder **und das Strenge-Profil pro Template**) dem Nutzer offenlegen, bevor Dateien geschrieben werden.
- `.github/ISSUE_TEMPLATE/*.yml` und `.github/ISSUE_TEMPLATE/config.yml` gemeinsam schreiben — niemals einen halbkonfigurierten Stand zurücklassen.
- vor dem Schreiben von `feature_request.yml` validieren, dass nicht mehr als die Such-Bestätigung plus ein inhaltliches Feld `required: true` sind und dass das inhaltliche Pflichtfeld ein `textarea` ist; den Schreibvorgang abbrechen, wenn eine der Bedingungen verletzt ist.
- wieder ausführbar sein: ein erneuter Lauf auf einem Repo, das bereits Templates hat, **MUSS [MUST]** Drift erkennen (geänderter Projekttyp, neue Audiences, fehlende Pflichtfelder, **oder eine `feature_request.yml`, die Pflichtfelder über das Limit hinaus angesammelt hat**) und einen Diff anbieten, statt still zu überschreiben.

## Acceptance Criteria

- [ ] Ein nach dieser Spec auditiertes Repo besitzt `.github/ISSUE_TEMPLATE/config.yml` mit explizit gesetztem `blank_issues_enabled`.
- [ ] Ein nach dieser Spec auditiertes Repo besitzt mindestens `bug_report.yml` und `feature_request.yml` als Issue Forms.
- [ ] Jedes Pflichtfeld eines Bug-Templates lässt sich auf eine in Schritt 3 des Ableitungsverfahrens identifizierte Triage-Frage zurückführen.
- [ ] Jedes Template enthält eine verpflichtende Suchen-vor-Anlegen-Bestätigung.
- [ ] `feature_request.yml` trägt insgesamt höchstens zwei Pflichtfelder (Suchen-vor-Anlegen-Bestätigung + ein inhaltliches Feld).
- [ ] Das primäre inhaltliche Pflichtfeld in `feature_request.yml` ist ein `textarea`, kein `dropdown` und kein `checkboxes`.
- [ ] `feature_request.yml` verlangt kein Feld aus einer geschlossenen Taxonomie als Pflichtangabe (Severity, Priority, Target-Release, Milestone, Owner).
- [ ] Für ein Claude-Plugin-Repo fragt das Bug-Template nach Plugin-Version und betroffenem Skill oder Agent.
- [ ] Für ein Anwendungs-Repo (zum Beispiel kamerplanter) fragt das Bug-Template nach der für die Anwendung spezifischen Laufzeitumgebung (OS, Python- / Runtime-Version, gegebenenfalls relevante Hardware).
- [ ] Kein Template nutzt das Markdown-Format (`.md`), außer es handelt sich um einen rein informativen Stub.
- [ ] Die angewendete Ableitung (Projekttyp, Audiences, gewählte Templates, projektspezifische Felder) ist an einer Stelle festgehalten, die der Skill beim nächsten Lauf wieder lesen kann — entweder als Kommentar in den Templates oder in einem benachbarten Artefakt.
- [ ] Ein erneuter Lauf des Generators auf einem Repo, das bereits konform ist, erzeugt keinen Diff.

## Open Questions

- Soll der Ableitungs-Record (Projekttyp, Audiences, gewählte Templates) als YAML-Kommentarblock inline in `config.yml` leben oder in einer separaten Datei (zum Beispiel `.github/ISSUE_TEMPLATE/.derivation.yml`)? Inline ist einfacher; eine separate Datei ist für den Skill leichter parsebar.
- Wie spielt diese Spec mit der offenen `project-structure`-Frage zu Community-Health-Dateien zusammen? Sobald CODEOWNERS / SECURITY.md ebenfalls spezifiziert sind, soll der Issue-Template-Chooser via `config.yml.contact_links` automatisch auf SECURITY.md verlinken?
- Soll ein "security vulnerability"-Template überhaupt zulässig sein oder immer über `contact_links` an einen privaten Kanal geleitet werden? Aktueller Default: privat leiten, kein öffentliches Template.
- Discussion-Templates: in eine Folge-Spec auslagern oder hier mit aufnehmen?
