from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import yaml

from .r3_spatial import REGIME_PROJECTED_UTM_M


def load_sensitivity_config(path: str | Path) -> Dict[str, Any]:
    p = Path(path)
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def _recompute_spatial_pass(df: pd.DataFrame, tol_mult: float) -> pd.Series:
    tau_eff = df["tau_m"].astype(float) * float(tol_mult)
    return (
        (df["georef_regime"] == REGIME_PROJECTED_UTM_M)
        & (df["anchor_dispersion_m"].astype(float) <= tau_eff)
        & (df["truenorth_outlier"].astype(int) == 0)
    ).astype(int)


def _recompute_semantic_pass(df: pd.DataFrame, proxy_threshold_pct: float) -> pd.Series:
    return (df["proxy_pct"].astype(float) < float(proxy_threshold_pct)).astype(int)


def run_sensitivity(
    file_level_csv: str | Path,
    sensitivity_yaml: str | Path,
    out_dir: str | Path,
) -> pd.DataFrame:
    """Run a simple what-if sweep around thresholds.

    The sensitivity config supports:
    - tol_mult: list of multipliers applied to discipline-aware tau_m
    - proxy_thresholds_pct: list of proxy thresholds (percent)
    """
    cfg = load_sensitivity_config(sensitivity_yaml)
    tol_mults = cfg.get("tol_mult", [0.9, 1.0, 1.1])
    proxy_thresholds = cfg.get("proxy_thresholds_pct", [40, 50, 60])

    df = pd.read_csv(file_level_csv)

    rows: List[Dict[str, Any]] = []
    for tm in tol_mults:
        spatial = _recompute_spatial_pass(df, tm)
        for pt in proxy_thresholds:
            semantic = _recompute_semantic_pass(df, pt)
            # Data gate kept as recorded in file-level outputs (contractual gate)
            data_gate = df["Data_gate_pass"].astype(int) if "Data_gate_pass" in df.columns else 0
            all_pass = (spatial & semantic & data_gate).astype(int)

            rows.append(
                {
                    "tol_mult": float(tm),
                    "proxy_threshold_pct": float(pt),
                    "All_gates_pass_rate": float(all_pass.mean()) if len(all_pass) else float("nan"),
                    "Spatial_pass_rate": float(spatial.mean()) if len(spatial) else float("nan"),
                    "Semantic_pass_rate": float(semantic.mean()) if len(semantic) else float("nan"),
                    "Data_gate_pass_rate": float(data_gate.mean()) if len(df) else float("nan"),
                    "N_files": int(len(df)),
                }
            )

    out_df = pd.DataFrame(rows)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out_dir / "sensitivity_summary.csv", index=False)
    return out_df
