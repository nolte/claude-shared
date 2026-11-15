# Best Practices für Linux-Images

Status: draft
Portfolio-Scope: local

## Kontext

Manche Portfolio-Repositories liefern keine Anwendung aus, sondern ein ganzes Betriebssystem: ein Disk-Image, das bootet, eine Appliance, einen Embedded-Firmware-Build oder einen Container, der als Betriebssystem bootet. Die Defaults eines naiv gebauten Images sind für dieses Artefakt die falsche Haltung. Es schwimmt auf dem, was der Paket-Mirror an diesem Tag ausgeliefert hat, sodass sich zwei Builds desselben Commits unterscheiden. Es brennt eine Maschinenidentität und Host-Keys in jede Kopie ein. Es liefert die Build-Toolchain mit aus. Es hat keinen Weg zurück, wenn ein Update nicht bootet. Und niemand kann sagen, was es enthält. Diese Spec übersetzt die aktuelle Upstream-Leitlinie in eine normative Checkliste. Der Skill `linux-image-audit` setzt sie durch, der Agent `linux-image-developer` baut gegen sie, und ein Reviewer misst eine Image-Definition an ihr.

Die Spec ist **im Kern toolchain-neutral und nur in ihren Profilen toolchain-spezifisch**. Der Kern (§A–§H) nennt jede Pflicht genau einmal, unabhängig vom Build-Werkzeug. §I bildet jede Pflicht auf die fünf Familien von Build-Toolchains im Scope ab: mkosi und das systemd-Ökosystem, Yocto und Buildroot, Debian/Ubuntu-Image-Builder, NixOS und OSTree sowie bootc. §J legt fest, welche Pflichten ein statisches Audit entscheiden kann und was es meldet, wenn es das nicht kann. Jedes Image trägt eine maschinenlesbare **Image-Deklaration**, die die Fakten festhält, die weder ein Scan noch ein Boot verlässlich ableiten kann. Werkzeuge lesen die Spec und die Deklaration und erkennen die Toolchain zur Laufzeit. Es gibt keine Spec und kein Artefakt pro Toolchain. Der Anforderungsdatensatz `project/requirements/nolte-linux-plugin.md` hält diese Formentscheidung (sein Punkt R3) und die Wahl einer eigenen Deklarationsdatei mit Schema (sein Punkt R11) fest.

Der Inhalt stammt aus zwei Rechercheläufen am 2026-11-14 über die Spezifikationen der UAPI Group, die systemd-Dokumentation und -Manpages, die `SOURCE_DATE_EPOCH`-Spezifikation von reproducible-builds.org, die Dokumentation von Yocto Project und Buildroot sowie die Dokumentation von bootc, mkosi, mmdebstrap, `rpm-ostree` und den Update-Frameworks. Dass keine bestehende Spec dieses Gebiet bereits abdeckt, ist belegt durch ein `grep -rli` über `spec/**/en.md` nach `dm-verity`, `secure boot`, `systemd-repart`, `mkosi`, `yocto`, `buildroot`, `debootstrap`, `ostree`, `bootc`, `SOURCE_DATE_EPOCH` und `unified kernel image`, das am 2026-11-14 keine Datei lieferte.

**Abgrenzung:** `spec/project/dockerfile-best-practices/` besitzt den Inhalt eines `Containerfile`/`Dockerfile`. Für bootc regelt sie die Build-Datei einschließlich Pinning des Basis-Images und Geheimnissen in Schichten, und sie nimmt bootc-Images von ihrer Säule zum Nicht-Root-`USER` aus. `spec/project/artifact-signing/` besitzt Signierung und Attestierung von OCI-Artefakten. `spec/project/license-check/` besitzt die Lizenzklassifikation der SBOM. `spec/project/image-boot-verification/` besitzt den Nachweis, dass ein Image bootet, als Realisierung der E2E-Stufe aus `spec/project/test-pyramid-foundation/`. Dort werden auch die Eigenschaften eines gebauten Root-Dateisystems geprüft (§J). `spec/project/continuous-delivery/` besitzt die Auslieferungs-Pipeline um den Build herum. Diese Spec besitzt die **Image-Definition**: was ins Image kommt, wie es gepinnt ist, wie es bootet, wie es aktualisiert wird und was es über sich selbst deklariert.

**Leser:** Maintainer image-bauender Repositories; die Autoren des Skills `linux-image-audit`, des Agenten `linux-image-scanner` und des Agenten `linux-image-developer`; Reviewer, die eine Image-Definition an dieser Messlatte prüfen.

## Ziele

- Jeder Image-Build ist **aus gepinnten Eingaben reproduzierbar**: Derselbe Commit ergibt dasselbe Image, sodass sich zeigen lässt, dass ein Security-Fix nur ändert, was er ändern soll
- Jedes Image ist zur Build-Zeit **frei von maschinenspezifischer Identität und Geheimnissen**, sodass Kopien eines Images nie eine Machine-ID, Host-Keys oder Zugangsdaten teilen
- Jedes im Feld aktualisierte Image hat einen **Rollback-Pfad, der automatisch auslöst**, wenn ein Update nicht gesund hochkommt
- Jedes Image **deklariert seinen Inhalt** über eine maschinenlesbare SBOM
- Die **Boot-Kette** einer Appliance lässt sich durchgehend verifizieren (Secure Boot, UKI, dm-verity, Measured Boot), wobei jeder Schritt benannt und sein Fehlen sichtbar ist
- Dienste, die das Image ausliefert, laufen **in einer systemd-Sandbox** statt mit den vollen Rechten des Hosts
- Eine Checkliste gilt für jede Toolchain, sodass ein Auditor beim Wechsel zwischen einem Yocto-Repo und einem mkosi-Repo denselben Vertrag prüft, und ein Audit meldet nie ein Bestehen, das es nicht belegen konnte

## Non-Goals

- Kernel-Entwicklung: Kernel-Module, Kernel-Konfigurationsfragmente und Out-of-Tree-Treiber (außerhalb des MVP-Scopes des Plugins gemäß Punkt R2 des Anforderungsdatensatzes)
- Entwicklung eigenständiger Daemons oder CLI-Werkzeuge, die lediglich unter Linux laufen; diese Spec deckt deren systemd-Unit nur als Teil eines Images ab
- Mechanik der Signierung und Attestierung von OCI-Artefakten, die `spec/project/artifact-signing/` besitzt. Die Signierung und Attestierung eines Nicht-OCI-Image-Artefakts (ein rohes Disk-Image, ein Firmware-Bundle) hat noch keine zuständige Spec; diese Spec hält die Lücke in ihren Offenen Fragen fest, statt sie zu füllen
- Lizenzklassifikation und NOTICE-Erzeugung, die `spec/project/license-check/` besitzt
- Das Image auszuführen und nachzuweisen, dass es bootet, was `spec/project/image-boot-verification/` besitzt
- Flottenverwaltung, Geräte-Provisionierung und die Serverseite von Updates (die API eines Update-Servers, Rollout-Wellen, Geräteregistrierung)
- Die Wahl einer Toolchain für ein Projekt; die Spec regelt die Toolchain, die das Repository bereits verwendet

## Anforderungen

Anforderungen in einem als **Pflichtsäule** markierten Abschnitt (§C, §D, §F, §G) sind in einem Audit harte Fehler. Ein **MUSS** in jedem anderen Abschnitt wird als Warning gemeldet, ein **SOLLTE** als Suggestion. §J legt fest, wann ein Audit eine Anforderung stattdessen als `not-decidable` meldet.

### A. Image-Definition und Image-Deklaration

- **MUSS** die vollständige Image-Definition im Repository unter Versionskontrolle halten: die Build-Konfiguration, jedes Overlay oder jeden Zusatzbaum, jede Paketliste und jede Lock- oder Manifest-Datei, aus der der Build Eingaben auflöst
- **MUSS** pro Image genau eine Image-Deklaration mitliefern, eine Datei namens `image-declaration.yaml` neben der Image-Definition, die gegen `schemas/image-declaration-v1.0.schema.yaml` validiert. Die Deklaration nennt das Image und seine Toolchain, sein Update-Modell (`field-updated` oder `reflash-only`), welche Boot-Ketten-Schritte es umsetzt (§E), seine Health-Definition (§A, als Unit-Name oder Framework-Hook) und bei einem im Feld aktualisierten Image die Switches, die die Boot-Verifikation nutzt (§F)
- **MUSS** pro Image genau eine primäre Toolchain verwenden, nämlich die, die seine Deklaration nennt
- **SOLLTE** ein Image über einen einzigen, im Repository deklarierten Einstiegspunkt bauen (ein Taskfile-Target oder ein gleichwertiges Skript), sodass CI und ein Entwickler denselben Befehl ausführen
- **MUSS** jedem Image eine **Health-Definition** geben: den Punkt, an dem das Image entscheidet, dass ein Boot gesund ist. Bei einem systemd-basierten Image ist das eine Unit, die vor `boot-complete.target` eingeordnet ist; bei einem Image, dessen Update-Framework den Commit besitzt (RAUC, SWUpdate, Mender, greenboot), ist es der Health-Hook dieses Frameworks
- **MUSS** die Health-Definition, sobald sie entschieden hat, eine **Health-Report-Zeile** auf jede Konsole schreiben lassen, die das Image konfiguriert, einschließlich einer seriellen Konsole, als Zeile, die mit `IMAGE-HEALTH-REPORT` gefolgt von einem Leerzeichen beginnt, in der Form `IMAGE-HEALTH-REPORT status=<healthy|unhealthy> image_id=<id> image_version=<version> system_state=<state> failed_units=<kommagetrennte Liste oder -> machine_id_app=<id oder ->`. Die Werte `image_id` und `image_version` sind die aus `os-release` des gebooteten Systems. `system_state` ist der Zustand des Service-Managers im Moment des Reports, also `starting`, solange die Health-Definition `boot-complete.target` noch steuert; `failed_units` listet die in diesem Moment gescheiterten Units. `machine_id_app` ist die für die feste Application-ID `6dc31fbecafb40ec9395fe013ebd2c7c` abgeleitete Machine-ID (die app-spezifische Machine-ID von systemd), mit der ein Verifizierer zwei Boots vergleichen kann, ohne die rohe Machine-ID preiszugeben [R7]. Sie ist kein Geheimnis, aber ein stabiles Pseudonym des Geräts, und dient deshalb nur diesem Vergleich. Alle drei tragen echte Werte, sobald das Image systemd betreibt, auch wenn seine Health-Definition ein Framework-Hook ist, und sind nur auf einem Image ohne systemd `-`. Die Boot-Verifikation liest diese Zeile (`spec/project/image-boot-verification/` §F), sodass sich ein Image ohne interaktive Shell auf seiner Konsole verifizieren lässt

### B. Komposition und Minimierung

- **SOLLTE** nur installieren, was das Image ausführt: keine Compiler, Paketbau-Werkzeuge oder Debugger in einem Produktions-Image. Wo die Toolchain Build- und Zielumgebung trennt (Yocto, Buildroot, mkosi-Tools-Trees, mehrstufige bootc-Builds), **DARF** das Build-Werkzeug **NICHT** ins Ziel-Root-Dateisystem durchsickern
- **SOLLTE** Dokumentation, Manpages und Locales, die die Appliance nicht nutzt, ausschließen, wenn die Toolchain dafür einen Schalter bietet
- **SOLLTE** ein schreibgeschütztes Root-Dateisystem ausliefern (zum Beispiel ein durch dm-verity geschütztes `/usr`, ein OSTree-/bootc-Deployment oder ein schreibgeschütztes squashfs/erofs) und veränderlichen Zustand unter `/etc` und `/var` halten
- **KANN** die UAPI Discoverable Partitions Specification (GPT-Partitionstyp-Kennungen) nutzen, sodass `systemd-gpt-auto-generator` Root, `/var` und weitere Partitionen ohne fest kodierte `/etc/fstab` findet [R2]

### C. Reproduzierbarkeit und gepinnte Eingaben (Pflichtsäule)

- **MUSS** jede externe Eingabe auf eine unveränderliche Referenz pinnen: Paket-Repositories auf einen datierten Snapshot, Layer und Quellbäume auf einen Commit und Nix-Eingaben über eine committete Lock-Datei. Ein Build, der die neueste Version von einem Live-Mirror auflöst, ist ein harter Fehler. Für bootc regelt `spec/project/dockerfile-best-practices/` §"Base-Image-Pinning (Pflichtsäule)" das Pinning des Basis-Images (Tag plus Digest); es wird hier nicht wiederholt
- **MUSS** die Lock- oder Manifest-Datei committen, die die gepinnten Referenzen festhält, sodass der Pin in einem Pull Request überprüfbar ist
- **MUSS** dem Build ein festes `SOURCE_DATE_EPOCH` übergeben, das aus dem Quellstand abgeleitet ist (zum Beispiel dem Zeitstempel des letzten Commits), nie aus der Systemuhr, es sei denn, die Toolchain leitet es selbst aus dem Quellstand ab (§I sagt, wo). Die Semantik der Variable definiert die Spezifikation von reproducible-builds.org: Die Ausgabe soll aussehen, als sei der Build zu diesem Zeitstempel erfolgt [R4]
- **MUSS** den eigenen Reproduzierbarkeits-Schalter der Toolchain aktivieren, wo einer existiert (§I)
- **SOLLTE** jeden Pin mit einem automatischen Updater koppeln (Renovate oder gleichwertig), sodass ein Pin gepatcht bleibt statt still zu veralten
- **SOLLTE** die Reproduzierbarkeit prüfen, indem zweimal gebaut und die Ausgaben verglichen werden (zum Beispiel mit `diffoscope`), und **SOLLTE** bekannte verbleibende Quellen von Nichtdeterminismus entfernen oder dokumentieren, etwa eine zur Build-Zeit geschriebene Seed-Datei oder ein Dateisystem-Image-Werkzeug, das die aktuelle Uhrzeit einträgt [R6]

### D. Keine maschinenspezifische Identität und keine Geheimnisse im Image (Pflichtsäule)

- **DARF NICHT** eine feste Maschinenidentität ausliefern: keine befüllte `/etc/machine-id` und keine auf anderem Weg übergebene feste Machine-ID, etwa auf einer ins Image eingebrannten Kernel-Kommandozeile. Die Datei fehlt oder ist leer (oder `uninitialized`), sodass jede Maschine beim ersten Boot ihre eigene ID erzeugt [R7]
- **DARF NICHT** SSH-Host-Keys, einen Random-Seed, private TLS-Schlüssel oder ein anderes maschinenspezifisches Geheimnis ausliefern. Diese werden beim ersten Boot erzeugt oder beim Deployment bereitgestellt [R7]
- **DARF NICHT** Zugangsdaten in eine Image-Schicht, ein Overlay oder ein Build-Log einbrennen. Ein Build, der zur Build-Zeit Zugangsdaten braucht, **MUSS** sie über einen Mechanismus erhalten, der sie aus der Ausgabe heraushält (eine reine Build-Umgebung, die nicht in den Zielbaum kopiert wird). Für bootc regelt das `spec/project/dockerfile-best-practices/` §"Secrets außerhalb der Layer (Pflichtsäule)"; es wird hier nicht wiederholt
- **SOLLTE** für maschinenspezifische Einrichtung `systemd-firstboot` oder eine gleichwertige First-Boot-Unit statt Build-Zeit-Skripten verwenden

### E. Integrität der Boot-Kette

- **SOLLTE** über ein Unified Kernel Image (UKI) booten: eine signierte UEFI-PE-Datei, die den Boot-Stub `systemd-stub`, den Kernel, die Initial-RAM-Disk und die Kernel-Kommandozeile gemäß UAPI.5 vereint [R1]. Eine Kernel-Kommandozeile außerhalb des signierten Artefakts lässt sich ändern, ohne die Signatur zu brechen
- **SOLLTE** den Boot-Pfad für UEFI Secure Boot signieren (shim oder ein direkt eingeschriebener Schlüssel, der Bootloader und das UKI). Der private Signierschlüssel **DARF NICHT** im Repository oder im Image liegen (er fällt unter §D)
- **SOLLTE** das schreibgeschützte Root oder `/usr` mit dm-verity schützen und den Verity-Root-Hash in die signierte UKI-Kommandozeile binden, sodass eine Offline-Veränderung des Root-Dateisystems beim Boot erkannt wird [R9]
- **SOLLTE**, wenn das Image Geheimnisse über das TPM2 entsperrt, diese an signierte PCR-Policies binden (`systemd-measure`/`ukify` berechnen PCR 11 für das UKI vor, eingeschrieben über `systemd-cryptenroll`) statt an rohe PCR-Werte, die bei jedem Kernel-Update brechen [R10]
- **MUSS** im Block `boot_chain` der Image-Deklaration für jeden dieser vier Schritte festhalten, ob das Image ihn umsetzt oder auslässt, sodass eine Auslassung eine dokumentierte Entscheidung ist und kein Versehen

### F. Update und Rollback (Pflichtsäule für im Feld aktualisierte Images)

Dieser Abschnitt gilt für jedes Image, dessen Deklaration `update_model: field-updated` sagt, und für jedes Image ohne gültige Deklaration, da ein Audit nicht erkennen kann, dass ein solches Image nie in place aktualisiert wird. Ein Image, dessen Deklaration `reflash-only` sagt, ist ausgenommen, und seine Deklaration **DARF NICHT** einen Block `update` tragen; eine Deklaration, die das tut, ist ein Widerspruch, den das Audit als Fehler dieses Abschnitts meldet.

- Ein im Feld aktualisiertes Image **MUSS** atomar aktualisieren: Entweder wird eine vollständige neue Version aktiv, oder die alte bleibt aktiv. In-place-Paket-Upgrades auf einer laufenden Appliance sind im Sinne dieser Spec kein Update-Mechanismus
- Ein solches Image **MUSS** einen Rollback-Pfad haben, der **automatisch auslöst**, wenn die neue Version nicht gesund hochkommt. Zulässige Mechanismen: systemd-boot Automatic Boot Assessment (Boot-Counting mit `systemd-bless-boot`, Erfolg erst nach `boot-complete.target`) [R3], die eigene Commit-nach-Boot-Logik eines Update-Frameworks (RAUC, SWUpdate, Mender) [R12] oder das vorherige Deployment eines deployment-basierten Systems (OSTree mit greenboot, bootc, NixOS-Generationen) in Kombination mit der Health-Definition des Images [R13], [R14], [R17]
- Seine Health-Definition (§A) **MUSS** diesen Rollback-Pfad steuern, **DARF NICHT** einen Boot nur deshalb als gut markieren, weil der Kernel gestartet ist, und **MUSS** das System selbst neu starten, nachdem sie `unhealthy` gemeldet hat, sodass ein unbeaufsichtigtes Gerät seinen Rollback-Pfad ohne Hilfe von außen erreicht
- Seine Health-Definition **MUSS** einen **Failure-Switch** beachten: einen Wert, den der Host übergibt, ohne eine signierte Boot-Komponente zu verändern (ein systemd-Credential oder auf einem Image ohne systemd ein SMBIOS-Type-11-String), benannt in `health.failure_switch` der Deklaration. Nennt der Wert des Switches die laufende Image-Version und ist diese Version noch nicht als gut markiert, meldet die Health-Definition `unhealthy`; sobald eine Version als gut markiert ist, wirkt der Switch auf sie nicht mehr, sodass er ein committetes System nicht in einen Rollback treiben kann. Über diesen Haken weist die Boot-Verifikation den Rollback-Pfad nach (`spec/project/image-boot-verification/` §I)
- Sein Update-Mechanismus **MUSS** seine Update-Quelle über einen vom Host injizierbaren Switch annehmen, der in `update.source_switch` der Deklaration benannt ist. Bietet diese Quelle eine neuere Version als die laufende an, **MUSS** der Mechanismus sie ohne weitere Eingabe installieren und in sie neu starten, und er **MUSS** eine Version ablehnen, die nicht neuer ist, sodass der Switch keinen Downgrade erzwingen kann. Die Deklaration **MUSS** in `update.max_boot_attempts` festhalten, wie viele Boots einer ungesunden Version der Rollback-Mechanismus zulässt
- **SOLLTE** ein A/B-Partitionslayout (oder das Deployment-Äquivalent) verwenden, das für zwei vollständige Versionen bemessen ist. Mit `systemd-sysupdate` **MÜSSEN** die Partitionen vor dem ersten Update existieren, da `systemd-sysupdate` keine Partitionen anlegt; `systemd-repart` legt sie an [R5]
- **MUSS** die Signatur einer Update-Payload vor der Installation prüfen, gleich welche Quelle der Quell-Switch nennt, da der Switch dem Host erlaubt, die Quelle umzulenken. Das Signierschema des Update-Frameworks ist der Mechanismus; die Signierung von OCI-Artefakten regelt `spec/project/artifact-signing/`

### G. SBOM (Pflichtsäule)

- **MUSS** für jeden Image-Build eine maschinenlesbare SBOM im Format SPDX oder CycloneDX erzeugen, generiert aus dem Build selbst (der nativen SBOM-Ausgabe der Toolchain, wo §I eine nennt) oder von einem SBOM-Generator, der aus dem Build-Einstiegspunkt oder dem CI-Workflow gegen das fertige Root-Dateisystem läuft
- **MUSS** die SBOM für ein als OCI-Artefakt veröffentlichtes Image (bootc) in SPDX erzeugen, weil `spec/project/artifact-signing/` SBOMs von OCI-Artefakten als SPDX attestiert
- **MUSS** die SBOM neben dem Image-Artefakt veröffentlichen, das sie beschreibt, sodass jedes veröffentlichte Image genau eine SBOM hat
- **DARF NICHT** die Ausgabe von Buildroots `make legal-info` allein als SBOM werten: Sie sammelt Lizenzen und Quellen, ist aber kein SPDX- oder CycloneDX-Dokument [R8]
- Die Lizenzklassifikation der SBOM ist an `spec/project/license-check/` delegiert, ihre Signierung oder Attestierung als OCI-Artefakt an `spec/project/artifact-signing/`

### H. Hygiene der systemd-Units

- **SOLLTE** jeden Dienst, den das Image ausliefert, mit der jeweils passenden systemd-Sandbox betreiben (`ProtectSystem=strict` mit expliziten `ReadWritePaths=`, `ProtectHome=`, `PrivateTmp=`, `NoNewPrivileges=`, `DynamicUser=` oder ein dedizierter Systembenutzer, `CapabilityBoundingSet=`) und **SOLLTE** paketierte Units über Drop-ins härten statt die Hersteller-Unit zu editieren [R11]
- **SOLLTE** die Exposure-Werte von `systemd-analyze security <unit>` für die eigenen Units des Images als Review-Hilfe festhalten. Der Wert spiegelt wider, welche systemd-Features genutzt werden, nicht die Sicherheit der Anwendung, und **DARF** daher **NICHT** für sich allein als Bestanden/Nicht-bestanden-Schwelle dienen [R11]
- **SOLLTE** die Health-Definition (§A) von den Diensten abhängig machen, für die die Appliance existiert, sodass ein gesunder Report bedeutet, dass diese Dienste laufen
- **DARF NICHT** netzwerkseitige Dienste aktivieren, die die Appliance nicht braucht

### I. Toolchain-Profile

Die Profile bilden den Kern auf jede Toolchain ab. Sie nennen Erkennungssignale und den Schalter, der eine Kernanforderung erfüllt. Ein Profil fügt nie eine Pflicht hinzu, die der Kern nicht nennt. Schalternamen ändern sich zwischen Toolchain-Releases, deshalb **MUSS** eine Implementierung sie gegen die Toolchain-Version lesen, die das Repository pinnt. Ein Eintrag, der eine Pflichtsäule speist und auf weniger unabhängigen Quellen beruht, als `spec/claude/research-triangulate/` verlangt, ist als **[unverified]** markiert; §J regelt, wie ein Audit ihn behandelt. Einträge, die nur beratende Abschnitte speisen, tragen keine Markierung; ihre Quellenzahl steht in den Referenzen. Das Feld `image.toolchain` der Deklaration wählt das Profil; die Erkennungssignale unten bestätigen es und finden die Definitionsdateien.

#### I.1 mkosi und das systemd-Ökosystem

- Erkennung: `mkosi.conf`, `mkosi.conf.d/` oder `mkosi.*`-Verzeichnisse
- §C: `SourceDateEpoch=` [R15] **[unverified]**; der Distributions-Mirror auf einen Snapshot gepinnt, eine Einstellung, deren Namen dieser Recherchelauf nicht belegt hat **[unverified]**
- §E: `UnifiedKernelImages=`, `SecureBoot=` mit einem Signierschlüssel, der von außerhalb des Repositorys bereitgestellt wird, `Verity=` (der Verity-Hash kommt in eine eigene GPT-Partition, was ein schreibgeschütztes Root impliziert) [R9], [R15]
- §F: `systemd-sysupdate`-Transfer-Definitionen unter `sysupdate.d/` plus `systemd-repart`-Definitionen für die A/B-Partitionen [R5]; Boot-Counting über systemd-boot [R3]
- §G: keine native SBOM-Ausgabe wird angenommen; ein SBOM-Generator läuft aus dem Build-Einstiegspunkt oder CI gegen das Ausgabe-Root

#### I.2 Yocto und Buildroot

- Erkennung, Yocto: `conf/local.conf`, `conf/bblayers.conf`, `meta-*`-Layer oder eine `kas`-YAML-Datei. Erkennung, Buildroot: eine `configs/*_defconfig` oder ein `BR2_EXTERNAL`-Baum
- §C, Yocto: jeder Layer auf einen Commit gepinnt (eine `kas`-Lock-Datei oder ein `repo`-Manifest mit Revisionen). Reproduzierbare Builds sind seit Release 3.1 der Default, und OE-Core leitet `SOURCE_DATE_EPOCH` selbst aus dem Quellstand ab; eine Konfiguration, die `BUILD_REPRODUCIBLE_BINARIES = "0"` setzt, schaltet sie ab [R16] **[unverified]**, sodass das Audit sie als `not-decidable` mit einer Warning meldet, nicht als `fail`
- §C, Buildroot: `BR2_REPRODUCIBLE=y`, das `SOURCE_DATE_EPOCH` beachtet und es sonst aus dem letzten Commit ableitet [R18] **[unverified]**
- §G, Yocto: SPDX-Ausgabe der Klasse `create-spdx`, die aktuelle Releases standardmäßig über `INHERIT_DISTRO` aktivieren und ältere Releases über `INHERIT += "create-spdx"` brauchen [R8]. §G, Buildroot: ein separater SPDX- oder CycloneDX-Generator, da `legal-info` keine SBOM ist [R8]
- §F: ein Layer oder Paket eines Update-Frameworks (RAUC, SWUpdate, Mender) mit aktivierter Rollback-Logik [R12]

#### I.3 Debian- und Ubuntu-Image-Builder

- Erkennung: ein Aufruf von `mmdebstrap` oder `debootstrap` im Build-Einstiegspunkt, eine live-build-`auto/config` oder ein `debos`-Rezept (`*.yaml` mit `architecture:` und `actions:`)
- §C: das Archiv auf einen `snapshot.debian.org`-Zeitstempel gepinnt, mit `SOURCE_DATE_EPOCH` auf denselben Zeitpunkt gesetzt. `mmdebstrap` erzeugt reproduzierbare `chroot`-Bäume, wenn `SOURCE_DATE_EPOCH` gesetzt ist. Snapshot-Archive brauchen `Acquire::Check-Valid-Until "false"`, da ihre Release-Dateien ein altes Datum tragen [R6]
- §D: am Ende des Builds den Inhalt von `/etc/machine-id`, `/var/lib/systemd/random-seed` und die SSH-Host-Keys löschen [R6], [R7]
- §G: keine native SBOM-Ausgabe; ein SBOM-Generator läuft aus dem Build-Einstiegspunkt oder CI gegen das fertige Root

#### I.4 NixOS und OSTree

- Erkennung, NixOS: `flake.nix` mit `nixosConfigurations` oder `configuration.nix`. Erkennung, OSTree: eine Compose-Definition (`*.json`/`*.yaml`, das `rpm-ostree compose` verarbeitet) oder ein `ostree`-Repository im Build
- §C, NixOS: eine committete `flake.lock`, die jede Eingabe pinnt [R13]. Wie Nix-Derivationen Zeitstempel unabhängig von der Systemuhr halten, hat dieser Recherchelauf nicht belegt, deshalb ist die `SOURCE_DATE_EPOCH`-Abbildung für NixOS **[unverified]**
- §F, NixOS: Generationen liefern das vorherige Deployment (`nixos-rebuild switch --rollback` oder das Bootmenü); die Garbage Collection entfernt Rollback-Ziele, deshalb **SOLLTE** das Image mindestens eine vorherige Generation behalten. Boot-Counting ist für systemd-boot verfügbar [R13]
- §F, OSTree: Deployments sind geordnete Bootloader-Einträge; `rpm-ostree rollback` macht das vorherige Deployment zum Default, und greenboot-Health-Checks lösen nach wiederholt gescheiterten Boots eines Updates eine automatische Rückkehr zum vorherigen Deployment aus [R17]
- §C, OSTree: die Paket-Repositories der Compose-Definition auf Snapshots gepinnt; wie `rpm-ostree compose` mit `SOURCE_DATE_EPOCH` umgeht, hat dieser Recherchelauf nicht belegt **[unverified]**
- §G: keine native SBOM-Ausgabe wird angenommen; ein SBOM-Generator läuft aus dem Build-Einstiegspunkt oder CI gegen die gebaute System-Closure oder den committeten Baum

#### I.5 bootc

- Erkennung: eine Deklaration mit `image.toolchain: bootc` oder ein `Containerfile`/`Dockerfile`, das das Label `containers.bootc 1` selbst setzt, das bootc-kompatible Basis-Images tragen [R19]. Ob ein abgeleitetes Image dieses Label von seiner Basis erbt, ist nicht belegt, deshalb stützt sich ein abgeleiteter Build auf die Deklaration
- Die Build-Datei regelt `spec/project/dockerfile-best-practices/`, die bootc-Images (an einem der beiden Signale oben erkannt) von ihrer Säule zum Nicht-Root-`USER` ausnimmt: Ein bootc-Image ist das Host-Betriebssystem, sein finaler Benutzer ist daher konstruktionsbedingt root
- §F: `bootc upgrade` stellt ein neues Image atomar bereit; `bootc rollback` lässt das vorherige Deployment als Nächstes booten und verwirft ein bereitgestelltes, noch nicht angewendetes Upgrade [R14]. Pakete **DÜRFEN NICHT** auf einem laufenden bootc-System aktualisiert werden; Änderungen gehen in ein neu gebautes Image [R14]
- §C: wie ein bootc-Build `SOURCE_DATE_EPOCH` in die Image-Schichten weitergibt, hat dieser Recherchelauf nicht belegt **[unverified]**
- §G: eine SPDX-SBOM des Images, attestiert gemäß `spec/project/artifact-signing/`
- Disk-Images werden mit `bootc-image-builder` (oder dessen Nachfolger) aus dem gepinnten Image-Digest erzeugt [R14]

### J. Entscheidbarkeit im Audit

- Ein Audit **MUSS** jede Anforderung als genau eines von `pass`, `fail` oder `not-decidable` melden und **DARF NIEMALS** `not-decidable` als Bestehen werten. Eine Anforderung außerhalb der Pflichtsäulen behält für jedes nicht bestandene Ergebnis ihren Schweregrad Warning oder Suggestion
- Jedes `not-decidable`-Ergebnis **MUSS** genau eine Ursache tragen, und ein Gate, das das Audit zusammenfasst, behandelt es nach dieser Ursache:
  - `resolvable: <scenario>`: eine Anforderung der Klasse `needs-built-artifact`, die ein benanntes Szenario der Boot-Verifikation auflöst. Sie blockiert das Gate wie ein `fail`, bis dieses Szenario besteht
  - `unverified: <§I entry>`: Die Entscheidung hängt an einem **[unverified]**-§I-Eintrag. Sie ist eine Warning, die nicht blockiert, da die Lücke in der Recherche dieser Spec liegt, nicht im Repository
  - `spec-gap: <reason>`: Weder ein §I-Schalter noch ein Szenario der Boot-Verifikation deckt die Anforderung bisher ab (die Tabelle sagt das in ihrer Zeile). Sie ist aus demselben Grund eine Warning, die nicht blockiert
  - `delegated: <spec>`: Eine andere Spec besitzt die Prüfung für diese Toolchain (die bootc-Build-Datei), und deren Audit entscheidet sie. Sie blockiert nicht, sobald das Ergebnis dieses Audits für dieselbe Revision vorliegt; solange es fehlt (das zuständige Audit lief nicht oder sein Plugin ist nicht installiert), blockiert sie wie `resolvable`, sodass eine Pflichtsäule nie ungeprüft besteht
  - `evidence: <reason>`: Eine Eingabe des Audits selbst fehlt (das Ergebnis des Deklarations-Validators oder die Liste der getrackten Dateien), oder der einzige Beleg für das Ergebnis ist eine Aussage im auditierten Inhalt. Sie blockiert in einer Pflichtsäule und bei der Deklarationsprüfung wie `resolvable`, da die Lücke in diesem Lauf liegt, nicht in der Spec, und ist anderswo eine Warning
- Jede Anforderung einer Pflichtsäule gehört zu einer Entscheidbarkeitsklasse, die festlegt, was ein statisches Audit schließen kann:

  | Anforderung | Klasse | Was das statische Audit prüft |
  |---|---|---|
  | §C Eingaben gepinnt | static-heuristic | Lock- oder Manifest-Dateien und in §I genannte Snapshot-Einstellungen; ein Profil ohne benannten Pinning-Schalter ergibt `not-decidable` (Ursache `spec-gap`) |
  | §C Lock-Datei committet | static-file | Die Lock- oder Manifest-Datei existiert und ist getrackt |
  | §C `SOURCE_DATE_EPOCH` aus dem Quellstand | static-heuristic | Einstiegspunkt oder Schalter berechnet es zur Build-Zeit aus dem Quellstand; ein Systemuhr-Ausdruck oder ein committetes Literal, das mit dem nächsten Commit veraltet, ist ein `fail` |
  | §C Reproduzierbarkeits-Schalter | static-file | Der §I-Schalter der Toolchain |
  | §D keine befüllte `machine-id` | needs-built-artifact | Nur ein Overlay-Baum oder Rezeptschritt, der die Datei schreibt; sonst `not-decidable`, aufgelöst durch das Identitäts-Szenario aus `spec/project/image-boot-verification/` §I (Ursache `resolvable`); bei einem Image ohne systemd, das `machine_id_app=-` meldet, ist die Ursache `spec-gap` |
  | §D keine Host-Keys oder Geheimnisse | static-heuristic | Committete Schlüsseldateien in Overlay-Bäumen und ein Secret-Scan der Definition |
  | §D keine Zugangsdaten in Schichten oder Logs | static-heuristic | Zugangsdaten-Muster in der Definition und im Einstiegspunkt sowie ein reiner Build-Mechanismus für jede Build-Zeit-Zugangsdaten |
  | §F Anwendbarkeit | static-file | `update_model` der Deklaration |
  | §F atomares Update, automatischer Rollback | static-heuristic | Der Update-Mechanismus und die in §I genannten Rollback-Signale |
  | §F Failure- und Quell-Switch, `max_boot_attempts` | static-file | `health.failure_switch` und Block `update` der Deklaration |
  | §F Health-Definition steuert Rollback | static-heuristic | Die Unit oder der Hook, den `health.definition` der Deklaration nennt, existiert, und eine Unit ist vor `boot-complete.target` eingeordnet |
  | §F Installation und Neustart ohne Eingabe, Neustart nach ungesundem Report | needs-built-artifact | Aufgelöst durch das Rollback-Szenario aus `spec/project/image-boot-verification/` §I |
  | §F Payload-Signatur geprüft | static-heuristic | Die Signatur- oder Keyring-Einstellung des Update-Frameworks; noch kein §I-Profil nennt diesen Schalter, deshalb ist das Ergebnis `not-decidable` (Ursache `spec-gap`), bis eines es tut |
  | §F kein Block `update` bei `reflash-only` | static-file | Die Deklaration |
  | §F lehnt nicht neuere Version ab, Switch nach Commit wirkungslos | needs-built-artifact | Noch von keinem Szenario der Boot-Verifikation abgedeckt; gemeldet als `not-decidable` (Ursache `spec-gap`) |
  | §G SBOM erzeugt | static-heuristic | Ein nativer SBOM-Schalter aus §I oder ein Generator-Aufruf im Einstiegspunkt oder in CI |
  | §G SPDX für OCI-Images | static-heuristic | Das Ausgabeformat des Generators bei einer Deklaration mit `image.toolchain: bootc` |
  | §G nicht `legal-info` allein | static-heuristic | Ein Generator-Aufruf neben `make legal-info` |
  | §G SBOM neben dem Image veröffentlicht | static-heuristic | Ein Veröffentlichungsschritt im Einstiegspunkt oder in CI, der die SBOM mit dem Image hochlädt |

- Eine Anforderung der Klasse `needs-built-artifact` **MUSS** vom statischen Audit als `not-decidable` gemeldet werden, wann immer die Rezeptseite keine Antwort gibt. Nennt die Tabelle ein Szenario der Boot-Verifikation, löst dieses sie am laufenden Image auf (Ursache `resolvable`); nennt sie keines, ist die Ursache `spec-gap`
- Ein als **[unverified]** markierter §I-Eintrag **DARF NICHT** eine Anforderung zu `fail` machen. Hängt die Entscheidung an ihm, meldet das Audit `not-decidable` und nennt den unverifizierten Eintrag

## Akzeptanzkriterien

Diese Kriterien fassen die obigen Anforderungen zusammen; jede Anforderung bleibt für sich normativ.

- [ ] `spec/project/linux-image-best-practices/` existiert mit `en.md` (kanonisch) und `de.md` (Übersetzung) und ist in `spec/README.md` gelistet
- [ ] §A verlangt pro Image eine `image-declaration.yaml`, die gegen `schemas/image-declaration-v1.0.schema.yaml` validiert, eine Health-Definition für jedes Image und die Konsolenzeile `IMAGE-HEALTH-REPORT` mit ihrer Feldliste, ihrer Pflicht zur seriellen Konsole und dem Moment, in dem `system_state` erhoben wird
- [ ] Die Schweregrad-Regel ist festgehalten: Eine Anforderung in einer Pflichtsäule (§C, §D, §F, §G) ist ein harter Fehler, ein MUSS anderswo eine Warning, ein SOLLTE eine Suggestion
- [ ] §C verlangt gepinnte Eingaben, eine committete Lock-Datei, ein quellstandsbasiertes `SOURCE_DATE_EPOCH` und den Reproduzierbarkeits-Schalter der Toolchain und delegiert das Pinning des bootc-Basis-Images an `spec/project/dockerfile-best-practices/`
- [ ] §D verbietet eine feste Maschinenidentität (eine befüllte `/etc/machine-id` oder eine auf anderem Weg übergebene feste Machine-ID), maschinenspezifische Geheimnisse und Zugangsdaten in jeder Schicht, jedem Overlay und jedem Log
- [ ] §E verlangt, dass der Block `boot_chain` der Deklaration jeden der vier Boot-Ketten-Schritte als umgesetzt oder ausgelassen festhält
- [ ] §F gilt für jedes nicht als `reflash-only` deklarierte Image, nennt die zulässigen automatischen Rollback-Mechanismen und verlangt eine Health-Definition, die den Rollback steuert und nach einem ungesunden Report neu startet, einen Failure-Switch, der nach dem Commit einer Version wirkungslos ist, einen Update-Quell-Switch, der ohne weitere Eingabe installiert und neu startet und eine nicht neuere Version ablehnt, die Prüfung der Payload-Signatur und `max_boot_attempts`, und verbietet einen Block `update` in einer `reflash-only`-Deklaration
- [ ] §G verlangt pro Build eine SPDX- oder CycloneDX-SBOM, SPDX für OCI-Images, die Veröffentlichung neben dem Artefakt und weist `make legal-info` allein zurück
- [ ] §I hat ein Profil pro Toolchain im Scope (mkosi/systemd, Yocto/Buildroot, Debian/Ubuntu, NixOS/OSTree, bootc), und jedes nennt sein Erkennungssignal und seine Abbildung von §C, §F und §G, wobei jeder unterbelegte Eintrag, der eine Pflichtsäule speist, als **[unverified]** markiert ist
- [ ] Jeder toolchain-spezifische Schalter, gegen den eine Anforderung geprüft wird, steht in §I; der Kern nennt Werkzeuge nur als Beispiele oder in Regeln, die nur gelten, solange dieses Werkzeug im Einsatz ist
- [ ] §J ordnet jeder Anforderung einer Pflichtsäule eine Entscheidbarkeitsklasse zu, verbietet, `not-decidable` als Bestehen zu werten, gibt jedem `not-decidable` eine von fünf Ursachen, die entscheiden, ob es blockiert, leitet Prüfungen am gebauten Artefakt an benannte Szenarien der Boot-Verifikation weiter, hält einen **[unverified]**-Eintrag davon ab, `fail` zu erzeugen oder ein Gate zu blockieren, und wendet dieselben drei Ergebnisse außerhalb der Pflichtsäulen an
- [ ] `spec/project/dockerfile-best-practices/` nimmt bootc-Images, erkannt an der Deklaration oder am Label, von ihrer Nicht-Root-`USER`-Säule aus, und der Skill `dockerfile-audit` und sein Scanner wenden diese Ausnahme an
- [ ] Signierung, Lizenzklassifikation und Boot-Verifikation sind an `spec/project/artifact-signing/`, `spec/project/license-check/` und `spec/project/image-boot-verification/` delegiert, ohne sie zu wiederholen

## Referenzen

- Quellen abgerufen am 2026-11-14. Quellenklassen gemäß `spec/claude/research-triangulate/` §"Quellenklassen und Unabhängigkeit": **Primary** und **Secondary**.
- [R1] UAPI.5 Unified Kernel Images (**Primary**): <https://uapi-group.org/specifications/specs/unified_kernel_image/>; systemd, "The recommended way to boot a systemd based OS" (**Primary**): <https://systemd.io/ROOTFS_DISCOVERY/>
- [R2] UAPI.2 Discoverable Partitions Specification (**Primary**): <https://uapi-group.org/specifications/specs/discoverable_partitions_specification/>; UAPI.3 Discoverable Disk Images (**Primary**): <https://uapi-group.org/specifications/specs/discoverable_disk_image/>
- [R3] systemd, "Automatic Boot Assessment" (**Primary**): <https://systemd.io/AUTOMATIC_BOOT_ASSESSMENT>; `systemd-bless-boot.service(8)` (**Primary**): <https://man.cs50.io/8/systemd-bless-boot.service>; Fedora-IoT-Issue #12, "Boot Counting and Success Determination" (**Secondary**): <https://pagure.io/fedora-iot/issue/12>
- [R4] reproducible-builds.org, `SOURCE_DATE_EPOCH`-Spezifikation (**Primary**): <https://reproducible-builds.org/specs/source-date-epoch>; reproducible-builds.org, `SOURCE_DATE_EPOCH`-Dokumentation (**Primary**): <https://reproducible-builds.org/docs/source-date-epoch/>; Yocto `reproducible_build.bbclass` (**Secondary**): <https://git.yoctoproject.org/poky/tree/meta/classes/reproducible_build.bbclass?h=2.8_M3>
- [R5] `systemd-sysupdate(8)` (**Primary**): <https://www.freedesktop.org/software/systemd/man/260/systemd-sysupdate.html>; `sysupdate.d(5)` (**Primary**): <https://www.mankier.com/5/sysupdate.d>; Igalia, "How to integrate systemd-sysupdate with your Yocto-based image" (**Secondary**): <https://blogs.igalia.com/mabente/how-to-integrate-systemd-sysupdate-with-your-yocto-based-image/>
- [R6] Debian-Wiki, "Reproducible installs" (**Primary**): <https://wiki.debian.org/ReproducibleInstalls>; `mmdebstrap(1)` (**Primary**): <https://manpages.ubuntu.com/manpages/plucky/man1/mmdebstrap.1.html>; mmdebstrap-Commit "make bit-by-bit reproducible" (**Primary**): <https://gitlab.mister-muffin.de/josch/mmdebstrap/commit/134330d786a5680aff30849c4120a894466da358>; debian-hurd-Liste, Nichtdeterminismus durch Random-Seed (**Secondary**): <https://lists.debian.org/debian-hurd/2024/12/msg00006.html>
- [R7] systemd, "Safely Building Images" (**Primary**): <https://systemd.io/BUILDING_IMAGES>; `machine-id(5)`, einschließlich der app-spezifischen Machine-ID (**Primary**): <https://www.man7.org/linux/man-pages/man5/machine-id.5.html>; Launchpad-Bug #2039434, "ubuntu-image leaving machine-id and host SSH keys in images" (**Secondary**): <https://launchpad.net/bugs/2039434>
- [R8] Yocto Project, "Creating a Software Bill of Materials" (**Primary**): <https://docs.yoctoproject.org/dev-manual/sbom.html>; AC6, "SBOM for embedded firmware" (**Secondary**): <https://www.ac6-formation.com/en/articles/sbom-embedded-firmware>; Foundries.io, "Creating SBOM for embedded devices" (**Secondary**): <https://foundries.io/insights/blog/creating-sbom-embedded-devices>
- [R9] `mkosi(1)`, `Verity=` (**Primary**): <https://manpages.debian.org/testing/mkosi/mkosi.1>; systemd-devel, "Is tpm2-measure-pcr really an additional security?" (**Secondary**): <https://lists.freedesktop.org/archives/systemd-devel/2025-March/051255.html>
- [R10] `systemd-measure(1)` (**Primary**): <https://www.freedesktop.org/software/systemd/man/260/systemd-measure.html>; `systemd-measure(1)` auf man7.org (**Primary**): <https://www.man7.org/linux/man-pages/man1/systemd-measure.1.html>
- [R11] Arch-Wiki, `systemd/Sandboxing` (**Secondary**): <https://wiki.archlinux.org/title/Systemd/Sandboxing>; Debian-Wiki, `ServiceSandboxing` (**Secondary**): <https://wiki.debian.org/ServiceSandboxing>; Rocky Linux, "systemd hardening" (**Secondary**): <https://docs.rockylinux.org/guides/security/systemd_hardening/>
- [R12] Pengutronix, RAUC (**Primary**): <https://pengutronix.de/en/software/rauc.html>; FOSDEM 2025, "Exploring Open Source Dual A/B Update Solutions for Embedded Linux" (**Secondary**): <https://fosdem.org/schedule/event/fosdem-2025-6299-exploring-open-source-dual-a-b-update-solutions-for-embedded-linux>; Yocto-Project-Wiki, "System Update" (**Secondary**): <https://wiki.yoctoproject.org/wiki/System_Update>
- [R13] NixOS Discourse, "How to rollback an update done by `nixos-upgrade` when using flakes?" (**Secondary**): <https://discourse.nixos.org/t/how-to-rollback-an-update-done-by-nixos-upgrade-when-using-flakes/51010>; NixOS & Flakes Book, "Downgrade or upgrade packages" (**Secondary**): <https://nixos-and-flakes.thiscute.world/nixos-with-flakes/downgrade-or-upgrade-packages>; nixpkgs-Commit, der Boot-Counting für systemd-boot ergänzt (**Primary**): <https://code.ornl.gov/nix/nixpkgs/-/commit/a6303da3a750d5aa759307f5d25859bd2d32fa2d>
- [R14] `bootc(8)` (**Primary**): <https://www.mankier.com/8/bootc>; Red Hat, "Managing RHEL bootc images" (**Primary**): <https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/using_image_mode_for_rhel_to_build_deploy_and_manage_operating_systems/managing-rhel-bootc-images>; CIQ, "bootc images" (**Secondary**): <https://docs.ciq.com/rlc/installation/bootc-images>
- [R15] `mkosi(1)` (**Primary**): <https://manpages.debian.org/testing/mkosi/mkosi.1>; `pacman`-Merge-Request 213 zu einem reproduzierbaren Installationsdatum, der die `SOURCE_DATE_EPOCH`-Unterstützung von mkosi erwähnt (**Secondary**): <https://gitlab.archlinux.org/pacman/pacman/-/merge_requests/213>; Vortrag auf All Systems Go 2024 zu Arch Linux und mkosi (**Secondary**): <https://pkgbuild.com/~jelle/arch-mkosi-all-systems-go-2024/>
- [R16] Yocto-Project-Testhandbuch, "Reproducible Builds" (**Primary**): <https://docs.yoctoproject.org/_sources/test-manual/reproducible-builds.rst.txt>; OpenEmbedded-Core `meta/lib/oe/reproducible.py` (**Primary**): <https://git.openembedded.org/openembedded-core/tree/meta/lib/oe/reproducible.py>; OpenBMC-Spiegel der Yocto-Dokumentation zu reproduzierbaren Builds (**Secondary**): <https://grok.openbmc.org/xref/openbmc/openbmc/poky/documentation/test-manual/reproducible-builds.rst?r=517393d9>
- [R17] `rpm-ostree(1)` (**Primary**): <https://mankier.com/1/rpm-ostree>; Red Hat, "Automating RHEL for Edge image rollback with greenboot" (**Secondary**): <https://www.redhat.com/en/blog/automating-rhel-edge-image-rollback-greenboot>; `docs.bazzite.gg`, "Rolling back system updates" (**Secondary**): <https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing//rolling_back_system_updates/>
- [R18] Buildroot, "reproducibility: introduce config knob" (**Primary**): <https://lists.buildroot.org/pipermail/buildroot/2016-July/165779.html>; Buildroot-Patch, der ein bestehendes `SOURCE_DATE_EPOCH` beibehält (**Primary**): <https://lists.buildroot.org/pipermail/buildroot/2017-November/207894.html>
- [R19] bootc, "bootc compatible images" (**Primary**): <https://containers.github.io/bootc/bootc-images.html>; Red Hat, "Creating bootc images from scratch" (**Primary**): <https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/10/html/using_image_mode_for_rhel_to_build_deploy_and_manage_operating_systems/generating-a-custom-minimal-base-image>; Fedora, "From scratch Fedora/CentOS bootc base container images" (**Primary**): <https://docs.fedoraproject.org/es/bootc/building-from-scratch/>

**Triangulationsstand.** Die Author-Time-Stufe aus `spec/claude/research-triangulate/` §"Author-Time-Aussagen" verlangt drei unabhängige Quellen. Gezählt nach Domain-Wurzel:

- Auf oder über der Stufe: [R3], [R4], [R5], [R6], [R7], [R8], [R12], [R13], [R14], [R17].
- Die drei Quellen von [R19] sind das bootc-Projekt und zwei Distributionen, deren Dokumentation davon abgeleitet ist. So gezählt wie [R16] ist das eine Upstream-Wurzel, sodass das Label-Signal aus §I.5 allein auf dem bootc-Projekt beruht. Ein abgeleiteter Build stützt sich ohnehin auf die Deklaration, das Label dient nur als zweites Signal.
- Zwei Wurzeln: [R1] (UAPI Group, systemd) und [R9] (Debian-Manpage-Spiegel von mkosi, systemd-devel), die nur beratende Abschnitte speisen; [R15] (die mkosi-Manpage, zwei Arch-Linux-Quellen) und [R16] (Yocto Project, OpenEmbedded, die dritte Quelle ein Spiegel der ersten), deren §I-Einträge deshalb als **[unverified]** markiert sind.
- Eine Wurzel: [R2], [R10], [R18]. [R2] und [R10] speisen nur beratende Abschnitte; [R18] stützt den Buildroot-Eintrag in §I.2, der deshalb als **[unverified]** markiert ist.
- Keine Quelle in diesem Lauf: der mkosi-Mirror-Snapshot-Schalter (§I.1) und die Abbildung von `SOURCE_DATE_EPOCH` für NixOS, OSTree (§I.4) und bootc (§I.5), alle als **[unverified]** markiert.
- Nicht belegt, daher nicht genutzt: ob ein abgeleitetes bootc-Image das Label `containers.bootc` von seiner Basis erbt (§I.5).
- Bewusst weggelassen: die Aussage, der Code von `bootc-image-builder` sei in `image-builder` aufgegangen (eine einzige Blog-Quelle), weshalb §I.5 „oder dessen Nachfolger“ sagt; und die Dateiendung unter `sysupdate.d`, die sich zwischen Quellen unterscheidet (`*.conf` in älteren Manpages, `*.transfer` in neueren), weshalb §I.1 nur das Verzeichnis nennt.

## Offene Fragen

- **Strenge der Boot-Kette** (parking-lot). §E ist beratend. Sollen Secure Boot, UKI und dm-verity für Appliances verpflichtend werden, deren Bedrohungsmodell physischen Zugriff umfasst? Die entscheidende Eingabe ist ein Bedrohungsmodell pro Repository, das diese Spec nicht definiert. Bis es existiert, verlangt §E nur, dass die Auslassung dokumentiert ist.
- **Signierung von Nicht-OCI-Image-Artefakten** (parking-lot). `spec/project/artifact-signing/` deckt nur OCI-Artefakte ab. Ein rohes Disk-Image oder Firmware-Bundle und seine SBOM haben noch keinen Signier- und Attestierungsvertrag. Ob das in `artifact-signing` oder in eine neue Spec gehört, entscheidet deren Eigentümer.
- **Schließen der [unverified]-Einträge** (load-bearing für §C). §J verhindert, dass die unverifizierten §I-Einträge einen Fehler erzeugen oder ein Gate blockieren, sodass das Audit heute nutzbar ist. Für jede Toolchain außer den Debian-Buildern kann der Reproduzierbarkeits-Teil von §C aber nicht scheitern, solange sein Schalter unverifiziert ist, womit diese Säule praktisch beratend wird. Die Lücke zu schließen braucht pro Toolchain einen Recherchelauf, der ihren §C-Schalter auf drei unabhängige Quellen bringt.
- **Portfolio-Scope-Hochstufung** (parking-lot). Soll diese Spec `local` bleiben oder zu `portfolio` hochgestuft werden, sodass image-bauende Repositories sie per Referenz gemäß `spec/project/portfolio-inherited-spec-layer/` erben? Die Hochstufung ist ein expliziter Maintainer-Akt und wird hier zurückgestellt. Eine Hochstufung muss `spec/project/dockerfile-best-practices/` mitnehmen oder deren bootc-Ausnahme umschreiben, die die Image-Deklaration dieser Spec liest.
