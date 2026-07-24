# Blog-author outputs

Detailed on-disk layout and the field-level contract of the three delivery artefacts, referenced from `SKILL.md` §Outputs. Every run produces the post pair plus these three artefacts; the artefacts are written in English so `lektorat-apply` and any downstream skill can parse them.

## Layout (Astro consumer, reference `nolte/blog`)

```
<consumer-repo>/
├── src/content/posts/
│   ├── en/<slug>.md         # EN-canonical post
│   └── de/<slug>.md         # DE translation, same cross-language binding key
└── project/handovers/<slug>.md   # delivery contract: the three artefacts below
```

## Delivery artefacts (all three `MUST` when the skill writes them)

The spec calls the skill an "agentic author" and §Delivery contract promotes these to `MUST` for that case:

- **Self-check manifest** — one status line per acceptance-criterion ID from the two sibling specs (`a-1`…`a-17b` for `post-writing-style` — the range includes `a-4a`, `a-17a`, and `a-17b` — and `a-1`…`a-13` for `post-audience-communication`), with value `passed`, `finding: <reason>`, or `override: <reference>`. Per-language block (EN + DE) and per-pair block kept separate so build status, cross-language binding identity, and audience-field identity show as their own lines.
- **Source-to-claim mapping** — every entry of the briefing source list mapped to the concrete post passage it supports (heading anchor + sentence number). Multi-source citation is allowed; an unused source is a `finding`, not a violation. Every named-project / named-library / named-tool claim in the post points at ≥ 1 source.
- **Handover manifest** — three lines naming (a) the chosen handover route (target-state via `lektorat-apply` or transitional via `prose-vale-curator` + reviewer judgement), (b) the build status and the command used, (c) the repository state (branch name, optional commit SHA) the self-check ran against.

The skill writes all three under the consumer's handover-artefact path (reference: `project/handovers/<slug>.md`) as a single Markdown file with three top-level headings, one per artefact; the path is part of the merge commit so `lektorat-apply` and any reviewer can read them together with the post pair.
