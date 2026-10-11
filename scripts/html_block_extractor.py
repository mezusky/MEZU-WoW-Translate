"""Locale-neutral HTML block extraction for offline regression audits."""
from html.parser import HTMLParser
import re

class Extractor(HTMLParser):
    def __init__(self, tags, scoped):
        super().__init__(convert_charrefs=True)
        self.tags, self.scoped = set(tags), scoped
        self.scope = 0
        self.stack = []
        self.blocks = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self.skip += 1
            for _, parts in self.stack: parts.append(" ")
            return
        if self.skip:
            return
        if tag in ("main", "article"):
            self.scope += 1
        if tag in ("br", "p", "li", "ul", "ol", "div"):
            for _, parts in self.stack: parts.append(" ")
        if tag in self.tags and (self.scope or not self.scoped):
            self.stack.append([tag, []])

    def handle_data(self, data):
        if not self.skip:
            for _, parts in self.stack: parts.append(data)

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self.skip:
            self.skip -= 1
            return
        if self.skip:
            return
        if self.stack and self.stack[-1][0] == tag:
            kind, parts = self.stack.pop()
            value = re.sub(r"\s+", " ", "".join(parts)).strip()
            if value:
                self.blocks.append((kind, value))
        if tag in ("p", "li", "ul", "ol", "div"):
            for _, parts in self.stack: parts.append(" ")
        if tag in ("main", "article") and self.scope:
            self.scope -= 1

    def close(self):
        super().close()
        while self.stack:
            kind, parts = self.stack.pop()
            value = re.sub(r"\s+", " ", "".join(parts)).strip()
            if value:
                self.blocks.append((kind, value))

def extract_blocks(html, tags=("h1","h2","h3","h4","p","li","td","th"), scoped=False):
    parser = Extractor(tags, scoped)
    parser.feed(html)
    parser.close()
    return parser.blocks
