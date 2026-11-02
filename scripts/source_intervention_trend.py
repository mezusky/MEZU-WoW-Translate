#!/usr/bin/env python3
"""Source-only intervention proxy; never a browser translation quality score.

Use only first-seen, independently sampled guide IDs with explicit counts.
A family can affect several pages, so these are interventions per page, NOT
the fraction of pages with errors or a reason to stop the hourly audit.
"""
import json
import sys
from pathlib import Path


def _nonnegative_int(value):
    return type(value) is int and value >= 0


def _aggregate(rows):
    pages = sum(row["pages"] for row in rows)
    families = sum(row["families"] for row in rows)
    overrides = sum(row["overrides"] for row in rows)
    return {
        "cycles": len(rows),
        "sampledPages": pages,
        "newReusableTermFamilies": families,
        "newManualSentenceOverrides": overrides,
        "termFamiliesPerPage": round(families / pages, 4) if pages else None,
        "manualOverridesPerPage": round(overrides / pages, 4) if pages else None,
    }


def summarize(cycles, window=10):
    if not isinstance(cycles, list) or type(window) is not int or window < 1:
        raise ValueError("Expected a cycle list and a positive window size")
    seen = set()
    eligible = []
    excluded = {"invalidSample": 0, "missingMetrics": 0, "repeatedPages": 0}
    for cycle in cycles:
        ids = cycle.get("sampledPageIds")
        count = cycle.get("sampledPageCount")
        if (not isinstance(ids, list) or not _nonnegative_int(count)
                or count == 0 or len(ids) != count
                or any(not isinstance(page_id, str) or not page_id.strip()
                       for page_id in ids)):
            excluded["invalidSample"] += 1
            continue
        # Even a cycle lacking metrics establishes that these pages were seen.
        # Otherwise later repeats could masquerade as independent heldouts.
        fresh = len(set(ids)) == count and all(page_id not in seen for page_id in ids)
        seen.update(ids)
        families = cycle.get("newReusableTermFamiliesObserved")
        overrides = cycle.get("newManualSentenceOverrides")
        if not (_nonnegative_int(families) and _nonnegative_int(overrides)):
            excluded["missingMetrics"] += 1
        elif not fresh:
            excluded["repeatedPages"] += 1
        else:
            eligible.append({"pages": count, "families": families,
                             "overrides": overrides})
    early = _aggregate(eligible[:window])
    recent = _aggregate(eligible[-window:])
    # Overlapping windows cannot establish a directional comparison.
    comparable = len(eligible) >= 2 * window
    trend = None
    if comparable:
        a, b = early["termFamiliesPerPage"], recent["termFamiliesPerPage"]
        trend = "lower" if b < a else "higher" if b > a else "unchanged"
    return {
        "measurementType": "source-only editorial intervention proxy",
        "browserTranslationErrorRate": None,
        "novelTranslationIssueRate": None,
        "eligibleCycles": len(eligible),
        "excludedCycles": excluded,
        "windowCycles": window,
        "early": early,
        "recent": recent,
        "recentTermFamilyRateVsEarly": trend,
        "caveat": ("Sample selection and author reporting vary; this proxy cannot "
                   "verify translated output, DOM behavior, or stop criteria."),
    }


def load_cycles(history_path, audits_dir, corpus_path):
    """Append only explicit, corpus-grounded source-only audit samples.

    Older narrative audits do not provide comparable counts and are ignored.
    This avoids repeatedly rewriting the large historical trend file just to
    record one new heldout cycle. No network or browser claims are involved.
    """
    if __package__:
        from .locale_glossary import normalize_locale, same_base_language
    else:
        from locale_glossary import normalize_locale, same_base_language

    history = json.loads(Path(history_path).read_text(encoding="utf-8"))
    cycles = list(history["cycles"])
    known = {
        page["id"] for page in
        json.loads(Path(corpus_path).read_text(encoding="utf-8"))["pages"]
    }
    audit_ids = set()
    for path in sorted(Path(audits_dir).glob("*.json")):
        audit = json.loads(path.read_text(encoding="utf-8"))
        if "sourceInterventionSample" not in audit:
            continue
        sample = audit["sourceInterventionSample"]
        if not isinstance(sample, dict) or audit.get("auditMethod") != "indexed-source-only":
            raise ValueError(f"Invalid source-only intervention sample: {path}")
        cycle_id = sample.get("cycleId")
        ids = sample.get("sampledPageIds")
        source, target = sample.get("sourceLanguage"), sample.get("targetLanguage")
        if (not isinstance(cycle_id, str) or not cycle_id.strip()
                or cycle_id in audit_ids or not isinstance(ids, list)
                or not ids or any(not isinstance(i, str) or i not in known for i in ids)
                or len(set(ids)) != len(ids)
                or sample.get("sampledPageCount") != len(ids)
                or type(sample.get("newReusableTermFamiliesObserved")) is not int
                or sample["newReusableTermFamiliesObserved"] < 0
                or type(sample.get("newManualSentenceOverrides")) is not int
                or sample["newManualSentenceOverrides"] < 0
                or sample.get("browserRenderedPagesVerified") != 0):
            raise ValueError(f"Invalid or ungrounded source-only sample: {path}")
        try:
            source, target = normalize_locale(source), normalize_locale(target)
            if same_base_language(source, target):
                raise ValueError("No translation needed")
        except ValueError as exc:
            raise ValueError(f"Invalid translation direction: {path}") from exc
        audit_ids.add(cycle_id)
        cycles.append({**sample, "date": audit.get("date"), "cycleId": cycle_id})
    # Stable ordering preserves the original order of multiple audits on one day.
    # A new file cannot retroactively change first-seen page attribution.
    return sorted(cycles, key=lambda row: row.get("date", ""))


def main(path, audits_dir="audits", corpus_path="data/wowhead_regression_pages.json"):
    cycles = load_cycles(path, audits_dir, corpus_path)
    print(json.dumps(summarize(cycles), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/wowhead_audit_trend.json")
