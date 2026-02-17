# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

## [1.0.2] - 2026-02-13
### Added
- Formal output data dictionary (docs/ifc-quality-gate_outputs_dictionary_v1.0.0.{xlsx,md,yml}) describing columns, types, units and meanings.

## [1.0.1] - 2026-02-13
### Added
- Minimal GitHub Actions CI workflow (ruff + pytest across Python 3.10–3.12).

### Changed
- CSV outputs now follow a stable, paper-aligned public schema (`file_level_outputs.csv`, `per_pset_outputs.csv`), with full diagnostics kept in `file_level_outputs_full.csv`.
- Failure-driver labels are now expanded to distinguish multi-failure combinations (e.g., `Mixed (Spatial+Data)`) to support stacked-driver reporting.
- Figure generation now includes proxy top-20 aggregates (R4) and R6 PSET-level figures when per-PSET outputs are provided.

## [1.0.0] - 2026-02-13
### Added
- First public release of the executable R3–R7 pipeline.
- CLI commands: `run`, `calibrate`, `sensitivity`, `figures`, `benchmark-build`.
- Config-driven thresholds and owner profiles.
- Synthetic benchmark generator scaffold and toy example IFC.
