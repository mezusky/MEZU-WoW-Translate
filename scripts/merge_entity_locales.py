"""Merge canonical entity locale records without dropping old IDs."""


def merge_rows(old, new):
    out = {k: dict(v) for k, v in old.items()}
    for key, locales in new.items():
        out.setdefault(key, {}).update({k: v for k, v in locales.items() if isinstance(v, str) and v.strip()})
    return out


def merge_verified_locale_refresh(previous, fresh, source_key, target_key):
    """Keep incomplete new IDs without pairing asynchronous locale snapshots.

    Search responses can be missing one locale. A partial refresh for an
    existing ID must not combine a newly renamed source with an older target
    (or vice versa) and publish a false official translation. Only refresh
    an existing ID's translation pair when both names arrive together.
    New unpaired IDs remain visible to the collision guard.
    """
    if source_key == target_key:
        raise ValueError("Source and target keys must differ")
    accepted = {
        key: names for key, names in fresh.items()
        if key not in previous or
        (source_key in names and target_key in names)
    }
    return merge_rows(previous, accepted)


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
