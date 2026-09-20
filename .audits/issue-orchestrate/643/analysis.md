---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "643"
classification: "security"
secondary-classes: [refactor]
route: "direct"
status: approved
created: "2026-09-20"
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Issue**: #643 — `[chore]` nolte-media: harden `image_generate.py` input and response bounds (deferred from #639 security review)
- **Author**: `nolte` (repository owner, trusted) · **Labels**: enhancement, skills · **Comments**: none
- **Linked items**: none (`closedByPullRequestsReferences` empty; no pull request references it)
- **Prior art**: none under `project/`. The issue was filed by this session on 2026-09-19 from the `code-security-reviewer` findings on PR #639, which were deliberately deferred so the feature PR stayed focused.

## Requirements gate

No requirement artefact under `project/requirements/`. **Operator override** proposed: the issue is owner-authored, carries four acceptance criteria, names its three findings with file anchors, and states its own out-of-scope boundary. Its claims were re-measured below rather than inherited.

## Asserted causes: all three verified against the current tree

`spec/project/issue-orchestration/` §"Issue acquisition and comprehension" (the rule added in `fdb9d53e`) requires the asserted cause to be measured before the first tracked change. The issue's anchors were written against `a06dbfcf`; `develop` has since moved to `68a4d8e0`, so each was re-read there.

| Finding | Asserted | Verified at `68a4d8e0` |
|---|---|---|
| H1 | `load_reference_images` reads unbounded, follows symlinks, falls back to `application/octet-stream` | **confirmed**, `image_generate.py:715-726`: `path.read_bytes()` with no size or type check, no `is_file()` guard, `EXT_TO_MIME.get(suffix, "application/octet-stream")` |
| H2 | `_request` calls `response.read()` with no `amt` | **confirmed**, `:133`: `return response.read(), response.headers.get_content_type()` |
| H3 | the upstream `error.message` and the response `Content-Type` reach the terminal verbatim | **confirmed**, `:104-112` interpolates `detail` from `_api_error_detail` into the operator message; `:636` writes the sniffed `mime` into the sidecar and `:617` warns with it |

Line anchors unchanged from the issue's text, so nothing drifted between filing and now.

## Classification

- **Primary: `security`.** The findings came from a `code-security-reviewer` run, and each change is a security control: an input bound, a type check, an output-size bound, and terminal-output sanitisation. None of them repairs an exploitable defect today — they are defence in depth — but classifying downward would skip the audit-then-verify chain operation 6 attaches to this class, and the surface handles credentials.
- **Secondary: `refactor`.** No user-visible capability is added.
- **Confirmed by the operator 2026-09-20** ("Passt"), per the skill's operation 2.

## Scope

- **In scope**: H1 (reject a non-regular file, cap the read, reject an extension outside `EXT_TO_MIME`), H2 (bound the response read), H3 (strip non-printable characters and cap the length of server-controlled strings before they reach stderr or the sidecar), each with tests that fail when the rule is removed.
- **Out of scope**: client-side dimension validation of reference images — `spec/tools/image-generation/` §`cloudflare` forbids it and requires the endpoint's error body to stay authoritative; any change to the provider registry, the CLI contract, or the sidecar's six base keys; the Klein 4B response-shape question, which waits for a live call.

## Route

**Direct.** One coherent outcome (the three bounds), one PR strand, no roadmap item.

## Proposed values, to confirm with the classification

Confirmed by the operator 2026-09-20 ("OK").

| # | Decision | Proposal |
|---|---|---|
| D1 | Reference-image size cap | 20 MiB. The endpoint's own limit is "under 512×512 pixels", which no byte count expresses exactly; 20 MiB is far above any conforming image and far below a memory hazard. Stated as a module constant so it is one edit to change. |
| D2 | Response-body cap | 64 MiB, generous for a single generated image at any size the providers offer. |
| D3 | Unknown extension | Reject as a usage error rather than uploading as `application/octet-stream`. The fallback exists to be permissive; here it silently uploads a non-image to a third party. |
| D4 | Sanitisation scope | The upstream `error.message`, the response `Content-Type`, and any provider string reaching stderr or the sidecar: strip C0/C1 control characters including ANSI escapes, cap at 500 characters with an explicit truncation marker. |
| D5 | Symlinks | Reject a path that is not a regular file after resolution (`path.is_file()` is true through a symlink to a regular file; the hazard is a symlink to a device or FIFO, which `is_file()` already excludes). No separate symlink rule. |

## Work packages

### P1 — the three bounds and their tests

- **Problem statement** (hypothesis, refutable): all three findings are local to `image_generate.py` and need no change to the CLI contract, the provider registry, or the sidecar's base keys. If bounding the response read turns out to require restructuring `_request`'s callers — the Pollinations path reads bytes directly, the JSON paths decode — that refines the package rather than refuting it.
- **Acceptance criteria**: (a) `--ref-image` on a directory, a device file, an oversize file, or an unknown extension exits 2 before `urlopen` is called; (b) a response body above the cap exits 1 with a readable message and writes no file; (c) an upstream message containing an ANSI escape reaches stderr without the escape bytes and the sidecar without them; (d) the caps are module constants; (e) every existing test passes unchanged (58 today); (f) each new rule has a test that fails when the rule is removed, verified by mutation and restored from a file copy, never `git stash`, per `spec/project/test-falsifiability/` §"Negative verification" §Mechanics.
- **Touched files**: `plugins/nolte-media/skills/image-generate/scripts/image_generate.py`, `tests/test_image_generate.py`
- **Specialist**: `nolte-engineering:fullstack-developer`
- **Depends on**: none

### P2 — the skill's operator-facing text

- **Problem statement** (hypothesis, refutable): `image-generate/SKILL.md` documents `--ref-image` without the new refusals, and its §Gotchas is where an operator learns them. The hypothesis is that this is a §Gotchas plus §Operations edit with no frontmatter change; the description is at 983 of 1024 characters, so it has little room.
- **Acceptance criteria**: the refusals and the caps appear where an operator meets them; `validate_skills.py` clean; no description growth beyond the cap.
- **Touched files**: `plugins/nolte-media/skills/image-generate/SKILL.md`, possibly `examples/01-cloudflare-default.md`
- **Specialist**: `nolte-claude-dev:claude-plugin-developer`
- **Depends on**: P1 (documents its exact messages)

## Dependency ordering

P1 → P2.

## Defect-class decision (`spec/project/defect-class-guards/`)

The PR type will be `chore` or `fix`, so a `## Class sweep` section may bind. The class is **"a server- or operator-supplied value reaches memory, the filesystem, or the terminal without a bound"**. G1 asks what it leaves behind:

- **Guard**: the tests are the guard for the three repaired sites, but they check sites, not the class (G3). A class-wide predicate would be a linter rule over this script: every `read()`/`read_bytes()` call carries a bound, every provider string reaching output passes the sanitiser. That is one script for one file, and this repository's only such script guards a corpus-wide property.
- **Operator decision 2026-09-20 ("Notizen reichen")**: state the class and the reason as a note in the issue and the pull request; no one-file linter. The reason recorded for a later reader: this repository's only class guard, `scripts/check_default_branch_claims.py` (#652), enforces a property of the whole corpus, where a predicate pays for itself. A linter whose subject set is a single file is a test in a costlier form, and the tests P1 adds already sit on those sites. Per G1 the written note is the deliverable where no proportionate guard exists.

## Risks

- **Caps are judgement, not measurement.** No conforming input was measured against 20 MiB or 64 MiB; they are bounds chosen to be far from both hazard and legitimate use. Recorded as unestablished by measurement, and stated as constants so a real observation can change them cheaply.
- **Sanitisation could hide diagnostics.** Stripping control characters from an upstream message must not drop the message; the spec's shared-layer rule requires the provider's actual error text to stay visible.
- **Security-sensitive path.** Operation 6 attaches the `code-security-reviewer` scope and a diff-scoped review to this class.

## Open questions for the operator

All three answered 2026-09-20: classification `security` confirmed, D1 to D5 confirmed, guard recorded as a note rather than built.

## Dispatch log

<!-- Appended during operation 5. -->

## Member results

- **P1** — `nolte-engineering:fullstack-developer`, commit `1bcf27ae`. Hypothesis held: all three `_request` call sites want the whole body, so one cap covers them. Constants `MAX_REF_IMAGE_BYTES`, `MAX_RESPONSE_BYTES`, `MAX_PROVIDER_TEXT_CHARS`. Negative verification over 8 rules from a file copy, each killing exactly its test; the `is_file` mutant made the FIFO test block for ever, which is the hazard itself. Orchestrator re-measurement: suite 314 → **330 passed, 2 skipped**; the transient third skip was this worktree's unsynced Vale styles, confirmed by running `vale sync` and re-running. Side effect worth noting: the test fake's `read()` gained the real `HTTPResponse` signature with a consuming cursor — it had been more permissive than production, the T9 shape this corpus named in `fdb9d53e`.
- **P2** — `nolte-claude-dev:claude-plugin-developer`, commit below. SKILL.md §Inputs, §Operations step 2, §Gotchas; the example's §Failure modes carries the verbatim strings. Description 973/1024, body ~3,086 tokens, `validate_skills.py` 0 Critical, markdownlint green. Orchestrator verification: a source grep for the quoted messages fails by construction, because each message is assembled across several f-string lines — so the three refusals were **triggered** instead and their stderr compared to the documentation. All three match verbatim.

## Security chain (operation 6, class `security`)

`nolte-engineering:code-security-reviewer` read the whole script, the hardening test block, the spec's shared-layer requirements and CPython's `urllib/request.py`. **Nothing in the diff blocks.** Verified as sound: one `urlopen` entry point so the cap covers all three call sites and the error body; a lying `Content-Length` cannot defeat the loop's own counter; the `limit: 0` billing signal is read from the full body before truncation; C1 stripping runs on decoded text and cannot mangle UTF-8; no new path exposes a credential.

Four findings, attributed by re-measurement rather than accepted as reported:

| Finding | Introduced by this PR? | Evidence |
|---|---|---|
| SEC-003 operator paths unsanitised on stderr | **yes** | all four interpolations appear as `+` lines in this diff |
| SEC-002 TOCTOU between `is_file()` and `open()` | **yes** | the sequence is new in `load_reference_images` |
| SEC-004 `_CONTROL_CHARS` misses bidi and isolate overrides | **yes** | the function is new; its class is `[\x00-\x1f\x7f-\x9f]` |
| SEC-001 credentials forwarded across a cross-host redirect | **no** | the diff contains no `urlopen`, redirect-handler or opener line; CPython's default handler copies every header but `content-length`/`content-type` |
- **P3** — `nolte-engineering:fullstack-developer`, the three findings this pull request introduced. SEC-003: one `_safe_text` of the operator path reused across all four refusals plus the two pre-existing message paths; no refusal wording changed, so `c41e6bae`'s documentation stays correct. SEC-002: `_open_ref_image` decides type and size from `os.fstat` on the open descriptor, one path resolution instead of two. SEC-004: direction overrides and isolates added to the control class, with U+200E/200F deliberately left out and the reason recorded.
  **Refutation, measured, and it changed the implementation:** the reviewer's proposed remediation for SEC-002 was `open()` then `fstat`. Measured with a SIGALRM probe on Linux: `open(fifo, "rb")` blocks, so that sequence hangs before `fstat` can run. `os.open(..., O_RDONLY|O_NONBLOCK)` returns at once and `fstat` reports `S_ISFIFO`. `O_NONBLOCK` is therefore load-bearing, and its removal is pinned by a test that fails by alarm.
  **A negative verification that failed on the first attempt, and was strengthened rather than accepted:** mutating the size check back to `path.stat()` first left the descriptor test green, because the "grew past the cap" message shares the strings `20 MiB`, `MAX_REF_IMAGE_BYTES` and exit 2 with the oversize message. The assertions were tightened until the mutation failed.
  Suite 330 → **335 passed, 2 skipped**; `pre-commit` clean.

## An edge reported by P3, measured by the orchestrator and deliberately not fixed

P3 reported that the reference image's basename reaches the sidecar's `reference_images[].name` and the multipart header without sanitisation. Measured rather than assumed:

- **Sidecar: not a hazard.** `json.dumps` encodes a control character as its `\uXXXX` escape, so no raw ESC reaches the file. Verified by encoding a name containing `\x1b[2J`: the output contains `\u001b` and no raw escape byte.
- **Multipart header: raw, and still not a hazard.** The byte does survive into the body, verified by calling `_encode_multipart` directly. That body travels to the provider and is never rendered in a terminal; the attack that matters there is header injection through a quote or CRLF, and `_encode_multipart` has escaped both since #639.

Recorded here, and in the pull request, so that a later reader does not mistake the deliberately partial sanitisation for an oversight. Per `spec/project/defect-class-guards/` G7, a fix must not leave the unrepaired part of its class looking intended without saying so.
