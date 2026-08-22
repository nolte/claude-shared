# Ansible Playbook Development Best Practices

Status: draft
Implementation: documentary-only—Ansible automation lives outside the `nolte-shared` plugin scope; this spec is portfolio-wide guidance for repositories that ship Ansible automation, but no Claude Code skill or agent in this plugin operationalises it. Repos that adopt the conventions consume the spec by reference and apply it through their own Ansible tooling (`ansible-playbook`, `ansible-lint`, Molecule).

## Context
Ansible playbooks are the executable layer that orchestrates reusable roles and collections against an inventory of target hosts. Across the nolte portfolio they bootstrap and maintain Linux devices ranging from servers to Raspberry-Pi-class edge hardware. This spec defines the best-practice baseline for the *playbook layer*: repository layout, inventory hygiene, vault and secrets handling, tagging discipline, variable precedence, dependency consumption, and CI gating. The *role layer* (the reusable units consumed via `requirements.yml`) is governed by [`spec/ansible/role-development/`](../role-development/en.md), and this spec deliberately doesn't repeat role-internal conventions.

Consumers: this repository consumes §Repository profiles indirectly. `spec/project/project-structure/` §Source layout cites it for the inventory-tree profiles, and the `project-structure-reviewer` agent enforces that layout, so those rules are load-bearing here even though no skill or agent names this path. The authoring guidance below has no local consumer and isn't owed one: this repository ships no playbooks, and its readers are the portfolio's bootstrap and provisioning repositories. An inventory that greps skills and agents for this path finds nothing; that's a limit of the method, not an orphaned spec.

References:
- [Ansible Playbooks intro](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_intro.html)
- [Ansible Tips and Tricks (official best-practice guide)](https://docs.ansible.com/ansible/latest/tips_tricks/ansible_tips_tricks.html)
- [Inventory guide](https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html)
- [Vault guide](https://docs.ansible.com/ansible/latest/vault_guide/index.html)
- [Best practices for Ansible (community blog)](https://www.jeffgeerling.com/blog/2019/best-practices-ansible-2019)
- [DevSec Hardening Framework](https://dev-sec.io/)

## Goals
- Every playbook repository in the portfolio has a predictable layout that humans and AI agents can navigate without per-repo discovery
- Inventory data, secrets, and execution logic are cleanly separated so the same playbook can run across environments without code changes
- Reruns and `check_mode` dry-runs report zero changes against a converged host, so they're reliable diagnostic tools
- CI gates lint, syntax, and dry-run failures before any change reaches a host
- Roles are consumed as versioned, pinned dependencies; never copied directly into a playbook repository, except in the *single-environment-bootstrap* profile (see §Repository profiles), where roles encode device-specific configuration that isn't reused elsewhere

## Non-Goals
- Role-internal conventions (variable name prefixing, `defaults/` vs `vars/`, Molecule scenarios, Galaxy publishing); covered by `spec/ansible/role-development/`
- Choice of Ansible distribution channel (community-package vs Red Hat AAP)
- Choice of underlying OS or hardware target; the spec applies to any Linux target
- Concrete deployment topology or release-promotion process (separate spec / repo conventions)
- Provisioning of the Ansible control node itself (bootstrap of Python, `ansible-core`)

## Requirements

### Repository layout
- **MUST** organize a playbook repository per the active *Repository profile* (see below), and in any profile include `ansible.cfg` (project-local; never depend on the user's `~/.ansible.cfg`), `requirements.yml` (declares all consumed roles and collections), and `playbooks/` with one playbook file per orchestration target (for example `playbooks/bootstrap.yml`, `playbooks/deploy.yml`)
- **MUST NOT** keep inventory, `group_vars`, or `host_vars` data inside `playbooks/` or any role; the inventory tree is the single home of host- and group-scoped data
- **SHOULD** include a `README.md` at the repository root that lists the available playbooks, the supported environments (or the single target device, in the bootstrap profile), and the entry-point command per playbook

### Repository profiles
A playbook repository **MUST** declare itself as exactly one of the two profiles below. The choice governs the inventory layout (§Inventory conventions) and whether inline roles are allowed (§Dependency consumption). When in doubt, default to *multi-environment-fleet*.

- **multi-environment-fleet** (default): fleets, services, or devices that span multiple environments (`production`, `staging`, `dev`). Inventory lives at `inventories/<env>/hosts.yml` plus `inventories/<env>/group_vars/` and `inventories/<env>/host_vars/` per environment. Roles **MUST** arrive via `requirements.yml`; no top-level `roles/`. Every other requirement in this spec defaults to this profile.
- **single-environment-bootstrap**: a repository whose entire purpose is to bootstrap exactly one concrete machine, or a small fixed fleet of *identical* devices (for example one `Reachy Mini`, or four identical edge sensors), with no expectation of growing into multi-environment deployment. Inventory lives at `inventory/hosts.yml` plus `inventory/group_vars/` and `inventory/host_vars/` (no `<env>` segment). Inline `roles/<name>/` directories are permitted **only** for device-specific configuration that isn't reused by any other repository; the moment a second repository would consume the same role, the role **MUST** be extracted into its own role repo per `spec/ansible/role-development/` and consumed via `requirements.yml`. All other requirements of this spec (idempotent runs, secrets handling, naming and tagging, linting, CI gates) apply unchanged.

### Python toolchain
- **MUST** install `ansible-core` and every Python helper used by the toolchain (`ansible-lint`, `yamllint`, related plugins) inside a project-local Python virtual environment per `spec/project/project-structure/` §Python development; never rely on a system-wide or user-global Ansible install
- **MUST** pin runtime dependencies (`ansible-core`, plus any collection-side Python dependencies such as `requests`, `netaddr`, `kubernetes` for the relevant collections) in `requirements.txt`, and pin tooling-only dependencies (`ansible-lint`, `yamllint`) in `requirements-dev.txt`
- **SHOULD** wire Taskfile targets so `task install` provisions the virtual environment from those files and CI invokes the same target before running lint, syntax, and dry-run stages, so developer workstation and CI share one entry point
- There is deliberately **no** portfolio-wide minimum `ansible-core` version: the version floor stays per-repo (edge/Raspberry-Pi targets and control-node Python versions differ), and the explicit `requirements.txt` pin above is what guarantees reproducibility
- The CI runtime is left to the consuming repo; this spec deliberately doesn't mandate an execution-environment (EE) image. The load-bearing reproducibility guarantee is the project-local venv pinned via `requirements.txt` / `requirements-dev.txt` and the single shared install entry point above, not a container image

### Idempotent runs and check mode
- **MUST** make every play idempotent; a second invocation against an already-converged host reports zero changed tasks
- **MUST** ensure every play runs cleanly under `--check` (Ansible's `check_mode`); modules that can't honour check mode are wrapped with explicit `check_mode: false` only when no idempotent alternative exists
- **SHOULD** include `--diff` in every dry-run invocation so reviewers see what would change

### Inventory conventions
- **MUST** prefer static YAML inventories for stable infrastructure: `inventories/<env>/hosts.yml` in the *multi-environment-fleet* profile, `inventory/hosts.yml` in the *single-environment-bootstrap* profile
- **MUST** scope variables strictly: host-specific values in `host_vars/<host>.yml`, group-shared values in `group_vars/<group>.yml`, environment-shared defaults in `group_vars/all.yml` (in the *single-environment-bootstrap* profile, the `all.yml` defaults still apply, simply at the single-environment level)
- **MUST** place the `group_vars/` and `host_vars/` directories **next to the inventory file**, not at the repository root: Ansible resolves these directories relative to the inventory source (or the playbook directory), and a top-level `group_vars/` is silently ignored when the playbook lives under `playbooks/`
- **MUST NOT** declare inventory-bound variables in playbook `vars:` blocks; playbook-local `vars:` is reserved for play-internal helpers
- **MAY** use a dynamic inventory plugin when host enumeration must come from a source of truth (cloud, CMDB, Home Assistant); pin the plugin version via the consuming collection in `requirements.yml`

### Secrets handling
- **MUST** treat every secret (passwords, API tokens, signing keys, TLS material) as vaulted: encrypt with `ansible-vault` (per-file or per-string) or pass through a SOPS-encrypted file consumed via a community plugin
- **MUST NOT** commit a vault-password file (typical names `.vault-pass`, `vault_password_file`) to the repository; configure the path via `ansible.cfg` or the `--vault-password-file` flag and `.gitignore` the file by name
- **MUST NOT** commit any secret in plain text to a tracked file under `inventories/`, `playbooks/`, `group_vars/`, or `host_vars/`; the only acceptable form is a vault-encrypted block or an external reference
- **SHOULD** use vaulted *strings* (single values inline) for short secrets and vaulted *files* for entire variable groups, to keep diff readability high
- **MAY** integrate `sops` (or another external secret store like HashiCorp Vault) for environments where `ansible-vault` doesn't fit the operational model

### Naming and tagging
- **MUST** give every play a `name:` that reads as a goal (`Bootstrap base packages`), not as a tool action (`run apt`)
- **MUST** give every task a `name:` that describes the desired end state, not the module verb
- **MUST** assign `tags: [never]` to any task whose effect is destructive or non-recoverable (disk wipes, force reboots, certificate revocation), so the task only runs when explicitly opted in via `--tags`
- **SHOULD** apply tags consistently, with at least one of `bootstrap`, `config`, `deploy`, `verify` per task, so operators can target a slice with `--tags`

### Variable precedence
- **MUST** treat the consumed roles' `defaults/main.yml` as the only default layer; overrides flow through `group_vars/`, `host_vars/`, and (last resort) `--extra-vars`
- **MUST NOT** redefine a role's variable inside a playbook's `vars:` block when the same value belongs in `group_vars/` / `host_vars/`; playbook-`vars:` is reserved for play-internal helpers
- **SHOULD** prefix every playbook-level variable with a name that makes ownership obvious (`bootstrap_disk_layout`, not `disk_layout`) so it doesn't collide with role variables

### Dependency consumption
- **MUST** declare every role and collection used by the playbooks in `requirements.yml`
- **MUST** pin every Galaxy or Git source to a release tag (for example `version: 1.4.0` for Galaxy, `version: v1.4.0` for Git); never `master` / `main` or a moving branch
- **MUST NOT** inline a role into a *multi-environment-fleet* repository (no top-level `roles/` folder shadowing Galaxy roles); reusable units live in their own role repo per `spec/ansible/role-development/`. The *single-environment-bootstrap* profile **MAY** keep device-specific roles inline under top-level `roles/<name>/` per §Repository profiles; once such a role is consumed by a second repository it **MUST** be extracted
- **SHOULD** install dependencies into a project-local path (`ansible.cfg` `roles_path`, `collections_path`) so each repo is self-contained

### Linting
- **MUST** run `ansible-lint` and `yamllint` as a CI gate; both have to be green before a playbook can land on the integration branch
- **SHOULD** wire both linters into a `.pre-commit-config.yaml` so violations are caught locally before commit
- **SHOULD** keep linter exceptions inline (`# noqa`) and narrow rather than disabling rules globally; document the reason next to each exception

### CI pipeline
- **MUST** include in CI: a lint stage (`ansible-lint`, `yamllint`), a syntax stage (`ansible-playbook --syntax-check`), and a dry-run stage (`ansible-playbook --check --diff`) against a representative test inventory
- **SHOULD** run a real apply against a Staging environment from CI (or via an explicit gated workflow) before any apply against Production; this stays a **SHOULD** (not a **MUST**), because not every multi-environment-fleet repo declares a staging environment that mirrors production, and concrete release-promotion is out of scope per §Non-Goals
- **SHOULD** publish the dry-run diff as a PR artifact so reviewers can read what would change without rerunning locally; the artifact's file format and retention are left to per-repo discretion (the spec mandates only that the diff is published, not how it's stored)

### Cross-references
- For role-internal conventions (Galaxy directory layout, `meta/argument_specs.yml`, `defaults/` vs `vars/`, Molecule, Galaxy publishing), see [`spec/ansible/role-development/`](../role-development/en.md)

## Acceptance Criteria
- [ ] Repository declares its profile (multi-environment-fleet or single-environment-bootstrap) in `README.md` or `CLAUDE.md`
- [ ] Repository contains `ansible.cfg`, `requirements.yml`, a `playbooks/` folder with one or more playbook files, and the inventory tree appropriate for its declared profile: `inventories/<env>/hosts.yml` plus `group_vars/` and `host_vars/` for at least one environment (multi-environment-fleet), or `inventory/hosts.yml` plus `inventory/group_vars/` and `inventory/host_vars/` (single-environment-bootstrap)
- [ ] `group_vars/` and `host_vars/` live next to the inventory file (under `inventories/<env>/` or `inventory/`), not at the repository root
- [ ] `requirements.txt` pins `ansible-core` (and any collection-side Python dependencies); `requirements-dev.txt` pins `ansible-lint` and `yamllint`
- [ ] CI invokes the same install path that local Taskfile targets use, so developer workstation and CI share one entry point
- [ ] No tracked file under `inventories/`, `playbooks/`, `group_vars/`, or `host_vars/` contains a secret in plain text; every secret is vault-encrypted or sourced from an external store
- [ ] Vault-password file (typical names `.vault-pass`, `vault_password_file`) isn't tracked and is listed in `.gitignore`
- [ ] Every entry in `requirements.yml` pins a Galaxy or Git source to a release tag, not a moving branch
- [ ] In a *multi-environment-fleet* repository, no top-level `roles/` directory shadows Galaxy roles; all roles arrive via `requirements.yml`. In a *single-environment-bootstrap* repository, every inline role under `roles/<name>/` is device-specific and not consumed by any other repository
- [ ] Every play and every task in `playbooks/` has a `name:` field
- [ ] Every play converges with zero changed tasks on a second run against the same host
- [ ] CI runs `ansible-lint`, `yamllint`, `ansible-playbook --syntax-check`, and `ansible-playbook --check --diff` against a test inventory; all four are required for merge
- [ ] At least one tagged execution slice (`--tags bootstrap`, `--tags deploy`, …) is documented in `README.md`
- [ ] No playbook `vars:` block redefines a variable that already exists in any consumed role's `defaults/main.yml`

## Open Questions

_All previously deferred open questions were settled on 2026-06-06: each provisional default is now the standing rule. The per-item decisions and rationale are preserved in git history (decision log, 2026-06-06)._
