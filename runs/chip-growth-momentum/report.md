# Screen: Companies worth over 2 billion dollars growing revenue 30% or more, with price above the 200-day average and beating the S&P 500 over 3 months

As of **2026-10-08** (last price date 2026-10-08). Universe: tradable US-listed (NYSE/Nasdaq/AMEX/Arca/BATS) operating companies with an SEC CIK and a 10-K/10-Q/20-F/40-F in the last 18 months; close >= $1; 50-day avg dollar volume >= $1,000,000; one listing per CIK. Model: deepseek / deepseek-v4-pro (translation and prose only; every filter, rank and number below is computed by code).

## 1. Screen spec (proposed by the model, validated by code)

```json
{
  "version": 1,
  "observation": "Companies worth over 2 billion dollars growing revenue 30% or more, with price above the 200-day average and beating the S&P 500 over 3 months",
  "universe": {
    "market_cap_min": 2000000000
  },
  "conditions": [
    {
      "field": "revenue_growth_yoy",
      "op": ">=",
      "value": 0.3,
      "why": "growing revenue 30% or more"
    },
    {
      "field": "close",
      "op": ">",
      "ref": "sma200",
      "why": "price above the 200-day average"
    },
    {
      "field": "rs_3m_vs_spy",
      "op": ">",
      "value": 0,
      "why": "beating the S&P 500 over 3 months"
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
  "notes": "Revenue growth is interpreted as trailing twelve months revenue versus the prior year. After applying the required filters, companies are ranked by revenue growth with higher growth ranked better."
}
```

## 2. Funnel

| step | in | pass | fail | missing data |
|---|---:|---:|---:|---:|
| universe (liquid US common stocks with SEC filings) | 3827 | 3827 | 0 | 0 |
| market_cap >= $2.00B | 3827 | 1902 | 1712 | 213 |
| revenue_growth_yoy >= +30.0% | 1902 | 206 | 1236 | 460 |
| close > sma200 | 206 | 106 | 100 | 0 |
| rs_3m_vs_spy > +0.0% | 106 | 66 | 40 | 0 |

## 3. Ranked survivors (66)

| rank | symbol | name | score | market_cap | revenue_growth_yoy | close | sma200 | rs_3m_vs_spy |
|---|---|---|---|---|---|---|---|---|
| 1 | BMNR | BITMINE IMMERSION TECHNOLOGIES, INC. | 1.000 | $14.5B | +1022.3% | $24.04 | $21.58 | +57.7% |
| 2 | VAL | Valaris Ltd | 0.985 | $5.8B | +548.5% | $83.96 | $82.90 | +5.5% |
| 3 | IBRX | ImmunityBio, Inc. | 0.970 | $10.5B | +192.9% | $9.91 | $7.36 | +17.8% |
| 4 | MU | MICRON TECHNOLOGY INC | 0.955 | $1,169.9B | +167.0% | $1,035.84 | $697.81 | +3.0% |
| 5 | TARS | Tarsus Pharmaceuticals, Inc. | 0.939 | $3.2B | +105.2% | $72.22 | $68.44 | +21.4% |
| 6 | ABCL | AbCellera Biologics Inc. | 0.924 | $3.7B | +101.3% | $12.02 | $6.17 | +74.0% |
| 7 | VG | Venture Global, Inc. | 0.909 | $33.1B | +100.7% | $13.29 | $12.15 | +6.1% |
| 8 | BETA | BETA Technologies, Inc. | 0.894 | $4.8B | +94.4% | $20.50 | $19.80 | +13.0% |
| 9 | CAI | Caris Life Sciences, Inc. | 0.879 | $7.8B | +85.4% | $27.50 | $21.22 | +59.1% |
| 10 | NVDA | NVIDIA CORP | 0.864 | $5,554.6B | +83.4% | $230.48 | $201.60 | +6.6% |
| 11 | LITE | Lumentum Holdings Inc. | 0.848 | $94.1B | +83.2% | $1,048.60 | $760.63 | +28.0% |
| 12 | LPG | DORIAN LPG LTD. | 0.833 | $2.5B | +81.1% | $58.23 | $38.70 | +45.9% |
| 13 | PLTR | Palantir Technologies Inc. | 0.818 | $477.6B | +78.9% | $198.78 | $152.26 | +54.0% |
| 14 | SMCI | Super Micro Computer, Inc. | 0.803 | $28.1B | +77.8% | $42.77 | $32.27 | +48.3% |
| 15 | SM | SM Energy Co | 0.788 | $8.8B | +75.4% | $37.08 | $28.41 | +31.3% |
| 16 | HNI | HNI CORP | 0.773 | $3.4B | +70.1% | $46.91 | $41.00 | +15.5% |
| 17 | DNOW | DNOW Inc. | 0.758 | $2.8B | +69.8% | $15.65 | $13.90 | +17.2% |
| 18 | LTC | LTC PROPERTIES INC | 0.742 | $2.3B | +59.8% | $42.05 | $38.01 | +6.9% |
| 19 | BE | Bloom Energy Corp | 0.727 | $77.6B | +58.3% | $272.82 | $211.49 | +8.8% |
| 20 | TER | TERADYNE, INC | 0.712 | $62.3B | +57.9% | $398.72 | $339.48 | +8.2% |
| 21 | INSW | International Seaways, Inc. | 0.697 | $6.0B | +57.4% | $121.82 | $74.76 | +41.9% |
| 22 | KNSA | Kiniksa Pharmaceuticals International, plc | 0.682 | $6.0B | +56.7% | $78.75 | $56.92 | +21.4% |
| 23 | ARX | Accelerant Holdings | 0.667 | $4.3B | +54.6% | $19.75 | $14.69 | +53.5% |
| 24 | APH | AMPHENOL CORP /DE/ | 0.652 | $105.2B | +54.2% | $85.32 | $74.37 | +4.7% |
| 25 | CLOV | CLOVER HEALTH INVESTMENTS, CORP. /DE | 0.636 | $2.4B | +54.0% | $4.58 | $3.37 | +0.4% |

(41 more in run.json)

## 4. Why the dislocation might exist (top 5)

Every quote below was checked by code to appear verbatim in the linked SEC document. Claims whose quotes failed the check were removed and are listed.

### BMNR: explained

- source: [BMNR 8-K earnings release (Exhibit 99.1), filed 2025-11-21](https://www.sec.gov/Archives/edgar/data/1829311/000149315225024555/ex99-1.htm)
- source: [BMNR 10-Q for period 2026-05-31, MD&A, filed 2026-07-14](https://www.sec.gov/Archives/edgar/data/1829311/000162828026048157/bmnr-20260531.htm)
- source: [Benzinga: Tom Lee Predicts 'Largest Crypto Bull Market Ever' but ETH Craters 5% (2026-10-08)](https://www.benzinga.com/crypto/cryptocurrency/26/10/62252704/tom-lee-predicts-largest-crypto-bull-market-ever-but-eth-craters-5)
- source: [Benzinga: Tom Lee Says Bitmine Will 'Stop' Buying ETH—BMNR Falls 6% (2026-10-07)](https://www.benzinga.com/crypto/cryptocurrency/26/10/62224399/tom-lee-says-bitmine-will-stop-buying-eth-bmnr-falls-6)
- source: [Benzinga: Bitcoin's Rebound Isn't as Strong as It Seems: Watch These Warning Signs (2026-10-06)](https://www.benzinga.com/crypto/cryptocurrency/26/10/62200044/bitcoins-rebound-isnt-as-strong-as-it-seems-watch-these-warning-signs)
- source: [Benzinga: Bitmine Buys 15,112 ETH as BMNR Hits a Make-Or-Break Level (2026-10-05)](https://www.benzinga.com/crypto/cryptocurrency/26/10/62165819/bitmine-buys-15112-eth-as-bmnr-hits-a-make-or-break-level)
- source: [Benzinga: Bitmine Immersion Technologies Announces It Holds 6,016,414 ETH; Total Holdings At $17.4B (2026-10-05)](https://www.benzinga.com/news/26/10/62159927/bitmine-immersion-technologies-announces-it-holds-6-016-414-eth-total-holdings-17-4b)
- source: [Benzinga: Tom Lee’s BitMine Stock Flashes Golden Cross as Ethereum Buying Nears an Inflection Point (2026-10-03)](https://www.benzinga.com/markets/equities/26/10/62151785/tom-lees-bitmine-stock-flashes-a-golden-cross-as-ethereum-buying-nears-an-inflection-point)
- source: [Benzinga: Tom Lee’s Crypto Bull Case Gets an AI Twist as BitMine Stock Flashes a Golden Cross (2026-10-01)](https://www.benzinga.com/crypto/cryptocurrency/26/10/62118618/tom-lee-bmnr-ai-crypto)
- source: [Benzinga: Tom Lee Asks Investors, 'Do You Have Enough Crypto,' After Changpeng Zhao Hints Bull Market Could Come 'Soon' (2026-09-30)](https://www.benzinga.com/crypto/cryptocurrency/26/09/62069673/tom-lee-changpeng-zhao-crypto-bull-market-soon)
- source: [Benzinga: Bitmine Buys 17,362 ETH as BMNR Stock Holds $27 (2026-09-28)](https://www.benzinga.com/crypto/cryptocurrency/26/09/62024785/bitmine-buys-17362-eth-as-bmnr-stock-holds-27)
- source: [Benzinga: Bitmine Says It Holds 6,001,302 ETH After Buying 17,362 In Past Week; Total Holdings At $17.2B (2026-09-28)](https://www.benzinga.com/quote/BMNR)
- source: [Benzinga: Ethereum Exchange Supply Hits Record Low as ETH Gains 10% — Is a Correction Next? (2026-09-25)](https://www.benzinga.com/crypto/cryptocurrency/26/09/61998408/ethereum-exchange-supply-hits-record-low-as-eth-gains-10-is-a-correction-next)
- source: [Benzinga: Why Is BitMine Stock Falling Wednesday? (2026-09-23)](https://www.benzinga.com/trading-ideas/movers/26/09/61956108/why-is-bitmine-stock-falling-wednesday)

**Thesis**
- The reported revenue growth comes from a tiny base, as revenues rose from $2,052 to $46,535 year over year, making the percentage increase misleading.  
  > "During the three months ended May 31, 2026, revenues were $46,535, compared to $2,052 during the three months ended May 31, 2025." ([BMNR-10Q-2026-07-14-mdna](https://www.sec.gov/Archives/edgar/data/1829311/000162828026048157/bmnr-20260531.htm))
- A news report says Bitmine bought 15,112 Ethereum, lifting holdings to 6.02 million ETH, which may have supported the stock price despite weak reported financials.  
  > "Bitmine buys 15,112 Ethereum, lifting holdings to 6.02 million ETH as Tom Lee says the company beat the crypto bear market." ([BMNR-news-2026-10-05-62165819](https://www.benzinga.com/crypto/cryptocurrency/26/10/62165819/bitmine-buys-15112-eth-as-bmnr-hits-a-make-or-break-level))

**Bear case**
- The company's nine-month net loss was $9,106,103, compared to a net loss of $2,754 in the prior-year period, showing significant deterioration.  
  > "Net loss $ (9,106,103) $ (2,754) NM" ([BMNR-10Q-2026-07-14-mdna](https://www.sec.gov/Archives/edgar/data/1829311/000162828026048157/bmnr-20260531.htm))
- The company recorded a net loss on derivative contracts of $92,093 in the most recent quarter, adding significant operational losses.  
  > "During the three months ended May 31, 2026, the Company recognized a net loss on derivative contracts of $(92,093)" ([BMNR-10Q-2026-07-14-mdna](https://www.sec.gov/Archives/edgar/data/1829311/000162828026048157/bmnr-20260531.htm))
- The company has very limited cash and working capital relative to its market capitalization, with only $340,289 in cash and working capital of $433,123, raising liquidity concerns.  
  > "As of May 31, 2026, the Company had $340,289 in cash on hand and working capital of $433,123." ([BMNR-10Q-2026-07-14-mdna](https://www.sec.gov/Archives/edgar/data/1829311/000162828026048157/bmnr-20260531.htm))

*Stripped by the citation check (1):* "While revenue grew, the company's general and administrative expenses of $37,270" (claim states numbers not in its quote: ['46535'])

*model said evidence: sufficient*

### VAL: explained

- source: [VAL 8-K earnings release (Exhibit 99.1), filed 2026-08-05](https://www.sec.gov/Archives/edgar/data/314808/000031480826000138/a06302026ex991pressrelease.htm)
- source: [VAL 10-Q for period 2026-06-30, MD&A, filed 2026-08-06](https://www.sec.gov/Archives/edgar/data/314808/000031480826000141/val-20260630.htm)
- source: [Benzinga: Valaris Announces About $220M Of Backlog From New Contracts And Extensions, Including Petronas Drillship Contract Offshore Suriname (2026-10-07)](https://www.benzinga.com/quote/VAL)
- source: [Benzinga: Susquehanna Maintains Neutral on Valaris, Raises Price Target to $86 (2026-10-05)](https://www.benzinga.com/news/26/10/62164574/susquehanna-maintains-neutral-valaris-raises-price-target-86)
- source: [Benzinga: Valaris Says U.S. DOJ Closes Antitrust Investigation Into Valaris And Transocean Deal; Co And Transocean Expect Business Combination To Close In Q4 2026 (2026-09-30)](https://www.benzinga.com/news/26/09/62094961/valaris-says-u-s-doj-closes-antitrust-investigation-valaris-and-transocean-deal-co-and-transocean-ex)

**Thesis**
- A news report says Valaris announced about $220M of backlog from new contracts and extensions, including a Petronas drillship contract offshore Suriname, which may be a positive catalyst.  
  > "Valaris Announces About $220M Of Backlog From New Contracts And Extensions, Including Petronas Drillship Contract Offshore Suriname" ([VAL-news-2026-10-07-62212329](https://www.benzinga.com/quote/VAL))
- A news report says the U.S. DOJ closed its antitrust investigation into the Valaris and Transocean deal and both companies expect the business combination to close in Q4 2026, which may support the stock.  
  > "Valaris Says U.S. DOJ Closes Antitrust Investigation Into Valaris And Transocean Deal; Co And Transocean Expect Business Combination To Close In Q4 2026" ([VAL-news-2026-09-30-62094961](https://www.benzinga.com/news/26/09/62094961/valaris-says-u-s-doj-closes-antitrust-investigation-valaris-and-transocean-deal-co-and-transocean-ex))

**Bear case**
- Ongoing Middle East conflicts negatively impacted second-quarter Adjusted EBITDA by approximately $30 million, adding cost pressure.  
  > "The ongoing conflicts in the Middle East negatively impacted Adjusted EBITDA by approximately $30 million compared to $8 million in the first quarter" ([VAL-8K-2026-08-05-ex99](https://www.sec.gov/Archives/edgar/data/314808/000031480826000138/a06302026ex991pressrelease.htm))
- The company will not hold future earnings conference calls or provide forward-looking guidance updates due to the pending Transocean combination, reducing transparency.  
  > "In connection with the pending business combination with Transocean Ltd., announced on February 9, 2026, Valaris does not intend to hold future earnings conference calls or provide updates to forward-looking guidance." ([VAL-8K-2026-08-05-ex99](https://www.sec.gov/Archives/edgar/data/314808/000031480826000138/a06302026ex991pressrelease.htm))

*Stripped by the citation check (3):* "The company's consolidated statement of operations shows total operating revenue" (claim states numbers not in its quote: ['2', '2025', '2026']); "The company's revenues exclusive of reimbursable items increased sequentially fr" (claim states numbers not in its quote: ['2']); "Net cash provided by operating activities fell to $88.1 million in the first six" (claim states numbers not in its quote: ['2026'])

*model said evidence: sufficient*

### IBRX: explained

- source: [IBRX 8-K earnings release (Exhibit 99.1), filed 2026-08-04](https://www.sec.gov/Archives/edgar/data/1326110/000132611026000077/ibrx-202684x8kexhibit991.htm)
- source: [IBRX 10-Q for period 2026-06-30, MD&A, filed 2026-08-04](https://www.sec.gov/Archives/edgar/data/1326110/000132611026000079/ibrx-20260630.htm)
- source: [Benzinga: ImmunityBio Stock Jumps: What's Going On? (2026-10-02)](https://www.benzinga.com/trading-ideas/movers/26/10/62142450/immunitybio-stock-jumps-whats-going-on)

**Thesis**
- The company reported record Q2 2026 net product revenue of $50.7 million, up 92% year-over-year and 15% sequentially, marking the eighth consecutive quarter of sequential growth.  
  > "Q2 2026 net product revenue of $50.7 million, up 92% year-over-year and 15% sequentially from Q1 2026, marking the eighth consecutive quarter of sequential revenue growth since the commercial launch of ANKTIVA®, driven by continued adoption among U.S. urologists and strong market access" ([IBRX-8K-2026-08-04-ex99](https://www.sec.gov/Archives/edgar/data/1326110/000132611026000077/ibrx-202684x8kexhibit991.htm))
- In July 2026, the UAE granted the broadest marketing authorization for ANKTIVA across BCG-unresponsive NMIBC and metastatic NSCLC.  
  > "In July 2026, we announced the Emirates Drug Establishment of the United Arab Emirates granted the broadest marketing authorization for ANKTIVA across BCG-unresponsive NMIBC for CIS and papillary disease and metastatic NSCLC" ([IBRX-8K-2026-08-04-ex99](https://www.sec.gov/Archives/edgar/data/1326110/000132611026000077/ibrx-202684x8kexhibit991.htm))
- The FDA accepted for review the sBLA for ANKTIVA plus BCG in papillary disease without CIS, with a PDUFA date of January 6, 2027.  
  > "The FDA accepted for review the Company’s supplemental Biologics License Application (sBLA) for ANKTIVA plus BCG in patients with BCG-unresponsive NMIBC with papillary disease without CIS and assigned a PDUFA target action date of January 6, 2027" ([IBRX-8K-2026-08-04-ex99](https://www.sec.gov/Archives/edgar/data/1326110/000132611026000077/ibrx-202684x8kexhibit991.htm))

**Bear case**
- Net loss attributable to common stockholders was $863.2 million for the first half of 2026, versus $222.2 million in the prior-year period.  
  > "Net loss attributable to ImmunityBio common stockholders was $863.2 million during the six months ended June 30, 2026, compared to $222.2 million during the six months ended June 30, 2025." ([IBRX-8K-2026-08-04-ex99](https://www.sec.gov/Archives/edgar/data/1326110/000132611026000077/ibrx-202684x8kexhibit991.htm))

*Stripped by the citation check (2):* "Net loss attributable to common stockholders increased to $230.4 million in Q2 2" (claim states numbers not in its quote: ['2']); "The company's balance sheet shows a total stockholders' deficit of $1,046,629 th" (claim states numbers not in its quote: ['2025', '2026', '30'])

*model said evidence: sufficient*

### MU: explained

- source: [MU 8-K earnings release (Exhibit 99.1), filed 2026-09-30](https://www.sec.gov/Archives/edgar/data/723125/000072312526000018/a2026q4ex991-pressrelease.htm)
- source: [MU 10-Q for period 2026-05-28, MD&A, filed 2026-06-25](https://www.sec.gov/Archives/edgar/data/723125/000072312526000015/mu-20260528.htm)
- source: [Benzinga: Micron Analyst Sees Stock Nearly Tripling to $3,000, Warns Short Sellers: 'You Have an Expiry' (2026-10-08)](https://www.benzinga.com/markets/prediction-markets/26/10/62256022/micron-stock-3000-price-target-short-sellers)
- source: [Benzinga: Watching Micron Technology; Hearing Investor Business Daily SwingTrader Sells Stock (2026-10-08)](https://www.benzinga.com/quote/MU)
- source: [Benzinga: What's Going On With Micron Technology Stock Thursday? (2026-10-08)](https://www.benzinga.com/markets/tech/26/10/62252561/whats-going-on-with-micron-technology-stock-thursday-7)
- source: [Benzinga: Samsung's Q3 Profit Guidance Tops Analyst Estimates As AI Demand Outstrips Memory Supply (2026-10-08)](https://www.benzinga.com/markets/earnings/26/10/62236247/samsung-third-quarter-guidance-profit-sales-ai-memory-demand)
- source: [Benzinga: Applied Digital, Webull Corp., Super Micro Computer, Micron and Caterpillar: Why These 5 Stocks Are on Investors' Radars Today (2026-10-08)](https://www.benzinga.com/markets/equities/26/10/62236166/applied-digital-webull-super-micro-micron-caterpillar-stocks-investors-radar)
- source: [Benzinga: Micron Stock Falls Amid Chip-Sector Slump as Taiwan Union Votes 99% for Strike Authorization (2026-10-07)](https://www.benzinga.com/trading-ideas/movers/26/10/62216483/micron-stock-falls-amid-chip-sector-slump-as-taiwan-union-votes-99-for-strike-authorization)
- source: [Benzinga: Reported Earlier, 'Micron Tech chipmaker union in Taiwan gets OK to strike' - Reuters (2026-10-07)](https://www.benzinga.com/news/26/10/62215976/reported-earlier-micron-tech-chipmaker-union-taiwan-gets-ok-strike-reuters)
- source: [Benzinga: DA Davidson Maintains Buy on Micron Technology, Raises Price Target to $3000 (2026-10-07)](https://www.benzinga.com/news/26/10/62213009/da-davidson-maintains-buy-micron-technology-raises-price-target-3000)
- source: [Benzinga: First Samsung, Now Micron: Netlist’s Patent Offensive Unlocks Another $600 Million (2026-10-07)](https://www.benzinga.com/markets/tech/26/10/62210782/first-samsung-now-micron-netlists-patent-offensive-unlocks-another-600-million)
- source: [Benzinga: MU, SNDK, SKHY Stocks Decline on Toshiba Storage Fears: Researcher Points to Cantor Note Calling the Pullback a 'Buying Opportunity' (2026-10-07)](https://www.benzinga.com/markets/equities/26/10/62209966/mu-sndk-skhy-stocks-decline-on-toshiba-storage-fears-researcher-points-to-cantor-note-calling-the-pullback-a-buying-opportunity)
- source: [Benzinga: Micron’s AI Memory Boom Could Spark $100 Billion Cash Windfall, Says JPMorgan (2026-10-06)](https://www.benzinga.com/trading-ideas/long-ideas/26/10/62200556/micron-ai-100b-cash-windfall)
- source: [Benzinga: Here's How Much $1000 Invested In Micron Technology 15 Years Ago Would Be Worth Today (2026-10-06)](https://www.benzinga.com/news/26/10/62197446/here-s-how-much-1000-invested-micron-technology-15-years-ago-would-be-worth-today)

**Thesis**
- Management stated that AI-driven demand and strong operational execution position Micron for a record fiscal 2027.  
  > "AI-driven demand and strong operational execution position Micron for a record fiscal 2027" ([MU-8K-2026-09-30-ex99](https://www.sec.gov/Archives/edgar/data/723125/000072312526000018/a2026q4ex991-pressrelease.htm))
- The company reported that AI-driven memory and storage growth is outpacing industry supply, indicating continued demand strength.  
  > "AI-driven memory and storage growth is outpacing industry supply." ([MU-10Q-2026-06-25-mdna](https://www.sec.gov/Archives/edgar/data/723125/000072312526000015/mu-20260528.htm))

**Bear case**
- A news report said Micron stock fell amid a chip-sector slump as a Taiwan union voted 99% for strike authorization, a potential labor disruption.  
  > "Micron Stock Falls Amid Chip-Sector Slump as Taiwan Union Votes 99% for Strike Authorization" ([MU-news-2026-10-07-62216483](https://www.benzinga.com/trading-ideas/movers/26/10/62216483/micron-stock-falls-amid-chip-sector-slump-as-taiwan-union-votes-99-for-strike-authorization))
- A news report said Micron agreed to pay Netlist $600 million in a patent settlement, a one-time cash outflow that could weigh on near-term results.  
  > "Micron agrees to pay Netlist $600M in a landmark patent settlement." ([MU-news-2026-10-07-62210782](https://www.benzinga.com/markets/tech/26/10/62210782/first-samsung-now-micron-netlists-patent-offensive-unlocks-another-600-million))

*Stripped by the citation check (1):* "Micron reported fourth-quarter fiscal 2026 revenue of $54.23 billion, up from $1" (claim states numbers not in its quote: ['2026'])

*model said evidence: sufficient*

### TARS: explained

- source: [TARS 8-K earnings release (Exhibit 99.1), filed 2026-08-06](https://www.sec.gov/Archives/edgar/data/1819790/000181979026000063/exhibit991tarsus862026.htm)
- source: [TARS 10-Q for period 2026-06-30, MD&A, filed 2026-08-06](https://www.sec.gov/Archives/edgar/data/1819790/000181979026000064/tars-20260630.htm)
- source: [Benzinga: Tarsus Pharmaceuticals To Present 11 Abstracts On XDEMVY, Demodex Blepharitis, And Ocular Rosacea At American Academy Of Optometry Meeting (2026-09-29)](https://www.benzinga.com/quote/TARS)
- source: [Benzinga: Goldman Sachs Reinstates Buy on Tarsus Pharmaceuticals, Announces $116 Price Target (2026-09-24)](https://www.benzinga.com/news/26/09/61967829/goldman-sachs-reinstates-buy-tarsus-pharmaceuticals-announces-116-price-target)
- source: [Benzinga: Barclays Reinstates Overweight on Tarsus Pharmaceuticals, Announces $110 Price Target (2026-09-16)](https://www.benzinga.com/news/26/09/61813452/barclays-reinstates-overweight-tarsus-pharmaceuticals-announces-110-price-target)
- source: [Benzinga: Jefferies Maintains Buy on Tarsus Pharmaceuticals, Raises Price Target to $105 (2026-09-08)](https://www.benzinga.com/news/26/09/61670050/jefferies-maintains-buy-tarsus-pharmaceuticals-raises-price-target-105)

**Thesis**
- The company reported second quarter 2026 XDEMVY net product sales of $173.9 million, up more than 69% year-over-year, which likely contributes to the apparent dislocation.  
  > "Generated second quarter 2026 XDEMVY® net product sales of $173.9 million, an increase of more than 69% year-over-year" ([TARS-8K-2026-08-06-ex99](https://www.sec.gov/Archives/edgar/data/1819790/000181979026000063/exhibit991tarsus862026.htm))
- Management raised full-year 2026 XDEMVY net product sales guidance to $685-705 million, signaling continued commercial momentum.  
  > "Increased full-year 2026 XDEMVY net product sales guidance to $685-705 million" ([TARS-8K-2026-08-06-ex99](https://www.sec.gov/Archives/edgar/data/1819790/000181979026000063/exhibit991tarsus862026.htm))
- The pending Alkeus acquisition adds a Phase 3 program for Stargardt disease, expanding the company's retina pipeline.  
  > "Pending acquisition of Alkeus Pharmaceuticals to expand Tarsus’ retina pipeline with a Phase 3 clinical program for Stargardt disease, an inherited retinal disease affecting more than 36,000 patients in the United States that can lead to blindness" ([TARS-8K-2026-08-06-ex99](https://www.sec.gov/Archives/edgar/data/1819790/000181979026000063/exhibit991tarsus862026.htm))
- A news report says Goldman Sachs reinstated a Buy rating and announced a $116 price target, which may support the stock's positive relative strength.  
  > "Goldman Sachs Reinstates Buy on Tarsus Pharmaceuticals, Announces $116 Price Target" ([TARS-news-2026-09-24-61967829](https://www.benzinga.com/news/26/09/61967829/goldman-sachs-reinstates-buy-tarsus-pharmaceuticals-announces-116-price-target))

**Bear case**
- Despite strong sales growth, the company still reported a net loss of $18.6 million for the second quarter, so profitability is not yet established.  
  > "Net loss: was $18.6 million, compared to $20.3 million for the same period in 2025. Basic and diluted net loss per share was $(0.43), compared with $(0.48) for the same period in 2025." ([TARS-8K-2026-08-06-ex99](https://www.sec.gov/Archives/edgar/data/1819790/000181979026000063/exhibit991tarsus862026.htm))
- Selling, general and administrative expenses rose to $150.7 million from $103.0 million year-over-year, showing that commercial spending is climbing sharply.  
  > "Selling, general and administrative (SG&A) expenses: were $150.7 million compared to $103.0 million for the same period in 2025." ([TARS-8K-2026-08-06-ex99](https://www.sec.gov/Archives/edgar/data/1819790/000181979026000063/exhibit991tarsus862026.htm))
- The company's own risk disclosure states it is heavily dependent on continued successful commercialization of XDEMVY, creating concentration risk for the investment.  
  > "Tarsus is heavily dependent on the continued successful commercialization of its lead product, XDEMVY for the treatment of Demodex blepharitis and the successful development, regulatory approval and commercialization of its current and future product candidates;" ([TARS-8K-2026-08-06-ex99](https://www.sec.gov/Archives/edgar/data/1819790/000181979026000063/exhibit991tarsus862026.htm))

*model said evidence: sufficient*

## Data limits

- Prices: Alpaca SIP daily bars, split and dividend adjusted; no intraday data used.
- Fundamentals: SEC XBRL companyfacts, US-GAAP filers only. Foreign private issuers (IFRS, 20-F/40-F) and companies without standard tags drop out as 'missing', they are not guessed.
- Market cap uses the latest cover-page share count; for multi-class issuers it can understate.
- Industry groups are SEC SIC codes, a coarse proxy for a theme (no GICS/BICS in free data).
- Short interest: FINRA consolidated short interest (twice monthly, non-commercial use); % is of shares outstanding, not float.
- Earnings-call transcripts are licensed content and were not used; explanations rely on the 8-K earnings release, 10-Q/10-K MD&A, and news headlines and summaries (Alpaca / Benzinga), never full articles.
- No consensus estimates, revisions, ownership or borrow-cost data: those need a licensed source.
