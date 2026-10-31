"""Locale-neutral HTML block extraction for offline regression audits."""
from html.parser import HTMLParser
import re

# Inert and explicitly hidden subtrees are not visible guide prose.
# This is audit-only behavior, separate from the extension translation engine.
# Source-only prose audits must not train on executable macro snippets, import
# payloads or copy-button labels. This does not modify browser translation.
SKIP_TAGS = frozenset(("script", "style", "noscript", "template", "svg",
                       "pre", "code", "kbd", "samp", "textarea", "button"))
VOID_TAGS = frozenset(("area", "base", "br", "col", "embed", "hr", "img", "input",
                       "link", "meta", "param", "source", "track", "wbr"))
CSS_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
CSS_VALUE = re.compile(r"\s*([a-z-]+)\s*(!\s*important)?\s*$", re.IGNORECASE)


def normalize_block_text(parts):
    """Keep source line boundaries until non-prose macro filtering is done.

    A flat whitespace collapse turns `#showtooltip` and `/cast` into ordinary
    sentence fragments, defeating the line-anchored audit filters. Div-based
    macro lines need boundaries just as <br> lines do. The caller
    can flatten the cleaned prose later; this is not browser DOM behavior.
    """
    value = "".join(parts).replace("\r\n", "\n").replace("\r", "\n")
    value = re.sub(r"[^\S\n]+", " ", value)
    return re.sub(r" *\n+ *", "\n", value).strip()


def inline_style_hidden(style):
    """Resolve repeated inline declarations using CSS importance and source order.

    This does not attempt stylesheet/class resolution or browser layout.
    """
    effective = {}
    for declaration in CSS_COMMENT.sub("", style).split(";"):
        name, separator, value = declaration.partition(":")
        name = name.strip().lower()
        if not separator or name not in ("display", "visibility", "content-visibility"):
            continue
        match = CSS_VALUE.fullmatch(value)
        if not match:
            continue
        important = bool(match.group(2))
        previous = effective.get(name)
        if previous is None or important or not previous[1]:
            effective[name] = (match.group(1).lower(), important)
    return (effective.get("display", (None,))[0] == "none"
            or effective.get("visibility", (None,))[0] in ("hidden", "collapse")
            or effective.get("content-visibility", (None,))[0] == "hidden")


def is_hidden(attrs):
    """Honor explicit hidden attributes and effective inline CSS declarations."""
    attrs = dict(attrs)
    return "hidden" in attrs or inline_style_hidden(attrs.get("style") or "")


class Extractor(HTMLParser):
    def __init__(self, tags, scoped):
        super().__init__(convert_charrefs=True)
        self.tags, self.scoped = set(tags), scoped
        self.scope = 0
        self.stack = []
        self.blocks = []
        self.skipped_tags = []

    def handle_starttag(self, tag, attrs):
        if self.skipped_tags or tag in SKIP_TAGS or is_hidden(attrs):
            if not self.skipped_tags:
                for _, parts in self.stack:
                    parts.append(" ")
            if tag not in VOID_TAGS:
                self.skipped_tags.append(tag)
            return
        if tag in ("main", "article"):
            self.scope += 1
        if tag in ("br", "p", "li", "ul", "ol", "div"):
            for _, parts in self.stack:
                parts.append("\n" if tag in ("br", "div") else " ")
        if tag in self.tags and (self.scope or not self.scoped):
            self.stack.append([tag, []])

    def handle_data(self, data):
        if not self.skipped_tags:
            for _, parts in self.stack:
                parts.append(data)

    def handle_endtag(self, tag):
        if self.skipped_tags:
            if tag in self.skipped_tags:
                while self.skipped_tags:
                    if self.skipped_tags.pop() == tag:
                        break
            return
        if self.stack and self.stack[-1][0] == tag:
            kind, parts = self.stack.pop()
            value = normalize_block_text(parts)
            # A selected child (e.g. <p> inside <li> or <td>) is already
            # included in the selected ancestor's accumulated text. Emitting
            # both would double-count guide prose in source-only audits.
            if value and not self.stack:
                self.blocks.append((kind, value))
        if tag in ("p", "li", "ul", "ol", "div"):
            for _, parts in self.stack:
                parts.append(" ")
        if tag in ("main", "article") and self.scope:
            self.scope -= 1

    def close(self):
        super().close()
        while self.stack:
            kind, parts = self.stack.pop()
            value = normalize_block_text(parts)
            # A selected child (e.g. <p> inside <li> or <td>) is already
            # included in the selected ancestor's accumulated text. Emitting
            # both would double-count guide prose in source-only audits.
            if value and not self.stack:
                self.blocks.append((kind, value))


def extract_blocks(html, tags=("h1", "h2", "h3", "h4", "p", "li", "td", "th"), scoped=False):
    parser = Extractor(tags, scoped)
    parser.feed(html)
    parser.close()
    return parser.blocks


def extract_readable_blocks(html, tags=("h1", "h2", "h3", "h4", "p", "li", "td", "th"),
                            min_scoped_blocks=4):
    """Prefer article/main prose over site navigation for source-only audits.

    Some upstream pages have no semantic main/article wrapper; in those cases
    retain the original unscoped behavior instead of silently losing all text.
    This is not a browser DOM reconstruction or translation simulation.
    """
    scoped = extract_blocks(html, tags=tags, scoped=True)
    # A short but real article (for example a two-paragraph Blizzard notice)
    # must not fall back to global navigation/footer text just because it has
    # fewer than four blocks. Only heading-only wrappers remain eligible for
    # fallback: they can be empty page shells with the prose elsewhere.
    if len(scoped) >= min_scoped_blocks or any(
        tag in ("p", "li", "td", "th") for tag, _ in scoped
    ):
        return scoped
    return extract_blocks(html, tags=tags, scoped=False)
