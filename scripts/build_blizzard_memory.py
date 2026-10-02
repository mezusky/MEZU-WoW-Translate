#!/usr/bin/env python3
"""Build an EN->frFR translation memory from paired official Blizzard WoW articles.

We discover recent /news/<id> pages from the English news index, fetch the same
article ID in en-us and fr-fr, align article blocks conservatively, and publish
only high-confidence exact sentence/block pairs. This layer is for prose and
patch-note wording; official spell/item names still come from Blizzard Game Data.
"""
import html
import json
import re
import time
import urllib.request
from difflib import SequenceMatcher
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "blizzard_translation_memory.json"
UA = "MEZU-WoW-Translate-DataBot/1.0 (+https://github.com/mezusky/MEZU-WoW-Translate)"
BASE = "https://worldofwarcraft.blizzard.com"
INDEX_PAGES = 6
MAX_ARTICLES = 60

# A few known high-value official articles are always included.
SEED_IDS = {
    "24245217",  # Midnight pre-expansion update
    "24066687",  # Hotfixes example with many class changes
}

NOISE = {
    "share","tweet","learn more","read more","world of warcraft","blizzard entertainment",
    "news","patch notes","hotfixes","back to top","previous article","next article",
}
NUM_RE = re.compile(r"\b\d+(?:[.,]\d+)?%?\b")
ID_RE = re.compile(r"/(?:en-us|fr-fr)/news/(\d+)")
WS_RE = re.compile(r"\s+")
SENT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-ZÀ-ÖØ-Þ0-9])")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.8"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode("utf-8", "replace")


class BlockParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_article = 0
        self.in_main = 0
        self.capture = None
        self.buf = []
        self.blocks = []

    def handle_starttag(self, tag, attrs):
        if tag == "article":
            self.in_article += 1
        if tag == "main":
            self.in_main += 1
        if tag in {"h1","h2","h3","h4","p","li"} and (self.in_article or self.in_main):
            self.capture = tag
            self.buf = []

    def handle_endtag(self, tag):
        if self.capture == tag:
            text = WS_RE.sub(" ", "".join(self.buf)).strip()
            if text:
                self.blocks.append((tag, text))
            self.capture = None
            self.buf = []
        if tag == "article" and self.in_article:
            self.in_article -= 1
        if tag == "main" and self.in_main:
            self.in_main -= 1

    def handle_data(self, data):
        if self.capture:
            self.buf.append(data)


def clean_blocks(raw_html):
    p = BlockParser()
    p.feed(raw_html)
    blocks = p.blocks

    # Fallback for pages whose body is not wrapped in <article>/<main>.
    if len(blocks) < 4:
        class AnyParser(HTMLParser):
            def __init__(self):
                super().__init__(convert_charrefs=True)
                self.capture = None
                self.buf = []
                self.blocks = []
            def handle_starttag(self, tag, attrs):
                if tag in {"h1","h2","h3","h4","p","li"}:
                    self.capture = tag
                    self.buf = []
            def handle_endtag(self, tag):
                if self.capture == tag:
                    t = WS_RE.sub(" ", "".join(self.buf)).strip()
                    if t: self.blocks.append((tag,t))
                    self.capture = None; self.buf=[]
            def handle_data(self, data):
                if self.capture: self.buf.append(data)
        q = AnyParser(); q.feed(raw_html); blocks = q.blocks

    out = []
    seen = set()
    for tag, text in blocks:
        text = html.unescape(text).replace("\u00a0", " ")
        text = WS_RE.sub(" ", text).strip()
        low = text.casefold().strip(" :.-")
        if len(text) < 8 or len(text) > 1200 or low in NOISE:
            continue
        if text in seen:
            continue
        seen.add(text)
        out.append((tag, text))
    return out


def structural_score(a, b):
    taga, ea = a
    tagb, fr = b
    score = 0.0
    if taga == tagb:
        score += 2.2
    na, nb = NUM_RE.findall(ea), NUM_RE.findall(fr)
    if na and na == nb:
        score += 4.0
    elif not na and not nb:
        score += 0.7
    elif set(na) & set(nb):
        score += 1.5

    la, lb = max(1,len(ea)), max(1,len(fr))
    ratio = min(la,lb)/max(la,lb)
    if ratio >= 0.75: score += 2.0
    elif ratio >= 0.55: score += 1.0
    elif ratio < 0.32: score -= 2.5

    if ea.count("%") == fr.count("%"): score += 0.5
    if ea.count(":") == fr.count(":"): score += 0.3
    if (taga.startswith("h") and tagb.startswith("h")): score += 0.8
    return score


def align_blocks(en_blocks, fr_blocks):
    # Dynamic-programming alignment with gaps; conservative acceptance later.
    n, m = len(en_blocks), len(fr_blocks)
    gap = -1.8
    dp = [[0.0]*(m+1) for _ in range(n+1)]
    bt = [[None]*(m+1) for _ in range(n+1)]
    for i in range(1,n+1):
        dp[i][0] = dp[i-1][0] + gap; bt[i][0] = "U"
    for j in range(1,m+1):
        dp[0][j] = dp[0][j-1] + gap; bt[0][j] = "L"
    for i in range(1,n+1):
        for j in range(1,m+1):
            diag = dp[i-1][j-1] + structural_score(en_blocks[i-1], fr_blocks[j-1])
            up = dp[i-1][j] + gap
            left = dp[i][j-1] + gap
            best = max(diag, up, left)
            dp[i][j] = best
            bt[i][j] = "D" if best == diag else ("U" if best == up else "L")
    pairs = []
    i,j=n,m
    while i or j:
        move = bt[i][j]
        if move == "D":
            pairs.append((en_blocks[i-1], fr_blocks[j-1], structural_score(en_blocks[i-1], fr_blocks[j-1])))
            i-=1; j-=1
        elif move == "U":
            i-=1
        else:
            j-=1
    pairs.reverse()
    return pairs


def sentences(text):
    parts = [x.strip() for x in SENT_RE.split(text) if x.strip()]
    return parts if parts else [text]


def good_pair(en, fr, score):
    if score < 4.0:
        return False
    if en.casefold() == fr.casefold():
        return False
    if len(en) < 12 or len(fr) < 12:
        return False
    if len(en) > 900 or len(fr) > 900:
        return False
    ratio = min(len(en),len(fr))/max(len(en),len(fr))
    if ratio < 0.34:
        return False
    # Avoid obvious nav/metadata.
    bad = ("cookie","privacy","facebook","twitter","instagram","youtube","copyright")
    low = (en+" "+fr).casefold()
    return not any(x in low for x in bad)


def discover_ids():
    ids = set(SEED_IDS)
    for page in range(1, INDEX_PAGES+1):
        urls = [
            f"{BASE}/en-us/news" if page == 1 else f"{BASE}/en-us/news?page={page}",
        ]
        for url in urls:
            try:
                raw = fetch(url)
                ids.update(ID_RE.findall(raw))
            except Exception as exc:
                print("WARN news index", url, exc)
        time.sleep(0.1)
    # Deterministic selection: always keep high-value seeds, then newest-looking
    # numeric article IDs. Set iteration order previously made the 60-article corpus
    # change randomly on every run, which caused the Data Pack to churn.
    seeds = sorted(SEED_IDS, key=lambda x: int(x), reverse=True)
    discovered = sorted((x for x in ids if x not in SEED_IDS), key=lambda x: int(x), reverse=True)
    return seeds + discovered[:max(0, MAX_ARTICLES - len(seeds))]


def main():
    memory = {}
    sources = {}
    article_stats = {}
    ids = discover_ids()
    print("Discovered", len(ids), "candidate Blizzard article IDs")

    for idx, article_id in enumerate(ids, 1):
        en_url = f"{BASE}/en-us/news/{article_id}"
        fr_url = f"{BASE}/fr-fr/news/{article_id}"
        try:
            en_html = fetch(en_url)
            fr_html = fetch(fr_url)
            en_blocks = clean_blocks(en_html)
            fr_blocks = clean_blocks(fr_html)
            if len(en_blocks) < 3 or len(fr_blocks) < 3:
                continue

            accepted = 0
            for (te,en),(tf,fr),score in align_blocks(en_blocks, fr_blocks):
                if not good_pair(en,fr,score):
                    continue

                # Whole-block memory.
                prev = memory.get(en)
                if prev is None:
                    memory[en] = fr
                    sources[en] = article_id
                    accepted += 1
                elif prev != fr:
                    memory.pop(en, None)
                    sources.pop(en, None)

                # Sentence memory when structure is one-to-one.
                es, fs = sentences(en), sentences(fr)
                if len(es) == len(fs) and 1 <= len(es) <= 8:
                    for e,f in zip(es,fs):
                        if good_pair(e,f,score):
                            prev = memory.get(e)
                            if prev is None:
                                memory[e] = f
                                sources[e] = article_id
                                accepted += 1
                            elif prev != f:
                                memory.pop(e, None)
                                sources.pop(e, None)

            if accepted:
                article_stats[article_id] = {
                    "accepted_pairs": accepted,
                    "en_blocks": len(en_blocks),
                    "fr_blocks": len(fr_blocks),
                    "en_url": en_url,
                    "fr_url": fr_url,
                }
            print(f"[{idx}/{len(ids)}] {article_id}: +{accepted}")
        except Exception as exc:
            print("WARN article", article_id, exc)
        time.sleep(0.08)

    payload = {
        "schema": 1,
        "source": "Official Blizzard World of Warcraft news",
        "pair_count": len(memory),
        "article_count": len(article_stats),
        "exact": dict(sorted(memory.items(), key=lambda kv: kv[0].casefold())),
        "sources": sources,
        "articles": article_stats,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print("Blizzard translation memory:", len(memory), "pairs from", len(article_stats), "paired articles")

if __name__ == "__main__":
    main()
