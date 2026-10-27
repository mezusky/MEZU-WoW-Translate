#!/usr/bin/env python3
"""Fetch selected Wowhead guides and report translation coverage/regression signals.

This does not attempt to replace the browser translator. It gives MEZU a stable,
repeatable view of the real guide source so automated review can spot untranslated
or uncovered WoW phrases before relying on screenshots from the user.
"""
import json, re, urllib.request
from pathlib import Path
from html_block_extractor import extract_readable_blocks
from guide_audit_boundaries import trim_guide_footer
from wowhead_source_status import classify_html_source, classify_fetch_error
from source_language_evidence import detect_source_language, audit_source_prose

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CFG = DATA / "wowhead_regression_pages.json"
OUT = DATA / "wowhead_regression_report.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/154 Safari/537.36 MEZU-WoW-Translate"

WS = re.compile(r"\s+")
WOW_SIGNAL = re.compile(r"\b(?:Paladin|Demon Hunter|Tank|Mythic\+|Raid|cooldown|GCD|Holy Power|Haste|Crit|Mastery|Versatility|BiS|Best in Slot|Raidbots|Great Vault|spender|generator|overcap|defensive|mitigation)\b", re.I)

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read().decode("utf-8", "replace")

def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

cfg = load_json(CFG)
pack = load_json(DATA / "datapack.json")
exact = pack.get("exact", {}) or {}
phrase_memory = pack.get("phrase_memory", {}) or {}
jargon = pack.get("jargon", {}) or {}
source_language = cfg.get("sourceLanguage", pack.get("sourceLanguage", "en"))
target_language = cfg.get("targetLanguage", pack.get("targetLanguage", "fr"))
language_profiles = load_json(DATA / "audit_language_signals.json")["profiles"]

report = {"schema": 2, "auditMethod": "source-only; browser translation not verified",
          "expectedSourceLanguage": source_language, "targetLanguage": target_language,
          "languageEvidenceMethod": "conservative prose stopword evidence; unknown is not a failure",
          "pages": []}

for page in cfg.get("pages", []):
    url = page["url"]
    row = {"id": page["id"], "url": url, "ok": False, "sourceStatus": "pending", "blocks": [], "stats": {}}
    try:
        raw = fetch(url)
        # A 200 response may be a JS challenge, not guide prose.
        row["sourceStatus"], reason = classify_html_source(raw)
        if row["sourceStatus"] != "accessible":
            row["accessNote"] = reason
            report["pages"].append(row)
            continue
        parsed_blocks = trim_guide_footer(extract_readable_blocks(raw))
        evidence = detect_source_language(parsed_blocks, language_profiles)
        row["sourceLanguageEvidence"] = evidence
        detected = evidence["detectedLanguage"]
        if detected and detected.split("-")[0] != source_language.split("-")[0]:
            row["sourceStatus"] = "language_mismatch"
            row["accessNote"] = ("Prose appears to be " + detected +
                                 ", not expected " + source_language +
                                 "; not scored as a translation failure")
            report["pages"].append(row)
            continue
        seen = set()
        blocks = []
        for tag, value in parsed_blocks:
            text = WS.sub(" ", value).strip()
            if len(text) < 8:
                continue
            # Score length after stripping opaque widgets, otherwise a long
            # import payload can discard otherwise readable adjacent prose.
            clean, source_signal = audit_source_prose(text, source_language, language_profiles)
            if len(clean) < 8 or len(clean) > 1200 or clean in seen:
                continue
            # English WoW labels remain useful even without prose stopwords.
            # Other source locales rely on their data-only language profile.
            wow_signal = (source_language.replace("_", "-").split("-")[0].casefold() == "en"
                          and bool(WOW_SIGNAL.search(clean)))
            if not source_signal and not wow_signal:
                continue
            seen.add(clean)
            covered = clean in exact or clean in phrase_memory
            jargon_hits = [k for k in jargon.keys() if isinstance(k, str) and len(k) >= 3 and re.search(r"(?<!\w)" + re.escape(k) + r"(?!\w)", clean, re.I)]
            blocks.append({
                "tag": tag,
                "text": clean,
                "exact_override": covered,
                "wow_signal": wow_signal,
                "jargon_hits": jargon_hits[:12]
            })
        row["blocks"] = [{k: v for k, v in b.items() if k != "text"} for b in blocks]
        row["stats"] = {
            "block_count": len(blocks),
            "exact_covered": sum(1 for b in blocks if b["exact_override"]),
            "wow_blocks": sum(1 for b in blocks if b["wow_signal"]),
            "wow_exact_covered": sum(1 for b in blocks if b["wow_signal"] and b["exact_override"])
        }
        row["sourceStatus"] = "accessible" if blocks else "unscorable"
        row["ok"] = bool(blocks)
    except Exception as exc:
        row["sourceStatus"], row["accessNote"] = classify_fetch_error(exc)
    report["pages"].append(row)

OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
for p in report["pages"]:
    print(p["id"], p["sourceStatus"], p.get("stats", {}), p.get("accessNote", ""))
