# bjw-s Common Chart Deployment

Status: draft
Portfolio-Scope: local

## Context

Several self-hosted applications in the portfolio (for example `kamerplanter`) are built in-house and need a Kubernetes deployment. Rather than hand-write Deployment, Service, Ingress, PVC, ConfigMap, and Secret manifests per application, the portfolio standardises on the [bjw-s-labs `common` library chart](https://github.com/bjw-s-labs/helm-charts/tree/main/charts/library/common) as the foundation. `common` is a Helm **library** chart (not installable on its own): a consumer declares it as a `Chart.yaml` dependency and describes the whole workload in a single declarative values tree (`controllers`, `containers`, `service`, `ingress`, `persistence`, `configMaps`, `secrets`, `serviceAccount`, `rbac`, …). The library's loader (`bjw-s.common.loader.init` → `bjw-s.common.loader.generate`) then renders every Kubernetes object in a deterministic, dependency-aware order (`PersistentVolumeClaim`, `ServiceAccount`, and `ConfigMap` objects before the controllers that reference them, networking last) and validates the values against a bundled `values.schema.json`.

Writing such a chart by hand is repetitive and error-prone: an incomplete container block (missing probes, resources, or an `env` key the app reads), a service port that no ingress or probe references, a persistence volume mounted at the wrong path, or a secret wired in the clear are all easy to get wrong and only surface at install or run time. The manual, cluster-specific inputs an operator still has to supply (image tag, ingress host, storage class, secret material) also tend to live only in a maintainer's head.

This spec defines the contract for **generating a complete, correct, schema-valid application chart on top of the `common` library** for a self-hosted portfolio application, and for **recording every irreducible manual step in that chart's own README**. It's the foundation for a future engineering agent that takes an application (its image, its runtime configuration surface, its exposure needs) and emits the chart. The spec pins the upstream library as its normative anchor and delegates the library's full reference to upstream documentation rather than restating it—the same delegation discipline `spec/project/taskfile/` applies to `nolte/taskfiles`.

## Goals

- A self-hosted portfolio application gets a deployment chart built on the `common` library whose values are **complete** (every runtime input the container needs is declared) and **schema-valid** (they pass the library's bundled `values.schema.json`), so `helm install` produces a running workload without hidden gaps
- The generated chart is **runnable, not a stub**: it renders with `helm template`/`helm lint` at the library's minimum Kubernetes version with zero errors before it's considered done
- The container contract is configured completely and correctly: image with an explicit tag, `env`/`envFrom`, health probes, resource requests, and a hardened security context—no unbounded, un-probed, `latest`-tagged container
- Every action the chart **can't** perform itself (image tag, secret material, ingress host, storage class, dependency build, first-run bootstrap) is enumerated in the generated chart's README as an actionable manual step stating *what* to set, *where*, and *why*
- Charts generated across the portfolio share the same shape—one loader-driven templates entry point, the same value sections, the same README structure—so a reviewer moving between apps reads a familiar layout
- The upstream `common` version is pinned and tracked, and the full upstream reference is linked, not duplicated, so there's one source of truth for the library's behaviour

## Non-Goals

- Defining the application's business logic, its `Dockerfile`, or how its container image is built and published—the image coordinates are an **input** to chart generation, not an output
- Choosing whether to use the `common` library at all versus another chart approach—this spec assumes `common` has been chosen as the foundation; it governs how to use it well
- Governing the cluster-side deployment mechanism (a GitOps controller, `helm install` in CI, and similar)—this spec stops at the **chart boundary**; wiring the chart into a delivery pipeline is out of scope
- Prescribing the secret-management backend (Sealed Secrets, SOPS, External Secrets Operator)—this spec requires only that secret material is **never** committed in the clear and that the chart documents how the operator supplies it; which backend is a per-repository decision
- Restating the `common` library's full values reference, its template internals, or its per-key schema—the generated chart and the agent read the upstream `values.yaml`/`values.schema.json` at generation time; this spec links to upstream and governs only the consumer chart built on it
- Covering the `app-template` chart's use as a shrink-wrapped install (`helm install app-template -f values.yaml`)—this spec targets a **dedicated, versioned consumer chart** committed to the application's repository; `app-template` is noted only as an alternative for throwaway cases

## Requirements

### Upstream anchor and versioning

- A generated chart **MUST** declare `common` as a `Chart.yaml` dependency with an explicit, pinned version and the canonical repository, never a floating or absent version:

  ```yaml
  dependencies:
    - name: common
      version: 5.0.1   # pinned; bumped deliberately, tracked by Renovate
      repository: https://bjw-s-labs.github.io/helm-charts/
  ```

- The chart **MUST** set `kubeVersion` in `Chart.yaml` to the library's declared floor (`>=1.31.0-0` for `common` 5.0.x; the 4.x line declared `>=1.28.0-0`) or higher, so an install against an older cluster fails fast rather than rendering an incompatible object. The floor **MUST** track the pinned `common` version, because the library raises it across major bumps (see §Sources)
- The generator **MUST** run `helm dependency build` (or `update`) so a `Chart.lock` is produced and the library is vendored under `charts/` before any templating or linting; a chart shipped without a resolvable dependency is incomplete
- The chart's dependency on `common` **SHOULD** be tracked by the repository's dependency-update automation (Renovate, per `spec/project/dependency-audit/`) so version bumps are proposed and reviewed rather than drifting silently
- Generated values **MUST** validate against the library's bundled `values.schema.json`; the generator **MUST NOT** emit values that violate the schema (unknown keys, wrong types, missing required fields), because the library enforces the schema at render time

### Chart skeleton

- The generator **MUST** emit an `application`-type chart consisting of at minimum: `Chart.yaml` (name, chart `version`, `appVersion`, the `common` dependency block, `kubeVersion`), `values.yaml`, `README.md`, and a `templates/` entry point that invokes the `common` loader and nothing else
- Every rendered Kubernetes object **MUST** flow through the `common` loader; the chart **MUST NOT** contain hand-written Kubernetes manifests alongside the library except where the library genuinely can't express the object, in which case the exception is documented in the chart README
- The chart `version` (chart packaging SemVer) and `appVersion` (the application release being deployed) are distinct: `appVersion` **MUST** track the application's released image tag, and the chart `version` **MUST** be bumped when the chart's own shape changes independently of the app

### Controllers and containers (the core correctness contract)

- The chart **MUST** define at least one controller under `controllers.<id>` with an explicit `type`: `deployment` for a stateless service (the default), `statefulset` when the app needs stable network identity or per-replica storage, `cronjob`/`job` for scheduled or one-shot batch work, `daemonset` for node-level agents; the choice **MUST** match how the application actually runs, not defaulted blindly
- Each controller **MUST** carry at least one container under `controllers.<id>.containers.<id>` with a complete `image`: an explicit `repository` **and** an explicit, immutable `tag` (a digest or a released version—never `latest` and never empty), with `pullPolicy` consistent with the tag
- A container's runtime inputs **MUST** be declared completely: every configuration value the application reads at runtime is provided through `env` (literal or `valueFrom`) or `envFrom` (a referenced ConfigMap/Secret); `command`/`args` are set only to override the image's own entrypoint, not restated when the image default is correct
- Health probes **MUST** be configured to match the application: `probes.readiness` and `probes.liveness` are declared for any long-running server, and `probes.startup` is added where the app has a slow cold start; each probe **MUST** target a real endpoint/port or command—if the application exposes no HTTP health endpoint, a `tcp` or `exec` probe is used, and disabling a probe entirely **MUST** be a recorded decision with a rationale in the chart README, not a silent omission
- Each container **MUST** declare `resources` requests and **MUST** set a memory `limit` per `spec/project/kubernetes-deployment-best-practices/` §Resource requests, limits, and quality of service (which mandates a memory limit, ideally equal to the request); an unbounded container with no resource requests **MUST NOT** be emitted
- Each container (or the pod default) **MUST** set a hardened `securityContext` to the strength `spec/project/kubernetes-deployment-best-practices/` §Security context and Pod Security Standards mandates (`runAsNonRoot`, a non-zero `runAsUser`/`runAsGroup`, `readOnlyRootFilesystem`, dropped capabilities, `allowPrivilegeEscalation: false`, `seccompProfile.type: RuntimeDefault`), preferring a single `defaultPodOptions.securityContext` over per-container repetition; that spec is the authority on which fields are mandatory, and `readOnlyRootFilesystem` is among them—a writable path the app needs comes from a mounted `emptyDir` or volume, not from relaxing the setting
- Pre-start work (schema migrations, permission fix-ups, config templating) **SHOULD** be expressed as an `initContainers` entry rather than folded into the main container's `command`, so start-up ordering and failure attribution stay explicit

### Services and networking

- Every controller that serves network traffic **MUST** have a `service.<id>` bound to that controller (`service.<id>.controller: <controller-id>`) exposing **named** ports; the port **name** (not a bare number) is the reference other sections use, so a probe or ingress backend **MUST** reference the port by its declared name
- When the application is reachable from outside the cluster, the chart **MUST** generate an `ingress.<id>` (or, for Gateway API, a `route.<id>`) with `className`, `hosts[].host`, `paths[].path`/`pathType`, a backend `service` identifier + named port, and TLS configuration; the host and `className` are **operator inputs** surfaced as values and README steps and **MUST NOT** be hard-coded to a specific cluster's domain
- External exposure **SHOULD** default to disabled (`ingress.<id>.enabled: false`) so the chart installs safely before the operator supplies their host and ingress class, rather than emitting an ingress bound to a placeholder domain

### Persistence and configuration

- Durable application state **MUST** be declared under `persistence.<id>` with an explicit `type`: `persistentVolumeClaim` for durable data, `configMap`/`secret` for mounted configuration, `emptyDir` for scratch that need not survive a restart; the type **MUST** reflect how durable the data really is
- A `persistentVolumeClaim` persistence item **MUST** specify `accessMode` and `size`; `storageClass` is an **operator input** (surfaced, not hard-coded), and `existingClaim` **MUST** be supported as an alternative so an operator can bring a pre-provisioned volume
- Volume mounts **MUST** be explicit and correct: `globalMounts` when the volume belongs in every container of the owning controller, `advancedMounts.<controller>.<container>` when only a specific container needs it; the mount `path` **MUST** match the path the application actually reads or writes
- Non-secret configuration files the application reads from disk **SHOULD** be delivered through `configMaps.<id>` and mounted via a `persistence` item, not baked into the image, so configuration changes don't require a rebuild
- Secret material (credentials, tokens, keys) **MUST** be delivered through `secrets.<id>` or `envFrom`/`valueFrom` referencing an externally-managed `Secret`; the chart **MUST NOT** commit plaintext secret values in `values.yaml`, and the chart README **MUST** record how the operator supplies them (an existing `Secret`, External Secrets, SOPS, …)

### Pod-level defaults and identity

- Cross-cutting pod concerns (`securityContext`, `nodeSelector`, `tolerations`, `topologySpreadConstraints`, `imagePullSecrets`, `affinity`) **SHOULD** be set once under `defaultPodOptions` rather than repeated per controller; when one controller must diverge, the divergence is expressed through the controller's own pod options with an explicit merge/overwrite strategy
- If the application needs to call the Kubernetes API, the chart **MUST** declare an explicit `serviceAccount` and a least-privilege `rbac` binding scoped to exactly what the app needs; if it needs no API access, the chart relies on the default and doesn't over-grant

### Completeness verification (the generator's own gate)

- Before declaring the chart complete, the generator **MUST** verify it renders end-to-end: `helm dependency build`, then `helm template` (and `helm lint`) at the pinned `kubeVersion` floor, with zero errors—a chart that doesn't render isn't delivered
- The generator **MUST** cross-check referential integrity: every port name a probe or ingress references is declared on a service; every mount path maps to a declared `persistence` item; every `env`/`envFrom` key the container relies on resolves to a declared source; every `secret`/`configMap` reference exists—no dangling reference and no undeclared runtime requirement
- The generator **MUST NOT** leave placeholder or `TODO` values in `values.yaml` that would let `helm install` succeed into a broken workload; a value the operator must provide is either given a safe, install-able default **or** surfaced as a required README step and, where the library supports it, made to fail fast via schema `required`/validation rather than defaulting to a wrong value

### Manual steps → chart README

- The generated chart's `README.md` **MUST** contain a dedicated "Manual steps" (configuration) section enumerating every action the operator must take that the chart can't perform itself—at minimum: running `helm dependency build`; setting the image `tag`/`appVersion`; providing secret material; choosing the ingress `host` and `className`; choosing the `storageClass` or an `existingClaim`; and any first-run migration or bootstrap step
- Each manual step **MUST** state *what* to set, *where* (the concrete `values.yaml` key path), and *why*, so the step is actionable by an operator without reading the chart's templates or the upstream library internals
- The README **MUST NOT** duplicate the upstream `common` library reference; it links to the upstream documentation and documents only this chart's application-specific decisions and the required operator inputs
- A step the chart can safely default on the operator's behalf **MUST NOT** be listed as a manual step; the manual list is the **irreducible** operator surface—the set of inputs the chart genuinely can't supply—not an inventory of everything that's configurable

### Agent behaviour and inputs

- The generator's inputs are the target application and its runtime surface: the container image coordinates, the runtime configuration (`env` keys, ports, on-disk config file paths, persistent data paths, required secrets), and the app's exposure needs (internal-only versus externally reachable)
- The generator **SHOULD** derive these from the application's own source where it can (a `Dockerfile`'s `EXPOSE`/`VOLUME`/`ENV`, `compose` files, documented config paths, code that reads environment variables) and **confirm** what it finds rather than inventing values
- Where a required input is missing or ambiguous, the generator **MUST** elicit it from the operator (per `spec/project/requirements-elicitation/`) or record an explicit, visible assumption in the chart README—it **MUST NOT** silently guess a value that would render an incorrect deployment
- The generator **MUST** write the chart into the consuming repository's conventional chart location, matching an existing convention if the repository already has one (for example `deploy/charts/<app>/` or `charts/<app>/`) rather than imposing a new layout

## Acceptance Criteria

- [ ] `spec/project/bjw-s-common-chart-deployment/` exists with `en.md` (canonical) and `de.md` (translation) and is listed in `spec/README.md`
- [ ] The upstream anchor is pinned: the spec requires an explicit `common` dependency version, the canonical repository, a `kubeVersion` floor, `helm dependency build`, and `values.schema.json` validation
- [ ] The controllers/containers correctness contract is stated with RFC 2119 keywords and covers explicit image tag, complete `env`/`envFrom`, health probes, resource requests, security context, and `initContainers`
- [ ] The services/networking, persistence/configuration, and pod-defaults/identity requirements are each stated with named-port binding, explicit mount semantics (`globalMounts` versus `advancedMounts`), the no-plaintext-secret rule, and `defaultPodOptions` reuse
- [ ] The generator's completeness gate (renders via `helm template`/`helm lint` at the `kubeVersion` floor, referential-integrity cross-check, no placeholder values) is a testable requirement
- [ ] The README manual-steps contract is explicit and testable: a reviewer can verify the generated README has a dedicated section enumerating each irreducible operator step with *what*/*where*/*why*, and no step the chart could have defaulted
- [ ] The spec delegates the full upstream reference to bjw-s documentation rather than duplicating the library's per-key schema
- [ ] A worked example (a chart generated for `kamerplanter`) would pass `helm dependency build`, `helm lint`, and `helm template` at the pinned `kubeVersion` floor with a README that lists exactly the manual inputs that chart requires

## Open Questions

- **Scope promotion.** Should this spec stay `Portfolio-Scope: local` or be promoted to `portfolio`, so consumer repositories with self-hosted apps (`kamerplanter`, `kamerplanter-ha`, `claude-home-assistant`, `reachy-mini-app`) inherit it by reference per `spec/project/portfolio-inherited-spec-layer/`? Promotion is an explicit maintainer act and is deferred here.
- **Dedicated chart versus `app-template`.** Is a dedicated, versioned consumer chart always the target, or should the agent offer the shrink-wrapped `app-template` path for trivial/throwaway apps?
- **Secret-management backend.** Does the portfolio standardise on one backend (External Secrets Operator, SOPS, Sealed Secrets)? If so, the "no plaintext" requirement can name a concrete default instead of leaving the mechanism open.
- **GitOps boundary.** This spec stops at the chart. Should a companion spec govern wiring the chart into a GitOps controller, or is that intentionally left to each repository?
- **Chart location convention.** Is there a portfolio-standard chart path (`deploy/charts/<app>/` versus `charts/<app>/`) this spec should reference from `spec/project/project-structure/`, or does it remain a per-repository convention the agent detects?

## Sources

The upstream-anchor assertions above (the `common` library version pin and its `kubeVersion` floor) are author-time external assertions triangulated per `spec/claude/research-triangulate/` §Author-time assertions (author-time tier: at least three independent sources, ordered Primary-first). Retrieval date for every source below: 2026-07-24.

- **`common` library `version: 5.0.1` and canonical repository `https://bjw-s-labs.github.io/helm-charts/`**: `common` `Chart.yaml` at tag `common-5.0.1`, declaring `version: 5.0.1` (Primary), `https://raw.githubusercontent.com/bjw-s-labs/helm-charts/common-5.0.1/charts/library/common/Chart.yaml`; the published Helm repository index listing `common` 5.0.1 and the canonical repo URL (Primary), `https://bjw-s-labs.github.io/helm-charts/index.yaml`; the `bjw-s-labs/helm-charts` GitHub releases (Primary), `https://github.com/bjw-s-labs/helm-charts/releases`
- **`kubeVersion` floor `>=1.31.0-0` for `common` 5.0.x (the 4.x line declared `>=1.28.0-0`)**: `common` `Chart.yaml` at tag `common-5.0.1`, declaring `kubeVersion: ">=1.31.0-0"` (Primary), `https://raw.githubusercontent.com/bjw-s-labs/helm-charts/common-5.0.1/charts/library/common/Chart.yaml`; the Helm repository index, where `common` 4.0.1 through 4.6.2 carry `>=1.28.0-0` and 5.0.0/5.0.1 carry `>=1.31.0-0` (Primary), `https://bjw-s-labs.github.io/helm-charts/index.yaml`; the `common` 5.0.0 release note, "increased minimum Kubernetes requirements to version 1.31" (Secondary), `https://github.com/bjw-s-labs/helm-charts/releases`

The `>=1.28.0-0` floor stated in an earlier draft was accurate only for the `common` 4.x line; it was corrected to `>=1.31.0-0` to match the pinned 5.0.1 version, per the triangulation above.
