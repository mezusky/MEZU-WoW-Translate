"""Merge canonical entity locale records without dropping old IDs."""


def _locale_alias(value):
    """Treat Blizzard en_US and BCP-47 en-US as the same locale identity."""
    return value.strip().replace("_", "-").casefold()


def _alias_values(row, requested):
    """All nonempty names for one exact locale, without regional fallback."""
    locale = _locale_alias(requested)
    return {
        value.strip() for key, value in row.items()
        if isinstance(key, str) and _locale_alias(key) == locale
        and isinstance(value, str) and value.strip()
    }


def merge_rows(old, new):
    out = {k: dict(v) for k, v in old.items()}
    for key, locales in new.items():
        out.setdefault(key, {}).update({k: v.strip() for k, v in locales.items() if isinstance(v, str) and v.strip()})
    return out


def merge_verified_locale_refresh(previous, fresh, source_key, target_key):
    """Refresh only verified locale pairs, including equivalent locale aliases.

    An incomplete response must not combine a renamed source with a stale
    target. When an ID is refreshed, old en-US/en_US aliases for the refreshed
    locales must be replaced, not retained as conflicting official names.
    """
    if _locale_alias(source_key) == _locale_alias(target_key):
        raise ValueError("Source and target keys must differ")

    def complete_pair(names):
        # Conflicting aliases are not verified names. Empty strings are not
        # evidence of a fresh translation, even if the old row has a value.
        return all(len(_alias_values(names, key)) == 1
                   for key in (source_key, target_key))

    accepted = {
        key: names for key, names in fresh.items()
        if key not in previous or complete_pair(names)
    }
    merged = merge_rows(previous, accepted)
    for entity_id, names in accepted.items():
        if entity_id not in previous or not complete_pair(names):
            continue
        old_source_names = _alias_values(previous[entity_id], source_key)
        new_source_name = next(iter(_alias_values(names, source_key)))
        refreshed_locales = {
            _locale_alias(key) for key, value in names.items()
            if isinstance(key, str) and isinstance(value, str) and value.strip()
        }
        renamed_source = bool(old_source_names and
                              old_source_names != {new_source_name})
        for old_key in previous[entity_id]:
            old_locale = _locale_alias(old_key)
            # Remove stale alternate spellings (en-US vs en_US) for every
            # refreshed locale, even when the source name has not changed.
            if old_locale in refreshed_locales and old_key not in names:
                merged[entity_id].pop(old_key, None)
            # A verified source rename invalidates omitted third-language
            # names until those locales are fetched and verified together.
            elif renamed_source and old_locale not in refreshed_locales:
                merged[entity_id].pop(old_key, None)
    return merged

def _locale_name(row, requested):
    """Prefer the exact locale, then its generic language; never another region.

    Canonical records currently use ``en``/``fr``, while future callers may
    request ``en-US``/``fr-FR``. Regional names must not leak across regions.
    """
    requested = _locale_alias(requested)
    # Blizzard and imported data can use both en_US and en-US. These are
    # aliases of one locale, not two independently trusted translations.
    # Reject conflicting labels rather than letting dict insertion order
    # silently choose an official name for a canonical entity ID.
    names, conflicts = {}, set()
    for key, value in row.items():
        if not isinstance(key, str) or not isinstance(value, str) or not value.strip():
            continue
        locale = _locale_alias(key)
        name = value.strip()
        if locale in names and names[locale] != name:
            conflicts.add(locale)
        else:
            names[locale] = name
    if requested in conflicts:
        return None
    if requested in names:
        return names[requested]
    if "-" in requested:
        generic = requested.split("-", 1)[0]
        return None if generic in conflicts else names.get(generic)
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
    # Whole-name matching may be case-insensitive in downstream consumers.
    # Two IDs that differ only by source capitalization must not project
    # conflicting localized names; likewise a missing target blocks the
    # case-folded source family. Preserve harmless capitalization variants.
    folded_targets = {}
    for name, translations in candidates.items():
        folded_targets.setdefault(name.casefold(), set()).update(
            value.casefold() for value in translations
        )
    incomplete_folded = {name.casefold() for name in incomplete}
    return {
        name: next(iter(translations))
        for name, translations in candidates.items()
        if len(translations) == 1
        and name.casefold() not in incomplete_folded
        and len(folded_targets[name.casefold()]) == 1
    }
