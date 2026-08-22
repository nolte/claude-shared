# Artifact Signing and Verification

Status: draft
Portfolio-Scope: portfolio

## Context

Portfolio repositories publish container images and Helm charts to the GitHub Container Registry (GHCR) and deploy them to Kubernetes through Argo CD. Nothing in that path proves *who built* an artifact or *rejects* an artifact nobody built: a GHCR tag is a mutable pointer with no registry-side immutability option [R12], a stolen `packages: write` credential can push or re-tag anything, and Argo CD 3.5 verifies neither chart nor image signatures for Helm/OCI sources [R13]. This spec closes that gap. It binds every published image and chart to the GitHub Actions workflow, commit, and ref that produced it—cryptographically, with Sigstore keyless signatures and build attestations—and it names the two places where that binding is enforced: the CI promotion gate and the Kubernetes admission webhook.

The content comes from a dedicated research pass on 2026-08-19 across the Sigstore, OCI, Helm, GitHub, Kyverno, and Argo CD primary sources, including live probes against `ghcr.io`. Three verified findings shape the rules below: GHCR doesn't implement the OCI 1.1 referrers API, so every signature and attestation lands in a client-maintained fallback index tagged `sha256-<digest>` (established by a live probe on 2026-08-19: the referrers endpoint returns `404 MANIFEST_UNKNOWN` while the fallback tag resolves; corroborated by [R11]); Cosign v3 stores signatures as OCI referrer artifacts in the Sigstore bundle format by default [R2]; and Kyverno deprecated `ClusterPolicy` in favor of the CEL-based `ImageValidatingPolicy` [R9].

**Boundaries:** `spec/project/continuous-delivery/` owns the delivery discipline—stage sequence, artifact immutability, and the securing-stage matrix; its §C requires a retrievable provenance record, and this spec supplies the concrete signing and verification contract for the OCI artifact classes, answering that spec's open question for images and charts. `spec/project/github-actions-best-practices/` owns workflow hardening (digest-pinned actions, least-privilege permissions, untrusted input); its §H already mandates platform-generated attestations, and this spec doesn't restate it. `spec/project/dockerfile-best-practices/` owns the build artifact itself, including OCI labels and base-image digest pinning. `spec/project/kubernetes-deployment-best-practices/` owns runtime posture, including digest-pinned workload references and `imagePullSecrets`. `spec/project/release-automation/` declares signing a non-goal; this spec is where that non-goal resolves.

**Readers:** contributors and AI agents wiring release workflows or cluster policy, the authors of the `cicd-pipeline-design` skill and `cicd-pipeline-reviewer` agent that operationalize the pipeline side, and operators responding to a supply-chain incident.

## Goals

- Every image and chart running in production is cryptographically attributable to one repository, one workflow, one commit, and one release ref, and a machine can check that attribution
- No long-lived signing key exists anywhere in CI—nothing to steal, rotate, or distribute
- Tag replacement, registry tampering, and replay of old artifacts are rejected at admission or detected by monitoring
- Each release digest carries a signature, a SLSA provenance attestation, and a signed SBOM, all retrievable from GHCR and verifiable offline
- Development, staging, and production differ only in verification policy, never in signing mechanics

## Non-Goals

- Signing non-OCI artifact classes (Python packages, npm packages, release binaries); `spec/project/continuous-delivery/` §C governs their provenance expectations
- Operating a private Sigstore instance (Fulcio, Rekor, TSA); the public-good instance is assumed
- Verifying Helm charts at Kubernetes admission—charts are rendered client-side and never reach the API server, so chart verification lives in the promotion gate by construction
- Notation/Notary trust stores, Docker Content Trust (shut down 2026-12-08 [R14]), GPG `.prov` provenance as the primary mechanism, and the `helm-sigstore` plugin (effectively unmaintained [R15])
- Runtime workload hardening, network policy, and application secret management

## Requirements

### A. Signing identity

- **MUST** sign keyless via Sigstore: the GitHub Actions OIDC token is exchanged for a short-lived Fulcio certificate whose SAN is the workflow identity and whose extensions carry repository, commit, ref, trigger, and runner environment [R1], [R3]
- **MUST NOT** store a private signing key in GitHub secrets, in the repository, or on a runner; a key-based `cosign sign --key` invocation in CI is a defect
- **MUST** grant `id-token: write` only to the job that signs and attests, never at workflow level
- **MUST** run signing jobs on GitHub-hosted runners and only on `push` events for release refs; verification policy pins the `runner_environment` and trigger extensions accordingly [R3]
- **SHOULD** centralize the signing steps in one reusable release workflow, so the certificate identity (`job_workflow_ref`) is a single value that policies and verifiers pin across repositories and the build gains the isolation that GitHub documents as the SLSA Build L3 path [R4]

### B. Digest discipline

- **MUST** sign and attest by digest (`name@sha256:…`), never by tag; a tag is a mutable pointer with no immutability option on GHCR [R12], while a digest is content-addressed by the OCI image spec [R5]
- **MUST** capture the digest from the producing step itself—`docker/build-push-action`'s `digest` output for images, the `Digest:` line of `helm push` for charts—rather than re-resolving a tag afterwards
- **MUST** reference images by digest in deployment manifests and GitOps values, per `spec/project/kubernetes-deployment-best-practices/` §Image supply-chain hygiene; tags remain human-readable annotations
- **MUST** check that the target version tag doesn't already exist before pushing a release image or chart, and fail the run when it does; GHCR silently overwrites tags and Helm doesn't refuse a re-push [R6]

### C. Container images: Sign and attest

- **MUST** publish, per release image digest, all three of: a Cosign keyless signature (`cosign sign --yes <name>@<digest>`), a SLSA v1 provenance attestation produced by the platform's attestation mechanism with `push-to-registry: true`, and an SPDX SBOM signed as a Cosign attestation (`cosign attest --type spdxjson`) [R2], [R7], [R8]
- **MUST** generate the SBOM against the pushed digest (`syft registry:<name>@<digest>`), not against a local build, so the described bytes are the signed bytes
- **MUST** sign only after the security scan of the pushed digest has passed; an unsigned image in GHCR is a safe intermediate state because policy refuses to admit it
- **MUST** sign the multi-arch index digest; signing each platform manifest additionally (`--recursive`) is a **MAY** reserved for consumers that pin platform digests directly
- **MUST NOT** use `cosign attach sbom` (deprecated and unsigned [R8]) or treat BuildKit's in-index SBOM/provenance as evidence—they're unsigned build metadata and **MAY** stay enabled as supplementary data
- **MUST NOT** downgrade to the legacy Cosign signature format (`--new-bundle-format=false`); verifiers consume the bundle format, and Cosign v4 removes the legacy path [R2]

### D. Helm charts: Sign and attest

- **MUST** publish charts as OCI artifacts (`helm push` to the portfolio registry path), capture the printed chart digest, and publish a Cosign keyless signature plus a SLSA provenance attestation for it, exactly as for images—a chart is an ordinary OCI manifest and Sigstore documents signing it [R7]
- **MUST** pin the image reference inside the chart's default values by digest before packaging, so a verified chart transitively pins a verified image
- **MUST** keep chart `version` equal to the release version and free of `+` build metadata, which OCI tags can't represent (Helm rewrites `+` to `_`) [R6]
- **MAY** additionally ship a GPG `.prov` file for external consumers of `helm install --verify`; when chosen, it becomes permanent, because the provenance layer changes the chart's manifest digest

### E. Storage in GHCR

- **MUST** treat the `sha256-<digest>` fallback index tags as load-bearing artifacts: GHCR lacks the referrers API, so Cosign, `actions/attest`, and ORAS all store the signature-to-subject link in that client-maintained tag (established by the live probe named in §Context; [R11])
- **MUST** exclude `sha256-*` tags, multi-arch child manifests, and any digest referenced from GitOps from every GHCR retention or cleanup job; a naive untagged-version cleanup deletes signatures, attestations, and platform manifests
- **MUST** authenticate registry writes in CI with the workflow's `GITHUB_TOKEN` and link each package to its repository via the `org.opencontainers.image.source` label, per `spec/project/dockerfile-best-practices/`
- **MUST** provision non-Actions consumers (cluster pull secrets, Argo CD repository credentials, Dependabot) with a classic PAT scoped to `read:packages` under a machine account with a recorded rotation cadence; fine-grained PATs and GitHub App installation tokens can't authenticate to GHCR as of 2026-08 [R16]
- **SHOULD** publish signing-relevant release evidence (the digest map of image digest, chart digest, commit, and tag) as an immutable release asset, so audit doesn't depend on GHCR retention

### F. Verification at promotion

- **MUST** verify, before any GitOps change that promotes a release: the image signature, the chart signature, the SBOM attestation, and the provenance attestation, each against the pinned OIDC issuer `https://token.actions.githubusercontent.com` and an anchored identity pattern for the release workflow
- **MUST** anchor every identity regular expression (`^…$`, escaped dots); an unanchored pattern also matches an attacker's look-alike repository
- **MUST** verify provenance with the platform tooling (`gh attestation verify` with `--signer-workflow`, `--source-ref`, and `--deny-self-hosted-runners`), because the source-ref and signer checks evaluate certificate extensions the workflow can't forge [R4]
- **MUST** write the promoted chart version and image digest to the GitOps repository through a reviewed pull request; the review is the human production gate

### G. Verification at admission

- **MUST** enforce image verification in the cluster with a CEL-based Kyverno `ImageValidatingPolicy`; new `ClusterPolicy`-style `verifyImages` rules **MUST NOT** be written, because Kyverno deprecated them with removal announced for v1.20 [R9]
- **MUST** restrict admitted images to the portfolio registry namespace and reject images whose signature doesn't match the pinned issuer and release-workflow identity, fail-closed (`failurePolicy: Fail`, deny action), with only cluster bootstrap namespaces exempt
- **MUST** resolve tags to digests at admission (`mutateDigest`) and reject digest-less references (`verifyDigest`), so a tag moved between promotion and pod creation can't swap content
- **MUST**, for production namespaces, additionally require the SLSA provenance and SBOM attestations and check the provenance predicate's source repository and release-ref pattern against expectations
- **MUST** account for the verification cache when revoking trust: a denied digest or narrowed identity takes effect only after the cache TTL, so incident response flushes the cache
- **SHOULD** run Kyverno background scans so existing pods are re-evaluated against policy changes in reports, since admission alone never blocks running workloads
- **MAY** use the Sigstore policy controller with GitHub's trust-policies chart instead, where a cluster enforces exclusively GitHub artifact attestations [R10]; the namespace opt-in model and the Helm chart's lagging app version are the accepted trade-offs

### H. GitOps deployment role

- **MUST** treat Argo CD as a deployment mechanism, not a verifier: Argo CD 3.5 verifies neither chart nor image signatures for Helm/OCI sources, and its source-integrity feature covers Git GPG only [R13]
- **MUST** restrict every `AppProject` to the portfolio registry namespace and the GitOps repository as sources, with tight destination lists
- **MUST** pin chart references to an exact version—never a SemVer range—and **SHOULD** move to digest-pinned chart references once the native OCI source type is adopted, which closes the chart-tag mutability window between promotion and sync
- **MUST** set server-side diff options (`ServerSideDiff=true,IncludeMutationWebhook=true`, `ServerSideApply=true`) on applications subject to digest mutation, so admission-time mutation doesn't produce permanent drift [R9]

### I. Monitoring, incident containment, and keys

- **MUST** monitor the transparency log for the portfolio's signing identities (`rekor-monitor` or equivalent) and alert on signatures that don't correspond to an expected release run; the Sigstore security model is detection-based and offers no revocation [R1]
- **MUST** contain a compromised-identity window by policy: deny the affected digests at admission, narrow the accepted identity, rebuild and re-release, and rotate the involved credentials—in that order
- **MUST** keep verification working during a Sigstore outage: signature bundles carry the inclusion proof and timestamp, and verifiers hold a pinned trusted root, so signing halts but admission keeps verifying
- **MUST** track the Sigstore trusted root as versioned configuration with a recurring update check; a stale root eventually fails verification after upstream key rotations
- **MAY** hold one offline hardware-backed key as a documented break-glass signer for a prolonged Sigstore outage; its use requires an incident record, and it never appears in CI

## Acceptance Criteria

- [ ] No `cosign.key`, key-based signing flag, or signing-key secret exists in any portfolio workflow; every signature verifies against the GitHub OIDC issuer (rolls up §A)
- [ ] Every release image digest and chart digest carries a verifiable signature, SLSA provenance attestation, and (images) SPDX SBOM attestation, retrievable from GHCR (rolls up §C, §D)
- [ ] `cosign verify` and `gh attestation verify` succeed against a release artifact using only the pinned issuer, anchored identity, source ref, and runner-environment constraints—and fail when any one constraint is wrong (rolls up §F)
- [ ] A deliberately unsigned test image in the portfolio registry namespace is rejected by admission in every environment, and a signed-but-attestation-less image is rejected in production (rolls up §G)
- [ ] Re-pushing an existing release version tag fails the pipeline before any registry write (§B)
- [ ] GHCR cleanup configuration demonstrably excludes `sha256-*` tags and multi-arch child manifests (§E)
- [ ] Argo CD `AppProject` source lists contain only the portfolio registry namespace and the GitOps repository, and chart references are exact versions or digests (§H)
- [ ] The transparency-log monitor is running and has alerted at least once in a rehearsed drill on an unexpected signature (§I)

## References

- Sources retrieved 2026-08-19.
- `spec/project/continuous-delivery/`: the delivery discipline whose §C provenance rule and §F securing-stage matrix this spec makes concrete for OCI artifacts
- `spec/project/github-actions-best-practices/`: workflow hardening and §H platform attestations, which §A and §C build on without restating
- `spec/project/dockerfile-best-practices/`: the build artifact contract, including the `org.opencontainers.image.source` label §E relies on
- `spec/project/kubernetes-deployment-best-practices/`: the runtime digest-pinning and pull-secret rules §B and §E reference
- `spec/project/release-automation/`: the release transition that declares signing a non-goal, resolved here
- [R1] Sigstore security model (**Primary**): <https://docs.sigstore.dev/about/security/>
- [R2] Cosign 3.0 release announcement—bundle format and OCI 1.1 referrer storage by default, legacy removal in v4 (**Primary**): <https://blog.sigstore.dev/cosign-3-0-available/>
- [R3] Fulcio certificate extensions (OID 1.3.6.1.4.1.57264.1.8–.24) (**Primary**): <https://github.com/sigstore/fulcio/blob/main/docs/oid-info.md>
- [R4] GitHub Docs: artifact attestations and the reusable-workflow path to SLSA v1 Build L3 (**Primary**): <https://docs.github.com/en/actions/security-for-github-actions/using-artifact-attestations/using-artifact-attestations-and-reusable-workflows-to-achieve-slsa-v1-build-level-3>
- [R5] OCI image spec: descriptor digests as content identifiers (**Primary**): <https://github.com/opencontainers/image-spec/blob/main/descriptor.md>
- [R6] Helm Docs: OCI-based registries—push output, tag mapping, digest references (**Primary**): <https://helm.sh/docs/topics/registries/>
- [R7] Sigstore Docs: signing other artifact types, including Helm charts (**Primary**): <https://docs.sigstore.dev/cosign/signing/other_types/>
- [R8] Cosign issue deprecating `attach sbom` in favor of SBOM attestations (**Primary**): <https://github.com/sigstore/cosign/issues/2755>
- [R9] Kyverno 1.17 announcement: `ClusterPolicy` deprecation schedule and CEL policy types (**Primary**): <https://kyverno.io/blog/2026/02/02/announcing-kyverno-release-1.17/>
- [R10] GitHub artifact-attestations Helm charts: the policy-controller trust-policies alternative (**Primary**): <https://github.com/github/artifact-attestations-helm-charts>
- [R11] GitHub community discussion: GHCR doesn't support the OCI referrers API (**Secondary**): <https://github.com/orgs/community/discussions/163029>
- [R12] GitHub community feature request for GHCR tag immutability, unanswered as of 2026-08 (**Secondary**): <https://github.com/orgs/community/discussions/181783>
- [R13] Argo CD Docs: source integrity verification is Git-GPG only, not Helm/OCI (**Primary**): <https://argo-cd.readthedocs.io/en/stable/user-guide/source-integrity/>
- [R14] Docker: Content Trust retirement and migration guidance, shutdown 2026-12-08 (**Primary**): <https://www.docker.com/blog/docker-content-trust-retirement-and-migration-guidance/>
- [R15] `helm-sigstore` maintainer issue questioning project status and the Rekor `helm` entry type (**Primary**): <https://github.com/sigstore/helm-sigstore/issues/426>
- [R16] GitHub Docs: GitHub Packages authenticates with classic personal access tokens only (**Primary**): <https://docs.github.com/en/packages/learn-github-packages/about-permissions-for-github-packages>

## Open Questions

- Are portfolio repositories that need artifact attestations ever private? GitHub artifact attestations for private repositories require GitHub Enterprise Cloud, and public-instance signatures publish the repository identity in the transparency log—open because the answer decides whether §C's provenance mechanism applies portfolio-wide or needs a Cosign-only fallback.
- When does the Argo CD native OCI source type (beta since 3.1) become the sanctioned chart reference path? Open because §H's digest-pinned chart reference depends on it, and the beta hasn't been exercised in this portfolio.
- Does the deployed Kyverno version verify GitHub attestation bundles from GHCR fallback tags in all attestor configurations? A crash report exists for key/cert attestors with transparency-log checks—open until a proof-of-concept in a staging cluster settles which predicate checks production policy can rely on.
- Do any external consumers require `helm install --verify`? Open because §D's optional GPG `.prov` layer is a one-way door: adding it later changes published chart digests.
