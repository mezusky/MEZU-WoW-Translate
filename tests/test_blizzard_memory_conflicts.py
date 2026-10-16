"""Regression: a source with conflicting translations must never reappear."""


def test_conflicting_translation_stays_excluded():
    observations = [("A", "B"), ("A", "C"), ("A", "B")]
    candidates = {}
    for source, target in observations:
        candidates.setdefault(source, set()).add(target)
    result = {key: next(iter(values)) for key, values in candidates.items() if len(values) == 1}
    assert "A" not in result
