# Screen: Profitable mid-caps (2–20B) that have pulled back 20%+ from their 52-week high but are still growing revenue over 10% and generating free cash flow, with price back above the 50-day average.

As of **2026-10-08** (last price date 2026-10-08). Universe: tradable US-listed (NYSE/Nasdaq/AMEX/Arca/BATS) operating companies with an SEC CIK and a 10-K/10-Q/20-F/40-F in the last 18 months; close >= $1; 50-day avg dollar volume >= $1,000,000; one listing per CIK. Model: deepseek / deepseek-v4-pro (translation and prose only; every filter, rank and number below is computed by code).

## 1. Screen spec (proposed by the model, validated by code)

```json
{
  "version": 1,
  "observation": "Profitable mid-caps (2\u201320B) that have pulled back 20%+ from their 52-week high but are still growing revenue over 10% and generating free cash flow, with price back above the 50-day average.",
  "universe": {
    "market_cap_min": 2000000000,
    "market_cap_max": 20000000000
  },
  "conditions": [
    {
      "field": "net_income_ttm",
      "op": ">",
      "value": 0,
      "why": "Profitable"
    },
    {
      "field": "drawdown_52w",
      "op": "<=",
      "value": -0.2,
      "why": "pulled back 20%+ from their 52-week high"
    },
    {
      "field": "revenue_growth_yoy",
      "op": ">",
      "value": 0.1,
      "why": "still growing revenue over 10%"
    },
    {
      "field": "fcf_ttm",
      "op": ">",
      "value": 0,
      "why": "generating free cash flow"
    },
    {
      "field": "close",
      "op": ">",
      "ref": "sma50",
      "why": "price back above the 50-day average"
    }
  ],
  "rank": [
    {
      "field": "revenue_growth_yoy",
      "direction": "desc",
      "weight": 1
    }
  ],
  "top_n": 5,
  "unmapped": [],
  "notes": "Interpreted mid-caps as market cap between $2B and $20B, revenue growth as TTM year-over-year revenue growth, and profitable as positive TTM net income. Since no ranking was specified, ranked by revenue growth to surface faster growers."
}
```

## 2. Funnel

| step | in | pass | fail | missing data |
|---|---:|---:|---:|---:|
| universe (liquid US common stocks with SEC filings) | 3827 | 3827 | 0 | 0 |
| market_cap >= $2.00B | 3827 | 1902 | 1712 | 213 |
| market_cap <= $20.00B | 1902 | 1318 | 584 | 0 |
| net_income_ttm > 0 | 1318 | 756 | 209 | 353 |
| drawdown_52w <= -20.0% | 756 | 343 | 409 | 4 |
| revenue_growth_yoy > +10.0% | 343 | 174 | 168 | 1 |
| fcf_ttm > 0 | 174 | 131 | 20 | 23 |
| close > sma50 | 131 | 23 | 108 | 0 |

## 3. Ranked survivors (23)

| rank | symbol | name | score | market_cap | net_income_ttm | drawdown_52w | revenue_growth_yoy | fcf_ttm | close | sma50 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | VICR | VICOR CORP | 1.000 | $11.9B | $137M | -30.9% | +96.1% | $87M | $262.32 | $226.76 |
| 2 | SITM | SITIME Corp | 0.957 | $19.4B | $14M | -28.4% | +83.0% | $84M | $645.06 | $624.37 |
| 3 | STRL | STERLING INFRASTRUCTURE, INC. | 0.913 | $15.9B | $431M | -47.8% | +60.8% | $482M | $518.41 | $517.61 |
| 4 | SANM | SANMINA CORP | 0.870 | $11.3B | $308M | -25.6% | +58.6% | $594M | $210.48 | $204.57 |
| 5 | KLIC | KULICKE & SOFFA INDUSTRIES INC | 0.826 | $4.8B | $116M | -31.9% | +44.4% | $41M | $90.92 | $88.13 |
| 6 | FN | Fabrinet | 0.783 | $17.5B | $473M | -34.7% | +35.7% | $4M | $487.33 | $450.32 |
| 7 | ELF | e.l.f. Beauty, Inc. | 0.739 | $6.3B | $60M | -27.0% | +31.2% | $280M | $105.96 | $98.75 |
| 8 | MOD | MODINE MANUFACTURING CO | 0.696 | $9.7B | $144M | -35.6% | +29.5% | $100M | $181.89 | $176.91 |
| 9 | KVYO | Klaviyo, Inc. | 0.652 | $5.2B | $7M | -47.2% | +28.9% | $253M | $17.57 | $17.50 |
| 10 | HUBS | HUBSPOT INC | 0.609 | $11.6B | $147M | -53.1% | +21.1% | $797M | $231.84 | $230.14 |
| 11 | WK | WORKIVA INC | 0.565 | $4.1B | $47M | -21.0% | +19.7% | $201M | $73.69 | $71.09 |
| 12 | WAY | Waystar Holding Corp. | 0.522 | $5.1B | $135M | -33.2% | +19.2% | $246M | $26.48 | $24.85 |
| 13 | RMBS | RAMBUS INC | 0.478 | $11.7B | $230M | -36.4% | +19.1% | $335M | $108.47 | $95.15 |
| 14 | DIOD | DIODES INC /DEL/ | 0.435 | $4.4B | $86M | -21.6% | +17.8% | $143M | $96.24 | $94.34 |
| 15 | MYRG | MYR GROUP INC. | 0.391 | $4.8B | $165M | -38.0% | +16.1% | $193M | $310.81 | $305.49 |
| 16 | MIR | Mirion Technologies, Inc. | 0.348 | $4.0B | $24M | -45.5% | +15.7% | $134M | $16.22 | $15.50 |
| 17 | OLLI | Ollie's Bargain Outlet Holdings, Inc. | 0.304 | $5.2B | $274M | -34.7% | +14.4% | $223M | $86.71 | $78.28 |
| 18 | BB | BLACKBERRY Ltd | 0.261 | $5.1B | $80M | -32.6% | +14.4% | $92M | $8.63 | $8.39 |
| 19 | BSY | BENTLEY SYSTEMS INC | 0.217 | $10.9B | $290M | -32.9% | +12.8% | $498M | $34.82 | $34.28 |
| 20 | EXTR | EXTREME NETWORKS INC | 0.174 | $3.2B | $42M | -28.3% | +12.6% | $95M | $24.18 | $23.38 |
| 21 | ATEN | A10 Networks, Inc. | 0.130 | $2.0B | $43M | -26.5% | +12.2% | $61M | $27.96 | $26.73 |
| 22 | EPAM | EPAM Systems, Inc. | 0.087 | $5.9B | $402M | -48.6% | +10.8% | $483M | $113.86 | $109.90 |
| 23 | UHS | UNIVERSAL HEALTH SERVICES INC | 0.043 | $10.5B | $1.5B | -27.7% | +10.0% | $845M | $175.72 | $173.59 |

## 4. Why the dislocation might exist (top 5)

Every quote below was checked by code to appear verbatim in the linked SEC document. Claims whose quotes failed the check were removed and are listed.

### VICR: not enough evidence

- source: [VICR 8-K earnings release (Exhibit 99.1), filed 2026-07-21](https://www.sec.gov/Archives/edgar/data/751978/000119312526309538/d115827dex991.htm)
- source: [VICR 10-Q for period 2026-06-30, MD&A, filed 2026-07-29](https://www.sec.gov/Archives/edgar/data/751978/000119312526322462/vicr-20260630.htm)
- source: [Benzinga: Top 3 Industrials Stocks You May Want To Dump In October (2026-10-06)](https://www.benzinga.com/trading-ideas/short-ideas/26/10/62188513/top-3-industrials-stocks-you-may-want-to-dump-in-october)
- source: [Benzinga: Vicor Stock Soars 11% On Another Outlook Hike (2026-10-01)](https://www.benzinga.com/markets/guidance/26/10/62099302/vicor-stock-soars-11-on-another-outlook-hike)
- source: [Benzinga: Needham Maintains Buy on Vicor, Raises Price Target to $350 (2026-10-01)](https://www.benzinga.com/news/26/10/62099280/needham-maintains-buy-vicor-raises-price-target-350)
- source: [Benzinga: Acuity, Accenture and 3 Stocks to Watch Heading Into Thursday (2026-10-01)](https://www.benzinga.com/markets/equities/26/10/62097267/acuity-accenture-and-3-stocks-to-watch-heading-into-thursday)
- source: [Benzinga: Vicor Q3  Revenue expected to be more than $186.358M vs $165.450M Est (2026-09-30)](https://www.benzinga.com/news/26/09/62093653/vicor-q3-revenue-expected-be-more-186-358m-vs-165-450m-est)
- source: [Benzinga: Vicor Raises Q3 Sequential Revenue Growth Guidance To Above 30% From Above 20% On Higher Vertical Power Delivery Royalties (2026-09-30)](https://www.benzinga.com/news/26/09/62092805/vicor-raises-q3-sequential-revenue-growth-guidance-above-30-above-20-higher-vertical-power-delivery-)
- source: [Benzinga: Top 3 Industrials Stocks That May Fall Off A Cliff This Quarter (2026-09-23)](https://www.benzinga.com/trading-ideas/short-ideas/26/09/61944188/top-3-industrials-stocks-that-may-fall-off-a-cliff-this-quarter-2)
- source: [Benzinga: Roth Capital Reiterates Buy on Vicor, Maintains $375 Price Target (2026-09-22)](https://www.benzinga.com/news/26/09/61929528/roth-capital-reiterates-buy-vicor-maintains-375-price-target)
- source: [Benzinga: Needham Reiterates Buy on Vicor, Maintains $320 Price Target (2026-09-22)](https://www.benzinga.com/news/26/09/61915445/needham-reiterates-buy-vicor-maintains-320-price-target)
- source: [Benzinga: Market-Moving News for September 22nd (2026-09-22)](https://www.benzinga.com/trading-ideas/movers/26/09/61915359/market-moving-news-september-22nd)
- source: [Benzinga: AutoZone, Vicor And 3 Stocks To Watch Heading Into Tuesday (2026-09-22)](https://www.benzinga.com/trading-ideas/long-ideas/26/09/61913202/autozone-vicor-and-3-stocks-to-watch-heading-into-tuesday)
- source: [Benzinga: Vicor Stock Rises After Stronger Q3 Guidance (2026-09-21)](https://www.benzinga.com/trading-ideas/movers/26/09/61909562/vicor-stock-rises-after-stronger-q3-guidance)

**Bear case**
- A news report says Vicor shows overbought RSI readings above 70, signaling potential momentum warnings for investors, which may explain near-term downside risk despite positive fundamentals.  
  > "Three industrial stocks—RXO, ACVA and VICR—show overbought RSI readings above 70, signaling potential momentum warnings for investors." ([VICR-news-2026-10-06-62188513](https://www.benzinga.com/trading-ideas/short-ideas/26/10/62188513/top-3-industrials-stocks-you-may-want-to-dump-in-october))
- Gross margin as a percentage of net revenues decreased to 58.0% in the second quarter of 2026 from 65.3% a year ago, indicating margin pressure that could weigh on profitability.  
  > "Gross margin, as a percentage of net revenues and patent litigation settlement, decreased to 58.0% for the second quarter of 2026, compared to 65.3% for the second quarter of 2025." ([VICR-10Q-2026-07-29-mdna](https://www.sec.gov/Archives/edgar/data/751978/000119312526322462/vicr-20260630.htm))

*model said evidence: thin*

### SITM: explained

- source: [SITM 8-K earnings release (Exhibit 99.1), filed 2026-08-05](https://www.sec.gov/Archives/edgar/data/1451809/000145180926000059/sitm-q226x8kxexx991.htm)
- source: [SITM 10-Q for period 2026-06-30, MD&A, filed 2026-08-06](https://www.sec.gov/Archives/edgar/data/1451809/000145180926000060/sitm-20260630.htm)
- source: [Benzinga: If You Invested $1000 In SiTime Stock 5 Years Ago, You Would Have This Much Today (2026-09-28)](https://www.benzinga.com/news/26/09/62037351/if-you-invested-1000-sitime-stock-5-years-ago-you-would-have-much-today)
- source: [Benzinga: Seaport Global Initiates Coverage On SiTime with Neutral Rating (2026-09-23)](https://www.benzinga.com/news/26/09/61940261/seaport-global-initiates-coverage-sitime-neutral-rating)
- source: [Benzinga: Morgan Stanley Initiates Coverage On SiTime with Overweight Rating, Announces Price Target of $730 (2026-09-17)](https://www.benzinga.com/news/26/09/61849157/morgan-stanley-initiates-coverage-sitime-overweight-rating-announces-price-target-730)

**Thesis**
- Revenue increased 127% year over year in the second quarter of 2026, driven by AI and datacenter demand.  
  > "Revenue increased by $87.9 million, or 127%, for the three months ended June 30, 2026 compared to the same period in the prior year primarily driven by demand for our products in the AI and datacenter applications." ([SITM-10Q-2026-08-06-mdna](https://www.sec.gov/Archives/edgar/data/1451809/000145180926000060/sitm-20260630.htm))
- Management highlighted strong revenue growth and a gross margin of 67.1%.  
  > "revenue increasing 127% year over year to $157.4 million and gross margin of 67.1%" ([SITM-8K-2026-08-05-ex99](https://www.sec.gov/Archives/edgar/data/1451809/000145180926000059/sitm-q226x8kxexx991.htm))
- On July 1, SiTime completed the acquisition of Renesas' Timing Business, adding over 550 clocking products.  
  > "On July 1, we completed the acquisition of Renesas' Timing Business, adding over 550 clocking products to our portfolio." ([SITM-8K-2026-08-05-ex99](https://www.sec.gov/Archives/edgar/data/1451809/000145180926000059/sitm-q226x8kxexx991.htm))

**Bear case**
- Acquisition-related costs surged 355% year over year, including $6.5 million of one-time costs for the Renesas deal, weighing on GAAP results.  
  > "Acquisition related costs increased by $6.6 million, or 355%, for the three months ended June 30, 2026, primarily due to one-time costs of $6.5 million incurred towards the acquisition of Renesas' timing business." ([SITM-10Q-2026-08-06-mdna](https://www.sec.gov/Archives/edgar/data/1451809/000145180926000060/sitm-20260630.htm))
- Customer concentration is high, with the top three distributors accounting for approximately 66% of revenue in the latest quarter.  
  > "Our top three customers by revenue, which are distributors, together accounted for approximately 66% of our revenue for the three months ended June 30, 2026 and 2025, and 66% and 64% of our revenues for the six months ended June 30, 2026 and 2025, respectively." ([SITM-10Q-2026-08-06-mdna](https://www.sec.gov/Archives/edgar/data/1451809/000145180926000060/sitm-20260630.htm))
- The Renesas acquisition was partly funded by issuing 3,558,691 shares of common stock, increasing share count and potential dilution.  
  > "Additionally, the Company issued 3,558,691 shares of the Company’s common stock towards this acquisition." ([SITM-10Q-2026-08-06-mdna](https://www.sec.gov/Archives/edgar/data/1451809/000145180926000060/sitm-20260630.htm))

*model said evidence: sufficient*

### STRL: explained

- source: [STRL 8-K earnings release (Exhibit 99.1), filed 2026-08-03](https://www.sec.gov/Archives/edgar/data/874238/000087423826000100/a20260803ex991earningsrele.htm)
- source: [STRL 10-Q for period 2026-06-30, MD&A, filed 2026-08-04](https://www.sec.gov/Archives/edgar/data/874238/000087423826000103/strl-20260630.htm)
- source: [Benzinga: Stifel Maintains Buy on Sterling Infrastructure, Lowers Price Target to $742 (2026-10-08)](https://www.benzinga.com/news/26/10/62254345/stifel-maintains-buy-sterling-infrastructure-lowers-price-target-742)
- source: [Benzinga: Cantor Fitzgerald Reiterates Overweight on Sterling Infrastructure, Maintains $742 Price Target (2026-09-30)](https://www.benzinga.com/news/26/09/62073161/cantor-fitzgerald-reiterates-overweight-sterling-infrastructure-maintains-742-price-target)
- source: [Benzinga: Here's How Much $1000 Invested In Sterling Infrastructure 20 Years Ago Would Be Worth Today (2026-09-28)](https://www.benzinga.com/news/26/09/62023821/here-s-how-much-1000-invested-sterling-infrastructure-20-years-ago-would-be-worth-today)
- source: [Benzinga: Raoul Pal Says There’s ‘Almost No Way’ AI Data Centers Don’t Trigger a Supercycle — 3 Stocks Positioned to Benefit (2026-09-08)](https://www.benzinga.com/markets/tech/26/09/61651775/raoul-pal-says-data-centers-are-only-30-percent-built-and-calls-it-an-inevitable-supercycle)

**Thesis**
- Second quarter revenues increased 90% to $1.17 billion, with acquisitions contributing $250.8 million.  
  > "Revenues of $1.17 billion increased by 90%. Acquisitions(1) contributed $250.8 million of revenue in the quarter." ([STRL-8K-2026-08-03-ex99](https://www.sec.gov/Archives/edgar/data/874238/000087423826000100/a20260803ex991earningsrele.htm))
- Backlog at June 30, 2026 was $4.33 billion, up 116% from the prior year period, and organic backlog increased 50% year-over-year.  
  > "Backlog at June 30, 2026 was $4.33 billion, up 116% from the prior year period. Backlog increased 50% year-over-year on an organic basis." ([STRL-8K-2026-08-03-ex99](https://www.sec.gov/Archives/edgar/data/874238/000087423826000100/a20260803ex991earningsrele.htm))
- Mission-critical projects represented 92% of E-Infrastructure backlog at quarter end, indicating strong demand in data centers and semiconductor facilities.  
  > "Mission-critical projects—including data centers, manufacturing, and semiconductor facilities—represented 92% of E-Infrastructure backlog at quarter end." ([STRL-8K-2026-08-03-ex99](https://www.sec.gov/Archives/edgar/data/874238/000087423826000100/a20260803ex991earningsrele.htm))

**Bear case**
- Building Solutions revenue declined 1% and adjusted operating income decreased 11%, and management expects housing market conditions to remain challenging through 2026.  
  > "In Building Solutions, revenue declined 1%, reflecting relatively flat levels of homebuilder activity, while adjusted operating income decreased 11%. We expect market conditions to remain challenging through 2026 as housing affordability pressures continue to affect prospective homebuyers" ([STRL-8K-2026-08-03-ex99](https://www.sec.gov/Archives/edgar/data/874238/000087423826000100/a20260803ex991earningsrele.htm))
- Transportation Solutions revenue decreased $40.1 million, or 20%, in the second quarter of 2026 compared to the prior year period.  
  > "Revenues were $156.7 million for the second quarter of 2026, a decrease of $40.1 million, or 20%, compared to the second quarter of 2025." ([STRL-10Q-2026-08-04-mdna](https://www.sec.gov/Archives/edgar/data/874238/000087423826000103/strl-20260630.htm))

*model said evidence: sufficient*

### SANM: explained

- source: [SANM 8-K earnings release (Exhibit 99.1), filed 2026-07-27](https://www.sec.gov/Archives/edgar/data/897723/000089772326000036/sanmina_exx991xjune272026.htm)
- source: [SANM 10-Q for period 2026-06-27, MD&A, filed 2026-07-27](https://www.sec.gov/Archives/edgar/data/897723/000089772326000037/sanm-20260627.htm)
- source: [Benzinga: Here’s How Much You Would Have Made Owning Sanmina Stock In The Last 5 Years (2026-10-06)](https://www.benzinga.com/news/26/10/62206336/here-s-how-much-you-would-have-made-owning-sanmina-stock-last-5-years)
- source: [Benzinga: $1000 Invested In Sanmina 20 Years Ago Would Be Worth This Much Today (2026-09-18)](https://www.benzinga.com/news/26/09/61883541/1000-invested-sanmina-20-years-ago-would-be-worth-much-today)
- source: [Benzinga: Here’s How Much You Would Have Made Owning Sanmina Stock In The Last 20 Years (2026-09-15)](https://www.benzinga.com/news/26/09/61794483/here-s-how-much-you-would-have-made-owning-sanmina-stock-last-20-years)

**Thesis**
- The drawdown may reflect investor concern about integration risk from the ZT Systems acquisition, which the company's own filings identify as a key risk.  
  > "the risk that the integration of and expected benefits from the ZT Systems acquisition may not be realized or may take longer to realize than anticipated;" ([SANM-8K-2026-07-27-ex99](https://www.sec.gov/Archives/edgar/data/897723/000089772326000036/sanmina_exx991xjune272026.htm))
- Interest expense surged due to acquisition-related borrowing, which could undermine earnings quality despite revenue growth.  
  > "Interest expense was $32 million and $5 million for the three months ended June 27, 2026 and June 28, 2025, respectively and $89 million and $15 million for the nine months ended June 27, 2026 and June 28, 2025, respectively." ([SANM-10Q-2026-07-27-mdna](https://www.sec.gov/Archives/edgar/data/897723/000089772326000037/sanm-20260627.htm))
- High customer concentration, with one customer representing 10% or more of quarterly sales, may raise concerns about revenue sustainability.  
  > "One customer represented 10% or more of our net sales for the three months ended June 27, 2026 and two customers represented 10% or more of our net sales for the nine months ended June 27, 2026." ([SANM-10Q-2026-07-27-mdna](https://www.sec.gov/Archives/edgar/data/897723/000089772326000037/sanm-20260627.htm))

**Bear case**
- The ZT Systems acquisition entails up to $450 million in contingent cash consideration and a recognized $183 million liability, adding future cash obligations that could pressure valuation.  
  > "The seller is also entitled to up to $450 million in contingent cash consideration upon the achievement of certain gross profit and revenue metrics during the three-year period following the Closing Date. Additionally, we recognized $183 million fair value of contingent cash consideration liability as of June 27, 2026." ([SANM-10Q-2026-07-27-mdna](https://www.sec.gov/Archives/edgar/data/897723/000089772326000037/sanm-20260627.htm))
- The company incurred $21 million in acquisition, integration and other expenses in the quarter, reducing GAAP profitability and indicating ongoing integration costs.  
  > "Acquisition, integration and others were $21 million and $137 million for the three and nine months ended June 27, 2026 respectively, and were related to the ZT Acquisition." ([SANM-10Q-2026-07-27-mdna](https://www.sec.gov/Archives/edgar/data/897723/000089772326000037/sanm-20260627.htm))

*Stripped by the citation check (1):* "Outside the acquired business, CPS gross margin declined to 12.8% from 14.7% due" (quote not found verbatim in the cited document)

*model said evidence: sufficient*

### KLIC: explained

- source: [KLIC 8-K earnings release (Exhibit 99.1), filed 2026-08-05](https://www.sec.gov/Archives/edgar/data/56978/000005697826000030/ex991liveq32026.htm)
- source: [KLIC 10-Q for period 2026-07-04, MD&A, filed 2026-08-06](https://www.sec.gov/Archives/edgar/data/56978/000005697826000032/klic-20260704.htm)
- source: [Benzinga: Kulicke & Soffa Indus Q3 2026 Earnings Call: Complete Transcript (2026-10-05)](https://www.benzinga.com/news/26/10/62156461/kulicke-soffa-indus-q3-2026-earnings-call-complete-transcript)

**Thesis**
- The company reported third quarter net revenue of $330.4 million and net income of $57.4 million, indicating strong recent fundamentals.  
  > "The Company reported third quarter net revenue of $330.4 million, net income of $57.4 million, representing EPS of $1.07 per fully diluted share, and non-GAAP net income of $64.2 million, representing non-GAAP EPS of $1.20 per fully diluted share." ([KLIC-8K-2026-08-05-ex99](https://www.sec.gov/Archives/edgar/data/56978/000005697826000030/ex991liveq32026.htm))
- Management stated that demand conditions continue to improve across all end markets.  
  > "We see strong sequential growth in the third quarter and demand conditions continue to improve across all end markets." ([KLIC-8K-2026-08-05-ex99](https://www.sec.gov/Archives/edgar/data/56978/000005697826000030/ex991liveq32026.htm))
- The company guides fourth quarter net revenue to approximately $375 million with GAAP diluted EPS of approximately $1.29.  
  > "K&S currently expects net revenue in the fourth quarter of fiscal 2026 ending October 3, 2026 to be approximately $375 million +/- $20 million, GAAP diluted EPS to be approximately $1.29 +/- 10%, and non-GAAP diluted EPS to be approximately $1.42 +/- 10%." ([KLIC-8K-2026-08-05-ex99](https://www.sec.gov/Archives/edgar/data/56978/000005697826000030/ex991liveq32026.htm))
- The company anticipates its expanded Advanced Solutions production facility will be completed within the second half of fiscal 2027.  
  > "Kulicke & Soffa anticipates its expanded Advanced Solutions production facility will be completed, as scheduled, within the second half of fiscal 2027." ([KLIC-8K-2026-08-05-ex99](https://www.sec.gov/Archives/edgar/data/56978/000005697826000030/ex991liveq32026.htm))

**Bear case**
- The filings warn of persistent macroeconomic headwinds and falling customer sentiment, potentially explaining price weakness despite strong results.  
  > "the persistent macroeconomic headwinds on our business, actual or potential inflationary pressures, interest rate and risk premium adjustments, falling customer sentiment, or economic recession caused directly or indirectly by geopolitical tensions," ([KLIC-8K-2026-08-05-ex99](https://www.sec.gov/Archives/edgar/data/56978/000005697826000030/ex991liveq32026.htm))
- The filings also warn of failures or delays in completing the cessation of its Electronics Assembly equipment business.  
  > "failures or delays in completing the Company's cessation of its Electronics Assembly equipment business" ([KLIC-8K-2026-08-05-ex99](https://www.sec.gov/Archives/edgar/data/56978/000005697826000030/ex991liveq32026.htm))
- The filings warn that the company's ability to develop, manufacture and gain market acceptance of new products is a risk.  
  > "our ability to develop, manufacture and gain market acceptance of new products" ([KLIC-8K-2026-08-05-ex99](https://www.sec.gov/Archives/edgar/data/56978/000005697826000030/ex991liveq32026.htm))

*model said evidence: sufficient*

## Data limits

- Prices: Alpaca SIP daily bars, split and dividend adjusted; no intraday data used.
- Fundamentals: SEC XBRL companyfacts, US-GAAP filers only. Foreign private issuers (IFRS, 20-F/40-F) and companies without standard tags drop out as 'missing', they are not guessed.
- Market cap uses the latest cover-page share count; for multi-class issuers it can understate.
- Industry groups are SEC SIC codes, a coarse proxy for a theme (no GICS/BICS in free data).
- Short interest: FINRA consolidated short interest (twice monthly, non-commercial use); % is of shares outstanding, not float.
- Earnings-call transcripts are licensed content and were not used; explanations rely on the 8-K earnings release, 10-Q/10-K MD&A, and news headlines and summaries (Alpaca / Benzinga), never full articles.
- No consensus estimates, revisions, ownership or borrow-cost data: those need a licensed source.
