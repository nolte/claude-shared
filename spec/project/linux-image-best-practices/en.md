# Linux Image Best Practices

Status: draft
Portfolio-Scope: local

## Context

Some portfolio repositories don't ship an application. They ship a whole operating system: a disk image that boots, an appliance, an embedded firmware build, or a container that boots as an OS. The defaults of a naively built image are the wrong posture for that artifact. It floats on whatever the package mirror served that day, so two builds of the same commit differ. It bakes a machine identity and host keys into every copy. It ships the build toolchain. It has no way back when an update doesn't boot. And nobody can say what it contains. This spec turns the current upstream guidance into a normative checklist. The `linux-image-audit` skill enforces it, the `linux-image-developer` agent builds against it, and a reviewer holds an image definition to it.

The spec is **toolchain-neutral at its core and toolchain-specific only in its profiles**. The core (§A–§H) states each obligation once, independent of the build tool. §I maps every obligation onto the five in-scope build toolchain families: mkosi and the systemd ecosystem, Yocto and Buildroot, Debian/Ubuntu image builders, NixOS and OSTree, and bootc. §J states which obligations a static audit can decide and what it reports when it can't. Each image carries a machine-readable **image declaration** that records the facts neither a scan nor a boot can infer reliably. Tooling reads the spec and the declaration and detects the toolchain at runtime. There's no per-toolchain spec and no per-toolchain artifact. The requirement record `project/requirements/nolte-linux-plugin.md` holds this shape decision (its item R3) and the choice of a dedicated declaration file with a schema (its item R11).

The content comes from two research passes on 2026-11-14 across the UAPI Group specifications, the systemd documentation and man pages, the reproducible-builds.org `SOURCE_DATE_EPOCH` specification, the Yocto Project and Buildroot documentation, and the bootc, mkosi, mmdebstrap, `rpm-ostree`, and update-framework documentation. That none of the existing specs already covers this ground is established by a `grep -rli` over `spec/**/en.md` for `dm-verity`, `secure boot`, `systemd-repart`, `mkosi`, `yocto`, `buildroot`, `debootstrap`, `ostree`, `bootc`, `SOURCE_DATE_EPOCH`, and `unified kernel image`, which returned no file on 2026-11-14.

**Boundaries:** `spec/project/dockerfile-best-practices/` owns the content of a `Containerfile`/`Dockerfile`. For bootc it governs the build file, including base-image pinning and secrets in layers, and it exempts bootc images from its non-root `USER` pillar. `spec/project/artifact-signing/` owns signing and attestation of OCI artifacts. `spec/project/license-check/` owns license classification of the SBOM. `spec/project/image-boot-verification/` owns proving that an image boots, as a realisation of the E2E tier of `spec/project/test-pyramid-foundation/`. It's also where the properties of a built root filesystem get checked (§J). `spec/project/continuous-delivery/` owns the delivery pipeline around the build. This spec owns the **image definition**: what goes into the image, how it's pinned, how it boots, how it updates, and what it declares about itself.

**Readers:** maintainers of image-building repositories; the authors of the `linux-image-audit` skill, the `linux-image-scanner` agent, and the `linux-image-developer` agent; reviewers holding an image definition to this bar.

## Goals

- Every image build is **reproducible from pinned inputs**: the same commit yields the same image, so a security fix can be shown to change only what it should
- Every image is **free of per-machine identity and secrets** at build time, so copies of one image never share a machine ID, host keys, or credentials
- Every image updated in the field has a **rollback path that triggers automatically** when an update doesn't come up healthy
- Every image **declares what it contains** through a machine-readable SBOM
- The **boot chain** of an appliance can be verified end to end (Secure Boot, UKI, dm-verity, measured boot), with each step stated and its absence visible
- Services the image ships run **inside a systemd sandbox** rather than with the full privileges of the host
- One checklist applies to every toolchain, so an auditor moving between a Yocto repo and a mkosi repo checks the same contract, and an audit never reports a pass it couldn't establish

## Non-Goals

- Kernel development: kernel modules, kernel configuration fragments, and out-of-tree drivers (out of the plugin's MVP scope, per the requirement record's item R2)
- Development of standalone daemons or CLI tools that merely run on Linux; this spec covers their systemd unit only as part of an image
- Signing and attestation mechanics of OCI artifacts, owned by `spec/project/artifact-signing/`. Signing and attesting a non-OCI image artifact (a raw disk image, a firmware bundle) has no owning spec yet; this spec records the gap in its Open Questions rather than filling it
- License classification and NOTICE generation, owned by `spec/project/license-check/`
- Running the image and proving that it boots, owned by `spec/project/image-boot-verification/`
- Fleet management, device provisioning, and the update server side (an update server's API, rollout waves, device enrolment)
- Picking a toolchain for a project; the spec governs whichever toolchain the repository already uses

## Requirements

Requirements in a section marked **mandatory pillar** (§C, §D, §F, §G) are hard failures in an audit. A **MUST** in any other section is reported as a Warning, and a **SHOULD** as a Suggestion. §J decides when an audit reports a requirement as `not-decidable` instead.

### A. Image definition and image declaration

- **MUST** keep the complete image definition under version control in the repository: the build configuration, every overlay or extra tree, every package list, and every lock or manifest file the build resolves inputs from
- **MUST** ship one image declaration per image, a file named `image-declaration.yaml` next to the image definition that validates against `schemas/image-declaration-v1.0.schema.yaml`. The declaration names the image and its toolchain, its update model (`field-updated` or `reflash-only`), which boot-chain steps it implements (§E), its health definition (§A, as a unit name or a framework hook), and, for an image updated in the field, the switches boot verification uses (§F)
- **MUST** use exactly one primary toolchain per image, the one its declaration names
- **SHOULD** build an image through a single repository-declared entry point (a Taskfile target or an equivalent script), so CI and a developer run the same command
- **MUST** give every image a **health definition**: the point at which the image decides that a boot is healthy. On a systemd-based image that's a unit ordered before `boot-complete.target`; on an image whose update framework owns the commit (RAUC, SWUpdate, Mender, greenboot) it's that framework's health hook
- **MUST** make the health definition write one **health report line**, once it has decided, to every console the image configures, including a serial console, as a line that begins with `IMAGE-HEALTH-REPORT` followed by a space and has the form `IMAGE-HEALTH-REPORT status=<healthy|unhealthy> image_id=<id> image_version=<version> system_state=<state> failed_units=<comma-separated list or -> machine_id_app=<id or ->`. The `image_id` and `image_version` values are those of the booted system's `os-release`. `system_state` is the service manager's state at the moment of the report, which is `starting` while the health definition still gates `boot-complete.target`; `failed_units` lists the units failed at that moment. `machine_id_app` is the machine ID derived for the fixed application ID `6dc31fbecafb40ec9395fe013ebd2c7c` (systemd's app-specific machine ID), which lets a verifier compare two boots without exposing the raw machine ID [R7]. It's no secret, but it's a stable per-device pseudonym, so it serves only that comparison. All three carry real values whenever the image runs systemd, also when its health definition is a framework hook, and are `-` only on an image without systemd. Boot verification reads this line (`spec/project/image-boot-verification/` §F), so an image can be verified without an interactive shell on its console

### B. Composition and minimisation

- **SHOULD** install only what the image runs: no compilers, package-build tooling, or debuggers in a production image. Where the toolchain separates build and target environments (Yocto, Buildroot, mkosi tools trees, multi-stage bootc builds), the build tooling **MUST NOT** leak into the target root filesystem
- **SHOULD** exclude documentation, man pages, and locales the appliance doesn't use when the toolchain offers a switch for it
- **SHOULD** ship a read-only root filesystem (for example a dm-verity-protected `/usr`, an OSTree/bootc deployment, or a read-only squashfs/erofs) and keep mutable state under `/etc` and `/var`
- **MAY** use the UAPI Discoverable Partitions Specification (GPT partition type identifiers), so `systemd-gpt-auto-generator` finds root, `/var`, and other partitions without a hard-coded `/etc/fstab` [R2]

### C. Reproducibility and pinned inputs (mandatory pillar)

- **MUST** pin every external input to an immutable reference: package repositories to a dated snapshot, layers and source trees to a commit, and Nix inputs through a committed lock file. A build that resolves the newest version from a live mirror is a hard failure. For bootc, base-image pinning is governed by `spec/project/dockerfile-best-practices/` §"Base image pinning (mandatory pillar)" (tag plus digest) and isn't restated here
- **MUST** commit the lock or manifest file that records the pinned references, so the pin is reviewable in a pull request
- **MUST** pass a fixed `SOURCE_DATE_EPOCH` to the build, derived from the source (for example the timestamp of the last commit), never from the wall clock, unless the toolchain derives it from the source on its own (§I says where). The variable's semantics are defined by the reproducible-builds.org specification: output should look as if the build had happened at that timestamp [R4]
- **MUST** enable the toolchain's own reproducibility switch where one exists (§I)
- **SHOULD** pair every pin with an automated updater (Renovate or an equivalent), so a pin stays patched rather than silently ageing
- **SHOULD** check reproducibility by building twice and comparing the outputs (for example with `diffoscope`), and **SHOULD** remove or document known residual sources of non-determinism, such as a seed file written at build time or a filesystem image tool that stamps the current time [R6]

### D. No per-machine identity or secrets in the image (mandatory pillar)

- **MUST NOT** ship a fixed machine identity: no populated `/etc/machine-id`, and no fixed machine ID passed another way, such as on a kernel command line baked into the image. The file is either absent or empty (or `uninitialized`), so each machine generates its own ID on first boot [R7]
- **MUST NOT** ship SSH host keys, a random seed, TLS private keys, or any other per-machine secret. These are generated on first boot or provisioned at deployment [R7]
- **MUST NOT** bake credentials into any image layer, overlay, or build log. A build that needs a credential at build time **MUST** receive it through a mechanism that keeps it out of the output (a build-only environment that isn't copied into the target tree). For bootc, `spec/project/dockerfile-best-practices/` §"Secrets out of layers (mandatory pillar)" governs this and isn't restated here
- **SHOULD** use `systemd-firstboot` or an equivalent first-boot unit for per-machine setup instead of build-time scripts

### E. Boot-chain integrity

- **SHOULD** boot through a Unified Kernel Image (UKI): one signed UEFI PE file that combines the `systemd-stub` boot stub, the kernel, the initial RAM disk, and the kernel command line, per UAPI.5 [R1]. A kernel command line that lives outside the signed artifact can be changed without breaking the signature
- **SHOULD** sign the boot path for UEFI Secure Boot (shim or a directly enrolled key, the boot loader, and the UKI). The private signing key **MUST NOT** be stored in the repository or the image (it falls under §D)
- **SHOULD** protect the read-only root or `/usr` with dm-verity and bind the verity root hash into the signed UKI command line, so offline modification of the root filesystem is detected at boot [R9]
- **SHOULD**, when the image unlocks secrets through the TPM2, bind them to signed PCR policies (`systemd-measure`/`ukify` pre-calculating PCR 11 for the UKI, enrolled through `systemd-cryptenroll`) rather than to raw PCR values that break on every kernel update [R10]
- **MUST** record in the image declaration's `boot_chain` block, for each of these four steps, whether the image implements it or omits it, so an omission is a recorded decision and not an oversight

### F. Update and rollback (mandatory pillar for images updated in the field)

This section applies to every image whose declaration says `update_model: field-updated`, and to every image without a valid declaration, since an audit can't tell that such an image is never updated in place. An image whose declaration says `reflash-only` is exempt, and its declaration **MUST NOT** carry an `update` block; a declaration that does is a contradiction the audit reports as a failure of this section.

- An image updated in the field **MUST** update atomically: either a complete new version becomes active or the old one stays active. In-place package upgrades on a running appliance aren't an update mechanism under this spec
- Such an image **MUST** have a rollback path that **triggers automatically** when the new version doesn't come up healthy. Accepted mechanisms: systemd-boot Automatic Boot Assessment (boot counting with `systemd-bless-boot`, success only after `boot-complete.target`) [R3], an update framework's own commit-after-boot logic (RAUC, SWUpdate, Mender) [R12], or a deployment-based system's previous deployment (OSTree with greenboot, bootc, NixOS generations) combined with the image's health definition [R13], [R14], [R17]
- Its health definition (§A) **MUST** gate that rollback path, **MUST NOT** mark a boot good merely because the kernel started, and **MUST** reboot the system on its own after it reports `unhealthy`, so an unattended device reaches its rollback path without outside help
- Its health definition **MUST** honour a **failure switch**: a value the host passes without altering any signed boot component (a systemd credential, or an SMBIOS Type 11 string on an image without systemd), named in the declaration's `health.failure_switch`. When the switch's value names the running image version and that version hasn't been marked good yet, the health definition reports `unhealthy`; once a version is marked good, the switch has no effect on it, so the switch can't turn a committed system into a rollback. This is the hook through which boot verification proves the rollback path (`spec/project/image-boot-verification/` §I)
- Its update mechanism **MUST** accept its update source through a host-injectable switch named in the declaration's `update.source_switch`. When that source offers a version newer than the running one, the mechanism **MUST** install it and reboot into it without further input, and it **MUST** refuse a version that isn't newer, so the switch can't force a downgrade. The declaration **MUST** state in `update.max_boot_attempts` how many boots of an unhealthy version the rollback mechanism allows
- **SHOULD** use an A/B partition layout (or the deployment equivalent) sized for two complete versions. With `systemd-sysupdate`, the partitions **MUST** exist before the first update, since `systemd-sysupdate` doesn't create partitions; `systemd-repart` creates them [R5]
- **MUST** verify the signature of an update payload before installing it, whatever source the source switch names, since the switch lets the host redirect the source. The update framework's signing scheme is the mechanism; signing OCI artifacts is governed by `spec/project/artifact-signing/`

### G. SBOM (mandatory pillar)

- **MUST** produce a machine-readable SBOM in SPDX or CycloneDX format for every image build, generated from the build itself (the toolchain's native SBOM output where §I names one) or by an SBOM generator run against the finished root filesystem from the build entry point or the CI workflow
- **MUST** produce the SBOM in SPDX for an image published as an OCI artifact (bootc), because `spec/project/artifact-signing/` attests the SBOM of an OCI artifact as SPDX
- **MUST** publish the SBOM next to the image artifact it describes, so every published image has exactly one SBOM
- **MUST NOT** count Buildroot's `make legal-info` output as an SBOM on its own: it collects licenses and sources but isn't an SPDX or CycloneDX document [R8]
- License classification of the SBOM is delegated to `spec/project/license-check/`, and signing or attesting it as an OCI artifact to `spec/project/artifact-signing/`

### H. systemd unit hygiene

- **SHOULD** run every service the image ships with systemd sandboxing appropriate to it (`ProtectSystem=strict` with explicit `ReadWritePaths=`, `ProtectHome=`, `PrivateTmp=`, `NoNewPrivileges=`, `DynamicUser=` or a dedicated system user, `CapabilityBoundingSet=`), and **SHOULD** add hardening to packaged units through drop-ins rather than by editing the vendor unit [R11]
- **SHOULD** record `systemd-analyze security <unit>` exposure scores for the image's own units as a review aid. The score reflects which systemd features are in use, not the application's security, so it **MUST NOT** be used as a pass/fail threshold on its own [R11]
- **SHOULD** make the health definition (§A) depend on the services the appliance exists to run, so a healthy report means those services are up
- **MUST NOT** enable network-facing services the appliance doesn't need

### I. Toolchain profiles

The profiles map the core onto each toolchain. They name detection signals and the knob that satisfies a core requirement. A profile never adds an obligation the core doesn't state. Knob names drift between toolchain releases, so an implementation **MUST** read them against the toolchain version the repository pins. An entry that feeds a mandatory pillar and rests on fewer independent sources than `spec/claude/research-triangulate/` requires is marked **[unverified]**; §J governs how an audit treats it. Entries that feed only advisory sections carry no marker; their source count is in the References. The declaration's `image.toolchain` selects the profile; the detection signals below confirm it and locate the definition files.

#### I.1 mkosi and the systemd ecosystem

- Detection: `mkosi.conf`, `mkosi.conf.d/`, or `mkosi.*` directories
- §C: `SourceDateEpoch=` [R15] **[unverified]**; the distribution mirror pinned to a snapshot, a setting whose name this research pass didn't establish **[unverified]**
- §E: `UnifiedKernelImages=`, `SecureBoot=` with the signing key supplied from outside the repository, `Verity=` (the verity hash goes into its own GPT partition, which implies a read-only root) [R9], [R15]
- §F: `systemd-sysupdate` transfer definitions under `sysupdate.d/` plus `systemd-repart` definitions for the A/B partitions [R5]; boot counting through systemd-boot [R3]
- §G: no native SBOM output is assumed; an SBOM generator runs against the output root from the build entry point or CI

#### I.2 Yocto and Buildroot

- Detection, Yocto: `conf/local.conf`, `conf/bblayers.conf`, `meta-*` layers, or a `kas` YAML file. Detection, Buildroot: a `configs/*_defconfig` or a `BR2_EXTERNAL` tree
- §C, Yocto: every layer pinned to a commit (a `kas` lock file or a `repo` manifest with revisions). Reproducible builds are the default since release 3.1, and OE-Core derives `SOURCE_DATE_EPOCH` from the source on its own; a configuration that sets `BUILD_REPRODUCIBLE_BINARIES = "0"` disables them [R16] **[unverified]**, so the audit reports it `not-decidable` with a Warning, not `fail`
- §C, Buildroot: `BR2_REPRODUCIBLE=y`, which honours `SOURCE_DATE_EPOCH` and otherwise derives it from the last commit [R18] **[unverified]**
- §G, Yocto: SPDX output from the `create-spdx` class, which current releases enable through `INHERIT_DISTRO` by default and older releases need through `INHERIT += "create-spdx"` [R8]. §G, Buildroot: a separate SPDX or CycloneDX generator, since `legal-info` isn't an SBOM [R8]
- §F: an update framework layer or package (RAUC, SWUpdate, Mender) with its rollback logic enabled [R12]

#### I.3 Debian and Ubuntu image builders

- Detection: an `mmdebstrap` or `debootstrap` invocation in the build entry point, a live-build `auto/config`, or a `debos` recipe (`*.yaml` with `architecture:` and `actions:`)
- §C: the archive pinned to a `snapshot.debian.org` timestamp, with `SOURCE_DATE_EPOCH` set to the same moment. `mmdebstrap` produces reproducible `chroot` trees when `SOURCE_DATE_EPOCH` is set. Snapshot archives need `Acquire::Check-Valid-Until "false"`, since their Release files carry an old date [R6]
- §D: delete `/etc/machine-id` contents, `/var/lib/systemd/random-seed`, and the SSH host keys at the end of the build [R6], [R7]
- §G: no native SBOM output; an SBOM generator runs against the finished root from the build entry point or CI

#### I.4 NixOS and OSTree

- Detection, NixOS: `flake.nix` with `nixosConfigurations`, or `configuration.nix`. Detection, OSTree: a compose definition (`*.json`/`*.yaml` consumed by `rpm-ostree compose`) or an `ostree` repository in the build
- §C, NixOS: a committed `flake.lock` pinning every input [R13]. How Nix derivations keep timestamps independent of the wall clock wasn't established by this research pass, so the `SOURCE_DATE_EPOCH` mapping for NixOS is **[unverified]**
- §F, NixOS: generations provide the previous deployment (`nixos-rebuild switch --rollback`, or the boot menu); garbage collection removes rollback targets, so the image **SHOULD** keep at least one previous generation. Boot counting is available for systemd-boot [R13]
- §F, OSTree: deployments are ordered boot loader entries; `rpm-ostree rollback` makes the previous deployment the default, and greenboot health checks trigger an automatic return to the previous deployment after repeated failed boots of an update [R17]
- §C, OSTree: the package repositories of the compose definition pinned to snapshots; how `rpm-ostree compose` handles `SOURCE_DATE_EPOCH` wasn't established by this research pass **[unverified]**
- §G: no native SBOM output is assumed; an SBOM generator runs against the built system closure or the committed tree from the build entry point or CI

#### I.5 bootc

- Detection: a declaration with `image.toolchain: bootc`, or a `Containerfile`/`Dockerfile` that sets the label `containers.bootc 1` itself, the label bootc-compatible base images carry [R19]. Whether a derived image inherits that label from its base wasn't established, so a derived build relies on the declaration
- The build file is governed by `spec/project/dockerfile-best-practices/`, which exempts bootc images (by either signal above) from its non-root `USER` pillar: a bootc image is the host operating system, so its final user is root by design
- §F: `bootc upgrade` stages a new image atomically; `bootc rollback` makes the previous deployment boot next and discards a staged upgrade that hasn't been applied yet [R14]. Packages **MUST NOT** be upgraded on a running bootc system; changes go into a rebuilt image [R14]
- §C: how a bootc build passes `SOURCE_DATE_EPOCH` into the image layers wasn't established by this research pass **[unverified]**
- §G: an SPDX SBOM of the image, attested per `spec/project/artifact-signing/`
- Disk images are produced with `bootc-image-builder` (or its successor) from the pinned image digest [R14]

### J. Audit decidability

- An audit **MUST** report every requirement as exactly one of `pass`, `fail`, or `not-decidable`, and **MUST NEVER** count `not-decidable` as a pass. A requirement outside the mandatory pillars keeps its Warning or Suggestion severity for either non-passing result
- Every `not-decidable` result **MUST** carry exactly one cause, and a gate that sums the audit treats it by that cause:
  - `resolvable: <scenario>`: a `needs-built-artifact` requirement that a named boot-verification scenario resolves. It blocks the gate like a `fail` until that scenario passes
  - `unverified: <§I entry>`: the decision rests on an **[unverified]** §I entry. It's a Warning that doesn't block, since the gap lies in this spec's research, not in the repository
  - `spec-gap: <reason>`: neither a §I knob nor a boot-verification scenario covers the requirement yet (the table says so in its row). It's a Warning that doesn't block, for the same reason
  - `delegated: <spec>`: another spec owns the check for this toolchain (the bootc build file), and its audit decides it. It doesn't block once that audit's result for the same revision is at hand; while it isn't (the owning audit wasn't run, or its plugin isn't installed), it blocks like `resolvable`, so a pillar is never passed unchecked
  - `evidence: <reason>`: the audit's own input is missing (the declaration validator's result or the tracked-file list), or the only evidence for the result is a statement inside the audited content. It blocks like `resolvable` in a mandatory pillar and in the declaration check, since the gap lies in this run, not in the spec, and is a Warning elsewhere
- Each mandatory-pillar requirement belongs to one decidability class, which fixes what a static audit can conclude:

  | Requirement | Class | What the static audit checks |
  |---|---|---|
  | §C inputs pinned | static-heuristic | Lock or manifest files and snapshot settings named in §I; a profile without a named pinning knob yields `not-decidable` (cause `spec-gap`) |
  | §C lock file committed | static-file | The lock or manifest file exists and is tracked |
  | §C `SOURCE_DATE_EPOCH` from source | static-heuristic | The entry point or knob computes it from the source at build time; a wall-clock expression or a committed literal, which goes stale with the next commit, is a `fail` |
  | §C reproducibility switch | static-file | The §I knob for the toolchain |
  | §D no populated `machine-id` | needs-built-artifact | Only an overlay tree or recipe step that writes the file; otherwise `not-decidable`, resolved by the identity scenario of `spec/project/image-boot-verification/` §I (cause `resolvable`); for an image without systemd, which reports `machine_id_app=-`, the cause is `spec-gap` |
  | §D no host keys or secrets | static-heuristic | Committed key files in overlay trees and a secret scan of the definition |
  | §D no credentials in layers or logs | static-heuristic | Credential patterns in the definition and the entry point, and a build-only mechanism for any build-time credential |
  | §F applicability | static-file | The declaration's `update_model` |
  | §F atomic update, automatic rollback | static-heuristic | The update mechanism and rollback signals named in §I |
  | §F failure and source switches, `max_boot_attempts` | static-file | The declaration's `health.failure_switch` and `update` block |
  | §F health definition gates rollback | static-heuristic | The unit or hook the declaration's `health.definition` names exists, and a unit is ordered before `boot-complete.target` |
  | §F install and reboot without input, unhealthy reboot | needs-built-artifact | Resolved by the rollback scenario of `spec/project/image-boot-verification/` §I |
  | §F payload signature verified | static-heuristic | The update framework's signature or keyring setting; no §I profile names that knob yet, so the result is `not-decidable` (cause `spec-gap`) until one does |
  | §F no `update` block on `reflash-only` | static-file | The declaration |
  | §F refuses a version that isn't newer, switch ignored once committed | needs-built-artifact | Not covered by a boot-verification scenario yet; reported `not-decidable` (cause `spec-gap`) |
  | §G SBOM produced | static-heuristic | A native SBOM knob from §I, or a generator invocation in the entry point or CI |
  | §G SPDX for OCI images | static-heuristic | The generator's output format for a declaration with `image.toolchain: bootc` |
  | §G not `legal-info` alone | static-heuristic | A generator invocation besides `make legal-info` |
  | §G SBOM published next to the image | static-heuristic | A publish step in the entry point or CI that uploads the SBOM with the image |

- A requirement of class `needs-built-artifact` **MUST** be reported `not-decidable` by the static audit whenever the recipe side gives no answer. Where the table names a boot-verification scenario, that scenario resolves it on the running image (cause `resolvable`); where it names none, the cause is `spec-gap`
- A §I entry marked **[unverified]** **MUST NOT** turn a requirement into `fail`. When the decision rests on it, the audit reports `not-decidable` and names the unverified entry

## Acceptance Criteria

These criteria roll up the requirements above; every requirement stays normative on its own.

- [ ] `spec/project/linux-image-best-practices/` exists with `en.md` (canonical) and `de.md` (translation) and is listed in `spec/README.md`
- [ ] §A requires one `image-declaration.yaml` per image that validates against `schemas/image-declaration-v1.0.schema.yaml`, a health definition for every image, and the `IMAGE-HEALTH-REPORT` console line with its field list, its serial-console requirement, and the moment `system_state` is sampled
- [ ] The severity rule is stated: a requirement in a mandatory pillar (§C, §D, §F, §G) is a hard failure, a MUST elsewhere a Warning, a SHOULD a Suggestion
- [ ] §C requires pinned inputs, a committed lock file, a source-derived `SOURCE_DATE_EPOCH`, and the toolchain's reproducibility switch, and delegates bootc base-image pinning to `spec/project/dockerfile-best-practices/`
- [ ] §D forbids a fixed machine identity (a populated `/etc/machine-id` or a fixed machine ID passed another way), per-machine secrets, and credentials in any layer, overlay, or log
- [ ] §E requires the declaration's `boot_chain` block to record each of the four boot-chain steps as implemented or omitted
- [ ] §F applies to every image not declared `reflash-only`, names the accepted automatic-rollback mechanisms, and requires a health definition that gates rollback and reboots after an unhealthy report, a failure switch that's ignored once a version is committed, an update source switch that installs and reboots without further input and refuses a version that isn't newer, payload signature verification, and `max_boot_attempts`, and forbids an `update` block on a `reflash-only` declaration
- [ ] §G requires an SPDX or CycloneDX SBOM per build, SPDX for OCI images, publication next to the artifact, and rejects `make legal-info` alone
- [ ] §I has one profile per in-scope toolchain (mkosi/systemd, Yocto/Buildroot, Debian/Ubuntu, NixOS/OSTree, bootc), each naming its detection signal and its §C, §F, and §G mapping, with every under-sourced entry that feeds a mandatory pillar marked **[unverified]**
- [ ] Every toolchain-specific knob a requirement is checked against appears in §I; the core names tools only as examples or in rules that apply only while that tool is in use
- [ ] §J assigns a decidability class to every mandatory-pillar requirement, forbids counting `not-decidable` as a pass, gives every `not-decidable` one of five causes that decide whether it blocks, routes built-artifact checks to named boot-verification scenarios, keeps an **[unverified]** entry from producing `fail` or blocking a gate, and applies the same three results outside the mandatory pillars
- [ ] `spec/project/dockerfile-best-practices/` exempts bootc images, recognised by the declaration or the label, from its non-root `USER` pillar, and the `dockerfile-audit` skill and its scanner apply that exemption
- [ ] Signing, license classification, and boot verification are delegated to `spec/project/artifact-signing/`, `spec/project/license-check/`, and `spec/project/image-boot-verification/` without restating them

## References

- Sources retrieved 2026-11-14. Source classes per `spec/claude/research-triangulate/` §"Source classes and independence": **Primary** and **Secondary**.
- [R1] UAPI.5 Unified Kernel Images (**Primary**): <https://uapi-group.org/specifications/specs/unified_kernel_image/>; systemd, "The recommended way to boot a systemd based OS" (**Primary**): <https://systemd.io/ROOTFS_DISCOVERY/>
- [R2] UAPI.2 Discoverable Partitions Specification (**Primary**): <https://uapi-group.org/specifications/specs/discoverable_partitions_specification/>; UAPI.3 Discoverable Disk Images (**Primary**): <https://uapi-group.org/specifications/specs/discoverable_disk_image/>
- [R3] systemd, "Automatic Boot Assessment" (**Primary**): <https://systemd.io/AUTOMATIC_BOOT_ASSESSMENT>; `systemd-bless-boot.service(8)` (**Primary**): <https://man.cs50.io/8/systemd-bless-boot.service>; Fedora IoT issue #12, "Boot Counting and Success Determination" (**Secondary**): <https://pagure.io/fedora-iot/issue/12>
- [R4] reproducible-builds.org, `SOURCE_DATE_EPOCH` specification (**Primary**): <https://reproducible-builds.org/specs/source-date-epoch>; reproducible-builds.org, `SOURCE_DATE_EPOCH` documentation (**Primary**): <https://reproducible-builds.org/docs/source-date-epoch/>; Yocto `reproducible_build.bbclass` (**Secondary**): <https://git.yoctoproject.org/poky/tree/meta/classes/reproducible_build.bbclass?h=2.8_M3>
- [R5] `systemd-sysupdate(8)` (**Primary**): <https://www.freedesktop.org/software/systemd/man/260/systemd-sysupdate.html>; `sysupdate.d(5)` (**Primary**): <https://www.mankier.com/5/sysupdate.d>; Igalia, "How to integrate systemd-sysupdate with your Yocto-based image" (**Secondary**): <https://blogs.igalia.com/mabente/how-to-integrate-systemd-sysupdate-with-your-yocto-based-image/>
- [R6] Debian Wiki, "Reproducible installs" (**Primary**): <https://wiki.debian.org/ReproducibleInstalls>; `mmdebstrap(1)` (**Primary**): <https://manpages.ubuntu.com/manpages/plucky/man1/mmdebstrap.1.html>; mmdebstrap commit "make bit-by-bit reproducible" (**Primary**): <https://gitlab.mister-muffin.de/josch/mmdebstrap/commit/134330d786a5680aff30849c4120a894466da358>; debian-hurd list, random-seed non-determinism (**Secondary**): <https://lists.debian.org/debian-hurd/2024/12/msg00006.html>
- [R7] systemd, "Safely Building Images" (**Primary**): <https://systemd.io/BUILDING_IMAGES>; `machine-id(5)`, including the app-specific machine ID (**Primary**): <https://www.man7.org/linux/man-pages/man5/machine-id.5.html>; Launchpad bug #2039434, "ubuntu-image leaving machine-id and host SSH keys in images" (**Secondary**): <https://launchpad.net/bugs/2039434>
- [R8] Yocto Project, "Creating a Software Bill of Materials" (**Primary**): <https://docs.yoctoproject.org/dev-manual/sbom.html>; AC6, "SBOM for embedded firmware" (**Secondary**): <https://www.ac6-formation.com/en/articles/sbom-embedded-firmware>; Foundries.io, "Creating SBOM for embedded devices" (**Secondary**): <https://foundries.io/insights/blog/creating-sbom-embedded-devices>
- [R9] `mkosi(1)`, `Verity=` (**Primary**): <https://manpages.debian.org/testing/mkosi/mkosi.1>; systemd-devel, "Is tpm2-measure-pcr really an additional security?" (**Secondary**): <https://lists.freedesktop.org/archives/systemd-devel/2025-March/051255.html>
- [R10] `systemd-measure(1)` (**Primary**): <https://www.freedesktop.org/software/systemd/man/260/systemd-measure.html>; `systemd-measure(1)` on man7.org (**Primary**): <https://www.man7.org/linux/man-pages/man1/systemd-measure.1.html>
- [R11] Arch Wiki, `systemd/Sandboxing` (**Secondary**): <https://wiki.archlinux.org/title/Systemd/Sandboxing>; Debian Wiki, `ServiceSandboxing` (**Secondary**): <https://wiki.debian.org/ServiceSandboxing>; Rocky Linux, "systemd hardening" (**Secondary**): <https://docs.rockylinux.org/guides/security/systemd_hardening/>
- [R12] Pengutronix, RAUC (**Primary**): <https://pengutronix.de/en/software/rauc.html>; FOSDEM 2025, "Exploring Open Source Dual A/B Update Solutions for Embedded Linux" (**Secondary**): <https://fosdem.org/schedule/event/fosdem-2025-6299-exploring-open-source-dual-a-b-update-solutions-for-embedded-linux>; Yocto Project Wiki, "System Update" (**Secondary**): <https://wiki.yoctoproject.org/wiki/System_Update>
- [R13] NixOS Discourse, "How to rollback an update done by `nixos-upgrade` when using flakes?" (**Secondary**): <https://discourse.nixos.org/t/how-to-rollback-an-update-done-by-nixos-upgrade-when-using-flakes/51010>; NixOS & Flakes Book, "Downgrade or upgrade packages" (**Secondary**): <https://nixos-and-flakes.thiscute.world/nixos-with-flakes/downgrade-or-upgrade-packages>; nixpkgs commit adding systemd-boot boot counting (**Primary**): <https://code.ornl.gov/nix/nixpkgs/-/commit/a6303da3a750d5aa759307f5d25859bd2d32fa2d>
- [R14] `bootc(8)` (**Primary**): <https://www.mankier.com/8/bootc>; Red Hat, "Managing RHEL bootc images" (**Primary**): <https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/using_image_mode_for_rhel_to_build_deploy_and_manage_operating_systems/managing-rhel-bootc-images>; CIQ, "bootc images" (**Secondary**): <https://docs.ciq.com/rlc/installation/bootc-images>
- [R15] `mkosi(1)` (**Primary**): <https://manpages.debian.org/testing/mkosi/mkosi.1>; `pacman` merge request 213 on a reproducible install date, which notes mkosi's `SOURCE_DATE_EPOCH` support (**Secondary**): <https://gitlab.archlinux.org/pacman/pacman/-/merge_requests/213>; All Systems Go 2024 talk on Arch Linux and mkosi (**Secondary**): <https://pkgbuild.com/~jelle/arch-mkosi-all-systems-go-2024/>
- [R16] Yocto Project test manual, "Reproducible Builds" (**Primary**): <https://docs.yoctoproject.org/_sources/test-manual/reproducible-builds.rst.txt>; OpenEmbedded-Core `meta/lib/oe/reproducible.py` (**Primary**): <https://git.openembedded.org/openembedded-core/tree/meta/lib/oe/reproducible.py>; OpenBMC mirror of the Yocto reproducible-builds documentation (**Secondary**): <https://grok.openbmc.org/xref/openbmc/openbmc/poky/documentation/test-manual/reproducible-builds.rst?r=517393d9>
- [R17] `rpm-ostree(1)` (**Primary**): <https://mankier.com/1/rpm-ostree>; Red Hat, "Automating RHEL for Edge image rollback with greenboot" (**Secondary**): <https://www.redhat.com/en/blog/automating-rhel-edge-image-rollback-greenboot>; `docs.bazzite.gg`, "Rolling back system updates" (**Secondary**): <https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing//rolling_back_system_updates/>
- [R18] Buildroot, "reproducibility: introduce config knob" (**Primary**): <https://lists.buildroot.org/pipermail/buildroot/2016-July/165779.html>; Buildroot patch that keeps an existing `SOURCE_DATE_EPOCH` (**Primary**): <https://lists.buildroot.org/pipermail/buildroot/2017-November/207894.html>
- [R19] bootc, "bootc compatible images" (**Primary**): <https://containers.github.io/bootc/bootc-images.html>; Red Hat, "Creating bootc images from scratch" (**Primary**): <https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/10/html/using_image_mode_for_rhel_to_build_deploy_and_manage_operating_systems/generating-a-custom-minimal-base-image>; Fedora, "From scratch Fedora/CentOS bootc base container images" (**Primary**): <https://docs.fedoraproject.org/es/bootc/building-from-scratch/>

**Triangulation status.** The author-time tier of `spec/claude/research-triangulate/` §"Author-time assertions" asks for three independent sources. Counted by domain root:

- At or above the tier: [R3], [R4], [R5], [R6], [R7], [R8], [R12], [R13], [R14], [R17].
- [R19]'s three sources are the bootc project and two distributions whose documentation derives from it. Counted the way [R16] is counted, that's one upstream root, so the label signal of §I.5 rests on the bootc project alone. The declaration is the signal a derived build relies on anyway, and the label serves only as a second signal.
- Two roots: [R1] (UAPI Group, systemd) and [R9] (Debian man page mirror of mkosi, systemd-devel), which feed only advisory sections; [R15] (the mkosi man page, two Arch Linux sources) and [R16] (Yocto Project, OpenEmbedded, with the third source a mirror of the first), whose §I entries are therefore marked **[unverified]**.
- One root: [R2], [R10], [R18]. [R2] and [R10] feed only advisory sections; [R18] backs the Buildroot entry in §I.2, which is therefore marked **[unverified]**.
- No source in this pass: the mkosi mirror-snapshot knob (§I.1) and the `SOURCE_DATE_EPOCH` mapping for NixOS, OSTree (§I.4), and bootc (§I.5), all marked **[unverified]**.
- Not established, so not relied on: whether a derived bootc image inherits the `containers.bootc` label from its base (§I.5).
- Deliberately left out: the claim that `bootc-image-builder`'s code moved into `image-builder` (a single blog source), which is why §I.5 says "or its successor"; and the `sysupdate.d` file suffix, which differs between sources (`*.conf` in older man pages, `*.transfer` in newer ones), so §I.1 names only the directory.

## Open Questions

- **Boot-chain strictness** (parking-lot). §E is advisory. Should Secure Boot, UKI, and dm-verity become mandatory for appliances whose threat model includes physical access? The deciding input is a per-repository threat model, which this spec doesn't define. Until that exists, §E only requires the omission to be recorded.
- **Signing non-OCI image artifacts** (parking-lot). `spec/project/artifact-signing/` covers OCI artifacts only. A raw disk image or firmware bundle and its SBOM have no signing and attestation contract yet. Whether that belongs in `artifact-signing` or a new spec is a decision for its owner.
- **Closing the [unverified] entries** (load-bearing for §C). §J keeps the unverified §I entries from producing a failure or blocking a gate, so the audit is usable today. But for every toolchain except the Debian builders, the reproducibility part of §C can't fail while its knob is unverified, which makes that pillar advisory in practice. Closing the gap needs one research pass per toolchain that brings its §C knob to three independent sources.
- **Portfolio-Scope promotion** (parking-lot). Should this spec stay `local` or be promoted to `portfolio`, so image-building repositories inherit it by reference per `spec/project/portfolio-inherited-spec-layer/`? Promotion is an explicit maintainer act and is deferred here. A promotion has to take `spec/project/dockerfile-best-practices/` along or rewrite its bootc exemption, which reads this spec's image declaration.
