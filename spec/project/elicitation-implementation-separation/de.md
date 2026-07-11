# Trennung von Anforderungserfassung und Umsetzung

Status: draft
Portfolio-Scope: portfolio

## Context

Leser: Mitwirkende, die unter der Arbeitsweise des Portfolios arbeiten — die Person,
die Anforderungen erfasst (der *Elicitor*), der Reviewer, der den Anforderungs-Pull-Request
freigibt, und die Spezialisten, die später gegen die gemergten Anforderungen umsetzen.
Diese Spec verankert einen **optionalen, benannten Arbeitsmodus**, der die
**Anforderungserfassung** (*Bearbeitung*) sauber von der **Umsetzung** (*Implementation*)
trennt.

Das Portfolio trennt Analyse und Umsetzung bereits *innerhalb eines einzelnen
orchestrierten Laufs*: `spec/project/issue-orchestration/` erfasst ein Issue, elicitiert
oder bestätigt seine Anforderungen, zerlegt sie und dispatcht erst dann die Spezialisten —
alles in einem Worktree, einem Durchlauf, einem Pull-Request. Das funktioniert, wenn
Anforderungen und Umsetzung von einer mitwirkenden Person in einem Zug zusammen bearbeitet
werden.

Was dieses Muster nicht bietet, ist ein Weg, die **erfassten Anforderungen zu einem
eigenständigen, gemergten, permalink-fähigen Artefakt** zu machen, das *vor* jeder Umsetzung
landet, sodass eine andere mitwirkende Person — oder dieselbe, später — ein commit-stabiles
Anforderungsdokument aufgreifen und umsetzen kann. Manchmal ist die Erfassung die wertvolle,
prüfbare Arbeit für sich; die Umsetzung wird aufgeschoben, an einen Spezialisten übergeben
oder unabhängig eingeplant. Ohne einen benannten Modus ist diese Trennung improvisiert:
Anforderungen und Code landen im selben Pull-Request, die Anforderungen existieren nie als
eigenständig prüfbares Artefakt, und die Übergabe von „was wir zu bauen vereinbart haben"
zu „wer es baut" bleibt informell.

Diese Spec benennt diese Trennung und schreibt ihren Ablauf vor. Sie macht die Trennung
**nicht** verpflichtend: Wer Anforderungen und Umsetzung zusammen bearbeiten will, bleibt
auf dem integrierten `issue-orchestration`-Pfad. Der Modus ist ein Werkzeug, zu dem eine
mitwirkende Person greifen **MAY [KANN]**, wenn sie will, dass die Anforderungen ein
gemergtes Artefakt sind, bevor die Umsetzung beginnt.

## Goals

- Dem Portfolio einen **benannten, optionalen Arbeitsmodus** geben, der die
  Anforderungserfassung von der Umsetzung trennt, sodass Mitwirkende ein gemeinsames
  Vokabular und einen vorgegebenen Ablauf haben, wenn sie die beiden Phasen trennen
- Die erfassten Anforderungen zu einem **eigenständigen, gemergten, commit-stabilen
  Artefakt** machen, das vor jeder Umsetzung landet, sodass es per Permalink referenziert
  und an einen Spezialisten übergeben werden kann
- Einen **4-Schritt-Ablauf** vorschreiben — dedizierter Erfassungs-Working-Copy →
  Pull-Request nur des Anforderungsdokuments → Tracking-Issue im umsetzungs-ownenden Repo →
  Umsetzung durch Spezialisten — als verbindliche Sequenz *innerhalb* des Modus, ohne den
  Modus jemandem aufzuzwingen
- Den Modus **komplementär zu `issue-orchestration`** halten, nicht konkurrierend: dieselbe
  Disziplin „Erfassung vor Umsetzung", gehoben zu einem Cross-Working-Copy-/Cross-Pull-Request-
  Workflow, auf dem Orchestration aufbauen MAY [KANN]
- Betroffene Dokumentation aktuell halten: Wenn Spezialisten umsetzen, wird jedes betroffene
  Doc/Spec im selben Pull-Request aktualisiert, reviewer-verifiziert

## Non-Goals

- **Die Trennung verpflichtend machen.** Diese Spec erzwingt die Trennung nie. Sie sagt
  „*so* trennst du sauber, wenn du dich dafür entscheidest", nicht „du **MUSST** immer
  trennen". Der integrierte Pfad (`issue-orchestration`) bleibt vollständig gültig.
- **Anforderungserfassung neu definieren.** `spec/project/requirements-elicitation/` bleibt
  maßgeblich dafür, *wie* Anforderungen erfasst werden, und für den `U_gate`-/`τ_high`-
  Confidence-Vertrag; diese Spec positioniert die Erfassung nur als separate, gemergte Phase
  und konsumiert die Artefakt-Form jener Spec.
- **Die Worktree-Disziplin neu definieren.** `spec/project/parallel-working-copies/` bleibt
  maßgeblich dafür, wie ein dedizierter Working-Copy erstellt und abgegrenzt wird; diese Spec
  verlangt nur, dass Schritt 1 einen verwendet.
- **Pull-Request- oder Merge-Regeln neu definieren.** `spec/project/pull-request-workflow/`
  und `spec/project/branching-model/` bleiben maßgeblich; der Anforderungs-Pull-Request aus
  Schritt 2 durchläuft diese Gates unverändert.
- **Ein Tracking-Issue-Template vorschreiben.** Diese Spec fixiert das *Minimal-Feldset*, das
  das Tracking-Issue tragen muss (unten); ob ein festes Issue-Template oder ein Label-Set es
  hinterlegt, bleibt dem adoptierenden Repo überlassen.
- **Die Umsetzungs-Spezialisten vorschreiben.** Welcher Spezialist in Schritt 4 umsetzt, wird
  vom umsetzungs-ownenden Repo aufgelöst (etwa über `issue-orchestration`'s Runtime-Spezialisten-
  Lookup), nicht hier fixiert.

## Requirements

### Der Arbeitsmodus und sein Ablauf

- **MUST [MUSS]** „Trennung von Anforderungserfassung und Umsetzung" als **optionalen,
  benannten Arbeitsmodus** behandeln, nicht als verpflichtendes Gate: Eine mitwirkende Person
  **MAY [KANN]** ihn wählen, wenn sie die Anforderungserfassung (*Bearbeitung*) von der
  Umsetzung (*Implementation*) trennen will; das Portfolio **MUST NOT [DARF NICHT]** ihn
  verlangen, damit eine Änderung gültig ist
- **MUST [MUSS]**, wenn der Modus gewählt wird, einem **4-Schritt-Ablauf** als verbindlicher
  Sequenz *innerhalb des Modus* folgen: (1) Anforderungserfassung in einem dedizierten
  Working-Copy; (2) ein Pull-Request, der **nur** das Anforderungsdokument in den Default-Branch
  landet; (3) ein Tracking-Issue, das das gemergte Dokument referenziert, erstellt im
  umsetzungs-ownenden Repo; (4) Umsetzung durch Spezialisten. Die Schritte **MUST [MÜSSEN]** in
  dieser Reihenfolge laufen — das gemergte Anforderungsdokument ist Vorbedingung für das
  Tracking-Issue, das Vorbedingung für die Umsetzung ist
- **MUST [MUSS]** **portfolio-weit** autoriert sein: eine Spec unter `spec/project/`, von
  adoptierenden Repos geerbt gemäß `spec/project/portfolio-inherited-spec-layer/`, die den Modus
  als portfolio-weite Arbeitsweise beschreibt, nicht als repository-lokale Konvention

### Schritt 1 — Erfassung in einem dedizierten Working-Copy

- **MUST [MUSS]**, wenn der Modus gewählt wird, die Anforderungserfassung in ihrem **eigenen
  dedizierten Working-Copy** (einem Worktree gemäß `spec/project/parallel-working-copies/`)
  durchführen, dessen **einziges Deliverable** das Anforderungsdokument
  (`project/requirements/<slug>.md`) ist; in diesem Working-Copy findet keine Umsetzung statt
- **SHOULD [SOLLTE]** dieses Dokument über `spec/project/requirements-elicitation/` (die
  `requirements-elicit`-Methodik) erzeugen, sodass das gemergte Artefakt ein bestätigtes
  Verständnis (seinen `U_gate`-/Confidence-Record) trägt statt unvalidierter Prosa

### Schritt 2 — Pull-Request des Anforderungsdokuments

- **MUST [MUSS]** in Schritt 2 einen Pull-Request öffnen, der **nur das Anforderungsdokument**
  in den Default-Branch (`develop`) landet, **bevor irgendeine Umsetzung beginnt**; das gemergte,
  permalink-fähige Dokument ist das Übergabe-Artefakt. Der Pull-Request durchläuft
  `spec/project/pull-request-workflow/` unverändert
- **MUST NOT [DARF NICHT]** Umsetzungsänderungen (Code, Specs über das Anforderungsdokument
  hinaus, Konfiguration) in den Schritt-2-Pull-Request aufnehmen; sie zu vermischen unterläuft
  die Trennung, für die der Modus existiert

### Schritt 3 — Tracking-Issue mit stabiler Referenz

- **MUST [MUSS]** das Tracking-Issue in **dem Repo erstellen, das das umzusetzende Artefakt
  ownt** — verallgemeinert als „das Repo, das das umzusetzende Artefakt ownt"; es ist nicht
  zwingend das Repo, in dem die Erfassung stattfand
- **MUST [MUSS]** das Tracking-Issue mindestens tragen lassen: (a) einen **commit-stabilen
  Permalink zum gemergten Anforderungsdokument** (die load-bearing Referenz — ein auf den
  Merge-Commit gepinnter Permalink, kein branch-relativer Link); (b) einen kurzen **Titel /
  eine Beschreibung** der umzusetzenden Änderung; (c) einen Pointer auf den/die **verantwortlichen
  Spezialisten** oder den erwarteten Umsetzungsansatz; (d) die explizite **Charge, betroffene
  Docs aktuell zu halten** — die Brücke zum Doc-Currency-Vertrag von Schritt 4

### Schritt 4 — Umsetzung durch Spezialisten

- **MUST [MUSS]** die Umsetzung durch **Spezialisten** (nicht den Elicitor) durchführen lassen,
  die die nötigen Änderungen aus dem gemergten Anforderungsdokument einschätzen und ausführen
- **MUST [MUSS]**, wenn Spezialisten umsetzen, **jedes betroffene Doc/Spec im selben Pull-Request
  wie die Umsetzung** aktualisieren, und der Pull-Request-Reviewer **MUST [MUSS]** dies als Teil
  der Freigabe verifizieren; Dokumentations-Drift ist nicht zugelassen. Das ist die konkrete,
  acceptance-testbare Bedeutung von „die Docs aktuell halten"

### Beziehung zu `issue-orchestration` (komplementär, nicht konkurrierend)

- **MUST [MUSS]** diesen Modus als **komplementär zu** `spec/project/issue-orchestration/`
  positionieren, das Analyse/Erfassung von Umsetzung bereits *innerhalb eines einzelnen
  orchestrierten Laufs* trennt: Dieser Modus hebt dieselbe Trennung zu einem **eigenständigen,
  opt-in Cross-Working-Copy-/Cross-Pull-Request-Workflow** — Erfassung als separates, gemergtes
  Artefakt vor jeder Umsetzung —, auf dem Orchestration aufbauen **MAY [KANN]**. Er **MUST NOT
  [DARF NICHT]** als konkurrierende Regel geframt werden; eine mitwirkende Person wählt je
  Änderung den integrierten oder den getrennten Pfad, und beide bleiben gültig

### Umfang der Modus-Wahl und aufgeschobene Mechanik

- **MAY [KANN]** nach Ermessen der mitwirkenden Person gewählt werden: Weil der Modus opt-in ist,
  gibt es **keine Trivial-Ausnahme zu definieren** — die Schwelle dafür, was „substantiell genug"
  ist, um die Phasen zu trennen, bleibt dem Urteil der mitwirkenden Person überlassen, nicht von
  dieser Spec fixiert
- **MAY [KANN]** den Fallback für „kein passender Spezialist existiert" für Schritt 4 — ob der
  Elicitor selbst umsetzt oder die Arbeit zurückgeroutet wird — dem Umsetzungsschritt überlassen;
  diese Spec fixiert diesen Fallback nicht
- **MAY [KANN]** die exakte Tracking-Issue-Mechanik (ein festes Issue-Template, ein Label-Set) dem
  adoptierenden Repo überlassen; nur das Minimal-Feldset aus Schritt 3 ist verbindlich

### Platzierung dieser Spec (entschieden)

- Die Platzierung dieser Arbeitsweise-Änderung — eine neue Standalone-Spec versus ein
  Amendment / Cross-Reference innerhalb bestehender Arbeitsweise-Specs — wurde **zugunsten dieser
  Standalone-Spec entschieden** (`spec/project/elicitation-implementation-separation/`), sodass
  der benannte Modus und sein 4-Schritt-Ablauf an einem kohärenten Ort leben statt über
  `parallel-working-copies`, `requirements-elicitation` und `issue-orchestration` fragmentiert zu
  werden. Jene Specs bleiben für ihren eigenen Scope maßgeblich und werden hier cross-referenziert

## Acceptance Criteria

- [ ] Der Modus ist als optional und benannt dokumentiert; keine Portfolio-Spec macht die
  Trennung von Erfassung und Umsetzung zur Vorbedingung dafür, dass eine Änderung gültig ist
- [ ] Wenn der Modus gewählt wird, sind die vier Schritte vorhanden und geordnet: ein dedizierter
  Erfassungs-Working-Copy, ein Pull-Request nur der Anforderungen, ein Tracking-Issue, das das
  gemergte Dokument referenziert, und Umsetzung durch Spezialisten
- [ ] Der Schritt-2-Pull-Request enthält nur das Anforderungsdokument
  (`project/requirements/<slug>.md`) und keine Umsetzungsänderung
- [ ] Das Schritt-3-Tracking-Issue trägt einen commit-stabilen Permalink zum gemergten
  Anforderungsdokument, einen Titel/eine Beschreibung, einen Spezialisten-/Ansatz-Pointer und die
  Doc-Currency-Charge
- [ ] Der Schritt-4-Umsetzungs-Pull-Request aktualisiert jedes betroffene Doc/Spec im selben
  Pull-Request, und der Reviewer bestätigt dies als Teil der Freigabe
- [ ] Die Spec referenziert `issue-orchestration` als komplementär (nicht konkurrierend) und
  stellt fest, dass eine mitwirkende Person je Änderung den integrierten oder den getrennten Pfad
  wählt
- [ ] Die Spec ist unter `spec/project/` mit `Portfolio-Scope: portfolio` autoriert, sodass
  adoptierende Repos sie gemäß `portfolio-inherited-spec-layer` erben

## Open Questions

- Der Fallback, wenn **kein passender Spezialist existiert** für Schritt 4 (Elicitor setzt selbst
  um versus Zurückrouten der Arbeit), ist bewusst dem Umsetzungsschritt überlassen; ob das
  Portfolio einen Default fixieren sollte, ist aufgeschoben, bis genug echte Läufe zur Kalibrierung
  existieren.
- Ob das Tracking-Issue aus Schritt 3 durch ein **festes Issue-Template / Label-Set** hinterlegt
  sein sollte (statt nur durch das verbindliche Minimal-Feldset), ist der Präferenz der
  adoptierenden Repos überlassen.
- Ob `issue-orchestration` einen expliziten „Resume aus einem gemergten Anforderungs-Artefakt"-
  Einstiegspfad erhalten sollte, der ein Schritt-2-Dokument direkt konsumiert, ist als natürliche
  Erweiterung notiert, aber hier nicht verlangt.
