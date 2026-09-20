#!/usr/bin/env python3
"""Generate an image from a text prompt via a pluggable backend provider.

A prompt in, an image file on disk out — no chat UI, scriptable into any
pipeline. Backends are swappable via ``--provider`` so the tool is not locked to
one vendor's pricing or availability:

  cloudflare    Cloudflare Workers AI: FLUX.1-schnell (Apache-2.0, default) or
                FLUX.2 [klein] 4B via --model flux-2-klein-4b (Apache-2.0,
                honours --width/--height, up to 4 --ref-image inputs). Real
                recurring free tier (10k neurons/day, no credit card). DEFAULT.
  pollinations  Pollinations.ai, FLUX. Auth-free. NOTE: public feed by default
                (this tool forces private=true) and the output licence is
                undocumented — a one-time disclaimer is shown.
  gemini        Google Gemini gemini-3.1-flash-image ("Nano Banana 2"). Requires
                BILLING on the API project: no Gemini image model carries a free
                tier. Replaces gemini-2.5-flash-image, which shuts down
                2026-10-02.

Stdlib-only by design: no runtime dependencies, so it drops into any shell or CI.

Exit codes:
  0  image(s) written
  1  generic runtime error (network, DNS, filesystem, malformed response)
  2  usage error (bad/missing arguments — argparse default)
  3  rate limit / quota exhausted (HTTP 429) — terminal, never retried
  4  authentication failure (HTTP 401 / 403)

Usage:
  CLOUDFLARE_API_TOKEN=... CLOUDFLARE_ACCOUNT_ID=... \
    python image_generate.py --prompt "a teal fox icon, flat" --out fox.png
  python image_generate.py --provider pollinations --prompt "a tree, comic style" --out tree.png
  python image_generate.py --provider gemini --prompt "..." --out x.png    # needs billing
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import secrets
import stat
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

EXT_TO_MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}

# Some providers (Pollinations) sit behind Cloudflare, whose bot protection
# rejects the default urllib User-Agent ("Python-urllib/x.y") with HTTP 403
# (error 1010). A normal browser-style UA passes; without it the GET is blocked.
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"

# --------------------------------------------------------------------------- #
# Safety bounds on operator- and provider-supplied data
# --------------------------------------------------------------------------- #
# Cap on a single --ref-image. The klein-4b endpoint's own limit is expressed in
# pixels ("under 512x512"), which no byte count states exactly, so this bound is
# deliberately loose: far above any conforming image, far below a memory hazard
# (a symlink to a huge file, a sparse file). The endpoint stays authoritative on
# dimensions — this tool never validates them client-side.
MAX_REF_IMAGE_BYTES = 20 * 1024 * 1024  # 20 MiB
# Cap on a response body. A malicious or intercepted endpoint must not be able to
# exhaust memory, and on the klein `image/*` branch those bytes go straight to disk.
MAX_RESPONSE_BYTES = 64 * 1024 * 1024  # 64 MiB
# Cap on any server-controlled string surfaced to the operator or the sidecar.
MAX_PROVIDER_TEXT_CHARS = 500
TRUNCATION_MARKER = " [truncated]"

# C0 (including ESC, so ANSI escape sequences never reach a terminal), DEL, C1, and
# the Unicode bidirectional controls: the embeddings/overrides U+202A-U+202E and the
# isolates U+2066-U+2069 are not control *characters* by codepoint range, but a
# terminal that honours them lets a message reorder its own visible text, which is
# the same forgery ESC buys.
_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f-\x9f\u202a-\u202e\u2066-\u2069]")
# Control characters that carry word separation; folded to a space before the rest
# is dropped, so a multi-line provider message stays readable on one line.
_WHITESPACE_CONTROLS = re.compile(r"[\t\n\v\f\r]")

# Exit codes
EXIT_OK = 0
EXIT_ERROR = 1
EXIT_USAGE = 2  # argparse's own code for a bad invocation; reused for semantic misuse
EXIT_RATE_LIMIT = 3
EXIT_AUTH = 4


class GenerationError(Exception):
    """Terminal error carrying an operator-facing message and an exit code."""

    def __init__(self, message: str, code: int = EXIT_ERROR) -> None:
        super().__init__(message)
        self.code = code


# --------------------------------------------------------------------------- #
# Shared HTTP layer (one place for error-body surfacing + limit:0 detection)
# --------------------------------------------------------------------------- #
def _safe_text(value: object) -> str:
    """Make an untrusted string safe to print or to store in the sidecar.

    Untrusted means server-controlled *and* operator-supplied: a path picked up by a
    shell glob over a directory the operator does not control carries whatever bytes
    its file name carries, so it forges terminal output exactly like a provider
    message does. Both classes go through here before reaching stderr.

    Strips C0 (ESC included, so ANSI escape sequences cannot forge terminal
    output), DEL, C1, and the Unicode bidirectional overrides/isolates, and caps
    the result at ``MAX_PROVIDER_TEXT_CHARS`` with an explicit marker. The
    provider's own wording stays intact — the shared layer is required to
    surface the upstream ``error.message``, so this sanitizes the text without
    swallowing it.
    """
    text = _WHITESPACE_CONTROLS.sub(" ", value if isinstance(value, str) else str(value))
    text = _CONTROL_CHARS.sub("", text).strip()
    if len(text) > MAX_PROVIDER_TEXT_CHARS:
        text = text[:MAX_PROVIDER_TEXT_CHARS].rstrip() + TRUNCATION_MARKER
    return text


def _read_capped(stream: object, limit: int, what: str) -> bytes:
    """Read at most ``limit`` bytes; refuse anything larger instead of buffering it.

    Reads ``limit + 1`` bytes so "exactly at the cap" still succeeds and the first
    byte past it is enough to refuse — the oversize body is never held in memory.
    """
    chunks: list[bytes] = []
    remaining = limit + 1
    while remaining > 0:
        chunk = stream.read(remaining)
        got = len(chunk) if chunk else 0
        if got == 0:  # EOF — and a zero-length chunk could never make progress
            break
        chunks.append(chunk)
        remaining -= got
    data = b"".join(chunks)
    if len(data) > limit:
        raise GenerationError(
            f"{what} exceeds the {limit // (1024 * 1024)} MiB safety cap "
            f"(MAX_RESPONSE_BYTES); the response was discarded and nothing was "
            "written. Re-run with a smaller request, or verify you are talking to "
            "the real provider endpoint."
        )
    return data


def _api_error_detail(exc: urllib.error.HTTPError) -> tuple[str, bool]:
    """Read the API error body; return (human-readable detail, is_zero_quota).

    Surfaces the provider's actual ``error.message`` instead of swallowing it —
    sanitized (control characters stripped, length capped) because it is
    server-controlled text on its way to the operator's terminal.
    ``is_zero_quota`` is True when the body reports a quota of ``limit: 0`` — the
    model requires billing rather than being temporarily rate-limited, so
    "retry later" would be wrong.
    """
    try:
        body = _read_capped(exc, MAX_RESPONSE_BYTES, "the provider error body").decode(
            "utf-8", "replace"
        )
    except Exception:
        return "", False
    try:
        detail = (json.loads(body).get("error", {}).get("message") or "").strip()
    except (ValueError, TypeError, AttributeError):
        detail = body.strip()
    zero_quota = re.search(r"limit:\s*0\b", body) is not None
    return _safe_text(detail), zero_quota


def _raise_http_error(exc: urllib.error.HTTPError, key_page: str | None) -> None:
    status = exc.code
    detail, zero_quota = _api_error_detail(exc)
    suffix = f" API said: {detail}" if detail else ""
    if status == 429:
        if zero_quota:
            raise GenerationError(
                "This model is not available on the free tier (reported quota "
                "limit: 0) — it requires billing on the API project. Enable billing, "
                f"then retry; waiting will not help.{suffix}",
                code=EXIT_RATE_LIMIT,
            ) from exc
        raise GenerationError(
            f"Rate limit / quota exhausted (HTTP 429). Not retried automatically — "
            f"each retry burns more quota. Wait for the window to reset.{suffix}",
            code=EXIT_RATE_LIMIT,
        ) from exc
    if status in (401, 403):
        hint = f" Check your credentials at {key_page}." if key_page else ""
        raise GenerationError(
            f"Authentication failed (HTTP {status}).{hint}{suffix}", code=EXIT_AUTH
        ) from exc
    raise GenerationError(
        f"Provider API returned HTTP {status}. The request was not fulfilled.{suffix}"
    ) from exc


def _request(req: urllib.request.Request, key_page: str | None = None) -> tuple[bytes, str]:
    """Perform a request; return (body_bytes, content_type). Maps errors to GenerationError.

    The body is read under ``MAX_RESPONSE_BYTES``: every caller (the JSON paths,
    the klein multipart path, the Pollinations raw-bytes path) wants the whole
    body, so one cap here bounds them all. The content type is sanitized here too,
    since it reaches both the stderr mismatch warning and the sidecar.
    """
    try:
        with urllib.request.urlopen(req) as response:
            body = _read_capped(response, MAX_RESPONSE_BYTES, "the provider response body")
            return body, _safe_text(response.headers.get_content_type())
    except urllib.error.HTTPError as exc:
        _raise_http_error(exc, key_page)
    except urllib.error.URLError as exc:
        raise GenerationError(f"Network error reaching the provider: {exc.reason}") from exc


def _post_json(url: str, body: dict, headers: dict, key_page: str | None) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": USER_AGENT, **headers},
        method="POST",
    )
    raw, _ = _request(req, key_page)
    try:
        return json.loads(raw)
    except (ValueError, TypeError) as exc:
        raise GenerationError("the provider returned a malformed (non-JSON) response") from exc


def _header_line_safe(value: str) -> str:
    """Drop CR and LF so a caller-supplied value can never inject a header line."""
    return value.replace("\r", "").replace("\n", "")


def _quoted_filename(filename: str) -> str:
    """Escape a filename for an RFC 2183 quoted-string ``filename="..."`` parameter.

    CR/LF are removed first (header injection), then ``\\`` and ``"`` are escaped so
    the value cannot terminate the quoted string early. An empty result falls back
    to ``image`` — a part without a usable filename still needs one.
    """
    safe = _header_line_safe(filename).replace("\\", "\\\\").replace('"', '\\"')
    return safe or "image"


def _encode_multipart(
    fields: dict[str, str],
    files: list[tuple[str, str, str, bytes]] | None = None,
) -> tuple[bytes, str]:
    """Encode form fields and files as multipart/form-data; return (body, content_type).

    Stdlib-only by design (no `requests`). ``files`` entries are
    ``(field_name, filename, content_type, data)``; ``filename`` and
    ``content_type`` are sanitized here, so every caller is covered. The boundary
    is random per call, so it can never collide with payload bytes.
    """
    boundary = "----imageGenerate" + secrets.token_hex(16)
    marker = f"--{boundary}".encode("ascii")
    out = bytearray()
    for name, value in fields.items():
        out += marker + b"\r\n"
        out += f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8")
        out += str(value).encode("utf-8") + b"\r\n"
    for name, filename, content_type, data in files or []:
        out += marker + b"\r\n"
        out += (
            f'Content-Disposition: form-data; name="{name}"; '
            f'filename="{_quoted_filename(filename)}"\r\n'
            f"Content-Type: {_header_line_safe(content_type)}\r\n\r\n"
        ).encode("utf-8")
        out += data + b"\r\n"
    out += marker + b"--\r\n"
    return bytes(out), f"multipart/form-data; boundary={boundary}"


def _post_multipart(
    url: str, body: bytes, content_type: str, headers: dict, key_page: str | None
) -> tuple[bytes, str]:
    """POST a multipart body; return (raw_bytes, response_content_type).

    Goes through _request so 401/403/429 handling and error-body surfacing are
    identical to the JSON path. urllib derives Content-Length from ``data``.
    """
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": content_type, "User-Agent": USER_AGENT, **headers},
        method="POST",
    )
    return _request(req, key_page)


def _result_image(resp: object) -> str | None:
    """Pull ``result.image`` out of a provider envelope.

    Returns None when ``result`` is absent, null, or not an object — a malformed
    envelope is "no image data", not an AttributeError traceback.
    """
    result = resp.get("result") if isinstance(resp, dict) else None
    return result.get("image") if isinstance(result, dict) else None


def _envelope_errors(resp: object) -> object:
    """Best-effort operator-facing detail from a response that carried no image."""
    if not isinstance(resp, dict):
        return resp
    return resp.get("errors") or resp.get("messages")


def _sniff_image_mime(raw: bytes) -> str:
    """Derive the MIME type from magic bytes (base64 payloads carry no type)."""
    if raw.startswith(b"\x89PNG"):
        return "image/png"
    if raw.startswith(b"\xff\xd8"):
        return "image/jpeg"
    if raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
        return "image/webp"
    return "image/png"


def _get_bytes(url: str, headers: dict, key_page: str | None) -> tuple[str, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **headers}, method="GET")
    raw, content_type = _request(req, key_page)
    return content_type or "image/jpeg", raw


# --------------------------------------------------------------------------- #
# Providers
# --------------------------------------------------------------------------- #
class Provider:
    """Backend contract: turn a prompt into [(mime, bytes), ...]."""

    name: str = ""
    model: str = ""
    # A provider that resolves a model alias server-side names what the sidecar can't know.
    model_variant_note: str | None = None

    def __init__(self, model: str | None = None) -> None:
        # --model pins a non-default model; the sidecar then reports the id actually used.
        if model:
            self.model = model
        # Filled in by run() when --ref-image was given; recorded in the sidecar.
        self.reference_images: list[dict[str, str]] = []

    def source(self) -> str:
        return ""

    def consent_notice(self) -> str | None:
        """One-time disclaimer to surface before first use, or None."""
        return None

    def generate(self, prompt: str, n: int, seed: int | None, opts: dict) -> list[tuple[str, bytes]]:
        raise NotImplementedError


class CloudflareProvider(Provider):
    name = "cloudflare"
    # Exactly two models, both Apache-2.0-licensed weights. klein-9b and flux-2-dev
    # are deliberately absent: they carry the FLUX Non-Commercial License.
    MODELS = {
        "flux-1-schnell": "@cf/black-forest-labs/flux-1-schnell",
        "flux-2-klein-4b": "@cf/black-forest-labs/flux-2-klein-4b",
    }
    DEFAULT_MODEL = "flux-1-schnell"
    KLEIN_MODEL_KEY = "flux-2-klein-4b"
    KLEIN_MODEL = MODELS[KLEIN_MODEL_KEY]
    MAX_REF_IMAGES = 4
    model = MODELS[DEFAULT_MODEL]
    KEY_PAGE = "https://dash.cloudflare.com/profile/api-tokens"

    def source(self) -> str:
        return "https://api.cloudflare.com/client/v4/accounts/<account>/ai/run/" + self.model

    def generate(self, prompt, n, seed, opts):
        token = os.environ.get("CLOUDFLARE_API_TOKEN")
        account = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
        if not token or not account:
            raise GenerationError(
                "cloudflare provider needs CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID. "
                "Create a free account (no credit card) and an API token with the "
                f"'Workers AI' scope at {self.KEY_PAGE}; the free tier grants 10,000 "
                "neurons/day (hundreds of FLUX images)."
            )
        url = f"https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/{self.model}"
        headers = {"Authorization": f"Bearer {token}"}
        if self.model == self.KLEIN_MODEL:
            return self._generate_klein(prompt, n, seed, opts, url, headers)
        return self._generate_schnell(prompt, n, seed, opts, url, headers)

    def _generate_schnell(self, prompt, n, seed, opts, url, headers):
        if opts.get("width", 1024) != 1024 or opts.get("height", 1024) != 1024:
            print(
                "warning: flux-1-schnell ignores --width/--height and always renders "
                "1024x1024; pass --model flux-2-klein-4b to control width and height.",
                file=sys.stderr,
            )
        images: list[tuple[str, bytes]] = []
        for i in range(n):
            # FLUX.1-schnell is optimal at 1-4 steps; 8 is only Cloudflare's cap and
            # adds latency and cost without quality. See spec/design/flux-image-generation/.
            body: dict = {"prompt": prompt, "steps": 4}
            if seed is not None:
                body["seed"] = seed + i
            resp = _post_json(url, body, headers, self.KEY_PAGE)
            b64 = _result_image(resp)
            if not b64:
                errs = _envelope_errors(resp)
                raise GenerationError(
                    f"Cloudflare returned no image data: {_safe_text(errs)}"
                )
            try:
                images.append(("image/jpeg", base64.b64decode(b64)))
            except (ValueError, TypeError) as exc:
                raise GenerationError("Cloudflare returned undecodable image data") from exc
        return images

    def _generate_klein(self, prompt, n, seed, opts, url, headers):
        # The klein-4b schema accepts multipart/form-data only, and fixes steps at 4
        # server-side — sending `steps` would be rejected.
        files = [
            (f"input_image_{i}", name, mime, data)
            for i, (name, mime, data) in enumerate(opts.get("ref_images") or [])
        ]
        images: list[tuple[str, bytes]] = []
        for i in range(n):
            fields = {
                "prompt": prompt,
                "width": str(opts.get("width", 1024)),
                "height": str(opts.get("height", 1024)),
            }
            if seed is not None:
                fields["seed"] = str(seed + i)
            body, content_type = _encode_multipart(fields, files)
            raw, response_type = _post_multipart(url, body, content_type, headers, self.KEY_PAGE)
            images.append(self._decode_klein_response(raw, response_type))
        return images

    @staticmethod
    def _decode_klein_response(raw: bytes, content_type: str) -> tuple[str, bytes]:
        """Accept both documented shapes: raw image/* bytes or a base64 JSON envelope."""
        if (content_type or "").startswith("image/"):
            if not raw:
                raise GenerationError("Cloudflare returned no image data: empty response body")
            return content_type, raw
        try:
            resp = json.loads(raw)
        except (ValueError, TypeError) as exc:
            raise GenerationError(
                "the provider returned a malformed (non-JSON) response"
            ) from exc
        if not isinstance(resp, dict):
            raise GenerationError(f"Cloudflare returned no image data: {_safe_text(repr(resp))}")
        b64 = _result_image(resp)
        if not b64:
            errs = _envelope_errors(resp)
            raise GenerationError(
                    f"Cloudflare returned no image data: {_safe_text(errs)}"
                )
        try:
            data = base64.b64decode(b64)
        except (ValueError, TypeError) as exc:
            raise GenerationError("Cloudflare returned undecodable image data") from exc
        return _sniff_image_mime(data), data


class PollinationsProvider(Provider):
    name = "pollinations"
    model = "flux"
    model_variant_note = (
        "Pollinations resolves the `flux` alias server-side and doesn't report the concrete "
        "FLUX.1 variant, so the output license can't be derived from this sidecar alone"
    )

    def source(self) -> str:
        return "https://image.pollinations.ai/prompt/<prompt>"

    def consent_notice(self) -> str | None:
        return (
            "Pollinations.ai notice (operated by Myceli.AI OU, Estonia; GDPR applies):\n"
            "- PUBLIC FEED: images and prompts go to a public feed by default. This tool "
            "forces private=true to opt out, but per the privacy policy that only hides "
            "them from the feed; it does NOT guarantee non-storage (response caches "
            "persist up to ~30 days).\n"
            "- OUTPUT LICENCE: the Terms grant no explicit ownership or licence for "
            "generated images; they state 'model licences vary; verify before commercial "
            "use'. For blog or commercial use you rely on the underlying model's licence "
            "(this tool uses FLUX). Treat outputs as legally unsettled.\n"
            "- CONTENT: no NSFW filter is applied by default. Do not send confidential or "
            "personal prompts, real people's likenesses, or trademarks.\n"
            "Set POLLINATIONS_API_TOKEN to remove watermarks."
        )

    def generate(self, prompt, n, seed, opts):
        token = os.environ.get("POLLINATIONS_API_TOKEN")
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        images: list[tuple[str, bytes]] = []
        for i in range(n):
            params = {
                "width": opts.get("width", 1024),
                "height": opts.get("height", 1024),
                "model": self.model,
                "nologo": "true",
                # Hard-coded opt-out of the public feed — never overridable via CLI.
                "private": "true",
            }
            if seed is not None:
                params["seed"] = seed + i
            url = (
                "https://image.pollinations.ai/prompt/"
                + urllib.parse.quote(prompt, safe="")
                + "?"
                + urllib.parse.urlencode(params)
            )
            mime, raw = _get_bytes(url, headers, None)
            if not raw or not mime.startswith("image/"):
                raise GenerationError(
                    f"Pollinations returned non-image content (type={mime}); the prompt "
                    "may have been rejected."
                )
            images.append((mime, raw))
        return images


class GeminiProvider(Provider):
    name = "gemini"
    # Pinned to the STABLE id, deliberately not the `-preview` id that Google's
    # deprecation table names as the successor of gemini-2.5-flash-image: a preview
    # id is not something to pin a tool to. The `generateContent` surface below is
    # the legacy one -- Google now leads with the Interactions API -- but it is
    # still the documented path for image models and keeps this migration to a
    # model swap. Moving to Interactions is tracked separately.
    model = "gemini-3.1-flash-image"
    ENDPOINT = "https://generativelanguage.googleapis.com/v1/models/gemini-3.1-flash-image:generateContent"
    KEY_PAGE = "https://aistudio.google.com/apikey"

    def source(self) -> str:
        return self.ENDPOINT

    def consent_notice(self) -> str | None:
        return (
            "Gemini notice: prompts and generated images may be used by Google to "
            "train and improve their models depending on your plan. Don't submit "
            "confidential or personal data. See https://ai.google.dev/gemini-api/terms. "
            "NOTE: no Gemini image model is on the free tier (quota limit 0), so "
            "gemini-3.1-flash-image requires billing on the API project. Every "
            "generated image carries a SynthID watermark."
        )

    def generate(self, prompt, n, seed, opts):
        key = os.environ.get("GEMINI_API_KEY")
        if not key:
            raise GenerationError(
                "gemini provider needs GEMINI_API_KEY. Create a key at "
                f"{self.KEY_PAGE} — but note this image model requires billing enabled."
            )
        # The documented minimal v1 call sends `contents` alone. generationConfig
        # is added only when the caller asks for -n or --seed, so a plain call
        # carries no field the endpoint could reject.
        body: dict = {"contents": [{"parts": [{"text": prompt}]}]}
        gen: dict = {}
        if n > 1:
            gen["candidateCount"] = n
        if seed is not None:
            gen["seed"] = seed
        if gen:
            body["generationConfig"] = gen
        resp = _post_json(self.ENDPOINT, body, {"x-goog-api-key": key}, self.KEY_PAGE)
        images: list[tuple[str, bytes]] = []
        for candidate in resp.get("candidates", []):
            for part in candidate.get("content", {}).get("parts", []):
                inline = part.get("inlineData") or part.get("inline_data")
                if not inline or not inline.get("data"):
                    continue
                # Server-controlled: it reaches the stderr warning and the sidecar.
                mime = _safe_text(inline.get("mimeType") or inline.get("mime_type") or "") or "image/png"
                try:
                    images.append((mime, base64.b64decode(inline["data"])))
                except (ValueError, TypeError) as exc:
                    raise GenerationError("Gemini returned undecodable image data") from exc
        if not images:
            raise GenerationError(
                "Gemini returned no image data (the prompt may have been refused)."
            )
        return images


PROVIDERS: dict[str, type[Provider]] = {
    "cloudflare": CloudflareProvider,
    "pollinations": PollinationsProvider,
    "gemini": GeminiProvider,
}
DEFAULT_PROVIDER = "cloudflare"


# --------------------------------------------------------------------------- #
# Prompt resolution
# --------------------------------------------------------------------------- #
def extract_prompt_from_doc(text: str, variant: str | None) -> str:
    """Pull the fenced prompt block out of a graphic-prompt-generator document."""
    if variant:
        heading = re.compile(
            rf"^#+\s*Prompt\s*[—-]\s*{variant}\s*mode\s*$",
            re.IGNORECASE | re.MULTILINE,
        )
        m = heading.search(text)
        if not m:
            raise GenerationError(
                f"no '## Prompt — {variant.title()} Mode' section found in the prompt document"
            )
        text = text[m.end():]
    fence = re.search(r"```[^\n]*\n(.*?)\n```", text, re.DOTALL)
    if not fence:
        raise GenerationError("no fenced prompt block found in the prompt document")
    prompt = fence.group(1).strip()
    if not prompt:
        raise GenerationError("the fenced prompt block in the prompt document is empty")
    return prompt


def resolve_prompt(args: argparse.Namespace) -> str:
    if args.prompt is not None:
        prompt = args.prompt
    elif args.prompt_file is not None:
        try:
            prompt = Path(args.prompt_file).read_text(encoding="utf-8")
        except OSError as exc:
            raise GenerationError(f"cannot read --prompt-file: {exc}") from exc
    else:  # args.from_prompt_doc
        try:
            doc = Path(args.from_prompt_doc).read_text(encoding="utf-8")
        except OSError as exc:
            raise GenerationError(f"cannot read --from-prompt-doc: {exc}") from exc
        prompt = extract_prompt_from_doc(doc, args.variant)
    prompt = prompt.strip()
    if not prompt:
        raise GenerationError("the resolved prompt is empty")
    return prompt


# --------------------------------------------------------------------------- #
# Consent (per-provider, one-time, digest-versioned)
# --------------------------------------------------------------------------- #
def ack_path(provider_name: str) -> Path:
    base = os.environ.get("XDG_STATE_HOME") or os.path.join(
        os.path.expanduser("~"), ".local", "state"
    )
    return Path(base) / "nolte-shared" / "image-generate" / provider_name / "ack"


def ensure_consent(provider: Provider, accept_flag: bool) -> None:
    notice = provider.consent_notice()
    if notice is None:
        return
    path = ack_path(provider.name)
    want = hashlib.sha256(notice.encode("utf-8")).hexdigest()
    try:
        if path.read_text(encoding="utf-8").strip() == want:
            return
    except OSError:
        pass
    print(notice, file=sys.stderr)
    if accept_flag:
        pass
    elif sys.stdin.isatty():
        if input("Type 'yes' to acknowledge and continue: ").strip().lower() not in {"yes", "y"}:
            raise GenerationError("notice not acknowledged; aborting")
    else:
        raise GenerationError(
            "notice not acknowledged; re-run with --accept-data-policy to acknowledge "
            "non-interactively"
        )
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(want + "\n", encoding="utf-8")
    except OSError as exc:
        raise GenerationError(f"cannot persist acknowledgement to {path}: {exc}") from exc


# --------------------------------------------------------------------------- #
# Output
# --------------------------------------------------------------------------- #
def target_paths(out: Path, count: int) -> list[Path]:
    if count == 1:
        return [out]
    stem, suffix = out.stem, out.suffix
    return [out.with_name(f"{stem}-{i + 1}{suffix}") for i in range(count)]


def check_overwrite(paths: list[Path], force: bool) -> None:
    existing = [p for p in paths if p.exists()]
    if existing and not force:
        names = ", ".join(str(p) for p in existing)
        raise GenerationError(
            f"refusing to overwrite existing file(s): {names}. Pass --force to overwrite."
        )


def warn_extension_mismatch(path: Path, mime: str) -> None:
    expected = EXT_TO_MIME.get(path.suffix.lower())
    if expected and expected != mime:
        print(
            f"warning: {path} has extension '{path.suffix}' (expects {expected}) but the "
            f"provider returned {mime}; writing anyway. Rename or rerun with a matching "
            "extension if needed.",
            file=sys.stderr,
        )


def write_sidecar(image_path: Path, prompt: str, mime: str, provider: Provider) -> None:
    meta = {
        "provider": provider.name,
        "model": provider.model,
        **({"model_variant_note": provider.model_variant_note} if provider.model_variant_note else {}),
        "source": provider.source(),
        "prompt": prompt,
        "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "mime_type": mime,
        # Only the basename and digest: never the bytes, never an absolute path.
        **({"reference_images": provider.reference_images} if provider.reference_images else {}),
    }
    sidecar = image_path.with_name(image_path.name + ".meta.json")
    sidecar.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_outputs(images: list[tuple[str, bytes]], paths: list[Path], prompt: str, provider: Provider) -> None:
    for (mime, raw), path in zip(images, paths):
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        except OSError as exc:
            raise GenerationError(f"cannot write image to {path}: {exc}") from exc
        warn_extension_mismatch(path, mime)
        write_sidecar(path, prompt, mime, provider)
        print(f"wrote {path} ({len(raw)} bytes) + {path.name}.meta.json [{provider.name}]", file=sys.stderr)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="image_generate",
        description="Generate an image from a text prompt via a pluggable provider backend.",
    )
    parser.add_argument(
        "--provider",
        choices=list(PROVIDERS),
        default=DEFAULT_PROVIDER,
        help=f"backend provider (default: {DEFAULT_PROVIDER})",
    )
    parser.add_argument(
        "--model",
        choices=sorted(CloudflareProvider.MODELS),
        help=(
            "cloudflare only: image model (default: "
            f"{CloudflareProvider.DEFAULT_MODEL}). flux-2-klein-4b honours "
            "--width/--height and accepts --ref-image."
        ),
    )
    parser.add_argument(
        "--ref-image",
        action="append",
        metavar="PATH",
        help=(
            "reference image, only with --provider cloudflare --model flux-2-klein-4b; "
            f"repeatable up to {CloudflareProvider.MAX_REF_IMAGES} times. The file is "
            "uploaded to Cloudflare."
        ),
    )
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--prompt", help="inline prompt text")
    src.add_argument("--prompt-file", help="path to a file holding the raw prompt text")
    src.add_argument(
        "--from-prompt-doc",
        help="path to a graphic-prompt-generator Markdown document; the fenced prompt block is extracted",
    )
    parser.add_argument(
        "--variant",
        choices=["light", "dark"],
        help="with --from-prompt-doc: pick the Light/Dark Mode prompt section",
    )
    parser.add_argument("--out", required=True, help="target image path (e.g. assets/hero.png); required")
    parser.add_argument("--force", action="store_true", help="overwrite the target file if it exists")
    parser.add_argument(
        "--accept-data-policy",
        action="store_true",
        help="acknowledge the provider's one-time data/licence notice non-interactively (CI)",
    )
    parser.add_argument("-n", type=int, default=1, metavar="N", help="number of images to request (default 1)")
    parser.add_argument("--seed", type=int, help="optional generation seed (recorded in the sidecar)")
    parser.add_argument("--width", type=int, default=1024, help="image width where the provider supports it (default 1024)")
    parser.add_argument("--height", type=int, default=1024, help="image height where the provider supports it (default 1024)")
    return parser


def _open_ref_image(raw_path: str) -> int:
    """Open a --ref-image without ever blocking on what the path points at.

    ``O_NONBLOCK`` is load-bearing: a plain ``open()`` on a FIFO blocks until a writer
    appears, so the descriptor the type check needs would never come into existence.
    With it the open returns immediately for a FIFO, a device, or a directory, and the
    caller decides on the object it actually holds. Measured on Linux: plain
    ``open(fifo, "rb")`` hangs; ``os.open(fifo, O_RDONLY | O_NONBLOCK)`` returns a
    descriptor whose ``fstat`` reports ``S_ISFIFO``.
    """
    flags = os.O_RDONLY | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_CLOEXEC", 0)
    return os.open(raw_path, flags)


def load_reference_images(paths: list[str]) -> list[tuple[str, str, bytes]]:
    """Read every --ref-image; return [(basename, mime, data), ...]. Fails before any call.

    Three bounds guard what leaves the machine: the file must be a regular file (a
    symlink to one is followed; directories, devices, and FIFOs are refused, so
    ``/dev/zero`` never gets read), its extension must be a known image type (an unknown
    one is refused, never uploaded as ``application/octet-stream``), and its size must
    stay under ``MAX_REF_IMAGE_BYTES``.

    Type and size are decided by ``os.fstat`` on the **open descriptor**, and the bytes
    are read from that same descriptor, so the path is resolved once: swapping it for a
    FIFO or a device after the check cannot change what is read. Every path echoed back
    to the operator goes through ``_safe_text`` first -- a file name is untrusted input
    just like a provider message.
    """
    supported = ", ".join(sorted(EXT_TO_MIME))
    loaded: list[tuple[str, str, bytes]] = []
    for raw_path in paths:
        path = Path(raw_path)
        shown = _safe_text(raw_path)
        try:
            descriptor = _open_ref_image(raw_path)
        except OSError as exc:
            raise GenerationError(f"cannot read --ref-image: {_safe_text(exc)}") from exc
        try:
            info = os.fstat(descriptor)
            if not stat.S_ISREG(info.st_mode):
                raise GenerationError(
                    f"--ref-image '{shown}' is not a regular file. Directories, devices, "
                    "and FIFOs cannot be uploaded — pass the path of an image file.",
                    code=EXIT_USAGE,
                )
            mime = EXT_TO_MIME.get(path.suffix.lower())
            if mime is None:
                raise GenerationError(
                    f"--ref-image '{shown}' has an unsupported extension "
                    f"'{_safe_text(path.suffix) or '(none)'}'. Supported: {supported}. "
                    "Convert the file or give it the extension matching its real format; "
                    "it is not uploaded with an unknown type.",
                    code=EXIT_USAGE,
                )
            if info.st_size > MAX_REF_IMAGE_BYTES:
                raise GenerationError(
                    f"--ref-image '{shown}' is {info.st_size} bytes, above the "
                    f"{MAX_REF_IMAGE_BYTES // (1024 * 1024)} MiB read cap "
                    "(MAX_REF_IMAGE_BYTES). Downscale or re-encode the image; the endpoint "
                    "expects a small reference anyway.",
                    code=EXIT_USAGE,
                )
            handle = os.fdopen(descriptor, "rb")
        except BaseException:
            os.close(descriptor)
            raise
        with handle:  # owns the descriptor from here on
            try:
                # Bounded read: one byte past the cap is enough to refuse a file that
                # grew after it was fstat'd, without buffering the rest.
                data = handle.read(MAX_REF_IMAGE_BYTES + 1)
            except OSError as exc:
                raise GenerationError(f"cannot read --ref-image: {_safe_text(exc)}") from exc
        if len(data) > MAX_REF_IMAGE_BYTES:
            # The file grew between fstat() and read(); refuse rather than upload it.
            raise GenerationError(
                f"--ref-image '{shown}' grew past the "
                f"{MAX_REF_IMAGE_BYTES // (1024 * 1024)} MiB read cap "
                "(MAX_REF_IMAGE_BYTES) while being read. Retry with a stable file.",
                code=EXIT_USAGE,
            )
        loaded.append((path.name, mime, data))
    return loaded


def check_model_options(args: argparse.Namespace) -> None:
    """Reject model/reference-image combinations no provider supports — before any call."""
    if args.model and args.provider != "cloudflare":
        raise GenerationError(
            "--model is only supported by the cloudflare provider, not "
            f"'{_safe_text(args.provider)}'",
            code=EXIT_USAGE,
        )
    refs = args.ref_image or []
    if not refs:
        return
    selected = args.model or (
        CloudflareProvider.DEFAULT_MODEL if args.provider == "cloudflare" else args.provider
    )
    if args.provider != "cloudflare" or args.model != CloudflareProvider.KLEIN_MODEL_KEY:
        raise GenerationError(
            "--ref-image requires --provider cloudflare --model flux-2-klein-4b; "
            f"'{_safe_text(selected)}' does not accept reference images",
            code=EXIT_USAGE,
        )
    if len(refs) > CloudflareProvider.MAX_REF_IMAGES:
        raise GenerationError(
            f"--ref-image accepts at most {CloudflareProvider.MAX_REF_IMAGES} images "
            f"(got {len(refs)})",
            code=EXIT_USAGE,
        )


def run(args: argparse.Namespace) -> int:
    if args.n < 1:
        raise GenerationError("-n must be at least 1")
    if args.variant and not args.from_prompt_doc:
        raise GenerationError("--variant only applies together with --from-prompt-doc")
    check_model_options(args)

    provider = PROVIDERS[args.provider](
        CloudflareProvider.MODELS[args.model] if args.model else None
    )
    prompt = resolve_prompt(args)
    out = Path(args.out)
    paths = target_paths(out, args.n)
    check_overwrite(paths, args.force)

    ensure_consent(provider, args.accept_data_policy)

    refs = load_reference_images(args.ref_image or [])
    provider.reference_images = [
        {"name": name, "sha256": hashlib.sha256(data).hexdigest()} for name, _, data in refs
    ]

    opts = {"width": args.width, "height": args.height, "ref_images": refs}
    images = provider.generate(prompt, args.n, args.seed, opts)

    if len(images) < args.n:
        print(
            f"warning: requested {args.n} image(s) but the provider returned {len(images)}; "
            "writing what was returned.",
            file=sys.stderr,
        )
        paths = paths[: len(images)]
    write_outputs(images, paths, prompt, provider)
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return run(args)
    except GenerationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exc.code


if __name__ == "__main__":
    sys.exit(main())
