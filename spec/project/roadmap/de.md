# Projekt-Roadmap

Status: draft

## Kontext

Leser: Repo-Maintainer von Hobby-Projekten im nolte-Portfolio, die die Skills `roadmap-init`, `roadmap-refine` und `roadmap-planner` aufrufen, sowie die Implementierer dieser Skills, die gegen das hier definierte Schema bauen.

Das nolte-Portfolio besteht überwiegend aus Hobby-Projekten. Sprint-Kadenz, verfügbare Kapazität und sogar die Frage, ob ein Projekt aktuell überhaupt aktiv ist, schwanken Woche für Woche stark. Bestehende Specs decken einzelne Auslieferungs-Mechaniken ab (`release-automation`, `release-skill-layer`, `quality-gate`) sowie reflektive Rituale (`continuous-improvement`, das sich explizit gegen Sprint-Kadenz positioniert), aber nichts definiert bisher, **welche Arbeit ansteht, warum sie wichtig ist und in welcher Reihenfolge sie umgesetzt werden soll**. Diese Spec führt diese Planungsschicht als Markdown-Artefaktpaar unter `project/` im Zielprojekt-Repo ein, bewusst leichtgewichtig genug für ein Hobby-Projekt und gleichzeitig strukturiert genug, dass die konsumierenden Claude-Skills (`roadmap-init`, `roadmap-refine`, `roadmap-planner`) und die Geschwister-Specs (`sprint`, `feature`, `release-artifact`) die Roadmap deterministisch lesen und schreiben können. Die Roadmap ist ein Brücken-Dokument: sie verknüpft jedes Warteschlangen-Item mit einem Projektergebnis (Outcome), damit Kapazität immer auf Dingen landet, die für den Endnutzer wertvoll sind.

## Ziele

- Die Datei-Form einer Projekt-Roadmap als zwei Markdown-Dateien im Repo-Root festlegen: `project/roadmap.md` (die Warteschlange) und `project/goals.md` (die Vision plus die Outcomes, denen die Warteschlange dient).
- Ein stabiles Item-Schema (über YAML-Frontmatter verankert) festlegen, damit konsumierende Skills Items parsen, ändern und neu rendern können, ohne pro Skill einen eigenen Parser zu bauen.
- Eine verbindliche Detailgrad-Konvention festlegen (`fine` für die nächsten beiden Sprints, `coarse` oder `backlog` darüber hinaus), damit Planungsaufwand dort landet, wo er sich auszahlt, und weiter entfernte Items nicht vorschnell überspezifiziert werden.
- Jedes Roadmap-Item mit mindestens einem Outcome aus `goals.md` verknüpfen, damit jede Priorisierungs-Diskussion eine Antwort auf "für wen ist das wichtig" hat.
- Portfolio-weit wiederverwendbar bleiben: jeder im Portfolio unterstützte Projekttyp (Claude-Plugin, Python-Anwendung, Python-Bibliothek, Node / TypeScript, CLI-Tool, dokumentations-only — dieselbe Taxonomie wie `github-issue-templates-apply`) kann das Layout ohne typ-spezifische Schema-Varianten übernehmen.

## Nicht-Ziele

- Sprint-Mechanik, Feature-Schema oder Release-Artefakt-Regeln festzulegen. Jedes davon gehört seiner eigenen Geschwister-Spec (`sprint`, `feature`, `release-artifact`); diese Spec erklärt nur Beziehungen, keine Innenleben.
- Projektmanagement-Tooling zu ersetzen (Jira, Linear, GitHub Projects). Die Roadmap ist ein Markdown-Artefakt unter Versionskontrolle, kein Ticket-Speicher; Verweise auf Issue-Tracker sind erlaubt, aber nie autoritativ.
- Eine Zeitachse zu erzwingen. Sprint-Dauer ist laut Geschwister-Spec `sprint` ausdrücklich variabel, deshalb trägt die Roadmap pro Item keine Start-/End-Daten; sie trägt eine Reihenfolge und einen grob-zu-fein Detailgradienten.
- `continuous-improvement` zu ersetzen. Diese Spec arbeitet ereignis- und kalendergetrieben über Audits, nicht über Sprint-Kadenz, und bleibt die Autorität für retrospektive Prozessänderungen.
- `audience-identification` zu ersetzen. Outcomes in `goals.md` werden aus dem Audience-Artefakt abgeleitet, falls vorhanden; diese Spec konsumiert das Artefakt, erfindet aber niemals Audiences inline.

## Anforderungen

### Verzeichnislayout

- **MUSS [MUST]** beide Dateien im Repo-Root unter `project/` ablegen: `project/roadmap.md` und `project/goals.md`. Das Verzeichnis ist ein Top-Level-Orientierungspunkt, nicht unter `docs/` verschachtelt.
- **DARF NICHT [MUST NOT]** die Roadmap auf mehrere Dateien aufteilen; es gibt genau eine `project/roadmap.md` pro Repository.
- **SOLLTE [SHOULD]** `project/goals.md` so kurz halten, dass sie in einem Zug gelesen werden kann (eine Bildschirmseite Vision plus eine flache Outcome-Liste ist die Zielform).
- **KANN [MAY]** Geschwisterdateien tragen, die andere Specs der Suite definieren (`project/sprints/<n>-<slug>.md`, `project/features/<slug>.md`); deren Existenz und Form regeln die Specs `sprint` bzw. `feature`.

### Form von `goals.md`

- **MUSS [MUST]** mit einem einzigen Absatz **Vision** beginnen, der erklärt, was das Projekt ist und für wen es gedacht ist, in der Hauptsprache des Projekts.
- **MUSS [MUST]** einen Abschnitt **Outcomes** tragen, der ein oder mehrere Outcomes auflistet. Jedes Outcome **MUSS [MUST]** einen stabilen Bezeichner (`O-<n>`, monoton vergeben, niemals wiederverwendet) und eine einzeilige Beschreibung im Stil eines Endnutzer-Vorteils haben.
- **MUSS [MUST]** jedes Outcome auf einen Audience-Eintrag aus dem Audience-Artefakt des Repos zurückführen (typischerweise `AUDIENCES.md` per `audience-identification`); existiert kein Audience-Artefakt, **MUSS [MUST]** `audience-identify` vor dem Schreiben von Outcomes ausgelöst werden — der Dispatch ist verpflichtend, nicht optional, weil Outcomes mit erfundenen Audiences keinem realen Leser dienen können.
- **DARF NICHT [MUST NOT]** Audience-Einträge inline erfinden; fehlende Audiences sind ein Blocker für die Outcome-Erstellung, kein Hinweis zum Fabrizieren.

### Form von `roadmap.md` und Item-Schema

- **MUSS [MUST]** die Roadmap als flache geordnete Liste strukturieren (oben-nach-unten ist höchste-zu-niedrigste Priorität). Items **KÖNNEN [MAY]** unter Level-2-Phasen-Überschriften gruppiert werden (zum Beispiel `## Phase 1 — Fundament`), wenn Phasen das Lesen erleichtern; Phasen sind optional und tragen kein Schema außer dem Überschriftstext.
- **MUSS [MUST]** jedes Roadmap-Item in folgender dreiteiliger Form, in dieser Reihenfolge, darstellen: (a) eine Level-3-Markdown-Überschrift, die das Item benennt (typischerweise `### <id> — <title>`); (b) unmittelbar gefolgt von einem fenced YAML-Codeblock (` ```yaml … ``` `), der die unten aufgeführten Schema-Felder in der festgelegten Reihenfolge trägt; (c) unmittelbar gefolgt vom Freitext-Body, dessen Pflicht-Tiefe vom `detail`-Wert abhängt (siehe unten). Das Paar aus Heading und YAML-Block identifiziert das Item gegenüber konsumierenden Skills; der Body dient menschlichen Lesern. Ein Dokument-weites YAML-Frontmatter (`---` am Anfang von `roadmap.md`) ist **nicht** die Form, in der Items dargestellt werden — jedes Item trägt seinen eigenen Inline-YAML-Codeblock.
- **MUSS [MUST]** im Per-Item-YAML-Block die folgenden Felder in dieser Reihenfolge tragen:
  - `id` (String, verpflichtend) — Muster `R-<n>`, monoton vergeben, niemals wiederverwendet;
  - `title` (String, verpflichtend) — einzeilige Zusammenfassung in der Hauptsprache des Projekts;
  - `detail` (Enum, verpflichtend) — einer von `fine`, `coarse`, `backlog`;
  - `outcomes` (Liste von Outcome-IDs, verpflichtend, nicht leer) — jeder Eintrag **MUSS [MUST]** ein `O-<n>` aus `goals.md` matchen;
  - `target_sprint` (Integer oder null, verpflichtend, darf null sein) — Sprint-Nummer, für die das Item momentan vorgesehen ist; das Feld **MUSS [MUST]** im YAML-Block erscheinen, auch wenn null, damit Item-Parser auf einen stabilen Schlüsselsatz vertrauen können;
  - `mvp` (Boolean, verpflichtend) — `true` markiert das Item als Teil des MVP-Scopes (Pflicht für die Erfüllung der Projektmission), `false` markiert es als Post-MVP (optional, explizit benannt, damit die Grenze sichtbar bleibt). Der Ort des Felds in diesem Schema gehört dieser Spec; die Semantik des Felds, das Stabilisierungs-Gate und die Audit-Regeln rund um Flag-Wechsel gehören der Geschwister-Spec `mission` — siehe `spec/project/mission/<canonical_language>.md`. Repositories ohne `project/mission.md` **KÖNNEN [MAY]** `mvp: false` auf jedem Item tragen oder die Datei vollständig weglassen; sobald eine Mission-Datei existiert, **MUSS [MUST]** jedes Roadmap-Item das Feld tragen;
  - `status` (Enum, verpflichtend) — einer von `proposed`, `active`, `done`, `cancelled`.
- **MUSS [MUST]** jedem YAML-Block einen Freitext-Body folgen lassen, dessen Pflicht-Tiefe vom `detail`-Wert abhängt:
  - `fine`: ein Absatz, der die für den Nutzer sichtbare Änderung beschreibt, plus eine Checkliste der vorgesehenen Features (nur Titel — das tatsächliche Feature-Schema lebt in der Spec `feature`);
  - `coarse`: ein bis zwei Sätze, die die Absicht beschreiben;
  - `backlog`: ein einziger Satz reicht.
- **DARF NICHT [MUST NOT]** Aufwandsschätzungen, Daten oder Zuweisungsfelder tragen; diese gehören in die konsumierenden Sprint- und Feature-Artefakte.

Konkrete Form eines `fine`-Items in `roadmap.md`:

````markdown
### R-3 — Replace the legacy auth flow

```yaml
id: R-3
title: Replace the legacy auth flow
detail: fine
outcomes: [O-1, O-4]
target_sprint: 7
mvp: true
status: proposed
```

End users authenticate via the new SSO provider in under three steps; the legacy session-token path is decommissioned.

- [ ] sso-redirect-flow
- [ ] legacy-auth-decommission
````

### Detailgrad-Konvention und Refinement-Regel

- **MUSS [MUST]** zu jedem Zeitpunkt sicherstellen, dass jedes Roadmap-Item, dessen `target_sprint` auf **den aktuellen Sprint** oder **den nächsten Sprint** zeigt, `detail: fine` trägt. **Der aktuelle Sprint** ist definiert als der Sprint, dessen `status` laut Geschwister-Spec `sprint` `active` ist (höchstens ein solcher Sprint pro Projekt); existiert kein `active`-Sprint, ist der aktuelle Sprint der niedrigst-nummerierte `planned`-Sprint und ersatzweise der höchst-nummerierte `closed`-Sprint, falls kein `planned` existiert. **Der nächste Sprint** ist der niedrigst-nummerierte `planned`-Sprint, dessen `number` größer als die `number` des aktuellen Sprints ist. Der Skill `roadmap-refine` ist der kanonische Durchsetzungspunkt und **MUSS [MUST]** eine Verletzung melden, wenn diese Invariante bricht. Eine Verletzung **MUSS [MUST]** als strukturierter Datensatz mit Item-`id`, dem fehlerhaften `target_sprint`, dem aktuellen `detail`, den aufgelösten Sprint-Nummern für „aktuell" und „nächster" (damit der Operator versteht, warum das Item geflaggt wurde) und einem einzeiligen Behebungshinweis gemeldet werden; der Exit-Code des konsumierenden Skills ist von null verschieden, und die Verletzung wird auf stderr (oder den strukturierten Output-Kanal des Skills) geschrieben, damit nachgelagertes Tooling sie aufgreifen kann.
- **KANN [MAY]** Items mit `detail: coarse` oder `detail: backlog` für jeden Sprint zwei oder mehr Sprints in der Zukunft tragen; die Promotion auf `fine` ist der Auslöser für `roadmap-refine`, das Item in Form zu bringen.
- **SOLLTE [SHOULD]** die Anzahl `fine`-Items grob auf die Kapazität der nächsten zwei Sprints begrenzen; ein unbegrenzter `fine`-Block hebelt den Gradienten aus und führt vorzeitige Über-Spezifikation wieder ein.

### Outcome-Verknüpfung

- **MUSS [MUST]** jedes Roadmap-Item ablehnen, dessen `outcomes`-Liste leer ist oder eine Outcome-ID enthält, die in `goals.md` nicht existiert. Konsumierende Skills **MÜSSEN [MUST]** sich weigern, solche Items zu schreiben.
- **SOLLTE [SHOULD]** ein bis zwei Outcome-Links pro Item bevorzugen; lange Listen sind ein Hinweis darauf, dass das Item gesplittet werden sollte.

### Sprint- und Feature-Verknüpfung

- **KANN [MAY]** `target_sprint` zuweisen, um vorzuschlagen, welcher Sprint das Item aufgreifen soll; der Vorschlag ist nicht bindend, und die tatsächliche Sprint-Zusammensetzung gehört `sprint-plan` laut Geschwister-Spec `sprint`.
- **MUSS [MUST]** `target_sprint` clearen oder neu zuweisen, sobald der referenzierte Sprint einen terminalen Status (`closed` oder `cancelled`) erreicht, ohne das Item aufgenommen zu haben; `sprint-plan` besitzt dieses Update beim Sprint-Abschluss. Die zulässigen Post-Closure-Werte sind `null` (Item fällt zurück auf ungeplant) oder ein neuer Integer, der auf einen `planned`-Sprint zeigt. `target_sprint` auf einen terminalen Sprint zeigen zu lassen, ist eine Lint-Verletzung.
- **DARF NICHT [MUST NOT]** Feature-Definitionen inline enthalten. Die Zerlegung eines Roadmap-Items in ein oder mehrere Features ist der Vertrag der Geschwister-Spec `feature` und des Skills `feature-decompose`; das Roadmap-Item referenziert seine Features höchstens per ID, nachdem sie existieren (die Rück-Referenz lebt auf der Feature-Seite, nicht in der Roadmap).

### Lifecycle

- **MUSS [MUST]** `status` nur entlang dieser Pfade übergehen lassen: `proposed → active`, `active → done`, `proposed → cancelled`, `active → cancelled`. Direktes `proposed → done` ist verboten, weil jedes erledigte Item aktiv bearbeitet worden sein muss; `cancelled → *` ist verboten, weil abgebrochene Items archiviert sind.
- **MUSS [MUST]** ein Item spätestens dann auf `active` setzen, wenn eines seiner Features laut `feature`-Spec nach `in_progress` geht; der konsumierende Skill (`sprint-execute`, wenn er ein Feature voranbringt) ist der kanonische Durchsetzungspunkt.
- **MUSS [MUST]** ein Item erst auf `done` setzen, wenn jedes seiner abgeleiteten Features `done` ist **und** der zugehörige Sprint `closed` erreicht hat (ausdrücklich `closed`, nicht `cancelled`); ein Sprint, der schließt, ohne jedes abgeleitete Feature aufzunehmen, blockiert das Item auf `done`, bis die verbliebenen Features neu zugeordnet sind. Ein Sprint, der aus irgendeinem Stadium `cancelled` erreicht, **DARF NICHT [MUST NOT]** ein Roadmap-Item auf `done` heben, selbst wenn alle Features einzeln `done` sind, weil Abbruch bedeutet, dass kein ausrollbares Artefakt das Mehrwert-Statement materialisiert hat; in diesem Fall **MÜSSEN [MUST]** die offenen Features des Roadmap-Items in einen neuen Sprint umgehängt werden, und das Item bleibt `active`, bis dieser Nachfolge-Sprint `closed` erreicht.

### Phasen

- **KANN [MAY]** Items unter Level-2-Phasen-Überschriften gruppieren (zum Beispiel `## Phase 1 — Fundament`); Phasen sind Dokumentation, kein Schema. Eine Phase hat keine ID, keinen Status und kein eigenes Frontmatter, und eine flache Roadmap mit null Phasen-Überschriften ist gleichwertig gültig.

### Hobby-Skala-Varianz

- **DARF NICHT [MUST NOT]** Daten, Zeitschätzungen oder Velocity-Tracking erzwingen. Sprint-Dauer ist laut Geschwister-Spec `sprint` variabel, und die Roadmap ist nicht der Ort, um das Gegenteil zu behaupten.
- **SOLLTE [SHOULD]** lange Inaktivitätsphasen tolerant tragen: die Roadmap ist eine Warteschlange, kein Zeitplan, also bleiben `status: proposed`-Items unbegrenzt gültig.

## Akzeptanzkriterien

- [ ] `project/roadmap.md` und `project/goals.md` existieren im Repo-Root jedes adoptierenden Projekts; verschachtelte oder alternative Orte schlagen die Validierung.
- [ ] `goals.md` öffnet mit einem Vision-Absatz und einem Outcomes-Abschnitt, in dem jedes Outcome eine `O-<n>`-ID und eine einzeilige Endnutzer-Vorteils-Beschreibung trägt.
- [ ] Jedes Roadmap-Item in `roadmap.md` trägt eine Level-3-Markdown-Überschrift, unmittelbar gefolgt von einem fenced YAML-Codeblock (` ```yaml … ``` `) mit den sieben Schema-Feldern (`id`, `title`, `detail`, `outcomes`, `target_sprint`, `mvp`, `status`) in der festgelegten Reihenfolge, unmittelbar gefolgt vom Freitext-Body; `target_sprint` ist immer vorhanden, mit dem literalen Wert `null`, wenn das Item ungeplant ist, und `mvp` ist als Boolean immer vorhanden, sobald das Repository eine `project/mission.md` trägt.
- [ ] Die `outcomes`-Liste jedes Roadmap-Items löst auf: jeder Eintrag matcht ein in `goals.md` definiertes `O-<n>`; Lints schlagen sonst fehl.
- [ ] Kein Roadmap-Item, dessen `target_sprint` auf den aktuellen oder nächsten Sprint zeigt, trägt einen anderen `detail`-Wert als `fine`; `roadmap-refine` meldet bei Bruch dieser Invariante eine Verletzung.
- [ ] Kein `proposed`-Item geht direkt nach `done`; die einzigen erlaubten Übergänge sind `proposed → active → done`, `proposed → cancelled` und `active → cancelled`.
- [ ] Keine Aufwandsschätzungen, Kalenderdaten oder Zuweisungsfelder erscheinen an Roadmap-Items; Lints flaggen jedes unbekannte Frontmatter-Schlüsselwort.
- [ ] Kein Roadmap-Item trägt `target_sprint`, das auf einen `closed`- oder `cancelled`-Sprint zeigt; Lints schlagen, sobald ein Sprint terminal wird, ohne dass `sprint-plan` noch auf ihn zeigende Items geclearet oder neu zugewiesen hat.
- [ ] Kein Roadmap-Item ist im Status `done`, solange ein abgeleitetes Feature in einem nicht-terminalen Status ist (`draft`, `ready`, `in_progress`); beim Sprint-Abschluss durch `sprint-review` durchgesetzt.
- [ ] Kein Roadmap-Item geht aus einem Sprint mit `status: cancelled` auf `status: done` über, selbst wenn alle Features des Items einzeln `done` sind; die offenen Features des Items müssen in einen neuen Sprint umgehängt werden, und das Item bleibt `active`, bis dieser Nachfolge-Sprint `closed` erreicht.
- [ ] `audience-identification` wird vor der Outcome-Erstellung auf einem frischen Repo ohne Audience-Artefakt ausgelöst; Outcomes werden niemals inline erfunden.

## Offene Fragen

- Soll die Roadmap ein Tag-Feld erlauben (`tags: [perf, ux, infra]`) zum Filtern großer Warteschlangen, oder gehört das auf eine zukünftige Oberfläche (eine generierte Index-Seite)? Verschoben, bis eine Roadmap mehr als ungefähr zwanzig `coarse`+`backlog`-Items enthält.
- Wie stellen wir Abhängigkeiten zwischen Roadmap-Items dar (`R-7 hängt von R-3 ab`)? Eine Frontmatter-Liste (`depends_on: [R-3]`) wäre die naheliegende Form, aber eine Hobby-Skala-Roadmap braucht selten strikte Reihenfolgen jenseits von oben-nach-unten; revisitieren, wenn ein echtes Projekt eine echte Blocker-Kette trifft.
- Soll `target_sprint` einen Bereich akzeptieren (`target_sprint: [3, 5]`) für Items, die mehrere Sprints überspannen, oder ist das Splitten des Items die richtige Antwort? Splitten wird heute bevorzugt; revisitieren, falls ein echtes Cross-Sprint-Item auftaucht, das sich tatsächlich nicht splitten lässt.
- Sollen Phasen einen stabilen Bezeichner tragen, damit nachgelagertes Tooling (Release Notes, audience-doc-author) Änderungen nach Phase gruppieren kann? Verschoben, bis mindestens ein phasen-bewusster Konsument existiert.
