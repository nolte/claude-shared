# Dockerfile Best Practices

Status: draft
Portfolio-Scope: local

## Context

Portfolio repositories that build container images publish them to the GitHub Container Registry (GHCR). This spec governs *what* a `Dockerfile` must contain to be **correctly labelled**, **secure**, and **reproducible**, independent of *how* the image is built (a plain `docker build`, BuildKit, or a CI pipeline using `docker/build-push-action`). It's the third sibling of `spec/project/kubernetes-deployment-best-practices/` (which governs the runtime deployment) and `spec/project/bjw-s-common-chart-deployment/` (which governs Helm-chart generation): those two own the *runtime* posture, this one owns the *build artifact*.

The headline mandatory pillar is a **container-labelling contract**. GHCR uses the `org.opencontainers.image.source` label to link a published package to its source repository and to inherit that repository's access—a package with no `source` label floats disconnected from the code that produced it. The remaining pre-defined OCI annotations (`title`, `description`, `version`, `revision`, `created`, …) make an image self-describing and auditable: which commit built it, when, and what it contains. The OCI image-spec defines every `org.opencontainers.image.*` key as *optional*; the mandatory/SHOULD tier assignment below is **this spec's own policy**, layered on top of OCI for the key names and semantics and on GitHub for the source-linking behaviour—it's never presented as OCI conformance.

Beyond labels, the defaults of a naively-written `Dockerfile` are the wrong posture for a published image: it runs as root, may bake build secrets into an immutable layer, floats on a mutable `:latest` base tag, and ships its whole build toolchain. This spec turns the current authoritative guidance—the official Docker build best-practices, the OCI image-spec annotations, the GHCR labelling documentation, the hadolint rule set, and the CIS Docker Benchmark—into a normative checklist a `dockerfile-audit` skill enforces and a reviewer holds a `Dockerfile` to. Every load-bearing claim in this spec was adversarially verified against those primary sources (see `Version and tool anchors`).

## Goals

- Every published image carries the **mandatory OCI core labels** (`source`, `title`, `description`, `version`, `revision`, `created`) so it's linked to its GHCR repository, self-describing, and traceable to the commit and build that produced it
- The label check is **realistic about build-time values**: a label counts as present whether it's a static literal, an `ARG`-wired value, or injected by CI (`docker/metadata-action` / `docker build --label`), because `version`/`revision`/`created` are inherently per-build and hard-coding them is a reproducibility smell
- Every image is **secure by construction at build time**: a non-root numeric `USER`, no secrets in any layer, a base image pinned by tag **and** digest, and a `.dockerignore` that keeps the build context (and stray secrets) out—the four build-time hardening pillars the audit hard-fails on
- The **advisory** best practices (multi-stage builds, `COPY` over `ADD`, package-manager hygiene, `HEALTHCHECK`, cache-friendly ordering, robust `RUN` shells) are stated with their rationale and, where a mechanical check exists, mapped to the hadolint rule that verifies them
- The spec **references, not duplicates,** the runtime security controls owned by `spec/project/kubernetes-deployment-best-practices/`: the `Dockerfile`'s job is to make them *feasible* (non-root, no reliance on a writable root filesystem), not to restate the SecurityContext
- The spec is the shared bar across the portfolio's image-building repositories, so a reviewer moving between repos checks the same contract and the `dockerfile-audit` skill emits the same posture

## Non-Goals

- The image **publish** workflow itself—registry authentication, `docker push`, tag strategy, and the `docker/build-push-action` wiring—which is CI/CD configuration governed per-repository, not `Dockerfile` content (this spec only *credits* CI-side label injection, it doesn't prescribe the pipeline)
- **Runtime** container hardening (capability dropping, `readOnlyRootFilesystem`, `runAsNonRoot` admission, seccomp/AppArmor, `no-new-privileges`), which aren't `Dockerfile` instructions and are owned by `spec/project/kubernetes-deployment-best-practices/`; this spec only requires the build to *make them satisfiable*
- Application-level security (input validation, authn/authz, dependency CVEs), owned by the code-security and dependency-audit specs, not the image build
- Restating the full `Dockerfile` instruction reference or the complete OCI annotation catalogue; this spec pins the load-bearing keys and their rationale and delegates exhaustive references upstream
- BuildKit provenance / SBOM attestations as a *labelling* mechanism: they're a separate in-toto manifest surface and **MUST NOT** count toward OCI-label presence (an image may still carry them, but a label requirement is satisfied by a label, not an attestation)

## Requirements

### OCI image labels (mandatory pillar)

- Every published image **MUST** carry the OCI core annotations `org.opencontainers.image.source`, `.title`, `.description`, `.version`, `.revision`, and `.created`; their absence is a hard failure. Key names and semantics come from OCI, the mandatory tier assignment is this spec's policy, and `source` additionally carries GHCR-specific behaviour (below)
- `org.opencontainers.image.source` **MUST** be set to the source-repository URL (`https://github.com/<owner>/<repo>`), because GHCR uses exactly this label to connect the published package to its repository and inherit repository access; an image without it stays unlinked from its code
- A label **MUST** be counted as *present* when its value is any of: (a) a static string literal; (b) an `ARG`-wired substitution (`ARG VERSION` + `LABEL org.opencontainers.image.version="$VERSION"`) whose `ARG` is declared in the same stage; or (c) injected by CI via `docker/metadata-action` → `docker/build-push-action` or `docker build --label`/`--annotation`, detectable in the repository's workflow files. The audit **MUST NOT** hard-fail a required label that's absent from the `Dockerfile` but demonstrably injected by CI; it hard-fails only when the label is present in neither place
- `org.opencontainers.image.version`, `.revision`, and `.created` **SHOULD** be `ARG`-wired or CI-injected rather than hard-coded literals: `.created` is a per-build RFC 3339 timestamp, `.revision` is the source-control commit SHA, and `.version` is the released version—a committed literal for any of these is stale on the next build and is flagged as a reproducibility smell, not a hard failure
- In a **multi-stage** build the audit **MUST** evaluate the mandatory labels against the **final (publishing) stage** only: a `LABEL` reachable only through `COPY --from=`/`RUN --mount=from=` is discarded from the output image and is a false positive; a label in the final stage (or inherited from the final `FROM` base) is the only one that ships
- An image **SHOULD** also set `org.opencontainers.image.licenses` (an SPDX license expression), `.url`, and `.documentation` where known. GHCR surfaces `description` and `licenses` on the package page **for a single-manifest image**, reading them from the config-layer labels; for an **image index** (multi-arch, *or* any build carrying a default BuildKit provenance/SBOM attestation) this fails unless the values are also present as index-level *annotations* (see the next rule), and a label-only index image surfaces "No description provided"
- For an image published to GHCR via **BuildKit / `docker/build-push-action`**, the OCI core values **MUST** be propagated as **index-level annotations**, not only as config `LABEL`s. `docker/build-push-action@v7` attaches a provenance attestation **by default**, so *every* push—even single-platform—is an OCI **image index** (rendered "OS/Arch 2" on the package page), and for an index it's the index annotations, not a child manifest's config labels, that feed the GHCR package page. Wire the annotations through `docker/metadata-action`'s `annotations:` input with the environment variable `DOCKER_METADATA_ANNOTATIONS_LEVELS` including `index` (for example `manifest,index`), and pass the computed annotations to `build-push-action`'s `annotations:` input. The config-`LABEL` contract (above) is **retained** as the single-manifest / `docker inspect` baseline—this annotation requirement is *additive* for the GHCR/index case, it doesn't replace or weaken the label rule. The reference wiring:

  ```yaml
  - name: Extract metadata
    id: meta
    uses: docker/metadata-action@v6
    env:
      DOCKER_METADATA_ANNOTATIONS_LEVELS: manifest,index
    with:
      images: ghcr.io/<owner>/<image>
      annotations: |
        org.opencontainers.image.title=<image>
        org.opencontainers.image.description=<per-image description>
        org.opencontainers.image.source=https://github.com/<owner>/<repo>
        org.opencontainers.image.vendor=<vendor>

  - name: Build and push
    uses: docker/build-push-action@v7
    with:
      # ...
      labels: ${{ steps.meta.outputs.labels }}
      annotations: ${{ steps.meta.outputs.annotations }}
  ```

- An image **SHOULD** record `org.opencontainers.image.base.name` (the fully-qualified base reference, no assumed default registry) and `.base.digest` (`sha256:…`); these **MUST** be authored explicitly, because Docker/BuildKit doesn't populate them automatically today (unlike Podman/Buildah)
- BuildKit provenance and SBOM attestations **MUST NOT** be accepted in place of the required labels: they're separate in-toto manifests, and base-image identity surviving only in provenance doesn't satisfy the `base.*` label SHOULD

### Non-root user (mandatory pillar)

- The final stage **MUST** end with a `USER` instruction that switches to a dedicated **non-root** user before `CMD`/`ENTRYPOINT`; a final image whose effective user is root (whether by an explicit `USER 0`/`root` or by never setting `USER`) is a hard failure. Note that hadolint `DL3002` only flags a *last* `USER` of root and **doesn't** flag an image that never sets `USER`, so the audit **MUST** additionally assert that a `USER` instruction exists
- The `USER` **MUST** be expressed as a **numeric UID** (for example `USER 10001:10001`), not a name, so a Kubernetes `runAsNonRoot: true` admission check can verify non-root without resolving `/etc/passwd`; the user and its primary group **SHOULD** be created explicitly (a user with no primary group runs in the root group)
- The image **SHOULD** tolerate an arbitrary injected UID in group 0 (the OpenShift random-UID model): write only to group-0-writable paths or mounted volumes/tmpfs, and **MUST NOT** hard-depend on one specific UID owning a path

### Secrets out of layers (mandatory pillar)

- A `Dockerfile` **MUST NOT** introduce secrets into any image layer: it **MUST NOT** pass a secret through `ARG` or `ENV` (both persist in the image and are visible in `docker history`) and **MUST NOT** `COPY` a secret file into the image (a later `rm` only hides the bytes in an earlier layer—they remain recoverable)
- A build that needs a build-time credential **MUST** use a BuildKit secret mount (`RUN --mount=type=secret,id=<id>`, exposing the secret at `/run/secrets/<id>` only for that instruction) and/or a multi-stage split that keeps the credential out of the final stage
- This pillar pairs with `.dockerignore` (below) as belt-and-suspenders: because the whole build context is sent to the daemon, an ignored secret file can't be swept into a broad `COPY .`

### Base image pinning (mandatory pillar)

- Every `FROM` **MUST** pin its base image by **digest** in addition to a tag: `FROM registry/image:tag@sha256:<digest>` (the tag stays for readability, the digest guarantees immutability); a `FROM` that floats on `:latest`, on an untagged image, or on a tag with no digest is a hard failure. hadolint `DL3006` (must be tagged) and `DL3007` (must not be `:latest`) cover the tag half; the digest half is checked by this spec directly
- A digest-pinned base **MUST** be paired with an automated updater (Renovate's `docker.pinDigests` manager or Docker Scout) so pins stay patched rather than silently ageing; a digest pin with no updater is a stale-base risk, not a set-and-forget win
- The base image **SHOULD** be minimal and from a trusted source (an Official Image, a Verified Publisher, or a distroless/slim variant), so `runAsNonRoot` is satisfiable and the attack surface is small

### `.dockerignore` present (mandatory pillar)

- The build context **MUST** ship a `.dockerignore` file; its absence is a hard failure. The stated Docker rationale is build-context size and build speed (especially for remote builders); the secret-exclusion benefit (an ignored file can't be caught by a broad `COPY .`) is a real but *secondary, inferred* benefit and isn't attributed to Docker as its headline purpose
- The `.dockerignore` **SHOULD** exclude at minimum `.git`, `.env`, and credential/key files, reinforcing the no-secrets-in-layers pillar

### Advisory: Build correctness and image slimness

- A `Dockerfile` **SHOULD** use a **multi-stage** build so the final image ships only runtime artifacts and not the build toolchain, compilers, or debuggers, lowering both size and attack surface
- A `Dockerfile` **SHOULD** prefer `COPY` over `ADD`, reaching for `ADD` only for its two legitimate jobs—a remote HTTPS/Git URL fetch or the automatic extraction of a local tar; `ADD` used as a plain copy is flagged (hadolint `DL3020` vs the `DL3010` archive carve-out). It **MUST NOT** be read as a blanket ban on `ADD`
- Package-manager use **SHOULD** be hygienic: `apt-get install -y --no-install-recommends` (`DL3015`, `DL3014`), the cache cleaned in the same layer (`rm -rf /var/lib/apt/lists/*`, `DL3009`; `apk add --no-cache`), `apt-get` not `apt` (`DL3027`), and package versions pinned (`DL3008`/`DL3013`/`DL3016`/`DL3018`/… by ecosystem)
- `apt-get update` and `apt-get install` **SHOULD** run in a single `RUN` (a cached lone `update` layer yields stale installs); there is no dedicated hadolint rule for this, so it's prose- or custom-checked, with `DL3059` (consolidate consecutive `RUN`) as the nearest proxy
- A `Dockerfile` **SHOULD** order instructions least- to most-frequently-changing (install dependencies before copying application source, `COPY .` late) so the dependency layer survives source edits in the build cache; and **SHOULD** avoid running an in-image `apt-get upgrade`/`dist-upgrade` (non-reproducible drift; rebuild on a fresh pinned base instead, a pattern hadolint still flags via `DL3005` for apt, `DL3017` for apk, and `DL3031` for yum)
- A long-running server image **SHOULD** declare a `HEALTHCHECK` (`DL3057` off-by-default; `DL3012` flags a duplicate); this is advisory because Kubernetes **ignores** the `Dockerfile` `HEALTHCHECK`: the orchestrator liveness/readiness/startup probes (owned by the k8s sibling spec) are the authoritative gate at runtime
- A piped `RUN` **SHOULD** set `pipefail` (`SHELL ["/bin/sh","-o","pipefail","-c"]` or an inline `set -o pipefail &&`, `DL4006`), `CMD`/`ENTRYPOINT` **SHOULD** use the JSON/exec form for correct signal handling (`DL3025`), and `WORKDIR` **SHOULD** be absolute (`DL3000`, with `DL3003` flagging `RUN cd`)
- A repository **MAY** restrict `FROM` to an allow-listed registry set (`DL3026`) to pin its supply chain

### Runtime controls (out of scope—cross-reference)

- The `Dockerfile` **MUST NOT** be treated as the place to express runtime security: capability dropping, `readOnlyRootFilesystem`, `allowPrivilegeEscalation: false`/`no-new-privileges`, seccomp/AppArmor, and `runAsNonRoot` admission **aren't** `Dockerfile` instructions and are owned by `spec/project/kubernetes-deployment-best-practices/`
- The `Dockerfile`'s obligation is to make those runtime controls **feasible**: ship a non-root numeric `USER` (so `runAsNonRoot` is satisfiable), avoid depending on writing to the image filesystem at runtime (declare writable paths as `VOLUME` or expect a mounted `emptyDir`, so `readOnlyRootFilesystem` is satisfiable), and require no setuid/privilege escalation. This split is framed by NIST SP 800-190 least-privilege

### Version and tool anchors

- The spec's normative content **MUST** be read against these pinned sources, current as of 2026-07-10: the OCI image-spec `annotations.md` (14 pre-defined `org.opencontainers.image.*` keys, all OPTIONAL); the Docker build best-practices documentation (`docs.docker.com/build/building/best-practices`); the GHCR container-labelling documentation; the CIS Docker Benchmark **v1.7** (controls 4.1 non-root user, 4.6 `HEALTHCHECK`, 4.7 single-`RUN` update+install); and NIST SP 800-190 for the build/runtime least-privilege framing
- A `dockerfile-audit` implementation **MUST** pin a specific **hadolint** version, because hadolint's rule set drifts across releases (rules are added, deprecated, and their defaults change between versions, so a pinned version keeps rule coverage reproducible); it **SHOULD** note that hadolint's default `--failure-threshold` is `info`, so Info-level findings already fail a default run, and it **MAY** promote Warning/Info mandatory-adjacent rules to `error` via a `.hadolint.yaml` override
- Build-time label wiring **SHOULD** follow the `docker/metadata-action` model (it derives `title`, `description`, `url`, `source`, `version`, `created`, `revision`, `licenses` from the Git/GitHub context; `version` is the first computed tag, `revision` the commit SHA) so a repository need not hand-maintain the per-build values
- The **annotations-on-index** behaviour is a load-bearing claim pinned to the GHCR container-registry documentation: GHCR reads a multi-arch/index image's `description` (and the metadata surfaced on the package page) from the `annotations` field of the manifest index, while the config-`LABEL` route surfaces metadata only for the single-manifest ("most images") case; GitHub's own package-page hint states to set `org.opencontainers.image.description` in the annotations field for multi-arch images. `nolte/kamerplanter#455` is the reference implementation applying index annotations across all image build jobs

## Acceptance Criteria

- [ ] `spec/project/dockerfile-best-practices/` exists with `en.md` (canonical) and `de.md` (translation) and is listed in `spec/README.md`
- [ ] The OCI-label contract is a mandatory section: the six core keys (`source`, `title`, `description`, `version`, `revision`, `created`) are required with RFC 2119 keywords, the five SHOULD keys are listed, and `source` is tied to GHCR repository linkage
- [ ] The label **presence rule** is stated: static literal OR `ARG`-wired OR CI-injected (`docker/metadata-action`/`--label`) all count, and the audit hard-fails only when a label is present in neither the `Dockerfile` nor CI
- [ ] The **multi-stage final-stage** rule for labels is stated: a `LABEL` reachable only via `COPY --from=` is a false positive
- [ ] The **annotation-on-index** rule is stated: for a GHCR image published via BuildKit/`docker/build-push-action` the OCI core values MUST be propagated as index-level annotations (`DOCKER_METADATA_ANNOTATIONS_LEVELS` incl. `index`, passed to `build-push-action` `annotations:`), with the config-`LABEL` contract retained as the single-manifest baseline, and the canonical reference wiring is included
- [ ] The four mandatory non-label pillars are each stated with RFC 2119 keywords and rationale: non-root **numeric** `USER` (plus the "a `USER` must exist" check beyond `DL3002`), no secrets in layers (with the BuildKit secret-mount remedy), base image pinned by **tag + digest** (plus the required updater), and `.dockerignore` present
- [ ] The advisory best practices (multi-stage, `COPY` over `ADD`, package hygiene, single-`RUN` update+install, cache ordering, no `apt-get upgrade`, `HEALTHCHECK`, `pipefail`, exec-form `CMD`, absolute `WORKDIR`, registry allow-list) are each stated with their rationale and, where one exists, the hadolint rule ID that checks them
- [ ] Runtime controls are explicitly delegated to `spec/project/kubernetes-deployment-best-practices/`, with the `Dockerfile`'s feasibility obligations (non-root `USER`, no writable-rootfs dependency) stated
- [ ] The version/tool anchors are pinned: OCI image-spec, Docker best-practices, GHCR docs, CIS Docker Benchmark v1.7, NIST SP 800-190, a pinned hadolint version with its `info` failure-threshold note, and the `docker/metadata-action` label-wiring model
- [ ] A reviewer (or the future `dockerfile-audit` skill) can hold a real `Dockerfile` against this checklist and mark each requirement done or not done

## Open Questions

- **Portfolio-Scope promotion.** Should this spec stay `local` or be promoted to `portfolio`, so the portfolio's image-building repositories inherit the labelling-and-hardening bar by reference per `spec/project/portfolio-inherited-spec-layer/`? Promotion is an explicit maintainer act and is deferred here.
- **`apply`-merge semantics.** When the future `dockerfile-audit apply` operation patches a `Dockerfile` that already has a partial or malformed `LABEL` block, should it merge the missing keys into the existing final-stage block (later key wins, custom labels preserved) or append a new block? The research recommends merge; the exact algorithm is fixed when the skill is authored.
- **Monorepo Dockerfile discovery.** What's the discovery glob for a repository with several images (`Dockerfile`, `*.Dockerfile`, `docker/*/Dockerfile`, per-service directories)? Each ships its own image with its own required labels; the audit should evaluate each independently, and non-published/test `Dockerfile`s may need an opt-out marker.
- **Digest-pin strictness.** Is the digest half of base-image pinning a hard `MUST` for every repository from day one, or a `MUST` gated on the digest-updater (Renovate/Scout) being present, to avoid mandating pins a repo can't keep fresh? Currently authored as `MUST` + required updater.
- **Non-mechanizable pillars.** For the pillars with no hadolint rule (single-`RUN` update+install, secret-in-layer detection), should the `dockerfile-audit` skill ship a supplementary custom linter (grep / conftest-OPA), or is prose review acceptable?

## Sources

The external version and tool anchors above are author-time external assertions triangulated per `spec/claude/research-triangulate/` §Author-time assertions (author-time tier: at least three independent sources, ordered Primary-first). Retrieval date for every source below: 2026-07-24.

- **OCI image-spec pre-defined `org.opencontainers.image.*` annotation keys (all OPTIONAL)**: OpenContainers image-spec `annotations.md` on `main` (Primary), `https://github.com/opencontainers/image-spec/blob/main/annotations.md`; the rendered OpenContainers annotations spec (Primary), `https://specs.opencontainers.org/image-spec/annotations/`; Snyk, "How and when to use Docker labels / OCI container annotations" (Secondary), `https://snyk.io/blog/how-and-when-to-use-docker-labels-oci-container-annotations/`
- **CIS Docker Benchmark v1.7 controls (4.1 non-root user, 4.6 `HEALTHCHECK`, 4.7 single-`RUN` update+install)**: CIS Docker Benchmark v1.7 (Primary), `https://rayasec.com/wp-content/uploads/CIS-Benchmark/Docker/CIS_Docker_Benchmark_v1.7_PDF.pdf`; the `dev-sec/cis-docker-benchmark` control implementation for container images (Secondary), `https://github.com/dev-sec/cis-docker-benchmark/blob/master/controls/container_images.rb`; OneUptime, "How to Audit Docker with CIS Benchmarks" (Secondary), `https://oneuptime.com/blog/post/2026-01-16-docker-cis-benchmarks/view`
- **hadolint default `--failure-threshold` is `info`**: hadolint README (Primary), `https://github.com/hadolint/hadolint`; hadolint man page 2.14.0 on ManKier (Secondary), `https://www.mankier.com/1/hadolint`; hadolint man page on Linux Command Library (Secondary), `https://linuxcommandlibrary.com/man/hadolint`
- **hadolint rule-set drift (rules like `DL3005`/`DL3017`/`DL3031` persist and still fire; the rule set changes across releases so a pinned version is required)**: hadolint wiki page for `DL3031` (Primary), `https://github.com/hadolint/hadolint/wiki/DL3031`; hadolint wiki page for `DL3017` (Primary), `https://github.com/hadolint/hadolint/wiki/DL3017`; hadolint issue #1049 confirming `DL3005` still fires (Primary), `https://github.com/hadolint/hadolint/issues/1049`. An earlier draft stated these three rules "were removed"; that is false (the wiki pages are live and the rules still trigger) and was corrected above.
- **`docker/metadata-action` derives OCI labels from the Git/GitHub context (`version` is the first computed tag, `revision` the commit SHA)**: `docker/metadata-action` README (Primary), `https://github.com/docker/metadata-action`; Snyk, "How and when to use Docker labels / OCI container annotations" (Secondary), `https://snyk.io/blog/how-and-when-to-use-docker-labels-oci-container-annotations/`; Renovate documentation, Docker datasource (source/revision labels) (Secondary), `https://docs.renovatebot.com/modules/datasource/docker/`
- **NIST SP 800-190 least-privilege build/runtime framing**: NIST SP 800-190 Application Container Security Guide (Primary), `https://nvlpubs.nist.gov/nistpubs/specialpublications/nist.sp.800-190.pdf`; Red Hat, "Guide to NIST SP 800-190 compliance" (Secondary), `https://www.redhat.com/en/resources/guide-nist-compliance-container-environments-detail`; Anchore, "NIST SP 800-190 Overview & Compliance Checklist" (Secondary), `https://anchore.com/compliance/nist/800-190/`
- **GHCR reads a multi-arch/index image's description from the manifest-index `annotations` field (not a config `LABEL`)**: GitHub Docs, "Working with the Container registry" (Primary), `https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry`; Docker Docs, "Annotations" (index-level annotations) (Secondary), `https://docs.docker.com/build/metadata/annotations/`; `docker/build-push-action` discussion #1022 on setting multi-arch index annotations (Secondary), `https://github.com/docker/build-push-action/discussions/1022`
