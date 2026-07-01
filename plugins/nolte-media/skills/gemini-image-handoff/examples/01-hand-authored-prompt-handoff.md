# Example 01 — hand-authored prompt → copy-paste block + UI steps

The core semi-automatic path for a one-off, non-brand asset. The skill
authors a Gemini-optimised prompt from the brief and hands the operator
the UI steps. No API call, no `GEMINI_API_KEY`, no file written.

## Input prompt

> Give me a Gemini prompt to paste into the app for a hero image of a
> sloth reading at a desk. I'll download it myself.

## Expected behaviour

1. **Automated half — author the prompt.** The skill turns the brief
   into **narrative descriptive prose** (not a comma-separated tag
   list) per the Gemini baseline: subject first (the sloth), then
   action (reading), location, composition, and style; hyper-specific
   about material and texture; photographic and lighting language to
   control the shot; the asset's intent stated. Any avoidance is
   expressed **positively** (`a clean, uncluttered desk` — Gemini has
   no negative-prompt parameter).
2. **Presented as one fenced copy-paste block** the operator can grab
   in a single selection.
3. **Manual half — UI steps.** The skill guides: open the **Gemini
   app** (`gemini.google.com`) or **AI Studio** (`aistudio.google.com`),
   a free Google account is enough; paste the block and send; iterate
   in the chat one change per turn if needed; use the download control
   on the generated image; place and rename the file wherever needed.
4. **SynthID caveat stated.** The skill notes every Gemini UI output
   carries an invisible SynthID watermark, and that a watermark-free
   asset should go through `image-generate --provider cloudflare`.
5. **No side effects.** No API call, no `GEMINI_API_KEY` requested, no
   image and no `.meta.json` sidecar written — the operator owns file
   placement and provenance.
