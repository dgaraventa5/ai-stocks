import datetime as dt
import forecast_resolvers as r

CREATED = dt.date(2026, 6, 26)


def _forecast(benchmark="layer_cohort_ew", constituents=("NVDA", "MU"), res="2026-09-29"):
    return {"ticker": "AVGO", "created_date": CREATED.isoformat(),
            "resolution_date": res,
            "resolution_rule": {"benchmark": benchmark,
                                "constituents": list(constituents), "horizon_td": 3}}


def _ramp(start, step, n=10):
    # n daily bars from CREATED; close = start * (1+step)^i
    return {CREATED + dt.timedelta(days=i): start * (1 + step) ** i for i in range(n)}


def _loader(table):
    return lambda ticker, start: table[ticker]


def test_self_beats_cohort_outcome_1():
    table = {"AVGO": _ramp(100, 0.05), "NVDA": _ramp(100, 0.01), "MU": _ramp(100, 0.0)}
    res = r.resolve_rel_strength_1q(_forecast(), price_loader=_loader(table), today=dt.date(2026, 10, 1))
    assert res.status == "resolved" and res.outcome == 1
    assert "AVGO" in res.evidence and res.resolver_confidence == "auto"


def test_self_loses_outcome_0():
    table = {"AVGO": _ramp(100, 0.0), "NVDA": _ramp(100, 0.05), "MU": _ramp(100, 0.05)}
    res = r.resolve_rel_strength_1q(_forecast(), price_loader=_loader(table), today=dt.date(2026, 10, 1))
    assert res.status == "resolved" and res.outcome == 0


def test_smh_fallback_path():
    table = {"AVGO": _ramp(100, 0.05), "SMH": _ramp(100, 0.01)}
    res = r.resolve_rel_strength_1q(_forecast(benchmark="SMH", constituents=("SMH",)),
                                    price_loader=_loader(table), today=dt.date(2026, 10, 1))
    assert res.status == "resolved" and res.outcome == 1 and "SMH" in res.evidence


def test_insufficient_bars_stays_open_then_needs_review():
    table = {"AVGO": _ramp(100, 0.05, n=2), "NVDA": _ramp(100, 0.01, n=2), "MU": _ramp(100, 0.0, n=2)}
    loader = _loader(table)
    f = _forecast()
    # within grace of resolution_date -> stay open
    early = r.resolve_rel_strength_1q(f, price_loader=loader, today=dt.date(2026, 9, 30))
    assert early.status == "open"
    # 30+ days past resolution_date and still short -> needs_review
    late = r.resolve_rel_strength_1q(f, price_loader=loader, today=dt.date(2026, 11, 15))
    assert late.status == "needs_review" and late.outcome is None


def test_degraded_cohort_needs_review():
    table = {"AVGO": _ramp(100, 0.05), "NVDA": {}, "MU": {}}  # both peers missing
    res = r.resolve_rel_strength_1q(_forecast(), price_loader=_loader(table), today=dt.date(2026, 10, 1))
    assert res.status == "needs_review" and "degraded" in res.evidence


def test_resolution_date_for_weekday_math():
    # 3 weekdays forward from Fri 2026-06-26 -> Wed 2026-07-01, +7 buffer -> 2026-07-08
    assert r.resolution_date_for(dt.date(2026, 6, 26), 3) == dt.date(2026, 7, 8)
