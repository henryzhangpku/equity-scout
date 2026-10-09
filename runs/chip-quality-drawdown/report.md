# Screen: Profitable companies worth over 2 billion dollars, down 30% or more from their highs, still growing revenue and generating free cash flow

As of **2026-10-08** (last price date 2026-10-08). Universe: tradable US-listed (NYSE/Nasdaq/AMEX/Arca/BATS) operating companies with an SEC CIK and a 10-K/10-Q/20-F/40-F in the last 18 months; close >= $1; 50-day avg dollar volume >= $1,000,000; one listing per CIK. Model: deepseek / deepseek-v4-pro (translation and prose only; every filter, rank and number below is computed by code).

## 1. Screen spec (proposed by the model, validated by code)

```json
{
  "version": 1,
  "observation": "Profitable companies worth over 2 billion dollars, down 30% or more from their highs, still growing revenue and generating free cash flow",
  "universe": {
    "market_cap_min": 2000000000
  },
  "conditions": [
    {
      "field": "net_income_ttm",
      "op": ">",
      "value": 0,
      "why": "Profitable companies"
    },
    {
      "field": "drawdown_52w",
      "op": "<=",
      "value": -0.3,
      "why": "down 30% or more from their highs"
    },
    {
      "field": "revenue_growth_yoy",
      "op": ">",
      "value": 0,
      "why": "still growing revenue"
    },
    {
      "field": "fcf_ttm",
      "op": ">",
      "value": 0,
      "why": "generating free cash flow"
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
  "notes": "Interpreted 'worth over 2 billion dollars' as market capitalization greater than $2B. 'Profitable' as positive trailing twelve-month net income. 'Down 30% or more from their highs' as current close at least 30% below its 52-week high. 'Growing revenue' as positive year-over-year TTM revenue growth. 'Generating free cash flow' as positive trailing twelve-month free cash flow. Ranked by drawdown_52w ascending to surface the most beaten-down stocks first, as the observation emphasizes the drawdown."
}
```

## 2. Funnel

| step | in | pass | fail | missing data |
|---|---:|---:|---:|---:|
| universe (liquid US common stocks with SEC filings) | 3827 | 3827 | 0 | 0 |
| market_cap >= $2.00B | 3827 | 1902 | 1712 | 213 |
| net_income_ttm > 0 | 1902 | 1120 | 235 | 547 |
| drawdown_52w <= -30.0% | 1120 | 239 | 877 | 4 |
| revenue_growth_yoy > +0.0% | 239 | 205 | 33 | 1 |
| fcf_ttm > 0 | 205 | 163 | 24 | 18 |

## 3. Ranked survivors (163)

| rank | symbol | name | score | market_cap | net_income_ttm | drawdown_52w | revenue_growth_yoy | fcf_ttm |
|---|---|---|---|---|---|---|---|---|
| 1 | CTVA | Corteva, Inc. | 1.000 | $9.2B | $1.0B | -84.8% | +3.7% | $629M |
| 2 | TTD | Trade Desk, Inc. | 0.994 | $5.8B | $407M | -77.2% | +11.6% | $863M |
| 3 | LQDA | Liquidia Corp | 0.988 | $2.5B | $139M | -69.2% | +2233.6% | $151M |
| 4 | Z | ZILLOW GROUP, INC. | 0.982 | $6.6B | $55M | -62.6% | +17.7% | $258M |
| 5 | CSGP | COSTAR GROUP, INC. | 0.975 | $12.1B | $73M | -62.3% | +22.0% | $280M |
| 6 | FICO | FAIR ISAAC CORP | 0.969 | $15.3B | $815M | -61.7% | +24.1% | $996M |
| 7 | PODD | INSULET CORP | 0.963 | $9.3B | $375M | -61.2% | +29.4% | $294M |
| 8 | LIF | Life360, Inc. | 0.957 | $3.4B | $147M | -61.1% | +34.0% | $103M |
| 9 | PRIM | Primoris Services Corp | 0.951 | $4.4B | $140M | -59.2% | +5.1% | $88M |
| 10 | WING | Wingstop Inc. | 0.945 | $3.2B | $116M | -58.1% | +7.6% | $128M |
| 11 | CELH | Celsius Holdings, Inc. | 0.939 | $6.9B | $129M | -57.8% | +82.9% | $463M |
| 12 | LULU | lululemon athletica inc. | 0.933 | $9.8B | $1.4B | -57.1% | +1.7% | $1.4B |
| 13 | INTU | INTUIT INC. | 0.926 | $81.2B | $4.6B | -54.9% | +13.9% | $8.7B |
| 14 | PATK | PATRICK INDUSTRIES INC | 0.920 | $2.1B | $147M | -54.7% | +3.2% | $128M |
| 15 | HUBS | HUBSPOT INC | 0.914 | $11.6B | $147M | -53.1% | +21.1% | $797M |
| 16 | PNR | PENTAIR plc | 0.908 | $8.5B | $671M | -52.7% | +3.1% | $716M |
| 17 | ALB | ALBEMARLE CORP | 0.902 | $12.0B | $224M | -52.4% | +18.3% | $1.3B |
| 18 | ESAB | ESAB Corp | 0.896 | $4.0B | $173M | -51.7% | +9.7% | $197M |
| 19 | CHWY | Chewy, Inc. | 0.890 | $7.7B | $274M | -51.7% | +5.9% | $568M |
| 20 | RH | RH | 0.883 | $2.2B | $112M | -51.2% | +3.3% | $251M |
| 21 | MTZ | MASTEC INC | 0.877 | $17.4B | $494M | -50.5% | +23.5% | $245M |
| 22 | FOUR | Shift4 Payments, Inc. | 0.871 | $3.1B | $133M | -50.3% | +32.4% | $573M |
| 23 | ROL | ROLLINS INC | 0.865 | $15.5B | $532M | -50.3% | +9.9% | $619M |
| 24 | AGX | ARGAN INC | 0.859 | $5.6B | $179M | -50.0% | +29.0% | $546M |
| 25 | INOD | INNODATA INC | 0.853 | $2.1B | $46M | -49.6% | +39.0% | $184M |

(138 more in run.json)

## 4. Why the dislocation might exist (top 5)

Every quote below was checked by code to appear verbatim in the linked SEC document. Claims whose quotes failed the check were removed and are listed.

### CTVA: explained

- source: [CTVA 8-K earnings release (Exhibit 99.1), filed 2026-07-30](https://www.sec.gov/Archives/edgar/data/1755672/000175567226000022/a2q_2026xearningsxnewsxr.htm)
- source: [CTVA 10-Q for period 2026-06-30, MD&A, filed 2026-07-31](https://www.sec.gov/Archives/edgar/data/1755672/000175567226000025/ctva-20260630.htm)
- source: [Benzinga: Corteva Completes Vylor Spin-Off: CTVA Vs. VYLR — Which Stock Is The Better Play Now? (2026-10-07)](https://www.benzinga.com/Opinion/26/10/62224289/corteva-completes-vylor-spin-off-ctva-vs-vylr-which-stock-is-the-better-play-now)
- source: [Benzinga: This NetApp Analyst Turns Bullish; Here Are Top 5 Upgrades For Wednesday (2026-10-07)](https://www.benzinga.com/analyst-stock-ratings/upgrades/26/10/62214736/this-netapp-analyst-turns-bullish-here-are-top-5-upgrades-for-wednesday-2)
- source: [Benzinga: Keybanc Upgrades Corteva to Overweight, Announces $17 Price Target (2026-10-07)](https://www.benzinga.com/news/26/10/62213190/keybanc-upgrades-corteva-overweight-announces-17-price-target)
- source: [Benzinga: JP Morgan Upgrades Corteva to Overweight, Lowers Price Target to $19 (2026-10-06)](https://www.benzinga.com/news/26/10/62187926/jp-morgan-upgrades-corteva-overweight-lowers-price-target-19)
- source: [Benzinga: How Does Corteva, Vylor Stand After Spin-off? (2026-10-02)](https://www.benzinga.com/trading-ideas/movers/26/10/62145012/how-does-corteva-vylor-stand-after-spin-off)
- source: [Benzinga: Nike, Corteva, Mattel, Accenture and Coherent: Why These 5 Stocks Are on Investors' Radars Today (2026-10-02)](https://www.benzinga.com/news/26/10/62125706/nike-corteva-mattel-accenture-and-coherent-why-these-5-stocks-are-on-investors-radars-today)
- source: [Benzinga: Nasdaq Gains 100 Points; ISM manufacturing PMI Slips In September (2026-10-01)](https://www.benzinga.com/markets/market-summary/26/10/62117701/nasdaq-gains-100-points-ism-manufacturing-pmi-slips-in-september)
- source: [Benzinga: Why Is Corteva Stock Sinking Thursday? (2026-10-01)](https://www.benzinga.com/trading-ideas/movers/26/10/62103401/why-is-corteva-stock-sinking-thursday)
- source: [Benzinga: Corteva Completes Spin Off Of Its Advanced Seed And Genetics Business (2026-10-01)](https://www.benzinga.com/news/26/10/62102609/corteva-completes-spin-its-advanced-seed-and-genetics-business)
- source: [Benzinga: Vylor Completes Its Separation From Corteva, To Trade On Nasdaq Under VYLR Symbol (2026-10-01)](https://www.benzinga.com/news/26/10/62102556/vylor-completes-its-separation-corteva-trade-nasdaq-under-vylr-symbol)
- source: [Benzinga: Jim Cramer Is Not Going To Go With This Consumer Cyclical Stock (2026-09-29)](https://www.benzinga.com/trading-ideas/long-ideas/26/09/62052921/jim-cramer-is-not-going-to-go-with-this-consumer-cyclical-stock)
- source: [Benzinga: Corteva Announces Seed Patent Suit Settlement With Inari, Which Will Destroy Corteva Material And Assign Related IP; Other Terms Confidential (2026-09-28)](https://www.benzinga.com/quote/CTVA)

**Thesis**
- A news report says Corteva's stock fell 82% following its spin-off of Vylor, and that the sharp price decline 'isn't what it seems.'  
  > "Corteva (CTVA) stock fell 82% following its spin-off of Vylor (VYLR). Here is why the sharp price decline isn't what it seems." ([CTVA-news-2026-10-01-62103401](https://www.benzinga.com/trading-ideas/movers/26/10/62103401/why-is-corteva-stock-sinking-thursday))
- A news report says Corteva completed the spin-off of its seed operating segment into Vylor Inc. on October 1, 2026, distributing Vylor shares pro rata to holders of record.  
  > "On October 1, 2026, Corteva Inc. (NYSE:CTVA) completed the spin-off of its seed operating segment into Vylor Inc. (NYSE:VYLR) through a pro rata distribution to holders of record as of the close of business on September" ([CTVA-news-2026-10-07-62224289](https://www.benzinga.com/Opinion/26/10/62224289/corteva-completes-vylor-spin-off-ctva-vs-vylr-which-stock-is-the-better-play-now))
- Corteva's earnings release states that full-year 2026 guidance was increased to reflect strong first-half performance, incremental benefits on controllable levers, and growth platforms.  
  > "Full-year 2026 guidance3 increased to reflect strong first half performance, incremental benefits on controllable levers, and growth platforms" ([CTVA-8K-2026-07-30-ex99](https://www.sec.gov/Archives/edgar/data/1755672/000175567226000022/a2q_2026xearningsxnewsxr.htm))

**Bear case**
- The Crop Protection segment experienced price declines due to market dynamics in Latin America, which could pressure revenue and margins.  
  > "The price decline was primarily due to market dynamics in Latin America." ([CTVA-10Q-2026-07-31-mdna](https://www.sec.gov/Archives/edgar/data/1755672/000175567226000025/ctva-20260630.htm))
- Corteva's restructuring and asset-related charges net increased to $141 million for the first half of 2026 from $101 million a year earlier.  
  > "Restructuring and asset related charges - net were $141 million for the six months ended June 30, 2026, an increase from $101 million for the six months ended June 30, 2025." ([CTVA-10Q-2026-07-31-mdna](https://www.sec.gov/Archives/edgar/data/1755672/000175567226000025/ctva-20260630.htm))
- Higher other expense was driven by litigation settlements and higher net exchange losses, further weighing on earnings.  
  > "Higher other expense was driven by litigation settlements and higher net exchange losses, as well as the absence of the receipt of insurance proceeds related to prior significant items during the first half of 2025." ([CTVA-10Q-2026-07-31-mdna](https://www.sec.gov/Archives/edgar/data/1755672/000175567226000025/ctva-20260630.htm))

*Stripped by the citation check (1):* "Corteva reported GAAP income from continuing operations of $1.94 billion for the" (claim states numbers not in its quote: ['2026'])

*model said evidence: sufficient*

### TTD: explained

- source: [TTD 8-K earnings release (Exhibit 99.1), filed 2026-08-06](https://www.sec.gov/Archives/edgar/data/1671933/000167193326000085/ttd-20260806x8kexx991.htm)
- source: [TTD 10-Q for period 2026-06-30, MD&A, filed 2026-08-06](https://www.sec.gov/Archives/edgar/data/1671933/000167193326000086/ttd-20260630.htm)
- source: [Benzinga: 'Apple fixed The Trade Desk’s Safari ad problem—but broader ad tech restrictions could be next'- AdAge (2026-10-08)](https://www.benzinga.com/news/26/10/62255747/apple-fixed-trade-desk-s-safari-ad-problem-broader-ad-tech-restrictions-could-be-next-adage)
- source: [Benzinga: Why Is The Trade Desk Stock Falling on Wednesday? (2026-09-23)](https://www.benzinga.com/trading-ideas/movers/26/09/61954056/why-is-the-trade-desk-stock-falling-on-wednesday)
- source: [Benzinga: Guggenheim Maintains Neutral on Trade Desk, Raises Price Target to $13 (2026-09-18)](https://www.benzinga.com/news/26/09/61865570/guggenheim-maintains-neutral-trade-desk-raises-price-target-13)
- source: [Benzinga: RBC Capital Reiterates Sector Perform on Trade Desk, Maintains $15 Price Target (2026-09-09)](https://www.benzinga.com/news/26/09/61686735/rbc-capital-reiterates-sector-perform-trade-desk-maintains-15-price-target)

**Thesis**
- Net income fell 29% year over year, signaling deteriorating profitability despite still-positive trailing twelve-month earnings.  
  > "Net income $ 64,394 $ 90,129 $ (25,735) (29) % $ 104,391 $ 140,807 $ (36,416) (26) %" ([TTD-10Q-2026-08-06-mdna](https://www.sec.gov/Archives/edgar/data/1671933/000167193326000086/ttd-20260630.htm))
- The CEO acknowledged that the quarter did not meet the company's own standard, suggesting internal execution issues.  
  > "This quarter did not meet the standard we set for ourselves, but it has reinforced our belief that we are focused on the right opportunities for the future" ([TTD-8K-2026-08-06-ex99](https://www.sec.gov/Archives/edgar/data/1671933/000167193326000085/ttd-20260806x8kexx991.htm))
- The revenue increase was partly offset by decreased gross spend from existing clients, indicating pressure on client retention or budget allocation.  
  > "partially offset by a decrease in gross spend from existing clients" ([TTD-10Q-2026-08-06-mdna](https://www.sec.gov/Archives/edgar/data/1671933/000167193326000086/ttd-20260630.htm))

**Bear case**
- A news report says the stock fell due to S&P 500 index deletion mechanical selling and ad-tech sector pressures from AppLovin.  
  > "The Trade Desk stock fell on Wednesday due to S&P 500 index deletion mechanical selling and ad-tech sector pressures from AppLovin" ([TTD-news-2026-09-23-61954056](https://www.benzinga.com/trading-ideas/movers/26/09/61954056/why-is-the-trade-desk-stock-falling-on-wednesday))
- A news report warns that Apple fixed The Trade Desk's Safari ad problem but broader ad tech restrictions could be next.  
  > "Apple fixed The Trade Desk’s Safari ad problem—but broader ad tech restrictions could be next" ([TTD-news-2026-10-08-62255747](https://www.benzinga.com/news/26/10/62255747/apple-fixed-trade-desk-s-safari-ad-problem-broader-ad-tech-restrictions-could-be-next-adage))

*Stripped by the citation check (1):* "Revenue growth decelerated to 3% year over year in Q2 2026, indicating a slowdow" (claim states numbers not in its quote: ['2'])

*model said evidence: sufficient*

### LQDA: explained

- source: [LQDA 8-K earnings release (Exhibit 99.1), filed 2026-08-12](https://www.sec.gov/Archives/edgar/data/1819576/000110465926094411/tm2622888d1_ex99-1.htm)
- source: [LQDA 10-Q for period 2026-06-30, MD&A, filed 2026-08-12](https://www.sec.gov/Archives/edgar/data/1819576/000110465926094410/lqda-20260630x10q.htm)
- source: [Benzinga: Wells Fargo Downgrades Liquidia to Equal-Weight, Lowers Price Target to $30 (2026-10-02)](https://www.benzinga.com/news/26/10/62135966/wells-fargo-downgrades-liquidia-equal-weight-lowers-price-target-30)
- source: [Benzinga: HC Wainwright & Co. Maintains Buy on Liquidia, Lowers Price Target to $58 (2026-10-02)](https://www.benzinga.com/news/26/10/62128875/hc-wainwright-co-maintains-buy-liquidia-lowers-price-target-58)
- source: [Benzinga: Raymond James Downgrades Liquidia to Outperform, Lowers Price Target to $53 (2026-10-01)](https://www.benzinga.com/news/26/10/62114602/raymond-james-downgrades-liquidia-outperform-lowers-price-target-53)
- source: [Benzinga: Liquidia Stock Extends Slide Following US Court Ruling in Patent Dispute (2026-10-01)](https://www.benzinga.com/trading-ideas/movers/26/10/62113623/liquidia-stock-extends-slide-following-us-court-ruling-in-patent-dispute)
- source: [Benzinga: This ExxonMobil Analyst Is No Longer Bullish; Here Are Top 5 Downgrades For Thursday (2026-10-01)](https://www.benzinga.com/news/26/10/62113290/this-exxonmobil-analyst-is-no-longer-bullish-here-are-top-5-downgrades-for-thursday)
- source: [Benzinga: BTIG Downgrades Liquidia to Neutral (2026-10-01)](https://www.benzinga.com/news/26/10/62099446/btig-downgrades-liquidia-neutral)
- source: [Benzinga: Needham Maintains Buy on Liquidia, Lowers Price Target to $72 (2026-10-01)](https://www.benzinga.com/news/26/10/62098941/needham-maintains-buy-liquidia-lowers-price-target-72)
- source: [Benzinga: Why is Liquidia (LQDA) Stock Trending After Hours? (2026-10-01)](https://www.benzinga.com/markets/equities/26/09/62096831/liquidia-corp-shares-after-hours-patent-ruling)
- source: [Benzinga: Trading Halt: Halt status updated at 1:35:00 PM ET: Quotation Resumption: News and Resumption Times (2026-09-30)](https://www.benzinga.com/quote/LQDA)
- source: [Benzinga: Judge Upholds Claims 1 And 14 Of United Therapeutics' '327 Patent, Rules Liquidia Infringes; Final Judgment Due Within One Week (2026-09-30)](https://www.benzinga.com/news/26/09/62085083/judge-upholds-claims-1-and-14-united-therapeutics-327-patent-rules-liquidia-infringes-final-judgment)
- source: [Benzinga: Trading Halt: Halt status updated at 11:38:29 AM ET: Trading Halt: Halt News Pending (2026-09-30)](https://www.benzinga.com/quote/LQDA)

**Thesis**
- Liquidia's filings caution that litigation with United Therapeutics could block YUTREPIA sales for PAH, PH-ILD, or both.  
  > "Our ability to maintain YUTREPIA’s approval and to continue commercialization of YUTREPIA remain subject to ongoing litigation in which United Therapeutics is seeking injunctive relief, which could block our ability to continue to sell YUTREPIA for one or both of PAH and PH-ILD." ([LQDA-8K-2026-08-12-ex99](https://www.sec.gov/Archives/edgar/data/1819576/000110465926094411/tm2622888d1_ex99-1.htm))
- A news report states a federal judge upheld United Therapeutics' patent claims and ruled Liquidia infringes, with final judgment due within one week.  
  > "Judge Upholds Claims 1 And 14 Of United Therapeutics' '327 Patent, Rules Liquidia Infringes; Final Judgment Due Within One Week" ([LQDA-news-2026-09-30-62085083](https://www.benzinga.com/news/26/09/62085083/judge-upholds-claims-1-and-14-united-therapeutics-327-patent-rules-liquidia-infringes-final-judgment))

**Bear case**
- Reported news says Liquidia shares closed 57.19% lower following the adverse patent ruling.  
  > "Liquidia Corp. shares gained 0.13% after hours after closing 57.19% lower following an adverse patent ruling." ([LQDA-news-2026-10-01-62096831](https://www.benzinga.com/markets/equities/26/09/62096831/liquidia-corp-shares-after-hours-patent-ruling))
- Analysts reportedly downgraded Liquidia and cut price targets after the ruling, as in Wells Fargo's equal-weight downgrade.  
  > "Wells Fargo Downgrades Liquidia to Equal-Weight, Lowers Price Target to $30" ([LQDA-news-2026-10-02-62135966](https://www.benzinga.com/news/26/10/62135966/wells-fargo-downgrades-liquidia-equal-weight-lowers-price-target-30))

*Stripped by the citation check (3):* "Liquidia reported net income of $74.7 million in Q2 2026, driven by YUTREPIA sal" (claim states numbers not in its quote: ['2']); "YUTREPIA net product sales were $170.4 million in Q2 2026, up from $6.5 million " (claim states numbers not in its quote: ['2']); "The company's own 10-Q warns it could be subject to injunctive relief that would" (claim states numbers not in its quote: ['10'])

*model said evidence: sufficient*

### Z: explained

- source: [Z 8-K earnings release (Exhibit 99.1), filed 2026-08-05](https://www.sec.gov/Archives/edgar/data/1617640/000161764026000050/q22026991.htm)
- source: [Z 10-Q for period 2026-06-30, MD&A, filed 2026-08-05](https://www.sec.gov/Archives/edgar/data/1617640/000161764026000052/z-20260630.htm)
- source: [Benzinga: U.S. Supreme Court Declines To Hear Zillow's Claim To Avoid An Investor Class Action Over Failed House-Flipping Business Activities (2026-10-05)](https://www.benzinga.com/news/26/10/62162056/u-s-supreme-court-declines-hear-zillow-s-claim-avoid-investor-class-action-over-failed-house-flippin)
- source: [Benzinga: Reported Earlier: Zillow Announces August Sales Drop 0.6% YoY (2026-09-08)](https://www.benzinga.com/news/26/09/61665826/reported-earlier-zillow-announces-august-sales-drop-0-6-yoy)

**Thesis**
- Zillow's second-quarter revenue rose 18% year over year to $772 million, above the high end of its outlook, showing strong fundamental growth despite the steep stock decline.  
  > "Q2 revenue was up 18% year over year to $772 million, above the high end of the company’s outlook range." ([Z-8K-2026-08-05-ex99](https://www.sec.gov/Archives/edgar/data/1617640/000161764026000050/q22026991.htm))
- Adjusted EBITDA was $176 million with a 23% margin, reflecting robust underlying profitability that the market may be discounting due to non-operating concerns.  
  > "Q2 Adjusted EBITDA was $176 million, above the high end of our outlook range, and Adjusted EBITDA margin was 23%." ([Z-8K-2026-08-05-ex99](https://www.sec.gov/Archives/edgar/data/1617640/000161764026000050/q22026991.htm))
- The company reported a GAAP net loss of $4 million in the quarter, a small loss that may nevertheless have contributed to negative investor sentiment.  
  > "Net loss was $4 million in Q2, and net loss margin was 1%, an 80-basis-point decrease year over year." ([Z-8K-2026-08-05-ex99](https://www.sec.gov/Archives/edgar/data/1617640/000161764026000050/q22026991.htm))

**Bear case**
- A news report says the U.S. Supreme Court declined to hear Zillow's claim to avoid an investor class action over failed house-flipping business activities, which could expose the company to significant legal liability.  
  > "U.S. Supreme Court Declines To Hear Zillow's Claim To Avoid An Investor Class Action Over Failed House-Flipping Business Activities" ([Z-news-2026-10-05-62162056](https://www.benzinga.com/news/26/10/62162056/u-s-supreme-court-declines-hear-zillow-s-claim-avoid-investor-class-action-over-failed-house-flippin))
- A news report says Zillow announced August sales dropped 0.6% year over year, pointing to weakening housing market conditions that could pressure future revenue.  
  > "Reported Earlier: Zillow Announces August Sales Drop 0.6% YoY" ([Z-news-2026-09-08-61665826](https://www.benzinga.com/news/26/09/61665826/reported-earlier-zillow-announces-august-sales-drop-0-6-yoy))
- Traffic to Zillow Group’s mobile apps and sites was down 2% year over year to 239 million average monthly unique users, indicating declining consumer engagement that could reduce advertising and lead-generation revenue.  
  > "Traffic to Zillow Group’s mobile apps and sites in Q2 was down 2% year over year to 239 million average monthly unique users." ([Z-8K-2026-08-05-ex99](https://www.sec.gov/Archives/edgar/data/1617640/000161764026000050/q22026991.htm))

*model said evidence: sufficient*

### CSGP: explained

- source: [CSGP 8-K earnings release (Exhibit 99.1), filed 2026-07-28](https://www.sec.gov/Archives/edgar/data/1057352/000105735226000061/q2fy262026earningspressr.htm)
- source: [CSGP 10-Q for period 2026-06-30, MD&A, filed 2026-07-29](https://www.sec.gov/Archives/edgar/data/1057352/000105735226000066/csgp-20260630.htm)
- source: [Benzinga: Needham Reiterates Buy on CoStar Group, Maintains $40 Price Target (2026-10-06)](https://www.benzinga.com/news/26/10/62183192/needham-reiterates-buy-costar-group-maintains-40-price-target)

**Thesis**
- CoStar reported a profitability inflection with net income rising to $55 million from $6 million a year earlier.  
  > "Net income was $55 million and earnings per diluted share was $0.14 for the second quarter of 2026, compared with net income of $6 million, and earnings per diluted share of $0.01, in the prior year period." ([CSGP-8K-2026-07-28-ex99](https://www.sec.gov/Archives/edgar/data/1057352/000105735226000061/q2fy262026earningspressr.htm))
- Adjusted EBITDA more than doubled year-over-year to $184 million, marking a profitability inflection.  
  > "The second quarter marked a profitability inflection point for CoStar Group as Adjusted EBITDA more than doubled year-over-year to $184 million." ([CSGP-8K-2026-07-28-ex99](https://www.sec.gov/Archives/edgar/data/1057352/000105735226000061/q2fy262026earningspressr.htm))
- Management raised its full-year 2026 Adjusted EBITDA guidance midpoint by $30 million.  
  > "The Company is affirming its Adjusted EBITDA guidance for the full year of 2026 in a range of $780 million to $820 million, which represents an increase of $30 million at the midpoint of the range from its guidance in February 2026." ([CSGP-8K-2026-07-28-ex99](https://www.sec.gov/Archives/edgar/data/1057352/000105735226000061/q2fy262026earningspressr.htm))

**Bear case**
- Contract renewal rates were only approximately 89% with cancellation rates around 11% over the trailing twelve months.  
  > "For each of the trailing 12 months ended June 30, 2026 and 2025, our contract renewal rates for existing company-wide CoStar Group subscription-based services for contracts with a term of at least one year were approximately 89%, and our cancellation rates for those services during the same periods were approximately 11%." ([CSGP-10Q-2026-07-29-mdna](https://www.sec.gov/Archives/edgar/data/1057352/000105735226000066/csgp-20260630.htm))
- Commercial Real Estate revenue growth is expected to moderate in 2026 partly due to a nonrecurring benefit from the Matterport acquisition in 2025.  
  > "We expect Commercial Real Estate's revenue growth rate for the year ending December 31, 2026 to moderate compared to the revenue growth rate for the year ended December 31, 2025 primarily due to the nonrecurring benefit realized in 2025 from the Matterport Acquisition." ([CSGP-10Q-2026-07-29-mdna](https://www.sec.gov/Archives/edgar/data/1057352/000105735226000066/csgp-20260630.htm))

*Stripped by the citation check (2):* "Revenue grew 18% year-over-year to $925 million in Q2 2026." (claim states numbers not in its quote: ['2']); "Annualized net new bookings declined to $69 million in Q2 2026 from $93 million " (claim states numbers not in its quote: ['2'])

*model said evidence: sufficient*

## Data limits

- Prices: Alpaca SIP daily bars, split and dividend adjusted; no intraday data used.
- Fundamentals: SEC XBRL companyfacts, US-GAAP filers only. Foreign private issuers (IFRS, 20-F/40-F) and companies without standard tags drop out as 'missing', they are not guessed.
- Market cap uses the latest cover-page share count; for multi-class issuers it can understate.
- Industry groups are SEC SIC codes, a coarse proxy for a theme (no GICS/BICS in free data).
- Short interest: FINRA consolidated short interest (twice monthly, non-commercial use); % is of shares outstanding, not float.
- Earnings-call transcripts are licensed content and were not used; explanations rely on the 8-K earnings release, 10-Q/10-K MD&A, and news headlines and summaries (Alpaca / Benzinga), never full articles.
- No consensus estimates, revisions, ownership or borrow-cost data: those need a licensed source.
