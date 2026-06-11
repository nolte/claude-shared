# E2E reference templates — Selenium + pytest

These files are the normative **Selenium + pytest reference profile** for
`spec/project/e2e-test-automation/`. They are a starting scaffold, not a drop-in
library: copy them into a consuming project's `tests/e2e/`, then adapt the
marked spots to that app. The `e2e-test-generator` agent treats them as the
scaffold to adapt; the `e2e-test-reviewer` agent treats them as the conformance
baseline.

A project on a different stack (Playwright, Cypress) ignores these files and
satisfies the framework-neutral core of the spec with its own equivalents.

## Layout

```
tests/e2e/
  conftest.py            # CLI options, browser + screenshot fixtures, protocol, checkpointing
  protocol_plugin.py     # the machine-generated Markdown protocol
  requirements.txt       # selenium + pytest + webdriver-manager + xdist
  pages/
    __init__.py          # re-exports every page object
    base_page.py         # BasePage: waits, locators, interactions (the conformance baseline)
    example_list_page.py # a worked page-object example
  test_example.py        # a worked test: markers, TC-IDs, screenshots, descriptive assertions
```

## What to adapt

| Spot | File | Change |
|------|------|--------|
| Base URL | `conftest.py` `--base-url` default / `E2E_BASE_URL` | Point at your running app |
| Seeding | `conftest.py` `seed_data` | Replace the placeholder with idempotent seeding |
| Auth | `conftest.py` `browser` fixture (commented block) | Wire your login flow, or delete if none |
| Loading hook | `pages/base_page.py` `LOADING_INDICATOR` | Your app's "loading" test hook |
| Page-title / error hooks | `pages/base_page.py` `PAGE_TITLE`, `ERROR_DISPLAY` | Your app's standard hooks |
| Component helpers | `pages/base_page.py` `close_dropdown`, `clear_and_fill` | Tune for your UI framework |
| Spec resolution | `protocol_plugin.py` env vars | `E2E_SPEC_REQ_DIR`, `E2E_SPEC_TC_DIR`, `E2E_REQ_PATTERN`, `E2E_TC_ID_PATTERN` |
| Example page + test | `pages/example_list_page.py`, `test_example.py` | Replace with your real features |

## Run

```bash
pip install -r tests/e2e/requirements.txt

# all tests against a local app
pytest tests/e2e/ --base-url http://localhost:8080

# fast smoke subset
pytest tests/e2e/ -m smoke

# with the machine-generated protocol (test-reports/e2e/<ts>/protocol.md)
pytest tests/e2e/ --generate-protocol

# resume an interrupted run from its checkpoint
pytest tests/e2e/ --generate-protocol --resume test-reports/e2e/<ts>/
```

`test-reports/` is run output — add it to the consuming project's `.gitignore`.
