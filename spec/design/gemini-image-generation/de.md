# Gemini-Bildgenerierung

Status: draft

## Kontext

Googles natives Gemini-Bildmodell — `gemini-3.1-flash-image` („Nano Banana 2") — ist der Pfad des Portfolios, wenn ein Asset Gemini-spezifische Stärken braucht: lesbaren Text im Bild, konversationelles Multi-Turn-Editing und Multi-Image-Komposition. Es wird über den `gemini`-Provider des `image-generation`-Tools erreicht. Gemini ist nativ multimodal und auf tiefem Sprachverständnis gebaut und belohnt daher — wie FLUX, anders als SDXL — erzählende, beschreibende Prosa statt komma-separierter Tag-Listen. Es geht weiter: Es belohnt zusätzlich eine genannte Absicht bzw. einen Zweck und versteht mehrstufige Anweisungen innerhalb eines einzelnen Prompts. Einen Gemini-Prompt wie eine FLUX- oder SDXL-Tag-Liste zu behandeln lässt Qualität liegen.

Ein Prompt ist nicht modellportabel: Derselbe String liefert über FLUX, Gemini und Imagen hinweg materiell unterschiedliche Ergebnisse, daher müssen Prompts auf das Zielmodell optimiert werden. Diese Spec ist die Gemini-Hälfte dieses Vertrags; `spec/design/flux-image-generation/` ist die FLUX-Hälfte.

Diese Spec ist die **Generierungs-Grundlage auf Modellebene** für Gemini: die verifizierten Prompting-Praktiken und die harten Invarianten, die jeden Gemini-Bildaufruf binden. Sie wird konsumiert von `spec/design/graphic-prompt-authoring/` (das brand-konforme Prompts zusammensetzt und den gewählten Generator korrekt adressieren muss) und von `spec/tools/image-generation/` (dessen `gemini`-Provider `gemini-3.1-flash-image` aufruft). Sie besitzt **nicht** den Brand-Farbvertrag (`corporate-design-colors`), die Tool-Mechanik (`image-generation`) oder das Prompt-Dokument-Format (`graphic-prompt-authoring`); sie liefert die Modell-Fakten, auf denen diese Specs aufbauen.

Leser: Prompt-Autoren und Skill-/Agent-Autoren, die Gemini adressieren; Betreiber, die die Generierung tunen; Reviewer, die prüfen, dass Gemini-Aufrufe Geminis Stärken nutzen statt portierter FLUX- oder SDXL-Gewohnheiten.

## Ziele

- Eine verifizierte Grundlage für optimales Prompting mit dem nativen Gemini-Bildmodell, abgegrenzt von der FLUX-Grundlage.
- Die Stärken des Modells (Bild-Text, konversationelles Editing, Multi-Image-Komposition) und seine harten Caveats (kein Negative-Prompt-Parameter, immer aktives SynthID-Wasserzeichen, Billing) einmal festgeschrieben, dort, wo sowohl die Prompt-Authoring-Spec als auch das Tool sie zitieren können.
- Eine klare Grenze zwischen dem geregelten Modell (`gemini-3.1-flash-image`), seinen Pro- und Lite-Geschwistern (`gemini-3-pro-image`, `gemini-3.1-flash-lite-image`) und Imagen, damit stufenspezifische Limits nicht falsch angewendet werden.

## Nicht-Ziele

- Das Brand-Farbsystem, das deskriptive Farbvokabular und der Style-Reference-Vertrag — Eigentum von `spec/design/corporate-design-colors/`.
- Tool-Mechanik (CLI, Provider-Auswahl, Sidecar, Credentials) — Eigentum von `spec/tools/image-generation/`.
- Prompt-Dokument-Format und Brand-Sourcing — Eigentum von `spec/design/graphic-prompt-authoring/`.
- Nicht-Gemini-Modelle (FLUX, SDXL) — Eigentum von `spec/design/flux-image-generation/` und etwaigen Geschwistern.
- Imagen (`imagen-*`): eine andere Modellfamilie mit anderen Limits (480-Token-Prompt, Text auf rund 25 Zeichen begrenzt); die Tool-Spec verdrahtet es unerreichbar, und es wird hier nur als Grenze referenziert, damit seine Limits nicht auf das native Gemini-Modell angewendet werden.
- Die Geschwister-Stufen `gemini-3-pro-image` („Nano Banana Pro": Reasoning-Kern, Studio-4K für Layout und Typografie) und `gemini-3.1-flash-lite-image` („Nano Banana 2 Lite": sehr niedrige Latenz zu geringeren Kosten) als Generierungsziel; sie werden nur als Grenze genannt, damit ihre Limits und Preise nicht auf das geregelte Modell angewendet werden.

## Anforderungen

### Modellwahl
- **MUSS [MUST]** `gemini-3.1-flash-image` („Nano Banana 2") als das Modell behandeln, das diese Grundlage regelt; das `image-generation`-Tool verdrahtet genau diese ID.
- **MUSS [MUST]** die stabile ID verdrahten, niemals `gemini-3.1-flash-image-preview`. Googles Deprecation-Tabelle nennt die Preview-ID als Nachfolger von `gemini-2.5-flash-image` ([E8]), während der Modellkatalog `gemini-3.1-flash-image` als stabil führt ([E9]); eine Preview-ID trägt keine Stabilitätszusage und ist nichts, worauf ein Tool sich verdrahtet.
- **MUSS [MUST]** festhalten, dass Gemini ein Asset erzeugt hat; das Sidecar-Feld `model` des Tools erfüllt das.
- **MUSS NICHT [MUST NOT]** die Limits dieser Grundlage auf Imagen (`imagen-*`), auf `gemini-3-pro-image` oder auf `gemini-3.1-flash-lite-image` anwenden; die Stufen unterscheiden sich in Output-Obergrenze, Reasoning-Verhalten und Preis, und Versionsdrift in Drittanbieter-Guides ist verbreitet (siehe Anti-Patterns).
- **MUSS [MUST]** `gemini-2.5-flash-image` für neue Arbeit als abgekündigt behandeln: Es wird am 2026-10-02 abgeschaltet ([E8], [E11], [E12]). Prompting-Ratschläge, die dafür geschrieben wurden, gelten nur weiter, wo diese Grundlage sie gegen die Dokumentation des Nachfolgers neu formuliert.

### Prompting (die Szene beschreiben)
- **MUSS [MUST]** Prompts als erzählende, beschreibende Sätze schreiben — „describe the scene, don't list keywords"; Geminis Sprachverständnis belohnt Prosa über komma-separierte Tag-Listen, genau wie FLUX.
- **SOLLTE [SHOULD]** die Absicht bzw. den Zweck des Assets nennen, nicht nur seinen Inhalt (`a logo for a high-end, minimalist skincare brand` schlägt ein bloßes Subjekt); genannte Absicht ist ein Gemini-Hebel, den FLUX nicht hat.
- **SOLLTE [SHOULD]** der Reihenfolge Subjekt, dann Aktion, Ort oder Kontext, Komposition und Stil folgen, das Subjekt zuerst.
- **SOLLTE [SHOULD]** den Prompt mit einem starken Verb eröffnen, das die primäre Operation benennt (`Create`, `Transform`, `Remove`), damit das Modell die Aufgabe kennt.
- **SOLLTE [SHOULD]** bei Material und Textur hyperspezifisch sein (`navy blue tweed` statt `suit jacket`; `ornate elven plate armor etched with silver leaf` statt `armor`); granulare Beschreibung ist der größte einzelne Qualitätshebel.
- **SOLLTE [SHOULD]** die Komposition mit photographischer und filmischer Sprache steuern (`wide-angle`, `macro`, `low-angle`, `85mm portrait lens`, `f/1.8 shallow depth of field`, `Dutch angle`) und Licht und Color-Grading explizit dirigieren (`three-point softbox`, `chiaroscuro`, `golden-hour backlighting`; `as if on 1980s color film, slightly grainy`; `muted teal color grading`).

### Use-Case-Templates
- **SOLLTE [SHOULD]** die Prompt-Formen je Use-Case als Ausgangspunkte verwenden:
  - Fotorealistisch: `A photorealistic [shot type] of [subject], [action], set in [environment], illuminated by [lighting] creating a [mood] atmosphere, captured with [camera/lens] emphasizing [textures].`
  - Sticker oder Illustration: `A [style] sticker of [subject], featuring [characteristics] and a [palette], with [line style] and [shading]. White background.`
  - Text oder Logo: `Create a [image type] for [brand] with text '[exact text]' in a [font style], [style], [color scheme].`
  - Produkt: `A studio-lit product photograph of [product] on [background], lighting [setup] to [purpose], camera angle [angle] showcasing [feature], sharp focus on [detail].`
  - Minimalismus oder Negative-Space: `A minimalist composition of a single [subject] in the [location], on a vast empty [color] canvas with significant negative space, [lighting].`
  - Comic-Panel: `A single comic panel in [art style]. Foreground: [character/action]. Background: [setting]. Caption box with text '[text]'. Lighting creates [mood].`

### Text-Rendering (eine Gemini-Stärke)
- **MUSS [MUST]** die wörtlichen Zielwörter in Anführungszeichen setzen (`"URBAN EXPLORER"`); das Quoting ist es, was Gemini den exakten String rendern lässt. Das ist dieselbe Quoting-Regel wie bei FLUX, aber Gemini rendert längeren, komplexeren Text zuverlässig.
- **SOLLTE [SHOULD]** den Font oder typografischen Stil benennen (`bold white sans-serif`, `Century Gothic`), und **KANN [MAY]** für mehrzeilige Layouts ein Styling pro Zeile angeben.
- **KANN [MAY]** Text in einer anderen Sprache rendern, indem der Prompt in einer Sprache geschrieben und die Zielsprache der gerenderten Wörter genannt wird.
- **KANN [MAY]** den Text-first-Ansatz nutzen — das Modell erst konversationell den Textinhalt erzeugen lassen, dann um ein Bild bitten, das ihn rendert — für knifflige Copy.
- **MUSS NICHT [MUST NOT]** annehmen, dass Imagens Grenze von rund 25 Zeichen gilt; das native Gemini-Modell rendert längere Strings, auch wenn sehr komplexe Typografie weiterhin Iteration brauchen kann.

### Editing und Multi-Image
- **SOLLTE [SHOULD]** per konversationellem Multi-Turn-Editing iterieren — der empfohlene Weg —, eine Sache pro Turn ändernd (`keep everything the same, but make the lighting warmer`) statt von Grund auf neu zu generieren.
- **SOLLTE [SHOULD]** eine Region per Semantic Masking bearbeiten: nur das zu ändernde Element nennen und das Modell anweisen, den Rest identisch zu halten und genannte Aspekte zu erhalten (`change only the [element] to [new]; keep everything else identical, preserving the lighting and composition`).
- **KANN [MAY]** aus bis zu 14 Referenzbildern komponieren: bis zu 10 für Objekttreue plus bis zu 4 für Charakterkonsistenz ([E2]). Dabei benennen, welches Element aus welchem Input stammt.
- **KANN [MAY]** Ausgabegröße und Seitenverhältnis ausdrücklich über den Provider des Tools anfordern statt in Prosa. Das Modell akzeptiert `1K`, `2K` und `4K` (ein großes `K` ist Pflicht, ein kleines `1k` wird abgewiesen) sowie die Verhältnisse `1:1`, `3:2`, `2:3`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9` ([E2]). Ob das Tool sie exponiert, ist eine Werkzeugfrage und gehört `spec/tools/image-generation/`.
- **MUSS [MUST]** die Seitenverhältnis-Vererbung berücksichtigen: Ein Edit erbt das Seitenverhältnis des Eingabebilds, und bei mehreren Inputs übernimmt es das Verhältnis des letzten Inputs; für eine Neugenerierung das gewünschte Seitenverhältnis (oder `do not change the input aspect ratio`) explizit angeben.

### Negative Prompts
- **MUSS NICHT [MUST NOT]** `no X`-Negativformulierung verwenden oder einen Negative-Prompt-Parameter annehmen; Gemini exponiert keinen. Unerwünschte Attribute ausdrücken, indem der gewünschte Zustand positiv beschrieben wird (`an empty, deserted street with no signs of traffic` statt `no cars`) — dieselbe semantisch-positive Regel wie bei FLUX.

### Output und Lizenzierung (harte Invarianten)
- **MUSS [MUST]** das SynthID-Wasserzeichen als immer vorhanden behandeln: Jedes Gemini-generierte Bild trägt es. Für Branding-, kommerzielle oder Blog-Assets ist das ein materieller Unterschied zum FLUX-über-Cloudflare-Pfad (kein Wasserzeichen) und **MUSS** bei der Provider-Wahl abgewogen werden.
- **MUSS [MUST]** Gemini als billing-pflichtig behandeln: kein Bildgenerierungsmodell der Gemini Developer API hat ein Free-Tier, und ein Aufruf ohne Billing scheitert an einer auf null gesetzten Free-Tier-Quota-Metrik ([E5], [E6], [E7]). Das ist eine Provider-Eigenschaft, kein Prompt-Belang, aber es beeinflusst die Provider-Wahl (Eigentum von `spec/tools/image-generation/`).

### Anti-Patterns
- **MUSS NICHT [MUST NOT]** einen FLUX- oder SDXL-Komma-Tag-Prompt wörtlich auf Gemini portieren; ihn als erzählende Prosa mit genannter Absicht neu schreiben.
- **MUSS NICHT [MUST NOT]** `no X`-Negative, Prompt-Gewichte (`(word:1.3)`, `++`) oder Betonungsklammern verwenden.
- **MUSS NICHT [MUST NOT]** Imagens 480-Token- oder Rund-25-Zeichen-Text-Limits auf das native Gemini-Modell anwenden, noch das Reasoning-Kern- und Studio-Typografie-Verhalten von `gemini-3-pro-image` auf diese Stufe übertragen, noch annehmen, dass der Preis von `gemini-3.1-flash-lite-image` hier gilt.
- **MUSS NICHT [MUST NOT]** Prompting-Ratschläge übernehmen, die für `gemini-2.5-flash-image` geschrieben wurden, ohne sie gegen diese Grundlage zu prüfen; die Modell-IDs unterscheiden sich, und Drittanbieter-Guides von vor der Abschaltung am 2026-10-02 adressieren das abgekündigte Modell.
- **MUSS NICHT [MUST NOT]** ein Gemini-Bild als wasserzeichenfreies kommerzielles Asset ausliefern; SynthID ist immer eingebettet.

## Akzeptanzkriterien

- [ ] Ein geprüfter Gemini-Prompt liest sich als erzählende Sätze, nicht als Komma-Tag-Liste, und nennt die Absicht des Assets.
- [ ] Bild-Text ist in Anführungszeichen gesetzt und sein Font oder Stil ist benannt.
- [ ] Unerwünschte Attribute sind positiv formuliert; kein Negative-Prompt-Parameter oder `no X`-Tag wird verwendet.
- [ ] Editing-Prompts nutzen konversationelle oder Semantic-Masking-Formulierung (`change only X, keep the rest identical`) und berücksichtigen die Seitenverhältnis-Vererbung.
- [ ] Der Prompt adressiert `gemini-3.1-flash-image` (die stabile ID, nicht die `-preview`-ID) und wendet weder Imagens Limits noch die der Pro- und Lite-Stufen an.
- [ ] Das Sidecar des generierenden Tools hält fest, dass Gemini das Asset erzeugt hat.
- [ ] Die Provider-Wahl für ein kommerzielles oder Blog-Asset berücksichtigt das immer vorhandene SynthID-Wasserzeichen.

## Referenzen

Die Billing-, Wasserzeichen- und Modell-Aktualitäts-Aussagen in §„Output und Lizenzierung (harte Invarianten)" sind Author-Time-externe Aussagen, trianguliert gemäß `spec/claude/research-triangulate/` §"Author-Time-Aussagen" (Author-Time-Stufe: mindestens drei unabhängige Quellen, Primary-first geordnet). Abrufdatum für jede externe Quelle unten: 2026-07-24.

- [R1] Prompt-Dokument-Authoring, das den gewählten Generator adressiert: `spec/design/graphic-prompt-authoring/`
- [R2] Das Tool, dessen `gemini`-Provider `gemini-3.1-flash-image` aufruft: `spec/tools/image-generation/`
- [R3] Die Schwester-Modell-Grundlage für den Standard-FLUX-Pfad: `spec/design/flux-image-generation/`
- [R4] Brand-Farbvertrag, den die Prompts erfüllen müssen: `spec/design/corporate-design-colors/`
- [E1] How to prompt Gemini Flash Image for the best results (Use-Case-Templates, Best Practices; für die 2.5-Generation geschrieben, hier für die Prompting-Formen behalten, die diese Grundlage neu formuliert, nicht für seine Modellfakten): <https://developers.googleblog.com/en/how-to-prompt-gemini-2-5-flash-image-generation-for-the-best-results/>
- [E2] Nano Banana image generation, offizielle API-Docs (Beispiele, Seitenverhältnisse, SynthID-Wasserzeichen): <https://ai.google.dev/gemini-api/docs/image-generation>
- [E3] Ultimate prompting guide for Nano Banana (Frameworks, Text-Rendering-Regeln, Kamera und Licht): <https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana>
- [E4] Imagen-Prompt-Guide, der Grenzfall, dessen 480-Token- und Rund-25-Zeichen-Text-Limits **nicht** auf das native Gemini-Modell zutreffen: <https://ai.google.dev/gemini-api/docs/imagen>
- [E5] Gemini-Developer-API-Pricing, dessen Free-Tier-Zeile für jedes Bildmodell „Not available" liest, `gemini-3.1-flash-image` eingeschlossen, und das dessen Bild-Output mit 60 USD je Million Token bepreist gegen 30 bei der Lite- und 120 bei der Pro-Stufe (Primary): <https://ai.google.dev/gemini-api/docs/pricing>
- [E6] Home-Assistant-core-Issue #157289, ein unabhängiger Konsument, der `generate_content_free_tier_requests, limit: 0` bei der Gemini-Bildgenerierung meldet (Secondary): <https://github.com/home-assistant/core/issues/157289>
- [E7] googleapis-`js-genai`-Issue #1322, dieselbe auf null gesetzte Free-Tier-Quota-Metrik, ausgelöst über Googles eigenes JavaScript-SDK (Secondary): <https://github.com/googleapis/js-genai/issues/1322>
- [E8] Gemini-API-Model-Deprecations, das `gemini-2.5-flash-image` das Abschaltdatum 2026-10-02 gibt und `gemini-3.1-flash-image-preview` als Ersatz nennt (Primary): <https://ai.google.dev/gemini-api/docs/deprecations>
- [E9] Gemini-API-Modellkatalog, der `gemini-3.1-flash-image` („Nano Banana 2"), `gemini-3.1-flash-lite-image` und `gemini-3-pro-image` als stabil führt (Primary): <https://ai.google.dev/gemini-api/docs/models>
- [E10] Die Legacy-`generateContent`-Oberfläche für Bildgenerierung, deren Beispiele `https://generativelanguage.googleapis.com/v1/models/gemini-3.1-flash-image:generateContent` aufrufen und `responseFormat.image.aspectRatio` sowie `imageSize` innerhalb von `generationConfig` übergeben (Primary): <https://ai.google.dev/gemini-api/docs/generate-content/image-generation>
- [E11] Ein unabhängiger Retirement-Tracker, der die Abschaltung am 2026-10-02 und das Migrationsziel festhält (Secondary): <https://vorplabs.com/models/google-model-retirements>
- [E12] Eine unabhängige Migrationsdarstellung, die dasselbe Abschaltdatum festhält und darauf hinweist, dass der in der Deprecation-Tabelle genannte Ersatz eine Preview-ID ist (Secondary): <https://www.aifreeapi.com/en/posts/gemini-2-5-flash-image-replacement>
- [E13] Eine unabhängige Darstellung, die `gemini-3.1-flash-image` als Googles empfohlenen Ersatz für die abgekündigten Imagen-4-Endpunkte und als sein aktuelles Allzweck-Bildmodell festhält (Secondary): <https://aicybr.com/blog/imagen-4-api-shutdown-migrate-gemini-image>

Verifiziert 2026-09-12 bei der Migration auf `gemini-3.1-flash-image`: Die Billing-Invariante hält — Google veröffentlicht für kein Gemini-Bildmodell ein Free-Tier-Kontingent, und die auf null gesetzte Quota-Metrik reproduziert sich über unabhängige Konsumenten hinweg ([E5]–[E7]). Auch das immer vorhandene SynthID-Wasserzeichen bleibt auf der primären Image-Generation-Seite dokumentiert ([E2], „All generated images include a SynthID watermark"), ohne dass irgendwo ein Opt-out dokumentiert wäre. Zwei Einschränkungen: Google veröffentlicht keine numerische Free-Tier-Request-Tabelle je Modell mehr, weshalb die „Not available"-Zeile der Preisseite der belastbare Beleg ist und keine Kontingentzahl; und ein `limit: 0`-Response-Body beweist für sich genommen nicht, dass einem Projekt Billing fehlt, da im Februar 2026 auch zahlende Projekte bei Bildmodellen dieselbe Metrik trafen. Die Modellidentität selbst ist über vier unabhängige Domain-Wurzeln trianguliert: Googles eigener Katalog und die Deprecation-Tabelle ([E8], [E9]) plus drei unabhängige Tracker ([E11]-[E13]).

## Offene Fragen

- **Exaktes Prompt-Token-Limit.** Google veröffentlicht für `gemini-3.1-flash-image` kein hartes Token-Cap vergleichbar mit FLUX' 256 oder Imagens 480. Das praktische Limit ist als großzügig, aber nicht primärdokumentiert zu behandeln, bis eine Zahl veröffentlicht wird.
- **Ob `candidateCount` und `seed` den Bildpfad erreichen.** Die `generateContent`-Bildbeispiele zeigen keines der beiden Felder ([E10]), während das Tool beide weiterhin sendet, übernommen aus dem `v1beta`-Aufruf für 2.5. Ob die `v1`-Oberfläche sie akzeptiert, ignoriert oder abweist, ist hier unverifiziert, weil es einen abgerechneten Aufruf braucht. Es ist eine Werkzeugfrage und gehört `spec/tools/image-generation/`; bis sie geklärt ist, sind `--n` und `--seed` beim `gemini`-Provider unbelegt statt bekannt gut.
- **Interactions statt `generateContent`.** Google führt seine Bildgenerierungs-Dokumentation inzwischen mit der Interactions-API an und bezeichnet `generateContent` als Legacy, dokumentiert es aber weiterhin für Bildmodelle ([E10]). Diese Grundlage bleibt bei `generateContent`, weil die begleitende Migration von einem Abschaltdatum getrieben war und eine zusätzliche API-Umstellung den Wirkungsradius eines Termin-Fixes vergrößert. Erneut prüfen, sobald `generateContent` ein eigenes Abkündigungsdatum bekommt.

<!-- Durch die Migration am 2026-09-12 aufgelöst: die Nachfolgemodell-Frage (entschieden auf die
stabile `gemini-3.1-flash-image`), die Anzahl der Referenzbilder (14 = 10 Objekte + 4 Charaktere,
[E2]) und die Frage nach der Output-Auflösung (1K/2K/4K mit großem K, [E2]). -->
