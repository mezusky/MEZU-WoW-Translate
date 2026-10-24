"""Locale-neutral HTML block extraction for offline regression audits."""
from html.parser import HTMLParser
import re

# Inert and explicitly hidden subtrees are not visible guide prose.
# This is audit-only behavior, separate from the extension translation engine.
SKIP_TAGS = frozenset(("script", "style", "noscript", "template", "svg"))
VOID_TAGS = frozenset(("area", "base", "br", "col", "embed", "hr", "img", "input",
                       "link", "meta", "param", "source", "track", "wbr"))
HIDDEN_STYLE = re.compile(
    r"(?:^|;)\s*(?:display\s*:\s*none|visibility\s*:\s*hidden)\s*"
    r"(?:!\s*important)?\s*(?:;|$)", re.IGNORECASE
)


def is_hidden(attrs):
    """Only honor HTML/CSS attributes that unambiguously hide an element."""
    attrs = dict(attrs)
    return "hidden" in attrs or bool(HIDDEN_STYLE.search(attrs.get("style") or ""))


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
                parts.append(" ")
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
            value = re.sub(r"\s+", " ", "".join(parts)).strip()
            if value:
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
            value = re.sub(r"\s+", " ", "".join(parts)).strip()
            if value:
                self.blocks.append((kind, value))


def extract_blocks(html, tags=("h1", "h2", "h3", "h4", "p", "li", "td", "th"), scoped=False):
    parser = Extractor(tags, scoped)
    parser.feed(html)
    parser.close()
    return parser.blocks
