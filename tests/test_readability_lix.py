"""Conformance tests for scripts/readability_lix.py.

Each test pins an Acceptance Criterion from spec/project/readability-lix/. The
load-bearing one is the canonical formula: a hand-computed fixture must yield
exactly LIX = A/B + (C * 100)/A, never the transposed textstat docstring form.
"""
from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import readability_lix as lix  # noqa: E402


def test_canonical_formula_hand_fixture():
    # Two sentences, ten words, zero long words: LIX = 10/2 + 0 = 5.
    r = lix.compute("The cat sat on the mat. The dog ran fast.", "en", "explanation")
    assert r["words"] == 10
    assert r["sentences"] == 2
    assert r["long_words"] == 0
    assert r["lix"] == 5
    assert r["asl"] == 5.0
    assert r["lwp"] == 0.0


def test_canonical_formula_long_words():
    # Four words, all long, one sentence: LIX = 4/1 + (4*100)/4 = 104.
    r = lix.compute("Configuration management requires understanding.", "en", "explanation")
    assert (r["words"], r["sentences"], r["long_words"]) == (4, 1, 4)
    assert r["lix"] == 104
    # Guard against the transposed docstring formula A/B + A*100/C (= 4/1 + 4*100/4
    # happens to coincide here, so use an asymmetric fixture too):
    r2 = lix.compute("Configuration is short.", "en", "explanation")
    # words: Configuration(long), is, short -> A=3, C=1, B=1
    assert (r2["words"], r2["long_words"]) == (3, 1)
    # canonical: 3/1 + 1*100/3 = 36.33 -> 36 ; transposed (3/1 + 3*100/1)=303
    assert r2["lix"] == 36


def test_long_word_threshold_boundary():
    # 6 letters is NOT long; 7 letters IS long.
    r6 = lix.compute("Sixsix word here.", "en", "reference")  # 'Sixsix' = 6 letters
    assert r6["long_words"] == 0
    r7 = lix.compute("Sevenly word here.", "en", "reference")  # 'Sevenly' = 7 letters
    assert r7["long_words"] == 1


def test_numeric_token_never_long():
    r = lix.compute("Built 2026 on v1.2.0 fast.", "en", "reference")
    # 2026 and v1.2.0 count as words but neither is a long word (no short word
    # in the fixture exceeds 6 letters either).
    assert r["long_words"] == 0
    assert r["words"] == 5


def test_german_umlauts_count_as_letters():
    # 'Grüßen' = G r ü ß e n = 6 letters (not long); 'Begrüßung' = 9 letters (long).
    r = lix.compute("Begrüßung folgt.", "de", "tutorial")
    assert r["long_words"] == 1


def test_trailing_punctuation_does_not_change_classification():
    a = lix.compute("Konfiguration.", "de", "reference")
    b = lix.compute("Konfiguration", "de", "reference")
    assert a["long_words"] == b["long_words"] == 1


def test_code_and_links_stripped():
    md = (
        "Visit [the dashboard](https://example.com/very/long/path) now.\n\n"
        "```python\nthis_is_ignored_completely_longword = 1\n```\n\n"
        "Inline `also_ignored_longword` stays out.\n"
    )
    r = lix.compute(md, "en", "explanation")
    # Link text "the dashboard" is prose; the URL, the fenced block, and the
    # inline code must not contribute long words.
    assert r["long_words"] == 1  # only "dashboard" (9 letters)


def test_frontmatter_stripped():
    md = "---\ntitle: Supercalifragilistic\naudience: developers\n---\n\nShort text here.\n"
    r = lix.compute(md, "en", "reference")
    assert r["long_words"] == 0  # frontmatter value not counted


def test_abbreviation_and_decimal_no_false_boundary():
    r = lix.compute("We wait 3.14 seconds, e.g. now. Then we stop.", "en", "tutorial")
    assert r["sentences"] == 2


def test_meta_is_exempt():
    r = lix.compute("Configuration management overview navigation.", "en", "meta")
    assert r["exempt"] is True
    assert r["severity"] == "exempt"
    assert r["corridor"] is None


def test_german_offset_is_five():
    for key, modes in (("tutorial", "tutorial"), ("explanation", "reference"), ("blog", "blog")):
        en = lix.CORRIDORS["en"][key]
        de = lix.CORRIDORS["de"][key]
        assert de["warn"] - en["warn"] == 5
        assert de["crit"] - en["crit"] == 5


def test_de_corridors_match_lektorat_existing():
    # lektorat §D1 German LIX corridors must stay verbatim.
    assert lix.CORRIDORS["de"]["tutorial"]["warn"] == 50
    assert lix.CORRIDORS["de"]["tutorial"]["crit"] == 60
    assert lix.CORRIDORS["de"]["explanation"]["warn"] == 60
    assert lix.CORRIDORS["de"]["explanation"]["crit"] == 70


def test_severity_classification():
    # Force a high LIX (all long words, one sentence) on a tutorial page.
    high = lix.compute("Configuration management requires understanding.", "en", "tutorial")
    assert high["severity"] == "critical"  # 104 > 55
    low = lix.compute("The cat sat on the mat.", "en", "tutorial")
    assert low["severity"] == "ok"
    assert low["within_corridor"] is True


def test_dominant_lever_present():
    r = lix.compute("Configuration management requires understanding.", "en", "tutorial")
    assert r["dominant_lever"] == "LWP"  # lwp=100 dominates asl=4
    r2 = lix.compute(
        "the cat and the dog and the fox and the owl and the bee and the ant ran.",
        "en", "tutorial",
    )
    assert r2["dominant_lever"] == "ASL"  # long single sentence, short words


def test_pipeline_metadata_shape():
    en = lix.compute("Short text.", "en", "reference")["pipeline_metadata"]
    assert en["long_word_threshold"] == 6
    assert en["library"] == lix.LIBRARY
    assert "decompounding" not in en  # DE-only field
    de = lix.compute("Kurzer Text.", "de", "reference")["pipeline_metadata"]
    assert de["decompounding"] is False
