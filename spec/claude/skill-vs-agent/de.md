# Skill- vs. Agent-Entscheidung

Status: draft

## Kontext
Claude Code bietet in diesem Plugin zwei Formate für wiederverwendbare Capabilities: **Skills** (unter `skills/<name>/SKILL.md` autoriert) und **Agents** (unter `agents/<name>.md` autoriert). Die `skill-management`-Spezifikation regelt die On-Disk-Struktur von Skills; die `agent-management`-Spezifikation dasselbe für Agents. Keine davon beantwortet die vorgelagerte Frage: **welches Format passt zu einer gegebenen Capability?** Ohne eine gemeinsame Entscheidungsregel driften Portfolio-Autoren — dieselbe Aufgabenklasse erscheint in einem Repository als Skill und in einem anderen als Agent, oder dieselbe Capability wird doppelt ausgeliefert, weil niemand entscheiden konnte. Der Abschnitt „Specialized-agent dispatch for remediation" in der `workflow-health`-Spezifikation setzt bereits ein Skill-orchestriert-Agent-führt-aus-Muster voraus; diese Spezifikation kodifiziert die Regel, die diese Voraussetzung portfolio-weit konsistent macht.

## Ziele
- Jede neue Claude-Code-Capability in diesem Plugin wird entweder als Skill oder als Agent autoriert, nie als beides, auf Basis einer deterministischen Entscheidungsregel
- Ähnliche Aufgaben in verschiedenen Repositories landen auf demselben Artefakt-Typ — kein Drift zwischen „hier Skill, dort Agent" für gleichwertige Arbeit
- Die Wahl wird im Artefakt selbst dokumentiert, sodass spätere Lesende verstehen, warum sie getroffen wurde, statt raten zu müssen
- Das Skill-als-Orchestrator- / Agent-als-Ausführer-Muster ist eine explizit beschriebene First-Class-Option und keine Zufallserscheinung
- Grenzfälle tauchen als offene Fragen in dieser Spezifikation auf und nicht als stillem Drift im Artefakt-Baum

## Nicht-Ziele
- On-Disk-Struktur, Benennung, Frontmatter oder Templates für eines der beiden Artefakte (abgedeckt durch `skill-management` und `agent-management`)
- Plugin-Distribution und Marketplace-Mechanik (abgedeckt durch diese Spezifikationen)
- Plugin-Level-Schnittführung — wann Capabilities in ein Plugin gegenüber mehreren gehören und wie ein einzelnes Plugin überschaubar bleibt, während es wächst (abgedeckt durch `plugin-scoping`)
- Welche konkreten Tools ein Agent im `tools`-Feld deklariert (eine pro-Agent-Scope-Entscheidung, keine portfolio-weite Regel)
- Discovery und Katalog-Rendering im MkDocs-Site (abgedeckt durch `skill-agent-catalog`)
- Das Routing-Verhalten der Claude-Code-Laufzeit selbst — diese Spezifikation regelt Autoring-Entscheidungen, nicht Laufzeit-Dispatch

## Anforderungen

### Entscheidungsdimensionen
Jede Kandidat-Capability wird entlang der folgenden Dimensionen bewertet. Jede Dimension hat einen natürlichen Bias in Richtung eines Artefakt-Typs, festgehalten in der zweiten und dritten Spalte. Die Format-Wahl eines autorierten Artefakts **MUSS [MUST]** gegen diese Tabelle begründbar sein.

| Dimension | Bias Richtung Skill | Bias Richtung Agent |
|---|---|---|
| **Kontextzugriff** | Benötigt den Zustand der Haupt-Konversation (offener PR, jüngste Diffs, vorherige User-Turns) | Eigenständige Eingabe; keine Konversations-Historie erforderlich |
| **Interaktivität** | User-Bestätigung oder Zwischen-Freigaben werden mitten im Fluss erwartet | Fire-and-forget — der Elternprozess dispatcht einmal und konsumiert einen strukturierten Report |
| **Parallelität** | Sequenziell, einer nach dem anderen im Haupt-Thread | Mehrere Instanzen können parallel laufen, wenn sie in einem einzigen Tool-Call-Batch gesendet werden |
| **Tool-Oberfläche** | Die volle Tool-Oberfläche des aufrufenden Claude reicht aus | Ein engerer, deklarierter `tools`-Scope ist vorzuziehen (Prinzip der geringsten Rechte) |
| **Kontext-Fenster-Wirkung** | Ausgabe fließt natürlich in die Haupt-Konversation ein | Umfangreiche Reads / Suchen würden den Haupt-Kontext verschmutzen; Isolation ist ein Gewinn |
| **Spezialisierung** | Allgemeine Prozedur; ein fokussierter System-Prompt würde die Qualität nicht messbar verändern | Ein enger System-Prompt schärft die Ausgabequalität spürbar |
| **Lebenszyklus** | Besteht über die gesamte Konversation hinweg — kann mehrfach aufgerufen werden | Einmal-Aufgabe mit klarem Abschlusskriterium |
| **Latenz** | Schnelle Rückmeldung zählt; das separate Kontext-Fenster eines Subagents bringt Spin-up- und Round-Trip-Overhead | Latenz ist nicht kritisch; die Aufgabe kann out-of-band laufen und sich zurückmelden, wenn sie fertig ist |
| **Änderungs-Umfang** | Eine schnelle, gezielte Änderung im aktuellen Kontext | Eine größere eigenständige Arbeitseinheit mit wohldefinierter Eingabe und Ausgabe |

Diese Dimensionen folgen Anthropics offizieller Anleitung „Choose between subagents and the main conversation" ([R5](#referenzen)): leite Arbeit an die **Haupt-Konversation** (einen Skill), wenn sie häufiges Hin und Her braucht, wenn mehrere Phasen erheblichen Kontext teilen, wenn die Änderung **schnell und gezielt** ist oder wenn **Latenz** zählt; leite sie an einen **Subagent** (einen Agent), wenn die Aufgabe ausführliche Ausgabe erzeugt, die der Orchestrator nicht braucht, wenn Tool- oder Berechtigungs-Einschränkung erwünscht ist oder wenn die Arbeit eigenständig ist und eine Zusammenfassung zurückgibt. Die Zeilen **Latenz** und **Änderungs-Umfang** tragen die zwei Kriterien, die der Rest der Tabelle nicht bereits erfasst hatte. Von den Agent-seitigen Dimensionen rahmt Anthropic **Parallelisierung und Kontext-Management als die zwei *primären* Treiber** dafür, Arbeit in einen Subagent zu verlagern (Spezialisierung und Tool-Einschränkung sind Unterfälle des Kontext-Managements) ([R6](#referenzen)); die Zeilen **Parallelität** und **Kontext-Fenster-Wirkung** sind daher die tragenden, wenn ein Agent gewählt wird.

### Primäre Entscheidungsregel
- **MUSS [MUST]** einen **Skill** wählen, wenn die Capability eines der folgenden erfüllt:
  - Die Prozedur ist ein Schritt in einem größeren, vom Menschen geführten Workflow (PR erstellen, PR landen, Projekt scaffolden, Audit durchführen)
  - Mindestens einmal mitten im Fluss wird User-Bestätigung benötigt
  - Die Ausgabe soll natürlich, ohne strukturierte Report-Grenze, in den Kontext der Haupt-Konversation einfließen
  - Die Prozedur selbst dispatched einen oder mehrere Agents — der Orchestrator ist immer ein Skill
- **MUSS [MUST]** einen **Agent** wählen, wenn die Capability eines der folgenden erfüllt:
  - Die Aufgabe ist eigenständig mit wohldefinierter Eingabe und wohldefinierter Ausgabeform
  - Die Aufgabe ist ein Kandidat für parallele Ausführung neben anderer unabhängiger Arbeit
  - Kontext-Fenster-Schutz zählt, weil die Aufgabe große Read-, Such- oder Datei-Traversal-Volumina produziert
  - Tool-Einschränkung ist erwünscht (Read-only-Research, reiner Lint, reines Refactor) und würde Sicherheit oder Verhalten messbar verbessern
  - Ein spezialisierter, enger System-Prompt verbessert die Ausgabequalität der Aufgabe messbar
- **MUSS [MUST]** als Default einen **Skill** wählen, wenn die obigen Kriterien widersprüchlich oder echt mehrdeutig sind; die Begründung: Skills bleiben die menschlich sichtbare Oberfläche und können später Agents dispatchen, ohne Consumer-Workflows umzustrukturieren, während ein Agent nicht zu einem Skill werden kann, ohne seinen Isolations-Kontrakt zu verlieren
- **MUSS [MUST]**, wenn Tool-Einschränkung **und** Mitten-im-Fluss-Interaktivität beide zutreffen, einen **Skill** autorieren und `allowed-tools` (gemäß `skill-management`) für freiwillige Tool-Disziplin deklarieren; ein Agent mit Pause-/Resume-Protokoll ist **verboten**, weil ein Agent in einem isolierten Subagent-Kontext läuft und keinen stabilen Weg hat, Skill-seitige Interaktivität an die Elternkonversation zurückzuspiegeln (siehe §Hybrid-Muster). Dies ist eine direkte Folge der obigen Default-zu-Skill-Regel, kein separater Ausweg.

### Hybrid-Muster: Skill orchestriert, Agent führt aus
- **MUSS [MUST]** Implementierungsarbeit, die innerhalb eines umfassenderen Workflows sitzt, als `skill → Agent(subagent_type=<agent>)` modellieren statt als monolithischen Skill, sobald mindestens ein Agent-seitiges Kriterium (Kontext-Fenster-Schutz, Parallelität, Tool-Einschränkung, Spezialisierung) auf den Implementierungsschritt zutrifft
- **DARF NICHT [MUST NOT]** dieses Muster umkehren — ein Agent **DARF NICHT [MUST NOT]** das Skill-Tool im Namen des Users aufrufen, weil Agents in einem isolierten Subagent-Kontext laufen und keinen stabilen Weg haben, Skill-seitige Interaktivität an die Elternkonversation zurückzuspiegeln
- **DARF NICHT [MUST NOT]** voraussetzen, dass ein Agent einen weiteren Subagent spawnen kann — Claude-Code-Subagents **können keine anderen Subagents spawnen** ([R1](#referenzen)). Der Skill bleibt die einzige Ebene, auf der Fan-out passiert; ein Agent, der Sub-Arbeit braucht, faltet sie entweder in den eigenen Kontext oder gibt die Kontrolle an den aufrufenden Skill zurück
- **SOLLTE [SHOULD]** die Rolle des Skills auf Orchestrierung, User-Interaktion und Validierung der Agent-Ausgabe beschränken; der Agent übernimmt das direkte Lesen, Bearbeiten oder Recherchieren
- **SOLLTE [SHOULD]** mehrere Agents sequenziell aus einem Skill verketten, wenn die Verantwortlichkeiten sich natürlich aufteilen (zum Beispiel: ein YAML-Fix-Agent, dann ein Git-Commit-Agent, dann der `pull-request-create`-Skill — einen weiteren Skill aus einem Skill im selben Thread aufzurufen ist zulässig)
- Der Abschnitt „Specialized-agent dispatch for remediation" der `workflow-health`-Spezifikation ist die kanonische portfolio-weite Instanz dieses Musters; Änderungen an diesem Abschnitt **MÜSSEN [MUST]** mit der hier deklarierten Regel konsistent bleiben

### Geforkte Skills: eine dritte Option, kein viertes Artefakt

Claude Code unterstützt, einen Skill selbst in einem isolierten Subagent-Kontext laufen zu lassen, indem `context: fork` plus `agent: <type>` im Frontmatter des Skills gesetzt werden ([R2](#referenzen)). Der Body des Skills wird zum Prompt, der den geforkten Subagent treibt; die eigene Tool-Oberfläche des Skills wird durch die Tools und das Modell des genannten Agent-Typs ersetzt. Dies ist die **Inverse** zum `skills:`-Preload-Feld eines Subagents — beide ergeben dieselbe Komposition über unterschiedliche Eigentümerschaft.

- **DARF [MAY]** eine Capability als Skill mit `context: fork` ausliefern statt als separate Agent-Datei, wenn die Capability natürlich **single-shot ist, in den Subagent-Isolations-Vertrag passt UND** sonst Orchestrierungslogik duplizieren würde, die ein bestehender Skill bereits besitzt
- **DARF NICHT [MUST NOT]** `context: fork` als Weg behandeln, um die Skill-vs-Agent-Regel zu umgehen — die Wahl wird weiterhin von der Tabelle der Entscheidungsdimensionen geregelt; der Fork ändert nur, *wie* ein gewählter Skill ausgeführt wird, nicht ob die Capability überhaupt ein Skill hätte sein sollen
- **SOLLTE [SHOULD]**, bei der Wahl zwischen „neuer Agent" und „bestehender Skill bekommt einen `context: fork`-Modus", letzteres nur dann bevorzugen, wenn der neue Modus nicht-triviale Logik mit dem bestehenden Verhalten des Skills teilt; sonst bleibt der neue Agent ein separates Artefakt, und die Entscheidungsregel von `skill-vs-agent` greift normal

### Duplikat-Vermeidung
- **DARF NICHT [MUST NOT]** einen Skill und einen Agent ausliefern, die innerhalb des `nolte-shared`-Plugins gleichwertige Capabilities bereitstellen; genau ein Artefakt pro Capability ist das Invariant
- **MUSS [MUST]** vor dem Autoring eines neuen Artefakts die bestehenden Skills unter `skills/` und Agents unter `agents/` auf eine gleichwertige oder nahezu gleichwertige Capability prüfen (jede `description`-Zeile lesen; nicht allein auf Namens-Ähnlichkeit verlassen)
- Der kanonische Mechanismus für diese plugin-interne Capability-Äquivalenz-Prüfung zum Audit-Zeitpunkt ist der Boundary-Matrix-Schritt des `skills-agents-sweep`-Skills: ein **semantisches Lesen jeder `description`-Zeile**, das jedes überlappende Paar als Konflikt, benachbart oder Kette klassifiziert. Keyword-Schnitt oder Embedding-Ähnlichkeit **DARF [MAY]** nur als optionaler Vorfilter dienen, der die Kandidatenpaare für das semantische Lesen einengt; keiner von beiden **DARF [MAY]** an die Stelle der Entscheidung selbst treten
- **SOLLTE [SHOULD]** bei wirklich unscharfer Grenze zwischen einem bestehenden Artefakt und einem neuen Vorschlag einen Merge, eine Umbenennung oder eine klarere Trennung als Teil des Autoring-PRs vorschlagen — nie stillschweigend ein drittes, sich überschneidendes Artefakt ausliefern
- **KANN [MAY]** gleichwertig wirkende Artefakte über **verschiedene** Plugins hinweg tolerieren; diese Regel ist auf `nolte-shared` beschränkt, und nachgelagerte Plugins verantworten ihre eigene De-Duplikation

### Entscheidungsprozess für Autoren
1. **Die Capability in einem Satz formulieren.** Gelingt keine Ein-Satz-Formulierung, ist die Capability zu breit — sie wird vor Anwendung der Regel aufgeteilt.
2. **Die Tabelle der Entscheidungsdimensionen durchgehen** und je Dimension den Bias notieren. Der Bias einer Dimension wiegt mehr, wenn die Dimension für die Aufgabe tragend ist (Parallelität zählt nur, wenn die Aufgabe tatsächlich mehrfach läuft; Tool-Einschränkung zählt nur, wenn die Aufgabe Credentials berührt).
3. **Die primäre Entscheidungsregel anwenden.** Passen beide Wege, ist der Default ein Skill.
4. **Auf Duplikate prüfen** gegen bestehende Skills und Agents. Stoppen, falls ein gleichwertiges Artefakt bereits existiert; es erweitern, umbenennen oder ablösen statt ein neues auszuliefern.
5. **Das Artefakt autorieren** gemäß `skill-management` oder `agent-management`.
6. **Die Wahl dokumentieren** im Artefakt-Body (siehe „Rationalen-Dokumentation" unten).

### Rationalen-Dokumentation
- **MUSS [MUST]** im Artefakt-Body — nicht nur in der Frontmatter-`description` — einen kurzen Rationalen-Abschnitt enthalten (ein kurzer Absatz oder eine Zwei-bis-Vier-Punkte-Liste), der die entscheidenden Dimensionen benennt, die zur Skill-vs-Agent-Wahl geführt haben
- **SOLLTE [SHOULD]** mindestens eine Dimension nennen, die in die andere Richtung gezeigt hat, und den Grund, warum sie überwogen wurde; das Fehlen einer Gegendimension-Notiz impliziert, dass die Wahl unumstritten war
- Die Ein-Dimensions-Messlatte ist beabsichtigt und bewusst ein hartes **MUSS [MUST]**, während die Zwei-Dimensions-Struktur (eine zweite benannte Dimension plus eine Gegendimension) bewusst nur ein **SOLLTE [SHOULD]** ist: zwei benannte Dimensionen bei einer wirklich einseitigen Wahl zu erzwingen erzeugt Füll-Prosa statt eines schärferen Audits, daher wird die Messlatte nicht angehoben
- **KANN [MAY]** ein konkretes Schwester-Artefakt als Präzedenz referenzieren (zum Beispiel: „folgt demselben Orchestrator-Muster wie `pull-request-create`")
- Die Platzierung im Body liegt im Ermessen der Autorin / des Autors; sinnvolle Orte sind direkt unter der obersten Überschrift oder als kurzer Fuß unmittelbar vor den Hard Rules

### Überschrift des Rationalen-Abschnitts
- **MUSS [MUST]** bei Skills exakt die Überschrift `## Why this is a skill, not an agent` für den Rationalen-Abschnitt verwenden; alternative Formulierungen (beispielsweise `## Rationale (why a skill, not an agent)`, `## Rationale`) sind nicht konform
- **MUSS [MUST]** bei Agents exakt die Überschrift `## Why this is an agent, not a skill` für den Rationalen-Abschnitt verwenden
- **KANN [MAY]** zusätzliche Rationalen-Unterüberschriften hinzufügen, wenn ein bestimmter Skill oder Agent eine themenspezifische Rationalen-Dimension besitzt (z. B. ist `## Why this is one skill, not three` als zusätzliche H2 neben der Pflichtüberschrift `## Why this is a skill, not an agent` zulässig), aber die Pflichtüberschrift MUSS vorhanden sein
- Begründung: eine deterministische Überschrift ermöglicht `grep`-basierte Portfolio-Audits und stellt eine Single Source of Truth für die Abschnitts-Semantik dar

### Portfolio-weite Konsistenz
- **MUSS [MUST]** eine Capability-Klasse, die in drei oder mehr Consumer-Repositories wiederkehrt, als Plugin-Level-Artefakt ausliefern statt als projekt-lokale Kopien; die Drei-Wiederholungs-Konstante gehört der `continuous-improvement`-Spezifikation (der allgemeinsten Formulierung der Regel), und `workflow-health`, `portfolio-management` sowie diese Spezifikation verweisen alle darauf. Der Schwellwert ändert sich nur im Gleichschritt über alle vier Spezifikationen hinweg — diese Spezifikation **DARF NICHT [MUST NOT]** auf eine andere Zahl abweichen. Die obige Entscheidungsregel bestimmt weiterhin, ob das Plugin-Level-Artefakt ein Skill oder ein Agent ist
- **SOLLTE [SHOULD]** ein neues Artefakt am Artefakt-Typ bestehender Peers desselben funktionalen Clusters (PR-Management, Audit, Lint, Release-Tooling) ausrichten — wenn alle bestehenden Peers Skills sind, ist das neue ein Skill, es sei denn eine Dimension erzwingt den anderen Weg
- **SOLLTE [SHOULD]** das optionale `tags`-Feld (gemäß `skill-management` / `agent-management`) als maschinell prüfbares Signal für Peer-Cluster-Zugehörigkeit nutzen — Artefakte, die denselben Tag teilen, bilden im Tag-Index des Katalogs ein Cluster, sodass die Cluster-Ausrichtung aus dem Frontmatter verifizierbar ist und nicht auf Namens-Ähnlichkeit beruht
- **KANN [MAY]** die Reklassifizierung eines bestehenden Artefakts (Skill → Agent oder umgekehrt) vorschlagen, wenn wiederholte Nutzung zeigt, dass die ursprüngliche Wahl falsch war; eine solche Reklassifizierung ist eine Breaking Change für Consumer und **MUSS [MUST]** als neues Artefakt plus Deprecation-Hinweis auf dem alten ausgeliefert werden, nie als stiller Format-Wechsel

## Akzeptanzkriterien
- [ ] Jeder Skill unter `skills/` in diesem Plugin enthält einen Rationalen-Abschnitt in `SKILL.md`, der mindestens eine entscheidende Dimension für die Skill-gegen-Agent-Wahl benennt
- [ ] Jeder Agent unter `agents/` in diesem Plugin enthält einen Rationalen-Abschnitt im Markdown-Body, der mindestens eine entscheidende Dimension für die Agent-gegen-Skill-Wahl benennt
- [ ] Keine zwei Artefakte in diesem Plugin (beliebige Mischung aus Skill und Agent) teilen sich eine gleichwertige Capability-Aussage — ein Audit, das jede `description`-Zeile liest, findet keine Äquivalente
- [ ] Kein Agent in diesem Plugin ruft das Skill-Tool im Namen des Users auf, nachweisbar durch Grep auf Agent-System-Prompt-Bodies nach `Skill(` oder äquivalenten Skill-Dispatch-Formulierungen
- [ ] Für jede Capability, die in drei oder mehr Consumer-Repositories wiederkehrt, existiert genau ein `nolte-shared`-Artefakt (Skill oder Agent), das sie abdeckt
- [ ] Jede Reklassifizierung eines bestehenden Artefakts (Skill ↔ Agent) wird als neues Artefakt plus Deprecation-Hinweis auf dem alten ausgeliefert, nie als In-place-Format-Wechsel
- [ ] Der Abschnitt „Specialized-agent dispatch for remediation" der `workflow-health`-Spezifikation bleibt mit der hier deklarierten Hybrid-Muster-Regel konsistent; künftige Divergenzen werden zugunsten dieser Spezifikation aufgelöst
- [ ] Kein Agent in diesem Plugin versucht, einen weiteren Subagent zu spawnen (verifizierbar durch Grep auf Agent-Bodies nach `Agent(`, `subagent_type` oder äquivalenten Dispatch-Formulierungen)
- [ ] Jeder Skill, der `context: fork` deklariert, dokumentiert in seinem Rationalen-Abschnitt, warum die Fork-Variante einer Schwester-Agent-Datei vorzuziehen ist
- [ ] Die Tabelle der Entscheidungsdimensionen ist konsistent mit der offiziellen Anthropic-Anleitung dazu, wann die Haupt-Konversation gegenüber einem Subagent zu wählen ist ([R3](#referenzen), [R5](#referenzen)); Divergenzen werden zugunsten dieser Spezifikation aufgelöst, aber in `## Offene Fragen` erläutert
- [ ] Die Tabelle der Entscheidungsdimensionen enthält die Dimensionen **Latenz** und **Änderungs-Umfang**, die Anthropics Kriterien aus „Choose between subagents and the main conversation" abbilden ([R5](#referenzen))

## Referenzen

- [R1] Create custom subagents, Claude-Code-Doku (Subagents können keine Subagents spawnen) — <https://code.claude.com/docs/en/sub-agents>
- [R2] Extend Claude with skills, Claude-Code-Doku (`context: fork`) — <https://code.claude.com/docs/en/skills>
- [R3] Building Effective AI Agents, Anthropic Engineering — <https://www.anthropic.com/research/building-effective-agents>
- [R4] Equipping agents for the real world with Agent Skills, Anthropic Engineering, 2025-10-16 — <https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills>
- [R5] Create custom subagents, Claude-Code-Doku — „Choose between subagents and the main conversation" (Haupt-Konversation für schnelle, gezielte Änderungen / wenn Latenz zählt; Subagent für ausführliche Ausgabe, Tool-Einschränkung, eigenständige Arbeit) — <https://code.claude.com/docs/en/sub-agents>
- [R6] Subagents im Claude Agent SDK (vier Vorteile — Kontext-Isolation, Parallelisierung, spezialisierte Instruktionen, Tool-Einschränkungen — mit Parallelisierung und Kontext-Management als den zwei primären Treibern) — <https://code.claude.com/docs/en/agent-sdk/subagents>

## Offene Fragen

_Alle zuvor zurückgestellten offenen Fragen wurden am 2026-06-06 entschieden: jeder vorläufige Default ist nun die geltende Regel. Siehe `.audits/decisions/2026-06-06-settle-open-questions.md` für die Einzelentscheidungen und Begründungen._
