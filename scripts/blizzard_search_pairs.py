"""Normalize Blizzard search results by canonical entity ID, independent of locale."""
try:
    from .blizzard_locale_name import verified_locale_name, has_conflicting_locale_aliases
except ImportError:  # Invoked as scripts from the build pipeline.
    from blizzard_locale_name import verified_locale_name, has_conflicting_locale_aliases




def search_names(document, locale):
    """Read only search-hit entities, never nested category or media IDs."""
    names = {}
    ambiguous = set()
    if not isinstance(document, dict):
        return names
    results = document.get("results", [])
    if not isinstance(results, list):
        return names
    for hit in results:
        data = hit.get("data") if isinstance(hit, dict) else None
        if not isinstance(data, dict):
            continue
        entity_id = data.get("id")
        if not isinstance(entity_id, int) or isinstance(entity_id, bool) or entity_id <= 0:
            continue
        key = str(entity_id)
        # A conflicting alias in any hit invalidates this ID, even if another
        # hit later offers a plausible single name for the same entity.
        if has_conflicting_locale_aliases(data.get("name"), locale):
            ambiguous.add(key)
            continue
        name = verified_locale_name(data.get("name"), locale)
        if not isinstance(name, str) or not name.strip():
            continue
        name = name.strip()
        if key in names and names[key] != name:
            ambiguous.add(key)
        else:
            names[key] = name
    for key in ambiguous:
        names.pop(key, None)
    return names


def collect_search_pairs(source_document, target_document, source_locale, target_locale,
                         source_key="en", target_key="fr"):
    """Retain canonical IDs even when only one locale returns a name.

    An incomplete ID cannot safely produce a whole-name translation, but it
    must still block a collision with a translated ID sharing its source name.
    The projection layer handles that ambiguity; never guess a missing name.
    """
    if source_key == target_key:
        raise ValueError("Source and target keys must differ")
    source = search_names(source_document, source_locale)
    target = search_names(target_document, target_locale)
    pairs = {key: {source_key: name} for key, name in source.items()}
    for key, name in target.items():
        pairs.setdefault(key, {})[target_key] = name
    return pairs
