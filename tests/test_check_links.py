"""Tests for the external-probe classification in scripts/check_links.py.

`_one_request` is replaced with a scripted sequence so each test controls the
responses a URL returns across attempts; no network is used.
"""

from __future__ import annotations

import importlib.util
import socket
import sys
import urllib.error
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("check_links", ROOT / "scripts" / "check_links.py")
check_links = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = check_links  # dataclasses resolve the defining module by name
assert _spec.loader is not None
_spec.loader.exec_module(check_links)


@pytest.fixture
def scripted(monkeypatch):
    """Feed a list of responses (status int or exception) to consecutive requests."""
    monkeypatch.setattr(check_links.time, "sleep", lambda s: None)

    def install(responses):
        queue = list(responses)
        calls = []

        def fake(url, method, timeout):
            calls.append(method)
            item = queue.pop(0) if len(queue) > 1 else queue[0]
            if isinstance(item, BaseException):
                raise item
            return item, None

        monkeypatch.setattr(check_links, "_one_request", fake)
        return calls

    return install


def probe(retries=2):
    cfg = check_links.Config()
    cfg.retries = retries
    return check_links.probe("https://example.org/page", cfg)


# #591 / F89: a single 404 or DNS failure used to be classified dead at once.
def test_404_that_recovers_on_retry_is_not_dead(scripted):
    scripted([404, 200])
    assert probe()[1] == "healthy"


def test_404_reproducing_on_every_attempt_is_dead(scripted):
    calls = scripted([404])
    severity, classification, reason = probe(retries=2)
    assert (severity, classification) == ("Critical", "dead")
    assert "3 attempts" in reason and len(calls) == 3


def test_dns_failure_that_recovers_is_not_dead(scripted):
    scripted([urllib.error.URLError(socket.gaierror("temporary failure")), 200])
    assert probe()[1] == "healthy"


def test_dns_failure_reproducing_on_every_attempt_is_dead(scripted):
    scripted([urllib.error.URLError(socket.gaierror("no such host"))])
    assert probe()[:2] == ("Critical", "dead")


def test_dead_mixed_with_server_errors_stays_transient(scripted):
    scripted([404, 503, 404])
    assert probe()[1] == "transient"


def test_server_errors_on_every_attempt_are_transient(scripted):
    scripted([503])
    assert probe()[:2] == ("Warning", "transient")
