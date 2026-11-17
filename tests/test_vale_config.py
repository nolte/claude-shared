"""`.vale.ini` opt-out sections switch off every rule enabled by name elsewhere.

An opt-out section drops style packages from `BasedOnStyles`, but not a rule that a
broader section turned on by name: Vale merges every matching section, so
`Microsoft.BiasFree = error` in `[*.md]` kept firing on the generated catalog, the
German tree, and the other opted-out paths (#779). Each such rule has to be set to
`NO` in each section that drops its package.

The model below follows Vale 3.15.2's parsing, checked against the real binary (#780):

* Inline comments (`Rule = NO  # reason`, `; reason`) are stripped, so they are
  stripped here too.
* Rule names are case-sensitive (`microsoft.biasfree = NO` does not switch off
  `Microsoft.BiasFree`); the level is not (`no` works like `NO`).
* A section *opts out* of a package when it sets `BasedOnStyles` and that list
  omits the package: an empty list drops all of them, a partial one such as
  `BasedOnStyles = Vale` drops `Microsoft`.
* A section *enables* rules by name when it drops none of the packages any section
  bases on (it sets no `BasedOnStyles`, or lists them all). Every such rule whose
  level isn't `NO` must be `NO` in each opt-out that drops the rule's package
  (the package is the rule-name prefix before the first `.`).

* A section that is itself an opt-out can still enable a rule by name (for
  example `BasedOnStyles = Vale` plus `Microsoft.BiasFree = error`); that rule must
  then be `NO` in every *other* opt-out that drops its package.
* A package counts as known when any section bases on it or names one of its
  rules, so a rule from a package no `BasedOnStyles` lists is still checked.
* Vale strips a `#` or `;` comment after a value even without a space before it.

Limitation: section globs aren't intersected, so the check assumes every enabling
section can apply to every opted-out path. That over-approximates (it may demand a
`NO` that Vale wouldn't need), which errs on the safe side for a guard.
"""
from __future__ import annotations

import configparser
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
VALE_INI = REPO / ".vale.ini"
GLOBAL = "__global__"
ALL_PACKAGES = "*"  # marker: an empty `BasedOnStyles` drops every package


def load(path: Path = VALE_INI) -> configparser.ConfigParser:
    """Parse a Vale config the way Vale reads it (see the module docstring)."""
    parser = configparser.ConfigParser(
        interpolation=None, strict=False, inline_comment_prefixes=("#", ";"))
    parser.optionxform = str  # rule names are case-sensitive in Vale
    # Vale's global keys sit above the first section; give them a section name.
    parser.read_string(f"[{GLOBAL}]\n" + path.read_text(encoding="utf-8"))
    return parser


def _value(raw: str) -> str:
    """A value with a trailing `#`/`;` comment removed, as Vale reads it."""
    return re.split(r"[#;]", raw, maxsplit=1)[0].strip()


def _styles(section) -> list[str] | None:
    """The packages a section bases on, or None when it doesn't set `BasedOnStyles`."""
    if "BasedOnStyles" not in section:
        return None
    return [style.strip() for style in _value(section["BasedOnStyles"]).split(",") if style.strip()]


def _is_off(level: str) -> bool:
    return _value(level).upper() == "NO"


def _package(rule: str) -> str:
    return rule.split(".", 1)[0]


def leaks(parser: configparser.ConfigParser) -> dict[str, list[str]]:
    """Map each opt-out section to the named rules it fails to switch off.

    Raises AssertionError when the config has nothing to check, so a refactor that
    drops the named rule or the opt-outs can't make this guard pass vacuously.
    """
    sections = {name: parser[name] for name in parser.sections() if name != GLOBAL}
    named = {name: {rule: level for rule, level in section.items() if "." in rule}
             for name, section in sections.items()}
    based_on = set().union(*(_styles(section) or [] for section in sections.values()),
                           *({_package(rule) for rule in rules} for rules in named.values()))

    def dropped(section) -> set[str] | None:
        """Packages the section opts out of, or None if it isn't an opt-out."""
        styles = _styles(section)
        if styles is None or not based_on - set(styles):
            return None
        return {ALL_PACKAGES} if not styles else based_on - set(styles)

    opt_outs = {name: packages for name, section in sections.items()
                if (packages := dropped(section)) is not None}
    # rule -> the sections that enable it by name (an opt-out may enable one too)
    enabled: dict[str, set[str]] = {}
    for name, rules in named.items():
        for rule, level in rules.items():
            if not _is_off(level):
                enabled.setdefault(rule, set()).add(name)
    assert enabled, "no section enables a rule by name; this guard has nothing to check"
    assert opt_outs, "no opt-out section found"

    missing = {
        name: sorted(rule for rule, sources in enabled.items()
                     if sources - {name}
                     and (ALL_PACKAGES in packages or _package(rule) in packages)
                     and not _is_off(sections[name].get(rule, "")))
        for name, packages in opt_outs.items()
    }
    return {name: rules for name, rules in missing.items() if rules}


def test_every_opt_out_section_disables_each_rule_enabled_by_name():
    assert leaks(load()) == {}


# Fixture configs: each case pins one parsing rule the guard must model.
BASE = """\
StylesPath = .github/styles
MinAlertLevel = error

[*.md]
BasedOnStyles = Vale, Microsoft
Microsoft.BiasFree = error

[docs/de/**]
BasedOnStyles =
{opt_out}
"""


@pytest.mark.parametrize(("opt_out", "extra", "expected"), [
    pytest.param("Microsoft.BiasFree = NO", "", {}, id="disabled"),
    pytest.param("Microsoft.BiasFree = NO # reason", "", {}, id="inline-hash-comment"),
    pytest.param("Microsoft.BiasFree = NO ; reason", "", {}, id="inline-semicolon-comment"),
    pytest.param("Microsoft.BiasFree = no", "", {}, id="level-case-insensitive"),
    pytest.param("", "", {"docs/de/**": ["Microsoft.BiasFree"]}, id="missing-NO"),
    pytest.param("microsoft.biasfree = NO", "",
                 {"docs/de/**": ["Microsoft.BiasFree"]}, id="rule-name-case-sensitive"),
    pytest.param("Microsoft.BiasFree = NO",
                 "\n[CLAUDE.md]\nBasedOnStyles = Vale\n",
                 {"CLAUDE.md": ["Microsoft.BiasFree"]}, id="partial-opt-out-without-NO"),
    pytest.param("Microsoft.BiasFree = NO",
                 "\n[CLAUDE.md]\nBasedOnStyles = Vale\nMicrosoft.BiasFree = NO\n",
                 {}, id="partial-opt-out-with-NO"),
    pytest.param("Microsoft.BiasFree = NO",
                 "\n[CLAUDE.md]\nBasedOnStyles = Microsoft\n",
                 {}, id="partial-opt-out-keeping-the-rule-package"),
    pytest.param("Microsoft.BiasFree = NO",
                 "\n[docs/**]\nBasedOnStyles = Vale, Microsoft\nVale.Repetition = error\n",
                 {"docs/de/**": ["Vale.Repetition"]}, id="second-enabling-section"),
    pytest.param("Microsoft.BiasFree = NO",
                 "\n[{docs,spec}/**.md]\nMicrosoft.Passive = error\n",
                 {"docs/de/**": ["Microsoft.Passive"]}, id="section-without-BasedOnStyles"),
    pytest.param("Microsoft.BiasFree = NO#reason", "", {}, id="comment-without-space"),
    pytest.param("Microsoft.BiasFree = NO",
                 "\n[docs/**]\nBasedOnStyles = Vale\nMicrosoft.Passive = error\n",
                 {"docs/de/**": ["Microsoft.Passive"], "docs/**": ["Microsoft.BiasFree"]},
                 id="opt-out-that-enables-a-rule"),
    pytest.param("Microsoft.BiasFree = NO",
                 "\n[*.md]\nwrite-good.Weasel = error\n\n[CLAUDE.md]\nBasedOnStyles = Vale\n",
                 {"CLAUDE.md": ["Microsoft.BiasFree", "write-good.Weasel"],
                  "docs/de/**": ["write-good.Weasel"]},
                 id="rule-from-a-package-no-section-bases-on"),
])
def test_guard_models_vale_parsing(tmp_path, opt_out, extra, expected):
    config = tmp_path / ".vale.ini"
    config.write_text(BASE.format(opt_out=opt_out) + extra, encoding="utf-8")
    assert leaks(load(config)) == expected


@pytest.mark.parametrize("text", [
    pytest.param("[*.md]\nBasedOnStyles = Vale, Microsoft\n\n[x/**]\nBasedOnStyles =\n",
                 id="no-rule-enabled-by-name"),
    pytest.param("[*.md]\nBasedOnStyles = Vale, Microsoft\nMicrosoft.BiasFree = error\n",
                 id="no-opt-out"),
])
def test_guard_refuses_a_vacuous_config(tmp_path, text):
    config = tmp_path / ".vale.ini"
    config.write_text(text, encoding="utf-8")
    with pytest.raises(AssertionError):
        leaks(load(config))
