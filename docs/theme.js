/* Light/dark theme: follows the system setting until the visitor picks one; the choice is remembered when storage works. */
(function () {
  "use strict";
  var KEY = "scout-theme";
  function stored() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function save(v) { try { localStorage.setItem(KEY, v); } catch (e) { /* private mode: keep it for this page only */ } }
  function system() { return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"; }
  function current() { return document.documentElement.getAttribute("data-theme") || system(); }
  function apply(v) { document.documentElement.setAttribute("data-theme", v); paint(); }
  var s = stored();
  var q = /[?&]theme=(light|dark)/.exec(location.search);   // for previews and screenshots; not saved
  if (q) s = q[1];
  if (s === "light" || s === "dark") document.documentElement.setAttribute("data-theme", s);

  function paint() {
    var b = document.getElementById("theme-toggle");
    if (!b) return;
    var dark = current() === "dark";
    b.setAttribute("aria-label", dark ? "Switch to light theme" : "Switch to dark theme");
    b.title = b.getAttribute("aria-label");
    b.innerHTML = dark
      ? '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><circle cx="12" cy="12" r="4.5" fill="currentColor"/><g stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></g></svg>'
      : '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path fill="currentColor" d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>';
  }
  document.addEventListener("DOMContentLoaded", function () {
    var b = document.getElementById("theme-toggle");
    if (!b) return;
    paint();
    b.addEventListener("click", function () { var v = current() === "dark" ? "light" : "dark"; save(v); apply(v); });
    if (window.matchMedia) {
      var mq = window.matchMedia("(prefers-color-scheme: dark)");
      var onChange = function () { if (!stored()) paint(); };
      if (mq.addEventListener) mq.addEventListener("change", onChange); else if (mq.addListener) mq.addListener(onChange);
    }
  });
})();
