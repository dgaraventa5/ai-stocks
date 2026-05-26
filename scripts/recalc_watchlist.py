"""Recalculate Watchlist TOTAL scores in Python using canonical methodology.

Mirrors the Excel formulas in Methodology tab so we can read TOTALs without
needing Excel/LibreOffice to evaluate cached formulas. Read-only — does not
modify the workbook.
"""
from __future__ import annotations

from openpyxl import load_workbook

XLSX = '/Users/dom/Desktop/ai-stocks/00-master/ai_supply_chain_scoring.xlsx'


def _num(v):
    if v is None or v == "": return None
    if isinstance(v, str):
        try: return float(v)
        except ValueError: return None
    return v


def _band(value, bands):
    """bands: list of (predicate_value, score) ordered from best to worst.
    For lower-is-better, predicate is "value <= threshold".
    For higher-is-better, predicate is "value >= threshold".
    Last entry is the catch-all (e.g., (None, 5)).
    """
    if value is None or value == "":
        return None
    for thresh, score in bands:
        if thresh is None:
            return score
        if isinstance(thresh, tuple):
            op, t = thresh
            if op == '<=' and value <= t: return score
            if op == '>=' and value >= t: return score
        else:
            if value >= thresh: return score
    return None


def score_fwd_pe(v):
    v = _num(v)
    if v is None: return None
    if v < 0: return 5
    for t, s in [(15, 90), (20, 75), (25, 60), (30, 45), (40, 30), (60, 15)]:
        if v <= t: return s
    return 5

def score_ev_ebitda(v):
    v = _num(v)
    if v is None: return None
    if v < 0: return 5
    for t, s in [(10, 90), (15, 75), (20, 60), (25, 45), (35, 30), (50, 15)]:
        if v <= t: return s
    return 5

def score_fcf_yield(v):
    v = _num(v)
    if v is None: return None
    for t, s in [(8, 100), (6, 90), (4, 75), (2, 60), (1, 45), (0, 30)]:
        if v >= t: return s
    return 15

def score_ps(v):
    v = _num(v)
    if v is None: return None
    for t, s in [(2, 90), (4, 75), (7, 60), (10, 45), (15, 30), (25, 15)]:
        if v <= t: return s
    return 5

def score_roic(v):
    v = _num(v)
    if v is None: return None
    for t, s in [(25, 100), (20, 90), (15, 75), (10, 60), (5, 45), (0, 30)]:
        if v >= t: return s
    return 15

def score_gm(v):
    v = _num(v)
    if v is None: return None
    for t, s in [(60, 100), (50, 90), (40, 75), (30, 60), (20, 45), (10, 30)]:
        if v >= t: return s
    return 15

def score_fcf_mgn(v):
    v = _num(v)
    if v is None: return None
    for t, s in [(25, 100), (20, 90), (15, 75), (10, 60), (5, 45), (0, 30)]:
        if v >= t: return s
    return 15

def score_nd_ebitda(v):
    v = _num(v)
    if v is None: return None
    for t, s in [(0, 100), (1, 90), (2, 75), (3, 60), (4, 45), (5, 30)]:
        if v <= t: return s
    return 15

def score_rev_cagr(v):
    v = _num(v)
    if v is None: return None
    for t, s in [(40, 100), (30, 90), (20, 75), (10, 60), (5, 45), (0, 30)]:
        if v >= t: return s
    return 15

def score_rev_yoy(v):
    v = _num(v)
    if v is None: return None
    for t, s in [(40, 100), (30, 90), (20, 75), (10, 60), (5, 45), (0, 30)]:
        if v >= t: return s
    return 15

def score_eps_yoy(v):
    v = _num(v)
    if v is None: return None
    for t, s in [(40, 100), (30, 90), (20, 75), (10, 60), (0, 45), (-10, 30)]:
        if v >= t: return s
    return 15


def avg_nonnull(vals):
    xs = [v for v in vals if v is not None]
    return sum(xs) / len(xs) if xs else None


def recalc():
    wb = load_workbook(XLSX, data_only=False)
    ws = wb['Watchlist']

    # Weights from Weights sheet
    wsw = wb['Weights']
    weights = {}
    for row in wsw.iter_rows(min_row=2, values_only=True):
        if row[0] and row[1] is not None:
            weights[row[0]] = row[1]

    # Default if Weights sheet uses different schema — fall back to rubric
    w = {
        'Value': weights.get('Value', 0.15),
        'Quality': weights.get('Quality', 0.20),
        'Growth': weights.get('Growth', 0.15),
        'AI': weights.get('AI', 0.30),
        'Momentum': weights.get('Momentum', 0.10),
        'Risk': weights.get('Risk', 0.10),
    }

    results = []
    for r in range(2, ws.max_row + 1):
        ticker = ws.cell(row=r, column=1).value
        if not ticker: continue
        layer = ws.cell(row=r, column=3).value

        # Objective inputs
        fwd_pe = ws.cell(row=r, column=5).value
        ev_ebitda = ws.cell(row=r, column=6).value
        fcf_yield = ws.cell(row=r, column=7).value
        ps = ws.cell(row=r, column=8).value
        roic = ws.cell(row=r, column=10).value
        gm = ws.cell(row=r, column=11).value
        fcf_mgn = ws.cell(row=r, column=12).value
        nd_eb = ws.cell(row=r, column=13).value
        rev_cagr = ws.cell(row=r, column=15).value
        rev_yoy = ws.cell(row=r, column=16).value
        eps_yoy = ws.cell(row=r, column=17).value

        # Subjective
        ai_inputs = [ws.cell(row=r, column=c).value for c in [19, 20, 21, 22, 23]]
        mom_inputs = [ws.cell(row=r, column=c).value for c in [25, 26, 27]]
        risk_inputs = [ws.cell(row=r, column=c).value for c in [29, 30, 31, 32]]

        # Subscores
        value = avg_nonnull([score_fwd_pe(fwd_pe), score_ev_ebitda(ev_ebitda),
                             score_fcf_yield(fcf_yield), score_ps(ps)])
        # ND/EBITDA: only include if EBITDA positive — proxy: include only when nd_eb is sensibly numeric
        quality = avg_nonnull([score_roic(roic), score_gm(gm), score_fcf_mgn(fcf_mgn),
                               score_nd_ebitda(nd_eb)])
        growth = avg_nonnull([score_rev_cagr(rev_cagr), score_rev_yoy(rev_yoy),
                              score_eps_yoy(eps_yoy)])
        ai = (sum(x for x in ai_inputs if x is not None) / sum(1 for x in ai_inputs if x is not None) * 20) if any(x is not None for x in ai_inputs) else None
        momentum = (sum(x for x in mom_inputs if x is not None) / sum(1 for x in mom_inputs if x is not None) * 20) if any(x is not None for x in mom_inputs) else None
        risk = (sum(x for x in risk_inputs if x is not None) / sum(1 for x in risk_inputs if x is not None) * 20) if any(x is not None for x in risk_inputs) else None

        # TOTAL
        parts = []
        if value is not None: parts.append(value * w['Value'])
        if quality is not None: parts.append(quality * w['Quality'])
        if growth is not None: parts.append(growth * w['Growth'])
        if ai is not None: parts.append(ai * w['AI'])
        if momentum is not None: parts.append(momentum * w['Momentum'])
        if risk is not None: parts.append(risk * w['Risk'])
        total = sum(parts) if parts else None

        def tier(t):
            if t is None: return None
            if t >= 85: return '✓✓✓'
            if t >= 70: return '✓✓'
            if t >= 55: return '✓'
            if t >= 40: return '?'
            return '✗'

        results.append({
            'ticker': ticker, 'layer': layer, 'row': r,
            'Value': value, 'Quality': quality, 'Growth': growth,
            'AI': ai, 'Momentum': momentum, 'Risk': risk,
            'TOTAL': total, 'Tier': tier(total)
        })

    return results


if __name__ == '__main__':
    rs = recalc()
    # Sort by TOTAL desc (None last)
    rs.sort(key=lambda x: (x['TOTAL'] is None, -(x['TOTAL'] or 0)))
    print(f"{'Tkr':<7}{'Layer':<35}{'Val':>6}{'Qual':>6}{'Grw':>6}{'AI':>6}{'Mom':>6}{'Risk':>6}{'TOT':>7}{'Tier':>5}")
    for x in rs:
        def f(v): return f"{v:5.1f}" if isinstance(v,(int,float)) else "  -- "
        print(f"{x['ticker']:<7}{(x['layer'] or '')[:34]:<35}{f(x['Value'])}{f(x['Quality'])}{f(x['Growth'])}{f(x['AI'])}{f(x['Momentum'])}{f(x['Risk'])}{f(x['TOTAL']):>7}{(x['Tier'] or ''):>5}")
