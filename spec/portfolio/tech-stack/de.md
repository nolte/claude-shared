# Portfolio-Tech-Stack-Erfassung

Status: draft

## Context

Das `nolte/*`-Portfolio deklariert über `spec/portfolio/portfolio-management/` bereits, **was** jedes Repository liefert: ein Capability-Inventar in der `project/portfolio.yml` jedes Portfolio-Mitglieds plus ein portfolio-weites Audit und ein gerendertes repoübergreifendes Inventar. Bewusst nicht adressiert wird dort, **wie** ein Repository technisch gebaut ist — welche Sprachen, Runtimes, Frameworks, Build-Tools, CI-Anbieter, Dependency-Bots, Doku-Generatoren, Linter, Test-Runner und Deploy-Targets ein gegebenes Repository tatsächlich verwendet. Zwei konkrete Folgen ergeben sich daraus: Das Audit kann zwei Repositories markieren, die dieselbe Capability liefern, aber nicht zwei Repositories, die dieselbe Capability auf inkompatiblen Stacks liefern; und ein neuer Beitragender, der das Portfolio-Inventar liest, erkennt nicht auf einen Blick, ob ein Repository `mkdocs` oder `docusaurus`, `uv` oder `poetry`, `task` oder `make` nutzt.

Diese Spec schließt diese Lücke mit einer **portfolio-weiten Tech-Stack-Erfassung** in einem bewussten Zwei-Schichten-Modell:

1. Ein **portfolio-weiter globaler Tech-Stack** liegt in diesem `claude-shared`-Repository unter `portfolio/tech-stack.yml`. Er listet die technischen Bausteine, auf die sich das Portfolio standardisiert — beispielsweise MkDocs als Doku-Generator, Renovate als Dependency-Bot, GitHub Actions als CI-Anbieter. Jeder Eintrag trägt einen Namen, eine `kind`-Klassifizierung, eine Rolle und einen Lifecycle-Status. Diese Datei ist die Single Source of Truth für portfolio-weite Defaults und wird vom `claude-shared`-Maintainer handgepflegt.

2. Ein **repo-spezifischer Tech-Stack-Block** liegt in der `project/portfolio.yml` jedes Portfolio-Mitglieds unter dem neuen Top-Level-Key `tech_stack:`. Er trägt zwei optionale Unter-Blöcke: `additions:` für repo-spezifische Stack-Einträge ohne portfolio-weite Entsprechung (beispielsweise eine Home-Assistant-Integration mit einer repo-spezifischen Runtime-Bindung) und `overrides:` für das Abbestellen eines globalen Eintrags, der auf dieses Repository nicht zutrifft (mit Pflicht-Begründung).

Der Vererbungs-Vertrag ist **additiv mit expliziten Overrides**: Jedes Portfolio-Mitglied erbt implizit den vollen globalen Stack; Additions erweitern; Overrides unterdrücken selektiv geerbte Einträge. Stille Abweichungen sind verboten — ein Repository, das einen globalen Eintrag nicht nutzt, muss das ausdrücklich per `overrides:` deklarieren, niemals durch Auslassen.

Leser: Maintainer von `nolte/*`-Repositories, die `project/portfolio.yml` schreiben oder überarbeiten; der `portfolio-audit`-Skill, der die repoübergreifende Konsistenz prüft; der `claude-shared`-Maintainer, der `portfolio/tech-stack.yml` kuratiert; Beitragende, die die technische Basis eines Repositories nachvollziehen müssen.

## Goals

- Jedes Portfolio-Mitglied deklariert seine technischen Bausteine in einer einheitlichen, maschinenlesbaren Form, damit das Portfolio-Audit, das Doku-Rendering und das Contributor-Onboarding sich ein Inventar teilen.
- Der portfolio-weite globale Stack wird zentral in `claude-shared` kuratiert, damit Additions, Deprecations und Renames per Vererbung auf jedes Portfolio-Mitglied propagieren, ohne pro-Repo-Duplizierung.
- Repo-spezifische Abweichungen vom globalen Stack sind explizit und auditierbar: Jeder Override trägt ein nicht-leeres `rationale`, und jede repo-spezifische Addition steht neben dem geerbten Set sichtbar.
- Das Audit kann vier Divergenz-Klassen mechanisch unterscheiden — undeklarierte Abweichung, fehlendes Rationale auf Override, deklarierter Eintrag nicht in Repo-Signalen nachweisbar, deprecated-Globaleintrag noch geerbt — und jede auf die kanonische Severity-Skala aus `spec/claude/review-plan/` routen.
- Das aggregierte Tech-Stack-Inventar rendert in die Portfolio-Doku-Site unter `docs/<lang>/portfolio/` neben dem Capability-Inventar, sodass ein Leser sowohl „wer besitzt diese Capability" als auch „welchen Stack nutzt dieses Repo" aus einer gerenderten Seite beantworten kann.
- Die Spec komponiert sauber mit `spec/portfolio/portfolio-management/`: Das `project/portfolio.yml`-Schema erhält genau einen neuen Top-Level-Key (`tech_stack:`), vollständig hier definiert; `portfolio-management` verweist auf diese Spec, statt das Feldschema neu zu definieren.

## Non-Goals

- Empfehlung konkreter Tools pro `kind`. Ob MkDocs oder Docusaurus in den globalen Docs-Slot gehört oder ob Renovate oder Dependabot den Dep-Bot-Slot besitzt, entscheidet der `claude-shared`-Maintainer beim Schreiben von `portfolio/tech-stack.yml`. Diese Spec definiert das Schema, nicht die Inhalte.
- Versions-Pinning und Versions-Upgrade-Workflow. Welche exakte MkDocs-Version ein Repo nutzt, wann ein Upgrade ansteht und wie es portfolio-weit koordiniert wird, gehört zu `spec/project/dependency-audit/` und Renovate, nicht zu dieser Spec. Das hier definierte `version:`-Feld ist deskriptiv, nicht erzwingend.
- Lizenz-Compliance-Prüfungen. Welche Lizenzen im Portfolio erlaubt sind, regelt der Lizenz-Compliance-Lauf von `dependency-audit`; diese Spec hält fest, was ein Repository nutzt, nicht ob die Lizenz zulässig ist.
- Repo-interne Build-Pipeline-Gestaltung. Sobald ein Repository CI-Anbieter, Build-Tool und Test-Runner deklariert hat, gehören die tatsächlichen Workflow-Dateien, `Taskfile.yml`-Targets und Testbefehle zu `spec/project/project-structure/` und `spec/project/quality-gate/`, nicht zu dieser Spec.
- Repoübergreifendes Laufzeit-Abhängigkeitstracking. Welcher deployte Service zur Laufzeit von welchem anderen abhängt, ist ein Release-Pipeline-Thema; diese Spec bleibt auf der pro-Repo deklarativen Ebene.
- Migrationswerkzeuge zur Konsolidierung von Repositories auf einen geteilten Stack-Eintrag. Das Audit identifiziert die Abweichung; der menschlich getriebene Konsolidierungs-PR ist eigene Arbeit.
- Ein formaler SAT-artiger Resolver für Vererbungskonflikte. Vererbung ist absichtlich flach (eine globale plus eine Konsumer-Schicht); keine transitiven Multi-Repo-Ketten werden modelliert.

## Requirements

### Globales Tech-Stack-Manifest

- **MUSS [MUST]** das portfolio-weite globale Tech-Stack-Manifest unter `portfolio/tech-stack.yml` im Wurzelverzeichnis des `claude-shared`-Repositories ablegen. Das Verzeichnis `portfolio/` wird durch diese Spec eingeführt und ist für portfolio-weite Quelldateien reserviert, die nicht zur eigenen Projektform von `claude-shared` gehören.
- **MUSS [MUST]** `portfolio/tech-stack.yml` als einen einzigen Top-Level-Key `entries:` strukturieren, dessen Wert eine Liste von Tech-Stack-Einträgen ist, von denen jeder dem §"Entry-Schema" unten entspricht; die Datei **DARF NICHT [MUST NOT]** Sub-Blöcke pro Repository tragen (diese gehören in jede Konsumer-`project/portfolio.yml`).
- **MUSS [MUST]** handgeschrieben und committet werden; die Datei ist die Single Source of Truth für portfolio-weite Defaults, niemals aus pro-Repo-Manifesten generiert.
- **DARF NICHT [MUST NOT]** in irgendeinem anderen Repository unter `nolte/*` auftauchen — nur `claude-shared` besitzt den portfolio-weiten globalen Stack. Ein Portfolio-Mitglied, das eine eigene Kopie ausliefert, ist ein `Critical`-Auditbefund.
- **KANN [MAY]** ein Top-Level-Feld `notes:` mit Fließtext tragen, der Kurations-Konventionen erläutert (zum Beispiel „wir standardisieren auf Python 3.12 im Portfolio; Runtime-Ausnahmen werden als Pro-Repo-Overrides erfasst").

### Pro-Repository-Tech-Stack-Block

- **MUSS [MUST]** jedes Portfolio-Mitglied verpflichten, in seiner `project/portfolio.yml` einen Top-Level-Key `tech_stack:` zu führen, sobald es diese Spec adoptiert. Der Key **KANN [MAY]** leer sein (`tech_stack: {}`), wenn das Repository den globalen Stack unverändert erbt.
- **MUSS [MUST]** genau zwei Sub-Blöcke unter `tech_stack:` zulassen: `additions:` (eine Liste vollständiger Einträge gemäß §"Entry-Schema") und `overrides:` (eine Liste von Override-Records gemäß §"Vererbungs-Semantik"). Beide Sub-Blöcke sind einzeln optional; ein leerer `tech_stack:` ist gültig.
- **DARF NICHT [MUST NOT]** einen Eintrag aus dem globalen Stack innerhalb von `additions:` erneut deklarieren, wenn das Repository ihn unverändert nutzt; implizite Vererbung ist der einzige Autorenweg für unveränderte globale Einträge.
- **MUSS [MUST]** `additions:`-Einträgenamen über die Vereinigung von (globalen Einträgen minus `overrides:` dieses Repos) und (`additions:` dieses Repos) eindeutig halten. Eine repo-spezifische Addition, die einen geerbten Eintrag ohne expliziten Override überdeckt, ist ein `Critical`-Auditbefund.
- **DARF NICHT [MUST NOT]** einen Tech-Stack-Eintrag deklarieren, den das Repository tatsächlich nicht nutzt; das Audit verifiziert deklarierte Einträge gegen Repository-Signale (zum Beispiel: ein `kind: package-manager`-Eintrag namens `uv` setzt eine `uv.lock` oder einen `[tool.uv]`-Block voraus; ein `kind: ci`-Eintrag namens `github-actions` setzt mindestens eine Workflow-Datei unter `.github/workflows/` voraus).

### Entry-Schema

- **MUSS [MUST]** jeden Eintrag — ob in `portfolio/tech-stack.yml:entries[]` oder in einer Konsumer-`tech_stack.additions[]` — die vier Pflichtfelder tragen lassen:
  - `name`: Kebab-case-Identifier, eindeutig innerhalb seiner Schicht (globale Einträge sind in `portfolio/tech-stack.yml` eindeutig; pro-Repo-Additions sind innerhalb ihrer `additions:`-Liste eindeutig).
  - `kind`: Ein Wert aus dem geschlossenen Enum in §"Kind-Enum" unten.
  - `role`: Ein Fließtextsatz, der nennt, was der Eintrag für das Repository oder Portfolio leistet.
  - `status`: Einer von `active`, `experimental`, `deprecated`.
- **KANN [MAY]** die optionalen Felder tragen:
  - `version`: Free-Form-String (Semver, Range oder Label). Nur deskriptiv — nicht erzwingend, und nicht der Ort für Upgrade-Verwaltung.
  - `since`: ISO-Datum, wann der Eintrag erstmals im globalen Stack oder im Repository erschien.
  - `source_of_truth`: Ein repo-relativer Pfad oder eine portfolio-weite URL, die auf die autoritative Deklaration zeigt (zum Beispiel `.tool-versions`, `pyproject.toml`, `renovate.json5`).
  - `deprecated_in_favor_of`: Bei `status: deprecated` eine `name`-Referenz auf den Ersatz-Eintrag.
  - `rationale`: Fließtextsatz, der begründet, warum dieser Eintrag in diese Schicht gehört. Auf Eintragsebene optional — aber **Pflicht** bei Overrides (siehe §"Vererbungs-Semantik").
- **MUSS [MUST]** sicherstellen, dass jede `deprecated_in_favor_of`-Referenz sich auf einen Eintrag derselben Schicht auflöst, dessen `status` nicht selbst `deprecated` ist; verkettete Deprecation-Referenzen (Eintrag A zeigt auf Eintrag B, der ebenfalls `deprecated` ist) sind ein `Warning`-Auditbefund, da sie kein konkretes Migrationsziel hinterlassen.
- **MUSS [MUST]** `name`-Werte stabil halten; Renames sind explizite Entscheidungen, getrackt in der Git-Historie des Manifests, und ein Rename eines globalen Eintrags **MUSS [MUST]** mit den `overrides:` jedes Konsumers, der ihn referenziert, innerhalb desselben Koordinationsfensters (höchstens ein geschlossener Sprint) koordiniert werden.

### Kind-Enum

- **MUSS [MUST]** `kind` auf die folgenden zwölf Werte beschränken; jeder andere Wert ist ein Parse-Fehler:
  - `language` — eine Programmiersprache, in der das Repository geschrieben ist (zum Beispiel Python, Go, TypeScript).
  - `runtime` — die Sprach-Runtime oder der Interpreter (CPython, Node.js, Bun).
  - `framework` — ein Application-Framework oder eine wesentliche Bibliothek, die die Form des Repositories definiert (FastAPI, React, Home Assistant).
  - `build` — ein Build-Orchestrator oder Task-Runner (Task, Make, Gradle).
  - `package-manager` — ein Abhängigkeits- / Lockfile-Manager (uv, poetry, pnpm, npm).
  - `ci` — ein Continuous-Integration-Anbieter (GitHub Actions).
  - `dep-bot` — ein automatisierter Dependency-Update-Bot (Renovate, Dependabot).
  - `docs` — ein Dokumentations-Generator (MkDocs, Docusaurus).
  - `lint` — ein Linter oder Style-Checker (Ruff, ESLint, Vale).
  - `test` — ein Test-Runner oder -Framework (Pytest, Vitest, Go test).
  - `deploy-target` — ein Deploy-Ziel oder Distributionskanal (Docker-Image, GitHub Pages, PyPI).
  - `other` — Fallback für Einträge, die legitim in keine der obigen Kategorien passen.
- **SOLLTE [SHOULD]** einen als `other` klassifizierten Eintrag, der über zwei aufeinanderfolgende Portfolio-Audits hinweg fortbesteht, als Katalog-Lücken-Befund (Severity `Suggestion`) routen, damit das Enum überarbeitet wird, bevor `other` zu einem versteckten Sammeltopf wird.

### Vererbungs-Semantik

- **MUSS [MUST]** jedes Portfolio-Mitglied behandeln, als erbe es implizit jeden Eintrag aus `portfolio/tech-stack.yml`, dessen `status` zum Audit-Zeitpunkt `active` oder `experimental` ist. Ein Konsumer deklariert geerbte Einträge nicht erneut; sein effektiver Stack ist die Vereinigung von `(globale active/experimental Einträge) minus (Einträge, die der Konsumer mit inherit: false überschreibt) vereint mit (den Additions des Konsumers)`.
- **SOLLTE [SHOULD]** einen globalen Eintrag von `status: experimental` auf `status: active` befördern, sobald mindestens ein Portfolio-Mitglied ihn über einen geschlossenen Sprint hinweg als geerbten Eintrag ohne `overrides:`-Record getragen hat. Das portfolio-weite Promotion-Kriterium für das Capability-Lifecycle-Vokabular wird unter den Open Questions von `spec/portfolio/portfolio-management/` verfolgt und ist dort nicht entschieden; dieses SOLLTE kodifiziert in der Zwischenzeit den tech-stack-spezifischen Default, damit die Severity-Tabelle in §Portfolio-Audit-Integration experimentell klassifizierte Einträge nicht unbefristet auf `Suggestion` bei fehlenden Signalen festsetzt.
- **MUSS [MUST]** jeden Eintrag in `tech_stack.overrides[]` als Override-Record strukturieren, der genau drei Felder trägt: `name` (verweisend auf den `name` eines existierenden globalen Eintrags), `inherit` (der **MUSS [MUST]** auf `false` gesetzt sein; das Feld wird zur Lesbarkeit explizit benannt und um Raum für eine zukünftige Opt-in-Semantik zu lassen, ohne die Record-Form zu ändern) und `rationale` (ein nicht-leerer Fließtextsatz):

  ```yaml
  overrides:
    - name: mkdocs
      inherit: false
      rationale: "rein statisches Repo; Doku liefert reines Markdown ohne Generator aus"
  ```

- **MUSS [MUST]** einen `tech_stack.overrides[]`-Record ablehnen, dessen `name` sich nicht auf einen existierenden globalen Eintrag auflöst; gebrochene Override-Referenzen sind ein `Warning`-Auditbefund.
- **DARF NICHT [MUST NOT]** stille Abweichung vom globalen Stack zulassen. Ein Repository, das ein `kind: docs`-Artefakt ausliefert (gerendertes HTML), den globalen `docs`-Eintrag aber nicht erbt und keinen expliziten Override hat, ist ein `Warning`-Auditbefund.
- **DARF NICHT [MUST NOT]** zulassen, dass `tech_stack.overrides[]` irgendein Feld des geerbten Eintrags ändert, außer ihn zu unterdrücken. Ein Konsumer, der eine andere `version` eines geerbten Eintrags benötigt, setzt den geerbten Eintrag mit `inherit: false` plus Rationale außer Kraft **und** deklariert einen repo-spezifischen Ersatz unter `additions:` mit den gewünschten Feldern.
- **MUSS [MUST]** einen globalen Eintrag, der auf `status: deprecated` wechselt, weiter als geerbt durch jeden Konsumer behandeln, bis jeder Konsumer ihn entweder überschreibt oder der globale Eintrag in die `deprecated_in_favor_of`-Auflösung übergeht; das Audit erzeugt einen `Suggestion`-Befund für jeden Konsumer, der nach einem geschlossenen Sprint einen deprecated-Eintrag weiterhin erbt.

### Portfolio-Audit-Integration

- **MUSS [MUST]** den `portfolio-audit`-Skill, der in `spec/portfolio/portfolio-management/` definiert ist, dahin erweitern, dass er Tech-Stack-Konsistenz im selben Audit-Lauf prüft, in dem er Capability-Konsistenz prüft; kein separater `tech-stack-audit`-Skill wird eingeführt.
- **MUSS [MUST]** Tech-Stack-Befunde nach der kanonischen Severity-Skala aus `spec/claude/review-plan/` klassifizieren:
  - `Critical` — ein Portfolio-Mitglied liefert eine eigene `portfolio/tech-stack.yml` aus (verbotene Duplizierung); ein pro-Repo-`additions:`-Eintrag überdeckt einen geerbten Eintrag ohne entsprechenden Override.
  - `Warning` — ein Override verweist auf einen globalen Eintrag, den es nicht gibt; ein deklarierter Eintrag mit `status: active` ist nicht in Repo-Signalen nachweisbar; ein Konsumer rendert Doku-HTML, ohne den globalen `docs`-Eintrag zu erben und ohne expliziten Override.
  - `Suggestion` — ein globaler Eintrag ist `deprecated`, und mindestens ein Konsumer erbt ihn nach einem geschlossenen Sprint immer noch; ein als `other` klassifizierter Eintrag besteht über zwei aufeinanderfolgende Audits fort; ein geerbter Eintrag mit `status: experimental` ist nicht in Repo-Signalen nachweisbar (lockerere Schwelle als bei `active`, da Experimental-Einträge ausdrücklich auf Probe stehen).
  - `Info` — Beobachtungen, die noch keine Handlung erfordern (zum Beispiel ein globaler Eintrag mit `since` jünger als ein geschlossener Sprint; ein experimenteller Eintrag ohne Konsumer-Adoption).
- **MUSS [MUST]** Repository-Signale mindestens für die folgenden Klassen verifizieren:
  - `kind: package-manager`: Lockfile- oder Tool-Config-Präsenz passend zum `name` des Eintrags (zum Beispiel `uv.lock` für `name: uv`).
  - `kind: ci`: Mindestens eine anbieterspezifische Workflow-Datei (zum Beispiel `.github/workflows/*.yml` für `name: github-actions`).
  - `kind: dep-bot`: Bot-spezifische Config-Präsenz (zum Beispiel `renovate.json5` für `name: renovate`).
  - `kind: docs`: Generator-Config-Präsenz (zum Beispiel `mkdocs.yml` für `name: mkdocs`).
  - `kind: lint`: Linter-Config-Präsenz (zum Beispiel `.vale.ini` für `name: vale`, `pyproject.toml:[tool.ruff]` für `name: ruff`).
- **KANN [MAY]** einen Read-Only-Specialist-Agent für das Signal-Probing in großen Repositories dispatchen; die Orchestrierung bleibt im `portfolio-audit`-Skill gemäß `spec/claude/skill-vs-agent/`.

### Dokumentations-Rendering

- **MUSS [MUST]** das Portfolio-Doku-Rendering, das in `spec/portfolio/portfolio-management/` definiert ist, dahin erweitern, dass es einen Tech-Stack-Abschnitt pro Portfolio-Mitglied einschließt, neben dem Capability-Abschnitt. Render-Ziel: `docs/<canonical_language>/portfolio/` mit Übersetzungen unter jeder weiteren konfigurierten Sprache.
- **MUSS [MUST]** den globalen Stack als separaten Top-Level-Abschnitt vor dem Pro-Repository-Inventar rendern, sodass ein Leser die portfolio-weite Baseline sieht, bevor er in einzelne Repositories abtaucht.
- **MUSS [MUST]** den effektiven Tech-Stack jedes Konsumers zeigen: die geerbten Einträge (mit „inherited"-Badge), die `additions:` des Konsumers (mit „repo-specific"-Badge) und die `overrides:` des Konsumers (mit „suppressed"-Badge und sichtbarem Rationale).
- **MUSS [MUST]** automatisch aus `portfolio/tech-stack.yml` plus der `project/portfolio.yml` jedes Portfolio-Mitglieds generiert werden; die gerenderten Dateien **DÜRFEN NICHT [MUST NOT]** handgeändert werden.
- **SOLLTE [SHOULD]** die Kind-Verteilung portfolio-weit mit einem Mermaid-Diagramm visualisieren, das gemäß `spec/project/mermaid-diagrams/` erstellt wird (beispielsweise ein `flowchart`, das `kind`-Zählwerte pro Repository aggregiert), damit strukturelle Ausreißer (ein Repo ohne `test`-Eintrag, ein Repo mit zwei `language`-Einträgen) auf einen Blick erkennbar sind. Nicht-Mermaid-Chart-Formate fallen außerhalb des portfolio-weiten Diagramm-Katalogs und werden hier nicht verwendet.

### Cross-References mit Portfolio-Management

- **MUSS [MUST]** das `project/portfolio.yml`-Capability-Schema, das in `spec/portfolio/portfolio-management/` definiert ist, unverändert lassen; diese Spec trägt genau einen neuen Top-Level-Key (`tech_stack:`) bei.
- **MUSS [MUST]** aus `spec/portfolio/portfolio-management/` (kanonisch und jede Übersetzung) per Ein-Satz-Verweis referenziert werden, der diese Spec als Eigentümer von `tech_stack:` nennt; das Neudefinieren des Feldschemas innerhalb von `portfolio-management` ist verboten.
- **DARF NICHT [MUST NOT]** verlangen, dass irgendein anderes Feld von `project/portfolio.yml` sich ändert. Capability-Einträge sind unberührt; Audiences sind unberührt; Peer-Referenzen sind unberührt.

## Acceptance Criteria

- [ ] `portfolio/tech-stack.yml` existiert im Wurzelverzeichnis des `claude-shared`-Repositories mit mindestens einem Eintrag gemäß §"Entry-Schema".
- [ ] Die `project/portfolio.yml` jedes aktiven Portfolio-Mitglieds trägt einen Top-Level-Key `tech_stack:` (gegebenenfalls leer), wobei `additions:` und `overrides:` dieser Spec entsprechen.
- [ ] Jeder `tech_stack.overrides[]`-Record löst sich auf einen existierenden globalen Eintrag auf; der Lauf der Broken-Override-Reference-Prüfung produziert null `Warning`-Befunde.
- [ ] Jeder Rename oder jede Löschung eines globalen Stack-Eintrags wird im nächsten Audit-Lauf über die obige Broken-Override-Reference-Prüfung sichtbar; kein `Warning`-Override-Reference-Befund besteht über das Ein-geschlossener-Sprint-Rename-Koordinationsfenster aus §Entry-Schema hinaus fort.
- [ ] Jeder Eintrag mit `status: deprecated`, der `deprecated_in_favor_of` trägt, löst sich auf einen Eintrag derselben Schicht auf, dessen `status` nicht selbst `deprecated` ist; der Lauf der Deprecation-Chain-Prüfung produziert null `Warning`-Befunde.
- [ ] Jeder `tech_stack.overrides[]`-Record hat ein nicht-leeres `rationale`; der Lauf der Rationale-Presence-Prüfung auf Overrides produziert null `Warning`-Befunde.
- [ ] Kein Portfolio-Mitglied außer `claude-shared` liefert eine eigene `portfolio/tech-stack.yml` aus; der Lauf der Duplicate-Global-Manifest-Prüfung produziert null `Critical`-Befunde.
- [ ] Kein pro-Repo-`additions:`-Eintrag überdeckt einen geerbten globalen Eintrag ohne entsprechenden `overrides:`-Record; der Lauf der Shadow-Without-Override-Prüfung produziert null `Critical`-Befunde.
- [ ] Für jeden deklarierten Eintrag, dessen `kind` zu den signal-verifizierten Klassen (`package-manager`, `ci`, `dep-bot`, `docs`, `lint`) gehört, weist das Audit das passende Repository-Signal nach; der Lauf der Signal-Presence-Prüfung produziert null `Warning`-Befunde.
- [ ] Die Acceptance Criteria des `portfolio-audit`-Skill-Specs gewinnen einen Tech-Stack-Coverage-Check; der resultierende Audit-Findings-Report schließt einen `## Tech stack`-Unterabschnitt (oder Äquivalent) ein.
- [ ] Die kanonische `spec/portfolio/portfolio-management/en.md` und jede vorhandene Übersetzung tragen jeweils einen Ein-Satz-Cross-Reference zu dieser Spec, der sie als Eigentümer des `tech_stack:`-Blocks nennt.
- [ ] Das gerenderte Portfolio-Inventar unter `docs/<canonical_language>/portfolio/` enthält sowohl einen Abschnitt „Global tech stack" als auch pro-Repository-Tech-Stack-Unterabschnitte mit inherited-/repo-specific-/suppressed-Badges.

## Open Questions

- Sollte `version:` eine strukturierte Form (zum Beispiel `{ requested: "3.12", actual: "3.12.4", source: "pyproject.toml" }`) statt Free-Form-Text akzeptieren? Strukturierte Form ermöglicht mechanische Version-Drift-Checks, koppelt diese Spec aber enger an sprachspezifische Konventionen.
- Sollte `source_of_truth:` für ausgewählte Kinds (insbesondere `language`, `runtime`, `package-manager`) verpflichtend werden, damit das Audit den deklarierten Eintrag mechanisch gegen die autoritativen Konfigurationsdateien des Repositories abgleichen kann? Verpflichtendes `source_of_truth` erhöht die Autorenhürde, festigt aber den Audit-Griff auf Drift.
- Wie lange darf `kind: other` fortbestehen, bevor er von `Suggestion` zu `Warning` eskaliert? Der aktuelle Vorschlag („über zwei aufeinanderfolgende Audits") ist ein Platzhalter; die Kalibrierung hängt davon ab, wie oft das Audit läuft.
- Sollte der globale Stack ein explizites `replaces:`-Feld tragen, das Einträge auflistet, die er bewusst ersetzt (zum Beispiel ein Übergang von `name: poetry` zu `name: uv`), damit das Audit Konsumer-Migrationen vorschlagen kann? Erhöht den Kurationsaufwand, verbessert aber die portfolioübergreifende Koordination.
- Sollte `tech_stack:` einen dritten Sub-Block `notes:` (pro-Repo-Free-Form-Text) für Stack-Eigenschaften unterstützen, die nicht ins Entry-Schema passen (zum Beispiel „dieses Repo deployt absichtlich manuell wegen regulatorischer Vorgaben")? Billig hinzuzufügen, riskiert aber zur Restmülltonne zu werden.
- Für Repositories, deren Mission ist, *ein Werkzeug* für andere Portfolio-Mitglieder zu sein (zum Beispiel `nolte/vale-style`, `nolte/gh-plumbing`), tauchen sie im Tech-Stack-Inventar des Konsumers als `kind: lint`- / `kind: ci`-Peers auf, oder werden Inter-Portfolio-Mitglieder-Abhängigkeiten anderswo erfasst? Die Antwort beeinflusst, ob `peers:` aus `portfolio-management` und `tech_stack:` aus dieser Spec sich überschneiden.
- Sollte das Doku-Rendering das **Delta** pro Konsumer (welche geerbten Einträge überschrieben, welche Additions eingeführt) als First-Class-Sicht visualisieren oder nur den effektiven Stack? Eine Delta-Sicht schärft das Drift-Bewusstsein; eine Effektivstack-Sicht liest sich natürlicher.
