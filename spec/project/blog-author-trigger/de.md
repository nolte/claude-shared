# Blog-Autor-Trigger

Status: draft

## Kontext

Leserschaft: Implementierer einer zukünftigen Trigger-Skill oder eines Hooks, der die [`blog-author`](../blog-author/de.md)-Skill aufruft (primär), menschliche Operatoren, die abwägen, wann das Fertigstellen eines Features ein Blog-Post-Update rechtfertigt (sekundär), und Skill-Autoren, die diesen Trigger mit dem Sprint- und Feature-Lifecycle des Konsumenten integrieren.

Die [`blog-author`](../blog-author/de.md)-Skill definiert, **was** ein Autor produziert—ein zweisprachiges Post-Paar, ein Selbst-Check-Manifest, ein Quellen-zu-Behauptungs-Mapping, ein Übergabe-Manifest. Was jene Spec absichtlich offen lässt, ist, **wann** der Autor aufgerufen wird. Heute ist der einzige kanonische Trigger operator-initiiert: der Operator tippt `/nolte-shared:blog-author` (oder eine gleichwertige natürlichsprachige Anfrage) und durchläuft die Briefing-Intake. Das Post-Paar lebt in einem separaten Konsumenten-Repository (der Referenzkonsument ist `nolte/blog`); der Trigger feuert nicht automatisch, wenn Arbeit im **selben** Quell-Konsumenten einen Zustand erreicht, der das Schreiben darüber rechtfertigt.

Diese Spec schließt die Lücke auf einer Seite dieser Frage: sie definiert den Vertrag, mit dem ein **Feature-done-Ereignis** in einem Konsumenten der Sprint-und-Feature-Specs dieses Plugins (`spec/project/sprint/`, `spec/project/feature/`) an einen **Blogpost-Vorschlag** verdrahtet werden kann, den der Operator entweder annimmt (was `blog-author` mit einem abgeleiteten Briefing aufruft) oder zurückstellt (was den Trigger in einem pro-Feature-Backlog festhält). Die Spec ist **vertragsorientiert**: sie benennt das Trigger-Ereignis, die Form des abgeleiteten Briefings, die Operator-Entscheidungspunkte und das Verhältnis zu den aufrufenden Skills. Sie schreibt **nicht** den Verdrahtungsmechanismus vor (einen Hook in `settings.json`, eine Folgedispatch aus `sprint-execute`, eine separate Trigger-Skill); diese Wahl ist offen und unter §Offene Fragen festgehalten.

Das Referenzszenario, für das diese Spec entworfen ist: ein Feature in `nolte/claude-shared` (dieses Plugin) erreicht `done` per `sprint-execute`; der Operator möchte, dass `blog-author` einen Draft (neuer Post oder Update zu einem bestehenden Post) über dieses Feature in `nolte/blog` produziert. Die Spec ist so formuliert, dass derselbe Trigger für jedes Konsumenten-Paar funktioniert, in dem ein Repository die Quelle der Arbeit beherbergt und ein anderes Repository den Personal-Blog.

## Ziele

- Ein **benanntes Trigger-Ereignis** definieren (`feature → done`), an das nachgelagerte Skills, Hooks oder Operator-Workflows ansetzen können, mit einem geschlossenen Input-Vertrag, abgeleitet aus dem Feature-Record.
- Den **Briefing-Ableitungs-Vertrag** definieren: wie ein Feature-Record (per `spec/project/feature/`) in ein Briefing umgewandelt wird, das die §Briefing-Inputs von [`blog-author`](../blog-author/de.md) erfüllt.
- Den **Operator-Entscheidungs-Vertrag** definieren: am Trigger-Punkt beantwortet der Operator eine von drei Wahlen—neuen Post verfassen, bestehenden Post aktualisieren, ins Backlog zurückstellen. Die Spec benennt, wie jede Wahl downstream fließt.
- Den **Dual-Repository-Vertrag** definieren: das Quell-Feature lebt in einem Konsumenten-Repository (hier: ein `claude-shared`-förmiges Repository mit `project/features/`); das Post-Paar lebt in einem separaten Konsumenten-Repository (hier: ein `blog-author`-förmiges Blog-Repository). Der Trigger ist die Brücke.
- Das **Zurückstellungs-Artefakt** definieren: eine Zurückstellungs-Wahl lässt den Trigger nicht still fallen; sie erzeugt einen pro-Feature-Eintrag, der bei Sprint-Review oder später wieder zur Oberfläche kommen kann.
- Die Spec **verdrahtungsagnostisch** halten: der Mechanismus (Hook, Skill-Kette, separate Trigger-Skill) ist offen. Die Spec ist der Vertrag, den jeder Mechanismus einhalten muss.

## Nicht-Ziele

- Den **Verdrahtungsmechanismus** für den Trigger definieren. Ob der Trigger aus einem Claude-Code-`settings.json`-Hook feuert, aus einer Folgedispatch innerhalb von `sprint-execute`, aus einer neuen dedizierten Trigger-Skill oder aus einer GitHub Action, ist absichtlich außerhalb des Geltungsbereichs; siehe §Offene Fragen.
- Definieren, **wie `blog-author` den Post erzeugt**, sobald aufgerufen. Das wird umfassend von [`blog-author`](../blog-author/de.md) abgedeckt; diese Spec endet an der Wahl des Operators und an der Übergabe des abgeleiteten Briefings.
- Die **Feature-Record-Form selbst** definieren (Frontmatter, Lifecycle-Zustände, AC-Struktur). Das gehört [`spec/project/feature/`](../feature/de.md); diese Spec konsumiert den Feature-Record, wie er existiert.
- Den **Sprint-Execute-Lifecycle** definieren (wann ein Feature `in_progress → done` übergeht, wer entscheidet, welche Gates gelten). Das gehört [`spec/project/sprint/`](../sprint/de.md); diese Spec konsumiert das Übergangs-Ereignis.
- **Cross-Repository-Schreibrechte** definieren (ob die Trigger-Skill in einem Repo operiert und in ein anderes schreibt, oder ob der Operator manuell Repos wechselt). Die Spec beschreibt den Vertrag; der §Referenz-Beispiel-Annex benennt, wie das Referenz-Konsumenten-Paar (`nolte/claude-shared` + `nolte/blog`) damit umgeht, aber andere Konsumenten-Paare können anders verfahren.
- **Veröffentlichungs-Frequenz-Politik** definieren (jedes Feature bekommt einen Post vs. nur Meilenstein-Features vs. Sprint-Zusammenfassungs-Posts vs. Ad-hoc-Kuration). Das ist eine Roadmap-Frage für den Quell-Konsumenten, keine Trigger-Spec-Frage.
- **Die lektorseitige Reaktion auf einen getriggerten Post** definieren (würde `lektorat-apply` getriggerte Posts anders behandeln als operator-initiierte?). Heute ist die Antwort nein—getriggerte und manuelle Posts teilen denselben `blog-author`-Workflow, denselben Liefervertrag und dieselbe Lektor-Übergabe.

## Konsumenten-Vertrag

Diese Spec setzt zwei Konsumenten-Repositories voraus—einen **Quell-Konsumenten** und einen **Blog-Konsumenten** —, die dieselbe oder verschiedene Repositories sein dürfen. Ein Konsument, der diese Spec übernimmt, **MUSS [MUST]** in seinem `CLAUDE.md` (oder gleichwertigen Vertragsdokument) deklarieren, welche Rolle jede Seite spielt.

### Quell-Konsument

Ein Quell-Konsument, der diese Spec übernimmt, **MUSS [MUST]** Folgendes erfüllen:

- Das Repository beherbergt Features per [`spec/project/feature/`](../feature/de.md) und Sprints per [`spec/project/sprint/`](../sprint/de.md). Features tragen Frontmatter, das mindestens einen Titel, einen Status und einen Akzeptanzkriterien-Block benennt, und leben unter `project/features/<slug>.md`.
- Das Repository ruft [`sprint-execute`](../../../skills/sprint-execute/SKILL.md) auf (oder eine gleichwertige Skill, die `spec/project/sprint/` erfüllt), um Feature-Übergänge zu treiben. Der `in_progress → done`-Übergang ist das in §Trigger-Ereignis benannte Trigger-Ereignis.
- Das Repository deklariert in seinem `CLAUDE.md`, welcher **Blog-Konsument** abgeleitete Briefings empfängt—per Name (z. B. `nolte/blog`), per Clone-Pfad (z. B. `~/repos/github/blog`) oder per beidem. Ein Quell-Konsument **DARF [MAY]** sich selbst als eigenen Blog-Konsumenten deklarieren (ein einzelnes Repository beherbergt sowohl Quellarbeit als auch Blog).

### Blog-Konsument

Ein Blog-Konsument, der diese Spec übernimmt, **MUSS [MUST]** den §Konsumenten-Vertrag von [`blog-author`](../blog-author/de.md) erfüllen. Er **MUSS [MUST]** zusätzlich deklarieren:

- Einen **Bestehende-Posts-Index**, den der Trigger konsultieren kann, um die „bestehenden Post aktualisieren?"-Frage des Operators zu beantworten. Die Referenzkonvention ist die Post-Paar-Lokation des Konsumenten (`src/content/posts/en/` für Astro-Konsumenten) plus eine Korpus-Auflistung, die bestehende Slugs auf ihr `pubDate`, `tags` und `portfolioProject`-Frontmatter abbildet.
- Ein **Portfolio-Projekt-Mapping** (optional, **SOLLTE [SHOULD]**), das dem Trigger erlaubt, das `portfolioProject`-Feld des Briefings aus dem Repository-Namen des Quell-Konsumenten vorauszufüllen (z. B. bildet ein Feature in `nolte/claude-shared` auf `portfolioProject: claude-shared` ab). Wenn fehlend, liefert der Operator den Wert bei der Briefing-Intake.

## Anforderungen

### Trigger-Ereignis

- **MUSS [MUST]** das Trigger-Ereignis als **`feature → done`** benennen: der Übergang eines Feature-Records von `status: in_progress` zu `status: done` per [`spec/project/feature/`](../feature/de.md) §Lifecycle. Das Ereignis wird in dem Moment beobachtet, in dem der Feature-Record mit dem neuen Status auf die Festplatte geschrieben wird—nicht in dem Moment, in dem ein PR gemerged wird, nicht in dem Moment, in dem ein Sprint schließt.
- **MUSS [MUST]** das Trigger-Ereignis die folgende Payload tragen, direkt aus dem Feature-Record abgeleitet:
  - Die **`id`** und der **`slug`** des Features.
  - Der **`title`** und die **`description`** des Features (Freitext-Body des Feature-Records).
  - Die **Akzeptanzkriterien** des Features als Liste von Strings (der Body-Block unter §Akzeptanzkriterien in der Feature-Datei).
  - Der **Roadmap-Item-Rückverweis** des Features (falls vorhanden) per [`spec/project/feature/`](../feature/de.md)—verwendet, um `portfolioProject` abzuleiten, wenn der Quell-Konsument ein Roadmap-zu-Portfolio-Mapping ausliefert.
  - Der **Repository-Name** des Quell-Konsumenten (z. B. `nolte/claude-shared`) und der **Commit-SHA** des `in_progress → done`-Übergangs-Commits.
- **DARF NICHT [MUST NOT]** das Trigger-Ereignis eine Payload tragen, die nicht aus dem On-Disk-Feature-Record oder der Git-History ableitbar ist. Der Trigger ist reproduzierbar: gegeben derselbe Feature-Record und dieselbe Git-History, feuert dasselbe Trigger-Ereignis.
- **DARF NICHT [MUST NOT]** andere Lifecycle-Übergänge (`ready → in_progress`, `done → cancelled`, Sprint-Level-Übergänge) diesen Trigger feuern. Ihre Semantik unterscheidet sich; ihre Behandlung gehört in separate Trigger, wenn und falls nötig (siehe §Offene Fragen).
- **SOLLTE [SHOULD]** das Trigger-Ereignis einen **abgeleiteten Vorschlag** tragen, ob das Feature einen neuen Post oder ein Update zu einem bestehenden Post rechtfertigt, berechnet aus dem Bestehende-Posts-Index (siehe §Operator-Entscheidungs-Vertrag). Der Vorschlag ist beratend; die Wahl des Operators überstimmt ihn.

### Briefing-Ableitung

Das Trigger-Ereignis wird in ein Briefing umgewandelt, das die §Briefing-Inputs von [`blog-author`](../blog-author/de.md) erfüllt. Die Ableitungs-Regeln unten sind deterministisch: gegeben dieselbe Trigger-Ereignis-Payload, wird dasselbe Briefing produziert.

- **MUSS [MUST]** das **Topic-as-Thesis** aus dem Feature-`title` plus dem ersten Satz der Feature-`description` ableiten. Der Operator wird bei der Briefing-Intake aufgefordert, die These zu verfeinern; die abgeleitete Form ist ein Startpunkt, nicht der endgültige Wert. Beispiel: Feature „Add lektorat-scanner agent" mit Beschreibung „Read-only scanner that walks Markdown artefacts and returns D1–D5 findings" leitet die These ab „Ich beschreibe den read-only lektorat-scanner-Agent, der Markdown-Artefakte durchläuft und D1–D5-Befunde zurückgibt".
- **MUSS [MUST]** das **gegründete-Artefakt**-Feld mit dem Repository-Verweis des Quell-Konsumenten (`<owner>/<repo>` plus dem `done`-Übergangs-Commit-SHA) befüllen. Das erfüllt [`blog-author`](../blog-author/de.md) §Briefing-Inputs „mindestens ein gegründetes Artefakt" minimal; der Operator **DARF [MAY]** bei Intake Diffs, Befehlsausgaben oder Screenshots hinzufügen.
- **MUSS [MUST]** die **Primär-Audience** im abgeleiteten Briefing ungesetzt lassen. Der Trigger hat keine Basis, um zwischen den Endleser-Untergruppen des Konsumenten (Referenz: `A`/`B`/`C`) zu wählen; der Operator **MUSS [MUST]** bei Intake auswählen.
- **MUSS [MUST]** die **Quellenliste** mit mindestens der Repository-URL des Quell-Konsumenten seeden (`https://github.com/<owner>/<repo>/commit/<sha>`). Der Operator erweitert die Liste bei Intake; der Seed erfüllt das Verbot der leeren Liste für Posts, die das Repository des Quell-Konsumenten benennen.
- **MUSS [MUST]** den **Slug** aus dem Feature-`slug` mit entferntem Präfix ableiten (z. B. leitet das Feature `add-lektorat-scanner-agent` den Post-Slug `lektorat-scanner-agent` ab); wenn der abgeleitete Slug bereits im Bestehende-Posts-Index des Blog-Konsumenten existiert, flagged der Trigger ein Update (siehe §Operator-Entscheidungs-Vertrag).
- **MUSS [MUST]** den **sprachübergreifenden Bindungs-Key** (Referenz: `translationKey`) aus dem Post-Slug ableiten. Die Konvention folgt der Slug-zu-Key-Regel des Blog-Konsumenten; der Referenzkonsument (`nolte/blog`) setzt `translationKey` gleich dem Slug.
- **SOLLTE [SHOULD]** das **`portfolioProject`** aus dem Repository-Namen des Quell-Konsumenten ableiten, wenn der Blog-Konsument ein Portfolio-Mapping ausliefert (z. B. `nolte/claude-shared` → `portfolioProject: claude-shared`). Wenn fehlend, liefert der Operator den Wert bei Intake.

### Operator-Entscheidungs-Vertrag

Am Trigger-Punkt beantwortet der Operator genau eine der drei Wahlen unten. Die Wahl ist das Gate zu nachgelagertem Verhalten; der Trigger geht ohne sie nicht weiter.

- **Wahl 1—neuen Post verfassen.** Der Trigger dispatched [`blog-author`](../blog-author/de.md) mit dem abgeleiteten Briefing als Schritt-1-Input. Der Operator durchläuft von dort den standardmäßigen Sieben-Schritte-Workflow.
- **Wahl 2—bestehenden Post aktualisieren.** Der Trigger dispatched [`blog-author`](../blog-author/de.md) mit dem abgeleiteten Briefing plus dem `slug` und `translationKey` des bestehenden Posts (der Operator wählt den Ziel-Post aus dem Bestehende-Posts-Index). Der Update-Pfad wird von [`blog-author`](../blog-author/de.md) §Briefing-Inputs „Update- vs. Neuanlage-Felder" geregelt; der Trigger liefert den **Update-Anlass** als den Feature-`title` plus eine Ein-Zeilen-Zusammenfassung dessen, was sich geändert hat.
- **Wahl 3—ins Backlog zurückstellen.** Der Trigger schreibt einen pro-Feature-Backlog-Eintrag (siehe §Zurückstellungs-Artefakt). Der Operator kann beim Sprint-Review oder zu jeder Zeit später erneut prüfen; der Eintrag persistiert, bis er entweder von einem späteren Trigger-Lauf konsumiert oder explizit abgebrochen wird.

Der Operator **MUSS [MUST]** die Wahl innerhalb derselben Claude-Code-Session treffen, in der der Trigger feuert; der Trigger erstreckt sich nicht über Sessions. Wenn die Session ohne Wahl endet, wird der Trigger implizit per Wahl 3 zurückgestellt.

Wenn mehrere `feature → done`-Übergänge in einer Session feuern, **MUSS [MUST]** der Trigger sie sequenziell zur Oberfläche bringen—eine dreifache Wahl pro Feature—statt mehrere Features in eine einzelne Entscheidung zu batchen; das hält a-4 „genau drei Wahlen pro Trigger-Punkt" pro Feature intakt. Der Trigger **DARF [MAY]** eine Alle-verbleibenden-überspringen-Abkürzung anbieten, die jedes verbleibende Feature per Wahl 3 zurückstellt.

Der Trigger **DARF [MAY]** einen **abgeleiteten Vorschlag** tragen (per §Trigger-Ereignis), der Wahl 1, 2 oder 3 basierend auf der Suche im Bestehende-Posts-Index empfiehlt. Beispiel-Heuristiken (nicht normativ):

- Abgeleiteter Slug nicht im Bestehende-Posts-Index → Wahl 1 vorschlagen.
- Abgeleiteter Slug bereits im Bestehende-Posts-Index → Wahl 2 mit diesem Post als Ziel vorschlagen.
- Feature ist das dritte in einem Sprint, dessen `verifies_sprint_value`-Feature noch nicht ausgeliefert wurde → Wahl 3 vorschlagen (zurückstellen, bis das wertverifizierende Feature des Sprints bereit ist, dann einen Sprint-Zusammenfassungs-Post schreiben).

### Zurückstellungs-Artefakt

Eine Wahl-3-Zurückstellung schreibt einen Backlog-Eintrag, der Claude-Code-Sessions überlebt und erneut zur Oberfläche kommen kann.

- **MUSS [MUST]** das Zurückstellungs-Artefakt im Repository des **Quell-Konsumenten** liegen (nicht im Blog-Konsumenten), unter `project/blog-triggers/<feature-slug>.yml`. Der Pfad hält die Zurückstellung mit dem Feature-Record, auf den sie sich bezieht, co-lokalisiert.
- **MUSS [MUST]** das Zurückstellungs-YAML die volle Trigger-Ereignis-Payload (per §Trigger-Ereignis) plus einen `deferred_at`-Zeitstempel, einen `deferral_reason` (Freitext, operator-geliefert zur Entscheidungszeit) und ein `status`-Feld mit einem der Werte `deferred`, `cancelled`, `consumed` tragen.
- **MUSS [MUST]** ein späterer Trigger-Lauf, der dieselbe Feature-`id` erneut antrifft, das bestehende Zurückstellungs-Artefakt konsumieren, statt ein zweites zu erzeugen. Der Trigger aktualisiert `status: deferred → consumed`, wenn der Operator beim zweiten Durchlauf Wahl 1 oder Wahl 2 trifft; `status: cancelled` ist operator-gesetzt und niemals trigger-gesetzt. Ein Zurückstellungs-Artefakt kann durch Feature-Abbruch niemals veralten: es wird nur nach `feature → done` geschrieben, und [`spec/project/feature/`](../feature/de.md) §Lifecycle macht `cancelled` nur aus `draft`, `ready` oder `in_progress` erreichbar—niemals aus `done`—, sodass ein Feature, das eine Zurückstellung trägt, `cancelled` über den legalen Lifecycle nie erreichen kann.
- **SOLLTE [SHOULD]** die `sprint-review`-Skill des Quell-Konsumenten (per [`spec/project/sprint/`](../sprint/de.md)-Lifecycle) unkonsumierte Zurückstellungen beim Sprint-Schluss an die Oberfläche bringen, damit Zurückstellungen nicht still auflaufen. Der Mechanismus ist Wahl des Quell-Konsumenten; diese Spec beschreibt den Vertrag, nicht die Verdrahtung.

### Cross-Repository-Übergabe

Wenn der Quell-Konsument und der Blog-Konsument **verschiedene Repositories** sind, überquert der Trigger eine Repository-Grenze. Der Übergabe-Vertrag:

- **MUSS [MUST]** der Trigger im Claude-Code-Arbeitsverzeichnis des Quell-Konsumenten laufen; der Trigger liest den Feature-Record aus `project/features/<slug>.md` und schreibt das Zurückstellungs-Artefakt (wenn zutreffend) unter `project/blog-triggers/` des Quell-Konsumenten.
- **MUSS [MUST]** die Dispatch an [`blog-author`](../blog-author/de.md) (Wahl 1 und 2) die Repository-Grenze explizit überqueren. Der Trigger **DARF NICHT [MUST NOT]** still ins Arbeitsverzeichnis des Blog-Konsumenten `cd`-en; er **MUSS [MUST]** den Pfad dem Operator anzeigen und den Operator den Arbeitsverzeichnis-Wechsel bestätigen lassen (oder eine neue Claude-Code-Session im Clone des Blog-Konsumenten öffnen).
- **DARF NICHT [MUST NOT]** der Trigger Dateien in den Working-Tree des Blog-Konsumenten ohne explizite Operator-Bestätigung schreiben. Der Working-Tree des Blog-Konsumenten ist der lokale Clone des Operators; der Trigger respektiert das lokale Repository als die Arbeitsumgebung des Operators.
- **DARF [MAY]** der Trigger das abgeleitete Briefing als Markdown-Datei unter `project/blog-triggers/<feature-slug>.briefing.md` des Quell-Konsumenten vorbereiten, damit der Operator es kopieren oder in der Session des Blog-Konsumenten öffnen kann. Die vorbereitete Datei verwendet die Briefing-Form, die [`blog-author`](../blog-author/de.md) §Briefing-Inputs erwartet.

Wenn der Quell-Konsument **ist** der Blog-Konsument (ein einzelnes Repository beherbergt sowohl Quellarbeit als auch Blog), kollabiert die Cross-Repository-Übergabe: der Trigger dispatched `blog-author` in-place, ohne Arbeitsverzeichnis-Wechsel.

Die bedingungslose Kein-stilles-Schreiben-Haltung oben ist entschieden: diese Spec trägt **keinen** Opt-in für vollautomatisches Cross-Repo-Posting, und die Operator-Bestätigung **MUSS [MUST]** jedem Schreibvorgang in den Working-Tree des Blog-Konsumenten vorausgehen, unabhängig davon, wie ein-händig das Konsumenten-Paar ist. Eine zukünftige Iteration, die diese Sicherheitsmarge gegen Bequemlichkeit eintauscht (zum Beispiel eine `cross_repo_autopost`-Deklaration, die dem Trigger erlaubt, die Blog-Konsumenten-Session automatisch zu öffnen), ist eine bewusste, vom Eigentümer autorisierte Änderung an diesem Abschnitt, kein Default, den der Trigger annehmen darf.

## Akzeptanzkriterien

Eine Trigger-Implementierung (Hook, Skill oder Operator-Workflow) erfüllt diese Spec, wenn **alle** der pro-Trigger-Kriterien unten gelten.

- [ ] **a-1** Der Trigger feuert genau am `feature → done`-Übergang; kein anderer Lifecycle-Übergang triggert ihn (per §Trigger-Ereignis).
- [ ] **a-2** Die Trigger-Ereignis-Payload ist vollständig aus dem On-Disk-Feature-Record und der Git-History ableitbar; keine andere Quelle trägt zur Payload bei (per §Trigger-Ereignis).
- [ ] **a-3** Das abgeleitete Briefing erfüllt die Pflichtfelder-Liste von [`blog-author`](../blog-author/de.md) §Briefing-Inputs, modulo der explizit operator-pflichtigen Felder (Primär-Audience) (per §Briefing-Ableitung).
- [ ] **a-4** Dem Operator werden am Trigger-Punkt genau die drei Wahlen (neuer Post, bestehenden Post aktualisieren, ins Backlog zurückstellen) präsentiert (per §Operator-Entscheidungs-Vertrag).
- [ ] **a-5** Eine Wahl-3-Zurückstellung schreibt einen Backlog-Eintrag unter `project/blog-triggers/<feature-slug>.yml` des Quell-Konsumenten mit dem in §Zurückstellungs-Artefakt beschriebenen Schema.
- [ ] **a-6** Ein späterer Trigger-Lauf auf derselben Feature-`id` konsumiert das bestehende Zurückstellungs-Artefakt, statt ein Duplikat zu erzeugen (per §Zurückstellungs-Artefakt).
- [ ] **a-7** Wenn Quell-Konsument ≠ Blog-Konsument, schreibt der Trigger keine Dateien in den Working-Tree des Blog-Konsumenten ohne explizite Operator-Bestätigung (per §Cross-Repository-Übergabe).
- [ ] **a-8** Wenn der Operator Wahl 1 oder Wahl 2 trifft, wird das abgeleitete Briefing an [`blog-author`](../blog-author/de.md) Schritt 1 übergeben und der standardmäßige Sieben-Schritte-Workflow läuft von dort.

## Referenz-Beispiel-Annex

Das Referenz-Konsumenten-Paar ist:

- **Quell-Konsument**: `nolte/claude-shared` (das Repository dieses Plugins). Beherbergt Features unter `project/features/<slug>.md`, ruft [`sprint-execute`](../../../skills/sprint-execute/SKILL.md) auf, um Übergänge zu treiben.
- **Blog-Konsument**: `nolte/blog` (ein zweisprachiger Astro-Static-Blog). Beherbergt Post-Paare unter `src/content/posts/{en,de}/<slug>.md`, erfüllt alle `blog-author`-Konsumenten-Vertrag-Oberflächen per `spec/project/blog-author/` §Referenz-Beispiel-Annex.

Die Cross-Repository-Übergabe für dieses Paar ist: der Operator führt den Trigger aus dem `claude-shared`-Clone aus; bei Wahl 1 oder 2 schreibt der Trigger ein vorbereitetes Briefing unter `claude-shared/project/blog-triggers/<feature-slug>.briefing.md`, zeigt den Pfad zu `~/repos/github/blog` an, und der Operator öffnet eine neue Claude-Code-Session in `~/repos/github/blog` und ruft `blog-author` mit dem vorbereiteten Briefing als Input auf.

Die Referenz-Verdrahtung, die den Trigger feuert, ist die [`blog-author-trigger`](../../../skills/blog-author-trigger/SKILL.md)-Skill, automatisch dispatched aus [`sprint-execute`](../../../skills/sprint-execute/SKILL.md) Operation C (`in_progress → done`) Schritt 6. Die Skill besitzt die Briefing-Ableitung, die dreifache Operator-Wahl und das Deferral-Artefakt; `sprint-execute` feuert sie nur, nachdem das Feature als `done` markiert wurde. Diese Paarung (eine dedizierte Skill, in-session aus `sprint-execute` per [`sprint/de.md`](../sprint/de.md) dispatched) ist nur die Referenzwahl; die Spec bleibt verdrahtungsagnostisch, und andere Konsumenten dürfen weiterhin einen anderen Mechanismus wählen.

Portfolio-Projekt-Mapping für dieses Paar: jedes Feature in `nolte/claude-shared` bildet auf `portfolioProject: claude-shared` in der Portfolio-Collection des Blog-Konsumenten ab. Das Mapping ist im `CLAUDE.md` des Blog-Konsumenten deklariert.

Andere Konsumenten-Paare, die diese Spec übernehmen, tragen einen analogen Annex im `CLAUDE.md` (oder gleichwertigen Vertragsdokument) des Quell-Konsumenten.

## Offene Fragen

- **Trigger aus `ready → in_progress` (Start-der-Arbeit-Post).** Manche Posts machen mehr Sinn, wenn die Arbeit beginnt (ein „hier ist das Problem, das ich angehe"-Post), als wenn die Arbeit endet. Ob diese Spec ein zweites Trigger-Ereignis für den Start-der-Arbeit-Fall wachsen lässt, ist offen. Ausgelöst vom ersten Operator, der danach fragt; bis dahin sind Start-der-Arbeit-Posts operator-initiiert wie jeder andere.
- **Sprint-Zusammenfassungs-Trigger.** Ein Sprint-Level-Zusammenfassungs-Post (ein Post pro Sprint, der alle Features dieses Sprints abdeckt) ist eine andere Form als ein pro-Feature-Post. Ob diese Spec ein `sprint → review`-Trigger-Ereignis für Sprint-Zusammenfassungen wachsen lässt—verdrahtet an [`sprint-review`](../../../skills/sprint-review/SKILL.md) —, ist offen. Die zwei könnten komponieren: ein Sprint mit fünf Features würde fünf pro-Feature-Trigger feuern (die meisten zurückgestellt) und einen Sprint-Zusammenfassungs-Trigger beim Sprint-Schluss. Aufgeschoben, bis der Operator mindestens einen vollen Sprint mit dieser verdrahteten Spec ausgeführt hat.
## Referenzen

Schwester-Specs (in diesem Plugin):

- [`blog-author/de.md`](../blog-author/de.md)—was der Autor produziert; konsumiert das Briefing, das diese Spec ableitet.
- [`feature/de.md`](../feature/de.md)—der Feature-Record, den diese Spec liest.
- [`sprint/de.md`](../sprint/de.md)—der Sprint-Lifecycle, dessen `feature → done`-Übergang diese Spec angreift.
- [`roadmap/de.md`](../roadmap/de.md)—die Quelle des in §Briefing-Ableitung referenzierten Portfolio-Projekt-Mappings.

Hintergrund:

- [`spec/claude/resumable-work/`](../../claude/resumable-work/de.md)—relevant, wenn der Operator Wahl 1 oder 2 trifft und der resultierende `blog-author`-Aufruf Resume-Semantik benötigt.
- [Trigger-Skills vs. Hooks vs. Dispatch]—internes Design-Muster, noch nicht in `spec/claude/` kodifiziert; unter §Offene Fragen festgehalten.
