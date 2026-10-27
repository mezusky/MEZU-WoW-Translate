"""Guard official Blizzard index coverage against partial API responses.

Canonical IDs can accumulate additional locale names over time. Refreshing
one translation pair must never erase another locale on a still-valid ID.
"""
try:
    from .merge_entity_locales import merge_verified_locale_refresh
except ImportError:  # Executed as python scripts/build_datapack.py
    from merge_entity_locales import merge_verified_locale_refresh


def retain_on_partial_index(kind, fresh, previous, min_ratio=0.8,
                            source_key="en", target_key="fr"):
    """Refresh names by ID, retaining extra locales on surviving records.

    Normal complete index refreshes can retire missing IDs. Partial indexes
    retain older IDs. A one-sided locale refresh never pairs a new name
    with an old translation; complete pairs update together.
    """
    if previous and len(fresh) < len(previous) * min_ratio:
        print(f"WARN partial Blizzard index {kind}: {len(fresh)}/{len(previous)}; retaining prior IDs")
        return merge_verified_locale_refresh(previous, fresh, source_key, target_key)
    surviving = {key: previous[key] for key in fresh if key in previous}
    return merge_verified_locale_refresh(surviving, fresh, source_key, target_key)
