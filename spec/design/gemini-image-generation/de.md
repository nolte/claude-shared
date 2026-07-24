# Gemini-Bildgenerierung

Status: draft

## Kontext

Googles natives Gemini-Bildmodell — `gemini-2.5-flash-image` („Nano Banana") — ist der Pfad des Portfolios, wenn ein Asset Gemini-spezifische Stärken braucht: lesbaren Text im Bild, konversationelles Multi-Turn-Editing und Multi-Image-Komposition. Es wird über den `gemini`-Provider des `image-generation`-Tools erreicht. Gemini ist nativ multimodal und auf tiefem Sprachverständnis gebaut und belohnt daher — wie FLUX, anders als SDXL — erzählende, beschreibende Prosa statt komma-separierter Tag-Listen. Es geht weiter: Es belohnt zusätzlich eine genannte Absicht bzw. einen Zweck und versteht mehrstufige Anweisungen innerhalb eines einzelnen Prompts. Einen Gemini-Prompt wie eine FLUX- oder SDXL-Tag-Liste zu behandeln lässt Qualität liegen.

Ein Prompt ist nicht modellportabel: Derselbe String liefert über FLUX, Gemini und Imagen hinweg materiell unterschiedliche Ergebnisse, daher müssen Prompts auf das Zielmodell optimiert werden. Diese Spec ist die Gemini-Hälfte dieses Vertrags; `spec/design/flux-image-generation/` ist die FLUX-Hälfte.

Diese Spec ist die **Generierungs-Grundlage auf Modellebene** für Gemini: die verifizierten Prompting-Praktiken und die harten Invarianten, die jeden Gemini-Bildaufruf binden. Sie wird konsumiert von `spec/design/graphic-prompt-authoring/` (das brand-konforme Prompts zusammensetzt und den gewählten Generator korrekt adressieren muss) und von `spec/tools/image-generation/` (dessen `gemini`-Provider `gemini-2.5-flash-image` aufruft). Sie besitzt **nicht** den Brand-Farbvertrag (`corporate-design-colors`), die Tool-Mechanik (`image-generation`) oder das Prompt-Dokument-Format (`graphic-prompt-authoring`); sie liefert die Modell-Fakten, auf denen diese Specs aufbauen.

Leser: Prompt-Autoren und Skill-/Agent-Autoren, die Gemini adressieren; Betreiber, die die Generierung tunen; Reviewer, die prüfen, dass Gemini-Aufrufe Geminis Stärken nutzen statt portierter FLUX- oder SDXL-Gewohnheiten.

## Ziele

- Eine verifizierte Grundlage für optimales Prompting mit dem nativen Gemini-Bildmodell, abgegrenzt von der FLUX-Grundlage.
- Die Stärken des Modells (Bild-Text, konversationelles Editing, Multi-Image-Komposition) und seine harten Caveats (kein Negative-Prompt-Parameter, immer aktives SynthID-Wasserzeichen, Billing) einmal festgeschrieben, dort, wo sowohl die Prompt-Authoring-Spec als auch das Tool sie zitieren können.
- Eine klare Grenze zwischen dem nativen Gemini-Modell (`gemini-2.5-flash-image`), den neueren Nano-Banana-Pro- und Nano-Banana-2-Stufen und Imagen, damit versionsspezifische Limits nicht falsch angewendet werden.

## Nicht-Ziele

- Das Brand-Farbsystem, das deskriptive Farbvokabular und der Style-Reference-Vertrag — Eigentum von `spec/design/corporate-design-colors/`.
- Tool-Mechanik (CLI, Provider-Auswahl, Sidecar, Credentials) — Eigentum von `spec/tools/image-generation/`.
- Prompt-Dokument-Format und Brand-Sourcing — Eigentum von `spec/design/graphic-prompt-authoring/`.
- Nicht-Gemini-Modelle (FLUX, SDXL) — Eigentum von `spec/design/flux-image-generation/` und etwaigen Geschwistern.
- Imagen (`imagen-*`): eine andere Modellfamilie mit anderen Limits (480-Token-Prompt, Text auf rund 25 Zeichen begrenzt); die Tool-Spec verdrahtet es unerreichbar, und es wird hier nur als Grenze referenziert, damit seine Limits nicht auf das native Gemini-Modell angewendet werden.
- Die neueren Nano-Banana-Pro- und Nano-Banana-2-Stufen („Gemini 3 Pro/Flash Image") als Generierungsziel; ihre erweiterten Limits (größerer Kontext, 4K-Output, mehr Referenzbilder) werden nur genannt, um Fehlanwendung zu verhindern.

## Anforderungen

### Modellwahl
- **MUSS [MUST]** `gemini-2.5-flash-image` („Nano Banana") als das Modell behandeln, das diese Grundlage regelt; das `image-generation`-Tool verdrahtet genau diese ID.
- **MUSS [MUST]** festhalten, dass Gemini ein Asset erzeugt hat; das Sidecar-Feld `model` des Tools erfüllt das.
- **MUSS NICHT [MUST NOT]** die Limits dieser Grundlage auf Imagen (`imagen-*`) anwenden, noch annehmen, dass die neueren Nano-Banana-Pro- oder Nano-Banana-2-Limits für `gemini-2.5-flash-image` gelten; Versionsdrift in Drittanbieter-Guides ist verbreitet (siehe Anti-Patterns).

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
- **KANN [MAY]** aus mehreren Referenzbildern komponieren und benennen, welches Element aus welchem Input stammt.
- **MUSS [MUST]** die Seitenverhältnis-Vererbung berücksichtigen: Ein Edit erbt das Seitenverhältnis des Eingabebilds, und bei mehreren Inputs übernimmt es das Verhältnis des letzten Inputs; für eine Neugenerierung das gewünschte Seitenverhältnis (oder `do not change the input aspect ratio`) explizit angeben.

### Negative Prompts
- **MUSS NICHT [MUST NOT]** `no X`-Negativformulierung verwenden oder einen Negative-Prompt-Parameter annehmen; Gemini exponiert keinen. Unerwünschte Attribute ausdrücken, indem der gewünschte Zustand positiv beschrieben wird (`an empty, deserted street with no signs of traffic` statt `no cars`) — dieselbe semantisch-positive Regel wie bei FLUX.

### Output und Lizenzierung (harte Invarianten)
- **MUSS [MUST]** das SynthID-Wasserzeichen als immer vorhanden behandeln: Jedes Gemini-generierte Bild trägt es. Für Branding-, kommerzielle oder Blog-Assets ist das ein materieller Unterschied zum FLUX-über-Cloudflare-Pfad (kein Wasserzeichen) und **MUSS** bei der Provider-Wahl abgewogen werden.
- **MUSS [MUST]** Gemini als billing-pflichtig behandeln: kein Bildgenerierungsmodell der Gemini Developer API hat ein Free-Tier, und ein Aufruf ohne Billing scheitert an einer auf null gesetzten Free-Tier-Quota-Metrik ([E5], [E6], [E7]). Das ist eine Provider-Eigenschaft, kein Prompt-Belang, aber es beeinflusst die Provider-Wahl (Eigentum von `spec/tools/image-generation/`).

### Anti-Patterns
- **MUSS NICHT [MUST NOT]** einen FLUX- oder SDXL-Komma-Tag-Prompt wörtlich auf Gemini portieren; ihn als erzählende Prosa mit genannter Absicht neu schreiben.
- **MUSS NICHT [MUST NOT]** `no X`-Negative, Prompt-Gewichte (`(word:1.3)`, `++`) oder Betonungsklammern verwenden.
- **MUSS NICHT [MUST NOT]** Imagens 480-Token- oder Rund-25-Zeichen-Text-Limits auf das native Gemini-Modell anwenden, noch Nano-Banana-Pro- oder Nano-Banana-2-Limits (größerer Kontext, 4K-Output, mehr Referenzbilder) für `gemini-2.5-flash-image` annehmen.
- **MUSS NICHT [MUST NOT]** ein Gemini-Bild als wasserzeichenfreies kommerzielles Asset ausliefern; SynthID ist immer eingebettet.

## Akzeptanzkriterien

- [ ] Ein geprüfter Gemini-Prompt liest sich als erzählende Sätze, nicht als Komma-Tag-Liste, und nennt die Absicht des Assets.
- [ ] Bild-Text ist in Anführungszeichen gesetzt und sein Font oder Stil ist benannt.
- [ ] Unerwünschte Attribute sind positiv formuliert; kein Negative-Prompt-Parameter oder `no X`-Tag wird verwendet.
- [ ] Editing-Prompts nutzen konversationelle oder Semantic-Masking-Formulierung (`change only X, keep the rest identical`) und berücksichtigen die Seitenverhältnis-Vererbung.
- [ ] Der Prompt adressiert `gemini-2.5-flash-image` und wendet weder Imagen- noch Nano-Banana-Pro/2-Limits an.
- [ ] Das Sidecar des generierenden Tools hält fest, dass Gemini das Asset erzeugt hat.
- [ ] Die Provider-Wahl für ein kommerzielles oder Blog-Asset berücksichtigt das immer vorhandene SynthID-Wasserzeichen.

## Referenzen

Die Billing-, Wasserzeichen- und Modell-Aktualitäts-Aussagen in §„Output und Lizenzierung (harte Invarianten)" sind Author-Time-externe Aussagen, trianguliert gemäß `spec/claude/research-triangulate/` §"Author-time assertions" (Author-Time-Stufe: mindestens drei unabhängige Quellen, Primary-first geordnet). Abrufdatum für jede externe Quelle unten: 2026-07-24.

- [R1] Prompt-Dokument-Authoring, das den gewählten Generator adressiert: `spec/design/graphic-prompt-authoring/`
- [R2] Das Tool, dessen `gemini`-Provider `gemini-2.5-flash-image` aufruft: `spec/tools/image-generation/`
- [R3] Die Schwester-Modell-Grundlage für den Standard-FLUX-Pfad: `spec/design/flux-image-generation/`
- [R4] Brand-Farbvertrag, den die Prompts erfüllen müssen: `spec/design/corporate-design-colors/`
- [E1] How to prompt Gemini 2.5 Flash Image for the best results (Use-Case-Templates, Best Practices): <https://developers.googleblog.com/en/how-to-prompt-gemini-2-5-flash-image-generation-for-the-best-results/>
- [E2] Nano Banana image generation, offizielle API-Docs (Beispiele, Seitenverhältnisse, SynthID-Wasserzeichen): <https://ai.google.dev/gemini-api/docs/image-generation>
- [E3] Ultimate prompting guide for Nano Banana (Frameworks, Text-Rendering-Regeln, Kamera und Licht): <https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana>
- [E4] Imagen-Prompt-Guide, der Grenzfall, dessen 480-Token- und Rund-25-Zeichen-Text-Limits **nicht** auf das native Gemini-Modell zutreffen: <https://ai.google.dev/gemini-api/docs/imagen>
- [E5] Gemini-Developer-API-Pricing, dessen Free-Tier-Zeile für jedes Bildmodell „Not available" lautet, `gemini-2.5-flash-image` eingeschlossen (Primary): <https://ai.google.dev/gemini-api/docs/pricing>
- [E6] Home-Assistant-core-Issue #157289, ein unabhängiger Konsument, der `generate_content_free_tier_requests, limit: 0` bei der Gemini-Bildgenerierung meldet (Secondary): <https://github.com/home-assistant/core/issues/157289>
- [E7] googleapis-`js-genai`-Issue #1322, dieselbe auf null gesetzte Free-Tier-Quota-Metrik, ausgelöst über Googles eigenes JavaScript-SDK (Secondary): <https://github.com/googleapis/js-genai/issues/1322>
- [E8] Gemini-API-Model-Deprecations, das `gemini-2.5-flash-image` das Abschaltdatum 2026-10-02 gibt und den Ersatz benennt (Primary): <https://ai.google.dev/gemini-api/docs/deprecations>

Verifiziert 2026-07-24: Die Billing-Invariante hält — Google veröffentlicht für kein Gemini-Bildmodell ein Free-Tier-Kontingent, und die auf null gesetzte Quota-Metrik reproduziert sich über unabhängige Konsumenten hinweg ([E5]–[E7]). Auch das immer vorhandene SynthID-Wasserzeichen bleibt auf der primären Image-Generation-Seite dokumentiert ([E2], „All generated images include a SynthID watermark"), ohne dass irgendwo ein Opt-out dokumentiert wäre. Zwei Einschränkungen: Google veröffentlicht keine numerische Free-Tier-Request-Tabelle je Modell mehr, weshalb die „Not available"-Zeile der Preisseite der belastbare Beleg ist und keine Kontingentzahl; und ein `limit: 0`-Response-Body beweist für sich genommen nicht, dass einem Projekt Billing fehlt, da im Februar 2026 auch zahlende Projekte bei Bildmodellen dieselbe Metrik trafen.

## Offene Fragen

- **Exaktes Prompt-Token-Limit von `gemini-2.5-flash-image`.** Das native Modell hat kein veröffentlichtes hartes Token-Cap vergleichbar mit FLUX' 256 oder Imagens 480; die in Guides genannten großen Kontextfenster (131K/65K) gehören zu den neueren Nano-Banana-Pro- und Nano-Banana-2-Stufen. Das praktische Limit des 2.5-Modells als großzügig, aber nicht primär dokumentiert behandeln, bis Google eine Zahl veröffentlicht.
- **Anzahl Referenzbilder bei 2.5.** Die Angabe „bis zu 14 Referenzbilder" ist für die Nano-Banana-Pro/2-Stufen dokumentiert; die unterstützte Anzahl speziell für `gemini-2.5-flash-image` ist hier nicht primär verifiziert. Erneut prüfen, falls Google sie dokumentiert.
- **Output-Auflösung des gemini-Pfads des Tools.** Neuere Stufen liefern 1K/2K/4K; was `gemini-2.5-flash-image` standardmäßig über den verdrahteten `v1beta`-Endpunkt zurückgibt, ist ein Tool-Mechanik-Belang im Eigentum von `spec/tools/image-generation/` und wird hier nicht wiederholt.
- **Nachfolgemodell für diese Grundlage.** Google gibt `gemini-2.5-flash-image` das Abschaltdatum 2026-10-02 und nennt `gemini-3.1-flash-image` als Ersatz ([E8]); `gemini-3.1-flash-lite-image` und `gemini-3-pro-image` sind die weiteren aktuellen stabilen Bildmodelle. Auf welches davon diese Grundlage neu gepinnt wird und welche ihrer Prompting-Invarianten den Wechsel überleben, wird zusammen mit der Tool-seitigen Migration im Eigentum von `spec/tools/image-generation/` entschieden — nicht hier geraten, denn die Prompting-Fakten müssen gegen die Dokumentation des Nachfolgers neu verifiziert statt geerbt werden.
