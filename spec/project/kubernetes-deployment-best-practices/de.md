# Kubernetes-Deployment-Best-Practices

Status: draft
Portfolio-Scope: local

## Kontext

Mehrere selbst gehostete Anwendungen im Portfolio laufen auf Kubernetes. `spec/project/bjw-s-common-chart-deployment/` regelt, *wie* ein Helm-Chart auf der bjw-s-`common`-Library generiert wird; diese Spec regelt, *was* ein Deployment enthalten muss, um **sicher** und **skalierbar** zu sein — unabhängig davon, wie die Manifeste erzeugt werden (ein handgeschriebenes Chart, die `common`-Library oder eine Kustomize-Base). Die zwei Pflichtsäulen dieser Spec sind **Netzwerkpolicies** und der **Security-Context**, die Bereiche, in denen eine falsche oder fehlende Einstellung die Angriffsfläche oder den Wirkungsradius einer Kompromittierung am direktesten vergrößert.

Die Standardwerte, die Kubernetes ausliefert, sind bewusst permissiv und die falsche Haltung für einen Produktions-Workload. Jeder Pod kann jeden anderen Pod erreichen, bis eine `NetworkPolicy` ihn isoliert, und diese `NetworkPolicy` ist wirkungslos, solange das CNI-Plugin des Clusters sie nicht durchsetzt (`Calico` und `Cilium` tun es; `Flannel` nicht). Ein Container läuft als root, mit beschreibbarem Root-Dateisystem und der Fähigkeit, Privilegien zu eskalieren, solange kein `securityContext` ihn einsperrt. `PodSecurityPolicy`, das alte cluster-seitige Schutzgeländer, wurde in Kubernetes 1.25 entfernt und durch Pod Security Admission ersetzt, sodass der Workload selbst nun die Verantwortung trägt, die gehärteten Einstellungen zu deklarieren, die die Admission dann verifiziert. Auf der Skalierbarkeitsseite kann ein Single-Replica-Deployment ohne Resource-Requests, ohne Disruption-Budget und ohne Readiness-Probe weder gut geplant noch sicher skaliert noch ohne Downtime gedraint werden.

Diese Spec überführt die aktuelle, autoritative Leitlinie (offizielle Kubernetes-Dokumentation, den NSA/CISA Kubernetes Hardening Guide, das OWASP Kubernetes Security Cheat Sheet und die Pod Security Standards) in eine normative Checkliste für ein Deployment auf Workload-Ebene, aktuell für Kubernetes 1.28–1.31. Sie ist der Security-und-Skalierbarkeits-Vertrag, den ein Deployment-Generator (zum Beispiel der `common`-Chart-Generator) anwendet, und die Messlatte, an der eine reviewende Person ein Deployment misst.

## Ziele

- Ein Deployment trägt die zwei Pflichtsäulen explizit: eine Default-Deny-**Netzwerkpolicy**, die nur durch Least-Privilege-Allow-Regeln gelockert wird, und einen gehärteten **Security-Context** auf jedem Container, der den `restricted`-Pod-Security-Standard erfüllt
- Ein Deployment ist **sicher by construction**: non-root, non-privileged, keine Host-Namespaces, weggelassene Capabilities, ein unveränderlich gepinntes Image und ein Least-Privilege-ServiceAccount — die Einstellungen, die der NSA/CISA-Guide und OWASP als minimale Härtungs-Baseline benennen
- Ein Deployment ist **skalierbar und resilient by construction**: Resource-Requests, die den Scheduler es platzieren lassen, mehr als eine über Ausfalldomänen verteilte Replika, ein Disruption-Budget, Health-Probes, die Traffic gaten, und eine Rollout-Strategie, die Pods graceful herunterfährt
- Jede normative Anforderung benennt das konkrete Feld und seine Begründung und markiert die Kubernetes-Versionsgrenze, an der sich die Leitlinie änderte (Pod Security Admission GA, `PodSecurityPolicy`-Entfernung, die sich entwickelnde AdminNetworkPolicy-API), sodass die Spec ehrlich bleibt, was für einen gegebenen Cluster gilt
- Die Spec ist die geteilte Messlatte über die selbst gehosteten Workloads des Portfolios, sodass eine reviewende Person beim Wechsel zwischen Apps dieselben Einstellungen prüft und ein Generator dieselbe Haltung ausgibt

## Nicht-Ziele

- Cluster- und Control-Plane-Härtung (API-Server-Flags, `etcd`-Verschlüsselung, kubelet-Konfiguration, Node-OS-Härtung und Audit-Log-Policy), die der NSA/CISA-Guide ebenfalls abdeckt, die aber unterhalb der Workload-Grenze liegt, die diese Spec regelt
- Das Installieren oder Wählen der unterstützenden Infrastruktur, von der eine Anforderung abhängt: das CNI-Plugin, das `NetworkPolicy` durchsetzt, die Metrics-API, die den Autoscaler speist, oder die Admission-Webhooks, die Pod Security Admission durchsetzen; diese Spec setzt ihre Existenz voraus und fordert, dass der Workload gegen sie korrekt ist
- Das erneute Aufschreiben der vollständigen Feld-Referenz einer Ressource; das Deployment und der Generator lesen die Upstream-Kubernetes-Dokumentation für erschöpfende Feldlisten, während diese Spec die tragenden Einstellungen und ihre Begründung pinnt, nicht jede Option
- Die Vorgabe eines Service-Mesh, eines Ingress-Controllers, eines Secret-Management-Backends oder eines GitOps-Delivery-Tools, die Entscheidungen pro Repository oder der Portfolio-Infrastruktur sind und anderswo geregelt werden
- Sicherheit auf Anwendungsebene (Eingabevalidierung, authn/authz, Dependency-CVEs), die die Domäne der Code-Security- und Dependency-Audit-Specs ist, nicht des Deployment-Manifests

## Anforderungen

### Netzwerkpolicies (Pflichtsäule)

- Jeder Namespace, der einen Workload betreibt, **MUSS** eine Default-Deny-`NetworkPolicy` tragen, die alle Pods auswählt (ein leerer `podSelector`) und **beide** Richtungen `Ingress` und `Egress` in `policyTypes` ohne Allow-Regeln listet, sodass ein Pod, den keine explizite Policy abdeckt, in beiden Richtungen isoliert ist; Konnektivität wird dann nur durch explizite Least-Privilege-Allow-Policies wieder geöffnet
- Allow-Policies **MÜSSEN** ihre Peers nach dem Least-Privilege-Prinzip über label-basierte `podSelector` und `namespaceSelector` (oder deren Kombination) auswählen und `ipBlock` (ein `cidr` mit optionalem `except`) nur dort verwenden, wo ein echter externer CIDR unvermeidlich ist, niemals als pauschales Allow-all
- Sobald Default-Deny-`Egress` in Kraft ist, **MUSS** das Deployment einen expliziten Egress-Allow für DNS ergänzen (UDP und TCP Port 53 zu den `kube-dns`/`CoreDNS`-Pods des Clusters); ohne ihn bricht die clusterinterne Namensauflösung, und das Symptom ist verwirrend, weil Verbindungen bei der Auflösung statt bei der Verbindung scheitern
- Ein Deployment **DARF NICHT** `NetworkPolicy` als wirksame Isolation behandeln, ohne zu bestätigen, dass das CNI-Plugin des Clusters sie durchsetzt, und **MUSS** diese CNI-Annahme festhalten; eine `NetworkPolicy` auf einem Cluster, dessen Plugin sie ignoriert (zum Beispiel `Flannel`), ist still wirkungslos und gibt falsche Sicherheit
- Das Deployment **MUSS** `NetworkPolicy` als reine OSI-Layer-3/4-Kontrolle behandeln: sie kann keine Layer-7-Regeln ausdrücken (HTTP-Pfad oder -Methode), kann einen Pod nicht per Name ansprechen (nur Labels) und kann die Cluster-Egress-Quell-IP nicht steuern; wo Layer 7 oder zentralisierte Admin-Kontrolle wirklich erforderlich ist, wird stattdessen eine CNI-spezifische Policy (`CiliumNetworkPolicy`) oder die `AdminNetworkPolicy`/`BaselineAdminNetworkPolicy`-API verwendet, und die Wahl wird dokumentiert
- Wenn `AdminNetworkPolicy` verwendet wird, **MUSS** das Deployment die auf dem Ziel-Cluster vorhandene API-Version pinnen: das `v1alpha1`-Modell `AdminNetworkPolicy`/`BaselineAdminNetworkPolicy` (ein numerisches `priority` von 0 bis 1000, wobei niedriger gewinnt, Aktionen `Allow`/`Deny`/`Pass`, Tier-Reihenfolge `AdminNetworkPolicy` dann `NetworkPolicy` dann `BaselineAdminNetworkPolicy`) wird durch ein aufkommendes `ClusterNetworkPolicy` mit einem `tier`-Feld abgelöst, und die Feldnamen unterscheiden sich zwischen beiden

### Security-Context und Pod Security Standards (Pflichtsäule)

- Jeder Container **MUSS** einen `securityContext` deklarieren mit `runAsNonRoot: true`, einem expliziten `runAsUser` und `runAsGroup` ungleich null, `allowPrivilegeEscalation: false`, `privileged: false`, `capabilities.drop: ["ALL"]` (nur die spezifische Capability zurückgebend, die die App nachweislich braucht) und `seccompProfile.type: RuntimeDefault` — die Feldmenge, die der `restricted`-Pod-Security-Standard operationalisiert
- Jeder Container **MUSS** `readOnlyRootFilesystem: true` setzen und jeden beschreibbaren Pfad, den die App braucht, über ein gemountetes `emptyDir` oder Volume statt über eine beschreibbare Image-Schicht bereitstellen, sodass ein Angriff, der auf das Schreiben ins Dateisystem angewiesen ist, gestoppt wird
- Der Pod **DARF NICHT** Host-Namespaces oder Host-Mounts verwenden: `hostNetwork`, `hostPID` und `hostIPC` bleiben `false` (abwesend), und der Pod deklariert kein `hostPath`-Volume, denn dies sind die Breakout-Features, die der NSA/CISA-Guide zuerst benennt
- Einstellungen, die für jeden Container im Pod gelten, **SOLLTEN** einmal auf Pod-Ebene gesetzt werden (`spec.securityContext`, zum Beispiel `runAsNonRoot` und ein `fsGroup` für Volume-Ownership) und nur dort pro Container überschrieben werden, wo ein Container wirklich abweicht, sodass der gehärtete Standard an einer Stelle sichtbar ist
- Der Namespace **MUSS** den `restricted`-Pod-Security-Standard über Pod-Security-Admission-Labels durchsetzen (`pod-security.kubernetes.io/enforce: restricted` plus `audit` und `warn` auf derselben Stufe) und `pod-security.kubernetes.io/enforce-version` pinnen, wo Reproduzierbarkeit über Cluster-Upgrades hinweg wichtig ist
- Ein Deployment **DARF NICHT** von `PodSecurityPolicy` abhängen: sie wurde in 1.21 deprecatet und in 1.25 entfernt, und Pod Security Admission (stabil seit 1.25) ist ihr eingebauter Nachfolger; man beachte, dass der NSA/CISA-v1.2-Guide (2022) dem vorausgeht und Admission noch als 1.23-Beta beschreibt, weshalb er hier für die Härtungs-Kontrollen zitiert wird, nicht für den Status des Admission-Mechanismus

### Resource-Requests, -Limits und Quality of Service

- Jeder Container **MUSS** CPU- und Memory-`requests` deklarieren, weil der `kube-scheduler` einen Pod anhand seiner Requests (nicht seiner Limits) platziert; ein Container ohne Request konkurriert schlecht und landet in der `BestEffort`-Klasse, die unter Druck zuerst evicted wird
- Jeder Container **MUSS** ein Memory-`limit` deklarieren und **SOLLTE** das Memory-Limit gleich dem Memory-Request setzen: Memory-Limits werden vom Kernel-OOM-Killer erst durchgesetzt, wenn er Speicherdruck erkennt, sodass ein Workload mit Request-gleich-Limit vorhersehbares `Guaranteed`-Klassen-Verhalten hat statt einer Überraschungs-Kill nach Über-Allokation
- Ein CPU-`limit` **SOLLTE** weggelassen oder nur mit bewusstem Spielraum gesetzt werden: ein CPU-Limit ist ein hartes Limit, das der Kernel durch Throttling durchsetzt (der Container kann es nie überschreiten), was Latenz hinzufügen kann, während der CPU-Request das Scheduling bereits schützt, sodass ein pauschal niedriges CPU-Limit ein häufiges selbstverschuldetes Performance-Problem ist

### Horizontales Autoscaling

- Ein Workload, von dem erwartet wird, dass er mit der Last skaliert, **SOLLTE** einen `HorizontalPodAutoscaler` definieren (`scaleTargetRef` auf das Deployment, `minReplicas`, `maxReplicas` und ein Metrik-Target), sodass die Replika-Zahl der Nachfrage folgt, statt auf eine Schätzung gepinnt zu sein
- Ein CPU-Utilization-`HorizontalPodAutoscaler` **MUSS** gegen Pods laufen, die CPU-`requests` gesetzt haben, weil das Ziel-Utilization als Prozentsatz des Requests berechnet wird; wenn ein anvisierter Container keinen CPU-Request hat, ist die Utilization undefiniert, und der Autoscaler unternimmt still keine Aktion
- Der `HorizontalPodAutoscaler` **MUSS** eine verfügbare Metrics-API haben (die `metrics.k8s.io`-API, üblicherweise vom separat installierten Metrics Server bereitgestellt, oder einen Custom-/External-Metrics-Adapter); ohne sie kann der Autoscaler das Signal nicht lesen, auf das er skaliert
- Ein `HorizontalPodAutoscaler` und ein Vertical Pod Autoscaler **DÜRFEN NICHT** beide auf derselben Ressourcendimension (zum Beispiel beide CPU verstellend) für einen Workload agieren, weil ihre Regelkreise kollidieren; event-getriebene Skalierungsbedarfe (Queue-Tiefe, Cron) **KÖNNEN** stattdessen KEDA verwenden

### Verfügbarkeit, Disruption-Sicherheit und Verteilung

- Ein Produktions-Workload **MUSS** mindestens zwei Replicas betreiben (`replicas: 2` oder mehr), sodass ein einzelner Pod-Verlust oder ein Single-Node-Drain den Dienst nicht vollständig lahmlegt, und **DARF NICHT** als Single-Replica-Deployment verfasst sein, das als hochverfügbar dargestellt wird
- Ein replizierter Workload **MUSS** ein `PodDisruptionBudget` deklarieren (`minAvailable` oder `maxUnavailable`), sodass freiwillige Disruptions (Node-Drains für Reparatur oder Upgrade, Cluster-Scale-down und Controller-getriebene Restarts) nicht jede Replika auf einmal evicten können; ein `PodDisruptionBudget` deckt keine unfreiwilligen Disruptions ab (Hardware-Ausfall, Kernel-Panic), die ein separates Anliegen bleiben
- Ein replizierter Workload **SOLLTE** seine Replicas über Nodes und, wo der Cluster mehrzonig ist, über Zonen verteilen — mittels `topologySpreadConstraints` (`maxSkew`, ein `topologyKey` wie `kubernetes.io/hostname` oder `topology.kubernetes.io/zone` und `whenUnsatisfiable`) oder `affinity.podAntiAffinity` — sodass ein Node- oder Zonen-Ausfall nur einen begrenzten Bruchteil der Replicas entfernt

### Health-Probes

- Jeder langlaufende Server-Container **MUSS** eine `readinessProbe` deklarieren, weil Readiness gatet, ob der Pod Service-Traffic erhält; ohne sie sendet ein Rolling-Update oder ein Scale-up Requests an einen Pod, der noch nicht bereit ist, und ein Rollout kann Traffic ins Leere laufen lassen
- Jeder langlaufende Server-Container **SOLLTE** eine `livenessProbe` deklarieren, damit der kubelet einen festgefahrenen Container neu starten kann, abgestimmt (Schwellen und Verzögerungen), sodass eine langsame-aber-gesunde App nicht in einer Restart-Schleife gefangen wird
- Ein Container mit langsamem oder variablem Kaltstart **SOLLTE** eine `startupProbe` deklarieren, sodass die Liveness-Prüfung zurückgehalten wird, bis der Start abgeschlossen ist, statt den Container mitten im Hochfahren zu töten
- Jede Probe **MUSS** auf einen realen Endpunkt, Port oder Befehl zielen: eine HTTP-Probe zeigt auf einen echten Health-Pfad, und ein Container ohne HTTP-Health-Fläche verwendet eine `tcp`- oder `exec`-Probe statt einer leeren oder stets bestehenden Prüfung

### Deployment-Rollout und Graceful Shutdown

- Ein `Deployment` **MUSS** die `RollingUpdate`-Strategie mit explizitem `maxSurge` und `maxUnavailable` verwenden, dimensioniert für die Replika-Zahl (`maxUnavailable: 0`, wo ein Zero-Downtime-Rollout erforderlich ist), statt sich auf ungenannte Defaults zu verlassen
- Die Anwendung **MUSS** `SIGTERM` behandeln und innerhalb von `terminationGracePeriodSeconds` graceful herunterfahren (der kubelet sendet `SIGTERM`, wartet die Grace-Periode ab, dann `SIGKILL`); ein Workload, der `SIGTERM` ignoriert, wird hart gekillt und verwirft laufende Requests bei jedem Rollout und Scale-down
- Ein Workload, der Verbindungen vor dem Beenden draind muss, **SOLLTE** einen `preStop`-Hook (oder eine In-Process-Verzögerung) verwenden, sodass der Pod aufhört, neuen Traffic zu erhalten, und laufende Requests abschließt, bevor der Container beendet wird

### Image-Supply-Chain-Hygiene

- Ein Container-Image **MUSS** auf eine unveränderliche Referenz gepinnt sein (ein spezifischer veröffentlichter Tag wie `v1.42.0` und/oder ein Digest, `<image>@sha256:…`) und **DARF NICHT** den `:latest`-Tag verwenden, der die laufende Version schwer nachverfolgbar und Rollback unzuverlässig macht
- `imagePullPolicy` **SOLLTE** explizit und konsistent mit der Referenz sein (ein Digest defaultet auf `IfNotPresent`, ein `:latest`-Tag defaultet auf `Always`), sodass die Image-Auflösung deterministisch ist statt von Kubernetes' Default-Auflösungsregeln abzuhängen
- Ein Image aus einer privaten Registry **MUSS** Credentials über `imagePullSecrets` mit Verweis auf ein `Secret` liefern, niemals ins Image gebacken oder im Klartext ins Manifest
- Ein Image **SOLLTE** einen Non-Root-User mitbringen und minimal sein (distroless oder slim), sodass `runAsNonRoot` erfüllbar ist und die Angriffsfläche klein bleibt

### ServiceAccount und API-Least-Privilege

- Ein Workload, der die Kubernetes-API nicht aufruft, **MUSS** `automountServiceAccountToken: false` setzen (im Pod-Spec oder seinem ServiceAccount), sodass kein API-Token in den Pod gemountet wird, was ein Credential entfernt, das ein Angreifer sonst nach einer Kompromittierung nutzen könnte
- Ein Workload, der die Kubernetes-API aufruft, **MUSS** unter einem dedizierten ServiceAccount (`spec.serviceAccountName`) laufen, das an Least-Privilege-RBAC gebunden ist, niemals dem `default`-ServiceAccount des Namespace, den jeder nicht zugewiesene Pod teilt
- Ein Workload-ServiceAccount **DARF NICHT** `cluster-admin`, Wildcard-Verbs/-Ressourcen oder cluster-scoped RBAC erhalten, wo eine namespaced `Role` genügt; die Bindung gewährt nur die spezifischen Verbs und Ressourcen, die die App nachweislich braucht

## Akzeptanzkriterien

- [ ] `spec/project/kubernetes-deployment-best-practices/` existiert mit `en.md` (kanonisch) und `de.md` (Übersetzung) und ist in `spec/README.md` gelistet
- [ ] Netzwerkpolicies sind ein Pflichtabschnitt: Default-Deny für sowohl `Ingress` als auch `Egress`, Least-Privilege-label-basierte Allow-Regeln, die DNS-Egress-Erlaubnis, der CNI-Durchsetzungs-Vorbehalt und die Layer-3/4-only-Beschränkung (mit dem `AdminNetworkPolicy`/`CiliumNetworkPolicy`-Eskalationspfad) sind alle mit RFC-2119-Schlüsselwörtern formuliert
- [ ] Security-Context ist ein Pflichtabschnitt: `runAsNonRoot`, `runAsUser`/`runAsGroup` ungleich null, `allowPrivilegeEscalation: false`, `privileged: false`, `capabilities.drop: ["ALL"]`, `seccompProfile RuntimeDefault`, `readOnlyRootFilesystem` und die Kein-Host-Namespace-Regel sind gefordert und auf `restricted`-Pod-Security-Admission-Durchsetzung abgebildet
- [ ] Die Skalierbarkeits-Anforderungen (Resource-Requests/-Limits und QoS, HPA mit seiner Requests-+-Metrics-API-Abhängigkeit, Replicas + `PodDisruptionBudget` + Verteilung, Probes, Rollout-Strategie + Graceful Shutdown) sind je mit dem konkreten Feld und seiner Begründung formuliert
- [ ] Die unterstützenden Sicherheits-Anforderungen (Image-Pinning + kein `:latest` + `imagePullSecrets` sowie ServiceAccount `automountServiceAccountToken: false` + dedizierte-SA-Least-Privilege-RBAC) sind mit RFC-2119-Schlüsselwörtern formuliert
- [ ] Jede Versionsgrenze ist markiert: Pod Security Admission GA und `PodSecurityPolicy`-Entfernung in 1.25, der NSA/CISA-v1.2-Pre-GA-Snapshot, die CNI-Durchsetzungs-Abhängigkeit und die sich entwickelnde `AdminNetworkPolicy`-API-Version
- [ ] Die Spec delegiert erschöpfende Feld-Referenzen an die Upstream-Kubernetes-Dokumentation und zitiert die autoritativen Quellen (Kubernetes-Docs, NSA/CISA, OWASP, Pod Security Standards), statt sie zu duplizieren
- [ ] Eine reviewende Person kann ein reales Deployment (zum Beispiel ein `kamerplanter`-Chart) gegen diese Checkliste halten und jede Anforderung als erledigt oder nicht erledigt markieren

## Offene Fragen

- **Portfolio-Scope-Promotion.** Sollte diese Spec `local` bleiben oder auf `portfolio` angehoben werden, sodass die selbst gehosteten Workloads des Portfolios die Security-und-Skalierbarkeits-Messlatte per Referenz gemäß `spec/project/portfolio-inherited-spec-layer/` erben? Die Promotion ist ein expliziter Wartungs-Akt und wird hier zurückgestellt.
- **CNI der Wahl.** Welches CNI betreiben die Ziel-Cluster des Portfolios? Die Antwort entscheidet, ob `NetworkPolicy` tatsächlich durchgesetzt wird und ob der Layer-7-Eskalationspfad `CiliumNetworkPolicy` oder das CRD eines anderen CNI ist; die Spec hält dies derzeit als dokumentierte Annahme pro Cluster.
- **AdminNetworkPolicy-API-Version.** Sollte die Spec das `v1alpha1`-Modell `AdminNetworkPolicy`/`BaselineAdminNetworkPolicy` oder das aufkommende `ClusterNetworkPolicy` (`tier`-Feld) anvisieren, angesichts der CRD-Verfügbarkeit über Calico/Cilium/OVN-Kubernetes auf 1.28–1.31-Clustern?
- **Autoritative Härtungs-Zitierung.** Gibt es eine Post-v1.2-NSA/CISA-Revision oder ein aktuelles CIS Kubernetes Benchmark, das Pod Security Admission GA widerspiegelt, um den 2022er-Snapshot als primäre Härtungs-Zitierung zu ersetzen?
- **Generator-Kopplung.** Welche dieser Anforderungen sollte der `common`-Chart-Generator (`spec/project/bjw-s-common-chart-deployment/`) automatisch ausgeben, und welche sind Hard-Fail versus Warn in seinem Vollständigkeits-Gate?

## Quellen

Die externen Härtungs-Leitfaden- und Plattform-Verhaltens-Aussagen oben sind Author-Time-externe Aussagen, trianguliert gemäß `spec/claude/research-triangulate/` §"Author-time assertions" (Author-Time-Stufe: mindestens drei unabhängige Quellen, Primary-first geordnet). Abrufdatum für jede Quelle unten: 2026-07-24.

- **NSA/CISA Kubernetes Hardening Guide v1.2 (2022-08-29)**: NSA/CISA, *Kubernetes Hardening Guide*, Version 1.2 (Primary), `https://media.defense.gov/2022/Aug/29/2003066362/-1/-1/0/CTR_KUBERNETES_HARDENING_GUIDANCE_1.2_20220829.PDF`; Kubernetes Blog, „A Closer Look at NSA/CISA Kubernetes Hardening Guidance" (Secondary), `https://kubernetes.io/blog/2021/10/05/nsa-cisa-kubernetes-hardening-guidance/`; Fairwinds, „An Overview of the NSA Kubernetes Hardening Guide" (Secondary), `https://www.fairwinds.com/blog/nsa-kubernetes-hardening-guide`
- **OWASP Kubernetes Security Cheat Sheet**: OWASP Cheat Sheet Series, „Kubernetes Security Cheat Sheet" gerenderte Seite (Primary), `https://cheatsheetseries.owasp.org/cheatsheets/Kubernetes_Security_Cheat_Sheet.html`; OWASP/CheatSheetSeries Quell-Markdown (Primary), `https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Kubernetes_Security_Cheat_Sheet.md`; NSA/CISA Hardening Guide v1.2, der dieselben Kontrollen bestätigt (Secondary), `https://media.defense.gov/2022/Aug/29/2003066362/-1/-1/0/CTR_KUBERNETES_HARDENING_GUIDANCE_1.2_20220829.PDF`
- **Pod Security Standards `restricted`-Profil** (`runAsNonRoot`, `allowPrivilegeEscalation: false`, `capabilities.drop: ["ALL"]`, `seccompProfile.type: RuntimeDefault`): Kubernetes-Dokumentation, „Pod Security Standards" (Primary), `https://kubernetes.io/docs/concepts/security/pod-security-standards/`; OWASP Kubernetes Security Cheat Sheet (Secondary), `https://cheatsheetseries.owasp.org/cheatsheets/Kubernetes_Security_Cheat_Sheet.html`; NSA/CISA Hardening Guide v1.2 (Secondary), `https://media.defense.gov/2022/Aug/29/2003066362/-1/-1/0/CTR_KUBERNETES_HARDENING_GUIDANCE_1.2_20220829.PDF`
- **`PodSecurityPolicy` in 1.21 deprecated und in 1.25 entfernt; Pod Security Admission stable seit 1.25**: Kubernetes-Dokumentation, „Pod Security Admission" (`FEATURE STATE: v1.25 [stable]`) (Primary), `https://kubernetes.io/docs/concepts/security/pod-security-admission/`; Kubernetes-v1.25-Release-Ankündigung (Primary), `https://kubernetes.io/blog/2022/08/23/kubernetes-v1-25-release/`; OWASP Kubernetes Security Cheat Sheet (Secondary), `https://cheatsheetseries.owasp.org/cheatsheets/Kubernetes_Security_Cheat_Sheet.html`
- **`NetworkPolicy` ist wirkungslos, solange das CNI-Plugin sie nicht durchsetzt (Calico und Cilium setzen sie durch; Flannel nicht)**: Kubernetes-Dokumentation, „Network Policies" („Network policies are implemented by the network plugin") (Primary), `https://kubernetes.io/docs/concepts/services-networking/network-policies/`; Calico-Dokumentation, „Kubernetes network policy" (Primary), `https://docs.tigera.io/calico/latest/network-policy/get-started/kubernetes-policy/kubernetes-network-policy`; Flannel-README, das Network Policy an ein anderes Projekt wie Calico delegiert (Primary), `https://github.com/flannel-io/flannel`
- **`AdminNetworkPolicy`/`BaselineAdminNetworkPolicy` v1alpha1 (numerische `priority` 0 bis 1000, kleinerer Wert gewinnt; Aktionen Allow/Deny/Pass) und das aufkommende `ClusterNetworkPolicy` (`tier`-Feld)**: SIG-Network-Policy-API-Referenz (Primary), `https://network-policy-api.sigs.k8s.io/reference/spec/`; SIG-Network-Policy-Blog, „API update for v1alpha2: ClusterNetworkPolicy replaces AdminNetworkPolicy and BaselineAdminNetworkPolicy" (Primary), `https://network-policy-api.sigs.k8s.io/blog/2025/10/09/api-update-for-v1alpha2-clusternetworkpolicy-replaces-adminnetworkpolicy-and-baselineadminnetworkpolicy/`; Red-Hat-OpenShift-Dokumentation für `BaselineAdminNetworkPolicy [policy.networking.k8s.io/v1alpha1]` (Secondary), `https://docs.redhat.com/en/documentation/openshift_container_platform/4.18/html/network_apis/baselineadminnetworkpolicy-policy-networking-k8s-io-v1alpha1`
