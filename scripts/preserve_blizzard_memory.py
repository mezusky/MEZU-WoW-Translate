"""Merge verified Blizzard translations after a partial sync; quarantine conflicts."""
import json
import sys
from pathlib import Path

old_path, new_path = map(Path, sys.argv[1:3])
old = json.loads(old_path.read_text(encoding="utf-8"))
new = json.loads(new_path.read_text(encoding="utf-8"))
for key in ("sourceLanguage", "targetLanguage"):
    if old.get(key) and new.get(key) and old[key] != new[key]:
        raise SystemExit("Language mismatch: " + key)
blocked = set(old.get("ambiguous", [])) | set(new.get("ambiguous", []))
merged = dict(old.get("exact", {}))
for source, target in new.get("exact", {}).items():
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
