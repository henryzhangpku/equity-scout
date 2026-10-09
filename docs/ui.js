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
      if (Math.abs(v) >= 1e12) return "$" + (v / 1e12).toFixed(2) + "T";
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
  var LABELS = { rank: "#", symbol: "Ticker", name: "Company", score: "Score", market_cap: "Market cap" };
  function label(f) { return LABELS[f] || (fields()[f] || {}).label || f; }
  var BSHORT = { spy: "S&P 500", qqq: "Nasdaq-100", iwm: "Russell 2000", smh: "chips (SMH)", soxx: "chips (SOXX)" };
  var HSHORT = { revenue_growth_yoy: "Revenue growth (YoY)", revenue_growth_q_yoy: "Qtr revenue growth (YoY)",
    revenue_growth_accel: "Growth acceleration", fcf_ttm: "Free cash flow (12m)", net_income_ttm: "Net income (12m)",
    revenue_ttm: "Revenue (12m)", avg_dollar_volume_50d: "Avg $ volume (50d)", volume_ratio_50d: "Volume vs 50d avg",
    short_pct_shares_out: "Short interest", sma50_above_sma200: "50d > 200d", drawdown_52w: "From 52w high" };
  function headLabel(f) {
    var m = /^rs_(\d+)m_vs_(\w+)$/.exec(f);
    if (m) return "vs " + (BSHORT[m[2]] || m[2].toUpperCase()) + ", " + m[1] + "m";
    return HSHORT[f] || label(f);
  }

  // ---------- plain English ----------
  function trim0(x) { return String(Number(x.toFixed(2))); }
  function money(v) {
    var a = Math.abs(v), sg = v < 0 ? "-" : "";
    if (a >= 1e12) return sg + "$" + trim0(a / 1e12) + "T";
    if (a >= 1e9) return sg + "$" + trim0(a / 1e9) + "B";
    if (a >= 1e6) return sg + "$" + trim0(a / 1e6) + "M";
    return sg + "$" + trim0(a);
  }
  function plainVal(f, v) {
    var k = kind(f);
    if (typeof v === "boolean") return v ? "yes" : "no";
    if (typeof v !== "number") return String(v);
    if (k === "ratio") return trim0(v * 100) + "%";
    if (k === "usd") return money(v);
    if (k === "days") return trim0(v) + " days";
    return trim0(v);
  }
  var OPW = { ">": "above", ">=": "at least", "<": "below", "<=": "at most" };
  function months(m) { return m === "1" ? "1 month" : m + " months"; }
  function benchName(b) { var bp = (window.SCOUT_SCHEMA || {}).bench_plain || window.SCOUT_BENCH || {}; return bp[b] || b.toUpperCase(); }
  var NICE = { ai_semis: "AI chips", ai_networking: "AI networking", ai_power: "AI power and cooling",
               data_center_reits: "data-center REITs", neoclouds: "GPU clouds" };
  function pretty(id) { return NICE[id] || String(id).replace(/_/g, " "); }

  function plainCond(c) {
    var f = c.field, v = c.value, op = c.op, m;
    if (c.ref) {
      var sm = /^sma(\d+)$/.exec(c.ref);
      if (f === "close" && sm) return "Price " + (op[0] === ">" ? "above" : "below") + " its " + sm[1] + "-day average";
      return label(f) + " " + (OPW[op] || op) + " " + label(c.ref).toLowerCase();
    }
    if (f === "sma50_above_sma200") return v ? "50-day average above 200-day average (uptrend)" : "50-day average below 200-day average (downtrend)";
    if (op === "between") return label(f) + " between " + plainVal(f, v[0]) + " and " + plainVal(f, v[1]);
    if (f === "drawdown_52w" && typeof v === "number") {
      if ((op === "<=" || op === "<") && v < 0) return "Down at least " + trim0(-v * 100) + "% from 52-week high";
      if ((op === ">=" || op === ">") && v < 0) return "Within " + trim0(-v * 100) + "% of 52-week high";
    }
    if ((m = /^pct_vs_sma(\d+)$/.exec(f)) && typeof v === "number") {
      if (v === 0) return "Price " + (op[0] === ">" ? "above" : "below") + " its " + m[1] + "-day average";
      if ((op[0] === "<") === (v < 0))
        return "Price at least " + trim0(Math.abs(v) * 100) + "% " + (v > 0 ? "above" : "below") + " its " + m[1] + "-day average";
    }
    if ((m = /^rs_(\d+)m_vs_(\w+)$/.exec(f)) && v === 0)
      return (op[0] === "<" ? "Lagging " : "Beating ") + benchName(m[2]) + " over " + months(m[1]);
    if ((m = /^mom_(\d+)m$/.exec(f)) && v === 0) return "Price " + (op[0] === ">" ? "up" : "down") + " over " + months(m[1]);
    if (f === "volume_ratio_50d" && op[0] === ">") return "Volume at least " + trim0(v) + "\u00d7 its 50-day average";
    var sym = { ">": ">", ">=": "\u2265", "<": "<", "<=": "\u2264" }[op] || op;
    return label(f) + " " + sym + " " + plainVal(f, v);
  }

  function plainSteps(spec) {
    var u = spec.universe || {}, out = ["All liquid US-listed companies"];
    if (u.industries || u.themes) {
      var parts = [];
      if (u.industries && u.industries.length) parts.push("Industry: " + u.industries.map(pretty).join(", "));
      if (u.themes && u.themes.length) parts.push((parts.length ? "theme: " : "Theme: ") + u.themes.map(pretty).join(", "));
      out.push(parts.join(" or "));
    }
    if (u.exclude_industries) out.push("Excluding " + u.exclude_industries.map(pretty).join(", "));
    if (u.market_cap_min != null) out.push("Market cap at least " + money(u.market_cap_min));
    if (u.market_cap_max != null) out.push("Market cap at most " + money(u.market_cap_max));
    if (u.min_price != null) out.push("Price at least " + money(u.min_price));
    if (u.min_avg_dollar_volume != null) out.push("Avg daily $ volume at least " + money(u.min_avg_dollar_volume));
    spec.conditions.forEach(function (c) { out.push(plainCond(c)); });
    return out;
  }

  function tableColumns(spec) {
    var cols = ["rank", "symbol", "name", "score", "market_cap"];
    spec.conditions.forEach(function (c) { cols.push(c.field); if (c.ref) cols.push(c.ref); });
    spec.rank.forEach(function (r) { cols.push(r.field); });
    return cols.filter(function (c, i) { return cols.indexOf(c) === i; });
  }

  function specHtml(spec, title) {
    var h = [];
    h.push('<div class="step">' + esc(title) + '</div><ul class="plainlist">');
    plainSteps(spec).slice(1).forEach(function (t) { h.push("<li>" + esc(t) + "</li>"); });
    h.push("</ul>");
    h.push('<div class="meta">Ranked by ' + spec.rank.map(function (k) {
      return esc(label(k.field)) + " (" + (k.direction === "desc" ? "higher is better" : "lower is better") +
        (spec.rank.length > 1 ? ", weight " + esc(k.weight) : "") + ")";
    }).join("; ") + ". " + esc(spec.notes || "") + "</div>");
    if (spec.unmapped && spec.unmapped.length) {
      h.push('<div class="unmapped"><strong>Not screened: free data cannot measure this</strong><ul>');
      spec.unmapped.forEach(function (x) { h.push("<li>\u201c" + esc(x.text) + "\u201d: " + esc(x.reason) + "</li>"); });
      h.push("</ul></div>");
    }
    h.push("<details><summary>Show spec (the exact JSON the screen ran)</summary><pre>" + esc(JSON.stringify(spec, null, 2)) + "</pre></details>");
    return h.join("");
  }

  function funnelHtml(funnel, title, spec) {
    var h = [], n0 = funnel[0].n_in || 1;
    var plain = spec ? plainSteps(spec) : null;
    if (plain && plain.length !== funnel.length) plain = null;
    h.push('<div class="step">' + esc(title || "How the list narrowed (computed by code)") + '</div><div class="funnel">');
    funnel.forEach(function (s, i) {
      var p = 100 * s.n_pass / n0, m = 100 * s.n_missing / n0;
      h.push('<div class="frow"><div class="label' + (plain ? " plain" : "") + '" title="' + esc(s.step) + '">' + esc(plain ? plain[i] : s.step) +
        '</div><div class="bar"><span class="p" style="width:' + p + '%"></span><span class="m" style="width:' + m + '%"></span></div>' +
        '<div class="n"><strong>' + s.n_pass.toLocaleString("en-US") + "</strong>" +
        (s.n_missing ? '<span class="miss" title="dropped because the value is missing in free data">' + s.n_missing.toLocaleString("en-US") + " no data</span>" : "") +
        "</div></div>");
    });
    h.push('</div><div class="legend"><span><i class="sw p"></i>companies still in</span>' +
      '<span><i class="sw m"></i>dropped because free data has no value for them</span></div>');
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
      h.push("<th" + cls + ' title="' + esc(label(c) + ": " + ((fields()[c] || {}).desc || c)) + '">' + esc(headLabel(c)) + "</th>");
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
    if (ex.model_status && !/^model said evidence/.test(ex.model_status)) h.push('<p class="stripped"><em>' + esc(ex.model_status) + "</em></p>");
    h.push("</div>");
    return h.join("");
  }

  window.ScoutUI = { esc: esc, fmt: fmt, cond: cond, label: label, plainCond: plainCond, plainSteps: plainSteps,
                     tableColumns: tableColumns, specHtml: specHtml,
                     funnelHtml: funnelHtml, tableHtml: tableHtml, cardHtml: cardHtml };
})();
