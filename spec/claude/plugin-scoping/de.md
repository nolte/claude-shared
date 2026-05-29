# Claude-Plugin-Schnittführung

Status: draft

## Kontext
Claude Code bündelt wiederverwendbare Capabilities — Skills, Agents, Slash-Commands, Hooks, MCP-/LSP-Server — als **Plugins**. Dieses Repository liefert genau ein solches Plugin aus, `nolte-shared`, das heute 40+ Skills und 25+ Agents über alle Phasen des Delivery-Lebenszyklus hinweg bündelt. Drei bestehende Specs beantworten je eine andere Scoping-Frage: `skill-vs-agent` entscheidet den Artefakt-**Typ** (Skill oder Agent), `skill-management` und `agent-management` entscheiden die On-Disk-**Form** jedes Artefakts, und `skill-agent-catalog` entscheidet die **Discovery**-Oberfläche. Keine davon beantwortet die Frage, die über allen dreien steht: **was begrenzt ein Plugin selbst?** Wann gehört ein Satz von Capabilities in *ein* Plugin und wann auf *mehrere* aufgeteilt, und wie bleibt ein einzelnes Plugin überschaubar („übersichtlich") und zielgerecht, während es wächst?

Ohne eine Regel driften Autoren in einen von zwei Fehlermodi: ein „Kitchen-Sink"-Plugin, durch das niemand navigieren kann, oder eine verfrühte Fragmentierung, die einen einzigen Nutzer-Workflow über viele Installationen verstreut. Eine Recherche gegen die autoritativen Anthropic-Quellen ([R1](#referenzen)–[R4](#referenzen)) ergab, dass Anthropic Plugin-Grenzen **rein nach Distribution und Wiederverwendung** entscheidet, **keine** Obergrenze für Capabilities pro Plugin dokumentiert und **keine** thematische Kohäsions-Regel dafür gibt, was in ein Plugin gegenüber mehreren gehört. Die verbreitete Intuition, Anthropics eigene First-Party-Plugins seien jeweils auf einen einzigen Workflow oder eine Domäne zugeschnitten, wurde geprüft und **nicht bestätigt**. Diese Spezifikation kodifiziert daher die distributions-basierte Regel als autoritativen Kern und markiert jede darüber hinausgehende Breiten- oder Aufteilungs-Regel ausdrücklich als lokale `nolte-shared`-Konvention statt als Anthropic-Vorgabe.

Lesende: Plugin-Autoren, die entscheiden, wo eine neue Capability lebt; Reviewer, die prüfen, ob eine vorgeschlagene Plugin-Aufteilung gerechtfertigt ist; und Portfolio-Pflegende, die abwägen, ob `nolte-shared` jemals mehr als ein Plugin werden sollte.

## Ziele
- Eine deterministische Regel für die **Plugin-Zugehörigkeit**: welche Capabilities in ein Plugin gegenüber einem separaten ausgeliefert werden
- Eine klare Trennung zwischen dem, was Anthropic tatsächlich dokumentiert (die distributions-basierte Grenze), und dem, was eine lokale `nolte-shared`-Konvention ist (alles zu Breite, Aufteilungen und Übersichtlichkeit)
- Ein bewusst breites Plugin überschaubar und zielgerecht halten — durch *Intra*-Plugin-Organisation, nicht durch Aufteilung um der Breite willen
- Die echten Anti-Patterns benennen: Capability-Überlappung, die das Routing verschlechtert, und themengetriebene Fragmentierung, die einen Workflow über mehrere Plugins zersplittert
- Reviewern eine prüfbare Grundlage geben, ein vorgeschlagenes zweites Plugin im Portfolio anzunehmen oder abzulehnen

## Nicht-Ziele
- Die Artefakt-Typ-Wahl zwischen Skill und Agent (gehört zu `skill-vs-agent`)
- Die On-Disk-Form, das Frontmatter und die Benennung einzelner Skills oder Agents (gehört zu `skill-management` und `agent-management`)
- Der MkDocs-Katalog, die Phasen-Klassifikation und das Tag-Vokabular, die ein Plugin durchsuchbar machen (gehört zu `skill-agent-catalog`)
- Marketplace-Mechanik und der Plugin-Versions-Bump (gehört zu `release-automation` und den Manifest-Specs)
- Laufzeit-Laden, Namespace-Auflösung und Routing-Verhalten von Claude Code selbst
- Ob eine gegebene Capability überhaupt ein Plugin-Artefakt sein sollte gegenüber einem projektlokalen `.claude/`-Artefakt (eine Distributions-Entscheidung, die zu `skill-management` / `agent-management` gehört)

## Anforderungen

### Die Plugin-Grenze ist die Distributions-Einheit, nicht das Thema
- **MUSS [MUST]** die Plugin-Zugehörigkeit nach dem **Distributions-Vertrag** entscheiden, nicht nach Thema oder Anzahl: eine Capability gehört in ein Plugin, wenn sie dessen Release-Kadenz, Marketplace-Eintrag, Versionslinie und die einzelne Installations-Entscheidung des Konsumenten teilt. Das ist das einzige Plugin-Grenz-Kriterium, das Anthropic dokumentiert — die Leitlinie „When to use plugins vs standalone configuration" stützt sich vollständig auf das Teilen mit einem Team, die Wiederverwendung über Projekte hinweg, versionierte Updates und Marketplace-Distribution ([R1](#referenzen))
- **DARF NICHT [MUST NOT]** thematische Breite oder Capability-Anzahl als Grund behandeln, ein Plugin aufzuteilen: Anthropic dokumentiert keine Obergrenze für Capabilities pro Plugin und keine thematische Kohäsions-Regel dafür, was in ein Plugin gegenüber mehreren gehört ([R1](#referenzen)). Ein breites, mehrthematisches Plugin wie `nolte-shared` ist **konstruktionsbedingt** konform, solange seine Mitglieder einen Distributions-Vertrag teilen
- **DARF NICHT [MUST NOT]** „Anthropic schneidet seine Plugins nach Thema/Domäne/Workflow" als Rechtfertigung für irgendeine Regel in diesem Portfolio anführen — die Behauptung, Anthropics First-Party-Plugins seien jeweils auf einen einzigen Workflow zugeschnitten, wurde gegen die Quelle geprüft und nicht bestätigt, ist also keine Grundlage für lokale Regeln
- Ein Plugin **KANN [MAY]** heterogene Komponenten-Typen (Skills, Agents, Commands, Hooks, MCP-/LSP-Server, Settings) unter einer `.claude-plugin/plugin.json` bündeln; das Manifest, nicht ein einzelner Komponenten-Typ, ist die Scoping-Grenze ([R1](#referenzen))

### Wann in ein separates Plugin aufgeteilt wird
Dieser Abschnitt ist eine **lokale `nolte-shared`-Konvention**, abgeleitet aus der distributions-basierten Regel oben; Anthropic gibt kein First-Party-Aufteilungs-Kriterium.

- **MUSS [MUST]** einen Teilsatz von Capabilities nur dann in ein eigenes Plugin aufteilen, wenn dieser Teilsatz einen wirklich anderen **Distributions-Vertrag** hat, zum Beispiel:
  - eine andere Konsumenten-Zielgruppe (manche Konsumenten wollen Teilsatz A, aber nie B)
  - eine andere Release-Kadenz oder Stabilitäts-Garantie (experimentelle Capabilities gegenüber der stabilen Oberfläche)
  - eine andere Laufzeit- oder Abhängigkeits-Anforderung, die nicht alle Konsumenten erfüllen können
  - eine andere Eigentums-, Lizenz- oder Zugriffs-Grenze
- **DARF NICHT [MUST NOT]** ein Plugin nur deshalb aufteilen, weil seine Mitglieder verschiedene Themen oder Lebenszyklus-Phasen adressieren; eine reine Themen-Aufteilung fragmentiert einen einzigen durchgängigen Nutzer-Workflow über mehrere Installationen und zwingt einen Konsumenten, N Plugins zu entdecken, zu installieren und versionsmäßig zu verfolgen, um einen kohärenten Fluss zu erhalten
- **MUSS [MUST]** den konkreten Distributions-Vertrags-Unterschied in der Beschreibung des Aufteilungs-PRs benennen; eine Aufteilung, deren Begründung sich auf „das sind verschiedene Themen" oder „das Plugin wird groß" reduziert, erfüllt diese Spezifikation nicht
- **SOLLTE [SHOULD]** ein Plugin pro Distributions-Vertrag bevorzugen, selbst wenn dieses Plugin viele Lebenszyklus-Phasen umspannt; die `phase`-Klassifikation des Katalogs ([R5](#referenzen)), nicht die Plugin-Grenze, ist die Achse, die ein Plugin nach Lebenszyklus organisiert
- **SOLLTE [SHOULD]** den einzelnen Distributions-Vertrag jedes Plugins in dessen `project/portfolio.yml`-Capability-Begründung festhalten (gemäß `portfolio-management`), sodass die gerenderte Portfolio-Inventur den Distributions-Vertrag jedes Plugins sichtbar macht und Aufteilungs-Entscheidungen über das gesamte Portfolio hinweg auditierbar werden statt nur pro PR; der Consumer-Mode von `skill-agent-catalog` katalogisiert Artefakte für die Discovery und ist **nicht** der Ort, an dem Distributions-Verträge festgehalten werden

### Übersichtlichkeit ist eine Intra-Plugin-Angelegenheit
Dieser Abschnitt ist eine **lokale `nolte-shared`-Konvention**.

- **MUSS [MUST]** ein wachsendes Plugin durch die *Intra*-Plugin-Organisationsschichten überschaubar halten statt durch Aufteilung: `phase`-Klassifikation, `tags`, Index-Seiten pro Abschnitt und aufgabenorientierte Landing-Pages (alle gehören zu `skill-agent-catalog` [R5](#referenzen)), plus die Benennungs-Disziplin, die zu `skill-management` und `agent-management` gehört
- **MUSS [MUST]** das Duplikat-Präventions-Invariant (eine Capability pro Artefakt, gemäß `skill-vs-agent` §Duplikat-Prävention) als primäre Verteidigung der Klarheit eines Plugins behandeln: Capability-**Überlappung**, nicht Capability-**Anzahl**, ist das, was die Navigierbarkeit erodiert
- **SOLLTE [SHOULD]** die aufgabenorientierten Landing-Pages des Katalogs als menschlichen Einstiegspunkt behandeln, der ein breites Plugin nach Nutzer-Absicht navigierbar hält („Ich möchte ein Release veröffentlichen") statt durch das Durchblättern Dutzender Artefakte
- **SOLLTE [SHOULD]**, wenn ein Reviewer das Plugin als schwer navigierbar empfindet, zuerst nach fehlender oder schwacher `phase`-/`tags`-/Landing-Page-Abdeckung und nach Duplikat-Capability-Drift suchen, bevor eine Plugin-Aufteilung erwogen wird

### Auffindbarkeit ist der eigentliche Skalierungsdruck
- **MUSS [MUST]** anerkennen, dass die bindende Skalierungsgrenze eines wachsenden Plugins **Routing und Discovery** ist, nicht das Plugin-Manifest: beim Start lädt Claude nur die `name`- plus `description`-Metadaten jedes Artefakts vor, um über potenziell 100+ Skills zu routen, sodass ein Überangebot an überlappenden oder vage beschriebenen Artefakten die automatische Auswahl und Delegation verschlechtert ([R2](#referenzen), [R3](#referenzen))
- **MUSS [MUST]** „Scoping-Disziplin" daher als **Beschreibungs-Qualitäts- und Überlappungs-Eliminierungs-Disziplin** operationalisieren (geregelt durch `skill-management`, `agent-management` und `skill-vs-agent`), niemals als Zielzahl von Plugins oder Artefakten
- **SOLLTE [SHOULD]**, wenn die Routing-Zuverlässigkeit beim Wachstum des Plugins sichtbar nachlässt, zuerst die `description`-Felder schärfen (dritte Person, Was + Wann) und Capability-Überlappung entfernen; eine Distributions-Vertrags-Aufteilung nur erwägen, wenn eine wirklich existiert
- **SOLLTE [SHOULD]** explizite Aufrufe gegenüber dem Verlass auf automatische Delegation für Agents bevorzugen, deren Routing mehrdeutig ist, weil automatische Delegation nachlässt, je größer die Zahl ähnlicher Agents wird ([R3](#referenzen))
- **SOLLTE NICHT [SHOULD NOT]** eine weiche, selbst auferlegte Artefakt-Obergrenze als Review-Trigger einführen; `nolte-shared` hängt seiner Scoping-Disziplin keine Zahl an und verlässt sich rein auf beobachtete Routing-Qualitäts- und Überlappungs-Signale. Der periodische `skills-agents-sweep` ([R5](#referenzen)) ist der Review-Trigger, getrieben von Routing-Qualitäts- und Überlappungs-Signalen statt von einer Anzahl, und niemals als Aufteilungs-Kriterium gelesen

### Namespace- und Benennungs-Kohärenz
- **MUSS [MUST]** einen Plugin-`name` wählen, der ein stabiler, kollisionsresistenter **Namespace** ist: Plugin-Skills sind immer als `/<plugin-name>:<skill-name>` namensraum-präfigiert, und das `name`-Feld der `plugin.json` *ist* der Skill-Namespace ([R1](#referenzen))
- **MUSS [MUST]** die Artefakt-Benennung über das **gesamte** Plugin hinweg konsistent halten — eine Benennungs-Konvention für jeden Skill und Agent, den es ausliefert (gemäß `skill-management` §Frontmatter-Validierung, die Verb-Nomen-Konvention dieses Plugins); inkonsistente Benennungs-Muster innerhalb einer einzelnen Sammlung sind ein dokumentiertes Discovery-Anti-Pattern ([R2](#referenzen))
- **DARF NICHT [MUST NOT]** den Plugin-Namespace leichtfertig umbenennen: der Namespace-Präfix ist Teil jedes `subagent_type:`- und `/<plugin>:<skill>`-Aufrufs eines Konsumenten, sodass eine Namespace-Änderung ein Breaking Change ist, der derselben Deprecation-Disziplin unterliegt, die `skill-vs-agent` §Portfolio-weite Konsistenz auf die Artefakt-Reklassifikation anwendet

## Akzeptanzkriterien
- [ ] Jedes Plugin im Portfolio ist durch einen einzigen Distributions-Vertrag gerechtfertigt (geteilte Release-Kadenz + Marketplace-Eintrag + Installations-Entscheidung des Konsumenten), festgehalten in seiner README oder Top-Level-Orientierungsdatei
- [ ] Keine Plugin-Aufteilung im Portfolio ist allein durch Thema, Lebenszyklus-Phase oder Artefakt-Anzahl gerechtfertigt; die PR-Beschreibung jeder Aufteilung benennt einen konkreten Distributions-Vertrags-Unterschied aus den vier aufgezählten Gründen (oder ein dokumentiertes Äquivalent)
- [ ] `nolte-shared` bleibt ein einzelnes Plugin, das mehrere Lebenszyklus-Phasen umspannt; seine Überschaubarkeit beruht auf der `phase`-/`tags`-/Katalog-/Landing-Page-Abdeckung, prüfbar in der gebauten Doku-Site, nicht auf einer reduzierten Artefakt-Anzahl
- [ ] Das Duplikat-Präventions-Invariant hält: keine zwei Artefakte in einem Plugin teilen eine gleichwertige Capability-Aussage (gegengeprüft gemäß `skill-vs-agent`)
- [ ] Der Plugin-`name` in `.claude-plugin/plugin.json` ist ein eindeutiger, gültiger Skill-Namespace, und jeder Plugin-Skill routet als `/<plugin-name>:<name>`
- [ ] Die Artefakt-Benennung ist über das gesamte Plugin hinweg konsistent — kein Gemisch aus Verb-Nomen- und Gerund- (oder anderen) Konventionen in einem Plugin
- [ ] Keine Anforderung in dieser Spezifikation oder in irgendeiner sie zitierenden Regel behauptet „Anthropic schneidet Plugins nach Thema"; jede Breiten-/Aufteilungs-Regel über die Distributions-Vertrags-Regel hinaus ist als lokale Konvention markiert
- [ ] Ein Reviewer kann ein vorgeschlagenes zweites Plugin allein durch das Lesen dieser Spezifikation entscheiden: annehmen, wenn ein Distributions-Vertrags-Unterschied benannt ist, ablehnen, wenn nur Thema/Breite angeführt wird

## Referenzen

- [R1] Plugins, Claude-Code-Doku (Plugin-vs-Standalone-Entscheidung stützt sich auf Teilen/Wiederverwendung/Versionierung/Marketplace; `plugin.json` `name` ist der Skill-Namespace; Skills immer als `/<plugin>:<skill>` namensraum-präfigiert): <https://code.claude.com/docs/en/plugins>
- [R2] Skill-Authoring-Best-Practices, Anthropic-Platform-Doku (`description` treibt die Auswahl über 100+ Skills; vage/generische Namen und inkonsistente Benennung innerhalb einer Sammlung sind Anti-Patterns): <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices>
- [R3] Create custom subagents, Claude-Code-Doku (automatische Delegation stützt sich auf die `description`; fokussierte Single-Responsibility-Subagents): <https://code.claude.com/docs/en/sub-agents>
- [R4] Equipping agents for the real world with Agent Skills, Anthropic Engineering, 2025-10-16 (Progressive Disclosure; viele Skills ohne Kontext-Strafe installieren): <https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills>
- [R5] `skill-vs-agent`, `skill-management`, `agent-management`, `skill-agent-catalog` (dieses Plugin): die Artefakt-Typ-, On-Disk-Form- und Katalog-Specs, über denen diese Spezifikation steht

## Offene Fragen
- Skill-Anzahl-Disziplin (Vorladen vollständiger `SKILL.md`-Bodies). Keine Spec-Änderung, bis `anthropics/claude-code#14882` (derzeit OPEN, seit 2026-05-16 mit „has repro" gelabelt, also bestätigt-reproduziert, aber unbehoben) einen der folgenden Zustände erreicht: (a) CLOSED als „working as intended" / „wontfix" — das bedeutet, das Vorladen vollständiger Bodies ist das tatsächliche Design, woraufhin die Kontext-Budget-Kosten zu einer gemessenen Anzahl-Strafe werden und eine defensive Disziplin evidenzbasiert wird; oder (b) CLOSED als behoben in einer veröffentlichten Claude-Code-Version — woraufhin diese offene Frage gegenstandslos ist und entfernt werden sollte. Upstream: <https://github.com/anthropics/claude-code/issues/14882>
- Ein zweites Plugin für eine Stabilitäts-Aufteilung. Erneut zu prüfen, wenn ein konkreter Konsument (oder die Portfolio-Pflege) die stabile Oberfläche braucht, aber nicht die experimentelle — das heißt, ein Artefakt-Satz erlangt einen wirklich abweichenden Distributions-Vertrag: eine separate Release-Kadenz oder Versionslinie, einen separaten Marketplace-Eintrag oder eine Installations-Entscheidung des Konsumenten, die sich von der einzelnen von `nolte-shared` unterscheidet. Operativ: wenn irgendeine Capability, die derzeit in `project/portfolio.yml` mit `status: experimental` markiert ist, auf einer eigenen Versionslinie oder einem eigenen Marketplace-Eintrag statt auf der einzelnen 0.1.x-Linie von `nolte-shared` ausgeliefert würde. In diesem Moment greift §Wann in ein separates Plugin aufgeteilt wird mechanisch, und der Aufteilungs-PR muss den Vertrags-Unterschied benennen.
