# Example 03 — `flake`, no fix needed, record-only with generalist tracking PR

Demonstrates the no-dispatch branch for `flake`: a single-headSha re-run returns green, no infra signal explains the first failure, and per the spec the work is documenting the flake in the project's flake registry — **not** opening a code-fix PR. The skill produces a generalist tracking PR that adds a flake-registry entry; it does **not** dispatch a specialised agent.

## Input prompt

> Der `tests.yml`-Run auf `develop` war heute morgen rot, jetzt ist er nach einem Re-Run grün. Ich glaube, das war ein Flake — kannst du das ordentlich triagen und in die Flake-Registry eintragen?

## Input files

Repository state when the skill is invoked:

- `spec/project/workflow-health/en.md` — present, declares `flake` as one of the six classes and requires *reproducible evidence* (re-run of the same `headSha` returned green and no infra signal explains the first failure).
- `.github/workflows/tests.yml` — required check on `develop`.
- Two `gh run view --json …` calls on the same `headSha`:
  - First run (run id `9988333444`): conclusion `failure`, failing step `pytest tests/integration/test_eventual_consistency.py::test_settle_within_2s` with timeout-after-2s assertion.
  - Second run (same `headSha`, run id `9988333445`, triggered manually as a re-run): conclusion `success`, same step passes in 1.1s.
- `gh run view 9988333444 --log-failed` excerpt:
  ```
  AssertionError: expected settled within 2.0s, got 2.04s (margin 0.04s)
  ```
- `git log --oneline -1 <headSha>` shows a docs-only commit (`docs(roadmap): refine R-12 wording`). The diff doesn't touch `tests/`, doesn't touch `tests.yml`, doesn't touch any application code under test.
- No GitHub status incident, no rate-limit or 5xx in the failed-step log, no token / OIDC error — `infra` and `secret drift` are excluded.
- `FLAKES.md` exists at the repo root and is the project's flake registry (entries shaped as `## <test id>` blocks with run links and a one-line root-cause hypothesis).
- `agents/` directory at runtime contains the same set as the other examples; none of their `description:` lines name *flake-registry maintenance*.

## Expected behaviour

1. **Reproducible-evidence check.** The skill verifies the spec's strict definition of `flake`: same `headSha`, second run returned green, no infra signal in the first run, the failing test's tolerance (2.0s) is suspiciously close to the observed value (2.04s) — a timing-margin classic. The classification is `flake`.
2. **Confirm with the user.** `flake` is one of the three high-cost classes (misclassifying a real `defect` as `flake` and re-running into green is exactly the *Gotchas* anti-pattern). The skill quotes the spec's reproducible-evidence rule in German and asks the user to confirm before proceeding.
3. **No agent dispatch.** Per the SKILL's §3.3 *Recognise the no-fix classifications*, `flake` produces no specialised-agent dispatch by design. The skill **does not** `Glob` `agents/*.md` for a match — there is no fix to delegate. (The runtime-discovery walk is skipped; the no-fix branch is detected before candidate enumeration.)
4. **Record in the flake registry.** The skill adds a new entry to `FLAKES.md`:
   - Heading with the fully-qualified test id (`tests/integration/test_eventual_consistency.py::test_settle_within_2s`).
   - Links to both run URLs (the failing run `9988333444` and the green re-run `9988333445`).
   - One-line root-cause hypothesis: *"timing-margin flake — observed 2.04s vs 2.0s assertion threshold; bump tolerance or stabilise the wait condition"*.
   - Date stamp `2026-05-10` and the `headSha` short hash for cross-reference.
5. **Open a generalist tracking PR.** The skill chains `pull-request-create` for a docs-only PR titled `docs(flakes): record tests/integration/test_eventual_consistency.py::test_settle_within_2s timing-margin flake`. The Risk / rollout notes carry literally:
   - `Triage classification: flake`
   - `Dispatched agent: no matching specialised agent—generalist remediation`
   The PR's Summary names this as a record-only entry (no test or production code is modified), and the body links the spec's `flake`-row text so reviewers see why no code fix shipped.
6. **Hard-rule guard.** The skill **never** proposes `continue-on-error: true` on the flaky test, **never** removes the test from the required set without a tracking Issue (the registry entry doubles as that tracking Issue's seed), and **never** re-runs the failed run more than the once-already-done re-run that produced the reproducibility evidence.
7. **Stop after PR open.** Final report names the run IDs (both first failure and re-run), the classification (`flake`), the literal `no matching specialised agent—generalist remediation` sentence, the tracking-PR URL, and the next-action hint *"invoke `pull-request-merge` after CI is green"*. No specialised agent was dispatched and the skill says so explicitly.
8. **Anti-pattern guard.** If the user pushes back with *"einfach noch einmal re-runnen und gut"*, the skill cites the SKILL's *Gotchas* — *"`flake` without reproducible evidence is `defect`"* — and refuses to record a flake without the second-run-green proof already in hand. Here the proof exists, so the path stays `flake`; if it didn't, the class would flip to `defect` and the flow would fall through to dispatch instead.
