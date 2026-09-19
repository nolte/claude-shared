# Group pre-analysis: 2026-09-19-verification-discipline-specs

> Run-scoped artifact. Committed on the integration branch, removed with a fix-forward
> `git rm` before the bundle merges. It must never reach the default branch, and it must
> never be hidden behind a `.gitignore` entry.

## Scope of this analysis

**Research question:** Which failure forms measured in the consuming repository
(`nolte/kamerplanter`, waves of 2026-09-16 to 2026-09-19) have no named rule and no
detecting check in the hub's verification-discipline specs, and how do the five open
issues that report them fit into one bundle without conflicting edits?

**The group's single logical change, in one sentence:** The verification-discipline
specs (`test-falsifiability`, `defect-class-guards`, `issue-orchestration`,
`issue-batch-integration`) and their implementing skills gain one named rule with its
detecting check for each failure form the last kamerplanter waves measured.

**Out of scope:** #643 (code hardening in `nolte-media`, different capability and touch
surface; its own `issue-orchestrate` run); #393 (Renovate dashboard, bot artefact); the
consumer-side lane in kamerplanter that #637 says waits for the marker rule (that repo
adopts the rule after the hub release); any change to `parallel-working-copies` beyond a
cross-reference (#642 keeps that spec's stash rule for worktree transfer).

**Tier:** 3 — `test-falsifiability` and `defect-class-guards` carry
`Portfolio-Scope: portfolio` (`spec/project/test-falsifiability/en.md:4`,
`spec/project/defect-class-guards/en.md:4`), so the group changes a published contract
that consumer repositories inherit at a pinned ref.

## Members

| Issue | Class | Admitting predicate | Evidence |
|---|---|---|---|
| #636 | spec-change | shared touch surface | edits `spec/project/test-falsifiability/en.md` §"Detection: Static criteria" (`:53-58`) and `plugins/nolte-engineering/skills/test-pyramid-check/SKILL.md` op 5 (`:69-83`); the same spec section #640 and #642 edit |
| #637 | spec-change | thematic coupling | adds a rule to `spec/project/defect-class-guards/en.md` §"The rules" (`:34-41`, G1–G6 today), the spec #640 also extends |
| #640 | spec-change | shared touch surface | edits `defect-class-guards` §"The rules" and `test-falsifiability` T6 (`:48`); the issue names #636/#637 as "the same backlog" |
| #641 | spec-change | thematic coupling | edits `spec/project/issue-orchestration/en.md` §"Issue acquisition and comprehension" (`:96-130`) and `spec/project/issue-batch-integration/en.md` §A (`:43-53`) plus `skills/issue-orchestrate/SKILL.md` op 1 and `skills/issue-batch-orchestrate/SKILL.md` op 1; same capability (verification before the fix) |
| #642 | spec-change | shared touch surface | edits `test-falsifiability` §"Negative verification" (`:72-79`) and the taxonomy (`:43-51`); cross-references `parallel-working-copies/en.md:84-85` |

All five authored by `nolte` (repository owner, trusted-author set); no comments exist.
Each is bounded: one outcome, one PR strand, no roadmap item.

**Dependency ordering:** #636 → #642 → #640 → #637 → #641.
`test-falsifiability` is edited by #636 (static criteria), then #642 (negative-verification
mechanics, new T10), then #640 (T6 addendum), so T-numbering is fixed before #640 refers
to it. `defect-class-guards` is edited by #640 (G7) before #637 (G8), so G-numbering is
fixed in issue order of the more fundamental rule first. #641 is independent of the other
four and goes last so the two orchestration skills are edited after the spec texts they
will cite are final.

**Shared touch surface:** `spec/project/test-falsifiability/{en,de}.md` (#636, #642,
#640); `spec/project/defect-class-guards/{en,de}.md` (#640, #637); `spec/README.md`
(every member, `Last updated` column).

## Mode decision

**Mode:** A — single strand

**Reason:** No member is likely to need removal: all five are prose edits to hub specs and
skills authored by the operator, every "decide before implementing" checkbox is answered
at this write gate (see Open questions), no member depends on a party outside the group
(kamerplanter waits on this bundle, not the reverse), and none is `security`-classified.
Three members edit the same two files, which is the case where separate sub-branches
would only manufacture merge conflicts (`references/mode-gate.md`).

## Structural finding

**Cluster shape:** class cluster

**Root cause or defect class:** *A failure form measured in a consuming repository has
no named rule and no detecting check in the governing hub spec or skill.* Every member is
an instance: each cites a kamerplanter measurement (#1405, #1456, #1573, five cases in
#641, three observations in #642), each checked the existing taxonomy (T1–T9, G1–G6)
and found the form absent, and each proposes the rule plus the check that detects it.

**Process finding:** Measured consumer findings reach the hub only as individual `spec`
issues and then wait: #636 and #637 were open for two days while #640 was filed noting
"the two process findings from the previous wave have not reached the specs either. That
is the same backlog." Nothing in `spec/project/continuous-improvement/` §"Portfolio gap
closure" counts open consumer-measured `spec` issues as a recurrence signal, so the
backlog has no trigger of its own. To be filed as its own issue against
`continuous-improvement` after the operator approves this artifact (externally visible;
per `references/measurement-discipline.md` it waits for the gate).

**Preventive change:** a rule in `continuous-improvement` §"Portfolio gap closure" that
treats `n` open, consumer-measured `spec`-labelled issues (proposal: three, the spec's
existing recurrence threshold) as a trigger to schedule an `issue-batch-orchestrate`
run, so the intake cadence is counted rather than noticed.

**Recurrence fed to the portfolio loop:** class "measured form without a named rule",
recurrence 5 in this group (plus the two earlier waves #640 and #641 cite).

## Decisions proposed for the write gate (answers to each issue's "decide before implementing")

| Member | Question in the issue | Proposal |
|---|---|---|
| #636 | spec bullet, skill bullet, or both | **both**: static-criteria bullet naming the F841 form and the linter rule; op-5 bullet pointing at that criterion as covered by the static tier, not by the sweep |
| #640 | new G7 or G1 addendum | **G7** ("a guard left behind by a fix MUST NOT assert an unrepaired member of the class as intended; a deliberately partial fix names the unrepaired members and fails, skips explicitly, or carries the follow-up issue at the assertion"); G1 asks whether an artefact exists, G7 what it says |
| #640 | prose-satisfies-the-check: T6 or G3 | **T6** named form ("the accessor resolves to prose that describes the rule"), because it is about what the guard reads |
| #637 | rule numbering, grammar, age bound | **G8** after #640's G7; marker grammar `SELF-REVOKED: #<issue> <YYYY-MM-DD>`; valid only while the issue is open **and** a red/`xfail` guard exists; age bound 30 days, overridable per project with a recorded reason (mirrors the threshold pattern of `requirements-elicitation`) |
| #642 | T5 worked example or new category | **T10 — "the test reaches the rule by a door production doesn't use"**, with the three observations as the worked example; T5 stays run-time fallback |
| #642 | §Mechanics placement | new sub-bullets under §"Negative verification": file-copy restore, the explicit `git stash` warning with the reason, `git show --stat HEAD` before push; cross-reference to `parallel-working-copies` §"Uncommitted changes between worktrees" |
| #641 | where the obligation lives | `issue-orchestration` §"Issue acquisition and comprehension" (new MUST: the asserted cause is verified against the code before the first tracked change; divergence recorded with the measurement, measurement wins; reading cited lines counts, re-reading the issue and a green existing check don't; binds only where a cause is asserted) and `issue-batch-integration` §A per member; mirrored in both skills' operation 1 |

## Completeness matrix

Columns derived from what this repository ships: a `spec/` tree (EN canonical + DE
translation), skills and agents as the shipped product, `tests/` with `task test`, a
`docs/` MkDocs tree, `.github/` config, and two generated indexes (`spec/README.md`,
the docs catalog under `docs/*/{skills,agents}/`).

| Member | Spec (EN + DE) | Skills / agents | Tests | Docs | Config / workflows | Generated index |
|---|---|---|---|---|---|---|
| #636 | `test-falsifiability/{en,de}.md` §Static criteria: F841 pre-state bullet naming the rule; check: `pre-commit run --files` (vale, markdownlint, check-section-refs) + EN/DE bullet-count parity | `test-pyramid-check/SKILL.md` op 5: one bullet delegating the form to the static tier; check: `python3 scripts/validate_skills.py` (body token cap) | not applicable — no test asserts spec prose; frontmatter tests run via `validate_skills.py` | not applicable — no guide restates the taxonomy (`grep -rl test-falsifiability docs/{en,de}` outside the generated catalog: none) | not applicable — no workflow reads this spec | `spec/README.md` row `Last updated`; docs catalog regenerated by `gen_catalog.py`; check: `python3 scripts/check_links.py --offline` after `gen_catalog.py` |
| #642 | `test-falsifiability/{en,de}.md`: §Negative verification mechanics sub-bullets, T10 in the taxonomy, cross-reference; check: as above + `grep -n "T10\|T9" ` shows every count/list that enumerates the taxonomy updated | `test-pyramid-check` op 5 and any skill/agent that enumerates T1–T9; check: `grep -rn "T1–T9\|T1-T9\|T9" plugins skills agents spec` restatement sweep, each hit revisited | not applicable — same reason | not applicable — same reason | not applicable | as #636 |
| #640 | `defect-class-guards/{en,de}.md`: G7 + acceptance criterion; `test-falsifiability/{en,de}.md`: T6 named form; check: pre-commit + `grep -n "G1–G6\|G6" spec skills plugins agents` restatement sweep (`source-code-review` D11 names G3/G4/G6) | agents that grade guards (`python-code-reviewer`, `frontend-code-reviewer`, `unit-test-reviewer`) if they enumerate G-rules; check: the same grep, each hit revisited or recorded as "enumerates none" | not applicable | not applicable | not applicable | as #636 |
| #637 | `defect-class-guards/{en,de}.md`: G8 marker rule + acceptance criterion + open question on consumer lane; check: pre-commit, parity | `guard-coverage-scanner` / `guard-coverage-check` if they inventory guard rules; check: grep for `G6`/`G7` in `plugins/nolte-engineering`, revisited | not applicable | not applicable | not applicable — the counting lane is the consumer's | as #636 |
| #641 | `issue-orchestration/{en,de}.md` §Issue acquisition + acceptance criterion; `issue-batch-integration/{en,de}.md` §A + acceptance criterion; check: pre-commit, parity | `skills/issue-orchestrate/SKILL.md` op 1 (cause verification before decomposition) and `skills/issue-batch-orchestrate/SKILL.md` op 1; check: `validate_skills.py` (body under the 5,000-token cap: issue-orchestrate is the fuller body, measure) | `tests/test_check_section_refs.py` exercises §-references generally; check: `python3 -m pytest tests -q` | not applicable | not applicable | as #636 |

**Bundle-level checks (integration branch tip, recorded with output):** `python3
scripts/validate_skills.py`; `python3 -m pytest tests -q`; `pre-commit run --all-files`
minus the catalog-page Vale noise; `python3 scripts/docs/gen_catalog.py && python3
scripts/check_links.py --offline`; `python3 -m mkdocs build --strict`; EN/DE structural
parity (heading, bullet, checkbox counts) for every touched spec; the per-issue
falsification checks: #640's rule applied to kamerplanter PR #1573 must identify the
adjacency assertion; #641's rule applied to its five cases must fire on each; #642's
text must grade a `git stash` counter-proof as non-conformant.

## Risks

- **Numbering churn.** T10/G7/G8 are referenced by number elsewhere in the corpus; a
  missed restatement leaves two taxonomies. Mitigation: the grep sweeps in the matrix,
  run and recorded per member, not once at the end.
- **Body-token caps.** `issue-orchestrate/SKILL.md` and `issue-batch-orchestrate/SKILL.md`
  gain an operation-1 obligation; `validate_skills.py` caps bodies at 5,000 tokens.
  Mitigation: measure after #641; move detail into `references/` if needed.
- **Self-modification.** #641 changes the skill running this group; the new rule binds
  the next run, not this one. Recorded here so the reviewer isn't surprised.
- **Portfolio contract.** Two touched specs are portfolio-scope; consumers pin a hub ref,
  so nothing breaks at merge, but the release notes must name the new rules. Mitigation:
  the PR body lists T10, G7, G8 explicitly.
- **Vale.** The corpus's Microsoft style forbids spaced em-dashes and requires
  contractions; the specs already use unspaced em-dashes in the T/G lines. Mitigation:
  `pre-commit run --files` per member before commit.

## Open questions for the operator

All three answered 2026-09-19 ("Passt so"): proposals, Mode A with the ordering, and the process-finding issue after the gate.

1. Approve the seven proposals in "Decisions proposed for the write gate" (or amend any).
2. Approve Mode A and the ordering #636 → #642 → #640 → #637 → #641.
3. Approve filing the process finding as an issue against `continuous-improvement` once
   the bundle's gate is green.

## Member results

Filled during implementation. Each entry records the dispatched specialist and the
**actual output** of every declared check, never an assertion that it passed.

| Member | Specialist | Check | Actual output |
|---|---|---|---|

## Deviations

| Member | Kind | What changed |
|---|---|---|
