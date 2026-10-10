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

    def handle_starttag(self, tag, attrs):
        if tag in ("main", "article"):
            self.scope += 1
        if tag == "br" and self.stack:
            self.stack[-1][1].append(" ")
        if tag in self.tags and (self.scope or not self.scoped):
            if not self.stack or tag == "li":
                self.stack.append([tag, []])

    def handle_data(self, data):
        if self.stack:
            self.stack[-1][1].append(data)

    def handle_endtag(self, tag):
        if self.stack and self.stack[-1][0] == tag:
            kind, parts = self.stack.pop()
            value = re.sub(r"\s+", " ", "".join(parts)).strip()
            if value:
                self.blocks.append((kind, value))
        if tag in ("main", "article") and self.scope:
            self.scope -= 1

def extract_blocks(html, tags=("h1","h2","h3","h4","p","li","td","th"), scoped=False):
    parser = Extractor(tags, scoped)
    parser.feed(html)
    return parser.blocks
