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
        # Each semantic container remembers the selected-block depth at entry.
        # An unclosed paragraph must not absorb the following footer or sibling
        # article when its enclosing <main>/<article> ends.
        self.scope_frames = []
        self.stack = []
        self.blocks = []
        self.skipped_tags = []

    def handle_starttag(self, tag, attrs):
        # HTML implicitly closes an open <p> when another <p> begins. The
        # standard HTMLParser does not apply browser tree-repair rules, so
        # without this guard adjacent malformed paragraphs become one audit
        # block. Only close a topmost selected paragraph: a surrounding li/td
        # must retain its own text and continue to emit one parent block.
        # Paragraphs inside an already skipped subtree do not affect prose.
        # A newly hidden <p> still closes its visible predecessor in HTML.
        if (tag == "p" and self.stack and self.stack[-1][0] == "p"
                and not self.skipped_tags):
            self._finish_selected()
        if self.skipped_tags or tag in SKIP_TAGS or is_hidden(attrs):
            if not self.skipped_tags:
                for _, parts in self.stack:
                    parts.append(" ")
            if tag not in VOID_TAGS:
                self.skipped_tags.append(tag)
            return
        if tag in ("main", "article"):
            self.scope_frames.append((tag, len(self.stack)))
        if tag in ("br", "p", "li", "ul", "ol", "div"):
            for _, parts in self.stack:
                parts.append("\n" if tag in ("br", "div") else " ")
        if tag in self.tags and (self.scope_frames or not self.scoped):
            self.stack.append([tag, []])

    def _finish_selected(self):
        kind, parts = self.stack.pop()
        value = normalize_block_text(parts)
        # Nested selected blocks already contribute to their parent.
        if value and not self.stack:
            self.blocks.append((kind, value))
        return kind

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
        # HTML in guide widgets can close a selected parent while a selected
        # child remains unclosed (e.g. <li><p>text</li>). HTMLParser does not
        # auto-repair that nesting. Unwind through the matching ancestor so
        # the next list item/cell cannot be swallowed into the previous one.
        if any(kind == tag for kind, _ in self.stack):
            while self.stack:
                if self._finish_selected() == tag:
                    break
        if tag in ("p", "li", "ul", "ol", "div"):
            for _, parts in self.stack:
                parts.append(" ")
        if tag in ("main", "article"):
            # HTMLParser does not repair malformed markup. Close selected
            # descendants at their semantic container boundary, preserving
            # outer selected parents when <article> is nested in <main>.
            for index in range(len(self.scope_frames) - 1, -1, -1):
                if self.scope_frames[index][0] == tag:
                    depth = self.scope_frames[index][1]
                    while len(self.stack) > depth:
                        self._finish_selected()
                    del self.scope_frames[index:]
                    break

    def close(self):
        super().close()
        while self.stack:
            self._finish_selected()


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
