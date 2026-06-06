# Wiederaufnehmbare Skill- und Agent-Arbeit

Status: draft

## Context
Lang laufende, mehrschrittige Claude-Code-Skills und -Agents — zum Beispiel `portfolio-audit`, `spec-drift-audit`, `skills-agents-sweep`, `feature-decompose`, `sprint-plan`, `release-notes-curate` — verschränken automatisierte Arbeit mit Genehmigungsgates der Nutzerin oder des Nutzers und produzieren unterwegs Zwischenartefakte (Scan-Ergebnisse, Drafts, Teilbefunde). Stürzt der Host-Rechner ab, schließt sich das Terminalfenster, läuft die Claude-Code-Session ab oder läuft die Person einfach weg, verdampft jedes Byte dieses laufenden Zustands. Bei der nächsten Invocation müssen Operator:innen bei Null beginnen und jedes Genehmigungsprompt erneut beantworten — das ist ärgerlich und eine stille Quelle von Inkonsistenz: niemand tippt dieselben Entscheidungen zweimal hintereinander identisch.

Diese Spec definiert eine **Resume-Working-Copy**-Konvention: eine kleine, gitignorierte, menschenlesbare On-Disk-Persistenzschicht, in die lang laufende Skills und Agents während ihres Fortschritts schreiben und die sie bei einer erneuten Invocation konsultieren. Die Konvention fixiert nur den Envelope (Ort, Identität, Pflichtfelder, Lebenszyklus); jeder Skill bzw. Agent bleibt frei, sein eigenes Checkpoint-Payload innerhalb des Envelopes zu modellieren.

Die Konvention ist bewusst lokal-first: der Zustand liegt neben der Working Copy, gitignoriert, und verlässt die Maschine nie. Sie ist kein verteilter State-Store, kein CI-Feature und kein Ersatz für das Committen fertiger Arbeit.

Leserschaft: Skill- und Agent-Autor:innen in `claude-shared` sowie Operator:innen, die lange Workflows ausführen und nach Unterbrechungen wieder einsteigen müssen.

## Goals
- Jeder in-scope Skill bzw. Agent kann nach Crash, Terminal-Schließen oder Session-Ablauf wiederaufgenommen werden, ohne Genehmigungsgates, die bereits eine Entscheidung erzeugt haben, erneut zu durchlaufen
- Ein Run ist auf derselben Maschine sitzungsübergreifend eindeutig und stabil identifizierbar, sodass die Auto-Detektion bei Re-Invocation deterministisch ist
- Das State-Dateiformat ist menschenlesbar (YAML), vorwärtskompatibel (trägt eine `schema_version`) und mit `cat` / `ls` ohne Spezialtools inspizierbar
- Skills und Agents fail closed: eine korrupte, nicht parsbare oder schema-inkompatible State-Datei führt zu einem Operator-Prompt, nicht zum stillen Verwerfen oder stillen Anwenden
- Operator:innen erkennen auf Katalog-Ebene, welche Skills und Agents Resume unterstützen, damit sie wissen, wann sie ein Resume-Prompt erwarten dürfen und welche Workflows sich gefahrlos unterbrechen lassen
- Die Konvention koexistiert sauber mit `spec/project/parallel-working-copies/`: Resume-State ist pro Worktree, nie über Symlink zwischen Worktrees geteilt

## Non-Goals
- Maschinenübergreifende oder Remote-State-Synchronisation (Dropbox, S3, git, Cloud-Sync) — der State ist strikt lokal zur Working Copy auf dieser Maschine
- Recovery von harness-getrackten Background-Jobs, MCP-Server-Prozessen, lang laufenden Shell-Sessions oder externen CI-Runs — diese haben eigene Lebenszyklen und werden hier nicht modelliert
- Triviale Einmal-Skills und -Agents, deren komplette Ausführung billig von vorne wiederholbar ist (etwa `quality-gate`s Lint/Test-Aufruf, der Scan-Schritt des `dependency-audit-scanner`-Agents) — Resume-Support wäre für sie unnötiger Overhead
- Das interne Content-Schema des Checkpoint-Payloads jedes Skills — jeder Skill bzw. Agent besitzt die Form seines eigenen `state:`-Abschnitts; diese Spec fixiert nur den Envelope darum
- Das Committen oder Versionieren des Resume-Verzeichnisses im Sourcecontrol — es ist standardmäßig `.gitignore`d und nur für die lokale Working Copy relevant
- Das Ersetzen des bestehenden `.audits/`-Output-Mechanismus — fertige Audit-Artefakte leben weiterhin unter `.audits/`; das Resume-Verzeichnis hält ausschließlich In-Flight-Scratch-State

## Requirements

### Geltungsbereich
- **MUSS [MUST]** für jeden Skill gelten, dessen normaler Kontrollfluss mehr als ein Genehmigungsgate oder mehr als eine interne Phase mit einem Zwischenartefakt umfasst, das die Person bei Unterbrechung sonst verlieren würde; Agents fallen unter die Ermessensklausel weiter unten statt unter dieses MUSS, weil ein Agent headless läuft und kein Genehmigungsgate zu bewahren hat
- **MUSS [MUST]** im `SKILL.md`-Frontmatter des Skills (bzw. im Agent-Frontmatter) per `resumable: true`-Feld deklariert werden, damit der Katalog-Generator und die Peer-Lookups aus `skill-vs-agent` Resume-Support sichtbar machen können
- **MUSS [MUST]** aus dem `description`-Text des Skills bzw. Agents heraus referenziert werden (eine kurze Klausel: „supports resume on re-invocation"), wann immer `resumable: true` gesetzt ist, damit Operator:innen, die den Katalog lesen ohne ins Frontmatter zu schauen, dies dennoch erkennen
- **SOLLTE NICHT [SHOULD NOT]** für Einmal-Skills gelten, deren komplette Ausführung ein einzelner Bash-Aufruf oder ein einzelner Tool-Call ist, der selbst billig neu startbar ist; `resumable: false` (oder das Feld auslassen) ist für diese die richtige Wahl
- **KANN [MAY]** für Agents gelten, deren Vertrag ansonsten fire-and-forget ist, wenn sie intern mehrere Phasen umspannen, die vom Checkpointing profitieren; das ist eine bewusste Ausnahme zur üblichen Skills-sind-mehrturnig-/-Agents-sind-einturnig-Trennung aus `spec/claude/skill-vs-agent/`

### Persistenz-Ort
- **MUSS [MUST]** Resume-State unter `.resume/<skill-or-agent-name>/<run-id>.yml` an der Repository-Wurzel der Working Copy schreiben
- **MUSS [MUST]** den kebab-case-`name` aus dem Frontmatter des Skills bzw. Agents als `<skill-or-agent-name>` verwenden, damit das Verzeichnis aus dem Artefakt-Bezeichner vorhersehbar ist
- **MUSS [MUST]** sicherstellen, dass die `.gitignore` des Repositories `/.resume/` enthält (an der Repo-Wurzel verankert); wenn ein nachgelagertes Projekt diese Spec konsumiert, ist der `project-structure`-Scaffolder der richtige Ort, den Eintrag hinzuzufügen
- **MUSS [MUST]** das Verzeichnis `.resume/<skill-or-agent-name>/` beim ersten Checkpoint-Schreiben erzeugen, falls nicht vorhanden, und **DARF NICHT [MUST NOT]** fehlschlagen, wenn das Verzeichnis bereits aus einem früheren Run existiert
- **DARF NICHT [MUST NOT]** Resume-State außerhalb von `.resume/` für diesen Zweck schreiben — kein `/tmp/...`, kein `~/.claude/...`, kein `.audits/...`, kein committeter Ort innerhalb des Repositories
- **DARF NICHT [MUST NOT]** `.resume/` per Symlink von einem Worktree zu einem anderen verlinken; gemäß `spec/project/parallel-working-copies/` hält jeder Worktree sein eigenes unabhängiges `.resume/`
- **MUSS [MUST]** `.resume/` als einzige, an der Repo-Wurzel verankerte Konvention behandeln, unabhängig davon, wie viele Sprach-Ökosysteme das Repository beherbergt; das Verzeichnis ist nach dem Claude-Code-Artefakt-Namen verschlüsselt, nicht nach Toolchain, und wird daher nie pro Sprach-Ökosystem aufgeteilt (die Lockfile-Analogie überträgt sich nicht), womit Auto-Detektion und der einzelne `/.resume/`-gitignore-Eintrag über Einzweck-Repositories und polyglotte Monorepos hinweg einheitlich bleiben

### Run-Identität
- **MUSS [MUST]** jedem neuen Run eine eindeutige `run_id` zuweisen, deren empfohlene Form ein ISO-8601-UTC-Zeitstempel gefolgt von einem kurzen Zufallssuffix ist, mit Bindestrich verbunden — zum Beispiel `20260522T143012Z-a3f9`; das Zeitstempel-Präfix sortiert Runs chronologisch in einer Verzeichnisliste, das Suffix verhindert Kollisionen, wenn zwei Runs in derselben Sekunde starten
- **MUSS [MUST]** die `run_id` wortwörtlich in das `run_id:`-Feld der State-Datei einbetten, übereinstimmend mit dem Dateistamm (ohne die Endung `.yml`)
- **MUSS [MUST]** einen deterministischen `inputs:`-Snapshot erfassen — die initialen Invocation-Argumente sowie Ziel-Identifier (etwa Ziel-Spec-Topic, Ziel-Sprint-Nummer, Ziel-Audit-Bundle) — damit die Auto-Detektion eine Re-Invocation per Vergleich der Inputs dem richtigen in-progress Run zuordnen kann
- **KANN [MAY]** beim Vergleich von `inputs:` für von Menschen getippte Identifier eine deterministische Normalisierung anwenden (Case-Folding, Trimmen/Zusammenfassen von Whitespace), sodass zwei Schreibweisen desselben Ziels zu einem in-progress Run aufgelöst werden, statt beantwortete Gates fälschlich erneut zu stellen; die Normalisierung **MUSS [MUST]** selbst dokumentiert und deterministisch sein, im Einklang mit der Determinismus-Anforderung aus §Resume-Detektion
- **KANN [MAY]** zusätzlich ein kurzes menschenlesbares `label:` einbetten (freier Text, ≤80 Zeichen), sodass das Resume-Prompt „spec-drift-audit · bundle-7 (4 specs)" statt nur einer Run-ID anzeigen kann

### State-Datei-Envelope
Die folgenden Schlüssel bilden den Pflicht-Envelope, den jede State-Datei tragen MUSS. Skills und Agents fügen ihre eigenen Schlüssel unter `state:` hinzu.

- **MUSS [MUST]** `schema_version` (Integer, derzeit `1`) als ersten Schlüssel der Datei enthalten
- **MUSS [MUST]** genau eines von `skill:` oder `agent:` enthalten, dessen Wert der kebab-case-`name` übereinstimmend mit dem Artefakt-Frontmatter ist
- **MUSS [MUST]** `run_id` enthalten, übereinstimmend mit dem Dateistamm
- **MUSS [MUST]** `started_at` (ISO 8601 UTC, einmalig bei Run-Erzeugung gesetzt) und `last_checkpoint_at` (ISO 8601 UTC, bei jedem Checkpoint-Schreiben aktualisiert) enthalten
- **MUSS [MUST]** `inputs:` als Mapping oder Liste mit dem Snapshot der initialen Invocation-Argumente enthalten, die für das Auto-Detect-Matching verwendet werden
- **MUSS [MUST]** `phase:` enthalten (kurzer freier Text, der den letzten abgeschlossenen Checkpoint innerhalb des Skills bzw. Agents identifiziert, etwa `scanned`, `findings-drafted`, `awaiting-approval-3`)
- **MUSS [MUST]** `decisions:` als geordnete Liste der bereits eingesammelten Nutzer-Antworten enthalten; jeder Eintrag **MUSS [MUST]** `gate` (Bezeichner des Genehmigungsgates innerhalb des Skills), `question` (der Fragetext, den die Person beantwortet hat), `answer` (der gewählte Wert) und `at` (ISO-8601-UTC-Zeitstempel der Antwort) tragen
- **MUSS [MUST]** `status:` enthalten, dessen Wert genau eines aus `in_progress`, `completed` oder `discarded` ist
- **KANN [MAY]** `label:` enthalten (siehe Run-Identität oben) sowie beliebig viele weitere Schlüssel unter `state:`, modelliert vom besitzenden Skill bzw. Agent
- **DARF NICHT [MUST NOT]** Credentials, rohe API-Keys, OAuth-Tokens oder andere geheime Materialien in der State-Datei speichern; die Datei ist Klartext auf der Platte und damit als Secret-Store ungeeignet

### Checkpoint-Kadenz
- **MUSS [MUST]** unmittelbar nach jedem erfolgreichen Genehmigungsgate einen Checkpoint schreiben, bevor Arbeit ausgeführt wird, die von der neuen Entscheidung abhängt; das ist die tragende Regel — sie ist die gelebte Garantie der Operator:innen, dass keine beantwortete Frage beim Resume zweimal gestellt wird
- **MUSS [MUST]** nach jeder benannten Phasengrenze innerhalb des Skills bzw. Agents einen Checkpoint schreiben (etwa nach Abschluss eines Scans, nach dem Verfassen eines Drafts, nach dem Berechnen eines Diffs), damit lange Compute-Schritte beim Resume nicht wiederholt werden müssen
- **MUSS [MUST]** `last_checkpoint_at` bei jedem Checkpoint-Schreiben auf den aktuellen ISO-8601-UTC-Zeitstempel setzen
- **MUSS [MUST]** nur an `decisions:` anhängen — frühere Einträge weder umschreiben noch umordnen — sodass die Checkpoint-Historie ein strikt wachsendes Log ist
- **SOLLTE NICHT [SHOULD NOT]** Checkpoints innerhalb einer engen inneren Schleife schreiben (Pro-Datei-Iteration, Pro-Record-Scanning); stattdessen an der Schleifengrenze checkpointen, damit die Datei nicht hundertfach pro Sekunde überschrieben wird
- **SOLLTE [SHOULD]** die Datei atomar schreiben (Write-then-Rename), damit ein Crash mitten im Schreibvorgang einen bestehenden Checkpoint nicht korrumpiert

### Resume-Detektion bei Re-Invocation
- **MUSS [MUST]** bei jeder Invocation `.resume/<skill-or-agent-name>/*.yml` scannen, bevor die Person nach Inputs gefragt wird, und Dateien mit `status: in_progress` auswählen
- **MUSS [MUST]** wiederaufnehmbare Kandidaten durch Vergleich des gespeicherten `inputs:`-Snapshots mit den aktuellen Invocation-Inputs matchen; der Matching-Algorithmus ist Sache jedes Skills bzw. Agents, **MUSS [MUST]** aber bei gleichen Inputs deterministisch sein
- **MUSS [MUST]** bei genau einem passenden in-progress Run die Person mit folgendem Prompt fragen: `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)?` und genau drei Wahlmöglichkeiten anbieten: `resume` (State re-hydrieren und fortfahren), `start-new` (frischen Run starten; bestehende Datei bleibt als `in_progress` liegen), `discard` (bestehende Datei löschen, dann frischen Run starten); das Prompt bleibt bei diesen drei Wahlmöglichkeiten ohne „Diff gegen Bestehendes"-Vorschau, weil `start-new` nicht-destruktiv ist (es lässt die bestehende Datei intakt — nur `discard` löscht), sodass es kein Datenverlust-Risiko gibt, das eine Vorschau abmildern müsste
- **MUSS [MUST]** bei mehreren passenden in-progress Runs diese mit `run_id`, `label` (falls vorhanden), `phase` und `last_checkpoint_at` auflisten und fragen, welcher fortgesetzt werden soll — oder ob ein neuer Run gestartet wird
- **MUSS [MUST]** bei keinem passenden in-progress Run einen frischen Run starten und beim ersten Checkpoint eine neue State-Datei schreiben
- **MUSS [MUST]** die Wahl der Person exakt befolgen: `resume` re-hydriert aus der Datei und **DARF NICHT [MUST NOT]** Fragen erneut stellen, deren Antwort bereits in `decisions:` steht; `start-new` schreibt eine frische Datei mit neuer `run_id` und lässt die alte Datei unangetastet; `discard` löscht die alte Datei vor dem Fortfahren
- **DARF NICHT [MUST NOT]** die bloße Existenz der Datei als Resume-Autorisierung werten — die interaktive Bestätigung der Person ist jedes Mal erforderlich, es sei denn die Person übergibt einen expliziten Non-Interactive-Override (siehe §Non-Interactive-Override unten)
- **MUSS [MUST]** bei einem `resumable: true`-Agent (der headless läuft und das interaktive Prompt nicht selbst rendern kann) seine Resume-Wahl aus dem dispatchenden Kontext erhalten: das Parent-Skill löst die Drei-Wege-Wahl mit der Person auf und reicht sie über den §Non-Interactive-Override-Mechanismus nach unten durch, oder der Agent wendet `start-new` als Default an, wenn keine Wahl übergeben wird; ein Agent **DARF NICHT [MUST NOT]** still aus einem Checkpoint wiederaufnehmen, ohne dass eine Wahl explizit übergeben wurde

### Abschluss und Aufräumen
- **MUSS [MUST]** `status:` bei natürlichem Abschluss auf `completed` setzen (der Skill bzw. Agent hat seinen terminalen Schritt erfolgreich erreicht)
- **SOLLTE [SHOULD]** eine `completed`-State-Datei für einen weiteren passenden Invocation-Zyklus als „Recent-Run"-Eintrag behalten, damit die Person nachsehen kann, was im vorherigen Run passiert ist; ein separater Housekeeping-Schritt oder eine Aktion der Person entfernt sie danach
- **MUSS [MUST]** `status:` bei operator-getriebener Abbruchaktion auf `discarded` setzen (oder die Datei direkt löschen); beide Optionen sind zulässig, aber eine partielle in-progress Datei **DARF NICHT [MUST NOT]** still zurückbleiben
- **DARF NICHT [MUST NOT]** veraltete `in_progress`-Dateien älter als 30 Tage behalten, ohne sie bei der nächsten passenden Invocation der Person zu zeigen; das Resume-Prompt **MUSS [MUST]** dann `discard` als klar benannte Option neben `resume` anbieten
- **KANN [MAY]** einen portfolioweiten Housekeeping-Skill (oder ein `task`-Target) bereitstellen, der `completed`- und veraltete `in_progress`-Dateien in Sammelaktion bereinigt — diese Spec schreibt das nicht vor, erlaubt es aber
- Solange beobachtete Anhäufung veralteter Dateien es nicht rechtfertigt (siehe den messbaren Trigger in §Offene Fragen), ist der provisorische Default kein dedizierter Prune-Skill: jedes Artefakt besorgt sein eigenes Aufräumen über die Status-Flips und die 30-Tage-Surfacing-Regel oben
- **MUSS [MUST]** direkten `ls .resume/`- und `cat .resume/<name>/<run-id>.yml`-Zugriff als unterstützte Baseline für Operator:innen behandeln; jeder `task resume:list`-/`task resume:prune`-Helper ist optional und **DARF NICHT [MUST NOT]** vorgeschrieben sein, da das Format bewusst so gestaltet ist, dass es ohne Spezialtools inspizierbar ist (gemäß §Goals)

### Vorwärtskompatibilität
- **MUSS [MUST]** das Wiederaufnehmen einer State-Datei verweigern, deren `schema_version` höher ist als die Version, die der laufende Skill bzw. Agent kennt; die Verweigerung **MUSS [MUST]** eine klare Meldung ausgeben, die beide Versionen benennt, und **MUSS [MUST]** `start-new` oder `discard` als einzig zulässige Folgeaktionen anbieten
- **SOLLTE [SHOULD]** ältere `schema_version`s in-place migrieren, wenn die Migration trivial ist (nur additive Felder, kein Rename), und die aktualisierte Datei vor dem Wiederaufnehmen schreiben
- **MUSS [MUST]** das Wiederaufnehmen mit derselben `start-new`-/`discard`-Fallback-Logik verweigern, wenn eine ältere `schema_version` nicht trivial migrierbar ist
- **MUSS [MUST]** das Wiederaufnehmen verweigern, wenn die Datei nicht parsbar ist (kaputtes YAML, mitten im Schreiben abgeschnitten) und denselben Fallback anbieten; **DARF NICHT [MUST NOT]** still einen frischen Run starten, weil die Person die Datei möglicherweise inspizieren oder reparieren möchte, bevor sie verworfen wird

### Non-Interactive-Override
- **KANN [MAY]** ein Non-Interactive-Override-Flag unterstützen (etwa `--resume <run-id>`, `--new` oder `--discard <run-id>`), damit Automatisierungen oder Batch-Skripte die Resume-Wahl vorauswählen können; wenn der Skill bzw. Agent so ein Flag unterstützt, **MUSS [MUST]** dies in der `description` dokumentiert sein
- **MUSS [MUST]** mangels eines solchen Flags auf das interaktive Prompt aus §Resume-Detektion bei Re-Invocation zurückfallen
- **DARF NICHT [MUST NOT]** still wiederaufnehmen ohne operator-seitige Bestätigung, wenn kein Flag übergeben wurde — die interaktive Bestätigung bleibt die Sicherheitsgrenze

### Zusammenspiel mit weiteren Portfolio-Specs
- **MUSS [MUST]** mit `spec/project/parallel-working-copies/` koexistieren: `.resume/` liegt unabhängig an der Wurzel jedes Worktrees; keine Symlinks, kein geteilter State über Worktrees hinweg
- **MUSS [MUST]** die durch `spec/project/project-structure/` geformte `.gitignore` mit `/.resume/` erweitern statt mit ihr zu kollidieren
- **MUSS [MUST]** aus `spec/claude/skill-management/` und `spec/claude/agent-management/` heraus quer-referenziert werden (nicht dupliziert): diese Specs erhalten eine kurze Regel, dass in-scope Artefakte `resumable: true` deklarieren und dieser Spec folgen; die tragenden Details bleiben hier
- **DARF NICHT [MUST NOT]** `.audits/` (im Besitz von `spec/claude/review-plan/` und skill-spezifischen Audit-Outputs) für In-Flight-Resume-State umzweckentfremden; `.audits/` ist Final-Output-Territorium, `.resume/` ist In-Flight-Scratch
- **MUSS [MUST]** weiterhin jedes fertige Audit, jeden Bericht und jedes Artefakt an den Ort schreiben, den die jeweilige eigene Spec vorgibt; das Wiederaufnehmen eines Runs, der eine `.audits/...`-Datei produziert, bedeutet, dass die Datei geschrieben wird, wenn der Run seinen terminalen Schritt erreicht, nicht als Checkpoint-Nebeneffekt

## Acceptance Criteria
- [ ] Jeder Skill unter `skills/`, dessen normaler Kontrollfluss mehr als ein Genehmigungsgate ODER mehr als eine benannte interne Phase mit einem Zwischenartefakt hat, trägt `resumable: true` im Frontmatter
- [ ] Jeder Agent unter `agents/`, der `resumable: true` trägt, umspannt tatsächlich mehr als eine benannte Phase mit einem Zwischenartefakt (gemäß der Ermessensklausel für Agents in §Geltungsbereich); ein read-only Single-Pass-Agent lässt das Feld korrekt weg, und das Weglassen ist nie selbst ein Befund
- [ ] Jeder Skill und Agent mit `resumable: true` erwähnt Resume-Support im `description:`-Text
- [ ] Kein Skill bzw. Agent mit `resumable: true` schreibt Resume-State außerhalb von `.resume/<skill-or-agent-name>/`
- [ ] Die `.gitignore` des Repositories enthält einen Eintrag, der `/.resume/` ignoriert
- [ ] Keine Datei unter `.resume/<name>/` hat eine `schema_version`, die höher ist als die Version, die der zugehörige Skill bzw. Agent kennt; sofern Mismatches existieren, sind sie von einer operator-seitigen Entscheidung begleitet (gelöschte Datei oder `discarded`-Status)
- [ ] Keine State-Datei unter `.resume/` fehlt einer der Pflicht-Envelope-Schlüssel (`schema_version`, genau eines von `skill`/`agent`, `run_id`, `started_at`, `last_checkpoint_at`, `inputs`, `phase`, `decisions`, `status`)
- [ ] Keine `run_id` einer State-Datei weicht von ihrem Dateistamm ab
- [ ] Keine State-Datei enthält Klartext-Secrets (API-Keys, OAuth-Tokens, Passwörter) unter irgendeinem Schlüssel, einschließlich `state:`
- [ ] Kein `.resume/`-Symlink existiert, der außerhalb des `.resume/`-Verzeichnisses des aktuellen Worktrees zeigt
- [ ] Jede State-Datei mit `status: in_progress`, deren `last_checkpoint_at` älter als 30 Tage ist, ist von Belegen begleitet (Operator-Notiz, Folge-Issue oder `discard`-Entscheidung aus einem späteren Run), die zeigen, dass die Person darauf angesprochen wurde
- [ ] Bei einem absichtlich unterbrochenen Run eines `resumable: true`-Skills zeigt das erneute Invocaten mit denselben Inputs das Resume-Prompt, das die bestehende `run_id`, `phase` und `last_checkpoint_at` benennt
- [ ] Bei einer Resume-Wahl wird keine Frage, deren Antwort bereits in `decisions:` steht, erneut an die Person gestellt
- [ ] Sowohl `spec/claude/skill-management/` als auch `spec/claude/agent-management/` quer-referenzieren diese Spec aus ihren Requirements (keine Duplikation der Envelope- oder Lebenszyklus-Regeln)

Notes on coverage: Die `MUSS`-Regeln in §Checkpoint-Kadenz zu *wann* ein Checkpoint geschrieben wird (nach jedem Gate, nach jeder benannten Phase, atomares Write-then-Rename) sind skill-interne Kontrollfluss-Konventionen ohne stabiles post-hoc beobachtbares Merkmal an der State-Datei selbst; sie werden durch Autorenpraxis und durch Skill-Reviews (`spec/claude/skill-review/`, `spec/claude/agent-review/`) durchgesetzt, nicht durch ein mechanisches AC. Die `MUSS`-Regeln in §Vorwärtskompatibilität zu *was zu tun ist* bei einem `schema_version`-Mismatch oder einer nicht parsbaren Datei sind Laufzeitverhalten, die nur dann zutage treten, wenn ein Mismatch auftritt; ACs decken die post-hoc-Form ab (keine Waisen-Dateien mit hoher Version), nicht aber das Verhalten pro Vorfall. Das `DARF NICHT` gegen das Werten der bloßen Datei-Existenz als Resume-Autorisierung (in §Resume-Detektion bei Re-Invocation) ist ebenfalls eine Laufzeitverhalten-Konvention; sie ist nur durch direktes Operator-Testen des Skills beobachtbar, nicht durch Inspektion des Resume-Verzeichnisses.

## Open Questions

_Alle zuvor zurückgestellten offenen Fragen wurden am 2026-06-06 entschieden: jeder vorläufige Default ist nun die geltende Regel. Siehe `.audits/decisions/2026-06-06-settle-open-questions.md` für die Einzelentscheidungen und Begründungen._
