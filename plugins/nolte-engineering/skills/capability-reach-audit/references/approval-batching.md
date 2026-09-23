# Approval batching and persistence

Contents: §Batch order and size · §Batch table · §Answer vocabulary · §Persistence · §Not-constructible manifest

Loaded by `capability-reach-audit` `derive` step 3 (rendering a batch, reading an answer) and step 4 (writing approved probes). Governing rules: `spec/project/capability-reach-audit/` §"Derivation, approval, and durability" and executor requirement R4 (present before persisting; persist only the approved set).

## Batch order and size

1. One batch per declaration source, in the fixed order **requirement → endpoint → capability → inventory**. A source whose `presence` is `absent` or `skipped` (quote its `reason`), or with no drafted probe, is named in one line and produces no batch.
2. A source with more than **twelve** drafts is split into sub-batches of at most twelve, in the payload's `entries[]` order, labelled `endpoint 1/3`, `endpoint 2/3`, and so on. Twelve rows keep one table readable in a single turn; the operator can still answer the whole sub-batch with one word.
3. `not_constructible` entries never enter a batch. They are listed once, after the last batch, grouped by reason (see §Not-constructible manifest).

## Batch table

Render each batch as one table, followed by the `assumes[]` of every row that has any:

```text
### Batch <source> (<k>/<n>): <count> drafts

| # | id | declaration | tier | expected | observe | derived_from |
|---|---|---|---|---|---|---|
| 1 | endpoint-scan-workflow-dispatch-runs | .github/workflows/scan.yml (on.workflow_dispatch) | T0 | 300 runs | gh run list --workflow scan.yml … --jq length | 9feca6a8d2c1 |
| 2 | … | … | … | … | … | … |

Assumes:
- #1 needs `gh` authenticated for this repository (evidence: .github/workflows/scan.yml:3)
- #2 needs Taskfile target `db:up` (evidence: Taskfile.yml:41)

Answer: approve all | approve <ids or #s> | reject <ids or #s> [reason] | skip
```

- `declaration` is `path (location)` for an in-repository anchor, `inherited <topic/slug> @ <ref>` for an inherited spec, `external: <where>` for the rest. Show `monitoring: unmonitored` in the same cell when the scanner set it, so the operator knows this probe re-derives only on request (R6).
- `expected` is `<value> <unit>` for a count and `<n> values, <unit>` for a set; the full set is shown on request.
- `observe` is the argv joined by spaces, cut at 80 characters with `…`; the full argv is shown on request. Never paraphrase it: the argv is what the operator approves.
- Show the scanner's `note` under the table when present. It is an inventory fact ("no local referent found by …"); never turn it into a verdict word.

## Answer vocabulary

| Answer | Effect |
|---|---|
| `approve all` | every row of this batch still open is approved |
| `approve <ids or #s>` | the named rows are approved; the rest of the batch is rejected |
| `reject <ids or #s> [reason]` | the named rows are rejected; the rest of the batch **stays open** and is re-shown for an explicit `approve all`, `approve <ids>`, or `skip`. A rejection never approves anything |
| `skip` | nothing still open in this batch is approved or rejected; the drafts are dropped and re-drafted on the next `derive` |
| anything else | ask again; never infer approval from silence, a question, a partial sentence, or the rows a `reject` didn't name |

A row the operator wants changed (a different tier, a tighter expected value, another argv) is **rejected** with that wish as the reason; the skill never edits a draft into an approved probe, because the operator would then be approving text the scanner did not return. Re-run `derive` with the entry filter set to that draft's `declaration.path` (the scanner filters by declaration path, not by id) and the wish forwarded as context.

A batch is answered once no row is open. After every answered batch, append one entry to `decisions[]` (`gate: approve-<source>-<k>`, the batch's ids as the question, the operator's answer verbatim, `at`) and checkpoint (`phase: approved-<source>-<k>`). On resume, a batch whose gate is already in `decisions[]` is not asked again.

## Persistence

For each approved draft write `<target>/project/reach-probes/<id>.yml`:

```yaml
# Approved reach probe; derived by capability-reach-scanner, approved via capability-reach-audit.
# Never edit in place: any later commit to this file is reported as weakened. Re-derive instead.
id: <id>
summary: <as drafted, if present>
declaration: {<as drafted>}
tier: <as drafted>
expected: {<as drafted>}
derived_from: "<as drafted>"
environment: [<as drafted, if present>]
teardown: [<as drafted, if present>]
observe: {<as drafted>}
approval:
  approved_at: "2026-09-23T14:30:12Z"
  approved_by: "<operator>"
```

- Copy the draft **as returned**: same keys, same values, no additions except `approval`. The schema (`schemas/reach-probe-v1.0.schema.yaml`) has `additionalProperties: false` at every level.
- `approved_at` is the current UTC time in `YYYY-MM-DDTHH:MM:SSZ` form and **quoted**; unquoted, the loader turns it into a timestamp object and the probe fails the schema.
- `approved_by` is `git -C <target> config user.name`. When that is empty, ask the operator for the name to record; never write an empty string (schema `minLength: 1`) and never fall back to a generic label.
- Create `project/reach-probes/` when absent. When `<id>.yml` already exists, overwrite it only if this derive round re-derived its declaration path (entry filter or stale routing); otherwise stop and ask, because two declarations mapped to one id.
- Rejected and skipped drafts are written nowhere in the target. Their only trace is `decisions[]` in the checkpoint.

After writing, tell the operator: the runner reads the probe set from git history, so the set must be **committed** before `run` can execute it; recommend one commit per derive round touching only `project/reach-probes/`, so the baseline commit is unambiguous.

## Not-constructible manifest

Write `<target>/project/reach-probes/_not-constructible.yml` on every derive round, validated by `schemas/reach-not-constructible-v1.0.schema.yaml` (closed objects, no verdict field):

```yaml
# Not-constructible manifest; written by capability-reach-audit derive, read by the runner.
# Empty `entries` means every declared entry received a probe; an absent file means nothing was recorded.
entries:
  - id: <scanner entry id>
    declaration: {source: <entry.source>, path: <anchor.path> | inherited_spec: <anchor.inherited_spec> [, hub: <anchor.hub>], location: "<entry.location>"}
    reason: <scope_not_countable | needs_model_judgement | effect_in_third_party | missing_environment_target | missing_observation_helper>
    detail: <the scanner's detail, if any>
    derived_from: "<as returned>"
    recorded_at: "2026-09-23T14:30:12Z"
```

- Only entries the scanner returned as `not_constructible` go in. A draft the operator rejected or skipped is not one: it had a probe, the operator declined it, and it is re-drafted on the next `derive`. Putting it here would count a decision as an audit blind spot.
- The scanner returns no `declaration` object for a not-constructible entry; it returns `source`, `anchor{path | inherited_spec [+ hub] | external}`, and `location`. Build `declaration` from them: `source` and `location` copied; `anchor.path` → `declaration.path`; `anchor.inherited_spec` → `declaration.inherited_spec`, plus `hub` only when the anchor carries one. An `external` anchor yields a declaration with **`source` and `location` only**, no `path` and no `inherited_spec`: the schema's `Declaration` requires exactly those two, forbids `path` and `inherited_spec` together, allows `hub` only beside `inherited_spec`, and has no `external` field, so a literal copy of the anchor fails validation. Keep the external `where` by prefixing `detail` with `external anchor: <where>` followed by a semicolon and a space. `recorded_at` is quoted UTC, like `approved_at`.
- Ids must be unique and must not name a probe file; when a re-derive turns a manifest entry into an approved probe, remove it from the manifest in the same round, or the runner reports a `contradiction` and withholds the probe.
- The manifest is part of the probe set: commit it with the probes. When the round produced no `not_constructible` entry, write `entries: []` anyway.

Then group the entries by reason code in the summary, show each entry's `detail` under its code, and propose the two actionable groups as work in the target repository:

| Reason code | Meaning | Proposed work |
|---|---|---|
| `missing_environment_target` | no Taskfile target stands up the environment the probe needs (R9) | add the Taskfile target the `detail` names; the entry becomes a T1 or T2 probe on the next `derive` |
| `missing_observation_helper` | the observation needs a program (seed, act, count) the repository doesn't ship | add the helper the `detail` names under the repository's scripts; then `derive` again |
| `scope_not_countable` | the declaration states no count and no set, so the schema admits no expectation | tell the operator; amending the declaration is the only way in, and that is a decision, not audit work |
| `needs_model_judgement` | the only executing path is a Claude session; no deterministic observation point | no probe possible; record as a known not-probed remainder |
| `effect_in_third_party` | the effect lands in a system with no readable record; the spec's open question | no probe possible today; record as a known not-probed remainder |

The runner reports each manifest entry as `not probed` with reason `not constructible: <code>` and counts it in the headline. The operator decides whether each actionable entry becomes an issue in the target repository; the manifest keeps it counted until it does.
