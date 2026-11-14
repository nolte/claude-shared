# Requirements — nolte-linux plugin (Linux image and appliance development)

<!--
Produced via the `requirements-elicit` skill, following
spec/project/requirements-elicitation/.
`c_d` is an uncertainty proxy (self-consistency-derived), not a calibrated
probability. A requirement is `confirmed` only after an explicit teach-back.
-->

## Bounded context

- **What:** a sixth plugin, `nolte-linux` (`plugins/nolte-linux/`), for Linux system and appliance development: bootable images, systemd integration, A/B update and rollback, and boot verification.
- **For whom:** only repositories that build Linux images or appliances. They install it on top of `nolte-shared`; `nolte-engineering` is recommended, not required.
- **Split rationale (distribution contract):** the consumer audience, with runtime and dependency needs as a secondary signal (`qemu-system-*`, OVMF, and the toolchain itself). Topic alone is not the rationale.
- **Toolchains in scope:** mkosi and the systemd ecosystem (systemd-repart, UKI, systemd-sysupdate), Yocto/Buildroot, Debian/Ubuntu images (debootstrap, live-build, debos), NixOS/OSTree, and bootc.
- **Out of scope:** kernel module and kernel-configuration development, standalone daemon and CLI tool development, a real QEMU boot inside this repository's CI, and per-toolchain artifacts.

## Understanding KPI

- Thresholds: `τ_low = 0.4`, `τ_high = 0.8`, self-consistency `k = 2`, question budget = `6` (spec defaults; 4 interview turns used)
- Revisit 2026-11-14: R11 added after the readiness reviews of both specs surfaced free-text declarations a scanner can't decide; one further question, answered.
- `U_gate = min_d c_d` over required dimensions = **0.80**
- Termination: `saturation` (every remaining open point is either fixed by repository policy or carried as a named assumption below)

### Gap matrix

| Dimension | Applicable | `c_d` | Uncertainty source | Evidence event |
|---|---|---|---|---|
| `functional` | yes | 0.85 | specification | Plan §3 artifact table; turns 2–3 (spec split, boot-verify kind) |
| `non_functional` | yes | 0.80 | interpretation | Turn 3: fail-closed on missing host tooling; description routing budget (plan §5 invariant) |
| `constraints` | yes | 0.90 | specification | Plan §5 invariants (lockstep, EN canonical, naming); turn 3: `nolte-engineering` only recommended |
| `domain_objects` | yes | 0.80 | interpretation | Plan §1 toolchain list; turn 2: one core spec plus per-toolchain profiles (k=2 readings: profiles vs. per-toolchain specs, resolved) |
| `actors` | yes | 0.85 | interpretation | Turn 1 teach-back of the consumer audience |
| `acceptance_criteria` | yes | 0.85 | specification | Turn 4: static checks and dogfooding; no real boot in the PR |
| `edge_cases` | yes | 0.80 | specification | Turn 3: missing QEMU/OVMF/KVM leads to `not-run` plus a diagnosis; TCG fallback only with a warning |
| `scope_boundaries` | yes | 0.90 | specification | Turn 1: MVP is images plus units/packaging; kernel and daemons excluded |

## Requirements

- **R1:** The repository SHALL ship a sixth plugin `nolte-linux` under `plugins/nolte-linux/`. Its `plugin.json` version SHALL equal the current lockstep release line, and its distribution-contract rationale SHALL be the consumer audience, with runtime dependencies as a secondary signal.
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: turn 1 teach-back of plan §1
- **R2:** The plugin's MVP SHALL cover image/appliance composition, A/B update and rollback, boot verification, and systemd units and packaging *as part of an image*. Kernel modules, kernel configuration, and standalone daemon or CLI development SHALL be out of scope.
  - _dimension_: `scope_boundaries` · _status_: `confirmed` · _source_: turn 1 "Image + Units/Pakete"
- **R3:** A single spec `spec/project/linux-image-best-practices/` (EN canonical plus DE) SHALL govern the plugin. It SHALL have a toolchain-neutral core (composition, minimisation, boot-chain hardening, A/B update/rollback, reproducibility, SBOM, systemd unit hygiene) and one profile section for each in-scope toolchain.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: turn 2 "Eine Spec + Profile"
- **R4:** Boot verification SHALL be specified as a realisation of the existing E2E tier in a spec `spec/project/image-boot-verification/` (EN plus DE). The closed tier taxonomy of `test-pyramid-foundation` SHALL NOT be extended; the foundation gains at most a reference to the new spec.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: turn 2 "E2E-Realisierung"
- **R5:** WHEN an operator asks to verify that an image boots, the `image-boot-verify` **skill** SHALL check host tooling, boot the image in QEMU, assert the boot target and health over the serial console, and write a protocol plus the serial log.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: turn 3 "Skill"
- **R6:** IF `qemu-system-*` or OVMF is missing, THEN `image-boot-verify` SHALL return the verdict `not-run` with the list of missing tools and an install hint, and SHALL NEVER report a pass. IF only KVM is missing, it MAY fall back to TCG, but only with an explicit warning and an adjusted timeout.
  - _dimension_: `edge_cases` · _status_: `confirmed` · _source_: turn 3 "Abbruch + Diagnose"
- **R7:** `nolte-linux` SHALL require only `nolte-shared`. References to `nolte-engineering` capabilities SHALL degrade cleanly when that plugin isn't installed.
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: turn 3 "Nur empfohlen"
- **R8:** The plugin SHALL ship a read-only scanner agent `linux-image-scanner`, an audit skill `linux-image-audit` that dispatches it, and a generator agent `linux-image-developer`. Each detects the toolchain at runtime and reads R3's spec, and none of them overlaps with `dockerfile-audit`, `quality-gate`, or `deployment-*`.
  - _dimension_: `functional` · _status_: `assumed` (names and roles from plan §3 table, not individually confirmed) · _source_: plan §3
- **R9:** The new plugin SHALL be registered at every registration point listed in plan §2: marketplace, release-automation, catalog-sources, Taskfile `plugin:reload`, CLAUDE.md, README, AUDIENCES, docs using/lifecycle (EN+DE), portfolio.yml, and a `validate_skills` test case.
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: plan §2, repository policy (CLAUDE.md lockstep/sync rule)
- **R10:** The PR SHALL count as done WHEN `task lint`, `task test`, and `task docs` are green, `skill-review` and `agent-review` report no Critical finding, and `/skills` lists `nolte-linux:*` under `task plugin:reload`. A real boot run of `image-boot-verify` against a consumer image SHALL be filed as a follow-up issue rather than done in this PR.
  - _dimension_: `acceptance_criteria` · _status_: `confirmed` · _source_: turn 4 "Statisch + Dogfood"

- **R11:** Each image SHALL carry a machine-readable declaration in its own YAML file (`image-declaration.yaml` next to the image definition) governed by a versioned JSON Schema under `schemas/`. The audit and boot verification SHALL read the update model, boot-chain steps, health definition, and update switches from it instead of from free-text README sections.
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: follow-up question after the spec readiness reviews, "Eigene YAML + Schema"

## Surviving assumptions / open risks

- **R8 artifact names** (`linux-image-scanner`, `linux-image-audit`, `linux-image-developer`, `image-boot-verify`) come from the plan and haven't been confirmed one by one. They will be checked against `spec/claude/skill-agent-naming/` during authoring.
- **Unproven boot-verify behaviour:** R10 deliberately leaves `image-boot-verify` without a real run in this PR. Until the follow-up issue is done, its QEMU invocation is verified only statically.
- **Description routing budget** for the new plugin's agents hasn't been measured yet (`validate_skills.py` is the token authority).
