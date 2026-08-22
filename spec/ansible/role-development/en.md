# Ansible Role Development Best Practices

Status: draft
Implementation: documentary-only—Ansible automation lives outside the `nolte-shared` plugin scope; this spec is portfolio-wide guidance for repositories that ship Ansible roles, but no Claude Code skill or agent in this plugin operationalises it. Role authors consume the spec by reference and apply it through their own Ansible tooling (`ansible-galaxy`, `ansible-lint`, Molecule).

## Context
Ansible roles are the reusable units that a playbook repository consumes via `requirements.yml`. They encapsulate idempotent state-management logic for a focused responsibility (install `nginx`, harden SSH, bootstrap a base OS) so the same logic can be reused across environments and projects. This spec defines the best-practice baseline for the *role layer*: Galaxy-conformant directory layout, role interface (argument specs, metadata, dependencies), variable hygiene, idempotent behaviour, naming, testing with Molecule, linting, semantic versioning, and Galaxy publishing. The consuming *playbook layer* is governed by [`spec/ansible/playbook-development/`](../playbook-development/en.md), and this spec deliberately doesn't repeat orchestration-level conventions (inventory, vault, CI dry-run).

Consumers: this repository consumes this spec indirectly. `spec/project/project-structure/` §Source layout cites it for the Galaxy-conformant role directories of a standalone role repository, and the `project-structure-reviewer` agent enforces that layout, so those rules are load-bearing here even though no skill or agent names this path. The authoring guidance below has no local consumer and isn't owed one: this repository ships no roles, and its readers are the portfolio's role repositories. An inventory that greps skills and agents for this path finds nothing; that's a limit of the method, not an orphaned spec.

References:
- [Reusing roles (official guide)](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_reuse_roles.html)
- [Developing collections](https://docs.ansible.com/projects/ansible/latest/dev_guide/developing_collections.html)
- [Galaxy: creating a role](https://galaxy.ansible.com/docs/contributing/creating_role.html)
- [Molecule (testing framework)](https://ansible.readthedocs.io/projects/molecule/)
- [`ansible-lint`](https://ansible.readthedocs.io/projects/lint/)
- [Tips and tricks (official practice guidance)](https://docs.ansible.com/projects/ansible/latest/tips_tricks/ansible_tips_tricks.html)
- [DevSec Hardening Framework](https://dev-sec.io/)

## Goals
- Every role in the portfolio is Galaxy-conformant so it can be installed via `ansible-galaxy install` or via `requirements.yml` without per-repo glue
- The role's public surface (variables, dependencies, supported platforms) is declared in metadata files so consumers can discover it without reading task code
- Variable name prefixing prevents collisions when multiple roles run inside the same play
- Every change to a role passes Molecule, `ansible-lint`, and `yamllint` before publishing
- Roles ship as semantically versioned artifacts so playbook repos can pin against a stable contract

## Non-Goals
- Orchestration-level conventions (inventory, `group_vars`, vault, CI dry-run); covered by `spec/ansible/playbook-development/`
- Choice of templating language beyond Jinja2 (the Ansible default)
- Concrete role business logic (what `nginx` config to ship, which packages to install)
- Multi-role meta-orchestration; that's the playbook's job

## Requirements

### Galaxy-conformant directory layout
- **MUST** include the Galaxy-conformant subdirectories in any role: `defaults/`, `vars/`, `tasks/`, `handlers/`, `templates/`, `files/`, `meta/`
- **MUST** include a `tasks/main.yml` as the role's entry point; further task files are included via `import_tasks:` / `include_tasks:` from `main.yml`
- **MUST** include a `meta/main.yml` declaring `galaxy_info` (author, description, license, supported platforms, minimum Ansible version) and `dependencies` (other roles consumed transitively)
- **SHOULD** include `tests/` with at least a smoke-test playbook, and `molecule/` with at least a `default` scenario (see Testing with Molecule)
- **MAY** package the role inside a collection (`<namespace>/<collection>/roles/<role>/`) when shipping multiple related roles together; collection-level metadata then lives in `galaxy.yml`

### Python toolchain
- **MUST** install `ansible-core` and every Python helper used by the toolchain (`ansible-lint`, `yamllint`, `molecule`, related plugins) inside a project-local Python virtual environment per `spec/project/project-structure/` §Python development; never rely on a system-wide or user-global Ansible install
- **MUST** pin runtime dependencies (`ansible-core`, plus any collection-side Python dependencies such as `requests`, `netaddr`) in `requirements.txt`, and pin tooling-only dependencies (`ansible-lint`, `yamllint`, `molecule`, a Molecule driver plugin such as `molecule-plugins[docker]` or `molecule-plugins[podman]`, `testinfra` where used) in `requirements-dev.txt`
- **SHOULD** wire Taskfile targets so `task install` provisions the virtual environment from those files and CI invokes the same target before running lint, syntax, and Molecule stages, so developer workstation and CI share one entry point

### Role interface
- **MUST** declare a `meta/argument_specs.yml` for the role, with one `options:` entry per consumed variable specifying `type`, `description`, and `required` (and `default`, `choices`, `elements` where applicable)
- **MUST** keep `meta/argument_specs.yml` in sync with `defaults/main.yml`: every `defaults/` variable that's part of the role's public surface appears in `argument_specs.yml`
- **MUST** declare every transitive role the role depends on under `meta/main.yml` `dependencies:`; never call a sibling role with `import_role:` / `include_role:` and forget to record the dependency
- **SHOULD** document non-obvious variable interactions (mutually exclusive sets, conditional requirements) in the `description:` field of `argument_specs.yml`

### `defaults/` vs `vars/` discipline
- **MUST** place every overridable variable in `defaults/main.yml`; a consumer has to be able to override it via `group_vars`, `host_vars`, or `--extra-vars` without monkey-patching the role
- **MUST** restrict `vars/main.yml` to internal constants and derived values that the role itself owns (for example mapping a distribution family to a package name); never expose `vars/` values as the role's public knobs
- **MUST NOT** store any secret (password, token, key) in either `defaults/main.yml` or `vars/main.yml`; secrets arrive via the consuming playbook's vault layer
- **SHOULD** keep `defaults/main.yml` short and self-documenting; comments above each variable explain intent and link to the matching `argument_specs.yml` entry where relevant

### Idempotent runs and check mode
- **MUST** make every task idempotent: re-running the role on a converged host reports zero changed tasks
- **MUST** ensure every task is `check_mode`-safe; modules that can't honour check mode are gated with explicit `check_mode: false` only when no idempotent alternative exists, and are documented in the role's README
- **SHOULD** prefer Ansible-built-in modules over `command:` / `shell:`; when shell is unavoidable, guard the task with `creates:`, `removes:`, or an explicit `changed_when:` condition

### Naming
- **MUST** prefix every public role variable with the role name (`nginx_port`, not `port`; `chrony_servers`, not `servers`) so variables don't collide when multiple roles run in one play
- **MUST** prefix handler names the same way (`nginx | restart`, not `restart`) so notifications resolve unambiguously
- **MUST** give every task a `name:` field that describes the desired end state, not the module verb (`Ensure nginx is enabled`, not `service`)
- **SHOULD** name task files after their function (`tasks/install.yml`, `tasks/configure.yml`, `tasks/service.yml`) rather than by module category

### Testing with Molecule
- **MUST** include a `molecule/default/` scenario that converges the role and asserts idempotent behaviour (a second `converge` reports zero changes)
- **MUST** run `molecule test` (the full create/converge/idempotence/verify/destroy lifecycle) as a CI gate; merging to the integration branch requires it green
- **MUST NOT** use the `delegated` driver to verify that the role is idempotent because it bypasses the per-host state model
- **SHOULD** use the `docker` or `podman` driver, and include at least one verification step (`molecule verify` with `ansible.builtin.assert` or `testinfra`) covering the role's primary observable outcome. Roles that change observable runtime state (a running service, an open port, a deployed file) SHOULD treat the verify step as effectively mandatory.
- **MAY** add additional scenarios (`molecule/<scenario>/`) for distro-specific or topology-specific test matrices
- **SHOULD** provide one Molecule scenario per platform family declared in `meta/main.yml` `galaxy_info.platforms`, so the test matrix tracks the role's own stated support contract. The spec deliberately prescribes no portfolio-wide minimum matrix (Debian, RHEL, or otherwise)—the per-role platform list is the single source of truth, mirroring the per-repo environment-floor decision in [`spec/ansible/playbook-development/`](../playbook-development/en.md) §Python toolchain.

### Linting
- **MUST** run `ansible-lint` and `yamllint` as a CI gate; both have to be green before a role version can be tagged
- **SHOULD** enable `ansible-lint`'s `args` rule so argument-spec violations and `defaults/main.yml` ↔ `argument_specs.yml` drift surface in the existing lint gate; no separate validator is required
- **SHOULD** wire both linters into a `.pre-commit-config.yaml` so violations are caught locally before commit
- **SHOULD** keep linter exceptions inline (`# noqa`) and narrow rather than disabling rules globally; document the reason next to each exception

### Versioning
- **MUST** version every released role with semantic versioning on Git tags (`v1.4.2`, never just `1.4` or `latest`)
- **MUST** treat the role's public surface as a stability contract: breaking changes to `argument_specs.yml`, `defaults/main.yml` defaults, or `meta/main.yml` `dependencies:` require a major-version bump
- **SHOULD** ship variable renames/removals with one minor version carrying an Ansible `deprecated`/`warn` notice before the major bump; dependency and default-value breaks MAY go straight to the major bump
- **SHOULD** maintain a `CHANGELOG.md` (or release-drafter output) that lists changes per tagged version

### Galaxy publishing
- **MUST** publish the role (or the containing collection) so consuming playbook repos can pin to it via `requirements.yml`; standalone roles publish via `ansible-galaxy role import`, collections via `ansible-galaxy collection publish`. Single-role repos default to standalone-role publishing; adopt a collection (`galaxy.yml`) once the repo ships a second related role, in line with the collection-centric direction the ecosystem took with Ansible 2.10. Standalone roles aren't deprecated, but they're positioned as legacy content on Galaxy: the CLI import path is still documented and current, while the web-UI role import was dropped when Galaxy moved to Galaxy NG in 2023 (see §Sources).
- **SHOULD** drive publishing from a CI workflow triggered on tag push, not from a developer's machine, so every release is reproducible
- **MAY** publish to a private Galaxy / Pulp instance when the role is portfolio-internal; the consuming playbook's `requirements.yml` then uses the matching `source:` URL

### Cross-references
- For orchestration-level conventions (inventory, vault, CI dry-run, tags), see [`spec/ansible/playbook-development/`](../playbook-development/en.md)

## Acceptance Criteria
- [ ] Role contains `defaults/`, `vars/`, `tasks/main.yml`, `handlers/`, `templates/`, `files/`, `meta/main.yml` (subdirectories with content as needed; `meta/main.yml` is mandatory)
- [ ] `requirements.txt` pins `ansible-core` (and any collection-side Python dependencies); `requirements-dev.txt` pins `ansible-lint`, `yamllint`, `molecule`, and a Molecule driver plugin (`molecule-plugins[docker]` or `molecule-plugins[podman]`)
- [ ] CI invokes the same install path that local Taskfile targets use, so developer workstation and CI share one entry point
- [ ] `meta/main.yml` declares `galaxy_info` (author, description, license, platforms, `min_ansible_version`) and `dependencies`
- [ ] `meta/argument_specs.yml` exists and lists every public variable from `defaults/main.yml` with `type`, `description`, and `required`
- [ ] `defaults/main.yml` and `vars/main.yml` contain no secret value; secrets arrive from the consuming playbook
- [ ] Every public variable in `defaults/main.yml` is prefixed with the role name
- [ ] Every task in `tasks/` has a `name:` field
- [ ] Re-running the role on a converged host reports zero changed tasks
- [ ] `molecule/default/` exists, uses the `docker` or `podman` driver, and asserts idempotent behaviour; `molecule test` runs in CI as a required check
- [ ] `ansible-lint` and `yamllint` run as CI gates and are green on the head commit
- [ ] Released versions are Git-tagged with semantic versioning (`vMAJOR.MINOR.PATCH`); a breaking change to `argument_specs.yml`, `defaults/main.yml`, or `meta/main.yml` `dependencies:` carries a major-version bump
- [ ] The role (or its containing collection) is published to a Galaxy / Pulp endpoint that the consuming playbook's `requirements.yml` pins to a tagged release

## Open Questions
_None at this time._

## Sources

The ecosystem-direction assertion in §"Galaxy publishing" is an author-time external assertion triangulated per `spec/claude/research-triangulate/` §Author-time assertions (author-time tier: at least three independent sources, ordered Primary-first). Retrieval date for every source below: 2026-07-24.

- **Ansible 2.10 executed the split that made collections the ecosystem's distribution format**: Ansible, "Ansible 2.10 porting guide" ("In Ansible 2.10, many plugins and modules have migrated to Collections on Ansible Galaxy") (Primary), <https://docs.ansible.com/projects/ansible/latest/porting_guides/porting_guide_2.10.html>; Ansible, "Developing collections" ("Collections are a distribution format for Ansible content") (Primary), <https://docs.ansible.com/projects/ansible/latest/dev_guide/developing_collections.html>; Opensource.com, "5 tips for choosing an Ansible collection" ("In August 2020, Ansible issued its first release since the developers split the core functionality from the vast majority of its modules and plugins") (Secondary), <https://opensource.com/article/21/3/ansible-collections>; ATIX AG, "Ansible Collections: more clarity and easier sharing" (Secondary), <https://atix.de/en/blog/ansible-collections/>
- **A repo shipping several related roles is the documented trigger for adopting a collection**: Ansible, "Migrating Roles to Roles in Collections on Galaxy" ("distribute many roles in a single cohesive unit of reusable automation"; shared plugins "instead of duplicating them") (Primary), <https://docs.ansible.com/projects/ansible/latest/dev_guide/migrating_roles.html>; Ansible, "Distributing collections," requiring `galaxy.yml` and documenting `ansible-galaxy collection publish` (Primary), <https://docs.ansible.com/projects/ansible/latest/dev_guide/developing_collections_distributing.html>; Red Hat, "Ansible Content Collections" ("the essential building blocks of automation") (Secondary, vendor), <https://www.redhat.com/en/technologies/management/ansible/content-collections>
- **Standalone-role publishing survives via the CLI and is positioned as legacy, not deprecated**: Ansible, `ansible-galaxy` CLI reference, documenting `role import` alongside `collection publish` (Primary), <https://docs.ansible.com/projects/ansible/latest/cli/ansible-galaxy.html>; Galaxy NG user guide, which files standalone roles under the "Legacy" navigation and its v1 API while keeping `ansible-galaxy role import` current (Primary), <https://docs.ansible.com/projects/galaxy-ng/en/latest/community/userguide.html>; Red Hat, "The new Ansible Galaxy," whose feature comparison drops the GitHub role-import UI with the note that publishing collections is the recommendation and existing roles stay maintainable via the CLI (Primary, vendor announcement), <https://www.redhat.com/en/blog/new-ansible-galaxy>

Verified 2026-07-24: no deprecation or sunset of Galaxy's standalone-role content type has been announced. What was retired is adjacent and easy to confuse with it—the legacy Galaxy codebase (now read-only) and the Galaxy v2 API—so the requirement above keeps standalone publishing as the single-role default while naming collections as the direction of travel.
