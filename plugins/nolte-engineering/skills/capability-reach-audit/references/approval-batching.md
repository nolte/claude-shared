# Approval batching and persistence

Loaded by `capability-reach-audit` `derive` step 3 (rendering a batch, reading an answer) and step 4 (writing approved probes). Governing rules: `spec/project/capability-reach-audit/` §"Derivation, approval, and durability" and executor requirement R4 (present before persisting; persist only the approved set).

## Batch order and size

1. One batch per declaration source, in the fixed order **requirement → endpoint → capability → inventory**. A source whose `presence` is `absent` or `skipped` (quote its `reason`), or with no drafted probe, is named in one line and produces no batch.
2. A source with more than **twelve** drafts is split into sub-batches of at most twelve, in the payload's `entries[]` order, labelled `endpoint 1/3`, `endpoint 2/3`, and so on. Twelve rows keep one table readable in a single turn; the operator can still answer the whole sub-batch with one word.
3. `not_constructible` entries never enter a batch. They are listed once, after the last batch, grouped by reason (see §Not-constructible handover).

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
| `approve all` | every row of this batch is approved |
| `approve <ids or #s>` | the named rows are approved; the rest of the batch is rejected |
| `reject <ids or #s> [reason]` | the named rows are rejected; the rest of the batch is approved |
| `skip` | nothing in this batch is approved or rejected; the drafts are dropped and re-drafted on the next `derive` |
| anything else | ask again; never infer approval from silence, a question, or a partial sentence |

A row the operator wants changed (a different tier, a tighter expected value, another argv) is **rejected** with that wish as the reason; the skill never edits a draft into an approved probe, because the operator would then be approving text the scanner did not return. Re-run `derive` with the entry filter for that id and the wish forwarded as context.

After every answered batch, append one entry to `decisions[]` (`gate: approve-<source>-<k>`, the batch's ids as the question, the operator's answer verbatim, `at`) and checkpoint (`phase: approved-<source>-<k>`). On resume, a batch whose gate is already in `decisions[]` is not asked again.

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
- Create `project/reach-probes/` when absent. When `<id>.yml` already exists, overwrite it only if this derive round re-derived that id (entry filter or stale routing); otherwise stop and ask, because two declarations mapped to one id.
- Rejected and skipped drafts are written nowhere in the target. Their only trace is `decisions[]` in the checkpoint.

After writing, tell the operator: the runner reads the probe set from git history, so the set must be **committed** before `run` can execute it; recommend one commit per derive round touching only `project/reach-probes/`, so the baseline commit is unambiguous.

## Not-constructible handover

Group the payload's `not_constructible` entries by reason code, show each entry's `detail` under its code, and propose the two actionable groups as work in the target repository:

| Reason code | Meaning | Proposed work |
|---|---|---|
| `missing_environment_target` | no Taskfile target stands up the environment the probe needs (R9) | add the Taskfile target the `detail` names; the entry becomes a T1 or T2 probe on the next `derive` |
| `missing_observation_helper` | the observation needs a program (seed, act, count) the repository doesn't ship | add the helper the `detail` names under the repository's scripts; then `derive` again |
| `scope_not_countable` | the declaration states no count and no set, so the schema admits no expectation | tell the operator; amending the declaration is the only way in, and that is a decision, not audit work |
| `needs_model_judgement` | the only executing path is a Claude session; no deterministic observation point | no probe possible; record as a known not-probed remainder |
| `effect_in_third_party` | the effect lands in a system with no readable record; the spec's open question | no probe possible today; record as a known not-probed remainder |

These entries have no probe file, so the runner's report never counts them. Keep the list in the `derive` summary and in the checkpoint's `state:` so it survives the session; the operator decides whether each becomes an issue in the target repository.
