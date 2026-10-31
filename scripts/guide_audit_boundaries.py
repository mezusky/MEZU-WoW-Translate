"""Exclude Wowhead's post-guide discussion from source-only prose audits.

This is an audit boundary, not a browser translation or DOM modification.
Exact heading matches avoid truncating real guide prose mentioning feedback.
"""

# Wowhead localizes its discussion UI even when guide prose stays English.
# These are site chrome markers, not translation glossary entries; they must
# be recognized regardless of the detected source or requested target locale.
# Keep the list conservative and grounded in observed Wowhead headings.
FOOTER_HEADINGS = frozenset((
    "feedback", "comments", "contribute",
    "commentaires", "kommentare", "comentarios", "comentários", "commenti",
    "評論", "评论", "contribuer",
))
COMMENT_AUTHOR_PREFIXES = (
    "comment by ", "commentaire de ", "kommentar von ",
    "comentario de ", "comentário de ",
)


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
            any(heading.startswith(prefix) and len(heading) > len(prefix)
                for prefix in COMMENT_AUTHOR_PREFIXES))


def trim_guide_footer(blocks):
    """Keep guide blocks before the first standalone discussion heading.

    Only section headings qualify; a sentence such as "Feedback on talents"
    remains guide content. Return a new list without mutating the extractor.
    """
    for index, (tag, value) in enumerate(blocks):
        if is_discussion_heading(tag, value):
            return list(blocks[:index])
    return list(blocks)
