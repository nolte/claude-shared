# Image Boot Verification

Status: draft
Portfolio-Scope: local

## Context

An image definition can pass every static check in `spec/project/linux-image-best-practices/` and still not boot: a missing driver in the initial RAM disk, a partition the boot loader can't find, a health unit that never starts, or a rollback path that's wired but never fires. The only proof that an image boots is to boot it. This spec governs that proof: starting a built image in a virtual machine with real firmware (UEFI or U-Boot), waiting for the image's own health report, asserting what it reports, and, for an image updated in the field, exercising the update-and-rollback path.

Boot verification is a **realisation of the end-to-end tier** of `spec/project/test-pyramid-foundation/`, not a seventh tier. The foundation's functional-tier taxonomy is closed, and booting a whole operating system and asserting its observable state is exactly what that tier describes. The foundation defines it as the tier that "drives the real user-facing surface of a running system and asserts on observable behaviour" and for an appliance that surface is the booted system. The requirement record `project/requirements/nolte-linux-plugin.md` holds this placement decision (its item R4). The spec fills the foundation's per-tier invariant shape in §A (purpose and scope boundary), §B (isolation and doubles), §C (speed and determinism), §D (execution placement), §E (traceability), §K (anti-patterns), and §L (reference profile). §F–§J add what's specific to images: the readiness and state contract, the protocol, host tooling and verdicts, the update-and-rollback scenario, and timeouts.

The content comes from a research pass on 2026-11-14 across the systemd documentation (the VM interface, Automatic Boot Assessment, `systemd-vmspawn`), the EDK II OVMF documentation, libvirt's Secure Boot notes, and the boot smoke tests that Debian and OpenEmbedded run against their own images.

**Boundaries:** `spec/project/linux-image-best-practices/` owns what an image must contain and declare, including the image declaration and the health report line this spec reads. This spec only boots the image and checks what it reports at runtime. Against the neighbouring tiers: the static-analysis tier of an image is the `linux-image-audit` skill against that spec, which never boots anything; a single component's integration with one real collaborator has no image-specific tier and stays with the component's own tests. `spec/project/e2e-test-automation/` owns E2E tests of an application's user interface. Its browser-specific rules (page objects, screenshots, the Selenium profile, the opt-in test protocol) don't apply here, while its determinism and traceability rules apply through the foundation, which owns them. When an appliance serves a web UI, its UI tests run against the booted VM under that spec, not this one. `spec/project/test-pyramid-foundation/` owns the tier model, the test-double vocabulary, arrangement fidelity, and the CI gating model this spec applies.

**Readers:** the authors of the `image-boot-verify` skill; maintainers of image-building repositories who wire a boot check into their pipeline; reviewers judging whether a boot verdict is trustworthy.

## Goals

- A built image is proven to boot to a healthy state the image itself reports, not merely to start a kernel
- A run that couldn't verify anything reports exactly that, and is never mistaken for a pass
- An image updated in the field is proven to roll back on its own when an update comes up unhealthy
- Every run leaves a protocol that names exactly which image, firmware, and host it ran on, so a verdict can be reproduced and audited
- Boot checks stay deterministic: condition-based waits with bounded timeouts, never fixed delays

## Non-Goals

- Static review of the image definition, owned by `spec/project/linux-image-best-practices/` and the `linux-image-audit` skill
- Tests of an application's user interface running on the appliance, owned by `spec/project/e2e-test-automation/`
- Booting on physical hardware, hardware-in-the-loop rigs, and board-specific bring-up. A verdict from a virtual machine, under UEFI or U-Boot, doesn't establish that the image boots on physical hardware, such as a Raspberry Pi that runs its own firmware chain before any boot loader of the image
- Images whose firmware is neither UEFI nor U-Boot, such as BIOS (§A)
- Performance benchmarking of boot time; a run records durations, but this spec sets no boot-time target
- Fleet-level update rollout and the update server side

## Requirements

### A. Purpose and scope boundary

- A boot verification **MUST** assert that the image reaches its healthy state as its own health definition reports it: the image's health report line (`spec/project/linux-image-best-practices/` §A) says `status=healthy`, and the reported system state is acceptable under §F
- A boot verification **MUST NOT** assert application business behaviour. A service's own functional behaviour belongs to that service's test tiers; this spec asserts only what the image's health definition reports
- A boot verification resolves the properties of the built image that a static audit can't decide (`spec/project/linux-image-best-practices/` §J) through the scenarios of §I: the rollback scenario for the update behaviour, and the identity scenario for a machine ID baked into the image
- Boot verification covers images whose firmware is UEFI or U-Boot, each booted under a hypervisor's virtual machine. The declaration's `image.firmware` (`schemas/image-declaration-v1.1.schema.yaml`) names the firmware type, and a declaration of schema version 1.0, which has no such field, counts as `uefi`. An image that declares `bios` or `other` is out of scope: every scenario is `not-run` with the reason that its firmware is out of scope, and `spec/project/linux-image-best-practices/` §J reports the results those scenarios would resolve as `spec-gap: boot verification out of scope for <firmware>` instead of blocking
- A run boots the guest architecture the declaration's `image.architectures` names; when it names several, the operator's input or the artifact selects one of them. For a declaration of schema version 1.0, the architecture comes from the artifact or an explicit input. When none of these yields it, every scenario is `not-run`
- A verdict is evidence for the image under the virtual machine's firmware and machine type only. It **MUST NOT** be presented as proof that the image boots on physical hardware, whose firmware chain the run doesn't exercise

### B. Isolation, test doubles, and arrangement fidelity

- The image under test, the boot loader, and the kernel **MUST** be the real build artifacts, booted unmodified. A run **MUST NOT** rebuild, patch, or re-sign the image to make it boot
- A run **MUST** boot from a disposable copy or a copy-on-write overlay of the image, so the artifact under test is never modified by its own boot
- A run **MUST** refuse an artifact that refers to another file, such as a qcow2 image with a backing file or an external data file, and record the affected scenarios `not-run`, because the reference would let the hypervisor read a host file or fetch a URL outside this isolation
- Each arrangement is classified in the vocabulary of `spec/project/test-pyramid-foundation/` §"Test-double taxonomy" and held to its §"Arrangement fidelity":
  - **Firmware**: real firmware of the declared type, not a double: UEFI firmware, or a U-Boot build for the hypervisor's machine type. When the declaration's `boot_chain.secure_boot` is `implemented`, the firmware **MUST** run with Secure Boot enabled and only the image's own public keys enrolled; enrolling a broader key set or disabling Secure Boot is a divergence the run **MUST NOT** make
  - **TPM**: a software TPM emulator **MAY** stand in for the hardware TPM; it's a fake. The protocol records that the TPM was emulated
  - **Update server**: a local source that serves the next image version is a fake of the update server. It **MUST** serve the real next-version artifact, signed as it would be in production
  - **Acceleration**: emulation instead of hardware virtualisation is a declared divergence in speed only; §H governs it
- A run **MUST** give the VM no route to an external network or to a host service other than the declared local-source endpoint. A scenario with an update source (rollback, positive) reaches exactly one forwarded endpoint, the local source that serves the next version; a scenario without one (smoke, identity) runs with no network device at all. Any other reachable endpoint is a collaborator the arrangement doesn't declare, so a verdict couldn't account for it
- Before each boot, the run **MUST** assert the network configuration it passes to the hypervisor: for a scenario with an update source, user-mode networking in restricted mode (`restrict=on` in the reference profile of §L) with exactly one forwarded endpoint, the declared one; for a scenario without one, no network device. A configuration that fails the assertion, such as one without the restriction or with a second forward, is rejected before boot, and the scenario is `not-run` (§H)

### C. Speed and determinism budget

- A single boot check is expected to take on the order of minutes. Every wait **MUST** be bounded by an explicit timeout from §J, and the run **MUST** record every timeout it used
- A run **MUST NOT** synchronise with fixed delays (`sleep`). It waits for a condition: the health report line, or the end of a bounded timeout [R3]
- A run **MUST NOT** retry a scenario silently. A retry is a new attempt, and the protocol records the attempt number. A scenario that fails and then passes on a retry **MUST** carry the `flaky` flag on its verdict, per `spec/project/test-pyramid-foundation/` §"Determinism and flakiness"

### D. Execution placement

- Boot verification **SHOULD** run in a dedicated stage or on a schedule (nightly, or before a release), not on every pull request, consistent with the slow-tier placement that `spec/project/test-pyramid-foundation/` §"CI gating model" sets. A repository **MAY** gate pull requests on it when its risk profile justifies the runtime
- Boot verification **MUST** be runnable locally by the same entry point the pipeline uses, so a red pipeline run can be reproduced on a developer machine

### E. Traceability

- Each boot scenario **MUST** name the requirement or TC-ID it verifies, as `spec/project/test-pyramid-foundation/` §"Traceability" requires. At minimum, the smoke scenario names the image's health definition, the rollback scenario the image's rollback requirement, and the identity scenario the image's identity requirement (`spec/project/linux-image-best-practices/` §D)
- The protocol (§G) **MUST** carry those identifiers, so a report maps back to requirements without external bookkeeping

### F. Readiness and state assertions

- A run **MUST** capture the serial console of the VM to a file from power-on to shutdown, in every scenario [R2]
- A run **MUST** treat the image's health report line (`spec/project/linux-image-best-practices/` §A) on the serial console as the readiness condition and the single source for the assertions below. Before matching, the run strips a trailing carriage return, other control characters, and terminal escape sequences from each captured line. A report is a normalised line that begins with `IMAGE-HEALTH-REPORT` followed by a space; a report broken up by interleaved console output doesn't count, so the image writes it as one write; a mention of that string anywhere else in a line, such as an echoed kernel command line, isn't a report. Per boot, the run waits for the first report until the readiness timeout of §J expires
- When the line reports `status=healthy`, the run **MUST** check two things. Every unit in `failed_units` is listed in the declaration's `health.tolerated_units`. And `system_state` is `starting` (the health definition still gates `boot-complete.target`), `running`, or `degraded`; the value `-` is accepted only when the declaration's `health.definition.kind` is `framework-hook`. `failed_units=-` means no unit failed. Anything else fails
- When the line reports `status=unhealthy`, or no report appears before the readiness timeout, the smoke scenario fails. A missing report is the image's defect, since `spec/project/linux-image-best-practices/` §A requires the line on a serial console
- A run **MUST** record the reported `image_id` and `image_version` and **MUST** check them against the declaration's `image.name` and the expected version the caller passed for the artifact (§H), so the protocol proves which image actually booted
- A run **MAY** use an out-of-band readiness channel offered by the hypervisor and the image (§L) for progress diagnostics. Such a channel **MUST NOT** replace the health report line as the basis of a verdict

### G. Protocol

- Every run **MUST** write a machine-readable protocol (`protocol.json`) and the captured serial log into one run directory. The default location is outside the tracked tree (git-ignored), like the E2E test protocol
- The protocol **MUST** contain: the version of the protocol format; the run timestamp; the overall verdict and the exit status that exposes it (§H); the host (operating system, kernel, architecture); each image artifact (the one under test and, for the rollback and positive scenarios, the next version) with its digest and expected version; the commit of the image definition; the image declaration it read; the firmware type, the firmware build, and whether Secure Boot was enabled; the guest architecture and where it came from (§A), the machine type, and whether the guest architecture differs from the host's; whether the TPM was emulated; the hypervisor and its version; the acceleration mode and, under emulation, the warning and the timeout factor; every timeout used; per scenario whether it's required, its verdict, `flaky` flag, attempt number, network isolation (no network, or the one forwarded endpoint, with the configuration asserted before boot), duration of each phase, and the health report lines observed; the image versions observed after each boot of the rollback scenario; the machine UUID and the `machine_id_app` value of each of the two boots of the identity scenario; for `not-run`, the missing tools or the failed precondition and an install hint; the requirement or TC-IDs covered; and the path of the serial log
- The protocol **MUST** be written for every verdict, including `not-run`. A field the run couldn't collect is written as `unavailable` with a reason, never omitted or guessed
- `schemas/image-boot-protocol-v1.1.schema.yaml` is normative for the protocol format, and a run **MUST** write its protocol in that version. A run **MUST** write `schema_version` and **MUST** validate its protocol against the schema that version names before it hands the protocol on; a consumer **MUST** validate a protocol the same way before it uses it and **MUST** ignore one that fails. A consumer **MUST** still accept a protocol that names version `1.0` and validates against `schemas/image-boot-protocol-v1.0.schema.yaml`. The schema expresses the `unavailable` convention (an uncollected field holds `status: unavailable` and a non-empty `reason`, never `null`) and admits only consistent pairs of overall verdict and exit status. It also admits each scenario at most once, rejects a `pass` or `fail` scenario whose network isolation is `unavailable`, rejects a `pass` scenario that carries no report line, and requires the smoke and identity scenarios to run without a network device. A `fail` scenario may carry no report line: that's the missing report of §F, for example a readiness timeout. Rules that span several fields stay with the consumer, which **MUST** ignore a protocol that breaks one: the overall verdict is the worst verdict of the required scenarios as §H defines it; a scenario with a forwarded endpoint names exactly the endpoint the run served the next version from (§B); an identity `pass` records two different `machine_id_app` values; a `pass` or `fail` scenario records the commit of the image definition and the artifact it booted, not `unavailable`; and an image whose firmware is out of scope, or the identity scenario under U-Boot, carries only `not-run` (§A, §I)

### H. Host tooling and verdicts

- A run takes as input the path of the image declaration, the artifact under test with its expected version and the commit of the image definition it was built from, and, for the rollback and positive scenarios, the next-version artifact with its expected version. The run records that commit in the protocol as given and never substitutes the working copy's current commit. A missing input is a failed precondition
- Before booting, a run **MUST** check every precondition: a firmware type in scope (§A) and the guest architecture (§A); the hypervisor for that architecture and the firmware of the declared type it selects: for `uefi`, UEFI firmware for the architecture and, when the declaration says `secure_boot: implemented`, firmware variables with the image's keys enrolled; for `u-boot`, a U-Boot build for the hypervisor's machine type and the architecture that the image's boot chain accepts unchanged, which for an image that implements Secure Boot trusts only the image's own keys; the TPM emulator, when the declaration says `measured_boot: implemented`; a valid image declaration; a readable image artifact; for the rollback scenario, the next-version artifact and a local source the guest can reach; for the identity scenario, a hypervisor that can assign a machine UUID the guest reads, which isn't established for `u-boot`, so a U-Boot image's identity scenario is `not-run` until a real run confirms one; and, for every scenario, the network isolation of §B, asserted from the configuration. When isolation can't be established, the affected scenario is `not-run`; a run **MUST NOT** boot it with open networking instead
- Each scenario **MUST** end in exactly one verdict, defined by exclusion:
  - `not-run`: a precondition failed, the run's own infrastructure failed before the firmware handed over to the image (the hypervisor couldn't start, the overlay couldn't be created, the protocol directory isn't writable), or §I names the case as `not-run` (a missing switch, a report without `machine_id_app`). In each case the run verified nothing that the scenario exists to check
  - `fail`: every precondition held, the image was started, and an assertion of §F or §I failed or the readiness timeout expired
  - `pass`: every precondition held and every assertion held
- A scenario **MUST NEVER** return `pass` when any precondition is missing. A `not-run` verdict **MUST NOT** be counted as a green check by any gate
- The run's overall verdict is the worst verdict of its required scenarios (the smoke scenario, and the rollback scenario for an image updated in the field), in the order `fail`, `not-run`, `pass`. A recommended scenario (the positive and the identity scenario) raises the overall verdict to `fail` when it fails, but its `not-run` is reported without raising the overall verdict. The run **MUST** expose it both in the protocol and as its process exit status: `0` for `pass` (with or without the `flaky` flag), `1` for `fail`, `2` for `not-run`
- A guest architecture that differs from the host's always runs under emulation, and the protocol records the boot as cross-architecture
- IF hardware virtualisation is unavailable, THEN the run **MAY** fall back to emulation. Such a run states an explicit warning in its output and protocol and scales every timeout by the emulation factor of §J. A scenario that holds under emulation **MAY** return `pass`; the protocol's acceleration field keeps the weaker evidence visible. Emulated boots on shared CI runners are known to exceed timeouts sized for accelerated boots [R3]

### I. Update and rollback scenario

- For an image whose declaration says `update_model: field-updated`, boot verification **MUST** include a rollback scenario, driven entirely through the switches the declaration names (`spec/project/linux-image-best-practices/` §F):
  1. Boot version N from a fresh copy, with `update.source_switch` set to the local source that serves version N+1 and `health.failure_switch` set to N+1's expected version. The run sets both values once, at launch; they persist across the reboots the guest triggers, and the run doesn't restart the hypervisor during the scenario. N reports `status=healthy`, since the failure switch names another version
  2. The image's update mechanism installs N+1 and reboots into it without further input (`spec/project/linux-image-best-practices/` §F); wait for the first report of N+1
  3. N+1 reports `status=unhealthy` because of the failure switch and reboots on its own; keep reading reports
  4. Assert that the first `status=healthy` report after at most `update.max_boot_attempts` unhealthy reports of N+1 comes from version N. Then power the VM off from the host; the scenario ends there. The power-off is best-effort: N may already have started to install N+1 again, which doesn't affect the verdict, since the copy is discarded
- A run **MUST NOT** make N+1 unhealthy by corrupting or altering the artifact, since a corrupted artifact tests the update framework's signature check, not the rollback path
- A run **SHOULD** also include the positive scenario, as a separate boot from a fresh copy: the same steps without the failure switch, asserting that N+1 reports `status=healthy` and is still the reported version after one further boot, which the run triggers as a reset of the VM through the hypervisor, without restarting the hypervisor process
- When the declaration lacks the `update` block or `health.failure_switch` despite `update_model: field-updated`, the rollback scenario is `not-run` with that reason; it's never skipped silently
- For an image whose firmware is `u-boot`, the rollback and positive scenarios, and every later scenario that sets a host switch, are `not-run` with the reason that no switch transport is established for U-Boot, until one is established that passes the switches without altering a signed boot component (tracked in #740). The identity scenario of such an image is `not-run` too, with the reason that no machine-UUID transport is established for U-Boot (§H)
- A run **SHOULD** include the identity scenario for every image: boot the artifact twice, each time from a fresh copy, with a distinct machine UUID assigned by the hypervisor and with no failure or source switch set, and compare the `machine_id_app` values of the two reports. Each boot is held to the smoke assertions of §F, so an unhealthy or missing report fails the scenario. Equal values fail it, because the image ships a fixed machine identity (`spec/project/linux-image-best-practices/` §D). When either report carries `machine_id_app=-`, the scenario is `not-run`

### J. Timeouts

- A run **MUST** use these timeouts unless the caller overrides one, in which case the protocol records the override. The defaults are engineering values for an accelerated boot, not calibrated measurements:

  | Timeout | Default | Bounds |
  |---|---|---|
  | Readiness | 300 s | From power-on to the first health report line of one boot |
  | Update installation | 600 s | From the first healthy report of N to the first report of N+1 |
  | Rollback | (`max_boot_attempts` + 1) × readiness | From N+1's first unhealthy report to N's healthy report, covering every boot of N+1 and the boot of N |
  | Total | Sum of the scenario's phases plus 120 s | One scenario, including shutdown |

- Under emulation (§H), every timeout **MUST** be multiplied by an emulation factor of at least 5, and the protocol records the factor used

### K. Canonical anti-patterns

- Declaring success when the kernel prints its banner or the login prompt appears, without the image's health report
- Waiting with a fixed `sleep` before reading the console
- Reporting `pass` when the hypervisor, the firmware, or another precondition was missing
- Booting with Secure Boot disabled, or with a broader key set enrolled, to verify an image that declares Secure Boot
- Booting the build artifact in place, so a first-boot write changes the artifact that's later published
- Testing rollback by corrupting the update payload
- Treating an out-of-band readiness notification as proof that the image is healthy

### L. Reference profile (optional)

This profile is a worked default. `spec/project/test-pyramid-foundation/` §"Per-tier invariant shape (the meta-contract)" demotes such a profile to a reference, so the profile sets no requirement.

- Hypervisor: QEMU (`qemu-system-<target>`) with KVM acceleration where `/dev/kvm` is available, and TCG emulation otherwise; the image attached with `-snapshot` or through a copy-on-write overlay. The target is the guest architecture (`x86_64`, `aarch64`, `riscv64`, `s390x`), `arm` for `armv7l`, and `ppc64` for `ppc64le`; a guest architecture other than the host's runs under TCG
- Firmware: EDK II OVMF. For Secure Boot, a firmware variables file with only the image's keys enrolled, prepared with `virt-fw-vars`; a distribution's pre-enrolled template carries a broader key set and doesn't satisfy §B. The variables file has to match the firmware build [R2], [R4]
- U-Boot: the QEMU `virt` machine type of the guest architecture, with a U-Boot build for that board passed as `-bios` **[unverified]**
- TPM: `swtpm` attached as an emulated TPM 2.0 device [R4]
- Console: `-serial file:<path>` captures the serial console [R2]
- Network isolation: a scenario without an update source runs with `-nic none`, which configures no network device [R6]. A scenario with one uses restricted user-mode networking with exactly one guest forward to the host-side local source, for example `-netdev user,id=n0,restrict=on,guestfwd=tcp:10.0.2.100:8080-tcp:127.0.0.1:<port>`, and the source switch names `http://10.0.2.100:8080/`. `restrict=on` isolates the guest from the host and the outside network, and `guestfwd` forwards one guest address to a host endpoint [R6] **[unverified]**: that `guestfwd` keeps working under `restrict=on`, and that an outbound connection to any other address fails, awaits the first real run on the pinned QEMU version (#728)
- Switches: SMBIOS Type 11 strings passed with `-smbios type=11,value=<key>=<value>`; a systemd credential uses the key `io.systemd.credential:<name>` [R1] **[unverified]**
- Machine UUID: `-uuid <uuid>`, a fresh value per boot of the identity scenario
- Under U-Boot on the `virt` machine type, SMBIOS very likely doesn't reach the guest, so neither SMBIOS Type 11 switches nor the `-uuid` value are available to it there **[unverified]**; §H and §I make the affected scenarios `not-run`
- Out-of-band readiness (diagnostics only): the `vmm.notify_socket` system credential, through which a systemd guest reports `READY=1` over `AF_VSOCK` [R1]
- Launchers: `mkosi vm` or `systemd-vmspawn` **MAY** replace a raw QEMU command line, provided the run still meets §B–§J [R5]

## Acceptance Criteria

These criteria roll up the requirements above; every requirement stays normative on its own.

- [ ] `spec/project/image-boot-verification/` exists with `en.md` (canonical) and `de.md` (translation) and is listed in `spec/README.md`, and `spec/project/test-pyramid-foundation/` names it as the image realisation of the E2E tier
- [ ] Every field of the foundation's per-tier invariant shape is filled: purpose and scope boundary (§A), isolation and doubles (§B), speed and determinism (§C), execution placement (§D), traceability (§E), anti-patterns (§K), and an optional reference profile (§L), with the boundary against neighbouring tiers stated
- [ ] §B forbids rebuilding, patching, re-signing, or booting the artifact in place, and classifies firmware, TPM, update server, and acceleration with their fidelity rules
- [ ] §C forbids fixed delays and silent retries and requires the `flaky` flag
- [ ] §F makes the line-anchored health report on the serial console the readiness condition and the single source of the state assertions, accepts `starting`, `running`, and tolerated `degraded`, and requires the reported identity to match the declaration and the expected version
- [ ] §G lists every protocol field, requires a protocol for every verdict, and writes uncollected fields as `unavailable` with a reason
- [ ] §G names `schemas/image-boot-protocol-v1.1.schema.yaml` as normative for the protocol format; every protocol a run writes validates against it, including a `fail` without a report line, a consumer ignores a protocol that doesn't validate against the schema its version names, and a valid version `1.0` protocol stays accepted
- [ ] §B forbids every network route except the declared local-source endpoint, runs a scenario without an update source with no network device, and has the run assert the network configuration before boot and reject one without the restriction
- [ ] In a scenario with an update source, a connection from the guest to any address other than the forwarded endpoint, an external address or a host service, fails, while the forwarded endpoint serves the next version
- [ ] §A limits boot verification to UEFI and U-Boot images under a virtual machine, counts a declaration of schema version 1.0 as `uefi`, puts `bios` and `other` out of scope with a `spec-gap` result in the audit, and states that a verdict from a virtual machine doesn't establish boot on physical hardware
- [ ] A run boots the hypervisor of the declared guest architecture and is `not-run` when neither the declaration, nor the artifact, nor an input yields the architecture; a U-Boot image's rollback and positive scenarios are `not-run` until a switch transport is established, and its identity scenario until a machine-UUID transport is
- [ ] §H names the run's inputs, defines `pass`, `fail`, and `not-run` by exclusion, lists every precondition, defines the overall verdict as the worst verdict of the required scenarios, with a recommended scenario's `not-run` not raising it, with exit statuses `0`, `1`, and `2`, and allows `pass` under emulation only with the warning and scaled timeouts
- [ ] §I drives the rollback scenario only through the declared switches set once at launch, relies on the image to install, reboot, and roll back on its own, bounds it by `max_boot_attempts`, ends it at N's healthy report, forbids corrupting the artifact, turns a missing switch into `not-run`, and adds the identity scenario
- [ ] Run on a host without the hypervisor, the skill exits with status `2` and writes a protocol whose verdict is `not-run`, whose uncollected fields read `unavailable`, and which validates against the protocol schema
- [ ] For a declaration with `max_boot_attempts: 3`, the rollback scenario ends after at most four boots counted from the first boot of N+1 (three of N+1, one of N), within the §J rollback timeout
- [ ] §J states default timeouts, a rollback timeout that covers the final boot of N, and the minimum emulation factor
- [ ] Tool names appear only in the reference profile (§L) and as cited examples, never as binding requirements

## References

- Sources retrieved 2026-11-14. Source classes per `spec/claude/research-triangulate/` §"Source classes and independence": **Primary** and **Secondary**.
- [R1] systemd, "The VM Interface" (**Primary**): <https://systemd.io/VM_INTERFACE/>; Debian source of `VM_INTERFACE.md` (**Primary**): <https://sources.debian.org/src/systemd/259-1/docs/VM_INTERFACE.md>; `systemd-vmspawn(1)` (**Primary**): <https://www.freedesktop.org/software/systemd/man/261/systemd-vmspawn.html>
- [R2] EDK II, `OvmfPkg/README` (**Primary**): <https://qemu.googlesource.com/edk2/+/refs/heads/master/OvmfPkg/README>; kraxel.org, "Firmware logging" (**Secondary**): <https://www.kraxel.org/blog/2025/10/firmware-logging/>; libvirt, "Secure Boot" (**Primary**): <https://libvirt.org/kbase/secureboot.html>
- [R3] Debian systemd test `boot-smoke` (**Primary**): <https://sources.debian.org/src/systemd/259-1/debian/tests/boot-smoke>; OpenEmbedded-Core patch on boot state polling (**Primary**): <https://patchwork.yoctoproject.org/project/oe-core/patch/20240104135112.490141-1-mikko.rapeli@linaro.org/>; `rpm-ostree-engine` issue #78 on replacing a bare `is-system-running --wait` with timeout logic (**Secondary**): <https://git.shivering-isles.com/os-forge/rpm-ostree-engine/-/issues/78>; Launchpad comment on slow nested-KVM boots (**Secondary**): <https://bugs.launchpad.net/ubuntu/+source/gnutls28/+bug/1928648/comments/13>
- [R4] `virt-fw-vars(1)` (**Primary**): <https://www.mankier.com/1/virt-fw-vars>; OpenStack Nova spec, "Allow Secure Boot for QEMU- and KVM-based guests" (**Secondary**): <https://specs.openstack.org/openstack/nova-specs/specs/ussuri/approved/allow-secure-boot-for-qemu-kvm-guests.html>; Ubuntu Discourse, "Enable TPM, Secure Boot in Ubuntu 25.10 QEMU/KVM Guests" (**Secondary**): <https://discourse.ubuntu.com/t/enable-tpm-secure-boot-in-ubuntu-25-10-qemu-kvm-guests/76045>; trust|me, "Run trust|me image in QEMU/KVM" (**Secondary**): <https://trustm3.github.io/deploy/qemu>
- [R5] `systemd-vmspawn(1)` (**Primary**): <https://www.freedesktop.org/software/systemd/man/261/systemd-vmspawn.html>; `mkosi(1)` (**Primary**): <https://manpages.debian.org/testing/mkosi/mkosi.1>
- [R6] QEMU, "Invocation" (**Primary**), the options `-nic none` and `-netdev user` with `restrict=` and `guestfwd=`, retrieved 2026-11-15: <https://www.qemu.org/docs/master/system/invocation.html>

**Triangulation status.** The author-time tier of `spec/claude/research-triangulate/` §"Author-time assertions" asks for three independent sources. [R2], [R3], and [R4] meet it. [R1] rests on one domain root (systemd) and [R5] on two; the `io.systemd.credential:` key of §L is marked **[unverified]** for that reason. [R6] rests on one root (QEMU), and the documentation alone doesn't establish how `guestfwd` behaves under `restrict=on`, so the network-isolation entry of §L is marked **[unverified]**; the U-Boot entry of §L has no source in this pass and is marked the same way. Everything that rests on them sits in the optional reference profile (§L) and is never the basis of a verdict: the binding contract of §F is the health report line that `spec/project/linux-image-best-practices/` §A defines, not a hypervisor or init-system mechanism. [R5] doesn't establish the launchers' current command names (`mkosi vm` versus the older `mkosi qemu`), so an implementation reads them from the pinned toolchain version.

## Open Questions

- **Interactive implementation** (load-bearing). The `image-boot-verify` skill shipped with this spec runs interactively. It doesn't yet provide the exit statuses of §H, the entry point shared with the pipeline of §D, or the acceptance criterion on exit status `2`. A non-interactive runner closes the gap, tracked in #728. Until then, this spec stays `draft` and boot verification is evidence for a person, not a pipeline gate.

- **Cross-architecture evidence** (parking-lot). §A and §H settle the architecture scope: the declaration names its architectures, the run boots the hypervisor for the one under test, and a boot on a foreign host architecture runs under emulation and is recorded as cross-architecture. Whether such emulated evidence suffices for a release gate stays a decision for the first consumer that builds for a foreign architecture; the protocol keeps it visible.
- **U-Boot switch transport** (load-bearing for U-Boot images updated in the field). §I makes a U-Boot image's rollback and positive scenarios `not-run` until a transport passes the switches without altering a signed boot component, and its identity scenario until the guest can read a machine UUID the hypervisor assigns. The candidates (the QEMU `fw_cfg` interface, a U-Boot environment on a separate unsigned medium, a kernel command line that isn't part of a signed artifact) need a research pass and a real run, tracked in #740. Until then, `linux-image-audit` can't resolve the rollback and identity results of such an image, which stays `INCOMPLETE`.
- **Calibrating the timeouts** (parking-lot). The §J defaults are engineering values. The first real runs against consumer images (a follow-up per the requirement record's item R10) should measure boot durations and adjust them.
