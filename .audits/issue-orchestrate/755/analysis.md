---
artifact-type: issue-orchestration-analysis
repo: nolte/claude-shared
issue: "755, 756"
classification: spec-change
secondary-classes: [bug]
route: direct
status: approved
created: 2026-11-16
---

# Issue Orchestration — Pre-analysis (group #755 + #756)

Group admitted on the **dependency chain** predicate (#756 states "Decide [#755] first or
together") and the **shared touch surface** predicate (both edit the §C `SOURCE_DATE_EPOCH`
rule in `spec/project/linux-image-best-practices/` and the NixOS/Debian audit fixtures).
One integration branch, one PR: `fix/sde-literal-rule-755-756`.

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issues**: #755 — decide how SOURCE_DATE_EPOCH relates to the snapshot and to committed literals; #756 — align the NixOS SOURCE_DATE_EPOCH support cell with the §J literal rule
- **Labels**: spec, nolte-linux
- **Linked items**: #753 (fixtures, merged eec5b7c6), #752
- **Prior art checked**: no open PR references #755/#756 (`gh issue view`, no linked PRs); no `project/features/` entry
- **Requirement gate**: `project/requirements/nolte-linux-plugin.md` `U_gate = 0.80 = τ_high` (line 22) — met

## Maintainer decision (recorded 2026-11-16, operator)

1. A `SOURCE_DATE_EPOCH` set to the committed `snapshot.debian.org` timestamp (§I.3) **is
   source-derived**: the value lives in a committed lock file and moves with every lock
   update, so it doesn't go stale the way a free literal does.
2. A committed **constant** literal (e.g. 315532800, `SourceDateEpoch=0`) is a
   **non-blocking Warning**, not a `fail`. **Epoch zero stays `fail`** (the `rpm-ostree
   status` failure mode, `armada-os` #457).
3. A wall-clock expression stays `fail` (unchanged).

## Classification

- **Primary class**: spec-change
- **Secondary class(es)**: bug (#756: table vs §J inconsistency)
- **Rationale**: the deliverable is a maintainer decision written into the spec, with fixtures and scanner wording following it.
- **Asserted cause verified**:
  - #755 — **confirmed**: `en.md:62` (core §C, from source), `en.md:150` (§I.3 "set to the same moment"), `en.md:190` (§J committed literal = `fail`), `en.md:292` (Open Question) disagree as described.
  - #756 — **partly refuted**: `en.md:157` says the nixpkgs setup hook *raises* the fallback to the newest source mtime, so an image relying on stdenv commits no literal and the §J committed-literal `fail` does not reach it. The inconsistency is real only for an explicitly committed `SOURCE_DATE_EPOCH = 315532800`. Neither `nixos-pass` nor `nixos-fail` `expected.yaml` asserts the `§C SOURCE_DATE_EPOCH from source` row at all (measured: no `c-source-date-epoch` id in either file), so no fixture currently encodes the claimed `fail`.

## Scope

- **In scope**: the decision in §C, §I.3, §I.4, the §I support table (NixOS cell), the §J row, the Open Question removed (EN canonical + DE); scanner `linux-image-scanner.md:98` restatement; fixtures `debian-pass`, `field-updated-without-update`, `nixos-pass`, `nixos-fail`.
- **Out of scope**: `linux-image-developer.md:59` ("never as a committed literal") stays — still the right authoring advice under a Warning; Yocto profile beyond the shared §J sentence; any runner change (#754).

## Route

- **Decision**: direct
- **Rationale**: one outcome (one consistent SDE rule), one PR strand, no roadmap item.

## Work packages

### P1 — Write the decision into the spec

- **Problem statement**: §C/§I.3/§J/OQ give three readings; the NixOS cell says experimental while §J could give `fail`.
- **Acceptance criteria**: (a) §J row grades: source-computed or snapshot-aligned → `pass`; wall-clock → `fail`; constant literal ≠ 0 → Warning (non-blocking); epoch 0 → `fail`. (b) §I.3 states the snapshot-aligned value is source-derived under §C. (c) §I.4 and the NixOS table cell: stdenv reliance without a committed literal → `not-decidable`, cause `unverified` (Warning), since the derivation is [unverified] and its fallback is at worst a constant; the cell stays "experimental" and now agrees with §J. (d) Open Question "Constant `SOURCE_DATE_EPOCH` literals" removed, decision recorded. (e) EN and DE in sync; `task lint` (Vale, markdownlint, link check) green.
- **Touched files**: `spec/project/linux-image-best-practices/en.md`, `de.md`
- **Specialist**: `nolte-shared:spec` (skill, run in this session)
- **Depends on**: none

### P2 — Scanner rule wording

- **Problem statement**: `plugins/nolte-linux/agents/linux-image-scanner.md:98` says a committed literal `fail`s "until the Open Question … is decided".
- **Acceptance criteria**: line restates the P1 grading (incl. snapshot-aligned pass, constant → Warning, epoch 0 → fail, NixOS stdenv → `not-decidable`/`unverified`); `python3 scripts/validate_skills.py` within budgets.
- **Touched files**: `plugins/nolte-linux/agents/linux-image-scanner.md` (audit SKILL.md only if it restates — measured: it doesn't)
- **Specialist**: `nolte-claude-dev:claude-plugin-developer`
- **Depends on**: P1

### P3 — Fixtures follow the rule (defect-class guard)

- **Problem statement**: fixtures don't pin the decided grading; `debian-pass` justifies its pass by calling §I.3 "profile wording".
- **Acceptance criteria**: `debian-pass` `c-source-date-epoch` spec citation updated to the decision; `nixos-pass` gains `c-source-date-epoch: not-decidable, cause unverified`; `nixos-fail` gains `c-source-date-epoch: fail` (`builtins.currentTime` / `--impure` wall-clock signals); `field-updated-without-update` checked (its SDE is last-commit → no change unless it asserts the row); `pytest tests/e2e/linux_image_audit` green.
- **Touched files**: `tests/e2e/linux_image_audit/fixture/{debian-pass,nixos-pass,nixos-fail,field-updated-without-update}/expected.yaml`
- **Specialist**: no matching specialised agent — generalist remediation (fixture data; `unit-test-generator` lives in nolte-engineering, not loaded in this session)
- **Depends on**: P1

## Completeness matrix

| AC | Package |
|---|---|
| #755 AC1 Open Question resolved (EN+DE) | P1 |
| #755 AC2 §I.3 and §J agree on snapshot-aligned SDE | P1 |
| #755 AC3 debian-pass / field-updated-without-update fixtures follow the rule, pytest green | P3 |
| #755 AC4 scanner/audit wording matches | P2 |
| #756 AC1 NixOS cell and §J/§I.4 give one result (EN+DE) | P1 |
| #756 AC2 nixos-pass / nixos-fail expect that result, fixture test green | P3 |

## Dependency ordering

P1 → P2 ; P1 → P3 (P2 and P3 independent of each other)

## Risks

- EN/DE drift — mitigated by `spec` skill translation step and a section-by-section diff check.
- Fixture eval (`test_linux_image_audit.py`, live scanner) may need a matcher for the new rows — run the deterministic fixture test; the live eval is opt-in.
- Not security-sensitive.

## Open questions

none (decision recorded above)

## Findings

| Finding | Source | Outcome | Reproduction | Issue |
|---|---|---|---|---|

## Dispatch log
