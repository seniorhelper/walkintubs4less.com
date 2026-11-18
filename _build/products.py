# Product data for walkintubs4less.com: normalizes model facts and writes the store's own copy.
# Facts come from the local agingsafelybaths.com export (specs only), the manufacturers' published
# sheets (Rane, ANZZI), and the CATALOG helper's enriched file when it exists. Copy is written here,
# fresh, from those facts. No ASB sentences are reused.
import json, os, re, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ASB_SRC = "/home/claude/research/wt4l/asb"
CATALOG = "/home/claude/research/wt4l/catalog"
ASB = "https://www.agingsafelybaths.com"

BRANDS = {
    "hydro-dimensions": {"name": "Hydro Dimensions", "short": "Hydro Dimensions", "asb_hub": ASB + "/hydro-dimensions-walk-in-tubs/"},
    "ellas-bubbles": {"name": "Ella's Bubbles", "short": "Ella's Bubbles", "asb_hub": ASB + "/ella-bubbles-walk-in-tubs/"},
    "meditub": {"name": "Meditub", "short": "Meditub", "asb_hub": ASB + "/brand/meditub/"},
    "rane": {"name": "Rane by Bestbath", "short": "Rane", "asb_hub": ""},
    "anzzi": {"name": "ANZZI", "short": "ANZZI", "asb_hub": ""},
}
ASB_BRAND = {"Hydro Dimensions": "hydro-dimensions", "Ella": "ellas-bubbles", "Meditub": "meditub"}
SKIP = {"ella-microbubble", "hydro-dimensions-3260-large"}  # therapy page / duplicate listing, not a distinct model


def num(s):
    if s is None:
        return None
    m = re.search(r"(\d+(?:\.\d+)?)", str(s))
    return float(m.group(1)) if m else None


def fmt(x):
    if x is None:
        return ""
    return ("%g" % x)


# ---------- overlays: facts from manufacturer sheets I opened (Rane brochures, anzzi.com listings) ----------
# keyed by CATALOG slug; "url" keeps a URL that the earlier build already used.
OVERLAY = {
    "rane-rk12-winnipeg-6133": {"url": "rane-rk12-winnipeg", "series": "Transfer tub (home and healthcare)",
        "door_note": "Outward-swinging door with a compression handle and a secondary safety latch",
        "shell": "Gelcoat composite shell on a welded aluminum frame", "cap_note": "48 gallons at overflow, unoccupied", "occupant": 600,
        "therapy": ["CleanRane air spa (factory-installed)", "Built-in disinfectant system", "Thermostatic mixing valve", "Temperature readout"],
        "extra": [("Occupant capacity", "600 lb"), ("Water depth", "About 21 in. from the tub floor"), ("Loaded weight", "About 905 lb with tub, bather and water"),
                  ("Plumbing", "1.5 in. drain outlet; hot and cold male NPT supplies"), ("Leveling", "4 adjustable feet (0 to 2 in.)"),
                  ("Standards listed", "CSA B45.5 / ANSI Z124, ASME A112.19.7M and A112.19.8M, UL 1795")],
        "rough": "Stud opening is the nominal size plus 1/4 in., never smaller, per the Rane sheet. Check the floor framing against the loaded weight.",
        "avail": "Call to confirm current availability: Rane builds the RK12 for healthcare and home use, and we confirm it with Bestbath before quoting.",
        "source": ("Rane RK12 Winnipeg brochure", "https://ezable.com/content/2014RaneBrochures/RK12WinnipegBrochure.pdf"), "power": "yes"},
    "rane-rr7-atlantic-7334": {"url": "rane-rr7-atlantic", "model": "RR7-II Atlantic", "series": "Reclining transfer tub (Professional Health Care Series)",
        "H": 51, "cap": 38, "cap_note": "38 gallons with a bather seated; 24 gallons to pre-fill the foot well", "door": "upward",
        "door_note": "Upward-swinging door, left side only", "shell": "Composite shell", "occupant": 450, "seat_h": 21, "seat_w": 24,
        "therapy": ["Thermostatic mixing valve with anti-scald protection", "Built-in disinfection system", "Optional CleanRane air spa", "Optional auto-fill (24 gallons)", "Optional battery backup"],
        "extra": [("Occupant capacity", "450 lb"), ("Length reclined", "88 in."), ("Height with door raised", "78 in. at the lowest setting"),
                  ("Electrical", "115V AC, 60Hz, 15 amp"), ("Plumbing layouts", "Side, front or island configuration")],
        "rough": "Plan floor space for the 88 in. reclined length and overhead room for the 78 in. raised door.",
        "source": ("Rane RR7-II Atlantic brochure", "https://ezable.com/content/2014RaneBrochures/RR7-IIAtlanticBrochure.pdf"), "power": "yes"},
    "anzzi-value-3060": {"url": "anzzi-value-series-30x60-soaking",
        "extra": [("Wall finish", "Tile flange on the tub"), ("Faucet", "Quick Fill faucet with a 60 in. handheld shower")],
        "rough": "Order the drain side that matches the existing drain.", "source": ("ANZZI product listing, anzzi.com", "https://anzzi.com/products/azb3060lws")},
    "anzzi-coupe-premier-2853": {"url": "anzzi-coupe-premier-28x53-soaking", "ext": 7,
        "extra": [("Extension kit", "7 in. kit to fill a 60 in. alcove"), ("Comfort", "Water-resistant headrest pillow")],
        "rough": "Dry-fit the 7 in. extension before the tub is set, and plan the wall surround so water cannot get behind it.",
        "source": ("ANZZI walk-in tub listings, anzzi.com", "https://anzzi.com/collections/all?page=5")},
    "anzzi-value-3053": {"ext": 7, "extra": [("Extension kit", "7 in. kit for a 60 in. retrofit"), ("Wall finish", "Tile flange included"),
        ("Faucet", "Quick Fill faucet with a 60 in. handheld shower"), ("Dual therapy version", "AZB3053RWA: 6 whirlpool jets, 18 air jets, inline maintenance heater")],
        "source": ("ANZZI product listing, anzzi.com", "https://anzzi.com/products/azb3053-prx")},
    "anzzi-value-2646": {"L": 45.5, "W": 26, "H": 37.5, "ext": 14, "extra": [("Extension kit", "14 in. matching kit for a 60 in. retrofit"), ("Wall finish", "No tile flange"),
        ("Drain", "Cable-operated drain and overflow you can work while seated")],
        "rough": "The 14 in. extension kit is how this short tub closes a 60 in. alcove; with no tile flange, plan the surround.",
        "source": ("ANZZI product listing, anzzi.com", "https://anzzi.com/products/azb2646ws-prx")},
}

WARRANTY = {
    "hydro-dimensions": "Lifetime warranty on shell, frame, finish, door seal, motors and controls",
    "ellas-bubbles": "Lifetime on shell, frame and door gasket; 5 years on hardware and components; labor not covered by Ella",
    "meditub": "10 years on shell, frame and finish; 1 year on motors and controls; lifetime on the door seal; 90 days labor (register within 90 days)",
    "rane": "5 years on shell and external finishes; 3 years on parts; lifetime on the door seal with preventive maintenance",
    "anzzi": "Lifetime warranty on the door pressure seal; full terms in ANZZI's warranty document",
}
ORIGIN = {"hydro-dimensions": "Temecula, California, USA", "rane": "Sparta, Tennessee, USA", "ellas-bubbles": "", "meditub": "", "anzzi": ""}
BRAND_KEY = {"Hydro Dimensions": "hydro-dimensions", "Ella's Bubbles": "ellas-bubbles", "Meditub": "meditub", "ANZZI": "anzzi", "Rane (RANE by Bestbath)": "rane"}
BAD = re.compile(r"\b(ASB|Caring|verify|confirm|listing|nominal|not reviewed|sandbox|per existing|Best Company|dealer listing|unconfirmed)\b", re.I)


def clean(t):
    t = re.sub(r"\s*\([^)]*\)", lambda m: "" if BAD.search(m.group(0)) else m.group(0), t or "").strip()
    return t


def door_kind(s):
    s = (s or "").lower()
    if "outward" in s or "out-swing" in s or "outswing" in s:
        return "outward"
    if "upward" in s:
        return "upward"
    if "inward" in s or "inswing" in s:
        return "inward"
    return ""


def load():
    ext = {m["slug"]: m for m in json.load(open(os.path.join(HERE, "data", "asb-extract.json"), encoding="utf-8"))}
    cat = json.load(open(os.path.join(CATALOG, "products.json"), encoding="utf-8"))
    prods = []
    for c in cat:
        b = BRAND_KEY.get(c["brand"])
        st = c.get("status", "")
        if not b or not (st.startswith("current") or c["slug"] == "rane-rk12-winnipeg-6133"):
            continue
        if not c.get("width_in") or not c.get("length_in"):
            continue
        o = OVERLAY.get(c["slug"], {})
        asb_slug = (c.get("asb_url") or "").rstrip("/").split("/")[-1]
        a = ext.get(asb_slug, {})
        sp = a.get("specs", {})
        model = o.get("model") or c["model"]
        name = (P_NAME.get(b, BRANDS[b]["short"]) + " " + model) if b != "anzzi" else "ANZZI " + model
        door_src = c.get("door_type") or sp.get("Door", "")
        p = {"slug": o.get("url") or c["slug"], "cat_slug": c["slug"], "asb_slug": asb_slug, "brand": b, "model": model, "name": name,
             "series": o.get("series") or c.get("series") or "", "W": o.get("W") or num(c.get("width_in")), "L": o.get("L") or num(c.get("length_in")),
             "H": o.get("H") or num(c.get("height_in")), "cap": o.get("cap") or num(c.get("capacity_gallons")), "cap_note": o.get("cap_note", ""),
             "door": o.get("door") or door_kind(door_src), "door_note": o.get("door_note") or (clean(door_src)[:1].upper() + clean(door_src)[1:] if door_src else ""),
             "door_side": clean(c.get("door_side") or ""), "shell": o.get("shell") or clean(c.get("shell") or ""),
             "origin": ORIGIN[b], "warranty": WARRANTY[b],
             "seat_w": o.get("seat_w") or num(c.get("inside_seat_width_in")) or num(sp.get("Seat width")), "seat_d": num(c.get("seat_depth_in")) or num(sp.get("Seat depth")),
             "hip": num(c.get("max_seated_hip_width_in")) or num(sp.get("Max hip width (seated)")), "bather": c.get("bather_height_range") or sp.get("Bather height range", ""),
             "seat_h": o.get("seat_h") or num(c.get("seat_height_in")), "step": num(c.get("step_in_height_in")),
             "occupant": o.get("occupant") or num(c.get("weight_capacity_lb")), "ext": o.get("ext"),
             "packages": [x.strip() for x in sp.get("Therapy packages", "").split(",") if x.strip()],
             "therapy": o.get("therapy", []), "therapy_labels": [], "therapy_opts": c.get("therapy_options") or [],
             "skus": clean(c.get("skus") or ""), "extra": o.get("extra", []), "rough": o.get("rough", ""), "avail": o.get("avail", ""),
             "delivery_note": clean(c.get("delivery_note") or ""), "best_for": clean(c.get("best_for") or ""),
             "summary": c.get("summary") or "", "asb": c.get("asb_url") or "", "source": o.get("source"),
             "cat_imgs": [os.path.join(CATALOG, "img", x) for x in (c.get("images") or [])], "cat_alts": c.get("image_alt") or [],
             "schematic": [os.path.join(CATALOG, "img", x) for x in [c.get("schematic"), c.get("schematic_extra")] if isinstance(x, str) and x],
             "spec_pdf": os.path.join(CATALOG, c["spec_pdf"]) if c.get("spec_pdf") else "",
             "local_imgs": a.get("main_images", []) + [a.get("thumb", "")] if a else [], "schematics": [],
             "tags": c.get("category_tags", [])}
        if isinstance(c.get("schematic_extra"), list):
            p["schematic"] += [os.path.join(CATALOG, "img", x) for x in c["schematic_extra"]]
        ser = p["series"].lower()
        opts = [x.lower() for x in p["therapy_opts"]]
        p["two"] = "two seat" in ser or model.lower() in ("companion", "tub4two", "big4two", "escape")
        p["transfer"] = "transfer-wheelchair" in p["tags"] or any(k in ser for k in ("transfer", "wheelchair", "assisted")) or "wca" in model.lower() or "wheelchair" in model.lower()
        p["laydown"] = "lay down" in ser
        p["soaker"] = (opts and all(x in ("soaker", "inline heater") for x in opts)) or (not opts and not p["therapy"] and b == "anzzi")
        p["jets"] = any(x in opts for x in ("whirlpool", "combo", "foot jets")) or any("jet" in x.lower() or "whirlpool" in x.lower() for x in p["therapy"])
        p["air"] = any(x in opts for x in ("air", "combo", "microbubble")) or any("air" in x.lower() for x in p["therapy"])
        if o.get("power"):
            p["power"] = o["power"]
        elif p["soaker"]:
            p["power"] = "none"
        elif "soaker" in opts:
            p["power"] = "depends"
        else:
            p["power"] = "yes"
        if b == "anzzi":
            p["curbside"] = True
        if not p["asb"]:
            p["asb"] = ""
        p["summary_ok"] = p["summary"] if p["summary"] and not BAD.search(p["summary"]) else ""
        p["url"] = "/tubs/%s/" % p["slug"]
        prods.append(p)
    for p in prods:
        derive(p)
    order = {"hydro-dimensions": 0, "ellas-bubbles": 1, "meditub": 2, "rane": 3, "anzzi": 4}
    prods.sort(key=lambda p: (order[p["brand"]], p["W"] or 0, p["L"] or 0, p["model"]))
    return prods


P_NAME = {"hydro-dimensions": "Hydro Dimensions", "ellas-bubbles": "Ella's Bubbles", "meditub": "Meditub", "rane": "Rane"}


def derive(p):
    W, L = p["W"] or 0, p["L"] or 0
    p["wide"] = W >= 32 or (p["seat_w"] or 0) >= 24 or (p["occupant"] or 0) >= 450 or "wide-bariatric" in p.get("tags", [])
    p["small"] = 0 < L <= 48
    p["usa"] = p["brand"] == "rane"
    p["door_label"] = {"inward": "Inward swing", "outward": "Outward swing", "upward": "Lift-up door"}.get(p["door"], "Wide door")
    if L >= 59:
        p["alcove"] = "full"
    elif L >= 50:
        p["alcove"] = "short"
    else:
        p["alcove"] = "compact"
    p["size"] = "%s x %s in." % (fmt(p["W"]), fmt(p["L"])) if W and L else ""


# ---------- images ----------
def dhash(im, n=8):
    g = im.convert("L").resize((n + 1, n))
    px = list(g.getdata())
    bits = "".join("1" if px[r * (n + 1) + c] > px[r * (n + 1) + c + 1] else "0" for r in range(n) for c in range(n))
    return "%016x" % int(bits, 2)


def process_images(prods, out_root):
    """Copy local images into /assets/tubs/ as webp (max 1200 px, < 200 KB). Returns count."""
    from PIL import Image
    dst = os.path.join(out_root, "assets", "tubs")
    os.makedirs(dst, exist_ok=True)
    seen = {}
    n = 0
    for p in prods:
        gallery = []
        cands = []
        for i, x in enumerate(p.get("cat_imgs", [])):
            cands.append((x, "", "photo"))
        for x in p["local_imgs"]:
            if x:
                cands.append((ASB_SRC + x, "", "photo"))
        for x in p.get("schematic", []):
            cands.append((x, "", "drawing"))
        cands = [(a, b, "drawing" if ("schematic" in os.path.basename(a).lower() or "drawing" in os.path.basename(a).lower()) else c) for a, b, c in cands]
        cands.sort(key=lambda c: c[2] == "drawing")
        for path, alt, kind in cands:
            if not os.path.exists(path) or os.path.getsize(path) < 2500:
                continue
            try:
                im = Image.open(path)
                if im.width < 220 or im.height < 160:
                    continue
                h = dhash(im)
                if any(bin(int(h, 16) ^ int(g["hash"], 16)).count("1") <= 8 for g in gallery):
                    continue
                if h in seen:
                    fn, w, hh = seen[h]
                else:
                    im = im.convert("RGBA") if im.mode in ("P", "LA", "RGBA") else im.convert("RGB")
                    if im.mode == "RGBA":
                        bg = Image.new("RGB", im.size, (255, 255, 255)); bg.paste(im, mask=im.split()[3]); im = bg
                    if im.width > 1200:
                        im = im.resize((1200, round(im.height * 1200 / im.width)), Image.LANCZOS)
                    k = len([g for g in gallery]) + 1
                    fn = "%s-%s-%d.webp" % (p["slug"], "drawing" if kind == "drawing" else "walk-in-tub", k)
                    q = 82
                    while True:
                        im.save(os.path.join(dst, fn), "WEBP", quality=q, method=5)
                        if os.path.getsize(os.path.join(dst, fn)) < 200_000 or q <= 40:
                            break
                        q -= 10
                    w, hh = im.size
                    seen[h] = (fn, w, hh)
                    n += 1
                gallery.append({"src": "/assets/tubs/" + fn, "w": w, "h": hh, "kind": kind, "hash": h, "alt": alt})
            except Exception as e:
                print("img fail", path, e)
                continue
            if len(gallery) >= 8:
                break
        p["gallery"] = gallery
    return n
