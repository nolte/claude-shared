---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "655"
classification: "security"
secondary-classes: []
route: "direct"
status: approved
created: "2026-09-20"
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Issue**: #655 — `[security]` `image_generate.py` forwards provider credentials across a cross-host redirect
- **Author**: `nolte` (repository owner, trusted) · **Labels**: security, skills · **Comments**: one, this session's measurement correction
- **Linked items**: none. Filed from the security review of PR #656 (#643) and attributed there as pre-existing.
- **Prior art**: none under `project/`.

## Requirements gate

No requirement artefact. **Operator override** proposed: owner-authored, three acceptance criteria, four decisions named, and its central claim was re-measured below rather than inherited — which refuted part of it.

## Asserted cause: confirmed, and one detail of the issue refuted

**Confirmed.** `HTTPRedirectHandler.redirect_request`, read from the installed runtime (**Python 3.14.6**, not the 3.12 the issue body cites), builds the redirected request with `newheaders = {k: v for k, v in req.headers.items() if k.lower() not in ("content-length", "content-type")}` and no host comparison. The script sends credentials as headers: `Authorization: Bearer <token>` for Cloudflare (`:395`) and optionally Pollinations (`:505`), and `x-goog-api-key` for Gemini (`:577`). There is one `urlopen` call (`:217`) and it uses the default opener.

**Refuted: which status codes expose.** The issue says the credential goes to the attacker "on a 307/308 (or on the GET path)". Measured with two local `http.server` instances and a real redirect:

| Status | POST | GET |
|---|---|---|
| 301 / 302 / 303 | **followed, rewritten to GET, credential forwarded** | **followed, credential forwarded** |
| 307 / 308 | `HTTPError` raised, not followed | **followed, credential forwarded** |

So the POST exposure is on 301/302/303, the opposite of what the issue states, because the library refuses 307/308 on a POST. Recorded in a comment on #655.

**Consequences for the design:** `_post_json` and `_post_multipart` (Cloudflare, Gemini) are exposed on 301/302/303; `_get_bytes` (Pollinations) on all five. No status class is safe, so the remedy cannot be narrowed to one.

**A second measurement, about the tests.** `tests/test_image_generate.py` patches `urllib.request.urlopen` (one call site, used by every provider test). A patch at that level **replaces the opener entirely**, so no existing test could observe redirect behaviour, and a test written in the established style would pass against an unfixed script. The issue anticipated this; it is confirmed.

**Scope beyond this file.** `grep -rln "urlopen" scripts/ plugins/*/skills/*/scripts/` returns this file only, so the portfolio-wide check the issue asks for has exactly one subject today.

## Scope

- **In scope**: preventing a provider credential from reaching a host other than the one the request was addressed to, for all three providers and every redirect status; a test that exercises the opener rather than mocking `urlopen`.
- **Out of scope**: the two unbounded prompt-file reads (#657); any change to the provider registry, endpoints, or the CLI contract; proxy handling; certificate pinning.

## Route

**Direct.** One coherent outcome, one PR strand, no roadmap item.

## Decisions for the write gate

Confirmed by the operator 2026-09-20.

| # | Question | Proposal |
|---|---|---|
| D1 | Strip the credential on a cross-host redirect, or refuse redirects outright? | **Refuse.** All three endpoints are single documented URLs. A redirect is far likelier to be an incident than a feature, refusing is simpler to implement and to test, and the measurement shows the library already refuses 307/308 on the POST paths — so refusal generalises what the library does rather than inventing a policy. The cost is a provider that legitimately relocates an endpoint, which would then fail loudly instead of silently succeeding. |
| D2 | Where? | A module-level `OpenerDirector` built once, with a `HTTPRedirectHandler` subclass whose `redirect_request` returns `None`, so the library raises rather than following. `_request` uses `_OPENER.open(req)` instead of `urllib.request.urlopen(req)`. One call site changes. |
| D3 | What does the operator see? | A `GenerationError` naming the provider, the status, and the redirect target's host, with exit code 1. A redirect is neither a rate limit nor an auth failure, so it keeps the generic runtime code. |
| D4 | How is it tested? | The `http.server` probe from the #655 comment, promoted into the suite: two local servers, one redirecting to the other, asserting the second never receives the request and the credential never leaves. This is the first test in this file that does not mock `urlopen`; it must not weaken the existing ones. |
| D5 | Same shape elsewhere in the portfolio? | Measured: `urlopen` appears in no other script under `scripts/` or any plugin's `scripts/`. Recorded as checked, with nothing to do. |

## Work packages

### P1 — refuse cross-host redirects, with a test that exercises the opener

- **Problem statement** (hypothesis, refutable): a module-level opener with a refusing redirect handler replaces the one `urlopen` call without touching the CLI, the providers, or the error taxonomy. The likeliest refutation is D4: if a local `http.server` test proves flaky or slow in this suite, the test has to change shape — but a test that mocks `urlopen` would not test the fix at all, so the shape is load-bearing.
- **Acceptance criteria**: a cross-host redirect on 301, 302, 303, 307 and 308 reaches no second host and forwards no credential, for both a POST and a GET path; the error names the provider and the target host; every existing test passes unchanged (335 today); the new test fails if the handler is removed, verified by mutation and restored from a file copy.
- **Touched files**: `plugins/nolte-media/skills/image-generate/scripts/image_generate.py`, `tests/test_image_generate.py`
- **Specialist**: `nolte-engineering:fullstack-developer`
- **Depends on**: none

### P2 — the spec and the operator-facing text

- **Problem statement** (hypothesis, refutable): `spec/tools/image-generation/` §"Provider-agnostic (shared layer)" is where a credential-handling obligation belongs, beside the existing rule that credentials travel only in environment variables; the skill's §Gotchas is where an operator learns that a relocated endpoint now fails loudly.
- **Acceptance criteria**: the spec states the obligation in EN and DE with parity; the skill documents the behaviour; no spec restatement in the skill.
- **Touched files**: `spec/tools/image-generation/{en,de}.md`, `plugins/nolte-media/skills/image-generate/SKILL.md`
- **Specialist**: `nolte-shared:spec` for the spec, `nolte-claude-dev:claude-plugin-developer` for the skill
- **Depends on**: P1

## Dependency ordering

P1 → P2.

## Defect-class decision

Class: **a credential-bearing request follows a redirect to a host it was not addressed to.** G1 asks what it leaves behind.

- **Guard**: the portfolio-wide predicate is `grep -rln "urlopen"` over `scripts/` and every plugin's `scripts/`, which today returns one file. A guard that fires on a second file appearing is cheap and is a real class predicate, not a site check — but it would live in this repository while the property belongs to any repository that writes such a script.
- **Operator decision 2026-09-20**: the test is the guard for this file; the portfolio question is a note. Reason recorded: the predicate is real and cheap, but it would sit in this repository while the property belongs to every repository that writes a credential-bearing script, so a guard here would assert something about a corpus it cannot see. The note names the predicate so a later portfolio-wide sweep can run it.

## Risks

- **Behaviour change.** A provider that legitimately redirects would stop working, loudly. Today's three endpoints do not, but this is the trade-off D1 accepts and the PR must state it.
- **A real network test in a suite that has none.** Two loopback servers per test; if the suite runs where binding a port is refused, the test must skip with a stated reason rather than fail silently.

## Open questions for the operator

Both answered 2026-09-20: refuse redirects, and test-plus-note for the guard.

## Dispatch log

<!-- Appended during operation 5. -->
