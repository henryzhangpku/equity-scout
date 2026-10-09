(function () {
  "use strict";
  var U = window.ScoutUI, esc = U.esc;
  var STATUS = null, proposed = null, attempts = null, currentJob = null, es = null;
  function $(id) { return document.getElementById(id); }

  var STAGES = [["translate", "1 Translate"], ["confirm", "2 Confirm spec"], ["screening", "3 Screen + rank"],
                ["explain", "4 Read filings + explain"], ["done", "5 Done"]];
  function stages(active, state) {
    $("stages").innerHTML = STAGES.map(function (s) {
      var i = STAGES.findIndex(function (x) { return x[0] === active; });
      var j = STAGES.indexOf(s);
      var cls = j < i ? "ok" : j === i ? (state === "bad" ? "bad" : "on") : "";
      return '<span class="stage ' + cls + '">' + s[1] + "</span>";
    }).join("");
  }
  function status(html, busy) { $("status").innerHTML = (busy ? '<span class="spinner"></span>' : "") + html; }

  function post(url, body, timeoutMs) {
    var ctrl = new AbortController();
    var t = setTimeout(function () { ctrl.abort(); }, timeoutMs || 200000);
    return fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body), signal: ctrl.signal })
      .then(function (r) { return r.json(); })
      .finally(function () { clearTimeout(t); });
  }

  function init() {
    fetch("/api/status").then(function (r) { return r.json(); }).then(function (s) {
      STATUS = s; window.SCOUT_FIELDS = s.fields;
      $("mode").className = "badge " + (s.offline ? "off" : "live");
      $("mode").textContent = s.offline ? "offline: recorded material only" : "live";
      $("meta").innerHTML = "Snapshot as of <strong>" + esc(s.data.last_price_date) + "</strong> close, " + esc(s.data.n_companies) +
        " companies. Model " + esc(s.model) + " (key " + (s.keys.deepseek ? "found" : "<strong>missing</strong>") + "), Alpaca news " +
        (s.keys.alpaca ? "on" : "<strong>off</strong> (keys missing)") + ". Rebuild the snapshot with <code>scout build --as-of YYYY-MM-DD</code>.";
      $("replay-run").innerHTML = s.runs.map(function (r) { return '<option value="' + esc(r.id) + '">' + esc(r.id) + "</option>"; }).join("");
      stages("translate");
      var q = new URLSearchParams(location.search);
      if (q.get("obs")) $("obs").value = q.get("obs");
      if (q.get("replay")) { $("replay-run").value = q.get("replay"); $("replay").click(); }
    }).catch(function () { status('<span class="err">Cannot reach the local server.</span>'); });
  }

  $("propose").onclick = function () {
    var obs = $("obs").value.trim();
    if (!obs) { status("Write an observation first."); return; }
    resetOut(); stages("translate");
    var t0 = Date.now(), tick = setInterval(function () {
      status("Translating with " + esc(STATUS.model) + "… " + Math.round((Date.now() - t0) / 1000) + " s", true);
    }, 500);
    $("propose").disabled = true;
    post("/api/translate", { observation: obs }, 200000).then(function (r) {
      if (r.ok) { showConfirm(r.spec, r.attempts); return; }
      if (r.refused) {
        stages("confirm", "bad");
        status('<span class="err">The model’s spec was refused by the validator:</span><ul>' + r.problems.map(function (p) { return "<li>" + esc(p) + "</li>"; }).join("") +
          "</ul>Rephrase, or replay a recorded run.");
        return;
      }
      fail(r.error, r.hint);
    }).catch(function (e) { fail(e.name === "AbortError" ? "Translation timed out." : e.message); })
      .finally(function () { clearInterval(tick); $("propose").disabled = false; });
  };

  function showConfirm(spec, att) {
    proposed = spec; attempts = att;
    stages("confirm");
    status("Review the spec. Nothing runs until you confirm." + (att && att.length > 1 ? " (The validator refused the first attempt; the model corrected it.)" : ""));
    $("confirm").hidden = false;
    $("spec-view").innerHTML = U.specHtml(spec, "Proposed by the model, validated by code");
    $("spec-json").value = JSON.stringify(spec, null, 2);
    $("refusal").innerHTML = "";
    $("confirm").scrollIntoView({ behavior: "smooth", block: "start" });
  }

  $("cancel").onclick = function () { $("confirm").hidden = true; stages("translate"); status(""); };

  $("run").onclick = function () {
    var spec;
    try { spec = JSON.parse($("spec-json").value); }
    catch (e) { $("refusal").innerHTML = '<p class="err">Not valid JSON: ' + esc(e.message) + "</p>"; return; }
    post("/api/run", { spec: spec, attempts: attempts }, 30000).then(function (r) {
      if (!r.ok) {
        $("refusal").innerHTML = r.refused ? '<div class="refusal panel"><strong>Refused:</strong><ul>' + r.problems.map(function (p) { return "<li>" + esc(p) + "</li>"; }).join("") + "</ul></div>"
          : '<p class="err">' + esc(r.error) + "</p>";
        return;
      }
      $("confirm").hidden = true;
      listen(r.job, spec);
    }).catch(function (e) { fail(e.message); });
  };

  $("replay").onclick = function () {
    resetOut(); $("confirm").hidden = true;
    post("/api/replay", { run: $("replay-run").value }, 30000).then(function (r) {
      if (!r.ok) return fail(r.error);
      listen(r.job, null);
    }).catch(function (e) { fail(e.message); });
  };

  function resetOut() {
    if (es) { es.close(); es = null; }
    $("out").innerHTML = ""; $("record-box").hidden = true; $("record").disabled = false;
    $("record-msg").textContent = "Appends the top names and entry closes to runs/picks.jsonl (hash-chained). Nothing is recorded unless you click.";
  }

  function listen(jobId, spec) {
    currentJob = jobId;
    var specShown = !!spec, lastT = 0, explaining = "";
    $("out").innerHTML = '<div class="panel" id="o-spec"></div><div class="panel" id="o-funnel" hidden></div><div class="panel" id="o-table" hidden></div>' +
      '<div class="panel" id="o-ex" hidden><div class="step">Why the dislocation might exist</div><p class="muted" style="margin-top:0">Each quote is checked by code to appear verbatim in its linked source (8-K earnings release, 10-Q/10-K MD&amp;A, or a news headline/summary). Claims that fail are removed and listed.</p><div class="cards" id="cards"></div></div>';
    if (spec) $("o-spec").innerHTML = U.specHtml(spec, "Spec being run");
    stages("screening");
    status("Screening…", true);
    es = new EventSource("/api/jobs/" + jobId + "/events");
    function on(name, fn) { es.addEventListener(name, function (m) { var e = JSON.parse(m.data); lastT = e.t; fn(e.data); }); }
    on("status", function (d) { status(esc(d.message), true); });
    on("spec", function (d) { if (!specShown) { spec = d; $("o-spec").innerHTML = U.specHtml(d, "Recorded spec (replay)"); } });
    on("screen", function (d) {
      $("o-funnel").hidden = false; $("o-table").hidden = false;
      $("o-funnel").innerHTML = U.funnelHtml(d.funnel, "How the list narrowed (computed by code, snapshot as of " + d.as_of + ")", spec);
      var sp = spec || { conditions: [], rank: [] };
      var cols = d.ranked.length ? U.tableColumns(sp).filter(function (c) { return c in d.ranked[0] || c === "rank"; }) : [];
      $("o-table").innerHTML = U.tableHtml(cols, d.ranked.slice(0, 25), d.top_n, d.ranked.length);
      if (d.top_n && d.ranked.length) {
        $("o-ex").hidden = false;
        $("cards").innerHTML = d.ranked.slice(0, d.top_n).map(function (r) {
          return '<div class="card pending" id="card-' + esc(r.symbol) + '"><div class="hd"><h3>' + esc(r.symbol) + '</h3><span class="badge">waiting</span></div></div>';
        }).join("");
      }
      stages("explain");
    });
    on("explaining", function (d) {
      explaining = d.symbol;
      status("Reading " + esc(d.symbol) + "’s 8-K, MD&amp;A and news, then asking the model (" + d.i + " of " + d.n + ")…", true);
      var c = $("card-" + d.symbol); if (c) c.querySelector(".badge").textContent = "reading filings…";
    });
    on("explanation", function (ex) {
      var c = $("card-" + ex.symbol);
      var html = U.cardHtml(ex);
      if (c) c.outerHTML = html; else $("cards").insertAdjacentHTML("beforeend", html);
    });
    on("heartbeat", function () { if (explaining) status("Still working on " + esc(explaining) + "… " + lastT + " s elapsed", true); });
    on("done", function (d) {
      es.close(); es = null; stages("done");
      status("Done in " + lastT + " s. Saved to " + esc(d.run_dir) + ".");
      $("record-box").hidden = !d.recordable;
    });
    on("error", function (d) { es.close(); es = null; fail(d.message, d.hint); });
    es.onerror = function () { if (es) { es.close(); es = null; fail("Lost the connection to the local server."); } };
  }

  $("record").onclick = function () {
    $("record").disabled = true;
    post("/api/record", { job: currentJob }, 30000).then(function (r) {
      if (!r.ok) { $("record").disabled = false; $("record-msg").innerHTML = '<span class="err">' + esc(r.error) + "</span>"; return; }
      $("record-msg").textContent = "Recorded as ledger entry #" + r.seq + " (" + r.run_id + "), hash " + r.hash.slice(0, 12) + "…";
    });
  };

  function fail(msg, hint) {
    stages("done", "bad");
    status('<span class="err">' + esc(msg || "Something failed.") + "</span> " + esc(hint || "You can replay a recorded run instead."));
  }

  init();
})();
