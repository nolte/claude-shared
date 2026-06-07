# Link Validation

Status: draft

## Context
Documentation is only as trustworthy as its links. A portfolio repository ships MkDocs documentation that links three ways: internally, with relative markdown links between pages (`](../guide/install.md)`); across the repository tree, into roots the docs reference (`spec/`, `src/`, `scripts/`, …); and outward, to the open web (`https://…`). Every one of those links rots. A page is renamed and the relative link 404s at build-but-not-strict; a script is deleted and the doc still points at it; an upstream blog post moves, a vendor sunsets a product page, a GitHub permalink's branch is force-pushed away. The reader hits a dead end, and trust in the whole document set erodes.

The portfolio already owns part of this surface but not the deterministic, gating part. `spec/project/docs-freshness/` audits internal-link rot and cross-tree reference rot as one of eleven drift categories, but it does so through an LLM agent (`agents/docs-freshness-checker.md`) that runs quarterly and pre-release, is read-only by design, **can't run unattended in CI**, and explicitly declares external-link checking a Non-Goal. The CI workflow says so out loud: the internal-link slice is *"consciously deferred to the quarterly / pre-release agent run … Promote to a real paths-filtered job once a deterministic link-rot detector ships under `scripts/`."* That detector is what this spec defines.

This spec owns **link validity as a deterministic, machine-checkable practice**: a stdlib-only checker under `scripts/` that resolves internal and cross-tree links against the working tree and probes external URLs over HTTP, a thin gating layer that wires the offline (internal + cross-tree) slice into CI and the quality gate, and a read-only agent that runs the networked (external) slice as a periodic and pre-release audit. The goal is blunt: **no dead links in the documentation.** It complements `docs-freshness` (which keeps the non-deterministic drift categories—parity, ADR hygiene, stale markers, Mermaid drift) rather than replacing it, and it complements `prose-style`/`prose-vale-curator` (prose correctness) and `mkdocs build --strict` (rendering) by owning the one surface none of them gate: whether a link's target actually resolves.

## Goals
- Every repository with documentation can validate every internal, cross-tree, and external link with a single deterministic command, and that command is the source of truth for "is this link dead?"
- The offline slice (internal + cross-tree links) runs unattended as a blocking CI gate on documentation changes and inside the aggregate quality gate, so dead internal links never merge
- The online slice (external links) runs as a read-only, network-tolerant audit at documented cadences, classified so that flakiness (timeouts, transient 5xx, rate-limit responses) never masquerades as link rot
- Findings are classified by a shared severity scale and emitted in a deterministic, greppable shape so both humans and the wiring layer consume them the same way
- The checker defines not only what counts as **dead** but what counts as a **healthy, helpful link**, so authors get a positive target rather than only a failure signal
- The practice is clearly delimited from `docs-freshness`, `prose-style`, and the MkDocs build—each concern owns its own surface, with no duplicated gate and no silent coverage gap

## Non-Goals
- Re-implementing the non-link drift categories owned by `spec/project/docs-freshness/`: language parity, content-staleness deltas, Mermaid diagram-source drift, ADR index and status hygiene, stale markers, track/content-mode frontmatter. This spec owns the link-resolution slice only; `docs-freshness` keeps the rest and delegates the link slice here (see §Delimitation)
- Prose linting, vocabulary, or anchor-text *wording* quality: that's `spec/project/prose-style/` + `prose-vale-curator`. This spec checks whether the link *resolves* and whether its *shape* is healthy, not whether the surrounding sentence reads well
- Rendering validation: `mkdocs build --strict` is the authoritative check that the site builds; this checker runs against markdown sources, before and independently of rendering
- Fixing links: the checker and the agent are read-only. Repairing a dead link, choosing a replacement URL, or archiving a citation is a deliberate, separate authoring step (see §Read-only discipline)
- Link-shortener expansion, archival snapshotting (for example, automatically submitting to web.archive.org), or content-diffing a remote page to detect "the page still exists but the section moved"—these are valuable but out of scope for the first iteration; §Open Questions tracks the archival question
- Validating links inside source code, code comments, or non-documentation files. Scope is the documentation surface (see §Scope); a repository **MAY** extend scope, but the floor is docs

## Requirements

### Scope
- **MUST** include every markdown file under the MkDocs `docs_dir` configured in `mkdocs.yml`. When no `mkdocs.yml` exists, the scope falls back to every tracked `*.md` file in the repository except those under ignored roots (`.git/`, `node_modules/`, `.audits/`, vendored trees)
- **MUST** include the repository's top-level hand-maintained markdown (`README.md`, `CLAUDE.md`, and any other tracked root-level `*.md`) in the **internal and cross-tree** link checks, because those files link into `docs/`, `spec/`, and `scripts/` and rot the same way
- **MUST** extract and classify these link forms in every in-scope file:
  - inline links `[text](target)` and autolinks `<https://…>`
  - reference-style links `[text][id]` with their `[id]: target` definitions
  - bare URLs that markdown renderers autolink, when the repository's renderer is configured to autolink them
  - image sources `![alt](target)`: a broken image is a broken link
  - HTML `href`/`src` attributes embedded in markdown, when present
- **MUST NOT** treat fenced or inline **code spans** as link sources—a URL inside a code block is an example, not a live link
- **MAY** narrow a run to a single class (internal-only, external-only, cross-tree-only) on request; the narrowing **MUST** be recorded in any persisted artifact (§Audit artifact)

### Link classification
The checker **MUST** classify every extracted link into exactly one class, because the resolution method and the gating policy differ per class:

- **Internal link**: a relative path resolving to another in-repo documentation file (`./`, `../`, or repo-relative), optionally with an `#anchor` fragment. Resolved offline against the working tree.
- **Intra-page anchor**: a fragment-only link (`#section`) into the same file. Resolved offline against the file's own headings.
- **Cross-tree reference**: a relative or repo-relative link from a doc into a non-docs repo root (`spec/`, `src/`, `scripts/`, `docker/`, `helm/`, `tests/`, `tools/`, …). Resolved offline against the working tree.
- **External link**: an absolute `http://` or `https://` URL. Resolved online via an HTTP probe.
- **Non-HTTP scheme**: `mailto:`, `tel:`, `ftp:`, `irc:`, custom schemes. Not probed for liveness; checked only for well-formedness, and `mailto:`/`tel:` are validated against a syntactic pattern (§Healthy links).

### What counts as a dead link
- **Internal link / cross-tree reference**: dead when the target path doesn't exist in the working tree. Path resolution is case-sensitive and respects the OS path separator normalised to `/`.
- **Intra-page anchor and internal-link `#anchor`**: the **file** existing is a `MUST` check; the **anchor** resolving inside the target file is a `MUST` check resolved against the GitHub-Flavored-Markdown / `mkdocs-material` slugification algorithm (lowercase, spaces→`-`, strip punctuation, de-duplicate with numeric suffixes). Anchor resolution was a `SHOULD` while themes varied; with `spec/project/mkdocs-structure/` mandating `mkdocs-material` portfolio-wide, the slug algorithm is single and known, so anchor resolution is a `MUST` here. An explicitly authored `{#custom-anchor}` attribute **MUST** be honoured over the derived slug.
- **External link**: classified by the HTTP response to a request that prefers `HEAD` and falls back to `GET` when `HEAD` isn't allowed (`405`/`501`) or returns an ambiguous status:
  - **dead** (critical): final status `404`, `410`, or a DNS-resolution / connection-refused failure that reproduces across all retries
  - **dead** (critical): `400`, `401`, `403` **only** when they reproduce on the `GET` fallback and the host isn't on the known-soft-403 list (some hosts, for example certain CDNs and `linkedin.com`, return `403`/`999` to automated agents though the page is live for humans)—otherwise classified as **unverifiable** (info), never as a passing link
  - **rate-limited** (warning, never failing): `429`, or `403`/`999` from a known-bot-hostile host; the link is presumed live, the report records that it couldn't be confirmed
  - **transient** (warning, never failing): `5xx`, request timeout, or TLS error that reproduces across retries; presumed live, flagged for re-check, **MUST NOT** fail an offline-eligible gate
  - **redirect-stale** (warning): a permanent redirect (`301`/`308`) whose final target differs from the requested URL; the link works but **SHOULD** be updated to the canonical target. A temporary redirect (`302`/`303`/`307`) is **healthy**, not flagged
  - **healthy**: final status `2xx`
- **MUST NOT** classify a timeout, a transient `5xx`, or a rate-limit response as `dead`. Network flakiness is a `warning` at most; only a reproducing `404`/`410`/DNS-failure (or a reproducing hard `4xx` off the soft list) is link rot

### Healthy, helpful links
Beyond "not dead," the checker **MUST** evaluate link *quality* and emit `info`-severity findings (never failing a gate) when a live link is nonetheless poor. A healthy link:

- **Resolves**: the non-negotiable floor (above)
- **Prefers `https://` over `http://`** for external links where the host serves HTTPS; a bare `http://` to an HTTPS-capable host is an `info` finding
- **Points at a stable, canonical target**: prefer a release tag or commit-pinned permalink over a moving branch ref for source-host links (`github.com/...../blob/main/...` → flag in favour of a tag/commit permalink for citations meant to be durable); prefer the canonical target of a permanent redirect over the redirecting URL (the `redirect-stale` warning above)
- **Isn't a local or non-portable host**: `localhost`, `127.0.0.1`, `0.0.0.0`, private-range IPs, or `file://` URLs in shipped documentation are `warning` findings—they work for the author and nobody else
- **Carries meaningful anchor text**: a link whose visible text is a bare URL, `here`, `click here`, `this`, `link`, or `→` is an `info` finding (accessibility + helpfulness); this is the one quality check that touches anchor *text*, scoped narrowly to the click-target word so it doesn't overlap `prose-style`
- **Isn't a tracking-laden URL**: an external URL carrying `utm_*`, `fbclid`, `gclid`, or session-id query parameters is an `info` finding—strip to the canonical URL
- **Resolves its fragment**: an external link with an `#anchor` is checked for resolution only when the response is HTML and cheaply parseable; otherwise the fragment isn't validated (recorded as not-checked, not as a finding)

These quality findings are advisory: they sharpen what authors should aim for and **MUST NOT** fail a CI gate or the quality gate on their own.

### The deterministic checker (`scripts/`)
- **MUST** ship as a single stdlib-only Python script under `scripts/` (reference name `scripts/check_links.py`), with no third-party runtime dependency, consistent with the other validators in that directory (`validate_skills.py`, `readability_lix.py`)
- **MUST** expose these exit codes, matching the portfolio validator convention:
  - `0`: no finding at or above the configured failing severity floor (default: `critical`)
  - `1`: at least one finding at or above the failing floor
  - `2`: internal error (a file unreadable, `mkdocs.yml` unparseable, etc.); never confused with "links are dead"
- **MUST** emit one finding per line, prefixed with severity in Title Case (`Critical`, `Warning`, `Info`), so downstream tooling greps deterministically; each line **MUST** carry the source file, the source line number, the link target, the class, and a one-phrase reason
- **MUST** support a machine-readable output mode (`--format json`) emitting the full finding list plus a per-class, per-severity count summary, so the agent and any CI annotation step consume structured data rather than re-parsing prose
- **MUST** support `--offline`, which runs **only** the internal, intra-page-anchor, and cross-tree classes and never touches the network—this is the mode CI and the quality gate run
- **MUST** support narrowing flags (`--internal`, `--external`, `--cross-tree`) and a path/target argument so a caller can scope a run; absent scoping, it checks the full §Scope set
- **MUST** be deterministic in offline mode: the same working tree yields byte-identical output, so a `git diff --exit-code`-style gate is possible and CI failures are reproducible
- **MUST** read its configuration (ignore list, soft-403 hosts, timeout, retries, concurrency, failing-severity floor) from a single optional repo-root config file (reference name `.linkcheck.toml`, parsed with stdlib `tomllib`); absent the file, documented defaults apply
- **SHOULD**, when bundled inside a distributed Claude Code plugin/skill, be invoked via `${CLAUDE_PLUGIN_ROOT}` so it resolves in consumer repositories (per the bundled-script convention established for `image_generate.py`)

### External-probe discipline
- **MUST** apply a per-request timeout (default 10 s) and a bounded retry with backoff (default 2 retries) before classifying an external link as `transient`
- **MUST** bound concurrency and throttle per host (default: global concurrency 8, per-host no more than 2 concurrent and a small inter-request delay) to avoid self-inflicted rate-limiting and to be a good network citizen
- **MUST** send a descriptive, honest `User-Agent` identifying the checker; **MUST NOT** spoof a browser to defeat bot detection (a host that blocks bots yields `unverifiable`/`rate-limited`, not a forged success)
- **MUST** support an ignore/allowlist mechanism so known-flaky or auth-walled URLs are recorded once and excluded from failing classification: both a config-file glob list and an inline `<!-- linkcheck-ignore -->` / `<!-- linkcheck-ignore-next-line -->` marker in the markdown. Every ignore entry **SHOULD** carry a reason; the report lists what was ignored so the suppression is never silent
- **MAY** cache external results for a short, configurable TTL (default 24 h) under `.audits/link-validation/.cache/` so repeated runs in a release window don't re-probe every URL; the cache **MUST** be ignorable (`--no-cache`) and **MUST NOT** be committed
- **MUST NOT** follow more than a bounded redirect chain (default 5 hops); a longer chain is a `warning`

### Severity classification
- **MUST** adopt this scale, aligned with `docs-freshness` §Severity so a dead link is treated identically across the two audits:
  - **critical** (response window: before merge / before the next release): internal-link rot, intra-page or internal `#anchor` that doesn't resolve, cross-tree reference rot, external `404`/`410`/DNS-failure, reproducing hard `4xx` off the soft list
  - **warning** (response window: within the current quarter): external `transient` (5xx/timeout/TLS), `rate-limited`, `redirect-stale`, over-long redirect chain, `localhost`/private-host/`file://` link, `unverifiable` hard `4xx` on the soft list
  - **info** (best effort): `http://`-to-HTTPS-capable-host, non-canonical/branch-ref permalink for a durable citation, weak anchor text, tracking-parameter URL, unresolved external fragment
- **MUST NOT** downgrade a severity on local judgement alone; a disagreement is recorded as an explicit ignore-list entry with a reason, not a silent reclassification

### Triggers, cadence, and gating
- **Offline slice (internal + intra-page-anchor + cross-tree)**—deterministic, no network:
  - **MUST** run as a blocking CI gate (`--offline`) on every PR; a `critical` finding fails the build. The deterministic offline run is sub-second, so it runs unconditionally rather than paths-filtered—this isn't just simpler, it's more correct: a docs-only path filter would miss the most dangerous case, a PR that renames a file under a referenced root (`spec/`, `scripts/`, …) and so breaks a doc link without touching any `docs/` file. A repository **MAY** add a path filter when CI minutes are genuinely scarce, accepting that gap
  - **MUST** be reachable from the aggregate quality gate (`task check` / `task lint`) per `spec/project/quality-gate/`, so a local run catches dead internal links before push
  - **SHOULD** run on the full set (not just changed files) at least once per release, to catch rot introduced by a *move* in a file the PR didn't touch
- **Online slice (external)**—network-dependent, never the blocking PR gate by default:
  - **MUST** run before every release tag that includes documentation changes since the previous run, and **MUST** run at least once per calendar quarter
  - **MAY** run as a **non-blocking, scheduled** CI job (for example, a weekly `workflow_dispatch`/`schedule`) whose failure opens or updates a tracking issue rather than blocking a merge—chosen per repository (§Open Questions records the default)
  - **MUST NOT** be wired as a required, merge-blocking status check, because external flakiness would make the gate non-deterministic and erode trust in CI

### Read-only discipline
- The checker and the agent **MUST** be read-only: they report findings; repairing a link is a separate, opt-in authoring step
- **MUST NOT** modify, create, or delete any in-scope file—not even to "fix" an obvious typo in a link or to strip a tracking parameter
- The agent **MUST NOT** hit the network beyond the external HTTP probes the run requires, and **MUST NOT** submit any URL to a third-party archival or analytics service
- The only files the practice may write are its own cache (under `.audits/link-validation/.cache/`, uncommitted) and its audit artifact (below)

### Audit artifact
- **MUST** persist every full online (external) audit under the portfolio audit-trail convention `.audits/link-validation/<YYYY>-Q<n>.md` (or `<YYYY-MM-DD>.md` for an ad-hoc/pre-release run), matching the `.audits/<topic>/` pattern, and **MUST** live outside the MkDocs `docs_dir` so the audit never self-scans its own artifacts
- **MUST** record in the artifact: date, trigger (quarterly / pre-release / scheduled / manual), the repo root and `mkdocs.yml` path used, which classes were run (or narrowed out), the audited Git revision, the per-class/per-severity counts, the full finding list sorted by severity, and the full ignore list applied (target + reason)
- **MUST** cap per-class listings at 15 entries in the artifact and summarise the remainder with a count, so large rot clusters don't flood the report
- The offline CI slice **doesn't** persist an artifact (its output is the build log and the failing annotation); only the online audit produces a committed artifact
- **SHOULD** consult `spec/project/parallel-working-copies/` §Audit artefacts in multiple worktrees when the audit runs inside a worktree rather than the primary checkout

### Delimitation
- **MUST** stay the single owner of deterministic link resolution. `spec/project/docs-freshness/` **MUST** delegate its `Internal-link rot` and `Cross-tree reference rot` categories to this checker rather than re-detecting them: the `docs-freshness-checker` agent either invokes `scripts/check_links.py --offline` or cites this spec as the authority for those two categories, and keeps sole ownership of language parity, content-staleness, Mermaid drift, ADR index/status hygiene, stale markers, and track/content-mode frontmatter
- **MUST** stay separate from `spec/project/prose-style/` and `prose-vale-curator`: Vale owns prose and vocabulary; this checker owns link resolution and link shape. The one overlap point—weak anchor *text* (`here`, `click here`)—is owned here as a link-quality `info` finding scoped to the click-target word only, and **MUST NOT** be duplicated as a Vale rule
- **MUST** stay separate from `mkdocs build --strict`: the build is the rendering check; this checker resolves link targets against sources, independently of and before rendering
- **MUST NOT** be the place where the on-disk MkDocs shape, theme, or nav is declared—that's `spec/project/mkdocs-structure/`; this checker reads `mkdocs.yml` only to discover `docs_dir`

## Acceptance Criteria
- [ ] A single deterministic command (`scripts/check_links.py`) validates internal, intra-page-anchor, cross-tree, and external links across the documentation surface, with exit codes `0`/`1`/`2` and one severity-prefixed finding per line, plus a `--format json` mode
- [ ] `--offline` runs the internal + intra-page-anchor + cross-tree classes with zero network access and byte-identical output for an unchanged tree
- [ ] A CI job runs the offline slice on every PR and fails the build on any `critical` finding; the same offline run is reachable from `task check` (via `task check:links`) per `spec/project/quality-gate/`
- [ ] The external slice runs at the documented cadences (per release with doc changes; at least quarterly), is never wired as a required merge-blocking check, and classifies timeouts/transient-5xx/rate-limits as `warning` (never `critical`)
- [ ] No external link is reported `dead` on a single transient response; a `404`/`410`/DNS-failure is only `critical` after reproducing across the configured retries (and a hard `4xx` only off the soft-403 list)
- [ ] The ignore mechanism (config glob list + inline `<!-- linkcheck-ignore -->` markers) suppresses known-flaky/auth-walled URLs, every suppression carries a reason, and the report lists what was ignored—no silent suppression
- [ ] Link-quality findings (`http`-vs-`https`, non-canonical permalink, local host, weak anchor text, tracking params, unresolved fragment) are emitted at `info` and never fail a gate
- [ ] Every full external audit is persisted under `.audits/link-validation/` recording date, trigger, repo root, `mkdocs.yml` path, classes run, Git revision, per-class/severity counts, the sorted finding list, and the applied ignore list; per-class listings are capped at 15 with a remainder count
- [ ] `spec/project/docs-freshness/` references this spec as the owner of its `Internal-link rot` and `Cross-tree reference rot` categories, and the `docs-freshness-checker` agent no longer independently re-detects them; the agent `agents/link-rot-scanner.md` produces output mapping 1-to-1 onto the classes and severities declared here
- [ ] The checker and the agent are read-only in practice: no in-scope file is modified, created, or deleted by a run, and no URL is submitted to a third-party service

## Open Questions
- [ ] **Scheduled external CI job default.** Should the non-blocking external-link CI job be a portfolio-wide default (weekly `schedule` opening a tracking issue on new rot) or opt-in per repository? Provisional default: opt-in, with the quarterly + pre-release agent run as the floor; revisit once one repository has run the scheduled job for two quarters and we can measure issue-noise vs. caught-rot.
- [ ] **Archival of dead external citations.** When an external citation goes `404`/`410`, should the practice offer to look up a Wayback Machine snapshot and propose the archived URL as the replacement? Provisional default: out of scope for the first iteration (the audit reports the dead citation; replacement is a manual authoring decision); revisit if dead-citation findings become a recurring, high-volume artifact line.
- [ ] **Soft-403 host list location.** Should the known-bot-hostile host list (`linkedin.com`, certain CDNs) live in this repo's checker defaults, in the per-repo `.linkcheck.toml`, or be sourced from a shared upstream list? Provisional default: a small built-in default list in the checker plus per-repo extension via `.linkcheck.toml`; revisit if the list grows past a maintainable handful or diverges sharply per repository.
