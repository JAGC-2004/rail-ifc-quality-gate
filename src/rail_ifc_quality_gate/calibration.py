from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd
import yaml


def suggest_threshold(series: pd.Series, quantile: float, higher_is_better: bool = True) -> float:
    """Suggest a threshold value based on a quantile of observed data."""
    s = series.dropna().astype(float)
    if s.empty:
        return float("nan")
    q = float(s.quantile(quantile))
    return q if higher_is_better else q


def calibrate_from_file_level_outputs(
    file_level_csv: str | Path,
    out_path: str | Path,
    proxy_quantile: float = 0.5,
    anchor_quantile: float = 0.95,
) -> Dict[str, Any]:
    """Example calibration helper.

    This function does NOT claim universal optimality. It merely documents a repeatable
    calibration procedure that can be reused across owners/portfolios without
    re-engineering the pipeline code.
    """
    df = pd.read_csv(file_level_csv)

    proxy_thr = suggest_threshold(df["proxy_pct"], quantile=proxy_quantile, higher_is_better=False)
    anchor_thr = suggest_threshold(df["anchor_dispersion_m"], quantile=anchor_quantile, higher_is_better=False)

    calib = {
        "proxy_threshold_pct": float(proxy_thr) if not np.isnan(proxy_thr) else 50.0,
        "anchor_dispersion_quantile_thr_m": float(anchor_thr) if not np.isnan(anchor_thr) else 5.0,
        "proxy_quantile": proxy_quantile,
        "anchor_quantile": anchor_quantile,
        "notes": "Calibration is operational and owner-configurable; do not treat as universal optimum.",
    }

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(yaml.safe_dump(calib, sort_keys=False), encoding="utf-8")
    return calib
