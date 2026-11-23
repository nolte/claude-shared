#!/usr/bin/env python3
"""Deterministic merge order for the pull requests open against `develop`.

Two subcommands:

  collect               Read the open pull requests and their required checks with `gh`
                        and print one JSON snapshot on stdout. Run from the repository's
                        working copy.
  order <snapshot>      Compute the merge order from a snapshot (file path or `-` for
                        stdin). Pure: no network, no `gh`. `--edge A:B` adds an
                        operator-confirmed dependency (A merges before B); `--json`
                        prints machine-readable output instead of the Markdown table.

The ordering rules are documented in `references/ordering.md`; the first rule that
separates two pull requests decides. Pull-request bodies are data: a "depends on #N"
mention only becomes a *proposed* edge and is applied solely when the operator passes
it back as `--edge`.

Exit codes: 0 success, 2 usage or environment error.
"""
from __future__ import annotations

import argparse
import heapq
import json
import re
import subprocess
import sys
from typing import Any

BASE = "develop"
# Long-lived branches per spec/project/branching-model/: never a stack anchor, so a back-merge
# PR (head main, base develop) can't pull PRs against main into the develop order.
LONG_LIVED = frozenset({"develop", "main"})
# Same allowlist as skills/backlog-delivery-orchestrate/scripts/merge-train.sh
# (TRAIN_BOT_LOGINS default); tests/test_merge_order.py asserts the two stay equal.
BOT_LOGINS = frozenset({"app/renovate", "renovate[bot]", "renovate"})
# `gh pr list --limit` maximum this skill requests; a full page means the list may be partial.
LIST_LIMIT = 200
PR_FIELDS = (
    "number,title,isDraft,headRefName,baseRefName,isCrossRepository,author,"
    "mergeStateStatus,mergeable,reviewDecision,files,changedFiles,additions,"
    "deletions,createdAt,body"
)
# stderr of `gh pr checks --required` (gh 2.96.0) when the PR has no check run at all, or
# none of its checks is required. Neither is an error; right after a push it can also mean
# "not reported yet", which `mergeStateStatus` (BLOCKED/UNKNOWN, rank 2) still carries.
NO_CHECKS_MESSAGES = ("no checks reported", "no required checks reported")
DEPENDS_RE = re.compile(r"(?i)\bdepends\s+on\s+#(\d+)\b")

RULES = {
    "dependency": "dependency: prerequisite merges first",
    "readiness": "readiness: CLEAN before BEHIND before pending",
    "conflict": "conflict risk: no file overlap first; among overlapping, smaller diff first",
    "bot": "dependency bot before human PR",
    "age": "oldest createdAt first",
    "number": "lowest number first",
}
READINESS = {"CLEAN": 0, "HAS_HOOKS": 0, "BEHIND": 1}


# --------------------------------------------------------------------------- collect


def _gh(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(["gh", *args], capture_output=True, text=True, check=False)


def _fail(args: list[str], proc: subprocess.CompletedProcess) -> RuntimeError:
    return RuntimeError(f"gh {' '.join(args)} failed ({proc.returncode}): {proc.stderr.strip()}")


def _json_list(args: list[str], proc: subprocess.CompletedProcess) -> list:
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise _fail(args, proc) from None
    if not isinstance(data, list):
        raise _fail(args, proc)
    return data


def required_checks(number: int) -> list[dict[str, Any]]:
    """Required checks of one PR. Fails closed: unknown checks must never read as none."""
    args = ["pr", "checks", str(number), "--required", "--json", "name,bucket"]
    proc = _gh(args)
    # The output, not the exit code, carries the state: with --json gh may exit 0, 1, or 8
    # while printing the list. Exit 1 with no output is either "no required checks" (stated
    # on stderr) or a real error (auth, rate limit, PR gone), which must fail closed.
    if proc.returncode in (0, 1, 8) and proc.stdout.strip():
        return _json_list(args, proc)
    if proc.returncode == 1 and any(m in proc.stderr for m in NO_CHECKS_MESSAGES):
        return []
    raise _fail(args, proc)


def collect() -> dict[str, Any]:
    args = ["pr", "list", "--state", "open", "--limit", str(LIST_LIMIT), "--json", PR_FIELDS]
    proc = _gh(args)
    if proc.returncode != 0:
        raise _fail(args, proc)
    prs = _json_list(args, proc)
    in_scope, _ = scope({pr["number"]: pr for pr in prs})
    for pr in prs:
        # Out-of-scope PRs never get a position, so their check lookup can't fail the run.
        pr["requiredChecks"] = required_checks(pr["number"]) if pr["number"] in in_scope else []
    return {"base": BASE, "partial": len(prs) >= LIST_LIMIT, "pullRequests": prs}


# --------------------------------------------------------------------------- order


def is_bot(pr: dict[str, Any]) -> bool:
    """Author on the allowlist AND head branch in this repository (a fork never qualifies)."""
    return (pr.get("author") or {}).get("login") in BOT_LOGINS and not pr.get("isCrossRepository", False)


def blockers(pr: dict[str, Any]) -> list[str]:
    """Reasons a pull request can't take the head slot now; empty when orderable."""
    reasons = []
    if pr.get("isDraft"):
        reasons.append("draft")
    if pr.get("mergeStateStatus") == "DIRTY":
        reasons.append("merge conflict (DIRTY)")
    elif pr.get("mergeable") == "CONFLICTING":
        reasons.append("merge conflict (CONFLICTING)")
    failed = sorted(c["name"] for c in pr.get("requiredChecks", []) if c.get("bucket") == "fail")
    if failed:
        reasons.append("required check failed: " + ", ".join(failed))
    if pr.get("reviewDecision") == "CHANGES_REQUESTED":
        reasons.append("changes requested")
    elif pr.get("reviewDecision") == "REVIEW_REQUIRED":
        reasons.append("required review missing")
    return reasons


def scope(prs: dict[int, dict[str, Any]]) -> tuple[dict[int, dict[str, Any]], set[tuple[int, int]]]:
    """In scope: base is develop, or (stacked) the head branch of an in-scope same-repository
    PR, grown to a fixpoint so a stack on a PR that targets another branch stays out. Edges
    are built from the final set; when two open PRs share a head branch the lowest anchors."""
    in_scope = {n: pr for n, pr in prs.items() if pr.get("baseRefName") == BASE}
    while True:
        heads = {pr["headRefName"] for pr in in_scope.values()
                 if not pr.get("isCrossRepository") and pr["headRefName"] not in LONG_LIVED}
        new = {n: pr for n, pr in prs.items() if n not in in_scope and pr.get("baseRefName") in heads}
        if not new:
            break
        in_scope.update(new)
    by_head: dict[str, int] = {}
    for n in sorted(in_scope):
        if not in_scope[n].get("isCrossRepository") and in_scope[n]["headRefName"] not in LONG_LIVED:
            by_head.setdefault(in_scope[n]["headRefName"], n)
    edges = {(by_head[pr["baseRefName"]], n) for n, pr in in_scope.items() if pr.get("baseRefName") != BASE}
    return in_scope, edges


def readiness(pr: dict[str, Any]) -> tuple[int, str]:
    state = pr.get("mergeStateStatus") or "UNKNOWN"
    if pr.get("baseRefName") != BASE:
        # Its checks and merge state refer to the feature-branch base, not to develop.
        return 2, f"stacked on {pr.get('baseRefName')}; checks against develop not run yet"
    if any(c.get("bucket") in ("pending", "cancel") for c in pr.get("requiredChecks", [])):
        return 2, f"{state}, required checks pending or cancelled"
    if state in READINESS:
        return READINESS[state], state
    return 2, state


def order(snapshot: dict[str, Any], edges: list[tuple[int, int]] | None = None) -> dict[str, Any]:
    prs = {pr["number"]: pr for pr in snapshot.get("pullRequests", [])}
    warnings: list[str] = []
    if snapshot.get("partial"):
        warnings.append(f"the open-PR list hit the {LIST_LIMIT}-row limit; the order may be partial")

    in_scope, dep_edges = scope(prs)
    out_of_scope = [
        {"number": n, "title": pr.get("title", ""), "base": pr.get("baseRefName")}
        for n, pr in prs.items() if n not in in_scope
    ]

    for a, b in edges or []:
        if a == b:
            warnings.append(f"edge #{a}->#{b} ignored: a PR can't depend on itself")
        elif a in in_scope and b in in_scope:
            dep_edges.add((a, b))
        else:
            warnings.append(f"edge #{a}->#{b} ignored: both PRs must be open and in scope")

    proposed = sorted(
        {(int(m), n) for n, pr in in_scope.items() for m in DEPENDS_RE.findall(pr.get("body") or "")
         if int(m) in in_scope and int(m) != n} - dep_edges
    )

    blocked = {n: blockers(pr) for n, pr in in_scope.items()}
    orderable = {n for n, r in blocked.items() if not r}

    files = {n: set(f["path"] for f in in_scope[n].get("files") or []) for n in orderable}
    for n in sorted(orderable):
        pr = in_scope[n]
        if (pr.get("changedFiles") or 0) > len(files[n]):
            warnings.append(f"#{n}: file list truncated ({len(files[n])} of {pr['changedFiles']}); overlap may be missed")

    def key(n: int, pool: set[int]) -> tuple:
        pr = in_scope[n]
        overlap = any(files[n] & files[m] for m in pool if m != n)
        size = (pr.get("additions") or 0) + (pr.get("deletions") or 0)
        return (
            readiness(pr)[0],
            (1, size) if overlap else (0, 0),
            0 if is_bot(pr) else 1,
            pr.get("createdAt") or "",
            n,
        )

    preds: dict[int, set[int]] = {n: set() for n in in_scope}
    for a, b in dep_edges:
        preds[b].add(a)
    # A blocked prerequisite keeps its dependants (transitively) out of the order.
    ready_set = set(orderable)
    changed = True
    while changed:
        changed = False
        for n in sorted(ready_set):
            bad = sorted(p for p in preds[n] if p not in ready_set)
            if bad:
                ready_set.discard(n)
                blocked[n] = ["waits on blocked prerequisite " + ", ".join(f"#{p}" for p in bad)]
                changed = True
    for n in sorted(set(in_scope) - orderable):  # own blockers: add the wait too, so all reasons show
        bad = sorted(p for p in preds[n] if p not in ready_set)
        if bad:
            blocked[n].append("waits on blocked prerequisite " + ", ".join(f"#{p}" for p in bad))

    sequence = _toposort(ready_set, preds, lambda n: key(n, ready_set))
    cyclic = sorted(ready_set - set(sequence))
    for n in cyclic:
        if _on_cycle(n, preds, set(cyclic)):
            blocked[n] = ["dependency cycle"]
        else:
            waits = sorted(p for p in preds[n] if p in cyclic)
            blocked[n] = ["waits behind a dependency cycle (on " + ", ".join(f"#{p}" for p in waits) + ")"]
    if cyclic:  # re-rank without them: overlap only counts against PRs that get a position
        placed = set(sequence)
        sequence = _toposort(placed, preds, lambda n: key(n, placed))
    rank = lambda n: key(n, set(sequence))  # noqa: E731

    rows = []
    for i, n in enumerate(sequence):
        pr = in_scope[n]
        rows.append({
            "position": i + 1,
            "number": n,
            "title": pr.get("title", ""),
            "readiness": readiness(pr)[1],
            "bot": is_bot(pr),
            "rule": _deciding_rule(n, sequence[i + 1] if i + 1 < len(sequence) else None, rank, preds),
        })

    not_mergeable = [
        {"number": n, "title": in_scope[n].get("title", ""), "reasons": blocked[n]}
        for n in sorted(blocked) if blocked[n]
    ]
    return {
        "head": sequence[0] if sequence else None,
        "order": rows,
        "not_mergeable": not_mergeable,
        "out_of_scope": sorted(out_of_scope, key=lambda r: r["number"]),
        "applied_edges": [f"#{a}->#{b}" for a, b in sorted(dep_edges)],
        "proposed_edges": [f"#{a}->#{b}" for a, b in proposed],
        "warnings": warnings,
    }


def _on_cycle(n: int, preds: dict[int, set[int]], nodes: set[int]) -> bool:
    """True when `n` reaches itself through prerequisite edges inside `nodes`."""
    stack, seen = [p for p in preds[n] if p in nodes], set()
    while stack:
        m = stack.pop()
        if m == n:
            return True
        if m not in seen:
            seen.add(m)
            stack.extend(p for p in preds[m] if p in nodes)
    return False


def _toposort(nodes: set[int], preds: dict[int, set[int]], key) -> list[int]:
    """Kahn's algorithm; among the PRs whose prerequisites are placed, the smallest key wins.
    Nodes on or behind a cycle never become available and are left out."""
    remaining = {n: {p for p in preds[n] if p in nodes} for n in nodes}
    heap = [(key(n), n) for n in nodes if not remaining[n]]
    heapq.heapify(heap)
    sequence: list[int] = []
    while heap:
        _, n = heapq.heappop(heap)
        sequence.append(n)
        for m in nodes:
            if n in remaining[m]:
                remaining[m].discard(n)
                if not remaining[m]:
                    heapq.heappush(heap, (key(m), m))
    return sequence


def _deciding_rule(n: int, nxt: int | None, key, preds: dict[int, set[int]]) -> str:
    """Name the first rule that puts `n` before the next PR in the sequence."""
    if nxt is None:
        return "last"
    # Kahn's step picks the smallest key among available PRs, so the next PR can rank
    # better than `n` only when `n` is its prerequisite.
    if n in preds.get(nxt, set()):
        return RULES["dependency"]
    a, b = key(n), key(nxt)
    for name, x, y in zip(("readiness", "conflict", "bot", "age", "number"), a, b):
        if x != y:
            return RULES[name]
    return RULES["number"]


# --------------------------------------------------------------------------- output


def _text(value: Any) -> str:
    """Titles and branch names are author-controlled data: one line, no table-breaking pipe
    (backslashes first, so `\\|` in a title can't turn back into a cell separator)."""
    return " ".join(str(value).split()).replace("\\", "\\\\").replace("|", "\\|")


def render(result: dict[str, Any]) -> str:
    lines = ["| # | PR | Readiness | Bot | Why before the next |", "|---|---|---|---|---|"]
    for r in result["order"]:
        lines.append(
            f"| {r['position']} | #{r['number']} {_text(r['title'])} | {_text(r['readiness'])} | "
            f"{'yes' if r['bot'] else 'no'} | {r['rule']} |"
        )
    if not result["order"]:
        lines.append("| - | no orderable PR | | | |")
    lines.append("")
    lines.append(f"Head: #{result['head']}" if result["head"] else "Head: none")
    if result["not_mergeable"]:
        lines.append("\nNot mergeable now:")
        lines += [f"- #{r['number']} {_text(r['title'])}: {'; '.join(r['reasons'])}" for r in result["not_mergeable"]]
    if result["out_of_scope"]:
        lines.append("\nOut of scope (base is neither develop nor the branch of an in-scope same-repository PR):")
        lines += [f"- #{r['number']} {_text(r['title'])} (base {_text(r['base'])})" for r in result["out_of_scope"]]
    if result["applied_edges"]:
        lines.append("\nApplied dependency edges: " + ", ".join(result["applied_edges"]))
    if result["proposed_edges"]:
        lines.append("\nProposed edges from PR bodies (not applied; confirm with --edge A:B): "
                     + ", ".join(result["proposed_edges"]))
    for w in result["warnings"]:
        lines.append(f"\nWarning: {w}")
    return "\n".join(lines) + "\n"


def _edge(text: str) -> tuple[int, int]:
    m = re.fullmatch(r"#?(\d+):#?(\d+)", text)
    if not m:
        raise argparse.ArgumentTypeError(f"edge must look like A:B, got {text!r}")
    return int(m.group(1)), int(m.group(2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("collect", help="read open PRs and required checks via gh")
    p_order = sub.add_parser("order", help="compute the merge order from a snapshot")
    p_order.add_argument("snapshot", help="snapshot file from `collect`, or - for stdin")
    p_order.add_argument("--edge", action="append", type=_edge, default=[], metavar="A:B")
    p_order.add_argument("--json", action="store_true", help="print JSON instead of Markdown")
    args = parser.parse_args(argv)

    if args.cmd == "collect":
        try:
            print(json.dumps(collect(), indent=2))
        except (RuntimeError, FileNotFoundError, KeyError, TypeError) as exc:
            print(f"collect failed: {exc}", file=sys.stderr)
            return 2
        return 0

    try:
        raw = sys.stdin.read() if args.snapshot == "-" else open(args.snapshot, encoding="utf-8").read()
        snapshot = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"cannot read snapshot: {exc}", file=sys.stderr)
        return 2
    try:
        result = order(snapshot, args.edge)
    except (AttributeError, KeyError, TypeError) as exc:
        print(f"malformed snapshot: {exc!r}", file=sys.stderr)
        return 2
    sys.stdout.write(json.dumps(result, indent=2) + "\n" if args.json else render(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
