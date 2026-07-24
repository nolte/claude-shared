# Lizenzprüfung

Status: draft

## Kontext
**Leser:** Portfolio-Engineers, die diesen Prozess in einem Repository übernehmen, und der Skill-Autor, der das Prüf-Tool umsetzt.

Jedes Repository im Portfolio verbindet drei Ströme geistigen Eigentums: den eigenen Quellcode des Projekts, die Third-Party-Dependencies, die es über Manifeste hereinzieht, und die Werkzeuge, die den Build oder die Artefakte berühren (einschließlich KI-Generatoren, die Code, Bilder oder Modelle emittieren). Jeder Strom trägt Lizenzpflichten — Attribution, Notice-Weitergabe, Quelltext-Offenlegungs-Trigger, Patent-Grants —, und ein permissiv ausgerichtetes Portfolio kann eine Copyleft- oder nutzungsbeschränkte Pflicht, der es nie zugestimmt hat, nicht stillschweigend absorbieren. Heute wird Lizenzrisiko nur an den Rändern behandelt: `spec/project/dependency-audit/` fährt einen optionalen, allowlist-getriebenen Lizenz-Pass über Dependencies, `spec/project/project-structure/` verlangt eine Root-`LICENSE`-Datei, und `spec/tools/image-generation/` warnt vor der Output-Lizenz eines einzelnen Generators. Keines davon besitzt den *Prozess*: wie eine Lizenz identifiziert wird, welche Pflichten ihre Kategorie auslöst, welche Kombinationen mit der eigenen Lizenz des Projekts verträglich sind, wie KI-generierte Provenienz ins Inventar gelangt und wie ein Befund zu Remediation oder Attribution wird. Diese Spec definiert genau diesen End-to-End-Prozess — `Inventory/Discovery → SBOM → SPDX-Identifikation → Klassifizierung → Policy-Gate → Remediation → Attribution/NOTICE → CI-Dauerprüfung` —, durchgängig in SPDX verankert, und trägt die Default-allow/review/deny-Policy des Portfolios. Sie ist die Lizenz-Compliance-*Autorität*, die der Lizenz-Pass von `dependency-audit` für den Dependency-Slice umsetzt.

Die Sachaussagen dieser Spec (Lizenzkategorien und ihre Pflichten, die einseitige Apache-2.0/GPL-Kompatibilität, der GPL-„conveying"-Trigger, AGPL §13 Netzwerk-Copyleft, MPL-2.0 / EPL-2.0 datei-granulares Copyleft und Patent-Klauseln, die KI-Provenienz-Befunde, das stack-spezifische Tooling) sind durch ein vierrundiges Recherche-Protokoll belegt (2026-05-30 bis 2026-06-04); die tragenden Primärquellen sind in §Sources katalogisiert. Zwei interpretative Vorbehalte sind tragend und werden dort wiedergegeben, wo sie greifen: die FSF-Position, dass statisches und dynamisches Linken äquivalent sind, ist **kein** entschiedenes Recht, und der populäre Begriff „license laundering" ist Interpretation, nicht der Wortlaut der peer-reviewten Quellen.

## Ziele
- Jede Lizenz, die in ein Repository gelangt — eigener Code, Dependency oder Tool-/KI-generiertes Artefakt —, wird durch eine kanonische SPDX-Kennung identifiziert (oder einen expliziten `LicenseRef-`/`NOASSERTION`-Fallback), deren Volltext bei Bedarf auflösbar ist
- Jede identifizierte Lizenz wird einer Kategorie zugeordnet, deren Pflichten einmal niedergeschrieben und portfolioweit gleich angewendet werden
- Eine Default-allow/review/deny-Policy, auf ein permissiv ausgerichtetes Portfolio abgestimmt, gated jede Komponente, wobei deny den Pflichten vorbehalten bleibt, die das Portfolio wirklich nicht absorbieren kann (strong und network Copyleft in conveyed/netzwerk-exponierten Komponenten)
- Die eigene Lizenz des Projekts gilt als Kompatibilitäts-Anker: jede Dependency oder eingebundenes Werk wird gegen sie auf Kompatibilität geprüft, nicht im Abstrakten
- KI-generierte Artefakte tragen maschinenlesbare Provenienz, und KI-emittierter Code wird gegen quasi-wörtliche Reproduktion von Copyleft-Quellen gegated, damit das Inventar nicht stillschweigend verschmutzt werden kann
- Befunde werden zu einer begrenzten Reaktion (ersetzen / Ausnahme dokumentieren / die geforderte Attribution erzeugen), und die geforderte NOTICE-/Attribution-Ausgabe wird produziert statt vorausgesetzt
- Die Prüfung läuft dauerhaft in CI und beim Release und teilt sich Kadenz und Artefakt-Konventionen mit `dependency-audit`, statt sie zu duplizieren

## Nicht-Ziele
- Einen bestimmten Lizenz-Scanner als verpflichtend zu wählen: wie `dependency-audit` ist der Prozess tool-agnostisch; diese Spec benennt einen empfohlenen Default je Stack, das Repository darf aber ein Äquivalent einsetzen, das SPDX-Kennungen emittiert
- Rechtsberatung zu geben oder anwaltlichen Rat zu ersetzen: diese Spec kodiert einen Engineering-Prozess und eine konservative Default-Policy; ein wirklich mehrdeutiger oder risikoreicher Fall eskaliert zu einer menschlichen Entscheidung, nie zu einem erfundenen Urteil
- Die ausgehende Lizenz des Portfolios neu zu entscheiden: das ist eine Repository-Wahl, festgehalten in der `LICENSE`-Datei gemäß `spec/project/project-structure/`; diese Spec konsumiert sie als Kompatibilitäts-Anker
- Das CVE-/Vulnerability-Scanning von `dependency-audit` zu ersetzen: jene Spec besitzt das Supply-Chain-*Vulnerability*-Risiko; diese Spec besitzt das *Lizenz*-Risiko und liefert die Policy, die ihr Lizenz-Pass umsetzt
- Die operativen Details des umsetzenden Skills zu definieren (Tool-Aufruf, Output-Rendering): die leben unter `skills/` und dürfen sich ohne Spec-Änderung weiterentwickeln
- Den IP-Status des KI-Trainings selbst oder Fair-Use-Fragen aufzulösen: außerhalb des Scopes; abgedeckt ist nur *Provenienz und Lizenz-Hygiene der Artefakte, die im Repository landen*

## Anforderungen

### Scope — was geprüft wird
- **MUSS [MUST]** alle drei IP-Ströme prüfen: (1) die eigenen Quelldateien des Repositorys, (2) jede in einem getrackten Manifest deklarierte Third-Party-Dependency (unter Wiederverwendung des Manifest-Sets aus `spec/project/dependency-audit/` §Scope) und (3) Tools und KI-Generatoren, die zum Build-Output beitragen oder committete Artefakte emittieren (generierter Code, Bilder, Modellgewichte)
- **MUSS [MUST]** transitive Dependencies abdecken, nicht nur direkte; eine Copyleft-Pflicht in einem transitiven Paket bindet genauso wie in einem direkten
- **MUSS [MUST]** jeden Subroot in einem Monorepo einschließen, der ein eigenes Manifest trägt, damit Befunde der besitzenden Komponente zugeordnet werden
- **MUSS [MUST]** ein committetes KI-generiertes Artefakt (Code, Bild, Modellgewicht oder anderes Asset) als in-Scope-Element behandeln, dessen Provenienz und Lizenzstatus gemäß §KI-Provenienz festgehalten werden
- **MUSS [MUST]** im Inventar Komponenten, die *conveyed* werden (ausgeliefert, gelinkt oder als Teil des Produkts über ein Netzwerk angeboten), von Tools unterscheiden, die lediglich *auf Armeslänge ausgeführt* werden zur Build- oder Entwicklungszeit, weil die Pflicht-Trigger differieren (siehe §Klassifizierung und Pflichten); wenn der Nutzungskontext nicht bestimmbar ist, als `unknown-use-context` festhalten und die Komponente in den `review`-Tier leiten

### Die Pipeline
- **MUSS [MUST]** die Lizenzprüfung als geordnete Kette ausführen: `Inventory/Discovery → SBOM → SPDX-Identifikation → Klassifizierung → Policy-Gate → Remediation → Attribution/NOTICE → CI-Dauerprüfung`; jede Stufe konsumiert die Ausgabe der vorigen Stufe
- **MUSS [MUST]** ein maschinenlesbares SBOM als Inventar-Substrat erzeugen oder konsumieren statt einer Ad-hoc-Liste, damit das Inventar reproduzierbar und zwischen Läufen diffbar ist
- **DARF NICHT [MUST NOT]** ein grünes Policy-Gate als terminal behandeln: geforderte Attribution-/NOTICE-Ausgabe und (wo Pflichten es verlangen) Quelltext-Verfügbarkeit sind Teil der Kette, kein optionales Follow-up

### SPDX-Verankerung
- **MUSS [MUST]** jede Lizenz durch eine kanonische SPDX-Kurzkennung identifizieren; zusammengesetzte Fälle nutzen SPDX-License-Expressions (`OR` / `AND` / `WITH`), und eine Lizenz ohne SPDX-Match wird als `LicenseRef-<idstring>` festgehalten (nie stillschweigend verworfen)
- **MUSS [MUST]** jede identifizierte SPDX-Kennung bei Bedarf zu ihrem Lizenz-Volltext auflösen können — etwa via `https://spdx.org/licenses/<ID>.json` (`licenseText`), die `text/<ID>.txt` des `license-list-data`-Repositorys oder einen äquivalenten Offline-Mirror —, damit ein Reviewer die exakten Pflichten hinter jedem Befund nachlesen kann
- **MUSS [MUST]** die für einen Prüflauf verwendete SPDX-License-List-Version pinnen und im Artefakt festhalten, weil die Liste über die Zeit wächst und die Kennungs-Auflösung reproduzierbar sein muss
- **SOLLTE [SHOULD]** für Lizenzen, die noch nicht in der SPDX-Liste sind, auf die ScanCode LicenseDB (`scancode-licensedb.aboutcode.org/<key>`) zurückfallen und auf `spdx_license_key` mappen, wo es einen gibt, sonst auf `LicenseRef-scancode-<key>`
- **MUSS [MUST]** ein Element, dessen Lizenz nicht bestimmbar ist, als `NOASSERTION` festhalten und in den `review`-Tier leiten, nie in `allow`

### Klassifizierung und Pflichten
- **MUSS [MUST]** jede identifizierte Lizenz in genau eine Kategorie klassifizieren und deren Pflichten einheitlich anwenden:
  - **permissive** (z. B. MIT, BSD-2/3-Clause, ISC, Apache-2.0, 0BSD, Zlib, PSF-2.0): Pflicht ist Attribution — Copyright-Notice und Lizenztext erhalten; Apache-2.0 verlangt zusätzlich die Weitergabe etwaiger `NOTICE`-Datei-Inhalte
  - **weak (datei-granulares) Copyleft** (z. B. LGPL-2.1/3.0, MPL-2.0, EPL-2.0): die Quelltext-Offenlegungspflicht ist auf die lizenzierten Dateien oder die Bibliothek begrenzt; MPL-2.0-Copyleft greift pro Datei, die Covered Code enthält (eine neue Datei ohne Covered Code ist keine Modification, selbst innerhalb eines Larger Work); EPL-2.0-Copyleft greift nur auf Modified Works (Linken/Binden/Subklassen allein ist keine Contribution); LGPL-statisches-Linken ist erlaubt, verpflichtet aber, die Anwendung in einer Form auszuliefern, die dem Nutzer das Relinken der Bibliothek erlaubt — es verpflichtet **nicht** zur Offenlegung des Anwendungs-Quelltextes selbst
  - **strong Copyleft** (z. B. GPL-2.0, GPL-3.0): das kombinierte Werk trägt die GPL; die Quelltext-Offenlegungspflicht triggert beim *conveying* (Distribution an eine andere Partei), **nicht** bei rein interner Nutzung und **nicht** bei bloßer Netzwerkinteraktion ohne Transfer einer Kopie
  - **network Copyleft** (z. B. AGPL-3.0): ergänzt AGPLv3 §13 — eine modifizierte Version, die Nutzern über ein Netzwerk angeboten wird, muss diesen Nutzern den Corresponding Source anbieten; das schließt die SaaS/ASP-Lücke, die die gewöhnliche GPL offen lässt
  - **source-available / restricted** (z. B. BUSL-1.1, SSPL-1.0, Open-Weight-Modelllizenzen): nicht OSI-konform; trägt Field-of-Use-, Zeit- oder verhaltensbasierte Beschränkungen
  - **public-domain / public-domain-äquivalent** (z. B. CC0-1.0, Unlicense): keine Pflicht über das Nicht-Falschdarstellen der Autorschaft hinaus
- **MUSS [MUST]** für strong- und network-Copyleft-Befunde festhalten, ob die Komponente *conveyed/gelinkt/netzwerk-exponiert* oder *auf Armeslänge ausgeführt* ist, weil diese Unterscheidung den Policy-Tier entscheidet (siehe §Default-Policy)
- **SOLLTE [SHOULD]** Patent-Grant- und Patent-Retaliation-Klauseln erfassen, wo die Kategorie sie trägt: Apache-2.0 §3 (expliziter Grant der Claims, die durch eine Contribution allein oder kombiniert mit dem Work notwendig verletzt werden; der Grant erlischt, wenn der Lizenznehmer Patentklage erhebt mit der Behauptung, das Work verletze Patente), GPL-3.0 §11 (jeder Contributor gewährt eine non-exclusive, weltweite, royalty-free Lizenz unter seinen essential patent claims, flankiert von einer Anti-Diskriminierungs-Regel, die das Conveyen unter einem diskriminierenden Patent-Deal verbietet — GPL-3.0 trägt also KEINE Patent-Retaliation-Termination), MPL-2.0 (§2.1 Grant, §5.2 Retaliation-Termination) und EPL-2.0 (§2(b) Grant ohne Hardware, §7 Retaliation) —, weil eine Patent-Retaliation-Termination den Grant aushebeln kann, auf den sich ein Downstream-Nutzer verlässt (der wörtliche Klausel-Wortlaut ist jederzeit über §SPDX-Verankerung auflösbar, z. B. via `https://spdx.org/licenses/Apache-2.0.json`)
- **MUSS [MUST]** die FSF-Position „statisches und dynamisches Linken erzeugen beide ein kombiniertes Werk unter der GPL" als konservative Default-Annahme für das Gate behandeln, dabei aber im Artefakt festhalten, dass dies die FSF-Interpretation und **kein** entschiedenes Fallrecht ist

### Kompatibilität gegen die eigene Lizenz des Projekts
- **MUSS [MUST]** jede conveyed Dependency oder eingebundenes Werk auf Kompatibilität gegen die ausgehende Lizenz des Repositorys prüfen (gelesen aus der Root-`LICENSE`), nicht gegen ein abstraktes Ideal
- **MUSS [MUST]** die einseitigen Kompatibilitäten kodieren, die die Recherche belegt hat, mindestens:
  - lax-permissive Lizenzen sind untereinander kompatibel und meist in eine Copyleft-Kombination absorbierbar, mit der original-BSD-4-Clause (advertising clause) als inkompatibler Ausnahme
  - Apache-2.0-Code darf in ein GPLv3- (oder späteres) Werk kombiniert werden, aber GPLv3-Code darf **nicht** in ein Apache-2.0-lizenziertes Werk kombiniert werden — die Kompatibilität ist einseitig
  - Apache-2.0 ist **nicht** mit GPLv2 kompatibel (Patent-Termination-/Indemnification-Klauseln), aber mit GPLv3 kompatibel
  - zwei verschiedene Copyleft-Lizenzen sind ohne explizite Kompatibilitäts-Klausel gegenseitig inkompatibel (z. B. GPLv2 vs. GPLv3)
- **MUSS [MUST]** jede Kombination, die sie nicht positiv als kompatibel bestätigen kann, in den `review`-Tier leiten statt zu raten

### Default-Policy (permissiv ausgerichtetes Portfolio)
- **MUSS [MUST]** eine dreistufige Default-Policy anwenden, je Repository nur mit explizitem, festgehaltenem Rationale überschreibbar (analog zur Allowlist-mit-Rationale-Disziplin von `dependency-audit`):
  - **allow** (passiert automatisch): die permissive und public-domain Kategorie; die konkrete Default-Allowlist ist an SPDX-Kennungen verankert und aus dem CNCF-allowed-third-party-license-Set geseedet (z. B. `0BSD, BSD-2-Clause, BSD-3-Clause, MIT, MIT-0, ISC, Apache-2.0, PSF-2.0, Python-2.0, PostgreSQL, Zlib, X11, Unlicense, CC0-1.0`)
  - **review** (manuelle Entscheidung nötig, Gate ist `blocked`, nicht `pass`): weak/datei-granulares Copyleft; source-available/restricted Lizenzen; Open-Weight-Modelllizenzen; die BSD-4-Clause-advertising-clause-Ausnahme; jedes `LicenseRef-*` / `NOASSERTION`; jede nicht positiv als kompatibel bestätigte Kombination; strong/network Copyleft in einer Komponente, die *nur auf Armeslänge ausgeführt* wird (Build-/Dev-Tool, nicht conveyed)
  - **deny** (scheitert automatisch): strong Copyleft (GPL-Familie) und network Copyleft (AGPL) in jeder Komponente, die als Teil des Produkts *conveyed, gelinkt oder über ein Netzwerk angeboten* wird — gerechtfertigt, weil ein permissiv ausgerichtetes, teils SaaS-basiertes Portfolio die Pflicht zum kombinierten Werk bzw. zur §13-Quelltext-Offenlegung nicht absorbieren kann
- **MUSS [MUST]** ein deny-Tier-Override nur mit einer benannten, zeitlich begrenzten, rationale-tragenden Ausnahme erlauben (gleiche Hülle wie §Remediation), nie als stillschweigende Allowlist-Änderung
- **MUSS [MUST]** diese Portfolio-Default-Policy als die „explicit policy with named disallowed licenses" behandeln, die `spec/project/dependency-audit/` §License audit verlangt, bevor ein Lizenzbefund hart fehlschlagen darf: ein Repository, das `license-check` übernommen hat, braucht keine zusätzliche Per-Repository-Deny-Deklaration, damit der deny-Tier bindet
- **DARF NICHT [MUST NOT]** die Kategorie einer Lizenz allein nach lokalem Ermessen herabstufen; Widerspruch ist eine festgehaltene Ausnahme mit Rationale, keine Neuklassifizierung

### Eigener-Code- und In-Repo-Compliance
- **MUSS [MUST]** bestätigen, dass das Repository seine ausgehende Lizenz über eine Root-`LICENSE`-Datei deklariert (die Existenzpflicht der Datei wird an `spec/project/project-structure/` delegiert) und dass die deklarierte SPDX-Kennung valide ist
- **SOLLTE [SHOULD]** pro-Datei-Lizenzinformation für den eigenen Quellcode im FSFE-REUSE-Stil tragen — `SPDX-FileCopyrightText` + `SPDX-License-Identifier`-Header (oder `.license`-Sidecars / `REUSE.toml`) — und eine `LICENSES/<SPDX-ID>.txt`-Datei je verwendeter Lizenz, damit die In-Repo-Lizenzauflösung deterministisch ist
- **MUSS [MUST]** die Attribution-/NOTICE-Ausgabe produzieren, die die Dependency-Lizenzen verpflichten — direkt erzeugt oder über ein vom umsetzenden Skill benanntes delegiertes Attribution-Tool (z. B. eine aggregierte Third-Party-Notices-Datei) —, statt anzunehmen, dass Attribution erfüllt sei; für Apache-2.0-Dependencies schließt das die Weitergabe der `NOTICE`-Inhalte ein

### KI-Provenienz
- **MUSS [MUST]** maschinenlesbare Provenienz für jedes committete KI-generierte Artefakt festhalten — mindestens die Tatsache, dass es KI-generiert ist, und wo bekannt Generator/Modell und Tier — unter Nutzung eines verfügbaren Standard-Trägers (CycloneDX ML-BOM Component-Typ `machine-learning-model` + `modelCard` oder die SPDX-3.0.1-AI-Profile-`AIPackage`-Properties); für eine schlichte KI-generierte *Datei* ohne dediziertes „AI-generated"-Flag im Standard ist ein SPDX-Comment/Annotation der akzeptierte Fallback
- **MUSS [MUST]** KI-emittierten Code als Copyleft-Kontaminationsrisiko behandeln und gaten: es ist empirisch belegt, dass selbst leistungsstärkste Code-LLMs Open-Source-Code in rund 0,88–2,01 % der generierten Snippets mit „striking similarity" reproduzieren und für Copyleft-Snippets meist keine Lizenzinformation emittieren; der Prozess **MUSS [MUST]** einen Duplikat-/Ähnlichkeits-Erkennungsschritt gegen Copyleft-Quellen für KI-emittierten Code enthalten, bevor dieser als eigener Code behandelt wird
- **MUSS [MUST]** Open-Weight-Modelllizenzen (z. B. OpenRAIL / RAIL-M, die Llama Community License, die custom Gemma Terms of Use) als `review`-Tier source-available/restricted Lizenzen klassifizieren, **nicht** als OSI-Open-Source, weil sie Use-Restrictions tragen und die „for any purpose"-Freiheiten der Open Source AI Definition verfehlen — und **MUSS [MUST]** die Artefakt-Version pinnen, da ein Open-Weight-Modell die Lizenz zwischen Versionen ändern kann (z. B. Gemmas custom Terms für v1–v3 versus Apache-2.0 für v4)
- **DARF NICHT [MUST NOT]** annehmen, dass die Terms eines kommerziellen Generators ein sauberes, urheberrechtlich schützbares Artefakt gewähren: die Terms variieren (manche weisen Output-Eigentum zu, ohne Schützbarkeit zu garantieren; IP-Indemnities sind häufig auf zahlende Tiers gegated), und rein KI-generierter Output ist nach US-Recht ggf. überhaupt nicht schützbar (ein auf US-Jurisdiktion begrenzter Befund; andere Jurisdiktionen weichen ab) — die geltenden Terms und den Tier im Artefakt erfassen statt vorauszusetzen. Die bislang verifizierten Per-Generator-Terms (GitHub Copilot, OpenAI, Adobe Firefly, Midjourney) sind im Evidenz-Anhang [`ai-generator-terms.md`](ai-generator-terms.md) festgehalten; diese Tabelle ist die volatile Evidenzschicht und bleibt aus diesem normativen Text heraus, weil sich Anbieter-Terms ändern
- **SOLLTE [SHOULD]** die „license laundering"-Rahmung als Interpretation kennzeichnen, wenn sie in Dokumentation verwendet wird; das zugrundeliegende Compliance-Risiko (nicht-attribuierter copyleft-ähnlicher Code) ist belegt, das Label ist nicht der Wortlaut der Primärquellen

### Stack-spezifisches Tooling
- **MUSS [MUST]** auf Spec-Ebene tool-agnostisch bleiben: jedes Tool ist akzeptabel, das Lizenzen per SPDX-Kennung identifiziert und die Pipeline speist; das Repository hält im Artefakt fest, welches Tool und welche Version es nutzte (Reproduzierbarkeit, wie in `dependency-audit`)
- **SOLLTE [SHOULD]** diese Defaults je Stack bevorzugen, die jeweils SPDX emittieren oder darauf mappen:
  - **Python**: auf PEP-639-`License-Expression` / `License-File` Core-Metadata zurückgreifen, wo vorhanden; `pip-audit` dient zugleich als CycloneDX-SBOM-Generator für die Discovery+SBOM-Stufen
  - **Node**: `license-checker-rseidelsohn` (der gepflegte Nachfolger des aufgegebenen `license-checker`), der `package.json`-Metadaten gegen das `spdx`-Modul validiert und fertige CI-Gate-Primitive (`--failOn`, `--onlyAllow`) bietet
  - **Go**: `go-licenses` (Google), aufgebaut auf dem Google License Classifier, der Lizenzen mit SPDX-Kennungen benennt und einen Confidence-Score 0.0–1.0 trägt
  - **cross-stack**: CycloneDX native Per-Ökosystem-Generatoren für das SBOM; ein Classifier (Syft, ScanCode, ORT) für das Lizenztext-Matching
- **MUSS [MUST]** je Stack bestätigen, dass die gewählte Tool-Kette die Attribution-/NOTICE-Ausgabe erzeugen kann, die §Eigener-Code- und In-Repo-Compliance verlangt: die benannten Defaults decken Discovery, SBOM und Klassifizierung ab; für die Attribution-/NOTICE-Generierung ist der verifizierte stack-übergreifende Default die NOTICE-Templates des ORT-Reporters (`PlainTextTemplate` bzw. die `NOTICE_SUMMARY`-Variante, beide via Apache Freemarker anpassbar), und für Go bündelt `go-licenses save` Lizenztext und Copyright-Notice je Dependency; berücksichtige die dokumentierten Grenzen von `go-licenses` (warnt bei Nicht-Go-Code, der weitere Lizenzpflichten verbergen kann, und kann eine Lizenz-URL nicht auflösen), sodass eine Nicht-Go- oder ungelöste Komponente ein `review`-Befund ist, nie ein Silent-Pass
- **MUSS [MUST]** Scanner so konfigurieren, dass Lizenztext, der keiner bekannten SPDX-Kennung zugeordnet werden kann, zum Review aufgetaucht wird statt stillschweigend als „unlicensed" markiert (eine bekannte Syft-Default-Falle vor dessen `include-unknown-license-content`-Option) — eine nicht zugeordnete Lizenz ist ein `review`-Befund, nie ein `allow`
- **DARF NICHT [MUST NOT]** irgendeine Heuristik „metadaten-basierte SBOM-Generatoren sind ungenauer als build-basierte" als Tool-Auswahl-Regel übernehmen: dieser Claim wurde untersucht und widerlegt und darf die Tool-Leitlinie der Spec nicht treiben

### Remediation und Ausnahmen
- **MUSS [MUST]** auf jeden Befund, der nicht `allow` ist, eine von drei Reaktionen anwenden, innerhalb eines begrenzten Fensters, ausgerichtet an der Reaktionsdisziplin von `dependency-audit`:
  - **replace**: die Komponente gegen eine kompatibel lizenzierte Alternative tauschen
  - **exception with rationale**: eine benannte, zeitlich begrenzte (`valid-until`, ISO 8601) Ausnahme mit einzeiligem Rationale und Genehmiger festhalten; erlaubt für `review`-Befunde und, nur mit explizitem Sign-off, für ein deny-Tier-Override
  - **satisfy the obligation**: die Komponente behalten und produzieren, was ihre Lizenz verlangt (Attribution-/NOTICE-Eintrag, Quelltext-Verfügbarkeits-Angebot, relink-fähige Form für LGPL)
- **MUSS [MUST]** jede Ausnahme an ihrem `valid-until`-Datum erneut prüfen; Erneuerung erfordert ein frisches Rationale
- **DARF NICHT [MUST NOT]** einen Befund stummschalten, indem die Allowlist ohne Rationale bearbeitet oder die Lizenz neu klassifiziert wird

### Trigger, Kadenz und CI
- **MUSS [MUST]** als CI-Dauerprüfung bei Änderungen laufen, die ein Dependency-Manifest, eine Lockfile, die `LICENSE`-Datei oder committete KI-generierte Artefakte berühren
- **MUSS [MUST]** eine Vollprüfung vor jedem Release-Tag laufen und sich das Release-Gate-Timing von `spec/project/dependency-audit/` teilen
- **MUSS [MUST]** mit `dependency-audit` integrieren statt es zu duplizieren: wenn der Lizenz-Pass von `dependency-audit` auf dem Dependency-Slice läuft, wendet er die Klassifizierung und Policy *dieser* Spec an; diese Spec besitzt zusätzlich die Eigener-Code- und KI-Provenienz-Slices und die Policy-Autorität
- **SOLLTE [SHOULD]** die Taskfile-Target-Konvention des Repositorys wiederverwenden, damit Contributor die Prüfung lokal reproduzieren

### Audit-Artefakt
- **MUSS [MUST]** das Ergebnis jeder Vollprüfung persistieren, standardmäßig unter der portfolioweiten `.audits/license-check/`-Pfadkonvention, und festhalten: Datum, Trigger, Scope (geprüfte und übersprungene Subroots/Ströme), das/die genutzte(n) Tool(s) und Version(en), die gepinnte SPDX-License-List-Version, die Per-Komponente-SPDX-Kennung, Kategorie, Policy-Tier und Reaktionsentscheidung, plus die geprüfte Git-Revision
- **SOLLTE [SHOULD]** auf das vorige Artefakt verlinken, damit der Verlauf nachvollziehbar ist

### Abgrenzung
- **MUSS [MUST]** die Lizenz-Compliance-Autorität bleiben, während `dependency-audit` das Vulnerability-/CVE-Risiko besitzt; beide teilen Kadenz- und Artefakt-Konventionen, vermischen aber nie ihre Befunde
- **MUSS [MUST]** die ausgehende Lizenz aus der `LICENSE`-Pflicht von `spec/project/project-structure/` konsumieren, statt die Datei erneut zu verlangen
- **MUSS [MUST]** den Output-Lizenz-Disclaimer von `spec/tools/image-generation/` als eine Instanz der §KI-Provenienz-Regel für KI-generierte Bild-Assets behandeln, nicht als konkurrierende Policy
- **DARF NICHT [MUST NOT]** über KI-Trainings-Legalität, Fair Use oder die Wahl der ausgehenden Lizenz des Projekts urteilen

## Akzeptanzkriterien
- [ ] Jedes Repository, das diese Spec übernimmt, produziert ein nachvollziehbares Lizenzprüfungs-Artefakt (Default `.audits/license-check/`), das das/die Tool(s) und Version(en), die gepinnte SPDX-License-List-Version und die geprüfte Git-Revision benennt
- [ ] Jede Komponente im jüngsten Artefakt trägt eine kanonische SPDX-Kennung (oder ein explizites `LicenseRef-`/`NOASSERTION`), eine Kategorie, einen Policy-Tier und — wo nicht `allow` — eine Reaktionsentscheidung
- [ ] Jede identifizierte SPDX-Kennung im Artefakt kann von einem Reviewer über die festgehaltene Auflösungsmethode zu ihrem Lizenz-Volltext aufgelöst werden
- [ ] Keine conveyed/netzwerk-exponierte Komponente trägt eine strong- oder network-Copyleft-Lizenz im `allow`-Tier; jede solche Komponente ist entweder ersetzt oder steht unter einer abgezeichneten, zeitlich begrenzten deny-Tier-Ausnahme
- [ ] Jede Dependency oder eingebundenes Werk ist als kompatibel mit der ausgehenden Lizenz des Repositorys festgehalten oder in `review` geleitet, mit benannter konkreter Inkompatibilität
- [ ] Jedes committete KI-generierte Artefakt trägt maschinenlesbare Provenienz, und KI-emittierter Code hat den Copyleft-Ähnlichkeits-Erkennungsschritt durchlaufen, bevor er als eigener Code behandelt wurde
- [ ] Open-Weight-Modelllizenzen erscheinen als `review`-Tier (nicht `allow`), mit gepinnter Modell-Artefakt-Version
- [ ] Die geforderte Third-Party-Attribution-/NOTICE-Ausgabe existiert und schließt die Apache-2.0-`NOTICE`-Weitergabe ein, wo zutreffend
- [ ] Jeder Nicht-`allow`-Befund hat eine `replace`-, `exception with rationale`- (mit `valid-until` und Genehmiger) oder `satisfy the obligation`-Entscheidung; keine Ausnahme steht über ihr `valid-until` hinaus ohne frisches Rationale
- [ ] Die Prüfung läuft in CI bei relevanten Änderungen und vor Release-Tags, und der Lizenz-Pass von `dependency-audit` delegiert Klassifizierung und Policy an diese Spec
- [ ] Jeder Nicht-`allow`-Befund trägt eine Reaktionsentscheidung (oder eine dokumentierte Ausnahme mit `valid-until` und Genehmiger), datiert innerhalb des zutreffenden Reaktionsfensters, damit die Begrenzte-Fenster-Pflicht verifizierbar ist
- [ ] Jede strong- oder network-Copyleft-Komponente im Artefakt hält ihren conveyed/gelinkt/netzwerk-exponiert- vs. Armeslänge-Status (oder `unknown-use-context`) fest, und dieser Status passt zum zugewiesenen Policy-Tier
- [ ] Der umsetzende Prozess wird gegen Fixtures für die vier aufgezählten einseitigen Kompatibilitätsregeln geübt (z. B. eine conveyed GPLv3-Dependency in einem Apache-2.0-Produkt ist nie `allow`; eine Apache-2.0-Dependency in einem GPLv3-Projekt schon), womit die Kompatibilitäts-Kodierung bestätigt wird statt eines pauschalen Route-to-`review`

## Offene Fragen
- Gelöst am 2026-06-04 (Follow-up-Recherche-Runde): die Cross-Reference-Neuausrichtung ist umgesetzt, sodass `spec/portfolio/tech-stack/` und `spec/project/dependency-audit/` nun `license-check` als Policy-Autorität benennen; der Patent-Wortlaut von Apache-2.0 §3 und GPL-3.0 §11 ist verifiziert und in §Klassifizierung und Pflichten eingearbeitet; der NOTICE-Generierungs-Default ist in §Stack-spezifisches Tooling auf den ORT-Reporter gehärtet; und die Per-Generator-Terms (GitHub Copilot, OpenAI, Adobe Firefly, Midjourney) sind im Evidenz-Anhang [`ai-generator-terms.md`](ai-generator-terms.md) festgehalten statt in diesem normativen Text.
- Den deny-Tier-Default erneut prüfen, falls ein `nolte/*`-Repository jemals absichtlich unter Copyleft lizenziert wird, was den Kompatibilitäts-Anker für dieses Repository umkehren würde.

## Sources

Die Sachaussagen oben stützen sich auf ein vierrundiges Primärquellen-Recherche-Protokoll (2026-05-30 bis 2026-06-04). Die tragenden Quellen, gruppiert:

**SPDX-Verankerung und In-Repo-Compliance**

- <https://spdx.org/licenses/> und <https://github.com/spdx/license-list-data> (Identifier-Auflösung und volle Lizenztexte)
- <https://scancode-licensedb.aboutcode.org/> (Fallback für Lizenzen außerhalb der SPDX-Liste)
- <https://reuse.software/spec-3.3/> (Per-Datei-Lizenzinformation)

**Kompatibilität und Copyleft-Interpretation**

- <https://www.gnu.org/licenses/gpl-faq.html>, <https://www.gnu.org/licenses/license-list.en.html> und <https://www.gnu.org/licenses/license-compatibility.en.html>
- <https://www.apache.org/licenses/GPL-compatibility.html> (die einseitige Apache-2.0/GPLv3-Regel)
- <https://www.mozilla.org/MPL/2.0/> und die zugehörige FAQ (datei-granularer Copyleft-Scope)
- <https://spdx.org/licenses/GPL-3.0-only.html> und <https://spdx.org/licenses/EPL-2.0.html> (wörtlicher Patent-Klausel-Wortlaut)
- <https://lwn.net/Articles/548216/> (Kontext der Linking-Äquivalenz-Debatte)

**Policy-Seeds**

- CNCF `allowed-third-party-license-policy` (<https://github.com/cncf/foundation>): eine SPDX-Identifier-verankerte Allowlist, Seed für den Default-`allow`-Tier — bewusst nicht als „rein permissiv" überzeichnet

**KI-Provenienz und Output-Rechte**

- U.S. Copyright Office, *Copyright and Artificial Intelligence, Part 2: Copyrightability* (<https://www.copyright.gov/ai/Copyright-and-Artificial-Intelligence-Part-2-Copyrightability-Report.pdf>) und <https://www.copyright.gov/newsnet/2025/1060/>
- Das `LiCoEval`-Benchmark (<https://arxiv.org/html/2408.02487v3>) — der 0,88–2,01-%-Striking-Similarity-Befund — und <https://arxiv.org/html/2409.06390v1>
- <https://opensource.org/ai/open-source-ai-definition> (Open-Weight-Lizenzen gegen die OSAID-Freiheiten)
- <https://cyclonedx.org/capabilities/mlbom/> (ML-BOM-Provenienz-Träger); das SPDX-3.0.1-AI-Profil
- Anbieter-Terms: `learn.microsoft.com` Customer Copyright Commitment (GitHub Copilot), <https://openai.com/policies/row-terms-of-use>, Adobe-Firefly-Legal-FAQ, `docs.midjourney.com`-Terms (via <https://terms.law/ai-output-rights/midjourney/>, wenn die Primärquelle Fetches blockt) — das verifizierte Extrakt liegt in [`ai-generator-terms.md`](ai-generator-terms.md)

**Stack-spezifisches Tooling**

- <https://peps.python.org/pep-0639/> (Python-`License-Expression`-Metadaten)
- <https://www.npmjs.com/package/license-checker-rseidelsohn> (Node)
- <https://github.com/google/go-licenses> (Go; dokumentierte Nicht-Go- und URL-Auflösungs-Grenzen)
- <https://oss-review-toolkit.org/ort/docs/tools/reporter> (ORT-NOTICE-Templates, der verifizierte stack-übergreifende Attribution-Default)
- <https://www.deepbits.com/blog/BreakingDownTheAccuracyOfSBOMGenerators> (die untersuchte und widerlegte Metadata-vs-Build-SBOM-Genauigkeits-Behauptung)
