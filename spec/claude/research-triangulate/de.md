# Recherche-Triangulation

Status: draft

## Kontext
Skills und Agents im `nolte-shared`-Plugin produzieren regelmäßig Aussagen über Dinge, die **außerhalb** der aktuellen Working Copy leben: Versions-Pins von Upstream-Paketen und GitHub Apps, Dateipfade in Schwester-Repos, API-Signaturen und Defaults von Drittanbieter-Libraries, Konfigurations-Schemata externer Tools (Renovate, Probot, Vale), URLs, Quotas, Pricing-Tiers und Produktnamen. Wenn eine solche Aussage aus einer **einzigen** Quelle abgeleitet wird (einem einzelnen Web-Such-Snippet, einem einzelnen Memory-Eintrag, einer Erinnerung aus dem Pre-Training), gibt es keinen zweiten Blick, der eine Halluzination, einen veralteten Pin, ein umbenanntes Paket oder eine nie existierte API-Signatur abfangen könnte. Die Specs `skill-management`, `agent-management` und `skill-vs-agent` regeln, wie Claude-Code-Capabilities geformt werden, aber keiner davon regelt, **wie diese Capabilities wissen, dass das, was sie gleich behaupten, wahr ist**. Dieser Spec definiert eine portfolio-weite Triangulationsmethodik, die diese Lücke schließt: eine deterministische Regel dafür, wann trianguliert werden muss, wie viele unabhängige Quellen erforderlich sind, wie Quellenklassen gewichtet werden, wie Konflikte gehandhabt werden und wie das Ergebnis dokumentiert wird, damit eine spätere Leserin oder ein späterer Leser die Aussage auditieren kann.

**Adressatinnen und Adressaten:** Skill- und Agent-Autorinnen und -Autoren im `nolte-shared`-Plugin, die repo-externe Aussagen in ihren Artefakten verankern, sowie die Claude-Code-Laufzeit, die diese Skills und Agents zur Laufzeit im Auftrag der Operator-Person ausführt.

## Ziele
- Faktische Aussagen über repo-externe Sachverhalte in Skill-Outputs, Agent-Reports und Spec-Drafts werden niemals aus einer einzigen Quelle abgeleitet
- Halluzinationsrisiko für Upstream-Versions-Pins, Paketnamen, API-Signaturen und das Verhalten externer Services wird messbar gesenkt, bevor die Aussage in einem Schreib-Ziel landet
- Konflikte zwischen Quellen werden dem Operator sichtbar gemacht, bevor ein Schreibvorgang passiert—es gibt keine stille Mehrheitsentscheidung
- Die Mindest-Quellenzahl skaliert mit dem Blast Radius der nachgelagerten Handlung, die die Aussage legitimiert
- Jedes Artefakt, das eine triangulierte Aussage trägt, macht die Quellenliste sichtbar, damit ein späterer Leser die Aussage ohne erneute Recherche prüfen kann

## Nicht-Ziele
- Repo-interne Aussagen über die aktuelle Working Copy (Pfade, Datei-Inhalte, Frontmatter-Werte)—die werden direkt per `Read` / `Grep` verifiziert und brauchen keinen Multi-Source-Vergleich
- Subjektive Designentscheidungen (Stil-Präferenz, Roadmap-Priorität, Naming-Geschmack)—der Operator oder eine regelnde Spec sind Source of Truth
- Allgemeines Pre-Training-Wissen ohne externe Behauptung (Mathematik, gängige Sprach-Syntax, allgemein bekannte Konzepte)
- Live-Aussagen des Operators über seine eigene Umgebung—der Operator ist Primärquelle, und Triangulation gegen ihn wäre fehlplatziertes Misstrauen
- Ersatz für `spec-readiness-reviewer` (interne Spec-Konsistenz), `dependency-audit-scanner` (CVE-Erkennung) oder `workflow-health-triage` (CI-Rot-Triage)—Triangulation ist eine Recherche-Methodik, kein Tool, das capability-spezifische Specs ablöst

## Anforderungen

### Wann Triangulation Pflicht ist
- **MUSS [MUST]** jede faktische Aussage triangulieren, die sich auf etwas bezieht, das **nicht in der aktuellen Working Copy verifizierbar** ist, einschließlich:
  - Versions-Pins von Upstream-Paketen, GitHub Apps oder Container-Images
  - Existenz, Pfad oder Inhalt von Dateien in Schwester-Repos
  - API-Signaturen, Default-Werte oder Laufzeit-Verhalten von Drittanbieter-Libraries oder -Services
  - Konfigurations-Schemata, erlaubte Werte oder Deprecation-Status externer Tools (zum Beispiel Probot-Apps, Renovate-Presets, Vale-Styles)
  - URLs, Endpoints, Quotas, Pricing-Tiers oder Service-Level-Garantien
  - Produkt-, Paket- oder Markennamen, die nicht im aktuellen Repo verankert sind
- **DARF NICHT [MUST NOT]** repo-interne Aussagen separat triangulieren; die werden durch direktes Lesen der Working Copy verifiziert, und Triangulation gegen externe Quellen wäre langsamer und unzuverlässiger als ein `Grep`. Die Pflicht, dieses Lesen tatsächlich durchzuführen und die Behauptung zu markieren, wenn es unterblieb, besitzt `spec/claude/claim-provenance/`; der Ausschluss hier ist kein Freibrief, eine repo-interne Behauptung ungeprüft aufzustellen
- **DARF NICHT [MUST NOT]** subjektive Entscheidungen triangulieren; sie sind keine faktischen Aussagen und haben keine unabhängigen Quellen zum Vergleich
- **DARF [MAY]** auch repo-interne Aussagen triangulieren, wenn der tragende Spec dies explizit fordert (zum Beispiel weil die Aussage einen irreversiblen Schreibvorgang außerhalb des Repos gattet)

### Quellenklassen und Unabhängigkeit
Triangulation unterscheidet vier Quellenklassen:

| Quellenklasse | Beispiele | Gewichtung |
|---|---|---|
| **Primärquelle** | Offizielle Dokumentation des Upstream-Projekts, Source-of-Truth-Repository, vom Upstream-Owner gepflegte Schema-Datei | Höchste |
| **Sekundärquelle** | Gepflegter Aggregator (npmjs.com, pypi.org, GitHub Marketplace), gepflegter Mirror, datierter und autorisierter Blogartikel, der die Primärquelle zitiert | Mittel |
| **Web-Aggregator** | Suchergebnis-Snippet ohne klare Provenance, KI-generierte Zusammenfassung, undatierter Forenbeitrag | Niedrig |
| **Modellgedächtnis** | Pre-Training-Wissen, Memory-Einträge ohne zitierte Quelle | Nur Hypothese |

- **MUSS [MUST]** in jeder Triangulation **mindestens eine** Quelle der Klasse Primär ODER Sekundär enthalten; drei Web-Aggregator-Treffer allein erfüllen die Anforderung nicht
- **MUSS [MUST]** Quellen nur dann als unabhängig behandeln, wenn ihre Provenance wirklich verschieden ist: zwei Treffer vom selben Domain-Root, dieselbe Nachricht über mehrere Mirrors hinweg neu veröffentlicht oder mehrere Aggregator-Snippets, die alle auf denselben Aggregator zurückverweisen, zählen als **eine** Quelle
- **DARF NICHT [MUST NOT]** Modellgedächtnis als eine der erforderlichen Quellen zählen; es DARF die zu triangulierende Hypothese vorschlagen, MUSS aber von mindestens einer Primär- oder Sekundärquelle bestätigt werden, bevor die Aussage als verifiziert gilt
- **DARF NICHT [MUST NOT]** eine Quelle, die ein noch nicht ausgeliefertes Verhalten ankündigt (Release-Notes für eine geplante Version, Roadmap-Einträge, Pre-Release-Changelogs), zur Schwelle unabhängiger Quellen zählen; eine solche Quelle ist eine Hypothese—sie DARF die zu triangulierende Hypothese vorschlagen, aber das Verhalten MUSS in einer Primärquelle beobachtbar sein (veröffentlichte Version, Live-Schema, ausgelieferter Endpoint), bevor die Aussage als verifiziert gilt
- **SOLLTE [SHOULD]** mindestens eine Quelle ein verifizierbares Datum tragen (Last-Modified-Header, Commit-Zeitstempel, Veröffentlichungsdatum), damit ein veralteter Pin oder eine deprecated API erkennbar wird

### Mindest-Quellenzahl skaliert mit Blast Radius
Die Mindestanzahl **unabhängiger** Quellen skaliert mit der nachgelagerten Handlung, die die Aussage legitimiert:

| Nachgelagerter Effekt der Aussage | Mindestanzahl unabhängiger Quellen |
|---|---|
| Konversations-Output an den Operator ohne nachfolgenden Schreibvorgang | **2:** eine Primär, eine unabhängige Sekundär |
| Lokaler Edit in der Working Copy (Code, Doku, Spec-Draft) | **2:** eine Primär, eine unabhängige Sekundär |
| Schreibvorgang in einer Konfigurationsdatei, die ein Release oder einen Workflow-Dispatch triggern kann (zum Beispiel `renovate.json5`, `release-publish.yml`, versionstragende Dateien unter `docs/requirements.txt`) | **3:** eine Primär plus zwei unabhängige Sekundär oder zwei unabhängige Primär |
| Force-Push, Release-Publish, Workflow-Dispatch, Cross-Repo-Pull-Request | **3** plus explizite Operator-Bestätigung der Quellenliste vor dem Aufruf |

- **MUSS [MUST]** die geforderte Mindest-Quellenzahl erreichen, bevor eine Aussage in einem Artefakt landet
- **MUSS [MUST]**, wenn die geforderte Zahl unerreichbar ist, die Aussage als `unverified` markieren und die Kontrolle an den Operator zurückgeben—niemals eine untertriangulierte Aussage als verifiziert ausgeben
- **SOLLTE [SHOULD]** im Zweifel die höhere Stufe wählen; die Kosten eines zusätzlichen Quellen-Fetches sind geringer als die Kosten eines falschen Pins, der nach `main` gemerged wurde
- **DARF [MAY]** eine einzelne Primärquelle als ausreichend behandeln, wenn keine unabhängige Sekundärquelle trotz dokumentiertem Sucheffort gefunden werden kann (zum Beispiel ein brandneues Upstream-Tool ohne Aggregator-Präsenz); in diesem Fall **MUSS [MUST]** die Quellenliste den dokumentierten Sucheffort festhalten, UND für jede Blast-Radius-Stufe oberhalb von "Lokaler Edit" **MUSS [MUST]** der Operator die untertriangulierte Aussage explizit bestätigen, bevor die nachgelagerte Handlung fortgesetzt wird; autonome Loops ohne erreichbaren Operator **MÜSSEN [MUST]** den Schreibvorgang abbrechen

### Author-Time-Aussagen
Aussagen, die in langlebigen Authoring-Artefakten fest verdrahtet sind (der `SKILL.md`-Datei eines Skills, einer Agent-Datei unter `agents/` oder einer Spec-Datei unter `spec/`), persistieren über viele Runs und prägen viele nachfolgende Operationen. Sie rechtfertigen daher eine strengere Schwelle als die Laufzeit-Stufe, in der die Aussage sonst säße.

- **MUSS [MUST]** jede Author-Time-Aussage **mindestens auf der Release/Dispatch-Stufe** (drei unabhängige Quellen) triangulieren, wenn die Aussage das Verhalten eines Skills oder Agents in Richtung Schreibvorgängen außerhalb der Working Copy lenkt—Versions-Pins, Pfade in Schwester-Repos, Drittanbieter-API-Signaturen, Default-Werte externer Tools
- **DARF NICHT [MUST NOT]** sich für eine Author-Time-Aussage allein auf das Modellgedächtnis verlassen, auch wenn das Artefakt noch im Draft-Zustand ist und noch nicht ausgeliefert wurde
- **SOLLTE [SHOULD]** die Quellenliste in der Beschreibung des Authoring-Pull-Requests festhalten, wenn das Artefakt-Format keinen natürlichen Inline-Slot bietet (zum Beispiel weil die Aussage eine von vielen in einem langen Spec-Body ist)

### Konfliktauflösung
- **MUSS [MUST]**, wenn zwei oder mehr Quellen einander widersprechen, **anhalten** und die Konfliktlage dem Operator offen legen, einschließlich:
  - welche Quellen widersprechen sich
  - in welchem konkreten Detail (eine Versions-Zeichenkette, ein Pfad, ein API-Feld, ein Flag-Default)
  - der Quellenklasse jeder widersprechenden Quelle
  - einem verifizierbaren Datum für jede Quelle, wo eines existiert
- **DARF NICHT [MUST NOT]** still eine Mehrheitsentscheidung fällen—auch nicht bei 2-zu-1
- **DARF NICHT [MUST NOT]** auf die Quellenklassen-Hierarchie als automatischen Tie-Breaker zurückfallen; die Hierarchie wird dem Operator als Empfehlung präsentiert, der Operator entscheidet
- **SOLLTE [SHOULD]** im Konfliktbericht die wahrscheinlichste Erklärung benennen (zum Beispiel "Quelle A ist 18 Monate älter als Quelle B; das Upstream-Verhalten hat sich zwischen diesen Daten wahrscheinlich geändert"), damit der Operator entscheiden kann, ohne die Recherche von vorn neu zu starten
- **MUSS [MUST]**, wenn der Operator nicht erreichbar ist (autonomer Loop, geplanter Run, Cron-gesteuerter Dispatch), den **Schreibvorgang abbrechen** und die Konfliktlage als Findings-Report persistieren, anstatt zu raten

### Dokumentation der Triangulation
Der Findings-Report-Pfad nutzt das Per-Run-Snapshot-Muster (`.audits/<skill>/<run>/`), nicht den Per-Target-Review-Plan-Pfad aus `spec/claude/review-plan/`. Ein Triangulations-Report hält die Quellenliste **zum Zeitpunkt der Aussage** fest—das sind run-bezogene Daten und kein dauerhafter Per-Target-Review-Eintrag; die beiden Muster bestehen absichtlich nebeneinander.

- **MUSS [MUST]** die Quellenliste im Artefakt sichtbar machen, das die triangulierte Aussage trägt—entweder inline (Fußnote, Quellenliste am Ende, Referenzen im `[R1]`-Stil) oder in einem assoziierten Findings-Report unter dem Audit-Verzeichnis des aufrufenden Skills (`.audits/<skill>/<run>/`), je nach Träger-Format
- **MUSS [MUST]** für jede Quelle mindestens festhalten: URL oder Pfad, Quellenklasse und Abrufdatum
- **SOLLTE [SHOULD]** die Quellenliste nach Gewichtung sortieren (Primärquelle zuerst), damit ein Leser, der die Provenance überfliegt, die stärkste Quelle sofort sieht
- **SOLLTE [SHOULD]** jede festgehaltene Quelle als Träger einer beratenden Time-to-Live behandeln, die am Aussagetyp ausgerichtet ist—30 Tage für Versions-Pin-Quellen, 90 Tage für API-Verhalten- oder Schema-Quellen (an den Staleness-Schwellen in `spec/project/docs-freshness` ausgerichtet); wenn ein tragender Skill eine Aussage wiederverwendet, deren neueste Quelle älter als ihre TTL ist, um einen Schreibvorgang oberhalb der "Lokaler Edit"-Stufe zu gatten, SOLLTE er vor dem Schreibvorgang gegen eine aktuelle Quelle erneut validieren
- **DARF [MAY]** die Quellenliste bei späteren Re-Runs auffrischen—Triangulation altert, und das erneute Bestätigen einer alten Aussage gegen eine aktuelle Quelle ist eine legitime Pflegeaufgabe

### Wechselwirkung mit bestehenden Skills und Agents
- **MUSS [MUST]** diese Methodik in Skills anwenden, die repo-externe Aussagen an den Operator surfacen, einschließlich, aber nicht beschränkt auf: `dependency-audit`, `release-notes-curate`, `cookiecutter-template-manage` und jeden Skill, der WebSearch oder WebFetch verwendet
- **MUSS [MUST]** diese Methodik in Agents anwenden, die repo-externe Aussagen produzieren; die Triangulation passiert **innerhalb** des Agent-Runs und die Quellenliste wird als Teil des strukturierten Reports an den dispatchenden Skill zurückgegeben
- **SOLLTE [SHOULD]** den Quellenliste-Abschnitt des Agent-Reports vor dem Operator-Approval-Gate vom dispatchenden Skill sichten lassen und jeden vom Agent gemeldeten Konflikt erneut sichtbar machen
- **DARF [MAY]** die Methodik in Skills überspringen, deren Scope rein repo-intern ist (zum Beispiel `quality-gate`, `sprint-execute`, `feature-decompose`, `pull-request-create`), sofern sie keine repo-externen Aussagen treffen

## Akzeptanzkriterien
- [ ] Ein Skill, der WebSearch verwendet, erfüllt die Mindest-Quellenzahl aus der Blast-Radius-Tabelle, bevor er eine Aussage dem Operator als verifiziert präsentiert
- [ ] Ein Agent, der eine Drittanbieter-API-Signatur in einem Spec-Draft verankert, hält die Quellenliste—einschließlich URL oder Pfad, Quellenklasse und Abrufdatum pro Quelle—entweder inline im Spec-Body oder in einem assoziierten Findings-Report unter `.audits/<skill>/<run>/` fest
- [ ] Bei einem Konflikt zwischen zwei Quellen-Treffern hält der aufrufende Skill an und legt die Konfliktlage offen—mit Angabe, welche Quellen widersprechen, in welchem Detail, mit welcher Quellenklasse und mit einem verifizierbaren Datum pro Quelle, wo eines existiert —, anstatt eine Mehrheitsentscheidung zu treffen
- [ ] Wenn die geforderte Mindest-Quellenzahl unerreichbar ist, markiert das Artefakt die Aussage als `unverified` und der Skill gibt die Kontrolle an den Operator zurück
- [ ] Repo-interne Aussagen werden nicht gegen externe Quellen trianguliert; sie werden über `Read` oder `Grep` direkt gegen die Working Copy verifiziert
- [ ] Modellgedächtnis (Pre-Training-Wissen, Memory-Einträge ohne zitierte Quelle) zählt nicht zur Schwelle unabhängiger Quellen
- [ ] Zwei Quellen-Treffer vom selben Domain-Root oder mehrere Mirrors derselben Upstream-Nachricht werden als eine einzige Quelle und nicht als zwei unabhängige Quellen zur Schwelle gezählt
- [ ] In einem autonomen Loop ohne erreichbaren Operator bricht der Skill bei einem Quellen-Konflikt den ausstehenden Schreibvorgang ab und persistiert den Konflikt als Findings-Report unter dem Audit-Verzeichnis des Runs
- [ ] Wenn nur eine Primärquelle trotz dokumentiertem Sucheffort verfügbar ist, hält ein Skill oberhalb der "Lokaler Edit"-Stufe den Schreibvorgang an, bis der Operator die Ein-Quellen-Aussage bestätigt; ein autonomer Loop ohne erreichbaren Operator bricht den Schreibvorgang vollständig ab
- [ ] Eine Author-Time-Aussage, die in `SKILL.md`, einer `agents/*.md`-Datei oder einer Spec-Datei fest verdrahtet ist und das Verhalten eines Skills oder Agents in Richtung repo-externer Schreibvorgänge lenkt, wird auf mindestens der Release/Dispatch-Stufe (drei unabhängige Quellen) trianguliert, bevor der Authoring-Pull-Request gemerged wird

## Offene Fragen
_Derzeit keine._
