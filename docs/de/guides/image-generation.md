---
title: Bildgenerierung
audience: [maintainer, external-contributor]
content_mode: how-to
track: developer-docs
last_updated: 2026-05-30
---

# Bildgenerierung

Der Skill `image-generate` verwandelt einen Text-Prompt in eine Bilddatei auf der Platte — vollständig über die Kommandozeile, sodass er sich in jede Pipeline einfügt. Er hat **austauschbare Provider-Backends** (gewählt über `--provider`), damit die Fähigkeit nicht an Preise oder Verfügbarkeit eines einzelnen Anbieters gebunden ist.

Die deterministische Engine ist ein reines Stdlib-Skript, `skills/image-generate/scripts/image_generate.py`; der Skill ist die betreiberseitige Hülle.

## Provider im Überblick

| `--provider` | Benötigte Credentials | Kostenlos? | Output-Lizenz | Wofür |
|---|---|---|---|---|
| `cloudflare` (**Default**) | `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID` | Ja, echtes Free-Tier (keine Karte) | FLUX.1-schnell, Apache-2.0; Output gehört dir | Blog- und Produktionsbilder |
| `pollinations` | keine (optional `POLLINATIONS_API_TOKEN`) | Ja, auth-frei | Keine explizite Lizenz (Verweis aufs Modell); öffentlicher Feed als Default | Schnelle Wegwerf-Bilder |
| `gemini` | `GEMINI_API_KEY` | Nein, **erfordert Billing** | Kommerzielle Nutzung erlaubt | Nur, wenn ohnehin bezahlt |

**Empfehlung:** Für alles, was du veröffentlichst, `cloudflare` nutzen. Es ist kostenlos, trägt kein Wasserzeichen und keinen öffentlichen Feed, und FLUX.1-schnell ist Apache-2.0 — die generierten Bilder gehören also klar dir. `pollinations` ist für Wegwerf-Bilder okay, gewährt aber keine explizite Output-Lizenz; `gemini` braucht ein bezahltes Projekt (das Free-Tier-Kontingent dieses Bildmodells ist null).

## Welchen Token braucht welcher Provider?

### Cloudflare (Default, empfohlen)

Cloudflare Workers AI betreibt FLUX.1-schnell auf einem echten, wiederkehrenden Free-Tier (10.000 Neuronen/Tag, keine Kreditkarte). Du brauchst einen **Token** und deine **Account-ID**:

1. Kostenlosen Account anlegen unter <https://dash.cloudflare.com/sign-up> (keine Karte nötig).
2. Im Dashboard zu **AI → Workers AI → "Use REST API"** gehen.
3. **"Create a Workers AI API Token"** klicken. Cloudflare füllt die richtigen Rechte vorab aus:
   - `Account` · `Workers AI` · **Read**
   - `Account` · `Workers AI` · **Edit** (dieses ist erforderlich, weil das Generieren eines Bildes eine `run`-/Edit-Aktion ist)
4. Token erstellen und kopieren (nur einmal angezeigt).
5. Die **Account-ID** von derselben Seite kopieren.

Dann beide exportieren (das Tool liest sie nur aus der Umgebung, nie als Flag):

```bash
export CLOUDFLARE_API_TOKEN="dein_token"
export CLOUDFLARE_ACCOUNT_ID="deine_account_id"
```

Das Free-Tier setzt täglich zurück; FLUX.1-schnell kostet ~4,8 Neuronen pro 512x512-Kachel, also sind 10.000 Neuronen/Tag grob hunderte Bilder.

### Pollinations (auth-frei)

Kein Token erforderlich. Optional `POLLINATIONS_API_TOKEN` setzen, um das Wasserzeichen anonymer Requests zu entfernen. Der erste Lauf zeigt einen einmaligen Disclaimer (öffentlicher Feed, keine explizite Output-Lizenz), den du bestätigen musst.

### Gemini (Billing erforderlich)

`GEMINI_API_KEY` von <https://aistudio.google.com/apikey> setzen. Beachte: `gemini-2.5-flash-image` ist **nicht** im Free-Tier (sein Free-Tier-Kontingent ist `0`); das Projekt muss Billing aktiviert haben, sonst gibt jeder Aufruf einen Billing-erforderlich-Fehler zurück.

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

Jeder Lauf schreibt das Bild plus ein `<image>.meta.json`-Sidecar mit `provider`, `model`, `source`, `prompt`, `timestamp` und `mime_type`.

Nützliche Flags: `--from-prompt-doc <doc> --variant light|dark` (ein `graphic-prompt-generator`-Dokument rendern), `-n <N>` (mehrere Bilder desselben Prompts), `--seed`, `--width`/`--height`, `--force` (existierende Datei überschreiben).

!!! tip
    Cloudflare und Pollinations liefern beide JPEG. Nutze ein `.jpg`-Ziel, um die Endungs-/MIME-Abweichungswarnung zu vermeiden (das Bild wird so oder so geschrieben).

## Nutzung in einem anderen Repo

Wenn das `nolte-shared`-Plugin in einem anderen Repository installiert ist, ist diese Fähigkeit dort als `/nolte-shared:image-generate` erreichbar — es wird nichts ins Consumer-Repo kopiert. Der Skill ruft das mitgelieferte Skript über `${CLAUDE_PLUGIN_ROOT}` auf, das in jedem Kontext auf das installierte Plugin-Verzeichnis zeigt (Marketplace-Installation und `claude --plugin-dir .`-Dogfooding), sodass derselbe Befehl überall funktioniert:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/image-generate/scripts/image_generate.py" \
    --prompt "a teal fox icon, flat" --out fox.jpg
```

Nur der *Skript*-Pfad ist plugin-relativ; Daten-Pfade (`--out`, `--from-prompt-doc`) bleiben relativ zum Arbeitsverzeichnis des Consumers. Die Abkürzung `task image:generate` ist `claude-shared`-lokal (sie führt das repo-relative Skript außerhalb von Claude aus); Consumer-Repos nutzen stattdessen den Slash-Command.

## Fügt sich in eine Pipeline

Das Tool schließt eine dreistufige Asset-Pipeline:

1. `graphic-prompt-generator` (Agent) verfasst ein brand-konformes Prompt-Dokument unter `design/prompts/`.
2. `image-generate` rendert es: `--from-prompt-doc design/prompts/hero.md --variant dark --out hero.jpg`.
3. `png-to-transparent-svg` (Agent) vektorisiert das Ergebnis für ein Icon oder Logo.

## Exit-Codes

`0` Erfolg · `1` Laufzeitfehler (Netzwerk, Filesystem, fehlerhafte Antwort) · `2` Usage-Fehler · `3` Rate-Limit / Kontingent / Billing-erforderlich · `4` Auth-Fehler. Bei `429` wird nichts automatisch wiederholt.
