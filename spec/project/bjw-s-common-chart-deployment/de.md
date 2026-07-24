# bjw-s-Common-Chart-Deployment

Status: draft
Portfolio-Scope: local

## Kontext

Mehrere selbst gehostete Anwendungen im Portfolio (zum Beispiel `kamerplanter`) sind Eigenentwicklungen und brauchen ein Kubernetes-Deployment. Statt pro Anwendung Deployment-, Service-, Ingress-, PVC-, ConfigMap- und Secret-Manifeste von Hand zu schreiben, standardisiert das Portfolio auf das [bjw-s-labs-`common`-Library-Chart](https://github.com/bjw-s-labs/helm-charts/tree/main/charts/library/common) als Fundament. `common` ist ein Helm-**Library**-Chart (nicht eigenständig installierbar): Ein Consumer deklariert es als `Chart.yaml`-Abhängigkeit und beschreibt den gesamten Workload deklarativ unter einem einheitlichen Values-Schema (`controllers`, `containers`, `service`, `ingress`, `persistence`, `configMaps`, `secrets`, `serviceAccount`, `rbac`, …). Der Loader der Library (`bjw-s.common.loader.init` → `bjw-s.common.loader.generate`) rendert dann jedes Kubernetes-Objekt in einer deterministischen, abhängigkeitsbewussten Reihenfolge (PVCs, ServiceAccounts und ConfigMaps vor den Controllern, die sie referenzieren, Networking zuletzt) und validiert die Values gegen ein mitgeliefertes `values.schema.json`.

Ein solches Chart von Hand zu schreiben ist repetitiv und fehleranfällig: ein unvollständiger Container-Block (fehlende Probes, Resources oder ein `env`-Schlüssel, den die App liest), ein Service-Port, den kein Ingress und keine Probe referenziert, ein Persistence-Volume, das am falschen Pfad gemountet ist, oder ein im Klartext verdrahtetes Secret — all das ist leicht falsch zu machen und fällt erst zur Install- oder Laufzeit auf. Die manuellen, cluster-spezifischen Eingaben, die eine betreibende Person weiterhin liefern muss (Image-Tag, Ingress-Host, Storage-Class, Secret-Material), leben zudem oft nur im Kopf einer wartenden Person.

Diese Spec definiert den Vertrag für das **Generieren eines vollständigen, korrekten, schemavaliden Application-Charts auf Basis der `common`-Library** für eine selbst gehostete Portfolio-Anwendung und für das **Festhalten jedes irreduziblen manuellen Schritts in der README dieses Charts**. Sie ist die Grundlage für einen späteren Engineering-Agenten, der eine Anwendung (ihr Image, ihre Laufzeit-Konfigurationsfläche, ihre Exposition-Bedürfnisse) entgegennimmt und das Chart ausgibt. Die Spec pinnt die Upstream-Library als ihren normativen Anker und delegiert die vollständige Referenz der Library an die Upstream-Dokumentation, statt sie erneut aufzuschreiben — dieselbe Delegations-Disziplin, die `spec/project/taskfile/` auf `nolte/taskfiles` anwendet.

## Ziele

- Eine selbst gehostete Portfolio-Anwendung erhält ein auf der `common`-Library aufgebautes Deployment-Chart, dessen Values **vollständig** sind (jede Laufzeit-Eingabe, die der Container braucht, ist deklariert) und **schemavalide** (sie bestehen das mitgelieferte `values.schema.json` der Library), sodass `helm install` ohne versteckte Lücken einen laufenden Workload erzeugt
- Das generierte Chart ist **lauffähig, kein Stub**: Es rendert mit `helm template`/`helm lint` bei der minimalen Kubernetes-Version der Library fehlerfrei, bevor es als fertig gilt
- Der Container-Vertrag ist vollständig und korrekt konfiguriert: Image mit explizitem Tag, `env`/`envFrom`, Health-Probes, Resource-Requests und ein gehärteter Security-Context — kein ungebundener, ungeprüfter, mit `latest` getaggter Container
- Jede Aktion, die das Chart **nicht** selbst ausführen kann (Image-Tag, Secret-Material, Ingress-Host, Storage-Class, Dependency-Build, First-Run-Bootstrap), ist in der README des generierten Charts als handlungsleitender manueller Schritt aufgeführt, der *was* zu setzen ist, *wo* und *warum* benennt
- Über das Portfolio generierte Charts teilen dieselbe Form — ein loader-getriebener `templates`-Einstiegspunkt, dieselben Value-Sektionen, dieselbe README-Struktur — sodass eine reviewende Person beim Wechsel zwischen Apps ein vertrautes Layout liest
- Die Upstream-`common`-Version ist gepinnt und wird nachverfolgt, und die vollständige Upstream-Referenz ist verlinkt, nicht dupliziert, sodass es eine einzige Quelle der Wahrheit für das Verhalten der Library gibt

## Nicht-Ziele

- Die Definition der Business-Logik der Anwendung, ihres `Dockerfile` oder wie ihr Container-Image gebaut und veröffentlicht wird — die Image-Koordinaten sind eine **Eingabe** der Chart-Generierung, kein Ergebnis
- Die Wahl, ob überhaupt die `common`-Library statt eines anderen Chart-Ansatzes verwendet wird — diese Spec setzt voraus, dass `common` als Fundament gewählt wurde; sie regelt, wie man es gut verwendet
- Die Regelung des cluster-seitigen Deployment-Mechanismus (ein GitOps-Controller, `helm install` in CI und Ähnliches) — diese Spec endet an der **Chart-Grenze**; die Verdrahtung des Charts in eine Delivery-Pipeline liegt außerhalb des Scopes
- Die Vorgabe des Secret-Management-Backends (Sealed Secrets, SOPS, External Secrets Operator) — diese Spec fordert nur, dass Secret-Material **nie** im Klartext committet wird und dass das Chart dokumentiert, wie die betreibende Person es liefert; welches Backend, ist eine Entscheidung pro Repository
- Das erneute Aufschreiben der vollständigen Values-Referenz der `common`-Library, ihrer Template-Interna oder ihres Schemas pro Schlüssel — das generierte Chart und der Agent lesen das Upstream-`values.yaml`/`values.schema.json` zur Generierungszeit; diese Spec verlinkt Upstream und regelt nur das darauf aufbauende Consumer-Chart
- Die Nutzung des `app-template`-Charts als schrumpfverpackte Installation (`helm install app-template -f values.yaml`) — diese Spec zielt auf ein **dediziertes, versioniertes Consumer-Chart**, das im Repository der Anwendung eingecheckt ist; `app-template` wird nur als Alternative für Wegwerf-Fälle erwähnt

## Anforderungen

### Upstream-Anker und Versionierung

- Ein generiertes Chart **MUSS** `common` als `Chart.yaml`-Abhängigkeit mit einer expliziten, gepinnten Version und dem kanonischen Repository deklarieren, niemals mit einer schwebenden oder fehlenden Version:

  ```yaml
  dependencies:
    - name: common
      version: 5.0.1   # gepinnt; bewusst angehoben, per Renovate nachverfolgt
      repository: https://bjw-s-labs.github.io/helm-charts/
  ```

- Das Chart **MUSS** `kubeVersion` in `Chart.yaml` auf die deklarierte Untergrenze der Library (`>=1.31.0-0` für `common` 5.0.x; die 4.x-Linie deklarierte `>=1.28.0-0`) oder höher setzen, sodass eine Installation gegen einen älteren Cluster früh scheitert, statt ein inkompatibles Objekt zu rendern. Die Untergrenze **MUSS** der gepinnten `common`-Version folgen, weil die Library sie über Major-Sprünge hinweg anhebt (siehe §Quellen)
- Der Generator **MUSS** `helm dependency build` (oder `update`) ausführen, sodass ein `Chart.lock` erzeugt und die Library unter `charts/` eingebunden wird, bevor überhaupt getemplatet oder gelintet wird; ein Chart ohne auflösbare Abhängigkeit ist unvollständig
- Die Abhängigkeit des Charts von `common` **SOLLTE** von der Dependency-Update-Automatisierung des Repositories (Renovate, gemäß `spec/project/dependency-audit/`) nachverfolgt werden, sodass Versions-Anhebungen vorgeschlagen und reviewt werden, statt still zu driften
- Generierte Values **MÜSSEN** gegen das mitgelieferte `values.schema.json` der Library validieren; der Generator **DARF NICHT** Values ausgeben, die das Schema verletzen (unbekannte Schlüssel, falsche Typen, fehlende Pflichtfelder), da die Library das Schema zur Render-Zeit erzwingt

### Chart-Skelett

- Der Generator **MUSS** ein Chart vom Typ `application` ausgeben, das mindestens besteht aus: `Chart.yaml` (Name, Chart-`version`, `appVersion`, dem `common`-Abhängigkeitsblock, `kubeVersion`), `values.yaml`, `README.md` und einem `templates/`-Einstiegspunkt, der den `common`-Loader aufruft und sonst nichts
- Jedes gerenderte Kubernetes-Objekt **MUSS** durch den `common`-Loader fließen; das Chart **DARF NICHT** handgeschriebene Kubernetes-Manifeste neben der Library enthalten, außer die Library kann das Objekt wirklich nicht ausdrücken — in diesem Fall wird die Ausnahme in der README des Charts dokumentiert
- Die Chart-`version` (SemVer der Chart-Paketierung) und die `appVersion` (das deployte Anwendungs-Release) sind verschieden: `appVersion` **MUSS** dem veröffentlichten Image-Tag der Anwendung folgen, und die Chart-`version` **MUSS** angehoben werden, wenn sich die Form des Charts unabhängig von der App ändert

### Controller und Container (der Kern-Korrektheitsvertrag)

- Das Chart **MUSS** mindestens einen Controller unter `controllers.<id>` mit explizitem `type` definieren — `deployment` für einen zustandslosen Dienst (der Standard), `statefulset`, wenn die App eine stabile Netzwerkidentität oder Speicher pro Replika braucht, `cronjob`/`job` für geplante oder einmalige Batch-Arbeit, `daemonset` für Agenten auf Node-Ebene; die Wahl **MUSS** dazu passen, wie die Anwendung tatsächlich läuft, nicht blind vorbelegt sein
- Jeder Controller **MUSS** mindestens einen Container unter `controllers.<id>.containers.<id>` mit vollständigem `image` tragen: ein explizites `repository` **und** ein explizites, unveränderliches `tag` (ein Digest oder eine veröffentlichte Version — niemals `latest` und niemals leer), mit einer zum Tag konsistenten `pullPolicy`
- Die Laufzeit-Eingaben eines Containers **MÜSSEN** vollständig deklariert sein: jeder Konfigurationswert, den die Anwendung zur Laufzeit liest, wird über `env` (literal oder valueFrom) oder `envFrom` (eine referenzierte ConfigMap/Secret) bereitgestellt; `command`/`args` werden nur gesetzt, um den Entrypoint des Images zu überschreiben, nicht wiederholt, wenn der Image-Standard korrekt ist
- Health-Probes **MÜSSEN** passend zur Anwendung konfiguriert sein: `probes.readiness` und `probes.liveness` werden für jeden langlaufenden Server deklariert, und `probes.startup` wird ergänzt, wo die App einen langsamen Kaltstart hat; jede Probe **MUSS** auf einen realen Endpunkt/Port oder Befehl zielen — wenn die Anwendung keinen HTTP-Health-Endpunkt bereitstellt, wird eine `tcp`- oder `exec`-Probe verwendet, und das vollständige Deaktivieren einer Probe **MUSS** eine dokumentierte Entscheidung mit Begründung in der README des Charts sein, keine stille Auslassung
- Jeder Container **MUSS** `resources`-Requests deklarieren und **MUSS** ein Memory-`limit` setzen gemäß `spec/project/kubernetes-deployment-best-practices/` §Resource requests, limits, and quality of service (die ein Memory-Limit vorschreibt, idealerweise gleich dem Request); ein ungebundener Container ohne Resource-Requests **DARF NICHT** ausgegeben werden
- Jeder Container (oder der Pod-Standard) **MUSS** einen gehärteten `securityContext` in der Stärke setzen, die `spec/project/kubernetes-deployment-best-practices/` §Security context and Pod Security Standards vorschreibt (`runAsNonRoot`, eine `runAsUser`/`runAsGroup` ungleich null, `readOnlyRootFilesystem`, weggelassene Capabilities, `allowPrivilegeEscalation: false`, `seccompProfile.type: RuntimeDefault`), wobei ein einzelnes `defaultPodOptions.securityContext` einer Wiederholung pro Container vorzuziehen ist; jene Spec ist die Autorität darüber, welche Felder verpflichtend sind, und `readOnlyRootFilesystem` gehört dazu — ein vom Programm benötigter schreibbarer Pfad kommt aus einem gemounteten `emptyDir` oder Volume, nicht aus einer Lockerung der Einstellung
- Vorstart-Arbeit (Schema-Migrationen, Berechtigungs-Korrekturen, Config-Templating) **SOLLTE** als `initContainers`-Eintrag ausgedrückt werden, statt in das `command` des Hauptcontainers eingefaltet zu werden, sodass Start-Reihenfolge und Fehlerzuordnung explizit bleiben

### Services und Networking

- Jeder Controller, der Netzwerkverkehr bedient, **MUSS** einen `service.<id>` haben, der an diesen Controller gebunden ist (`service.<id>.controller: <controller-id>`) und **benannte** Ports exponiert; der Port-**Name** (keine nackte Zahl) ist die Referenz, die andere Sektionen verwenden, sodass eine Probe oder ein Ingress-Backend den Port über seinen deklarierten Namen referenzieren **MUSS**
- Wenn die Anwendung von außerhalb des Clusters erreichbar ist, **MUSS** das Chart einen `ingress.<id>` (oder, für die Gateway-API, einen `route.<id>`) mit `className`, `hosts[].host`, `paths[].path`/`pathType`, einem Backend-`service`-Identifier + benanntem Port und TLS-Konfiguration generieren; der Host und `className` sind **Eingaben der betreibenden Person**, die als Values und README-Schritte sichtbar gemacht werden, und **DÜRFEN NICHT** auf die Domain eines bestimmten Clusters hartkodiert sein
- Die externe Exposition **SOLLTE** standardmäßig deaktiviert sein (`ingress.<id>.enabled: false`), sodass das Chart sicher installiert, bevor die betreibende Person Host und Ingress-Class liefert, statt einen Ingress auszugeben, der an eine Platzhalter-Domain gebunden ist

### Persistence und Konfiguration

- Dauerhafter Anwendungszustand **MUSS** unter `persistence.<id>` mit explizitem `type` deklariert werden: `persistentVolumeClaim` für dauerhafte Daten, `configMap`/`secret` für gemountete Konfiguration, `emptyDir` für Scratch, das einen Neustart nicht überleben muss; der Typ **MUSS** das reale Dauerhaftigkeits-Bedürfnis der Daten widerspiegeln
- Ein `persistentVolumeClaim`-Persistence-Item **MUSS** `accessMode` und `size` angeben; `storageClass` ist eine **Eingabe der betreibenden Person** (sichtbar gemacht, nicht hartkodiert), und `existingClaim` **MUSS** als Alternative unterstützt werden, sodass eine betreibende Person ein vorab bereitgestelltes Volume mitbringen kann
- Volume-Mounts **MÜSSEN** explizit und korrekt sein: `globalMounts`, wenn das Volume in jeden Container des besitzenden Controllers gehört, `advancedMounts.<controller>.<container>`, wenn nur ein bestimmter Container es braucht; der Mount-`path` **MUSS** dem Pfad entsprechen, den die Anwendung tatsächlich liest oder schreibt
- Nicht-geheime Konfigurationsdateien, die die Anwendung von der Platte liest, **SOLLTEN** über `configMaps.<id>` bereitgestellt und über ein `persistence`-Item gemountet werden, nicht ins Image gebacken, sodass Konfigurationsänderungen keinen Rebuild erfordern
- Secret-Material (Credentials, Tokens, Schlüssel) **MUSS** über `secrets.<id>` oder `envFrom`/`valueFrom` mit Verweis auf ein extern verwaltetes `Secret` bereitgestellt werden; das Chart **DARF NICHT** Secret-Werte im Klartext in `values.yaml` committen, und die README des Charts **MUSS** festhalten, wie die betreibende Person sie liefert (ein bestehendes `Secret`, External Secrets, SOPS, …)

### Pod-weite Standards und Identität

- Querschnittliche Pod-Belange (`securityContext`, `nodeSelector`, `tolerations`, `topologySpreadConstraints`, `imagePullSecrets`, `affinity`) **SOLLTEN** einmal unter `defaultPodOptions` gesetzt werden, statt pro Controller wiederholt zu werden; wenn ein Controller abweichen muss, wird die Abweichung über die eigenen Pod-Optionen des Controllers mit einer expliziten Merge-/Overwrite-Strategie ausgedrückt
- Wenn die Anwendung die Kubernetes-API aufrufen muss, **MUSS** das Chart einen expliziten `serviceAccount` und eine `rbac`-Bindung mit geringstmöglichen Rechten deklarieren, die genau auf das zugeschnitten ist, was die App braucht; braucht sie keinen API-Zugriff, verlässt sich das Chart auf den Standard und vergibt nicht über Bedarf hinaus

### Vollständigkeitsprüfung (das eigene Gate des Generators)

- Bevor das Chart als fertig erklärt wird, **MUSS** der Generator verifizieren, dass es Ende-zu-Ende rendert: `helm dependency build`, dann `helm template` (und `helm lint`) bei der gepinnten `kubeVersion`-Untergrenze, mit null Fehlern — ein Chart, das nicht rendert, wird nicht ausgeliefert
- Der Generator **MUSS** die referenzielle Integrität gegenprüfen: jeder Port-Name, den eine Probe oder ein Ingress referenziert, ist an einem Service deklariert; jeder Mount-Pfad bildet auf ein deklariertes `persistence`-Item ab; jeder `env`/`envFrom`-Schlüssel, auf den der Container angewiesen ist, löst zu einer deklarierten Quelle auf; jede `secret`/`configMap`-Referenz existiert — keine baumelnde Referenz und keine undeklarierte Laufzeit-Anforderung
- Der Generator **DARF NICHT** Platzhalter- oder `TODO`-Werte in `values.yaml` zurücklassen, die `helm install` in einen kaputten Workload gelingen ließen; ein Wert, den die betreibende Person liefern muss, erhält entweder einen sicheren, installierbaren Standard **oder** wird als erforderlicher README-Schritt sichtbar gemacht und, wo die Library es unterstützt, über Schema-`required`/Validierung zum frühen Scheitern gebracht, statt auf einen falschen Wert vorzubelegen

### Manuelle Schritte → Chart-README

- Die `README.md` des generierten Charts **MUSS** eine eigene Sektion „Manuelle Schritte" (Konfiguration) enthalten, die jede Aktion aufzählt, die die betreibende Person ausführen muss und die das Chart nicht selbst leisten kann — mindestens: das Ausführen von `helm dependency build`; das Setzen von Image-`tag`/`appVersion`; das Bereitstellen von Secret-Material; die Wahl von Ingress-`host` und `className`; die Wahl von `storageClass` oder eines `existingClaim`; und jeden First-Run-Migrations- oder Bootstrap-Schritt
- Jeder manuelle Schritt **MUSS** benennen, *was* zu setzen ist, *wo* (der konkrete `values.yaml`-Schlüsselpfad) und *warum*, sodass der Schritt für eine betreibende Person handlungsleitend ist, ohne die Templates des Charts oder die Interna der Upstream-Library zu lesen
- Die README **DARF NICHT** die Upstream-Referenz der `common`-Library duplizieren; sie verlinkt die Upstream-Dokumentation und dokumentiert nur die anwendungsspezifischen Entscheidungen dieses Charts und die erforderlichen Eingaben der betreibenden Person
- Ein Schritt, den das Chart stellvertretend für die betreibende Person sicher vorbelegen kann, **DARF NICHT** als manueller Schritt aufgeführt werden; die manuelle Liste ist die **irreduzible** Bedienfläche — die Menge der Eingaben, die das Chart wirklich nicht liefern kann — kein Inventar von allem, was konfigurierbar ist

### Agenten-Verhalten und Eingaben

- Die Eingaben des Generators sind die Zielanwendung und ihre Laufzeitfläche: die Container-Image-Koordinaten, die Laufzeit-Konfiguration (`env`-Schlüssel, Ports, Config-Dateipfade auf der Platte, persistente Datenpfade, benötigte Secrets) und die Exposition-Bedürfnisse der App (nur intern vs. extern erreichbar)
- Der Generator **SOLLTE** diese aus der eigenen Quelle der Anwendung ableiten, wo er kann (ein `EXPOSE`/`VOLUME`/`ENV` eines `Dockerfile`, `compose`-Dateien, dokumentierte Config-Pfade, Code, der Umgebungsvariablen liest) und das Gefundene **bestätigen**, statt Werte zu erfinden
- Wo eine erforderliche Eingabe fehlt oder mehrdeutig ist, **MUSS** der Generator sie von der betreibenden Person erheben (gemäß `spec/project/requirements-elicitation/`) oder eine explizite, sichtbare Annahme in der README des Charts festhalten — er **DARF NICHT** still einen Wert raten, der ein falsches Deployment rendern würde
- Der Generator **MUSS** das Chart an den konventionellen Chart-Ort des konsumierenden Repositories schreiben und einer bestehenden Konvention folgen, falls das Repository bereits eine hat (zum Beispiel `deploy/charts/<app>/` oder `charts/<app>/`), statt ein neues Layout aufzuzwingen

## Akzeptanzkriterien

- [ ] `spec/project/bjw-s-common-chart-deployment/` existiert mit `en.md` (kanonisch) und `de.md` (Übersetzung) und ist in `spec/README.md` gelistet
- [ ] Der Upstream-Anker ist gepinnt: Die Spec fordert eine explizite `common`-Abhängigkeitsversion, das kanonische Repository, eine `kubeVersion`-Untergrenze, `helm dependency build` und `values.schema.json`-Validierung
- [ ] Der Controller-/Container-Korrektheitsvertrag ist mit RFC-2119-Schlüsselwörtern formuliert und deckt explizites Image-Tag, vollständiges `env`/`envFrom`, Health-Probes, Resource-Requests, Security-Context und initContainers ab
- [ ] Die Anforderungen zu Services/Networking, Persistence/Konfiguration und Pod-Standards/Identität sind je mit benannter-Port-Bindung, expliziter Mount-Semantik (`globalMounts` vs. `advancedMounts`), der Kein-Klartext-Secret-Regel und `defaultPodOptions`-Wiederverwendung formuliert
- [ ] Das Vollständigkeits-Gate des Generators (rendert via `helm template`/`helm lint` bei der `kubeVersion`-Untergrenze, referenzielle-Integritäts-Gegenprüfung, keine Platzhalter-Werte) ist eine testbare Anforderung
- [ ] Der README-Manuelle-Schritte-Vertrag ist explizit und testbar: Eine reviewende Person kann verifizieren, dass die generierte README eine eigene Sektion hat, die jeden irreduziblen Schritt der betreibenden Person mit *was*/*wo*/*warum* aufzählt, und keinen Schritt, den das Chart hätte vorbelegen können
- [ ] Die Spec delegiert die vollständige Upstream-Referenz an die bjw-s-Dokumentation, statt das Schema der Library pro Schlüssel zu duplizieren
- [ ] Ein durchgearbeitetes Beispiel (ein für `kamerplanter` generiertes Chart) würde `helm dependency build`, `helm lint` und `helm template` bei der gepinnten `kubeVersion`-Untergrenze bestehen, mit einer README, die genau die manuellen Eingaben auflistet, die dieses Chart erfordert

## Offene Fragen

- **Scope-Promotion.** Sollte diese Spec `Portfolio-Scope: local` bleiben oder auf `portfolio` angehoben werden, sodass Consumer-Repositories mit selbst gehosteten Apps (`kamerplanter`, `kamerplanter-ha`, `claude-home-assistant`, `reachy-mini-app`) sie per Referenz gemäß `spec/project/portfolio-inherited-spec-layer/` erben? Die Promotion ist ein expliziter Wartungs-Akt und wird hier zurückgestellt.
- **Dediziertes Chart vs. `app-template`.** Ist ein dediziertes, versioniertes Consumer-Chart immer das Ziel, oder sollte der Agent für triviale/Wegwerf-Apps den schrumpfverpackten `app-template`-Pfad anbieten?
- **Secret-Management-Backend.** Standardisiert das Portfolio auf ein Backend (External Secrets Operator, SOPS, Sealed Secrets)? Falls ja, kann die „Kein-Klartext"-Anforderung einen konkreten Standard benennen, statt den Mechanismus offenzulassen.
- **GitOps-Grenze.** Diese Spec endet am Chart. Sollte eine begleitende Spec die Verdrahtung des Charts in einen GitOps-Controller regeln, oder bleibt das bewusst jedem Repository überlassen?
- **Chart-Ort-Konvention.** Gibt es einen portfolio-weiten Standard-Chart-Pfad (`deploy/charts/<app>/` vs. `charts/<app>/`), auf den diese Spec aus `spec/project/project-structure/` verweisen sollte, oder bleibt es eine Konvention pro Repository, die der Agent erkennt?

## Quellen

Die Upstream-Anker-Aussagen oben (der Versions-Pin der `common`-Library und ihre `kubeVersion`-Untergrenze) sind Author-Time-externe Aussagen, trianguliert gemäß `spec/claude/research-triangulate/` §"Author-time assertions" (Author-Time-Stufe: mindestens drei unabhängige Quellen, Primary-first geordnet). Abrufdatum für jede Quelle unten: 2026-07-24.

- **`common`-Library `version: 5.0.1` und kanonisches Repository `https://bjw-s-labs.github.io/helm-charts/`**: `common`-`Chart.yaml` am Tag `common-5.0.1`, deklariert `version: 5.0.1` (Primary), `https://raw.githubusercontent.com/bjw-s-labs/helm-charts/common-5.0.1/charts/library/common/Chart.yaml`; der veröffentlichte Helm-Repository-Index, der `common` 5.0.1 und die kanonische Repo-URL listet (Primary), `https://bjw-s-labs.github.io/helm-charts/index.yaml`; die `bjw-s-labs/helm-charts`-GitHub-Releases (Primary), `https://github.com/bjw-s-labs/helm-charts/releases`
- **`kubeVersion`-Untergrenze `>=1.31.0-0` für `common` 5.0.x (die 4.x-Linie deklarierte `>=1.28.0-0`)**: `common`-`Chart.yaml` am Tag `common-5.0.1`, deklariert `kubeVersion: ">=1.31.0-0"` (Primary), `https://raw.githubusercontent.com/bjw-s-labs/helm-charts/common-5.0.1/charts/library/common/Chart.yaml`; der Helm-Repository-Index, in dem `common` 4.0.1 bis 4.6.2 `>=1.28.0-0` und 5.0.0/5.0.1 `>=1.31.0-0` tragen (Primary), `https://bjw-s-labs.github.io/helm-charts/index.yaml`; die `common`-5.0.0-Release-Notiz, „increased minimum Kubernetes requirements to version 1.31" (Secondary), `https://github.com/bjw-s-labs/helm-charts/releases`

Die in einem früheren Entwurf angegebene Untergrenze `>=1.28.0-0` traf nur für die `common`-4.x-Linie zu; sie wurde gemäß der obigen Triangulation auf `>=1.31.0-0` korrigiert, um der gepinnten 5.0.1-Version zu entsprechen.
