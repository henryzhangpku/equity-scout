// Runs docs/scout-core.js under Node for the parity tests.
// stdin: {"specs": [...], "validate": [...], "snapshot": "path"}; stdout: results JSON.
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const docs = path.resolve(__dirname, "..", "..", "docs");
const input = JSON.parse(fs.readFileSync(0, "utf8"));
const ctx = { window: {} };
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(docs, "data", "schema.js"), "utf8"), ctx);
if (input.snapshot) vm.runInContext(fs.readFileSync(path.join(docs, "data", input.snapshot), "utf8"), ctx);
const Core = require(path.join(docs, "scout-core.js"));
Core.setSchema(ctx.window.SCOUT_SCHEMA);
const out = { screens: [], validations: [], formats: [] };
for (const s of input.specs || []) {
  const v = Core.validate(s, true);
  if (!v.ok) { out.screens.push({ error: v.problems }); continue; }
  const snap = ctx.window.SCOUT_SNAPSHOT;
  const r = Core.runScreen(snap, v.spec);
  const ranked = Core.rank(snap, r.survivors, v.spec);
  out.screens.push({ funnel: r.funnel,
    ranked: ranked.map(x => ({ symbol: snap.columns.symbol[x._i], score: x.score, rank: x.rank })) });
}
for (const s of input.validate || []) {
  const v = Core.validate(s.spec, s.short_interest_available !== false);
  out.validations.push(v.ok ? { ok: true, spec: v.spec } : { ok: false, problems: v.problems });
}
for (const x of input.format || []) out.formats.push(Core.fmtValue(x[0], x[1]));
process.stdout.write(JSON.stringify(out));
