"""Regression corpus must not silently duplicate pages."""
import json
from pathlib import Path

pages = json.loads((Path(__file__).resolve().parents[1] / "data/wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]
assert len({page["id"] for page in pages}) == len(pages)
assert len({page["url"] for page in pages}) == len(pages)
