# Kubernetes Deployment Best Practices

Status: draft
Portfolio-Scope: local

## Context

Several self-hosted applications in the portfolio run on Kubernetes. `spec/project/bjw-s-common-chart-deployment/` governs *how* a Helm chart is generated on the bjw-s `common` library; this spec governs *what* a deployment must contain to be **secure** and **scalable**, independent of how the manifests are produced (a hand-written chart, the `common` library, or a Kustomize base). The two mandatory pillars of this spec are **network policies** and the **security context**, the areas where a wrong or absent setting most directly widens the attack surface or the blast radius of a compromise.

The defaults Kubernetes ships are deliberately permissive and are the wrong posture for a production workload. Every pod can reach every other pod until a `NetworkPolicy` isolates it, and that `NetworkPolicy` is inert unless the cluster's CNI plugin enforces it (`Calico` and `Cilium` do; `Flannel` doesn't). A container runs as root, with a writable root filesystem and the ability to escalate privileges, unless a `securityContext` locks it down. `PodSecurityPolicy`, the old cluster-side guardrail, was removed in Kubernetes 1.25 and replaced by Pod Security Admission, so the workload itself now carries responsibility for declaring the hardened settings that admission then verifies. On the scalability side, a single-replica deployment with no resource requests, no disruption budget, and no readiness probe can't be scheduled well, scaled safely, or drained without downtime.

This spec turns the current, authoritative guidance (official Kubernetes documentation, the NSA/CISA Kubernetes Hardening Guide, the OWASP Kubernetes Security Cheat Sheet, and the Pod Security Standards) into a normative checklist for a workload-level deployment, current for Kubernetes 1.28–1.31. It's the security-and-scalability contract a deployment generator (for example the `common`-chart generator) applies, and the bar a reviewer holds a deployment to.

## Goals

- A deployment carries the two mandatory pillars explicitly: a default-deny **network policy** relaxed only by least-privilege allow rules, and a hardened **security context** on every container that satisfies the `restricted` Pod Security Standard
- A deployment is **secure by construction**: non-root, non-privileged, no host namespaces, dropped capabilities, an immutable pinned image, and a least-privilege ServiceAccount, the settings the NSA/CISA guide and OWASP name as the minimum hardening baseline
- A deployment is **scalable and resilient by construction**: resource requests that let the scheduler place it, more than one replica spread across failure domains, a disruption budget, health probes that gate traffic, and a rollout strategy that shuts pods down gracefully
- Every normative requirement names the concrete field and its rationale, and flags the Kubernetes-version boundary where the guidance changed (Pod Security Admission GA, `PodSecurityPolicy` removal, the evolving AdminNetworkPolicy API), so the spec stays honest about what applies to a given cluster
- The spec is the shared bar across the portfolio's self-hosted workloads, so a reviewer moving between apps checks the same settings, and a generator emits the same posture

## Non-Goals

- Cluster and control-plane hardening (API-server flags, `etcd` encryption, kubelet configuration, node OS hardening, and audit-log policy), which the NSA/CISA guide also covers but which lives below the workload boundary this spec governs
- Installing or choosing the supporting infrastructure a requirement depends on: the CNI plugin that enforces `NetworkPolicy`, the metrics API that feeds the autoscaler, or the admission webhooks that enforce Pod Security Admission; this spec assumes they exist and requires the workload to be correct against them
- Restating the full field reference of any resource; the deployment and the generator read the upstream Kubernetes documentation for exhaustive field lists, while this spec pins the load-bearing settings and their rationale, not every option
- Prescribing a service mesh, an ingress controller, a secret-management backend, or a GitOps delivery tool, which are per-repository or portfolio-infrastructure decisions governed elsewhere
- Application-level security (input validation, authn/authz, dependency CVEs), which is the domain of the code-security and dependency-audit specs, not the deployment manifest

## Requirements

### Network policies (mandatory pillar)

- Each namespace running a workload **MUST** carry a default-deny `NetworkPolicy` that selects all pods (an empty `podSelector`) and lists **both** `Ingress` and `Egress` in `policyTypes` with no allow rules, so a pod that no explicit policy covers is isolated in both directions; connectivity is then re-opened only by explicit least-privilege allow policies
- Allow policies **MUST** select their peers by least privilege using label-based `podSelector` and `namespaceSelector` (or their combination), and use `ipBlock` (a `cidr` with an optional `except`) only where a real external CIDR is unavoidable, never a blanket allow-all
- Once default-deny `Egress` is in place, the deployment **MUST** add an explicit egress allow for DNS (UDP and TCP port 53 to the cluster's `kube-dns`/`CoreDNS` pods); without it, in-cluster name resolution breaks and the symptom is confusing, because connections fail at resolution rather than at connection
- A deployment **MUST NOT** treat `NetworkPolicy` as effective isolation without confirming the cluster's CNI plugin enforces it, and **MUST** record that CNI assumption; a `NetworkPolicy` on a cluster whose plugin ignores it (for example `Flannel`) is silently inert and gives false confidence
- The deployment **MUST** treat `NetworkPolicy` as an OSI layer-3/4 control only: it can't express layer-7 rules (HTTP path or method), can't target a pod by name (labels only), and can't control the cluster-egress source IP; where layer-7 or centralized admin control is genuinely required, a CNI-specific policy (`CiliumNetworkPolicy`) or the `AdminNetworkPolicy`/`BaselineAdminNetworkPolicy` API is used instead, and the choice is documented
- When `AdminNetworkPolicy` is used, the deployment **MUST** pin the API version present on the target cluster: the `v1alpha1` `AdminNetworkPolicy`/`BaselineAdminNetworkPolicy` model (a numeric `priority` from 0 to 1000 where lower wins, actions `Allow`/`Deny`/`Pass`, tier order `AdminNetworkPolicy` then `NetworkPolicy` then `BaselineAdminNetworkPolicy`) is being superseded by an emerging `ClusterNetworkPolicy` with a `tier` field, and the field names differ between them

### Security context and Pod Security Standards (mandatory pillar)

- Every container **MUST** declare a `securityContext` with `runAsNonRoot: true`, an explicit non-zero `runAsUser` and `runAsGroup`, `allowPrivilegeEscalation: false`, `privileged: false`, `capabilities.drop: ["ALL"]` (adding back only the specific capability the app provably needs), and `seccompProfile.type: RuntimeDefault`, the field set the `restricted` Pod Security Standard operationalizes
- Every container **MUST** set `readOnlyRootFilesystem: true`, providing any writable path the app needs through a mounted `emptyDir` or volume rather than a writable image layer, so an attack that depends on writing to the filesystem is stopped
- The pod **MUST NOT** use host namespaces or host mounts: `hostNetwork`, `hostPID`, and `hostIPC` stay `false` (absent) and the pod declares no `hostPath` volume, because these are the breakout features the NSA/CISA guide names first
- Settings that apply to every container in the pod **SHOULD** be set once at pod level (`spec.securityContext`, for example `runAsNonRoot` and an `fsGroup` for volume ownership) and overridden per container only where one container genuinely differs, so the hardened default is visible in one place
- The namespace **MUST** enforce the `restricted` Pod Security Standard through Pod Security Admission labels (`pod-security.kubernetes.io/enforce: restricted` plus `audit` and `warn` at the same level), pinning `pod-security.kubernetes.io/enforce-version` where reproducibility across cluster upgrades matters
- A deployment **MUST NOT** depend on `PodSecurityPolicy`: it was deprecated in 1.21 and removed in 1.25, and Pod Security Admission (stable since 1.25) is its built-in successor; note that the NSA/CISA v1.2 guide (2022) predates this and still describes admission as a 1.23 beta, so it's cited here for the hardening controls, not for the admission mechanism's status

### Resource requests, limits, and quality of service

- Every container **MUST** declare CPU and memory `requests`, because the `kube-scheduler` places a pod using its requests (not its limits); a container with no request competes poorly and lands in the `BestEffort` class that's evicted first under pressure
- Every container **MUST** declare a memory `limit`, and **SHOULD** set the memory limit equal to the memory request: memory limits are enforced by the kernel OOM-killer only once it detects memory pressure, so a request-equals-limit workload has predictable, `Guaranteed`-class behaviour instead of a surprise kill after over-allocation
- A CPU `limit` **SHOULD** be omitted or set only with deliberate headroom: a CPU limit is a hard limit the kernel enforces by throttling (the container can never exceed it), which can add latency, while the CPU request already protects scheduling, so a blanket-low CPU limit is a common self-inflicted performance problem

### Horizontal autoscaling

- A workload expected to scale with load **SHOULD** define a `HorizontalPodAutoscaler` (`scaleTargetRef` to the deployment, `minReplicas`, `maxReplicas`, and a metric target), so replica count tracks demand instead of being pinned to a guess
- A CPU-utilization `HorizontalPodAutoscaler` **MUST** run against pods that have CPU `requests` set, because target utilization is computed as a percentage of the request; if a targeted container has no CPU request, utilization is undefined and the autoscaler silently takes no action
- The `HorizontalPodAutoscaler` **MUST** have a metrics API available (the `metrics.k8s.io` API, usually provided by the separately-installed Metrics Server, or a custom/external metrics adapter); without it the autoscaler can't read the signal it scales on
- A `HorizontalPodAutoscaler` and a Vertical Pod Autoscaler **MUST NOT** both act on the same resource dimension (for example both adjusting CPU) for one workload, because their control loops conflict; event-driven scaling needs (queue depth, cron) **MAY** instead use KEDA

### Availability, disruption safety, and spreading

- A production workload **MUST** run at least two replicas (`replicas: 2` or more) so a single pod loss or a single-node drain doesn't take the service fully down, and **MUST NOT** be authored as a single-replica deployment presented as highly available
- A replicated workload **MUST** declare a `PodDisruptionBudget` (`minAvailable` or `maxUnavailable`) so voluntary disruptions (node drains for repair or upgrade, cluster scale-down, and controller-driven restarts) can't evict every replica at once; a `PodDisruptionBudget` doesn't cover involuntary disruptions (hardware failure, kernel panic), which stay a separate concern
- A replicated workload **SHOULD** spread its replicas across nodes and, where the cluster is multi-zone, across zones, using `topologySpreadConstraints` (`maxSkew`, a `topologyKey` such as `kubernetes.io/hostname` or `topology.kubernetes.io/zone`, and `whenUnsatisfiable`) or `affinity.podAntiAffinity`, so one node or zone failure removes only a bounded fraction of the replicas

### Health probes

- Every long-running server container **MUST** declare a `readinessProbe`, because readiness gates whether the pod receives Service traffic; without it a rolling update or a scale-up sends requests to a pod that isn't ready yet, and a rollout can black-hole traffic
- Every long-running server container **SHOULD** declare a `livenessProbe` to let the kubelet restart a wedged container, tuned (thresholds and delays) so a slow-but-healthy app isn't caught in a restart loop
- A container with a slow or variable cold start **SHOULD** declare a `startupProbe`, so the liveness check is held off until startup completes rather than killing the container mid-boot
- Every probe **MUST** target a real endpoint, port, or command: an HTTP probe points at a genuine health path, and a container with no HTTP health surface uses a `tcp` or `exec` probe instead of an empty or always-passing check

### Deployment rollout and graceful shutdown

- A `Deployment` **MUST** use the `RollingUpdate` strategy with explicit `maxSurge` and `maxUnavailable` sized for the replica count (`maxUnavailable: 0` where a zero-downtime rollout is required), rather than relying on unstated defaults
- The application **MUST** handle `SIGTERM` and shut down gracefully within `terminationGracePeriodSeconds` (the kubelet sends `SIGTERM`, waits the grace period, then `SIGKILL`); a workload that ignores `SIGTERM` is hard-killed and drops in-flight requests on every rollout and scale-down
- A workload that needs connections to drain before exit **SHOULD** use a `preStop` hook (or an in-process delay) so the pod stops receiving new traffic and finishes in-flight requests before the container is terminated

### Image supply-chain hygiene

- A container image **MUST** be pinned to an immutable reference (a specific released tag such as `v1.42.0` and/or a digest, `<image>@sha256:…`) and **MUST NOT** use the `:latest` tag, which makes the running version hard to track and rollback unreliable
- `imagePullPolicy` **SHOULD** be explicit and consistent with the reference (a digest defaults to `IfNotPresent`, a `:latest` tag defaults to `Always`), so image resolution is deterministic rather than dependent on Kubernetes' default-resolution rules
- An image from a private registry **MUST** supply credentials through `imagePullSecrets` referencing a `Secret`, never baked into the image or the manifest in the clear
- An image **SHOULD** ship a non-root user and be minimal (distroless or slim), so `runAsNonRoot` is satisfiable and the attack surface is small

### ServiceAccount and API least privilege

- A workload that doesn't call the Kubernetes API **MUST** set `automountServiceAccountToken: false` (on the pod spec or its ServiceAccount) so no API token is mounted into the pod, removing a credential an attacker could otherwise use after a compromise
- A workload that does call the Kubernetes API **MUST** run under a dedicated ServiceAccount (`spec.serviceAccountName`) bound to least-privilege RBAC, never the namespace `default` ServiceAccount, which every unassigned pod shares
- A workload ServiceAccount **MUST NOT** be granted `cluster-admin`, wildcard verbs/resources, or cluster-scoped RBAC where a namespaced `Role` suffices; the binding grants only the specific verbs and resources the app provably needs

## Acceptance Criteria

- [ ] `spec/project/kubernetes-deployment-best-practices/` exists with `en.md` (canonical) and `de.md` (translation) and is listed in `spec/README.md`
- [ ] Network policies are a mandatory section: default-deny for both `Ingress` and `Egress`, least-privilege label-based allow rules, the DNS-egress allowance, the CNI-enforcement caveat, and the layer-3/4-only limitation (with the `AdminNetworkPolicy`/`CiliumNetworkPolicy` escalation path) are all stated with RFC 2119 keywords
- [ ] Security context is a mandatory section: `runAsNonRoot`, non-zero `runAsUser`/`runAsGroup`, `allowPrivilegeEscalation: false`, `privileged: false`, `capabilities.drop: ["ALL"]`, `seccompProfile RuntimeDefault`, `readOnlyRootFilesystem`, and the no-host-namespace rule are required, and mapped to `restricted` Pod Security Admission enforcement
- [ ] The scalability requirements (resource requests/limits and QoS, HPA with its requests + metrics-API dependency, replicas + `PodDisruptionBudget` + spreading, probes, rollout strategy + graceful shutdown) are each stated with the concrete field and its rationale
- [ ] The supporting-security requirements (image pinning + no `:latest` + `imagePullSecrets`, and ServiceAccount `automountServiceAccountToken: false` + dedicated-SA least-privilege RBAC) are stated with RFC 2119 keywords
- [ ] Every version boundary is flagged: Pod Security Admission GA and `PodSecurityPolicy` removal in 1.25, the NSA/CISA v1.2 pre-GA snapshot, the CNI-enforcement dependency, and the evolving `AdminNetworkPolicy` API version
- [ ] The spec delegates exhaustive field references to the upstream Kubernetes documentation and cites the authoritative sources (Kubernetes docs, NSA/CISA, OWASP, Pod Security Standards) rather than duplicating them
- [ ] A reviewer can hold a real deployment (for example a `kamerplanter` chart) against this checklist and mark each requirement done or not done

## Open Questions

- **Portfolio-Scope promotion.** Should this spec stay `local` or be promoted to `portfolio`, so the portfolio's self-hosted workloads inherit the security-and-scalability bar by reference per `spec/project/portfolio-inherited-spec-layer/`? Promotion is an explicit maintainer act and is deferred here.
- **CNI of record.** Which CNI do the portfolio's target clusters run? The answer decides whether `NetworkPolicy` is actually enforced and whether the layer-7 escalation path is `CiliumNetworkPolicy` or the CRD of another CNI; the spec currently keeps this a documented per-cluster assumption.
- **AdminNetworkPolicy API version.** Should the spec target the `v1alpha1` `AdminNetworkPolicy`/`BaselineAdminNetworkPolicy` model or the emerging `ClusterNetworkPolicy` (`tier` field), given the CRD availability across Calico/Cilium/OVN-Kubernetes on 1.28–1.31 clusters?
- **Authoritative hardening citation.** Is there a post-v1.2 NSA/CISA revision or a current CIS Kubernetes Benchmark that reflects Pod Security Admission GA, to replace the 2022 snapshot as the primary hardening citation?
- **Generator coupling.** Which of these requirements should the `common`-chart generator (`spec/project/bjw-s-common-chart-deployment/`) emit automatically, and which are hard-fail versus warn in its completeness gate?

## Sources

The external hardening-guidance and platform-behaviour assertions above are author-time external assertions triangulated per `spec/claude/research-triangulate/` §Author-time assertions (author-time tier: at least three independent sources, ordered Primary-first). Retrieval date for every source below: 2026-07-24.

- **NSA/CISA Kubernetes Hardening Guide v1.2 (2022-08-29)**: NSA/CISA, *Kubernetes Hardening Guide*, version 1.2 (Primary), `https://media.defense.gov/2022/Aug/29/2003066362/-1/-1/0/CTR_KUBERNETES_HARDENING_GUIDANCE_1.2_20220829.PDF`; Kubernetes Blog, "A Closer Look at NSA/CISA Kubernetes Hardening Guidance" (Secondary), `https://kubernetes.io/blog/2021/10/05/nsa-cisa-kubernetes-hardening-guidance/`; `Fairwinds`, "An Overview of the NSA Kubernetes Hardening Guide" (Secondary), `https://www.fairwinds.com/blog/nsa-kubernetes-hardening-guide`
- **OWASP Kubernetes Security Cheat Sheet**: OWASP Cheat Sheet Series, "Kubernetes Security Cheat Sheet" rendered page (Primary), `https://cheatsheetseries.owasp.org/cheatsheets/Kubernetes_Security_Cheat_Sheet.html`; OWASP/CheatSheetSeries source markdown (Primary), `https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Kubernetes_Security_Cheat_Sheet.md`; NSA/CISA Hardening Guide v1.2 corroborating the same controls (Secondary), `https://media.defense.gov/2022/Aug/29/2003066362/-1/-1/0/CTR_KUBERNETES_HARDENING_GUIDANCE_1.2_20220829.PDF`
- **Pod Security Standards `restricted` profile** (`runAsNonRoot`, `allowPrivilegeEscalation: false`, `capabilities.drop: ["ALL"]`, `seccompProfile.type: RuntimeDefault`): Kubernetes documentation, "Pod Security Standards" (Primary), `https://kubernetes.io/docs/concepts/security/pod-security-standards/`; OWASP Kubernetes Security Cheat Sheet (Secondary), `https://cheatsheetseries.owasp.org/cheatsheets/Kubernetes_Security_Cheat_Sheet.html`; NSA/CISA Hardening Guide v1.2 (Secondary), `https://media.defense.gov/2022/Aug/29/2003066362/-1/-1/0/CTR_KUBERNETES_HARDENING_GUIDANCE_1.2_20220829.PDF`
- **`PodSecurityPolicy` deprecated in 1.21 and removed in 1.25; Pod Security Admission stable since 1.25**: Kubernetes documentation, "Pod Security Admission" (`FEATURE STATE: v1.25 [stable]`) (Primary), `https://kubernetes.io/docs/concepts/security/pod-security-admission/`; Kubernetes v1.25 release announcement (Primary), `https://kubernetes.io/blog/2022/08/23/kubernetes-v1-25-release/`; OWASP Kubernetes Security Cheat Sheet (Secondary), `https://cheatsheetseries.owasp.org/cheatsheets/Kubernetes_Security_Cheat_Sheet.html`
- **`NetworkPolicy` is inert unless the CNI plugin enforces it (Calico and Cilium enforce it; Flannel doesn't)**: Kubernetes documentation, "Network Policies" ("Network policies are implemented by the network plugin") (Primary), `https://kubernetes.io/docs/concepts/services-networking/network-policies/`; Calico documentation, "Kubernetes network policy" (Primary), `https://docs.tigera.io/calico/latest/network-policy/get-started/kubernetes-policy/kubernetes-network-policy`; Flannel README, which defers network policy to another project such as Calico (Primary), `https://github.com/flannel-io/flannel`
- **`AdminNetworkPolicy`/`BaselineAdminNetworkPolicy` v1alpha1 (numeric `priority` 0 to 1000, lower wins; actions Allow/Deny/Pass) and the emerging `ClusterNetworkPolicy` (`tier` field)**: SIG Network Policy API reference (Primary), `https://network-policy-api.sigs.k8s.io/reference/spec/`; SIG Network Policy blog, "API update for v1alpha2: ClusterNetworkPolicy replaces AdminNetworkPolicy and BaselineAdminNetworkPolicy" (Primary), `https://network-policy-api.sigs.k8s.io/blog/2025/10/09/api-update-for-v1alpha2-clusternetworkpolicy-replaces-adminnetworkpolicy-and-baselineadminnetworkpolicy/`; Red Hat OpenShift documentation for `BaselineAdminNetworkPolicy [policy.networking.k8s.io/v1alpha1]` (Secondary), `https://docs.redhat.com/en/documentation/openshift_container_platform/4.18/html/network_apis/baselineadminnetworkpolicy-policy-networking-k8s-io-v1alpha1`
