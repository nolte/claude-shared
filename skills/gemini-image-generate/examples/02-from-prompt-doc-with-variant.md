# Example 02 — render a prompt document's Dark-Mode section over an existing file

Render the Dark-Mode prompt from a `graphic-prompt-generator` document to a path
that already exists. Exercises `--from-prompt-doc`, `--variant`, and the
overwrite-confirmation gate.

## Input prompt

> Render the dark-mode hero from `design/prompts/hero-landing.md` to
> `docs/assets/hero-dark.png` — it's already there, replace it.

## Input files

`design/prompts/hero-landing.md` contains `## Prompt — Light Mode` and
`## Prompt — Dark Mode` headings, each followed by a fenced prompt block.
`docs/assets/hero-dark.png` already exists. The acknowledgement file is present
and its digest matches the current notice.

## Expected behaviour

1. **Resolve.** Skill selects `--from-prompt-doc design/prompts/hero-landing.md
   --variant dark`; the script extracts the fenced block under the Dark-Mode
   heading.
2. **Overwrite gate.** `docs/assets/hero-dark.png` exists. The operator's "replace
   it" is an explicit confirmation, so the skill passes `--force`. (Without an
   explicit confirmation the skill would ask first and never pass `--force`.)
3. **No data-protection re-prompt.** The stored digest matches, so the notice is
   not shown again.
4. **Run.** `python3 …/gemini_image_generate.py --from-prompt-doc
   design/prompts/hero-landing.md --variant dark --out docs/assets/hero-dark.png
   --force`.
5. **Report.** Skill reports the overwritten image and its refreshed
   `docs/assets/hero-dark.png.meta.json` sidecar.
