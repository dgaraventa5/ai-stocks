# Cohort membership — P1 percentile scoring (GENERATED, do not hand-edit)

Source of truth: the Watchlist `Layer` column. Regenerate with
`python3 scripts/cohort_membership.py --update`. A diff here means the way
names are peer-ranked changed (rule 24). `pct` = percentile-ranked (cohort
has >= 8 non-null); `abs` = absolute-band fallback. Layer 09 col-F
(EV/*) is always `abs` (mixed EV/EBITDA + EV/MW).

## Layer 01 — 33 names
metrics: ev_ebitda=pct(32)  fcf_yield=pct(33)  ps=pct(31)  roic=pct(25)  gm=pct(33)  fcf_mgn=pct(31)
members: AEP, AR, BE, BW, BWXT, CCJ, CEG, CMI, D, DUK, EQT, ETR, EXE, GNRC, LEU, NEE, NNE, NRG, NXT, OKLO, PLUG, PPL, PSIX, PUMP, RRC, SEI, SMR, SO, TE, TLN, UEC, VST, XEL

## Layer 02 — 11 names
metrics: ev_ebitda=pct(11)  fcf_yield=pct(11)  ps=pct(11)  roic=pct(11)  gm=pct(11)  fcf_mgn=pct(11)
members: ABBNY, ATKR, ETN, GEV, HTHIY, HUBB, MTZ, NVT, POWL, PWR, SBGSY

## Layer 03 — 11 names
metrics: ev_ebitda=pct(11)  fcf_yield=pct(11)  ps=pct(11)  roic=pct(10)  gm=pct(11)  fcf_mgn=pct(11)
members: AAON, CARR, DLR, EME, EQIX, FIX, IRM, JCI, MOD, TT, VRT

## Layer 04 — 28 names
metrics: ev_ebitda=pct(28)  fcf_yield=pct(27)  ps=pct(28)  roic=pct(18)  gm=pct(28)  fcf_mgn=pct(27)
members: ACLS, AEIS, AIP, AMAT, AMKR, ARM, ASML, ASX, BESIY, CAMT, CDNS, CEVA, COHU, ENTG, FORM, KEYS, KLAC, KLIC, KN, LRCX, MKSI, ONTO, PLAB, SNPS, TER, TOELY, TTMI, UCTT

## Layer 05 — 8 names
metrics: ev_ebitda=pct(8)  fcf_yield=pct(8)  ps=pct(8)  roic=abs(5)  gm=pct(8)  fcf_mgn=pct(8)
members: 0981.HK, 5347.TWO, GFS, HHUSF, INTC, TSEM, TSM, UMC

## Layer 06 — 20 names
metrics: ev_ebitda=pct(20)  fcf_yield=pct(20)  ps=pct(20)  roic=pct(17)  gm=pct(20)  fcf_mgn=pct(20)
members: ADI, ALAB, AMBA, AMD, AVGO, LSCC, MCHP, MPWR, MRVL, MU, NVDA, NVTS, NXPI, ON, QCOM, RMBS, SNDK, STM, SWKS, TXN

## Layer 07 — 12 names
metrics: ev_ebitda=pct(12)  fcf_yield=pct(12)  ps=pct(12)  roic=pct(11)  gm=pct(12)  fcf_mgn=pct(12)
members: AAOI, ANET, APH, CIEN, COHR, CRDO, CSCO, FN, GLW, LITE, POET, TEL

## Layer 08 — 8 names
metrics: ev_ebitda=pct(8)  fcf_yield=pct(8)  ps=pct(8)  roic=abs(6)  gm=pct(8)  fcf_mgn=pct(8)
members: DELL, FLEX, HPE, NTAP, P, SMCI, STX, WDC

## Layer 09 — 20 names
metrics: ev_ebitda=abs(20)  fcf_yield=pct(20)  ps=pct(20)  roic=pct(16)  gm=pct(20)  fcf_mgn=pct(20)
members: AMZN, APLD, BTDR, CIFR, CLSK, CORZ, CRWV, GOOGL, HIVE, HUT, IREN, KEEL, META, MSFT, NBIS, ORCL, RIOT, SHAZ, WULF, WYFI

## Layer 10 — 21 names
metrics: ev_ebitda=pct(19)  fcf_yield=pct(20)  ps=pct(21)  roic=pct(11)  gm=pct(21)  fcf_mgn=pct(20)
members: AAPL, ADBE, ADSK, APP, CRM, CRWD, DDOG, FTNT, INTU, MDB, NOW, PANW, PATH, PLTR, RDDT, SNOW, SPCX, TEM, TSLA, WDAY, ZS

