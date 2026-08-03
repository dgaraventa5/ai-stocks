"""One-shot driver: add the 2026-08-02 robotics universe to the Watchlist.

Feeds explicit (ticker, layer) tuples into batch_score.run() — bypasses
parse_universe() because most Layer-11 names use local-line tickers
(6954.T, 9880.HK, AUTO.OL, ...) that the map's [A-Z]+ ticker regex cannot
match (same situation as 5347.TWO / 0981.HK, which were also added by
direct driver). Serialized yfinance per CLAUDE.md (no parallel scraping).

Decision record: 11-robotics/robotics-universe-2026-08-02.md
"""
from batch_score import run

L11 = "11 Robotics & Physical AI / "
L06 = "06 AI Compute Silicon / "

TICKERS = [
    # Humanoid & service robot makers
    ("9880.HK", L11 + "Humanoid & service robot makers"),
    ("SERV",    L11 + "Humanoid & service robot makers"),
    ("TNC",     L11 + "Humanoid & service robot makers"),
    # Industrial automation & robot arms
    ("6954.T",  L11 + "Industrial automation & robot arms"),
    ("6506.T",  L11 + "Industrial automation & robot arms"),
    # Warehouse & logistics automation
    ("SYM",     L11 + "Warehouse & logistics automation"),
    ("AUTO.OL", L11 + "Warehouse & logistics automation"),
    ("6383.T",  L11 + "Warehouse & logistics automation"),
    ("KGX.DE",  L11 + "Warehouse & logistics automation"),
    ("2590.HK", L11 + "Warehouse & logistics automation"),
    # Surgical & medical robotics
    ("ISRG",    L11 + "Surgical & medical robotics"),
    ("PRCT",    L11 + "Surgical & medical robotics"),
    ("GMED",    L11 + "Surgical & medical robotics"),
    ("SSII",    L11 + "Surgical & medical robotics"),
    ("2252.HK", L11 + "Surgical & medical robotics"),
    # Components: motion & actuation
    ("6324.T",  L11 + "Components: motion & actuation"),
    ("6268.T",  L11 + "Components: motion & actuation"),
    ("6481.T",  L11 + "Components: motion & actuation"),
    ("2049.TW", L11 + "Components: motion & actuation"),
    ("TKR",     L11 + "Components: motion & actuation"),
    ("RRX",     L11 + "Components: motion & actuation"),
    ("ALNT",    L11 + "Components: motion & actuation"),
    ("NOVT",    L11 + "Components: motion & actuation"),
    ("VPG",     L11 + "Components: motion & actuation"),
    # Machine vision & perception
    ("CGNX",    L11 + "Machine vision & perception"),
    ("6861.T",  L11 + "Machine vision & perception"),
    ("OUST",    L11 + "Machine vision & perception"),
    ("HSAI",    L11 + "Machine vision & perception"),
    ("AEVA",    L11 + "Machine vision & perception"),
    ("2498.HK", L11 + "Machine vision & perception"),
    ("BSL.DE",  L11 + "Machine vision & perception"),
    # Autonomy platforms & defense
    ("MBLY",    L11 + "Autonomy platforms & defense"),
    ("KTOS",    L11 + "Autonomy platforms & defense"),
    ("AVAV",    L11 + "Autonomy platforms & defense"),
    ("RCAT",    L11 + "Autonomy platforms & defense"),
    ("ONDS",    L11 + "Autonomy platforms & defense"),
    ("UMAC",    L11 + "Autonomy platforms & defense"),
    ("DRO.AX",  L11 + "Autonomy platforms & defense"),
    ("PDYN",    L11 + "Autonomy platforms & defense"),
    # Layer 6 sensor semis (cohort coherence, rule 24)
    ("ALGM",    L06 + "Magnetic & position sensing (robotics)"),
    ("MELE.BR", L06 + "Magnetic & position sensing (robotics)"),
]

if __name__ == "__main__":
    summary = run(TICKERS)
    print()
    print("=== GAPS SUMMARY ===")
    for r in summary.get("log", []):
        gaps = [g for g in r["gaps"] if not g.startswith("ROIC:")]
        if gaps or r["status"] != "ok":
            print(f"{r['ticker']:<9} {r['status']:<16} {'; '.join(gaps)}")
