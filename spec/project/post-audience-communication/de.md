# Audience-Kommunikation für Posts

Status: draft

## Kontext

Leserschaft: Implementierer der [`blog-author`](../blog-author/de.md)-Skill im `nolte-shared`-Plugin (primär), menschliche Autoren, die KI-entworfene Blog-Posts kuratieren (sekundär), und nachgelagerte Review-Skills, die einen Post vor Veröffentlichung gegen diese Spec prüfen.

Diese Spec ist der Begleiter zu [`post-writing-style`](../post-writing-style/de.md). Wo `post-writing-style` dem Autor sagt, **wie geschrieben wird** (Stimme, Lesbarkeit, Typografie, Verbotswörter), sagt diese Spec dem Autor, **für wen geschrieben wird, und wie ein einzelner Post so geformt wird, dass der richtige Leser zuerst bedient wird, ohne die anderen zu vergraulen**.

Das Konsumenten-Repository—ein zweisprachiges Personal-Blog- oder Technik-Blog-Repository, das den [`blog-author`](../blog-author/de.md)-Vertrag übernimmt—liefert ein Audience-Artefakt, erzeugt per [`spec/project/audience-identification/`](../audience-identification/de.md). Dieses Artefakt listet die Audiences des Konsumenten und rangiert ihre Kritikalität. Diese Spec verwendet eine **abstrakte Audience-Form** (beschrieben in §Konsumenten-Audience-Vertrag) und verweist auf spezifische Audience-Identifikatoren nur dann, wenn sie im Konsumenten-Artefakt existieren. Der Referenzkonsument ist `nolte/blog`; der §Referenz-Beispiel-Annex nennt seine konkreten Identifikatoren (`A`/`B`/`C`/`L`/`M`).

Das schwierige Problem, das diese Spec löst: **ein einzelner Blog-Post kann nicht für jede direkte Endleser-Untergruppe maximal optimieren.** Ein technischer Peer-Leser will Tiefe; ein Portfolio-Reviewer will ein Sechs-Sekunden-Signal; ein Future-Self-Knowledge-Base-Leser will rohe Arbeitsnotizen, die die anderen beiden zu rau fänden. Bestehende Forschung der technischen Kommunikation (Carliner, Lannon, gov.uk Content Design, NN/g Progressive Disclosure) konvergiert auf eine einzige Antwort: geschichtetes Schreiben mit einer pro Post deklarierten Primär-Audience. Diese Antwort ist es, was diese Spec kodifiziert.

## Ziele

- Mandatieren, dass jeder Post **genau eine Primär-Audience deklariert**, damit der Autor und die `blog-author`-Skill ein unzweideutiges Ziel haben, wenn Lede, Tiefe und Schluss geformt werden.
- Eine **Pro-Audience-Form-Adressierungsrubrik** bereitstellen—für jede der drei Referenz-Endleser-Formen (technischer Peer-Leser, Portfolio-Reviewer, Future-Self-Knowledge-Base-Leser)—die benennt, wofür zu optimieren, was zu vermeiden, das Lede-Muster, und die Konfliktlösungs-Haltung, wenn Audiences uneins sind.
- **Mehraudience-Schichtungs-Regeln** bereitstellen, sodass ein primär für eine Audience geschriebener Post die anderen weiterhin über Progressive Disclosure bedient (skimbare Lede → Body-Tiefe → optionale Drawer / Fußnoten / verlinkter Anhang).
- **Behandlung benannter Drittparteien** kodifizieren (die periphere Audience „benannte Drittparteien", Referenzidentifikator `L`): wie sie fair zu charakterisieren sind, wann Einwilligung erforderlich ist, was der Korrekturpfad ist.
- **Zweisprachige Audience-Symmetrie** fixieren: das EN- und DE-Post-Paar bedient dieselbe Primär-Audience in beiden Sprachen; die Wahl wechselt nicht zwischen den Seiten.
- **Personal-Blog-scoped** bleiben: die Spec regelt den Body eines Markdown-Posts, den ein Konsument erzeugt, der diese Spec übernimmt. Header-Metadaten, Sitemap, OG-Card-Inhalt und RSS-Form sind außerhalb des Geltungsbereichs (sie bedienen die Suchmaschinen-/Crawler-Audience und werden anderswo geregelt).

## Nicht-Ziele

- Das **Audience-Artefakt** selbst oder die Audience-Identifikationsmethodik definieren—das lebt im `AUDIENCES.md` (oder Äquivalent) des Konsumenten und in [`spec/project/audience-identification/`](../audience-identification/de.md).
- [`post-writing-style`](../post-writing-style/de.md) ersetzen. Die Writing-Style-Spec definiert Stimme, Lesbarkeit, Typografie und Verbotsvokabular, unabhängig von der Audience. Diese Spec definiert Audience-Targeting darüber hinaus; die beiden sind so entworfen, dass sie sich komponieren.
- **Per-Seite-Docs-Tracks-Frontmatter** definieren. Post-Frontmatter trägt nicht das `track:`-Feld der Docs-Audience-Tracks, das die MkDocs-Seite verwendet, weil jeder Blog-Post dieselbe Endleser-Spur bedient. Das Audience-Signal in dieser Spec lebt in einem separaten Frontmatter-Feld (siehe §Primär-Audience-Deklaration).
- **Inhaltsauswahl** definieren. Welche Projekte, Entscheidungen oder Erfahrungen es in einen Post schaffen, ist ein Roadmap-/Sprint-Thema, kein Audience-Kommunikations-Thema. Sobald ein Thema gewählt ist, definiert diese Spec, für wen der Post ist.
- **SEO / Metadaten für die Suchmaschinen-/Crawler-Audience** definieren. Die Crawler-zugewandte Oberfläche ist Strukturdaten-Form, keine Body-Prosa; sie gehört in eine separate Metadaten- oder Robots-Policy-Spec.
- **Journalistische Redaktionsstandards** ersetzen. Der Autor ist kein Journalist; die Spec leiht BBC-/Reuters-/AP-Normen, die für Drittparteien-Darstellung gelten, mandatiert aber nicht die volle redaktionelle Governance, die diese Organisationen tragen.
- Das **Audience-Signal auf der Seite rendern** (ein sichtbares „für Entwickler" / „für Portfolio-Leser"-Badge nahe des Post-Headers). Das ist ein konsumentenseitiges Präsentations-Thema auf der Docs-/UX-Roadmap des Konsumenten, und der Default der Spec ist, das Signal nur intern (Frontmatter) zu halten—sichtbare Badges könnten defensiv gelesen werden. Das spiegelt, wie [`blog-author`](../blog-author/de.md) das Rendern und die Stil-Policy von Hero-Bildern an ein konsumentenseitiges Roadmap-Item delegiert, statt es als Spec-Level-Offene-Frage zu tragen.

## Konsumenten-Audience-Vertrag

Diese Spec ist gegen eine **abstrakte Audience-Form** geschrieben, nicht gegen spezifische Identifikator-Buchstaben. Ein Konsumenten-Repository, das diese Spec übernimmt, **MUSS [MUST]** ein Audience-Artefakt (per [`spec/project/audience-identification/`](../audience-identification/de.md)) liefern, das die folgende Form erfüllt:

- Mindestens drei **direkte Endleser-Untergruppen**, die auf die drei Rubriken in §Pro-Audience-Adressierungsrubriken abbilden:
  - ein **technischer Peer-Leser** (der Referenzkonsument nennt das `A`): ein Entwickler, der über Suche, RSS oder den Link eines Peers vorbeischaut und auf technische Genauigkeit und „Show your work"-Tiefe liest.
  - ein **Portfolio-Reviewer** (Referenz: `B`): ein Recruiter oder Hiring Manager, der aus CV / LinkedIn kommt und auf ein schnelles Signal von Projektarbeit, Arbeitsstil und Aktualität liest. Sechs-bis-sieben-Sekunden initialer Scan.
  - ein **Future-Self-Knowledge-Base-Leser** (Referenz: `C`): der Autor, der seine eigenen Posts re-liest, um eine Entscheidung, eine Methode oder Kontext wiederzugewinnen. Toleriert rauere Entwürfe; braucht langlebige, eigenständig-kohärente Erklärung.
- Mindestens eine **periphere Audience für benannte Drittparteien** (Referenz: `L`): Menschen, Projekte, Bibliotheken und Werkzeuge, die namentlich in Posts charakterisiert werden. Lese-Fairness-Regeln gelten für sie unabhängig von der Primär-Audience.
- Optional eine **periphere Suchmaschinen-/Crawler-Audience** (Referenz: `M`): außerhalb des Geltungsbereichs für Body-Prosa.

Ein Konsument **DARF [MAY]** zusätzliche Untergruppen ausliefern (eine vierte direkte Audience, eine Sponsor-Audience usw.); diese werden adressiert, indem demselben Rubrik-Muster wie der nächstgelegenen Referenzform gefolgt wird, dokumentiert im eigenen Annex des Konsumenten.

Wo diese Spec bloße Identifikator-Buchstaben (`A`, `B`, `C`, `L`, `M`) verwendet—um die Rubriken lesbar zu halten —, verweisen diese Buchstaben auf die Identifikatoren des **Referenzkonsumenten**. Ein Konsument mit anderen Identifikatoren interpretiert jeden solchen Verweis gegen sein eigenes Audience-Artefakt über das Mapping in §Referenz-Beispiel-Annex.

## Anforderungen

### Primär-Audience-Deklaration

- **MUSS [MUST]** für jeden Post genau eine **Primär-Audience** über ein Frontmatter-Feld `primaryAudience: <Identifikator>` deklarieren. Nur Identifikatoren für direkte Endleser-Untergruppen (Referenz: `A`, `B`, `C`) sind gültige Werte für dieses Feld; der Identifikator für benannte Drittparteien (Referenz: `L`) ist nie eine Primär-Audience (er ist eine Beschränkung, kein Ziel—siehe §Behandlung benannter Drittparteien) und der Suchmaschinen-/Crawler-Identifikator (Referenz: `M`) ist außerhalb des Geltungsbereichs per §Nicht-Ziele.
- **MUSS [MUST]** eine Sekundär-Audience-Liste über ein Frontmatter-Feld `secondaryAudiences: [<Identifikator>, …]` deklarieren. Die Liste **DARF NICHT [MUST NOT]** den Wert enthalten, der in `primaryAudience` verwendet wird; sie **DARF [MAY]** leer sein (`[]`), wenn der Post absichtlich eng ist.
- **DARF NICHT [MUST NOT]** `primaryAudience` nach Veröffentlichung rotieren, um einen unterperformenden Post neu auszurichten. Das Frontmatter-Feld ist ein Write-once-Vertrag, der die Form des Posts verankert; ein Post, der eine andere Audience bedienen will, ist ein neuer Post unter einem neuen Slug.
- **SOLLTE [SHOULD]** eine **ausgewogene Verteilung** über die drei Referenz-Endleser-Untergruppen des Konsumenten anstreben, gemessen an einem rollenden Fünf-Post-Fenster. Die Referenzverteilung für `nolte/blog` ist **A: rund 50 %, B: rund 20 %, C: rund 30 %**; andere Konsumenten fixieren ihr eigenes Ziel basierend auf der Kritikalitätsrangliste ihres Audience-Artefakts und Traffic-Daten. Die Aufteilung ist ein Startpunkt, gegen tatsächliche Traffic-/Referrer-Daten zu kalibrieren; Abweichungen sind in jedem einzelnen Post in Ordnung und signalisieren eine Kalibrierungs-Frage nur über einen 10-Post-Horizont.
- **DARF [MAY]** einen Post `primaryAudience: <Future-Self-Knowledge-Base-Identifikator>` markieren, auch wenn der Inhalt langlebig und teilbar ist; das Feld deklariert, für welchen Leser die Form des Posts optimiert wurde, nicht wer ihn lesen darf.

### Pro-Audience-Adressierungsrubriken

Die drei Rubriken unten entsprechen den drei Referenz-Endleser-Untergruppen in §Konsumenten-Audience-Vertrag. Das Audience-Artefakt eines Konsumenten kann andere Identifikator-Buchstaben verwenden; in dem Fall hängt die Rubrik per Audience-Form an (die Rubrik unten für „technische Peer-Leser" hängt an, welchen Identifikator der Konsument auch immer dieser Form zuweist).

#### Technischer-Peer-Leser-Rubrik (Referenzidentifikator `A`)

Ein technischer Peer-Leser kam über Suche, einen RSS-Reader oder einen Link eines anderen Entwicklers. Die erste Frage des Lesers ist „weiß diese Person, wovon sie spricht", beantwortet im ersten Absatz. Die zweite Frage des Lesers ist „kann ich die hier gezeigte Arbeit kopieren / anpassen / verifizieren", beantwortet im Body.

- **MUSS [MUST]** mit dem konkreten Artefakt führen—der Problemstellung, dem fehlschlagenden Fall, dem tatsächlichen Code unter Diskussion, dem Versions-Pin. Die ersten 80 Wörter eines `A`-Posts **DÜRFEN NICHT [MUST NOT]** Hintergrundkontext sein; sie **MÜSSEN [MUST]** die technische Behauptung benennen.
- **MUSS [MUST]** das Arbeits-Artefakt wörtlich tragen: den Diff, die Befehlsausgabe, die Config, den fehlschlagenden Test, den Screenshot des UI-Zustands—was auch immer der Leser für die Reproduktion bräuchte. Das Artefakt ist keine Illustration des Posts; der Post ist die Erklärung um das Artefakt herum.
- **MUSS [MUST]** Versionen jedes diskutierten Werkzeugs / Bibliothek / Frameworks benennen (`Astro 5.x`, `Tailwind 4.0`, `Claude Opus 4.7`, `Python 3.12`), damit der Leser die Behauptung zeitlich verankern und entscheiden kann, ob sie noch auf sein Setup zutrifft.
- **DARF NICHT [MUST NOT]** das Vokabular des Portfolio-Reviewers voraussetzen. „MVP", „ROI", „Stakeholder" und „Value-Delivery" sind nicht im Register; wenn eine geschäftliche Rahmung wirklich wichtig ist, in technischen Begriffen benennen („wir wollten, dass das in CI läuft, ohne für einen Hosted-Runner zu zahlen").
- **DARF NICHT [MUST NOT]** unterzeigen, weil „der Leser weiß das schon". Im Zweifel auf die Primärquelle verlinken statt den Verweis zu überspringen; ein `A`-Leser nutzt die Links, ein `B`-Leser überspringt sie, keiner zahlt einen Preis.
- **SOLLTE [SHOULD]** mit einem „außerhalb des Geltungsbereichs / offene Fragen / was ich als Nächstes tun würde"-Abschnitt schließen. Das dient `A`s Neugier (andere Wege durchs Problem) und dem Future-Self-Leser (`C`) gleichzeitig, ohne Kosten für `B`, der bereits weg ist.
- **SOLLTE [SHOULD]** das Erfahrungsniveau früh signalisieren. „Ich hatte X vor diesem Projekt nicht angefasst" setzt die Erwartungen des Lesers so genau wie „Ich habe X seit fünf Jahren in Produktion ausgeliefert"; beides ist ehrlich und beides nützt `A`.

#### Portfolio-Reviewer-Rubrik (Referenzidentifikator `B`)

Ein Portfolio-Reviewer ist ein Recruiter, Hiring Manager oder jemand, der das Portfolio des Autors aus einem nicht-tief-technischen Winkel bewertet. Eye-Tracking-Studien legen den initialen Scan auf sechs bis sieben Sekunden; der Post muss **was gebaut wurde, welche Rolle der Autor spielte, und wie aktuell die Arbeit ist** in diesem Fenster signalisieren, sonst geht der Leser.

- **MUSS [MUST]** die ersten 80 Wörter (das Inverted-Pyramid-Lead, das von [`post-writing-style`](../post-writing-style/de.md) gefordert ist) als Sechs-Sekunden-Signal arbeiten lassen: es **MUSS [MUST]** (a) das Projekt oder Thema, (b) was getan wurde, und (c) die First-Person-Rolle des Autors benennen. „Ich habe die Deploy-Pipeline meiner Home-Assistant-Integration umgeschrieben, sodass sie bei jedem Push grün ausliefert" besteht; „Heute erkunden wir CI/CD" fällt durch.
- **MUSS [MUST]** früh einen Ein-Zeilen-Satz „was das in der Praxis bedeutet" tragen—was sich geändert hat, was ausgeliefert wurde, was gelernt wurde—in Klarsprache formuliert. Ein `B`-Leser parst nicht `kubectl rollout restart`, liest aber „Ich habe die Deploy-Zeit von 12 Minuten auf 90 Sekunden gekürzt".
- **MUSS [MUST]** den Post visuell scannbar halten: mindestens zwei H2-Überschriften in jedem Post über 600 Wörter, die erste H2 innerhalb des ersten Viewports an Text (≈ 400 Wörter in einer Desktop-Lesespalte).
- **DARF NICHT [MUST NOT]** vom Leser verlangen, die Code-Blöcke zu lesen. Ein `B`-Leser überspringt umzäunten Code. Die umgebende Prosa **MUSS [MUST]** die Botschaft tragen; der Code stützt sie, ist aber nicht die Botschaft.
- **DARF NICHT [MUST NOT]** mit einer Jargon-Barriere öffnen („In diesem Post geht es um k8s-Operatoren auf CRDs …"). Der Jargon darf im Body kommen, sobald die breitere Behauptung gelandet ist.
- **SOLLTE [SHOULD]** das Portfolio-Projekt explizit nennen und auf sein Repository verlinken (oder auf die `/projects/<slug>`-Route des Konsumenten für Portfolio-Einträge), damit der `B`-Leser mit einem Klick vom Post zur Projektseite wechseln kann.
- **SOLLTE [SHOULD]** ein Datums-Signal jenseits des Frontmatter-`pubDate` einschließen—„im Mai 2026" im Lede, oder ein Tag wie „laufende Arbeit" / „in Produktion ausgeliefert"—weil `B`-Leser, die einen Post 2027 lesen, wissen wollen, dass er noch aktuell ist.

#### Future-Self-Knowledge-Base-Rubrik (Referenzidentifikator `C`)

Ein Future-Self-Leser ist der Autor, der seine eigene Arbeit Monate oder Jahre später re-liest, um eine Entscheidung, eine Methode oder ein Stück Kontext wiederzugewinnen, das aus der Erinnerung gefallen ist. Die Erwartung des Lesers ist Langlebigkeit und Eigenständigkeit: der Post sollte kalt aufgenommen werden können, ohne das Gespräch, das ihn erzeugte.

- **MUSS [MUST]** das **Warum** jeder Entscheidung festhalten, die der Post beschreibt, nicht nur das **Was**. „Ich nahm `bun` statt `node`" ohne „weil der Build 4× schneller war und `node_modules` eine konstante Quelle für Merge-Konflikte gewesen war" ist für das Future-Self nutzlos.
- **MUSS [MUST]** die **erwogenen und verworfenen Alternativen** benennen, wenn der Post eine nicht-offensichtliche Wahl beschreibt. Die Liste von „was ich nicht gewählt habe" ist für das Future-Self mindestens so wertvoll wie die endgültige Wahl—das sind die Sackgassen, die der Autor nicht neu erkunden muss.
- **MUSS [MUST]** ein **Glossar oder eine „was diese Begriffe in diesem Post bedeuten"-Notiz** tragen, wenn der Post sich auf Terminologie verlässt, die sich bis zum Re-Lesen verschoben haben kann. Den Begriff einmal mit einer kurzen Parenthese oder einem Link zum Original-RFC / Projekt-README markieren; Future-Self erinnert sich nicht zwingend an die Bedeutung von „Agent" oder „Skill" in 2026, wenn 2028 ist.
- **DARF [MAY]** rauer sein als ein `A`-targeted oder `B`-targeted Post—abgebrochene Gedanken in Klammern, halb fertige Sätze stehen gelassen, „TODO: später drauf zurückkommen"-Marker—vorausgesetzt, der Post ist ehrlich als `primaryAudience: C` getaggt. Die raue Form ist das Feature; sie auf `A`-Niveau zu schleifen würde die Eigenschaft löschen, die `C`-Posts im Digital-Garden-Sinn nützlich macht.
- **MUSS [MUST]** trotzdem die **verifizierbare-Behauptungen-Regel der Writing-Style-Spec** erfüllen: Rauheit ist in der Form erlaubt, nicht in der sachlichen Genauigkeit. Ein `C`-Post, der sagt „Bibliothek X tut Y" ohne Quelle, ist derselbe Verstoß wie ein `A`-Post, der das tut.
- **SOLLTE [SHOULD]** aggressiv zu anderen Posts zu verwandten Themen cross-verlinkt werden. `C`-Posts ziehen ihren Wert aus dem verlinkten Graphen; ein isolierter `C`-Post ist ein weniger nützlicher `C`-Post.

### Behandlung benannter Drittparteien (Referenzidentifikator `L`)

Die Audience benannter Drittparteien deckt jeden ab, den der Post namentlich charakterisiert: Maintainer diskutierter Bibliotheken, Projekte, die der Autor kritisiert, zitierte Personen, verglichene Werkzeuge. Die Fairness-Regeln unten sind nicht verhandelbar, unabhängig davon, welche Primär-Audience der Post bedient.

- **MUSS [MUST]** jede Charakterisierung einer benannten Drittpartei in einer Primärquelle gründen—dem README des Projekts, der öffentlichen Aussage eines Maintainers, einer Release-Note, einer Code-Referenz an einem fixierten Stand. Kritik ist erlaubt; unverifizierte sachliche Behauptungen über Verhalten sind es nicht.
- **MUSS [MUST]** den bevorzugten Namen und die bevorzugte Großschreibung der Drittpartei verwenden, wenn bekannt (z. B. `npm` nicht `NPM`, `Astro` nicht `astro`). Für Personen die öffentlich verwendete Form.
- **DARF NICHT [MUST NOT]** private Kommunikationen (DMs, private E-Mails, geschlossene Issue-Threads, internes Slack) ohne explizite Einwilligung der Quelle zitieren.
- **DARF NICHT [MUST NOT]** die Absicht einer Drittpartei charakterisieren („sie taten dies, weil sie Nutzer einsperren wollten"), ohne eine die Charakterisierung stützende öffentliche Aussage; Absichts-Behauptungen sind die mit dem höchsten Verleumdungsrisiko in beiden Jurisdiktionen (EN-sprachig und DE-sprachig).
- **SOLLTE [SHOULD]** Korrekturanfragen über die heute verfügbaren impliziten Kanäle leiten—öffentliche Quell-Repository-Issues und die E-Mail auf der About-Seite des Konsumenten—und die implizit-Kanal-Form ist der konforme Baseline für den aktuellen Spec-Stand. Wenn das Audience-Artefakt des Konsumenten die offene Frage eines dedizierten Kontakt-/Korrekturkanals löst, wird dieses **SOLLTE [SHOULD]** zu einem **MUSS [MUST]** befördert, das den deklarierten Kanal **MUSS [MUST]** benennen; die Beförderung wird als Spec-Revision festgehalten, nicht als stille Bearbeitung. Die Absicht dieses Konditionals ist, die Regel heute unzweideutig konform zu halten statt unbestimmt.
- **SOLLTE [SHOULD]** eine Ein-Zeilen-Zuschreibung tragen, wenn der Post sich stark an die Arbeit oder Rahmung eines anderen lehnt („die Rahmung von X als Y stammt aus <Name>s Post unter <URL>"). Das dient `L` (die zitierte Partei fühlt sich gesehen statt vereinnahmt) und `A` (der Leser lernt, wo weiterzuverfolgen).
- **DARF [MAY]** eine spezifische Person in Lob nennen; **SOLLTE NICHT [SHOULD NOT]** eine spezifische Person in Kritik nennen, wenn die Kritik auf Projekt- oder Codebase-Ebene liegt—den Projektnamen nennen, auf das öffentliche Artefakt verlinken und den genannten Maintainer den Post finden lassen, wenn er möchte. Projekt-Level-Kritik ist leichter fair zu halten als Personen-Level-Kritik.

### Mehraudience-Schichtung

Ein einzelner Post bedient mehrere Audiences nur dann, wenn seine **Form** jeder Audience erlaubt, die nötige Tiefe selbst zu wählen. Die geforderten Schichten unten leiten sich aus NN/g Progressive Disclosure und der Tradition „writing for multiple audiences" in der technischen Kommunikation ab.

- **MUSS [MUST]** ein **Inverted-Pyramid-Lede** tragen (gefordert von [`post-writing-style`](../post-writing-style/de.md)), das die Behauptung des Posts jeder Audience in ≤ 80 Wörtern liefert. Das Lede ist die gemeinsame Oberfläche; es **DARF NICHT [MUST NOT]** von einer der direkten Endleser-Untergruppen verlangen, weiterzulesen, um die Schlagzeile zu extrahieren.
- **MUSS [MUST]** einen **Body tragen, der die Primär-Audience auf Tiefe bedient**. Das Prosa-Register, die Code-Block-Dichte, die Begriffstiefe und die Link-Dichte des Bodys werden auf `primaryAudience` abgestimmt. Quer-verwiesenes Material, das eine Sekundär-Audience interessieren würde, gehört in Escape-Hatch-Links, nicht in den Hauptfluss.
- **SOLLTE [SHOULD]** eine **Escape-Hatch-Schicht** für die wahrscheinlichste Sekundär-Audience tragen. Übliche Muster:
  - Für einen `primaryAudience: A`-Post mit sekundär `B`: ein Ein-Zeilen-Satz „was das für Nicht-Ingenieure bedeutet" früh im Body, und ein Link aus dem Lede heraus auf `/projects/<slug>` (oder die Portfolio-Eintrags-Route des Konsumenten).
  - Für einen `primaryAudience: B`-Post mit sekundär `A`: ein Abschnitt „Details und Fallstricke" gegen Ende mit dem tieferen technischen Material, geschrieben so, dass ein `B`-Leser, der bereits weg ist, nichts Wichtiges verpasst.
  - Für einen `primaryAudience: C`-Post mit sekundär `A`: ein Absatz „falls du zufällig hier gelandet bist, hier ist der Kontext" oben im Post.
- **DARF [MAY]** einen **einklappbaren Drawer** (`<details>…</details>`) verwenden, um einen langen Code-Block oder ein Seiten-Argument zu verbergen, das die Primär-Audience nicht braucht, die Sekundär-Audience aber vielleicht. Drawer **DÜRFEN NICHT [MUST NOT]** verwendet werden, um Inhalt zu vergraben, den die Primär-Audience braucht; das ist „Arbeit verstecken" und verletzt die Spec.
- **DARF NICHT [MUST NOT]** über drei Tiefen hinaus schichten (Lede, Body, Escape-Hatch). Das Hinzufügen einer vierten Schicht („… und wenn du wirklich tief gehen willst …") signalisiert, dass der Post in zwei Posts aufgeteilt werden sollte.

### Diátaxis-Positionierung

Das Diátaxis-Framework partitioniert Dokumentation in Tutorial, How-to, Reference und Explanation. Personal-Blog-Posts in einem Konsumenten dieser Spec sitzen in zwei dieser vier Quadranten und **bleiben explizit fern** der anderen zwei.

- **MUSS [MUST]** jeden Post als **Explanation**, **How-to** oder eine Mischung der zwei positionieren:
  - *Explanation*—der Post erklärt, warum etwas so ist, wie es ist, welcher Trade-off gewählt wurde, was der Autor gelernt hat. Bildet sauber auf `primaryAudience: A` oder `primaryAudience: C` ab.
  - *How-to*—der Post führt durch die Lösung eines spezifischen Problems mit einem Arbeits-Artefakt. Bildet sauber auf `primaryAudience: A` ab; selten `primaryAudience: B`.
- **DARF NICHT [MUST NOT]** einen Post als **Tutorial** im Diátaxis-Sinn strukturieren (eine Lehrreise durch ein Anfänger-Curriculum). Der Blog ist kein Kurs; Tutorial-Inhalt gehört in die Upstream-Projekt-Dokumentation, nicht hierher. Ein Post, der ein Tutorial wäre, sollte entweder eine Explanation dessen sein, was der Autor durch die Bearbeitung des Tutorials gelernt hat, oder ein How-to, das einen spezifischen Haken adressiert.
- **DARF NICHT [MUST NOT]** einen Post als reine **Reference** strukturieren (eine enumerierte, vollständige API- oder Schema-Beschreibung). Reference gehört in die Quellcode-Dokumentation oder eine dedizierte Docs-Site. Ein Post, der Reference-Inhalt wäre, sollte geteilt werden: das Reference-Material lebt, wo es hingehört; der Post erklärt das Warum oder führt durch einen Use-Case.
Die Diátaxis-Haltung ist implizit im Lede („so habe ich X zum Funktionieren gebracht" → How-to; „so habe ich X über Y gewählt" → Explanation) und **DARF [MAY]** in umgebender Prosa explizit ausgesprochen werden, wenn das den Post schärft; ein dediziertes Frontmatter-Feld ist absichtlich **nicht** erforderlich (siehe §Offene Fragen für die aufgeschobene Lint-freundliche Variante). Diese Leitlinie ist Reviewer-Meta und ist keine pro Post prüfbare Regel—kein Akzeptanzkriterium zielt darauf.

### Konfliktlösung zwischen Audiences

Wenn die Audiences inkompatible Dinge wollen—`A` will mehr Tiefe, `B` will Knappheit, `C` will rohe Notizen—folgt der Post den unten stehenden Regeln in der Reihenfolge.

- **MUSS [MUST]** zugunsten der deklarierten `primaryAudience` lösen. Der ganze Sinn der Frontmatter-Deklaration ist, dass der Trade-off im Voraus gemacht wurde; der Post verhandelt ihn nicht Absatz für Absatz.
- **MUSS [MUST]** niemals **gegen** die Erwartungen der Benannte-Drittparteien-Audience lösen (Referenz: `L`). Sie ist keine Primär-Audience, ist aber eine **unverletzliche Beschränkung**: ein Post darf zu dicht für `B` oder zu spärlich für `C` sein, aber er darf **niemals** eine benannte Drittpartei unfair charakterisieren, um `A`s Appetit auf scharfe Kritik zu bedienen.
- **SOLLTE [SHOULD]** Sekundär-Audience-Züge in Escape-Hatch-Links auflösen statt in Inline-Anpassungen. Ein `primaryAudience: A`-Post, der mitten drin in `B`-freundliche Business-Rahmung abdriftet, verliert `A`s Vertrauen, ohne `B` zu bedienen; der richtige Zug ist ein einzelner `B`-targeted Satz oben und ein Link aus unten heraus, nicht ein mittlerer Absatz, der weder noch bedient.
- **DARF [MAY]** ein einzelnes zugrunde liegendes Thema in zwei Posts aufteilen, jeder mit eigener `primaryAudience`, wenn ein Post nicht beide Audiences bedienen kann, ohne beide zu kompromittieren. Die zwei Posts cross-verlinken sich, teilen Tags und dürfen ein `portfolioProject` teilen. Aufteilen ist die kanonische Antwort auf das wiederkehrende „dieser Post will zwei Posts sein"-Gefühl.

### Zweisprachige Audience-Symmetrie

- **MUSS [MUST]** `primaryAudience` zwischen der EN-Datei und der DE-Datei eines Post-Paars identisch halten. Ein Post ist „für `A`" in beiden Sprachen oder „für `C`" in beiden Sprachen; das Frontmatter-Feld unterscheidet sich nicht über die sprachübergreifende Bindung.
- **MUSS [MUST]** `secondaryAudiences` zwischen EN und DE aus demselben Grund identisch halten.
- **MUSS [MUST]** Audience-spezifische Rahmungen idiomatisch übersetzen. Ein `B`-targeted Lede, das ein Arbeitsmarkt-Signal nennt („Ich habe das zwischen Aufträgen ausgeliefert"), übersetzt idiomatisch zu einer DE-Formulierung, die dasselbe für-Recruiter-lesbare Signal trägt, nicht eine wörtliche Wiedergabe.
- **DARF [MAY]** Verweise lokalisieren, die wirklich zwischen EN- und DE-sprachigen Audiences unterscheiden (z. B. ein juristisches Zitat), wenn die Lokalisierung ehrlich ist und die zugrunde liegende Behauptung unverändert. Re-Übersetzung **DARF NICHT [MUST NOT]** die Substanz des Posts ändern—nur seine Oberfläche.
- **DARF NICHT [MUST NOT]** das Audience-Ziel eines Posts mitten in der Übersetzung kippen, um eine unausgewogene Korpus-Verteilung „zu reparieren". Korpus-Level-Rebalancing geschieht auf der Nächster-Post-Ebene, nicht durch nachträgliches Umschreiben eines bestehenden Paars.

## Akzeptanzkriterien

Ein Post erfüllt diese Spec, wenn **alle** der folgenden gelten. Die Kriterien sind so formuliert, dass ein Reviewer (der Autor, die `blog-author`-Skill oder eine zukünftige Lint-Skill) jedes ohne Ambiguität als erledigt / nicht erledigt markieren kann.

**Enforcement-Status.** Kriterien `a-1` und `a-2` sind Build-erzwungen: Der Referenzkonsument deklariert `primaryAudience` und `secondaryAudiences` in seinem Static-Site-Content-Schema (`src/content.config.ts` von `nolte/blog`), sodass ein Post, der eines der Felder weglässt oder falsch typisiert, den Build fehlschlagen lässt. Das Schema eines Konsumenten **SOLLTE [SHOULD]** eine fehlende `primaryAudience` auf `A` (technischer Peer-Leser) defaulten, die häufigste Form des Korpus. Die übrigen Kriterien werden Reviewer-geprüft (der Autor, die `blog-author`-Skill oder eine zukünftige Lint-Skill).

- [ ] **a-1** Frontmatter deklariert genau eine `primaryAudience` aus den Identifikatoren der direkten Endleser-Untergruppen des Konsumenten (Referenz: `{A, B, C}`).
- [ ] **a-2** Frontmatter deklariert eine `secondaryAudiences`-Liste aus demselben Identifikatoren-Set, die den Primär-Wert nicht enthält.
- [ ] **a-3** Die ersten 80 Wörter des Bodys liefern die Schlagzeile des Posts in einer Form, die kein Weiterlesen erfordert.
- [ ] **a-4** Tiefe, Begriffe und Code-Block-Dichte des Bodys sind auf die deklarierte `primaryAudience` abgestimmt, nicht mitten im Post aufgespalten, um eine Sekundär-Audience zu bedienen.
- [ ] **a-5** Wenn der Post eine nicht-leere `secondaryAudiences`-Liste hat, ist mindestens eine explizite Escape-Hatch (Link, Drawer, Ein-Zeilen-Anpassung) im Post-Body vorhanden und identifizierbar als dieser Audience dienend—durch angrenzende Prosa, durch den Anchor-Text des Links oder durch den Summary-Text des Drawers.
- [ ] **a-6** Jede benannte Drittpartei (Referenzidentifikator `L`) ist in einem Primärquellen-Zitat gegründet; keine private Kommunikation wird ohne explizite Einwilligung zitiert; keine Absichts-Behauptung wird ohne stützende öffentliche Aussage geäußert.
- [ ] **a-7** Der Post passt in Diátaxis Explanation, How-to oder eine Mischung; er ist kein Tutorial im Diátaxis-Sinn und keine reine Reference.
- [ ] **a-8** Die EN-Datei und die DE-Datei tragen identische `primaryAudience` und `secondaryAudiences`.
- [ ] **a-9** Kein Post im jüngsten Fünf-Post-Fenster zielt exklusiv auf die Technischer-Peer-Leser-Audience (Referenz: `A`); das Korpus zeigt mindestens einen Portfolio-Reviewer-targeted und mindestens einen Future-Self-targeted Post in jedem rollenden 10-Post-Fenster (Korpus-Level-Kriterium, im Sprint-Review geprüft, nicht pro Post).
- [ ] **a-10** Wenn Audience-Bedürfnisse im Post kollidieren, begünstigt die Auflösung `primaryAudience` und niemals gegen die Benannte-Drittparteien-Audience (Referenz: `L`); der Reviewer kann den spezifischen Trade-off ohne Suche benennen.
- [ ] **a-11** Post-Body bedient auf Tiefe die deklarierte `primaryAudience` per ihrer Rubrik—konkret:
  - Für `primaryAudience: A`: Arbeits-Artefakt vorhanden (Diff / Ausgabe / Config / Screenshot), Versionen benannter Werkzeuge fixiert, „außerhalb des Geltungsbereichs / nächstes"-Abschnitt vorhanden, **Erfahrungsniveau früh signalisiert** („Ich hatte X vor diesem Projekt nicht angefasst" oder „Ich habe X seit Jahren in Produktion ausgeliefert"—so oder so, ehrlich).
  - Für `primaryAudience: B`: Lede nennt Projekt + Rolle + Aktualität in Klarsprache, Body lesbar ohne Code-Blöcke zu parsen, Link auf die Portfolio-Eintrags-Route des Konsumenten (oder Äquivalent), **Datums-Signal jenseits `pubDate` vorhanden** (ein In-Prosa-Monat / Jahr oder ein Tag wie „laufende Arbeit" / „in Produktion ausgeliefert").
  - Für `primaryAudience: C`: „Warum" jeder Entscheidung festgehalten, erwogene Alternativen benannt, Glossar oder Kontext-Notiz vorhanden, wo re-leser-verwirrende Terminologie auftritt.
- [ ] **a-12** Der Post schichtet nicht über drei Tiefen hinaus (Lede, Body, Escape-Hatch).
- [ ] **a-13** Kein `<details>`-einklappbarer Drawer im Body hält Inhalt, auf den sich das Argument des Posts für die **Primär**-Audience verlässt; Drawer tragen nur Material, das eine Sekundär-Audience wollen könnte, niemals Material, das die Primär-Audience benötigt.

## Referenz-Beispiel-Annex

Der Referenzkonsument ist das `nolte/blog`-Repository. Sein Audience-Artefakt (`AUDIENCES.md` im Repository-Root) bildet auf die abstrakte Form dieser Spec wie folgt ab:

- Technischer Peer-Leser → Identifikator **`A`**.
- Portfolio-Reviewer → Identifikator **`B`**.
- Future-Self-Knowledge-Base-Leser → Identifikator **`C`**.
- Benannte Drittparteien → Identifikator **`L`**.
- Suchmaschinen und LLM-Crawler → Identifikator **`M`** (außerhalb des Geltungsbereichs für Body-Prosa).
- Autor als Site-Maintainer → Identifikator **`D`** (außerhalb des Geltungsbereichs für den Post-Body—die Spec adressiert keine Site-Wartungs-Lektüre).
- Claude Code als KI-Co-Operator → Identifikator **`E`** (außerhalb des Geltungsbereichs für den Post-Body—die Spec adressiert keine KI-Werkzeug-Lektüre).

Korpus-Verteilungsziel (nur Referenzkonsument): **A: ~ 50 %, B: ~ 20 %, C: ~ 30 %** an einem rollenden Fünf-Post-Fenster, rekalibriert gegen tatsächliche Traffic-/Referrer-Daten nach den ersten 20 Posts.

Andere Konsumenten, die diese Spec übernehmen, tragen einen analogen Annex in der eigenen Repository-Dokumentation. Ein Konsument **DARF [MAY]** seinen Annex inline in sein `CLAUDE.md` einbetten statt als separate Datei.

## Offene Fragen

_Alle zuvor zurückgestellten offenen Fragen wurden am 2026-06-06 entschieden: jeder vorläufige Default ist nun die geltende Regel. Siehe `.audits/decisions/2026-06-06-settle-open-questions.md` für die Einzelentscheidungen und Begründungen._

## Referenzen

Audience-Methodik und Content-Design:

- [Content design: planning, writing and managing content—GOV.UK](https://www.gov.uk/guidance/content-design)
- [Content design: writing for GOV.UK](https://www.gov.uk/guidance/content-design/writing-for-gov-uk)
- [Audience Analysis: Primary, Secondary and Hidden Audiences—Writing Commons](https://writingcommons.org/article/audience-analysis-primary-secondary-and-hidden-audiences/)
- [Audience—Howdy or Hello? Technical and Professional Communication](https://odp.library.tamu.edu/howdyorhello/chapter/audience/)
- [The Elements of Content Strategy by Erin Kissane (A Book Apart)](https://elements-of-content-strategy.abookapart.com/)

Dokumentations-Frameworks:

- [Diátaxis—diataxis.fr](https://diataxis.fr/)
- [Start here—Diátaxis in five minutes](https://diataxis.fr/start-here/)
- [Progressive Disclosure—IBM Documentation](https://www.ibm.com/docs/en/technical-content?topic=practices-progressive-disclosure)
- [Progressive Disclosure—I'd Rather Be Writing](https://idratherbewriting.com/ucd-progressive-disclosure/)

Leserverhalten:

- [Inverted Pyramid: Writing for Comprehension—NN/G](https://www.nngroup.com/articles/inverted-pyramid/)
- [How to Prevent F-Pattern Scanning—Mailchimp](https://mailchimp.com/resources/f-pattern-scanning/)
- [Ladders Updates Popular Recruiter Eye-Tracking Study—PR Newswire](https://www.prnewswire.com/news-releases/ladders-updates-popular-recruiter-eye-tracking-study-with-new-key-insights-on-how-job-seekers-can-improve-their-resumes-300744217.html)
- [Eye tracking study shows recruiters look at resumes for 7 seconds—HR Dive](https://www.hrdive.com/news/eye-tracking-study-shows-recruiters-look-at-resumes-for-7-seconds/541582/)

Schreiben für Entwickler (Technischer-Peer-Leser-Audience):

- [How to Write for a Developer Audience—Kalyna Marketing](https://kalynamarketing.com/blog/writing-for-developers)
- [Writing for Developers: 5 Best Practices—Firebrand](https://www.firebrand.marketing/deep-dives/writing-for-developers-5-best-practices/)
- [Kalzumeus—Patrick McKenzie's archive](https://www.kalzumeus.com/archive/)
- [Julia Evans—jvns.ca](https://jvns.ca/)

Knowledge-Base / Future-Self-Schreiben:

- [Evergreen notes—Andy Matuschak](https://notes.andymatuschak.org/Evergreen_notes)
- [A Brief History & Ethos of the Digital Garden—Maggie Appleton](https://maggieappleton.com/garden-history)
- [The Garden of Maggie Appleton](https://maggieappleton.com/garden/)

Fairness gegenüber benannten Drittparteien:

- [BBC sets protocol for generative AI content—Broadcast](https://www.broadcastnow.co.uk/production-and-post/bbc-sets-protocol-for-generative-ai-content/5200816.article)
- [Key AI concepts to grasp in a new hybrid journalism era—Reuters Institute](https://reutersinstitute.politics.ox.ac.uk/key-ai-concepts-grasp-new-hybrid-journalism-era-transparency-autonomy-and-authorship)
- [Offering Criticism in Open Source Projects—Jonathan Desrosiers](https://jonathandesrosiers.com/2026/02/offering-criticism-in-open-source-projects/)

Personal-Blog-Prinzipien:

- [POSSE—IndieWeb](https://indieweb.org/POSSE)
- [Own your data—IndieWeb](https://indieweb.org/own_your_data)
- [The Promise of Stripe Press—alohomora](https://morgmah.substack.com/p/the-promise-of-stripe-press)
