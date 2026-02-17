# rail-ifc-quality-gate

Tool-independent, computable quality metrics and an integrated publish/hold **quality gate** for rail/linear and depot BIM deliverables in **openBIM / IFC**.

This repository provides an **executable reference implementation** of the R3–R7 pipeline described in the companion manuscript(s):

- **R3** Spatial audit (georeferencing regime, TrueNorth coherence, anchor dispersion)
- **R4** Semantic audit (proxy ratio via `IfcBuildingElementProxy`)
- **R5** File-level information completeness KPI (`overall_I`, continuous)
- **R6** Data gate (core PSET by stage; `S_pass` / `I_pass`)
- **R7** Integrated gate (`Spatial ∧ Semantic ∧ Data`) + failure-driver attribution

> **Important**: Real project IFC deliverables and owner documents are often confidential.  
> This repo is designed so you can run the pipeline on your own data locally, and publish **non-sensitive derived outputs** (aggregated indicators) and/or **synthetic benchmarks**.

## Quickstart (CLI)

### 1) Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

If you want IFC parsing via IfcOpenShell:

```bash
pip install -r requirements.txt
```

### 2) Run on an IFC folder

```bash
rail-ifc-quality-gate run \
  --ifc-dir path/to/ifc_folder \
  --config examples/example_config.yml \
  --out-dir outputs/
```

This produces:

- `outputs/file_level_outputs.csv`
- `outputs/case_state_summary.csv`
- `outputs/figures/` (optional)

### 3) Sensitivity analysis

```bash
rail-ifc-quality-gate sensitivity \
  --file-level outputs/file_level_outputs.csv \
  --config configs/thresholds/sensitivity_ranges.yml \
  --out-dir outputs/sensitivity/
```

### 4) Generate paper figures

```bash
rail-ifc-quality-gate figures \
  --file-level outputs/file_level_outputs.csv \
  --case-state outputs/case_state_summary.csv \
  --out-dir outputs/figures/
```

## Repository layout

See the full structure in this repo. The most relevant folders:

- `src/rail_ifc_quality_gate/` — core implementation
- `configs/` — thresholds, profiles, and mappings
- `docs/` — methodology and benchmarking protocol
- `docs/ifc-quality-gate_outputs_dictionary_v1.0.0.*` — formal CSV output schema (columns, types, units).
- `scripts/` — thin wrappers (one-command runs)
- `examples/` — non-sensitive toy example + example configs
- `docker/` — containerized execution

## Citation

If you use this software in academic work, please cite it using `CITATION.cff`.

## License

MIT License — see `LICENSE-MIT.txt`.

## Version

v1.0.2 (2026-02-13)
