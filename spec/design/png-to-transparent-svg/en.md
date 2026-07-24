# PNG to Transparent SVG

Status: draft

## Context

AI image generators (Gemini, DALL-E, Midjourney, and similar—this list is illustrative of the pattern, not an exhaustive or normative set) frequently emit PNGs where the checkerboard motif meant to signal "transparent" is actually painted into the RGB channels with `alpha=255` everywhere. Vectorisers like vtracer treat that motif as legitimate image content, so the resulting SVG carries a full-canvas checkerboard behind the motif. Until this spec lands, the `plugins/nolte-media/agents/png-to-transparent-svg.md` agent (heritage from earlier image-utility work) operationalises the cleanup-and-vectorise loop without an authorising spec—a `spec-drift-audit` finding (D-3 in the cross-cutting coverage matrix, since retired to git history). This spec closes the drift by formalising what the agent does, what it doesn't, and how a downstream consumer judges its output.

## Goals

- Provide an authoritative, version-controlled definition of the fake-transparency-cleanup-then-vectorise contract that the existing agent already implements
- Make the agent's behaviour reviewable: the `agent-review` skill can now check the agent against an explicit spec rather than against an implicit author intent
- Document the boundary between this utility and adjacent image work (vectorisation that doesn't need cleanup, photographic content) so the agent isn't invoked outside its safe envelope
- Keep the spec narrow: this is a small dedicated utility, not a general image-processing framework

## Non-Goals

- Replacing vtracer or any other vectoriser; the cleanup step is the value-add, the vectorisation is a thin wrapper
- Handling photographic PNGs where the background isn't a flat fake-transparency pattern (those would need raster-to-vector training, out of scope)
- Cleaning PNGs that already carry real alpha transparency (`alpha < 255` somewhere)—those go straight to the vectoriser without this agent
- Defining a portfolio-wide image-asset format spec; this is one utility, not a content-pipeline framework

## Requirements

- **MUST** detect the fake-transparency pattern from the alpha channel and the corner-pixel colour profile of each input PNG before any pixel rewrite—silent treatment of a real-alpha PNG as fake-transparency would corrupt legitimate transparency
- **MUST** rewrite the qualifying pixel set (those whose colour matches the detected fake-transparency colour) to `alpha=0` and emit an intermediate cleaned PNG; the cleaned PNG is the input to the vectoriser, never the original
- **MUST** vectorise the cleaned PNG with vtracer at parameters documented in the agent body; parameter changes live in the agent, not in this spec
- **MUST** treat detection thresholds (RGB delta, corner-cluster tolerance) as tuning values owned by the agent body, not configured at the spec level; callers steer via the per-file outlier report, not a threshold parameter
- **MUST** warn and skip a file in the report—rather than guess a threshold or block the batch on a question—when the detector can't classify it as either real-alpha or a clean fake-transparency pattern (mixed corner colours, partial alpha)
- **MUST** strip any full-canvas background path the vectoriser may still emit, so the resulting SVG carries no background fill
- **MUST** report a per-file summary (original size, pixels removed, SVG size, status) so the caller can spot anomalies (for example, a "0 % pixels removed" outlier indicates the detector failed and the file should be re-checked)
- **MUST NOT** modify a PNG that the detector classifies as already carrying real alpha transparency; route those directly to the vectoriser without cleanup, or refuse and report
- **MUST NOT** require network access; image processing runs locally via Python in `Bash`
- **SHOULD** accept single-file, directory, and glob inputs uniformly so callers don't have to script around the per-file loop
- **SHOULD** preserve the original PNG and write the cleaned PNG and the SVG as new files, so the input is never overwritten

## Acceptance Criteria

- [ ] An invocation against a sample PNG with baked-in checkerboard transparency produces a cleaned intermediate PNG (with `alpha=0` for the matching pixel set) plus an SVG with no background fill
- [ ] An invocation against a PNG that already carries real alpha transparency either skips the cleanup step (vectorising directly) or refuses with a clear message—and never silently rewrites alpha values
- [ ] The per-file summary contains pixel-removal counts that allow the caller to flag detector outliers (for example, a threshold below 5 % triggers caller review)
- [ ] An invocation against a PNG the detector can't classify (mixed corner colours, partial alpha) warns and skips that file in the per-file report rather than guessing a threshold or blocking the batch on a question
- [ ] The agent at `plugins/nolte-media/agents/png-to-transparent-svg.md` cites this spec in its `description` or body so the link is discoverable
- [ ] The agent's tools list is the minimum needed (`Read`, `Bash`, `Glob`)—no `Write` (image-file writes happen inside the Python helpers invoked through `Bash`), no `Edit`, no network tools

## Open Questions

_None at this time._
