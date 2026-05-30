---
title: gemini-image-generate
audience: [maintainer]
content_mode: reference
track: developer-docs
last_updated: generated
---

# gemini-image-generate

> Erzeugt aus einem Text-Prompt ein Bild über das Gemini-Free-Tier-Modell und schreibt Bild plus Metadaten-Sidecar an einen gewählten Pfad.

_Generates an image from a text prompt via the Gemini Free-Tier model (`gemini-2.5-flash-image`), writing the image plus a `<image>.meta.json` metadata sidecar to an operator-chosen path. Wraps the bundled, stdlib-only `scripts/gemini_image_generate.py`, which hard-codes the Free-Tier model and endpoint so paid Imagen / Vertex AI models are unreachable. Invoke when the user asks to \"generate an image\", \"create a hero image or icon from a prompt\", \"render this prompt to a PNG\", \"turn a graphic-prompt-generator document into an image\", or equivalent German-language requests. Don't use for image editing, in-painting, or multi-turn refinement; for paid Imagen / Vertex models; or for batch pipelines (all out of scope per spec/tools/gemini-image-generation/). To author the prompt itself rather than render it, use graphic-prompt-generator. Supports resume is not applicable: a generation is a single terminal call._

- **Plugin:** `nolte-shared`
- **Phase:** 4 Build (`build`)
- **Tags:** `design`
- **Quelle:** [skills/gemini-image-generate/SKILL.md](https://github.com/nolte/claude-shared/blob/main/skills/gemini-image-generate/SKILL.md)

## Anwenden wenn

- you want to generate an image from a text prompt to a chosen file path
- you want to render a graphic-prompt-generator prompt document into an image
- you want a terminal-driven text-to-image call without a chat UI

## Nicht anwenden wenn

- **You want to author the prompt rather than render it** → [`graphic-prompt-generator`](../../agents/nolte-shared/graphic-prompt-generator.md)

## Siehe auch

- [`graphic-prompt-generator`](../../agents/nolte-shared/graphic-prompt-generator.md)
- [`png-to-transparent-svg`](../../agents/nolte-shared/png-to-transparent-svg.md)

---

## Gemini Image Generate

Implements `spec/tools/gemini-image-generation/` — a prompt in, an image file on disk out, no chat UI. The spec defines the Free-Tier constraints, the data-protection contract, the error contract, and the sidecar shape; this skill binds those rules to the on-disk procedure by driving the bundled `scripts/gemini_image_generate.py`.

### Why this is a skill, not an agent

- **Operator-invoked slash command.** The capability is reached as `/nolte-shared:gemini-image-generate` with a prompt and a target path; the operator drives it directly rather than a parent dispatching a fire-and-forget worker.
- **Mid-flow confirmation is part of the contract.** The first generation in an environment surfaces a data-protection notice the operator must acknowledge, and an existing target file must not be overwritten without explicit confirmation. Those are interactive gates an agent's structured-report shape can't carry.
- **The result flows back into the conversation.** The written image path(s) and sidecar path(s) land in the operator's working context so the next step (embedding, vectorising via [`png-to-transparent-svg`](../../agents/nolte-shared/png-to-transparent-svg.md)) can follow inline.
- Counter-dimension considered: the generation itself is a single deterministic script call (an agent-like executor), but the load-bearing dimensions are operator invocation and the acknowledgement / overwrite gates, so skill wins. The deterministic engine is isolated in the bundled script rather than in agent prose.

### German trigger phrases

This skill also triggers on equivalent German-language requests, including:

- „erzeuge ein Bild aus diesem Prompt"
- „generiere ein Hero-Bild / Icon"
- „rendere diesen Prompt als PNG"
- „mach aus dem graphic-prompt-generator-Dokument ein Bild"

### Inputs

- A **prompt**, supplied as inline text, a `--prompt-file`, or a `--from-prompt-doc` graphic-prompt-generator document (with `--variant light|dark` to select a section).
- A **target path** (`--out`), always explicit — the spec forbids a silent default to the working directory.
- `GEMINI_API_KEY` in the environment. A free key needs no billing setup (`https://aistudio.google.com/apikey`).

### Operations

#### 1. `run`

Generate one image (or `n` images) from the resolved prompt to the target path.

1. **Resolve prompt and path.** Determine the prompt source and the explicit `--out` path from the request. If no target path is given, ask the operator for one — never invent a default.
2. **Pre-flight the obvious failures in conversation.** If `GEMINI_API_KEY` is unset, surface the setup hint (name the variable, link the key page, note Free-Tier needs no billing) and stop. If the target file already exists, ask the operator to confirm overwrite before passing `--force`.
3. **Run the bundled engine.** Invoke the script with the resolved arguments:

   ```bash
   GEMINI_API_KEY=… python3 skills/gemini-image-generate/scripts/gemini_image_generate.py \
       --prompt "<prompt>" --out <path> [--from-prompt-doc <doc> --variant <light|dark>] [-n <N>] [--seed <S>] [--force]
   ```

   On the **first generation in an environment**, the script prints the data-protection notice and requires acknowledgement; relay the notice to the operator and only pass `--accept-data-policy` once they have explicitly acknowledged it (the script persists a SHA-256 digest of the notice so they are not re-prompted on the same machine until the notice text changes).
4. **Report the result.** On success, report each written image path and its `<image>.meta.json` sidecar. On a non-zero exit, relay the script's actionable message verbatim and the exit code (`3` = Free-Tier quota exhausted, `4` = auth failure, `1` = other runtime error, `2` = usage error) — never retry a `429` automatically, because each retry burns more Free-Tier quota.

### Hard rules

- **Never** edit the model ID or endpoint in the bundled script to reach a paid model (`imagen-*`) or a Vertex AI endpoint (`*-aiplatform.googleapis.com`); the Free-Tier allowlist is a spec MUST enforced in code.
- **Never** pass the API key on the command line or echo it into the conversation; it travels only through the `GEMINI_API_KEY` environment variable.
- **Never** pass `--accept-data-policy` on the operator's behalf before they have seen and acknowledged the data-protection notice.
- **Never** pass `--force` to overwrite an existing file without an explicit operator confirmation in the same turn.
- **Never** retry on an HTTP 429; surface the quota message and stop.
- When `spec/tools/gemini-image-generation/` disagrees with this skill, the spec wins; propose updating this skill rather than diverging.

### Gotchas

- **The data-protection acknowledgement is per machine and digest-versioned.** It lives at `$XDG_STATE_HOME/nolte-shared/gemini-image-generation/ack` (or `$HOME/.local/state/…`) and stores a SHA-256 digest of the exact notice text. A future spec revision that changes the notice re-prompts every operator automatically — don't treat a pre-existing ack file as permanent consent.
- **An extension / MIME mismatch is a warning, not a failure.** The image is still written (the Free-Tier quota was already spent); the operator can rename or rerun with a matching extension without re-paying.
- **`n>1` writes `<stem>-1`, `<stem>-2`, … with one sidecar each**, and the `prompt` field is identical across every sidecar by design.

### Examples

- Read `examples/01-inline-prompt-to-png.md` when generating a single image from an inline prompt for the first time in an environment (covers the data-protection acknowledgement).
- Read `examples/02-from-prompt-doc-with-variant.md` when rendering a [`graphic-prompt-generator`](../../agents/nolte-shared/graphic-prompt-generator.md) document's Dark-Mode section to a file that already exists (covers `--from-prompt-doc`, `--variant`, and the overwrite confirmation).
