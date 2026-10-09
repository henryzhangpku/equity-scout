/* "Try it": ask the hosted API in plain English, click an example, or (Advanced) build a spec.
 *
 * Examples and Advanced run entirely in the page on the shipped snapshot, which loads only when first needed.
 * The hosted API base URL comes from config.js; keys live only on the server.
 */
(function () {
  "use strict";
  var U = window.ScoutUI, esc = U.esc;
  var SNAP_FILE = "data/snapshot-2026-10-08.js";
  var API = (window.SCOUT_API_BASE || "").replace(/\/+$/, "");
  var S = null, SNAP = null, loading = null, apiLive = false, health = null;
  var root = document.getElementById("try-body");
  var adv = document.getElementById("advanced");
  var CHIPS = window.SCOUT_CHIPS || [];
  function byId(id) { return document.getElementById(id); }

  function loadScript(src) {
    return new Promise(function (ok, fail) {
      var s = document.createElement("script");
      s.src = src; s.async = true;
      s.onload = ok; s.onerror = function () { fail(new Error("could not load " + src)); };
      document.head.appendChild(s);
    });
  }

  function ensureLoaded() {
    if (loading) return loading;
    showOut('<div class="panel"><p class="muted" style="margin:0">Loading the 2026-10-08 snapshot of about 3,800 companies (about 2 MB)…</p></div>');
    loading = loadScript("data/schema.js?v=20261009b").then(function () {
      S = window.SCOUT_SCHEMA; ScoutCore.setSchema(S);
      return Promise.all([loadScript(SNAP_FILE), loadScript("data/chips-ex.js?v=20261009b")]);
    }).then(function () { SNAP = window.SCOUT_SNAPSHOT; buildAdvanced(); showOut(""); })
      .catch(function (e) { showOut('<div class="panel refusal"><p class="err" style="margin:0">' + esc(e.message) + "</p></div>"); loading = null; throw e; });
    return loading;
  }

  function showOut(html) { byId("t-out").innerHTML = html; }

  // ---------- hosted API: status pill + ask box ----------
  function pill(live, text) {
    var p = byId("api-status");
    p.className = "status-pill" + (live ? " live" : "");
    p.lastElementChild.textContent = text;
  }
  function apiFetch(path, opts, ms) {
    var ctrl = new AbortController(), t = setTimeout(function () { ctrl.abort(); }, ms || 15000);
    opts = opts || {};
    opts.signal = ctrl.signal;
    if (opts.body) opts.headers = { "Content-Type": "application/json" };
    return fetch(API + path, opts).then(function (r) {
      return r.json().catch(function () { return { ok: false, error: "Unexpected response from the live service." }; })
        .then(function (j) { j._status = r.status; return j; });
    }).finally(function () { clearTimeout(t); });
  }
  function renderAsk() {
    var box = byId("ask");
    box.innerHTML =
      '<label for="ask-text" class="step" style="display:block;margin:14px 0 8px">Describe what you are looking for</label>' +
      '<textarea id="ask-text" class="prose" rows="2" maxlength="500" placeholder="e.g. Cash-rich small caps trading near their lows, with growing revenue"></textarea>' +
      '<div class="row"><button id="ask-go" class="primary">Analyze</button><span id="ask-msg" class="meta" style="margin:0"></span></div>';
    byId("ask-go").onclick = ask;
    byId("ask-text").addEventListener("keydown", function (e) { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) ask(); });
  }
  function askMsg(html) { byId("ask-msg").innerHTML = html; }
  function offlineNote() {
    return "Live analysis is offline right now. Pick an example above, or open <em>Advanced</em> to build a screen yourself.";
  }
  function checkApi() {
    if (!API) { pill(false, "Snapshot (offline)"); askMsg(offlineNote()); return; }
    apiFetch("/api/health", null, 5000).then(function (h) {
      health = h;
      apiLive = !!(h && h.ok && h.live);
      pill(apiLive, apiLive ? "Live" : "Snapshot (offline)");
      if (!apiLive) askMsg(h && h.killed ? "Live analysis is paused. Pick an example above." : offlineNote());
      else askMsg("Live: the model proposes a screen, code runs it on the " + esc(h.last_price_date) + " snapshot, then reads the top " +
        esc(h.max_explain) + " names’ filings (about a minute per name).");
    }).catch(function () { apiLive = false; pill(false, "Snapshot (offline)"); askMsg(offlineNote()); });
  }

  function ask() {
    var obs = byId("ask-text").value.trim();
    if (!obs) { askMsg("Write what you are looking for first."); return; }
    if (!apiLive) { askMsg(offlineNote()); return; }
    var btn = byId("ask-go"); btn.disabled = true;
    var t0 = Date.now(), tick = setInterval(function () { askMsg('<span class="spinner"></span>Turning your words into a screen… ' + Math.round((Date.now() - t0) / 1000) + " s"); }, 500);
    apiFetch("/api/translate", { method: "POST", body: JSON.stringify({ observation: obs }) }, 180000).then(function (r) {
      if (r.ok) { askMsg(""); confirmLive(r.spec); return; }
      if (r.refused) { askMsg('<span class="err">The proposed screen did not pass the checks:</span> ' + esc(r.problems.join("; "))); return; }
      askMsg('<span class="err">' + esc(r.error || "The live service could not answer.") + "</span>");
      if (r.limited) pill(false, "Snapshot (limit reached)");
    }).catch(function (e) {
      askMsg('<span class="err">' + (e.name === "AbortError" ? "That took too long." : "The live service is unreachable.") + "</span> Pick an example above instead.");
    }).then(function () { clearInterval(tick); btn.disabled = false; });
  }

  function confirmLive(spec) {
    showOut('<div class="panel">' + U.specHtml(spec, "The screen the model proposed (checked by code)") +
      '<div class="row"><button id="live-run" class="primary">Run this screen</button>' +
      '<button id="live-edit" class="ghost">Adjust it under Advanced</button></div></div>');
    byId("live-run").onclick = function () { runLive(spec); };
    byId("live-edit").onclick = function () {
      adv.open = true;
      ensureLoaded().then(function () { setSpec(JSON.parse(JSON.stringify(spec))); byId("t-form").scrollIntoView({ behavior: "smooth" }); });
    };
    byId("t-out").scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function runLive(spec) {
    var btn = byId("live-run"); if (btn) btn.disabled = true;
    apiFetch("/api/run", { method: "POST", body: JSON.stringify({ spec: spec }) }, 90000).then(function (r) {
      if (!r.ok) {
        var msg = r.refused ? "Refused: " + r.problems.join("; ") : (r.error || "The live service could not run this.");
        showOut('<div class="panel refusal"><p class="err" style="margin:0">' + esc(msg) + "</p></div>");
        return;
      }
      var cols = U.tableColumns(spec);
      renderResults({ spec: spec, funnel: r.funnel, rows: r.ranked, nRanked: r.n_ranked, topN: r.top_n, breakdown: r.sector_breakdown,
        note: "<strong>Live run</strong> on the snapshot as of " + esc(r.last_price_date) + " close. Explanations read today’s SEC filings and news; they appear as each name finishes.",
        cols: cols, pending: r.ranked.slice(0, r.top_n).map(function (x) { return x.symbol; }) });
      poll(r.job);
    }).catch(function () { showOut('<div class="panel refusal"><p class="err" style="margin:0">The live service is unreachable. Try an example above.</p></div>'); });
  }

  function poll(job) {
    apiFetch("/api/run/" + job, null, 20000).then(function (p) {
      if (!p.ok) { setCardsNote('<span class="err">' + esc(p.error || "Lost track of this analysis.") + "</span>"); return; }
      p.explanations.forEach(function (ex) {
        var c = byId("card-" + ex.symbol);
        if (c && c.classList.contains("pending")) c.outerHTML = U.cardHtml(ex);
      });
      if (p.working_on) { var w = byId("card-" + p.working_on); if (w) w.querySelector(".verdict").textContent = "reading filings…"; }
      if (p.error) { setCardsNote('<span class="err">' + esc(p.error.message) + "</span>"); return; }
      if (!p.done) setTimeout(function () { poll(job); }, 2500);
      else setCardsNote("Done in " + Math.round(p.elapsed) + " s.");
    }).catch(function () { setTimeout(function () { poll(job); }, 5000); });
  }
  function setCardsNote(html) { var n = byId("cards-note"); if (n) n.innerHTML = html; }

  // ---------- shared results renderer ----------
  function renderResults(o) {
    var h = [];
    h.push('<div class="panel"><p class="label-note">' + o.note + "</p>" + U.specHtml(o.spec, "What was screened") + "</div>");
    h.push('<div class="panel">' + U.funnelHtml(o.funnel, "How the list narrowed", o.spec) + "</div>");
    h.push('<div class="panel">' + U.tableHtml(o.cols, o.rows, o.topN, o.nRanked, "Ranked results") + "</div>");
    if (o.breakdown && o.breakdown.length) h.push('<div class="panel">' + U.sectorHtml(o.breakdown, "Survivors by sector (all " + o.nRanked + ")") + "</div>");
    var top = o.rows.slice(0, o.topN);
    if (top.length) {
      h.push('<div class="panel"><div class="step">Why the price and the business may disagree — top ' + top.length + "</div>");
      h.push('<p class="muted" style="margin-top:0">' + (o.exNote || "Each quote was checked by code to appear word for word in its linked source.") +
        ' <span id="cards-note"></span></p><div class="cards">');
      top.forEach(function (r) {
        var ex = o.explanations && o.explanations[r.symbol];
        if (ex) h.push(U.cardHtml(ex));
        else if (o.pending && o.pending.indexOf(r.symbol) >= 0)
          h.push('<div class="card pending" id="card-' + esc(r.symbol) + '"><div class="hd"><h3>' + esc(r.symbol) + '</h3><span class="verdict thin">waiting</span></div><p class="meta">' + esc(r.name || "") + "</p></div>");
        else h.push('<div class="card"><div class="hd"><h3>' + esc(r.symbol) + '</h3><span class="verdict thin">no explanation yet</span></div><p class="meta">' +
          esc(r.name || "") + ". " + (o.missingNote || "") + "</p></div>");
      });
      h.push("</div></div>");
    }
    h.push('<div class="panel" id="bt-panel"></div>');
    showOut(h.join(""));
    U.mountBacktest(byId("bt-panel"), { key: o.btKey || null, spec: o.spec, api: API || null,
      live: function () { return apiLive; }, precomputedSrc: "data/backtests.js?v=20261009b" });
  }

  // ---------- examples ----------
  function renderChips() {
    var box = byId("chips");
    if (!CHIPS.length) { box.innerHTML = '<span class="muted">No examples bundled.</span>'; return; }
    box.innerHTML = CHIPS.map(function (c) { return '<button class="chipbtn" data-chip="' + esc(c.id) + '">' + esc(c.label) + "</button>"; }).join("");
    box.querySelectorAll("[data-chip]").forEach(function (b) {
      b.onclick = function () {
        box.querySelectorAll(".chipbtn").forEach(function (x) { x.classList.remove("on"); });
        b.classList.add("on");
        runChip(b.getAttribute("data-chip"));
      };
    });
    byId("chip-note").innerHTML = "Each example was translated by the model once, checked by code, and its top names explained from live SEC filings and news on " +
      esc(CHIPS[0].generated) + " (UTC). The screen itself re-runs here, in your browser.";
  }
  function runChip(id) {
    var c = CHIPS.filter(function (x) { return x.id === id; })[0];
    ensureLoaded().then(function () {
      setSpec(JSON.parse(JSON.stringify(c.spec)));
      var v = ScoutCore.validate(c.spec, S.short_interest_available);
      if (!v.ok) { showOut('<div class="panel refusal">' + esc(v.problems.join("; ")) + "</div>"); return; }
      var res = screen(v.spec);
      var exs = {};
      ((window.SCOUT_CHIP_EX || {})[id] || []).forEach(function (ex) { exs[ex.symbol] = ex; });
      renderResults({ spec: v.spec, funnel: res.funnel, rows: res.rows, nRanked: res.n, topN: v.spec.top_n, cols: res.cols,
        breakdown: res.breakdown, btKey: c.id,
        note: "<strong>Example:</strong> “" + esc(c.observation) + "”<br>Snapshot as of " + esc(S.data.last_price_date) +
          " close, screened in your browser. Explanations were generated on " + esc(c.generated) + " (UTC) from live SEC filings and news.",
        explanations: exs });
      byId("t-out").scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }
  function screen(spec) {
    ScoutCore.ensureSectors(SNAP);
    var res = ScoutCore.runScreen(SNAP, spec);
    var ranked = ScoutCore.rank(SNAP, res.survivors, spec);
    var cols = U.tableColumns(spec), C = SNAP.columns;
    var rows = ranked.slice(0, 25).map(function (r) {
      var o = { rank: r.rank, score: r.score };
      cols.forEach(function (c) { if (c !== "rank" && c !== "score") o[c] = C[c] ? C[c][r._i] : null; });
      return o;
    });
    return { funnel: res.funnel, rows: rows, n: ranked.length, cols: cols, breakdown: ScoutCore.sectorBreakdown(SNAP, res.survivors) };
  }

  // cached explanations from the recorded runs, by symbol (shown for Advanced runs)
  var cached = {};
  (window.SCOUT_RUNS || []).forEach(function (r) {
    r.explanations.forEach(function (ex) { cached[ex.symbol] = { ex: ex, run: r.id, as_of: r.as_of }; });
  });

  // ---------- Advanced: spec editor + bring-your-own-key ----------
  var spec = null;
  function blankSpec() {
    return { version: 1, observation: "My observation", universe: { market_cap_min: 2e9 },
             conditions: [{ field: "drawdown_52w", op: "<=", value: -0.2 }],
             rank: [{ field: "drawdown_52w", direction: "asc", weight: 1 }], top_n: 5, unmapped: [], notes: "" };
  }
  function clone(x) { return JSON.parse(JSON.stringify(x)); }
  function status(html) { byId("t-status").innerHTML = html; }

  function buildAdvanced() {
    var runs = window.SCOUT_RUNS || [];
    var opts = runs.map(function (r) { return '<option value="run:' + esc(r.id) + '">Recorded run: ' + esc(r.observation.slice(0, 60)) + "…</option>"; }).join("") +
      CHIPS.map(function (c) { return '<option value="chip:' + esc(c.id) + '">Example: ' + esc(c.label) + "</option>"; }).join("");
    root.innerHTML =
      '<p class="label-note">Data as of the ' + esc(S.data.last_price_date) + ' close, ' + esc(S.data.n_companies) + ' companies. The screen runs in your browser.</p>' +
      '<div class="subpanel"><h3>Build the screen (allowed fields only)</h3><div id="t-status" class="meta"></div>' +
      '<div class="row"><select id="t-template"><option value="">Start from…</option>' + opts + '<option value="__blank">Blank example</option></select></div>' +
      '<div id="t-form"></div>' +
      '<details><summary>Edit as JSON</summary><textarea id="t-json" rows="14" spellcheck="false"></textarea>' +
      '<div class="row"><button id="t-apply" class="ghost">Load JSON into the form</button></div></details>' +
      '<div class="row"><button id="t-run" class="primary">Check and run</button></div></div>';
    byId("t-template").onchange = function () {
      var v = this.value; if (!v) return;
      if (v === "__blank") return setSpec(blankSpec());
      var parts = v.split(":"), src = parts[0] === "run" ? runs.filter(function (x) { return x.id === parts[1]; })[0]
        : CHIPS.filter(function (x) { return x.id === parts[1]; })[0];
      setSpec(clone(src.spec));
    };
    byId("t-apply").onclick = function () {
      try { setSpec(JSON.parse(byId("t-json").value)); status(""); }
      catch (e) { showOut('<div class="panel refusal"><strong>Not valid JSON:</strong> ' + esc(e.message) + "</div>"); }
    };
    byId("t-run").onclick = runAdvanced;
    setSpec(CHIPS.length ? clone(CHIPS[0].spec) : runs.length ? clone(runs[0].spec) : blankSpec());
  }

  function setSpec(s) { spec = s; renderForm(); syncJson(); }
  function syncJson() { byId("t-json").value = JSON.stringify(spec, null, 2); }

  var GROUPS = { size: "Size and liquidity", technical: "Price, trend and volume", fundamental: "Fundamentals", short_interest: "Short interest" };
  function fieldOptions(sel, allowBool) {
    var groups = {};
    Object.keys(S.fields).forEach(function (k) {
      var f = S.fields[k];
      if (!allowBool && f.kind === "bool") return;
      (groups[f.group] = groups[f.group] || []).push(k);
    });
    var h = "";
    if (sel && !S.fields[sel]) h += '<option value="' + esc(sel) + '" selected>' + esc(sel) + " (not in whitelist)</option>";
    Object.keys(groups).forEach(function (g) {
      h += '<optgroup label="' + esc(GROUPS[g] || g) + '">' + groups[g].map(function (k) {
        return '<option value="' + k + '"' + (k === sel ? " selected" : "") + ' title="' + esc(k + ": " + S.fields[k].desc) + '">' + esc(U.label(k)) + "</option>";
      }).join("") + "</optgroup>";
    });
    return h;
  }
  function numText(v) { return v === undefined || v === null ? "" : String(v); }

  function renderForm() {
    var u = spec.universe && typeof spec.universe === "object" ? spec.universe : {};
    var h = [];
    h.push('<div class="row"><label>Observation <input id="f-obs" value="' + esc(spec.observation || "") + '"></label></div>');
    h.push('<div class="formsec">Universe</div><div class="row wrap">');
    [["market_cap_min", "Market cap ≥ (USD)"], ["market_cap_max", "Market cap ≤ (USD)"], ["min_price", "Price ≥ ($)"],
     ["min_avg_dollar_volume", "50-day $ volume ≥"]].forEach(function (k) {
      h.push('<label class="sm">' + k[1] + ' <input data-u="' + k[0] + '" value="' + esc(numText(u[k[0]])) + '" placeholder="none" inputmode="decimal"></label>');
    });
    h.push("</div>");
    h.push('<details class="pick"><summary>Industry groups (SEC SIC) <span class="cnt">— ' + ((u.industries || []).length || "any") + "</span></summary><div class=\"checks\">" +
      Object.keys(S.industries).map(function (k) {
        return '<label title="' + esc(S.industries[k][0]) + '"><input type="checkbox" data-ind="' + k + '"' + ((u.industries || []).indexOf(k) >= 0 ? " checked" : "") + "> " + k + "</label>";
      }).join("") + "</div></details>");
    h.push('<details class="pick"><summary>Theme baskets (curated in code) <span class="cnt">— ' + ((u.themes || []).length || "none") + "</span></summary><div class=\"checks\">" +
      Object.keys(S.themes).map(function (k) {
        return '<label title="' + esc(S.themes[k][0] + ": " + S.themes[k][1].join(", ")) + '"><input type="checkbox" data-th="' + k + '"' + ((u.themes || []).indexOf(k) >= 0 ? " checked" : "") + "> " + k + "</label>";
      }).join("") + "</div></details>");
    h.push('<div class="formsec">Conditions (all must hold; ratios are decimals: 0.10 = 10%)</div>');
    (Array.isArray(spec.conditions) ? spec.conditions : []).forEach(function (c, i) {
      var f = S.fields[c.field], isBool = f && f.kind === "bool", isRef = c && Object.prototype.hasOwnProperty.call(c, "ref");
      h.push('<div class="row cond" data-i="' + i + '"><select data-c="field">' + fieldOptions(c.field, true) + "</select>");
      h.push('<select data-c="op">' + S.ops.map(function (o) { return "<option" + (o === c.op ? " selected" : "") + ">" + esc(o) + "</option>"; }).join("") + "</select>");
      if (isBool) {
        h.push('<select data-c="bool"><option value="true"' + (c.value === true ? " selected" : "") + '>true</option><option value="false"' + (c.value === false ? " selected" : "") + ">false</option></select>");
      } else {
        h.push('<select data-c="mode"><option value="value"' + (!isRef ? " selected" : "") + '>value</option><option value="ref"' + (isRef ? " selected" : "") + ">field</option></select>");
        if (isRef) h.push('<select data-c="ref">' + fieldOptions(c.ref, false) + "</select>");
        else h.push('<input data-c="value" value="' + esc(Array.isArray(c.value) ? c.value.join(", ") : numText(c.value)) + '" placeholder="' + (c.op === "between" ? "low, high" : "number") + '">');
      }
      h.push('<button class="ghost x" data-c="del" title="remove">×</button></div>');
    });
    h.push('<div class="row"><button class="ghost" id="f-addc">+ condition</button></div>');
    h.push('<div class="formsec">Rank (weighted mean of percentile ranks)</div>');
    (Array.isArray(spec.rank) ? spec.rank : []).forEach(function (r, i) {
      h.push('<div class="row rk" data-i="' + i + '"><select data-r="field">' + fieldOptions(r.field, false) + "</select>" +
        '<select data-r="direction"><option value="desc"' + (r.direction === "desc" ? " selected" : "") + '>higher is better</option><option value="asc"' + (r.direction === "asc" ? " selected" : "") + ">lower is better</option></select>" +
        '<label class="sm">weight <input data-r="weight" value="' + esc(numText(r.weight == null ? 1 : r.weight)) + '" inputmode="decimal"></label>' +
        '<button class="ghost x" data-r="del" title="remove">×</button></div>');
    });
    h.push('<div class="row"><button class="ghost" id="f-addr">+ rank key</button>' +
      '<label class="sm">Explain top <input id="f-topn" value="' + esc(numText(spec.top_n)) + '" inputmode="numeric"></label></div>');
    byId("t-form").innerHTML = h.join("");
    wireForm();
  }

  function parseNum(t) { t = String(t).trim().replace(/,/g, ""); if (t === "") return undefined; var v = Number(t); return isNaN(v) ? t : v; }

  function wireForm() {
    var form = byId("t-form");
    byId("f-obs").oninput = function () { spec.observation = this.value; syncJson(); };
    form.querySelectorAll("[data-u]").forEach(function (el) {
      el.onchange = function () {
        if (typeof spec.universe !== "object" || !spec.universe) spec.universe = {};
        var v = parseNum(el.value);
        if (v === undefined) delete spec.universe[el.dataset.u]; else spec.universe[el.dataset.u] = v;
        syncJson();
      };
    });
    [["data-ind", "industries"], ["data-th", "themes"]].forEach(function (p) {
      form.querySelectorAll("[" + p[0] + "]").forEach(function (el) {
        el.onchange = function () {
          if (typeof spec.universe !== "object" || !spec.universe) spec.universe = {};
          var list = (spec.universe[p[1]] || []).filter(function (x) { return x !== el.getAttribute(p[0]); });
          if (el.checked) list.push(el.getAttribute(p[0]));
          if (list.length) spec.universe[p[1]] = list; else delete spec.universe[p[1]];
          syncJson();
          el.closest("details").querySelector(".cnt").textContent = "— " + (list.length || (p[1] === "themes" ? "none" : "any"));
        };
      });
    });
    form.querySelectorAll(".cond").forEach(function (row) {
      var i = +row.dataset.i, c = spec.conditions[i];
      row.querySelectorAll("[data-c]").forEach(function (el) {
        var k = el.dataset.c;
        var handler = function () {
          if (k === "del") { spec.conditions.splice(i, 1); renderForm(); syncJson(); return; }
          if (k === "field") {
            c.field = el.value;
            var f = S.fields[c.field];
            if (f && f.kind === "bool") { c.op = "=="; c.value = true; delete c.ref; }
            renderForm();
          } else if (k === "op") { c.op = el.value; if (c.op === "between" && !Array.isArray(c.value)) c.value = [0, 1]; renderForm(); }
          else if (k === "bool") c.value = el.value === "true";
          else if (k === "mode") {
            if (el.value === "ref") { delete c.value; c.ref = "sma50"; } else { delete c.ref; c.value = 0; }
            renderForm();
          } else if (k === "ref") c.ref = el.value;
          else if (k === "value") {
            c.value = c.op === "between" ? el.value.split(",").map(parseNum) : parseNum(el.value);
          }
          syncJson();
        };
        if (el.tagName === "BUTTON") el.onclick = handler; else el.onchange = handler;
      });
    });
    form.querySelectorAll(".rk").forEach(function (row) {
      var i = +row.dataset.i, r = spec.rank[i];
      row.querySelectorAll("[data-r]").forEach(function (el) {
        var k = el.dataset.r;
        var handler = function () {
          if (k === "del") { spec.rank.splice(i, 1); renderForm(); }
          else if (k === "weight") r.weight = parseNum(el.value);
          else r[k] = el.value;
          syncJson();
        };
        if (el.tagName === "BUTTON") el.onclick = handler; else el.onchange = handler;
      });
    });
    byId("f-addc").onclick = function () {
      if (!Array.isArray(spec.conditions)) spec.conditions = [];
      spec.conditions.push({ field: "rsi14", op: "<", value: 30 }); renderForm(); syncJson();
    };
    byId("f-addr").onclick = function () {
      if (!Array.isArray(spec.rank)) spec.rank = [];
      spec.rank.push({ field: "market_cap", direction: "desc", weight: 1 }); renderForm(); syncJson();
    };
    byId("f-topn").onchange = function () { var v = parseNum(this.value); if (v === undefined) delete spec.top_n; else spec.top_n = v; syncJson(); };
  }

  // ---------- run (Advanced) ----------
  function runAdvanced() {
    var raw;
    try { raw = JSON.parse(byId("t-json").value); }
    catch (e) { showOut('<div class="panel refusal"><strong>Not valid JSON:</strong> ' + esc(e.message) + "</div>"); return; }
    var v = ScoutCore.validate(raw, S.short_interest_available);
    if (!v.ok) {
      showOut('<div class="panel refusal"><strong>Refused by the checks</strong> (same rules as the Python app; nothing was screened):<ul>' +
        v.problems.map(function (p) { return "<li>" + esc(p) + "</li>"; }).join("") + "</ul></div>");
      byId("t-out").scrollIntoView({ behavior: "smooth", block: "start" });
      return;
    }
    var res = screen(v.spec), exs = {};
    res.rows.slice(0, v.spec.top_n).forEach(function (r) { if (cached[r.symbol]) exs[r.symbol] = cached[r.symbol].ex; });
    renderResults({ spec: v.spec, funnel: res.funnel, rows: res.rows, nRanked: res.n, topN: v.spec.top_n, cols: res.cols,
      note: "<strong>Data as of the " + esc(S.data.last_price_date) + " close.</strong> Screened in your browser.",
      exNote: "Where a name already has an explanation from a recorded run it is shown; it was written for that run’s screen, not this one. For fresh, cited explanations, describe this screen in <em>Ask your own question</em>.",
      explanations: exs, missingNote: "No recorded explanation for this name." });
    byId("t-out").scrollIntoView({ behavior: "smooth", block: "start" });
  }

  // ---------- boot ----------
  renderAsk();
  renderChips();
  checkApi();
  if (adv) adv.addEventListener("toggle", function () { if (adv.open) ensureLoaded(); });
  var q = new URLSearchParams(location.search);
  if (q.get("example")) runChip(q.get("example"));
  if (location.hash === "#advanced") { adv.open = true; ensureLoaded(); }
})();
