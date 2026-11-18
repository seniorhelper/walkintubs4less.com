# walkintubs4less.com static site generator v2 (2026-11-17)
# Usage: python3 -I _build/build.py            (writes into the repo root, next to _build/)
# Renders every page from data: products.py (catalog), pages.py (static page bodies), guides from the GUIDES helper.
import os, sys, json, html, shutil, re, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import products as P  # noqa: E402

ROOT = os.path.dirname(HERE)
DOMAIN = "https://walkintubs4less.com"
PHONE = "1-888-779-2284"
TEL = "+18887792284"
EMAIL = "sales@agingsafelybaths.com"
LEAD = "https://clients.eyetoad.com/lead/send.php"
TODAY = "2026-11-17"
ASB = "https://www.agingsafelybaths.com"
BBB = "https://www.bbb.org/us/co/denver/profile/walk-in-tubs/aging-safely-walk-in-tubs-1296-90145069"
STORE = "Walk-In Tubs 4 Less"
GUIDES_SRC = "/home/claude/research/wt4l/guides"
VER = "20261117"
PAGES = {}   # path -> html
PAGES_404 = ""
EXTRA_FILES = {}
ALL = []
SITEMAP = []  # (path, priority)


def esc(s):
    return html.escape(str(s), quote=True)


def fmt(x):
    return P.fmt(x)


def ico(name, size=20):
    paths = {
        "phone": '<path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1A17 17 0 0 1 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1z" fill="currentColor"/>',
        "check": '<path d="M9 16.2 4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4z" fill="currentColor"/>',
        "shield": '<path d="M12 2 4 5v6c0 5 3.4 9.7 8 11 4.6-1.3 8-6 8-11V5z" fill="none" stroke="currentColor" stroke-width="2"/><path d="m8.5 12 2.5 2.5 4.5-5" fill="none" stroke="currentColor" stroke-width="2"/>',
        "star": '<path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z" fill="currentColor"/>',
        "truck": '<path d="M2 6h11v9H2zM13 9h4l3 3v3h-7z" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="6" cy="17" r="2" fill="currentColor"/><circle cx="17" cy="17" r="2" fill="currentColor"/>',
        "clock": '<circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 7v5l3 2" fill="none" stroke="currentColor" stroke-width="2"/>',
        "wide": '<path d="M3 12h18M6 8l-3 4 3 4M18 8l3 4-3 4" fill="none" stroke="currentColor" stroke-width="2"/>',
        "two": '<circle cx="8" cy="8" r="3" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="16" cy="8" r="3" fill="none" stroke="currentColor" stroke-width="2"/><path d="M3 20c0-3 2.5-5 5-5s5 2 5 5M11 20c0-3 2.5-5 5-5s5 2 5 5" fill="none" stroke="currentColor" stroke-width="2"/>',
        "chair": '<circle cx="10" cy="4.5" r="2" fill="currentColor"/><path d="M10 8v6h6l2 5M10 11h5" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="9.5" cy="16.5" r="4.5" fill="none" stroke="currentColor" stroke-width="2"/>',
        "step": '<path d="M3 20h6v-5h6v-5h6" fill="none" stroke="currentColor" stroke-width="2"/>',
        "waves": '<path d="M3 9c3-2 6 2 9 0s6 2 9 0M3 15c3-2 6 2 9 0s6 2 9 0" fill="none" stroke="currentColor" stroke-width="2"/>',
        "flag": '<path d="M5 21V4M5 4h12l-2 4 2 4H5" fill="none" stroke="currentColor" stroke-width="2"/>',
        "small": '<rect x="4" y="4" width="16" height="16" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M9 9h6v6H9z" fill="currentColor"/>',
        "menu": '<path d="M3 6h18M3 12h18M3 18h18" stroke="currentColor" stroke-width="2.4"/>',
    }
    return '<svg viewBox="0 0 24 24" width="%d" height="%d" aria-hidden="true" focusable="false">%s</svg>' % (size, size, paths[name])


def call_btn(cls="btn btn-call", label=True):
    return '<a class="%s" href="tel:%s">%s<span>%s</span></a>' % (cls, TEL, ico("phone"), ("Call " + PHONE) if label else PHONE)


def quote_btn(href="/quote/", text="Get my price", cls="btn btn-quote"):
    return '<a class="%s" href="%s">%s</a>' % (cls, esc(href), esc(text))


# ---------------- needs / brands navigation ----------------
NEEDS = [
    ("wide", "Wide and bariatric", "32 in. and wider, or rated for larger bathers", "wide"),
    ("two", "Two-seat tubs", "Room for two, or one bather who wants to stretch out", "two"),
    ("transfer", "Wheelchair transfer", "Outward or lift-up doors with transfer seats", "chair"),
    ("lowstep", "Low step-in", "The lowest thresholds we have published heights for", "step"),
    ("jets", "Hydrotherapy jets", "Water jets, air jets or both", "waves"),
    ("usa", "Made in USA", "Rane by Bestbath, built in Sparta, Tennessee", "flag"),
    ("small", "Small bathrooms", "48 in. long or less, for tight rooms", "small"),
]
BRAND_ORDER = ["hydro-dimensions", "ellas-bubbles", "meditub", "rane", "anzzi"]
BRAND_LINE = {
    "hydro-dimensions": "Lifetime warranty on the whole tub",
    "ellas-bubbles": "Widest range: transfer, two-seat, lay-down",
    "meditub": "Sizes from 26 x 46 to 36 x 60",
    "rane": "Fully made in USA, healthcare grade",
    "anzzi": "Lowest-cost soakers and dual therapy",
}


def header(path):
    brands = "".join('<a href="/brands/%s/">%s<small>%s</small></a>' % (k, esc(P.BRANDS[k]["name"]), esc(BRAND_LINE[k])) for k in BRAND_ORDER)
    needs = "".join('<a href="/walk-in-tubs/#need=%s">%s<small>%s</small></a>' % (k, esc(n), esc(d)) for k, n, d, _ in NEEDS)
    buying = ('<a href="/walk-in-tubs/">All walk-in tubs<small>Filter every model we sell</small></a>'
              '<a href="/supply-only/">Supply only<small>Shipped to you or your installer</small></a>'
              '<a href="/white-glove/">Fully installed<small>Factory-certified install, old tub hauled away</small></a>'
              '<a href="/compare/">Compare tubs<small>Up to three side by side</small></a>'
              '<a href="/specs/">Specs and rough-in<small>Every size, door and capacity in one table</small></a>'
              '<a href="/planner/">Fit planner<small>Doorway, alcove and water heater check</small></a>')
    mega = ('<div class="mega" id="mega-shop"><div class="wrap">'
            '<div><h3>Shop by brand</h3>%s</div><div><h3>Shop by need</h3>%s</div><div><h3>Buying</h3>%s</div>'
            '<div class="m-card"><h3>Talk to a person</h3><p>Tell us the bathroom size and who is bathing. We match the tub and price it both ways, shipped or installed.</p>%s<p class="mt10">%s</p></div>'
            '</div></div>') % (brands, needs, buying, call_btn("btn btn-call full"), quote_btn(cls="btn btn-line full"))
    drawer = ('<div class="drawer" id="drawer"><div class="wrap">'
              '<a class="d-top" href="/walk-in-tubs/">All walk-in tubs</a>'
              '<details><summary>Shop by brand</summary>%s</details>'
              '<details><summary>Shop by need</summary>%s</details>'
              '<details><summary>Buying help</summary>%s</details>'
              '<a class="d-top" href="/guides/">Guides</a><a class="d-top" href="/faq/">FAQ</a><a class="d-top" href="/about/">About us</a>'
              '</div></div>') % (
        "".join('<a href="/brands/%s/">%s</a>' % (k, esc(P.BRANDS[k]["name"])) for k in BRAND_ORDER) + '<a href="/brands/">All brands</a>',
        "".join('<a href="/walk-in-tubs/#need=%s">%s</a>' % (k, esc(n)) for k, n, _, _ in NEEDS),
        '<a href="/supply-only/">Supply only</a><a href="/white-glove/">Fully installed</a><a href="/compare/">Compare tubs</a><a href="/specs/">Specs and rough-in</a><a href="/planner/">Fit planner</a><a href="/quote/">Get my price</a>')
    nav = ('<ul class="nav" aria-label="Main">'
           '<li><button type="button" data-mega aria-expanded="false" aria-controls="mega-shop">Shop tubs</button></li>'
           '<li><a href="/supply-only/">Supply only</a></li><li><a href="/white-glove/">Fully installed</a></li>'
           '<li><a href="/guides/">Guides</a></li><li><a href="/faq/">FAQ</a></li></ul>')
    return ('<a class="skip" href="#main">Skip to content</a>'
            '<div class="strip"><div class="wrap"><span>An <b>Aging Safely Baths</b> company</span>'
            '<span class="s-hide">BBB A+ since 2012 &middot; Open 7 days, 7am to 8pm MT</span></div></div>'
            '<header class="hdr"><div class="wrap">'
            '<a class="brand" href="/" aria-label="Walk-In Tubs 4 Less by Aging Safely Baths, home">'
            '<img src="/assets/aging-safely-baths-logo.webp" srcset="/assets/aging-safely-baths-logo-400.webp 400w, /assets/aging-safely-baths-logo.webp 660w" sizes="(min-width:900px) 280px, 200px" width="660" height="175" alt="Aging Safely Baths logo">'
            '<span>Walk-In Tubs 4 Less</span></a>'
            '<nav aria-label="Main">%s</nav>'
            '<div class="hdr-cta">%s%s<button class="menu-btn" type="button" aria-expanded="false" aria-controls="drawer">%s Menu</button></div>'
            '</div>%s%s</header>') % (nav, call_btn("btn btn-call", label=False), quote_btn(), ico("menu"), mega, drawer)


def trust_bar():
    items = [("shield", "<b>BBB A+</b> accredited since 2012"), ("star", "<b>4.9</b> on Google"),
             ("truck", "Ships to <b>50 states + Canada</b>"), ("clock", "<b>1-day install</b> in most homes"),
             ("check", "<b>Lifetime shell</b> warranty on most models")]
    return '<section class="trust" aria-label="Why buy from us"><div class="wrap"><ul>%s</ul></div></section>' % "".join(
        "<li>%s<span>%s</span></li>" % (ico(i, 18), t) for i, t in items)


def footer():
    return ('<footer class="ftr"><div class="wrap"><div class="cols">'
            '<div><img class="f-logo" src="/assets/aging-safely-baths-logo-400.webp" width="400" height="106" alt="Aging Safely Baths" loading="lazy">'
            '<p><b>%s</b><br>An Aging Safely Baths company. BBB A+ since 2012.</p>'
            '<p><a href="tel:%s"><b>%s</b></a><br><a href="mailto:%s">%s</a><br>Open 7 days, 7am to 8pm Mountain</p></div>'
            '<div><h2>Shop</h2><ul><li><a href="/walk-in-tubs/">All walk-in tubs</a></li>%s<li><a href="/compare/">Compare tubs</a></li></ul></div>'
            '<div><h2>Buying</h2><ul><li><a href="/supply-only/">Supply only</a></li><li><a href="/white-glove/">Fully installed</a></li><li><a href="/specs/">Specs and rough-in</a></li><li><a href="/planner/">Fit planner</a></li><li><a href="/tech-support/">Installer tech support</a></li><li><a href="/quote/">Get my price</a></li></ul></div>'
            '<div><h2>Company</h2><ul><li><a href="/about/">About us</a></li><li><a href="/guides/">Guides</a></li><li><a href="/faq/">FAQ</a></li><li><a href="/privacy/">Privacy</a></li><li><a href="/accessibility/">Accessibility</a></li>'
            '<li><a href="%s/" rel="nofollow">Aging Safely Baths</a></li><li><a href="https://www.showers4less.com/" rel="nofollow">Showers4Less</a></li></ul></div>'
            '</div><div class="fine"><p>No bathing product eliminates the risk of falls; walk-in tubs are designed to reduce risk when installed and used properly. '
            'Specs come from each manufacturer\'s published sheets and can change; your written quote confirms the exact model. Prices are given by written quote.</p>'
            '<p>&copy; 2026 %s, an Aging Safely Baths company. Denver, Colorado.</p></div></div></footer>'
            '<div class="mbar">%s%s</div>') % (
        STORE, TEL, PHONE, EMAIL, EMAIL,
        "".join('<li><a href="/brands/%s/">%s</a></li>' % (k, esc(P.BRANDS[k]["name"])) for k in BRAND_ORDER),
        ASB, STORE, call_btn("btn btn-call", label=False), quote_btn())


def org_node():
    return {"@type": ["Store", "HomeAndConstructionBusiness"], "@id": DOMAIN + "/#org", "name": STORE,
            "url": DOMAIN + "/", "logo": DOMAIN + "/assets/aging-safely-baths-logo.webp", "image": DOMAIN + "/assets/og.png",
            "telephone": "+1-888-779-2284", "email": EMAIL,
            "parentOrganization": {"@type": "Organization", "name": "Aging Safely Baths", "legalName": "Aging Safely Baths & More, LLC", "url": ASB + "/"},
            "address": {"@type": "PostalAddress", "addressLocality": "Denver", "addressRegion": "CO", "addressCountry": "US"},
            "areaServed": [{"@type": "Country", "name": "United States"}, {"@type": "Country", "name": "Canada"}],
            "openingHours": "Mo-Su 07:00-20:00", "sameAs": [ASB + "/", BBB],
            "brand": [{"@type": "Brand", "name": P.BRANDS[k]["name"]} for k in BRAND_ORDER]}


def crumbs_html(trail):
    if not trail:
        return ""
    li = ['<li><a href="/">Home</a></li>']
    for i, (n, u) in enumerate(trail):
        li.append('<li>%s</li>' % (esc(n) if i == len(trail) - 1 else '<a href="%s">%s</a>' % (esc(u), esc(n))))
    return '<nav class="crumbs wrap" aria-label="Breadcrumb"><ol>%s</ol></nav>' % "".join(li)


def crumbs_ld(trail):
    items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN + "/"}]
    for i, (n, u) in enumerate(trail):
        items.append({"@type": "ListItem", "position": i + 2, "name": n, "item": DOMAIN + u})
    return {"@type": "BreadcrumbList", "itemListElement": items}


def faq_ld(qas):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in qas]}


def faq_html(qas, h="Questions buyers ask"):
    return '<div class="faq"><h2>%s</h2>%s</div>' % (esc(h), "".join(
        '<details><summary>%s</summary><div><p>%s</p></div></details>' % (esc(q), a) for q, a in qas))


def strip(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()


def band(h="Not sure which tub fits?", p="Call and tell us about the bathroom and the bather. We price it shipped or installed, in writing."):
    return ('<section class="band"><div class="wrap"><div><h2>%s</h2><p>%s</p></div><div class="btns">%s%s</div></div></section>'
            % (esc(h), esc(p), call_btn(), quote_btn()))


CSP = ("default-src 'self'; script-src 'self'; style-src 'self' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; "
       "img-src 'self' data:; connect-src https://clients.eyetoad.com; form-action 'self' https://clients.eyetoad.com; base-uri 'self'; object-src 'none'")


def page(path, title, desc, body, trail=None, ld=None, index=True, og_img=None, home=False, canonical=None):
    assert len(desc) <= 175, (path, len(desc))
    url = DOMAIN + "/" + path
    graph = [org_node()] if home else [{"@type": "Organization", "@id": DOMAIN + "/#org", "name": STORE, "url": DOMAIN + "/",
                                         "telephone": "+1-888-779-2284",
                                         "parentOrganization": {"@type": "Organization", "name": "Aging Safely Baths", "url": ASB + "/"}}]
    if trail:
        graph.append(crumbs_ld(trail))
    graph += (ld or [])
    og = og_img or DOMAIN + "/assets/og.png"
    doc = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
           '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
           '<meta http-equiv="Content-Security-Policy" content="%s">\n'
           '<meta name="referrer" content="strict-origin-when-cross-origin">\n'
           '<title>%s</title>\n<meta name="description" content="%s">\n<meta name="robots" content="%s">\n'
           '<link rel="canonical" href="%s">\n'
           '<meta property="og:type" content="%s"><meta property="og:site_name" content="%s"><meta property="og:title" content="%s">'
           '<meta property="og:description" content="%s"><meta property="og:url" content="%s"><meta property="og:image" content="%s">\n'
           '<meta name="twitter:card" content="summary_large_image">\n'
           '<link rel="icon" href="/favicon.svg" type="image/svg+xml">\n'
           '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
           '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&amp;display=swap">\n'
           '<link rel="stylesheet" href="/assets/site.css?v=%s">\n'
           '<script type="application/ld+json">%s</script>\n</head>\n<body>\n%s\n<main id="main">\n%s\n%s\n</main>\n%s\n'
           '<script src="/assets/site.js?v=%s" defer></script>\n<script src="/lead-send.js" defer></script>\n</body>\n</html>\n') % (
        CSP, esc(title), esc(desc), "index,follow" if index else "noindex,follow", esc(canonical or url),
        "website" if home else "article" if path.startswith("guides/") and path != "guides/" else "website",
        STORE, esc(title), esc(desc), esc(url), esc(og), VER,
        json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False).replace("</", "<\\/"),
        header(path), crumbs_html(trail), body, footer(), VER)
    PAGES[path] = doc
    if index:
        SITEMAP.append(path)


def redirect(path, to):
    u = DOMAIN + to
    PAGES[path] = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Moved</title><meta name="robots" content="noindex">'
                   '<link rel="canonical" href="%s"><meta http-equiv="refresh" content="0; url=%s"></head><body><p>This page moved to <a href="%s">%s</a>.</p></body></html>\n'
                   % (u, u, u, u))


# ---------------- product helpers ----------------
def drawing_svg(p, cls="", title=True):
    """Original top-view drawing of the tub footprint from published dimensions."""
    W, L = p["W"] or 30, p["L"] or 60
    sc = min(280 / L, 150 / W)
    w, l = L * sc, W * sc
    x0, y0 = (400 - w) / 2 - 22, 40 + (170 - l) / 2
    door_at = p["door"] in ("outward", "upward")
    seat_w = min(w * .32, 24 * sc)
    two = p["two"]
    parts = ['<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="14" fill="#fff" stroke="#12357a" stroke-width="3"/>' % (x0, y0, w, l),
             '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="10" fill="#e8f2fb" stroke="#9db8d6" stroke-width="1.5"/>' % (x0 + 8, y0 + 8, w - 16, l - 16)]
    seats = [x0 + 10] + ([x0 + w - 10 - seat_w] if two else [])
    for sx in seats:
        parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6" fill="#cfe2f3" stroke="#12357a" stroke-width="1.5"/>' % (sx, y0 + 10, seat_w, l - 20))
        parts.append('<text x="%.1f" y="%.1f" font-size="11" text-anchor="middle" fill="#12357a" font-family="Inter,Arial,sans-serif">SEAT</text>' % (sx + seat_w / 2, y0 + l / 2 + 4))
    dx = x0 + 10 + seat_w * .1
    dwid = min(w * .45, 30 * sc) if not p["transfer"] else min(w * .5, 34 * sc)
    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#1f7a33" stroke-width="6" stroke-linecap="round"/>' % (dx, y0 + l, dx + dwid, y0 + l))
    if door_at:
        parts.append('<path d="M%.1f %.1f A %.1f %.1f 0 0 0 %.1f %.1f" fill="none" stroke="#1f7a33" stroke-width="1.5" stroke-dasharray="4 4"/>' % (dx + dwid, y0 + l, dwid, dwid, dx, y0 + l + dwid * .6))
    else:
        parts.append('<path d="M%.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" fill="none" stroke="#1f7a33" stroke-width="1.5" stroke-dasharray="4 4"/>' % (dx + dwid, y0 + l, dwid, dwid, dx, y0 + l - dwid * .6))
    lab = {"outward": "DOOR (swings out)", "upward": "DOOR (lifts up)", "inward": "DOOR (swings in)"}.get(p["door"], "DOOR")
    parts.append('<text x="%.1f" y="%.1f" font-size="12" fill="#1f7a33" font-weight="700" font-family="Inter,Arial,sans-serif">%s</text>' % (dx, y0 + l + 20, lab))
    parts.append('<line x1="%.1f" y1="24" x2="%.1f" y2="24" stroke="#4a5872" stroke-width="1.2"/><path d="M%.1f 19v10M%.1f 19v10" stroke="#4a5872" stroke-width="1.2"/>' % (x0, x0 + w, x0, x0 + w))
    parts.append('<text x="%.1f" y="18" font-size="13" text-anchor="middle" fill="#14213d" font-family="Inter,Arial,sans-serif" font-weight="700">%s in. long</text>' % (x0 + w / 2, fmt(p["L"])))
    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#4a5872" stroke-width="1.2"/><path d="M%.1f %.1fh10M%.1f %.1fh10" stroke="#4a5872" stroke-width="1.2"/>' % (x0 + w + 16, y0, x0 + w + 16, y0 + l, x0 + w + 11, y0, x0 + w + 11, y0 + l))
    parts.append('<text x="%.1f" y="%.1f" font-size="13" fill="#14213d" font-family="Inter,Arial,sans-serif" font-weight="700">%s in.</text>' % (x0 + w + 22, y0 + l / 2 + 4, fmt(p["W"])))
    t = ('<title>%s top view drawing</title><desc>Footprint %s inches long by %s inches wide, %s, drawn to scale from published dimensions.</desc>'
         % (esc(p["name"]), fmt(p["L"]), fmt(p["W"]), esc(p["door_label"].lower()))) if title else ""
    return ('<svg class="%s" viewBox="0 0 400 260" role="img" xmlns="http://www.w3.org/2000/svg">%s'
            '<rect width="400" height="260" fill="#fbfdff"/>%s</svg>') % (cls, t, "".join(parts))


def first_img(p):
    g = [x for x in p.get("gallery", []) if x["kind"] == "photo"] or p.get("gallery", [])
    return g[0] if g else None


def card(p):
    im = first_img(p)
    if im:
        media = '<img src="%s" width="%d" height="%d" alt="%s walk-in tub" loading="lazy" decoding="async">' % (im["src"], im["w"], im["h"], esc(p["name"]))
    else:
        media = drawing_svg(p, title=False).replace('role="img"', 'aria-hidden="true"')
    chips = [p["size"], p["door_label"]]
    if p["seat_w"]:
        chips.append('%s in. seat' % fmt(p["seat_w"]))
    elif p["cap"]:
        chips.append('%s gal' % fmt(p["cap"]))
    elif p["soaker"]:
        chips.append("Soaker")
    data = {"brand": p["brand"], "width": wbucket(p), "length": p["alcove"], "door": p["door"] or "other",
            "need": " ".join(needs_of(p)), "seat": seat_bucket(p)}
    attrs = " ".join('data-%s="%s"' % (k, esc(v)) for k, v in data.items())
    return ('<article class="pcard" %s><a class="ph" href="%s" tabindex="-1" aria-hidden="true">%s</a><div class="pb">'
            '<span class="br">%s</span><h3><a href="%s">%s</a></h3><ul class="chips">%s</ul>'
            '<div class="acts"><a class="btn btn-line" href="%s">Details</a><a class="btn btn-quote" href="/quote/?tub=%s">Price</a></div></div></article>') % (
        attrs, p["url"], media, esc(P.BRANDS[p["brand"]]["short"]), p["url"], esc(p["name"]),
        "".join("<li>%s</li>" % esc(c) for c in chips if c), p["url"], esc(p["model"]))


def wbucket(p):
    w = p["W"] or 0
    return "u28" if w < 28 else ("w28" if w < 32 else "w32")


def seat_bucket(p):
    s = p["seat_w"] or 0
    return "s24" if s >= 24 else ("s22" if s >= 22 else ("s20" if s else "na"))


def needs_of(p):
    n = []
    if p["wide"]: n.append("wide")
    if p["two"]: n.append("two")
    if p["transfer"]: n.append("transfer")
    if p.get("step") and p["step"] <= 7: n.append("lowstep")
    if p["jets"] or p["air"]: n.append("jets")
    if p["usa"]: n.append("usa")
    if p["small"]: n.append("small")
    if p["soaker"]: n.append("soaker")
    return n


# ---------------- page builders ----------------
import pages as PG  # noqa: E402  (static page bodies; uses helpers above)


def write_all():
    keep = {".git", "_build", "CNAME", ".nojekyll", "lead-send.js", "favicon.svg"}
    # remove previously generated html dirs (everything except kept files); assets/tubs regenerated
    for name in os.listdir(ROOT):
        if name in keep or name == "assets":
            if name == "assets" and os.path.isdir(os.path.join(fp_root := ROOT, "assets", "spec")):
                shutil.rmtree(os.path.join(ROOT, "assets", "spec"))
            continue
        fp = os.path.join(ROOT, name)
        if os.path.isdir(fp):
            shutil.rmtree(fp)
        else:
            os.remove(fp)
    for path, doc in PAGES.items():
        fp = os.path.join(ROOT, path, "index.html") if (path == "" or path.endswith("/")) else os.path.join(ROOT, path)
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        with open(fp, "w", encoding="utf-8") as fh:
            fh.write(doc)


def main():
    prods = P.load()
    tubs_dir = os.path.join(ROOT, "assets", "tubs")
    if os.path.isdir(tubs_dir):
        shutil.rmtree(tubs_dir)
    nimg = P.process_images(prods, ROOT)
    # static assets
    shutil.copy(os.path.join(HERE, "site.css"), os.path.join(ROOT, "assets", "site.css"))
    shutil.copy(os.path.join(HERE, "site.js"), os.path.join(ROOT, "assets", "site.js"))
    logos(os.path.join(ROOT, "assets"))
    guides = PG.load_guides()
    PG.build(prods, guides, sys.modules[__name__])
    write_all()
    # text files
    PG.write_text_files(prods, guides, sys.modules[__name__])
    print("pages:", len(PAGES), "sitemap:", len(SITEMAP), "products:", len(prods), "images:", nimg, "guides:", len(guides))


def logos(dst):
    from PIL import Image
    src = "/home/claude/research/wt4l/logos/aging-safely-baths-logo.webp"
    im = Image.open(src).convert("RGBA")
    bg = Image.new("RGB", im.size, (255, 255, 255)); bg.paste(im, mask=im.split()[3])
    bg.save(os.path.join(dst, "aging-safely-baths-logo.webp"), "WEBP", quality=88)
    bg.resize((400, round(im.height * 400 / im.width)), Image.LANCZOS).save(os.path.join(dst, "aging-safely-baths-logo-400.webp"), "WEBP", quality=88)
    for old in ("planner.js",):
        fp = os.path.join(dst, old)
        if os.path.exists(fp):
            os.remove(fp)


if __name__ == "__main__":
    main()
