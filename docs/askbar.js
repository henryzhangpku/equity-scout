/* Floating "ask" bar: a shortcut to the Ask your own question box from anywhere on the page.
   It reuses the existing box (try.js): fills #ask-text, scrolls to #try and presses #ask-go.
   Enter asks, Shift+Enter adds a line, "/" or Ctrl/Cmd+K focuses it, Esc leaves it. On focus it offers the
   one-click examples (they answer instantly from the snapshot, even when live analysis is offline). */
(function () {
  "use strict";
  var KEY = "scout-askbar-hidden", MAX = 500;
  function hidden() { try { return sessionStorage.getItem(KEY) === "1"; } catch (e) { return false; } }
  function setHidden(v) { try { sessionStorage.setItem(KEY, v ? "1" : "0"); } catch (e) { /* storage blocked */ } }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  var mac = /Mac|iPhone|iPad/.test(navigator.platform || "");

  var IDEAS = [
    "Large caps with daily RSI under 30",
    "Profitable small caps down 40% from their highs",
    "Fast growers over $2B beating the S&P 500",
    "Heavily shorted names back above the 50-day average",
    "Cheap on free cash flow with net cash"
  ];
  var CHIPS = (window.SCOUT_CHIPS || []).slice(0, 4);

  var SPARK = '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M12 2l1.9 5.6L19.5 9.5l-5.6 1.9L12 17l-1.9-5.6L4.5 9.5l5.6-1.9zM19 14l.9 2.6 2.6.9-2.6.9L19 21l-.9-2.6-2.6-.9 2.6-.9z"/></svg>';
  var ARROW = '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M5 12h11.6l-4.3-4.3 1.4-1.4L20.4 13l-6.7 6.7-1.4-1.4 4.3-4.3H5z" transform="translate(0 -1)"/></svg>';

  var wrap = document.createElement("div");
  wrap.id = "askbar-wrap";
  wrap.innerHTML =
    '<div id="askbar-pop" class="askpop" hidden>' +
      '<div class="askpop-hd"><span>One click, instant answer</span><span class="askpop-keys"><kbd>Enter</kbd> ask &middot; <kbd>Shift</kbd>+<kbd>Enter</kbd> new line &middot; <kbd>Esc</kbd> close</span></div>' +
      '<div class="askpop-list">' + CHIPS.map(function (c) {
        return '<button type="button" class="askpop-item" data-chip="' + esc(c.id) + '"><span class="askpop-ico">' + SPARK + "</span>" + esc(c.label) + "</button>";
      }).join("") + "</div>" +
      '<p class="askpop-foot">Or write your own idea. The model proposes a screen; code checks it, runs it on about 3,800 companies and backtests it.</p>' +
    "</div>" +
    '<form id="askbar" aria-label="Ask your own question">' +
      '<span class="askbar-ico" aria-hidden="true">' + SPARK + "</span>" +
      '<textarea id="askbar-text" rows="1" maxlength="' + MAX + '" autocomplete="off" aria-label="Your investment idea" placeholder="' + esc(IDEAS[0]) + '"></textarea>' +
      '<span id="askbar-status" class="askbar-status" title="Live analysis status"><span class="dot"></span><span class="lbl">Snapshot</span></span>' +
      '<span id="askbar-count" class="askbar-count" hidden></span>' +
      '<kbd class="askbar-kbd" aria-hidden="true">' + (mac ? "&#8984;K" : "Ctrl K") + "</kbd>" +
      '<button type="submit" id="askbar-go" class="askbar-go" disabled aria-label="Analyze">' + ARROW + '<span>Analyze</span></button>' +
      '<button type="button" id="askbar-close" class="askbar-x" aria-label="Hide the ask bar">&times;</button>' +
    "</form>";
  var tab = document.createElement("button");
  tab.id = "askbar-tab"; tab.type = "button";
  tab.innerHTML = SPARK + "<span>Ask</span>";
  tab.setAttribute("aria-label", "Show the ask bar");
  document.body.appendChild(wrap);
  document.body.appendChild(tab);
  document.body.classList.add("has-askbar");

  var bar = document.getElementById("askbar"), text = document.getElementById("askbar-text"),
      go = document.getElementById("askbar-go"), pop = document.getElementById("askbar-pop"),
      count = document.getElementById("askbar-count"), status = document.getElementById("askbar-status");

  var inTry = false;
  function render() {
    var h = hidden();
    wrap.classList.toggle("off", h || inTry);
    tab.classList.toggle("off", !h || inTry);
    if (h || inTry) pop.hidden = true;
  }

  // auto-grow up to 5 lines; the counter appears near the limit; Analyze is enabled only with text
  function sync() {
    text.style.height = "auto";
    if (text.value) text.style.height = Math.min(text.scrollHeight, 132) + "px";  // empty: one line, placeholder clipped
    var n = text.value.length;
    count.hidden = n < MAX - 100;
    count.textContent = (MAX - n) + " left";
    go.disabled = !text.value.trim();
    wrap.classList.toggle("multi", !!text.value && text.scrollHeight > 48);
  }

  // rotate the placeholder through example ideas while the bar is empty and not focused
  var pi = 0;
  setInterval(function () {
    if (document.activeElement === text || text.value) return;
    pi = (pi + 1) % IDEAS.length;
    text.setAttribute("placeholder", IDEAS[pi]);
  }, 4000);

  // mirror the live/snapshot pill from the Try section
  function mirror() {
    var p = document.getElementById("api-status");
    if (!p) return;
    var live = /live/i.test(p.textContent) && !/offline/i.test(p.textContent);
    status.classList.toggle("live", live);
    status.querySelector(".lbl").textContent = live ? "Live" : "Snapshot";
    status.title = live ? "Live: your question is translated and run now" : "Live analysis is offline: the examples still answer instantly";
  }
  var pillEl = document.getElementById("api-status");
  if (pillEl && "MutationObserver" in window) new MutationObserver(mirror).observe(pillEl, { childList: true, subtree: true, characterData: true, attributes: true });
  mirror();

  function submit() {
    var q = text.value.trim();
    var box = document.getElementById("ask-text"), btn = document.getElementById("ask-go");
    var sec = document.getElementById("try");
    pop.hidden = true;
    if (sec) sec.scrollIntoView({ behavior: "smooth", block: "start" });
    if (!q || !box || !btn) { if (box) box.focus(); return; }
    box.value = q;
    go.classList.add("busy");
    // The live check (try.js) can still be running on a fresh page: wait up to 6 s for "Live", then press anyway.
    var t0 = Date.now();
    (function press() {
      var p = document.getElementById("api-status");
      var live = p && /live/i.test(p.textContent) && !/offline/i.test(p.textContent);
      if (!live && Date.now() - t0 < 6000) { setTimeout(press, 250); return; }
      go.classList.remove("busy");
      if (!btn.disabled) btn.click();
    })();
  }

  bar.addEventListener("submit", function (e) { e.preventDefault(); submit(); });
  text.addEventListener("input", sync);
  text.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey && !e.isComposing) { e.preventDefault(); if (text.value.trim()) submit(); }
    if (e.key === "Escape") { pop.hidden = true; text.blur(); }
  });
  text.addEventListener("focus", function () { if (CHIPS.length && !text.value) pop.hidden = false; wrap.classList.add("focus"); });
  text.addEventListener("blur", function () { wrap.classList.remove("focus"); setTimeout(function () { if (!wrap.contains(document.activeElement)) pop.hidden = true; }, 150); });
  pop.addEventListener("mousedown", function (e) { e.preventDefault(); }); // keep focus while picking
  pop.querySelectorAll("[data-chip]").forEach(function (b) {
    b.addEventListener("click", function () {
      pop.hidden = true;
      var chip = document.querySelector('#chips [data-chip="' + b.getAttribute("data-chip") + '"]');
      if (chip) chip.click();
    });
  });
  document.getElementById("askbar-close").addEventListener("click", function () { setHidden(true); render(); });
  tab.addEventListener("click", function () { setHidden(false); render(); text.focus(); });

  // "/" or Ctrl/Cmd+K focuses the bar from anywhere (not while typing elsewhere)
  document.addEventListener("keydown", function (e) {
    var t = e.target, typing = t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable);
    var k = (e.key === "k" || e.key === "K") && (e.metaKey || e.ctrlKey);
    if (!(k || (e.key === "/" && !typing))) return;
    if (inTry) { var box = document.getElementById("ask-text"); if (box) { e.preventDefault(); box.focus(); } return; }
    e.preventDefault();
    if (hidden()) { setHidden(false); render(); }
    text.focus();
  });

  // Out of the way while the Try box or the hero's idea cards and examples are on screen (they are the same entry points).
  var watched = ["ask", "ideas", "chips"].map(function (id) { return document.getElementById(id); }).filter(Boolean);
  if (watched.length && "IntersectionObserver" in window) {
    var seen = {};
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { seen[e.target.id] = e.isIntersecting; });
      inTry = Object.keys(seen).some(function (k) { return seen[k]; });
      render();
    });
    watched.forEach(function (el) { io.observe(el); });
  }
  sync();
  render();
})();
