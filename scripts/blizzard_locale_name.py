"""Read one verified Blizzard locale name from scalar or locale-keyed API data.

BCP-47 and Blizzard underscore locale tags are aliases, not competing names.
Conflicting alias values must fail closed before canonical ID projection.
Do not fall back across regions or infer a missing translation.
"""


def locale_name_values(value, locale):
    """Collect all nonempty names for one exact locale, including tag aliases."""
    if not isinstance(value, dict) or not isinstance(locale, str) or not locale.strip():
        return set()
    requested = locale.strip().replace("_", "-").casefold()
    return {
        name.strip()
        for key, name in value.items()
        if isinstance(key, str)
        and key.strip().replace("_", "-").casefold() == requested
        and isinstance(name, str)
        and name.strip()
    }


def has_conflicting_locale_aliases(value, locale):
    """A contradictory API hit must poison its entity ID, not be skipped."""
    return len(locale_name_values(value, locale)) > 1


def verified_locale_name(value, locale):
    if isinstance(value, str):
        return value.strip() or None
    names = locale_name_values(value, locale)
    return next(iter(names)) if len(names) == 1 else None
