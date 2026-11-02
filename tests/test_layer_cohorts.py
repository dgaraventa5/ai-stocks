"""Rule 13 cohort: one definition, used by all four scoring files. Offline."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import layer_cohorts as lc  # noqa: E402

SCRIPTS = Path(lc.__file__).parent


@pytest.mark.parametrize("layer,expected", [
    ("09 Cloud – Bitcoin Miner Pivot", True),
    ("09 Cloud – Neocloud", True),
    ("09 Cloud – NEOCLOUD", True),
    ("  09 Cloud – Neocloud", True),
    ("09 Cloud – Hyperscaler", False),
    ("10 Software – Neocloud", False),
    ("", False),
    (None, False),
])
def test_cohort_membership(layer, expected):
    assert lc.is_layer9_capacity(layer) is expected


@pytest.mark.parametrize("name", ["batch_score", "refresh_objective_inputs",
                                  "recalc_watchlist", "rebuild_watchlist_formulas"])
def test_scoring_files_share_the_definition(name):
    src = (SCRIPTS / f"{name}.py").read_text()
    assert "from layer_cohorts import is_layer9_capacity" in src
    assert "def is_layer9_capacity" not in src
    assert "def _is_layer9_capacity" not in src
