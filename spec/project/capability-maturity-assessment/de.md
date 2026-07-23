# Reifegrad-Bewertung fachlicher Funktionen

Status: draft
Portfolio-Scope: portfolio

## Kontext

Eine laufende Anwendung sammelt Dutzende fachlicher Funktionen an — „einen Standort anlegen", „eine Winterhärtezone erkennen", „eine Druckansicht exportieren" — und Stakeholder stellen dazu immer wieder dieselben zwei Fragen: *für wen ist jede Funktion*, und *wie fertig ist sie wirklich?* Die zweite Frage verbirgt drei getrennte, die Teams routinemäßig zu einem einzigen Bauchgefühl kollabieren lassen: ist die Funktion **vollständig gebaut** gegen das, was sie versprach, ist sie **gut gebaut** als Code, und ist sie **vertrauenswürdig gebaut**, also durch Tests auf den richtigen Stufen verifiziert. Eine Funktion kann feature-vollständig, aber ungetestet sein, oder makellos getestet und doch ein dünner Stub — und eine Ein-Wort-Antwort („fertig") löscht diesen Unterschied. Was fehlt, ist ein **wiederholbarer, top-down Prozess**, der die fachlichen Funktionen der Anwendung inventarisiert, jede an die Zielgruppen bindet, die sie bedient, und den *Bau-Reifegrad* jeder Funktion entlang dieser drei Achsen auf einer geteilten, verteidigbaren Skala einstuft.

Diese Spec definiert diesen Prozess. Sie regelt, wie man die fachlichen Capabilities einer Anwendung **inventarisiert**, jede an die Zielgruppen **zuordnet**, die sie bedient (das Zielgruppen-Artefakt konsumierend statt es neu zu erfinden), und jede Capability **pro Achse** in ein **Bronze- / Silber- / Gold**-Reifegrad-Tier **klassifiziert** — Umsetzungsgrad, Code-Qualität und Testabdeckung über die Teststufen — plus ein **separates Gesamt-Tier**, das aus diesen Achsen abgeleitet wird. Sie fixiert die *Kriterien und den Vertrag*, nicht eine feste Funktionsliste: jede Anwendung im Portfolio erbt dieselbe Rubrik und erzeugt ihre eigene Capability-Matrix.

Die Drei-Medaillen-Einstufung ist nicht ad hoc erfunden: gestufte Projekt-Qualitätsstufen mit genau der Bronze/Silber/Gold-Form sind die etablierte Konvention des **OpenSSF Best Practices Badge** (passing/silver/gold) [R11], die drei Bewertungsachsen sind je in einem etablierten Praxis-Korpus verankert (das ISO/IEC-25010-Produktqualitätsmodell für Code-Qualität [R8], McCabes zyklomatische Komplexität als Wartbarkeits-Signal [R9], das portfolio-eigene Testpyramiden-Fundament für die Test-Achse [R2]), und die bewusste Abgrenzung von *Prozess*-Reifegradmodellen (CMMI [R12]) hält die Bewertung beim Produkt, nicht bei der Organisation.

Die Spec zieht eine **harte Grenze**: Sie regelt *nur Inventarisierung, Zielgruppen-Zuordnung und Einstufung*. In dem Moment, in dem das Tier einer Capability zugewiesen und in die Matrix geschrieben ist, stoppt der Prozess. Ein Tier als Merge-Gate durchzusetzen, zu priorisieren, welche Bronze-Capability als Nächstes befördert wird, oder die Einstufung in ein Dashboard zu verdrahten, ist **nachgelagerte Aktion**, außerhalb des Scopes (siehe §Nicht-Ziele). Insbesondere ist diese Spec **kein** Pass/Fail-Quality-Gate: `spec/project/quality-gate/` [R3] beantwortet „darf dieser PR mergen?" binär; diese Spec beantwortet „wie reif ist diese Capability?" mit einer gestuften, beratenden Einstufung, die nie einen Merge blockiert.

Sie ist der Form nach eine Schwester von `spec/project/kpi-definition-process/` [R7] — beide sind `Portfolio-Scope: portfolio`-Methodik-Specs, die ein nachgelagertes `nolte-engineering`-Skill gründen, dessen read-only Scanner den Quellbaum liest, und beide trennen mechanische Detektion von einer menschlichen Urteilssache. Sie unterscheiden sich in der Frage: KPIs messen *Geschäftsergebnisse zur Laufzeit* (hat die App ihr Ziel erreicht?), diese Spec misst *Bau-Reifegrad einer Capability* (ist die Funktion vollständig, gut und verifizierbar gebaut?). Die beiden komponieren — eine Gold-Tier-Capability kann dennoch ein schlechtes KPI treiben, und ein kritisches KPI kann auf einer Bronze-Tier-Capability ruhen, die Beförderung braucht.

Leser: Teams, die wissen müssen, wie vollständig und vertrauenswürdig jede Funktion ihrer Anwendung ist und für wen; die Autoren des künftigen `maturity-assess`-Skills und seines read-only Scanner-Agenten; Reviewer, die eine Reifegrad-Matrix prüfen; Consumer-Repositories, die diese Spec by-reference erben.

## Ziele

- Die fachlichen Capabilities der Anwendung werden **top-down inventarisiert** als nutzer-bedeutsame Funktionen, rückverfolgbar auf Requirements, nicht bottom-up aus den zufällig existierenden Code-Modulen
- Jede Capability wird an die **Zielgruppen zugeordnet, die sie bedient**, das Artefakt aus `spec/project/audience-identification/` [R1] konsumierend, sodass „für wen ist das" aus einer autoritativen Liste beantwortet wird, nicht aus einer privaten Annahme
- Jede Capability wird auf **drei expliziten, unabhängigen Achsen** eingestuft — Umsetzungsgrad, Code-Qualität und Testabdeckung über die Teststufen — sodass die „wie fertig ist es"-Frage zerlegt statt kollabiert wird
- Jede Achse wird in eines von **Bronze / Silber / Gold** gegen eine ausformulierte Rubrik klassifiziert, mit einem vierten impliziten **Unrated**-Boden für eine Capability, die auf dieser Achse Bronze noch nicht erreicht
- Ein **separates Gesamt-Tier** wird aus den drei Achsen-Tiers per **Weakest-Link**-Regel abgeleitet und *neben* den Pro-Achse-Tiers berichtet, sodass ein Leser sowohl die Zusammenfassung als auch deren Herkunft sieht
- Die Einstufung trennt sauber **maschinell ableitbare Signale** (statische Analyse, Komplexität, Coverage, Teststufen-Präsenz, CI-Status) von **Urteils-Eingaben** (Zielgruppen-Zuordnung, Vollständigkeit gegen Akzeptanzkriterien), sodass der Prozess automatisierbar ist, wo er es sein kann, und ehrlich, wo er es nicht kann
- Die eingestuften Capabilities landen in einem **menschenlesbaren, urteils-lesbaren Artefakt** (`project/maturity/<slug>.md`), dem ein Leser folgen und das er anfechten kann, weil ein Reifegrad-Tier eine verteidigbare Behauptung ist, kein Maschinen-Dump
- Tier-Schwellenwerte (Coverage-Bänder, Komplexitäts-Obergrenzen) sind **projekt-konfigurierbare Parameter** mit einer festen Monotonie-Invariante, sodass die *Rubrik-Struktur* portfolioweit ist, während die *Zahlen* zu jedem Stack passen
- Der Prozess ist **portfolio-vererbbar**: Ein Consumer-Repository referenziert diese Spec auf einem gepinnten Hub-Release und stuft die Capabilities seiner eigenen Anwendung gegen denselben Vertrag ein

## Nicht-Ziele

- **Ein Tier als Gate durchsetzen.** Einen Merge blockieren, CI fehlschlagen lassen oder ein Release verweigern, weil eine Capability unter einem Ziel-Tier liegt, ist nachgelagerte Aktion; diese Spec erzeugt eine beratende Einstufung, nie ein Gate. Die binäre Merge-Entscheidung bleibt Eigentum von `spec/project/quality-gate/` [R3]
- **Priorisierung und Roadmapping.** Zu entscheiden, *welche* Bronze-Capability als Nächstes befördert wird, oder Beförderungs-Arbeit zu sequenzieren, ist eine Planungsentscheidung, die `spec/project/roadmap/` und `spec/project/sprint/` gehört; diese Spec stuft den Ist-Zustand ein, sie plant nicht den nächsten
- **Dashboarding und Trend-Verfolgung.** Die Matrix in ein Dashboard rendern, Tier-Bewegung über die Zeit verfolgen oder auf Regressionen alerten ist ein Mess-/Darstellungs-Anliegen außerhalb des Scopes
- **Die Zielgruppen der Anwendung definieren.** Zielgruppen zu enumerieren und zu charakterisieren gehört `spec/project/audience-identification/` [R1]; diese Spec *konsumiert* jenes Artefakt, sie erzeugt es nicht
- **Die Teststufen oder die Coverage-als-Leitfaden-Regel neu definieren.** Die funktionale Teststufen-Taxonomie (static → unit → component → integration → contract → E2E) und die „Coverage ist ein Leitfaden, kein Zielwert"-Governance-Regel gehören `spec/project/test-pyramid-foundation/` [R2]; die Test-Achse *konsumiert* sie
- **Eine feste, universelle Capability-Liste.** Diese Spec definiert den *Prozess und die Rubrik* zur Einstufung projektspezifischer Capabilities, nicht einen Konserven-Katalog „der Funktionen, die jede App hat"; die Capabilities werden immer aus *dieser* Anwendung inventarisiert
- **Organisations- oder Prozessreife bewerten.** CMMI-artige Prozess-Reifegrad-Stufen [R12] stufen ein, wie eine Organisation Software baut; diese Spec stuft ein, wie reif eine gebaute Capability ist. Die Namensähnlichkeit ist zufällig und die Grenze bewusst

## Anforderungen

### Das Capability-Inventar

- Der Prozess **MUSS** **fachliche Capabilities** inventarisieren: nutzer-bedeutsame Funktionseinheiten, die eine benannte Zielgruppe als etwas erkennt, das die Anwendung tut (z. B. „eine Ernte erfassen", „eine Klimazone erkennen"), jede rückverfolgbar auf ein Requirement oder Akzeptanzkriterium. Eine Capability **DARF NICHT** als Code-Artefakt (ein Modul, eine Klasse, ein Endpoint) definiert werden; Code-Artefakte sind der *Beleg*, gegen den eine Capability eingestuft wird, nicht die Einheit der Einstufung
- Das Inventar **MUSS** **top-down** aus den Requirements, dem Feature-Set oder der nutzerseitigen Oberfläche der Anwendung abgeleitet werden und **DARF NICHT** bottom-up aus der Verzeichnisstruktur zusammengesetzt werden; eine Capability, die nicht auf etwas zurückgeführt werden kann, das ein Nutzer oder eine Zielgruppe will, ist ein Code-Artefakt, keine Capability
- Jede Capability **MUSS** einen stabilen Kurz-Identifier (z. B. `C1`) für Querverweise, einen menschenlesbaren Namen und eine Ein-Satz-Beschreibung dessen tragen, was die Funktion für ihre Zielgruppe tut
- Der Prozess **MUSS** wiederholbar sein: Wenn sich die Anwendung ändert, **SOLLTE** die Neu-Bewertung zeigen, welche Capabilities ihr Tier hielten, welche aufstiegen und welche regredierten, statt die Matrix still zu ersetzen

### Zielgruppen-Zuordnung

- Jede Capability **MUSS** an **mindestens eine Zielgruppe** aus dem `spec/project/audience-identification/` [R1]-Artefakt des Repositories (`AUDIENCES.md` oder seine ratifizierte Alternative) zugeordnet werden. Eine Capability, die keiner identifizierbaren Zielgruppe dient, ist ein Defekt im Inventar — entweder ist die Zielgruppenliste unvollständig oder die Capability ist tot
- Der Prozess **MUSS** das vorhandene Zielgruppen-Artefakt konsumieren und **DARF NICHT** Zielgruppen neu ableiten oder erfinden; wenn kein Zielgruppen-Artefakt existiert, **MUSS** der Prozess warnen, dass die Zielgruppen-Zuordnung nicht verfügbar ist, und **SOLLTE** empfehlen, zuerst die Audience-Identification-Methode laufen zu lassen, dann fortfahren mit der Zuordnung als offenem Punkt vermerkt (ein **Soft-Gate**, die Carve-out der Schwester-KPI-Spec spiegelnd [R7])
- Das Reifegrad-Tier einer Capability wird standardmäßig **pro Capability** zugewiesen; wo der Reifegrad **materiell nach Zielgruppe divergiert** (z. B. die Funktion ist Gold für die primäre Zielgruppe, aber der Pfad für eine sekundäre Zielgruppe ist ein Bronze-Stub), **SOLLTE** der Prozess die Pro-Zielgruppe-Divergenz vermerken, statt sie zu einem einzigen Tier zu flachen

### Die drei Bewertungsachsen

- Jede Capability **MUSS** auf genau diesen **drei unabhängigen Achsen** eingestuft werden, jede klassifiziert in Bronze / Silber / Gold (oder Unrated unter Bronze):
  - **Achse A — Umsetzungsgrad**: wie vollständig die Capability gegen das gebaut ist, was sie versprach (ihre Akzeptanzkriterien / ihr Requirement)
  - **Achse B — Code-Qualität**: wie gut der Code, der die Capability realisiert, gebaut ist, gemäß dem ISO/IEC-25010-Produktqualitätsmodell [R8] und statischen-Analyse-Signalen
  - **Achse C — Testabdeckung über die Teststufen**: wie vertrauenswürdig die Capability durch automatisierte Tests auf den passenden Stufen der Testpyramide [R2] verifiziert ist
- Die drei Achsen **MUSS**en **unabhängig** eingestuft und berichtet werden; eine starke Achse **DARF NICHT** eine schwache auf Achsen-Ebene still kompensieren (Kompensation ist durch die Weakest-Link-Gesamtregel unten explizit verboten). Dies ist die tragende Zerlegung der gesamten Spec: „wie fertig ist es" sind drei Fragen, nicht eine

### Achse A — Umsetzungsgrad

- Achse A **MUSS** gegen die **Akzeptanzkriterien / das Requirement** der Capability eingestuft werden, die abstrakten Fälle von `spec/project/test-case-derivation/` [R4] und die Akzeptanzkriterien von `spec/project/spec-driven-development/` [R5] konsumierend, wo sie existieren; wo nicht, **MUSS** der Bewerter die verwendete Vollständigkeits-Baseline angeben, weil Vollständigkeit ohne ein „vollständig gegen was?" bedeutungslos ist
- Die Tier-Rubrik für Achse A **MUSS** sein:
  - **Bronze**: der Kern-Happy-Path ist implementiert und für seine Zielgruppe erreichbar; mindestens das primäre Akzeptanzkriterium ist erfüllt; sichtbare Lücken, Stubs oder TODOs sind erlaubt; Fehlerbehandlung und Randfälle sind nicht erforderlich
  - **Silber**: alle dokumentierten Akzeptanzkriterien der Capability sind erfüllt; die wesentlichen Fehler- und Validierungspfade sind behandelt; es gibt keine bekannten funktionalen Lücken auf dem primären Zielgruppen-Pfad; die Capability ist über ihre volle Fläche (z. B. API + UI + i18n) für diesen Pfad vollständig
  - **Gold**: Silber, plus Rand- und Fehlerfälle sind behandelt, die auf die Capability zutreffenden nicht-funktionalen Anforderungen sind erfüllt (z. B. Performance, Barrierefreiheit, Sicherheit, Datenschutzpflichten), es gibt keine offenen funktionalen Defekte oder TODOs gegen sie, und Endnutzer-Dokumentation existiert für jede zugeordnete Zielgruppe
- Achse A ist **primär eine Urteils-Eingabe** (siehe §„Maschinell ableitbare vs. Urteils-Eingaben"): Vollständigkeit gegen Akzeptanzkriterien zu bewerten erfordert das Lesen des Requirements, was ein Scanner nicht kann; der Scanner **KANN** Signale zutage fördern (Unimplemented-Marker, `TODO`/`FIXME`, Feature-Flags, Stub-Rückgaben), **DARF** aber das Achse-A-Tier **NICHT** zuweisen

### Achse B — Code-Qualität

- Achse B **MUSS** im **ISO/IEC-25010**-Produktqualitätsmodell [R8] verankert sein — prinzipiell in seiner *Wartbarkeits*-Charakteristik (Modularität, Wiederverwendbarkeit, Analysierbarkeit, Modifizierbarkeit, Testbarkeit) — und in der statischen-Analyse-Stufe des Portfolios (`spec/project/test-tier-static-analysis/`), gelesen gegen die repository-eigenen Style Guides
- Die Tier-Rubrik für Achse B **MUSS** sein:
  - **Bronze**: der Code baut/läuft und besteht die statische Analyse (Lint, Type-Check, Format-Check) mit **keinen Fehlern** (Warnungen erlaubt); der anwendbare Style Guide wird grob befolgt
  - **Silber**: die statische Analyse besteht mit **keinen Warnungen**; der Style Guide wird vollständig befolgt; die Architektur-Schichtung / Modul-Grenzen des Projekts werden respektiert; die zyklomatische Komplexität [R9] liegt unter der konfigurierten Obergrenze des Projekts und die Duplizierung unter dessen konfigurierter Schranke; der Code ist typisiert, wo der Stack es unterstützt
  - **Gold**: Silber, plus öffentliche Schnittstellen sind dokumentiert, es gibt keine verbleibenden Code-Smells oder Tech-Debt-Marker, sicherheitsorientierte statische Regeln (SAST) bestehen sauber, die Komplexität ist durchweg niedrig statt bloß unter Obergrenze, und der Code hat ein menschliches Review bestanden
- Achse B ist **weitgehend maschinell ableitbar**: statischer-Analyse-Status, Komplexitäts-Metriken, Duplizierung und Type-Coverage sind Scanner-Signale; der **Gold**-Schritt („keine verbleibenden Smells", „menschliches Review bestanden") behält eine Urteils-Komponente, die das Skill **MUSS** bestätigen statt schlussfolgern

### Achse C — Testabdeckung über die Teststufen

- Achse C **MUSS** die funktionale Teststufen-Taxonomie und Governance-Regeln von `spec/project/test-pyramid-foundation/` [R2] konsumieren und **DARF NICHT** eine Stufe neu definieren. Sie stuft eine Capability danach ein, **welche Teststufen sie verifizieren und ob sie bestehen**, nicht nach einer einzigen Coverage-Zahl
- Die Tier-Rubrik für Achse C **MUSS** sein:
  - **Bronze**: die Kernlogik der Capability ist durch **Unit**-Tests abgedeckt, die bestehen, und die statische Analyse ist grün; die Line-/Branch-Coverage der Capability erreicht das konfigurierte **untere** Band des Projekts
  - **Silber**: Bronze, plus **Component- und/oder Integration**-Tests üben die Capability, und **Contract**-Tests decken jede Service-Grenze ab, die sie überschreitet; die Coverage erreicht das konfigurierte **mittlere** Band; jede dieser Stufen besteht in der CI
  - **Gold**: Silber, plus mindestens ein **End-to-End**-Test treibt die Capability durch den realen Workflow einer zugeordneten Zielgruppe, Fehler- und Randfälle sind getestet, die Coverage erreicht das konfigurierte **obere** Band, und jeder Test ist auf die Capability rückverfolgbar, die er verifiziert (gemäß der Requirement→TC-ID→Test-Kette von [R2])
- Achse C **MUSS** die **Coverage-als-Leitfaden**-Regel der Testpyramide [R2], [R10] achten: die Coverage-Bänder sind ein **gestuftes Reifegrad-Signal, rein beratend**, und ein Band zu erreichen **DARF** von dieser Spec **NICHT** in ein PR-Merge-Gate verwandelt werden (Gating bleibt bei `quality-gate` [R3]). Wo die Toolchain es unterstützt, **SOLLTE** der **Mutation-Score** als das stärkere Suite-Qualitäts-Signal neben der Coverage berichtet werden, genau wie [R2] es fordert
- Achse C ist **weitgehend maschinell ableitbar** (Stufen-Präsenz, Pass/Fail-Status, Coverage %, Mutation-Score), mit einem Urteils-Rest dafür, ob ein E2E-Test echt den Workflow der *zugeordneten Zielgruppe* übt

### Pro-Achse-Tier und das Gesamt-Tier

- Jede Capability **MUSS** mit **allen drei Pro-Achse-Tiers explizit** berichtet werden (Achse A, Achse B, Achse C), nie nur mit einer Zusammenfassung; die Pro-Achse-Aufschlüsselung ist, wo die Information der Bewertung liegt
- Ein **separates Gesamt-Tier MUSS** per **Weakest-Link**-Regel abgeleitet werden: das Gesamt-Tier ist das **Minimum** der drei Achsen-Tiers (Gold nur, wenn *jede* Achse Gold ist; Silber, wenn die schwächste Achse Silber ist; Bronze, wenn irgendeine Achse Bronze ist; Unrated, wenn irgendeine Achse unter Bronze ist). Eine starke Achse **DARF NICHT** eine schwache im Gesamt-Tier kompensieren
- Das Gesamt-Tier und die drei Achsen-Tiers **MUSS**en beide in der Matrix erscheinen; der Prozess **DARF** sie **NICHT** in das Gesamt-Tier allein kollabieren, weil die Achsen-Divergenz *der* handlungsleitende Inhalt ist
- Wo die Achsen divergieren (z. B. Achse B Gold, Achse C Bronze), **SOLLTE** der Prozess die Divergenz als expliziten **Verbesserungs-Hebel** vermerken — die eine Achse, die, wenn angehoben, das Gesamt-Tier anheben würde — sodass die Matrix als Anleitung liest, nicht bloß als Anzeigetafel

### Maschinell ableitbare vs. Urteils-Eingaben

- Der Prozess **MUSS** jede Einstufungs-Eingabe klassifizieren als **maschinell ableitbar** (ein read-only Scanner kann sie berechnen: statischer-Analyse-Status, zyklomatische Komplexität, Duplizierung, Type-Coverage, Pro-Stufe-Testpräsenz und -Pass/Fail, Coverage %, Mutation-Score, `TODO`/Stub-Marker) oder **Urteil** (ein Mensch muss sie entscheiden: Zielgruppen-Zuordnung, Vollständigkeit gegen Akzeptanzkriterien, ob eine NFR erfüllt ist, ob ein E2E-Test den zugeordneten Workflow übt, ob Gold-Level-Smells verbleiben)
- Der read-only Scanner **MUSS** **nur Detektion** leisten und **DARF** kein finales Tier zuweisen; das interaktive Skill besitzt die Tier-Zuweisung, die Urteils-Eingaben, die Operator-Bestätigung und den Schreibvorgang. Dies spiegelt die Scanner/Skill-Naht der Schwester-KPI-Spec [R7] und die Read-only-Agent-Disziplin von `spec/claude/`
- Wo eine Achse weitgehend maschinell ableitbar ist (B und C), **SOLLTE**n die Signale des Scanners ein **vorgeschlagenes** Tier erzeugen, das das Skill bestätigt oder überschreibt; wo eine Achse primär Urteil ist (A), liefert der Scanner Belege, aber das Skill weist das Tier von Anfang an zu

### Das Ausgabe-Artefakt

- Die eingestuften Capabilities **MUSS**en nach `project/maturity/<slug>.md` geschrieben werden, das Layout von `project/kpis/<slug>.md` spiegelnd: ein Header, der den Inventar-Scope, das konsumierte Zielgruppen-Artefakt und die konfigurierten Schwellenwerte benennt, gefolgt von einem strukturierten Block (oder einer Tabellenzeile) pro Capability
- Jeder Capability-Block **MUSS** tragen: `id`, `name`, `description`, zugeordnete `audience(s)`, die drei Pro-Achse-Tiers (A/B/C), das abgeleitete `overall`-Tier, den `improvement-lever` (die als Nächstes anzuhebende Achse) und eine kurze `rationale`, die jedes Achsen-Tier verteidigbar macht; wo der Reifegrad nach Zielgruppe divergiert, **MUSS** die Pro-Zielgruppe-Divergenz vermerkt werden
- Das Artefakt **MUSS** **menschenlesbares Markdown** sein, kein bloßer Daten-Dump, weil ein Reifegrad-Tier eine verteidigbare Behauptung ist, der ein Leser folgen und die er anfechten können muss; die Zielgruppen-Zuordnung jeder Capability **MUSS** auf eine reale Zielgruppe im konsumierten Artefakt auflösen (eine Geister-Zielgruppe ist ein Defekt)
- Der Header **SOLLTE** die verwendeten Rubrik-Parameter angeben (die konfigurierten Coverage-Bänder und die Komplexitäts-Obergrenze) und jede Capability, deren Achse A mangels Akzeptanzkriterien nicht eingestuft werden konnte, als benannten offenen Punkt auflisten, sodass die Bewertung auditierbar ist

### Schwellenwerte sind projekt-konfigurierbar

- Die **numerischen Schwellenwerte**, auf die die Rubrik verweist — die unteren/mittleren/oberen Coverage-Bänder (Achse C) und die Komplexitäts-Obergrenze und Duplizierungs-Schranke (Achse B) — **MUSS**en **projekt-konfigurierbare Parameter** sein, keine in dieser Spec hartcodierten Werte, sodass die Rubrik-Struktur portfolioweit ist, während die Zahlen zu jedem Stack und jeder Sprache passen
- Die konfigurierten Schwellenwerte **MUSS**en die **Monotonie-Invariante** `Bronze ≤ Silber ≤ Gold` auf jedem eingestuften Band erfüllen; eine Konfiguration, die die Bänder invertiert oder flacht, ist ungültig
- Diese Spec **KANN** Start-Defaults empfehlen, **DARF** aber keinen universellen Coverage-Prozentsatz oder keine universelle Komplexitäts-Zahl **mandatieren**; ein fester universeller Schwellenwert widerspräche sowohl dem application-agnostischen Ziel als auch der Coverage-als-Leitfaden-Regel [R2]

### Tooling-Form (Skill + read-only Scanner)

- Der Prozess **MUSS** als **interaktives Skill** (Arbeitsname `maturity-assess`) plus **ein read-only Scanner-Agent** (Arbeitsname `capability-maturity-scanner`) operationalisiert werden: der Scanner schürft im Quellbaum nach den maschinell ableitbaren Signalen der Achsen B und C und den Achse-A-Beleg-Markern; das Skill besitzt das Inventar, die Zielgruppen-Zuordnung, die Urteils-Achsen, die Tier-Zuweisung, die Operator-Bestätigung und den Schreibvorgang. Das Skill **MUSS** interaktiv bleiben, weil Inventar, Zielgruppen-Zuordnung und Vollständigkeit Urteilssachen sind; der Scanner **MUSS** read-only und nebenwirkungsfrei bleiben
- Das Tooling **MUSS** im `nolte-engineering`-Plugin leben — seine Zielgruppe sind code-tragende Repositories, weil der Scanner Quellcode und Testergebnisse liest — während diese Spec repo-weit unter `spec/` bleibt
- Das Tooling **SOLLTE** ein einzelner Scanner sein statt eines Scanners-pro-Achse, um das Agent-Description-Routing-Budget von `spec/claude/` zu respektieren

### Abgrenzung gegen benachbarte Specs

- Gegen `spec/project/quality-gate/` [R3]: Quality-Gate ist ein **binäres PR-Gate** über die schnellen Stufen; diese Spec ist eine **gestufte, beratende Einstufung** pro Capability. Eine Capability kann gesamt Bronze sein und dennoch das Quality-Gate bestehen, und umgekehrt; die beiden ersetzen einander nie
- Gegen `spec/project/test-pyramid-foundation/` [R2] und die `test-tier-*`-Specs: jene **besitzen** die Stufen-Definitionen, die Coverage-als-Leitfaden-Regel und die Rückverfolgbarkeits-Kette; Achse C **konsumiert** sie und fügt nur die *Einstufungs-Bänder* hinzu, nie eine neue Stufe
- Gegen `spec/project/kpi-definition-process/` [R7]: KPIs messen **Geschäftsergebnisse zur Laufzeit**; Reifegrad misst **Bau-Qualität einer Capability**. Das Tier einer Capability ist eine Eingabe dafür, *ob einem KPI vertraut werden kann*, nicht selbst ein KPI
- Gegen CMMI [R12]: CMMI stuft **organisationale Prozess**-Capability ein; diese Spec stuft **Produkt-Capability**-Reifegrad ein. Nur zur Abgrenzung benannt
- Gegen `spec/project/audience-identification/` [R1]: jene Spec **erzeugt** die Zielgruppenliste; diese Spec **konsumiert** sie für die Zuordnungs-Spalte

### Portfolio-Scope und Vererbung

- Diese Spec trägt `Portfolio-Scope: portfolio` und **MUSS** vererbbar per Referenz gemäß `spec/project/portfolio-inherited-spec-layer/` [R6] bleiben: ein Consumer-Repository deklariert `inherits:` auf einem gepinnten Hub-`ref` und stuft die Capabilities seiner eigenen Anwendung gegen diesen Vertrag ein, ohne je den Spec-Text zu kopieren
- Der normative Inhalt der Spec **MUSS** **application-agnostisch** sein: er schreibt die *Inventarisierungs-Methode, die drei Achsen, die Tier-Rubriken und den Artefakt-Vertrag* vor, nie eine feste Capability-Liste, Zielgruppenliste oder Schwellenwert-Zahl, sodass jede Anwendung im Portfolio ihn erben und ihre eigene Capability-Matrix erzeugen kann

### Framework-Anker

- Der normative Inhalt der Spec **MUSS** gegen die Anker in §Referenzen gelesen werden: der **OpenSSF Best Practices Badge** [R11] als Präzedenz für gestufte Bronze/Silber/Gold-Projekt-Qualitätsstufen; **ISO/IEC 25010** [R8] als das Code-Qualitätsmodell hinter Achse B; **McCabes zyklomatische Komplexität** [R9] als das Wartbarkeits-Signal, auf das Achse B verweist; das portfolio-eigene **Testpyramiden-Fundament** [R2] (und Fowlers Coverage-als-Leitfaden-Vorbehalt [R10]) als Basis von Achse C; und **CMMI** [R12], nur benannt, um Produkt- von Prozess-Reifegrad abzugrenzen
- Jede externe Framework-Zuschreibung ([R8]–[R12]) ist eine Autorenzeitpunkt-externe-Aussage und **SOLLTE** gemäß `spec/claude/research-triangulate/` trianguliert werden, bevor diese Spec über `draft` hinaus befördert wird; die internen Spec-Referenzen ([R1]–[R7]) sind tragende Querverweise, keine externen Behauptungen

## Akzeptanzkriterien

- [ ] `spec/project/capability-maturity-assessment/` existiert mit `en.md` (kanonisch) und `de.md` (Übersetzung), trägt `Portfolio-Scope: portfolio` und ist in `spec/README.md` gelistet
- [ ] Die Capability-Einheit ist als **fachliche, zielgruppen-erkennbare Funktion, rückverfolgbar auf ein Requirement** definiert und explizit davon ausgeschlossen, ein Code-Artefakt zu sein; das Inventar wird als top-down gefordert
- [ ] Jede Capability wird gefordert, an **mindestens eine Zielgruppe** aus dem `audience-identification`-Artefakt zuzuordnen, mit dem Fehlt-Artefakt-**Soft-Gate** (warnen + empfehlen, nicht blockieren) und der Pro-Zielgruppe-Divergenz-Regel ausformuliert
- [ ] Genau **drei unabhängige Achsen** (Umsetzungsgrad, Code-Qualität, Testabdeckung über die Teststufen) sind definiert, jede mit einer expliziten **Bronze- / Silber- / Gold**-Rubrik und einem **Unrated**-Boden
- [ ] Achse A ist in Akzeptanzkriterien verankert (`test-case-derivation` / `spec-driven-development` konsumierend) und als **primär Urteil** markiert; Achse B ist in ISO/IEC 25010 + statischer Analyse + McCabe-Komplexität verankert und als **weitgehend maschinell ableitbar** markiert; Achse C konsumiert die Testpyramiden-Stufen und ist als **weitgehend maschinell ableitbar** markiert
- [ ] Das **Weakest-Link-Gesamt-Tier** (Minimum über die Achsen) ist spezifiziert, **neben** den drei Pro-Achse-Tiers berichtet, mit verbotener Achsen-Kompensation und dem bei Divergenz vermerkten **Verbesserungs-Hebel**
- [ ] Der **maschinell-ableitbar-vs.-Urteil**-Split ist pro Eingabe ausformuliert, und der Scanner ist von der Zuweisung eines finalen Tiers ausgeschlossen (nur Detektion; das Skill weist zu und schreibt)
- [ ] Achse C **achtet Coverage-als-Leitfaden** [R2]: die Coverage-Bänder sind beratende Einstufungs-Signale und werden von dieser Spec explizit **nicht** in ein PR-Merge-Gate verwandelt; der Mutation-Score ist als das stärkere Signal benannt, wo verfügbar
- [ ] Das **Ausgabe-Artefakt** `project/maturity/<slug>.md` ist spezifiziert: menschenlesbar, `project/kpis/` spiegelnd, ein Block pro Capability mit id/name/description/audiences/drei Achsen-Tiers/overall/improvement-lever/rationale, mit auf eine reale Zielgruppe auflösender Zuordnung
- [ ] Schwellenwerte (Coverage-Bänder, Komplexitäts-Obergrenze, Duplizierungs-Schranke) sind als **projekt-konfigurierbare Parameter** mit der `Bronze ≤ Silber ≤ Gold`-**Monotonie-Invariante** spezifiziert, und kein universeller numerischer Schwellenwert wird mandatiert
- [ ] Die **Tooling-Form** ist spezifiziert: ein interaktives `maturity-assess`-Skill + ein read-only `capability-maturity-scanner`-Agent in `nolte-engineering`, mit dem Skill, das Inventar/Zuordnung/Urteil/Zuweisung/Schreibvorgang besitzt, und dem read-only Scanner
- [ ] Die **Abgrenzungen** gegen `quality-gate` (gestuft ≠ Gate), `test-pyramid-foundation` (konsumieren ≠ neu definieren), `kpi-definition-process` (Bau-Reifegrad ≠ Geschäftsergebnis), CMMI (Produkt ≠ Prozess) und `audience-identification` (konsumieren ≠ erzeugen) sind je ausformuliert
- [ ] Die Spec ist **application-agnostisch und portfolio-vererbbar** (schreibt Methode/Achsen/Rubrik/Vertrag vor, nicht eine feste Capability-, Zielgruppen- oder Schwellenwert-Liste) und bleibt referenzierbar gemäß `portfolio-inherited-spec-layer`
- [ ] EN- und DE-Versionen sind strukturell identisch (gleiche Überschriften, Anforderungs-Anzahl und Akzeptanzkriterien-Anzahl) und der Spec-Index listet den neuen Slug

## Offene Fragen

- **Capability-Granularität.** Wie grob oder fein eine „fachliche Capability" sein sollte (ein ganzes Feature-Areal wie „Standortverwaltung" versus eine einzelne Funktion wie „eine Winterhärtezone erkennen") ist eine Pro-Projekt-Urteilssache; diese Spec fixiert die Rückverfolgbar-auf-ein-Requirement- und Zielgruppen-erkennbar-Tests, nicht eine universelle Granularität. Ob das Inventar ein vorhandenes Artefakt (`project/features/`, eine REQ-Liste) als seine Capability-Quelle wiederverwenden sollte, statt neu zu inventarisieren, wird beim Autorenzeitpunkt des `maturity-assess`-Skills geklärt
- **Exakte Skill-/Agent-Namen.** Die Arbeitsnamen `maturity-assess` (Skill) und `capability-maturity-scanner` (Agent) werden gegen die `<object-noun>-<action>`-Namenskonvention und die Katalog-Auffindbarkeit beim Skill-Autorenzeitpunkt bestätigt
- **Gesamt-Tier-Regel jenseits von Weakest-Link.** Die Spec fixiert Weakest-Link (Minimum) als Gesamt-Regel; ob ein Projekt per lokalem Override in ein strikteres „Gold erfordert Gold auf allen Achsen **und** ein bestandenes menschliches Review" oder eine lockerere Variante *opt-in* darf, ist zurückgestellt
- **Pro-Zielgruppe-Einstufungs-Tiefe.** Ob die Pro-Zielgruppe-Divergenz eine volle parallele Einstufung (drei Achsen × jede Zielgruppe) oder eine leichtgewichtige Notiz an der Capability sein sollte, ist auf den Skill-Autorenzeitpunkt zurückgestellt; die Spec fordert das Vermerken der Divergenz, nicht eine feste Tiefe
- **Schwellenwert-Default-Empfehlungen.** Ob diese Spec *empfohlene* Start-Coverage-Bänder und eine Komplexitäts-Obergrenze mitliefern sollte (klar zu „Referenz" degradiert, gemäß dem tool-agnostischen Präzedenz von `test-pyramid-foundation`) oder jede Zahl dem Projekt überlassen, ist zurückgestellt

## Referenzen

- [R1] `spec/project/audience-identification/`: Audience Identification (erzeugt die Zielgruppenliste, die die Zuordnungs-Spalte konsumiert)
- [R2] `spec/project/test-pyramid-foundation/`: Test Pyramid Foundation (besitzt die funktionale Teststufen-Taxonomie, die Coverage-als-Leitfaden-Regel und die Rückverfolgbarkeits-Kette, die Achse C konsumiert)
- [R3] `spec/project/quality-gate/`: Quality Gate (das binäre PR-Gate, gegen das die gestufte Einstufung dieser Spec abgegrenzt ist)
- [R4] `spec/project/test-case-derivation/`: Test-Case Derivation from Requirements (die Akzeptanz-/TC-IDs, gegen die Achse A Vollständigkeit einstuft)
- [R5] `spec/project/spec-driven-development/`: Spec-Driven Development (die Akzeptanzkriterien-Basis für Achse A)
- [R6] `spec/project/portfolio-inherited-spec-layer/`: Portfolio-Inherited Spec Layer (wie ein Consumer-Repo diese Spec by-reference erbt)
- [R7] `spec/project/kpi-definition-process/`: KPI Definition Process (Schwester-Methodik-Spec; die Bau-Reifegrad-vs-Geschäftsergebnis-Abgrenzung)
- [R8] ISO/IEC 25010 — Systems and software Quality Requirements and Evaluation (SQuaRE), Produktqualitätsmodell (acht Charakteristiken inkl. Wartbarkeit): <https://iso25000.com/index.php/en/iso-25000-standards/iso-25010>
- [R9] Thomas J. McCabe, *A Complexity Measure*, IEEE Transactions on Software Engineering, 1976; Überblick: <https://en.wikipedia.org/wiki/Cyclomatic_complexity>
- [R10] Martin Fowler, *TestCoverage* (Coverage als Leitfaden, nicht als Zielwert): <https://martinfowler.com/bliki/TestCoverage.html>
- [R11] OpenSSF Best Practices Badge Program (passing / silver / gold gestufte Projekt-Qualitätsstufen): <https://www.bestpractices.dev/en/criteria>
- [R12] CMMI (Capability Maturity Model Integration) — Prozess-Capability-Reifegrad-Stufen, nur benannt, um Produkt- von Prozess-Reifegrad abzugrenzen: <https://en.wikipedia.org/wiki/Capability_Maturity_Model_Integration>
