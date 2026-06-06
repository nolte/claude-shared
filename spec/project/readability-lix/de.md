# Lesbarkeit (LIX)

Status: draft

## Kontext

Portfolio-Repositories messen Lesbarkeit bereits innerhalb der redaktionellen Ebene: [`spec/project/lektorat/`](../lektorat/de.md) §D1 bewertet englische Prosa mit Flesch Reading Ease (FRE) und Flesch–Kincaid Grade Level (FKGL) und deutsche Prosa mit der Wiener Sachtextformel (WSTF) und LIX. Diese Aufteilung hat für einen zweisprachigen Korpus eine strukturelle Schwäche: die englische und die deutsche Hälfte desselben Dokumentationssatzes werden an **unterschiedlichen, nicht vergleichbaren** Skalen gemessen, sodass „ist diese Seite lesbar?" keine einzelne Antwort hat, die über das EN ↔ DE-Paar hinweg trägt, und eine iterative Autor-zu-Lektor-Schleife keinen gemeinsamen Zielwert hat, auf den sie konvergieren kann.

LIX (Läsbarhetsindex, Carl-Hugo Björnsson, 1968) ist die eine Metrik in diesem Satz, die **vergleichsweise sprachunabhängig** ist: sie zählt Buchstaben, nicht Silben — deshalb fanden sprachübergreifende Korrelationsstudien (Französisch/Englisch, Deutsch/Englisch, Griechisch/Englisch), dass übersetzte Paralleltexte unter LIX ihre relative Schwierigkeits-Rangfolge behalten. Diese Spec erhebt LIX von „der Nur-Deutsch-Metrik" zur **primären, sprachübergreifenden Lesbarkeitsmetrik**, die für Englisch und Deutsch identisch berechnet wird, sodass ein einziger Lesbarkeits-Zielwert den gesamten zweisprachigen Korpus regiert und die Autor ↔ Lektor-Schleife eine Zahl hat, die sie senken kann.

Diese Spec ist die **einzige Quelle der Wahrheit** für: die LIX-Formel und ihre Langwort-Regel, die Tokenisierungs- und Segmentierungs-Entscheidungen, die einen LIX-Wert reproduzierbar und EN/DE-vergleichbar machen, die Skala-Interpretation, die sprachübergreifende Kalibrierung (das Deutsch-gegen-Englisch-Kaveat), die Zielkorridore pro Texttyp, den Katalog bedeutungserhaltender Transformationen, die einen LIX-Wert senken, und das Verhältnis von LIX zu den ergänzenden Metriken. [`spec/project/lektorat/`](../lektorat/de.md) §D1, [`spec/project/post-writing-style/`](../post-writing-style/de.md) und [`spec/project/lektorat-auto-revise/`](../lektorat-auto-revise/de.md) referenzieren diese Spec, statt etwas davon erneut zu formulieren.

**Leserschaft** dieser Spec sind Implementierer des `lektorat-scanner`-Agents (der LIX berechnet), der `lektorat-apply`- und `lektorat-auto-revise`-Skills (die die iterative Verbesserungsschleife antreiben) und der Autoren-Ebene (`audience-doc-author`-Agent, `blog-author`-Skill), deren Entwürfe an einem LIX-Korridor gemessen werden. Vertrautheit mit [`spec/project/mkdocs-structure/`](../mkdocs-structure/de.md) (dem `content_mode`-Enum), [`spec/project/lektorat/`](../lektorat/de.md) (den D1–D5-Dimensionen, der §Outputs-JSON-Form und den §Language-handling-Stripping-Regeln) und [`spec/project/audience-identification/`](../audience-identification/de.md) (dem Audience-Artefakt und den Protected-Terms-Quellen) wird vorausgesetzt; Begriffe aus jenen Specs werden ohne erneute Erklärung verwendet.

Eine bewusste Design-Ehrlichkeit: die **Formel, die Langwort-Schwelle und die fünf Interpretations-Referenzpunkte sind stabile, primärquellen-belegte historische Fakten** (Björnsson 1968). Die **Zielkorridore, der Deutsch-gegen-Englisch-Offset und das Hebel-Prioritäts-Ranking sind Engineering-Judgment**, kalibriert aus jenen Fakten plus den bestehenden `lektorat`-Korridoren, und durchgängig als solches gekennzeichnet. Jedes Judgment trägt eine Offene Frage mit einer Revisit-Bedingung, gegated an akkumulierten Portfolio-Audit-Daten, analog dazu, wie `lektorat` seine eigene Korridor-Kalibrierung behandelt.

## Ziele

- Eine **kanonische Definition von LIX** (Formel, Langwort-Regel, Tokenisierung, Segmentierung), die für Englisch und Deutsch **identisch** berechnet wird, sodass ein LIX-Wert über den zweisprachigen Korpus hinweg vergleichbar und über Läufe hinweg reproduzierbar ist.
- Ein **sprachbewusstes Zielkorridor-System** pro `content_mode`, mit einem expliziten Deutsch-Offset, der durch den dokumentierten Kompositum-Inflationseffekt begründet ist statt pro Repository erfunden zu werden.
- Ein **Katalog bedeutungserhaltender Transformationen**, die einen LIX-Wert senken, gemappt auf den Hebel, den jede bewegt (Satzlänge gegen Langwort-Anteil), und nach Wirkung und Risiko geordnet, mit einer expliziten Anti-Gaming-Grenze, die echte Lesbarkeitsgewinne von Edits trennt, die bloß die Zahl bewegen.
- Eine **gepinnte, reproduzierbare Berechnungs-Pipeline** (Library, Version, Tokenizer, Satz-Segmentierer), aufgezeichnet in den Lauf-Metadaten, sodass dieselbe Prosa denselben LIX-Wert liefert und EN und DE vergleichbar bleiben.
- Ein expliziter, **unterordnender Bezug zu den ergänzenden Metriken** (FRE/FKGL für Englisch, WSTF für Deutsch): LIX ist primär und sprachübergreifend; die anderen sind beratende Signale, die niemals einen LIX-Befund überstimmen.
- Eine Definition, wie LIX an der **iterativen Autor ↔ Lektor-Verbesserungsschleife** teilnimmt: der Konvergenz-Zielwert, die Briefing-Eingaben pro Durchlauf, die der Autor benötigt, und das Gate, das echte Verbesserung von Regression oder Gaming unterscheidet.

## Nicht-Ziele

- Definition der **redaktionellen Operations-Mechanik** (`audit` / `patch` / `revise`, Severity-Klassifikation, die Form des Findings-Report-JSON): die gehört [`spec/project/lektorat/`](../lektorat/de.md). Diese Spec definiert, **was LIX ist und wie es berechnet, anvisiert und verbessert wird**, was `lektorat` §D1 dann konsumiert.
- Definition von **Erstautorschafts-Voice, -Tonalität und -Struktur**: die gehören [`spec/project/prose-style/`](../prose-style/de.md) (Dokumentation) und [`spec/project/post-writing-style/`](../post-writing-style/de.md) (Blog-Posts). Diese Spec liefert den Lesbarkeits-Zielwert, auf den jene Autoren hinschreiben.
- **Neudefinition von FRE, FKGL oder WSTF**: die behalten ihre Definitionen aus ihren eigenen Quellen und bleiben ergänzende Signale (§Verhältnis zu anderen Metriken).
- Definition von **Routing, Re-Audit-Gate oder Per-Datei-Bound** der autonomen Revise-Schleife: die gehören [`spec/project/lektorat-auto-revise/`](../lektorat-auto-revise/de.md). Diese Spec definiert nur die LIX-spezifischen Eingaben und den Konvergenz-Zielwert, die jene Schleife konsumiert (§Iterative Verbesserungsschleife).
- **Implementierung** der Metrik: die Spec beschränkt die Formel, die Korridore, den Pipeline-Vertrag und die Reproduzierbarkeits-Garantien, nicht den Code. Die gewählte Library und der Tokenizer sind Implementierungsdetail, unterworfen den Pinning- und Vergleichbarkeits-Anforderungen unten.
- Als **blockierendes Release-Gate** zu wirken: die Severity und Gate-Tauglichkeit eines LIX-Befunds werden von `lektorat` §Severity-Klassifikation regiert (standardmäßig beratend), und diese Spec fügt kein eigenes blockierendes Verhalten hinzu.

## Anforderungen

### LIX-Definition (kanonisch)

- **MUSS [MUST]** LIX mit der kanonischen Björnsson-Formel berechnen:

  ```
  LIX = ASL + LWP
        wobei  ASL = A / B          (mittlere Satzlänge, Wörter pro Satz)
               LWP = (C × 100) / A  (Prozentsatz langer Wörter)
               A   = Anzahl der Wörter (Tokens)
               B   = Anzahl der Sätze
               C   = Anzahl der langen Wörter
  ```

  Äquivalent: `LIX = A/B + (C × 100)/A`. Das Ergebnis **MUSS [MUST]** als auf die nächste ganze Zahl gerundete Ganzzahl berichtet werden; die zugrundeliegenden `ASL`, `LWP` und die rohen Zählungen `A`, `B`, `C` **MÜSSEN [MUST]** in voller Genauigkeit für die Befund-Evidenz (§Reproduzierbarkeit) erhalten bleiben, damit ein Autor weiß, welchen Hebel er ziehen muss.
- **MUSS [MUST]** ein **langes Wort** als Wort von **mehr als 6 Buchstaben** definieren (das heißt **7 oder mehr**). Die Schwelle ist fix und **DARF NICHT [MUST NOT]** konfigurierbar gemacht werden; Björnsson wählte `> 6`, weil es den diskriminierenden Unterschied zwischen einfachen und schwierigen Texten maximierte, und eine bewegliche Schwelle würde die Vergleichbarkeit über Läufe und Repositories hinweg zerstören.
- **MUSS [MUST]** die **„Buchstaben gegen Zeichen"-Entscheidung** explizit pinnen, denn sie ist die dominante Quelle von EN/DE-Unvergleichbarkeit und von Drift zwischen Implementierungen:
  - Die Länge eines Worts für den Langwort-Test **MUSS [MUST]** die Zahl seiner **Unicode-Buchstaben** sein, einschließlich der deutschen `ä ö ü ß` und etwaiger akzentuierter lateinischer Buchstaben, und **MUSS [MUST]** umgebende oder eingebettete Interpunktion ausschließen (den abschließenden Punkt, Kommata, Anführungszeichen, Klammern).
  - Das weicht bewusst vom naiven `len(token)` ab, das manche Libraries verwenden (zum Beispiel misst `textstat` `len(w)`), denn rohe Zeichenlänge lässt abschließende Interpunktion und Zifferngruppen die Zählung an der Schwellen­kante verschieben und bricht die Vergleichbarkeit. Eine Implementierung, die auf einer solchen Library aufbaut, **MUSS [MUST]** Tokens normalisieren (umschließende Interpunktion entfernen), bevor sie den Längen-Test anwendet, oder dokumentieren, dass ihre Library das bereits tut.
- **MUSS [MUST]** die folgenden Token-Klassen über beide Sprachen hinweg konsistent behandeln:
  - **Zahlen**: ein numerisches Token (`2026`, `3.14`, `v1.2.0`) zählt als ein **Wort** zu `A` und zur `B`-relativen Satzlänge und zählt als **langes Wort** nur, wenn seine Buchstabenzahl 6 übersteigt — was, da Ziffern keine Buchstaben sind, bedeutet, dass ein rein numerisches Token **niemals** ein langes Wort ist. Das verhindert, dass Versionsstrings und Daten `LWP` aufblähen.
  - **Bindestrich-Wörter** (`build-and-test`, `Audience-Doc-Author`): zählen als **ein** Token; der Langwort-Test gilt für die Buchstabenzahl des gesamten Tokens. Das entspricht der Art, wie ein Leser ein einzelnes Bindestrich-Konzept parst.
  - **Abkürzungen und Akronyme**: als ein Token gezählt; der Langwort-Test gilt für ihre Buchstabenzahl. Abkürzungs-interne Punkte (`z. B.`, `e.g.`) **DÜRFEN NICHT [MUST NOT]** als Satzgrenzen behandelt werden (§Tokenisierung und Segmentierung).
- **MUSS [MUST]** LIX **nur über Prosa** berechnen: vor dem Scoring **MUSS [MUST]** eine Implementierung dieselben Nicht-Prosa-Elemente entfernen, die [`spec/project/lektorat/`](../lektorat/de.md) §Language handling bereits entfernt — umzäunte Code-Blöcke, Inline-Code, HTML-Kommentare, YAML-Frontmatter und Markdown-Link- / Bild-**Ziele** (der sichtbare Link-**Text** ist Prosa und bleibt erhalten) — unter Wiederverwendung jenes Strippings, sodass ein LIX-Wert widerspiegelt, was ein Mensch liest, nicht das Markdown-Gerüst. Code-Identifier und URLs **DÜRFEN NICHT [MUST NOT]** zu `A`, `B` oder `C` beitragen.

### Tokenisierung und Segmentierung

- **MUSS [MUST]** eine **einzige Tokenisierungs-und-Satz-Segmentierungs-Pipeline** pinnen, die für **beide** Sprachen — Englisch und Deutsch — verwendet wird, und sie in den Lauf-Metadaten aufzeichnen (§Reproduzierbarkeit). Ein LIX-Wert ist nur so reproduzierbar und so sprachübergreifend vergleichbar wie der Segmentierer, der `A`, `B` und `C` erzeugt hat; zwei verschiedene Segmentierer auf demselben Text erzeugen verschiedene LIX-Werte, also ist der Segmentierer Teil des Vertrags, nicht eine freie Implementierungswahl.
- **MUSS [MUST]** Sätze an terminaler Interpunktion (`.`, `!`, `?`) und am Doppelpunkt (`:`) segmentieren, wenn dieser einen eigenständigen Hauptsatz einleitet, konsistent mit der kanonischen „Anzahl der Punkte"-Definition von `B`, und dabei falsche Grenzen unterdrücken bei:
  - bekannten **Abkürzungen** (`z. B.`, `d. h.`, `usw.`, `Nr.`, `e.g.`, `i.e.`, `etc.`, `Dr.`),
  - **Dezimal- und Versionszahlen** (`3.14`, `v1.2.0`),
  - **Ordinalzahlen** im Deutschen (`1.`, `2.` gefolgt von einer kleingeschriebenen Fortsetzung).
- **SOLLTE [SHOULD]** einen gepflegten mehrsprachigen Segmentierer (zum Beispiel `syntok` oder `ucto`) einem naiven Split-am-Punkt vorziehen, weil Abkürzungs- und Zahlen-Behandlung `B` und damit `ASL` materiell verändern. Wenn die gewählte Readability-Library nicht intern segmentiert (zum Beispiel verlangt `andreasvc/readability` vor-segmentierte, vor-tokenisierte Eingabe), **MUSS [MUST]** der vorgeschaltete Segmentierer der gepinnte sein und **MUSS [MUST]** aufgezeichnet werden; „die Qualität des Preprocessings beeinflusst die Validität der Ergebnisse" ist eine Eigenschaft der Pipeline, keine Entschuldigung, sie unspezifiziert zu lassen.
- **MUSS [MUST]** byteweise-äquivalentes Stripping und Tokenisierung auf die EN- und DE-Datei desselben Artefakts anwenden, sodass ein berichtetes EN-gegen-DE-LIX-Delta die Prosa widerspiegelt, nicht eine Tokenizer-Asymmetrie.

### Skala-Interpretation

- **MUSS [MUST]** die Interpretation auf Björnssons **fünf kanonischen Referenzpunkten** verankern, behandelt als **Referenzpunkte, nicht als Bandgrenzen**:

  | Referenzpunkt | LIX | Leser-orientierte Bedeutung |
  | --- | --- | --- |
  | Sehr leicht | 20 | Kinderbücher |
  | Leicht | 30 | Belletristik, Boulevardpresse |
  | Mittel | 40 | Normale Zeitung / allgemeine Sachprosa |
  | Schwer | 50 | Fach- / Amtsprosa |
  | Sehr schwer | 60 | Akademische, bürokratische, Dissertations-Prosa |

- **DARF NICHT [MUST NOT]** irgendeine feiner granulierte „Band-Tabelle" (zum Beispiel „Sehr leicht 20–25 / Leicht 30–35 / …") als kanonisch oder als Björnsson zuschreibbar darstellen; solche expliziten Bandgrenzen kursieren weit online, sind aber **nicht** primärquellen-belegt (sie wurden in der Recherche, die diese Spec grundiert, widerlegt). Nur die fünf Referenzpunkte oben sind autoritativ; alle operativen Schwellen sind das eigene Engineering-Judgment dieser Spec (§Zielkorridore), als solches gekennzeichnet.
- **SOLLTE [SHOULD]** die Korpus-Kalibrierung aus der grundierenden Recherche als Plausibilitäts-Anker für die Referenzpunkte lesen (Kindertexte ≈ 22, Nachrichten ≈ 40, Enzyklopädie ≈ 45, Parlaments-Prosa ≈ 47), nicht als zusätzliche Schwellen.

### Sprachübergreifende Kalibrierung

Dieser Abschnitt ist das **Kaveat höchster Priorität** für eine zweisprachige Pipeline.

- **MUSS [MUST]** einen rohen LIX-Wert als **sprachrelativ** behandeln: dieselbe LIX-Zahl bezeichnet **nicht** gleiche Leseschwierigkeit in Deutsch und Englisch. Deutschlands produktive Kompositabildung (Komposita) und allgemein längere Wörter blähen den Langwort-Anteil (`LWP`) auf, selbst wenn die Wörter konkret und leicht verständlich sind — `Vergrößerungsglas` ist ein langes Wort, aber kein schwieriges. Morphologische Länge ist in einer kompositabildenden Sprache nicht dasselbe wie Leseschwierigkeit.
- **MUSS [MUST]** diese Inflation kompensieren, indem deutsche Korridore **um einen festen Offset Δ höher** als englische Korridore gesetzt werden, sodass gleiche *tatsächliche* Schwierigkeit auf einen höheren *rohen* deutschen LIX abbildet. Der Default-Offset ist **Δ = 5 LIX-Punkte** (Engineering-Judgment). Eine Implementierung **MUSS [MUST]** Δ über die sprachspezifische Korridor-Tabelle in §Zielkorridore anwenden statt einen rohen Wert nachträglich anzupassen, sodass der aufgezeichnete LIX-Wert eine getreue Messung bleibt und nur die *Schwelle* sich je Sprache unterscheidet.
- **DARF [MAY]** stattdessen normalisieren, indem **deutsche Wörter vor dem Langwort-Test dekomponiert werden** (`Vergrößerungsglas` wird nur für die Längenzählung in `Vergrößerungs` + `Glas` zerlegt, niemals im gerenderten Text), als fortgeschrittene Alternative zum Offset. Eine Implementierung, die das tut, **MUSS [MUST]** es in den Lauf-Metadaten aufzeichnen, **DARF [MAY]** es **NICHT** mit dem Offset kombinieren (das würde doppelt korrigieren), und **DARF NICHT [MUST NOT]** die gerenderte Prosa verändern. Der Default bleibt der Offset; Dekomposition ist opt-in.
- **MUSS [MUST]** den Wert Δ = 5 als **provisorisches Engineering-Judgment** kennzeichnen; der empirisch kalibrierte Deutsch-gegen-Englisch-Offset ist eine Offene Frage, gegated an akkumulierten zweisprachigen Audit-Daten.

### Zielkorridore

Die Korridore unten sind **Engineering-Judgment**, verankert an den §Skala-Interpretation-Referenzpunkten (40 = mittel, 50 = schwer), abgeglichen mit den bestehenden deutschen LIX-Korridoren aus [`spec/project/lektorat/`](../lektorat/de.md) §D1 und versetzt gemäß §Sprachübergreifende Kalibrierung (Deutsch = Englisch + Δ, Δ = 5). Die Designabsicht der `aim`-Spalte ist **„komfortabel für eine gebildete technische Leserschaft, ohne herablassend simpel zu sein"** — für technische Prosa liegt dieser Zielwert um die mittel-bis-schwer-Referenzpunkte (LIX ≈ 40–55), nicht unten am Kinderbuch-Ende.

- **MUSS [MUST]** Korridore pro `content_mode` und pro Sprache mit drei Schwellen ausweisen — `aim` (der Konvergenz-Zielwert, auf den der Autor hinschreibt), `warn` (ein `warning`-D1-Befund bei Überschreitung) und `crit` (ein `critical`-D1-Befund bei Überschreitung):

  | `content_mode` | EN aim / warn / crit | DE aim / warn / crit |
  | --- | --- | --- |
  | `tutorial`, `how-to`, `troubleshooting` | ≤ 40 / > 45 / > 55 | ≤ 45 / > 50 / > 60 |
  | `explanation`, `reference`, `glossary` | ≤ 50 / > 55 / > 65 | ≤ 55 / > 60 / > 70 |
  | Blog-Post (Peer-Professional) | ≤ 45 / > 50 / > 55 | ≤ 50 / > 55 / > 60 |

- **MUSS [MUST]** die deutschen `warn` / `crit`-Spalten **konsistent mit den bestehenden deutschen LIX-Korridoren aus `lektorat` §D1** halten (Tutorial-Gruppe `> 50 / > 60`; Explanation/Reference/Glossary-Gruppe `> 60 / > 70`); diese Spec übernimmt jene Werte für Deutsch wortgleich und leitet die englischen Spalten als die deutschen minus Δ ab. Wenn `lektorat` §D1 aktualisiert wird, um diese Spec zu referenzieren, ändern sich die deutschen Zahlen nicht.
- **MUSS [MUST]** Seiten, deren `content_mode` `meta` ist, vollständig von der LIX-Bewertung ausnehmen, konsistent mit der Meta-Ausnahme aus `lektorat` §D1; navigatorische Prosa wird nicht an einem Lesbarkeits-Korridor gemessen.
- **MUSS [MUST]** die Blog-Post-Zeile nur für Artefakte im Blog-Post-Scope wählen (ein Konsument, der [`spec/project/blog-author/`](../blog-author/de.md) übernimmt); die Zeile ist so kalibriert, dass ein Post, der den englischen Flesch–Kincaid-7–10-Zielwert aus [`spec/project/post-writing-style/`](../post-writing-style/de.md) trifft, auch innerhalb des LIX-`aim` landet, sodass die beiden Lesbarkeits-Zielwerte gegenseitig konsistent statt konkurrierend bleiben.
- **DARF [MAY]** einem Repository erlauben, einen Korridor pro Datei über denselben `lektorat`-lokalen Konfigurationsmechanismus zu überschreiben, den `lektorat` §D1 bereits definiert (`LIX_warn` / `LIX_crit`-Schlüssel, benannte Begründung, innerhalb ±50 % des Defaults); diese Spec fügt keinen zweiten Override-Mechanismus hinzu.
- **MUSS [MUST]** die Korridorwerte als **provisorisch** kennzeichnen; portfolio-weite Re-Kalibrierung ist eine Offene Frage, gegated an mindestens drei Portfolio-Member-Repositories, die LIX-Audit-Daten beitragen, analog zur Korridor-Kalibrierungs-Offenen-Frage aus `lektorat` §D1.

### Einen LIX-Wert verbessern

LIX hat genau **zwei Hebel**: die mittlere Satzlänge (`ASL`, der `A/B`-Term) und den Langwort-Anteil (`LWP`, der `(C × 100)/A`-Term). Jede bedeutungserhaltende Verbesserung bewegt einen oder beide.

- **MUSS [MUST]** jede Transformation nach dem Hebel klassifizieren, den sie bewegt, und **SOLLTE [SHOULD]** sie in der Prioritätsreihenfolge unten anwenden (höchste Wirkung und niedrigstes Bedeutungs-Risiko zuerst):

  | Priorität | Transformation | Hebel | Anmerkungen |
  | --- | --- | --- | --- |
  | 1 | Einen langen Satz in zwei teilen | `ASL` ↓ | Höchste Wirkung, niedrigstes Risiko; ein Split kann LIX um mehrere Punkte bewegen, ohne ein einziges Wort anzufassen. |
  | 2 | Füllwörter und Redundanz entfernen („um zu" statt „um … zu können", „es sei angemerkt, dass" streichen) | `ASL` ↓ | Verkürzt Sätze und verbessert die Prosa unabhängig. |
  | 3 | Nominalisierungen in Verben wandeln („eine Validierung durchführen" → „validieren") | `ASL` ↓ und `LWP` ↓ | Bewegt beide Hebel; fast immer ein echter Lesbarkeitsgewinn. |
  | 4 | Aktiv statt Passiv bevorzugen | `ASL` ↓ | Verkürzt und klärt meist; konsistent mit den `prose-style`-Voice-Regeln. |
  | 5 | Ein langes Wort durch ein kürzeres exaktes Synonym ersetzen | `LWP` ↓ | Nur wenn das Synonym wirklich genauso präzise ist; niemals Präzision gegen Länge tauschen. |
  | 6 | Ein deutsches Kompositum aufbrechen, wo der Split natürlicher liest | `LWP` ↓ | Nur Deutsch; hohes Bedeutungs-Risiko — siehe Anti-Gaming-Regel. |

- **SOLLTE [SHOULD]** für typische technische Prosa den **`ASL`-Hebel** priorisieren: Satz-Splitting und Füllwort-Entfernung sind der sicherste und zuverlässigste Weg, LIX zu senken und dabei die Lesbarkeit wirklich zu verbessern, während Wort-Ersetzung (der `LWP`-Hebel) das höchste Risiko trägt, Präzision gegen eine niedrigere Zahl zu tauschen. Die relative Größenordnung der beiden Hebel für einen gegebenen Korpus ist eine Offene Frage; die Prioritätsreihenfolge ist risiko-zuerst-Engineering-Judgment, kein gemessenes Wirkungs-Ranking.
- **DARF NICHT [MUST NOT]** einen Edit vornehmen, dessen **einzige** Wirkung ist, die Metrik zu senken, ohne die menschliche Lesbarkeit zu verbessern („Gaming"). Ausdrücklich verboten:
  - einen Satz mitten im Teilsatz zu teilen, wo der Bruch das Verständnis schädigt,
  - einen etablierten deutschen Fachbegriff willkürlich zu dekomponieren, sodass er auf der Seite als zwei Wörter liest (`Pull-Request` wird nicht dadurch besser, dass es bloß zum Senken eines langen Worts zu `Pull Request` wird),
  - einen präzisen Domänenbegriff durch ein kürzeres, vageres Wort zu ersetzen,
  - irgendeinen **geschützten Begriff** (Eigenname, Produktname, technischer Identifier, Befehl oder Begriff aus dem Audience-Artefakt oder der `lektorat`-Protected-Terms-Liste) zu verändern, um `LWP` zu senken.
- **MUSS [MUST]** den LIX-Korridor als der Lesbarkeit dienend behandeln, nicht umgekehrt: wenn der einzige Weg, in den Korridor zu kommen, ein oben verbotener Edit ist, ist das korrekte Ergebnis, **den Befund offen zu lassen und ihn dem Operator vorzulegen**, nicht den Wert zu gamen. Diese Unterordnung hält die Metrik über die iterative Schleife hinweg ehrlich.

### Reproduzierbarkeit

- **MUSS [MUST]** die LIX-Berechnungs-Pipeline in der maschinenlesbaren Ausgabe des Laufs aufzeichnen, sodass ein Wert reproduzierbar und EN/DE-vergleichbar ist. Die Pipeline-Metadaten **MÜSSEN [MUST]** pro Sprache tragen: den Library-`name` und die `version` der Readability-Library, `name` und `version` des Tokenizers/Segmentierers, die `long_word_threshold` (immer `6`) und ob `decompounding` angewandt wurde (Boolean, nur Deutsch). Das erweitert den `pipeline_metadata`-Block, den `lektorat` §Outputs bereits definiert, statt ein paralleles Artefakt einzuführen.
- **MUSS [MUST]** pro Datei mit einem LIX-Befund den berechneten `lix` (Ganzzahl), `asl`, `lwp` sowie die rohen Zählungen `words` (`A`), `sentences` (`B`) und `long_words` (`C`) in der Befund-Evidenz aufzeichnen, sodass der Befund auditierbar ist und den Autor zum dominanten Hebel lenkt.
- **MUSS [MUST]** die Implementierung gegen die **kanonische Formel** validieren, nicht gegen den Dokumentationsstring einer Library: die weit verbreitete `textstat`-Library liefert einen **Docstring, der eine vertauschte, mathematisch falsche Formel angibt** (`A/B + A*100/C`), während ihr ausgeführter Code korrekt ist — ein Implementierer, der den Docstring kopiert, berechnet die falsche Zahl. Ein Konformitätstest **MUSS [MUST]** behaupten, dass ein bekannter Fixture-Text den von Hand berechneten kanonischen LIX ergibt.
- **MUSS [MUST]** dieselbe Library und denselben Tokenizer für Englisch und Deutsch verwenden; zwei verschiedene Implementierungen zu verwenden führt die Unvergleichbarkeit wieder ein, deren Beseitigung der Daseinszweck dieser Spec ist.

### Verhältnis zu anderen Metriken

- **MUSS [MUST]** **LIX als primäre Lesbarkeitsmetrik** für beide Sprachen behandeln, weil sein Buchstaben-zählendes Design (keine Silbenzählung) das ist, was es über EN und DE hinweg übertragbar macht, wo Flesch-Familien-Metriken, da sie auf englische Silben getunt sind, es nicht sind.
- **MUSS [MUST]** FRE und FKGL (Englisch) und WSTF (Deutsch) als **ergänzende, beratende Signale** behandeln: sie dürfen neben LIX berechnet und berichtet werden (sie fangen silbenbasierte Dichte-Effekte, für die LIX blind ist, und sind Autoren vertraut), aber eine Ergänzungs-Metrik-Lesung **DARF NICHT [MUST NOT]** einen LIX-basierten D1-Befund überstimmen, eskalieren oder unterdrücken.
- **DARF NICHT [MUST NOT]** die iterative Verbesserungsschleife an einer Ergänzungs-Metrik gaten; Konvergenz ist gegen den LIX-Korridor definiert (§Iterative Verbesserungsschleife). Eine Ergänzungs-Metrik, die LIX widerspricht, wird als beratender Kontext aufgeführt, nicht als konkurrierender Zielwert.
- **SOLLTE [SHOULD]** anmerken, dass in der grundierenden Recherche keine direkte quantitative LIX-gegen-WSTF- oder LIX-gegen-FKGL-Korrelation etabliert wurde; die Ergänzungs-Metriken zu behalten ist eine begründete Absicherung (Vertrautheit, silbenbasierte Abdeckung), keine evidenz-gestützte Äquivalenz, und ihre fortgesetzte Nutzung ist eine Offene Frage.

### Iterative Verbesserungsschleife

Dieser Abschnitt definiert, wie LIX am autonomen Autor ↔ Lektor-Zyklus teilnimmt, der [`spec/project/lektorat-auto-revise/`](../lektorat-auto-revise/de.md) gehört; er fügt jenem Zyklus LIX-spezifische Eingaben und einen Konvergenz-Zielwert hinzu, ohne dessen Routing, Bound oder Re-Audit-Mechanik neu zu definieren.

- **MUSS [MUST]** den **LIX-Konvergenz-Zielwert** für eine Datei definieren als: der LIX der Datei liegt auf oder unter der `warn`-Schwelle ihres aufgelösten `content_mode`-und-Sprach-Korridors (§Zielkorridore). Eine Datei auf oder unter `aim` ist komfortabel konvergiert; eine Datei zwischen `aim` und `warn` ist akzeptabel; eine Datei über `warn` ist nicht konvergiert.
- **MUSS [MUST]** in das Per-Datei-Briefing, das die Revise-Schleife für einen Autor zusammenstellt, den aktuellen `lix` der Datei, `asl`, `lwp`, den aufgelösten Korridor (`aim` / `warn` / `crit` für `content_mode` und Sprache der Datei) und den **dominanten Hebel** (jenen von `ASL` oder `LWP`, der mehr Abstand über den Korridor beiträgt) aufnehmen, sodass jeder Autor-Durchlauf auf den richtigen Hebel **gerichtet** ist statt blind umzuschreiben.
- **MUSS [MUST]** ein Re-Audit, in dem der LIX einer Datei von über `warn` auf oder unter `warn` rückt, als **Fortschritt** behandeln, und ein Re-Audit, in dem LIX steigt, als **Regression**, was in das bestehende `lektorat-auto-revise`-Re-Audit-Gate einspeist; der Per-Datei-Durchlauf-**Bound** und das Routing (`audience-doc-author` für Dokumentation, `blog-author` für Posts) sind unverändert und gehören jener Spec.
- **MUSS [MUST]** über die bestehenden Bedeutungserhaltungs- und Anti-Gaming-Garantien jeden Autor-Durchlauf zurückweisen, der LIX durch eine verbotene Transformation gesenkt hat (§Einen LIX-Wert verbessern); eine niedrigere Zahl, durch Gaming erlangt, ist **keine** Konvergenz.

## Akzeptanzkriterien

- [ ] Ein Fixture-Text mit von Hand berechneten `A`, `B`, `C` ergibt aus der Implementierung den exakten kanonischen `LIX = A/B + (C × 100)/A`, auf die nächste Ganzzahl gerundet.
- [ ] Ein Wort von genau 6 Buchstaben wird **nicht** als langes Wort gezählt; ein Wort von 7 Buchstaben **wird** es (die `> 6`-Schwelle wird eingehalten).
- [ ] Ein rein numerisches Token (`2026`, `v1.2.0`) wird als Wort, aber **niemals** als langes Wort gezählt.
- [ ] Deutsche `ä ö ü ß` und akzentuierte lateinische Buchstaben werden im Langwort-Längen-Test als Buchstaben gezählt (ein 7-Buchstaben-Wort mit `ü` qualifiziert).
- [ ] Abschließende Interpunktion an einem Token ändert seine Langwort-Klassifikation **nicht** (`Konfiguration,` zählt identisch zu `Konfiguration`).
- [ ] Umzäunte Code-Blöcke, Inline-Code, HTML-Kommentare, YAML-Frontmatter und Markdown-Link/Bild-Ziele tragen **nicht** zu `A`, `B` oder `C` bei; sichtbarer Link-Text schon.
- [ ] Ein abkürzungs-interner Punkt (`z. B.`, `e.g.`) und eine Dezimal-/Versionszahl (`3.14`, `v1.2.0`) erzeugen **keine** falsche Satzgrenze.
- [ ] Dieselbe Library und derselbe Tokenizer/Segmentierer werden für die EN- und DE-Datei eines Artefakts verwendet, und beide werden in den `pipeline_metadata` des Laufs mit Name und Version aufgezeichnet.
- [ ] Die `pipeline_metadata` zeichnen `long_word_threshold: 6` und für Deutsch einen `decompounding`-Boolean auf.
- [ ] Eine deutsche und eine englische Datei gleicher *tatsächlicher* Schwierigkeit werden an Korridoren gemessen, die sich um den Offset Δ unterscheiden (das deutsche `warn`/`crit` übersteigt das englische um 5), gemäß §Zielkorridore.
- [ ] Die deutschen `warn`/`crit`-Korridorwerte stimmen wortgleich mit den bestehenden deutschen LIX-Korridoren aus `lektorat` §D1 überein (Tutorial-Gruppe `> 50 / > 60`; Explanation/Reference/Glossary-Gruppe `> 60 / > 70`).
- [ ] Eine Seite, deren `content_mode` `meta` ist, erzeugt **keinen** LIX-Befund.
- [ ] Ein Blog-Post-Artefakt wird an der Blog-Post-Korridor-Zeile gemessen, und das `aim` jener Zeile enthält den LIX-Wert eines Posts, der den Flesch–Kincaid-7–10-Zielwert aus `post-writing-style` erfüllt.
- [ ] Ein LIX-D1-Befund zeichnet `lix`, `asl`, `lwp` und die rohen `words`/`sentences`/`long_words`-Zählungen in seiner Evidenz auf.
- [ ] Eine auf `textstat` aufbauende Implementierung berechnet die **kanonische** Formel, nicht die vertauschte Formel aus dem `textstat`-Docstring (ein Konformitätstest behauptet den Fixture-Wert).
- [ ] Eine Ergänzungs-Metrik-Lesung (FRE/FKGL/WSTF) überstimmt, eskaliert oder unterdrückt niemals einen LIX-basierten D1-Befund.
- [ ] Das Per-Datei-Briefing, das die Revise-Schleife für einen Autor zusammenstellt, enthält den `lix` der Datei, den aufgelösten Korridor und den dominanten Hebel (`ASL` oder `LWP`).
- [ ] Ein Autor-Durchlauf, der LIX durch Verändern eines geschützten Begriffs, Dekomponieren eines etablierten Fachbegriffs bloß zum Streichen eines langen Worts oder Ersetzen eines präzisen Begriffs durch ein vageres kürzeres senkt, wird **nicht** als konvergiert akzeptiert.
- [ ] Ein LIX-Wert, der von über `warn` auf oder unter `warn` rückt, wird vom Re-Audit-Gate als Fortschritt aufgezeichnet; ein steigender LIX als Regression.

## Offene Fragen

- **Wie lautet der empirisch kalibrierte Deutsch-gegen-Englisch-Offset Δ?** Der Kompositum-Inflationseffekt ist richtungsmäßig etabliert (Deutsch erzielt bei gleicher Schwierigkeit mehrere Punkte mehr), aber die grundierende Recherche lieferte keine kalibrierte Zahl. Δ = 5 ist provisorisches Engineering-Judgment. Revisit, wenn mindestens drei Portfolio-Member-Repositories mit zweisprachigen `docs/en` + `docs/de`-Bäumen LIX-Audit-Daten akkumuliert haben, die strukturell-parallele EN/DE-Seiten paaren, sodass das mittlere EN-gegen-DE-LIX-Delta auf gleich-schwerem Inhalt gemessen werden kann. Bis dahin gilt Δ = 5.
- **Sind die Korridore pro Texttyp für eine technisch-professionelle Leserschaft richtig?** Die grundierende Recherche lieferte Björnssons generische Fünf-Punkte-Skala und Korpus-Mittel (Nachrichten ≈ 40, Enzyklopädie ≈ 45), aber keine texttyp-spezifische Empfehlung für technisch-professionelle Leser. Die Korridore sind an jenen Punkten verankert und mit den bestehenden deutschen Werten aus `lektorat` abgeglichen. Revisit gemeinsam mit der Korridor-Kalibrierungs-Offenen-Frage aus `lektorat` §D1, sobald drei Repos Audit-Daten beitragen.
- **Welcher Hebel bewegt LIX mehr für typische technische Prosa — `ASL` oder `LWP`?** Die Prioritätsreihenfolge in §Einen LIX-Wert verbessern ist risiko-zuerst-Engineering-Judgment, kein gemessenes Wirkungs-Ranking. Revisit, wenn ein Audit-Korpus existiert, der groß genug ist, um das LIX-Delta gegen Per-Edit-Hebel-Attribution zu regressieren.
- **Sollte Dekomposition-vor-Scoring den Offset als deutschen Default ersetzen?** Dekomposition wird als opt-in-Alternative angeboten. Revisit, wenn ein gepflegter deutscher Dekomponierer gegen den Offset am selben zweisprachigen Korpus evaluiert und gezeigt wurde, dass er menschlich beurteilter Schwierigkeit näher folgt.
- **Sollten die Ergänzungs-Metriken (FRE/FKGL/WSTF) zurückgezogen werden, sobald LIX die sprachübergreifende Primärmetrik ist?** Es wurde keine direkte LIX-gegen-WSTF/FKGL-Korrelation etabliert, also werden die Ergänzungs-Metriken als Absicherung behalten. Revisit, wenn akkumulierte Audit-Daten zeigen, ob sie je ein Lesbarkeitsproblem aufdecken, das LIX verfehlte; wenn sie nie nützlich divergieren, zurückziehen, um die Pipeline-Fläche zu reduzieren.

## Quellen

<!-- Autoritative externe Referenzen, gegen die die obigen Anforderungen validiert wurden; verifiziert über einen faktengeprüften Deep-Research-Durchlauf (23 von 25 extrahierten Claims bestätigt, 2 widerlegt). -->

- Björnsson, C. H. (1968). *Läsbarhet.* Stockholm: Liber. — Definiert LIX (`LIX = A/B + (C × 100)/A`), die `> 6`-Buchstaben-Langwort-Schwelle (für maximale Diskriminierung gewählt, S. 217) und die fünf Interpretations-Referenzpunkte (sehr leicht 20 … sehr schwer 60, S. 89).
- Anderson, J. (1981). *Analysing the readability of English and non-English texts in the classroom with Lix.* ERIC ED207022. — Schritt-für-Schritt-LIX-Prozedur; sprachübergreifende Korrelationsstudien (Französisch/Englisch, Deutsch/Englisch, Griechisch/Englisch), die erhaltene relative Schwierigkeits-Rangfolge über übersetzte Paralleltexte zeigen; hält fest, dass sprachspezifische Normen nötig sind und die sprachübergreifende Forschungsbasis vorläufig ist.
- Anderson, J. (1983). *Lix and Rix: Variations on a little-known readability index.* Journal of Reading 26(6), 490–496. — Das Buchstaben-zählende (nicht Silben-zählende) Design, das LIX/RIX für nicht-englische Sprachen geeignet macht.
- *Cross-lingual readability assessment* (2024). arXiv:2404.01196. — Formel-Restatement (`A` = Tokens, `B` = Sätze, `C` = Wörter mit > 6 Buchstaben); das Kompositum-Inflations-Kaveat (ein morphologisch komplexes Kompositum wie *forstørrelsesglass* / deutsch *Vergrößerungsglas* ist lang, aber nicht schwierig); Korpus-Kalibrierung (Kinder ≈ 22, Nachrichten ≈ 40, Enzyklopädie ≈ 45, Parlament ≈ 47).
- `textstat`-Quellcode — [`_lix.py`](https://github.com/textstat/textstat/blob/main/textstat/backend/metrics/_lix.py) und [`_count_long_words.py`](https://github.com/textstat/textstat/blob/main/textstat/backend/counts/_count_long_words.py). — Korrekte ausgeführte Formel (`asl + 100 × long_words / words`, langes Wort = `len(w) > 6`), **aber ein vertauschter, falscher Docstring** (`A/B + A*100/C`): gegen die Formel validieren, nicht gegen den Docstring.
- `andreasvc/readability` — [PyPI](https://pypi.org/project/readability/) / [GitHub](https://github.com/andreasvc/readability). — Berechnet LIX und RIX für Englisch, Deutsch und Niederländisch in einer Library, tokenisiert oder segmentiert aber **nicht** intern; verlangt vor-segmentierte Eingabe, also muss der vorgeschaltete Segmentierer gepinnt werden.
- *Lix (readability test)* — [Wikipedia](https://en.wikipedia.org/wiki/Lix_(readability_test)). — Stellt die Formel und die „Anzahl der Punkte"-Definition von `B` dar (Punkt, Doppelpunkt oder großer Anfangsbuchstabe als Grenze).
- Flesch, R. (1948); Kincaid et al. (1975); Bamberger & Vanecek (1984). — Definitionen der ergänzenden Metriken (FRE, FKGL, WSTF), die gemäß §Verhältnis zu anderen Metriken als beratende Signale behalten werden; konsumiert über [`spec/project/lektorat/`](../lektorat/de.md).
