from rail_ifc_quality_gate.r7_integrated_gate import compute_r7_integrated_gate


def test_r7_driver():
    out = compute_r7_integrated_gate(1,1,0)
    assert out["All_gates_pass"] == 0
    assert out["failure_driver"] == "Data"
