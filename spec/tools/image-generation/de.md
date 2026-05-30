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

### `cloudflare` (Default)
- **MUSS [MUST]** Cloudflare Workers AI FLUX.1-schnell (Apache-2.0-Output) mit `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID` aufrufen; Fehlen einer der beiden ergibt einen Setup-Hinweis, der beide nennt sowie das Free-Tier-Neuronen-Budget. Kein Datenschutz-/Lizenzhinweis erforderlich.

### `pollinations`
- **MUSS [MUST]** bei jedem Request `private=true` erzwingen (Opt-out vom öffentlichen Feed) und **MUSS NICHT [MUST NOT]** ein CLI-Flag anbieten, das dies deaktiviert.
- **MUSS [MUST]** einen einmaligen Disclaimer präsentieren, der den öffentlichen-Feed-Default und die **undokumentierte Output-Lizenz** abdeckt, mit Bestätigung vor der ersten Nutzung.
- **MUSS NICHT [MUST NOT]** der Default-Provider sein.
- **MUSS [MUST]** einen Browser-typischen `User-Agent` senden; der Default-`urllib`-UA wird von Pollinations' Cloudflare-Bot-Schutz abgewiesen (HTTP 403, error 1010).

### `gemini`
- **MUSS [MUST]** die Modell-ID `gemini-2.5-flash-image` und den `v1beta`-generativelanguage-Endpunkt fest verdrahten; bezahlte `imagen-*`-Modelle und Vertex-AI-Endpunkte (`*-aiplatform.googleapis.com`) **MÜSSEN [MUST]** unerreichbar sein.
- **MUSS [MUST]** die Billing-Anforderung explizit machen (das Free-Tier-Kontingent des Modells ist 0) — sowohl im Setup-Hinweis als auch im einmaligen Hinweis.

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

## Offene Fragen

- Ein lokaler/selbst-gehosteter Provider (`stable-diffusion.cpp`: null laufende Kosten, voller Datenschutz, keine Rate-Limits) ist das geplante nächste Backend; hier zurückgestellt wegen seiner Build-/Modell-Download-/GPU-Setup-Oberfläche.
- Pollinations' Output-Lizenz und Prompt-Retention bleiben extern undokumentiert (Upstream-Issue #8741 ungelöst). Die Schutzplanke (erzwungenes `private=true` + Disclaimer) ist die Minderung; erneut prüfen, falls Pollinations formale Terms veröffentlicht.
