"""Exclude Wowhead's post-guide discussion from source-only prose audits.

This is an audit boundary, not a browser translation or DOM modification.
Exact heading matches avoid truncating real guide prose mentioning feedback.
"""

FOOTER_HEADINGS = frozenset(("feedback", "comments", "contribute"))


def trim_guide_footer(blocks):
    """Keep guide blocks before the first standalone discussion heading.

    Only section headings qualify; a sentence such as "Feedback on talents"
    remains guide content. Return a new list without mutating the extractor.
    """
    for index, (tag, value) in enumerate(blocks):
        if tag in ("h2", "h3") and value.strip().casefold() in FOOTER_HEADINGS:
            return list(blocks[:index])
    return list(blocks)
