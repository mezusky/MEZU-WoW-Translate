"""Select player terminology only for the requested translation direction.

The current published Data Pack is EN->FR. This module is deliberately locale
neutral so additional target-language glossaries cannot silently leak into it.
Remote glossaries remain data-only; no executable rules are downloaded.
"""


def normalize_locale(locale):
    if not isinstance(locale, str) or not locale.strip():
        raise ValueError("Language must be a non-empty locale string")
    return locale.strip().replace("_", "-").casefold()


def locale_matches(configured, requested):
    """A generic 'fr' glossary can serve fr-FR; fr-CA cannot serve fr-FR."""
    configured = normalize_locale(configured)
    requested = normalize_locale(requested)
    return configured == requested or (
        "-" not in configured and requested.startswith(configured + "-")
    )


def select_jargon(glossary, source_language, target_language):
    """Return validated terms for a locale pair, rejecting wrong-language data.

    An identical source/target locale never requires translation.
    Mismatched glossaries fail closed instead of contaminating another locale.
    """
    source = normalize_locale(source_language)
    target = normalize_locale(target_language)
    if source == target:
        return {}
    if not isinstance(glossary, dict):
        raise ValueError("Glossary must be a JSON object")
    if not locale_matches(glossary.get("sourceLanguage"), source):
        raise ValueError("Player glossary source language does not match pack")
    if not locale_matches(glossary.get("targetLanguage"), target):
        raise ValueError("Player glossary target language does not match pack")
    terms = glossary.get("jargon", {})
    if not isinstance(terms, dict):
        raise ValueError("Player glossary jargon must be an object")
    if any(not isinstance(k, str) or not k.strip() or
           not isinstance(v, str) or not v.strip()
           for k, v in terms.items()):
        raise ValueError("Player glossary contains an invalid term")
    return dict(terms)
