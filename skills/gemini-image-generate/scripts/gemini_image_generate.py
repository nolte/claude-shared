#!/usr/bin/env python3
"""Generate an image from a text prompt via the Gemini Free-Tier model.

A prompt in, an image file on disk out — no chat UI. Implements
`spec/tools/gemini-image-generation/`. The model ID and endpoint are a
hard-coded allowlist: only `gemini-2.5-flash-image` on the Google AI Studio
Generative Language `v1beta` endpoint is reachable; paid models (`imagen-*`)
and Vertex AI (`*-aiplatform.googleapis.com`) are structurally unreachable
from this code path.

Stdlib-only by design: a single hard-coded endpoint literal makes the
Free-Tier constraint statically verifiable and keeps the tool dependency-free
so it drops into any pipeline.

Exit codes:
  0  image(s) written
  1  generic runtime error (network, DNS, filesystem, malformed response)
  2  usage error (bad/missing arguments — argparse default)
  3  rate limit / quota exhausted (HTTP 429) — terminal, never retried
  4  authentication failure (HTTP 401 / 403)

Usage:
  GEMINI_API_KEY=... python scripts/gemini_image_generate.py \
      --prompt "a minimalist teal fox icon, flat" --out fox.png
  ... --prompt-file prompt.txt --out hero.png
  ... --from-prompt-doc design/prompts/hero_x.md --variant dark --out hero.png
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# --- Hard-coded Free-Tier allowlist (spec §Requirements; never parameterised) ---
MODEL = "gemini-2.5-flash-image"
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent"
API_KEY_ENV = "GEMINI_API_KEY"
KEY_PAGE = "https://aistudio.google.com/apikey"

# Free-Tier ceiling surfaced on HTTP 429 so the operator understands the limit
# that was hit (spec: the 429 message MUST carry a quantitative figure).
FREE_TIER_RATE = "Free-Tier limits for gemini-2.5-flash-image are roughly 10 requests per minute / 100 per day"

# Verbatim data-protection notice (spec §Requirements). Its SHA-256 digest is
# the consent version signal: change the text and every operator is re-prompted.
DATA_NOTICE = (
    "Free-Tier prompts and generated images are used by Google to train and "
    "improve their models. Don't submit confidential or personal data. To opt "
    "out, enable billing on this API key—see "
    "<https://ai.google.dev/gemini-api/terms>."
)

EXT_TO_MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}

# Exit codes
EXIT_OK = 0
EXIT_ERROR = 1
EXIT_RATE_LIMIT = 3
EXIT_AUTH = 4


class GenerationError(Exception):
    """Terminal error carrying an operator-facing message and an exit code."""

    def __init__(self, message: str, code: int = EXIT_ERROR) -> None:
        super().__init__(message)
        self.code = code


# --------------------------------------------------------------------------- #
# Prompt resolution
# --------------------------------------------------------------------------- #
def extract_prompt_from_doc(text: str, variant: str | None) -> str:
    """Pull the fenced prompt block out of a graphic-prompt-generator document.

    The agent writes `## Prompt — Light Mode` / `## Prompt — Dark Mode` headings
    each followed by a ```-fenced block. With `variant` we pick that section;
    without one we take the first fenced block in the document.
    """
    if variant:
        # Find the heading for the requested variant, then the next fenced block.
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
# Data-protection acknowledgement (one-time, per machine, digest-versioned)
# --------------------------------------------------------------------------- #
def ack_path() -> Path:
    base = os.environ.get("XDG_STATE_HOME") or os.path.join(
        os.path.expanduser("~"), ".local", "state"
    )
    return Path(base) / "nolte-shared" / "gemini-image-generation" / "ack"


def notice_digest() -> str:
    return hashlib.sha256(DATA_NOTICE.encode("utf-8")).hexdigest()


def ensure_ack(accept_flag: bool) -> None:
    """Show the notice and require acknowledgement unless the stored digest matches."""
    path = ack_path()
    want = notice_digest()
    try:
        if path.read_text(encoding="utf-8").strip() == want:
            return  # already acknowledged this exact notice text
    except OSError:
        pass  # missing/unreadable → prompt

    print(DATA_NOTICE, file=sys.stderr)
    if accept_flag:
        pass  # explicit non-interactive acknowledgement
    elif sys.stdin.isatty():
        reply = input("Type 'yes' to acknowledge and continue: ").strip().lower()
        if reply not in {"yes", "y"}:
            raise GenerationError("data-protection notice not acknowledged; aborting")
    else:
        raise GenerationError(
            "data-protection notice not acknowledged; re-run with --accept-data-policy "
            "to acknowledge non-interactively"
        )
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(want + "\n", encoding="utf-8")
    except OSError as exc:
        raise GenerationError(f"cannot persist acknowledgement to {path}: {exc}") from exc


# --------------------------------------------------------------------------- #
# API call
# --------------------------------------------------------------------------- #
def require_api_key() -> str:
    key = os.environ.get(API_KEY_ENV)
    if not key:
        raise GenerationError(
            f"{API_KEY_ENV} is not set. Create a free key at {KEY_PAGE} — "
            f"Free-Tier usage requires no billing setup, then export {API_KEY_ENV}."
        )
    return key


def build_request(prompt: str, api_key: str, n: int, seed: int | None) -> urllib.request.Request:
    body: dict = {"contents": [{"parts": [{"text": prompt}]}]}
    gen_config: dict = {}
    if n > 1:
        gen_config["candidateCount"] = n
    if seed is not None:
        gen_config["seed"] = seed
    if gen_config:
        body["generationConfig"] = gen_config
    return urllib.request.Request(
        ENDPOINT,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            # Key travels in a header, never in the URL — so it never lands in
            # the sidecar `endpoint` field, logs, or error traces.
            "x-goog-api-key": api_key,
        },
        method="POST",
    )


def _api_error_detail(exc: urllib.error.HTTPError) -> tuple[str, bool]:
    """Read the API error body; return (human-readable detail, is_zero_quota).

    The body is read here so Google's actual ``error.message`` is surfaced
    instead of being swallowed (the original code looked only at the status
    code). ``is_zero_quota`` is True when the body reports a Free-Tier quota of
    ``limit: 0`` — the model is not enabled on the Free Tier at all and requires
    billing, which is categorically different from a temporary rate-limit that
    retrying would clear.
    """
    try:
        body = exc.read().decode("utf-8", "replace")
    except Exception:
        return "", False
    try:
        detail = (json.loads(body).get("error", {}).get("message") or "").strip()
    except (ValueError, TypeError, AttributeError):
        detail = body.strip()
    zero_quota = re.search(r"limit:\s*0\b", body) is not None
    return detail, zero_quota


def call_api(request: urllib.request.Request) -> dict:
    try:
        with urllib.request.urlopen(request) as response:
            payload = response.read()
    except urllib.error.HTTPError as exc:
        status = exc.code
        detail, zero_quota = _api_error_detail(exc)
        suffix = f" API said: {detail}" if detail else ""
        if status == 429:
            if zero_quota:
                raise GenerationError(
                    "This model is not available on the Free Tier (reported quota "
                    "limit: 0) — it requires billing on the API key's Google Cloud "
                    "project. Enable billing, then retry; waiting will not help."
                    f"{suffix}",
                    code=EXIT_RATE_LIMIT,
                ) from exc
            raise GenerationError(
                f"Free-Tier quota exhausted (HTTP 429). {FREE_TIER_RATE}. "
                "Not retried automatically — each retry burns more quota. "
                f"Wait for the window to reset or enable billing.{suffix}",
                code=EXIT_RATE_LIMIT,
            ) from exc
        if status in (401, 403):
            raise GenerationError(
                f"Authentication failed (HTTP {status}). Check {API_KEY_ENV} and "
                f"manage your key at {KEY_PAGE}.{suffix}",
                code=EXIT_AUTH,
            ) from exc
        raise GenerationError(
            f"Gemini API returned HTTP {status}. The request was not fulfilled.{suffix}"
        ) from exc
    except urllib.error.URLError as exc:
        raise GenerationError(
            f"Network error reaching the Gemini API: {exc.reason}"
        ) from exc

    try:
        return json.loads(payload)
    except (ValueError, TypeError) as exc:
        raise GenerationError("the Gemini API returned a malformed (non-JSON) response") from exc


def extract_images(response: dict) -> list[tuple[str, bytes]]:
    """Return [(mime_type, raw_bytes), ...] for every inline image in the response."""
    images: list[tuple[str, bytes]] = []
    for candidate in response.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data")
            if not inline:
                continue
            mime = inline.get("mimeType") or inline.get("mime_type") or "image/png"
            data = inline.get("data")
            if not data:
                continue
            try:
                raw = base64.b64decode(data)
            except (ValueError, TypeError) as exc:
                raise GenerationError("the Gemini API returned undecodable image data") from exc
            images.append((mime, raw))
    if not images:
        raise GenerationError(
            "the Gemini API response contained no image data (the prompt may have "
            "been refused — check that it requests an image)."
        )
    return images


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
            f"warning: {path} has extension '{path.suffix}' (expects {expected}) but "
            f"the API returned {mime}; writing anyway. Rename or rerun with a matching "
            "extension if needed.",
            file=sys.stderr,
        )


def write_sidecar(image_path: Path, prompt: str, mime: str) -> None:
    meta = {
        "prompt": prompt,
        "model": MODEL,
        "endpoint": ENDPOINT,
        "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "mime_type": mime,
    }
    sidecar = image_path.with_name(image_path.name + ".meta.json")
    sidecar.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_outputs(images: list[tuple[str, bytes]], paths: list[Path], prompt: str) -> None:
    for (mime, raw), path in zip(images, paths):
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        except OSError as exc:
            raise GenerationError(f"cannot write image to {path}: {exc}") from exc
        warn_extension_mismatch(path, mime)
        write_sidecar(path, prompt, mime)
        print(f"wrote {path} ({len(raw)} bytes) + {path.name}.meta.json", file=sys.stderr)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gemini_image_generate",
        description="Generate an image from a text prompt via the Gemini Free-Tier model.",
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
        help="acknowledge the Free-Tier data-protection notice non-interactively (CI)",
    )
    parser.add_argument("-n", type=int, default=1, metavar="N", help="number of images to request (default 1)")
    parser.add_argument("--seed", type=int, help="optional generation seed (recorded in the sidecar)")
    return parser


def run(args: argparse.Namespace) -> int:
    if args.n < 1:
        raise GenerationError("-n must be at least 1")
    if args.variant and not args.from_prompt_doc:
        raise GenerationError("--variant only applies together with --from-prompt-doc")

    prompt = resolve_prompt(args)
    out = Path(args.out)
    paths = target_paths(out, args.n)
    check_overwrite(paths, args.force)

    api_key = require_api_key()
    ensure_ack(args.accept_data_policy)

    response = call_api(build_request(prompt, api_key, args.n, args.seed))
    images = extract_images(response)

    if len(images) < args.n:
        print(
            f"warning: requested {args.n} image(s) but the API returned {len(images)}; "
            "writing what was returned.",
            file=sys.stderr,
        )
        paths = paths[: len(images)]
    write_outputs(images, paths, prompt)
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
