---
review-type: agent-review
target: "agents/license-check-scanner.md"
target-kind: agent
specs-applied:
  - slug: agent-management
    revision: "84aafe7"
  - slug: skill-vs-agent
    revision: "b91b67b"
  - slug: review-plan
    revision: "ea7a5e1"
  - slug: agent-review
    revision: "b91b67b"
repo-revision: "b311e01"
created: "2026-06-05"
status: in-progress
---

# Agent Review: license-check-scanner

## Scope

Target: `agents/license-check-scanner.md` (single self-contained file; no nested sibling folder; no external referenced assets).
Specs applied: `agent-management`, `skill-vs-agent`, `review-plan`, `agent-review` (revisions in frontmatter).
Narrowing: none (full review).
Validator: `scripts/validate_skills.py` (Taskfile `validate:skills`) ran clean for this agent (no errors / warnings) — the `skills-ref` stop-gap for this repo.
Companion: dispatched by the `license-check` skill (reviewed separately in `.audits/skill-review/license-check.md`).
Explicitly out of scope: runtime behavior, Vale/markdown style (`task lint`).

## Summary

- Critical: 1
- Warning: 1
- Suggestion: 0
- Info: 1

Go/no-go: FAIL — one `Critical`: the read-only-Bash narrow exception is claimed but its mandatory condition (forbid writes / package installs / file edits) is violated by the agent's own permitted-operations list.
Next concrete action: re-architect so SBOM generation (the install + write step) lives in the `license-check` skill, and the agent only reads a provided SBOM plus read-only per-component resolution — then the read-only-Bash exception is validly claimed.

## Findings

### Critical

- [x] [agent-management.tool-access-readonly-bash] The read-only-Bash narrow exception is invalidly claimed: §Tool access requires the `## Read-only Bash justification` section to "explicitly forbid anything else (writes, network mutations, package installs, file edits)", but this agent's section instead *permits* `uv venv` + `uv pip install` (package installs into a temporary venv) and writing `sbom.cdx.json` ("The only permitted writes are a temporary venv and the gitignored `sbom.cdx.json`"). A read-only agent that installs packages and writes an SBOM is not side-effect-free, so `Bash` here stays `Critical` rather than downgrading to `Info`.
      Where: `agents/license-check-scanner.md` §"Read-only Bash justification" and §"Working procedure" Phase 2 (the `uv venv` / `uv pip install` / `cyclonedx-py environment` path).
      Fix: move SBOM *generation* (the step that installs and writes) into the `license-check` skill — the skill runs `task license:sbom` (a skill may write) and passes the resulting `sbom.cdx.json` path to the agent; the agent then only *reads* that SBOM plus side-effect-free per-component resolution (`go-licenses report`, `license-checker-rseidelsohn`, `curl` PyPI metadata, `cat`, `find`, `git ls-files`), and its justification section forbids installs and writes outright.
      Verify: the agent's `## Read-only Bash justification` lists only side-effect-free commands and explicitly forbids installs/writes; no `uv venv` / `uv pip install` / `-o sbom.cdx.json` remains in the agent body; the skill owns SBOM generation.

### Warning

- [ ] [skill-vs-agent.duplicate-prevention] Capability adjacency with `dependency-audit-scanner`, whose `description` is also a read-only scanner over the same manifests.
      Where: `agents/license-check-scanner.md` `description` vs. `agents/dependency-audit-scanner.md` `description`.
      Fix: none required — the split is explicit and documented: `dependency-audit-scanner` returns a CVE inventory, `license-check-scanner` returns a license inventory; this agent's `dont_use_when` names `dependency-audit-scanner` for vulnerability scans, and its body forbids running a CVE scan. Confirm the split reads clearly; no merge or rename.
      Verify: both descriptions name disjoint outputs (CVE list vs. license inventory); neither claims the other's surface.

### Info

- [ ] [agent-management.no-skill-dispatch] The body contains the string "Skill tool", but only inside the hard rule "Never call the `Skill` tool or dispatch sibling agents" — a prohibition, not a dispatch. No violation; recorded so a grep-only re-review does not mistake it for a `Skill(` dispatch.
      Where: `agents/license-check-scanner.md` §Hard rules.
      Fix: n/a (observation).
      Verify: n/a.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
2026-06-05 — readonly-bash-exception — moved SBOM generation (install + write) into the license-check skill; agent now reads the skill-provided SBOM and resolves gaps read-only; justification section forbids installs/venv/writes — verified: grep shows no `uv venv` / `uv pip install` / SBOM generation in the agent body except as MUST-NOT prohibitions
