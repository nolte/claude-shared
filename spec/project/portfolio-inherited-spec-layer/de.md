# Portfolio-vererbte Spec-Schicht

Status: draft
Portfolio-Scope: portfolio

## Context

Das `nolte/*`-Portfolio steuert seine Repositories über einen geteilten Spec-Korpus. Die kanonische Kopie jeder portfolioweiten Konvention – das Branching-Modell, der Pull-Request-Workflow, die Projektstruktur, der Plugin-Authoring-Vertrag – lebt in diesem `claude-shared`-Hub-Repository unter `spec/`. Heute hat ein Consumer-Repository, das von einer dieser Konventionen geregelt werden möchte, nur eine Option: die Spec-Datei **wortgleich kopieren** in den eigenen `spec/`-Baum. Diese Kopie ist unmittelbar eine DRY-Verletzung. In dem Moment, in dem der Hub die kanonische Spec überarbeitet, ist jede Kopie still veraltet, und es gibt keinen Mechanismus, der eine *beabsichtigte* Repo-Abweichung von einer *versehentlichen* Drift unterscheiden kann. `spec/project/spec-drift-audit/` kann die Specs eines einzelnen Repositories gegen dessen eigene Implementierung abgleichen, kennt aber keinen Upstream-Kanon, dem eine lokale Spec folgen soll.

Genau diese Lücke hat `spec/portfolio/tech-stack/` für die technischen Bausteine eines Repositories bereits geschlossen: ein portfolioweiter globaler Stack lebt einmal im Hub, jedes Mitglied erbt ihn, und Abweichungen werden deklariert, nie durch Auslassung impliziert. Diese Spec überträgt denselben Vertrag – **per Referenz erben, jede Abweichung deklarieren** – auf den Spec-Korpus selbst.

Sie definiert eine **portfolio-vererbte Spec-Schicht**: einen Mechanismus, mit dem ein Consumer-Repository portfolioweite Specs *referenziert*, die kanonisch im Hub leben, statt sie zu kopieren. Die tragende Prämisse ist **DRY**: eine portfolioweite Spec existiert **genau einmal**, im Hub, und jeder Consumer referenziert sie. Der Consumer speichert nur das Vererbungs-Manifest plus eventuelle deklarierte Deltas – nie eine Kopie des geerbten Texts.

Der Vertrag ist ein bewusstes **hybrides Precedence-Modell**, gegründet auf externer Best Practice (die vollständige zitierte Recherche liegt unter `.resume/portfolio-inherited-spec-layer/research-report.md`). Konfigurations-Tools (TypeScript `extends`, ESLint, Helm, Kustomize, Renovate) konvergieren auf *local-wins, last-defined*, lösen Overrides aber per Position und Auslassung ohne Marker auf, sodass stille Divergenz immer möglich ist. Governance-Systeme mit Invarianten (AWS IAM explicit-deny-wins, OPA/Rego-Konfliktfehler, CSS-Cascade-Layers) machen Divergenz stattdessen laut und lassen eine autoritative Schicht Werte sperren, die eine lokale Schicht nicht aufweichen kann. Ein Spec-Korpus ist ein Governance-Korpus, daher übernimmt diese Spec das Governance-Modell: **geerbte Specs sind by default autoritativ; ein Consumer weicht nur über einen expliziten, begründeten Override ab; undeklarierte Divergenz ist ein harter Fehler; und ein portfolio-gesperrter Invarianten-Tier kann downstream gar nicht aufgeweicht werden.** Das spiegelt die zwei Vererbungs-Idiome, die das Portfolio bereits betreibt – `tech-stack` additive-override-with-rationale und die tag-gepinnte Probot/Renovate-`_extends`/`extends`-Referenz –, sodass das Portfolio ein mentales Modell für Vererbung behält, statt einen dritten Dialekt zu erfinden.

Leser: Maintainer von `nolte/*`-Consumer-Repositories, die von Hub-Specs geregelt werden wollen, ohne sie zu kopieren; der `claude-shared`-Maintainer, der kuratiert, welche Specs portfolioweit sind; der `spec`-Skill, der einen Local-vs-Inherited-Drift-Pass erhält; `spec-drift-audit` und `spec-readiness`, die Vererbungs-Findings klassifizieren; Contributors, die ein Repository von kopierten Specs auf referenzierte migrieren. Implementoren, die den `spec`-Skill oder das `spec/.spec-config.yml`-Schema erweitern, arbeiten aus §Requirements; Consumer-Repository-Maintainer arbeiten aus §"Copy→Reference-Migrationspfad" und §"Das Vererbungs-Manifest"; ein `spec-drift-audit`-Maintainer arbeitet aus §"Drift-Detection".

Provenance: Diese Spec ist unter dem `spec`-Skill verfasst und folgt dem Sechs-Abschnitts-Template unter `skills/spec/templates/spec.template.md`; künftige Revisionen folgen demselben Pfad per `spec/project/spec-driven-development/`.

## Goals

- Eine portfolioweite Spec lebt **genau einmal** im Hub und wird von jedem Consumer referenziert; kein Consumer speichert je eine wortgleiche Kopie geerbten Spec-Inhalts.
- Ein Consumer deklariert, von welchem Hub er erbt, gepinnt auf ein explizites Release, in einem Manifest-Key (`inherits:` in `spec/.spec-config.yml`), sodass das Übernehmen einer Upstream-Revision ein bewusster, prüfbarer Bump statt unsichtbarer Drift ist.
- Geerbte Specs sind by default autoritativ; jede Consumer-Abweichung ist **sichtbar, begründet und prüfbar**, und undeklarierte Divergenz vom Kanon ist ein harter Fehler, nie ein stiller Schatten.
- Ein kleiner **portfolio-gesperrter Invarianten**-Tier existiert, den ein Consumer strenger, aber nie schwächer machen darf – der AWS-SCP-artige Schutzwall für Regeln, aus denen das Portfolio kein Repository austreten lassen will.
- Die Menge vererbbarer Specs wird **pro Spec** kuratiert, nicht pro Verzeichnis, sodass ein Docs-only-Consumer nie gezwungen wird, eine Code-only-Spec zu erben, und umgekehrt.
- Cross-References lösen deterministisch im kombinierten Namespace `local ∪ inherited` auf, wobei Kollisionen als Fehler statt als stilles Last-Wins auftauchen und Ghost-References genau so erkannt werden, wie `spec/project/spec-readiness/` es bereits verlangt.
- Ein Consumer, dessen `canonical_language` von der des Hubs abweicht, erbt das kanonische Artefakt des Hubs als einzige Quelle der Wahrheit und behält seine eigene Sprache als abgeleitete Übersetzungssicht, sodass kein Sprachpaar die Anzahl autoritativer Kopien vervielfacht.
- Es gibt einen definierten, mechanischen Migrationspfad von einer kopierten Spec zu einer referenzierten, mit `nolte/claude-home-assistant#14` als durchgearbeitetem Fall.

## Non-Goals

- **Festlegen, welche Specs portfolioweit sind.** Diese Spec definiert das `Portfolio-Scope:`-Flag und seine Semantik; *welche* Hub-Specs `portfolio`-Scope tragen, ist die Kuratierungs-Entscheidung des `claude-shared`-Maintainers, je Spec einzeln getroffen. Diese Spec definiert den Mechanismus, nicht die Mitgliederliste.
- **`spec/portfolio/tech-stack/` ersetzen.** Jene Spec erbt die *technischen Bausteine* eines Repositories; diese Spec erbt die *Spec-Dokumente* selbst. Sie teilen bewusst ein Vererbungs-Idiom, regeln aber disjunkte Artefakte.
- **Ein allgemeiner transitiver Vererbungs-Resolver.** Vererbung ist bewusst flach: eine Hub-Schicht plus eine Consumer-Schicht, keine Mehr-Sprung-Ketten (siehe §"Flache Kette und Wurzel-Grenze"). Eine C3-artige Linearisierung für tiefe Ketten ist explizit außerhalb des Scopes und in §Open Questions geparkt.
- **Die Übersetzungssicht des Consumers automatisch generieren.** Diese Spec verlangt, dass eine Nicht-kanonisch-sprachige Darstellung *abgeleitet* und *nie autoritativ* ist und dass Drift-Checks canonical-to-canonical laufen; sie definiert nicht den Übersetzungs-Generierungs-Workflow selbst, den der bestehende Übersetzungs-Flow des `spec`-Skills bereits besitzt.
- **Die Severity-Skala oder die Ghost-Reference-Regel neu definieren.** Severities gehören `spec/claude/review-plan/` §"Severity scale" und die Ghost-Reference-Regel `spec/project/spec-readiness/`; diese Spec referenziert beide und wiederholt keine.
- **Die Marketplace-Publish-Mechanik und der Plugin-Versions-Bump.** Gehören `spec/project/release-automation/` und den Manifest-Specs; diese Spec verlangt nur, dass die vererbbare Spec-Teilmenge mit dem Plugin *ausgeliefert* und *tag-gepinnt* wird.
- **Geerbte Prosa tief mergen.** Ein Override ersetzt einen ganzen deklarierten Abschnitt; diese Spec definiert kein Merge auf Absatz- oder Satzebene geerbten Spec-Texts (siehe §"Override-Granularität und Merge-Tiefe").

## Requirements

### Das Vererbungs-Manifest

- **MUSS [MUST]** die Vererbungs-Deklaration des Consumers in seiner bestehenden `spec/.spec-config.yml` unter einem neuen optionalen Top-Level-Key `inherits:` verorten. Ein Repository ohne `inherits:`-Key erbt nichts und wird allein von seinem lokalen `spec/`-Baum geregelt; der Key ist rein additiv zu den drei Keys (`canonical_language`, `languages`, `spec_root`), die die Datei bereits trägt.
- **MUSS [MUST]** `inherits:` als Liste von **Source-Records** strukturieren, jeder mit genau diesen Feldern:
  - `source`: der Hub-Identifier – der Plugin-/Marketplace-Name, dessen ausgelieferter Spec-Korpus geerbt wird (Referenzwert: `nolte-shared`).
  - `ref`: ein **tag-gepinnter** Release-Identifier dieses Hubs (zum Beispiel `v0.1.8`). Der `ref` **DARF NICHT [MUST NOT]** ein gleitender Branch-Name sein; ein gleitender oder fehlender `ref` ist ein `Warning`-Audit-Finding (§"Audit- und CI-Integration"). Dies ist die explizite Verbesserung gegenüber Probot Settings `_extends`, das den Default-Branch des referenzierten Repositories gleiten lässt und kein Tag-Pinning bietet (siehe §References).
  - `overrides:` (optional): eine Liste von **Override-Records** per §"Precedence und Override-Deklaration".

  ```yaml
  canonical_language: en
  languages: [en, de]
  spec_root: spec
  inherits:
    - source: nolte-shared
      ref: v0.1.8
      overrides:
        - spec: project/branching-model
          section: "§Branch roles"
          reason: "trunk-based repo; the long-lived develop branch role does not apply"
          local: spec/project/branching-model/override.md
  ```

- **MUSS [MUST]** jede geerbte Spec über ihren **logischen Key** `<topic>/<slug>` auflösen (zum Beispiel `project/branching-model`), unabhängig davon, welche Sprachdatei sie trägt. Der Key ist der stabile Identifier über die Vererbungsgrenze; der Oberflächen-Dateiname und die Sprache sind es nicht.
- **MUSS [MUST]** den aufgelösten Hub-Korpus als **regenerierbaren Cache** behandeln: materialisiert eine Implementierung geerbte Spec-Dateien für Offline-Lesen auf der Platte, dann unter einem gitignorierten Cache-Pfad (Referenzpfad: `.spec-cache/`) und nie innerhalb des getrackten `spec/`-Baums des Consumers. Eine getrackte wortgleiche Kopie geerbten Inhalts ist ein `Critical`-Audit-Finding – genau die Kopie, die diese Spec eliminieren soll.

### Das `Portfolio-Scope:`-Flag

- **MUSS [MUST]** Vererbbarkeit **pro Spec** über eine `Portfolio-Scope:`-Header-Zeile in der kanonischen Datei steuern, neben der bestehenden `Status:`-Zeile. Ihr Wert ist einer von:
  - `portfolio`: die Spec ist Teil der vererbbaren Menge – eine echte portfolioweite Invariante, die ein Consumer referenzieren darf.
  - `local`: die Spec ist repo-intern und wird nie geerbt.
- **MUSS [MUST]** eine Spec ohne `Portfolio-Scope:`-Zeile auf `local` defaulten. Vererbbarkeit ist Opt-in; eine Spec wird nur durch einen expliziten, prüfbaren Akt im Hub portfolioweit.
- **MUSS [MUST]** `portfolio`-Scope für Specs unter **beiden** `spec/project/*` und `spec/claude/*` verfügbar machen. Der Plugin-Authoring-Vertrag (`spec/claude/*` – `skill-management`, `agent-management`, `skill-vs-agent`, `review-plan`, `resumable-work`, `plugin-scoping`) ist der am echtesten portfolioweite Korpus überhaupt, da jedes code-tragende Repository, das Claude-Code-Capabilities ausliefert, sie identisch verfasst; ihn auszuschließen würde den am stärksten geteilten Korpus ungeteilt lassen.
- **DARF NICHT [MUST NOT]** Vererbbarkeit per Verzeichnis steuern. Eine pauschale „ganz `spec/project/*`"-Regel würde repo-geformte Specs (zum Beispiel `e2e-test-automation`, `mermaid-diagrams`, `blog-author`, `api-error-handling`) Consumern aufzwingen, denen diese Capability fehlt, im Widerspruch zum Audience-Split-Prinzip von `spec/claude/plugin-scoping/`. Das Flag ist die Einheit; das Verzeichnis nicht.
- **MUSS [MUST]** die geerbte Einheit beim **kanonischen** Inhalt des Hubs belassen. Das Flag lebt auf der kanonischen Datei; eine Übersetzung trägt nie einen eigenständigen Scope.

### Zwei-Quellen-Auflösung

- **MUSS [MUST]** die **effektive Spec-Menge** eines Consumers als Vereinigung von (a) dem lokalen `spec/`-Baum und (b) jeder Hub-Spec berechnen, deren `Portfolio-Scope:` beim gepinnten `ref` jeder `inherits:`-Source `portfolio` ist.
- **MUSS [MUST]** eine Suche nach dem logischen Key `<topic>/<slug>` gegen die effektive Menge mit **Local-First**-Semantik auflösen, vorbehaltlich der Konfliktregeln unten – Local-First ist die *Such*-Reihenfolge, keine Lizenz dafür, dass lokaler Inhalt bei Konflikt still gewinnt.
- **MUSS [MUST]** eine lokale Spec, die einen logischen Key mit einer geerbten `portfolio`-Scope-Spec teilt, als genau einen von zwei Fällen behandeln:
  - Die lokale Spec ist ein **deklarierter Override** (sie taucht als `overrides:`-Record auf, der diese geerbte Spec adressiert): die Auflösung ist das Abschnitts-Merge aus §"Precedence und Override-Deklaration".
  - Die lokale Spec ist **kein** deklarierter Override: dies ist eine **undeklarierte Divergenz** und ein `Critical`-Audit-Finding. Der Consumer muss entweder die lokale Kopie löschen (und erben) oder den Override deklarieren. Es gibt keinen Silent-Local-Wins-Pfad; eine undeklarierte Key-Kollision scheitert wie ein OPA/Rego-Konfliktfehler statt per Position aufzulösen.
- **MUSS [MUST]** Vererbung flach halten per §"Flache Kette und Wurzel-Grenze": eine geerbte Spec wird as-is vom Hub übernommen und nicht selbst gegen eine dritte Quelle neu aufgelöst.

### Precedence und Override-Deklaration

- **MUSS [MUST]** jede geerbte `portfolio`-Scope-Spec als **by default autoritativ** behandeln: ohne deklarierten Override regelt der geerbte Kanon den Consumer unverändert.
- **MUSS [MUST]** verlangen, dass eine Consumer-Abweichung von einer geerbten Spec nur über einen expliziten **Override-Record** unter der betreffenden `inherits:`-Source ausgedrückt wird, mit genau diesen Feldern:
  - `spec`: der logische Key `<topic>/<slug>` der überschriebenen geerbten Spec; **MUSS [MUST]** beim gepinnten `ref` der Source auf eine existierende `portfolio`-Scope-Spec auflösen, sonst ein `Warning`-Audit-Finding (gebrochene Override-Referenz).
  - `section`: die Überschrift des geerbten Abschnitts, den der Override ersetzt, in der `§<Section>`-Form, die der Korpus bereits für Cross-References nutzt.
  - `reason`: ein nicht-leerer Prosa-Satz, der die Abweichung begründet; ein leerer oder fehlender `reason` ist ein `Warning`-Audit-Finding. Dies spiegelt die verpflichtende `rationale` bei `tech-stack`-Overrides.
  - `local`: ein repository-relativer Pfad zur lokalen Override-Datei, die den ersetzenden Abschnittsinhalt trägt.
- **MUSS [MUST]** einen deklarierten Override als **Abschnitts-Ersatz** auflösen: die effektive Spec ist der geerbte Kanon mit jedem deklarierten `section` wortgleich durch den `local`-Inhalt des Consumers ersetzt; jeder nicht überschriebene Abschnitt bleibt der geerbte Kanon. Die Override-Datei trägt nur die ersetzten Abschnitte – nie eine Kopie des unberührten Rests.
- **MUSS [MUST]** einen **portfolio-gesperrten Invarianten**-Tier unterstützen: ein Requirement, das in einer geerbten `portfolio`-Scope-Spec direkt nach seinem RFC-2119-Keyword mit `[locked]` markiert ist (zum Beispiel `- **MUST** [locked] …`), ist downstream nicht überschreibbar. Ein `overrides:`-Record, dessen `section` ein `[locked]`-Requirement enthält, ist ein `Critical`-Audit-Finding. Ein Consumer **KANN [MAY]** *strenger* als eine gesperrte Invariante sein (ein zusätzliches lokales MUST, das ihr nicht widerspricht), **DARF** sie aber **NICHT [MUST NOT]** aufweichen oder unterdrücken – das AWS-SCP-Explicit-Deny-Analogon.
- **DARF NICHT [MUST NOT]** einen anderen Override-Mechanismus zulassen als den deklarierten `overrides:`-Record plus seine `local`-Datei. Insbesondere sind das In-Place-Editieren geerbten Inhalts, das Beschatten durch eine undeklarierte Same-Key-lokale-Spec und das Unterdrücken durch Auslassung allesamt verboten (die ersten zwei sind `Critical`; Unterdrückung-durch-Auslassung kann nicht entstehen, weil nichts kopiert wird, das man auslassen könnte).

### Override-Granularität und Merge-Tiefe

- **MUSS [MUST]** den **Abschnitt** zur Override-Einheit machen. Es gibt kein implizites Tief-Merge geerbter Prosa: ein Consumer, der ein einzelnes Requirement innerhalb eines Abschnitts ändern will, ersetzt den ganzen Abschnitt (mit der eingeschlossenen Änderung) und nennt den `reason`. Das entspricht dem Tool-übergreifenden Befund, dass Arrays und verschachtelte Blöcke standardmäßig wortgleich ersetzt, nicht konkateniert werden – die Merge-Tiefe explizit zu machen vermeidet den universellen Config-Vererbungs-Fallstrick.
- **MUSS [MUST]** listen-förmigen oder strukturierten geerbten Inhalt (zum Beispiel ein Enum, einen Schema-Block) gleich behandeln: ein Override ersetzt den ganzen Block; ein Teil-Element-Merge wird nicht abgeleitet.
- **KANN [MAY]**, wo eine künftige Revision eine explizite Additive-Merge-Direktive für ein bestimmtes Feld definiert, Tief-Merge nur als **deklarierte Ausnahme** zulassen; bis eine solche Direktive existiert, ist Ersatz die einzige Semantik. Jedes Tief-Merge MUSS Opt-in und benannt sein, nie der Default.

### Kombinierte-Namespace-Cross-Reference-Auflösung

- **MUSS [MUST]** jede Cross-Reference der Form `spec/<topic>/<slug>/` gegen den **kombinierten Namespace** `local ∪ inherited` auflösen, Local-First, genau wie §"Zwei-Quellen-Auflösung" eine direkte Suche auflöst.
- **MUSS [MUST]** eine Cross-Reference, deren logischer Key in weder der lokalen noch der geerbten Menge auflöst – oder auf eine Spec auflöst, der die referenzierte `§<Section>` fehlt –, als **Ghost-Reference** kennzeichnen, klassifiziert `Critical` per `spec/project/spec-readiness/`. Diese Spec fügt keine neue Ghost-Reference-Regel hinzu; sie erweitert den Namespace, gegen den jene Regel auflöst, um geerbte Specs.
- **MUSS [MUST]** einen logischen Key, der in **beiden** der lokalen und der geerbten Menge auflöst, wobei das Lokale **kein** deklarierter Override ist, als **Duplicate-Key-Kollision** und `Critical`-Finding behandeln – nie als stille Last-Wins-Auflösung. Dies ist das JSON-Schema-Duplicate-`$id`-Modell: eine Kollision ist ein Fehler, kein Precedence-Rätsel.
- **MUSS [MUST]** eine `§<Section>`-Referenz gegen die **effektive** (post-Override) Spec auflösen, sodass eine Referenz auf einen von einem Override ersetzten Abschnitt auf den ersetzenden Inhalt auflöst und eine Referenz auf einen von einem Override entfernten Abschnitt eine Ghost-Reference ist.

### Kanonische-Sprache-Behandlung

- **MUSS [MUST]** die geerbte Einheit zum **kanonisch-sprachigen** Artefakt des Hubs machen (Hub-`canonical_language`, aktuell `en`), identifiziert über seinen logischen Key. Ein Consumer erbt den kanonischen Inhalt, nicht eine bestimmte Sprachdarstellung.
- **MUSS [MUST]** einem Consumer, dessen `canonical_language` von der des Hubs abweicht (zum Beispiel ein `de`-kanonischer Consumer, der von einem `en`-kanonischen Hub erbt), erlauben, den Hub-Kanon als seine **Quelle der Wahrheit** zu erben; die eigensprachige Darstellung einer geerbten Spec durch den Consumer ist eine **abgeleitete Übersetzungssicht** und **DARF NICHT [MUST NOT]** als zweite kanonische Kopie behandelt werden. Eine separate autoritative Kopie in der Sprache des Consumers zu erzeugen ist das Silent-Fork-Versagen, das diese Spec verbietet.
- **MUSS [MUST]** Drift-Detection **canonical-to-canonical** ausführen: der `local`-Override-Inhalt eines Consumers wird, in der kanonischen Sprache des Hubs, gegen den geerbten kanonischen Abschnitt verglichen, den er beim gepinnten `ref` ersetzt. Eine veraltete oder abweichende Übersetzungssicht maskiert oder erfindet nie eine Divergenz, weil der Check die Übersetzungssicht nie liest.
- **SOLLTE [SHOULD]** die consumer-sprachige Übersetzungssicht geerbter Specs über den bestehenden Canonical→Translation-Flow des `spec`-Skills pflegen, sodass ein menschlicher Leser eines `de`-kanonischen Consumers geerbte Specs weiterhin in `de` liest, ohne dass diese Sicht autoritativ wird.

### Distribution und Versions-Pinning

- **MUSS [MUST]** die vererbbare Spec-Teilmenge verteilen, indem sie **mit dem Plugin** über den Marketplace ausgeliefert wird, tag-gepinnt an die Plugin-Release-Linie. Dies ist das Package-with-Lockfile-Modell: der Korpus existiert einmal im Hub-Registry-Eintrag, der Consumer referenziert ihn per gepinnter Version, und die On-Disk-aufgelöste Kopie ist ein regenerierbarer Cache. Heute wird `spec/` mit keinem Plugin ausgeliefert; die `portfolio`-Scope-Teilmenge auszuliefern ist eine bewusste, begrenzte Packaging-Änderung, und die Nicht-`portfolio`-(lokalen)-Specs bleiben repo-intern.
- **DARF NICHT [MUST NOT]** geerbte Specs per git submodule, git subtree, Sync/Vendoring (copier/cruft-artige Kopie) oder Symlink verteilen. Submodules tragen dokumentierte Clone-/Pull-/CI-/GC-Reibung; Subtree und Vendoring duplizieren den Korpus physisch, sodass ein beabsichtigter Override und eine versehentliche Drift ununterscheidbar werden; Symlinks scheitern über Clones und CI hinweg. Jedes verfehlt entweder das Exists-Exactly-Once- oder das No-Silent-Divergence-Ziel. (Die cruft-*Drift-Detection-Idee* wird in §"Drift-Detection" übernommen; seine Copy-Distribution nicht.)
- **MUSS [MUST]** jede `inherits:`-Source auf ein Release-Tag pinnen und Upstream-Revisionen durch einen expliziten `ref`-Bump übernehmen. Der Bump **SOLLTE [SHOULD]** je Consumer durch die bestehende Renovate-artige Update-Automatisierung des Portfolios sichtbar gemacht werden, sodass Veraltung eine sichtbare PR-Queue statt unsichtbarer Fäulnis wird.

### Flache Kette und Wurzel-Grenze

- **MUSS [MUST]** Vererbung **flach** halten: genau eine Hub-Schicht plus eine Consumer-Schicht. Eine geerbte Spec wird as-is übernommen und **nicht** gegen irgendeine weitere Quelle neu aufgelöst, sodass keine transitive Mehr-Sprung-Kette entsteht.
- **MUSS [MUST]** den Hub (`claude-shared`) als **Wurzel** behandeln: die eigene `spec/.spec-config.yml` des Hubs trägt keinen `inherits:`-Key, sodass die Auflösung am Hub terminiert. Ein Consumer, der selbst Hub für ein drittes Repository ist, liegt in dieser Revision außerhalb des Scopes (siehe §Open Questions).
- **DARF NICHT [MUST NOT]** eine zyklische Vererbungs-Deklaration zulassen (eine Source, die direkt oder indirekt zurück auf den Consumer auflöst); ein Zyklus ist ein `Critical`-Audit-Finding.

### Drift-Detection

- **MUSS [MUST]** die Drift-Check-Operation des `spec`-Skills (heute: Übersetzung-gegen-Kanon) um einen **Local-vs-Inherited**-Pass erweitern, der für jede `inherits:`-Source verifiziert:
  - jeder `overrides:`-Record-`spec` löst auf eine `portfolio`-Scope-Spec beim gepinnten `ref` auf;
  - jeder überschriebene `section` existiert weiterhin in dieser geerbten Spec beim gepinnten `ref` (ein verschwundenes Ziel ist ein veralteter Override, `Warning`);
  - kein überschriebener `section` enthält ein `[locked]`-Requirement (`Critical`);
  - jeder `reason` ist nicht-leer (`Warning`);
  - keine lokale Spec teilt einen logischen Key mit einer geerbten `portfolio`-Scope-Spec ohne deklarierten Override (`Critical`, undeklarierte Divergenz);
  - keine Cross-Reference ist eine Ghost-Reference oder eine Duplicate-Key-Kollision im kombinierten Namespace (`Critical`).
- **MUSS [MUST]** den Drift-Check **gegen den gepinnten `ref`** ausführen, nicht gegen das aktuelle `develop` des Hubs, sodass die Konformität eines Consumers gegen genau den Upstream beurteilt wird, den er gepinnt hat.
- **SOLLTE [SHOULD]** die Local-vs-Inherited-Drift-Findings in `spec/project/spec-drift-audit/` integrieren, sodass Vererbungs-Drift im selben wiederkehrenden Audit abgeglichen wird wie Spec-gegen-Implementierung-Drift, statt als isolierter Check. Konkret macht `spec-drift-audit` die **Vererbungs-Drift-Finding-Klasse** dieser Spec (die oben aufgezählten Local-vs-Inherited-Findings) bei den in §"Audit- und CI-Integration" gemappten Severities sichtbar, neben seinen bestehenden Spec-gegen-Implementierung-Findings; diese Spec besitzt die Finding-Definitionen und Severities, `spec-drift-audit` besitzt den wiederkehrenden Lauf, der sie meldet.

### Audit- und CI-Integration

- **MUSS [MUST]** jedes Finding dieser Spec über die kanonische Severity-Skala aus `spec/claude/review-plan/` §"Severity scale" klassifizieren; diese Spec wiederholt keine der vier Stufen und mappt ihre Findings nur darauf:
  - `Critical`: eine getrackte wortgleiche Kopie geerbten Inhalts im `spec/`-Baum des Consumers; eine undeklarierte Divergenz (lokale Spec beschattet eine geerbte `portfolio`-Scope-Spec ohne deklarierten Override); ein Override, der ein `[locked]`-Requirement adressiert; eine Ghost-Reference oder Duplicate-Key-Kollision im kombinierten Namespace; eine zyklische Vererbungs-Deklaration.
  - `Warning`: eine gebrochene Override-Referenz (`spec` löst beim gepinnten `ref` nicht auf); ein veralteter Override (überschriebener `section` upstream verschwunden); ein leerer oder fehlender `reason`; ein gleitender oder fehlender `ref` auf einer `inherits:`-Source.
  - `Suggestion`: ein `inherits:`-`ref`, gepinnt auf ein Hub-Release mehr als einen abgeschlossenen Sprint hinter dem neuesten Hub-Release (die Veraltungs-Schwelle, passend zur Ein-abgeschlossener-Sprint-Koordinations-Cadence, die `spec/portfolio/tech-stack/` bereits nutzt); eine `portfolio`-Scope-Hub-Spec, die noch von keinem Consumer referenziert wird.
  - `Info`: ein deklarierter Override auf einem Consumer (bewusste, geprüfte Abweichung – nützlicher Kontext, keine Aktion).
- **MUSS [MUST]** undeklarierte Divergenz zu einem **CI-Fehler** machen, nicht zu einer weichen Warnung: der Local-vs-Inherited-Drift-Pass endet bei jedem offenen `Critical` mit Nicht-Null-Exit, sodass ein stiller Fork `develop` nicht erreichen kann. Dies ist die Loud-Failure-Governance-Haltung, kein Discouraged-Habit-Stupser.

### Copy→Reference-Migrationspfad

- **MUSS [MUST]** die Migration von einer kopierten Spec zu einer referenzierten als diese Sequenz definieren, für einen Consumer, der aktuell eine wortgleiche Kopie einer Hub-`portfolio`-Scope-Spec hält (durchgearbeiteter Fall: `nolte/claude-home-assistant#14`):
  1. Die `inherits:`-Source in der `spec/.spec-config.yml` des Consumers hinzufügen (oder erweitern), gepinnt auf einen Hub-`ref`, dessen Korpus die kanonische Spec beim erforderlichen `Portfolio-Scope: portfolio` enthält.
  2. Die lokale wortgleiche Kopie gegen den geerbten Kanon bei diesem `ref` diffen. Ist die Kopie identisch, die lokale Kopie ersatzlos löschen – sie löst nun aus der geerbten Menge auf.
  3. Trägt die Kopie legitime Abweichungen, jede als deklarierten `overrides:`-Record plus eine minimale `local`-Override-Datei erfassen, die nur die abweichenden Abschnitte enthält, dann den Rest der lokalen Kopie löschen.
  4. Den Local-vs-Inherited-Drift-Check ausführen; jeden `Critical` (keine undeklarierte Divergenz, kein Locked-Section-Override) und jeden `Warning` vor dem Merge auflösen.
  5. Die Migration als spec-verankerten PR per `spec/project/pull-request-workflow/` landen, mit `Refs`-Link auf diese Spec.
- **DARF NICHT [MUST NOT]** eine Migration abschließen, die für denselben logischen Key sowohl eine getrackte lokale Kopie als auch eine `inherits:`-Referenz hinterlässt; der Endzustand ist Referenz-plus-deklarierte-Deltas, nie Referenz-plus-Kopie.

### Tooling und Durchsetzung

- **MUSS [MUST]** den Resolver-Einstiegspunkt für einen geerbten Korpus zur gebündelten `spec/`-Payload des Plugins machen, gelesen vom installierten Hub-Plugin beim gepinnten `ref` über `${CLAUDE_PLUGIN_ROOT}/spec/` – dieselbe Bundled-Asset-Pfad-Konvention, die jeder Plugin-Skill bereits für ausgelieferte Ressourcen nutzt. Der `inherits:`-`ref` eines Consumers wählt das installierte Hub-Plugin-Release, und der aus `${CLAUDE_PLUGIN_ROOT}/spec/` bei diesem Release aufgelöste Korpus ist der regenerierbare Cache aus §"Das Vererbungs-Manifest". Ob die Plugin-Payload nur `Portfolio-Scope: portfolio`-Dateien trägt oder den ganzen `spec/`-Baum, zur Auflösungszeit auf `portfolio`-Scope gefiltert, ist eine Implementierungs-Wahl, die der Tooling-Schritt klärt; der Resolver-Einstiegspunkt ist auf `${CLAUDE_PLUGIN_ROOT}/spec/` festgelegt, und das Marketplace-Payload-Packaging, das `spec/` dort platziert, gehört `spec/project/release-automation/`.
- **MUSS [MUST]** das `spec/.spec-config.yml`-Schema um den `inherits:`-Key (und seine Source-/Override-Record-Formen) erweitern und die `Portfolio-Scope:`-Header-Zeile sowie den `[locked]`-Requirement-Marker erkennen; die Schema-Änderung wird vom selben CI-/Pre-Commit-Mechanismus validiert, der das Repository bereits absichert, sodass ein malformter `inherits:`-Block `develop` nicht erreichen kann.
- **MUSS [MUST]** den `spec`-Skill (`skills/spec/SKILL.md`) um den Local-vs-Inherited-Drift-Pass aus §"Drift-Detection" erweitern, der sich mit seinem bestehenden Übersetzungs-Drift-Check komponiert – nicht ihn ersetzt.
- **KANN [MAY]** reichere Affordanzen (ein dediziertes Migrations-Sub-Kommando, automatisches Override-Datei-Scaffolding, eine gerenderte „Inherited vs Local"-Sicht) auf spätere Revisionen verschieben; die tragende Durchsetzung ist die Schema-Validierung plus der Drift-Pass.

## Acceptance Criteria

- [ ] `spec/.spec-config.yml` akzeptiert eine optionale `inherits:`-Liste von Source-Records (`source`, `ref`, optional `overrides:`); ein malformter Record wird von CI/Pre-Commit abgelehnt und kann `develop` nicht erreichen.
- [ ] Die kanonische Datei einer Spec darf eine `Portfolio-Scope:`-Header-Zeile tragen (`portfolio` | `local`); eine Datei ohne eine solche Zeile wird von der Auflösungs- und Audit-Tooling als `local` behandelt.
- [ ] `Portfolio-Scope: portfolio` wird für Specs unter beiden `spec/project/*` und `spec/claude/*` beachtet; keine Verzeichnis-Ebenen-Vererbbarkeits-Regel existiert.
- [ ] Die effektive Spec-Menge eines Consumers ist die Vereinigung seines lokalen Baums und jeder geerbten `portfolio`-Scope-Spec bei jedem gepinnten `ref`; eine Suche löst Local-First vorbehaltlich der Konfliktregeln auf.
- [ ] Eine lokale Spec, die einen logischen Key mit einer geerbten `portfolio`-Scope-Spec **ohne** deklarierten Override teilt, erzeugt ein `Critical`-Finding und einen Nicht-Null-CI-Exit.
- [ ] Ein deklarierter `overrides:`-Record löst als Abschnitts-Ersatz auf: überschriebene Abschnitte kommen aus der `local`-Datei des Consumers, alle anderen Abschnitte aus dem geerbten Kanon, und die `local`-Datei enthält nur die überschriebenen Abschnitte.
- [ ] Ein `overrides:`-Record, der einen Abschnitt mit einem `[locked]`-Requirement adressiert, erzeugt ein `Critical`-Finding; ein Consumer, der ein strengeres, nicht-widersprechendes lokales MUST neben einer gesperrten Invariante hinzufügt, nicht.
- [ ] Jeder `overrides:`-Record trägt einen nicht-leeren `reason`; ein leerer oder fehlender `reason` erzeugt ein `Warning`.
- [ ] Jede `inherits:`-Source trägt einen tag-gepinnten `ref`; ein gleitender oder fehlender `ref` erzeugt ein `Warning`.
- [ ] Eine Cross-Reference, deren logischer Key in keiner Menge auflöst, oder auf eine Spec ohne die referenzierte `§Section`, wird `Critical` per `spec/project/spec-readiness/` gekennzeichnet; ein Key, der in beiden Mengen ohne deklarierten Override auflöst, wird `Critical` gekennzeichnet (Duplicate-Key-Kollision).
- [ ] Ein `de`-kanonischer (oder anderweitig nicht-hub-kanonischer) Consumer erbt den Hub-Kanon als Quelle der Wahrheit; keine zweite autoritative Kopie in der Sprache des Consumers existiert, und der Drift-Check vergleicht canonical-to-canonical.
- [ ] Keine geerbte Spec wird per Submodule, Subtree, Vendoring oder Symlink verteilt; die vererbbare Teilmenge wird mit dem Plugin ausgeliefert und der Consumer referenziert sie per gepinntem `ref`; jede getrackte wortgleiche Kopie geerbten Inhalts in `spec/` ist ein `Critical`-Finding.
- [ ] Vererbung ist flach und verwurzelt: die `spec/.spec-config.yml` des Hubs trägt keinen `inherits:`-Key, eine geerbte Spec wird nicht gegen eine weitere Quelle neu aufgelöst, und eine zyklische Deklaration ist ein `Critical`-Finding.
- [ ] Der Drift-Check des `spec`-Skills erhält einen Local-vs-Inherited-Pass, der gegen den gepinnten `ref` läuft, die §"Drift-Detection"-Findings emittiert und bei jedem offenen `Critical` mit Nicht-Null-Exit endet.
- [ ] Ein `spec-drift-audit`-Lauf meldet die Vererbungs-Drift-Finding-Klasse (die Local-vs-Inherited-Findings) bei den in §"Audit- und CI-Integration" gemappten Severities, neben seinen Spec-gegen-Implementierung-Findings.
- [ ] Für einen nicht-hub-kanonischen Consumer wird die consumer-sprachige Sicht der geerbten Specs über den Canonical→Translation-Flow des `spec`-Skills erzeugt und ist nie das Ziel, gegen das der Drift-Check vergleicht.
- [ ] Ein `ref`-Bump auf einer `inherits:`-Source wird als per-Consumer-Update-PR durch die Renovate-artige Update-Automatisierung des Portfolios (oder einen äquivalenten konfigurierten Update-Kanal) sichtbar gemacht.
- [ ] Kein Repository im Portfolio behält für denselben logischen Key sowohl eine getrackte Kopie als auch eine `inherits:`-Referenz (der Reference-not-Copy-Endzustand, vom lokalen Working-Tree verifizierbar); die `nolte/claude-home-assistant#14`-Migration ist der durchgearbeitete Fall, zur PR-Zeit gegen §"Copy→Reference-Migrationspfad" verifiziert.
- [ ] Die `.spec-config.yml`-Schema-Erweiterung und die `spec`-Skill-Drift-Check-Erweiterung werden geliefert und `task test` besteht.

## Open Questions

- **Transitive / Mehr-Sprung-Vererbung.** Diese Revision deckelt Vererbung bei einem Hub + einem Consumer und behandelt einen Consumer-der-auch-Hub-ist als außerhalb des Scopes. Tritt ein echter Bedarf für eine zweite Schicht auf, muss die Auflösungsregel eine deterministische, monotone Linearisierung (C3-artig) werden, bevor Tiefe erlaubt wird, und eine `root: true`-artige Stopp-Grenze muss für jede Schicht definiert werden – dann revisitieren, nicht präventiv.
- **Granularität unterhalb des Abschnitts.** Die Override-Granularität ist der Abschnitt. Müssen Consumer wiederholt ein einzelnes Requirement innerhalb eines großen Abschnitts ändern und erweist sich der Ganz-Abschnitt-Ersatz in der Praxis als zu grob, kann eine künftige Revision ein Requirement-ID-Adressierungsschema plus eine benannte Additive-Merge-Direktive hinzufügen (für die die deklarierte Tief-Merge-Ausnahme §"Override-Granularität und Merge-Tiefe" Raum lässt). Verschoben, bis das grobe Modell nachweislich beißt.
- **Residuale Packaging-Mechanik.** §"Tooling und Durchsetzung" legt den Resolver-Einstiegspunkt auf `${CLAUDE_PLUGIN_ROOT}/spec/` fest; die residuale Wahl, ob die Plugin-Payload nur `Portfolio-Scope: portfolio`-Dateien oder den ganzen, zur Auflösungszeit gefilterten `spec/`-Baum trägt, ist ein Parking-Lot-Detail, das der Tooling-Schritt und `spec/project/release-automation/` klären, ohne Bezug auf den Vererbungs-Vertrag selbst.

## References

Externe Best-Practice-Quellen, die das Precedence- und Distributions-Modell begründen. Die vollständige zitierte Recherche, mit Verifikations-Verdikten je Behauptung, liegt unter `.resume/portfolio-inherited-spec-layer/research-report.md` (gitignoriertes Arbeitsartefakt); die tragenden externen Verhaltensweisen werden hier sichtbar gemacht, sodass sie ohne sie verifizierbar sind.

- Probot Settings `_extends` — referenziert eine zentrale Config in einem anderen Repo, lässt aber dessen Default-Branch gleiten, ohne Tag-Pinning: <https://github.com/probot/settings>, <https://github.com/probot/octokit-plugin-config>
- Renovate-Shareable-Presets und Tag-Pinning (`extends`, `github>owner/repo#tag`) — das Pin-and-Bump-Modell, das diese Spec spiegelt: <https://docs.renovatebot.com/config-presets/>, <https://docs.renovatebot.com/dependency-pinning/>
- AWS-IAM-Policy-Evaluation — Explicit-Deny-Wins und SCP-Org-Level-Guardrails, das Modell für den portfolio-gesperrten Invarianten-Tier: <https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic_policy-eval-denyallow.html>
- OPA/Rego — eine Complete-Rule-Kollision löst einen harten `eval_conflict_error` statt eines stillen Gewinners aus, das Modell für „undeklarierte Divergenz scheitert laut": <https://www.openpolicyagent.org/docs/policy-language/>
- TypeScript-`tsconfig`-`extends` — Last-Defined gewinnt und Arrays werden wortgleich ersetzt, der Merge-Tiefe-Präzedenzfall: <https://www.typescriptlang.org/tsconfig/extends.html>
- npm-Package-Locks — Pin + Lockfile mit regenerierbarem installiertem Cache, das Distributions-Modell: <https://docs.npmjs.com/cli/v6/configuring-npm/package-locks/>
- Git-Submodules — dokumentierte Clone-/Pull-/CI-/GC-Reibung hinter der Submodule-Ablehnung: <https://git-scm.com/book/en/v2/Git-Tools-Submodules>
- cruft — Template-Drift-Detection über einen gepinnten Commit plus eine explizite Skip-List, die hier übernommene Drift-Detection-Idee (seine Copy-Distribution nicht): <https://github.com/cruft/cruft>
- JSON-Schema-`$ref`/`$id` — Kombinierte-Namespace-Auflösung, bei der ein Duplicate-`$id` ein Fehler ist, kein stilles Last-Wins: <https://www.learnjsonschema.com/2020-12/core/ref/>
- CSS-Cascade-Layers — ein expliziter Base-Guard-Tier, den eine lokale Schicht nicht beiläufig überschreiben kann, das Cascade-Analogon des gesperrten Tiers: <https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_cascade/Cascade>
