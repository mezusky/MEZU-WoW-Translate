import json
import os
import urllib.parse
import urllib.request
import base64
import hashlib
from pathlib import Path
from blizzard_search_pairs import collect_search_pairs
from index_retention import retain_on_partial_index
from merge_entity_locales import project_locale_pairs
from locale_glossary import select_jargon, select_locale_data
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

# Current release pair; locale-aware helpers accept future language directions.
PACK_SOURCE_LANGUAGE = "en"
PACK_TARGET_LANGUAGE = "fr"

region = os.environ.get("BLIZZARD_REGION", "eu")
client_id = os.environ["BLIZZARD_CLIENT_ID"]
client_secret = os.environ["BLIZZARD_CLIENT_SECRET"]

auth = base64.b64encode((client_id + ":" + client_secret).encode()).decode()
req = urllib.request.Request(
    "https://oauth.battle.net/token",
    data=b"grant_type=client_credentials",
    headers={
        "Authorization": "Basic " + auth,
        "Content-Type": "application/x-www-form-urlencoded",
    },
    method="POST",
)
with urllib.request.urlopen(req, timeout=30) as response:
    token = json.load(response)["access_token"]

def get(path, locale):
    sep = "&" if "?" in path else "?"
    url = (
        f"https://{region}.api.blizzard.com{path}"
        f"{sep}namespace=static-{region}&locale={locale}"
    )
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + token})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)

def collect_pairs(en_doc, fr_doc):
    en = {}
    fr = {}

    def walk(value, target):
        if isinstance(value, list):
            for item in value:
                walk(item, target)
        elif isinstance(value, dict):
            if isinstance(value.get("id"), int) and isinstance(value.get("name"), str):
                target[str(value["id"])] = value["name"]
            for key, item in value.items():
                if key not in ("_links", "key", "media"):
                    walk(item, target)

    walk(en_doc, en)
    walk(fr_doc, fr)
    return {
        i: {"en": name, "fr": fr[i]}
        for i, name in en.items()
        if i in fr and name and fr[i]
    }

endpoints = {
    "class": "/data/wow/playable-class/index",
    "race": "/data/wow/playable-race/index",
    "specialization": "/data/wow/playable-specialization/index",
    "profession": "/data/wow/profession/index",
    "mount": "/data/wow/mount/index",
    "pet": "/data/wow/pet/index",
    "talent": "/data/wow/talent/index",
    "pvp_talent": "/data/wow/pvp-talent/index",
    "reputation": "/data/wow/reputation-faction/index",
    "title": "/data/wow/title/index",
    "toy": "/data/wow/toy/index",
    "journal_expansion": "/data/wow/journal-expansion/index",
    "power_type": "/data/wow/power-type/index",
    "pet_ability": "/data/wow/pet-ability/index",
    "heirloom": "/data/wow/heirloom/index",
    "pvp_tier": "/data/wow/pvp-tier/index",
    "achievement_category": "/data/wow/achievement-category/index",
    "item_class": "/data/wow/item-class/index",
    "creature_type": "/data/wow/creature-type/index",
    "creature_family": "/data/wow/creature-family/index",
    "quest_category": "/data/wow/quest/category/index",
    "quest_area": "/data/wow/quest/area/index",
    "quest_type": "/data/wow/quest/type/index",
    "covenant": "/data/wow/covenant/index",
    "soulbind": "/data/wow/covenant/soulbind/index",
    "conduit": "/data/wow/covenant/conduit/index",
}

# Prefer the newest canonical IDs in the same fixed API request budget.
# Historical ascending-page IDs remain available through previous_entities.
# Blizzard search supports orderby=id:desc; never scrape Wowhead in CI.
search_endpoints = {
    "spell": "/data/wow/search/spell?orderby=id:desc&_pageSize=1000&_page=1",
    "item": "/data/wow/search/item?orderby=id:desc&_pageSize=1000&_page=1",
    "creature": "/data/wow/search/creature?orderby=id:desc&_pageSize=1000&_page=1",
    "journal_encounter_search": "/data/wow/search/journal-encounter?orderby=id:desc&_pageSize=1000&_page=1",
}

previous_entities = {}
previous_pack_path = DATA / "datapack.json"
if previous_pack_path.exists():
    try:
        previous_entities = json.loads(previous_pack_path.read_text(encoding="utf-8")).get("entities", {}) or {}
    except Exception as exc:
        print("WARN previous datapack", exc)
        previous_entities = {}

entities = {}
for kind, path in endpoints.items():
    print("Sync", kind)
    try:
        fresh = collect_pairs(get(path, "en_US"), get(path, "fr_FR"))
        entities[kind] = retain_on_partial_index(kind, fresh, previous_entities.get(kind, {}))
    except Exception as exc:
        print("WARN sync", kind, exc)
        entities[kind] = previous_entities.get(kind, {})

for kind, path in search_endpoints.items():
    print("Search", kind)
    try:
        fresh = collect_search_pairs(get(path, "en_US"), get(path, "fr_FR"), "en_US", "fr_FR")
        # Preserve verified IDs across partial pages; new official names win.
        entities[kind] = {**previous_entities.get(kind, {}), **fresh}
    except Exception as exc:
        print("WARN search", kind, exc)
        entities[kind] = previous_entities.get(kind, {})

manual_path = DATA / "manual_overrides.json"
manual = json.loads(manual_path.read_text(encoding="utf-8"))

community_path = DATA / "community_glossary.json"
community = {}
if community_path.exists():
    try:
        community = json.loads(community_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print("WARN community glossary", exc)
        community = {}

player_glossary_path = DATA / "mezu_player_glossary.json"
player_glossary = {}
if player_glossary_path.exists():
    try:
        player_glossary = json.loads(player_glossary_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print("WARN MEZU player glossary", exc)
        player_glossary = {}

blizzard_memory_path = DATA / "blizzard_translation_memory.json"
blizzard_memory = {}
if blizzard_memory_path.exists():
    try:
        blizzard_memory = json.loads(blizzard_memory_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print("WARN Blizzard translation memory", exc)
        blizzard_memory = {}

# Never mix translation directions: official phrase memory and player rules
# must match this pack. Older untagged manual/community sources are EN->FR only.
# The selectors return empty layers for other directions, not French fallbacks.
manual = select_locale_data(manual, PACK_SOURCE_LANGUAGE, PACK_TARGET_LANGUAGE,
                            legacy_pair=("en", "fr"))
community = select_locale_data(community, PACK_SOURCE_LANGUAGE, PACK_TARGET_LANGUAGE,
                               legacy_pair=("en", "fr"))
blizzard_memory = select_locale_data(blizzard_memory, PACK_SOURCE_LANGUAGE,
                                     PACK_TARGET_LANGUAGE)
player_glossary = select_locale_data(player_glossary, PACK_SOURCE_LANGUAGE,
                                    PACK_TARGET_LANGUAGE)

# Project current EN->FR pack from canonical ID records, never by assuming
# identical source names identify the same spell/item across entity types.
# The helper accepts arbitrary source/target language keys for future packs.
# Ambiguous or incomplete IDs fall back to prose translation, not a guessed name.
exact = project_locale_pairs(entities, PACK_SOURCE_LANGUAGE, PACK_TARGET_LANGUAGE)

# Official Blizzard translation-memory phrases are whole-string matches only.
# This lets us reuse real Blizzard EN->FR wording without injecting fragments into prose.
for en, fr in (blizzard_memory.get("exact", {}) or {}).items():
    if isinstance(en, str) and isinstance(fr, str) and en.strip() and fr.strip():
        exact.setdefault(en.strip(), fr.strip())

# Community EN->frFR mappings are also exact-match only.
for en, fr in (community.get("exact", {}) or {}).items():
    if isinstance(en, str) and isinstance(fr, str) and en.strip() and fr.strip():
        exact.setdefault(en.strip(), fr.strip())

# Manual MEZU player-language rules always win over every automatic source.
exact.update(manual.get("exact", {}))

# Keep the official Blizzard prose memory as a distinct layer too.  The browser
# extension uses this for sentence-level exact matching and conservative
# source-aware patterns; entity names are intentionally excluded from it.
phrase_memory = {}
for en, fr in (blizzard_memory.get("exact", {}) or {}).items():
    if not isinstance(en, str) or not isinstance(fr, str):
        continue
    en = " ".join(en.split()).strip()
    fr = " ".join(fr.split()).strip()
    if not en or not fr or en.casefold() == fr.casefold():
        continue
    if len(en) < 12 or len(en) > 320 or len(fr) < 10 or len(fr) > 420:
        continue
    phrase_memory[en] = fr

jargon = dict(manual.get("jargon", {}) or {})
if player_glossary:
    jargon.update(select_jargon(player_glossary, PACK_SOURCE_LANGUAGE, PACK_TARGET_LANGUAGE))

stable = {
    "schema": 1,
    "sourceLanguage": PACK_SOURCE_LANGUAGE,
    "targetLanguage": PACK_TARGET_LANGUAGE,
    "entities": entities,
    "exact": exact,
    "jargon": jargon,
    "protected_names": manual.get("protected_names", []),
    "phrase_memory": phrase_memory,
    "community_meta": {
        "source": community.get("source"),
        "license": community.get("license"),
        "term_count": len(community.get("terms", {}) or {}),
        "exact_count": len(community.get("exact", {}) or {})
    },
    "blizzard_memory_meta": {
        "source": blizzard_memory.get("source"),
        "article_count": blizzard_memory.get("article_count", 0),
        "pair_count": blizzard_memory.get("pair_count", 0)
    },
}
stable_json = json.dumps(stable, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
version = hashlib.sha256(stable_json.encode("utf-8")).hexdigest()[:20]

manifest_path = DATA / "manifest.json"
previous = {}
if manifest_path.exists():
    try:
        previous = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        previous = {}

# Compact coverage telemetry, including categories that returned zero search hits.
# Keep this in the small manifest so audits never need to download the full pack.
entity_counts_by_kind = {kind: len(rows) for kind, rows in sorted(entities.items())}
if previous.get("version") == version:
    if previous.get("entity_counts_by_kind") != entity_counts_by_kind:
        previous["entity_counts_by_kind"] = entity_counts_by_kind
        manifest_path.write_text(
            json.dumps(previous, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print("Updated manifest category coverage without rewriting datapack")
    else:
        print("No WoW data changes. Version:", version)
    raise SystemExit(0)

generated_at = datetime.now(timezone.utc).isoformat()
pack = dict(stable)
pack["version"] = version
pack["generated_at"] = generated_at

(DATA / "datapack.json").write_text(
    json.dumps(pack, ensure_ascii=False, separators=(",", ":")) + "\n",
    encoding="utf-8",
)
manifest_path.write_text(
    json.dumps({
        "schema": 1,
        "sourceLanguage": PACK_SOURCE_LANGUAGE,
        "targetLanguage": PACK_TARGET_LANGUAGE,
        "version": version,
        "generated_at": generated_at,
        "entity_count": sum(len(x) for x in entities.values()),
        "entity_counts_by_kind": entity_counts_by_kind,
        "exact_count": len(exact),
        "community_exact_count": len(community.get("exact", {}) or {}),
        "community_term_count": len(community.get("terms", {}) or {}),
        "blizzard_memory_pair_count": len(blizzard_memory.get("exact", {}) or {}),
        "blizzard_phrase_count": len(phrase_memory),
        "blizzard_memory_article_count": blizzard_memory.get("article_count", 0),
        "datapack_url": "https://raw.githubusercontent.com/mezusky/MEZU-WoW-Translate/main/data/datapack.json"
    }, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
