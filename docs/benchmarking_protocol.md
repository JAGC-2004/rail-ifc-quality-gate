# Benchmarking protocol

Goal: allow *tool-to-tool* and *portfolio-to-portfolio* comparisons using a common
set of computable metrics.

1. Select an owner profile (or build one using the template).
2. Run the pipeline on the target IFC corpus.
3. Export:
   - file-level outputs (`file_level_outputs.csv`)
   - Case×State summary (`case_state_summary.csv`)
4. Compare:
   - pass rates by gate
   - distributional KPIs (proxy_pct, overall_I)
   - failure drivers and hotspots

For cross-tool benchmarking, you can implement the same metric definitions in a different tool
and compare against the published CSV schemas.
