# Example 02 — Three-recurrence finding, gap-closure action initiated

Demonstrates the `update` operation when a finding class hits the three-recurrence threshold and no matching specialist exists. The skill surfaces the portfolio gap, asks the user whether to author a new specialist before the fix PR, and records the gap-closure decision in the triage artifact with the required justification.

## Input prompt

> Ich habe gerade im Triage-Artifact gesehen, dass `prose-style`-Lint-Fehler jetzt dreimal generalistisch behandelt wurden. Bitte dispatchen oder Spezialist anlegen — was empfiehlst du?

## Input files

Repository state when the skill is invoked:

- Open triage artifact at `.audits/continuous-improvement/2026-Q2.md` with `status: open`, containing:
  - **F3 — prose-style lint gap**: 3 generalist-handled occurrences (PRs #104, #109, #116), recurrence count at threshold, decision still `pending`.
- `agents/` directory at runtime:
  - `agents/claude-plugin-developer.md` — "spec-conformant authoring of Claude Code skills, agents, and plugin manifests".
  - `agents/audience-doc-author.md` — "audience-aware MkDocs documentation prose; applies Vale style checks and prose-quality guidelines".
- No agent with a description matching "prose-style lint", "markdown formatting lint", or "Vale lint failure remediation" directly, but `audience-doc-author`'s description mentions "Vale style checks"—a near-neighbour match.
- The same `prose-style` failure class has been observed in one other portfolio repository (`nolte/project-alpha`), making this a cross-repository finding class.

## Expected behaviour

1. **Confirm the open artifact.** The skill reads `.audits/continuous-improvement/2026-Q2.md`, confirms `status: open`, and locates finding F3 with decision `pending`.

2. **Present F3 to the user.** In German: "F3 (prose-style Lint) wurde dreimal generalistisch behandelt — der Threshold ist erreicht. Im Agent-Inventar gibt es `audience-doc-author`, dessen Beschreibung Vale-Style-Checks erwähnt — ein naher Nachbar, aber kein direkter Match auf `prose-style`-Lint-Behebung. Außerdem wurde dieselbe Klasse in `nolte/project-alpha` beobachtet, was Plugin-Distribution für jeden neuen Spezialisten vorschreibt."

3. **Offer the three decisions.** Present clearly:
   - A: Extend `audience-doc-author`'s `description` to cover prose-style lint remediation (preferred per spec — near-neighbour extension before authoring a new specialist).
   - B: Author a new specialist skill `prose-style-fix` via `claude-plugin-developer` with `distribution: plugin` (required because the class appears in two repositories).
   - C: Defer with explicit reason and owner.

4. **User chooses A** (extend `audience-doc-author`). The skill records this as a gap-closure decision and dispatches `Agent(subagent_type="nolte-claude-dev:claude-plugin-developer")` with the brief: "Extend the `description` of `agents/audience-doc-author.md` to explicitly name prose-style markdown lint failure remediation and Vale lint fix authoring as responsibilities; the current description mentions Vale style checks but not fixing lint failures."

5. **Wait for agent report.** `claude-plugin-developer` updates `agents/audience-doc-author.md` and proposes a PR. The skill records the fix PR number.

6. **Record D3 in `## Decisions`.** Append to the triage artifact:
   - Finding: F3
   - Action: gap-closure — extended `audience-doc-author` description
   - Cross-repository note: finding class observed in `nolte/project-alpha`; plugin distribution confirmed (agent already lives in the plugin)
   - Fix PR: `#<number>`
   - The fix PR's **Risk / rollout notes** must carry:
     - Originating source: prose-style lint findings from PRs #104, #109, #116.
     - Dispatched specialist: gap-closure initiated—`audience-doc-author` description extended; prior occurrences read "no matching specialist existed — generalist handled".

7. **No pre-threshold early-creation path taken.** The decision was made at the threshold, not before it; no special high-impact justification is required. (Had the user chosen to act after only one occurrence, the justification field in the authoring PR would be mandatory.)

8. **Cross-repository promotion confirmed.** Because `audience-doc-author` is already a plugin-distributed agent in `nolte-shared`, the extension satisfies the cross-repository distribution requirement automatically; no separate promotion step is needed.

9. **Report back.** Decision D3 recorded. F3 status updated to `gap-closure initiated`. Triage artifact updated. Recommend running `update` again for any remaining pending findings before closing the cycle.
