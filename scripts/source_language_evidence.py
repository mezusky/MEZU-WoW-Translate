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
# Native WoW talent build exports are bare base64-like tokens (no "1|" prefix).\n# Match only long mixed-case alphanumeric payloads, never ordinary prose.\nTALENT_IMPORT_TOKEN = re.compile(r"(?<![A-Za-z0-9+/=])[A-Za-z0-9+/=]{80,}(?![A-Za-z0-9+/=])")
# WoW macro commands are executable game instructions, not translation prose.
# Only strip whole directive lines, preserving inline /cast mentions in prose.
# /tar, /run, /script and /click occur in independent Wowhead macro guides.
# This is source-audit filtering, not a browser DOM protection guarantee.
WOW_MACRO_LINE = re.compile(
    r"^[ \t]*(?:#(?:showtooltip|show)\b|/(?:castsequence|cast|use|cancelaura|"
    r"stopcasting|stopspelltarget|stopmacro|stopattack|startattack|"
    r"targetlasttarget|targetenemyplayer|targetenemy|target|cleartarget|"
    r"clearfocus|focus|petattack|petpassive|petfollow|tm|equipslot|cqs|console|tar|run|script|click)\b)"
    r"[^\r\n]*(?=\r?$)", re.IGNORECASE | re.MULTILINE
)

# WoW Edit Mode exports are long, whitespace-separated layout records rather
# than base64 CDM strings. Header versions vary (e.g. 0 and 2 across
# unrelated class guides); match the structural header rather than a fixed
# version. Only suppress a whole cell with multiple frame records; ordinary
# text mentioning UIParent stays.
EDIT_MODE_HEADER = re.compile(
    r"^\d{1,2}\s+\d{1,3}(?:\s+[01]){3}(?:\s+\d+){2}\s+[A-Za-z][A-Za-z0-9]*\b"
)
EDIT_MODE_FRAME = re.compile(r"\b(?:UIParent|[A-Za-z][A-Za-z0-9]*Frame)\b")

# Northern Sky Raid Tools reminders are structured encounter/timing records,
# not prose. Seen in both Holy and Discipline Priest raid guides. Match
# complete records rather than removing generic words like "time" or "Heroic".
RAID_REMINDER_HEADER = re.compile(
    # Boss names may contain spaces (e.g. Twin Fangs / Coiled Altar).
    # Stop before a following timing record or delimiter, never consume it.
    r"(?<!\w)EncounterID:\d{3,8};Difficulty:[A-Za-z]+;Name:"
    r"[^\r\n;]{1,60}?(?=\s+(?:time|ph):|;|\r?$);?",
    re.MULTILINE,
)
RAID_REMINDER_EVENT = re.compile(
    # Both field orders occur in independent raid reminder exports.
    r"(?<!\w)(?:time:\d+(?:\.\d+)?;ph:\d+(?:\.\d+)?;"
    r"|ph:\d+(?:\.\d+)?;time:\d+(?:\.\d+)?;)"
    r"tag:\d+;spellid:\d+;"
)


# Method Raid Tools notes use a different, line-oriented import syntax.
# Strip complete time+spell records only at line start; preserve nearby prose.
MRT_NOTE_LINE = re.compile(
    r"^[ \t]*\{time:\d{1,2}:\d{2}(?::\d{2})?\}"
    r"[^\r\n]{0,200}\{spell:\d{3,8}\}[^\r\n]*(?=\r?$)",
    re.MULTILINE,
)



def is_opaque_edit_mode_export(text):
    value = text.strip()
    return (len(value) >= 250 and bool(EDIT_MODE_HEADER.match(value))
            and len(EDIT_MODE_FRAME.findall(value)) >= 3
            and value.count(" -1 ") >= 3)


def _strip_talent_import(match):
    token = match.group()
    return (" " if any(char.isdigit() for char in token)
            and any(char.islower() for char in token)
            and any(char.isupper() for char in token) else token)


def clean_non_prose(text):
    """Remove generated widget assignments and opaque import payloads."""
    if is_opaque_edit_mode_export(text):
        return ""
    text = WOW_MACRO_LINE.sub(" ", text)
    text = MRT_NOTE_LINE.sub(" ", text)
    text = RAID_REMINDER_EVENT.sub(" ", RAID_REMINDER_HEADER.sub(" ", text))
    text = OPAQUE_IMPORT.sub(" ", text)
    text = TALENT_IMPORT_TOKEN.sub(_strip_talent_import, text)
    return NON_PROSE_ASSIGNMENT.sub(" ", NON_PROSE_PLACEHOLDER.sub(" ", text))
PROSE_TAGS = frozenset(("p", "li", "td", "th"))


def normalized_language_signals(profiles):
    """Group regional profiles by base language, never as rival languages.

    en, en-US and en_GB are evidence for one language, not competing
    candidates. This also accepts regional-only profiles without requiring a
    duplicate base-language entry. It is source-audit evidence, not browser
    locale selection or a translation fallback.
    """
    if not isinstance(profiles, dict) or not profiles:
        raise ValueError("Language evidence profiles must be a nonempty object")
    signals = {}
    for locale, words in profiles.items():
        if (not isinstance(locale, str) or not locale.strip()
                or not isinstance(words, list)
                or any(not isinstance(word, str) or not word.strip()
                       for word in words)):
            raise ValueError("Invalid language evidence profile")
        base = locale.strip().replace("_", "-").casefold().split("-")[0]
        signals.setdefault(base, set()).update(word.casefold() for word in words)
    return signals


def audit_source_prose(text, source_language, profiles):
    """Clean widget payloads and check prose in the configured source language.

    Regional profiles contribute evidence for their shared base language.
    This is not a translation-quality classifier or browser language detector.
    """
    if not isinstance(text, str):
        return "", False
    locale = source_language.strip().replace("_", "-").casefold().split("-")[0]
    words = normalized_language_signals(profiles).get(locale)
    if not words:
        raise ValueError("Missing source-language audit profile: " + locale)
    clean = clean_non_prose(text)
    clean = " ".join(clean.split()).strip()
    tokens = set(TOKEN.findall(clean.casefold()))
    return clean, bool(tokens & words)




def detect_source_language(blocks, profiles, min_tokens=25, min_hits=7):
    """Infer a language only when prose strongly favors one configured profile.

    Ignore headings (often English even on localized pages), repeated blocks,
    and long calculator/import payloads. Mixed official spell names should not
    outweigh surrounding prose. Returns evidence, not a probability estimate.
    """
    signals = normalized_language_signals(profiles)
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
