# Methodology summary (paper-aligned)

This repo implements an IFC file-level audit pipeline that produces:
- file-level audit records (R3–R7 metrics + flags),
- aggregated Case×State indicators, and
- diagnostic charts and failure-driver attribution.

## Metric suite overview

### R3 Spatial audit
- Georeferencing regime classification
- TrueNorth angle extraction + outlier flag (robust median-based)
- Anchor extraction from IFC placement + Case×State dispersion

### R4 Semantic audit
- `proxy_pct = count(IfcBuildingElementProxy) / count(IfcElement) * 100`
- `Semantic_pass = proxy_pct < proxy_threshold_pct`

### R5 Information completeness KPI
- `overall_I` is a continuous KPI (0..1) aggregated from per-PSET completeness indicators.

### R6 Data gate
- Stage-specific core PSET profile (EX/PC/EW).
- `Data_gate_pass = AND(I_pass(core PSETs))`
- Thresholds: `S_presence_threshold`, `I_fill_threshold`.

### R7 Integrated gate
- `All_gates_pass = Spatial_pass ∧ Semantic_pass ∧ Data_gate_pass`
- Failure-driver attribution: Spatial / Semantic / Data / Mixed.

See `configs/` for thresholds and profiles.
