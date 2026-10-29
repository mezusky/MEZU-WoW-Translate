"""Summarize explicit cross-page quality samples without inventing missing rates.

Audit JSON files may include a `qualitySample` object. Older reports are
ignored: glossary edits and indexed snippets are not browser translation audits.
This is a local, data-only reporting tool; it never fetches Wowhead.
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit


def _canonical_guide_url(value):
    """Identify the same Wowhead guide across locale, query and hash variants.

    This is an audit identity, not a fetch URL or a translation locale. PTR
    namespaces remain distinct because their guide content may differ.
    """
    if not isinstance(value, str) or not value.startswith("https://www.wowhead.com/"):
        return None
    try:
        parsed = urlsplit(value)
        if (parsed.scheme != "https" or parsed.hostname != "www.wowhead.com"
                or parsed.username is not None or parsed.password is not None
                or parsed.port is not None):
            return None
    except ValueError:
        return None
    path = parsed.path.rstrip("/")
    if not path or any(ord(char) < 32 for char in path):
        return None
    # Localized WoW entity names do not make /fr/guide and /guide
    # independent source pages. Keep /ptr/ and /ptr-2/ separate.
    path = re.sub(r"^/(?!ptr/)[a-z]{2,3}(?:-[a-z0-9]{2,8})*/(?=guide/)",
                  "/", path, flags=re.IGNORECASE)
    return "https://www.wowhead.com" + path




def _case_matches_guide_identity(case, canonical_url):
    """Do not trust declared class/spec labels without matching the source URL.

    Otherwise one real browser page could be mislabeled as several classes
    and satisfy the cross-class stop gate without independent coverage.
    """
    if canonical_url is None:
        return False
    path = urlsplit(canonical_url).path
    match = re.fullmatch(
        r"/(?:(?:ptr|ptr-\d+)/)?guide/classes/([a-z][a-z-]*)/([a-z][a-z-]*)/[^/]+",
        path, flags=re.IGNORECASE,
    )
    if not (match and case.get("wowClass") == match.group(1).lower()
            and case.get("spec") == match.group(2).lower()):
        return False
    # When the guide slug explicitly identifies the role, reject contradictory
    # metadata rather than allowing a DPS guide to masquerade as tank evidence.
    # Other slugs (gear, macros, talents) do not encode role: do not guess.
    slug = path.rsplit("/", 1)[-1].lower()
    role_hint = (re.search(r"-pve-(tank|healer|dps)$", slug)
                 or re.fullmatch(r"(tank|healer|dps)-leveling-tips", slug))
    if role_hint is not None and case.get("role") != role_hint.group(1):
        return False

    # A browser audit must not claim several content sections from a set of
    # URLs that all show the same section. Ground the declared section in the
    # actual Wowhead guide slug; unknown slugs fail closed until classified.
    section = case.get("section")
    section_prefixes = (
        ("rotation-cooldowns-", "rotation"),
        ("talent-builds-", "talents"),
        ("abilities-talents-", "abilities"),
        ("stat-priority-", "stats"),
        ("enchants-gems-", "consumables"),
        ("bis-gear", "gear"),
        ("overview-pve-", "overview"),
        ("mythic-plus-dungeon-tips", "mythic-plus"),
        ("mythic-keystones-and-dungeons", "mythic-plus"),
        ("addons-macro-ui-imports", "macros"),
        ("midnight-season-2-raid-tips", "raid"),
        ("manaforge-omega-raid-tips", "raid"),
        ("dps-leveling-tips", "leveling"),
        ("healer-leveling-tips", "leveling"),
        ("tank-leveling-tips", "leveling"),
    )
    expected = next((name for prefix, name in section_prefixes
                     if slug.startswith(prefix)), None)
    if expected is None:
        expected = {
            "rotation": "rotation", "talents": "talents",
            "gear": "gear", "raid": "raid",
            "mythic-plus": "mythic-plus", "basics": "basics",
            "cheat-sheet": "cheat-sheet", "tier-set-bonuses": "tier-set",
            "midnight-season-2": "season",
        }.get(slug)
    return section == expected and expected is not None



def _valid_locale(value):
    return isinstance(value, str) and re.fullmatch(
        r"[a-z]{2,3}(?:-[a-z0-9]{2,8})*", value, re.IGNORECASE
    ) is not None


def _timestamp(value):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.utcoffset() is None:
            raise ValueError("timezone required")
        return parsed
    except ValueError as exc:
        raise ValueError("auditedAt must be an offset-aware ISO timestamp") from exc


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
        _timestamp(audited_at)
        source_language = sample.get("sourceLanguage")
        target_language = sample.get("targetLanguage")
        # Regional variants of the same base language require no translation.
        # The browser skip contract must agree with canonical entity projection.
        valid_pair = (_valid_locale(source_language) and _valid_locale(target_language)
                      and source_language.split("-", 1)[0].casefold()
                      != target_language.split("-", 1)[0].casefold())
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
            urls = [_canonical_guide_url(c.get("url")) for c in cases]
            valid_cases = (
                all(u is not None for u in urls)
                and len(set(urls)) == new_pages
                and all(_case_matches_guide_identity(c, u) for c, u in zip(cases, urls))
                and all(c.get("sourceLanguage") == source_language
                        and c.get("targetLanguage") == target_language for c in cases)
                and all(c.get("browserRendered") is True and c.get("strictPass") is True
                        for c in cases)
                and all(isinstance(c.get(key), str) and c[key]
                        for c in cases for key in ("wowClass", "spec", "role", "section"))
                and len({c["wowClass"] for c in cases}) >= 3
                and len({c["spec"] for c in cases}) >= 3
                and {"tank", "healer", "dps"}.issubset({c["role"] for c in cases})
                and len({c["section"] for c in cases}) >= 2
                and sum(c.get("heldout") is True for c in cases) >= 2
            )
        # Indexed excerpts can reveal terminology but cannot measure rendered
        # French output or count toward the two-cycle stop condition.
        rendered = sample.get("auditMethod") == "browser-rendered"
        measured = (rendered and new_pages > 0 and browser_pages >= new_pages
                    and novel is not None)
        strict = (measured and valid_cases and valid_pair
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
            "sourceLanguage": source_language,
            "targetLanguage": target_language,
            "_verifiedUrls": urls if strict else [],
        })
    cycles.sort(key=lambda c: (_timestamp(c["auditedAt"]), c["cycleId"]))
    if len({c["cycleId"] for c in cycles}) != len(cycles):
        raise ValueError("Duplicate quality cycle IDs")
    clean_streak = 0
    newer = None
    for cycle in reversed(cycles):
        if not cycle["strictCleanCycle"]:
            break
        if newer is not None:
            same_pair = (cycle["sourceLanguage"], cycle["targetLanguage"]) == (
                newer["sourceLanguage"], newer["targetLanguage"])
            distinct_time = _timestamp(cycle["auditedAt"]) < _timestamp(newer["auditedAt"])
            fresh_pages = not (set(cycle["_verifiedUrls"]) & set(newer["_verifiedUrls"]))
            if not (same_pair and distinct_time and fresh_pages):
                break
        clean_streak += 1
        newer = cycle
    for cycle in cycles:
        del cycle["_verifiedUrls"]
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
