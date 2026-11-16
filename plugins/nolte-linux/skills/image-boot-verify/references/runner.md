# Non-interactive runner

Read before running the runner, and before wiring it into a pipeline. The runner is the entry point that the pipeline and a developer machine share (`spec/project/image-boot-verification/` §D). It exposes the overall verdict as its exit status (§H).

## Status

The runner ships, but it hasn't booted a real image yet. Its tests run against a fake hypervisor: a script that writes scripted console lines and boots nothing. These harness tests show the runner's control flow. They're no evidence that any image boots. Until the first real run of nolte/claude-shared#728, these parts stay **[unverified]**:

- the §L QEMU command line
- the `restrict=on` network isolation, including whether `guestfwd` still forwards under it
- the §J timeout defaults
- the commit-boundary scenario's kept state: that the image's committed state survives a new hypervisor process on the overlay file (§L)

The runner writes protocol version 1.2 for every run. §G requires it for an image updated in the field, and the version 1.2 schema also admits a run without the update-security scenarios. For an image updated in the field, it runs the four update-security scenarios of §I: downgrade and signature-rejection (required), and commit-boundary and interrupted-update (recommended).

## Usage

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/image-boot-verify/scripts/boot_verify.py" \
    --declaration images/app/image-declaration.yaml \
    --artifact build/app_1.4.0.raw --expected-version 1.4.0 \
    --commit <full commit id of the image definition> \
    [--next-artifact build/app_1.5.0.raw --next-expected-version 1.5.0] \
    [--previous-artifact build/app_1.3.2.raw --previous-expected-version 1.3.2] \
    [--untrusted-payload <file> --untrusted-payload-version 1.5.0 \
     --untrusted-payload-production "<how it was built>" --untrusted-key-id <fingerprint>] \
    [--unsigned-payload <file> --unsigned-payload-version 1.5.0 --unsigned-payload-production "<how>" \
     | --unsigned-not-producible "<why the payload format can't carry an unsigned payload>"] \
    [--scenarios smoke,rollback,positive,identity,downgrade,signature-rejection,commit-boundary,interrupted-update] \
    [--out <run directory>]
```

The runner asks nothing. A missing input is a failed precondition: the affected scenarios are `not-run`, and the run still writes a protocol.

## Inputs

| Option | Meaning |
|---|---|
| `--declaration` | The image's `image-declaration.yaml`. The bundled `linux-image-audit/scripts/validate_declaration.py` validates it first. |
| `--artifact`, `--expected-version` | The artifact under test (version N) and the `image_version` it must report. |
| `--commit` | The full commit id of the image definition that built the artifact. The runner records it as given. |
| `--next-artifact`, `--next-expected-version` | Version N+1, for the rollback, positive, and interrupted-update scenarios. The local update source serves exactly this file. |
| `--previous-artifact`, `--previous-expected-version` | A version strictly older than N, such as N−1, for the downgrade scenario. Without it, or with a dotted numeric version newer than N, only downgrade is `not-run`. A version equal to N's once zero-padded (`1.4` equals `1.4.0`), a non-numeric version identical to N's, or N's own artifact (the same digest, which also covers the same path), makes downgrade `not-run` with the reason `previous-version artifact isn't older than N`, without booting. |
| `--untrusted-payload`, `--untrusted-payload-version`, `--untrusted-payload-production`, `--untrusted-key-id` | The signature-rejection untrusted-key payload: a bootable image of a version newer than N, signed with a throwaway key the image doesn't trust; how it was produced; and the key's identifier or fingerprint. The runner refuses a key identifier or production note that looks like key material (a PEM marker, a line break, or a token of 40 or more base64 characters that isn't a hex fingerprint) and never echoes it. A missing part, or a payload that offers N's or the previous-version artifact's version, or a dotted numeric version older than N, makes only this variant `not-run`. When the versions aren't dotted numeric, the production note in the protocol records that newness over N rests on the operator. |
| `--unsigned-payload`, `--unsigned-payload-version`, `--unsigned-payload-production` | The unsigned variant's payload, the same build without a signature. |
| `--unsigned-not-producible` | Instead of an unsigned payload: why the payload format of the declared `update.mechanism` can't carry one. The variant is then `not-producible`, isn't booted, and the runner prints a warning. |
| `--arch` | The guest architecture. Needed only when the declaration names several, or none (schema 1.0). |
| `--scenarios` | A comma-separated subset of `smoke,rollback,positive,identity,downgrade,signature-rejection,commit-boundary,interrupted-update`. Default: all that apply. A dropped required scenario (smoke; rollback, downgrade, and signature-rejection for an image updated in the field) is recorded `not-run` ("excluded by the operator"). |
| `--trace-id SCENARIO=ID` | The requirement or TC-ID per scenario (§E). Repeatable. Default: the image spec section. |
| `--firmware-code`, `--firmware-vars` | The firmware build and its variables template. Required when the declaration says `secure_boot: implemented`: a template with only the image's keys enrolled. Otherwise the runner looks in the usual distribution paths. |
| `--memory` | Guest memory in MiB. Default 2048. |
| `--timeout-readiness`, `--timeout-update`, `--timeout-rollback`, `--timeout-update-window`, `--timeout-recovery`, `--timeout-margin` | Override a §J timeout in seconds. The protocol records the source `override`. |
| `--emulation-factor` | The timeout factor under emulation. The runner never uses less than 5 (§J). |
| `--out` | A new or empty run directory. The runner refuses a non-empty one with exit `2`, so an earlier protocol is never taken for this run's. Default `.image-boot-verify/<YYYY-MM-DD-HHMM>/`. The runner warns when it isn't git-ignored. |

## Host requirements

- Python 3. The runner itself uses only the standard library. The validator it calls needs `pyyaml` and `jsonschema`. Without them, every scenario is `not-run`, and the install hint names them.
- For a boot: `qemu-system-<target>` for the guest architecture, firmware of the declared type, `swtpm` when `measured_boot: implemented`, `-uuid` support for the identity scenario, and `qemu-img` for the commit-boundary scenario. A missing tool makes the affected scenarios `not-run` with an install hint.
- `/dev/kvm` is optional. Without it, or for a foreign guest architecture, the runner boots under TCG emulation, prints a warning, and scales every timeout by the emulation factor.

## What the runner does

1. It reads the declaration once, validates that copy, and checks every §H precondition. Under `u-boot` firmware, identity and every scenario that sets a host switch (rollback, positive, and the four update-security scenarios) are `not-run`. Under `uefi`, a declared `qemu-fw-cfg` switch makes `not-run` each scenario that sets it: a `qemu-fw-cfg` source switch blocks rollback, positive, downgrade, signature-rejection, and interrupted-update, and a `qemu-fw-cfg` failure switch blocks rollback and commit-boundary. The QEMU `fw_cfg` transport stays unconfirmed until a real run (§H, §I, #728).
2. It refuses a qcow2 artifact, next artifact, previous-version artifact, or test payload that refers to another file: a backing file (a nonzero backing-file offset in the header) or an external data file (incompatible-feature bit 2 of a version 3 header). Either would let the hypervisor read a host file or fetch a URL outside the isolation of §B, so the affected scenarios are `not-run` with that cause.
3. It builds the QEMU command line per §L. The artifact is attached with `snapshot=on`, and the serial console goes to `<boot>.serial.log`. The one exception: when commit-boundary is planned, the positive scenario boots a copy-on-write overlay that `qemu-img` creates in the run's temporary directory on top of the artifact, which QEMU opens read-only as the backing file. Commit-boundary then boots that overlay, with copies of the positive scenario's firmware variables and TPM state, in a new hypervisor process, and deletes it afterwards.
4. Before each boot, it asserts the network configuration (§B): `-nodefaults` and `-no-user-config`, plus `-nic none` for smoke, identity, and commit-boundary, or exactly one `-netdev user` with `restrict=on` and exactly one `guestfwd` to the local source for the scenarios with an update source. It refuses any other configuration before boot and records the scenario as `not-run`.
5. The local update source serves exactly one file at `/<file name>`: the next artifact for rollback, positive, and interrupted-update, the previous-version artifact for downgrade, and each variant's test payload for signature-rejection, whose two variants share one forwarded endpoint. It opens the file once without following a symlink, checks it against the digest the protocol records, and answers every other path with `404`, without a directory listing. The log records every request; `source_requests` counts only requests for the served file.
6. Before the positive scenario's VM reset, it discards the console output read so far. Only a report printed after the reset counts for the reset boot.
7. Downgrade and each signature-rejection variant read reports for the §J update window from N's first report, reset the VM through QMP, and read one more report; every report must be healthy and name N's version. Unless the source sent the whole served file within the window, the scenario or variant is `not-run` (`update source not contacted within the update window`): a `404`, a `HEAD`, or an aborted download offered the guest nothing to refuse. A report that failed an assertion makes it `fail` even then. Before a reset, the runner reads a half-written console line to its end instead of discarding it. When every assertion held but neither rollback nor positive passed in this run, the scenario is `not-run` (`no positive control: neither rollback nor positive passed`); a failed assertion is `fail` regardless.
8. Signature-rejection fails when either variant fails, passes when untrusted-key passes and unsigned passes or is `not-producible` (under the positive control), and is `not-run` otherwise.
9. Commit-boundary runs only after a positive `pass` (`no committed version: positive scenario didn't pass`), with the failure switch set to N+1's version: the first report and the one after a reset must be healthy N+1.
10. Interrupted-update resets the VM once the source has sent the whole next artifact and before any report of N+1, records that moment, and then needs a healthy report of N or N+1 within the §J recovery timeout; unhealthy reports before it are allowed.
11. It interprets only normalised serial lines that begin with `IMAGE-HEALTH-REPORT` and a space. Every other console line is untrusted guest output, stored and never acted on.
12. It writes `protocol.candidate.json`, validates it with `validate_declaration.py --kind boot-protocol`, and publishes it as `protocol.json` only when it's valid.

## Outputs

The run directory holds:

- `protocol.json`: written only when the protocol validates against `schemas/image-boot-protocol-v1.2.schema.yaml`. It records the observed versions and source requests of the update-security scenarios, each signature-rejection variant's verdict, and the interrupted-update reset. Uncollected fields hold `{"status": "unavailable", "reason": "…"}`. A `fail` without any health report, such as a readiness timeout (§F), carries `report_lines: []` and is a valid protocol.
- `protocol.invalid.json` (validator exit `1`) or `protocol.unvalidated.json` (validator exit `2`): kept for diagnosis, never evidence (§G).
- Per boot: `<boot>.serial.log` and `<boot>.hypervisor.log`. Per boot with an update source: `<boot>.update-source.log` with the source's requests.

`firmware.secure_boot` records whether the runner enabled Secure Boot, as the declaration's `boot_chain.secure_boot` requires. It's the operator's declaration, not an observation from inside the guest.

On standard output, the runner prints a JSON summary: the overall verdict, the exit status, the protocol path, whether it's valid, the per-scenario verdicts, the failure notes, and warnings such as a `not-producible` unsigned variant. A warning doesn't change the exit status.

## Exit status

| Status | Meaning |
|---|---|
| `0` | `pass`: every required scenario passed, no recommended one failed, and the protocol is valid. |
| `1` | `fail`: a required scenario failed, or a recommended one did. |
| `2` | `not-run`: a required scenario is `not-run`. A run whose protocol isn't valid never exits `0`; a `pass` becomes `2`. |

A gate **MUST** treat `2` as not green (§H).

On `SIGTERM` or `SIGHUP`, the runner stops the running boot through its process group, records the interrupted scenario and every later one as `not-run`, and still writes the protocol. A signal during a required scenario never leaves exit `0`: the run exits `2`, or `1` when a scenario failed.
