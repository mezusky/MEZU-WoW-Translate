"""Fail-closed locale contract for source-only Wowhead regression audits.

This validates whether the *published* Data Pack can be used to score a
requested translation direction. It does not perform browser translation.
"""
import re

if __package__:
    from .locale_glossary import locale_matches, normalize_locale, same_base_language
else:  # Direct execution of scripts/analyze_wowhead_guides.py
    from locale_glossary import locale_matches, normalize_locale, same_base_language

_LOCALE = re.compile(r"[a-z]{2,3}(?:-[a-z0-9]{2,8})*", re.IGNORECASE)


def resolve_audit_locale_contract(config, pack):
    """Return an explicit audit status without borrowing another locale's data.

    A generic pack can serve regional requests, but a region-specific pack
    cannot silently serve another region or an unspecified generic locale.
    When source and target share a base language, no translation is needed.
    """
    if not isinstance(config, dict) or not isinstance(pack, dict):
        raise ValueError("Audit configuration and Data Pack must be objects")
    source = config.get("sourceLanguage", pack.get("sourceLanguage"))
    target = config.get("targetLanguage", pack.get("targetLanguage"))
    pack_source = pack.get("sourceLanguage")
    pack_target = pack.get("targetLanguage")
    try:
        source, target, pack_source, pack_target = (
            normalize_locale(value) for value in
            (source, target, pack_source, pack_target)
        )
    except ValueError:
        return {"sourceLanguage": source, "targetLanguage": target,
                "canScore": False, "status": "invalid_locale"}
    if not all(_LOCALE.fullmatch(value) for value in
               (source, target, pack_source, pack_target)):
        return {"sourceLanguage": source, "targetLanguage": target,
                "canScore": False, "status": "invalid_locale"}
    if same_base_language(source, target):
        return {"sourceLanguage": source, "targetLanguage": target,
                "canScore": False, "status": "skipped_same_language"}
    if not (locale_matches(pack_source, source)
            and locale_matches(pack_target, target)):
        return {"sourceLanguage": source, "targetLanguage": target,
                "canScore": False, "status": "pack_locale_mismatch"}
    return {"sourceLanguage": source, "targetLanguage": target,
            "canScore": True, "status": "ready"}
