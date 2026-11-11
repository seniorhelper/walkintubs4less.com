/* walkintubs4less: form guard (runs in the capture phase, before lead-send.js).
   Blocks bots (filled honeypot or submit < 3 s after load), checks required fields + consent,
   and pre-selects path/tub from ?path= and ?tub= links. Sending is done by lead-send.js. */
(function () {
  "use strict";
  var loaded = Date.now();
  var q = new URLSearchParams(location.search);
  document.addEventListener("DOMContentLoaded", function () {
    var f = document.querySelector("form[data-lead]");
    if (!f) { return; }
    var path = q.get("path");
    if (path === "supply") { var a = f.querySelector("#p-supply"); if (a) { a.checked = true; } }
    if (path === "whiteglove") { var b = f.querySelector("#p-wg"); if (b) { b.checked = true; } }
    var tub = (q.get("tub") || "").slice(0, 60);
    var sel = f.querySelector("#f-tub");
    if (tub && sel) {
      var hit = Array.prototype.some.call(sel.options, function (o) { if (o.value === tub) { o.selected = true; return true; } return false; });
      if (!hit) { var n = f.querySelector("#f-notes"); if (n && !n.value) { n.value = "Model: " + tub; } }
    }
    var note = (q.get("note") || "").slice(0, 300);
    if (note) { var nn = f.querySelector("#f-notes"); if (nn) { nn.value = (nn.value ? nn.value + " | " : "") + note; } }
  });
  document.addEventListener("submit", function (e) {
    var f = e.target;
    if (!f || !f.matches || !f.matches("form[data-lead]")) { return; }
    var err = f.querySelector(".err");
    function stop(msg) {
      e.preventDefault(); e.stopImmediatePropagation();
      if (err && msg) { err.textContent = msg; err.hidden = false; err.focus && err.setAttribute("tabindex", "-1"); err.focus(); }
    }
    var hp = f.querySelector("[name=_honey]");
    if (hp && hp.value.trim()) { stop(""); f.innerHTML = "<p role=status>Thank you.</p>"; return; }
    if (Date.now() - loaded < 3000) { stop("Please take a moment to check your details, then press send again."); return; }
    var name = f.querySelector("[name=name]"), phone = f.querySelector("[name=phone]"), zip = f.querySelector("[name=zip]"), consent = f.querySelector("[name=consent]");
    if (!name.value.trim()) { stop("Please enter your name."); name.focus(); return; }
    if ((phone.value.match(/\d/g) || []).length < 10) { stop("Please enter a 10-digit phone number so we can reach you."); phone.focus(); return; }
    if (zip && !/^\d{5}(-\d{4})?$/.test(zip.value.trim())) { stop("Please enter a 5-digit ZIP code."); zip.focus(); return; }
    if (consent && !consent.checked) { stop("Please tick the box so we're allowed to contact you about your request."); consent.focus(); return; }
    if (err) { err.hidden = true; }
  }, true);
})();
