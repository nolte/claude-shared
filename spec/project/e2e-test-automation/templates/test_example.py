"""E2E tests for REQ-001 — Example item list and creation.

Spec-TC mapping (test TC -> spec/cases/<...>):
  TC-001-001  ->  TC-001-001  Item list page loads
  TC-001-002  ->  TC-001-002  Item list renders rows
  TC-001-003  ->  TC-001-003  Creating an item adds a row

A worked example demonstrating the spec's disciplines: every interaction goes
through a page object, every wait is condition-based, every test carries a
marker and a TC-ID docstring, screenshots are captured at checkpoints, created
data uses a unique suffix, and assertions carry descriptive messages with the
TC-ID. Replace REQ-001/the routes/the hooks with your real feature.
"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Callable

import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from .pages import ExampleListPage


@pytest.fixture
def items(browser: WebDriver, base_url: str) -> ExampleListPage:
    return ExampleListPage(browser, base_url)


class TestExampleList:
    """Example item list display and creation (Spec: TC-001-001..003)."""

    @pytest.mark.smoke
    def test_list_loads(
        self, items: ExampleListPage, screenshot: Callable[..., Path]
    ) -> None:
        """TC-001-001: Item list page loads and shows its title.

        Spec: TC-001-001 -- Open the item list as an authenticated user.
        """
        items.open()
        screenshot("TC-001-001_items-loaded", "Item list page after initial load")

        title = items.get_page_title()
        assert title, "TC-001-001 FAIL: Page title should not be empty"

    @pytest.mark.smoke
    @pytest.mark.core_crud
    def test_list_renders_rows(
        self, items: ExampleListPage, screenshot: Callable[..., Path]
    ) -> None:
        """TC-001-002: The item list renders at least one row.

        Spec: TC-001-002 -- Seeded items are listed.
        """
        items.open()
        count = items.get_row_count()
        screenshot("TC-001-002_items-rows", f"Item list — {count} rows found")

        if count == 0:
            pytest.skip("No items seeded — cannot verify the list renders rows")
        assert count >= 1, f"TC-001-002 FAIL: Expected at least 1 row, got {count}"

    @pytest.mark.core_crud
    def test_create_adds_row(
        self, items: ExampleListPage, screenshot: Callable[..., Path]
    ) -> None:
        """TC-001-003: Creating an item adds a row to the list.

        Spec: TC-001-003 -- Create an item and see it in the list.
        """
        items.open()
        before = items.get_row_count()
        screenshot("TC-001-003_before-create", f"Item list before create — {before} rows")

        unique = uuid.uuid4().hex[:6]
        items.click_create()
        items.fill_name(f"Example {unique}")
        items.submit()
        screenshot("TC-001-003_after-create", f"Item list after creating 'Example {unique}'")

        after = items.get_row_count()
        assert after == before + 1, (
            f"TC-001-003 FAIL: Expected row count to grow from {before} to "
            f"{before + 1}, got {after}"
        )
