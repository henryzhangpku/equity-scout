(function () {
  "use strict";
  var RUNS = window.SCOUT_RUNS || [];
  var U = window.ScoutUI, esc = U.esc;

  function renderRun(r) {
    var h = [];
    h.push('<div class="panel"><div class="step">1 · Observation</div><blockquote class="obs">' + esc(r.observation) + "</blockquote>");
    h.push('<div class="meta">As of <strong>' + esc(r.as_of) + "</strong> (prices to " + esc(r.data.last_price_date) +
      ", FINRA short interest settlement " + esc(r.data.short_interest_settlement || "n/a") + "). Universe: " +
      esc(r.data.universe_rule) + ". " + esc(r.data.n_companies) + " companies.</div></div>");
    h.push('<div class="panel">' + U.specHtml(r.spec, "2 · The screen — proposed by " + r.llm.model + ", checked by code" + (r.attempts > 1 ? " after " + (r.attempts - 1) + " correction round" : "")) + "</div>");
    h.push('<div class="panel">' + U.funnelHtml(r.funnel, "3 · How the list narrowed (computed by code)", r.spec) + "</div>");
    h.push('<div class="panel">' + U.tableHtml(r.columns, r.ranked, r.top_n, r.n_ranked, "4 · Ranked results") + "</div>");
    if (r.sector_breakdown && r.sector_breakdown.length) h.push('<div class="panel">' + U.sectorHtml(r.sector_breakdown, "Survivors by sector (all " + r.n_ranked + ")") + "</div>");
    h.push('<div class="panel"><div class="step">5 · Why the price and the business may disagree — top ' + r.explanations.length +
      '</div><p class="muted" style="margin-top:0">Each quote was checked by code to appear verbatim in its linked source; claims that failed were removed and are listed under each card. No earnings-call transcripts were used (licensed content).</p><div class="cards">');
    r.explanations.forEach(function (ex) { h.push(U.cardHtml(ex)); });
    h.push("</div></div>");
    h.push('<div class="panel" id="bt-run"></div>');
    document.getElementById("run").innerHTML = h.join("");
    U.mountBacktest(document.getElementById("bt-run"), { key: r.id, spec: r.spec, api: null, precomputedSrc: "data/backtests.js?v=20261009b" });
  }

  var tabs = document.getElementById("tabs");
  var TITLES = { "a-midcap-pullback": "A · Mid-cap pullbacks still growing",
    "b-ai-infra-laggards": "B · AI-infrastructure laggards", "c-oversold-volume": "C · Oversold on heavy volume" };
  RUNS.forEach(function (r) {
    var b = document.createElement("button");
    b.setAttribute("role", "tab");
    b.textContent = TITLES[r.id] || r.id;
    b.onclick = function () {
      Array.prototype.forEach.call(tabs.children, function (x) { x.setAttribute("aria-selected", "false"); });
      b.setAttribute("aria-selected", "true");
      renderRun(r);
      try { history.replaceState(null, "", "#" + r.id); } catch (e) {}
    };
    tabs.appendChild(b);
  });
  var start = 0;
  RUNS.forEach(function (r, i) { if (location.hash === "#" + r.id) start = i; });
  if (tabs.children[start]) {
    tabs.children[start].setAttribute("aria-selected", "true");
    renderRun(RUNS[start]);
  }
  if (!RUNS.length) document.getElementById("run").innerHTML = '<p class="muted">No recorded runs yet.</p>';

  var T = window.SCOUT_TRACKING || {};
  var tr = document.getElementById("tracking");
  if (tr && T.marks) {
    var pct = function (v) { return v == null ? "n/a" : (v >= 0 ? "+" : "") + (v * 100).toFixed(2) + "%"; };
    var t = ['<p class="muted" style="margin-top:0"><strong>' + esc(T.label) + ".</strong> Each live run appends its top names and entry closes to an append-only, hash-chained ledger (runs/picks.jsonl); <code>scout track</code> marks them to market from Alpaca closes. Hash chain: " +
      (T.chain_ok ? "intact" : "BROKEN") + ", " + esc(T.n_entries) + " entries, generated " + esc(T.generated_at) + ".</p>"];
    t.push('<div class="tablewrap"><table><thead><tr><th class="l">Run</th><th>As of</th><th>Marked to</th><th>Trading days</th><th class="l">Picks</th><th>Basket</th><th>SPY</th><th>SMH</th><th>Basket − SPY</th><th>Basket − SMH</th></tr></thead><tbody>');
    T.marks.forEach(function (m) {
      t.push('<tr><td class="l">' + esc(m.run_id) + "</td><td>" + esc(m.as_of) + "</td><td>" + esc(m.marked_to) + "</td><td>" + m.trading_days +
        '</td><td class="l">' + m.picks.map(function (p) { return esc(p.symbol) + " " + pct(p.return); }).join(", ") + "</td><td>" + pct(m.basket_return) +
        "</td><td>" + pct(m.benchmarks.SPY) + "</td><td>" + pct(m.benchmarks.SMH) + "</td><td>" + pct(m.basket_vs.SPY) + "</td><td>" + pct(m.basket_vs.SMH) + "</td></tr>");
    });
    t.push("</tbody></table></div>");
    tr.innerHTML = t.join("");
  }
  var f = document.getElementById("foot-limits");
  if (f && RUNS.length) {
    f.innerHTML = "Recorded runs use real data as of " + esc(RUNS[0].as_of) + ". Data limits: <ul>" +
      RUNS[0].limits.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul>";
  }
})();
