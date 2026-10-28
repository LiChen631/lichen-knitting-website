# -*- coding: utf-8 -*-
"""Generate the Lichen Knitting Factory static website.

The HTML in website/ is the deliverable; this script exists so that the shared
header / footer / <head> blocks can never drift apart between pages. Re-running it
regenerates every .html file from scratch, so hand edits to those files would be lost.

Content rules taken from the handoff document (项目交接文档 第 3–5 节):
  * Only confirmed business facts. No invented email, founding year, capacity,
    machine count, price, MOQ, lead time, free sampling or customer cases.
  * Product imagery is an illustration (示意图), never claimed to be a factory photo.
  * The inquiry form must never pretend to send or store anything.
"""
import html
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "lichen_knitting_website")

PHONE = "13210025853"
PHONE_TEL = "tel:13210025853"
AMAP = "https://surl.amap.com/GzwN9YCG7pf"

ADDR_ZH = "山东省青岛市即墨区通济街道办事处张家西城东村工业园即墨区利晨针织厂"
ADDR_EN = (
    "Jimo Lichen Knitting Factory, Zhangjia Xichengdong Village Industrial Park, "
    "Tongji Subdistrict, Jimo District, Qingdao, Shandong, China"
)
BRAND_ZH = "即墨区利晨针织厂"
BRAND_EN = "Jimo Lichen Knitting Factory"

TAGLINE_ZH = "针织面料定制与加工 · 欢迎国内外采购商联系"
TAGLINE_EN = "Knitted fabric customization & processing · Buyers worldwide welcome"

FOOTER_ZH = "专注针织面料定制与加工，支持来样、来图、成分及克重定制，灵活沟通订单需求。"
FOOTER_EN = (
    "Knitted fabric customization and processing, including sample-based, design-based, "
    "composition and weight customization."
)
LEGAL_ZH = "本网站信息以实际沟通确认为准。"
LEGAL_EN = "Website information is subject to confirmation through direct communication."

NAV = [
    ("index.html", "首页", "Home"),
    ("about.html", "关于我们", "About Us"),
    ("products.html", "产品中心", "Products"),
    ("custom.html", "定制服务", "Customization"),
    ("contact.html", "联系我们", "Contact"),
]


# --------------------------------------------------------------------------- helpers
def esc(value):
    return html.escape(str(value), quote=True)


def el(tag, zh, en=None, cls=None, attrs="", aria=None):
    """A bilingual leaf element: Chinese content in markup, English in data-en."""
    a = ""
    if cls:
        a += ' class="%s"' % cls
    if aria:
        a += ' data-zh-aria="%s" data-en-aria="%s"' % (esc(aria[0]), esc(aria[1]))
    a += attrs
    data_en = ' data-en="%s"' % esc(en) if en is not None else ""
    return "<%s%s data-zh=\"%s\"%s>%s</%s>" % (
        tag, a, esc(zh), data_en, esc(zh), tag)


def img(src, alt_zh, alt_en, width, height, eager=False, cls=None):
    a = ""
    if cls:
        a += ' class="%s"' % cls
    a += ' data-zh-alt="%s" data-en-alt="%s"' % (esc(alt_zh), esc(alt_en))
    return (
        '<img src="%s" alt="%s" width="%d" height="%d" %s decoding="async"%s>'
        % (
            src,
            esc(alt_zh),
            width,
            height,
            'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"',
            a,
        )
    )


# --------------------------------------------------------------------------- layout
def page_url(cfg):
    """Absolute URL for a page; the homepage canonicalises to the bare origin."""
    slug = cfg["slug"]
    if slug == "index.html":
        return URL_ORIGIN + "/"
    return URL_ORIGIN + "/" + slug


def head(cfg):
    title_zh = cfg["title_zh"]
    title_en = cfg["title_en"]
    desc_zh = cfg["desc_zh"]
    desc_en = cfg["desc_en"]
    key_zh = cfg["key_zh"]
    key_en = cfg["key_en"]

    # Social preview image: per-page where a meaningful photo exists, else the icon.
    rel_image = cfg.get("og_image", "assets/img/icon-512.png")
    og_image = URL_ORIGIN + "/" + rel_image if URL_ORIGIN else rel_image
    canonical_hint = page_url(cfg) if URL_ORIGIN else ""

    parts = [
        "<!doctype html>",
        '<html lang="zh-CN" data-title-en="%s">' % esc(title_en),
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        "<title>%s</title>" % esc(title_zh),
        '<meta name="description" content="%s" data-zh="%s" data-en="%s">'
        % (esc(desc_zh), esc(desc_zh), esc(desc_en)),
        '<meta name="keywords" content="%s" data-zh="%s" data-en="%s">'
        % (esc(key_zh), esc(key_zh), esc(key_en)),
        '<meta name="author" content="%s">' % esc(BRAND_ZH),
        '<meta name="robots" content="index,follow">',
        '<meta name="theme-color" content="#1456a0">',
        '<meta name="format-detection" content="telephone=no">'
        if False
        else '<meta name="format-detection" content="telephone=yes">',
        # Open Graph / social preview
        '<meta property="og:type" content="%s">' % cfg.get("og_type", "website"),
        '<meta property="og:site_name" content="%s">' % esc(BRAND_ZH),
        '<meta property="og:locale" content="zh_CN">',
        '<meta property="og:locale:alternate" content="en_US">',
        '<meta property="og:title" content="%s" data-zh="%s" data-en="%s">'
        % (esc(title_zh), esc(title_zh), esc(title_en)),
        '<meta property="og:description" content="%s" data-zh="%s" data-en="%s">'
        % (esc(desc_zh), esc(desc_zh), esc(desc_en)),
        '<meta property="og:image" content="%s">' % og_image,
        '<meta name="twitter:card" content="summary">',
        '<meta name="twitter:image" content="%s">' % og_image,
        '<meta name="twitter:title" content="%s" data-zh="%s" data-en="%s">'
        % (esc(title_zh), esc(title_zh), esc(title_en)),
        '<meta name="twitter:description" content="%s" data-zh="%s" data-en="%s">'
        % (esc(desc_zh), esc(desc_zh), esc(desc_en)),
        # Icons
        '<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">',
        '<link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">',
        '<link rel="manifest" href="site.webmanifest">',
    ]
    if canonical_hint:
        parts.append('<link rel="canonical" href="%s">' % esc(canonical_hint))
    if URL_ORIGIN:
        parts.insert(
            parts.index('<meta property="og:site_name" content="%s">' % esc(BRAND_ZH)) + 1,
            '<meta property="og:url" content="%s">' % esc(page_url(cfg)),
        )
    parts.append('<link rel="stylesheet" href="assets/style.css">')
    for block in cfg.get("jsonld", []):
        parts.append(
            '<script type="application/ld+json">%s</script>'
            % json.dumps(block, ensure_ascii=False, separators=(",", ":"))
        )
    parts.append('<script src="assets/site.js" defer></script>')
    parts.append("</head>")
    return "\n".join(parts)


def header_html(slug):
    nav_links = "".join(
        '<a href="%s" data-zh="%s" data-en="%s">%s</a>' % (href, esc(zh), esc(en), esc(zh))
        for href, zh, en in NAV
    )
    return """<body>
<a class="skip-link" href="#main" data-zh="跳到主要内容" data-en="Skip to main content">跳到主要内容</a>
<div class="topline"><div class="wrap"><span data-zh="%s" data-en="%s">%s</span><span><span data-zh="电话 / 微信：" data-en="Phone / WeChat: ">电话 / 微信：</span><a href="%s">%s</a></span></div></div>
<header class="site-header"><div class="wrap nav">
<a class="brand" href="index.html"><span class="brand-mark" aria-hidden="true">利</span><span class="brand-text"><span class="brand-name">%s</span><span class="brand-sub">JIMO LICHEN KNITTING FACTORY</span></span></a>
<button class="menu-btn" type="button" data-zh-aria="打开导航" data-en-aria="Open navigation" aria-label="打开导航">☰</button>
<nav class="navlinks" aria-label="%s">
%s
</nav><div class="nav-actions"><button class="lang" type="button" aria-label="Switch to English" aria-pressed="false">EN</button><a class="btn" href="contact.html" data-zh="立即询价" data-en="Request a Quote">立即询价</a></div>
</div></header>""" % (
        esc(TAGLINE_ZH),
        esc(TAGLINE_EN),
        esc(TAGLINE_ZH),
        PHONE_TEL,
        PHONE,
        esc(BRAND_ZH),
        "主导航" if slug != "contact" else "主导航",
        nav_links,
    )


def breadcrumbs(crumbs, current_zh, current_en):
    """crumbs: list of (href, zh, en) for the ancestors."""
    chunks = []
    for i, (href, zh, en) in enumerate(crumbs):
        chunks.append(
            '<a href="%s" data-zh="%s" data-en="%s">%s</a>' % (href, esc(zh), esc(en), esc(zh))
        )
        chunks.append('<span aria-hidden="true">/</span>')
    chunks.append(
        '<span aria-current="page" data-zh="%s" data-en="%s">%s</span>'
        % (esc(current_zh), esc(current_en), esc(current_zh))
    )
    return (
        '<nav class="breadcrumbs" data-zh-aria="面包屑导航" data-en-aria="Breadcrumb">%s</nav>'
        % " ".join(chunks)
    )


def footer_html():
    return """<footer class="footer"><div class="wrap"><div class="footer-grid">
<div><div class="brand" style="color:white;margin-bottom:14px"><span class="brand-mark">利</span><span class="brand-text"><span class="brand-name" style="color:white">%s</span><span class="brand-sub" style="color:#b9d0ec">JIMO LICHEN KNITTING FACTORY</span></span></div><p data-zh="%s" data-en="%s">%s</p></div>
<div><h3 data-zh="快速导航" data-en="Quick Links">快速导航</h3><div class="footer-links"><a href="about.html" data-zh="关于我们" data-en="About Us">关于我们</a><a href="products.html" data-zh="产品中心" data-en="Products">产品中心</a><a href="custom.html" data-zh="定制服务" data-en="Customization">定制服务</a><a href="contact.html" data-zh="联系我们" data-en="Contact">联系我们</a></div></div>
<div><h3 data-zh="联系我们" data-en="Contact">联系我们</h3><div class="footer-links"><a href="%s">%s</a><span data-zh="%s" data-en="%s">%s</span><a href="%s" target="_blank" rel="noopener" data-zh="高德地图导航 ↗" data-en="Amap Directions ↗">高德地图导航 ↗</a></div></div>
</div><div class="copyright">© <span id="year">2026</span> %s · <span data-zh="%s" data-en="%s">%s</span></div></div></footer>
</body></html>""" % (
        esc(BRAND_ZH),
        esc(FOOTER_ZH),
        esc(FOOTER_EN),
        esc(FOOTER_ZH),
        PHONE_TEL,
        PHONE,
        esc(ADDR_ZH),
        esc(ADDR_EN),
        esc(ADDR_ZH),
        AMAP,
        esc(BRAND_ZH),
        esc(LEGAL_ZH),
        esc(LEGAL_EN),
        esc(LEGAL_ZH),
    )


def page(cfg):
    body = "\n".join(
        [
            head(cfg),
            header_html(cfg["slug"]),
            '<main id="main">',
            cfg["body"],
            "</main>",
            footer_html(),
        ]
    )
    return body


# --------------------------------------------------------------------------- site config
# The production origin is NOT hard-coded: no domain has been purchased or confirmed
# yet (see handoff document §7 第六步). Put the final URL in site.config.json via
# tools/set_domain.py and canonical links, og:url and sitemap.xml are generated.
CONFIG_PATH = os.path.join(ROOT, "site.config.json")


def load_origin():
    try:
        with io.open(CONFIG_PATH, encoding="utf-8") as fh:
            return str(json.load(fh).get("origin", "")).rstrip("/")
    except Exception:
        return ""


URL_ORIGIN = load_origin()


def org_jsonld():
    data = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "@id": "#organization",
        "name": BRAND_ZH,
        "alternateName": BRAND_EN,
        "description": (
            "即墨区利晨针织厂位于山东省青岛市即墨区，拥有自有生产车间和针织设备，"
            "提供平纹、双面及其他针织面料的来样、来图定制与加工服务，支持打样及灵活订单。"
        ),
        "telephone": "+86-13210025853",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "通济街道办事处张家西城东村工业园",
            "addressLocality": "青岛市即墨区",
            "addressRegion": "山东省",
            "addressCountry": "CN",
        },
        "areaServed": [{"@type": "Country", "name": "中国"}, {"@type": "Place", "name": "海外采购商"}],
        "knowsLanguage": ["zh-CN", "en"],
        "image": "assets/img/icon-512.png",
    }
    if URL_ORIGIN:
        data["url"] = URL_ORIGIN
    return data


def bc_jsonld(crumbs, current_name):
    items = []
    for i, (href, zh, en) in enumerate(crumbs, start=1):
        item = {"@type": "ListItem", "position": i, "name": zh}
        if URL_ORIGIN:
            item["item"] = URL_ORIGIN + "/" + href
        items.append(item)
    items.append({"@type": "ListItem", "position": len(items) + 1, "name": current_name})
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}


FAQ = [
    (
        "是否支持来样、来图定制？",
        "支持。您可以提供实物样品或清晰的产品图片作为沟通依据，工厂据此沟通面料组织、成分、克重与规格。",
        "Do you support sample-based or design-based customization?",
        "Yes. You can share a physical sample or clear product images as a reference, and the factory will discuss the knit structure, composition, weight and specifications accordingly.",
    ),
    (
        "起订量（MOQ）是多少？",
        "起订量需要按面料规格、颜色数量与工厂当期生产排期沟通确认。网站不公布固定起订量，以免与实际条件不符。",
        "What is the minimum order quantity?",
        "MOQ is confirmed according to fabric specifications, colour quantities and the factory's current production schedule. No fixed MOQ is published, to avoid quoting conditions that may not apply.",
    ),
    (
        "打样怎么安排？需要收费吗？",
        "支持打样。打样的时间、费用与具体安排需要提前沟通确认，网站不做“免费打样”的承诺。",
        "How is sampling handled? Is it free?",
        "Sampling is available. Timing, cost and the exact arrangement are agreed in advance; the website does not promise free sampling.",
    ),
    (
        "交货周期一般多久？",
        "交期根据订单规格、数量与当期生产排期确认，具体以沟通结果为准，网站不承诺固定交期。",
        "What is the lead time?",
        "Lead time is confirmed according to specifications, quantity and the current production schedule. No fixed lead time is promised.",
    ),
    (
        "可以定制哪些参数？",
        "可以沟通来样、来图、指定面料规格、成分与克重、颜色与规格等内容，具体可行的范围以沟通确认为准。",
        "Which parameters can be customized?",
        "Sample-based and design-based work, specified fabric specifications, composition and weight, colour and other requirements can be discussed; the feasible scope is confirmed during discussion.",
    ),
    (
        "如何获得报价？",
        "网站不公开固定价格。请提供产品类别、用途、成分/克重/规格、颜色与预计数量，工厂会据此沟通报价。",
        "How do I get a quotation?",
        "No fixed prices are listed. Please provide the product category, intended use, composition, weight, specifications, colours and estimated quantity, and a quotation will be discussed accordingly.",
    ),
    (
        "是否对接海外采购商？",
        "工厂面向国内外采购商，可以用中文或英文沟通。贸易方式与物流安排请在联系时具体确认。",
        "Do you work with overseas buyers?",
        "The factory serves both domestic and overseas buyers and can communicate in Chinese or English. Trade terms and logistics are confirmed at the time of contact.",
    ),
]


def faq_section():
    items = []
    for q_zh, a_zh, q_en, a_en in FAQ:
        items.append(
            '<details><summary data-zh="%s" data-en="%s">%s</summary>'
            '<p class="faq-a" data-zh="%s" data-en="%s">%s</p></details>'
            % (esc(q_zh), esc(q_en), esc(q_zh), esc(a_zh), esc(a_en), esc(a_zh))
        )
    return (
        '<section class="band" id="faq"><div class="wrap">'
        '<div class="section-head"><div><div class="kicker" data-zh="常见问题" data-en="FAQ">常见问题</div>'
        '<h2 data-zh="采购商常问的问题" data-en="Questions Buyers Often Ask">采购商常问的问题</h2>'
        '<p data-zh="以下回答以工厂可确认的口径为准；未明确的条件请在联系时具体沟通。'
        '" data-en="These answers reflect what the factory can confirm. Anything not stated here is agreed at the time of contact.">'
        "以下回答以工厂可确认的口径为准；未明确的条件请在联系时具体沟通。</p></div></div>"
        '<div class="faq">%s</div></div></section>' % "".join(items)
    )


def faq_jsonld():
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q_zh,
                "acceptedAnswer": {"@type": "Answer", "text": a_zh},
            }
            for q_zh, a_zh, _q_en, _a_en in FAQ
        ],
    }


MACHINES = [
    ("双面机", "Double Knit Machines", ["34×24", "34×28", "38×24", "38×28"]),
    (
        "单面机",
        "Single Jersey Machines",
        ["30×24", "30×28", "34×24", "34×28", "34×32", "38×28", "38×30", "38×32"],
    ),
    ("毛巾机", "Terry Machine", ["34×19"]),
]


def machine_list():
    cards = []
    for zh, en, models in MACHINES:
        tags = "".join('<span class="tag">%s</span>' % m for m in models)
        cards.append(
            '<div class="machine"><h3 data-zh="%s" data-en="%s">%s</h3>'
            '<div class="tags">%s</div></div>' % (esc(zh), esc(en), esc(zh), tags)
        )
    return '<div class="machine-list">%s</div>' % "".join(cards)


PRODUCT_CATEGORIES = [
    (
        "product-single-jersey.html",
        "平纹针织面料",
        "Single Jersey Knit",
        "assets/img/fabric-single-jersey.jpg",
        "平纹针织面料示意（面料纹理照片）",
        "Single jersey knit fabric, illustrative texture photo",
        "适用范围与具体规格可按客户用途沟通。",
        "Discuss end use and specifications based on your application.",
    ),
    (
        "product-double-knit.html",
        "双面针织面料",
        "Double Knit Fabric",
        "assets/img/fabric-double-knit.jpg",
        "双面针织提花面料示意（面料纹理照片）",
        "Double knit jacquard fabric, illustrative texture photo",
        "可沟通不同组织、成分、克重及颜色需求。",
        "Discuss knit structure, composition, weight and colors.",
    ),
    (
        "product-other.html",
        "其他针织面料",
        "Other Knitted Fabrics",
        "assets/img/fabric-other.jpg",
        "其他针织面料示意（针织绒面料纹理照片）",
        "Other knitted fabric, illustrative fleece texture photo",
        "根据样品、图片或产品用途沟通定制方案。",
        "Discuss custom options based on samples, designs or intended use.",
    ),
]


def product_cards(with_button=True):
    cards = []
    for i, (href, zh, en, src, alt_zh, alt_en, p_zh, p_en) in enumerate(
            PRODUCT_CATEGORIES, start=1):
        img_html = img(src, alt_zh, alt_en, 900, 675)
        btn = (
            '<a class="btn secondary" href="%s" data-zh="产品详情 →" data-en="Product Details →">产品详情 →</a>'
            % href
            if with_button
            else '<a class="text-link" href="%s" data-zh="了解详情 →" data-en="View Details →">了解详情 →</a>'
            % href
        )
        cards.append(
            '<article class="card"><div class="card-img">%s</div><div class="card-body">'
            '<div class="kicker">0%d</div><h3 data-zh="%s" data-en="%s">%s</h3>'
            '<p data-zh="%s" data-en="%s">%s</p>%s</div></article>'
            % (img_html, i, esc(zh), esc(en), esc(zh), esc(p_zh), esc(p_en), esc(p_zh), btn)
        )
    return '<div class="grid-3">%s</div>' % "".join(cards)


def cta_section(heading_zh="告诉我们您的面料需求", heading_en="Tell Us About Your Fabric Needs"):
    return (
        '<section><div class="wrap map-panel"><div>'
        f'<h2 data-zh="{heading_zh}" data-en="{heading_en}">{heading_zh}</h2>'
        '<p data-zh="准备好产品类别、预计数量、成分/克重/规格与颜色要求后，可通过电话或微信直接联系工厂。" '
        'data-en="Once you have the product category, estimated quantity, composition, weight, specifications and colours ready, contact the factory directly by phone or WeChat.">'
        "准备好产品类别、预计数量、成分/克重/规格与颜色要求后，可通过电话或微信直接联系工厂。</p>"
        f'<p><strong data-zh="电话 / 微信：{PHONE}" data-en="Phone / WeChat: {PHONE}">电话 / 微信：{PHONE}</strong></p>'
        "</div>"
        '<a class="btn" href="contact.html" data-zh="前往询价 →" data-en="Request a Quote →">前往询价 →</a>'
        "</div></section>"
    )


def contact_strip():
    """Prominent phone / WeChat / address block. Shown right under the homepage hero."""
    return f"""<section class="contact-strip" id="contact"><div class="wrap">
<div class="cs-item"><small data-zh="电话 / 微信" data-en="Phone / WeChat">电话 / 微信</small>
<div class="wechat-line"><a class="cs-phone" href="{PHONE_TEL}">{PHONE}</a><button class="copy-btn" type="button" data-copy="{PHONE}" data-zh="复制微信号" data-en="Copy WeChat ID">复制微信号</button></div></div>
<div class="cs-item"><small data-zh="工厂地址" data-en="Factory Address">工厂地址</small>
<span class="cs-addr" data-zh="{esc(ADDR_ZH)}" data-en="{esc(ADDR_EN)}">{esc(ADDR_ZH)}</span></div>
<div class="cs-actions"><a class="btn" href="{PHONE_TEL}" data-zh="立即拨打 →" data-en="Call Now →">立即拨打 →</a><a class="btn ghost" href="{AMAP}" target="_blank" rel="noopener" data-zh="高德导航 ↗" data-en="Amap Directions ↗">高德导航 ↗</a></div>
</div></section>"""


def workshop_video(src, poster, note_zh, note_en, label_zh, label_en):
    return (
        f'<div class="video-frame"><video controls playsinline preload="none" '
        f'poster="{poster}" data-zh-aria="{esc(label_zh)}" data-en-aria="{esc(label_en)}" '
        f'aria-label="{esc(label_zh)}">'
        f'<source src="{src}" type="video/mp4">'
        f'<p data-zh="{esc(note_zh)}" data-en="{esc(note_en)}">{esc(note_zh)}</p>'
        "</video></div>"
        f'<p class="video-note" data-zh="{esc(note_zh)}" data-en="{esc(note_en)}">{esc(note_zh)}</p>'
    )


# =================================================================== index.html
# The homepage is deliberately short: hero -> contact strip -> three product
# categories -> one workshop video block -> three entry links. Everything detailed
# (equipment list, process, FAQ, quotes) lives on its own page and is reached by a
# normal page jump, not by scrolling.
INDEX_BODY = f"""<section class="hero"><div class="wrap hero-grid"><div>
<div class="eyebrow" data-zh="针织面料 · 定制加工" data-en="KNITTED FABRICS · CUSTOM PROCESSING">针织面料 · 定制加工</div>
<h1 data-zh="以织造经验，承接每一份定制需求" data-en="Knitting Experience for Your Custom Fabric Needs">以织造经验，承接每一份定制需求</h1>
<p data-zh="即墨区利晨针织厂拥有自有生产车间与针织设备，提供平纹、双面及其他针织面料的定制与加工。支持来样、来图、成分及克重定制，并可沟通打样。" data-en="Jimo Lichen Knitting Factory operates its own workshop and knitting equipment, offering customized single jersey, double-knit and other knitted fabrics. Sample-based, design-based, composition and fabric-weight customization are available, with sampling by arrangement.">即墨区利晨针织厂拥有自有生产车间与针织设备，提供平纹、双面及其他针织面料的定制与加工。支持来样、来图、成分及克重定制，并可沟通打样。</p>
<div class="hero-buttons"><a class="btn light" href="tel:{PHONE}" data-zh="立即电话咨询 →" data-en="Call Us Now →">立即电话咨询 →</a><a class="btn secondary" href="products.html" data-zh="查看产品类别" data-en="Explore Products">查看产品类别</a></div>
</div><div class="hero-media">{img("assets/img/factory-5.jpg", "即墨区利晨针织厂车间内的针织大圆机（工厂实拍）", "Circular knitting machine inside the Jimo Lichen Knitting Factory workshop (factory photo)", 1600, 900, eager=True)}
<div class="image-note" data-zh="车间实拍 · 针织大圆机" data-en="Workshop photo · circular knitting machine">车间实拍 · 针织大圆机</div></div></div></section>
{contact_strip()}
<section><div class="wrap"><div class="section-head"><div>
<div class="kicker" data-zh="产品类别" data-en="PRODUCT CATEGORIES">产品类别</div>
<h2 data-zh="针织面料，按需求定制" data-en="Knitted Fabrics Made to Your Requirements">针织面料，按需求定制</h2>
<p data-zh="面料成分、克重、颜色、规格及订单数量可根据需求沟通确认，不预设统一价格。" data-en="Composition, weight, color, specifications and quantity are discussed for each inquiry. Pricing is quoted according to requirements.">面料成分、克重、颜色、规格及订单数量可根据需求沟通确认，不预设统一价格。</p>
</div><a class="btn secondary" href="products.html" data-zh="全部产品 →" data-en="All Products →">全部产品 →</a></div>
{product_cards(with_button=False)}
<p class="hint" style="margin-top:18px" data-zh="面料图片为示意图，用于说明面料类别，不是本厂特定批次的实拍；具体成分、克重与颜色按订单沟通确认。" data-en="Fabric images are illustrative and show the fabric category; they are not photographs of a specific production batch. Composition, weight and colours are confirmed per order.">面料图片为示意图，用于说明面料类别，不是本厂特定批次的实拍；具体成分、克重与颜色按订单沟通确认。</p>
</div></section>
<section class="band"><div class="wrap split"><div>{workshop_video(
    "assets/video/yarn-creel.mp4",
    "assets/img/poster-yarn-creel.jpg",
    "设备运转实拍（由工厂拍摄提供）",
    "Video of the machines in operation, filmed at the factory",
    "工厂车间设备运转实拍视频",
    "Video of knitting machines running in the factory",
)}
</div><div class="copy"><div class="kicker" data-zh="工厂实拍" data-en="IN THE WORKSHOP">工厂实拍</div>
<h2 data-zh="自有车间与设备，灵活响应订单" data-en="In-house Workshop, Flexible Production">自有车间与设备，灵活响应订单</h2>
<p data-zh="工厂位于山东省青岛市即墨区通济街道办事处张家西城东村工业园，拥有自有生产车间和针织设备，在各类针织面料织造方面具备经验。具体交期、起订量和生产安排以沟通确认为准。" data-en="Located in Zhangjia Xichengdong Village Industrial Park, Tongji Subdistrict, Jimo District, Qingdao, Shandong, China, the factory has its own workshop and knitting equipment, with experience across knitted fabric types. Lead time, minimum order quantity and production scheduling are confirmed case by case.">工厂位于山东省青岛市即墨区通济街道办事处张家西城东村工业园，拥有自有生产车间和针织设备，在各类针织面料织造方面具备经验。具体交期、起订量和生产安排以沟通确认为准。</p>
<ul class="checklist"><li data-zh="来样定制、来图定制" data-en="Sample-based and design-based customization">来样定制、来图定制</li><li data-zh="成分、克重、颜色与规格定制" data-en="Composition, weight, color and specification customization">成分、克重、颜色与规格定制</li><li data-zh="支持打样，小批量与大批量需求均可沟通" data-en="Sampling available; discuss small and large orders">支持打样，小批量与大批量需求均可沟通</li></ul>
<a class="btn" href="about.html" data-zh="查看工厂详情 →" data-en="About the Factory →">查看工厂详情 →</a></div></div></section>
<section><div class="wrap"><div class="section-head"><div>
<div class="kicker" data-zh="继续了解" data-en="MORE">继续了解</div>
<h2 data-zh="按需要进入对应页面" data-en="Go Straight to What You Need">按需要进入对应页面</h2>
</div></div><div class="entry-grid">
<a class="entry" href="about.html"><h3 data-zh="关于我们" data-en="About Us">关于我们</h3><p data-zh="工厂情况、生产设备与针织机型清单。" data-en="The factory, its equipment and the knitting machine model list.">工厂情况、生产设备与针织机型清单。</p><span class="more" data-zh="进入关于我们 →" data-en="Go to About Us →">进入关于我们 →</span></a>
<a class="entry" href="custom.html"><h3 data-zh="定制服务" data-en="Customization">定制服务</h3><p data-zh="来样来图、成分克重、打样流程与询价准备。" data-en="Sample and design based work, composition and weight, sampling process and what to prepare.">来样来图、成分克重、打样流程与询价准备。</p><span class="more" data-zh="进入定制服务 →" data-en="Go to Customization →">进入定制服务 →</span></a>
<a class="entry" href="contact.html"><h3 data-zh="联系我们" data-en="Contact">联系我们</h3><p data-zh="地址地图、联系方式与询价内容整理表单。" data-en="Address and map, contact details and the inquiry helper form.">地址地图、联系方式与询价内容整理表单。</p><span class="more" data-zh="进入联系我们 →" data-en="Go to Contact →">进入联系我们 →</span></a>
</div></div></section>"""

INDEX = {
    "slug": "index.html",
    "title_zh": "即墨区利晨针织厂｜针织面料定制与加工",
    "title_en": "Jimo Lichen Knitting Factory | Custom Knitted Fabric Manufacturer, Qingdao",
    "desc_zh": "即墨区利晨针织厂位于山东省青岛市即墨区，拥有自有生产车间和针织设备，提供平纹、双面及其他针织面料的来样、来图定制与加工服务，支持打样及灵活订单。",
    "desc_en": "Jimo Lichen Knitting Factory in Qingdao, Shandong, China offers custom single jersey, double-knit and other knitted fabrics, with in-house equipment, sample-based and design-based customization, and sampling by arrangement.",
    "key_zh": "即墨区利晨针织厂,针织面料,针织面料定制,针织加工,来样定制,来图定制,青岛针织厂,即墨针织厂",
    "key_en": "Jimo Lichen Knitting Factory, knitted fabric, custom knitted fabric, knitted fabric manufacturer, sample-based fabric customization, custom knitting, Qingdao knitting factory",
    "og_type": "website",
    "og_image": "assets/img/factory-5.jpg",
    "body": INDEX_BODY,
    "jsonld": [org_jsonld()],
}

# =================================================================== about.html
ABOUT_CRUMBS = [("index.html", "首页", "Home")]
ABOUT_BODY = f"""<section class="page-hero"><div class="wrap">{breadcrumbs(ABOUT_CRUMBS, "关于我们", "About Us")}
<div class="eyebrow" data-zh="关于利晨" data-en="ABOUT LICHEN">关于利晨</div>
<h1 data-zh="专注针织面料织造与定制服务" data-en="Focused on Knitted Fabric Production & Customization">专注针织面料织造与定制服务</h1>
<p data-zh="以客户需求为导向，围绕面料类型、成分、克重、颜色与规格开展沟通和定制。" data-en="Customer-focused discussion and customization around fabric type, composition, weight, color and specifications.">以客户需求为导向，围绕面料类型、成分、克重、颜色与规格开展沟通和定制。</p>
</div></section>
<section><div class="wrap split"><div class="copy">
<div class="kicker" data-zh="工厂简介" data-en="FACTORY PROFILE">工厂简介</div>
<h2 data-zh="自有生产车间，灵活承接定制需求" data-en="An In-house Workshop for Flexible Custom Orders">自有生产车间，灵活承接定制需求</h2>
<p data-zh="即墨区利晨针织厂位于山东省青岛市即墨区通济街道办事处张家西城东村工业园。工厂拥有自有生产车间和针织设备，在各类针织面料织造方面具备经验，主要提供针织面料定制与加工服务。" data-en="Jimo Lichen Knitting Factory is located in Zhangjia Xichengdong Village Industrial Park, Tongji Subdistrict, Jimo District, Qingdao, Shandong, China. The factory has its own workshop and knitting equipment, with experience in knitted fabric production, and focuses on custom fabric manufacturing and processing.">即墨区利晨针织厂位于山东省青岛市即墨区通济街道办事处张家西城东村工业园。工厂拥有自有生产车间和针织设备，在各类针织面料织造方面具备经验，主要提供针织面料定制与加工服务。</p>
<p data-zh="可根据客户样品、图片及实际用途沟通面料方案。打样要求、起订量和交货周期均根据产品规格、订单数量与生产排期确认。" data-en="Fabric options can be discussed based on customer samples, images and intended use. Sampling, minimum order quantities and lead times are confirmed according to specifications, order volume and production schedule.">可根据客户样品、图片及实际用途沟通面料方案。打样要求、起订量和交货周期均根据产品规格、订单数量与生产排期确认。</p>
<a class="btn" href="custom.html" data-zh="查看定制服务 →" data-en="See Customization →">查看定制服务 →</a>
</div><figure class="split-img" style="margin:0">{img("assets/img/factory-8.jpg", "即墨区利晨针织厂车间内的双面针织大圆机（工厂实拍）", "Double knit circular knitting machine in the Jimo Lichen Knitting Factory workshop (factory photo)", 1600, 900)}
<figcaption class="photo-caption"><strong data-zh="车间实拍" data-en="Workshop photo">车间实拍</strong><span data-zh="双面针织大圆机 · 由工厂拍摄提供" data-en="Double knit circular machine · filmed at the factory">双面针织大圆机 · 由工厂拍摄提供</span></figcaption>
</figure></div></section>
<section class="band"><div class="wrap split"><div>{workshop_video(
    "assets/video/machine-fabric.mp4",
    "assets/img/poster-machine-fabric.jpg",
    "织造过程实拍（由工厂拍摄提供）",
    "Video of the knitting process, filmed at the factory",
    "织造过程实拍视频",
    "Video of the knitting process in the factory",
)}
</div><div class="copy"><div class="kicker" data-zh="生产现场" data-en="ON THE FLOOR">生产现场</div>
<h2 data-zh="设备与车间，真实可见" data-en="Real Machines, Real Workshop">设备与车间，真实可见</h2>
<p data-zh="以上照片与视频均由工厂实地拍摄，展示自有生产车间与针织设备的实际运行情况。设备数量、产能等信息暂未在网站上公布，如需了解请直接联系沟通。" data-en="The photos and video above were filmed at the factory and show the actual workshop and knitting equipment in operation. Equipment counts and capacity are not published here; please contact us directly for details.">以上照片与视频均由工厂实地拍摄，展示自有生产车间与针织设备的实际运行情况。设备数量、产能等信息暂未在网站上公布，如需了解请直接联系沟通。</p>
<ul class="checklist"><li data-zh="自有生产车间，设备自主安排" data-en="Own workshop, production scheduled in-house">自有生产车间，设备自主安排</li><li data-zh="针织大圆机现场织造" data-en="Knitting carried out on circular machines on site">针织大圆机现场织造</li><li data-zh="欢迎联系确认具体工艺与排期" data-en="Contact us to confirm processes and scheduling">欢迎联系确认具体工艺与排期</li></ul>
<a class="btn" href="contact.html" data-zh="联系工厂 →" data-en="Contact the Factory →">联系工厂 →</a></div></div></section>
<section class="band"><div class="wrap"><div class="section-head"><div>
<div class="kicker" data-zh="设备信息" data-en="EQUIPMENT">设备信息</div>
<h2 data-zh="工厂提供的针织机型" data-en="Knitting Machine Models">工厂提供的针织机型</h2>
<p data-zh="仅展示已提供的机型，不虚构设备数量、产能或未确认的技术参数。" data-en="Only provided machine models are listed. Equipment counts, capacity and unconfirmed technical details are not invented.">仅展示已提供的机型，不虚构设备数量、产能或未确认的技术参数。</p>
</div></div>{machine_list()}</div></section>
<section><div class="wrap"><div class="section-head"><div>
<div class="kicker" data-zh="合作特点" data-en="WHY WORK WITH US">合作特点</div>
<h2 data-zh="围绕订单需求灵活沟通" data-en="Flexible Communication Around Your Order">围绕订单需求灵活沟通</h2>
</div></div><div class="grid-3">
<div class="card"><div class="card-body"><h3 data-zh="来样 / 来图定制" data-en="Sample / Design Based">来样 / 来图定制</h3><p data-zh="支持以客户提供的样品或图片作为沟通依据。" data-en="Discuss requirements using customer samples or design images.">支持以客户提供的样品或图片作为沟通依据。</p></div></div>
<div class="card"><div class="card-body"><h3 data-zh="成分与克重定制" data-en="Composition & Weight">成分与克重定制</h3><p data-zh="根据面料用途沟通成分、克重、颜色和规格。" data-en="Discuss composition, weight, color and specifications for the intended use.">根据面料用途沟通成分、克重、颜色和规格。</p></div></div>
<div class="card"><div class="card-body"><h3 data-zh="灵活订单安排" data-en="Flexible Order Planning">灵活订单安排</h3><p data-zh="小批量与大批量需求均可联系沟通，具体条件以确认结果为准。" data-en="Discuss both small and large orders; terms are confirmed case by case.">小批量与大批量需求均可联系沟通，具体条件以确认结果为准。</p></div></div>
</div></div></section>
<section class="band"><div class="wrap"><div class="info-box"><h2 style="margin:0 0 10px" data-zh="关于本网站的信息口径" data-en="About the Information on This Website">关于本网站的信息口径</h2>
<p data-zh="网站上不展示固定价格、起订量、交期、产能、设备数量、成立时间与客户案例等信息，因为这些内容需以实际沟通确认为准。已公开的内容来自工厂提供并确认的资料。" data-en="Fixed prices, minimum order quantities, lead times, capacity, machine counts, founding date and customer cases are not published on this website because they are confirmed through direct communication. Published content reflects information supplied and confirmed by the factory.">网站上不展示固定价格、起订量、交期、产能、设备数量、成立时间与客户案例等信息，因为这些内容需以实际沟通确认为准。已公开的内容来自工厂提供并确认的资料。</p></div></div></section>
{cta_section()}"""

ABOUT = {
    "slug": "about.html",
    "title_zh": "关于我们｜即墨区利晨针织厂 · 青岛针织面料工厂",
    "title_en": "About Us | Jimo Lichen Knitting Factory, Qingdao",
    "desc_zh": "即墨区利晨针织厂是位于青岛即墨的小型针织面料工厂，自有生产车间及双面机、单面机、毛巾机，主营针织面料定制代工，支持来样、来图与打样沟通。",
    "desc_en": "Jimo Lichen Knitting Factory is a small knitted fabric manufacturer in Jimo, Qingdao, with its own workshop and double knit, single jersey and terry machines, focused on custom fabric production and sampling by arrangement.",
    "key_zh": "即墨区利晨针织厂,青岛针织厂,即墨针织厂,针织面料工厂,针织代工,针织面料定制,来样定制",
    "key_en": "Jimo Lichen Knitting Factory, Qingdao knitting factory, knitted fabric manufacturer China, custom knit fabric supplier, knitting mill Shandong",
    "og_type": "website",
    "og_image": "assets/img/factory-8.jpg",
    "body": ABOUT_BODY,
    "jsonld": [bc_jsonld(ABOUT_CRUMBS, "关于我们"), org_jsonld()],
}

# =================================================================== products.html
PRODUCTS_CRUMBS = [("index.html", "首页", "Home")]

SPEC_ROWS = [
    (
        "单面 / 平纹组织",
        "Single jersey / plain structure",
        "平纹针织面料",
        "Single Jersey Knit",
        "可按客户用途沟通面料组织、成分与克重。",
        "Discuss knit structure, composition and weight for the intended use.",
    ),
    (
        "双面组织",
        "Double-knit structure",
        "双面针织面料",
        "Double Knit Fabric",
        "可沟通不同组织、成分、克重与颜色需求。",
        "Discuss knit structure, composition, weight and colors.",
    ),
    (
        "其他针织 / 毛巾组织",
        "Other knit / terry structures",
        "其他针织面料",
        "Other Knitted Fabrics",
        "根据样品、图片或产品用途沟通可行的定制方向。",
        "Discuss feasible customization based on samples, images or intended use.",
    ),
]


def spec_table():
    rows = []
    for i, (zh, en, cat_zh, cat_en, note_zh, note_en) in enumerate(SPEC_ROWS, start=1):
        rows.append(
            "<tr>"
            '<th scope="row">%d</th>'
            '<td data-zh="%s" data-en="%s">%s</td>'
            '<td data-zh="%s" data-en="%s">%s</td>'
            '<td data-zh="%s" data-en="%s">%s</td>'
            "</tr>"
            % (
                i,
                esc(zh),
                esc(en),
                esc(zh),
                esc(cat_zh),
                esc(cat_en),
                esc(cat_zh),
                esc(note_zh),
                esc(note_en),
                esc(note_zh),
            )
        )
    return (
        '<div class="table-scroll"><table class="spec-table">'
        '<caption class="sr-only" data-zh="针织面料类别对照" data-en="Knitted fabric category reference">针织面料类别对照</caption>'
        "<thead><tr>"
        '<th scope="col">#</th>'
        '<th scope="col" data-zh="面料组织方向" data-en="Structure direction">面料组织方向</th>'
        '<th scope="col" data-zh="对应产品类别" data-en="Product category">对应产品类别</th>'
        '<th scope="col" data-zh="可沟通内容" data-en="What can be discussed">可沟通内容</th>'
        "</tr></thead><tbody>%s</tbody></table></div>" % "".join(rows)
    )


PRODUCTS_BODY = f"""<section class="page-hero"><div class="wrap">{breadcrumbs(PRODUCTS_CRUMBS, "产品中心", "Products")}
<div class="eyebrow" data-zh="产品中心" data-en="PRODUCTS">产品中心</div>
<h1 data-zh="针织面料产品类别" data-en="Knitted Fabric Categories">针织面料产品类别</h1>
<p data-zh="产品图片为通用面料纹理示意图，非本厂实拍。具体成分、克重、颜色、规格和适用范围请通过电话或微信沟通。" data-en="Images are generic fabric texture illustrations, not actual factory photos. Please contact us to discuss composition, weight, color, specifications and applications.">产品图片为通用面料纹理示意图，非本厂实拍。具体成分、克重、颜色、规格和适用范围请通过电话或微信沟通。</p>
</div></section>
<section><div class="wrap">{product_cards()}
<div class="notice" style="margin-top:28px" data-zh="本网站不展示固定价格。面料报价、起订量、打样安排与交期需根据具体规格、订单数量和生产排期确认。" data-en="No fixed prices are listed. Quotes, minimum order quantities, sampling and lead times are confirmed based on specifications, quantity and production schedule.">本网站不展示固定价格。面料报价、起订量、打样安排与交期需根据具体规格、订单数量和生产排期确认。</div>
</div></section>
<section class="band"><div class="wrap"><div class="section-head"><div>
<div class="kicker" data-zh="类别对照" data-en="CATEGORY REFERENCE">类别对照</div>
<h2 data-zh="三类针织面料的沟通口径" data-en="How the Three Categories Differ">三类针织面料的沟通口径</h2>
<p data-zh="下表只说明可沟通的定制方向，不代表固定规格或固定用途；具体参数以沟通确认为准。" data-en="The table only describes the directions that can be discussed. It does not state fixed specifications or end uses; parameters are confirmed during discussion.">下表只说明可沟通的定制方向，不代表固定规格或固定用途；具体参数以沟通确认为准。</p>
</div></div>{spec_table()}</div></section>
<section><div class="wrap"><div class="section-head"><div>
<div class="kicker" data-zh="选择方向" data-en="HOW TO CHOOSE">选择方向</div>
<h2 data-zh="不确定该选哪一类？" data-en="Not Sure Which Category Fits?">不确定该选哪一类？</h2>
<p data-zh="最直接的方式是提供样品或图片，并说明用途与大致的数量，工厂会据此沟通可行方向。" data-en="The most direct approach is to share a sample or image, describe the intended use and an approximate quantity; feasible directions can then be discussed.">最直接的方式是提供样品或图片，并说明用途与大致的数量，工厂会据此沟通可行方向。</p>
</div><a class="btn" href="custom.html" data-zh="查看定制服务 →" data-en="See Customization →">查看定制服务 →</a></div></div></section>
{cta_section()}"""

PRODUCTS = {
    "slug": "products.html",
    "title_zh": "产品中心｜平纹·双面·其他针织面料 - 即墨区利晨针织厂",
    "title_en": "Products | Single Jersey, Double Knit & Other Knitted Fabrics - Jimo Lichen",
    "desc_zh": "即墨区利晨针织厂产品类别：平纹针织面料、双面针织面料与其他针织面料。支持来样、来图、成分与克重定制，不公开固定价格，按需求沟通报价与打样。",
    "desc_en": "Product categories: single jersey, double knit and other knitted fabrics. Sample-based, design-based, composition and weight customization; no fixed prices, quotes and sampling discussed per inquiry.",
    "key_zh": "针织面料产品,平纹针织面料,双面针织面料,针织面料类别,针织面料加工,针织面料定制,即墨区利晨针织厂",
    "key_en": "single jersey fabric, double knit fabric, terry fabric, custom knitted fabric categories, knitted fabric China supplier",
    "og_type": "website",
    "og_image": "assets/img/fabric-double-knit.jpg",
    "body": PRODUCTS_BODY,
    "jsonld": [bc_jsonld(PRODUCTS_CRUMBS, "产品中心"), org_jsonld()],
}

# =================================================================== custom.html
CUSTOM_CRUMBS = [("index.html", "首页", "Home")]
CUSTOM_BODY = f"""<section class="page-hero"><div class="wrap">{breadcrumbs(CUSTOM_CRUMBS, "定制服务", "Customization")}
<div class="eyebrow" data-zh="定制服务" data-en="CUSTOMIZATION">定制服务</div>
<h1 data-zh="按样品、图片与实际用途沟通面料方案" data-en="Fabric Solutions Based on Samples, Designs & Applications">按样品、图片与实际用途沟通面料方案</h1>
<p data-zh="支持来样定制、来图定制、指定面料规格、成分与克重定制，以及颜色和规格定制。" data-en="Customization is available based on samples, designs, requested specifications, composition, weight, colors and other requirements.">支持来样定制、来图定制、指定面料规格、成分与克重定制，以及颜色和规格定制。</p>
</div></section>
<section><div class="wrap"><div class="section-head"><div>
<div class="kicker" data-zh="定制范围" data-en="CUSTOMIZATION OPTIONS">定制范围</div>
<h2 data-zh="可沟通的定制项目" data-en="What We Can Discuss">可沟通的定制项目</h2>
</div></div><div class="grid-3">
<div class="card"><div class="card-body"><h3 data-zh="来样 / 来图" data-en="Samples / Designs">来样 / 来图</h3><p data-zh="根据实物样品或图片沟通面料效果与规格。" data-en="Discuss fabric appearance and specifications based on a physical sample or image.">根据实物样品或图片沟通面料效果与规格。</p></div></div>
<div class="card"><div class="card-body"><h3 data-zh="成分与克重" data-en="Composition & Weight">成分与克重</h3><p data-zh="根据产品用途沟通目标成分、克重及相关要求。" data-en="Discuss target composition, weight and related requirements for the intended use.">根据产品用途沟通目标成分、克重及相关要求。</p></div></div>
<div class="card"><div class="card-body"><h3 data-zh="颜色与规格" data-en="Color & Specifications">颜色与规格</h3><p data-zh="按订单需求确认颜色、规格及其他面料要求。" data-en="Confirm colors, specifications and other fabric requirements for each order.">按订单需求确认颜色、规格及其他面料要求。</p></div></div>
</div></div></section>
<section class="band"><div class="wrap"><div class="section-head"><div>
<div class="kicker" data-zh="合作流程" data-en="PROCESS">合作流程</div>
<h2 data-zh="清晰沟通每个关键环节" data-en="A Clear Process for Each Order">清晰沟通每个关键环节</h2>
</div></div><div class="steps">
<div class="step"><h3 data-zh="沟通需求" data-en="Discuss Requirements">沟通需求</h3><p data-zh="确认面料类型、用途、成分、克重、颜色与数量。" data-en="Confirm fabric type, application, composition, weight, color and quantity.">确认面料类型、用途、成分、克重、颜色与数量。</p></div>
<div class="step"><h3 data-zh="提供样品 / 图片" data-en="Share Sample / Image">提供样品 / 图片</h3><p data-zh="客户提供参考样品或图片，双方确认定制目标。" data-en="Share a reference sample or image and align on the target.">客户提供参考样品或图片，双方确认定制目标。</p></div>
<div class="step"><h3 data-zh="打样与确认" data-en="Sampling & Confirmation">打样与确认</h3><p data-zh="打样要求及相关安排需事先沟通，样品由客户确认。" data-en="Sampling requirements and arrangements are agreed in advance, followed by customer approval.">打样要求及相关安排需事先沟通，样品由客户确认。</p></div>
<div class="step"><h3 data-zh="确认订单并生产" data-en="Confirm Order & Produce">确认订单并生产</h3><p data-zh="订单细节确认后，结合生产排期安排生产。" data-en="Production is scheduled after order details are confirmed.">订单细节确认后，结合生产排期安排生产。</p></div>
</div>
<div class="notice" style="margin-top:22px" data-zh="起订量、交货周期及打样要求均需根据产品规格、订单数量与工厂排期沟通确认；网站不承诺未确认的免费打样或固定交期。" data-en="Minimum order quantities, lead times and sampling terms are confirmed case by case. No unconfirmed free sampling or fixed lead time is promised.">起订量、交货周期及打样要求均需根据产品规格、订单数量与工厂排期沟通确认；网站不承诺未确认的免费打样或固定交期。</div>
</div></section>
<section><div class="wrap"><div class="section-head"><div>
<div class="kicker" data-zh="询价准备" data-en="BEFORE YOU ASK">询价准备</div>
<h2 data-zh="带上这些信息，沟通会更快" data-en="Bring These Details for a Faster Discussion">带上这些信息，沟通会更快</h2>
<p data-zh="信息越具体，工厂越容易判断可行方向并给出对应报价。" data-en="The more specific the information, the easier it is to assess feasible directions and quote accordingly.">信息越具体，工厂越容易判断可行方向并给出对应报价。</p>
</div></div><div class="grid-2">
<div class="info-box"><h3 style="margin:0 0 8px" data-zh="必填信息" data-en="Essential">必填信息</h3><ul class="checklist" style="margin:8px 0 0"><li data-zh="产品类别（平纹 / 双面 / 其他）" data-en="Product category (single jersey / double knit / other)">产品类别（平纹 / 双面 / 其他）</li><li data-zh="用途或成品类型" data-en="Intended use or finished product type">用途或成品类型</li><li data-zh="预计数量" data-en="Estimated quantity">预计数量</li><li data-zh="联系电话或微信" data-en="Phone number or WeChat">联系电话或微信</li></ul></div>
<div class="info-box"><h3 style="margin:0 0 8px" data-zh="有帮助的补充信息" data-en="Helpful extras">有帮助的补充信息</h3><ul class="checklist" style="margin:8px 0 0"><li data-zh="成分与克重要求" data-en="Composition and weight requirements">成分与克重要求</li><li data-zh="颜色要求或色卡" data-en="Color requirements or a color card">颜色要求或色卡</li><li data-zh="样布、图片或实物样品" data-en="A swatch, image or physical sample">样布、图片或实物样品</li><li data-zh="目标价格区间与交期预期" data-en="Target price range and expected lead time">目标价格区间与交期预期</li></ul></div>
</div></div></section>
{faq_section()}
{cta_section("准备好需求后，直接联系工厂", "Contact the Factory Once Your Requirements Are Ready")}"""

CUSTOM = {
    "slug": "custom.html",
    "title_zh": "定制服务｜来样·来图·成分克重定制 - 即墨区利晨针织厂",
    "title_en": "Customization | Sample-Based, Design-Based Fabric Customization - Jimo Lichen",
    "desc_zh": "即墨区利晨针织厂提供针织面料来样定制、来图定制、指定规格、成分与克重、颜色与规格定制，支持打样。起订量、报价与交期按实际需求沟通确认。",
    "desc_en": "Custom knitted fabric service: sample-based and design-based customization, specified composition, weight, color and specifications, with sampling by arrangement. MOQ, pricing and lead time confirmed per inquiry.",
    "key_zh": "针织面料定制,来样定制,来图定制,克重定制,成分定制,针织打样,针织加工,即墨区利晨针织厂",
    "key_en": "custom knitted fabric, sample-based fabric customization, design-based fabric customization, fabric weight customization, knitting sampling, knit fabric processing China",
    "og_type": "website",
    "og_image": "assets/img/fabric-single-jersey.jpg",
    "body": CUSTOM_BODY,
    "jsonld": [bc_jsonld(CUSTOM_CRUMBS, "定制服务"), faq_jsonld(), org_jsonld()],
}

# =================================================================== contact.html
CONTACT_CRUMBS = [("index.html", "首页", "Home")]

PRODUCT_OPTIONS = [
    ("平纹针织面料", "单面 / 平纹针织面料", "Single Jersey Knit"),
    ("双面针织面料", "双面针织面料", "Double Knit Fabric"),
    ("其他针织面料", "其他针织面料", "Other Knitted Fabric"),
    ("暂不确定", "暂不确定，需要沟通", "Not sure yet"),
]


def product_select():
    opts = []
    for value, zh, en in PRODUCT_OPTIONS:
        opts.append(
            '<option value="%s" data-zh="%s" data-en="%s">%s</option>'
            % (esc(value), esc(zh), esc(en), esc(zh))
        )
    return '<select id="product" name="product">%s</select>' % "".join(opts)


CONTACT_BODY = f"""<section class="page-hero"><div class="wrap">{breadcrumbs(CONTACT_CRUMBS, "联系我们", "Contact")}
<div class="eyebrow" data-zh="联系我们" data-en="CONTACT US">联系我们</div>
<h1 data-zh="欢迎沟通针织面料需求" data-en="Let's Discuss Your Knitted Fabric Needs">欢迎沟通针织面料需求</h1>
<p data-zh="请通过电话或微信联系。网站询价表单仅用于整理需求，不会自动向后台发送或保存客户信息。" data-en="Contact us by phone or WeChat. This static inquiry form helps organize your requirements but does not automatically send or store customer information.">请通过电话或微信联系。网站询价表单仅用于整理需求，不会自动向后台发送或保存客户信息。</p>
</div></section>
<section><div class="wrap contact-grid"><div class="contact-card">
<div class="kicker" data-zh="联系信息" data-en="CONTACT DETAILS">联系信息</div>
<h2 style="margin:0 0 10px" data-zh="即墨区利晨针织厂" data-en="Jimo Lichen Knitting Factory">即墨区利晨针织厂</h2>
<div class="contact-item"><small data-zh="电话 / 微信" data-en="Phone / WeChat">电话 / 微信</small><strong><a href="{PHONE_TEL}">{PHONE}</a></strong><p class="hint" data-zh="可直接拨打电话，或通过微信联系。" data-en="Call directly or contact us on WeChat.">可直接拨打电话，或通过微信联系。</p></div>
<div class="contact-item"><small data-zh="工厂地址" data-en="Factory Address">工厂地址</small><strong data-zh="{esc(ADDR_ZH)}" data-en="{esc(ADDR_EN)}">{esc(ADDR_ZH)}</strong></div>
<div class="contact-item"><small data-zh="联系时间" data-en="Contact Availability">联系时间</small><strong data-zh="全天可留言" data-en="Messages welcome at any time">全天可留言</strong><p class="hint" data-zh="此信息表示可随时留言，不代表全天人工在线。" data-en="Messages can be left at any time; this does not imply 24-hour live staffing.">此信息表示可随时留言，不代表全天人工在线。</p></div>
<div class="contact-item"><small data-zh="语言" data-en="Languages">语言</small><strong data-zh="中文 / English" data-en="Chinese / English">中文 / English</strong></div>
<a class="btn" href="{AMAP}" target="_blank" rel="noopener" data-zh="高德地图导航 ↗" data-en="Amap Directions ↗">高德地图导航 ↗</a>
</div>
<div class="form-card">
<div class="kicker" data-zh="需求整理" data-en="INQUIRY DETAILS">需求整理</div>
<h2 style="margin:0 0 8px" data-zh="填写面料需求" data-en="Describe Your Requirements">填写面料需求</h2>
<p class="hint" data-zh="填写后点击“整理询价内容”，可复制内容再通过电话或微信发送给工厂。本表单不会提交至服务器。" data-en="After filling this out, select &quot;Prepare Inquiry Details&quot; to copy the text, then send it to the factory by phone or WeChat. This form does not submit to a server.">填写后点击“整理询价内容”，可复制内容再通过电话或微信发送给工厂。本表单不会提交至服务器。</p>
<form data-inquiry novalidate="false">
<div class="form-grid">
<div class="field"><label for="name" data-zh="客户姓名" data-en="Name">客户姓名</label><input id="name" name="name" autocomplete="name" required></div>
<div class="field"><label for="contact" data-zh="联系电话或微信" data-en="Phone or WeChat">联系电话或微信</label><input id="contact" name="contact" autocomplete="tel" required></div>
<div class="field"><label for="product" data-zh="产品类型" data-en="Product Type">产品类型</label>{product_select()}</div>
<div class="field"><label for="quantity" data-zh="订单数量" data-en="Order Quantity">订单数量</label><input id="quantity" name="quantity" data-zh-placeholder="例如：预计数量" data-en-placeholder="e.g. estimated quantity" placeholder="例如：预计数量"></div>
<div class="field full"><label for="spec" data-zh="面料成分、克重、规格" data-en="Composition, Weight & Specifications">面料成分、克重、规格</label><input id="spec" name="spec" data-zh-placeholder="如暂不确定，可填写“待沟通”" data-en-placeholder="Write &quot;to be discussed&quot; if unsure" placeholder="如暂不确定，可填写“待沟通”"></div>
<div class="field full"><label for="details" data-zh="详细需求" data-en="Details">详细需求</label><textarea id="details" name="details" data-zh-placeholder="请描述用途、颜色、是否来样/来图等需求" data-en-placeholder="Application, color, sample or design details" placeholder="请描述用途、颜色、是否来样/来图等需求"></textarea></div>
<div class="field full"><button class="btn" type="submit" data-zh="整理询价内容" data-en="Prepare Inquiry Details">整理询价内容</button>
<p class="hint" data-zh="说明：本页为静态页面，不接收服务器提交，因此不会出现“已发送”状态，也不会保存任何客户资料。" data-en="Note: this is a static page. It does not accept server submissions, so no &quot;sent&quot; status is shown and no customer data is stored.">说明：本页为静态页面，不接收服务器提交，因此不会出现“已发送”状态，也不会保存任何客户资料。</p></div>
</div>
</form>
<div id="inquiry-result" class="notice hidden" style="margin-top:18px"></div>
<div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:12px"><button id="copy-inquiry" class="btn secondary" type="button" data-zh="复制询价内容" data-en="Copy Inquiry Details">复制询价内容</button><a class="btn" href="{PHONE_TEL}" data-zh="直接拨打电话" data-en="Call Us Now">直接拨打电话</a></div>
<p id="inquiry-status" class="sr-only" role="status" aria-live="polite"></p>
</div></div></section>
<section class="band"><div class="wrap"><div class="map-panel"><div><div class="map-pin" aria-hidden="true">📍</div>
<h2 data-zh="工厂位置与导航" data-en="Factory Location & Directions">工厂位置与导航</h2>
<p data-zh="{esc(ADDR_ZH)}" data-en="{esc(ADDR_EN)}">{esc(ADDR_ZH)}</p></div>
<a class="btn" href="{AMAP}" target="_blank" rel="noopener" data-zh="打开高德地图 ↗" data-en="Open Amap ↗">打开高德地图 ↗</a></div>
<p class="hint" style="margin-top:12px" data-zh="当前采用高德地图分享链接作为导航入口；如需在网页内嵌入地图，需进一步核验该分享链接是否支持网页内嵌及高德开放平台的接口要求。" data-en="The Amap share link is used as a directions entry. Embedding a map would require verifying whether this share link supports embedding and reviewing the Amap open platform requirements.">当前采用高德地图分享链接作为导航入口；如需在网页内嵌入地图，需进一步核验该分享链接是否支持网页内嵌及高德开放平台的接口要求。</p>
</div></section>
<section><div class="wrap"><div class="section-head"><div>
<div class="kicker" data-zh="联系建议" data-en="HOW TO REACH US">联系建议</div>
<h2 data-zh="这样联系更高效" data-en="The Fastest Way to Reach Us">这样联系更高效</h2>
</div></div><div class="grid-3">
<div class="card"><div class="card-body"><h3 data-zh="电话沟通" data-en="By Phone">电话沟通</h3><p data-zh="急单或需要当场确认细节时，直接拨打 {PHONE}。" data-en="For urgent enquiries or details to confirm on the spot, call {PHONE} directly.">急单或需要当场确认细节时，直接拨打 {PHONE}。</p></div></div>
<div class="card"><div class="card-body"><h3 data-zh="微信沟通" data-en="By WeChat">微信沟通</h3><p data-zh="可通过微信 {PHONE} 发送样布照片、色卡或需求说明。" data-en="Send swatch photos, color cards or requirement notes via WeChat {PHONE}.">可通过微信 {PHONE} 发送样布照片、色卡或需求说明。</p></div></div>
<div class="card"><div class="card-body"><h3 data-zh="来访工厂" data-en="Visiting the Factory">来访工厂</h3><p data-zh="如需到厂沟通，请先电话确认时间与接待安排，避免无人接待。" data-en="If you plan to visit, please call ahead to confirm a time and reception arrangements.">如需到厂沟通，请先电话确认时间与接待安排，避免无人接待。</p></div></div>
</div></div></section>
{cta_section("还有其他问题？", "Any Other Questions?")}"""

CONTACT = {
    "slug": "contact.html",
    "title_zh": f"联系我们｜电话微信 {PHONE} - 即墨区利晨针织厂",
    "title_en": f"Contact | Phone & WeChat {PHONE} - Jimo Lichen Knitting Factory",
    "desc_zh": f"即墨区利晨针织厂联系方式：电话与微信 {PHONE}，地址位于山东省青岛市即墨区通济街道办事处张家西城东村工业园。可拨打电话、加微信或通过高德地图导航到厂。",
    "desc_en": f"Contact Jimo Lichen Knitting Factory: phone and WeChat {PHONE}, located in Zhangjia Xichengdong Village Industrial Park, Tongji Subdistrict, Jimo District, Qingdao, Shandong. Call, message on WeChat or use Amap for directions.",
    "key_zh": "即墨区利晨针织厂联系方式,青岛针织厂电话,即墨针织厂地址,针织面料工厂联系,13210025853",
    "key_en": "Jimo Lichen Knitting Factory contact, Qingdao knitting factory phone, knitted fabric supplier address, knitting factory WeChat",
    "og_type": "website",
    "og_image": "assets/img/factory-5.jpg",
    "body": CONTACT_BODY,
    "jsonld": [bc_jsonld(CONTACT_CRUMBS, "联系我们"), org_jsonld()],
}

# =================================================================== product detail pages
DETAIL_PAGES = []

_DETAILS = [
    {
        "slug": "product-single-jersey.html",
        "file_src": "assets/img/fabric-single-jersey-large.jpg",
        "alt_zh": "平纹针织面料纹理示意图",
        "alt_en": "Single jersey knit texture illustration",
        "name_zh": "平纹针织面料",
        "name_en": "Single Jersey Knit",
        "hero_zh": "可根据客户用途沟通面料成分、克重、颜色与规格。支持来样或来图作为沟通参考。",
        "hero_en": "Discuss composition, weight, color and specifications based on the intended use. Samples or images can be used as references.",
        "intro_zh": "平纹织物是最常见的单面针织结构之一，正反面外观不同。本页不预设固定成分或克重，所有参数按订单需求沟通确认。",
        "intro_en": "Plain (single jersey) is one of the most common single-faced knit structures, with a different face and back. This page does not preset a composition or weight; all parameters are agreed per order.",
        "specs_zh": ["面料组织方向：单面 / 平纹", "成分：按需求沟通", "克重：按需求沟通", "颜色与规格：按订单确认"],
        "specs_en": ["Structure: single-faced / plain", "Composition: discussed per requirement", "Weight: discussed per requirement", "Color and specifications: confirmed per order"],
        "title_zh": "平纹针织面料｜来样来图定制 - 即墨区利晨针织厂",
        "title_en": "Single Jersey Knit Fabric | Custom Knitted Fabric - Jimo Lichen Factory",
        "desc_zh": "即墨区利晨针织厂提供平纹针织面料（单面针织面料）定制与加工，支持来样、来图、成分与克重、颜色与规格定制，具体报价与打样按需求沟通确认。",
        "desc_en": "Custom single jersey knitted fabric from Jimo Lichen Knitting Factory: sample-based and design-based customization, composition, weight, color and specification options. Quotes and sampling confirmed per inquiry.",
        "key_zh": "平纹针织面料,单面针织面料,平纹布定制,针织面料来样定制,即墨区利晨针织厂",
        "key_en": "single jersey fabric, plain knit fabric, custom single jersey, jersey knit supplier China",
        "use_zh": "服装、内衣、T恤及客户指定的其他用途，均可作为沟通起点；实际适用范围以沟通确认为准。",
        "use_en": "Apparel, underwear, T-shirts and other customer-specified applications can all serve as a starting point for discussion; suitability is confirmed during discussion.",
    },
    {
        "slug": "product-double-knit.html",
        "file_src": "assets/img/fabric-double-knit-large.jpg",
        "alt_zh": "双面针织面料纹理示意图",
        "alt_en": "Double knit fabric texture illustration",
        "name_zh": "双面针织面料",
        "name_en": "Double Knit Fabric",
        "hero_zh": "可沟通不同成分、克重、颜色及规格要求，具体面料方案需根据用途和样品确认。",
        "hero_en": "Discuss composition, weight, color and specifications. The fabric solution is confirmed based on application and sample.",
        "intro_zh": "双面针织面料由双面机织造，结构相对稳定。本页不预设固定成分或克重，所有参数按订单需求沟通确认。",
        "intro_en": "Double knit fabric is produced on double knit machines and has a relatively stable structure. This page does not preset a composition or weight; all parameters are agreed per order.",
        "specs_zh": ["面料组织方向：双面", "成分：按需求沟通", "克重：按需求沟通", "颜色与规格：按订单确认"],
        "specs_en": ["Structure: double knit", "Composition: discussed per requirement", "Weight: discussed per requirement", "Color and specifications: confirmed per order"],
        "title_zh": "双面针织面料｜来样来图定制 - 即墨区利晨针织厂",
        "title_en": "Double Knit Fabric | Custom Knitted Fabric - Jimo Lichen Factory",
        "desc_zh": "即墨区利晨针织厂提供双面针织面料定制与加工，支持来样、来图、成分与克重、颜色与规格定制，具体报价与打样按需求沟通确认。",
        "desc_en": "Custom double knit fabric from Jimo Lichen Knitting Factory: sample-based and design-based customization, composition, weight, color and specification options. Quotes and sampling confirmed per inquiry.",
        "key_zh": "双面针织面料,双面布定制,双面机织造,针织面料定制,即墨区利晨针织厂",
        "key_en": "double knit fabric, interlock fabric, custom double knit, double knit supplier China",
        "use_zh": "外套、休闲装及其他客户指定用途，均可作为沟通起点；实际适用范围以沟通确认为准。",
        "use_en": "Outerwear, casual apparel and other customer-specified applications can all serve as a starting point; suitability is confirmed during discussion.",
    },
    {
        "slug": "product-other.html",
        "file_src": "assets/img/fabric-other-large.jpg",
        "alt_zh": "其他针织面料纹理示意图",
        "alt_en": "Other knitted fabric texture illustration",
        "name_zh": "其他针织面料",
        "name_en": "Other Knitted Fabrics",
        "hero_zh": "如有特定用途、样品或图片，可联系工厂进一步沟通可行的定制方向。",
        "hero_en": "For specific applications, samples or images, contact the factory to discuss suitable customization options.",
        "intro_zh": "工厂配备毛巾机等针织设备，除平纹与双面外还可沟通其他针织组织方向。是否可行需结合样品、用途与排期确认。",
        "intro_en": "The factory operates knitting equipment including a terry machine, so knit structures beyond plain and double knit can be discussed. Feasibility depends on the sample, application and schedule.",
        "specs_zh": ["面料组织方向：其他针织 / 毛巾等", "成分：按需求沟通", "克重：按需求沟通", "颜色与规格：按订单确认"],
        "specs_en": ["Structure: other knits / terry and similar", "Composition: discussed per requirement", "Weight: discussed per requirement", "Color and specifications: confirmed per order"],
        "title_zh": "其他针织面料｜毛巾组织等针织面料定制 - 即墨区利晨针织厂",
        "title_en": "Other Knitted Fabrics | Terry & Specialty Knits - Jimo Lichen Factory",
        "desc_zh": "即墨区利晨针织厂提供平纹、双面以外的其他针织面料定制与加工沟通，配备毛巾机等设备，是否可行需结合样品、用途与生产排期确认。",
        "desc_en": "Beyond single jersey and double knit, Jimo Lichen Knitting Factory can discuss other knitted fabric structures including terry. Feasibility depends on the sample, application and production schedule.",
        "key_zh": "其他针织面料,毛巾布定制,针织面料加工,特种针织面料,即墨区利晨针织厂",
        "key_en": "terry fabric, other knitted fabrics, specialty knit fabric, custom terry fabric China",
        "use_zh": "需要特殊组织的面料需求，可提供样品或图片说明目标效果；实际可行性以沟通确认为准。",
        "use_en": "For fabrics requiring a special structure, share a sample or image to describe the target; actual feasibility is confirmed during discussion.",
    },
]

for _d in _DETAILS:
    _crumbs = [
        ("index.html", "首页", "Home"),
        ("products.html", "产品中心", "Products"),
    ]
    _spec_zh = "".join('<li data-zh="%s" data-en="%s">%s</li>' % (esc(a), esc(b), esc(a))
                       for a, b in zip(_d["specs_zh"], _d["specs_en"]))
    _body = f"""<section class="page-hero"><div class="wrap">{breadcrumbs(_crumbs, _d["name_zh"], _d["name_en"])}
<div class="eyebrow" data-zh="产品详情" data-en="PRODUCT DETAILS">产品详情</div>
<h1 data-zh="{esc(_d['name_zh'])}" data-en="{esc(_d['name_en'])}">{esc(_d['name_zh'])}</h1>
<p data-zh="{esc(_d['hero_zh'])}" data-en="{esc(_d['hero_en'])}">{esc(_d['hero_zh'])}</p>
</div></section>
<section><div class="wrap product-detail"><div class="card-img">{img(_d["file_src"], _d["alt_zh"], _d["alt_en"], 1200, 900, eager=True)}</div>
<div class="copy"><div class="kicker" data-zh="按需定制" data-en="MADE TO REQUIREMENTS">按需定制</div>
<h2 data-zh="具体规格按订单需求沟通" data-en="Specifications Confirmed for Each Order">具体规格按订单需求沟通</h2>
<p data-zh="{esc(_d['intro_zh'])}" data-en="{esc(_d['intro_en'])}">{esc(_d['intro_zh'])}</p>
<h3 style="margin:18px 0 8px;font-size:16px" data-zh="可沟通的项目" data-en="What Can Be Discussed">可沟通的项目</h3>
<ul class="checklist">{_spec_zh}</ul>
<p class="hint" data-zh="以上为沟通方向，不代表固定规格；价格、起订量与交期需按需求确认。" data-en="These are discussion directions, not fixed specifications. Pricing, MOQ and lead time are confirmed per requirement.">以上为沟通方向，不代表固定规格；价格、起订量与交期需按需求确认。</p>
<a class="btn" href="contact.html" data-zh="联系工厂询价 →" data-en="Contact for a Quote →">联系工厂询价 →</a>
<a class="btn secondary" href="products.html" style="margin-left:10px" data-zh="返回产品中心" data-en="Back to Products">返回产品中心</a>
<p class="hint" style="margin-top:14px" data-zh="图片为通用面料纹理示意图，不是本厂实拍，后续将替换为真实照片。" data-en="This image is a generic fabric texture illustration, not a photograph of our production; it will be replaced with real photos later.">图片为通用面料纹理示意图，不是本厂实拍，后续将替换为真实照片。</p>
</div></div></section>
<section class="band"><div class="wrap"><div class="grid-2">
<div class="info-box"><h3 style="margin:0 0 8px" data-zh="常见用途沟通" data-en="Discussing Applications">常见用途沟通</h3><p data-zh="{esc(_d['use_zh'])}" data-en="{esc(_d['use_en'])}">{esc(_d['use_zh'])}</p></div>
<div class="info-box"><h3 style="margin:0 0 8px" data-zh="下一步" data-en="Next Step">下一步</h3><p data-zh="提供样品或图片、说明用途与预计数量，即可沟通可行方向、报价与打样安排。" data-en="Share a sample or image, describe the intended use and estimated quantity, and feasible directions, pricing and sampling can be discussed.">提供样品或图片、说明用途与预计数量，即可沟通可行方向、报价与打样安排。</p><a class="text-link" href="custom.html" data-zh="查看定制流程 →" data-en="See the Customization Process →">查看定制流程 →</a></div>
</div></div></section>
{cta_section()}"""
    DETAIL_PAGES.append(
        {
            "slug": _d["slug"],
            "title_zh": _d["title_zh"],
            "title_en": _d["title_en"],
            "desc_zh": _d["desc_zh"],
            "desc_en": _d["desc_en"],
            "key_zh": _d["key_zh"],
            "key_en": _d["key_en"],
            "og_type": "website",
            "og_image": _d["file_src"],
            "body": _body,
            "jsonld": [bc_jsonld(_crumbs, _d["name_zh"]), org_jsonld()],
        }
    )

# =================================================================== 404.html
NOTFOUND_BODY = f"""<section class="page-hero"><div class="wrap">
<div class="eyebrow" data-zh="404" data-en="404">404</div>
<h1 data-zh="页面没有找到" data-en="Page Not Found">页面没有找到</h1>
<p data-zh="您访问的地址可能已更改或输入有误。可以通过下面的入口继续浏览，或直接联系工厂。" data-en="The address may have changed or been mistyped. Continue browsing below, or contact the factory directly.">您访问的地址可能已更改或输入有误。可以通过下面的入口继续浏览，或直接联系工厂。</p>
</div></section>
<section><div class="wrap"><div class="grid-3">
<div class="card"><div class="card-body"><h3 data-zh="首页" data-en="Home">首页</h3><p data-zh="返回网站首页，查看工厂与产品概览。" data-en="Return to the homepage for an overview of the factory and products.">返回网站首页，查看工厂与产品概览。</p><a class="text-link" href="index.html" data-zh="回到首页 →" data-en="Go to Homepage →">回到首页 →</a></div></div>
<div class="card"><div class="card-body"><h3 data-zh="产品中心" data-en="Products">产品中心</h3><p data-zh="查看平纹、双面及其他针织面料类别。" data-en="See single jersey, double knit and other knitted fabric categories.">查看平纹、双面及其他针织面料类别。</p><a class="text-link" href="products.html" data-zh="查看产品 →" data-en="View Products →">查看产品 →</a></div></div>
<div class="card"><div class="card-body"><h3 data-zh="联系我们" data-en="Contact">联系我们</h3><p data-zh="电话或微信 {PHONE}，也可使用高德地图导航。" data-en="Phone or WeChat {PHONE}; Amap directions are also available.">电话或微信 {PHONE}，也可使用高德地图导航。</p><a class="text-link" href="contact.html" data-zh="联系工厂 →" data-en="Contact Us →">联系工厂 →</a></div></div>
</div></div></section>"""

NOTFOUND = {
    "slug": "404.html",
    "title_zh": "页面未找到｜即墨区利晨针织厂",
    "title_en": "Page Not Found | Jimo Lichen Knitting Factory",
    "desc_zh": "页面未找到。请通过首页、产品中心或联系我们页面继续浏览即墨区利晨针织厂网站。",
    "desc_en": "Page not found. Continue browsing the Jimo Lichen Knitting Factory website via the homepage, products or contact page.",
    "key_zh": "即墨区利晨针织厂",
    "key_en": "Jimo Lichen Knitting Factory",
    "og_type": "website",
    "body": NOTFOUND_BODY,
    "jsonld": [],
}

# =================================================================== write files
PAGES = [INDEX, ABOUT, PRODUCTS, CUSTOM, CONTACT] + DETAIL_PAGES + [NOTFOUND]

SITEMAP_SKIP = {"404.html"}


def sitemap_priorities(slug):
    """Relative crawl priority. Homepage highest, commercial pages next."""
    if slug == "index.html":
        return "1.0", "weekly"
    if slug in ("products.html", "custom.html", "contact.html"):
        return "0.9", "monthly"
    if slug.startswith("product-"):
        return "0.8", "monthly"
    return "0.7", "monthly"


def write_sitemap():
    """Sitemap requires absolute URLs, so it is only written once an origin exists."""
    sitemap_path = os.path.join(OUT, "sitemap.xml")
    if not URL_ORIGIN:
        # Remove a previously generated sitemap so a stale domain can never ship.
        if os.path.exists(sitemap_path):
            os.remove(sitemap_path)
            print("removed stale sitemap.xml (no origin configured)")
        return False
    from datetime import date

    today = date.today().isoformat()
    entries = []
    for cfg in PAGES:
        slug = cfg["slug"]
        if slug in SITEMAP_SKIP:
            continue
        pr, freq = sitemap_priorities(slug)
        entries.append(
            "  <url>\n"
            "    <loc>%s</loc>\n"
            "    <lastmod>%s</lastmod>\n"
            "    <changefreq>%s</changefreq>\n"
            "    <priority>%s</priority>\n"
            "  </url>" % (page_url(cfg), today, freq, pr)
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )
    io.open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8", newline="\n").write(xml)
    print("wrote sitemap.xml (%d urls)" % len(entries))
    return True


def main():
    os.makedirs(OUT, exist_ok=True)
    for cfg in PAGES:
        html_text = page(cfg)
        if cfg["slug"] == "404.html":
            html_text = html_text.replace('<meta name="robots" content="index,follow">',
                                          '<meta name="robots" content="noindex,follow">')
        path = os.path.join(OUT, cfg["slug"])
        io.open(path, "w", encoding="utf-8", newline="\n").write(html_text)
        print("wrote %-32s %6d bytes" % (cfg["slug"], len(html_text.encode("utf-8"))))

    # robots.txt
    if URL_ORIGIN:
        robots = (
            "User-agent: *\n"
            "Allow: /\n"
            "Disallow: /_diag.html\n"
            "\n"
            "Sitemap: %s/sitemap.xml\n" % URL_ORIGIN
        )
    else:
        robots = (
            "User-agent: *\n"
            "Allow: /\n"
            "Disallow: /_diag.html\n"
            "\n"
            "# 网站尚未绑定域名，先不声明 Sitemap。\n"
            "# 绑定域名后运行 python tools/set_domain.py https://your-domain 即可自动生成。\n"
        )
    io.open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8", newline="\n").write(robots)
    print("wrote robots.txt")
    write_sitemap()

    # web app manifest
    manifest = {
        "name": BRAND_ZH,
        "short_name": "利晨针织",
        "description": "针织面料定制与加工",
        "lang": "zh-CN",
        "start_url": "./index.html",
        "scope": "./",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#1456a0",
        "icons": [
            {"src": "assets/favicon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any"},
            {"src": "assets/img/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
            {"src": "assets/img/apple-touch-icon.png", "sizes": "180x180", "type": "image/png"},
        ],
    }
    io.open(os.path.join(OUT, "site.webmanifest"), "w", encoding="utf-8", newline="\n").write(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    )
    print("wrote site.webmanifest")


if __name__ == "__main__":
    main()