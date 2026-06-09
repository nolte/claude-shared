# `Lektorat Auto-Revise`

Status: draft

## Kontext

[`spec/project/lektorat/`](../lektorat/de.md) definiert die Lektorats-Schicht: ein `audit` erzeugt einen strukturierten Findings-Report (D1–D6, severity-klassifiziert, audience-gebunden), ein `patch` wendet pro Operator-Freigabe ein Finding an, und ein `revise` schreibt ein vollständiges Artefakt hinter einem Operator-Diff-Gate um. Alle drei mutierenden Pfade haben bei jedem Schreibvorgang einen Menschen in der Schleife, und `revise` führt den Rewrite **innerhalb der `lektorat-apply`-Skill selbst** aus – ein generischer, lexikalischer Rewrite ohne audience-spezifisches Tiefenmodell und ohne Bindung an die Schreibstil-Specs, die ein Author konsultieren würde.

Was fehlt, ist die **autonome Brücke** vom bestehenden Audit-Report zum fertigen, re-verifizierten Artefakt, bei der der Rewrite vom **für den Artefakttyp am besten geeigneten Author** ausgeführt wird – dem Author, dessen eigener Vertrag bereits das Lesen des Audience-Artefakts und der Schreibstil-Spec vorschreibt, sodass *Stil*- und *Audience-Fit*-Konformität strukturell statt re-implementiert ist. Der `audience-doc-author`-Agent nimmt das bereits vorweg: Er benennt eine *„future orchestrating skill"* als Treiber, der seinen fire-and-forget-Executor-Vertrag in eine geschlossene Schleife verwandelt. `Lektorat Auto-Revise` ist dieser Treiber.

Die Schicht ist **operativ**: Sie schreibt einen Prozess vor – einen Audit-Report konsumieren, jedes betroffene Artefakt an den passenden Author routen, ein Per-Artefakt-Briefing komponieren, den Author revidieren lassen, dann re-auditieren bis das Artefakt konvergiert – mit expliziten Vor- und Nachbedingungen, sodass eine nachgelagerte Skill den Vertrag implementieren kann, ohne die Semantik neu zu verhandeln. Sie besitzt **keine** eigenen Lektorats-Regeln: Severities, Dimensionen, Scope, Audience-Binding und Semantik-Erhaltungs-Garantien gehören alle zu `lektorat`; die Schreibstil- und Audience-Regeln gehören zu den gebundenen Specs der Author. Diese Spec definiert nur die **Orchestrierung**, die sie zusammenschaltet, und die **maschinelle Verifikation** (Re-Audit), die das menschliche Per-Finding-Gate ersetzt.

**Leser** dieser Spec sind Implementoren der `lektorat-auto-revise`-Skill (primär) und Operatoren, die eine autonome Lektorats-Remediation aus einem Sprint-Review, einem Release-Gate oder einem manuellen Aufräum-Durchlauf anstoßen (sekundär). Vertrautheit mit [`spec/project/lektorat/`](../lektorat/de.md) (Findings-Report, Severities, Audience-Binding, Semantik-Erhaltungs-Garantien), [`spec/project/audience-identification/`](../audience-identification/de.md) (das Audience-Artefakt), [`spec/project/prose-style/`](../prose-style/de.md) (EN Voice/Tone) und dem Blog-seitigen Paar [`spec/project/post-writing-style/`](../post-writing-style/de.md) und [`spec/project/post-audience-communication/`](../post-audience-communication/de.md) wird vorausgesetzt; Begriffe aus diesen Specs werden ohne Wiederholung verwendet.

## Ziele

- Ein bestehender `lektorat audit`-Findings-Report kann **automatisch** abgearbeitet werden, ohne einen Per-Finding-Freigabezyklus durch einen Menschen, sodass die Lektorats-Remediation über das hinaus skaliert, was manuelles `patch` / `revise` erlaubt
- Jedes betroffene Artefakt wird an den **passenden Author** nach Artefakttyp geroutet, sodass der Rewrite von der Komponente ausgeführt wird, deren Vertrag bereits die relevanten Schreibstil- und Audience-Specs bindet
- **Schreibstil und Audience-Fit sind zwingend**, nicht advisory: Der Prozess verweigert das Dispatchen jedes Authors ohne aufgelöste Audience-Menge und gebundene Schreibstil-Spec, sodass Stil- und Audience-Konformität strukturell garantiert ist
- Die autonome Schleife ist **maschinell verifiziert**: Ein Re-Audit bestätigt, dass das Artefakt konvergiert ist (keine verbleibenden Findings auf oder über dem Severity-Floor, keine Regression), bevor der Lauf als fertig markiert wird, und ersetzt damit das menschliche Diff-Gate durch eine reproduzierbare Prüfung
- Die Abgrenzung gegen `lektorat` (die Regeln, die Findings, die `patch` / `revise`-Operationen), `audience-doc-author` und `blog-author` (erstklassige Autorenschaft) und `audience-identification` / `prose-style` / `post-writing-style` / `post-audience-communication` (die Regelquellen) ist scharf genug, dass keine Anforderung in zwei Specs wiederholt wird
- Der Dokumentations-Pfad läuft **vollautonom**; der Blog-Pfad läuft **assistiert** und erhält den einen interaktiven Briefing-Touchpoint, den der Skill-Vertrag von `blog-author` verlangt, sodass die Spec ehrlich über den Unterschied zwischen einem dispatchbaren Agent und einer interaktiven Skill ist

## Nicht-Ziele

- Findings, Severities (`critical` / `warning` / `suggestion`) oder die sechs Qualitätsdimensionen (D1–D6) definieren, neu klassifizieren oder neu gewichten – alle im Besitz von [`spec/project/lektorat/`](../lektorat/de.md); `Lektorat Auto-Revise` konsumiert den Findings-Report und **DARF NICHT [MUST NOT]** irgendein Feld davon neu definieren
- Die Lektorats-**Detektion** selbst durchführen – der Input ist ein Findings-Report aus einem vorherigen `lektorat audit`; diese Spec re-implementiert den Scan nie, sie konsumiert dessen Output und ruft ihn für die Konvergenzprüfung erneut auf
- Erstautorenschaft neuer Artefakte – im Besitz des `audience-doc-author`-Agents und der `blog-author`-Skill; diese Schicht treibt nur die **Revision bereits existierender Artefakte**, die bereits Findings tragen
- Die Schreibstil-Regeln (EN Voice/Tone, Blog-Verbotswortliste, bilinguale Typografie) oder das Audience-Modell definieren – im Besitz von `prose-style`, `post-writing-style`, `post-audience-communication` und `audience-identification`; der Prozess bindet diese Specs **über den dispatchten Author**, er wiederholt sie nicht
- Die `patch`- und `revise`-Operationen von `lektorat` ersetzen – diese bleiben die **interaktiven, menschlich-gegateten** Remediations-Pfade für Fälle, die ein Operator von Hand treiben will; `Lektorat Auto-Revise` ist die autonome, author-geroutete Alternative, und ein Repository **KANN [MAY]** beide verwenden
- Den Lektorats-Scope erweitern: Artefaktklassen, die `lektorat` §Scope and applicability ausschließt (Dateien unter `spec/`, `skills/**/SKILL.md`, `skills/**/templates/**`, `skills/**/examples/**`, `agents/*.md`, Quellcode, generierte Konfiguration), werden **nie** an einen Author geroutet und hier **hart abgewiesen**, genau wie `lektorat` sie upstream verbietet
- Übersetzung oder sprachübergreifende Parität – im Besitz von `spec`, `docs-multilingual-authoring` und `docs-freshness`; jedes Artefakt wird in seiner eigenen Sprache von einem Author revidiert, der in dieser Sprache arbeitet

## Anforderungen

### Input-Vertrag

- **MUSS [MUST]** einen **abgeschlossenen `lektorat audit`-Findings-Report** als Input nehmen: entweder einen Pfad zu einer bestehenden `.audits/lektorat/<YYYY-MM-DD-HHMM>/findings.json` oder eine Direktive, zuerst einen frischen `audit` (via `lektorat-apply`) zu fahren und dessen Output zu konsumieren. Die Form des Reports ist die in [`spec/project/lektorat/`](../lektorat/de.md) §Outputs deklarierte; diese Spec konsumiert sie verbatim und **DARF NICHT [MUST NOT]** ein Feld hinzufügen, weglassen oder umbenennen
- **MUSS [MUST]** nur Einträge im `findings`-Array des Reports verarbeiten. Einträge in `inventory_findings` beschreiben Infrastruktur-Bedingungen, die einen Teil des Scans am Abschluss hinderten; für jede in einem `inventory_findings`-Eintrag benannte Datei **DARF** der Prozess **NICHT [MUST NOT]** einen Author dispatchen (ein ungescanntes Artefakt lässt sich nicht sicher revidieren) und **MUSS [MUST]** die Bedingung dem Operator anzeigen
- **MUSS [MUST]** den **Severity-Floor** des Input-Laufs honorieren: standardmäßig adressiert er jedes `critical`- und `warning`-Finding und **SOLLTE [SHOULD]** `suggestion`-Findings nur adressieren, wenn das den Rewrite-Scope nicht erweitert, analog zu `lektorat` §Operation C. Ein Repository **KANN [MAY]** den Floor für einen entrauschten autonomen Durchlauf auf `critical` verengen
- **MUSS [MUST]** das `findings`-Array **nach `file`** gruppieren, bevor geroutet wird, sodass jedes einzelne Artefakt einmal mit der vollständigen Menge seiner Findings behandelt wird, unabhängig davon, wie die Findings im Report sortiert waren

### Artefakttyp-Routing

- **MUSS [MUST]** jede einzelne `file` in den Findings in **genau eine** Routing-Klasse klassifizieren, bevor ein Author dispatcht wird. Die Klassen und ihre Auflösung sind:

  | Routing-Klasse | Erkennungssignal | Dispatchter Author |
  | --- | --- | --- |
  | `documentation` | MkDocs-Seite unter `docs/<lang>/`, oder Top-Level-Repository-Markdown (`README.md`, `ONBOARDING.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `SECURITY.md`), oder ein GitHub-Release-/Issue-/Pull-Request-Body; identifiziert über den Pfad plus, für MkDocs-Seiten, das `track` / `content_mode`-Frontmatter aus `docs-audience-tracks` | `audience-doc-author`-Agent |
  | `blog-post` | ein Post-Paar-Artefakt, das den sprachübergreifenden Bindungsschlüssel des Consumers (Referenz: `translationKey`) im Frontmatter trägt, am vom Consumer deklarierten Blogpost-Ort (Referenz: `nolte/blog`) | `blog-author`-Skill |
  | `rejected` | jeder Pfad, den `lektorat` §Scope and applicability ausschließt (unter `spec/`, `skills/**/SKILL.md`, `skills/**/templates/**`, `skills/**/examples/**`, `agents/*.md`, Quellcode, generierte Konfiguration, Binaries) | keiner – **hart abweisen** |

- **MUSS [MUST]** **pro Datei** routen: ein Findings-Report, der sowohl Dokumentations- als auch Blog-Artefakte umspannt, fächert auf beide Author auf, wobei jeder nur die Dateien seiner Klasse behandelt
- **MUSS [MUST]** jede `rejected`-Klassen-Datei mit einer Ein-Satz-Meldung hart abweisen, die den zuständigen Autoren-Flow benennt (die `spec`-Skill für `spec/`, `skill-management` / `agent-management` für LLM-Instruktions-Artefakte), und **DARF NICHT [MUST NOT]** einen Author daran dispatchen. Eine solche Datei sollte diesen Prozess nie erreichen (ein konformer `lektorat audit` schließt sie bereits aus), aber die Abweisung ist eine defensive Invariante, keine Annahme
- **MUSS [MUST]** den ganzen Lauf mit einer Operator-Meldung anhalten, wenn eine Datei **keiner** der drei Klassen entspricht (ein in-scope Artefakttyp, den diese Spec noch nicht routet); ihn still zu überspringen würde unremediierte Findings verbergen
- **DARF NICHT [MUST NOT]** die Routing-Tabelle auf eine Klasse erweiterbar machen, die `lektorat` verbietet; ein Repository **KANN [MAY]** eine neue Routing-Klasse nur durch Änderung dieser Spec hinzufügen, genau wie `lektorat` seinen Scope gatet

### Komposition des Author-Briefings

- **MUSS [MUST]** für jede geroutete Datei ein **Briefing** komponieren, das der dispatchte Author erhält und das alles davon enthält:
  1. die **Teilmenge der Findings** für diese Datei, verbatim aus dem Input-Report (Severity, Dimension, Zeilenbereich, Message, `rule`, `audience`, `evidence`, `suggested_resolution`)
  2. die **aufgelöste Audience-Menge** der Datei, gewonnen über die **gleiche Prioritätskette** wie `lektorat` §Audience binding (Frontmatter `audience:` → Artefakttyp-Defaults → ganze Audience-Menge); dieser Prozess **DARF NICHT [MUST NOT]** Audiences nach einer anderen Regel auflösen
  3. die **gebundene(n) Schreibstil-Spec(s)** für den Pfad (siehe §Zwingende Stil- und Audience-Bindung)
  4. die **Ziel-Dimensionen** – die einzelnen D1–D6-Werte in den Findings der Datei – sodass der Author weiß, welche Lektorats-Achsen die Revision bewegen muss
  5. für jede Datei mit einem **D1-Lesbarkeits-Finding** die **LIX-Ziel-Inputs** gemäß [`spec/project/readability-lix/`](../readability-lix/de.md) §Iterative Verbesserungsschleife: den aktuellen `lix`, den aufgelösten Korridor (`aim` / `warn` / `crit` für `content_mode` und Sprache der Datei) und den **dominanten Hebel** (`ASL` oder `LWP`) – sodass der Durchlauf des Authors auf den richtigen Lesbarkeits-Hebel (Sätze teilen versus lange Wörter kürzen) gerichtet ist, statt blind umzuschreiben
- **MUSS [MUST]** das **Audience-Artefakt** von seinem kanonischen Ort lesen, genau wie `lektorat` §Audience binding vorschreibt, und **MUSS [MUST]** die **Per-Datei**-Remediation (nicht den ganzen Lauf) mit derselben Operator-Meldung anhalten, die auf die `audience-identify`-Skill zeigt, wenn das Artefakt fehlt; der Prozess **DARF NICHT [MUST NOT]** Audiences erfinden und **DARF NICHT [MUST NOT]** einen Author ohne aufgelöste Audience-Menge dispatchen
- **MUSS [MUST]** das Briefing in einer Form übergeben, die der Input-Vertrag des dispatchten Authors akzeptiert: für `audience-doc-author` den Audience-Artefakt-Pfad, die Doc-Type-Spec, die `prose-style`-Baseline und das Quellmaterial (die zu revidierende Datei); für `blog-author` die Briefing-Inputs, die sein Skill-Vertrag verlangt (siehe §Autonomie und menschliche Touchpoints zur Regel des assistierten Touchpoints)

### Zwingende Stil- und Audience-Bindung

- **MUSS [MUST]** die **Schreibstil-Spec** pro Routing-Klasse binden und **DARF NICHT [MUST NOT]** einen Author ohne sie dispatchen:
  - `documentation` → [`spec/project/prose-style/`](../prose-style/de.md) (plus die Doc-Type-Spec, die der `audience-doc-author`-Vertrag auflöst, z. B. `readme-structure`, `release-notes-audience-analysis`)
  - `blog-post` → [`spec/project/post-writing-style/`](../post-writing-style/de.md) und [`spec/project/post-audience-communication/`](../post-audience-communication/de.md)
- **MUSS [MUST]** den Author dispatchen, dessen **eigener Vertrag bereits das Konsultieren** dieser Specs vorschreibt, sodass Schreibstil- und Audience-Fit-Konformität durch den Vertrag des Authors erzwungen wird statt hier nachgeprüft zu werden; dieser Prozess **DARF NICHT [MUST NOT]** eine parallele Kopie irgendeiner Stil- oder Audience-Regel führen
- **DARF NICHT [MUST NOT]** Prosa selbst umschreiben. Der Rewrite wird **immer** an den gerouteten Author delegiert, genau damit das Audience-Tiefenmodell und die Schreibstil-Kompetenz des Authors greifen; ein generischer Orchestrator-interner Rewrite ist das, was `lektorat` §Operation C bereits bietet, und ist explizit **nicht** Aufgabe dieser Schicht
- **MUSS [MUST]** einen fehlenden **der beiden** Inputs – aufgelöste Audience-Menge **oder** gebundene Schreibstil-Spec – als Per-Datei-**Stopp-Bedingung** behandeln, nie als weichen Default; „keine Audience" und „keine Stil-Spec" sind keine Zustände, in denen ein Author laufen darf

### Autonomie und menschliche Touchpoints

- **MUSS [MUST]** den `documentation`-Pfad **vollautonom** fahren: keine Per-Finding-Freigabe, kein menschliches Diff-Gate. Der dispatchte `audience-doc-author`-Agent editiert das Artefakt in-place; Korrektheit wird durch das §Re-Audit-Konvergenz-Gate verifiziert, nicht durch einen Menschen
- **MUSS [MUST]** den `blog-post`-Pfad **assistiert** fahren: `blog-author` ist eine interaktive Skill, deren Vertrag Briefing-Inputs verlangt (Topic-as-Thesis, fundiertes Artefakt, Primary Audience, Quellliste, Slug, sprachübergreifender Bindungsschlüssel), die sich nicht allein aus Findings rekonstruieren lassen. Der Prozess **MUSS [MUST]** das aus den Findings abgeleitete Briefing dieser Skill vorlegen und **DARF NICHT [MUST NOT]** die Briefing-Inputs erfinden, die sie verlangt; der Operator liefert, was der bestehende Post und die Findings nicht hergeben
- **MUSS [MUST]** pro Datei aufzeichnen, ob der Pfad `autonomous` oder `assisted` lief (§Outputs), sodass ein Leser des Audit-Trails genau sieht, wo ein Mensch in der Schleife war
- **KANN [MAY]** als getrackte zukünftige Erweiterung einen vollautonomen Blog-Pfad gewinnen, sobald `blog-author` (oder ein Geschwister) einen findings-getriebenen Update-Modus bereitstellt, der kein interaktives Briefing braucht; bis dahin ist der obige assistierte Vertrag bindend (siehe §Offene Fragen)

### Semantik-Erhaltung

- **MUSS [MUST]** vom dispatchten Author verlangen, semantischen Inhalt unter den **gleichen Garantien** zu erhalten, die `lektorat` §Operation C `revise` und §Refactor safety vorschreiben: jede Tatsache, Behauptung, jeder Befehl, Identifier, jedes Link-Ziel, jeder Frontmatter-Schlüssel, Code-Block, jedes blockzitierte Zitat (`> …`) und jeder HTML-Kommentar-Marker des Original-Artefakts wird byte-identisch erhalten, mit höchstens lexikalischer Änderung; kein Listenpunkt, keine Tabellenzeile, kein Checklisten-Eintrag wird umgeordnet, zusammengeführt oder entfernt; kein neuer faktischer Inhalt (Befehle, Dateipfade, Produktnamen, URLs), der im Original fehlt, wird eingeführt. Dieser Prozess **DARF NICHT [MUST NOT]** eine dieser Bedingungen lockern und **DARF NICHT [MUST NOT]** sie wiederholen – die maßgebliche Liste liegt in `lektorat`
- **MUSS [MUST]** jede Author-Revision, die eine Semantik-Erhaltungs-Garantie verletzt, als **fehlgeschlagenen Durchlauf** für diese Datei behandeln, sie dem Operator anzeigen und den Rewrite **DARF NICHT [MUST NOT]** als konvergiert auf Disk akzeptieren

### Re-Audit-Konvergenz-Gate

- **MUSS [MUST]** nach Abschluss einer Datei durch den Author den **`lektorat audit` erneut** auf dem revidierten Artefakt mit der **gleichen Konfiguration** wie der Input-Lauf fahren (Severity-Floor, Audience-Artefakt, Sprach-Pipeline)
- **MUSS [MUST]** eine Datei nur dann als **konvergiert** behandeln, wenn **beides** gilt:
  1. **kein verbleibendes Finding** auf oder über dem Severity-Floor für diese Datei, **und**
  2. **keine Regression** – die Gesamtzahl der Findings nach der Revision für die Datei ist **kleiner oder gleich** der Zahl vor der Revision (spiegelt `lektorat` §Operation C Regressions-Detektion)
- **DARF NICHT [MUST NOT]** eine Datei als fertig markieren und den Lauf als abgeschlossen behandeln, bevor jede geroutete (nicht abgewiesene) Datei konvergiert oder eskaliert ist
- **MUSS [MUST]** bei Nicht-Konvergenz einer Datei den Author mit den **Rest-Findings** für eine **begrenzte** Anzahl von Author-Durchläufen erneut dispatchen (**Default: 2** Durchläufe pro Datei); nach Erreichen der Grenze **MUSS [MUST]** der Prozess die Rest-Findings an den Operator eskalieren und **DARF NICHT [MUST NOT]** weiter schleifen. Die Grenze und die Eskalation sind tragend: eine autonome Schleife ohne Deckel ist verboten
- **MUSS [MUST]** eine **Regression** (Zahl nach Revision höher als vor Revision) dem Operator anzeigen und einen regressierten Rewrite **DARF NICHT [MUST NOT]** automatisch als konvergiert akzeptieren, selbst wenn er den Severity-Floor unterschritten hat
- **MUSS [MUST]** ein **D1-Lesbarkeits-Finding** erst dann als konvergiert behandeln, wenn das Re-Audit den LIX der Datei auf oder unter ihrem aufgelösten `warn`-Korridor zeigt, gemäß [`spec/project/readability-lix/`](../readability-lix/de.md) §Iterative Verbesserungsschleife; ein Re-Audit, in dem LIX von über `warn` auf oder unter `warn` rückt, ist Fortschritt, ein Re-Audit, in dem LIX steigt, ist eine Regression, und ein Durchlauf, der LIX über eine von `readability-lix` §Einen LIX-Wert verbessern verbotene Transformation gesenkt hat (ein etabliertes Kompositum dekomponieren, einen präzisen Begriff gegen ein vageres kürzeres tauschen, einen geschützten Begriff verändern), wird von den §Bedeutungserhaltungs-Garantien gefangen und ist ein **fehlgeschlagener Durchlauf**, niemals Konvergenz
- **MUSS [MUST]** pro Datei die Zahl vor Revision, die Zahl nach Revision, die Anzahl der Author-Durchläufe und den Endstatus (`converged` / `regressed` / `escalated`) im Output aufzeichnen

### Outputs

- **MUSS [MUST]** einen Lauf-Trail unter `.audits/lektorat-auto-revise/<YYYY-MM-DD-HHMM>/` schreiben (spiegelt die `.audits/lektorat/`-Konvention von `lektorat`), enthaltend:
  - `routing.json` – pro Datei: die Routing-Klasse, das Erkennungssignal, das sie auflöste, und den dispatchten Author (oder den Abweisungsgrund)
  - `run.json` – den konsumierten Quell-Audit-Lauf (Pfad zur Input-`findings.json`), den aufgelösten Severity-Floor und den aufgelösten Audience-Artefakt-Pfad
  - pro konvergierter oder eskalierter Datei: das **Unified-Diff** des Author-Rewrites, die Findings-Zahlen vor und nach Revision, die Author-Durchlauf-Zahl und den Endstatus
  - `summary.md` – eine menschenlesbare, severity-sortierte Zusammenfassung, die pro Datei den Pfad (`autonomous` / `assisted`), den Endstatus und etwaige eskalierte Rest-Findings benennt
- **MUSS [MUST]** den **Quell-`lektorat audit`-Lauf** referenzieren, den er konsumiert hat, sodass die autonome Remediation auf den auslösenden Audit zurückführbar ist
- **MUSS [MUST]** jede **eskalierte Rest**-Datei und jede **regressierte** Datei in `summary.md` unübersehbar machen (zuerst gelistet, vor den konvergierten Dateien); unremediierte Findings still abzuschneiden ist verboten
- Die `.audits/lektorat-auto-revise/`-JSON ist der **Vertrag**; sie als CI- oder Pull-Request-Annotationen zu rendern ist eine nachgelagerte Entscheidung außerhalb des Scopes hier, konsistent damit, wie `lektorat` und die anderen Audit-Specs ihren On-Disk-Trail als das Liefergut behandeln

### Skill- und Agent-Verteilung (Empfehlung)

Die Spec lässt die Implementierungs-Form **offen**, **SOLLTE [SHOULD]** aber als eine einzelne orchestrierende Skill implementiert werden, das Hybrid-Muster des Portfolios spiegelnd:

- **`lektorat-auto-revise`-Skill** – der Orchestrator und die einzige neue Komponente. Sie konsumiert den Audit-Report, klassifiziert das Routing, komponiert Briefings, dispatcht den bestehenden `audience-doc-author`-Agent (Dokumentations-Pfad) und die bestehende `blog-author`-Skill (Blog-Pfad), fährt den `lektorat audit` für das Konvergenz-Gate erneut, besitzt den assistierten Blog-Operator-Touchpoint und schreibt den `.audits/lektorat-auto-revise/`-Trail. Sie ist eine **Skill**, kein Agent, weil der interaktive Briefing-Touchpoint des Blog-Pfads und der persistente On-Disk-Audit-Trail beide tragend sind – der fire-and-forget-Vertrag eines Agents würde den Dialog und die Orchestrierungsrolle verlieren
- Die Skill **DARF NICHT [MUST NOT]** einen neuen Scanner einführen; das Konvergenz-Re-Audit nutzt den bestehenden `lektorat`-Audit-Pfad (`lektorat-apply` / `lektorat-scanner`) wieder, sodass es genau eine Lektorats-Detektions-Implementierung im Portfolio gibt

### Koordination mit benachbarten Specs

- **MUSS [MUST]** [`spec/project/lektorat/`](../lektorat/de.md) als maßgebliche Quelle der Findings-Report-Form, der Severities, Dimensionen, des Scopes, des Audience-Bindings und der Semantik-Erhaltungs-Garantien referenzieren; `Lektorat Auto-Revise` konsumiert sie und **DARF NICHT [MUST NOT]** sie neu definieren
- **MUSS [MUST]** [`spec/project/audience-identification/`](../audience-identification/de.md) als maßgebliche Quelle der Audience-Identifier und -Eigenschaften referenzieren; der Prozess liest das Artefakt und **DARF NICHT [MUST NOT]** Audiences erfinden
- **MUSS [MUST]** [`spec/project/prose-style/`](../prose-style/de.md) (Dokumentations-Pfad) und [`spec/project/post-writing-style/`](../post-writing-style/de.md) + [`spec/project/post-audience-communication/`](../post-audience-communication/de.md) (Blog-Pfad) als maßgebliche Schreibstil-Regeln referenzieren, über den dispatchten Author gebunden und hier nie wiederholt
- **DARF NICHT [MUST NOT]** irgendein in den obigen Specs deklariertes MUST überschreiben, lockern oder duplizieren; Konflikte werden durch Änderung der Upstream-Spec gelöst, nicht durch eine Ausnahme in `Lektorat Auto-Revise`

## Akzeptanzkriterien

- [ ] Ein Lauf nimmt eine `lektorat audit`-`findings.json` als Input und konsumiert ihr `findings`-Array, ohne ein Feld des Reports hinzuzufügen, wegzulassen oder umzubenennen
- [ ] Eine in einem `inventory_findings`-Eintrag des Input-Reports benannte Datei wird **nicht** an einen Author geroutet, und die Infrastruktur-Bedingung wird dem Operator angezeigt
- [ ] Das `findings`-Array wird nach `file` gruppiert, sodass jedes Artefakt einmal mit der vollständigen Menge seiner Findings behandelt wird
- [ ] Ein Dokumentations-Artefakt (MkDocs-Seite oder Top-Level-Markdown) wird an `audience-doc-author` geroutet; ein Blogpost-Artefakt (das den sprachübergreifenden Bindungsschlüssel des Consumers trägt) wird an `blog-author` geroutet; Routing-Klasse und dispatchter Author werden in `routing.json` aufgezeichnet
- [ ] Eine Datei unter `spec/`, `skills/**/SKILL.md`, `skills/**/templates/**`, `skills/**/examples/**` oder `agents/*.md` wird mit einer Meldung, die den zuständigen Autoren-Flow benennt, hart abgewiesen, und kein Author wird daran dispatcht
- [ ] Eine Datei, die keiner der drei Routing-Klassen entspricht, hält den Lauf mit einer Operator-Meldung an, statt still übersprungen zu werden
- [ ] Jeder dispatchte Author erhält ein Briefing, das die Findings der Datei, die aufgelöste Audience-Menge, die gebundene(n) Schreibstil-Spec(s) und die Ziel-Dimensionen D1–D6 enthält
- [ ] Die Audience-Menge wird über die Prioritätskette `lektorat` §Audience binding aufgelöst (Frontmatter → Artefakttyp-Default → ganze Menge), identisch zu einem eigenständigen `lektorat audit`
- [ ] Wenn das Audience-Artefakt fehlt, hält die Per-Datei-Remediation mit der auf `audience-identify` zeigenden Meldung an, und kein Author wird dispatcht
- [ ] Kein Author wird ohne sowohl aufgelöste Audience-Menge als auch gebundene Schreibstil-Spec dispatcht; ein fehlender der beiden ist eine Per-Datei-Stopp-Bedingung
- [ ] Der Prozess schreibt Prosa nie selbst um; jeder Rewrite wird vom gerouteten Author ausgeführt (aus dem Audit-Trail überprüfbar, der pro Datei den Author ausweist)
- [ ] Der Dokumentations-Pfad läuft ohne jede Per-Finding-Freigabe oder menschliches Diff-Gate; der Audit-Trail zeichnet den Pfad als `autonomous` auf
- [ ] Der Blog-Pfad legt `blog-author` das aus den Findings abgeleitete Briefing vor, erhält dessen interaktiven Briefing-Touchpoint, erfindet die von `blog-author` verlangten Briefing-Inputs nicht und zeichnet den Pfad als `assisted` auf
- [ ] Eine Author-Revision, die einen Code-Block, Listenpunkt, eine Tabellenzeile, einen Checklisten-Eintrag, ein Link-Ziel, einen Frontmatter-Schlüssel, ein Zitat oder einen HTML-Kommentar entfernt, oder die einen neuen Befehl/Pfad/Produktnamen/eine URL einführt, der/die im Original fehlt, wird als fehlgeschlagener Durchlauf behandelt und nicht als konvergiert akzeptiert
- [ ] Nach jedem Author-Durchlauf wird der `lektorat audit` auf dem revidierten Artefakt mit der gleichen Konfiguration wie der Input-Lauf erneut gefahren
- [ ] Eine Datei wird nur dann als konvergiert markiert, wenn sie kein verbleibendes Finding auf oder über dem Severity-Floor hat **und** die Findings-Zahl nach Revision ≤ der Zahl vor Revision ist
- [ ] Eine Datei, deren Findings-Zahl nach Revision die Zahl vor Revision übersteigt, wird als Regression an den Operator gemeldet und nicht automatisch als konvergiert akzeptiert
- [ ] Eine Datei, die innerhalb der begrenzten Anzahl von Author-Durchläufen (Default 2) nicht konvergiert, hat ihre Rest-Findings an den Operator eskaliert, und die Schleife läuft nicht über die Grenze hinaus weiter
- [ ] Der Lauf schreibt `routing.json`, `run.json`, Per-Datei-Rewrite-Diffs mit Vor-/Nach-Zahlen und Durchlauf-Zahl sowie `summary.md` unter `.audits/lektorat-auto-revise/<YYYY-MM-DD-HHMM>/` und referenziert den Quell-Audit-Lauf
- [ ] `summary.md` listet eskalierte und regressierte Dateien vor konvergierten Dateien, sodass unremediierte Findings nicht übersehen werden können

## Offene Fragen

- Soll der **Blog-Pfad** vollautonom werden, sobald ein findings-getriebener `blog-author`-Update-Modus existiert, der kein interaktives Briefing braucht? Default heute: **assistiert**, weil der Skill-Vertrag von `blog-author` Briefing-Inputs verlangt (Topic-as-Thesis, Quellliste, Slug, sprachübergreifender Bindungsschlüssel), die sich nicht allein aus Lektorats-Findings rekonstruieren lassen. Neu bewerten, wenn `blog-author` (oder eine Geschwister-Skill/-Agent) eine dokumentierte findings-getriebene Update-Operation bereitstellt, deren Inputs vollständig aus dem bestehenden Post plus dem Findings-Report ableitbar sind; das zu beobachtende Upstream-Signal ist eine `blog-author`-Revision, die eine solche Operation hinzufügt.
- Soll der **Author-Durchlauf-Deckel** der Konvergenz-Schleife (Default 2) pro Repository einstellbar sein, und soll ein wiederholt eskalierendes Artefakt ein `continuous-improvement`-Signal speisen? Default: ein fixer Deckel von 2 mit Operator-Eskalation, der einfachste Deckel, der eine unbegrenzte Schleife verhindert. Neu bewerten, wenn akkumulierte `.audits/lektorat-auto-revise/`-Daten eine wiederkehrende Klasse von Artefakten zeigen, die bei jedem Lauf eskalieren (ein Zeichen, dass der Deckel falsch ist oder die Findings strukturell nicht durch einen Author behebbar sind).
- Soll diese Schicht je Findings für **Blogposts** konsumieren, die `lektorat` unter einer consumer-seitigen Scope-Erweiterung erzeugt hat, angesichts dessen, dass `lektorat` §Scope and applicability (in diesem Repository) Blogposts nicht listet? Default: der Prozess ist **repository-agnostisch** und konsumiert jede konforme `findings.json`, die ihm gereicht wird, wie auch immer der Upstream-`lektorat`-Lauf sie erzeugte (im Blog-Consumer reicht `blog-author` Schritt 7 bereits an `lektorat-apply` weiter). Neu bewerten, falls der `lektorat`-Scope des Blog-Consumers und der Blog-Pfad dieser Schicht je darüber uneins werden, welche Blog-Artefakte in-scope sind.

## Quellen

<!-- Maßgebliche externe Referenzen, gegen die die obigen Anforderungen validiert wurden. -->

- [`spec/project/lektorat/`](../lektorat/de.md) – die Findings-Report-Form, Severity-Klassifikation, das Audience-Binding, die Operationen (`audit` / `patch` / `revise`) und Semantik-Erhaltungs-Garantien, die diese Schicht orchestriert.
- [`spec/project/audience-identification/`](../audience-identification/de.md) – das Audience-Artefakt und Identifier-Modell, gegen das die Briefing-Komposition auflöst.
- [`spec/project/prose-style/`](../prose-style/de.md) – die EN-Voice/Tone-Regeln, auf dem Dokumentations-Pfad über `audience-doc-author` gebunden.
- [`spec/project/post-writing-style/`](../post-writing-style/de.md) und [`spec/project/post-audience-communication/`](../post-audience-communication/de.md) – die Schreibstil- und Audience-Regeln, auf dem Blog-Pfad über `blog-author` gebunden.
- Der Vertrag des `audience-doc-author`-Agents (`agents/audience-doc-author.md`), der eine *„future orchestrating skill"* als seinen Treiber benennt – die Rolle, die diese Spec definiert.
