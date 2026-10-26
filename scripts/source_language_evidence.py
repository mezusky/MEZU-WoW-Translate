"""Conservative, locale-extensible language evidence for source-only audits.

Profiles are data-only; this is NOT the Chrome Translator API or a browser
language detector. Unknown/mixed evidence must never be counted as a failure.
"""
import re

TOKEN = re.compile(r"[^\\W\\d_]+", re.UNICODE)
PROSE_TAGS = frozenset(("p", "li", "td", "th"))


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
        normalized = " ".join(value.split()).casefold()
        if normalized in seen or len(normalized) > 1200:
            continue
        seen.add(normalized)
        tokens.extend(word for word in TOKEN.findall(normalized) if len(word) > 1)
    counts = {locale: sum(word in words for word in tokens)
              for locale, words in signals.items()}
    ranking = sorted(counts.items(), key=lambda entry: entry[1], reverse=True)
    winner, hits = ranking[0]
    runner_up = ranking[1][1] if len(ranking) > 1 else 0
    enough = (len(tokens) >= min_tokens and hits >= min_hits
              and hits / len(tokens) >= 0.12 and hits >= 1.7 * runner_up)
    return {
        "detectedLanguage": winner if enough else None,
        "status": "strong_evidence" if enough else
                  ("insufficient_prose" if len(tokens) < min_tokens else "ambiguous"),
        "tokenCount": len(tokens),
        "signalCounts": counts,
    }
