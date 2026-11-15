# Boot-Verifikation von Images

Status: draft
Portfolio-Scope: local

## Kontext

Eine Image-Definition kann jede statische Prüfung aus `spec/project/linux-image-best-practices/` bestehen und trotzdem nicht booten: ein fehlender Treiber in der Initial-RAM-Disk, eine Partition, die der Bootloader nicht findet, eine Health-Unit, die nie startet, oder ein Rollback-Pfad, der verdrahtet ist, aber nie auslöst. Der einzige Nachweis, dass ein Image bootet, ist, es zu booten. Diese Spec regelt diesen Nachweis: ein gebautes Image in einer virtuellen Maschine mit echter UEFI-Firmware starten, auf den eigenen Health-Report des Images warten, prüfen, was er meldet, und bei einem im Feld aktualisierten Image den Update-und-Rollback-Pfad durchspielen.

Boot-Verifikation ist eine **Realisierung der End-to-End-Stufe** aus `spec/project/test-pyramid-foundation/`, keine siebte Stufe. Die funktionale Stufen-Taxonomie der Foundation ist geschlossen, und ein ganzes Betriebssystem zu booten und seinen beobachtbaren Zustand zu prüfen ist genau das, was diese Stufe beschreibt. Die Foundation definiert sie als die Stufe, die „die echte nutzerseitige Oberfläche eines laufenden Systems steuert und beobachtbares Verhalten prüft“, und bei einer Appliance ist diese Oberfläche das gebootete System. Der Anforderungsdatensatz `project/requirements/nolte-linux-plugin.md` hält diese Einordnung fest (sein Punkt R4). Die Spec füllt die invariante Stufen-Form der Foundation in §A (Zweck und Scope-Grenze), §B (Isolation und Doubles), §C (Geschwindigkeit und Determinismus), §D (Ausführungsort), §E (Traceability), §K (Anti-Patterns) und §L (Referenzprofil). §F–§J ergänzen das Image-Spezifische: den Vertrag für Bereitschaft und Zustand, das Protokoll, Host-Werkzeuge und Verdikte, das Update-und-Rollback-Szenario und Timeouts.

Der Inhalt stammt aus einem Recherchelauf am 2026-11-14 über die systemd-Dokumentation (die VM-Schnittstelle, Automatic Boot Assessment, `systemd-vmspawn`), die EDK-II-OVMF-Dokumentation, die Secure-Boot-Hinweise von libvirt sowie die Boot-Smoke-Tests, die Debian und OpenEmbedded gegen ihre eigenen Images fahren.

**Abgrenzung:** `spec/project/linux-image-best-practices/` besitzt, was ein Image enthalten und deklarieren muss, einschließlich der Image-Deklaration und der Health-Report-Zeile, die diese Spec liest. Diese Spec bootet das Image nur und prüft, was es zur Laufzeit meldet. Gegenüber den Nachbarstufen: Die Static-Analysis-Stufe eines Images ist der Skill `linux-image-audit` gegen jene Spec, der nie etwas bootet; die Integration einer einzelnen Komponente mit einem echten Kollaborateur hat keine image-spezifische Stufe und bleibt bei den eigenen Tests der Komponente. `spec/project/e2e-test-automation/` besitzt E2E-Tests der Benutzeroberfläche einer Anwendung. Ihre browserspezifischen Regeln (Page Objects, Screenshots, das Selenium-Profil, das optionale Testprotokoll) gelten hier nicht, ihre Regeln zu Determinismus und Traceability gelten über die Foundation, die sie besitzt. Bietet eine Appliance eine Web-UI an, laufen deren UI-Tests unter jener Spec gegen die gebootete VM, nicht unter dieser. `spec/project/test-pyramid-foundation/` besitzt das Stufenmodell, das Test-Double-Vokabular, die Arrangement-Treue und das CI-Gating-Modell, das diese Spec anwendet.

**Leser:** die Autoren des Skills `image-boot-verify`; Maintainer image-bauender Repositories, die einen Boot-Check in ihre Pipeline einbinden; Reviewer, die beurteilen, ob ein Boot-Verdikt vertrauenswürdig ist.

## Ziele

- Für ein gebautes Image ist nachgewiesen, dass es in einen gesunden Zustand bootet, den das Image selbst meldet, nicht bloß einen Kernel startet
- Ein Lauf, der nichts verifizieren konnte, meldet genau das und wird nie mit einem Bestehen verwechselt
- Für ein im Feld aktualisiertes Image ist nachgewiesen, dass es von selbst zurückrollt, wenn ein Update ungesund hochkommt
- Jeder Lauf hinterlässt ein Protokoll, das genau benennt, auf welchem Image, welcher Firmware und welchem Host er lief, sodass ein Verdikt reproduzierbar und auditierbar ist
- Boot-Checks bleiben deterministisch: bedingungsbasierte Wartezeiten mit begrenzten Timeouts, nie feste Verzögerungen

## Non-Goals

- Statische Prüfung der Image-Definition, die `spec/project/linux-image-best-practices/` und der Skill `linux-image-audit` besitzen
- Tests der Benutzeroberfläche einer Anwendung, die auf der Appliance läuft, die `spec/project/e2e-test-automation/` besitzt
- Booten auf physischer Hardware, Hardware-in-the-Loop-Aufbauten und board-spezifische Inbetriebnahme
- Performance-Benchmarks der Bootzeit; ein Lauf protokolliert Dauern, aber diese Spec setzt kein Bootzeit-Ziel
- Flottenweiter Update-Rollout und die Serverseite von Updates

## Anforderungen

### A. Zweck und Scope-Grenze

- Eine Boot-Verifikation **MUSS** prüfen, dass das Image seinen gesunden Zustand erreicht, so wie seine eigene Health-Definition ihn meldet: Die Health-Report-Zeile des Images (`spec/project/linux-image-best-practices/` §A) sagt `status=healthy`, und der gemeldete Systemzustand ist nach §F zulässig
- Eine Boot-Verifikation **DARF NICHT** Geschäftsverhalten einer Anwendung prüfen. Das funktionale Verhalten eines Dienstes gehört in dessen eigene Teststufen; diese Spec prüft nur, was die Health-Definition des Images meldet
- Eine Boot-Verifikation löst die Eigenschaften des gebauten Images, die ein statisches Audit nicht entscheiden kann (`spec/project/linux-image-best-practices/` §J), über die Szenarien aus §I auf: das Rollback-Szenario für das Update-Verhalten und das Identitäts-Szenario für eine ins Image eingebrannte Machine-ID

### B. Isolation, Test-Doubles und Arrangement-Treue

- Das Image unter Test, der Bootloader und der Kernel **MÜSSEN** die echten Build-Artefakte sein und unverändert gebootet werden. Ein Lauf **DARF** das Image **NICHT** neu bauen, patchen oder neu signieren, damit es bootet
- Ein Lauf **MUSS** von einer Wegwerfkopie oder einem Copy-on-Write-Overlay des Images booten, sodass das Artefakt unter Test nie durch seinen eigenen Boot verändert wird
- Jedes Arrangement wird im Vokabular von `spec/project/test-pyramid-foundation/` §"Test-Double-Taxonomie" eingeordnet und an deren §"Arrangement-Treue" gemessen:
  - **Firmware**: echte UEFI-Firmware, kein Double. Sagt `boot_chain.secure_boot` der Deklaration `implemented`, **MUSS** die Firmware mit aktiviertem Secure Boot laufen und nur die eigenen öffentlichen Schlüssel des Images eingeschrieben haben; einen breiteren Schlüsselsatz einzuschreiben oder Secure Boot abzuschalten ist eine Abweichung, die der Lauf **NICHT** vornehmen **DARF**
  - **TPM**: Ein Software-TPM-Emulator **KANN** das Hardware-TPM vertreten; er ist ein Fake. Das Protokoll hält fest, dass das TPM emuliert war
  - **Update-Server**: Eine lokale Quelle, die die nächste Image-Version ausliefert, ist ein Fake des Update-Servers. Sie **MUSS** das echte Artefakt der nächsten Version ausliefern, signiert wie in Produktion
  - **Beschleunigung**: Emulation statt Hardware-Virtualisierung ist eine deklarierte Abweichung nur in der Geschwindigkeit; §H regelt sie
- Ein Lauf **SOLLTE** der VM keinen Zugang zu externen Netzen geben, es sei denn, das getestete Szenario braucht ihn

### C. Budget für Geschwindigkeit und Determinismus

- Ein einzelner Boot-Check dauert erwartungsgemäß in der Größenordnung von Minuten. Jede Wartezeit **MUSS** durch einen expliziten Timeout aus §J begrenzt sein, und der Lauf **MUSS** jeden verwendeten Timeout protokollieren
- Ein Lauf **DARF NICHT** über feste Verzögerungen (`sleep`) synchronisieren. Er wartet auf eine Bedingung: die Health-Report-Zeile oder das Ende eines begrenzten Timeouts [R3]
- Ein Lauf **DARF** ein Szenario **NICHT** stillschweigend wiederholen. Eine Wiederholung ist ein neuer Versuch, und das Protokoll hält die Versuchsnummer fest. Ein Szenario, das scheitert und dann bei einer Wiederholung besteht, **MUSS** gemäß `spec/project/test-pyramid-foundation/` §"Determinismus und Flakiness" das Flag `flaky` an seinem Verdikt tragen

### D. Ausführungsort

- Boot-Verifikation **SOLLTE** in einer eigenen Stufe oder zeitgesteuert laufen (nächtlich oder vor einem Release), nicht bei jedem Pull Request, entsprechend der Platzierung langsamer Stufen, die `spec/project/test-pyramid-foundation/` §"CI-Gating-Modell" festlegt. Ein Repository **KANN** Pull Requests daran gaten, wenn sein Risikoprofil die Laufzeit rechtfertigt
- Boot-Verifikation **MUSS** lokal über denselben Einstiegspunkt ausführbar sein, den die Pipeline nutzt, sodass sich ein roter Pipeline-Lauf auf einem Entwicklerrechner reproduzieren lässt

### E. Traceability

- Jedes Boot-Szenario **MUSS** die Anforderung oder TC-ID benennen, die es verifiziert, wie `spec/project/test-pyramid-foundation/` §"Traceability" es verlangt. Mindestens benennt das Smoke-Szenario die Health-Definition des Images, das Rollback-Szenario die Rollback-Anforderung des Images und das Identitäts-Szenario die Identitäts-Anforderung des Images (`spec/project/linux-image-best-practices/` §D)
- Das Protokoll (§G) **MUSS** diese Kennungen tragen, sodass ein Bericht ohne externe Buchführung auf Anforderungen zurückführt

### F. Bereitschaft und Zustandsprüfungen

- Ein Lauf **MUSS** die serielle Konsole der VM vom Einschalten bis zum Herunterfahren in jedem Szenario in eine Datei mitschneiden [R2]
- Ein Lauf **MUSS** die Health-Report-Zeile des Images (`spec/project/linux-image-best-practices/` §A) auf der seriellen Konsole als Bereitschaftsbedingung und als einzige Quelle der folgenden Prüfungen behandeln. Vor dem Abgleich entfernt der Lauf aus jeder mitgeschnittenen Zeile einen abschließenden Wagenrücklauf, andere Steuerzeichen und Terminal-Escape-Sequenzen. Ein Report ist eine normalisierte Zeile, die mit `IMAGE-HEALTH-REPORT` gefolgt von einem Leerzeichen beginnt; ein durch eingeschobene Konsolenausgabe zerrissener Report zählt nicht, deshalb schreibt das Image ihn in einem Schreibvorgang; eine Erwähnung dieser Zeichenkette an anderer Stelle einer Zeile, etwa in einer ausgegebenen Kernel-Kommandozeile, ist kein Report. Pro Boot wartet der Lauf auf den ersten Report, bis der Bereitschafts-Timeout aus §J abläuft
- Meldet die Zeile `status=healthy`, **MUSS** der Lauf zwei Dinge prüfen. Jede Unit in `failed_units` steht in `health.tolerated_units` der Deklaration. Und `system_state` ist `starting` (die Health-Definition steuert `boot-complete.target` noch), `running` oder `degraded`; der Wert `-` wird nur akzeptiert, wenn `health.definition.kind` der Deklaration `framework-hook` ist. `failed_units=-` bedeutet, dass keine Unit gescheitert ist. Alles andere scheitert
- Meldet die Zeile `status=unhealthy` oder erscheint vor dem Bereitschafts-Timeout kein Report, scheitert das Smoke-Szenario. Ein fehlender Report ist ein Defekt des Images, da `spec/project/linux-image-best-practices/` §A die Zeile auf einer seriellen Konsole verlangt
- Ein Lauf **MUSS** die gemeldeten Werte `image_id` und `image_version` festhalten und **MUSS** sie gegen `image.name` der Deklaration und die erwartete Version prüfen, die der Aufrufer für das Artefakt übergeben hat (§H), sodass das Protokoll belegt, welches Image tatsächlich gebootet hat
- Ein Lauf **KANN** einen Out-of-Band-Bereitschaftskanal, den Hypervisor und Image anbieten (§L), für Fortschrittsdiagnosen nutzen. Ein solcher Kanal **DARF** die Health-Report-Zeile **NICHT** als Grundlage eines Verdikts ersetzen

### G. Protokoll

- Jeder Lauf **MUSS** ein maschinenlesbares Protokoll (`protocol.json`) und das mitgeschnittene serielle Log in ein Laufverzeichnis schreiben. Der Default-Ort liegt außerhalb des getrackten Baums (git-ignoriert), wie das E2E-Testprotokoll
- Das Protokoll **MUSS** enthalten: den Zeitstempel des Laufs; den Host (Betriebssystem, Kernel, Architektur); das Image-Artefakt und seinen Digest; den Commit der Image-Definition; die gelesene Image-Deklaration; den Firmware-Build und ob Secure Boot aktiv war; ob das TPM emuliert war; den Hypervisor und seine Version; den Beschleunigungsmodus und unter Emulation die Warnung und den Timeout-Faktor; jeden verwendeten Timeout; pro Szenario sein Verdikt, das Flag `flaky`, die Versuchsnummer, die Dauer jeder Phase und die beobachteten Health-Report-Zeilen; die nach jedem Boot des Rollback-Szenarios beobachteten Image-Versionen; für jeden der beiden Boots die Machine-UUID und den Wert `machine_id_app` des Identitäts-Szenarios; bei `not-run` die fehlenden Werkzeuge oder die gescheiterte Vorbedingung und einen Installationshinweis; die abgedeckten Anforderungen oder TC-IDs; und den Pfad des seriellen Logs
- Das Protokoll **MUSS** für jedes Verdikt geschrieben werden, auch für `not-run`. Ein Feld, das der Lauf nicht erheben konnte, wird als `unavailable` mit Begründung geschrieben, nie weggelassen oder geraten

### H. Host-Werkzeuge und Verdikte

- Ein Lauf erhält als Eingabe den Pfad der Image-Deklaration, das Artefakt unter Test mit seiner erwarteten Version und dem Commit der Image-Definition, aus dem es gebaut wurde, und für das Rollback- und das positive Szenario das Artefakt der nächsten Version mit seiner erwarteten Version. Der Lauf hält diesen Commit so im Protokoll fest, wie er übergeben wurde, und setzt nie den aktuellen Commit der Arbeitskopie ein. Eine fehlende Eingabe ist eine gescheiterte Vorbedingung
- Vor dem Booten **MUSS** ein Lauf jede Vorbedingung prüfen: den Hypervisor und die UEFI-Firmware, die er auswählt; Firmware-Variablen mit eingeschriebenen Schlüsseln des Images, wenn die Deklaration `secure_boot: implemented` sagt; den TPM-Emulator, wenn die Deklaration `measured_boot: implemented` sagt; eine gültige Image-Deklaration; ein lesbares Image-Artefakt; für das Rollback-Szenario das Artefakt der nächsten Version und eine lokale Quelle, die der Gast erreicht; und für das Identitäts-Szenario einen Hypervisor, der die Machine-UUID vergeben kann
- Jedes Szenario **MUSS** mit genau einem Verdikt enden, definiert per Ausschluss:
  - `not-run`: Eine Vorbedingung ist gescheitert, die eigene Infrastruktur des Laufs ist gescheitert, bevor die Firmware an das Image übergeben hat (der Hypervisor konnte nicht starten, das Overlay ließ sich nicht anlegen, das Protokollverzeichnis ist nicht beschreibbar), oder §I nennt den Fall als `not-run` (ein fehlender Switch, ein Report ohne `machine_id_app`). In jedem Fall hat der Lauf nichts von dem verifiziert, wofür das Szenario existiert
  - `fail`: Jede Vorbedingung hielt, das Image wurde gestartet, und eine Prüfung aus §F oder §I schlug fehl oder der Bereitschafts-Timeout lief ab
  - `pass`: Jede Vorbedingung hielt, und jede Prüfung hielt
- Ein Szenario **DARF NIEMALS** `pass` zurückgeben, wenn eine Vorbedingung fehlt. Ein `not-run`-Verdikt **DARF** von keinem Gate als grüner Check gewertet werden
- Das Gesamtverdikt des Laufs ist das schlechteste Verdikt seiner Pflicht-Szenarien (das Smoke-Szenario und bei einem im Feld aktualisierten Image das Rollback-Szenario), in der Reihenfolge `fail`, `not-run`, `pass`. Ein empfohlenes Szenario (das positive und das Identitäts-Szenario) hebt das Gesamtverdikt auf `fail`, wenn es scheitert, ein `not-run` daraus wird aber gemeldet, ohne das Gesamtverdikt anzuheben. Der Lauf **MUSS** es sowohl im Protokoll als auch als Prozess-Exit-Status ausgeben: `0` für `pass` (mit oder ohne Flag `flaky`), `1` für `fail`, `2` für `not-run`
- WENN Hardware-Virtualisierung nicht verfügbar ist, DANN **KANN** der Lauf auf Emulation zurückfallen. Ein solcher Lauf gibt eine explizite Warnung in Ausgabe und Protokoll aus und skaliert jeden Timeout mit dem Emulationsfaktor aus §J. Ein Szenario, das unter Emulation hält, **KANN** `pass` zurückgeben; das Beschleunigungsfeld des Protokolls hält den schwächeren Nachweis sichtbar. Emulierte Boots auf geteilten CI-Runnern überschreiten bekanntermaßen Timeouts, die für beschleunigte Boots bemessen sind [R3]

### I. Update-und-Rollback-Szenario

- Für ein Image, dessen Deklaration `update_model: field-updated` sagt, **MUSS** die Boot-Verifikation ein Rollback-Szenario enthalten, das vollständig über die Switches gesteuert wird, die die Deklaration benennt (`spec/project/linux-image-best-practices/` §F):
  1. Version N von einer frischen Kopie booten, mit `update.source_switch` auf die lokale Quelle gesetzt, die Version N+1 ausliefert, und `health.failure_switch` auf die erwartete Version von N+1 gesetzt. Der Lauf setzt beide Werte einmal beim Start; sie bleiben über die Neustarts erhalten, die der Gast auslöst, und der Lauf startet den Hypervisor während des Szenarios nicht neu. N meldet `status=healthy`, da der Failure-Switch eine andere Version nennt
  2. Der Update-Mechanismus des Images installiert N+1 ohne weitere Eingabe und startet in N+1 neu (`spec/project/linux-image-best-practices/` §F); auf den ersten Report von N+1 warten
  3. N+1 meldet wegen des Failure-Switches `status=unhealthy` und startet selbst neu; weiter Reports lesen
  4. Prüfen, dass der erste `status=healthy`-Report nach höchstens `update.max_boot_attempts` ungesunden Reports von N+1 von Version N kommt. Dann die VM vom Host aus ausschalten; das Szenario endet dort. Das Ausschalten geschieht nach bestem Bemühen: N kann bereits erneut begonnen haben, N+1 zu installieren, was das Verdikt nicht berührt, da die Kopie verworfen wird
- Ein Lauf **DARF** N+1 **NICHT** durch Beschädigen oder Verändern des Artefakts ungesund machen, da ein beschädigtes Artefakt die Signaturprüfung des Update-Frameworks testet, nicht den Rollback-Pfad
- Ein Lauf **SOLLTE** auch das positive Szenario enthalten, als eigenen Boot von einer frischen Kopie: dieselben Schritte ohne Failure-Switch, mit der Prüfung, dass N+1 `status=healthy` meldet und nach einem weiteren Boot, den der Lauf als Reset der VM über den Hypervisor auslöst, ohne den Hypervisor-Prozess neu zu starten, noch die gemeldete Version ist
- Fehlen der Deklaration trotz `update_model: field-updated` der Block `update` oder `health.failure_switch`, ist das Rollback-Szenario `not-run` mit diesem Grund; es wird nie stillschweigend übersprungen
- Ein Lauf **SOLLTE** für jedes Image das Identitäts-Szenario enthalten: das Artefakt zweimal booten, jeweils von einer frischen Kopie, mit einer eigenen, vom Hypervisor vergebenen Machine-UUID und ohne gesetzten Failure- oder Quell-Switch, und die Werte `machine_id_app` der beiden Reports vergleichen. Jeder Boot wird an den Smoke-Prüfungen aus §F gemessen, sodass ein ungesunder oder fehlender Report das Szenario scheitern lässt. Gleiche Werte lassen es scheitern, denn das Image liefert eine feste Maschinenidentität aus (`spec/project/linux-image-best-practices/` §D). Trägt einer der Reports `machine_id_app=-`, ist das Szenario `not-run`

### J. Timeouts

- Ein Lauf **MUSS** diese Timeouts verwenden, sofern der Aufrufer keinen überschreibt; dann hält das Protokoll die Überschreibung fest. Die Defaults sind Engineering-Werte für einen beschleunigten Boot, keine kalibrierten Messungen:

  | Timeout | Default | Begrenzt |
  |---|---|---|
  | Bereitschaft | 300 s | Vom Einschalten bis zur ersten Health-Report-Zeile eines Boots |
  | Update-Installation | 600 s | Vom ersten gesunden Report von N bis zum ersten Report von N+1 |
  | Rollback | (`max_boot_attempts` + 1) × Bereitschaft | Vom ersten ungesunden Report von N+1 bis zum gesunden Report von N, über jeden Boot von N+1 und den Boot von N |
  | Gesamt | Summe der Phasen des Szenarios plus 120 s | Ein Szenario einschließlich Herunterfahren |

- Unter Emulation (§H) **MUSS** jeder Timeout mit einem Emulationsfaktor von mindestens 5 multipliziert werden, und das Protokoll hält den verwendeten Faktor fest

### K. Kanonische Anti-Patterns

- Erfolg melden, wenn der Kernel sein Banner ausgibt oder der Login-Prompt erscheint, ohne den Health-Report des Images
- Mit einem festen `sleep` warten, bevor die Konsole gelesen wird
- `pass` melden, obwohl Hypervisor, Firmware oder eine andere Vorbedingung fehlte
- Mit deaktiviertem Secure Boot oder mit einem breiteren eingeschriebenen Schlüsselsatz booten, um ein Image zu verifizieren, das Secure Boot deklariert
- Das Build-Artefakt an Ort und Stelle booten, sodass ein Schreibvorgang beim ersten Boot das später veröffentlichte Artefakt verändert
- Rollback testen, indem die Update-Payload beschädigt wird
- Eine Out-of-Band-Bereitschaftsmeldung als Beleg dafür werten, dass das Image gesund ist

### L. Referenzprofil (optional)

Dieses Profil ist ein ausgearbeiteter Default. `spec/project/test-pyramid-foundation/` §"Invariante Stufen-Form (der Meta-Vertrag)" stuft ein solches Profil zu einer Referenz herab, deshalb setzt das Profil keine Anforderung.

- Hypervisor: QEMU (`qemu-system-<arch>`) mit KVM-Beschleunigung, wo `/dev/kvm` verfügbar ist, sonst TCG-Emulation; das Image mit `-snapshot` oder über ein Copy-on-Write-Overlay eingebunden
- Firmware: EDK II OVMF. Für Secure Boot eine Firmware-Variablendatei, in der nur die Schlüssel des Images eingeschrieben sind, vorbereitet mit `virt-fw-vars`; eine vorbefüllte Vorlage einer Distribution trägt einen breiteren Schlüsselsatz und erfüllt §B nicht. Die Variablendatei muss zum Firmware-Build passen [R2], [R4]
- TPM: `swtpm`, eingebunden als emuliertes TPM-2.0-Gerät [R4]
- Konsole: `-serial file:<path>` schneidet die serielle Konsole mit [R2]
- Update-Quelle: User-Mode-Networking (`-netdev user`), unter dem der Gast eine vom Host ausgelieferte Quelle unter der Adresse erreicht, die der Hypervisor dem Host zuweist, standardmäßig `10.0.2.2` **[unverified]**
- Switches: SMBIOS-Type-11-Strings, übergeben mit `-smbios type=11,value=<key>=<value>`; ein systemd-Credential nutzt den Schlüssel `io.systemd.credential:<name>` [R1] **[unverified]**
- Machine-UUID: `-uuid <uuid>`, ein frischer Wert pro Boot des Identitäts-Szenarios
- Out-of-Band-Bereitschaft (nur Diagnose): das System-Credential `vmm.notify_socket`, über das ein systemd-Gast `READY=1` über `AF_VSOCK` meldet [R1]
- Launcher: `mkosi vm` oder `systemd-vmspawn` **KÖNNEN** eine rohe QEMU-Kommandozeile ersetzen, sofern der Lauf weiterhin §B–§J erfüllt [R5]

## Akzeptanzkriterien

Diese Kriterien fassen die obigen Anforderungen zusammen; jede Anforderung bleibt für sich normativ.

- [ ] `spec/project/image-boot-verification/` existiert mit `en.md` (kanonisch) und `de.md` (Übersetzung) und ist in `spec/README.md` gelistet, und `spec/project/test-pyramid-foundation/` nennt sie als Image-Realisierung der E2E-Stufe
- [ ] Jedes Feld der invarianten Stufen-Form der Foundation ist gefüllt: Zweck und Scope-Grenze (§A), Isolation und Doubles (§B), Geschwindigkeit und Determinismus (§C), Ausführungsort (§D), Traceability (§E), Anti-Patterns (§K) und ein optionales Referenzprofil (§L), mit festgehaltener Grenze zu den Nachbarstufen
- [ ] §B verbietet, das Artefakt neu zu bauen, zu patchen, neu zu signieren oder an Ort und Stelle zu booten, und ordnet Firmware, TPM, Update-Server und Beschleunigung mit ihren Treue-Regeln ein
- [ ] §C verbietet feste Verzögerungen und stilles Wiederholen und verlangt das Flag `flaky`
- [ ] §F macht den zeilenverankerten Health-Report auf der seriellen Konsole zur Bereitschaftsbedingung und zur einzigen Quelle der Zustandsprüfungen, akzeptiert `starting`, `running` und toleriertes `degraded` und verlangt, dass die gemeldete Identität zur Deklaration und zur erwarteten Version passt
- [ ] §G listet jedes Protokollfeld, verlangt ein Protokoll für jedes Verdikt und schreibt nicht erhobene Felder als `unavailable` mit Begründung
- [ ] §H nennt die Eingaben des Laufs, definiert `pass`, `fail` und `not-run` per Ausschluss, listet jede Vorbedingung, definiert das Gesamtverdikt als schlechtestes Verdikt der Pflicht-Szenarien, wobei ein `not-run` eines empfohlenen Szenarios es nicht anhebt, mit den Exit-Status `0`, `1` und `2` und erlaubt `pass` unter Emulation nur mit Warnung und skalierten Timeouts
- [ ] §I steuert das Rollback-Szenario nur über die beim Start einmal gesetzten deklarierten Switches, verlässt sich darauf, dass das Image selbst installiert, neu startet und zurückrollt, begrenzt es durch `max_boot_attempts`, beendet es beim gesunden Report von N, verbietet das Beschädigen des Artefakts, macht einen fehlenden Switch zu `not-run` und ergänzt das Identitäts-Szenario
- [ ] Auf einem Host ohne Hypervisor beendet sich der Skill mit Status `2` und schreibt ein Protokoll, dessen Verdikt `not-run` ist und dessen nicht erhobene Felder `unavailable` lauten
- [ ] Bei einer Deklaration mit `max_boot_attempts: 3` endet das Rollback-Szenario nach höchstens vier Boots, gezählt ab dem ersten Boot von N+1 (drei von N+1, einer von N), innerhalb des Rollback-Timeouts aus §J
- [ ] §J nennt Default-Timeouts, einen Rollback-Timeout, der den letzten Boot von N abdeckt, und den minimalen Emulationsfaktor
- [ ] Werkzeugnamen erscheinen nur im Referenzprofil (§L) und als zitierte Beispiele, nie als bindende Anforderungen

## Referenzen

- Quellen abgerufen am 2026-11-14. Quellenklassen gemäß `spec/claude/research-triangulate/` §"Quellenklassen und Unabhängigkeit": **Primary** und **Secondary**.
- [R1] systemd, "The VM Interface" (**Primary**): <https://systemd.io/VM_INTERFACE/>; Debian-Quelle von `VM_INTERFACE.md` (**Primary**): <https://sources.debian.org/src/systemd/259-1/docs/VM_INTERFACE.md>; `systemd-vmspawn(1)` (**Primary**): <https://www.freedesktop.org/software/systemd/man/261/systemd-vmspawn.html>
- [R2] EDK II, `OvmfPkg/README` (**Primary**): <https://qemu.googlesource.com/edk2/+/refs/heads/master/OvmfPkg/README>; kraxel.org, "Firmware logging" (**Secondary**): <https://www.kraxel.org/blog/2025/10/firmware-logging/>; libvirt, "Secure Boot" (**Primary**): <https://libvirt.org/kbase/secureboot.html>
- [R3] Debian-systemd-Test `boot-smoke` (**Primary**): <https://sources.debian.org/src/systemd/259-1/debian/tests/boot-smoke>; OpenEmbedded-Core-Patch zum Abfragen des Boot-Zustands (**Primary**): <https://patchwork.yoctoproject.org/project/oe-core/patch/20240104135112.490141-1-mikko.rapeli@linaro.org/>; `rpm-ostree-engine`-Issue #78 zum Ersetzen eines nackten `is-system-running --wait` durch Timeout-Logik (**Secondary**): <https://git.shivering-isles.com/os-forge/rpm-ostree-engine/-/issues/78>; Launchpad-Kommentar zu langsamen Nested-KVM-Boots (**Secondary**): <https://bugs.launchpad.net/ubuntu/+source/gnutls28/+bug/1928648/comments/13>
- [R4] `virt-fw-vars(1)` (**Primary**): <https://www.mankier.com/1/virt-fw-vars>; OpenStack-Nova-Spec, "Allow Secure Boot for QEMU- and KVM-based guests" (**Secondary**): <https://specs.openstack.org/openstack/nova-specs/specs/ussuri/approved/allow-secure-boot-for-qemu-kvm-guests.html>; Ubuntu Discourse, "Enable TPM, Secure Boot in Ubuntu 25.10 QEMU/KVM Guests" (**Secondary**): <https://discourse.ubuntu.com/t/enable-tpm-secure-boot-in-ubuntu-25-10-qemu-kvm-guests/76045>; trust|me, "Run trust|me image in QEMU/KVM" (**Secondary**): <https://trustm3.github.io/deploy/qemu>
- [R5] `systemd-vmspawn(1)` (**Primary**): <https://www.freedesktop.org/software/systemd/man/261/systemd-vmspawn.html>; `mkosi(1)` (**Primary**): <https://manpages.debian.org/testing/mkosi/mkosi.1>

**Triangulationsstand.** Die Author-Time-Stufe aus `spec/claude/research-triangulate/` §"Author-Time-Aussagen" verlangt drei unabhängige Quellen. [R2], [R3] und [R4] erfüllen sie. [R1] beruht auf einer Domain-Wurzel (systemd), [R5] auf zweien; der Schlüssel `io.systemd.credential:` aus §L ist deshalb als **[unverified]** markiert. Alles, was auf ihnen beruht, steht im optionalen Referenzprofil (§L) und ist nie Grundlage eines Verdikts: Der bindende Vertrag aus §F ist die Health-Report-Zeile, die `spec/project/linux-image-best-practices/` §A definiert, kein Hypervisor- oder Init-System-Mechanismus. [R5] belegt nicht die aktuellen Befehlsnamen der Launcher (`mkosi vm` gegenüber dem älteren `mkosi qemu`), deshalb liest eine Implementierung sie aus der gepinnten Toolchain-Version.

## Offene Fragen

- **Interaktive Implementierung** (load-bearing). Der mit dieser Spec ausgelieferte Skill `image-boot-verify` läuft interaktiv. Er liefert noch nicht die Exit-Status aus §H, den mit der Pipeline geteilten Einstiegspunkt aus §D und das Akzeptanzkriterium zum Exit-Status `2`. Ein nicht interaktiver Runner schließt die Lücke, verfolgt in #728. Bis dahin bleibt diese Spec `draft`, und Boot-Verifikation ist ein Nachweis für eine Person, kein Pipeline-Gate.

- **Architektur-Abdeckung** (parking-lot). Das Referenzprofil setzt die Architektur des Hosts voraus. Architekturübergreifende Boots (ein `aarch64`-Image auf einem `x86_64`-Host) brauchen konstruktionsbedingt Emulation und fallen unter die Emulationsregel aus §H. Ob ein solcher Nachweis für ein Release-Gate genügt, entscheidet der erste Consumer, der für eine fremde Architektur baut.
- **Kalibrieren der Timeouts** (parking-lot). Die §J-Defaults sind Engineering-Werte. Die ersten echten Läufe gegen Consumer-Images (ein Folgeschritt gemäß Punkt R10 des Anforderungsdatensatzes) sollten Bootdauern messen und sie anpassen.
