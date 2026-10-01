#!/usr/bin/env python3
import json, re, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "community_glossary.json"
BASE = "https://raw.githubusercontent.com/Yumash/BabelChat/main/addon/BabelChat/Data/"
FILES = [
    "Clases.lua","Combate.lua","Comercio.lua","Endgame.lua","Estadisticas.lua",
    "Estado.lua","Grupos.lua","Hermandad.lua","Mazz_Raid.lua","Profesiones.lua",
    "Roles.lua","Slang.lua","Social.lua"
]
UA = "MEZU-WoW-Translate-DataBot/1.0"
entry_rx = re.compile(r'\["([^"]+)"\]\s*=\s*\{(.*?)\n\s*\},?', re.S)
field_rx = re.compile(r'\b(enUS|frFR)\s*=\s*"((?:\\.|[^"])*)"')

def fetch(name):
    req = urllib.request.Request(BASE + name, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")

def clean(v):
    return (v.replace(r'\"','"').replace(r"\'", "'")
             .replace(r"\n"," ").replace(r"\t"," ")
             .replace(r"\\","\")).strip()

terms, exact, conflicts = {}, {}, {}
for filename in FILES:
    try:
        text = fetch(filename)
    except Exception as exc:
        print("WARN", filename, exc)
        continue
    for key, body in entry_rx.findall(text):
        fields = {k: clean(v) for k, v in field_rx.findall(body)}
        en, fr = fields.get("enUS"), fields.get("frFR")
        if not en or not fr:
            continue
        terms[key] = {"en": en, "fr": fr, "source_file": filename}
        if en in conflicts:
            conflicts[en] = sorted(set(conflicts[en] + [fr]))
        elif en not in exact:
            exact[en] = fr
        elif exact[en] != fr:
            conflicts[en] = sorted({exact.pop(en), fr})

payload = {
    "schema": 1,
    "source": "Yumash/BabelChat",
    "source_url": "https://github.com/Yumash/BabelChat",
    "license": "MIT",
    "terms": terms,
    "exact": exact,
    "conflicts": conflicts
}
OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)+"\n", encoding="utf-8")
print("community terms", len(terms), "exact", len(exact), "conflicts", len(conflicts))
