# Blog-Autor

Status: accepted

## Kontext

Leserschaft: Implementierer der [`blog-author`](../../../skills/blog-author/SKILL.md)-Skill im `nolte-shared`-Plugin (primär), menschliche Autoren, die KI-entworfene Blog-Posts in einem Konsumenten-Repository kuratieren, das diesen Vertrag übernimmt (sekundär), und nachgelagerte Review-Skills (`lektorat-apply`, `prose-vale-curator`), die das Post-Paar konsumieren, das diese Spec erzeugt (tertiär).

Ein Konsument dieser Spec ist ein **zweisprachiges Personal-Blog- oder Technik-Blog-Repository**, das die Schwester-Specs [`post-writing-style`](../post-writing-style/de.md) und [`post-audience-communication`](../post-audience-communication/de.md) übernimmt. Der Referenzkonsument ist `nolte/blog`; die Spec ist so formuliert, dass andere Portfolio-Repositories mit derselben Form sie ohne Modifikation übernehmen können (siehe §Konsumenten-Vertrag und §Referenz-Beispiel-Annex).

Posts dieser Klasse werden interaktiv produziert: ein Operator briefed das Thema, ein Autor (ein Mensch oder die `blog-author`-Skill, die über Claude Code schreibt) verfasst einen EN-Post, übersetzt ihn ins Deutsche und übergibt das Paar an eine redaktionelle Ebene ([`spec/project/lektorat/`](../lektorat/de.md)). Was diesem Workflow ohne diese Spec fehlt, ist ein expliziter Vertrag für die **Autorenrolle selbst**—also für die **Inputs**, die ein Post-Draft braucht, die **Schritte**, in denen ein Post Form annimmt, und den **Übergabepunkt**, an dem der Post den Autor verlässt und den Lektor erreicht. Diese Spec füllt diese Lücke.

Drei Schwester-Specs werden hier referenziert, nicht dupliziert:

- [`post-writing-style`](../post-writing-style/de.md) regelt Stimme, Lesbarkeit, Typografie, Verbotswörter und AI-Disclosure-Tonalität—**wie** geschrieben wird.
- [`post-audience-communication`](../post-audience-communication/de.md) regelt Primär-Audience-Deklaration, Audience-Rubriken, Mehraudience-Schichtung, Diátaxis-Positionierung und Behandlung benannter Drittparteien—**für wen** geschrieben wird.
- [`spec/project/audience-identification/`](../audience-identification/de.md) erzeugt das Audience-Artefakt des Konsumenten, das beide Schwester-Specs (und diese Spec) als autoritative Quelle für Audience-Identifikatoren und ihre Erwartungen lesen.

Diese Spec sitzt **davor**: davor, weil sie das Briefing definiert, ohne das kein `post-writing-style`-konformer Draft existieren kann; und davor, weil sie den Übergabepunkt zum Lektor definiert, der die Schwester-Specs als Quelle der pro-Post-Akzeptanzkriterien konsumiert. Die Spec ist absichtlich **prozess- und vertragsorientiert**—sie sagt, **welche Information wann und wo fließt**, nicht, **welche Wörter im Body stehen**.

## Ziele

- Eine **geschlossene Liste verpflichtender Briefing-Inputs** definieren, die ein Post-Draft braucht, sodass der Autor (ein Mensch oder die `blog-author`-Skill) entweder einen vollständigen Draft produziert oder eine explizite, dokumentierte Briefing-Lücke aufzeigt—niemals still eine Lücke erfindet.
- Den **Workflow vom Briefing zur Lektor-Übergabe** in benannten, sequenziellen Schritten auslegen, sodass eine Skill-Implementierung an genau denselben Schritten ansetzt wie ein Mensch.
- Einen **Pre-Handover-Selbst-Check** mandatieren, der die pro-Post-Akzeptanzkriterien aus [`post-writing-style`](../post-writing-style/de.md) und [`post-audience-communication`](../post-audience-communication/de.md) als geschlossene Liste durchgeht, sodass der Lektor mit einem Post startet, der die Schwester-Spec-Regeln nicht offensichtlich verletzt.
- Den **Übergabevertrag zum Lektor** so formulieren, dass er mit [`spec/project/lektorat/`](../lektorat/de.md) (dem Vertragsdokument des Lektors) zusammenspielt, ohne die interne Mechanik des Lektors zu wiederholen.
- Die **harten DARF-NICHT-Pflichten des Autors** an einem Ort bündeln, abgeleitet aus den Hard-Rules des Konsumenten und aus den MUSSEN der zwei Schwester-Specs—sodass „was darf der Autor nie tun" nicht über drei Dateien hinweg rekonstruiert werden muss.
- Als **Vertragsdokument** für die [`blog-author`](../../../skills/blog-author/SKILL.md)-Skill dienen—die Spec ist so formuliert, dass eine Skill-Implementierung die Briefing-Inputs als ihr Input-Schema, die Workflow-Schritte als ihre interaktiven Phasen und die Akzeptanzkriterien als ihre interne Verifikation eins-zu-eins übernehmen kann.

## Nicht-Ziele

- **Stimme, Tonalität, Lesbarkeit, Typografie und Verbotswörter** definieren—das wird umfassend von [`post-writing-style`](../post-writing-style/de.md) abgedeckt. Diese Spec referenziert die pro-Post-Akzeptanzkriterien jener Spec im Selbst-Check; sie wiederholt sie nicht.
- **Audience-Rubriken, Primär-/Sekundär-Audience-Mechanik, Diátaxis-Positionierung oder Fairness-Regeln für benannte Drittparteien** definieren—das wird umfassend von [`post-audience-communication`](../post-audience-communication/de.md) abgedeckt. Diese Spec fordert die Audience-Deklaration als verpflichtenden Briefing-Input und referenziert die pro-Post-Kriterien jener Spec im Selbst-Check.
- Das **Frontmatter-Schema des Konsumenten** (Schlüsselsatz, Pflichtfelder, Typen) definieren—das wird von der Static-Site-Engine des Konsumenten deklariert (Astros Zod-Content-Collection-Schema, Hugos Archetypes, Eleventys Data-Cascade) plus dem `CLAUDE.md` des Konsumenten. Diese Spec setzt jene Felder voraus und verweist auf sie.
- Die **interne Mechanik des Lektors** (Operationen, Dimensionen, Severity-Klassifikation, JSON-Reportform) definieren—das gehört zu [`spec/project/lektorat/`](../lektorat/de.md). Diese Spec definiert nur den **Übergabepunkt** von der Autorenseite.
- **PR-Form, Commit-Message-Konventionen, Branching-Modell oder Merge-Gates** definieren—das gehört zu [`spec/project/pull-request-workflow/`](../pull-request-workflow/de.md), nicht hierher. Diese Spec endet an der Lektor-Übergabe; was folgt, wird anderswo geregelt.
- **Themenwahl, Veröffentlichungs-Frequenz oder Korpus-Mix** definieren—das sind Roadmap- und Sprint-Fragen, die von [`spec/project/roadmap/`](../roadmap/de.md) und [`spec/project/sprint/`](../sprint/de.md) geregelt werden. Diese Spec gilt, sobald ein Thema gewählt ist.
- Die **Trigger-Mechanik** definieren, die diese Skill ausführt, wenn ein Feature `done` erreicht—das ist Aufgabe von [`spec/project/blog-author-trigger/`](../blog-author-trigger/de.md). Diese Spec definiert, was der Autor produziert; die Trigger-Spec definiert, wann der Autor aufgerufen wird.
- **Lint- oder CI-Mechanik** definieren, die die Akzeptanzkriterien automatisiert. Die Spec ist heute Reviewer-Urteil; das Verdrahten in `task check` oder eine nachgelagerte Skill ist offen (siehe §Offene Fragen).

## Konsumenten-Vertrag

Ein Konsumenten-Repository, das diese Spec übernimmt, **MUSS [MUST]** die Vertrags-Oberflächen liefern, die in [`post-writing-style`](../post-writing-style/de.md) §Konsumenten-Vertrag und [`post-audience-communication`](../post-audience-communication/de.md) §Konsumenten-Audience-Vertrag benannt sind. Zusätzlich verlangt diese Spec Folgendes:

- Eine **Post-Paar-Übergabefläche**, die einen einzelnen Commit überlebt: die EN-Datei, die DE-Datei und die drei Liefer-Vertrag-Artefakte, die unter §Liefervertrag benannt sind, sind **alle im selben Merge-Commit erreichbar** (im Commit-Body, im PR-Body oder als referenzierte Dateien im Diff). Erreichbarkeit ist das Gate; die Speicherform ist die Wahl des Konsumenten.
- Ein **Build-Kommando**, das beweist, dass das Post-Paar Ende-zu-Ende rendert (Referenzkonvention ist `task build` / `task check`).
- Einen **Lektor-Einstiegspunkt**, der das Post-Paar konsumiert: heute ist der Referenz-Lektor die `lektorat-apply`-Skill in `nolte-shared` (Zielzustand) oder `prose-vale-curator` (Übergangsregime). Der Konsument **MUSS [MUST]** in seinem `CLAUDE.md` oder gleichwertig benennen, welche der zwei er als Einstiegspunkt akzeptiert.

Wo diese Spec auf „die EN-Datei", „die DE-Datei", „den sprachübergreifenden Bindungs-Key" (Referenz: `translationKey`), „die AI-Disclosure-Flag" (Referenz: `aiGenerated: true`) oder „die Audience-Identifikatoren-Menge" verweist, verweist sie auf die Instanzen des Konsumenten dieser Konzepte unter den Verträgen der Schwester-Specs. Der §Referenz-Beispiel-Annex nennt das konkrete Mapping für den `nolte/blog`-Konsumenten.

## Anforderungen

### Briefing-Inputs

Ein Post-Draft startet mit einem **Briefing**. Die unten aufgeführten Pflichtfelder sind der geschlossene Mindestsatz; fehlt eines, **DARF NICHT [MUST NOT]** der Draft starten, bevor die Lücke entweder gefüllt oder als dokumentierte offene Frage im Briefing festgehalten ist (siehe die „Briefing-Lücken"-Unterregel am Ende dieses Abschnitts). Die optionalen Felder erweitern den Draft; ihre Abwesenheit blockiert ihn nicht.

#### Pflichtfelder

- **MUSS [MUST]** ein **Thema** als ein- bis zweisätzige These benennen, formuliert als das, was der Post **aussagen** wird—nicht als Schlagwort. „Ich beschreibe, wie der `astro:content`-Loader das Frontmatter validiert" besteht; „Astro Content Collections" fällt durch.
- **MUSS [MUST]** **mindestens ein konkret-gegründetes Artefakt** benennen, auf dem der Post aufbaut: einen Repo-Verweis (Repo-Name plus Commit-SHA oder Tag), einen Diff, eine Befehlsausgabe, einen Screenshot, ein README-Zitat oder ein explizites Operator-Briefing. Diese Pflicht setzt die Hard-Rule des Konsumenten „Niemals technische Fakten über Projekte erfinden" an die Eingangsstelle des Workflows—ohne Artefakt darf der Draft nicht starten.
- **MUSS [MUST]** eine **Primär-Audience** aus den Identifikatoren der direkten Endleser-Untergruppen des Konsumenten (Referenz: `{A, B, C}`) benennen, gemäß [`post-audience-communication`](../post-audience-communication/de.md) §Primär-Audience-Deklaration. Der Identifikator für benannte Drittparteien (Referenz: `L`) ist nie eine Primär-Audience; der Suchmaschinen-/Crawler-Identifikator (Referenz: `M`) ist außerhalb des Geltungsbereichs.
- **MUSS [MUST]** eine **Quellenliste** mit URLs zu Primärquellen führen, gegen die jede konkrete technische Behauptung des Posts verifiziert werden kann (README, Release-Notes, RFC, GitHub-Issue, Source-File, Operator-Briefing-Transkript). Die Liste **DARF [MAY]** im Verlauf des Drafts wachsen; sie **DARF NICHT [MUST NOT]** leer bleiben, wenn der Post **eine einzige** konkrete Aussage über ein benanntes Projekt, eine Bibliothek oder ein Werkzeug trägt.
- **MUSS [MUST]** den **`slug`** in ASCII-Kebab-Case festlegen, abgeleitet aus dem englischen Titel; der Slug ist nach Veröffentlichung stabil. Maximale Länge folgt der Slug-Regel des Konsumenten (Referenz: ≤ 60 Zeichen).
- **MUSS [MUST]** den **sprachübergreifenden Bindungs-Key** (Referenz: `translationKey`) festlegen, der zwischen der EN- und der DE-Datei des Post-Paars geteilt wird, gemäß Konsumenten-Vertrag.

#### Optionale Felder

- **DARF [MAY]** **Sekundär-Audiences** (`secondaryAudiences`) als Liste aus den Identifikatoren der direkten Endleser-Untergruppen des Konsumenten deklarieren, exklusive des Primär-Werts. Eine leere Liste signalisiert einen absichtlich engen Post; eine nicht-leere Liste löst die Mehraudience-Schichtungs-Anforderungen aus [`post-audience-communication`](../post-audience-communication/de.md) §Mehraudience-Schichtung aus.
- **DARF [MAY]** einen **Portfolio-Projekt-Slug** (Referenzfeld: `portfolioProject`) deklarieren, wenn der Post an einen Eintrag in der Portfolio-Collection des Konsumenten bindet; das aktiviert die Cross-Link-Erwartung aus [`post-audience-communication`](../post-audience-communication/de.md) §Portfolio-Reviewer-Rubrik („Link auf die Portfolio-Eintrags-Route des Konsumenten").
- **DARF [MAY]** eine **Diátaxis-Position** (`explanation`, `how-to`, `blend`) als Briefing-Hinweis deklarieren; das Frontmatter des Konsumenten trägt heute möglicherweise kein solches Feld (siehe [`post-audience-communication`](../post-audience-communication/de.md) §Offene Fragen—Diátaxis-Frontmatter-Signal), aber die Position formt das Lede und die Body-Form und gehört daher ins Briefing.

#### Update- vs. Neuanlage-Felder

- **MUSS [MUST]** bei einem **Update** eines bereits veröffentlichten Posts einen **Update-Anlass** im Briefing tragen: ein bis zwei Sätze, was sich geändert hat und warum die Aktualisierung jetzt fällig ist (ein Bug in der Originalbehauptung, ein neues Release der zitierten Bibliothek, ein neues besseres Artefakt). Eine kosmetische Korrektur ohne sachliche Änderung **DARF [MAY]** den Anlass auf „Korrekturlauf nach Lektor-Befund `<ID>`" oder Äquivalent verkürzen.
- **MUSS [MUST]** beim Update das Frontmatter-Feld **`updatedDate`** auf das ISO-Datum der Aktualisierung setzen, gemäß Frontmatter-Konvention des Konsumenten. Das Feld **DARF NICHT [MUST NOT]** stillschweigend gesetzt werden, ohne dass der Update-Anlass im Briefing dokumentiert ist.
- **DARF NICHT [MUST NOT]** ein Update den **`slug`** oder den **sprachübergreifenden Bindungs-Key** ändern; das wäre ein neuer Post unter einer neuen Identität, gemäß [`post-audience-communication`](../post-audience-communication/de.md) §Primär-Audience-Deklaration (Write-once-Vertrag).
- Hinweis: die **Schwelle** zwischen Update und Neuanlage—wie groß eine sachliche Änderung sein muss, um statt eines Updates einen neuen Post zu rechtfertigen—ist absichtlich **Autorenurteil** und nicht von einem harten Kriterium geregelt. Eine spätere Spec-Verschärfung wird durch einen konkreten Streitfall ausgelöst, nicht prospektiv.

#### Nachweis-Feld für benannte Drittparteien

- **MUSS [MUST]**, wenn der geplante Post eine **namentlich genannte Drittpartei** charakterisiert (Referenz-Audience-Identifikator: `L`), im Briefing eine **Nachweis-Liste** führen, die für jede Charakterisierung mindestens ein Primärquellen-Zitat trägt (URL plus die zitierte Stelle, wörtlich oder mit Commit-SHA / Revisions-Pin). Das setzt die MUSS aus [`post-audience-communication`](../post-audience-communication/de.md) §Behandlung benannter Drittparteien an die Eingangsstelle des Workflows.
- **MUSS [MUST]** für **Zitate aus privater Kommunikation** (DMs, private E-Mails, geschlossene Issue-Threads, internes Slack) im Briefing eine **Einwilligungs-Notiz** der Quelle tragen—wenigstens als Verweis auf die Stelle, an der die Einwilligung dokumentiert ist (eigene E-Mail-Antwort, geteilter Slack-Thread). Ohne diese Notiz **DARF NICHT [MUST NOT]** das Zitat im Post landen.
- **SOLLTE [SHOULD]** den **bevorzugten Namen und die bevorzugte Großschreibung** der Drittpartei im Briefing festhalten (z. B. `npm` statt `NPM`, `Astro` statt `astro`), damit die Schreibung nicht bei jedem Draft neu recherchiert werden muss.

#### Hero- und OG-Bild

- **DARF [MAY]** ein **Hero- / OG-Bild** im Briefing planen, mit einem Pfad relativ zum öffentlichen Asset-Root des Konsumenten (Referenz: `/public/`) und einem **beschreibenden Alt-Text-Vorschlag**. Hero-Bilder sind heute **nicht** verpflichtend.
- **MUSS [MUST]**, wenn ein Hero- / OG-Bild in den Post aufgenommen wird, der **Alt-Text** beschreiben, **was auf dem Bild zu sehen ist**—nicht die Bildunterschrift wiederholen und nicht „Hero-Bild" oder „Screenshot" lauten (analog zur Screenshot-Alt-Text-Regel aus [`post-writing-style`](../post-writing-style/de.md) §Code, Befehle und andere technische Inhalte).
- **DARF NICHT [MUST NOT]** der Post-Body ein **Hero-Bild als Ersatz** für ein Inverted-Pyramid-Lede verwenden; das Bild ergänzt das Lede, ersetzt es nicht (vgl. [`post-writing-style`](../post-writing-style/de.md) §Struktur und Fluss).
- Hinweis: die breitere **Hero-Bild-Politik** für das Korpus (verpflichtend vs. optional, uniformer Stil, Generierungs-Pipeline) ist nicht entschieden; siehe §Offene Fragen.

#### Briefing-Lücken

- **MUSS [MUST]** jede **Briefing-Lücke** explizit dokumentiert sein, bevor der Draft startet—entweder als „offene Frage" im Briefing-Kopf oder als Inline-Marker im späteren Post-Body, der den Lektor zwingt, die Lücke vor Veröffentlichung zu adressieren.
- **DARF NICHT [MUST NOT]** der Autor (Mensch oder Skill) eine Briefing-Lücke **still** mit einer plausibel klingenden Vermutung füllen; das ist genau die Fehlerart, die die Hard-Rule des Konsumenten „Niemals technische Fakten erfinden" ausschließt.

### Workflow

Der Workflow ist eine **lineare Sequenz** benannter Schritte. Spätere Schritte setzen frühere voraus; Zurückspringen ist erlaubt, **DARF [MAY]** aber **NICHT [NOT]** dazu führen, dass ein späterer Schritt einen früheren still überspringt.

- **MUSS [MUST]** **Schritt 1—Briefing entgegennehmen und klären**: das Briefing (siehe §Briefing-Inputs) wird gegen die Pflichtfelder geprüft; Lücken werden adressiert oder explizit als offene Fragen festgehalten. Ohne erfülltes Briefing endet der Workflow hier.
- **MUSS [MUST]** **Schritt 2—EN-Draft schreiben**: der englische Post-Body wird gemäß [`post-writing-style`](../post-writing-style/de.md) und der Audience-Rubrik aus [`post-audience-communication`](../post-audience-communication/de.md) für die im Briefing benannte `primaryAudience` entworfen. Das Frontmatter wird gemäß Konsumenten-Vertrag ausgefüllt, einschließlich der AI-Disclosure-Flag (Referenz: `aiGenerated: true`) für KI-entworfene Posts.
- **MUSS [MUST]** **Schritt 3—Pre-Handoff-Selbst-Check**: der Selbst-Check (siehe §Pre-Handoff-Selbst-Check) wird gegen den EN-Draft und sein Frontmatter ausgeführt; Befunde werden behoben, **bevor** Schritt 4 startet.
- **MUSS [MUST]** **Schritt 4—DE-Übersetzung schreiben**: der deutsche Post-Body wird unter dem DE-Post-Pfad des Konsumenten (Referenz: `src/content/posts/de/<slug>.md`) angelegt, mit demselben Dateinamens-Slug und demselben sprachübergreifenden Bindungs-Key wie die EN-Datei, mit identischen Werten für `primaryAudience`, `secondaryAudiences`, `pubDate`, `tags`, `portfolioProject` und die AI-Disclosure-Flag. Die Übersetzung folgt §Zweisprachige Typografie aus [`post-writing-style`](../post-writing-style/de.md) und §Zweisprachige Audience-Symmetrie aus [`post-audience-communication`](../post-audience-communication/de.md).
- **MUSS [MUST]** **Schritt 5—Pre-Handoff-Selbst-Check (zweite Hälfte)**: der Selbst-Check wird gegen den DE-Draft und die Paar-Invarianten ausgeführt (siehe §Pre-Handoff-Selbst-Check, Per-Paar-Block).
- **MUSS [MUST]** **Schritt 6—das Build-Kommando des Konsumenten ausführen** (Referenz: `task build` / `task check`). Ein Lauf, der nicht grün ist, blockiert die Übergabe an den Lektor; der Autor behebt die Bau-Fehler und wiederholt den Schritt.
- **MUSS [MUST]** **Schritt 7—Übergabe an den Lektor**, gemäß §Übergabe an den Lektor. Der Autor stellt **keine** eigene Korrekturlese-Mechanik bereit; er liefert einen Post, dessen Eingangsbedingungen die Lektor-Stufe `audit` akzeptiert.
- **SOLLTE [SHOULD]** der Autor zwischen Schritt 2 und 3 (oder zwischen 4 und 5) den **Draft laut lesen** oder per TTS lesen lassen, gemäß [`post-writing-style`](../post-writing-style/de.md) §Edit-Pass. Dieses Laut-Lesen ist Autorenpflicht in jener Spec; diese Spec wiederholt es hier, damit es im Workflow sichtbar bleibt.

### Pre-Handoff-Selbst-Check

Der Selbst-Check ist eine **geschlossene, durchgehbare Liste**. Jedes Item ist eine pro-Post-Anforderung aus einer Schwester-Spec oder aus den Hard-Rules des Konsumenten, die der Autor (Mensch oder die `blog-author`-Skill) aktiv **einmal** für jede der zwei Sprachdateien vor der Lektor-Übergabe beantwortet. Der Selbst-Check **ersetzt nicht** den Lektor; er stellt nur sicher, dass der Lektor mit einem Post startet, der die Spec-Regeln nicht offensichtlich verletzt.

#### Pro Sprachdatei (separat für EN und DE anwenden)

- **MUSS [MUST]** **jedes pro-Post-Akzeptanzkriterium** aus [`post-writing-style`](../post-writing-style/de.md) §Akzeptanzkriterien (a-1 bis a-17) durchgegangen sein und keinen ungelösten Verstoß tragen, sofern das Kriterium auf die zu prüfende Sprachdatei zutrifft (z. B. ist die Flesch–Kincaid-Anforderung a-4 heute auf den EN-Body beschränkt—siehe die vorläufige Klausel jenes Kriteriums).
- **MUSS [MUST]** **jedes pro-Post-Akzeptanzkriterium** aus [`post-audience-communication`](../post-audience-communication/de.md) §Akzeptanzkriterien (a-1 bis a-13) durchgegangen sein, unter dem Enforcement-Status-Caveat jener Spec für die Frontmatter-Felder `primaryAudience` und `secondaryAudiences` (a-1 / a-2 sind autoreseitige Konventionen, bis das Static-Site-Schema des Konsumenten sie deklariert).
- **MUSS [MUST]** **jede konkrete technische Behauptung** über ein benanntes Projekt, eine Bibliothek oder ein Werkzeug gegen die im Briefing geführte Quellenliste **gegenprüfen**—die zitierte Stelle neu öffnen, das zitierte README am fixierten Stand öffnen oder den zitierten Befehl neu ausführen (vgl. [`post-writing-style`](../post-writing-style/de.md) §Edit-Pass).
- **MUSS [MUST]** eine gerichtete Suche-und-Prüfung für die **Verbotswörter-Liste** aus [`post-writing-style`](../post-writing-style/de.md) §Verbotswörter und -phrasen auf der zu prüfenden Sprachdatei ausgeführt haben; jeder Treffer wird entweder ersetzt oder trägt einen dokumentierten Override per §Override-Verfahren jener Spec.

#### Pro Paar (auf das EN + DE-Paar als Ganzes anwenden)

- **MUSS [MUST]** der **sprachübergreifende Bindungs-Key** in beiden Dateien **identisch** sein, und der Dateinamens-Slug ist in `<slug>.md` auf sowohl der EN- als auch der DE-Seite identisch (per Slug-Regel des Konsumenten).
- **MUSS [MUST]** das Frontmatter-Feld **`primaryAudience`** in beiden Dateien identisch sein; **`secondaryAudiences`** ebenso identisch (per [`post-audience-communication`](../post-audience-communication/de.md) §Zweisprachige Audience-Symmetrie).
- **MUSS [MUST]** die **AI-Disclosure-Flag** (Referenz: `aiGenerated: true`) in beiden Dateien gesetzt sein, solange der Post KI-entworfen ist (per Hard-Rule des Konsumenten und [`post-writing-style`](../post-writing-style/de.md) §AI-Disclosure-Tonalität).
- **MUSS [MUST]** das **Build-Kommando** des Konsumenten (Referenz: `task build` / `task check`) lokal grün gegen den Working-Tree laufen, der beide Dateien enthält.
- **SOLLTE [SHOULD]** der Autor das EN ↔ DE-Paar einmal über den Sprachschalter im Dev-Server des Konsumenten umschalten, damit ein sprachübergreifender Bindungs-Mismatch oder ein stiller Paar-Bruch sichtbar wird (per [`post-writing-style`](../post-writing-style/de.md) §Edit-Pass).

### Liefervertrag

Dieser Abschnitt benennt die Artefakte, die **zusätzlich** zum Post-Paar selbst zu liefern sind, damit der Lektor und jede nachgelagerte Skill die in §Pre-Handoff-Selbst-Check und §Übergabe an den Lektor formulierten Bedingungen **verifizierbar** vorfinden—nicht nur als „der Autor hat geprüft" beteuert.

Die Verpflichtung ist **rollenkonditional**:

- für den **menschlichen Autor** sind die Artefakte unten **SOLLTE [SHOULD]**, weil ein Mensch die Belege in seinem Kopf zusammenstellt und den Selbst-Check kohärent durchgeht;
- für die **`blog-author`-Skill** (und jeden anderen agentischen Autor) sind sie **MUSS [MUST]**, weil ein Agent ohne expliziten Output-Beleg von einem nicht-prüfenden Agenten nicht unterscheidbar ist.

Die heute gültige Form für alle drei Artefakte ist Markdown-Prosa (handgeschrieben) oder eine einfache Liste im Commit-Body / in der PR-Beschreibung. Eine maschinenlesbare Form (YAML / JSON, mit Schema) ist als Folge-Schritt aufgeschoben (siehe §Offene Fragen—„Briefing und Liefervertrag als YAML-Schema").

#### Selbst-Check-Manifest

- **MUSS [MUST]** (für die `blog-author`-Skill; **SOLLTE [SHOULD]** für menschliche Autoren) eine Status-Zeile für jeden pro-Post-Akzeptanzkriterien-ID aus den Schwester-Specs liefern, die §Pre-Handoff-Selbst-Check referenziert, mit einem von genau drei Werten:
  - `passed`—das Kriterium ist erfüllt;
  - `finding: <kurzer Grund>`—das Kriterium ist verletzt, der Befund ist beschrieben;
  - `override: <Verweis auf §Override-Verfahren in post-writing-style oder eine analoge Begründung>`—der Verstoß ist dokumentiert und akzeptiert.
- **MUSS [MUST]** (für die `blog-author`-Skill) den Pro-Sprachdatei- und den Pro-Paar-Block aus §Pre-Handoff-Selbst-Check im Manifest getrennt halten, sodass Build-Status, sprachübergreifende Bindungs-Identität und Audience-Feld-Identität als eigene Zeilen sichtbar sind.
- **DARF [MAY]** das Manifest im Commit-Body / in der PR-Beschreibung leben (eine Markdown-Liste reicht) oder in einer separaten Datei neben dem Post-Paar (z. B. `<slug>.selfcheck.md`); der Pfad ist nicht vorgeschrieben, aber **Erreichbarkeit zusammen mit dem Post-Paar im Merge-Commit** ist es.

#### Quellen-zu-Behauptungs-Mapping

- **MUSS [MUST]** (für die `blog-author`-Skill; **SOLLTE [SHOULD]** für menschliche Autoren) jeden Eintrag der Briefing-Quellenliste auf die konkreten Post-Passagen abbilden, die er stützt—minimal in der Form „Quelle `<n>` stützt Post-Absatz `<Anker oder Überschrift + Satznummer>`". Mehrfach-Stützung ist erlaubt; eine ungenutzte Quelle ist ein Befund, kein Verstoß.
- **MUSS [MUST]** (für die `blog-author`-Skill) jede **konkrete technische Behauptung** über ein benanntes Projekt / Bibliothek / Werkzeug auf mindestens eine Quelle zeigen; sonst trägt sie einen `finding`-Eintrag im Selbst-Check-Manifest (Verstoß gegen §Verbotene Praktiken für den Autor—„Behauptungen ohne Quellen").
- **DARF [MAY]** das Mapping in das Selbst-Check-Manifest integriert sein oder daneben als zweite Liste sitzen; separate Pflege ist erlaubt, separate Lesbarkeit ist verpflichtend.

#### Übergabe-Manifest

- **MUSS [MUST]** (für die `blog-author`-Skill; **SOLLTE [SHOULD]** für menschliche Autoren) eine kurze ein- bis drei-Zeilen-Notiz die folgenden Felder explizit benennen:
  - die **gewählte Übergabe-Route** per §Übergabe an den Lektor (heute: `prose-vale-curator`, Selbst-Urteil oder eine Kombination—Zielzustand: ein Lauf von `lektorat-apply`);
  - der **Build-Status** mit dem verwendeten Kommando (`task build` oder `task check`) und dem Ergebnis (`grün`);
  - der **Repository-Stand**, gegen den der Selbst-Check ausgeführt wurde (Branch-Name plus optionaler Commit-SHA), damit der Lektor weiß, gegen welchen Stand er prüft.
- **MUSS [MUST]** das Übergabe-Manifest **zusammen mit dem Post-Paar sichtbar sein**—im Commit-Body, im PR-Body oder als referenzierte Datei. Eine still ohne Manifest erfolgte Übergabe ist ein Verstoß gegen §Übergabe an den Lektor (Eingangsbedingungen).
- **DARF NICHT [MUST NOT]** das Manifest behaupten, dass ein Verfahren durchgeführt wurde, das tatsächlich nicht ausgeführt wurde; eine falsche Beteuerung ist ein schwererer Verstoß als ein offener `finding`-Eintrag.

### Übergabe an den Lektor

Der **Lektor** ist die nachgelagerte Korrekturlese-Stufe, geregelt von [`spec/project/lektorat/`](../lektorat/de.md). Aus Sicht des Autors ist der Lektor eine Black Box mit einer `audit`-Eingangsstufe; was innen geschieht (fünf Dimensionen, Severity-Klassifikation, JSON-Reportform), ist außerhalb des Geltungsbereichs dieser Spec. Die Übergabe ist ein **Vertragspunkt**: der Autor liefert einen Post, der die Eingangsbedingungen erfüllt, und übergibt die redaktionelle Endverantwortung an den Lektor.

#### Eingangsbedingungen für die `audit`-Stufe des Lektors

- **MUSS [MUST]** das **EN + DE-Post-Paar** vollständig auf der Festplatte vorhanden sein, beide Dateien mit gültigem Frontmatter, identischem sprachübergreifenden Bindungs-Key, identischem Slug und identischen Audience-Feldern (siehe §Pre-Handoff-Selbst-Check, Per-Paar).
- **MUSS [MUST]** das **Build-Kommando** des Konsumenten grün gelaufen sein; der Lektor ist kein Build-Repair-Tool, und ein Post, der nicht baut, ist nicht übergabefertig.
- **MUSS [MUST]** die **AI-Disclosure-Flag** (Referenz: `aiGenerated: true`) auf KI-entworfenen Posts gesetzt sein; der Lektor stützt seine Behandlung des Posts auf diese Flag (vgl. [`post-writing-style`](../post-writing-style/de.md) §AI-Disclosure-Tonalität).
- **MUSS [MUST]** der **Selbst-Check** (siehe §Pre-Handoff-Selbst-Check) abgeschlossen sein; offene Selbst-Check-Befunde werden **vor** der Übergabe gelöst, nicht **mit** der Übergabe.

#### Aufgabengrenze

- **DARF NICHT [MUST NOT]** diese Spec verlangen, dass der Blog-Autor die **interne Mechanik des Lektors** (Metriken, Schwellen, Dimension-IDs) kennt oder reproduziert. Der Autor übergibt einen Post; der Lektor liefert Befunde. Die Spec definiert den Übergabepunkt, nicht die Lektor-Operation.
- **DARF NICHT [MUST NOT]** der Autor versuchen, **Lektor-Befunde im Voraus zu antizipieren** und dadurch die Schwester-Spec-Regeln anders zu interpretieren, als sie geschrieben sind. Der Selbst-Check dient den geschriebenen Regeln; alles darüber hinaus ist die Aufgabe des Lektors.

#### Übergabe-Routen

Der Autor **MUSS [MUST]** in Schritt 7 genau eine der zwei unten stehenden Routen anwenden und **MUSS [MUST]** die gewählte Route im Übergabe-Manifest benennen (siehe §Übergabe-Manifest), damit die Route im Merge-Commit auditierbar ist.

- **Zielzustand-Route**—die `audit`-Operation aus [`lektorat-apply`](../../../skills/lektorat-apply/SKILL.md) über das EN + DE-Post-Paar ausführen (Blog-Posts sind für einen `blog-author`-übernehmenden Konsumenten eine Opt-in-`Lektorat`-Scope-Fläche, gemäß [`spec/project/lektorat/`](../lektorat/de.md) §Scope and applicability). Jeder Befund der Severity **`critical`** wird vor dem Mergen des Post-Paars gelöst (per `patch`-Operation, per Autor-Edits oder per der eingebauten „skip-and-record"-Ablehnung des Befunds mit dokumentiertem Grund). Der Autor **SOLLTE [SHOULD]** Befunde der Severity **`warning`** adressieren, mit dem Recht auf eine dokumentierte Ablehnung in Einzelfällen. Befunde der Severity **`suggestion`** sind optional.
- **Übergangs-Route**—den `prose-vale-curator`-Agent aus `nolte-shared` über die **englische** Sprachdatei ausführen (deckt EN-Vale-Mechanik ab; keine DE-Pipeline) **und** ein dokumentiertes **Reviewer-Urteil** des menschlichen Autors gegen den Selbst-Check festhalten, explizit als „transitionaler Selbst-Copy-Edit" im Übergabe-Manifest vermerkt. Diese Route ist nur erlaubt, solange [`spec/project/lektorat/`](../lektorat/de.md) noch nicht zur Übernahme durch den Konsumenten freigegeben ist.

Ein Konsument **DARF NICHT [MUST NOT]** eine dritte Route führen. Die Übergangs-Route ist ausdrücklich zeitlich begrenzt und wird durch die Zielzustand-Route ersetzt, sobald der Konsument die Übernahme signalisiert (durch Entfernen der Übergangs-Klausel aus seinem `CLAUDE.md` oder gleichwertigen Vertragsdokument).

### Verbotene Praktiken für den Autor

Die folgenden Regeln sind die harten **DARF-NICHT-Pflichten** des Autors, gebündelt aus den Hard-Rules des Konsumenten und aus MUSSEN der zwei Schwester-Specs. Sie sind an einem Ort versammelt, sodass „was darf der Autor nie tun" nicht über drei Dateien hinweg rekonstruiert werden muss; die Schwester-Specs und das `CLAUDE.md` des Konsumenten bleiben die autoritativen Quellen.

- **DARF NICHT [MUST NOT]** eine **konkrete technische Behauptung** über ein benanntes Projekt, eine Bibliothek oder ein Werkzeug **ohne eine Primärquelle** in der Briefing-Quellenliste setzen (Hard-Rule des Konsumenten; gespiegelt in [`post-writing-style`](../post-writing-style/de.md) §AI-Disclosure-Tonalität).
- **DARF NICHT [MUST NOT]** die **AI-Disclosure-Flag** (Referenz: `aiGenerated: true`) auf einem KI-entworfenen Post entfernen oder auf `false` setzen (Hard-Rule des Konsumenten).
- **DARF NICHT [MUST NOT]** einen Post als **DE-only** oder **EN-only** veröffentlichen; das Paar ist Pflicht (Hard-Rule des Konsumenten; gespiegelt in §Briefing-Inputs und §Workflow).
- **DARF NICHT [MUST NOT]** den **`primaryAudience`-Wert** nach Veröffentlichung rotieren, um einen unterperformenden Post umzunutzen ([`post-audience-communication`](../post-audience-communication/de.md) §Primär-Audience-Deklaration—Write-once-Vertrag).
- **DARF NICHT [MUST NOT]** **private Kommunikation** ohne explizite Einwilligung der Quelle zitieren, dokumentiert im Nachweis-Feld des Briefings für benannte Drittparteien ([`post-audience-communication`](../post-audience-communication/de.md) §Behandlung benannter Drittparteien; gespiegelt in §Briefing-Inputs).
- **DARF NICHT [MUST NOT]** ein Wort aus der **geschlossenen Verbotsliste** in [`post-writing-style`](../post-writing-style/de.md) §Verbotswörter und -phrasen ohne dokumentierten Override in der umgebenden Prosa verwenden.
- **DARF NICHT [MUST NOT]** den **sprachübergreifenden Bindungs-Key** zwischen der EN- und der DE-Datei desselben Post-Paars unterscheiden lassen oder den Slug zwischen den zwei Sprachen unterscheiden lassen (Slug-Regel des Konsumenten; gespiegelt in §Pre-Handoff-Selbst-Check).

## Akzeptanzkriterien

Ein Post-Draft erfüllt diese Spec, wenn **alle** der pro-Post-Kriterien unten gelten. Jedes Kriterium ist so formuliert, dass ein Reviewer (der Autor, die `blog-author`-Skill oder der Lektor selbst) es ohne Ambiguität als erledigt / nicht erledigt markieren kann.

- [ ] **a-1** Das Briefing trägt **alle Pflichtfelder** aus §Briefing-Inputs (Thema, mindestens ein gegründetes Artefakt, Primär-Audience, Quellenliste, Slug, sprachübergreifender Bindungs-Key); fehlende Werte sind als explizite offene Fragen im Briefing festgehalten.
- [ ] **a-2** Wenn der Post benannte Drittparteien charakterisiert (Referenz-Audience-Identifikator: `L`), trägt das Briefing in der Nachweis-Liste ein **Primärquellen-Zitat** für jede Charakterisierung und eine **Einwilligungs-Notiz** für jedes Zitat aus privater Kommunikation.
- [ ] **a-3** Der **EN-Draft wurde vor dem DE-Draft erzeugt** (Schritt 2 vor Schritt 4); die Workflow-Schritt-Reihenfolge wird respektiert.
- [ ] **a-4** Der **Pre-Handoff-Selbst-Check** (§Pre-Handoff-Selbst-Check) wurde für **beide** Sprachdateien separat plus das Paar als Ganzes abgeschlossen; vor der Lektor-Übergabe bleibt kein ungelöster Befund.
- [ ] **a-5** Das **Build-Kommando** des Konsumenten (Referenz: `task build` / `task check`) ist lokal grün gegen den Working-Tree, der beide Dateien enthält.
- [ ] **a-6** Das EN + DE-Paar teilt einen identischen sprachübergreifenden Bindungs-Key und einen identischen Dateinamens-Slug; `primaryAudience`, `secondaryAudiences`, `pubDate`, `tags`, `portfolioProject` und die AI-Disclosure-Flag sind zwischen den zwei Dateien identisch.
- [ ] **a-7** Bei einem **Update** eines bereits veröffentlichten Posts ist `updatedDate` gesetzt **und** der Update-Anlass im Briefing dokumentiert; `slug` und der sprachübergreifende Bindungs-Key sind unverändert.
- [ ] **a-8** Wenn der Post ein **Hero- / OG-Bild** trägt, ist der Alt-Text beschreibend (was auf dem Bild zu sehen ist) und wiederholt nicht die Bildunterschrift; das Bild ersetzt nicht das Lede.
- [ ] **a-9** Die Lektor-Übergabe geschieht nur, nachdem die **Eingangsbedingungen für die `audit`-Stufe** (§Übergabe an den Lektor) erfüllt sind; die gewählte Übergabe-Route (Zielzustand vs. Übergang) ist im Übergabe-Manifest benannt.
- [ ] **a-10** Keine der **harten DARF-NICHT-Regeln** aus §Verbotene Praktiken für den Autor ist verletzt; insbesondere ist die AI-Disclosure-Flag gesetzt, keine private Kommunikation wird ohne Einwilligung zitiert, kein Wort aus der Verbotsliste wird ohne Override verwendet, und der `primaryAudience`-Wert wurde nach Veröffentlichung nicht rotiert.
- [ ] **a-11** Für die **`blog-author`-Skill**: das Selbst-Check-Manifest, das Quellen-zu-Behauptungs-Mapping und das Übergabe-Manifest sind per §Liefervertrag zusammen mit dem Post-Paar im Merge-Commit erreichbar; für einen **menschlichen Autor** ist mindestens das Übergabe-Manifest sichtbar (gewählte Übergabe-Route, Build-Status, Repository-Stand).

## Referenz-Beispiel-Annex

Der Referenzkonsument ist das `nolte/blog`-Repository (ein zweisprachiger Astro-Static-Blog). Es bildet die abstrakten Konzepte dieser Spec auf die konkreten Felder unten ab:

- Post-Paar-Lokation: EN unter `src/content/posts/en/<slug>.md`, DE unter `src/content/posts/de/<slug>.md`.
- Sprachübergreifender Bindungs-Key: Frontmatter-Feld `translationKey`.
- AI-Disclosure-Flag: Frontmatter-Feld `aiGenerated: true`.
- Slug-Regel: ASCII-Kebab-Case, abgeleitet aus dem EN-Titel, ≤ 60 Zeichen, nach Veröffentlichung stabil.
- Frontmatter-Schema-Quelle: Astro-Zod-Schema unter `src/content.config.ts`.
- Audience-Artefakt: `AUDIENCES.md` im Repository-Root, mit Identifikatoren `A` (technische Leser), `B` (Portfolio-Reviewer), `C` (Autor als Future-Self), `L` (benannte Drittparteien), `M` (Suchmaschinen), `D` (Autor als Site-Maintainer, außerhalb des Geltungsbereichs für Post-Body), `E` (Claude Code als KI-Co-Operator, außerhalb des Geltungsbereichs für Post-Body).
- Autorenseitiges Vertragsdokument: `CLAUDE.md` im Repository-Root.
- Build-Kommando: `task build` (voll) / `task check` (schnellere Variante).
- Portfolio-Eintrags-Route (für den `B`-Rubrik-Cross-Link): `/projects/<slug>`.
- Lektor-Einstiegspunkt: `lektorat-apply` (Zielzustand) / `prose-vale-curator` (Übergang).

Andere Konsumenten, die diese Spec übernehmen, tragen einen analogen Annex in der eigenen Repository-Dokumentation. Ein Konsument **DARF [MAY]** seinen Annex inline in sein `CLAUDE.md` einbetten statt als separate Datei.

## Offene Fragen

- **Per-Konsument-Übernahme der Zielzustand-Übergabe-Route — aufgelöst (2026-06-06).** §Übergabe-Routen behält die Zwei-Routen-Oberfläche per Design bei (Zielzustand `lektorat-apply` oder Übergang `prose-vale-curator` + Reviewer-Urteil). Bedingung (1) ist nun erfüllt: [`spec/project/lektorat/`](../lektorat/de.md) ist `Status: accepted` und nimmt Blog-Posts als Opt-in-Scope-Fläche auf, sodass die Zielzustand-Route jedem Konsumenten zur Verfügung steht, der sich einklinkt. Bedingung (2) bleibt per Design pro Konsument: ein Konsument schaltet auf eine Ein-Routen-Oberfläche um, wenn sein `CLAUDE.md` `lektorat-apply` als Lektor-Einstiegspunkt benennt und die Übergangs-Klausel streicht; bis dahin bleibt die Übergangs-Route für diesen Konsumenten gültig. Der Referenzkonsument `nolte/blog` (`~/repos/github/blog/CLAUDE.md`) hat diese Änderung noch nicht vorgenommen und behält die Zwei-Routen-Oberfläche. Die Zwei-Routen-Oberfläche ist damit das stehende Design, keine offene Entscheidung.
_Die Deferrals „Übergabe-Vertrag als YAML-Schema" und „Hero-Bild-Korpus-Politik" wurden am 2026-06-06 entschieden (siehe [`.audits/decisions/2026-06-06-settle-open-questions.md`](../../../.audits/decisions/2026-06-06-settle-open-questions.md)): der Prosa-Übergabe-Vertrag steht, und die Hero-Bild-Korpus-Politik bleibt eine konsumentenseitige Produktentscheidung. Das gelöste Item oben und die „Intentionally not open"-Notizen unten bleiben erhalten._

### Absichtlich nicht offen

- **Update-vs.-Neuanlage-Schwelle** ist keine offene Frage, sondern eine absichtlich reaktive Entscheidung; die Schwelle ist Autorenurteil (siehe §Briefing-Inputs, Update- vs. Neuanlage-Felder). Ein konkreter Streitfall würde eine spätere Spec-Verschärfung auslösen.
- **Trigger-Integration ist gelöst, nicht offen.** Die Begleit-Spec [`spec/project/blog-author-trigger/`](../blog-author-trigger/de.md) ist veröffentlicht; ihre §Briefing-Ableitung erfüllt die §Briefing-Inputs dieser Spec, und die Referenz-Verdrahtung (`sprint-execute` Operation C Schritt 6 → `blog-author-trigger`) ist implementiert. Die stehende Schnittstelle zwischen den zwei Specs bleibt §Briefing-Inputs.

## Referenzen

Schwester-Specs (im selben Plugin):

- [`post-writing-style/de.md`](../post-writing-style/de.md)—Stimme, Lesbarkeit, Typografie, Verbotswörter, AI-Disclosure-Tonalität.
- [`post-audience-communication/de.md`](../post-audience-communication/de.md)—Primär-Audience-Deklaration, Audience-Rubriken, Mehraudience-Schichtung, Diátaxis, Behandlung benannter Drittparteien.
- [`audience-identification/de.md`](../audience-identification/de.md)—Methodik, die das Audience-Artefakt des Konsumenten erzeugt.
- [`lektorat/de.md`](../lektorat/de.md)—das Vertragsdokument des Lektors; der in §Übergabe an den Lektor benannte Übergabe-Endpunkt.
- [`blog-author-trigger/de.md`](../blog-author-trigger/de.md)—wann der Autor aufgerufen wird (z. B. aus `sprint-execute` bei einem `feature → done`-Übergang); erzeugt das Briefing, das diese Spec konsumiert.

Hintergrund zum Workflow-Stil dieser Spec:

- [Diátaxis—diataxis.fr](https://diataxis.fr/)—die Quadranten-Theorie, die von [`post-audience-communication`](../post-audience-communication/de.md) §Diátaxis-Positionierung konsumiert wird; hier relevant, weil die Diátaxis-Position ein optionales Briefing-Feld ist.
- [Inverted Pyramid—Nielsen Norman Group](https://www.nngroup.com/articles/inverted-pyramid/)—die Lede-Form, die von beiden Schwester-Specs gefordert wird; hier relevant, weil das Hero-Bild-DARF-NICHT verhindert, dass das Bild das Inverted-Pyramid-Lede ersetzt.
- [Content design: writing for GOV.UK](https://www.gov.uk/guidance/content-design/writing-for-gov-uk)—Inspiration für die „Inputs—Prozess—Übergabepunkt"-Trennung, die diese Spec strukturell übernimmt.
