---
title: gemini-image-handoff
audience: [maintainer]
content_mode: reference
track: developer-docs
last_updated: generated
---

# gemini-image-handoff

> Authors a Gemini-optimised prompt and guides the operator through pasting it into the Gemini web UI and downloading the image — a semi-automatic, no-API, no-billing handoff.

_Runs a semi-automatic Gemini image-generation handoff. The automated half authors a Gemini-optimised prompt from a brief per `spec/design/gemini-image-generation/`; the manual half guides the operator to paste it into the Gemini web UI (the Gemini app or AI Studio) and download the image from the chat. No API call, no billing, no `GEMINI_API_KEY`, and the skill writes no image and no sidecar — the operator places the downloaded file. Invoke when the user wants a Gemini image without enabling API billing, asks for a \"Gemini prompt to paste into the UI\", wants the manual Gemini chat route, or makes an equivalent German-language request (\"Bild über die Gemini-UI generieren\", \"Prompt zum Einfügen in Gemini\"). Don't use to call the Gemini API and write a file (use image-generate --provider gemini), to author a brand-conformant prompt document (use graphic-prompt-generator), or for FLUX/Cloudflare generation (use image-generate). Resume is not applicable: the handoff is a single interactive turn._

- **Plugin:** `nolte-media`
- **Phase:** 4 Build (`build`)
- **Tags:** `design`
- **Source:** [skills/gemini-image-handoff/SKILL.md](https://github.com/nolte/claude-shared/blob/main/skills/gemini-image-handoff/SKILL.md)

## Use when

- you want a Gemini image but won't enable API billing
- you want an optimised Gemini prompt to paste into the Gemini app or AI Studio yourself
- you want the manual chat-download route rather than an automated API call

## Don't use when

- **You can use the Gemini API (billing enabled) and want the file written automatically with a sidecar** → [`image-generate`](image-generate.md)
- **You want a free, fully-automated generation with no UI step** → [`image-generate`](image-generate.md)
- **You want to author a brand-conformant prompt document** → [`graphic-prompt-generator`](../../agents/nolte-media/graphic-prompt-generator.md)

## See also

- [`image-generate`](image-generate.md)
- [`graphic-prompt-generator`](../../agents/nolte-media/graphic-prompt-generator.md)

---

## Gemini Image Handoff

A **semi-automatic** route to a Gemini image that needs no API billing. The skill does one half automatically — author a prompt that is optimised for Google's native Gemini image model — and hands the other half to the operator: paste the prompt into the Gemini web UI, generate, and download the image from the chat. It makes **no API call**, needs **no `GEMINI_API_KEY`**, and writes **no image and no sidecar**; the operator owns where the downloaded file lands.

It exists because the `gemini` provider of the [`image-generate`](image-generate.md) tool requires billing (`gemini-2.5-flash-image` reports a Free-Tier quota of `limit: 0`). This skill keeps Gemini reachable for occasional use through the free chat UI, while still applying the verified model baseline so the pasted prompt is actually optimised for Gemini.

### Why this is a skill, not an agent

- **Operator-invoked slash command.** Reached as `/nolte-media:gemini-image-handoff` with a brief; the operator drives it directly.
- **A human step sits between the two halves.** The operator must paste the prompt into the UI and download the result before anything else can happen. An agent's fire-and-forget contract can't wait on a manual UI action.
- **The deliverable flows back into the conversation.** The copy-paste prompt block and the UI steps land in the operator's context to act on immediately.
- Counter-dimension: prompt authoring on its own could be an agent ([`graphic-prompt-generator`](../../agents/nolte-media/graphic-prompt-generator.md) is exactly that). The load-bearing dimension here isn't prompt quality but the interactive, operator-in-the-loop handoff — so this is a skill, and it **delegates to [`graphic-prompt-generator`](../../agents/nolte-media/graphic-prompt-generator.md)** when a brand-conformant prompt document is wanted.

### German trigger phrases

- „generiere ein Bild über die Gemini-UI", „gib mir einen Prompt zum Einfügen in Gemini", „Gemini-Bild ohne Billing", „manueller Gemini-Weg, ich lade das Bild selbst runter"

### How it works — the two halves

#### 1. Author the Gemini prompt (automated)

Turn the brief into a prompt optimised for `gemini-2.5-flash-image`, following `spec/design/gemini-image-generation/`:

- Write it as **narrative, descriptive prose** (describe the scene; never a comma-separated tag list) and **state the asset's intent or purpose**.
- Front-load the subject, then action, location or context, composition, and style; be hyper-specific about material and texture; control the shot with photographic and lighting language.
- For **in-image text**, quote the exact words and name the font or style.
- Express any avoidance **positively** (`a clean, uncluttered background` over `no clutter`) — Gemini has **no** negative-prompt parameter.
- When the asset must be **brand-conformant** (uses the repo's brand tokens, will be published), don't hand-author it here: dispatch the **[`graphic-prompt-generator`](../../agents/nolte-media/graphic-prompt-generator.md)** agent with the target generator `gemini-2.5-flash-image`, then hand off the prompt block from the document it writes.

Present the result as a single fenced **copy-paste block** so the operator can grab it in one go.

#### 2. Hand off to the Gemini UI (manual)

Guide the operator through:

1. Open the Gemini web UI — the **Gemini app** (`gemini.google.com`) or **Google AI Studio** (`aistudio.google.com`); a free Google account is enough, no billing.
2. Paste the prompt block from step 1 and send it.
3. Iterate **in the chat** if needed — conversational, one change per turn (`keep everything the same, but make the lighting warmer`); this is Gemini's recommended refinement path.
4. **Download the image** from the chat (the download / save-image control on the generated image).
5. Place and rename the downloaded file wherever the operator needs it — the skill does not move or record it.

### Hard rules

- **Never** call the Gemini API, request a `GEMINI_API_KEY`, or run the [`image-generate`](image-generate.md) script for this flow; the whole point is the no-billing UI route.
- **Never** write the image or a `<image>.meta.json` sidecar — provenance and file placement are the operator's responsibility (this is the "Nur Download-Anleitung" contract).
- **Always** state the **SynthID watermark** caveat: every Gemini UI output carries an invisible SynthID watermark. For a watermark-free commercial or blog asset, steer the operator to `image-generate --provider cloudflare` (FLUX.1-schnell, Apache-2.0, no watermark) instead.
- **Always** author the prompt to the Gemini baseline — don't paste a FLUX or SDXL tag-list prompt into the Gemini UI; a prompt isn't model-portable.

### Gotchas

- **Don't reach for `image-generate --provider gemini` here.** That path makes a billed API call and writes a sidecar; this skill deliberately avoids both. They share the model but not the route.
- **Brand assets go through [`graphic-prompt-generator`](../../agents/nolte-media/graphic-prompt-generator.md) first.** It enforces the brand color contract and writes a durable prompt document; this skill then only handles the UI handoff for the prompt it produced.
- **The watermark is unavoidable in the UI.** There is no UI toggle to disable SynthID; if the asset can't carry a watermark, the route is wrong, not the prompt.
- **Aspect ratio / resolution are the UI's to control.** State the desired aspect ratio in the prompt; the chat UI doesn't expose the API's size parameters.
