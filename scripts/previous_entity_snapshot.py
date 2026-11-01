"""Load the previous published entity snapshot without silent data loss.

Blizzard API refreshes may fail or return partial results. A damaged prior
snapshot must not be interpreted as an empty first-time build: that would
discard canonical IDs and their accumulated locale names.
"""
import hashlib
import json
from pathlib import Path

try:
    from .data_layer_io import load_required_layer
except ImportError:  # python scripts/build_datapack.py
    from data_layer_io import load_required_layer


def stable_pack_version(payload):
    """Hash the stable data, excluding only the two generated metadata fields.

    The builder and the snapshot validator must use the same version contract.
    A row name can be corrupted without changing any entity counts, so counts
    alone are not sufficient evidence of a trustworthy canonical snapshot.
    """
    stable = {key: value for key, value in payload.items()
              if key not in ("version", "generated_at")}
    encoded = json.dumps(stable, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:20]


def load_previous_entities(pack_path, manifest_path, source_language, target_language):
    pack_path, manifest_path = Path(pack_path), Path(manifest_path)
    if not pack_path.exists() and not manifest_path.exists():
        return {}  # Genuine first-time bootstrap only.
    if not pack_path.exists() or not manifest_path.exists():
        raise ValueError("Previous Data Pack and manifest must exist together")

    pack = load_required_layer(pack_path)
    manifest = load_required_layer(manifest_path)
    for key, expected in (("sourceLanguage", source_language),
                          ("targetLanguage", target_language)):
        if pack.get(key) != expected or manifest.get(key) != expected:
            raise ValueError(f"Previous Data Pack {key} does not match build locale")
    if not isinstance(pack.get("version"), str) or (
        pack["version"] != manifest.get("version")
    ):
        raise ValueError("Previous Data Pack version does not match manifest")
    if pack["version"] != stable_pack_version(pack):
        raise ValueError("Previous Data Pack content checksum does not match version")

    entities = pack.get("entities")
    if not isinstance(entities, dict) or not entities or any(
        not isinstance(kind, str) or not kind
        or not isinstance(rows, dict) for kind, rows in entities.items()
    ):
        raise ValueError("Previous Data Pack has invalid canonical entity categories")
    counts = {kind: len(rows) for kind, rows in sorted(entities.items())}
    if manifest.get("entity_count") != sum(counts.values()):
        raise ValueError("Previous Data Pack entity count does not match manifest")
    if (manifest.get("entity_counts_by_kind") is not None
            and manifest["entity_counts_by_kind"] != counts):
        raise ValueError("Previous Data Pack entity category counts do not match manifest")
    return entities
