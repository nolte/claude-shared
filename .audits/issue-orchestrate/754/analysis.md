---
artifact-type: issue-orchestration-analysis
repo: nolte/claude-shared
issue: "754"
classification: feature-request
secondary-classes: [spec-change]
route: direct
status: approved
created: 2026-11-16
---

# Issue Orchestration — Pre-analysis (#754)

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #754 — run the v1.2 update-security boot scenarios in the image-boot-verify runner
- **Labels**: feat, nolte-linux
- **Linked items**: #752 (spec + schema v1.2, merged 1e24b36a), #728 (first real boot; stays open, independent)
- **Prior art checked**: no linked or open PR; no `project/features/` entry
- **Requirement gate**: `project/requirements/nolte-linux-plugin.md` `U_gate = 0.80 = τ_high` — met

## Classification

- **Primary class**: feature-request
- **Secondary**: spec-change (closing the runner-gap Open Question)
- **Asserted cause verified**: confirmed — `plugins/nolte-linux/skills/image-boot-verify/scripts/boot_verify.py:1227` writes `"schema_version": "1.1"`; v1.2 schema at `schemas/image-boot-protocol-v1.2.schema.yaml`; Open Question "Runner coverage of the update-security scenarios" at `spec/project/image-boot-verification/en.md:247`.

## Scope

- **In scope**: protocol v1.2 emission and pre-hand-off validation; downgrade, signature-rejection (`untrusted-key`, `unsigned`), commit-boundary, interrupted-update scenarios in `boot_verify.py`; deterministic unit tests with the fake hypervisor; `references/runner.md`; Open Question removed (EN+DE).
- **Out of scope**: a real boot (#728 — no QEMU/OVMF on this host); U-Boot `fw_cfg` chain confirmation (#728 scope item 2).

## Route

- **Decision**: direct — one outcome (runner reaches spec v1.2), one PR strand, no roadmap item. Large but cohesive; split into packages, one PR.

## Work packages

### P1 — Protocol v1.2 emission

- **Acceptance criteria**: field-updated image → protocol validates against v1.2 schema before publish; non-field-updated image → valid protocol per the version §G prescribes (read §G for v1.1 vs v1.2); unit tests for both.
- **Touched files**: `boot_verify.py`, `tests/test_boot_verify_runner.py`
- **Depends on**: none

### P2 — downgrade + signature-rejection (required for field-updated)

- **Acceptance criteria**: §I positive-control rule implemented: scenario always boots; `pass` only with a rollback or positive `pass` in the same run, else `not-run`; failed assertion → `fail`; `not-producible` only with a format reason, raising a non-blocking Warning; inputs per §H (previous-version artifact, untrusted-key and unsigned payloads) — missing input → `not-run` with cause; §J update-window timeout; deterministic unit tests per path.
- **Touched files**: `boot_verify.py`, tests
- **Depends on**: P1

### P3 — commit-boundary + interrupted-update (run when declared)

- **Acceptance criteria**: run only when declared; commit-boundary uses committed state per spec line ~189 (not `-snapshot` discard); interrupted-update recovery timeout `(max_boot_attempts + 1) × readiness`; unit tests incl. not-declared path.
- **Touched files**: `boot_verify.py`, tests
- **Depends on**: P1

### P4 — Docs and spec close-out

- **Acceptance criteria**: `references/runner.md` and SKILL.md gotchas describe v1.2 and the four scenarios; Open Question "Runner coverage of the update-security scenarios" removed from `en.md` and `de.md`; "Runner status" OQ (`en.md:243`) updated if it restates v1.1; `task lint` + `task test` green.
- **Specialist**: `nolte-shared:spec` (spec), `nolte-claude-dev:claude-plugin-developer` (skill docs)
- **Depends on**: P2, P3

**Specialist for P1–P3**: no matching specialised agent loaded in this session — `fullstack-developer` / `unit-test-generator` ship in nolte-engineering, which this session doesn't load; generalist remediation (`general-purpose` drafting in the worktree, reviewed here), followed by `python-code-reviewer`-equivalent review by a fresh general-purpose reviewer.

## Dependency ordering

P1 → P2 ; P1 → P3 ; (P2, P3) → P4

## Risks

- Network-isolation invariant (#734): every new scenario boot MUST pass the existing `-nodefaults -no-user-config` / `restrict=on` assertion — reuse the existing boot path, never a new QEMU command builder. Security-relevant path → run `security-review` scoped to the worktree diff before PR.
- Fake-hypervisor tests prove control flow only, not boot behaviour — state so in the PR (as #746 did).
- `boot_verify.py` is 1376 lines; scenario additions may push it further — keep scenario code in the existing scenario structure.

## Open questions

none blocking; §G's rule for non-field-updated protocol version is read from the spec during P1.

## Findings

| Finding | Source | Outcome | Reproduction | Issue |
|---|---|---|---|---|

## Dispatch log
