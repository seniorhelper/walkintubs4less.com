# Pulls model facts (specs, image paths, therapy option names) from the local agingsafelybaths.com export.
# Only facts are kept; no ASB sentences are copied into the store copy.
import re, html, json, os, sys, glob
SRC = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/research/wt4l/asb"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "asb-extract.json")
prods = {p["u"]: p for p in json.load(open(os.path.join(SRC, "assets/products.json"))) if p.get("c") == "tub"}
def txt(s): return html.unescape(re.sub(r"<[^>]+>", " ", s)).replace("″", '"').strip()
out = []
for f in sorted(glob.glob(os.path.join(SRC, "walk-in-tubs/*/index.html"))):
    slug = f.split("/")[-2]
    s = open(f, encoding="utf-8").read()
    main = s[s.find("<main"):s.find("</main>")] if "<main" in s else s
    rows = {txt(k): re.sub(r"\s+", " ", txt(v)) for k, v in re.findall(r"<tr><th>(.*?)</th><td>(.*?)</td></tr>", main, re.S)}
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", main, re.S)
    imgs = []
    for tag in re.findall(r"<img\b[^>]*>", main):
        src = re.search(r'\ssrc="([^"]+)"', tag)
        if not src: continue
        src = src.group(1)
        if "logo" in src or "bbb.org" in src: continue
        fb = re.search(r'data-fb="([^"]*)"', tag)
        alt = re.search(r'alt="([^"]*)"', tag)
        imgs.append({"src": src, "fb": [x for x in (fb.group(1).split("|") if fb else []) if x], "alt": html.unescape(alt.group(1)) if alt else ""})
    # only the main-gallery images: stop at the "Related" block
    rel_at = main.find("Related ")
    main_imgs = []
    for tag in re.findall(r"<img\b[^>]*>", main[:rel_at if rel_at > 0 else len(main)]):
        m = re.search(r'\ssrc="([^"]+)"', tag)
        if m and "logo" not in m.group(1) and "bbb.org" not in m.group(1): main_imgs.append(m.group(1))
    # therapy option names from the upgrades list (bold labels only)
    up = re.search(r"Therapy and comfort upgrades</h2>(.*?)</(section|ul)>", main, re.S)
    ther = [txt(x).rstrip(":") for x in re.findall(r"<(?:b|strong)>(.*?)</(?:b|strong)>", up.group(1))] if up else []
    std = re.search(r"What comes standard on.*?</h2>\s*<p>(.*?)</p>", main, re.S)
    schem = sorted(set(re.findall(r'(/wp-content/uploads/(?:schematics|mfr|pdf)/[^"\s)]+)', main)))
    p = prods.get(f"/walk-in-tubs/{slug}/", {})
    out.append({"slug": slug, "h1": txt(h1.group(1)) if h1 else "", "specs": rows, "brand": p.get("b", ""),
                "name": p.get("n", ""), "w": p.get("w"), "l": p.get("l"), "seat": p.get("seat"), "door": p.get("door"),
                "tags": p.get("tags", []), "th": p.get("th", []), "thumb": p.get("t", ""), "img": p.get("i", ""),
                "images": imgs, "main_images": main_imgs, "therapy_labels": ther,
                "schematics": schem})
json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)
print(len(out), "models ->", OUT)
