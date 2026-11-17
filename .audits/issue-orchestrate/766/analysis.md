---
artifact-type: issue-orchestration-analysis
repo: nolte/claude-shared
issue: "766"
classification: infra
secondary-classes: [bug]
route: direct
status: approved
created: 2026-11-17
---

# Issue Orchestration — Pre-analysis (#766)

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #766 — ci: run the real-Vale tests in the test job instead of skipping them
- **Labels**: cicd, test
- **Linked items**: #751 (vale-style v0.2.1), #767 (test fix, merged 7fcbbf6d), #762/#765 (where it surfaced)
- **Prior art checked**: no comments; only #767 references it (`gh pr list --search "766 in:body"`)
- **Requirement gate**: no artefact under `project/requirements/`; **operator override** (2026-11-17): decompose against the issue's three acceptance criteria
- **Trust**: issue author is the repository owner (nolte)

## Operator decisions (2026-11-17)

- Scope widened from "real-Vale tests" to the class **"a test skips silently in CI"**: CI fails on any skip outside an explicit allowlist.
- Requirements-elicit gate overridden (see above).

## Classification

- **Primary class**: infra (CI test lane)
- **Secondary**: bug (a defect stayed hidden behind the skip)
- **Rationale**: the CI `test` job's environment makes tests skip silently; no red run exists, so `workflow-health-triage` doesn't apply — the specialist is the CI pipeline designer.
- **Asserted cause verified**: confirmed — `ci.yml:112–128` test job installs no Vale (lint job does, `ci.yml:83` `VALE_VERSION: "3.15.2"`, `:100–104`); `tests/test_check_prose.py:159` `skipif(shutil.which("vale") is None)` plus two `pytest.skip` on unsynced styles (`:166`, `:170`).
- **Class measurement** (`pytest -q -rs tests` with Vale removed from PATH, develop 7fcbbf6d): 22 skips = 21 `behavioural` evals (`RUN_EVALS=1`, intended) + 1 real-Vale test. CI reported 23 skips on the same suite; the extra one is `tests/test_validate_mission.py:83` (`history not available in this checkout`), because the test job's checkout (`ci.yml:115`) sets no `fetch-depth`, so `01575fa` is absent — established from the config line and the skip condition, not from a CI skip list (CI runs `pytest -q`, which doesn't name skips).
- Platform skips (FIFO, loopback port, SHA-256 git in `test_image_generate.py`, `test_reach_audit.py`) don't fire on the ubuntu runner per this measurement's Linux host; under the guard they would fail CI if they ever did, which is intended.

## Scope

- **In scope**: test job installs Vale at the shared pin and runs `vale sync`; full-history checkout for the test job; a strict-skip mode in `tests/conftest.py` that turns any skip of a test **not** marked `behavioural` into a failure when `CI_FAIL_ON_SKIP=1`; the test job sets it; positive control recorded in the PR.
- **Out of scope**: running behavioural evals in CI (API cost; stays opt-in).

## Route

- **Decision**: direct — one outcome, one PR strand.

## Work packages

### P1 — Strict-skip mode in the test harness

- **Acceptance criteria**: with `CI_FAIL_ON_SKIP=1`, a skipped test without the `behavioural` marker is reported as failed, naming its skip reason; `behavioural` tests still skip; without the variable nothing changes; unit tests for the hook via `pytester` or an equivalent subprocess run.
- **Touched files**: `tests/conftest.py`, a new test file for the hook
- **Specialist**: no matching specialised agent loaded (nolte-engineering not in this session) — generalist remediation
- **Depends on**: none

### P2 — CI test job

- **Acceptance criteria**: test job installs Vale from the same `VALE_VERSION` as lint (single source), runs `vale sync`, checks out full history, sets `CI_FAIL_ON_SKIP=1`; actions stay digest-pinned; `cicd-pipeline-reviewer` finds no new issue.
- **Touched files**: `.github/workflows/ci.yml`
- **Specialist**: skill `nolte-shared:cicd-pipeline-design` (writes workflow files); review by agent `nolte-shared:cicd-pipeline-reviewer`
- **Depends on**: P1

### P3 — Positive control

- **Acceptance criteria**: a temporary commit that breaks the real-Vale assertion makes the CI `test` job red on the PR, then is reverted; both run URLs recorded in the PR body (issue AC3).
- **Specialist**: orchestrator (verification step)
- **Depends on**: P2

## Dependency ordering

P1 → P2 → P3

## Risks

- Workflow change on a security-relevant path (`.github/workflows/`): least privilege, digest pins, no untrusted input — `cicd-pipeline-reviewer` before PR; the built-in `security-review` can't see the worktree.
- Longer test job (Vale download + sync, full clone) — small.
- A future platform skip on the runner turns CI red — intended; the fix is to make the capability available or mark the test explicitly.

## Open questions

none

## Findings

| Finding | Source | Outcome | Reproduction | Issue |
|---|---|---|---|---|
| `test_validate_mission.py:83` skips in CI on the shallow checkout | class measurement | fixed by P2 (full-history checkout) | `ci.yml:115` + skip condition | — |

## Dispatch log
