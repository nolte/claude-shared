# Bildgenerierung (Multi-Provider)

Status: draft

## Kontext

Bildgenerierung soll vom Terminal aus erreichbar sein — Prompt rein, Bilddatei auf der Platte raus — ohne eine Chat-UI zu öffnen und skriptbar in beliebige Pipelines. Kein einzelner Anbieter ist eine sichere langfristige Wette: Preise, Free-Tier-Kontingente und Modellverfügbarkeit ändern sich ohne Vorwarnung. Diese Spec regelt daher eine **Multi-Provider**-Fähigkeit mit austauschbaren Backends, umgesetzt durch den Skill `image-generate`, der das mitgelieferte `scripts/image_generate.py` ansteuert.

Diese Spec ersetzt die frühere Spec „Gemini-Bildgenerierung (Free-Tier)", deren Kernprämisse sich als falsch erwiesen hat: `gemini-2.5-flash-image` meldet ein Free-Tier-Kontingent von `limit: 0` und **erfordert Billing** (live verifiziert; siehe die Projekt-Historie rund um die `image-generate`-Arbeit). „Free-Tier" ist daher eine **Provider-Eigenschaft, keine Garantie des Tools**, und Modell-ID-Pinning kann Kostenfreiheit für sich genommen nicht garantieren — dasselbe Modell ist free oder paid, je nach Billing-Status des Projekts.

Drei Randbedingungen prägen das Design:

1. **Kein Vendor-Lock-in.** Der Provider wird zur Aufrufzeit gewählt (`--provider`); ein Backend hinzuzufügen oder zu entfernen darf den gemeinsamen CLI-, Output- und Sidecar-Vertrag nicht berühren.
2. **Sichere Defaults.** Der Default-Provider muss ein echtes, dokumentiertes Free-Tier und eine klare Output-Lizenz haben. Ein Provider mit Datenschutz- oder Lizenzrisiko darf niemals Default sein und muss diese Risiken vor der ersten Nutzung sichtbar machen.
3. **Ehrliche Fehler.** Provider-Fehler-Bodies müssen durchgereicht, nicht verschluckt werden; ein dauerhafter `limit: 0`- / Billing-erforderlich-Zustand muss von einem temporären Rate-Limit unterschieden werden.

## Ziele

- Ein Aufruf verwandelt einen Text-Prompt in eine Bilddatei an einem von der Betreiberin gewählten Pfad, über jeden konfigurierten Provider.
- Der Default-Provider (`cloudflare`) braucht kein Billing und trägt eine klare Output-Lizenz.
- Jedes generierte Bild trägt ein Sidecar mit genug Metadaten, um den Aufruf zu reproduzieren oder zu auditieren, inklusive des erzeugenden Providers.
- Datenschutz- oder lizenzkritische Provider sind nur hinter expliziten, bestätigten Schutzplanken nutzbar.

## Nicht-Ziele

- In-Painting und Mehrschritt-Verfeinerung — das Tool generiert in einem Terminal-Aufruf. Referenzbild-konditionierte Generierung mit dem `cloudflare`-Modell `flux-2-klein-4b` **ist** im Geltungsbereich (dieses Modell vereint Generierung und Bearbeitung in einem Endpunkt); ein iterativer Bearbeitungs-Workflow nicht.
- Batch-Pipelines (n Prompts pro Job) — ein Prompt pro Aufruf (`-n` fordert mehrere Bilder **desselben** Prompts an).
- Ein lokaler/selbst-gehosteter Provider (`stable-diffusion.cpp`) — ein geplanter Folgeschritt, in dieser Iteration außerhalb des Geltungsbereichs.
- Garantieren, dass ein Provider kostenlos bleibt — Kontingente liegen in der Hand der Anbieter.
- Midjourney als Provider — es bietet keine skriptbare, vom Terminal aus erreichbare Text-zu-Bild-API und fehlt daher bewusst in der festen `--provider`-Registry. `spec/design/graphic-prompt-authoring/` darf ein Midjourney-Ziel-Prompt-Dokument verfassen, doch dieses Tool generiert nie gegen Midjourney; die beiden Specs treffen sich nur am Prompt-Artefakt, nicht an einem gemeinsamen Backend.

## Anforderungen

### Provider-agnostisch (gemeinsame Schicht)
- **MUSS [MUST]** den Provider via `--provider` aus einer festen Registry wählen; der Default **MUSS [MUST]** `cloudflare` sein.
- **MUSS [MUST]** jede Provider-Credential ausschließlich aus Umgebungsvariablen lesen; **MUSS NICHT [MUST NOT]** einen Key via CLI-Flag oder Config-Datei akzeptieren und **MUSS NICHT [MUST NOT]** irgendeine Credential loggen, echoen oder schreiben (auch nicht in Fehlern und Sidecars).
- **MUSS [MUST]** einen expliziten Zielpfad (`--out`) verlangen; kein stilles Default auf das Arbeitsverzeichnis. **MUSS [MUST]** das Überschreiben einer existierenden Zieldatei ohne ausdrückliche Bestätigung (`--force`) verweigern.
- **MUSS [MUST]** neben jedes Bild ein `<image>.meta.json`-Sidecar schreiben, das mindestens `provider`, `model`, `source`, `prompt`, `timestamp` (RFC 3339 UTC) und `mime_type` enthält. `model` **MUSS [MUST]** die konkrete Modell-ID tragen, die der Aufruf tatsächlich verwendet hat (bei `cloudflare` die vollständige `@cf/…`-ID), nie einen Provider-Alias.
- **MUSS [MUST]**, wenn der Aufruf Referenzbilder übergeben hat, dem Sidecar eine Liste `reference_images` mit Basisname und SHA-256-Digest jedes Bildes hinzufügen, damit die Konditionierungs-Eingaben auditierbar sind; das Sidecar **DARF NICHT [MUST NOT]** die Bildbytes oder einen absoluten Pfad tragen.
- **MUSS [MUST]** HTTP 429 als terminal für den Aufruf behandeln (kein automatisches Retry) und **MUSS [MUST]** einen `limit: 0`- / Billing-erforderlich-Zustand (Retry hilft nie) von einem temporären Rate-Limit unterscheiden, mit jeweils handlungsfähiger Meldung.
- **MUSS [MUST]** den tatsächlichen Fehler-Response-Body des Providers (nicht nur den Statuscode) in der an die Betreiberin gerichteten Meldung sichtbar machen.
- **MUSS [MUST]** HTTP 401/403 als terminalen Auth-Fehler behandeln, der auf die Credential-Seite des Providers verweist; jeder andere Fehler (Netzwerk, DNS, Filesystem, fehlerhafte Antwort) **MUSS [MUST]** eine lesbare Meldung und einen Exitcode ungleich null erzeugen, niemals einen rohen Stacktrace als einzige Ausgabe.
- **SOLLTE [SHOULD]** das Format aus der Ziel-Endung ableiten und bei MIME-Abweichung warnen (nicht scheitern); das Bild wird trotzdem geschrieben, weil das Kontingent bereits verbraucht ist.
- **MUSS [MUST]** einen einmaligen, digest-versionierten Bestätigungsmechanismus anbieten, **pro Provider** gekeyed unter `$XDG_STATE_HOME/nolte-shared/image-generate/<provider>/ack`, für Provider, die einen Hinweis deklarieren.
- **MUSS [MUST]** das mitgelieferte Skript über `${CLAUDE_PLUGIN_ROOT}` statt über einen repo-relativen Pfad aufrufen, damit der Skill aus jedem Consumer-Repository funktioniert, das das Plugin installiert (das Skript liegt im installierten Plugin-Verzeichnis, nicht im Arbeitsbaum des Consumers); nur Daten-Pfade (`--out`, `--from-prompt-doc`) bleiben relativ zum Arbeitsverzeichnis des Consumers.

### `cloudflare` (Default)
- **MUSS [MUST]** Cloudflare Workers AI mit `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID` aufrufen; Fehlen einer der beiden ergibt einen Setup-Hinweis, der beide nennt sowie das Free-Tier-Neuronen-Budget. Kein Datenschutz-/Lizenzhinweis erforderlich.
- **MUSS [MUST]** genau zwei Modelle anbieten, gewählt über `--model`: `flux-1-schnell` → `@cf/black-forest-labs/flux-1-schnell` (der Default) und `flux-2-klein-4b` → `@cf/black-forest-labs/flux-2-klein-4b`. Beide tragen Apache-2.0-Modellgewichte (siehe §Quellen); ein unbekannter `--model`-Wert ist ein Usage-Fehler.
- **DARF NICHT [MUST NOT]** `flux-2-klein-9b` oder `flux-2-dev` anbieten: beide tragen die FLUX Non-Commercial License. Die Lizenzgrenze verläuft *innerhalb* der Klein-Familie; die Apache-2.0-Eigenschaft ist also eine Eigenschaft einer Modell-ID, nie des `cloudflare`-Providers, und jedes Dokument, das sie behauptet, **MUSS [MUST]** das Modell nennen, für das sie gilt.
- **MUSS [MUST]** `flux-1-schnell` als Default behalten, bis ein Live-Aufruf die Antwortform von Klein 4B bestätigt hat (siehe §Offene Fragen) und die Betreiberin die höheren Neuronen-Kosten akzeptiert: nach geltender Preisliste kostet ein 1024×1024-Bild ≈ 58 Neuronen auf schnell (4 Kacheln × 4,80 + 4 Steps × 9,60) und ≈ 104 Neuronen auf Klein 4B (4 Output-Kacheln × 26,05), sodass der freie 10.000-Neuronen-Tag grob 170 gegenüber 95 Bildern ergibt.
- **MUSS [MUST]** auf dem `flux-1-schnell`-Pfad den JSON-Body (`prompt`, `steps`, optional `seed`) senden und das base64-kodierte `result.image` dekodieren; dieser Endpunkt exponiert kein `width`/`height`, daher **MUSS [MUST]** das Tool auf stderr warnen, wenn eine nicht-standardmäßige Größe übergeben wird, und **DARF NICHT [MUST NOT]** stillschweigend vorgeben, sie sei berücksichtigt worden.
- **MUSS [MUST]** auf dem `flux-2-klein-4b`-Pfad `multipart/form-data` senden (die einzige vom Schema akzeptierte Eingabeform) mit `prompt`, `width`, `height` (je 256–1920 laut Changelog; die Endpunkt-Defaults sind 1024×768) und optionalem `seed`; **DARF NICHT [MUST NOT]** `steps` senden, das der Endpunkt fest auf 4 setzt. Der Encoder bleibt stdlib-only (`urllib`, kein `requests`).
- **MUSS [MUST]** auf dem Klein 4B-Pfad beide dokumentierten Antwortformen akzeptieren und anhand des Response-`Content-Type` verzweigen: eine JSON-Hülle mit base64-kodiertem `result.image` (der im Roh-Schema deklarierte Output) und rohe `image/*`-Bytes (die Beschreibung im Changelog); der MIME-Typ der base64-Form wird aus den Magic Bytes ermittelt.
- **KANN [MAY]** auf dem Klein 4B-Pfad bis zu vier Referenzbilder über ein wiederholbares Flag `--ref-image <pfad>` annehmen, gesendet als Multipart-Dateiteile `input_image_0` … `input_image_3` (je < 512×512 laut Changelog). Das Flag **MUSS [MUST]** auf `flux-1-schnell` und bei jedem anderen Provider als Usage-Fehler vor jedem Netzwerkaufruf abgelehnt werden; ein nicht lesbarer Pfad ist ein Laufzeitfehler vor jedem Netzwerkaufruf. Das Tool **DARF NICHT [MUST NOT]** das Größenlimit clientseitig erzwingen; der Fehler-Body des Endpunkts wird gemäß der gemeinsamen Schicht wörtlich durchgereicht. Referenzbilder werden zu Cloudflare hochgeladen, und die Dokumentation des Skills **MUSS [MUST]** das sagen.
- **SOLLTE [SHOULD]** für diesen Provider den Modell-Invarianten aus `spec/design/flux-image-generation/` folgen: natürlichsprachige Prompts (keine SDXL-Komma-Tags oder Prompt-Gewichte), `guidance = 0`, `steps ≤ 8` und keine Negative Prompts (Unerwünschtes positiv formuliert).

### `pollinations`
- **MUSS [MUST]** bei jedem Request `private=true` erzwingen (Opt-out vom öffentlichen Feed) und **MUSS NICHT [MUST NOT]** ein CLI-Flag anbieten, das dies deaktiviert.
- **MUSS [MUST]** einen einmaligen Disclaimer präsentieren, mit Bestätigung vor der ersten Nutzung, der abdeckt: den öffentlichen-Feed-Default; dass `private=true` nur ein Feed-Opt-out ist und **keine** Nicht-Speicherungs-Garantie (Response-Caches bleiben laut Privacy Policy des Anbieters bestehen); und dass die Terms **keine explizite Output-Lizenz** gewähren (Verweis auf die Lizenz des zugrunde liegenden Modells).
- **MUSS NICHT [MUST NOT]** der Default-Provider sein.
- **MUSS [MUST]** einen Browser-typischen `User-Agent` senden; der Default-`urllib`-UA wird von Pollinations' Cloudflare-Bot-Schutz abgewiesen (HTTP 403, error 1010).

### `gemini`
- **MUSS [MUST]** die stabile Modell-ID `gemini-3.1-flash-image` und den `v1`-generativelanguage-Endpunkt fest verdrahten, niemals die `-preview`-ID, die Googles Deprecation-Tabelle als Nachfolger nennt; bezahlte `imagen-*`-Modelle und Vertex-AI-Endpunkte (`*-aiplatform.googleapis.com`) **MÜSSEN [MUST]** unerreichbar sein.
- **MUSS [MUST]** die Billing-Anforderung ausdrücklich machen (kein Gemini-Bildmodell hat ein Free-Tier), sowohl im Setup-Hinweis als auch im einmaligen Notice, und **MUSS [MUST]** dort auch das immer vorhandene SynthID-Wasserzeichen benennen.
- **SOLLTE [SHOULD]** für diesen Provider den Modell-Invarianten aus `spec/design/gemini-image-generation/` folgen: erzählende Prompts mit genannter Absicht (keine SDXL-Komma-Tags), unerwünschte Attribute positiv formuliert (es existiert kein Negative-Prompt-Parameter), in Anführungszeichen gesetzte Literale für Bild-Text und das Bewusstsein, dass jeder Output ein SynthID-Wasserzeichen trägt.

## Manueller UI-Handoff-Pfad (kein API-Aufruf)

Der `gemini`-Provider oben erfordert Billing. Eine **halbautomatische Alternative** umgeht die API vollständig und ist im Besitz der `gemini-image-handoff`-Skill: Ein Gemini-optimierter Prompt wird erzeugt, dann fügt der Operator ihn in die Gemini-Web-UI ein (die Gemini-App oder AI Studio) und lädt das Bild aus dem Chat herunter. Dieser Pfad:

- **MUSS NICHT [MUST NOT]** irgendeinen API-Aufruf machen; er trägt daher keine Billing-Anforderung und braucht keinen `GEMINI_API_KEY`.
- **MUSS [MUST]** den Prompt gemäß der Modell-Grundlage in `spec/design/gemini-image-generation/` erzeugen; die automatisierte Hälfte ist der Prompt, die manuelle Hälfte ist der UI-Schritt des Operators.
- schreibt **keine** Bilddatei und **kein** Sidecar; Dateiablage und Provenienz liegen in der Verantwortung des Operators, und der Sidecar-Vertrag oben bindet nur die API-gestützten Provider.
- **MUSS [MUST]** den SynthID-Wasserzeichen-Vorbehalt sichtbar machen (jeder Gemini-UI-Output ist mit Wasserzeichen versehen), damit eine kommerzielle oder Blog-Asset-Wahl informiert erfolgt.
- **MUSS NICHT [MUST NOT]** mit dem `gemini`-API-Provider oben vermengt werden; es ist ein eigener, netzwerkloser Pfad.

## Akzeptanzkriterien

- [ ] `--provider` defaultet auf `cloudflare`; ein unbekannter Provider ist ein Usage-Fehler.
- [ ] Statische Inspektion zeigt kein `imagen-*`-Literal und keinen `*-aiplatform.googleapis.com`-Aufruf im ausführbaren Code.
- [ ] Jedes generierte Bild hat ein `<image>.meta.json`-Sidecar mit den sechs Pflichtschlüsseln, inklusive korrektem `provider`; keine Credential erscheint in einem Sidecar.
- [ ] Bei nicht gesetzten Credentials des gewählten Providers gibt das Tool einen Setup-Hinweis aus, der die nötigen Variablen nennt, und beendet ungleich null ohne Netzwerkaufruf (cloudflare, gemini).
- [ ] Ein simuliertes HTTP 429 mit `limit: 0` ergibt eine Billing-erforderlich-Meldung (nicht „retry später"); ein 429 ohne dies ergibt eine Rate-Limit-Meldung; keines retryt.
- [ ] Ein Provider-HTTP-Fehler macht den Upstream-`error.message`-Text in der an die Betreiberin gerichteten Meldung sichtbar.
- [ ] Jede `pollinations`-Request-URL enthält `private=true`, und es gibt kein Flag, das dies deaktiviert; der erste `pollinations`-Lauf zeigt den Feed-/Lizenz-Disclaimer und verlangt Bestätigung.
- [ ] Aufruf ohne `--out` ist ein Usage-Fehler; Aufruf über eine existierende Datei wird ohne `--force` abgelehnt.
- [ ] Der Bestätigungspfad enthält den Provider-Namen; zwei Provider bestätigen unabhängig; das Überschreiben eines gespeicherten Digests löst eine erneute Aufforderung aus.
- [ ] Der manuelle UI-Handoff-Pfad macht keinen Netzwerkaufruf und schreibt kein Bild und kein Sidecar; er liefert einen der Gemini-Grundlage entsprechenden Prompt plus die UI-Eingabe- und Download-Schritte und nennt den SynthID-Vorbehalt.
- [ ] `--provider cloudflare --model flux-2-klein-4b --width 1280 --height 720` sendet einen `multipart/form-data`-Body mit `prompt`, `width=1280`, `height=720` und ohne `steps`; das `model` im Sidecar ist `@cf/black-forest-labs/flux-2-klein-4b`; sowohl eine base64-JSON- als auch eine Rohbyte-Antwort erzeugen eine Bilddatei.
- [ ] Ohne `--model` ist der `cloudflare`-Aufruf byte-identisch mit dem schnell-JSON-Body vor #638; ein nicht-standardmäßiges `--width`/`--height` auf schnell gibt eine stderr-Warnung aus und lässt den Body unverändert.
- [ ] Zwei `--ref-image`-Dateien auf Klein 4B werden zu den Multipart-Teilen `input_image_0` und `input_image_1` mit den Dateibytes, und `reference_images` im Sidecar listet beide mit ihrem SHA-256; `--ref-image` auf schnell oder bei `pollinations` beendet mit dem Usage-Code ohne Netzwerkaufruf; ein fünftes `--ref-image` ist ein Usage-Fehler.
- [ ] `grep -rn -i "apache" plugins/ docs/ spec/tools spec/design` findet keine Zeile, die Apache-2.0 dem `cloudflare`-Provider als Ganzem zuschreibt; jeder Treffer nennt `flux-1-schnell` oder `flux-2-klein-4b`.

## Offene Fragen

- Ein lokaler/selbst-gehosteter Provider (`stable-diffusion.cpp`: null laufende Kosten, voller Datenschutz, keine Rate-Limits) ist das geplante nächste Backend; hier zurückgestellt wegen seiner Build-/Modell-Download-/GPU-Setup-Oberfläche.
- **Die Antwortform von Klein 4B ist live nicht belegt.** Cloudflares Roh-Modellschema deklariert den Output als base64-`image`-String, während das Launch-Changelog rohe Bildbytes beschreibt; beim Verfassen dieser Anforderung wurde kein Live-Aufruf gemacht (in jener Session lagen keine Cloudflare-Credentials vor). Das Tool akzeptiert beide Formen; die klärende Beobachtung ist ein authentifizierter `curl` gegen den Endpunkt, der zugleich entscheidet, ob Klein 4B Default werden darf.
- **Cloudflares Umgang mit hochgeladenen Referenzbildern** (Aufbewahrung, Trainingsausschluss) wurde für #638 nicht erneut gelesen; die Anforderung fügt daher keinen Consent-Hinweis hinzu und verpflichtet stattdessen die Dokumentation, klar zu sagen, dass Referenzbilder hochgeladen werden. Erneut prüfen, falls sich Cloudflares Seite „Your Data and Workers AI" ändert oder ein Konsument die Garantie ausbuchstabiert braucht.
- Pollinations' Output-Lizenz und Prompt-Retention bleiben extern undokumentiert (Upstream-Issue #8741 ungelöst). Die Schutzplanke (erzwungenes `private=true` + Disclaimer) ist die Minderung; erneut prüfen, falls Pollinations formale Terms veröffentlicht.
- Ob `candidateCount` und `seed` den Bildpfad erreichen, ist unverifiziert: Die `v1`-`generateContent`-Bildbeispiele zeigen keines der beiden Felder, während der Provider beide weiterhin sendet, übernommen aus dem `v1beta`-Aufruf gegen das abgekündigte Modell. Die Klärung braucht einen abgerechneten Aufruf, daher sind `-n` und `--seed` beim `gemini`-Provider unbelegt statt bekannt gut. Ein einfacher Aufruf sendet nur `contents`, wie der dokumentierte `v1`-Minimalaufruf, und trägt damit kein Feld, das der Endpunkt abweisen könnte. Google führt seine Bild-Dokumentation außerdem inzwischen mit der Interactions-API an und bezeichnet `generateContent` als Legacy, dokumentiert es aber weiterhin für Bildmodelle; der Oberflächenwechsel ist zurückgestellt, weil diese Migration von einem Abschaltdatum getrieben war.

## Quellen

Die Gemini-Billing-Aussagen in §Kontext und §`gemini` sind Author-Time-externe Aussagen, trianguliert gemäß `spec/claude/research-triangulate/` §"Author-Time-Aussagen" (Author-Time-Stufe: mindestens drei unabhängige Quellen, Primary-first geordnet). Sie verdienen die strengere Behandlung, weil eine frühere Revision dieser Fähigkeit auf der umgekehrten Prämisse aufgebaut war. Abrufdatum: 2026-07-24 für die beiden GitHub-Issue-Quellen; 2026-09-12 für jede Google-Seite, bei der Migration auf `gemini-3.1-flash-image` erneut geprüft, und für die zwei damit ergänzten unabhängigen Tracker.

- **Kein Gemini-Bildgenerierungsmodell der Gemini Developer API hat ein Free-Tier; Aufrufe von `gemini-3.1-flash-image` ohne Billing scheitern an einer auf null gesetzten Free-Tier-Quota-Metrik**: Google, „Gemini Developer API pricing", dessen Free-Tier-Zeile für jedes Bildmodell „Not available" liest (Primary), <https://ai.google.dev/gemini-api/docs/pricing>; Home-Assistant-Core-Issue #157289 (Secondary), <https://github.com/home-assistant/core/issues/157289>; `googleapis/js-genai`-Issue #1322 (Secondary), <https://github.com/googleapis/js-genai/issues/1322>.
- **Der vorherige Pin ist abgekündigt: `gemini-2.5-flash-image` wird am 2026-10-02 abgeschaltet, und der Provider verdrahtet jetzt die stabile `gemini-3.1-flash-image`**: Google, „Gemini API model deprecations", das `gemini-3.1-flash-image-preview` als Ersatz nennt (Primary), <https://ai.google.dev/gemini-api/docs/deprecations>; Google, „Gemini API models", das `gemini-3.1-flash-image` als stabil führt (Primary), <https://ai.google.dev/gemini-api/docs/models>; ein unabhängiger Retirement-Tracker mit demselben Datum (Secondary), <https://vorplabs.com/models/google-model-retirements>; eine unabhängige Migrationsdarstellung, die darauf hinweist, dass der genannte Ersatz eine Preview-ID ist (Secondary), <https://www.aifreeapi.com/en/posts/gemini-2-5-flash-image-replacement>.

Die `cloudflare`-Modellaussagen in §`cloudflare` (Modell-IDs, Lizenzen, Request-Form, Parameter, Preise) wurden am 2026-09-19 für #638 direkt von den Primärseiten gelesen, nachdem die Analyse des Issues selbst auf Suchzusammenfassungen angewiesen war:

- **`@cf/black-forest-labs/flux-2-klein-4b` existiert auf Workers AI, nimmt ausschließlich `multipart/form-data` und deklariert einen base64-`image`-Output**: Cloudflare-Modellseite und Roh-Schema (`required: ["multipart"]`; Output `image: "Generated image as Base64 string."`) (Primary), <https://developers.cloudflare.com/workers-ai/models/flux-2-klein-4b/>.
- **Parameter `prompt`, `width`/`height` 256–1920, `seed`, `guidance`, `input_image_0`–`input_image_3` (< 512×512), `steps` fest auf 4; der Launch-Post beschreibt rohe Bildbytes als Antwort**: Cloudflare-Changelog 2026-01-15 (Primary), <https://developers.cloudflare.com/changelog/post/2026-01-15-flux-2-klein-4b-workers-ai/>.
- **Die Gewichte von FLUX.2 Klein 4B sind Apache-2.0 („Open weights available for commercial use under the Apache 2.0 license")**: Hugging-Face-Modellkarte (Primary), <https://huggingface.co/black-forest-labs/FLUX.2-Klein-4B>.
- **Freikontingent von 10.000 Neuronen/Tag ohne modellbezogenen Ausschluss; Klein 4B mit 5,37 Neuronen pro Input-Kachel und 26,05 pro Output-Kachel, schnell mit 4,80 pro Kachel plus 9,60 pro Step; Klein 9B und dev separat bepreist**: Cloudflare-Workers-AI-Pricing (Primary), <https://developers.cloudflare.com/workers-ai/platform/pricing/>.
- **`flux-1-schnell` trägt keinen Deprecation-Hinweis und akzeptiert weiterhin `prompt` (1–2048), `steps` (≤ 8, Default 4), `seed` mit base64-JSON als Antwort**: Cloudflare-Modellseite (Primary), <https://developers.cloudflare.com/workers-ai/models/flux-1-schnell/>.
- **Klein 9B und FLUX.2 [dev] tragen die FLUX Non-Commercial License**: aus den Quellen des Issues übernommen (`black-forest-labs/flux2` Issue #32 und `LICENSE-FLUX-DEV`), am 2026-09-19 nicht erneut gelesen; die Anforderung stützt sich nur negativ darauf (keines der beiden Modelle wird angeboten).

Verifiziert 2026-07-24 und bei der Migration am 2026-09-12 erneut geprüft, mit zwei Einschränkungen, die die Anforderungen oben bewusst aus der Meldung an den Operator heraushalten. Erstens veröffentlicht Google keine numerische Free-Tier-Request-Tabelle je Modell mehr, weshalb der belastbare Beleg die „Not available"-Zeile der Preisseite ist und keine Kontingentzahl. Zweitens ist ein `limit: 0`-Body kein Beweis dafür, dass einem Projekt Billing fehlt: Im Februar 2026 wurde berichtet, dass auch zahlende Tier-1-Projekte bei Bildmodellen gegen dieselbe auf null gesetzte Free-Tier-Quota-Metrik liefen (<https://discuss.ai.google.dev/t/bug-paid-tier-1-account-getting-free-tier-requests-limit-0-on-image-generation-models-gemini-2-5-flash-image-gemini-3-pro-image-preview/123906>), sodass die Anforderung aus §„Provider-agnostisch (gemeinsame Schicht)", die `error.message` des Upstreams wörtlich durchzureichen, diesen Fall diagnostizierbar hält.
