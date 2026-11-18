#!/usr/bin/env python3
"""Select a reproducible, diverse subset of the Wowhead regression corpus.

This is a *source coverage* sampler, not a translation-quality score. Fetch live
pages with the assistant's browser/web access, never GitHub-hosted runners.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CORPUS = ROOT / "data" / "wowhead_regression_pages.json"
SECTIONS = {
    "overview": "overview", "rotation": "rotation", "abilities-talents": "talents",
    "bis-gear": "gear", "stat-priority": "stats", "enchants-gems": "consumables",
    "mythic-plus": "mythic-plus", "raid": "raid", "tier-set": "tier-set",
}


def dimensions(page):
    url = page["url"].split("?", 1)[0]
    parts = url.split("/")
    edition = parts[3] if len(parts) > 3 and parts[3] in ("classic", "tbc", "wotlk", "cata") else "retail"
    if "classes" in parts:
        index = parts.index("classes")
        klass = parts[index + 1] if len(parts) > index + 1 else "unknown"
        spec = parts[index + 2] if len(parts) > index + 2 else "unknown"
    else:
        klass, spec = "general", "general"
    slug = parts[-1]
    section = next((label for prefix, label in SECTIONS.items() if slug.startswith(prefix)), "other")
    role = "tank" if "tank" in slug else "healer" if "healer" in slug else "dps" if "dps" in slug else "unknown"
    return {"edition": edition, "class": klass, "spec": spec, "classSpec": klass + "/" + spec, "section": section, "role": role}


def sample(pages, count=12, cycle="0"):
    """Greedy marginal coverage, with stable cycle-based tie-breaking."""
    remaining = list(pages)
    chosen = []
    seen = set()
    while remaining and len(chosen) < count:
        def score(page):
            dims = dimensions(page)
            novelty = sum(weight for key, weight in
                          (("section", 6), ("role", 4), ("class", 3), ("edition", 2), ("classSpec", 1))
                          if (key, dims[key]) not in seen)
            tie = hashlib.sha256((cycle + "|" + page["url"]).encode()).hexdigest()
            return novelty, tie
        winner = max(remaining, key=score)
        remaining.remove(winner)
        chosen.append({"id": winner["id"], "url": winner["url"], **dimensions(winner)})
        seen.update(dimensions(winner).items())
    return chosen


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--count", type=int, default=12)
    parser.add_argument("--cycle", default="0", help="Stable cycle label for rotating tied candidates")
    args = parser.parse_args()
    if args.count < 1:
        parser.error("--count must be positive")
    pages = json.loads(args.corpus.read_text(encoding="utf-8"))["pages"]
    print(json.dumps({"cycle": args.cycle, "corpusCount": len(pages),
                      "selectionMethod": "greedy categorical source coverage; not translated output",
                      "pages": sample(pages, args.count, args.cycle)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
