# Cookiecutter-Template-Autorenschaft

Status: draft

## Kontext
<!-- Warum existiert diese Spec? Welches Problem, welches Nutzer-Bedürfnis oder welche Einschränkung treibt sie? -->

Das Portfolio verwendet [Cookiecutter](https://www.cookiecutter.io/) als kanonisches Scaffolding-Werkzeug für neue Projekte, die schon mit dem ersten Commit in spec-konformer Form starten sollen. Der `cookiecutter-template-author`-Agent verfasst diese Templates heute bereits, aber er tut das gegen ein Set von MUSTs, das nur im Body des Agents lebt — es gibt keine Spec, gegen die ein Reviewer den Agent auditieren kann, keine Spec, die ein Folge-Agent lesen kann, und keine Spec, gegen die der `spec-drift-audit`-Prozess Implementierungen vergleichen kann. Diese Spec hebt diese MUSTs in dieselbe Form, die jede andere Portfolio-Capability nutzt: eine normative Anforderungsliste, testbare Akzeptanzkriterien und eine klare Grenze zu Nachbar-Specs (`project-structure`, `pull-request-workflow`, `branching-model`, `release-automation`, `release-skill-layer`).

Ein Cookiecutter-Template in diesem Portfolio ist ein Projekt-Scaffold-Artefakt, das in einem Schritt ein neues Repository rendert, dessen Initial-Commit jeden anwendbaren MUSS in diesen Nachbar-Specs erfüllt. Das Template trägt eigene Hooks (`pre_prompt.py`, `pre_gen_project.py`, `post_gen_project.py`), eine eigene `cookiecutter.json`-Variablenform und ein eigenes Test-Harness (`pytest-cookies` plus eine GitHub-Actions-Matrix). Diese Spec regelt dieses Artefakt: was das Template ausliefern MUSS, welche Hooks es laufen lässt, wie seine Tests den gerenderten Output prüfen und welche Anti-Patterns es ablehnen MUSS.

Leser: Autoren des `cookiecutter-template-author`-Agents und der von ihm erzeugten Templates, Reviewer, die ein Template gegen die benachbarten Scaffolding-Specs prüfen, sowie der `spec-drift-audit`-Prozess, der Template-Implementierungen gegen diese Spec abgleicht.

## Ziele
<!-- Was diese Spec erreichen will. Stichpunkte, outcome-orientiert. -->
- Jedes im Portfolio verfasste Cookiecutter-Template rendert ein Projekt, dessen Initial-Commit jeden anwendbaren MUSS in `spec/project/project-structure/`, `spec/project/pull-request-workflow/`, `spec/project/branching-model/`, `spec/project/release-automation/` und `spec/project/release-skill-layer/` erfüllt
- Templates liefern ein `pytest-cookies`-basiertes Test-Harness aus, das den gerenderten Output prüft, sodass eine Regression in einer Nachbar-Spec die CI des Templates bricht, bevor es ausgeliefert wird
- Die Cookiecutter-Hooks (`pre_prompt.py`, `pre_gen_project.py`, `post_gen_project.py`) folgen einem dokumentierten Kontrakt — was jeder darf und nicht darf, welche Nebeneffekte erlaubt sind, wie sie mit dem gerenderten Tree interagieren
- Der `cookiecutter-template-author`-Agent hat einen normativen Anker, gegen den ihn `spec-readiness-reviewer` auditieren und den der periodische `spec-drift-audit`-Prozess abgleichen kann
- Neue Portfolio-Templates erben dieselbe Anti-Pattern-Liste (keine committeten virtualenv-Verzeichnisse, kein gerendertes `__pycache__`, keine hartcodierten Secrets, keine ungetesteten Hook-Seiteneffekte, …) statt dass jedes Template sie neu entdeckt

## Nicht-Ziele
<!-- Explizit außerhalb des Scopes. Verhindert Scope-Creep. -->
- Das Konsumieren eines existierenden Templates (ein gewöhnlicher `cookiecutter <url>`-Aufruf braucht keine Spec und keinen Agent)
- Generisches Python-Projekt-Bootstrap ohne Cookiecutter-Bezug (verwende die Standard-Python-Projektstruktur aus `spec/project/project-structure/`)
- Copier- oder cruft-Templates — die haben andere Anti-Patterns und andere Hook-Kontrakte; Querverweise auf sie gehören in den Agent-Body, nicht in diese Spec. Eine eigene `copier-template-authoring`- / `cruft-template-authoring`-Spec wird nur dann erstellt, wenn das Portfolio tatsächlich ein solches Template ausliefert.
- Templates, die absichtlich von den nolte-Portfolio-Specs abweichen (out-of-scope für den Agent und für diese Spec; die Abweichung verlangt einen expliziten Waiver außerhalb dieser Oberfläche)
- Das Render-Zeit-`cookiecutter.json`-Variablen-Schema (variiert pro Template by Design — die Spec regelt die Form des resultierenden Projekts, nicht die Eingabeform)
- Visuelle Identität oder Branding des gerenderten Projekts (Per-Template-Entscheidung, gegated durch die `mkdocs-material`-Palette-Einstellungen des gerenderten Projekts)

## Anforderungen
<!-- RFC-2119-Schlüsselwörter verwenden: MUSS, SOLLTE, KANN. Eine atomare Anforderung pro Stichpunkt. -->

### Rendered-Project-Konformität

- **MUSS [MUST]** ein Projekt rendern, dessen Initial-Commit jeden MUSS in `spec/project/project-structure/` erfüllt: die sieben Basis-Dateien / Ordner (`README.md`, `LICENSE`, `.gitignore`, `Taskfile.yml`, `mkdocs.yml` wenn Docs ausgeliefert werden, `.github/`, `pyproject.toml` oder Äquivalent), die sieben Basis-GitHub-Configs (`.github/settings.yml`, `release-drafter.yml`, `boring-cyborg.yml`, `stale.yml` plus die Probot-`extends:`-Pointer) und das vom project-structure-mandierte Renovate-Setup
- **MUSS [MUST]** ein Projekt rendern, dessen Initial-Commit die in `spec/project/branching-model/` definierte Branching-Form erfüllt: mindestens einen `develop`-Branch (`main` legt der User mit dem ersten Release an), keinen committeten Feature-Branch-State, keine committete Working-Tree-Verschmutzung (`__pycache__`, `.venv`, `node_modules`, Build-Artefakte)
- **MUSS [MUST]** ein `.github/workflows/`-Set rendern, das `spec/project/release-automation/` und `spec/project/release-skill-layer/` für den gewählten Release-Flow erfüllt: einen `release-drafter`-Workflow beim PR-Merge auf `develop`, einen `release-publish.yml`-Workflow, den das `release-publish-trigger`-Skill dispatchen kann, und den Required-Checks-Kontrakt auf `develop` gemäß `spec/project/workflow-health/`
- **MUSS [MUST]** ein `.github/PULL_REQUEST_TEMPLATE.md` und ein Issue-Template-Set rendern, das `spec/project/pull-request-workflow/` und `spec/project/github-issue-templates/` erfüllt (sofern das gerenderte Projekt überhaupt Issues / PRs ausliefern soll)
- **MUSS [MUST]** ein Taskfile rendern, dessen Targets der Portfolio-Konvention entsprechen: `task install`, `task lint`, `task test`, `task docs` (wenn Docs ausgeliefert werden), `task release` (wenn Release-Flow verdrahtet ist); jedes Target ruft die projekt-lokale Toolchain auf statt sich auf global installierte Binaries zu verlassen
- **MUSS [MUST]** im gerenderten Projekt einen `AUDIENCES.md`-Stub oder einen `## Audiences`-README-Abschnitt gemäß `spec/project/audience-identification/` einschließen, sodass das gerenderte Projekt mit dem Audience-Identifikations-Schritt startet statt ihn nachzurüsten
- **DARF NICHT [MUST NOT]** committete Secrets, hartcodierte API-Keys oder Credentials irgendwelcher Form rendern — auch nicht in Beispiel- oder Test-Dateien. Render-Zeit-Secrets gelangen über `.env.example` oder eine äquivalente Platzhalter-Form ins Projekt.

### Hook-Kontrakt

- **MUSS [MUST]** `pre_prompt.py` auf read-only Operationen und Variablen-Validierungs-Logik beschränken. Der Hook **DARF NICHT [MUST NOT]** das Dateisystem außerhalb seines eigenen ephemeren Arbeitsverzeichnisses mutieren, **DARF NICHT [MUST NOT]** Netzwerkaufrufe machen und **DARF NICHT [MUST NOT]** Shell-Prozesse spawnen, die Seiteneffekte produzieren.
- **MUSS [MUST]** `pre_gen_project.py` auf Validierung, Normalisierung und Abbruch-Logik beschränken (eine klare Fehlermeldung drucken und `sys.exit(1)` für ungültige Eingaben). Der Hook **DARF NICHT [MUST NOT]** den gerenderten Projekt-Tree vor dem Rendern mutieren — er läuft per Design *vor* der Generierung und der Tree existiert noch nicht.
- **MUSS [MUST]** `post_gen_project.py` auf Operationen beschränken, die das gerenderte Projekt finalisieren: Dateien / Ordner entfernen, gegen die der User per `cookiecutter.json`-Variablen optiert hat, ein git-Repository initialisieren (`git init` ist erlaubt; `git remote add` und `git push` sind verboten), `pre-commit install` laufen lassen und ein finales „Nächste Schritte"-Banner drucken. Der Hook **DARF NICHT [MUST NOT]** Abhängigkeiten installieren (Python, Node, System), **DARF NICHT [MUST NOT]** Netzwerkaufrufe machen und **DARF NICHT [MUST NOT]** Dateien außerhalb des gerenderten Projekt-Trees modifizieren.
- **MUSS [MUST]** jeden Hook-Seiteneffekt durch einen `pytest-cookies`-Test verifizierbar machen (siehe §Test-Harness unten); ein Hook, der den gerenderten Tree ohne abdeckenden Test mutiert, ist ein Autoren-Fehler
- **SOLLTE [SHOULD]** jeden Hook unter ~100 Zeilen Python halten; längere Hooks deuten darauf hin, dass die Verantwortung zu einem separaten Skill oder einem Runtime-Tool gehört, nicht zum Template
- **KANN [MAY]** das gerenderte Projekt zum `audience-identify`-Skill als Post-Generation-Nächster-Schritt verweisen (im Banner gedruckt, nicht automatisch aufgerufen), sodass der Operator dem spec-mandierten Audience-Identifikations-Flow direkt nach der Generierung folgt. Dies bleibt by Design KANN (banner-only): Der Hook des gerenderten Projekts ist kein Skill und **DARF NICHT [MUST NOT]** das Skill-Tool aufrufen (siehe `spec/claude/skill-vs-agent/`, die einem Agent verbietet, das Skill-Tool im Namen des Users aufzurufen), und das `cookiecutter-template-manage`-Skill zur Authoring-Zeit kann den Generierungs-Zeit-Kontext des Konsumenten nicht erreichen. Ein Upgrade auf automatisches Dispatch verlangt einen neuen Generierungs-Zeit-Wrapper, keine Änderung am Hook-Kontrakt.

### Test-Harness

- **MUSS [MUST]** eine `pytest-cookies`-Test-Suite ausliefern, die das Template mit einem repräsentativen Variablen-Set rendert und prüft, dass der gerenderte Tree jeden MUSS in §Rendered-Project-Konformität erfüllt
- **MUSS [MUST]** die Test-Suite in eine GitHub-Actions-Matrix verdrahten, die das Template auf mindestens den in `pyproject.toml` (oder Äquivalent) deklarierten Python-Versionen und mindestens dem OS prüft, das dem Ziel des gerenderten Projekts entspricht — typischerweise `ubuntu-latest`. Wenn das gerenderte Ziel eines Templates Windows-Ausführung impliziert (Windows-Binär-Releases, eine Home-Assistant-Integration), löst sich „das OS, das dem Ziel des gerenderten Projekts entspricht" zu der Aufnahme von `windows-latest` in die Matrix dieses Templates auf.
- **MUSS [MUST]** Post-Generation-Hook-Outcomes mechanisch prüfen (Datei vorhanden, Datei nicht vorhanden, `pre-commit`-Install-Zustand, …) statt über Banner-Output-Inspektion
- **SOLLTE [SHOULD]** einen „Zweimal rendern mit identischen Variablen ergibt identische Trees"-Idempotenz-Test einschließen, sodass nicht-deterministische Hooks zur Template-CI-Zeit erkannt werden
- **KANN [MAY]** eine „Rendern mit optionalen Features aus, dann an"-Matrix-Dimension einschließen, wenn die `cookiecutter.json` des Templates Feature-Toggle-Variablen exponiert; das erkennt Features, die heimlich voneinander abhängen

### Anti-Pattern-Refusal

Das Template **DARF NICHT [MUST NOT]** eines der folgenden rendern:

- Committete `.venv/`, `node_modules/`, `__pycache__/`, `.pytest_cache/`, Build-Artefakte oder anderen ignorierbaren Working-Tree-State
- Editor-spezifische Konfiguration außerhalb der Portfolio-Konvention (`.idea/`, `.vscode/settings.json` mit User-spezifischen Pfaden)
- Hartcodierte User-spezifische Pfade (`/home/<user>/`, `C:\\Users\\<user>\\`) in irgendeiner gerenderten Datei
- Dokumentation, die der tatsächlichen Form des gerenderten Projekts widerspricht (ein `README.md`, das Dateien dokumentiert, die das Template nicht rendert)
- `LICENSE`-Dateien, die wortwörtlich aus einem anderen Projekt kopiert wurden, ohne dass SPDX-Bezeichner und Copyright-Holder-Felder für das gerenderte Projekt korrekt gefüllt sind
- Ein `CHANGELOG.md` mit Platzhalter-Einträgen, das vortäuscht, das gerenderte Projekt habe Releases ausgeliefert, obwohl es das nicht hat

### Dokumentation

- **MUSS [MUST]** ein Template-Level-`README.md` ausliefern (am Repository-Root des Templates, separat vom `README.md` des gerenderten Projekts), das benennt: was das Template rendert, die `cookiecutter.json`-Variablenform, die optionalen Features und ihre Toggles, den Post-Generation-Banner-Output und den Link zu dieser Spec
- **MUSS [MUST]** den Agent, der dieses Template verfasst (`cookiecutter-template-author`), als kanonisches Authoring-Tool im Template-Level-README deklarieren
- **SOLLTE [SHOULD]** eine `docs/` MkDocs-Site für das Template selbst ausliefern, wenn das Template mehr als ~20 Variablen rendert, sodass die Variablenoberfläche auffindbar bleibt

## Akzeptanzkriterien
<!-- Testbare, prüfbare Bedingungen. Ein Reviewer kann jedes als erledigt/nicht erledigt markieren. -->
- [ ] Jedes Cookiecutter-Template im Portfolio rendert ein Projekt, dessen Initial-Commit jeden anwendbaren MUSS in `project-structure`, `pull-request-workflow`, `branching-model`, `release-automation` und `release-skill-layer` erfüllt; verifizierbar dadurch, dass die `pytest-cookies`-Test-Suite des Templates grün läuft
- [ ] Jedes Template liefert eine `pytest-cookies`-Test-Suite aus, die in eine GitHub-Actions-Matrix verdrahtet ist; die CI im Template-Repo beweist, dass die Suite läuft
- [ ] Jeder `pre_prompt.py`-, `pre_gen_project.py`- und `post_gen_project.py`-Hook im Portfolio honoriert die obigen Operations-/Seiteneffekt-Beschränkungen; verifizierbar durch ein Reviewer-Audit der Hook-Bodies (keine Netzwerkaufrufe, keine Dep-Installs, keine Out-of-tree-Writes)
- [ ] Jedes Template-`post_gen_project.py`-Banner verweist den Operator auf das `audience-identify`-Skill als Post-Generation-Nächsten-Schritt
- [ ] Jedes gerenderte Projekt liefert einen `AUDIENCES.md`-Stub oder einen `## Audiences`-README-Abschnitt aus, sodass der Audience-Identifikations-Flow zur Generierungs-Zeit startet
- [ ] Kein Template im Portfolio rendert eines der gelisteten Anti-Pattern-Artefakte (committete `.venv/`, `__pycache__/`, hartcodierte Credentials, User-spezifische Pfade, …); die CI des Templates fängt jedes mechanisch
- [ ] Der `cookiecutter-template-author`-Agent zitiert in seinem Body diese Spec als normative Quelle, statt die Anforderungen zu wiederholen

## Offene Fragen

_Alle zuvor zurückgestellten offenen Fragen wurden am 2026-06-06 entschieden: jeder vorläufige Default ist nun die geltende Regel. Die Einzelentscheidungen und Begründungen sind in der Git-Historie erhalten (Entscheidungslog, 2026-06-06)._

## Quellen
<!-- Autoritative externe Referenzen, gegen die die obigen Anforderungen validiert wurden (≥2 unabhängige Quellen pro Aussage). -->
- Cookiecutter-Dokumentation (cookiecutter.readthedocs.io) — kanonische Referenz für den Hook-Lifecycle (`pre_prompt.py` / `pre_gen_project.py` / `post_gen_project.py`) und die `cookiecutter.json`-Variablenform
- `pytest-cookies`-Dokumentation (github.com/hackebrot/pytest-cookies) — kanonische Referenz für die Test-Harness-Fixtures, die den gerenderten Output prüfen
- `spec/project/project-structure/`, `spec/project/pull-request-workflow/`, `spec/project/branching-model/`, `spec/project/release-automation/`, `spec/project/release-skill-layer/`, `spec/project/audience-identification/` — die Portfolio-Specs, aus denen diese Spec Anforderungen hebt
- Aktueller Body des cookiecutter-template-author-Agents (`agents/cookiecutter-template-author.md`) — die De-facto-Anforderungsliste, die diese Spec in eine normative Form ratifiziert
