# equity-scout

Write an investment observation in plain English, for example *"profitable mid-caps that have pulled back 20%
from their highs but are still growing revenue over 10%"*. A language model translates it into a typed,
whitelisted screen spec. Code validates the spec, screens about 3,800 US-listed operating companies on
point-in-time data, ranks the survivors and computes every number. For the top names, the model reads the latest
earnings release, the 10-Q/10-K MD&A and recent news headlines, then explains why the stock and the fundamentals
might disagree. Code deletes any claim whose quote does not appear verbatim in its source.

![Recorded run A on the demo site](docs/screenshot.png)

## Try it

**In the browser, with nothing installed:** open the demo site
([henryzhangpku.github.io/equity-scout](https://henryzhangpku.github.io/equity-scout/), or `docs/index.html` from disk)
and open **Try your own**.

* The panel loads the full 2026-10-08 feature snapshot for 3,827 companies. That is 5.2 MB raw and about 2.1 MB
  gzipped, fetched only when the panel opens. The screen, funnel and ranking then run in the page.
  `docs/scout-core.js` is a line-by-line port of the Python validator, screen and ranker. A parity test runs the
  recorded specs through both implementations and requires identical funnels, rankings and refusal messages.
* **Spec editor.** Start from any recorded run's spec, or from a blank one. Choose fields, operators and
  thresholds from the whitelist, or edit the JSON. The browser validator applies the same rules as the app and shows
  each refusal.
* **Bring your own key (optional).** Paste a DeepSeek key and the page sends your observation, with the same system
  prompt the app uses, straight to `api.deepseek.com`. DeepSeek's API allows browser CORS; this was checked before
  the feature was built. The key stays in a JavaScript variable, is never stored, and goes nowhere else. The
  proposed spec fills the editor; nothing runs until you press Run.
* **Explanations are not generated in the browser.** SEC documents cannot be fetched from a browser, because EDGAR
  has no CORS. Results are labelled *snapshot as of 2026-10-08 close; explanations need the local app*. When a
  name already has an explanation from a recorded run, that explanation is shown.

![Try your own: spec editor and in-browser screen](docs/screenshot-try.png)

**Locally, for live demos:** `uv run scout serve` opens `http://127.0.0.1:8765/`. Type an observation and the model
proposes a spec. After you confirm, the full pipeline runs on the latest snapshot plus live EDGAR filings and
Alpaca news. The funnel and table appear first. The cited explanations then stream in, one per name, about 40 s
each, with links to the SEC documents.

* Each stage is shown on screen. Each model call times out after 180 s. A failure on one name turns into a *not
  enough evidence* card and the run continues. Any error message points to the fallback.
* **Replay a recorded run** streams a recorded run with no network.
* `scout serve --offline` answers only from recorded material (the LLM cache and saved documents). It is the safe
  mode when the network is unreliable.
* Picks go into the hash-chained ledger only when you click **Record**.
* Keys come from the environment, as for the CLI, and never reach the page.
* `?replay=<run-id>` in the URL starts a replay on page load.

![scout serve replaying run C](docs/screenshot-serve.png)

## The rule: the model proposes, deterministic code decides

| Step | Model | Code |
|---|---|---|
| Translate | fills a JSON spec from the observation | validates every key, field, operator, unit and threshold against a whitelist; refuses anything else with a reason; one correction round, then the run stops |
| Screen | nothing | applies the conditions in order and records, for each step, how many names entered, passed, failed and lacked data |
| Rank | nothing | weighted mean of percentile ranks; ties go to market cap, then ticker |
| Explain | writes claims, each with a quote and a document id | keeps a claim only if the quote is found verbatim in that document (only whitespace, curly quotes and dashes are normalised) and every number in the claim also appears in the quote; with fewer than two surviving thesis claims the verdict is *not enough evidence* |

Anything the schema cannot express (analyst downgrades, guidance, sentiment) goes in `unmapped` and is shown
as **not screened**. It is never silently dropped or approximated. Every prompt and response is stored in
`llm_cache/`, so the recorded runs replay offline with no API key.

## Architecture

```
observation ──LLM──▶ spec (JSON) ──validate──▶ screen ──▶ funnel + ranked table ──▶ top N
                                                  ▲                                    │
             feature snapshot (point-in-time) ────┘          EDGAR 8-K ex.99.1, MD&A, news headlines
   Alpaca bars ─ indicators                                              │
   SEC companyfacts ─ TTM / growth / FCF / EV                       LLM writes claims
   SEC submissions ─ SIC, filing list                                    │
   FINRA short interest                                       citation validator ──▶ report
```

Every data layer sits behind a small interface in `src/scout/data/base.py`, so a licensed source can replace the
free one without touching the screen, the ranking or the validator.

| Layer | This demo (free) | Institutional equivalent | What the free version lacks |
|---|---|---|---|
| Universe + prices | Alpaca assets + daily SIP bars, split and dividend adjusted (`data/alpaca.py`) | Bloomberg BQL / BQuant, LSEG, S&P Capital IQ | survivorship-free history, delisted names, intraday data |
| Fundamentals | SEC XBRL companyfacts, each fact gated by its `filed` date (`data/sec.py`, `fundamentals.py`) | BQL fundamentals, Capital IQ / Compustat point-in-time | IFRS filers, standardised line items, segments, consensus estimates and revisions |
| Classification | SEC SIC codes in named groups, plus a few curated theme baskets defined in code | GICS, BICS, TRBC, vendor theme baskets | real theme membership |
| Short interest | FINRA consolidated short interest, twice monthly (`data/finra.py`) | securities-lending feeds | float-based %, daily data, borrow cost |
| Documents | EDGAR 8-K Exhibit 99.1 and 10-Q / 10-K MD&A (`data/edgar_docs.py`) | document search on the same terminals | earnings-call transcripts (interface kept, `NoTranscripts`) |
| News | Alpaca news API (Benzinga): headline and summary only, cut at the as-of close (`data/news.py`) | Bloomberg / LSEG / Dow Jones news | full articles, broad sources |
| LLM | DeepSeek `deepseek-v4-pro` (Kimi as an alternative) through one OpenAI-compatible client (`llm.py`) | a frontier model inside the firm's controls | nothing structural |

### Point-in-time rules

* A fundamental fact is visible only on or after its `filed` date. When a period is restated, the restated value
  stays hidden until it is filed.
* Quarters are taken as reported or derived from year-to-date facts within a single XBRL concept (Q4 = FY − 9M).
  Cash-flow items are mostly reported year-to-date, so this derivation is what makes TTM free cash flow possible.
* If the latest quarter ended more than 220 days before the as-of date, the fundamentals are left missing. They are
  never carried forward.
* Short interest is visible 8 business days after its settlement date. News is visible only if it was published
  before 16:00 New York time on the as-of date.
* The SEC frames API was evaluated and not used for values. A frame returns the *latest-filed* number for each
  period and has no `filed` date, so a restatement would leak into the past (`data/sec.py` explains this).

## Recorded runs (real data as of 2026-10-08 close)

| Run | Funnel (names left after each step) | Top names |
|---|---|---|
| A: profitable mid-caps, 20%+ below the 52-week high, revenue growth > 10%, FCF positive, back above the 50-day | 3827 → 1902 → 1318 → 756 → 343 → 174 → 131 → **23** | VICR (not enough evidence), SITM, STRL, SANM, KLIC |
| B: AI-infrastructure suppliers lagging the semiconductor index (SOXX) over 3 months with accelerating revenue growth | 3827 → 38 → 20 → **13** | AVGO, AAOI, AMAT, COHR, AMKR |
| C: large caps with RSI < 35 on 1.5x volume, 50-day still above the 200-day, FCF positive, short interest < 5%; "no recent analyst downgrades" refused as unmapped | 3827 → 872 → 86 → 29 → 14 → 3 → **2** | BX, SBUX |

Each run folder in `runs/` holds `run.json` (spec, translation attempts, funnel, every ranked row, explanations,
data manifest with SHA-256 hashes), `report.md`, and `docs/`, which contains the exact document text the model
was shown, so each citation can be checked by hand.

The universe in run B comes from curated baskets (`THEMES` in `spec.py`). SIC codes cannot separate data-center
REITs from other REITs or find neoclouds at all, and with SIC alone the top of the list was micro-caps. The
baskets are a fixed list in code, open to review, and the model can only choose among them.

## Forward tracking

Every live run appends its top names and entry closes to `runs/picks.jsonl`. The file is append-only and
hash-chained: each entry stores the SHA-256 of its own content and the hash of the entry before it, so editing or
deleting a past entry is detected. `scout track` checks the chain and marks every entry to market against SPY and
SMH using fresh Alpaca closes. The site shows the result under the label **"since run date; days of history, not
evidence"**. As of the recording date every entry has 0 trading days of history.

## Data limits

* Only US-GAAP quarterly filers have fundamentals. Foreign private issuers (IFRS, 20-F) and banks with
  non-standard revenue tags show up as *missing* in the funnel. About 1,100 of the 3,827 names have no current
  fundamentals.
* Market cap is the price times the latest cover-page share count. For multi-class issuers the count often covers
  one class only. When it is far below the weighted-average share count, the weighted average is used instead.
  Counts under 100,000 shares, and any market cap implying price/sales below 0.01, are rejected as data errors.
  The name is then *missing*, not mis-sized. Berkshire, for example, drops out of size filters instead of
  appearing as a $0.5B company.
* Prices come from Alpaca's current asset list, so delisted names are absent. That is survivorship bias, harmless
  for a screen as of today but wrong for a backtest.
* Short interest is a percentage of shares outstanding, not float (float is not in free data).
* No consensus estimates, revisions, ownership or borrow data. Those need a licensed source, and the spec
  refuses conditions on them.
* Any change to a prompt or to the schema text changes the request hash and invalidates the recordings. Re-record
  by running the observation again with a key set.

## Run it

```bash
uv sync
# offline: replay a recorded run (no keys, no network)
uv run scout replay runs/b-ai-infra-laggards

# live: needs DEEPSEEK_API_KEY, plus ALPACA_API_KEY / ALPACA_API_SECRET for news
uv run scout run "Profitable mid-caps ... back above the 50-day average." --top 5
uv run scout spec "..."          # translate only; prints the validated spec
uv run scout serve               # local web app (add --offline for recorded material only)
uv run scout track               # mark the pick ledger to market vs SPY and SMH
uv run scout site                # export runs, schema and the browser snapshot to docs/data/

# rebuild the feature snapshot for a new date (Alpaca + SEC + FINRA, about 30 min cold, cached afterwards)
uv run scout build --as-of 2026-10-08
```

`scout run` prints the spec and asks for confirmation before it screens (`--yes` skips the prompt). Keys are read
from the environment, and on Windows also from the per-user environment in the registry. They are never printed or
written to disk. Choose the model provider with `--provider deepseek|kimi`. The Kimi client is wired up but untested end to end:
the key used here belongs to a plan that the Kimi coding endpoint rejected (HTTP 403).

Dependencies: `numpy`, `pandas`, `requests`, plus `pytest` for development. HTML is parsed with the standard
library.

## Tests

`uv run pytest`: 83 tests, none skipped. The browser parity tests need Node.js on the PATH.

* indicators against hand-computed values (SMA, Wilder RSI step by step, EMA/MACD, momentum, volume ratio,
  drawdown, relative strength)
* point-in-time visibility, hidden restatements, YTD-derived quarters, TTM consecutiveness, staleness, share-count
  sanity rules
* schema validation and refusals: unknown fields, operators, industries and themes, percent-vs-decimal mistakes,
  and short-interest conditions when the source is unavailable
* the citation validator rejects paraphrased, invented, case-changed and too-short quotes, and numbers that are not in the quote
* funnel arithmetic on a hand-built universe, including missing data counts
* the pick ledger detects edits and deletions; mark-to-market arithmetic
* news cut at the as-of close, with full article text never used
* browser parity: the JS validator, screen and ranker under Node give the same funnels, rankings and
  refusal messages as Python, on the shipped browser snapshot and against the recorded runs
* `scout serve` endpoints, offline: status, translate from the recorded cache, refusals, a streamed run that
  reproduces run C, record-on-click (one ledger entry, chain intact), replay, path and job guards
* offline replay of all three recorded runs, with the network disabled, reproduces spec, funnel, ranking and
  explanations exactly

Research tool only: it places no orders and makes no recommendations.
