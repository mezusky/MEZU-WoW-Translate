"""Merge canonical entity locale records without dropping old IDs."""


def merge_rows(old, new):
    out = {k: dict(v) for k, v in old.items()}
    for key, locales in new.items():
        out.setdefault(key, {}).update({k: v for k, v in locales.items() if isinstance(v, str) and v.strip()})
    return out


def _locale_name(row, requested):
    """Prefer the exact locale, then its generic language; never another region.

    Canonical records currently use ``en``/``fr``, while future callers may
    request ``en-US``/``fr-FR``. Regional names must not leak across regions.
    """
    requested = requested.strip().replace("_", "-").casefold()
    names = {
        key.strip().replace("_", "-").casefold(): value
        for key, value in row.items()
        if isinstance(key, str) and isinstance(value, str) and value.strip()
    }
    if requested in names:
        return names[requested]
    if "-" in requested:
        return names.get(requested.split("-", 1)[0])
    return None


def project_locale_pairs(entities, source_language, target_language):
    """Project unambiguous canonical names for any supported locale direction.

    Generic canonical names may serve regional requests. Specific regional
    names never silently serve another region or a generic locale. Incomplete
    or conflicting IDs cannot contribute an unsafe whole-name translation.
    """
    source = source_language.strip().replace("_", "-").casefold()
    target = target_language.strip().replace("_", "-").casefold()
    if source.split("-")[0] == target.split("-")[0]:
        return {}
    candidates = {}
    incomplete = set()
    for bucket in entities.values():
        for row in bucket.values():
            source_name = _locale_name(row, source)
            target_name = _locale_name(row, target)
            if not source_name:
                continue
            if not target_name:
                incomplete.add(source_name)
                continue
            candidates.setdefault(source_name, set()).add(target_name)
    return {
        name: next(iter(translations))
        for name, translations in candidates.items()
        if len(translations) == 1 and name not in incomplete
    }
