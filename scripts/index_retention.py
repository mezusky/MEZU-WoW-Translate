"""Guard official Blizzard index coverage against partial API responses."""


def retain_on_partial_index(kind, fresh, previous, min_ratio=0.8):
    """Keep old canonical IDs only when an index shrinks unexpectedly.

    Normal complete index refreshes replace old data so retired IDs can expire.
    A partial response keeps previous entries, with fresh official names winning.
    """
    if previous and len(fresh) < len(previous) * min_ratio:
        print(f"WARN partial Blizzard index {kind}: {len(fresh)}/{len(previous)}; retaining prior IDs")
        return {**previous, **fresh}
    return fresh
