# Best Practices für die Ansible-Rollen-Entwicklung

Status: draft
Implementierung: documentary-only — Ansible-Automation liegt außerhalb des Scopes des `nolte-shared`-Plugins; diese Spec ist portfolioweite Leitlinie für Repositories, die Ansible-Rollen ausliefern, aber kein Claude-Code-Skill und kein Agent in diesem Plugin operationalisiert sie. Rollen-Autor:innen konsumieren die Spec per Verweis und wenden sie über ihr eigenes Ansible-Tooling (`ansible-galaxy`, `ansible-lint`, Molecule) an.

## Kontext
Ansible-Rollen sind die wiederverwendbaren Einheiten, die ein Playbook-Repository über `requirements.yml` konsumiert. Sie kapseln idempotente Zustands-Logik für eine fokussierte Verantwortlichkeit (nginx installieren, SSH härten, ein Basis-OS bootstrappen), damit dieselbe Logik über Umgebungen und Projekte hinweg wiederverwendet werden kann. Diese Spec definiert die Best-Practice-Baseline für die *Rollen-Schicht* — Galaxy-konformes Verzeichnislayout, Rollen-Schnittstelle (Argument-Specs, Metadaten, Abhängigkeiten), Variablen-Hygiene, Idempotenz, Naming, Tests mit Molecule, Linting, semantische Versionierung und Galaxy-Publishing. Die konsumierende *Playbook-Schicht* wird von [`spec/ansible/playbook-development/`](../playbook-development/de.md) geregelt; diese Spec wiederholt orchestrierungs-bezogene Konventionen (Inventar, Vault, CI-Dry-Run) bewusst nicht.

Referenzen:
- [Reusing roles (offizieller Guide)](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_reuse_roles.html)
- [Developing collections](https://docs.ansible.com/ansible/latest/dev_guide/developing_collections.html)
- [Galaxy — creating a role](https://galaxy.ansible.com/docs/contributing/creating_role.html)
- [Molecule (Test-Framework)](https://ansible.readthedocs.io/projects/molecule/)
- [ansible-lint](https://ansible.readthedocs.io/projects/lint/)
- [Jeff Geerling — Best Practices for Ansible (Community)](https://www.jeffgeerling.com/blog/2019/best-practices-ansible-2019)
- [DevSec Hardening Framework](https://dev-sec.io/)

## Ziele
- Jede Rolle im Portfolio ist Galaxy-konform, sodass sie via `ansible-galaxy install` oder `requirements.yml` ohne projektspezifischen Klebstoff installierbar ist
- Die öffentliche Oberfläche der Rolle (Variablen, Abhängigkeiten, unterstützte Plattformen) ist in Metadaten-Dateien deklariert, sodass Konsumenten sie ohne Lesen des Task-Codes entdecken können
- Variablen-Namespacing verhindert Kollisionen, wenn mehrere Rollen innerhalb desselben Plays laufen
- Jede Änderung an einer Rolle besteht Molecule, ansible-lint und yamllint vor dem Publishing
- Rollen werden als semantisch versionierte Artefakte ausgeliefert, sodass Playbook-Repos gegen einen stabilen Vertrag pinnen können

## Nicht-Ziele
- Orchestrierungs-bezogene Konventionen (Inventar, group_vars, Vault, CI-Dry-Run) — abgedeckt durch `spec/ansible/playbook-development/`
- Wahl der Sprache für Template-Inhalte jenseits von Jinja2 (dem Ansible-Default)
- Konkrete Geschäftslogik einer Rolle (welche nginx-Konfiguration, welche Pakete)
- Multi-Rollen-Meta-Orchestrierung — das ist Aufgabe des Playbooks

## Anforderungen

### Galaxy-konformes Verzeichnislayout
- **MUSS [MUST]** die Galaxy-konformen Unterverzeichnisse jeder Rolle enthalten: `defaults/`, `vars/`, `tasks/`, `handlers/`, `templates/`, `files/`, `meta/`
- **MUSS [MUST]** ein `tasks/main.yml` als Einstiegspunkt der Rolle enthalten; weitere Task-Dateien werden via `import_tasks:` / `include_tasks:` aus `main.yml` eingebunden
- **MUSS [MUST]** ein `meta/main.yml` enthalten, das `galaxy_info` (Autor:in, Beschreibung, Lizenz, unterstützte Plattformen, Mindest-Ansible-Version) und `dependencies` (transitiv konsumierte Rollen) deklariert
- **SOLLTE [SHOULD]** ein `tests/`-Verzeichnis mit mindestens einem Smoke-Test-Playbook und ein `molecule/`-Verzeichnis mit mindestens einem `default`-Szenario enthalten (siehe Tests mit Molecule)
- **KANN [MAY]** die Rolle innerhalb einer Collection (`<namespace>/<collection>/roles/<role>/`) verpacken, wenn mehrere verwandte Rollen gemeinsam ausgeliefert werden; Collection-Metadaten leben dann in `galaxy.yml`

### Python-Toolchain
- **MUSS [MUST]** `ansible-core` und jeden Python-Helfer der Toolchain (`ansible-lint`, `yamllint`, `molecule`, zugehörige Plugins) innerhalb einer projektlokalen Python-Virtual-Environment installieren — gemäß `spec/project/project-structure/` §Python-Entwicklung; niemals auf eine systemweite oder user-globale Ansible-Installation verlassen
- **MUSS [MUST]** Laufzeit-Abhängigkeiten (`ansible-core` plus etwaige Collection-seitige Python-Deps wie `requests`, `netaddr`) in `requirements.txt` pinnen und Tooling-only-Abhängigkeiten (`ansible-lint`, `yamllint`, `molecule`, ein Molecule-Driver-Plugin wie `molecule-plugins[docker]` oder `molecule-plugins[podman]`, `testinfra` wo genutzt) in `requirements-dev.txt` pinnen
- **SOLLTE [SHOULD]** Taskfile-Targets so verkabeln, dass `task install` das venv aus diesen Dateien provisioniert und die CI dasselbe Target vor Lint-, Syntax- und Molecule-Stufen aufruft — sodass Entwicklungs-Workstation und CI denselben Einstiegspunkt teilen

### Rollen-Schnittstelle
- **MUSS [MUST]** ein `meta/argument_specs.yml` für die Rolle deklarieren, mit einem `options:`-Eintrag pro konsumierter Variable, der `type`, `description` und `required` (sowie ggf. `default`, `choices`, `elements`) angibt
- **MUSS [MUST]** `meta/argument_specs.yml` mit `defaults/main.yml` synchron halten: jede `defaults/`-Variable, die zur öffentlichen Oberfläche der Rolle gehört, taucht in `argument_specs.yml` auf
- **MUSS [MUST]** jede transitive Rolle, von der die Rolle abhängt, unter `meta/main.yml` `dependencies:` deklarieren; niemals eine Geschwister-Rolle mit `import_role:` / `include_role:` aufrufen und vergessen, die Abhängigkeit zu hinterlegen
- **SOLLTE [SHOULD]** nicht-offensichtliche Variablen-Wechselwirkungen (sich gegenseitig ausschließende Mengen, bedingte Pflicht-Felder) im `description:`-Feld von `argument_specs.yml` dokumentieren

### `defaults/` vs `vars/`-Disziplin
- **MUSS [MUST]** jede überschreibbare Variable in `defaults/main.yml` ablegen; eine Konsumentin muss sie über `group_vars`, `host_vars` oder `--extra-vars` überschreiben können, ohne die Rolle zu monkey-patchen
- **MUSS [MUST]** `vars/main.yml` auf interne Konstanten und abgeleitete Werte beschränken, die die Rolle selbst besitzt (zum Beispiel Mapping einer Distro-Familie auf einen Paketnamen); `vars/`-Werte niemals als öffentliche Knöpfe der Rolle exponieren
- **MUSS NICHT [MUST NOT]** Geheimnisse (Passwörter, Tokens, Schlüssel) in `defaults/main.yml` oder `vars/main.yml` ablegen; Geheimnisse kommen über die Vault-Schicht des konsumierenden Playbooks
- **SOLLTE [SHOULD]** `defaults/main.yml` kurz und selbsterklärend halten; Kommentare über jeder Variable erklären die Absicht und verlinken auf den passenden `argument_specs.yml`-Eintrag, wenn relevant

### Idempotente Läufe und Check-Mode
- **MUSS [MUST]** jeden Task idempotent gestalten: ein erneutes Ausführen der Rolle gegen einen konvergierten Host meldet null geänderte Tasks
- **MUSS [MUST]** sicherstellen, dass jeder Task `check_mode`-tauglich ist; Module, die Check-Mode nicht unterstützen, werden nur dann mit explizitem `check_mode: false` geöffnet, wenn keine idempotente Alternative existiert, und in der README der Rolle dokumentiert
- **SOLLTE [SHOULD]** Ansible-eigene Module gegenüber `command:` / `shell:` bevorzugen; wenn Shell unvermeidbar ist, den Task mit `creates:`, `removes:` oder einer expliziten `changed_when:`-Bedingung absichern

### Naming
- **MUSS [MUST]** jede öffentliche Rollen-Variable mit dem Rollennamen präfixieren (`nginx_port`, nicht `port`; `chrony_servers`, nicht `servers`), damit Variablen nicht kollidieren, wenn mehrere Rollen in einem Play laufen
- **MUSS [MUST]** Handler-Namen genauso präfixieren (`nginx | restart`, nicht `restart`), damit Notifications eindeutig auflösen
- **MUSS [MUST]** jedem Task ein `name:`-Feld geben, das den gewünschten Endzustand beschreibt, nicht das Modul-Verb (`Ensure nginx is enabled`, nicht `service`)
- **SOLLTE [SHOULD]** Task-Dateien nach Funktion benennen (`tasks/install.yml`, `tasks/configure.yml`, `tasks/service.yml`) statt nach Modul-Kategorie

### Tests mit Molecule
- **MUSS [MUST]** ein `molecule/default/`-Szenario enthalten, das die Rolle konvergiert und Idempotenz prüft (ein zweiter `converge` meldet null Änderungen)
- **MUSS [MUST]** `molecule test` (den vollen Lifecycle aus create/converge/idempotence/verify/destroy) als CI-Gate ausführen; ein Merge auf den Integrations-Branch erfordert Grün
- **MUSS NICHT [MUST NOT]** den `delegated`-Driver für Idempotenz-Aussagen verwenden, weil er das per-Host-Zustandsmodell umgeht
- **SOLLTE [SHOULD]** den `docker`- oder `podman`-Driver verwenden und mindestens einen Verifikations-Schritt enthalten (`molecule verify` mit `ansible.builtin.assert` oder `testinfra`), der das primäre beobachtbare Ergebnis der Rolle abdeckt. Rollen, die beobachtbaren Laufzeit-Zustand ändern (einen laufenden Dienst, einen offenen Port, eine ausgelieferte Datei), SOLLTEN den Verify-Schritt als faktisch verpflichtend behandeln.
- **KANN [MAY]** zusätzliche Szenarien (`molecule/<scenario>/`) für distro- oder topologie-spezifische Test-Matrizen ergänzen

### Linting
- **MUSS [MUST]** `ansible-lint` und `yamllint` als CI-Gate ausführen; beide müssen grün sein, bevor eine Rollen-Version getaggt werden darf
- **SOLLTE [SHOULD]** die `args`-Regel von `ansible-lint` aktivieren, damit Argument-Spec-Verstöße und Drift zwischen `defaults/main.yml` ↔ `argument_specs.yml` im bestehenden Lint-Gate auffallen; ein separater Validator ist nicht erforderlich
- **SOLLTE [SHOULD]** beide Linter in eine `.pre-commit-config.yaml` verkabeln, damit Verstöße lokal vor dem Commit auffallen
- **SOLLTE [SHOULD]** Linter-Ausnahmen inline (`# noqa`) und eng halten, statt Regeln global zu deaktivieren; den Grund neben jeder Ausnahme dokumentieren

### Versionierung
- **MUSS [MUST]** jede veröffentlichte Rolle mit semantischer Versionierung auf Git-Tags versionieren (`v1.4.2`, niemals nur `1.4` oder `latest`)
- **MUSS [MUST]** die öffentliche Oberfläche der Rolle als Stabilitäts-Vertrag behandeln: Breaking Changes an `argument_specs.yml`, an Defaults in `defaults/main.yml` oder an `meta/main.yml` `dependencies:` erfordern einen Major-Version-Bump
- **SOLLTE [SHOULD]** Variablen-Umbenennungen/-Entfernungen mit einer Minor-Version ausliefern, die einen Ansible-`deprecated`/`warn`-Hinweis trägt, bevor der Major-Bump erfolgt; Brüche an Abhängigkeiten und Default-Werten DÜRFEN [MAY] direkt zum Major-Bump gehen
- **SOLLTE [SHOULD]** ein `CHANGELOG.md` (oder Release-Drafter-Output) pflegen, das Änderungen je getaggter Version auflistet

### Galaxy-Publishing
- **MUSS [MUST]** die Rolle (oder die enthaltende Collection) so veröffentlichen, dass konsumierende Playbook-Repos sie via `requirements.yml` pinnen können; Standalone-Rollen via `ansible-galaxy role import`, Collections via `ansible-galaxy collection publish`. Single-Role-Repos setzen standardmäßig auf Standalone-Rollen-Publishing; eine Collection (`galaxy.yml`) wird übernommen, sobald das Repo eine zweite verwandte Rolle ausliefert, im Einklang mit der Post-2.10-Ökosystem-Richtung.
- **SOLLTE [SHOULD]** das Publishing aus einem CI-Workflow triggern (auf Tag-Push), nicht von der Maschine einer Entwicklerin, damit jeder Release reproduzierbar ist
- **KANN [MAY]** auf eine private Galaxy- / Pulp-Instanz veröffentlichen, wenn die Rolle portfolio-intern ist; das `requirements.yml` des konsumierenden Playbooks nutzt dann die passende `source:`-URL

### Querverweise
- Für orchestrierungs-bezogene Konventionen (Inventar, Vault, CI-Dry-Run, Tags) siehe [`spec/ansible/playbook-development/`](../playbook-development/de.md)

## Akzeptanzkriterien
- [ ] Rolle enthält `defaults/`, `vars/`, `tasks/main.yml`, `handlers/`, `templates/`, `files/`, `meta/main.yml` (Unterverzeichnisse mit Inhalt nach Bedarf; `meta/main.yml` ist Pflicht)
- [ ] `requirements.txt` pinnt `ansible-core` (und etwaige Collection-seitige Python-Deps); `requirements-dev.txt` pinnt `ansible-lint`, `yamllint`, `molecule` und ein Molecule-Driver-Plugin (`molecule-plugins[docker]` oder `molecule-plugins[podman]`)
- [ ] CI ruft denselben Installations-Pfad auf, den auch lokale Taskfile-Targets nutzen, sodass Entwicklungs-Workstation und CI denselben Einstiegspunkt teilen
- [ ] `meta/main.yml` deklariert `galaxy_info` (Autor:in, Beschreibung, Lizenz, Plattformen, min_ansible_version) und `dependencies`
- [ ] `meta/argument_specs.yml` existiert und listet jede öffentliche Variable aus `defaults/main.yml` mit `type`, `description` und `required`
- [ ] `defaults/main.yml` und `vars/main.yml` enthalten keinen Geheimnis-Wert; Geheimnisse kommen vom konsumierenden Playbook
- [ ] Jede öffentliche Variable in `defaults/main.yml` ist mit dem Rollennamen präfixiert
- [ ] Jeder Task in `tasks/` hat ein `name:`-Feld
- [ ] Ein erneuter Lauf der Rolle gegen einen konvergierten Host meldet null geänderte Tasks
- [ ] `molecule/default/` existiert, nutzt den `docker`- oder `podman`-Driver und prüft Idempotenz; `molecule test` läuft in der CI als Pflicht-Check
- [ ] `ansible-lint` und `yamllint` laufen als CI-Gates und sind auf dem HEAD-Commit grün
- [ ] Veröffentlichte Versionen sind Git-getaggt mit semantischer Versionierung (`vMAJOR.MINOR.PATCH`); ein Breaking Change an `argument_specs.yml`, `defaults/main.yml` oder `meta/main.yml` `dependencies:` führt zu einem Major-Version-Bump
- [ ] Die Rolle (oder ihre enthaltende Collection) ist auf einen Galaxy- / Pulp-Endpunkt veröffentlicht, gegen den das `requirements.yml` des konsumierenden Playbooks an einen getaggten Release pinnt

## Offene Fragen
- Soll die Spec eine portfolio­weite Mindest-Molecule-Szenario-Matrix vorschreiben (Debian + RHEL-Familie, oder nur eines)?
