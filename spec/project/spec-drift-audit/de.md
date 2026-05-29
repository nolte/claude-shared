# Spec-Drift-Audit

Status: draft

## Kontext
Das Portfolio pflegt eine wachsende Menge an Specs unter `spec/<topic>/<slug>/`. Gleichzeitig verändert sich der tatsächliche Repository-Zustand durch Pull Requests, Dependency-Bumps, Plattform-Evolution (GitHub, Claude Code, Taskfiles) und ad-hoc Hotfixes, und zwar schneller als Specs nachgezogen werden. Ohne einen verbindlichen Abgleichprozess entsteht stille Drift in beide Richtungen: entweder laufen Repositories an ihren Specs vorbei (Spec-MUSS-Regeln sind nicht umgesetzt) oder Specs dokumentieren einen Soll-Zustand, über den die Praxis mit gutem Grund hinweggegangen ist. Beide Formen von Drift untergraben, dass Menschen und KI-Agenten Specs als vertrauenswürdige Referenz nutzen können. Diese Spezifikation definiert daher den verbindlichen, wiederkehrenden Audit-Prozess: wann er läuft, welchen Scope er abdeckt, wie Ergebnisse gehandhabt werden und wie der Feedbackloop als Spec-Revision oder als Implementierungs-Fix zurückkehrt.

## Ziele
- Jedes Repository im Portfolio führt in dokumentierten Auslöser-Intervallen einen Abgleich zwischen Implementierung und Specs durch
- Entdeckte Abweichungen werden innerhalb einer dokumentierten Reaktionszeit entweder in Code oder Config korrigiert oder bewusst in eine Spec-Revision überführt — kein „known bug, next quarter"
- Der Audit bindet bestehende spezialisierte Prüfer (Skills, Linter, Actions) zu einem einheitlichen Lagebild zusammen, statt sie isoliert laufen zu lassen
- Neue Specs bringen ab Veröffentlichung eine prüfbare Audit-Strategie mit (wer prüft, wie oft, mit welchem Werkzeug)
- Die Audit-Historie ist im Repository nachvollziehbar (eine kurze Audit-Notiz als Commit, Issue oder Audit-Datei), damit iterative Verbesserung sichtbar ist

## Nicht-Ziele
- Interne Mechanik der Einzel-Audits — zum Beispiel wie `project-structure-apply` konkret arbeitet oder wie `vocab-drift-audit` die Upstream-Vokabel-Datei vergleicht (jeweils in den eigenen Skills oder Specs)
- Ersatz existierender Linter und CI-Checks — diese bleiben der laufende Schutzwall; der Audit ist die periodische Tiefen-Bohrung
- Festlegung von Release-Cadence oder Sprint-Ritualen — nicht vorgegeben; Audits sind anlassbezogen oder quartalsweise, passend zum Repository-Kontext
- Vorgabe einer konkreten Tooling-Pipeline — die Spec verlangt dokumentierte Durchführung, nicht eine bestimmte Technologie

## Anforderungen

### Audit-Scope
- **MUSS [MUST]** „Implementierung" im Sinne dieser Spec folgendes umfassen: Quellcode (`src/`, `skills/`, `agents/`), Konfigurationsdateien (`.github/`, `.claude/`, `Taskfile.yml`, `mkdocs.yml`, `pyproject.toml` / `package.json` / Äquivalente), Dokumentation (`docs/`, `README.md`, `CLAUDE.md`) sowie Workflows und Hooks
- **MUSS [MUST]** jede Spec unter `spec/<topic>/<slug>/<canonical_language>.md` einbeziehen, die einen nicht-leeren `## Requirements`- oder `## Acceptance Criteria`-Abschnitt trägt; Specs mit `Status: draft` sind **nicht** ausgenommen
- **DARF [MAY]** den Scope auf einen thematischen Teilbereich eingrenzen, wenn der Audit-Auslöser selbst eng ist (zum Beispiel ein reiner `pull-request-workflow`-Audit nach einer Änderung dieser Spec); die Eingrenzung **MUSS [MUST]** im Audit-Ergebnis festgehalten werden

### Auslöser und Rhythmus
- **MUSS [MUST]** einen Full-Scope-Audit mindestens einmal pro Kalenderquartal durchführen; der Audit-Kalender folgt Kalenderquartalen, nicht individueller Verfügbarkeit
- **MUSS [MUST]** zusätzlich einen thematisch passenden Teil-Audit auslösen, sobald eine Spec signifikant geändert wurde (neue MUSS-Regel, geändertes Akzeptanzkriterium, verschobene Scope-Grenzen) — spätestens im Folge-Merge nach dem Spec-Update
- **SOLLTE [SHOULD]** die Spec-Kopplung jedes neu eingeführten Skills oder Agents im selben Audit-Zyklus mitprüfen, damit neue Artefakte nicht von Tag 1 an mit eigener Drift starten
- **MUSS [MUST]** als lokaler, operator-ausgelöster Audit pro Repository laufen (quartalsweise plus spec-change-getriggert); die repo-übergreifende Aggregation ist hier nicht im Scope und wird durch `spec/portfolio/portfolio-management` geregelt, daher **DARF** dieser Audit **NICHT [MUST NOT]** an einen Cron-getriggerten zentralen Durchlauf gekoppelt werden

### Durchführung
- **MUSS [MUST]** jeden Audit reproduzierbar durchführen: das Audit-Ergebnis **MUSS [MUST]** die eingesetzten Werkzeuge (`project-structure-apply`, `vocab-drift-audit`, `task lint` und Entsprechungen) sowie die exakte Git-Revision des geprüften Repositories nennen
- **MUSS [MUST]** pro Spec-Acceptance-Criterion ein prüfbares Resultat produzieren: `pass`, `fail`, `blocked` (zum Beispiel fehlende Tooling-Installation) oder `not-applicable` (Criterion greift für dieses Repository nicht — mit Begründung)
- **SOLLTE [SHOULD]** automatisierbare Teile (Vale-Drift, project-structure-Abgleich, Branch-Protection-Abfrage via GitHub-API) an einen Skill oder Workflow übergeben; manuelle Checks sind zulässig, ihre Ergebnisse **MÜSSEN [MUST]** aber in derselben Struktur erfasst werden

### Feedbackloop — Umgang mit Befunden
- **MUSS [MUST]** jedes `fail` innerhalb einer dokumentierten Reaktionszeit adressieren: kritische Befunde (Security, Release-Blocker) sofort, sonstige spätestens im nächsten Quartal
- **MUSS [MUST]** pro Befund eine von drei Entscheidungen festhalten: (a) Implementierung anpassen, damit die Spec erfüllt wird, (b) Spec anpassen, weil die Realität einen guten Grund zur Abweichung hat, oder (c) den Befund als Open Question dokumentieren, wenn die Entscheidung externer Abstimmung bedarf; die Entscheidung **MUSS [MUST]** schriftlich festgehalten werden
- **DARF NICHT [MUST NOT]** ein `fail`-Befund stillschweigend ignoriert, auf eine unbegrenzte Zukunft verschoben oder zwischen Audits „vergessen" werden; die Audit-Historie im Repository muss jede Entscheidung nachvollziehbar machen
- **SOLLTE [SHOULD]** wiederkehrende Befunde an derselben Stelle nach dem zweiten Auftreten strukturell adressieren (automatisierter Check, strengere Pre-Commit-Regel, Spec-Präzisierung), statt noch einen Einzelfix nachzuliefern

### Audit-Ergebnis-Artefakt
- **MUSS [MUST]** das Ergebnis jedes Audits als git-getrackte Markdown-Datei unter `.audits/spec-drift/<YYYY>-Q<n>.md` persistieren (ein PR-Body zählt nur, wenn der PR gemergt wird); dies ist der portfolio-weite Standard-Artefakt-Ort und ersetzt jede frühere `docs/audits/`-Konvention
- **MUSS [MUST]** das Artefakt gemäß dem Vier-Abschnitte-Layout und der kanonischen Severity-Skala strukturieren, die `spec/claude/review-plan` vorschreibt (derselbe Artefakt-Vertrag, den `spec/portfolio/portfolio-management` unter `.audits/portfolio/` persistiert), damit sich Spec-Drift-Befunde identisch zu jedem anderen Audit-Artefakt im Portfolio lesen
- **DARF [MAY]** das Ergebnis zusätzlich als GitHub-Issue mit Label `audit` als sekundäre, menschenlesbare Form ausweisen, aber die git-getrackte `.audits/spec-drift/`-Datei bleibt das maßgebliche Artefakt
- **MUSS [MUST]** mindestens enthalten: Datum, Auslöser (quartal, spec-change, neuer Skill), Scope, eingesetzte Werkzeuge, Ergebnisse pro Criterion und die Entscheidungen gemäß §Feedbackloop

### Abgrenzung zu anderen Specs und Skills
- **MUSS [MUST]** `spec/project/workflow-health/` als *laufenden* Gesundheitscheck behandeln (dauerhaft grüne CI, Triage von Flakes), während diese Spec der *periodische* Tiefen-Audit ist; beide ergänzen sich und **DÜRFEN NICHT [MUST NOT]** vermischt werden
- **SOLLTE [SHOULD]** die Skills `project-structure-apply` und `vocab-drift-audit` als Teil-Auditoren im Audit ausführen und dabei festhalten, dass sie je nur einen Ausschnitt der Gesamtoberfläche abdecken
- **DARF NICHT [MUST NOT]** dieser Audit-Prozess als Rechtfertigung genutzt werden, andere Specs (zum Beispiel `pull-request-workflow`) auf Spec-Ebene zu unterlaufen — Audit-Befunde durchlaufen den regulären Pull-Request-Prozess
- **MUSS [MUST]** die repo-übergreifende, portfolio-weite Aggregation an `spec/portfolio/portfolio-management` delegieren (der zentralisierte, quartalsweise + on-demand laufende Portfolio-Audit, der aus `claude-shared` läuft, nie per Cron); diese Spec bleibt repo-lokal, und beide **DÜRFEN NICHT [MUST NOT]** vermischt werden

## Akzeptanzkriterien
- [ ] Im Repository existiert eine nachvollziehbare Audit-Historie (Commits, Issues oder Audit-Dateien) mit mindestens einem Eintrag pro Kalenderquartal seit Einführung dieser Spec — oder eine dokumentierte Ausnahme, warum ein Quartal ausgesetzt wurde
- [ ] Der letzte Audit-Eintrag deckt jede Spec unter `spec/<topic>/<slug>/` mit nicht-leerem `## Requirements` oder `## Acceptance Criteria` ab, oder dokumentiert explizit, welche Specs ausgelassen wurden und warum
- [ ] Kein `fail`-Befund aus dem letzten Audit liegt ohne dokumentierte Entscheidung (Implementierung anpassen, Spec anpassen, Open Question) im Repository
- [ ] Nach jeder signifikanten Spec-Änderung (neue MUSS-Regel oder geändertes Akzeptanzkriterium) findet sich im darauf folgenden Merge oder einem Folge-PR ein thematisch passender Teil-Audit-Nachweis
- [ ] Audit-Einträge referenzieren die Git-Revision des geprüften Repository-Stands und die Version der genutzten Audit-Skills, damit der Audit reproduzierbar ist

## Offene Fragen
_Derzeit keine._
