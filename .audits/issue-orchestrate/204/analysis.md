---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "#204"
classification: "spec-change"
secondary-classes: ["infra"]
route: "direct"
status: orchestrated
created: "2026-06-09"
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #204 — Portfolio in-flight triage: work off the 2026-05-23 v2 findings (21 items / 8 repos)
- **URL**: <https://github.com/nolte/claude-shared/issues/204>
- **Labels**: audit
- **Linked items**: none (no linked PRs; `gh pr list --search 204` empty)
- **Prior art checked**: `.audits/portfolio-inflight/2026-05-23-v2.md` (the v2 work-order, `status: open`); `.audits/portfolio-inflight/2026-06-07.md` (newer audit, committed, **supersedes v2**); `agents/portfolio-inflight-collector.md` (current branch pre-filter); `spec/portfolio/portfolio-inflight-management/{en,de}.md`. No roadmap item / feature / open PR addresses this.

## Classification

- **Primary class**: spec-change
- **Secondary class(es)**: infra
- **Rationale**: The one durable in-repo work item — the collector deploy-branch (`gh-pages`) pre-filter — is governed by the `portfolio-inflight-management` spec (§Data sources line 50, §Stalling thresholds line 63 frame branch exclusion as "no open PR to develop AND not the default branch"). The spec is source-of-truth; the collector agent implements it. Hence spec-change primary, infra (portfolio tooling) secondary.

## Scope

- **In scope**:
  1. Extend the `portfolio-inflight-management` spec (EN canonical + DE translation, kept in sync) so the *branch-without-active-PR* data source additionally excludes the `gh-pages` deploy branch, alongside the existing default-branch and open-PR-to-develop exclusions.
  2. Refine `agents/portfolio-inflight-collector.md` to implement that exclusion in the branch-enumeration step.
  3. Close out the tracker: comment on #204 that the 2026-06-07 audit supersedes the v2 work-order, and close it pointing at that report.
- **Out of scope** (with pointers):
  - Working off the 21 v2 findings item-by-item. **Superseded** by `.audits/portfolio-inflight/2026-06-07.md`, which is the current truth and itself instructs to "route remediation through `/nolte-shared:continuous-improvement-triage` and update or close #204". The live remediation targets (kamerplanter PR backlog, dormant Renovate dashboards, real stale feature branches) live in **other** repositories and are tracked by the newer audit, not by this single-repo PR.
  - 2 of the 8 v2 repos (`esphome-configs`, `k8s-home-lab`) have left the portfolio scope entirely (no `project/portfolio.yml`) and are out-of-scope in the 2026-06-07 audit.
  - The default-branch (`main`/`master`) part of the issue's collector improvement is **already implemented** (the collector pre-filters the default branch via `gh api repos/<repo> --jq .default_branch`); only the `gh-pages` deploy-branch case remains.

## Route

- **Decision**: direct
- **Rationale**: One coherent outcome (harden the branch data source against deploy-branch false positives), a single PR strand, no new or retargeted roadmap item. Bounded → direct implementation.
- **Pipeline hand-off**: n/a

## Work packages

### P1 — Spec: exclude the `gh-pages` deploy branch from the branch data source

- **Problem statement**: The spec's branch-without-active-PR data source (§Data sources) and its stalling threshold (§Stalling thresholds) exclude only the default branch and branches with an open PR to `develop`. A `gh-pages` deploy branch is neither, so it surfaces as a perpetual false-positive finding (it has no PR by design and only changes on deploy). The spec must declare the deploy-branch exclusion so the contract — not just the agent — is the source of truth.
- **Acceptance criteria**:
  - `spec/portfolio/portfolio-inflight-management/en.md` §Data sources (branch bullet, ~line 50) and §Stalling thresholds (branch bullet, ~line 63) name `gh-pages` as an excluded deploy branch alongside the default-branch exclusion.
  - `spec/portfolio/portfolio-inflight-management/de.md` carries the strictly-synced translation at the parallel lines.
  - `task test` (frontmatter/skill validation) stays green; spec drift-check reports EN/DE in sync.
- **Touched files / artifacts**: `spec/portfolio/portfolio-inflight-management/en.md`, `spec/portfolio/portfolio-inflight-management/de.md`
- **Specialist**: `nolte-shared:spec` (skill) — resolved by runtime Glob; description: "update or translate an existing one … translations kept strictly in sync."
- **Depends on**: none

### P2 — Collector agent: implement the deploy-branch pre-filter

- **Problem statement**: Implement P1's spec change in `agents/portfolio-inflight-collector.md` so the branch-enumeration step (data source 3) drops `gh-pages` in addition to the default branch and open-PR-to-develop branches, and the exclusion-rules line and example reflect it.
- **Acceptance criteria**:
  - The agent's branch data-source step (around the `gh api repos/<repo>/branches` enumeration) and its §Data-source exclusion-rules line state that `gh-pages` is filtered out as a deploy branch.
  - The change is consistent with P1's spec wording (no agent-vs-spec drift).
  - `task test` stays green.
- **Touched files / artifacts**: `agents/portfolio-inflight-collector.md`
- **Specialist**: `nolte-shared:claude-plugin-developer` (agent) — resolved by runtime Glob; description: "refine an existing one, in strict conformance with every spec under spec/claude/."
- **Depends on**: P1

## Dependency ordering

P1 → P2. (Close-out of #204 happens in the verify phase, after the PR opens.)

## Risks

- **Speculative hardening, zero live findings**: the 2026-06-07 audit currently surfaces no `gh-pages` finding, so this fixes a latent false-positive class rather than an active one. Mitigation: the issue's own acceptance criterion explicitly asks for this ("either implemented or split into its own tracked issue"); implementing it closes that AC. Scope is kept tight to the canonical `gh-pages` name — no speculative configurable deploy-branch list (YAGNI).
- **EN/DE drift**: a spec edit that updates only EN would break the strict-sync invariant. Mitigation: P1 is dispatched to the `spec` skill, which owns translation sync; verify via the spec drift-check.
- **Security-sensitive paths**: none touched (spec prose + a read-only audit agent's enumeration logic). No `code-security-reviewer` / `security-review` requirement.

## Open questions

none — scope confirmed with the operator (route: "Härtung + Close-out").

## Dispatch log

2026-06-09 P1 dispatched to nolte-shared:spec — DONE. Extended §Data sources (line 50) + §Stalling thresholds (line 63) in en.md (canonical) and de.md to exclude the `gh-pages` deploy branch. EN/DE drift check passed (2 gh-pages occurrences each, 16 headings, 94 bullets — in sync).
2026-06-09 P2 dispatched to nolte-shared:claude-plugin-developer — DONE. Updated agents/portfolio-inflight-collector.md at 4 spots (§Read-only Bash justification line 46, §Scope line 60, output-shape example line 145, §Working procedure step 4c line 233) to pre-filter the gh-pages deploy branch. validate_skills.py green (78 artifacts, 0C). No agent-vs-spec drift; primary checkout untouched.
2026-06-09 verify — quality gate green: validate_skills.py 78 artifacts / 0 Critical; Vale `task lint:prose` 0 errors/0 warnings/0 suggestions (182 files); catalog regenerated + committed. No security-sensitive path → no security-review. Draft PR opened: <https://github.com/nolte/claude-shared/pull/295> (Closes #204). Close-out comment posted on #204 (supersession by 2026-06-07 audit). Next action: invoke `pull-request-merge` after CI is green.
