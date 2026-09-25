# Audit der tatsächlichen Reichweite von Fähigkeiten

Status: draft

## Kontext

In zwei Tagen gemessener Issue-Arbeit an einem Repository wurden fünf Defekte einer einzigen Gestalt gefunden. Nach keinem davon wurde gesucht. Jeder trat als Nebenwirkung unverwandter Arbeit zutage: einer Dokumentationskorrektur, einer CVE-Pinnung, einer Sicherheitsfrage, einer Abfragereparatur.

| Fähigkeit | Deklariert | Tatsächlich erreicht |
|---|---|---|
| Datenexport | 15 Collections und 8 Kanten | 0 |
| Abschluss der Löschung | 26 Collections löschen oder unkenntlich machen | 0 gelöscht, 0 unkenntlich gemacht |
| Ranking-Dienst | ein funktionierender Ranking-Endpunkt | `/ready` antwortet dauerhaft mit 503, während `HEALTHCHECK` gesund meldet |
| Scan-Spur auf Abruf | Scan auf Abruf | 0 von 300 `pull_request`-Läufen ausgeführt |
| Inventar personenbezogener Daten | eine Aufzählung | zwei deklarierte Inventare, und das gepflegte ist nicht das ausführende |

Frühere Fälle aus demselben Repository: eine spezifizierte, aber nirgends verdrahtete Berechtigungsprüfung, mehrere implementierte und wirkungslose Wächter, und ein Wächter, den sein eigener Allowlist-Eintrag entschärfte.

Die gemeinsame Gestalt ist nicht unfertige Arbeit. Es ist ein Artefakt, das existiert, typprüft, Tests trägt und Erfolg meldet, während es nichts von dem Umfang erreicht, den es deklariert. Jeder Fall hat ein Code-Review bestanden. Mehrere haben ein grünes CI-Gate passiert. Die Zeilenabdeckung war bei allen hoch.

Die Kosten sind nicht nur die Defekte. Es ist, dass ihr Auffinden davon abhängt, was jemand zufällig angefasst hat, die Abdeckung also zufällig ist.

Dieses Repository trug früher eine statische Audit-Schicht, und sie wurde entfernt, weil sie Gerüste als vollständig zählte. Das ist derselbe Fehlschlag: sie fragte, ob das Artefakt existiert, und bekam damit die falsche Antwort auf die einzige Frage, auf die es ankam. Dieser Spec existiert, weil die Frage stattdessen durch Ausführung beantwortet werden muss, und §"Warum dies die entfernte Audit-Schicht nicht wiederholt" benennt, was den Unterschied strukturell statt zu einer Frage der Sorgfalt macht.

## Ziele

- Je deklarierter Fähigkeit feststellen, ob der ausführende Pfad den Umfang erreicht, den die Fähigkeit deklariert, indem etwas ausgeführt und nicht etwas gelesen wird.
- Zufällige Abdeckung durch eine bewusste, aufzählbare Prüfmenge ersetzen.
- Die blinden Flecken des Audits selbst zu einer berichteten Zahl machen statt zu einem Schweigen.
- Den zweiten Lauf zu einem Diff machen, damit das Audit billig genug bleibt, um es zu wiederholen.

## Nicht-Ziele

- Kein Ersatz für `spec/project/capability-maturity-assessment/`. Jenes benotet Qualität auf drei Achsen. Dieses stellt eine Tatsache fest, die jene Benotung derzeit auf Treu und Glauben nimmt.
- Kein Merge-Gate. Dies ist eine periodische Messung des Gesamtsystems. Eine dabei aufgedeckte Klasse wird zu einem Wächter nach `spec/project/defect-class-guards/`; das Audit selbst blockiert nichts.
- Keine Testsuite. Es behauptet nicht, dass Verhalten korrekt ist, sondern nur, dass Verhalten überhaupt stattfindet.
- Keine Abdeckungsmetrik. Die Zeilenabdeckung war bei jedem der obigen Defekte hoch.
- Keine Spezifikation des Ausführenden. Dieser Spec sagt, was ein Audit feststellen und berichten muss, nicht wie ein Skill oder Agent das umsetzt.

## Anforderungen

### Die Prüfmenge

- **MUSS [MUST]** die Prüfmenge aus dem ableiten, was das Projekt **über sich deklariert**, gezogen aus vier Deklarationsquellen, von denen jede ihre eigene Probenform trägt:
  1. ein **Anforderungsdokument**, einschließlich einer Spezifikation, eines Feature-Datensatzes oder eines Regelwerksartikels, den das Projekt zu erfüllen behauptet;
  2. ein **spezifizierter Endpunkt**, einschließlich eines API-Vertrags, einer dokumentierten Route, eines geplanten Jobs oder eines Workflow-Triggers;
  3. eine **dokumentierte Fähigkeit**, einschließlich einer README-Behauptung, einer veröffentlichten Seite oder einer Skill- oder Agent-Beschreibung;
  4. ein **deklariertes Inventar**, also eine Aufzählung, die das Projekt über sich selbst pflegt, etwa ein Inventar personenbezogener Daten, eine Collection-Liste oder ein Register unterstützter Provider.
- **DARF NICHT [MUST NOT]** die Prüfmenge daraus ableiten, was der Quellbaum zufällig enthält. Ein aus dem Code gebautes Inventar kann eine Fähigkeit nicht enthalten, die der Code nie umgesetzt hat, und das ist der wichtigste Fall.
- **MUSS [MUST]** eine deklarierte und gänzlich abwesende Fähigkeit als schwerste Befundklasse melden, nie als Lücke im Inventar.
- **MUSS [MUST]** je Eintrag die Deklarationsquelle und die genaue `datei:zeile` oder Dokumentstelle festhalten, die ihn deklariert hat, damit ein Lesender den Eintrag bestreiten kann statt das Urteil.

### Die Probe

- **MUSS [MUST]** je Eintrag eine Beobachtung festlegen, die **erreicht** von **nicht erreicht** unterscheidet, und diese Beobachtung **MUSS [MUST]** durch Ausführung entstehen: eine Anfrage und ihr Antwortkörper, ein Container, der bereit wird und antwortet, eine Datei, die der Export tatsächlich geschrieben hat, Zeilen, die eine Löschung tatsächlich entfernt hat, der Lauf-Nachweis einer Plattform über tatsächlich stattgefundene Läufe.
- **MUSS [MUST]** den Beobachtungspunkt **außerhalb des geprüften Artefakts** legen. Das ist die tragende Regel dieses Specs, und jeder Defekt in §Kontext schlägt ein Audit, das sie ignoriert. Der Nachweis ist das Archiv, das der Export erzeugt hat, nicht das Statusfeld, das der Export gesetzt hat. Es sind die verbliebenen Zeilen in der Datenbank, nicht der Rückgabewert der Löschung. Es ist der Körper einer Ranking-Antwort, nicht der Gesundheitsbericht des Containers über sich selbst.
- **MUSS [MUST]** die **tatsächliche Ausgabe** der Probe als Nachweis festhalten. Ein als bestanden vermerkter Eintrag, dessen Probe nie lief, liest sich wie ein Nachweis und ist schlimmer als gar kein Vermerk.
- **DARF NICHT [MUST NOT]** eine selbstgemeldete Erfolgsangabe als Messung der Reichweite akzeptieren. Jedes der folgenden Signale war in einem der obigen Defekte genau das, was log: ein Statusfeld mit `completed`, ein HTTP 2xx, ein grüner Build, ein bestandener `HEALTHCHECK`, ein Exitcode null für sich allein, und eine Logzeile, die das Artefakt über sich selbst schreibt.
- **DARF NICHT [MUST NOT]** zulassen, dass die bloße Existenz des Artefakts zur Reichweite beiträgt. Ein Gerüst erreicht null, weil seine Probe nichts beobachtet, nicht weil eine Markierung darin gefunden wurde. Kein Defekt in §Kontext trägt eine Unfertig-Markierung, ein `TODO`, eine Stub-Rückgabe oder ein Feature-Flag.
- **MUSS [MUST]** einen Eintrag, für den sich auf keiner Stufe eine Probe konstruieren lässt, als **nicht geprobt** melden, nie als erreicht und nie, indem er aus der Menge fällt, und **MUSS [MUST]** den Grund festhalten, aus dem keine Probe konstruierbar war. Sonst existiert die Einordnung nur in der Prosa, und eine umsetzende Person hat keine Regel, die sie erzwingt.
- **SOLLTE [SHOULD]** die erwartete Beobachtung als Anzahl oder Menge ausdrücken, wo die Deklaration selbst eine Anzahl oder Menge ist, denn `0 von 15 Collections` ist ein Befund und `der Export lief` nicht.

### Umgebungsstufen

- **MUSS [MUST]** je Probe genau eine Umgebungsstufe deklarieren:
  - **T0**, keine Umgebung: die Probe läuft gegen einen Nachweis oder eine Schnittstelle, die bereits existiert, etwa die Lauf-Historie einer Plattform oder ein veröffentlichtes Artefakt.
  - **T1**, eine kurzlebige Abhängigkeit: die Probe startet einen Container oder einen temporären Dienst und beobachtet ihn.
  - **T2**, voller Stack mit Saatdaten: die Probe braucht ein laufendes System mit Daten, die sie dort abgelegt hat.
- **MUSS [MUST]** die Reichweite **je Stufe** berichten, samt dem ungeprobten Rest, damit das Fahren nur der billigen Stufen in der Ausgabe sichtbar wird statt von einem sauberen Ergebnis ununterscheidbar zu sein.
- **DARF NICHT [MUST NOT]** eine niedrigere Stufe für eine höhere einstehen lassen. Wenn der deklarierte Umfang einer Fähigkeit nur auf T2 beobachtbar ist, gilt eine T0-Probe dafür als **nicht geprobt**, nie als bestanden. Ohne diese Regel wird die Stufung zu einem Weg, ein grünes Audit zu melden, das nichts gemessen hat, und genau das soll dieser Spec verhindern.
- **MUSS [MUST]** T0 als Ausführung behandeln, nicht als statisches Lesen. Eine Plattform danach zu fragen, welche Läufe tatsächlich ausgeführt wurden, ist die Beobachtung einer Wirkung. Die Workflow-Datei zu lesen, die sie auslösen sollte, ist es nicht, und die Scan-Spur auf Abruf in §Kontext ist genau diese Unterscheidung. T0 stellt fest, dass etwas lief, nie dass es funktioniert, sodass ein T0-Ergebnis für sich genommen nie Korrektheit bescheinigt.

### Herleitung, Abnahme und Dauerhaftigkeit

- **MUSS [MUST]** Proben-Kandidaten aus der Deklaration herleiten, sie der Betreiberin zur Abnahme vorlegen und die abgenommene Menge als **versioniertes Artefakt unter Versionskontrolle** ablegen.
- **MUSS [MUST]** bei jedem späteren Lauf die abgelegten Proben ausführen statt sie neu herzuleiten. Die Herleitung macht den ersten Lauf teuer; die Ausführung macht den zweiten Lauf zu einem Diff.
- **MUSS [MUST]** eine Probe neu herleiten, wenn sich ihre Deklaration ändert, und **MUSS [MUST]** diese Änderung erkennen, statt darauf zu warten, dass es jemand bemerkt. Eine Probe, die weiterhin gegen eine verschobene Deklaration besteht, ist ein falsches Bestehen.
- **MUSS [MUST]** eine Probe am **Inhalt** ihrer Deklaration verankern, wo die Deklaration im geprüften Repository liegt, nicht an dem Commit, an dem sie gelesen wurde. Der Squash-Merge, den das Portfolio vorschreibt, gibt der Änderung einen neuen Commit und nimmt den Branch-Commit aus der Historie des Standard-Branches, während der Inhalt der Deklaration ihn unverändert übersteht; ein Commit-Anker, der im selben Pull Request wie die Deklarationsänderung festgehalten wurde, lässt sich nach dem Merge daher nicht mehr auflösen. Eine spätere Änderung der Deklaration wird dann als Änderung erkannt, und das Verschieben des Ankers zählt nur dann als Neuherleitung, wenn sich der verankerte Inhalt geändert hat und der neue Anker der Deklaration entspricht, wie sie der Commit enthält, der die Probe festgehalten hat. Eine geerbte Spec bleibt an ihrer gepinnten Referenz verankert; ein vor dieser Regel festgehaltener Commit-Anker bleibt gültig, bis die Probe das nächste Mal neu hergeleitet wird.
- **SOLLTE [SHOULD]** eine Probe an den **Abschnitten** verankern, die sie zitiert, statt an der ganzen Datei, wo die Deklaration ein Markdown-Dokument ist und jeder zitierte Abschnitt eindeutig auflöst, über eine Überschriftennummer oder die erste Zelle einer Tabellenzeile. Ein Anforderungsdokument wird weit öfter geändert als jeder einzelne seiner Abschnitte: Über siebzehn Änderungen eines Anforderungsdokuments bei einem Consumer wären fünf an der ganzen Datei verankerte Proben 85-mal veraltet gewesen, an ihren Abschnitten verankert 11-mal. Eine Probe veraltet dann, wenn sich ein zitierter Abschnitt ändert oder nicht mehr auffindbar ist, und folgt nie einem umnummerierten oder umbenannten Abschnitt. Ein Locator, der mehr als eine Stelle trifft, ist kein Abschnittsanker, und seine Probe behält den Dateianker.
- **MUSS [MUST]** für eine veraltete Probe, deren Deklaration sich geändert hat, ohne das Geprüfte zu berühren, eine **Neubestätigung** anbieten: Der Operator sieht die Änderung der Deklaration seit dem Anker, bestätigt jede Probe einzeln, und der neue Anker wird zusammen mit einer Markierung festgehalten, die die Neubestätigung im Bericht von einer Neuherleitung unterscheidet. Eine Neubestätigung, die an der Probe mehr als ihren Anker und ihre Abnahme ändert, wird als Abschwächung sichtbar gemacht, und das Verschieben jedes Ankers bleibt demselben Nachweis unterworfen wie eine Neuherleitung. Proben, die bereits an einer ganzen Markdown-Datei verankert sind, werden einmalig auf Abschnittsanker migriert, jede einzeln bestätigt.
- **MUSS [MUST]** die **Probenmenge** zum dauerhaften Ergebnis machen. Der Bericht wird durch ihre Ausführung neu erzeugt und ist nie selbst das gepflegte Artefakt.
- **MUSS [MUST]** je Lauf berichten, welche Proben sich seit dem vorigen Lauf geändert haben und in welcher Änderung. Eine Probe, die abgeschwächt wurde, seit die von ihr geprüfte Deklaration zuletzt geändert wurde, **MUSS [MUST]** als Befund sichtbar gemacht statt akzeptiert werden, gleich ob beide zusammen geändert wurden. Auf eine einzelne Änderung eingeschränkt, entginge der Regel eine über zwei Änderungen verteilte Abschwächung, und das ist der gewöhnliche Fall, nicht der ausgefallene. Die Probenmenge liegt im geprüften Repository, damit sie mit derselben Änderung prüfbar ist, die sie entwertet, und ist damit auch von dieser Änderung editierbar: genau die Gestalt, die einen Wächter durch seinen eigenen Allowlist-Eintrag entschärfte. Diese Regel ist es, die das Beisammenliegen sicher statt bloß bequem macht.
- **MUSS [MUST]** je Berichtseintrag den Zeitstempel tragen, zu dem diese Probe zuletzt lief. Ein Bericht, der zitiert wird, nachdem er aufgehört hat zu stimmen, ist dann sichtbar veraltet, und das ist die konkrete Antwort auf die entfernte Audit-Schicht, deren Ergebnis ein Dokument war.

### Berichterstattung

- **MUSS [MUST]** jeden Eintrag in genau eine Klasse einordnen: **erreicht**, **teilweise erreicht**, **nicht erreicht**, **nicht geprobt**.
- **MUSS [MUST]** die Reichweite als **Verhältnis samt der Messung** ausdrücken, die es erzeugt hat, etwa `0/15 Collections, gemessen durch <Kommando>`. Eine Note ist nicht handlungsfähig, und ein nacktes Urteil verbirgt, ob überhaupt jemand nachgesehen hat.
- **DARF NICHT [MUST NOT]** eine Stufe oder Note als primäre Ausgabe liefern. Eine Benotung **KANN [MAY]** das Ergebnis dieses Audits verbrauchen; sie ersetzt es nie.
- **MUSS [MUST]** den Bericht mit der **Anzahl der nicht geprobten Einträge** eröffnen. Diese Zahl ist das ehrliche Maß der Abdeckung des Audits selbst, und sie zu vergraben lässt ein Audit, das ein Drittel der Oberfläche gemessen hat, vollständig aussehen.
- **MUSS [MUST]** die Herkunft der Prüfmenge angeben: welche Deklarationsquellen gelesen wurden, welche nicht verfügbar waren, und worüber das Audit daher nicht sprechen kann.

### Abgrenzung

Das Audit ist ebenso durch das bestimmt, was bereits existiert, wie durch das, was es hinzufügt. Jede Zeile benennt den Grund, aus dem der benachbarte Spec diese Frage nicht beantworten kann.

| Spec | Was er tut | Warum er die Reichweite nicht feststellt |
|---|---|---|
| `spec/project/capability-maturity-assessment/` | Benotet Vollständigkeit, Qualität und Testtiefe | Seine Achse A ist von Entwurf wegen eine Urteilseingabe, und sein Scanner fördert Markierungen zutage. Kein Defekt in §Kontext trägt eine Markierung; jeder hat einen Docstring, eine plausible Signatur, bestehende Tests und eine normale Rückgabe. |
| `spec/project/quality-gate/` | Eine lokale oder aufrufbare Vorprüfung, die spiegelt, was CI über die schnellen Stufen fährt | Vier der fünf Defekte gingen durch eben diese Prüfungen, während sie grün waren. Seine eigenen Nicht-Ziele sagen, dass er CI nicht ersetzt und CI die maßgebliche Instanz für den Merge-Schutz bleibt, also beansprucht er auch nicht, das Gate zu sein. |
| `spec/project/spec-drift-audit/` | Gleicht Spezifikation und Umsetzung ab | Er liest beide. Das fängt einen Spec, der einen nicht existierenden Konfigurationsschlüssel nennt; es fängt keine Funktion, deren Körper nichts erreicht. |
| `spec/project/defect-class-guards/` | Verweigert eine Defektklasse, sobald sie benannt ist | Von Konstruktion her reaktiv. Er ist die richtige Antwort nach einem Befund und kann keine Abdeckung erzeugen. |
| `spec/project/test-falsifiability/` | Fragt, ob ein Test belegt, was er behauptet | Notwendig, und er hat mehrere dieser Fälle geklärt, nachdem jemand nachgesehen hatte. Er sagt nicht, wo nachzusehen ist. |
| `spec/project/gdpr-audit-process/` | Auditiert eine Domäne von Anfang bis Ende | Nach seinem eigenen Abschnitt §"Read-only-Vertrag" streng lesend, und seine Klasse „code-verifizierbar" heißt: aus dem Repository bestätigt. Zwei Defekte in §Kontext liegen in seiner Domäne, und er fand sie nicht. Dieses Audit steht **daneben**, mit dem umgekehrten Mechanismus, und übernimmt seine Ehrlichkeitsgrenze: genau eine Klasse je Befund, und ein nicht überprüfbarer Eintrag wird nie als bestanden gemeldet. |

## Abnahme am Beispiel: Die fünf Defekte

Ein Lesender **MUSS [MUST]** für jeden Defekt in §Kontext beantworten können, ob dieses Audit ihn findet und durch welche Messung. Die Tabelle ist der Abnahmetest dieses Specs, und jede Zeile benennt die Probe statt des Urteils.

| Defekt | Deklarationsquelle | Probe, und der Beobachtungspunkt außerhalb des Artefakts | Stufe | Messung |
|---|---|---|---|---|
| Datenexport erreicht 0 Collections | Anforderungsdokument (Auskunftsrecht) | Export für eine gesäte betroffene Person fahren, dann das erzeugte Archiv öffnen und die **Datensätze je Collection** zählen und je gegen das Gesäte halten. Die vorhandenen Collections zu zählen würde wieder Anwesenheit messen, und ein Export, der 15 leere Dateien schreibt, bestünde. Nicht das Statusfeld des Jobs. | T2 | `0/15 Collections, 0/8 Kanten` |
| Abschluss der Löschung löscht nichts | Anforderungsdokument (Recht auf Löschung) | Eine betroffene Person über alle 26 Collections säen, Löschung fahren, dann die noch passenden Zeilen zählen und die Zeilen mit veränderten Werten. Nicht der vermerkte `status`. | T2 | `0/26 gelöscht, 0/26 unkenntlich gemacht` |
| Ranking-Dienst wird nie bereit | dokumentierte Fähigkeit | Den Container starten, dann den Ranking-Endpunkt selbst mit Zeitgrenze abfragen, um den Absendezeitpunkt zu bestimmen, nie eines der beiden Statussignale. Zwei Anfragen senden, deren richtige Reihenfolgen sich unterscheiden, und prüfen, dass die Antwortkörper sich entsprechend unterscheiden; eine konstante Antwort muss durchfallen, sonst bestünde ein Stub. Nicht `HEALTHCHECK` und nicht `/ready`, die einander widersprachen. | T1 | `0/1 Endpunkte antworten` |
| Scan-Spur läuft nie | spezifizierter Endpunkt (Workflow-Trigger) | Die Plattform nach Ausführungen dieses Jobs über die letzten 300 Ereignisse seines deklarierten Triggers fragen. Nicht die Workflow-Datei, die den Trigger deklariert. | T0 | `0/300 Läufe ausgeführt` |
| Zwei Inventare personenbezogener Daten, eines ausführend | deklariertes Inventar | Die Aufzählung ausführen, die der Code tatsächlich aufruft, ihre Rückgabe festhalten und gegen jedes deklarierte Inventar diffen. | T2 | `1 von 2 deklarierten Inventaren deckt sich mit dem ausführenden` |

Jede Zeile beobachtet eine Wirkung, die der deklarierte Umfang der Fähigkeit nach sich zieht, an einer Stelle, die die Fähigkeit nicht selbst schreibt. Jeder aus diesem abgeleitete Spec, der diese Tabelle nicht für alle fünf Zeilen füllen kann, hat die Anforderung nicht erfüllt.

## Warum dies die entfernte Audit-Schicht nicht wiederholt

Die entfernte Schicht zählte Gerüste als vollständig, weil Existenz ihre Maßeinheit war. Drei Regeln hier machen dieses Ergebnis unerreichbar statt bloß unerwünscht:

1. **Existenz trägt nichts bei.** Reichweite ist ausschließlich eine Funktion einer beobachteten Wirkung, sodass ein Gerüst von Konstruktion wegen null erreicht. Es gibt keinen Weg, auf dem die Existenz eines Artefakts seine Zahl hebt.
2. **Der Beobachtungspunkt liegt außerhalb des Artefakts.** Jede Selbstauskunft, die das Artefakt abgeben kann, ist namentlich ausgeschlossen, sodass ein Artefakt sein eigenes Audit nicht bestehen kann, indem es behauptet, funktioniert zu haben.
3. **Nicht nachzusehen ist eine berichtete Zahl, kein Schweigen.** §"Die Probe" verlangt, einen Eintrag ohne auf irgendeiner Stufe konstruierbare Probe als nicht geprobt samt Grund zu melden, und §Berichterstattung verlangt, dass diese Zahl den Bericht eröffnet, sodass ein Audit, das wenig gemessen hat, sich nicht wie ein Audit lesen kann, das wenig gefunden hat.

Die entfernte Schicht scheiterte an allen dreien. Sie maß Existenz, sie vertraute der Selbstauskunft des Artefakts, und eine Fähigkeit, die sie nicht beurteilen konnte, senkte ihren Prozentsatz schlicht nicht.

## Akzeptanzkriterien

- [ ] Die Prüfmenge ist aus den vier Deklarationsquellen gebaut, und jeder Eintrag nennt Quelle und Stelle, die ihn deklariert hat.
- [ ] Eine deklarierte und gänzlich abwesende Fähigkeit erscheint als schwerste Klasse, nicht als fehlender Eintrag.
- [ ] Jeder Eintrag trägt eine Probe, deren Ausgabe durch Ausführung entstand, und der Bericht hält diese Ausgabe fest statt einer Behauptung darüber.
- [ ] Das Urteil keines Eintrags ruht auf einem Statusfeld, einem HTTP 2xx, einem grünen Build, einem `HEALTHCHECK`, einem Exitcode für sich allein oder einer Logzeile, die das Artefakt über sich selbst schreibt.
- [ ] Jede Probe deklariert genau eine der Stufen T0, T1, T2, und eine nur auf höherer Stufe beobachtbare Fähigkeit wird als nicht geprobt gemeldet, wenn sie auf niedrigerer geprobt wurde.
- [ ] Ein Eintrag ohne auf irgendeiner Stufe konstruierbare Probe erscheint als nicht geprobt samt festgehaltenem Grund und zählt in die Kopfzahl.
- [ ] Ein Lauf berichtet, welche Proben sich seit dem vorigen Lauf geändert haben, und eine Probe, die abgeschwächt wurde, seit ihre Deklaration zuletzt geändert wurde, wird sichtbar gemacht statt akzeptiert, gleich ob beide zusammen geändert wurden.
- [ ] Der Bericht eröffnet mit der Anzahl der nicht geprobten Einträge und gibt die Herkunft der Prüfmenge an.
- [ ] Reichweite ist als Verhältnis samt erzeugendem Kommando ausgedrückt; keine Note erscheint als primäre Ausgabe.
- [ ] Die Probenmenge steht unter Versionskontrolle, spätere Läufe führen sie aus statt sie neu herzuleiten, und jeder Berichtseintrag trägt den Ausführungszeitstempel seiner Probe.
- [ ] Eine Deklaration, die sich seit der Abnahme ihrer Probe geändert hat, wird erkannt, und ihre Probe wird neu hergeleitet statt erneut gefahren.
- [ ] Eine Probe, die im selben Pull Request wie die Änderung ihrer Deklaration neu hergeleitet wurde, bleibt nach dem Squash-Merge dieses Pull Requests unverändert gültig, eine spätere Änderung der Deklaration macht sie veraltet, und ein Verschieben ihres Ankers ohne Änderung des verankerten Inhalts wird als Abschwächung sichtbar gemacht.
- [ ] Eine Änderung außerhalb aller Abschnitte, die eine an Markdown verankerte Probe zitiert, lässt sie gültig, eine Änderung in einem davon oder ein nicht mehr auffindbarer Abschnitt macht sie veraltet, und eine veraltete Probe lässt sich neu bestätigen, nachdem der Operator die Änderung gesehen hat, wobei die Neubestätigung im Bericht von einer Neuherleitung unterscheidbar ist.
- [ ] Die Tabelle in §"Abnahme am Beispiel: Die fünf Defekte" beantwortet für alle fünf Defekte sowohl ob das Audit ihn findet als auch durch welche Messung.

## Offene Fragen

- **Was begrenzt die Kosten von T2?** Ein voller Stack mit Saatdaten ist die Stufe, die die schwersten Defekte fängt, und die Stufe, die am ehesten übersprungen wird. Ob die Grenze ein Zeitbudget, eine Stichprobe der Einträge oder eine langsamere Kadenz allein für T2 ist, ist ungeklärt.
- **Wie wird eine Fähigkeit geprobt, deren Wirkung außerhalb liegt?** Wenn die deklarierte Wirkung in einem Fremdsystem landet, ist der Beobachtungspunkt außerhalb des Artefakts in einer Audit-Umgebung womöglich unerreichbar. Ein solcher Eintrag ist heute nicht geprobt, was ehrlich ist, aber ein großer Anteil der Menge sein kann.
- **Welche Kadenz hält die Menge aktuell, ohne sie neu herzuleiten?** Der Spec verlangt, eine geänderte Deklaration zu erkennen, und sagt noch nicht, wie oft diese Erkennung läuft.

## Quellen

- Die fünf Defekte und die entfernte statische Audit-Schicht: `nolte/kamerplanter#1645`, `#1609`, `#1607`, `#1622`, `#1614`, festgehalten in `nolte/claude-shared#660`.
- Achse A als Urteilseingabe: der Abschnitt §"Machine-derivable vs. judgement inputs" in `spec/project/capability-maturity-assessment/en.md`.
- Der lesende Vertrag und die Überprüfbarkeitsgrenze, die dieser Spec übernimmt: die Abschnitte §"Read-only contract" und §"Code-verifiable versus legal-review boundary" in `spec/project/gdpr-audit-process/en.md`.
- Schweregrad-Vokabular: der Abschnitt §"Severity scale" in `spec/claude/review-plan/`.
