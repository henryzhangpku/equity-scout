/* Floating "ask" bar: a shortcut to the Ask your own question box from anywhere on the page.
   It reuses the existing box (try.js): fills #ask-text, scrolls to #try and presses #ask-go. */
(function () {
  "use strict";
  var KEY = "scout-askbar-hidden";
  function hidden() { try { return sessionStorage.getItem(KEY) === "1"; } catch (e) { return false; } }
  function setHidden(v) { try { sessionStorage.setItem(KEY, v ? "1" : "0"); } catch (e) { /* storage blocked */ } }

  var bar = document.createElement("form");
  bar.id = "askbar";
  bar.setAttribute("aria-label", "Ask your own question");
  bar.innerHTML =
    '<input id="askbar-text" type="text" maxlength="500" autocomplete="off" ' +
    'placeholder="Ask anything, e.g. Large caps with daily RSI under 30">' +
    '<button type="submit" class="primary">Analyze</button>' +
    '<button type="button" id="askbar-close" class="askbar-x" aria-label="Hide">&times;</button>';
  var tab = document.createElement("button");
  tab.id = "askbar-tab"; tab.type = "button"; tab.textContent = "Ask";
  tab.setAttribute("aria-label", "Show the ask bar");
  document.body.appendChild(bar);
  document.body.appendChild(tab);
  document.body.classList.add("has-askbar");

  var inTry = false;
  function render() {
    var h = hidden();
    bar.classList.toggle("off", h || inTry);
    tab.classList.toggle("off", !h || inTry);
  }

  bar.addEventListener("submit", function (e) {
    e.preventDefault();
    var q = document.getElementById("askbar-text").value.trim();
    var box = document.getElementById("ask-text"), go = document.getElementById("ask-go");
    var sec = document.getElementById("try");
    if (sec) sec.scrollIntoView({ behavior: "smooth", block: "start" });
    if (!q || !box || !go) { if (box) box.focus(); return; }
    box.value = q;
    // The live check (try.js) can still be running on a fresh page: wait up to 6 s for "Live", then press anyway.
    var pill = document.getElementById("api-status"), t0 = Date.now();
    (function press() {
      var live = pill && /live/i.test(pill.textContent);
      if (!live && Date.now() - t0 < 6000) { setTimeout(press, 250); return; }
      if (!go.disabled) go.click();
    })();
  });
  document.getElementById("askbar-close").addEventListener("click", function () { setHidden(true); render(); });
  tab.addEventListener("click", function () { setHidden(false); render(); document.getElementById("askbar-text").focus(); });

  var ask = document.getElementById("ask");
  if (ask && "IntersectionObserver" in window) {
    new IntersectionObserver(function (es) { inTry = es[0].isIntersecting; render(); }).observe(ask);
  }
  render();
})();
