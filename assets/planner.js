/* Walk-in tub planner: client-side fit check. Sizes = makers' spec sheets (same data as the tub pages). */
(function () {
  "use strict";
  var TUBS = [
    { name: "ANZZI Value Series 30 x 60 Soaker", url: "../tubs/anzzi-value-series-30x60-soaking/", model: "AZB3060WS", w: 30, l: 60, ext: 0, gal: null, transfer: false, jets: false },
    { name: "ANZZI Coupe Premier 28 x 53 Soaker", url: "../tubs/anzzi-coupe-premier-28x53-soaking/", model: "AZ2853S", w: 28, l: 53, ext: 7, gal: null, transfer: false, jets: false },
    { name: "Rane RK12 Winnipeg transfer tub", url: "../tubs/rane-rk12-winnipeg/", model: "RK12 Winnipeg", w: 33.25, l: 61.5, ext: 0, gal: 48, transfer: true, jets: true }
  ];
  function num(id) { var v = parseFloat(document.getElementById(id).value); return isNaN(v) ? null : v; }
  function radio(n) { var r = document.querySelector("input[name='" + n + "']:checked"); return r ? r.value : ""; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  document.addEventListener("DOMContentLoaded", function () {
    var f = document.getElementById("planner"), out = document.getElementById("pl-out");
    if (!f) { return; }
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      var door = num("pl-door"), len = num("pl-len"), wid = num("pl-wid"), heater = num("pl-heater");
      var drain = radio("pl-drain"), who = radio("pl-who");
      if (door === null || len === null || wid === null) {
        out.innerHTML = '<h2 class="h3">Your results</h2><p class="err">Please enter the doorway, alcove length and alcove depth in inches.</p>';
        return;
      }
      var rows = TUBS.map(function (t) {
        var why = [], ok = true;
        if (t.w + 2 > door) { ok = false; why.push("needs about " + (t.w + 2) + " in. of doorway (yours: " + door + ")"); }
        var fill = t.l + t.ext;
        if (fill - 0.75 > len) { ok = false; why.push("needs about " + t.l + " in. of wall-to-wall length"); }
        else if (len - fill > 3) { why.push("leaves " + (len - fill).toFixed(1) + " in. to fill with a panel or wall build-out"); }
        if (t.w > wid + 0.5) { ok = false; why.push("is " + t.w + " in. deep; your alcove is " + wid); }
        if (t.ext && ok && len >= 59) { why.push("uses the included " + t.ext + " in. extension kit"); }
        if (who === "wheelchair" && !t.transfer) { why.push("not a transfer-height tub, so check with us for a wheelchair user"); }
        return { t: t, ok: ok, why: why };
      });
      var fits = rows.filter(function (r) { return r.ok; });
      var html = '<h2 class="h3">Your results</h2>';
      html += fits.length ? "<p><b>" + fits.length + " of " + rows.length + "</b> tubs with full spec pages pass your numbers.</p>" : "<p><b>None of our spec-page tubs pass all three size checks.</b> That's common in tight older homes; there are narrower and shorter models we can price for you.</p>";
      html += '<ul class="pl-list">' + rows.map(function (r) {
        return '<li class="' + (r.ok ? "pl-ok" : "pl-no") + '"><b>' + (r.ok ? "Fits: " : "Doesn't fit: ") + '<a href="' + r.t.url + '">' + esc(r.t.name) + "</a></b>" + (r.why.length ? "<br><span>" + esc(r.why.join("; ")) + "</span>" : "") + "</li>";
      }).join("") + "</ul>";
      if (heater !== null) {
        html += heater === 0 ? "<p><b>Hot water:</b> tankless heaters fill steadily; check that its flow rate can keep up with the tub's faucet.</p>"
          : "<p><b>Hot water:</b> your tank is " + heater + " gallons. The RK12 holds 48 gallons at overflow; for other tubs compare the fill volume on the spec sheet. A tank smaller than the fill volume will likely run lukewarm before the tub is full.</p>";
      }
      if (drain === "unsure") { html += "<p><b>Drain side:</b> stand facing where the tub will go and note which end the drain is on. Walk-in tubs are ordered left or right.</p>"; }
      if (who === "wheelchair") { html += "<p><b>Wheelchair or lift:</b> look for a transfer-height seat and an outward-swinging door on your transfer side.</p>"; }
      var note = "Planner: doorway " + door + " in, alcove " + len + " x " + wid + " in, heater " + (heater === null ? "?" : heater) + " gal, drain " + drain + ", bather " + who;
      var pick = fits.length ? fits[0].t.model : "";
      html += '<a class="btn btn-b full" href="../quote/?note=' + encodeURIComponent(note) + (pick ? "&tub=" + encodeURIComponent(pick) : "") + '">Send these numbers with a price request</a>';
      out.innerHTML = html;
      out.focus && out.setAttribute("tabindex", "-1");
      if (window.innerWidth < 980) { out.scrollIntoView({ behavior: "smooth", block: "start" }); }
    });
  });
})();
