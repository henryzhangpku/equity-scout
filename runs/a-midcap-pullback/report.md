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
      "why": "have pulled back 20%+ from their 52-week high"
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
      "field": "drawdown_52w",
      "direction": "asc",
      "weight": 1
    }
  ],
  "top_n": 5,
  "unmapped": [],
  "notes": "Interpreted 'profitable' as positive TTM net income, 'generating free cash flow' as positive TTM free cash flow, and 'still growing revenue over 10%' as TTM revenue growth YoY > 10%. Added a rank by drawdown_52w ascending to prioritize stocks with larger pullbacks, as the observation emphasizes the pullback magnitude; no explicit ranking was specified."
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
| 1 | HUBS | HUBSPOT INC | 1.000 | $11.6B | $147M | -53.1% | +21.1% | $797M | $231.84 | $230.14 |
| 2 | EPAM | EPAM Systems, Inc. | 0.957 | $5.9B | $402M | -48.6% | +10.8% | $483M | $113.86 | $109.90 |
| 3 | STRL | STERLING INFRASTRUCTURE, INC. | 0.913 | $15.9B | $431M | -47.8% | +60.8% | $482M | $518.41 | $517.61 |
| 4 | KVYO | Klaviyo, Inc. | 0.870 | $5.2B | $7M | -47.2% | +28.9% | $253M | $17.57 | $17.50 |
| 5 | MIR | Mirion Technologies, Inc. | 0.826 | $4.0B | $24M | -45.5% | +15.7% | $134M | $16.22 | $15.50 |
| 6 | MYRG | MYR GROUP INC. | 0.783 | $4.8B | $165M | -38.0% | +16.1% | $193M | $310.81 | $305.49 |
| 7 | RMBS | RAMBUS INC | 0.739 | $11.7B | $230M | -36.4% | +19.1% | $335M | $108.47 | $95.15 |
| 8 | MOD | MODINE MANUFACTURING CO | 0.696 | $9.7B | $144M | -35.6% | +29.5% | $100M | $181.89 | $176.91 |
| 9 | OLLI | Ollie's Bargain Outlet Holdings, Inc. | 0.652 | $5.2B | $274M | -34.7% | +14.4% | $223M | $86.71 | $78.28 |
| 10 | FN | Fabrinet | 0.609 | $17.5B | $473M | -34.7% | +35.7% | $4M | $487.33 | $450.32 |
| 11 | WAY | Waystar Holding Corp. | 0.565 | $5.1B | $135M | -33.2% | +19.2% | $246M | $26.48 | $24.85 |
| 12 | BSY | BENTLEY SYSTEMS INC | 0.522 | $10.9B | $290M | -32.9% | +12.8% | $498M | $34.82 | $34.28 |
| 13 | BB | BLACKBERRY Ltd | 0.478 | $5.1B | $80M | -32.6% | +14.4% | $92M | $8.63 | $8.39 |
| 14 | KLIC | KULICKE & SOFFA INDUSTRIES INC | 0.435 | $4.8B | $116M | -31.9% | +44.4% | $41M | $90.92 | $88.13 |
| 15 | VICR | VICOR CORP | 0.391 | $11.9B | $137M | -30.9% | +96.1% | $87M | $262.32 | $226.76 |
| 16 | SITM | SITIME Corp | 0.348 | $19.4B | $14M | -28.4% | +83.0% | $84M | $645.06 | $624.37 |
| 17 | EXTR | EXTREME NETWORKS INC | 0.304 | $3.2B | $42M | -28.3% | +12.6% | $95M | $24.18 | $23.38 |
| 18 | UHS | UNIVERSAL HEALTH SERVICES INC | 0.261 | $10.5B | $1.5B | -27.7% | +10.0% | $845M | $175.72 | $173.59 |
| 19 | ELF | e.l.f. Beauty, Inc. | 0.217 | $6.3B | $60M | -27.0% | +31.2% | $280M | $105.96 | $98.75 |
| 20 | ATEN | A10 Networks, Inc. | 0.174 | $2.0B | $43M | -26.5% | +12.2% | $61M | $27.96 | $26.73 |
| 21 | SANM | SANMINA CORP | 0.130 | $11.3B | $308M | -25.6% | +58.6% | $594M | $210.48 | $204.57 |
| 22 | DIOD | DIODES INC /DEL/ | 0.087 | $4.4B | $86M | -21.6% | +17.8% | $143M | $96.24 | $94.34 |
| 23 | WK | WORKIVA INC | 0.043 | $4.1B | $47M | -21.0% | +19.7% | $201M | $73.69 | $71.09 |

## 4. Why the dislocation might exist (top 5)

Every quote below was checked by code to appear verbatim in the linked SEC document. Claims whose quotes failed the check were removed and are listed.

### HUBS: explained

- source: [HUBS 8-K earnings release (Exhibit 99.1), filed 2026-10-06](https://www.sec.gov/Archives/edgar/data/1404655/000119312526414965/d183135dex991.htm)
- source: [HUBS 10-Q for period 2026-06-30, MD&A, filed 2026-08-05](https://www.sec.gov/Archives/edgar/data/1404655/000119312526335232/hubs-20260630.htm)
- source: [Benzinga: Cantor Fitzgerald Reiterates Neutral on HubSpot, Maintains $200 Price Target (2026-10-07)](https://www.benzinga.com/news/26/10/62212467/cantor-fitzgerald-reiterates-neutral-hubspot-maintains-200-price-target)
- source: [Benzinga: HubSpot Stock Dips: What's Going On? (2026-10-06)](https://www.benzinga.com/trading-ideas/movers/26/10/62196552/hubspot-stock-dips-whats-going-on)
- source: [Benzinga: HubSpot Affirms Q3 Adj EPS Guidance of $3.25-$3.27 vs $3.27 Est; Affirms Q3 Sales Guidance of $924.000M-$925.000M vs $924.613M Est (2026-10-06)](https://www.benzinga.com/news/26/10/62189518/hubspot-affirms-q3-adj-eps-guidance-3-25-3-27-vs-3-27-est-affirms-q3-sales-guidance-924-000m-925-000)
- source: [Benzinga: This HubSpot Analyst Is No Longer Bullish; Here Are Top 5 Downgrades For Monday (2026-10-05)](https://www.benzinga.com/analyst-stock-ratings/downgrades/26/10/62160307/this-hubspot-analyst-is-no-longer-bullish-here-are-top-5-downgrades-for-monday-2)
- source: [Benzinga: Raymond James Downgrades HubSpot to Market Perform (2026-10-05)](https://www.benzinga.com/news/26/10/62156003/raymond-james-downgrades-hubspot-market-perform)
- source: [Benzinga: What's Going On With HubSpot Stock Monday? (2026-09-28)](https://www.benzinga.com/trading-ideas/movers/26/09/62030536/whats-going-on-with-hubspot-stock-monday)
- source: [Benzinga: BMO Capital Maintains Market Perform on HubSpot, Raises Price Target to $250 (2026-09-21)](https://www.benzinga.com/news/26/09/61904913/bmo-capital-maintains-market-perform-hubspot-raises-price-target-250)
- source: [Benzinga: Truist Securities Maintains Buy on HubSpot, Raises Price Target to $275 (2026-09-21)](https://www.benzinga.com/news/26/09/61893581/truist-securities-maintains-buy-hubspot-raises-price-target-275)
- source: [Benzinga: Stephens & Co. Maintains Equal-Weight on HubSpot, Raises Price Target to $255 (2026-09-21)](https://www.benzinga.com/news/26/09/61892684/stephens-co-maintains-equal-weight-hubspot-raises-price-target-255)
- source: [Benzinga: TD Cowen Maintains Hold on HubSpot, Lowers Price Target to $260 (2026-09-18)](https://www.benzinga.com/news/26/09/61871632/td-cowen-maintains-hold-hubspot-lowers-price-target-260)
- source: [Benzinga: UBS Maintains Buy on HubSpot, Raises Price Target to $290 (2026-09-18)](https://www.benzinga.com/news/26/09/61868485/ubs-maintains-buy-hubspot-raises-price-target-290)
- source: [Benzinga: RBC Capital Reiterates Outperform on HubSpot, Maintains $300 Price Target (2026-09-18)](https://www.benzinga.com/news/26/09/61868429/rbc-capital-reiterates-outperform-hubspot-maintains-300-price-target)

**Thesis**
- The company said it had decided to reduce its workforce by ~7%, which may have contributed to the stock's drawdown despite positive profitability.  
  > "decided to reduce the size of our team by ~7% and will be saying goodbye to nearly 660 HubSpotters." ([HUBS-8K-2026-10-06-ex99](https://www.sec.gov/Archives/edgar/data/1404655/000119312526414965/d183135dex991.htm))
- The company stated that over the past year it shifted its strategy to delivering outcomes with AI, which could raise uncertainty about the transition.  
  > "Over the past year, we have shifted our strategy from building software that helps customers grow to delivering outcomes for them with AI." ([HUBS-8K-2026-10-06-ex99](https://www.sec.gov/Archives/edgar/data/1404655/000119312526414965/d183135dex991.htm))
- A news report says Raymond James downgraded HubSpot to Market Perform, a possible sign of waning analyst sentiment.  
  > "Raymond James Downgrades HubSpot to Market Perform" ([HUBS-news-2026-10-05-62156003](https://www.benzinga.com/news/26/10/62156003/raymond-james-downgrades-hubspot-market-perform))
- A news report says Cantor Fitzgerald reiterated a Neutral rating and a $200 price target, which may reflect muted expectations.  
  > "Cantor Fitzgerald Reiterates Neutral on HubSpot, Maintains $200 Price Target" ([HUBS-news-2026-10-07-62212467](https://www.benzinga.com/news/26/10/62212467/cantor-fitzgerald-reiterates-neutral-hubspot-maintains-200-price-target))

**Bear case**
- Customer growth in the quarter was driven primarily by lower-priced Starter products, which could pressure average revenue per customer.  
  > "The growth in Customers was primarily driven by increased demand for our lower-priced Starter products." ([HUBS-10Q-2026-08-05-mdna](https://www.sec.gov/Archives/edgar/data/1404655/000119312526335232/hubs-20260630.htm))
- Management expects gross margins to decline slightly over time as it makes AI-related investments.  
  > "As a result of these investments, over time, we expect gross margins to decline slightly." ([HUBS-10Q-2026-08-05-mdna](https://www.sec.gov/Archives/edgar/data/1404655/000119312526335232/hubs-20260630.htm))
- The company expects subscription and professional services costs to increase in absolute dollars as it scales AI capabilities, which may weigh on margins.  
  > "We expect that the cost of subscription and professional services and other revenue will increase in absolute dollars as we continue to invest in our infrastructure and capitalize software development costs for new offerings to grow our business and scale with AI capabilities." ([HUBS-10Q-2026-08-05-mdna](https://www.sec.gov/Archives/edgar/data/1404655/000119312526335232/hubs-20260630.htm))

*model said evidence: sufficient*

### EPAM: explained

- source: [EPAM 8-K earnings release (Exhibit 99.1), filed 2026-08-06](https://www.sec.gov/Archives/edgar/data/1352010/000135201026000043/exhibit99_q2x2026.htm)
- source: [EPAM 10-Q for period 2026-06-30, MD&A, filed 2026-08-06](https://www.sec.gov/Archives/edgar/data/1352010/000135201026000046/epam-20260630.htm)

**Thesis**
- Full-year revenue growth guidance of 3.2% to 4.2% may explain the stock's steep drawdown despite positive trailing earnings, because it signals a deceleration from the growth threshold that triggered the screen.  
  > "For the full year, EPAM now expects the year-over-year revenue growth rate to be in the range of 3.2% to 4.2%" ([EPAM-8K-2026-08-06-ex99](https://www.sec.gov/Archives/edgar/data/1352010/000135201026000043/exhibit99_q2x2026.htm))
- Operating cash flow turned negative in the first six months of 2026, a reversal from the prior-year cash inflow, which could undermine confidence in free cash flow generation.  
  > "Cash used in operating activities was $38.8 million for the first six months of 2026, compared to cash provided by operating activities of $77.4 million for the first six months of 2025;" ([EPAM-8K-2026-08-06-ex99](https://www.sec.gov/Archives/edgar/data/1352010/000135201026000043/exhibit99_q2x2026.htm))
- The company's cash, cash equivalents and restricted cash decreased 39.0% to $794.3 million as of June 30, 2026.  
  > "Cash, cash equivalents and restricted cash totaled $794.3 million as of June 30, 2026, a decrease of $507.1 million, or 39.0%, from $1.301 billion as of December 31, 2025;" ([EPAM-8K-2026-08-06-ex99](https://www.sec.gov/Archives/edgar/data/1352010/000135201026000043/exhibit99_q2x2026.htm))
- The ongoing war in Ukraine is identified as a material adverse risk to operations.  
  > "Russia’s attack on Ukraine has had, and could continue to have, a material adverse effect on our operations." ([EPAM-10Q-2026-08-06-mdna](https://www.sec.gov/Archives/edgar/data/1352010/000135201026000046/epam-20260630.htm))

**Bear case**
- Full-year revenue growth guidance of only 3.2% to 4.2% and organic constant currency growth of 2.0% to 3.0% suggest a sharp slowdown.  
  > "For the full year, EPAM now expects the year-over-year revenue growth rate to be in the range of 3.2% to 4.2% and now expects the year-over-year revenue growth rate on an organic constant currency basis to be in the range of 2.0% to 3.0%" ([EPAM-8K-2026-08-06-ex99](https://www.sec.gov/Archives/edgar/data/1352010/000135201026000043/exhibit99_q2x2026.htm))
- Operating cash flow was a use of $38.8 million in the first six months of 2026, a deterioration from the $77.4 million provided in the same period a year earlier.  
  > "Cash used in operating activities was $38.8 million for the first six months of 2026, compared to cash provided by operating activities of $77.4 million for the first six months of 2025;" ([EPAM-8K-2026-08-06-ex99](https://www.sec.gov/Archives/edgar/data/1352010/000135201026000043/exhibit99_q2x2026.htm))

*Stripped by the citation check (1):* "Revenues in Software & Hi-Tech declined 10.8% and 6.6% for the three and six mon" (quote not found verbatim in the cited document)

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

### KVYO: explained

- source: [KVYO 8-K earnings release (Exhibit 99.1), filed 2026-08-05](https://www.sec.gov/Archives/edgar/data/1835830/000183583026000039/confidentialfiscalq22026ea.htm)
- source: [KVYO 10-Q for period 2026-06-30, MD&A, filed 2026-08-05](https://www.sec.gov/Archives/edgar/data/1835830/000183583026000040/kvyo-20260630.htm)
- source: [Benzinga: Klaviyo Q2 2026 Earnings Call: Complete Transcript (2026-09-18)](https://www.benzinga.com/news/26/09/61860625/klaviyo-q2-2026-earnings-call-complete-transcript)

**Thesis**
- Klaviyo reported second quarter revenue of $370.6 million, representing 26% year-over-year growth, indicating fundamental strength despite the stock's selloff.  
  > "Second quarter revenue of $370.6 million, representing 26% year-over-year growth" ([KVYO-8K-2026-08-05-ex99](https://www.sec.gov/Archives/edgar/data/1835830/000183583026000039/confidentialfiscalq22026ea.htm))
- The company raised full-year revenue guidance to $1.526 billion to $1.534 billion, for year-over-year growth of 24%, reflecting management confidence.  
  > "Raises FY26 revenue guidance to $1.526 billion to $1.534 billion, for year-over-year growth of 24%" ([KVYO-8K-2026-08-05-ex99](https://www.sec.gov/Archives/edgar/data/1835830/000183583026000039/confidentialfiscalq22026ea.htm))
- As of June 30, 2026, Klaviyo had 4,477 customers generating over $50,000 of ARR, representing growth of 36% year-over-year.  
  > "As of June 30, 2026, we had 4,477 customers generating over $50,000 of ARR, compared to 3,291 customers generating over $50,000 of ARR as of June 30, 2025, representing growth of 36% year-over-year." ([KVYO-10Q-2026-08-05-mdna](https://www.sec.gov/Archives/edgar/data/1835830/000183583026000040/kvyo-20260630.htm))

**Bear case**
- Cost of revenue increased by 42.4% year-over-year to $101.5 million, outpacing revenue growth and pressuring margins.  
  > "Cost of revenue for the three months ended June 30, 2026 increased by $30.2 million or 42.4%, to $101.5 million compared to $71.2 million for the three months ended June 30, 2025." ([KVYO-10Q-2026-08-05-mdna](https://www.sec.gov/Archives/edgar/data/1835830/000183583026000040/kvyo-20260630.htm))
- The company expects gross margin to decline modestly as text messaging and WhatsApp usage increases due to higher associated communication sending costs.  
  > "Our text messaging and WhatsApp messaging offerings have higher associated communication sending costs, and as the number of text messages and WhatsApp messages sent by our customers increases, we expect our gross margin to decline modestly." ([KVYO-10Q-2026-08-05-mdna](https://www.sec.gov/Archives/edgar/data/1835830/000183583026000040/kvyo-20260630.htm))

*Stripped by the citation check (1):* "The guidance table shows year-over-year growth rates of 21.5% to 22.5% for Q3 an" (claim states numbers not in its quote: ['26', '3'])

*model said evidence: sufficient*

### MIR: not enough evidence

- source: [MIR 8-K earnings release (Exhibit 99.1), filed 2026-07-28](https://www.sec.gov/Archives/edgar/data/1809987/000162828026050171/a2026-07x28exhibit991.htm)
- source: [MIR 10-Q for period 2026-06-30, MD&A, filed 2026-07-29](https://www.sec.gov/Archives/edgar/data/1809987/000162828026050604/mir-20260630.htm)

**Thesis**
- Orders excluding acquisitions grew 10% to $229 million, while including acquisitions orders grew 40% to $291 million, reflecting robust demand.  
  > "Second quarter orders, excluding Paragon & Certrec acquisitions, were $229 million, a 10% increase from $208 million in the same period last year. Including Paragon and Certrec acquisitions, second quarter orders were $291 million, a 40% increase compared to the same period last year." ([MIR-8K-2026-07-28-ex99](https://www.sec.gov/Archives/edgar/data/1809987/000162828026050171/a2026-07x28exhibit991.htm))

**Bear case**
- GAAP net income fell 4.7% to $8.1 million in the second quarter, showing earnings did not keep pace with revenue growth.  
  > "GAAP net income was $8.1 million in the second quarter, a 4.7% decrease compared to GAAP net income of $8.5 million in the same period in 2025" ([MIR-8K-2026-07-28-ex99](https://www.sec.gov/Archives/edgar/data/1809987/000162828026050171/a2026-07x28exhibit991.htm))
- Medical segment revenues decreased due to a $9.5 million volume decline driven by tariff regime impacts in Asia-Pacific and lower dosimetry product sales.  
  > "Medical segment revenues decreased for the three months ended June 30, 2026 compared with the three months ended June 30, 2025 primarily due to a decline in volume of $9.5 million, specifically driven by a decline within Asia-Pacific countries due to the introduced tariff regime in prior years paired with a decline in dosimetry product sales," ([MIR-10Q-2026-07-29-mdna](https://www.sec.gov/Archives/edgar/data/1809987/000162828026050604/mir-20260630.htm))
- Selling, general and administrative expenses surged $22.5 million to $105.1 million, compressing profitability.  
  > "Selling, general and administrative (“SG&A”) expenses were $105.1 million for the three months ended June 30, 2026 and $82.6 million for the three months ended June 30, 2025, resulting in an increase of $22.5 million period over period." ([MIR-10Q-2026-07-29-mdna](https://www.sec.gov/Archives/edgar/data/1809987/000162828026050604/mir-20260630.htm))

*Stripped by the citation check (2):* "The company reported second quarter 2026 revenue growth of 19.7% to $266.8 milli" (claim states numbers not in its quote: ['2026']); "The company reaffirmed 2026 revenue growth guidance of approximately 22.0% – 24." (claim states numbers not in its quote: ['2026'])

*model said evidence: sufficient*

## Data limits

- Prices: Alpaca SIP daily bars, split and dividend adjusted; no intraday data used.
- Fundamentals: SEC XBRL companyfacts, US-GAAP filers only. Foreign private issuers (IFRS, 20-F/40-F) and companies without standard tags drop out as 'missing', they are not guessed.
- Market cap uses the latest cover-page share count; for multi-class issuers it can understate.
- Industry groups are SEC SIC codes, a coarse proxy for a theme (no GICS/BICS in free data).
- Short interest: FINRA consolidated short interest (twice monthly, non-commercial use); % is of shares outstanding, not float.
- Earnings-call transcripts are licensed content and were not used; explanations rely on the 8-K earnings release, 10-Q/10-K MD&A, and news headlines and summaries (Alpaca / Benzinga), never full articles.
- No consensus estimates, revisions, ownership or borrow-cost data: those need a licensed source.
