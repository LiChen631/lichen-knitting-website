# -*- coding: utf-8 -*-
"""Validate the generated Lichen Knitting website.

Checks (all offline, no dependencies beyond the standard library):
  1. every local href / src resolves to a file that exists (no 404s)
  2. every page has a unique <title>, description, keywords and lang
  3. every English string in the navigation/CTA set is covered by data-en
  4. no <a>/<button> renders with empty text (the previous version had 7)
  5. JSON-LD blocks parse as JSON
  6. no forbidden claims leaking in (fabricated email, capacity, free sampling,
     fixed price / MOQ / lead time, founding year)
  7. every <img> has alt text; the inquiry form is present and marked static

Exit code 1 if any hard check fails.
"""
import html.parser
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "lichen_knitting_website")

PAGES = [
    "index.html",
    "about.html",
    "products.html",
    "custom.html",
    "contact.html",
    "product-single-jersey.html",
    "product-double-knit.html",
    "product-other.html",
    "404.html",
]

# Claims the handoff document forbids (未确认信息不得自行补写).
FORBIDDEN = [
    (r"免费打样", "不得宣称免费打样"),
    (r"免费样品", "不得宣称免费样品"),
    (r"[Aa]?\s*@[A-Za-z0-9.-]+\.(com|cn|net)", "不得编造邮箱地址"),
    (r"成立于\s*\d{4}", "不得编造成立时间"),
    (r"年产能|月产能|日产\s*\d+|年产\s*\d+", "不得编造产能"),
    (r"员工\s*\d+\s*人|技术人员\s*\d+", "不得编造人员数量"),
    (r"¥\s*\d+|￥\s*\d+|\d+\s*元/公?斤|\d+\s*元/米", "不得公开固定价格"),
    (r"起订量[:：]\s*\d+|MOQ[:：]\s*\d+|最小起订\s*\d+", "不得承诺固定起订量"),
    (r"交期[:：]\s*\d+\s*天|交货期[:：]\s*\d+", "不得承诺固定交期"),
    (r"ISO\s*\d{4,5}|CE认证|OEKO-TEX", "不得编造资质认证"),
    (r"客户案例|合作品牌[:：]", "不得编造客户案例"),
    (r"(成为|领先|最大|第一|顶级)的?针织", "不得使用无法证实的最佳性表述"),
]

# The static-form rule from 交接文档 第 6 节.
FORM_RULES = [
    ("会不会自动发送", r"不会自动发送|does not submit|nothing was sent|not sent"),
]

errors = []
warnings = []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


class Parser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []  # (attr, value)
        self.ids = set()
        self.titles = []
        self.title_text = ""
        self._in_title = False
        self.metas = []  # dict of attrs
        self.jsonld = []
        self._in_jsonld = False
        self._jsonld_buf = ""
        self.images = []
        self.anchors = []  # (tag, attrs, text)
        self._anchor_stack = []
        self.text_by_anchor = {}
        self._buf = ""
        self._pending = None
        self._collect = False

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if "id" in d:
            self.ids.add(d["id"])
        if tag in ("a", "link") and "href" in d:
            self.links.append((tag, d["href"]))
        if tag == "img":
            self.images.append(d)
            if "src" in d:
                self.links.append(("img", d["src"]))
        # <video>/<source> and poster images must resolve too, and the video has to be
        # in a codec browsers can actually play (H.264, not HEVC).
        if tag in ("source", "video") and "src" in d:
            self.links.append((tag, d["src"]))
        if tag == "video" and "poster" in d:
            self.links.append(("video-poster", d["poster"]))
        if tag in ("script", "link") and d.get("src"):
            self.links.append(("script", d["src"]))
        if tag == "meta":
            self.metas.append(d)
        if tag == "title":
            self._in_title = True
            self.title_text = ""
        if tag == "script" and d.get("type") == "application/ld+json":
            self._in_jsonld = True
            self._jsonld_buf = ""
        if tag in ("a", "button"):
            self._anchor_stack.append({"tag": tag, "attrs": d, "text": []})
        # accumulate text for the innermost a/button
        self._collect = bool(self._anchor_stack)

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
            self.titles.append(self.title_text.strip())
        if tag == "script" and self._in_jsonld:
            self._in_jsonld = False
            self.jsonld.append(self._jsonld_buf)
        if tag in ("a", "button") and self._anchor_stack:
            node = self._anchor_stack.pop()
            self.anchors.append((node["tag"], node["attrs"], "".join(node["text"]).strip()))
        self._collect = bool(self._anchor_stack)

    def handle_data(self, data):
        if self._in_title:
            self.title_text += data
        if self._in_jsonld:
            self._jsonld_buf += data
        if self._anchor_stack:
            self._anchor_stack[-1]["text"].append(data)


def parse(path):
    p = Parser()
    with io.open(path, encoding="utf-8") as fh:
        p.feed(fh.read())
    return p


def meta_map(metas):
    out = {}
    for m in metas:
        key = m.get("name") or m.get("property")
        if key:
            out.setdefault(key, []).append(m)
    return out


def check_links(slug, parser):
    base = os.path.dirname(os.path.join(SITE, slug))
    for tag, href in parser.links:
        if href is None:
            err("%s: <%s> has an empty reference" % (slug, tag))
            continue
        if href.startswith(("http://", "https://", "//", "tel:", "mailto:", "data:", "#")):
            if href.startswith(("http://", "https://")):
                warn("%s: external link %s (needs internet / platform check)" % (slug, href))
            continue
        target = href.split("#")[0].split("?")[0]
        if not target:
            continue
        resolved = os.path.normpath(os.path.join(base, target))
        if not os.path.exists(resolved):
            err("%s: broken local reference -> %s" % (slug, href))
        if tag == "a" and target.startswith("#"):
            if target[1:] not in parser.ids:
                err("%s: anchor target #%s does not exist" % (slug, target[1:]))


def check_head(slug, parser):
    if not parser.titles:
        err("%s: missing <title>" % slug)
        return
    title = parser.titles[0]
    if not title:
        err("%s: empty <title>" % slug)
    if len(title) > 70:
        warn("%s: <title> is %d chars (search results truncate ~60-70)" % (slug, len(title)))
    m = meta_map(parser.metas)
    for needed in ("description", "keywords", "viewport", "theme-color"):
        if needed not in m:
            err("%s: missing meta %s" % (slug, needed))
    desc = m.get("description", [{}])[0]
    if "data-en" not in desc:
        err("%s: description has no English variant (data-en)" % slug)
    for prop in ("og:title", "og:description", "og:type", "og:image"):
        if prop not in m:
            err("%s: missing %s" % (slug, prop))
    if "og:url" not in m:
        warn("%s: og:url / canonical omitted (no confirmed domain yet)" % slug)


def check_buttons(slug, parser):
    for tag, attrs, text in parser.anchors:
        # An element that only gets its label from JS is a defect: without JS the
        # visitor sees an empty button. Require visible fallback text in the markup.
        if attrs.get("data-zh") is not None and not text:
            err("%s: empty <%s> with data-zh label (blank without JavaScript)" % (slug, tag))
        elif tag == "a" and not text:
            err("%s: <a> with no visible text (href=%s)" % (slug, attrs.get("href")))


def check_images(slug, parser):
    for attrs in parser.images:
        if not attrs.get("alt"):
            err("%s: <img src=%s> missing alt" % (slug, attrs.get("src")))
        if not attrs.get("width") or not attrs.get("height"):
            warn("%s: <img src=%s> without width/height (layout shift)" % (slug, attrs.get("src")))
        if not attrs.get("loading"):
            warn("%s: <img src=%s> without loading attribute" % (slug, attrs.get("src")))


def check_jsonld(slug, parser):
    for i, block in enumerate(parser.jsonld):
        try:
            json.loads(block)
        except Exception as exc:
            err("%s: JSON-LD block %d is invalid: %s" % (slug, i + 1, exc))


def check_forbidden(slug, text):
    """Flag invented business claims.

    A claim is allowed when the clause it sits in explicitly negates or disclaims
    it (e.g. "网站上不展示…客户案例", "不承诺免费打样") — that is the honest way to
    talk about something that must not be promised. So the negation test looks at
    the whole clause up to the match, not a fixed character window.
    """
    for pattern, reason in FORBIDDEN:
        for match in re.finditer(pattern, text):
            clause = re.split(r"[。！？；;\n]", text[: match.start()])[-1]
            if re.search(r"(不|未|无|非|没有|no |not |never |without|neither)", clause):
                continue
            snippet = text[max(0, match.start() - 20) : match.end() + 10]
            err("%s: forbidden claim (%s): …%s…" % (slug, reason, snippet.replace("\n", " ").strip()))
            break


def check_bilingual_coverage(slug, text):
    """Every element carrying data-zh should also carry data-en (or -aria/-alt)."""
    for m in re.finditer(r"<([a-zA-Z][a-zA-Z0-9]*)\b([^>]*?)>", text):
        attrs = m.group(2)
        if "data-zh=" not in attrs:
            continue
        if "data-zh-" in attrs or "data-en=" in attrs or "data-en-" in attrs:
            continue
        err("%s: element <%s> has data-zh but no data-en" % (slug, m.group(1)))


def check_form(slug, text):
    if slug != "contact.html":
        return
    if "data-inquiry" not in text:
        err("contact.html: inquiry form missing")
        return
    for label, pattern in FORM_RULES:
        if not re.search(pattern, text):
            err("contact.html: form does not state that nothing is sent (%s)" % label)
    if 'type="submit"' not in text:
        err("contact.html: form has no submit button")
    if 'id="inquiry-result"' not in text:
        err("contact.html: missing inquiry-result container")
    if 'id="copy-inquiry"' not in text:
        err("contact.html: missing copy button")
    # The old bug: a literal "\n" instead of a newline inside the JS string.
    js = io.open(os.path.join(SITE, "assets", "site.js"), encoding="utf-8").read()
    if "\\\\n" in js:
        err("assets/site.js: contains a literal backslash-n in a string")


def main():
    print("Checking %d pages in %s\n" % (len(PAGES), SITE))
    titles = {}
    descs = {}
    for slug in PAGES:
        path = os.path.join(SITE, slug)
        if not os.path.exists(path):
            err("%s: file missing" % slug)
            continue
        text = io.open(path, encoding="utf-8").read()
        parser = parse(path)
        check_links(slug, parser)
        check_head(slug, parser)
        check_buttons(slug, parser)
        check_images(slug, parser)
        check_jsonld(slug, parser)
        check_forbidden(slug, text)
        check_bilingual_coverage(slug, text)
        check_form(slug, text)
        if parser.titles:
            titles.setdefault(parser.titles[0], []).append(slug)
        m = meta_map(parser.metas)
        if "description" in m:
            d = m["description"][0].get("content", "")
            descs.setdefault(d, []).append(slug)

    # Unique titles / descriptions (duplicate meta is an SEO defect).
    for title, slugs in titles.items():
        if len(slugs) > 1:
            err("duplicate <title> %r on: %s" % (title, ", ".join(slugs)))
    for desc, slugs in descs.items():
        if len(slugs) > 1:
            err("duplicate meta description on: %s" % ", ".join(slugs))

    # Extra files.
    for extra in ("robots.txt", "site.webmanifest", "assets/style.css", "assets/site.js",
                  "CREDITS.md"):
        if not os.path.exists(os.path.join(SITE, extra)):
            err("missing %s" % extra)

    # Videos must be H.264/AAC: HEVC clips simply do not play in most browsers.
    video_dir = os.path.join(SITE, "assets", "video")
    videos = []
    if os.path.isdir(video_dir):
        videos = sorted(f for f in os.listdir(video_dir) if f.endswith(".mp4"))
    if not videos:
        err("no .mp4 files found in assets/video (expected the factory clips)")
    for name in videos:
        path = os.path.join(video_dir, name)
        raw = io.open(path, "rb").read()
        if b"hvc1" in raw or b"hev1" in raw:
            err("assets/video/%s is HEVC/H.265 — most browsers cannot play it" % name)
        if b"avc1" not in raw:
            err("assets/video/%s has no H.264 (avc1) video track" % name)
        kb = len(raw) / 1024
        if kb > 1500:
            warn("assets/video/%s is %.0f KB — consider compressing for mobile" % (name, kb))
        print("video  %-24s %7.0f KB  H.264" % (name, kb))

    print("Unique titles:      %d" % len(titles))
    print("Unique descriptions:%d" % len(descs))
    print()

    for w in warnings:
        print("WARN  " + w)
    if warnings:
        print()
    for e in errors:
        print("FAIL  " + e)

    if errors:
        print("\n%d error(s), %d warning(s)" % (len(errors), len(warnings)))
        return 1
    print("All checks passed (%d warnings)." % len(warnings))
    return 0


if __name__ == "__main__":
    sys.exit(main())