"""Merge canonical entity locale records without dropping old IDs."""

def merge_rows(old, new):
    out = {k: dict(v) for k, v in old.items()}
    for key, locales in new.items():
        out.setdefault(key, {}).update({k: v for k, v in locales.items() if isinstance(v, str) and v.strip()})
    return out


def project_locale_pairs(entities, source_language, target_language):
    """Build only unambiguous exact names for one locale pair.

    Canonical ID/locale records remain intact even when either locale is absent.
    """
    # Regional variants of one language do not need a translated name.
    if source_language.replace("_", "-").casefold().split("-")[0] == target_language.replace("_", "-").casefold().split("-")[0]:
        return {}
    candidates = {}
    incomplete = set()
    for bucket in entities.values():
        for row in bucket.values():
            source = row.get(source_language)
            target = row.get(target_language)
            if not isinstance(source, str) or not source.strip():
                continue
            if not isinstance(target, str) or not target.strip():
                incomplete.add(source)
                continue
            candidates.setdefault(source, set()).add(target)
    return {source: next(iter(targets)) for source, targets in candidates.items() if len(targets) == 1 and source not in incomplete}
