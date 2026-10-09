# Screen: AI suppliers lagging the chip index while revenue accelerates

As of **2026-10-08** (last price date 2026-10-08). Universe: tradable US-listed (NYSE/Nasdaq/AMEX/Arca/BATS) operating companies with an SEC CIK and a 10-K/10-Q/20-F/40-F in the last 18 months; close >= $1; 50-day avg dollar volume >= $1,000,000; one listing per CIK. Model: deepseek / deepseek-v4-pro (translation and prose only; every filter, rank and number below is computed by code).

## 1. Screen spec (proposed by the model, validated by code)

```json
{
  "version": 1,
  "observation": "AI suppliers lagging the chip index while revenue accelerates",
  "universe": {
    "themes": [
      "ai_semis",
      "ai_networking",
      "ai_power"
    ]
  },
  "conditions": [
    {
      "field": "rs_3m_vs_smh",
      "op": "<",
      "value": 0,
      "why": "lagging the chip index"
    },
    {
      "field": "revenue_growth_accel",
      "op": ">",
      "value": 0,
      "why": "revenue accelerates"
    }
  ],
  "rank": [
    {
      "field": "revenue_growth_accel",
      "direction": "desc",
      "weight": 1
    }
  ],
  "top_n": 5,
  "unmapped": [],
  "notes": "Interpreted AI suppliers as the ai_semis, ai_networking, and ai_power theme baskets. Used SMH as the chip index and a 3-month relative return below zero for lagging; revenue acceleration is latest quarter YoY growth minus prior quarter YoY growth."
}
```

## 2. Funnel

| step | in | pass | fail | missing data |
|---|---:|---:|---:|---:|
| universe (liquid US common stocks with SEC filings) | 3827 | 3827 | 0 | 0 |
| theme in ['ai_semis', 'ai_networking', 'ai_power'] | 3827 | 32 | 3795 | 0 |
| rs_3m_vs_smh < +0.0% | 32 | 18 | 14 | 0 |
| revenue_growth_accel > +0.0% | 18 | 12 | 6 | 0 |

## 3. Ranked survivors (12)

| rank | symbol | name | score | market_cap | rs_3m_vs_smh | revenue_growth_accel |
|---|---|---|---|---|---|---|
| 1 | AVGO | Broadcom Inc. | 1.000 | $1,719.2B | -9.2% | +37.6% |
| 2 | AAOI | APPLIED OPTOELECTRONICS, INC. | 0.917 | $9.0B | -11.1% | +35.1% |
| 3 | AMAT | APPLIED MATERIALS INC /DE | 0.833 | $404.4B | -14.7% | +13.4% |
| 4 | COHR | COHERENT CORP. | 0.750 | $59.2B | -6.2% | +13.2% |
| 5 | AMKR | AMKOR TECHNOLOGY, INC. | 0.667 | $12.6B | -26.9% | +11.6% |
| 6 | ALAB | Astera Labs, Inc. | 0.583 | $60.2B | -15.3% | +11.1% |
| 7 | CLS | CELESTICA INC | 0.500 | $41.0B | -0.3% | +9.6% |
| 8 | LRCX | LAM RESEARCH CORP | 0.417 | $401.2B | -7.8% | +6.2% |
| 9 | CSCO | CISCO SYSTEMS, INC. | 0.333 | $453.0B | -4.3% | +5.6% |
| 10 | GEV | GE Vernova Inc. | 0.250 | $266.2B | -7.8% | +5.6% |
| 11 | KLAC | KLA CORP | 0.167 | $257.0B | -14.3% | +3.7% |
| 12 | POWL | POWELL INDUSTRIES INC | 0.083 | $6.9B | -17.8% | +2.4% |

## 4. Why the dislocation might exist (top 5)

Every quote below was checked by code to appear verbatim in the linked SEC document. Claims whose quotes failed the check were removed and are listed.

### AVGO: explained

- source: [AVGO 8-K earnings release (Exhibit 99.1), filed 2026-09-02](https://www.sec.gov/Archives/edgar/data/1730168/000173016826000076/avgo-08022026x8kxex99.htm)
- source: [AVGO 10-Q for period 2026-08-02, MD&A, filed 2026-09-10](https://www.sec.gov/Archives/edgar/data/1730168/000173016826000080/avgo-20260802.htm)
- source: [Benzinga: OpenAI Revenue $20B Below Previous Reports, ORCL, NVDA Tumble (2026-10-08)](https://www.benzinga.com/markets/prediction-markets/26/10/62257221/openai-revenue-run-rate-ai-stocks)
- source: [Benzinga: EXCLUSIVE: TSMC Plans Up to $64 Billion in Capex and Still Isn’t ‘Building Enough,’ Says Applied Materials Veteran (2026-10-08)](https://www.benzinga.com/markets/prediction-markets/26/10/62254694/tsmc-capex-64-billion-building-enough)
- source: [Benzinga: 'Oracle, Broadcom and SpaceX Seek Blockbuster Debt Deals To Pay for AI Chips'- WSJ Exclusive (2026-10-07)](https://www.benzinga.com/news/26/10/62234456/oracle-broadcom-and-spacex-seek-blockbuster-debt-deals-to-pay-for-ai-chips-wsj-exclusive)
- source: [Benzinga: $100 Invested In Broadcom 15 Years Ago Would Be Worth This Much Today (2026-10-07)](https://www.benzinga.com/news/26/10/62235453/100-invested-broadcom-15-years-ago-would-be-worth-much-today)
- source: [Benzinga: Marvell Stock Is Up 230% This Year: Bank of America Sees a Further 40% Upside (2026-10-07)](https://www.benzinga.com/markets/tech/26/10/62228208/marvell-stock-investor-day-up-230-percent-2026-bofa-40-percent-upside)
- source: [Benzinga: What's Going On With Broadcom Stock Wednesday? (2026-10-07)](https://www.benzinga.com/markets/tech/26/10/62215731/whats-going-on-with-broadcom-stock-wednesday-7)
- source: [Benzinga: Challenging Nvidia's Dominance: Broadcom Pairs Custom TPU Chips with $60 Billion Debt Package (2026-10-06)](https://www.benzinga.com/markets/tech/26/10/62200140/challenging-nvidias-dominance-broadcom-pairs-custom-tpu-chips-with-60-billion-debt-package)
- source: [Benzinga: Jim Cramer Sees Marvell Sending a Bigger Signal to Broadcom (2026-10-06)](https://www.benzinga.com/markets/tech/26/10/62198664/jim-cramer-sees-marvell-sending-a-bigger-signal-to-broadcom)
- source: [Benzinga: 'Wall Street banks launch record $60B chip deal for Broadcom and Anthropic'- Financial Times (2026-10-05)](https://www.benzinga.com/news/26/10/62178697/wall-street-banks-launch-record-60b-chip-deal-broadcom-and-anthropic-financial-times)
- source: [Benzinga: Nvidia, Broadcom May Be Surprisingly Safe From a 32-GW Hole in the AI Boom, Morgan Stanley Says (2026-10-05)](https://www.benzinga.com/markets/prediction-markets/26/10/62174172/nvidia-broadcom-ai-power-shortage)
- source: [Benzinga: LinkedIn Cofounder Defends Massive AI Infrastructure Spending, Says AI Capital Is 'the Only Reason We’re Not in a Recession' (2026-10-04)](https://www.benzinga.com/markets/economic-data/26/10/62152166/linkedin-cofounder-defends-massive-ai-infrastructure-spending-says-ai-capital-is-the-only-reason-were-not-in-a-recession)
- source: [Benzinga: Taiwan Semiconductor Stock Rises on Broadcom's $60 Billion Chip Deal (2026-10-02)](https://www.benzinga.com/trading-ideas/movers/26/10/62143884/taiwan-semiconductor-stock-rises-on-broadcoms-60-billion-chip-deal)

**Thesis**
- The company disclosed that direct sales to one distributor accounted for 50% of net revenue, a concentration that may explain the stock's underperformance despite accelerating revenue.  
  > "Direct sales to one semiconductor solutions customer, which is a distributor, accounted for 50% and 46% of our net revenue for the fiscal quarter and three fiscal quarters ended August 2, 2026, respectively, and 32% and 30% of our net revenue for the fiscal quarter and three fiscal quarters ended August 3, 2025, respectively." ([AVGO-10Q-2026-09-10-mdna](https://www.sec.gov/Archives/edgar/data/1730168/000173016826000080/avgo-20260802.htm))
- Broadcom disclosed a maximum potential liability under its AI XPV backstop of approximately $29 billion, which could explain why accelerating revenue did not lift the stock.  
  > "Our maximum potential liability under the Backstop upon the deployment of all AI racks, on an undiscounted basis, was approximately $29 billion." ([AVGO-10Q-2026-09-10-mdna](https://www.sec.gov/Archives/edgar/data/1730168/000173016826000080/avgo-20260802.htm))
- A news report says OpenAI’s annualized revenue is about $20 billion below earlier reports, which may have contributed to Broadcom’s underperformance.  
  > "New figures put OpenAI’s annualized revenue near $50 billion, about $20 billion below earlier reports, as AI stocks fell." ([AVGO-news-2026-10-08-62257221](https://www.benzinga.com/markets/prediction-markets/26/10/62257221/openai-revenue-run-rate-ai-stocks))

**Bear case**
- The company warns that loss of any top-five end customer could materially harm its business, adding downside risk.  
  > "The loss of, or significant decrease in demand from, any of our top five end customers could have a material adverse effect on our business, results of operations and financial condition." ([AVGO-10Q-2026-09-10-mdna](https://www.sec.gov/Archives/edgar/data/1730168/000173016826000080/avgo-20260802.htm))
- The backstop agreement exposes Broadcom to a potential liability of approximately $29 billion if a customer defaults on leases.  
  > "Our maximum potential liability under the Backstop upon the deployment of all AI racks, on an undiscounted basis, was approximately $29 billion." ([AVGO-10Q-2026-09-10-mdna](https://www.sec.gov/Archives/edgar/data/1730168/000173016826000080/avgo-20260802.htm))
- A news report says Broadcom pairs custom TPU chips with a $60 billion debt package, which could raise balance-sheet risk.  
  > "Challenging Nvidia's Dominance: Broadcom Pairs Custom TPU Chips with $60 Billion Debt Package" ([AVGO-news-2026-10-06-62200140](https://www.benzinga.com/markets/tech/26/10/62200140/challenging-nvidias-dominance-broadcom-pairs-custom-tpu-chips-with-60-billion-debt-package))

*model said evidence: sufficient*

### AAOI: explained

- source: [AAOI 8-K earnings release (Exhibit 99.1), filed 2026-08-06](https://www.sec.gov/Archives/edgar/data/1158114/000168316826006055/aaoi_ex9901.htm)
- source: [AAOI 10-Q for period 2026-06-30, MD&A, filed 2026-08-06](https://www.sec.gov/Archives/edgar/data/1158114/000143774926026278/aaoi20260630_10q.htm)
- source: [Benzinga: Applied Optoelectronics Stock Rises on Possible Continued Momentum as It Completes Share Sale (2026-10-06)](https://www.benzinga.com/trading-ideas/movers/26/10/62194091/applied-optoelectronics-stock-rises-on-possible-continued-momentum-as-it-completes-share-sale)
- source: [Benzinga: Applied Optoelectronics Stock Slides Monday: What's Happening? (2026-09-28)](https://www.benzinga.com/trading-ideas/movers/26/09/62035697/applied-optoelectronics-stock-slides-monday-whats-happening)
- source: [Benzinga: Why Is Applied Optoelectronics Stock Surging Tuesday? (2026-09-08)](https://www.benzinga.com/trading-ideas/movers/26/09/61666003/why-is-applied-optoelectronics-stock-surging-tuesday)

**Thesis**
- Despite the revenue growth, the company posted a GAAP net loss that widened sequentially and year over year.  
  > "GAAP net loss was $22.8 million, or $0.28 per basic share, compared with net loss of $9.1 million, or $0.16 per basic share in the second quarter of 2025, and a net loss of $14.3 million, or $0.19 per basic share in the first quarter of 2026." ([AAOI-8K-2026-08-06-ex99](https://www.sec.gov/Archives/edgar/data/1158114/000168316826006055/aaoi_ex9901.htm))
- Gross margin contracted from 30.3% to 27.7% year over year, showing that growth came with lower profitability.  
  > "Gross margin decreased to 27.7% for the three months ended June 30, 2026, compared to 30.3% for the three months ended June 30, 2025." ([AAOI-10Q-2026-08-06-mdna](https://www.sec.gov/Archives/edgar/data/1158114/000143774926026278/aaoi20260630_10q.htm))
- Revenue is highly concentrated, with Digicomm alone representing about 42.8% of total revenue in the first half.  
  > "For the six months ended June 30, 2026, revenues from Digicomm were approximately $147.0 million, representing approximately 42.8% of consolidated revenues. These revenues were primarily attributable to the CATV product category." ([AAOI-10Q-2026-08-06-mdna](https://www.sec.gov/Archives/edgar/data/1158114/000143774926026278/aaoi20260630_10q.htm))

**Bear case**
- The company has no long-term purchase commitments, so the surge in demand may not be durable.  
  > "We do not have any long-term purchase commitments (in excess of one year) with any of our customers, most of whom purchase our products on a purchase order basis." ([AAOI-10Q-2026-08-06-mdna](https://www.sec.gov/Archives/edgar/data/1158114/000143774926026278/aaoi20260630_10q.htm))
- Operating cash flow was negative $73.8 million in the first half, reflecting working capital consumption.  
  > "Net cash used in operating activities was $73.8 million during the six months ended June 30, 2026 as compared to $116.4 million during the six months ended June 30, 2025, a decrease of 36.6%." ([AAOI-10Q-2026-08-06-mdna](https://www.sec.gov/Archives/edgar/data/1158114/000143774926026278/aaoi20260630_10q.htm))
- The company itself flags trade-policy and tariff uncertainty, which could pressure costs and demand.  
  > "At the same time, the global economic environment remains subject to uncertainty resulting from evolving trade policies, tariffs, export controls, geopolitical developments and other macroeconomic factors." ([AAOI-10Q-2026-08-06-mdna](https://www.sec.gov/Archives/edgar/data/1158114/000143774926026278/aaoi20260630_10q.htm))

*Stripped by the citation check (1):* "Revenue grew 86.4% year over year in Q2 2026, a strong fundamental acceleration." (claim states numbers not in its quote: ['2'])

*model said evidence: sufficient*

### AMAT: explained

- source: [AMAT 8-K earnings release (Exhibit 99.1), filed 2026-08-13](https://www.sec.gov/Archives/edgar/data/6951/000162828026056699/exhibit991q32026earningsre.htm)
- source: [AMAT 10-Q for period 2026-07-26, MD&A, filed 2026-08-20](https://www.sec.gov/Archives/edgar/data/6951/000162828026058235/amat-20260726.htm)
- source: [Benzinga: EXCLUSIVE: TSMC Plans Up to $64 Billion in Capex and Still Isn’t ‘Building Enough,’ Says Applied Materials Veteran (2026-10-08)](https://www.benzinga.com/markets/prediction-markets/26/10/62254694/tsmc-capex-64-billion-building-enough)
- source: [Benzinga: New Jersey Rep. Josh Gottheimer Sold Up to $30K Worth of Applied Materials Stock (2026-10-08)](https://www.benzinga.com/government/26/10/62249820/new-jersey-rep-josh-gottheimer-sold-30k-worth-applied-materials-stock)
- source: [Benzinga: Here’s How Much You Would Have Made Owning Applied Materials Stock In The Last 20 Years (2026-10-06)](https://www.benzinga.com/news/26/10/62194124/here-s-how-much-you-would-have-made-owning-applied-materials-stock-last-20-years)
- source: [Benzinga: Applied Materials, Intel Partnering Over Development Of Chipmaking Innovations For Transistors, Interconnects, Packing Technologies (2026-10-06)](https://www.benzinga.com/news/26/10/62189088/applied-materials-intel-partnering-over-development-chipmaking-innovations-transistors-interconnects)
- source: [Benzinga: Applied Materials, BE Semiconductor Industries Announce BE Joins EPIC Center As Innovation Partner (2026-10-01)](https://www.benzinga.com/news/26/10/62105025/applied-materials-be-semiconductor-industries-announce-be-joins-epic-center-innovation-partner)
- source: [Benzinga: What's Going On With Applied Materials Stock Wednesday? (2026-09-30)](https://www.benzinga.com/markets/tech/26/09/62076294/whats-going-on-with-applied-materials-stock-tuesday)
- source: [Benzinga: Applied Materials Says Kioxia Joins Its EPIC Center As Partner To Develop Next-Generation AI Memory Technologies (2026-09-29)](https://www.benzinga.com/quote/AMAT)
- source: [Benzinga: Morgan Stanley Maintains Equal-Weight on Applied Materials, Lowers Price Target to $563 (2026-09-28)](https://www.benzinga.com/news/26/09/62019127/morgan-stanley-maintains-equal-weight-applied-materials-lowers-price-target-563)
- source: [Benzinga: $100 Invested In Applied Materials 20 Years Ago Would Be Worth This Much Today (2026-09-23)](https://www.benzinga.com/news/26/09/61950302/100-invested-applied-materials-20-years-ago-would-be-worth-much-today)
- source: [Benzinga: What's Going On With Applied Materials Stock Friday? (2026-09-18)](https://www.benzinga.com/markets/tech/26/09/61869553/whats-going-on-with-applied-materials-stock-friday)
- source: [Benzinga: Applied Materials To Invest $5B In India Over Next Decade To Deepen Semiconductor R&D (2026-09-17)](https://www.benzinga.com/news/26/09/61834041/applied-materials-invest-5b-india-over-next-decade-deepen-semiconductor-r-d)

**Thesis**
- Applied Materials reported record revenue of $9.12 billion and a GAAP operating margin of 33.7 percent, reflecting strong fundamental performance that contrasts with its negative relative price momentum.  
  > "Applied generated record revenue of $9.12 billion. On a GAAP basis, the company reported gross margin of 50.3 percent, record operating income of $3.08 billion or 33.7 percent of revenue, and earnings per share (EPS) of $3.17." ([AMAT-8K-2026-08-13-ex99](https://www.sec.gov/Archives/edgar/data/6951/000162828026056699/exhibit991q32026earningsre.htm))
- U.S. export regulations have limited Applied Materials' ability to provide certain products and services to customers in China, a risk that may explain why the stock underperformed despite strong results.  
  > "The United States government has implemented export regulations for U.S. semiconductor technology sold or provided to customers in China, which have limited our ability to provide certain products and services to customers in China, over the past several years." ([AMAT-10Q-2026-08-20-mdna](https://www.sec.gov/Archives/edgar/data/6951/000162828026058235/amat-20260726.htm))
- The company's China revenue as a percentage of total revenue fell from 35% to 28% year over year, indicating a shrinking contribution from a key market.  
  > "China $ 2,506 28 % $ 2,548 35 % (2) % $ 6,688 28 % $ 6,565 30 % 2 %" ([AMAT-10Q-2026-08-20-mdna](https://www.sec.gov/Archives/edgar/data/6951/000162828026058235/amat-20260726.htm))

**Bear case**
- A news report says Morgan Stanley maintained an Equal-Weight rating on Applied Materials and lowered its price target to $563, suggesting tempered expectations.  
  > "Morgan Stanley Maintains Equal-Weight on Applied Materials, Lowers Price Target to $563" ([AMAT-news-2026-09-28-62019127](https://www.benzinga.com/news/26/09/62019127/morgan-stanley-maintains-equal-weight-applied-materials-lowers-price-target-563))
- The company's own risk disclosures warn that changes in tariffs, retaliatory measures, and export license requirements could materially affect its results, supporting a cautious view.  
  > "global trade issues, changes in trade and export regulations, license requirements, and their interpretation, and our ability to obtain licenses or authorizations on a timely basis, if at all; changes in tariffs, any retaliatory measures, and our ability to mitigate the impact of tariffs" ([AMAT-8K-2026-08-13-ex99](https://www.sec.gov/Archives/edgar/data/6951/000162828026056699/exhibit991q32026earningsre.htm))
- Applied Materials recorded a $253 million charge to settle an export controls compliance matter with the U.S. Commerce Department, highlighting regulatory risk.  
  > "Charge of $253 million for settlement with the U.S. Commerce Department Bureau of Industry and Security to resolve a previously disclosed export controls compliance matter." ([AMAT-8K-2026-08-13-ex99](https://www.sec.gov/Archives/edgar/data/6951/000162828026056699/exhibit991q32026earningsre.htm))

*model said evidence: sufficient*

### COHR: explained

- source: [COHR 8-K earnings release (Exhibit 99.1), filed 2026-08-12](https://www.sec.gov/Archives/edgar/data/820318/000119312526346860/d128030dex991.htm)
- source: [COHR 10-K for period 2026-06-30, MD&A, filed 2026-08-14](https://www.sec.gov/Archives/edgar/data/820318/000082031826000020/iivi-20260630.htm)
- source: [Benzinga: Nike, Corteva, Mattel, Accenture and Coherent: Why These 5 Stocks Are on Investors' Radars Today (2026-10-02)](https://www.benzinga.com/news/26/10/62125706/nike-corteva-mattel-accenture-and-coherent-why-these-5-stocks-are-on-investors-radars-today)
- source: [Benzinga: Lumentum, Coherent Rip Higher As Washington Targets Chinese Optical Transceivers (2026-10-01)](https://www.benzinga.com/trading-ideas/movers/26/10/62117250/lumentum-coherent-rip-higher-as-washington-targets-chinese-optical-transceivers)
- source: [Benzinga: Bernstein Initiates Coverage On Coherent with Outperform Rating, Announces Price Target of $350 (2026-09-30)](https://www.benzinga.com/news/26/09/62073486/bernstein-initiates-coverage-coherent-outperform-rating-announces-price-target-350)
- source: [Benzinga: If You Invested $1000 In Coherent Stock 20 Years Ago, You Would Have This Much Today (2026-09-29)](https://www.benzinga.com/news/26/09/62068212/if-you-invested-1000-coherent-stock-20-years-ago-you-would-have-much-today)
- source: [Benzinga: Bipartisan Lawmakers Seek to Bar a Chinese AI Data Center Component From Sensitive US Government Systems: ‘We Shouldn’t Rely on China’ (2026-09-26)](https://www.benzinga.com/markets/tech/26/09/62010472/bipartisan-lawmakers-seek-to-bar-a-chinese-ai-data-center-component-from-sensitive-us-government-systems-we-shouldnt-rely-on-china)
- source: [Benzinga: CUbIQ And Coherent Announce Successful Proof-Of-Concept QKD Demonstrator, A Major Milestone Toward Deploying Physical-Layer Security In Existing AI Infrastructure (2026-09-21)](https://www.benzinga.com/quote/COHR)
- source: [Benzinga: Coherent Expands Pluggable Optical Line System Portfolio, With Full C-Band, High-Power Variable-Gain Amplifier Optical Line System In Compact QSFP Form Factor (2026-09-17)](https://www.benzinga.com/news/26/09/61856234/coherent-expands-pluggable-optical-line-system-portfolio-full-c-band-high-power-variable-gain-amplif)
- source: [Benzinga: $100 Invested In Coherent 15 Years Ago Would Be Worth This Much Today (2026-09-08)](https://www.benzinga.com/news/26/09/61673353/100-invested-coherent-15-years-ago-would-be-worth-much-today)

**Thesis**
- Coherent reported Q4 revenue of $2.05B, up 34% Y/Y, indicating strong reported growth.  
  > "Q4 REVENUE OF $2.05B, INCREASED 34% Y/Y AND 42% Y/Y ON A PRO FORMA BASIS" ([COHR-8K-2026-08-12-ex99](https://www.sec.gov/Archives/edgar/data/820318/000119312526346860/d128030dex991.htm))
- Management's guidance for first-quarter fiscal 2027 revenue of $2.2 billion to $2.4 billion implies continued sequential revenue momentum.  
  > "Revenue for the first quarter of fiscal 2027 is expected to be between $2.2 billion and $2.4 billion." ([COHR-8K-2026-08-12-ex99](https://www.sec.gov/Archives/edgar/data/820318/000119312526346860/d128030dex991.htm))
- AI datacenter investments by hyperscalers and cloud providers are significantly boosting demand for Coherent's transceivers, supporting the revenue acceleration.  
  > "The increasing investments by hyperscale and other cloud providers in AI datacenter infrastructures have significantly boosted demand for our datacenter transceivers." ([COHR-10K-2026-08-14-mdna](https://www.sec.gov/Archives/edgar/data/820318/000082031826000020/iivi-20260630.htm))

**Bear case**
- Net cash provided by operating activities was only $79.5 million while additions to property, plant and equipment were $1,102.9 million, indicating heavy investment and negative free cash flow.  
  > "Net cash provided by operating activities

$
79.5

$
633.6

Cash Flows from Investing Activities

Additions to property, plant & equipment

(1,102.9
)

(440.8
)" ([COHR-8K-2026-08-12-ex99](https://www.sec.gov/Archives/edgar/data/820318/000119312526346860/d128030dex991.htm))
- The Lasers reporting unit's fair value exceeds carrying value by only about 8%, leaving goodwill exposed to impairment if assumptions deteriorate.  
  > "For the Lasers reporting unit, as of April 1, 2026, the estimated fair value exceeded the carrying value by approximately 8%. Accordingly, we concluded that goodwill was not impaired; however, the reporting unit remains sensitive to changes in assumptions and future operating performance." ([COHR-10K-2026-08-14-mdna](https://www.sec.gov/Archives/edgar/data/820318/000082031826000020/iivi-20260630.htm))

*Stripped by the citation check (1):* "Inventories nearly doubled from 1,437.6 to 2,581.0, which may signal an overbuil" (quote is 3 words (must be 6-80))

*model said evidence: sufficient*

### AMKR: explained

- source: [AMKR 8-K earnings release (Exhibit 99.1), filed 2026-07-27](https://www.sec.gov/Archives/edgar/data/1047127/000104712726000043/amkr6302026erex-991.htm)
- source: [AMKR 10-Q for period 2026-06-30, MD&A, filed 2026-07-28](https://www.sec.gov/Archives/edgar/data/1047127/000104712726000046/amkr-20260630.htm)
- source: [Benzinga: AI’s Semiconductor Boom Has a Clear Center of Gravity: Taiwan Semiconductor (2026-09-30)](https://www.benzinga.com/markets/tech/26/09/62074203/ais-semiconductor-boom-has-a-clear-center-of-gravity-taiwan-semiconductor)
- source: [Benzinga: Amkor Technology Reveals Phase 2 Of Arizona Advanced Packaging And Test Campus; The Expansion Increases The Project’s Planned Investment To ~$12B (2026-09-08)](https://www.benzinga.com/news/26/09/61674271/amkor-technology-reveals-phase-2-arizona-advanced-packaging-and-test-campus-expansion-increases-proj)

**Thesis**
- The company's capital expenditures more than tripled, with first-half 2026 capex of $688.4 million compared to $226.1 million in the prior year, consuming cash despite accelerating revenue.  
  > "Our capital expenditures totaled $688.4 million for the six months ended June 30, 2026 compared to $226.1 million for the six months ended June 30, 2025." ([AMKR-10Q-2026-07-28-mdna](https://www.sec.gov/Archives/edgar/data/1047127/000104712726000046/amkr-20260630.htm))
- The company issued $1.15 billion of 2031 Notes in May 2026, increasing leverage to fund capital expenditures.  
  > "In May 2026, we issued $1.15 billion of the 2031 Notes. The 2031 Notes were issued pursuant to, and are governed by, an indenture, dated as of May 5, 2026, between us and U.S. Bank Trust Company, National Association, as trustee." ([AMKR-10Q-2026-07-28-mdna](https://www.sec.gov/Archives/edgar/data/1047127/000104712726000046/amkr-20260630.htm))

**Bear case**
- Management's own risk disclosures warn that convertible notes could dilute existing stockholders or adversely affect the stock price.  
  > "terms of our convertible notes could delay or prevent an otherwise beneficial takeover of us, may dilute the ownership interest of existing stockholders or may otherwise adversely affect the price of our common stock;" ([AMKR-8K-2026-07-27-ex99](https://www.sec.gov/Archives/edgar/data/1047127/000104712726000043/amkr6302026erex-991.htm))
- A news report says the Arizona expansion increases the project's planned investment to ~$12B, which may further strain capital resources.  
  > "Amkor Technology Reveals Phase 2 Of Arizona Advanced Packaging And Test Campus; The Expansion Increases The Project’s Planned Investment To ~$12B" ([AMKR-news-2026-09-08-61674271](https://www.benzinga.com/news/26/09/61674271/amkor-technology-reveals-phase-2-arizona-advanced-packaging-and-test-campus-expansion-increases-proj))
- Management says tariff and related trade actions could impact the business, with effects uncertain.  
  > "We continue to monitor the recent changes in global trade policy, including tariffs and related trade actions announced by the U.S. and other countries. The degree to which such tariffs and other related actions impact our business, financial condition and results of operations will depend on future developments, which are uncertain." ([AMKR-10Q-2026-07-28-mdna](https://www.sec.gov/Archives/edgar/data/1047127/000104712726000046/amkr-20260630.htm))

*Stripped by the citation check (2):* "Free cash flow turned deeply negative, falling to -$269,860 thousand in the firs" (claim states numbers not in its quote: ['2026']); "Customer concentration remains high, with the top ten customers accounting for 6" (claim states numbers not in its quote: ['2026'])

*model said evidence: sufficient*

## Data limits

- Prices: Alpaca SIP daily bars, split and dividend adjusted; no intraday data used.
- Fundamentals: SEC XBRL companyfacts, US-GAAP filers only. Foreign private issuers (IFRS, 20-F/40-F) and companies without standard tags drop out as 'missing', they are not guessed.
- Market cap uses the latest cover-page share count; for multi-class issuers it can understate.
- Industry groups are SEC SIC codes, a coarse proxy for a theme (no GICS/BICS in free data).
- Short interest: FINRA consolidated short interest (twice monthly, non-commercial use); % is of shares outstanding, not float.
- Earnings-call transcripts are licensed content and were not used; explanations rely on the 8-K earnings release, 10-Q/10-K MD&A, and news headlines and summaries (Alpaca / Benzinga), never full articles.
- No consensus estimates, revisions, ownership or borrow-cost data: those need a licensed source.
