import pandas as pd

from rail_ifc_quality_gate.r7_integrated_gate import compute_r7_integrated_gate


def test_regression_expected_outputs_schema():
    df = pd.DataFrame([
        {"spatial_pass":1,"semantic_pass":1,"Data_gate_pass":1},
        {"spatial_pass":0,"semantic_pass":1,"Data_gate_pass":1},
    ])
    out = df.apply(lambda r: compute_r7_integrated_gate(int(r.spatial_pass), int(r.semantic_pass), int(r.Data_gate_pass)), axis=1, result_type="expand")
    assert set(out.columns) == {"All_gates_pass","failure_driver"}
