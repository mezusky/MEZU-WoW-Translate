from scripts.merge_entity_locales import project_locale_pairs


def test_incomplete_locales_keep_canonical_ids():
    entities = {"spell": {"1": {"en": "Name"}, "2": {"fr": "Nom"}}}
    assert all(str(i).isdigit() for bucket in entities.values() for i in bucket)
    assert project_locale_pairs(entities, "en", "fr") == {}


def test_same_locale_skips_translation():
    entities = {"spell": {"42": {"en": "Arcane", "fr": "Arcanes"}}}
    assert project_locale_pairs(entities, "en", "en") == {}


def test_ambiguous_incomplete_ids_do_not_leak_into_exact_pairs():
    entities = {"spell": {
        "1": {"en": "Shared", "fr": "Partagé"},
        "2": {"en": "Shared"},
        "3": {"en": "Unique", "fr": "Unique FR"},
    }}
    assert project_locale_pairs(entities, "en", "fr") == {"Unique": "Unique FR"}

def test_collision_guard_applies_across_entity_types_and_locales():
    entities = {
        "spell": {"1": {"de": "Echo", "fr": "Écho"}},
        "item": {"2": {"de": "Echo"}, "3": {"de": "Schild", "fr": "Bouclier"}},
    }
    assert project_locale_pairs(entities, "de", "fr") == {"Schild": "Bouclier"}
