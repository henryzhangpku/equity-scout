# Screen: Small caps between 300 million and 2 billion dollars with more cash than debt, down 40% or more from their highs, still generating free cash flow

As of **2026-10-08** (last price date 2026-10-08). Universe: tradable US-listed (NYSE/Nasdaq/AMEX/Arca/BATS) operating companies with an SEC CIK and a 10-K/10-Q/20-F/40-F in the last 18 months; close >= $1; 50-day avg dollar volume >= $1,000,000; one listing per CIK. Model: deepseek / deepseek-v4-pro (translation and prose only; every filter, rank and number below is computed by code).

## 1. Screen spec (proposed by the model, validated by code)

```json
{
  "version": 1,
  "observation": "Small caps between 300 million and 2 billion dollars with more cash than debt, down 40% or more from their highs, still generating free cash flow",
  "universe": {
    "market_cap_min": 300000000,
    "market_cap_max": 2000000000
  },
  "conditions": [
    {
      "field": "net_debt",
      "op": "<",
      "value": 0,
      "why": "more cash than debt"
    },
    {
      "field": "drawdown_52w",
      "op": "<=",
      "value": -0.4,
      "why": "down 40% or more from their highs"
    },
    {
      "field": "fcf_ttm",
      "op": ">",
      "value": 0,
      "why": "still generating free cash flow"
    }
  ],
  "rank": [
    {
      "field": "fcf_ttm",
      "direction": "desc",
      "weight": 1
    }
  ],
  "top_n": 5,
  "unmapped": [],
  "notes": "Interpreted 'down from their highs' as the drawdown from the 52-week high close, since all-time high data is not available. Net debt less than zero captures more cash than debt. Ranked by absolute free cash flow to emphasize the positive cash flow requirement."
}
```

## 2. Funnel

| step | in | pass | fail | missing data |
|---|---:|---:|---:|---:|
| universe (liquid US common stocks with SEC filings) | 3827 | 3827 | 0 | 0 |
| market_cap >= $300M | 3827 | 3060 | 554 | 213 |
| market_cap <= $2.00B | 3060 | 1158 | 1902 | 0 |
| net_debt < 0 | 1158 | 389 | 434 | 335 |
| drawdown_52w <= -40.0% | 389 | 111 | 254 | 24 |
| fcf_ttm > 0 | 111 | 31 | 57 | 23 |

## 3. Ranked survivors (31)

| rank | symbol | name | score | market_cap | net_debt | drawdown_52w | fcf_ttm |
|---|---|---|---|---|---|---|---|
| 1 | OPFI | OppFi Inc. | 1.000 | $411M | $-14M | -46.5% | $385M |
| 2 | COLL | COLLEGIUM PHARMACEUTICAL, INC | 0.968 | $720M | $-118M | -55.6% | $328M |
| 3 | YELP | YELP INC | 0.935 | $1.1B | $-77M | -42.7% | $297M |
| 4 | TDOC | Teladoc Health, Inc. | 0.903 | $1.0B | $-732M | -43.0% | $254M |
| 5 | CRMD | CorMedix Inc. | 0.871 | $571M | $-257M | -42.5% | $250M |
| 6 | UPWK | UPWORK, INC | 0.839 | $1.1B | $-254M | -61.2% | $204M |
| 7 | ALHC | Alignment Healthcare, Inc. | 0.806 | $1.8B | $-378M | -64.5% | $178M |
| 8 | BL | BLACKLINE, INC. | 0.774 | $1.7B | $-528M | -50.3% | $177M |
| 9 | LZ | LEGALZOOM.COM, INC. | 0.742 | $1.0B | $-167M | -45.8% | $150M |
| 10 | TRIP | TripAdvisor, Inc. | 0.710 | $1.1B | $-19M | -46.4% | $133M |
| 11 | INSP | Inspire Medical Systems, Inc. | 0.677 | $1.9B | $-299M | -53.7% | $117M |
| 12 | PLAB | PHOTRONICS INC | 0.645 | $1.8B | $-669M | -45.9% | $110M |
| 13 | AGNT | AGNT, Inc. | 0.613 | $670M | $-110M | -65.0% | $93M |
| 14 | SEDG | SOLAREDGE TECHNOLOGIES, INC. | 0.581 | $2.0B | $-527M | -58.6% | $90M |
| 15 | TRUP | TRUPANION, INC. | 0.548 | $1.1B | $-292M | -41.3% | $82M |
| 16 | PHR | Phreesia, Inc. | 0.516 | $662M | $-73M | -55.3% | $81M |
| 17 | PSIX | POWER SOLUTIONS INTERNATIONAL, INC. | 0.484 | $1.1B | $-64M | -50.9% | $67M |
| 18 | ADTN | ADTRAN Holdings, Inc. | 0.452 | $610M | $-55M | -61.4% | $57M |
| 19 | OIS | OIL STATES INTERNATIONAL, INC | 0.419 | $495M | $-2M | -43.0% | $54M |
| 20 | ERII | Energy Recovery, Inc. | 0.387 | $349M | $-93M | -62.2% | $39M |
| 21 | REAL | TheRealReal, Inc. | 0.355 | $1.2B | $-109M | -43.1% | $36M |
| 22 | TLS | TELOS CORP | 0.323 | $327M | $-40M | -43.7% | $34M |
| 23 | COUR | Coursera, Inc. | 0.290 | $1.4B | $-982M | -50.9% | $33M |
| 24 | BBW | BUILD-A-BEAR WORKSHOP INC | 0.258 | $319M | $-7M | -62.7% | $25M |
| 25 | LINC | LINCOLN EDUCATIONAL SERVICES CORP | 0.226 | $737M | $-18M | -58.3% | $25M |

(6 more in run.json)

## 4. Why the dislocation might exist (top 5)

Every quote below was checked by code to appear verbatim in the linked SEC document. Claims whose quotes failed the check were removed and are listed.

### OPFI: explained

- source: [OPFI 8-K earnings release (Exhibit 99.1), filed 2026-08-10](https://www.sec.gov/Archives/edgar/data/1818502/000181850226000073/oppfi-reportsxsecondxqua.htm)
- source: [OPFI 10-Q for period 2026-06-30, MD&A, filed 2026-08-10](https://www.sec.gov/Archives/edgar/data/1818502/000181850226000075/opfi-20260630.htm)
- source: [Benzinga: BNCCORP Stockholders Approve OppFi Merger; BNCC Stockholders To Receive $19.375/Share And 1.9 Shares of OppFi ClassA Common Stock For Each BNCC Share (2026-09-17)](https://www.benzinga.com/quote/OPFI)

**Thesis**
- Reported net charge-offs as a percentage of average receivables rose to 52.3% from 43.5%, indicating a sharp deterioration in credit quality that likely contributed to the stock's decline.  
  > "Net charge-offs as % of average receivables, annualized(c) 52.3 % 43.5 % 20.4 %" ([OPFI-8K-2026-08-10-ex99](https://www.sec.gov/Archives/edgar/data/1818502/000181850226000073/oppfi-reportsxsecondxqua.htm))
- Adjusted net income decreased 27.0% year over year, showing that the company's underlying profitability weakened even as GAAP net income increased.  
  > "Adjusted net income(2) $ 28,760 $ 39,401 (27.0) %" ([OPFI-8K-2026-08-10-ex99](https://www.sec.gov/Archives/edgar/data/1818502/000181850226000073/oppfi-reportsxsecondxqua.htm))
- Total net originations fell 9.3% year over year, pointing to slower loan growth that may pressure future revenue.  
  > "Total net originations(a) $ 212,038 $ 233,873 (9.3) %" ([OPFI-8K-2026-08-10-ex99](https://www.sec.gov/Archives/edgar/data/1818502/000181850226000073/oppfi-reportsxsecondxqua.htm))

**Bear case**
- Change in fair value of finance receivables increased 39.8% year over year to a larger loss, reflecting higher gross charge-offs and a negative fair value adjustment.  
  > "Change in fair value of finance receivables (58,999) (42,197) (16,802) 39.8" ([OPFI-8K-2026-08-10-ex99](https://www.sec.gov/Archives/edgar/data/1818502/000181850226000073/oppfi-reportsxsecondxqua.htm))
- Professional fees rose 184.1% year over year, reflecting higher transaction-related costs that reduce operating income.  
  > "Professional fees 13,613 4,792 8,821 184.1" ([OPFI-8K-2026-08-10-ex99](https://www.sec.gov/Archives/edgar/data/1818502/000181850226000073/oppfi-reportsxsecondxqua.htm))
- A news report says BNCC stockholders approved the merger and will receive 1.9 shares of OppFi Class A common stock for each BNCC share, implying potential share dilution.  
  > "BNCCORP Stockholders Approve OppFi Merger; BNCC Stockholders To Receive $19.375/Share And 1.9 Shares of OppFi ClassA Common Stock For Each BNCC Share" ([OPFI-news-2026-09-17-61857010](https://www.benzinga.com/quote/OPFI))

*model said evidence: sufficient*

### COLL: explained

- source: [COLL 8-K earnings release (Exhibit 99.1), filed 2026-08-06](https://www.sec.gov/Archives/edgar/data/1267565/000162828026053849/coll-2026x06x30xex99x1.htm)
- source: [COLL 10-Q for period 2026-06-30, MD&A, filed 2026-08-06](https://www.sec.gov/Archives/edgar/data/1267565/000162828026053851/coll-20260630.htm)
- source: [Benzinga: Collegium Pharmaceutical Reports Q2 2026 Results: Full Earnings Call Transcript (2026-10-05)](https://www.benzinga.com/news/26/10/62156443/collegium-pharmaceutical-reports-q2-2026-results-full-earnings-call-transcript)
- source: [Benzinga: Oppenheimer Initiates Coverage On Collegium Pharmaceutical with Outperform Rating, Announces Price Target of $50 (2026-09-23)](https://www.benzinga.com/news/26/09/61940882/oppenheimer-initiates-coverage-collegium-pharmaceutical-outperform-rating-announces-price-target-50)
- source: [Benzinga: Truist Securities Maintains Buy on Collegium Pharmaceutical, Lowers Price Target to $49 (2026-09-09)](https://www.benzinga.com/news/26/09/61692957/truist-securities-maintains-buy-collegium-pharmaceutical-lowers-price-target-49)
- source: [Benzinga: Leerink Partners Initiates Coverage On Collegium Pharmaceutical with Outperform Rating, Announces Price Target of $45 (2026-09-09)](https://www.benzinga.com/news/26/09/61691096/leerink-partners-initiates-coverage-collegium-pharmaceutical-outperform-rating-announces-price-targe)

**Thesis**
- Despite the GAAP loss, adjusted EBITDA rose 8% year over year in the quarter, indicating underlying operational strength.  
  > "Adjusted EBITDA for the 2026 Quarter was $113.8 million, compared to $105.1 million for the 2025 Quarter, representing an 8% increase year-over-year." ([COLL-8K-2026-08-06-ex99](https://www.sec.gov/Archives/edgar/data/1267565/000162828026053849/coll-2026x06x30xex99x1.htm))
- JORNAY PM quarterly net revenue grew 41% year over year, showing strong ADHD portfolio momentum.  
  > "Generated JORNAY PM® Quarterly Net Revenue of $46.1 Million, Up 41% Year-over-Year" ([COLL-8K-2026-08-06-ex99](https://www.sec.gov/Archives/edgar/data/1267565/000162828026053849/coll-2026x06x30xex99x1.htm))
- A news report says Oppenheimer initiated coverage with an Outperform rating and $50 price target.  
  > "Oppenheimer Initiates Coverage On Collegium Pharmaceutical with Outperform Rating, Announces Price Target of $50" ([COLL-news-2026-09-23-61940882](https://www.benzinga.com/news/26/09/61940882/oppenheimer-initiates-coverage-collegium-pharmaceutical-outperform-rating-announces-price-target-50))

**Bear case**
- Pain portfolio revenues fell 9% year over year in the quarter, driven by declines in multiple pain products.  
  > "Generated pain portfolio net revenues of $140.9 million in the 2026 Quarter, down 9% year-over-year." ([COLL-8K-2026-08-06-ex99](https://www.sec.gov/Archives/edgar/data/1267565/000162828026053849/coll-2026x06x30xex99x1.htm))
- The company lowered full-year Product Revenues, Net and Adjusted EBITDA guidance, citing lower-than-expected pricing on Nucynta authorized generics.  
  > "The decreases in Product Revenues, Net and Adjusted EBITDA are largely driven by lower-than-expected revenue from the AG versions of Nucynta and Nucynta ER due to lower net pricing." ([COLL-8K-2026-08-06-ex99](https://www.sec.gov/Archives/edgar/data/1267565/000162828026053849/coll-2026x06x30xex99x1.htm))
- The company's 2025 Term Loan principal was $865.5 million, with $55.0 million due within the next twelve months, indicating significant leverage from the Azstarys acquisition.  
  > "As of June 30, 2026, the outstanding principal balance of the 2025 Term Loan was $865.5 million, of which $55.0 million in principal payments are due within the next 12 months." ([COLL-10Q-2026-08-06-mdna](https://www.sec.gov/Archives/edgar/data/1267565/000162828026053851/coll-20260630.htm))

*model said evidence: sufficient*

### YELP: explained

- source: [YELP 8-K earnings release (Exhibit 99.1), filed 2026-08-06](https://www.sec.gov/Archives/edgar/data/1345016/000134501626000059/yelpq2-26ex991pressrelease.htm)
- source: [YELP 10-Q for period 2026-06-30, MD&A, filed 2026-08-07](https://www.sec.gov/Archives/edgar/data/1345016/000134501626000066/yelp-20260630.htm)

**Thesis**
- Other revenue grew 98% year over year to a record $33 million in the second quarter.  
  > "Other revenue accelerated from the first quarter, increasing 98% year over year to a record $33 million." ([YELP-8K-2026-08-06-ex99](https://www.sec.gov/Archives/edgar/data/1345016/000134501626000059/yelpq2-26ex991pressrelease.htm))
- Adjusted EBITDA margin remained at 24% in the second quarter despite Adjusted EBITDA decreasing 9% year over year.  
  > "Adjusted EBITDA1 decreased 9% year over year to $91 million, reflecting a 24% margin" ([YELP-8K-2026-08-06-ex99](https://www.sec.gov/Archives/edgar/data/1345016/000134501626000059/yelpq2-26ex991pressrelease.htm))
- Yelp held $94.1 million in cash and cash equivalents as of June 30, 2026.  
  > "As of June 30, 2026, we had cash and cash equivalents of $94.1 million, including cash held internationally of $37.5 million." ([YELP-10Q-2026-08-07-mdna](https://www.sec.gov/Archives/edgar/data/1345016/000134501626000066/yelp-20260630.htm))

**Bear case**
- Advertising revenue declined 3% year over year in both the three and six months ended June 30, 2026.  
  > "Advertising revenue for the three and six months ended June 30, 2026 decreased 3% year over year." ([YELP-10Q-2026-08-07-mdna](https://www.sec.gov/Archives/edgar/data/1345016/000134501626000066/yelp-20260630.htm))
- Management anticipates net revenue will decrease slightly in the third quarter of 2026 due to continued economic challenges.  
  > "We anticipate net revenue will decrease slightly in the three months ended September 30, 2026 compared to the prior-year period, reflecting the continued economic challenges facing consumers and local businesses." ([YELP-10Q-2026-08-07-mdna](https://www.sec.gov/Archives/edgar/data/1345016/000134501626000066/yelp-20260630.htm))
- Yelp has paused share repurchases through the remainder of 2026.  
  > "we plan to prioritize as we pause share repurchases through the remainder of 2026" ([YELP-10Q-2026-08-07-mdna](https://www.sec.gov/Archives/edgar/data/1345016/000134501626000066/yelp-20260630.htm))

*Stripped by the citation check (1):* "Yelp reported free cash flow of $106,229 thousand for the first half of 2026, in" (claim states numbers not in its quote: ['2026'])

*model said evidence: sufficient*

### TDOC: explained

- source: [TDOC 8-K earnings release (Exhibit 99.1), filed 2026-07-29](https://www.sec.gov/Archives/edgar/data/1477449/000147744926000036/tdoc-20260630xexx991.htm)
- source: [TDOC 10-Q for period 2026-06-30, MD&A, filed 2026-07-30](https://www.sec.gov/Archives/edgar/data/1477449/000147744926000038/tdoc-20260630.htm)
- source: [Benzinga: Teladoc Turns Smartphone Cameras Into AI-Powered Vital Sign Monitors (2026-10-07)](https://www.benzinga.com/news/health-care/26/10/62214223/teladoc-turns-smartphone-cameras-into-ai-powered-vital-sign-monitors)
- source: [Benzinga: Teladoc Health Adds Two New AI-Powered Capabilities To Its Enterprise Smart Care Platform Solo (2026-10-07)](https://www.benzinga.com/news/26/10/62211086/teladoc-health-adds-two-new-ai-powered-capabilities-its-enterprise-smart-care-platform-solo)
- source: [Benzinga: OpenAI Announces MentalHealthBench, Open Benchmark For Evaluating AI Responses In Mental Health Conversations, Built With More Than 80 Licensed Experts (2026-09-23)](https://www.benzinga.com/news/26/09/61957908/openai-announces-mentalhealthbench-open-benchmark-evaluating-ai-responses-mental-health-conversation)

**Thesis**
- BetterHelp's cash-pay revenue pressure accelerated late in the quarter, prompting a lowered segment outlook.  
  > "However, pressure on cash pay revenue accelerated further in late May and into June, beyond the assumptions underlying our prior outlook." ([TDOC-8K-2026-07-29-ex99](https://www.sec.gov/Archives/edgar/data/1477449/000147744926000036/tdoc-20260630xexx991.htm))
- Consolidated revenue declined 4% year over year in the second quarter.  
  > "Total revenue was $606.9 million for the three months ended June 30, 2026, compared to $631.9 million for the three months ended June 30, 2025, a decrease of $25.0 million, or 4%." ([TDOC-10Q-2026-07-30-mdna](https://www.sec.gov/Archives/edgar/data/1477449/000147744926000038/tdoc-20260630.htm))
- The company acknowledges that BetterHelp goodwill could be impaired if share-price weakness or segment performance worsens.  
  > "We will continue to monitor and evaluate events and circumstances, including a sustained decrease in our share price and the future performance of the BetterHelp segment, and should any change occur, it could require further testing of the goodwill, which may result in an impairment of the BetterHelp reporting unit's goodwill." ([TDOC-10Q-2026-07-30-mdna](https://www.sec.gov/Archives/edgar/data/1477449/000147744926000038/tdoc-20260630.htm))
- Free cash flow declined sharply compared to the prior year in both the second quarter and first half.  
  > "Free cash flow was $35.7 million in Second Quarter 2026, compared to $61.2 million in Second Quarter 2025, and was $9.4 million in the first six months of 2026, compared to $45.5 million in the first six months of 2025." ([TDOC-8K-2026-07-29-ex99](https://www.sec.gov/Archives/edgar/data/1477449/000147744926000036/tdoc-20260630xexx991.htm))

**Bear case**
- BetterHelp revenue fell 12% year over year and its adjusted EBITDA margin was nearly zero in the quarter.  
  > "BetterHelp segment revenue of $212.6 million, down 12% year-over-year, and adjusted EBITDA margin of 0.2%" ([TDOC-8K-2026-07-29-ex99](https://www.sec.gov/Archives/edgar/data/1477449/000147744926000036/tdoc-20260630xexx991.htm))
- Management has lowered the BetterHelp segment revenue outlook for the full year, reflecting continued cash-pay weakness.  
  > "we have lowered our BetterHelp segment revenue outlook to reflect updated assumptions for cash pay including prioritization of the growing insurance market." ([TDOC-8K-2026-07-29-ex99](https://www.sec.gov/Archives/edgar/data/1477449/000147744926000036/tdoc-20260630xexx991.htm))

*Stripped by the citation check (1):* "The company expects up to $20 million in restructuring costs for 2026, indicatin" (claim states numbers not in its quote: ['20'])

*model said evidence: sufficient*

### CRMD: not enough evidence

- source: [CRMD 8-K earnings release (Exhibit 99.1), filed 2026-08-13](https://www.sec.gov/Archives/edgar/data/1410098/000141009826000054/crmd_q22026earningspr.htm)
- source: [CRMD 10-Q for period 2026-06-30, MD&A, filed 2026-08-13](https://www.sec.gov/Archives/edgar/data/1410098/000141009826000056/crmd-20260630.htm)
- source: [Benzinga: Oppenheimer Initiates Coverage On Cormedix with Outperform Rating, Announces Price Target of $15 (2026-09-23)](https://www.benzinga.com/news/26/09/61940378/oppenheimer-initiates-coverage-cormedix-outperform-rating-announces-price-target-15)

**Thesis**
- A favorable change in accounting estimates boosted first-half 2026 net sales by $9.0 million and net income by $6.1 million, suggesting some of the reported strength is non-recurring and may be discounted by investors.  
  > "For the six months ended June 30, 2026, the resulting changes in accounting estimates positively impacted net sales by $9.0 million, and positively impacted income from continuing operations and net income by $6.1 million, net of taxes, and increased basic and diluted earnings per share by $0.08 and $0.07 per share, respectively." ([CRMD-10Q-2026-08-13-mdna](https://www.sec.gov/Archives/edgar/data/1410098/000141009826000056/crmd-20260630.htm))

**Bear case**
- The company states that new tariffs on imported APIs and packaging materials may adversely affect gross margins and operating results, adding cost pressure to the outlook.  
  > "On April 2, 2026, the U.S. government issued an executive order imposing new tariffs on certain imported goods, including active pharmaceutical ingredients (“APIs”), excipients, and packaging materials commonly used in the pharmaceutical industry. The Company is currently assessing the impact of the tariffs, which may adversely affect our gross margins and operating results." ([CRMD-10Q-2026-08-13-mdna](https://www.sec.gov/Archives/edgar/data/1410098/000141009826000056/crmd-20260630.htm))

*Stripped by the citation check (4):* "The company reported Q2 2026 consolidated revenue of $101.9 million, up from $39" (claim states numbers not in its quote: ['2', '2026']); "The company also reported Q2 2026 net income of $26.0 million and adjusted EBITD" (claim states numbers not in its quote: ['2', '2026']); "The 10-Q discloses that DefenCath's post-TDAPA transition caused reimbursement t" (claim states numbers not in its quote: ['10']); "The company is incurring legal fees for ongoing securities litigation, as it rec" (quote not found verbatim in the cited document)

*model said evidence: sufficient*

## Data limits

- Prices: Alpaca SIP daily bars, split and dividend adjusted; no intraday data used.
- Fundamentals: SEC XBRL companyfacts, US-GAAP filers only. Foreign private issuers (IFRS, 20-F/40-F) and companies without standard tags drop out as 'missing', they are not guessed.
- Market cap uses the latest cover-page share count; for multi-class issuers it can understate.
- Industry groups are SEC SIC codes, a coarse proxy for a theme (no GICS/BICS in free data).
- Short interest: FINRA consolidated short interest (twice monthly, non-commercial use); % is of shares outstanding, not float.
- Earnings-call transcripts are licensed content and were not used; explanations rely on the 8-K earnings release, 10-Q/10-K MD&A, and news headlines and summaries (Alpaca / Benzinga), never full articles.
- No consensus estimates, revisions, ownership or borrow-cost data: those need a licensed source.
