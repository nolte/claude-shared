"""Unit tests for skills/image-generate/scripts/image_generate.py.

No real network calls: every test that exercises a provider mocks
`urllib.request.urlopen`. Covers the shared layer plus the three MVP providers
(cloudflare, pollinations, gemini).
"""
from __future__ import annotations

import base64
import json
import re
import sys
import urllib.error
from io import BytesIO
from pathlib import Path
from unittest import mock

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "skills" / "image-generate" / "scripts"
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
