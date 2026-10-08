/* equity-scout browser core: spec validation, screen, funnel and ranking.
 *
 * A line-by-line port of src/scout/spec.py (validate), src/scout/screen.py
 * (run_screen, rank, describe). tests/test_browser_parity.py runs the recorded
 * specs and a set of invalid specs through both implementations and requires
 * identical funnels, rankings and refusal messages.
 *
 * Works in the browser (window.ScoutCore) and in Node (module.exports).
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.ScoutCore = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  // ---------- Python formatting helpers ----------
  function pyStrRepr(s) { return "'" + String(s) + "'"; }
  function pyList(a) { return "[" + a.map(pyStrRepr).join(", ") + "]"; }
  function pyRepr(v) {
    if (v === null || v === undefined) return "None";
    if (v === true) return "True";
    if (v === false) return "False";
    if (typeof v === "string") return pyStrRepr(v);
    if (typeof v === "number") return pyNum(v);
    if (Array.isArray(v)) return "[" + v.map(pyRepr).join(", ") + "]";
    return "{" + Object.keys(v).map(function (k) { return pyStrRepr(k) + ": " + pyRepr(v[k]); }).join(", ") + "}";
  }
  function pyNum(x) { return String(x); }
  function sortedKeys(setLike) { return Object.keys(setLike).sort(); }

  // round-half-even on the exact binary value, like Python's format()
  function pyFixed(x, d) {
    var s = x.toFixed(d);
    var scaled = Math.abs(x) * Math.pow(10, d);
    var frac = scaled - Math.floor(scaled);
    if (frac === 0.5) {                           // exact tie: Python rounds half to even
      var lo = Math.floor(scaled);
      var n = (lo % 2 === 0) ? lo : lo + 1;
      s = (n / Math.pow(10, d)).toFixed(d);
      if (x < 0) s = "-" + s;
    }
    return s;
  }
  function withCommas(s) {
    var neg = s[0] === "-";
    if (neg) s = s.slice(1);
    var parts = s.split(".");
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    return (neg ? "-" : "") + parts.join(".");
  }
  // Python's format(v, "g"): 6 significant digits, trailing zeros stripped
  function pyG(v) {
    if (v === 0) return (1 / v < 0) ? "-0" : "0";
    if (!isFinite(v)) return v > 0 ? "inf" : (v < 0 ? "-inf" : "nan");
    var exp = Math.floor(Math.log10(Math.abs(v)));
    var m = Number(Math.abs(v).toPrecision(6));
    exp = Math.floor(Math.log10(m));
    var out;
    if (exp < -4 || exp >= 6) {
      var mant = (m / Math.pow(10, exp)).toPrecision(6).replace(/\.?0+$/, "");
      out = mant + "e" + (exp < 0 ? "-" : "+") + (Math.abs(exp) < 10 ? "0" : "") + Math.abs(exp);
    } else {
      out = m.toFixed(Math.max(0, 5 - exp));
      if (out.indexOf(".") >= 0) out = out.replace(/\.?0+$/, "");
    }
    return (v < 0 ? "-" : "") + out;
  }

  // ---------- schema (filled from docs/data/schema.js) ----------
  var S = null;
  function setSchema(schema) { S = schema; }

  function isNum(x) { return typeof x === "number" && isFinite(x); }
  function isObj(x) { return x !== null && typeof x === "object" && !Array.isArray(x); }
  function has(o, k) { return Object.prototype.hasOwnProperty.call(o, k); }

  function validate(d, shortInterestAvailable) {
    if (shortInterestAvailable === undefined) shortInterestAvailable = true;
    var F = S.fields, p = [];
    if (!isObj(d)) return { ok: false, problems: ["spec must be a JSON object"] };
    Object.keys(d).forEach(function (k) {
      if (S.top_keys.indexOf(k) < 0) p.push("unknown top-level key '" + k + "' (allowed: " + pyList(S.top_keys.slice().sort()) + ")");
    });
    var obs = d.observation;
    if (typeof obs !== "string" || !obs.trim()) p.push("'observation' must be the user's text");

    var u = d.universe;
    if (!u || (Array.isArray(u) && !u.length) || u === 0 || u === "") u = {};
    if (!isObj(u)) { p.push("'universe' must be an object"); u = {}; }
    Object.keys(u).forEach(function (k) {
      var v = u[k];
      if (S.universe_keys.indexOf(k) < 0) {
        p.push("unknown universe key '" + k + "' (allowed: " + pyList(S.universe_keys.slice().sort()) + ")");
      } else if (k === "industries" || k === "exclude_industries" || k === "themes") {
        var allowed = k === "themes" ? S.themes : S.industries;
        var label = k === "themes" ? "theme basket" : "industry group";
        if (!Array.isArray(v) || !v.every(function (x) { return typeof x === "string"; })) {
          p.push("universe." + k + " must be a list of " + label + " names");
        } else {
          v.forEach(function (x) {
            if (!has(allowed, x)) p.push("unknown " + label + " '" + x + "' (allowed: " + pyList(sortedKeys(allowed)) + ")");
          });
        }
      } else if (!isNum(v) || v < 0) {
        p.push("universe." + k + " must be a non-negative number, got " + pyRepr(v));
      }
    });
    if (isNum(u.market_cap_min) && isNum(u.market_cap_max) && u.market_cap_min >= u.market_cap_max)
      p.push("universe.market_cap_min must be below market_cap_max");

    var conds = d.conditions;
    if (!Array.isArray(conds) || !conds.length) { p.push("'conditions' must be a non-empty list"); conds = []; }
    conds.forEach(function (c, i) {
      var where = "conditions[" + i + "]";
      if (!isObj(c)) { p.push(where + " must be an object"); return; }
      Object.keys(c).forEach(function (k) {
        if (S.cond_keys.indexOf(k) < 0) p.push(where + ": unknown key '" + k + "' (allowed: " + pyList(S.cond_keys.slice().sort()) + ")");
      });
      var f = c.field;
      if (typeof f !== "string" || !has(F, f)) { p.push(where + ": unknown field " + pyRepr(f) + "; it is not in the whitelist of computed fields"); return; }
      var fd = F[f];
      if (fd.group === "short_interest" && !shortInterestAvailable) { p.push(where + ": '" + f + "' refused: short interest unavailable in free data"); return; }
      var op = c.op;
      if (S.ops.indexOf(op) < 0) { p.push(where + ": operator " + pyRepr(op) + " not allowed (allowed: " + pyList(S.ops.slice().sort()) + ")"); return; }
      var hasVal = has(c, "value"), hasRef = has(c, "ref");
      if (hasVal === hasRef) { p.push(where + ": give exactly one of 'value' (a threshold) or 'ref' (another field)"); return; }
      if (fd.kind === "bool") {
        if (op !== "==" || typeof c.value !== "boolean") p.push(where + ": '" + f + "' is boolean; use op '==' with value true/false");
        return;
      }
      if (op === "==") { p.push(where + ": '==' is only for boolean fields"); return; }
      if (hasRef) {
        var r = c.ref;
        if (typeof r !== "string" || !has(F, r)) p.push(where + ": unknown ref field " + pyRepr(r));
        else if (F[r].kind !== fd.kind) p.push(where + ": cannot compare '" + f + "' (" + fd.kind + ") with '" + r + "' (" + F[r].kind + ")");
        else if (op === "between") p.push(where + ": 'between' needs a [low, high] value, not a ref");
        return;
      }
      var v = c.value, vals;
      if (op === "between") {
        if (!(Array.isArray(v) && v.length === 2 && v.every(isNum) && v[0] < v[1])) {
          p.push(where + ": 'between' needs value [low, high] with low < high"); return;
        }
        vals = v;
      } else if (!isNum(v)) {
        p.push(where + ": value must be a number, got " + pyRepr(v)); return;
      } else vals = [v];
      vals.forEach(function (x) {
        if (fd.kind === "ratio" && Math.abs(x) > 20) p.push(where + ": " + f + " is a decimal ratio (0.10 = 10%); " + pyNum(x) + " looks like a percent");
        if (f === "rsi14" && !(x >= 0 && x <= 100)) p.push(where + ": rsi14 thresholds must be within 0-100");
      });
    });

    var rank = d.rank;
    if (!Array.isArray(rank) || !rank.length) { p.push("'rank' must be a non-empty list of {field, direction, weight}"); rank = []; }
    rank.forEach(function (r, i) {
      var where = "rank[" + i + "]";
      if (!isObj(r)) { p.push(where + " must be an object"); return; }
      Object.keys(r).forEach(function (k) { if (S.rank_keys.indexOf(k) < 0) p.push(where + ": unknown key '" + k + "'"); });
      if (typeof r.field !== "string" || !has(F, r.field) || F[r.field].kind === "bool")
        p.push(where + ": field " + pyRepr(r.field) + " is not a rankable whitelisted field");
      else if (F[r.field].group === "short_interest" && !shortInterestAvailable)
        p.push(where + ": '" + r.field + "' refused: short interest unavailable in free data");
      if (r.direction !== "asc" && r.direction !== "desc") p.push(where + ": direction must be 'asc' or 'desc'");
      var w = has(r, "weight") ? r.weight : 1;
      if (!isNum(w) || w <= 0) p.push(where + ": weight must be a positive number");
    });

    var topN = has(d, "top_n") ? d.top_n : 5;
    if (typeof topN !== "number" || !Number.isInteger(topN) || topN < 1 || topN > S.max_top_n)
      p.push("top_n must be an integer 1-" + S.max_top_n);

    var unm = d.unmapped;
    if (!unm) unm = [];
    if (!Array.isArray(unm) || !unm.every(function (x) { return isObj(x) && has(x, "text") && has(x, "reason"); })) {
      p.push("'unmapped' must be a list of {text, reason}"); unm = [];
    }
    if (p.length) return { ok: false, problems: p };
    return { ok: true, spec: {
      version: 1, observation: obs.trim(), universe: u, conditions: conds,
      rank: rank.map(function (r) { return { field: r.field, direction: r.direction, weight: has(r, "weight") ? r.weight : 1 }; }),
      top_n: topN, unmapped: unm, notes: d.notes === undefined ? "" : String(d.notes) } };
  }

  // ---------- screen ----------
  function fmtValue(field, v) {
    var kind = S.fields[field] ? S.fields[field].kind : "number";
    if (typeof v === "boolean") return v ? "true" : "false";
    if (kind === "ratio") return Math.abs(v) < 20 ? ((v * 100 >= 0 && !(Object.is(v * 100, -0)) ? "+" : "") + pyFixed(v * 100, 1) + "%") : pyNum(v);
    if (kind === "usd" && Math.abs(v) >= 1e6)
      return Math.abs(v) >= 1e9 ? "$" + withCommas(pyFixed(v / 1e9, 2)) + "B" : "$" + withCommas(pyFixed(v / 1e6, 0)) + "M";
    return pyG(v);
  }
  function describe(c) {
    if (has(c, "ref")) return c.field + " " + c.op + " " + c.ref;
    if (c.op === "between") return fmtValue(c.field, c.value[0]) + " <= " + c.field + " <= " + fmtValue(c.field, c.value[1]);
    return c.field + " " + c.op + " " + fmtValue(c.field, c.value);
  }

  var CMP = { "<": function (a, b) { return a < b; }, "<=": function (a, b) { return a <= b; },
              ">": function (a, b) { return a > b; }, ">=": function (a, b) { return a >= b; } };
  function num(v) { return (typeof v === "number" && isFinite(v)) ? v : null; }

  // snapshot: {columns: {name: [...]}, n}; rows are referenced by index
  function col(snap, name) { return snap.columns[name]; }

  function maskCondition(snap, idx, c) {
    var f = c.field, x = col(snap, f), pass = [], miss = [];
    if (S.fields[f].kind === "bool") {
      idx.forEach(function (i) { var v = x[i]; var m = (v === null || v === undefined); miss.push(m); pass.push(!m && v === c.value); });
      return [pass, miss];
    }
    if (has(c, "ref")) {
      var y = col(snap, c.ref);
      idx.forEach(function (i) { var a = num(x[i]), b = num(y[i]); var m = a === null || b === null; miss.push(m); pass.push(!m && CMP[c.op](a, b)); });
      return [pass, miss];
    }
    idx.forEach(function (i) {
      var a = num(x[i]); var m = a === null; miss.push(m);
      if (m) pass.push(false);
      else if (c.op === "between") pass.push(a >= c.value[0] && a <= c.value[1]);
      else pass.push(CMP[c.op](a, c.value));
    });
    return [pass, miss];
  }

  function universeSteps(spec) {
    var u = spec.universe, steps = [];
    if (has(u, "industries") || has(u, "themes")) {
      var codes = {}, syms = {};
      (u.industries || []).forEach(function (g) { S.industries[g][1].forEach(function (c) { codes[c] = 1; }); });
      (u.themes || []).forEach(function (t) { S.themes[t][1].forEach(function (s) { syms[s] = 1; }); });
      var anyCodes = Object.keys(codes).length > 0;
      var parts = [];
      if (u.industries && u.industries.length) parts.push("industry in " + pyList(u.industries));
      if (u.themes && u.themes.length) parts.push("theme in " + pyList(u.themes));
      steps.push([parts.join(" or "), function (snap, idx) {
        var sic = col(snap, "sic"), sym = col(snap, "symbol"), pass = [], miss = [];
        idx.forEach(function (i) {
          var s = num(sic[i]), inTheme = has(syms, sym[i]);
          pass.push((s !== null && has(codes, s)) || inTheme);
          miss.push(s === null && !inTheme && anyCodes);
        });
        return [pass, miss];
      }]);
    }
    if (has(u, "exclude_industries")) {
      var codesX = {};
      u.exclude_industries.forEach(function (g) { S.industries[g][1].forEach(function (c) { codesX[c] = 1; }); });
      steps.push(["industry not in " + pyList(u.exclude_industries), function (snap, idx) {
        var sic = col(snap, "sic"), pass = [], miss = [];
        idx.forEach(function (i) { var s = num(sic[i]); pass.push(s !== null && !has(codesX, s)); miss.push(s === null); });
        return [pass, miss];
      }]);
    }
    [["market_cap_min", "market_cap", ">="], ["market_cap_max", "market_cap", "<="],
     ["min_price", "close", ">="], ["min_avg_dollar_volume", "avg_dollar_volume_50d", ">="]].forEach(function (t) {
      if (has(u, t[0])) {
        var c = { field: t[1], op: t[2], value: u[t[0]] };
        steps.push([describe(c), function (snap, idx) { return maskCondition(snap, idx, c); }]);
      }
    });
    return steps;
  }

  function runScreen(snap, spec) {
    var idx = [];
    for (var i = 0; i < snap.n; i++) idx.push(i);
    var funnel = [{ step: "universe (liquid US common stocks with SEC filings)", kind: "start",
                    n_in: idx.length, n_pass: idx.length, n_fail: 0, n_missing: 0 }];
    var steps = universeSteps(spec).map(function (s) { return [s[0], s[1], "universe"]; });
    spec.conditions.forEach(function (c) {
      steps.push([describe(c), function (snap, ix) { return maskCondition(snap, ix, c); }, "condition"]);
    });
    steps.forEach(function (s) {
      var r = s[1](snap, idx), pass = r[0], miss = r[1];
      var nIn = idx.length, nPass = 0, nMiss = 0, next = [];
      for (var k = 0; k < nIn; k++) {
        if (pass[k]) { nPass++; next.push(idx[k]); }
        else if (miss[k]) nMiss++;
      }
      funnel.push({ step: s[0], kind: s[2], n_in: nIn, n_pass: nPass, n_fail: nIn - nPass - nMiss, n_missing: nMiss });
      idx = next;
    });
    return { funnel: funnel, survivors: idx };
  }

  // pandas Series.rank(pct=True, method="average", ascending=asc); NaN stays NaN
  function pctRank(vals, asc) {
    var items = [];
    vals.forEach(function (v, i) { if (v !== null) items.push([v, i]); });
    items.sort(function (a, b) { return asc ? a[0] - b[0] : b[0] - a[0]; });
    var out = vals.map(function () { return null; }), n = items.length, k = 0;
    while (k < n) {
      var j = k;
      while (j + 1 < n && items[j + 1][0] === items[k][0]) j++;
      var avg = (k + 1 + j + 1) / 2;
      for (var t = k; t <= j; t++) out[items[t][1]] = avg / n;
      k = j + 1;
    }
    return out;
  }

  function rank(snap, survivors, spec) {
    var totalW = spec.rank.reduce(function (a, r) { return a + r.weight; }, 0);
    var score = survivors.map(function () { return 0; });
    var pcts = {};
    spec.rank.forEach(function (r) {
      var x = col(snap, r.field);
      var vals = survivors.map(function (i) { return num(x[i]); });
      var pct = pctRank(vals, r.direction === "desc").map(function (v) { return v === null ? 0 : v; });
      for (var k = 0; k < score.length; k++) score[k] += r.weight * pct[k];
      pcts[r.field] = pct;
    });
    var mc = col(snap, "market_cap"), sym = col(snap, "symbol");
    var rows = survivors.map(function (i, k) {
      var row = { _i: i, score: score[k] / totalW };
      Object.keys(pcts).forEach(function (f) { row["rank_pct_" + f] = pcts[f][k]; });
      return row;
    });
    rows.sort(function (a, b) {
      if (a.score !== b.score) return b.score - a.score;
      var ma = num(mc[a._i]), mb = num(mc[b._i]);
      if (ma !== mb) {
        if (ma === null) return 1;
        if (mb === null) return -1;
        return mb - ma;
      }
      return sym[a._i] < sym[b._i] ? -1 : sym[a._i] > sym[b._i] ? 1 : 0;
    });
    rows.forEach(function (r, k) { r.rank = k + 1; });
    return rows;
  }

  return { setSchema: setSchema, validate: validate, runScreen: runScreen, rank: rank,
           describe: describe, fmtValue: fmtValue, pyG: pyG, pyFixed: pyFixed };
});
