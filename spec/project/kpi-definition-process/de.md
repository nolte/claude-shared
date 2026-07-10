# KPI-Definitionsprozess

Status: draft
Portfolio-Scope: portfolio

## Kontext

Eine Business-Anwendung lässt sich auf hundert Arten messen — Request-Zahlen, Zeilenzahlen, Klickraten, Fehlersummen — und die meisten davon sind Rauschen. Ein Team, das Kennzahlen bottom-up wählt, aus dem, was der Code zufällig exponiert, endet mit einem Dashboard voller Vanity-Zahlen, die keine Geschäftsfrage beantworten; ein Team, das keine wählt, fliegt blind. Was fehlt, ist ein **top-down, zielorientierter Prozess**, der entscheidet, *welche* Handvoll Indikatoren die **Schlüssel-Indikatoren** für genau diese Anwendung sind und *wie jeder definiert ist*, bevor irgendjemand eine einzige Messung verdrahtet.

Diese Spec definiert diesen Prozess: wie man die projektspezifischen KPIs einer Business-Anwendung **ermittelt** (aus ihren Geschäftszielen, ihren Requirement-Dokumenten und ihrem Quellcode) und wie man jeden präzise **definiert** (Name, Definition, Formel-Intent, Einheit, Zielwert, Klassifikation, Owner, Ziel-Verknüpfung, Datenquellen-Zeiger, Rationale). Sie ist in der etablierten Mess-Literatur verankert — dem **Goal/Question/Metric**-Paradigma (Basili, Caldiera, Rombach) als Ableitungs-Rückgrat, den **SMART**-Kriterien (Doran, 1981) als Pro-KPI-Qualitätsgate, der **Leading-vs-Lagging**-Indikator-Unterscheidung als Klassifikationsachse und der **KPI-vs-Metrik**-Grenze, die die Auswahl der wenigen Schlüssel-Indikatoren aus den vielen möglichen Metriken erzwingt.

Die Spec zieht eine **harte Grenze**: Sie regelt *nur Ermittlung und Definition*. In dem Moment, in dem ein KPI definiert ist, stoppt der Prozess. Wie dieser KPI instrumentiert, erhoben, zur Laufzeit berechnet, gespeichert oder angezeigt wird, ist **Messung**, und Messung ist außerhalb des Scopes (siehe §Nicht-Ziele). GQM selbst macht diese Naht explizit: seine späteren Schritte — „select data collection techniques, tools and procedures … develop the data collection mechanisms, including validation and analysis" — sind genau die Mess-Stufe, die diese Spec ausschließt. Diese Spec übernimmt GQMs Goal→Question→Metric-*Ableitung* und stoppt vor seiner Datenerhebungs-Stufe.

Sie ist die vierte Schwester der Methodik-Spec-Familie neben `spec/project/dockerfile-best-practices/`, `spec/project/kubernetes-deployment-best-practices/` und `spec/project/bjw-s-common-chart-deployment/`: Wie sie formuliert sie einen normativen Prozess, den ein nachgelagertes `nolte-engineering`-Skill durchsetzt. Sie unterscheidet sich auf zwei Achsen — sie ist `Portfolio-Scope: portfolio` (vererbbar durch Consumer-Repos, die ihre eigenen KPIs ableiten, gemäß `spec/project/portfolio-inherited-spec-layer/`), und sie gründet ein Tool, dessen read-only Scanner **zwei** Input-Flächen liest (Quellcode *und* Requirement-Dokumente). Sie ist das Definitions-seitige Gegenstück zu `spec/project/requirements-elicitation/` (das Geschäftsziele erfasst) und `spec/project/mission/` (dessen `verifies_via`-Zeiger benennt, wie eine Mission beurteilt wird): Jene liefern die Ziele; diese Spec verwandelt Ziele in definierte KPIs.

Leser: Teams und Repositories, die die aussagekräftigen KPIs ihrer Business-Anwendung ermitteln müssen; die Autoren des künftigen `kpi-derive`-Skills und seines read-only Scanner-Agenten; Consumer-Repositories, die diese Spec by-reference erben. Jede tragende Framework-Aussage wurde gegen Primärquellen verifiziert (siehe §Framework-Anker).

## Ziele

- Der KPI-Satz einer Business-Anwendung wird **top-down abgeleitet** aus ihren Geschäftszielen und Requirements über eine GQM-artige Goal→Question→Kandidaten-KPI-Verfeinerung, nie bottom-up aus dem zusammengesetzt, was der Code exponiert
- Jeder KPI ist **vollständig definiert** gegen einen festen Vertrag (id, name, definition, formula-intent, unit, target/threshold, `leading|lagging`-Typ, owner, goal-linkage, data-source-pointer, rationale), sodass zwei Leser ihn identisch interpretieren
- Jeder KPI **besteht ein SMART-Gate** (Specific, Measurable, Achievable, Relevant, Time-bound); ein KPI, der einen Buchstaben verfehlt, wird als noch-nicht-definiert markiert statt veröffentlicht
- Der Prozess **wählt die wenigen Schlüssel-Indikatoren**: Er fördert viele Kandidaten-Metriken zutage, unterscheidet aber einen **KPI** (eine an ein Geschäftsziel gebundene Schlüssel-Metrik) von einer schlichten Metrik, und nur die ausgewählten, ziel-verknüpften werden KPIs
- Jeder KPI ist **rückverfolgbar auf das Ziel oder Requirement**, das ihn motiviert hat, sodass der KPI-Satz bei Zieländerung neu abgeleitet und auditiert werden kann
- Der Prozess **konsumiert ein vorhandenes Requirement-Artefakt**, wenn vorhanden (`project/requirements/<slug>.md`), als primäre Zielquelle, und **degradiert anmutig** auf `goals.md` / `mission.md` und Quellcode-Signale, wenn es fehlt
- Die abgeleiteten KPI-Definitionen landen in einem **menschenlesbaren, urteils-lesbaren Artefakt** (`project/kpis/<slug>.md`), das das Requirements-Artefakt spiegelt, weil KPI-Auswahl eine Urteilssache ist, kein Maschinen-Dump
- Der Prozess ist **portfolio-vererbbar**: Ein Consumer-Repository referenziert diese Spec auf einem gepinnten Hub-Release und leitet die KPIs seiner eigenen Anwendung gegen denselben Vertrag ab

## Nicht-Ziele

- **Messung, Instrumentierung und Telemetrie.** Einen Zähler emittieren, einen Metrik-Client hinzufügen, OpenTelemetry/Prometheus/StatsD verdrahten, einen KPI zur Laufzeit berechnen oder eine Erhebungs-Pipeline aufstellen ist außerhalb des Scopes. Das Feld `data-source-pointer` benennt, *woher die Daten kämen*; es verdrahtet sie nicht. Dies ist die tragende Grenze der gesamten Spec
- **Speicherung, Aggregation und Dashboarding.** Time-Series-Retention, Roll-ups, feuernde Alert-Schwellen und jede Dashboard-/Report-Fläche (Grafana, ein BI-Tool, eine In-App-Analytics-Seite) gehören zur Mess-Stufe und sind ausgeschlossen
- **GQMs Datenerhebungs-Stufe.** Diese Spec übernimmt GQMs Goal→Question→Metric-*Definitions*-Ebenen; GQMs anschließender Schritt „develop the data collection mechanisms, including validation and analysis" ist genau die oben ausgeschlossene Mess-Arbeit
- **Das Erheben der Geschäftsziele selbst.** Zu erfassen, was das Geschäft erreichen will, gehört `spec/project/requirements-elicitation/`, `spec/project/mission/` und `spec/project/roadmap/`; diese Spec *konsumiert* jene Ziele, sie erhebt sie nicht
- **OKRs, SLAs und SLOs als solche.** Objectives-and-Key-Results, Service-Level-Objectives/-Agreements und Error-Budgets sind angrenzende Zielsetzungs-Frameworks; diese Spec benennt die KPI-vs-KRI/KBI/OKR-Grenze zur Abgrenzung, definiert aber keinen OKR- oder SLO-Prozess
- **Ein fester, universeller KPI-Katalog.** Diese Spec definiert den *Prozess* zur Ableitung projektspezifischer KPIs, nicht eine Konservenliste „der 10 KPIs, die jede App braucht"; die KPIs werden immer aus den Zielen *dieser* Anwendung abgeleitet

## Anforderungen

### Der Ermittlungsprozess (GQM-basierte Ableitung)

- Der Prozess **MUSS** KPIs **top-down** aus Geschäftszielen ableiten, der Goal/Question/Metric-Verfeinerung folgend: aus jedem Ziel die **Fragen** ableiten, die die Zielerreichung charakterisieren, dann aus jeder Frage die **Kandidaten-Metriken** ableiten, die sie beantworten würden. Ein KPI, der nicht auf eine Frage und ein Ziel zurückgeführt werden kann, ist ein Bottom-up-Artefakt und **DARF NICHT** als KPI veröffentlicht werden
- Jedes abgeleitete Ziel **SOLLTE** mit GQMs Ziel-Koordinaten gefasst werden — **purpose** (z. B. verbessern/erhöhen/reduzieren), **issue** (der Qualitäts-/Ergebnis-Fokus, z. B. Conversion, Retention, erlebte Latenz), **object** (das Produkt-Feature, der Geschäftsprozess oder die User-Journey, die gemessen wird) und **viewpoint** (wessen Ziel es ist: der Business-Owner, der Endnutzer, der Betreiber) — damit die abgeleiteten Fragen gut abgegrenzt sind
- Der Prozess **MUSS** die resultierenden Metriken als **Kandidaten** behandeln und einen **Auswahlschritt** anwenden (siehe §„KPI vs. Metrik"), bevor ein Kandidat ein KPI wird; Kandidaten zutage fördern ist mechanisch, die Schlüssel-Indikatoren auswählen ist eine dem Operator vorbehaltene Urteilssache
- Der Prozess **MUSS** wiederholbar sein: Wenn sich die Quell-Ziele ändern, **SOLLTE** die Neu-Ableitung zeigen, welche KPIs weiter gelten, welche neu validiert werden müssen und welche irrelevant geworden sind, statt den Satz still zu ersetzen

### Der Pro-KPI-Definitionsvertrag

- Jeder definierte KPI **MUSS** all diese Felder tragen; ein KPI, dem ein Feld fehlt, ist **noch nicht definiert**:
  - `id` — ein stabiler Kurz-Identifier (z. B. `K1`) für Querverweis und Rückverfolgbarkeit
  - `name` — ein menschenlesbarer Name
  - `definition` — eine Ein-Satz-Klartext-Aussage, was der KPI misst
  - `formula-intent` — die *beabsichtigte* Berechnung in Klartext (z. B. „bezahlte Checkouts ÷ gestartete Checkouts"); sie drückt Intent aus, **DARF NICHT** eine verdrahtete Query oder ein Metrik-Ausdruck sein (das ist Messung)
  - `unit` — die Einheit des Ergebnisses (%, Anzahl, Sekunden, Währung, Verhältnis)
  - `target` / `threshold` — der Wert oder das Band, das als Erfolg zählt, mit seinem Zeithorizont
  - `type` — genau eines von `leading` oder `lagging` (siehe §„Leading vs. Lagging")
  - `owner` — die für den KPI verantwortliche Rolle (der SMART-Buchstabe „Assignable")
  - `goal-linkage` — ein Verweis zurück auf das ursprüngliche Ziel oder Requirement (z. B. eine `project/requirements/<slug>.md`-Requirement-Id, eine `goals.md`-Outcome-Id oder ein Missions-`verifies_via`-Zeiger)
  - `data-source-pointer` — ein Klartext-Zeiger darauf, *woher die zugrunde liegenden Daten kämen* (z. B. „die Orders-Tabelle", „die Login-Events des Auth-Service"); er benennt Provenienz, **DARF NICHT** Erhebung definieren
  - `rationale` — warum dieser KPI für das Geschäftsziel zählt, d. h. warum er die Auswahl vor anderen Kandidaten verdient hat
- Jeder definierte KPI **MUSS** ein **SMART**-Gate bestehen — **Specific**, **Measurable**, **Achievable**, **Relevant**, **Time-bound** — und die Definition **SOLLTE** jeden Buchstaben prüfbar machen: Measurable bildet auf `formula-intent` + `unit` ab, Relevant auf `goal-linkage`, Assignable auf `owner`, Time-bound auf einen `target`-Horizont. Ein Kandidat, der einen SMART-Buchstaben verfehlt, **MUSS** als noch-nicht-definierter offener Punkt erfasst werden, nicht als KPI veröffentlicht

### KPI vs. Metrik, Leading vs. Lagging

- Der Prozess **MUSS** die **KPI-vs-Metrik**-Unterscheidung durchsetzen: Jeder KPI ist eine Metrik, aber eine Metrik wird nur dann zum **KPI, wenn sie *Schlüssel* ist — an ein Geschäftsziel gebunden und als einer der wenigen zählenden Indikatoren ausgewählt**. Der Scanner darf viele Metriken zutage fördern; das Artefakt **MUSS** nur die ausgewählten, ziel-verknüpften KPIs enthalten, mit der Verworfene-Kandidaten-Begründung als Rationale verfügbar, nicht als flacher Dump jeder messbaren Größe
- Jeder KPI **MUSS** als **leading** (ein prädiktiver Input, der sich *vor* einem Ergebnis ändert — Adoption, Aktivierung, Pipeline) oder **lagging** (ein Output, der berichtet, was bereits geschehen ist — Umsatz, Churn, Retention) klassifiziert werden. Ein KPI-Satz, der **ausschließlich lagging** ist, **SOLLTE** markiert werden, weil er nur die Vergangenheit berichten und Handeln nicht steuern kann; ein gesunder Satz paart Lagging-Ergebnisse mit den Leading-Inputs, die sie bewegen
- Die Spec **KANN** eine **North-Star**-Strukturierungs-Konvention unterstützen — ein primärer Lagging-KPI plus die stützenden Leading-KPIs, die ihn treiben — **DARF** sie aber **NICHT** vorschreiben; North-Star ist eine optionale Ordnungs-Linse, kein Pflichtfeld
- Angrenzende Indikator-Typen — **KRI** (Risiko), **KBI** (Verhalten) und **OKR**-Key-Results — **SOLLTEN** nur zur Abgrenzung benannt werden; der Prozess definiert KPIs, und ein Kandidat, der eigentlich ein Risiko- oder Verhaltens-Indikator ist, wird als solcher erfasst und beiseitegelegt

### Input-Quellen und Requirements-Kopplung

- Der Prozess **MUSS** Inputs in dieser Prioritätsreihenfolge sammeln: (1) ein vorhandenes `project/requirements/<slug>.md`-Artefakt (die primäre Geschäftsziel-Quelle), (2) `project/goals.md` und `project/mission.md`, (3) Quellcode-Signale (Domain-Events, aggregierbare Entitäten, Zustandsübergänge, Funnels, Fehlerflächen)
- Wenn **kein** Requirement-Artefakt vorhanden ist, **DARF** der Prozess **NICHT** blockieren: Er **MUSS** warnen, dass die Ziel-Verknüpfung schwächer sein wird, und **SOLLTE** empfehlen, zuerst `requirements-elicit` zu laufen, dann zur Ableitung aus den übrigen Quellen fortfahren. Dies ist ein **Soft-Gate** — ein Code-only-Repository kann trotzdem KPIs aus seinen Zielen und seinem Quellcode ableiten, es leitet sie nur mit einem erfassten Vorbehalt ab. Anders als die Hard-Gate-Consumer, die in `spec/project/requirements-elicitation/` §"H. Consumer contract" benannt sind (`roadmap-plan`, `feature-decompose`, `issue-orchestrate`) und `requirements-elicit` dispatchen oder ein explizites Operator-Override erfassen **MÜSSEN**, bevor sie fortfahren, ist `kpi-derive` ein **bewusster Soft-Gate-Carve-out**: Er fährt allein auf dem erfassten Vorbehalt fort, ohne ein Operator-Override zu verlangen, weil ein Code-und-Ziele-Repository trotzdem einen nützlichen KPI-Satz ableiten kann
- Quellcode ist eine **Kandidaten-Signal-Quelle, nie eine Ziel-Quelle**: Der Prozess **DARF NICHT** ein Geschäftsziel aus Code allein erfinden; Code-Signale füllen Kandidaten-Metriken, die trotzdem auf ein Ziel aus (1) oder (2) zurückführen **MÜSSEN**, um ausgewählt zu werden

### Das Ausgabe-Artefakt

- Die abgeleiteten KPIs **MÜSSEN** nach `project/kpis/<slug>.md` geschrieben werden, das Layout von `project/requirements/` spiegelnd: ein Bounded-Context-/Quellen-Header (der die konsumierten Ziel-Quellen benennt), gefolgt von einem strukturierten Block pro KPI, der jedes Feld von §„Der Pro-KPI-Definitionsvertrag" trägt
- Das Artefakt **MUSS** **menschenlesbares Markdown** sein, kein bloßer Daten-Dump, weil KPI-Auswahl und Rationale Urteils-Inhalt sind, dem ein Leser folgen und den er anfechten können muss; die `goal-linkage` jedes KPIs **MUSS** auf ein reales ursprüngliches Ziel/Requirement auflösen (eine Geister-Verknüpfung ist ein Defekt)
- Das Artefakt **SOLLTE** in seinem Header die verwendeten Framework-Parameter angeben (dass GQM/SMART angewandt wurden) und alle noch-nicht-definierten Kandidaten als benannte offene Punkte auflisten, sodass die Ableitung auditierbar ist

### Tool-Gestalt (Skill + read-only Scanner)

- Der Prozess **MUSS** als **interaktives Skill** (Arbeitsname `kpi-derive`) plus **einem read-only Dual-Source-Scanner-Agenten** operationalisiert werden: Der Scanner führt **nur Detektion** durch — er mined sowohl den Quellbaum als auch die Requirement-/Ziel-Dokumente nach Kandidaten-KPI-Signalen — und das Skill besitzt Kandidaten-**Auswahl**, KPI-**Definition**, die **Operator-Bestätigung** und den **Write**. Das Skill **MUSS** interaktiv bleiben, weil die Schlüssel-KPIs auszuwählen und jede Definition zu bestätigen eine Urteilssache ist; der Scanner **MUSS** read-only und seiteneffektfrei bleiben
- Das Tooling **MUSS** im `nolte-engineering`-Plugin leben (seine Audience sind code-tragende Repositories, weil es Quellcode liest), während diese Spec repo-weit unter `spec/` bleibt. Es **SOLLTE** ein einzelner Dual-Source-Scanner sein statt eines Scanner-Paars, um das Agent-Description-Routing-Budget zu schonen

### Portfolio-Scope und Vererbung

- Diese Spec trägt `Portfolio-Scope: portfolio` und **MUSS** by-reference vererbbar bleiben gemäß `spec/project/portfolio-inherited-spec-layer/`: Ein Consumer-Repository deklariert `inherits:` auf einem gepinnten Hub-`ref` und leitet die KPIs seiner eigenen Anwendung gegen diesen Vertrag ab, ohne den Spec-Text zu kopieren
- Der normative Inhalt der Spec **MUSS** anwendungs-agnostisch sein: Er schreibt den *Prozess und Vertrag* vor, nie eine feste KPI-Liste, sodass jede Business-Anwendung im Portfolio ihn erben und ihre eigenen projektspezifischen KPIs ableiten kann

### Framework-Anker

- Der normative Inhalt der Spec **MUSS** gegen diese verankerten Quellen gelesen werden (verifiziert 2026-07-10): das **GQM**-Paradigma (Basili, Caldiera, Rombach, *The Goal Question Metric Approach*; Ziel-Koordinaten purpose/issue/object/viewpoint; drei Ebenen Goal→Question→Metric; Metriken objektiv oder subjektiv; business-getriebene Ziele als Input) für das Ableitungs-Rückgrat und die Mess-Stufen-Grenze; **SMART** (G. T. Doran, „There's a S.M.A.R.T. way to write management's goals and objectives", *Management Review*, 1981) für das Pro-KPI-Gate; die **Leading-vs-Lagging**-Indikator-Unterscheidung (leading = prädiktive Inputs, lagging = realisierte Outputs) für die Klassifikation; und die **KPI-vs-Metrik**-Grenze (ein KPI ist eine *Schlüssel*-Metrik, an ein Geschäftsergebnis gebunden) für die Auswahl
- Eine `kpi-derive`-Implementierung **MUSS** jede Ableitung in diesen Frameworks verankern und **DARF NICHT** die Mess-Grenze überschreiten: Sie definiert KPIs, sie emittiert nie Instrumentierung, einen Metrik-Client oder eine Erhebungs-Pipeline
- Jede Framework-Attribution oben ist eine Author-Time-externe Aussage und **MUSS** gemäß `spec/claude/research-triangulate/` §"Author-time assertions" auf mindestens drei unabhängige Quellen trianguliert werden; die Quellenliste (URL, Quellklasse, Abrufdatum, Primary-first) ist in §Quellen erfasst

## Akzeptanzkriterien

- [ ] `spec/project/kpi-definition-process/` existiert mit `en.md` (kanonisch) und `de.md` (Übersetzung), trägt `Portfolio-Scope: portfolio` und ist in `spec/README.md` gelistet
- [ ] Der Ermittlungsprozess ist als **top-down GQM-Verfeinerung** (Goal → Question → Kandidaten-Metrik) mit den Ziel-Koordinaten (purpose/issue/object/viewpoint) und einem Pflicht-Auswahlschritt formuliert
- [ ] Die **Wiederholbarkeit bei geänderten Zielen** ist eine formulierte Anforderung, und die Neu-Ableitung zeigt, welche KPIs weiter gelten, welche neu validiert werden müssen und welche irrelevant wurden (statt den Satz still zu ersetzen)
- [ ] Der **Pro-KPI-Definitionsvertrag** listet jedes Pflichtfeld (id, name, definition, formula-intent, unit, target/threshold, type, owner, goal-linkage, data-source-pointer, rationale) mit RFC-2119-Keywords, und `formula-intent`/`data-source-pointer` sind explizit *nur Intent/Provenienz*, keine verdrahtete Messung
- [ ] Das **SMART**-Gate ist pro KPI verpflichtend, mit jedem Buchstaben auf ein Vertragsfeld abgebildet, und ein verfehlender Kandidat wird als noch-nicht-definiert erfasst statt veröffentlicht
- [ ] Die **KPI-vs-Metrik**-Auswahlregel und die verpflichtende **`leading|lagging`**-Klassifikation sind formuliert, mit dem All-Lagging-Flag und der optionalen (nicht vorgeschriebenen) North-Star-Konvention
- [ ] Die **KRI/KBI/OKR-Abgrenzung** (nur benannt, dann beiseitegelegt) ist formuliert, sodass ein Angrenzender-Indikator-Kandidat als solcher erfasst statt fälschlich als KPI veröffentlicht wird
- [ ] Die **Input-Priorität** (Requirements → Goals/Mission → Quellcode) und das **Soft-Gate**-Verhalten bei fehlendem Requirement-Artefakt (warnen + empfehlen, nicht blockieren) sind formuliert, und Quellcode ist als Ziel-Quelle ausgeschlossen
- [ ] Das **Ausgabe-Artefakt** `project/kpis/<slug>.md` ist spezifiziert: menschenlesbar, `project/requirements/` spiegelnd, ein Block pro KPI, goal-linkage auf ein reales Ziel auflösend
- [ ] Der **Header** des Ausgabe-Artefakts ist spezifiziert, die verwendeten Framework-Parameter (GQM/SMART angewandt) anzugeben und alle noch-nicht-definierten Kandidaten als benannte offene Punkte aufzulisten, sodass die Ableitung auditierbar ist
- [ ] Die **Tool-Gestalt** ist spezifiziert: ein interaktives `kpi-derive`-Skill + ein read-only Dual-Source-Scanner-Agent in `nolte-engineering`, wobei das Skill Auswahl/Definition/Write besitzt und der Scanner read-only ist
- [ ] Die **harte Mess-Grenze** (keine Instrumentierung, Telemetrie, Erhebung, Speicherung, Aggregation, Dashboarding; GQMs Datenerhebungs-Stufe ausgeschlossen) ist in §Nicht-Ziele formuliert und in den Anforderungen bekräftigt
- [ ] Die **Framework-Anker** sind gepinnt: GQM (Basili/Caldiera/Rombach), SMART (Doran 1981), Leading/Lagging, KPI-vs-Metrik — und §Quellen erfasst mindestens drei unabhängige Quellen pro Attribution mit URL, Quellklasse und Abrufdatum gemäß `spec/claude/research-triangulate/`
- [ ] Die Spec ist **anwendungs-agnostisch und portfolio-vererbbar**: Sie schreibt Prozess und Vertrag vor, keine feste KPI-Liste, und bleibt referenzierbar gemäß `spec/project/portfolio-inherited-spec-layer/`

## Offene Fragen

- **Scanner-Signal-Taxonomie.** Der genaue Katalog dessen, was als KPI-Signal im Quellcode zählt (Domain-Events, aggregierbare Entitäten, Zustandsübergänge, Funnel-Schritte, Fehlerflächen) versus in Requirement-Dokumenten (Akzeptanzkriterien, nicht-funktionale Zielwerte, Geschäftsergebnisse), wird aufgezählt, wenn der `kpi-derive`-Scanner autort wird; diese Spec fixiert die zwei Quell-Flächen und die goal-linkage-Regel, nicht die Pro-Signal-Heuristiken
- **Genaue Skill-/Agent-Namen.** Arbeitsnamen `kpi-derive` (Skill) und `kpi-signal-scanner` (Agent) werden zum Skill-Authoring-Zeitpunkt gegen `<object-noun>-<action>`-Naming und Katalog-Discoverability bestätigt
- **North-Star-Durchsetzung.** Ob ein Repository per lokalem Override *opt-in* einen deklarierten North-Star-KPI (ein primärer Lagging + stützende Leading) verlangen darf, da die Spec ihn standardmäßig optional hält
- **Cross-Artefakt-Drift.** Wenn sich `project/requirements/<slug>.md` ändert, nachdem `project/kpis/<slug>.md` geschrieben wurde, ob ein Drift-Check zwischen beiden (analog zum Translation-vs-kanonisch-Drift-Check) eine `kpi-derive`-Operation sein oder an ein breiteres Freshness-Audit delegiert werden sollte

## Quellen

Die Framework-Attributionen in §"Framework-Anker" sind Author-Time-externe Aussagen, trianguliert gemäß `spec/claude/research-triangulate/` (Author-Time-Stufe: mindestens drei unabhängige Quellen, Primary-first geordnet). Abrufdatum für jede Quelle unten: 2026-07-10.

- **GQM (Goal/Question/Metric)** — V. R. Basili, G. Caldiera, H. D. Rombach, *The Goal Question Metric Approach* (Primary), `https://www.cs.umd.edu/users/mvz/handouts/gqm.pdf`; R. van Solingen, E. Berghout, *The Goal/Question/Metric Method: A Practical Guide* (Secondary, Wiley), `https://onlinelibrary.wiley.com/doi/10.1002/0471028959.sof142`; *GQM* (Tertiary, Wikipedia), `https://en.wikipedia.org/wiki/GQM`
- **SMART** — G. T. Doran, „There's a S.M.A.R.T. way to write management's goals and objectives", *Management Review* 70(11), 1981 (Primary, historischer Ursprungsartikel); *SMART criteria* (Tertiary, Wikipedia), `https://en.wikipedia.org/wiki/SMART_criteria`; *SMART Goals* (Secondary, MindTools), `https://www.mindtools.com/a4wo118/smart-goals/`; *SMART goals* (Secondary, TechTarget WhatIs), `https://www.techtarget.com/whatis/definition/SMART-SMART-goals`
- **Leading vs. Lagging Indicators** — *Leading vs Lagging Indicators* (Secondary, BMC), `https://www.bmc.com/blogs/leading-vs-lagging-indicators/`; *Leading vs. Lagging Indicators* (Secondary, Amplitude), `https://amplitude.com/blog/leading-lagging-indicators`; *Leading and Lagging Indicators* (Secondary, Klipfolio), `https://www.klipfolio.com/blog/leading-and-lagging-indicators`
- **KPI vs. Metrik** — *Leading vs Lagging / KPI vs metric* (Secondary, BSC Designer), `https://bscdesigner.com/leading-vs-lagging.htm`; *Leading vs. Lagging KPIs* (Secondary, SuccessCOACHING), `https://successcoaching.co/blog/leading-vs-lagging-kpis`; *Metrics and KPIs* (Secondary, Geckoboard), `https://www.geckoboard.com/blog/leading-lagging-or-lost-how-to-find-the-right-key-performance-indicators-for-your-sales-team/`
