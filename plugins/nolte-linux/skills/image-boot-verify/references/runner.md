# Non-interactive runner

Read before running the runner, and before wiring it into a pipeline. The runner is the entry point that the pipeline and a developer machine share (`spec/project/image-boot-verification/` §D). It exposes the overall verdict as its exit status (§H).

## Status

The runner ships, but it hasn't booted a real image yet. Its tests run against a fake hypervisor: a script that writes scripted console lines and boots nothing. These harness tests show the runner's control flow. They're no evidence that any image boots. Until the first real run of nolte/claude-shared#728, these parts stay **[unverified]**:

- the §L QEMU command line
- the `restrict=on` network isolation, including whether `guestfwd` still forwards under it
- the §J timeout defaults

## Usage

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/image-boot-verify/scripts/boot_verify.py" \
    --declaration images/app/image-declaration.yaml \
    --artifact build/app_1.4.0.raw --expected-version 1.4.0 \
    --commit <full commit id of the image definition> \
    [--next-artifact build/app_1.5.0.raw --next-expected-version 1.5.0] \
    [--scenarios smoke,rollback,positive,identity] [--out <run directory>]
```

The runner asks nothing. A missing input is a failed precondition: the affected scenarios are `not-run`, and the run still writes a protocol.

## Inputs

| Option | Meaning |
|---|---|
| `--declaration` | The image's `image-declaration.yaml`. The bundled `linux-image-audit/scripts/validate_declaration.py` validates it first. |
| `--artifact`, `--expected-version` | The artifact under test (version N) and the `image_version` it must report. |
| `--commit` | The full commit id of the image definition that built the artifact. The runner records it as given. |
| `--next-artifact`, `--next-expected-version` | Version N+1, for the rollback and positive scenarios. |
| `--update-source-dir` | The directory the local update source serves. Default: the directory of the next artifact. |
| `--arch` | The guest architecture. Needed only when the declaration names several, or none (schema 1.0). |
| `--scenarios` | A comma-separated subset of `smoke,rollback,positive,identity`. Default: all that apply. A dropped required scenario is recorded `not-run` ("excluded by the operator"). |
| `--trace-id SCENARIO=ID` | The requirement or TC-ID per scenario (§E). Repeatable. Default: the image spec section. |
| `--firmware-code`, `--firmware-vars` | The firmware build and its variables template. Required when the declaration says `secure_boot: implemented`: a template with only the image's keys enrolled. Otherwise the runner looks in the usual distribution paths. |
| `--memory` | Guest memory in MiB. Default 2048. |
| `--timeout-readiness`, `--timeout-update`, `--timeout-rollback`, `--timeout-margin` | Override a §J timeout in seconds. The protocol records the source `override`. |
| `--emulation-factor` | The timeout factor under emulation. The runner never uses less than 5 (§J). |
| `--out` | The run directory. Default `.image-boot-verify/<YYYY-MM-DD-HHMM>/`. The runner warns when it isn't git-ignored. |

## Host requirements

- Python 3. The runner itself uses only the standard library. The validator it calls needs `pyyaml` and `jsonschema`. Without them, every scenario is `not-run`, and the install hint names them.
- For a boot: `qemu-system-<target>` for the guest architecture, firmware of the declared type, `swtpm` when `measured_boot: implemented`, and `-uuid` support for the identity scenario. A missing tool makes the affected scenarios `not-run` with an install hint.
- `/dev/kvm` is optional. Without it, or for a foreign guest architecture, the runner boots under TCG emulation, prints a warning, and scales every timeout by the emulation factor.

## What the runner does

1. It validates the declaration and checks every §H precondition. Under `u-boot` firmware, rollback, positive, and identity are `not-run` (§I, #740).
2. It builds the QEMU command line per §L. The artifact is attached with `snapshot=on`, and the serial console goes to `<scenario>.serial.log`.
3. Before each boot, it asserts the network configuration (§B): `-nodefaults` plus `-nic none` for smoke and identity, or exactly one `-netdev user` with `restrict=on` and exactly one `guestfwd` to the local source for rollback and positive. It refuses any other configuration before boot and records the scenario as `not-run`.
4. It interprets only normalised serial lines that begin with `IMAGE-HEALTH-REPORT` and a space. Every other console line is untrusted guest output, stored and never acted on.
5. It writes `protocol.candidate.json`, validates it with `validate_declaration.py --kind boot-protocol`, and publishes it as `protocol.json` only when it's valid.

## Outputs

The run directory holds:

- `protocol.json`: written only when the protocol validates against `schemas/image-boot-protocol-v1.0.schema.yaml`. Uncollected fields hold `{"status": "unavailable", "reason": "…"}`.
- `protocol.invalid.json` (validator exit `1`) or `protocol.unvalidated.json` (validator exit `2`): kept for diagnosis, never evidence (§G).
- Per boot: `<boot>.serial.log` and `<boot>.hypervisor.log`. Per update scenario: `<scenario>.update-source.log` with the source's requests.

On standard output, the runner prints a JSON summary: the overall verdict, the exit status, the protocol path, whether it's valid, the per-scenario verdicts, and the failure notes.

## Exit status

| Status | Meaning |
|---|---|
| `0` | `pass`: every required scenario passed, no recommended one failed, and the protocol is valid. |
| `1` | `fail`: a required scenario failed, or a recommended one did. |
| `2` | `not-run`: a required scenario is `not-run`. A run whose protocol isn't valid never exits `0`; a `pass` becomes `2`. |

A gate **MUST** treat `2` as not green (§H).

## Known gap

§F makes a missing report before the readiness timeout a `fail`. The v1.0 schema rejects a `fail` scenario without a report line (§G). For such a run, the runner exits `1` but writes `protocol.invalid.json`, not `protocol.json`. Resolving the gap is part of the §F/§H follow-up of #728.
