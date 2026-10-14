"""Regression contract: partial official API responses must not delete prior IDs or locales."""


def test_missing_locale_is_preserved():
    previous = {"101": {"en": "Example", "fr": "Exemple"}}
    incoming = {"101": {"en": "Example updated"}}
    merged = {key: {**previous.get(key, {}), **names} for key, names in incoming.items()}
    assert merged["101"]["fr"] == "Exemple"


def test_missing_id_is_preserved():
    previous = {"101": {"fr": "Exemple"}, "202": {"de": "Beispiel"}}
    incoming = {"101": {"en": "Example"}}
    merged = {**previous, **{key: {**previous.get(key, {}), **names} for key, names in incoming.items()}}
    assert merged["202"] == previous["202"]
