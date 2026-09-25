# Runner exit codes and not-probed routing

Loaded by `capability-reach-audit` `run` step 2. The runner is `scripts/reach_audit.py` (invoked only as `python3 "${CLAUDE_PLUGIN_ROOT}/skills/capability-reach-audit/scripts/reach_audit.py" --repo <path>`); its exit codes and reason strings are the contract this file maps to an operator-facing next step. Nothing here re-derives a verdict: the report's classes and ratios are quoted, never recomputed.

## Exit codes

| Exit | Runner meaning | What the skill does next |
|---|---|---|
| `0` | report written, no findings | run `report`; the headline may still say `Not probed: <n> of <total>`, which is a coverage fact to surface, not a pass |
| `1` | runtime error (unreadable probe set, report not writable, git failure) | relay stderr verbatim; don't retry blind; the fix is in the target's state, not in the invocation |
| `2` | usage error or non-local target | relay the message verbatim; a remote address, a missing directory, a missing `.git`, a subdirectory, a bare repository, or a repository with no commit is refused by design; never route around it |
| `3` | no probe file: `project/reach-probes/` is absent, empty, or holds only the manifest; nothing was executed | **not** a clean result. Without a manifest the report says "no probe set"; with manifest entries it is a full report in which every entry is not probed. Either way route to `derive` (with a manifest, the actionable entries are the work to do first) |
| `4` | report written with findings (weakened or invalid probes, approval mismatches, contradictions, manifest defects); takes precedence over 3 | run `report` leading with the Findings section, then the headline; see §Findings |
| `5` | PyYAML or jsonschema missing | relay the runner's `pip install` hint verbatim and stop; never parse or validate probes yourself |

A negative or zero `--environment-timeout` also exits `2` before anything runs.

## Findings (exit 4)

- **weakened** `<id>`: the probe file changed after the commit that recorded its `derived_from`, or has uncommitted changes. The probe was **withheld** (`not probed`, reason `weakened: …`), never executed as approved. Lead with these. The operator either reverts the change (restoring the approved text) or re-derives the entry (`derive` with the entry filter), which records a new `derived_from` and a new baseline. Editing the file again is never the fix.
- **invalid probe** `<file>`: the file fails the probe schema. Quote the runner's error list. The fix is a re-derive of that entry; a hand edit to satisfy the schema would itself be a weakening.
- **invalid probe** `<file>` with the error `symlink: refused and not read; a probe file must be a regular file`: a symlink under `project/reach-probes/` is listed and never followed, so a probe set can't pull in text from outside the directory. Remove the symlink, re-derive the entry so a real file lands there, and commit it; never copy the link target into place by hand.
- **approval mismatch** `<id>`: the change-detection state whose reason is `approval does not cover the current observation step`; the committed `observe`, `environment`, or `teardown` no longer match `approval.observation_digest`. The probe was withheld. Re-derive and re-approve the entry; never hand-edit the digest to make it match. Read §Re-baseline rule when the operator asks why a re-approval didn't clear an older `weakened` finding at the same time.
- **contradiction** `<id>`: the id is both a probe file and a manifest entry; the probe is **not executed** and the row is not probed. The manifest is stale from a round that turned the entry into a probe: re-run `derive` with the entry filter set to that entry's declaration path, which rewrites the manifest without it; never delete the probe file to resolve it.
- **invalid manifest** (`_not-constructible.yml`): the file is unparseable or fails the schema above `entries/<i>`; none of its entries is counted and the headline says so. The fix is a re-run of `derive`, which rewrites the manifest from the scanner's payload; never repair it by hand.
- **invalid manifest entry** `<id>`: one entry fails the schema (a bad reason code, a missing `derived_from`, an unquoted `recorded_at`); it still counts as not probed. Re-run `derive` for that entry.
- **duplicate manifest id** `<id>`: listed more than once, counted once. Re-run `derive`; the scanner's ids are unique per payload, so a duplicate means two rounds were merged by hand.

## Not-probed reasons and their routing

The runner writes every not-probed reason into the report's Probes table. These are the ones that call for a next step from the skill:

| Reason (as written by the runner) | Meaning | Next step |
|---|---|---|
| `declaration changed since derivation: …` | the declaration's content at HEAD is no longer the `blob:` anchor (`the content of <rel> at HEAD is no longer <df>`), the file is gone (`<rel> no longer exists at HEAD`) or is no regular file (`<rel> is not a regular file at HEAD`), it has uncommitted edits, its latest commit postdates a commit anchor, or a moved inherited `ref` (stale, R2). Under a section anchor the reason names each locator: `in <rel>, heading 3.1 changed`, `in <rel>, row AK-OS-07 not found`, `in <rel>, heading 3.1 is ambiguous (2 matches)`, joined by semicolons | offer `reconfirm` (per probe, after the diff; `references/reconfirm-and-migrate.md`) and, for the rest, `derive` with the entry filter set to exactly these probes' declaration paths (R5). A locator that is `not found` or `ambiguous` can't be re-confirmed, since the runner never follows a renumbered section: `derive` |
| `probe file is not committed; …` | the approved set isn't under version control yet (R11) | the operator commits `project/reach-probes/`, then `run` again |
| `not approved` | a probe file without an `approval` block, for example a copied example | the file was never approved through the gate; remove it or re-derive and approve the entry |
| `approval does not cover the current observation step` | the probe's `observe`, `environment`, or `teardown` no longer match `approval.observation_digest`: a later commit swapped the argv or a target and left the old approval in place, or the block was written without the digest | the probe was **withheld**, never executed. Never recompute or paste the digest by hand; re-derive and re-approve the entry, and tell the operator to read the file's history, since the approved step and the committed step differ |
| `tier T2 not requested` | T2 probes withheld by default (R8) | say so; add `--include-t2` only on the operator's explicit request |
| `not constructible: <code>` | a manifest entry: no probe exists at any tier, counted in the headline | `missing_environment_target` and `missing_observation_helper` are work in the target repository (the `detail` names it), after which `derive` turns the entry into a probe; the other three codes stay counted until the declaration or the environment changes |
| `environment target <name> failed (…)` | the Taskfile target didn't come up (R10) | relay the target's output; this is infrastructure, never "not reached" |
| `observation step exited <n>: …` / `observation step timed out …` | the observe argv failed or hung | relay; the probe's argv or the host's tooling (`gh` auth, `psql`) needs attention in the target |
| `observation step printed nothing` | the argv exited 0 without output; for a count and a set alike, silence is no observation and is never read as zero or as an empty set | the argv must print the observation (one integer, or one member per line, or a genuine `0` when nothing matches); re-derive the entry with an argv that does |
| `observation has <n> digits; a count has at most 18` | the printed count exceeds eighteen digits, which is a runaway command, not a measurement | relay; the argv is counting the wrong thing (a byte count, a concatenation); re-derive the entry |
| `anchor … lies outside the repository; change is not monitored` | external anchor (R6) | inform the operator; re-derive only on their request |
| `derived_from … is not a commit of the target repository` / `… not in the history of HEAD` | a commit anchor doesn't resolve in this clone (shallow clone, rewritten history, a squash merge that dropped the derivation commit) | fetch full history or re-derive, which records a content anchor; never edit `derived_from` by hand |
| `derived_from <df> is a content anchor, but an inherited spec is anchored by its pinned inherits[].ref` / `derived_from <df> is a content anchor, but <where>; a content anchor needs a declaration file inside the repository` / `derived_from <df> is not a content anchor of the form blob:<40 hex digits>` | a `blob:` anchor on an inherited or external declaration, or a malformed one (unresolved) | re-derive the entry; the scanner records the right anchor form per §Derivation anchors |
| `derived_from <df> is a section anchor, but declaration.sections is absent` / `declaration.sections needs derived_from of the form sections:<64 hex digits>, not <df>` / `derived_from '<df>' is not a section anchor of the form sections:<64 hex digits>` / `declaration.sections lists <kind> <loc> more than once` / `derived_from <df> does not match the digests in declaration.sections` / `declaration.sections is not a list of heading or row locators with a digest` / `derived_from <df> is a section anchor, but an inherited spec is anchored by its pinned inherits[].ref` / `… is a section anchor, but <where>; a section anchor needs a declaration file inside the repository` | the section anchor is inconsistent: hand-edited, a locator listed twice, a digest that doesn't produce the recorded `derived_from`, or sections on a declaration that can't carry them (unresolved) | re-derive the entry, or migrate it again with the helper in `references/reconfirm-and-migrate.md`; never adjust a digest or the anchor by hand |

Every other reason is quoted as written and needs no routing.

An executed probe whose `approval.mode` is `reconfirmed` carries the note `approval is a re-confirmation, not a re-derivation`, and Provenance lists them as `- Probes whose approval is a re-confirmation rather than a re-derivation: N (ids).` Quote both; they tell a re-approved probe from a re-derived one (R6) and are no finding.

## Derivation anchors

`derived_from` takes one of four forms (probe schema v1.2, a revision that keeps every v1.1 probe valid):

- **Content anchor** `blob:<40 hex>` for an in-repository declaration: the declaration file's git blob at derivation (`git rev-parse <commit>:<path>`). It names no commit, so a probe re-derived in the same pull request as its declaration change stays clean after a squash merge. The probe is stale when the file is dirty, gone at HEAD, or its HEAD blob differs. A directory or submodule at the path is no regular file and reads as stale; a symlink is anchored by its link text, not by the file it points to.
- **Section anchor** `sections:<64 hex>` for a Markdown declaration whose cited sections each resolve exactly once: `declaration.sections` lists one locator per cited section, `heading: "3.1.1"` (the heading's first token, one trailing dot stripped) or `row: AK-OS-07` (a pipe-table row's first cell), each with `digest`, the SHA-256 of that section's exact bytes; `derived_from` is the SHA-256 of `json.dumps([[kind, locator, digest], …], separators=(",", ":"), ensure_ascii=False)` in list order (`reach_audit.section_anchor()`). The probe is stale only when a cited section changed, no longer resolves, or matches more than once; an edit elsewhere in the file leaves it clean. The free-text `location` stays the citation. SHA-256 repositories can use it too, since it hashes bytes, not git objects.
- **Pinned ref** for an inherited spec, compared with `inherits[].ref`; a content anchor there is refused.
- **Commit** for an external anchor (HEAD, unmonitored), and, as a migration rule, for an in-repository probe derived before v1.1: it stays valid, with its commit-ancestry check, until the next re-derivation records a content anchor. A SHA-256 repository keeps commit anchors, since the content anchor is SHA-1 only.

Two limits to state when asked: an edit that goes A→B→A reads clean against A, since the content is the anchored one again (an accepted trade-off); and any byte change, whitespace included, is a change.

## Re-baseline rule

The runner's baseline for a probe is the commit that recorded its current `derived_from`. Moving `derived_from` starts a fresh baseline, so every earlier change to the file is forgiven, and that is exactly how a single commit could lower an expectation and bump `derived_from` to launder its own weakening. The runner therefore accepts a moved `derived_from` as a **re-derivation only when the declaration itself changed**:

- section anchor: every new digest must be its section at the baseline commit, each locator resolving once there, and a previously anchored section (or, from a file anchor, the file) must have changed since the recording commit. Moving a file anchor onto sections of an unchanged file is a migration: clean only when nothing but `derived_from`, `declaration.sections`, and `approval` changed. The reverse relabel, sections back to a `blob:`, is accepted on the same terms;
- re-confirmation (`approval.mode: reconfirmed`): on top of the anchor proof, only `derived_from`, the section digests, and `approval` may differ from the derivation it re-confirms, compared against the commit that recorded that derivation;
- content anchor: the new `blob:` must be the declaration's content at the baseline commit, and the previously anchored content (the old blob, or for a migrating commit anchor the file's content at that commit) must differ from it. A pure rename keeps the blob and moves `declaration.path`; the runner recognises it by path plus blob;
- commit anchor: the declaration's latest commit as of the new `derived_from` must lie outside the old one's history;
- inherited spec: the pin in `spec/.spec-config.yml` must have moved to the new value;
- external anchor: it can't show a change, so its re-baseline is never accepted.

Otherwise the probe is reported `weakened` with `re-baselined without a declaration change: <moved>`, where `<moved>` names the baseline and the old and new anchor (or, for a path move, `<baseline> moved the declaration of <df> from <old> to <new>`), followed by the reason:

| Reason suffix | Meaning |
|---|---|
| `…, but <new> is not the content of <rel> at <baseline>` | the new blob isn't what the declaration held when the probe was recorded |
| `…, but <new_df> is not a content anchor of the form blob:<40 hex digits>` | the new anchor is malformed |
| `…, but a content anchor needs a declaration file inside the repository` | the new anchor sits on a declaration without a repository path |
| `…, but the previous derived_from is not a content anchor of the form blob:<40 hex digits>, so no declaration change can be shown` | the old anchor was a malformed `blob:` value |
| `…, but the previous derived_from cannot be resolved to a commit, so no declaration change can be shown` | the old commit anchor is gone (for example after a squash merge) |
| `…, but <rel> did not change in between` | the anchored content is the same before and after the move |
| `…, but the previous derived_from <df> is not the content of <rel> at <recording>, where it was recorded, so no declaration change can be shown` | the old `blob:` anchor never matched the declaration when it was recorded, so it proves no change |
| `…, but the content of <rel> at the previous derived_from <commit> is not its content at <recording>, where it was recorded, so no declaration change can be shown` | the old commit anchor pointed at other declaration content than the file held when it was recorded |
| `…, but the same commit changed the probe beyond declaration.path, which a pure move of the declaration does not justify` | a pure move may change only `declaration.path` and the `approval` stamp of its re-derive; `expected`, `observe`, `tier`, or `declaration.location` changed too |
| `…, but <new_rel> already held <new_df> when the previous derivation was recorded in <recording>, so re-pointing at it shows no declaration change` | the probe was re-pointed at a file that already held that content, so nothing changed |
| `…, but the probe changed in <commits> after its previous derivation was recorded in <recording>` | a pure move or migration only relabels the previous derivation, and the probe was edited after it |
| `…, but its previous derivation was no re-derivation either: <reason>` | the relabelled derivation was itself a re-baseline without a declaration change; `<reason>` names why |
| `…, but the recorded sections are not the content of <rel> at <sha>: <mismatches>` | a new section digest isn't what the declaration held at the baseline commit, or a locator didn't resolve once there |
| `…, but the previous derived_from <df> is not the content of its sections of <rel> at <sha>, where it was recorded, so no declaration change can be shown` | the old section anchor never matched the declaration when it was recorded |
| `…, but the anchored sections of <rel> did not change in between` | a section anchor moved although none of its sections changed |
| `…, but <rel> already held these sections when the previous derivation was recorded in <sha>, so re-pointing at it shows no declaration change` | the probe was re-pointed at another file that already held the same sections |
| `…, but a re-confirmation may change only derived_from, the section digests and approval, and it also changed <fields> against the derivation recorded in <sha>` | a re-confirmation also changed `expected`, `observe`, `tier`, `environment`, the declaration target, or a locator; revert it and re-derive instead |

Consequences to state plainly to the operator:

- A corrected typo in `derived_from`, a re-approval made "to be safe", or any `derived_from` move on a probe with an external anchor stays `weakened` until its declaration changes. The way back to clean is a re-derive **after a real declaration change**, never a hand edit and never a revert of the revert.
- The rule can't tell a whitespace-only declaration change from a substantive one; a reformatting commit to the declaration file counts as a change. That is a stated limit of the mechanism, not a bug to route around.
- A probe that was weakened for another reason (a later commit to the file) isn't cleared by a re-approval alone either; the re-derive must move `derived_from` to an anchor the declaration actually changed to.
- Residual risk: deleting the declaration and re-pointing the probe at a file created or changed after the previous recording, with a weakening in the same commit, is indistinguishable from a rename plus edit and is accepted.
- Residual risk: commit anchors keep the pre-v1.1 rules, including the two-commit re-anchor that a content anchor now refuses; re-derive to a content anchor to close it. A later pure move over an old commit anchor that no longer resolves reads `weakened`.
