---
name: dockerfile-audit
description: Audits a project's Dockerfiles against spec/project/dockerfile-best-practices/ and produces a severity-classified audit artifact. The default `audit` operation dispatches the read-only dockerfile-audit-scanner agent, then hard-fails on any missing mandatory OCI core label (source, title, description, version, revision, created) present in neither the Dockerfile nor CI injection, and on any of the four mandatory non-label pillars (non-root numeric USER, in-layer secrets, base not pinned by tag+digest, missing .dockerignore); advisory pillars are scored. The opt-in `apply` operation inserts or merges the OCI LABEL block into the final stage. Invoke when the user asks to "audit a Dockerfile," "check OCI image labels," "run a Dockerfile best-practices check," or equivalent German-language requests. Don't use for dependency CVEs (dependency-audit), license inventory (license-check), or Kubernetes runtime hardening. Supports resume per spec/claude/resumable-work/.
tags: [audit]
phase: quality
summary: "Audits a project's Dockerfiles against the best-practices spec (mandatory OCI labels + four hardening pillars), reports findings, and can apply the OCI LABEL block."
summary_de: "Auditiert die Dockerfiles eines Projekts gegen die Best-Practices-Spec (Pflicht-OCI-Labels + vier Härtungs-Säulen), meldet Findings und kann den OCI-LABEL-Block anwenden."
use_when:
  - "you want to audit a repo's Dockerfiles for OCI labels and build-time hardening"
  - "you want a pre-PR or pre-release Dockerfile best-practices gate"
  - "you want to insert or merge the mandatory OCI LABEL block into a Dockerfile"
dont_use_when:
  - situation: "You want a dependency CVE / vulnerability scan"
    alternative: dependency-audit
  - situation: "You want a license-compliance inventory"
    alternative: license-check
  - situation: "You want Kubernetes runtime hardening (SecurityContext, probes)"
    alternative: quality-gate
see_also:
  - dockerfile-audit-scanner
  - dependency-audit
resumable: true
---

# Dockerfile Audit

Audit every Dockerfile a project ships against the container-labelling and build-time hardening contract, and produce a single severity-classified audit artifact. The default `audit` operation reports and recommends; the opt-in `apply` operation writes a Dockerfile only after explicit confirmation.

Implements `spec/project/dockerfile-best-practices/` — the spec defines the mandatory OCI-label contract, the four mandatory non-label pillars, the advisory best practices with their hadolint rule IDs, and the CI-injection presence rule. This skill binds those rules to the on-disk procedure and owns policy, severity, the report, and the apply.

## German trigger phrases

This skill also triggers on equivalent German-language requests, including:

- "Dockerfile auditieren" / "Dockerfile-Best-Practices prüfen"
- "OCI-Labels prüfen" / "Container-Labels sicherstellen"
- "OCI-LABEL-Block einfügen"

## User-language policy

Detect the user's language from their message and respond in it. The audit artifact uses English section headings (so downstream tooling can parse it reliably); prose around the report is localised.

## Inputs

- **Repo root**: default is the current working directory.
- **Operation**: `audit` (default, read-only) or `apply` (opt-in, writes). Never run `apply` without the caller explicitly asking for it.
- **hadolint version pin**: per `spec/project/dockerfile-best-practices/` §Version and tool anchors, an audit MUST pin a specific hadolint version because its rule set drifts. Read the pinned version from a repo `.hadolint.yaml` / Taskfile target when present; otherwise record the version actually run. Note that hadolint's default `--failure-threshold` is `info`, so Info-level findings already fail a default run.

## Operations

### `audit` (default, read-only)

1. **Dispatch the read-only scan agent.** Dispatch `dockerfile-audit-scanner` (Agent) for the detection pass: it discovers every Dockerfile, evaluates the mandatory OCI labels against the final stage (crediting CI-side injection in `.github/workflows/`), checks the four mandatory pillars, runs hadolint, checks the GHCR index-annotation wiring (the `index-annotation-wiring` finding: `present` / `MISSING` / `n/a-not-ghcr-published`), and returns a structured per-Dockerfile findings inventory. Wait for its inventory before triaging.

2. **Apply the hard-fail policy.** Per `spec/project/dockerfile-best-practices/`, mark a Dockerfile **fail** when any of these is true; otherwise **pass** (advisory findings never flip a pass to fail):
   - Any of the six mandatory OCI core labels (`source`, `title`, `description`, `version`, `revision`, `created`) is present in **neither** the final stage **nor** CI injection. A label that is a static literal, `ARG`-wired, or CI-injected counts as present. Do **not** hard-fail a required label the scanner credited to CI (`docker/metadata-action` / `docker build --label`).
   - The final stage has **no** non-root numeric `USER` — either because no `USER` instruction exists at all (the check beyond hadolint `DL3002`) or because the effective user is root.
   - A secret is introduced into a layer (secret via `ARG`/`ENV`, or a credential file `COPY`ed in).
   - A `FROM` base image is not pinned by **tag + digest** (floats on `:latest`, an untagged image, or a tag with no digest).
   - No `.dockerignore` ships in the build context.
   - The image is **published to GHCR via `docker/build-push-action`** and its OCI labels are present, **but** the workflow does not wire index-level annotations (scanner finding `index-annotation-wiring: MISSING`). This dimension is scoped to a detected GHCR/index publication: a Dockerfile the scanner marked `n/a-not-ghcr-published` is governed by the label baseline alone and is **not** failed on it.

   **Severity decision (documented per `spec/project/dockerfile-best-practices/`).** The index-annotation dimension is a **hard fail** for a GHCR/index-published image, and this tier comes directly from the spec — it is not a unilateral promotion. §"OCI image labels" states the annotation rule with a **MUST** ("the OCI core values MUST be propagated as index-level annotations, not only as config `LABEL`s") because `build-push-action@v7`'s default provenance makes the push an OCI image index, and GHCR reads the package page from the index annotations, not the config labels — so a label-only index surfaces "No description provided". The spec frames the MUST as **additive** for the GHCR/index case (the config-`LABEL` contract is retained as the single-manifest / `docker inspect` baseline), which is exactly why the failure is **scoped** to a detected GHCR publication rather than applied to every Dockerfile. Treating it as a hard fail is what stops a clean label verdict from falsely implying GHCR will display the metadata; the "when spec disagrees, spec wins" rule holds, so if the spec later re-tiers this rule, this skill follows.

3. **Score the advisory pillars.** The SHOULD items (multi-stage, `COPY` over `ADD`, package hygiene, single-`RUN` update+install, no `apt-get upgrade`, cache-friendly ordering, `HEALTHCHECK`, `pipefail`, exec-form `CMD`, absolute `WORKDIR`, registry allow-list, and the SHOULD labels `licenses`/`url`/`documentation`/`base.name`/`base.digest`) are scored and surfaced by their hadolint rule ID (or as `custom` for the non-mechanizable ones), never promoted to a hard fail. Also surface a hard-coded `version`/`revision`/`created` literal as a **reproducibility smell** (advisory), not a failure.

4. **Render the report** (see Report shape). Sort per-Dockerfile, mandatory pillars before advisory, so the rendered report diffs cleanly across runs.

5. **Persist the audit artifact.** Write the full audit to the portfolio-wide `.audits/dockerfile-audit/` path (default `.audits/dockerfile-audit/dockerfiles-YYYY-MM-DD.md`). The artifact MUST record: date; trigger (pre-PR / pre-release / manifest-change); scope (which Dockerfiles were audited, which were skipped and why); the hadolint version run and whether CI label injection was credited; the per-Dockerfile pass/fail verdict with each hard-fail reason; and the Git revision audited. Link to the prior artifact so the progression stays traceable.

### `apply` (opt-in, writes)

Run only when the caller explicitly asks to apply fixes, and confirm before writing each file. `apply` makes the **safe, mechanical** fixes the audit found; it never guesses a value that belongs to build time.

- **Insert or merge the OCI `LABEL` block into the final stage.** Wire the per-build values through `ARG` rather than hard-coding them — `version`/`revision`/`created` are per-build and a committed literal is stale on the next build:

  ```dockerfile
  ARG VERSION
  ARG VCS_REF
  ARG BUILD_DATE
  LABEL org.opencontainers.image.source="https://github.com/<owner>/<repo>" \
        org.opencontainers.image.title="<image name>" \
        org.opencontainers.image.description="<one-line description>" \
        org.opencontainers.image.version="$VERSION" \
        org.opencontainers.image.revision="$VCS_REF" \
        org.opencontainers.image.created="$BUILD_DATE"
  ```

  Set `source`/`title`/`description` as literals where known; leave `version`/`revision`/`created` `ARG`-wired for build-time substitution. Insert the block into the **final** stage only.

- **Merge, don't duplicate.** When the final stage already has a partial or malformed `LABEL` block, merge the missing keys into it — **later key wins**, and preserve any custom (non-`org.opencontainers.image.*`) labels already present. Never blindly append a second `LABEL` block that duplicates keys.

- **Other safe mechanical fixes** the audit surfaced and that have an unambiguous rewrite: `apt`→`apt-get` (`DL3027`), adding `--no-install-recommends`, switching a plain-copy `ADD` to `COPY` (`DL3020`), a shell-form `CMD`/`ENTRYPOINT` to exec form (`DL3025`). Leave anything requiring a judgement call (choosing a base digest, restructuring `RUN` layers, choosing a UID) to the operator with a recommendation.

- **Out of scope for `apply`:** substituting the actual `version`/`revision`/`created` values (that is build time), creating a `.dockerignore`'s content policy (recommend it, list the minimum `.git`/`.env`/key-file entries, but let the operator confirm), and pinning a base digest (recommend the updater — Renovate `docker.pinDigests` / Docker Scout — rather than inventing a digest).

## Report shape

```text
# Dockerfile Audit

Scope: <repo root>, <n> Dockerfiles discovered (skipped: <list with reasons>)
Trigger: <pre-PR | pre-release | manifest-change>
hadolint: <version | not installed — static checks only>
CI label injection: <credited from <workflow file(s)> | none found>
Git revision: <sha>

## Verdict
<pass | fail> — Dockerfiles failing: <count>, advisory findings: <count>

## <path/to/Dockerfile>  (final stage: <name or index>) — <PASS | FAIL>
### Mandatory (hard-fail on any FAIL)
- OCI labels: source <ok/MISSING>, title <...>, description <...>, version <...>, revision <...>, created <...>
- USER (non-root numeric): <PASS | FAIL: no USER instruction | FAIL: USER root> [<file:line>]
- Secrets in layers: <PASS | FAIL: <what>> [<file:line>]
- Base pinned tag+digest: <PASS | FAIL: <FROM ref>> [<file:line>]
- .dockerignore present: <PASS | FAIL>
- GHCR index-annotation wiring: <PASS (present) | FAIL: labels present, but index-annotation wiring missing → GHCR will show no metadata | n/a (not GHCR-published)> [<workflow file:line>]
### Advisory (scored)
- <check> (<DL#### | custom>) — <note> [<file:line>]

## Health
- Dockerfiles audited: <list>
- Dockerfiles skipped (with reason): <list or none>
- hadolint version: <version | not installed>
- CI-injected labels credited: <list or none>
- GHCR index-annotation wiring: <per-Dockerfile: present | MISSING | n/a-not-ghcr-published>
```

## Gotchas

- **A `LABEL` in a non-final stage is a false positive.** In a multi-stage build only the final (publishing) stage's labels ship; a `LABEL` reachable only through `COPY --from=` is discarded from the output image. Always evaluate the mandatory labels against the final stage the scanner identified, never against an earlier build stage.
- **A required label absent from the Dockerfile is not automatically a failure.** When CI wires the labels (`docker/metadata-action` → `docker/build-push-action`, or `docker build --label`), the requirement is satisfied and the label legitimately lives outside the Dockerfile. Only hard-fail when the label is present in neither the Dockerfile nor CI. Report a CI-credited label as `pass` with a note.
- **hadolint `DL3002` does not catch a never-set `USER`.** `DL3002` flags only a *last* `USER` of root; an image that never sets `USER` runs as root and is a hard failure the audit must assert statically, independent of any `DL3002` finding.
- **hadolint's rule set drifts, so pin the version.** The `DL3005`/`DL3017`/`DL3031` rules were removed upstream; a floating hadolint gives non-reproducible audits. Record the version actually run in the artifact, and remember its default `--failure-threshold` is `info` (Info findings already fail a default run).
- **Three pillars have no hadolint rule.** No `apt-get upgrade`, single-`RUN` update+install, and secret-in-layer detection are prose/custom checks the scanner does statically — a clean hadolint run does **not** mean these passed. Read the scanner's `custom`-sourced findings, not just the `DL####` ones.
- **BuildKit provenance/SBOM attestations do not satisfy a label requirement.** A required label is satisfied by a label, not by an in-toto attestation; never credit provenance toward OCI-label presence.
- **A config `LABEL` does not feed the GHCR package page once the artifact is an image index.** GHCR reads a single-manifest image's `description`/`licenses` from the config labels, but reads an **image index's** package-page metadata from **index-level annotations**. `docker/build-push-action@v7` attaches a provenance attestation by default, so nearly every push — even single-platform — becomes an index, making the label-only route surface "No description provided". A clean OCI-label verdict therefore does **not** imply GHCR will display the metadata: for a GHCR-published image, also require the workflow to wire index annotations (`DOCKER_METADATA_ANNOTATIONS_LEVELS` including `index` on `docker/metadata-action`, and `annotations: ${{ steps.meta.outputs.annotations }}` passed to `docker/build-push-action`). The config-`LABEL` contract stays the single-manifest / `docker inspect` baseline; the annotation wiring is the additive index requirement.

## Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/dockerfile-audit/<run-id>.yml` after every successful user-approval gate and after each named phase boundary (detection, triage, apply). On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope (`schema_version`, `run_id`, `inputs`, `phase`, `decisions[]`, `status`, ...) and the fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

## Hard rules

- **Never** write to a Dockerfile in `audit` mode. `apply` runs only when the caller explicitly asks, and confirms before writing each file.
- **Never** hard-fail a required OCI label that the scanner demonstrably credited to CI injection; it is present, just outside the Dockerfile.
- **Never** evaluate the mandatory labels against a non-final build stage.
- **Never** hard-code a `version`, `revision`, or `created` literal on `apply`; wire them through `ARG` for build-time substitution.
- **Never** append a duplicate `LABEL` block on `apply`; merge the missing keys into the existing final-stage block (later key wins, custom labels preserved).
- **Never** promote an advisory (SHOULD) finding to a hard fail, and never demote a mandatory pillar to advisory, without a spec change.
- **Never** hard-fail the index-annotation dimension for a Dockerfile the scanner marked `index-annotation-wiring: n/a-not-ghcr-published`; the additive MUST is scoped to a detected GHCR/index publication, and the label baseline alone governs a local/single-manifest build.
- **Always** pin and record the hadolint version used; a floating version gives non-reproducible audits.
- **Always** persist the audit artifact under `.audits/dockerfile-audit/` with the per-Dockerfile verdict, hard-fail reasons, and Git revision.
- When `spec/project/dockerfile-best-practices/` and this skill disagree, the spec wins; this skill needs the update.

## Why this is a skill, not an agent

This skill follows the hybrid pattern: the read-only detection phase is delegated to the `dockerfile-audit-scanner` agent (context-window isolation, tool restriction), while policy, severity, the report, and the apply stay in the skill.

- **Orchestration role**: typical callers run this as one step inside a larger flow (pre-PR gate, release cut, periodic image review); the output flows back into the main conversation so the operator can triage.
- **Mid-flow interactivity**: the `apply` operation needs per-file user approval — inserting or merging the `LABEL` block, rewriting an `ADD`/`apt` line — so the interactivity favours the skill side.
- **Persistent artifact**: the deliverable is an on-disk audit artifact under `.audits/dockerfile-audit/`; skills own persistent state.
- **Counter-dimension**: the detection half (discover Dockerfiles, parse the final stage, run hadolint, check the pillars) is self-contained and verbose — exactly the context-window pressure that favours an agent. That pull is honoured, but only for the scan half, which is delegated to `dockerfile-audit-scanner`; the interactivity of the apply step and the persistent artifact keep the orchestrating surface a skill.
