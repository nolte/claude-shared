# Portfolio-Management

Status: draft

## Kontext

Die GitHub-Organisation `nolte/*` umfasst eine wachsende Sammlung von Repositories, die benachbarte Probleme lösen — eine Home-Assistant-Integration hier, eine Python-Anwendung dort, ein gemeinsames Claude-Code-Plugin, eine Ansible-Rollen-Bibliothek, Vokabular-Kuratierung, Plumbing-Repositories. Jedes Repository deklariert **seinen eigenen** Zweck über `project/mission.md`, **seinen eigenen** Scope über `project/roadmap.md` und **seine eigene** interne Form über `project/project-structure/`. Was keine bestehende Spec beantwortet, ist **die Cross-Repository-Frage**: Welches Repository soll eine gegebene Capability besitzen, wo tragen zwei Repositories stillschweigend dieselbe Logik parallel, und welche Capabilities braucht das Portfolio, die aber niemand aktuell liefert?

Die nächstgelegenen bestehenden Kontrollen sind partiell: `continuous-improvement` setzt einen 3-Wiederholungs-Trigger für Claude-Agent-/Claude-Skill-Spezialisten-Lücken durch, `skill-vs-agent` §Portfolio-weite Konsistenz mandatiert die Plugin-Level-Promotion von Capabilities, die in drei oder mehr Konsumenten wiederkehren, und `project-structure` definiert die *Form*, die jedes Repository teilt. Keine dieser Specs adressiert allgemeine Capability-Allokation, Cross-Repository-Duplikat-Erkennung jenseits von Claude-Artefakten, oder die Existenz eines Portfolio-Inventars als gerendertes Dokumentations-Artefakt. Diese Spec füllt die Lücke.

Eine *Capability* in dieser Spec ist eine kohärente Wert-Einheit, die das Repository einer benannten Audience liefert — zum Beispiel „Pflanzenpflege-Tracking", „Home-Assistant-Integration", „wiederverwendbare Claude-Code-Skills und -Agents", „geteiltes GitHub-Actions-Plumbing", „Vale-Style-Vokabulare". Capabilities sind bewusst **grob granular**: Eine Capability ist ungefähr das, was man im ersten Absatz der README schreiben würde, nicht was in einen Funktions-Docstring gehört. Feinere Granularität (Module, Bibliotheken, einzelne Funktionen) ist Verantwortung der internen Struktur jedes Repositorys, nicht des Portfolio-Managements.

Leser: Maintainer von `nolte/*`-Repositories, der Claude-Code-Skill / -Agent, der den periodischen Portfolio-Audit ausführt, Beitragende, die abwägen, wo ein neues Feature landen soll.

## Ziele

- Jede Capability im Portfolio hat genau ein **Owner-Repository**, explizit deklariert und auffindbar aus einem einzigen, maschinell lesbaren Manifest pro Repository.
- Cross-Repository-Duplikat-Capabilities (zwei oder mehr Repositories tragen überlappende Logik) werden durch einen periodischen Audit erkannt und als Findings sichtbar gemacht, nicht stillschweigend toleriert.
- Portfolio-Lücken — Capabilities, die das Manifest eines Repositorys als Peer-Abhängigkeit referenziert, aber kein Portfolio-Mitglied-Repository tatsächlich bereitstellt, oder Capabilities, die eine andere Spec voraussetzt, die das Portfolio aber noch nicht liefert — werden vom selben Audit erkannt und an einen Remediation-Owner geroutet.
- Das aggregierte Portfolio-Inventar wird als Teil der `claude-shared`-Dokumentationsseite gerendert, automatisch aus den Per-Repository-Manifests generiert, niemals von Hand gepflegt.
- Allokations-Entscheidungen („Capability X gehört in Repository Y, weil Z") werden mit Begründung dokumentiert, sodass ein späterer Audit die Entscheidung re-evaluieren kann, ohne das ursprüngliche Reasoning neu entdecken zu müssen.
- Der Audit selbst integriert sich in `continuous-improvement` als eine weitere Audit-Quelle, sodass Portfolio-Findings durch dieselbe Triage- und Spezialisten-Dispatch-Schleife fließen wie Drift-, Workflow-Health- und Vokabular-Findings.

## Nicht-Ziele

- Definition der Implementierungs-Details einzelner Capabilities; *wie* eine Capability gebaut wird, gehört zum Owner-Repository, nicht zu dieser Spec.
- Migrations-Toolchain für die Konsolidierung doppelter Capabilities in einen einzigen Owner. Der Audit *identifiziert* das Duplikat; der menschlich getriebene Konsolidierungs-PR ist eigene Arbeit.
- Repository-interne Architektur; sobald eine Capability einem Repository zugewiesen ist, regeln dessen eigene `project-structure`-, `mission`-, `roadmap`- und `feature`-Specs die Form. Das Interesse dieser Spec endet an der Repository-Grenze.
- Roadmap-Priorisierung über das Portfolio hinweg; die Sequenzierung der Capability-Einführung ist Sache der `roadmap`- und `mission`-Specs jedes Repositorys, nicht dieser Spec.
- Cross-Repository-Runtime-Dependency-Tracking (welches Deployment welches Repositorys von welchem Release welches anderen Repositorys abhängt). Das ist ein Deployment- / Release-Pipeline-Anliegen, adressiert durch `release-automation` und eine eventuelle künftige Cross-Repo-Deployment-Spec.
- Governance der `nolte/*`-Organisation selbst (Mitgliederzugriff, Repo-Anlage-Rechte etc.). Diese Spec regelt *was* wo lebt, nicht *wer* entscheiden darf.

## Anforderungen

### Portfolio-Scope

- **MUSS [MUST]** das Portfolio als genau die Menge der öffentlichen, nicht-archivierten Repositories unter der `nolte`-GitHub-Organisation zum Zeitpunkt eines Portfolio-Audit-Laufs behandeln. Forks von Upstream-Repositories sind keine Portfolio-Mitglieder, es sei denn, die Eigentümerschaft wurde übertragen und die Upstream-Beziehung ist getrennt.
- **DARF [MAY]** ein einzelnes Repository explizit aus dem Portfolio-Scope ausschließen, indem `portfolio: excluded` zusammen mit einer einzeiligen Begründung am Anfang der `CLAUDE.md` gesetzt wird; Opt-out ist absichtlich und inspizierbar, niemals stillschweigend.
- **DARF NICHT [MUST NOT]** archivierte Repositories in das aktive Portfolio-Inventar aufnehmen. Archivierte Repositories **DÜRFEN [MAY]** in einem separaten „historische Capabilities"-Abschnitt des gerenderten Inventars erscheinen, mit dem Archivierungsdatum markiert, sodass Peer-Referenzen aus aktiven Repositories weiterhin auflösen.
- **MUSS [MUST]** Portfolio-Mitgliedschaft zur Audit-Zeit über die GitHub-API ermitteln (`gh api orgs/nolte/repos --paginate --jq '.[] | select(.archived==false and .private==false) | .name'`) statt aus einer von Hand gepflegten Liste, sodass das Hinzufügen eines neuen Repositorys zur Organisation es automatisch in den Scope zieht.

### Capability-Inventar pro Repository

- **MUSS [MUST]** von jedem Portfolio-Mitglied-Repository ein `project/portfolio.yml`-Manifest fordern, das die Capabilities des Repositorys, die bedienten Audiences und Peer-Referenzen auf andere Portfolio-Mitglied-Repositories deklariert.
- **MUSS [MUST]** jeden Capability-Eintrag mindestens mit folgenden Feldern strukturieren: `name` (kebab-case-Identifier, eindeutig innerhalb des Manifests), `description` (ein bis zwei Prosa-Sätze, die benennen, was die Capability tut und für wen), `audience` (eine Liste von Audience-Identifiern, kreuzreferenziert mit dem `project/audiences.md`-Artefakt des Projekts gemäß `audience-identification`), `status` (einer von `experimental`, `active`, `deprecated`) und `rationale` (ein bis zwei Sätze, die benennen, warum dieses Repository die Capability besitzt).
- **DARF [MAY]** optionale Felder pro Capability enthalten: `peers` (Liste von `<repo>:<capability-name>`-Referenzen auf Capabilities in anderen Portfolio-Mitglied-Repositories, von denen diese Capability abhängt oder mit denen sie koordiniert), `deprecated_in_favor_of` (bei `status: deprecated` eine `<repo>:<capability-name>`-Referenz auf den Ersatz) und `since` (ISO-Datum, wann die Capability erstmals im Repository auftrat).
- **MUSS [MUST]** Capability-`name`-Werte stabil halten; Umbenennungen sind explizite Entscheidungen, in der Git-Historie des Manifests nachverfolgt, und **MÜSSEN [MUST]** im selben Koordinations-Fenster mit Peer-Referenzen in anderen Portfolio-Mitglied-Repositories abgestimmt werden.
- **DARF NICHT [MUST NOT]** eine Capability deklarieren, die das Repository nicht tatsächlich in ausgeliefertem Code, Dokumentation oder Workflows liefert; der Audit verifiziert, dass jede deklarierte Capability mindestens ein entsprechendes Implementierungs-Artefakt (ein Code-Modul, eine Workflow-Datei, eine Doku-Seite oder eine Skill-/Agent-Datei) im Repository hat.

### Tech-Stack-Block

- **MUSS [MUST]** den Top-Level-Key `tech_stack:` in `project/portfolio.yml` vollständig von `spec/portfolio/tech-stack/` definiert ansehen; diese Spec definiert das Feldschema weder neu noch beschränkt sie dessen Sub-Blöcke. Ob der Key für ein gegebenes Portfolio-Mitglied verpflichtend oder weglassbar ist, entscheiden die Adoptionsregeln in der referenzierten Spec, nicht hier. Capability-Einträge und der `tech_stack:`-Block sind orthogonal: Capabilities beantworten *was* das Repository liefert, `tech_stack:` beantwortet *wie* es technisch gebaut ist.

### Cross-Repository-Duplikat-Erkennung

- **MUSS [MUST]** während jedes Audit-Laufs jede Capability über jedes Manifest jedes Portfolio-Mitglied-Repositorys hinweg vergleichen und jedes Paar von Capabilities, deren `description`-Statements semantisch überlappen (nicht nur Keyword-Überlappung), als **Duplikat-Kandidat** flaggen.
- **MUSS [MUST]** bei einem bestätigten Duplikat von den Maintainern entweder verlangen, die Capability in ein Owner-Repository zu konsolidieren (die anderen Repositories markieren `status: deprecated` mit `deprecated_in_favor_of: <owner>:<capability-name>`) oder im `rationale`-Feld beider Capabilities zu dokumentieren, warum die Duplikation tatsächlich notwendig ist (andere Audience, andere Laufzeit-Bedingung, andere Lizenzierung).
- **MUSS [MUST]** ein Toleranz-Fenster von **einem geschlossenen Sprint pro Repository** anwenden, bevor ein bestätigtes Duplikat ein `Critical`-Finding wird; der Audit-Lauf, der es identifiziert, produziert ein `Warning`-Grad-Finding, und der nächste Audit nach einem geschlossenen Sprint ohne Auflösung eskaliert die Schwere.
- **SOLLTE [SHOULD]** bei der Owner-Wahl in einer Konsolidierung das Repository bevorzugen, dessen bestehende `mission`- und `audience`-Artefakte am ehesten zur Audience der Capability passen; Gleichstände werden zugunsten des Repositorys aufgelöst, das bereits die meisten Peer-Cluster-Artefakte hostet (gemäß der `tags`-Cluster-Konvention aus `skill-management` und `agent-management`).
- **DARF NICHT [MUST NOT]** stillschweigend zwei `active`-Capabilities mit überlappender `description` in zwei verschiedenen Portfolio-Mitglied-Repositories über das Toleranz-Fenster hinaus belassen; der Audit behandelt das als `Critical`-Finding, geroutet durch die Triage-Schleife von `continuous-improvement`.

### Lücken-Analyse

- **MUSS [MUST]** während jedes Audit-Laufs drei Klassen von Portfolio-Lücken identifizieren:
  - **Gebrochene Peer-Referenz**: Eine Capability listet einen `peers:`-Eintrag, der auf ein `<repo>:<capability-name>` zeigt, das kein Portfolio-Mitglied-Repository tatsächlich deklariert (das referenzierte Repo oder die Capability existiert nicht).
  - **Spec-geforderte Lücke**: Eine andere Spec unter `spec/` deklariert eine Capability als Vorbedingung (zum Beispiel könnte eine künftige Spec verlangen „jedes nolte-Projekt liefert einen Release-Notes-Slack-Notifier") und kein Portfolio-Mitglied-Repository-Manifest deklariert diese Capability.
  - **Cross-Repository-Copy-Paste-Smell**: Wenn dieselbe benutzerdefinierte Workflow-Datei, der gleiche Konfigurations-Block oder das gleiche nicht-triviale Code-Pattern in drei oder mehr Portfolio-Mitglied-Repositories dupliziert ist, ohne dass eine entsprechende geteilte Capability in einem einzigen Portfolio-Mitglied-Repository existiert, ist das Pattern ein Kandidat für die Promotion zu einer geteilten Capability — analog zur 3-Wiederholungs-Regel in `skill-vs-agent` §Portfolio-weite Konsistenz, aber über Claude-Artefakte hinaus erweitert.
- **MUSS [MUST]** jede identifizierte Lücke an einen Remediation-Owner routen: Der Audit emittiert ein Finding, das die Lückenklasse, die betroffenen Repositories und die vorgeschlagene Remediation benennt (neue Capability in Repository X anlegen, bestehende Capability in Repository Y erweitern, gebrochene Peer-Referenz außer Dienst stellen etc.).
- **SOLLTE [SHOULD]** ein Tracking-Issue im relevantesten Portfolio-Mitglied-Repository öffnen für jede Lücke, die nicht innerhalb desselben Audit-Zyklus behoben werden kann; der Issue-Body **MUSS [MUST]** den Audit-Finding-Identifier zitieren, sodass die Schleife von beiden Seiten schließbar ist.

### Portfolio-Audit

- **MUSS [MUST]** als dedizierter Skill `portfolio-audit` im `nolte-shared`-Plugin implementiert sein (analog zu `dependency-audit`, `vocab-drift-audit`, `docs-freshness-checker`), gemäß `skill-management` autoriert und gemäß `skill-review` reviewt.
- **MUSS [MUST]** mindestens auf einer quartalsweisen Kadenz laufen und **MUSS [MUST]** auch on-demand vom Operator aufrufbar sein; der Kadenz-Trigger und der On-demand-Trigger produzieren dieselbe Artefakt-Form.
- **MUSS [MUST]** eine Findings-Report-Datei unter `.audits/portfolio/<YYYY-MM-DD>.md` im `claude-shared`-Repository produzieren, die der `review-plan`-Artefakt-Spezifikation entspricht, einschließlich der vier Pflicht-Abschnitte (`## Scope`, `## Summary`, `## Findings`, `## Processing log`) und des kanonischen Schweregrad-Vokabulars (`Critical` / `Warning` / `Suggestion` / `Info`) gemäß `review-plan` §Schweregrad-Skala.
- **MUSS [MUST]** Findings nach derselben Schweregrad-Skala klassifizieren wie jeder andere Audit im Portfolio: ein Duplikat über das Toleranz-Fenster hinaus ist `Critical`, ein frisches Duplikat oder eine gebrochene Peer-Referenz ist `Warning`, ein Copy-Paste-Smell oder eine Spec-geforderte Lücke unterhalb des 3-Wiederholungs-Schwellwerts ist `Suggestion`, eine Beobachtung, die noch keine Aktion verlangt, ist `Info`.
- **MUSS [MUST]** mit `continuous-improvement` als anerkannte Audit-Quelle integriert sein, indem er in der „Finding sources in scope"-Sektion jener Spec in einer künftigen Revision aufgeführt wird; Portfolio-Findings fließen durch dieselbe Triage-und-Spezialisten-Dispatch-Schleife wie `spec-drift-audit`- und `workflow-health`-Findings.
- **DARF NICHT [MUST NOT]** als Claude-Agent implementiert sein — der Audit ist eine mehrstufige Orchestrierung, die mid-flow User-Bestätigung bei Duplikat-Auflösungs-Entscheidungen einschließt, was die Skill-Seite der `skill-vs-agent`-Entscheidungsregel ist. Der Audit **DARF [MAY]** read-only-Spezialisten-Agents (zum Beispiel einen `manifest-parser`-Agent) für context-window-lastige Subtasks dispatchen.

### Dokumentations-Rendering

- **MUSS [MUST]** das aggregierte Portfolio-Inventar unter `docs/<canonical_language>/portfolio/` im `claude-shared`-Repository rendern, mit einer Übersetzung unter `docs/<other_language>/portfolio/` für jede konfigurierte Dokumentationssprache.
- **MUSS [MUST]** das gerenderte Inventar automatisch aus den Per-Repository-`project/portfolio.yml`-Manifests generieren; die gerenderten Dateien **DÜRFEN NICHT [MUST NOT]** von Hand bearbeitet werden, und ein CI-Check **MUSS [MUST]** verifizieren, dass die gerenderte Ausgabe dem entspricht, was der Generator produzieren würde.
- **MUSS [MUST]** das gerenderte Inventar mit einer Sektion pro Portfolio-Mitglied-Repository strukturieren, jede Sektion enthält: das Mission-Statement des Repositorys (zitiert aus `project/mission.md`), die Capability-Liste mit Status-Badges, die bedienten Audiences (kreuzreferenziert auf `audience-identification`) und eine Outbound-Peer-Referenz-Liste, die benennt, von welchen anderen Repositories dieses abhängt.
- **SOLLTE [SHOULD]** ein Mermaid-Diagramm enthalten, das das Capability-zu-Repository-Mapping und die Cross-Repository-Peer-Referenzen visualisiert (gemäß `mermaid-diagrams`-Portfolio-Spec), sodass die gesamte Portfolio-Struktur auf einen Blick sichtbar ist.
- **DARF [MAY]** einen „historische Capabilities"-Anhang enthalten, der Capabilities in archivierten Repositories mit ihrem Archivierungsdatum auflistet, sodass historische Peer-Referenzen weiterhin auflösbar bleiben.

### Entscheidungs-Dokumentation

- **MUSS [MUST]** auf jedem Capability-Eintrag ein nicht-leeres `rationale`-Feld tragen, das benennt, warum das Owner-Repository gewählt wurde; ein Ein-Satz-Rationale ist akzeptabel, ein leeres oder Template-Rationale ist ein `Warning`-Finding aus dem Audit.
- **SOLLTE [SHOULD]** jede tatsächlich umstrittene Allokations-Entscheidung als Architecture Decision Record unter `docs/adr/` im Owner-Repository festhalten, mit einem Backlink aus dem `rationale`-Feld der Capability; das hebt die wichtigsten Allokations-Entscheidungen in die Dokumentationsschicht, statt sie nur im Manifest zu belassen.
- **MUSS [MUST]** die Re-Allokation einer Capability von einem Repository zu einem anderen als koordinierte atomare Operation behandeln: Das neue Owner-Repository deklariert die Capability in seinem Manifest, das alte Owner-Repository setzt gleichzeitig `status: deprecated` mit `deprecated_in_favor_of`, das auf den neuen Owner zeigt, und beide Änderungen landen innerhalb desselben Koordinations-Fensters (höchstens ein geschlossener Sprint). Der Audit behandelt halbfertige Re-Allokationen als `Critical`-Findings.

## Abnahmekriterien

- [ ] Jedes nicht-archivierte öffentliche Repository in der `nolte`-GitHub-Organisation liefert entweder ein gültiges `project/portfolio.yml`-Manifest **oder** deklariert `portfolio: excluded` mit Begründung am Anfang der `CLAUDE.md`.
- [ ] Jedes `project/portfolio.yml` parst als gültiges YAML und enthält mindestens einen Capability-Eintrag mit den Pflicht-Feldern (`name`, `description`, `audience`, `status`, `rationale`).
- [ ] Keine zwei `active`-Capabilities in zwei verschiedenen Portfolio-Mitglied-Repositories teilen sich eine überlappende `description` jenseits des Ein-geschlossener-Sprint-Toleranz-Fensters; das Ausführen des Duplikat-Erkennungs-Checks über das Portfolio produziert null `Critical`-Findings.
- [ ] Jede `peers:`-Referenz in jedem Manifest löst auf eine Capability auf, die tatsächlich im Manifest des benannten Portfolio-Mitglied-Repositorys existiert; das Ausführen des Gebrochene-Peer-Referenz-Checks produziert null `Warning`-Findings.
- [ ] Der Skill `portfolio-audit` existiert unter `skills/portfolio-audit/SKILL.md` im `nolte-shared`-Plugin, entspricht `skill-management` und wurde mindestens einmal gegen `skill-review` reviewt mit dem resultierenden Plan geschlossen.
- [ ] Mindestens ein quartalsweiser Audit-Findings-Report existiert unter `.audits/portfolio/<YYYY-MM-DD>.md` im `claude-shared`-Repository, der der `review-plan`-Vier-Abschnitts-Struktur und dem kanonischen Schweregrad-Vokabular entspricht.
- [ ] Das aggregierte Portfolio-Inventar ist unter `docs/<canonical_language>/portfolio/` veröffentlicht und rendert korrekt via `task docs`; ein CI-Check verifiziert, dass die gerenderte Ausgabe dem entspricht, was die Re-Generierung aus den Manifests produzieren würde.
- [ ] `continuous-improvement` listet `portfolio-audit` als anerkannte Audit-Quelle in seiner „Finding sources in scope"-Sektion.
- [ ] Jede Capability in jedem Manifest hat ein nicht-leeres `rationale`-Feld; das Ausführen des Rationale-Anwesenheits-Checks produziert null `Warning`-Findings.
- [ ] Die `claude-shared`-`docs/<canonical_language>/portfolio/index.md` enthält ein Mermaid-Diagramm, das das Capability-zu-Repository-Mapping gemäß `mermaid-diagrams` visualisiert.

## Offene Fragen

- Sollte das Toleranz-Fenster für bestätigte Duplikate ein geschlossener Sprint pro Repository sein (aktueller Vorschlag) oder ein festes Kalender-Fenster (z. B. 30 Tage)? Die Sprint-basierte Toleranz skaliert mit der Repository-Aktivität, ist aber mechanisch schwerer durchzusetzen.
- Wie wird „Capability-Description-Überlappung" mechanisch vom Audit erkannt — semantische Embedding-Ähnlichkeit über einem Schwellwert, ein LLM-basierter Vergleichs-Pass oder ein leichtgewichtiges Keyword-Schnitt-Signal? Die Wahl beeinflusst Audit-Kosten, False-Positive-Rate und Reproduzierbarkeit.
- Sollte `project/portfolio.yml` aus `project/mission.md` und `project/roadmap.md` auto-generiert werden, wenn ein Repository die Spec erstmals adoptiert, oder immer von Grund auf von Hand autoriert? Auto-Generierung gibt einen Schnellstart, riskiert aber Drift gegenüber der tatsächlichen Capability-Menge.
- Wie interagiert diese Spec mit `mission` für Repositories, deren Mission selbst „eine geteilte Bibliothek / ein Plugin sein, das von anderen Portfolio-Mitglied-Repositories genutzt wird" ist (z. B. `nolte/claude-shared`, `nolte/vale-style`, `nolte/gh-plumbing`)? Die Capability-Liste in solchen Repositories tendiert dazu, aufzuzählen, was sie Konsumenten anbieten; der Audit sollte das nicht mit Eigentümerschaft an Konsumenten-seitigen Capabilities verwechseln.
- Sollte das gerenderte Portfolio-Inventar auch externe (nicht-`nolte/*`) Abhängigkeiten ausweisen, auf die Portfolio-Mitglied-Repositories sich stützen, oder strikt innerhalb der `nolte/*`-Grenze bleiben? Ein „externe Abhängigkeiten"-Anhang würde Supply-Chain-Sichtbarkeit fördern, erweitert aber den Scope des Audits.
- Was ist das exakte Promotionskriterium einer Capability von `experimental` zu `active`? Soll es an `mission`-MVP-Status, an einen Roadmap-Feinheit-Trigger gekoppelt sein oder dem Owner-Repository überlassen bleiben? Engere Kopplung an bestehende Specs vermeidet Reinvent-Lifecycle-Vokabular; lose Kopplung hält Experimentation günstig.
- Für Repositories, die legitim zwei verwandte Capabilities hosten (zum Beispiel liefert `nolte/claude-shared` sowohl wiederverwendbare Skills *als auch* wiederverwendbare Agents) — sollte das Manifest sie als eine Capability oder zwei behandeln? Das Duplikat-Erkennungs-Verhalten des Audits hängt von der Antwort ab.
- Sollte `portfolio-audit` auch Capabilities, deren `status` länger als ein definiertes Fenster (z. B. vier geschlossene Sprints) `experimental` ist, als Stagnations-`Suggestion` ausweisen, ähnlich der Detail-Level-Invariante, die `roadmap`-Items haben? Die Absicht wäre, indefinit-experimentellen Status als versteckte Form von Drift zu verhindern.
