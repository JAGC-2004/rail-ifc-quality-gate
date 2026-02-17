# Transferability and calibration

This project separates:
- **Transferable method**: metric definitions + pipeline architecture + evidence schema
- **Configurable parameters**: thresholds, stage profiles, and mapping rules

## How to calibrate without re-engineering
1. Start with baseline thresholds (`configs/thresholds/baseline.yml`).
2. Define the owner profile (core PSET groups by stage) in YAML.
3. Run the pipeline on a representative subset of deliverables.
4. Use `rail-ifc-quality-gate calibrate ...` to generate documented threshold suggestions.
5. Validate via sensitivity analysis (`tol_mult`, threshold sweeps).

The scientific contribution is the repeatable procedure and auditable evidence, not the exact numeric threshold.
