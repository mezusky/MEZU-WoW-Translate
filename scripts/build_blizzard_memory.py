#!/usr/bin/env python3
"""Build an EN->frFR translation memory from paired official Blizzard WoW articles.

We discover recent /news/<id> pages from the English news index, fetch the same
article ID in en-us and fr-fr, align article blocks conservatively, and publish
only high-confidence exact sentence/block pairs. This layer is for prose and
patch-note wording; official spell/item names still come from Blizzard Game Data.
"""
import html
import json
import re
import time
import urllib.request
from difflib import SequenceMatcher
from functools import lru_cache
try:
    from .html_block_extractor import extract_readable_blocks
except ImportError:  # Direct execution: python scripts/build_blizzard_memory.py
    from html_block_extractor import extract_readable_blocks
from pathlib import Path
try:
    from .locale_number_words import normalize_count_words
except ImportError:  # Direct execution from scripts/
    from locale_number_words import normalize_count_words

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "blizzard_translation_memory.json"
UA = "MEZU-WoW-Translate-DataBot/1.0 (+https://github.com/mezusky/MEZU-WoW-Translate)"
BASE = "https://worldofwarcraft.blizzard.com"
INDEX_PAGES = 6
MAX_ARTICLES = 60

# A few known high-value official articles are always included.
SEED_IDS = {
    "24245217",  # Midnight pre-expansion update
    "24066687",  # Hotfixes example with many class changes
}

NOISE = {
    "share","tweet","learn more","read more","world of warcraft","blizzard entertainment",
    "news","patch notes","hotfixes","back to top","previous article","next article",
}
ID_RE = re.compile(r"/(?:en-us|fr-fr)/news/(\d+)")
WS_RE = re.compile(r"\s+")
SENT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-ZÀ-ÖØ-Þ0-9])")


def accept_language_for_url(url):
    """Request Blizzard's locale explicitly, without assuming every page is English.

    A localized URL determines the preferred response language. This avoids
    accidentally requesting English when collecting official translated prose.
    """
    from urllib.parse import urlsplit

    segment = urlsplit(url).path.strip("/").split("/", 1)[0]
    if not re.fullmatch(r"[a-z]{2,3}-[a-z]{2}", segment, re.IGNORECASE):
        raise ValueError("Blizzard article URL must contain a language-region locale")
    language, region = segment.split("-", 1)
    return f"{language.lower()}-{region.upper()},{language.lower()};q=0.8"


def fetch(url):
    req = urllib.request.Request(
        url, headers={"User-Agent": UA, "Accept-Language": accept_language_for_url(url)}
    )
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode("utf-8", "replace")


def clean_blocks(raw_html):
    """Extract only visible article prose with the shared, tested HTML parser.

    Official phrase memory must not learn JavaScript, template contents, or
    hidden navigation text. Use the same block extraction semantics as the
    Wowhead source auditor; fall back to unscoped parsing only when needed.
    """
    tags = ("h1", "h2", "h3", "h4", "p", "li")
    blocks = extract_readable_blocks(raw_html, tags=tags)

    out = []
    seen = set()
    for tag, text in blocks:
        text = html.unescape(text).replace("\u00a0", " ")
        text = WS_RE.sub(" ", text).strip()
        low = text.casefold().strip(" :.-")
        if len(text) < 8 or len(text) > 1200 or low in NOISE:
            continue
        if text in seen:
            continue
        seen.add(text)
        out.append((tag, text))
    return out


@lru_cache(maxsize=4096)
def _alignment_number_tokens(text, locale):
    """Cache canonical numeric evidence across alignment DP cells.

    Reuse the locale-aware safety parser: EN decimal dots and FR decimal
    commas, or yards and metres, must not appear to be different facts.
    Strip a postfix + only for alignment scoring; comparison_facts still
    verifies inclusive thresholds before a phrase enters the memory.
    """
    normalized = normalize_count_words(text, locale)
    return tuple((value.removesuffix("+"), unit)
                 for value, unit in numeric_facts(normalized, locale))


def structural_score(a, b, source_language="en-US", target_language="fr-FR"):
    taga, ea = a
    tagb, fr = b
    score = 0.0
    if taga == tagb:
        score += 2.2
    # Compare digit and spelled-out counts consistently with the safety gate.
    # Locale data supplies vocabulary; the collector's current defaults are EN/FR.
    na = _alignment_number_tokens(ea, source_language)
    nb = _alignment_number_tokens(fr, target_language)
    if na and na == nb:
        score += 4.0
    elif not na and not nb:
        score += 0.7
    elif set(na) & set(nb):
        score += 1.5

    la, lb = max(1,len(ea)), max(1,len(fr))
    ratio = min(la,lb)/max(la,lb)
    if ratio >= 0.75: score += 2.0
    elif ratio >= 0.55: score += 1.0
    elif ratio < 0.32: score -= 2.5

    if ea.count("%") == fr.count("%"): score += 0.5
    if ea.count(":") == fr.count(":"): score += 0.3
    if (taga.startswith("h") and tagb.startswith("h")): score += 0.8
    return score


def align_blocks(en_blocks, fr_blocks, source_language="en-US", target_language="fr-FR"):
    # Dynamic-programming alignment with gaps; conservative acceptance later.
    n, m = len(en_blocks), len(fr_blocks)
    gap = -1.8
    dp = [[0.0]*(m+1) for _ in range(n+1)]
    bt = [[None]*(m+1) for _ in range(n+1)]
    for i in range(1,n+1):
        dp[i][0] = dp[i-1][0] + gap; bt[i][0] = "U"
    for j in range(1,m+1):
        dp[0][j] = dp[0][j-1] + gap; bt[0][j] = "L"
    for i in range(1,n+1):
        for j in range(1,m+1):
            diag = dp[i-1][j-1] + structural_score(en_blocks[i-1], fr_blocks[j-1], source_language, target_language)
            up = dp[i-1][j] + gap
            left = dp[i][j-1] + gap
            best = max(diag, up, left)
            dp[i][j] = best
            bt[i][j] = "D" if best == diag else ("U" if best == up else "L")
    pairs = []
    i,j=n,m
    while i or j:
        move = bt[i][j]
        if move == "D":
            pairs.append((en_blocks[i-1], fr_blocks[j-1], structural_score(en_blocks[i-1], fr_blocks[j-1], source_language, target_language)))
            i-=1; j-=1
        elif move == "U":
            i-=1
        else:
            j-=1
    pairs.reverse()
    return pairs


def sentences(text):
    parts = [x.strip() for x in SENT_RE.split(text) if x.strip()]
    return parts if parts else [text]


# Shared number grammar for locale-aware facts and threshold comparisons.
NUMBER_VALUE_PATTERN = (
    r"[+\-\u2212]?(?:\d{1,3}(?:[ \u00a0\u202f]\d{3})+(?:[.,]\d+)?|"
    r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:[.,]\d+)?)"
)


def _normalize_numeric_value(value, locale):
    """Normalize numeric separators without conflating 1,000 EN and 1,000 FR."""
    language = (locale or "").replace("_", "-").split("-", 1)[0].casefold()
    value = re.sub(r"[ \u00a0\u202f]", "", value.replace("−", "-").lstrip("+"))
    if language == "en" and re.fullmatch(r"-?\d{1,3}(?:,\d{3})+(?:\.\d+)?", value):
        return value.replace(",", "")
    return value.replace(",", ".")


def _suffix_comparator_gap(locale):
    """Optional data-only threshold phrase between a number and its unit."""
    suffixes = [phrase for forms in _comparison_terms(locale).get("suffix", {}).values()
                for phrase in forms if isinstance(phrase, str) and phrase.strip()]
    if not suffixes:
        return ""
    alternatives = "|".join(
        re.escape(phrase.replace("’", "'")).replace(r"\ ", r"\s+")
        for phrase in sorted(suffixes, key=len, reverse=True)
    )
    return r"(?:\s+(?:" + alternatives + r"))?"


def numeric_facts(text, locale=None):
    """Compare numeric facts using only the declared locale's unit vocabulary.

    Symbols shared across languages stay in the engine; written unit names
    belong to data/<locale>_numeric_units.json. Do not interpret French words
    on an English page (or English words on an unknown-language page).
    """
    shared_units = {"ms": "ms", "s": "s", "min": "min", "h": "h"}
    aliases = {**shared_units, **_numeric_unit_aliases(locale)}
    unit_pattern = "|".join(
        re.escape(unit) for unit in sorted(aliases, key=len, reverse=True)
    )
    pattern = (
        r"(?<!\w)(" + NUMBER_VALUE_PATTERN + r")(\+(?!\d))?"
        + _suffix_comparator_gap(locale)
        # A dash is accepted only before a recognized unit; 2-3 is a range.
        + r"(?:(?:\s*[-‑–—]\s*|\s*)(%|" + unit_pattern + r")"
        r"(?![^\W\d_]))?"
    )
    # Compact ranges (2-3 targets) use a separator, not a negative sign.
    normalized = re.sub(r"(?<=\d)[-–—](?=\d)", "–", text)
    facts = []
    for match in re.finditer(pattern, normalized, flags=re.IGNORECASE):
        value, lower_bound, unit = match.groups()
        unit = unit.casefold().rstrip(".")
        canonical_unit = aliases.get(unit, unit)
        if canonical_unit == "wow_ability_charge":
            # A resource such as "3 charges de puissance sacrée" is NOT
            # three spell charges. Its complete localized name is checked
            # independently against the canonical resource ID below.
            tail = normalized[match.end():]
            if any(name.startswith(unit + " ") and
                   re.match(re.escape(name[len(unit):]) + r"(?![\w-])",
                            tail, flags=re.IGNORECASE)
                   for _, name in _resource_names(locale)):
                canonical_unit = ""
        facts.append((_normalize_numeric_value(value, locale) + lower_bound,
                      canonical_unit))
    return facts  # Keep source order: swapping two percentage values is unsafe.


@lru_cache(maxsize=16)
def _comparison_terms(locale):
    """Read data-only, locale-scoped inequality phrases; never execute remote rules."""
    normalized = (locale or "").strip().replace("_", "-").casefold()
    if not re.fullmatch(r"[a-z]{2,3}-[a-z]{2}", normalized):
        return {}
    language, region = normalized.split("-", 1)
    path = ROOT / "data" / f"{language}_{region.upper()}_comparison_terms.json"
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("locale", "").replace("_", "-").casefold() != normalized:
        return {}
    return payload


@lru_cache(maxsize=16)
def _numeric_unit_aliases(locale):
    """Load data-only unit spellings by locale; never infer another locale."""
    normalized = (locale or "").strip().replace("_", "-").casefold()
    if not re.fullmatch(r"[a-z]{2,3}-[a-z]{2}", normalized):
        return {}
    language, region = normalized.split("-", 1)
    path = ROOT / "data" / f"{language}_{region.upper()}_numeric_units.json"
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("locale", "").replace("_", "-").casefold() != normalized:
        return {}
    aliases = {}
    for canonical, forms in payload.get("aliases", {}).items():
        if not re.fullmatch(r"[a-z][a-z0-9_]*", canonical) or not isinstance(forms, list):
            continue
        for form in forms:
            if isinstance(form, str) and re.fullmatch(r"[^\W\d_][\w.-]{0,30}", form):
                aliases[form.casefold()] = canonical
    return aliases


def range_facts(text, locale=None):
    """Preserve bounded numeric intervals across locale-specific word order.

    Dash ranges are language-neutral; spelled-out connectors live in locale
    data. The ordered endpoints are semantic: 1-2 is not 1 and 2, or 2-1.
    Unknown locales only recognize dash ranges, never borrowed vocabulary.
    """
    connectors = _comparison_terms(locale).get("rangeConnectors", [])
    words = [re.escape(word.strip()) for word in connectors
             if isinstance(word, str) and word.strip()]
    separator = r"\s*[-–—]\s*"
    if words:
        separator += r"|\s+(?:" + "|".join(words) + r")\s+"
    pattern = (r"(?<![\w.,])(?P<lower>" + NUMBER_VALUE_PATTERN + r")"
               r"(?:" + separator + r")"
               r"(?P<upper>" + NUMBER_VALUE_PATTERN + r")(?![\w.,])")
    matches = list(re.finditer(pattern, text, flags=re.IGNORECASE))

    # Locale-scoped paired delimiters: "between 2 and 3" / "entre 2 et 3".
    # Do not mistake "2 and 3" (two separate values) for a numeric interval.
    # Only data supplies the words; the parser remains locale-neutral.
    bounded = _comparison_terms(locale).get("boundedRange", {})
    prefixes = bounded.get("prefix", [])
    joins = bounded.get("join", [])
    if isinstance(prefixes, list) and isinstance(joins, list):
        prefix_words = [re.escape(x.strip()).replace(r"\ ", r"\s+")
                        for x in prefixes if isinstance(x, str) and x.strip()]
        join_words = [re.escape(x.strip()).replace(r"\ ", r"\s+")
                      for x in joins if isinstance(x, str) and x.strip()]
        if prefix_words and join_words:
            bounded_pattern = (
                r"(?<!\w)(?:" + "|".join(prefix_words) + r")\s+"
                r"(?P<lower>" + NUMBER_VALUE_PATTERN + r")\s+"
                r"(?:" + "|".join(join_words) + r")\s+"
                r"(?P<upper>" + NUMBER_VALUE_PATTERN + r")(?![\w.,])"
            )
            matches.extend(re.finditer(bounded_pattern, text, flags=re.IGNORECASE))
    return [(_normalize_numeric_value(m.group("lower"), locale),
             _normalize_numeric_value(m.group("upper"), locale))
            for m in sorted(matches, key=lambda match: match.start())]


def comparison_facts(text, locale=None):
    """Preserve strict/inclusive numeric thresholds across supported locales.

    Textual comparator vocabulary is locale data; the engine only recognizes
    exact phrases adjacent to a number. Longest-match wins so 'no more than'
    cannot accidentally become 'more than'. Unknown locales retain symbol
    comparison only, rather than guessing another language's phrases.
    """
    normalized = text.replace("’", "'")
    candidates = []
    symbol_pattern = (
        r"(?<![-=<>])(?P<op><=|>=|≤|≥|<|>)\s*"
        r"(?P<value>" + NUMBER_VALUE_PATTERN + r")"
    )
    symbols = {"≤": "<=", "≥": ">="}
    for match in re.finditer(symbol_pattern, normalized):
        candidates.append((match.start(), match.end(),
                           symbols.get(match.group("op"), match.group("op")),
                           _normalize_numeric_value(match.group("value"), locale)))

    # Compact inclusive thresholds (5+ stacks / 4+ Souls) are a
    # language-neutral >= operator, not an exact count. Do not interpret
    # addition (5+10) or signed positive modifiers (+5%) as thresholds.
    plus_pattern = r"(?<![\w.+-])(?P<value>" + NUMBER_VALUE_PATTERN + r")\+(?![\w+])"
    for match in re.finditer(plus_pattern, normalized):
        candidates.append((match.start(), match.end(), ">=",
                           _normalize_numeric_value(match.group("value"), locale)))

    terms = _comparison_terms(locale)
    for position in ("prefix", "suffix"):
        for operator, phrases in terms.get(position, {}).items():
            if operator not in {"<", "<=", ">", ">=", "lt", "lte", "gt", "gte"}:
                continue
            canonical = {"lt": "<", "lte": "<=", "gt": ">", "gte": ">="}.get(operator, operator)
            for phrase in phrases:
                if not isinstance(phrase, str) or not phrase.strip():
                    continue
                escaped = re.escape(phrase.replace("’", "'")).replace(r"\ ", r"\s+")
                if position == "prefix":
                    expression = (r"(?<!\w)" + escaped + r"\s*"
                                  r"(?P<value>" + NUMBER_VALUE_PATTERN + r")")
                else:
                    # "6 or more Combo Points" and "6 points de combo ou plus"
                    # express the same threshold despite different word order.
                    # Permit only a short run of non-numeric words before the
                    # suffix, bounded by locale data to avoid crossing clauses.
                    max_words = max(0, min(4, int(terms.get("suffixMaxUnitWords", 0))))
                    unit_words = (r"(?:[ \t]+[^\W\d_][\w'-]*){0,"
                                  + str(max_words) + r"}")
                    expression = (r"(?<!\w)(?P<value>" + NUMBER_VALUE_PATTERN
                                  + r")" + unit_words + r"\s+" + escaped + r"(?!\w)")
                for match in re.finditer(expression, normalized, flags=re.IGNORECASE):
                    candidates.append((match.start(), match.end(), canonical,
                                       _normalize_numeric_value(match.group("value"), locale)))

    # Prefer longer overlapping phrases, then preserve their original order.
    chosen = []
    for candidate in sorted(candidates, key=lambda x: (-(x[1] - x[0]), x[0])):
        if not any(candidate[0] < other[1] and other[0] < candidate[1]
                   for other in chosen):
            chosen.append(candidate)
    return [(operator, value) for _, _, operator, value
            in sorted(chosen, key=lambda x: x[0])]


@lru_cache(maxsize=16)
def _resource_names(locale):
    """Load only the declared locale's canonical WoW resource names (data-only)."""
    normalized = locale.strip().replace("_", "-").casefold()
    if not re.fullmatch(r"[a-z]{2,3}-[a-z]{2}", normalized):
        return ()
    language, region = normalized.split("-", 1)
    path = ROOT / "data" / f"{language}_{region.upper()}_resource_terms.json"
    if not path.is_file():
        return ()
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("targetLanguage", "").replace("_", "-").casefold() != normalized:
        return ()
    names = set()
    for resource_id, forms in payload.get("resourceNames", {}).items():
        if not isinstance(forms, dict):
            continue
        for form in forms.values():
            if isinstance(form, str) and form.strip():
                names.add((str(resource_id), " ".join(form.replace("’", "'").casefold().split())))
    return tuple(sorted(names))


def _looks_like_proper_name_suffix(tail):
    """Avoid counting resource words that begin longer title-cased entity names.

    A number may count casts/players rather than the resource: "2 Chi Burst
    casts", "3 Fury Warriors", "3 Fury of the Aldrachi procs". Permit up to
    two short lowercase linking words between title-cased name components.
    This conservative check may discard a valid memory pair, but never
    invents a resource identity from a proper name. Unicode casing keeps
    the heuristic independent of the locale's alphabet.
    """
    continuation = re.match(
        r"\s+([^\W\d_][\w'-]*)(?:\s+([^\W\d_][\w'-]*))?(?:\s+([^\W\d_][\w'-]*))?",
        tail,
    )
    if not continuation:
        return False
    preceding = []
    for word in continuation.groups():
        if word is None:
            break
        if word[0].isupper() and all(len(link) <= 3 and link.islower() for link in preceding):
            return True
        preceding.append(word)
    return False


def resource_count_facts(text, locale):
    """Preserve counted WoW resources by canonical ID, not translated surface name.

    Only explicit '3 Soul Shards' / '3 éclats d’âme' patterns are protected.
    Unknown locales and uncounted references remain outside this conservative
    check; browser prose translation is not simulated here.
    """
    # Keep original casing for title-cased spell/spec names. IGNORECASE
    # still matches locale-specific resource forms without casefold offsets.
    normalized = " ".join(text.replace("’", "'").split())
    found = set()
    # Some languages place a comparator between a quantity and its resource:
    # "6 or more Combo Points". Other locales place it after the resource.
    gap = _suffix_comparator_gap(locale)
    for resource_id, name in _resource_names(locale):
        pattern = (r"(?<!\w)(\d+(?:[.,]\d+)?)(?:\+(?!\d))?" + gap + r"\s+"
                   + re.escape(name) + r"(?![\w-])")
        for match in re.finditer(pattern, normalized, flags=re.IGNORECASE):
            if _looks_like_proper_name_suffix(normalized[match.end():]):
                continue
            found.add((match.start(), match.group(1).replace(",", "."), resource_id))
    return [(value, resource_id) for _, value, resource_id in sorted(found)]


def numeric_semantics_match(source, target, source_language="en-US", target_language="fr-FR"):
    """One locale-aware safety gate for new and retained official phrase pairs."""
    # Locale-specific spelled counts share the same numeric checks as digits.
    # This is validation-only; no remote executable translation logic.
    source = normalize_count_words(source, source_language)
    target = normalize_count_words(target, target_language)
    # A postfix + carries comparator meaning, checked independently below.
    # Compare numeric magnitudes/units without rejecting valid 5+ -> au moins 5
    # locale translations; the comparison gate still rejects a missing >=.
    source_numbers = [(value.removesuffix("+"), unit)
                      for value, unit in numeric_facts(source, source_language)]
    target_numbers = [(value.removesuffix("+"), unit)
                      for value, unit in numeric_facts(target, target_language)]
    return (source_numbers == target_numbers
            and comparison_facts(source, source_language)
                == comparison_facts(target, target_language)
            and range_facts(source, source_language)
                == range_facts(target, target_language)
            and resource_count_facts(source, source_language)
                == resource_count_facts(target, target_language))


def good_pair(en, fr, score):
    if score < 4.0:
        return False
    if en.casefold() == fr.casefold():
        return False
    if len(en) < 12 or len(fr) < 12:
        return False
    if len(en) > 900 or len(fr) > 900:
        return False
    ratio = min(len(en),len(fr))/max(len(en),len(fr))
    if ratio < 0.34:
        return False
    # Exact translation memory must not silently change numeric facts.
    if not numeric_semantics_match(en, fr):
        return False
    # Avoid obvious nav/metadata.
    bad = ("cookie","privacy","facebook","twitter","instagram","youtube","copyright")
    low = (en+" "+fr).casefold()
    return not any(x in low for x in bad)


def discover_ids():
    ids = set(SEED_IDS)
    for page in range(1, INDEX_PAGES+1):
        urls = [
            f"{BASE}/en-us/news" if page == 1 else f"{BASE}/en-us/news?page={page}",
        ]
        for url in urls:
            try:
                raw = fetch(url)
                ids.update(ID_RE.findall(raw))
            except Exception as exc:
                print("WARN news index", url, exc)
        time.sleep(0.1)
    # Deterministic selection: always keep high-value seeds, then newest-looking
    # numeric article IDs. Set iteration order previously made the 60-article corpus
    # change randomly on every run, which caused the Data Pack to churn.
    seeds = sorted(SEED_IDS, key=lambda x: int(x), reverse=True)
    discovered = sorted((x for x in ids if x not in SEED_IDS), key=lambda x: int(x), reverse=True)
    return seeds + discovered[:max(0, MAX_ARTICLES - len(seeds))]


def main():
    memory = {}
    sources = {}
    ambiguous = set()
    article_stats = {}
    ids = discover_ids()
    print("Discovered", len(ids), "candidate Blizzard article IDs")

    for idx, article_id in enumerate(ids, 1):
        en_url = f"{BASE}/en-us/news/{article_id}"
        fr_url = f"{BASE}/fr-fr/news/{article_id}"
        try:
            en_html = fetch(en_url)
            fr_html = fetch(fr_url)
            en_blocks = clean_blocks(en_html)
            fr_blocks = clean_blocks(fr_html)
            if len(en_blocks) < 3 or len(fr_blocks) < 3:
                continue

            accepted = 0
            for (te,en),(tf,fr),score in align_blocks(en_blocks, fr_blocks):
                if not good_pair(en,fr,score):
                    continue

                # Whole-block memory.
                if en not in ambiguous:
                    prev = memory.get(en)
                    if prev is None:
                        memory[en] = fr
                        sources[en] = article_id
                        accepted += 1
                    elif prev != fr:
                        memory.pop(en, None)
                        sources.pop(en, None)
                        ambiguous.add(en)

                # Sentence memory when structure is one-to-one.
                es, fs = sentences(en), sentences(fr)
                if len(es) == len(fs) and 1 <= len(es) <= 8:
                    for e,f in zip(es,fs):
                        if good_pair(e,f,score):
                            if e in ambiguous:
                                continue
                            prev = memory.get(e)
                            if prev is None:
                                memory[e] = f
                                sources[e] = article_id
                                accepted += 1
                            elif prev != f:
                                memory.pop(e, None)
                                sources.pop(e, None)
                                ambiguous.add(e)

            if accepted:
                article_stats[article_id] = {
                    "accepted_pairs": accepted,
                    "en_blocks": len(en_blocks),
                    "fr_blocks": len(fr_blocks),
                    "en_url": en_url,
                    "fr_url": fr_url,
                }
            print(f"[{idx}/{len(ids)}] {article_id}: +{accepted}")
        except Exception as exc:
            print("WARN article", article_id, exc)
        time.sleep(0.08)

    payload = {
        "schema": 1,
        # This collector currently pairs the two explicit Blizzard locales.
        # The merger uses these fields to prevent cross-locale contamination.
        "sourceLanguage": "en-US",
        "targetLanguage": "fr-FR",
        "ambiguous": sorted(ambiguous),
        "source": "Official Blizzard World of Warcraft news",
        "pair_count": len(memory),
        "article_count": len(article_stats),
        "exact": dict(sorted(memory.items(), key=lambda kv: kv[0].casefold())),
        "sources": sources,
        "articles": article_stats,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print("Blizzard translation memory:", len(memory), "pairs from", len(article_stats), "paired articles")

if __name__ == "__main__":
    main()
