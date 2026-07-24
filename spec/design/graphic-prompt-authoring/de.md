# Grafik-Prompt-Autorenschaft

Status: draft

## Kontext

Portfolioweit braucht KI-Bildgenerierung erst einen Prompt, bevor sie ein Asset erzeugen kann: ein Hero-Bild für einen Blogpost, eine Empty-State-Illustration für eine Web-App, ein App-Icon, eine Social Card. Diese Prompts ad hoc zu schreiben erzeugt zwei Fehlermodi. Erstens driften die Prompts vom Brand ab — jeder Autor greift zu anderen Farbwörtern, ignoriert die publizierte Style-Referenz oder hartcodiert eine Farbton-Intuition, die das `corporate-design-colors`-Spec verbietet. Zweitens sind die Prompts nicht reproduzierbar: Es gibt kein dauerhaftes Artefakt, das festhält, was angefragt wurde, sodass „dasselbe Bild, nur breiter" Monate später Raterei ist.

Diese Spec regelt, wie ein Claude-Code-Agent (der `graphic-prompt-generator`-Agent, `distribution: plugin`) ein kurzes Grafik-Briefing in ein **brand-konformes, generatorfertiges Prompt-Dokument auf der Platte** überführt. Sie ist die Autoren-Hälfte der KI-Bild-Pipeline: Diese Spec erzeugt den Prompt; `spec/tools/image-generation/` konsumiert einen Prompt und liefert eine Bilddatei; `spec/design/png-to-transparent-svg/` reinigt einen generierten Raster zu einem Vektor, wenn Transparenz nötig ist. Der Farbvertrag, den diese Prompts erfüllen müssen, gehört zu `spec/design/corporate-design-colors/` §AI image color contract; diese Spec wiederholt ihn nicht, sondern operationalisiert ihn für den Prompt-Autoren-Schritt und erweitert ihn auf Generatoren jenseits von Midjourney.

Die Capability ist der generalisierte Nachfolger eines projektlokalen `gemini-graphic-prompt-generator`-Agents, der die Palette, das Maskottchen und die Dateipfade eines einzelnen Projekts hartcodiert hatte. Die Portfolio-Form liest den Brand aus den publizierten Design-Tokens des Konsumenten-Repositorys, statt den Brand irgendeines Projekts im Body zu tragen.

Leser: Skill- und Agent-Autoren, die den Prompt-Autoren-Agent pflegen; Reviewer, die prüfen, dass erzeugte Prompt-Dokumente brand-konform sind; Operatoren, die den Agent mit einem frei formulierten Brief aufrufen und sich auf das dauerhafte Prompt-Dokument stützen, um ein Asset später neu zu generieren — diese Spec regelt das erzeugte Dokument und seine Reproduzierbarkeit, nicht das interne Format des Briefs.

## Ziele

- Ein Grafik-Briefing rein, ein strukturiertes, copy-paste-fertiges Prompt-Dokument auf der Platte raus — ein dauerhaftes Artefakt pro angefordertem Asset
- Jeder autorisierte Prompt ist per Konstruktion brand-konform: Er konsumiert die publizierten Brand-Tokens und das deskriptive Farbvokabular, statt Farbe aus Intuition neu abzuleiten
- Prompts sind reproduzierbar: Das Dokument hält genug fest (Zielgenerator, Style-Referenz, deskriptive Phrasen, Hex-Verstärkung, Seed-Slot, Zielmaße), um das Asset später neu zu erzeugen oder anzupassen
- Der Vertrag ist in seiner Form generatoragnostisch, lässt aber jeden Prompt explizit genau einen konkreten Generator (Gemini, Midjourney oder einen Nachfolger) anvisieren
- Die Grenze zu den benachbarten Specs (Farbvertrag, Bildgenerierung, Transparenz-Reinigung) ist explizit, sodass der Agent nicht außerhalb seines Autoren-Anwendungsfensters aufgerufen wird

## Nicht-Ziele

- Definition des Brand-Farbsystems, des deskriptiven Farbvokabulars, der kanonischen Style-Referenz (`--sref` oder pro-Modell-Äquivalent) oder der Farb-Prompt-Assemblierungs-Reihenfolge — alles im Besitz von `spec/design/corporate-design-colors/` §AI image color contract; diese Spec referenziert jenen Vertrag und darf ihm nicht widersprechen
- Der tatsächliche Aufruf eines Bildgenerators oder das Schreiben einer Bilddatei (im Besitz von `spec/tools/image-generation/` und jedem künftigen pro-Generator-Geschwister)
- Nachbearbeitung erzeugter Raster — Hintergrund-Reinigung und Vektorisierung gehören zu `spec/design/png-to-transparent-svg/`
- Nicht-farbliche Bild-Achsen (Komposition, Beleuchtung, fotografisch-vs-illustrativ) über das hinaus, was ein einzelnes Briefing spezifiziert; eine künftige `spec/design/imagery-style/` besitzt die portfolioweite Behandlung
- Pflege des `brand-prompt-library.md`-Ledgers *publizierter* Hero-Bilder (das ist ein Post-Generierungs-Record im Besitz von `corporate-design-colors`); diese Spec regelt Vor-Generierungs-Prompt-Dokumente

## Anforderungen

### Brand-Bezug

- **MUSS [MUST]** den Brand aus dem publizierten Design-Token-Bundle des Konsumenten-Repositorys und dem `brand-vocabulary.md` der freigegebenen deskriptiven Farbphrasen auflösen, die `spec/design/corporate-design-colors/` deklariert; der Agent **DARF NICHT [MUST NOT]** die konkrete Palette, das Maskottchen oder Brand-Assets irgendeines Projekts im eigenen Body tragen
- **MUSS [MUST]**, wenn kein publiziertes Brand-Bundle oder `brand-vocabulary.md` im Konsumenten-Repository auffindbar ist, stoppen und die fehlende Brand-Quelle melden, statt Farbwerte zu erfinden; ein Off-Brand-Prompt ist schlimmer als kein Prompt
- **MUSS [MUST]** Farbe auf der Ebene deskriptiver Phrasen und semantischer Tokens konsumieren, nie durch Picken eines rohen Farbtons; Hex-Werte erscheinen im Prompt nur als der vom Farbvertrag definierte Verstärkungs-Slot, nie als alleiniges Farbsignal ([corporate-design-colors §AI image color contract](../corporate-design-colors/de.md))
- **DARF [MAY]** zusätzlichen Read-only-Projektkontext lesen (Theme-Token-Dateien, ein bestehendes Style-Referenz-Bild, frühere Prompt-Dokumente), um einen Batch visuell konsistent zu halten

### Prompt-Assemblierung

- **MUSS [MUST]** jeden brand-bewussten Prompt in der von `corporate-design-colors` §AI image color contract vorgeschriebenen Reihenfolge assemblieren: (1) die kanonische Style-Referenz (`--sref`-Code für Midjourney oder das pro-Modell-Äquivalent für Generatoren ohne sref-Mechanismus), (2) deskriptive Farbphrasen aus `brand-vocabulary.md`, (3) Hex-Werte als finale Verstärkung angehängt, (4) ein festgehaltener Seed-Slot für Reproduzierbarkeit
- **MUSS [MUST]** das pro-Modell-Style-Referenz-Äquivalent für sref-lose Generatoren (ein festes Referenzbild oder ein kanonischer Stil-Absatz) als im Besitz von `corporate-design-colors` §AI image color contract behandeln; diese Spec konsumiert, was jener Vertrag festschreibt, und **DARF NICHT [MUST NOT]** das Äquivalent eigenmächtig Generator für Generator entscheiden
- **MUSS [MUST]** pro Prompt genau einen benannten Generator anvisieren und dessen Prompt-Syntax verwenden; ein Prompt-Dokument **MUSS [MUST]** seinen Zielgenerator benennen (zum Beispiel `gemini-2.5-flash-image`, `midjourney-v7`), damit ein nachgelagerter Konsument weiß, für welches Tool der Prompt gültig ist
- **MUSS [MUST]**, wenn der benannte Generator FLUX oder Gemini ist, der Generierungs-Grundlage dieses Modells und ihren harten Invarianten folgen — `spec/design/flux-image-generation/` für FLUX-Ziele, `spec/design/gemini-image-generation/` für Gemini-Ziele —, denn ein Prompt ist nicht modellportabel: Die FLUX- und Gemini-Prompts für dasselbe Asset unterscheiden sich materiell (FLUX will eine knappe, front-loaded Beschreibung mit `guidance = 0` und ohne Negative Prompts; Gemini will erzählende Prosa plus genannte Absicht und rendert in Anführungszeichen gesetzten Bild-Text zuverlässig), daher **MUSS [MUST]** der erzeugte Prompt auf das Modell optimiert sein, auf dem er läuft, nicht bloß gültige Syntax dafür
- **MUSS [MUST]** eine explizite Vermeidungs-Klausel einschließen (zum Beispiel: kein eingebetteter Text, keine Logos anderer Firmen, kein Wasserzeichen), passend zum Zielgenerator, weil generierter Text und Streumarken über aktuelle Diffusionsmodelle hinweg unzuverlässig sind; sie über den eigenen Negativ-Mechanismus des Generators ausdrücken nur dort, wo einer existiert (Midjourneys `--no`), und für FLUX und Gemini — die keinen Negative-Prompt-Parameter exponieren — die Vermeidung als positive Formulierung des gewünschten Zustands gemäß der Modell-Grundlage kodieren (`a clean, uncluttered background` statt `no clutter`), niemals als Negative-Prompt-Parameter
- **DARF NICHT [MUST NOT]** lesbaren Text oder Typografie als Nutzlast des Assets in den Prompt einbetten; Text wird in der Nachbearbeitung hinzugefügt, und das Prompt-Dokument hält dies als Post-Schritt fest, statt den Generator um Textsatz zu bitten
- **SOLLTE [SHOULD]** eine Light-Mode- und eine Dark-Mode-Prompt-Variante erzeugen, wann immer das Asset gegen beide Flächen rendert, und die Dark-Variante durch erneutes Ziehen der Dark-Mode-Brand-Tokens ableiten statt durch Invertieren der Light-Mode-Farben
- **SOLLTE [SHOULD]** Skalierbarkeits-Hinweise für größensensitive Asset-Typen (Icons, Favicons, Badges) einschließen: kleinste Zielgröße notieren und was zu vereinfachen ist, damit das Motiv lesbar bleibt

### Prompt-Dokument-Ausgabe

- **MUSS [MUST]** ein Markdown-Prompt-Dokument pro angefordertem Asset schreiben; der Wert des Agents ist das dauerhafte Artefakt auf der Platte, nicht eine reine Chat-Antwort
- **MUSS [MUST]** Prompt-Dokumente unter einem einzelnen konfigurierbaren Design-Prompts-Verzeichnis schreiben, per Default `design/prompts/` im Konsumenten-Repository, und **DARF NICHT [MUST NOT]** den Pfad irgendeines Projekts hartcodieren (der projektlokale Vorgänger schrieb nach `spec/design/`, was nicht portierbar ist)
- **MUSS [MUST]** das konfigurierte Design-Prompts-Verzeichnis anlegen, falls es nicht existiert (es ist ein Ausgabe-Ort, keine Vorbedingung), und **DARF NICHT [MUST NOT]** Prompt-Dokumente unter dem `docs/`-Baum ablegen, der für publizierte zielgruppengerichtete Seiten reserviert ist
- Es wird kein separates Vor-Generierungs-Ledger gepflegt; das Pro-Asset-Dokument (plus das untenstehende Batch-Index-Dokument) ist der dauerhafte Vor-Generierungs-Record. Das Post-Generierungs-`brand-prompt-library.md` bleibt im Besitz von `corporate-design-colors`
- **MUSS [MUST]** jedes Dokument `<asset-type>_<slug>.md` benennen, wobei `<asset-type>` einem dokumentierten Typ-Vokabular entstammt (zum Beispiel `app-icon`, `logo`, `nav-icon`, `illustration`, `empty-state`, `onboarding`, `hero`, `badge`, `pattern`, `diagram`) und `<slug>` eine kebab-case-Beschreibung ist (dieses Asset-Typ-Vokabular ist hier provisorisch normativ; falls `spec/design/imagery-style/` landet, besitzt sie nicht-farbliche Bild-Achsen wie Komposition und Beleuchtung, und die beiden Specs klären, ob das Dateinamen-Typ-Vokabular migriert oder bleibt—siehe §Offene Fragen)
- **MUSS [MUST]** in jedes Dokument aufnehmen: den Asset-Typ, den Zielgenerator, die beabsichtigten Varianten (light/dark/neutral), die Zielmaße und das Dateiformat, die copy-paste-fertigen Prompt-Blöcke und eine Nachbearbeitungs-Checkliste (zum Beispiel „Hintergrund via `png-to-transparent-svg` entfernen", „skalieren und Lesbarkeit bei 48 px prüfen")
- **MUSS [MUST]** den Seed-Slot festhalten (auch wenn leer/`unset`) sowie den verwendeten Style-Referenz-Identifier, sodass ein späteres Neu-Generieren-mit-Anpassung reproduzierbar ist
- **SOLLTE [SHOULD]**, wenn ein einzelnes Briefing mehrere Assets anfordert, ein Index-Dokument schreiben und Cross-Asset-Visuell-Konsistenz (gleiches Stilregister, Strichstärke, Farbverteilung, Perspektive) über den Batch erzwingen
- **SOLLTE [SHOULD]** den Prompt-Body frei von projektinternem Jargon halten, den ein Generator nicht parsen kann; das Motiv in konkreten visuellen Begriffen beschreiben

### Schreib-Effekte und Tool-Oberfläche

- **MUSS [MUST]** Schreibvorgänge auf Markdown-Prompt-Dokumente unter dem konfigurierten Design-Prompts-Verzeichnis beschränken; der Agent **DARF NICHT [MUST NOT]** Quellcode, Theme-Tokens, das Brand-Bundle, `brand-vocabulary.md` oder ein Bild-Asset modifizieren
- **MUSS [MUST]** das Brand-Bundle, `brand-vocabulary.md`, Theme-Tokens und jedes Style-Referenz-Asset als Read-only-Eingaben behandeln
- **DARF NICHT [MUST NOT]** Netzwerkzugriff erfordern; Prompt-Autorenschaft ist eine lokale Lese-und-Schreib-Operation, und der eigentliche Generierungs-Aufruf ist ein separates nachgelagertes Tool

## Akzeptanzkriterien

- [ ] Den Agent für ein Asset zu briefen erzeugt genau ein Markdown-Prompt-Dokument unter dem konfigurierten Design-Prompts-Verzeichnis (Default `design/prompts/`), benannt `<asset-type>_<slug>.md`
- [ ] Der autorisierte Prompt assembliert die vier Slots in der vorgeschriebenen Reihenfolge (Style-Referenz, deskriptive Phrasen, Hex-Verstärkung, Seed), und die deskriptiven Phrasen lassen sich alle auf Einträge im `brand-vocabulary.md` des Konsumenten-Repositorys zurückführen
- [ ] Den Agent in einem Repository ohne publiziertes Brand-Bundle oder `brand-vocabulary.md` aufzurufen stoppt mit einem klaren „missing brand source"-Report und schreibt kein Prompt-Dokument mit erfundenen Farben
- [ ] Jedes Prompt-Dokument benennt genau einen Zielgenerator und verwendet dessen Prompt-Syntax
- [ ] Jedes Prompt-Dokument enthält eine Negativ-Prompt-/Vermeidungs-Klausel und eine Nachbearbeitungs-Checkliste und hält den Seed-Slot sowie den Style-Referenz-Identifier fest
- [ ] Ein Light/Dark-Asset erzeugt zwei Prompt-Varianten, deren Farben pro Modus neu gezogen werden (nicht RGB-invertiert)
- [ ] Ein Multi-Asset-Briefing erzeugt ein Index-Dokument, und die Pro-Asset-Prompts teilen ein visuelles Register
- [ ] Der Agent schreibt nur Markdown unter dem Design-Prompts-Verzeichnis; statische Inspektion zeigt keine Edits an Quellcode, Tokens, dem Brand-Bundle oder Bild-Assets und keinen hartcodierten Einzelprojekt-Pfad oder eine -Palette im Agent-Body
- [ ] Der Agent deklariert das minimale Tool-Set (Lesen + Schreiben + Suche) ohne Ausführungs- oder Netzwerk-Tools und zitiert diese Spec in seinem Body oder seiner `description`

## Referenzen

- [R1] AI image color contract, deskriptives Farbvokabular, Style-Referenz und Prompt-Assemblierungs-Reihenfolge: `spec/design/corporate-design-colors/` §AI image color contract
- [R2] Nachgelagertes Bildgenerierungs-Tool (Prompt rein, Bilddatei raus): `spec/tools/image-generation/`
- [R3] Nachbearbeitung für Transparenz-Reinigung und Vektorisierung: `spec/design/png-to-transparent-svg/`
- [R4] Agent-Autoren-Regeln, denen dieser Agent entspricht: `spec/claude/agent-management/`
- [R5] Skill-vs-Agent-Entscheidungsregel und Rationale-Abschnitts-Anforderung: `spec/claude/skill-vs-agent/`
- [R6] FLUX-Generierungs-Grundlage auf Modellebene (die Prompting-Regeln und harten Invarianten für FLUX-Ziele): `spec/design/flux-image-generation/`
- [R7] Gemini-Generierungs-Grundlage auf Modellebene (die Prompting-Regeln und harten Invarianten für Gemini-Ziele): `spec/design/gemini-image-generation/`

## Offene Fragen

_Alle offenen Fragen sind aufgelöst. Das pro-Modell-Style-Referenz-Äquivalent wird von `corporate-design-colors` §AI image color contract festgelegt, der ein festes kanonisches Referenzbild vorschreibt (keinen Freitext-Stil-Absatz); da `brand-primary` nun entschieden ist (`oklch(0.47 0.12 276)` / `#4A529D`), konsumiert diese Spec jenen Vertrag direkt. Das Asset-Typ-Vokabular-Deferral wurde am 2026-06-06 entschieden. Der vollständige Eintrag ist in der Git-Historie erhalten (Entscheidungslog, 2026-06-06)._
