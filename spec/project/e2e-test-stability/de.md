# End-to-End-Test-Stabilitäts-Engineering

Status: draft

## Context

Ein Stabilisierungs-Durchlauf über die komplette E2E-Suite eines konsumierenden Projekts (≈720 Selenium-+-pytest-Tests, xdist-parallel, Docker-komponierter App-Stack) hat gezeigt, dass die meiste Instabilität **nicht** aus den Bereichen kommt, die der Automatisierungs-Standard bereits regelt (Page Objects, bedingungsbasierte Waits, Locator-Hierarchie — `spec/project/e2e-test-automation/`). Sie kam aus fünf wiederkehrenden Mechanismen, die keine Locator- oder Wait-Disziplin verhindert:

1. **Shared-State-Kopplung** — Tests konsumieren „die erste Zeile", Seed-Reste oder Entitäten, die ein anderer Test (auf einem anderen parallelen Worker) zufällig erzeugt hat. Symptome: reihenfolgeabhängige stille Skips (13 Tests skippten still in jedem Lauf), Tests, die je nach Worker-Scheduling bestehen oder fehlschlagen.
2. **Globaler serverseitiger Zustand, über Worker hinweg mutiert** — ein Per-User-Singleton (Erfahrungsstufe am geteilten Anonymous-Mode-User) kippte mitten in der Assertion, weil eine fremde Testdatei auf einem anderen Worker lief.
3. **Hazard-anfällige UI-Interaktionen** — ein blindes `ESC`-an-`body`-„Backdrop-Schließen", das den *Eltern-Dialog* schließt, sobald das Select-Menü bereits von selbst zu ist (ein Race, das ~20 kopierte Page-Object-Methoden traf); Klicks, die von noch einklappenden Snackbars abgefangen werden.
4. **Optimistisches UI-Feedback** — ein „Gespeichert"-Snackbar, der *vor* Auflösung des PATCH enqueued wurde; der Test vertraute ihm, lud neu, und der laufende Request wurde gekillt — die Änderung ging still verloren (ein realer nutzerseitiger Datenverlust-Bug, kein Testproblem).
5. **Echte Anwendungs-Concurrency-Defekte, die erst parallele E2E-Last sichtbar macht** — ein Auto-Create-on-Read-Race, das Duplikat-Singleton-Dokumente erzeugte (kein Unique-Index), und ein Read-Modify-Write des Gesamtdokuments, das parallele PATCHes disjunkter Felder verlor. Beide waren nach Identifikation außerhalb der Suite deterministisch reproduzierbar.

Ein späterer Stabilisierungs-Durchlauf über das **Mobile**-E2E-Profil desselben Projekts (141 → 72 → 8 → 5 Failures über vier volle Läufe, bei auf denselben Commits grünen Desktop-Profilen) ergänzte einen sechsten Mechanismus: **viewport-abhängiges Verhalten** — Rollen-Kollisionen mit verstecktem responsivem Chrome, Layout-Wechsel, die die DOM-Form ändern, breakpoint-abhängige Wrapper-Geometrie, Aktivierungsmodelle, die ein synthetischer Fallback nicht bedienen kann, Popovers, die mitten in der Animation repositionieren. Die meisten davon schlagen nicht laut fehl: Sie produzieren leere Reads und No-op-Interaktionen, die Tests aus dem falschen Grund bestehen lassen. §G katalogisiert diese Klasse.

Die tragende Erkenntnis: **Eine parallele E2E-Suite ist de facto ein Concurrency-Test der Anwendung.** Ihre Failures zerfallen in Test-Design-Schulden (1–3), App-Wahrhaftigkeits-Schulden (4) und Produkt-Concurrency-Defekte (5) — und jede Klasse hat einen anderen korrekten Fix. Stabilisierung per Retries, Skips, Voll-Serialisierung oder abgeschwächten Assertions versteckt alle drei.

Diese Spec destilliert die Befunde zu Design-Regeln, damit neue Suiten vom ersten Commit an stabil sind, und zu einem begrenzten Stabilisierungs-Loop für bestehende Suiten. Sie ergänzt `spec/project/e2e-test-automation/` (dort liegt die *Form* der Suite: Page Objects, Waits, Locator, Screenshots, Protokoll, Traceability); diese Spec verantwortet die *Laufzeit-Stabilität* unter paralleler Ausführung.

Leser: Autor:innen und Reviewer von E2E-Suiten; die Agents `e2e-test-generator` / `e2e-test-reviewer`; die Test-Cycle-Skills, die fehlschlagende Läufe klassifizieren und reparieren.

## Goals

- E2E-Tests per Design deterministisch machen: selbst provisionierte Daten, keine Kopplung zwischen Tests oder Workern
- Suiten parallel-sicher machen: globaler mutierbarer Zustand ist inventarisiert und seine Mutatoren serialisiert, alles andere bleibt parallel
- Die bekannten UI-Interaktions-Hazards katalogisieren (blinde Tastatur-Dismissals, Transient-Overlay-Intercepts) und die geschützten Helper verbindlich machen, die sie vermeiden
- Die Responsive-/Viewport-Hazards katalogisieren, die ein Mobile- oder Tablet-Profil hinzufügt (Breakpoint-übergreifende Rollen-Kollisionen, Layout-Wechsel-Reader, unsaubere Klick-Fallbacks, Animations-Races), und layout-prüfende, laut fehlschlagende Page Objects sowie einen animationsfreien Harness verbindlich machen
- Jeden Wait an dauerhafte, wahrhaftige Signale binden — und optimistisches Erfolgs-Feedback in der App als den Implementierungsdefekt behandeln, der es ist
- Concurrency-Failures aus parallelen E2E-Läufen als Produktdefekte an die Anwendung routen, statt sie in der Testschicht zu absorbieren
- Skips und Expected-Failure-Marker ehrlich halten: deterministisch, begründet, überwacht und nach Heilung entfernt
- Den Stabilisierungs-Loop (klassifizieren → klassengerecht fixen → erneut laufen → zweimal grün ohne Eingriff) als Exit-Kriterium der Suite-Arbeit definieren

## Non-Goals

- Form und Disziplin der E2E-Suite — Page-Object-Kapselung, deterministische Wait-Primitive, Locator-Strategie, Screenshots, Protokoll, Marker, Traceability — liegt bei `spec/project/e2e-test-automation/`
- Die Failure-Klassifikations-Taxonomie und die Flake-vs-Real-Adjudikation — liegt bei `spec/project/test-cycle-result-analysis/`; diese Spec konsumiert deren Klassen
- Wie ein bestätigter echter Defekt im Produktivcode gefixt wird (inkl. No-Cheating-Invariante) — liegt bei `spec/project/test-cycle-code-adaptation/`
- Provisionierung von Testability-Hooks (`data-testid`, Zustands-Exposition) in der Anwendung — liegt bei `spec/frontend/testability-identifiers/`
- Test-Tier-Platzierung (was überhaupt in E2E gehört) — liegt bei `spec/project/test-pyramid-foundation/`

## Requirements

### A. Testdaten-Isolation (Self-Provisioning)

- Ein Test, der eine Entität mutiert oder von deren Teilzustand abhängt (z. B. „hat noch keine Qualitätsbewertung"), **MUST** [MUSS] diese Entität selbst erzeugen, markiert mit einem kollisionsfreien eindeutigen Identifier (UUID-abgeleitet; eindeutig über parallele Worker und wiederholte Läufe)
- Ein Test **MUST NOT** [DARF NICHT] von Entitäten anderer Testdateien, deren Ausführungsreihenfolge oder dem ausführenden parallelen Worker abhängen; „klicke die erste Zeile" ist nur für Read-only-Assertions akzeptabel, die für *jede* Zeile gelten
- Read-only-Tests **MAY** [KÖNNEN] geteilte Seed-Daten konsumieren, aber wenn die erwarteten Daten legitim fehlen können, **MUST** [MÜSSEN] sie auf Self-Provisioning zurückfallen statt zu skippen — ein verfügbarkeitsabhängiger Skip ist ein stilles Coverage-Loch, kein Pass
- Self-Provisioning-Helper **MUST** [MÜSSEN] „Erzeugung aus einem erwartbaren fachlichen Grund unmöglich" (expliziter, begründeter Skip) von „Erzeugung fehlgeschlagen" (lauter Failure) unterscheiden und **MUST NOT** [DÜRFEN NICHT] Letzteres in Ersteres umwandeln

### B. Parallele Ausführung und globaler Zustand

- Eine Suite **MUST** [MUSS] ein Inventar des globalen serverseitigen mutierbaren Zustands pflegen, den ihre Tests berühren — Singleton-Dokumente, Shared-User-Präferenzen (Anonymous-/Light-Modi), clusterweite Feature-Flags — und welche Testdateien jeden davon mutieren oder darauf asserten
- Tests, die denselben globalen Zustand mutieren oder darauf asserten, **MUST** [MÜSSEN] über parallele Worker hinweg gegeneinander serialisiert werden (Inter-Prozess-Lock, Scheduler-Gruppen oder Äquivalent), während der Rest der Suite parallel bleibt; die gesamte Suite zu serialisieren ist kein akzeptabler Ersatz
- Wenn ein Test in isolierter Wiederholung stabil ist, aber unter der parallelen Suite fehlschlägt, **MUST** [MUSS] diese Asymmetrie als Beleg für Cross-Test-Interferenz behandelt und als solche untersucht werden (Isolations-Experiment: N aufeinanderfolgende Einzeldatei-Läufe gegen denselben Stack) — nicht als Flake umetikettiert
- Ein durch parallele Ausführung aufgedeckter Concurrency-Failure — Duplikat-Zeilen aus einem Auto-Create-on-Read-Race, ein Lost Update aus einem Read-Modify-Write-Gesamtdokument-Muster, ein fehlender Unique-Constraint auf einem logisch eindeutigen Schlüssel — **MUST** [MUSS] als Anwendungsdefekt klassifiziert und in der Anwendung gefixt werden (Unique-Constraint plus Upsert-Semantik; partielle Feld-Updates), **niemals** durch testseitige Retries, Ordering oder wachsende Lock-Scopes absorbiert
- Fixes solcher Anwendungsdefekte **SHOULD** [SOLLTEN] einen Regressionstest auf dem niedrigsten Tier enthalten, das das Race ausdrücken kann (meist Unit-/Integrationstest auf die Update-Doc-Form oder den Upsert-Pfad), damit das E2E-Tier nicht der einzige Wächter ist

### C. Interaktions-Hazard-Katalog

- Ein Test oder Page Object **MUST NOT** [DARF NICHT] ein blindes Tastatur-Dismissal (`ESC` an `body`) senden, um ein Menü, Popover oder Backdrop „aufzuräumen": Ist das Popover bereits von selbst zu, landet die Taste im Eltern-Dialog und schließt ihn — ein Timing-Race. Dismissal **MUST** [MUSS] durch einen geschützten Helper erfolgen, der (1) sofort zurückkehrt, wenn das Popover bereits weg ist, (2) kurz auf Auto-Close wartet, (3) `ESC` nur sendet, solange das Popover nachweislich noch offen ist, und (4) danach auf sein Verschwinden wartet
- Ein Klick auf ein Element, das ein transientes Overlay (Snackbar, Toast, Collapse-Animation) verdecken kann, **MUST** [MUSS] einen Overlay-toleranten Klick nutzen (in den Viewport scrollen, dann Klick mit Intercepted-Click-Fallback), keinen nackten Element-Klick
- Nach der Auswahl einer Option aus einem Menü/Select **MUST** [MUSS] der Interaktionsfluss warten, bis das Popover weg ist, bevor die nächste Element-Interaktion erfolgt; wo das Formular es erlaubt, **SHOULD** [SOLLTEN] einfache Eingabefelder vor menüöffnenden Interaktionen gefüllt werden statt danach
- Diese geschützten Helper **MUST** [MÜSSEN] einmal in der geteilten Page-Object-Basis leben; per-Page-Kopien von Interaktions-Plumbing sind der Weg, auf dem derselbe Hazard ~20-mal wieder eingeführt wurde

### D. Wahrhaftige asynchrone Signale

- Ein Wait **MUST** [MUSS] an ein dauerhaftes Signal gebunden sein — serverbestätigter Zustand, ein Read-back nach Full-Reload, ein Element, dessen Präsenz Persistenz beweist — niemals an optimistisches UI-Feedback, das der Auflösung des zugrunde liegenden Requests vorausgeht
- Wenn die Anwendung Erfolgs-Feedback ausgibt, bevor die Änderung dauerhaft persistiert ist (Fire-and-Forget-Dispatch gefolgt von sofortigem Erfolgs-Toast), ist das ein **Implementierungsdefekt** — wer zügig wegnavigiert, verliert die Änderung — und **MUST** [MUSS] in der Anwendung gefixt werden (Persistenz awaiten, dann bestätigen; Fehler-Feedback im Fehlerfall). Testseitige Kompensation (Sleeps, dem Toast trotzdem vertrauen) ist verboten
- Ein zustandsändernder Helper **MUST** [MUSS] seine Wirkung verifizieren (Read-back mit begrenzten Retries, wo legitim mit erneutem Versuch der Aktion) und **MUST** [MUSS] laut fehlschlagen, wenn der Zustand nie eintritt; stilles Weiterlaufen nach erschöpftem Retry-Loop lässt den Test gegen den *vorherigen* Zustand asserten und produziert Um-eins-versetzt-Failures, die stundenlang fehlattribuiert werden
- Fail-open- versus Fail-closed-Rendering während asynchroner Loads (Navigation zeigt alles vs. Formularfelder versteckt, solange ein Fetch läuft) **MUST** [MUSS] pro Oberfläche verstanden sein und sich darin spiegeln, worauf der Test pollt; ein Poll, der „noch nicht geladen" nie von „korrekt abwesend" unterscheiden kann, ist keine valide Assertion

### E. Skip- und Expected-Failure-Hygiene

- Jeder Skip **MUST** [MUSS] für ein gegebenes Tripel (Code, Seed, Konfiguration) deterministisch sein und einen Reason-String tragen, der die konkrete Vorbedingung benennt; ein Skip, dessen Auslösen vom Worker-Scheduling oder der Testreihenfolge abhängt, ist ein Testdefekt gemäß §A
- Ein Expected-Failure-Marker (`xfail`) **MUST** [MUSS] non-strict nur mit dokumentiertem Grund, Verweis auf den zugrunde liegenden Befund/Issue und einer Revisit-Bedingung sein; Suiten **MUST** [MÜSSEN] die xpass-Zahl beobachten, und sobald die Ursache gefixt ist und die markierten Tests konsistent durch das Grün-Bestätigungsfenster der Suite (§F) bestehen, **MUST** [MÜSSEN] die Marker entfernt werden statt zu verrotten
- Triage-Output **MUST** [MUSS] Skip-Zahlen pro Datei sichtbar machen, damit still verlorene Coverage auffällt; eine Testklasse, die in jedem Lauf skippt, ist ein Befund, kein Hintergrundrauschen

### F. Stabilisierungs-Loop (Prozess)

- Jeder Non-Pass **MUST** [MUSS] vor jeder Änderung klassifiziert werden, mit den Klassen aus `spec/project/test-cycle-result-analysis/` (real defect / flake / test bug / infrastructure), und der Fix **MUST** [MUSS] zur Klasse passen: Test-Bug → minimaler chirurgischer Test-Fix; Implementierungs-Bug → Root-Cause-Fix in der Anwendung; Flake → per unabhängigem Re-Run beweisen, dann Bedingung oder Setup härten; Infrastruktur → Harness fixen
- Ein Profil/eine Suite gilt erst als stabilisiert, wenn sie **zweimal in Folge ohne jeden Eingriff** dazwischen besteht; jede Code- oder Test-Änderung setzt den Zähler zurück
- Retries-als-Fix, neue Skips, gelöschte Tests und abgeschwächte Assertions sind verbotene Stabilisierungsmittel (die No-Cheating-Invariante aus `spec/project/test-cycle-code-adaptation/` auf Suite-Ebene angewandt); das Löschen eines Tests erfordert eine explizite Begründung gegen seine Testfall-Spezifikation
- Lauf-Artefakte — Screenshots, Anwendungs-/Container-Logs, Request-Logs, das maschinengenerierte Protokoll — **MUST** [MÜSSEN] pro Lauf aufbewahrt und als Triage-Evidenz genutzt werden; eine Behauptung über „was die App zeigte" wird per Screenshot entschieden, eine über „was der Server tat" per Request-Log — einschließlich Request-Count-Diffs zwischen Läufen, die klären, ob der Server überhaupt gefragt wurde —, bevor gegen eine Hypothese programmiert wird
- Wenn dieselbe Oberfläche wiederholt mit rotierenden Root Causes fehlschlägt, **MUST** [MUSS] der Loop weiterbohren, bis ein Mechanismus *bewiesen* ist (außerhalb der Suite reproduziert oder per Isolations-Asymmetrie demonstriert) — drei distinkte gestapelte Ursachen auf einer Seite (optimistisches Feedback, Lost Update, Duplikat-Singletons) sind ein realistisches Ergebnis, und nach dem ersten plausiblen Fix aufzuhören lässt die Suite rot

### G. Responsive- und Viewport-abhängige Hazards

Eine responsive UI rendert je Breakpoint anderes Chrome, andere DOM-Formen und andere Geometrie; eine Suite, die ein Mobile- oder Tablet-Profil ergänzt, erbt damit eine Hazard-Klasse, die §A–F nicht abdecken — und die überwiegend still fehlschlägt: als leere Reads und No-op-Interaktionen, die Tests aus dem falschen Grund bestehen lassen:

- Ein Locator, der allein auf einer strukturellen oder ARIA-Rolle baut (eine nackte Dialog- oder Listbox-Rolle, ein nackter Tabellen- oder Zellen-Selektor), **MUST NOT** [DARF NICHT] ungescoped verwendet werden: Komponentenbibliotheken vergeben dieselbe Rolle an unterschiedliches Chrome an unterschiedlichen Breakpoints, und ein verstecktes, kept-mounted responsives Element kann die Rolle tragen und dem echten Ziel im DOM vorausgehen. Der Selektor wird auf seinen besitzenden Container eingegrenzt oder adressiert einen dedizierten Test-Hook, gemäß `spec/project/e2e-test-automation/` §Locator-Strategie
- Ein Page Object **MUST NOT** [DARF NICHT] eine layout-spezifische Struktur (Desktop-Tabelle, mobile Kartenliste) lesen, ohne zu asserten, dass dieses Layout aktiv ist, und ein Reader, der seine erwartete Struktur nicht findet, **MUST** [MUSS] laut fehlschlagen, statt ein leeres Ergebnis zurückzugeben — ein leerer Read, der eine „nichts Unerwartetes vorhanden"-Assertion erfüllt, ist ein stilles Coverage-Loch
- Zugriff in eine responsive Sammlung **MUST** [MUSS] key-basiert erfolgen, niemals positionsbasiert: Ein positionsbasierter Read ist an jedem Breakpoint falsch, auf Desktop nur unbemerkbar. Die providerseitigen Pflichten, von denen das abhängt — dieselben key-basierten Hooks in jedem Layout, Layout-übergreifende Unterscheidbarkeit von Listen, der Identifikator auf dem interaktionsempfangenden Element — liegen bei `spec/frontend/testability-identifiers/`
- Ein Klick-Fallback (synthetischer Script-Klick, koordinatenbasierter Event-Dispatch) **MUST** [MUSS] für das Aktivierungsmodell der Zielkomponente korrekt sein oder **MUST** [MUSS] laut fehlschlagen; ein Fallback, der die Wirkung nicht erzeugen kann, aber Erfolg meldet, ist schlimmer als kein Fallback — und koordinatenbasierter Dispatch macht keinen Interactability-Hit-Test, liefert Events also an das, was obenauf liegt
- Ein Helper, der ein Menü, Select oder Popover öffnet, **MUST** [MUSS] verifizieren, dass die Komponente tatsächlich geöffnet ist (Expanded-State-Attribut oder Äquivalent), statt anzunehmen, dass der Klick gewirkt hat — §Ds Verifiziere-die-Wirkung-Regel, angewandt auf den Öffnungs-Schritt
- Eine viewport-konditionale Affordance (hinter einem Disclosure-Control eingeklappte Sektion, Overflow-Menü, Drawer-Navigation) **MUST** [MUSS] Teil des Page-Object-Vertrags sein und vor abhängigen Interaktionen bedingungsbasiert und idempotent expandiert werden
- Der Browser-Harness **MUST** [MUSS] UI-Animationen suite-weit deaktivieren (erzwungene Reduced-Motion-Präferenz oder das Framework-Äquivalent); der Klick auf ein noch animierendes, repositionierendes Popover ist ein Race, das kein Wait zuverlässig schließt
- Gegen ein gegebenes Browser-Grid **MUST** [MUSS] zur selben Zeit genau ein Anwendungs-Stack laufen; nebenläufige Stacks erschöpfen die Session-Kapazität des Grids und produzieren massenhafte Setup-Fehler, die sich als Suite-Failures tarnen
- Ein Profil in einer deklarierten Test-Matrix **MUST** [MUSS] erst nach mindestens einem validen Baseline-Lauf als abgedeckt gelten; ein infrastruktur-vergifteter Lauf ist keine Baseline

## Acceptance Criteria

- [ ] Neue E2E-Tests provisionieren die Entitäten, die sie mutieren oder von deren Teilzustand sie abhängen, selbst — mit kollisionsfreien eindeutigen Identifiern
- [ ] Die Suite dokumentiert ihr Inventar globalen mutierbaren Zustands und serialisiert genau die mutierenden/assertenden Testdateien gegeneinander, nicht mehr
- [ ] Kein Page Object sendet ein ungeschütztes `ESC`-an-`body`-Dismissal; Menü-/Overlay-Dismissal läuft über den geteilten geschützten Helper
- [ ] Kein Wait bindet an optimistisches UI-Feedback; zustandsändernde Helper lesen ihre Wirkung zurück und schlagen bei Nicht-Eintritt laut fehl
- [ ] Unter parallelen Läufen gefundene Concurrency-Defekte werden in der Anwendung gefixt (mit Regressionstest auf niedrigerem Tier), nicht in der Testschicht absorbiert
- [ ] Alle Skips sind deterministisch und begründet; xfail-Marker tragen Grund + Revisit-Bedingung und werden entfernt, sobald sie ein volles Grün-Bestätigungsfenster lang xpassen
- [ ] Suite-Stabilisierung folgt klassifizieren → klassengerechter Fix → Re-Run, mit zweimal-grün-ohne-Eingriff als Exit-Kriterium
- [ ] Kein Struktur-/ARIA-Rollen-Locator wird ungescoped verwendet; layout-spezifische Reader asserten ihr aktives Layout und schlagen laut fehl, statt leere Ergebnisse zurückzugeben
- [ ] Klick-Fallbacks sind für das Aktivierungsmodell des Ziels korrekt oder schlagen laut fehl, Öffnungs-Helper verifizieren den geöffneten Zustand, der Harness läuft animationsfrei mit einem Stack pro Browser-Grid, und ein Matrix-Profil gilt erst nach einem validen Baseline-Lauf als abgedeckt
- [ ] Die Agents `e2e-test-generator` und `e2e-test-reviewer` wenden diese Spec neben `spec/project/e2e-test-automation/` an, wenn sie Suiten scaffolden oder reviewen

## References

- `spec/project/e2e-test-automation/` — der Suite-Form-Standard, den diese Spec ergänzt (Page Objects, Waits, Locator, Screenshots, Protokoll, Traceability)
- `spec/project/test-cycle-result-analysis/` — Failure-Klassifikations-Taxonomie, konsumiert von §F
- `spec/project/test-cycle-code-adaptation/` — No-Cheating-Invariante und Root-Cause-Fixing für bestätigte Defekte
- `spec/project/test-pyramid-foundation/` — Tier-Platzierung; die von §B geforderten Regressionstests auf niedrigeren Tiers
- `spec/frontend/testability-identifiers/` — providerseitige Testability-Hooks in der Anwendung unter Test
- Quell-Erfahrung: kamerplanter-Full-Suite-E2E-Stabilisierung (2026-07), Branch `fix/e2e-full-run-stabilization` — reihenfolgeabhängige Harvest-Detail-Skips, ESC-Race über ~20 Page Objects, optimistischer Erfahrungsstufen-Snackbar, Preference-Lost-Update, Duplikat-Singleton-Preference-Dokumente; jeder Mechanismus aus §Context mappt auf einen dort reproduzierten Vorfall; der Mobile-Profil-Durchlauf (Läufe `20260725_010046`, `030325`, `055859`, `073849`; 141 → 72 → 8 → 5 Failures) lieferte die §G-Viewport-Hazards

## Open Questions

- Soll das Global-State-Inventar (§B) ein maschinenlesbares Artefakt sein (z. B. eine conftest-Registry, aus der die Lock-Fixture ihre Dateiliste ableitet) statt Prosa? Das konsumierende Projekt hardcodet das serialisierte Modul-Set aktuell neben dem Lock
- Ob das Isolations-Experiment (§B) als Triage-Skill-Schritt automatisiert werden soll (fehlschlagende Datei N× gegen frischen Stack laufen lassen und die Asymmetrie berichten) oder manuelle Diagnostik bleibt
