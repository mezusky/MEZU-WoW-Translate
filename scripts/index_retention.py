"""Guard official Blizzard index coverage against partial API responses.

Canonical IDs can accumulate additional locale names over time. Refreshing
one translation pair must never erase another locale on a still-valid ID.
"""
try:
    from .merge_entity_locales import merge_rows
except ImportError:  # Executed as python scripts/build_datapack.py
    from merge_entity_locales import merge_rows


def retain_on_partial_index(kind, fresh, previous, min_ratio=0.8):
    """Refresh names by ID, retaining extra locales on surviving records.

    Normal complete index refreshes can retire missing IDs. Partial indexes
    retain older IDs; in either case, newly fetched names win per locale.
    """
    if previous and len(fresh) < len(previous) * min_ratio:
        print(f"WARN partial Blizzard index {kind}: {len(fresh)}/{len(previous)}; retaining prior IDs")
        return merge_rows(previous, fresh)
    surviving = {key: previous[key] for key in fresh if key in previous}
    return merge_rows(surviving, fresh)
