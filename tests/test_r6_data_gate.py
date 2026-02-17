from pathlib import Path

from rail_ifc_quality_gate.ifc_io import open_ifc
from rail_ifc_quality_gate.r6_data_gate import load_owner_profile, compute_r6_data_gate


def test_r6_data_gate_runs():
    toy = Path(__file__).resolve().parents[1] / "examples" / "toy_ifc_generated" / "toy_case_0001.ifc"
    model = open_ifc(toy)
    prof = load_owner_profile(Path(__file__).resolve().parents[1] / "configs" / "profiles" / "owner_profile_O0_generic_min.yml")
    out = compute_r6_data_gate(model, state="EX", discipline_domain="building", owner_profile=prof)
    assert "Data_gate_pass" in out
    assert "per_pset_rows" in out
