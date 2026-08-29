#!/usr/bin/env python3
"""Deterministic documentation link checker.

Implements `spec/project/link-validation/`. Resolves internal, intra-page
anchor, and cross-tree links offline against the working tree, and probes
external `http(s)` links over HTTP. Reports findings; never edits files.

Link classes (one per extracted link):
  internal      relative link to another in-repo doc file (+ optional #anchor)
  anchor        fragment-only link (#section) into the same file
  cross-tree    relative link into a non-docs repo root (spec/, src/, ...)
  external      absolute http:// or https:// URL (probed online)
  scheme        mailto:/tel:/ftp:/... (well-formedness only, never probed)

Exit codes:
  0  no finding at or above the failing severity floor (default: critical)
  1  at least one finding at or above the failing floor
  2  internal error (file unreadable, mkdocs.yml/config unparseable, etc.)

Usage:
  python scripts/check_links.py                  # full scope, online
  python scripts/check_links.py --offline        # internal + anchor + cross-tree only
  python scripts/check_links.py --external        # external links only
  python scripts/check_links.py docs/en/guide.md # narrow to one path
  python scripts/check_links.py --format json     # machine-readable output

Output is one finding per line, prefixed with severity in Title Case
(`Critical`, `Warning`, `Info`) so downstream tooling greps deterministically.
Offline-mode output is byte-identical for an unchanged tree.

Configuration (all optional) lives in `.linkcheck.toml` at the repo root:
  ignore       = ["https://flaky.example/*", "*/legacy/*"]  # fnmatch globs
  soft_403     = ["linkedin.com", "x.com"]                  # bot-hostile hosts
  timeout      = 10        # seconds per request
  retries      = 2         # retries before classifying transient
  concurrency  = 8         # global parallel probes
  max_redirects = 5
  fail_on      = "critical"  # critical | warning | info
"""
from __future__ import annotations

import argparse
import concurrent.futures
import fnmatch
import json
import re
import socket
import ssl
import sys
import threading
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

try:  # Python 3.11+
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - older interpreters
    tomllib = None

REPO = Path(__file__).resolve().parent.parent
USER_AGENT = (
    "nolte-shared-link-checker/1.0 "
    "(+https://github.com/nolte/claude-shared; spec/project/link-validation)"
)

# Repo roots that, when a link resolves into them, mark the link as cross-tree
# rather than an ordinary internal doc link. Sourced from
# spec/project/docs-freshness/ §Cross-tree reference rot.
CROSS_TREE_ROOTS = {
    "spec", "src", "scripts", "docker", "helm", "tests", "tools",
    "agents", "skills", "ansible", "portfolio",
}

# Directories never scanned for source files.
SKIP_DIRS = {".git", "node_modules", ".audits", ".venv", "venv",
             "__pycache__", "site", ".cache", "vendor"}

# Hand-maintained markdown trees outside the MkDocs docs_dir that participate in
# the default scope, per spec/project/link-validation/ §Scope. Extend only with a
# tree that is authored by hand and linked into; generated trees stay out.
HAND_MAINTAINED_TREES = ("spec",)

# Built-in known bot-hostile hosts that answer 403/999 to automated agents
# though the page is live for humans (spec §What counts as a dead link).
DEFAULT_SOFT_403 = {
    "linkedin.com", "www.linkedin.com", "x.com", "twitter.com",
    "facebook.com", "www.facebook.com", "instagram.com", "medium.com",
}

WEAK_ANCHOR_TEXT = {
    "here", "click here", "click", "this", "link", "this link", "→",
    "read more", "more", "see here", "see", "details", "info",
}
TRACKING_KEYS = {"fbclid", "gclid", "mc_eid", "igshid", "msclkid", "yclid"}
BRANCH_REF_RE = re.compile(
    r"https?://(?:www\.)?github\.com/[^/]+/[^/]+/(?:blob|tree|raw)/"
    r"(?:main|master|develop|HEAD)/"
)
LOCAL_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0", "::1"}

SEVERITY_ORDER = {"Info": 0, "Warning": 1, "Critical": 2}


# --------------------------------------------------------------------------- #
# Data model
# --------------------------------------------------------------------------- #
@dataclass
class Link:
    path: str          # repo-relative source file
    line: int
    text: str          # visible anchor text ("" for autolinks/bare/images)
    target: str        # raw link target (may include #fragment)
    is_image: bool = False


@dataclass
class Finding:
    severity: str      # Critical | Warning | Info
    path: str
    line: int
    target: str
    cls: str           # internal | anchor | cross-tree | external | scheme
    reason: str

    def as_line(self) -> str:
        return (f"{self.severity}: {self.path}:{self.line} [{self.cls}] "
                f"{self.target} — {self.reason}")

    def as_dict(self) -> dict:
        return {
            "severity": self.severity, "path": self.path, "line": self.line,
            "target": self.target, "class": self.cls, "reason": self.reason,
        }


@dataclass
class Config:
    ignore: list = field(default_factory=list)
    soft_403: set = field(default_factory=lambda: set(DEFAULT_SOFT_403))
    timeout: float = 10.0
    retries: int = 2
    concurrency: int = 8
    max_redirects: int = 5
    per_host_delay: float = 0.3
    fail_on: str = "critical"
    cache_ttl: float = 24 * 3600


# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
def load_config(repo: Path) -> Config:
    cfg = Config()
    path = repo / ".linkcheck.toml"
    if not path.exists():
        return cfg
    if tomllib is None:
        raise RuntimeError(".linkcheck.toml present but tomllib unavailable "
                           "(needs Python 3.11+)")
    with path.open("rb") as fh:
        data = tomllib.load(fh)
    cfg.ignore = list(data.get("ignore", []))
    cfg.soft_403 = set(DEFAULT_SOFT_403) | set(data.get("soft_403", []))
    cfg.timeout = float(data.get("timeout", cfg.timeout))
    cfg.retries = int(data.get("retries", cfg.retries))
    cfg.concurrency = int(data.get("concurrency", cfg.concurrency))
    cfg.max_redirects = int(data.get("max_redirects", cfg.max_redirects))
    cfg.per_host_delay = float(data.get("per_host_delay", cfg.per_host_delay))
    cfg.fail_on = str(data.get("fail_on", cfg.fail_on)).lower()
    cfg.cache_ttl = float(data.get("cache_ttl", cfg.cache_ttl))
    return cfg


# --------------------------------------------------------------------------- #
# Scope discovery
# --------------------------------------------------------------------------- #
def discover_docs_dir(repo: Path) -> Path | None:
    """Read `docs_dir` from mkdocs.yml without a YAML dependency."""
    mk = repo / "mkdocs.yml"
    if not mk.exists():
        return None
    try:
        for raw in mk.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\s*docs_dir\s*:\s*(\S+)", raw)
            if m:
                return repo / m.group(1).strip().strip("\"'")
    except OSError:
        return None
    return repo / "docs"  # mkdocs default when key is absent


def scope_files(repo: Path, targets: list[str]) -> list[Path]:
    """Resolve the in-scope markdown file set, deterministically sorted."""
    if targets:
        out: list[Path] = []
        for t in targets:
            p = (repo / t).resolve() if not Path(t).is_absolute() else Path(t)
            if p.is_dir():
                out.extend(p.rglob("*.md"))
            elif p.suffix == ".md" and p.exists():
                out.append(p)
        return sorted(set(out))

    files: set[Path] = set()
    docs_dir = discover_docs_dir(repo)
    if docs_dir and docs_dir.exists():
        files.update(docs_dir.rglob("*.md"))
    else:
        # Fallback: every tracked-looking markdown file outside skip dirs.
        for p in repo.rglob("*.md"):
            if not any(part in SKIP_DIRS for part in p.relative_to(repo).parts):
                files.add(p)
    # Top-level hand-maintained markdown always participates (spec §Scope).
    for name in ("README.md", "CLAUDE.md"):
        p = repo / name
        if p.exists():
            files.add(p)
    for p in repo.glob("*.md"):
        files.add(p)
    # Hand-maintained markdown trees outside docs_dir participate too, per spec
    # §Scope. `spec/` is authored by hand and links into docs/, skills/, agents/,
    # and its own siblings, so it rots the same way — but it was only ever a link
    # *target* here, never a *source*, which let six dead links inside
    # spec/project/blog-author-trigger/ survive a fully green gate (PR #571).
    # The inclusion is deliberately scoped to the offline classes: this corpus
    # carries ~80x more external URLs than docs_dir, and §Scope forbids widening
    # the external class to it by default.
    for tree in HAND_MAINTAINED_TREES:
        d = repo / tree
        if d.is_dir():
            files.update(
                p for p in d.rglob("*.md")
                if not any(part in SKIP_DIRS for part in p.relative_to(repo).parts)
            )
    return sorted(files)


# --------------------------------------------------------------------------- #
# Link + heading extraction
# --------------------------------------------------------------------------- #
INLINE_RE = re.compile(r"(!?)\[([^\]]*)\]\(\s*([^)]+?)\s*\)")
REF_USE_RE = re.compile(r"(!?)\[([^\]]+)\]\[([^\]]*)\]")
REF_DEF_RE = re.compile(r"^\s*\[([^\]]+)\]:\s*(\S+)")
AUTOLINK_RE = re.compile(r"<((?:https?|ftp|mailto|tel):[^>\s]+)>")
HTML_ATTR_RE = re.compile(r"""(?:href|src)\s*=\s*["']([^"']+)["']""", re.I)
BARE_URL_RE = re.compile(r"(?<![\(<\"'\]])(https?://[^\s<>)\]\"']+)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
CUSTOM_ID_RE = re.compile(r"\{#([A-Za-z0-9_-]+)\}\s*$")
INLINE_CODE_RE = re.compile(r"`[^`]*`")
IGNORE_SAME = "<!-- linkcheck-ignore -->"
IGNORE_NEXT = "<!-- linkcheck-ignore-next-line -->"


def strip_inline_code(line: str) -> str:
    """Blank out inline code spans so URLs inside them aren't treated as links."""
    return INLINE_CODE_RE.sub(lambda m: " " * len(m.group(0)), line)


def first_token(target: str) -> str:
    """Drop a markdown link title: (url "title") -> url; strip <>."""
    t = target.strip()
    if t.startswith("<") and ">" in t:
        return t[1:t.index(">")]
    return t.split()[0] if t.split() else t


def extract(path: Path, rel: str,
            docs_dir: Path | None = None) -> tuple[list[Link], set[str], set[int]]:
    """Return (links, heading-slugs, ignored-line-numbers) for one file."""
    github = not (docs_dir is not None and docs_dir in path.parents)
    links: list[Link] = []
    headings: list[str] = []
    custom_ids: set[str] = set()
    ignored_lines: set[int] = set()
    in_fence = False
    fence_marker = ""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()

    for idx, raw in enumerate(lines, start=1):
        stripped = raw.lstrip()
        # Fenced code blocks (``` or ~~~): toggle, never extract inside.
        fm = re.match(r"(```+|~~~+)", stripped)
        if fm:
            if not in_fence:
                in_fence, fence_marker = True, fm.group(1)[0]
            elif stripped[0] == fence_marker:
                in_fence = False
            continue
        if in_fence:
            continue

        if IGNORE_NEXT in raw:
            ignored_lines.add(idx + 1)
        if IGNORE_SAME in raw:
            ignored_lines.add(idx)

        hm = HEADING_RE.match(raw)
        if hm:
            htext = hm.group(2)
            cid = CUSTOM_ID_RE.search(htext)
            if cid:
                custom_ids.add(cid.group(1))
                htext = CUSTOM_ID_RE.sub("", htext)
            headings.append(htext)

        code_free = strip_inline_code(raw)

        # Reference definitions are not themselves clickable links, but their
        # targets must resolve — record as links with empty visible text.
        dm = REF_DEF_RE.match(code_free)
        if dm:
            links.append(Link(rel, idx, "", first_token(dm.group(2))))
            continue

        seen_spans: list[tuple[int, int]] = []
        for m in INLINE_RE.finditer(code_free):
            seen_spans.append(m.span())
            links.append(Link(rel, idx, m.group(2).strip(),
                              first_token(m.group(3)), is_image=bool(m.group(1))))
        for m in AUTOLINK_RE.finditer(code_free):
            seen_spans.append(m.span())
            links.append(Link(rel, idx, "", m.group(1)))
        for m in HTML_ATTR_RE.finditer(code_free):
            links.append(Link(rel, idx, "", m.group(1)))
        for m in BARE_URL_RE.finditer(code_free):
            if any(s <= m.start() < e for s, e in seen_spans):
                continue
            links.append(Link(rel, idx, "", m.group(1).rstrip(".,;:")))

    slugs = build_slugs(headings, github) | custom_ids
    return links, slugs, ignored_lines


def _pre_slug(text: str) -> str:
    """Drop inline markdown emphasis/code/link syntax before slugging."""
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return re.sub(r"[`*_~]", "", text)


def slugify_material(text: str) -> str:
    """python-markdown / mkdocs-material default (ASCII) slug: collapses runs."""
    value = unicodedata.normalize("NFKD", _pre_slug(text))
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[\s-]+", "-", value)


def slugify_github(text: str) -> str:
    """GitHub-Flavored-Markdown slug: 1:1 space->hyphen, no run collapsing."""
    value = _pre_slug(text).strip().lower()
    value = re.sub(r"[^\w\s-]", "", value, flags=re.UNICODE)
    return value.replace(" ", "-")


def build_slugs(headings: list[str], github: bool) -> set[str]:
    """Slugify headings with the renderer's numeric de-duplication.

    The slug algorithm is renderer-specific: files under the MkDocs `docs_dir`
    render through mkdocs-material (whitespace collapsed); top-level files like
    README.md and anything outside `docs_dir` render on GitHub (1:1 spacing).
    Using the wrong one produces systematic false positives on headings with
    special characters (e.g. `## Scope & guarantees`).
    """
    slug = slugify_github if github else slugify_material
    seen: dict[str, int] = {}
    out: set[str] = set()
    for h in headings:
        base = slug(h)
        if not base:
            continue
        if base in seen:
            seen[base] += 1
            out.add(f"{base}-{seen[base]}")
        else:
            seen[base] = 0
            out.add(base)
    return out


# --------------------------------------------------------------------------- #
# Classification + offline resolution
# --------------------------------------------------------------------------- #
def classify(target: str) -> str:
    low = target.lower()
    if low.startswith(("http://", "https://")):
        return "external"
    if re.match(r"^[a-z][a-z0-9+.-]*:", low) and not low.startswith("file:"):
        return "scheme"
    if target.startswith("#"):
        return "anchor"
    return "internal-or-cross"  # disambiguated after path resolution


def resolve_offline(repo: Path, file_path: Path, link: Link,
                    own_slugs: set[str], slug_cache: dict,
                    docs_dir: Path | None = None) -> Finding | None:
    rel = str(file_path.relative_to(repo))
    target = link.target
    path_part, _, frag = target.partition("#")

    # Pure fragment -> intra-page anchor.
    if not path_part:
        if frag and frag not in own_slugs:
            return Finding("Critical", rel, link.line, target, "anchor",
                           f"anchor #{frag} not found in this file")
        return None

    # Resolve the path component against the working tree.
    if path_part.startswith("/"):
        tgt = (repo / path_part.lstrip("/")).resolve()
    else:
        tgt = (file_path.parent / path_part).resolve()

    try:
        rel_tgt = tgt.relative_to(repo)
        top = rel_tgt.parts[0] if rel_tgt.parts else ""
    except ValueError:
        top = ""
    cls = "cross-tree" if top in CROSS_TREE_ROOTS else "internal"

    if not tgt.exists():
        return Finding("Critical", rel, link.line, target, cls,
                       "target path does not exist")

    # Anchor into another markdown file (only when we can read it).
    if frag and tgt.suffix == ".md" and tgt.is_file():
        if tgt not in slug_cache:
            try:
                _, s, _ = extract(tgt, str(rel_tgt), docs_dir)
                slug_cache[tgt] = s
            except OSError:
                slug_cache[tgt] = None
        slugs = slug_cache[tgt]
        if slugs is not None and frag not in slugs:
            return Finding("Critical", rel, link.line, target, cls,
                           f"anchor #{frag} not found in {rel_tgt}")
    return None


def scheme_finding(link: Link) -> Finding | None:
    low = link.target.lower()
    if low.startswith("mailto:"):
        addr = link.target[7:].split("?")[0]
        if "@" not in addr or "." not in addr.split("@")[-1]:
            return Finding("Warning", link.path, link.line, link.target,
                           "scheme", "malformed mailto: address")
    if low.startswith("tel:"):
        if not re.match(r"^tel:\+?[0-9\-\s().]+$", low):
            return Finding("Warning", link.path, link.line, link.target,
                           "scheme", "malformed tel: number")
    return None


# --------------------------------------------------------------------------- #
# Link-quality findings (info; never fail a gate) for external links
# --------------------------------------------------------------------------- #
def quality_findings(link: Link) -> list[Finding]:
    out: list[Finding] = []
    url = link.target
    parsed = urllib.parse.urlsplit(url)
    host = (parsed.hostname or "").lower()
    if host in LOCAL_HOSTS or url.lower().startswith("file:"):
        return out  # local/non-portable hosts are covered by a Warning already
    if parsed.scheme == "http":
        out.append(Finding("Info", link.path, link.line, url, "external",
                           "http:// — prefer https://"))
    if BRANCH_REF_RE.match(url):
        out.append(Finding("Info", link.path, link.line, url, "external",
                           "branch-ref permalink — prefer a tag/commit permalink"))
    qs = urllib.parse.parse_qs(parsed.query)
    bad = [k for k in qs if k.startswith("utm_") or k in TRACKING_KEYS]
    if bad:
        out.append(Finding("Info", link.path, link.line, url, "external",
                           f"tracking parameters present: {', '.join(sorted(bad))}"))
    if link.text and link.text.strip().lower() in WEAK_ANCHOR_TEXT:
        out.append(Finding("Info", link.path, link.line, url, "external",
                           f"weak anchor text: {link.text.strip()!r}"))
    return out


def local_host_finding(link: Link, host: str) -> Finding | None:
    if link.target.lower().startswith("file:"):
        return Finding("Warning", link.path, link.line, link.target, "external",
                       "file:// link is not portable")
    h = host.split(":")[0]
    if h in LOCAL_HOSTS or h.startswith(("10.", "192.168.", "127.")):
        return Finding("Warning", link.path, link.line, link.target, "external",
                       f"local/private host: {h}")
    return None


# --------------------------------------------------------------------------- #
# External HTTP probing
# --------------------------------------------------------------------------- #
class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # surface the 3xx to us instead of following it


_OPENER = urllib.request.build_opener(_NoRedirect)


def _one_request(url: str, method: str, timeout: float):
    """Return (status, location_or_none). Raises on network/transport errors."""
    req = urllib.request.Request(url, method=method,
                                 headers={"User-Agent": USER_AGENT,
                                          "Accept": "*/*"})
    try:
        with _OPENER.open(req, timeout=timeout) as resp:
            return resp.status, None
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Location")


def probe(url: str, cfg: Config) -> tuple[str, str, str]:
    """Probe one external URL. Return (severity, classification, reason)."""
    parsed = urllib.parse.urlsplit(url)
    host = parsed.hostname or ""

    def attempt() -> tuple[str, str, str] | None:
        current, method, hops = url, "HEAD", 0
        while hops <= cfg.max_redirects:
            status, location = _one_request(current, method, cfg.timeout)
            if status in (405, 501) and method == "HEAD":
                method = "GET"
                continue
            if 300 <= status < 400 and location:
                nxt = urllib.parse.urljoin(current, location)
                if status in (301, 308) and hops == 0:
                    # Permanent redirect away from the cited URL.
                    final = _follow_final(nxt, cfg)
                    if final and 200 <= final < 400:
                        return ("Warning", "redirect-stale",
                                f"permanent redirect ({status}) -> {nxt}")
                current, hops = nxt, hops + 1
                method = "HEAD"
                continue
            if hops > cfg.max_redirects:
                return ("Warning", "redirect-loop",
                        f"redirect chain exceeds {cfg.max_redirects} hops")
            if 200 <= status < 300:
                return ("ok", "healthy", f"{status}")
            if status in (404, 410):
                return ("Critical", "dead", f"HTTP {status}")
            if status == 429 or (status in (403, 999) and _soft(host, cfg)):
                return ("Warning", "rate-limited",
                        f"HTTP {status} (bot-hostile/throttled; presumed live)")
            if status in (400, 401, 403):
                if method == "HEAD":
                    method = "GET"
                    continue
                return ("Critical", "dead", f"HTTP {status}")
            if 500 <= status < 600:
                return None  # transient -> retry
            return ("Warning", "unverifiable", f"HTTP {status}")
        return ("Warning", "redirect-loop",
                f"redirect chain exceeds {cfg.max_redirects} hops")

    last_reason = "no response"
    for n in range(cfg.retries + 1):
        try:
            res = attempt()
            if res is not None:
                return res
            last_reason = "server error (5xx)"
        except urllib.error.URLError as e:
            reason = getattr(e, "reason", e)
            if isinstance(reason, (socket.gaierror,)):
                return ("Critical", "dead", "DNS resolution failed")
            if isinstance(reason, ConnectionRefusedError):
                return ("Critical", "dead", "connection refused")
            last_reason = f"{type(reason).__name__}: {reason}"
        except (socket.timeout, TimeoutError):
            last_reason = "timeout"
        except (ssl.SSLError, ConnectionError, OSError) as e:
            last_reason = f"{type(e).__name__}"
        if n < cfg.retries:
            time.sleep(0.5 * (n + 1))
    return ("Warning", "transient", f"transient ({last_reason}); presumed live")


def _follow_final(url: str, cfg: Config) -> int | None:
    current, hops = url, 0
    try:
        while hops <= cfg.max_redirects:
            status, location = _one_request(current, "HEAD", cfg.timeout)
            if 300 <= status < 400 and location:
                current = urllib.parse.urljoin(current, location)
                hops += 1
                continue
            return status
    except Exception:
        return None
    return None


def _soft(host: str, cfg: Config) -> bool:
    h = host.lower()
    return any(h == s or h.endswith("." + s) for s in cfg.soft_403)


def probe_all(links: list[Link], cfg: Config) -> list[Finding]:
    """Probe unique external URLs concurrently, with per-host throttling."""
    findings: list[Finding] = []
    by_url: dict[str, list[Link]] = {}
    for ln in links:
        by_url.setdefault(ln.target, []).append(ln)

    # Up-front, offline quality + local-host checks (no network needed).
    for url, occ in by_url.items():
        host = urllib.parse.urlsplit(url).hostname or ""
        lf = local_host_finding(occ[0], host)
        if lf:
            for ln in occ:
                findings.append(Finding("Warning", ln.path, ln.line, url,
                                        "external", lf.reason))
        for ln in occ:
            findings.extend(quality_findings(ln))

    host_lock: dict[str, threading.Lock] = {}
    host_last: dict[str, float] = {}
    glock = threading.Lock()

    def throttled_probe(url: str) -> tuple[str, tuple[str, str, str]]:
        host = urllib.parse.urlsplit(url).hostname or ""
        if host.lower() in LOCAL_HOSTS or url.lower().startswith("file:"):
            return url, ("ok", "skipped", "local/non-portable; not probed")
        with glock:
            lock = host_lock.setdefault(host, threading.Lock())
        with lock:
            wait = cfg.per_host_delay - (time.monotonic()
                                         - host_last.get(host, 0))
            if wait > 0:
                time.sleep(wait)
            result = probe(url, cfg)
            host_last[host] = time.monotonic()
        return url, result

    probe_urls = [u for u in by_url
                  if not (urllib.parse.urlsplit(u).hostname or "").lower()
                  in LOCAL_HOSTS and not u.lower().startswith("file:")]
    with concurrent.futures.ThreadPoolExecutor(max_workers=cfg.concurrency) as ex:
        for url, (sev, cls, reason) in ex.map(throttled_probe, probe_urls):
            if sev == "ok":
                continue
            for ln in by_url[url]:
                findings.append(Finding(sev, ln.path, ln.line, url,
                                        "external", reason))
    return findings


# --------------------------------------------------------------------------- #
# Ignore handling
# --------------------------------------------------------------------------- #
def is_ignored(f: Finding, cfg: Config, ignored_lines: dict) -> bool:
    if f.line in ignored_lines.get(f.path, set()):
        return True
    return any(fnmatch.fnmatch(f.target, pat) for pat in cfg.ignore)


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #
def run(repo: Path, targets: list[str], offline: bool,
        classes: set[str], cfg: Config) -> tuple[list[Finding], list[Finding]]:
    files = scope_files(repo, targets)
    docs_dir = discover_docs_dir(repo)
    internal_findings: list[Finding] = []
    external_links: list[Link] = []
    ignored_lines: dict[str, set[int]] = {}
    slug_cache: dict[Path, set[str] | None] = {}

    for fp in files:
        rel = str(fp.relative_to(repo))
        links, own_slugs, ig = extract(fp, rel, docs_dir)
        ignored_lines[rel] = ig
        for link in links:
            cls = classify(link.target)
            if cls == "external":
                if "external" in classes:
                    external_links.append(link)
            elif cls == "scheme":
                sf = scheme_finding(link)
                if sf:
                    internal_findings.append(sf)
            else:  # anchor / internal / cross-tree
                if "internal" not in classes and "cross-tree" not in classes:
                    continue
                f = resolve_offline(repo, fp, link, own_slugs, slug_cache,
                                    docs_dir)
                if f is None:
                    continue
                if f.cls == "cross-tree" and "cross-tree" not in classes:
                    continue
                if f.cls in ("internal", "anchor") and "internal" not in classes:
                    continue
                internal_findings.append(f)

    external_findings: list[Finding] = []
    if not offline and external_links and "external" in classes:
        external_findings = probe_all(external_links, cfg)

    all_findings = internal_findings + external_findings
    kept, ignored = [], []
    for f in all_findings:
        (ignored if is_ignored(f, cfg, ignored_lines) else kept).append(f)
    kept.sort(key=lambda x: (-SEVERITY_ORDER[x.severity], x.path, x.line,
                             x.target))
    return kept, ignored


def emit_text(kept: list[Finding], ignored: list[Finding], offline: bool) -> None:
    counts = {"Critical": 0, "Warning": 0, "Info": 0}
    for f in kept:
        print(f.as_line())
        counts[f.severity] += 1
    mode = "offline" if offline else "online"
    print(f"\n[{mode}] {counts['Critical']} critical, "
          f"{counts['Warning']} warning, {counts['Info']} info; "
          f"{len(ignored)} ignored")
    if ignored:
        print("Ignored (suppressed, not failing):")
        for f in ignored:
            print(f"  - {f.path}:{f.line} {f.target} — {f.reason}")


def emit_json(kept: list[Finding], ignored: list[Finding], offline: bool) -> None:
    summary: dict = {"Critical": 0, "Warning": 0, "Info": 0}
    per_class: dict = {}
    for f in kept:
        summary[f.severity] += 1
        per_class.setdefault(f.cls, {"Critical": 0, "Warning": 0, "Info": 0})
        per_class[f.cls][f.severity] += 1
    print(json.dumps({
        "mode": "offline" if offline else "online",
        "summary": summary,
        "per_class": per_class,
        "findings": [f.as_dict() for f in kept],
        "ignored": [f.as_dict() for f in ignored],
    }, indent=2, ensure_ascii=False))


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Deterministic documentation link checker.")
    ap.add_argument("targets", nargs="*", help="files/dirs to narrow scope")
    ap.add_argument("--offline", action="store_true",
                    help="internal + anchor + cross-tree only; no network")
    ap.add_argument("--internal", action="store_true",
                    help="check internal + intra-page-anchor links")
    ap.add_argument("--cross-tree", action="store_true",
                    help="check cross-tree references")
    ap.add_argument("--external", action="store_true",
                    help="check external http(s) links")
    ap.add_argument("--format", choices=("text", "json"), default="text")
    ap.add_argument("--fail-on", choices=("critical", "warning", "info"),
                    default=None, help="severity floor that yields exit 1")
    ap.add_argument("--repo", default=str(REPO), help="repository root")
    args = ap.parse_args(argv)

    repo = Path(args.repo).resolve()
    try:
        cfg = load_config(repo)
    except (RuntimeError, ValueError) as e:
        print(f"Critical: config error — {e}", file=sys.stderr)
        return 2

    # Class selection: explicit flags win; otherwise everything (minus
    # external when --offline).
    explicit = args.internal or args.cross_tree or args.external
    if explicit:
        classes = set()
        if args.internal:
            classes.add("internal")
        if args.cross_tree:
            classes.add("cross-tree")
        if args.external:
            classes.add("external")
    else:
        classes = {"internal", "cross-tree", "external"}
    offline = args.offline or not ({"external"} & classes)
    if offline:
        classes.discard("external")

    fail_on = (args.fail_on or cfg.fail_on or "critical").capitalize()
    floor = SEVERITY_ORDER.get(fail_on, 2)

    try:
        kept, ignored = run(repo, args.targets, offline, classes, cfg)
    except OSError as e:
        print(f"Critical: {e}", file=sys.stderr)
        return 2

    if args.format == "json":
        emit_json(kept, ignored, offline)
    else:
        emit_text(kept, ignored, offline)

    return 1 if any(SEVERITY_ORDER[f.severity] >= floor for f in kept) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
