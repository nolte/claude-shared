---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "638"
classification: "feature-request"
secondary-classes: [spec-change, docs]
route: "direct"
status: approved
created: "2026-09-19"
---

# Issue Orchestration — Pre-analysis

<!-- Run-scoped artifact: committed on the run's feature branch, then removed with a
     fix-forward `git rm` before the PR merges, per spec/project/issue-orchestration/
     §Pre-analysis artifact lifecycle. -->

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #638 — [feat] nolte-media: FLUX.2 [klein] 4B als Cloudflare-Modell anbieten
- **URL**: https://github.com/nolte/claude-shared/issues/638
- **Labels**: enhancement, needs-triage
- **Author / trust**: `nolte` (repository owner) → trusted-author set; no comments exist, so no foreign text to weigh.
- **Linked items**: none (`closedByPullRequestsReferences: []`; `gh pr list --search 638 --state all` empty)
- **Prior art checked**: `project/features/`, `project/roadmap.md`, `project/requirements/` — no FLUX/klein/Cloudflare entry (grep, 2026-09-19). Not self-resolved: `image_generate.py:180` still pins `flux-1-schnell` alone.

## Requirements gate

- No requirement artefact under `project/requirements/` covers #638 → `U_gate` undefined, below `τ_high`.
- **Operator override recorded 2026-09-19 (gate: requirements-override, answer: ok):** the issue is operator-authored, carries four testable acceptance criteria, an explicit non-goal (never `klein-9b`/`dev`), a scoped six-item proposal, and a Step-0 verification protocol that this run executed. The two residual unknowns the issue itself names (default model, reference-image scope) are surfaced under *Open questions* rather than interviewed. `requirements-elicit` is an interactive funnel interview and cannot run in this unattended session.

## Step 0 — verification (executed this run, 2026-09-19)

| Claim in the issue | Source read | Result |
|---|---|---|
| `@cf/black-forest-labs/flux-2-klein-4b` exists on Workers AI | model page + raw schema JSON (`cloudflare-docs/.../flux-2-klein-4b.json`) | **established** — ID confirmed; `partner: true`, terms link → bfl.ai ToS |
| klein-4b weights are Apache-2.0 | HF model card `black-forest-labs/FLUX.2-klein-4B` | **established** — "License: apache-2.0", "Open weights available for commercial use under the Apache 2.0 license" |
| Request is `multipart/form-data` | raw schema (`required: ["multipart"]`) + changelog 2026-01-15 (curl example with `--form`) | **established** |
| Parameters `prompt`, `width`, `height` (256–1920; defaults 1024×768), `seed`, `guidance`, `input_image_0..3` (< 512×512); `steps` fixed at 4 | changelog post | **established** (changelog only; the raw schema types the body as an opaque `object`) |
| Response is **raw image bytes** | raw schema output: `{"image": {"type": "string", "description": "Generated image as Base64 string."}}` | **refuted by the schema** — the schema declares a base64 `image` field, the same shape as schnell. Live REST behaviour **unestablished** (no `CLOUDFLARE_API_TOKEN` in this session). Implementation must accept both shapes and a unit test must cover both. |
| Free tier covers klein-4b (10k neurons/day, no card) | pricing page | **established** — "free allocation allows anyone to use a total of 10,000 Neurons per day at no charge", klein-4b priced in neurons (5.37 in / 26.05 out per 512² tile), no model-level exclusion listed |
| Cost: klein-4b vs schnell | pricing page, computed | schnell 57.6 neurons per 1024² image (≈174/day); klein-4b 104.2 (≈96/day, output tiles only) → klein-4b ≈ 1.8× the cost per image |
| `flux-1-schnell` deprecation | model page | **established** — no deprecation/sunset notice; params `prompt` (1–2048), `steps` (≤8, default 4), `seed`; base64 JSON `image` |
| `klein-9b` / `dev` are FLUX Non-Commercial | issue sources (BFL flux2#32, LICENSE-FLUX-DEV) | **carried forward unestablished** — not re-read this run; irrelevant to the change because neither model is added, but relevant to doc wording ("per model, not per provider") |

## Classification

- **Primary class**: feature-request
- **Secondary class(es)**: spec-change (`spec/tools/image-generation/` §cloudflare currently says **MUST** call FLUX.1-schnell; `spec/design/flux-image-generation/` scopes itself to FLUX.1), docs
- **Rationale**: adds a selectable model to an existing provider behind a new CLI surface; the licence-accuracy requirement forces spec and doc edits alongside the code.

## Scope

- **In scope**: `--model` selection for the `cloudflare` provider with `flux-1-schnell` (unchanged, default) and `flux-2-klein-4b`; hand-rolled stdlib multipart encoder; `width`/`height` pass-through for klein-4b; sidecar records the concrete `@cf/...` ID; unit tests; spec wording per model; SKILL.md, examples, `gemini-image-handoff` cross-reference, `docs/{en,de}/guides/image-generation.md`.
- **In scope (widened at the gate, operator decision 3 — "das werden wir viel nutzen")**: reference-image input for klein-4b via a repeatable `--ref-image <path>` flag (up to 4, sent as `input_image_0..3` multipart file parts; usage error on any other model); the sidecar records each reference image's basename and SHA-256 for provenance; the spec non-goal "image editing" is narrowed to in-painting and multi-turn refinement.
- **Out of scope**: switching to `klein-9b` or `dev` (issue non-goal); client-side dimension validation of reference images (the endpoint's `< 512×512` limit is documented, the server's error body is surfaced verbatim per the shared-layer rule); `nolte/kamerplanter` `scripts/kami/README.md` — separate repo, follow-up issue filed after the verify gate; FLUX.2 [flex]/[max].

## Route

- **Decision**: direct
- **Rationale**: one coherent outcome (klein-4b selectable with accurate licence claims), one PR strand, no roadmap item created or retargeted. Many files, but a single planning shape — "bounded is about planning shape, not effort".

## Design decision (confirmed at gate 2026-09-19)

- **Default stays `flux-1-schnell`** in this PR (operator decision 2: ok). Evidence: ≈1.8× cost per image (measured above), the live response shape of klein-4b is unobserved, and `spec/tools/image-generation/` §cloudflare pins schnell as a MUST. Flipping the default is a one-line follow-up once a live call has confirmed the response shape and the operator accepts the neuron budget.
- **Model selection** via a new `--model` flag (short names `flux-1-schnell` | `flux-2-klein-4b`, validated per provider; unknown → usage error). The sidecar `model` field carries the full `@cf/black-forest-labs/...` ID.
- **schnell path unchanged** (JSON body, `steps: 4`, seed). When `--width`/`--height` differ from 1024 on schnell, print a stderr warning that the model ignores them.
- **klein-4b path**: `multipart/form-data` (stdlib-only encoder, RFC 2046 boundary) with `prompt`, `width`, `height`, optional `seed` (+ i for `-n`); no `steps` field. Response: JSON with `result.image` base64 (per schema) **or** raw `image/*` bytes (per changelog/issue) — branch on the response `Content-Type`; MIME for the base64 path by magic-byte sniff (PNG/JPEG), default `image/png`.
- **Reference images (klein-4b only)**: `--ref-image PATH` repeatable ≤ 4 → multipart file parts `input_image_0..3` (filename = basename, content type from `EXT_TO_MIME`, fallback `application/octet-stream`); rejected with a usage error on schnell or any non-cloudflare provider; more than 4 → usage error; unreadable path → runtime error before any network call. Sidecar gains `reference_images: [{"name", "sha256"}]` only when used. No consent notice is added for cloudflare (Cloudflare's data-usage terms weren't re-read this run; the docs state plainly that the file is uploaded to Cloudflare).

## Work packages

### P1 — Spec: per-model licence wording and the klein-4b Cloudflare path

- **Problem statement**: `spec/tools/image-generation/{en,de}.md` §`cloudflare` states a MUST to call FLUX.1-schnell, and `spec/design/flux-image-generation/{en,de}.md` §Model selection / §Cloudflare Workers AI path describe only FLUX.1. Hypothesis: both specs need a klein-4b clause (Apache-2.0, multipart, `width`/`height` 256–1920, `steps` fixed 4, base64 `image` per schema, up to four `input_image_*` reference images < 512×512) and a licence split note (klein-4b Apache-2.0; klein-9b and dev FLUX Non-Commercial → MUST NOT be offered); the default MUST remain schnell; the non-goal "image editing" narrows to in-painting / multi-turn refinement in both specs; the sidecar contract gains the optional `reference_images` list.
- **Acceptance criteria**: EN canonical + DE translation updated in lockstep; §References carries the four primary sources read this run (model page, raw schema, changelog, HF card, pricing) with retrieval date 2026-09-19; no line claims Apache-2.0 for the provider as a whole; `task test` (validate_skills + spec checks) green.
- **Touched files**: `spec/tools/image-generation/en.md`, `de.md`; `spec/design/flux-image-generation/en.md`, `de.md`
- **Specialist**: `nolte-shared:spec` (skill — description names spec authoring, translation, drift check)
- **Depends on**: none (gate approval of the design decision)

### P2 — Code + unit tests: `--model`, multipart encoder, klein-4b provider path

- **Problem statement**: `CloudflareProvider` hard-codes one model and a JSON/base64 path. Hypothesis (refutable): the design decision above is implementable stdlib-only in `image_generate.py` without touching the shared CLI/sidecar contract beyond the new `--model` flag.
- **Acceptance criteria**: (a) `--provider cloudflare --model flux-2-klein-4b --width 1280 --height 720` sends a `multipart/form-data` body with `prompt`, `width=1280`, `height=720`, no `steps`, `Content-Type: multipart/form-data; boundary=…` header (asserted on the mocked `urlopen` request); (b) response handling covers JSON `result.image` base64 **and** raw `image/png` bytes; (c) sidecar `model` = `@cf/black-forest-labs/flux-2-klein-4b`; (d) `--model` omitted → schnell, every existing cloudflare test passes unchanged; (e) `--model` unknown → exit 2; (f) schnell with non-1024 width/height → stderr warning, JSON body unchanged; (g) `-n 2` with seed → seed, seed+1 in the two multipart bodies; (h) module docstring provider list names both models with their licence; (i) `--ref-image a.png --ref-image b.jpg` with klein-4b → multipart parts `input_image_0` (filename a.png, image/png) and `input_image_1` (image/jpeg) carrying the file bytes, sidecar `reference_images` lists both with SHA-256; (j) `--ref-image` with schnell or pollinations → exit 2, no network call; (k) five `--ref-image` → exit 2; (l) the token never appears in the multipart body (extend the leak test). `python3 -m pytest tests/test_image_generate.py -q` green.
- **Touched files**: `plugins/nolte-media/skills/image-generate/scripts/image_generate.py`, `tests/test_image_generate.py`
- **Specialist**: `nolte-engineering:fullstack-developer` (agent — "turns a sharply-scoped requirement into production-ready, runnable code … plus matching tests"). **Dispatch mode (operator decision 4)**: nolte-engineering is loaded now; subagents may not reach the worktree path → the brief asks for direct writes with a scratchpad fallback, and the orchestrator persists.
- **Depends on**: P1 (contract wording fixed first)

### P3 — Skill artefacts: SKILL.md, examples, gemini-image-handoff cross-reference

- **Problem statement**: `image-generate/SKILL.md` (frontmatter description, §Providers table, hard rule "FLUX.1-schnell is Apache-2.0", §Operations command line, §Gotchas), `examples/01-cloudflare-default.md`, `examples/02-pollinations-disclaimer.md:14`, `gemini-image-handoff/SKILL.md:75`, and `gemini-image-handoff/examples/03-watermark-caveat-reroute.md:22` state the Apache-2.0 property per provider or name schnell alone. Hypothesis: every claim can be reworded per model without exceeding the 1024-char description cap (current 959 chars).
- **Acceptance criteria**: `grep -rn "Apache" plugins/nolte-media` shows only per-model claims (schnell, klein-4b); the provider table lists both models with `--model`, `width`/`height` behaviour, and cost; `examples/01` shows the klein-4b non-square call and the resulting sidecar `model`; frontmatter description and `dont_use_when` exclude in-painting / multi-turn refinement but name reference-image conditioned generation on klein-4b; §Operations shows `--model` and `--ref-image`; `task test` green (description ≤ 1024).
- **Touched files**: `plugins/nolte-media/skills/image-generate/SKILL.md`, `examples/01-cloudflare-default.md`, `examples/02-pollinations-disclaimer.md`, `plugins/nolte-media/skills/gemini-image-handoff/SKILL.md`, `plugins/nolte-media/skills/gemini-image-handoff/examples/03-watermark-caveat-reroute.md`
- **Specialist**: `nolte-claude-dev:claude-plugin-developer` (agent — "drafts or refines a plugin artifact (skill or agent) … in strict conformance with every spec under spec/claude/"); loaded in this session; draft-and-return, orchestrator persists into the worktree.
- **Depends on**: P2 (flag name and behaviour final)

### P4 — User guide: `docs/{en,de}/guides/image-generation.md`

- **Problem statement**: the provider table (line 19), recommendation (23), Cloudflare setup (29), and cost line (46) name FLUX.1-schnell and its licence as the provider's property; `README.md:68` says "Cloudflare FLUX" (fine as is). Hypothesis: four-line edits per language plus a short "choosing the model" paragraph.
- **Acceptance criteria**: EN/DE parity; per-model licence wording; cost line covers both models; `task lint` (vale/markdownlint) green; `scripts/check_links.py --offline` green.
- **Touched files**: `docs/en/guides/image-generation.md`, `docs/de/guides/image-generation.md`
- **Specialist**: `nolte-shared:audience-doc-author` requires an audience artifact that this repo doesn't hold for the guides (none under `project/`) → **no matching specialised agent — generalist remediation** (orchestrator edits, mirroring P3's wording), unless the operator wants `audience-identify` dispatched first.
- **Depends on**: P3

### Follow-ups (externally visible — filed only after the verify gate is green)

- **F1** `nolte/kamerplanter`: issue for `scripts/kami/README.md` (model ID, `--model`, the "ignores width/height → ~1024² square" line now schnell-only, free-tier note).
- **F3** (optional) flip the cloudflare default to klein-4b once a live call confirms the response shape.

## Dependency ordering

P1 → P2 → P3 → P4 ; F1, F3 after verify.

## Risks

- **Response shape mismatch** (schema says base64, issue says raw bytes; unobserved live): mitigated by handling both and testing both; residual risk closes with the operator's live smoke test (acceptance criterion 1 of the issue).
- **Default-model regression**: mitigated by keeping schnell default; `test_default_provider_is_cloudflare` and `test_cloudflare_uses_flux_optimal_steps` stay unchanged as guards.
- **Licence misstatement surviving in a translation or example**: mitigated by the corpus grep in verify (`grep -rn -i "apache" plugins/ docs/ spec/tools spec/design README.md`).
- **Description cap**: 959/1024 chars; P3 must not push it over.
- **No security-sensitive path**: credentials remain env-only (existing guard `test_no_credentials_leak_into_sidecar_or_stderr`); the multipart body must never carry the token. `code-security-reviewer` not required; the verify step re-runs the leak test.

## Open questions

Answered by the operator 2026-09-19 (recorded in `.resume/issue-orchestrate/20260919T134336Z-k4b1.yml` `decisions:`):

1. Requirements override — **ok**.
2. Default model — **schnell stays default**.
3. Reference images — **in scope now** ("mach es gleich mit, das werden wir viel nutzen").
4. Dispatch mode — **nolte-engineering loaded in this session**; dispatch proceeds here.

Remaining: none blocking. Live response-shape check (base64 vs raw bytes) stays with the operator's smoke test after merge.

## Dispatch log

<!-- Appended during operation 5; one line per package once its specialist reports. -->

- **P1** — specialist `nolte-shared:spec` (skill, run inline by the orchestrator): `spec/tools/image-generation/{en,de}.md` and `spec/design/flux-image-generation/{en,de}.md` updated in lockstep (EN canonical first); hypothesis held. Vale forced the spelling "FLUX.2 Klein 4B" in prose (bare `klein` fails Vale.Spelling; code ids keep `flux-2-klein-4b`). Vale, markdownlint, section-ref check green; EN/DE heading, bullet, and checkbox counts equal. Committed on `feat/638-flux-2-klein-4b`.
- **P2** — specialist `nolte-engineering:fullstack-developer` (agent, wrote directly into the worktree): `image_generate.py` (+211) and `tests/test_image_generate.py` (+169); hypothesis **confirmed** (stdlib-only, only `secrets` added). Contract additions: `EXIT_USAGE = 2` constant; `Provider.__init__(model=None)`; `CloudflareProvider.MODELS`. Result re-verified by the orchestrator: `51 passed`. Mutation probes by the specialist: every rule-breaking mutation failed exactly its test. Refutation note: none. Doc finding handed to P3: `examples/02-pollinations-disclaimer.md:14` attributes Apache-2.0 to the provider. Incident: an orchestrator `pre-commit` stash briefly reset the specialist's unstaged test file mid-run; the specialist re-applied it. Lesson recorded in gotchas candidate list: never run stash-based hooks in a worktree a specialist is writing to.
- **P4** — no matching specialised agent — generalist remediation (`audience-doc-author` needs an audience artefact the guides don't have): `docs/{en,de}/guides/image-generation.md` gained the per-model provider row, a "Choosing the Cloudflare model" section with the cost table and a Klein 4B example, and the updated cost line. Vale (EN) and markdownlint green; EN/DE heading counts equal (13/13). Run in parallel with P3 on disjoint files; wording follows the spec, not P3's draft. Committed.
- **P3** — specialist `nolte-claude-dev:claude-plugin-developer` (agent, wrote directly into the worktree): `image-generate/SKILL.md` (description 981 chars incl. quotes, under the 1024 cap; `summary_de` trimmed to 197 to stay under the 200 catalog limit), `examples/01`, `examples/02`, `gemini-image-handoff/SKILL.md:75`, `gemini-image-handoff/examples/03`. Deviations reported: description trimmed below the headroom threshold; a German trigger phrase added for the new use case. `validate_skills.py` clean for the touched files; all pre-commit hooks green. Committed.

## Verify (operation 6, run in the worktree 2026-09-19)

| Gate | Result |
|---|---|
| `git diff --stat origin/develop...HEAD` | non-empty: 13 files, +621/−61 (captured before any review verdict) |
| `python3 scripts/validate_skills.py` | exit 0; only pre-existing Info/Warning (gemini-image-handoff description 1005 chars, feature-decompose body size) |
| `python3 scripts/validate_mission.py` | no findings |
| `python3 -m pytest tests -q` | 270 passed, 2 skipped |
| `scripts/docs/gen_catalog.py` + `scripts/check_links.py --offline` | 0 critical (the 152 criticals seen before catalog generation were the gitignored catalog pages) |
| Vale (EN specs, EN guide), markdownlint, check-section-refs | green per file |
| Corpus grep `apache` over plugins/, docs/, spec/tools, spec/design, README.md | every hit names FLUX.1-schnell or FLUX.2 Klein 4B; no provider-level claim remains |
| Corpus grep for the old "ignores width/height → always ~1024² square" claim | only schnell-scoped statements remain in this repo; `nolte/kamerplanter` `scripts/kami/README.md:29` still carries the provider-level form → F1 |
| Security-sensitive paths | none touched (credentials stay env-only; leak test extended to the multipart body and green); `code-security-reviewer` not required |
| Defect-class guard (`spec/project/defect-class-guards/`) | not applicable: classification `feature-request`, PR type `feat`, no defect closed; the licence-claim invariant is nevertheless guarded mechanically by the spec's grep acceptance criterion and by `test_no_paid_or_vertex_strings_in_executable`-style unit tests on the model registry |
