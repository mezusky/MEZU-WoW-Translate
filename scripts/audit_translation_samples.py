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
import unicodedata
from pathlib import Path

ENTITY = re.compile(r"\b(spell|item|npc|quest|achievement)=(\d+)\b")
PLACEHOLDER = re.compile(r"\{\{[A-Z][A-Z0-9_]*\}\}")
# Preserve explicit percentages in rotations, tier bonuses and stat thresholds.
# Allow a French space before % and comma as the decimal separator.
PERCENT = re.compile(r"(?<![\w.,])\d+(?:[.,]\d+)?\s*%")
# In a range such as 10-20%, the percent sign applies to both endpoints.
PERCENT_RANGE = re.compile(
    r"(?<![\w.,])(?P<lower>\d+(?:[.,]\d+)?)\s*(?:-|–|—|to|à)\s*\d+(?:[.,]\d+)?\s*%",
    re.IGNORECASE,
)

def percentages(text):
    values = [match.group().replace(" ", "").replace("\u00a0", "").replace("\u202f", "").replace(",", ".")
              for match in PERCENT.finditer(text)]
    values.extend(match.group("lower").replace(",", ".") + "%"
                  for match in PERCENT_RANGE.finditer(text))
    return sorted(values)

def normalized_name(value):
    """Normalize typographic variants without weakening entity ID checks."""
    value = unicodedata.normalize("NFKC", value).casefold()
    value = value.replace("’", "'").replace("‘", "'")
    return " ".join(value.split())


def contains_official_name(text, name):
    """Match a full localized name, not a substring of a different WoW name."""
    expected = normalized_name(name)
    actual = normalized_name(text)
    return bool(expected and re.search(r"(?<!\w)" + re.escape(expected) + r"(?!\w)", actual))


def linked_entity_labels(text, kind, entity_id):
    """Read every captured 'Localized Name (spell=123)' label, if present.

    Return None when the capture lacks this structure; a global name search
    cannot prove that the correct label belongs to the referenced entity.
    """
    marker = re.compile(r"\(\s*" + re.escape(kind) + r"=" +
                        re.escape(entity_id) + r"\s*\)")
    labels = []
    for match in marker.finditer(text):
        prefix = text[:match.start()].rstrip()
        parenthesized = re.search(r"\(([^()]*)\)\s*$", prefix)
        if parenthesized:
            labels.append(parenthesized.group(1).strip())
            continue
        words = re.search(r"([A-ZÀ-ÖØ-Þ][\w’'’-]*(?:\s+[\w’'’-]+)*)\s*$", prefix)
        labels.append(words.group(1).strip() if words else "")
    return labels


def audit_sample(sample):
    source = sample["source"]
    translated = sample["translated"]
    source_locale = sample["sourceLanguage"].replace("_", "-").lower()
    target_locale = sample["targetLanguage"].replace("_", "-").lower()
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
    if percentages(source) != percentages(translated):
        findings.append("percentage_mismatch")
    source_ids = sorted(ENTITY.findall(source))
    translated_ids = sorted(ENTITY.findall(translated))
    if source_ids != translated_ids:
        findings.append("entity_id_mismatch")
    for entity in sample.get("entities", []):
        name = entity.get("targetName")
        entity_id = str(entity.get("id", ""))
        # Only require the official target name when this entity occurs in
        # the source. Otherwise an unrelated glossary entry becomes a false failure.
        entity_type = entity.get("type")
        referenced = any(id_ == entity_id and (not entity_type or kind == entity_type)
                         for kind, id_ in source_ids)
        if name and referenced:
            # Legacy samples may omit the entity kind. Infer it only when
            # the source identifies a single kind for this numeric ID.
            # Never guess when an item and a spell share the same ID.
            matching_kinds = {kind for kind, id_ in source_ids if id_ == entity_id}
            resolved_type = entity_type or (next(iter(matching_kinds)) if len(matching_kinds) == 1 else None)
            # Prefer an ID-attached label. A name anywhere else in the prose
            # may belong to another spell (e.g. Frappe vs Frappe mortelle).
            labels = linked_entity_labels(translated, resolved_type, entity_id) if resolved_type else []
            if labels:
                valid = all(bool(re.search(r"(?<!\w)" + re.escape(normalized_name(name)) + r"$", normalized_name(label))) for label in labels)
            else:
                # An unbound name elsewhere cannot establish the label of this ID.
                # Report an unverifiable capture instead of a misleading pass.
                if contains_official_name(translated, name):
                    findings.append("unverified_entity_label:" + entity_id)
                    continue
                valid = False
            if not valid:
                findings.append("missing_target_entity:" + entity_id)
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
