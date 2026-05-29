# Dependency-Audit

Status: draft

## Kontext
Jedes Repository im Portfolio zieht Drittanbieter-Pakete über ein oder mehrere Dependency-Manifeste ein (`pyproject.toml`, `package.json`, `go.mod`, `Cargo.toml` und deren Lockfiles). Jedes dieser Pakete ist eine Supply-Chain-Angriffsfläche: bekannte Schwachstellen (CVEs / GHSAs / PYSECs) werden fortlaufend offengelegt, transitive Abhängigkeiten multiplizieren diese Fläche, und Lizenzen bringen manchmal Verpflichtungen mit (Copyleft, Attribution), die die eigene Lizenz des Projekts nicht absorbieren kann. Ohne verbindliche Audit-Praxis sammeln sich Befunde still an — Auditoren werden ad hoc ausgeführt, Renovate-PRs tragen keinen Sicherheitskontext, und das Portfolio kann die Frage „Wie hoch ist unsere aktuelle CVE-Exposition?" nicht reproduzierbar beantworten. Diese Spec definiert, wann Dependency-Audits laufen, was sie abdecken, wie Ergebnisse klassifiziert werden und wie Befunde in Handlung übergehen. Sie ergänzt `spec/project/workflow-health/` (kontinuierliche CI-Gesundheit) und `spec/project/spec-drift-audit/` (periodisches Tiefen-Audit), indem sie die spezifische Scheibe des Supply-Chain-Risikos besetzt.

## Ziele
- Jedes Repository mit einem Dependency-Manifest führt ein Schwachstellen-Audit an dokumentierten Triggerpunkten durch, nicht zufällig
- Befunde werden nach einer geteilten Schweregrad-Skala klassifiziert, sodass dieselbe CVE portfolio-weit gleich behandelt wird
- Kritische und hohe Befunde erhalten eine dokumentierte Reaktion innerhalb eines begrenzten Zeitfensters — niemals „bekannt, vielleicht später"
- Die Audit-Ausführung respektiert Repository-Konventionen (Taskfile-Targets, Ignore-Listen), damit die Praxis auf Projekte mit begründeten lokalen Richtlinien skaliert
- Lizenz-Compliance läuft, wenn aktiviert, auf derselben Kadenz und berichtet über dasselbe Artefakt, sodass das Risiko an einer Stelle aggregiert wird

## Nicht-Ziele
- Die Wahl eines konkreten Schwachstellen-Auditors (`pip-audit`, `npm audit`, `govulncheck`, `cargo audit`): das Audit ist werkzeug-agnostisch und das Repository wählt, was zum Ökosystem passt
- Die Deklaration einer Upgrade-Richtlinie (minor vs. major, automatisch vs. reviewed): die Entscheidung bleibt bei den Dependency-Ownern und der Renovate- / Dependabot-Konfiguration
- Den Ersatz kontinuierlicher CI-Checks, die bei jedem Push bereits Abhängigkeiten scannen — diese bleiben; diese Spec definiert den periodischen Tiefendurchlauf und das Pre-Release-Gate
- Die operativen Details des zugehörigen Skills (Taskfile-Target-Erkennung, Ausgabeform) — diese gehören zu `skills/dependency-audit/` und können sich ohne Spec-Änderung entwickeln

## Anforderungen

### Geltungsbereich
- **MUSS** jedes Paket als „Dependency" behandeln, das in einem vom Repository getrackten Manifest deklariert ist: für Python `pyproject.toml` / `requirements*.txt` / `poetry.lock` / `uv.lock` / `Pipfile.lock`, für Node `package.json` + passendes Lockfile (`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`), für Go `go.mod`, für Rust `Cargo.toml` + `Cargo.lock`
- **MUSS** in einem Monorepo jeden Unterordner einbeziehen, der sein eigenes Manifest führt (zum Beispiel `backend/`, `frontend/`, `packages/*`); Audits laufen pro Unterordner, damit Befunde dem verantwortlichen Team / Paket zugeordnet werden können
- **MUSS** transitive Abhängigkeiten abdecken, nicht nur direkte — ein Befund in einem transitiven Paket bleibt ein Befund; der Report unterscheidet beide, damit die Triage auf der richtigen Schicht ansetzt
- **DARF** zusätzlich ein Lizenz-Audit ausführen, wenn das Repository es aktiviert, mit einer Allowlist unter `.license-allowlist.txt`, unter `tool.*` im Manifest oder Äquivalent; fehlende Allowlist bedeutet, dass Lizenz-Befunde als `review` berichtet werden, nicht als Failure. Lizenz-Auditing gilt als „aktiviert", sobald gemäß §Lizenz-Audit eine Allowlist auffindbar ist: das Quartals- und das vollständige Audit **MÜSSEN** dann den Lizenzdurchlauf automatisch ausführen, während Ad-hoc-Invocations opt-in bleiben

### Auslöser und Kadenz
- **MUSS** in jedem Repository mit Dependency-Manifest mindestens ein vollständiges Audit pro Kalenderquartal durchführen; der Kalender folgt Kalenderquartalen, nicht individueller Verfügbarkeit
- **MUSS** zusätzlich vor jedem Release-Tag oder Produktions-Deployment laufen, der eine Dependency-Änderung seit dem vorigen Audit enthält
- **SOLLTE** als Pre-PR-Gate (optionale lokale Invocation) laufen, sobald ein PR ein Dependency-Manifest oder ein Lockfile modifiziert
- **DARF** auf einer kürzeren Kadenz laufen (monatlich, wöchentlich), wenn das Risikoprofil es rechtfertigt — sicherheitssensitive Services, öffentlich zugängliche Produkte

### Schweregrad-Klassifikation
- **MUSS** die folgende Schweregrad-Skala übernehmen, mit der nativen Klassifikation des Auditors als Quelle der Wahrheit:
  - **critical**: eine CVE mit CVSS ≥ 9.0 oder der native `critical`-Tag des Auditors; Reaktionsfenster: innerhalb von 7 Tagen
  - **high**: CVSS 7.0 – 8.9 oder `high`-Tag des Auditors; Reaktionsfenster: innerhalb von 30 Tagen
  - **medium**: CVSS 4.0 – 6.9 oder `moderate` / `medium`-Tag des Auditors; Reaktionsfenster: innerhalb des laufenden Kalenderquartals
  - **low**: CVSS < 4.0 oder `low`-Tag des Auditors; Reaktionsfenster: best effort, beim nächsten Quartals-Audit erneut geprüft
  - **unknown**: der Auditor konnte den Befund nicht klassifizieren; als `high` behandeln, bis eine Klassifikation vorliegt
- **DARF NICHT** einen Schweregrad allein auf Basis lokaler Einschätzung absenken; Abweichung von der Klassifikation des Auditors ist ein Ignore-Listen-Eintrag mit expliziter Begründung (siehe §Ignore-Disziplin)

### Reaktion auf Befunde
- **MUSS** auf jeden Befund innerhalb des Reaktionsfensters seines Schweregrads eine von drei Reaktionen anwenden:
  - **upgrade**: das betroffene Paket auf eine Version heben, die die `fixed_in`-Grenze überschreitet
  - **ignore mit Begründung**: die Advisory-ID in die Ignore-Liste des Auditors eintragen, mit verpflichtendem `valid-until`-Datum und einer einzeiligen Begründung; zulässig nur, wenn es noch keinen veröffentlichten Fix gibt, der Befund tatsächlich nicht gilt, oder das Upgrade einen Vertrag brechen würde, den das Projekt im Fenster nicht brechen kann
  - **als bekannt akzeptieren**: den Befund im Audit-Artefakt mit einer Business-Akzeptanz-Erklärung festhalten; zulässig nur für `low`-Befunde oder ausdrücklich freigegebene `medium`-Befunde
- **MUSS** jeden Eintrag „ignore mit Begründung" spätestens an seinem `valid-until`-Datum erneut prüfen; der Eintrag **DARF NICHT** ohne frische Begründung verlängert werden
- **DARF NICHT** einen `critical`- oder `high`-Befund als „als bekannt akzeptieren" markieren; diese Reaktionsoption ist den Stufen `medium` / `low` vorbehalten

### Ausführungsmechanik
- **MUSS** vom Repository deklarierte Taskfile-Targets (`task audit`, `task deps:audit`, `task security:audit`) bevorzugen, wenn sie denselben Auditor wrappen, den die Spec sonst direkt aufrufen würde — das übernimmt projektspezifische Ignore-Listen, die das Taskfile bereits anwendet
- **MUSS** auf den nativen Auditor des Ökosystems zurückfallen, wenn kein Taskfile-Target existiert; der Fallback ist pro Unterordner, nicht pro Repository
- **MUSS** im Audit-Artefakt festhalten, welches Werkzeug (Taskfile-Target oder direkter Auditor) in welcher Version ausgeführt wurde, damit das Audit reproduzierbar ist
- **DARF NICHT** einen Unterordner still überspringen, dessen Auditor nicht installiert ist; das Audit berichtet den Skip und den Installationshinweis, und das Gate behandelt einen übersprungenen Unterordner als `blocked`, nicht als `pass`

### Ignore-Disziplin
- **MUSS** die Ignore-Liste an einem Ort ablegen, den der Auditor nativ liest — `pyproject.toml` unter `[tool.pip-audit]`, `.npm-audit-ignore.json` oder Äquivalent — nicht als freie Prosa, die nur das Audit-Artefakt sieht
- **MUSS** für jeden Ignore-Eintrag deklarieren: Advisory-ID, betroffenes Paket, `valid-until`-Datum (ISO 8601) und eine einzeilige Begründung; Einträge ohne diese Felder **MÜSSEN** das Audit zum Fehlschlag bringen
- **SOLLTE** die Gesamtzahl aktiver Ignore-Einträge klein halten (Richtwert: weniger als zehn pro Unterordner); eine wachsende Ignore-Liste signalisiert, dass die Dependency-Strategie selbst revidiert werden muss — dies ist ein Richtwert, kein erzwungenes Cap; eine Zahl darüber löst eine Dependency-Strategie-Review aus statt eines Gate-Fehlschlags
- **DARF NICHT** einen Befund global stillstellen (`--ignore-vuln <id>` ohne Datum), nur um das Gate grün zu machen; dieses Muster untergräbt den Zweck der Spec

### Audit-Artefakt
- **MUSS** das Ergebnis jedes vollständigen Audits als Commit, Issue oder Datei im Repository persistieren; der Artefaktort bleibt eine Wahl pro Repository und ist kein portfolioweit fest verdrahteter Pfad (analog zur Freiheit pro Repository, die `spec/project/spec-drift-audit/` bewusst bewahrt)
- **SOLLTE** standardmäßig den kanonischen Pfad `.audits/dependency-audit/dependencies-YYYY-Q<n>.md` verwenden (der portfolio-weite `.audits/<audit-type>/`-Standard, gemäß `spec/project/spec-drift-audit/`); ein GitHub-Issue mit Label `security-audit` ist eine akzeptierte Alternative, und etwaige später gebaute Cross-Repo-Aggregations-Werkzeuge knüpfen an eine der beiden Formen an
- **MUSS** im Artefakt enthalten: Datum, Auslöser (quartalsweise, pre-release, manifest-change), Geltungsbereich (welche Unterordner wurden auditiert, welche übersprungen und warum), die verwendeten Werkzeuge und ihre Versionen, pro Befund Schweregrad und Reaktionsentscheidung, sowie die auditierte Git-Revision
- **SOLLTE** auf das vorherige Audit-Artefakt verlinken, damit der Fortschritt über Quartale hinweg nachvollziehbar bleibt

### Lizenz-Audit (wenn aktiviert)
- **MUSS** Lizenz-Auditing als „aktiviert" behandeln, sobald eine Allowlist auffindbar ist (unter `.license-allowlist.txt`, unter `tool.*` im Manifest oder Äquivalent); in diesem Fall führen das Quartals- und das vollständige Audit den Lizenzdurchlauf automatisch aus, und nur Ad-hoc-Invocations dürfen sich abmelden
- **MUSS** den Ort der Allowlist im README des Repositorys oder Äquivalent dokumentieren, damit das Regelwerk auffindbar ist
- **MUSS** jedes Paket, dessen Lizenz nicht auf der Allowlist steht, als `review` klassifizieren, nicht als Failure, solange keine explizite Richtlinie existiert; ein Hard Fail setzt eine explizite Richtlinie mit namentlich ausgeschlossenen Lizenzen voraus
- **SOLLTE** einen Lizenz-Befund mit den Reaktionsoptionen aus §Reaktion auf Befunde paaren, angepasst: `replace` (Wechsel auf kompatibel lizenzierte Alternative), `zur Allowlist hinzufügen` (mit Begründung und Freigabe) oder `als bekannt akzeptieren`, sofern vertretbar

### Abgrenzung
- **MUSS** Dependency-Audits von `spec/project/workflow-health/` abgrenzen: workflow-health ist kontinuierlich und breit (CI grün, Flake-Triage), Dependency-Audit ist gezielt und periodisch (CVEs + Lizenzen)
- **MUSS** mit `spec/project/spec-drift-audit/` integrieren: das quartalsweise Tiefen-Audit referenziert das jüngste Dependency-Audit-Artefakt, statt dessen Arbeit zu duplizieren
- **DARF NICHT** die Auslöser des Dependency-Audits an individuelle PR-Review-Kadenzen koppeln; das Pre-PR-Gate ist optional, das Quartals-Audit nicht

## Akzeptanzkriterien
- [ ] Jedes Repository mit Dependency-Manifest enthält eine nachvollziehbare Dependency-Audit-Historie (Commit, Issue oder Audit-Datei) mit mindestens einem Eintrag pro Kalenderquartal seit Einführung dieser Spec, oder eine dokumentierte Ausnahme, die benennt, welches Quartal warum übersprungen wurde
- [ ] Das jüngste Dependency-Audit-Artefakt nennt die ausgeführten Werkzeuge, deren Versionen, die einbezogenen und ausgeschlossenen Unterordner und die auditierte Git-Revision
- [ ] Kein `critical`-Befund aus dem jüngsten Audit sitzt jenseits seines 7-Tage-Reaktionsfensters ohne dokumentiertes Upgrade, Ignore-Eintrag oder (nur falls nach den Regeln zulässig) Als-bekannt-Akzeptanz-Entscheidung
- [ ] Jeder Ignore-Listen-Eintrag im Repository trägt Advisory-ID, betroffenes Paket, `valid-until`-ISO-8601-Datum und eine einzeilige Begründung
- [ ] Das Taskfile (oder äquivalenter Task-Runner) stellt ein Target bereit, das das Audit des Skills reproduziert, damit Beitragende Befunde lokal nachvollziehen können
- [ ] Wenn das Lizenz-Auditing aktiviert ist, ist die Allowlist im README oder einer verlinkten Datei dokumentiert, und jeder Lizenz-Befund trägt eine Reaktionsentscheidung im Audit-Artefakt
- [ ] Das Audit-Artefakt zu jedem Release-Tag referenziert den Dependency-Audit-Zustand zur Release-Revision, damit post-Release-Supply-Chain-Triage von einer bekannten Baseline aus starten kann

## Offene Fragen
- Muss die Quartalskadenz enger werden (monatlich) für Repositories im Geltungsbereich bestimmter Compliance-Regime, und wenn ja, welche Regime rechtfertigen die Verschärfung?
