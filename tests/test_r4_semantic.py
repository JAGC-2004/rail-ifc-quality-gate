from pathlib import Path

from rail_ifc_quality_gate.ifc_io import open_ifc
from rail_ifc_quality_gate.r4_semantic import compute_r4_metrics


def test_r4_proxy_ratio():
    toy = Path(__file__).resolve().parents[1] / "examples" / "toy_ifc_generated" / "toy_case_0001.ifc"
    model = open_ifc(toy)
    r4 = compute_r4_metrics(model, proxy_threshold_pct=50.0)
    assert "proxy_pct" in r4
    assert "semantic_pass" in r4
