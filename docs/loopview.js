/* "Learning loop" section: rendered from window.SCOUT_LOOP (docs/data/loop.js), which `scout site` writes
 * straight from the recorded ledgers in runs/loop-*. No number on this section is typed by hand.
 */
(function () {
  "use strict";
  var U = window.ScoutUI, esc = U.esc;
  var L = window.SCOUT_LOOP || { runs: [] };
  var box = document.getElementById("loop-body");
  if (!box) return;
  var scripted = L.runs.filter(function (r) { return r.proposer === "scripted"; })[0];
  var llm = L.runs.filter(function (r) { return r.proposer !== "scripted"; })[0];
  if (!scripted) { box.innerHTML = '<p class="muted">No recorded loop run bundled.</p>'; return; }

  function pct(v) { return v === null || v === undefined ? "n/a" : (v >= 0 ? "+" : "") + (v * 100).toFixed(2) + "%"; }
  function n2(v) { return v === null || v === undefined ? "n/a" : v.toFixed(2); }
  function p4(v) { return v === null || v === undefined ? "n/a" : v.toFixed(4); }
  function cap(s) { s = String(s || ""); return s.charAt(0).toUpperCase() + s.slice(1); }
  function bar(r) { return "p < " + String(r.corrected_p); }
  function int(v) { return Number(v).toLocaleString("en-US"); }
  function maxAbsT(r) { return r.steps.reduce(function (m, s) { return s.t === null ? m : Math.max(m, Math.abs(s.t)); }, 0); }
  function allNegative(r) { return r.steps.every(function (s) { return s.excess !== null && s.excess < 0; }); }
  function nRejected(r) { return r.steps.filter(function (s) { return s.decision === "reject"; }).length; }
  function repoLink(r) {
    return '<a href="https://github.com/henryzhangpku/equity-scout/tree/main/runs/' + esc(r.label) + '" target="_blank" rel="noopener">runs/' + esc(r.label) + "</a>";
  }

  function table(r, withBar) {
    var h = ['<div class="tablewrap"><table class="looptable"><thead><tr><th>Step</th><th class="l">Hypothesis</th><th>Events</th>' +
      '<th title="Mean forward return of the signal minus the universe over the same days, after a round-trip cost">Excess after costs</th>' +
      "<th>t</th><th>p</th>" + (withBar ? "<th>Bar</th>" : "") + "<th>Decision</th></tr></thead><tbody>"];
    r.steps.forEach(function (s) {
      h.push("<tr><td>" + s.step + '</td><td class="l hyp">' + esc(cap(s.description)) + "</td><td>" + (s.events === null ? "n/a" : int(s.events)) +
        '</td><td class="' + (s.excess < 0 ? "neg" : "") + '">' + pct(s.excess) + "</td><td>" + n2(s.t) + "</td><td>" + p4(s.p) + "</td>" +
        (withBar ? "<td>" + bar(r) + "</td>" : "") +
        '<td><span class="verdict ' + (s.decision === "reject" ? "thin" : "ok") + '" title="' + esc(s.reason) + '">' + esc(s.decision === "reject" ? "rejected" : s.decision) + "</span></td></tr>");
    });
    h.push("</tbody></table></div>");
    return h.join("");
  }

  var r = scripted, d = r.data, h = [];
  var never = !r.oos_opened.length;

  h.push('<div class="panel"><div class="step">The loop, one step at a time</div><ol class="flow loopflow">' +
    "<li><strong>Propose.</strong> An agent writes the next idea as a typed rule: entry conditions on RSI, MACD and RSI divergence, a long or short side, a holding period. It sees only earlier discovery results.</li>" +
    "<li><strong>Evaluate on a fixed split.</strong> Code tests the rule on the discovery years only. The split was set in code before the first idea ran.</li>" +
    "<li><strong>Correct for the number of tries.</strong> The number of tries is declared up front and every try counts, so each one must clear p &lt; 0.05 divided by that number.</li>" +
    "<li><strong>Record.</strong> The rule, its numbers, the decision and the reason go into a hash-chained ledger. A repeat of a tested rule is refused without touching the data.</li>" +
    "<li><strong>Decide.</strong> Only an idea that clears the bar in discovery gets one look at the sealed later years, and must clear it again there.</li></ol></div>");

  h.push('<div class="facts">' +
    '<div class="fact"><span class="k">Discovery</span><span class="v"><span class="nw">' + esc(d.first) + '</span> to <span class="nw">' + esc(r.discovery_end) + '</span></span><span class="s">signals whose holding period ends by ' + esc(r.discovery_end) + "</span></div>" +
    '<div class="fact"><span class="k">Sealed out-of-sample</span><span class="v">from ' + esc(r.oos_start) + '</span><span class="s">' +
      (never ? "never opened" : "opened for " + r.oos_opened.length + " idea(s)") + "</span></div>" +
    '<div class="fact"><span class="k">Costs</span><span class="v">' + r.cost_bps_per_side + ' bps a side</span><span class="s">' + (2 * r.cost_bps_per_side) + " bps round trip, charged on every event</span></div>" +
    '<div class="fact"><span class="k">Bar for ' + r.K + ' tries</span><span class="v">' + bar(r) + '</span><span class="s">' + esc(r.correction) + ": " + r.alpha + " / " + r.K + ", one-sided</span></div>" +
    "</div>");

  h.push('<div class="panel"><div class="step">The ' + r.steps.length + " scripted hypotheses (discovery results, " + int(d.n_symbols) + " liquid US companies, " + int(d.sessions) + " sessions)</div>" +
    table(r, true) +
    '<p class="meta">Excess is the signal’s mean forward return minus the universe’s over the same days, signed by side, after a round-trip cost. ' +
    "Every row and its reason is in " + repoLink(r) + " (ledger hash chain " + (r.chain_ok ? "intact" : "BROKEN") + ").</p>" +
    (never ? '<p class="sealed"><strong>The sealed out-of-sample period was never opened.</strong> No idea cleared discovery, so the years from ' + esc(r.oos_start) +
      " are still unused, ready for the next idea.</p>" : "") + "</div>");

  var cap1 = "Read it plainly: " + (allNegative(r) ? "every variant lost money after costs, measured against simply holding the universe" : "no variant cleared the bar") +
    ", and no variant has |t| above " + maxAbsT(r).toFixed(2) + ", so the differences between them are within noise. " +
    "Adding MACD made some variants look a little less bad and others a little worse; with numbers this close that is not a lesson, it is chance. " +
    "A loop without the correction and the sealed years could keep slicing until one of these crossed p &lt; 0.05. This one recorded " + nRejected(r) +
    " rejections instead. That is the evaluator doing its job.";
  h.push('<p class="label-note loopcaption">' + cap1 + "</p>");

  if (llm) {
    var allRej = nRejected(llm) === llm.steps.length;
    h.push('<div class="panel"><div class="step">Ideas proposed by the model</div><p style="margin-top:0">A second run let a language model propose its own ' +
      llm.steps.length + " ideas, reading only the discovery results already in its ledger (" + llm.K + " tries, so the bar was " + bar(llm) + "). " +
      (allRej ? "All " + llm.steps.length + " were rejected" : nRejected(llm) + " were rejected") +
      (allNegative(llm) ? ": none had a positive excess after costs in discovery, so the sealed years stayed closed." : ".") + "</p>" +
      '<details><summary>Show the ' + llm.steps.length + ' ideas</summary><div style="margin-top:12px">' + table(llm, false) + "</div>" +
      '<p class="meta">Prompts and responses are cached in the repository; see ' + repoLink(llm) + ".</p></details></div>");
  }
  box.innerHTML = h.join("");
})();
