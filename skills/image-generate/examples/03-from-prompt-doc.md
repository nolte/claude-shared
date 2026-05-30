# Example 3 — Render a graphic-prompt-generator document

The `graphic-prompt-generator` agent writes brand-conformant prompt documents under
`design/prompts/` with fenced `## Prompt — Light Mode` / `## Prompt — Dark Mode` blocks.
This tool can render a chosen section directly — closing the pipeline
*author prompt → generate image → vectorise*.

## Generate the Dark-Mode variant

```bash
python3 skills/image-generate/scripts/image_generate.py \
    --from-prompt-doc design/prompts/hero_dashboard.md \
    --variant dark \
    --out assets/hero-dark.png
```

`--from-prompt-doc` reads the document, `--variant dark` selects the Dark-Mode section,
and the fenced prompt block inside it is extracted verbatim and sent to the default
provider (Cloudflare).

## Without `--variant`

If you omit `--variant`, the **first** fenced prompt block in the document is used.

## Chain into vectorisation

For an icon/logo that should become a clean SVG, follow up with the
`png-to-transparent-svg` agent on the generated PNG.

## Notes

- `--variant` only applies together with `--from-prompt-doc`; using it elsewhere is a
  usage error.
- The extracted prompt text is recorded verbatim in the `.meta.json` sidecar.
