"""Collect canonical Blizzard index names without losing unpaired locale IDs.

Indexes, like search results, can return different IDs per locale. Keep
incomplete IDs so whole-name projection can detect ambiguous source names.
No text is translated or inferred by this module.
"""


def index_names(document, locale):
    names = {}
    ambiguous = set()

    def walk(value):
        if isinstance(value, list):
            for item in value:
                walk(item)
        elif isinstance(value, dict):
            entity_id = value.get("id")
            name = value.get("name")
            if isinstance(name, dict):
                name = name.get(locale) or name.get(locale.replace("_", "-"))
            if (isinstance(entity_id, int) and not isinstance(entity_id, bool)
                    and entity_id > 0 and isinstance(name, str) and name.strip()):
                key = str(entity_id)
                name = name.strip()
                if key in names and names[key] != name:
                    ambiguous.add(key)
                else:
                    names[key] = name
            for key, item in value.items():
                if key not in ("_links", "key", "media"):
                    walk(item)

    walk(document)
    for key in ambiguous:
        names.pop(key, None)
    return names


def collect_index_pairs(source_document, target_document, source_locale, target_locale,
                        source_key="en", target_key="fr"):
    """Union IDs by canonical ID; never fabricate missing localized names."""
    if source_key == target_key:
        raise ValueError("Source and target keys must differ")
    source = index_names(source_document, source_locale)
    target = index_names(target_document, target_locale)
    rows = {key: {source_key: name} for key, name in source.items()}
    for key, name in target.items():
        rows.setdefault(key, {})[target_key] = name
    return rows
