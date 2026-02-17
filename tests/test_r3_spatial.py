from pathlib import Path

import pandas as pd

from rail_ifc_quality_gate.ifc_io import open_ifc
from rail_ifc_quality_gate.r3_spatial import compute_r3_preliminary, postprocess_r3_group, REGIME_LOCAL, REGIME_PROJECTED_UTM_M


def test_r3_preliminary_on_toy_ifc(tmp_path: Path):
    # Use included toy IFC file
    toy = Path(__file__).resolve().parents[1] / "examples" / "toy_ifc_generated" / "toy_case_0001.ifc"
    model = open_ifc(toy)
    r3 = compute_r3_preliminary(model)
    assert "georef_regime" in r3
    assert "truenorth_deg" in r3


def test_r3_postprocess_group():
    df = pd.DataFrame([
        {"case":"Depot_A","state":"EX","discipline":"EST","anchor_x_m":0,"anchor_y_m":0,"anchor_z_m":0,"truenorth_deg":0,"georef_regime":REGIME_PROJECTED_UTM_M},
        {"case":"Depot_A","state":"EX","discipline":"EST","anchor_x_m":0,"anchor_y_m":0,"anchor_z_m":0,"truenorth_deg":0,"georef_regime":REGIME_PROJECTED_UTM_M},
    ])
    out = postprocess_r3_group(df, {"EST":5.0})
    assert "anchor_dispersion_m" in out.columns
    assert out["spatial_pass"].iloc[0] in (0,1)
