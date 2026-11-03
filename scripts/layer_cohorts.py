"""The rule-13 capacity cohort, defined once. Standard library only: the offline
scoring path and the site-deploy CI import this."""
from __future__ import annotations


def is_layer9_capacity(layer) -> bool:
    """Rule 13 cohort: Layer 9 bitcoin-miner pivots and neoclouds.

    Hyperscalers keep standard EV/EBITDA.
    """
    if not layer or not str(layer).strip().startswith("09"):
        return False
    l = str(layer).lower()
    return "bitcoin" in l or "neocloud" in l
