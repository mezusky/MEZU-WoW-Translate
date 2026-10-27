"""Conservative, locale-extensible language evidence for source-only audits.

Profiles are data-only; this is NOT the Chrome Translator API or a browser
language detector. Unknown/mixed evidence must never be counted as a failure.
"""
import re

TOKEN = re.compile(r"[^\W\d_]+", re.UNICODE)
# Generated UI placeholders are not prose, even inside otherwise readable cells.
NON_PROSE_PLACEHOLDER = re.compile(r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b")
# Indexed guide widgets can leak key=value configuration (e.g. stat-guide=32588
# or stats=Int>mastery>haste). Such formulas are not natural-language prose.
NON_PROSE_ASSIGNMENT = re.compile(r"\b[a-z][a-z0-9-]{1,40}=[^\s\]\[]+")
# UI/CDM import strings are serialized configuration, not translatable prose.
# Require a long base64-like body to avoid hiding ordinary numbered text.
OPAQUE_IMPORT = re.compile(r"(?<!\S)\d+\|[A-Za-z0-9+/=]{80,}(?!\S)")

# WoW Edit Mode exports are long, whitespace-separated layout records rather
# than base64 CDM strings. Only suppress a whole import cell with a recognized
# header and multiple frame records; ordinary text mentioning UIParent stays.
EDIT_MODE_HEADER = re.compile(
    r"^2\s+\d+(?:\s+[01]){3}(?:\s+\d+){2}\s+[A-Za-z][A-Za-z0-9]*\b"
)
EDIT_MODE_FRAME = re.compile(r"\b(?:UIParent|[A-Za-z][A-Za-z0-9]*Frame)\b")


def is_opaque_edit_mode_export(text):
    value = text.strip()
    return (len(value) >= 250 and bool(EDIT_MODE_HEADER.match(value))
            and len(EDIT_MODE_FRAME.findall(value)) >= 3
            and value.count(" -1 ") >= 3)


def clean_non_prose(text):
    """Remove generated widget assignments and opaque import payloads."""
    if is_opaque_edit_mode_export(text):
        return ""
    return NON_PROSE_ASSIGNMENT.sub(" ", NON_PROSE_PLACEHOLDER.sub(" ",
                                     OPAQUE_IMPORT.sub(" ", text)))
PROSE_TAGS = frozenset(("p", "li", "td", "th"))


def audit_source_prose(text, source_language, profiles):
    """Clean widget payloads and check prose in the configured source locale.

    This is a source-only audit filter, not a translation-quality classifier.
    A language-specific profile can be added as data without changing code.
    Regional locales use their exact profile, or the base-language profile.
    """
    if not isinstance(text, str):
        return "", False
    locale = source_language.strip().replace("_", "-").casefold()
    words = profiles.get(locale, profiles.get(locale.split("-")[0]))
    if not isinstance(words, list) or not words:
        raise ValueError("Missing source-language audit profile: " + locale)
    clean = clean_non_prose(text)
    clean = " ".join(clean.split()).strip()
    tokens = set(TOKEN.findall(clean.casefold()))
    return clean, bool(tokens & {word.casefold() for word in words})




def detect_source_language(blocks, profiles, min_tokens=25, min_hits=7):
    """Infer a language only when prose strongly favors one configured profile.

    Ignore headings (often English even on localized pages), repeated blocks,
    and long calculator/import payloads. Mixed official spell names should not
    outweigh surrounding prose. Returns evidence, not a probability estimate.
    """
    if not isinstance(profiles, dict) or not profiles:
        raise ValueError("Language evidence profiles must be a nonempty object")
    signals = {}
    for locale, words in profiles.items():
        if not isinstance(locale, str) or not locale.strip() or not isinstance(words, list):
            raise ValueError("Invalid language evidence profile")
        if any(not isinstance(word, str) or not word.strip() for word in words):
            raise ValueError("Invalid language evidence word")
        signals[locale.strip().replace("_", "-").casefold()] = {
            word.casefold() for word in words
        }
    seen, tokens = set(), []
    for tag, value in blocks:
        if tag not in PROSE_TAGS or not isinstance(value, str):
            continue
        # Strip long serialized UI data before the prose-length guard.
        # Otherwise a valid paragraph next to an import is silently lost.
        clean = clean_non_prose(value)
        normalized = " ".join(clean.split()).casefold()
        if not normalized or normalized in seen or len(normalized) > 1200:
            continue
        seen.add(normalized)
        tokens.extend(word for word in TOKEN.findall(normalized) if len(word) > 1)
    counts = {locale: sum(word in words for word in tokens)
              for locale, words in signals.items()}
    # Repeated template text (e.g. many cells containing only "the and")
    # must not become strong language evidence merely through repetition.
    # Require several DIFFERENT signal words, independently of locale.
    unique_tokens = set(tokens)
    distinct_counts = {locale: len(unique_tokens & words)
                       for locale, words in signals.items()}
    ranking = sorted(counts.items(), key=lambda entry: entry[1], reverse=True)
    winner, hits = ranking[0]
    runner_up = ranking[1][1] if len(ranking) > 1 else 0
    enough = (len(tokens) >= min_tokens and hits >= min_hits
              and distinct_counts[winner] >= 4
              and hits / len(tokens) >= 0.12 and hits >= 1.7 * runner_up)
    return {
        "detectedLanguage": winner if enough else None,
        "status": "strong_evidence" if enough else
                  ("insufficient_prose" if len(tokens) < min_tokens else "ambiguous"),
        "tokenCount": len(tokens),
        "signalCounts": counts,
        "distinctSignalCounts": distinct_counts,
    }
