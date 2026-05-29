# Decision — Behavioural eval harness: promptfoo vs. pytest

Status: proposed
Date: 2026-05-29
Scope: choosing the framework for **behavioural** evals of this plugin's skills/agents
(does a change to a skill / agent / spec measurably improve the end result?). The
existing static layer (`scripts/validate_skills.py`, frontmatter/structure) is out of
scope and stays as-is — it is *Layer 0* below.

> **Decision (recommendation): use promptfoo as the primary behavioural-eval harness**,
> anchored first on report-producing agents, driving the agent through a thin custom
> provider over `claude -p`. Keep `validate_skills.py` static checks in Python/`task`.
> Use a pytest-driven runner only as the documented escape-hatch for file-mutating
> *skills* (scaffolding) where assertions are about written files and repo state.
> The decision flips to **pytest-primary** if the eval corpus turns out to be dominated
> by file-mutating skills rather than report/review agents (see §When the decision flips).

This document is *not executed* — the snippets are illustrative sketches that show how
each framework would wire up, not a benchmarked run.

## Why this is hard (recap)

Skills/agents are *prompts*; their output is non-deterministic. A "test" is therefore:
scenario → run headless → **grade** (deterministic assertions + LLM-as-judge) →
**pass-rate** over N samples. "A change has a positive effect" is only provable as a
**baseline-vs-change comparison** of the same suite (A/B regression for prompts).
The framework's job is the *grading + sampling + comparison + reporting* layer; both
candidates can *drive* the agent the same way (`claude -p`), so the layer above is the
real differentiator.

## Anchor target

`agents/spec-readiness-reviewer.md` — read-only (`Read, Glob, Grep, Bash`), input =
a spec slug, output = one severity-sorted Markdown report (no file writes). It is the
cleanest input→output case (no mid-flow user turn) and its governing spec
(`spec/project/spec-readiness/`) plus its own Hard rules / Output-shape give us a ready
made grading rubric. Fixture: one spec file with a *planted* MUST-vs-MUST-NOT
contradiction and one orphan Acceptance Criterion, so a correct run must surface both.

## Comparison matrix

| Axis | promptfoo | pytest (+ DIY helpers) |
|---|---|---|
| **Baseline-vs-change comparison** (the core goal) | Native: multiple providers/configs side-by-side; `promptfoo eval` + `promptfoo view` diff; per-assertion pass-rate | DIY: write `scorecard.json`, diff with a custom `compare.py` |
| **LLM-as-judge / rubric** | Built-in (`llm-rubric`, `g-eval`, `model-graded-*`) | DIY: a `judge()` helper that calls the API and parses a score |
| **N-sampling / pass-rate / flakiness** | `--repeat N`, assertion thresholds | DIY: parametrize/loop + aggregate |
| **Deterministic assertions** | `contains`, `regex`, `not-contains`, `is-json`, `javascript`, `python` | Strongest: arbitrary Python `assert`, full fixture access |
| **Driving the agent (tool-use, multi-turn, scripted user)** | Single-shot is natural; multi-turn possible but awkward for "dispatch a plugin agent against a fixture repo" | Full control via the Claude Agent SDK: scripted user turns for judgment-heavy skills |
| **Fixtures: repo state before/after, file-write assertions** | Awkward — text-in/text-out oriented; file side-effects need a custom provider returning a diff | Native: `tmp_path`, fixture dirs, snapshot files |
| **CI / toolchain fit** | Adds a **Node/npx** toolchain to a currently Node-free repo (`actions/setup-node`); no `node_modules` commit needed (`npx promptfoo`) | Drops into existing `task test`; Python 3.12 already in CI; same language as `validate_skills.py` |
| **Reporting / UI / shareability** | Web UI (`promptfoo view`), shareable HTML, JSON output | Terminal + JUnit XML; any UI is DIY |
| **Cost control / caching** | Built-in caching, `--no-cache`, per-run token accounting | DIY |
| **Spec-AC traceability** | Pull `- [ ]` AC lines into the `llm-rubric` text | Pull the same AC lines into the `judge()` rubric |
| **Maintenance model** | External tool, declarative YAML config; matches this repo's "declarative spec + thin script" aesthetic | In-house Python; full control but you own every eval primitive |

The two decisive rows for *this* repo and *this* goal: **baseline-vs-change comparison**
(promptfoo native, pytest DIY) and **fixtures/file-side-effects** (pytest native,
promptfoo awkward). The anchor we chose — a report-producing agent — lands squarely in
promptfoo's sweet spot.

## Sketch A — promptfoo (anchored on spec-readiness-reviewer)

`evals/promptfooconfig.yaml` (illustrative):

```yaml
description: spec-readiness-reviewer behavioural eval

prompts:
  - "Readiness check for promoting {{spec_slug}}"

providers:
  # Fidelity route: drive the real agent through Claude Code headless.
  - id: "exec: bash evals/providers/run_agent.sh"
    label: agent@HEAD
  # Cheaper, more deterministic route: the agent body as system prompt,
  # the fixture spec inlined as a var (tests the derivation discipline,
  # not the file-discovery tools).
  - id: anthropic:messages:claude-sonnet-4-6
    label: agent@anthropic-direct
    config:
      # strip frontmatter from the agent file before use
      systemPrompt: file://./providers/spec-readiness-reviewer.system.md

defaultTest:
  vars:
    spec_slug: project/fixture-contradiction
  assert:
    # deterministic
    - type: contains
      value: "## Critical"
    - type: regex
      value: "fixture-contradiction.*MUST.*MUST NOT"
    - type: not-contains
      value: "Blocker"            # invented severity outside the canonical scale
    # LLM-as-judge against the spec ACs + the agent's Output-shape
    - type: llm-rubric
      value: |
        PASS only if ALL hold:
        - Severity-sorted, canonical buckets only (Critical/Warning/Suggestion/Info).
        - The planted MUST-vs-MUST-NOT contradiction appears under ## Critical with a
          concrete spec-path + line/section reference.
        - The orphan Acceptance Criterion is flagged under ## Warning.
        - No file write is claimed; the output is a report only.

tests:
  - vars: { spec_slug: project/fixture-contradiction }
```

Prove a positive effect:

```bash
# baseline
git stash; npx promptfoo eval -o evals/out/base.json
# change (edit the agent or its spec), then:
git stash pop; npx promptfoo eval -o evals/out/head.json --repeat 5
npx promptfoo view            # side-by-side pass-rate per assertion, base vs head
```

A change is justified when the per-assertion pass-rate rises on the targeted scenarios
with no regression elsewhere, at comparable or lower token cost.

## Sketch B — pytest (same anchor)

`evals/conftest.py` (illustrative):

```python
import json, subprocess, pathlib

def run_agent(prompt: str, repo: pathlib.Path) -> str:
    out = subprocess.run(
        ["claude", "-p", prompt, "--plugin-dir", str(repo),
         "--output-format", "json"],
        capture_output=True, text=True, check=True,
    )
    return json.loads(out.stdout)["result"]

def judge(report: str, rubric: str) -> float:
    # DIY: call the Anthropic API, ask for a 0..1 score against `rubric`, parse it.
    ...
```

`evals/test_spec_readiness_reviewer.py` (illustrative):

```python
import pytest

RUBRIC = pathlib.Path("evals/rubrics/spec_readiness.md").read_text()

@pytest.mark.parametrize("run", range(5))   # N-sampling
def test_planted_contradiction(run, fixture_repo):
    report = run_agent("Readiness check for promoting project/fixture-contradiction",
                       fixture_repo)
    # deterministic
    assert "## Critical" in report
    assert "Blocker" not in report
    # judge
    assert judge(report, RUBRIC) >= 0.8
    # file-side-effect guard (pytest's strength): nothing was written
    assert fixture_repo_unchanged(fixture_repo)
```

Prove a positive effect: run the suite on the baseline commit → `scorecard-base.json`
(pass-rate over N per scenario), run on the change → `scorecard-head.json`, then
`python evals/compare.py base head` diffs them. Every primitive — judge, sampling
aggregation, diff, reporting — is hand-built.

## When the decision flips

Choose **pytest-primary** instead if any of these hold:

- The eval corpus will be dominated by **file-mutating skills** (scaffolding:
  `project-structure-apply`, `mkdocs-structure-apply`, `readme-structure-apply`,
  `pull-request-create`), where assertions are about written files / repo state and
  golden snapshots — pytest's fixture model is far more natural than a promptfoo custom
  provider that has to return a diff.
- Avoiding a second toolchain (Node) in a Python-only repo is a hard constraint.
- Judgment-heavy skills with **mid-flow user approval** dominate (e.g. `spec-drift-audit`,
  the `*-apply` skills), needing scripted multi-turn user simulation — easier with the
  Claude Agent SDK inside pytest than inside promptfoo.

## Recommendation and next step

1. **promptfoo primary** for behavioural evals, starting with report/review *agents*
   (`spec-readiness-reviewer`, `prose-vale-curator`, `feature-consistency-reviewer`, …) —
   their input→output shape is promptfoo's sweet spot and they directly serve the
   "prove a change improved the result" goal via native side-by-side comparison.
2. **Keep `validate_skills.py` static checks** in Python/`task` as Layer 0 (cheap,
   deterministic, every PR).
3. **pytest escape-hatch** for file-mutating skills, wired into the same `task test`
   target so CI has one entry point.
4. **Wire CI path-filtered**: Layer 0 on every PR; behavioural evals only when the
   touched skill/agent/spec changed, plus a small smoke set; N-sample pass-rate
   thresholds rather than hard pass/fail; baseline scorecard as a CI artifact.

Open follow-ups before building: pin the eval model; decide the fixture-repo layout
(reuse the per-skill `examples/*.md` as the scenario seed corpus); decide whether the
`llm-rubric` text is generated mechanically from each spec's `- [ ]` Acceptance Criteria.
