#!/usr/bin/env python3
"""Tests for skills/gemini-image-generate/scripts/gemini_image_generate.py.

One test (or cluster) per Acceptance Criterion in
`spec/tools/gemini-image-generation/`. No real network calls: every test that
exercises the API mocks `urllib.request.urlopen`.
"""
from __future__ import annotations

import base64
import contextlib
import io
import json
import os
import re
import sys
import unittest
import urllib.error
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

SCRIPTS = Path(__file__).resolve().parent.parent / "skills" / "gemini-image-generate" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import gemini_image_generate as gig  # noqa: E402

SCRIPT_PATH = SCRIPTS / "gemini_image_generate.py"


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
class _FakeResponse:
    """Context-manager stand-in for the object urlopen() returns."""

    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, *exc) -> bool:
        return False

    def read(self) -> bytes:
        return self._payload


def image_response(mime: str = "image/png", payload: bytes = b"\x89PNG-fake-bytes", n: int = 1) -> bytes:
    part = {"inlineData": {"mimeType": mime, "data": base64.b64encode(payload).decode()}}
    candidates = [{"content": {"parts": [part]}} for _ in range(n)]
    return json.dumps({"candidates": candidates}).encode()


def http_error(code: int) -> urllib.error.HTTPError:
    return urllib.error.HTTPError("https://x", code, "err", {}, None)


def http_error_with_body(code: int, body: str) -> urllib.error.HTTPError:
    """HTTPError whose .read() returns `body` — mirrors a real Google error payload."""
    return urllib.error.HTTPError("https://x", code, "err", {}, io.BytesIO(body.encode()))


def executable_source() -> str:
    """Source with the module docstring and full-line comments removed."""
    src = SCRIPT_PATH.read_text(encoding="utf-8")
    src = re.sub(r'""".*?"""', "", src, count=1, flags=re.DOTALL)  # module docstring
    src = re.sub(r"(?m)^\s*#.*$", "", src)  # full-line comments
    return src


class _Base(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self._env = mock.patch.dict(
            os.environ,
            {"XDG_STATE_HOME": str(self.tmp / "state"), gig.API_KEY_ENV: "secret-key-123"},
        )
        self._env.start()

    def tearDown(self) -> None:
        self._env.stop()
        self._tmp.cleanup()

    def out(self, name: str = "img.png") -> Path:
        return self.tmp / name


@contextlib.contextmanager
def capture_stderr():
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        yield buf


# --------------------------------------------------------------------------- #
# AC1 / AC2 — static inspection
# --------------------------------------------------------------------------- #
class StaticInspection(unittest.TestCase):
    def test_model_id_is_the_only_one_and_no_imagen(self):
        self.assertEqual(gig.MODEL, "gemini-2.5-flash-image")
        code = executable_source().lower()
        self.assertNotIn("imagen", code)
        self.assertNotIn("gemini-1", code)
        self.assertNotIn("gemini-pro", code)

    def test_no_vertex_ai(self):
        code = executable_source().lower()
        self.assertNotIn("aiplatform", code)
        self.assertNotIn("vertexai", code)
        self.assertNotIn("import vertex", code)

    def test_endpoint_is_pinned_v1beta_generativelanguage(self):
        self.assertTrue(gig.ENDPOINT.startswith("https://generativelanguage.googleapis.com/v1beta/"))
        self.assertIn(":generateContent", gig.ENDPOINT)


# --------------------------------------------------------------------------- #
# AC3 / AC4 — API key handling
# --------------------------------------------------------------------------- #
class ApiKey(_Base):
    def test_key_read_only_from_env_and_sent_as_header(self):
        req = gig.build_request("p", "secret-key-123", n=1, seed=None)
        self.assertEqual(req.get_header("X-goog-api-key"), "secret-key-123")
        self.assertNotIn("secret-key-123", req.full_url)  # never in the URL

    def test_missing_key_emits_setup_hint_nonzero(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop(gig.API_KEY_ENV, None)
            with capture_stderr() as err:
                code = gig.main(["--prompt", "x", "--out", str(self.out()), "--accept-data-policy"])
        self.assertNotEqual(code, 0)
        msg = err.getvalue()
        self.assertIn(gig.API_KEY_ENV, msg)
        self.assertIn("aistudio.google.com/apikey", msg)
        self.assertIn("billing", msg.lower())


# --------------------------------------------------------------------------- #
# AC5 / AC6 / AC7 — HTTP error handling, no retry
# --------------------------------------------------------------------------- #
class HttpErrors(_Base):
    def _run_with(self, side_effect):
        with mock.patch("urllib.request.urlopen") as m:
            m.side_effect = side_effect
            with capture_stderr() as err:
                code = gig.main(["--prompt", "x", "--out", str(self.out()), "--accept-data-policy"])
            return code, err.getvalue(), m

    def test_429_terminal_no_retry(self):
        code, msg, m = self._run_with(http_error(429))
        self.assertEqual(code, gig.EXIT_RATE_LIMIT)
        self.assertEqual(m.call_count, 1)  # never retried
        self.assertIn("429", msg)

    def test_429_message_has_quantitative_figure(self):
        _, msg, _ = self._run_with(http_error(429))
        self.assertRegex(msg, r"\d+\s*(requests\s*)?per\s*(minute|day)")

    def test_401_auth_failure_links_key_page(self):
        code, msg, _ = self._run_with(http_error(401))
        self.assertEqual(code, gig.EXIT_AUTH)
        self.assertIn("aistudio.google.com/apikey", msg)

    def test_403_auth_failure(self):
        code, _, _ = self._run_with(http_error(403))
        self.assertEqual(code, gig.EXIT_AUTH)

    def test_network_error_is_readable_nonzero(self):
        code, msg, _ = self._run_with(urllib.error.URLError("dns boom"))
        self.assertEqual(code, gig.EXIT_ERROR)
        self.assertIn("Network error", msg)
        self.assertNotIn("Traceback", msg)

    # --- error-body handling (issue #239): surface the real cause ----------- #
    _ZERO_QUOTA_BODY = json.dumps({"error": {
        "code": 429,
        "message": "You exceeded your current quota. Quota exceeded for metric: "
                   "generativelanguage.googleapis.com/generate_content_free_tier_requests, "
                   "limit: 0, model: gemini-2.5-flash-preview-image",
        "status": "RESOURCE_EXHAUSTED",
    }})
    _RATE_LIMIT_BODY = json.dumps({"error": {
        "code": 429,
        "message": "Resource has been exhausted (e.g. check quota). Please retry in 5s.",
        "status": "RESOURCE_EXHAUSTED",
    }})

    def test_429_zero_quota_reports_billing_not_retry(self):
        # limit:0 means the model is off the Free Tier entirely — billing, not waiting.
        code, msg, _ = self._run_with(http_error_with_body(429, self._ZERO_QUOTA_BODY))
        self.assertEqual(code, gig.EXIT_RATE_LIMIT)
        self.assertIn("billing", msg.lower())
        self.assertIn("limit: 0", msg)
        self.assertIn("gemini-2.5-flash-preview-image", msg)  # real cause surfaced

    def test_429_real_rate_limit_keeps_quota_guidance_and_surfaces_detail(self):
        code, msg, _ = self._run_with(http_error_with_body(429, self._RATE_LIMIT_BODY))
        self.assertEqual(code, gig.EXIT_RATE_LIMIT)
        self.assertRegex(msg, r"\d+\s*(requests\s*)?per\s*(minute|day)")  # quota figure kept
        self.assertIn("Please retry in 5s", msg)  # Google's actual message surfaced

    def test_http_error_body_detail_surfaced_on_generic_status(self):
        body = json.dumps({"error": {"message": "Something specific went wrong", "status": "INTERNAL"}})
        code, msg, _ = self._run_with(http_error_with_body(500, body))
        self.assertEqual(code, gig.EXIT_ERROR)
        self.assertIn("Something specific went wrong", msg)

    def test_unreadable_error_body_falls_back_cleanly(self):
        # The original fp=None helper must still produce the generic message, no crash.
        code, msg, _ = self._run_with(http_error(429))
        self.assertEqual(code, gig.EXIT_RATE_LIMIT)
        self.assertIn("429", msg)


# --------------------------------------------------------------------------- #
# AC8 / AC15 — data-protection acknowledgement & digest versioning
# --------------------------------------------------------------------------- #
class Acknowledgement(_Base):
    def _generate_once(self, args_extra, name="img.png"):
        with mock.patch("urllib.request.urlopen") as m:
            m.return_value = _FakeResponse(image_response())
            with capture_stderr() as err:
                code = gig.main(["--prompt", "x", "--out", str(self.out(name))] + args_extra)
            return code, err.getvalue()

    def test_first_run_prompts_then_persists_digest(self):
        self.assertFalse(gig.ack_path().exists())
        code, msg = self._generate_once(["--accept-data-policy"])
        self.assertEqual(code, 0)
        self.assertIn("train and improve", msg)  # notice shown
        stored = gig.ack_path().read_text().strip()
        self.assertEqual(stored, gig.notice_digest())
        self.assertRegex(stored, r"^[0-9a-f]{64}$")  # SHA-256 hex

    def test_second_run_does_not_reprompt(self):
        self._generate_once(["--accept-data-policy"], name="first.png")
        # second run without the flag, to a distinct path: digest matches → no
        # notice, no failure (and no overwrite refusal masking the ack check)
        code, msg = self._generate_once([], name="second.png")
        self.assertEqual(code, 0)
        self.assertNotIn("train and improve", msg)

    def test_changed_digest_reprompts(self):
        gig.ack_path().parent.mkdir(parents=True, exist_ok=True)
        gig.ack_path().write_text("deadbeef\n")
        code, msg = self._generate_once(["--accept-data-policy"])
        self.assertEqual(code, 0)
        self.assertIn("train and improve", msg)  # re-prompted because digest differs
        self.assertEqual(gig.ack_path().read_text().strip(), gig.notice_digest())

    def test_noninteractive_without_flag_aborts(self):
        with mock.patch("sys.stdin.isatty", return_value=False), \
             mock.patch("urllib.request.urlopen") as m:
            m.return_value = _FakeResponse(image_response())
            with capture_stderr():
                code = gig.main(["--prompt", "x", "--out", str(self.out())])
        self.assertNotEqual(code, 0)
        self.assertFalse(self.out().exists())  # no image written without consent


# --------------------------------------------------------------------------- #
# AC9 / AC10 — usage & overwrite guards
# --------------------------------------------------------------------------- #
class Guards(_Base):
    def test_missing_out_is_usage_error(self):
        with self.assertRaises(SystemExit) as cm, capture_stderr():
            gig.main(["--prompt", "x"])
        self.assertEqual(cm.exception.code, 2)

    def test_existing_target_refused_without_force(self):
        target = self.out()
        target.write_bytes(b"original")
        with mock.patch("urllib.request.urlopen") as m:
            with capture_stderr() as err:
                code = gig.main(["--prompt", "x", "--out", str(target), "--accept-data-policy"])
        self.assertNotEqual(code, 0)
        self.assertEqual(m.call_count, 0)  # bailed before any API call
        self.assertEqual(target.read_bytes(), b"original")  # untouched
        self.assertIn("--force", err.getvalue())

    def test_existing_target_overwritten_with_force(self):
        target = self.out()
        target.write_bytes(b"original")
        with mock.patch("urllib.request.urlopen") as m:
            m.return_value = _FakeResponse(image_response())
            with capture_stderr():
                code = gig.main(["--prompt", "x", "--out", str(target), "--force", "--accept-data-policy"])
        self.assertEqual(code, 0)
        self.assertNotEqual(target.read_bytes(), b"original")


# --------------------------------------------------------------------------- #
# AC11 / AC12 / AC13 — output, sidecar, mime mismatch
# --------------------------------------------------------------------------- #
class Outputs(_Base):
    def _run_ok(self, name, mime="image/png"):
        with mock.patch("urllib.request.urlopen") as m:
            m.return_value = _FakeResponse(image_response(mime=mime))
            with capture_stderr() as err:
                code = gig.main(["--prompt", "a fox", "--out", str(self.out(name)), "--accept-data-policy"])
            return code, err.getvalue()

    def test_image_and_sidecar_written_with_required_keys(self):
        code, _ = self._run_ok("hero.png")
        self.assertEqual(code, 0)
        img = self.out("hero.png")
        sidecar = self.out("hero.png.meta.json")
        self.assertTrue(img.exists())
        self.assertTrue(sidecar.exists())
        meta = json.loads(sidecar.read_text())
        self.assertEqual(set(meta), {"prompt", "model", "endpoint", "timestamp", "mime_type"})
        self.assertEqual(meta["prompt"], "a fox")
        self.assertEqual(meta["model"], "gemini-2.5-flash-image")

    def test_sidecar_never_contains_key(self):
        self._run_ok("hero.png")
        self.assertNotIn("secret-key-123", self.out("hero.png.meta.json").read_text())

    def test_extension_mime_mismatch_warns_but_writes(self):
        code, msg = self._run_ok("hero.jpg", mime="image/png")
        self.assertEqual(code, 0)
        self.assertTrue(self.out("hero.jpg").exists())  # still written
        self.assertIn("warning", msg.lower())


# --------------------------------------------------------------------------- #
# AC14 — n>1
# --------------------------------------------------------------------------- #
class MultiImage(_Base):
    def test_n_images_yield_n_files_and_n_sidecars(self):
        with mock.patch("urllib.request.urlopen") as m:
            m.return_value = _FakeResponse(image_response(n=3))
            with capture_stderr():
                code = gig.main(["--prompt", "p", "-n", "3", "--out", str(self.out("x.png")), "--accept-data-policy"])
        self.assertEqual(code, 0)
        imgs = sorted(self.tmp.glob("x-*.png"))
        sidecars = sorted(self.tmp.glob("x-*.png.meta.json"))
        self.assertEqual(len(imgs), 3)
        self.assertEqual(len(sidecars), 3)
        prompts = {json.loads(s.read_text())["prompt"] for s in sidecars}
        self.assertEqual(prompts, {"p"})  # identical across all sidecars


# --------------------------------------------------------------------------- #
# Prompt resolution (incl. pipeline glue to graphic-prompt-generator docs)
# --------------------------------------------------------------------------- #
class PromptResolution(_Base):
    DOC = (
        "# Graphic Prompt: Fox\n\n"
        "## Prompt — Light Mode\n```\nteal fox on white, flat\n```\n\n"
        "## Prompt — Dark Mode\n```\nteal fox on charcoal, flat\n```\n"
    )

    def test_extract_variant_from_prompt_doc(self):
        self.assertEqual(
            gig.extract_prompt_from_doc(self.DOC, "dark"), "teal fox on charcoal, flat"
        )

    def test_extract_first_block_without_variant(self):
        self.assertEqual(
            gig.extract_prompt_from_doc(self.DOC, None), "teal fox on white, flat"
        )

    def test_missing_variant_section_raises(self):
        with self.assertRaises(gig.GenerationError):
            gig.extract_prompt_from_doc("# no prompts here\n", "light")

    def test_from_prompt_doc_end_to_end(self):
        doc = self.tmp / "fox.md"
        doc.write_text(self.DOC)
        with mock.patch("urllib.request.urlopen") as m:
            m.return_value = _FakeResponse(image_response())
            with capture_stderr():
                code = gig.main(
                    ["--from-prompt-doc", str(doc), "--variant", "light",
                     "--out", str(self.out()), "--accept-data-policy"]
                )
        self.assertEqual(code, 0)
        meta = json.loads(self.out("img.png.meta.json").read_text())
        self.assertEqual(meta["prompt"], "teal fox on white, flat")


if __name__ == "__main__":
    unittest.main()
