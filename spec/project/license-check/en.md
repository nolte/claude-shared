# License Check

Status: draft

## Context
**Readers:** portfolio engineers adopting this process in a repository, and the skill author implementing the check tool.

Every repository in the portfolio combines three streams of intellectual property: the project's own source code, the third-party dependencies it pulls in through manifests, and the tools that touch the build or the artifacts (including AI generators that emit code, images, or models). Each stream carries license obligations—attribution, notice propagation, source-disclosure triggers, patent grants—and a permissive-leaning portfolio can't silently absorb a copyleft or use-restricted obligation it never agreed to. Today license risk is handled only at the edges: `spec/project/dependency-audit/` runs an optional, allowlist-driven license pass over dependencies, `spec/project/project-structure/` mandates a root `LICENSE` file, and `spec/tools/image-generation/` warns about one generator's output licence. None of these owns the *process*: how a license is identified, what obligations its category triggers, which combinations are compatible with the project's own license, how AI-generated provenance enters the inventory, and how a finding turns into remediation or attribution. This spec defines that end-to-end process (`Inventory/Discovery → SBOM → SPDX identification → classification → policy gate → remediation → attribution/NOTICE → continuous CI check`), anchored throughout in SPDX, and it carries the portfolio's default allow/review/deny policy. It's the license-compliance *authority* that `dependency-audit`'s license pass implements for the dependency slice.

The factual claims in this spec (license categories and their obligations, the one-directional Apache-2.0/GPL compatibility, the GPL "conveying" trigger, AGPL §13 network copyleft, MPL-2.0 / EPL-2.0 file-level copyleft and patent clauses, the AI-provenance findings, the per-stack tooling) are grounded in a four-round research record persisted under `.audits/license-check/` (2026-05-30 plus three 2026-06-01 notes). Two interpretive caveats are load-bearing and reproduced where they apply: the FSF position that static and dynamic linking are equivalent lacks settled case law, and the popular term "license laundering" is interpretation, not the wording of the peer-reviewed sources.

## Goals
- Every license entering a repository—own code, dependency, or tool/AI-generated artifact—is identified by a canonical SPDX identifier (or an explicit `LicenseRef-`/`NOASSERTION` fallback) whose full text is resolvable on demand
- Each identified license is classified into a category whose obligations are written down once and applied the same way across the portfolio
- A default allow/review/deny policy, tuned for a permissive-leaning portfolio, gates every component, with deny reserved for obligations the portfolio genuinely can't absorb (strong and network copyleft in conveyed/networked components)
- The project's own license is treated as the compatibility anchor: every dependency or incorporated work is checked for compatibility against it, not in the abstract
- AI-generated artifacts carry machine-readable provenance, and AI-emitted code is gated against quasi-verbatim reproduction of copyleft sources so the inventory can't be silently polluted
- Findings turn into a bounded response (replace / document an exception / generate the required attribution), and required NOTICE/attribution output is produced rather than assumed
- The check runs continuously in CI and at release, sharing cadence and artifact conventions with `dependency-audit` rather than duplicating them

## Non-Goals
- Choosing one specific license scanner as mandatory: like `dependency-audit`, the process is tool-agnostic; this spec names a recommended default per stack but the repository may substitute an equivalent that emits SPDX identifiers
- Giving legal advice or substituting for counsel: this spec encodes an engineering process and a conservative default policy; a genuinely ambiguous or high-stakes case escalates to a human decision, never to an invented ruling
- Re-deciding the portfolio's own outbound license: that's a per-repository choice recorded in the `LICENSE` file per `spec/project/project-structure/`; this spec consumes it as the compatibility anchor
- Replacing `dependency-audit`'s CVE/vulnerability scanning: that spec owns supply-chain *vulnerability* risk; this spec owns *license* risk and provides the policy its license pass implements
- Defining the operational details of the implementing skill (tool invocation, output rendering): those live under `skills/` and may evolve without a spec change
- Resolving the IP status of AI training itself or fair-use questions: out of scope; only the *provenance and license hygiene of artifacts that land in the repository* is covered

## Requirements

### Scope—what's checked
- **MUST** check all three IP streams: (1) the repository's own source files, (2) every third-party dependency declared in a tracked manifest (reusing the manifest set defined in `spec/project/dependency-audit/` §Scope), and (3) tools and AI generators that contribute to the build output or emit committed artifacts (generated code, images, model weights)
- **MUST** cover transitive dependencies, not only direct ones; a copyleft obligation in a transitive package binds the same as a direct one
- **MUST** include every subroot in a monorepo that carries its own manifest, so findings attribute to the owning component
- **MUST** treat a committed AI-generated artifact (code, image, model weight, or other asset) as an in-scope item whose provenance and license status are recorded per §AI provenance
- **MUST** distinguish, in the inventory, components that are *conveyed* (shipped, linked, or offered over a network as part of the product) from tools that are merely *executed at arm's length* at build or development time, because the obligation triggers differ (see §Classification and obligations); when the use context can't be determined, record it as `unknown-use-context` and route the component to `review`

### The pipeline
- **MUST** run the license check as an ordered chain: `Inventory/Discovery → SBOM → SPDX identification → classification → policy gate → remediation → attribution/NOTICE → continuous CI check`; each stage consumes the previous stage's output
- **MUST** produce, or consume, a machine-readable SBOM as the inventory substrate rather than an ad-hoc list, so the inventory is reproducible and diffable between runs
- **MUST NOT** treat a green policy gate as terminal: required attribution/NOTICE output and (where obligations demand it) source-availability are part of the chain, not optional follow-ups

### SPDX anchoring
- **MUST** identify every license by a canonical SPDX short identifier; composite cases use SPDX license expressions (`OR` / `AND` / `WITH`), and a license with no SPDX match is recorded as `LicenseRef-<idstring>` (never silently dropped)
- **MUST** be able to resolve any identified SPDX identifier to its full license text on demand—for example via `https://spdx.org/licenses/<ID>.json` (`licenseText`), the `license-list-data` repository's `text/<ID>.txt`, or an equivalent offline mirror—so a reviewer can read the exact obligations behind any finding
- **MUST** pin the SPDX License List version used for a given check run and record it in the artifact, because the list grows over time and identifier resolution must be reproducible
- **SHOULD** fall back to the ScanCode LicenseDB (`scancode-licensedb.aboutcode.org/<key>`) for licenses not yet in the SPDX list, mapping to `spdx_license_key` where one exists and to `LicenseRef-scancode-<key>` otherwise
- **MUST** record an item whose license can't be determined as `NOASSERTION` and route it to the `review` tier, never to `allow`

### Classification and obligations
- **MUST** classify every identified license into one category, and apply that category's obligations uniformly:
  - **permissive** (for example MIT, BSD-2/3-Clause, ISC, Apache-2.0, 0BSD, Zlib, PSF-2.0): obligation is attribution—retain the copyright notice and license text; Apache-2.0 additionally requires propagating any `NOTICE` file contents
  - **weak (file-level) copyleft** (for example LGPL-2.1/3.0, MPL-2.0, EPL-2.0): source-disclosure obligation is bounded to the licensed files or library; MPL-2.0 copyleft attaches per file containing covered code (a new file with no covered code isn't a Modification, even inside a Larger Work); EPL-2.0 copyleft attaches only to Modified Works (linking/binding/subclassing alone isn't a Contribution); LGPL static linking is permitted but obliges shipping the application in a form that lets the user relink the library—it obliges **no** disclosure of the application's own source
  - **strong copyleft** (for example GPL-2.0, GPL-3.0): the combined work carries the GPL; the source-disclosure obligation triggers on *conveying* (distribution to another party), **not** on purely internal use, and **not** on mere network interaction without transfer of a copy
  - **network copyleft** (for example AGPL-3.0): adds AGPLv3 §13—a modified version offered to users over a network must offer those users the Corresponding Source; this closes the SaaS/ASP gap that the plain GPL leaves open
  - **source-available / restricted** (for example BUSL-1.1, SSPL-1.0, open-weight model licenses): not OSI-conforming; carries field-of-use, time, or behavioural restrictions
  - **public-domain / public-domain-equivalent** (for example CC0-1.0, Unlicense): no obligation beyond not misrepresenting authorship
- **MUST** record, for strong and network copyleft findings, whether the component is *conveyed/linked/networked* or *executed at arm's length*, because that distinction decides the policy tier (see §Default policy)
- **SHOULD** capture patent-grant and patent-retaliation clauses where the category carries them—Apache-2.0, GPL-3.0, MPL-2.0 (§2.1 grant, §5.2 retaliation termination), EPL-2.0 (§2(b) grant excluding hardware, §7 retaliation)—because a patent-retaliation termination can void the grant a downstream user relies on
- **MUST** treat the FSF position "static and dynamic linking both create a combined work under the GPL" as the conservative default assumption for the gate, while recording in the artifact that this is the FSF interpretation and **not** settled case law

### Compatibility against the project's own license
- **MUST** validate every conveyed dependency or incorporated work for compatibility against the repository's own outbound license (read from the root `LICENSE`), not against an abstract ideal
- **MUST** encode the one-directional compatibilities the research established, at least:
  - lax-permissive licenses are mutually compatible and usually absorbable into a copyleft combination, with the original BSD-4-Clause (advertising clause) as the incompatible exception
  - Apache-2.0 code may be combined into a GPLv3 (or later) work, but GPLv3 code may **not** be combined into an Apache-2.0-licensed work—the compatibility is one-directional
  - Apache-2.0 is **incompatible** with GPLv2 (patent-termination / indemnification clauses), but compatible with GPLv3
  - two different copyleft licenses are mutually incompatible absent an explicit compatibility clause (for example GPLv2 vs GPLv3)
- **MUST** route any combination it can't positively confirm as compatible to the `review` tier rather than guessing

### Default policy (permissive-leaning portfolio)
- **MUST** apply a three-tier default policy, overridable per repository only with an explicit, recorded rationale (mirroring `dependency-audit`'s allowlist-with-rationale discipline):
  - **allow** (passes automatically): the permissive and public-domain categories; the concrete default allowlist is anchored to SPDX identifiers and seeded from the CNCF allowed-third-party-license set (for example `0BSD, BSD-2-Clause, BSD-3-Clause, MIT, MIT-0, ISC, Apache-2.0, PSF-2.0, Python-2.0, PostgreSQL, Zlib, X11, Unlicense, CC0-1.0`)
  - **review** (manual decision required, gate is `blocked` not `pass`): weak/file-level copyleft; source-available/restricted licenses; open-weight model licenses; the BSD-4-Clause advertising-clause exception; any `LicenseRef-*` / `NOASSERTION`; any combination not positively confirmed compatible; strong/network copyleft in a component that's *executed at arm's length only* (build/dev tool, not conveyed)
  - **deny** (fails automatically): strong copyleft (GPL family) and network copyleft (AGPL) in any component that's *conveyed, linked, or offered over a network* as part of the product—justified because a permissive-leaning, partly SaaS portfolio can't absorb the combined-work or §13 source-disclosure obligation
- **MUST** allow a deny-tier override only with a named, time-bounded, rationale-bearing exception (same envelope as §Remediation), never as a silent allowlist edit
- **MUST** treat this portfolio-default policy as the "explicit policy with named disallowed licenses" that `spec/project/dependency-audit/` §License audit requires before a license finding may hard-fail: a repository that has adopted `license-check` needs no additional per-repository deny declaration for the deny tier to bind
- **MUST NOT** downgrade a license's category on local judgement alone; disagreement is a recorded exception with rationale, not a reclassification

### Own-code and in-repo compliance
- **MUST** confirm the repository declares its own outbound license via a root `LICENSE` file (deferring the file's existence requirement to `spec/project/project-structure/`) and that the declared SPDX identifier is valid
- **SHOULD** carry per-file licensing information for the project's own source in the FSFE REUSE style, with `SPDX-FileCopyrightText` + `SPDX-License-Identifier` headers (or `.license` sidecars / `REUSE.toml`), and a `LICENSES/<SPDX-ID>.txt` file per license in use, so in-repo license resolution is deterministic
- **MUST** produce the attribution/NOTICE output that the dependency licenses oblige—generated directly or via a delegated attribution tool named by the implementing skill (for example an aggregated third-party notices file)—rather than assuming attribution is satisfied; for Apache-2.0 dependencies this includes propagating `NOTICE` contents

### AI provenance
- **MUST** record machine-readable provenance for every committed AI-generated artifact—at minimum the fact that it's AI-generated, and where known the generator/model and tier—using an available standard carrier (CycloneDX ML-BOM component type `machine-learning-model` + `modelCard`, or the SPDX 3.0.1 AI Profile `AIPackage` properties); for a plain AI-generated *file* with no dedicated "AI-generated" flag in the standard, a SPDX comment/annotation is the accepted fallback
- **MUST** treat AI-emitted code as a copyleft-contamination risk and gate it: it's empirically established that even top-performing code LLMs reproduce open-source code with "striking similarity" in roughly 0.88–2.01 % of generated snippets and usually emit no license information for copyleft snippets; the process **MUST** include a duplicate-/similarity-detection step against copyleft sources for AI-emitted code before it's treated as own code
- **MUST** classify open-weight model licenses (for example OpenRAIL / RAIL-M, the Llama Community License, the custom Gemma Terms of Use) as `review`-tier source-available/restricted licenses, **not** as OSI open source, because they carry use-restrictions and fail the Open Source AI Definition's "for any purpose" freedoms—and **MUST** pin the artifact version, since an open-weight model can change license between versions (for example Gemma's custom terms for v1–v3 versus Apache-2.0 for v4)
- **MUST NOT** assume a commercial generator's terms grant a clean, copyrightable artifact: terms vary (some assign output ownership without warranting copyrightability; IP indemnities are frequently tier-gated to paid plans), and purely AI-generated output may not be copyrightable at all under U.S. law (a finding scoped to U.S. jurisdiction; other jurisdictions differ)—capture the governing terms and tier in the artifact rather than presuming
- **SHOULD** label the "license laundering" framing as interpretation when it's used in documentation; the underlying compliance risk (unattributed copyleft-similar code) is evidenced, the label isn't the wording of the primary sources

### Per-stack tooling
- **MUST** stay tool-agnostic at the spec level: any tool is acceptable that identifies licenses by SPDX identifier and feeds the pipeline; the repository records which tool and version it used in the artifact (reproducibility, as in `dependency-audit`)
- **SHOULD** prefer these defaults per stack, each of which emits or maps to SPDX:
  - **Python**: rely on PEP 639 `License-Expression` / `License-File` core metadata where present; `pip-audit` doubles as a CycloneDX SBOM generator for the discovery+SBOM stages
  - **Node**: `license-checker-rseidelsohn` (the maintained successor to the abandoned `license-checker`), which validates `package.json` metadata against the `spdx` module and exposes ready CI-gate primitives (`--failOn`, `--onlyAllow`)
  - **Go**: `go-licenses` (Google), built on the Google License Classifier, which names licenses with SPDX identifiers and carries a 0.0–1.0 confidence score
  - **cross-stack**: CycloneDX native per-ecosystem generators for the SBOM; a classifier (Syft, ScanCode, ORT) for license text matching
- **MUST** confirm, per stack, that the chosen tool chain can produce the attribution/NOTICE output §Own-code and in-repo compliance requires: the named defaults cover discovery, SBOM, and classification, but their attribution-generation capability—and `go-licenses`' vendoring / missing-LICENSE limits—is unverified (see Open Questions); where a default can't generate attribution, the implementing skill names a dedicated attribution generator (for example the ORT NOTICE reporter)
- **MUST** configure scanners so that license text which fails to match a known SPDX identifier is surfaced for review, not silently marked "unlicensed" (a known Syft default pitfall before its `include-unknown-license-content` option)—an unmatched license is a `review` finding, never an `allow`
- **MUST NOT** adopt any "metadata-based SBOM generators are less accurate than build-based ones" heuristic as a tool-selection rule: that claim was investigated and refuted, and must not drive the spec's tool guidance

### Remediation and exceptions
- **MUST** apply one of three responses to every finding that isn't `allow`, inside a bounded window aligned with `dependency-audit`'s response discipline:
  - **replace**: swap the component for a compatibly-licensed alternative
  - **exception with rationale**: record a named, time-bounded (`valid-until`, ISO 8601) exception with a one-line rationale and the approver; permitted for `review` findings and, only with explicit sign-off, for a deny-tier override
  - **satisfy the obligation**: keep the component and produce what its license requires (attribution/NOTICE entry, source-availability offer, relink-capable form for LGPL)
- **MUST** revisit every exception on its `valid-until` date; renewal requires a fresh rationale
- **MUST NOT** silence a finding by editing the allowlist without a rationale, or by reclassifying the license

### Triggers, cadence, and CI
- **MUST** run as a continuous CI check on changes that touch a dependency manifest, a lockfile, the `LICENSE` file, or committed AI-generated artifacts
- **MUST** run a full check before every release tag, sharing the release-gate timing of `spec/project/dependency-audit/`
- **MUST** integrate with `dependency-audit` rather than duplicate it: when `dependency-audit`'s license pass runs on the dependency slice, it applies *this* spec's classification and policy; this spec additionally owns the own-code and AI-provenance slices and the policy authority
- **SHOULD** reuse the repository's Taskfile target convention so contributors reproduce the check locally

### Audit artifact
- **MUST** persist the result of every full check, defaulting to the portfolio-wide `.audits/license-check/` path convention, recording: date, trigger, scope (subroots/streams checked and skipped), the tools and versions used, the pinned SPDX License List version, the per-component SPDX identifier, category, policy tier, and response decision, plus the Git revision checked
- **SHOULD** link to the prior artifact so the progression is traceable

### Delimitation
- **MUST** remain the license-compliance authority while `dependency-audit` owns vulnerability/CVE risk; the two share cadence and artifact conventions but never merge their findings
- **MUST** consume the outbound license from `spec/project/project-structure/`'s `LICENSE` requirement rather than re-mandating the file
- **MUST** treat `spec/tools/image-generation/`'s output-licence disclaimer as one instance of the §AI provenance rule for AI-generated image assets, not as a competing policy
- **MUST NOT** rule on AI training legality, fair use, or the project's choice of outbound license

## Acceptance Criteria
- [ ] Every repository adopting this spec produces a traceable license-check artifact (default `.audits/license-check/`) naming the tools and versions, the pinned SPDX License List version, and the Git revision checked
- [ ] Every component in the most recent artifact carries a canonical SPDX identifier (or an explicit `LicenseRef-`/`NOASSERTION`), a category, a policy tier, and (where not `allow`) a response decision
- [ ] Any identified SPDX identifier in the artifact can be resolved to its full license text by a reviewer following the recorded resolution method
- [ ] No conveyed/networked component carries a strong- or network-copyleft license in the `allow` tier; any such component is either replaced or sits under a signed-off, time-bounded deny-tier exception
- [ ] Every dependency or incorporated work is recorded as compatible with the repository's own outbound license, or routed to `review` with the specific incompatibility named
- [ ] Every committed AI-generated artifact carries machine-readable provenance, and AI-emitted code has passed the copyleft similarity-detection step before being treated as own code
- [ ] Open-weight model licenses appear as `review`-tier (not `allow`), with the model artifact version pinned
- [ ] The required third-party attribution/NOTICE output exists and includes Apache-2.0 `NOTICE` propagation where applicable
- [ ] Every non-`allow` finding has a `replace`, `exception with rationale` (with `valid-until` and approver), or `satisfy the obligation` decision; no exception sits past its `valid-until` without a fresh rationale
- [ ] The check runs in CI on relevant changes and before release tags, and `dependency-audit`'s license pass defers classification and policy to this spec
- [ ] Every non-`allow` finding carries a response decision (or a documented exception with `valid-until` and approver) dated within the applicable response window, so the bounded-window obligation is verifiable
- [ ] Every strong- or network-copyleft component in the artifact records its conveyed/linked/networked versus arm's-length (or `unknown-use-context`) status, and that status matches its assigned policy tier
- [ ] The implementing process is exercised against fixtures for the four enumerated one-directional compatibility rules (for example a conveyed GPLv3 dependency in an Apache-2.0 product is never `allow`; an Apache-2.0 dependency in a GPLv3 project is), confirming the compatibility encoding rather than a blanket route-to-`review`

## Open Questions
- Cross-reference realignment: `spec/portfolio/tech-stack/` §Non-Goals currently states license-compliance is governed by `dependency-audit`, and `dependency-audit`'s §License audit predates this spec. Read both as descriptions of the pre-`license-check` state, not as prescriptive constraints that override this spec's authority claim; on adoption, `license-check` is authoritative. Once this spec stabilises, both references SHOULD be patched to name `license-check` as the policy authority (and `dependency-audit`'s license pass described as an implementer). No sibling-spec edit until this spec leaves `draft`.
- Midjourney and other image/asset generator terms, and the GitHub Copilot / OpenAI output-rights detail beyond what's already recorded, weren't fully verified in the research record; the AI-provenance requirements stay at the level the evidence supports. Sharpen the generator-specific terms table in a follow-up before any repo relies on a per-generator ruling.
- Apache-2.0 §3 and GPL-3.0 §11 patent-grant wording wasn't directly verified in the dedicated patent round (only MPL-2.0 and EPL-2.0 were); confirm the exact grant/retaliation wording before the patent-clause guidance is treated as quotable rather than categorical.
- Stack-crossing NOTICE/attribution generation (ORT NOTICE reporter, oss-attribution-generator) and the concrete limits of `go-licenses` (vendoring, missing LICENSE files, confidence threshold / false-positive rate) weren't verified; the §Per-stack tooling defaults name the tools but the attribution-generation mechanics need a verified pass before they harden from `SHOULD` to a named default.
- Revisit the deny-tier default if a `nolte/*` repository is ever intentionally licensed under copyleft, which would invert the compatibility anchor for that repository.
