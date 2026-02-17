from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import yaml

from . import __version__
from .ifc_io import open_ifc
from .reporting_units import infer_from_filename, load_discipline_domains
from .r3_spatial import compute_r3_preliminary, postprocess_r3_group
from .r4_semantic import compute_r4_metrics
from .r5_overallI import compute_r5_overallI
from .r6_data_gate import load_owner_profile, compute_r6_data_gate
from .r7_integrated_gate import compute_r7_integrated_gate
from .calibration import calibrate_from_file_level_outputs
from .sensitivity import run_sensitivity
from .figures import generate_all_default_figures


def _load_yaml(path: str | Path) -> Dict[str, Any]:
    p = Path(path)
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def cmd_run(args: argparse.Namespace) -> int:
    cfg = _load_yaml(args.config)

    ifc_dir = Path(args.ifc_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load mappings and thresholds
    discipline_domains = load_discipline_domains(cfg["mappings"]["discipline_domains"])
    discipline_to_tau = {}
    for disc, meta in discipline_domains.items():
        tau = meta.get("tau_m", None)
        if tau is not None:
            discipline_to_tau[disc] = float(tau)

    thresholds = _load_yaml(cfg["thresholds"]["baseline"])
    proxy_thr = float(thresholds.get("proxy_threshold_pct", 50.0))
    s_presence_thr = float(thresholds.get("S_presence_threshold", 0.95))
    i_fill_thr = float(thresholds.get("I_fill_threshold", 0.80))

    owner_profile = load_owner_profile(cfg["profiles"]["owner_profile"])

    # Gather IFC files
    ifc_files = sorted([p for p in ifc_dir.rglob("*.ifc") if p.is_file()])
    if not ifc_files:
        raise SystemExit(f"No IFC files found under: {ifc_dir}")

    file_rows: List[Dict[str, Any]] = []
    per_pset_rows_all: List[Dict[str, Any]] = []

    for fp in ifc_files:
        ru = infer_from_filename(fp, discipline_domains)
        model = open_ifc(fp)

        r3 = compute_r3_preliminary(model)
        r4 = compute_r4_metrics(model, proxy_threshold_pct=proxy_thr)
        r6 = compute_r6_data_gate(
            model=model,
            state=ru.state,
            discipline_domain=ru.domain,
            owner_profile=owner_profile,
            s_presence_threshold=s_presence_thr,
            i_fill_threshold=i_fill_thr,
        )
        r5 = compute_r5_overallI(r6["per_pset_rows"])
        # Placeholder spatial_pass added later (group-aware)
        row = {
            "schema_version": __version__,
            "file": fp.name,
            "case": ru.case,
            "state": ru.state,
            "discipline": ru.discipline,
            "domain": ru.domain,
            "ifc_schema": model.schema(),
            **r3,
            **r4,
            "Data_gate_pass": int(r6["Data_gate_pass"]),
            "nopk_align_flag": int(r6.get("nopk_align_flag", 0)),
            "S_presence_threshold": s_presence_thr,
            "I_fill_threshold": i_fill_thr,
            **r5,
            "profile_name": r6.get("profile_name", ""),
        }
        file_rows.append(row)

        # Store per-PSET metrics (R6 evidence)
        for pr in r6["per_pset_rows"]:
            pset_name = pr.get("pset") or pr.get("PSET")
            per_pset_rows_all.append(
                {
                    "schema_version": __version__,
                    "file": fp.name,
                    "case": ru.case,
                    "state": ru.state,
                    "discipline": ru.discipline,
                    "domain": ru.domain,
                    "pset": pset_name,
                    **{k: v for k, v in pr.items() if k not in ("PSET", "pset")},
                    "profile_name": r6.get("profile_name", ""),
                }
            )

    df = pd.DataFrame(file_rows)

    # Add discipline-aware tau if missing
    if "tau_m" not in df.columns or df["tau_m"].isna().all():
        df["tau_m"] = df["discipline"].map(discipline_to_tau)

    # R3 postprocess (Case×State medians, outliers, spatial_pass)
    df = postprocess_r3_group(df, discipline_to_tau_m=discipline_to_tau)

    # R7 integrated gate + driver
    r7 = df.apply(
        lambda r: compute_r7_integrated_gate(int(r["spatial_pass"]), int(r["semantic_pass"]), int(r["Data_gate_pass"])),
        axis=1,
        result_type="expand",
    )
    df = pd.concat([df, r7], axis=1)

    # Save outputs
    # Persist a full diagnostic file (all intermediate columns) and a stable public schema
    file_level_full_csv = out_dir / "file_level_outputs_full.csv"
    df.to_csv(file_level_full_csv, index=False)

    public_cols = [
        "schema_version",
        "file",
        "case",
        "state",
        "discipline",
        "domain",
        "ifc_schema",
        "georef_regime",
        "truenorth_deg",
        "truenorth_outlier",
        "anchor_dispersion_m",
        "tau_m",
        "spatial_pass",
        "proxy_pct",
        "semantic_pass",
        "overall_I",
        "Data_gate_pass",
        "nopk_align_flag",
        "All_gates_pass",
        "failure_driver",
        "proxy_threshold_pct",
        "S_presence_threshold",
        "I_fill_threshold",
        "profile_name",
    ]
    # Ensure the stable schema exists even if some optional columns are missing.
    for c in public_cols:
        if c not in df.columns:
            df[c] = pd.NA
    file_level_csv = out_dir / "file_level_outputs.csv"
    df[public_cols].to_csv(file_level_csv, index=False)

    per_pset_csv = out_dir / "per_pset_outputs.csv"
    per_pset_df = pd.DataFrame(per_pset_rows_all)
    per_pset_public_cols = [
        "schema_version",
        "file",
        "case",
        "state",
        "discipline",
        "domain",
        "pset",
        "S_presence",
        "I_fill",
        "S_pass",
        "I_pass",
        "n_required_fields",
        "S_presence_threshold",
        "I_fill_threshold",
        "profile_name",
    ]
    for c in per_pset_public_cols:
        if c not in per_pset_df.columns:
            per_pset_df[c] = pd.NA
    per_pset_df[per_pset_public_cols].to_csv(per_pset_csv, index=False)

    # Case×State summary
    df["case_state"] = df["case"].astype(str) + "×" + df["state"].astype(str)
    summary = (
        df.groupby("case_state")
        .agg(
            N_files=("file", "count"),
            Spatial_pass_rate=("spatial_pass", "mean"),
            Semantic_pass_rate=("semantic_pass", "mean"),
            Data_gate_pass_rate=("Data_gate_pass", "mean"),
            All_gates_pass_rate=("All_gates_pass", "mean"),
        )
        .reset_index()
    )
    summary.to_csv(out_dir / "case_state_summary.csv", index=False)

    if args.figures:
        generate_all_default_figures(file_level_csv=file_level_csv, per_pset_csv=per_pset_csv, out_dir=out_dir / "figures")

    print(f"Wrote: {file_level_full_csv}")
    print(f"Wrote: {file_level_csv}")
    print(f"Wrote: {per_pset_csv}")
    print(f"Wrote: {out_dir / 'case_state_summary.csv'}")
    return 0


def cmd_calibrate(args: argparse.Namespace) -> int:
    calib = calibrate_from_file_level_outputs(
        file_level_csv=args.file_level,
        out_path=args.out,
        proxy_quantile=args.proxy_quantile,
        anchor_quantile=args.anchor_quantile,
    )
    print(yaml.safe_dump(calib, sort_keys=False))
    return 0


def cmd_sensitivity(args: argparse.Namespace) -> int:
    out_df = run_sensitivity(args.file_level, args.config, args.out_dir)
    print(out_df.to_string(index=False))
    return 0


def cmd_figures(args: argparse.Namespace) -> int:
    generate_all_default_figures(args.file_level, args.out_dir, per_pset_csv=getattr(args, "per_pset", None))
    print(f"Wrote figures under: {args.out_dir}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="rail-ifc-quality-gate", add_help=True)
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sub = p.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", help="Run R3–R7 pipeline on a folder of IFC files.")
    run.add_argument("--ifc-dir", required=True)
    run.add_argument("--config", required=True, help="YAML config (paths to thresholds/profiles/mappings).")
    run.add_argument("--out-dir", required=True)
    run.add_argument("--figures", action="store_true", help="Generate default figures (PNG) from outputs.")
    run.set_defaults(func=cmd_run)

    cal = sub.add_parser("calibrate", help="Calibrate threshold suggestions from file-level outputs.")
    cal.add_argument("--file-level", required=True)
    cal.add_argument("--out", required=True)
    cal.add_argument("--proxy-quantile", type=float, default=0.5)
    cal.add_argument("--anchor-quantile", type=float, default=0.95)
    cal.set_defaults(func=cmd_calibrate)

    sen = sub.add_parser("sensitivity", help="Run threshold sensitivity sweeps.")
    sen.add_argument("--file-level", required=True)
    sen.add_argument("--config", required=True)
    sen.add_argument("--out-dir", required=True)
    sen.set_defaults(func=cmd_sensitivity)

    fig = sub.add_parser("figures", help="Generate figures from file-level outputs.")
    fig.add_argument("--file-level", required=True)
    fig.add_argument("--per-pset", required=False, default=None, help="Optional per-PSET outputs CSV (enables R6 figures).")
    fig.add_argument("--out-dir", required=True)
    fig.set_defaults(func=cmd_figures)

    return p


def main(argv: List[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
