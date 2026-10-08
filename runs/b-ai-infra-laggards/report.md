# Screen: AI-infrastructure suppliers (semis, networking, power, data-center REITs and neoclouds) whose shares lag the semiconductor index over 3 months while revenue growth is accelerating.

As of **2026-10-08** (last price date 2026-10-08). Universe: tradable US-listed (NYSE/Nasdaq/AMEX/Arca/BATS) operating companies with an SEC CIK and a 10-K/10-Q/20-F/40-F in the last 18 months; close >= $1; 50-day avg dollar volume >= $1,000,000; one listing per CIK. Model: deepseek / deepseek-v4-pro (translation and prose only; every filter, rank and number below is computed by code).

## 1. Screen spec (proposed by the model, validated by code)

```json
{
  "version": 1,
  "observation": "AI-infrastructure suppliers (semis, networking, power, data-center REITs and neoclouds) whose shares lag the semiconductor index over 3 months while revenue growth is accelerating.",
  "universe": {
    "themes": [
      "ai_semis",
      "ai_networking",
      "ai_power",
      "data_center_reits",
      "neoclouds"
    ]
  },
  "conditions": [
    {
      "field": "rs_3m_vs_soxx",
      "op": "<",
      "value": 0,
      "why": "shares lag the semiconductor index over 3 months"
    },
    {
      "field": "revenue_growth_accel",
      "op": ">",
      "value": 0,
      "why": "revenue growth is accelerating"
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
  "notes": "SOXX is used as the semiconductor index. The AI-infrastructure supplier universe is defined by the listed curated theme baskets, which include the named segments. No explicit ranking was requested, so results are ranked by revenue growth acceleration to surface the most accelerating names among the filtered set."
}
```

## 2. Funnel

| step | in | pass | fail | missing data |
|---|---:|---:|---:|---:|
| universe (liquid US common stocks with SEC filings) | 3827 | 3827 | 0 | 0 |
| theme in ['ai_semis', 'ai_networking', 'ai_power', 'data_center_reits', 'neoclouds'] | 3827 | 38 | 3789 | 0 |
| rs_3m_vs_soxx < +0.0% | 38 | 20 | 18 | 0 |
| revenue_growth_accel > +0.0% | 20 | 13 | 6 | 1 |

## 3. Ranked survivors (13)

| rank | symbol | name | score | market_cap | rs_3m_vs_soxx | revenue_growth_accel |
|---|---|---|---|---|---|---|
| 1 | AVGO | Broadcom Inc. | 1.000 | $1,719.2B | -6.8% | +37.6% |
| 2 | AAOI | APPLIED OPTOELECTRONICS, INC. | 0.923 | $9.0B | -8.6% | +35.1% |
| 3 | AMAT | APPLIED MATERIALS INC /DE | 0.846 | $404.4B | -12.3% | +13.4% |
| 4 | COHR | COHERENT CORP. | 0.769 | $59.2B | -3.8% | +13.2% |
| 5 | AMKR | AMKOR TECHNOLOGY, INC. | 0.692 | $12.6B | -24.5% | +11.6% |
| 6 | ALAB | Astera Labs, Inc. | 0.615 | $60.2B | -12.9% | +11.1% |
| 7 | EQIX | EQUINIX INC | 0.538 | $99.8B | -0.3% | +6.5% |
| 8 | LRCX | LAM RESEARCH CORP | 0.462 | $401.2B | -5.3% | +6.2% |
| 9 | CSCO | CISCO SYSTEMS, INC. | 0.385 | $453.0B | -1.9% | +5.6% |
| 10 | GEV | GE Vernova Inc. | 0.308 | $266.2B | -5.4% | +5.6% |
| 11 | KLAC | KLA CORP | 0.231 | $257.0B | -11.9% | +3.7% |
| 12 | POWL | POWELL INDUSTRIES INC | 0.154 | $6.9B | -15.4% | +2.4% |
| 13 | CRWV | CoreWeave, Inc. | 0.077 | $45.0B | -5.2% | +0.8% |

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
- Broadcom reported third-quarter revenue of $29.6 billion, up 86 percent from the prior year period, indicating strong fundamental growth despite the stock's underperformance.  
  > "Revenue of $29.6 billion for the third quarter, up 86 percent from the prior year period" ([AVGO-8K-2026-09-02-ex99](https://www.sec.gov/Archives/edgar/data/1730168/000173016826000076/avgo-08022026x8kxex99.htm))
- Broadcom's AI semiconductor revenue grew 221% year-over-year to $16.7 billion in the third quarter, driving the reported revenue acceleration.  
  > "Q3 AI semiconductor revenue of $16.7 billion grew 221% year-over-year, and 54% quarter-over-quarter" ([AVGO-8K-2026-09-02-ex99](https://www.sec.gov/Archives/edgar/data/1730168/000173016826000076/avgo-08022026x8kxex99.htm))
- The company states that deploying AI infrastructure to meet demand requires customers to access significant capital, a financing dependency that may explain investor caution.  
  > "deploying AI infrastructure to meet this demand requires our customers to access significant capital" ([AVGO-10Q-2026-09-10-mdna](https://www.sec.gov/Archives/edgar/data/1730168/000173016826000080/avgo-20260802.htm))
- A news report says OpenAI's annualized revenue was about $20 billion below earlier reports, as AI stocks fell, which could explain sector-wide price pressure on Broadcom.  
  > "New figures put OpenAI’s annualized revenue near $50 billion, about $20 billion below earlier reports, as AI stocks fell." ([AVGO-news-2026-10-08-62257221](https://www.benzinga.com/markets/prediction-markets/26/10/62257221/openai-revenue-run-rate-ai-stocks))

**Bear case**
- Broadcom's revenue is highly concentrated, with a single distributor customer accounting for 50% of net revenue in the fiscal quarter.  
  > "Direct sales to one semiconductor solutions customer, which is a distributor, accounted for 50% and 46% of our net revenue for the fiscal quarter and three fiscal quarters ended August 2, 2026, respectively" ([AVGO-10Q-2026-09-10-mdna](https://www.sec.gov/Archives/edgar/data/1730168/000173016826000080/avgo-20260802.htm))
- Broadcom's AI XPV platform exposes the company to a maximum backstop liability of approximately $29 billion if the customer defaults.  
  > "Our maximum potential liability under the Backstop upon the deployment of all AI racks, on an undiscounted basis, was approximately $29 billion." ([AVGO-10Q-2026-09-10-mdna](https://www.sec.gov/Archives/edgar/data/1730168/000173016826000080/avgo-20260802.htm))
- A news report says Broadcom is among companies seeking blockbuster debt deals to pay for AI chips, increasing financial leverage risk.  
  > "'Oracle, Broadcom and SpaceX Seek Blockbuster Debt Deals To Pay for AI Chips'- WSJ Exclusive" ([AVGO-news-2026-10-07-62234456](https://www.benzinga.com/news/26/10/62234456/oracle-broadcom-and-spacex-seek-blockbuster-debt-deals-to-pay-for-ai-chips-wsj-exclusive))

*model said evidence: sufficient*

### AAOI: explained

- source: [AAOI 8-K earnings release (Exhibit 99.1), filed 2026-08-06](https://www.sec.gov/Archives/edgar/data/1158114/000168316826006055/aaoi_ex9901.htm)
- source: [AAOI 10-Q for period 2026-06-30, MD&A, filed 2026-08-06](https://www.sec.gov/Archives/edgar/data/1158114/000143774926026278/aaoi20260630_10q.htm)
- source: [Benzinga: Applied Optoelectronics Stock Rises on Possible Continued Momentum as It Completes Share Sale (2026-10-06)](https://www.benzinga.com/trading-ideas/movers/26/10/62194091/applied-optoelectronics-stock-rises-on-possible-continued-momentum-as-it-completes-share-sale)
- source: [Benzinga: Applied Optoelectronics Stock Slides Monday: What's Happening? (2026-09-28)](https://www.benzinga.com/trading-ideas/movers/26/09/62035697/applied-optoelectronics-stock-slides-monday-whats-happening)
- source: [Benzinga: Why Is Applied Optoelectronics Stock Surging Tuesday? (2026-09-08)](https://www.benzinga.com/trading-ideas/movers/26/09/61666003/why-is-applied-optoelectronics-stock-surging-tuesday)

**Thesis**
- Although revenue increased sharply year over year, GAAP net loss widened to $22.8 million from $9.1 million, which may explain why the stock underperformed despite strong sales growth.  
  > "GAAP net loss was $22.8 million, or $0.28 per basic share, compared with net loss of $9.1 million, or $0.16 per basic share in the second quarter of 2025, and a net loss of $14.3 million, or $0.19 per basic share in the first quarter of 2026." ([AAOI-8K-2026-08-06-ex99](https://www.sec.gov/Archives/edgar/data/1158114/000168316826006055/aaoi_ex9901.htm))
- The company's gross margin declined to 27.7% from 30.3% a year earlier, indicating that revenue growth is coming at the cost of profitability, a potential reason for investor skepticism.  
  > "GAAP gross margin was 27.7%, compared with 30.3% in the second quarter of 2025 and 29.1% in the first quarter of 2026." ([AAOI-8K-2026-08-06-ex99](https://www.sec.gov/Archives/edgar/data/1158114/000168316826006055/aaoi_ex9901.htm))
- The company issued a large number of shares through at-the-market offerings, which may have pressured the stock price despite strong fundamentals.  
  > "On April 2, 2026, the Company completed the First ATM Offering and sold approximately 4.8 million shares at a weighted average price of $103.51 per share, providing proceeds of approximately $490 million, net of expenses and underwriting discounts and commissions." ([AAOI-10Q-2026-08-06-mdna](https://www.sec.gov/Archives/edgar/data/1158114/000143774926026278/aaoi20260630_10q.htm))
- A news report says the stock slid alongside the broader fiber optic connectivity sector, suggesting sector-wide pressure rather than company-specific bad news.  
  > "Applied Optoelectronics shares fall Monday afternoon, sliding alongside the broader fiber optic connectivity sector." ([AAOI-news-2026-09-28-62035697](https://www.benzinga.com/trading-ideas/movers/26/09/62035697/applied-optoelectronics-stock-slides-monday-whats-happening))

**Bear case**
- Net cash used in operating activities was $73.8 million in the first half of 2026, meaning the company is still consuming cash despite rapid revenue growth.  
  > "Net cash used in operating activities was $73.8 million during the six months ended June 30, 2026 as compared to $116.4 million during the six months ended June 30, 2025, a decrease of 36.6%." ([AAOI-10Q-2026-08-06-mdna](https://www.sec.gov/Archives/edgar/data/1158114/000143774926026278/aaoi20260630_10q.htm))
- The company's GAAP net loss widened to $22.8 million from $9.1 million a year earlier, indicating profitability remains elusive.  
  > "GAAP net loss was $22.8 million, or $0.28 per basic share, compared with net loss of $9.1 million, or $0.16 per basic share in the second quarter of 2025, and a net loss of $14.3 million, or $0.19 per basic share in the first quarter of 2026." ([AAOI-8K-2026-08-06-ex99](https://www.sec.gov/Archives/edgar/data/1158114/000168316826006055/aaoi_ex9901.htm))
- Revenues from a single customer, Digicomm, represented approximately 42.8% of consolidated revenues, exposing the company to significant customer concentration risk.  
  > "For the six months ended June 30, 2026, revenues from Digicomm were approximately $147.0 million, representing approximately 42.8% of consolidated revenues." ([AAOI-10Q-2026-08-06-mdna](https://www.sec.gov/Archives/edgar/data/1158114/000143774926026278/aaoi20260630_10q.htm))

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
- Applied reported record revenue of $9.12 billion, up 25 percent year over year, while its stock underperformed peers, suggesting a dislocation driven by non-operating concerns.  
  > "Record revenue $9.12 billion, up 25 percent year over year" ([AMAT-8K-2026-08-13-ex99](https://www.sec.gov/Archives/edgar/data/6951/000162828026056699/exhibit991q32026earningsre.htm))
- The company's own forward-looking risk disclosure cites export-license and trade-policy uncertainties that may explain the stock's relative underperformance despite accelerating revenue.  
  > "global trade issues, changes in trade and export regulations, license requirements, and their interpretation, and our ability to obtain licenses or authorizations on a timely basis, if at all" ([AMAT-8K-2026-08-13-ex99](https://www.sec.gov/Archives/edgar/data/6951/000162828026056699/exhibit991q32026earningsre.htm))
- A news report says Morgan Stanley maintained an Equal-Weight rating and lowered its price target to $563, indicating analyst caution despite the strong earnings release.  
  > "Morgan Stanley Maintains Equal-Weight on Applied Materials, Lowers Price Target to $563" ([AMAT-news-2026-09-28-62019127](https://www.benzinga.com/news/26/09/62019127/morgan-stanley-maintains-equal-weight-applied-materials-lowers-price-target-563))

**Bear case**
- U.S. export controls have already limited Applied's ability to sell certain products and services to customers in China, and further updates could reduce its revenue in that key market.  
  > "The United States government has implemented export regulations for U.S. semiconductor technology sold or provided to customers in China, which have limited our ability to provide certain products and services to customers in China, over the past several years." ([AMAT-10Q-2026-08-20-mdna](https://www.sec.gov/Archives/edgar/data/6951/000162828026058235/amat-20260726.htm))
- The company's forward-looking risk factors include the concentrated nature of its customer base, which may make investors discount robust current growth.  
  > "the concentrated nature of our customer base" ([AMAT-8K-2026-08-13-ex99](https://www.sec.gov/Archives/edgar/data/6951/000162828026056699/exhibit991q32026earningsre.htm))

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
- Coherent reported fiscal Q4 revenue of $2.05B, up 34% year over year and 42% on a pro forma basis, showing accelerating growth that contrasts with its three-month relative underperformance.  
  > "Q4 REVENUE OF $2.05B, INCREASED 34% Y/Y AND 42% Y/Y ON A PRO FORMA BASIS" ([COHR-8K-2026-08-12-ex99](https://www.sec.gov/Archives/edgar/data/820318/000119312526346860/d128030dex991.htm))
- The company attributes revenue acceleration to AI datacenter demand, as hyperscale investments have boosted demand for its datacenter transceivers.  
  > "The increasing investments by hyperscale and other cloud providers in AI datacenter infrastructures have significantly boosted demand for our datacenter transceivers." ([COHR-10K-2026-08-14-mdna](https://www.sec.gov/Archives/edgar/data/820318/000082031826000020/iivi-20260630.htm))
- The company is investing in manufacturing capacity for its Datacenter and Communications markets, which may pressure near-term free cash flow despite the revenue acceleration.  
  > "We are investing in manufacturing capacity for the Datacenter and Communications markets, including expanding our indium phosphide capacity in Sherman, Texas, to address our increased customer demand and industry-wide shortage." ([COHR-10K-2026-08-14-mdna](https://www.sec.gov/Archives/edgar/data/820318/000082031826000020/iivi-20260630.htm))

**Bear case**
- Goodwill in the Lasers reporting unit is sensitive, with estimated fair value exceeding carrying value by only about 8%, leaving little cushion for a possible impairment charge.  
  > "For the Lasers reporting unit, as of April 1, 2026, the estimated fair value exceeded the carrying value by approximately 8%." ([COHR-10K-2026-08-14-mdna](https://www.sec.gov/Archives/edgar/data/820318/000082031826000020/iivi-20260630.htm))
- The company's own risk disclosures state that its stock price may not trade in line with industrial technology leaders, which could explain the relative underperformance.  
  > "the risks that the Company’s stock price will not trade in line with industrial technology leaders" ([COHR-8K-2026-08-12-ex99](https://www.sec.gov/Archives/edgar/data/820318/000119312526346860/d128030dex991.htm))

*model said evidence: sufficient*

### AMKR: explained

- source: [AMKR 8-K earnings release (Exhibit 99.1), filed 2026-07-27](https://www.sec.gov/Archives/edgar/data/1047127/000104712726000043/amkr6302026erex-991.htm)
- source: [AMKR 10-Q for period 2026-06-30, MD&A, filed 2026-07-28](https://www.sec.gov/Archives/edgar/data/1047127/000104712726000046/amkr-20260630.htm)
- source: [Benzinga: AI’s Semiconductor Boom Has a Clear Center of Gravity: Taiwan Semiconductor (2026-09-30)](https://www.benzinga.com/markets/tech/26/09/62074203/ais-semiconductor-boom-has-a-clear-center-of-gravity-taiwan-semiconductor)
- source: [Benzinga: Amkor Technology Reveals Phase 2 Of Arizona Advanced Packaging And Test Campus; The Expansion Increases The Project’s Planned Investment To ~$12B (2026-09-08)](https://www.benzinga.com/news/26/09/61674271/amkor-technology-reveals-phase-2-arizona-advanced-packaging-and-test-campus-expansion-increases-proj)

**Thesis**
- Capital expenditures tripled to $688.4 million in the first half of 2026 from $226.1 million a year earlier, reflecting an aggressive buildout that may worry investors.  
  > "Our capital expenditures totaled $688.4 million for the six months ended June 30, 2026 compared to $226.1 million for the six months ended June 30, 2025." ([AMKR-10Q-2026-07-28-mdna](https://www.sec.gov/Archives/edgar/data/1047127/000104712726000046/amkr-20260630.htm))
- The company's own risk disclosures concede that the convertible notes may dilute shareholders or depress the stock price, which could explain the price decline.  
  > "terms of our convertible notes could delay or prevent an otherwise beneficial takeover of us, may dilute the ownership interest of existing stockholders or may otherwise adversely affect the price of our common stock" ([AMKR-8K-2026-07-27-ex99](https://www.sec.gov/Archives/edgar/data/1047127/000104712726000043/amkr6302026erex-991.htm))
- A news report says the Arizona campus expansion will raise the project's planned investment to about $12 billion, adding to concerns about capital intensity.  
  > "Amkor Technology Reveals Phase 2 Of Arizona Advanced Packaging And Test Campus; The Expansion Increases The Project’s Planned Investment To ~$12B" ([AMKR-news-2026-09-08-61674271](https://www.benzinga.com/news/26/09/61674271/amkor-technology-reveals-phase-2-arizona-advanced-packaging-and-test-campus-expansion-increases-proj))

**Bear case**
- The company is exposed to a cyclical semiconductor industry, and any downturn could hurt revenue and margins.  
  > "dependence on the cyclical and volatile semiconductor industry and vulnerability to industry downturns and declines in global economic and financial conditions" ([AMKR-8K-2026-07-27-ex99](https://www.sec.gov/Archives/edgar/data/1047127/000104712726000043/amkr6302026erex-991.htm))
- Heavy investments in equipment and facilities may not pay off if customer demand fails to materialize as expected.  
  > "We make substantial investments in equipment and facilities to support the demand of our customers, which may materially and adversely affect our business if the demand of our customers does not develop as we expect or is adversely affected." ([AMKR-10Q-2026-07-28-mdna](https://www.sec.gov/Archives/edgar/data/1047127/000104712726000046/amkr-20260630.htm))
- Concentration in a few key customers or end markets, such as mobile and automotive, increases earnings risk.  
  > "dependence on key customers or concentration of customers in certain end markets, such as mobile communications and automotive" ([AMKR-8K-2026-07-27-ex99](https://www.sec.gov/Archives/edgar/data/1047127/000104712726000043/amkr6302026erex-991.htm))

*Stripped by the citation check (1):* "The company's free cash flow turned negative at -$269.9 million in the first hal" (claim states numbers not in its quote: ['2026', '269.9'])

*model said evidence: sufficient*

## Data limits

- Prices: Alpaca SIP daily bars, split and dividend adjusted; no intraday data used.
- Fundamentals: SEC XBRL companyfacts, US-GAAP filers only. Foreign private issuers (IFRS, 20-F/40-F) and companies without standard tags drop out as 'missing', they are not guessed.
- Market cap uses the latest cover-page share count; for multi-class issuers it can understate.
- Industry groups are SEC SIC codes, a coarse proxy for a theme (no GICS/BICS in free data).
- Short interest: FINRA consolidated short interest (twice monthly, non-commercial use); % is of shares outstanding, not float.
- Earnings-call transcripts are licensed content and were not used; explanations rely on the 8-K earnings release, 10-Q/10-K MD&A, and news headlines and summaries (Alpaca / Benzinga), never full articles.
- No consensus estimates, revisions, ownership or borrow-cost data: those need a licensed source.
