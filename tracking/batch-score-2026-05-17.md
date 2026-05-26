# Batch score run — 2026-05-17

- Total processed: **105**
- Succeeded: **104**
- Errors: **1**
- Elapsed: **192.4s**
- Watchlist tickers after batch (including pre-existing): **112**

## Headline findings — read before rating sessions

### 1. JNPR (Juniper Networks) — delisted
yfinance returned empty info. JNPR was acquired by HPE (deal closed); already flagged in `00-master/ai_supply_chain_research_map.md` Layer 7. **AI exposure for Juniper IP now lives inside HPE** (already in Watchlist). No further action; JNPR is not in the Watchlist.

### 2. Universal data gap (every name)
**ROIC** is not exposed by `yfinance.Ticker.info`. All new rows have the ROIC cell blank; Quality subscore averages over the 3 remaining inputs. Fix in future: pull EBIT × (1 − tax) ÷ (debt + equity) from EDGAR companyfacts.

### 3. Name-specific gaps to address in rating session
| Ticker | Gap | Interpretation |
|---|---|---|
| OKLO | Rev 3y CAGR — non-positive base | Pre-revenue SMR developer; Growth subscore low by definition; rating lives in D-dimensions |
| ARM | Rev 3y CAGR — non-positive base | IPO'd Sep 2023 — limited public history |
| SNDK | Rev 3y CAGR — only 3 years | Spun from WDC Feb 2025 — recent spin |
| NNE | Rev 3y CAGR — only 3 years | NANO Nuclear — recent IPO |
| TOELY | Rev 3y CAGR — non-positive base | Tokyo Electron ADR; yfinance has poor foreign-ADR coverage |
| AR | ND/EBITDA — missing EBITDA | Antero Resources; gas E&P, check whether negative quarterly EBITDA flipped the calc |
| CAMT | FCF Yield — missing FCF | Small-cap Camtek; yfinance intermittent |
| BITF | totalDebt, totalCash, FCF, P/S all missing | Bitfarms small-cap; yfinance returns very partial data |

### 4. BTC miners as a category — heavy gaps
Most miners pivoting to AI hosting (CORZ, CIFR, CLSK, BTDR, HUT, BITF, RIOT, WULF) have **no trailing P/E** in yfinance — earnings are negative or volatile. Expected; Value subscore will be impaired across the layer. Use D2/D3/D4 to evaluate the AI-pivot thesis rather than earnings-based metrics.

## Per-ticker log

| Ticker | Company | Row | Status | Gaps | Seconds |
|---|---|---:|---|---|---:|
| D | Dominion Energy, Inc. | 10 | ok | — | 1.9 |
| AEP | American Electric Power Company, Inc. | 11 | ok | — | 1.5 |
| DUK | Duke Energy Corporation | 12 | ok | — | 1.5 |
| SO | The Southern Company | 13 | ok | — | 1.7 |
| NEE | NextEra Energy, Inc. | 14 | ok | — | 1.5 |
| ETR | Entergy Corporation | 15 | ok | — | 1.5 |
| PPL | PPL Corporation | 16 | ok | — | 1.7 |
| XEL | Xcel Energy Inc. | 17 | ok | — | 1.5 |
| VST | Vistra Corp. | 18 | ok | — | 1.6 |
| TLN | Talen Energy Corporation | 19 | ok | — | 1.5 |
| NRG | NRG Energy, Inc. | 20 | ok | — | 1.5 |
| CCJ | Cameco Corporation | 21 | ok | — | 1.6 |
| UEC | Uranium Energy Corp. | 22 | ok | — | 1.4 |
| LEU | Centrus Energy Corp. | 23 | ok | — | 1.5 |
| BWXT | BWX Technologies, Inc. | 24 | ok | — | 1.5 |
| SMR | NuScale Power Corporation | 25 | ok | — | 1.4 |
| OKLO | Oklo Inc. | 26 | ok | Rev 3y CAGR: non-positive base or current value | 1.4 |
| NNE | NANO Nuclear Energy Inc. | 27 | ok | Rev 3y CAGR: only 3 years of data | 1.5 |
| EQT | EQT Corporation | 28 | ok | — | 1.5 |
| RRC | Range Resources Corporation | 29 | ok | — | 1.5 |
| AR | Antero Resources Corporation | 30 | ok | ND/EBITDA: missing totalDebt/totalCash/ebitda | 1.5 |
| CTRA | Coterra Energy Inc. | 31 | ok | — | 1.6 |
| EXE | Expand Energy Corporation | 32 | ok | — | 1.5 |
| PLUG | Plug Power Inc. | 33 | ok | — | 1.5 |
| CMI | Cummins Inc. | 34 | ok | — | 1.4 |
| GNRC | Generac Holdings Inc. | 35 | ok | — | 1.4 |
| ETN | Eaton Corporation plc | 36 | ok | — | 1.5 |
| SBGSY | Schneider Electric S.E. | 37 | ok | — | 1.6 |
| ABBNY | ABB Ltd | 38 | ok | — | 1.6 |
| HTHIY | Hitachi, Ltd. | 39 | ok | — | 1.4 |
| HUBB | Hubbell Incorporated | 40 | ok | — | 1.5 |
| PWR | Quanta Services, Inc. | 41 | ok | — | 1.6 |
| MTZ | MasTec, Inc. | 42 | ok | — | 1.5 |
| POWL | Powell Industries, Inc. | 43 | ok | — | 1.6 |
| NVT | nVent Electric plc | 44 | ok | — | 1.5 |
| ATKR | Atkore Inc. | 45 | ok | — | 1.5 |
| DLR | Digital Realty Trust, Inc. | 46 | ok | — | 1.6 |
| EQIX | Equinix, Inc. | 47 | ok | — | 1.7 |
| IRM | Iron Mountain Incorporated | 48 | ok | — | 1.5 |
| FIX | Comfort Systems USA, Inc. | 49 | ok | — | 1.5 |
| EME | EMCOR Group, Inc. | 50 | ok | — | 1.7 |
| MOD | Modine Manufacturing Company | 51 | ok | — | 1.6 |
| CARR | Carrier Global Corporation | 52 | ok | — | 1.6 |
| TT | Trane Technologies plc | 53 | ok | — | 1.6 |
| JCI | Johnson Controls International plc | 54 | ok | — | 1.6 |
| ASML | ASML Holding N.V. | 55 | ok | — | 1.5 |
| AMAT | Applied Materials, Inc. | 56 | ok | — | 1.5 |
| LRCX | Lam Research Corporation | 57 | ok | — | 1.4 |
| KLAC | KLA Corporation | 58 | ok | — | 1.6 |
| TOELY | Tokyo Electron Limited | 59 | ok | Rev 3y CAGR: non-positive base or current value | 1.3 |
| TER | Teradyne, Inc. | 60 | ok | — | 1.4 |
| ONTO | Onto Innovation Inc. | 61 | ok | — | 1.6 |
| CAMT | Camtek Ltd. | 62 | ok | FCF Yield: missing freeCashflow or marketCap | 1.4 |
| KLIC | Kulicke and Soffa Industries, Inc. | 63 | ok | — | 1.7 |
| ENTG | Entegris, Inc. | 64 | ok | — | 1.6 |
| MKSI | MKS Inc. | 65 | ok | — | 1.8 |
| PLAB | Photronics, Inc. | 66 | ok | — | 1.5 |
| UCTT | Ultra Clean Holdings, Inc. | 67 | ok | — | 1.5 |
| CDNS | Cadence Design Systems, Inc. | 68 | ok | — | 1.5 |
| SNPS | Synopsys, Inc. | 69 | ok | — | 1.5 |
| ARM | Arm Holdings plc | 70 | ok | Rev 3y CAGR: non-positive base or current value | 1.5 |
| TSM | Taiwan Semiconductor Manufacturing Compa | 71 | ok | — | 1.6 |
| INTC | Intel Corporation | 72 | ok | — | 1.6 |
| GFS | GLOBALFOUNDRIES Inc. | 73 | ok | — | 1.5 |
| TSEM | Tower Semiconductor Ltd. | 74 | ok | — | 1.6 |
| UMC | United Microelectronics Corporation | 75 | ok | — | 1.4 |
| AVGO | Broadcom Inc. | 76 | ok | — | 1.6 |
| MRVL | Marvell Technology, Inc. | 77 | ok | — | 1.4 |
| ALAB | Astera Labs, Inc. | 78 | ok | — | 1.3 |
| SNDK | Sandisk Corporation | 79 | ok | Rev 3y CAGR: only 3 years of data | 1.5 |
| COHR | Coherent Corp. | 80 | ok | — | 1.5 |
| LITE | Lumentum Holdings Inc. | 81 | ok | — | 1.6 |
| FN | Fabrinet | 82 | ok | — | 1.5 |
| AAOI | Applied Optoelectronics, Inc. | 83 | ok | — | 1.5 |
| POET | POET Technologies Inc. | 84 | ok | — | 1.5 |
| ANET | Arista Networks, Inc. | 85 | ok | — | 1.5 |
| CSCO | Cisco Systems, Inc. | 86 | ok | — | 1.4 |
| JNPR |  | — | error_no_data | yfinance returned empty info | 0.6 |
| CIEN | Ciena Corporation | 87 | ok | — | 1.4 |
| APH | Amphenol Corporation | 88 | ok | — | 1.5 |
| TEL | TE Connectivity plc | 89 | ok | — | 1.8 |
| GLW | Corning Incorporated | 90 | ok | — | 1.4 |
| SMCI | Super Micro Computer, Inc. | 91 | ok | — | 1.5 |
| DELL | Dell Technologies Inc. | 92 | ok | — | 1.5 |
| HPE | Hewlett Packard Enterprise Company | 93 | ok | — | 1.4 |
| MSFT | Microsoft Corporation | 94 | ok | — | 1.4 |
| GOOGL | Alphabet Inc. | 95 | ok | — | 1.6 |
| AMZN | Amazon.com, Inc. | 96 | ok | — | 1.5 |
| META | Meta Platforms, Inc. | 97 | ok | — | 1.4 |
| ORCL | Oracle Corporation | 98 | ok | — | 1.5 |
| NBIS | Nebius Group N.V. | 99 | ok | — | 1.5 |
| APLD | Applied Digital Corporation | 100 | ok | — | 1.5 |
| CORZ | Core Scientific, Inc. | 101 | ok | — | 1.6 |
| IREN | IREN Limited | 102 | ok | — | 1.6 |
| CIFR | Cipher Digital Inc. | 103 | ok | — | 1.5 |
| CLSK | CleanSpark, Inc. | 104 | ok | — | 1.6 |
| BTDR | Bitdeer Technologies Group | 105 | ok | — | 1.4 |
| HUT | Hut 8 Corp. | 106 | ok | — | 1.6 |
| BITF | Bitfarms Ltd | 107 | ok | FCF Yield: missing freeCashflow or marketCap; ND/EBITDA: missing totalDebt/totalCash/ebitd | 1.6 |
| RIOT | Riot Platforms, Inc. | 108 | ok | — | 1.7 |
| WULF | TeraWulf Inc. | 109 | ok | — | 1.3 |
| PLTR | Palantir Technologies Inc. | 110 | ok | — | 1.5 |
| SNOW | Snowflake Inc. | 111 | ok | — | 1.5 |
| NOW | ServiceNow, Inc. | 112 | ok | — | 1.5 |
| CRM | Salesforce, Inc. | 113 | ok | — | 1.6 |
