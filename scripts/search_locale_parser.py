"""Read canonical ID/name pairs from Blizzard's localized search results.

The search response wraps each entity in results[].data; walking nested
metadata would mistakenly treat class or category IDs as entity IDs.
"""


def extract_search_records(document, locales, response_locale=None):
    """Return {canonical_id: {language: official_name}}.

    locales maps language tags (e.g. "fr") to Blizzard locales ("fr_FR").
    Both localized name dictionaries and locale-specific string names work.
    """
    records = {}
    if not isinstance(document, dict):
        return records
    for result in document.get("results", []):
        if not isinstance(result, dict):
            continue
        entity = result.get("data")
        if not isinstance(entity, dict):
            continue
        entity_id, name = entity.get("id"), entity.get("name")
        if type(entity_id) is not int:
            continue
        names = {}
        if isinstance(name, dict):
            for language, locale in locales.items():
                value = name.get(locale)
                if isinstance(value, str) and value.strip():
                    names[language] = value.strip()
        elif isinstance(name, str) and name.strip():
            for language, locale in locales.items():
                if locale == response_locale:
                    names[language] = name.strip()
        if names:
            records[str(entity_id)] = names
    return records
