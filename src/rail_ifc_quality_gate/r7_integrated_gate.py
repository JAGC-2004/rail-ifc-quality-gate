from __future__ import annotations

from typing import Any, Dict


def failure_driver(spatial_pass: int, semantic_pass: int, data_gate_pass: int) -> str:
    if spatial_pass and semantic_pass and data_gate_pass:
        return "Pass"

    fails = []
    if not spatial_pass:
        fails.append("Spatial")
    if not semantic_pass:
        fails.append("Semantic")
    if not data_gate_pass:
        fails.append("Data")

    if len(fails) == 1:
        return fails[0]
    if len(fails) == 2:
        return f"Mixed ({fails[0]}+{fails[1]})"
    return "Mixed (Spatial+Semantic+Data)"


def compute_r7_integrated_gate(
    spatial_pass: int,
    semantic_pass: int,
    data_gate_pass: int,
) -> Dict[str, Any]:
    all_pass = int(bool(spatial_pass) and bool(semantic_pass) and bool(data_gate_pass))
    return {
        "All_gates_pass": all_pass,
        "failure_driver": failure_driver(spatial_pass, semantic_pass, data_gate_pass),
    }
