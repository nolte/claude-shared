#!/usr/bin/env python3
"""Generate the aggregated portfolio inventory under ``docs/<lang>/portfolio/``.

Reads the committed snapshot ``portfolio/aggregate.yml`` (populated by the
``portfolio-audit`` skill's Render operation) and renders one section per
Portfolio-Member repository plus a capability-to-repository Mermaid map and a
historical-capabilities appendix, per
``spec/portfolio/portfolio-management/`` §Documentation rendering.

It also renders the portfolio tech stack per ``spec/portfolio/tech-stack/``
§Documentation rendering: a global-stack section preceding the per-repository
inventory, a per-member effective-stack view organised by ``group`` first and
``kind`` second with inherited / repo-specific / suppressed / regrouped badges,
the per-member delta view, a kind-distribution diagram, and the §Benefits
paraphrase with a backlink required by ``spec/portfolio/tech-stack-discovery/``
§Acceptance Criteria.

Determinism is load-bearing: the output is a pure function of
``portfolio/aggregate.yml`` and the configured languages, with no timestamps or
ordering nondeterminism, so the committed pages can be verified fresh in CI via
``git diff --exit-code`` (mirroring the skill-agent catalog mechanism). Edit the
snapshot, never the generated pages.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
AGGREGATE = REPO_ROOT / "portfolio" / "aggregate.yml"
SPEC_CONFIG = REPO_ROOT / "spec" / ".spec-config.yml"

TRACK = "developer-docs"
AUDIENCE = "maintainer"
CONTENT_MODE = "reference"

STATUS_BADGE = {
    "active": "✅ active",
    "experimental": "🧪 experimental",
    "deprecated": "⚠️ deprecated",
    "planned": "🗓️ planned",
}

# Per spec/portfolio/tech-stack/ §Group enum, in the order the spec defines —
# both the global-stack section and every per-member effective-stack view are
# organised by this order first and by `kind` second.
GROUP_ORDER = ["documentation", "quality", "automation", "build-tooling", "plugin-platform"]

# Per spec/portfolio/tech-stack/ §Inheritance semantics, a Portfolio-Member
# implicitly inherits every global entry whose status is active or experimental.
INHERITABLE_STATUS = ("active", "experimental")

# Backlink target for the §Benefits paraphrase required by
# spec/portfolio/tech-stack-discovery/ §Acceptance Criteria. The docs site
# doesn't publish the spec tree, so the backlink points at the canonical file on
# the default integration branch, one language file per rendered language.
SPEC_BASE = "https://github.com/nolte/claude-shared/blob/develop/spec/portfolio"

# Per-language page chrome. The snapshot data (capability descriptions, mission
# statements) is English source-of-truth and is rendered verbatim in both trees;
# only the structural labels below are translated.
L = {
    "en": {
        "title": "Portfolio inventory",
        "h1": "Portfolio inventory",
        "intro": (
            "Aggregated capability inventory across the active `nolte/*` portfolio, "
            "generated from each member repository's `project/portfolio.yml` manifest. "
            "This page is auto-generated — edit `portfolio/aggregate.yml` (or re-run the "
            "`portfolio-audit` skill's Render operation), not this file."
        ),
        "map": "Capability map",
        "map_intro": "Capability-to-repository mapping across the portfolio.",
        "overview": lambda r, c: f"**{r}** repositories · **{c}** capabilities",
        "legend": "Status:",
        "mission": "Mission",
        "mission_missing": "_No mission statement declared (`project/mission.md` missing)._",
        "capabilities": "Capabilities",
        "col_cap": "Capability",
        "col_status": "Status",
        "col_desc": "Description",
        "col_aud": "Audiences",
        "peers": "Peer references",
        "peers_none": "_None declared._",
        "historical": "Historical capabilities",
        "historical_none": "_No archived repositories with registered capabilities._",
        "archived_on": "archived",
        "tech_global": "Global tech stack",
        "tech_global_intro": (
            "The portfolio-wide technical baseline, hand-curated in "
            "`portfolio/tech-stack.yml`. Every Portfolio-Member repository implicitly "
            "inherits each entry below whose status is `active` or `experimental`; a "
            "member opts out by declaring an override with a rationale. Sections follow "
            "the `group` order defined by the tech-stack spec, and entries are ordered "
            "by `kind` inside each group."
        ),
        "tech_benefits": "Why this inventory exists",
        "tech_benefits_items": [
            "**Visibility across repositories.** One page answers which repositories use "
            "which building block, instead of grepping the lockfiles and workflow files of "
            "every repository in turn (outcome O-1).",
            "**Compressed onboarding cost.** A new contributor reads the technical "
            "baseline in one place before opening a single source file (outcomes O-1, O-2).",
            "**Standardisation pressure with an explicit safety valve.** The portfolio "
            "carries a default stack, and a repository that deviates announces itself with "
            "a written rationale rather than quietly reinventing the setup (outcome O-1).",
            "**Auditability of structural outliers.** With the inventory in place the "
            "portfolio audit can ask structural questions a free-form README can't answer, "
            "such as which repository ships rendered documentation without declaring a "
            "documentation generator (outcomes O-2, O-3).",
            "**Dogfooding the planning suite.** `claude-shared` captures its own stack "
            "first, so the capture flow is proven here before it ships to consumers "
            "(outcome O-3).",
        ],
        "tech_benefits_link": (
            "Paraphrased from the tech-stack-discovery spec's Benefits section; the full "
            "wording and the outcome anchors live in [`spec/portfolio/tech-stack-discovery/`]"
            f"({SPEC_BASE}/tech-stack-discovery/en.md)."
        ),
        "tech_dist": "Kind distribution",
        "tech_dist_intro": (
            "Repository-specific entries per `kind`, so structural outliers (a repository "
            "with two `language` entries, or none of a given kind) are visible at a glance. "
            "Inherited global entries are identical everywhere and are left out."
        ),
        "tech_dist_none": "_No repository declares its own tech-stack entries yet._",
        "tech_member": "Tech stack",
        "tech_member_none": (
            "_No `tech_stack:` block declared yet; this repository's effective stack is the "
            "global baseline above, unchanged._"
        ),
        "tech_legend": "Origin:",
        "origin_badge": {
            "inherited": "🔗 inherited",
            "repo-specific": "➕ repo-specific",
            "suppressed": "🚫 suppressed",
            "regrouped": "🔀 regrouped",
        },
        "col_entry": "Entry",
        "col_kind": "Kind",
        "col_role": "Role",
        "col_origin": "Origin",
        "col_notes": "Notes",
        "tech_delta": "Delta against the global stack",
        "delta_none": "_No delta; this repository inherits the global stack unchanged._",
    },
    "de": {
        "title": "Portfolio-Inventar",
        "h1": "Portfolio-Inventar",
        "intro": (
            "Aggregiertes Fähigkeiten-Inventar über das aktive `nolte/*`-Portfolio, "
            "generiert aus dem `project/portfolio.yml`-Manifest jedes Member-Repositories. "
            "Diese Seite ist auto-generiert — bearbeite `portfolio/aggregate.yml` (oder lass "
            "die Render-Operation des `portfolio-audit`-Skills erneut laufen), nicht diese Datei."
        ),
        "map": "Fähigkeiten-Karte",
        "map_intro": "Fähigkeit-zu-Repository-Zuordnung über das Portfolio.",
        "overview": lambda r, c: f"**{r}** Repositories · **{c}** Fähigkeiten",
        "legend": "Status:",
        "mission": "Mission",
        "mission_missing": "_Kein Mission-Statement deklariert (`project/mission.md` fehlt)._",
        "capabilities": "Fähigkeiten",
        "col_cap": "Fähigkeit",
        "col_status": "Status",
        "col_desc": "Beschreibung",
        "col_aud": "Zielgruppen",
        "peers": "Peer-Referenzen",
        "peers_none": "_Keine deklariert._",
        "historical": "Historische Fähigkeiten",
        "historical_none": "_Keine archivierten Repositories mit registrierten Fähigkeiten._",
        "archived_on": "archiviert",
        "tech_global": "Globaler Tech-Stack",
        "tech_global_intro": (
            "Die portfolioweite technische Grundlinie, handkuratiert in "
            "`portfolio/tech-stack.yml`. Jedes Portfolio-Member-Repository erbt implizit "
            "jeden Eintrag unten, dessen Status `active` oder `experimental` ist; ein Member "
            "steigt über einen Override mit Begründung aus. Die Abschnitte folgen der "
            "`group`-Reihenfolge aus der Tech-Stack-Spec, innerhalb einer Gruppe wird nach "
            "`kind` sortiert."
        ),
        "tech_benefits": "Warum es dieses Inventar gibt",
        "tech_benefits_items": [
            "**Sichtbarkeit über Repositories hinweg.** Eine Seite beantwortet, welches "
            "Repository welchen Baustein nutzt, statt in jedem Repository einzeln Lockfiles "
            "und Workflow-Dateien zu durchsuchen (Outcome O-1).",
            "**Geringere Onboarding-Kosten.** Neue Mitwirkende lesen die technische "
            "Grundlinie an einer Stelle, bevor sie die erste Quelldatei öffnen "
            "(Outcomes O-1, O-2).",
            "**Standardisierungsdruck mit explizitem Sicherheitsventil.** Das Portfolio hat "
            "einen Default-Stack, und ein abweichendes Repository meldet sich mit einer "
            "schriftlichen Begründung, statt das Setup stillschweigend neu zu erfinden "
            "(Outcome O-1).",
            "**Auditierbarkeit struktureller Ausreißer.** Mit dem Inventar kann das "
            "Portfolio-Audit strukturelle Fragen stellen, die ein freies README nicht "
            "beantworten kann, etwa welches Repository gerenderte Dokumentation ausliefert, "
            "ohne einen Dokumentationsgenerator zu deklarieren (Outcomes O-2, O-3).",
            "**Dogfooding der Planungs-Suite.** `claude-shared` erfasst zuerst den eigenen "
            "Stack, damit der Erfassungsablauf hier erprobt ist, bevor er an Konsumenten "
            "ausgeliefert wird (Outcome O-3).",
        ],
        "tech_benefits_link": (
            "Paraphrasiert aus dem Benefits-Abschnitt der Tech-Stack-Discovery-Spec; der "
            "vollständige Wortlaut und die Outcome-Anker stehen in "
            "[`spec/portfolio/tech-stack-discovery/`]"
            f"({SPEC_BASE}/tech-stack-discovery/de.md)."
        ),
        "tech_dist": "Verteilung nach Art",
        "tech_dist_intro": (
            "Repo-spezifische Einträge je `kind`, damit strukturelle Ausreißer (ein "
            "Repository mit zwei `language`-Einträgen oder ganz ohne eine bestimmte Art) auf "
            "einen Blick sichtbar sind. Geerbte globale Einträge sind überall identisch und "
            "bleiben außen vor."
        ),
        "tech_dist_none": "_Noch kein Repository deklariert eigene Tech-Stack-Einträge._",
        "tech_member": "Tech-Stack",
        "tech_member_none": (
            "_Noch kein `tech_stack:`-Block deklariert; der effektive Stack dieses "
            "Repositories ist die globale Grundlinie oben, unverändert._"
        ),
        "tech_legend": "Herkunft:",
        "origin_badge": {
            "inherited": "🔗 geerbt",
            "repo-specific": "➕ repo-spezifisch",
            "suppressed": "🚫 unterdrückt",
            "regrouped": "🔀 neu gruppiert",
        },
        "col_entry": "Eintrag",
        "col_kind": "Art",
        "col_role": "Rolle",
        "col_origin": "Herkunft",
        "col_notes": "Anmerkungen",
        "tech_delta": "Delta gegenüber dem globalen Stack",
        "delta_none": "_Kein Delta; dieses Repository erbt den globalen Stack unverändert._",
    },
}

AUTOGEN = (
    "<!-- AUTO-GENERATED by scripts/docs/gen_portfolio.py from "
    "portfolio/aggregate.yml. Do not edit by hand; edit the snapshot and run "
    "`task docs:portfolio`. -->"
)


class PortfolioError(Exception):
    """Raised on malformed snapshot input."""


def load_languages() -> list[str]:
    cfg = yaml.safe_load(SPEC_CONFIG.read_text(encoding="utf-8")) or {}
    langs = cfg.get("languages") or ["en"]
    if not isinstance(langs, list) or not langs:
        raise PortfolioError("spec/.spec-config.yml: 'languages' must be a non-empty list")
    return [str(x) for x in langs]


def _node_id(prefix: str, n: int) -> str:
    return f"{prefix}{n}"


def _esc(text: str) -> str:
    """Escape a Mermaid node label (quotes only; labels are wrapped in quotes)."""
    return str(text).replace('"', "'")


def _html(text: str) -> str:
    """Escape plain-text Markdown cell/blockquote content so angle-bracket
    placeholders (``<name>``, ``<plugin>:<agent>``) survive rendering instead of
    being parsed as HTML tags by the Markdown/HTML pipeline. Backtick code spans
    in the source render as before; only literal ``&``/``<``/``>`` are escaped."""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def render_mermaid(members: list[dict]) -> list[str]:
    # Per spec/project/mermaid-diagrams/ every Mermaid block under docs/<lang>/
    # MUST be preceded by a diagram-source comment; this block is derived from
    # the committed snapshot, so docs-freshness can detect drift against it.
    #
    # Each repository is a subgraph that visually boxes its capabilities (clearer
    # than a flat repo→capability arrow fan). Non-active capabilities carry
    # their status badge in the node label: spec/project/mermaid-diagrams/
    # MUST NOTs classDef/style/linkStyle with hard-coded colors, so light/dark
    # rendering stays with Material's theme bridge and status stays scannable
    # through the label text. Peer references are drawn as repo-to-repo edges.
    out = [
        "<!-- diagram-source: derived—portfolio/aggregate.yml -->",
        "```mermaid",
        "flowchart LR",
    ]
    for ri, m in enumerate(members):
        out.append(f'    subgraph R{ri}["{_esc(m["repo"])}"]')
        for ci, cap in enumerate(m.get("capabilities", [])):
            cid = _node_id(f"R{ri}C", ci)
            status = str(cap.get("status", ""))
            label = _esc(cap["name"])
            if status in STATUS_BADGE and status != "active":
                label = f"{label}<br/>{STATUS_BADGE[status]}"
            out.append(f'        {cid}["{label}"]')
        out.append("    end")
    # Outbound peer edges (repo-to-repo) when declared.
    repo_to_rid = {m["repo"]: _node_id("R", ri) for ri, m in enumerate(members)}
    for ri, m in enumerate(members):
        for peer in m.get("peers") or []:
            target = repo_to_rid.get(peer)
            if target:
                out.append(f'    R{ri} -.peer.-> {target}')
    out.append("```")
    return out


def _cell(text: str) -> str:
    """Escape a value for a Markdown table cell: HTML-escape it, collapse the
    folded-YAML line breaks the snapshot carries, and neutralise pipes so a
    rationale sentence can't break the column layout."""
    return _html(" ".join(str(text).split())).replace("|", "\\|")


def _group_sort_key(group: str) -> tuple[int, str]:
    """Order a group by the spec's §Group enum sequence; an unknown value sorts
    last but stays rendered, so an enum extension shows up instead of vanishing."""
    group = str(group)
    return (GROUP_ORDER.index(group) if group in GROUP_ORDER else len(GROUP_ORDER), group)


def _by_group(rows: list[dict]) -> list[tuple[str, list[dict]]]:
    """Bucket rows into (group, rows) pairs, group-first per §Group enum order and
    kind-second inside each group."""
    groups = sorted({str(r["group"]) for r in rows}, key=_group_sort_key)
    return [
        (
            g,
            sorted(
                (r for r in rows if str(r["group"]) == g),
                key=lambda r: (str(r["kind"]), str(r["name"])),
            ),
        )
        for g in groups
    ]


def effective_stack(member: dict, global_entries: list[dict]) -> list[dict]:
    """Compute a member's effective tech stack per spec/portfolio/tech-stack/
    §Inheritance semantics: the inheritable global entries, with `overrides:`
    marked suppressed and `regroup:` re-classified, plus the member's own
    `additions:`. Suppressed entries stay in the view (carrying their rationale)
    because §Documentation rendering requires them to be shown, not dropped."""
    ts = member.get("tech_stack") or {}
    overrides = {str(o["name"]): o for o in (ts.get("overrides") or [])}
    regroups = {str(r["name"]): r for r in (ts.get("regroup") or [])}
    rows: list[dict] = []
    for e in global_entries:
        if str(e.get("status")) not in INHERITABLE_STATUS:
            continue
        name = str(e["name"])
        row = {
            "name": name,
            "kind": e.get("kind", "—"),
            "group": e.get("group", "—"),
            "status": e.get("status", ""),
            "origin": "inherited",
            "note": "",
        }
        if name in overrides:
            row["origin"] = "suppressed"
            row["note"] = overrides[name].get("rationale", "")
        elif name in regroups:
            rg = regroups[name]
            row["origin"] = "regrouped"
            row["group"] = rg.get("group", row["group"])
            row["note"] = f"`{e.get('group', '—')}` → `{rg.get('group', '—')}` — {rg.get('rationale', '')}"
        rows.append(row)
    for a in ts.get("additions") or []:
        rows.append(
            {
                "name": str(a["name"]),
                "kind": a.get("kind", "—"),
                "group": a.get("group", "—"),
                "status": a.get("status", ""),
                "origin": "repo-specific",
                "note": "",
            }
        )
    return rows


def render_global_tech_stack(entries: list[dict], t: dict) -> list[str]:
    """Render the global-stack section that §Documentation rendering requires to
    precede the per-repository inventory, plus the §Benefits paraphrase and the
    kind-distribution diagram."""
    out = [f"## {t['tech_global']}", "", t["tech_global_intro"], ""]
    out += [f"### {t['tech_benefits']}", ""]
    out += [f"- {b}" for b in t["tech_benefits_items"]]
    out += ["", t["tech_benefits_link"], ""]
    for group, rows in _by_group(entries):
        out += [
            f"### `{group}`",
            "",
            f"| {t['col_entry']} | {t['col_kind']} | {t['col_status']} | {t['col_role']} |",
            "|---|---|---|---|",
        ]
        for r in rows:
            badge = STATUS_BADGE.get(str(r.get("status", "")), str(r.get("status", "—")))
            out.append(
                f"| `{r['name']}` | `{r['kind']}` | {badge} | {_cell(r.get('role', '—'))} |"
            )
        out.append("")
    return out


def render_kind_distribution(members: list[dict], t: dict) -> list[str]:
    """Kind-distribution diagram per spec/portfolio/tech-stack/ §Documentation
    rendering: one subgraph per repository that declares its own entries, one node
    per `kind` carrying that repository's count, so a repo with two `language`
    entries or none of a kind stands out. Inherited entries are portfolio-uniform
    and would only add noise, so the diagram covers `additions:` only."""
    declaring = [
        m for m in members if (m.get("tech_stack") or {}).get("additions")
    ]
    out = [f"## {t['tech_dist']}", "", t["tech_dist_intro"], ""]
    if not declaring:
        return out + [t["tech_dist_none"], ""]
    # Per spec/project/mermaid-diagrams/ every Mermaid block under docs/<lang>/
    # MUST carry a diagram-source comment; this one is derived from the committed
    # snapshot, so docs-freshness can detect drift against it.
    out += [
        "<!-- diagram-source: derived—portfolio/aggregate.yml -->",
        "```mermaid",
        "flowchart LR",
    ]
    for ri, m in enumerate(declaring):
        counts: dict[str, int] = {}
        for a in m["tech_stack"]["additions"]:
            counts[str(a.get("kind", "other"))] = counts.get(str(a.get("kind", "other")), 0) + 1
        out.append(f'    subgraph K{ri}["{_esc(m["repo"])}"]')
        for ki, kind in enumerate(sorted(counts)):
            out.append(f'        K{ri}N{ki}["{_esc(kind)} × {counts[kind]}"]')
        out.append("    end")
    out += ["```", ""]
    return out


def render_member_tech_stack(m: dict, global_entries: list[dict], t: dict) -> list[str]:
    """Render one member's effective-stack view (the §Documentation rendering MUST:
    group-first, kind-second, badged) followed by its delta view (the SHOULD)."""
    out = [f"### {t['tech_member']}", ""]
    if not (m.get("tech_stack") or {}):
        return out + [t["tech_member_none"], ""]
    rows = effective_stack(m, global_entries)
    for group, group_rows in _by_group(rows):
        out += [
            f"#### `{group}`",
            "",
            f"| {t['col_entry']} | {t['col_kind']} | {t['col_status']} | "
            f"{t['col_origin']} | {t['col_notes']} |",
            "|---|---|---|---|---|",
        ]
        for r in group_rows:
            badge = STATUS_BADGE.get(str(r.get("status", "")), str(r.get("status", "—")))
            origin = t["origin_badge"][r["origin"]]
            note = _cell(r["note"]) if r["note"] else "—"
            out.append(f"| `{r['name']}` | `{r['kind']}` | {badge} | {origin} | {note} |")
        out.append("")

    ts = m["tech_stack"]
    delta: list[str] = []
    for o in ts.get("overrides") or []:
        delta.append(
            f"- {t['origin_badge']['suppressed']} `{o['name']}` — "
            f"{_cell(o.get('rationale', '—'))}"
        )
    for r in ts.get("regroup") or []:
        delta.append(
            f"- {t['origin_badge']['regrouped']} `{r['name']}` — `{r.get('group', '—')}` "
            f"({_cell(r.get('rationale', '—'))})"
        )
    for a in ts.get("additions") or []:
        delta.append(
            f"- {t['origin_badge']['repo-specific']} `{a['name']}` — "
            f"`{a.get('kind', '—')}` / `{a.get('group', '—')}`"
        )
    out += [f"#### {t['tech_delta']}", ""]
    out += (delta + [""]) if delta else [t["delta_none"], ""]
    return out


def render_member(m: dict, t: dict, global_entries: list[dict]) -> list[str]:
    out = [f"## {m['repo']}", ""]
    mission = (m.get("mission_statement") or "").strip()
    if mission:
        out += [f"> {_html(mission)}", ""]
    else:
        # Per spec/portfolio/portfolio-management/ §Documentation rendering, a
        # member without a project/mission.md renders a placeholder noting the
        # gap (the Audit emits a Warning); the renderer never invents a mission.
        out += [t["mission_missing"], ""]
    out += [f"### {t['capabilities']}", ""]
    caps = m.get("capabilities", [])
    if caps:
        out += [
            f"| {t['col_cap']} | {t['col_status']} | {t['col_desc']} | {t['col_aud']} |",
            "|---|---|---|---|",
        ]
        for cap in caps:
            badge = STATUS_BADGE.get(str(cap.get("status", "")), str(cap.get("status", "—")))
            desc = _html(" ".join(str(cap.get("description", "")).split()))
            # One audience per line keeps the cell scannable instead of a
            # run-on; <br> renders as a line break in the Material table cell.
            aud = "<br>".join(_html(a) for a in (cap.get("audience") or [])) or "—"
            name = cap.get("name", "—")
            out.append(f"| `{name}` | {badge} | {desc} | {aud} |")
        out.append("")
    out += render_member_tech_stack(m, global_entries, t)
    peers = m.get("peers") or []
    out += [f"### {t['peers']}", ""]
    if peers:
        out += [f"- `{p}`" for p in peers] + [""]
    else:
        out += [t["peers_none"], ""]
    return out


def render_page(lang: str, snapshot: dict) -> str:
    t = L.get(lang, L["en"])
    members = sorted(snapshot.get("members", []), key=lambda m: m["repo"])
    historical = snapshot.get("historical") or []
    global_entries = snapshot.get("global_tech_stack") or []

    fm = [
        "---",
        f"title: {t['title']}",
        f"audience: [{AUDIENCE}]",
        f"content_mode: {CONTENT_MODE}",
        f"track: {TRACK}",
        "last_updated: generated",
        "---",
        "",
    ]
    n_caps = sum(len(m.get("capabilities", [])) for m in members)
    legend = " · ".join(
        STATUS_BADGE[k] for k in ("active", "experimental", "deprecated", "planned")
    )

    body = [AUTOGEN, "", f"# {t['h1']}", "", t["intro"], ""]
    body += [t["overview"](len(members), n_caps), ""]
    body += [f"## {t['map']}", "", t["map_intro"], ""]
    body += render_mermaid(members)
    body += ["", f"{t['legend']} {legend}", ""]
    # Per spec/portfolio/tech-stack/ §Documentation rendering the global stack is
    # a top-level section that precedes the per-repository inventory.
    if global_entries:
        body += render_global_tech_stack(global_entries, t)
        body += render_kind_distribution(members, t)
        origin_legend = " · ".join(
            t["origin_badge"][k]
            for k in ("inherited", "repo-specific", "suppressed", "regrouped")
        )
        body += [f"{t['tech_legend']} {origin_legend}", ""]
    for m in members:
        body += render_member(m, t, global_entries)
    body += [f"## {t['historical']}", ""]
    if historical:
        for h in historical:
            cap = h.get("name", "—")
            repo = h.get("repo", "—")
            date = h.get("archived", "—")
            body.append(f"- `{cap}` ({repo}) — {t['archived_on']} {date}")
        body.append("")
    else:
        body += [t["historical_none"], ""]
    return "\n".join(fm + body).rstrip() + "\n"


def main() -> int:
    if not AGGREGATE.exists():
        raise PortfolioError(f"missing snapshot: {AGGREGATE}")
    snapshot = yaml.safe_load(AGGREGATE.read_text(encoding="utf-8")) or {}
    if not isinstance(snapshot.get("members"), list):
        raise PortfolioError("portfolio/aggregate.yml: top-level 'members' must be a list")
    for lang in load_languages():
        out_dir = REPO_ROOT / "docs" / lang / "portfolio"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.md").write_text(render_page(lang, snapshot), encoding="utf-8")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except PortfolioError as exc:
        print(f"gen_portfolio: {exc}", file=sys.stderr)
        sys.exit(1)
