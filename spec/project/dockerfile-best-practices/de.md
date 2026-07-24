# Dockerfile-Best-Practices

Status: draft
Portfolio-Scope: local

## Kontext

Portfolio-Repositories, die Container-Images bauen, veröffentlichen sie in der GitHub Container Registry (GHCR). Diese Spec regelt, *was* ein `Dockerfile` enthalten muss, um **korrekt gelabelt**, **sicher** und **reproduzierbar** zu sein — unabhängig davon, *wie* das Image gebaut wird (ein einfaches `docker build`, BuildKit oder eine CI-Pipeline mit `docker/build-push-action`). Sie ist die dritte Schwester von `spec/project/kubernetes-deployment-best-practices/` (das das Laufzeit-Deployment regelt) und `spec/project/bjw-s-common-chart-deployment/` (das die Helm-Chart-Generierung regelt): Diese beiden besitzen die *Laufzeit*-Haltung, diese hier besitzt das *Build-Artefakt*.

Die zentrale Pflichtsäule ist ein **Container-Labelling-Vertrag**. GHCR nutzt das Label `org.opencontainers.image.source`, um ein veröffentlichtes Package mit seinem Quell-Repository zu verknüpfen und dessen Zugriff zu erben — ein Package ohne `source`-Label schwebt losgelöst von dem Code, der es erzeugt hat. Die übrigen vordefinierten OCI-Annotationen (`title`, `description`, `version`, `revision`, `created`, …) machen ein Image selbstbeschreibend und auditierbar: welcher Commit es gebaut hat, wann, und was es enthält. Die OCI-Image-Spec definiert jeden `org.opencontainers.image.*`-Schlüssel als *optional*; die Pflicht-/SOLLTE-Staffelung unten ist **die Policy dieser Spec**, aufgesetzt auf OCI für die Schlüsselnamen und -semantik und auf GitHub für das Source-Verknüpfungsverhalten — sie wird nie als OCI-Konformität dargestellt.

Jenseits der Labels sind die Defaults eines naiv geschriebenen `Dockerfile` die falsche Haltung für ein veröffentlichtes Image: Es läuft als Root, backt womöglich Build-Secrets in eine unveränderliche Schicht, schwebt auf einem veränderlichen `:latest`-Base-Tag und liefert seine gesamte Build-Toolchain mit. Diese Spec überführt die aktuelle autoritative Leitlinie — die offiziellen Docker-Build-Best-Practices, die OCI-Image-Spec-Annotationen, die GHCR-Labelling-Dokumentation, das hadolint-Regelwerk und den CIS Docker Benchmark — in eine normative Checkliste, die ein `dockerfile-audit`-Skill durchsetzt und an der ein Reviewer ein `Dockerfile` misst. Jede tragende Aussage dieser Spec wurde adversarial gegen diese Primärquellen verifiziert (siehe `Versions- und Tool-Anker`).

## Ziele

- Jedes veröffentlichte Image trägt die **verpflichtenden OCI-Kern-Labels** — `source`, `title`, `description`, `version`, `revision`, `created` —, sodass es mit seinem GHCR-Repository verknüpft, selbstbeschreibend und auf den Commit und Build zurückverfolgbar ist, der es erzeugt hat
- Der Label-Check ist **realistisch bei Build-Zeit-Werten**: Ein Label zählt als vorhanden, ob es ein statisches Literal, ein `ARG`-verdrahteter Wert oder von CI injiziert ist (`docker/metadata-action` / `docker build --label`), weil `version`/`revision`/`created` inhärent pro Build entstehen und ihr Hartkodieren ein Reproduzierbarkeits-Geruch ist
- Jedes Image ist **sicher by construction zur Build-Zeit**: ein nicht-root numerischer `USER`, keine Secrets in irgendeiner Schicht, ein Base-Image gepinnt per Tag **und** Digest, und ein `.dockerignore`, das den Build-Context (und versprengte Secrets) fernhält — die vier Build-Zeit-Härtungssäulen, an denen das Audit hart fehlschlägt
- Die **empfohlenen** Best-Practices (Multi-Stage-Builds, `COPY` statt `ADD`, Paketmanager-Hygiene, `HEALTHCHECK`, cache-freundliche Reihenfolge, robuste `RUN`-Shells) sind mit ihrer Begründung angegeben und, wo eine mechanische Prüfung existiert, auf die hadolint-Regel abgebildet, die sie verifiziert
- Die Spec **referenziert, statt zu duplizieren,** die Laufzeit-Security-Kontrollen, die `spec/project/kubernetes-deployment-best-practices/` besitzt: Die Aufgabe des `Dockerfile` ist es, sie *ermöglichbar* zu machen (nicht-root, keine Abhängigkeit von einem beschreibbaren Root-Dateisystem), nicht den SecurityContext zu wiederholen
- Die Spec ist der gemeinsame Maßstab über die image-bauenden Repositories des Portfolios, sodass ein Reviewer, der zwischen Repos wechselt, denselben Vertrag prüft und das `dockerfile-audit`-Skill dieselbe Haltung ausgibt

## Nicht-Ziele

- Der Image-**Publish**-Workflow selbst — Registry-Authentifizierung, `docker push`, Tag-Strategie und die `docker/build-push-action`-Verdrahtung —, der CI/CD-Konfiguration ist, per-Repository geregelt, nicht `Dockerfile`-Inhalt (diese Spec *kreditiert* nur CI-seitige Label-Injektion, sie schreibt die Pipeline nicht vor)
- **Laufzeit**-Container-Härtung — Capability-Dropping, `readOnlyRootFilesystem`, `runAsNonRoot`-Admission, seccomp/AppArmor, `no-new-privileges` —, die keine `Dockerfile`-Instruktionen sind und `spec/project/kubernetes-deployment-best-practices/` besitzt; diese Spec verlangt nur, dass der Build sie *erfüllbar* macht
- Anwendungs-Security (Input-Validierung, Authn/Authz, Dependency-CVEs), die den Code-Security- und Dependency-Audit-Specs gehört, nicht dem Image-Build
- Die vollständige `Dockerfile`-Instruktionsreferenz oder den kompletten OCI-Annotationskatalog zu wiederholen; diese Spec pinnt die tragenden Schlüssel und ihre Begründung und delegiert erschöpfende Referenzen nach upstream
- BuildKit-Provenance / SBOM-Attestations als *Labelling*-Mechanismus: Sie sind eine separate in-toto-Manifest-Fläche und **DÜRFEN NICHT** zur OCI-Label-Präsenz zählen (ein Image darf sie trotzdem tragen, aber eine Label-Anforderung wird durch ein Label erfüllt, nicht durch eine Attestation)

## Anforderungen

### OCI-Image-Labels (Pflichtsäule)

- Jedes veröffentlichte Image **MUSS** die OCI-Kern-Annotationen `org.opencontainers.image.source`, `.title`, `.description`, `.version`, `.revision` und `.created` tragen; ihr Fehlen ist ein harter Fehlschlag. Schlüsselnamen und -semantik sind OCIs, die Pflicht-Staffelung ist die Policy dieser Spec, und `source` trägt zusätzlich GHCR-spezifisches Verhalten (unten)
- `org.opencontainers.image.source` **MUSS** auf die Quell-Repository-URL (`https://github.com/<owner>/<repo>`) gesetzt sein, weil GHCR genau dieses Label nutzt, um das veröffentlichte Package mit seinem Repository zu verbinden und dessen Zugriff zu erben; ein Image ohne es ist nicht mit seinem Code verknüpft
- Ein Label **MUSS** als *vorhanden* gezählt werden, wenn sein Wert eines der folgenden ist: (a) ein statisches String-Literal; (b) eine `ARG`-verdrahtete Substitution (`ARG VERSION` + `LABEL org.opencontainers.image.version="$VERSION"`), deren `ARG` in derselben Stage deklariert ist; oder (c) von CI injiziert via `docker/metadata-action` → `docker/build-push-action` oder `docker build --label`/`--annotation`, erkennbar in den Workflow-Dateien des Repositories. Das Audit **DARF NICHT** ein Pflicht-Label hart fehlschlagen lassen, das im `Dockerfile` fehlt, aber nachweislich von CI injiziert wird; es schlägt nur fehl, wenn das Label an keiner der beiden Stellen vorhanden ist
- `org.opencontainers.image.version`, `.revision` und `.created` **SOLLTEN** `ARG`-verdrahtet oder CI-injiziert sein statt hartkodierter Literale: `.created` ist ein RFC-3339-Zeitstempel pro Build, `.revision` ist die Quellcode-Commit-SHA und `.version` ist die veröffentlichte Version — ein committetes Literal für eines davon ist beim nächsten Build veraltet und wird als Reproduzierbarkeits-Geruch markiert, nicht als harter Fehlschlag
- In einem **Multi-Stage**-Build **MUSS** das Audit die Pflicht-Labels nur gegen die **finale (veröffentlichende) Stage** auswerten: Ein `LABEL`, das nur über `COPY --from=`/`RUN --mount=from=` erreichbar ist, wird aus dem Output-Image verworfen und ist ein False Positive; ein Label in der finalen Stage (oder vom finalen `FROM`-Base geerbt) ist das einzige, das mitgeliefert wird
- Ein Image **SOLLTE** außerdem `org.opencontainers.image.licenses` (eine SPDX-Lizenz-Expression), `.url` und `.documentation` setzen, wo bekannt. GHCR zeigt `description` und `licenses` auf der Package-Seite an **für ein Single-Manifest-Image**, gelesen aus den Config-Layer-Labels; für einen **Image-Index** (Multi-Arch, *oder* jeder Build, der eine standardmäßige BuildKit-Provenance-/SBOM-Attestation trägt) schlägt dies fehl, sofern die Werte nicht zusätzlich als Index-Level-*Annotationen* vorhanden sind (siehe die nächste Regel), und ein Label-only-Index-Image zeigt „No description provided"
- Für ein Image, das via **BuildKit / `docker/build-push-action`** in GHCR veröffentlicht wird, **MÜSSEN** die OCI-Kernwerte als **Index-Level-Annotationen** propagiert werden, nicht nur als Config-`LABEL`s. `docker/build-push-action@v7` hängt **standardmäßig** eine Provenance-Attestation an, sodass *jeder* Push — auch bei nur einer Plattform — ein OCI-**Image-Index** ist (auf der Package-Seite als „OS/Arch 2" dargestellt), und für einen Index sind es die Index-Annotationen, nicht die Config-Labels eines Kind-Manifests, die die GHCR-Package-Seite speisen. Die Annotationen über den `annotations:`-Input von `docker/metadata-action` mit der Umgebungsvariable `DOCKER_METADATA_ANNOTATIONS_LEVELS` inklusive `index` (zum Beispiel `manifest,index`) verdrahten und die berechneten Annotationen an den `annotations:`-Input von `build-push-action` durchreichen. Der Config-`LABEL`-Vertrag (oben) bleibt als Single-Manifest-/`docker inspect`-Baseline **erhalten** — diese Annotation-Anforderung ist *additiv* für den GHCR-/Index-Fall, sie ersetzt oder schwächt die Label-Regel nicht. Die Referenz-Verdrahtung:

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

- Ein Image **SOLLTE** `org.opencontainers.image.base.name` (die voll-qualifizierte Base-Referenz, keine angenommene Default-Registry) und `.base.digest` (`sha256:…`) festhalten; diese **MÜSSEN** explizit geschrieben werden, weil Docker/BuildKit sie heute nicht auto-befüllt (anders als Podman/Buildah)
- BuildKit-Provenance und SBOM-Attestations **DÜRFEN NICHT** anstelle der Pflicht-Labels akzeptiert werden: Sie sind separate in-toto-Manifeste, und eine Base-Image-Identität, die nur in der Provenance überlebt, erfüllt die `base.*`-Label-SOLLTE nicht

### Nicht-Root-User (Pflichtsäule)

- Die finale Stage **MUSS** mit einer `USER`-Instruktion enden, die vor `CMD`/`ENTRYPOINT` auf einen dedizierten **nicht-root**-User wechselt; ein finales Image, dessen effektiver User root ist (ob durch ein explizites `USER 0`/`root` oder dadurch, dass nie ein `USER` gesetzt wird), ist ein harter Fehlschlag. Man beachte, dass hadolint `DL3002` nur ein *letztes* `USER` von root markiert und **nicht** ein Image markiert, das nie ein `USER` setzt, weshalb das Audit **MUSS** zusätzlich prüfen, dass eine `USER`-Instruktion existiert
- Der `USER` **MUSS** als **numerische UID** ausgedrückt werden (zum Beispiel `USER 10001:10001`), nicht als Name, sodass ein Kubernetes-`runAsNonRoot: true`-Admission-Check nicht-root verifizieren kann, ohne `/etc/passwd` aufzulösen; der User und seine primäre Gruppe **SOLLTEN** explizit angelegt werden (ein User ohne primäre Gruppe läuft in der root-Gruppe)
- Das Image **SOLLTE** eine beliebig injizierte UID in Gruppe 0 tolerieren (das OpenShift-Random-UID-Modell): nur in gruppe-0-beschreibbare Pfade oder gemountete Volumes/tmpfs schreiben, und **DARF NICHT** hart davon abhängen, dass eine spezifische UID einen Pfad besitzt

### Secrets außerhalb der Layer (Pflichtsäule)

- Ein `Dockerfile` **DARF NICHT** Secrets in irgendeine Image-Schicht einbringen: Es **DARF NICHT** ein Secret über `ARG` oder `ENV` übergeben (beide persistieren im Image und sind in `docker history` sichtbar) und **DARF NICHT** eine Secret-Datei ins Image `COPY`en (ein späteres `rm` verbirgt nur die Bytes in einer früheren Schicht — sie bleiben wiederherstellbar)
- Ein Build, der ein Build-Zeit-Credential braucht, **MUSS** einen BuildKit-Secret-Mount nutzen (`RUN --mount=type=secret,id=<id>`, der das Secret nur für diese Instruktion unter `/run/secrets/<id>` bereitstellt) und/oder einen Multi-Stage-Split, der das Credential aus der finalen Stage heraushält
- Diese Säule ergänzt `.dockerignore` (unten) als doppelten Boden: Weil der gesamte Build-Context an den Daemon gesendet wird, kann eine ignorierte Secret-Datei nicht in ein breites `COPY .` gefegt werden

### Base-Image-Pinning (Pflichtsäule)

- Jedes `FROM` **MUSS** sein Base-Image zusätzlich zum Tag per **Digest** pinnen: `FROM registry/image:tag@sha256:<digest>` (der Tag bleibt für Lesbarkeit, der Digest garantiert Unveränderlichkeit); ein `FROM`, das auf `:latest`, auf einem ungetaggten Image oder auf einem Tag ohne Digest schwebt, ist ein harter Fehlschlag. hadolint `DL3006` (muss getaggt sein) und `DL3007` (darf nicht `:latest` sein) decken die Tag-Hälfte ab; die Digest-Hälfte prüft diese Spec direkt
- Ein digest-gepinnter Base **MUSS** mit einem automatisierten Updater gepaart werden (Renovates `docker.pinDigests`-Manager oder Docker Scout), sodass Pins gepatcht bleiben statt still zu altern; ein Digest-Pin ohne Updater ist ein Stale-Base-Risiko, kein Set-and-Forget-Gewinn
- Das Base-Image **SOLLTE** minimal und aus einer vertrauenswürdigen Quelle sein (ein Official Image, ein Verified Publisher oder eine distroless/slim-Variante), sodass `runAsNonRoot` erfüllbar und die Angriffsfläche klein ist

### `.dockerignore` vorhanden (Pflichtsäule)

- Der Build-Context **MUSS** eine `.dockerignore`-Datei mitliefern; ihr Fehlen ist ein harter Fehlschlag. Dockers erklärte Begründung ist Build-Context-Größe und Build-Geschwindigkeit (besonders für Remote-Builder); der Secret-Ausschluss-Nutzen — eine ignorierte Datei kann nicht von einem breiten `COPY .` erfasst werden — ist ein realer, aber *sekundärer, abgeleiteter* Nutzen und wird Docker nicht als sein zentraler Zweck zugeschrieben
- Die `.dockerignore` **SOLLTE** mindestens `.git`, `.env` und Credential-/Key-Dateien ausschließen und verstärkt so die Keine-Secrets-in-Layern-Säule

### Empfehlung: Build-Korrektheit und Image-Schlankheit

- Ein `Dockerfile` **SOLLTE** einen **Multi-Stage**-Build nutzen, sodass das finale Image nur Laufzeit-Artefakte liefert und nicht die Build-Toolchain, Compiler oder Debugger, was sowohl Größe als auch Angriffsfläche senkt
- Ein `Dockerfile` **SOLLTE** `COPY` gegenüber `ADD` bevorzugen und `ADD` nur für seine zwei legitimen Aufgaben greifen — einen Remote-HTTPS/Git-URL-Fetch oder eine lokale Tar-Auto-Extraktion; `ADD` als schlichtes Kopieren verwendet wird markiert (hadolint `DL3020` gegenüber der `DL3010`-Archiv-Ausnahme). Es **DARF NICHT** als pauschales Verbot von `ADD` gelesen werden
- Paketmanager-Nutzung **SOLLTE** hygienisch sein: `apt-get install -y --no-install-recommends` (`DL3015`, `DL3014`), der Cache in derselben Schicht bereinigt (`rm -rf /var/lib/apt/lists/*`, `DL3009`; `apk add --no-cache`), `apt-get` statt `apt` (`DL3027`) und Paketversionen gepinnt (`DL3008`/`DL3013`/`DL3016`/`DL3018`/… je Ökosystem)
- `apt-get update` und `apt-get install` **SOLLTEN** in einem einzigen `RUN` laufen (eine gecachte einzelne `update`-Schicht führt zu veralteten Installs); es gibt dafür keine dedizierte hadolint-Regel, weshalb es prosa- oder custom-geprüft wird, mit `DL3059` (aufeinanderfolgende `RUN` konsolidieren) als nächstem Näherungswert
- Ein `Dockerfile` **SOLLTE** Instruktionen von am-seltensten- zu am-häufigsten-ändernd ordnen (Dependencies installieren, bevor Anwendungs-Source kopiert wird, `COPY .` spät), sodass die Dependency-Schicht Source-Änderungen im Build-Cache überlebt; und **SOLLTE** ein In-Image-`apt-get upgrade`/`dist-upgrade` vermeiden (nicht-reproduzierbare Drift; stattdessen auf einem frischen gepinnten Base neu bauen, ein Muster, das hadolint weiterhin via `DL3005` für apt, `DL3017` für apk und `DL3031` für yum meldet)
- Ein Image mit langlaufendem Server **SOLLTE** einen `HEALTHCHECK` deklarieren (`DL3057` standardmäßig aus; `DL3012` markiert ein Duplikat); dies ist empfohlen, weil Kubernetes den `Dockerfile`-`HEALTHCHECK` **ignoriert** — die Liveness-/Readiness-/Startup-Probes des Orchestrators (im k8s-Schwester-Spec) sind zur Laufzeit das autoritative Gate
- Ein `RUN` mit Pipe **SOLLTE** `pipefail` setzen (`SHELL ["/bin/sh","-o","pipefail","-c"]` oder ein inline `set -o pipefail &&`, `DL4006`), `CMD`/`ENTRYPOINT` **SOLLTEN** die JSON-/Exec-Form für korrektes Signal-Handling nutzen (`DL3025`), und `WORKDIR` **SOLLTE** absolut sein (`DL3000`, mit `DL3003`, das `RUN cd` markiert)
- Ein Repository **KANN** `FROM` auf eine erlaubte Registry-Menge beschränken (`DL3026`), um seine Supply-Chain zu pinnen

### Runtime-Kontrollen (außerhalb des Scopes — Querverweis)

- Das `Dockerfile` **DARF NICHT** als der Ort behandelt werden, an dem Laufzeit-Security ausgedrückt wird: Capability-Dropping, `readOnlyRootFilesystem`, `allowPrivilegeEscalation: false`/`no-new-privileges`, seccomp/AppArmor und `runAsNonRoot`-Admission sind **keine** `Dockerfile`-Instruktionen und gehören `spec/project/kubernetes-deployment-best-practices/`
- Die Pflicht des `Dockerfile` ist es, diese Laufzeit-Kontrollen **erfüllbar** zu machen: einen nicht-root numerischen `USER` mitliefern (sodass `runAsNonRoot` erfüllbar ist), keine Abhängigkeit vom Schreiben ins Image-Dateisystem zur Laufzeit (beschreibbare Pfade als `VOLUME` deklarieren oder ein gemountetes `emptyDir` erwarten, sodass `readOnlyRootFilesystem` erfüllbar ist) und kein setuid/Privilege-Escalation verlangen. Dieser Split ist durch NIST SP 800-190 Least-Privilege gerahmt

### Versions- und Tool-Anker

- Der normative Inhalt der Spec **MUSS** gegen diese gepinnten Quellen gelesen werden, aktuell zum 2026-07-10: die OCI-Image-Spec `annotations.md` (14 vordefinierte `org.opencontainers.image.*`-Schlüssel, alle OPTIONAL); die Docker-Build-Best-Practices-Dokumentation (`docs.docker.com/build/building/best-practices`); die GHCR-Container-Labelling-Dokumentation; der CIS Docker Benchmark **v1.7** (Kontrollen 4.1 Nicht-Root-User, 4.6 `HEALTHCHECK`, 4.7 einzelnes `RUN` update+install); und NIST SP 800-190 für die Build-/Laufzeit-Least-Privilege-Rahmung
- Eine `dockerfile-audit`-Implementierung **MUSS** eine spezifische **hadolint**-Version pinnen, weil hadolints Regelwerk über Releases hinweg driftet (Regeln werden hinzugefügt, deprecatet, und ihre Defaults ändern sich zwischen Versionen, sodass eine gepinnte Version die Regel-Abdeckung reproduzierbar hält); sie **SOLLTE** anmerken, dass hadolints Default-`--failure-threshold` `info` ist, sodass Info-Level-Findings einen Default-Lauf bereits fehlschlagen lassen, und sie **KANN** Warning-/Info-pflichtnahe-Regeln via `.hadolint.yaml`-Override auf `error` anheben
- Build-Zeit-Label-Verdrahtung **SOLLTE** dem `docker/metadata-action`-Modell folgen (es leitet `title`, `description`, `url`, `source`, `version`, `created`, `revision`, `licenses` aus dem Git-/GitHub-Kontext ab; `version` ist der erste berechnete Tag, `revision` die Commit-SHA), sodass ein Repository die Werte-pro-Build nicht von Hand pflegen muss
- Das **Annotations-on-Index**-Verhalten ist eine tragende Aussage, gepinnt an die GHCR-Container-Registry-Dokumentation: GHCR liest die `description` eines Multi-Arch-/Index-Images (und die auf der Package-Seite dargestellten Metadaten) aus dem `annotations`-Feld des Manifest-Index, während der Config-`LABEL`-Weg Metadaten nur für den Single-Manifest-Fall („most images") darstellt; GitHubs eigener Package-Seiten-Hinweis besagt, `org.opencontainers.image.description` für Multi-Arch-Images im Annotations-Feld zu setzen. `nolte/kamerplanter#455` ist die Referenz-Implementierung, die Index-Annotationen über alle Image-Build-Jobs anwendet

## Akzeptanzkriterien

- [ ] `spec/project/dockerfile-best-practices/` existiert mit `en.md` (kanonisch) und `de.md` (Übersetzung) und ist in `spec/README.md` gelistet
- [ ] Der OCI-Label-Vertrag ist ein Pflicht-Abschnitt: Die sechs Kern-Schlüssel (`source`, `title`, `description`, `version`, `revision`, `created`) sind mit RFC-2119-Keywords verpflichtend, die fünf SOLLTE-Schlüssel gelistet, und `source` an die GHCR-Repository-Verknüpfung gebunden
- [ ] Die Label-**Präsenzregel** ist formuliert: statisches Literal ODER `ARG`-verdrahtet ODER CI-injiziert (`docker/metadata-action`/`--label`) zählen alle, und das Audit schlägt nur hart fehl, wenn ein Label weder im `Dockerfile` noch in CI vorhanden ist
- [ ] Die **Multi-Stage-finale-Stage**-Regel für Labels ist formuliert: Ein `LABEL`, das nur über `COPY --from=` erreichbar ist, ist ein False Positive
- [ ] Die **Annotation-on-Index**-Regel ist formuliert: Für ein via BuildKit/`docker/build-push-action` in GHCR veröffentlichtes Image MÜSSEN die OCI-Kernwerte als Index-Level-Annotationen propagiert werden (`DOCKER_METADATA_ANNOTATIONS_LEVELS` inkl. `index`, durchgereicht an `build-push-action` `annotations:`), mit dem Config-`LABEL`-Vertrag als erhaltener Single-Manifest-Baseline, und die kanonische Referenz-Verdrahtung ist enthalten
- [ ] Die vier Pflicht-Nicht-Label-Säulen sind je mit RFC-2119-Keywords und Begründung formuliert: nicht-root **numerischer** `USER` (plus die „ein `USER` muss existieren"-Prüfung jenseits von `DL3002`), keine Secrets in Layern (mit dem BuildKit-Secret-Mount-Remedy), Base-Image gepinnt per **Tag + Digest** (plus dem verlangten Updater) und `.dockerignore` vorhanden
- [ ] Die empfohlenen Best-Practices (Multi-Stage, `COPY` statt `ADD`, Paket-Hygiene, einzelnes `RUN` update+install, Cache-Reihenfolge, kein `apt-get upgrade`, `HEALTHCHECK`, `pipefail`, Exec-Form-`CMD`, absolutes `WORKDIR`, Registry-Allow-List) sind je mit ihrer Begründung und, wo eine existiert, der hadolint-Regel-ID formuliert, die sie prüft
- [ ] Laufzeit-Kontrollen sind explizit an `spec/project/kubernetes-deployment-best-practices/` delegiert, mit den Erfüllbarkeits-Pflichten des `Dockerfile` (nicht-root `USER`, keine Writable-Rootfs-Abhängigkeit) formuliert
- [ ] Die Versions-/Tool-Anker sind gepinnt: OCI-Image-Spec, Docker-Best-Practices, GHCR-Docs, CIS Docker Benchmark v1.7, NIST SP 800-190, eine gepinnte hadolint-Version mit ihrer `info`-Failure-Threshold-Anmerkung und das `docker/metadata-action`-Label-Verdrahtungsmodell
- [ ] Ein Reviewer (oder das künftige `dockerfile-audit`-Skill) kann ein reales `Dockerfile` gegen diese Checkliste halten und jede Anforderung als erledigt oder nicht erledigt markieren

## Offene Fragen

- **Portfolio-Scope-Promotion.** Soll diese Spec `local` bleiben oder auf `portfolio` promoted werden, sodass die image-bauenden Repositories des Portfolios den Labelling-und-Härtungs-Maßstab per Referenz erben gemäß `spec/project/portfolio-inherited-spec-layer/`? Promotion ist ein expliziter Maintainer-Akt und wird hier aufgeschoben.
- **`apply`-Merge-Semantik.** Wenn die künftige `dockerfile-audit apply`-Operation ein `Dockerfile` patcht, das bereits einen partiellen oder fehlerhaften `LABEL`-Block hat, soll sie die fehlenden Schlüssel in den bestehenden Finale-Stage-Block mergen (letzter Schlüssel gewinnt, custom Labels erhalten) oder einen neuen Block anhängen? Die Recherche empfiehlt Merge; der genaue Algorithmus wird beim Authoring des Skills festgelegt.
- **Monorepo-Dockerfile-Discovery.** Was ist der Discovery-Glob für ein Repository mit mehreren Images (`Dockerfile`, `*.Dockerfile`, `docker/*/Dockerfile`, per-Service-Verzeichnisse)? Jedes liefert sein eigenes Image mit seinen eigenen Pflicht-Labels; das Audit sollte jedes unabhängig auswerten, und nicht-veröffentlichte/Test-`Dockerfile`s brauchen womöglich einen Opt-out-Marker.
- **Digest-Pin-Strenge.** Ist die Digest-Hälfte des Base-Image-Pinnings ein hartes `MUSS` für jedes Repository ab Tag eins, oder ein `MUSS`, das am Vorhandensein des Digest-Updaters (Renovate/Scout) gated ist, um keine Pins vorzuschreiben, die ein Repo nicht frisch halten kann? Aktuell als `MUSS` + verlangter Updater geschrieben.
- **Nicht-mechanisierbare Säulen.** Für die Säulen ohne hadolint-Regel (einzelnes `RUN` update+install, Secret-in-Layer-Erkennung) — soll das `dockerfile-audit`-Skill einen ergänzenden Custom-Linter (grep / conftest-OPA) mitliefern, oder ist Prosa-Review akzeptabel?

## Quellen

Die externen Versions- und Tool-Anker oben sind Author-Time-externe Aussagen, trianguliert gemäß `spec/claude/research-triangulate/` §"Author-time assertions" (Author-Time-Stufe: mindestens drei unabhängige Quellen, Primary-first geordnet). Abrufdatum für jede Quelle unten: 2026-07-24.

- **Vordefinierte `org.opencontainers.image.*`-Annotation-Schlüssel der OCI-Image-Spec (alle OPTIONAL)**: OpenContainers-image-spec `annotations.md` auf `main` (Primary), `https://github.com/opencontainers/image-spec/blob/main/annotations.md`; die gerenderte OpenContainers-Annotations-Spec (Primary), `https://specs.opencontainers.org/image-spec/annotations/`; Snyk, „How and when to use Docker labels / OCI container annotations" (Secondary), `https://snyk.io/blog/how-and-when-to-use-docker-labels-oci-container-annotations/`
- **CIS Docker Benchmark v1.7 Kontrollen (4.1 Nicht-Root-User, 4.6 `HEALTHCHECK`, 4.7 einzelnes `RUN` update+install)**: CIS Docker Benchmark v1.7 (Primary), `https://rayasec.com/wp-content/uploads/CIS-Benchmark/Docker/CIS_Docker_Benchmark_v1.7_PDF.pdf`; die `dev-sec/cis-docker-benchmark`-Control-Implementierung für Container-Images (Secondary), `https://github.com/dev-sec/cis-docker-benchmark/blob/master/controls/container_images.rb`; OneUptime, „How to Audit Docker with CIS Benchmarks" (Secondary), `https://oneuptime.com/blog/post/2026-01-16-docker-cis-benchmarks/view`
- **hadolint-Default-`--failure-threshold` ist `info`**: hadolint-README (Primary), `https://github.com/hadolint/hadolint`; hadolint-Man-Page 2.14.0 auf ManKier (Secondary), `https://www.mankier.com/1/hadolint`; hadolint-Man-Page auf Linux Command Library (Secondary), `https://linuxcommandlibrary.com/man/hadolint`
- **hadolint-Regelsatz-Drift (Regeln wie `DL3005`/`DL3017`/`DL3031` bestehen fort und feuern weiterhin; der Regelsatz ändert sich über Releases, sodass eine gepinnte Version erforderlich ist)**: hadolint-Wiki-Seite für `DL3031` (Primary), `https://github.com/hadolint/hadolint/wiki/DL3031`; hadolint-Wiki-Seite für `DL3017` (Primary), `https://github.com/hadolint/hadolint/wiki/DL3017`; hadolint-Issue #1049, das bestätigt, dass `DL3005` weiterhin feuert (Primary), `https://github.com/hadolint/hadolint/issues/1049`. Ein früherer Entwurf behauptete, diese drei Regeln seien „entfernt worden"; das ist falsch (die Wiki-Seiten sind live und die Regeln feuern weiterhin) und wurde oben korrigiert.
- **`docker/metadata-action` leitet OCI-Labels aus dem Git/GitHub-Kontext ab (`version` ist der erste berechnete Tag, `revision` die Commit-SHA)**: `docker/metadata-action`-README (Primary), `https://github.com/docker/metadata-action`; Snyk, „How and when to use Docker labels / OCI container annotations" (Secondary), `https://snyk.io/blog/how-and-when-to-use-docker-labels-oci-container-annotations/`; Renovate-Dokumentation, Docker-Datasource (source/revision-Labels) (Secondary), `https://docs.renovatebot.com/modules/datasource/docker/`
- **NIST SP 800-190 Least-Privilege-Build/Runtime-Rahmung**: NIST SP 800-190 Application Container Security Guide (Primary), `https://nvlpubs.nist.gov/nistpubs/specialpublications/nist.sp.800-190.pdf`; Red Hat, „Guide to NIST SP 800-190 compliance" (Secondary), `https://www.redhat.com/en/resources/guide-nist-compliance-container-environments-detail`; Anchore, „NIST SP 800-190 Overview & Compliance Checklist" (Secondary), `https://anchore.com/compliance/nist/800-190/`
- **GHCR liest die Beschreibung eines Multi-Arch-/Index-Images aus dem `annotations`-Feld des Manifest-Index (nicht aus einem Config-`LABEL`)**: GitHub Docs, „Working with the Container registry" (Primary), `https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry`; Docker Docs, „Annotations" (Index-Level-Annotationen) (Secondary), `https://docs.docker.com/build/metadata/annotations/`; `docker/build-push-action`-Discussion #1022 zum Setzen von Multi-Arch-Index-Annotationen (Secondary), `https://github.com/docker/build-push-action/discussions/1022`
