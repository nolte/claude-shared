# Drittanbieter-Skills im Frontend-Audit

Status: draft

## Kontext

Die eigenen Frontend-Reviews des Plugins (`spec/frontend/source-code-review/` mit seinem F1–F11-Overlay und `spec/frontend/webview-ui-optimization/` mit seinen fünf Domänen) werden in diesem Repository geschrieben und gepflegt. Für ein ausführliches Audit reicht das allein nicht: Gepflegte Skill-Sammlungen von Drittanbietern kodieren bereits große, kuratierte Regelwerke für dieselbe Oberfläche. Vercels Web Interface Guidelines umfassen mehr als hundert UI-Regeln, Vercels React Best Practices ordnen rund siebzig Performance-Regeln nach Wirkung, Anthropics Skill `frontend-design` benennt die visuellen Merkmale schablonenhaften, generierten Designs, und Microsofts `playwright-cli` steuert einen echten Browser, sodass ein Audit die gerenderte Seite ansehen kann, statt sie aus dem Quelltext zu erschließen.

Diese Spec macht diese Drittanbieter-Skills zum **Kern** eines ausführlichen Frontend-Audits und lässt die eigenen Reviewer des Plugins mit ihren vollständigen Regelsätzen daneben laufen: Die Drittanbieter-Skills fügen ihre Befunde hinzu, und wo beide denselben Defekt finden, zeigt der Report ihn einmal mit beiden Quellen. Sie legt je Skill fest, **wann** er läuft und **was erfüllt sein muss**, bevor er laufen kann, und sie regelt, wie seine Befunde in einen gemeinsamen, attribuierten Report eingehen.

Der Inhalt stammt aus einer Anforderungserhebung vom 2026-11-17 (`project/requirements/frontend-audit-rework.md`; dieses Artefakt nummeriert seine eigenen Anforderungen R1–R15, das sind nicht die Referenzen `[R1]`–`[R5]` dieser Spec) und aus einer Untersuchung der vier Skills am selben Tag. Wo ein Fakt lokal beobachtet wurde, ist die Beobachtung genannt; wo er nur auf einem Upstream-README beruht, sagt die Referenz das.

Abgrenzung: Die eigenen Review-Dimensionen gehören weiterhin `spec/frontend/source-code-review/` und `spec/frontend/webview-ui-optimization/`; diese Spec ändert ihre Regeln nicht. Das Patchen von Befunden bleibt bei `webview-ui-optimize` und den Spezialisten, an die die Reports routen. Der Testidentifikator-Vertrag (`spec/frontend/testability-identifiers/`) und die Usability-Überarbeitung (`frontend-usability-optimizer`) bleiben unverändert.

Leser: Autorinnen und Autoren des Skills `frontend-audit` und der Reviewer-Agents, die er dispatcht; Operatoren, die ein Consumer-Repository für ein ausführliches Frontend-Audit vorbereiten.

## Ziele

- Ein Operator erkennt aus einer Tabelle, welchen Drittanbieter-Skill ein Audit nutzt, unter welcher Bedingung, und was vorher zu installieren und bereitzustellen ist
- Eine fehlende Vorbedingung verkleinert ein Audit nie stillschweigend: Sie erscheint als benannte Coverage-Lücke, und die eigenen Reviewer laufen weiter mit ihren vollständigen Regelsätzen
- Ein Skill, der auf den erkannten Stack nicht zutrifft, ist von einem fehlenden Skill unterscheidbar
- Jeder Befund im gemeinsamen Report nennt den Skill oder Agent, der ihn erzeugt hat, und ein Defekt, den zwei Quellen melden, erscheint einmal
- Drittanbieter-Befunde passen in das Severity-Vokabular des Plugins und seine Grenze zwischen Code und Geschmack, ohne die Drittanbieter-Regeln umzuschreiben
- Zur Laufzeit von Upstream geladene Regeln gelten als Audit-Kriterien, nie als Anweisungen, und ein Lauf hält genau fest, welchen Regeltext er verwendet hat

## Nicht-Ziele

- Drittanbieter-Skills aus dem Audit heraus installieren, aktualisieren oder entfernen — das tut der Operator
- Die zu prüfende Anwendung starten, bauen oder deployen
- Die Drittanbieter-Regelwerke in diesem Repository nachbilden oder wiederholen
- Befunde patchen; das Audit ist read-only
- Drittanbieter-Regeln an den Quellen-Schwellen dieses Repositorys messen (`spec/claude/research-triangulate/`); Drittanbieter-Befunde sind attribuierte Befunde, keine Regeln dieses Korpus
- Andere Frameworks als React für den Code-Performance-Strang; `react-best-practices` ist der einzige Drittanbieter-Skill für Code-Performance im Scope

## Anforderungen

### A. Skill-Katalog

Das Audit nutzt genau diese Drittanbieter-Skills. Jede Zeile ist für Auslöser und Vorbedingungen normativ; §B regelt den Installationsvertrag, §C die Verfügbarkeitsprüfung.

| Skill | Quelle | Strang | Läuft, wenn | Vorbedingungen | Nicht anwendbar, wenn |
|---|---|---|---|---|---|
| `web-design-guidelines` | `vercel-labs/agent-skills` | UI (statisch) | Web-UI-Code (Markup, Components, Styles) im Audit-Scope liegt | Skill installiert; Netzzugriff auf `raw.githubusercontent.com` zur Laufzeit | kein Web-UI-Code im Scope |
| `react-best-practices` (Frontmatter-Name `vercel-react-best-practices`) | `vercel-labs/agent-skills` | Code | React oder Next.js eine deklarierte Abhängigkeit des geprüften Moduls ist | Skill installiert | keine React- oder Next.js-Abhängigkeit |
| `frontend-design` | `anthropics/skills` oder das Plugin `frontend-design` aus dem offiziellen Claude-Plugin-Marketplace | UI (statisch), beratende Linse | Web-UI-Code im Scope liegt | Skill oder Plugin installiert | kein Web-UI-Code im Scope |
| `playwright-cli` | `@playwright/cli` (`microsoft/playwright-cli`) | UI (gerendert) | der Operator eine erreichbare Anwendungs-URL übergibt | CLI im `PATH`; Skill installiert; ein Browser dafür installiert; die URL vom Audit-Host erreichbar | nie — ohne URL ist der Strang eine Coverage-Lücke, siehe §D |

- **MUSS** die Anwendbarkeit aus den eigenen Manifesten und Quellen des geprüften Moduls ableiten (Paketmanifest, Framework- und Bundler-Konfiguration, Component-Baum), mit derselben Erkennung, die `source-code-review` für eine Browser-Oberfläche nutzt; ein `package.json` allein ist keine Web-UI
- **MUSS** jeden anwendbaren, verfügbaren Skill genau einmal je Audit über den Audit-Scope ausführen
- **DARF NICHT** einen Skill außerhalb seines Strangs ausführen: `react-best-practices`-Befunde gehören zum Code-Strang, `web-design-guidelines`- und `frontend-design`-Befunde zum statischen UI-Strang, `playwright-cli`-Evidenz zum gerenderten UI-Strang
- **MUSS** die serverseitigen Regelkategorien von `react-best-practices` (serverseitige Performance, React Server Components, Server Actions) als nicht anwendbar behandeln, wenn das Modul eine clientseitig gerenderte Anwendung ohne Server-Runtime ausliefert, Befunde dieser Kategorien streichen — Regel-IDs mit dem Präfix `server-` und jeden Befund zu React Server Components oder Server Actions — und die Zahl der gestrichenen Befunde im Report-Header festhalten

### B. Installationsvertrag

- **MUSS** die Installation dem Operator überlassen; der Skill `frontend-audit` **DARF NICHT** `npx skills add`, `npx skills update`, `playwright-cli install`, `playwright-cli install-browser` oder irgendeine Paketmanager-Installation ausführen
- **MUSS** jede Drittanbieter-Skill-Installation auf einen Tag oder vollständigen Commit pinnen, nie auf einen beweglichen Branch:
  - `npx skills add vercel-labs/agent-skills@<ref> --skill web-design-guidelines -a claude-code`
  - `npx skills add vercel-labs/agent-skills@<ref> --skill react-best-practices -a claude-code`
  - `npx skills add anthropics/skills@<ref> --skill frontend-design -a claude-code`, sofern nicht stattdessen das Plugin `frontend-design` installiert ist
  - `npm install -g @playwright/cli@<version>`, danach `playwright-cli install --skills` und `playwright-cli install-browser`
- Das Plugin `frontend-design` aus dem offiziellen Claude-Plugin-Marketplace ist von der Pin-Regel ausgenommen: Eine Marketplace-Installation ist durch ihre Plugin-Version bestimmt, und der Report-Header **MUSS** diese Version festhalten (§H)
- **SOLLTE** projektbezogen installieren (in das `.claude/skills/` des Repositorys; das `skills`-CLI kann die Dateien unter `.agents/skills/<skill>/` ablegen und `.claude/skills/<skill>` dorthin verlinken, beobachtet in einem Repository am 2026-11-18) und die vom `skills`-CLI geschriebene `skills-lock.json` committen, damit jeder Operator des Repositorys mit demselben Skill-Commit auditiert [R1]
- **KANN** die installierten Skill-Dateien selbst (den Ordner, den das CLI geschrieben hat, und, wo es verlinkt, den Link) in das Consumer-Repository committen; ein Repository, das das tut, verbreitet Drittanbieter-Text weiter, und sein Operator **MUSS** vorher die Lizenz jedes committeten Skills prüfen. Diese Spec erteilt keine Lizenz und verbürgt sich für keine. Beobachtet am 2026-11-18 über die GitHub-API (`repos/<owner>/<repo>` und `repos/<owner>/<repo>/license`): `vercel-labs/agent-skills` meldet keine Lizenz und hat keine Lizenzdatei, sein README nennt MIT; `anthropics/skills` meldet im Repository-Wurzelverzeichnis keine Lizenz, und `skills/frontend-design/` trägt eine eigene `LICENSE.txt`; `vercel-labs/web-interface-guidelines` meldet MIT mit Lizenzdatei; `microsoft/playwright-cli` meldet Apache-2.0 mit Lizenzdatei
- **KANN** benutzerbezogen installieren (`-g`), wenn ein Repository keine Drittanbieter-Skills tragen darf; das Audit kann dann nicht belegen, welcher Commit lief, und **MUSS** das im Report sagen
- Die Tool-Versionen in diesem Absatz sind Vorbedingungen, keine Pins: Das `skills`-CLI braucht Node.js 22.20 oder neuer [R1]; `@playwright/cli` braucht Node.js 20 oder neuer [R3]. `playwright-cli install --skills` installiert den Skill nach `<cwd>/.claude/skills/playwright-cli` (`--skills=agents` nach `.agents/skills/`, `-g` ins Home-Verzeichnis) und installiert keinen Browser — das tut `playwright-cli install-browser` (belegt: `@playwright/cli` 0.1.24, `playwright-cli install --help` und das `skillCheck.js` des Pakets)

### C. Verfügbarkeitsprüfung

- **MUSS** die Verfügbarkeit jedes anwendbaren Skills prüfen, bevor irgendein Strang läuft, und das Ergebnis je Skill als `available`, `missing` oder `not applicable` festhalten
- **MUSS** jeden Skill unter dem Namen suchen, unter dem die Session ihn listet, also seinem Frontmatter-`name`, nicht seinem Installationsordner: `web-design-guidelines`, `vercel-react-best-practices` (installiert mit `--skill react-best-practices`), `frontend-design` oder der Plugin-Skill `frontend-design:frontend-design` sowie `playwright-cli`
- **MUSS** einen Skill als verfügbar zählen, wenn die Session ihn listet — projektbezogen, benutzerbezogen oder als Plugin-Skill — und **SOLLTE** zusätzlich den Installationsort des Skills festhalten sowie bei Projektinstallationen den Commit aus `skills-lock.json`, wenn der Lock einen festhält
- **MUSS** für `web-design-guidelines`, `vercel-react-best-practices` und ein `frontend-design`, das nicht das Marketplace-Plugin ist, eine Lock-Prüfung ausführen. Ein Skill besteht sie, wenn die `skills-lock.json` des geprüften Repositorys einen Eintrag unter dem Namen enthält, unter dem die Session ihn listet, die `source` dieses Eintrags das Repository ist, das §A für den Skill nennt, ein Ordner dieses Namens im Projekt-Skill-Ordner des Repositorys existiert (`.claude/skills/<name>`, auch als Link nach `.agents/skills/<name>`) und kein Skill desselben Namens im Skill-Ordner des Benutzers existiert (`~/.claude/skills/<name>`). Ein Skill, der die Prüfung nicht besteht — was jede benutzerbezogene Installation einschließt —, **MUSS** im Report-Header als Warning zum Audit-Setup erscheinen und läuft erst, nachdem der Operator ihn bestätigt hat, bevor dieser Skill läuft; ein Skill, den der Operator nicht bestätigt, läuft nicht und ist eine Coverage-Lücke (§D)
- Die Lock-Prüfung ist eine Plausibilitätsprüfung, kein Beleg. Ein Lock-Eintrag hält die Upstream-`source`, ihren `sourceType`, den Upstream-Pfad, einen Inhalts-Hash (`computedHash`) und in Lock-Version 2 einen `commit` fest; einen Installationsort hält er nicht fest (belegt: Lock-Dateien der Versionen 1 und 2, vom `skills`-CLI in drei Repositorys geschrieben, gelesen am 2026-11-18). Ein an Ort und Stelle im selben Ordner ersetzter Skill besteht die Prüfung daher, ebenso ein Repository, das Skill und Lock gemeinsam ändert. Die Session listet Skills nach Namen ohne Pfad, und welchen von zwei gleichnamigen Skills sie lädt, ist hier nicht belegt (eine Session mit einem projektbezogenen und einem benutzerbezogenen Skill gleichen Namens würde es klären); deshalb besteht ein gleichnamiger benutzerbezogener Skill die Prüfung nicht
- **MUSS** für `playwright-cli` zusätzlich prüfen, dass das CLI läuft (`playwright-cli --version`), und dessen Version festhalten; eine CLI-Warnung, dass der installierte Skill nicht zur Tool-Version passt, **MUSS** im Report als Warning zum Audit-Setup erscheinen, nicht zum geprüften Code
- **DARF NICHT** eine erfolgreiche Prüfung als Beleg werten, dass ein Strang lief; der Report sagt je Strang, ob er lief, und wenn nicht, warum

### D. Coverage-Lücken

- **MUSS** einen fehlenden anwendbaren Skill als **Coverage-Lücke** melden, mit dem Skill, dem Strang, den er abgedeckt hätte, und dem Installationsbefehl aus §B
- **MUSS** das Audit weiterlaufen lassen, wenn ein Skill fehlt; die Regelsätze der eigenen Reviewer hängen nicht davon ab, welche Drittanbieter-Skills gelaufen sind
- **MUSS** einen Skill, der die Lock-Prüfung (§C) nicht bestanden hat und den der Operator nicht bestätigt hat, als Coverage-Lücke melden, deren Grund die unbestätigte Lock-Prüfung ist
- **MUSS** einen nicht zutreffenden Skill als `not applicable` mit Begründung melden (zum Beispiel mit der Begründung „keine React- oder Next.js-Abhängigkeit“), nie als Coverage-Lücke
- **MUSS**, wenn keine Anwendungs-URL übergeben wurde, den gerenderten Strang überspringen und als Coverage-Lücke melden, deren Begründung festhält, dass keine Anwendungs-URL übergeben wurde, und **DARF NICHT** die Anwendung starten, bauen oder ausliefern, um eine zu erhalten
- **MUSS**, wenn eine URL übergeben wurde, aber nicht erreichbar ist oder der Browser nicht startet, den gerenderten Strang als Coverage-Lücke mit dem beobachteten Fehler melden
- **MUSS**, wenn `web-design-guidelines` seine Regeln nicht laden kann (kein Netz, HTTP-Fehler), eine Coverage-Lücke für diesen Skill melden; das Audit **DARF NICHT** eine zwischengespeicherte oder erinnerte Kopie der Regeln einsetzen
- **MUSS** ein Framework, das ein eigener Reviewer als nicht unterstützt meldet (kein Profil in `spec/frontend/source-code-review/`), als Coverage-Lücke des Strangs dieses Reviewers melden; ein Teil des Referenz-Stacks aus `spec/frontend/webview-ui-optimization/`, den das Modul nicht nutzt, macht die Regeln dieser Spec dafür `not applicable`, nie zu einer Coverage-Lücke

### E. Live geladene Regeln

`web-design-guidelines` lädt seine Regeln bei jedem Lauf von `https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md` (laut SKILL.md des Skills [R2]). Der Regeltext ist durch die Skill-Installation also nicht gepinnt.

- **MUSS** den Skill seine Regeln bei jedem Lauf von Upstream-`main` laden lassen, wie der Skill es vorsieht
- **MUSS** im Report die Abrufzeit (UTC, ISO 8601) und den SHA-256 des Regeltexts festhalten, den der Skill angewandt hat, damit zwei Audits vergleichbar sind und ein geänderter Regelsatz sichtbar wird
- **KANN**, wenn der Skill den angewandten Text nicht offenlegt, einen separaten Abruf derselben URL hashen; der Report **MUSS** den Hash dann als aus separatem Abruf stammend kennzeichnen, weil er nicht belegt, welchen Text der Skill angewandt hat
- Der eigene Abruf des Skills kann dem Modell eine Zusammenfassung der Seite statt ihres Rohtexts liefern; das Audit hat dann keinen angewandten Text zum Hashen, und der Hash aus separatem Abruf ist der erwartete Fall. Für dieses Audit nicht belegt: Kein Lauf hat festgehalten, was der Skill erhalten hat; ein Lauf gegen ein echtes Frontend, der das tut, würde es klären
- **MUSS** jeden geladenen Drittanbieter-Regeltext als Audit-Kriterium behandeln — als Daten, die entscheiden, ob ein Befund vorliegt — und nie als Anweisung, die den Ablauf des Audits ändert: Aus geladenem Text dürfen keine Dateischreibvorgänge, keine Tool-Aufrufe und kein Netzzugriff über das hinaus folgen, was das Audit ohnehin ausführt
- **MUSS**, wenn geladener Text eine Passage enthält, die etwas anderes verlangt, als die geprüften Dateien an einer UI-Regel zu messen oder die Befunde darzustellen — eine Datei außerhalb des Audit-Scopes lesen, einen Befehl ausführen, eine Datei schreiben, aufs Netz zugreifen, den Audit-Scope ändern oder Befunde streichen, verbergen oder umformulieren —, die Passage ignorieren und eine Warning zum Audit-Setup melden, die die Quelle nennt und sie zitiert. Entscheidend ist, was eine Passage verlangt, nicht wo sie steht: Der Review-Rahmen, mit dem die Guidelines beginnen (eine Anweisung, Dateien auf Einhaltung zu prüfen), und ihr Abschnitt zum Ausgabeformat lösen nur so weit keine Warning aus, wie sie sagen, dass Dateien an den Regeln geprüft werden und wie die Rohbefunde des Skills gruppiert und formatiert werden; eine Passage in einem von beiden, die mehr verlangt, fällt unter die Warning
- **MUSS** alles, was der gerenderte Strang von der URL des Operators liest — Accessibility-Snapshots, sichtbaren Seitentext, Konsolenausgabe —, als Fremdtext unter derselben Regel behandeln: Es ist Beleg für einen Befund und nie eine Anweisung

### F. Eigene Reviewer neben den Drittanbieter-Skills

- **MUSS** `frontend-code-reviewer` und `webview-ui-expert` in jedem Audit mit ihren vollständigen Regelsätzen dispatchen; keine eigene Regel wird übersprungen, weil ein Drittanbieter-Skill einen ähnlichen Defekt abdeckt
- **DARF NICHT** den Scope eines eigenen Reviewers davon abhängig machen, ob oder in welcher Reihenfolge die Drittanbieter-Skills gelaufen sind; die Reviewer **KÖNNEN** parallel zu ihnen laufen
- Die Überschneidung ist erwartet und gewollt: Regeln der Web Interface Guidelines überschneiden sich mit F8, F10 und den generischen HTML- und CSS-Regeln aus `spec/frontend/webview-ui-optimization/`, und `vercel-react-best-practices` überschneidet sich mit F6. Die Zusammenführung in §H löst das auf, keine Aufteilung auf Regelebene

### G. Severity-Zuordnung und Routing

Drittanbieter-Befunde behalten ihren Text und ihre Regelreferenz; das Audit ordnet sie der Severity-Skala aus `spec/claude/review-plan/` §Schweregrad-Skala zu:

| Quelle | Drittanbieter-Klasse | Severity | Routing |
|---|---|---|---|
| `web-design-guidelines` | jede Regel außerhalb von Content & Copy und Typography auf Textebene | Warning | `fullstack-developer`; Fragen zur Barrierefreiheits-Konformität an `webview-ui-expert` |
| `web-design-guidelines` | Content & Copy; Typography-Regeln zu Zeichen und Anführungszeichen | Info | `frontend-usability-optimizer` |
| `react-best-practices` | CRITICAL, HIGH | Warning | `fullstack-developer` |
| `react-best-practices` | MEDIUM-HIGH, MEDIUM | Suggestion | `fullstack-developer` |
| `react-best-practices` | LOW-MEDIUM, LOW | Info | `fullstack-developer` |
| `frontend-design` | jede | Info | `frontend-usability-optimizer` |
| `playwright-cli` | gerenderte Evidenz zu einem Befund | Severity des Befunds | Routing des Befunds |

- **DARF NICHT** einem Befund, dessen einzige Quelle ein Drittanbieter-Skill ist, Critical zuweisen; Critical bleibt den eigenen Severity-Floors vorbehalten (ein unbehandelter Fehlerpfad, eine aktive Injection-Senke), und ein zusammengeführter Befund behält das Critical eines eigenen Reviewers
- **MUSS** die Tooling-first-Regel aus `spec/project/source-code-review/` auf Drittanbieter-Befunde anwenden: Ein Defekt, den der konfigurierte Linter oder Type-Checker des Projekts bereits meldet, ist kein Befund. Das Audit entscheidet das aus der konfigurierten Regelmenge (Linter-Konfiguration und ihre aktivierten Plugins), ohne den Linter auszuführen; klärt die Konfiguration nicht, ob eine Regel den Defekt abdeckt, bleibt der Befund bestehen
- **MUSS** jeden geladenen Drittanbieter-Skill nur als Audit-Kriterium nutzen: Anleitungen in `frontend-design`, `vercel-react-best-practices` oder `web-design-guidelines`, Code zu gestalten, zu schreiben, zu refaktorieren oder zu korrigieren, führen nie zu einem Schreibvorgang im geprüften Repository
- **MUSS** die Grenze zwischen Code und Geschmack aus `spec/frontend/source-code-review/` §„Abgrenzung zum UX-Review“ einhalten: Als Info geroutete Copy- und Design-Befunde gelangen nie in ein Work-Package
- **MUSS** `playwright-cli` nur zum Sammeln von Evidenz nutzen — Accessibility-Snapshots, Screenshots, Konsolenfehler und das Ergebnis reiner Tastaturbedienung — und sie einem Befund anhängen; ein Befund, dessen einzige Evidenz ein gerenderter Eindruck ist, bleibt Info
- **MUSS** jede `playwright-cli`-Ausgabe — Snapshots, Screenshots, Traces — in das Laufverzeichnis unter `.audits/frontend-audit/evidence/<target-slug>/` (§H) lenken, über eine dort liegende CLI-Konfigurationsdatei, deren `outputDir` `.` ist (übergeben mit `--config`), oder über ein explizites `--filename`; das Standard-Ausgabeverzeichnis des CLI ist `.playwright-cli/` im Arbeitsverzeichnis, ein Schreibvorgang außerhalb des Reports (belegt: `@playwright/cli` 0.1.24 setzt `cliOutputDir = ".playwright-cli"` in `playwright-core/lib/coreBundle.js`; ein Testlauf am 2026-11-17 mit `open --config=<dir>/cli.config.json` schrieb Snapshot und Screenshot nur unterhalb von `<dir>`, wobei `outputDir` relativ zur Konfigurationsdatei aufgelöst wird)

### H. Gemeinsamer Report

- **MUSS** je Audit einen Report nach `.audits/frontend-audit/<target-slug>.md` und seine Evidenz in ein Laufverzeichnis `.audits/frontend-audit/evidence/<target-slug>/<run-id>/` schreiben; nur ein Lauf, der seinen Report schreibt, entfernt die anderen Laufverzeichnisse dieses Ziels, deren Lauf nicht noch in Arbeit ist, sodass ein früher endender Lauf den vorigen Report und seine Evidenz unangetastet lässt
- **MUSS** den Report mit einem Header eröffnen, der festhält: den Audit-Scope; das erkannte Framework; je Drittanbieter-Skill Verfügbarkeitsstatus, Installationsort, Commit oder Version (beim Plugin `frontend-design` dessen Plugin-Version), das Ergebnis der Lock-Prüfung (§C) und ob er lief; Abrufzeit und SHA-256 der live geladenen Regeln (§E); die Zahl gestrichener serverseitiger Befunde (§A); und jede Coverage-Lücke
- **MUSS** jeden Befund mit `source` taggen — dem Drittanbieter-Skill (zum Beispiel `vercel/web-design-guidelines`) oder dem eigenen Agent mit Regel-ID (zum Beispiel `nolte/frontend-code-reviewer F2`)
- **MUSS** Befunde, die zwei Quellen für denselben Defekt melden — derselbe Defekt an derselben Datei und Zeile —, zu einem Befund zusammenführen, der alle Quellen, die höhere Severity und jeden Umsetzungsvorschlag eines eigenen Reviewers trägt; verschiedene Defekte in einer Zeile, Befunde ohne Zeile und Befunde an verschiedenen Zeilen bleiben getrennt
- **MUSS** für Warning und höher aus jeder Quelle den Work-Package-Vertrag aus `spec/project/source-code-review/` einhalten (disjunkte Dateimengen, Routing-Ziele): Ein Befund in einer Datei, die ein bestehendes Package besitzt, tritt diesem Package bei, jeder andere eröffnet ein Package für seinen Component-Slice, und der Behebungstext eines Drittanbieter-Befunds dient als sein Umsetzungsvorschlag
- **DARF NICHT** Drittanbieter-Befunde in die `pass`-/`fail`-Regeltabelle von `webview-ui-optimize` einfließen lassen; diese Tabelle beurteilt nur die Regeln aus `spec/frontend/webview-ui-optimization/`

### I. Orchestrierung

- **MUSS** von einem Skill orchestriert werden, `frontend-audit`, im Plugin `nolte-engineering`; der Skill läuft in der Hauptsession, weil Drittanbieter-Skills und die URL-Entscheidung des Operators dort liegen
- **MUSS** die Drittanbieter-Skills über den Skill-Mechanismus der Session aufrufen und `playwright-cli` über sein CLI
- **MUSS** `frontend-code-reviewer` für die eigenen Regeln des Code-Strangs und `webview-ui-expert` für die eigenen Regeln des statischen UI-Strangs dispatchen, jeweils mit vollständigem Regelsatz (§F)
- **MUSS** gegenüber dem geprüften Repository read-only bleiben, abgesehen von der Report-Datei, ihrer Evidenz unter `.audits/frontend-audit/evidence/<target-slug>/` und dem Resume-Zustand des Laufs unter `.resume/frontend-audit/`
- `source-code-review` und `webview-ui-optimize` bleiben bestehen; beide **SOLLTEN** Operatoren für das ausführliche, durch Drittanbieter gestützte Audit auf `frontend-audit` verweisen

## Akzeptanzkriterien

- [ ] Die Spec nennt für jeden der vier Skills Auslöser, Vorbedingungen, Bedingung für Nicht-Anwendbarkeit und gepinnten Installationsbefehl
- [ ] Ein Audit auf einem React-Repository mit allen installierten Skills und erreichbarer URL meldet alle vier Skills als `available` und gelaufen und listet keine Coverage-Lücke
- [ ] Ein Audit ohne installiertes `vercel-react-best-practices` meldet eine Coverage-Lücke mit Installationsbefehl, und die Befunde der eigenen Reviewer sind dieselben wie mit installiertem Skill
- [ ] Ein Audit, dessen Abruf von `web-design-guidelines` scheitert, meldet eine Coverage-Lücke für diesen Skill und nutzt keine zwischengespeicherten Regeln
- [ ] Ein Audit auf einem Web-Frontend ohne React meldet `vercel-react-best-practices` als `not applicable`, nicht als Lücke
- [ ] Ein Audit ohne URL meldet den gerenderten Strang als Coverage-Lücke und startet keine Anwendung
- [ ] Der Report-Header hält Abrufzeit und SHA-256 des Web-Interface-Guidelines-Texts fest
- [ ] Eine geladene Passage, die mehr verlangt, als Dateien an einer Regel zu messen oder Befunde darzustellen, wird ignoriert und als Warning zum Audit-Setup gemeldet, egal wo sie steht; der Review-Rahmen und der Abschnitt zum Ausgabeformat der Guidelines lösen so weit keine aus, wie sie nur das tun
- [ ] Text, den der gerenderte Strang von der Seite oder ihrer Konsole liest, ändert nie den Ablauf des Audits
- [ ] Ein Skill, der die Lock-Prüfung nicht besteht, erscheint als Warning zum Audit-Setup im Header und läuft erst, nachdem der Operator ihn bestätigt hat; unbestätigt wird er als Coverage-Lücke gemeldet
- [ ] Ein Audit, das das Marketplace-Plugin `frontend-design` nutzt, hält die Plugin-Version im Header fest
- [ ] §B nennt den Operator als denjenigen, der die Lizenz jedes Skills prüft, bevor Skill-Dateien committet werden
- [ ] Jeder Befund trägt eine `source`; melden zwei Quellen dieselbe Datei und Zeile, erscheint das einmal mit beiden
- [ ] Kein Befund, dessen einzige Quelle ein Drittanbieter-Skill ist, trägt Critical; Copy- und Design-Befunde sind Info und liegen außerhalb der Work-Packages
- [ ] Beide eigenen Reviewer führen in jedem Audit ihre vollständigen Regelsätze aus, egal welche Drittanbieter-Skills gelaufen sind
- [ ] Der Skill `frontend-audit` führt keinen Installationsbefehl aus, und jede `playwright-cli`-Ausgabe landet unter `.audits/frontend-audit/evidence/<target-slug>/`

## Referenzen

- Quellen abgerufen am 2026-11-17.
- [R1] Vercel-`skills`-Kommandozeilenwerkzeug, README mit `docs/agents.md` und `docs/commands.md` (P): <https://github.com/vercel-labs/skills>
- [R2] Vercel Agent Skills, `skills/web-design-guidelines/SKILL.md` und `skills/react-best-practices/SKILL.md` (P): <https://github.com/vercel-labs/agent-skills>
- [R3] Microsoft-`playwright-cli`-README (P): <https://github.com/microsoft/playwright-cli>
- [R4] Vercel Web Interface Guidelines, `command.md` (P): <https://github.com/vercel-labs/web-interface-guidelines>
- [R5] anthropics/skills, `frontend-design` (P): <https://github.com/anthropics/skills>
- Frontend-Code-Review-Overlay und seine UX-Abgrenzung: `spec/frontend/source-code-review/`
- Web-View-UI-Regelwerk: `spec/frontend/webview-ui-optimization/`
- Kern-Review, Tooling-first-Regel und Work-Package-Vertrag: `spec/project/source-code-review/`
- Severity-Skala und Ablageort von Audit-Artefakten: `spec/claude/review-plan/`
- Anforderungen hinter dieser Spec: `project/requirements/frontend-audit-rework.md`

## Offene Fragen

- Soll das Audit optional anbieten, die Web Interface Guidelines von einem gepinnten Commit statt von `main` zu laden? Die Erhebung hat Live-Laden mit festgehaltenem Hash gewählt; ein gepinnter Modus würde zwei Audits reproduzierbar machen, bräuchte aber einen Weg, die Abruf-URL eines Drittanbieter-Skills zu steuern, den der Skill nicht anbietet
- Welcher Drittanbieter-Skill für Code-Performance deckt Vue, Svelte oder Angular ab, falls überhaupt einer? Bis einer benannt ist, erhalten diese Stacks keine Drittanbieter-Befunde zur Code-Performance
- Soll die Zusammenführung auch einen Defekt erfassen, der an verschiedenen Zeilen eines mehrzeiligen Elements oder ohne Zeile gemeldet wird? Die exakte Datei-und-Zeile-Regel hält die Zusammenführung deterministisch, lässt solche Doppelbefunde aber im Report; eine weitere Regel braucht eine definierte Zuordnung zwischen eigenen Regel-IDs und Drittanbieter-Kategorien, die der Revisit vom 2026-11-18 entfernt hat
- Wie kann das Audit zeigen, dass jeder eigene Reviewer seinen vollständigen Regelsatz angewandt hat? Der Revisit hat die Listen angewandter Regeln zusammen mit der Delegation entfernt; ohne sie sehen eine saubere und eine übersprungene Regel im Report gleich aus
- Welches `frontend-design` läuft, wenn ein Repository sowohl den Projekt-Skill als auch das Marketplace-Plugin trägt, und gilt die Lock-Prüfung dann? In einem untersuchten Repository war beides vorhanden; welchem die Session den Vorrang gibt, ist nicht belegt
- Kann die Lock-Prüfung die installierten Skill-Dateien mit dem `computedHash` des Locks vergleichen? Das würde einen an Ort und Stelle ersetzten Skill erkennen, aber wie das `skills`-CLI den Hash berechnet, ist nicht belegt; ein Blick in den Quelltext des CLI würde es klären
- Rechtfertigt `playwright-cli`-Evidenz, die Konfidenz eines statischen Befunds von suspected auf confirmed anzuheben? Die aktuelle Regel hängt Evidenz nur an; eine Bestätigungsregel braucht eine definierte Zuordnung von Evidenz zu Befund
