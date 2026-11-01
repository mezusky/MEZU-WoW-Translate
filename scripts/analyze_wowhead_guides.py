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
from source_language_evidence import detect_source_language, audit_source_prose, compile_wow_term_signals
from audit_locale_contract import resolve_audit_locale_contract, source_accept_language
from jargon_coverage import JargonCoverage

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CFG = DATA / "wowhead_regression_pages.json"
OUT = DATA / "wowhead_regression_report.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/154 Safari/537.36 MEZU-WoW-Translate"

WS = re.compile(r"\s+")

def fetch(url, source_language):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept-Language": source_accept_language(source_language),
    })
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read().decode("utf-8", "replace")

def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

cfg = load_json(CFG)
pack = load_json(DATA / "datapack.json")
exact = pack.get("exact", {}) or {}
phrase_memory = pack.get("phrase_memory", {}) or {}
jargon = pack.get("jargon", {}) or {}
contract = resolve_audit_locale_contract(cfg, pack)
source_language = contract["sourceLanguage"]
target_language = contract["targetLanguage"]
language_signals = load_json(DATA / "audit_language_signals.json")
language_profiles = language_signals["profiles"]
source_wow_pattern = compile_wow_term_signals(language_signals.get("wowTerms", {}), source_language)
jargon_coverage = JargonCoverage(jargon)

report = {"schema": 2, "auditMethod": "source-only; browser translation not verified",
          "expectedSourceLanguage": source_language, "targetLanguage": target_language,
          "languageEvidenceMethod": "conservative prose stopword evidence; unknown is not a failure",
          "localeContractStatus": contract["status"],
          "coverageEligible": contract["canScore"],
          "pages": []}

for page in cfg.get("pages", []):
    url = page["url"]
    row = {"id": page["id"], "url": url, "ok": False, "sourceStatus": "pending", "blocks": [], "stats": {}}
    # Do not fetch or score with an incompatible language-direction Data Pack.
    # Same-base-language requests require no translation at all.
    if not contract["canScore"]:
        row["sourceStatus"] = contract["status"]
        row["accessNote"] = "No translation audit with this locale/Data Pack pair"
        report["pages"].append(row)
        continue
    try:
        raw = fetch(url, source_language)
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
            # Keep original line breaks until executable macro lines are
            # removed. Flattening first makes /cast and #showtooltip invisible
            # to the line-anchored filter in source_language_evidence.
            # Also score length only after stripping opaque widgets.
            clean, source_signal = audit_source_prose(value, source_language, language_profiles)
            if len(clean) < 8 or len(clean) > 1200 or clean in seen:
                continue
            # Short WoW labels can be useful without prose stopwords; their
            # locale-scoped terms live in data, never hardcoded as English.
            wow_signal = bool(source_wow_pattern and source_wow_pattern.search(clean))
            if not source_signal and not wow_signal:
                continue
            seen.add(clean)
            covered = clean in exact or clean in phrase_memory
            jargon_hits = jargon_coverage.hits(clean)
            blocks.append({
                "tag": tag,
                "text": clean,
                "exact_override": covered,
                "wow_signal": wow_signal,
                "jargon_hits": jargon_hits
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
