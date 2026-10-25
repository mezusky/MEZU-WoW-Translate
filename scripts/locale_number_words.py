"""Normalize unambiguous spelled-out quantities for locale-aware safety checks.

The lexicon is data-only and specific to the declared source/target locale.
This is an offline validation helper, not a browser translation rule.
"""
import json
import re
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"


@lru_cache(maxsize=32)
def _number_words(locale):
    normalized = (locale or "").strip().replace("_", "-").casefold()
    if not re.fullmatch(r"[a-z]{2,3}-[a-z]{2}", normalized):
        return None, {}
    language, region = normalized.split("-", 1)
    path = DATA / f"{language}_{region.upper()}_number_words.json"
    if not path.is_file():
        return None, {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("locale", "").replace("_", "-").casefold() != normalized:
        return None, {}
    forms = {}
    for value, aliases in payload.get("cardinals", {}).items():
        if not re.fullmatch(r"[2-9]|1[0-9]|20", value) or not isinstance(aliases, list):
            continue
        for word in aliases:
            # Exclude ambiguous one/un, multiword grammar and proper-name tokens.
            if isinstance(word, str) and word.islower() and re.fullmatch(r"[^\W\d_]+", word):
                if word in forms and forms[word] != value:
                    return None, {}  # Ambiguous lexicon: fail closed.
                forms[word] = value
    if not forms:
        return None, {}
    pattern = re.compile(r"(?<![\w-])(?:" + "|".join(re.escape(w) for w in sorted(forms, key=len, reverse=True)) + r")(?![\w-])")
    return pattern, forms


def normalize_count_words(text, locale):
    """Convert lower-case count words to digits; leave titles and unknown locales intact."""
    pattern, forms = _number_words(locale)
    return pattern.sub(lambda match: forms[match.group()], text) if pattern else text
