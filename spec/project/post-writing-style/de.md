# Post-Schreibstil

Status: accepted

## Kontext

Leserschaft: Implementierer der [`blog-author`](../blog-author/de.md)-Skill im `nolte-shared`-Plugin (primär) und menschliche Autoren, die KI-entworfene Blog-Posts in einem Konsumenten-Repository kuratieren, das diese Spec übernimmt (sekundär). Vertrautheit mit [`spec/project/audience-identification/`](../audience-identification/de.md) (das das Audience-Artefakt des Konsumenten erzeugt) und der Schwester-Spec [`post-audience-communication`](../post-audience-communication/de.md) (die entscheidet, **für wen** zu schreiben ist) wird vorausgesetzt; Begriffe aus jenen Specs werden ohne erneute Erklärung verwendet.

Ein Konsument dieser Spec ist ein **zweisprachiges Personal-Blog- oder Technik-Blog-Repository** mit einem EN-kanonischen / DE-übersetzten Post-Paar-Vertrag, einem Static-Site-Renderer (Astro, Hugo, Eleventy, MkDocs im `blog`-Modus oder gleichwertig) und einem Autorenprofil, das zwischen Hand-Schreiben und Kuratieren KI-entworfener Ausgaben wechselt. Der Referenzkonsument ist `nolte/blog`; die Spec ist so formuliert, dass andere Portfolio-Repositories mit derselben Form sie ohne Modifikation übernehmen können (siehe §Konsumenten-Vertrag und §Referenz-Beispiel-Annex).

Diese Spec **erweitert und operationalisiert** die autoreseitigen Stimmen-Regeln des Konsumenten mit forschungsgestützten Schwellenwerten, einem expliziten Verbotsvokabular, Konventionen zur zweisprachigen Typografie und Lifecycle-Gates, gegen die ein Lint oder ein menschlicher Reviewer prüfen kann. Wo die Repository-Regeln des Konsumenten (sein `CLAUDE.md`, sein Style-Guide, sein README) eine kurze Voice-Zeile tragen, ist diese Spec die operative Ebene dahinter.

Stilentscheidungen auf dieser Blog-Klasse haben eine Eigenschaft zweiter Ordnung: weil Posts von einem LLM entworfen werden, ist AI-Tell-Vokabular („delve", „tapestry", „leverage", „robust", „seamless") die dominante Fehlerart, nicht die Formalitäts-Drift typischer Unternehmens-Blogs. Die Spec lehnt sich aus diesem Grund stark in AI-Tell-Unterdrückung—und in „show your work"-Muster, die ein generisches LLM schwer fälschen kann—beides dient unmittelbar einem Konsumenten-Wert von gegründeten, quellenbelegten, projektabgeleiteten Posts.

## Ziele

- Eine einzige Quelle der Wahrheit für **Stimme, Tonalität, Struktur, Formatierung, Lesbarkeit und Typografie** über jedes Post-Paar (EN + DE) etablieren, damit die zweisprachige Oberfläche intern konsistent bleibt und eine `blog-author`-Skill (oder ein menschlicher Kurator) gegen einen stabilen Vertrag schreiben kann.
- **Messbare Schwellenwerte** festlegen (Satzlängen-Durchschnitt, Absatzlänge, Flesch–Kincaid-Grade-Ziel, Aktiv-Anteil-Ziel, Überschriftstiefe), sodass Stil-Konformität reviewfähig ist, nicht Geschmackssache.
- Eine **geschlossene „Verbotswörter"-Liste** in dieser Spec führen, abgeleitet aus dokumentierten AI-Tells, Plain-Language-Forschung und beobachteten Fehlerarten, damit Hinzufügungen und Streichungen auditierbar sind statt pro Post erfunden zu werden.
- **AI-Disclosure-Tonalität** mandatieren—wie ein Post die Tatsache formuliert, KI-entworfen zu sein—separat zur Disclosure-Flag im Frontmatter des Konsumenten, damit textliches und strukturelles Signal aufeinander passen.
- **Regeln zweisprachiger Typografie** kodifizieren (Anführungszeichen, Gedankenstrich, ß / Umlaute, Erhalt technischer Bezeichner), sodass das EN ↔ DE-Paar auf jeder Seite typografisch idiomatisch ist statt eine wörtliche Transliteration.
- **Personal-Blog-scoped** bleiben: jede Anforderung gilt für einen Markdown-Post, den ein Konsument erzeugt, der diese Spec übernimmt. Projekt-READMEs, ADRs, Spec-Dateien und PR-Beschreibungen sind außerhalb des Geltungsbereichs (sie werden von [`spec/project/prose-style/`](../prose-style/de.md) und [`spec/project/lektorat/`](../lektorat/de.md) abgedeckt).

## Nicht-Ziele

- **Welche Themen** ein Post abdecken sollte, **welche Projekte** zu beschreiben oder **wie häufig** zu veröffentlichen ist, definieren—das sind Roadmap- und Sprint-Themen, die [`spec/project/roadmap/`](../roadmap/de.md) und [`spec/project/sprint/`](../sprint/de.md) gehören.
- Die **Audience-Analyse** selbst definieren. Audiences und ihre Kritikalität gehören zum Audience-Artefakt des Konsumenten (per [`spec/project/audience-identification/`](../audience-identification/de.md)). Die Schwester-Spec [`post-audience-communication`](../post-audience-communication/de.md) definiert, **wie diese Audiences in einem einzelnen Post anzusprechen sind**; diese Spec definiert, **wie zu schreiben ist**, unabhängig davon, auf welche Audience ein gegebener Post sich neigt.
- Das **Frontmatter-Schema des Konsumenten** definieren. Frontmatter-Form (Pflichtfelder, Validierung, Typen) wird vom Static-Site-Engine des Konsumenten deklariert (z. B. Astros Zod-Content-Collection-Schema, Hugos Archetypes, Eleventys Data-Cascade) plus dem `CLAUDE.md` des Konsumenten oder gleichwertig. Diese Spec setzt den unter §Konsumenten-Vertrag dokumentierten Vertrag voraus und verweist auf seine Felder mit ihren konventionellen Namen.
- **SEO-Metadaten, Sitemap, OG-Bilder, RSS-Form oder LLM-Crawler-Haltung** definieren. Die dienen einer Crawler-Audience und werden von der Metadaten- oder Robots-Policy-Spec des Konsumenten geregelt, nicht hier.
- **MkDocs- / Docs-Tracks-Specs** ersetzen. Die regeln Docs-Site-Inhalte mit Audience-Tracks; diese Spec regelt das Personal-Blog-Korpus, in dem jeder Post dieselbe Leser-Spur bedient.
- **Review-Workflow / Merge-Gates** definieren. PR-Review gehört zu [`spec/project/pull-request-workflow/`](../pull-request-workflow/de.md), nicht hierher. Diese Spec definiert, wie der Post selbst auszusehen hat, nicht wie er nach `main` gelangt.
- **Lektorats-Mechanik** definieren (Per-Dimension-Befunde, Severity-Klassifikation, JSON-Reportform). Die gehört zu [`spec/project/lektorat/`](../lektorat/de.md); diese Spec definiert, wie ein an den Lektor übergebener Post auszusehen hat, nicht was der Lektor tut.

## Konsumenten-Vertrag

Ein Konsumenten-Repository, das diese Spec übernimmt, **MUSS [MUST]** Folgendes liefern—das sind Vorbedingungen, keine Anforderungen, die diese Spec erfindet:

- Eine **Post-Paar-Lokationskonvention**: eine kanonisch-sprachige Datei und eine Übersetzungsdatei pro Post, die einen stabilen sprachübergreifenden Bindungs-Key teilen. Die Referenzkonvention ist `src/content/posts/{en,de}/<slug>.md` plus ein Frontmatter-Feld `translationKey`; gleichwertige Konventionen in anderen Engines sind akzeptabel.
- Einen **Frontmatter-Vertrag**, der mindestens deklariert: `title`, `pubDate`, `lang` (oder gleichwertiges Sprachetikett), den sprachübergreifenden Bindungs-Key, `tags`, eine Draft-Flag und eine **AI-Disclosure-Flag** (Referenzname `aiGenerated: true`; gleichwertige Namen sind akzeptabel, solange der Vertrag des Konsumenten eindeutig ist).
- Ein **Audience-Artefakt**, erzeugt per [`spec/project/audience-identification/`](../audience-identification/de.md), mit mindestens einer direkten Endleser-Audience und mindestens einer peripheren Audience für namentlich genannte Drittparteien (der Referenzkonsument nennt diese `A`/`B`/`C` für Endleser-Untergruppen und `L` für Drittparteien; gleichwertige Bezeichnungen sind akzeptabel).
- Ein **Build-Kommando**, das das Post-Paar Ende-zu-Ende rendert (Referenzkonvention ist `task build` / `task check` per [`spec/project/quality-gate/`](../quality-gate/de.md); andere Taskfile-Targets oder direkte Aufrufe sind akzeptabel, solange ein einzelnes Kommando kanonisch ist).
- Eine **Slug-Konvention**—ASCII-Kebab-Case, abgeleitet aus dem EN-Titel, nach Veröffentlichung stabil, ≤ 60 Zeichen—deklariert im `CLAUDE.md` des Konsumenten oder gleichwertig.

Wo diese Spec auf einen „Post-Body", ein „Post-Paar", ein „Frontmatter-Feld `aiGenerated`" oder eine „Audience-L-Charakterisierung" verweist, verweist sie auf die Instanz des Konsumenten dieser Konzepte unter dem obigen Vertrag. Der §Referenz-Beispiel-Annex nennt das konkrete Mapping für den `nolte/blog`-Konsumenten; andere Konsumenten tragen einen analogen Annex in der eigenen Repository-Dokumentation.

## Anforderungen

### Person, Voice und Ton

- **MUSS [MUST]** in der ersten Person Singular („ich") schreiben. Plural-„wir" ist nur erlaubt, wenn der Post explizit für eine tatsächlich existierende Mehr-Personen-Kollaboration spricht—niemals als Unternehmens-Plural, der eine Einzel-Stimme maskiert.
- **MUSS [MUST]** den Post auf den vier NN/g-Tonalitätsdimensionen (Humor, Formalität, Respekt, Begeisterung) wie folgt positionieren: ernsthaft mit gelegentlich trockenem Einschlag, lässig, respektvoll, sachlich. Ausbrüche von Begeisterung sind erlaubt, wenn etwas den Autor wirklich überrascht hat; ein anhaltender begeisterter Register ist **DARF NICHT [MUST NOT]**.
- **MUSS [MUST]** als sachkundiger Peer-zu-Peer-Gespräch lesbar sein, nicht als Dokumentation, nicht als Unternehmens-Post, nicht als Tutorial, das mit „In der heutigen schnelllebigen Welt …" beginnt. „Show the thinking, not just the conclusion": wenn eine Entscheidung schwer war, **MUSS [MUST]** der Post benennen, was sie schwer gemacht hat, bevor benannt wird, was gewählt wurde.
- **MUSS [MUST]** in EN-Posts Kontraktionen bevorzugen („it's", „you'll", „don't", „I've"); ausgeschriebene Formen lesen sich als korporativ oder LLM-Default und gelten als Stil-Verstoß. Die DE-Entsprechung verwendet natürliche deutsche Äquivalente—keine erzwungenen Kolloquialismen.
- **MUSS [MUST]** den Leser in einem einzigen, konsistenten informellen Register ansprechen: in EN-Posts durchgängig das `you` der zweiten Person; in DE-Posts durchgängig das informelle `du` (sowie seine Formen `dich` / `dir` / `dein`). **DARF NICHT [MUST NOT]** ins formelle `Sie` wechseln und **DARF NICHT [MUST NOT]** auf das unpersönliche `man` (EN `one`) zurückfallen, wo ein Satz den Leser anspricht—dann zu `du` / `you` umschreiben. Diese Regel betrifft nur, wie der *Leser* angesprochen wird; die Autoren-Stimme in der ersten Person (`ich` / `I`) aus dem ersten Punkt dieses Abschnitts bleibt unberührt.
- **DARF NICHT [MUST NOT]** mit einem Aufhänger eröffnen, der das Thema oder den Leser schmeichelt („In einer Ära raschen Wandels …", „Entwickler überall stehen vor …"). Öffne mit einem konkreten Artefakt (einem Code-Fragment, einem Screenshot, einer einsätzigen Behauptung, einer spezifischen Frage, die der Post beantwortet).
- **SOLLTE [SHOULD]** Humor trocken und selten halten. Selbstironische Bemerkungen auf Kosten des Autors sind in Ordnung; die Behandlung von Scherzen über namentlich genannte Dritte wird ausschließlich von [§Audience-L-Sicherheit](#audience-l-sicherheit) geregelt—dieser Abschnitt wiederholt die Regel nicht.

### Lesbarkeits-Schwellenwerte

- **MUSS [MUST]** die durchschnittliche Satzlänge im Post-Body zwischen **14 und 20 Wörtern** halten (American-Press-Institute-Verständlichkeitsdaten: ≥ 90 % bei 14 Wörtern, scharfer Abfall über 25). Einzelne Sätze **DÜRFEN [MAY]** 30 Wörter überschreiten, wenn ein einzelner langer Satz dem Rhythmus oder der Präzision dient, aber niemals zwei in Folge.
- **MUSS [MUST]** Body-Absätze auf **höchstens 4 Sätze** halten (gov.uk-Forschung: Menschen lesen 20–28 % des Texts auf einer Seite; lange Absätze verstärken Drop-off). Ein-Satz-Absätze sind ausdrücklich erlaubt, wenn sie einen Akzent tragen.
- **MUSS [MUST]** für den EN-Body (Code-Blöcke und Frontmatter ausgenommen) eine Flesch–Kincaid-Grade-Stufe zwischen **7 und 10** anzielen. Posts unter 7 lesen kindlich; Posts über 10 verlieren Leser, die den Post für ein schnelles Portfolio-Signal skimmen.
- **MUSS [MUST]** den **LIX**-Korridor für den Blog-Post-Texttyp aus [`spec/project/readability-lix/`](../readability-lix/de.md) §Zielkorridore auf **beiden** Sprach-Bodys anzielen (EN aim ≤ 45, DE aim ≤ 50; das deutsche aim liegt um den sprachübergreifenden Offset Δ = 5 höher, weil deutsche Kompositabildung den Langwort-Anteil aufbläht). LIX ist das primäre, sprachübergreifende Lesbarkeitsziel — es gibt dem DE-Body eine Lesbarkeitszahl, die er zuvor nicht hatte, und sein Blog-Post-`aim` ist so kalibriert, dass es mit dem EN-Flesch–Kincaid-7–10-Ziel zusammenfällt, sodass die beiden Metriken übereinstimmen statt zu konkurrieren. Flesch–Kincaid bleibt ein ergänzendes EN-Signal.
- **MUSS [MUST]** Aktiv-Voice bevorzugen. Faustregel: wenn das grammatikalische Subjekt eines Passiv-Satzes fehlt oder „vom System / vom Framework / vom Nutzer" lautet, in Aktiv umschreiben. Passiv ist akzeptabel für Sätze, in denen der Akteur wirklich unbekannt ist oder in denen das Objekt das Thema ist und der Akteur beiläufig ist.
- **SOLLTE [SHOULD]** einen gemessenen Aktiv-Anteil von ≥ 70 % über den Post-Body anstreben. Der Anteil ist ein Ziel, kein hartes Gate, weil einige technische Beschreibungen natürlicher im Passiv lesen (z. B. „die Anfrage wird mit HMAC-SHA256 signiert").

### Struktur und Fluss

- **MUSS [MUST]** mit einer Inverted-Pyramid-Eröffnung beginnen: der erste Absatz **MUSS [MUST]** die Behauptung, den Geltungsbereich oder die Frage des Posts in ≤ 80 Wörtern konkret machen, sodass ein F-Pattern-Skimmer entscheiden kann, ob er weiterliest.
- **MUSS [MUST]** eine scannbare Subhead-Hierarchie tragen. Jeder Post länger als 600 Wörter **MUSS [MUST]** mindestens zwei H2-Subheads haben; jeder Abschnitt länger als ~ 400 Wörter **SOLLTE [SHOULD]** mindestens eine H3 tragen.
- **DARF NICHT [MUST NOT]** einen „TL;DR"-Block als Ersatz für eine Inverted-Pyramid-Eröffnung verwenden. Wenn ein TL;DR wirklich die richtige Form ist (z. B. ein langer technischer Post, der ein mehrstufiges Argument darlegt), **DARF [MAY]** er als erster Block unter der H1 erscheinen, **MUSS [MUST]** aber weiterhin als ein Absatz lesbar sein und **DARF NICHT [MUST NOT]** ein Bullet-Dump sein.
- **MUSS [MUST]** „die Arbeit zeigen": wenn der Post ein Ergebnis behauptet (ein Refactor, eine Entscheidung, eine Messung), **MUSS [MUST]** er mindestens eines der folgenden tragen: (a) den Diff, (b) die Befehlsausgabe, (c) den Screenshot oder (d) ein wörtliches Zitat / einen Verweis. Unbelegte Ergebnis-Behauptungen sind ein Verstoß, weil sie die Fehlerart sind, die diese Blog-Klasse explizit ablehnt—per Hard-Rule des Konsumenten „Niemals technische Fakten erfinden".
- **SOLLTE [SHOULD]** mit einer kurzen Coda schließen, die benennt, worüber der Autor unsicher ist, was absichtlich außerhalb des Geltungsbereichs ist oder was ein Folge-Post abdecken würde. Das dient der Future-Self-Knowledge-Base-Audience mehr als technischen Peers oder Portfolio-Reviewern, kostet die anderen aber nichts, weil es kurz ist.

### Überschriften

- **MUSS [MUST]** Sentence-Case für jede Überschrift verwenden (H1 bis H6). Erstes Wort groß, Eigennamen groß, alles andere klein. Das stimmt mit Google Material, Apple HIG und Microsoft Fluent überein.
- **MUSS [MUST]** genau eine H1 pro Post tragen—den Post-Titel—geliefert vom `title`-Frontmatter des Posts über das Layout des Konsumenten. Der Body-Markdown **DARF NICHT [MUST NOT]** eine zusätzliche H1 deklarieren.
- **MUSS [MUST]** Überschriften sequenziell verschachteln. H1 wird von H2 gefolgt (niemals H3). H2 darf von H2 oder H3 gefolgt werden, niemals H4. Stufen-Überspringen nach unten verletzt WCAG 1.3.1 (heading-order). Stufen-Überspringen nach oben (z. B. H3 schließt zurück zu H2) ist erlaubt.
- **MUSS [MUST]** Überschriftstext den Abschnittsinhalt beschreibend halten, nicht niedlich. „Picking a state library" ist eine gültige Überschrift; „The journey begins" ist es nicht.
- **SOLLTE [SHOULD]** Überschriftslänge unter 60 Zeichen halten, sodass sie in der Inhaltsverzeichnis und im OG-Card-Derivat sauber rendert.

### Code, Befehle und andere technische Inhalte

- **MUSS [MUST]** auf jedem umzäunten Code-Block einen Sprach-Identifikator deklarieren. Die akzeptierten Identifikatoren hängen vom Syntax-Highlighter des Konsumenten ab (Shiki, Prism, highlight.js); übliche sind `ts`, `tsx`, `js`, `jsx`, `astro`, `bash`, `zsh`, `json`, `yaml`, `toml`, `html`, `css`, `md`, `mdx`, `diff`, `python`, `go`, `rust`. Für reine Ausgaben (keine Syntax zum Hervorheben) `text` verwenden statt den Identifikator leer zu lassen.
- **MUSS [MUST]** einzelne Code-Zeilen wo vernünftig ≤ 100 Zeichen halten. Längere Zeilen für Lesbarkeit im Post umbrechen oder refactoren, auch wenn die Originalquelle sie länger hat; die ursprüngliche Position in der umgebenden Prosa zitieren.
- **MUSS [MUST]** Code-Blöcke mit je einer Leerzeile vor und nach von umgebender Prosa trennen.
- **MUSS [MUST]** in umgebender Prosa **vor** dem Block beschreiben, was der Code tut (Setup), und **nach** dem Block, wenn die Ausgabe wichtig ist (Interpretation). Code-Blöcke sind nie das ganze Argument; sie stützen es.
- **SOLLTE [SHOULD]** Inline-Code (einzelne Backticks) für kurze Bezeichner, Dateipfade, CLI-Flags und Config-Key-Verweise im Fließtext verwenden. Kursiv-/Fett-Formatierung **DARF NICHT [MUST NOT]** als Ersatz für Code-Formatierung von Bezeichnern verwendet werden.
- **DARF NICHT [MUST NOT]** Screenshots von Code als Ersatz für umzäunte Code-Blöcke verwenden—Screenshots sind nicht durchsuchbar, für Screenreader unzugänglich und brechen Copy-Paste. Screenshots sind nur für UI-Zustände erlaubt, die nicht anders vermittelbar sind (ein Styling-Ergebnis, ein Layout, ein Chart).
- **SOLLTE [SHOULD]** Screenshots mit beschreibendem Alt-Text in der Markdown-Bild-Syntax kennzeichnen. Der Text **DARF NICHT [MUST NOT]** die Bildunterschrift wiederholen oder „Screenshot" lauten—er **MUSS [MUST]** beschreiben, was auf dem Bild zu sehen ist, damit Screenreader-Nutzer die Information erhalten.

### Links

- **MUSS [MUST]** Link-Text das Ziel des Links selbständig beschreiben lassen (WCAG 2.4.4 Link Purpose, Level A). „[the Astro content collection docs]" besteht; „[click here]" oder „[here]" fällt durch.
- **MUSS [MUST]** das Verlinken auf die **Primärquelle** gegenüber einem Aggregator bevorzugen. Den W3C-Draft, das GitHub-Issue, das Originalpapier, das Upstream-README—nicht einen Kommentar oder eine Content-Farm-Zusammenfassung.
- **MUSS [MUST]** absolute URLs für externe Links verwenden. Interne Cross-Post-Links **MÜSSEN [MUST]** die relative Slug-basierte URL verwenden, die der Router des Konsumenten exponiert (kein hartkodiertes `https://…` für eigene Inhalte).
- **SOLLTE [SHOULD]** sparsam verlinken—jeder Link ist ein Kontextwechsel für den Leser. Ein Link verdient seinen Platz durch Hinzugewinn an Präzision (eine Definitions-Referenz, ein Primärquellen-Zitat, ein Tiefen-Escape-Hatch), nicht reflexartig.
- **DARF NICHT [MUST NOT]** externe Links standardmäßig in einem neuen Tab öffnen. Erzwungenes `target="_blank"` verletzt User-Agency-Erwartungen; wenn ein Link wirklich neu öffnen muss (z. B. weil er einen langen Workflow unterbricht), sage es in Prosa.

### AI-Disclosure-Tonalität

- **MUSS [MUST]** die AI-Disclosure-Flag im Frontmatter des Konsumenten (Referenzname `aiGenerated: true`) auf jedem KI-entworfenen Post gesetzt halten; das Entfernen dieser Flag ist per `CLAUDE.md` des Konsumenten verboten und hier als Stil-Invariante wiederholt, weil die **textliche Tonalität** davon abhängt, dass die Flag ehrlich ist. Die Flag zu entfernen und die Tonalität unverändert zu lassen würde Leser und genannte Drittparteien täuschen.
- **DARF NICHT [MUST NOT]** den Post in einer entschuldigenden Rahmung um das KI-Entworfen-Sein wickeln („Das wurde mit Claude geschrieben, bitte sei nachsichtig …"). Direkte Endleser-Audiences erwarten, dass KI-entworfener Inhalt denselben Standard wie handgeschriebener Inhalt erfüllt. Die Disclosure ist strukturell—heute über die AI-Disclosure-Flag im Frontmatter und zusätzlich über ein sichtbares Per-Post-Badge bei Konsumenten, die eines ausliefern. Ein Konsument, der ein sichtbares AI-Disclosure-Badge ausliefert, **MUSS [MUST]** es rendern (Text-Inhalt: ein kurzes wörtliches Label wie „AI"; Position: in oder direkt neben der Post-Meta-Zeile am Kopf des gerenderten Posts, neben dem Veröffentlichungs- und Aktualisierungsdatum; Sichtbarkeit: genau dann angezeigt, wenn die AI-Disclosure-Flag im Frontmatter wahr ist). Das Badge **SOLLTE [SHOULD]** auf eine About-Page-Erklärung des KI-entworfen-menschlich-kuratiert-Workflows verlinken; der Referenzkonsument `nolte/blog` rendert derzeit ein unverlinktes Label (siehe §Referenz-Beispiel-Annex), und ein kleines Follow-up in jenem Konsumenten umschließt den Label-Span mit einem Anchor, um die SOLLTE zu erfüllen.
- **DARF NICHT [MUST NOT]** behaupten, der Post sei handgeschrieben, wenn er KI-entworfen ist, einschließlich indirekter Behauptungen über First-Person-Erinnerungsrahmungen („als ich mich hinsetzte und das schrieb …"), die implizieren, die Tasten seien die des Autors gewesen. Akzeptabel: First-Person-Rahmungen zu Entscheidungen, Meinungen und Verifikationen, die der Autor tatsächlich gemacht hat.
- **MUSS [MUST]** jede konkrete technische Behauptung (ein Projekt tut X, eine Bibliothek verhält sich Y, ein Werkzeug emittiert Z) in einer verifizierbaren Quelle gründen—Quellcode, README, Release-Notes, Befehlsausgabe oder ein explizites Operator-Briefing—gemäß der Hard-Rule des Konsumenten gegen das Erfinden technischer Fakten. Wo die Behauptung die eigene Meinung oder Erfahrung des Autors ist, **SOLLTE [SHOULD]** das mit Formulierungen wie „Ich fand, dass …", „in meiner Nutzung von X …" signalisiert werden, nicht als externer Fakt behauptet.
- **SOLLTE [SHOULD]** die KI-entworfen-menschlich-kuratiert-Rahmung als Arbeitsmethode positionieren, nicht als Neuheit. Der Blog als Ganzes erklärt den Workflow über seine About-Seite (oder gleichwertige Disclosure-Fläche); einzelne Posts müssen ihn nicht neu erklären.

### Zweisprachige Typografie

- **MUSS [MUST]** jeden **technischen Bezeichner** (Funktionsname, Dateipfad, CLI-Flag, Paketname, Env-Var, Branch-Name, Error-String, Frontmatter-Key) zwischen EN und DE unverändert erhalten. Übersetzung operiert ausschließlich auf natürlicher Prosa.
- **MUSS [MUST]** gerade ASCII-Doppelanführungszeichen `"…"` in **EN-Posts** verwenden (die Render-Konvention ist Klartext-ASCII, passend zur Typografie-Regel des Konsumenten). Einfache Anführungszeichen `'…'` für Verschachtelungen oder Kontraktionen.
- **MUSS [MUST]** deutsche Anführungszeichen `„…"` in **DE-Posts** verwenden (neun-unten-Öffner, sechs-oben-Schließer, nach Duden). Guillemets `»…«` sind eine akzeptable Alternative für eine stilistische Ausnahme (visuell abgesetzte Block-Zitate), **DÜRFEN NICHT [MUST NOT]** aber mit `„…"` im selben Post gemischt werden.
- **MUSS [MUST]** den Gedankenstrich mit umgebenden Spatien—wie hier—in **beiden EN und DE** verwenden (passt zu Dudens „Gedankenstrich mit Spatien"-Konvention). Der Halbgeviertstrich `–` ist für numerische Bereiche reserviert (`Seiten 12–15`, `2020–2024`); niemals als Gedanken-Pausen-Trenner verwenden.
- **MUSS [MUST]** in DE-Posts korrekte deutsche Diakritika verwenden: `ä` `ö` `ü` `ß`. ASCII-Ersatzformen (`ae`, `oe`, `ue`, `ss`) sind im Post-Body **DÜRFEN NICHT [MUST NOT]**. Slug-Felder **MÜSSEN [MUST]** den EN-Slug behalten (per Slug-Regel des Konsumenten), damit URLs ASCII bleiben, unabhängig von der Body-Sprache.
- **DARF NICHT [MUST NOT]** ein EN-Idiom („low-hanging fruit", „back-of-the-envelope", „the elephant in the room") wörtlich auf DE wiedergeben; der Übersetzer wählt ein gleichwertiges deutsches Idiom oder formuliert den Satz um. Die umgekehrte Richtung ist symmetrisch: ein seltenes DE-Idiom auf der DE-Seite wird auf der EN-Seite umgeschrieben statt wörtlich übersetzt.
- **DARF NICHT [MUST NOT]** einen **Calque** erzeugen: einen DE-Satz, dessen Struktur das EN Wort-für-Wort spiegelt, selbst wenn jedes einzelne Wort korrekt ist (zum Beispiel „Was die Kosten kaufen, ist Eigentum." für „What the costs buy is ownership."). Den Gedanken neu ausdrücken, wie ein deutscher Autor ihn von Grund auf formulieren würde; das Erkennungs-Gegenstück ist die D6-Dimension in [`spec/project/lektorat/`](../lektorat/de.md).
- **MUSS [MUST]** einem entlehnten Term das **Genus und die Flexion der Zielsprache** geben („die Bridge", „der Hub", „das Repository"), niemals das aus der Ausgangssprache übernommene Genus.
- **SOLLTE [SHOULD]** so übersetzen, dass der Post lesbar ist, als wäre er ursprünglich in der Zielsprache geschrieben—Satzrhythmus, Absatz-Takte und kulturelle Verweise angepasst, nicht nur Vokabular ersetzt.
- **MUSS [MUST]** die **sprachübergreifende Bindungs-Invariante** wahren: die EN-Datei und die DE-Datei teilen einen sprachübergreifenden Bindungs-Key (`translationKey` oder Äquivalent) und einen Dateinamens-Slug, gemäß Konsumenten-Vertrag. Stil-Verstöße auf einer Seite, die von der Sprache abhängen (z. B. eine DE-spezifische `„`-Platzierung), **DÜRFEN NICHT [MUST NOT]** als Edits auf die andere Seite übertragen werden.

### Verbotswörter und -phrasen

Dies ist die **geschlossene Liste** von Wörtern und Phrasen, die **DÜRFEN NICHT [MUST NOT]** im Post-Body ohne expliziten Override erscheinen. Inline-Code, direkte Zitate und Eigennamen-Produktnamen (z. B. eine Bibliothek, die tatsächlich `Seamless.js` heißt) sind ausgenommen; alles andere ist im Scope.

#### Hype-Wörter

- `leverage` (verwende „use")
- `delve` (verwende „go into", „look at", „dig into")
- `robust` (verwende eine konkrete Eigenschaft—„handles invalid input without crashing", „tested across X cases")
- `seamless` (lösche oder ersetze durch das, was tatsächlich passiert: „no manual step", „single command")

#### AI-Tell-Ergänzungen (forschungsabgeleitet; mehrere Quellen unter §Referenzen zitiert)

- `utilize` (verwende „use")
- `harness` (verwende „use" oder „tap")
- `streamline` (verwende eine konkrete Beschreibung—„skips the dry-run step", „halves the round-trips")
- `underscore` (verwende „highlights", „shows" oder forme zu einem Substantiv um)
- `pivotal` (verwende „central" oder „important")
- `cutting-edge` (lösche; oder nenne die spezifische Version / Fähigkeit)
- `innovative` (lösche; beschreibe die Neuheit konkret)
- `tapestry`, `realm`, `landscape`, `synergy`, `testament`, `underpinnings` (lösche; formuliere den Satz um)
- `It's worth noting that …`, `It is important to note that …`, `In conclusion`, `In summary` (lösche den Wrapper; behalte den eigentlichen Punkt)
- `In today's fast-paced …`, `In an era of …`, `As we navigate the …` (lösche; öffne mit der konkreten Behauptung)
- `Whether you're a … or a …` (drop den audience-schmeichelnden Wrapper)

#### Corporate-Speak / Sales-Register

- `synergies`, `holistic`, `best-in-class`, `world-class`, `industry-leading`, `enterprise-grade`, `mission-critical`, `next-gen`
- `unlocks`, `empowers`, `accelerates`, `transforms`, `revolutionises`, `disrupts` (als transitive Verben über Technologie)

#### LLM-Betonungs-Tics

- Sätze, die mit „**It's** [adjective] **that** …" oder „**It is** [adjective] **to** …" beginnen—umformen zu einer direkten Behauptung.
- Sätze, die mit „… and that's a **good thing** / **bad thing**." enden—umformen zur spezifischen Begründung.

#### Override-Verfahren

- Ein spezifisches Wort auf der geschlossenen Liste **DARF [MAY]** in einem einzelnen Post beibehalten werden, wenn ein dokumentierter Grund gilt (wörtliches Zitat, namentliches Produkt, ironische Nutzung klar als solche gerahmt). Der Post-Body **MUSS [MUST]** den Override in umgebender Prosa sichtbar machen („… die Doku nennt das eine ‚seamless' Integration, was …") statt die Liste still zu verletzen.

#### Listen-Pflege

Die obige Liste ist die autoritative Inventur der Spec. Änderungen daran sind keine Per-Post-Ereignisse; sie sind Spec-Level-Änderungen, geregelt durch die unten stehenden Regeln.

- **MUSS [MUST]** für jede **Hinzufügung** zu einer Unterliste (Hype-Wörter, AI-Tell-Ergänzungen, Corporate-Speak, LLM-Betonungs-Tics) ein Quellenzitat im Spec-Diff tragen. Akzeptable Quellen sind dokumentierte AI-Tell-Kataloge, Plain-Language-Style-Guides oder ein dokumentierter Vorfall in einem Konsumenten-Repo, in dem das Wort eine bekannte Fehlerart erzeugte; das Zitat gehört in die Commit-Message, die die Hinzufügung einführt, nicht zwingend in den Spec-Body.
- **MUSS [MUST]** für jede **Streichung** aus einer Unterliste eine Ein-Zeilen-Begründung im Spec-Diff tragen (z. B. „Wort in alltäglich-neutralen Gebrauch übergegangen; ab 2026-Qx von der Liste genommen").
- **MUSS [MUST]** die gesamte Liste bei jedem Claude-Modellfamilien-Übergang (z. B. Claude 4.x → 5.x) re-reviewen. Der Modellfamilien-Übergang ist das Erfassungs-Ereignis für einen Ad-hoc-Befund unter [`spec/project/continuous-improvement/`](../continuous-improvement/de.md): das Re-Review wird dort als nachverfolgter Remediation-Eintrag eröffnet, als Commit mit dem Tag `forbidden-list re-review` gelandet (die Form, nach der `a-20` in `git log` greppt) und sein Abschluss in den Risk- / Rollout-Notes des auslösenden PR gemäß jener Spec festgehalten. Das Re-Review **DARF NICHT [MUST NOT]** still übergangen werden.
- **SOLLTE [SHOULD]** die Liste implizit über die `Status:`-Zeile der Spec plus Git-History versionieren—kein `version:`-Feld wird ergänzt; der Audit-Trail lebt in `git log -- spec/project/post-writing-style/`.

### Edit-Pass (vor Veröffentlichung)

Die Anforderungen in diesem Abschnitt regeln die **Vor-Veröffentlichungs-Pflichten des Autors** an einer Arbeitskopie des Posts. Eine nachgelagerte Lint-Skill oder ein automatisierter Reviewer **DARF [MAY]** die Items mit korrespondierendem Akzeptanzkriterium prüfen (siehe §Akzeptanzkriterien—`a-2`, `a-3`, `a-4`, `a-9`, `a-14`, `a-15`, `a-16`); die übrigen Items in diesem Abschnitt sind menschliche Autorenpflichten, die kein aktuelles Werkzeug verifizieren kann und die der §Nicht-Ziele-Ausschluss „Review-Workflow / Merge-Gates" nicht zu einem CI-Gate erhebt.

- **MUSS [MUST]** den Post vor Veröffentlichung laut lesen—oder von einer TTS laut lesen lassen. Sätze, über die der Autor stolpert, sind zu lang oder enthalten versteckte Passiv-Konstruktionen; das Laut-Lesen fängt beides.
- **MUSS [MUST]** jede konkrete Behauptung über ein Projekt / eine Bibliothek / ein Werkzeug gegen die zitierte Quelle verifizieren (per Hard-Rule des Konsumenten). Den zitierten Befehl erneut ausführen, die zitierte Datei am zitierten Stand öffnen oder das README wörtlich zitieren sind die kanonischen Verifikationen.
- **MUSS [MUST]** das Build-Kommando des Konsumenten (Referenz: `task build` / `task check`) vor Veröffentlichung ausführen. Ein Post, der nicht baut, geht nicht raus.
- **SOLLTE [SHOULD]** einen Absatz löschen, über den der Autor zögert—die meisten Posts, die nach dieser Löschung veröffentlicht werden, lesen sich straffer als die Alternative. (Strunk-/Zinsser-Prinzip, pro Post angewandt.)
- **SOLLTE [SHOULD]** sowohl die EN- als auch die DE-Datei unter dem Dev-Server des Konsumenten gegen den Live-Sprachschalter rendern lassen, bevor gemerged wird. Ein sprachübergreifender Bindungs-Mismatch ist ein stiller Bruch, den der Build nicht in jedem Fall fängt.

### Audience-L-Sicherheit

Der Referenzidentifikator `L` (im Audience-Artefakt von `nolte/blog` verwendet) benennt die periphere Audience von Menschen und Projekten, die namentlich in einem Post charakterisiert werden. Konsumenten, die andere Identifikator-Buchstaben verwenden, interpretieren diesen Abschnitt gegen die entsprechende periphere-Drittpartei-Audience ihres Audience-Artefakts.

- **MUSS [MUST]** jede Charakterisierung eines Drittprojekts / einer Drittperson / eines Drittwerkzeugs in einem Primärquellen-Zitat gründen (dem README des Projekts, einer öffentlichen Aussage eines Maintainers, einer Code-Referenz, einer Release-Note). Kritik ist erlaubt; verleumderische Behauptungen über unverifiziertes Verhalten sind es nicht.
- **MUSS [MUST]** einen Korrekturweg anbieten. Der Default-Korrekturweg ist implizit (das Quell-Repo ist öffentlich, die E-Mail steht auf der About-Seite); wenn das Audience-Artefakt des Konsumenten die offene Frage eines dedizierten Kontakt- / Korrekturkanals löst, **MUSS [MUST]** diese Klausel aktualisiert werden, um den spezifischen Kanal zu benennen.
- **DARF NICHT [MUST NOT]** private Kommunikationen (Slack-DMs, private E-Mails, geschlossene Issue-Threads) ohne explizite Einwilligung der Quelle zitieren.
- **SOLLTE [SHOULD]** den bevorzugten Namen und die bevorzugte Großschreibung des benannten Projekts verwenden (z. B. `npm` nicht `NPM`, `Astro` nicht `astro`). Für Personen die Form, die sie öffentlich verwenden.

## Akzeptanzkriterien

Ein Post erfüllt diese Spec, wenn **alle** der Per-Post-Kriterien unten gelten. Die Spec-Level-Kriterien (`a-18` und folgende) werden gegen das Spec-Korpus und seine Git-History verifiziert, nicht pro Post; sie werden geprüft, wenn die Spec selbst sich ändert. Jedes Kriterium ist so formuliert, dass ein Reviewer (der Autor, die `blog-author`-Skill oder eine zukünftige Lint-Skill) es ohne Ambiguität als erledigt / nicht erledigt markieren kann.

### Per-Post-Kriterien

- [ ] **a-1** Der Body öffnet mit einem Inverted-Pyramid-Lead-Absatz (≤ 80 Wörter), der die Behauptung, den Geltungsbereich oder die Frage des Posts benennt.
- [ ] **a-2** Die durchschnittliche Satzlänge im Body fällt zwischen 14 und 20 Wörter; keine zwei aufeinanderfolgenden Sätze überschreiten 30 Wörter.
- [ ] **a-3** Kein Body-Absatz überschreitet 4 Sätze (Bullet-Listen ausgenommen, die für diese Regel keine Absätze sind).
- [ ] **a-4** Flesch–Kincaid-Grade-Stufe auf dem EN-Body (Code-Blöcke ausgenommen) fällt zwischen 7 und 10. **Vorläufig**: bis ein `textstat`-oder-Äquivalent-Lint-Hook ausgeliefert wird (siehe §Offene Fragen), ist die Prüfung Reviewer-Urteil, und die Schwelle 7–10 selbst unterliegt einer Rekalibrierung nach den ersten 10 EN-Posts in einem gegebenen Konsumenten-Repo. Flesch–Kincaid ist ein ergänzendes EN-Signal; das sprachübergreifende Lesbarkeitsziel ist LIX (a-4a).
- [ ] **a-4a** LIX auf **beiden** Sprach-Bodys (Code-Blöcke ausgenommen) liegt im Blog-Post-Korridor aus [`spec/project/readability-lix/`](../readability-lix/de.md) §Zielkorridore (EN aim ≤ 45 / warn 50; DE aim ≤ 50 / warn 55). Das ersetzt die frühere DE-Lesbarkeits-Ausnahme — der DE-Body trägt jetzt das primäre sprachübergreifende Lesbarkeitsziel. **Vorläufig**: der Korridor und der Offset Δ = 5 unterliegen einer Rekalibrierung gemäß `readability-lix` §Offene Fragen.
- [ ] **a-5** Jeder umzäunte Code-Block deklariert einen unterstützten Sprach-Identifikator.
- [ ] **a-6** Jeder Link-Text beschreibt sein Ziel selbständig (besteht WCAG 2.4.4).
- [ ] **a-7** Überschriften sind durchgängig Sentence-Case; der Body deklariert keine zweite H1; Überschrifts-Stufen werden nicht nach unten übersprungen.
- [ ] **a-8** Kein Wort und keine Phrase aus der geschlossenen Verbotsliste erscheint im Body ohne dokumentierten Override in umgebender Prosa.
- [ ] **a-9** Jede konkrete technische Behauptung über ein benanntes Projekt / eine Bibliothek / ein Werkzeug zitiert eine verifizierbare Quelle.
- [ ] **a-10** Die AI-Disclosure-Flag des Konsumenten (Referenz: `aiGenerated: true`) ist im Frontmatter vorhanden; der Body widerspricht ihrem Wahrheitswert nicht über „ich habe mich hingesetzt und das selbst geschrieben"-Rahmungen.
- [ ] **a-11** Die EN-Datei und die DE-Datei teilen denselben sprachübergreifenden Bindungs-Key (`translationKey` oder Äquivalent) und denselben Dateinamens-Slug, und beide rendern unter dem Dev-Server des Konsumenten.
- [ ] **a-12** DE-Post verwendet `„…"`-Anführungszeichen, Gedankenstrich mit umgebenden Spatien und `ä`/`ö`/`ü`/`ß` (keine ASCII-Ersatzformen). EN-Post verwendet ASCII `"…"` und Gedankenstrich mit umgebenden Spatien.
- [ ] **a-13** Jede Charakterisierung einer benannten Drittpartei (periphere Audience für benannte Drittparteien, Referenzidentifikator `L`) trägt ein Primärquellen-Zitat; keine Privat-Kommunikationszitate erscheinen ohne explizite Einwilligung.
- [ ] **a-14** Das Build-Kommando des Konsumenten (Referenz: `task build`) ist auf dem Working-Tree, der beide Dateien enthält, grün.
- [ ] **a-15** Der EN-Body verwendet Kontraktionen (`it's`, `you'll`, `don't`, `I've`, `we're`) im Fließtext; ausgeschriebene Formen erscheinen nur in direkten Zitaten, Code-Blöcken oder dort, wo eine Kontraktion echte Mehrdeutigkeit erzeugen würde.
- [ ] **a-16** Wenn der Post eine nicht-offensichtliche Entscheidung beschreibt, benennt der Body, was die Entscheidung schwer gemacht hat, **bevor** die getroffene Wahl benannt wird (die „show the thinking"-MUSS in §Person, Voice und Ton).
- [ ] **a-17** Ein Konsument, der ein sichtbares AI-Disclosure-Badge ausliefert, rendert es auf der Post-Seite, wenn `aiGenerated` wahr ist, mit Badge-Text und Position gemäß §AI-Disclosure-Tonalität. Konsumenten, die kein Badge ausliefern, erfüllen §AI-Disclosure-Tonalität über die durch `a-10` abgedeckte `aiGenerated: true`-Frontmatter-Flag.
- [ ] **a-17a** Der Leser wird in jedem Body durchgängig in einem konsistenten informellen Register angesprochen — EN `you` der zweiten Person, DE informelles `du` — ohne formelles `Sie` und ohne unpersönliches `man` / `one` in einem Satz, der den Leser anspricht (§Person, Voice und Ton). Die Autoren-Stimme in der ersten Person (`ich` / `I`) ist ausgenommen.
- [ ] **a-17b** Der DE-Body enthält keinen Calque (einen Satz, der das EN Wort-für-Wort spiegelt) und keinen Lehnwort-Genus-Fehler; EN-Idiome werden idiomatisch wiedergegeben, nicht wörtlich (§Zweisprachige Typografie). Das Erkennungs-Gegenstück ist die D6-Dimension in [`spec/project/lektorat/`](../lektorat/de.md).

### Spec-Level-Kriterien

Verifiziert gegen `git log -- spec/project/post-writing-style/`, nicht gegen einzelne Posts. Diese Kriterien gehören zum Unterabschnitt §Verbotswörter und -phrasen—§Listen-Pflege.

- [ ] **a-18** Jede Hinzufügung zu einer Unterliste unter §Verbotswörter und -phrasen trägt ein Quellenzitat im Spec-Diff oder in der Commit-Message, die die Hinzufügung einführt.
- [ ] **a-19** Jede Streichung aus einer Unterliste unter §Verbotswörter und -phrasen trägt eine Ein-Zeilen-Begründung im Spec-Diff oder in der Commit-Message, die die Streichung einführt.
- [ ] **a-20** Ein Re-Review-Eintrag für die §Verbotswörter-Liste existiert bei jedem Claude-Modellfamilien-Übergang (z. B. 4.x → 5.x), erkennbar in `git log` als entweder Commit-Message-Tag (z. B. `forbidden-list re-review`) oder dedizierter Continuous-Improvement-Eintrag.

## Referenz-Beispiel-Annex

Der Referenzkonsument ist das `nolte/blog`-Repository (ein zweisprachiger Astro-Static-Blog). Es bildet die §Konsumenten-Vertrag-Konzepte wie folgt ab:

- Post-Paar-Lokation: `src/content/posts/en/<slug>.md` und `src/content/posts/de/<slug>.md`.
- Sprachübergreifender Bindungs-Key: Frontmatter-Feld `translationKey`.
- AI-Disclosure-Flag: Frontmatter-Feld `aiGenerated: true`.
- AI-Disclosure-Badge: bernsteinfarbener „AI"-Span in der Post-Meta-Zeile, gerendert von `src/layouts/PostLayout.astro`, wenn `aiGenerated` wahr ist; unverlinkt mit Stand 2026-05.
- Frontmatter-Schema-Quelle: Astro-Zod-Schema unter `src/content.config.ts`.
- Audience-Artefakt: `AUDIENCES.md` im Repository-Root, mit Identifikatoren `A` (technische Leser), `B` (Portfolio-Reviewer), `C` (Autor als Future-Self), `L` (benannte Drittparteien), `M` (Suchmaschinen).
- Autorenseitiges Vertragsdokument: `CLAUDE.md` im Repository-Root.
- Build-Kommando: `task build` (voll) / `task check` (schnellere Variante).

Andere Konsumenten, die diese Spec übernehmen, tragen einen analogen Annex in der eigenen Repository-Dokumentation und bilden ihre engine-spezifischen Namen auf den oben formulierten abstrakten Vertrag ab. Ein Konsument **DARF [MAY]** seinen Annex inline in sein `CLAUDE.md` einbetten statt als separate Datei.

## Offene Fragen

_Alle zuvor zurückgestellten offenen Fragen wurden am 2026-06-06 entschieden: jeder vorläufige Default ist nun die geltende Regel. Die Einzelentscheidungen und Begründungen sind in der Git-Historie erhalten (Entscheidungslog, 2026-06-06). Die frühere Frage zum DE-seitigen Lesbarkeitsziel ist zusätzlich auf der Implementierungsseite durch das sprachübergreifende LIX-Ziel (`a-4a`) gemäß [`spec/project/readability-lix/`](../readability-lix/de.md) aufgelöst._

## Referenzen

Stimme und Tonalität:

- [The Four Dimensions of Tone of Voice—NN/G](https://www.nngroup.com/articles/tone-of-voice-dimensions/)
- [Voice and tone—Google developer documentation style guide](https://developers.google.com/style/tone)
- [Active voice—Google developer documentation style guide](https://developers.google.com/style/voice)
- [Voice and Tone—Mailchimp Content Style Guide](https://styleguide.mailchimp.com/voice-and-tone/)
- [Top 10 tips for Microsoft style and voice—Microsoft Style Guide](https://learn.microsoft.com/en-us/style-guide/top-10-tips-style-voice)
- [Microsoft's brand voice; above all, simple and human—Microsoft Style Guide](https://learn.microsoft.com/en-us/style-guide/brand-voice-above-all-simple-human)

Plain Language und Lesbarkeit:

- [Federal Plain Language Guidelines (plainlanguage.gov)](https://www.plainlanguage.gov/howto/guidelines/FederalPLGuidelines/FederalPLGuidelines.pdf)
- [Top 10 Principles for Plain Language—National Archives](https://www.archives.gov/open/plain-writing/10-principles.html)
- [Flesch–Kincaid readability tests—Wikipedia](https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests)
- [Sentence length—Readability guidelines](http://readabilityguidelines.wikidot.com/sentence-length)
- [Improve the readability of your technical documentation with Flesch (ClickHelp)](https://clickhelp.com/clickhelp-technical-writing-blog/improve-the-readability-of-your-technical-documentation-with-flesch/)

Struktur und Fluss:

- [Inverted Pyramid: Writing for Comprehension—NN/G](https://www.nngroup.com/articles/inverted-pyramid/)
- [Content design: writing for GOV.UK](https://www.gov.uk/guidance/content-design/writing-for-gov-uk)
- [How to Prevent F-Pattern Scanning—Mailchimp](https://mailchimp.com/resources/f-pattern-scanning/)

Überschriften und Barrierefreiheit:

- [Title Case vs. Sentence Case—Grammarly](https://www.grammarly.com/blog/sentences/title-case-sentence-case/)
- [G141: Organizing a page using headings—W3C WCAG Techniques](https://www.w3.org/TR/WCAG20-TECHS/G141.html)
- [Understanding Success Criterion 2.4.4: Link Purpose (In Context)—W3C WAI](https://www.w3.org/WAI/WCAG21/Understanding/link-purpose-in-context.html)
- [Headings—W3C Web Accessibility Initiative tutorial](https://www.w3.org/WAI/tutorials/page-structure/headings/)

Code und Markdown-Konventionen:

- [Markdown best practices—Microsoft Learn (PowerShell contributor guide)](https://learn.microsoft.com/en-us/powershell/scripting/community/contributing/general-markdown)
- [Fenced Code Blocks—Python-Markdown documentation](https://python-markdown.github.io/extensions/fenced_code_blocks/)

AI-Tell und Verbotswörter:

- [Don't Write Like AI: Red Flag Words—Blake Stockton](https://www.blakestockton.com/red-flag-words/)
- ["I'd like to delve into how AI is fostering changes in writing"—Mere Sophistry](https://meresophistry.substack.com/p/id-like-to-delve-into-how-ai-is-fostering)
- [How to Spot AI Writing Tells—Olivia Cal](https://www.oliviacal.com/post/ai-writing-tells)

AI-Inhalts-Disclosure-Normen:

- [BBC sets protocol for generative AI content—Broadcast](https://www.broadcastnow.co.uk/production-and-post/bbc-sets-protocol-for-generative-ai-content/5200816.article)
- [7 things you need to know about the BBC's AI guidance—Broadcast](https://www.broadcastnow.co.uk/production-and-post/7-things-you-need-to-know-about-the-bbcs-ai-guidance/5200901.article)
- [Key AI concepts to grasp in a new hybrid journalism era—Reuters Institute](https://reutersinstitute.politics.ox.ac.uk/key-ai-concepts-grasp-new-hybrid-journalism-era-transparency-autonomy-and-authorship)

Deutsche Typografie:

- [Duden—Anführungszeichen](https://www.duden.de/sprachwissen/rechtschreibregeln/anfuehrungszeichen)
- [Wikipedia:Typografie—Anführungszeichen und Gedankenstrich](https://de.wikipedia.org/wiki/Wikipedia:Typografie)

„Show your work"-Beispiel-Blogs:

- [Kalzumeus—Patrick McKenzie's archive](https://www.kalzumeus.com/archive/)
- [Julia Evans—jvns.ca](https://jvns.ca/)
