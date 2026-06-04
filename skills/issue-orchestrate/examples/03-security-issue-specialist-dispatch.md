# Example 03 — security-class issue, specialist dispatch with mandatory review

Demonstrates the `security` path: an issue reporting a potential injection in a
bundled script is classified `security` (with the mandatory pre-decomposition
confirmation gate), audited by `code-security-reviewer`, fixed by the dispatched
specialist, and run through the `security-review` skill before the PR opens. The
audit trail names every specialist; the orchestration stops before merge.

## Input prompt

> Issue #298 sieht ernst aus — jemand meldet, dass unser gebündeltes
> `image-generate`-Script einen Dateinamen ungeprüft an die Shell weiterreicht.
> Bitte das sauber analysieren und beheben.

## Input files

Repository state when the skill is invoked:

- `spec/project/issue-orchestration/en.md` — present (canonical).
- Issue #298 `bug`-labelled by the reporter, body describes an unsanitised filename
  flowing into a shell invocation in a bundled script — a command-injection surface.
- The referenced bundled script under `skills/image-generate/` — present.
- At runtime the candidate walk (globbing `${CLAUDE_PLUGIN_ROOT}` plus the project
  roots) discovers `code-security-reviewer` (`description:` names a read-only
  whole-codebase OWASP audit). The diff-scoped `security-review` skill is the Claude
  Code harness built-in — invoked directly as the `security-review` skill, not
  dispatched as a `nolte-shared` agent.
- `gh auth status` — authenticated.

## Expected behaviour

1. **Preconditions pass.** Repo, auth, and spec presence confirmed.
2. **Acquire.** The skill reads the full issue surface and the referenced bundled
   script, and confirms the acquired scope with the operator.
3. **Re-classify `security`.** Although the reporter labelled it `bug`, the substance
   is a command-injection surface → primary class `security`. Per the spec, `security`
   is one of the two classes that **MUST** be operator-confirmed before decomposition;
   the skill surfaces the re-classification and waits for confirmation.
4. **Decompose with a review-first ordering.**
   - `P1` — audit the injection surface and its blast radius; acceptance: a
     `code-security-reviewer` report enumerating every tainted call path; specialist
     `nolte-shared:code-security-reviewer` (read-only).
   - `P2` — sanitise the filename input / switch to an argument-array invocation;
     acceptance: the tainted path is closed and `quality-gate` passes; touches the
     bundled script; specialist resolved by description match for the code fix;
     **depends on** `P1`.
   - `P3` — run `security-review` on the produced diff; acceptance: no remaining
     high/critical finding on the changed lines; **depends on** `P2`.
5. **Write the pre-analysis artifact.** Written to
   `.audits/issue-orchestrate/298/analysis.md` with the DAG `P1 → P2 → P3`, the risk
   note that the path is security-sensitive (so the `code-security-reviewer` /
   `security-review` requirement is mandatory before PR), and presented for operator
   approval before dispatch.
6. **Route `direct`.** One coherent outcome (close the injection), a single PR strand,
   no new roadmap item → bounded → direct.
7. **Dispatch in DAG order.** `P1`: `Agent(subagent_type="nolte-shared:code-security-reviewer")`
   produces the audit; its report is recorded. `P2`: dispatch the code-fix specialist
   resolved at runtime, passing the audit findings; record the result. Each dispatch
   gates on operator confirmation.
8. **Mandatory security verification.** `P3` runs the `security-review` skill on the
   diff (the spec makes this mandatory for a security-sensitive path), in addition to
   `quality-gate` passing green. No PR opens until both are clean.
9. **Open the PR with the full audit trail.** `pull-request-create` with `Closes #298`
   and **Risk / rollout notes**:
   - `Issue: #298 — classification: security`
   - `P1 dispatched specialist: nolte-shared:code-security-reviewer`
   - `P2 dispatched specialist: <runtime-resolved code-fix specialist>`
   - `P3 verification: security-review (built-in skill) — no remaining high/critical finding`
   The operator confirms title and body before push.
10. **Stop before merge.** The skill reports the issue number, classification
    (`security`), route (`direct`), the dispatched specialists, the artifact path, the
    PR URL, and the next-action hint "invoke `pull-request-merge` after CI is green".
    It does **not** merge and never passes `--admin`.
