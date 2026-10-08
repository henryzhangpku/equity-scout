# Screen: Large caps above $10B being sold hard: RSI(14) below 35 on volume at least 1.5x the 50-day average, yet still in a long-term uptrend with the 50-day above the 200-day, positive free cash flow, short interest under 5% of shares, and no recent analyst downgrades. Most oversold first.

As of **2026-10-08** (last price date 2026-10-08). Universe: tradable US-listed (NYSE/Nasdaq/AMEX/Arca/BATS) operating companies with an SEC CIK and a 10-K/10-Q/20-F/40-F in the last 18 months; close >= $1; 50-day avg dollar volume >= $1,000,000; one listing per CIK. Model: deepseek / deepseek-v4-pro (translation and prose only; every filter, rank and number below is computed by code).

## 1. Screen spec (proposed by the model, validated by code)

```json
{
  "version": 1,
  "observation": "Large caps above $10B being sold hard: RSI(14) below 35 on volume at least 1.5x the 50-day average, yet still in a long-term uptrend with the 50-day above the 200-day, positive free cash flow, short interest under 5% of shares, and no recent analyst downgrades. Most oversold first.",
  "universe": {
    "market_cap_min": 10000000000
  },
  "conditions": [
    {
      "field": "rsi14",
      "op": "<",
      "value": 35,
      "why": "RSI(14) below 35"
    },
    {
      "field": "volume_ratio_50d",
      "op": ">=",
      "value": 1.5,
      "why": "volume at least 1.5x the 50-day average"
    },
    {
      "field": "sma50_above_sma200",
      "op": "==",
      "value": true,
      "why": "still in a long-term uptrend with the 50-day above the 200-day"
    },
    {
      "field": "fcf_ttm",
      "op": ">",
      "value": 0,
      "why": "positive free cash flow"
    },
    {
      "field": "short_pct_shares_out",
      "op": "<",
      "value": 0.05,
      "why": "short interest under 5% of shares"
    }
  ],
  "rank": [
    {
      "field": "rsi14",
      "direction": "asc",
      "weight": 1
    }
  ],
  "top_n": 5,
  "unmapped": [
    {
      "text": "no recent analyst downgrades",
      "reason": "No field is available for analyst ratings, revisions, or downgrades."
    }
  ],
  "notes": "Large caps are interpreted as market capitalization above $10 billion. The analyst downgrade requirement cannot be measured by the available fields and is listed as unmapped."
}
```

**Not screened: outside the schema**

- "no recent analyst downgrades": No field is available for analyst ratings, revisions, or downgrades.

## 2. Funnel

| step | in | pass | fail | missing data |
|---|---:|---:|---:|---:|
| universe (liquid US common stocks with SEC filings) | 3827 | 3827 | 0 | 0 |
| market_cap >= $10.00B | 3827 | 872 | 2742 | 213 |
| rsi14 < 35 | 872 | 86 | 786 | 0 |
| volume_ratio_50d >= 1.5 | 86 | 29 | 57 | 0 |
| sma50_above_sma200 == true | 29 | 14 | 15 | 0 |
| fcf_ttm > 0 | 14 | 3 | 0 | 11 |
| short_pct_shares_out < +5.0% | 3 | 2 | 1 | 0 |

## 3. Ranked survivors (2)

| rank | symbol | name | score | market_cap | rsi14 | volume_ratio_50d | sma50_above_sma200 | fcf_ttm | short_pct_shares_out |
|---|---|---|---|---|---|---|---|---|---|
| 1 | BX | Blackstone Inc. | 1.000 | $84.6B | 31.26 | 1.53 | yes | $5.5B | +2.6% |
| 2 | SBUX | STARBUCKS CORP | 0.500 | $106.3B | 34.44 | 4.24 | yes | $3.6B | +3.5% |

## 4. Why the dislocation might exist (top 5)

Every quote below was checked by code to appear verbatim in the linked SEC document. Claims whose quotes failed the check were removed and are listed.

### BX: explained

- source: [BX 8-K earnings release (Exhibit 99.1), filed 2026-07-23](https://www.sec.gov/Archives/edgar/data/1393818/000119312526313250/d153439dex991.htm)
- source: [BX 10-Q for period 2026-06-30, MD&A, filed 2026-08-07](https://www.sec.gov/Archives/edgar/data/1393818/000119312526340208/d158269d10q.htm)
- source: [Benzinga: Barclays Maintains Equal-Weight on Blackstone, Lowers Price Target to $124 (2026-10-08)](https://www.benzinga.com/news/26/10/62250415/barclays-maintains-equal-weight-blackstone-lowers-price-target-124)
- source: [Benzinga: 'Oracle, Broadcom and SpaceX Seek Blockbuster Debt Deals To Pay for AI Chips'- WSJ Exclusive (2026-10-07)](https://www.benzinga.com/news/26/10/62234456/oracle-broadcom-and-spacex-seek-blockbuster-debt-deals-to-pay-for-ai-chips-wsj-exclusive)
- source: [Benzinga: 'Waymo Boosts Private Debt Deal to $5 Billion in Push for Growth' - Bloomberg (2026-10-06)](https://www.benzinga.com/news/26/10/62203335/waymo-boosts-private-debt-deal-5-billion-push-growth-bloomberg)
- source: [Benzinga: KKR Private Credit Fund Edges Past Redemption Limit (2026-10-06)](https://www.benzinga.com/markets/private-markets/26/10/62202325/kkr-private-credit-fund-edges-past-redemption-limit)
- source: [Benzinga: Blue Owl Investors Seek to Pull 39% From $5B Tech Credit Fund (2026-10-02)](https://www.benzinga.com/markets/private-markets/26/10/62146487/blue-owl-investors-seek-to-pull-39-from-5b-tech-credit-fund)
- source: [Benzinga: Here’s How Much You Would Have Made Owning Blackstone Stock In The Last 10 Years (2026-10-02)](https://www.benzinga.com/news/26/10/62138835/here-s-how-much-you-would-have-made-owning-blackstone-stock-last-10-years)
- source: [Benzinga: Blackstone Pours $1 Billion Into New Defense Tech Firm (2026-10-02)](https://www.benzinga.com/m-a/26/10/62138407/blackstone-pours-1-billion-into-new-defense-tech-firm)
- source: [Benzinga: 'KKR, Blackstone Are Among Suitors for Windshield Repairer Cary' - Bloomberg (2026-10-02)](https://www.benzinga.com/news/26/10/62134848/kkr-blackstone-are-among-suitors-windshield-repairer-cary-bloomberg)
- source: [Benzinga: Wells Fargo Initiates Coverage On Blackstone with Equal-Weight Rating, Announces Price Target of $122 (2026-10-02)](https://www.benzinga.com/news/26/10/62131557/wells-fargo-initiates-coverage-blackstone-equal-weight-rating-announces-price-target-122)
- source: [Benzinga: Blackstone Launches Defense Tech Platform Falcata Through TSC, Applied Systems Engineering Combination (2026-10-01)](https://www.benzinga.com/news/26/10/62105131/blackstone-launches-defense-tech-platform-falcata-through-tsc-applied-systems-engineering-combinatio)
- source: [Benzinga: Goldman’s $18B Private Credit Fund Bucks Redemption Wave — Again (2026-09-30)](https://www.benzinga.com/markets/private-markets/26/09/62092249/goldman-private-credit-fund-bucks-redemption-wave-again)
- source: [Benzinga: Blackstone To Debut Nordic Logistics Platform Of 200 Warehouses, Offering Investors More Direct Route Into High-Growth Sector (2026-09-29)](https://www.benzinga.com/news/26/09/62041393/blackstone-debut-nordic-logistics-platform-200-warehouses-offering-investors-more-direct-route-high-)

**Thesis**
- Blackstone's own earnings release reports an outstanding second quarter with strong earnings growth and nearly $70 billion of inflows, which conflicts with the stock's oversold technical signals.  
  > "Blackstone delivered an outstanding second quarter, highlighted by strong growth in earnings and nearly $70 billion of inflows." ([BX-8K-2026-07-23-ex99](https://www.sec.gov/Archives/edgar/data/1393818/000119312526313250/d153439dex991.htm))
- The MD&A states that U.S. capital markets activity expanded considerably, which would normally support fee-related earnings and contradicts the price decline.  
  > "U.S. capital markets activity levels expanded considerably following an active first quarter." ([BX-10Q-2026-08-07-mdna](https://www.sec.gov/Archives/edgar/data/1393818/000119312526340208/d158269d10q.htm))
- A news report says Barclays maintained an Equal-Weight rating and lowered its price target to $124, which may have contributed to selling pressure despite strong fundamentals.  
  > "Barclays Maintains Equal-Weight on Blackstone, Lowers Price Target to $124" ([BX-news-2026-10-08-62250415](https://www.benzinga.com/news/26/10/62250415/barclays-maintains-equal-weight-blackstone-lowers-price-target-124))

**Bear case**
- The company's MD&A notes that the ten-year Treasury yield has risen to 4.72% as of July 31, 2026, which could pressure valuations for rate-sensitive alternative asset managers.  
  > "The ten-year U.S. Treasury yield increased 15 basis points in the second quarter of 2026 to 4.47% and has since risen to 4.72% as of July 31, 2026." ([BX-10Q-2026-08-07-mdna](https://www.sec.gov/Archives/edgar/data/1393818/000119312526340208/d158269d10q.htm))
- A news report says Blue Owl investors sought to pull 39% from a tech credit fund, signaling redemption pressures in private credit that could spill over to investor sentiment on Blackstone's credit business.  
  > "Blue Owl Investors Seek to Pull 39% From $5B Tech Credit Fund" ([BX-news-2026-10-02-62146487](https://www.benzinga.com/markets/private-markets/26/10/62146487/blue-owl-investors-seek-to-pull-39-from-5b-tech-credit-fund))

*model said evidence: sufficient*

### SBUX: explained

- source: [SBUX 8-K earnings release (Exhibit 99.1), filed 2026-07-29](https://www.sec.gov/Archives/edgar/data/829224/000082922426000129/sbux-06282026xearningsrele.htm)
- source: [SBUX 10-Q for period 2026-06-28, MD&A, filed 2026-07-29](https://www.sec.gov/Archives/edgar/data/829224/000082922426000130/sbux-20260628.htm)
- source: [Benzinga: Why Is Jersey Mike's Subs Stock Gaining Thursday? (2026-10-08)](https://www.benzinga.com/trading-ideas/movers/26/10/62259027/why-is-jersey-mikes-subs-stock-gaining-thursday)
- source: [Benzinga: UBS Maintains Neutral on Starbucks, Lowers Price Target to $105 (2026-10-08)](https://www.benzinga.com/news/26/10/62257066/ubs-maintains-neutral-starbucks-lowers-price-target-105)
- source: [Benzinga: QUICK SPARK: Chipotle Stock Eyes Best Day Since July on Starbucks' Takeover Interest (2026-10-08)](https://www.benzinga.com/m-a/26/10/62251550/chipotle-stock-best-day-starbucks-takeover-interest)
- source: [Benzinga: Chipotle Stock Jumps: What's Going On? (2026-10-08)](https://www.benzinga.com/trading-ideas/movers/26/10/62250019/chipotle-stock-jumps-whats-going-on)
- source: [Benzinga: 'Starbucks has explored takeover of Chipotle in restaurant megadeal'- Financial Times (2026-10-08)](https://www.benzinga.com/news/26/10/62247653/starbucks-has-explored-takeover-chipotle-restaurant-megadeal-financial-times)
- source: [Benzinga: Starbucks Raises Quarterly Dividend From $0.62 To $0.63/Share (2026-10-07)](https://www.benzinga.com/quote/SBUX)
- source: [Benzinga: 'A Starbucks-Chipotle Tie-up Might Be Crazy Enough To Work; People Close To The Company Tell Semafor That Chipotle Hasn’t Received A Takeover Bid'- Semafor (2026-10-06)](https://www.benzinga.com/news/26/10/62197465/starbucks-chipotle-tie-might-be-crazy-enough-work-people-close-company-tell-semafor-chipotle-hasn-t-)
- source: [Benzinga: 'Starbucks sued over 'sugar-free' claims for protein beverages'- Reuters (2026-10-05)](https://www.benzinga.com/news/26/10/62172156/starbucks-sued-over-sugar-free-claims-protein-beverages-reuters)
- source: [Benzinga: JP Morgan Maintains Overweight on Starbucks, Lowers Price Target to $105 (2026-09-29)](https://www.benzinga.com/news/26/09/62053181/jp-morgan-maintains-overweight-starbucks-lowers-price-target-105)
- source: [Benzinga: Starbucks to Close Select North America Coffeehouses, Cuts Store Outlook (2026-09-25)](https://www.benzinga.com/markets/large-cap/26/09/61997944/starbucks-to-close-select-north-america-coffeehouses-cuts-store-outlook)
- source: [Benzinga: Starbucks Board Approves Further Actions Under 'Back To Starbucks' Strategy; Will Close ~250, Or ~1% Of, Its North America Coffeehouses; Expects $300M Of Restructuring Charges, Including $200M In Cash And $100M Non-Cash Charges For Coffeehouse Asset Disposal And Impairments; Expects FY26 Net New Global Coffeehouse Openings Of ~440; Majority Of Starbucks Coffeehouse Closures Expected By End Of FY26 (2026-09-24)](https://www.benzinga.com/quote/SBUX)
- source: [Benzinga: Seaport Global Initiates Coverage On Starbucks with Neutral Rating (2026-09-16)](https://www.benzinga.com/news/26/09/61809341/seaport-global-initiates-coverage-starbucks-neutral-rating)

**Thesis**
- Starbucks reported a 7.9% increase in global comparable store sales, according to its earnings release.  
  > "Global comparable store sales increased 7.9%, primarily driven by a 4.2% increase in comparable transactions and a 3.5% increase in average ticket" ([SBUX-8K-2026-07-29-ex99](https://www.sec.gov/Archives/edgar/data/829224/000082922426000129/sbux-06282026xearningsrele.htm))
- Starbucks raised its guidance, including expecting fourth quarter U.S. comparable store sales growth of 6.5% or greater.  
  > "Fourth quarter U.S. comparable store sales growth of 6.5% or greater" ([SBUX-8K-2026-07-29-ex99](https://www.sec.gov/Archives/edgar/data/829224/000082922426000129/sbux-06282026xearningsrele.htm))
- A news report says Starbucks has explored a takeover of Chipotle in a restaurant megadeal, which may explain the stock's underperformance despite strong fundamentals.  
  > "Starbucks has explored takeover of Chipotle in restaurant megadeal" ([SBUX-news-2026-10-08-62247653](https://www.benzinga.com/news/26/10/62247653/starbucks-has-explored-takeover-chipotle-restaurant-megadeal-financial-times))

**Bear case**
- A news report says Starbucks has looked into buying Chipotle, which could weigh on the stock due to deal risk.  
  > "Starbucks has looked into buying the company" ([SBUX-news-2026-10-08-62250019](https://www.benzinga.com/trading-ideas/movers/26/10/62250019/chipotle-stock-jumps-whats-going-on))
- Starbucks incurred a $282 million increase in restructuring and impairments, reflecting costs from store closures and organizational changes.  
  > "Restructuring and impairments increased $282 million, largely due to costs associated with the impairment of Starbucks Reserve and Roastery store locations, and partner severance costs." ([SBUX-10Q-2026-07-29-mdna](https://www.sec.gov/Archives/edgar/data/829224/000082922426000130/sbux-20260628.htm))
- A news report says UBS maintained a Neutral rating and lowered its price target to $105, signaling caution on Starbucks shares.  
  > "UBS Maintains Neutral on Starbucks, Lowers Price Target to $105" ([SBUX-news-2026-10-08-62257066](https://www.benzinga.com/news/26/10/62257066/ubs-maintains-neutral-starbucks-lowers-price-target-105))

*model said evidence: sufficient*

## Data limits

- Prices: Alpaca SIP daily bars, split and dividend adjusted; no intraday data used.
- Fundamentals: SEC XBRL companyfacts, US-GAAP filers only. Foreign private issuers (IFRS, 20-F/40-F) and companies without standard tags drop out as 'missing', they are not guessed.
- Market cap uses the latest cover-page share count; for multi-class issuers it can understate.
- Industry groups are SEC SIC codes, a coarse proxy for a theme (no GICS/BICS in free data).
- Short interest: FINRA consolidated short interest (twice monthly, non-commercial use); % is of shares outstanding, not float.
- Earnings-call transcripts are licensed content and were not used; explanations rely on the 8-K earnings release, 10-Q/10-K MD&A, and news headlines and summaries (Alpaca / Benzinga), never full articles.
- No consensus estimates, revisions, ownership or borrow-cost data: those need a licensed source.
