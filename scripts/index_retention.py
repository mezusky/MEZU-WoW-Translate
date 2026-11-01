"""Guard official Blizzard index coverage against partial API responses.

Canonical IDs can accumulate additional locale names over time. A single API
response cannot establish that a missing ID was retired, even when its size
looks nearly complete. Preserve learned IDs by default; allow retirement only
after independent completeness verification.
"""
try:
    from .merge_entity_locales import merge_verified_locale_refresh
except ImportError:  # Executed as python scripts/build_datapack.py
    from merge_entity_locales import merge_verified_locale_refresh


def retain_on_partial_index(kind, fresh, previous, min_ratio=0.8,
                            source_key="en", target_key="fr",
                            allow_retirement=False):
    """Refresh names by canonical ID without treating a partial index as deletion.

    A single Blizzard index response cannot prove an absent ID was retired.
    By default retain all previously verified IDs, even if 90% of the index
    returned successfully. This prevents silent cumulative data loss from
    transient omissions that fall above the historical 80% threshold.

    A caller may explicitly permit retirement only after independently
    confirming a complete index. Even then, suspiciously small responses
    retain old IDs and all refreshed IDs require verified locale pairs.
    """
    if previous and len(fresh) < len(previous) * min_ratio:
        print(f"WARN partial Blizzard index {kind}: {len(fresh)}/{len(previous)}; retaining prior IDs")
        return merge_verified_locale_refresh(previous, fresh, source_key, target_key)
    if not allow_retirement:
        if previous and len(fresh) < len(previous):
            print(f"INFO unconfirmed Blizzard index omissions {kind}: "
                  f"{len(set(previous) - set(fresh))} IDs retained")
        return merge_verified_locale_refresh(previous, fresh, source_key, target_key)
    surviving = {key: previous[key] for key in fresh if key in previous}
    return merge_verified_locale_refresh(surviving, fresh, source_key, target_key)
