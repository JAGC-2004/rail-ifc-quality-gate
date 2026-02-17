# IFC Quality Gate — Output Data Dictionary (v1.0.0)

Schema version covered: **1.0.1**

## file_level_outputs.csv

| column               | type   | unit        | description                                                                                                                          |
|:---------------------|:-------|:------------|:-------------------------------------------------------------------------------------------------------------------------------------|
| schema_version       | string | -           | Semantic version of the public output schema produced by the pipeline.                                                               |
| file                 | string | -           | IFC filename (no directory).                                                                                                         |
| case                 | string | -           | Case identifier (anonymized portfolio/site tag).                                                                                     |
| state                | string | -           | Delivery state tag used to select stage-specific profiles and reporting.                                                             |
| discipline           | string | -           | Discipline code inferred from filename (project taxonomy).                                                                           |
| domain               | string | -           | Hybrid-asset domain class used for discipline-aware rules.                                                                           |
| ifc_schema           | string | -           | IFC schema declared by the parsed file.                                                                                              |
| georef_regime        | string | -           | Spatial scale / georeferencing regime classification (R3).                                                                           |
| truenorth_deg        | float  | deg         | TrueNorth azimuth extracted from the geometric representation context (0° aligned to +Y). NaN if missing.                            |
| truenorth_outlier    | int    | -           | 1 if TrueNorth deviates more than the outlier threshold from the Case×State median; else 0.                                          |
| anchor_dispersion_m  | float  | m           | Euclidean distance between the file anchor point and the Case×State median anchor (R3 inter-model consistency).                      |
| tau_m                | float  | m           | Discipline-aware anchor tolerance τ(disc) used for the Spatial gate.                                                                 |
| spatial_pass         | int    | -           | Spatial gate outcome (R3): projected UTM/m regime AND anchor_dispersion_m ≤ tau_m AND truenorth_outlier=0.                           |
| proxy_pct            | float  | %           | Semantic proxy ratio (R4): count(IfcBuildingElementProxy)/count(IfcElement)×100. NaN if no IfcElement.                               |
| semantic_pass        | int    | -           | Semantic gate outcome (R4): 1 if proxy_pct < proxy_threshold_pct; else 0.                                                            |
| overall_I            | float  | ratio (0–1) | Continuous file-level information completeness KPI (R5): mean(I_fill) across core PSETs.                                             |
| Data_gate_pass       | int    | -           | Binary Data gate outcome (R6): AND across I_pass(core PSET profile by stage).                                                        |
| nopk_align_flag      | int    | -           | Linear-discipline diagnostic: 1 if no PK/alignment-related property names were detected; else 0. Not used as a hard gate by default. |
| All_gates_pass       | int    | -           | Integrated gate (R7): spatial_pass ∧ semantic_pass ∧ Data_gate_pass.                                                                 |
| failure_driver       | string | -           | Failure attribution label derived from which gates failed (R7).                                                                      |
| proxy_threshold_pct  | float  | %           | Configured threshold for the Semantic gate.                                                                                          |
| S_presence_threshold | float  | ratio (0–1) | Configured S_presence threshold used when computing per-PSET metrics (presence/coverage).                                            |
| I_fill_threshold     | float  | ratio (0–1) | Configured I_fill threshold used when computing per-PSET metrics (required-field fill).                                              |
| profile_name         | string | -           | Owner profile identifier used to select core PSETs and required fields.                                                              |

## per_pset_outputs.csv

| column               | type   | unit        | description                                                                                      |
|:---------------------|:-------|:------------|:-------------------------------------------------------------------------------------------------|
| schema_version       | string | -           | Semantic version of the public output schema produced by the pipeline.                           |
| file                 | string | -           | IFC filename (no directory).                                                                     |
| case                 | string | -           | Case identifier (anonymized).                                                                    |
| state                | string | -           | Delivery state tag.                                                                              |
| discipline           | string | -           | Discipline code inferred from filename.                                                          |
| domain               | string | -           | Hybrid-asset domain class.                                                                       |
| pset                 | string | -           | Property set group evaluated for this stage profile (core PSET).                                 |
| S_presence           | float  | ratio (0–1) | Presence/coverage indicator for the PSET in the IFC (file-level, best-effort). Typically 0 or 1. |
| I_fill               | float  | ratio (0–1) | Fraction of required fields in the PSET that are non-empty (file-level).                         |
| S_pass               | int    | -           | Pass flag for presence check against S_presence_threshold.                                       |
| I_pass               | int    | -           | Pass flag for required-field fill against thresholds (presence + I_fill ≥ I_fill_threshold).     |
| n_required_fields    | int    | count       | Number of required fields configured for this PSET in the owner profile.                         |
| S_presence_threshold | float  | ratio (0–1) | Configured threshold for S_presence.                                                             |
| I_fill_threshold     | float  | ratio (0–1) | Configured threshold for I_fill.                                                                 |
| profile_name         | string | -           | Owner profile identifier.                                                                        |

## case_state_summary.csv

| column              | type   | unit        | description                                                         |
|:--------------------|:-------|:------------|:--------------------------------------------------------------------|
| case                | string | -           | Case identifier (anonymized).                                       |
| state               | string | -           | Delivery state tag.                                                 |
| case_state          | string | -           | Composite reporting unit (case × state).                            |
| N_files             | int    | count       | Number of IFC files in the reporting unit.                          |
| Spatial_pass_rate   | float  | ratio (0–1) | Mean spatial_pass across files in the reporting unit.               |
| Semantic_pass_rate  | float  | ratio (0–1) | Mean semantic_pass across files in the reporting unit.              |
| Data_gate_pass_rate | float  | ratio (0–1) | Mean Data_gate_pass across files in the reporting unit.             |
| All_gates_pass_rate | float  | ratio (0–1) | Mean All_gates_pass across files in the reporting unit.             |
| overall_I_mean      | float  | ratio (0–1) | Mean overall_I across files in the reporting unit (diagnostic KPI). |

## figure_source_tables.xlsx

This workbook contains figure source/pivot tables derived from the public CSV outputs.
