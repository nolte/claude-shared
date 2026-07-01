# Example 02 — brand-conformant asset → delegate to `graphic-prompt-generator`

When the asset must use the repo's brand tokens and will be published,
the skill does **not** hand-author the prompt. It dispatches
`graphic-prompt-generator` to write a durable, brand-conformant prompt
document, then handles only the UI handoff for the block that document
produces.

## Input prompt

> I need a Gemini prompt for a blog header that uses our brand colors,
> ready to publish. I'll paste it into Gemini myself.

## Expected behaviour

1. **Brand signal recognised.** The asset uses the repo's brand tokens
   and will be published, so the skill must not hand-author the prompt
   inline (that would bypass the brand color contract).
2. **Delegate to `graphic-prompt-generator`.** The skill dispatches the
   agent with the target generator `gemini-2.5-flash-image`. The agent
   writes a durable prompt document that enforces the brand color
   contract and is optimised for the Gemini model baseline.
3. **Hand off the produced block.** The skill takes the prompt block
   from the document `graphic-prompt-generator` wrote and presents it as
   the single fenced copy-paste block — it does not re-author or edit
   the brand prose.
4. **Manual half — same UI steps.** Open the Gemini app or AI Studio,
   paste, generate, iterate one change per turn, download, place the
   file. The SynthID watermark caveat is stated again — a publishable
   brand asset that can't carry a watermark should route to
   `image-generate --provider cloudflare` instead.
5. **No side effects.** Still no API call, no `GEMINI_API_KEY`, and no
   image or sidecar written by this skill; provenance lives in the
   `graphic-prompt-generator` document and the operator's placement.
