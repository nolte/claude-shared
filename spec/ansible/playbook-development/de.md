# Best Practices für die Ansible-Playbook-Entwicklung

Status: draft
Implementierung: documentary-only — Ansible-Automation liegt außerhalb des Scopes des `nolte-shared`-Plugins; diese Spec ist portfolioweite Leitlinie für Repositories, die Ansible-Automation ausliefern, aber kein Claude-Code-Skill und kein Agent in diesem Plugin operationalisiert sie. Repositories, die die Konventionen übernehmen, konsumieren die Spec per Verweis und wenden sie über ihr eigenes Ansible-Tooling (`ansible-playbook`, `ansible-lint`, Molecule) an.

## Kontext
Ansible-Playbooks sind die ausführende Schicht, die wiederverwendbare Rollen und Collections gegen ein Inventar von Ziel-Hosts orchestriert. Im nolte-Portfolio dienen sie unter anderem dem reproduzierbaren Bereitstellen von Linux-Geräten — vom Server bis zur Edge-Hardware auf Raspberry-Pi-Klasse. Diese Spec definiert die Best-Practice-Baseline für die *Playbook-Schicht* — Repository-Layout, Inventar-Hygiene, Vault- und Secrets-Behandlung, Tagging-Disziplin, Variablen-Precedence, Dependency-Konsum und CI-Gating. Die *Rollen-Schicht* (die wiederverwendbaren Einheiten, konsumiert via `requirements.yml`) wird von [`spec/ansible/role-development/`](../role-development/de.md) geregelt; diese Spec wiederholt rollen-interne Konventionen bewusst nicht.

Referenzen:
- [Ansible-Playbooks-Einführung](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_intro.html)
- [Ansible Tips and Tricks (offizieller Best-Practice-Guide)](https://docs.ansible.com/ansible/latest/tips_tricks/ansible_tips_tricks.html)
- [Inventory-Guide](https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html)
- [Vault-Guide](https://docs.ansible.com/ansible/latest/vault_guide/index.html)
- [Jeff Geerling — Best Practices for Ansible (Community)](https://www.jeffgeerling.com/blog/2019/best-practices-ansible-2019)
- [DevSec Hardening Framework](https://dev-sec.io/)

## Ziele
- Jedes Playbook-Repository im Portfolio hat ein vorhersagbares Layout, in dem sich Menschen und KI-Agenten ohne projektspezifische Entdeckung orientieren können
- Inventar-Daten, Secrets und Ausführungslogik sind sauber getrennt, damit dasselbe Playbook ohne Code-Änderungen über Umgebungen hinweg läuft
- Idempotenz und `check_mode`-Tauglichkeit sind für jeden Play Pflicht, sodass Reruns und Dry-Runs verlässliche Diagnose-Werkzeuge sind
- CI gated Lint-, Syntax- und Dry-Run-Fehler, bevor eine Änderung einen Host erreicht
- Rollen werden als versionierte, gepinnte Abhängigkeiten konsumiert; niemals in ein Playbook-Repository eingelegt — außer im Profil *single-environment-bootstrap* (siehe §Repository-Profile), wo Rollen device-spezifische Konfiguration kodieren, die nicht woanders wiederverwendet wird

## Nicht-Ziele
- Rollen-interne Konventionen (Variablen-Namespacing, `defaults/` vs `vars/`, Molecule-Szenarien, Galaxy-Publishing) — abgedeckt durch `spec/ansible/role-development/`
- Wahl des Ansible-Distributionskanals (Community-Paket vs. Red Hat AAP)
- Wahl des darunterliegenden OS oder Hardware-Ziels — die Spec gilt für jedes Linux-Ziel
- Konkrete Deployment-Topologie oder Release-Promotion-Prozess (separate Spec / Repo-Konventionen)
- Provisionierung des Ansible-Control-Nodes selbst (Bootstrap von Python, ansible-core)

## Anforderungen

### Repository-Layout
- **MUSS [MUST]** ein Playbook-Repository gemäß dem aktiven *Repository-Profil* organisieren (siehe unten) und in jedem Profil enthalten: `ansible.cfg` (projektlokal; niemals von der `~/.ansible.cfg` der Benutzerin abhängen), `requirements.yml` (deklariert alle konsumierten Rollen und Collections) sowie `playbooks/` mit einer Playbook-Datei je Orchestrierungs-Ziel (zum Beispiel `playbooks/bootstrap.yml`, `playbooks/deploy.yml`)
- **MUSS NICHT [MUST NOT]** Inventar-, group_vars- oder host_vars-Daten in `playbooks/` oder in einer Rolle ablegen; der Inventar-Baum ist die einzige Heimat von host- und gruppen-bezogenen Daten
- **SOLLTE [SHOULD]** eine `README.md` im Repository-Wurzelverzeichnis enthalten, die die verfügbaren Playbooks, die unterstützten Umgebungen (oder das einzelne Ziel-Gerät im Bootstrap-Profil) und das Einstiegs-Kommando je Playbook auflistet

### Repository-Profile
Ein Playbook-Repository **MUSS [MUST]** sich als genau eines der zwei Profile unten deklarieren. Die Wahl steuert das Inventar-Layout (§Inventar-Konventionen) und ob Inline-Rollen erlaubt sind (§Dependency-Konsum). Im Zweifel: Default *multi-environment-fleet*.

- **multi-environment-fleet** (Default): Flotten, Dienste oder Geräte, die mehrere Umgebungen bedienen (`production`, `staging`, `dev`). Inventar liegt unter `inventories/<env>/hosts.yml` plus `inventories/<env>/group_vars/` und `inventories/<env>/host_vars/` je Umgebung. Rollen **MÜSSEN [MUST]** über `requirements.yml` kommen; kein Top-Level-`roles/`. Auf dieses Profil sind alle übrigen Anforderungen dieser Spec standardmäßig zugeschnitten.
- **single-environment-bootstrap**: ein Repository, dessen einziger Zweck das Bootstrappen genau einer konkreten Maschine oder einer kleinen festen Flotte *identischer* Geräte ist (zum Beispiel ein `Reachy Mini` oder vier identische Edge-Sensoren), ohne Erwartung, in ein Multi-Environment-Deployment hineinzuwachsen. Inventar liegt unter `inventory/hosts.yml` plus `inventory/group_vars/` und `inventory/host_vars/` (kein `<env>`-Segment). Inline-`roles/<name>/`-Verzeichnisse sind **nur** für device-spezifische Konfiguration erlaubt, die von keinem anderen Repository wiederverwendet wird; sobald ein zweites Repository dieselbe Rolle konsumieren würde, **MUSS [MUST]** die Rolle in ihr eigenes Rollen-Repo gemäß `spec/ansible/role-development/` extrahiert und über `requirements.yml` konsumiert werden. Alle übrigen Anforderungen dieser Spec (Idempotente Läufe, Secrets-Behandlung, Naming/Tagging, Linting, CI-Gates) gelten unverändert.

### Python-Toolchain
- **MUSS [MUST]** `ansible-core` und jeden Python-Helfer der Toolchain (`ansible-lint`, `yamllint`, zugehörige Plugins) innerhalb einer projektlokalen Python-Virtual-Environment installieren — gemäß `spec/project/project-structure/` §Python-Entwicklung; niemals auf eine systemweite oder user-globale Ansible-Installation verlassen
- **MUSS [MUST]** Laufzeit-Abhängigkeiten (`ansible-core` plus etwaige Collection-seitige Python-Deps wie `requests`, `netaddr`, `kubernetes` für die relevanten Collections) in `requirements.txt` pinnen und Tooling-only-Abhängigkeiten (`ansible-lint`, `yamllint`) in `requirements-dev.txt` pinnen
- **SOLLTE [SHOULD]** Taskfile-Targets so verkabeln, dass `task install` das venv aus diesen Dateien provisioniert und die CI dasselbe Target vor Lint-, Syntax- und Dry-Run-Stufen aufruft — sodass Entwicklungs-Workstation und CI denselben Einstiegspunkt teilen
- Es gibt bewusst **keine** portfolioweite Mindestversion von `ansible-core`: Die Versions-Untergrenze bleibt pro Repo (Edge-/Raspberry-Pi-Ziele und Control-Node-Python-Versionen unterscheiden sich), und der explizite `requirements.txt`-Pin oben ist das, was Reproduzierbarkeit garantiert
- Die CI-Laufzeit bleibt dem konsumierenden Repo überlassen; diese Spec schreibt bewusst **kein** Execution-Environment-Image (EE) vor. Die tragende Reproduzierbarkeits-Garantie ist das projektlokale venv, gepinnt über `requirements.txt` / `requirements-dev.txt`, und der eine gemeinsame Installations-Einstiegspunkt oben — nicht ein Container-Image

### Idempotente Läufe und Check-Mode
- **MUSS [MUST]** jeden Play idempotent gestalten; ein zweiter Aufruf gegen einen bereits konvergierten Host meldet null geänderte Tasks
- **MUSS [MUST]** jeden Play sauber unter `--check` (Ansibles `check_mode`) laufen lassen; Module, die Check-Mode nicht unterstützen, werden nur dann mit explizitem `check_mode: false` umhüllt, wenn keine idempotente Alternative existiert
- **SOLLTE [SHOULD]** `--diff` in jedem Dry-Run-Aufruf einschließen, damit Reviewer sehen, was sich ändern würde

### Inventar-Konventionen
- **MUSS [MUST]** statische YAML-Inventare für stabile Infrastruktur bevorzugen: `inventories/<env>/hosts.yml` im Profil *multi-environment-fleet*, `inventory/hosts.yml` im Profil *single-environment-bootstrap*
- **MUSS [MUST]** Variablen strikt scopen: host-spezifische Werte in `host_vars/<host>.yml`, gruppen-geteilte Werte in `group_vars/<group>.yml`, umgebungs-geteilte Defaults in `group_vars/all.yml` (im Profil *single-environment-bootstrap* gelten die `all.yml`-Defaults weiterhin, einfach auf der Ebene der einen Umgebung)
- **MUSS [MUST]** die Verzeichnisse `group_vars/` und `host_vars/` **neben der Inventar-Datei** ablegen, nicht im Repository-Wurzelverzeichnis: Ansible löst diese Verzeichnisse relativ zur Inventar-Quelle (oder zum Playbook-Verzeichnis) auf, und ein Top-Level-`group_vars/` wird stillschweigend ignoriert, wenn das Playbook unter `playbooks/` liegt
- **MUSS NICHT [MUST NOT]** inventar-gebundene Variablen in Playbook-`vars:`-Blöcken deklarieren; playbook-lokales `vars:` ist Helfer-Werten innerhalb eines Plays vorbehalten
- **KANN [MAY]** ein dynamisches Inventory-Plugin verwenden, wenn die Host-Aufzählung aus einer Quelle der Wahrheit kommen muss (Cloud, CMDB, Home Assistant); die Plugin-Version über die konsumierende Collection in `requirements.yml` pinnen

### Secrets-Behandlung
- **MUSS [MUST]** jedes Geheimnis (Passwörter, API-Tokens, Signier-Schlüssel, TLS-Material) vaulted behandeln: mit `ansible-vault` verschlüsseln (per Datei oder per String) oder über eine SOPS-verschlüsselte Datei via Community-Plugin durchreichen
- **MUSS NICHT [MUST NOT]** eine Vault-Password-Datei (typische Namen `.vault-pass`, `vault_password_file`) in das Repository einchecken; den Pfad über `ansible.cfg` oder den `--vault-password-file`-Flag konfigurieren und die Datei namentlich in `.gitignore` führen
- **MUSS NICHT [MUST NOT]** ein Klartext-Geheimnis in eine getrackte Datei unter `inventories/`, `playbooks/`, `group_vars/` oder `host_vars/` einchecken; akzeptabel ist ausschließlich ein vault-verschlüsselter Block oder eine externe Referenz
- **SOLLTE [SHOULD]** vaulted *Strings* (Einzelwerte inline) für kurze Geheimnisse und vaulted *Dateien* für ganze Variablen-Gruppen verwenden, damit Diffs lesbar bleiben
- **KANN [MAY]** `sops` (oder einen anderen externen Secret-Store wie HashiCorp Vault) integrieren, wenn `ansible-vault` nicht zum operativen Modell der Umgebung passt

### Naming und Tagging
- **MUSS [MUST]** jedem Play ein `name:` geben, das als Ziel formuliert ist (`Bootstrap base packages`), nicht als Werkzeug-Aktion (`run apt`)
- **MUSS [MUST]** jedem Task ein `name:` geben, das den gewünschten Endzustand beschreibt, nicht das Modul-Verb
- **MUSS [MUST]** `tags: [never]` an jeden Task anlegen, dessen Effekt destruktiv oder nicht wiederherstellbar ist (Disk-Wipes, erzwungene Reboots, Zertifikat-Widerrufe), damit der Task nur bei explizitem `--tags`-Opt-in läuft
- **SOLLTE [SHOULD]** Tags konsistent vergeben — mindestens eines aus `bootstrap`, `config`, `deploy`, `verify` je Task — sodass Operator:innen mit `--tags` einen Ausschnitt gezielt steuern können

### Variablen-Precedence
- **MUSS [MUST]** das `defaults/main.yml` der konsumierten Rollen als einzige Default-Schicht behandeln; Overrides fließen über `group_vars/`, `host_vars/` und (letzter Ausweg) `--extra-vars`
- **MUSS NICHT [MUST NOT]** eine Rollen-Variable im `vars:`-Block eines Playbooks neu definieren, wenn derselbe Wert in `group_vars/` / `host_vars/` gehört; playbook-`vars:` ist Helfer-Werten innerhalb eines Plays vorbehalten
- **SOLLTE [SHOULD]** jeder Playbook-Ebene-Variable einen Namens-Präfix geben, der die Eigentumsverhältnisse offensichtlich macht (`bootstrap_disk_layout`, nicht `disk_layout`), damit sie nicht mit Rollen-Variablen kollidiert

### Dependency-Konsum
- **MUSS [MUST]** jede von den Playbooks genutzte Rolle und Collection in `requirements.yml` deklarieren
- **MUSS [MUST]** jede Galaxy- oder Git-Quelle an einen Release-Tag pinnen (zum Beispiel `version: 1.4.0` für Galaxy, `version: v1.4.0` für Git) — niemals `master` / `main` oder einen beweglichen Branch
- **MUSS NICHT [MUST NOT]** eine Rolle in ein *multi-environment-fleet*-Repository einlegen (kein Top-Level-`roles/`-Ordner, der Galaxy-Rollen verschattet); wiederverwendbare Einheiten leben in ihrem eigenen Rollen-Repo gemäß `spec/ansible/role-development/`. Das Profil *single-environment-bootstrap* **KANN [MAY]** device-spezifische Rollen inline unter Top-Level-`roles/<name>/` halten gemäß §Repository-Profile; sobald eine solche Rolle von einem zweiten Repository konsumiert wird, **MUSS [MUST]** sie extrahiert werden
- **SOLLTE [SHOULD]** Abhängigkeiten in einen projektlokalen Pfad installieren (`ansible.cfg` `roles_path`, `collections_path`), damit jedes Repo in sich geschlossen ist

### Linting
- **MUSS [MUST]** `ansible-lint` und `yamllint` als CI-Gate ausführen; beide müssen grün sein, bevor ein Playbook auf dem Integrations-Branch landen darf
- **SOLLTE [SHOULD]** beide Linter in eine `.pre-commit-config.yaml` verkabeln, damit Verstöße lokal vor dem Commit auffallen
- **SOLLTE [SHOULD]** Linter-Ausnahmen inline (`# noqa`) und eng halten, statt Regeln global zu deaktivieren; den Grund neben jeder Ausnahme dokumentieren

### CI-Pipeline
- **MUSS [MUST]** in der CI enthalten: einen Lint-Schritt (`ansible-lint`, `yamllint`), einen Syntax-Schritt (`ansible-playbook --syntax-check`) und einen Dry-Run-Schritt (`ansible-playbook --check --diff`) gegen ein repräsentatives Test-Inventar
- **SOLLTE [SHOULD]** aus der CI heraus (oder via explizit gegateten Workflow) einen realen Apply gegen eine Staging-Umgebung laufen lassen, bevor Apply gegen Production erfolgt; dies bleibt ein **SOLLTE [SHOULD]** (kein **MUSS [MUST]**), weil nicht jedes multi-environment-fleet-Repo eine Staging-Umgebung deklariert, die Production spiegelt, und konkrete Release-Promotion gemäß §Nicht-Ziele außerhalb des Scopes liegt
- **SOLLTE [SHOULD]** den Dry-Run-Diff als PR-Artefakt veröffentlichen, damit Reviewer ohne lokales Reproduzieren lesen können, was sich ändern würde; Dateiformat und Aufbewahrung des Artefakts bleiben jeder Repo-Diskretion überlassen (die Spec schreibt nur vor, dass der Diff veröffentlicht wird, nicht wie er gespeichert wird)

### Querverweise
- Für rollen-interne Konventionen (Galaxy-Verzeichnislayout, `meta/argument_specs.yml`, `defaults/` vs `vars/`, Molecule, Galaxy-Publishing) siehe [`spec/ansible/role-development/`](../role-development/de.md)

## Akzeptanzkriterien
- [ ] Repository deklariert sein Profil (multi-environment-fleet oder single-environment-bootstrap) in `README.md` oder `CLAUDE.md`
- [ ] Repository enthält `ansible.cfg`, `requirements.yml`, einen `playbooks/`-Ordner mit einer oder mehreren Playbook-Dateien sowie den zum deklarierten Profil passenden Inventar-Baum: `inventories/<env>/hosts.yml` plus `group_vars/` und `host_vars/` für mindestens eine Umgebung (multi-environment-fleet) oder `inventory/hosts.yml` plus `inventory/group_vars/` und `inventory/host_vars/` (single-environment-bootstrap)
- [ ] `group_vars/` und `host_vars/` liegen neben der Inventar-Datei (unter `inventories/<env>/` oder `inventory/`), nicht im Repository-Wurzelverzeichnis
- [ ] `requirements.txt` pinnt `ansible-core` (und etwaige Collection-seitige Python-Deps); `requirements-dev.txt` pinnt `ansible-lint` und `yamllint`
- [ ] CI ruft denselben Installations-Pfad auf, den auch lokale Taskfile-Targets nutzen, sodass Entwicklungs-Workstation und CI denselben Einstiegspunkt teilen
- [ ] Keine getrackte Datei unter `inventories/`, `playbooks/`, `group_vars/` oder `host_vars/` enthält ein Klartext-Geheimnis; jedes Geheimnis ist vault-verschlüsselt oder stammt aus einem externen Store
- [ ] Vault-Password-Datei (typische Namen `.vault-pass`, `vault_password_file`) ist nicht getrackt und in `.gitignore` gelistet
- [ ] Jeder Eintrag in `requirements.yml` pinnt eine Galaxy- oder Git-Quelle an einen Release-Tag, nicht an einen beweglichen Branch
- [ ] In einem *multi-environment-fleet*-Repository verschattet kein Top-Level-`roles/`-Verzeichnis Galaxy-Rollen; alle Rollen kommen über `requirements.yml`. In einem *single-environment-bootstrap*-Repository ist jede Inline-Rolle unter `roles/<name>/` device-spezifisch und wird von keinem anderen Repository konsumiert
- [ ] Jeder Play und jeder Task in `playbooks/` hat ein `name:`-Feld
- [ ] Jeder Play konvergiert beim zweiten Lauf gegen denselben Host mit null geänderten Tasks
- [ ] CI führt `ansible-lint`, `yamllint`, `ansible-playbook --syntax-check` und `ansible-playbook --check --diff` gegen ein Test-Inventar aus; alle vier sind Pflicht für den Merge
- [ ] Mindestens ein getaggter Ausführungs-Slice (`--tags bootstrap`, `--tags deploy`, …) ist in der `README.md` dokumentiert
- [ ] Kein Playbook-`vars:`-Block definiert eine Variable neu, die bereits im `defaults/main.yml` einer konsumierten Rolle existiert

## Offene Fragen
- Soll das Profil *single-environment-bootstrap* in eine eigene dedizierte Spec (`spec/ansible/edge-device-bootstrap/`) ausgelagert werden, sobald ein zweites Repository es übernimmt — oder als Profil innerhalb dieser Spec bleiben?
- Soll `sops`-Integration von **KANN [MAY]** auf **SOLLTE [SHOULD]** angehoben werden, sobald ein portfolio­weites Muster (kustomize-artiger Key-Store) entsteht?
