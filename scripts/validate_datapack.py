#!/usr/bin/env python3
import json, sys
from pathlib import Path

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
    "priority damage": "dégâts prio",
    "priority burst damage": "burst prio",
    "single target": "monocible",
    "Debuff-based defensives (Fiery Brand and Frailty) still require targets to be cast.": "Les défensifs basés sur des debuffs (Marque enflammée et Fragilité) nécessitent toujours une cible.",
    "Vengeance Demon Hunter gearing is much simpler than one might expect.": "L’équipement du Chasseur de démons Vengeance est beaucoup plus simple qu’on pourrait le penser.",
}
for en, expected in required.items():
    actual = exact.get(en)
    if actual != expected:
        errors.append(f"required override mismatch: {en!r}: {actual!r} != {expected!r}")

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
