# Gemini-Bildgenerierung (Free-Tier)

Status: draft

## Kontext

Bildgenerierung soll vom Terminal aus erreichbar sein — Prompt rein, Bilddatei auf der Platte raus — ohne eine Chat-UI zu öffnen. Die Gemini API von Google bietet ein Free-Tier-Bildmodell (`gemini-2.5-flash-image`), das diesen Bedarf ohne Billing-Einrichtung und ohne Risiko versehentlicher kostenpflichtiger Nutzung deckt.

Diese Spec regelt, wie diese Fähigkeit innerhalb dieses Repositories operationalisiert wird. Ein zukünftiger Skill oder Agent (Arbeitstitel: `gemini-image-generate`) wird sie umsetzen. Die Spec entsteht zuerst, damit der Skill/Agent dagegen geprüft werden kann (siehe `spec/claude/skill-management/` und `spec/claude/agent-management/`).

Zwei Randbedingungen prägen jede Entscheidung hier:

1. **Ausschließlich Free-Tier.** Kein Aufrufpfad darf ein kostenpflichtiges Gemini-Modell ansprechen (`imagen-*`, Vertex AI). Das wird im Code durchgesetzt, nicht nur per Konvention.
2. **Free-Tier-Prompts werden für das Modelltraining verwendet.** Die Betreiberin MUSS [MUST] vor dem ersten Bild darüber informiert werden.

Außerdem: Die Modell-ID `gemini-2.5-flash-image` ist in dieser Spec bewusst versions-fest verdrahtet; ein zukünftiges Free-Tier-Nachfolgemodell verlangt eine Spec-Revision, bevor die Implementierung es übernehmen darf.

## Ziele

- Ein Skill/Agent verwandelt einen Text-Prompt in eine Bilddatei am gewünschten Pfad — mit einem Aufruf.
- Aufrufe sind auf das Free-Tier-fähige Modell beschränkt; kostenpflichtige Modelle sind über diesen Codepfad nicht erreichbar.
- Fehler (fehlender Key, Rate-Limit, Auth) ergeben handlungsfähige Meldungen — keine stillen Abstürze, keine automatischen Retries, die das Free-Tier-Kontingent verbrennen.
- Jedes erzeugte Bild trägt ein Sidecar mit ausreichend Metadaten, um den Aufruf zu reproduzieren oder zu auditieren.
- Die Betreiberin wird einmal, explizit, darüber informiert, dass Free-Tier-Eingaben in das Modelltraining fließen.

## Nicht-Ziele

- Imagen-Modelle (`imagen-3.0-*`, `imagen-4.0-*`) — nur kostenpflichtig, außerhalb dieser Spec.
- Vertex-AI-Endpunkte — kostenpflichtig, benötigen GCP-Projekt-Setup, außerhalb dieser Spec.
- Bild-Editing / In-Painting / mehrstufige Verfeinerung — anderer Funktionsraum; diese Spec deckt ausschließlich Text-zu-Bild ab.
- Batch-Pipelines (n Bilder über viele Prompts in einem Job) — kann eine Folge-Spec sein; der Skill/Agent hier behandelt einen Prompt pro Aufruf.
- Self-hosted-Alternativen (Stable Diffusion, lokale Diffusers) — anderes Betriebsmodell.

## Anforderungen

- **MUSS [MUST]** `gemini-2.5-flash-image` als einzige Modell-ID verwenden. Die Modell-ID ist eine fest verdrahtete Allowlist-Konstante in der Implementierung, kein freier Parameter.
- **MUSS [MUST]** ausschließlich den Google-AI-Studio-Endpunkt der Generative Language API ansprechen: `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent`. Vertex-AI-Endpunkte (`*-aiplatform.googleapis.com`) sind verboten.
- **MUSS [MUST]** den API-Schlüssel aus der Umgebungsvariable `GEMINI_API_KEY` lesen. Keine CLI-Flag, keine Config-Datei, keine Aufforderung an die Betreiberin, einen Key in den Chat zu kleben.
- **MUSS [MUST]** den API-Schlüssel niemals loggen, echoen oder in Dateien schreiben — auch nicht in Fehlermeldungen, Traces oder Sidecar-Dateien.
- **MUSS [MUST]** HTTP 429 (Rate-Limit / Kontingent erschöpft) als terminalen Fehler des aktuellen Aufrufs behandeln: klare Meldung an die Betreiberin, Exit. Automatisches Retry ist verboten, weil jeder Retry zusätzliches Free-Tier-Kontingent verbrennt.
- **MUSS [MUST]** HTTP 401 / 403 (Auth-Fehler) als terminalen Fehler mit einer Meldung behandeln, die auf `https://aistudio.google.com/apikey` verweist.
- **MUSS [MUST]** für jeden Fehler, der nicht von den spezifischen HTTP-Fehler-Regeln oben abgedeckt ist, eine handlungsfähige Fehlermeldung ausgeben und mit Exitcode ungleich null beenden — einschließlich Netzwerkfehlern, DNS-Auflösungsfehlern, fehlerhaften API-Antworten, Filesystem-Berechtigungsfehlern und fehlenden Eltern-Verzeichnissen.
- **MUSS [MUST]** den Zielpfad explizit von der Betreiberin verlangen. Kein stilles Default auf das aktuelle Arbeitsverzeichnis.
- **MUSS [MUST]** das Überschreiben einer existierenden Zieldatei ohne ausdrückliche Bestätigung im selben Aufruf verweigern.
- **MUSS [MUST]** vor der ersten erfolgreichen Generierung in einer Umgebung einen einmaligen Datenschutzhinweis anzeigen:
  > „Free-Tier-Prompts und erzeugte Bilder werden von Google zum Trainieren und Verbessern ihrer Modelle verwendet. Übermittle keine vertraulichen oder personenbezogenen Daten. Zum Abschalten muss Billing für diesen API-Key aktiviert werden — siehe https://ai.google.dev/gemini-api/terms."
  Die Bestätigung MUSS [MUST] unter `$XDG_STATE_HOME/nolte-shared/gemini-image-generation/ack` persistiert werden (Fallback `$HOME/.local/state/nolte-shared/gemini-image-generation/ack`, wenn `XDG_STATE_HOME` nicht gesetzt ist), damit die Betreiberin auf derselben Maschine über Sessions hinweg nicht erneut gefragt wird.
- **MUSS [MUST]** neben jedes erzeugte Bild eine Sidecar-Metadatendatei `<image>.meta.json` schreiben, die mindestens enthält:
  - `prompt` — der wortgetreu übermittelte Prompt
  - `model` — die verwendete Modell-ID (`gemini-2.5-flash-image`)
  - `endpoint` — die vollständige aufgerufene URL
  - `timestamp` — RFC-3339-UTC-Zeitstempel der Antwort
  - `mime_type` — der von der API zurückgegebene MIME-Typ
- **SOLLTE [SHOULD]** das Bildformat aus der Dateiendung des Zielpfads ableiten (`.png`, `.jpg`, `.webp`) und gegen den von der API zurückgegebenen MIME-Typ validieren; Abweichung ist eine Warnung, kein Abbruch.
- **SOLLTE [SHOULD]** eine freundliche Setup-Hilfe ausgeben, wenn `GEMINI_API_KEY` fehlt — mit Verweis auf `https://aistudio.google.com/apikey` und Hinweis, dass Free-Tier kein Billing-Setup verlangt.
- **SOLLTE [SHOULD]** das aktuelle Free-Tier-Rate-Limit in der 429-Fehlermeldung erwähnen, damit die Betreiberin versteht, woran sie hängt.
- **KANN [MAY]** einen optionalen `n`-Parameter für mehrere Bilder pro Aufruf akzeptieren, sofern das Modell das unterstützt; jedes Bild bekommt sein eigenes Sidecar (der Prompt wird über die Sidecars hinweg bewusst dupliziert — bekannte Konsequenz der Ein-Sidecar-pro-Bild-Konvention).
- **KANN [MAY]** einen optionalen Seed-Parameter akzeptieren, wenn das Modell deterministische Generierung unterstützt, und diesen im Sidecar festhalten.

## Akzeptanzkriterien

- [ ] Statische Inspektion der Implementierung zeigt `gemini-2.5-flash-image` als einziges Modell-ID-Literal; keine `imagen-*`-Strings auffindbar.
- [ ] Statische Inspektion zeigt keine Aufrufe gegen `*-aiplatform.googleapis.com` oder ein Vertex-AI-SDK.
- [ ] Der API-Key wird ausschließlich aus `GEMINI_API_KEY` gelesen; eine grep-Suche nach dem Key-Wert in stdout, Logs, Sidecar-JSON und Fehler-Traces liefert keine Treffer.
- [ ] Aufruf mit ungesetztem `GEMINI_API_KEY` erzeugt eine Setup-Hilfe, die die Variable benennt, auf `https://aistudio.google.com/apikey` verlinkt und erklärt, dass Free-Tier kein Billing-Setup verlangt; Exitcode ist ungleich null.
- [ ] Eine simulierte HTTP-429-Antwort führt zu einer einzigen Fehlermeldung („Free-Tier-Kontingent erschöpft…") und Exit; in HTTP-Traces sind keine Retry-Versuche zu sehen.
- [ ] Die HTTP-429-Fehlermeldung enthält eine quantitative Rate-Limit-Angabe (z.B. „10 Requests pro Minute" oder „100 Requests pro Tag").
- [ ] Eine simulierte HTTP-401-Antwort führt zu einer Auth-Fehler-Meldung mit Link auf die Key-Management-Seite; Exitcode ist ungleich null.
- [ ] Ein induzierter Netzwerk- / DNS- / Filesystem-Fehler erzeugt eine menschenlesbare Fehlermeldung und einen Exitcode ungleich null; kein stiller Crash, kein Traceback-Dump als einzige für die Betreiberin sichtbare Ausgabe.
- [ ] Der erste erfolgreiche Aufruf in einer sauberen Umgebung zeigt den Datenschutzhinweis und verlangt eine explizite Bestätigung; spätere Aufrufe — auch in einer frischen Shell-Session auf derselben Maschine — fragen nicht erneut, und die Bestätigungsdatei existiert unter dem in der MUSS deklarierten Pfad.
- [ ] Aufruf ohne Zielpfad wird mit einem Usage-Fehler abgelehnt.
- [ ] Aufruf gegen einen bestehenden Dateipfad wird abgelehnt, solange die Betreiberin Überschreiben nicht im selben Aufruf bestätigt.
- [ ] Ein Szenario, in dem Dateiendung des Zielpfads und der von der API zurückgegebene MIME-Typ nicht übereinstimmen, erzeugt eine Warnung, aber die Datei wird trotzdem geschrieben.
- [ ] Jedes erzeugte Bild hat ein `<image>.meta.json`-Sidecar mit den fünf geforderten Schlüsseln.
- [ ] Die Sidecar-JSON enthält den API-Key unter keinem Feldnamen.

## Offene Fragen

- Soll der Skill/Agent ein optionales Default-Zielverzeichnis (z.B. `$XDG_PICTURES_DIR/gemini/`) anbieten, wenn die Betreiberin den Pfad weglässt, oder ist die Pflicht zum expliziten Pfad absolut? Die aktuelle MUSS-Regel ist das sicherere Default; in der Praxis neu bewerten, falls sie Reibung erzeugt.
- Bindet die Implementierungssprache uns an ein bestimmtes SDK (Python `google-genai`, Node `@google/generative-ai`, blankes `curl`)? Der Endpunkt liegt fest; die SDK-Wahl ist Implementierungsdetail und gehört zum operationalisierenden Skill/Agent, nicht in diese Spec.
