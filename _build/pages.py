# Page bodies for walkintubs4less.com v2. Called from build.py with the build module as B.
import os, re, json, html

GUIDES_SRC = "/home/claude/research/wt4l/guides"
INSTALLED = "$15,250 to $20,000 after current promotions"


def esc(s):
    return html.escape(str(s), quote=True)


GUIDE_SLUGS = set()


def gl(slug, anchor):
    return '<a href="/guides/%s/">%s</a>' % (slug, esc(anchor)) if slug in GUIDE_SLUGS else esc(anchor)


# ======================= product copy =======================
def title_for(p):
    for t in ("Buy %s Walk-In Tub | Supply Only or Installed" % p["name"],
              "Buy %s | Supply Only or Installed" % p["name"],
              "%s Walk-In Tub for Sale" % p["name"]):
        if len(t) <= 70:
            return t
    return p["name"][:70]


def desc_for(p, B):
    bits = [p["size"].replace(" in.", " inches")] if p["size"] else []
    if p["door"]:
        bits.append(p["door_label"].lower() + " door")
    d = "Buy the %s (%s) shipped to you or fully installed by a factory-certified installer. Specs, delivery facts and a written price." % (p["name"], ", ".join(bits))
    if len(d) > 170:
        d = "Buy the %s shipped to you or fully installed. Specs, delivery facts, door and seat details, and a written price." % p["name"]
    if len(d) > 170:
        d = "Buy the %s shipped or installed. Specs, delivery facts and a written price." % p["name"]
    return d


def fit_sentence(p):
    L = p["L"]
    if not L:
        return ""
    f = B_.fmt(L)
    if p["alcove"] == "full" and L <= 61.5:
        return "At %s inches long it is sized for the common 60-inch alcove that a standard bathtub leaves behind." % f
    if p["alcove"] == "full":
        return "At %s inches long it needs more room than a standard 60-inch tub space, so it suits a larger bathroom, an open wall or a full remodel." % f
    if p["alcove"] == "short":
        if p.get("ext"):
            return "At %s inches long it sits short of a 60-inch alcove; the %s-inch extension kit closes the gap." % (f, B_.fmt(p["ext"]))
        return "At %s inches long it sits short of a 60-inch alcove, so the gap is closed with a filler panel or a short wall build-out, and your quote names which one." % f
    return "At %s inches long it is meant for small bathrooms and old shower spaces rather than a full tub alcove." % f


def door_sentence(p):
    return {
        "inward": "The door opens into the tub, so the water's weight helps press it against the gasket. The bather steps in past the open door, which works best for people who can stand and walk in on their own or with a cane.",
        "outward": "The door opens out into the room, which leaves the whole opening clear for a sideways slide from a wheelchair or a walker seat. Plan for open floor in front of the tub so the door can swing fully.",
        "upward": "The door lifts up instead of swinging, so the side of the tub opens for a seated transfer from a wheelchair or a patient lift.",
    }.get(p["door"], "The wide door closes on a pressure seal, and the door must be latched before the tub is filled.")


def suits(p):
    yes, no = [], []
    if p["seat_w"]:
        yes.append("A %s-inch-wide seat%s" % (B_.fmt(p["seat_w"]), (", with seated hip room to %s inches" % B_.fmt(p["hip"])) if p["hip"] else ""))
    if p["bather"]:
        yes.append("Bathers in the published height range of %s" % p["bather"])
    if p.get("seat_h"):
        yes.append("A seat %s inches off the floor%s" % (B_.fmt(p["seat_h"]), ", close to typical wheelchair seat height" if p["seat_h"] >= 19 else ""))
    if p.get("step"):
        yes.append("A %s-inch step-in threshold" % B_.fmt(p["step"]))
    if p["two"]:
        yes.append("Two people bathing together, or one bather plus a helper's reach")
    if p["transfer"]:
        yes.append("Seated transfers from a wheelchair, walker or lift")
    if p["wide"] and not p["seat_w"]:
        yes.append("Larger bathers: %s inches of outside width" % B_.fmt(p["W"]))
    if p["small"]:
        yes.append("Tight bathrooms where a 60-inch tub will not fit")
    if p.get("occupant"):
        yes.append("Bathers up to %s lb (the maker's occupant rating)" % B_.fmt(p["occupant"]))
    if p["soaker"]:
        yes.append("A deep soak with nothing to wire for jets")
    elif p["jets"] or p["air"]:
        yes.append("Massage: water jets, air jets or both, chosen at order time")
    if p.get("best_for"):
        yes.append(p["best_for"][0].upper() + p["best_for"][1:])
    if p["door"] == "outward":
        no.append("Rooms with no clear floor in front of the tub, because the door swings out")
    if p["door"] == "inward" and not p["transfer"]:
        no.append("Bathers who cannot stand to step in; an outward-door transfer model is the better match")
    if (p["W"] or 0) >= 32:
        no.append("Houses where every route to the bathroom is narrower than about %s inches, unless the crate can be tipped on edge" % B_.fmt((p["W"] or 0) + 2))
    if p["soaker"]:
        no.append("Anyone who wants massage jets")
    if (p["L"] or 0) > 61.5:
        no.append("A standard 60-inch alcove with no wall changes")
    if not no:
        no.append("Bathrooms you have not measured yet: send us the alcove, doorway and drain side first")
    return yes[:6], no[:3]


def therapy_list(p):
    out = []
    if p["packages"]:
        out += ["Package: " + x for x in p["packages"]]
    for x in p["therapy"] + p["therapy_labels"]:
        x = x[0].upper() + x[1:]
        if x not in out:
            out.append(x)
    names = {"soaker": "Soaker (no jets)", "whirlpool": "Whirlpool water jets", "air": "Air jets", "combo": "Combination water and air",
             "microbubble": "Microbubble therapy", "foot jets": "Foot and calf jets", "heated seat": "Heated seat and backrest",
             "inline heater": "Inline heater to hold water temperature", "chromatherapy": "Chromatherapy lighting", "aromatherapy": "Aromatherapy"}
    if p.get("therapy_opts"):
        out += [names.get(x, x[0].upper() + x[1:]) for x in p["therapy_opts"] if names.get(x, x) not in out]
    return out[:8]


STANDARD = {
    "hydro-dimensions": ["Low step-in door and a built-in contoured seat", "Angled grab bar inside the tub", "Chrome Roman faucet with a 5-foot handheld wand",
                         "Drain kit with overflow", "Textured, slip-resistant floor", "Faucet finish upgrades: oil-rubbed bronze or brushed nickel (extra cost)"],
    "ellas-bubbles": ["The door style shown, with a low threshold", "Molded, contoured seat", "Stainless steel grab bar and textured floor",
                      "Chrome faucet with a pull-out handheld shower", "Ella's 2-inch Dual Drain (Ella rates it at about 80 seconds to empty)"],
    "meditub": ["Built-in seat and a safety grab bar", "Low step-in door with a heavy-duty latch", "Textured floor", "Faucet set with an extendable handheld shower"],
    "rane": ["Factory-installed safety systems listed in the specs table", "Handheld shower", "Thermostatic mixing valve to limit water temperature"],
    "anzzi": ["Quick Fill faucet with a handheld shower on a 60-inch hose", "Built-in grab bar and slip-resistant floor", "Contoured seating and a low threshold",
              "Spec sheet, install guide, care guide and warranty from ANZZI"],
}


def spec_rows(p):
    f = B_.fmt
    r = [("Brand", B_.P.BRANDS[p["brand"]]["name"]), ("Model", p["model"])]
    if p["series"]: r.append(("Series", p["series"]))
    if p.get("skus"): r.append(("SKUs", p["skus"]))
    if p["W"] and p["L"]:
        r.append(("Outside size", "%s in. wide x %s in. long%s" % (f(p["W"]), f(p["L"]), (" x %s in. high" % f(p["H"])) if p["H"] else "")))
    r.append(("Door", p["door_note"] or p["door_label"]))
    if p.get("door_side"): r.append(("Door / drain side", p["door_side"]))
    if p.get("step"): r.append(("Step-in height", "%s in." % f(p["step"])))
    if p.get("seat_h"): r.append(("Seat height", "%s in. from the floor" % f(p["seat_h"])))
    if p["seat_w"]: r.append(("Seat width", "%s in." % f(p["seat_w"])))
    if p["seat_d"]: r.append(("Seat depth", "%s in." % f(p["seat_d"])))
    if p["hip"]: r.append(("Max hip width, seated", "%s in." % f(p["hip"])))
    if p["bather"]: r.append(("Bather height range", p["bather"]))
    if p["cap"]: r.append(("Water capacity", p["cap_note"] or "%s gallons (operating capacity)" % f(p["cap"])))
    if p["shell"]: r.append(("Shell", p["shell"]))
    if p["origin"]: r.append(("Made in", p["origin"]))
    r += p["extra"]
    if p["warranty"]: r.append(("Warranty", p["warranty"]))
    r.append(("Power needed", {"yes": "Yes: a dedicated GFCI-protected circuit (amperage on the spec sheet)", "none": "No circuit needed for a soaking build",
                               "depends": "Soaker version: none. Jetted, air or heated versions: a dedicated GFCI-protected circuit"}[p["power"]]))
    if p.get("avail"): r.append(("Availability", p["avail"]))
    return r


def faqs_for(p):
    f = B_.fmt
    n = p["name"]
    out = []
    if p["W"]:
        out.append(("Will the %s fit through my doorways?" % n,
                    "The shell is %s inches wide%s. Measure the narrowest door, hall turn and stair landing between the street and the bathroom. You want roughly %s inches clear at the tightest point, or enough room to tip the crate on edge. Send us the numbers and we confirm the route before anything ships."
                    % (f(p["W"]), (" and %s inches tall" % f(p["H"])) if p["H"] else "", f(p["W"] + 2))))
    if p["transfer"]:
        out.append(("Can a wheelchair user get into the %s?" % n,
                    "Yes, that is what it is built for. The %s door opens the side of the tub so the bather slides across from the chair to the seat instead of stepping over a wall.%s Tell us which side the bather transfers from so we order the right hand."
                    % (p["door_label"].lower(), (" The seat sits %s inches off the floor." % f(p["seat_h"])) if p.get("seat_h") else "")))
    elif p["two"]:
        out.append(("Do two people fit in the %s?" % n,
                    "It has two seats in a %s by %s inch shell, so two adults can bathe side by side. Many buyers also use the second seat as room for a caregiver to reach in. Check the hot water: a two-seat tub holds far more water than a standard bathtub." % (f(p["W"]), f(p["L"]))))
    elif p["cap"]:
        out.append(("How much hot water does the %s use?" % n,
                    "Plan on about %s gallons%s. You fill a walk-in after you sit down and close the door, so the water heater has to deliver most of that as hot water in one go. Tell us your heater size and we flag it on your quote if it looks short."
                    % (f(p["cap"]), (" (%s)" % p["cap_note"]) if p["cap_note"] else "")))
    out.append(("Can I buy the %s supply only?" % n,
                "Yes. It ships by freight to your curb or driveway%s and your own plumber or contractor sets it, with our phone tech support behind them. %s"
                % (" (ANZZI ships curbside only)" if p["brand"] == "anzzi" else "",
                   {"yes": "Because it runs jets, air or a heater, line up a licensed electrician for its dedicated circuit before delivery day.",
                    "none": "This soaking build needs no circuit, which keeps a self-managed install simpler.",
                    "depends": "The soaker version needs no power; jetted, air or heated versions need a dedicated circuit, so line up an electrician if you choose one."}[p["power"]])))
    if p["warranty"] and len(out) < 4:
        out.append(("What warranty comes with the %s?" % n,
                    "%s. We send the maker's warranty document with your written quote so you can read the exact terms, including what it expects from the installation." % p["warranty"].rstrip(".")))
    return out[:4]


def buybox(p, B):
    f = B.fmt
    quick = []
    if p["size"]: quick.append(("Size", p["size"]))
    quick.append(("Door", p["door_label"]))
    if p.get("seat_h"): quick.append(("Seat height", "%s in." % f(p["seat_h"])))
    elif p["seat_w"]: quick.append(("Seat width", "%s in." % f(p["seat_w"])))
    if p.get("step"): quick.append(("Step-in", "%s in." % f(p["step"])))
    elif p["cap"]: quick.append(("Capacity", "%s gal" % f(p["cap"])))
    if len(quick) < 4: quick.append(("Therapy", "Soaker" if p["soaker"] else ("Jets / air options" if (p["jets"] or p["air"]) else "Ask us")))
    dl = p["door_label"].lower()
    lead = "%s, %s. Shipped to you, or fully installed." % (p["size"] or "Walk-in tub", dl if dl.endswith("door") else dl + " door")
    return ('<div class="buybox"><p class="pill">%s</p><h1>%s Walk-In Tub</h1><p class="lead">%s</p>'
            '<fieldset class="choice" id="path-box"><legend>How do you want it?</legend>'
            '<label class="opt"><input type="radio" name="pathpick" value="supply" checked><span><b>Supply only (shipped to you)</b>Freight to your curb or driveway. Your installer, our tech support.</span></label>'
            '<label class="opt"><input type="radio" name="pathpick" value="installed"><span><b>Fully installed (factory-certified installer)</b>Old tub out, new tub in, in 1 day in most homes.</span></label>'
            '</fieldset>'
            '<div class="ctas"><a class="btn btn-quote" href="%s?path=supply" data-path-link="path-box">Get my price</a>%s</div>'
            '<ul class="quick mt14">%s</ul>'
            '<p class="src">No price is listed online: you get a written supply-only or installed price for this exact model.</p></div>') % (
        esc(B.P.BRANDS[p["brand"]]["name"]), esc(p["name"]), esc(lead), p["url"], B.call_btn(),
        "".join("<li>%s<b>%s</b></li>" % (esc(k), esc(v)) for k, v in quick[:4]))


def gallery(p, B):
    g = p.get("gallery", [])
    items = []
    for i, im in enumerate(g):
        alt = im.get("alt") or ("%s, %s" % (p["name"], "factory drawing with dimensions" if im["kind"] == "drawing" else "maker's product photo"))
        tag = '<img src="%s" width="%d" height="%d" alt="%s"%s decoding="async">' % (im["src"], im["w"], im["h"], esc(alt), "" if i == 0 else ' loading="lazy"')
        items.append((tag, alt))
    items.append((B.drawing_svg(p), "%s top view drawn to scale from its published size" % p["name"]))
    main = items[0][0].replace(' loading="lazy"', '')
    thumbs = ""
    if len(items) > 1:
        thumbs = '<div class="thumbs" role="group" aria-label="Choose a picture">%s</div>' % "".join(
            '<button type="button" aria-pressed="%s" aria-label="Show picture %d of %d" data-cap="%s">%s<template>%s</template></button>'
            % ("true" if i == 0 else "false", i + 1, len(items), esc(c), re.sub(r'<title>.*?</desc>', '', t.replace('role="img"', 'aria-hidden="true"')).replace('loading="lazy" ', '').replace(' decoding="async"', ' loading="lazy"'), t.replace(' loading="lazy"', ''))
            for i, (t, c) in enumerate(items))
    return '<div class="gal"><div class="gal-main">%s</div><p class="cap">%s</p>%s</div>' % (main, esc(items[0][1]), thumbs)


def price_form(p=None, B=None, heading="Get your written price", ctx="product"):
    tub_field = ('<input type="hidden" name="tub" value="%s"><input type="hidden" name="tub_page" value="%s">' % (esc(p["model"] + " (" + p["name"] + ")"), esc(p["url"]))) if p else ""
    tub_select = ""
    if not p:
        groups = []
        for k in B.BRAND_ORDER:
            opts = "".join('<option value="%s">%s</option>' % (esc(x["model"]), esc(x["name"])) for x in B.ALL if x["brand"] == k)
            groups.append('<optgroup label="%s">%s</optgroup>' % (esc(B.P.BRANDS[k]["name"]), opts))
        tub_select = ('<div><label for="f-tub">Tub</label><select id="f-tub" name="tub"><option value="">Help me choose</option>%s'
                      '<option value="Other model">Another model (tell us below)</option></select></div>') % "".join(groups)
    return ('<form class="form card" id="price-form" data-lead action="%s" method="post" novalidate aria-label="Walk-in tub price request">'
            '<h2 class="h-form">%s</h2>'
            '<fieldset class="choice"><legend>Price it as</legend>'
            '<label class="opt"><input type="radio" name="path" id="p-supply" data-key="supply" value="Supply only (shipped to you)" checked><span><b>Supply only</b>Shipped to you or your installer</span></label>'
            '<label class="opt"><input type="radio" name="path" id="p-inst" data-key="installed" value="Fully installed (factory-certified installer)"><span><b>Fully installed</b>Factory-certified installer, old tub hauled away</span></label>'
            '<label class="opt"><input type="radio" name="path" id="p-both" data-key="both" value="Price both"><span><b>Price both</b>So I can compare</span></label>'
            '</fieldset>%s'
            '<div class="row"><div><label for="f-name">Full name</label><input id="f-name" name="name" autocomplete="name" maxlength="80" required></div>'
            '<div><label for="f-phone">Phone</label><input id="f-phone" name="phone" type="tel" autocomplete="tel" maxlength="30" required></div></div>'
            '<div class="row"><div><label for="f-zip">ZIP code (or Canadian postal code)</label><input id="f-zip" name="zip" autocomplete="postal-code" maxlength="10" required></div>'
            '<div><label for="f-email">Email (optional)</label><input id="f-email" name="email" type="email" autocomplete="email" maxlength="200"></div></div>%s'
            '<div><label for="f-notes">Anything we should know? (optional)</label><textarea id="f-notes" name="notes" rows="3" maxlength="1500" placeholder="Bathroom size, doorway width, who is bathing, wheelchair or walker"></textarea></div>'
            '<div class="hp" aria-hidden="true"><label for="f-hp">Leave this empty</label><input id="f-hp" name="_honey" tabindex="-1" autocomplete="off"></div>'
            '<input type="hidden" name="_subject" value="New walk-in tub price request - walkintubs4less">'
            '<input type="hidden" name="form" value="wt4l-%s">%s'
            '<label class="consent"><input type="checkbox" name="consent" value="yes" required><span>I agree that Walk-In Tubs 4 Less and Aging Safely Baths may contact me about this request by phone, text or email at the number and address I gave, including by automated means. Consent is not a condition of buying. Message and data rates may apply. Reply STOP to opt out of texts. See our <a href="/privacy/">privacy policy</a>.</span></label>'
            '<p class="err" role="alert" hidden></p>'
            '<button class="btn btn-quote full" type="submit">Send my price request</button>'
            '<p class="src m0">Prefer to talk? Call <a href="tel:%s">%s</a>, 7am to 8pm Mountain, 7 days.</p>'
            '</form>') % (B.LEAD, esc(heading), tub_field if p else "", tub_select, ctx, "", B.TEL, B.PHONE)


def related(p, B):
    same = [x for x in B.ALL if x["brand"] == p["brand"] and x["slug"] != p["slug"]]
    key = lambda x: abs((x["W"] or 0) - (p["W"] or 0)) * 2 + abs((x["L"] or 0) - (p["L"] or 0)) + (0 if x["transfer"] == p["transfer"] else 6)
    rel = sorted(same, key=key)[:4]
    if len(rel) < 4:
        rel += sorted([x for x in B.ALL if x["brand"] != p["brand"]], key=key)[:4 - len(rel)]
    return rel


def product_page(p, B):
    f = B.fmt
    yes, no = suits(p)
    ther = therapy_list(p)
    std = STANDARD.get(p["brand"], [])
    faqs = faqs_for(p)
    intro = " ".join(x for x in [
        "The %s is a %s walk-in tub from %s%s." % (p["name"], ("%s by %s inch" % (f(p["W"]), f(p["L"]))) if p["W"] else "", B.P.BRANDS[p["brand"]]["name"], (", " + p["series"]) if p["series"] and p["series"] not in p["name"] else ""),
        fit_sentence(p), door_sentence(p)] if x)
    summ = p.get("summary_ok", "")
    asb_line = ""
    if p["asb"]:
        asb_line = ('<p>Comparing this model against the rest of the range? Aging Safely Baths keeps <a href="%s" rel="nofollow">the %s full specs and installation guide</a>, written for installers and planners.</p>'
                    % (esc(p["asb"]), esc(p["model"])))
    pdf = ""
    if p.get("spec_pdf") and os.path.exists(p["spec_pdf"]):
        p["pdf_local"] = "/assets/spec/%s-spec-sheet.pdf" % p["slug"]
        B.EXTRA_BIN[p["pdf_local"].lstrip("/")] = p["spec_pdf"]
    if p.get("pdf_local"):
        pdf = '<p><a class="btn btn-line" href="%s">Download the %s spec sheet (PDF)</a></p>' % (p["pdf_local"], esc(p["model"]))
    src = ""
    if p.get("source"):
        src = '<p class="src">Specs: <a href="%s" rel="nofollow noopener">%s</a>. Checked November 2026.</p>' % (esc(p["source"][1]), esc(p["source"][0]))
    else:
        src = '<p class="src">Specs: %s published spec sheets and factory drawings, checked November 2026. Makers change details; your written quote confirms the exact model.</p>' % esc(B.P.BRANDS[p["brand"]]["name"])
    supply_pts = ["Ships by freight truck to your curb or driveway%s." % (" (ANZZI delivers curbside only)" if p["brand"] == "anzzi" else ""),
                  "Inspect the crate with the driver and note any damage before you sign.",
                  "You arrange carry-in, removal of the old tub and the install." ,
                  {"yes": "A licensed electrician runs the dedicated circuit for the jets, air or heater.", "none": "Soaking build: there is no jet or heater circuit to run.",
                   "depends": "Soaker version: no circuit. Jets, air or heater: a licensed electrician runs a dedicated circuit."}[p["power"]],
                  "Phone tech support for whoever installs it, at no charge."]
    inst_pts = ["A factory-certified tech does a full site visit before install: doorways, drain side, water heater, power.",
                "Old tub and surround removed and hauled away.",
                "Tub set level, plumbed, sealed%s and test-filled." % (", wired" if p["power"] != "none" else ""),
                "Done in 1 day in most homes, with a walkthrough of every control.",
                "Installed walk-in tub jobs run %s, itemized in writing." % INSTALLED]
    deliv = []
    if p["W"]:
        deliv.append("<b>Carry-in width:</b> the shell is %s in. wide%s; the crate adds a little. Measure the tightest door, hall turn and stair landing." % (f(p["W"]), (" and %s in. tall" % f(p["H"])) if p["H"] else ""))
    if p["cap"]:
        deliv.append("<b>Hot water:</b> about %s gallons. Compare that with your water heater before delivery day." % f(p["cap"]))
    if p["power"] != "none":
        deliv.append("<b>Electrical:</b> jets, air and inline heaters run on a dedicated GFCI-protected circuit; amperage is on the spec sheet.")
    if p.get("rough"):
        deliv.append("<b>Rough-in:</b> %s" % esc(p["rough"]))
    if p.get("delivery_note"):
        deliv.append("<b>Delivery:</b> %s" % esc(p["delivery_note"]))
    deliv.append("<b>Lead time and freight:</b> confirmed on your written quote. Call to confirm current availability.")
    deliv.append("<b>Canada:</b> supply only, with freight quoted to your postal code.")
    rel = related(p, B)
    body = ('<div class="wrap"><div class="pd">%s%s</div></div>'
            '<section class="sec alt"><div class="wrap two-col"><div>'
            '<h2>%s at a glance</h2><p>%s</p>%s'
            '<div class="tbl-plain"><table class="specs"><caption class="vh">%s specifications</caption><tbody>%s</tbody></table></div>%s%s%s</div>'
            '<aside><div class="card"><h3>Good fit for</h3><ul class="checks">%s</ul><h3>Think twice if</h3><ul class="dots">%s</ul></div>'
            '%s%s</aside></div></section>'
            '<section class="sec"><div class="wrap"><h2>Supply only or fully installed: what changes for this tub</h2>'
            '<div class="grid g2"><div class="card"><h3>Supply only (shipped to you)</h3><ul class="checks">%s</ul><a class="btn btn-line" href="/supply-only/">How supply only works</a></div>'
            '<div class="card"><h3>Fully installed (factory-certified installer)</h3><ul class="checks">%s</ul><a class="btn btn-line" href="/white-glove/">What a full install includes</a></div></div>'
            '<h3 class="mt28">Delivery and fit facts for the %s</h3><ul class="dots">%s</ul>'
            '<p>Before you order, read %s and hand your installer %s.</p></div></section>'
            '<section class="sec alt"><div class="wrap two-col"><div>%s</div><div>%s</div></div></section>'
            '<section class="sec"><div class="wrap"><div class="sec-h"><h2>Similar tubs</h2><a href="/compare/?m=%s">Compare these side by side</a></div><div class="pgrid">%s</div></div></section>'
            ) % (
        gallery(p, B), buybox(p, B),
        esc(p["name"]), esc(intro), ('<p>%s</p>' % esc(summ)) if summ else "",
        esc(p["name"]), "".join('<tr><th scope="row">%s</th><td>%s</td></tr>' % (esc(k), esc(v)) for k, v in spec_rows(p)),
        asb_line, pdf, src,
        "".join("<li>%s</li>" % esc(x) for x in yes), "".join("<li>%s</li>" % esc(x) for x in no),
        ('<div class="card mt16"><h3>What comes standard</h3><ul class="checks">%s</ul></div>' % "".join("<li>%s</li>" % esc(x) for x in std)) if std else "",
        ('<div class="card mt16"><h3>Therapy and comfort options</h3><ul class="dots">%s</ul><p class="src">Jets and heaters are built in at the factory, so pick them when you order.</p></div>' % "".join("<li>%s</li>" % esc(x) for x in ther)) if ther else "",
        "".join("<li>%s</li>" % esc(x) for x in supply_pts), "".join("<li>%s</li>" % esc(x) for x in inst_pts),
        esc(p["model"]), "".join("<li>%s</li>" % x for x in deliv),
        gl("walk-in-tub-delivery-will-it-fit", "our guide to measuring the path in"), gl("walk-in-tub-rough-in-specs", "the rough-in and spec sheet guide"),
        price_form(p, B, "Price the %s" % p["model"]), B.faq_html(faqs, "%s questions" % p["model"]),
        ",".join([p["slug"]] + [x["slug"] for x in rel[:2]]), "".join(B.card(x) for x in rel))
    imgs = [B.DOMAIN + im["src"] for im in p.get("gallery", [])][:6]
    prod = {"@type": "Product", "@id": B.DOMAIN + p["url"] + "#product", "name": p["name"] + " Walk-In Tub",
            "brand": {"@type": "Brand", "name": B.P.BRANDS[p["brand"]]["name"]}, "model": p["model"], "category": "Walk-in bathtub",
            "description": B.strip(intro)[:300], "url": B.DOMAIN + p["url"]}
    if imgs: prod["image"] = imgs
    if p.get("skus"): prod["sku"] = p["model"]
    props = []
    if p["W"]: props.append({"@type": "PropertyValue", "name": "Width", "value": p["W"], "unitCode": "INH"})
    if p["L"]: props.append({"@type": "PropertyValue", "name": "Length", "value": p["L"], "unitCode": "INH"})
    if p["H"]: props.append({"@type": "PropertyValue", "name": "Height", "value": p["H"], "unitCode": "INH"})
    props.append({"@type": "PropertyValue", "name": "Door", "value": p["door_label"]})
    if p.get("seat_h"): props.append({"@type": "PropertyValue", "name": "Seat height", "value": p["seat_h"], "unitCode": "INH"})
    if p.get("step"): props.append({"@type": "PropertyValue", "name": "Step-in height", "value": p["step"], "unitCode": "INH"})
    if p["cap"]: props.append({"@type": "PropertyValue", "name": "Water capacity", "value": p["cap"], "unitText": "US gallons"})
    prod["additionalProperty"] = props
    trail = [("Walk-in tubs", "/walk-in-tubs/"), (B.P.BRANDS[p["brand"]]["name"], "/brands/%s/" % p["brand"]), (p["model"], p["url"])]
    B.page(p["url"].strip("/") + "/", title_for(p), desc_for(p, B), body, trail=trail,
           ld=[prod, B.faq_ld(faqs)], og_img=imgs[0] if imgs else None)
    return faqs, intro


# ======================= collection =======================
def collection(B, prods):
    def box(name, legend, opts):
        return '<fieldset><legend>%s</legend>%s</fieldset>' % (esc(legend), "".join(
            '<label><input type="checkbox" name="%s" value="%s"> %s <span class="src">(%d)</span></label>' % (name, v, esc(l), c) for v, l, c in opts if c))
    cnt = lambda fn: sum(1 for p in prods if fn(p))
    brands = [(k, B.P.BRANDS[k]["name"], cnt(lambda p, k=k: p["brand"] == k)) for k in B.BRAND_ORDER]
    needs = [(k, n, cnt(lambda p, k=k: k in B.needs_of(p))) for k, n, _, _ in B.NEEDS] + [("soaker", "Soaker (no jets)", cnt(lambda p: "soaker" in B.needs_of(p)))]
    widths = [("u28", "Under 28 in.", cnt(lambda p: B.wbucket(p) == "u28")), ("w28", "28 to 31.9 in.", cnt(lambda p: B.wbucket(p) == "w28")), ("w32", "32 in. and wider", cnt(lambda p: B.wbucket(p) == "w32"))]
    lengths = [("compact", "Under 50 in. (small rooms)", cnt(lambda p: p["alcove"] == "compact")), ("short", "50 to 58.9 in.", cnt(lambda p: p["alcove"] == "short")), ("full", "59 in. and longer", cnt(lambda p: p["alcove"] == "full"))]
    doors = [("inward", "Inward swing", cnt(lambda p: p["door"] == "inward")), ("outward", "Outward swing", cnt(lambda p: p["door"] == "outward")), ("upward", "Lift-up door", cnt(lambda p: p["door"] == "upward")), ("other", "Wide door (ANZZI)", cnt(lambda p: not p["door"]))]
    seats = [("s24", "24 in. or wider", cnt(lambda p: B.seat_bucket(p) == "s24")), ("s22", "22 to 23.9 in.", cnt(lambda p: B.seat_bucket(p) == "s22")), ("s20", "Under 22 in.", cnt(lambda p: B.seat_bucket(p) == "s20"))]
    filt = ('<aside class="filters closed" id="filters" aria-label="Filter tubs"><button class="btn btn-line f-toggle" type="button" aria-expanded="false" aria-controls="f-body">Filter tubs</button>'
            '<div class="f-body" id="f-body"><div class="f-top"><span class="f-count" id="f-count" aria-live="polite">%d tubs</span><button type="button" class="f-reset">Clear all</button></div>'
            '%s%s%s%s%s%s<p class="src">Seat width is shown where the maker publishes it.</p></div></aside>') % (
        len(prods), box("need", "Shop by need", needs), box("brand", "Brand", brands), box("width", "Outside width", widths),
        box("length", "Length", lengths), box("door", "Door", doors), box("seat", "Seat width", seats))
    body = ('<section class="hero sm"><div class="wrap"><div><p class="eyebrow">%d models &middot; 5 makers</p><h1>Walk-In Tubs for Sale: Every Model We Ship or Install</h1>'
            '<p class="lead">Filter by size, door, seat and need. Every tub can be shipped or fully installed.</p><div class="ctas">%s%s</div></div></div></section>%s'
            '<section class="sec"><div class="wrap shop">%s<div><div class="pgrid" id="tub-grid">%s</div><div class="empty" id="f-empty" hidden><p><b>No tub matches every filter.</b> Clear one or two, or call us: we can often order sizes and door hands that are not shown here.</p></div></div></div></section>'
            '<section class="sec alt"><div class="wrap narrow prose"><h2>How to narrow it down fast</h2>'
            '<p>Start with the room, then the bather. Measure the alcove wall to wall and the tightest doorway on the way in; that removes most of the list. Then pick the door: inward doors suit people who can stand and step in, while outward and lift-up doors open the side of the tub for a seated transfer. Finally choose the therapy: a soaker is simplest, while water jets, air jets and heaters add comfort and a dedicated circuit.</p>'
            '<p>Still between two or three? Put them in the <a href="/compare/">compare tool</a>, check the <a href="/specs/">specs and rough-in table</a>, or run your numbers through the <a href="/planner/">fit planner</a>. Weighing a big-box listing against a dealer? Read %s.</p></div></section>%s') % (
        len(prods), B.call_btn(), B.quote_btn(), B.trust_bar(), filt, "".join(B.card(p) for p in prods),
        gl("home-depot-lowes-costco-walk-in-tubs", "Home Depot, Lowe's and Costco walk-in tubs versus a dealer"), B.band())
    il = {"@type": "ItemList", "name": "Walk-in tubs for sale", "numberOfItems": len(prods),
          "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": B.DOMAIN + p["url"], "name": p["name"]} for i, p in enumerate(prods)]}
    B.page("walk-in-tubs/", "Walk-In Tubs for Sale: %d Models, Shipped or Installed" % len(prods),
           "Shop %d walk-in tubs from Hydro Dimensions, Ella's Bubbles, Meditub, Rane and ANZZI. Filter by size, door and seat, then buy supply only or installed." % len(prods),
           body, trail=[("Walk-in tubs", "/walk-in-tubs/")], ld=[il])


# ======================= brands =======================
BRAND_COPY = {
    "hydro-dimensions": {
        "title": "Buy Hydro Dimensions Walk-In Tubs | Supply Only or Installed",
        "desc": "Hydro Dimensions walk-in tubs for sale: every size we carry, lifetime coverage on the whole tub, and a choice of supply only or fully installed.",
        "h1": "Hydro Dimensions Walk-In Tubs for Sale", "lead": "The best-value warranty we sell, in sizes for real bathrooms.",
        "best": "Best value for most buyers. Hydro Dimensions publishes a lifetime warranty covering the shell, frame, finish, door seal, motors and controls, which is the broadest coverage across the brands we carry. Tubs are built in Temecula, California, in gel-coat fiberglass, and most models use an inward door.",
        "body": "<h2>Why Hydro Dimensions is our value pick</h2><p>When a family asks which tub gives the most protection for the money, this is the brand we point to first. The warranty covers the whole tub, motors and controls included, rather than the shell alone. Sizes run from compact 26-inch-wide models for small rooms up to the 35.5-inch-wide 3555 Plus, and every model can be ordered as a soaker or with water jets, air jets or both.</p>"
                "<h2>How Hydro Dimensions is organized</h2><p>Model numbers follow width and length: a 3052 is about 30 by 52 inches. The standard HD Series covers the everyday sizes; the Specialty Series adds outward-door W models for transfers, deeper D models and the wide 3555 Plus. Most HD tubs use an inward door, so look at the 3052W or 3252W if the bather transfers from a chair.</p>"
                "<h2>Buying Hydro Dimensions supply only</h2><p>HD tubs are built to order, so lead time is confirmed on your quote. Soaking builds are the simplest self-managed installs; jetted and heated builds need a dedicated circuit. Every supply-only order includes our phone tech support for your installer.</p>",
        "faq": [("Are Hydro Dimensions walk-in tubs made in the USA?", "Hydro Dimensions builds its tubs in Temecula, California. Rane by Bestbath is the line we sell that is fully made in the USA from its own plant in Sparta, Tennessee."),
                ("What does the Hydro Dimensions warranty cover?", "Hydro Dimensions publishes a lifetime warranty on the shell, frame, finish, door seal, motors and controls. We send the current warranty document with your written quote so you can read the exact terms.")]},
    "ellas-bubbles": {
        "title": "Buy Ella's Bubbles Walk-In Tubs | Supply Only or Installed",
        "desc": "Ella's Bubbles walk-in tubs for sale: transfer doors, two-seat, lay-down and wide models. Shipped to you or fully installed, with a written price.",
        "h1": "Ella's Bubbles Walk-In Tubs for Sale", "lead": "The widest lineup we carry: transfer, two-seat and lay-down tubs.",
        "best": "Best for specific bodies and specific needs. Ella's Bubbles has the most door styles and shapes we sell: L-shaped wheelchair transfer doors, U-shaped outswing doors, two-seat tubs, lay-down tubs and widths up to 36 inches. Tubs are acrylic with fiberglass reinforcement from a Chicago-based maker, with lifetime coverage on the shell, frame and door gasket.",
        "body": "<h2>When Ella's Bubbles is the right call</h2><p>If the bather uses a wheelchair, is tall, is a larger adult, or wants to lie back rather than sit upright, Ella usually has a shape that fits. The Transfer series lines its L-shaped door up with the seat for a sideways move from a chair. The Big4One, ShaK and Big4Two are built for bigger and taller bathers, and the Lay Down tubs let you recline.</p>"
                "<h2>Reading Ella's published fit data</h2><p>Ella publishes seat width, seat depth, maximum seated hip width and a bather height range for most models. Those four numbers are the best way to match a tub to a body, and they are on each model page here.</p>"
                "<h2>Buying Ella supply only</h2><p>Larger Ella tubs need a wider route into the bathroom and, for outswing doors, clear floor in front of the tub. We confirm both before anything ships.</p>",
        "faq": [("What does the Ella's Bubbles warranty cover?", "Ella's warranty document lists lifetime coverage on the shell, frame and door gasket and 5 years on hardware and components. Ella does not pay labor, so the installer's own labor warranty matters; we explain ours on your quote."),
                ("Which Ella tub is best for a wheelchair user?", "Start with the Transfer series (Transfer26, Transfer30, Transfer32, Transfer60 and TransferXXL). Their L-shaped outward doors open the side of the tub at seat level. Tell us the bather's side of transfer and we order the right door hand.")]},
    "meditub": {
        "title": "Buy Meditub Walk-In Tubs | Supply Only or Installed",
        "desc": "Meditub walk-in tubs for sale in sizes from 26 x 46 to 36 x 60, including wheelchair-access WCA models. Supply only or fully installed.",
        "h1": "Meditub Walk-In Tubs for Sale", "lead": "A size for almost any footprint, from 26 x 46 to 36 x 60.",
        "best": "Best for matching an exact footprint. Meditub model numbers are the tub's size, and the range covers compact front-entry tubs, standard 30 by 60 alcove tubs, a 36-inch-wide model and WCA wheelchair-access versions with outward doors. Meditub's manual lists 10 years on the shell, frame and finish, 1 year on motors and controls, and lifetime coverage on the door seal.",
        "body": "<h2>Why buyers pick Meditub</h2><p>When the space is unusual, Meditub often has the size. Short front-entry models such as the 2739, 3140 and 3238 fit rooms where a long tub never could, while the 3660 gives a 36-inch-wide bathing well for larger bathers. Shells are acrylic, and fiberglass versions are also made.</p>"
                "<h2>WCA models for wheelchair users</h2><p>The WCA suffix marks Meditub's wheelchair-access tubs. The 2953WCA and 3060WCA use outward doors so the bather can transfer across from a chair.</p>"
                "<h2>Buying Meditub supply only</h2><p>Soaker builds are simple to set; air, hydro and dual therapy builds need a dedicated circuit. We confirm the drain side and door hand on your quote.</p>",
        "faq": [("What do Meditub model numbers mean?", "The digits are the approximate width and length in inches, so a 3060 is about 30 by 60. The exact outside size is on each model page."),
                ("Does Meditub make a wheelchair-accessible walk-in tub?", "Yes. Models ending in WCA, such as the 2953WCA and 3060WCA, are wheelchair-access versions with outward-swinging doors.")]},
    "rane": {
        "title": "Rane Walk-In Tubs by Bestbath: Made in USA | Buy or Installed",
        "desc": "Rane walk-in and transfer tubs by Bestbath, made in Sparta, Tennessee. Healthcare-grade features, high weight ratings, shipped or installed.",
        "h1": "Rane by Bestbath: Made-in-USA Walk-In Tubs", "lead": "The only fully made-in-USA line we sell. Built for transfers.",
        "best": "Best for wheelchair users, lifts and heavier daily use. Rane by Bestbath is the only line we sell that is fully made in the USA, built in Sparta, Tennessee. Its tubs come from healthcare bathing, so features such as thermostatic mixing valves, built-in disinfection and high occupant ratings (600 lb on the RK12 Winnipeg) carry into the home models.",
        "body": "<h2>Who should look at Rane</h2><p>Rane makes sense when the bather transfers from a wheelchair or a lift, when more than one person in the home uses the tub, or when a caregiver runs the bath. The RK12 Winnipeg uses an outward door and a 600 lb occupant rating; the RR7 Atlantic uses a lift-up door and a reclining seat. Both are heavy, engineered pieces, so most homes choose a full install.</p>"
                "<h2>Built to plumbing and hydromassage standards</h2><p>Rane's sheets list CSA B45.5 / ANSI Z124 for plastic plumbing fixtures, ASME A112.19.7M for whirlpool bathtub appliances, ASME A112.19.8M for suction fittings and UL 1795 for hydromassage bathtubs.</p>"
                "<h2>More Rane models</h2><p>Rane also builds residential tubs beyond the two we list in detail. Ask us for a specific Rane model by name and we confirm its current specs with Bestbath before quoting.</p>",
        "faq": [("Where are Rane walk-in tubs made?", "In Sparta, Tennessee, by Rane Bathing Systems, part of Bestbath. It is the only line we sell that is fully made in the USA."),
                ("Are Rane tubs good for wheelchair users?", "Yes. The RK12 Winnipeg uses an outward-swinging door and the RR7 Atlantic a lift-up door, both designed for seated transfers from a wheelchair, walker or lift.")]},
    "anzzi": {
        "title": "Buy ANZZI Walk-In Tubs | Value Series and Coupe, Shipped or Installed",
        "desc": "ANZZI walk-in tubs for sale: Value Series and Coupe Premier soakers and dual-therapy tubs. Our lowest-cost line, shipped curbside or fully installed.",
        "h1": "ANZZI Walk-In Tubs for Sale", "lead": "Our lowest-cost walk-ins. Ships curbside, or we install it.",
        "best": "Best for a tight budget and a handy installer. ANZZI is the lowest-cost line we carry. Its Value Series and Coupe Premier tubs include a Quick Fill faucet, a handheld shower and a lifetime warranty on the door's pressure seal, and the shorter models ship with extension kits for a 60-inch alcove. ANZZI freight is curbside only.",
        "body": "<h2>What you get with ANZZI</h2><p>ANZZI keeps the core safety features (low threshold, grab bar, slip-resistant floor, contoured seat) and keeps the price down. Soakers need no electrical work at all; the dual-therapy 30 x 53 adds 6 whirlpool jets, 18 air jets and an inline heater, and needs a circuit.</p>"
                "<h2>The curbside catch</h2><p>ANZZI's carrier unloads the tub at the curb and leaves. That is fine with two strong helpers and an installer lined up. If not, choose a full install and we bring it in, set it and haul the old tub away.</p>"
                "<h2>Extension kits explained</h2><p>Short ANZZI models ship with matching extension kits (7 inches on the 53-inch tubs, 14 inches on the 26 x 46) so the tub fills a standard 60-inch alcove.</p>",
        "faq": [("Are ANZZI walk-in tubs good?", "They are a value line: the core safety features and a lifetime-warranted door seal at a lower price than most makers. The trade-off is more of the install on you, which is where our tech support helps."),
                ("Do ANZZI walk-in tubs fit a 60-inch bathtub space?", "The 30 x 60 fits directly. The 53-inch models use a 7-inch extension kit, and the 26 x 46 uses a 14-inch kit, to fill a 60-inch alcove.")]},
}


def brand_hub(k, B, prods):
    c = BRAND_COPY[k]
    mine = [p for p in prods if p["brand"] == k]
    hub = B.P.BRANDS[k]["asb_hub"]
    up = ('<p>Want every %s model compared on one page, with installation notes? Aging Safely Baths keeps <a href="%s" rel="nofollow">a full %s model comparison</a>.</p>'
          % (esc(B.P.BRANDS[k]["name"]), hub, esc(B.P.BRANDS[k]["short"]))) if hub else ""
    hero_img = next((first for first in (B.first_img(p) for p in mine) if first and first["kind"] == "photo"), None)
    media = ('<div class="hero-media"><img src="%s" width="%d" height="%d" alt="%s walk-in tub" fetchpriority="high"></div>' % (hero_img["src"], hero_img["w"], hero_img["h"], esc(B.P.BRANDS[k]["name"]))) if hero_img else ""
    body = ('<section class="hero"><div class="wrap"><div><p class="eyebrow">%d models in stock to quote</p><h1>%s</h1><p class="lead">%s</p><div class="ctas">%s%s</div></div>%s</div></section>%s'
            '<section class="sec"><div class="wrap"><div class="note"><b>Honest take:</b> %s</div></div></section>'
            '<section class="sec alt"><div class="wrap"><div class="sec-h"><h2>Every %s tub we sell</h2><a href="/walk-in-tubs/#brand=%s">Filter these with other brands</a></div><div class="pgrid">%s</div></div></section>'
            '<section class="sec"><div class="wrap narrow prose">%s%s<p>Buying from a store or a dealer? Compare the options in %s, and check %s before delivery day.</p>%s</div></section>%s') % (
        len(mine), esc(c["h1"]), esc(c["lead"]), B.call_btn(), B.quote_btn(), media, B.trust_bar(), esc(c["best"]),
        esc(B.P.BRANDS[k]["short"]), k, "".join(B.card(p) for p in mine), c["body"], up,
        gl("home-depot-lowes-costco-walk-in-tubs", "our big-box versus dealer guide"), gl("walk-in-tub-delivery-will-it-fit", "whether the tub fits through your doors"),
        B.faq_html(c["faq"]), B.band())
    il = {"@type": "ItemList", "name": B.P.BRANDS[k]["name"] + " walk-in tubs",
          "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": B.DOMAIN + p["url"], "name": p["name"]} for i, p in enumerate(mine)]}
    B.page("brands/%s/" % k, c["title"], c["desc"], body, trail=[("Brands", "/brands/"), (B.P.BRANDS[k]["name"], "/brands/%s/" % k)], ld=[il, B.faq_ld(c["faq"])])


def brands_index(B, prods):
    rows = "".join('<tr><th scope="row"><a href="/brands/%s/">%s</a></th><td>%d</td><td>%s</td><td>%s</td></tr>' % (
        k, esc(B.P.BRANDS[k]["name"]), sum(1 for p in prods if p["brand"] == k), esc(BRAND_LINE_LONG[k][0]), esc(BRAND_LINE_LONG[k][1])) for k in B.BRAND_ORDER)
    tiles = "".join('<a class="tile" href="/brands/%s/"><b>%s</b><span>%s</span></a>' % (k, esc(B.P.BRANDS[k]["name"]), esc(B.BRAND_LINE[k])) for k in B.BRAND_ORDER)
    body = ('<section class="hero sm"><div class="wrap"><div><p class="eyebrow">5 makers, one honest answer</p><h1>Walk-In Tub Brands We Sell</h1>'
            '<p class="lead">Pick by value, by made in USA, or by the shape the bather needs.</p><div class="ctas">%s%s</div></div></div></section>%s'
            '<section class="sec"><div class="wrap"><div class="grid g3">%s</div></div></section>'
            '<section class="sec alt"><div class="wrap"><h2>Brands side by side</h2><div class="tbl-wrap"><table class="data"><thead><tr><th scope="col">Brand</th><th scope="col">Models</th><th scope="col">Best for</th><th scope="col">Warranty (as published)</th></tr></thead><tbody>%s</tbody></table></div>'
            '<p class="src">Warranty summaries are from each maker\'s published materials, checked November 2026. We send the actual warranty document with every quote.</p></div></section>'
            '<section class="sec"><div class="wrap narrow prose"><h2>Which brand is the best value?</h2><p>For most buyers, Hydro Dimensions. Its published lifetime warranty covers the whole tub, motors and controls included, and its sizes fit the bathrooms most people have. If made in the USA matters most, Rane by Bestbath is the only fully USA-made line we sell. If the bather needs a transfer door, two seats or a lay-down tub, Ella\'s Bubbles has the widest choice. If the budget is tight and you have a capable installer, ANZZI is the lowest-cost route.</p></div></section>%s') % (
        B.call_btn(), B.quote_btn(), B.trust_bar(), tiles, rows, B.band())
    B.page("brands/", "Walk-In Tub Brands: Hydro Dimensions, Ella, Meditub, Rane, ANZZI",
           "Compare the five walk-in tub brands we sell: best value, made in USA, transfer and two-seat choices, and the lowest-cost line. Shipped or installed.",
           body, trail=[("Brands", "/brands/")])


BRAND_LINE_LONG = {
    "hydro-dimensions": ("Best value: broadest warranty, everyday sizes", "Lifetime: shell, frame, finish, door seal, motors, controls"),
    "ellas-bubbles": ("Transfer doors, two-seat, lay-down, tall or larger bathers", "Lifetime shell, frame, door gasket; 5 years hardware"),
    "meditub": ("Matching an exact footprint; WCA wheelchair models", "10 years shell, frame, finish; lifetime door seal"),
    "rane": ("Made in USA; wheelchair and lift transfers; heavy use", "5 years shell; 3 years parts; lifetime door seal"),
    "anzzi": ("Lowest cost; supply only with a handy installer", "Lifetime on the door's pressure seal (ANZZI terms)"),
}


# ======================= compare =======================
def compare(B, prods):
    data = {"rows": [["size", "Outside size"], ["door", "Door"], ["seat_h", "Seat height"], ["step", "Step-in height"], ["seat_w", "Seat width"],
                     ["cap", "Water capacity"], ["therapy", "Therapy"], ["shell", "Shell"], ["origin", "Made in"], ["warranty", "Warranty"]],
            "items": {}}
    for p in prods:
        data["items"][p["slug"]] = {"name": p["name"], "model": p["model"], "url": p["url"], "size": p["size"], "door": p["door_note"] or p["door_label"],
                                    "seat_h": ("%s in." % B.fmt(p["seat_h"])) if p.get("seat_h") else "", "step": ("%s in." % B.fmt(p["step"])) if p.get("step") else "",
                                    "seat_w": ("%s in." % B.fmt(p["seat_w"])) if p["seat_w"] else "", "cap": ("%s gal" % B.fmt(p["cap"])) if p["cap"] else "",
                                    "therapy": "Soaker" if p["soaker"] else ("Jets and air options" if (p["jets"] or p["air"]) else ""),
                                    "shell": p["shell"], "origin": p["origin"], "warranty": p["warranty"]}
    opts = "".join('<optgroup label="%s">%s</optgroup>' % (esc(B.P.BRANDS[k]["name"]), "".join(
        '<option value="%s">%s</option>' % (p["slug"], esc(p["name"])) for p in prods if p["brand"] == k)) for k in B.BRAND_ORDER)
    pick = "".join('<label>Tub %d<select aria-label="Tub %d"><option value="">Choose a tub</option>%s</select></label>' % (i, i, opts) for i in (1, 2, 3))
    body = ('<section class="hero sm"><div class="wrap"><div><p class="eyebrow">Side by side</p><h1>Compare Walk-In Tubs Side by Side</h1>'
            '<p class="lead">Pick up to three. Size, door, seat, step-in and warranty in one table.</p><div class="ctas">%s%s</div></div></div></section>'
            '<section class="sec"><div class="wrap"><div class="cmp-pick">%s</div><div id="cmp-out" class="mt18" aria-live="polite"><p class="empty">Pick two or three tubs above to see them side by side.</p></div>'
            '<script type="application/json" id="cmp-data">%s</script></div></section>'
            '<section class="sec alt"><div class="wrap narrow prose"><h2>What to compare first</h2><ol class="steps">'
            '<li><b>Outside size against your space.</b> Width decides whether it gets through the door; length decides whether it fills the alcove.</li>'
            '<li><b>Door direction against the bather.</b> Inward doors suit walkers; outward and lift-up doors suit seated transfers.</li>'
            '<li><b>Seat and step-in heights against the body.</b> A lower step is easier on hips and knees; a seat near wheelchair height makes a transfer level.</li>'
            '<li><b>Water capacity against your heater.</b> Bigger tubs need more hot water at once.</li>'
            '<li><b>Warranty in writing.</b> Coverage differs a lot between makers; ask for the document, not a summary.</li></ol>'
            '<p>Blank cells mean the maker has not published that number. We get it from the factory drawing when you request a quote.</p></div></section>%s') % (
        B.call_btn(), B.quote_btn(), pick, json.dumps(data, ensure_ascii=False).replace("</", "<\\/"), B.band())
    B.page("compare/", "Compare Walk-In Tubs Side by Side: Size, Door, Seat, Warranty",
           "Compare up to three walk-in tubs side by side: outside size, door direction, seat and step-in height, water capacity and warranty.",
           body, trail=[("Compare tubs", "/compare/")])


# ======================= specs =======================
def specs(B, prods):
    f = B.fmt
    rows = "".join('<tr><th scope="row"><a href="%s">%s</a></th><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
        p["url"], esc(p["name"]), f(p["W"]), f(p["L"]), f(p["H"]) or "", esc(p["door_label"]), (f(p["step"]) if p.get("step") else ""),
        (f(p["seat_h"]) if p.get("seat_h") else ""), (f(p["cap"]) if p["cap"] else "")) for p in sorted(prods, key=lambda x: (x["W"] or 0, x["L"] or 0)))
    known_step = sorted([p for p in prods if p.get("step")], key=lambda p: p["step"])
    low = ", ".join('<a href="%s">%s</a> (%s in.)' % (p["url"], esc(p["name"]), f(p["step"])) for p in known_step[:6])
    body = ('<section class="hero sm"><div class="wrap"><div><p class="eyebrow">For you or your contractor</p><h1>Walk-In Tub Specs, Rough-In and Delivery Sizes</h1>'
            '<p class="lead">Every size we sell in one table, plus the five checks before you order.</p><div class="ctas">%s%s</div></div></div></section>'
            '<section class="sec"><div class="wrap"><h2>All %d tubs by size</h2><p>Inches, from each maker\'s published sheets. Blank means not published; we pull it from the factory drawing on request. Tap a column header on a phone to scroll sideways.</p>'
            '<div class="tbl-wrap"><table class="data"><caption class="vh">Walk-in tub dimensions</caption><thead><tr><th scope="col">Model</th><th scope="col">Width</th><th scope="col">Length</th><th scope="col">Height</th><th scope="col">Door</th><th scope="col">Step-in</th><th scope="col">Seat height</th><th scope="col">Gallons</th></tr></thead><tbody>%s</tbody></table></div></div></section>'
            '<section class="sec alt"><div class="wrap narrow prose">'
            '<h2 id="rough-in">Rough-in: what the installer needs first</h2><p>Ask for the factory drawing of the exact model and door hand before any demolition. It shows the drain location, the supply connections, the frame footprint and how far the access panel sits from the wall. Order the drain side that matches the existing drain: standing in front of the tub, is the drain on your left or your right? Moving a drain is possible but it is the single most common reason an install runs long. Our %s walks through every line on a spec sheet.</p>'
            '<h2 id="electrical">Electrical: soakers need nothing, jets need a circuit</h2><p>A soaking walk-in has no pump and needs no power. Water jets, air jets, inline heaters and heated seats do. The National Electrical Code treats these as hydromassage bathtubs (Article 680, Part VII), which calls for ground-fault (GFCI) protection, and makers specify a dedicated circuit with the amperage on the spec sheet. A licensed electrician should read that sheet before the tub ships.</p>'
            '<h2 id="door-clearance">Door clearance</h2><p>Inward doors swing into the tub and need no floor space in front. Outward doors swing into the room: plan clear floor at least as wide as the door so it opens fully, and keep the toilet and vanity out of its path. Lift-up doors, such as the Rane RR7 Atlantic, need overhead clearance instead.</p>'
            '<h2 id="step-in">Step-in height</h2><p>The threshold is the wall you step over to get in. Lower is easier on hips and knees. The lowest published thresholds on tubs we sell: %s.</p>'
            '<h2 id="delivery">Delivery sizes and the path in</h2><p>The tub travels crated, so the crate is a little larger than the shell. Measure every point on the route: the front door, hall turns, stair landings and the bathroom door, at the tightest spot including trim. As a first check, look for about 2 inches more than the tub\'s width. Tubs can sometimes be tipped on edge to pass a narrow door; your installer judges that on site. Our <a href="/planner/">fit planner</a> runs these numbers for you.</p>'
            '<h2 id="hot-water">Hot water</h2><p>You fill a walk-in after you sit down and close the door, so the heater has to deliver most of the fill in one go. Compare the gallons in the table with your water heater. Aging Safely Baths explains <a href="https://www.agingsafelybaths.com/what-size-water-heater-for-a-walk-in-tub/">how to size a water heater for a walk-in tub</a> in detail.</p>'
            '<p class="src">Electrical reference: NFPA 70, National Electrical Code, Article 680 Part VII (hydromassage bathtubs). Local codes and inspectors have the final word.</p></div></section>%s') % (
        B.call_btn(), B.quote_btn(), len(prods), rows, gl("walk-in-tub-rough-in-specs", "rough-in and spec sheet guide"), low or "ask us for the drawing of the model you are considering", B.band("Need the drawing for a specific model?", "Tell us the model and door hand. We send the factory drawing and spec sheet to you or your installer."))
    B.page("specs/", "Walk-In Tub Specs and Rough-In Dimensions: Every Model",
           "Walk-in tub dimensions for every model we sell, plus rough-in, electrical (GFCI), door clearance, step-in height and delivery path checks.",
           body, trail=[("Specs and rough-in", "/specs/")])


# ======================= quote =======================
def quote(B):
    body = ('<section class="hero sm"><div class="wrap"><div><p class="eyebrow">Written price, no pressure</p><h1>Get Your Walk-In Tub Price</h1>'
            '<p class="lead">Supply only, fully installed, or both. In writing, for your exact model.</p><div class="ctas">%s</div></div></div></section>'
            '<section class="sec"><div class="wrap two-col"><div>%s</div><aside><div class="card"><h2 class="h-side">What happens next</h2><ol class="steps">'
            '<li>We call or text you back, usually the same day, 7am to 8pm Mountain.</li>'
            '<li>We confirm the model, the door hand and your bathroom size, by phone or from photos.</li>'
            '<li>You get an itemized written price: tub and freight for supply only, or the full install.</li>'
            '<li>For installed jobs, a factory-certified tech does a full site visit before install day.</li></ol>'
            '<p class="src">No high-pressure sales visit. Nothing is charged until you approve the quote. Installed walk-in tub jobs run %s.</p></div></aside></div></section>%s') % (
        B.call_btn(), price_form(None, B, "Request a price", "quote"), INSTALLED, B.trust_bar())
    B.page("quote/", "Get a Walk-In Tub Price: Supply Only or Fully Installed",
           "Request a written walk-in tub price: supply only (shipped to you) or fully installed by a factory-certified installer. No high-pressure sales visit.",
           body, trail=[("Get my price", "/quote/")])


# ======================= home =======================
def home(B, prods, guides):
    feat_slugs = ["hydro-dimensions-3060", "ellas-bubbles-transfer30", "meditub-3060wca", "rane-rk12-winnipeg", "hydro-dimensions-3052w", "ellas-bubbles-companion", "meditub-3260", "anzzi-value-series-30x60-soaking"]
    feat = [p for s in feat_slugs for p in prods if p["slug"] == s]
    hero = next((B.first_img(p) for p in prods if p["slug"] == "hydro-dimensions-3060" and B.first_img(p)), None) or next(B.first_img(p) for p in prods if B.first_img(p))
    needs = "".join('<a class="tile" href="/walk-in-tubs/#need=%s">%s<b>%s</b><span>%s</span></a>' % (k, B.ico(i, 26), esc(n), esc(d)) for k, n, d, i in B.NEEDS)
    brands = "".join('<a class="tile" href="/brands/%s/"><b>%s</b><span>%s</span><span class="src">%d models</span></a>' % (
        k, esc(B.P.BRANDS[k]["name"]), esc(B.BRAND_LINE[k]), sum(1 for p in prods if p["brand"] == k)) for k in B.BRAND_ORDER)
    gl = "".join('<a class="tile" href="/guides/%s/"><b>%s</b><span>%s</span></a>' % (g["slug"], esc(g["h1"]), esc(g["desc"])) for g in guides[:3])
    faqs = [("Can I buy a walk-in tub without installation?", "Yes. Choose supply only: the tub ships by freight to your curb or driveway and your own plumber or contractor installs it, with our phone tech support for them at no charge."),
            ("What does fully installed include?", "A factory-certified tech does a full site visit first. On install day the old tub comes out and is hauled away, the new tub is set, plumbed, sealed and test-filled, and you get a walkthrough. Most homes are done in 1 day. Installed walk-in tub jobs run %s." % INSTALLED),
            ("Which walk-in tub brand is the best value?", "For most buyers, Hydro Dimensions: its published lifetime warranty covers the whole tub, motors and controls included. Rane by Bestbath is the only fully made-in-USA line we sell."),
            ("Do you ship walk-in tubs to Canada?", "Yes, supply only. Freight is quoted to your postal code, and our tech line supports your installer the same way it does in the US.")]
    body = ('<section class="hero"><div class="wrap"><div><p class="eyebrow">%d models &middot; Hydro Dimensions &middot; Ella\'s Bubbles &middot; Meditub &middot; Rane &middot; ANZZI</p>'
            '<h1>Walk-In Tubs for Sale: Shipped or Installed</h1><p class="lead">Buy the tub alone with free tech support, or let our factory-certified installers do it all.</p>'
            '<div class="ctas">%s%s</div></div><div class="hero-media"><img src="%s" width="%d" height="%d" alt="White walk-in tub with an inward-swinging door and built-in seat" fetchpriority="high"></div></div></section>%s'
            '<section class="sec"><div class="wrap"><div class="sec-h"><h2>Shop by need</h2><a href="/walk-in-tubs/">See all %d tubs</a></div><div class="grid g4">%s</div></div></section>'
            '<section class="sec alt"><div class="wrap"><h2>Two ways to buy any tub</h2><div class="grid g2">'
            '<div class="card"><h3>Supply only (shipped to you)</h3><ul class="checks"><li>Pay for the tub and freight, nothing else</li><li>Freight to your curb or driveway, 50 states and Canada</li><li>Spec sheet and factory drawing before you order</li><li>Phone tech support for your installer</li></ul><a class="btn btn-line" href="/supply-only/">How supply only works</a></div>'
            '<div class="card"><h3>Fully installed (factory-certified installer)</h3><ul class="checks"><li>Full site visit by a factory-certified tech before install</li><li>Old tub out and hauled away</li><li>Set, plumbed, sealed and test-filled, in 1 day in most homes</li><li>One itemized written price</li></ul><a class="btn btn-line" href="/white-glove/">What a full install includes</a></div>'
            '</div></div></section>'
            '<section class="sec"><div class="wrap"><div class="sec-h"><h2>Popular tubs</h2><a href="/compare/">Compare tubs side by side</a></div><div class="pgrid">%s</div></div></section>'
            '<section class="sec alt"><div class="wrap"><h2>Shop by brand</h2><div class="grid g3">%s</div></div></section>'
            '<section class="sec"><div class="wrap two-col"><div class="prose"><h2>Why buy your walk-in tub here</h2>'
            '<p><b>You pay only for what you need.</b> Have a plumber you trust? Buy the tub supply only. Want it handled? Choose a full install and get one price for the tub and the work.</p>'
            '<p><b>Five makers, one straight answer.</b> Because we sell Hydro Dimensions, Ella\'s Bubbles, Meditub, Rane and ANZZI, we can match the tub to the bathroom and the bather instead of pushing one brand. When a walk-in tub is not the right answer, we say so.</p>'
            '<p><b>Help after the truck leaves.</b> Every tub comes with phone support for whoever installs it: rough-in, leveling, the door-seal test and the electrical for jets and heaters.</p>'
            '<p><b>A company you can check.</b> Walk-In Tubs 4 Less is part of Aging Safely Baths, BBB A+ accredited since 2012 and rated 4.9 on Google. We install in all 50 states and ship supply-only orders to the US and Canada.</p>'
            '<h2>How it works</h2><ol class="steps"><li><b>Pick a tub</b> or tell us about the room and the bather.</li><li><b>Get a written price</b> for supply only, a full install, or both.</li><li><b>Confirm the fit:</b> doorways, drain side, water heater and power.</li><li><b>Delivery or install day.</b> Freight to you, or old tub out and new tub in.</li></ol></div>'
            '<aside>%s</aside></div></section>'
            '%s'
            '<section class="sec"><div class="wrap narrow">%s</div></section>%s') % (
        len(prods), B.call_btn(), B.quote_btn(), hero["src"], hero["w"], hero["h"], B.trust_bar(), len(prods), needs,
        "".join(B.card(p) for p in feat), brands, price_form(None, B, "Get my price", "home"),
        ('<section class="sec alt"><div class="wrap"><div class="sec-h"><h2>Buying guides</h2><a href="/guides/">All guides</a></div><div class="grid g3">%s</div></div></section>' % gl) if gl else "",
        B.faq_html(faqs), B.band())
    B.page("", "Walk-In Tubs for Sale: Shipped or Installed | Walk-In Tubs 4 Less",
           "Walk-in tubs for sale from Hydro Dimensions, Ella's Bubbles, Meditub, Rane and ANZZI. Buy supply only with tech support, or fully installed. BBB A+.",
           body, ld=[B.faq_ld(faqs), {"@type": "WebSite", "@id": B.DOMAIN + "/#site", "name": B.STORE, "url": B.DOMAIN + "/", "publisher": {"@id": B.DOMAIN + "/#org"}}], home=True)


# ======================= supply-only / installed / about / faq / tech / planner / legal =======================
def supply(B):
    faqs = [("Is a walk-in tub hard for a regular plumber to install?", "Most experienced plumbers and remodelers can do it. It takes more care than a standard tub: the frame must be level and fully supported so the door seals, and jetted or heated models need a circuit. We send the factory drawing and manual before you order and stay on the phone with your installer during the job."),
            ("What does supply only cost compared with installed?", "Supply only is the tub plus freight. An installed price adds removal and haul-away of the old tub, plumbing, any electrical, wall finish and the site visit. We quote both in writing so you compare real numbers. Installed walk-in tub jobs run %s." % INSTALLED),
            ("What if the tub arrives damaged?", "Inspect the crate before the driver leaves, write any damage on the delivery receipt, take photos and call us the same day. A clean signature makes a freight claim much harder."),
            ("Is the warranty the same if my own installer puts it in?", "Each maker writes its own warranty, and most require installation that follows their manual. We send the actual warranty document with your quote so you know what it expects.")]
    body = ('<section class="hero sm"><div class="wrap"><div><p class="eyebrow">Path 1 &middot; Supply only</p><h1>Buy a Walk-In Tub Online, Shipped to You</h1>'
            '<p class="lead">Pay for the tub and freight. Your installer, our free tech support.</p><div class="ctas">%s%s</div></div></div></section>%s'
            '<section class="sec"><div class="wrap two-col"><div class="prose">'
            '<p>Supply only is how most discount walk-in tub prices happen: you skip paying for installation you do not need. You buy the tub, it ships by freight to your curb or driveway in the US or Canada, and your own plumber, contractor or handy family member installs it with our tech line behind them.</p>'
            '<h2>What you get</h2><ul class="checks"><li>A new tub in its factory crate, with the maker\'s warranty</li><li>Freight delivery to your curb, driveway or jobsite</li><li>The spec sheet, factory drawing, install manual and warranty for your model before you order</li><li>Phone tech support for you or your installer, at no charge</li><li>A written quote first; nothing is charged until you approve it</li></ul>'
            '<h2>What you handle</h2><ul class="dots"><li>Carrying the tub from the curb to the bathroom (two or three strong people and a dolly)</li><li>Removing the old tub</li><li>Hiring the installer and, where your city requires one, the permit</li><li>Electrical for jets, air or heaters, by a licensed electrician</li></ul>'
            '<p>Rather hand off that list? Choose <a href="/white-glove/">fully installed</a> instead.</p>'
            '<h2>Is supply only right for you?</h2><p>It fits if someone you trust has set a tub before, if the whole bathroom is being remodeled anyway, or if you live where our install crews do not reach. It is a poor fit if nobody involved is comfortable with plumbing and a level, because a walk-in tub that is not set right will leak at the door.</p>'
            '<h2>Five checks before you order</h2><ol class="steps"><li><b>The path in.</b> Measure the tightest doorway, hall turn and landing and compare with the tub\'s width.</li><li><b>The alcove.</b> Many walk-ins fit a 60-inch tub space; shorter ones use an extension kit or a filler panel.</li><li><b>Drain side.</b> Facing the tub space, is the drain on your left or right? Order to match.</li><li><b>Hot water.</b> Compare the tub\'s gallons with your water heater.</li><li><b>Power.</b> Soakers need none; jets, air and heaters need the circuit on the spec sheet.</li></ol>'
            '<p>Run the numbers in our <a href="/planner/">fit planner</a> or the <a href="/specs/">specs and rough-in table</a>. For freight, inspection and return terms, read %s; if you are looking at a secondhand tub, read %s first.</p>%s</div>'
            '<aside>%s</aside></div></section>%s') % (
        B.call_btn(), B.quote_btn("/quote/?path=supply"), B.trust_bar(), gl("buy-walk-in-tub-online", "how to buy a walk-in tub online"),
        gl("used-walk-in-tub-for-sale", "what to check on a used walk-in tub"), B.faq_html(faqs, "Supply only questions"), price_form(None, B, "Price it supply only", "supply"), B.band())
    B.page("supply-only/", "Buy a Walk-In Tub Online: Supply Only, Shipped to You",
           "Buy a walk-in tub online, supply only: freight to your curb in the US or Canada, factory warranty, and free phone tech support for your installer.",
           body, trail=[("Supply only", "/supply-only/")], ld=[B.faq_ld(faqs)])


def installed(B):
    faqs = [("How long does a walk-in tub install take?", "1 day in most homes, once the tub is on site. Jobs that move a drain, add a circuit or need wall repair take longer, and your written quote lists the expected days."),
            ("Do you haul away the old tub?", "Yes. Removal and haul-away of the old tub, the surround and the job debris are part of a full install, listed on your quote."),
            ("Is a full install available where I live?", "We install in all 50 states through factory-certified installers. Put your ZIP code on the quote form or tell us by phone and we confirm coverage and timing for your area."),
            ("Will you pull the permit?", "Where your city or county requires a plumbing or electrical permit, it is on the quote as its own line. Requirements vary a lot, so we check yours rather than guess.")]
    body = ('<section class="hero sm"><div class="wrap"><div><p class="eyebrow">Path 2 &middot; Fully installed</p><h1>Walk-In Tub Delivery and Installation, Done for You</h1>'
            '<p class="lead">One written price. Old tub out, new tub in, in 1 day in most homes.</p><div class="ctas">%s%s</div></div></div></section>%s'
            '<section class="sec"><div class="wrap two-col"><div class="prose">'
            '<p>Our white glove package covers delivery, removal, installation and haul-away, done by factory-certified installers. You pick the tub and the day. Installed walk-in tub jobs run %s, and your quote itemizes every piece.</p>'
            '<h2>Everything on a full install</h2><ol class="steps">'
            '<li><b>Written quote first.</b> By phone or from photos, with no high-pressure sales visit.</li>'
            '<li><b>Site visit.</b> After you pick a tub and place a deposit, a factory-certified tech visits to measure, photograph and confirm doorways, drain side, water heater and power.</li>'
            '<li><b>Delivery inside.</b> The tub comes into the bathroom, not to the curb.</li>'
            '<li><b>Removal and haul-away.</b> The old tub and surround leave with the crew.</li>'
            '<li><b>Set, plumb, power.</b> Leveled, plumbed and sealed; jetted and heated models get their circuit.</li>'
            '<li><b>Test and walkthrough.</b> A full fill, a door-seal check, a drain test and a lesson on every control.</li></ol>'
            '<p>Curious how the tub gets through the house? Our %s explains it step by step.</p>'
            '<h2>Who it is for</h2><p>Families buying for a parent who lives alone. Anyone recovering from surgery. People who have been burned by a remodel. And anyone who would rather not coordinate a store, a freight company, a plumber and an electrician.</p>'
            '<h2>What we will not do</h2><p>We will not rush you with a today-only price, and we will not tell you Medicare will pay for it: Original Medicare generally does not cover walk-in tubs. Veterans and Medicaid members may have grant or waiver options; Aging Safely Baths explains <a href="https://www.agingsafelybaths.com/va-hisa-grant-for-bathroom-modifications/">how the VA HISA grant works for bathroom changes</a>.</p>%s</div>'
            '<aside>%s</aside></div></section>%s') % (
        B.call_btn(), B.quote_btn("/quote/?path=installed"), B.trust_bar(), INSTALLED, gl("walk-in-tub-delivery-will-it-fit", "walk-in tub delivery guide"), B.faq_html(faqs, "Installation questions"),
        price_form(None, B, "Price it fully installed", "installed"), B.band())
    B.page("white-glove/", "White Glove Walk-In Tub Delivery and Installation",
           "Walk-in tub delivery, removal, installation and haul-away by factory-certified installers. 1 day in most homes. One itemized written price.",
           body, trail=[("Fully installed", "/white-glove/")], ld=[B.faq_ld(faqs)])


def about(B):
    body = ('<section class="hero sm"><div class="wrap"><div><p class="eyebrow">An Aging Safely Baths company</p><h1>About Walk-In Tubs 4 Less</h1>'
            '<p class="lead">The walk-in tub store of Aging Safely Baths, Denver, Colorado.</p><div class="ctas">%s%s</div></div></div></section>%s'
            '<section class="sec"><div class="wrap narrow prose">'
            '<p>Walk-In Tubs 4 Less is the online store of Aging Safely Baths, a Denver company that has installed walk-in tubs, roll-in showers and handicap showers since it was founded in 2011. Aging Safely Baths has been BBB accredited since August 2012 with an A+ rating, and its Google rating was 4.9 from 35 reviews as of October 2026.</p>'
            '<h2>What we do</h2><ul class="checks"><li>Sell walk-in tubs from Hydro Dimensions, Ella\'s Bubbles, Meditub, Rane by Bestbath and ANZZI</li><li>Ship supply-only orders to all 50 states and Canada</li><li>Install in all 50 states through factory-certified installers, in 1 day in most homes</li><li>Support your own installer by phone, at no charge</li></ul>'
            '<h2>How we work</h2><p>Every price is itemized and in writing, by phone or from photos. There is no high-pressure sales visit. For installed jobs, a factory-certified tech does a full site visit before install day. Tubs carry their maker\'s warranty. Hydro Dimensions and Ella\'s Bubbles cover the shell for life; Meditub, Rane and ANZZI terms differ, and each model page lists them. We send the actual warranty document with every quote.</p>'
            '<h2>Contact</h2><p>Phone <a href="tel:%s">%s</a>, 7am to 8pm Mountain, 7 days. Email <a href="mailto:%s">%s</a>. Machine-readable company facts are published at <a href="https://www.agingsafelybaths.com/facts.json" rel="nofollow">agingsafelybaths.com/facts.json</a>, and our <a href="%s" rel="nofollow noopener">BBB profile</a> is public.</p>'
            '<p class="src">No bathing product eliminates the risk of falls; walk-in tubs are designed to reduce risk when installed and used properly.</p></div></section>%s') % (
        B.call_btn(), B.quote_btn(), B.trust_bar(), B.TEL, B.PHONE, B.EMAIL, B.EMAIL, B.BBB, B.band())
    B.page("about/", "About Walk-In Tubs 4 Less, an Aging Safely Baths Company",
           "Walk-In Tubs 4 Less is the walk-in tub store of Aging Safely Baths, Denver: BBB A+ since 2012, installs in 50 states, ships to the US and Canada.",
           body, trail=[("About us", "/about/")])


def faq(B):
    qas = [("Can I really buy a walk-in tub without the installation?", "Yes, that is supply only. You pay for the tub and freight, it is delivered to your curb or driveway, and your own installer puts it in with our phone tech support."),
           ("Why do some companies only sell walk-in tubs installed?", "Many brands sell the tub and the installation as one package, so you cannot see the tub price on its own. We price the tub alone and the full job separately, so you can compare."),
           ("How wide does my doorway need to be?", "Compare the narrowest doorway or hall turn with the tub's width. Many walk-ins are 26 to 33 inches wide, and the crate adds a little. If it is close, send us the measurements before you order; tubs can sometimes be tipped on edge, but not always."),
           ("Will a walk-in tub fit where my old bathtub is?", "Often. Many walk-ins are built for the common 60-inch alcove, and shorter models use an extension kit or filler panel. The drain side also needs to match."),
           ("Do I need a bigger water heater?", "Maybe. A walk-in holds more than a standard tub and you fill it after you sit down. Compare the tub's gallons with your heater. An inline heater keeps water warm but does not heat cold water from scratch."),
           ("How much does an installed walk-in tub cost?", "Installed walk-in tub jobs run %s, depending on the model, therapy options and the bathroom. Supply only is the tub plus freight. Both are quoted in writing." % INSTALLED),
           ("Does Medicare cover walk-in tubs?", "Original Medicare generally does not. Some Medicare Advantage plans offer supplemental home-safety benefits, so call your plan. Medicaid waivers and VA grants are separate programs with their own rules."),
           ("Do you ship to Canada?", "Yes, supply only, with freight quoted to your postal code."),
           ("Can I pay online?", "Not by card. You get a written quote with the tub, freight and any installation listed, and you pay after you approve it."),
           ("What about returns?", "Walk-in tubs ship by freight, so returns work differently from small parcels and vary by maker. The return and cancellation terms for your tub are on your quote before you pay.")]
    body = ('<section class="hero sm"><div class="wrap"><div><p class="eyebrow">Buying questions</p><h1>Walk-In Tub Buying FAQ</h1>'
            '<p class="lead">Straight answers on buying, delivery, fit and installation.</p><div class="ctas">%s%s</div></div></div></section>'
            '<section class="sec"><div class="wrap narrow">%s<p class="src">Medicare answer based on Medicare.gov durable medical equipment rules and CMS National Coverage Determination 280.1. No bathing product eliminates the risk of falls.</p></div></section>%s') % (
        B.call_btn(), B.quote_btn(), B.faq_html(qas, "Frequently asked"), B.band())
    B.page("faq/", "Walk-In Tub Buying FAQ: Delivery, Fit, Installation, Cost",
           "Answers on buying a walk-in tub online: supply only vs installed, doorway and alcove fit, water heaters, installed cost, Medicare and returns.",
           body, trail=[("FAQ", "/faq/")], ld=[B.faq_ld(qas)])


def tech(B):
    body = ('<section class="hero sm"><div class="wrap"><div><p class="eyebrow">For you or your contractor</p><h1>Walk-In Tub Installation Help by Phone</h1>'
            '<p class="lead">Every tub we sell comes with free tech support for whoever installs it.</p><div class="ctas">%s%s</div></div></div></section>'
            '<section class="sec"><div class="wrap narrow prose">'
            '<p>Homeowners, handymen, plumbers and remodelers all call the same line: <a href="tel:%s">%s</a>. Have the model number, the serial label and photos of the space ready.</p>'
            '<h2>What installers call about</h2><ul class="dots"><li><b>Rough-in:</b> drain location, supply connections and the stud opening for the exact model.</li><li><b>Leveling:</b> walk-in doors seal only on a level, fully supported frame.</li><li><b>The door-seal test:</b> how to fill and check the door before the walls close up.</li><li><b>Electrical:</b> which circuit jets, air systems and inline heaters need, per the spec sheet.</li><li><b>Extension kits and flanges:</b> fitting a shorter tub into a 60-inch alcove.</li><li><b>Start-up:</b> first fill, first drain, and what normal sounds like.</li></ul>'
            '<h2>Before you call</h2><p>Photos of the drain, the supply lines, the floor and the wall framing solve most questions in one call. The <a href="/specs/">specs and rough-in page</a> has every size in one table.</p>'
            '<h2>What we cannot do by phone</h2><p>We cannot sign off on electrical or plumbing work; your licensed trades and your inspector do that. If something in the house does not match the sheet, we tell you what to ask the maker, or get them on the line.</p>'
            '<h2>Contractors quoting a client</h2><p>If your client buys the tub from us, send the model and site photos and we send the spec sheet and manual for that exact SKU. You install and bill your labor, with backup when something about the tub is unclear.</p></div></section>%s') % (
        B.call_btn(), B.quote_btn("/quote/?path=supply", "Price a tub for a client"), B.TEL, B.PHONE, B.band())
    B.page("tech-support/", "Walk-In Tub Installation Tech Support for Installers",
           "Free phone tech support for whoever installs a walk-in tub bought from us: rough-in, leveling, door-seal test, electrical and extension kits.",
           body, trail=[("Tech support", "/tech-support/")])


def planner(B, prods):
    body = ('<section class="hero sm"><div class="wrap"><div><p class="eyebrow">Free fit check</p><h1>Walk-In Tub Planner: Will It Fit?</h1>'
            '<p class="lead">Five numbers. A list of tubs that get through your house and fill the space.</p><div class="ctas">%s%s</div></div></div></section>'
            '<section class="sec"><div class="wrap two-col">'
            '<form class="form card" id="planner" novalidate aria-label="Walk-in tub fit check">'
            '<div class="row"><div><label for="pl-door">Narrowest doorway or hall turn on the way in (inches)</label><input id="pl-door" type="number" inputmode="decimal" min="18" max="60" step="0.25" required></div>'
            '<div><label for="pl-len">Alcove length, wall to wall (inches)</label><input id="pl-len" type="number" inputmode="decimal" min="30" max="90" step="0.25" required></div></div>'
            '<div class="row"><div><label for="pl-wid">Alcove depth, back wall to front edge (inches)</label><input id="pl-wid" type="number" inputmode="decimal" min="20" max="50" step="0.25" required></div>'
            '<div><label for="pl-heater">Water heater size (gallons, 0 if tankless)</label><input id="pl-heater" type="number" inputmode="numeric" min="0" max="120" step="1"></div></div>'
            '<fieldset class="choice"><legend>How does the bather get in today?</legend>'
            '<label class="opt"><input type="radio" name="pl-who" value="standing" checked><span><b>Walks in</b>Maybe with a grab bar</span></label>'
            '<label class="opt"><input type="radio" name="pl-who" value="walker"><span><b>Walker or cane</b>Needs a low step</span></label>'
            '<label class="opt"><input type="radio" name="pl-who" value="wheelchair"><span><b>Wheelchair or lift</b>Needs a seated transfer</span></label></fieldset>'
            '<button class="btn btn-quote full" type="submit">Check my fit</button></form>'
            '<aside class="card" id="pl-out" aria-live="polite"><h2 class="h-side">Your results</h2><p>Enter your measurements and press <b>Check my fit</b>. Measure at the tightest point: door stops and trim count, and hall corners are often tighter than doorways.</p></aside>'
            '</div></section>'
            '<section class="sec alt"><div class="wrap narrow prose"><h2>How the planner decides</h2><ul class="dots">'
            '<li><b>Doorway:</b> a crated tub needs about an inch of play on each side, so it looks for tubs at least 2 inches narrower than your tightest opening. Tipping a tub on edge sometimes helps; your installer judges that on site.</li>'
            '<li><b>Alcove:</b> the tub has to fit wall to wall. Up to about 8 inches of extra length can be closed with an extension kit or a filler panel.</li>'
            '<li><b>Hot water:</b> if your tank is smaller than the tub\'s published fill volume, plan for a larger heater or a tankless unit.</li>'
            '<li><b>Bather:</b> wheelchair and lift users get outward or lift-up door transfer tubs; walker users see the lowest published step-ins first.</li></ul>'
            '<p class="src">Sizes come from each maker\'s spec sheet, the same data as the tub pages. This is a first check, not a site measurement; we confirm the fit before anything ships.</p></div></section>%s') % (
        B.call_btn(), B.quote_btn(), B.band("Want a person to double-check?", "Send your numbers with a price request and we confirm the fit before anything ships."))
    B.page("planner/", "Walk-In Tub Planner: Doorway, Alcove and Water Heater Fit Check",
           "Free walk-in tub fit check: enter your doorway, alcove and water heater sizes and see which walk-in tubs fit your house and your bather.",
           body, trail=[("Fit planner", "/planner/")])
    # planner script: data from the catalog
    tubs = [{"n": p["name"], "u": p["url"], "m": p["model"], "w": p["W"], "l": p["L"], "x": p.get("ext") or 0, "g": p["cap"],
             "t": bool(p["transfer"] or p["door"] in ("outward", "upward")), "s": p.get("step")} for p in prods if p["W"] and p["L"]]
    js = PLANNER_JS.replace("__TUBS__", json.dumps(tubs, separators=(",", ":")))
    B.EXTRA_FILES["assets/planner.js"] = js


PLANNER_JS = r"""/* Walk-in tub planner: client-side fit check. Sizes = makers' spec sheets (same data as the tub pages). Generated by _build. */
(function () {
  "use strict";
  var TUBS = __TUBS__;
  function num(id) { var v = parseFloat(document.getElementById(id).value); return isNaN(v) ? null : v; }
  function radio(n) { var r = document.querySelector("input[name='" + n + "']:checked"); return r ? r.value : ""; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  document.addEventListener("DOMContentLoaded", function () {
    var f = document.getElementById("planner"), out = document.getElementById("pl-out");
    if (!f) { return; }
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      var door = num("pl-door"), len = num("pl-len"), wid = num("pl-wid"), heater = num("pl-heater"), who = radio("pl-who");
      if (door === null || len === null || wid === null) {
        out.innerHTML = '<h2 class="h-side">Your results</h2><p class="err">Please enter the doorway, alcove length and alcove depth in inches.</p>';
        return;
      }
      var fits = [];
      TUBS.forEach(function (t) {
        if (t.w + 2 > door) { return; }
        if (t.w > wid + 0.5) { return; }
        var fill = t.l + t.x;
        if (t.l - 0.75 > len) { return; }
        if (len - Math.max(fill, t.l) > 8) { return; }
        if (who === "wheelchair" && !t.t) { return; }
        var notes = [];
        if (len - t.l > 1 && !t.x) { notes.push("fill " + (len - t.l).toFixed(1) + " in. with a panel or build-out"); }
        if (t.x && len - t.l > 1) { notes.push("uses its " + t.x + " in. extension kit"); }
        if (heater !== null && heater > 0 && t.g && t.g > heater) { notes.push("holds about " + t.g + " gal; your " + heater + " gal heater may run short"); }
        fits.push({ t: t, notes: notes, score: (who === "walker" && t.s ? t.s : 9) * 10 + Math.abs(len - Math.max(fill, t.l)) });
      });
      fits.sort(function (a, b) { return a.score - b.score; });
      var h = '<h2 class="h-side">' + fits.length + (fits.length === 1 ? " tub fits" : " tubs fit") + " your numbers</h2>";
      if (!fits.length) {
        h += "<p>Nothing in our catalog clears all of those measurements. That happens with narrow doorways; call us, because some tubs can be tipped on edge and some rooms can take a shorter model.</p>";
      } else {
        h += '<ul class="dots">' + fits.slice(0, 12).map(function (x) {
          return '<li><a href="' + esc(x.t.u) + '">' + esc(x.t.n) + "</a> (" + x.t.w + " x " + x.t.l + " in.)" + (x.notes.length ? ": " + esc(x.notes.join("; ")) : "") + "</li>";
        }).join("") + "</ul>";
        if (fits.length > 12) { h += "<p>Plus " + (fits.length - 12) + ' more. <a href="/walk-in-tubs/">Filter the full list</a>.</p>'; }
      }
      h += '<p><a class="btn btn-quote" href="/quote/?note=' + encodeURIComponent("Planner: door " + door + ", alcove " + len + " x " + wid + ", heater " + (heater === null ? "?" : heater) + ", bather " + who) + '">Send these numbers with a price request</a></p>';
      out.innerHTML = h;
    });
  });
})();
"""


def legal(B):
    priv = ('<section class="hero sm"><div class="wrap"><div><h1>Privacy Policy</h1><p class="lead">What we collect, why, and how to reach us.</p><div class="ctas">%s</div></div></div></section>'
            '<section class="sec"><div class="wrap narrow prose">'
            '<p>Walk-In Tubs 4 Less is part of Aging Safely Baths. This policy covers walkintubs4less.com. Updated November 17, 2026.</p>'
            '<h2>What we collect</h2><p>When you send a price request we receive what you type (name, phone, ZIP or postal code, optional email and notes), the page you sent it from, the tub and path you chose, and basic technical details such as device type and any campaign tags in the link you followed. We do not sell your information.</p>'
            '<h2>How we use it</h2><p>To answer your request, prepare your quote, schedule delivery or installation, and keep records of the job. With your consent we may contact you by phone, text or email about your request, including by automated means. Reply STOP to opt out of texts at any time.</p>'
            '<h2>Who handles it</h2><p>Form submissions are stored and forwarded by our lead server, operated for us by our web developer, and delivered to the Aging Safely Baths sales team. Freight carriers and installers receive the details they need to do the job.</p>'
            '<h2>Data sharing opt-out and deletion</h2><p>To opt out of any sharing, or to ask us to see, correct or delete your information, email <a href="mailto:%s">%s</a> or call <a href="tel:%s">%s</a>.</p>'
            '<h2>Cookies</h2><p>This site does not set advertising cookies. Fonts load from Google Fonts.</p>'
            '<h2>How long we keep it</h2><p>We keep request and job records for as long as we need them to serve you, honor warranties and meet tax and legal record rules, then delete them.</p>'
            '<h2>Children</h2><p>This store is for adults. We do not knowingly collect information from children under 13.</p>'
            '<h2>Changes</h2><p>If we change this policy we update the date at the top of this page.</p></div></section>') % (B.call_btn(), B.EMAIL, B.EMAIL, B.TEL, B.PHONE)
    B.page("privacy/", "Privacy Policy | Walk-In Tubs 4 Less", "How Walk-In Tubs 4 Less, an Aging Safely Baths company, collects and uses information from price requests, and how to opt out.", priv, trail=[("Privacy", "/privacy/")])
    acc = ('<section class="hero sm"><div class="wrap"><div><h1>Accessibility Statement</h1><p class="lead">We want every shopper to be able to use this site.</p><div class="ctas">%s</div></div></div></section>'
           '<section class="sec"><div class="wrap narrow prose">'
           '<p>Many of our customers are older adults, people with disabilities and the family members helping them, so accessibility is part of how this store is built. We aim to meet the Web Content Accessibility Guidelines (WCAG) 2.2 at level AA.</p>'
           '<h2>What we do</h2><ul class="dots"><li>Large, high-contrast text on white backgrounds, with no dark text on dark colors</li><li>Every page works with a keyboard alone, with a visible focus outline and a skip-to-content link</li><li>Buttons are at least 46 pixels tall for easier tapping</li><li>Images carry text descriptions, and tub drawings include a written summary of their dimensions</li><li>Motion is minimal and turns off when your device asks for reduced motion</li><li>Forms label every field and explain errors in words</li></ul>'
           '<h2>Prefer the phone?</h2><p>Everything on this site can be done by phone: call <a href="tel:%s">%s</a>, 7am to 8pm Mountain, 7 days. We are happy to read specs aloud, email you documents in a larger font, or take your price request by phone.</p>'
           '<h2>Known limits</h2><p>Spec sheet PDFs come from the manufacturers and may not be fully accessible to screen readers. Every key number on those sheets also appears as text on the tub\'s page, and we will read any sheet to you by phone.</p>'
           '<h2>Tell us about a problem</h2><p>If something on this site is hard to use, email <a href="mailto:%s">%s</a> with the page and what happened. We aim to reply within two business days and fix confirmed problems promptly.</p></div></section>') % (B.call_btn(), B.TEL, B.PHONE, B.EMAIL, B.EMAIL)
    B.page("accessibility/", "Accessibility Statement | Walk-In Tubs 4 Less", "Our accessibility commitment: WCAG 2.2 AA goals, keyboard and screen reader support, large text, and help by phone 7 days a week.", acc, trail=[("Accessibility", "/accessibility/")])
    ty = ('<section class="hero sm"><div class="wrap"><div><h1>Thank You: We Got Your Request</h1><p class="lead">We will call or text you back, usually the same day.</p><div class="ctas">%s</div></div></div></section>'
          '<section class="sec"><div class="wrap narrow prose"><p>While you wait, it helps to measure the narrowest doorway on the way to the bathroom and note your water heater size. Want to keep browsing? <a href="/walk-in-tubs/">See every tub</a>.</p></div></section>') % B.call_btn()
    B.page("thank-you/", "Thank You | Walk-In Tubs 4 Less", "Thanks for your walk-in tub price request. We will call or text you back, usually the same day.", ty, index=False)


# ======================= guides =======================
def load_guides():
    out = []
    mf = os.path.join(GUIDES_SRC, "meta.json")
    if not os.path.exists(mf):
        return out
    try:
        meta = json.load(open(mf, encoding="utf-8"))
    except Exception:
        return out
    items = meta if isinstance(meta, list) else meta.get("guides") or list(meta.values()) if isinstance(meta, dict) else []
    if isinstance(meta, dict) and not isinstance(items, list):
        items = []
    for g in items:
        if not isinstance(g, dict):
            continue
        slug = g.get("slug")
        fp = os.path.join(GUIDES_SRC, "%s.html" % slug)
        if not slug or not os.path.exists(fp):
            continue
        body = open(fp, encoding="utf-8").read()
        out.append({"slug": slug, "title": g.get("title") or g.get("h1"), "h1": g.get("h1") or g.get("title"),
                    "desc": g.get("description") or g.get("desc") or "", "body": body, "meta": g})
    return out


def guide_pages(B, guides, prods):
    for g in guides:
        m = g["meta"]
        faqs = [(q.get("q") or q.get("question"), q.get("a") or q.get("answer")) for q in (m.get("faq") or m.get("faqs") or []) if isinstance(q, dict)]
        ld = [{"@type": "BlogPosting", "headline": g["h1"], "description": g["desc"], "datePublished": m.get("datePublished", B.TODAY),
               "dateModified": m.get("dateModified", B.TODAY), "author": {"@type": "Person", "name": "Zach Wennstedt"},
               "publisher": {"@type": "Organization", "name": "Aging Safely Baths", "url": B.ASB + "/"},
               "mainEntityOfPage": B.DOMAIN + "/guides/%s/" % g["slug"], "image": B.DOMAIN + "/assets/og.png",
               "speakable": {"@type": "SpeakableSpecification", "cssSelector": [".g-answer"]} if 'class="g-answer"' in g["body"] else None}]
        ld[0] = {k: v for k, v in ld[0].items() if v is not None}
        kw = [m.get("target_keyword")] + list(m.get("secondary_keywords") or [])
        kw = [k for k in kw if k]
        if kw:
            ld[0]["keywords"] = ", ".join(kw)
        if faqs:
            ld.append(B.faq_ld(faqs))
        rel = [x for x in guides if x["slug"] != g["slug"]][:3]
        relh = ('<section class="sec alt"><div class="wrap"><h2>More buying guides</h2><div class="grid g3">%s</div></div></section>' % "".join(
            '<a class="tile" href="/guides/%s/"><b>%s</b><span>%s</span></a>' % (x["slug"], esc(x["h1"]), esc(x["desc"])) for x in rel)) if rel else ""
        body_html = g["body"]
        has_h1 = "<h1" in body_html
        hero = "" if has_h1 else ('<section class="hero sm"><div class="wrap"><div><p class="eyebrow">Buying guide &middot; Updated November 17, 2026</p><h1>%s</h1>'
                                   '<p class="lead">%s</p><div class="ctas">%s%s</div></div></div></section>') % (
            esc(g["h1"]), esc(m.get("lead") or m.get("subhead") or "By Zach Wennstedt, Aging Safely Baths."), B.call_btn(), B.quote_btn())
        body = ('%s<article class="sec"><div class="wrap narrow prose">%s</div></article>%s%s') % (hero, body_html, relh, B.band())
        title = g["title"] if len(g["title"]) <= 70 else g["h1"][:70]
        desc = g["desc"] if len(g["desc"]) <= 170 else g["desc"][:167].rsplit(" ", 1)[0] + "."
        B.page("guides/%s/" % g["slug"], title, desc, body, trail=[("Guides", "/guides/"), (g["h1"], "/guides/%s/" % g["slug"])], ld=ld)
    if guides:
        tiles = "".join('<a class="tile" href="/guides/%s/"><b>%s</b><span>%s</span></a>' % (g["slug"], esc(g["h1"]), esc(g["desc"])) for g in guides)
        body = ('<section class="hero sm"><div class="wrap"><div><p class="eyebrow">Before you buy</p><h1>Walk-In Tub Buying Guides</h1>'
                '<p class="lead">Fit, delivery, specs and where to buy, from the people who install them.</p><div class="ctas">%s%s</div></div></div></section>'
                '<section class="sec"><div class="wrap"><div class="grid g3">%s</div></div></section>'
                '<section class="sec alt"><div class="wrap narrow prose"><h2>Where to start</h2><p>New to walk-in tubs? Read the delivery and fit guide first: most problems come from a tub that cannot get through the house, not from the tub itself. Then compare where to buy, and hand the rough-in guide to whoever installs it. When you are ready, <a href="/walk-in-tubs/">browse every tub</a> or <a href="/quote/">ask for a written price</a>.</p>'
                '<p>Funding, Medicare and cost questions are covered in depth by our parent company: see Aging Safely Baths on <a href="https://www.agingsafelybaths.com/walk-in-tub-cost/">what a walk-in tub costs installed</a>.</p></div></section>%s') % (
            B.call_btn(), B.quote_btn(), tiles, B.band())
        il = {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": B.DOMAIN + "/guides/%s/" % g["slug"], "name": g["h1"]} for i, g in enumerate(guides)]}
        B.page("guides/", "Walk-In Tub Buying Guides: Fit, Delivery, Specs, Where to Buy",
               "Walk-in tub buying guides: will it fit, delivery and white glove, rough-in specs, buying online, and big-box stores versus a dealer.",
               body, trail=[("Guides", "/guides/")], ld=[il])


# ======================= redirects, text files =======================
REDIRECTS = None


def redirects(B):
    rows = [l.strip().split(",") for l in open("/home/claude/research/wt4l/301-MAP.csv", encoding="utf-8").read().splitlines()[1:] if l.strip()]
    fix = {"/buy-online/": "/supply-only/", "/brands/": "/walk-in-tubs/"}
    special = {"/blogs/walk-in-tubs/comfortable-safe-baths-for-bigger-bodies-why-seat-width-and-so-much-more-matters": "/walk-in-tubs/#need=wide",
               "/blogs/walk-in-tubs/different-sizes-for-walk-in-tubs": "/specs/",
               "/blogs/walk-in-tubs/u-s-a-made-walk-in-tubs-with-leading-lifetime-warranties": "/brands/rane/",
               "/blogs/walk-in-tubs/usa-made-walk-in-bathtubs-the-best-quality-lifetime-warranties-and-unbeatable-discounts": "/brands/rane/",
               "/blogs/walk-in-tubs/walk-in-bath-tubs-2025-models-youll-want-to-check-out": "/walk-in-tubs/",
               "/products/3052-2851-walk-in-tub": "/tubs/hydro-dimensions-3052/",
               "/collections/frontpage": "/walk-in-tubs/", "/collections/all": "/walk-in-tubs/",
               "/search": "/walk-in-tubs/", "/pages/walk-in-tub-planner": "/planner/"}
    done = set()
    for old, new in rows:
        if old in done:
            continue
        done.add(old)
        to = special.get(old, fix.get(new, new))
        B.redirect(old.strip("/") + "/", to)
    B.redirect("buy-online/", "/supply-only/")


def write_text_files(prods, guides, B):
    R = B.ROOT
    import shutil
    for rel, src in B.EXTRA_BIN.items():
        fp = os.path.join(R, rel)
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        shutil.copy(src, fp)
    for rel, txt in B.EXTRA_FILES.items():
        fp = os.path.join(R, rel)
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        open(fp, "w", encoding="utf-8").write(txt)
    # sitemap
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in B.SITEMAP:
        pr = "1.0" if p == "" else "0.9" if p in ("walk-in-tubs/", "quote/") else "0.8" if p.startswith(("brands/", "tubs/")) else "0.6"
        sm.append("<url><loc>%s/%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>" % (B.DOMAIN, p, B.TODAY, pr))
    sm.append("</urlset>")
    open(os.path.join(R, "sitemap.xml"), "w").write("\n".join(sm) + "\n")
    bots = ["*", "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "anthropic-ai", "PerplexityBot", "Google-Extended", "Applebot-Extended"]
    open(os.path.join(R, "robots.txt"), "w").write("".join("User-agent: %s\nAllow: /\n\n" % b for b in bots) + "Sitemap: %s/sitemap.xml\n" % B.DOMAIN)
    # llms.txt
    L = ["# Walk-In Tubs 4 Less", "",
         "> Online walk-in tub store of Aging Safely Baths (Denver, Colorado). Every tub can be bought two ways: Supply only (shipped by freight to the buyer's curb or driveway in the US or Canada, with free phone tech support for the installer) or Fully installed (factory-certified installer; a full site visit before install; old tub removed and hauled away; 1 day in most homes). Prices are given by itemized written quote; no card checkout online. Phone 1-888-779-2284.", "",
         "Parent company: Aging Safely Baths (https://www.agingsafelybaths.com/), legal name Aging Safely Baths & More, LLC, BBB A+ accredited since 2012, Google rating 4.9 (35 reviews, Oct 2026). Hours 7am to 8pm Mountain, 7 days. Email sales@agingsafelybaths.com.",
         "Machine-readable business facts: https://www.agingsafelybaths.com/facts.json",
         "Installed walk-in tub jobs: $15,250 to $20,000 after current promotions (Aging Safely Baths published range). Supply-only prices: by written quote.",
         "Process: itemized written quote by phone or from photos; no high-pressure sales visit; a factory-certified tech does a full site visit before an installed job.",
         "Warranty: each maker's terms apply. Hydro Dimensions: lifetime on shell, frame, finish, door seal, motors and controls. Ella's Bubbles: lifetime on shell, frame and door gasket. Meditub: 10 years on shell, lifetime door seal. Rane: 5 years on shell, lifetime door seal. ANZZI: lifetime on the door seal.",
         "Updated: %s" % B.TODAY, "", "## Brands"]
    for k in B.BRAND_ORDER:
        L.append("- [%s](%s/brands/%s/): %d models. %s." % (B.P.BRANDS[k]["name"], B.DOMAIN, k, sum(1 for p in prods if p["brand"] == k), BRAND_LINE_LONG[k][0]))
    L += ["", "## Key pages",
          "- [All walk-in tubs, filterable](%s/walk-in-tubs/)" % B.DOMAIN,
          "- [Supply only: buy a walk-in tub online](%s/supply-only/)" % B.DOMAIN,
          "- [Fully installed: delivery, removal and installation](%s/white-glove/)" % B.DOMAIN,
          "- [Compare tubs side by side](%s/compare/)" % B.DOMAIN,
          "- [Specs and rough-in dimensions for every model](%s/specs/)" % B.DOMAIN,
          "- [Fit planner](%s/planner/)" % B.DOMAIN,
          "- [Get a written price](%s/quote/)" % B.DOMAIN,
          "- [Buying FAQ](%s/faq/)" % B.DOMAIN, "- [About](%s/about/)" % B.DOMAIN]
    if guides:
        L += ["", "## Guides"] + ["- [%s](%s/guides/%s/): %s" % (g["h1"], B.DOMAIN, g["slug"], g["desc"]) for g in guides]
    L += ["", "## Products (outside width x length, inches; door)"]
    for p in prods:
        L.append("- [%s](%s%s): %s; %s door%s%s" % (p["name"], B.DOMAIN, p["url"], p["size"], p["door_label"].lower(),
                                                   ("; seat height %s in." % B.fmt(p["seat_h"])) if p.get("seat_h") else "",
                                                   ("; step-in %s in." % B.fmt(p["step"])) if p.get("step") else ""))
    L += ["", "## Facts we state carefully", "- Original Medicare generally does not cover walk-in tubs.",
          "- No bathing product eliminates the risk of falls; walk-in tubs are designed to reduce risk when installed and used properly.",
          "- Specs come from manufacturers' published spec sheets and factory drawings."]
    open(os.path.join(R, "llms.txt"), "w").write("\n".join(L) + "\n")
    # 404
    nf = B.PAGES_404
    open(os.path.join(R, "404.html"), "w").write(nf)


def notfound(B):
    body = ('<section class="hero sm"><div class="wrap"><div><h1>We Could Not Find That Page</h1><p class="lead">The tub you want is probably one click away.</p>'
            '<div class="ctas">%s%s</div></div></div></section><section class="sec"><div class="wrap narrow prose"><ul class="dots">'
            '<li><a href="/walk-in-tubs/">All walk-in tubs</a></li><li><a href="/brands/">Brands</a></li><li><a href="/supply-only/">Supply only</a></li><li><a href="/white-glove/">Fully installed</a></li><li><a href="/guides/">Guides</a></li></ul></div></section>') % (B.call_btn(), B.quote_btn())
    B.page("404.html", "Page Not Found | Walk-In Tubs 4 Less", "That page is not here. Browse every walk-in tub, or call 1-888-779-2284 for help.", body, index=False)
    B.PAGES_404 = B.PAGES.pop("404.html")


# ======================= orchestrate =======================
B_ = None


def build(prods, guides, B):
    global B_
    B_ = B
    B.ALL = prods
    B.EXTRA_FILES = {}
    B.EXTRA_BIN = {}
    GUIDE_SLUGS.update(g["slug"] for g in guides)
    home(B, prods, guides)
    collection(B, prods)
    brands_index(B, prods)
    for k in B.BRAND_ORDER:
        brand_hub(k, B, prods)
    for p in prods:
        product_page(p, B)
    compare(B, prods)
    specs(B, prods)
    quote(B)
    supply(B)
    installed(B)
    about(B)
    faq(B)
    tech(B)
    planner(B, prods)
    legal(B)
    guide_pages(B, guides, prods)
    redirects(B)
    notfound(B)
