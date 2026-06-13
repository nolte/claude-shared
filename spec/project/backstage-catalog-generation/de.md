# Backstage-catalog-info.yaml-Generierung

Status: draft

## Context

[Backstage](https://backstage.io) ist das Open-Source-Framework für Entwicklerportale, das Spotify an die CNCF gespendet hat. Sein zentrales Feature ist der **Software Catalog**: ein Graph aus Software- und Organisations-Entities, beschrieben in YAML-Deskriptordateien — konventionell eine `catalog-info.yaml` im Wurzelverzeichnis jedes Repositories —, die Backstage ingestiert, validiert und zu einem navigierbaren Modell dessen zusammenfügt, *welche Software existiert, wem sie gehört, wovon sie abhängt und welche APIs sie bereitstellt*. Ein zweites, separates Feature, das **Tech Radar**, visualisiert die Technologieentscheidungen einer Organisation (adopt / trial / assess / hold) und wird häufig in dasselbe Portal eingebunden, ist jedoch an eine eigene Datenquelle gekoppelt und nicht an den Catalog.

Ein bestehendes Softwareprojekt in ein Backstage-Portal aufzunehmen, bedeutet, einen Deskriptor zu schreiben, der auf drei Achsen zugleich korrekt ist: Er MUSS [MUST] Backstages per-Kind-JSON-Schema und Feld-Format-Validatoren erfüllen; er MUSS [MUST] Owner, Systeme und APIs referenzieren, die tatsächlich auflösen; und er SOLLTE [SHOULD] die well-known Annotations tragen, die die Integrationen des Portals aktivieren (Quell-Links, CI, TechDocs, GitHub). Von Hand ist das fehleranfällig — die Validierungsregeln sind strenger, als die Prosa-Docs vermuten lassen, mehrere Pflichtfelder sind nicht offensichtlich (ein leeres-aber-vorhandenes `spec.children` bei einer Group, kein `lifecycle` bei einer Resource), und eine Klasse von Metadaten DARF NICHT [MUST NOT] authored werden, weil der Catalog sie automatisch setzt.

Diese Spec erfasst diesen Wissensbestand als normative Referenz und als Pflichtenkatalog für einen automatisierten Generator. Sie ist die **Grundlage für einen späteren Skill**, der ein bestehendes Softwareprojekt liest und eine passende `catalog-info.yaml` erzeugt. Gemäß dem Scope des Projektverantwortlichen deckt sie den **vollen Entity-Kernel** ab — Component, API, Resource, System, Domain, Group, User, Location und Template — mit **besonderem Fokus auf den Software Catalog und das Tech Radar**. Sie fußt auf einer 146-Quellen-Recherche über `backstage.io/docs` sowie die Quellbäume `backstage/backstage` und `backstage/community-plugins`, festgehalten unter `.audits/backstage-research/2026-06-07-research-notes.md`.

Die Spec ist bewusst zweischichtig, passend dazu, wie sich das Wissen zerlegt: **§Das Backstage-Catalog-Modell** beschreibt, was ein konformer Deskriptor (und die Tech-Radar-Datendatei) erfüllen muss — das normative Substrat, unabhängig von jedem Generator gültig; **§Generator-Anforderungen** beschreibt, was ein auf diesem Substrat aufbauender automatisierter Generator tun, inferieren, emittieren und zu emittieren verweigern muss. Die Acceptance Criteria sind gegen einen Generator formuliert, damit der spätere Skill ein testbares Ziel hat.

## Goals

- Ein Generator kann ein bestehendes Repository lesen und eine `catalog-info.yaml` emittieren, die Backstages Schema-, Feld-Format- und Policy-Validierung deterministisch besteht, ohne dass am Pflicht-Floor manuell nachgebessert werden muss.
- Der volle Entity-Kernel wird einmalig präzise spezifiziert: per-Kind `apiVersion`/`kind`, required-vs-optional `spec`-Felder, die Konventions-Enums und die abgeleiteten Relations — sodass der Generator (und ein menschlicher Reviewer) eine einzige autoritative Tabelle hat statt der verstreuten, teils widersprüchlichen Upstream-Prosa.
- Der Generator emittiert den **MUST-Floor** je Kind plus ein **sicheres MAY-Set**, das er aus Repository-Signalen rechtfertigen kann, und er **authored nie** die Metadaten, die Backstage automatisch setzt.
- Benennungs-, Referenz- und Format-Constraints werden in ihrer tatsächlichen (strengeren) Stärke angegeben, sodass generierte Namen und Referenzen niemals zur Verarbeitungszeit an `FieldFormatEntityPolicy` scheitern.
- Das Tech-Radar-Datenmodell wird als erstklassiges, **separates** Anliegen erfasst: seine `TechRadarLoaderResponse`-Gestalt, sein Ring/Quadrant/Timeline-Modell, sein Custom-Data-Wiring und die Tatsache, dass es keine Catalog-Entity ist und kein Modell mit dem Catalog teilt.
- Validierung und Tooling werden so spezifiziert, dass der Generator seine Ausgabe selbst prüfen kann und die Praxis sich in CI einfügt.
- Versions- und Editions-Caveats (Deskriptor-`apiVersion`-Strings, neues vs. legacy Backend-System, die Tech-Radar-Paketverlagerung) werden fixiert, sodass ein Generator nicht auf der falschen Achse verzweigt oder ein veraltetes Format anvisiert.

## Non-Goals

- **Den Generator-Skill selbst zu bauen.** Diese Spec ist das Substrat; der Skill wird separat (via `skill-management` → `claude-plugin-developer`) gegen diese Anforderungen verfasst.
- **Ein Backstage-Backend zu betreiben oder zu konfigurieren.** App-Config-Wiring (`catalog.locations`, `catalog.providers.*`, das Tech-Radar-Backend `techRadar.url`) wird nur als der Onboarding-Kontext beschrieben, in dem der generierte Deskriptor landet; diese Spec besitzt keine Backend-Konfiguration.
- **Das Tech-Radar-UI-Plugin zu installieren oder zu stylen.** Das Datenmodell ist im Scope; die React-Installation, das Routing und das Styling nicht.
- **Eigene Entity-Kinds, Processors oder Feld-Format-Validatoren zu authoren.** Der Generator zielt auf den Kern-Kernel und die Default-Policy-Chain; das Modell zu erweitern ist explizit außerhalb des Scopes (und nur dort als Open Question getrackt, wo es das Generator-Verhalten begrenzt).
- **Group- und User-Entities zu ingestieren oder zu erzeugen.** Owner-Referenzen müssen *auflösen*, aber den Org-Graphen zu befüllen (aus einer SCM-Org via `GitHubOrgEntityProvider` und Verwandten) ist ein Operator-/SCM-Anliegen; der Generator emittiert Owner-Referenzen und markiert unaufgelöste, er fertigt die Owner nicht selbst.
- **Repository-übergreifende Topologie aufzulösen.** `spec.system`, `spec.dependsOn` und `spec.domain` erfordern in der Regel Wissen, das das einzelne Repository nicht trägt; der Generator schlägt sie nur aus expliziten Signalen vor und überlässt sie sonst dem Operator-Input.

## Requirements

Die Anforderungen sind in zwei Schichten organisiert. **§Das Backstage-Catalog-Modell** ist das normative Substrat: Jeder Punkt beschreibt, was Backstage selbst von einem konformen Deskriptor oder einer Tech-Radar-Datendatei verlangt, unabhängig von jedem Generator. **§Generator-Anforderungen** beschreibt, was ein auf diesem Substrat aufbauender automatisierter Generator MUSS [MUST], SOLLTE [SHOULD] und KANN [MAY]. Ein Generator ist nur dann konform zu dieser Spec, wenn er die Generator-Schicht erfüllt *und* jeder von ihm emittierte Deskriptor die Modell-Schicht erfüllt.

### Das Backstage-Catalog-Modell

#### Entity-Envelope

- Jede Catalog-Entity **MUSS [MUST]** ein YAML-Objekt mit genau diesen authored Root-Keys sein: `apiVersion` (string), `kind` (string, großgeschrieben), `metadata` (object) und `spec` (object, kind-spezifisch).
- `relations` (array von `{type, targetRef}`) und `status` (object mit `items[]` aus `{type, level, message, error?}`) sind **read-only, catalog-abgeleitete** Ausgabefelder. Ein Deskriptor **DARF NICHT [MUST NOT]** sie authoren; sie sind hier nur aufgeführt, damit Generator und Reviewer sie als tabu erkennen.
- Mehrere Entities **KÖNNEN [MAY]** sich eine Datei teilen, getrennt durch den Standard-YAML-Dokumenttrenner `---`.
- Der `metadata`-Block ist allen Kinds gemein. `metadata.name` ist **required**; `metadata.namespace` ist optional (Default `default`); `metadata.uid` und `metadata.etag` sind output-only und **DÜRFEN NICHT [MUST NOT]** authored werden. Optionale authored Metadaten: `title`, `description`, `labels` (key→value-Map), `annotations` (key→value-Map), `tags` (Liste von Strings), `links` (array von `{url (required), title, icon, type}`).

#### Entity-Kinds

Der Kernel umfasst neun Kinds. Ihre `spec.type`- und `spec.lifecycle`-Werte sind **Konventionen, keine erzwungenen Enums** — pro Organisation erweiterbar; das per-Kind-JSON-Schema erzwingt nur die `required`-Arrays und die String/Array-Gestalten. Ein konformer Deskriptor **MUSS [MUST]** jedes `required`-Feld seines Kinds tragen und **MUSS [MUST]** die dokumentierten `apiVersion`/`kind`-Strings verwenden.

| Kind | apiVersion | Required `spec` | Optional `spec` | Konventions-Enums | Hinweise |
| --- | --- | --- | --- | --- | --- |
| Component | `backstage.io/v1alpha1` | `type`, `lifecycle`, `owner` | `system`, `subcomponentOf`, `providesApis`, `consumesApis`, `dependsOn`, `dependencyOf` | type: `service`/`website`/`library`; lifecycle: `experimental`/`production`/`deprecated` | Das primäre Generator-Ziel. |
| API | `backstage.io/v1alpha1` | `type`, `lifecycle`, `owner`, `definition` | `system` | type: `openapi`/`asyncapi`/`graphql`/`grpc` | `definition` MUSS [MUST] ein nicht-leerer String sein; via `$text:`-Placeholder auf die Spec-Datei liefern. |
| Resource | `backstage.io/v1alpha1` | `type`, `owner` | `system`, `dependsOn`, `dependencyOf` | type org-definiert (`database`, `s3-bucket`, …) | **Kein `lifecycle`-Feld.** Ein `lifecycle` zu emittieren ist invalid. |
| System | `backstage.io/v1alpha1` | `owner` | `type`, `domain` | type org-definiert (`product`, `service`, …) | Kein `lifecycle`. |
| Domain | `backstage.io/v1alpha1` | `owner` | `type`, `subdomainOf` | type org-definiert | Kein `lifecycle`. `subdomainOf` ermöglicht verschachtelte Domains. |
| Group | `backstage.io/v1alpha1` | `type`, `children` | `profile` (`{displayName, email, picture}`), `parent`, `members` | type org-definiert (`team`, `business-unit`, `root`) | `children` MUSS [MUST] vorhanden sein; **darf eine leere Liste `[]` sein**, aber der Key darf nicht fehlen. |
| User | `backstage.io/v1alpha1` | `memberOf` | `profile` | — | `memberOf` MUSS [MUST] vorhanden sein; **darf `[]` sein**, aber der Key darf nicht fehlen. Kein type/lifecycle/owner. |
| Location | `backstage.io/v1alpha1` | — | `type`, `target` *oder* `targets`, `presence` (`required`/`optional`, Default `required`) | type z. B. `url`/`file` | Ein Zeiger auf weitere Entity-Daten, kein reales Ding. `target` oder `targets` verwenden. |
| Template | `scaffolder.backstage.io/v1beta3` | `type`, `owner` | `parameters`, `steps`, `output`, `secrets`, `presentation` | — | Aktueller Deskriptor ist `v1beta3`; `v1beta2` und das ursprüngliche `v1alpha1`-Scaffolder-Format sind älter/deprecated. Vom Scaffolder konsumiert, nicht Teil des Software-Entity-Relation-Graphen. |

- Ein Deskriptor **DARF NICHT [MUST NOT]** `spec.lifecycle` bei Resource, System, Domain, Group oder User emittieren — nur Component und API tragen es.
- Ein Group-Deskriptor **MUSS [MUST]** `spec.children` und ein User-Deskriptor **MUSS [MUST]** `spec.memberOf` enthalten, auch wenn leer (`[]`), sonst scheitert die Schema-Validierung.
- Die abgeleiteten **Relations**, die ein Generator verstehen sollte (indirekt authored, über die `spec`-Referenzfelder, nie direkt): `ownedBy`/`ownerOf`, `partOf`/`hasPart`, `dependsOn`/`dependencyOf`, `providesApi`/`apiProvidedBy`, `consumesApi`/`apiConsumedBy`, `parentOf`/`childOf`, `memberOf`/`hasMember`. Man beachte die Asymmetrie: `spec`-Feldnamen sind im Plural (`providesApis`, `consumesApis`), während die abgeleiteten Relation-Type-Strings im Singular stehen (`providesApi`, `consumesApi`).

#### Benennungs- und Format-Constraints

Die Feld-Format-Validatoren (`KubernetesValidatorFunctions` / `CommonValidatorFunctions`) sind **strenger als die Prosa-Docs**; ein konformer Deskriptor — und damit ein Generator — **MUSS [MUST]** sie in ihrer tatsächlichen Stärke erfüllen:

- **`metadata.name`** (`isValidObjectName`): Länge **1–63**; das **erste und letzte Zeichen MUSS [MUST] alphanumerisch sein**; die Trenner `[-_.]` sind nur im Inneren erlaubt. Ein führender oder abschließender Trenner ist invalid. Namen sind case-insensitiv eindeutig je `(kind, namespace)`; gemischte Groß-/Kleinschreibung ist nach der Default-Regel erlaubt (die Lowercase-und-Bindestriche-Konvention ist stilistisch, nicht erzwungen).
- **`metadata.namespace`** (`isValidDnsLabel`): kleingeschriebene Alphanumerische in bindestrich-getrennten Gruppen, Länge 1–63; **kein Underscore, kein Punkt, kein Großbuchstabe** — strenger als `name`.
- **Label-Keys**: optionaler DNS-Subdomain-Prefix (≤253 Zeichen) + `/` + ein Name-Teil nach der Entity-Name-Regel. Der `backstage.io/`-Prefix ist reserviert. **Label-Werte**: leerer String ODER die Entity-Name-Regel.
- **Annotation-Keys**: gleiche Gestalt wie Label-Keys. **Annotation-Werte**: beliebige Strings beliebiger Länge und Zeichenmenge — nur eine `typeof string`-Prüfung. Folglich **MUSS [MUST]** ein Deskriptor jeden numerisch oder boolesch aussehenden Annotation-Wert YAML-quoten (`github.com/user-id: '123456'`, `backstage.io/orphan: 'true'`), damit er ein String bleibt.
- **`tags`**: jedes Tag matcht `^[a-z0-9:+#]+(\-[a-z0-9:+#]+)*$` (kleingeschriebene `[a-z0-9:+#]`-Gruppen, bindestrich-getrennt, Länge 1–63).
- Der Catalog weist unbekannte Root-Level-Felder zurück (`NoForeignRootFieldsEntityPolicy`): nur `apiVersion`, `kind`, `metadata`, `spec`, `relations`, `status` sind auf Root-Ebene erlaubt.

#### Entity-Referenzen und Owner-Auflösung

- Eine Referenz in einem `spec`-Feld ist ein String `[<kind>:][<namespace>/]<name>` (1–3 Teile). Wenn ein Teil fehlt: das **kind** defaultet je nach Feldkontext, der **namespace** defaultet auf `default`.
- Das per-Feld-Default-Kind, das ein Generator anwenden MUSS [MUST], wenn er eine bare Referenz emittiert:

  | Feld | Default-Kind |
  | --- | --- |
  | `owner` | Group |
  | `system` | System |
  | `subcomponentOf` | Component |
  | `providesApis` / `consumesApis` | API |
  | `dependsOn` / `dependencyOf` | Component (bei einer Component); Component oder Resource (bei einer Resource) |
  | `domain` (System) | Domain |
  | `subdomainOf` (Domain) | Domain |
  | `parent` / `children` (Group) | Group |
  | `members` (Group) | User |
  | `memberOf` (User) | Group |

- **Owner-Disambiguierung**: `spec.owner` akzeptiert sowohl Group als auch User, aber eine *bare* Referenz defaultet auf **Group**. Um Ownership auf eine Person zu zeigen, **MUSS [MUST]** ein Deskriptor eine explizite `user:`-präfixierte Referenz emittieren; ein bare `owner`, der nur einen User dieses Namens matcht, dangelt.
- Eine Referenz löst nur auf, wenn bereits eine passende Entity im Catalog existiert. Referenzen werden auf *Grammatik* in der Schema-Schicht geprüft (das per-Kind-Schema erzwingt auf Referenzfeldern nur `string`/`minLength: 1`) und auf *Ziel-Existenz* nachgelagert während der Verarbeitung — sodass ein grammatikalisch valider Deskriptor dennoch eine dangelnde Relation erzeugen kann.

#### Well-known Annotations und Labels

Backstage dokumentiert ein Register well-known Annotations. Sie teilen sich in zwei Klassen, die ein Generator unterschiedlich behandeln muss:

- **Authorbar (emittieren, wenn das Signal existiert)** — `github.com/project-slug` (`org/repo`), `gitlab.com/project-slug`, `backstage.io/source-location` (`url:https://github.com/org/repo/`, abschließender Slash für ein Verzeichnis), `backstage.io/techdocs-ref` (`dir:.` wenn Docs kolokiert sind), `backstage.io/techdocs-entity`/`-entity-path`, `backstage.io/view-url`/`edit-url`, plus Integrations-Annotations, namespaced durch das integrierende System (`circleci.com/project-slug`, `jenkins.io/job-full-name`, `sonarqube.org/project-key`, `sentry.io/project-slug`, `pagerduty.com/integration-key`, …). Integrations-Annotations, deren Plugin außerhalb des Kerns lebt (Kubernetes `backstage.io/kubernetes-id`/`-label-selector`, PagerDuty, Jira), sind auf ihren Plugin-Seiten dokumentiert, nicht auf der zentralen Annotations-Seite.
- **Auto-gesetzt (ein Deskriptor DARF NICHT [MUST NOT] diese authoren)** — `backstage.io/managed-by-location`, `backstage.io/managed-by-origin-location`, `backstage.io/orphan`. Der Catalog leitet sie während der Ingestion ab; sie zu authoren ist falsch.
- **Deprecated Mappings**, die ein Generator vermeiden MUSS [MUST]: `backstage.io/github-actions-id` → `github.com/project-slug` verwenden; `backstage.io/definition-at-location` → Placeholder-Substitution (`$text:`/`$json:`/`$yaml:`) verwenden; `jenkins.io/github-folder` → `jenkins.io/job-full-name` verwenden.

#### Das Tech-Radar-Datenmodell

Das Tech Radar ist ein **eigenständiges Frontend-Plugin**, **nicht** in den Software Catalog verdrahtet und **konsumiert keine** Catalog-Entities. Seine Einträge sind keine Catalog-Entities — sie tragen keinen `apiVersion`/`kind`/`metadata`/`spec`-Envelope und werden nie als `catalog-info.yaml` registriert. Die beiden teilen out-of-the-box kein Datenmodell und keine Entity-Referenzen.

- Der Datenvertrag, den eine Tech-Radar-Datenquelle erfüllen **MUSS [MUST]**, ist `TechRadarLoaderResponse`, mit drei required Arrays: `quadrants` (`RadarQuadrant[]`), `rings` (`RadarRing[]`), `entries` (`RadarEntry[]`).
- Interface-Gestalten:

  | Interface | Felder |
  | --- | --- |
  | `RadarQuadrant` | `id` (string), `name` (string) |
  | `RadarRing` | `id`, `name`, `color`, `description?` |
  | `RadarEntry` | `key`, `id`, `quadrant` (eine quadrant-id), `title`, `url?`, `timeline` (`RadarEntrySnapshot[]`), `description?`, `links?` (`RadarEntryLink[]`) |
  | `RadarEntryLink` | `url`, `title` |
  | `RadarEntrySnapshot` | `date` (ein JS-`Date`), `ringId`, `description?`, `moved?` (`MovedState`) |
  | `enum MovedState` | `Down = -1`, `NoChange = 0`, `Up = 1` |

- **Rings** kodieren Adoptions-Reife (Sample-Daten: `adopt`/`trial`/`assess`/`hold`); **Quadrants** kodieren Technologie-Kategorien (Sample-Daten: Languages/Frameworks/Infrastructure/Process). Beide sind datengetrieben: Ring- und Quadrant-Anzahl und -Namen kommen aus den Daten-Arrays, nicht aus festen Enums.
- Der **aktuelle Ring eines Eintrags ist kein Feld am Eintrag** — er wird aus den `timeline`-Snapshots des Eintrags abgeleitet (latest-by-date ist die starke, sample-daten-gestützte Annahme; die exakte Selektionsregel ist eine Open Question). `date` ist im In-Memory-Modell ein JS-`Date`, sodass JSON-Datumsstrings **MÜSSEN [MUST]** konvertiert werden (`new Date(...)`), wenn ein Custom-Client die Daten lädt; der zod-Parser des Backends nutzt `z.coerce.date()`.
- Wiring: der Erweiterungspunkt ist `techRadarApiRef` (`interface TechRadarApi { load(id?: string): Promise<TechRadarLoaderResponse> }`). Drei Sourcing-Pfade existieren: der Default-Client (`DefaultTechRadarApi`, fetcht `<backend>/data`, validiert mit `TechRadarLoaderResponseParser`, fällt bei Fehler auf Mock-Daten zurück); ein Custom-Client, der `TechRadarApi` implementiert und via `createApiFactory(techRadarApiRef, new MyClient())` registriert wird (hat Vorrang vor einem Backend, wenn beide existieren); und das `plugin-tech-radar-backend`, das eine JSON-Datei von einer unter dem Top-Level-`techRadar.url`-App-Config-Key deklarierten URL liest und sie unter `/data` ausliefert.
- **Paketverlagerung**: Stand Mitte 2026 lebt das Plugin in `backstage/community-plugins` unter dem `@backstage-community`-Scope, aufgeteilt in `plugin-tech-radar` (Frontend), `plugin-tech-radar-common` (`model.ts`, `schema.ts`, `sampleTechRadarResponse.json` — die kanonische Modellquelle) und `plugin-tech-radar-backend`. Der alte `@backstage`-Paketname und die alten `backstage.io/docs/features/techradar/`-URLs sind deprecated / 404. Eine Spec oder ein Generator **MUSS [MUST]** die `@backstage-community`-Pakete referenzieren.

#### Validierung, Schema und die Policy-Chain

- Es gibt **kein** offizielles `backstage-cli`-Subkommando, um einen Deskriptor auf der Platte zu validieren (`config:check`/`print`/`schema` gelten für App-Config, nicht für Catalog-Entities).
- Der kanonische serverseitige Validierungspfad ist `POST <backend>/api/catalog/validate-entity` (z. B. `http://localhost:7007/api/catalog/validate-entity`). Der JSON-Request-Body erfordert **beide**, `location` (string) und `entity` (object) — `location` steht im Body, nicht in einem HTTP-Header. Antworten: `200` (kein Body) bei Erfolg; `400` mit `{ "errors": [ { "name", "message" } ] }` bei Fehler.
- Der de-facto Offline-/CI-Linter ist der Community-`@roadiehq/backstage-entity-validator` (CLI-Binary `validate-entity`, eine `RoadieHQ/backstage-entity-validator` GitHub Action und ein Docker-Image). Er führt Backstages eigene strukturelle Validierung plus Well-known-Annotation-Checks aus, akzeptiert Globs und Custom-Schema-Dateien, prüft aber **nicht** die Ziel-Existenz von Entity-Referenzen.
- Kanonische JSON-Schemas (draft-07) liegen in `packages/catalog-model/src/schema/` (`Entity`, `EntityEnvelope`, `EntityMeta` und per-Kind-Dateien unter `kinds/`). Die Default-Policy-Chain (`CatalogBuilder.buildEntityPolicy()`) ist `allOf(SchemaValidEntityPolicy, DefaultNamespaceEntityPolicy, NoForeignRootFieldsEntityPolicy, FieldFormatEntityPolicy)`.
- Validierung erfolgt in drei Stufen: **Ingestion** (grob — nur Präsenz von `kind`, `metadata.name`, `metadata.namespace`), **Processing** (volles Schema + Policy + Feld-Format + Processor-Emission) und **Stitching**. Ein Deskriptor, der die Ingestion besteht, kann zur Processing-Zeit dennoch zurückgewiesen werden.

#### Versions- und Editions-Caveats

- Deskriptor-`apiVersion`: `backstage.io/v1alpha1` für Component, API, Resource, System, Domain, Group, User, Location; `scaffolder.backstage.io/v1beta3` für Template (aktuell).
- Catalog-Discovery und Org-Ingestion installieren via das **neue Backend-System** (`backend.add(import('<module>'))`), das das legacy `CatalogBuilder.addEntityProvider()`/`addProcessor()` ersetzt. Eine auf Onboarding zielende Spec/Generator **SOLLTE [SHOULD]** den Entity-Provider-Pfad beschreiben, nicht den deprecated Discovery-Processor-Pfad.
- **Frontend-System-Invarianz**: `catalog-info.yaml`-Inhalt und Catalog-Ingestion-Config sind Backend-, Frontend-agnostische Anliegen. Ein Generator **DARF NICHT [MUST NOT]** beim Erzeugen eines Deskriptors auf das alte-vs-neue Frontend-System verzweigen.

### Generator-Anforderungen

Diese Anforderungen binden den späteren Generator-Skill. Ein Generator ist nur dann konform, wenn jeder von ihm emittierte Deskriptor zugleich §Das Backstage-Catalog-Modell erfüllt.

#### MUST-emit-/MAY-emit-Floor

- Für jedes Kind **MUSS [MUST]** der Generator den Envelope (`apiVersion`, `kind`, valides `metadata.name`, `spec`) plus jedes `required`-`spec`-Feld aus der per-Kind-Tabelle emittieren, und er **DARF NICHT [MUST NOT]** ein Feld emittieren, das das Kind nicht definiert (insbesondere nie `lifecycle` bei Resource/System/Domain/Group/User).
- Der Generator **MUSS [MUST]** die leeren-aber-required Keys emittieren, wo sie zutreffen: `spec.children: []` bei einer Group ohne bekannte Children, `spec.memberOf: []` bei einem User ohne bekannte Memberships.
- Für Component (das primäre Ziel) ist der MUST-Floor: `apiVersion: backstage.io/v1alpha1`, `kind: Component`, ein valides `metadata.name`, `spec.type`, `spec.lifecycle`, `spec.owner`. Alles andere ist MAY.
- Für API **MUSS [MUST]** der Generator ein nicht-leeres `spec.definition` emittieren, bevorzugt via einen `$text:`-Placeholder, der auf die entdeckte Spec-Datei zeigt, statt das ganze Dokument zu inlinen.
- Der Generator **KANN [MAY]** ein optionales `spec`-Feld nur dann emittieren, wenn er den Wert aus einem konkreten Repository-Signal rechtfertigen kann (siehe §Inferenz); er **DARF NICHT [MUST NOT]** ein geratenes `system`, `dependsOn` oder `domain` emittieren.

#### Inferenz aus einem bestehenden Projekt

Der Generator **SOLLTE [SHOULD]** Folgendes aus Repository-Signalen inferieren und **MUSS [MUST]** festhalten (z. B. als Kommentar oder Sidecar-Notiz), welche Werte inferiert wurden vs. eine Operator-Bestätigung erfordern:

- **`metadata.name`**: den Repository-/Projektnamen sluggen, dann führende/abschließende Nicht-Alphanumerische strippen und auf 63 Zeichen kappen, sodass das Ergebnis `isValidObjectName` erfüllt.
- **`spec.type`**: aus der Primärsprache/-struktur inferieren (`service`/`website`/`library` für Component; `openapi`/`asyncapi`/`graphql`/`grpc` für API), den Wert als Konvention behandeln, nicht als festes Enum.
- **`spec.lifecycle`**: nur mit einem rechtfertigenden Signal auf einen konservativen Wert defaulten (z. B. `experimental` oder `production`); sonst für Operator-Input markieren.
- **`spec.owner`**: aus `CODEOWNERS` oder einem Team-Slug ableiten; einen bare Slug nur für eine Group emittieren und eine explizite `user:`-präfixierte Referenz für eine Einzelperson.
- **APIs**: wenn eine OpenAPI/AsyncAPI/GraphQL/gRPC-Definition vorliegt, eine API-Entity mit `spec.definition: { $text: ./<relativer-pfad> }` emittieren und die API zu den `providesApis` der Component hinzufügen.
- **Annotations**: `github.com/project-slug` (aus dem Remote), `backstage.io/source-location` (`url:.../<repo>/`, abschließender Slash) und `backstage.io/techdocs-ref: dir:.` emittieren, wenn Docs kolokiert sind.

#### Automatisch gesetzte Felder, die der Generator NICHT authoren DARF

- Der Generator **DARF NICHT [MUST NOT]** `backstage.io/managed-by-location`, `backstage.io/managed-by-origin-location` oder `backstage.io/orphan` authoren (catalog-abgeleitet), noch `metadata.uid`/`metadata.etag` (output-only), noch `relations`/`status` (read-only).
- Der Generator **DARF NICHT [MUST NOT]** eine deprecated Annotation aus §Well-known Annotations emittieren; er verwendet stattdessen den Ersatz.

#### Descriptor-Platzierung und Owner-Auflösung

- Der Generator **MUSS [MUST]** den Deskriptor im Repository-Root als `catalog-info.yaml` platzieren, passend zum Default-Pfad der Discovery-Provider (`catalogPath` `/catalog-info.yaml` für GitHub/Bitbucket, `entityFilename` `catalog-info.yaml` für GitLab).
- Der Generator **MUSS [MUST]** Referenzen (insbesondere `owner`) in einer Form emittieren, die auflöst: er **SOLLTE [SHOULD]** für Cross-System-Robustheit die volle dreiteilige `kind:namespace/name`-Form bevorzugen und **MUSS [MUST]** für Einzel-Owner einen expliziten `user:`-Prefix verwenden.
- Wenn ein Owner nicht als auflösbar bestätigt werden kann (keine passende Group/User im Ziel-Catalog), **MUSS [MUST]** der Generator ihn als operator-handlungsbedürftig markieren, statt stillschweigend eine dangelnde Referenz zu emittieren; den Org-Graphen (Groups/Users) zu befüllen ist außerhalb des Scopes (siehe Non-Goals).

#### Tech-Radar-Generierung

- Ein Tech-Radar-Generator-Pfad (optionales zweites Ziel) **MUSS [MUST]** eine `TechRadarLoaderResponse`-JSON-Datei emittieren — `quadrants`, `rings`, `entries` — konform zu §Das Tech-Radar-Datenmodell, **nicht** eine `catalog-info.yaml`; er **DARF NICHT [MUST NOT]** Radar-Einträge als Catalog-Entities modellieren.
- Er **MUSS [MUST]** die Ring-Platzierung jedes Eintrags über die `timeline` des Eintrags ausdrücken (ein Snapshot mit `ringId` und einem `date`), nicht als direktes Feld, und **MUSS [MUST]** `date`-Werte emittieren, die ein Consumer zu einem JS-`Date` coercen kann.
- Er **SOLLTE [SHOULD]** das `@backstage-community`-Paketmodell anvisieren und **DARF NICHT [MUST NOT]** das deprecated `@backstage`-Tech-Radar-Paket oder die toten `backstage.io/docs/features/techradar/`-URLs referenzieren.

#### Generator-Selbstvalidierung

- Der Generator **SOLLTE [SHOULD]** jeden emittierten Deskriptor validieren, bevor er ihn präsentiert — mindestens gegen den Offline-`@roadiehq/backstage-entity-validator` (oder eine äquivalente stdlib-Prüfung des Schema-Floors und der Feld-Format-Regeln) — und **KANN [MAY]** zusätzlich an das `/api/catalog/validate-entity` eines laufenden Backends POSTen, wenn eines erreichbar ist.
- Der Generator **MUSS [MUST]** die Ziel-Existenz von Referenzen als vom Offline-Validator unbestätigt behandeln und Owner-/System-/API-Referenzen als zu bestätigende Behauptungen ausweisen, nicht als validierte Fakten.

## Acceptance Criteria

- [ ] Die Spec-Tabelle listet alle neun Kinds mit ihren `apiVersion`, required und optional `spec`-Feldern und Konventions-Enums, und ein Reviewer kann daraus den MUST-Floor für jedes Kind ableiten.
- [ ] Ein nach dieser Spec gebauter Generator emittiert eine Component-`catalog-info.yaml`, deren required Floor (`apiVersion`, `kind`, valides `metadata.name`, `spec.type`/`lifecycle`/`owner`) `@roadiehq/backstage-entity-validator` ohne manuelle Bearbeitung besteht.
- [ ] Ein generierter Resource-Deskriptor enthält nie `spec.lifecycle`; ein generierter Group-Deskriptor enthält stets `spec.children` (ggf. `[]`); ein generierter User-Deskriptor enthält stets `spec.memberOf` (ggf. `[]`).
- [ ] Ein generiertes `metadata.name` erfüllt stets `isValidObjectName` (1–63 Zeichen, erstes/letztes alphanumerisch, nur innen `[-_.]`), selbst wenn der Quell-Repo-Name führende/abschließende Trenner hat.
- [ ] Eine generierte API-Entity trägt ein nicht-leeres `spec.definition`, geliefert via einen `$text:`-Placeholder, und die bereitstellende Component listet sie unter `providesApis`.
- [ ] Kein generierter Deskriptor authored `backstage.io/managed-by-location`, `backstage.io/managed-by-origin-location`, `backstage.io/orphan`, `metadata.uid`, `metadata.etag`, `relations` oder `status`.
- [ ] Kein generierter Deskriptor verwendet eine deprecated Annotation (`backstage.io/github-actions-id`, `backstage.io/definition-at-location`, `jenkins.io/github-folder`).
- [ ] Numerisch oder boolesch aussehende Annotation-Werte in generierten Deskriptoren sind YAML-gequotete Strings.
- [ ] Ein Einzel-Owner wird mit einem expliziten `user:`-Prefix emittiert; eine bare Owner-Referenz wird nur je für eine Group verwendet.
- [ ] Der Deskriptor wird im Repository-Root als `catalog-info.yaml` geschrieben.
- [ ] Eine Tech-Radar-Ausgabe (falls generiert) ist eine `TechRadarLoaderResponse`-JSON-Datei mit `quadrants`/`rings`/`entries`, kodiert die Ring-Platzierung über die Eintrags-`timeline`, referenziert das `@backstage-community`-Modell und wird nie als Catalog-Entity modelliert.
- [ ] Inferierte Feldwerte sind von operator-bestätigungsbedürftigen Werten in der Generator-Ausgabe unterscheidbar.

## Open Questions

Übertragen aus der Recherche (`.audits/backstage-research/2026-06-07-research-notes.md`); jede begrenzt oder verfeinert das Generator-Verhalten und sollte vor oder während der Skill-Erstellung aufgelöst werden.

1. **Template aktueller Deskriptor** — die volle optionale `spec`-Feldliste (`parameters`, `steps`, `output`, `secrets`, `presentation`) für `scaffolder.backstage.io/v1beta3` gegen die Live-`software-templates/writing-templates`-Docs für das anvisierte Release bestätigen.
2. **`additionalProperties` auf per-Kind-`spec`** — ob die per-Kind-JSON-Schemas `additionalProperties: false` auf `spec` setzen (d. h. ob ein unbekanntes `spec`-Feld bei einem bekannten Kind zurückgewiesen oder bloß ignoriert wird). Bestimmt, ob ein Generator ohne ein Custom-Kind sicher Custom-`spec`-Felder hinzufügen darf.
3. **Owner-Group/User-Vorrang** — die exakte Regel, wenn ein bare `owner` sowohl eine Group als auch einen User gleichen Namens im selben Namespace matcht (warnen vs. still Group bevorzugen). Der Generator umgeht dies, indem er Owner stets präfixiert, aber die Regel sollte fixiert werden.
4. **catalog-import-App-Config-Keys** — bestätigen, ob die Register-Component-Flow-Keys `catalog.import.entityFilename` (Default `catalog-info.yaml`) und `catalog.import.pullRequestBranchName` (Default `backstage-integration`) sind, gegen `plugin-catalog-import`-Quelle.
5. **`validate-entity`-Scope** — ob der Endpoint die volle Custom-Processor-Chain ausführt oder nur Envelope + Kind-Schema + Default-Policies (d. h. ob Referenz-Ziel-Existenz und Custom-Kind-Validität dort geprüft werden).
6. **First-Party-Offline-Validator** — ob irgendeine aktuelle `@backstage/cli`/`@backstage/repo-tools`-Version ein Offline-`catalog-info.yaml`-Validate-Subkommando ausliefert (zum Recherchezeitpunkt keines gefunden).
7. **`validate-entity`-`location`-Semantik** — als im JSON-Body required bestätigt; bestätigen, dass keine Version zusätzlich einen HTTP-`Location`-Header akzeptiert/erfordert.
8. **Neu-vs-legacy-Erweiterungsmigration** — ob `CatalogBuilder.setFieldFormatValidators`/`addProcessor` zugunsten von `catalogModelExtensionPoint.setFieldValidators` / `catalogProcessingExtensionPoint.addProcessor` für das anvisierte Release deprecated sind.
9. **Enumerierte Validierungs-Fehlermeldungen** — der exakte Wortlaut, den `SchemaValidEntityPolicy` / `NoForeignRootFieldsEntityPolicy` / `FieldFormatEntityPolicy` emittieren, nützlich für das Selbstvalidierungs-Reporting des Generators.
10. **Relation-Array-Element-Schema** — das exakte Schema eines `relations[]`-Elements (string `targetRef` vs. strukturiertes `target {kind,namespace,name}`); authoring-tabu, aber relevant fürs Lesen bestehender Deskriptoren.
11. **Jira-Annotation-Keys** — bestätigen, ob `jira/project-key`, `jira/component` aus einem bestimmten Community-Plugin (z. B. RoadieHQ) statt aus dem Kern stammen.
12. **Status-Modell-Instabilität** — zusätzliche Status-Typen jenseits von `backstage.io/catalog-processing` könnten in neueren Releases existieren; das Status-Format ist explizit in Entwicklung. Annotation-Einführungs-/Deprecation-Release-Versionen sind unfixiert.
13. **`metadata.title`/`description`-Längenlimits** — upstream nicht angegeben; nur `name`, `namespace`, Label-/Annotation-Keys, Tags und Icons tragen explizite Constraints.
14. **Quell-Annotation-Auto-Befüllung** — welcher Processor (wahrscheinlich `AnnotateLocationEntityProcessor`) `source-location`/`edit-url`/`view-url`/`project-slug` beim Lesen von einer GitHub-URL auto-ableitet vs. welche hand-authored werden müssen. Begrenzt, welche Annotations der Generator emittieren sollte vs. dem Catalog überlassen.
15. **GitLab/Bitbucket-Onboarding-Spezifika** — `useSearch`, `catalogFile` vs. `entityFilename`, Subgroup-Handling, `GitlabFillerProcessor` und ob sie wie GitHub auf den Repo-Default-Branch defaulten.
16. **Tech-Radar-per-Item-zod-Feldregeln** — strengere Constraints (Color-Regex, nicht-leer, ob `links` validiert wird) in `plugin-tech-radar-common/src/schema.ts`, Zeile für Zeile gelesen.
17. **Tech-Radar-Backend-Refresh/-Header** — ob `plugin-tech-radar-backend` einen Refresh/Schedule oder Custom-Request-Header/Caching für `techRadar.url` unterstützt; App-Config-Keys jenseits von `techRadar.url`.
18. **Tech-Radar-kanonischer-Docs-Ort** — ob backstage.io noch eine Tech-Radar-Feature-Seite unter einem verlagerten Pfad hostet oder ob die kanonischen Docs nur im community-plugins-README leben.
19. **Tech-Radar-Current-Ring-Selektionsregel** — latest-by-date-Selektion und Tie-/Ordering-Handling aus der Rendering-Component-Quelle bestätigen.
