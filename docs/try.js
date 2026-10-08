/* "Try your own": build or translate a screen spec and run it in the browser on the shipped snapshot.
 *
 * Everything runs locally in the page. The snapshot (2026-10-08 close) loads only when the panel opens.
 * Optional: translate an observation with your own DeepSeek key. The key lives in a JS variable for this
 * page only, is never stored, and is sent only to api.deepseek.com (which allows browser CORS).
 */
(function () {
  "use strict";
  var U = window.ScoutUI, esc = U.esc;
  var SNAP_FILE = "data/snapshot-2026-10-08.js";
  var S = null, SNAP = null, loading = null;
  var apiKey = "";                // memory only
  var root = document.getElementById("try-body");
  var panel = document.getElementById("try");

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
    root.innerHTML = '<p class="muted" id="try-loading">Loading the 2026-10-08 snapshot for ~3,800 companies (about 2 MB)…</p>';
    loading = loadScript("data/schema.js").then(function () {
      S = window.SCOUT_SCHEMA; ScoutCore.setSchema(S);
      return loadScript(SNAP_FILE);
    }).then(function () { SNAP = window.SCOUT_SNAPSHOT; build(); })
      .catch(function (e) { root.innerHTML = '<p class="err">' + esc(e.message) + "</p>"; loading = null; });
    return loading;
  }

  // ---------- state ----------
  var spec = null;
  function blankSpec() {
    return { version: 1, observation: "My observation", universe: { market_cap_min: 2e9 },
             conditions: [{ field: "drawdown_52w", op: "<=", value: -0.2 }],
             rank: [{ field: "drawdown_52w", direction: "asc", weight: 1 }], top_n: 5, unmapped: [], notes: "" };
  }
  function clone(x) { return JSON.parse(JSON.stringify(x)); }

  // cached explanations from the recorded runs, by symbol
  var cached = {};
  (window.SCOUT_RUNS || []).forEach(function (r) {
    r.explanations.forEach(function (ex) { cached[ex.symbol] = { ex: ex, run: r.id, as_of: r.as_of }; });
  });

  // ---------- UI skeleton ----------
  function build() {
    var runs = window.SCOUT_RUNS || [];
    var opts = runs.map(function (r) { return '<option value="' + esc(r.id) + '">Recorded run: ' + esc(r.observation.slice(0, 70)) + "…</option>"; }).join("");
    root.innerHTML =
      '<p class="label-note"><strong>Snapshot as of ' + esc(S.data.last_price_date) + ' close; explanations need the local app (SEC documents can’t be fetched from a browser).</strong> ' +
      esc(S.data.n_companies) + " companies. Universe: " + esc(S.data.universe_rule) + ".</p>" +
      '<div class="try-grid">' +
      '<div class="subpanel"><h3>A · Translate an observation (optional, your own DeepSeek key)</h3>' +
      '<textarea id="t-obs" rows="3" placeholder="e.g. Small caps under $2B with revenue growth above 25%, positive free cash flow, and RSI below 40"></textarea>' +
      '<div class="row"><input id="t-key" type="password" autocomplete="off" spellcheck="false" placeholder="DeepSeek API key (kept in memory only)">' +
      '<button id="t-translate">Translate</button><button id="t-forget" class="ghost">Forget key</button></div>' +
      '<p class="meta">The key stays in this page’s memory and is sent only to api.deepseek.com; it is never stored or sent anywhere else. ' +
      "The model (" + esc(S.model) + ") only fills the spec below; nothing runs until you press Run.</p>" +
      '<div id="t-status" class="meta"></div></div>' +
      '<div class="subpanel"><h3>B · Edit the spec (whitelisted fields only)</h3>' +
      '<div class="row"><select id="t-template"><option value="">Start from…</option>' + opts + '<option value="__blank">Blank example</option></select></div>' +
      '<div id="t-form"></div>' +
      '<details><summary>Edit as JSON</summary><textarea id="t-json" rows="14" spellcheck="false"></textarea>' +
      '<div class="row"><button id="t-apply" class="ghost">Load JSON into the form</button></div></details>' +
      '<div class="row"><button id="t-run" class="primary">Validate and run</button></div></div>' +
      "</div>" +
      '<div id="t-out"></div>';
    byId("t-template").onchange = function () {
      var v = this.value; if (!v) return;
      var r = runs.filter(function (x) { return x.id === v; })[0];
      setSpec(r ? clone(r.spec) : blankSpec());
    };
    byId("t-apply").onclick = function () {
      try { setSpec(JSON.parse(byId("t-json").value)); status(""); }
      catch (e) { showOut('<div class="panel refusal"><strong>Not valid JSON:</strong> ' + esc(e.message) + "</div>"); }
    };
    byId("t-run").onclick = run;
    byId("t-translate").onclick = translate;
    byId("t-forget").onclick = function () { apiKey = ""; byId("t-key").value = ""; status("Key forgotten."); };
    setSpec(runs.length ? clone(runs[0].spec) : blankSpec());
  }
  function byId(id) { return document.getElementById(id); }
  function status(html) { byId("t-status").innerHTML = html; }
  function showOut(html) { byId("t-out").innerHTML = html; }

  // ---------- form <-> spec ----------
  function setSpec(s) { spec = s; renderForm(); syncJson(); }
  function syncJson() { byId("t-json").value = JSON.stringify(spec, null, 2); }

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
      h += '<optgroup label="' + esc(g) + '">' + groups[g].map(function (k) {
        return '<option value="' + k + '"' + (k === sel ? " selected" : "") + ' title="' + esc(S.fields[k].desc) + '">' + k + "</option>";
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
    [["market_cap_min", "Market cap ≥ (USD)"], ["market_cap_max", "Market cap ≤ (USD)"], ["min_price", "Close ≥ ($)"],
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

  // ---------- run ----------
  function run() {
    var raw;
    try { raw = JSON.parse(byId("t-json").value); }
    catch (e) { showOut('<div class="panel refusal"><strong>Not valid JSON:</strong> ' + esc(e.message) + "</div>"); return; }
    var v = ScoutCore.validate(raw, S.short_interest_available);
    if (!v.ok) {
      showOut('<div class="panel refusal"><strong>Refused by the validator</strong> (same rules as the Python app; nothing was screened):<ul>' +
        v.problems.map(function (p) { return "<li>" + esc(p) + "</li>"; }).join("") + "</ul></div>");
      return;
    }
    var t0 = performance.now();
    var res = ScoutCore.runScreen(SNAP, v.spec);
    var ranked = ScoutCore.rank(SNAP, res.survivors, v.spec);
    var ms = Math.round(performance.now() - t0);
    var cols = U.tableColumns(v.spec), C = SNAP.columns;
    var rows = ranked.slice(0, 25).map(function (r) {
      var o = { rank: r.rank, score: r.score };
      cols.forEach(function (c) { if (c !== "rank" && c !== "score") o[c] = C[c] ? C[c][r._i] : null; });
      return o;
    });
    var h = [];
    h.push('<div class="panel"><p class="label-note"><strong>Snapshot as of ' + esc(S.data.last_price_date) + " close; explanations need the local app (SEC documents can’t be fetched from a browser).</strong> Screened " +
      esc(SNAP.n) + " companies in " + ms + " ms, in your browser.</p>" + U.specHtml(v.spec, "Screen spec — validated in the browser") + "</div>");
    h.push('<div class="panel">' + U.funnelHtml(res.funnel) + "</div>");
    h.push('<div class="panel">' + U.tableHtml(cols, rows, v.spec.top_n, ranked.length) + "</div>");
    var top = ranked.slice(0, v.spec.top_n);
    if (top.length) {
      h.push('<div class="panel"><div class="step">Explanations for the top ' + top.length + "</div>");
      h.push('<p class="muted" style="margin-top:0">The browser cannot fetch SEC filings (no CORS), so new explanations need the local app: <code>uv run scout serve</code>. ' +
        "Where a name already has a recorded explanation from one of the recorded runs, it is shown below; it was written for that run’s screen, not this one.</p><div class=\"cards\">");
      top.forEach(function (r) {
        var sym = C.symbol[r._i], c = cached[sym];
        if (c) h.push(U.cardHtml(c.ex, "Recorded in run <strong>" + esc(c.run) + "</strong> (as of " + esc(c.as_of) + ")."));
        else h.push('<div class="card"><div class="hd"><h3>' + esc(sym) + '</h3><span class="verdict thin">no recorded explanation</span></div><p class="meta">' +
          esc(C.name[r._i] || "") + ". Run this spec in the local app to read its 8-K, MD&amp;A and news with verified citations.</p></div>");
      });
      h.push("</div></div>");
    }
    showOut(h.join(""));
    byId("t-out").scrollIntoView({ behavior: "smooth", block: "start" });
  }

  // ---------- bring-your-own-key translation ----------
  function callModel(messages, signal) {
    return fetch("https://api.deepseek.com/chat/completions", {
      method: "POST", signal: signal,
      headers: { "Authorization": "Bearer " + apiKey, "Content-Type": "application/json" },
      body: JSON.stringify({ model: S.model, messages: messages, temperature: 0, max_tokens: 8000,
                             response_format: { type: "json_object" } })
    }).then(function (r) {
      if (!r.ok) return r.text().then(function (t) { throw new Error("DeepSeek HTTP " + r.status + ": " + t.slice(0, 200)); });
      return r.json();
    }).then(function (j) { return (j.choices[0].message.content || ""); });
  }
  function parseModelJson(t) {
    t = t.trim();
    if (t.indexOf("```") === 0) t = t.split("\n").slice(1).join("\n").replace(/```\s*$/, "");
    return JSON.parse(t);
  }

  function translate() {
    var obs = byId("t-obs").value.trim();
    var k = byId("t-key").value.trim();
    if (k) { apiKey = k; byId("t-key").value = ""; byId("t-key").placeholder = "key held in memory (Forget key to clear)"; }
    if (!obs) { status("Write an observation first."); return; }
    if (!apiKey) { status("Paste a DeepSeek API key, or skip this and edit the spec directly."); return; }
    var ctrl = new AbortController(), t0 = Date.now();
    var timer = setInterval(function () { status("Asking " + esc(S.model) + "… " + Math.round((Date.now() - t0) / 1000) + " s (reasoning models take 10-60 s)"); }, 500);
    var timeout = setTimeout(function () { ctrl.abort(); }, 150000);
    var btn = byId("t-translate"); btn.disabled = true;
    var messages = [{ role: "system", content: S.translate_system_prompt }, { role: "user", content: obs }];
    var attempt = function (n) {
      return callModel(messages, ctrl.signal).then(function (raw) {
        var d, problems;
        try { d = parseModelJson(raw); } catch (e) { problems = ["not valid JSON: " + e.message]; }
        if (d && typeof d === "object" && !Array.isArray(d)) d.observation = obs;
        if (!problems) { var v = ScoutCore.validate(d, S.short_interest_available); if (v.ok) return { spec: v.spec, rounds: n }; problems = v.problems; }
        if (n >= 1) { var err = new Error("the model did not produce a valid spec after a correction round"); err.problems = problems; err.raw = d; throw err; }
        messages = messages.concat([{ role: "assistant", content: raw }, { role: "user", content:
          "The screener refused that spec:\n- " + problems.join("\n- ") + "\nReturn a corrected JSON spec. Move anything you cannot express into 'unmapped'." }]);
        return attempt(n + 1);
      });
    };
    attempt(0).then(function (r) {
      setSpec(r.spec);
      status("Proposed by the model" + (r.rounds ? " after one correction round" : "") + " and accepted by the validator. Review it below, then press <strong>Validate and run</strong>." +
        (r.spec.unmapped.length ? " Not screened: " + r.spec.unmapped.map(function (u) { return "“" + esc(u.text) + "”"; }).join(", ") + "." : ""));
      byId("t-form").scrollIntoView({ behavior: "smooth", block: "start" });
    }).catch(function (e) {
      var msg = e.name === "AbortError" ? "Timed out after 150 s." : esc(e.message);
      if (e.problems) {
        msg += "<ul>" + e.problems.map(function (p) { return "<li>" + esc(p) + "</li>"; }).join("") + "</ul>";
        if (e.raw) setSpec(e.raw);
        msg += "The refused spec is loaded below so you can fix it by hand.";
      }
      status('<span class="err">' + msg + "</span>");
    }).then(function () { clearInterval(timer); clearTimeout(timeout); btn.disabled = false; });
  }

  if (panel) {
    panel.addEventListener("toggle", function () { if (panel.open) ensureLoaded(); });
    if (location.hash === "#try") { panel.open = true; ensureLoaded(); }
    window.addEventListener("hashchange", function () { if (location.hash === "#try") { panel.open = true; ensureLoaded(); } });
  }
})();
