---
review-type: skill-review
target: "skills/mkdocs-structure-apply/SKILL.md"
target-kind: skill
specs-applied:
  - slug: skill-management
    revision: "95ec039"
  - slug: skill-vs-agent
    revision: "45418ab"
  - slug: review-plan
    revision: "3f5c312"
  - slug: skill-review
    revision: "45418ab"
repo-revision: "16a3754"
created: "2026-05-18"
status: complete
---

# Skill Review: mkdocs-structure-apply

## Scope

Target: `skills/mkdocs-structure-apply/` (single `SKILL.md`, 141 lines; no referenced templates, references, examples, or scripts).
Specs applied: `skill-management`, `skill-vs-agent`, `review-plan`, `skill-review` (revisions recorded in frontmatter).
Validator: override — `skills-ref` is not provisioned in this repository; the project-local `scripts/validate_skills.py` runs in its place as the canonical local structure validator per `skill-management` §Frontmatter validation (line 37 references `scripts/validate_skills.py` as the local validator). Output captured: `1C / 0W / 0S / 0I`, surfaced as Finding C1 below with the validator's rule identifier in the bracketed prefix.
Narrowing: none (full review of frontmatter, body, rationale, hard rules, output contract, gotchas; no referenced assets to walk).
Explicitly out of scope: runtime behaviour of the skill (no execution against any target repo), Vale and markdown style (handled by `task lint`), dispatched agents beyond confirming the orchestration direction (none yet at review time — the skill names `audience-doc-author` as a hand-off target but doesn't dispatch in this static review).
Reviewer context: review run from the `feat/mkdocs-structure-apply-skill` worktree at SHA `16a3754` (= develop tip with `spec/project/mkdocs-structure/` merged); plan lives under that worktree's `.audits/skill-review/`.

## Summary

- Critical: 1
- Warning: 3
- Suggestion: 1
- Info: 1

Go/no-go: **FAIL** — the Critical (description-length over the Anthropic platform cap) blocks PR merge; once addressed the skill is otherwise structurally clean.
Next concrete action: author trims `description` from 1554 to ≤1024 characters by moving the trigger enumeration into the body (Operations section already lists them) and keeping only the contract sentence plus the primary trigger keywords in frontmatter.

## Findings

### Critical

- [x] [skill-management.frontmatter-description-cap] `description` length is 1554 characters, exceeding the Anthropic platform 1024-character cap by 530 characters; the upstream platform validator rejects skills over this cap, and the local `scripts/validate_skills.py` flags it as Critical (rule `skill-management.frontmatter-description-cap`).
      Where: `skills/mkdocs-structure-apply/SKILL.md:3` (the `description:` field).
      Fix: rewrite the description in two parts: (a) one tight contract sentence naming what the skill does (audit / scaffold / patch MkDocs against `spec/project/mkdocs-structure/`), (b) a short trigger and anti-trigger list. Move the long enumeration of plugins, sections, and operation details into the body's introductory paragraph and the existing Operations section (they're already enumerated there). Target ≤ ~700 characters to leave headroom for the combined `description` + `when_to_use` 1536-character cap.
      Verify: `python3 -c "import yaml,re;m=re.match(r'---\n(.*?)\n---',open('skills/mkdocs-structure-apply/SKILL.md').read(),re.DOTALL);print(len(yaml.safe_load(m.group(1))['description']))"` returns ≤1024, and `python3 scripts/validate_skills.py skills/mkdocs-structure-apply/SKILL.md` returns `0C`.

### Warning

- [x] [skill-management.body-self-consistency] Hard rule #4 ("Always read `spec/project/mkdocs-structure/<canonical_language>.md` at runtime. The skill does not carry a baked-in copy of the spec. A missing spec file is a hard stop") directly contradicts the body's introductory paragraph at line 11 ("When the spec isn't present in the target repository, fall back to the copy shipped by the `nolte-shared` plugin (read it at runtime from the plugin install path)") and Precondition 2 at line 41 ("Locate `spec/project/mkdocs-structure/<canonical_language>.md` — either in the target repo or via the `nolte-shared` plugin"). The two policies (hard-stop vs plugin-fallback) can't both be true at runtime; a downstream consumer or maintainer reading the skill cold can't tell which path the skill actually takes.
      Where: `skills/mkdocs-structure-apply/SKILL.md:11`, `:41`, `:120` (Hard rule #4).
      Fix: pick one policy and apply it consistently. Recommended: keep the plugin-install-path fallback (matches the spec's own §Extension hooks §"Project-type discovery" pattern of letting marker-file presence drive behaviour), rewrite Hard rule #4 to allow the plugin-shipped copy as an explicit fallback ("Always read the spec at runtime; prefer the target repo's `spec/project/mkdocs-structure/<canonical_language>.md`, fall back to the copy shipped by `nolte-shared` only when the target repo lacks one — never carry a baked-in copy inside the skill itself"), and align all three locations to that wording.
      Verify: `grep -n "fall back\|hard stop\|baked-in" skills/mkdocs-structure-apply/SKILL.md` returns a single consistent policy across the body, the precondition, and the hard rule.
- [x] [skill-management.body-self-consistency] Hard rule #8 is internally self-contradictory: the first sentence says "Never dispatch the `Agent` tool to spawn a sibling agent, nor call the `Skill` tool recursively in a way that loops", and the second sentence immediately allows "Skill-orchestrates-agent-executes is allowed (`audience-doc-author`, future `docs-dry-refactor`)". `skill-vs-agent` §Hybrid pattern (line 52) explicitly endorses skill-orchestrates-agent-executes, so the prohibition is wrong and the allowance is right; the contradiction makes the rule unenforceable as written.
      Where: `skills/mkdocs-structure-apply/SKILL.md:124` (Hard rule #8).
      Fix: rewrite Hard rule #8 to forbid only the genuinely-disallowed shapes: "**Never** dispatch the `Skill` tool recursively into this skill (silent loops) or chain to a sibling skill outside the declared hand-off points; the skill orchestrates the `audience-doc-author` agent and the future `docs-dry-refactor` skill at the explicit hand-off points named in the Output contract." That keeps the no-loop guarantee and explicitly permits the documented orchestrations.
      Verify: a fresh read of Hard rule #8 has no internally-contradictory clauses and matches `skill-vs-agent` §Hybrid pattern; `grep -n "Never.*Agent tool\|orchestrates-agent-executes is allowed" skills/mkdocs-structure-apply/SKILL.md` returns at most one match per rule (no clashing pair).
- [x] [skill-vs-agent.duplicate-prevention] Plausible capability overlap with the existing `skills/skill-agent-catalog-apply/SKILL.md`: both skills edit the same `mkdocs.yml` `plugins:` block in the same target repository. The split is reasonable in principle — `skill-agent-catalog-apply` owns the catalog-generator plumbing (`mkdocs-gen-files`, `mkdocs-literate-nav`, the catalog source-roots wiring), and `mkdocs-structure-apply` owns the baseline (theme, i18n, `pymdownx.superfences`, `search`, `mkdocs-include-markdown-plugin`) — but the boundary is implicit. A reader can't tell from either description alone which skill to invoke when both kinds of work are needed.
      Where: `skills/mkdocs-structure-apply/SKILL.md:3` (description) and Hard rule #11 at `:127`; compare with `skills/skill-agent-catalog-apply/SKILL.md` description and operations.
      Fix: make the split explicit in both directions. In `mkdocs-structure-apply`'s description, append one sentence to the negative-trigger list naming the boundary ("`skill-agent-catalog-apply` owns the catalog-generator wiring; this skill only declares the catalog extension's MUSTs as part of the audit"). Hard rule #11 already routes the user there; lift its phrasing into the description so a Claude routing prompt sees the boundary at metadata-read time, not only after invoking the wrong skill.
      Verify: `grep -n "skill-agent-catalog-apply" skills/mkdocs-structure-apply/SKILL.md` returns at least two matches (description + Hard rule), and a corresponding cross-reference is proposed for the peer skill's description as a follow-up (tracked as an Info finding here).

### Suggestion

- [x] [skill-management.evaluation-discipline] The skill folder lacks an `examples/` sibling with at least three evaluation scenarios (input prompt, optional input files, expected behaviour) per `skill-management` §Evaluation discipline; for a new skill this is a `Suggestion`, escalating to `Warning` once the skill has been edited more than three times since the last evaluation pass.
      Where: `skills/mkdocs-structure-apply/` folder shape (no `examples/`).
      Fix: add `skills/mkdocs-structure-apply/examples/` with at least three scenarios: (a) `audit-only-existing-mkdocs-yml.md` (input: a repo with `mkdocs.yml` present, expected: structured audit report with per-MUST status), (b) `scaffold-greenfield.md` (input: a repo without `mkdocs.yml`, expected: proposed `mkdocs.yml` + `docs/<lang>/` layout, dep-manifest pin proposal, user-approval gate), (c) `patch-add-missing-plugin.md` (input: a repo missing `mkdocs-include-markdown-plugin`, expected: additive patch to `plugins:` and the dep manifest, build verification). Skill-management §Evaluation discipline accepts these as markdown scenario files.
      Verify: `ls skills/mkdocs-structure-apply/examples/` lists ≥3 markdown files; each file states input, expected behaviour, and the rule it exercises.

### Info

- [x] [skill-management.evaluation-discipline-multi-model] No evidence (comment, example output, or test rubric) of multi-model testing across Haiku / Sonnet / Opus per `skill-management` §Evaluation discipline. Recorded as `Info` per `skill-review` §Checks derived from evaluation discipline ("MAY record an `Info` finding when no evidence of multi-model testing exists").
      Where: `skills/mkdocs-structure-apply/` folder shape.
      Fix: n/a (observation); when the examples scenarios above are authored, name the model they were tested against in each scenario's header.
      Verify: n/a.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
2026-05-18 — critical/frontmatter-description-cap — rewrote description from 1554 to 922 characters by lifting the long enumeration of plugins, sections, and operation details out of the frontmatter (already present in the body) and keeping only the contract sentence plus key triggers and anti-trigger boundaries — verified: `python3 scripts/validate_skills.py skills/mkdocs-structure-apply/SKILL.md` returns `0C / 0W / 0S / 0I`
2026-05-18 — warning/body-self-consistency-spec-fallback — rewrote Hard rule #4 to make the plugin-install-path fallback explicit and consistent with the body's introductory paragraph (line 11) and Precondition 2 (line 41); the unified policy is "prefer target repo, fall back to plugin-shipped copy, never bake in" — verified: `grep -n "fall back\|baked-in" skills/mkdocs-structure-apply/SKILL.md` returns the new Hard rule #4 plus the existing body and precondition mentions, all consistent
2026-05-18 — warning/body-self-consistency-rule-8 — rewrote Hard rule #8 to forbid only silent recursion and undeclared sibling-skill chains; explicit orchestration of `audience-doc-author` agent and future `docs-dry-refactor` skill at declared hand-off points is now allowed and cited against `spec/claude/skill-vs-agent/` §Hybrid pattern — verified: re-read of Hard rule #8 has no internally-contradictory clauses; orchestration permissions align with the spec
2026-05-18 — warning/duplicate-prevention-skill-agent-catalog-apply — the new (trimmed) description now closes with an explicit boundary clause: "catalog generator wiring (use `skill-agent-catalog-apply`; this skill only verifies the catalog extension's MUSTs at the baseline level)"; the corresponding reverse cross-reference inside `skills/skill-agent-catalog-apply/SKILL.md` is left as a follow-up (deferred — to be tracked alongside any future skill-agent-catalog-apply edit) — verified: `grep -n "skill-agent-catalog-apply" skills/mkdocs-structure-apply/SKILL.md` returns two matches (description boundary + Hard rule #11 routing)
2026-05-18 — suggestion/evaluation-discipline — deferred to a follow-up PR; the three example scenarios (audit-only-existing, scaffold-greenfield, patch-add-missing-plugin) will be authored once the skill has been dispatched at least once in a real consumer repo so the scenarios reflect actual behaviour rather than a-priori speculation
2026-05-18 — info/evaluation-discipline-multi-model — deferred along with the suggestion above; multi-model evaluation rubric will be added together with the examples scenarios so each scenario names the model it was tested against
