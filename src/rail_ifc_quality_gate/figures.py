from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .r3_spatial import REGIME_LOCAL, REGIME_PROJECTED_MISMATCH, REGIME_PROJECTED_UTM_M


def set_aic_style() -> None:
    """Set a consistent, journal-friendly style (Automation in Construction-like)."""
    matplotlib.rcParams.update(
        {
            "font.size": 11,
            "axes.titlesize": 12,
            "axes.labelsize": 11,
            "legend.fontsize": 10,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "figure.dpi": 150,
            "savefig.dpi": 300,
        }
    )


def _case_state_label(df: pd.DataFrame) -> pd.Series:
    return df["case"].astype(str) + " — " + df["state"].astype(str)


def fig_r3_scale_regime_distribution(file_level: pd.DataFrame, out_path: Path) -> None:
    set_aic_style()
    df = file_level.copy()
    df["CaseState"] = _case_state_label(df)

    regimes = [REGIME_PROJECTED_UTM_M, REGIME_PROJECTED_MISMATCH, REGIME_LOCAL]
    counts = (
        df.pivot_table(index="CaseState", columns="georef_regime", values="file", aggfunc="count", fill_value=0)
        if "file" in df.columns
        else df.pivot_table(index="CaseState", columns="georef_regime", values="case", aggfunc="size", fill_value=0)
    )
    for r in regimes:
        if r not in counts.columns:
            counts[r] = 0
    counts = counts[regimes]

    ax = counts.plot(kind="bar", stacked=True, figsize=(8.5, 4.5))
    ax.set_ylabel("Number of IFC files")
    ax.set_xlabel("")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.18), ncol=3, frameon=False)
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path)
    plt.close()


def fig_r3_truenorth_scatter(file_level: pd.DataFrame, out_path: Path) -> None:
    set_aic_style()
    df = file_level.copy()
    df["CaseState"] = _case_state_label(df)
    order = list(dict.fromkeys(df["CaseState"].tolist()))
    x = df["CaseState"].apply(lambda v: order.index(v))

    plt.figure(figsize=(8.5, 4.5))
    plt.scatter(x, df["truenorth_deg"], s=25)
    plt.xticks(range(len(order)), order, rotation=20, ha="right")
    plt.ylabel("TrueNorth angle (deg)")
    plt.xlabel("")
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path)
    plt.close()


def fig_r3_anchor_dispersion_scatter(file_level: pd.DataFrame, out_path: Path) -> None:
    set_aic_style()
    df = file_level.copy()
    df["CaseState"] = _case_state_label(df)
    order = list(dict.fromkeys(df["CaseState"].tolist()))
    x = df["CaseState"].apply(lambda v: order.index(v))

    plt.figure(figsize=(8.5, 4.5))
    plt.scatter(x, df["anchor_dispersion_m"], s=25)
    plt.xticks(range(len(order)), order, rotation=20, ha="right")
    plt.ylabel("Anchor dispersion to Case×State median (m)")
    plt.xlabel("")
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path)
    plt.close()


def fig_r4_proxy_boxplot(file_level: pd.DataFrame, out_path: Path) -> None:
    set_aic_style()
    df = file_level.copy()
    df["CaseState"] = _case_state_label(df)
    groups = [g["proxy_pct"].dropna().astype(float).values for _, g in df.groupby("CaseState")]
    labels = [k for k, _ in df.groupby("CaseState")]

    plt.figure(figsize=(8.5, 4.5))
    plt.boxplot(groups, labels=labels, showmeans=True)
    plt.xticks(rotation=20, ha="right")
    plt.ylabel("Proxy ratio (%)")
    plt.xlabel("")
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path)
    plt.close()


def fig_r4_proxy_top20_aggregates(file_level: pd.DataFrame, out_path: Path, top_n: int = 20) -> None:
    """Highest proxy ratios by discipline (top-N aggregates).

    Aggregation unit: Case × State × Discipline.
    Statistic: mean proxy_pct across files in the unit (typically one file per unit).
    """
    set_aic_style()
    df = file_level.copy()

    agg = (
        df.groupby(["case", "state", "discipline"], dropna=False)["proxy_pct"]
        .mean(numeric_only=True)
        .reset_index(name="proxy_pct_mean")
        .sort_values("proxy_pct_mean", ascending=False)
        .head(int(top_n))
    )
    agg["label"] = agg.apply(lambda r: f"{r['case']} {r['state']} / {r['discipline']}", axis=1)

    # Plot highest at top
    agg = agg.iloc[::-1].reset_index(drop=True)

    plt.figure(figsize=(8.5, 6.0))
    plt.barh(range(len(agg)), agg["proxy_pct_mean"].astype(float).values)
    plt.yticks(range(len(agg)), agg["label"].tolist())
    plt.xlabel("Proxy ratio (%)")
    plt.ylabel("")
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path)
    plt.close()


def fig_r5_overallI_boxplot(file_level: pd.DataFrame, out_path: Path) -> None:
    set_aic_style()
    df = file_level.copy()
    df["CaseState"] = _case_state_label(df)
    groups = [g["overall_I"].dropna().astype(float).values for _, g in df.groupby("CaseState")]
    labels = [k for k, _ in df.groupby("CaseState")]

    plt.figure(figsize=(8.5, 4.5))
    plt.boxplot(groups, labels=labels, showmeans=True)
    plt.xticks(rotation=20, ha="right")
    plt.ylabel("overall_I (0–1)")
    plt.xlabel("")
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path)
    plt.close()


def fig_r6_ipass_by_pset(
    per_pset: pd.DataFrame,
    out_path: Path,
    design_state: str = "PC",
    executed_state: str = "EW",
) -> None:
    """Informational pass rate by PSET (design vs executed works).

    This is a convenience figure for benchmarking typical pipelines where
    design (PC) and executed works (EW) are contrasted.
    """
    set_aic_style()
    df = per_pset.copy()

    # Normalize column names
    if "PSET" in df.columns and "pset" not in df.columns:
        df = df.rename(columns={"PSET": "pset"})

    # Pick the most populated Case×State for each group
    def _pick_cs(dfg: pd.DataFrame) -> Optional[tuple[str, str]]:
        if dfg.empty:
            return None
        counts = dfg.groupby(["case", "state"]).size().sort_values(ascending=False)
        return tuple(counts.index[0])  # type: ignore

    design_df = df[df["state"].astype(str).str.contains(design_state, na=False)]
    exec_df = df[df["state"].astype(str).str.contains(executed_state, na=False)]
    cs_design = _pick_cs(design_df)
    cs_exec = _pick_cs(exec_df)

    if cs_design is None or cs_exec is None:
        return

    d1 = df[(df["case"] == cs_design[0]) & (df["state"] == cs_design[1])]
    d2 = df[(df["case"] == cs_exec[0]) & (df["state"] == cs_exec[1])]

    a1 = d1.groupby("pset")["I_pass"].mean().rename("design")
    a2 = d2.groupby("pset")["I_pass"].mean().rename("executed")
    out = pd.concat([a1, a2], axis=1).fillna(0.0)
    out = out.sort_index()

    psets = out.index.tolist()
    x = np.arange(len(psets))
    width = 0.38

    plt.figure(figsize=(9.0, 4.8))
    plt.bar(x - width / 2, out["design"].astype(float).values, width, label=f"{cs_design[0]} — {cs_design[1]}")
    plt.bar(x + width / 2, out["executed"].astype(float).values, width, label=f"{cs_exec[0]} — {cs_exec[1]}")
    plt.xticks(x, psets, rotation=20, ha="right")
    plt.ylabel("I-pass rate (fraction of IFCs passing)")
    plt.xlabel("")
    plt.legend(loc="upper center", bbox_to_anchor=(0.5, 1.18), ncol=2, frameon=False)
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path)
    plt.close()


def fig_r6_bottom_ipass_psets(per_pset: pd.DataFrame, out_path: Path, bottom_k: int = 3) -> None:
    """Lowest I-pass PSETs by Case×State (bottom-k per package)."""
    set_aic_style()
    df = per_pset.copy()
    if "PSET" in df.columns and "pset" not in df.columns:
        df = df.rename(columns={"PSET": "pset"})

    agg = (
        df.groupby(["case", "state", "pset"], dropna=False)["I_pass"]
        .mean(numeric_only=True)
        .reset_index(name="I_pass_rate")
    )
    bottom = agg.groupby(["case", "state"], group_keys=False).apply(lambda g: g.nsmallest(int(bottom_k), "I_pass_rate"))
    bottom = bottom.sort_values("I_pass_rate", ascending=True)
    bottom["label"] = bottom.apply(lambda r: f"{r['case']}|{r['state']}|{r['pset']}", axis=1)

    plt.figure(figsize=(9.0, 4.8))
    plt.bar(range(len(bottom)), bottom["I_pass_rate"].astype(float).values)
    plt.xticks(range(len(bottom)), bottom["label"].tolist(), rotation=55, ha="right")
    plt.ylabel("I-pass rate (fraction)")
    plt.xlabel("")
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path)
    plt.close()


def fig_r7_pass_rates(file_level: pd.DataFrame, out_path: Path) -> None:
    set_aic_style()
    df = file_level.copy()
    df["CaseState"] = _case_state_label(df)

    agg = df.groupby("CaseState").agg(
        Spatial=("spatial_pass", "mean"),
        Semantic=("semantic_pass", "mean"),
        Data=("Data_gate_pass", "mean"),
        All_gates=("All_gates_pass", "mean"),
    )
    agg = agg * 100.0

    ax = agg.plot(kind="bar", figsize=(8.5, 4.8))
    ax.set_ylabel("Pass rate (%)")
    ax.set_xlabel("")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.18), ncol=4, frameon=False)
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path)
    plt.close()


def fig_r7_outcomes_drivers(file_level: pd.DataFrame, out_path: Path) -> None:
    set_aic_style()
    df = file_level.copy()
    df["CaseState"] = _case_state_label(df)

    # Count drivers per case/state
    pivot = df.pivot_table(index="CaseState", columns="failure_driver", values="case", aggfunc="size", fill_value=0)

    driver_order = [
        "Pass",
        "Spatial",
        "Semantic",
        "Data",
        "Mixed (Spatial+Semantic)",
        "Mixed (Spatial+Data)",
        "Mixed (Semantic+Data)",
        "Mixed (Spatial+Semantic+Data)",
    ]
    for c in driver_order:
        if c not in pivot.columns:
            pivot[c] = 0
    pivot = pivot[driver_order]

    ax = pivot.plot(kind="bar", stacked=True, figsize=(8.5, 4.8))
    ax.set_ylabel("Number of IFC files")
    ax.set_xlabel("")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.20), ncol=4, frameon=False)
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path)
    plt.close()


def generate_all_default_figures(
    file_level_csv: str | Path,
    out_dir: str | Path,
    per_pset_csv: Optional[str | Path] = None,
) -> None:
    df = pd.read_csv(file_level_csv)
    df_pset = None
    if per_pset_csv:
        try:
            df_pset = pd.read_csv(per_pset_csv)
        except Exception:
            df_pset = None

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    fig_r3_scale_regime_distribution(df, out_dir / "Figure_02_R3-1_SpatialScaleRegime.png")
    fig_r3_truenorth_scatter(df, out_dir / "Figure_03_R3-2_TrueNorthOrientation.png")
    fig_r3_anchor_dispersion_scatter(df, out_dir / "Figure_04_R3-3_AnchorDispersion.png")
    fig_r4_proxy_boxplot(df, out_dir / "Figure_05_R4-1_ProxyRatioBoxplot.png")
    fig_r4_proxy_top20_aggregates(df, out_dir / "Figure_06_R4-2_ProxyTop20Aggregates.png")
    fig_r5_overallI_boxplot(df, out_dir / "Figure_07_R5_overallI.png")
    if df_pset is not None:
        fig_r6_ipass_by_pset(df_pset, out_dir / "Figure_08_R6-1_IpassByPSET.png")
        fig_r6_bottom_ipass_psets(df_pset, out_dir / "Figure_09_R6-3_BottomIpassPSETs.png")
    fig_r7_pass_rates(df, out_dir / "Figure_10_R7-1_QualityGatePassRates.png")
    fig_r7_outcomes_drivers(df, out_dir / "Figure_11_QualityGateOutcomesDrivers.png")
