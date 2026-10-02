#!/usr/bin/env python3
"""Fetch selected Wowhead guides and report translation coverage/regression signals.

This does not attempt to replace the browser translator. It gives MEZU a stable,
repeatable view of the real guide source so automated review can spot untranslated
or uncovered WoW phrases before relying on screenshots from the user.
"""
import json, re, urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CFG = DATA / "wowhead_regression_pages.json"
OUT = DATA / "wowhead_regression_report.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/154 Safari/537.36 MEZU-WoW-Translate"

WS = re.compile(r"\s+")
EN_SIGNAL = re.compile(r"\b(?:the|and|with|when|your|you|this|that|for|from|into|while|should|will|can|are|is|of|to)\b", re.I)
WOW_SIGNAL = re.compile(r"\b(?:Paladin|Demon Hunter|Tank|Mythic\+|Raid|cooldown|GCD|Holy Power|Haste|Crit|Mastery|Versatility|BiS|Best in Slot|Raidbots|Great Vault|spender|generator|overcap|defensive|mitigation)\b", re.I)

class Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.capture = None
        self.buf = []
        self.blocks = []
        self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in {"script","style","noscript"}:
            self.skip += 1
            return
        if self.skip:
            return
        if tag in {"h1","h2","h3","h4","p","li","td","th"}:
            self.capture = tag
            self.buf = []
    def handle_endtag(self, tag):
        if tag in {"script","style","noscript"} and self.skip:
            self.skip -= 1
            return
        if self.capture == tag:
            t = WS.sub(" ", "".join(self.buf)).strip()
            if t:
                self.blocks.append({"tag": tag, "text": t})
            self.capture = None
            self.buf = []
    def handle_data(self, data):
        if self.capture and not self.skip:
            self.buf.append(data)

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read().decode("utf-8", "replace")

def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

cfg = load_json(CFG)
manual = load_json(DATA / "manual_overrides.json")
exact = manual.get("exact", {}) or {}
jargon = manual.get("jargon", {}) or {}

report = {"schema": 1, "pages": []}

for page in cfg.get("pages", []):
    url = page["url"]
    row = {"id": page["id"], "url": url, "ok": False, "blocks": [], "stats": {}}
    try:
        raw = fetch(url)
        parser = Parser()
        parser.feed(raw)
        seen = set()
        blocks = []
        for b in parser.blocks:
            text = WS.sub(" ", b["text"]).strip()
            if len(text) < 8 or len(text) > 1200 or text in seen:
                continue
            seen.add(text)
            if not EN_SIGNAL.search(text) and not WOW_SIGNAL.search(text):
                continue
            covered = text in exact
            jargon_hits = [k for k in jargon.keys() if isinstance(k, str) and len(k) >= 3 and k.casefold() in text.casefold()]
            blocks.append({
                "tag": b["tag"],
                "text": text,
                "exact_override": covered,
                "wow_signal": bool(WOW_SIGNAL.search(text)),
                "jargon_hits": jargon_hits[:12]
            })
        row["blocks"] = blocks
        row["stats"] = {
            "block_count": len(blocks),
            "exact_covered": sum(1 for b in blocks if b["exact_override"]),
            "wow_blocks": sum(1 for b in blocks if b["wow_signal"]),
            "wow_exact_covered": sum(1 for b in blocks if b["wow_signal"] and b["exact_override"])
        }
        row["ok"] = True
    except Exception as exc:
        row["error"] = str(exc)
    report["pages"].append(row)

OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
for p in report["pages"]:
    print(p["id"], p.get("stats", {}), p.get("error", ""))
