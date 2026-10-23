"""Classify Wowhead source access separately from translation quality.

Used by offline source audits only; GitHub Actions must not fetch Wowhead.
A blocked request never counts as a MEZU translation regression.
"""
from urllib.error import HTTPError


def classify_html_source(html):
    """Return (status, reason); a successful fetch may still be a JS challenge."""
    text = html.casefold()
    if "verify that you're not a robot" in text or (
        "javascript is disabled" in text and "enable javascript" in text
    ):
        return "blocked_challenge", "Wowhead JavaScript verification"
    if not html.strip():
        return "unscorable", "empty source response"
    return "accessible", None


def classify_fetch_error(exc):
    """Separate HTTP access restrictions from other network failures."""
    if isinstance(exc, HTTPError) and exc.code in (403, 429):
        return "blocked_http", f"HTTP {exc.code} (source access restricted)"
    return "fetch_error", str(exc)
