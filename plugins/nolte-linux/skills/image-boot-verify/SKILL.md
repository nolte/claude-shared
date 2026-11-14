---
name: image-boot-verify
description: Boots a built Linux image in a virtual machine with real UEFI firmware and verifies it per spec/project/image-boot-verification/, the E2E-tier realisation for images. Checks every host precondition first and returns not-run, never pass, when the hypervisor, firmware, enrolled keys, or TPM emulator is missing; then reads the image's own IMAGE-HEALTH-REPORT line from the serial console, asserts its state and identity against image-declaration.yaml, and for an image updated in the field drives the rollback scenario through the declared switches. Writes protocol.json and the serial log for every verdict. Invoke when the user asks to "boot-test the image," "verify the image boots," "test the rollback," or equivalent German-language requests. Don't use for a static audit of the image definition (linux-image-audit) or to change it (linux-image-developer). Supports resume per spec/claude/resumable-work/.
tags: [quality-gate]
phase: quality
summary: "Boots a built Linux image in a UEFI VM, reads its health report, and runs the smoke, rollback, and identity scenarios with a protocol for every verdict."
summary_de: "Bootet ein gebautes Linux-Image in einer UEFI-VM, liest seinen Health-Report und fährt Smoke-, Rollback- und Identitäts-Szenario mit Protokoll für jedes Verdikt."
use_when:
  - "you want to prove that a built image boots to a healthy state"
  - "you want to prove that an image updated in the field rolls back on its own"
dont_use_when:
  - situation: "You want a static audit of the image definition"
    alternative: linux-image-audit
  - situation: "You want to change or scaffold the image definition"
    alternative: linux-image-developer
see_also:
  - linux-image-audit
  - linux-image-developer
resumable: true
---

# Image Boot Verify

Boot a built Linux image in a virtual machine and verify it the way `spec/project/image-boot-verification/` prescribes: the image's own health report is the only basis of a verdict, a missing precondition is `not-run` and never `pass`, and every run leaves a protocol.

Implements `spec/project/image-boot-verification/` (§A–§L) against the image contract of `spec/project/linux-image-best-practices/` (the image declaration, the `IMAGE-HEALTH-REPORT` line, the failure and source switches). Read both at the start of every run; when this skill and a spec disagree, the spec wins.

## German trigger phrases

This skill also triggers on equivalent German-language requests, including:

- "Image boot-testen" / "prüfen, ob das Image bootet"
- "Rollback testen" / "Update-und-Rollback-Szenario fahren"

## User-language policy

Detect the user's language from their message and respond in it. `protocol.json` keys and verdict values stay in English.

## Inputs

Ask for anything missing before booting; a missing input is a failed precondition, not a guess.

- **Declaration**: path of the image's `image-declaration.yaml`.
- **Artifact under test** and its **expected version**.
- **Next-version artifact** and its **expected version**: only for the rollback and positive scenarios.
- **Scenarios**: default smoke, plus rollback and positive for `update_model: field-updated`, plus identity. The user may drop a scenario; a dropped required scenario (smoke, or rollback when `field-updated`) is recorded as `not-run` with the reason "excluded by the operator" and still counts toward the overall verdict.
- **Requirement or TC-IDs** (optional): the consumer's identifiers per scenario. Default: smoke names the image's health definition (image spec §A), rollback its §F rollback requirement, positive §F, identity §D.
- **Run directory**: default `.image-boot-verify/<YYYY-MM-DD-HHMM>/`, which must be git-ignored. When it isn't, ask before writing.

## Preconditions

1. Locate both specs in the repository, or else in the installed `nolte-shared` plugin's `spec/` tree, plus `schemas/image-declaration-v1.0.schema.yaml`. When any is unreachable, stop and say which.
2. Validate the declaration against the schema; an invalid declaration makes every scenario `not-run`. Check the §F conditional rules of the image spec too, but a missing `update` block makes only the rollback and positive scenarios `not-run`, and a missing `health.failure_switch` only the rollback scenario, each with that reason.
3. Check host tooling per §H and record each result: the hypervisor binary for the artifact's architecture, UEFI firmware, a firmware variables file with only the image's keys when `boot_chain.secure_boot` is `implemented`, a TPM emulator when `boot_chain.measured_boot` is `implemented`, a readable artifact under test, for the rollback and positive scenarios a readable next-version artifact and a local source the guest can reach, and for the identity scenario a hypervisor that can assign the machine UUID. Probe hardware virtualisation (`/dev/kvm` in the reference profile) too, but its absence isn't a failed precondition: the run falls back to emulation per §H.
4. When any required precondition fails, the affected scenarios are `not-run`: write the protocol with the missing items, an install hint each, and `unavailable` for uncollected fields, and stop booting those scenarios.

## Operations

### 1. verify

1. **Plan the scenarios** from the declaration and the inputs, and show the plan (scenarios, timeouts from §J, acceleration mode) before the first boot. Under emulation, say so and scale every timeout by the factor of §J.
2. **Smoke scenario:** boot a disposable copy-on-write overlay of the artifact with the serial console captured to the run directory. Wait, bounded by the readiness timeout, for the first line that begins with `IMAGE-HEALTH-REPORT` followed by a space. Apply the §F assertions: status, `system_state`, `failed_units` against `health.tolerated_units`, `image_id` against `image.name`, `image_version` against the expected version.
3. **Rollback scenario** (`field-updated` only): serve the next-version artifact from the local source, boot N from a fresh copy with `update.source_switch` set to that source's URL and `health.failure_switch` set to N+1's expected version, both once at launch, and follow §I steps 1–4 by reading reports only. Give the VM network access to the local source only, and no network beyond that in any scenario (§B). Never alter the next-version artifact. Power the VM off after N's healthy report.
4. **Positive scenario** (`field-updated` only): the same steps from a fresh copy without the failure switch; assert that N+1 reports healthy, reset the VM through the hypervisor, and assert that N+1 is still the reported version.
5. **Identity scenario:** boot two fresh copies with distinct machine UUIDs and no switches, and hold each boot to the smoke assertions; an unhealthy or missing report fails the scenario. Compare `machine_id_app`: equal values fail it, and a report with `machine_id_app=-` makes it `not-run`.
6. **Verdicts:** per scenario `pass`, `fail`, or `not-run` by the exclusion rules of §H; a retried scenario that then passes carries `flaky`, which doesn't lower a `pass`. The overall verdict is the worst verdict of the required scenarios (smoke, plus rollback when `field-updated`) in the order `fail`, `not-run`, `pass`; a recommended scenario (positive, identity) raises it only by failing.
7. **Write `protocol.json`** with every field §G lists, `unavailable` plus a reason for anything not collected, next to the serial logs.
8. **Hand back** the overall verdict, the per-scenario verdicts with their evidence lines, and the path of the run directory.

## Gotchas

- **The kernel banner isn't health.** Only the image's own report line counts; a login prompt or a `READY=1` notification never does.
- **Don't fix the image to make it boot.** Rebuilding, patching, re-signing, enrolling broader keys, or disabling Secure Boot invalidates the run (§B, §K).
- **Not a pipeline gate yet.** This skill runs interactively and records the verdict in `protocol.json`. Two requirements of the boot spec need a non-interactive runner it doesn't ship yet: the exit statuses `0`/`1`/`2` of §H and the local entry point shared with the pipeline of §D. That runner is a follow-up, tracked together with the first real run against a consumer image in nolte/claude-shared#728. Until it exists, no pipeline gate can run this skill, and its verdict is evidence for a person, read from `protocol.json`.

## Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/image-boot-verify/<run-id>.yml` after the precondition check and after each finished scenario, carrying the run directory and the per-scenario verdicts. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. A scenario interrupted mid-boot restarts from a fresh copy; it never continues on a used overlay. The state-file envelope and the fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

## Hard rules

- **Never** return `pass` for a scenario with a missing precondition, and never count `not-run` as green.
- **Never** boot the artifact in place; always a disposable copy or overlay.
- **Never** synchronise with a fixed `sleep`; wait for a report line or a bounded timeout.
- **Never** change a switch or restart the hypervisor process during the rollback or positive scenario; a reset of the VM isn't a restart.
- **Never** write a protocol that omits a field; write `unavailable` with a reason.
- **Always** capture the serial console to a file for every boot.

## Why this is a skill, not an agent

- **Mid-flow interactivity:** missing inputs (expected versions, the next-version artifact) and host gaps (no KVM, no firmware) need the operator's decision before a boot, and the scenario plan is shown before it runs.
- **Host tooling in the main context:** the run starts and supervises long-lived VM processes and a local update source; that belongs where the operator can see and stop it.
- **Persistent artifact:** the deliverable is a run directory with `protocol.json` and serial logs.
- **Counter-dimension:** the log volume of several boots favours an agent's isolated context; the skill keeps only the report lines and the protocol in the conversation and leaves the raw logs on disk.
