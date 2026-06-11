"""Page objects for the E2E suite.

Re-export every page object here so test modules can import them from a single
place: ``from .pages import ExampleListPage``.
"""

from __future__ import annotations

from .base_page import BasePage
from .example_list_page import ExampleListPage

__all__ = ["BasePage", "ExampleListPage"]
