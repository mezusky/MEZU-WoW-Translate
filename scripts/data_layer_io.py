"""Fail closed when required, data-only translation sources are corrupt.

A missing/malformed glossary must not silently shrink a published Data Pack.
The previous remote pack remains available when the build fails.
"""
from pathlib import Path

try:
    from .locale_glossary import parse_json_unique_keys
except ImportError:  # Direct execution from scripts/
    from locale_glossary import parse_json_unique_keys


def load_required_layer(path):
    path = Path(path)
    try:
        payload = parse_json_unique_keys(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise ValueError(f"Invalid required translation layer {path.name}: {exc}") from exc
    if not isinstance(payload, dict) or not payload:
        raise ValueError(f"Required translation layer {path.name} must be a nonempty JSON object")
    return payload
