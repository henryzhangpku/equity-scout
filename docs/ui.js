/* Shared renderers for the static site, the "Try your own" panel and the local app (scout serve). */
(function () {
  "use strict";
  function fields() { return window.SCOUT_FIELDS || (window.SCOUT_SCHEMA || {}).fields || {}; }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function kind(f) { return (fields()[f] || {}).kind || ""; }
  function fmt(f, v) {
    if (v === null || v === undefined || v === "") return "n/a";
    if (typeof v === "boolean") return v ? "yes" : "no";
    if (typeof v === "string") return v;
    if (f === "score" || f.indexOf("rank_pct_") === 0) return v.toFixed(3);
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

  function tableColumns(spec) {
    var cols = ["rank", "symbol", "name", "score", "market_cap"];
    spec.conditions.forEach(function (c) { cols.push(c.field); if (c.ref) cols.push(c.ref); });
    spec.rank.forEach(function (r) { cols.push(r.field); });
    return cols.filter(function (c, i) { return cols.indexOf(c) === i; });
  }

  function specHtml(spec, title) {
    var h = [], u = spec.universe || {};
    h.push('<div class="step">' + esc(title) + '</div><div class="chips">');
    if (u.industries) h.push('<span class="chip u">industry ∈ ' + esc(u.industries.join(", ")) + "</span>");
    if (u.themes) h.push('<span class="chip u" title="curated, code-defined baskets">theme basket ∈ ' + esc(u.themes.join(", ")) + "</span>");
    if (u.exclude_industries) h.push('<span class="chip u">industry ∉ ' + esc(u.exclude_industries.join(", ")) + "</span>");
    if (u.market_cap_min != null) h.push('<span class="chip u">market_cap ≥ ' + fmt("market_cap", u.market_cap_min) + "</span>");
    if (u.market_cap_max != null) h.push('<span class="chip u">market_cap ≤ ' + fmt("market_cap", u.market_cap_max) + "</span>");
    if (u.min_price != null) h.push('<span class="chip u">close ≥ $' + esc(u.min_price) + "</span>");
    if (u.min_avg_dollar_volume != null) h.push('<span class="chip u">50d $ volume ≥ ' + fmt("avg_dollar_volume_50d", u.min_avg_dollar_volume) + "</span>");
    spec.conditions.forEach(function (c) { h.push('<span class="chip" title="' + esc(c.why || "") + '">' + esc(cond(c)) + "</span>"); });
    h.push('</div><div class="meta">Rank by: ' + spec.rank.map(function (k) {
      return esc(k.field) + " (" + (k.direction === "desc" ? "higher better" : "lower better") + ", weight " + esc(k.weight) + ")";
    }).join("; ") + ". " + esc(spec.notes || "") + "</div>");
    if (spec.unmapped && spec.unmapped.length) {
      h.push('<div class="unmapped"><strong>Not screened — outside the schema</strong><ul>');
      spec.unmapped.forEach(function (x) { h.push("<li>“" + esc(x.text) + "”: " + esc(x.reason) + "</li>"); });
      h.push("</ul></div>");
    }
    h.push("<details><summary>Spec JSON</summary><pre>" + esc(JSON.stringify(spec, null, 2)) + "</pre></details>");
    return h.join("");
  }

  function funnelHtml(funnel, title) {
    var h = [], n0 = funnel[0].n_in || 1;
    h.push('<div class="step">' + esc(title || "Funnel (computed by code)") + '</div><div class="funnel">');
    funnel.forEach(function (s) {
      var p = 100 * s.n_pass / n0, m = 100 * s.n_missing / n0;
      h.push('<div class="frow"><div class="label">' + esc(s.step) + '</div><div class="bar"><span class="p" style="width:' + p +
        '%"></span><span class="m" style="width:' + m + '%"></span></div><div class="n">' + s.n_pass +
        (s.n_missing ? ' <span class="muted" title="dropped for missing data">(' + s.n_missing + " n/a)</span>" : "") + "</div></div>");
    });
    h.push('</div><div class="legend"><span><i class="sw" style="background:var(--bar)"></i>names passing</span>' +
      '<span><i class="sw" style="background:var(--bar-miss)"></i>dropped because the value is missing in free data</span></div>');
    return h.join("");
  }

  function tableHtml(columns, rows, topN, nRanked, title) {
    var h = [];
    h.push('<div class="step">' + esc(title || "Ranked survivors") + " — " + nRanked + " names" +
      (nRanked > rows.length ? ", top " + rows.length + " shown" : "") + "</div>");
    if (!rows.length) return h.join("") + '<p class="muted">No company passed every condition.</p>';
    h.push('<div class="tablewrap"><table><thead><tr>');
    columns.forEach(function (c) {
      var cls = (c === "symbol" || c === "name") ? ' class="l"' : "";
      h.push("<th" + cls + ' title="' + esc((fields()[c] || {}).desc || "") + '">' + esc(LABELS[c] || c) + "</th>");
    });
    h.push("</tr></thead><tbody>");
    rows.forEach(function (row) {
      h.push('<tr class="' + (row.rank <= topN ? "top" : "") + '">');
      columns.forEach(function (c) {
        var cls = c === "symbol" ? ' class="l"' : c === "name" ? ' class="l name"' : "";
        var v = c === "name" ? row[c] : fmt(c, row[c]);
        h.push("<td" + cls + (c === "name" ? ' title="' + esc(row[c]) + '"' : "") + ">" + esc(v) + "</td>");
      });
      h.push("</tr>");
    });
    h.push("</tbody></table></div>");
    return h.join("");
  }

  function cardHtml(ex, note) {
    var h = [], ok = ex.verdict === "explained";
    h.push('<div class="card"><div class="hd"><h3>' + esc(ex.symbol) + '</h3><span class="verdict ' + (ok ? "ok" : "thin") + '">' + esc(ex.verdict) + "</span></div>");
    if (note) h.push('<p class="meta" style="margin:2px 0 0">' + note + "</p>");
    h.push('<ul class="srcs">');
    var link = function (d) { return '<li><a href="' + esc(d.url) + '" target="_blank" rel="noopener">' + esc(d.title) + "</a></li>"; };
    var docs = ex.documents || [];
    docs.filter(function (d) { return d.kind !== "news"; }).forEach(function (d) { h.push(link(d)); });
    var news = docs.filter(function (d) { return d.kind === "news"; });
    if (news.length) h.push("<li><details><summary>" + news.length + " news headlines and summaries given to the model (not full articles)</summary><ul>" +
      news.map(link).join("") + "</ul></details></li>");
    if (!docs.length) h.push("<li>No earnings documents found.</li>");
    h.push("</ul>");
    [["thesis", "Thesis"], ["bear_case", "Bear case"]].forEach(function (part) {
      if (!(ex[part[0]] || []).length) return;
      h.push('<div class="sub">' + part[1] + "</div>");
      ex[part[0]].forEach(function (c) {
        var tag = c.source_kind === "news" ? '<span class="tag news">news headline/summary</span> ' :
          '<span class="tag filing">' + (c.source_kind === "mdna" ? "10-Q/10-K MD&amp;A" : "8-K earnings release") + "</span> ";
        h.push('<div class="claim">' + tag + esc(c.claim) + "<q>“" + esc(c.quote) + '” <a class="cite" href="' + esc(c.url) +
          '" target="_blank" rel="noopener">' + esc(c.doc_id) + "</a></q></div>");
      });
    });
    if ((ex.stripped || []).length) {
      h.push('<details class="stripped"><summary>' + ex.stripped.length + " claim(s) removed by the citation check</summary><ul>");
      ex.stripped.forEach(function (c) { h.push("<li>" + esc(c.claim) + " <em>(" + esc(c.reason) + ")</em></li>"); });
      h.push("</ul></details>");
    }
    if (ex.model_status) h.push('<p class="stripped"><em>' + esc(ex.model_status) + "</em></p>");
    h.push("</div>");
    return h.join("");
  }

  window.ScoutUI = { esc: esc, fmt: fmt, cond: cond, tableColumns: tableColumns, specHtml: specHtml,
                     funnelHtml: funnelHtml, tableHtml: tableHtml, cardHtml: cardHtml };
})();
