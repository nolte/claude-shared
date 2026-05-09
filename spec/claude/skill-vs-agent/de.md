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
- **KANN [MAY]** ein konkretes Schwester-Artefakt als Präzedenz referenzieren (zum Beispiel: „folgt demselben Orchestrator-Muster wie `pull-request-create`")
- Die Platzierung im Body liegt im Ermessen der Autorin / des Autors; sinnvolle Orte sind direkt unter der obersten Überschrift oder als kurzer Fuß unmittelbar vor den Hard Rules

### Portfolio-weite Konsistenz
- **MUSS [MUST]** eine Capability-Klasse, die in drei oder mehr Consumer-Repositories wiederkehrt, als Plugin-Level-Artefakt ausliefern statt als projekt-lokale Kopien; dieser Schwellwert ist mit dem Drei-Wiederholungs-Trigger der `workflow-health`-Spezifikation für Specialized-Agent-Autoring abgestimmt, und die obige Entscheidungsregel bestimmt weiterhin, ob das Plugin-Level-Artefakt ein Skill oder ein Agent ist
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
- [ ] Die Tabelle der Entscheidungsdimensionen ist konsistent mit der offiziellen Anthropic-Anleitung dazu, wann die Haupt-Konversation gegenüber einem Subagent zu wählen ist ([R3](#referenzen)); Divergenzen werden zugunsten dieser Spezifikation aufgelöst, aber in `## Offene Fragen` erläutert

## Referenzen

- [R1] Create custom subagents, Claude-Code-Doku (Subagents können keine Subagents spawnen) — <https://code.claude.com/docs/en/sub-agents>
- [R2] Extend Claude with skills, Claude-Code-Doku (`context: fork`) — <https://code.claude.com/docs/en/skills>
- [R3] Building Effective AI Agents, Anthropic Engineering — <https://www.anthropic.com/research/building-effective-agents>
- [R4] Equipping agents for the real world with Agent Skills, Anthropic Engineering, 2025-10-16 — <https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills>

## Offene Fragen
- Soll diese Spezifikation eine Mindeststruktur für den „Rationalen-Abschnitt" festlegen (mindestens zwei benannte Dimensionen, mindestens eine Gegendimension), um Audits mechanisch durchführbar zu machen, oder reicht die aktuelle Messlatte „mindestens eine entscheidende Dimension" aus?
- Wenn eine Capability gleichzeitig von Tool-Einschränkung **und** Mitten-im-Fluss-Interaktivität profitieren würde (direkter Widerspruch zwischen Agent- und Skill-seitigen Dimensionen), gibt es einen bevorzugten Ausweg — ein Skill mit freiwilliger Tool-Disziplin oder ein Agent mit vordeklariertem Pause-/Resume-Protokoll?
- Sollen Slash-Commands / CLI-Einstiegspunkte in einer späteren Iteration als dritte Artefakt-Klasse eingeführt werden, und wie würde sich diese Entscheidungsregel auf sie ausdehnen?
- Wie wird die „Capability-Äquivalenz"-Prüfung in der Duplikat-Vermeidungsregel praktisch operationalisiert — als semantisches Lesen jeder `description` zum Audit-Zeitpunkt, als leichtgewichtiger Keyword-Schnitt oder als Generator, der Embeddings vergleicht?
- Soll der Drei-Wiederholungs-Schwellwert für die Plugin-Level-Promotion mit der `workflow-health`-Spezifikation im Gleichschritt gehalten werden (Änderungen gemeinsam getrackt) oder abweichen, wenn der breitere Scope dieser Spezifikation eine andere Zahl rechtfertigt?
