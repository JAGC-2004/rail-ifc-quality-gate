from __future__ import annotations

from typing import Any, Dict, Iterable, List

import numpy as np


def overall_I_from_psets(i_fill_values: Iterable[float]) -> float:
    vals = [float(v) for v in i_fill_values if v is not None and not np.isnan(v)]
    if not vals:
        return float("nan")
    return float(np.mean(vals))


def compute_r5_overallI(per_pset_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute file-level completeness KPI overall_I.

    Paper-aligned interpretation:
    - overall_I is a continuous KPI (0..1) used for diagnostics and prioritization.
    - It is *not* used as a hard acceptance gate; contractual acceptance is via Data_gate_pass.
    """
    vals = [r.get("I_fill") for r in per_pset_rows]
    overall_i = overall_I_from_psets([v for v in vals if v is not None])
    return {
        "overall_I": overall_i,
        "overall_I_n_psets": len([v for v in vals if v is not None and not np.isnan(v)]),
    }
