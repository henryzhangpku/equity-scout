(function () {
  "use strict";
  var RUNS = window.SCOUT_RUNS || [];
  var FIELDS = window.SCOUT_FIELDS || {};

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function kind(f) { return (FIELDS[f] || {}).kind || ""; }
  function fmt(f, v) {
    if (v === null || v === undefined || v === "") return "n/a";
    if (typeof v === "boolean") return v ? "yes" : "no";
    if (typeof v === "string") return v;
    if (f === "score") return v.toFixed(3);
    var k = kind(f);
    if (k === "ratio") return (v >= 0 ? "+" : "") + (v * 100).toFixed(1) + "%";
    if (k === "usd") {
      if (Math.abs(v) >= 1e9) return "$" + (v / 1e9).toFixed(1) + "B";
      if (Math.abs(v) >= 1e6) return "$" + (v / 1e6).toFixed(0) + "M";
      return "$" + v.toFixed(2);
    }
    if (k === "days") return v.toFixed(1) + "d";
    return Number.isInteger(v) ? String(v) : v.toFixed(2);
  }
  function cond(c) {
    if (c.ref) return c.field + " " + c.op + " " + c.ref;
    if (c.op === "between") return fmt(c.field, c.value[0]) + " ≤ " + c.field + " ≤ " + fmt(c.field, c.value[1]);
    return c.field + " " + c.op + " " + fmt(c.field, c.value);
  }
  var LABELS = { rank: "#", symbol: "Ticker", name: "Company", score: "Score", market_cap: "Mkt cap" };

  function renderRun(r) {
    var h = [];
    var u = r.spec.universe || {};
    // 1 observation
    h.push('<div class="panel"><div class="step">1 · Observation</div><blockquote class="obs">' + esc(r.observation) + "</blockquote>");
    h.push('<div class="meta">As of <strong>' + esc(r.as_of) + "</strong> (prices to " + esc(r.data.last_price_date) +
      ", FINRA short interest settlement " + esc(r.data.short_interest_settlement || "n/a") + "). Universe: " +
      esc(r.data.universe_rule) + ". " + esc(r.data.n_companies) + " companies.</div></div>");
    // 2 spec
    h.push('<div class="panel"><div class="step">2 · Screen spec — proposed by ' + esc(r.llm.provider + " / " + r.llm.model) +
      ", validated by code" + (r.attempts > 1 ? " after " + (r.attempts - 1) + " correction round" : "") + "</div>");
    h.push('<div class="chips">');
    if (u.industries) h.push('<span class="chip u">industry ∈ ' + esc(u.industries.join(", ")) + "</span>");
    if (u.exclude_industries) h.push('<span class="chip u">industry ∉ ' + esc(u.exclude_industries.join(", ")) + "</span>");
    if (u.market_cap_min != null) h.push('<span class="chip u">market_cap ≥ ' + fmt("market_cap", u.market_cap_min) + "</span>");
    if (u.market_cap_max != null) h.push('<span class="chip u">market_cap ≤ ' + fmt("market_cap", u.market_cap_max) + "</span>");
    if (u.min_price != null) h.push('<span class="chip u">close ≥ $' + esc(u.min_price) + "</span>");
    if (u.min_avg_dollar_volume != null) h.push('<span class="chip u">50d $ volume ≥ ' + fmt("avg_dollar_volume_50d", u.min_avg_dollar_volume) + "</span>");
    r.spec.conditions.forEach(function (c) {
      h.push('<span class="chip" title="' + esc(c.why || "") + '">' + esc(cond(c)) + "</span>");
    });
    h.push("</div><div class=\"meta\">Rank by: " + r.spec.rank.map(function (k) {
      return esc(k.field) + " (" + (k.direction === "desc" ? "higher better" : "lower better") + ", weight " + esc(k.weight) + ")";
    }).join("; ") + ". " + esc(r.spec.notes || "") + "</div>");
    if (r.spec.unmapped && r.spec.unmapped.length) {
      h.push('<div class="unmapped"><strong>Not screened — outside the schema</strong><ul>');
      r.spec.unmapped.forEach(function (x) { h.push("<li>“" + esc(x.text) + "”: " + esc(x.reason) + "</li>"); });
      h.push("</ul></div>");
    }
    h.push("<details><summary>Spec JSON</summary><pre>" + esc(JSON.stringify(r.spec, null, 2)) + "</pre></details></div>");
    // 3 funnel
    var n0 = r.funnel[0].n_in || 1;
    h.push('<div class="panel"><div class="step">3 · Funnel (computed by code)</div><div class="funnel">');
    r.funnel.forEach(function (s) {
      var p = 100 * s.n_pass / n0, m = 100 * s.n_missing / n0;
      h.push('<div class="frow"><div class="label">' + esc(s.step) + '</div><div class="bar"><span class="p" style="width:' + p +
        '%"></span><span class="m" style="width:' + m + '%"></span></div><div class="n">' + s.n_pass +
        (s.n_missing ? ' <span class="muted" title="dropped for missing data">(' + s.n_missing + " n/a)</span>" : "") + "</div></div>");
    });
    h.push('</div><div class="legend"><span><i class="sw" style="background:var(--bar)"></i>names passing</span>' +
      '<span><i class="sw" style="background:var(--bar-miss)"></i>dropped because the value is missing in free data</span></div></div>');
    // 4 table
    h.push('<div class="panel"><div class="step">4 · Ranked survivors — ' + r.n_ranked + " names" +
      (r.n_ranked > r.ranked.length ? ", top " + r.ranked.length + " shown" : "") + "</div>");
    if (!r.ranked.length) {
      h.push('<p class="muted">No company passed every condition.</p>');
    } else {
      h.push('<div class="tablewrap"><table><thead><tr>');
      r.columns.forEach(function (c) {
        var cls = (c === "symbol" || c === "name") ? ' class="l"' : "";
        h.push("<th" + cls + ' title="' + esc((FIELDS[c] || {}).desc || "") + '">' + esc(LABELS[c] || c) + "</th>");
      });
      h.push("</tr></thead><tbody>");
      r.ranked.forEach(function (row) {
        h.push('<tr class="' + (row.rank <= r.top_n ? "top" : "") + '">');
        r.columns.forEach(function (c) {
          var cls = c === "symbol" ? ' class="l"' : c === "name" ? ' class="l name"' : "";
          var v = c === "name" ? row[c] : fmt(c, row[c]);
          h.push("<td" + cls + (c === "name" ? ' title="' + esc(row[c]) + '"' : "") + ">" + esc(v) + "</td>");
        });
        h.push("</tr>");
      });
      h.push("</tbody></table></div>");
    }
    h.push("</div>");
    // 5 explanations
    h.push('<div class="panel"><div class="step">5 · Why the dislocation might exist — top ' + r.explanations.length +
      '</div><p class="muted" style="margin-top:0">Each quote was checked by code to appear verbatim in the linked SEC filing; claims that failed were removed and are listed under each card. No earnings-call transcripts were used (licensed content).</p><div class="cards">');
    r.explanations.forEach(function (ex) {
      var ok = ex.verdict === "explained";
      h.push('<div class="card"><div class="hd"><h3>' + esc(ex.symbol) + '</h3><span class="verdict ' + (ok ? "ok" : "thin") + '">' + esc(ex.verdict) + "</span></div>");
      h.push('<ul class="srcs">');
      ex.documents.forEach(function (d) { h.push('<li><a href="' + esc(d.url) + '" target="_blank" rel="noopener">' + esc(d.title) + "</a></li>"); });
      if (!ex.documents.length) h.push("<li>No earnings documents found.</li>");
      h.push("</ul>");
      [["thesis", "Thesis"], ["bear_case", "Bear case"]].forEach(function (part) {
        if (!ex[part[0]].length) return;
        h.push('<div class="sub">' + part[1] + "</div>");
        ex[part[0]].forEach(function (c) {
          h.push('<div class="claim">' + esc(c.claim) + "<q>“" + esc(c.quote) + '” <a class="cite" href="' + esc(c.url) +
            '" target="_blank" rel="noopener">' + esc(c.doc_id) + "</a></q></div>");
        });
      });
      if (ex.stripped.length) {
        h.push('<details class="stripped"><summary>' + ex.stripped.length + " claim(s) removed by the citation check</summary><ul>");
        ex.stripped.forEach(function (c) { h.push("<li>" + esc(c.claim) + " <em>(" + esc(c.reason) + ")</em></li>"); });
        h.push("</ul></details>");
      }
      h.push("</div>");
    });
    h.push("</div></div>");
    document.getElementById("run").innerHTML = h.join("");
  }

  var tabs = document.getElementById("tabs");
  var TITLES = { "a-midcap-pullback": "A · Mid-cap pullbacks still growing",
    "b-ai-infra-laggards": "B · AI-infrastructure laggards", "c-oversold-volume": "C · Oversold on heavy volume" };
  RUNS.forEach(function (r, i) {
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
  if (tabs.children[start]) tabs.children[start].click();
  if (!RUNS.length) document.getElementById("run").innerHTML = '<p class="muted">No recorded runs yet.</p>';
  var f = document.getElementById("foot");
  if (RUNS.length) {
    f.innerHTML = "Recorded runs use real data as of " + esc(RUNS[0].as_of) + ". Data limits: <ul>" +
      RUNS[0].limits.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") +
      "</ul>Research demo only: no orders, no recommendations. Every run, prompt and model response is in the repository.";
  }
})();
