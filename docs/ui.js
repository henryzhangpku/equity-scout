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
  var LABELS = { rank: "#", symbol: "Ticker", name: "Company", score: "Score", market_cap: "Market cap", sector: "Sector",
                 industry_group: "Industry group" };
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
    if ((u.sectors && u.sectors.length) || (u.industry_groups && u.industry_groups.length)) {
      var sp = [];
      if (u.sectors && u.sectors.length) sp.push("Sector: " + u.sectors.join(", "));
      if (u.industry_groups && u.industry_groups.length) sp.push((sp.length ? "industry: " : "Industry: ") + u.industry_groups.join(", "));
      out.push(sp.join(" or "));
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
    var cols = ["rank", "symbol", "name", "sector", "score", "market_cap"];
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
      var cls = (c === "symbol" || c === "name" || c === "sector") ? ' class="l"' : "";
      h.push("<th" + cls + ' title="' + esc(label(c) + ": " + ((fields()[c] || {}).desc || c)) + '">' + esc(headLabel(c)) + "</th>");
    });
    h.push("</tr></thead><tbody>");
    rows.forEach(function (row) {
      h.push('<tr class="' + (row.rank <= topN ? "top" : "") + '">');
      columns.forEach(function (c) {
        var cls = c === "symbol" ? ' class="l"' : c === "name" ? ' class="l name"' : c === "sector" ? ' class="l sec"' : "";
        var v = c === "name" ? row[c] : fmt(c, row[c]);
        h.push("<td" + cls + (c === "name" ? ' title="' + esc(row[c]) + '"' : "") + ">" + esc(v) + "</td>");
      });
      h.push("</tr>");
    });
    h.push("</tbody></table></div>");
    return h.join("");
  }

  function sectorHtml(breakdown, title) {
    if (!breakdown || !breakdown.length) return "";
    var max = breakdown[0].n || 1, total = breakdown.reduce(function (a, b) { return a + b.n; }, 0);
    var h = ['<div class="step">' + esc(title || "Survivors by sector") + '</div><div class="secs">'];
    breakdown.forEach(function (b) {
      h.push('<div class="secrow"><span class="secname">' + esc(b.sector) + '</span><span class="bar"><span class="p" style="width:' +
        (100 * b.n / max) + '%"></span></span><span class="secn">' + b.n + ' <span class="muted">(' + Math.round(100 * b.n / total) + "%)</span></span></div>");
    });
    h.push('</div><p class="meta">Sectors are mapped from each company\u2019s SEC SIC code (<a href="sectors.html">mapping table</a>), not a licensed classification.</p>');
    return h.join("");
  }

  // ---------- backtest ----------
  function pct(v, d) { return v === null || v === undefined || !isFinite(v) ? "n/a" : (v >= 0 ? "+" : "") + (v * 100).toFixed(d === undefined ? 1 : d) + "%"; }
  function chartSvg(curve) {
    var W = 760, H = 260, L = 48, R = 12, T = 14, Bm = 28;
    var keys = [["universe", "u"], ["spy", "s"], ["strategy", "x"]];
    var ys = [1];
    curve.forEach(function (c) { keys.forEach(function (k) { ys.push(c[k[0]]); }); });
    var lo = Math.min.apply(null, ys), hi = Math.max.apply(null, ys);
    var pad = (hi - lo) * 0.08 || 0.05; lo -= pad; hi += pad;
    var n = curve.length;
    function X(i) { return L + (W - L - R) * (i / n); }
    function Y(v) { return T + (H - T - Bm) * (1 - (v - lo) / (hi - lo)); }
    var h = ['<svg class="btchart" viewBox="0 0 ' + W + " " + H + '" role="img" aria-label="Growth of $1: screen vs benchmarks">'];
    var steps = [0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10, 25], step = steps[steps.length - 1];
    for (var si = 0; si < steps.length; si++) { if ((hi - lo) / steps[si] <= 6) { step = steps[si]; break; } }
    for (var g = Math.ceil(lo / step) * step; g <= hi; g += step) {
      h.push('<line x1="' + L + '" x2="' + (W - R) + '" y1="' + Y(g) + '" y2="' + Y(g) + '" class="grid"/>' +
        '<text x="' + (L - 6) + '" y="' + (Y(g) + 4) + '" class="ax" text-anchor="end">$' + g.toFixed(2) + "</text>");
    }
    h.push('<line x1="' + L + '" x2="' + (W - R) + '" y1="' + Y(1) + '" y2="' + Y(1) + '" class="base"/>');
    keys.forEach(function (k) {
      var pts = [X(0) + "," + Y(1)].concat(curve.map(function (c, i) { return X(i + 1) + "," + Y(c[k[0]]); }));
      h.push('<polyline class="ln ' + k[1] + '" points="' + pts.join(" ") + '"/>');
    });
    var first = curve.length ? curve[0].date : "", last = curve.length ? curve[curve.length - 1].date : "";
    h.push('<text x="' + L + '" y="' + (H - 8) + '" class="ax">' + esc(first.slice(0, 7)) + '</text><text x="' + (W - R) + '" y="' + (H - 8) +
      '" class="ax" text-anchor="end">' + esc(last.slice(0, 7)) + "</text></svg>");
    return h.join("");
  }
  function backtestHtml(r) {
    var h = [], st = r.stats, P = r.params;
    var cls = r.verdict === "Edge on this history" ? "ok" : r.verdict === "No edge" ? "bad" : "thin";
    h.push('<div class="btverdict ' + cls + '"><div class="step" style="margin:0 0 4px">Backtest verdict</div><div class="vtext">' + esc(r.verdict) +
      '</div><p class="meta" style="margin:6px 0 0">Monthly rebalance, top ' + P.top_n + " names equal weight, " + P.cost_bps_per_side +
      " bps cost per side, " + esc(P.first) + " to " + esc(P.last) + " (" + P.n_months + " months). This is evidence on a short history, not proof.</p>" +
      r.caveats.filter(function (c) { return c.indexOf("Look-ahead") === 0; }).map(function (c) { return '<p class="err" style="margin:8px 0 0;font-size:14px">' + esc(c) + "</p>"; }).join("") + "</div>");
    h.push('<div class="btgrid"><div><div class="step">Growth of $1</div>' + chartSvg(r.curve) +
      '<div class="legend"><span><i class="sw x"></i>This screen (after costs)</span><span><i class="sw u"></i>Equal-weight universe (no conditions)</span><span><i class="sw s"></i>SPY</span></div></div>');
    h.push('<div><div class="step">Gates (all must pass)</div><ul class="gates">');
    r.gates.forEach(function (g) {
      var val = g.id === "floor" ? g.value + " months" : pct(g.value, 2) + " / month";
      h.push('<li class="' + (g.pass ? "pass" : "fail") + '"><span class="gmark">' + (g.pass ? "\u2713" : "\u2715") + "</span><span>" + esc(g.label) +
        ' <span class="muted">(' + esc(val) + ")</span></span></li>");
    });
    h.push("</ul></div></div>");
    var rows = [["This screen", st.strategy], ["Equal-weight universe", st.universe], ["SPY", st.spy]];
    h.push('<div class="tablewrap" style="margin-top:16px"><table><thead><tr><th class="l">Series</th><th>Total</th><th>CAGR</th><th>Volatility</th><th>Sharpe</th><th>Max drawdown</th></tr></thead><tbody>');
    rows.forEach(function (x) {
      var s = x[1];
      h.push('<tr><td class="l">' + x[0] + "</td><td>" + pct(s.total) + "</td><td>" + pct(s.cagr) + "</td><td>" + pct(s.vol) + "</td><td>" +
        (s.sharpe === null ? "n/a" : s.sharpe.toFixed(2)) + "</td><td>" + pct(s.max_drawdown) + "</td></tr>");
    });
    h.push("</tbody></table></div>");
    h.push('<p class="meta">Beat SPY in ' + pct(st.hit_rate_vs_spy, 0).replace("+", "") + " of months held \u00b7 average " + st.avg_names.toFixed(1) +
      " names \u00b7 average turnover " + pct(st.avg_turnover, 0).replace("+", "") + " per rebalance \u00b7 " + st.months_too_few +
      " months with fewer than " + P.min_names + " names (held cash) \u00b7 " + st.names_stopped + " exits at a last close (name stopped trading)</p>");
    h.push('<details><summary>Caveats</summary><ul class="caveats">' + r.caveats.map(function (c) { return "<li>" + esc(c) + "</li>"; }).join("") + "</ul></details>");
    h.push('<details><summary>Month by month: names held and returns</summary><div class="tablewrap"><table><thead><tr><th class="l">From</th><th>Names</th><th>Screen (net)</th><th>SPY</th><th class="l">Held</th></tr></thead><tbody>');
    r.months.forEach(function (m) {
      h.push('<tr><td class="l">' + esc(m.date) + "</td><td>" + m.n + "</td><td>" + pct(m.net) + "</td><td>" + pct(m.spy) + '</td><td class="l held">' +
        esc(m.held.join(", ")) + "</td></tr>");
    });
    h.push("</tbody></table></div></details>");
    return h.join("");
  }

  // Backtest button + result. opts: {key: precomputed id or null, spec, api: base URL ("" = same origin) or null,
  // live: function () -> bool, precomputedSrc: script URL holding window.SCOUT_BACKTESTS}
  function mountBacktest(el, opts) {
    el.innerHTML = '<div class="btbar"><button class="primary" type="button">Backtest this screen</button>' +
      '<span class="meta" style="margin:0">Did this kind of idea work historically? Monthly, point-in-time, pure code.</span></div><div class="btout"></div>';
    var btn = el.querySelector("button"), out = el.querySelector(".btout");
    function show(r) { out.innerHTML = '<div style="margin-top:18px">' + backtestHtml(r) + "</div>"; }
    function fromApi() {
      if (opts.api === null || opts.api === undefined || !(opts.live ? opts.live() : true)) {
        out.innerHTML = '<p class="meta">Backtests for new screens run on the live service, which is offline right now. The examples and recorded runs have saved backtests.</p>';
        return;
      }
      var t0 = Date.now(), tick = setInterval(function () {
        out.innerHTML = '<p class="meta"><span class="spinner"></span>Running the screen on every month-end since 2023\u2026 ' + Math.round((Date.now() - t0) / 1000) + " s</p>"; }, 400);
      var ctrl = new AbortController(), to = setTimeout(function () { ctrl.abort(); }, 120000);
      btn.disabled = true;
      fetch(opts.api + "/api/backtest", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ spec: opts.spec }), signal: ctrl.signal })
        .then(function (r) { return r.json(); })
        .then(function (r) {
          if (r.ok) show(r);
          else out.innerHTML = '<p class="err">' + esc(r.refused ? "Refused: " + r.problems.join("; ") : (r.error || "The backtest failed.")) + "</p>";
        })
        .catch(function (e) { out.innerHTML = '<p class="err">' + (e.name === "AbortError" ? "The backtest took too long." : "The live service is unreachable.") + "</p>"; })
        .then(function () { clearInterval(tick); clearTimeout(to); btn.disabled = false; });
    }
    btn.onclick = function () {
      var table = window.SCOUT_BACKTESTS;
      if (opts.key && table && table[opts.key]) return show(table[opts.key]);
      if (opts.key && !table && opts.precomputedSrc) {
        out.innerHTML = '<p class="meta"><span class="spinner"></span>Loading the saved backtest\u2026</p>';
        var sc = document.createElement("script");
        sc.src = opts.precomputedSrc;
        sc.onload = function () { var t = window.SCOUT_BACKTESTS || {}; if (t[opts.key]) show(t[opts.key]); else fromApi(); };
        sc.onerror = fromApi;
        document.head.appendChild(sc);
        return;
      }
      fromApi();
    };
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
                     tableColumns: tableColumns, specHtml: specHtml, sectorHtml: sectorHtml, backtestHtml: backtestHtml,
                     mountBacktest: mountBacktest,
                     funnelHtml: funnelHtml, tableHtml: tableHtml, cardHtml: cardHtml };
})();
