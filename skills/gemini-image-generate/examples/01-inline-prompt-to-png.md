# Example 01 — inline prompt to a PNG (first run: data-protection acknowledgement)

A single image from an inline prompt to a fresh path, on a machine where no
acknowledgement file exists yet. Exercises the data-protection gate and the
single-image happy path.

## Input prompt

> Generiere ein minimalistisches, flaches Icon eines petrolfarbenen Fuchses
> und speichere es unter `assets/fox.png`.

## Input files

None. `GEMINI_API_KEY` is set in the environment; no
`$XDG_STATE_HOME/nolte-shared/gemini-image-generation/ack` file exists.

## Expected behaviour

1. **Resolve.** Skill takes the prompt verbatim and the explicit `--out
   assets/fox.png`. No default path is invented.
2. **Pre-flight.** `assets/fox.png` does not exist, so no overwrite question;
   `GEMINI_API_KEY` is set, so no setup hint.
3. **Data-protection gate.** The bundled script prints the data-protection
   notice (Free-Tier inputs train the model). The skill relays it to the
   operator and waits. Only after the operator explicitly acknowledges does the
   skill pass `--accept-data-policy`; the script persists the SHA-256 digest so
   the next run on this machine is not re-prompted.
4. **Run.** `python3 skills/gemini-image-generate/scripts/gemini_image_generate.py
   --prompt "…" --out assets/fox.png --accept-data-policy`.
5. **Report.** Skill reports `assets/fox.png` and `assets/fox.png.meta.json`
   (the sidecar carries prompt, model `gemini-2.5-flash-image`, endpoint,
   timestamp, mime_type). The API key appears nowhere in output or sidecar.
