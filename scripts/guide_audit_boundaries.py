"""Exclude Wowhead's post-guide discussion from source-only prose audits.

This is an audit boundary, not a browser translation or DOM modification.
Exact heading matches avoid truncating real guide prose mentioning feedback.
"""

FOOTER_HEADINGS = frozenset(("feedback", "comments", "contribute"))


def is_discussion_heading(tag, value):
    """Match discussion boundaries without suppressing ordinary guide prose.

    Search-indexed Wowhead pages sometimes expose individual user comments
    directly as `Comment by <username>` headings, without a `Comments` header.
    Only heading tags qualify; quoted prose and in-guide examples remain.
    """
    if tag not in ("h2", "h3"):
        return False
    heading = " ".join(value.split()).casefold()
    return (heading in FOOTER_HEADINGS or
            (heading.startswith("comment by ") and len(heading) > len("comment by ")))


def trim_guide_footer(blocks):
    """Keep guide blocks before the first standalone discussion heading.

    Only section headings qualify; a sentence such as "Feedback on talents"
    remains guide content. Return a new list without mutating the extractor.
    """
    for index, (tag, value) in enumerate(blocks):
        if is_discussion_heading(tag, value):
            return list(blocks[:index])
    return list(blocks)
