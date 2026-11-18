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
    re.compile(r"\b[Tt]he `" + NAME + r"` skill(?![\w-])"),
    re.compile(r"`" + NAME + r"`-Skill(?![\w-])"),
)


def references(text: str) -> list[tuple[int, str]]:
    """Every (line number, skill name) a delegation form names; a plugin prefix is dropped."""
    return [(lineno, name) for lineno, name, _ in matches(text)]


def matches(text: str) -> list[tuple[int, str, int]]:
    hits = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for index, form in enumerate(FORMS):
            hits.extend((lineno, match.group(1), index) for match in form.finditer(line))
    return hits


def shipped_skills() -> set[str]:
    manifests = [*ROOT.glob("skills/*/SKILL.md"), *ROOT.glob("plugins/*/skills/*/SKILL.md")]
    return {manifest.parent.name for manifest in manifests}


def builtin_skills() -> set[str]:
    lines = BUILTINS_FILE.read_text(encoding="utf-8").splitlines()
    return {line.strip() for line in lines if line.strip() and not line.strip().startswith("#")}


def scanned_roots() -> list[Path]:
    return [
        ROOT / "skills",
        ROOT / "agents",
        ROOT / "spec",
        *sorted(ROOT.glob("plugins/*/skills")),
        *sorted(ROOT.glob("plugins/*/agents")),
    ]


def scanned_files() -> list[Path]:
    return sorted(path for root in scanned_roots() for path in root.rglob("*.md"))


def unresolved(text: str, known: set[str]) -> list[tuple[int, str]]:
    return [(lineno, name) for lineno, name in references(text) if name not in known]


def test_detector_flags_each_form_and_accepts_known_names():
    known = {"spec", "security-review"}
    dead = (
        'Run `Skill(skill="no-such-skill")` first.\n'
        "The `no-such-skill` skill takes the result.\n"
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
    roots = scanned_roots()
    # The three top-level roots plus at least one plugin's skills and one plugin's agents.
    assert len(roots) >= 5, "a scanned root is missing; the layout moved"
    for root in roots:
        assert any(root.rglob("*.md")), f"{root.relative_to(ROOT)} holds no Markdown file; the layout moved"

    per_form = [0] * len(FORMS)
    dead = []
    for path in scanned_files():
        text = path.read_text(encoding="utf-8")
        for _, _, index in matches(text):
            per_form[index] += 1
        dead.extend(f"{path.relative_to(ROOT)}:{lineno}: `{name}`" for lineno, name in unresolved(text, known))

    # `Skill(skill="…")` has no corpus hit today; the detector test alone covers it.
    assert per_form[1], "the English prose form no longer matches the corpus"
    assert per_form[2], "the German prose form no longer matches the corpus"
    assert not dead, (
        "delegation to a skill that neither this repository ships nor the harness provides "
        f"({BUILTINS_FILE.relative_to(ROOT)}):\n" + "\n".join(dead)
    )
