# Frontend-Testbarkeit: Stabile Test-Identifikatoren

Status: draft

## Kontext

Ein End-to-End-Test kann nur vertrauenswürdig sein, wenn die Oberfläche, die er ansteuert, adressierbar ist: Jedes test-relevante Element und jede Seite muss einen stabilen, eindeutigen Identifikator bereitstellen, über den ein Test selektieren kann. Das ist die **Bereitstellungsseite** der Testbarkeit, und es ist Anwendungsarbeit — keine Testarbeit. `spec/project/e2e-test-automation/` regelt die **Konsumentenseite** (wie eine Suite *selektiert*: die Locator-Robustheitshierarchie, Page-Objects, bedingungsbasiertes Warten) und klammert die Bereitstellung bewusst *aus*: Ihre Nicht-Ziele nennen „das Generieren von Produktions-Anwendungscode oder `data-testid`-Hooks in der zu testenden Anwendung (die Suite *stützt sich auf* solche Hooks; sie hinzuzufügen ist Anwendungsarbeit)". Diese Spec beansprucht genau diese ausgeklammerte Anwendungsarbeit als ihr Thema. Die beiden Specs sind Konsumenten-/Provider-Geschwister: die eine normt, wie Tests selektieren, diese normt, was das Frontend bereitstellen muss.

Der wiederverwendbare Teil der Bereitstellung ist framework-unabhängig: die *Pflicht*, test-relevante Elemente zu markieren, der *Stabilitätsvertrag*, der diese Markierungen vor stillem Bruch bewahrt, das *Namensschema*, das sie vorhersagbar hält, und die Regel, dass wiederholte Sammlungen über einen Business-Key statt über eine Position adressierbar bleiben. Der wegwerfbare Teil ist der Mechanismus — welches Attribut den Identifikator in einer gegebenen Technologie trägt. Diese Spec formuliert die Pflicht framework-neutral als bindenden Kern und fixiert dann ein konkretes, voll ausgearbeitetes **Web-Referenzprofil** (`data-testid` im DOM) als normativen Abschnitt, sodass ein Web-Projekt einen sofort einsatzbereiten Default erhält, während andere Stacks denselben Kern umsetzen.

Der Inhalt ist aus dem kamerplanter-Standard `UI-NFR-022` (`R-001..R-025`) verallgemeinert und de-domänisiert: Die pflanzenspezifischen `species-*`-Beispiele werden zu `<entity>-*`-Platzhaltern, damit die Regeln portfolio-weit statt als Konvention einer einzelnen App lesbar sind.

Leser: Frontend-Entwickler, die eine Portfolio-UI bauen oder umgestalten (Zielgruppe `nolte-engineering`); die UX-/Usability-Rolle, die einen bestehenden Presentation-Layer editiert; Reviewer, die verifizieren, dass ein Diff die Oberfläche adressierbar hält. Sie wird im Gleichschritt mit den Frontend-Build- und UX-Agents operationalisiert, die sie konsumieren (`fullstack-developer`, `frontend-usability-optimizer`, `webview-ui-expert`).

## Ziele

- Die Bereitstellungspflicht einmal, framework-neutral, als bindenden Kern formulieren, den jedes konsumierende Frontend erfüllen muss, damit seine Oberfläche für eine E2E-Suite adressierbar ist.
- Den Kern auf jedem UI-Stack umsetzbar halten, indem das konkrete Träger-Attribut zu einem austauschbaren Referenzprofil statt zu einer Anforderung herabgestuft wird.
- Ein voll ausgearbeitetes, normatives **Web-Referenzprofil** (`data-testid`, DOM) mitliefern, sodass ein Web-Projekt sofort produktiv ist.
- Identifikatoren zu einem Stabilitätsvertrag machen: deterministisch, über ein Namensschema vorhersagbar, über Element-Zustände stabil und niemals still umbenannt oder entfernt.
- Nicht nur Frontend-Implementierer binden, sondern auch die UX-/Usability-Rolle, sodass eine Usability-Änderung die Identifikatoren, von denen ein Test abhängt, erhält statt zu brechen.
- Das Konsumenten-Geschwister (`e2e-test-automation` §Locator-Strategie) referenzieren, damit Provider und Konsument ein zusammenpassendes Paar bleiben.

## Nicht-Ziele

- Das **Selektieren** über diese Identifikatoren in einer Testsuite — die Locator-Robustheitshierarchie, die Page-Object-Kapselung und die Wartedisziplin gehören `spec/project/e2e-test-automation/` §Locator-Strategie (dem Konsumenten-Geschwister). Diese Spec stellt die Hooks bereit, die jene Hierarchie konsumiert; sie regelt nicht, wie Tests sie nutzen.
- Die Abfrage-Philosophie der **Komponenten-Teststufe** — `spec/project/test-tier-component/` bevorzugt nutzerseitige Abfragen (Rolle, Label, Text) und behandelt eine Test-ID als letztes Mittel, per Testing-Library-Design. Das ist bewusst anders als der E2E-Provider-Vertrag hier (Test-Hook zuerst) und ist eine Abgrenzung, kein Widerspruch: Die beiden Stufen optimieren für unterschiedliche Fehlerklassen.
- **Nicht-Web-Framework-Profile** (native Mobile, Flutter, Desktop) — vertagt, bis ein Consumer eines erzwingt, genau wie `e2e-test-automation` Nicht-Selenium-Profile vertagt. Der neutrale Kern bindet sie bereits; es fehlt nur das konkrete Profil.
- Das **Benennen eines konkreten Linters oder Durchsetzungswerkzeugs** — die Durchsetzung wird als optionales KANN beschrieben (siehe §Optionale Durchsetzung); diese Spec schreibt kein bestimmtes Tooling vor.
- Das Verfassen oder Editieren der Testsuiten, die diese Identifikatoren konsumieren.

## Anforderungen

### Framework-Neutralität

- Die bindenden Anforderungen in diesem Abschnitt **MÜSSEN** gegen eine Fähigkeit formuliert sein, die jeder UI-Stack bietet — das Anheften eines stabilen, maschinenlesbaren Identifikators an ein gerendertes Element — und **DÜRFEN** kein konkretes Attribut, Framework oder keine Komponentenbibliothek **benennen**.
- Ein konsumierendes Projekt **MUSS** angeben, welcher Mechanismus den Identifikator umsetzt; fehlt die Angabe, **MÜSSEN** Konsumenten und konsumierende Agents das Web-Referenzprofil (`data-testid`) unten annehmen.
- Jedes konkrete Artefakt, das diese Spec benennt (das `data-testid`-Attribut, die DOM-Beispiele), gehört zum **Referenzprofil** und **DARF** von einem Projekt auf einem anderen Stack vollständig ersetzt werden, solange der bindende Kern weiter gilt.

### Bereitstellungspflicht und die Trennung von Bereitstellung und Selektion

- Das Frontend **MUSS** an jedem test-relevanten Element und jeder Seite einen stabilen, eindeutigen Identifikator *bereitstellen*; eine Testsuite *selektiert* über diesen Identifikator, **DARF** aber **NICHT** dafür herangezogen werden, ihn zu erzeugen. Bereitstellung ist Anwendungsarbeit; Selektion ist Testarbeit.
- Ein Element ist **test-relevant**, wenn ein User-Journey-Test es lokalisieren müsste: interaktive Steuerelemente, Formularfelder, Dialoge, Navigations-Landmarks und jede Status- oder Ergebnisanzeige, deren Inhalt ein Test prüft. Im Zweifel **SOLLTE** ein Element als test-relevant behandelt werden (Recall vor Precision).
- Der bereitgestellte Identifikator **MUSS** der primäre Selektionsanker sein, der in der Locator-Hierarchie des Konsumenten zuerst genannt wird (`e2e-test-automation` §Locator-Strategie: dedizierter Test-Hook → id → Semantik/Rolle → CSS → XPath).

### Seiten-Marker

- Jede routbare Seite oder Top-Level-Ansicht **MUSS** einen Seiten-Marker-Identifikator der Form `<entity>-<view>-page` tragen, sodass ein Test prüfen kann, dass er auf der richtigen Seite gelandet ist, bevor er handelt.
- Ein gemeinsamer Lade-Zustands-Marker (`loading-skeleton` oder ein gleichwertiger, einzelner, stabiler Name) **MUSS** bereitgestellt werden, während eine Seite oder Region lädt, sodass ein Test auf eine Bedingung statt auf eine feste Verzögerung warten kann.

### Bereitstellung auf Element-Ebene

- Interaktive Elemente (Buttons, Links, Toggles, Menüeinträge), die ein Test ansteuert, **MÜSSEN** jeweils einen stabilen Identifikator tragen.
- Formularfelder **MÜSSEN** einen stabilen Identifikator der Form `form-field-<name>` tragen, wobei `<name>` der stabile Fachname des Feldes ist, nicht seine Position oder sein Label-Text.
- Dialoge, Modals und Overlays **MÜSSEN** an ihrer Wurzel einen stabilen Identifikator tragen, sodass ein Test die Selektion auf den offenen Dialog eingrenzen kann.
- Jede Status-, Validierungs- oder Ergebnisanzeige, deren Inhalt ein Test prüft, **MUSS** einen stabilen Identifikator tragen; das gilt unabhängig davon, wie das Element eingehängt ist (inline, Portal, Toast, Overlay) — der Einhäng-Kontext befreit ein test-relevantes Element nicht von der Bereitstellung.

### Wiederholte Sammlungen per Business-Key adressierbar

- Zeilen einer wiederholten Liste oder Tabelle **MÜSSEN** über einen stabilen **Business-Key** adressierbar sein (zum Beispiel `<entity>-row-<businessKey>`), niemals über einen Listen-Index oder eine DOM-Position, sodass ein Test Umsortierung, Filterung und Paginierung übersteht.
- WENN kein natürlicher Business-Key existiert, **MUSS** das Frontend einen stabilen synthetischen Key bereitstellen, der über Renders deterministisch ist; ein Render-Order-Index oder eine flüchtige Laufzeit-ID **DARF** **NICHT** als Adressierungs-Key verwendet werden.

### Namensschema

- Identifikator-Werte **MÜSSEN** einem einzigen Namensschema folgen: kebab-case, Englisch, zusammengesetzt aus stabilen Fachbegriffen (`<entity>-<view>-page`, `form-field-<name>`, `<entity>-row-<businessKey>`).
- Identifikator-Werte **DÜRFEN** keine volatilen Fakten kodieren (Positions-Index, Pixel-Geometrie, generierte Hashes, lokalisierter Anzeigetext); der Wert **MUSS** allein aus dem Schema lesbar und vorhersagbar bleiben.

### Stabilität als Vertrag

- Ein bereitgestellter Identifikator **MUSS** über Renders deterministisch sein und **MUSS** über die Zustände eines Elements stabil bleiben (aktiviert/deaktiviert, ladend/geladen, valide/invalide, leer/befüllt).
- Ein bereitgestellter Identifikator **DARF** **NICHT** still umbenannt oder entfernt werden; eine Änderung an einem Identifikator ist eine Breaking Change an der Testoberfläche und **MUSS** als solche behandelt werden (angekündigt, mit der konsumierenden Suite koordiniert).
- Framework-autogenerierte Identifikatoren, gehashte CSS-Modul-Klassennamen und andere nicht-deterministische oder nicht-sprechende Werte **DÜRFEN** **NICHT** zur Erfüllung der Bereitstellungspflicht verwendet werden.
- Ein Identifikator **MUSS** kosmetische Markup-Änderungen (Restyling, Wrapper-Elemente, Layout-Refactorings) überstehen, spiegelbildlich zur Konsumenten-Anforderung, dass Selektoren solche Änderungen überstehen.

### Accessibility-Hooks als sekundärer Anker

- Accessibility-Attribute (`role`, `aria-label` und Äquivalente) **DÜRFEN** als sekundärer Selektionsanker dienen und **SOLLTEN** um ihrer selbst willen vorhanden sein, **DÜRFEN** aber den primären bereitgestellten Identifikator **NICHT** ersetzen: a11y-Semantik und der Test-Hook sind komplementär, und ein test-relevantes Element trägt weiterhin seinen dedizierten Identifikator.

### Pflicht der UX-/Usability-Rolle

- Die UX-/Usability-Rolle (konkret der Agent `frontend-usability-optimizer`; sekundär die UX-Domäne des `webview-ui-expert`-Reviews) ist ein adressierter Provider und **MUSS** diesen Vertrag beachten.
- WENN die UX-/Usability-Rolle ein bestehendes Element umgestaltet — ein Formular, einen Dialog, eine Liste oder Tabelle, eine Detailseite oder deren Lade-/Fehler-/Leer-Zustände — **MUSS** das Frontend den stabilen Identifikator des Elements erhalten: Eine Usability-Änderung **DARF** einen bereitgestellten Identifikator **NICHT** still umbenennen oder entfernen (ein Spezialfall des Stabilitätsvertrags oben).

### Optionale Durchsetzung

- Ein konsumierendes Projekt **DARF** eine Lint- oder Review-Regel hinzufügen, dass eine neue interaktive Komponente einen bereitgestellten Identifikator mitliefert (das Definition-of-Done-Muster aus `UI-NFR-022`), aber diese Spec **DARF** keinen bestimmten Linter **benennen** oder einen bestimmten Durchsetzungsmechanismus vorschreiben; die Pflicht ist normativ, das Tooling ist eine Projektentscheidung.

### Web-Referenzprofil (normativ)

Dieses Profil ist die bindende Umsetzung des Kerns für Web-(DOM-)Projekte und der Default, den konsumierende Agents annehmen, wenn kein anderer Mechanismus angegeben ist. Ein Projekt auf einem anderen Stack ersetzt diesen Abschnitt vollständig, erfüllt aber weiterhin den Kern oben.

- Der bereitgestellte Identifikator **MUSS** vom `data-testid`-Attribut im DOM getragen werden; es ist der dedizierte Test-Hook, den die Konsumenten-Hierarchie zuerst nennt.
- Eine routbare Seite **MUSS** `data-testid="<entity>-<view>-page"` an ihrem Top-Level-Container rendern; eine Lade-Region **MUSS** `data-testid="loading-skeleton"` rendern, während sie lädt.
- Ein Formularfeld **MUSS** `data-testid="form-field-<name>"` rendern; ein interaktives Steuerelement **MUSS** ein `data-testid` rendern; eine Dialog-Wurzel **MUSS** ein `data-testid` rendern; ein test-relevantes Status- oder Ergebnis-Element **MUSS** ein `data-testid` rendern.
- Eine wiederholte Zeile **MUSS** `data-testid="<entity>-row-<businessKey>"` rendern, mit dem Business-Key als Schlüssel, niemals mit dem Index.
- Alle `data-testid`-Werte **MÜSSEN** kebab-case Englisch gemäß §Namensschema sein, und `data-testid` **DARF** **NICHT** über einen positionsbasierten oder gehashten Wert vergeben werden.
- `role`/`aria-label` **DÜRFEN** ein `data-testid` begleiten, **DÜRFEN** es aber **NICHT** ersetzen.

## Akzeptanzkriterien

- [ ] Jede bindende Anforderung außerhalb des Referenzprofil-Abschnitts ist formuliert, ohne ein konkretes Attribut, Framework oder eine Komponentenbibliothek zu benennen.
- [ ] Das Web-Referenzprofil ist konkret genug, dass ein Web-Projekt allein daraus eine konforme Oberfläche bereitstellen kann (Seiten-Marker, `loading-skeleton`, `form-field-<name>`, interaktive Steuerelemente, Dialoge, Statusanzeigen, Business-Key-Zeilen).
- [ ] Die Trennung von Bereitstellung und Selektion ist formuliert und zu `e2e-test-automation` §Locator-Strategie querverwiesen, und jene Spec trägt einen Vorwärts-Verweis zurück auf diese.
- [ ] Seiten-Marker, Element-Identifikatoren und Business-Key-Zeilenadressierung sind alle gefordert, wobei index-basierte Adressierung ausdrücklich verboten ist.
- [ ] Das Namensschema (kebab-case, Englisch, keine volatilen Fakten) und der Stabilitätsvertrag (deterministisch, zustandsstabil, keine stille Umbenennung, keine autogenerierten/gehashten Werte) sind beide normativ.
- [ ] Accessibility-Hooks sind als sekundärer Anker positioniert, der den primären Identifikator niemals ersetzt.
- [ ] Die UX-/Usability-Rolle ist als adressierter Provider gebunden, und der Identifikator-Erhalt bei einer Usability-Änderung ist gefordert.
- [ ] Die Durchsetzung ist nur als optionales KANN erwähnt, ohne einen Linter zu benennen.
- [ ] Die Komponenten-Stufen-Abgrenzung (`test-tier-component`, nutzerseitige-Abfrage-zuerst) ist als bewusster Unterschied vermerkt, nicht als Widerspruch.

## Referenzen

- [R1] Konsumenten-Geschwister (Locator-Strategie, Page-Objects, Wartedisziplin; die Suite, die diese Hooks konsumiert): `spec/project/e2e-test-automation/` §Locator-Strategie
- [R2] Abfrage-Philosophie der Komponenten-Stufe, gegen diese Spec abgegrenzt: `spec/project/test-tier-component/`
- [R3] Frontend-Regeln zu Performance/Security/a11y/i18n/UX für dieselbe Web-Oberfläche: `spec/frontend/webview-ui-optimization/`
- [R4] Herkunft der Bereitstellungsregeln, hier de-domänisiert: kamerplanter `UI-NFR-022` (`R-001..R-025`), PR #581
- [R5] Agent-Autorierungsregeln, denen die konsumierenden Agents folgen: `spec/claude/agent-management/`

## Offene Fragen

- Ob ein zweites, gleichwertig normatives Nicht-Web-Profil (native Mobile, Flutter, Desktop) mitgeliefert werden sollte, sobald ein Portfolio-Projekt es braucht, oder ob das Web-Profil plus der framework-neutrale Kern genug Leitlinie ist. Vorläufiger Default, bis ein Consumer die Frage erzwingt: nur das Web-Profil mitliefern und auf den Kern vertrauen.
- ~~Ob die konsumierenden UX-/Build-Agents (`frontend-usability-optimizer`, `webview-ui-expert`, `fullstack-developer`) diese Spec aus ihrer eigenen `description`/`use_when` zitieren sollten, oder ob die hier deklarierte Bindung ausreicht.~~ **Aufgelöst:** Die Bindung ist jetzt in den **Body** (System-Prompt) jedes Agents verdrahtet, nicht in dessen Routing-`description`/`use_when` — `fullstack-developer` stattet die von ihm gebaute UI mit Identifiern aus, `frontend-usability-optimizer` erhält sie bei einer Umgestaltung, und `webview-ui-expert` meldet fehlende/gebrochene als UX-Domänen-Finding. Der Body wurde der Frontmatter vorgezogen, um die operativen Regeln dort zu halten, wo das Verhalten liegt, und um das Routing-`description`-Budget der Agents nicht zu vergrößern.
