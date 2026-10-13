"""Merge canonical entity locale records without dropping old IDs."""

def merge_rows(old, new):
    out = {k: dict(v) for k, v in old.items()}
    for key, locales in new.items():
        out.setdefault(key, {}).update({k: v for k, v in locales.items() if isinstance(v, str) and v.strip()})
    return out
