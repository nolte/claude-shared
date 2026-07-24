# Quality-Gate

Status: draft
Portfolio-Scope: portfolio

## Kontext
Jedes Repository im Portfolio führt Lint-, Typprüfungs- und Testkommandos in irgendeiner Form aus, aber das Wann, das Was und die Form der Ausgabe divergieren über die Projekte hinweg. Manche Repositories verdrahten alles in ein einziges `task check`-Target; andere erwarten, dass Beitragende sich vier getrennte Kommandos merken; wieder andere laufen Teile des Gates nur in CI und nie lokal. Die Kosten sind zweifach: Beitragende können von ihrem Terminal aus nicht erkennen, ob das Repo auslieferbar ist, und CI wird zum ersten Ort, an dem Fehler auftauchen — was Feedback verlangsamt und Review-Zyklen auf Probleme verbrennt, die ein lokales Gate abgefangen hätte. Diese Spec definiert den Vertrag, den das Gate erfüllen muss, damit dieselbe Invocation überall im Portfolio funktioniert, die Ausgabeform parseable ist und Taskfile-Konventionen (geregelt von `spec/project/taskfile/`, das die kanonischen Target-Namen besitzt, über die dieses Gate aufgerufen wird) plus werkzeugspezifische Ignore-Listen die Details in der Hand behalten.

## Ziele
- Eine beitragende Person in einem beliebigen Portfolio-Repository kann ein erkennbares Gate (ein Taskfile-Target) vor einem Commit, einem PR oder einem Release ausführen und bekommt ein parsebares Pass/Fail-Ergebnis
- Die Zusammensetzung des Gates (Lint + Typprüfung + Tests) ist repository-übergreifend gleich; nur die Werkzeuge wechseln pro Sprache
- Taskfile-Targets bleiben der autoritative lokale Einstiegspunkt — Repository-Konventionen und Ignore-Listen werden nicht von einem höher gelegenen Runner überstimmt
- Die Ausgabe des Gates ist hinreichend deterministisch, dass Diffs des gerenderten Ergebnisses über Läufe hinweg stabil bleiben, damit CI-Logs und PR-Kommentare vergleichbar sind
- Das Gate ist klar abgegrenzt gegen kontinuierliche CI (`workflow-health`) und gegen Security-Scanning (`dependency-audit`); jedes Anliegen besetzt seine eigene Fläche

## Nicht-Ziele
- Die Wahl eines konkreten Linting- / Typechecking- / Testing-Werkzeugs für eine gegebene Sprache (ruff vs. flake8, mypy vs. pyright, vitest vs. jest): das ist eine Entscheidung pro Repository
- Die Definition des Inhalts eines Testsuites oder eines Lint-Regelwerks — diese leben in den eigenen Konfigurationen der Repositories
- Den Ersatz von CI: das Gate ist ein lokal-oder-aufrufbarer Vorab-Check, der spiegelt, was CI ebenfalls laufen lässt; CI bleibt die Quelle der Wahrheit für Merge-Schutz
- Die Deklaration operativer Details des Skills, der das Gate implementiert (`skills/quality-gate/`) — diese können sich ohne Spec-Änderung entwickeln

## Anforderungen

### Zusammensetzung
- **MUSS** drei Kategorien einschließen, wenn das Repository relevanten Code für jede hat: Lint, Typprüfung, Tests; Kategorien ohne relevanten Code (zum Beispiel Typprüfung in einem reinen Shell-Repo) sind nicht erforderlich
- **MUSS** jede Kategorie ausführen, die das Repository tatsächlich besitzt; partielle Gates, die eine Kategorie still weglassen, **DÜRFEN NICHT** `pass` berichten
- **MUSS** das aggregierte Gate als `task check` bereitstellen; die Pro-Kategorie-Targets (`task lint`, `task test`, `task typecheck`) und die Pro-Unterordner-Targets komponieren hinein. Ein einziger erkennbarer Name über das Portfolio hinweg ist das, was den dokumentierten Aufruf überall identisch macht (§Ziele)
- **SOLLTE** das Gate aus diesen bestehenden Taskfile-Targets komponieren, statt deren Arbeit zu duplizieren; ein neues Top-Level-Target, das Lint / Typprüfung / Tests neu implementiert, ist redundant
- **DARF** das Gate um weitere Kategorien erweitern, wenn die Natur des Repositorys es rechtfertigt (Schema-Validation für ein Daten-Projekt, Helm-Lint für ein Infrastruktur-Projekt); Erweiterungen **MÜSSEN** im Taskfile explizit deklariert und in der Ausgabe des Gates sichtbar sein. Wenn die Schema-Validation-Kategorie JSON-Schema-Meta-Validation ausführt, **MUSS** sie ein Schema ablehnen, das via `allOf` komponiert und sich zum Schließen seiner Form allein auf `additionalProperties: false` verlässt, weil `additionalProperties: false` unter `allOf` unzuverlässig ist; die Garantie der geschlossenen Form erfordert `unevaluatedProperties: false`
- Coverage-Schwellenprüfung ist **KEINE** erforderliche Gate-Kategorie; sie bleibt ein CI-seitiges Anliegen, damit der lokale und der CI-Lauf die „identisch ausführen"-Invariante (§Invocation-Vertrag) erfüllen, ohne auf jedem lokalen Lauf Coverage-Instrumentierung zu erzwingen. Ein Repository **DARF** sie als zusätzliche Kategorie (gemäß der DARF-Erweitern-Regel) in einer eigenen Zeile berichten; wenn es das tut, **MUSS** dasselbe Target lokal und in CI identisch laufen
- Wenn die CI eines Repositorys eine Coverage-Schwelle **bereits** als **erforderlichen Status-Check erzwingt**, **SOLLTE** dieses Repository denselben Coverage-Lauf als Gate-Kategorie bereitstellen (gemäß der DARF-Erweitern-Regel oben), damit das lokale Gate einer beitragenden Person eine Schwellen-Regression aufzeigt, bevor CI es tut — sonst wird Coverage genau die „CI wird zum ersten Ort, an dem Fehler auftauchen"-Kostenstelle, die der §Kontext dieser Spec beseitigen soll. Das macht Coverage **nicht** zu einem Ziel: Die Guide-nicht-Ziel-Haltung von `spec/project/test-pyramid-foundation/` §„Coverage and suite-quality metrics" gilt weiterhin, und dieser Punkt spiegelt nur ein Gate, das das Repository bereits zu erzwingen gewählt hat, damit die „identisch ausführen"-Invariante auch es abdeckt. Wo CI keine Coverage-Schwelle erzwingt, bleibt der Standard (Coverage bleibt aus dem lokalen Gate heraus) unverändert

### Invocation-Vertrag
- **MUSS** das Gate identisch vom lokalen Arbeitsplatz und aus CI ausführen — keine Umgebungs-Verzweigung, die eins strenger macht als das andere
- **MUSS** Taskfile-Targets respektieren, wenn sie existieren; direkter Werkzeugaufruf ist ein Fallback für Repositories ohne Taskfile, keine Umgehung projektspezifischer Ignore-Listen
- **DARF NICHT** repository-lokale Ignore-Regeln (Lint-Ausschlüsse, Coverage-Schwellen) anwenden, die nicht in den eigenen Configs des Repositorys deklariert sind; das Gate führt die Werkzeuge so aus, wie sie das Repository konfiguriert hat
- **SOLLTE** die drei Kategorien parallel ausführen, wenn das Ökosystem es zulässt; sequentieller Fallback ist akzeptabel, wenn eine Kategorie Eingaben liefert, die eine andere konsumiert (in der Praxis selten)

### Ausgabeform
- **MUSS** eine einzige Tabelle mit den Spalten `Check`, `Status`, `Runner`, `Details` produzieren — eine Zeile pro Kategorie — damit Konsumenten das Ergebnis mechanisch parsen können
- **MUSS** pro Zeile einen der Status `pass`, `fail`, `skipped`, `timeout` verwenden; keine anderen Werte
- **DARF NICHT** `pass` für eine Kategorie berichten, die `skipped` wurde, weil ihr Werkzeug nicht erkannt wurde; `skipped` bleibt in der Ausgabe distinkt
- **MUSS** in der Spalte `Runner` genau das Kommando festhalten, das ausgeführt wurde (`task lint`, `ruff check .`, `pnpm lint`), damit der Lauf reproduzierbar ist
- **SOLLTE** unter der Tabelle einen begrenzten Auszug (≤10 Zeilen) des ersten Fehlers pro `fail`- / `timeout`-Zeile anhängen, damit ein Reviewer triagen kann, ohne neu zu starten
- **MUSS** eine Gesamturteilszeile enthalten: grüne Zusammenfassung, wenn jede Zeile `pass` ist, rote Zusammenfassung, die die fehlschlagenden Zeilen nennt, andernfalls, und einen expliziten Hinweis, wenn irgendeine Zeile `skipped` ist

### Timeouts und Fehlerbehandlung
- **MUSS** eine begrenzte Zeitüberschreitung pro Kategorie anwenden: Lint ≤ 2 Minuten, Typprüfung ≤ 5 Minuten, Tests ≤ 10 Minuten; ein längeres Timeout ist nur akzeptabel, wenn das Taskfile-Target des Repositorys die längere Laufzeit dokumentiert
- **MUSS** ein Timeout als `timeout` berichten, nicht als `fail`; die Unterscheidung ist wichtig, weil ein Timeout ein Triage-Signal ist (Tests hängen vs. Tests schlagen fehl)
- **DARF NICHT** eine zeitüberschrittene Kategorie automatisch erneut versuchen; Retry ist eine menschliche Entscheidung, sobald die Grundursache bekannt ist
- **SOLLTE** den Exit-Code des zugrundeliegenden Werkzeugs in der Spalte `Details` zeigen, damit Konsumenten den Unterschied zwischen „Lint fand 3 Fehler" (Exit 1) und „Lint stürzte ab" (Exit > 1) erkennen

### Auslöser
- **MUSS** an drei verschiedenen Punkten ausführbar sein, auch wenn der Aufruf gleich aussieht: (a) ein lokaler Pre-Commit- / Pre-PR-Schritt einer beitragenden Person, (b) CI bei jedem Push auf einen PR-Branch, (c) Release-Gating vor einem Tag
- **SOLLTE** aus einem Pre-Commit-Hook aufrufbar sein, wenn das Repository pre-commit nutzt; Repositories, die pre-commit nicht nutzen, verlassen sich auf den expliziten Aufruf der beitragenden Person
- **DARF** einen `fast`-Scope (Lint + Typprüfung, Tests übersprungen) für den Pre-Commit-Einsatz bereitstellen; ein `fast`-Lauf **MUSS** die Tests-Zeile als `skipped` berichten (gemäß §Ausgabeform) und das Gesamturteil **MUSS** den übersprungenen Teil vermerken. Ob pre-commit das volle oder das `fast`-Gate aufruft, bleibt eine Entscheidung des Repositorys
- **DARF NICHT** das Gate selbst hinter einen CI-only-Runner binden (zum Beispiel einen Self-Hosted-GPU-Runner, der für die Tests nötig wäre); wenn eine Suite tatsächlich nicht lokal laufen kann, wird sie aus dem Gate herausgetrennt und der Split im README des Repositorys dokumentiert

### Abgrenzung
- **MUSS** getrennt bleiben von `spec/project/workflow-health/`: workflow-health deckt den kontinuierlichen CI-Zustand über die Zeit ab (Flake-Triage, Trend), das Gate ist das Pass/Fail pro Invocation
- **MUSS** getrennt bleiben vom Dependency-/Schwachstellen-Scanning: jenes Scanning hat eine eigene Kadenz und Schweregrad-Skala; das Gate übernimmt dafür keine Verantwortung
- **MUSS** unabhängig von `spec/project/release-automation/` bleiben in dem Sinne, dass ein grünes Gate eine Vorbedingung eines Release-Schnitts ist, nicht ein Ersatz für den Release-Workflow

### Monorepo- und Unterordner-Verhalten
- **MUSS** jede Kategorie auf die Unterordner skopieren, die das relevante Manifest tatsächlich besitzen (zum Beispiel `ruff` nur in `backend/`, `eslint` nur in `frontend/`), wenn das Repository ein Monorepo ist; eine monolithische Invocation, die den gesamten Baum durchläuft, würde unbeteiligten Code aufgreifen
- **SOLLTE** pro Unterordner Taskfile-Targets bereitstellen (`task lint:backend`, `task test:frontend`) neben den aggregierten Targets, damit Beitragende schnell skopieren können
- **MUSS** Unterordner-Ergebnisse unter der zugehörigen Kategoriezeile in der Ausgabetabelle aggregieren, statt die Tabelle in eine Zeile pro Unterordner zu explodieren; das Unterordner-Detail gehört in die Spalte `Details`. Dies gilt auch, wenn Unterordner divergierende Sprach-Stacks nutzen — die Lesbarkeit wird durch die Spalte `Details` bedient, nicht durch Zeilen-Explosion

## Akzeptanzkriterien
- [ ] Jedes Repository mit Lint- / Typprüfungs- / Testcode stellt das aggregierte Gate als `task check` bereit, komponiert aus `task lint`, `task test` und `task typecheck`
- [ ] Der dokumentierte Aufruf des Gates ist zwischen dem README des Repositorys und seinem CI-Workflow identisch
- [ ] Die Ausgabetabelle des Gates nutzt den Spaltenvertrag `Check` / `Status` / `Runner` / `Details` über jeden Invocation-Pfad hinweg
- [ ] Kein Repository berichtet das Gate als `pass`, während es eine Kategorie, für die es relevanten Code besitzt, still überspringt
- [ ] Das Gesamt-Timeout-Budget des Gates pro Kategorie überschreitet nicht die Grenzen aus §Timeouts, oder das Taskfile-Target dokumentiert eine längere Laufzeit ausdrücklich
- [ ] Monorepos skopieren jede Kategorie auf den besitzenden Unterordner (nicht den Repo-Root) und stellen mindestens ein aggregiertes Taskfile-Target bereit, das jeden Unterordner abdeckt
- [ ] Das README des Repositorys nennt das Gate-Target und die erwartete Ausgabeform, damit neue Beitragende es an ihrem ersten Tag reproduzieren können
- [ ] Ein Repository, dessen CI eine Coverage-Schwelle als erforderlichen Status-Check erzwingt, stellt denselben Coverage-Lauf als lokale Gate-Kategorie bereit, damit eine Schwellen-Regression lokal auffindbar ist, bevor sie CI erreicht
- [ ] Der Skill `skills/quality-gate/` ruft zuerst die Taskfile-Targets des Repositorys auf und fällt nur dann auf native Werkzeug-Erkennung zurück, wenn kein passendes Target existiert

## Offene Fragen
_Derzeit keine._

## Quellen

Die JSON-Schema-Meta-Validierungs-Aussage in §Zusammensetzung (dass `additionalProperties: false` unter `allOf` unsolide ist und die Closed-Shape-Garantie `unevaluatedProperties: false` erfordert) ist eine Author-Time-externe Aussage, trianguliert gemäß `spec/claude/research-triangulate/` §"Author-time assertions" (Author-Time-Stufe: mindestens drei unabhängige Quellen, Primary-first geordnet). Abrufdatum für jede Quelle unten: 2026-07-24.

- **`additionalProperties: false` erkennt nur Properties im selben Subschema und kann daher eine über `allOf`/`$ref` zusammengesetzte Form nicht schließen; `unevaluatedProperties: false` (eingeführt in draft 2019-09) ist das Keyword, das die Form über die Komposition hinweg schließt**: JSON Schema, „Understanding JSON Schema"-Objekt-Referenz („additionalProperties only recognizes properties declared in the same subschema as itself" und kann das Erweitern eines Schemas via Combining-Keywords wie `allOf` einschränken, während `unevaluatedProperties` in Subschemata deklarierte Properties erkennt) (Primary), `https://json-schema.org/understanding-json-schema/reference/object`; Learn JSON Schema, die `additionalProperties`-Referenz (2020-12) mit Querverweis auf `unevaluatedProperties` (Secondary), `https://www.learnjsonschema.com/2020-12/applicator/additionalproperties/`; Simon Mikulcik, „Bulletproof Your Input Validation: Understanding unevaluatedProperties" („additionalProperties ... only knows about its siblings"; die Lösung ist „add `unevaluatedProperties: false`") (Secondary), `https://medium.com/@smikulcik/bulletproof-your-input-validation-understanding-unevaluatedproperties-c6e7a0eb6ddd`
