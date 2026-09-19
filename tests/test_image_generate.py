"""Unit tests for plugins/nolte-media/skills/image-generate/scripts/image_generate.py.

No real network calls: every test that exercises a provider mocks
`urllib.request.urlopen`. Covers the shared layer plus the three MVP providers
(cloudflare, pollinations, gemini).
"""
from __future__ import annotations

import base64
import hashlib
import json
import re
import sys
import urllib.error
from email import policy
from email.parser import BytesParser
from io import BytesIO
from pathlib import Path
from unittest import mock

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "plugins" / "nolte-media" / "skills" / "image-generate" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import image_generate as ig  # noqa: E402

SCRIPT_PATH = SCRIPTS / "image_generate.py"
JPEG = b"\xff\xd8\xff-fake-jpeg"
PNG = b"\x89PNG-fake"


# --------------------------------------------------------------------------- #
# Fakes
# --------------------------------------------------------------------------- #
class _Headers:
    def __init__(self, ct: str) -> None:
        self._ct = ct

    def get_content_type(self) -> str:
        return self._ct


class _FakeResp:
    def __init__(self, payload: bytes, content_type: str = "application/json") -> None:
        self._payload = payload
        self.headers = _Headers(content_type)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self) -> bytes:
        return self._payload


def cloudflare_json(img: bytes = JPEG) -> _FakeResp:
    body = {"result": {"image": base64.b64encode(img).decode()}, "success": True, "errors": []}
    return _FakeResp(json.dumps(body).encode(), "application/json")


def gemini_json(img: bytes = PNG, mime: str = "image/png", n: int = 1) -> _FakeResp:
    part = {"inlineData": {"mimeType": mime, "data": base64.b64encode(img).decode()}}
    cands = [{"content": {"parts": [part]}} for _ in range(n)]
    return _FakeResp(json.dumps({"candidates": cands}).encode(), "application/json")


def pollinations_bytes(img: bytes = JPEG) -> _FakeResp:
    return _FakeResp(img, "image/jpeg")


def http_error(code: int, body: str = "") -> urllib.error.HTTPError:
    fp = BytesIO(body.encode()) if body else None
    return urllib.error.HTTPError("https://x", code, "err", {}, fp)


def executable_source() -> str:
    src = SCRIPT_PATH.read_text(encoding="utf-8")
    src = re.sub(r'""".*?"""', "", src, count=1, flags=re.DOTALL)
    src = re.sub(r"(?m)^\s*#.*$", "", src)
    return src


@pytest.fixture
def state(tmp_path, monkeypatch):
    """Isolate the consent-ack directory; return the tmp working dir."""
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    return tmp_path


@pytest.fixture
def cf_env(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "cf-token-xyz")
    monkeypatch.setenv("CLOUDFLARE_ACCOUNT_ID", "acct-123")


@pytest.fixture
def gemini_env(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "gem-key-xyz")


def run(argv, response=None):
    with mock.patch("urllib.request.urlopen") as m:
        if response is not None:
            m.return_value = response
        code = ig.main(argv)
    return code, m


# --------------------------------------------------------------------------- #
# Shared layer
# --------------------------------------------------------------------------- #
def test_default_provider_is_cloudflare():
    assert ig.DEFAULT_PROVIDER == "cloudflare"
    assert set(ig.PROVIDERS) == {"cloudflare", "pollinations", "gemini"}


def test_no_paid_or_vertex_strings_in_executable():
    code = executable_source().lower()
    assert "imagen" not in code
    assert "aiplatform" not in code


def test_missing_out_is_usage_error():
    with pytest.raises(SystemExit) as exc:
        ig.main(["--prompt", "x"])
    assert exc.value.code == 2


def test_unknown_provider_rejected():
    with pytest.raises(SystemExit) as exc:
        ig.main(["--provider", "midjourney", "--prompt", "x", "--out", "/tmp/x.png"])
    assert exc.value.code == 2


# --------------------------------------------------------------------------- #
# Cloudflare (default provider)
# --------------------------------------------------------------------------- #
def test_cloudflare_writes_image_and_sidecar(state, cf_env):
    out = state / "hero.png"
    code, _ = run(["--prompt", "a fox", "--out", str(out)], cloudflare_json())
    assert code == 0
    assert out.read_bytes() == JPEG
    meta = json.loads((state / "hero.png.meta.json").read_text())
    assert meta["provider"] == "cloudflare"
    assert meta["model"] == "@cf/black-forest-labs/flux-1-schnell"
    assert meta["prompt"] == "a fox"
    assert set(meta) == {"provider", "model", "source", "prompt", "timestamp", "mime_type"}


def test_cloudflare_missing_creds_setup_hint(state, monkeypatch, capsys):
    monkeypatch.delenv("CLOUDFLARE_API_TOKEN", raising=False)
    monkeypatch.delenv("CLOUDFLARE_ACCOUNT_ID", raising=False)
    code, m = run(["--prompt", "x", "--out", str(state / "x.png")])
    assert code != 0
    assert m.call_count == 0  # never hit the network
    err = capsys.readouterr().err
    assert "CLOUDFLARE_API_TOKEN" in err
    assert "CLOUDFLARE_ACCOUNT_ID" in err
    assert "neurons" in err.lower()


def test_cloudflare_no_consent_notice(state, cf_env):
    # Cloudflare has a clear licence → no one-time notice, no ack file.
    run(["--prompt", "x", "--out", str(state / "x.png")], cloudflare_json())
    assert not ig.ack_path("cloudflare").exists()


def test_no_credentials_leak_into_sidecar_or_stderr(state, cf_env, capsys):
    # Credential-handling regression guard: neither the token nor the account id
    # may appear in the sidecar or the operator-facing output.
    img = state / "x.png"
    run(["--prompt", "a secret subject", "--out", str(img)], cloudflare_json())
    err = capsys.readouterr().err
    sidecar = (state / "x.png.meta.json").read_text()
    for secret in ("cf-token-xyz", "acct-123"):
        assert secret not in sidecar
        assert secret not in err


def test_cloudflare_uses_flux_optimal_steps(state, cf_env):
    # FLUX.1-schnell is optimal at 1-4 steps (spec/design/flux-image-generation/);
    # 8 is only Cloudflare's hard cap. Guard against regressing back to the cap.
    code, m = run(["--prompt", "x", "--out", str(state / "x.png")], cloudflare_json())
    assert code == 0
    sent = json.loads(m.call_args.args[0].data)
    assert sent["steps"] == 4


def test_cloudflare_n_images(state, cf_env):
    with mock.patch("urllib.request.urlopen", side_effect=[cloudflare_json(), cloudflare_json()]):
        code = ig.main(["--prompt", "p", "-n", "2", "--out", str(state / "x.png")])
    assert code == 0
    assert sorted(p.name for p in state.glob("x-*.png")) == ["x-1.png", "x-2.png"]


# --------------------------------------------------------------------------- #
# Pollinations (forced private=true, disclaimer)
# --------------------------------------------------------------------------- #
def test_pollinations_forces_private_true(state):
    # The load-bearing privacy guard: the request URL MUST carry private=true.
    code, m = run(
        ["--provider", "pollinations", "--prompt", "a tree", "--out", str(state / "t.png"),
         "--accept-data-policy"],
        pollinations_bytes(),
    )
    assert code == 0
    called_url = m.call_args.args[0].full_url
    assert "private=true" in called_url
    assert "image.pollinations.ai/prompt/" in called_url


def test_pollinations_disclaimer_mentions_feed_and_licence(state, capsys):
    run(["--provider", "pollinations", "--prompt", "x", "--out", str(state / "x.png"),
         "--accept-data-policy"], pollinations_bytes())
    err = capsys.readouterr().err
    assert "public feed" in err.lower()
    assert "licence" in err.lower() or "license" in err.lower()
    assert "myceli" in err.lower()  # operating legal entity named (GDPR)
    assert "model" in err.lower()  # output rights deferred to the model licence


def test_pollinations_writes_binary_and_needs_no_auth(state):
    out = state / "t.png"
    code, _ = run(["--provider", "pollinations", "--prompt", "x", "--out", str(out),
                   "--accept-data-policy"], pollinations_bytes())
    assert code == 0
    assert out.read_bytes() == JPEG
    assert json.loads((state / "t.png.meta.json").read_text())["provider"] == "pollinations"


def test_pollinations_sidecar_says_the_model_variant_is_undisclosed(state):
    # #592 / F37: `flux` is a Pollinations alias, so the sidecar can't name the licensed variant.
    run(["--provider", "pollinations", "--prompt", "x", "--out", str(state / "t.png"),
         "--accept-data-policy"], pollinations_bytes())
    meta = json.loads((state / "t.png.meta.json").read_text())
    assert meta["model"] == "flux" and "variant" in meta["model_variant_note"]


def test_cloudflare_sidecar_names_the_concrete_model_without_a_note(state, cf_env):
    run(["--provider", "cloudflare", "--prompt", "x", "--out", str(state / "c.png")], cloudflare_json())
    meta = json.loads((state / "c.png.meta.json").read_text())
    assert meta["model"] == "@cf/black-forest-labs/flux-1-schnell" and "model_variant_note" not in meta


def test_pollinations_rejects_non_image_response(state):
    code, _ = run(["--provider", "pollinations", "--prompt", "x", "--out", str(state / "x.png"),
                   "--accept-data-policy"], _FakeResp(b"<html>error</html>", "text/html"))
    assert code != 0


# --------------------------------------------------------------------------- #
# Gemini (billing-required, error-body surfacing from #240)
# --------------------------------------------------------------------------- #
def test_gemini_inlinedata_image(state, gemini_env):
    out = state / "g.png"
    code, _ = run(["--provider", "gemini", "--prompt", "x", "--out", str(out),
                   "--accept-data-policy"], gemini_json())
    assert code == 0
    assert out.read_bytes() == PNG
    assert json.loads((state / "g.png.meta.json").read_text())["provider"] == "gemini"


def test_gemini_missing_key_setup_hint(state, monkeypatch, capsys):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    code, _ = run(["--provider", "gemini", "--prompt", "x", "--out", str(state / "x.png"),
                   "--accept-data-policy"])
    assert code != 0
    err = capsys.readouterr().err
    assert "GEMINI_API_KEY" in err
    assert "billing" in err.lower()


def test_gemini_zero_quota_reports_billing(state, gemini_env, capsys):
    body = json.dumps({"error": {"message": "Quota exceeded ... limit: 0, model: x",
                                  "status": "RESOURCE_EXHAUSTED"}})
    with mock.patch("urllib.request.urlopen", side_effect=http_error(429, body)):
        code = ig.main(["--provider", "gemini", "--prompt", "x", "--out", str(state / "x.png"),
                        "--accept-data-policy"])
    assert code == ig.EXIT_RATE_LIMIT
    err = capsys.readouterr().err
    assert "billing" in err.lower()
    assert "limit: 0" in err


def test_gemini_notice_mentions_billing(state, gemini_env, capsys):
    run(["--provider", "gemini", "--prompt", "x", "--out", str(state / "x.png"),
         "--accept-data-policy"], gemini_json())
    assert "billing" in capsys.readouterr().err.lower()


# --------------------------------------------------------------------------- #
# Consent mechanics (per-provider keyed, digest-versioned)
# --------------------------------------------------------------------------- #
def test_consent_ack_is_per_provider_keyed(state):
    assert "pollinations" in str(ig.ack_path("pollinations"))
    assert "gemini" in str(ig.ack_path("gemini"))
    assert ig.ack_path("pollinations") != ig.ack_path("gemini")


def test_consent_noninteractive_without_flag_aborts(state, monkeypatch):
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    code, _ = run(["--provider", "pollinations", "--prompt", "x", "--out", str(state / "x.png")],
                  pollinations_bytes())
    assert code != 0
    assert not (state / "x.png").exists()


def test_consent_digest_versioned(state):
    ig.ack_path("pollinations").parent.mkdir(parents=True, exist_ok=True)
    ig.ack_path("pollinations").write_text("deadbeef\n")
    code, _ = run(["--provider", "pollinations", "--prompt", "x", "--out", str(state / "x.png"),
                   "--accept-data-policy"], pollinations_bytes())
    assert code == 0
    stored = ig.ack_path("pollinations").read_text().strip()
    assert re.fullmatch(r"[0-9a-f]{64}", stored)  # rewritten with the real digest


# --------------------------------------------------------------------------- #
# Shared output behaviour
# --------------------------------------------------------------------------- #
def test_overwrite_guard(state, cf_env):
    out = state / "x.png"
    out.write_bytes(b"orig")
    code, m = run(["--prompt", "x", "--out", str(out)])
    assert code != 0
    assert m.call_count == 0
    assert out.read_bytes() == b"orig"


def test_extension_mime_mismatch_warns_but_writes(state, cf_env, capsys):
    out = state / "x.webp"  # cloudflare returns image/jpeg
    code, _ = run(["--prompt", "x", "--out", str(out)], cloudflare_json())
    assert code == 0
    assert out.exists()
    assert "warning" in capsys.readouterr().err.lower()


def test_error_body_surfaced_generic(state, cf_env, capsys):
    body = json.dumps({"error": {"message": "Specific upstream failure", "status": "INTERNAL"}})
    with mock.patch("urllib.request.urlopen", side_effect=http_error(500, body)):
        code = ig.main(["--prompt", "x", "--out", str(state / "x.png")])
    assert code == ig.EXIT_ERROR
    assert "Specific upstream failure" in capsys.readouterr().err


# --------------------------------------------------------------------------- #
# Prompt resolution (graphic-prompt-generator pipeline glue)
# --------------------------------------------------------------------------- #
DOC = (
    "# Graphic Prompt: Fox\n\n"
    "## Prompt — Light Mode\n```\nteal fox on white\n```\n\n"
    "## Prompt — Dark Mode\n```\nteal fox on charcoal\n```\n"
)


def test_extract_variant_from_prompt_doc():
    assert ig.extract_prompt_from_doc(DOC, "dark") == "teal fox on charcoal"


def test_from_prompt_doc_end_to_end(state, cf_env):
    doc = state / "fox.md"
    doc.write_text(DOC)
    code, _ = run(["--from-prompt-doc", str(doc), "--variant", "light", "--out", str(state / "x.png")],
                  cloudflare_json())
    assert code == 0
    assert json.loads((state / "x.png.meta.json").read_text())["prompt"] == "teal fox on white"


# --------------------------------------------------------------------------- #
# Gemini request shape (#581 migration). A billed call can't run in CI, so the
# request itself is the thing to pin: these fail against the retired 2.5 pin,
# against a `-preview` pin, and against a plain call that carries a
# generationConfig the documented minimal v1 call doesn't send.
# --------------------------------------------------------------------------- #
def _sent_request(m):
    req = m.call_args[0][0]
    return req.full_url, json.loads(req.data)


def test_gemini_request_targets_stable_v1_endpoint(state, gemini_env):
    code, m = run(["--provider", "gemini", "--prompt", "x", "--out", str(state / "g.png"),
                   "--accept-data-policy"], gemini_json())
    assert code == 0
    url, _ = _sent_request(m)
    assert url == "https://generativelanguage.googleapis.com/v1/models/gemini-3.1-flash-image:generateContent"
    assert "preview" not in url
    assert "v1beta" not in url


def test_gemini_plain_call_sends_contents_only(state, gemini_env):
    code, m = run(["--provider", "gemini", "--prompt", "a teal fox", "--out", str(state / "g.png"),
                   "--accept-data-policy"], gemini_json())
    assert code == 0
    _, body = _sent_request(m)
    assert body == {"contents": [{"parts": [{"text": "a teal fox"}]}]}
    assert "generationConfig" not in body


def test_gemini_seed_adds_only_the_requested_config(state, gemini_env):
    code, m = run(["--provider", "gemini", "--prompt", "x", "--out", str(state / "g.png"),
                   "--seed", "7", "--accept-data-policy"], gemini_json())
    assert code == 0
    _, body = _sent_request(m)
    assert body["generationConfig"] == {"seed": 7}


# --------------------------------------------------------------------------- #
# Documented flags must exist. Class guard for the `--n` slip in the #596 specs.
# A flag counts as documented when it sits where an operator would copy it from:
#   - anywhere in the repo, a fenced command that invokes the script, with
#     backslash continuations joined so a flag on a later line is still seen,
#     or an inline code span that names the script;
#   - in the tool's own docs, any inline span that starts with a flag, such as
#     `-n <N>`.
# Inline spans for other programs (`claude --plugin-dir .`) are not checked.
# The defined set comes from build_parser(), so aliases count.
# --------------------------------------------------------------------------- #
import subprocess

REPO = Path(__file__).resolve().parent.parent
TOOL_DOC_GLOBS = (
    "plugins/nolte-media/skills/image-generate/**/*.md",
    "plugins/nolte-media/skills/gemini-image-handoff/**/*.md",
    "spec/tools/image-generation/*.md",
    "spec/design/gemini-image-generation/*.md",
    "docs/*/guides/image-generation.md",
)
_FLAG = re.compile(r"(?<![\w/.=-])(--[a-z][a-z0-9-]*|-[a-zA-Z])(?![\w-])")
_INLINE = re.compile(r"`([^`\n]+)`")
_INVOKES = re.compile(r"image_generate\.py|image:generate")


def _option_strings(parser) -> set[str]:
    # Every name each action answers to, aliases included.
    return {name for action in parser._actions for name in action.option_strings}


def _tool_docs() -> set[str]:
    return {p.relative_to(REPO).as_posix() for g in TOOL_DOC_GLOBS for p in REPO.glob(g)}


def _checked_contexts(rel_path, text, tool_docs):
    in_fence, command, start = False, "", 0
    for lineno, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("```"):
            if in_fence and command and _INVOKES.search(command):
                yield start, command
            in_fence, command = not in_fence, ""
            continue
        if in_fence:
            if not command:
                start = lineno
            stripped = line.rstrip()
            if stripped.endswith("\\"):
                command += stripped[:-1] + " "
                continue
            command += stripped
            if _INVOKES.search(command):
                yield start, command
            command = ""
            continue
        for span in _INLINE.findall(line):
            if _INVOKES.search(span) or (rel_path in tool_docs and span.lstrip().startswith("-")):
                yield lineno, span


def _unknown_flags(rel_path, text, defined, tool_docs):
    return [
        f"{rel_path}:{lineno}: {token}"
        for lineno, context in _checked_contexts(rel_path, text, tool_docs)
        for token in _FLAG.findall(context)
        if token not in defined
    ]


def test_documented_flags_exist_in_parser():
    tracked = subprocess.run(
        ["git", "ls-files", "*.md"], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.split()
    docs = [p for p in tracked if not p.startswith(".audits/")]
    assert docs, "git ls-files found no Markdown, so the guard would check nothing"
    orphaned = [g for g in TOOL_DOC_GLOBS if not any(REPO.glob(g))]
    assert not orphaned, f"tool-doc globs that match nothing, so their files would go unchecked: {orphaned}"
    tool_docs = _tool_docs()
    defined = _option_strings(ig.build_parser())
    unknown = [
        u for p in docs for u in _unknown_flags(p, (REPO / p).read_text(encoding="utf-8"), defined, tool_docs)
    ]
    assert not unknown, "documented flags the parser does not define:\n" + "\n".join(unknown)


_DEFINED = {"-h", "--help", "-n", "--prompt", "--out", "--provider"}
_TOOL_DOC = "spec/tools/image-generation/en.md"


def test_flag_guard_flags_a_bare_single_letter_long_flag():
    # The first draft required two characters after `--` and missed `--n` itself.
    assert _unknown_flags(_TOOL_DOC, "pass `--n` for more", _DEFINED, {_TOOL_DOC}) == [f"{_TOOL_DOC}:1: --n"]


def test_flag_guard_reads_flags_on_continuation_lines():
    text = "```bash\npython3 scripts/image_generate.py \\\n    --prompt x \\\n    --n 3\n```\n"
    assert _unknown_flags("README.md", text, _DEFINED, set()) == ["README.md:2: --n"]


def test_flag_guard_checks_an_inline_flag_with_its_argument():
    assert _unknown_flags(_TOOL_DOC, "use `-n <N>` here", _DEFINED, {_TOOL_DOC}) == []
    assert _unknown_flags(_TOOL_DOC, "use `--n <N>` here", _DEFINED, {_TOOL_DOC}) == [f"{_TOOL_DOC}:1: --n"]


def test_flag_guard_ignores_other_programs():
    assert _unknown_flags(_TOOL_DOC, "run `claude --plugin-dir .` first", _DEFINED, {_TOOL_DOC}) == []
    assert _unknown_flags("CLAUDE.md", "`--resume` resumes a session", _DEFINED, set()) == []


def test_flag_guard_counts_aliases():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--out")
    assert {"-o", "--out"} <= _option_strings(parser)


# --------------------------------------------------------------------------- #
# Cloudflare model selection (#638): FLUX.2 [klein] 4B via --model. The klein-4b
# endpoint takes multipart/form-data only and fixes steps server-side, so the
# request shape is the thing to pin; the schnell path must stay byte-identical.
# --------------------------------------------------------------------------- #
KLEIN = ["--model", "flux-2-klein-4b"]
KLEIN_ID = "@cf/black-forest-labs/flux-2-klein-4b"


def _multipart(m, call: int = 0):
    """Return (url, content_type, {part_name: {"headers": str, "body": bytes}}).

    Asserts RFC 2046 framing byte for byte on the way through — a dropped CRLF, a
    missing blank line after a header block, or a missing closing delimiter fails
    here rather than silently producing a body Cloudflare would reject.
    """
    req = m.call_args_list[call].args[0]
    ctype = req.get_header("Content-type")
    boundary = ctype.split("boundary=", 1)[1]
    body, marker = req.data, b"--" + boundary.encode()

    assert body.startswith(marker + b"\r\n"), "body must open with the first delimiter"
    assert body.endswith(marker + b"--\r\n"), "body must end with the closing delimiter"
    idx = body.find(marker, 1)
    while idx != -1:
        assert body[idx - 2:idx] == b"\r\n", f"delimiter at offset {idx} not preceded by CRLF"
        idx = body.find(marker, idx + len(marker))

    parts = {}
    for chunk in body.split(marker):
        if not chunk.strip(b"-\r\n"):
            continue
        head, sep, raw = chunk.lstrip(b"\r\n").partition(b"\r\n\r\n")
        assert sep == b"\r\n\r\n", f"header block not terminated by a blank line: {head!r}"
        assert raw.endswith(b"\r\n"), "part payload must be followed by CRLF"
        name = re.search(r'name="([^"]+)"', head.decode()).group(1)
        parts[name] = {"headers": head.decode(), "body": raw[:-2]}

    # Cross-check with a real MIME parser: escaping and framing must survive it.
    parsed = BytesParser(policy=policy.default).parsebytes(
        b"Content-Type: " + ctype.encode() + b"\r\n\r\n" + body
    )
    assert parsed.is_multipart(), "a real MIME parser must see a multipart body"
    seen = {}
    for part in parsed.iter_parts():
        name = part.get_param("name", header="content-disposition")
        seen[name] = {"filename": part.get_filename(), "body": part.get_payload(decode=True)}
    assert set(seen) == set(parts), f"parser saw {sorted(seen)}, splitter saw {sorted(parts)}"
    for name, got in seen.items():
        assert got["body"] == parts[name]["body"], f"payload mismatch for part {name!r}"
        if got["filename"] is not None:
            parts[name]["filename"] = got["filename"]
    return req.full_url, ctype, parts


def test_cloudflare_klein_sends_multipart_with_size_and_no_steps(state, cf_env):
    out = state / "k.png"
    code, m = run(["--prompt", "a fox", "--out", str(out), "--width", "1280", "--height", "720"] + KLEIN,
                  cloudflare_json(PNG))
    assert code == 0
    url, ctype, parts = _multipart(m)
    assert ctype.startswith("multipart/form-data; boundary=")
    assert url.endswith("/ai/run/" + KLEIN_ID)
    assert parts["prompt"]["body"] == b"a fox"
    assert parts["width"]["body"] == b"1280"
    assert parts["height"]["body"] == b"720"
    assert "steps" not in parts  # the endpoint fixes steps at 4; sending it is rejected
    assert b'name="steps"' not in m.call_args.args[0].data
    assert json.loads((state / "k.png.meta.json").read_text())["model"] == KLEIN_ID


def test_cloudflare_klein_accepts_base64_json_response(state, cf_env):
    out = state / "k.png"
    code, _ = run(["--prompt", "x", "--out", str(out)] + KLEIN, cloudflare_json(PNG))
    assert code == 0
    assert out.read_bytes() == PNG
    assert json.loads((state / "k.png.meta.json").read_text())["mime_type"] == "image/png"


def test_cloudflare_klein_accepts_raw_image_bytes_response(state, cf_env):
    out = state / "k.png"
    code, _ = run(["--prompt", "x", "--out", str(out)] + KLEIN, _FakeResp(PNG, "image/png"))
    assert code == 0
    assert out.read_bytes() == PNG
    assert json.loads((state / "k.png.meta.json").read_text())["mime_type"] == "image/png"


def test_cloudflare_without_model_keeps_the_schnell_json_body(state, cf_env):
    code, m = run(["--prompt", "a fox", "--out", str(state / "s.png")], cloudflare_json())
    assert code == 0
    req = m.call_args.args[0]
    assert req.get_header("Content-type") == "application/json"
    assert json.loads(req.data) == {"prompt": "a fox", "steps": 4}
    assert json.loads((state / "s.png.meta.json").read_text())["model"] == "@cf/black-forest-labs/flux-1-schnell"


def test_unknown_model_is_a_usage_error(state):
    with pytest.raises(SystemExit) as exc:
        ig.main(["--model", "nonsense", "--prompt", "x", "--out", str(state / "x.png")])
    assert exc.value.code == 2


def test_model_on_a_non_cloudflare_provider_is_a_usage_error(state, capsys):
    code, m = run(["--provider", "pollinations", "--prompt", "x", "--out", str(state / "x.png"),
                   "--accept-data-policy"] + KLEIN)
    assert code == ig.EXIT_USAGE
    assert m.call_count == 0
    assert "--model" in capsys.readouterr().err


def test_schnell_warns_that_it_ignores_width_and_height(state, cf_env, capsys):
    code, m = run(["--prompt", "x", "--out", str(state / "s.png"), "--width", "512"], cloudflare_json())
    assert code == 0
    err = capsys.readouterr().err.lower()
    assert "width" in err and "height" in err and "ignore" in err
    assert "width" not in json.loads(m.call_args.args[0].data)


def test_cloudflare_klein_increments_the_seed_per_image(state, cf_env):
    code, m = run(["--prompt", "x", "-n", "2", "--seed", "7", "--out", str(state / "k.png")] + KLEIN,
                  cloudflare_json(PNG))
    assert code == 0
    assert m.call_count == 2
    assert [_multipart(m, i)[2]["seed"]["body"] for i in (0, 1)] == [b"7", b"8"]


def _ref_files(state):
    (state / "a.png").write_bytes(PNG)
    (state / "b.jpg").write_bytes(JPEG)
    return str(state / "a.png"), str(state / "b.jpg")


def test_cloudflare_klein_uploads_reference_images_and_records_their_digests(state, cf_env):
    a, b = _ref_files(state)
    code, m = run(["--prompt", "x", "--out", str(state / "k.png"),
                   "--ref-image", a, "--ref-image", b] + KLEIN, cloudflare_json(PNG))
    assert code == 0
    _, _, parts = _multipart(m)
    assert parts["input_image_0"]["body"] == PNG
    assert 'filename="a.png"' in parts["input_image_0"]["headers"]
    assert "Content-Type: image/png" in parts["input_image_0"]["headers"]
    assert parts["input_image_1"]["body"] == JPEG
    assert 'filename="b.jpg"' in parts["input_image_1"]["headers"]
    assert "Content-Type: image/jpeg" in parts["input_image_1"]["headers"]
    refs = json.loads((state / "k.png.meta.json").read_text())["reference_images"]
    assert refs == [
        {"name": "a.png", "sha256": hashlib.sha256(PNG).hexdigest()},
        {"name": "b.jpg", "sha256": hashlib.sha256(JPEG).hexdigest()},
    ]
    assert not any("/" in r["name"] for r in refs)  # basenames only, never a path


def test_ref_image_on_schnell_is_a_usage_error(state, cf_env, capsys):
    a, _ = _ref_files(state)
    code, m = run(["--prompt", "x", "--out", str(state / "x.png"), "--ref-image", a])
    assert code == ig.EXIT_USAGE
    assert m.call_count == 0
    assert "flux-2-klein-4b" in capsys.readouterr().err


def test_ref_image_on_another_provider_is_a_usage_error(state):
    a, _ = _ref_files(state)
    code, m = run(["--provider", "pollinations", "--prompt", "x", "--out", str(state / "x.png"),
                   "--accept-data-policy", "--ref-image", a])
    assert code == ig.EXIT_USAGE
    assert m.call_count == 0


def test_more_than_four_ref_images_is_a_usage_error(state, cf_env):
    a, _ = _ref_files(state)
    argv = ["--prompt", "x", "--out", str(state / "x.png")] + KLEIN
    for _ in range(5):
        argv += ["--ref-image", a]
    code, m = run(argv)
    assert code == ig.EXIT_USAGE
    assert m.call_count == 0


def test_unreadable_ref_image_is_a_runtime_error_before_the_call(state, cf_env):
    code, m = run(["--prompt", "x", "--out", str(state / "x.png"),
                   "--ref-image", str(state / "missing.png")] + KLEIN)
    assert code == ig.EXIT_ERROR
    assert m.call_count == 0


def test_no_credentials_leak_into_a_klein_multipart_body(state, cf_env, capsys):
    a, _ = _ref_files(state)
    code, m = run(["--prompt", "a secret subject", "--out", str(state / "k.png"),
                   "--ref-image", a] + KLEIN, cloudflare_json(PNG))
    assert code == 0
    body = m.call_args.args[0].data
    err = capsys.readouterr().err
    sidecar = (state / "k.png.meta.json").read_text()
    for secret in (b"cf-token-xyz", b"acct-123"):
        assert secret not in body  # the token travels in the Authorization header only
        assert secret.decode() not in sidecar
        assert secret.decode() not in err


# --------------------------------------------------------------------------- #
# Reference-image filename handling (SCR-001/SEC-001): a basename is attacker-
# influenced input that lands in a Content-Disposition header, so it must be
# escaped there while the sidecar keeps the untouched original.
# --------------------------------------------------------------------------- #
def _hostile_ref_image(state):
    """Create a ref image whose basename carries a quote (and CR/LF where allowed)."""
    for name in ('a"b\r\nc.png', 'a"b.png'):
        path = state / name
        try:
            path.write_bytes(PNG)
        except OSError:  # filesystem refuses CR/LF in names -> fall back to the quote
            continue
        return path
    raise AssertionError("could not create a reference image with a quote in its name")


def test_ref_image_filename_is_escaped_in_the_part_header(state, cf_env):
    ref = _hostile_ref_image(state)
    code, m = run(["--prompt", "x", "--out", str(state / "k.png"), "--ref-image", str(ref)] + KLEIN,
                  cloudflare_json(PNG))
    assert code == 0
    _, _, parts = _multipart(m)
    head = parts["input_image_0"]["headers"]
    assert '\\"' in head, f"the quote in the filename was not escaped: {head!r}"
    assert '"; filename="' in head  # name= parameter still terminates correctly
    for line in head.split("\r\n"):
        assert "\r" not in line and "\n" not in line
    assert head.count("Content-Disposition:") == 1  # no injected extra header
    # A real MIME parser recovers the sanitized name, not a truncated one.
    assert parts["input_image_0"]["filename"] == ref.name.replace("\r", "").replace("\n", "")
    assert parts["input_image_0"]["body"] == PNG
    refs = json.loads((state / "k.png.meta.json").read_text())["reference_images"]
    assert refs[0]["name"] == ref.name  # the sidecar keeps the original basename


def test_encode_multipart_sanitizes_crlf_in_filename_and_content_type():
    body, _ = ig._encode_multipart({}, [("f", "a\r\nX-Evil: 1\rb.png", "image/png\r\nX-Evil: 2", b"d")])
    head = body.split(b"\r\n\r\n", 1)[0].decode()
    lines = head.split("\r\n")
    assert len(lines) == 3 and lines[0].startswith("--")  # delimiter + exactly two headers
    assert lines[1].startswith('Content-Disposition: form-data; name="f"; filename="')
    assert lines[2] == "Content-Type: image/pngX-Evil: 2"  # CRLF stripped, no third header
    assert "X-Evil: 1" in lines[1]  # kept, but inside the quoted filename


def test_encode_multipart_falls_back_when_the_filename_sanitizes_to_nothing():
    body, _ = ig._encode_multipart({}, [("f", "\r\n", "image/png", b"d")])
    assert b'filename="image"' in body


# --------------------------------------------------------------------------- #
# Klein base64 responses carry no content type, so the sidecar MIME comes from
# magic bytes (SCR-003).
# --------------------------------------------------------------------------- #
WEBP = b"RIFF\x20\x00\x00\x00WEBPVP8 rest"
UNKNOWN = b"\x00\x01\x02not-an-image"


@pytest.mark.parametrize(
    "payload, expected",
    [(JPEG, "image/jpeg"), (WEBP, "image/webp"), (UNKNOWN, "image/png")],
    ids=["jpeg-magic", "webp-magic", "unknown-falls-back-to-png"],
)
def test_cloudflare_klein_sidecar_mime_comes_from_the_magic_bytes(state, cf_env, payload, expected):
    out = state / "k.png"
    code, _ = run(["--prompt", "x", "--out", str(out)] + KLEIN, cloudflare_json(payload))
    assert code == 0
    assert out.read_bytes() == payload
    assert json.loads((state / "k.png.meta.json").read_text())["mime_type"] == expected


# --------------------------------------------------------------------------- #
# Klein error paths (SCR-004/SEC-005): every malformed response shape exits 1
# with a readable message — never an AttributeError traceback.
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "response, expected_fragment",
    [
        (_FakeResp(b"", "image/png"), "no image data"),
        (_FakeResp(b"[1, 2]", "application/json"), "no image data"),
        (_FakeResp(b"<html>gateway</html>", "application/json"), "malformed"),
        (_FakeResp(json.dumps({"result": {"image": "!!!not base64!!!"}}).encode(),
                   "application/json"), "undecodable"),
        (_FakeResp(json.dumps({"result": [1, 2]}).encode(), "application/json"), "no image data"),
    ],
    ids=["empty-image-body", "json-not-an-object", "non-json-json-type",
         "undecodable-base64", "result-not-an-object"],
)
def test_cloudflare_klein_malformed_responses_exit_one_without_a_traceback(
    state, cf_env, capsys, response, expected_fragment
):
    code, _ = run(["--prompt", "x", "--out", str(state / "k.png")] + KLEIN, response)
    assert code == ig.EXIT_ERROR
    err = capsys.readouterr().err
    assert expected_fragment in err.lower()
    assert err.startswith("error: ")
    assert "Traceback" not in err
    assert not (state / "k.png").exists()


def test_schnell_survives_a_result_that_is_not_an_object(state, cf_env, capsys):
    # SEC-005 on the JSON path: `(resp.get("result") or {}).get(...)` used to raise.
    code, _ = run(["--prompt", "x", "--out", str(state / "s.png")],
                  _FakeResp(json.dumps({"result": [1, 2]}).encode(), "application/json"))
    assert code == ig.EXIT_ERROR
    assert "no image data" in capsys.readouterr().err.lower()


def test_klein_gate_uses_the_named_registry_key(state):
    # SCR-005: the --ref-image gate compares against the registry key, not a literal.
    assert ig.CloudflareProvider.KLEIN_MODEL_KEY in ig.CloudflareProvider.MODELS
    assert ig.CloudflareProvider.KLEIN_MODEL == ig.CloudflareProvider.MODELS[
        ig.CloudflareProvider.KLEIN_MODEL_KEY
    ]
