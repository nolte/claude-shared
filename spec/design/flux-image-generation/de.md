# FLUX-Bildgenerierung

Status: draft

## Kontext

FLUX (Black Forest Labs) ist das Bildmodell hinter dem Standard-Generierungspfad des Portfolios: **FLUX.1-schnell über Cloudflare Workers AI** (Apache-2.0, Free-Tier), mit FLUX.1-dev und den nur-API-Varianten pro/ultra als Alternativen. FLUX hat modell-spezifische Eigenheiten, die generische Prompt-Ratschläge falsch behandeln. Es basiert auf einem **T5-XXL**-Text-Encoder und belohnt daher natürlichsprachige Beschreibungen statt SDXL-typischer komma-separierter Tags; und die **schnell**-Variante ist guidance- und step-distilliert, läuft also ohne Classifier-Free Guidance und hat keine wirksamen Negative Prompts. FLUX wie SDXL zu behandeln erzeugt ausgewaschene, am Ziel vorbei generierte Bilder.

Diese Spec ist die **Generierungs-Grundlage auf Modellebene**: die verifizierten FLUX-Prompting-Praktiken und die harten Parameter-Invarianten, die jeden FLUX-Aufruf binden. Sie wird konsumiert von `spec/design/graphic-prompt-authoring/` (das brand-konforme Prompts zusammensetzt und FLUX korrekt adressieren muss) und von `spec/tools/image-generation/` (dessen `cloudflare`-Provider FLUX.1-schnell ausführt). Sie besitzt **nicht** den Brand-Farbvertrag (`corporate-design-colors`), die Tool-Mechanik (`image-generation`) oder das Prompt-Dokument-Format (`graphic-prompt-authoring`); sie liefert die Modell-Fakten, auf denen diese Specs aufbauen.

Leser: Prompt-Autoren und Skill-/Agent-Autoren, die FLUX adressieren; Betreiber, die die Generierung tunen; Reviewer, die prüfen, dass FLUX-Aufrufe keine SDXL-Gewohnheiten tragen.

## Ziele

- Eine verifizierte Grundlage für optimale Generierung mit FLUX, damit Prompts und Parameter nicht in SDXL-Gewohnheiten abdriften.
- Die harten Modell-Invarianten (Guidance, Steps, Token-Limits, Fehlen von Negative Prompts) einmal festgeschrieben, dort, wo sowohl die Prompt-Authoring-Spec als auch das Tool sie zitieren können.
- Der Standardpfad (FLUX.1-schnell über Cloudflare) vollständig spezifiziert, inklusive der Einschränkungen, die das Cloudflare-Schema auferlegt.

## Nicht-Ziele

- Das Brand-Farbsystem, die deskriptive Farb-Vokabular und der Style-Reference-Vertrag — Eigentum von `spec/design/corporate-design-colors/`.
- Tool-Mechanik (CLI, Provider-Auswahl, Sidecar, Credentials) — Eigentum von `spec/tools/image-generation/`.
- Prompt-Dokument-Format und Brand-Sourcing — Eigentum von `spec/design/graphic-prompt-authoring/`.
- Nicht-FLUX-Modelle (SDXL, Gemini-Image, Imagen) — eine Schwester-Modell-Spec würde diese besitzen.
- Bildbearbeitung, In-Painting, ControlNet oder LoRA-Finetuning.

## Anforderungen

### Modellwahl
- **MUSS [MUST]** **FLUX.1-schnell** als Standardmodell behandeln: Apache-2.0 (kommerzielle Nutzung sowohl des Modells als auch seiner Outputs erlaubt), few-step-distilliert, bei Cloudflare Workers AI in Neuronen abgerechnet und damit aus dessen freiem Tageskontingent an Neuronen bedient.
- **MUSS [MUST]** **FLUX.1-dev** als auf *Modell*-Ebene lizenzbeschränkt behandeln, nicht auf Output-Ebene: die FLUX-[dev]-Non-Commercial-License verlangt für die kommerzielle Nutzung des Modells selbst eine separate Black-Forest-Labs-Lizenz und verpflichtet den Betreiber zum Content-Filtering, während die erzeugten Outputs für jeden Zweck einschließlich kommerzieller genutzt werden dürfen (die einzige Output-Beschränkung ist das Training eines Konkurrenzmodells). Weil die Kommerzialitätsfrage damit am erzeugenden Lauf hängt und nicht am Asset, **MUSS NICHT [MUST NOT]** FLUX.1-dev der Default für Blog- oder kommerzielle Assets sein; nur für nicht-kommerzielle oder Evaluierungs-Arbeit nutzen.
- **MUSS [MUST]** festhalten, welche FLUX-Variante ein Asset erzeugt hat; das Sidecar-Feld `model` des `image-generation`-Tools erfüllt das.

### Prompting (natürliche Sprache)
- **MUSS [MUST]** Prompts als natürlichsprachige, beschreibende Sätze schreiben, nicht als komma-separierte SDXL-typische Tag-Listen; FLUX' T5-XXL-Encoder belohnt beschreibende Formulierung (`a sign with green text` statt `sign, green`).
- **SOLLTE [SHOULD]** der Prompt-Reihenfolge von Black Forest Labs folgen — Subjekt, dann Ort/Setting, Stil/Medium, Kamera, Licht, Farben, Effekt, zusätzliche Elemente — beginnend mit dem Subjekt (das Wichtigste zuerst).
- **MUSS [MUST]** jeglichen Bild-Text rendern, indem der wörtliche String in Anführungszeichen gesetzt wird (z. B. `"OPEN"`), und solche Strings kurz halten; T5-XXL macht FLUX stark bei lesbarem Text, aber nur wenn das Literal in Anführungszeichen steht.
- **MUSS NICHT [MUST NOT]** Prompt-Gewichte (`(word:1.3)`, `++`, Betonungsklammern) verwenden; FLUX ignoriert sie, daher Betonung in Worten ausdrücken (`with emphasis on the foreground`).
- **SOLLTE [SHOULD]** einen Stil beschreiben statt Künstlernamen zu stapeln; ein beschriebener Stil (`epic fantasy concept art, warm lighting, dramatic composition`) ist zuverlässiger als `by <artist>`.
- **SOLLTE [SHOULD]** englische Prompts für die präzisesten Ergebnisse bevorzugen.

### Token- und Längenlimits
- **MUSS [MUST]** FLUX.1-schnell-Prompts innerhalb von **256 Token** halten — das harte Limit des Modells; Text darüber hinaus wird abgeschnitten. FLUX.1-dev erlaubt rund 512 Token.
- Cloudflare deckelt zusätzlich den Prompt-**String** bei 2048 Zeichen; das 256-Token-Modell-Limit ist das engere, bindende Limit für schnell, daher schlagen dichte, front-loaded Prompts lange.

### Negative Prompts
- **MUSS NICHT [MUST NOT]** sich auf Negative Prompts mit FLUX.1-schnell verlassen: es läuft ohne Classifier-Free Guidance (Guidance ≈ 0), daher hat ein Negative Prompt keine Wirkung, und das Cloudflare-Schema exponiert keinen `negative_prompt`-Parameter.
- **MUSS [MUST]** unerwünschte Attribute stattdessen positiv ausdrücken — `a clean, uncluttered background` statt `no clutter`; `a clear blue sky` statt `no clouds`.

### Parameter (harte Invarianten)
- **MUSS [MUST]** `guidance_scale = 0.0` für FLUX.1-schnell setzen. Das ist für das distillierte Modell zwingend; das häufig zitierte `3.5` gilt für FLUX.1-dev und ist für schnell **falsch**. FLUX.1-dev nutzt Guidance ≈ 3.5.
- **MUSS [MUST]** `steps` im distillierten Bereich halten: schnell **1–4** (Cloudflare-Hard-Cap **8**; mehr Steps fügen Latenz und Kosten ohne Qualität hinzu), dev 28–50.
- **SOLLTE [SHOULD]** einen expliziten `seed` übergeben, wenn Reproduzierbarkeit zählt; ein identischer Seed plus identische Parameter und Prompt reproduziert das Bild.
- **SOLLTE [SHOULD]** 1024×1024 (~1 MP) oder ein vertrautes Seitenverhältnis (1:1, 16:9, 9:16, 3:2) anvisieren, mit durch 16 teilbaren Pixel-Dimensionen.

### Cloudflare-Workers-AI-Pfad (Default)
- Der Endpoint `@cf/black-forest-labs/flux-1-schnell` akzeptiert nur `prompt` (≤ 2048 Zeichen), `steps` (≤ 8) und `seed`; er exponiert **kein** `width`, `height`, `negative_prompt` oder `guidance`. Output ist base64-kodiertes JPEG.
- **MUSS NICHT [MUST NOT]** auf diesem Pfad Auflösungssteuerung annehmen: `width`/`height` sind keine Parameter, die Output-Größe ist also durch den Endpoint fest (≈ 1024×1024; siehe Offene Fragen). Seitenverhältnis- oder Auflösungssteuerung erfordert einen Provider, der diese Parameter exponiert (dev/pro-Endpoints), nicht den Cloudflare-schnell-Pfad.

### Anti-Patterns
- **MUSS NICHT [MUST NOT]** SDXL-typischen Komma-Tag-Spam, Prompt-Gewichte oder Negative Prompts bei schnell verwenden.
- **MUSS NICHT [MUST NOT]** Künstlernamen anstelle von Beschreibung stapeln, widersprüchliche Begriffe kombinieren (`wide-angle extreme close-up`, `bright dark`) oder `steps` über das Cap anheben in der Erwartung von mehr Qualität.

## Akzeptanzkriterien

- [ ] Ein geprüfter FLUX-Prompt liest sich als natürlichsprachige Sätze, nicht als Komma-Tag-Liste.
- [ ] Keine Prompt-Gewichte (`(word:1.3)`, `++`) erscheinen in FLUX-Prompts.
- [ ] Ein schnell-Aufruf setzt Guidance auf `0` und `steps ≤ 8` und übergibt keinen `negative_prompt`.
- [ ] Bild-Text ist im Prompt in Anführungszeichen gesetzt.
- [ ] Unerwünschte Attribute sind positiv formuliert, nicht als Negative Prompts.
- [ ] FLUX.1-dev ist nicht der Default für kommerzielle oder veröffentlichte Assets; seine non-commercial-Lizenz wird respektiert.
- [ ] Das Sidecar des generierenden Tools hält die verwendete FLUX-Variante fest.
- [ ] Ein FLUX.1-schnell-Prompt bleibt innerhalb von 256 Token.

## Referenzen

Die Lizenz- und Hosting-Aussagen in §„Modellwahl" sind Author-Time-externe Aussagen, trianguliert gemäß `spec/claude/research-triangulate/` §"Author-time assertions" (Author-Time-Stufe: mindestens drei unabhängige Quellen, Primary-first geordnet). Abrufdatum für jede externe Quelle unten: 2026-07-24.

- [R1] Prompt-Dokument-Authoring, das FLUX adressiert: `spec/design/graphic-prompt-authoring/`
- [R2] Das Tool, dessen `cloudflare`-Provider FLUX.1-schnell ausführt: `spec/tools/image-generation/`
- [R3] Brand-Farbvertrag, den die Prompts erfüllen müssen: `spec/design/corporate-design-colors/`
- [E1] Black-Forest-Labs-Prompting-Guide: <https://docs.bfl.ai/guides/prompting_unified_basics>
- [E2] FLUX.1-schnell-Modellkarte (`guidance_scale=0.0`, `max_sequence_length=256`): <https://huggingface.co/black-forest-labs/FLUX.1-schnell>
- [E3] FLUX.1-dev-Modellkarte (`guidance_scale=3.5`, `max_sequence_length=512`): <https://huggingface.co/black-forest-labs/FLUX.1-dev>
- [E4] Cloudflare-`@cf/black-forest-labs/flux-1-schnell`-Schema (`steps` max 8, `prompt` max 2048, kein width/height/negative_prompt): <https://developers.cloudflare.com/workers-ai/models/flux-1-schnell/>
- [E5] FLUX-[dev]-Non-Commercial-License v2.0, der von Black Forest Labs aktuell publizierte Lizenztext (Stand 2025-11-25; die Scope-Klausel nennt FLUX.1 [dev]), der Output-Nutzung „for any purpose (including for commercial purposes)" gewährt (Primary): <https://bfl.ai/legal/non-commercial-license-terms>
- [E6] `LICENSE-FLUX1-dev` v1.1.1, die im `flux`-Inferenz-Repository weiterhin ausgelieferte Lizenzversion, die für eine „commercial activity" rund um das Modell eine Company-Lizenz verlangt (Primary): <https://github.com/black-forest-labs/flux/blob/main/model_licenses/LICENSE-FLUX1-dev>
- [E7] Black Forest Labs' eigene Klarstellung, dass die kurzzeitige v1.1-Formulierung ohne kommerzielle Output-Gewährung in v1.1.1 zurückgenommen wurde (Primary, Vendor-Statement in einem Drittanbieter-Forum): <https://huggingface.co/black-forest-labs/FLUX.1-Kontext-dev/discussions/6>
- [E8] Cloudflare-Workers-AI-Pricing, das Free-Kontingent von 10.000 Neuronen pro Tag, gegen das die Per-Tile- und Per-Step-Raten von FLUX.1-schnell abgerechnet werden (Primary, unabhängiger Redistributor): <https://developers.cloudflare.com/workers-ai/platform/pricing/>
- [E9] Unabhängige Übersicht über die Aufteilung schnell (Apache-2.0) / dev (source-available, non-commercial) / pro (proprietär), inklusive des Umstands, dass Nutzer das Eigentum an den Outputs behalten (Tertiary): <https://en.wikipedia.org/wiki/Flux_(text-to-image_model)>

Verifiziert 2026-07-24: Die Beschränkung von FLUX.1-dev sitzt am Modell, nicht am Output. Eine frühere Revision dieser Spec behauptete, die Lizenz verbiete die kommerzielle Nutzung der *Outputs*; der geltende Lizenztext widerspricht dem ([E5], [E6], [E7]), daher wird §„Modellwahl" oben korrigiert statt bloß belegt. Zwei Lizenzversionen zirkulieren parallel — v2.0 auf der Legal-Seite von Black Forest Labs und v1.1.1 im Inferenz-Repository und auf der Modellkarte —, und sie stimmen in der Output-Gewährung überein. Black Forest Labs hat inzwischen die FLUX.2-Familie unter denselben konsolidierten Non-Commercial-Bedingungen veröffentlicht; diese Spec regelt weiterhin die FLUX.1-Modelle, die das `image-generation`-Tool erreicht.

## Offene Fragen

- **Cloudflare feste Output-Auflösung.** Das schnell-Schema lässt `width`/`height` aus, daher ist die feste Output-Größe des Endpoints nicht primär dokumentiert (≈ 1024×1024 wird angenommen, in der Praxis bei 1024×1024 beobachtet, aber nicht im Schema angegeben). Erneut prüfen, falls Cloudflare die Output-Dimensionen veröffentlicht oder Größen-Parameter hinzufügt.
- **Pixel-Divisor 16 vs. 64.** Ein Divisor von 16 ist für FLUX-Latents weit dokumentiert; ob die bindende Einschränkung strikt 16 oder konservativ 64 ist, ist nicht primär verifiziert. Auf dem Cloudflare-Pfad gegenstandslos (keine Größensteuerung); relevant nur für dev/pro-Provider.
- **FLUX.1-dev Token-Limit.** Das HF-dev-Beispiel nutzt 512 Token; das harte T5-Cap liegt höher. 512 wird hier als empfohlene Obergrenze behandelt, bis eine primäre Angabe des wahren Maximums vorliegt.
