# Compile step: canonical description → model-specific prompt

This is the **intermediate step** between a durable, model-agnostic *canonical
description* and the *compiled prompt* that is actually sent to one image generator.

```
  Canonical description  ──compile(model profile)──▶  Compiled prompt
  (long, complete,                                    (optimised for one
   model-agnostic —                                    generator's limits)
   reusable by any AI
   or a human)
```

## Why this exists

The full, detailed description is the **single source of truth** for the figure or
scene. It is written for *any* consumer — Midjourney, DALL·E / GPT-Image, Gemini,
FLUX-dev, or a human illustrator — so it must stay complete and never be trimmed to
fit one tool. Each generator, however, has hard limits (prompt length, no negative
prompts, no hex parsing). The **compile step** distils the canonical description into
a prompt that fits the *target* generator, without losing the canonical version.

So every prompt document keeps two layers:
- **`## Canonical description (model-agnostic)`** — the full description. Edit the
  figure here; this is what other AIs and humans read.
- **`## Compiled — <generator>`** — the derived, ready-to-send prompt(s). Regenerated
  from the canonical description whenever it changes, per the rules below.

The compile step is an **authoring task** (an LLM or a human applies the rules), not a
deterministic script — semantic compression needs judgement. Claude or the
`graphic-prompt-generator` agent can perform it.

## Model profiles

| Generator                         | Prompt style              | Budget        | Negative prompt | Hex codes | Style-reference mechanism |
| --------------------------------- | ------------------------- | ------------- | --------------- | --------- | ------------------------- |
| **cloudflare flux-1-schnell**     | natural-language prose    | **~256 tok**  | none (no CFG)   | ignored   | none (text only)          |
| **pollinations flux** (.1-dev)    | natural-language prose    | ~512 tok      | weak            | ignored   | none (text only)          |
| **gemini-2.5-flash-image**        | conversational NL         | long          | via instruction | partial   | a fixed reference image   |
| **midjourney v6/v7**              | compact NL + parameters   | moderate      | `--no` param    | ignored   | `--sref <code>`           |
| **openai gpt-image-1 / DALL·E 3** | rich NL (auto-rewritten)  | long          | via instruction | partial   | none                      |

## Compile rules (general)

1. **Extract the recognition anchors** from the canonical description — the 3–5
   features that MUST survive (here: blue-indigo fur, heart-shaped cream face mask,
   diagonal eye-stripes, no belly patch, three claws).
2. **Order by priority** (front-loaded): subject + dominant colour *with its
   anti-drift assertion* → anchors → style → background. The front of the prompt
   carries the most weight and survives truncation.
3. **Apply the profile's limits**: trim to the token budget, honour the negative /
   hex / style-ref columns.
4. **Verify**: render 2–4 seeds and compare against the canonical description, point
   by point. Discard drifted seeds.

## Compile rules — flux-1-schnell (the current generator)

- **Trim to ≤256 tokens (~1000 characters).** Anything past that is silently dropped
  (verified: a feature placed at ~token 470 never rendered, the same feature at the
  front did). Budget the prompt so nothing load-bearing sits in the tail.
- **Drop hex codes.** Diffusion models don't parse `#5B5FC7`; keep the descriptive
  name ("deep blue-indigo"). (Also per `corporate-design-colors` §AI image color
  contract: never rely on hex alone.) Hex stays in `brand-vocabulary.md` as docs only.
- **No negative prompt exists** (guidance-distilled, the API sends no `negative_prompt`).
  Convert "no X" into a positive assertion where it matters: "the body is solid indigo"
  beats "no belly patch"; "a plain dark-charcoal laptop" beats "no Apple logo".
- **Lead colour with an anti-drift assertion**: "deep blue-indigo, NOT brown" up front
  — "sloth" pulls FLUX toward natural brown fur.
- **Scene-first for scenes**: the action sentence ("a sloth typing at a laptop") must
  precede the character details, or FLUX renders the isolated mascot and drops the scene.
- **Prose, not labels**: the T5 text-encoder reads sentences; `CHARACTER:` / `POSE:`
  labels aren't needed (they don't hurt, but they cost tokens).
- `steps: 8` is fixed by the tool (Cloudflare's max for schnell); not a prompt concern.

## Worked compile (mascot front)

**Canonical** (excerpt): the full bullet list in `illustration_sloth-mascot.md`
§Character bible — every feature, both colour names and hex.

**Compiled — flux-1-schnell** (~187 tokens, hex-free, anchors first):

```
A chibi cartoon three-toed sloth sitting upright facing the viewer, symmetrical, with deep blue-indigo plush fur (a blue-violet indigo, definitely NOT brown). A big heart-shaped cream face mask with a small V-notch holds two large round dark-brown eyes; two broad dark diagonal stripes cross over the eyes like a mask, pale between them. Small dark nose, a gentle closed smile, two round coral-orange blush cheeks, a small jagged head tuft on top. The cream is only on the face — the whole body is solid indigo with no belly patch. Exactly three pale cream claws on each hand and foot. Bold even dark outline, smooth matte fills with soft cel-shading, flat warm bone-white background, soft oval shadow beneath. Modern flat kawaii vector cartoon style.
```

Every prompt document's `## Compiled — flux-1-schnell` block is produced this way.
