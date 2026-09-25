# Re-confirmation and migration to section anchors

Contents: §Section helpers · §Re-confirmation · §Migration · §Replay measurement

Loaded by `capability-reach-audit` `reconfirm` and `migrate`. Governing rules: `spec/project/capability-reach-audit/` §"Derivation, approval, and durability" (the SHOULD on section anchors and the MUST on re-confirmation) and requirements R5–R8 of `project/requirements/reach-probe-section-anchor.md` in the `claude-shared` repository. Probe shape: `schemas/reach-probe-v1.2.schema.yaml`. The runner decides whether a recorded anchor move is clean; this file only makes sure the skill records one that can be.

## Section helpers

Both helpers import the bundled runner, so a locator resolves here exactly as it resolves in `run`: an ATX heading outside fenced code and front matter whose first token, one trailing dot stripped, equals the locator, through the line before the next heading of the same or a higher level; or a pipe-table row (the line starts with `|`, at least two cells) whose trimmed first cell equals it. Setext headings and tables without a leading pipe never match. `-B` keeps Python from writing bytecode into the plugin directory. Both only read.

**Anchor helper.** Prints the match count per locator; when every locator resolves exactly once, prints the `declaration.sections` list and the `derived_from` value for it. Pass the locators in the order they will stand in `declaration.sections`, since the anchor covers that order:

```bash
git -C <target> show HEAD:<path> | python3 -B -c 'import sys, json; sys.path.insert(0, sys.argv[1]); import reach_audit as ra
content, sections = sys.stdin.buffer.read(), []
for arg in sys.argv[2:]:
    kind, locator = arg.split(":", 1)
    found = ra.find_sections(content, kind, locator)
    print(f"{arg}: {len(found)} match(es)")
    if len(found) == 1:
        sections.append({kind: locator, "digest": ra.section_digest(found[0])})
if len(sections) == len(sys.argv) - 2:
    print(json.dumps(sections, ensure_ascii=False)); print(ra.section_anchor(sections))' "${CLAUDE_PLUGIN_ROOT}/skills/capability-reach-audit/scripts" heading:3.1.1 row:AK-OS-07
```

**Section-diff helper.** Per locator, the match counts at the recording commit and at HEAD and, when both resolve once, the unified diff of that section and its digest at HEAD:

```bash
python3 -B -c 'import sys, subprocess, difflib; sys.path.insert(0, sys.argv[1]); import reach_audit as ra
repo, rec, path = sys.argv[2:5]
def show(rev): return subprocess.run(["git", "-C", repo, "show", f"{rev}:{path}"], capture_output=True).stdout
old, new = show(rec), show("HEAD")
for arg in sys.argv[5:]:
    kind, locator = arg.split(":", 1)
    before, after = ra.find_sections(old, kind, locator), ra.find_sections(new, kind, locator)
    print(f"== {arg}: {len(before)} match(es) at {rec[:12]}, {len(after)} at HEAD")
    if len(before) == len(after) == 1:
        sys.stdout.writelines(difflib.unified_diff(before[0].decode().splitlines(True), after[0].decode().splitlines(True), f"{rec[:12]}:{path}", f"HEAD:{path}"))
        print(f"digest at HEAD: {ra.section_digest(after[0])}")' "${CLAUDE_PLUGIN_ROOT}/skills/capability-reach-audit/scripts" <target> <recording-commit> <path> heading:3.1.1 row:AK-OS-07
```

The recording commit of a probe is `git -C <target> log -1 --format=%H -- project/reach-probes/<id>.yml`: for a stale probe that isn't also weakened, the probe file's latest commit is the one that recorded its derivation.

## Re-confirmation

A re-confirmation re-approves a **stale** probe whose declaration changed without affecting what it checks (R5). It moves only the anchor and the approval, and the report marks it (`approval is a re-confirmation, not a re-derivation`, plus the Provenance line `Probes whose approval is a re-confirmation rather than a re-derivation: N (ids).`), so the operator's choice stays auditable (R6).

**Eligible:** a probe the latest report lists `not probed` with `declaration changed since derivation: …`, not weakened, whose declaration is committed (`git status --porcelain --no-optional-locks -- <path>` empty; otherwise the operator commits the declaration first, since the new anchor must match the declaration at the commit that records it). **Not eligible**, route to `derive` instead: a section anchor whose reason says `not found` or `is ambiguous (<n> matches)` (a re-confirmation may not change a locator, and the runner never follows a renumbered section), a deleted or no-longer-regular declaration, and an inherited spec whose change can't be read at both refs.

Per eligible probe, in the order of the report's Probes table:

1. **Show the change since the anchor, never a summary of it.**
   - `blob:<sha1>` anchor: `git -C <target> diff <sha1> HEAD:<path>` (the whole file).
   - commit anchor: `git -C <target> diff <commit> HEAD -- <path>`.
   - section anchor: the section-diff helper with the recording commit and every locator of `declaration.sections`, in their order. Show the changed sections; say which ones are unchanged.
   - inherited spec: the diff of `spec/<inherited_spec>/` between the old and the new pinned ref in the hub checkout, when one is readable; otherwise the probe is not eligible.
2. **Show the probe's `expected`, `observe`, and `tier` next to the diff**, so the question is concrete: does the change leave the declared scope this probe measures as it was?
3. **Ask per probe**, one question each: `reconfirm <id>` | `derive <id>` | `skip <id>`. Never batch several probes into one answer, and never infer `reconfirm` from silence. `derive` routes the probe's declaration path to `derive` with the entry filter; `skip` leaves it stale.
4. **Compute the new anchor** from the committed declaration: `blob:` + `git -C <target> rev-parse HEAD:<path>` (SHA-1 repository; a commit anchor becomes a content anchor here, a SHA-256 repository records `git log -1 --format=%H -- <path>`), the anchor helper over the probe's existing locators in their order (section anchor), or the new pinned ref (inherited spec).
5. **Edit only these lines of the probe file**, keeping every other byte: `derived_from`, each `declaration.sections[].digest`, and the `approval` block rewritten as below. `expected`, `observe`, `tier`, `environment`, `teardown`, `summary`, `declaration.path`, `declaration.location`, and the locators stay as they are. Any other change is reported `weakened` with `…, but a re-confirmation may change only derived_from, the section digests and approval, and it also changed <fields> against the derivation recorded in <sha>`.

   ```yaml
   approval:
     approved_at: "<UTC now, YYYY-MM-DDTHH:MM:SSZ, quoted>"
     approved_by: "<git config user.name; ask when empty>"
     observation_digest: "<recomputed per approval-batching.md §Persistence; unchanged, since observe is>"
     mode: reconfirmed
   ```

6. **Checkpoint** (`phase: reconfirmed-<id>`) with the decision under `decisions[]`, then tell the operator to commit the re-confirmed probes in one commit that touches only `project/reach-probes/`, and to `run` again.

## Migration

A one-time step that moves every probe on a Markdown declaration from the whole-file anchor to the sections it cites (R8). It records a **re-derivation** of an unchanged declaration, never a re-confirmation.

1. **Select** the probes whose `declaration.path` ends in `.md`, that carry no `declaration.sections`, and that the latest report lists as executed or otherwise not stale and not weakened. A stale probe is re-confirmed or re-derived first; a migration must not hide a declaration change behind a relabel.
2. **Propose locators from `declaration.location` only**: each section number it cites (`§3.1.1 …` → `heading: "3.1.1"`) and each table-row id (`AK-OS-07` → `row: AK-OS-07`). A location that cites neither (`L42`, an unnumbered heading, a symbol) gets no proposal. Never pick a section by title or by nearness to a line.
3. **Resolve** each proposal with the anchor helper against HEAD. The probe keeps its file anchor, with the reason stated, when any locator matches nothing or more than once, or when the declaration has uncommitted edits.
4. **Ask per probe**, showing the `location`, the proposed locators with their match counts, and the first line of each resolved section: `migrate <id>` | `keep <id>`. Nothing is written without a `migrate` answer naming the probe.
5. **Write**, for each approved probe: `declaration.sections` (after `location`, in the proposed order, as the helper printed it), `derived_from: "sections:<…>"` from the helper, and a fresh `approval` stamp with `mode: derived` or no `mode` at all, never `reconfirmed` (a re-confirmation can't add locators). Keep `location` as the human-readable citation and every other field as it was; the runner accepts the move only as a relabel of the unchanged file that changed nothing but `derived_from`, `declaration.sections`, and `approval`.
6. **Report** the migrated count, the kept count with each reason, and the commit to make: one commit touching only `project/reach-probes/`, with no edit to the declarations in it.

## Replay measurement

To show what section anchors would save on a real declaration (R10), replay its history with the bundled script:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/capability-reach-audit/scripts/reach_replay.py" --repo <target> \
  --declaration <path> --probe <name>=heading:3.1,row:AK-OS-07 [--probe …] [--rev <rev>]
```

It walks the first-parent history of the file (no rename following), prints one line per commit, and ends with `file-anchor stale events: X` and `section-anchor stale events: Y`. The replay assumes every probe existed from the file's first commit, so quote it as a hypothetical measurement.
