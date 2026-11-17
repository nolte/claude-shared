"""`.vale.ini` opt-out sections switch off every rule `[*.md]` enables by name.

An opt-out section empties `BasedOnStyles`, which drops the style packages but not
a rule that a broader section turned on by name: Vale merges every matching
section, so `Microsoft.BiasFree = error` in `[*.md]` kept firing on the generated
catalog, the German tree, and the other opted-out paths. Each such rule has to be
set to `NO` in each opt-out section.
"""
from __future__ import annotations

import configparser
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _sections():
    parser = configparser.ConfigParser(interpolation=None, strict=False)
    parser.optionxform = str  # rule names are case-sensitive
    parser.read_string("[__global__]\n" + (REPO / ".vale.ini").read_text(encoding="utf-8"))
    return parser


def _named_rules(section) -> dict[str, str]:
    return {key: value for key, value in section.items() if "." in key}


def test_every_opt_out_section_disables_each_rule_md_enables_by_name():
    parser = _sections()
    enabled = {rule for rule, level in _named_rules(parser["*.md"]).items() if level.strip().upper() != "NO"}
    assert enabled, "[*.md] enables no rule by name; this guard has nothing to check"
    opt_outs = [name for name in parser.sections() if name not in ("__global__", "*.md")
                and parser[name].get("BasedOnStyles", None) is not None
                and not parser[name]["BasedOnStyles"].strip()]
    assert opt_outs, "no opt-out section found"
    missing = {name: sorted(rule for rule in enabled
                            if parser[name].get(rule, "").strip().upper() != "NO")
               for name in opt_outs}
    assert {name: rules for name, rules in missing.items() if rules} == {}
