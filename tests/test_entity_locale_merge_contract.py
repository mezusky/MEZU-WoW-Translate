from scripts.merge_entity_locales import project_locale_pairs, merge_verified_locale_refresh


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

def test_partial_search_refresh_does_not_pair_new_source_with_stale_target():
    previous = {"7": {"en": "Old Spell", "fr": "Ancien sort", "de": "Alter Zauber"}}
    fresh = {
        "7": {"en": "Renamed Spell"},
        "8": {"en": "Unpaired Spell"},
    }
    merged = merge_verified_locale_refresh(previous, fresh, "en", "fr")
    assert merged["7"] == previous["7"]
    assert merged["8"] == {"en": "Unpaired Spell"}
    assert project_locale_pairs({"spell": merged}, "en", "fr") == {
        "Old Spell": "Ancien sort"
    }


def test_partial_search_refresh_does_not_pair_new_target_with_stale_source():
    previous = {"7": {"en": "Old Spell", "fr": "Ancien sort"}}
    fresh = {"7": {"fr": "Nouveau sort"}, "8": {"fr": "Nom seulement"}}
    merged = merge_verified_locale_refresh(previous, fresh, "en", "fr")
    assert merged["7"] == previous["7"]
    assert merged["8"] == {"fr": "Nom seulement"}


def test_complete_search_refresh_updates_pair_and_keeps_other_locales():
    previous = {"7": {"en": "Old Spell", "fr": "Ancien sort", "de": "Alter Zauber"}}
    fresh = {"7": {"en": "New Spell", "fr": "Nouveau sort"}}
    merged = merge_verified_locale_refresh(previous, fresh, "en", "fr")
    assert merged["7"] == {
        "en": "New Spell", "fr": "Nouveau sort", "de": "Alter Zauber"
    }
    assert project_locale_pairs({"spell": merged}, "en", "fr") == {
        "New Spell": "Nouveau sort"
    }


def test_generic_locale_keys_and_invalid_identical_pair():
    previous = {"1": {"de": "Alt", "fr": "Ancien"}}
    assert merge_verified_locale_refresh(
        previous, {"1": {"de": "Neu"}}, "de", "fr"
    ) == previous
    try:
        merge_verified_locale_refresh(previous, {}, "fr", "fr")
    except ValueError:
        pass
    else:
        raise AssertionError("Identical locale keys must fail")
