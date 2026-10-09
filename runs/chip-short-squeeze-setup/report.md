# Screen: Profitable companies with heavy short interest that are moving back above their 50-day average

As of **2026-10-08** (last price date 2026-10-08). Universe: tradable US-listed (NYSE/Nasdaq/AMEX/Arca/BATS) operating companies with an SEC CIK and a 10-K/10-Q/20-F/40-F in the last 18 months; close >= $1; 50-day avg dollar volume >= $1,000,000; one listing per CIK. Model: deepseek / deepseek-v4-pro (translation and prose only; every filter, rank and number below is computed by code).

## 1. Screen spec (proposed by the model, validated by code)

```json
{
  "version": 1,
  "observation": "Profitable companies with heavy short interest that are moving back above their 50-day average",
  "universe": {},
  "conditions": [
    {
      "field": "net_income_ttm",
      "op": ">",
      "value": 0,
      "why": "Profitable companies"
    },
    {
      "field": "short_pct_shares_out",
      "op": ">",
      "value": 0.2,
      "why": "heavy short interest"
    },
    {
      "field": "close",
      "op": ">",
      "ref": "sma50",
      "why": "moving back above their 50-day average"
    }
  ],
  "rank": [
    {
      "field": "short_pct_shares_out",
      "direction": "desc",
      "weight": 1
    }
  ],
  "top_n": 5,
  "unmapped": [
    {
      "text": "moving back above their 50-day average",
      "reason": "Current close above SMA50 is used; the crossover from below is not directly observable with available fields."
    },
    {
      "text": "heavy short interest",
      "reason": "No objective threshold in the observation; used short interest > 20% of shares outstanding as a proxy, note float data is unavailable."
    }
  ],
  "notes": "Interpreted profitable as positive TTM net income and moving back above 50-day average as close > SMA50. Heavy short interest is proxied by short interest > 20% of shares outstanding because float is not available."
}
```

**Not screened: outside the schema**

- "moving back above their 50-day average": Current close above SMA50 is used; the crossover from below is not directly observable with available fields.
- "heavy short interest": No objective threshold in the observation; used short interest > 20% of shares outstanding as a proxy, note float data is unavailable.

## 2. Funnel

| step | in | pass | fail | missing data |
|---|---:|---:|---:|---:|
| universe (liquid US common stocks with SEC filings) | 3827 | 3827 | 0 | 0 |
| net_income_ttm > 0 | 3827 | 1633 | 823 | 1371 |
| short_pct_shares_out > +20.0% | 1633 | 28 | 1573 | 32 |
| close > sma50 | 28 | 6 | 22 | 0 |

## 3. Ranked survivors (6)

| rank | symbol | name | score | market_cap | net_income_ttm | short_pct_shares_out | close | sma50 |
|---|---|---|---|---|---|---|---|---|
| 1 | WOLF | WOLFSPEED, INC. | 1.000 | $1.6B | $4M | +49.3% | $31.02 | $27.90 |
| 2 | KSS | KOHLS Corp | 0.833 | $2.3B | $270M | +29.4% | $20.11 | $18.33 |
| 3 | CBRL | CRACKER BARREL OLD COUNTRY STORE, INC | 0.667 | $1.2B | $32M | +25.4% | $55.34 | $53.95 |
| 4 | MNRO | MONRO, INC. | 0.500 | $413M | $2M | +25.0% | $13.74 | $12.73 |
| 5 | SWKS | SKYWORKS SOLUTIONS, INC. | 0.333 | $12.2B | $290M | +21.7% | $80.75 | $75.86 |
| 6 | SG | Sweetgreen, Inc. | 0.167 | $1.1B | $14M | +21.3% | $9.57 | $7.06 |

## 4. Why the dislocation might exist (top 5)

Every quote below was checked by code to appear verbatim in the linked SEC document. Claims whose quotes failed the check were removed and are listed.

### WOLF: explained

- source: [WOLF 8-K earnings release (Exhibit 99.1), filed 2026-08-19](https://www.sec.gov/Archives/edgar/data/895419/000089541926000049/ex991q4-26.htm)
- source: [WOLF 10-K for period 2026-06-28, MD&A, filed 2026-08-20](https://www.sec.gov/Archives/edgar/data/895419/000089541926000054/wolf-20260628.htm)
- source: [Benzinga: What's Going On With Wolfspeed Stock Thursday? (2026-10-08)](https://www.benzinga.com/trading-ideas/movers/26/10/62246356/whats-going-on-with-wolfspeed-stock-thursday-2)
- source: [Benzinga: Wolfspeed Stock Soars on Massive Pentagon Loan Commitment (2026-10-07)](https://www.benzinga.com/trading-ideas/movers/26/10/62234223/wolfspeed-stock-soars-on-massive-pentagon-loan-commitment)
- source: [Benzinga: Wolfspeed Receives $1.5B Conditional Financing From U.S. Department Of War For Its Domestic Development, Production Of Silicon Carbide Materials, Wide Bandgap Power Devices (2026-10-07)](https://www.benzinga.com/news/26/10/62232932/wolfspeed-receives-15b-conditional-financing-from-u-s-department-of-war-for-its-domestic-development-production-of-silicon-carbide-materials-wide-bandgap-power-devices)
- source: [Benzinga: Wolfspeed's Busy Week: A New Substrate Launch, a Sector-Wide Rally (2026-10-02)](https://www.benzinga.com/trading-ideas/movers/26/10/62133978/wolfspeeds-busy-week-a-new-substrate-launch-a-sector-wide-rally)
- source: [Benzinga: Reported Sunday, Wolfspeed Launches Orderable Premium 200 mm SiC Substrate With Dedicated Capacity, Backed By 200 mm Production Running Continuously Since 2022 (2026-09-28)](https://www.benzinga.com/quote/WOLF)

**Thesis**
- The positive trailing net income is not from ongoing operations, as the successor period shows a net loss of $415.8 million while the predecessor period shows net income of $420.2 million.  
  > "Net (loss) income ($415.8) (88.8) % $420.2 213.5 % ($1,609.2) (212.4) %" ([WOLF-10K-2026-08-20-mdna](https://www.sec.gov/Archives/edgar/data/895419/000089541926000054/wolf-20260628.htm))
- Revenue is down 12% year over year, according to the MD&A, indicating fundamental weakness behind the positive price action.  
  > "Net sales for the Successor period ended June 28, 2026 and Predecessor period ended September 29, 2025 as compared to fiscal 2025 were down 12% primarily driven by the following:" ([WOLF-10K-2026-08-20-mdna](https://www.sec.gov/Archives/edgar/data/895419/000089541926000054/wolf-20260628.htm))

**Bear case**
- The company reported a GAAP net loss of $145 million and negative adjusted EBITDA of $62 million for the most recent quarter.  
  > "GAAP net loss of $145 million and adjusted EBITDA (non-GAAP) of ($62) million." ([WOLF-8K-2026-08-19-ex99](https://www.sec.gov/Archives/edgar/data/895419/000089541926000049/ex991q4-26.htm))
- The company expects revenue to remain flat to down and non-GAAP gross margin to stay negative in the next quarter.  
  > "The Company expects to generate revenue between $140 million and $160 million for its first quarter of fiscal 2027 with non-GAAP gross margin expected to remain negative." ([WOLF-8K-2026-08-19-ex99](https://www.sec.gov/Archives/edgar/data/895419/000089541926000049/ex991q4-26.htm))
- Operating cash flow was deeply negative, consuming $180.8 million in the successor period.  
  > "Cash used in operating activities of continuing operations ($180.8) ($22.4) ($711.7)" ([WOLF-10K-2026-08-20-mdna](https://www.sec.gov/Archives/edgar/data/895419/000089541926000054/wolf-20260628.htm))

*Stripped by the citation check (1):* "A news report says a conditional Pentagon loan commitment caused Wolfspeed share" (claim states numbers not in its quote: ['50'])

*model said evidence: sufficient*

### KSS: explained

- source: [KSS 8-K earnings release (Exhibit 99.1), filed 2026-08-26](https://www.sec.gov/Archives/edgar/data/885639/000119312526365860/d171200dex991.htm)
- source: [KSS 10-Q for period 2026-08-01, MD&A, filed 2026-09-03](https://www.sec.gov/Archives/edgar/data/885639/000119312526381893/kss-20260801.htm)
- source: [Benzinga: BTIG Reiterates Neutral on Kohl'sto Neutral (2026-09-18)](https://www.benzinga.com/news/26/09/61862330/btig-reiterates-neutral-kohl-sto-neutral)

**Thesis**
- Gross margin increased 305 basis points year-over-year, indicating stronger merchandise profitability.  
  > "Gross margin as a percentage of net sales was 43.0%, an increase of 305 basis points year-over-year." ([KSS-8K-2026-08-26-ex99](https://www.sec.gov/Archives/edgar/data/885639/000119312526365860/d171200dex991.htm))
- Management is restarting share repurchases of up to $100 million in 2026, returning capital to shareholders.  
  > "Share Repurchase Program: Restarting share repurchases of up to $100 million in 2026 under existing $3 billion authorization" ([KSS-8K-2026-08-26-ex99](https://www.sec.gov/Archives/edgar/data/885639/000119312526365860/d171200dex991.htm))

**Bear case**
- Net sales decreased 0.9% year-over-year, with comparable sales also down 0.9%.  
  > "Net sales decreased 0.9% year-over-year, to $3.3 billion, with comparable sales also down 0.9%." ([KSS-8K-2026-08-26-ex99](https://www.sec.gov/Archives/edgar/data/885639/000119312526365860/d171200dex991.htm))
- Operating income declined to $261 million from $279 million in the prior year, a decrease of 45 basis points as a percentage of total revenue.  
  > "Operating income was $261 million compared to $279 million in the prior year. As a percentage of total revenue, operating income was 7.4%, a decrease of 45 basis points year-over-year." ([KSS-8K-2026-08-26-ex99](https://www.sec.gov/Archives/edgar/data/885639/000119312526365860/d171200dex991.htm))

*Stripped by the citation check (2):* "The Company raised its full year 2026 financial outlook, reflecting improved pro" (claim states numbers not in its quote: ['2026']); "The company's debt ratings are below investment grade, and its 3.375% notes due " (claim states numbers not in its quote: ['3.375'])

*model said evidence: sufficient*

### CBRL: explained

- source: [CBRL 8-K earnings release (Exhibit 99.1), filed 2026-09-23](https://www.sec.gov/Archives/edgar/data/1067294/000110465926109812/tm2625926d1_ex99-1.htm)
- source: [CBRL 10-K for period 2026-07-31, MD&A, filed 2026-09-25](https://www.sec.gov/Archives/edgar/data/1067294/000110465926110772/cbrl-20260731x10k.htm)
- source: [Benzinga: Citigroup Maintains Sell on Cracker Barrel Old, Raises Price Target to $44 (2026-09-25)](https://www.benzinga.com/news/26/09/62000293/citigroup-maintains-sell-cracker-barrel-old-raises-price-target-44)
- source: [Benzinga: Cracker Barrel Battles Consumer Pressure With $7.99 Breakfast, $8.99 Early Dine Deals (2026-09-23)](https://www.benzinga.com/markets/earnings/26/09/61951771/cracker-barrel-battles-consumer-pressure-with-7-99-breakfast-8-99-early-dine-deals)
- source: [Benzinga: Full Transcript: Cracker Barrel Old Q4 2026 Earnings Call (2026-09-23)](https://www.benzinga.com/news/26/09/61944522/full-transcript-cracker-barrel-old-q4-2026-earnings-call)
- source: [Benzinga: Cracker Barrel Old Lowers FY2027 Sales Guidance from $3.800B-$3.900B to $3.325B-$3.400B vs $3.386B Est (2026-09-23)](https://www.benzinga.com/news/26/09/61941606/cracker-barrel-old-lowers-fy2027-sales-guidance-3-800b-3-900b-3-325b-3-400b-vs-3-386b-est)
- source: [Benzinga: Cracker Barrel Old Q4 Adj. EPS $0.99 Beats $0.15 Estimate, Sales $849.342M Beat $836.894M Estimate (2026-09-23)](https://www.benzinga.com/news/earnings/26/09/61941514/cracker-barrel-old-q4-adj-eps-0-99-beats-0-15-estimate-sales-849-342m-beat-836-894m-estimate)
- source: [Benzinga: UBS Maintains Neutral on Cracker Barrel Old, Raises Price Target to $46 (2026-09-21)](https://www.benzinga.com/news/26/09/61894345/ubs-maintains-neutral-cracker-barrel-old-raises-price-target-46)
- source: [Benzinga: How To Earn $500 A Month From Cracker Barrel Stock Ahead Of Q4 Earnings (2026-09-18)](https://www.benzinga.com/trading-ideas/dividends/26/09/61866275/how-to-earn-500-a-month-from-cracker-barrel-stock-ahead-of-q4-earnings)
- source: [Benzinga: Cracker Barrel Likely To Report Lower Q4 Earnings; These Most Accurate Analysts Revise Forecasts Ahead Of Earnings Call (2026-09-15)](https://www.benzinga.com/analyst-stock-ratings/price-target/26/09/61785035/cracker-barrel-likely-to-report-lower-q4-earnings-these-most-accurate-analysts-revise-forecasts-ahead-of-earnings-call)

**Thesis**
- Cracker Barrel's positive net income is supported by non-recurring items, including a $47,422 litigation settlement that is not part of core operations.  
  > "In the third quarter of 2026, the Company received and recorded $47,422, net of legal fees, pursuant to a settlement agreement resolving interchange fee litigation." ([CBRL-10K-2026-09-25-mdna](https://www.sec.gov/Archives/edgar/data/1067294/000110465926110772/cbrl-20260731x10k.htm))
- The company also recorded a $47,421 gain on a sale-leaseback transaction, further inflating reported GAAP profitability.  
  > "In the fourth quarter of 2026, we entered into a sale and leaseback transaction involving 26 of our owned Cracker Barrel properties and recorded a net gain of $47,421." ([CBRL-10K-2026-09-25-mdna](https://www.sec.gov/Archives/edgar/data/1067294/000110465926110772/cbrl-20260731x10k.htm))
- Full-year total revenue declined 4.7% in 2026, signaling weakness in the company's core sales trend.  
  > "Total revenue in 2026 decreased 4.7% as compared to 2025." ([CBRL-10K-2026-09-25-mdna](https://www.sec.gov/Archives/edgar/data/1067294/000110465926110772/cbrl-20260731x10k.htm))
- The company's own MD&A attributes the traffic decline to negative publicity and customer backlash from brand changes, which could continue to pressure sales.  
  > "negative publicity and customer reactions to certain changes in brand initiatives, including the launch of a new logo and modern test store remodels in the first quarter of 2026" ([CBRL-10K-2026-09-25-mdna](https://www.sec.gov/Archives/edgar/data/1067294/000110465926110772/cbrl-20260731x10k.htm))

**Bear case**
- A news report says Citigroup maintained a Sell rating on Cracker Barrel and raised its price target to $44.  
  > "Citigroup Maintains Sell on Cracker Barrel Old, Raises Price Target to $44" ([CBRL-news-2026-09-25-62000293](https://www.benzinga.com/news/26/09/62000293/citigroup-maintains-sell-cracker-barrel-old-raises-price-target-44))
- A news report says Cracker Barrel lowered its fiscal 2027 sales guidance to $3.325B-$3.400B from $3.800B-$3.900B.  
  > "Cracker Barrel Old Lowers FY2027 Sales Guidance from $3.800B-$3.900B to $3.325B-$3.400B vs $3.386B Est" ([CBRL-news-2026-09-23-61941606](https://www.benzinga.com/news/26/09/61941606/cracker-barrel-old-lowers-fy2027-sales-guidance-3-800b-3-900b-3-325b-3-400b-vs-3-386b-est))
- Cracker Barrel's operating results declined in 2026 compared to 2025 due to lower revenue, MSBC divestiture losses, and impairment charges.  
  > "Our operating results declined in 2026 as compared to 2025 primarily due to the decrease in total revenue, the loss on sale of business assets associated with the divestiture of the MSBC business and the impairment and store closing costs discussed above partially offset by the gain recognized on the 2026 sale and leaseback transaction." ([CBRL-10K-2026-09-25-mdna](https://www.sec.gov/Archives/edgar/data/1067294/000110465926110772/cbrl-20260731x10k.htm))

*model said evidence: sufficient*

### MNRO: explained

- source: [MNRO 8-K earnings release (Exhibit 99.1), filed 2026-07-29](https://www.sec.gov/Archives/edgar/data/876427/000119312526322170/d66984dex991.htm)
- source: [MNRO 10-Q for period 2026-06-27, MD&A, filed 2026-07-29](https://www.sec.gov/Archives/edgar/data/876427/000087642726000010/mnro-20260627x10q.htm)

**Thesis**
- The screen's positive TTM net income conflicts with the most recent quarter's net loss of $2.1 million, which likely contributes to elevated short interest.  
  > "Net loss for the first quarter of fiscal 2027 was $2.1 million, as compared to a net loss of $8.1 million in the same period of the prior year." ([MNRO-8K-2026-07-29-ex99](https://www.sec.gov/Archives/edgar/data/876427/000119312526322170/d66984dex991.htm))
- Adjusted operating income dropped to $2.2 million from $14.0 million in the prior-year quarter, showing that underlying profitability worsened despite the headline operating income improvement.  
  > "Adjusted operating income, a non-GAAP measure, for the first quarter of fiscal 2027 was $2.2 million, or 0.8% of sales, as compared to adjusted operating income of $14.0 million, or 4.7% of sales in the prior year period." ([MNRO-8K-2026-07-29-ex99](https://www.sec.gov/Archives/edgar/data/876427/000119312526322170/d66984dex991.htm))
- Sales decreased 4.6% in the most recent quarter, driven by closed stores and lower comparable store sales, indicating weak demand fundamentals that shorts may be targeting.  
  > "Sales for the first quarter of the fiscal year ending March 27, 2027 (“fiscal 2027”) decreased 4.6% to $287.1 million, as compared to sales of $301.0 million for the first quarter of the fiscal year ended March 28, 2026 (“fiscal 2026”)." ([MNRO-8K-2026-07-29-ex99](https://www.sec.gov/Archives/edgar/data/876427/000119312526322170/d66984dex991.htm))

**Bear case**
- Adjusted diluted loss per share was $.09, meaning the company lost money on a core basis in the latest quarter after excluding one-time items.  
  > "Adjusted diluted loss per share, a non-GAAP measure, for the first quarter of fiscal 2027 was $.09." ([MNRO-8K-2026-07-29-ex99](https://www.sec.gov/Archives/edgar/data/876427/000119312526322170/d66984dex991.htm))
- Cash used for operating activities was $30.4 million in the quarter, reflecting a net loss and significant working capital outflows.  
  > "For the three months ended June 27, 2026, cash used for operating activities was $30.4 million, which consisted of a net loss of $2.1 million and a change in operating assets and liabilities of $44.6 million, partially offset by non-cash adjustments of $16.3 million." ([MNRO-10Q-2026-07-29-mdna](https://www.sec.gov/Archives/edgar/data/876427/000087642726000010/mnro-20260627x10q.htm))

*Stripped by the citation check (1):* "Comparable store sales declined 1.7% due to lower store traffic and consumers de" (claim states numbers not in its quote: ['1.7'])

*model said evidence: sufficient*

### SWKS: explained

- source: [SWKS 8-K earnings release (Exhibit 99.1), filed 2026-07-28](https://www.sec.gov/Archives/edgar/data/4127/000000412726000047/q3268-kex991earningsrelease.htm)
- source: [SWKS 10-Q for period 2026-07-03, MD&A, filed 2026-07-28](https://www.sec.gov/Archives/edgar/data/4127/000000412726000049/swks-20260703.htm)
- source: [Benzinga: Skyworks Solutions Form 13G Shows Abigail P. Johnson Reports 12.6% Stake In Co. As Of Sept. 30 (2026-10-07)](https://www.benzinga.com/m/26/10/62224459/skyworks-solutions-form-13g-shows-abigail-p-johnson-reports-12-6-stake-co-sept-30)
- source: [Benzinga: Citigroup Maintains Neutral on Skyworks Solutions, Raises Price Target to $90 (2026-10-06)](https://www.benzinga.com/news/26/10/62200823/citigroup-maintains-neutral-skyworks-solutions-raises-price-target-90)
- source: [Benzinga: B. Riley Securities Upgrades Skyworks Solutions to Buy, Raises Price Target to $107 (2026-10-06)](https://www.benzinga.com/news/26/10/62198308/b-riley-securities-upgrades-skyworks-solutions-buy-raises-price-target-107)
- source: [Benzinga: RBC Capital Maintains Sector Perform on Skyworks Solutions, Raises Price Target to $95 (2026-10-01)](https://www.benzinga.com/news/26/10/62105621/rbc-capital-maintains-sector-perform-skyworks-solutions-raises-price-target-95)
- source: [Benzinga: Wall Street's Most Accurate Analysts Spotlight On 3 Tech Stocks Delivering High-Dividend Yields (2026-09-25)](https://www.benzinga.com/trading-ideas/dividends/26/09/61991547/wall-streets-most-accurate-analysts-spotlight-on-3-tech-stocks-delivering-high-dividend-yields-14)
- source: [Benzinga: Top 3 Tech Stocks That May Fall Off A Cliff This month (2026-09-14)](https://www.benzinga.com/trading-ideas/short-ideas/26/09/61762552/top-3-tech-stocks-that-may-fall-off-a-cliff-this-month-3)
- source: [Benzinga: Reported Friday, Skyworks Extends Withdrawal Deadline For Qorvo Note Exchange Offers To September 18, With Settlement Expected After Mergers Close (2026-09-14)](https://www.benzinga.com/quote/QRVO)
- source: [Benzinga: Stock of the Day: Is This the Top for Skyworks? (2026-09-11)](https://www.benzinga.com/trading-ideas/technicals/26/09/61749456/stock-of-the-day-is-this-the-top-for-skyworks)
- source: [Benzinga: QUICK SPARK: Skyworks Solution Stock Eyes Best Weekly Rally Since 2009 (2026-09-11)](https://www.benzinga.com/markets/tech/26/09/61748374/skyworks-solutions-stock-best-week-since-2009-qorvo-merger-final-stages)
- source: [Benzinga: QUICK SPARK: Skyworks Stock Poised to Be S&P 500’s Best Stock This Week (2026-09-11)](https://www.benzinga.com/trading-ideas/movers/26/09/61744663/skyworks-stock-sp-500-best-weekly-performer)

**Thesis**
- A news report says Skyworks shares rallied 22% in a week after the CEO said the $22 billion Qorvo merger has entered its final stages and should close by year-end, providing a bullish catalyst that may conflict with underlying fundamentals.  
  > "Skyworks shares have rallied 22% this week after CEO Phil Brace said the $22 billion Qorvo merger has entered its final stages and should close by year-end." ([SWKS-news-2026-09-11-61748374](https://www.benzinga.com/markets/tech/26/09/61748374/skyworks-solutions-stock-best-week-since-2009-qorvo-merger-final-stages))
- The Qorvo combination still has closing uncertainty, as the company states there can be no assurances that the closing will occur on its hoped-for timeline, which may encourage short sellers.  
  > "There can be no assurances that the closing will occur on this timeline." ([SWKS-10Q-2026-07-28-mdna](https://www.sec.gov/Archives/edgar/data/4127/000000412726000049/swks-20260703.htm))

**Bear case**
- GAAP diluted EPS of $0.22 and GAAP operating income of $49 million indicate slim GAAP profitability in the third fiscal quarter.  
  > "Revenue for the third fiscal quarter of 2026 was $935 million. On a GAAP basis, operating income for the third fiscal quarter was $49 million with diluted earnings per share of $0.22." ([SWKS-8K-2026-07-28-ex99](https://www.sec.gov/Archives/edgar/data/4127/000000412726000047/q3268-kex991earningsrelease.htm))
- The company's gross profit declined due to unfavorable product mix, pressuring margins despite higher unit volumes.  
  > "The decrease in gross profit for the three and nine months ended July 3, 2026, as compared with the corresponding periods in fiscal 2025, was primarily the result of unfavorable product mix, partially offset by higher unit volumes." ([SWKS-10Q-2026-07-28-mdna](https://www.sec.gov/Archives/edgar/data/4127/000000412726000049/swks-20260703.htm))
- The board has eliminated the quarterly dividend, which may remove a source of investor support for the stock.  
  > "the board has replaced the stock repurchase program expiring in February 2027 with a new $2 billion stock repurchase program, and the company has decided not to declare any quarterly dividends going forward, redirecting that capital toward these higher-return uses." ([SWKS-8K-2026-07-28-ex99](https://www.sec.gov/Archives/edgar/data/4127/000000412726000047/q3268-kex991earningsrelease.htm))

*Stripped by the citation check (1):* "Skyworks' own 10-Q shows net revenue fell year over year, driven primarily by a " (claim states numbers not in its quote: ['10'])

*model said evidence: sufficient*

## Data limits

- Prices: Alpaca SIP daily bars, split and dividend adjusted; no intraday data used.
- Fundamentals: SEC XBRL companyfacts, US-GAAP filers only. Foreign private issuers (IFRS, 20-F/40-F) and companies without standard tags drop out as 'missing', they are not guessed.
- Market cap uses the latest cover-page share count; for multi-class issuers it can understate.
- Industry groups are SEC SIC codes, a coarse proxy for a theme (no GICS/BICS in free data).
- Short interest: FINRA consolidated short interest (twice monthly, non-commercial use); % is of shares outstanding, not float.
- Earnings-call transcripts are licensed content and were not used; explanations rely on the 8-K earnings release, 10-Q/10-K MD&A, and news headlines and summaries (Alpaca / Benzinga), never full articles.
- No consensus estimates, revisions, ownership or borrow-cost data: those need a licensed source.
