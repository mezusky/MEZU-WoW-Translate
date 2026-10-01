import json
import os
import urllib.parse
import urllib.request
import base64
import hashlib
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

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
    url = (
        f"https://{region}.api.blizzard.com{path}"
        f"?namespace=static-{region}&locale={locale}"
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
}

entities = {}
for kind, path in endpoints.items():
    print("Sync", kind)
    entities[kind] = collect_pairs(get(path, "en_US"), get(path, "fr_FR"))

manual_path = DATA / "manual_overrides.json"
manual = json.loads(manual_path.read_text(encoding="utf-8"))

exact_candidates = {}
for bucket in entities.values():
    for row in bucket.values():
        exact_candidates.setdefault(row["en"], set()).add(row["fr"])

exact = {
    en: next(iter(values))
    for en, values in exact_candidates.items()
    if len(values) == 1
}
exact.update(manual.get("exact", {}))

stable = {
    "schema": 1,
    "entities": entities,
    "exact": exact,
    "jargon": manual.get("jargon", {}),
    "protected_names": manual.get("protected_names", []),
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

if previous.get("version") == version:
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
        "version": version,
        "generated_at": generated_at,
        "entity_count": sum(len(x) for x in entities.values()),
        "exact_count": len(exact),
        "datapack_url": "https://raw.githubusercontent.com/mezusky/MEZU-WoW-Translate/main/data/datapack.json"
    }, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
