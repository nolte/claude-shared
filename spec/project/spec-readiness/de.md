# Spec-Reife

Status: draft

## Kontext
Spezifikationen unter `spec/<topic>/<slug>/` sind die Quelle der Wahrheit für nachgelagerte Arbeit im Portfolio — Implementierung, Review-Pläne, Tooling, Dokumentation, Audits. Eine Spec, die in sich widersprüchlich ist, über ihre Leser schweigt oder Lücken hat, zwingt jeden nachgelagerten Schritt zum Raten. Die Kosten kumulieren: Widersprüche tauchen als Bugreports während der Implementierung auf, Audience-Mismatches als „das war nicht für uns geschrieben", Vollständigkeitslücken als Ad-hoc-Entscheidungen, die dann der Spec widersprechen, der sie folgen sollten. Heute hat das Portfolio benachbarte Audits — `spec/project/spec-drift-audit/` gleicht Spec gegen Implementierung ab, der `spec`-Skill dedupliziert über Übersetzungen hinweg, `audience-identify` erstellt Audience-Artefakte für Module, die noch keines haben — aber keines von ihnen prüft, ob eine Spec **für nachgelagerte Nutzung bereit** ist. Diese Spec definiert die Reife-Praxis: was das Audit prüft, wann es läuft, wie Befunde klassifiziert werden und wie eine Spec von Draft zu einer implementierbaren Quelle der Wahrheit aufsteigt.

Leser: Auditoren, die die Readiness-Prüfung durchführen, bevor eine Spec den Draft-Status verlässt, die Autoren des `spec-readiness-reviewer`, die sie operationalisieren, sowie Spec-Autoren, die die von ihr aufgedeckten Widersprüche, Zielgruppen-Lücken und Vollständigkeits-Befunde auflösen.

## Ziele
- Jede Spec im Geltungsbereich wird entlang dreier Dimensionen auditiert — Widersprüche, Audience-Fit, fachliche Vollständigkeit — bevor sie für nachgelagerte Arbeit herangezogen wird
- Befunde werden nach einer geteilten Schweregrad-Skala klassifiziert, sodass dieselbe Art von Problem portfolioweit gleich behandelt wird
- Reife ist eine Vorbedingung dafür, eine Spec aus `Status: draft` in einen stabilen-Vertrags-Zustand zu befördern (den akzeptierten-Äquivalent-Status des Portfolios)
- Das Audit ist read-only und an einen spezialisierten Agent delegiert, damit die Praxis wiederholbar bleibt und frei von Ad-hoc-Prosa-Urteilen
- Das Audit ist klar abgegrenzt vom Dedup-/Drift-/Übersetzungs-Check des `spec`-Skills, von der Spec-vs.-Implementierung-Abgleichung in `spec-drift-audit` und von der modul-seitigen Audience-Erzeugung in `audience-identify`

## Nicht-Ziele
- Specs zu schreiben, zu übersetzen oder umzustrukturieren — das bleibt beim `spec`-Skill
- Implementierung gegen eine Spec zu validieren — das ist `spec/project/spec-drift-audit/`
- Ein frisches Audience-Artefakt für ein Modul zu erzeugen, das keines hat — das ist `audience-identify` + `audience-review`
- Prosa-Korrektheit, Vokabular, Style-Durchsetzung — die gehören zu `spec/project/prose-style/` und `prose-vale-curator`
- Die Deklaration operativer Details des Agents, der das Audit implementiert (`agents/spec-readiness-reviewer.md`) — diese können sich ohne Spec-Änderung entwickeln
- Die Definition eines universellen „Akzeptanz"-Status-Labels jenseits dessen, was diese Spec bereits deklariert; Portfolio-Status-Mechanik lebt im Spec-Artefakt-Format, nicht hier

## Anforderungen

### Geltungsbereich
- **MUSS** auf jede Spec unter `spec/<topic>/<slug>/<canonical_language>.md` angewandt werden, deren `## Requirements`- oder `## Acceptance Criteria`-Sektion nicht leer ist
- **MUSS** Specs mit `Status: draft` einschließen — Drafts sind das primäre Reife-Ziel, nicht eine Ausnahme
- **MUSS** sowohl intra-Spec (innerhalb einer Spec) als auch cross-Spec (zwischen zwei oder mehr Specs) Anliegen abdecken
- **MUSS** die Prüfung der Auflösbarkeit von Querverweisen aus §Dimension 3 — Fachliche Vollständigkeit auf **jede konfigurierte Sprachdatei** einer in-Scope-Spec anwenden, nicht nur auf die kanonische. Die übrigen Dimensionen bleiben kanonisch: Widerspruchserkennung, Zielgruppen-Passung und die Abdeckung von Anforderung zu Akzeptanzkriterium lesen Inhalt, den eine Übersetzung spiegelt statt neu zu formulieren; sie je Sprache zu auditieren würde Arbeit verdoppeln, ohne Neues zu finden. Eine Sektions-Referenz ist von anderer Art, weil sie eine Überschrift benennt und Überschriften übersetzt werden
- **DARF** einen Lauf auf eine einzelne Spec oder ein einzelnes Topic einschränken, wenn der Auslöser selbst eng ist (zum Beispiel ein PR, der eine Spec ändert)

### Dimension 1 — Widerspruchs-Erkennung
- **MUSS** als `Critical` flaggen: ein MUST-/MUST-NOT-Paar innerhalb derselben Spec, das dasselbe Subjekt betrifft, aber entgegengesetzte Anforderungen deklariert
- **MUSS** als `Critical` flaggen: ein MUST in Spec A, das nicht gleichzeitig mit einem MUST in Spec B gelten kann; Paare, die von Scope-Ausschnitten abhängen, werden gelöst, indem der Ausschnitt explizit gemacht wird, nicht indem der Widerspruch ignoriert wird
- **MUSS** als `Warning` flaggen: ein MUST-vs.-SHOULD-Paar innerhalb derselben Spec, das in entgegengesetzte Richtungen zeigt; das MUST gewinnt immer, aber das SHOULD ist für Leser irreführend und ist ein Befund
- **MUSS** als `Warning` flaggen: ein Ziel, das einem Nicht-Ziel derselben Spec direkt widerspricht (zum Beispiel ein Ziel, das Ausgaben impliziert, die die Nicht-Ziele ausdrücklich ausschließen)
- **SOLLTE** als `Info` flaggen: Ketten von Abschwächung (ein MAY, das ein SHOULD effektiv umkehrt, das bereits konditional war), wenn sie das Regel-Set für einen Leser undurchsichtig machen
- **DARF** pro Befund eine Lösungsrichtung vorschlagen — eine Regel verstärken, die andere abschwächen, den Scope aufteilen — ohne die finale Wahl vorzuschreiben
- **MUSS** einen Cross-Spec-Widerspruch symmetrisch berichten (beide Specs benannt, keine bevorzugt); eine bevorzugte Lösungsrichtung ist das beratende DARF oben, niemals ein automatisches Urteil, das einen Sieger nach Spec-Alter, Stabilität oder Topic kürt — die Wahl des Siegers ist die Entscheidung des menschlichen Reviewers (siehe §Abgrenzung)
- **DARF NICHT** einen Widerspruch auf Basis von Prosa allein deklarieren, wenn kein RFC-2119-Verb im Spiel ist; reine Prosa-Inkonsistenzen sind Prosa-Lint-Anliegen, keine Reife-Anliegen
- Cross-Spec-Widerspruchs-Erkennung ist **emergent** aus dem Spec-Bestand im Geltungsbereich; das Audit leitet Kandidaten-Paare dynamisch ab, und ein gepflegtes „Widerspruchs-Korpus" ist ausdrücklich außerhalb des Geltungsbereichs, bis akkumulierte `Recurring`-Befunde belegen, dass der dynamische Check wiederkehrende Spannungspaare verfehlt (Info)

### Dimension 2 — Audience-Fit
- **MUSS** die impliziten Leser jeder Spec aus ihrer Prosa ableiten (typische Sets: Implementor\:innen, Reviewer\:innen, Tooling-Autor\:innen, Release-Manager\:innen, Product-Owner\:innen, Betreiber\:innen); die Ableitung ist Beobachtung, keine Audience-Analyse auf leerem Blatt
- **MUSS** prüfen, dass es für jede abgeleitete Audience Inhalte gibt, auf die sie handeln kann — Anforderungen für Implementor\:innen, Akzeptanzkriterien für Reviewer\:innen, schnittstellen-seitige MUSTs für Tooling-Autor\:innen, sichtbar gemachte Open Questions für Product-Owner\:innen
- **MUSS** als `Warning` flaggen: eine Spec, deren Audience nicht ableitbar ist („für wen ist das geschrieben?") oder deren Anforderungen die Entscheidungen der abgeleiteten Audience nicht adressieren
- **SOLLTE** ein existierendes `audience-identify`-Artefakt querverweisen, wenn das Modul der Spec eines hat; wenn die Spec eine Audience anspricht, die das Artefakt nennt, die Anforderungen der Spec diese aber nicht bedienen, ist der Befund `Warning`, nicht `Critical`. Der Schweregrad entscheidet sich hier an der Substanz, nicht an der bloßen Referenz: eine nicht bediente, artefakt-benannte Audience ist `Warning`, während das bloße Nicht-Zitieren eines Artefakts bei dennoch bedienter abgeleiteter Audience höchstens ein Info-Hinweis ist (siehe die §Dimension 2 Info-Regel unten)
- **SOLLTE** als `Info` flaggen: eine Spec, deren Audience implizit, aber nur mit Aufwand ableitbar ist; die Lösung ist meist ein einzeiliger „Leser:"-Hinweis, kein Umbau
- **DARF** `audience-identify` als Folge-Werkzeug nennen, wenn das Modul der Spec kein Audience-Artefakt hat und das Reife-Audit Audiences nicht zuverlässig ableiten kann
- **DARF NICHT** Audience-Artefakte als Teil dieses Audits erstellen oder schreiben; das ist außerhalb des Geltungsbereichs (siehe §Abgrenzung)

### Dimension 3 — Fachliche Vollständigkeit
- **MUSS** verifizieren, dass jede Anforderung mindestens ein Akzeptanzkriterium hat, das testbar ist (messbares Ergebnis, beobachtbarer Zustand oder durchsetzbares Gate) — eine Anforderung ohne testbares AK ist `Warning`; „mindestens eines pro Anforderung" ist die bewusste Grenze und eine AK-Quote pro MUSS ist außerhalb des Geltungsbereichs, weil feinere Quoten zum Gaming einladen (ein AK in N triviale aufspalten), ohne die echte Abdeckung zu verbessern
- **MUSS** verifizieren, dass jedes Akzeptanzkriterium auf eine Anforderung oder ein Ziel zurückführbar ist — ein verwaistes AK (nicht an eine Anforderung oder ein Ziel bindbar) ist `Warning`
- **MUSS** jede Open Question als entweder **tragend** (Implementierung oder nachgelagerte Arbeit kann nicht verantwortlich ohne Antwort fortfahren) oder **Ablage-Liste** (nice-to-have-Verfeinerung, nachgelagerte Arbeit kann mit einem vernünftigen Default fortfahren) klassifizieren; eine tragende OQ in einer Spec, die zur Beförderung erwogen wird, ist ein `Critical`-Befund
- **MUSS** als `Critical` flaggen: jede Referenz von Spec A auf Spec B, bei der Spec B nicht existiert oder existiert, aber nicht die Sektion enthält, die die Referenz impliziert
- **MUSS** jede Sektions-Referenz **gegen die Sprachdatei auflösen, die sie trägt**: eine in `de.md` geschriebene Referenz löst gegen die Überschriften der `de.md` der Ziel-Spec auf, nicht gegen die kanonischen Überschriften. Eine Referenz, die kanonisch auflöst, aber eine Überschrift benennt, die keine Übersetzung trägt, ist dasselbe `Critical`, denn wer diese Übersetzung liest, erreicht nichts. Deshalb dehnt §Geltungsbereich genau diese eine Prüfung über die Sprachen aus
- **DARF NICHT** eine übersetzte Sektions-Referenz als konform behandeln, weil ihr kanonisches Gegenstück auflöst; es sind zwei getrennte Zeichenketten, die auf getrennte Überschriften-Mengen zeigen, und strukturelle Parität zwischen Übersetzung und Kanonik (im Besitz des `spec`-Skills gemäß §Abgrenzung) belegt nicht, dass eine der beiden auflöst
- **SOLLTE** als `Warning` flaggen: jedes Ziel ohne mindestens eine passende Anforderung — ein Ziel, das die Spec dann nie operationalisiert, ist ein irreführendes Versprechen
- **SOLLTE** als `Info` flaggen: wenn der Scope einer Spec mehrdeutig ist und keine Nicht-Ziele-Sektion ihn einschneidet; die Lösung ist meist, drei bis fünf explizite Nicht-Ziele hinzuzufügen
- **DARF** als `Info` flaggen: Akzeptanzkriterien, die prinzipiell testbar sind, aber Infrastruktur benötigen, die das Portfolio noch nicht hat; das sind keine `Critical`-Klasse, warnen aber Konsument\:innen

### Schweregrad-Skala
- **MUSS** die kanonische Vier-Stufen-Schweregrad-Skala aus `spec/claude/review-plan/<canonical_language>.md` §Severity scale verwenden: `Critical` / `Warning` / `Suggestion` / `Info`, in Title Case
- **MUSS** Reife-Befunde gemäß den in §Dimension 1, 2 und 3 dokumentierten Mustern auf die Skala abbilden:
  - **Critical**: direkter MUST-/MUST-NOT-Widerspruch innerhalb oder zwischen Specs; tragende Open Question in einer zur Beförderung erwogenen Spec; Referenz auf eine nicht existierende Spec-Sektion; Cross-Spec-Widerspruch zwischen zwei akzeptierten Specs
  - **Warning**: MUST-vs.-SHOULD-Widerspruch; nicht identifizierbare Audience; abgeleitete Audience, deren Bedürfnisse nicht adressiert werden; Ziel ohne passende Anforderung; Anforderung ohne testbares Akzeptanzkriterium; verwaistes Akzeptanzkriterium
  - **Info**: Abschwächungsketten-Undurchsichtigkeit; implizite, aber ableitbare Audience; mehrdeutiger Scope ohne Nicht-Ziele; AK, das noch-nicht-portfolio-vorhandene Infrastruktur verlangt
- **DARF** den `Suggestion`-Bucket aus der kanonischen Skala befüllen, wenn ein Befund einen Ein-Zeilen-Fix oder eine stilistische Verbesserung benennt, die nicht zu den drei Reife-Mustern oben passt; Reife-Audits produzieren typischerweise nur `Critical` / `Warning` / `Info`, der Bucket existiert in der kanonischen Skala und bleibt verfügbar
- **DARF NICHT** zusätzliche Schweregrad-Stufen jenseits der kanonischen vier erfinden; Konsistenz über audit-erzeugende Specs hinweg ist der einzige Grund, warum diese Skala in `review-plan` lebt statt pro Spec neu definiert zu werden
- **DARF NICHT** einen Schweregrad allein auf Basis lokaler Einschätzung absenken; Abweichung von der Klassifikation ist eine dokumentierte Waiver-Notiz im Audit-Artefakt, keine stille Re-Klassifikation

### Auslöser
- **MUSS** vor jeder Beförderung einer Spec aus `Status: draft` heraus laufen; eine Spec mit unerledigten `Critical`-Reife-Befunden **DARF NICHT** befördert werden, bis diese Befunde gelöst oder ausdrücklich verzichtet sind. Dieses Beförderungs-Gate wird von der Betreiberin zum Beförderungszeitpunkt durchgesetzt, NICHT von CI; spec-readiness bleibt ein beratendes periodisches Audit (parallel zu `spec/project/spec-drift-audit/` §Abgrenzung, das der periodische Tiefgang ist, während `spec/project/workflow-health/` die kontinuierliche-CI-Spur besitzt). CI-Durchsetzung wird erst dann erneut erwogen, wenn mindestens vier abgeschlossene Quartals-Audits unter `.audits/spec-readiness/` eine gemessene Falsch-Critical-Rate unter 10% zeigen UND ein Einzel-Spec-Beförderungslauf ein stabiles `review-plan`-Format-Artefakt erzeugt hat (AK Zeile 102)
- **MUSS** mindestens einmal pro Kalenderquartal für jede Spec laufen, deren Status noch `draft` ist — Drafts, die ohne Neubewertung altern, driften
- **SOLLTE** als Same-Merge- oder Folge-Teilaudit laufen, wenn ein PR eine Spec ändert (neues MUST, geändertes AK, neuer Scope); der Teilaudit-Scope entspricht den im PR berührten Specs
- **DARF** portfolioweit auf derselben Kadenz wie `spec-drift-audit` laufen — die beiden sind komplementäre Quartals-Durchgänge und können sich das Audit-Ritual teilen, ohne sich den Scope zu teilen

### Read-only-Disziplin
- **MUSS** read-only sein: das Audit berichtet Befunde; Korrekturen (Umformulierung, Verstärkung, fehlende AKs hinzufügen, OQs lösen) sind ein separater, opt-in-Schritt, den die aufrufende Person mit dem `spec`-Skill oder von Hand unternimmt
- **DARF NICHT** während des Audits eine Spec-Datei modifizieren, erstellen oder löschen — auch wenn die Korrektur offensichtlich scheint
- **DARF NICHT** das Netzwerk bemühen; alle fürs Audit nötigen Informationen leben im Arbeitsbaum (Specs, Audience-Artefakte, Git-Historie)

### Audit-Artefakt
- **MUSS** das Ergebnis jedes Audits als Commit, Issue oder Datei im Repository persistieren; der Artefaktort **SOLLTE** pro Repository konsistent gewählt werden (zum Beispiel `.audits/spec-readiness/YYYY-Q<n>.md` oder ein GitHub-Issue mit Label `spec-readiness`)
- **MUSS** im Artefakt enthalten: Datum, Auslöser (quartalsweise, pre-promotion, PR-change), Scope (welche Specs auditiert wurden, welche ausgenommen), die auditierte Git-Revision, Schweregrad-Zählungen pro Spec und die vollständige Befundliste sortiert nach Schweregrad
- **SOLLTE** auf das vorherige Audit-Artefakt verlinken, damit der Reife-Verlauf des Portfolios über Quartale hinweg nachvollziehbar bleibt
- **SOLLTE** dem `review-plan`-Artefaktformat folgen, wenn das Audit eine einzelne Spec vor einer Beförderungsentscheidung anvisiert, damit die Ausgabe in dieselbe Audit-Mechanik wie Skill-Review und Agent-Review passt
- **SOLLTE** `spec/project/parallel-working-copies/` §Audit artefacts in multiple worktrees heranziehen, wenn das Audit in einem Worktree statt im primären Checkout läuft, da die Repository-weite Eindeutigkeit des Artefakts nur innerhalb eines Arbeitsbaums zugleich beobachtbar ist und die Worktree-lokalen Commit-, Transfer- und Aufräum-Regeln dort leben

### Abgrenzung
- **MUSS** vom `spec`-Skill getrennt bleiben: dieser Skill erstellt, übersetzt, indiziert, dedupliziert Übersetzungen und prüft Übersetzungs-Drift; dieses Audit prüft die Reife des **Inhalts**
- **MUSS** von `spec/project/spec-drift-audit/` getrennt bleiben: dieses Audit gleicht Spec vs. **Implementierung** ab (Code und Konfig); das hier gleicht eine Spec gegen **sich selbst** und gegen **andere Specs** ab
- **MUSS** von `spec/project/audience-identification/` getrennt bleiben: dieser Skill produziert ein Audience-Artefakt für ein Modul; dieses Audit prüft, ob eine existierende Spec ihrer ableitbaren Audience **dient**
- **MUSS** von `spec/project/prose-style/` getrennt bleiben: Vale besitzt Prosa-Korrektheit und Vokabular; dieses Audit ist indifferent gegenüber Prosa-Stil, außer er verursacht direkt einen Widerspruch oder ein unparseares RFC-Verb
- **DARF NICHT** Peer-Review ersetzen — dieses Audit macht die mechanischen Befunde sichtbar, und ein menschlicher Reviewer besitzt weiterhin die Urteilsentscheidungen, die das Audit sichtbar macht (in welche Richtung ein Widerspruch aufgelöst wird, ob ein Nicht-Ziel fehlt)

## Akzeptanzkriterien
- [ ] Jede Spec im Portfolio mit nicht-leerer `## Requirements`- oder `## Acceptance Criteria`-Sektion hat seit Einführung dieser Spec mindestens einen Reife-Audit-Eintrag in der Audit-Historie des Repositorys, oder eine dokumentierte Ausnahme
- [ ] Keine Spec mit unerledigten `Critical`-Reife-Befunden ist seit Einführung dieser Spec aus `Status: draft` befördert worden — entweder ist der Befund gelöst, oder die Beförderung ist blockiert, oder eine Waiver-Notiz ist im Audit-Artefakt festgehalten
- [ ] Das Audit-Artefakt jedes Reife-Laufs hält Scope (auditierte Spec-Slugs), auditierte Git-Revision, Schweregrad-Zählungen pro Spec und die vollständige Befundliste fest
- [ ] Kein Cross-Spec-Widerspruch zwischen zwei Specs, die beide aus Draft befördert wurden, bleibt im jüngsten Audit ohne dokumentierte Auflösung stehen — entweder ist der Widerspruch in den Quell-Specs gelöst, oder eine Waiver-Notiz ist im `## Processing log` des Audit-Artefakts laut `spec/claude/review-plan/` §Severity scale festgehalten
- [ ] Der Agent `agents/spec-readiness-reviewer.md` erzeugt Befunde, die 1-zu-1 auf die drei hier deklarierten Dimensionen und die kanonische Schweregrad-Skala abbilden, die diese Spec zitiert (definiert in `spec/claude/review-plan/` §Severity scale), damit Audit-Artefakte mechanisch erzeugt werden können
- [ ] Kein Audit-Lauf in irgendeinem Repository hat eine Spec-Datei modifiziert; die Read-only-Disziplin hält in der Praxis, nicht nur in dieser Spec
- [ ] Reife-Audit-Artefakte für Einzel-Spec-Beförderungsläufe entsprechen dem `review-plan`-Artefaktformat, damit sie von derselben Review-Closure-Mechanik wie Skill- und Agent-Review konsumierbar sind
- [ ] Jede Sektions-Referenz in jeder konfigurierten Sprachdatei einer in-Scope-Spec löst gegen die Überschriften der Datei der Ziel-Spec **in derselben Sprache** auf; eine Referenz, die nur in der kanonischen Sprache auflöst, wird als `Critical` gemeldet

## Offene Fragen

_Alle zuvor zurückgestellten offenen Fragen wurden am 2026-06-06 entschieden: jeder vorläufige Default ist nun die geltende Regel. Die Einzelentscheidungen und Begründungen sind in der Git-Historie erhalten (Entscheidungslog, 2026-06-06)._

- Die in §Geltungsbereich und §Dimension 3 ergänzte Sprachdatei-Regel ist vom Korpus heute **nicht** erfüllt. Ein erster Durchgang über alle `spec/<topic>/<slug>/`-Sektions-Referenzen fand einen erheblichen Rückstand, konzentriert auf eine Klasse: eine Übersetzung zitiert den **kanonischen** Sektionsnamen, während das übersetzte Ziel eine übersetzte Überschrift trägt. Drei bestätigte Fälle: `spec/claude/review-plan/` wird aus deutschen Dateien als §"Severity scale" zitiert, während die Zielüberschrift `Schweregrad-Skala` lautet; `spec/project/mkdocs-structure/` wird als §"language parity" zitiert, während die Überschrift `i18n and parity` lautet; `spec/project/lektorat/` wurde als §"Detection dimensions" zitiert, während die Überschrift `Quality dimensions` lautet (in der zitierenden Spec behoben). Ein maschineller Durchgang kann Kandidaten vorschlagen, sie aber nicht entscheiden, denn ein bewusst verkürzter Sektionsname liest sich für Menschen korrekt, und nur eine Einzelfall-Beurteilung trennt beides. Der Bereinigungslauf ist daher ein nachgelagerter Vorgang, nicht Teil der Änderung, die die Regel eingeführt hat, und das zugehörige Akzeptanzkriterium wird bis dahin absehbar fehlschlagen.
