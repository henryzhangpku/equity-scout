(function () {
  "use strict";
  // The morning brief: the investor team's own ideas, each screened and backtested by code; only edges survive.
  var B = window.SCOUT_BRIEF, U = window.ScoutUI, esc = U.esc;
  var el = document.getElementById("brief-body");
  if (!el) return;
  if (!B) { el.innerHTML = '<p class="muted">No brief recorded yet.</p>'; return; }
  function pct(v) { return v === null || v === undefined ? "n/a" : (v >= 0 ? "+" : "") + Math.round(v * 100) + "%"; }
  var h = ['<p class="section-intro">Recorded on the ' + esc(B.as_of) + " snapshot. " + B.n_tested + " ideas were tested; " + B.n_accepted +
    " passed every backtest gate and had names to hold. With many ideas tested, some passes are luck: an accepted idea is on probation until its forward record agrees.</p>"];
  B.ideas.filter(function (i) { return i.status === "accepted"; }).forEach(function (i, k) {
    var bt = i.backtest;
    h.push('<details class="panel disclose"' + (k === 0 ? " open" : "") + "><summary><h3>" + esc(i.observation) + "</h3></summary>");
    h.push('<p class="meta">Proposed by <strong>' + esc(i.investor_name) + "</strong>. " + i.n_ranked + " names pass today. Backtest " + esc(bt.first) +
      " to " + esc(bt.last) + ": screen <strong>" + pct(bt.total) + "</strong>, SPY " + pct(bt.spy_total) + ", equal-weight universe " + pct(bt.universe_total) +
      "; verdict <strong>" + esc(bt.verdict) + "</strong>.</p>");
    h.push('<div class="row"><button type="button" class="primary" data-open-idea="' + esc(i.id) + '">Open this idea: screen, backtest and the team&rsquo;s vote</button></div>');
    h.push("</details>");
  });
  var rej = B.ideas.filter(function (i) { return i.status !== "accepted"; });
  if (rej.length) {
    h.push('<div class="panel"><div class="step">Tested and rejected (' + rej.length + ')</div><div class="tablewrap"><table class="wrapt"><thead><tr><th>Investor</th><th>Idea</th><th>Why</th></tr></thead><tbody>');
    rej.forEach(function (i) {
      h.push("<tr><td>" + esc(i.investor_name) + "</td><td>" + esc(i.observation || "(no valid idea)") + "</td><td>" + esc(i.reason) + "</td></tr>");
    });
    h.push("</tbody></table></div></div>");
  }
  el.innerHTML = h.join("");
  el.querySelectorAll("[data-open-idea]").forEach(function (b) {
    b.onclick = function () { if (window.ScoutTry) window.ScoutTry.runIdea(b.getAttribute("data-open-idea")); };
  });
})();
