"""Merge verified Blizzard translations after a partial sync; quarantine conflicts."""
import json
import sys
from pathlib import Path

# Reuse the same numeric-fact validator as the collector: a previously
# accepted but unsafe pair must not survive every future incremental sync.
from build_blizzard_memory import numeric_semantics_match

old_path, new_path = map(Path, sys.argv[1:3])
old = json.loads(old_path.read_text(encoding="utf-8"))
new = json.loads(new_path.read_text(encoding="utf-8"))
for key in ("sourceLanguage", "targetLanguage"):
    if old.get(key) and new.get(key) and old[key] != new[key]:
        raise SystemExit("Language mismatch: " + key)
    if old.get(key) and not new.get(key):
        new[key] = old[key]
source_locale = new.get("sourceLanguage") or old.get("sourceLanguage") or "en-US"
target_locale = new.get("targetLanguage") or old.get("targetLanguage") or "fr-FR"

def safe_pair(source, target):
    return numeric_semantics_match(source, target, source_locale, target_locale)

blocked = set(old.get("ambiguous", [])) | set(new.get("ambiguous", []))
merged = {
    source: target for source, target in old.get("exact", {}).items()
    if isinstance(source, str) and isinstance(target, str)
    and safe_pair(source, target)
}
for source, target in new.get("exact", {}).items():
    if not isinstance(source, str) or not isinstance(target, str):
        continue
    if not safe_pair(source, target):
        continue
    if source in merged and merged[source] != target:
        blocked.add(source)
    else:
        merged[source] = target
for source in blocked:
    merged.pop(source, None)
new["exact"] = dict(sorted(merged.items()))
new["pair_count"] = len(merged)
new["ambiguous"] = sorted(blocked)
new["sources"] = {**old.get("sources", {}), **new.get("sources", {})}
new["sources"] = {k: v for k, v in new["sources"].items() if k in merged}
new["articles"] = {**old.get("articles", {}), **new.get("articles", {})}
new["article_count"] = len(new["articles"])
new_path.write_text(json.dumps(new, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
