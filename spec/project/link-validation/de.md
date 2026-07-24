# Link-Validierung

Status: draft

## Kontext
Dokumentation ist nur so vertrauenswürdig wie ihre Links. Ein Portfolio-Repository liefert MkDocs-Dokumentation aus, die auf drei Arten verlinkt: intern, mit relativen Markdown-Links zwischen Seiten (`](../guide/install.md)`); über den Repository-Baum hinweg, in Roots, die die Docs referenzieren (`spec/`, `src/`, `scripts/`, …); und nach außen, ins offene Web (`https://…`). Jeder dieser Links rottet. Eine Seite wird umbenannt und der relative Link liefert 404 beim Build-aber-nicht-strict; ein Script wird gelöscht und die Doku zeigt immer noch darauf; ein Upstream-Blogpost zieht um, ein Hersteller stellt eine Produktseite ein, der Branch eines GitHub-Permalinks wird per Force-Push entfernt. Der Leser läuft in eine Sackgasse, und das Vertrauen in den gesamten Dokumentenbestand erodiert.

Das Portfolio besitzt einen Teil dieser Fläche bereits, aber nicht den deterministischen, gatenden Teil. `spec/project/docs-freshness/` auditiert Interner-Link-Rot und Cross-Tree-Referenz-Rot als zwei von elf Drift-Kategorien, tut das aber über einen LLM-Agent (`agents/docs-freshness-checker.md`), der quartalsweise und pre-release läuft, per Design read-only ist, **nicht unbeaufsichtigt in CI laufen kann** und die Prüfung externer Links explizit zum Nicht-Ziel erklärt. Der CI-Workflow sagt es ausdrücklich: die Interner-Link-Schicht ist *„bewusst auf den quartalsweisen / pre-release-Agent-Lauf aufgeschoben … Promote to a real paths-filtered job once a deterministic link-rot detector ships under `scripts/`."* Genau diesen Detektor definiert diese Spec.

Diese Spec besitzt **Link-Validität als deterministische, maschinenprüfbare Praxis**: einen stdlib-only-Checker unter `scripts/`, der interne und Cross-Tree-Links gegen den Arbeitsbaum auflöst und externe URLs über HTTP probt, eine dünne Gating-Schicht, die die Offline-Schicht (intern + cross-tree) in CI und das Quality-Gate verdrahtet, und einen read-only-Agent, der die vernetzte (externe) Schicht als periodisches und pre-release-Audit läuft. Das Ziel ist unverblümt: **keine toten Links in der Dokumentation.** Sie ergänzt `docs-freshness` (das die nicht-deterministischen Drift-Kategorien behält — Parität, ADR-Hygiene, Stale-Marker, Mermaid-Drift), statt es zu ersetzen, und sie ergänzt `prose-style`/`prose-vale-curator` (Prosa-Korrektheit) und `mkdocs build --strict` (Rendering), indem sie die eine Fläche besetzt, die keines davon gatet: ob das Ziel eines Links tatsächlich auflöst.

Leser: Autoren von `scripts/check_links.py`, der CI- und Quality-Gate-Verdrahtung und des `link-rot-scanner`-Agents, die diese Praxis operationalisieren, sowie Reviewer und Doku-Autoren, die sich darauf verlassen, dass keine toten Links nach `develop` gelangen.

## Ziele
- Jedes Repository mit Dokumentation kann jeden internen, Cross-Tree- und externen Link mit einem einzigen deterministischen Befehl validieren, und dieser Befehl ist die Quelle der Wahrheit für „ist dieser Link tot?"
- Die Offline-Schicht (interne + Cross-Tree-Links) läuft unbeaufsichtigt als blockierender CI-Gate bei Dokumentationsänderungen und innerhalb des aggregierten Quality-Gates, sodass tote interne Links nie gemergt werden
- Die Online-Schicht (externe Links) läuft als read-only, netz-toleranter Audit an dokumentierten Kadenzen, so klassifiziert, dass Flakiness (Timeouts, transiente 5xx, Rate-Limit-Antworten) sich nie als Link-Rot tarnt
- Befunde werden nach einer geteilten Schweregrad-Skala klassifiziert und in einer deterministischen, greppbaren Form emittiert, sodass sowohl Menschen als auch die Verdrahtungsschicht sie gleich konsumieren
- Der Checker definiert nicht nur, was als **tot** zählt, sondern was als **gesunder, hilfreicher Link** zählt, sodass Autoren ein positives Ziel statt nur ein Fehlersignal erhalten
- Die Praxis ist klar abgegrenzt gegen `docs-freshness`, `prose-style` und den MkDocs-Build — jedes Anliegen besetzt seine eigene Fläche, ohne doppelten Gate und ohne stille Abdeckungslücke

## Nicht-Ziele
- Die Nicht-Link-Drift-Kategorien neu zu implementieren, die `spec/project/docs-freshness/` besitzt: Sprach-Parität, Inhalts-Staleness-Deltas, Mermaid-Diagramm-Quell-Drift, ADR-Index- und Status-Hygiene, Stale-Marker, Track-/Content-Mode-Frontmatter. Diese Spec besitzt nur die Link-Auflösungs-Schicht; `docs-freshness` behält den Rest und delegiert die Link-Schicht hierher (siehe §Abgrenzung)
- Prosa-Linting, Vokabular oder die *Wortwahl*-Qualität von Anker-Text: das ist `spec/project/prose-style/` + `prose-vale-curator`. Diese Spec prüft, ob der Link *auflöst* und ob seine *Form* gesund ist, nicht ob der umgebende Satz gut liest
- Rendering-Validierung: `mkdocs build --strict` ist die autoritative Prüfung, dass die Site baut; dieser Checker läuft gegen Markdown-Quellen, vor und unabhängig vom Rendering
- Links zu reparieren: der Checker und der Agent sind read-only. Einen toten Link zu reparieren, eine Ersatz-URL zu wählen oder ein Zitat zu archivieren ist ein bewusster, separater Autorenschafts-Schritt (siehe §Read-only-Disziplin)
- Link-Shortener-Expansion, Archivierungs-Snapshotting (z. B. automatisches Einreichen bei web.archive.org) oder Content-Diffing einer entfernten Seite, um „die Seite existiert noch, aber der Abschnitt ist umgezogen" zu erkennen — das ist wertvoll, aber außerhalb des Geltungsbereichs der ersten Iteration; §Offene Fragen verfolgt die Archivierungs-Frage
- Links innerhalb von Quellcode, Code-Kommentaren oder Nicht-Dokumentations-Dateien zu validieren. Der Geltungsbereich ist die Dokumentations-Fläche (siehe §Geltungsbereich); ein Repository **DARF** den Bereich erweitern, aber die Untergrenze ist die Doku

## Anforderungen

### Geltungsbereich
- **MUSS** jede Markdown-Datei unter dem in `mkdocs.yml` konfigurierten MkDocs-`docs_dir` einschließen. Wenn keine `mkdocs.yml` existiert, fällt der Geltungsbereich auf jede getrackte `*.md`-Datei im Repository zurück, außer denen unter ignorierten Roots (`.git/`, `node_modules/`, `.audits/`, vendored Bäume)
- **MUSS** die hand-gepflegte Top-Level-Markdown des Repositorys (`README.md`, `CLAUDE.md` und jede andere getrackte Root-Level-`*.md`) in die **internen und Cross-Tree**-Link-Prüfungen einschließen, weil diese Dateien nach `docs/`, `spec/` und `scripts/` verlinken und genauso rotten
- **MUSS** diese Link-Formen in jeder in-scope-Datei extrahieren und klassifizieren:
  - Inline-Links `[text](target)` und Autolinks `<https://…>`
  - Referenzstil-Links `[text][id]` mit ihren `[id]: target`-Definitionen
  - bare URLs, die Markdown-Renderer autolinken, wenn der Renderer des Repositorys auf Autolinking konfiguriert ist
  - Bildquellen `![alt](target)` — ein gebrochenes Bild ist ein gebrochener Link
  - HTML-`href`/`src`-Attribute, eingebettet in Markdown, wenn vorhanden
- **DARF NICHT** umfasste oder Inline-**Code-Spans** als Link-Quellen behandeln — eine URL innerhalb eines Code-Blocks ist ein Beispiel, kein lebender Link
- **DARF** einen Lauf auf eine einzelne Klasse einschränken (nur intern, nur extern, nur cross-tree) auf Anfrage; die Einschränkung **MUSS** in jedem persistierten Artefakt festgehalten werden (§Audit-Artefakt)

### Link-Klassifikation
Der Checker **MUSS** jeden extrahierten Link in genau eine Klasse klassifizieren, weil sich Auflösungsmethode und Gating-Politik je Klasse unterscheiden:

- **Interner Link**: ein relativer Pfad, der auf eine andere In-Repo-Dokumentationsdatei auflöst (`./`, `../` oder repo-relativ), optional mit einem `#anchor`-Fragment. Offline gegen den Arbeitsbaum aufgelöst.
- **Intra-Page-Anker**: ein fragment-nur-Link (`#section`) in dieselbe Datei. Offline gegen die eigenen Überschriften der Datei aufgelöst.
- **Cross-Tree-Referenz**: ein relativer oder repo-relativer Link aus einer Doku in einen Nicht-Doku-Repo-Root (`spec/`, `src/`, `scripts/`, `docker/`, `helm/`, `tests/`, `tools/`, …). Offline gegen den Arbeitsbaum aufgelöst.
- **Externer Link**: eine absolute `http://`- oder `https://`-URL. Online über einen HTTP-Probe aufgelöst.
- **Nicht-HTTP-Schema**: `mailto:`, `tel:`, `ftp:`, `irc:`, eigene Schemata. Nicht auf Lebendigkeit geprobt; nur auf Wohlgeformtheit geprüft, und `mailto:`/`tel:` werden gegen ein syntaktisches Muster validiert (§Gesunde Links).

### Was als toter Link zählt
- **Interner Link / Cross-Tree-Referenz**: tot, wenn der Zielpfad im Arbeitsbaum nicht existiert. Pfadauflösung ist case-sensitive und respektiert den OS-Pfadtrenner, normalisiert auf `/`.
- **Intra-Page-Anker und interner `#anchor`**: dass die **Datei** existiert, ist eine `MUSS`-Prüfung; dass der **Anker** innerhalb der Zieldatei auflöst, ist eine `MUSS`-Prüfung, aufgelöst gegen den GitHub-Flavored-Markdown- / `mkdocs-material`-Slugifizierungs-Algorithmus (lowercase, Leerzeichen→`-`, Interpunktion strippen, mit numerischen Suffixen deduplizieren). Anker-Auflösung war eine `SOLLTE`-Prüfung, solange Themes variierten; da `spec/project/mkdocs-structure/` nun `mkdocs-material` portfolioweit vorschreibt, ist der Slug-Algorithmus einzig und bekannt, sodass die Anker-Auflösung hier eine `MUSS`-Prüfung ist. Ein explizit autoriertes `{#custom-anchor}`-Attribut **MUSS** über dem abgeleiteten Slug honoriert werden.
- **Externer Link**: klassifiziert anhand der HTTP-Antwort auf eine Anfrage, die `HEAD` bevorzugt und auf `GET` zurückfällt, wenn `HEAD` nicht erlaubt ist (`405`/`501`) oder einen mehrdeutigen Status zurückgibt:
  - **tot** (critical): finaler Status `404`, `410` oder ein DNS-Auflösungs- / Connection-refused-Fehler, der sich über alle Retries reproduziert
  - **tot** (critical): `400`, `401`, `403` **nur**, wenn sie sich beim `GET`-Fallback reproduzieren und der Host nicht auf der Known-Soft-403-Liste steht (manche Hosts, z. B. bestimmte CDNs und `linkedin.com`, geben `403`/`999` an automatisierte Agenten zurück, obwohl die Seite für Menschen lebt) — andernfalls als **unverifizierbar** (info) klassifiziert, nie als bestehender Link
  - **rate-limited** (warning, nie failend): `429` oder `403`/`999` von einem bekannt-bot-feindlichen Host; der Link wird als lebend angenommen, der Report hält fest, dass er nicht bestätigt werden konnte
  - **transient** (warning, nie failend): `5xx`, Request-Timeout oder TLS-Fehler, der sich über Retries reproduziert; als lebend angenommen, zum Re-Check markiert, **DARF NICHT** einen offline-fähigen Gate failen
  - **redirect-stale** (warning): ein permanenter Redirect (`301`/`308`), dessen finales Ziel von der angefragten URL abweicht; der Link funktioniert, **SOLLTE** aber auf das kanonische Ziel aktualisiert werden. Ein temporärer Redirect (`302`/`303`/`307`) ist **gesund**, nicht markiert
  - **gesund**: finaler Status `2xx`
- **DARF NICHT** einen Timeout, ein transientes `5xx` oder eine Rate-Limit-Antwort als `tot` klassifizieren. Netz-Flakiness ist höchstens ein `warning`; nur ein reproduzierender `404`/`410`/DNS-Fehler (oder ein reproduzierender harter `4xx` außerhalb der Soft-Liste) ist Link-Rot

### Gesunde, hilfreiche Links
Über „nicht tot" hinaus **MUSS** der Checker Link-*Qualität* bewerten und `info`-Schweregrad-Befunde emittieren (die nie einen Gate failen), wenn ein lebender Link dennoch schlecht ist. Ein gesunder Link:

- **Löst auf** — die nicht verhandelbare Untergrenze (oben)
- **Bevorzugt `https://` über `http://`** bei externen Links, wo der Host HTTPS bedient; ein bloßes `http://` zu einem HTTPS-fähigen Host ist ein `info`-Befund
- **Zeigt auf ein stabiles, kanonisches Ziel**: bevorzuge ein Release-Tag oder einen commit-gepinnten Permalink über eine bewegliche Branch-Referenz bei Source-Host-Links (`github.com/…/blob/main/…` → zugunsten eines Tag-/Commit-Permalinks markieren für Zitate, die dauerhaft sein sollen); bevorzuge das kanonische Ziel eines permanenten Redirects über die umleitende URL (das `redirect-stale`-Warning oben)
- **Ist kein lokaler oder nicht-portabler Host**: `localhost`, `127.0.0.1`, `0.0.0.0`, Private-Range-IPs oder `file://`-URLs in ausgelieferter Dokumentation sind `warning`-Befunde — sie funktionieren für den Autor und sonst niemanden
- **Trägt aussagekräftigen Anker-Text**: ein Link, dessen sichtbarer Text eine bloße URL, `here`, `click here`, `this`, `link` oder `→` ist, ist ein `info`-Befund (Barrierefreiheit + Hilfreichheit); dies ist die eine Qualitätsprüfung, die Anker-*Text* berührt, eng auf das Klick-Ziel-Wort begrenzt, sodass sie nicht mit `prose-style` überlappt
- **Ist keine tracking-belastete URL**: eine externe URL, die `utm_*`-, `fbclid`-, `gclid`- oder Session-ID-Query-Parameter trägt, ist ein `info`-Befund — auf die kanonische URL strippen
- **Löst ihr Fragment auf**: ein externer Link mit einem `#anchor` wird auf Auflösung geprüft, nur wenn die Antwort HTML und günstig parsebar ist; andernfalls wird das Fragment nicht validiert (als nicht-geprüft festgehalten, nicht als Befund)

Diese Qualitäts-Befunde sind beratend: sie schärfen, worauf Autoren zielen sollten, und **DÜRFEN NICHT** allein einen CI-Gate oder das Quality-Gate failen.

### Der deterministische Checker (`scripts/`)
- **MUSS** als einzelnes stdlib-only-Python-Script unter `scripts/` ausgeliefert werden (Referenzname `scripts/check_links.py`), ohne Drittanbieter-Laufzeitabhängigkeit, konsistent mit den anderen Validatoren in diesem Verzeichnis (`validate_skills.py`, `readability_lix.py`)
- **MUSS** diese Exit-Codes bereitstellen, passend zur Portfolio-Validator-Konvention:
  - `0` — kein Befund auf oder über der konfigurierten failenden Schweregrad-Untergrenze (Standard: `critical`)
  - `1` — mindestens ein Befund auf oder über der failenden Untergrenze
  - `2` — interner Fehler (eine Datei unlesbar, `mkdocs.yml` unparsebar usw.); nie verwechselt mit „Links sind tot"
- **MUSS** einen Befund pro Zeile emittieren, präfigiert mit dem Schweregrad in Title Case (`Critical`, `Warning`, `Info`), sodass nachgelagerte Tools deterministisch greppen; jede Zeile **MUSS** die Quelldatei, die Quell-Zeilennummer, das Link-Ziel, die Klasse und einen Ein-Phrasen-Grund tragen
- **MUSS** einen maschinenlesbaren Ausgabemodus (`--format json`) unterstützen, der die volle Befundliste plus eine per-Klasse-, per-Schweregrad-Zähl-Zusammenfassung emittiert, sodass der Agent und jeder CI-Annotations-Schritt strukturierte Daten konsumieren statt Prosa neu zu parsen
- **MUSS** `--offline` unterstützen, das **nur** die internen, Intra-Page-Anker- und Cross-Tree-Klassen läuft und nie das Netz berührt — dies ist der Modus, den CI und das Quality-Gate laufen
- **MUSS** Einschränkungs-Flags (`--internal`, `--external`, `--cross-tree`) und ein Pfad-/Ziel-Argument unterstützen, sodass eine aufrufende Person einen Lauf scopen kann; ohne Scoping prüft er den vollen §Geltungsbereich-Satz
- **MUSS** im Offline-Modus deterministisch sein: derselbe Arbeitsbaum liefert byte-identische Ausgabe, sodass ein `git diff --exit-code`-artiger Gate möglich ist und CI-Fehlschläge reproduzierbar sind
- **MUSS** seine Konfiguration (Ignore-Liste, Soft-403-Hosts, Timeout, Retries, Concurrency, failende Schweregrad-Untergrenze) aus einer einzelnen optionalen Repo-Root-Konfigurationsdatei lesen (Referenzname `.linkcheck.toml`, geparst mit stdlib-`tomllib`); ohne die Datei greifen dokumentierte Defaults
- **SOLLTE**, wenn innerhalb eines verteilten Claude-Code-Plugins/-Skills gebündelt, über `${CLAUDE_PLUGIN_ROOT}` aufgerufen werden, sodass es in Consumer-Repositories auflöst (gemäß der bundled-script-Konvention, die für `image_generate.py` etabliert wurde)

### Externer-Probe-Disziplin
- **MUSS** einen Pro-Request-Timeout anwenden (Standard 10 s) und einen begrenzten Retry mit Backoff (Standard 2 Retries), bevor ein externer Link als `transient` klassifiziert wird
- **MUSS** Concurrency begrenzen und pro Host drosseln (Standard: globale Concurrency 8, pro Host nicht mehr als 2 gleichzeitig und eine kleine Inter-Request-Verzögerung), um selbstverschuldetes Rate-Limiting zu vermeiden und ein guter Netz-Bürger zu sein
- **MUSS** einen beschreibenden, ehrlichen `User-Agent` senden, der den Checker identifiziert; **DARF NICHT** einen Browser spoofen, um Bot-Erkennung zu besiegen (ein Host, der Bots blockiert, liefert `unverifizierbar`/`rate-limited`, keinen gefälschten Erfolg)
- **MUSS** einen Ignore-/Allowlist-Mechanismus unterstützen, sodass bekannt-flakige oder auth-gemauerte URLs einmal festgehalten und von failender Klassifikation ausgeschlossen werden: sowohl eine Konfigurationsdatei-Glob-Liste als auch einen Inline-`<!-- linkcheck-ignore -->`- / `<!-- linkcheck-ignore-next-line -->`-Marker in der Markdown. Jeder Ignore-Eintrag **SOLLTE** einen Grund tragen; der Report listet, was ignoriert wurde, sodass die Unterdrückung nie still ist
- **DARF** externe Ergebnisse für eine kurze, konfigurierbare TTL (Standard 24 h) unter `.audits/link-validation/.cache/` cachen, sodass wiederholte Läufe in einem Release-Fenster nicht jede URL neu proben; der Cache **MUSS** ignorierbar sein (`--no-cache`) und **DARF NICHT** committet werden
- **DARF NICHT** einer Redirect-Kette über eine begrenzte Länge hinaus folgen (Standard 5 Hops); eine längere Kette ist ein `warning`

### Schweregrad-Klassifikation
- **MUSS** diese Skala übernehmen, ausgerichtet auf `docs-freshness` §Schweregrad, sodass ein toter Link über die beiden Audits hinweg identisch behandelt wird:
  - **critical** (Reaktionsfenster: vor Merge / vor dem nächsten Release): Interner-Link-Rot, Intra-Page- oder interner `#anchor`, der nicht auflöst, Cross-Tree-Referenz-Rot, externer `404`/`410`/DNS-Fehler, reproduzierender harter `4xx` außerhalb der Soft-Liste
  - **warning** (Reaktionsfenster: innerhalb des laufenden Quartals): externer `transient` (5xx/Timeout/TLS), `rate-limited`, `redirect-stale`, zu lange Redirect-Kette, `localhost`/Private-Host/`file://`-Link, `unverifizierbarer` harter `4xx` auf der Soft-Liste
  - **info** (best effort): `http://`-zu-HTTPS-fähigem-Host, nicht-kanonischer/Branch-Ref-Permalink für ein dauerhaftes Zitat, schwacher Anker-Text, Tracking-Parameter-URL, nicht aufgelöstes externes Fragment
- **DARF NICHT** einen Schweregrad allein auf lokales Urteil herabstufen; eine Unstimmigkeit wird als expliziter Ignore-Listen-Eintrag mit Grund festgehalten, nicht als stille Neuklassifikation

### Trigger, Kadenz und Gating
- **Offline-Schicht (intern + Intra-Page-Anker + cross-tree)** — deterministisch, kein Netz:
  - **MUSS** als blockierender CI-Gate (`--offline`) bei jedem PR laufen; ein `critical`-Befund failt den Build. Der deterministische Offline-Lauf ist sub-sekunden, läuft also unkonditioniert statt paths-gefiltert — das ist nicht nur einfacher, sondern korrekter: ein nur-`docs/`-Pfadfilter würde den gefährlichsten Fall verpassen, einen PR, der eine Datei unter einem referenzierten Root (`spec/`, `scripts/`, …) umbenennt und so einen Doku-Link bricht, ohne eine `docs/`-Datei zu berühren. Ein Repository **DARF** einen Pfadfilter hinzufügen, wenn CI-Minuten wirklich knapp sind, und akzeptiert damit diese Lücke
  - **MUSS** vom aggregierten Quality-Gate (`task check` / `task lint`) gemäß `spec/project/quality-gate/` erreichbar sein, sodass ein lokaler Lauf tote interne Links vor dem Push fängt
  - **SOLLTE** mindestens einmal pro Release auf dem vollen Satz laufen (nicht nur geänderte Dateien), um Rot zu fangen, das durch ein *Verschieben* in einer Datei eingeführt wurde, die der PR nicht berührt hat
- **Online-Schicht (extern)** — netzabhängig, standardmäßig nie der blockierende PR-Gate:
  - **MUSS** vor jedem Release-Tag laufen, der Dokumentationsänderungen seit dem vorherigen Lauf enthält, und **MUSS** mindestens einmal pro Kalenderquartal laufen
  - **DARF** als **nicht-blockierender, geplanter** CI-Job laufen (z. B. wöchentlich `workflow_dispatch`/`schedule`), dessen Fehlschlag ein Tracking-Issue öffnet oder aktualisiert, statt einen Merge zu blockieren — pro Repository gewählt (§Offene Fragen hält den Default fest)
  - **DARF NICHT** als erforderlicher, merge-blockierender Status-Check verdrahtet werden, weil externe Flakiness den Gate nicht-deterministisch machen und Vertrauen in CI erodieren würde

### Read-only-Disziplin
- Der Checker und der Agent **MÜSSEN** read-only sein: sie melden Befunde; einen Link zu reparieren ist ein separater, opt-in-Autorenschafts-Schritt
- **DARF NICHT** eine in-scope-Datei modifizieren, erzeugen oder löschen — nicht einmal, um einen offensichtlichen Tippfehler in einem Link zu „reparieren" oder einen Tracking-Parameter zu strippen
- Der Agent **DARF NICHT** das Netz über die externen HTTP-Probes hinaus berühren, die der Lauf erfordert, und **DARF NICHT** irgendeine URL an einen Drittanbieter-Archivierungs- oder Analyse-Dienst einreichen
- Die einzigen Dateien, die die Praxis schreiben darf, sind ihr eigener Cache (unter `.audits/link-validation/.cache/`, uncommittet) und ihr Audit-Artefakt (unten)

### Audit-Artefakt
- **MUSS** jedes volle Online-(externe-)Audit unter der Portfolio-Audit-Trail-Konvention `.audits/link-validation/<YYYY>-Q<n>.md` persistieren (oder `<YYYY-MM-DD>.md` für einen Ad-hoc-/Pre-Release-Lauf), passend zum `.audits/<topic>/`-Muster, und **MUSS** außerhalb des MkDocs-`docs_dir` liegen, sodass das Audit nie seine eigenen Artefakte selbst scannt
- **MUSS** im Artefakt festhalten: Datum, Trigger (quartalsweise / pre-release / scheduled / manuell), den verwendeten Repo-Root und `mkdocs.yml`-Pfad, welche Klassen gelaufen (oder herausgenommen) wurden, die auditierte Git-Revision, die Per-Klasse-/Per-Schweregrad-Zählungen, die volle nach Schweregrad sortierte Befundliste und die volle angewendete Ignore-Liste (Ziel + Grund)
- **MUSS** Per-Klasse-Auflistungen im Artefakt auf 15 Einträge begrenzen und den Rest mit einer Zählung zusammenfassen, sodass große Rot-Cluster den Report nicht fluten
- Die Offline-CI-Schicht persistiert **kein** Artefakt (ihre Ausgabe ist das Build-Log und die failende Annotation); nur das Online-Audit produziert ein committetes Artefakt
- **SOLLTE** `spec/project/parallel-working-copies/` §Audit-Artefakte in mehreren Worktrees konsultieren, wenn das Audit innerhalb eines Worktrees statt im primären Checkout läuft

### Abgrenzung
- **MUSS** der einzige Eigentümer deterministischer Link-Auflösung bleiben. `spec/project/docs-freshness/` **MUSS** seine Kategorien `Interner-Link-Rot` und `Cross-Tree-Referenz-Rot` an diesen Checker delegieren, statt sie neu zu detektieren: der `docs-freshness-checker`-Agent ruft entweder `scripts/check_links.py --offline` auf oder zitiert diese Spec als Autorität für diese beiden Kategorien, und behält die alleinige Eigentümerschaft an Sprach-Parität, Inhalts-Staleness, Mermaid-Drift, ADR-Index-/Status-Hygiene, Stale-Markern und Track-/Content-Mode-Frontmatter
- **MUSS** getrennt bleiben von `spec/project/prose-style/` und `prose-vale-curator`: Vale besitzt Prosa und Vokabular; dieser Checker besitzt Link-Auflösung und Link-Form. Der eine Überlappungspunkt — schwacher Anker-*Text* (`here`, `click here`) — wird hier als Link-Qualitäts-`info`-Befund besessen, eng auf das Klick-Ziel-Wort begrenzt, und **DARF NICHT** als Vale-Regel dupliziert werden
- **MUSS** getrennt bleiben von `mkdocs build --strict`: der Build ist die Rendering-Prüfung; dieser Checker löst Link-Ziele gegen Quellen auf, unabhängig von und vor dem Rendering
- **DARF NICHT** der Ort sein, an dem die On-Disk-MkDocs-Form, das Theme oder die Nav deklariert werden — das ist `spec/project/mkdocs-structure/`; dieser Checker liest `mkdocs.yml` nur, um `docs_dir` zu erkennen

## Akzeptanzkriterien
- [ ] Ein einzelner deterministischer Befehl (`scripts/check_links.py`) validiert interne, Intra-Page-Anker-, Cross-Tree- und externe Links über die Dokumentations-Fläche, mit Exit-Codes `0`/`1`/`2` und einem schweregrad-präfigierten Befund pro Zeile, plus einem `--format json`-Modus
- [ ] `--offline` läuft die internen + Intra-Page-Anker- + Cross-Tree-Klassen mit null Netzzugriff und byte-identischer Ausgabe für einen unveränderten Baum
- [ ] Ein CI-Job läuft die Offline-Schicht bei jedem PR und failt den Build bei jedem `critical`-Befund; derselbe Offline-Lauf ist von `task check` (über `task check:links`) gemäß `spec/project/quality-gate/` erreichbar
- [ ] Die externe Schicht läuft an den dokumentierten Kadenzen (pro Release mit Doku-Änderungen; mindestens quartalsweise), wird nie als erforderlicher merge-blockierender Check verdrahtet und klassifiziert Timeouts/transiente-5xx/Rate-Limits als `warning` (nie `critical`)
- [ ] Kein externer Link wird bei einer einzelnen transienten Antwort als `tot` gemeldet; ein `404`/`410`/DNS-Fehler ist nur `critical`, nachdem er sich über die konfigurierten Retries reproduziert hat (und ein harter `4xx` nur außerhalb der Soft-403-Liste)
- [ ] Der Ignore-Mechanismus (Config-Glob-Liste + Inline-`<!-- linkcheck-ignore -->`-Marker) unterdrückt bekannt-flakige/auth-gemauerte URLs, jede Unterdrückung trägt einen Grund, und der Report listet, was ignoriert wurde — keine stille Unterdrückung
- [ ] Link-Qualitäts-Befunde (`http`-vs-`https`, nicht-kanonischer Permalink, lokaler Host, schwacher Anker-Text, Tracking-Parameter, nicht aufgelöstes Fragment) werden bei `info` emittiert und failen nie einen Gate
- [ ] Jedes volle externe Audit wird unter `.audits/link-validation/` persistiert und hält Datum, Trigger, Repo-Root, `mkdocs.yml`-Pfad, gelaufene Klassen, Git-Revision, Per-Klasse-/Schweregrad-Zählungen, die sortierte Befundliste und die angewendete Ignore-Liste fest; Per-Klasse-Auflistungen sind auf 15 mit einer Rest-Zählung begrenzt
- [ ] `spec/project/docs-freshness/` referenziert diese Spec als Eigentümer ihrer Kategorien `Interner-Link-Rot` und `Cross-Tree-Referenz-Rot`, und der `docs-freshness-checker`-Agent detektiert sie nicht mehr eigenständig neu; der Agent `agents/link-rot-scanner.md` produziert Ausgabe, die 1-zu-1 auf die hier deklarierten Klassen und Schweregrade abbildet
- [ ] Der Checker und der Agent sind in der Praxis read-only: keine in-scope-Datei wird durch einen Lauf modifiziert, erzeugt oder gelöscht, und keine URL wird an einen Drittanbieter-Dienst eingereicht

## Offene Fragen
- [ ] **Default für geplanten externen CI-Job.** Soll der nicht-blockierende externe-Link-CI-Job ein portfolioweiter Default sein (wöchentliches `schedule`, das bei neuem Rot ein Tracking-Issue öffnet) oder pro Repository opt-in? Provisorischer Default: opt-in, mit dem quartalsweisen + pre-release-Agent-Lauf als Untergrenze; erneut prüfen, sobald ein Repository den geplanten Job zwei Quartale gelaufen hat und wir Issue-Lärm vs. gefangenes Rot messen können.
- [ ] **Archivierung toter externer Zitate.** Wenn ein externes Zitat `404`/`410` wird, soll die Praxis anbieten, einen Wayback-Machine-Snapshot nachzuschlagen und die archivierte URL als Ersatz vorzuschlagen? Provisorischer Default: außerhalb des Geltungsbereichs der ersten Iteration (das Audit meldet das tote Zitat; der Ersatz ist eine manuelle Autorenschafts-Entscheidung); erneut prüfen, falls tote-Zitat-Befunde eine wiederkehrende, hochvolumige Artefakt-Zeile werden.
- [ ] **Ort der Soft-403-Hostliste.** Soll die bekannt-bot-feindliche Hostliste (`linkedin.com`, bestimmte CDNs) in den Checker-Defaults dieses Repos, in der per-Repo-`.linkcheck.toml` oder aus einer geteilten Upstream-Liste bezogen liegen? Provisorischer Default: eine kleine eingebaute Default-Liste im Checker plus per-Repo-Erweiterung über `.linkcheck.toml`; erneut prüfen, falls die Liste über eine wartbare Handvoll hinauswächst oder pro Repository stark divergiert.
