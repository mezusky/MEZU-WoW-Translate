"""Merge exact translation layers without overriding canonical WoW entity names.

Canonical names are derived from verified Blizzard IDs. A prose override may
correct a sentence, but must not rename a spell/item/class with an official ID.
All inputs are data-only and already selected for the requested locale pair.
"""


def merge_exact_layers(canonical, official, community, manual):
    """Preserve ID-backed names; keep legacy manual prose precedence elsewhere.

    Casefold protection matters because downstream exact matching may ignore
    capitalization. A non-ID layer must not introduce an alternate translation
    of the same canonical source name with different casing.
    """
    merged = dict(canonical or {})
    protected = {name.casefold() for name in merged}
    for layer in (official, community):
        for source, target in (layer or {}).items():
            if (isinstance(source, str) and source.strip()
                    and isinstance(target, str) and target.strip()
                    and source.casefold() not in protected):
                merged.setdefault(source, target)
    for source, target in (manual or {}).items():
        if (isinstance(source, str) and source.strip()
                and isinstance(target, str) and target.strip()
                and source.casefold() not in protected):
            merged[source] = target
    return merged
