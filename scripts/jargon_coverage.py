"""Reusable source-only terminology hit extraction for Wowhead audits.

This is diagnostic metadata, not the browser translation matcher. The glossary
remains data-only and locale-selected before this module is used.
"""
import re


class JargonCoverage:
    """Compile once per audit, favoring longer phrases over nested fragments."""

    def __init__(self, terms):
        if not isinstance(terms, dict):
            raise ValueError("Jargon terms must be an object")
        canonical = {}
        for source in terms:
            if not isinstance(source, str) or not source.strip():
                raise ValueError("Jargon source must be non-empty text")
            canonical.setdefault(source.casefold(), source)
        # Case variants are a single diagnostic concept; longer terms win.
        # Keep the stable source spelling from the data file for reporting.
        self._canonical = canonical
        spellings = sorted(canonical.values(), key=lambda s: (-len(s), s.casefold(), s))
        self._pattern = (re.compile(
            r"(?<!\w)(?:" + "|".join(re.escape(s) for s in spellings) + r")(?!\w)",
            re.IGNORECASE,
        ) if spellings else None)

    def hits(self, prose, limit=12):
        """Return distinct non-overlapping source phrases in reading order."""
        if not isinstance(prose, str) or not self._pattern or limit <= 0:
            return []
        seen, hits = set(), []
        for match in self._pattern.finditer(prose):
            identity = match.group(0).casefold()
            if identity not in seen:
                seen.add(identity)
                hits.append(self._canonical[identity])
                if len(hits) >= limit:
                    break
        return hits
