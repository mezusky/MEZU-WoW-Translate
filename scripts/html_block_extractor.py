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
        # HTML permits omitted </li>. Track the containing list depth so a
        # sibling item closes the previous item without splitting nested lists.
        self.list_depth = 0
        self.li_depths = []
        # A missing </td> is legal HTML. Keep cell identity per table depth so
        # nested tables do not accidentally close their parent cell.
        self.table_depth = 0
        self.cell_depths = []

    def handle_starttag(self, tag, attrs):
        # Hidden cells may omit </td>; a sibling cell or new row ends them.
        # A nested table inside the hidden cell is not an outer sibling.
        if (tag in ("td", "th", "tr") and self.skipped_tags
                and self.skipped_tags[0] in ("td", "th")
                and "table" not in self.skipped_tags[1:]):
            self.skipped_tags.clear()
        # HTMLParser does not implement implicit cell closing. Finish the
        # previous cell before a sibling cell or a new row, including its
        # unclosed nested paragraphs, but never close an outer-table cell.
        if (tag in ("td", "th", "tr") and not self.skipped_tags
                and self.cell_depths
                and self.cell_depths[-1] == self.table_depth):
            while self.stack:
                if self._finish_selected() in ("td", "th"):
                    break
        # A hidden <li> can also omit its closing tag. HTML implicitly
        # closes it at the next sibling <li>, even with inline descendants.
        # Do not escape a hidden item while its nested list is still open.
        if (tag == "li" and self.skipped_tags
                and self.skipped_tags[0] == "li"
                and not any(t in ("ul", "ol") for t in self.skipped_tags[1:])):
            self.skipped_tags.clear()
        if (tag == "li" and not self.skipped_tags and self.li_depths
                and self.li_depths[-1] == self.list_depth):
            # A new sibling <li> implicitly ends the previous one. Unwind
            # nested selected paragraphs too; they belong to the old item.
            while self.stack:
                if self._finish_selected() == "li":
                    break
        # HTML implicitly closes <p> before a new paragraph OR a structural
        # block (heading/list/table). HTMLParser does not repair that tree:
        # without this guard, a guide introduction can swallow its priority
        # list, losing separate li/td evidence. Keep div out of this repair:
        # Wowhead macro widgets use div lines inside paragraph-like markup
        # and their line boundaries are preserved by the audit extractor.
        # A hidden block still closes the visible paragraph in HTML, but a
        # block inside an already skipped subtree cannot affect visible text.
        if (tag in ("p", "h1", "h2", "h3", "h4", "h5", "h6",
                    "ul", "ol", "table")
                and self.stack and self.stack[-1][0] == "p"
                and not self.skipped_tags):
            self._finish_selected()
        if self.skipped_tags or tag in SKIP_TAGS or is_hidden(attrs):
            if not self.skipped_tags:
                for _, parts in self.stack:
                    parts.append(" ")
            if tag not in VOID_TAGS:
                self.skipped_tags.append(tag)
            return
        if tag == "table":
            self.table_depth += 1
        if tag in ("main", "article"):
            self.scope_frames.append((tag, len(self.stack)))
        if tag in ("ul", "ol"):
            self.list_depth += 1
        # Headings embedded in priority cells/list items are block boundaries.
        # Without separators, e.g. "Runic Power<h4>Why 75?</h4>" becomes
        # "Runic PowerWhy 75?" in the source-only audit corpus.
        if tag in ("br", "p", "li", "ul", "ol", "div",
                   "h1", "h2", "h3", "h4", "h5", "h6"):
            for _, parts in self.stack:
                parts.append("\n" if tag in ("br", "div") else " ")
        if tag in self.tags and (self.scope_frames or not self.scoped):
            self.stack.append([tag, []])
            if tag == "li":
                self.li_depths.append(self.list_depth)
            if tag in ("td", "th"):
                self.cell_depths.append(self.table_depth)

    def _finish_selected(self):
        kind, parts = self.stack.pop()
        if kind == "li":
            self.li_depths.pop()
        if kind in ("td", "th"):
            self.cell_depths.pop()
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
        # A row/table boundary also closes a hidden final cell without an
        # explicit </td>, including cells containing unclosed inline markup.
        if (tag in ("tr", "table") and self.skipped_tags
                and self.skipped_tags[0] in ("td", "th")
                and "table" not in self.skipped_tags[1:]):
            self.skipped_tags.clear()
        # The parent list also implicitly ends an unclosed hidden final
        # item. Otherwise the skipped state leaks into following guide prose.
        if (tag in ("ul", "ol") and self.skipped_tags
                and self.skipped_tags[0] == "li"
                and not any(t in ("ul", "ol") for t in self.skipped_tags[1:])):
            self.skipped_tags.clear()
        if self.skipped_tags:
            if tag in self.skipped_tags:
                while self.skipped_tags:
                    if self.skipped_tags.pop() == tag:
                        break
            return
        # Finish an implicitly unclosed final cell at its own row/table end.
        # Depth tracking protects an outer cell that contains a nested table.
        if (tag in ("tr", "table") and self.cell_depths
                and self.cell_depths[-1] == self.table_depth):
            while self.stack:
                if self._finish_selected() in ("td", "th"):
                    break
        if tag == "table":
            self.table_depth = max(0, self.table_depth - 1)
        # HTML in guide widgets can close a selected parent while a selected
        # child remains unclosed (e.g. <li><p>text</li>). HTMLParser does not
        # auto-repair that nesting. Unwind through the matching ancestor so
        # the next list item/cell cannot be swallowed into the previous one.
        if any(kind == tag for kind, _ in self.stack):
            while self.stack:
                if self._finish_selected() == tag:
                    break
        if tag in ("ul", "ol"):
            # Closing a list implicitly closes its final unclosed item, but
            # leaves the enclosing parent item of a nested list intact.
            while (self.list_depth > 0 and self.li_depths
                   and self.li_depths[-1] >= self.list_depth):
                while self.stack:
                    if self._finish_selected() == "li":
                        break
            self.list_depth = max(0, self.list_depth - 1)
        if tag in ("p", "li", "ul", "ol", "div",
                   "h1", "h2", "h3", "h4", "h5", "h6"):
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
