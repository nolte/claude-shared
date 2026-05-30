#!/usr/bin/env python3
"""Generate an image from a text prompt via a pluggable backend provider.

A prompt in, an image file on disk out — no chat UI, scriptable into any
pipeline. Backends are swappable via ``--provider`` so the tool is not locked to
one vendor's pricing or availability:

  cloudflare    Cloudflare Workers AI, FLUX.1-schnell (Apache-2.0). Real
                recurring free tier (10k neurons/day, no credit card). DEFAULT.
  pollinations  Pollinations.ai, FLUX. Auth-free. NOTE: public feed by default
                (this tool forces private=true) and the output licence is
                undocumented — a one-time disclaimer is shown.
  gemini        Google Gemini gemini-2.5-flash-image. Requires BILLING on the
                API project (the Free-Tier quota for this model is 0).

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
# Shared HTTP layer (one place for error-body surfacing + limit:0 detection)
# --------------------------------------------------------------------------- #
def _api_error_detail(exc: urllib.error.HTTPError) -> tuple[str, bool]:
    """Read the API error body; return (human-readable detail, is_zero_quota).

    Surfaces the provider's actual ``error.message`` instead of swallowing it.
    ``is_zero_quota`` is True when the body reports a quota of ``limit: 0`` — the
    model requires billing rather than being temporarily rate-limited, so
    "retry later" would be wrong.
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
    """Perform a request; return (body_bytes, content_type). Maps errors to GenerationError."""
    try:
        with urllib.request.urlopen(req) as response:
            return response.read(), response.headers.get_content_type()
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

    def source(self) -> str:
        return ""

    def consent_notice(self) -> str | None:
        """One-time disclaimer to surface before first use, or None."""
        return None

    def generate(self, prompt: str, n: int, seed: int | None, opts: dict) -> list[tuple[str, bytes]]:
        raise NotImplementedError


class CloudflareProvider(Provider):
    name = "cloudflare"
    model = "@cf/black-forest-labs/flux-1-schnell"
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
        images: list[tuple[str, bytes]] = []
        for i in range(n):
            body: dict = {"prompt": prompt, "steps": 8}
            if seed is not None:
                body["seed"] = seed + i
            resp = _post_json(url, body, headers, self.KEY_PAGE)
            b64 = (resp.get("result") or {}).get("image")
            if not b64:
                errs = resp.get("errors") or resp.get("messages")
                raise GenerationError(f"Cloudflare returned no image data: {errs}")
            try:
                images.append(("image/jpeg", base64.b64decode(b64)))
            except (ValueError, TypeError) as exc:
                raise GenerationError("Cloudflare returned undecodable image data") from exc
        return images


class PollinationsProvider(Provider):
    name = "pollinations"
    model = "flux"

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
    model = "gemini-2.5-flash-image"
    ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent"
    KEY_PAGE = "https://aistudio.google.com/apikey"

    def source(self) -> str:
        return self.ENDPOINT

    def consent_notice(self) -> str | None:
        return (
            "Gemini notice: prompts and generated images may be used by Google to "
            "train and improve their models depending on your plan. Don't submit "
            "confidential or personal data. See https://ai.google.dev/gemini-api/terms. "
            "NOTE: gemini-2.5-flash-image is NOT on the free tier (quota limit 0) and "
            "requires billing on the API project."
        )

    def generate(self, prompt, n, seed, opts):
        key = os.environ.get("GEMINI_API_KEY")
        if not key:
            raise GenerationError(
                "gemini provider needs GEMINI_API_KEY. Create a key at "
                f"{self.KEY_PAGE} — but note this image model requires billing enabled."
            )
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
                mime = inline.get("mimeType") or inline.get("mime_type") or "image/png"
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
        "source": provider.source(),
        "prompt": prompt,
        "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "mime_type": mime,
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


def run(args: argparse.Namespace) -> int:
    if args.n < 1:
        raise GenerationError("-n must be at least 1")
    if args.variant and not args.from_prompt_doc:
        raise GenerationError("--variant only applies together with --from-prompt-doc")

    provider = PROVIDERS[args.provider]()
    prompt = resolve_prompt(args)
    out = Path(args.out)
    paths = target_paths(out, args.n)
    check_overwrite(paths, args.force)

    ensure_consent(provider, args.accept_data_policy)

    opts = {"width": args.width, "height": args.height}
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
