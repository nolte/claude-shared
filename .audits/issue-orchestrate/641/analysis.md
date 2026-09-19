---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "641"
classification: "spec-change"
secondary-classes: []
route: "direct"
status: approved
created: "2026-09-19"
group: "2026-09-19-verification-discipline-specs"
---

# Issue Orchestration — Pre-analysis (member of a group run)

- **Classification:** spec-change. **Route:** direct. **Requirements gate:** operator
  override at the group write gate (decision: obligation in `issue-orchestration` §Issue
  acquisition and `issue-batch-integration` §A, mirrored in both skills' operation 1).
- **Cause verification:** the issue's own measurement `grep -niE "diagnos|claimed
  cause|Ursache" spec/project/issue-orchestration/de.md` → re-run before editing: no
  hit; EN §"Issue acquisition and comprehension" (`en.md:96-130`) names comprehension,
  trust, prior art and the requirements gate, no cause check. Confirmed.
- **P1 spec** → `nolte-shared:spec` (inline): one MUST bullet + one acceptance criterion
  in `issue-orchestration` EN/DE and in `issue-batch-integration` EN/DE. DE files carry
  English H2 headings (`## Open Questions`) — pre-existing, left as is.
- **P2 skills** → `nolte-claude-dev:claude-plugin-developer`: `issue-orchestrate/SKILL.md`
  op 1 (two sentences) + hard rule, op-6 prose moved into
  `references/measurement-discipline.md` (new section "Verify an asserted cause before
  the first tracked change"), template placeholder `Asserted cause verified`;
  `issue-batch-orchestrate/SKILL.md` op 1 paragraph + hard rule. Body tokens:
  issue-orchestrate ~4965/5000 (Warning stays, 35 tokens headroom),
  issue-batch-orchestrate ~3312.
- **Falsification (issue's own five cases) against the new rule:**

  | Case | Asserted cause | Does the rule fire? |
  |---|---|---|
  | Frontend flake | fixture too large | yes: reading the runtime table before editing shows flat runtimes; refutation recorded, measurement wins |
  | Login gate | refusal message placed before the hash comparison | yes: reading the serialisation shows the message in the response body; the proposed placement would reopen an enumeration oracle |
  | Favourites resolver | latent side channel, both arms 404 | yes: reading the fifth catalogue's model shows the tenant field; the cause is true for four of five |
  | Favourites error clause | narrow to the driver's "collection missing" error | yes: reading the driver's membership check shows false on every 404, so the clause was never reached by that error |
  | Dependency sweep | three files install without hashes | yes: the rule forbids treating the green first run as verification ("a green existing check may share the blind spot"); the checker's exception matched its own spelling |

- **Refutation:** none. Deviation (local adaptation): the template placeholder line the
  specialist added, recorded here and in the group artifact.
