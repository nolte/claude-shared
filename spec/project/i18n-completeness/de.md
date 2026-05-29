# i18n-Vollständigkeits-Audit

Status: draft

## Kontext

Eine lokalisierte Anwendung hält ihre nutzerseitigen Strings in pro-Locale-Übersetzungsdateien (ein JSON- oder YAML-Baum pro Sprache) und referenziert sie aus dem Code über den Lookup-Aufruf einer i18n-Bibliothek (`t('key')`, `i18nKey="key"`, `$t('key')`, `<FormattedMessage id="key">` und ähnliche). Drei Drifts häufen sich still an, während die App wächst: Ein Key, der zur Referenz-Locale hinzugefügt wurde, landet nie in den anderen Locales (ein Nutzer sieht einen rohen Key oder einen Fallback-Sprach-String); ein im Code referenzierter Key ist nie definiert (ein Laufzeit-Miss); und ein in den Dateien definierter Key wird nirgends mehr referenziert (Ballast, der Übersetzer in die Irre führt). Keiner davon wird per Default von einem Type-Checker oder einer Test-Suite gefangen, und sie tauchen als Produktions-UI-Defekte in der am wenigsten getesteten Locale auf.

Diese Spec regelt ein fokussiertes, **read-only-Vollständigkeits-Audit** von Übersetzungsdateien gegeneinander und gegen die Code-Verwendung, operationalisiert durch den `i18n-completeness-checker`-Agent (`distribution: plugin`). Sie ist der generalisierte Nachfolger eines projektlokalen Checkers, der die Locale-Pfade, die Referenzsprache und die `react-i18next`-Call-Site-Patterns einer einzelnen App hartcodiert hatte. Die Portfolio-Form entdeckt die Locale-Dateien und Source-Roots und passt sich an die deklarierte i18n-Bibliothek des Projekts an, statt eine anzunehmen.

Leser: Agent-Autoren, die den Checker pflegen; Reviewer, die seine Befunde prüfen; Entwickler, die ihn nach einem Feature, vor einem Release oder innerhalb eines Pre-PR-Checks laufen lassen.

## Ziele

- Die drei Vollständigkeits-Drifts — Cross-Locale-Paritätslücken, im-Code-verwendete-aber-undefinierte Keys und definierte-aber-ungenutzte Keys — als einen einzigen nach Schweregrad sortierten Report aufzeigen
- Im Kern-Algorithmus (Set-Diff über Locales plus ein Usage-Scan) framework-agnostisch bleiben, während die Call-Site-Patterns an die tatsächliche i18n-Bibliothek des Projekts angepasst werden
- Strikt read-only bleiben: Das Audit berichtet, es editiert nie Übersetzungsdateien oder Code
- Das Audit billig wiederholbar innerhalb eines Sprints machen, weil es seiteneffektfrei ist
- Eine klare Grenze zum breiten Webview-UI-i18n-Review und zur Übersetzungs-Autorenschaft ziehen, sodass der Agent nur für Datei-Level-Vollständigkeit aufgerufen wird

## Nicht-Ziele

- Übersetzungen verfassen oder korrigieren — das Audit berichtet Lücken, ein Mensch oder ein Übersetzungs-Workflow füllt sie
- Das breite Web-UI-Internationalisierungs-Review (RTL-Pipeline, i18n-Bootstrap, Locale-Switching-UX) im Besitz von `spec/frontend/webview-ui-optimization/`; diese Spec ist die enge Datei-vs-Code-Vollständigkeits-Scheibe
- Beurteilung der Übersetzungs-*Qualität* (Sprachfluss, Ton, Terminologie) über die mechanische „identisch über Locales ⇒ vermutlich unübersetzt"-Heuristik hinaus
- Erzwingung einer bestimmten Key-Namens-Konvention; das Audit **DARF [MAY]** Konventions-Drift berichten, wenn eine Konvention deklariert ist, aber es erlegt keine auf
- Laufzeit-Locale-Loading, Lazy-Namespace-Splitting oder Bundle-Size-Belange

## Anforderungen

### Eingaben und Discovery

- **MUSS [MUST]** die Menge der pro-Locale-Übersetzungsdateien entdecken, statt den Pfad irgendeines Projekts hartzucodieren; der Operator **DARF [MAY]** das Audit auf ein explizites Locale-Verzeichnis richten, und ohne das lokalisiert der Agent den konventionellen Locale-Baum (zum Beispiel `**/locales/<lang>/*.json`, `**/i18n/<lang>.json`, `**/lang/*.yaml`)
- **MUSS [MUST]** eine einzelne **Referenz-Locale** bestimmen (die Source-of-Truth-Sprache, gegen die andere Locales gemessen werden): die vom Operator benannte verwenden, sonst die deklarierte Default-Locale des Projekts, sonst auf eine dokumentierte Heuristik zurückfallen und angeben, welche Locale gewählt wurde
- **MUSS [MUST]** die zu scannenden Source-Roots für Key-Verwendung entdecken, statt den Pfad einer App hartzucodieren, und berichten, welche Roots und Datei-Globs gescannt wurden
- **MUSS [MUST]** die Call-Site-Lookup-Patterns an die i18n-Bibliothek des Projekts anpassen (react-i18next / i18next `t('…')` und `i18nKey="…"`, vue-i18n `$t('…')` / `<i18n-t>`, FormatJS / react-intl `formatMessage`/`<FormattedMessage id>` und vergleichbare); wenn die Bibliothek nicht bestimmt werden kann, das angenommene Pattern-Set im Report angeben
- **DARF [MAY]** eine optionale repository-lokale Config-Datei (`project/i18n-audit.yml`) lesen, die Locale-Pfade, Referenz-Locale, Source-Globs und i18n-Bibliothek deklariert; wenn vorhanden, haben ihre Werte Vorrang vor der Discovery, wenn abwesend, ist Pro-Invocation-Discovery der dokumentierte Default. Der Report **MUSS** pro aufgelöster Eingabe angeben, ob der Wert aus der Config-Datei, einem Operator-Argument oder der Discovery stammt

### Audit-Dimensionen

- **MUSS [MUST]** jeden unabhängigen Locale-Baum (pro Paket / Subroot) als separaten Audit-Scope behandeln und Keys nie über Bäume hinweg zusammenführen; die Referenz-Locale, Parität und Orphan-/Fehlend-Mathematik jedes Scopes wird allein innerhalb dieses Baums berechnet. Die Grenze ist der entdeckte Locale-Baum-Root oder die Pro-Scope-Einträge, wenn die optionale Config-Datei sie deklariert
- **MUSS [MUST]** jede Locale-Datei zu gepunkteten Key-Pfaden flachklopfen und gegen die Referenz-Locale berechnen: Keys, die in der Referenz vorhanden, aber in einer anderen Locale fehlen, und Keys, die in einer anderen Locale vorhanden, aber in der Referenz fehlen (strukturelle Divergenz)
- **MUSS [MUST]** einen **strukturellen Mismatch** berichten, wenn derselbe Key-Pfad über Locales hinweg zu unterschiedlichen Werttypen auflöst (String in einer, Objekt/verschachtelt in einer anderen)
- **MUSS [MUST]** die Source-Roots nach Key-Referenzen scannen und klassifizieren: ein im Code verwendeter, aber in keiner Locale definierter Key (**kritisch** — ein Laufzeit-Miss) und ein in den Locales definierter, aber nirgends im Code referenzierter Key (**Orphan**, informativ)
- **MUSS [MUST]** statisch unentscheidbare dynamische Keys (Template-String- oder Variablen-Lookups wie `` t(`enums.${type}`) ``) als notierten Vorbehalt behandeln, nie als harten Miss — sie als „dynamisch, nicht statisch verifizierbar" berichten, sodass sie weder den Kritisch-Zähler aufblähen noch still verschwinden
- **SOLLTE [SHOULD]** Qualitäts-Heuristiken laufen lassen: leere String-Werte pro Locale; Werte, die zwischen Referenz und einer anderen Locale identisch sind (vermutlich unübersetzt); und Interpolations-Platzhalter-Parität (dieselben `{{var}}` / `{var}` / `%s`-Platzhalter erscheinen im Wert jeder Locale für einen Key)
- **DARF [MAY]**, wenn das Projekt eine Key-Namens-Konvention deklariert, Keys berichten, die sie verletzen; ohne deklarierte Konvention erfindet der Agent keine

### Ausgabe und Seiteneffekte

- **MUSS [MUST]** strikt read-only sein: nur Lese- und Such-Tools deklarieren und nie Übersetzungsdateien, Code oder eine andere Datei editieren; die einzige Ausgabe ist ein Report
- **MUSS [MUST]** einen einzigen nach Schweregrad sortierten Report emittieren — **kritisch** (verwendet-aber-undefiniert; fehlend in einer Locale), dann **Warnung** (Orphans, struktureller Mismatch), dann **Info** (identische Werte, leere Werte, Platzhalter-Drift) — angeführt von einer Zusammenfassungs-Metrik-Tabelle (pro-Locale-Key-Zählungen, fehlend, Orphan, leer, identisch, dynamisch-übersprungen)
- **MUSS [MUST]** die Pro-Kategorie-Ausgabe deckeln (zum Beispiel: die ersten N Einträge zeigen und den Rest als „… und {n} weitere" zusammenfassen), sodass ein großer Drift keine unlesbare Key-Wand erzeugt
- **SOLLTE [SHOULD]** jeden verwendet-aber-undefinierten Key einer Source-Location (Datei und Zeile) zuordnen, sodass der Befund umsetzbar ist
- **MUSS [MUST]** berichten, welche Locale-Dateien, Source-Roots, Globs, Referenz-Locale und Call-Site-Patterns verwendet wurden, sodass der Scope des Audits auditierbar und reproduzierbar ist

## Akzeptanzkriterien

- [ ] Das Audit auf einem Projekt mit divergierenden Locale-Dateien laufen zu lassen erzeugt einen nach Schweregrad sortierten Report, dessen Zusammenfassungs-Tabelle pro-Locale-Key-Zählungen plus fehlend-, Orphan-, leer-, identisch- und dynamisch-übersprungen-Zählungen auflistet
- [ ] Ein in der Referenz-Locale vorhandener, aber in einer anderen Locale fehlender Key erscheint unter einem kritischen „fehlende Übersetzung"-Befund, der die Locale benennt
- [ ] Ein im Code referenzierter, aber in keiner Locale definierter Key erscheint als kritisch mit einer Source-Datei:Zeile-Zuordnung
- [ ] Ein in den Locales definierter, aber nirgends referenzierter Key erscheint als informativer Orphan, nicht als kritischer Befund
- [ ] Ein dynamischer/Template-String-Lookup wird als „dynamisch, nicht statisch verifizierbar" berichtet und vom Kritisch-Zähler ausgeschlossen
- [ ] Ein Key, dessen Werttyp über Locales hinweg abweicht (String vs. Objekt), wird als struktureller Mismatch berichtet
- [ ] Der Report gibt die entdeckten Locale-Dateien, Source-Roots und Globs, die gewählte Referenz-Locale und die verwendeten Call-Site-Patterns an
- [ ] Der Agent deklariert nur Lese-/Such-Tools (keine Schreib-, Edit- oder Ausführungs-Tools) und nimmt keine Datei-Modifikationen vor
- [ ] Das Audit auf einem Projekt aufzurufen, dessen i18n-Bibliothek nicht bestimmt werden kann, läuft trotzdem und gibt das angenommene Call-Site-Pattern-Set im Report an
- [ ] Der Agent zitiert diese Spec in seinem Body oder seiner `description`

## Referenzen

- [R1] Agent-Autoren-Regeln, denen dieser Agent entspricht: `spec/claude/agent-management/`
- [R2] Skill-vs-Agent-Entscheidungsregel und Rationale-Abschnitts-Anforderung: `spec/claude/skill-vs-agent/`
- [R3] Benachbartes breites Web-UI-Internationalisierungs-Review (gegen diese Spec abgegrenzt): `spec/frontend/webview-ui-optimization/`
- [R4] Review-Plan-/Audit-Ausgabe-Konventionen für nach Schweregrad sortierte Reports: `spec/claude/review-plan/`

## Offene Fragen

- Soll die „identisch über Locales"-Heuristik Locales ausnehmen, die legitim nah sind (zum Beispiel Eigennamen, Markennamen, Einheiten), und wenn ja via Allowlist?
- Soll die Platzhalter-Paritätsprüfung ICU-MessageFormat-Plural-/Select-Syntax verstehen, oder bei Simple-Platzhalter-Granularität bleiben, bis ein ICU-bewusster Pass gerechtfertigt ist?
