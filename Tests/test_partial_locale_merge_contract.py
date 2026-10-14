"""Regression contracts exercise the production canonical-ID merge functions."""

from scripts.merge_entity_locales import merge_rows, project_locale_pairs


def test_missing_locale_is_preserved():
    previous = {"spell": {"101": {"en": "Example", "fr": "Exemple"}}}
    incoming = {"spell": {"101": {"en": "Example updated"}}}
    merged = merge_rows(previous["spell"], incoming["spell"])
    assert merged["101"] == {"en": "Example updated", "fr": "Exemple"}


def test_missing_id_is_preserved():
    previous = {"101": {"fr": "Exemple"}, "202": {"de": "Beispiel"}}
    merged = merge_rows(previous, {"101": {"en": "Example"}})
    assert merged["202"] == previous["202"]


def test_blank_locale_does_not_erase_previous_translation():
    previous = {"101": {"en": "Example", "fr": "Exemple"}}
    merged = merge_rows(previous, {"101": {"fr": ""}})
    assert merged["101"]["fr"] == "Exemple"


def test_locale_projection_is_language_agnostic():
    entities = {"spell": {"101": {"de": "Licht", "fr": "Lumière"}}}
    assert project_locale_pairs(entities, "de", "fr") == {"Licht": "Lumière"}
    assert project_locale_pairs(entities, "de", "de") == {}
