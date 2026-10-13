import json
from pathlib import Path

def test_localized_entities_have_canonical_ids():
    data = json.loads((Path(__file__).resolve().parents[1] / "data/datapack.json").read_text())
    for bucket in data["entities"].values():
        assert all(str(k).isdigit() and v.get("en") and v.get("fr") for k, v in bucket.items())
