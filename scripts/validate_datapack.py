#!/usr/bin/env python3
import json, sys
from pathlib import Path
from locale_glossary import normalize_locale, select_jargon, same_base_language

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
pack_path = DATA / "datapack.json"
manifest_path = DATA / "manifest.json"

if not pack_path.exists() or not manifest_path.exists():
    raise SystemExit("Missing datapack.json or manifest.json")

pack = json.loads(pack_path.read_text(encoding="utf-8"))
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

errors = []
warnings = []

# Locale metadata is part of the Data Pack contract. Do not silently publish
# French player jargon in a future German/Spanish or reverse-direction pack.
source_language = pack.get("sourceLanguage")
target_language = pack.get("targetLanguage")
try:
    source_language = normalize_locale(source_language)
    target_language = normalize_locale(target_language)
    if same_base_language(source_language, target_language):
        errors.append("pack source and target base languages must differ (same-language skip)")
except ValueError as exc:
    errors.append(f"invalid pack locale metadata: {exc}")

if manifest.get("sourceLanguage") != pack.get("sourceLanguage") or (
    manifest.get("targetLanguage") != pack.get("targetLanguage")
):
    errors.append("manifest locale pair does not match datapack")

glossary_path = DATA / "mezu_player_glossary.json"
if glossary_path.exists() and isinstance(source_language, str) and isinstance(target_language, str):
    try:
        glossary = json.loads(glossary_path.read_text(encoding="utf-8"))
        selected = select_jargon(glossary, source_language, target_language)
        for term, translation in selected.items():
            if (pack.get("jargon", {}) or {}).get(term) != translation:
                errors.append(f"locale-specific player term missing from pack: {term!r}")
    except (ValueError, TypeError) as exc:
        errors.append(f"invalid locale-scoped player glossary: {exc}")

exact = pack.get("exact", {}) or {}
entities = pack.get("entities", {}) or {}
phrase_memory = pack.get("phrase_memory", {}) or {}

bad_tokens = ("ZXQMEZU", "MEZUXQ", "QXZ", "QZ")
for en, fr in exact.items():
    s = f"{en} {fr}"
    if any(tok in s for tok in bad_tokens):
        errors.append(f"placeholder leak: {en!r} -> {fr!r}")

required = {
    "Rogue": "Voleur",
    "Rogues": "Voleurs",
    "Demon Hunter": "Chasseur de démons",
    "Demon Hunters": "Chasseurs de démons",
    "priority burst damage": "burst prio",
    "single target": "monocible",
    "Debuff-based defensives (Fiery Brand and Frailty) still require targets to be cast.": "Les défensifs basés sur des debuffs (Marque enflammée et Fragilité) nécessitent toujours une cible.",
    "Vengeance Demon Hunter gearing is much simpler than one might expect.": "L’équipement du Chasseur de démons Vengeance est beaucoup plus simple qu’on pourrait le penser.",
}
# These legacy exact overrides are specific to the published EN->FR pack.
# Locale-scoped player jargon is checked separately against pack["jargon"]
# above, so moving a term from manual exact to the player glossary does not
# break validation or require duplicating it in two data layers.
if (source_language, target_language) == ("en", "fr"):
    for en, expected in required.items():
        actual = exact.get(en)
        if actual != expected:
            errors.append(f"required exact mismatch: {en!r}: {actual!r} != {expected!r}")

entity_count = sum(len(v) for v in entities.values() if isinstance(v, dict))
if entity_count < 10000:
    errors.append(f"entity count unexpectedly low: {entity_count}")

exact_count = len(exact)
if exact_count < 8000:
    errors.append(f"exact dictionary unexpectedly low: {exact_count}")

phrase_count = len(phrase_memory)
if phrase_count < 3000:
    errors.append(f"official Blizzard phrase memory unexpectedly low: {phrase_count}")
for en, fr in phrase_memory.items():
    if not isinstance(en, str) or not isinstance(fr, str) or not en.strip() or not fr.strip():
        errors.append("invalid phrase-memory row")
        break
    if any(tok in f"{en} {fr}" for tok in bad_tokens):
        errors.append(f"placeholder leak in phrase memory: {en!r} -> {fr!r}")
        break

# Catch obvious literal mistranslations observed during development.
for en, fr in exact.items():
    low = fr.casefold()
    if en.casefold() == "rogue" and "voyou" in low:
        errors.append("Rogue regressed to 'voyou'")
    if en.casefold() == "tips out" and "pourboire" in low:
        errors.append("Tips Out was translated literally")

# Keep the official prose memory conservative: very long full blocks should not be
# promoted as exact reusable phrases.
memory = pack.get("blizzard_memory_meta", {}) or {}
if memory.get("pair_count", 0) > 0:
    bm_path = DATA / "blizzard_translation_memory.json"
    if bm_path.exists():
        bm = json.loads(bm_path.read_text(encoding="utf-8"))
        too_long = [k for k in (bm.get("exact", {}) or {}) if len(k) > 320]
        if too_long:
            warnings.append(f"{len(too_long)} Blizzard memory entries exceed 320 chars")

# The manifest is the lightweight, remotely readable source of coverage
# metrics. Detect stale or misleading per-category counts before publication.
counts_by_kind = {kind: len(rows) for kind, rows in sorted(entities.items()) if isinstance(rows, dict)}
published_counts = manifest.get("entity_counts_by_kind")
if published_counts is not None and published_counts != counts_by_kind:
    errors.append("manifest entity_counts_by_kind does not match datapack")
for kind in ("spell", "item", "creature", "journal_encounter_search"):
    if counts_by_kind.get(kind, 0) == 0:
        warnings.append(f"Blizzard search category has no entities: {kind}")
print("Entity category coverage:", json.dumps(counts_by_kind, sort_keys=True))

if manifest.get("entity_count") != entity_count:
    errors.append("manifest entity_count does not match datapack")
if manifest.get("exact_count") != exact_count:
    errors.append("manifest exact_count does not match datapack")

for w in warnings:
    print("WARN:", w)
if errors:
    for e in errors:
        print("ERROR:", e)
    sys.exit(1)

print(f"OK: {entity_count} entities, {exact_count} exact EN->frFR mappings, {phrase_count} official phrases")
