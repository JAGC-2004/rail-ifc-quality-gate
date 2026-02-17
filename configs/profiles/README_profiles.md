# Owner profiles

Owner profiles are **configuration files** that define:
- stage-specific *core PSET groups* used for the contractual Data Gate (R6)
- (optional) required fields within each PSET group

The pipeline is designed so **transferability resides in the profile + thresholds**, not in
hard-coded numbers.

Files in this folder:
- `owner_profile_O0_generic_min.yml` — minimal generic profile (placeholder)
- `owner_profile_O1_design_stage.yml` — example design-stage profile
- `owner_profile_O2_executedworks_stage.yml` — example executed-works profile
- `owner_profile_case_study_anonymized.yml` — anonymized case-study-like mapping (no sensitive names)

To build your own profile, start from `configs/mappings/pset_field_mapping_template.yml`.
