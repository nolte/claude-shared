# YAML JSON Schema

Status: draft

## Kontext

Über das Portfolio hinweg werden Konfigurationen, Manifeste und strukturierte Datenformate zunehmend durch Schemata beschrieben — Frontmatter-Formen für `project/features/`, der `project/portfolio.yml`-Umschlag pro Repo, GitHub-Actions-Inputs, MkDocs-Plugin-Konfigurationen, eigene Ansible-Inventory-Layouts sowie die JSON-Schema-Descriptoren, die daneben ausgeliefert werden. Die Portfolio-Konvention ist, diese Schemata als **JSON-Schema-2020-12-Dokumente in YAML-Notation** zu führen statt in JSON: YAML trägt Kommentare, unterstützt mehrzeilige Literal-Strings und liest sich für hand-autorisierte Schema-Dokumente besser als das JSON-Pendant.

Ohne verbindliche Konvention driftet hand-autorisiertes Schema-Material entlang mehrerer Achsen: welche `$schema`-Dialekt-URI kanonisch ist, ob `$id` Pflicht ist, wo wiederverwendbare Sub-Schemata leben (inline `properties` vs `$defs` vs separate Dateien), ob Keywords snake_case oder camelCase folgen, ob `examples` und `default`-Werte erhalten bleiben und welchen Validator ein CI-Gate annehmen darf. Isoliert ist die Drift nicht katastrophal, aber im Portfolio-Maßstab wird sie es: Zwei Repositories, die „dasselbe" Objekt beschreiben, landen bei zwei inkompatiblen Schemata, und ein Konsument kann die übergreifende Form nicht erschließen, ohne beide erneut zu lesen.

Diese Spec definiert für jedes YAML-codierte JSON-Schema-Dokument, das das Portfolio autorisiert:

1. **den Dialekt**, den es beansprucht (`$schema`),
2. **das strukturelle Skelett**, das die Datei tragen muss,
3. **die Referenz-Regeln**, die `$ref`, `$defs` und externe `$id`-Grenzen regieren,
4. **den Validierungs-Vertrag**, der einem CI-Gate erlaubt zu beweisen, dass das Schema selbst gültig ist und dass etwaige Begleit-Datendateien dem Schema entsprechen,
5. **das On-Disk-Layout**, das das Schema dort auffindbar macht, wo auch die beschriebenen Daten liegen.

Die Spec begrenzt sich bewusst auf **JSON Schema 2020-12 in YAML**. JSON-codierte Schemata, OpenAPI-Schema-Objekte und AsyncAPI-Schema-Objekte sind nicht Scope — sie haben eigene regierende Specs (OpenAPI 3.x §Schema Object, AsyncAPI 3.x §Schema Object), die bewusst von reinem JSON Schema abweichen und eine eigene Portfolio-Regel verdienen, sobald der Bedarf konkret wird.

## Ziele

- Jedes YAML-codierte JSON-Schema-Dokument im Portfolio ist an Dateiendung, Header-Schlüsseln und On-Disk-Pfad erkennbar — kein Raten nötig.
- Jedes Schema deklariert seinen Dialekt (`$schema`) und seine Identität (`$id`), sodass ein Validator es deterministisch über Repositories hinweg auflösen kann, ohne maßgeschneiderte Konfiguration.
- Wiederverwendbare Sub-Schemata leben in `$defs` und werden via `$ref` referenziert; Inline-Duplizierung komplexer Objekt-Formen ist verboten, damit ein Refactoring nie zwei Kopien jagen muss.
- Jedes Schema wird selbst gegen die Meta-Schema seines deklarierten Dialekts validiert, als Teil des Quality-Gates des Repositories; ein Schema, das die Meta-Validierung nicht besteht, ist defekt, unabhängig davon, ob nachgelagerte Konsumenten damit klarkommen.
- Jede Datendatei, die das Schema regiert (`*.yaml`, `*.yml`, `*.json`-Begleiter), wird durch denselben Skill, der das Schema autorisiert hat, gegen es validiert, sodass Autoring und Validierung nicht zwei losgelöste Praxen sind.
- Die Konventionen werden durch genau einen Skill operationalisiert — `nolte-shared:yaml-json-schema` —, der Authoring, Audit, Refactoring und Datenvalidierung abdeckt. Operatoren shoppen nicht zwischen halb-überlappenden Skills.

## Nicht-Ziele

- Eine einzige JSON-Schema-Validator-Implementierung wählen. Die Validator-Wahl (`check-jsonschema`, `ajv-cli`, `python-jsonschema`, `jsonschema-rs`) bleibt eine Pro-Repo-Entscheidung, getrieben vom Sprach-Ökosystem, das das Projekt ohnehin nutzt.
- Konventionen für OpenAPI-3.x-Schema-Objekte oder AsyncAPI-Schema-Objekte definieren. Diese Formate erben *das meiste* von JSON Schema, weichen aber an bekannten Stellen ab (`nullable`, `discriminator`, `example` vs `examples`) und brauchen eine eigene Spec.
- `spec/project/feature/` (welche den *Inhalt* von Feature-Frontmatter regiert) durch eine Schema-Spec ersetzen. Diese Spec handelt von Form und Lebenszyklus der Schema-Dateien; die Frontmatter-Spec bleibt verbindlich dafür, *was* Feature-Frontmatter enthält.
- Häufig geteilte Schemata in einem portfolio-weiten Registry-Verzeichnis zentralisieren. Die Portfolio-Policy ist Repo-lokale Ablage; repository-übergreifendes Teilen wird durch `$id`-Disziplin und absolute `$ref`-URIs in den GitHub-Pfad des besitzenden Repos gelöst, nicht durch ein gemeinsames Verzeichnis unter `spec/portfolio/<topic>/schemas/`.
- Code-Generierung aus Schemata vorschreiben (Pydantic-Modelle, TypeScript-Typen, Go-Structs). Generierung ist erlaubt, bleibt aber außerhalb der MUSS/SOLL/DARF-Fläche dieser Spec — das ist eine künftige Spec.

## Anforderungen

### Dialekt

- **MUSS** `$schema` als ersten Schlüsseleintrag jeder Schema-Datei deklarieren, mit dem Wert `https://json-schema.org/draft/2020-12/schema`. Das Portfolio normiert auf JSON Schema 2020-12 (der aktuellste stabile Draft zum Zeitpunkt der Autorierung). Andere Draft-URIs (`draft-07`, `draft/2019-09`) werden nicht akzeptiert; verlangt ein vorgelagerter Konsument einen älteren Draft, deklariert dessen Repository das lokal und dokumentiert die Abweichung in seinem README.
- **DARF NICHT** Dialekte innerhalb eines einzelnen Schema-Dokuments mischen. Ein `$ref` aus einem 2020-12-Dokument in ein draft-07-Schema ist verboten; ist das referenzierte Schema notgedrungen draft-07 (externer Lieferant), wird der relevante Teil ins 2020-12-Dokument transkribiert und die Transkriptionsquelle in einem `description`-Feld festgehalten.
- **SOLLTE** `$schema` auch in `$defs`-Sub-Schemata, die in einem anderen Dokument eingebettet sind, nur dann deklarieren, wenn das eingebettete Schema später in eine eigene Datei gehoben werden soll; andernfalls deckt die `$schema`-Deklaration des Eltern-Dokuments den gesamten Dokumentbaum ab.

### Identität

- **MUSS** `$id` als zweiten Schlüsseleintrag jeder Schema-Datei deklarieren, mit einer absoluten URI unterhalb des `https://github.com/nolte/`-Namensraums nach dem Muster `https://github.com/nolte/<repo>/blob/main/<owner-path>/schemas/<slug>-v<major>.<minor>.schema.yaml`. Die URI spiegelt den Repository-relativen On-Disk-Pfad der Schema-Datei innerhalb des GitHub-gehosteten besitzenden Repositories wider, wodurch sie über das Portfolio hinweg konstruktionsbedingt eindeutig wird. JSON Schema behandelt `$id` als logischen Bezeichner; die URI muss keinen `fetch`-Aufruf auflösen, aber die Datei, auf die die URI zeigt, **MUSS** nach dem Merge auf `main` existieren.
- **MUSS** das `<minor>`-Segment der `$id` erhöhen, wenn das Schema ein rückwärtskompatibles Feld gewinnt, und das `<major>`-Segment erhöhen, wenn ein vorhandenes Feld umbenannt, entfernt oder sein Typ verengt wird. Schemata ohne versionierte `$id`-Segmente bestehen die Meta-Validierung nicht.
- **DARF NICHT** eine `$id`-URI über zwei nicht verwandte Schemata hinweg wiederverwenden. Das Repo-verwurzelte GitHub-Pfad-Muster (`…/<repo>/blob/main/<owner-path>/schemas/<slug>-v<major>.<minor>.schema.yaml`) macht Eindeutigkeit automatisch, solange keine zwei Schemata denselben Dateinamen im selben On-Disk-Verzeichnis tragen.
- **SOLLTE** den GitHub-Pfad der `$id` als verbindlich für die On-Disk-Lage des Schemas behandeln: Ein Schema mit `$id: https://github.com/nolte/claude-shared/blob/main/project/features/schemas/feature-frontmatter-v1.0.schema.yaml` lebt genau unter `project/features/schemas/feature-frontmatter-v1.0.schema.yaml` im Repository-Checkout. Das letzte Pfadsegment der URI matched den Dateinamen, sodass `grep` und `gh search` die Datei aus beiden Richtungen finden.

### Datei-Layout und Endung

- **MUSS** jede Schema-Datei mit der Endung `.schema.yaml` benennen (kleingeschrieben, doppelte Endung). Die doppelte Endung ist das unmissverständliche On-Disk-Signal, dass die Datei ein Schema ist und keine Datendatei. `*.schema.yml` (einfaches `l`) ist verboten — das Portfolio normiert auf `.yaml`.
- **MUSS** Schemata neben den Daten ablegen, die sie regieren, unter einem `schemas/`-Verzeichnis: `<repo>/<owner-path>/schemas/<slug>-v<major>.<minor>.schema.yaml`. Zum Beispiel `project/features/schemas/feature-frontmatter-v1.0.schema.yaml` oder `.github/workflows/schemas/inputs-v1.0.schema.yaml`.
- **DARF NICHT** Schemata unter `spec/` ablegen. Der `spec/`-Baum ist Governance-Dokumenten vorbehalten (einschließlich dieser Spec), nicht maschinenlesbaren Schemata, die diese Governance-Dokumente vorschreiben.
- **DARF NICHT** ein Schema in eine portfolio-geteilte Lage heben (`spec/portfolio/<topic>/schemas/`). Repository-übergreifendes Teilen geschieht über `$id`-URI-Disziplin und absolute `$ref` in den GitHub-Pfad des besitzenden Repos; eine Zentralisierung von Schemata unter `spec/portfolio/` würde die Quelle der Wahrheit duplizieren und ist verboten.

### Dokument-Skelett

Jede Schema-Datei **MUSS** als YAML lesbar, als JSON Schema 2020-12 parsbar und auf der obersten Ebene als exakt die folgenden geordneten Schlüsseleinträge strukturiert sein:

1. `$schema` — die Dialekt-URI (siehe §Dialekt).
2. `$id` — die Identitäts-URI (siehe §Identität).
3. `title` — eine kurze, menschenlesbare Substantivphrase, die das beschriebene Objekt benennt (zum Beispiel `Feature Frontmatter`).
4. `description` — ein bis drei Sätze, die erklären, was das Schema regiert und wo es konsumiert wird. Die Description **MUSS** die regierende Spec benennen (`Refs spec/<topic>/<slug>/`), sodass das Schema zu seiner Governing-Spec rückverfolgbar ist.
5. `type` — das JSON-Schema-Type-Keyword. Für Schemata, die Objekte beschreiben, ist der Wert `object`; für Schemata, die Arrays beschreiben, `array`. Schemata, die eine Typ-Union beschreiben, verwenden auf der obersten Ebene stattdessen `oneOf` oder `anyOf` und lassen das `type` auf oberster Ebene weg.
6. `required` — die Liste der erforderlichen Property-Namen, alphabetisch. Entfällt für Schemata, deren oberster Typ nicht `object` ist.
7. `additionalProperties` — explizites `false` oder ein Inline-Schema. Der Portfolio-Default ist `false` für geschlossene Objekt-Formen; `true` ist nur erlaubt, wenn die `description` des Schemas erklärt, warum das Objekt absichtlich erweiterbar ist.
8. `properties` — die Sub-Schemata pro Property, in der Reihenfolge, in der die konsumierende Spec sie aufzählt. Property-Namen verwenden **snake_case**, sofern nicht die beschriebenen Daten selbst durch externen Standard camelCase sind (zum Beispiel GitHub-Actions-Inputs).
9. `$defs` — die Map wiederverwendbarer Sub-Schemata. Nur vorhanden, wenn mindestens ein Eintrag per `$ref` aus anderer Stelle im Dokument referenziert wird; nie leer vorhanden.
10. `examples` — eine Liste mit mindestens einem voll-gültigen Beispiel-Objekt. Das Beispiel **MUSS** gegen das Schema validieren; das Meta-Validierungs-Gate beweist es.

- **DARF NICHT** zusätzliche Schlüsseleinträge auf oberster Ebene jenseits der zehn aufgeführten einführen. Implementierungsspezifische Erweiterungs-Keywords (`x-…`) sind auf oberster Ebene verboten; ist eine Vendor-Erweiterung tatsächlich nötig, lebt sie unter einem einzigen Top-Level-Objekt `vendorExtensions`, dokumentiert in der `description` des Schemas.
- **SOLLTE** unmittelbar über der ersten Nicht-Kommentar-Zeile der Datei einen einzeiligen YAML-Kommentar tragen, in der Form `# Schema for <object name>; consumed by <consumer>`, sodass ein Leser den Scope ohne Parsing erkennt.

### Property-Sub-Schemata

Innerhalb von `properties` und innerhalb von `$defs` **MUSS** jedes einzelne Property-Sub-Schema ebenfalls einem reduzierten Skelett folgen:

- `type` — das JSON-Schema-Type-Keyword (`string`, `integer`, `number`, `boolean`, `array`, `object`, oder `null`); niemals weggelassen, außer die Property nutzt `oneOf`/`anyOf`/`enum` zur Form-Beschränkung.
- `description` — ein Satz, der erklärt, was die Property bedeutet und warum sie existiert; niemals weggelassen auf oberer `properties`-Ebene. Für triviale Enum-Mitglieder innerhalb eines verschachtelten String-Arrays ist Weglassen erlaubt.
- Typ-spezifische Constraints (`enum`, `pattern`, `minimum`, `maximum`, `minLength`, `maxLength`, `format`, `items`, `properties`, …) folgen JSON Schema 2020-12 direkt, ohne portfolio-spezifische Umbenennung.
- `default` — nur vorhanden, wenn die konsumierende Spec einen Default definiert; nie erfunden, um „hilfreich zu sein". Ein `default` eines Schemas ist Dokumentation, keine Koerzion.
- `examples` — vorhanden auf Properties, deren Bedeutung sich nicht aus Name und `description` allein erschließt (freie Strings, komplexe Objekte, regex-eingeschränkte Werte).

### Referenzen (`$ref` und `$defs`)

- **MUSS** ein Sub-Schema in `$defs` herausziehen und per `$ref` referenzieren, sobald dieselbe Form mehr als einmal im selben Schema-Dokument auftaucht. Inline-Duplizierung von Objekt-Schemata ist die häufigste Drift-Ursache über Schema-Dateien hinweg und ist verboten.
- **MUSS** jeden `$defs`-Eintrag in `PascalCase` benennen (`SemverString`, `ISODate`, `FeatureSlug`). Die Benennung weicht bewusst vom snake_case der `properties` ab, damit ein `$ref`-Leser auf einen Blick erkennt, dass das Ziel eine wiederverwendbare Definition ist, kein Property-Name.
- **MUSS** `$ref`-Ziele innerhalb desselben Dokuments im JSON-Pointer-Fragment-Format `#/$defs/<Name>` adressieren. Andere Fragment-Formen (`#/properties/foo`, Anchor-basierte Refs ohne `$anchor`) sind verboten.
- **DARF** ein externes Schema per absoluter `$id`-URI referenzieren (`$ref: https://github.com/nolte/<repo>/blob/main/<owner-path>/schemas/<slug>-v<major>.<minor>.schema.yaml`), wenn das externe Schema in einem anderen `https://github.com/nolte/`-namensraumigen Repository liegt und seine Datei auf dessen `main`-Branch committed ist. Die Validator-Konfiguration des konsumierenden Repositories ist dafür zuständig, die URI auf einen fetchbaren Dateipfad zu mappen — typischerweise durch Spiegelung der Datei unter einem lokalen `vendor/schemas/`-Verzeichnis oder durch Klonen des besitzenden Repos als Build-Zeit-Abhängigkeit.
- **DARF NICHT** Relativpfad-`$ref`-Ziele verwenden (`$ref: ../other.schema.yaml#/$defs/Foo`). Relative Pfade brechen in dem Moment, in dem das Schema per `$id` aus einem anderen Working Directory importiert wird.

### Dokumentation und Auffindbarkeit

- **MUSS** in der `description` auf oberster Ebene jedes Schemas die konsumierende Spec benennen, mittels des Literal-Teilstrings `Refs spec/<topic>/<slug>/`. Das ist dieselbe `Refs`-Form, die in Pull-Request-Bodies verwendet wird (per `spec/project/pull-request-workflow/`), und holt Schema-Dateien in denselben Traceability-Graphen.
- **SOLLTE** einen Header-YAML-Kommentarblock (Zeilen, die mit `# ` beginnen) über `$schema` tragen, der den Zweck des Schemas für einen menschlichen Leser zusammenfasst, insbesondere wenn das Schema mehr als ~30 Zeilen umfasst.
- **MUSS** jede Schema-Datei im README des Repositories oder in einem neben den Schemata abgelegten `schemas/README.md` auflisten, sodass ein Leser, der ohne Vorwissen im Repo landet, die Schemata ohne Filesystem-Grep aufzählen kann.

### Meta-Validierung und Datenvalidierung

- **MUSS** jede `*.schema.yaml`-Datei im Repository gegen das JSON-Schema-2020-12-Meta-Schema validieren, als Teil des Quality-Gates des Repositories (`task lint` oder Äquivalent). Eine Datei unter `*.schema.yaml`, die die Meta-Validierung nicht besteht, lässt das Quality-Gate scheitern; einen Soft-Fail-Pfad gibt es nicht.
- **MUSS** jede Datendatei (jede `*.yaml`- oder `*.json`-Datei unter einem Pfad, den das Schema per Sidecar-`# yaml-language-server: $schema=…`-Kommentar, per `# Refs schema://…`-Kommentar oder per Repository-Level-`.schemas-config.yaml`-Mapping als regiert erklärt) gegen ihr deklariertes Schema validieren, als Teil desselben Quality-Gates.
- **SOLLTE** `check-jsonschema --check-metaschema` für Meta-Validierung in python-lastigen Repos bevorzugen und `ajv compile --spec=draft2020` in node-lastigen; die Wahl ist Pro-Repo und wird im `Taskfile.yml` des Repos festgehalten.
- **DARF NICHT** das Fehlen eines Validators als bestehendes Gate werten. Ist der gewählte Validator nicht installiert, scheitert das Gate mit einem Installationshinweis; stillschweigendes Überspringen ist verboten.

### Lebenszyklus

- **MUSS** ein neues Schema (eine neue `<slug>-v1.0.schema.yaml`) über den Skill `nolte-shared:yaml-json-schema` einführen, sodass die Dialekt-, Identitäts-, Layout- und Meta-Validierungs-Invarianten ohne Operator-Drift angewendet werden.
- **MUSS** ein bestehendes Schema revidieren, indem eine neue Datei `<slug>-v<major>.<minor+1>.schema.yaml` (Minor-Bump) oder `<slug>-v<major+1>.0.schema.yaml` (Major-Bump) geschrieben und Konsumenten auf die neue `$id` umgestellt werden. Die vorherige Datei bleibt liegen, bis jeder Konsument migriert ist; sie wird in einem Folge-Commit entfernt, sobald kein Konsument die `$id`-URI mehr referenziert.
- **DARF NICHT** eine Schema-Datei in-place editieren, sobald sie von außerhalb des eigenen Repositories per `$id` referenziert worden ist. In-place-Edits an extern referenzierten Schemata brechen Konsumenten, die die `$id`-URI pinnen.
- **SOLLTE** jede Schema-Anhebung in den Release Notes des Repositories unter einer `Schema`-Überschrift festhalten; der `release-notes-curate`-Skill erkennt die Überschrift und führt sie nach oben.

### Abgrenzung

- **MUSS** diese Spec von `spec/project/feature/` abgegrenzt halten: Die Feature-Spec regiert, *welche* Felder ein Feature-Frontmatter trägt; diese Spec regiert, *wie* das Schema, das diese Felder beschreibt, geschrieben wird.
- **MUSS** diese Spec von `spec/project/project-structure/` abgegrenzt halten: Die Structure-Spec regiert das Repository-Layout; diese Spec regiert Schemata, die innerhalb der `schemas/`-Verzeichnisse dieses Layouts liegen.
- **DARF NICHT** invocate werden, um OpenAPI-Schema-Objekte, AsyncAPI-Schema-Objekte oder JSON-codierte JSON-Schema-Dokumente zu validieren. Diese Formate haben eigene Specs oder werden welche bekommen.

## Akzeptanzkriterien

- [ ] Jede Datei im Repository, die `**/*.schema.yaml` matched, deklariert `$schema: https://json-schema.org/draft/2020-12/schema` als ersten Schlüsseleintrag und eine `$id` unterhalb von `https://github.com/nolte/<repo>/blob/main/` als zweiten; der Pfad der URI nach `/blob/main/` matched den tatsächlichen Repository-relativen Pfad der Datei.
- [ ] Jede `*.schema.yaml`-Datei besteht die JSON-Schema-2020-12-Meta-Validierung über `task lint`; der Lint-Schritt verlässt sich ausdrücklich nicht auf einen Soft-Pass — ein synthetisch defektes Schema im Regressionstest des Gates führt zu Exitcode ungleich Null.
- [ ] Die `description` jeder `*.schema.yaml`-Datei trägt den Literal-Teilstring `Refs spec/`, der mindestens eine regierende Spec benennt.
- [ ] Jede Datendatei unter einem als schema-regiert erklärten Pfad validiert im selben Lint-Schritt gegen ihr Schema; die Einführung einer synthetisch ungültigen Datendatei wird erkannt.
- [ ] Keine `*.schema.yaml`-Datei verwendet Relativpfad-`$ref`-Ziele; `grep -R '\$ref:.*\.\./' -- '**/*.schema.yaml'` liefert leer.
- [ ] Keine `*.schema.yaml`-Datei mischt Dialekte; jede `$ref` löst entweder auf `#/$defs/…` im gleichen Dokument oder auf eine absolute `https://github.com/nolte/…`-URI auf.
- [ ] Jedes Property-Sub-Schema innerhalb der obersten `properties` trägt eine `description`; das Meta-Validierungs-Gate scheitert auf fehlenden Descriptions.
- [ ] Der Skill `nolte-shared:yaml-json-schema` existiert und seine `SKILL.md` zitiert diese Spec per `spec/project/yaml-json-schema/`.
- [ ] Das README des Repositories (oder ein `schemas/README.md`) zählt jede ausgelieferte `*.schema.yaml`-Datei auf, mit ihrer `$id`, ihrem Title und ihrer konsumierenden Spec.

## Offene Fragen

- Soll die Spec `unevaluatedProperties: false` zusätzlich zu `additionalProperties: false` für geschlossene Objekt-Schemata mit `allOf`-Komposition vorschreiben, oder reicht die einfachere Regel, bis Komposition häufig wird?
- Soll Code-Generierung aus Schemata (Pydantic, TypeScript, Go) in einer Folge-Revision zu einem SOLL werden, und welcher Generator wird der Portfolio-Default?
- Sollen `*.json`-Schema-Dateien überhaupt zulässig sein (mit denselben `$schema`/`$id`/Skelett-Regeln), oder erzwingt das Portfolio YAML-only-Autoring, selbst wenn ein externer Konsument JSON bevorzugt?

## Referenzen

- JSON-Schema-2020-12-Spezifikation: <https://json-schema.org/draft/2020-12/release-notes>
- JSON-Schema-2020-12-Meta-Schema: <https://json-schema.org/draft/2020-12/schema>
- JSON-Schema-Core (`$schema`, `$id`, `$ref`, `$defs`): <https://json-schema.org/draft/2020-12/json-schema-core>
- JSON-Schema-Validation-Keywords: <https://json-schema.org/draft/2020-12/json-schema-validation>
- `yaml-language-server` Schema-Association-Kommentar (`# yaml-language-server: $schema=…`): <https://github.com/redhat-developer/yaml-language-server#using-inlined-schema>
- `spec/project/feature/` — Beispiel-Konsument; Feature-Frontmatter ist ein Kandidat-Schema-Ziel.
- `spec/project/pull-request-workflow/` — Ursprung des `Refs spec/<topic>/<slug>/`-Traceability-Musters.
- `spec/project/quality-gate/` — Gate, das Meta-Validierung und Datenvalidierung in CI ausführt.
- `spec/project/spec-driven-development/` — Dach-Prinzip, von dem diese Spec erbt.
