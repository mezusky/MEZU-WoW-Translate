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

try:
    from .locale_glossary import same_base_language
except ImportError:  # Direct CLI execution from scripts/
    from locale_glossary import same_base_language

ENTITY = re.compile(r"\b(spell|item|npc|quest|achievement)=(\d+)\b")
PLACEHOLDER = re.compile(r"\{\{[A-Z][A-Z0-9_]*\}\}")
# Wowhead guide templates sometimes expose unresolved utility slots in source.
# Preserve these machine-readable markers, not arbitrary uppercase WoW acronyms.
WOWHEAD_SLOT = re.compile(r"\b(?:UTIL\d+_(?:NAME|USECASE)|BRTOOL\d+)\b")
# Preserve explicit percentages in rotations, tier bonuses and stat thresholds.
# Allow a French space before % and comma as the decimal separator.
PERCENT = re.compile(r"(?<![\w.,])\d+(?:[.,]\d+)?\s*%")
# In a range such as 10-20%, the percent sign applies to both endpoints.
PERCENT_RANGE = re.compile(
    r"(?<![\w.,])(?P<lower>\d+(?:[.,]\d+)?)\s*(?:-|–|—|to|à)\s*\d+(?:[.,]\d+)?\s*%",
    re.IGNORECASE,
)

# A range can also be written as "between 10 and 20%" / "entre 10 et 20 %".
BETWEEN_PERCENT_RANGE = re.compile(
    r"\b(?:between|entre)\s+(?P<lower>\d+(?:[.,]\d+)?)\s+(?:and|et)\s+\d+(?:[.,]\d+)?\s*%",
    re.IGNORECASE,
)

def percentages(text):
    values = [re.sub(r"\s+", "", match.group()).replace(",", ".")
              for match in PERCENT.finditer(text)]
    values.extend(match.group("lower").replace(",", ".") + "%"
                  for match in PERCENT_RANGE.finditer(text))
    values.extend(match.group("lower").replace(",", ".") + "%"
                  for match in BETWEEN_PERCENT_RANGE.finditer(text))
    return sorted(values)


# Optional exact-number audit for short stat/gear snippets. Keep this opt-in:
# prose can legitimately change numbers through localization or paraphrasing.
NUMBER = re.compile(r"(?<![\w.,])\d+(?:[.,\u00a0\u202f ]\d{3})*(?:[.,]\d+)?(?!\w)")

def numeric_values(text):
    """Compare numeric values independent of French grouping/decimal punctuation."""
    values = []
    for match in NUMBER.finditer(text):
        token = match.group().replace(" ", "").replace("\u00a0", "").replace("\u202f", "")
        if "," in token and "." in token:
            decimal = "," if token.rfind(",") > token.rfind(".") else "."
            token = token.replace("." if decimal == "," else ",", "").replace(decimal, ".")
        elif re.fullmatch(r"\d{1,3}(?:[.,]\d{3})+", token):
            token = token.replace(",", "").replace(".", "")
        else:
            token = token.replace(",", ".")
        values.append(str(float(token)) if "." in token else str(int(token)))
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


# Addon import strings are machine-readable data, not translatable prose.
# Require at least two semicolon-delimited key:value fields to avoid
# mistaking ordinary headings or prose for an import record.
IMPORT_LINE = re.compile(r"^\s*[A-Za-z][A-Za-z0-9_]*:[^;\n]+;(?:[A-Za-z][A-Za-z0-9_]*:[^;\n]*;?){1,}\s*$")

def import_records(text):
    # Preserve sequence: addon import lines can encode ordered cooldown plans.
    return [line.strip() for line in text.splitlines()
            if IMPORT_LINE.fullmatch(line)]



# WoW talent exports are opaque, copy/paste data. Only consider long,
# uninterrupted base64-alphabet tokens; short words and normal prose are
# deliberately excluded to avoid false positives. Preserve duplicates/order.
TALENT_EXPORT = re.compile(r"(?<![A-Za-z0-9+/=])[A-Za-z0-9+/=]{80,}(?![A-Za-z0-9+/=])")

def talent_exports(text):
    return [token for token in TALENT_EXPORT.findall(text)
            if any(c.isupper() for c in token) and
            (any(c.islower() for c in token) or any(c.isdigit() for c in token))]


# Optional check for short tier-bonus labels, not whole guide prose.\n# The labels can be localized; preserve their 2-piece / 4-piece identity.\nTIER_BONUS_LABEL = re.compile(\n    r"(?<!\\w)([24])\\s*(?:pc|[- ]?set|[- ]?piece(?:s)?|\\s+pi[eè]ces?)(?!\\w)",\n    re.IGNORECASE,\n)\n\ndef tier_bonus_labels(text):\n    return sorted(match.group(1) for match in TIER_BONUS_LABEL.finditer(text))\n\n\n# Optional audit of explicit stat-priority relationships. Names may be localized,
# but the ordering operators must retain their sequence and strength.
# Only use for captured priority snippets, never arbitrary prose or HTML.
PRIORITY_OPERATOR = re.compile(r"(?<![<>=])(?:>{1,4}|<{1,4}|>=|<=|=)(?![<>=])")

def priority_operators(text):
    return PRIORITY_OPERATOR.findall(text)


def audit_sample(sample):
    source = sample["source"]
    translated = sample["translated"]
    source_locale = sample["sourceLanguage"].replace("_", "-").lower()
    target_locale = sample["targetLanguage"].replace("_", "-").lower()
    findings = []
    # Locale variants of the same language do not require prose translation.
    # Keep full locale tags for future target-specific terminology checks.
    # Reuse the shared locale contract: zh-CN and zh-TW have distinct
    # writing systems even though both use the same base language.
    same_language = same_base_language(source_locale, target_locale)
    if same_language:
        if translated != source:
            findings.append("same_language_changed")
        return findings
    if not translated.strip():
        findings.append("empty_translation")
    if source.strip() == translated.strip() and len(source.split()) >= 3:
        findings.append("unchanged_prose_review")
    if sorted(PLACEHOLDER.findall(source)) != sorted(PLACEHOLDER.findall(translated)):
        findings.append("placeholder_mismatch")
    if sorted(WOWHEAD_SLOT.findall(source)) != sorted(WOWHEAD_SLOT.findall(translated)):
        findings.append("wowhead_slot_mismatch")
    if sample.get("preserveTierBonusLabels") and tier_bonus_labels(source) != tier_bonus_labels(translated):\n        findings.append("tier_bonus_label_mismatch")\n    if sample.get("preserveStatPriority") and priority_operators(source) != priority_operators(translated):
        findings.append("stat_priority_relation_mismatch")
    if sample.get("preserveNumbers") and numeric_values(source) != numeric_values(translated):
        findings.append("number_mismatch")
    if import_records(source) != import_records(translated):
        findings.append("technical_import_mismatch")
    if talent_exports(source) != talent_exports(translated):
        findings.append("talent_export_mismatch")
    if percentages(source) != percentages(translated):
        findings.append("percentage_mismatch")
    source_ids = sorted(ENTITY.findall(source))
    translated_ids = sorted(ENTITY.findall(translated))
    if source_ids != translated_ids:
        findings.append("entity_id_mismatch")
    # Opt-in for a single captured priority list, not an entire guide: the
    # same IDs may legitimately appear in different order across sections.
    # Compare canonical entity references, never localized display names.
    if sample.get("preserveEntityOrder") and ENTITY.findall(source) != ENTITY.findall(translated):
        findings.append("entity_order_mismatch")
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
