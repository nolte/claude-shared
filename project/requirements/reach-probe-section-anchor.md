# Requirements — Section-level anchors and quick re-confirmation for capability-reach probes

<!--
Produced via the `requirements-elicit` skill, following
spec/project/requirements-elicitation/.
`c_d` is an uncertainty proxy (self-consistency-derived), not a calibrated
probability. A requirement is `confirmed` only after an explicit teach-back.
-->

## Bounded context

- **What is being built:** an extension of the capability-reach audit (`spec/project/capability-reach-audit/`,
  the `capability-reach-audit` skill, its runner `reach_audit.py`, and the `capability-reach-scanner`
  agent in `nolte-engineering`) that lowers the operator effort a declaration edit causes. Two parts:
  (a) **section anchors** for probes whose declaration is a Markdown document, so an edit elsewhere in
  the file no longer makes the probe stale; (b) a **quick re-confirmation** for any stale probe, so a
  declaration change that doesn't affect the probe costs one reviewed confirmation instead of a
  re-derivation.
- **For whom:** the operator of a consumer repository that runs the audit (reference consumer:
  `nolte/kamerplanter`, 14 probes on `origin/develop` on 2026-09-25).
- **Trigger:** nolte/claude-shared#674, follow-up of #668 / #673 (merged `66409882`), which anchors
  every in-repository probe on the whole declaration file (`derived_from: blob:<sha1>`, schema v1.1).
- **Out of scope:** section anchors for non-Markdown declarations (Python symbols, YAML key paths,
  README tables) — those use the quick re-confirmation; guessing a moved section by title; performing
  the one-time migration inside a consumer repository (this work ships the migration capability; running
  it in kamerplanter is the consumer's step).

## Understanding KPI

- Thresholds: `τ_low = 0.4`, `τ_high = 0.8`, self-consistency `k = 2`, question budget = 10 (spec defaults)
- `U_gate = min_d c_d` over required dimensions = **0.8**
- Termination: `saturation` (7 questions used, teach-back of the full set confirmed on 2026-09-25)

### Gap matrix

| Dimension | Applicable | `c_d` | Uncertainty source | Evidence event |
|---|---|---|---|---|
| `functional` | yes | 0.9 | specification | Q2 (both paths A and B), Q3 (re-confirmation rules), Q4 (locator forms); teach-back confirmed |
| `non_functional` | yes | 0.85 | specification | #673 laundering proof carried over (brief, teach-back point 7); replay measurement Q6 |
| `constraints` | yes | 0.85 | interpretation | schema revision rule of `spec/project/yaml-json-schema/`; v1.1 commit and blob anchors stay valid; teach-back |
| `domain_objects` | yes | 0.8 | interpretation | locator shape `declaration.sections` and per-locator digest — assumed, then confirmed in teach-back; k=2 sketches (combined vs per-locator digest) diverged, resolved by Q5 "report which section changed" need |
| `actors` | yes | 0.9 | — | operator (approves), scanner agent (proposes locators), runner (compares) — bounded context, teach-back |
| `acceptance_criteria` | yes | 0.85 | specification | Q6 replay chosen; measured 85 → 11 on 2026-09-25 |
| `edge_cases` | yes | 0.8 | specification | Q5 (not found = stale, several locators), ambiguous locator rule confirmed in teach-back |
| `scope_boundaries` | yes | 0.9 | specification | Q2 (Markdown only for A), Q5 migration (all Markdown probes, one-time) |

## Requirements

- **R1** — WHEN a probe's declaration is a Markdown file inside the target repository and every cited
  section resolves unambiguously, the scanner SHALL record one or more structured locators in
  `declaration.sections`, each either `heading: "<number>"` or `row: "<id>"`, and the free-text
  `declaration.location` SHALL stay as the human-readable citation.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: Q4 "Überschrift und Tabellen-ID"; teach-back (2), assumption on `declaration.sections` confirmed
- **R2** — A `heading` locator SHALL select the heading whose first token (the section number, e.g.
  `3.1.1`) equals the locator, through the line before the next heading of the same or a higher
  level; a `row` locator SHALL select the single Markdown table row whose first cell equals the locator.
  - _dimension_: `domain_objects` · _status_: `confirmed` · _source_: Q4; REQ-025 structure (57 headings, numbered and unique; 24 `AK-…` rows)
- **R3** — WHEN a probe is derived or re-confirmed with section locators, the executor SHALL store a
  digest of each selected section's exact text (whitespace significant) per locator, and the runner
  SHALL report the probe **stale** WHEN any locator's section changed or no longer resolves, naming
  the locator; it SHALL NOT follow a renumbered or renamed section.
  - _dimension_: `edge_cases` · _status_: `confirmed` · _source_: Q5 "Nicht gefunden = stale"; teach-back (3)
- **R4** — WHEN a locator is ambiguous (the heading number or row id occurs more than once), the
  scanner SHALL NOT record a section anchor for that probe; the probe SHALL keep the file anchor.
  - _dimension_: `edge_cases` · _status_: `confirmed` · _source_: teach-back assumption confirmed
- **R5** — WHEN a probe is stale, the skill SHALL offer a **re-confirmation**: it SHALL show the diff of
  the declaration (or of each changed section) since the stored anchor, ask per probe, and on approval
  record the new anchor (blob or section digests), a new approval stamp, and a marker distinguishing
  the re-confirmation from a re-derivation; the probe's `expected`, `observe`, `tier`, and declaration
  target SHALL NOT change in a re-confirmation.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: Q2 "Beides"; Q3 "Diff zeigen + eigenes Feld"; teach-back (4)
- **R6** — The report SHALL distinguish a re-confirmed probe from a re-derived one.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: Q3 ("damit der Bericht Bestätigungen von echten Neuableitungen unterscheidet")
- **R7** — The runner SHALL keep the anti-laundering strength of #673 for section anchors and
  re-confirmations: moving an anchor is accepted only when the anchored content changed and the new
  anchor matches the declaration at the recording commit, the previous anchor is proven where it was
  recorded, and a re-confirmation that also changes `expected`, `observe`, `tier`, or the declaration
  target is surfaced as **weakened**.
  - _dimension_: `non_functional` · _status_: `confirmed` · _source_: elicitation brief; teach-back (7)
- **R8** — The skill SHALL provide a one-time **migration** that proposes section locators for every
  existing probe on a Markdown declaration and records them only after per-probe approval; probes whose
  locators do not resolve unambiguously keep the file anchor.
  - _dimension_: `scope_boundaries` · _status_: `confirmed` · _source_: Q6 "Sofortige Migration aller Markdown-Probes"; teach-back (5)
- **R9** — Existing file (`blob:`) and commit anchors SHALL stay valid; the section anchor is a schema
  revision (v1.2, new file) that keeps every v1.1-valid probe valid.
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: `spec/project/yaml-json-schema/` revision rule; teach-back
- **R10** — Before the change merges, a replay over the history of a real Markdown declaration SHALL
  count, per commit, the stale events of file anchors versus section anchors for the probes anchored
  on it, and the pull request SHALL state the result.
  - _dimension_: `acceptance_criteria` · _status_: `confirmed` · _source_: Q7 "Replay der kamerplanter-Historie"; measured 2026-09-25 on `spec/req/REQ-025_Datenschutz-Betroffenenrechte.md` (17 edits, 5 probes): **85** stale events with file anchors, **11** with section anchors (§3.1.1 changed once, §3.5 twice, AK-OS-07 once); caveat: the five probes did not exist over the whole history, so the replay is hypothetical

## Surviving assumptions / open risks

- **Replay representativeness.** The 85 → 11 measurement covers one document and five probes over a
  history in which those probes mostly did not yet exist. A second document would strengthen it.
- **Section boundaries in unusual Markdown.** Setext headings, headings inside code fences, and tables
  without a leading pipe are not covered by R2; a locator that hits one of them must fail as
  not-resolvable (R3/R4) rather than cut a wrong section.
- **Re-confirmation as a rubber stamp.** R5 makes the diff mandatory, but cannot force the operator to
  read it; the `reconfirmed` marker (R6) keeps the choice auditable.
- **Migration in the consumer.** R8 ships the capability; running it in kamerplanter and approving
  each probe is the consumer's step and is not verified by this repository's gate.

Refs: `nolte/claude-shared#674`, `nolte/claude-shared#668`, `nolte/claude-shared#673`, `spec/project/capability-reach-audit/`.
