# Skills-und-Agents-Sweep-Audit

Status: draft

## Context

Die Specs `skill-review` und `agent-review` legen fest, wie ein einzelnes Artefakt reviewt wird: welche Regeln ein Reviewer prüft, in welcher Reihenfolge und welcher Plan dabei entsteht. Was sie nicht definieren, ist die Prüfung des gesamten Plugin-Inventars als kohärentes System. Per-Artefakt-Reviews sind bewusst isoliert: Jeder Plan fokussiert auf ein einzelnes Skill oder einen einzelnen Agent und berücksichtigt nicht, wie sich das Artefakt zu allen seinen Nachbarn verhält.

Portfolio-weite Befunde sind per-Artefakt-Reviews systematisch unsichtbar. Abgrenzungskonflikte zwischen zwei Skills treten nur zutage, wenn beide in derselben Session mit expliziter Cross-Referenzierung reviewt werden. Spec-induzierte Lücken -- wo eine Spec ein Skill oder einen Agent verlangt, der noch nicht existiert -- werden beim Review vorhandener Artefakte nie entdeckt. Vokabular-Drift bei Operations-Bezeichnungen akkumuliert im Inventar, ohne dass ein einzelner Per-Artefakt-Befund darauf hinweist. Namens-Inkonsistenzen und Lifecycle-Ordnungs-Lücken erfordern eine inventarweite Perspektive.

Diese Spec kodifiziert die Methodik eines Skills-und-Agents-Sweep-Audits: ein periodisches, portfolio-weites Verfahren, das per-Artefakt-Reviews durch Cross-Cutting-Analyse ergänzt. Die Methodik wurde empirisch beim Baseline-Sweep 2026-05-20 des `nolte-shared`-Plugins (34 Skills, 9 Agents) entwickelt. Diese Spec verallgemeinert diese Erfahrung zu einem wiederholbaren Verfahren.

Leser: Auditoren, die einen portfolioweiten Sweep des Plugin-Inventars durchführen, die Autoren des `skills-agents-sweep`-Skills, die die Methodik operationalisieren, sowie Betreuer, die auf die Querschnitts-Befunde reagieren, die Einzelartefakt-Reviews nicht sichtbar machen.

## Goals

- Jeder Sweep-Audit wendet dieselben Cross-Cutting-Analyse-Dimensionen in derselben Reihenfolge an und produziert einen konsolidierten Bericht, der über Sweep-Instanzen hinweg vergleichbar ist
- Cross-Cutting-Befunde -- Abgrenzungskonflikte, spec-induzierte Phantom-Skills, Vokabular-Drift bei Operations, Namens-Inkonsistenzen, Skill-vs-Agent-Fehlklassifikationen -- werden systematisch erkannt und mit konkreten Artefaktpaaren oder Spec-Pfaden belegt
- Plugin-Entwickler können aus dem konsolidierten Bericht Umsetzungswellen planen, ohne Prioritäten aus 40 oder mehr Einzel-Plänen neu ableiten zu müssen
- Die wellen-basierte Umsetzungs-Roadmap jedes Sweeps ist nach Aufwand mal Wirkung sortiert, unterscheidet mechanische Sweeps von Spec-Erweiterungen von strukturellen Neu-Artefakten, sodass Beitragende Wellen parallel oder sequenziell ausführen können
- Das Sweep-Verfahren ist werkzeug-agnostisch: Es kann manuell von einem menschlichen Reviewer durchgeführt, von einer LLM-Session gesteuert oder durch ein zukünftiges `skills-agents-sweep`-Skill operationalisiert werden, ohne den Output-Vertrag zu ändern
- Die Lifecycle-Invariante -- genau ein offener Sweep zur gleichen Zeit, geschlossen erst wenn jeder Wellenpunkt aufgelöst oder explizit zurückgestellt ist -- verhindert, dass überlappende Audits widersprüchliche Roadmaps erzeugen

## Non-Goals

- Vorgabe, wie einzelne Skills authored werden: `skill-management` ist zuständig
- Vorgabe, wie einzelne Agents authored werden: `agent-management` ist zuständig
- Definition des Per-Artefakt-Review-Verfahrens: `skill-review` und `agent-review` sind zuständig; diese Spec beauftragt jene Verfahren, wiederholt sie aber nicht
- Vorgabe des Per-Artefakt-Plan-Formats: `review-plan` ist zuständig
- Prüfung von Vale-Vokabularen auf Upstream-Drift: `vocab-drift-audit` ist zuständig
- Prüfung der Laufzeit- oder Verhaltens-Korrektheit von Skills oder Agents
- Prüfung von Linting- und Markdown-Style-Problemen, die bereits durch `task lint` / Vale / Pre-Commit-Hooks durchgesetzt werden
- Prüfung von Spec-Dateien auf interne Konsistenz oder Audience-Fit: `spec-readiness-reviewer` ist zuständig

## Requirements

### Sweep-Scope

- **MUSS** jeden Skill unter `skills/<name>/` und jeden Agent unter `agents/<name>.md` im Repository zum Zeitpunkt der Sweep-Eröffnung erfassen
- **MUSS** die Repository-Revision (Git-SHA), bei der der Sweep eröffnet wurde, im Frontmatter des konsolidierten Berichts festhalten
- **MUSS** folgende Cross-Artefakt-Dimensionen analysieren: Abgrenzungskonflikte und Overlaps, Workflow-Ketten-Dokumentation, spec-induzierte Lücken, Adoption-Friction, Operations-Vokabular-Konsistenz, Korrektheit der Skill-vs-Agent-Klassifikation und Namens-Konsistenz
- **KANN** den Sweep auf eine Teilmenge von Artefakten nach Lifecycle-Phase oder Frontmatter-Tag eingrenzen, wenn der Sweep durch ein konkretes Problem ausgelöst wird; in diesem Fall **MUSS** die Eingrenzung im Scope-Abschnitt des konsolidierten Berichts festgehalten werden, damit Reviewer wissen, welche Artefakte ausgeschlossen wurden

### Auslöser

- **MUSS** vor jedem Major-Plugin-Release ausgeführt werden (ein Release, das das erste Versionssegment erhöht)
- **SOLLTE** ausgeführt werden, wenn seit dem letzten geschlossenen Sweep mehr als fünf neue Skills oder Agents auf `develop` gelandet sind
- **KANN** ad hoc ausgeführt werden, wenn ein Beitragender cross-artefakt-weite Drift vermutet, die per-Artefakt-Reviews nicht aufdecken würden

### Phasen eines Sweeps

- **MUSS** folgende Phasen in dieser Reihenfolge durchlaufen: (1) Per-Artefakt-Reviews delegiert an `skill-review` und `agent-review`, (2) Cross-Cutting-Analyse über alle Artefakte, (3) Authoring des konsolidierten Berichts, (4) wellen-basierte Umsetzung
- **MUSS** den konsolidierten Bericht unter `.audits/skills-agents-sweep/<Datum>-<Slug>.md` persistieren, bevor Phase 4 beginnt
- **DARF NICHT** mit Phase 4 beginnen, bevor der konsolidierte Bericht auf der Festplatte existiert, sodass jeder Umsetzungs-PR den Bericht als Nachweis-Quelle referenzieren kann
- **SOLLTE** Per-Artefakt-Reviews in Phase 1 vor der Cross-Cutting-Analyse in Phase 2 durchführen, weil die Per-Artefakt-Pläne Einzelbefunde liefern, die in die Cross-Cutting-Dimensionen einfließen
- Der Phasen-Vertrag ist normativ; die Ausführungsstrategie (sequenziell, parallel, Subagent-Fan-out) ist die Wahl des Operators und **DARF** hier **NICHT** vorgeschrieben werden

### Cross-Cutting-Dimensionen

- **MUSS** die Abgrenzungs-Matrix analysieren: Für jedes Artefaktpaar, dessen Descriptions überlappende Trigger-Phrasen adressieren, den Overlap festhalten, eine Auflösung vorschlagen (Merge, Rename oder bidirektionale "Don't use for"-Klausel) und das Paar als Konflikt, Adjazenz oder Kette klassifizieren
- **MUSS** spec-induzierte Lücken inventarisieren: Für jeden `spec/`-Pfad, der in einem Skill- oder Agent-Body referenziert wird und keinem existierenden Skill oder Agent entspricht, die Lücke, die referenzierenden Artefakte und eine vorgeschlagene Auflösung festhalten
- **MUSS** jeden Befund nach Umsetzungswelle klassifizieren: mechanischer Sweep (automatisierte oder nahezu automatisierte Änderung), Spec-Erweiterung (erfordert eine Spec-Änderung vor der Umsetzung) oder strukturelles Neu-Artefakt (erfordert das Authoring eines neuen Skills oder Agents)
- **MUSS** die Skill-vs-Agent-Klassifikation analysieren: Für jeden Skill und jeden Agent prüfen, ob der Rationale-Abschnitt den gewählten Artefakttyp anhand der Entscheidungskriterien aus `spec/claude/skill-vs-agent/` begründet; Fehlklassifikationen sind Befunde
- **SOLLTE** die Operations-Vokabular-Konsistenz analysieren: Skills erkennen, die nicht-standardisierte Operations-Überschriften oder Operations-Verben verwenden, und Abweichungen gegen das in `spec/claude/skill-management/` definierte Vokabular festhalten
- **SOLLTE** die Namens-Konsistenz analysieren: Artefakte erkennen, deren Namen von der dominanten Namenskonvention im Lifecycle-Cluster abweichen (Gerundium- oder Verb-Nomen-Form), und die Abweichung mit einer vorgeschlagenen kanonischen Form festhalten
- **SOLLTE** Befunde unterscheiden, die einen Release blockieren (fehlgeschlagene MUSS-Regeln, Critical per `review-plan`), von aufschiebbaren Befunden (fehlgeschlagenes SOLLTE, Warning oder Suggestion per `review-plan`)

### Format des konsolidierten Berichts

- **MUSS** alle folgenden Abschnitte in dieser Reihenfolge enthalten: YAML-Frontmatter, Executive Summary mit Top-Findings-Tabelle, Artefakt-Inventar-Tabelle, Abgrenzungs-Matrix, spec-induziertes Lücken-Inventar, Adoption-Friction-Analyse, Skill-vs-Agent-Klassifikations-Befunde, wellen-basierte Umsetzungs-Roadmap und ein Processing-Log
- **MUSS** im YAML-Frontmatter enthalten: `audit-type: skills-agents-sweep`, `target`, `scope` (Artefaktanzahl), `repo-revision`, `created` (ISO-Datum), `status: open` und `per-artefact-plans` (Anzahl)
- **MUSS** die Per-Artefakt-Plan-Pfade unter `.audits/skill-review/` und `.audits/agent-review/` im Executive Summary zitieren, damit Reviewer Cross-Cutting-Befunde zu konkreten Per-Artefakt-Nachweisen zurückverfolgen können
- **SOLLTE** eine Go/No-Go-Empfehlung im Executive Summary enthalten, die angibt, ob Critical-Befunde eine Release-Promotion blockieren; diese Empfehlung bleibt menschenlesbar und ist **KEIN** maschinell lesbares Release-Gate, sodass `release-publish-trigger` sein Gate-Set weiterhin an `spec/project/release-automation/` §Pre-publish verification verankert, statt ein Frontmatter-Feld aus dem Sweep-Bericht zu lesen

### Wellen-basierte Umsetzungs-Roadmap

- **MUSS** vorgeschlagene PRs nach Aufwand mal Wirkung sortieren und die Sortierungs-Begründung im Roadmap-Abschnitt explizit machen
- **MUSS** mechanische Sweep-PRs (ohne Spec-Änderung), Spec-Erweiterungs-PRs (Spec-Änderung ist Vorbedingung) und strukturelle Neu-Artefakt-PRs (erfordern das Authoring eines neuen Skills oder Agents) unterscheiden
- **MUSS** Ordnungs-Constraints zwischen Wellen ausdrücken, wenn eine spätere Welle von einer Spec-Änderung oder einem neuen Artefakt aus einer früheren Welle abhängt
- **SOLLTE** drei bis sechs Wellen vorschlagen, wobei Welle 1 die wirkungsstärksten mechanischen Fixes enthält und spätere Wellen strukturelle Änderungen enthalten, die vom Abschluss früherer Wellen abhängen

### Lifecycle

- **MUSS** genau einen offenen Sweep pro Repository zur gleichen Zeit aufrechterhalten; ein zweiter Sweep **DARF NICHT** eröffnet werden, bis der vorherige Sweep geschlossen ist
- Der committete konsolidierte Bericht mit `status: open` ist der Koordinations-Lock; Beitragende erkennen einen laufenden Sweep an der Existenz dieser Datei auf dem Default-Branch. Es ist kein separater Lock-Mechanismus definiert
- **MUSS** durch einen Commit geschlossen werden, der die konsolidierte Berichtsdatei aus `.audits/skills-agents-sweep/` entfernt; die Commit-Message **MUSS** dem Muster `sweep(skills-agents-sweep): close <Slug>--<Wellen-Zusammenfassung>` folgen, wobei `<Wellen-Zusammenfassung>` beschreibt, welche Wellen umgesetzt oder zurückgestellt wurden
- **MUSS** im Processing-Log des konsolidierten Berichts pro Wellen-Abschluss einen Eintrag festhalten mit Datum, Wellen-Kenner, durchgeführter Aktion und Verifikations-Methode
- **SOLLTE** als veraltet gelten und eine Neu-Eröffnung erfordern, wenn er mehr als sechs Monate lang offen war ohne einen Processing-Log-Eintrag

### Beziehung zu anderen Specs

- **MUSS** `spec/claude/skill-review/` und `spec/claude/agent-review/` als Verfahren für Per-Artefakt-Reviews referenzieren, die in Sweep-Phase 1 beauftragt werden; ihre Anforderungen werden hier nicht wiederholt
- **MUSS** `spec/claude/review-plan/` für das Per-Artefakt-Plan-Format referenzieren; seine Anforderungen werden hier nicht wiederholt
- **DARF NICHT** Prüfungen duplizieren, die bereits durch `skill-review` oder `agent-review` abgedeckt sind; die Cross-Cutting-Analyse umfasst nur Dimensionen, die das gleichzeitige Betrachten des gesamten Inventars erfordern
- **SOLLTE** mit `spec/project/spec-drift-audit/` koordinieren, indem festgehalten wird, dass `spec-drift-audit` den Inhaltsdrift von Spec-Dateien abdeckt, während `skills-agents-sweep` Artefakt-zu-Spec-Bindungs-Lücken abdeckt; die beiden Specs haben unterschiedliche Scopes mit komplementären Befunden und bleiben deshalb getrennte, gegenseitig referenzierte Verfahren statt sich einen kombinierten Einstiegspunkt zu teilen

## Acceptance Criteria

- [ ] Jeder konsolidierte Sweep-Bericht unter `.audits/skills-agents-sweep/` enthält alle Pflicht-Abschnitte in der vorgeschriebenen Reihenfolge, und das YAML-Frontmatter enthält alle Pflichtfelder
- [ ] Jede in der Roadmap vorgeschlagene Welle ist entweder mit einem PR-Verweis umgesetzt, mit einem Issue-Verweis zurückgestellt oder mit einer Begründung explizit zurückgezogen
- [ ] Kein Skill oder Agent, der in einer "Don't use for ... use X instead"-Klausel irgendwo im Plugin referenziert wird, zeigt auf einen nicht-existenten Artefakt-Slug
- [ ] Der jüngste konsolidierte Sweep-Bericht wurde innerhalb der letzten sechs Monate eröffnet, oder ein Sweep ist aktuell offen
- [ ] Jeder im Executive Summary zitierte Per-Artefakt-Plan-Pfad zeigt zum Zeitpunkt der Berichterstellung auf eine existierende Datei unter `.audits/skill-review/` oder `.audits/agent-review/`
- [ ] Das Processing-Log im konsolidierten Bericht enthält pro geschlossener Welle einen Eintrag mit Datum, Wellen-Kenner, Aktion und Verifikations-Methode

## Open Questions

_Derzeit keine._
