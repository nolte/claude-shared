# Corporate Design — Farbsystem

Status: draft

## Kontext

Jedes Artefakt, das dieses Portfolio veröffentlicht — Web-Anwendungen, Doku-Sites, Blog-Posts, README-Badges, Mermaid-Diagramme und KI-generierte Hero-Bilder — muss als Teil einer einzigen wiedererkennbaren Marke gelesen werden. Farbe ist die tragende Achse dafür: Wer eine Release-Notes-Seite überfliegt, ein Hero-Bild über einem Marketing-Post sieht und ein Mermaid-Sequenzdiagramm in einer Spec liest, muss noch vor dem ersten Text wahrnehmen, dass alles zur selben Produktfamilie gehört. Diese Spec regelt genau diese Farb-Achse: Sie legt eine einzige Master-Marke fest, kodifiziert, wie komplementäre, split-komplementäre, analoge und tertiäre Farbtöne dazu in Beziehung stehen, und macht das Ergebnis zu einem portierbaren Token-Set, das menschliche Autorinnen und Autoren ebenso konsumieren wie Claude-gesteuerte Skills und Agents.

Die Spec ist bewusst eng gehalten: Sie betrifft ausschließlich Farbe. Typografie, Spacing, Iconography, Bildkomposition und Voice liegen explizit außerhalb des Scopes und werden später als Geschwister-Specs unter `spec/design/` landen. Die hier definierte Arbeit ist die tragende Vorbedingung dieser Folge-Specs, deshalb muss sie für sich allein verteidigbar sein und den Token-Kontrakt liefern, in den die späteren Specs einklinken.

Adressaten: Brand-Implementierende, die die konkreten OKLCH-Werte wählen; Skill- und Agent-Autorinnen, die Token-Bundles, Mermaid-Themes, README-Badges oder KI-Hero-Bilder erzeugen; sowie Reviewer, die prüfen, ob nachgelagerte Artefakte mit der veröffentlichten Palette konform sind.

## Ziele

- Eine einzige Master-Marke regelt jedes nolte/*-Repository; keine projektweisen Sub-Brand-Forks
- Farb-Entscheidungen sind reproduzierbar über drei Artefakt-Klassen hinweg (Web/Docs-UI, KI-Hero-Bilder, ergänzende Visuals wie Badges und Diagramme)
- Komplementäre, split-komplementäre und tertiäre Hue-Beziehungen sind explizit benannt, nicht implizit dem Operator-Geschmack überlassen
- WCAG 2.2 AA Kontrast ist die durchgesetzte Basis; APCA-Lc-Schwellen fahren als forward-kompatibles Quality-Gate mit
- Das veröffentlichte Token-Set übersteht die Aufnahme durch CSS, Tailwind v4, Figma, Mermaid und Style Dictionary ohne plattformspezifische Divergenz
- KI-Bild-Generierung reproduziert die Marken-Farb-Signatur deterministisch genug, dass zwei Heroes, die Monate auseinander generiert wurden, weiterhin als dieselbe Marke gelesen werden

## Nicht-Ziele

- Typografie, Spacing-Skala, Iconography, Bildkomposition, Motion und Voice (jeweils eine eigene `spec/design/…`-Schwester-Spec)
- Projekt-spezifische Sub-Brand-Systeme, White-Label-Theming, End-Anwender-Theme-Customisation
- Marketing-kreative Richtung über die Farb-Signatur hinaus (Illustrations-Stil, Foto-Behandlung gehören in eine künftige Imagery-Spec)
- Wahl des Build-Werkzeugs für die Token-Export-Pipeline (das *Format* ist normativ, der *Builder* nicht)

## Anforderungen

### Farbraum und Quelle der Wahrheit

- **MUSS [MUST]** jedes primitive Farb-Token in `oklch(L C H)`-Notation speichern; OKLCH ist die kanonische Quelle, hex und sRGB sind abgeleitete Ausgaben ([Tailwind v4 Release Notes — OKLCH-Default](https://tailwindcss.com/blog/tailwindcss-v4), [Evil Martians — OKLCH in CSS](https://evilmartians.com/chronicles/oklch-in-css-why-quit-rgb-hsl))
- **DARF NICHT [MUST NOT]** HSL oder HSV als kanonischen Farbraum verwenden, weil HSL-Lightness nicht wahrnehmungs-uniform ist — identische L-Werte über verschiedene Hues hinweg ergeben sichtbar unterschiedliche Helligkeitseindrücke ([Evil Martians — OKLCH in CSS](https://evilmartians.com/chronicles/oklch-in-css-why-quit-rgb-hsl), [CSS-Tricks — `oklch()`](https://css-tricks.com/almanac/functions/o/oklch/))
- **MUSS [MUST]** jedes primitive Token sowohl mit seinem kanonischen OKLCH-Tripel als auch mit dem gerundeten sRGB-Hex-Äquivalent dokumentieren, damit nachgelagerte Konsumenten ohne OKLCH-Unterstützung regelkonform bleiben
- **SOLLTE [SHOULD]** jedes semantische Token gegen die drei verbreiteten Color-Vision-Deficiency-Profile (Protan, Deutan, Tritan) mit Adobe Leonardo oder einem äquivalenten CVD-fähigen Generator simulieren, bevor das Token in den kanonischen Stand überführt wird ([adobe.design — Leonardo](https://adobe.design/toolkit/leonardo))

### Token-Architektur

- **MUSS [MUST]** Tokens in drei Schichten organisieren, in dieser Reihenfolge: `primitive` (rohe OKLCH-Ramp-Stufen, nur hue-benannt), `semantic` (rollen-benannt, z. B. `color.background.surface`, `color.text.primary`) und `component` (nur wenn eine komponenten-spezifische Entscheidung sich tatsächlich nicht semantisch ausdrücken lässt) ([Atlassian Design Tokens](https://atlassian.design/foundations/tokens/design-tokens), [IBM Carbon — Color Overview](https://carbondesignsystem.com/elements/color/overview/), [Contentful — Design Token System](https://www.contentful.com/blog/design-token-system/))
- **MUSS [MUST]** semantische Tokens nach Rolle und Kontext benennen, niemals nach Hue oder numerischer Stufe (`color.surface.elevated` ist erlaubt; `color.indigo.500` ist auf der semantischen Schicht verboten)
- **DARF NICHT [MUST NOT]** ein primitives Token direkt aus Anwendungscode konsumieren; Konsumenten referenzieren semantische (oder component-) Tokens, niemals Primitives
- **SOLLTE [SHOULD]** die semantische Schicht so flach halten, dass jedes neue Token in einer Bildschirmansicht prüfbar ist; überschreitet die semantische Schicht ~120 Tokens, vorher nach Sub-Domain aufteilen (`color.text.*`, `color.background.*`)
- **MUSS [MUST]** denselben semantischen Token-Namen als mode-auflösend behandeln: `color.background.surface` resolviert in Light- bzw. Dark-Mode zu unterschiedlichen OKLCH-Werten, der Name bleibt einer ([Primer — Color usage](https://primer.style/foundations/color/), [Radix — Dark mode](https://www.radix-ui.com/themes/docs/theme/dark-mode))

### Brand-Harmonie-Achsen

Das Brand-Identitäts-Vokabular definiert vier Slot-Namen: `brand-primary`, `brand-secondary`, `brand-accent` und `brand-complement`. Alle vier werden aus einem einzigen Anker (`brand-primary`) über die pro Slot unten festgelegte geometrische oder funktionale Beziehung abgeleitet. `brand-tertiary` ist ein optionaler funktionaler Hue, der als separater MAY-Slot unten definiert ist und nicht zum Vier-Slot-Brand-Identitäts-Vokabular gehört. Operator-Entscheidungen sind auf die pro Slot beschriebenen Beziehungen beschränkt.

- **MUSS [MUST]** genau einen `brand-primary`-Hue definieren. Die Primary-Key-Color ist die einzige wiedererkennbare Signatur des Portfolios und wechselt nie pro Repository
- **MUSS [MUST]** die `brand-secondary`-Achse entweder als **split-komplementär** (Hue von `brand-primary` ± 30° vom 180°-Komplement, zwei Winkel) oder als **analog** (Hue von `brand-primary` ± 30°) definieren. Echtes 180°-Komplement ist als Marken-Sekundärfarbe verboten, weil es auf großen Flächen Augen-Belastung erzeugt und sich für Body-Text nur schwer einsetzen lässt ([Figma — Complementary Colors](https://www.figma.com/resource-library/what-are-split-complementary-colors/), [Sketch — Color Combination Guide](https://www.sketch.com/blog/color-combination-guide/))
- **KANN [MAY]** einen `brand-tertiary`-Hue einführen — einen optionalen funktionalen Hue außerhalb des Vier-Slot-Brand-Identitäts-Vokabulars —, der per +60°-Hue-Rotation von `brand-primary` bei Tone 40 abgeleitet wird, wobei das Chroma auf den Peak gesetzt wird, den der Gamut des +60°-Hues zulässt, gemäß §Ramp-Struktur (nicht auf einen festen numerischen Chroma-Wert). Das folgt der Material-3-Tertiary-Ableitungsgeometrie, aber Material 3s Chroma 24 ist nur ein nicht-bindender Ausgangsanker, den die Peak-Chroma-pro-Gamut-Regel überschreibt. Genutzt wird dies, wenn Diagramme, Illustrationen oder Marketing tatsächlich eine dritte funktionale Achse brauchen ([Material 3 — Color roles](https://m3.material.io/styles/color/roles), [Material Color Utilities — dynamic color scheme](https://github.com/material-foundation/material-foundation-material-color-utilities))
- **KANN [MAY]** das echte 180°-Komplement von `brand-primary` ausschließlich als **punktuellen Akzent** nutzen (Einzelelement-Emphasis: Chart-Highlight, Callout-Band, CTA auf einer wenig-gesättigten Fläche). Es DARF NICHT zu Body, Surface, großen flachen Füllungen oder Lauftext heraufgestuft werden
- **MUSS [MUST]** Vokabular-Hygiene bewahren. Vier Slots sind definiert, und kein anderer Slot-Name ist in Skills, Agents oder nachgelagerter Doku zulässig:
  - `brand-primary`: einzelner Identitäts-Hue (einer pro Portfolio)
  - `brand-secondary`: die harmonische Achse, die nach der Regel oben aus Primary abgeleitet wird (`split-complementary` oder `analog`)
  - `brand-accent`: ausschließlich funktionale Emphasis (CTA, Active-State); darf nicht zu Surface, Body oder großen flachen Füllungen hochgestuft werden
  - `brand-complement`: echtes 180°-Komplement von Primary, beschränkt auf Chart- und Illustrations-Akzente

  Skills, Agents und nachgelagerte Doku MÜSSEN diese vier Begriffe mit dieser präzisen Bedeutung verwenden und DÜRFEN KEINEN fünften Brand-Identitäts-Slot-Namen einführen. `brand-tertiary` ist der einzige zulässige Name außerhalb dieser Vier-Menge und wird durch die Regel zum optionalen funktionalen Hue oben geregelt ([Vercel Geist — Colors](https://vercel.com/geist/colors), [Supabase — Color usage](https://supabase.com/design-system/docs/color-usage))

### Ramp-Struktur

- **MUSS [MUST]** jede chromatische Ramp (primary, secondary, tertiary, danger, success, warning, info) als 12-stufige Skala mit der folgenden funktionalen Slot-Zuordnung nach Radix' Palette-Composition erzeugen ([Radix — Understanding the Scale](https://www.radix-ui.com/colors/docs/palette-composition/understanding-the-scale)):

  | Stufen | Rolle                                                                |
  | ------ | -------------------------------------------------------------------- |
  | 1–2    | App-Hintergrund (Seitenfläche; dezente Fläche)                       |
  | 3–5    | Component-Hintergrund, Hover-State, Active-/Pressed-State            |
  | 6–8    | Borders, Trennlinien, Focus-Ringe                                    |
  | 9      | Solid (Peak-Chroma; Brand-Fill, Primary-Button-Hintergrund)          |
  | 10     | Solid-Hover                                                          |
  | 11     | Niedrig-kontrastierter, barrierefreier Text auf Stufe 1/2            |
  | 12     | Hoch-kontrastierter, barrierefreier Text / Iconography auf Stufe 1/2 |

- **MUSS [MUST]** die Neutral-Ramp (`neutral.1` … `neutral.12`) mit Chroma ≤ 0,01 in OKLCH erzeugen, damit die Marke durchgängig als eine warme oder eine kühle Familie gelesen wird; gemischte Neutrals sind verboten
- **MUSS [MUST]** Stufe 9 jeder chromatischen Ramp am Peak-Chroma halten, das der Gamut des jeweiligen Hues zulässt, nicht an einem uniformen numerischen Chroma-Wert, weil OKLCH-Gamut-Clipping pro Hue variiert
- **SOLLTE [SHOULD]** Stripes Step-Distanz-Heuristik als Quick-Kontrast-Check vor der exakten Ratio-Messung anwenden: zwei Stufen derselben Ramp ≥ 5 Stufen auseinanderpaaren für Text-auf-Hintergrund und ≥ 4 Stufen für Icon-auf-Hintergrund oder Large-Text-auf-Hintergrund ([Stripe — Accessible Color Systems](https://stripe.com/blog/accessible-color-systems)). Die Heuristik lockert die WCAG-Gates aus §Kontrast-Gates nicht; Heuristik-Fehlschlag bei bestandenem WCAG ist legal, die Heuristik ist nur ein schneller Vorfilter

### Light-/Dark-Mode-Kopplung

- **MUSS [MUST]** jedes semantische Token sowohl in `light`- als auch in `dark`-Modus-Varianten ausliefern; Dark-Mode ist nicht optional
- **MUSS [MUST]** den Dark-Mode-`brand-primary`-Solid (Stufe 9 im Dark) aus dem Light-Mode-Bereich der Stufen 4–6 ableiten (niedrigeres Chroma, höhere Lightness), nicht durch HSL- oder RGB-Invertierung des Light-Mode-Werts ([Material — Dark theme](https://design.google/library/material-design-dark-theme), [Inkbot Design — Dark Mode](https://inkbotdesign.com/dark-mode/))
- **DARF NICHT [MUST NOT]** pures `#000000` (`oklch(0 0 0)`) als Dark-Mode-Root-Surface verwenden; die dunkelste erlaubte Fläche ist `oklch(0.16 0 <hue>)` oder heller (≈ Materials `#121212`-Basis), wobei der Neutral-Hue in die Dark-Surface übernommen wird, damit die Brand-warme-oder-kühle Signatur konsistent bleibt ([Material — Dark theme](https://design.google/library/material-design-dark-theme), [Webheads United — Dark mode palette principles](https://webheadsunited.com/guide-to-dark-mode-color-palette-principles/))
- **SOLLTE [SHOULD]** beide Modi aus einem parametrischen Algorithmus ableitbar halten (eine OKLCH-Lightness-Kurve pro Modus), damit das Hinzufügen einer neuen chromatischen Ramp ein ausbalanciertes Light/Dark-Paar erzeugt, ohne dass jede Stufe einzeln tunbar sein muss

### Kontrast-Gates

Die veröffentlichte Palette MUSS diese Gates auf der semantischen Token-Schicht bestehen, nicht nur auf der primitiven.

- **MUSS [MUST]** WCAG 2.2 AA SC 1.4.3 *Contrast (Minimum)* erfüllen: 4,5:1 für Normaltext, 3:1 für Large-Text (≥ 18pt regular oder ≥ 14pt bold), paarweise auf jeder semantischen Text-auf-Hintergrund-Kombination, die das Designsystem als legal deklariert ([W3C — SC 1.4.3](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html))
- **MUSS [MUST]** WCAG 2.2 AA SC 1.4.11 *Non-text Contrast* erfüllen: 3:1 für UI-Component-State-Visuals (Focus-Ringe, Active-State-Borders, Form-Control-Outlines) und für grafische Objekte, die zum Verständnis nötig sind (Chart-Füllungen, Icon-only-Buttons), gegen die angrenzende Farbe ([W3C — SC 1.4.11](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html))
- **DARF NICHT [MUST NOT]** Kontrast-Werte aufrunden, um die Schwelle zu treffen; ein gemessenes 4,49:1 verfehlt 4,5:1
- **SOLLTE [SHOULD]** zusätzlich gegen APCA-Lc-Schwellen prüfen, um WCAG 3.0 vorzubereiten: Body-Text Lc ≥ 75, Microcopy Lc ≥ 90, große Headlines Lc ≥ 60. APCA-Fehlschläge zählen als `SHOULD-fail`, nicht als `MUST-fail`, bis APCA normativ wird ([APCA in a Nutshell](https://git.apcacontrast.com/documentation/APCA_in_a_Nutshell.html), [Radix — Understanding the Scale](https://www.radix-ui.com/colors/docs/palette-composition/understanding-the-scale))
- **KANN [MAY]** Marken-Wordmark, Logo-Glyphen und dekorative Hero-Bilder per WCAG-SC-1.4.3-Logotype-Ausnahme von den Kontrast-Gates ausnehmen; funktionale UI-Komponenten (Buttons, Links, Form-Controls, bedeutungstragende Icons) MÜSSEN die obigen Gates dennoch erfüllen ([W3C — SC 1.4.3](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html))

### Kompositions-Heuristik (60-30-10)

- **SOLLTE [SHOULD]** eine 60 % Neutral-Fläche / 30 % `brand-secondary` / 10 % `brand-accent` als Ausgangspunkt für Hero-Kompositionen, Marketing-Seiten und dicht belegte UI-Ansichten anwenden und nur mit dokumentierter Begründung abweichen. Die 60-30-10-Regel ist ein aus der Innenarchitektur auf UI übertragenes Erfahrungsmuster, keine normativ bewiesene Invariante, deshalb bleibt sie SOLLTE und wird nie MUSS ([Apartment Therapy — 60-30-10 explained](https://www.apartmenttherapy.com/interior-design-rule-60-30-10-explained-37504313))

### Anwendung pro Artefakt

Jede Artefakt-Klasse bindet an die semantische Token-Schicht. Skills und Agents, die diese Artefakte erzeugen, lesen semantische Tokens, niemals Primitives oder Component-Tokens.

- **MUSS [MUST]** das semantische Token-Set in Web-Anwendungen und Doku-Sites über CSS Custom Properties oder Framework-natives Theming konsumieren (Tailwind v4 `@theme`-Block, MUI `createTheme`, Mantine-Theme-Objekt, shadcn/ui `:root`-Block) ([shadcn/ui — Theming](https://ui.shadcn.com/docs/theming), [Tailwind v4 Release Notes](https://tailwindcss.com/blog/tailwindcss-v4))
- **MUSS [MUST]** ein Mermaid-Theme-Mapping publizieren, das die Mermaid-Theme-Variablen (`primaryColor`, `primaryTextColor`, `primaryBorderColor`, `lineColor`, `secondaryColor`, `tertiaryColor`, `background`, `mainBkg`, `secondBkg`, `tertiaryBkg`) auf semantische Tokens auflöst, damit Diagramme in MkDocs und READMEs die Marke ohne pro-Diagramm-Styling erben
- **MUSS [MUST]** das Mermaid-Theme-Mapping als **Light-/Dark-Paar** publizieren, gebunden an die mode-auflösenden semantischen Tokens (gemäß §Light-/Dark-Mode-Kopplung), niemals als einzelnes mode-agnostisches Theme, weil die Material-Light/Dark-Theme-Bridge, die `spec/project/mermaid-diagrams/` vorschreibt, Theme-Variablen pro Modus austauscht und ein mode-agnostisches Theme das Dark-Mode-Rendering brechen würde
- **MUSS [MUST]** dieses Theme-Mapping über eine einzige globale Konfiguration injizieren (ein MkDocs-Hook oder ein `extra_javascript`-Eintrag, der die Mermaid-Theme-Config einmalig für die gesamte Site setzt), niemals über pro-Diagramm-`%%{init: … }%%`-Overrides; pro-Diagramm-Overrides sind genau das Inline-Styling, das `spec/project/mermaid-diagrams/` verbietet. Die Verdrahtungs-Regel liegt in `spec/project/mermaid-diagrams/` §MkDocs-Setup
- **MUSS [MUST]** alle README-Badge-Farben (`shields.io`-`color=`- und `labelColor=`-Parameter, custom SVG-Badges) als an das semantische Token-Set gebunden behandeln; ad-hoc-Werte wie `color=blue` sind verboten
- **MUSS [MUST]** eine brand-themed Favicon-Palette und eine brand-themed Social-Card-Palette (Open-Graph-Image) versions-fixiert als semantische Tokens halten, damit eine Doku-Seite, ein Blog-Post-Share und eine GitHub-Repo-Card eine Farb-Signatur teilen
- **SOLLTE [SHOULD]** eine Print-/PDF-Fallback-Palette (CMYK-Approximationen der kanonischen OKLCH-Werte) bereitstellen, damit generierte PDFs — Release-Notes, Hand-outs, nach PDF exportierte Slide-Decks — nicht still abdriften
- **MUSS [MUST]**, falls die CMYK-Fallback-Palette gemäß obiger Regel existiert, sie neu erzeugen, sobald sich der kanonische OKLCH-Wert eines gebundenen semantischen Tokens ändert; die CMYK-Konversion ist verlustbehaftet und veraltete Konversionen entkoppeln Print stillschweigend vom Bildschirm

### KI-Bild-Farb-Kontrakt

Dieser Unterabschnitt regelt Hero-Bilder, Social-Cards und jegliche sonstige KI-generierte Bilder. Der Kontrakt muss so eng sein, dass zwei Heroes, die Monate auseinander entstehen, als dieselbe Marke gelesen werden.

- **MUSS [MUST]** einen festen Midjourney `--sref <code>` (oder pro-Modell-Äquivalent) als kanonische Brand-Style-Referenz pflegen, ihn wie ein Token versionieren (benannt, freigegeben, brand-version-getaggt) und im selben Veröffentlichungs-Artefakt wie die Farb-Tokens ablegen ([Midjourney — Style Reference](https://docs.midjourney.com/hc/en-us/articles/32180011136653-Style-Reference), [Numonic — Midjourney brand consistency](https://www.numonic.ai/blog/midjourney-brand-consistency-guide))
- **MUSS [MUST]** das pro-Modell-Äquivalent für Generatoren ohne `--sref`-Mechanismus (zum Beispiel Gemini) als **festes kanonisches Referenzbild** definieren: Image-Conditioning ist das nächste funktionale Analogon zu `--sref` und überlebt Regenerationen, während ein freitextlicher Style-Absatz zwischen Läufen driftet. Dieses Referenzbild MUSS exakt wie der `--sref`-Code versioniert und abgelegt werden. Dieser Contract besitzt das pro-Modell-Äquivalent; konsumierende Specs (zum Beispiel `graphic-prompt-authoring`) **DÜRFEN es NICHT [MUST NOT]** generatorweise neu definieren
- **MUSS [MUST]** jeden brand-bewussten KI-Bild-Prompt in dieser festen Reihenfolge zusammensetzen: (1) der kanonische `--sref <code>`, (2) deskriptive Farb-Phrasen aus dem Brand-Vokabular (z. B. „muted indigo", „warm off-white", „deep neutral charcoal"), (3) der Hex-Wert bzw. die Hex-Werte als finale Reinforcement am Prompt-Ende, (4) ein protokollierter `--seed` für Reproduzierbarkeit ([Midjourney — Style Reference](https://docs.midjourney.com/hc/en-us/articles/32180011136653-Style-Reference), [CometAPI — colors in Midjourney v7](https://www.cometapi.com/how-to-get-specific-colors-in-midjourney-v7/))
- **DARF NICHT [MUST NOT]** sich allein auf Hex-Codes im Prompt-Body verlassen, um Marken-Farbe zu erzwingen; reines Hex-Parsing ist in jedem aktuellen Diffusion-Modell unzuverlässig ([CometAPI — colors in Midjourney v7](https://www.cometapi.com/how-to-get-specific-colors-in-midjourney-v7/), [Skywork — lock brand colors](https://skywork.ai/blog/how-to-lock-brand-colors-prompt-constraints-guide/))
- **MUSS [MUST]** ein `brand-vocabulary.md` pflegen, das die freigegebenen deskriptiven Farb-Phrasen auflistet (die Namen, die ein Diffusion-Modell parsen kann: „muted teal", „cobalt", „warm bone", „deep forest"), gepaart mit dem OKLCH-Tripel, zu dem sie in der kanonischen Palette auflösen; Agents lesen diese Datei beim Komponieren von Prompts
- **MUSS [MUST]** den vollen Prompt-Stack (Modell + Version, `--sref`, Seed, Style-Weight, deskriptive Phrasen, Hex-Reinforcements) für jedes veröffentlichte Hero-Bild in einer versionierten `brand-prompt-library.md` protokollieren, die als eigenständige Datei neben `brand-vocabulary.md` gepflegt wird (eine Zeile pro veröffentlichtem Hero-Bild), damit ein Regenerate-with-Tweaks-Vorgang reproduzierbar bleibt
- **MUSS [MUST]** sowohl `brand-vocabulary.md` als auch `brand-prompt-library.md` unter `design/brand/` im Bundle-Producer-Repository ablegen, parallel zur `design/prompts/`-Konvention, die `spec/design/graphic-prompt-authoring` für Prompt-Dokumente festlegt; der relative Pfad ist normativ, auch wenn die Producer-Repo-Identität noch aussteht (siehe §Offene Fragen, vertagte `brand-primary`-Entscheidung)
- **SOLLTE [SHOULD]** den deskriptiven-Farbnamen-Slot dem Hex-Reinforcement-Slot für Primary-Brand-Farben vorziehen; das Hex-Reinforcement bleibt für den punktuellen Akzent oder für Hues, deren deskriptiver Name mehrdeutig ist ([Numonic — Midjourney brand consistency](https://www.numonic.ai/blog/midjourney-brand-consistency-guide))
- **KANN [MAY]** alternative `--sref`-Codes (oder pro-Modell-Äquivalente) für Sub-Kontexte pflegen (technical-illustration, photographic-product, abstract-marketing) innerhalb einer Brand-Familie; alternative sref-Codes MÜSSEN dasselbe deskriptive Farb-Vokabular teilen, damit die Marken-Signatur den Kontext-Wechsel überlebt

### Veröffentlichung und Export

- **MUSS [MUST]** das kanonische Token-Set im Format der W3C Design Tokens Community Group (DTCG 2025.10 oder neuer) publizieren: `$type: "color"`, `$value`-Objekt mit `colorSpace`, `components`, optional `alpha`, optional `hex`; Gruppen-Referenzen nutzen die `{group.token}`-Curly-Brace-Syntax; zirkuläre Referenzen sind verboten ([DTCG Format Module](https://www.designtokens.org/tr/drafts/format/), [W3C — DTCG first stable announcement](https://www.w3.org/community/design-tokens/2025/10/28/design-tokens-specification-reaches-first-stable-version/))
- **MUSS [MUST]** das kanonische Set mindestens zu (a) CSS Custom Properties unter `:root` und `[data-theme="dark"]`, (b) Tailwind v4 `@theme`-Block, (c) Figma Variables (JSON) und (d) Mermaid-Theme-Variablen aus einem einzigen Build-Step exportieren. Style Dictionary ist der empfohlene Builder; das Build-Werkzeug ist nicht normativ, das Ausgabe-Set ist es ([Style Dictionary — Examples](https://styledictionary.com/getting-started/examples/), [Tokens Studio — Token format](https://docs.tokens.studio/manage-settings/token-format))
- **MUSS [MUST]** das Token-Bundle mit Semantic Versioning versionieren; eine Hue-Änderung an der Primary- oder Secondary-Achse ist ein Major-Bump, eine nicht-wahrnehmbare Reorganisation ein Patch, jede andere Token-Set-Änderung ein Minor-Bump
- **MUSS [MUST]** das veröffentlichte Token-Bundle als portfolio-versioniertes Artefakt ausliefern, das nachgelagerte Repositories pinnen (analog dazu, wie `nolte/vale-style` pro `spec/project/prose-style/` von jedem Prose-lintenden Repo gepinnt wird); ad-hoc-Copy-Paste der Palette in ein Konsumenten-Repo ist verboten

### Governance und Change-Control

- **DARF NICHT [MUST NOT]** eine neue primitive Farb-Stufe einführen, ohne zu verifizieren, dass sie von `brand-primary` über die dokumentierten Hue-Offsets erreichbar ist (0°, ±30°, ±60°, 180°); ad-hoc Hex-Picks per Hue-Intuition sind verboten
- **MUSS [MUST]** jede Änderung an einer chromatischen Ramp durch das Review dieser Spec leiten: der Change-Request benennt die betroffene Ramp, das OKLCH-Delta, die resultierenden Kontrast-Deltas an jeder legalen Text-auf-Hintergrund-Paarung und die resultierenden Lc-Deltas für APCA
- **SOLLTE [SHOULD]** ein Brand-Change-Log innerhalb des veröffentlichten Token-Bundles führen, das jede Major- oder Minor-Änderung mit Begründung und den Kontrast-Deltas zum Zeitpunkt der Änderung dokumentiert
- **DARF NICHT [MUST NOT]** die KI-Bild-`--sref`-Codes still neu ableiten, wenn die Marke aufgefrischt wird; ein sref-Refresh ist ein Major-Bump, weil jedes zuvor erzeugte Hero ab diesem Punkt off-brand ist

## Akzeptanzkriterien

- [ ] Ein `brand-primary`-OKLCH-Tripel ist als kanonisch deklariert, samt Hex-Äquivalent und Gamut-Footprint
- [ ] Die `brand-secondary`-Achse ist entweder als `split-complementary` oder `analog` deklariert, mit expliziten Hue-Offsets und Begründung
- [ ] `brand-tertiary` ist entweder mit der +60°-/Tone-40-/Peak-Chroma-Ableitungsregel deklariert (Material-3-Geometrie, Peak-Chroma gemäß §Ramp-Struktur) oder explizit mit Begründung weggelassen
- [ ] Jede chromatische Ramp hat 12 Stufen mit der Radix-artigen funktionalen Slot-Zuordnung tabellarisch dokumentiert
- [ ] Stufe 9 jeder chromatischen Ramp liegt innerhalb von 2 Chroma-Einheiten an der OKLCH-Gamut-Grenze des jeweiligen Hues (Peak-Chroma-Regel), nicht auf einem uniformen numerischen Chroma-Wert
- [ ] Jede Neutral-Stufe hat OKLCH-Chroma ≤ 0,01
- [ ] Die Vier-Slot-Brand-Identitäts-Vokabular-Tabelle (`brand-primary`, `brand-secondary`, `brand-accent`, `brand-complement`) ist vorhanden, und kein fünfter Brand-Identitäts-Slot-Name taucht im veröffentlichten Bundle oder in dessen Konsumenten-Doku auf; `brand-tertiary` ist unter der Regel zum optionalen funktionalen Hue zulässig und zählt nicht als fünfter Identitäts-Slot
- [ ] Light- und Dark-Mode lösen jedes semantische Token auf; kein semantisches Token ist single-mode
- [ ] Keine Dark-Mode-Surface verwendet `oklch(0 0 0)`
- [ ] Jede legale Text-auf-Hintergrund-Semantic-Paarung hat eine protokollierte WCAG-2.2-AA-Kontrast-Ratio an oder über den SC-1.4.3-/SC-1.4.11-Schwellen, mit dem rohen (un-gerundeten) Messwert erhalten
- [ ] Jede legale Interactive-State-Semantic-Paarung hat einen protokollierten APCA-Lc-Wert; out-of-range-Werte sind als SHOULD-fails mit Remediation-Plan gelistet
- [ ] Das veröffentlichte Token-Bundle validiert gegen das DTCG-2025.10-Schema
- [ ] Das Bundle exportiert sauber zu CSS Custom Properties, Tailwind v4 `@theme`, Figma Variables JSON und einem Mermaid-Theme-Mapping aus einem einzigen Build-Step
- [ ] Ein Favicon-Palette-Token-Set und ein Social-Card-(Open-Graph-Image-)Palette-Token-Set existieren im veröffentlichten Bundle, sind versioniert und binden an semantische Tokens
- [ ] Kein README-Badge in den konsumierenden Portfolio-Repositories verwendet einen literalen Farb-Wert in `shields.io`-`color=`- oder `labelColor=`-Parametern; jede Badge-Farbe führt auf ein semantisches Token im veröffentlichten Bundle zurück
- [ ] Ein kanonischer Midjourney-`--sref`-Code (oder pro-Modell-Äquivalent) ist deklariert, versioniert und aus dem Bundle referenziert
- [ ] Ein `brand-vocabulary.md` existiert, listet jede freigegebene deskriptive Farb-Phrase und paart jede Phrase mit einem semantischen oder primitiven Token
- [ ] Eine versionierte `brand-prompt-library.md` existiert als eigenständige Datei neben `brand-vocabulary.md` und führt pro veröffentlichtem Hero-Bild einen Eintrag mit Modell+Version, `--sref`, Seed, Style-Weight, deskriptiven Phrasen und Hex-Reinforcements
- [ ] Das veröffentlichte Bundle wird von mindestens einem nachgelagerten Repository über einen gepinnten Versions-Pointer konsumiert (kein Copy-Paste)
- [ ] Jeder gemergte PR, der ein Token einer chromatischen Ramp ändert, trägt im PR-Body die betroffene Ramp, das OKLCH-Delta, die Kontrast-Deltas an jeder legalen Text-auf-Hintergrund-Paarung und die Lc-Deltas für APCA
- [ ] Für jeden Major- oder Minor-Brand-Versions-Bump existiert ein Change-Log-Eintrag mit den Kontrast- und Lc-Deltas zum Zeitpunkt der Änderung

## Offene Fragen

- **[vertagt — entschieden, Ziel gebunden]** Das genaue `brand-primary`-OKLCH-Tripel (Hue, Chroma, Lightness) ist auf die erste konkrete Implementierungs-Skill oder -Agent vertagt — am ehesten die von `spec/design/graphic-prompt-authoring` geregelte — und ist eines der deklarierten Outputs dieser Skill; diese Spec definiert nur den *Kontrakt*, den der gewählte Wert erfüllen muss, was hier ihre vollständige Aufgabe ist. Der objektiv korrekte Wert lässt sich aus keinem bestehenden Artefakt ableiten, deshalb muss ihn ein menschlicher Brand-Owner wählen. Empfohlener, nicht-bindender Ausgangsanker: ein gedämpftes Indigo (das deskriptive Beispiel, das in §KI-Bild-Farb-Kontrakt bereits zweimal verwendet wird), das gute Gamut-Reserve für die +60°-/180°-Ableitungen bietet und als glaubwürdige Signatur eines Technik-Portfolios gelesen wird. Nachgelagerte Skills und Agents, die vom gewählten Wert abhängen, können bis zum Vorliegen des entscheidenden Artefakts keine konforme Ausgabe erzeugen; die Abhängigkeit ist explizit, nicht implizit.
- **[Cross-Spec-Lücke]** Der "portfolio-versionierte Token-Bundle"-Pinning-Mechanismus ist hier per Analogie zu `nolte/vale-style` benannt, aber keine Spec definiert die Publication-Registry, das veröffentlichte Datei-Format oder die Konsumenten-seitige Pin-Syntax. Zwei vorgelagerte Ereignisse, in dieser Reihenfolge, lösen die Blockade: (1) ein Brand-Owner wählt `brand-primary` (die erste vertagte Offene Frage dieser Spec), was (2) die Auswahl eines Bundle-Producer-Repos und das erste veröffentlichte DTCG-Bundle freischaltet. `spec/portfolio/design-token-distribution/` (oder ein neuer Abschnitt in `release-automation`) wird erst geschrieben, sobald dieses Producer-Repo existiert und ein getaggtes Bundle veröffentlicht ist. `release-automation` §Nicht-Ziele schließt External-Registry-Publishing explizit aus, sodass dies sich nicht so wie es ist in die bestehende Release-Pipeline einfügen lässt. Bis dahin MÜSSEN nachgelagerte Konsumenten die Veröffentlichung und das Pinning mit den Eignerinnen und Eignern dieser Spec abstimmen.
- Default: Die CMYK-Fallback-Palette-Generierung bleibt `SHOULD`, solange nur Screen-Artefakte ausgeliefert werden; der bedingte Regenerate-on-Change-`MUST` in §Anwendung pro Artefakt begrenzt das Drift-Risiko bereits. Neu bewerten, wenn: Hochstufung auf `MUST` mit einem dokumentierten ICC-Konversions-Profil-Pin (zum Beispiel ein benanntes Profil wie ISO Coated v2 / FOGRA39), sobald ≥ 1 Print-/PDF-Deliverable pro Release-Zyklus über ≥ 2 Portfolio-Repos hinweg ausgeliefert wird oder ein Brand-Owner einen beobachteten CMYK-Farb-Drift-Defekt auf einem ausgelieferten Print-Artefakt meldet.
- Der Übergabe-Kontrakt mit einer künftigen `spec/design/imagery-style/` für nicht-farbliche Bild-Achsen wartet auf diese Spec. Beim Verfassen von `spec/design/imagery-style/` unter `spec/design/` wird hier eine reziproke Übergabe-Klausel ergänzt (die Farb-Achse bleibt im Eigentum von `corporate-design-colors`; alle nicht-farblichen Bild-Achsen liegen im Eigentum von `imagery-style`) sowie ein passender Verweis in `imagery-style`. Vorgelagerter Marker: `spec/design/` enthält derzeit nur `corporate-design-colors` und `graphic-prompt-authoring`, sodass `imagery-style` noch nicht existiert; bis sie landet, trägt der KI-Bild-Farb-Kontrakt hier allein.
