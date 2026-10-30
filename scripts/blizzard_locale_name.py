"""Read one verified Blizzard locale name from scalar or locale-keyed API data.

BCP-47 and Blizzard underscore locale tags are aliases, not competing names.
Conflicting alias values must fail closed before canonical ID projection.
Do not fall back across regions or infer a missing translation.
"""


def verified_locale_name(value, locale):
    if isinstance(value, str):
        return value.strip() or None
    if not isinstance(value, dict) or not isinstance(locale, str) or not locale.strip():
        return None
    requested = locale.strip().replace("_", "-").casefold()
    names = {
        name.strip()
        for key, name in value.items()
        if isinstance(key, str)
        and key.strip().replace("_", "-").casefold() == requested
        and isinstance(name, str)
        and name.strip()
    }
    return next(iter(names)) if len(names) == 1 else None
