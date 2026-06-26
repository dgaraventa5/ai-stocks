"""Generate tracking/calibration-report.md from resolved forecasts (rule 17).

Quarterly via /rescore-quarterly. matplotlib is optional (lazy, guarded); the
markdown table is the primary artifact (CI and the daily cron have no matplotlib).
"""
from __future__ import annotations

import sys
import argparse
import datetime as dt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import forecast_store as store
import forecast_metrics as metrics

REPORT_PATH = store.ROOT / "tracking" / "calibration-report.md"
CURVE_PATH = store.ROOT / "tracking" / "calibration-curve.png"
MIN_N_FOR_CURVE = 30


def _resolved(state) -> list[dict]:
    return [f for f in state.values() if f["status"] == "resolved" and f["outcome"] in (0, 1)]


def _section(label, ps, outs) -> list[str]:
    n = len(ps)
    if n == 0:
        return [f"### {label}", "", "_No resolved forecasts._", ""]
    bs = metrics.brier(ps, outs)
    bss = metrics.brier_skill_score(ps, outs)
    dec = metrics.murphy_decomposition(ps, outs)
    ll = metrics.log_loss(ps, outs)
    lines = [f"### {label}", "",
             f"- N: **{n}**  ·  base rate: {metrics.base_rate(outs):.2f}",
             f"- Brier: **{bs:.4f}**  ·  log loss: {ll:.4f}",
             f"- REL (lower better): {dec['REL']:.4f}  ·  RES (higher better): {dec['RES']:.4f}  ·  UNC: {dec['UNC']:.4f}"]
    if bss is None:
        lines.append("- BSS: undefined (one-sided outcomes)")
    else:
        lines.append(f"- BSS vs base rate: **{bss:.3f}** — "
                     + ("beats the base-rate null ✅" if bss > 0 else "no skill over the base rate ❌"))
    if n < MIN_N_FOR_CURVE:
        lines += ["", f"> ⚠️ N={n} < {MIN_N_FOR_CURVE}: the decomposition is noise — do not over-interpret."]
    lines += ["", "| bin | n | p̄ | ō |", "|---|---|---|---|"]
    for row in dec["table"]:
        if row["n"]:
            lines.append(f'| {row["bin"][0]:.1f}–{row["bin"][1]:.1f} | {row["n"]} '
                         f'| {row["p_bar"]:.2f} | {row["o_bar"]:.2f} |')
    lines.append("")
    return lines


def build_report(today: dt.date, path: Path = store.FORECASTS_PATH) -> str:
    state = store.materialize(path)
    out = ["# Forecast Calibration Report", "", f"_Generated {today.isoformat()}_", ""]
    if not state:
        out.append("No forecasts logged yet.")
        return "\n".join(out) + "\n"
    resolved = _resolved(state)
    review = sum(1 for f in state.values() if f["status"] in ("needs_review", "void"))
    out += [f"Total: {len(state)}  ·  resolved: {len(resolved)}  ·  "
            f"needs_review/void: {review}  ·  void rate: {review / len(state):.0%}", ""]
    ps = [f["probability"] for f in resolved]
    outs = [f["outcome"] for f in resolved]
    out += _section("Overall", ps, outs)
    out += ["## By dimension", ""]
    for dim in sorted({f["dimension"] for f in resolved if f.get("dimension")}):
        sub = [f for f in resolved if f["dimension"] == dim]
        out += _section(dim, [f["probability"] for f in sub], [f["outcome"] for f in sub])
    out += ["## By layer", ""]
    for layer in sorted({f["layer"] for f in resolved}):
        sub = [f for f in resolved if f["layer"] == layer]
        out += _section(f"Layer {layer}", [f["probability"] for f in sub], [f["outcome"] for f in sub])
    return "\n".join(out) + "\n"


def maybe_render_curve(today: dt.date, path: Path = store.FORECASTS_PATH) -> bool:
    resolved = _resolved(store.materialize(path))
    if len(resolved) < MIN_N_FOR_CURVE:
        return False
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return False
    ps = [f["probability"] for f in resolved]
    outs = [f["outcome"] for f in resolved]
    table = metrics.reliability_table(ps, outs)
    xs = [r["p_bar"] for r in table if r["n"]]
    ys = [r["o_bar"] for r in table if r["n"]]
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot([0, 1], [0, 1], "--", color="gray")
    ax.plot(xs, ys, "o-")
    ax.set_xlabel("forecast probability")
    ax.set_ylabel("observed frequency")
    ax.set_title(f"Reliability ({today.isoformat()})")
    fig.savefig(CURVE_PATH, dpi=100, bbox_inches="tight")
    plt.close(fig)
    return True


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true", help="print, do not write the file")
    args = ap.parse_args()
    today = dt.date.today()
    report = build_report(today)
    if args.dry_run:
        print(report)
        return
    REPORT_PATH.write_text(report)
    rendered = maybe_render_curve(today)
    print(f"wrote {REPORT_PATH}" + (f" + {CURVE_PATH}" if rendered else " (no PNG)"))


if __name__ == "__main__":
    main()
