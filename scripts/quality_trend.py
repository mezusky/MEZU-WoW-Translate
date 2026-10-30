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

# Audits must not invent a tank/healer/DPS mix on role-neutral guide slugs.
# This compact data-only mapping is independent of translation direction.
SPEC_ROLES = json.loads((Path(__file__).resolve().parents[1] / "data" /
                         "wow_spec_roles.json").read_text(encoding="utf-8"))["roles"]


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
    path = re.sub(r"^/(?!ptr(?:-\d+)?/)[a-z]{2,3}(?:-[a-z0-9]{2,8})*/(?=guide/)",
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
    # Even gear, raid and tier-set URLs (which lack a role suffix) must
    # agree with the known WoW specialization. Unknown specs fail closed.
    expected_role = SPEC_ROLES.get(match.group(1).lower(), {}).get(match.group(2).lower())
    if expected_role is None or case.get("role") != expected_role:
        return False
    # When the guide slug explicitly identifies the role, reject contradictory
    # metadata rather than allowing a DPS guide to masquerade as tank evidence.
    # Other slugs (gear, macros, talents) do not encode role: do not guess.
    slug = path.rsplit("/", 1)[-1].lower()
    # Legacy /bis-gear-pve-* paths are not live canonical guide identities.
    # A stale or fabricated URL must never count toward browser coverage.
    if slug.startswith("bis-gear") and slug != "bis-gear":
        return False
    role_hint = (re.search(r"-pve-(tank|healer|dps)$", slug)
                 or re.fullmatch(r"(tank|healer|dps)-leveling-tips", slug)
                 or re.fullmatch(r"mage-tower-(tank|healer|dps)-challenge-(?:[a-z0-9]+-)*[a-z0-9]+", slug))
    if role_hint is not None and case.get("role") != role_hint.group(1):
        return False

    # A browser audit must not claim several content sections from a set of
    # URLs that all show the same section. Ground the declared section in the
    # actual Wowhead guide slug; unknown slugs fail closed until classified.
    section = case.get("section")
    # Accept only known fixed guide slugs. Prefix matching used to accept
    # invented URLs such as mythic-plus-dungeon-tips-extra as browser evidence.
    # Role-specific guide sections are a compact pattern, not an open prefix.
    section_patterns = (
        (r"rotation-cooldowns-pve-(?:tank|healer|dps)", "rotation"),
        (r"talent-builds-pve-(?:tank|healer|dps)", "talents"),
        (r"abilities-talents-pve-(?:tank|healer|dps)", "abilities"),
        (r"stat-priority-pve-(?:tank|healer|dps)", "stats"),
        (r"enchants-gems-pve-(?:tank|healer|dps)", "consumables"),
        (r"overview-pve-(?:tank|healer|dps)", "overview"),
        (r"mage-tower-(?:tank|healer|dps)-challenge-(?:[a-z0-9]+-)*[a-z0-9]+", "mage-tower"),
    )
    section_exact = {
        "bis-gear": "gear",
        "mythic-plus-dungeon-tips": "mythic-plus",
        "mythic-keystones-and-dungeons": "mythic-plus",
        "addons-macro-ui-imports": "macros",
        "manaforge-omega-raid-tips": "raid",
        "dps-leveling-tips": "leveling",
        "healer-leveling-tips": "leveling",
        "tank-leveling-tips": "leveling",
    }
    expected = section_exact.get(slug)
    if expected is None:
        expected = next((name for pattern, name in section_patterns
                         if re.fullmatch(pattern, slug)), None)
    if expected is None:
        # Bare section labels such as /rotation, /talents and /gear are
        # not canonical Wowhead class-guide URLs. Accepting them would let
        # synthetic test fixtures count as real browser audit evidence.
        expected = {
            "basics": "basics",
            "cheat-sheet": "cheat-sheet",
            "tier-set-bonuses": "tier-set",
        }.get(slug)
    if expected is None:
        # Expansion/season labels evolve, but the Wowhead section structure
        # remains stable. Match complete slugs to avoid accepting fabricated
        # "raid" or "season" evidence from arbitrary guide names.
        if re.fullmatch(r"[a-z][a-z0-9-]*-season-[1-9][0-9]*-raid-tips", slug):
            expected = "raid"
        elif re.fullmatch(r"[a-z][a-z0-9-]*-season-[1-9][0-9]*", slug):
            expected = "season"
        elif re.fullmatch(r"[a-z][a-z0-9-]*-pre-patch", slug):
            expected = "prepatch"
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
        # Separate *measured* browser evidence from a *clean* audit.
        # A claimed browserVerifiedPages count without a matching manifest
        # must never produce a seemingly precise novelty rate.
        cases = sample.get("browserCases")
        verified_cases = (isinstance(cases, list) and len(cases) == new_pages
                          and new_pages > 0 and all(isinstance(c, dict) for c in cases))
        urls = []
        if verified_cases:
            urls = [_canonical_guide_url(c.get("url")) for c in cases]
            verified_cases = (
                all(u is not None for u in urls)
                and len(set(urls)) == new_pages
                and all(_case_matches_guide_identity(c, u) for c, u in zip(cases, urls))
                and all(c.get("sourceLanguage") == source_language
                        and c.get("targetLanguage") == target_language for c in cases)
                and all(c.get("browserRendered") is True for c in cases)
                and all(isinstance(c.get(key), str) and c[key]
                        for c in cases for key in ("wowClass", "spec", "role", "section"))
            )
        # Failed translations are still measurable, but cannot be clean.
        # Cross-role/section coverage and heldouts are stricter stop criteria.
        valid_cases = (
            verified_cases and new_pages >= 5
            and all(c.get("strictPass") is True for c in cases)
            and len({c["wowClass"] for c in cases}) >= 3
            and len({c["spec"] for c in cases}) >= 3
            and {"tank", "healer", "dps"}.issubset({c["role"] for c in cases})
            and len({c["section"] for c in cases}) >= 2
            and sum(c.get("heldout") is True for c in cases) >= 2
        )
        # Indexed excerpts can reveal terminology but cannot measure rendered
        # French output or count toward the two-cycle stop condition.
        rendered = sample.get("auditMethod") == "browser-rendered"
        measured = (rendered and verified_cases and valid_pair
                    and browser_pages == new_pages and novel is not None)
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
