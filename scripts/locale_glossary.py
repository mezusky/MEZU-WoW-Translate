"""Select player terminology only for the requested translation direction.

The current published Data Pack is EN->FR. This module is deliberately locale
neutral so additional target-language glossaries cannot silently leak into it.
Remote glossaries remain data-only; no executable rules are downloaded.
"""


def normalize_locale(locale):
    if not isinstance(locale, str) or not locale.strip():
        raise ValueError("Language must be a non-empty locale string")
    return locale.strip().replace("_", "-").casefold()


def same_base_language(source_language, target_language):
    """Regional variants share a base language and require no translation."""
    source = normalize_locale(source_language).split("-", 1)[0]
    target = normalize_locale(target_language).split("-", 1)[0]
    return source == target


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
    if same_base_language(source, target):
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


def select_locale_data(payload, source_language, target_language, legacy_pair=None, canonical_pair=None):
    """Select a data-only layer without leaking a different translation direction.

    Generic locale-tagged layers (en -> fr) may serve regional requests
    (en-US -> fr-FR), but a region-specific layer must never serve a generic
    request or a different region. An explicitly declared canonical regional
    pair may serve a generic pack (e.g. official en-US/fr-FR Blizzard memory
    in an en/fr pack), but only by opt-in and never across regional requests.
    Untagged legacy data is accepted only for its explicitly declared pair.
    """
    if not isinstance(payload, dict):
        raise ValueError("Translation data layer must be a JSON object")
    source = normalize_locale(source_language)
    target = normalize_locale(target_language)
    if same_base_language(source, target):
        return {}
    layer_source = payload.get("sourceLanguage")
    layer_target = payload.get("targetLanguage")
    if layer_source is None and layer_target is None:
        if legacy_pair is None or len(legacy_pair) != 2:
            return {}
        if (source, target) != tuple(normalize_locale(x) for x in legacy_pair):
            return {}
        return payload
    if layer_source is None or layer_target is None:
        raise ValueError("Translation data layer has incomplete locale metadata")
    def matches(configured, requested, canonical):
        if locale_matches(configured, requested):
            return True
        # A generic pack may explicitly opt into its canonical official
        # regional source; a fr-CA layer must not silently enter a fr-FR pack.
        return (canonical is not None
                and "-" not in requested
                and normalize_locale(configured) == normalize_locale(canonical)
                and normalize_locale(canonical).split("-")[0] == requested)

    if canonical_pair is not None:
        if not isinstance(canonical_pair, (tuple, list)) or len(canonical_pair) != 2:
            raise ValueError("Canonical locale pair must contain source and target")
    canonical_source, canonical_target = canonical_pair if canonical_pair else (None, None)
    if not matches(layer_source, source, canonical_source):
        return {}
    if not matches(layer_target, target, canonical_target):
        return {}
    return payload
