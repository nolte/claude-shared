---
artifact-type: plugin-boundary-decision
feature: F-18
roadmap_item: R-11
issue: 416
created: "2026-07-20"
decision: keep-and-watch
bound-by: spec/claude/plugin-scoping/
---

# Authoring-slice plugin carve-out decision (F-18)

**Verdict: keep — do not carve the authoring slice into a fourth plugin now.**
Re-evaluate on a stated trigger (below). The carve-out is a *legitimate*
consumer-audience split, not rejected on principle; it is not worth its standing
cost *at present*.

## The question

Should the plugin/skill-authoring slice — the skills `skill-management`,
`skill-review`, `agent-review`, `skills-agents-sweep`, `skill-agent-catalog-apply`
and the agent `claude-plugin-developer` — be extracted into its own plugin so the
majority of consumers, who install `nolte-shared` for the delivery lifecycle and
**never author a plugin or skill**, stop loading it?

F-5 settled this **for the agent-description budget** (`.audits/shared-plugin-analysis/2026-07-19.md`
§3): the slice is five skills plus one ~122-token agent, so a split removes only
~1.3 % of the agent-routing budget — the axis R-9 already guardrailed. F-5
explicitly re-opened the question on the **skill** axis. This is that decision.

## Measurement (skill-description axis)

Method: char count (and the 4-char/token estimate) of the `description`
frontmatter of each authoring-slice skill, versus the aggregate over all 45
`nolte-shared` skills. Skill descriptions load into the consumer's skill list on
every turn, the same way agent descriptions load into the routing budget.

| Authoring-slice skill | Description chars |
|---|---:|
| skill-agent-catalog-apply | 1,012 |
| skills-agents-sweep | 867 |
| skill-management | 851 |
| skill-review | 735 |
| agent-review | 732 |
| **Slice total (5 skills)** | **4,197 (~1,049 est. tokens)** |
| nolte-shared skill-description budget (45 skills) | 40,182 (~10,045 est. tokens) |
| **Slice share** | **10.4 %** |

(The agent `claude-plugin-developer`, ~386 chars, sits in the agent budget F-5
already assessed; the `cookiecutter-template-*` template-authoring pair, ~1,395
chars, is an adjacency a future split could include but is not core to the slice.)

**Finding:** on the skill axis the carve-out is **materially larger** than on the
agent axis — 10.4 % vs. 1.3 %. So the "it barely moves the budget" argument that
decided F-5 does **not** transfer; this axis has to be weighed on its own.

## Weighing the split against its cost

Bound by `spec/claude/plugin-scoping/`: a split is justified only by a
runtime/dependency or **consumer-audience** difference, never topic/count. The
authoring slice is a genuine consumer-audience category (most consumers never
author), so a split would be *rule-legitimate* — the same basis on which
`nolte-engineering` splits from `nolte-shared`.

**For a split:** ~1,049 est. tokens (10.4 %) of skill-list weight removed for every
non-authoring consumer; a clean audience boundary; a coherent, self-contained
slice.

**Against a split, decisive at present:**

1. **No acute skill-budget problem exists.** R-9 was driven by a real, observed
   failure — Claude Code's ~15k **agent-description** routing-budget warning tripping
   in `kamerplanter` (#371). There is no documented equivalent hard limit or observed
   warning for the **skill** list; ~1,049 tokens is a nice-to-have reduction, not the
   relief of an acute ceiling. Splitting to pre-empt a limit that has not appeared is
   speculative.
2. **A fourth plugin carries a permanent, per-release cost.** All plugins version in
   lockstep (CLAUDE.md), and the extra plugin's version bump is a **manual** step
   today (marketplace `plugins[].version` is deliberately absent; see
   `project_plugin_monorepo`). Every release would carry that added alignment surface
   forever, against a non-urgent one-time saving.
3. **The slice is not audience-exclusive in practice.** An occasional consumer that
   runs a single `skill-review` or `agent-review` still wants those skills present;
   carving them out makes an ad-hoc review a plugin-install decision.

The standing fourth-plugin cost is recurring and certain; the skill-budget saving is
real but not urgent. Net: **keep now.**

## Trigger for revision

Re-open this decision — and, if it flips, spawn a follow-on execution feature under
R-11 or a successor — when **either** holds:

- a **skill-list budget limit or warning** appears (a documented cap, or an observed
  Claude Code warning on the skill surface analogous to the ~15k agent warning); or
- the authoring slice **grows materially** (new authoring skills push the slice
  meaningfully past its current ~10 %), tilting the saving over the fourth-plugin cost.

Until then the question is **closed as keep**, with the measurement above as the
baseline a future re-evaluation compares against.

## Related sweep signal (PB-2)

The 2026-07-20 skills/agents sweep flagged two review agents —
`gdpr-data-protection-reviewer` and `quality-gate-enforcer` — living in
`nolte-shared/agents/` while their capability family (`code-security-reviewer`,
`dependency-audit`, the `quality-gate` skill) lives in `nolte-engineering`. That is a
**separate, smaller placement question** on the existing three-plugin boundary (does a
code-audience agent belong in the code-audience plugin?), independent of the authoring
carve-out. It is not resolved here; noted so a future boundary pass picks it up.
