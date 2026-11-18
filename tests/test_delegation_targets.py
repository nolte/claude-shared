"""Guard: a skill that a skill, agent or spec delegates to exists.

`pull-request-merge` delegated its pre-merge review to a skill named `review` long after
the harness stopped shipping it; the text still read as an instruction and the gate
degraded to whatever the session improvised (#772, #778). A delegation reference
therefore has to name a skill this repository ships or one the harness provides (#782).
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILTINS_FILE = Path(__file__).resolve().parent / "data" / "harness-builtin-skills.txt"

NAME = r"/?(?:[a-z0-9][a-z0-9-]*:)?([a-z0-9][a-z0-9-]*)"
# The three delegation forms. The trailing lookahead keeps the plural ("`x` skills",
# "`x`-Skills") and compounds ("`x` skill-layer") out: those name a family or a spec, not
# one skill. The German genitive ("des `x`-Skills") shares the plural's spelling and is
# not checked either.
FORMS = (
    re.compile(r"""Skill\(\s*skill\s*=\s*["']""" + NAME + r"""["']"""),
    re.compile(r"\bthe `" + NAME + r"` skill(?![\w-])"),
    re.compile(r"`" + NAME + r"`-Skill(?![\w-])"),
)


def references(text: str) -> list[tuple[int, str]]:
    """Every (line number, skill name) a delegation form names; a plugin prefix is dropped."""
    hits = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for form in FORMS:
            hits.extend((lineno, match.group(1)) for match in form.finditer(line))
    return hits


def shipped_skills() -> set[str]:
    manifests = [*ROOT.glob("skills/*/SKILL.md"), *ROOT.glob("plugins/*/skills/*/SKILL.md")]
    return {manifest.parent.name for manifest in manifests}


def builtin_skills() -> set[str]:
    lines = BUILTINS_FILE.read_text(encoding="utf-8").splitlines()
    return {line.strip() for line in lines if line.strip() and not line.startswith("#")}


def scanned_files() -> list[Path]:
    roots = [
        ROOT / "skills",
        ROOT / "agents",
        ROOT / "spec",
        *ROOT.glob("plugins/*/skills"),
        *ROOT.glob("plugins/*/agents"),
    ]
    return sorted(path for root in roots for path in root.rglob("*.md"))


def unresolved(text: str, known: set[str]) -> list[tuple[int, str]]:
    return [(lineno, name) for lineno, name in references(text) if name not in known]


def test_detector_flags_each_form_and_accepts_known_names():
    known = {"spec", "security-review"}
    dead = (
        'Run `Skill(skill="no-such-skill")` first.\n'
        "Hand the result to the `no-such-skill` skill.\n"
        "Danach übernimmt der `no-such-skill`-Skill.\n"
    )
    assert unresolved(dead, known) == [(1, "no-such-skill"), (2, "no-such-skill"), (3, "no-such-skill")]

    alive = (
        'Run `Skill(skill="nolte-shared:spec")` first.\n'
        "Hand the result to the `/nolte-shared:spec` skill.\n"
        "Danach übernimmt der `security-review`-Skill.\n"
    )
    assert [name for _, name in references(alive)] == ["spec", "spec", "security-review"]
    assert unresolved(alive, known) == []


def test_detector_ignores_plurals_and_compounds():
    text = (
        "It dispatches the `release-skill-layer` skills.\n"
        "Es dispatcht `release-skill-layer`-Skills.\n"
        "See the `spec` skill-management notes.\n"
    )
    assert references(text) == []


def test_builtin_list_names_no_shipped_skill():
    # A name in both sets would hide the removal of the shipped skill.
    assert builtin_skills() & shipped_skills() == set()


def test_every_delegation_reference_names_an_existing_skill():
    known = shipped_skills() | builtin_skills()
    files = scanned_files()
    assert files, "no file scanned; the roots moved"

    total = 0
    dead = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        total += len(references(text))
        dead.extend(f"{path.relative_to(ROOT)}:{lineno}: `{name}`" for lineno, name in unresolved(text, known))

    assert total, "no delegation reference found; the patterns no longer match the corpus"
    assert not dead, (
        "delegation to a skill that neither this repository ships nor the harness provides "
        f"({BUILTINS_FILE.relative_to(ROOT)}):\n" + "\n".join(dead)
    )
