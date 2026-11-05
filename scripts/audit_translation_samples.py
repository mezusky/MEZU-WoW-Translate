#!/usr/bin/env python3
"""Audit captured translation samples without pretending to run the browser Translator API.

Input JSON: {"samples":[{"sourceLanguage":"en","targetLanguage":"fr",
"source":"...", "translated":"...", "entities":[{"id":123,
"targetName":"Nom officiel"}]}]}.
Samples must be short, user-owned snippets; do not archive complete guides.
"""
import argparse
import json
import re
from pathlib import Path

ENTITY = re.compile(r"\b(?:spell|item|npc|quest|achievement)=(\d+)\b")
PLACEHOLDER = re.compile(r"\{\{[A-Z][A-Z0-9_]*\}\}")

def audit_sample(sample):
    source = sample["source"]
    translated = sample["translated"]
    source_locale = sample["sourceLanguage"].split("-")[0].lower()
    target_locale = sample["targetLanguage"].split("-")[0].lower()
    findings = []
    if source_locale == target_locale:
        if translated != source:
            findings.append("same_language_changed")
        return findings
    if not translated.strip():
        findings.append("empty_translation")
    if source.strip() == translated.strip() and len(source.split()) >= 5:
        findings.append("unchanged_prose_review")
    if sorted(PLACEHOLDER.findall(source)) != sorted(PLACEHOLDER.findall(translated)):
        findings.append("placeholder_mismatch")
    source_ids = sorted(ENTITY.findall(source))
    translated_ids = sorted(ENTITY.findall(translated))
    if source_ids != translated_ids:
        findings.append("entity_id_mismatch")
    for entity in sample.get("entities", []):
        name = entity.get("targetName")
        if name and name not in translated:
            findings.append("missing_target_entity:" + str(entity["id"]))
    return findings

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("samples", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.samples.read_text(encoding="utf-8"))
    rows = []
    for index, sample in enumerate(payload["samples"]):
        findings = audit_sample(sample)
        rows.append({"id": sample.get("id", str(index)), "findings": findings,
                     "passed": not findings})
    report = {"method": "captured-output structural checks; not browser verification",
              "sampleCount": len(rows), "passed": sum(row["passed"] for row in rows),
              "results": rows}
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        args.report.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 1 if any(not row["passed"] for row in rows) else 0

if __name__ == "__main__":
    raise SystemExit(main())
