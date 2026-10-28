"""Summarize explicit cross-page quality samples without inventing missing rates.

Audit JSON files may include a `qualitySample` object. Older reports are
ignored: glossary edits and indexed snippets are not browser translation audits.
This is a local, data-only reporting tool; it never fetches Wowhead.
"""
import json
import sys
from pathlib import Path


def summarize(reports):
    cycles = []
    for report in reports:
        sample = report.get("qualitySample")
        if not isinstance(sample, dict):
            continue
        cycle_id = sample.get("cycleId")
        audited_at = sample.get("auditedAt")
        if not isinstance(cycle_id, str) or not cycle_id or not isinstance(audited_at, str):
            raise ValueError("Quality samples require cycleId and auditedAt")
        new_pages = sample.get("newPagesAudited")
        novel = sample.get("novelIssueFamilies")
        browser_pages = sample.get("browserVerifiedPages", 0)
        if type(new_pages) is not int or new_pages < 0:
            raise ValueError("newPagesAudited must be a nonnegative integer")
        if type(browser_pages) is not int or browser_pages < 0:
            raise ValueError("browserVerifiedPages must be a nonnegative integer")
        if novel is not None and (type(novel) is not int or novel < 0):
            raise ValueError("novelIssueFamilies must be null or nonnegative")
        # A summary boolean cannot prove cross-page coverage. Require a
        # per-page browser evidence manifest before counting a clean cycle.
        cases = sample.get("browserCases")
        valid_cases = (isinstance(cases, list) and len(cases) == new_pages
                       and new_pages >= 5 and all(isinstance(c, dict) for c in cases))
        if valid_cases:
            urls = [c.get("url") for c in cases]
            valid_cases = (
                all(isinstance(u, str) and u.startswith("https://www.wowhead.com/") for u in urls)
                and len(set(urls)) == new_pages
                and all(c.get("browserRendered") is True and c.get("strictPass") is True
                        for c in cases)
                and len({c.get("wowClass") for c in cases if isinstance(c.get("wowClass"), str)}) >= 3
                and len({c.get("spec") for c in cases if isinstance(c.get("spec"), str)}) >= 3
                and {"tank", "healer", "dps"}.issubset({c.get("role") for c in cases})
                and len({c.get("section") for c in cases if isinstance(c.get("section"), str)}) >= 2
                and sum(c.get("heldout") is True for c in cases) >= 2
            )
        # Indexed excerpts can reveal terminology but cannot measure rendered
        # French output or count toward the two-cycle stop condition.
        rendered = sample.get("auditMethod") == "browser-rendered"
        measured = (rendered and new_pages > 0 and browser_pages >= new_pages
                    and novel is not None)
        strict = (measured and valid_cases
                  and sample.get("crossRoleVerified") is True
                  and sample.get("unrelatedHeldoutsVerified") is True
                  and novel / new_pages <= 0.05
                  and sample.get("strictAuditPassed") is True)
        cycles.append({
            "cycleId": cycle_id,
            "auditedAt": audited_at,
            "newPagesAudited": new_pages,
            "browserVerifiedPages": browser_pages,
            "novelIssueRate": novel / new_pages if measured else None,
            "strictCleanCycle": bool(strict),
        })
    cycles.sort(key=lambda c: (c["auditedAt"], c["cycleId"]))
    if len({c["cycleId"] for c in cycles}) != len(cycles):
        raise ValueError("Duplicate quality cycle IDs")
    clean_streak = 0
    for cycle in reversed(cycles):
        if not cycle["strictCleanCycle"]:
            break
        clean_streak += 1
    return {
        "cycles": cycles,
        "measuredCycleCount": sum(c["novelIssueRate"] is not None for c in cycles),
        "consecutiveStrictCleanCycles": clean_streak,
        "eligibleToConsiderStopping": clean_streak >= 2,
    }


def main(directory):
    reports = []
    for path in sorted(Path(directory).glob("*.json")):
        reports.append(json.loads(path.read_text(encoding="utf-8")))
    print(json.dumps(summarize(reports), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "audits")
