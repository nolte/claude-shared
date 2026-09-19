---
title: Bildgenerierung
audience: [maintainer, external-contributor]
content_mode: how-to
track: developer-docs
last_updated: 2026-09-19
---

# Bildgenerierung

Der Skill `image-generate` verwandelt einen Text-Prompt in eine Bilddatei auf der Platte. Das läuft vollständig über die Kommandozeile. So fügt er sich in jede Pipeline ein. Er hat **austauschbare Provider-Backends** (gewählt über `--provider`). So ist die Fähigkeit nicht an Preise oder Verfügbarkeit eines einzelnen Anbieters gebunden.

Die deterministische Engine ist ein reines Stdlib-Skript: `plugins/nolte-media/skills/image-generate/scripts/image_generate.py`. Der Skill ist die Hülle, über die Betreiber diese Engine bedienen.

## Provider im Überblick

| `--provider` | Benötigte Credentials | Kostenlos? | Output-Lizenz | Wofür |
|---|---|---|---|---|
| `cloudflare` (**Default**) | `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID` | Ja, echtes Free-Tier (keine Karte) | FLUX.1-schnell (Default) oder FLUX.2 Klein 4B über `--model`, beide Apache-2.0; Output gehört dir | Blog- und Produktionsbilder; Klein 4B für nicht-quadratische Formate und Referenzbilder |
| `pollinations` | keine (optional `POLLINATIONS_API_TOKEN`) | Ja, auth-frei | Keine explizite Lizenz (Verweis aufs Modell); öffentlicher Feed als Default | Schnelle Wegwerf-Bilder |
| `gemini` | `GEMINI_API_KEY` | Nein, **erfordert Billing** | Kommerzielle Nutzung erlaubt | Nur, wenn ohnehin bezahlt |

**Empfehlung:** Für alles, was du veröffentlichst, `cloudflare` nutzen. Es ist kostenlos und trägt kein Wasserzeichen und keinen öffentlichen Feed. Beide Modelle, FLUX.1-schnell und FLUX.2 Klein 4B, sind Apache-2.0 — die generierten Bilder gehören also klar dir. Die Lizenz ist eine Eigenschaft des Modells, nicht des Providers: Cloudflare hostet auch `flux-2-klein-9b` und `flux-2-dev` unter der FLUX Non-Commercial License, und das Tool bietet sie bewusst nicht an. `pollinations` ist für Wegwerf-Bilder okay, gewährt aber keine explizite Output-Lizenz. `gemini` braucht ein bezahltes Projekt; das Free-Tier-Kontingent dieses Bildmodells ist null.

## Welchen Token braucht welcher Provider?

### Cloudflare (Default, empfohlen)

Cloudflare Workers AI betreibt FLUX.1-schnell und FLUX.2 Klein 4B auf einem echten Free-Tier. Es gilt täglich neu (10.000 Neuronen/Tag, keine Karte). Du brauchst zweierlei: einen **Token** und deine **Account-ID**.

1. Kostenlosen Account anlegen unter <https://dash.cloudflare.com/sign-up> (keine Karte nötig).
2. Im Dashboard zu **AI → Workers AI → "Use REST API"** gehen.
3. **"Create a Workers AI API Token"** klicken. Cloudflare füllt die richtigen Rechte vorab aus:
   - `Account` · `Workers AI` · **Read**
   - `Account` · `Workers AI` · **Edit** (das ist nötig, denn das Generieren eines Bildes ist eine `run`-/Edit-Aktion)
4. Token erstellen und kopieren (nur einmal angezeigt).
5. Die **Account-ID** von derselben Seite kopieren.

Dann beide exportieren (das Tool liest sie nur aus der Umgebung, nie als Flag):

```bash
export CLOUDFLARE_API_TOKEN="dein_token"
export CLOUDFLARE_ACCOUNT_ID="deine_account_id"
```

Das Free-Tier setzt täglich zurück. FLUX.1-schnell kostet etwa 58 Neuronen pro 1024x1024-Bild (4,8 pro 512x512-Kachel plus 9,6 pro Step), FLUX.2 Klein 4B etwa 104 (26 pro Output-Kachel). 10.000 Neuronen/Tag sind also grob 170 schnell-Bilder oder 95 Klein-4B-Bilder.

### Pollinations (auth-frei)

Kein Token erforderlich. Optional `POLLINATIONS_API_TOKEN` setzen, um das Wasserzeichen anonymer Requests zu entfernen. Der erste Lauf zeigt einen einmaligen Disclaimer, den du bestätigen musst (öffentlicher Feed, keine explizite Output-Lizenz).

### Gemini (Billing erforderlich)

`GEMINI_API_KEY` von <https://aistudio.google.com/apikey> setzen. Beachte: kein Gemini-Bildmodell ist im Free-Tier (das Free-Tier-Kontingent ist `0`), `gemini-3.1-flash-image` eingeschlossen. Das Projekt muss Billing aktiviert haben. Sonst gibt jeder Aufruf einen Billing-erforderlich-Fehler zurück.

## Ein Bild generieren

Der Default-Provider ist `cloudflare`, dafür ist also kein `--provider` nötig:

```bash
# über das Taskfile (Skript-Args nach -- übergeben)
task image:generate -- --prompt "a minimalist teal fox icon, flat" --out fox.jpg

# oder direkt
python3 "${CLAUDE_PLUGIN_ROOT}/skills/image-generate/scripts/image_generate.py" \
    --prompt "a minimalist teal fox icon, flat" --out fox.jpg
```

Backend wechseln mit `--provider`:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/image-generate/scripts/image_generate.py" \
    --provider pollinations --prompt "a tree, comic style" --out tree.jpg --accept-data-policy
```

Jeder Lauf schreibt das Bild. Dazu kommt ein `<image>.meta.json`-Sidecar mit `provider`, `model`, `source`, `prompt`, `timestamp` und `mime_type`.

Nützliche Flags: `--from-prompt-doc <doc> --variant light|dark` (ein `graphic-prompt-generator`-Dokument rendern), `-n <N>` (mehrere Bilder desselben Prompts), `--seed`, `--width`/`--height`, `--model` und `--ref-image` (nur Cloudflare, siehe unten), `--force` (vorhandene Datei überschreiben).

## Das Cloudflare-Modell wählen

`--provider cloudflare` bietet zwei Modelle, gewählt über `--model`:

| `--model` | Lizenz | Größensteuerung | Referenzbilder | Kosten pro 1024x1024-Bild |
|---|---|---|---|---|
| `flux-1-schnell` (**Default**) | Apache-2.0 | keine: immer etwa 1024x1024, `--width`/`--height` werden mit Warnung ignoriert | nein | etwa 58 Neuronen |
| `flux-2-klein-4b` | Apache-2.0 | `--width`/`--height` werden berücksichtigt, je 256 bis 1920 | bis zu vier `--ref-image`-Dateien, je unter 512x512 | etwa 104 Neuronen |

Ein breites Hero-Bild rendern und auf ein Referenzbild konditionieren:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/image-generate/scripts/image_generate.py" \
    --model flux-2-klein-4b --width 1280 --height 720 \
    --ref-image design/mascot-ref.png \
    --prompt "the mascot waving in front of a sunrise, flat illustration" --out hero.png
```

Das Sidecar hält dann `model: @cf/black-forest-labs/flux-2-klein-4b` und eine Liste `reference_images` mit Name und SHA-256-Digest jeder Datei fest. Referenzbilder werden als Teil des Requests zu Cloudflare hochgeladen; halte vertrauliches Material daraus heraus. `--model` und `--ref-image` werden bei jedem anderen Provider mit einem Usage-Fehler abgelehnt, `--ref-image` zusätzlich bei `flux-1-schnell`.

`flux-1-schnell` bleibt der Default, weil es pro Bild etwa halb so viel kostet und sein Antwortformat lange verifiziert ist; die Antwortverarbeitung für Klein 4B deckt beide von Cloudflare dokumentierten Formen ab (base64-JSON und Rohbytes), ist aber noch nicht gegen einen Live-Aufruf bestätigt.

!!! tip
    FLUX.1-schnell und Pollinations liefern beide JPEG. Nutze ein `.jpg`-Ziel, um die Warnung zur Endungs-/MIME-Abweichung zu vermeiden (das Bild wird so oder so geschrieben). Das Format von Klein 4B wird aus der Antwort erkannt; richte die Endung nach dem `mime_type` im Sidecar aus.

## Nutzung in einem anderen Repo

Wenn das `nolte-media`-Plugin in einem anderen Repository installiert ist, ist diese Fähigkeit dort als `/nolte-media:image-generate` erreichbar — es wird nichts ins Consumer-Repo kopiert. Der Skill ruft das mitgelieferte Skript über `${CLAUDE_PLUGIN_ROOT}` auf. Diese Variable zeigt in jedem Kontext auf das installierte Plugin-Verzeichnis (Marketplace-Installation und `claude --plugin-dir ./plugins/nolte-media`-Dogfooding). So funktioniert derselbe Befehl überall:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/image-generate/scripts/image_generate.py" \
    --prompt "a teal fox icon, flat" --out fox.jpg
```

Nur der *Skript*-Pfad ist plugin-relativ. Daten-Pfade (`--out`, `--from-prompt-doc`) bleiben relativ zum Arbeitsverzeichnis des Consumers. Die Abkürzung `task image:generate` ist `claude-shared`-lokal: sie führt das repo-relative Skript außerhalb von Claude aus. Consumer-Repos nutzen stattdessen den Slash-Command.

## Teil einer Asset-Pipeline

Das Tool schließt eine dreistufige Asset-Pipeline:

1. `graphic-prompt-generator` (Agent) verfasst ein brand-konformes Prompt-Dokument unter `design/prompts/`.
2. `image-generate` rendert es: `--from-prompt-doc design/prompts/hero.md --variant dark --out hero.jpg`.
3. `png-to-transparent-svg` (Agent) vektorisiert das Ergebnis für ein Icon oder Logo.

## Exit-Codes

`0` Erfolg · `1` Laufzeitfehler (Netzwerk, Filesystem, fehlerhafte Antwort) · `2` Usage-Fehler · `3` Rate-Limit / Kontingent / Billing-erforderlich · `4` Auth-Fehler. Bei `429` wird nichts automatisch wiederholt.
