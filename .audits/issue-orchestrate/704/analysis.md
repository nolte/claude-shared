---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "704"
classification: "spec-change"
secondary-classes: [security]
route: "direct"
status: draft
created: "2026-11-10"
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #704 — capability-reach-audit spec: define what removing an approved probe means
- **URL**: https://github.com/nolte/claude-shared/issues/704
- **Labels**: security
- **Linked items**: #701/#703, #702/#705 (merged)
- **Prior art checked**: no PR references #704; the spec defines no removal rule (`grep -i 'delet|remov|renam|supersed'` over `spec/project/capability-reach-audit/en.md`: none); the only rule is prose in `references/runner-exit-codes.md:34` ("Never delete a superseded file"), not enforced.

## Classification

- **Primary class**: spec-change (operator-confirmed 2026-11-10)
- **Secondary class(es)**: security
- **Rationale**: the spec lacks a rule for a vanished probe; without it a probe can be retired and replaced by a weaker one unseen.
- **Asserted cause verified**: partly. Established: runner keeps no record of the probe set (no state besides `_not-constructible.yml`; `reach_audit.py` loads the files present at HEAD). Unestablished: the issue's three bypass shapes were reported by the #702 security reviewer from code reading and are not each measured; P2 must reproduce them as tests.
- **Requirements**: `project/requirements/reach-probe-removal.md`, U_gate 0.8 = τ_high, saturation (requirements-elicit, 2026-11-10).

## Scope

- **In scope**: R1–R11 of the requirement artifact: `removed` state, exchange under the same id, `_retired.yml` + `reach-retired-v1.0` schema with approval, contradiction/invalid entries, deleted superseded files, Provenance listing, skill operation `retire`, spec EN/DE, references.
- **Out of scope**: derivation/execution, the #701/#702 weakening rules, declaration re-verification.

## Route

- **Decision**: direct
- **Rationale**: one outcome, one PR (operator choice), no roadmap item.

## Work packages

### P1 — Spec rule (EN canonical + DE)

- **Problem statement**: add the removal rule to `spec/project/capability-reach-audit/` (Requirements + Acceptance criteria) per R1–R11; DE translation in sync.
- **Acceptance criteria**: MUST rules for R1/R2/R4–R8 and the retire operation exist in en.md with matching ACs; de.md mirrors them; `check_section_refs.py` and Vale pass.
- **Touched files**: `spec/project/capability-reach-audit/en.md`, `de.md`, `spec/README.md` date if the index requires it
- **Specialist**: nolte-shared:spec (skill, run by the orchestrator against the worktree)
- **Depends on**: none

### P2 — Schema, runner, tests

- **Problem statement**: hypothesis: one `git log --name-status --format` walk over `project/reach-probes/` on HEAD plus `git show` per distinct blob yields every id ever carried and its last commit; ids at HEAD come from the loaded probes; an exchange is an id whose HEAD file's followed history (file_log) never carried it while another path did. New `schemas/reach-retired-v1.0.schema.yaml` embedded in the runner with a drift test like `reach-not-constructible-v1.0`. The implementer may refute this.
- **Acceptance criteria**: the nine ACs of the requirement artifact, each as a pytest test against real git; full suite green, also on git 2.56; each new finding test fails on `develop`.
- **Touched files**: `schemas/reach-retired-v1.0.schema.yaml`, `plugins/nolte-engineering/skills/capability-reach-audit/scripts/reach_audit.py`, `tests/test_reach_audit.py`
- **Specialist**: nolte-engineering:fullstack-developer
- **Depends on**: P1

### P3 — Skill operation `retire` and references

- **Problem statement**: add the `retire` operation to the `capability-reach-audit` skill (per-id approval, writes `_retired.yml` only after approval) and document the `removed` state, contradiction/invalid entries, and the migration in `references/runner-exit-codes.md`.
- **Acceptance criteria**: SKILL.md operation within the token budget (`validate_skills.py` rc 0), reference text consistent with the runner's reason strings, markdownlint clean.
- **Touched files**: `plugins/nolte-engineering/skills/capability-reach-audit/SKILL.md`, `references/*.md`
- **Specialist**: nolte-claude-dev:claude-plugin-developer
- **Depends on**: P2

### P4 — Verify

- **Problem statement**: read-only check for bypasses of the removal rule and fail-open paths.
- **Acceptance criteria**: findings by severity on the worktree diff; full suite green.
- **Specialist**: nolte-engineering:code-security-reviewer
- **Depends on**: P3

## Dependency ordering

P1 → P2 → P3 → P4

## Risks

- Breaking for consumers that already deleted probes (one-time `retire` migration); release-note line.
- History scan cost not measured; P2 measures it.
- SKILL.md token budget for `capability-reach-audit` may be tight; P3 moves detail into references.

## Open questions

- none blocking.

## Dispatch log
2026-11-10 P1 run via nolte-shared:spec (orchestrator in session, worktree paths) — two MUST bullets (removal + retirement record) inserted before the timestamp rule in §"Derivation, approval, and durability", one AC after the weakening AC; EN/DE structurally aligned (34 requirement bullets, 15 ACs each, same positions); pre-commit (Vale, section refs) and markdownlint clean.
2026-11-10 P2 dispatched to nolte-engineering:fullstack-developer — hypothesis partly refuted: `--name-status` + per-blob `git show` can't see removed ids or merge-side removals; implemented one `git log -z --raw --diff-merges=separate --root --topo-order` walk over project/reach-probes plus two `cat-file` batches (CSafeLoader for historic ids); merges included (fail closed). New schema reach-retired-v1.0 (last_revision 40/64 hex, approval optional → unapproved record ineffective), state `removed`, retirement contradiction/invalid findings, Provenance listing with "new since the manifest's previous commit". Orchestrator-verified: 814 passed / 2 skipped; with the script reverted 33 of 35 test_704_* fail (2 are no-finding controls). Specialist: git 2.56 → 438 passed; cost on kamerplanter 0.18 s for judge_removals; kamerplanter would show 12 `removed` findings until `retire` runs (breaking, release note). Open for P4: CSafeLoader vs safe_load divergence; file_log lacks --root (fail-closed).
2026-11-10 P3 dispatched to nolte-claude-dev:claude-plugin-developer — `retire` operation in SKILL.md (per-id approval, `retire <id>` / `skip <id>`, no bulk), new references/retirement.md and examples/04-retire-removed-probe.md, runner-exit-codes.md §Removed probes and retirement (strings checked against reach_audit.py by grep -F); refined the line-34 instruction: retiring a deleted superseded file clears `removed` but not the replacement's `invalid supersede`, so restore is the full remedy. No example `_retired.yml` shipped (would need an approval block, which examples ship without). Orchestrator-verified: validate_skills no error (Warning body ~4880 tokens, near the 5,000 cap), markdownlint clean. Not executed: an agent run against example 04.
2026-11-10 P4 dispatched to nolte-engineering:code-security-reviewer (read-only; built-in security-review sees the primary checkout only) — no Critical/High. Medium: oversize/missing historic blobs fall back to the file-name stem (swap without `removed`; permanent false positive for a >1 MiB probe at HEAD); two YAML loaders (CSafeLoader vs safe_load); a symlinked probe directory escapes the rule. Low: `_records_at` returns {} on an unparseable manifest (check passes); SKILL.md vs retirement.md contradict on `observation_digest`. Holds: moves/renames/extension changes, forged dates, merges incl. `-s ours`, injection, fail-closed walk. Mediums + the `_records_at` Low returned to the P2 specialist, the doc Low to the P3 specialist.
2026-11-10 P4 follow-ups — runner (P2 specialist): missing blobs stop the run (exit 1), no size-based stem fallback, one YAML loader (`load_yaml`, guard test), symlinked `project`/`project/reach-probes` refused (exit 2), `_records_at` fail-closed on an unreadable manifest; 8 new tests fail on the P2 state. Docs (P3 specialist): observation_digest rule scoped to probes; the three new messages documented verbatim. Orchestrator-verified: 822 passed / 2 skipped; no direct `safe_load` left; markdownlint clean on all changed .md.
