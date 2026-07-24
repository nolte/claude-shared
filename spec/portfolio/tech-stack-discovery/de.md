# Portfolio-Tech-Stack-Discovery

Status: draft

## Context

Die Schwester-Spec `spec/portfolio/tech-stack/` definiert die **Form** des Portfolio-Tech-Stacks: ein globales Manifest unter `portfolio/tech-stack.yml`, einen pro-Repository-`tech_stack:`-Block in `project/portfolio.yml`, ein Eintragsschema, ein 12-Werte-`kind`-Enum, additive Vererbung mit expliziten `inherit: false`-Overrides und einen Audit-Integrationsvertrag. Diese Spec endet bewusst beim Schema und beim Audit; sie beantwortet drei orthogonale Fragen nicht, von denen die Tech-Stack-Erfassungsarbeit ebenfalls abhängt:

1. **Wie wird jeder Eintrag tatsächlich ermittelt** — welche Repository-Signale werden in welcher Reihenfolge mit welcher Nutzerinteraktion inspiziert, und wie unterscheidet der Ermittlungsfluss einen geerbten Eintrag von einer repo-spezifischen Addition?
2. **Wer konsumiert das resultierende Inventar** — welche Produzenten schreiben es, welche direkten Konsumenten handeln darauf, und welche indirekten Zielgruppen werden von ihm beeinflusst?
3. **Worin liegt der portfolioweite Nutzen** — warum lohnt sich ein zentral kuratiertes globales Stack-Manifest plus pro-Repo-Deltas trotz des Kurationsaufwands, und welche `project/goals.md`-Outcomes bedient es?

Diese Spec beantwortet diese drei Fragen normativ. Sie ist mit der Schema-Spec gekoppelt, so wie `spec/project/audience-identification/` mit nachgelagerten Specs gekoppelt ist, die ein Audience-Artefakt konsumieren: Das Schema ist der Vertrag, diese Spec ist die Methodik, und beide werden über wechselseitige Cross-References synchron gehalten.

Leser: der `claude-shared`-Maintainer, der `portfolio/tech-stack.yml` und den künftigen Capture-Skill schreibt; der Maintainer jedes Portfolio-Mitglied-Repositorys, das den `tech_stack:`-Block seiner `project/portfolio.yml` schreibt oder überarbeitet; der Implementierende des Capture-Skills (Claude Code als Ko-Autor); der `portfolio-audit`-Skill als automatisierter Konsumer der resultierenden Manifeste; Beitragende und Onboarding-Leser, die die gerenderte Portfolio-Doku konsultieren.

## Goals

- Eine reproduzierbare Ermittlungs-Methodik kodifizieren, sodass zwei Operatoren, die denselben Repository-Tech-Stack erfassen, bei derselben Eintragsmenge landen.
- Das Audience-Modell des Tech-Stack-Inventars explizit machen, mit einem Bullet pro Audience, das die berührte Oberfläche und die mitgebrachte Erwartung nennt.
- Die Vorteile eines portfolioweiten Stacks explizit und verlinkbar machen, sodass ein Maintainer den Kurationsaufwand mit einem wörtlichen Satz pro Vorteil im PR-Review oder bei der Sprint-Planung rechtfertigen kann.
- Die Schema-Spec (`spec/portfolio/tech-stack/`) frei von Methodik- und Audience-Prosa halten, sodass Schema-Änderungen keinen Methodik-PR erfordern und umgekehrt.

## Non-Goals

- Definition des Eintragsschemas, des `kind`-Enums, des Vererbungs-Vertrags oder der Audit-Severity-Tabelle — diese leben in `spec/portfolio/tech-stack/` und werden hier nicht wiederholt.
- Empfehlung konkreter Tools pro `kind` (MkDocs vs. `Docusaurus`, `uv` vs. poetry, etc.). Tool-Auswahl ist der Kurations-Entscheid des `claude-shared`-Maintainers beim Schreiben von `portfolio/tech-stack.yml`; diese Spec regelt den Pfad, der einen Eintrag in das Manifest bringt, nicht die Antwort darauf, welches Tool gewinnt.
- Schreiben des AUDIENCES-Artefakts für das `claude-shared`-Repository selbst — das ist die bereits via `audience-identification` produzierte `AUDIENCES.md`. Diese Spec konsumiert dieses Artefakt, sie ersetzt es nicht.
- Spezifikation, wie `portfolio-audit` ermittelte Einträge mechanisch gegen Repo-Signale verifiziert — die Signal-Klassen-Liste lebt in `spec/portfolio/tech-stack/` §Portfolio-Audit-Integration. Diese Spec regelt, wie ein Eintrag *erfasst* wird; die Schema-Spec regelt, wie er *geprüft* wird.
- Design der UX oder der Implementierungs-Details des Capture-Skills. Der Skill ist ein separates Artefakt, geschrieben gemäß `spec/claude/skill-management/`; diese Spec beschränkt nur den Ermittlungs-Fluss, den der Skill orchestriert.
- Sonderbehandlung von Portfolio-Anchor-Repositories (`nolte/gh-plumbing`, `nolte/vale-style`, `nolte/taskfiles`) während der Discovery. Der Discovery-Fluss läuft unverändert gegen ein Anchor-Repo und erfasst, wie der Anchor selbst gebaut ist. Was ein Anchor dem Portfolio *anbietet* (geteilte Workflows, Vokabulare, Taskfiles) ist eine `capabilities:`-Sache in `spec/portfolio/portfolio-management/`, orthogonal zur `tech_stack:`-Sache.

## Audiences

Das Tech-Stack-Inventar trägt drei Audience-Klassen. Jede Klasse ist mit der `AUDIENCES.md` des `claude-shared`-Repositories kreuzreferenziert, sodass eine Revision des einen Artefakts eine Sync-Prüfung am anderen auslöst.

### Producers

Producers schreiben Einträge — entweder direkt in `portfolio/tech-stack.yml` oder in den `tech_stack:`-Block eines Portfolio-Mitglieds via Capture-Skill.

- **`claude-shared`-Maintainer (Kurator des globalen Stacks).** Oberfläche: Hand-Edits an `portfolio/tech-stack.yml` in diesem Repository plus die Spec-Evolutionsautorität, die entscheidet, welche technischen Bausteine das Portfolio standardisiert. Erwartung: Edits sind reviewbar, Kind-Enum-Drift ist selten, und eine Promotion von `experimental` zu `active` folgt dem SOLLTE in `spec/portfolio/tech-stack/` §Vererbungs-Semantik. Kritikalität: primär. Mapping zu AUDIENCES.md → contributors / maintainers → `"Repo maintainer (nolte)"`.

- **Portfolio-Mitglied-Maintainer (Autor pro-Repo-Additions und -Overrides).** Oberfläche: der Capture-Skill, der im eigenen Repository läuft, plus direkte Hand-Edits an `project/portfolio.yml`. Erwartung: Discovery schlägt aus Repo-Signalen einen vollständigen Entwurf vor, jeder vorgeschlagene Eintrag wird interaktiv bestätigt bevor irgendetwas geschrieben wird, und geerbte Einträge werden nicht stillschweigend als repo-spezifische Additions neu deklariert. Kritikalität: primär portfolioweit. Tech-Stack-spezifische Verfeinerung nicht in `AUDIENCES.md`: Diese Audience liegt außerhalb des `claude-shared`-Bounded-Context (gemäß AUDIENCES.md §Bounded context), ist aber der primäre Autor jedes pro-Repo-`tech_stack:`-Blocks, weshalb diese Spec sie explizit nennt.

- **Capture-Skill (Claude Code als Ko-Autor).** Oberfläche: Skill-Orchestrierung, die Repo-Signale absucht, Einträge entwirft, sie dem Maintainer präsentiert und den resultierenden `tech_stack:`-Block schreibt. Erwartung: Der Skill folgt der Ermittlungssequenz dieser Spec und den Eintragsschema-Regeln der Schema-Spec; er erfindet keine Einträge, die die Repo-Signale nicht stützen. Kritikalität: primär. Mapping zu AUDIENCES.md → contributors / maintainers → `"Claude Code itself as co-author"`.

### Direkte Konsumenten

Direkte Konsumenten lesen das Inventar und handeln darauf.

- **`portfolio-audit`-Skill (automatisierter Konsumer).** Oberfläche: Parsen der `project/portfolio.yml` jedes Portfolio-Mitglieds plus `claude-shared`'s `portfolio/tech-stack.yml`, Ausführen der Signal-Verifikation aus `spec/portfolio/tech-stack/` §Portfolio-Audit-Integration und Emittieren von Critical-/Warning-/Suggestion-/Info-Befunden gemäß `spec/claude/review-plan/`. Erwartung: Das Inventar parst sauber und der Vererbungs-Vertrag ist eindeutig, sodass das Audit keine Heuristiken braucht. Kritikalität: primär. Tech-Stack-spezifische Verfeinerung nicht in `AUDIENCES.md`: Diese Audience ist eine Software-Capability des `nolte-shared`-Plugins, kein Mensch und keine Organisation, die von den Audience-Kategorien in `AUDIENCES.md` getrackt würden; der Bullet nennt sie ausdrücklich, weil das Audit der primäre automatisierte Konsumer des Inventars ist.

- **Downstream-Claude-Code-Nutzer in Portfolio-Projekten.** Oberfläche: Aufruf des Capture-Skills im eigenen Repository, um dessen `tech_stack:`-Block zu schreiben oder zu überarbeiten, plus Lesen des gerenderten Portfolio-Inventars unter `docs/<lang>/portfolio/`. Erwartung: Der Skill funktioniert ohne pro-Repo-Konfiguration; die geerbten Einträge sind ohne manuelle Deklaration sofort sichtbar; die gerenderte Seite ist eine faire Darstellung des tatsächlichen Stacks des Repos. Kritikalität: primär. Mapping zu AUDIENCES.md → direct consumers → `"Downstream Claude Code users in portfolio projects"`.

- **Onboarding-Beitragender beim Lesen der gerenderten Doku.** Oberfläche: Die Doku-Site unter `docs/<lang>/portfolio/`, die den globalen Stack-Abschnitt und die pro-Repository-Abschnitte mit inherited-/repo-specific-/suppressed-Badges zeigt. Erwartung: Eine einzige Seite beantwortet „worauf baut dieses Repo auf", ohne dass man die Lockfiles und Workflow-Dateien des Repositorys greppen muss. Kritikalität: sekundär. Mapping zu AUDIENCES.md → contributors / maintainers → `"External contributors via pull request"`.

### Indirekte Konsumenten

Indirekte Konsumenten interagieren nicht direkt mit dem Inventar, aber das Inventar prägt ihre Erfahrung.

- **Andere Nolte-Portfolio-Repos als passive Standardisierungs-Referenz.** Oberfläche: keine direkte; der globale Stack wirkt als De-facto-Standardisierungs-Referenz auch für Repos, die den Capture-Skill noch nicht adoptiert haben. Erwartung: Standardisierungs-Entscheidungen tauchen im gerenderten Inventar auf, nicht als stille Normen. Kritikalität: peripher. Mapping zu AUDIENCES.md → indirect → `"Other Nolte portfolio repos as passive consumers of the conventions"`.

- **Endnutzer von Downstream-Projekten, die `nolte-shared` installieren.** Oberfläche: keine direkte; die Konsistenz des Tech-Stacks portfolioweit prägt die Release-Disziplin und Qualitäts-Haltung, die sie sehen. Erwartung: nichts direkt aus diesem Inventar. Kritikalität: peripher. Mapping zu AUDIENCES.md → indirect → `"End users of downstream projects that install nolte-shared"`.

- **Portfolio-Consistency-Anchors (`nolte/gh-plumbing`, `nolte/vale-style`, `nolte/taskfiles`).** Oberfläche: keine direkte; die Anchors sind selbst Portfolio-Mitglied-Repos, deren eigene Tech-Stack-Einträge ein Teil des globalen Inventars werden, sobald sie den Capture-Flow adoptieren. Erwartung: Der globale Stack kodiert keine Tool-Entscheidung still, der die Anchors nicht zugestimmt haben. Kritikalität: sekundär. Mapping zu AUDIENCES.md → governing parties → `"Portfolio-consistency anchors"`.

## Benefits

Ein portfolioweites Tech-Stack-Inventar zahlt den Kurationsaufwand entlang fünf konkreter Achsen zurück. Jeder Vorteil nennt das `project/goals.md`-Outcome, das er bedient, sodass ein Reviewer die Arbeit in PR- oder Sprint-Diskussionen rechtfertigen kann.

- **Sichtbarkeit repoübergreifend** — eine einzige gerenderte Seite beantwortet „welche Repos nutzen MkDocs", „welche Repos nutzen `uv`" und „welches Repo weicht vom Doku-Default ab". Ohne sie erfordert dieselbe Frage Grepping in jedem Repos Lockfiles. Bedient O-1 (Downstream-Konsistenz für Portfolio-Konsumenten): Ein Downstream-Maintainer, der sein Repo gegen das Portfolio vergleicht, schafft das in einer Sicht statt in N Greps.

- **Onboarding-Kosten-Kompression** — ein Onboarding-Beitragender liest eine Seite und kennt die technische Baseline, bevor er eine einzige Datei öffnet. Heute erfordert dieselbe Orientierung Lesen von `pyproject.toml`, `Taskfile.yml`, den Workflow-Dateien und der Doku-Config jedes Repos separat. Bedient O-1 (Downstream-Konsistenz) und O-2 (Authoring-Suite-Ergonomie für den Maintainer): Jede beim Orientieren gesparte Minute ist eine bei der tatsächlichen Mitarbeit verbrachte Minute.

- **Standardisierungs-Druck mit explizitem Sicherheitsventil** — der Vererbungs-Vertrag gibt dem Portfolio einen Default-Stack (MkDocs, Renovate, GitHub Actions), erlaubt aber Einzelrepos, per `overrides:` mit nicht-leerem Rationale auszusteigen. Der Druck ist also sichtbar (ein abweichendes Repo meldet sich an) statt implizit (jeder erfindet das Doku-Setup neu). Bedient O-1 (Downstream-Konsistenz): Konvergenz passiert, weil Abweichung ein Rationale kostet, nicht weil Konformität erzwungen wird.

- **Auditierbarkeit struktureller Ausreißer** — sobald das Inventar existiert, kann `portfolio-audit` ein Repo flaggen, das gerenderte Doku-HTML ausliefert, aber den `docs`-Eintrag nicht erbt und keinen Override trägt, oder ein Repo, das einen `kind: ci`-Eintrag deklariert, dessen `.github/workflows/`-Ordner leer ist. Das Audit kann strukturelle Fragen stellen, die ein freies README schlicht nicht beantworten kann. Bedient O-2 (Authoring-Suite-Ergonomie) und O-3 (jede Spec wird zuerst gegen `claude-shared` dogfooded): Der erste Dogfood-Lauf des Audits trainiert auch `claude-shared`s eigenes Inventar.

- **Dogfooding der Planning-Suite** — `claude-shared` ist selbst ein Portfolio-Mitglied, also trägt seine eigene `project/portfolio.yml` einen `tech_stack:`-Block plus das globale Manifest unter `portfolio/tech-stack.yml`. Der Capture-Flow läuft daher gegen dieses Repository, bevor er an Konsumenten ausgeliefert wird — genau das Proof-of-Life-Muster, das O-3 für jede Spec verlangt, die das Plugin produziert. Bedient O-3 (jede Spec wird zuerst gegen `claude-shared` dogfooded).

## Requirements

### Ermittlungs-Sequenz pro Repository

- **MUSS [MUST]** pro-Repository-Discovery aus Repo-Signalen treiben, bevor der Maintainer zur Bestätigung eingeladen wird. Signal-Quellen umfassen (nicht abschließend): `pyproject.toml`, `uv.lock`, `poetry.lock`, `package.json`, `pnpm-lock.yaml`, `package-lock.json`, `Taskfile.yml`, `.github/workflows/*.yml`, `renovate.json5` / `renovate.json`, `mkdocs.yml`, `.vale.ini`, `.pre-commit-config.yaml`, `.tool-versions` und `pyproject.toml:[tool.ruff]` / `[tool.uv]`-Abschnitte.
- **MUSS [MUST]** eine kuratierte, geschlossene Allowlist bekannter JavaScript-/TypeScript-Ökosystem-Marker, die unter `package.json:dependencies` / `devDependencies` deklariert sind, als vollwertige Discovery-Signale behandeln, damit Framework, Sprache und CSS-Toolkit eines Web-Anwendungs-Repositories als signal-gestützte Kandidaten erfasst werden statt als free-form-`acknowledged-missing-signal:`-Additions. Die Allowlist ordnet jeden Marker einem `kind` zu: `astro`, `next`, `nuxt`, `@sveltejs/kit`, `@remix-run/react`, `gatsby`, `@angular/core`, `vue`, `react`, `solid-js`, `qwik` und `tailwindcss` → `kind: framework`; `typescript` → `kind: language`; `vite` → `kind: build`. Der Versions-Bereich der passenden Dependency wird wörtlich in das `version:`-Feld des Kandidaten übernommen. Die Allowlist zu erweitern ist ein koordinierter Edit dieser Spec plus der Signal-Quellen-Map der Capture-Skill (analog zur Hand-Kurations-Disziplin aus §Globale Stack-Kuration in `claude-shared`), niemals ein heuristischer „jede Dependency emittieren"-Sweep: der Ermittlungs-Fluss bleibt bei „fragen statt raten".
- **MUSS [MUST]** jeden Signal-Treffer dem geschlossenen `kind`-Enum aus `spec/portfolio/tech-stack/` §Kind-Enum zuordnen. Wenn zwei Enum-Werte gleichermaßen plausibel sind, fragt der Ermittlungs-Fluss den Maintainer, statt still zu entscheiden.
- **MUSS [MUST]** jeden Kandidaten-Eintrag *vor* dem Schreiben gegen den aktiven globalen Stack unter `portfolio/tech-stack.yml` abgleichen. Ein Kandidat, der einem geerbten globalen Eintrag entspricht (gleicher `name`, gleicher `kind`), wird aus der vorgeschlagenen `additions:`-Liste entfernt; will der Maintainer abweichen, bietet der Flow einen expliziten `overrides:`-Record mit `inherit: false` und fragt nach einem `rationale`.
- **MUSS [MUST]** jeden vorgeschlagenen Eintrag interaktiv mit dem Maintainer bestätigen, bevor geschrieben wird. Die Bestätigungs-Oberfläche zeigt (a) den vollen Feld-Satz des Kandidaten, (b) die Signal-Quellen, die ihn rechtfertigen, und (c) die inherited-vs-addition-Klassifikation. Der Maintainer antwortet pro Eintrag — annehmen, ablehnen, oder editieren.
- **DARF NICHT [MUST NOT]** einen `tech_stack:`-Block schreiben, bevor der Maintainer mindestens eine Runde des vorgeschlagenen Deltas bestätigt hat; ein leeres `tech_stack: {}` ist ein legitimes Ergebnis und wird erst nach expliziter Bestätigung geschrieben.
- **SOLLTE [SHOULD]** Einträge, die die Signale nicht stützen, die der Maintainer aber explizit (freihändig) hinzufügt, auffällig markieren und eine ausdrückliche Quittung verlangen, dass das Audit ein `Warning` für das fehlende Signal produzieren wird. Der Skill protokolliert die Quittung im `rationale`-Feld des Eintrags; das Audit liest dann das Rationale und stuft den Befund auf `Suggestion` herab.
- **KANN [MAY]** Discovery-State (ein Draft-Delta, eine Liste verworfener Kandidaten) für eine einzige Session persistieren, damit der Maintainer pausieren und fortsetzen kann; persistierter State wird nicht in Git eingecheckt.
- **SOLLTE [SHOULD]** das optionale `version:`-Feld aus dem erkannten Signal vorbefüllen, wenn das Signal eine eindeutige Version trägt (zum Beispiel `pyproject.toml:requires-python` für `kind: language`, name `python`; `package.json:engines.node` für `kind: runtime`, name `node`; ein Tag-Pin in `.tool-versions`). Wenn das Signal mehrdeutig oder abwesend ist, bleibt das Feld leer, statt einen geratenen Wert zu tragen.
- **KANN [MAY]** ein „Kandidaten-nicht-gewählt"-Protokoll neben dem geschriebenen `tech_stack:`-Block ausgeben, das signal-abgeleitete Kandidaten auflistet, die der Maintainer während der Bestätigung abgelehnt hat, mit einem Ein-Phrasen-Ablehnungsgrund pro Eintrag. Das Protokoll dient ausschließlich audit-lesbarer Drift-Erkennung; es wird nicht ins Repository eingecheckt.
- **SOLLTE [SHOULD]** für jeden Eintrag eine `lifecycle:`-Klassifikation vorschlagen, abgeleitet aus `kind:` dort, wo das Mapping eindeutig ist (`test`, `lint`, `dep-bot`, `package-manager` mappen typischerweise auf `development`; `ci`, `build`, `docs` mappen typischerweise auf `build`; `deploy-target` mappt typischerweise auf `runtime`), und beim Maintainer nachfragen, wenn mehrdeutig (`language`, `runtime`, `framework`, `other` hängen davon ab, ob das Repository einen Service ausliefert, nur Build-Artefakte oder beides; ein heuristischer Tipp würde irreführen). Der Vorschlag wird im Bestätigungsschritt oben präsentiert; der Maintainer akzeptiert, editiert oder überspringt das Feld. Überspringen ist legitim; das Feld ist optional.
- **MUSS [MUST]** für jeden Eintrag eine `group:`-Klassifikation vorschlagen, abgeleitet aus `kind:` plus Kontext des tragenden Repositories. Default-Mapping (verwendet, wenn der Zweck des tragenden Repositories nicht schon aus früheren Antworten abgeleitet wurde): `docs` → `documentation`; `lint`, der gegen Doku-Quellen läuft → `documentation`, sonst → `quality`; `test` → `quality`; `ci`, `dep-bot` plus die Probot-Governance-Bots → `automation`; `build`, `package-manager` → `build-tooling`; `framework`, dessen `name` zur Claude-Code-Plugin-Form passt, und `runtime` mit `name: claude-code` → `plugin-platform`. Für `kind: language`, `runtime`, `framework`, `deploy-target` und `other` fragt der Flow den Maintainer nach der Gruppe statt zu raten, weil die Wahl davon abhängt, ob das Tool die primäre Application-Runtime, ein reines Doku-Hilfsmittel oder ein Delivery-Kanal ist. Der Vorschlag wird im Bestätigungsschritt oben präsentiert; der Maintainer akzeptiert, editiert oder eskaliert für einen geerbten globalen Eintrag, dessen repo-spezifische Nutzung abweicht, zu einem `tech_stack.regroup[]`-Record gemäß `spec/portfolio/tech-stack/` §Gruppen-Umklassifizierung.

### Globale Stack-Kuration in `claude-shared`

- **MUSS [MUST]** `portfolio/tech-stack.yml` per Hand kuratieren, niemals via automatisierte Erkennung aus Portfolio-Mitglied-Repositories. Das Auto-Promoten eines Tools zu portfolioweitem Status, weil es in zwei oder drei Repos auftaucht, ist verboten — Promotion ist eine explizite menschliche Entscheidung in einem PR.
- **MUSS [MUST]** jede Revision von `portfolio/tech-stack.yml` durch den Standard-Pull-Request-Workflow (`spec/project/pull-request-workflow/`) routen, damit Änderungen reviewt werden, die Kind-Enum-Integrität geprüft wird und Conventional-Commits-Semantik erhalten bleibt.
- **SOLLTE [SHOULD]** jede Eintrags-Transition (`experimental → active`, `active → deprecated`) im PR-Body mit einem Ein-Satz-Rationale begleiten, das auf ein Sprint-Outcome oder einen `portfolio-audit`-Befund verweist, damit das Lifecycle-Vokabular nicht zu Bürokratie degeneriert.
- **KANN [MAY]** ein Tracking-Issue unter `nolte/claude-shared` öffnen, wenn ein `experimental`-Eintrag von einem Konsumer über einen geschlossenen Sprint ohne Override adoptiert wurde, um das Promotions-Kriterien-SOLLTE aus `spec/portfolio/tech-stack/` §Vererbungs-Semantik anzustoßen.

### Audience-Fit-Gate

- **MUSS [MUST]** die unter §Audiences oben aufgezählten Audiences als bindend behandeln: Eine Änderung der Ermittlungs-Sequenz, des globalen Stacks oder des gerenderten Inventars, die eine primäre Audience betrifft, ohne dass diese Audience konsultiert wurde (direkt, via `AUDIENCES.md` oder via `audience-identify`), ist reviewbar, aber nicht mergebar.
- **MUSS [MUST]** `AUDIENCES.md` konsultieren, wann immer eine primäre Audience ihre Oberfläche ändert (beispielsweise „Downstream Claude Code users in portfolio projects" gewinnen einen neuen Opt-in-Pfad) und die Änderung im selben PR auf §Audiences dieser Spec propagieren.
- **SOLLTE [SHOULD]** §Audiences dieser Spec immer dann erneut prüfen, wenn die Revisit-Trigger von `AUDIENCES.md` (gemäß `spec/project/audience-identification/`) feuern, auch wenn der Trigger nicht tech-stack-spezifisch ist.

### Benefits-Dokumentations-Gate

- **MUSS [MUST]** jeden Bullet unter §Benefits an mindestens eine Outcome-ID aus `project/goals.md` ankern (aktuell `O-1`, `O-2`, `O-3`). Ein Vorteil, der sich nicht an ein Outcome anbinden lässt, wird umformuliert oder entfernt.
- **SOLLTE [SHOULD]** den gerenderten Benefits-Abschnitt wörtlich in der Portfolio-Doku-Seite unter `docs/<canonical_language>/portfolio/` zitieren, damit ein Leser auf der Doku-Site die Spec nicht öffnen muss, um zu sehen, warum das Inventar existiert.
- **KANN [MAY]** in einem PR, der die Reichweite des Inventars wesentlich erweitert, einen neuen Benefits-Bullet hinzufügen (zum Beispiel „Dependency-Bot-Input-Priorisierung", sobald `portfolio-audit` Renovate-Entscheidungen speist); jeder neue Bullet folgt der Outcome-Anker-Regel.

### Cross-References

- **MUSS [MUST]** von `spec/portfolio/tech-stack/` (kanonisch und jede Übersetzung) per Cross-Reference (Ein-Satz-Verweis oder kurze Unter-Sektion) referenziert werden, der diese Spec als Eigentümer der Ermittlungs-Methodik, des Audience-Modells und der Benefits-Prosa nennt; das Wiederholen einer der drei Sachen in der Schema-Spec ist verboten.
- **DARF NICHT [MUST NOT]** Felder des Eintragsschemas, das `kind`-Enum, den Vererbungs-Vertrag oder die Audit-Severity-Tabelle neu definieren; diese leben in `spec/portfolio/tech-stack/` und werden per Referenz importiert.
- **MUSS [MUST]** in `AUDIENCES.md` unter dem relevanten Revisit-Trigger referenziert werden, wenn diese Spec ihre §Audiences wesentlich ändert.

## Acceptance Criteria

- [ ] `spec/portfolio/tech-stack/` (kanonisch und jede vorhandene Übersetzung) trägt einen Ein-Satz-Cross-Reference zu dieser Spec, der sie als Eigentümer der Ermittlungs-Methodik, des Audience-Modells und der Benefits-Prosa nennt.
- [ ] `AUDIENCES.md` §Revisit triggers nennt diese Spec als Trigger für den Fall, dass §Audiences sich wesentlich ändert.
- [ ] Jeder Bullet unter §Audiences löst sich auf einen Eintrag in `AUDIENCES.md` auf, oder §Audiences vermerkt explizit, dass der Bullet eine tech-stack-spezifische Verfeinerung eines AUDIENCES.md-Eintrags ist, mit Ein-Satz-Begründung.
- [ ] Jeder PR, der die §Ermittlungs-Sequenz pro Repository, die §Globale Stack-Kuration in `claude-shared` oder das gerenderte Inventar ändert und eine primäre Audience betrifft, nennt in seiner Beschreibung, welche primäre Audience konsultiert wurde und wie (ein wörtliches Zitat aus `AUDIENCES.md`, ein direktes Gespräch oder ein erneutes Ausführen von `audience-identify` reichen aus).
- [ ] Jeder Bullet unter §Benefits trägt mindestens eine explizite Outcome-ID-Referenz zu `project/goals.md`.
- [ ] `portfolio/tech-stack.yml` in diesem Repository ist handgepflegt (verifiziert via git-blame, das Maintainer-Commits zeigt, niemals einen automatisierten Generierungs-Commit).
- [ ] Der Capture-Skill (wenn er entsteht) implementiert die §Ermittlungs-Sequenz pro Repository in der dokumentierten Reihenfolge; ein Skill-Review gemäß `spec/claude/skill-review/` bestätigt die Reihenfolge.
- [ ] Die gerenderte Portfolio-Doku-Seite unter `docs/<canonical_language>/portfolio/` enthält entweder den wörtlichen §Benefits-Abschnitt oder eine kurze Paraphrase mit Backlink zu dieser Spec.
- [ ] Keine Revision dieser Spec landet ohne entsprechende Sync-Prüfung gegen `AUDIENCES.md`; die PR-Beschreibung nennt das Sync-Ergebnis.
- [ ] Keine Revision von `spec/portfolio/tech-stack/` landet ohne Sync-Prüfung gegen diese Spec; die PR-Beschreibung nennt das Sync-Ergebnis.
- [ ] Die Signal-Quellen-Map der Capture-Skill (`skills/tech-stack-capture/references/signal-source-map.md`) trägt genau eine Zeile pro Marker der §Ermittlungs-Sequenz-JS-/TS-Allowlist, und keine Allowlist-Zeile existiert in der Map ohne korrespondierenden Spec-Eintrag; eine Abweichung in beide Richtungen ist Drift.

## Open Questions

_Alle zuvor zurückgestellten offenen Fragen wurden am 2026-06-06 entschieden: jeder vorläufige Default ist nun die geltende Regel. Die Einzelentscheidungen und Begründungen sind in der Git-Historie erhalten (Entscheidungslog, 2026-06-06)._
