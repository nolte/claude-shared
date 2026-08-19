# Artefakt-Signierung und -Verifikation

Status: draft
Portfolio-Scope: portfolio

## Kontext

Portfolio-Repositories veröffentlichen Container-Images und Helm Charts in der GitHub Container Registry (GHCR) und deployen sie über Argo CD nach Kubernetes. Nichts auf diesem Pfad beweist, *wer* ein Artefakt gebaut hat, oder *weist* ein Artefakt *ab*, das niemand gebaut hat: Ein GHCR-Tag ist ein veränderlicher Zeiger ohne registry-seitige Unveränderlichkeitsoption [R12], ein gestohlenes Credential mit `packages: write` kann alles pushen oder umtaggen, und Argo CD 3.5 verifiziert für Helm-/OCI-Quellen weder Chart- noch Image-Signaturen [R13]. Diese Spec schließt diese Lücke. Sie bindet jedes veröffentlichte Image und Chart an den GitHub-Actions-Workflow, den Commit und den Ref, die es erzeugt haben — kryptographisch, mit Sigstore-Keyless-Signaturen und Build-Attestations — und benennt die beiden Stellen, an denen diese Bindung durchgesetzt wird: das CI-Promotion-Gate und den Kubernetes-Admission-Webhook.

Der Inhalt stammt aus einem dedizierten Recherchelauf am 2026-08-19 über die Primärquellen von Sigstore, OCI, Helm, GitHub, Kyverno und Argo CD, einschließlich Live-Proben gegen `ghcr.io`. Drei verifizierte Befunde prägen die folgenden Regeln: GHCR implementiert die OCI-1.1-Referrers-API nicht, sodass jede Signatur und Attestation in einem client-gepflegten Fallback-Index mit dem Tag `sha256-<digest>` landet (belegt durch eine Live-Probe am 2026-08-19: Der Referrers-Endpoint liefert `404 MANIFEST_UNKNOWN`, während der Fallback-Tag auflöst; bestätigt durch [R11]); Cosign v3 speichert Signaturen standardmäßig als OCI-Referrer-Artefakte im Sigstore-Bundle-Format [R2]; und Kyverno hat `ClusterPolicy` zugunsten der CEL-basierten `ImageValidatingPolicy` als veraltet markiert [R9].

**Abgrenzung:** `spec/project/continuous-delivery/` besitzt die Auslieferungsdisziplin — Stufenfolge, Artefakt-Unveränderlichkeit und die Securing-Stage-Matrix; ihr §C verlangt einen abrufbaren Provenance-Nachweis, und diese Spec liefert den konkreten Signier- und Verifikationsvertrag für die OCI-Artefaktklassen und beantwortet damit die offene Frage jener Spec für Images und Charts. `spec/project/github-actions-best-practices/` besitzt die Workflow-Härtung (digest-gepinnte Actions, minimale Berechtigungen, nicht vertrauenswürdige Eingaben); ihr §H schreibt plattform-erzeugte Attestations bereits vor, und diese Spec wiederholt das nicht. `spec/project/dockerfile-best-practices/` besitzt das Build-Artefakt selbst, einschließlich OCI-Labels und Base-Image-Digest-Pinning. `spec/project/kubernetes-deployment-best-practices/` besitzt die Runtime-Haltung, einschließlich digest-gepinnter Workload-Referenzen und `imagePullSecrets`. `spec/project/release-automation/` erklärt Signierung zum Non-Goal; diese Spec ist der Ort, an dem sich dieses Non-Goal auflöst.

**Leser:** Contributor und KI-Agenten, die Release-Workflows oder Cluster-Policies verdrahten, die Autoren des Skills `cicd-pipeline-design` und des Agenten `cicd-pipeline-reviewer`, die die Pipeline-Seite operationalisieren, sowie Operatoren, die auf einen Supply-Chain-Vorfall reagieren.

## Ziele

- Jedes in Produktion laufende Image und Chart ist kryptographisch einem Repository, einem Workflow, einem Commit und einem Release-Ref zuordenbar, und eine Maschine kann diese Zuordnung prüfen
- Nirgendwo in CI existiert ein langlebiger Signierschlüssel — nichts zu stehlen, zu rotieren oder zu verteilen
- Tag-Replacement, Registry-Manipulation und Replay alter Artefakte werden am Admission-Punkt abgewiesen oder durch Monitoring erkannt
- Jeder Release-Digest trägt eine Signatur, eine SLSA-Provenance-Attestation und eine signierte SBOM, alle aus GHCR abrufbar und offline verifizierbar
- Development, Staging und Produktion unterscheiden sich nur in der Verifikations-Policy, nie in der Signiermechanik

## Non-Goals

- Signierung von Nicht-OCI-Artefaktklassen (Python-Pakete, npm-Pakete, Release-Binaries); deren Provenance-Erwartungen regelt `spec/project/continuous-delivery/` §C
- Betrieb einer privaten Sigstore-Instanz (Fulcio, Rekor, TSA); die Public-Good-Instanz wird vorausgesetzt
- Verifikation von Helm Charts am Kubernetes-Admission-Punkt — Charts werden clientseitig gerendert und erreichen den API-Server nie, die Chart-Verifikation liegt daher konstruktionsbedingt im Promotion-Gate
- Notation-/Notary-Trust-Stores, Docker Content Trust (Abschaltung 2026-12-08 [R14]), GPG-`.prov`-Provenance als primärer Mechanismus und das Plugin `helm-sigstore` (faktisch ungewartet [R15])
- Runtime-Workload-Härtung, Network Policy und Secret-Management von Anwendungen

## Anforderungen

### A. Signieridentität

- **MUSS** keyless über Sigstore signieren: Das GitHub-Actions-OIDC-Token wird gegen ein kurzlebiges Fulcio-Zertifikat getauscht, dessen SAN die Workflow-Identität ist und dessen Extensions Repository, Commit, Ref, Trigger und Runner-Umgebung tragen [R1], [R3]
- **DARF NICHT** einen privaten Signierschlüssel in GitHub-Secrets, im Repository oder auf einem Runner ablegen; ein key-basierter `cosign sign --key`-Aufruf in CI ist ein Defekt
- **MUSS** `id-token: write` ausschließlich dem Job gewähren, der signiert und attestiert, nie auf Workflow-Ebene
- **MUSS** Signier-Jobs auf GitHub-gehosteten Runnern und nur auf `push`-Ereignisse für Release-Refs ausführen; die Verifikations-Policy pinnt die Extensions für `runner_environment` und Trigger entsprechend [R3]
- **SOLLTE** die Signierschritte in einem wiederverwendbaren Release-Workflow zentralisieren, sodass die Zertifikatsidentität (`job_workflow_ref`) ein einzelner, repository-übergreifend pinbarer Wert ist und der Build die Isolation erhält, die GitHub als Pfad zu SLSA Build L3 dokumentiert [R4]

### B. Digest-Disziplin

- **MUSS** per Digest (`name@sha256:…`) signieren und attestieren, nie per Tag; ein Tag ist ein veränderlicher Zeiger ohne Unveränderlichkeitsoption auf GHCR [R12], während ein Digest gemäß OCI-Image-Spec content-adressiert ist [R5]
- **MUSS** den Digest aus dem erzeugenden Schritt selbst erfassen — dem `digest`-Output von `docker/build-push-action` für Images, der `Digest:`-Zeile von `helm push` für Charts — statt einen Tag nachträglich erneut aufzulösen
- **MUSS** Images in Deployment-Manifesten und GitOps-Values per Digest referenzieren, gemäß `spec/project/kubernetes-deployment-best-practices/` §Image supply-chain hygiene; Tags bleiben menschenlesbare Annotationen
- **MUSS** vor dem Push eines Release-Images oder -Charts prüfen, dass der Ziel-Versions-Tag noch nicht existiert, und den Lauf andernfalls scheitern lassen; GHCR überschreibt Tags stillschweigend und Helm verweigert einen erneuten Push nicht [R6]

### C. Container-Images: Signieren und Attestieren

- **MUSS** pro Release-Image-Digest alle drei veröffentlichen: eine Cosign-Keyless-Signatur (`cosign sign --yes <name>@<digest>`), eine SLSA-v1-Provenance-Attestation, erzeugt durch den Attestierungsmechanismus der Plattform mit `push-to-registry: true`, und eine SPDX-SBOM, signiert als Cosign-Attestation (`cosign attest --type spdxjson`) [R2], [R7], [R8]
- **MUSS** die SBOM gegen den gepushten Digest erzeugen (`syft registry:<name>@<digest>`), nicht gegen einen lokalen Build, damit die beschriebenen Bytes die signierten Bytes sind
- **MUSS** erst signieren, nachdem der Security-Scan des gepushten Digests bestanden ist; ein unsigniertes Image in GHCR ist ein sicherer Zwischenzustand, weil die Policy seine Zulassung verweigert
- **MUSS** den Multi-Arch-Index-Digest signieren; das zusätzliche Signieren jedes Plattform-Manifests (`--recursive`) ist ein **KANN** für Konsumenten, die Plattform-Digests direkt pinnen
- **DARF NICHT** `cosign attach sbom` verwenden (veraltet und unsigniert [R8]) oder BuildKits In-Index-SBOM/-Provenance als Nachweis werten — sie sind unsignierte Build-Metadaten und **KÖNNEN** als ergänzende Daten aktiviert bleiben
- **DARF NICHT** auf Cosigns Legacy-Signaturformat zurückfallen (`--new-bundle-format=false`); die Verifier konsumieren das Bundle-Format, und Cosign v4 entfernt den Legacy-Pfad [R2]

### D. Helm Charts: Signieren und Attestieren

- **MUSS** Charts als OCI-Artefakte veröffentlichen (`helm push` auf den Portfolio-Registry-Pfad), den ausgegebenen Chart-Digest erfassen und dafür eine Cosign-Keyless-Signatur plus eine SLSA-Provenance-Attestation veröffentlichen, genau wie bei Images — ein Chart ist ein gewöhnliches OCI-Manifest, und Sigstore dokumentiert dessen Signierung [R7]
- **MUSS** die Image-Referenz in den Default-Values des Charts vor dem Paketieren per Digest pinnen, sodass ein verifiziertes Chart transitiv ein verifiziertes Image pinnt
- **MUSS** die Chart-`version` gleich der Release-Version und frei von `+`-Build-Metadata halten, die OCI-Tags nicht darstellen können (Helm schreibt `+` zu `_` um) [R6]
- **KANN** zusätzlich eine GPG-`.prov`-Datei für externe Konsumenten von `helm install --verify` ausliefern; einmal gewählt, wird sie dauerhaft, weil die Provenance-Layer den Manifest-Digest des Charts verändert

### E. Speicherung in GHCR

- **MUSS** die `sha256-<digest>`-Fallback-Index-Tags als tragende Artefakte behandeln: GHCR fehlt die Referrers-API, daher speichern Cosign, `actions/attest` und ORAS die Verknüpfung von Signatur und Subjekt in diesem client-gepflegten Tag (belegt durch die im §Kontext benannte Live-Probe; [R11])
- **MUSS** `sha256-*`-Tags, Multi-Arch-Kindmanifeste und jeden aus GitOps referenzierten Digest von jedem GHCR-Retention- oder Cleanup-Job ausnehmen; ein naives Aufräumen ungetaggter Versionen löscht Signaturen, Attestations und Plattform-Manifeste
- **MUSS** Registry-Schreibzugriffe in CI mit dem `GITHUB_TOKEN` des Workflows authentifizieren und jedes Package über das Label `org.opencontainers.image.source` mit seinem Repository verknüpfen, gemäß `spec/project/dockerfile-best-practices/`
- **MUSS** Nicht-Actions-Konsumenten (Cluster-Pull-Secrets, Argo-CD-Repository-Credentials, Dependabot) mit einem klassischen PAT mit Scope `read:packages` unter einem Maschinen-Account mit dokumentierter Rotationskadenz ausstatten; fine-grained PATs und GitHub-App-Installationstokens können sich Stand 2026-08 nicht an GHCR authentifizieren [R16]
- **SOLLTE** signierrelevante Release-Nachweise (die Digest-Zuordnung aus Image-Digest, Chart-Digest, Commit und Tag) als unveränderliches Release-Asset veröffentlichen, damit Audits nicht von der GHCR-Retention abhängen

### F. Verifikation bei der Promotion

- **MUSS** vor jeder GitOps-Änderung, die ein Release befördert, verifizieren: die Image-Signatur, die Chart-Signatur, die SBOM-Attestation und die Provenance-Attestation, jeweils gegen den gepinnten OIDC-Issuer `https://token.actions.githubusercontent.com` und ein verankertes Identitätsmuster für den Release-Workflow
- **MUSS** jeden regulären Ausdruck für Identitäten verankern (`^…$`, escapte Punkte); ein unverankertes Muster matcht auch das täuschend ähnliche Repository eines Angreifers
- **MUSS** die Provenance mit dem Plattform-Tooling verifizieren (`gh attestation verify` mit `--signer-workflow`, `--source-ref` und `--deny-self-hosted-runners`), weil die Prüfungen von Source-Ref und Signierer Zertifikats-Extensions auswerten, die der Workflow nicht fälschen kann [R4]
- **MUSS** die beförderte Chart-Version und den Image-Digest über einen reviewten Pull Request ins GitOps-Repository schreiben; der Review ist das menschliche Produktions-Gate

### G. Verifikation am Admission-Punkt

- **MUSS** die Image-Verifikation im Cluster mit einer CEL-basierten Kyverno-`ImageValidatingPolicy` durchsetzen; neue `verifyImages`-Regeln im `ClusterPolicy`-Stil **DÜRFEN NICHT** geschrieben werden, weil Kyverno sie mit angekündigter Entfernung in v1.20 als veraltet markiert hat [R9]
- **MUSS** zugelassene Images auf den Portfolio-Registry-Namespace beschränken und Images abweisen, deren Signatur nicht zum gepinnten Issuer und zur Release-Workflow-Identität passt, fail-closed (`failurePolicy: Fail`, Deny-Aktion), mit Ausnahmen nur für Cluster-Bootstrap-Namespaces
- **MUSS** Tags am Admission-Punkt zu Digests auflösen (`mutateDigest`) und digest-lose Referenzen abweisen (`verifyDigest`), damit ein zwischen Promotion und Pod-Erzeugung verschobener Tag keinen Inhalt tauschen kann
- **MUSS** für Produktions-Namespaces zusätzlich die SLSA-Provenance- und SBOM-Attestations verlangen und im Provenance-Predicate Source-Repository und Release-Ref-Muster gegen die Erwartungen prüfen
- **MUSS** beim Entzug von Vertrauen den Verifikations-Cache berücksichtigen: Ein gesperrter Digest oder eine verengte Identität greift erst nach Ablauf der Cache-TTL, die Incident-Response leert den Cache daher
- **SOLLTE** Kyverno-Background-Scans betreiben, damit bestehende Pods nach Policy-Änderungen in Reports neu bewertet werden, denn Admission allein blockiert laufende Workloads nie
- **KANN** stattdessen den Sigstore Policy Controller mit GitHubs Trust-Policies-Chart einsetzen, wenn ein Cluster ausschließlich GitHub Artifact Attestations durchsetzt [R10]; das Namespace-Opt-in-Modell und die hinterherhinkende App-Version des Helm-Charts sind die akzeptierten Kompromisse

### H. Rolle des GitOps-Deployments

- **MUSS** Argo CD als Deployment-Mechanismus behandeln, nicht als Verifier: Argo CD 3.5 verifiziert für Helm-/OCI-Quellen weder Chart- noch Image-Signaturen, und sein Source-Integrity-Feature deckt nur Git-GPG ab [R13]
- **MUSS** jedes `AppProject` auf den Portfolio-Registry-Namespace und das GitOps-Repository als Quellen beschränken, mit engen Destination-Listen
- **MUSS** Chart-Referenzen auf eine exakte Version pinnen — nie auf einen SemVer-Range — und **SOLLTE** auf digest-gepinnte Chart-Referenzen wechseln, sobald der native OCI-Quelltyp übernommen ist, was das Chart-Tag-Mutabilitätsfenster zwischen Promotion und Sync schließt
- **MUSS** Server-Side-Diff-Optionen (`ServerSideDiff=true,IncludeMutationWebhook=true`, `ServerSideApply=true`) an Applications setzen, die der Digest-Mutation unterliegen, damit Admission-Mutationen keinen dauerhaften Drift erzeugen [R9]

### I. Monitoring, Vorfalls-Eindämmung und Schlüssel

- **MUSS** das Transparenzlog auf die Signieridentitäten des Portfolios überwachen (`rekor-monitor` oder gleichwertig) und bei Signaturen alarmieren, die keinem erwarteten Release-Lauf entsprechen; Sigstores Sicherheitsmodell ist detektionsbasiert und bietet keine Revocation [R1]
- **MUSS** ein kompromittiertes Identitätsfenster per Policy eindämmen: die betroffenen Digests am Admission-Punkt sperren, die akzeptierte Identität verengen, neu bauen und neu releasen sowie die beteiligten Credentials rotieren — in dieser Reihenfolge
- **MUSS** die Verifikation während eines Sigstore-Ausfalls funktionsfähig halten: Signatur-Bundles tragen Inclusion Proof und Timestamp, und die Verifier halten einen gepinnten Trusted Root, sodass das Signieren stoppt, die Admission aber weiter verifiziert
- **MUSS** den Sigstore-Trusted-Root als versionierte Konfiguration mit wiederkehrender Update-Prüfung führen; ein veralteter Root lässt die Verifikation nach Upstream-Schlüsselrotationen irgendwann scheitern
- **KANN** einen offline verwahrten, hardware-gestützten Schlüssel als dokumentierten Break-Glass-Signierer für einen längeren Sigstore-Ausfall vorhalten; sein Einsatz erfordert einen Vorfallsnachweis, und er erscheint nie in CI

## Abnahmekriterien

- [ ] In keinem Portfolio-Workflow existiert ein `cosign.key`, ein key-basiertes Signier-Flag oder ein Signierschlüssel-Secret; jede Signatur verifiziert gegen den GitHub-OIDC-Issuer (fasst §A zusammen)
- [ ] Jeder Release-Image-Digest und Chart-Digest trägt eine verifizierbare Signatur, eine SLSA-Provenance-Attestation und (Images) eine SPDX-SBOM-Attestation, abrufbar aus GHCR (fasst §C, §D zusammen)
- [ ] `cosign verify` und `gh attestation verify` gelingen gegen ein Release-Artefakt allein mit gepinntem Issuer, verankerter Identität, Source-Ref- und Runner-Umgebungs-Constraints — und scheitern, sobald ein einzelner Constraint falsch ist (fasst §F zusammen)
- [ ] Ein absichtlich unsigniertes Test-Image im Portfolio-Registry-Namespace wird in jeder Umgebung von der Admission abgewiesen, und ein signiertes Image ohne Attestations wird in Produktion abgewiesen (fasst §G zusammen)
- [ ] Das erneute Pushen eines existierenden Release-Versions-Tags lässt die Pipeline vor jedem Registry-Schreibzugriff scheitern (§B)
- [ ] Die GHCR-Cleanup-Konfiguration nimmt `sha256-*`-Tags und Multi-Arch-Kindmanifeste nachweislich aus (§E)
- [ ] Die Quelllisten der Argo-CD-`AppProject`s enthalten nur den Portfolio-Registry-Namespace und das GitOps-Repository, und Chart-Referenzen sind exakte Versionen oder Digests (§H)
- [ ] Der Transparenzlog-Monitor läuft und hat in einer geprobten Übung mindestens einmal auf eine unerwartete Signatur alarmiert (§I)

## Referenzen

- Quellen abgerufen am 2026-08-19.
- `spec/project/continuous-delivery/`: die Auslieferungsdisziplin, deren §C-Provenance-Regel und §F-Securing-Stage-Matrix diese Spec für OCI-Artefakte konkretisiert
- `spec/project/github-actions-best-practices/`: Workflow-Härtung und §H-Plattform-Attestations, auf denen §A und §C aufbauen, ohne sie zu wiederholen
- `spec/project/dockerfile-best-practices/`: der Build-Artefakt-Vertrag, einschließlich des Labels `org.opencontainers.image.source`, auf das sich §E stützt
- `spec/project/kubernetes-deployment-best-practices/`: die Runtime-Regeln zu Digest-Pinning und Pull-Secrets, die §B und §E referenzieren
- `spec/project/release-automation/`: der Release-Übergang, der Signierung zum Non-Goal erklärt, hier aufgelöst
- [R1] Sigstore-Sicherheitsmodell (**Primary**): <https://docs.sigstore.dev/about/security/>
- [R2] Cosign-3.0-Release-Ankündigung — Bundle-Format und OCI-1.1-Referrer-Speicherung als Default, Legacy-Entfernung in v4 (**Primary**): <https://blog.sigstore.dev/cosign-3-0-available/>
- [R3] Fulcio-Zertifikats-Extensions (OID 1.3.6.1.4.1.57264.1.8–.24) (**Primary**): <https://github.com/sigstore/fulcio/blob/main/docs/oid-info.md>
- [R4] GitHub Docs: Artifact Attestations und der Reusable-Workflow-Pfad zu SLSA v1 Build L3 (**Primary**): <https://docs.github.com/en/actions/security-for-github-actions/using-artifact-attestations/using-artifact-attestations-and-reusable-workflows-to-achieve-slsa-v1-build-level-3>
- [R5] OCI Image Spec: Descriptor-Digests als Content-Identifier (**Primary**): <https://github.com/opencontainers/image-spec/blob/main/descriptor.md>
- [R6] Helm Docs: OCI-basierte Registries — Push-Ausgabe, Tag-Abbildung, Digest-Referenzen (**Primary**): <https://helm.sh/docs/topics/registries/>
- [R7] Sigstore Docs: Signieren weiterer Artefakttypen, einschließlich Helm Charts (**Primary**): <https://docs.sigstore.dev/cosign/signing/other_types/>
- [R8] Cosign-Issue zur Deprecation von `attach sbom` zugunsten von SBOM-Attestations (**Primary**): <https://github.com/sigstore/cosign/issues/2755>
- [R9] Kyverno-1.17-Ankündigung: Deprecation-Zeitplan für `ClusterPolicy` und CEL-Policy-Typen (**Primary**): <https://kyverno.io/blog/2026/02/02/announcing-kyverno-release-1.17/>
- [R10] GitHub Artifact-Attestations-Helm-Charts: die Policy-Controller-Trust-Policies-Alternative (**Primary**): <https://github.com/github/artifact-attestations-helm-charts>
- [R11] GitHub-Community-Diskussion: GHCR unterstützt die OCI-Referrers-API nicht (**Secondary**): <https://github.com/orgs/community/discussions/163029>
- [R12] GitHub-Community-Feature-Request zu GHCR-Tag-Immutabilität, Stand 2026-08 unbeantwortet (**Secondary**): <https://github.com/orgs/community/discussions/181783>
- [R13] Argo CD Docs: Source-Integrity-Verifikation ist ausschließlich Git-GPG, nicht Helm/OCI (**Primary**): <https://argo-cd.readthedocs.io/en/stable/user-guide/source-integrity/>
- [R14] Docker: Content-Trust-Abkündigung und Migrationsleitfaden, Abschaltung 2026-12-08 (**Primary**): <https://www.docker.com/blog/docker-content-trust-retirement-and-migration-guidance/>
- [R15] `helm-sigstore`-Maintainer-Issue, das den Projektstatus und den Rekor-`helm`-Eintragstyp infrage stellt (**Primary**): <https://github.com/sigstore/helm-sigstore/issues/426>
- [R16] GitHub Docs: GitHub Packages authentifiziert ausschließlich mit klassischen Personal Access Tokens (**Primary**): <https://docs.github.com/en/packages/learn-github-packages/about-permissions-for-github-packages>

## Offene Fragen

- Sind Portfolio-Repositories, die Artifact Attestations benötigen, jemals privat? GitHub Artifact Attestations für private Repositories erfordern GitHub Enterprise Cloud, und Signaturen der öffentlichen Instanz veröffentlichen die Repository-Identität im Transparenzlog — offen, weil die Antwort entscheidet, ob der Provenance-Mechanismus aus §C portfolio-weit gilt oder einen Cosign-only-Fallback braucht.
- Wann wird der native OCI-Quelltyp von Argo CD (Beta seit 3.1) der sanktionierte Chart-Referenzpfad? Offen, weil die digest-gepinnte Chart-Referenz aus §H davon abhängt und die Beta in diesem Portfolio noch nicht erprobt ist.
- Verifiziert die eingesetzte Kyverno-Version GitHub-Attestation-Bundles aus GHCR-Fallback-Tags in allen Attestor-Konfigurationen? Ein Crash-Report existiert für Key-/Zertifikats-Attestoren mit Transparenzlog-Prüfungen — offen, bis ein Proof of Concept in einem Staging-Cluster klärt, auf welche Predicate-Prüfungen sich die Produktions-Policy stützen kann.
- Benötigen externe Konsumenten `helm install --verify`? Offen, weil die optionale GPG-`.prov`-Layer aus §D eine Einbahnstraße ist: Sie später hinzuzufügen verändert veröffentlichte Chart-Digests.
