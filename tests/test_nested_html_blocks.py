"""Regression coverage for HTML audit block extraction."""
from scripts.html_block_extractor import extract_blocks


def test_hidden_script_is_not_prose():
    assert extract_blocks("<p>A<script>ignore</script>B</p>") == [("p", "A B")]


def test_inline_link_preserves_words():
    assert extract_blocks("<p>Use <a href=\"/spell=1\">Penance</a> now</p>") == [("p", "Use Penance now")]
