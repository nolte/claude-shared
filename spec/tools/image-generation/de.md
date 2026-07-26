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

- Bildbearbeitung / In-Painting / Mehrschritt-Verfeinerung — ausschließlich Text-zu-Bild.
- Batch-Pipelines (n Prompts pro Job) — ein Prompt pro Aufruf (`-n` fordert mehrere Bilder **desselben** Prompts an).
- Ein lokaler/selbst-gehosteter Provider (`stable-diffusion.cpp`) — ein geplanter Folgeschritt, in dieser Iteration außerhalb des Geltungsbereichs.
- Garantieren, dass ein Provider kostenlos bleibt — Kontingente liegen in der Hand der Anbieter.
- Midjourney als Provider — es bietet keine skriptbare, vom Terminal aus erreichbare Text-zu-Bild-API und fehlt daher bewusst in der festen `--provider`-Registry. `spec/design/graphic-prompt-authoring/` darf ein Midjourney-Ziel-Prompt-Dokument verfassen, doch dieses Tool generiert nie gegen Midjourney; die beiden Specs treffen sich nur am Prompt-Artefakt, nicht an einem gemeinsamen Backend.

## Anforderungen

### Provider-agnostisch (gemeinsame Schicht)
- **MUSS [MUST]** den Provider via `--provider` aus einer festen Registry wählen; der Default **MUSS [MUST]** `cloudflare` sein.
- **MUSS [MUST]** jede Provider-Credential ausschließlich aus Umgebungsvariablen lesen; **MUSS NICHT [MUST NOT]** einen Key via CLI-Flag oder Config-Datei akzeptieren und **MUSS NICHT [MUST NOT]** irgendeine Credential loggen, echoen oder schreiben (auch nicht in Fehlern und Sidecars).
- **MUSS [MUST]** einen expliziten Zielpfad (`--out`) verlangen; kein stilles Default auf das Arbeitsverzeichnis. **MUSS [MUST]** das Überschreiben einer existierenden Zieldatei ohne ausdrückliche Bestätigung (`--force`) verweigern.
- **MUSS [MUST]** neben jedes Bild ein `<image>.meta.json`-Sidecar schreiben, das mindestens `provider`, `model`, `source`, `prompt`, `timestamp` (RFC 3339 UTC) und `mime_type` enthält.
- **MUSS [MUST]** HTTP 429 als terminal für den Aufruf behandeln (kein automatisches Retry) und **MUSS [MUST]** einen `limit: 0`- / Billing-erforderlich-Zustand (Retry hilft nie) von einem temporären Rate-Limit unterscheiden, mit jeweils handlungsfähiger Meldung.
- **MUSS [MUST]** den tatsächlichen Fehler-Response-Body des Providers (nicht nur den Statuscode) in der an die Betreiberin gerichteten Meldung sichtbar machen.
- **MUSS [MUST]** HTTP 401/403 als terminalen Auth-Fehler behandeln, der auf die Credential-Seite des Providers verweist; jeder andere Fehler (Netzwerk, DNS, Filesystem, fehlerhafte Antwort) **MUSS [MUST]** eine lesbare Meldung und einen Exitcode ungleich null erzeugen, niemals einen rohen Stacktrace als einzige Ausgabe.
- **SOLLTE [SHOULD]** das Format aus der Ziel-Endung ableiten und bei MIME-Abweichung warnen (nicht scheitern); das Bild wird trotzdem geschrieben, weil das Kontingent bereits verbraucht ist.
- **MUSS [MUST]** einen einmaligen, digest-versionierten Bestätigungsmechanismus anbieten, **pro Provider** gekeyed unter `$XDG_STATE_HOME/nolte-shared/image-generate/<provider>/ack`, für Provider, die einen Hinweis deklarieren.
- **MUSS [MUST]** das mitgelieferte Skript über `${CLAUDE_PLUGIN_ROOT}` statt über einen repo-relativen Pfad aufrufen, damit der Skill aus jedem Consumer-Repository funktioniert, das das Plugin installiert (das Skript liegt im installierten Plugin-Verzeichnis, nicht im Arbeitsbaum des Consumers); nur Daten-Pfade (`--out`, `--from-prompt-doc`) bleiben relativ zum Arbeitsverzeichnis des Consumers.

### `cloudflare` (Default)
- **MUSS [MUST]** Cloudflare Workers AI FLUX.1-schnell (Apache-2.0-Output) mit `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID` aufrufen; Fehlen einer der beiden ergibt einen Setup-Hinweis, der beide nennt sowie das Free-Tier-Neuronen-Budget. Kein Datenschutz-/Lizenzhinweis erforderlich.
- **SOLLTE [SHOULD]** für diesen Provider den Modell-Invarianten aus `spec/design/flux-image-generation/` folgen: natürlichsprachige Prompts (keine SDXL-Komma-Tags oder Prompt-Gewichte), `guidance = 0`, `steps ≤ 8` und keine Negative Prompts (Unerwünschtes positiv formuliert).

### `pollinations`
- **MUSS [MUST]** bei jedem Request `private=true` erzwingen (Opt-out vom öffentlichen Feed) und **MUSS NICHT [MUST NOT]** ein CLI-Flag anbieten, das dies deaktiviert.
- **MUSS [MUST]** einen einmaligen Disclaimer präsentieren, mit Bestätigung vor der ersten Nutzung, der abdeckt: den öffentlichen-Feed-Default; dass `private=true` nur ein Feed-Opt-out ist und **keine** Nicht-Speicherungs-Garantie (Response-Caches bleiben laut Privacy Policy des Anbieters bestehen); und dass die Terms **keine explizite Output-Lizenz** gewähren (Verweis auf die Lizenz des zugrunde liegenden Modells).
- **MUSS NICHT [MUST NOT]** der Default-Provider sein.
- **MUSS [MUST]** einen Browser-typischen `User-Agent` senden; der Default-`urllib`-UA wird von Pollinations' Cloudflare-Bot-Schutz abgewiesen (HTTP 403, error 1010).

### `gemini`
- **MUSS [MUST]** die Modell-ID `gemini-2.5-flash-image` und den `v1beta`-generativelanguage-Endpunkt fest verdrahten; bezahlte `imagen-*`-Modelle und Vertex-AI-Endpunkte (`*-aiplatform.googleapis.com`) **MÜSSEN [MUST]** unerreichbar sein.
- **MUSS [MUST]** die Billing-Anforderung explizit machen (das Free-Tier-Kontingent des Modells ist 0) — sowohl im Setup-Hinweis als auch im einmaligen Hinweis.
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

## Offene Fragen

- Ein lokaler/selbst-gehosteter Provider (`stable-diffusion.cpp`: null laufende Kosten, voller Datenschutz, keine Rate-Limits) ist das geplante nächste Backend; hier zurückgestellt wegen seiner Build-/Modell-Download-/GPU-Setup-Oberfläche.
- Pollinations' Output-Lizenz und Prompt-Retention bleiben extern undokumentiert (Upstream-Issue #8741 ungelöst). Die Schutzplanke (erzwungenes `private=true` + Disclaimer) ist die Minderung; erneut prüfen, falls Pollinations formale Terms veröffentlicht.
- Die gepinnte ID `gemini-2.5-flash-image` trägt ein veröffentlichtes Abschaltdatum, den 2026-10-02, wobei Google `gemini-3.1-flash-image` als Ersatz nennt (siehe §Quellen). Das Pinning muss daher vor diesem Datum migrieren; welchen Nachfolger der `gemini`-Provider übernimmt — und ob Billing-Anforderung, SynthID-Vorbehalt und `v1beta`-Endpunkt unverändert mitgehen — wird bei der Migrationsplanung entschieden, nicht vorsorglich hier.

## Quellen

Die Gemini-Billing-Aussagen in §Kontext und §`gemini` sind Author-Time-externe Aussagen, trianguliert gemäß `spec/claude/research-triangulate/` §"Author-Time-Aussagen" (Author-Time-Stufe: mindestens drei unabhängige Quellen, Primary-first geordnet). Sie verdienen die strengere Behandlung, weil eine frühere Revision dieser Fähigkeit auf der umgekehrten Prämisse aufgebaut war. Abrufdatum für jede Quelle unten: 2026-07-24.

- **Kein Gemini-Bildgenerierungsmodell der Gemini Developer API hat ein Free-Tier; Aufrufe von `gemini-2.5-flash-image` ohne Billing scheitern an einer auf null gesetzten Free-Tier-Quota-Metrik**: Google, „Gemini Developer API pricing", dessen Free-Tier-Zeile für jedes Bildmodell einschließlich `gemini-2.5-flash-image` und `gemini-3-pro-image` „Not available" lautet und das separat vermerkt, dass die Nutzung der Oberfläche von Google AI Studio kostenfrei ist (Primary), <https://ai.google.dev/gemini-api/docs/pricing>; Home Assistant core, Issue #157289 „Google Generative AI can no longer generate free images" mit dem Befund `Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 0` (Secondary, unabhängiger Konsument), <https://github.com/home-assistant/core/issues/157289>; googleapis `js-genai`, Issue #1322 „429 error for gemini-2.5-flash-image" mit derselben auf null gesetzten Quota-Metrik aus dem offiziellen JavaScript-SDK (Secondary), <https://github.com/googleapis/js-genai/issues/1322>
- **Die gepinnte Modell-ID ist deprecated: `gemini-2.5-flash-image` wird am 2026-10-02 abgeschaltet, und Google nennt `gemini-3.1-flash-image` als Ersatz**: Google, „Gemini API model deprecations" mit Release- und Shutdown-Datum sowie benanntem Ersatz (Primary), <https://ai.google.dev/gemini-api/docs/deprecations>; Google, „Gemini API models", das `gemini-3.1-flash-image`, `gemini-3.1-flash-lite-image` und `gemini-3-pro-image` als aktuelle stabile Bildmodelle führt (Primary), <https://ai.google.dev/gemini-api/docs/models>; Curlscape, „Google Gemini API Pricing Guide 2026", das die Bildmodelle unabhängig außerhalb des Free-Tiers und die 3.x-Linie als aktuell verortet (Tertiary), <https://curlscape.com/blog/google-gemini-api-pricing-guide-2026>

Verifiziert 2026-07-24, mit zwei Einschränkungen, die die Anforderungen oben bewusst aus der Meldung an den Operator heraushalten. Erstens veröffentlicht Google keine numerische Free-Tier-Request-Tabelle je Modell mehr, weshalb der belastbare Beleg die „Not available"-Zeile der Preisseite ist und keine Kontingentzahl. Zweitens ist ein `limit: 0`-Body kein Beweis dafür, dass einem Projekt Billing fehlt: Im Februar 2026 wurde berichtet, dass auch zahlende Tier-1-Projekte bei Bildmodellen gegen dieselbe auf null gesetzte Free-Tier-Quota-Metrik liefen (<https://discuss.ai.google.dev/t/bug-paid-tier-1-account-getting-free-tier-requests-limit-0-on-image-generation-models-gemini-2-5-flash-image-gemini-3-pro-image-preview/123906>), sodass die Anforderung aus §„Provider-agnostisch (gemeinsame Schicht)", die `error.message` des Upstreams wörtlich durchzureichen, diesen Fall diagnostizierbar hält.
