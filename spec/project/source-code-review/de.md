# Ganzheitliches Source-Code-Review

Status: draft

## Kontext

Die bestehenden Review-Oberflächen des Portfolios sind bewusst schmal: `code-security-audit` deckt ausschließlich OWASP-Sicherheit ab, die Test-Tier-Reviewer prüfen je eine Tier-Checkliste, `quality-gate` führt mechanisches Tooling ohne Urteilsvermögen aus, und das eingebaute Diff-Review sieht nur die Änderungen des aktuellen Branches und persistiert nichts. Keine davon beantwortet die Frage, die ein Senior Engineer in einem echten Code-Review beantwortet: Ist dieser Code korrekt, wartbar, idiomatisch, frei von dupliziertem Fachwissen — und wird sein Testcode am selben Maßstab gemessen wie sein Produktivcode?

Diese Spec regelt dieses ganzheitliche Review. Sie ist in zwei Schichten geteilt, die sich nie vermischen: einen **sprachagnostischen Kern**, der die Review-Dimensionen, das Scope-Modell und den Report-Vertrag definiert, und je Programmiersprache ein **Sprachprofil**, das die Idiome, Fallstricke, Tooling-Baseline und Test-Framework-Konventionen definiert, die der Reviewer anwendet. Python ist das erste Referenzprofil. Operationalisiert wird das Review durch den Skill `source-code-review`, der die Zielsprache erkennt und den passenden Sprach-Reviewer-Agent dispatcht (`python-code-reviewer` für Python); der persistierte Report ist in disjunkte, spezialisten-geroutete Work-Packages zerlegt, sodass die Behebung parallel laufen kann.

Leserschaft: Autorinnen und Maintainer des Review-Skills und der Sprach-Reviewer-Agents; Reviewer, die den Report konsumieren; Entwickler, die das Review vor einem Release oder nach Abschluss eines Features ausführen.

## Ziele

- Ein ganzheitliches Senior-Engineer-Source-Code-Review definieren, das Produktiv- **und** Testcode mit gleichem Gewicht abdeckt
- Die sprachagnostischen Review-Dimensionen von sprachspezifischen Besonderheiten trennen, sodass neue Sprachprofile die Spec erweitern, ohne den Kern anzufassen
- **Fachwissens-Duplizierung** (dieselbe Geschäftsregel, Fachkonstante oder Validierung mehrfach implementiert) als erstklassige Review-Dimension etablieren, abgegrenzt von textueller Klon-Erkennung
- Dort beginnen, wo mechanisches Tooling endet: Das Review wiederholt nie, was Linter, Formatter oder Type-Checker bereits melden
- Einen persistierten, nach Schweregrad klassifizierten Report erzeugen, dessen Findings in **disjunkte, je einem Spezialisten zugeordnete Work-Packages** zerfallen, sodass die Behebung parallel dispatchbar ist
- Explizite Grenzen zum Security-Audit, Dependency-Audit, Observability-Audit, zu den Test-Tier-Reviewern und zum Quality-Gate ziehen

## Nicht-Ziele

- Tiefes OWASP-Security-Auditing — gehört `spec/project/code-security-audit/`; dieses Review flaggt nur offensichtliche Security-Smells und routet sie dorthin
- CVE-/Dependency-Schwachstellen-Scanning — gehört `spec/project/dependency-audit/`
- Auditieren des Observability-Vertrags — gehört `spec/project/monitoring-observability/`; dieses Review flaggt nur offensichtliche Logging-Smells und routet sie dorthin
- Test-Tier-Konformität in der Tiefe (Unit-/Integration-/Component-/Contract-/E2E-Checklisten) — gehört den `spec/project/test-tier-*/`-Specs und ihren Reviewern; dieses Review deckt querschnittliche Testcode-Qualität ab und routet Tier-spezifische Findings aus
- Mechanisches Tooling ausführen oder ersetzen (`quality-gate` besitzt Lint-/Typecheck-/Test-Ausführung)
- Fixes anwenden: Das Review findet, klassifiziert und routet; Spezialisten beheben

## Anforderungen

### Zwei-Schichten-Review-Modell

- **MUSS** die Kern-Dimensionen (§Kern-Review-Dimensionen dieser Spec) sprachagnostisch halten: Keine Regel im Kern benennt ein Sprachkonstrukt, eine Bibliothek oder ein Tool
- **MUSS** alles Sprachspezifische in einem benannten Sprachprofil definieren (§Sprachprofile); das Python-Referenzprofil unten ist das erste
- **MUSS** je dispatchtem Reviewer gegen genau ein Profil reviewen; ein polyglottes Repository erhält je erkannter Sprache einen Reviewer-Dispatch, nie ein vermischtes Review
- Eine Sprache ohne Profil in dieser Spec **MUSS** als nicht unterstützt gemeldet statt ad hoc reviewt werden; das Review benennt das angewandte Profil

### Scope-Modell

- **MUSS** Produktivcode und Testcode als **gleichrangige Review-Gegenstände** behandeln: Testcode ist langlebiger Engineering-Code, kein Anhang; jedes Finding trägt einen `production`- oder `test`-Marker
- **MUSS** standardmäßig den gesamten Source-Tree (Produktiv- plus Test-Wurzeln) erfassen und ein explizit engeres Ziel (ein Package, eine Modulmenge, ein Verzeichnis) vom Aufrufer akzeptieren; der Report benennt den reviewten Scope in beiden Fällen
- **MUSS** Source-Wurzeln und Test-Layout aus dem Repository selbst ermitteln (Build-Metadaten, Projektkonfiguration) statt ein Layout anzunehmen

### Tooling-first-Regel

- **DARF KEIN** Finding melden, das das konfigurierte mechanische Tooling des Projekts (Linter, Formatter, Type-Checker) bereits meldet oder automatisch beheben würde; der Wert des Reviews beginnt, wo das Tooling-Urteil endet
- **MUSS**, wenn dem Projekt eine Tooling-Baseline fehlt, die das Sprachprofil als Standard benennt, genau **ein** Finding zur Einführung der Baseline erheben — statt die einzelnen mechanischen Verstöße von Hand zu melden, die das Tooling fangen würde
- **SOLLTE** vermerken, wo eine Tooling-Konfiguration die Baseline wesentlich schwächt (breite Ignore-Listen, deaktivierte Strictness), als ein einzelnes Konfigurations-Finding

### Kern-Review-Dimensionen

Der Reviewer **MUSS** jede Datei im Scope gegen die folgenden Dimensionen prüfen und jedes Finding mit seiner Dimensions-ID taggen. Der Katalog ist auf Regelebene geschlossen; ihn zu erweitern ist eine Spec-Änderung.

- **D1—Korrektheit und Robustheit.** Logikfehler, unbehandelte Randfälle (leer, Grenzwert, Überlauf, Encoding), fehlende Fehlerbehandlung fehlbarer Operationen, still verschluckte oder unterdrückte Fehler (ein gefangenes Fehlersignal, das verworfen und weder behandelt noch propagiert noch geloggt wird), Eingabevalidierung an Vertrauensgrenzen, Ressourcen-Leaks, Race Conditions und geteilter veränderlicher Zustand, Off-by-one- und Reihenfolge-Annahmen.
- **D2—Lesbarkeit und Wartbarkeit.** Absichtsoffenbarende Benennung, Funktions- und Modulgröße, Schachtelungstiefe und kognitive Komplexität, toter Code, auskommentierter Code, irreführende oder redundante Kommentare, Magic Values, die eine benannte Konstante verdienen.
- **D3—Design und Architektur.** Separation of Concerns, Schichtverletzungen, Kopplung und Kohäsion, undichte Abstraktionen, Over-Engineering und spekulative Generalität (YAGNI), God-Objects/-Module, falsch platzierte Verantwortung sowie Verstöße gegen die deklarierte Architektur des Projekts.
- **D4—Fachwissens-Duplizierung.** Dieselbe Geschäftsregel, Fachkonstante, Validierung, Berechnung oder Zuordnung an mehr als einer Stelle implementiert: **semantische Duplizierung, nicht textuelle Ähnlichkeit**. Zwei strukturell verschiedene Funktionen, die dieselbe fachliche Entscheidung kodieren, sind ein Finding; zwei textuell ähnliche, aber fachlich unabhängige Blöcke nicht. Jedes Finding benennt alle Duplikat-Stellen und schlägt den Single-Source-of-Truth-Ort vor. Von der Sprache erzwungenes Boilerplate und bewusste Entkopplung über Bounded Contexts hinweg sind keine Findings; für spekulative Extraktion gilt die Rule of Three.
- **D5—Idiomatische Nutzung.** Konformität mit dem Idiom-Katalog und der Fallstrick-Liste des Sprachprofils sowie mit den etablierten Konventionen des Repositories; die Konventionen des Repositories gewinnen gegen die Präferenzen des Reviewers, wenn beide vertretbar sind.
- **D6—Testcode-Qualität.** Querschnittliche Test-Gesundheit unabhängig vom Tier: Tests prüfen beobachtbares Verhalten (nicht Implementierungsdetails), jeder Test benennt seine Absicht, keine logiktragenden Tests (Bedingungen/Schleifen, die die Erwartung berechnen), keine assertionsfreien oder Always-green-Tests, kein Over-Mocking, das den Test an Interna koppelt, keine versteckten Test-Abhängigkeiten oder geteilten veränderlichen Fixtures, kein dupliziertes Setup, das eine Fixture besitzen sollte, deterministische Ausführung (keine echte Zeit, kein Netzwerk, kein Sleep-basiertes Warten) und Testdaten, die nur benennen, was für den Fall zählt. Abdeckungslücken für geändertes oder kritisches Verhalten werden als Findings gemeldet; Tier-Konformitätsdetails routen zu den Tier-Reviewern.
- **D7—Performance und Ressourceneffizienz.** Versehentliche algorithmische Komplexität (quadratische Membership-Scans, N+1-Request- oder -Query-Muster), unbegrenztes Wachstum (Caches, Akkumulatoren, ungeschlossene Ressourcen), Arbeit in Hot Loops, die nach außen gehört, blockierende Aufrufe auf asynchronen Pfaden und vorzeitige Optimierung, die Lesbarkeit ohne gemessenen Bedarf kostet.
- **D8—API-Verträge und Dokumentation.** Klarheit der öffentlichen Oberfläche: kohärente Signaturen, dokumentiertes Verhalten und Fehlerverträge an öffentlichen Einstiegspunkten, ehrliche Benennung von Seiteneffekten, Rückwärtskompatibilitäts-Risiken an veröffentlichten Schnittstellen und Dokumentation, die dem tatsächlichen Code entspricht. In einem Repository, das ein OpenAPI-Dokument publiziert, gehört die Konformität dieses Dokuments `spec/project/api-documentation/` und wird dorthin geroutet.
- **D9—Dependency- und Grenz-Hygiene.** Nachgebaute Standardbibliotheks- oder Etablierte-Dependency-Funktionalität, unnötige neue Dependencies für triviale Bedürfnisse, vendorte Kopien von Upstream-Code sowie Fachlogik, die in Framework-Glue ausblutet oder umgekehrt. CVE-Status ist außerhalb des Scopes (Dependency-Audit).
- **D10—Querschnitts-Böden (Route-out).** Offensichtliche Security-Smells (String-gebaute Queries, hartkodierte Secrets, unsicheres Laden serialisierter Daten) und offensichtliche Observability-Smells (Debug-Prints, sensible Daten in Logs) werden **mit Routing-Vermerk zum besitzenden Audit geflaggt** — nie hier in der Tiefe untersucht. Die Behebung eines Boden-Findings lautet „das besitzende Audit dispatchen", nicht ein beschriebener Fix.

### Sprachprofile

Eine **Oberflächen-Erweiterung** darf diesem Kern Dimensionen hinzufügen, wo ein Review-Gegenstand Belange trägt, die kein Sprachprofil ausdrücken kann. `spec/frontend/source-code-review/` ist die erste: Für browsergerenderten Code legt sie Frontend-Dimensionen (F1–F11) und eine Framework-Profil-Achse über D1–D10. Eine Erweiterung übernimmt die Tooling-first-Regel, das Schweregrad-Vokabular, den Report-Vertrag und den Reviewer-Vertrag dieser Spec unverändert, wiederholt nie eine Kern-Regel und taggt jedes Finding mit genau einer Dimensions-ID.

Jedes Sprachprofil **MUSS** definieren, und ein Reviewer wendet es als Einheit an:

- **Tooling-Baseline:** die Linter-/Formatter-/Type-Checker-Menge, an die die Tooling-first-Regel delegiert, und was „Standard-Strictness" bedeutet
- **Idiom-Katalog:** die Konstrukte, die idiomatischer Code nutzt, und die nicht-idiomatischen Muster, die zu flaggen sind (D5)
- **Fallstrick-Liste:** sprachspezifische Defektmuster, geprüft unter D1
- **Typisierungs-Disziplin:** was das Profil auf öffentlichen und internen Oberflächen erwartet
- **Test-Framework-Profil:** der idiomatische Test-Stack und seine D6-relevanten Konventionen
- **Performance-Idiome:** die profilspezifischen Muster, geprüft unter D7

### Python-Referenzprofil

- **Tooling-Baseline:** `ruff` (Lint + Format) und ein strikter Type-Checker (`mypy` oder `pyright`) auf Produktivcode, `pytest` als Test-Runner. Stil, Import-Reihenfolge, Formatierung und mechanisch erkennbare Fehler sind Tooling-Domäne — der Reviewer delegiert per Tooling-first-Regel.
- **Idiom-Katalog (D5):** Context-Manager für jede besessene Ressource; `pathlib` statt String-Pfaden; f-Strings; Comprehensions und Generator-Ausdrücke, wo sie lesbar bleiben, Schleifen, wo nicht; `dataclasses` (oder die Modell-Bibliothek des Projekts, z. B. `pydantic`) statt nackter Dicts und Tupel für strukturierte Daten; `enum` statt Magic Strings; Unpacking und Keyword-only-Argumente, wo sie Aufrufstellen klären; EAFP statt LBYL, wo der Ausnahmepfad tatsächlich die Ausnahme ist; `__all__` auf öffentlichen Modulen; absolute Imports; keine Wildcard-Imports; keine Seiteneffekte zur Import-Zeit.
- **Fallstrick-Liste (D1):** veränderliche Default-Argumente; Late-Binding-Closures in Schleifen; nacktes `except:` und still verschluckte Exceptions; `is`-Vergleiche gegen Nicht-Singletons; Überschatten von Builtins; zirkuläre Imports; modul-globaler veränderlicher Zustand; Truthiness-Fallen bei Leerheitsprüfungen, wo `None` und „leer" verschieden sind; Float-Gleichheit; Mischen von naiven und zeitzonen-bewussten `datetime`-Werten; vergessenes `await`; blockierende Aufrufe (Datei/Netzwerk/`time.sleep`) in einer Event-Loop.
- **Typisierungs-Disziplin:** öffentliche Funktionen, Methoden und Dataclass-Felder sind annotiert; `Optional` ist explizit und wird vor Nutzung eingeengt; `Any` wird nicht zum Stummschalten des Checkers benutzt; strukturelle Abhängigkeiten werden als `Protocol` typisiert statt als konkrete Klassen, wo die Naht zählt; `TypedDict` oder eine `dataclass` ersetzt ein Dictionary unbekannter Form an jeder modulübergreifenden Grenze.
- **Exception- und Fehlerbehandlung:** Exceptions sind spezifische Typen, keine `Exception`-Catch-alls; Re-Raises verketten mit `raise … from`; ein Package mit öffentlichem Fehlervertrag definiert eine eigene Exception-Hierarchie; Exceptions dienen auf Hot Paths nicht als erwarteter Kontrollfluss; Fehlermeldungen tragen den fehlschlagenden Wert, nicht nur die Tatsache des Fehlschlags.
- **Logging:** das `logging`-Modul (oder der strukturierte Logger des Projekts) mit Modul-Loggern — nie `print` auf Produktivpfaden; Lazy-Interpolation (`logger.info("x=%s", x)`) statt eifriger f-Strings in Log-Aufrufen; Log-Level entsprechen der Schweregrad-Semantik.
- **Test-Framework-Profil (D6, pytest):** Fixtures statt `setUp`/xUnit-Vererbung; `parametrize` statt kopierter Fälle; `tmp_path`, `monkeypatch`, `capsys` statt Eigenbauten; `pytest.raises(..., match=...)` für Fehlerfälle; Mocking nur an eigenen Grenzen (dort patchen, wo der Name aufgelöst wird); kein Mischen von `unittest`-Stil in eine pytest-Suite, außer das Projekt hat sich bereits darauf standardisiert; deterministische Uhren (Freezing) statt `sleep`; Testnamen benennen Verhalten, nicht Methodennamen.
- **Performance-Idiome (D7):** `str.join` statt Konkatenation in Schleifen; Set-/Dict-Membership statt Listen-Scans; Generatoren für Streaming statt materialisierter Listen; `functools.lru_cache` nur mit begrenzten, unveränderlichen Eingaben; Batch-I/O statt Round-Trips pro Element.

### Report-Vertrag

- **MUSS** jedes Finding mit dem portfolioweiten Schweregrad-Vokabular aus `spec/claude/review-plan/` §Severity scale klassifizieren (Critical / Warning / Suggestion / Info, wörtlich in Title Case) — nie eine P0–P3- oder high/medium/low-Skala
- **MUSS** auf D1-Fehlerbehandlungs-Findings einen Schweregrad-Boden anwenden: Ein Finding, das einen still verschluckten oder unterdrückten Fehler oder fehlende Fehlerbehandlung einer fehlbaren Operation meldet, wird als **Critical** klassifiziert, wenn confirmed, und mindestens als **Warning**, wenn suspected — nie als Suggestion oder Info —, sodass es immer in die §Work-Packages eingeht; fehlende oder verschluckte Fehlerbehandlung ist ein No-Go, keine Stilfrage
- **MUSS** jedes Finding mit file:line, seiner Dimensions-ID (D1–D10), seinem `production`- oder `test`-Marker und dem Status confirmed oder suspected attribuieren; ein unsicheres Finding wird als suspected gemeldet, nie still verworfen
- **MUSS** mit einer Gesamtbewertung führen: reviewter Scope (Wurzeln, Globs, Sprachprofil, Commit), gefundene Tooling-Baseline und Finding-Anzahl je Dimension
- **MUSS** mit einer **§Work-Packages**-Sektion enden, die alle Critical- und Warning-Findings in Work-Packages zerlegt, bei denen **keine zwei Packages dieselbe Datei berühren**, sodass Spezialisten nebenläufig ohne Merge-Konflikte beheben können; jedes Package trägt seine Finding-IDs, seine Dateimenge, ein Ein-Zeilen-Ziel und ein **Routing-Ziel** (der Spezialisten-Skill oder -Agent, der die Behebung besitzt — Produktivcode-Fixes an die implementierende Engineer-Rolle, Tier-Konformitäts-Findings an den besitzenden Tier-Reviewer, D10-Böden an das besitzende Audit)
- **MUSS** jede Reihenfolge-Abhängigkeit zwischen Packages explizit deklarieren; Packages ohne deklarierte Abhängigkeit sind per Vertrag parallel-sicher
- **MUSS**, wenn vom aufrufenden Skill persistiert, unter `.audits/source-code-review/<target-slug>.md` liegen, per `spec/claude/review-plan/` §File location and naming; ein Re-Run überschreibt die kanonische Datei
- **SOLLTE** Suggestion- und Info-Findings aus den Work-Packages heraushalten (sie werden gelistet, nicht dispatcht)

### Reviewer-Vertrag

- **MUSS** strikt read-only sein: Der Sprach-Reviewer-Agent deklariert nur Lese- und Suchwerkzeuge, wendet keine Fixes an und fügt keine Unterdrückungskommentare ein; der Report ist die einzige Ausgabe
- **MUSS** diese Spec im Body oder in der `description` des Reviewer-Agents und des Skills zitieren
- **MUSS** die Behebung durch den Operator über die Work-Packages des Reports routen (direkt oder über einen im Report gegründeten Implementierungsplan), nie über Ad-hoc-Fixen im Review-Fluss

## Abnahmekriterien

- [ ] Der Reviewer-Agent deklariert nur `Read`, `Grep`, `Glob`, wendet keine Edits an und liefert einen Report, klassifiziert mit dem Review-Plan-Schweregrad-Vokabular
- [ ] Jedes Finding trägt file:line, eine D1–D10-Dimensions-ID, einen `production`/`test`-Marker und ein confirmed/suspected-Flag
- [ ] Ein Repository mit konfiguriertem `ruff`/`mypy` erzeugt kein Finding, das die Meldungen dieser Tools dupliziert; ein Repository ohne sie erzeugt genau ein Baseline-Einführungs-Finding statt mechanischer Einzel-Findings
- [ ] Dieselbe Fachregel an zwei Stellen wird einmal unter D4 gemeldet, mit Benennung beider Stellen und einem Single-Source-of-Truth-Vorschlag; textuell ähnlicher, aber fachlich unabhängiger Code wird nicht geflaggt
- [ ] Testdateien werden mit derselben Strenge reviewt wie Produktivdateien, und D6-Findings (logiktragende Tests, Over-Mocking, Nicht-Determinismus, Test-Kopplung) erscheinen mit `test`-Marker
- [ ] Die §Work-Packages des Reports enthalten disjunkte Dateimengen mit je einem Routing-Ziel; Packages ohne deklarierte Abhängigkeit sind parallel dispatchbar
- [ ] Ein still verschluckter Fehler oder fehlende Fehlerbehandlung einer fehlbaren Operation wird unter D1 mit Schweregrad Critical gemeldet, wenn confirmed (mindestens Warning, wenn suspected), und erscheint in den §Work-Packages; kein solches Finding wird als Suggestion oder Info abgelegt
- [ ] Ein Finding, das ein engeres besitzendes Audit abdeckt (Security, Dependency, Observability, Test-Tier), erscheint nur als geroutetes D10-/Route-out-Finding, nicht als Tiefen-Finding
- [ ] Ein Nicht-Python-Ziel wird vom Python-Profil als nicht unterstützt gemeldet statt ad hoc reviewt
- [ ] Der persistierte Report liegt unter `.audits/source-code-review/<target-slug>.md`, und ein Re-Run überschreibt ihn

## Referenzen

- [R1] Schweregrad-Vokabular und Audit-Artefakt-Konventionen: `spec/claude/review-plan/`
- [R2] Whole-Codebase-Security-Audit (Route-out-Ziel für D10-Security-Böden): `spec/project/code-security-audit/`
- [R3] Dependency-/CVE-Audit (abgegrenzt): `spec/project/dependency-audit/`
- [R4] Observability-Audit (Route-out-Ziel für D10-Observability-Böden): `spec/project/monitoring-observability/`
- [R5] Test-Tier-Specs und -Reviewer (Route-out-Ziele für Tier-Konformität): `spec/project/test-pyramid-foundation/` und `spec/project/test-tier-*/`
- [R6] Mechanisches Gate, an das die Tooling-first-Regel delegiert: `spec/project/quality-gate/`
- [R7] Agent-Autorenregeln und Read-only-Tool-Disziplin: `spec/claude/agent-management/`
- [R8] Skill-vs-Agent-Entscheidungsregel: `spec/claude/skill-vs-agent/`
- [R9] Frontend-Oberflächen-Erweiterung (Dimensionen F1–F11, Framework-Profile, Abgrenzung zum UX-Review): `spec/frontend/source-code-review/`

## Offene Fragen

- Soll die D4-Fachduplizierungs-Dimension einen Cross-Repository-Modus erhalten (Duplizierung über Portfolio-Mitglieder hinweg) oder repository-lokal bleiben, bis der Portfolio-inherited-Spec-Layer einen Cross-Repo-Resolver liefert?
- Welches zweite **Sprach**profil kommt zuerst, und lebt es in dieser Spec oder in einem Schwester-Profildokument, sobald die Profilzahl wächst? Die Browser-Oberfläche deckt inzwischen die Frontend-Erweiterung [R9] mit eigenen Framework-Profilen ab, sodass der offene Platz serverseitiges TypeScript ist — ein Repository mit Node-Service und Browser-Client erhält derzeit die Erweiterung für seinen Client und kein Profil für seinen Server.
