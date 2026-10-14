from scripts.merge_entity_locales import project_locale_pairs


def test_incomplete_locales_keep_canonical_ids():
    entities = {"spell": {"1": {"en": "Name"}, "2": {"fr": "Nom"}}}
    assert all(str(i).isdigit() for bucket in entities.values() for i in bucket)
    assert project_locale_pairs(entities, "en", "fr") == {}
