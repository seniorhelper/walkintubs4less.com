/* walkintubs4less.com v2 (2026-11-17)
   1) Form guard (runs in the capture phase, before lead-send.js): blocks bots (filled honeypot or
      submit < 3 s after load), checks required fields + consent, pre-selects path/tub from ?path= / ?tub=.
      Sending is done by lead-send.js (unchanged).
   2) Menus, product gallery, collection filters, compare tool. No libraries. */
(function () {
  "use strict";
  var loaded = Date.now();
  var q = new URLSearchParams(location.search);
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }

  document.addEventListener("DOMContentLoaded", function () {
    /* ---- forms: pre-fill ---- */
    var f = $("form[data-lead]");
    if (f) {
      var path = q.get("path");
      var map = { supply: "#p-supply", installed: "#p-inst", whiteglove: "#p-inst", both: "#p-both" };
      if (path && map[path]) { var r = $(map[path], f); if (r) { r.checked = true; } }
      var tub = (q.get("tub") || "").slice(0, 80);
      var sel = $("#f-tub", f);
      if (tub && sel && sel.tagName === "SELECT") {
        var hit = $$("option", sel).some(function (o) { if (o.value === tub) { o.selected = true; return true; } return false; });
        if (!hit) { var n = $("#f-notes", f); if (n && !n.value) { n.value = "Model: " + tub; } }
      }
      var note = (q.get("note") || "").slice(0, 300);
      if (note) { var nn = $("#f-notes", f); if (nn) { nn.value = (nn.value ? nn.value + " | " : "") + note; } }
    }
    /* product page: path choice outside a form updates the price link */
    $$("[data-path-link]").forEach(function (a) {
      var box = document.getElementById(a.getAttribute("data-path-link"));
      if (!box) { return; }
      function upd() {
        var c = $("input[type=radio]:checked", box);
        var u = new URL(a.getAttribute("href"), location.href);
        if (c) { u.searchParams.set("path", c.value); }
        a.setAttribute("href", u.pathname + u.search + "#price-form");
        $$("input[name=path]", f || document).forEach(function (x) { if (c && x.getAttribute("data-key") === c.value) { x.checked = true; } });
      }
      box.addEventListener("change", upd); upd();
    });

    /* ---- header menus ---- */
    var mb = $(".menu-btn"), dr = $("#drawer");
    if (mb && dr) {
      mb.addEventListener("click", function () {
        var o = dr.classList.toggle("open");
        mb.setAttribute("aria-expanded", o ? "true" : "false");
      });
    }
    $$("[data-mega]").forEach(function (b) {
      var p = document.getElementById(b.getAttribute("aria-controls"));
      if (!p) { return; }
      b.addEventListener("click", function (e) {
        e.stopPropagation();
        var o = !p.classList.contains("open");
        $$(".mega.open").forEach(function (m) { m.classList.remove("open"); });
        $$("[data-mega]").forEach(function (x) { x.setAttribute("aria-expanded", "false"); });
        if (o) { p.classList.add("open"); b.setAttribute("aria-expanded", "true"); }
      });
    });
    document.addEventListener("click", function (e) {
      if (!e.target.closest || !e.target.closest(".mega")) {
        $$(".mega.open").forEach(function (m) { m.classList.remove("open"); });
        $$("[data-mega]").forEach(function (x) { x.setAttribute("aria-expanded", "false"); });
      }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { $$(".mega.open").forEach(function (m) { m.classList.remove("open"); }); $$("[data-mega]").forEach(function (x) { x.setAttribute("aria-expanded", "false"); }); }
    });

    /* ---- gallery ---- */
    var gm = $(".gal-main");
    if (gm) {
      $$(".thumbs button").forEach(function (t) {
        t.addEventListener("click", function () {
          var tpl = t.querySelector("template");
          gm.innerHTML = tpl ? tpl.innerHTML : t.innerHTML;
          $$(".thumbs button").forEach(function (x) { x.setAttribute("aria-pressed", "false"); });
          t.setAttribute("aria-pressed", "true");
          var cap = $(".gal .cap"); if (cap) { cap.textContent = t.getAttribute("data-cap") || ""; }
        });
      });
    }

    /* ---- collection filters ---- */
    var fl = $("#filters");
    if (fl) {
      var cards = $$("#tub-grid .pcard"), cnt = $("#f-count"), empty = $("#f-empty");
      var tg = $(".f-toggle");
      if (tg) { tg.addEventListener("click", function () { var c = fl.classList.toggle("closed"); tg.setAttribute("aria-expanded", c ? "false" : "true"); }); }
      function apply() {
        var groups = {};
        $$("input[type=checkbox]:checked", fl).forEach(function (i) { (groups[i.name] = groups[i.name] || []).push(i.value); });
        var shown = 0;
        cards.forEach(function (c) {
          var ok = Object.keys(groups).every(function (g) {
            var v = (c.getAttribute("data-" + g) || "").split(" ");
            return groups[g].some(function (x) { return v.indexOf(x) >= 0; });
          });
          c.hidden = !ok; if (ok) { shown++; }
        });
        if (cnt) { cnt.textContent = shown + (shown === 1 ? " tub" : " tubs"); }
        if (empty) { empty.hidden = shown !== 0; }
        var keys = $$("input[type=checkbox]:checked", fl).map(function (i) { return i.name + "=" + i.value; });
        try { history.replaceState(null, "", keys.length ? "#" + keys.join("&") : location.pathname); } catch (e) { /* ignore */ }
      }
      fl.addEventListener("change", apply);
      var rs = $(".f-reset", fl);
      if (rs) { rs.addEventListener("click", function () { $$("input[type=checkbox]", fl).forEach(function (i) { i.checked = false; }); apply(); }); }
      function fromHash() {
        var h = location.hash.replace(/^#/, "");
        if (!h) { return; }
        h.split("&").forEach(function (kv) {
          var p = kv.split("="); var i = fl.querySelector("input[name='" + p[0] + "'][value='" + (p[1] || "") + "']");
          if (i) { i.checked = true; }
        });
      }
      fromHash(); apply();
      window.addEventListener("hashchange", function () { $$("input[type=checkbox]", fl).forEach(function (i) { i.checked = false; }); fromHash(); apply(); });
    }

    /* ---- compare ---- */
    var cd = document.getElementById("cmp-data");
    if (cd) {
      var D = JSON.parse(cd.textContent), sels = $$(".cmp-pick select"), out = $("#cmp-out");
      var pre = (q.get("m") || "").split(",").filter(Boolean);
      sels.forEach(function (s, i) { if (pre[i]) { s.value = pre[i]; } s.addEventListener("change", draw); });
      function esc(x) { return String(x == null ? "" : x).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
      function draw() {
        var pick = sels.map(function (s) { return D.items[s.value]; }).filter(Boolean);
        if (!pick.length) { out.innerHTML = '<p class="empty">Pick two or three tubs above to see them side by side.</p>'; return; }
        var h = '<div class="tbl-wrap"><table class="data cmp"><thead><tr><th scope="col">Spec</th>';
        pick.forEach(function (p) { h += '<th scope="col">' + esc(p.name) + "</th>"; });
        h += "</tr></thead><tbody>";
        D.rows.forEach(function (r) {
          if (!pick.some(function (p) { return p[r[0]]; })) { return; }
          h += '<tr><th scope="row">' + esc(r[1]) + "</th>";
          pick.forEach(function (p) { h += "<td>" + (esc(p[r[0]]) || "Ask us") + "</td>"; });
          h += "</tr>";
        });
        h += '<tr><th scope="row">Details</th>';
        pick.forEach(function (p) { h += '<td><a href="' + esc(p.url) + '">View tub</a> &middot; <a href="/quote/?tub=' + encodeURIComponent(p.model) + '">Get price</a></td>'; });
        h += "</tr></tbody></table></div>";
        out.innerHTML = h;
        try { history.replaceState(null, "", "?m=" + sels.map(function (s) { return s.value; }).filter(Boolean).join(",")); } catch (e) { /* ignore */ }
      }
      draw();
    }
  });

  /* ---- form guard (capture phase, before lead-send.js) ---- */
  document.addEventListener("submit", function (e) {
    var f = e.target;
    if (!f || !f.matches || !f.matches("form[data-lead]")) { return; }
    var err = f.querySelector(".err");
    function stop(msg) {
      e.preventDefault(); e.stopImmediatePropagation();
      if (err && msg) { err.textContent = msg; err.hidden = false; err.setAttribute("tabindex", "-1"); err.focus(); }
    }
    var hp = f.querySelector("[name=_honey]");
    if (hp && hp.value.trim()) { stop(""); f.innerHTML = "<p role=status>Thank you.</p>"; return; }
    if (Date.now() - loaded < 3000) { stop("Please take a moment to check your details, then press send again."); return; }
    var name = f.querySelector("[name=name]"), phone = f.querySelector("[name=phone]"), zip = f.querySelector("[name=zip]"), consent = f.querySelector("[name=consent]");
    if (!name.value.trim()) { stop("Please enter your name."); name.focus(); return; }
    if ((phone.value.match(/\d/g) || []).length < 10) { stop("Please enter a 10-digit phone number so we can reach you."); phone.focus(); return; }
    if (zip && !/^\d{5}(-\d{4})?$/.test(zip.value.trim()) && !/^[A-Za-z]\d[A-Za-z][ -]?\d[A-Za-z]\d$/.test(zip.value.trim())) { stop("Please enter a 5-digit ZIP code (or a Canadian postal code)."); zip.focus(); return; }
    if (consent && !consent.checked) { stop("Please tick the box so we're allowed to contact you about your request."); consent.focus(); return; }
    if (err) { err.hidden = true; }
  }, true);
})();
