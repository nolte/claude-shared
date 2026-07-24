---
artifact-type: agent-description-baseline
feature: F-7
roadmap_item: R-9
sprint: 5
issue: 371
created: "2026-07-19"
measurement_method: "4-char/token estimate (est = len(concat)//4) over the concatenated agent `description` frontmatter per plugin agents/ root; identical to check_body_token_estimate in scripts/validate_skills.py — the single method fixed in F-5"
---

# Post-remediation agent-description baseline (F-7)

This is the baseline F-8's per-plugin guardrail freezes. It records the aggregate
agent-`description` weight per plugin **after** the F-7 remediation, measured with
the single committed method (see frontmatter). F-5's pre-remediation figures are
in `2026-07-19.md`.

## Method

For each plugin, concatenate the `description` frontmatter value of every `*.md`
under its `agents/` root and take `len(concat)` (chars) and `len(concat) // 4`
(est. tokens). The **char count is the load-bearing, deterministic figure** the
guardrail should enforce; the token figure is the human-facing estimate.

## Baseline (post-remediation, 2026-07-19)

| Plugin | Agents | Chars (baseline) | Est. tokens | Pre-remediation (F-5) | Reduction |
|---|---:|---:|---:|---:|---:|
| nolte-shared | 23 | **11,451** | ~2,862 | 14,298 (~3,574) | −20% |
| nolte-engineering | 29 | **15,700** | ~3,925 | 21,379 (~5,344) | −27% |
| nolte-media | 2 | **1,108** | ~277 | 1,232 (~308) | −10% |
| **All three** | **54** | **28,259** | **~7,064** | 36,909 (~9,227) | **−23.4%** |

### 2026-07-22 re-baseline (F-18 authoring carve-out)

The F-18 flip (`keep → split`, `2026-07-22-authoring-carve-out-reopen.md`) moved
the agent `claude-plugin-developer` (386 chars) out of `nolte-shared` into the new
fourth plugin `nolte-claude-dev`. This is a **move, not a trim** — the aggregate
across plugins is unchanged. `AGENT_DESC_BASELINE_CHARS` in `validate_skills.py`
is updated accordingly (regression-only gate; a move that lowers a plugin's weight
is not a "raise" and needs no headroom re-derivation):

| Plugin | Agents | Chars (baseline) | Δ vs. 2026-07-19 |
|---|---:|---:|---|
| nolte-shared | 22 | **11,065** | −386 (agent moved out) |
| nolte-claude-dev | 1 | **386** | +386 (agent moved in) |

### 2026-07-24 re-baseline (source-code-review capability, legitimately-added agent)

The holistic source-code-review capability (`spec/project/source-code-review/`)
adds one agent to `nolte-engineering`: `python-code-reviewer` (597 chars,
authored to the F-6 contract shape from the start), and extends
`implementation-plan-author` by its third grounded-input mode (+30 chars,
856 → 886). This is the guardrail's sanctioned **raise** case (a
legitimately-added agent, not creep in the existing surface): the pre-existing
29 descriptions are unchanged at 17,908 chars aggregate — already above the
frozen 15,700 baseline inside its 15% headroom — so the residual slack
(~147 chars) could not fit a contract-shaped description and the plugin
re-baselines at the re-measured value:

| Plugin | Agents | Chars (baseline) | Δ vs. 2026-07-22 |
|---|---:|---:|---|
| nolte-engineering | 30 | **18,535** | +627 (python-code-reviewer +597; implementation-plan-author grounded-input extension +30) |

## Remediation summary

- Every shared agent `description` normalised to the F-6 §Description contract
  shape (what / when-triggers / don't-use cross-references), EN, third person,
  no XML tags, all ≤1024 chars.
- No `user:`/`assistant:`/`<commentary>`/`<example>` blocks were present or
  introduced (F-5 T5); the trim removed **agent-body material** that had leaked
  into descriptions — detail enumerations (what each scanner checks, the FIRST
  properties, anti-pattern catalogues, pillar breakdowns) — never the routing
  signal. Every description keeps its activation trigger (`Invoke …` /
  `dispatched by …`) and its `Don't use …` delimitation cross-references.
- Routing-signal preservation spot-checked on the most-trimmed descriptions
  (observability-audit-scanner, unit-test-reviewer, dockerfile-audit-scanner,
  gdpr-data-protection-reviewer, e2e-test-generator): all retain trigger +
  delimitation. `validate_skills.py` reports 0 Critical.

## Guidance for F-8

- Freeze the **char** baseline per plugin above. Enforce per-plugin
  (`descriptions concat chars // 4` ≤ a ceiling derived from the baseline plus a
  headroom allowance), not a single global number, so one plugin's growth can't
  hide behind another's slack.
- A headroom allowance is needed so a legitimately-added agent doesn't trip the
  gate on day one: the per-plugin average description is ~490 chars
  (28,259 / 54). A ceiling of **baseline + ~15%** (≈ 3–4 average descriptions of
  slack per plugin) is a reasonable starting allowance; F-8 sets the exact value.
