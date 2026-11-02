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


def main(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    print(json.dumps(summarize(data["cycles"]), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/wowhead_audit_trend.json")
