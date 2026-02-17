from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import yaml

from .ifc_io import IfcModel, get_property_sets


@dataclass
class OwnerProfile:
    name: str
    core_psets_by_state: Dict[str, List[str]]
    required_fields_by_pset: Dict[str, List[str]]
    handover_psets_by_state: Dict[str, List[str]] | None = None
    linear_pk_align_keywords: Tuple[str, ...] = ("PK", "ALIGN")


def load_owner_profile(path: str | Path) -> OwnerProfile:
    p = Path(path)
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    name = data.get("name", p.stem)

    core = data.get("core_psets_by_state", {})
    required = data.get("required_fields_by_pset", {})
    handover = data.get("handover_psets_by_state", None)
    keywords = tuple(data.get("linear_pk_align_keywords", ["PK", "ALIGN"]))
    return OwnerProfile(
        name=name,
        core_psets_by_state=core,
        required_fields_by_pset=required,
        handover_psets_by_state=handover,
        linear_pk_align_keywords=keywords,
    )


def _non_empty(v: Any) -> bool:
    if v is None:
        return False
    if isinstance(v, str) and v.strip() == "":
        return False
    return True


def compute_per_pset_metrics(
    file_psets: Dict[str, Dict[str, Any]],
    pset_name: str,
    s_presence_threshold: float = 0.95,
    i_fill_threshold: float = 0.80,
    required_fields: Optional[List[str]] = None,
) -> Dict[str, Any]:
    present = 1 if pset_name in file_psets else 0
    props = file_psets.get(pset_name, {}) if present else {}

    req = required_fields or []
    if present and req:
        filled = sum(1 for f in req if _non_empty(props.get(f)))
        i_fill = filled / len(req) if len(req) else float("nan")
    elif present:
        # If no required fields provided, treat as 'presence only' PSET.
        i_fill = 1.0
    else:
        i_fill = 0.0

    s_pass = int(present >= s_presence_threshold)  # with binary presence
    i_pass = int((present >= s_presence_threshold) and (i_fill >= i_fill_threshold))

    return {
        "PSET": pset_name,
        "S_presence": float(present),
        "I_fill": float(i_fill),
        "S_pass": s_pass,
        "I_pass": i_pass,
        "S_presence_threshold": s_presence_threshold,
        "I_fill_threshold": i_fill_threshold,
        "n_required_fields": len(req),
    }


def compute_r6_data_gate(
    model: IfcModel,
    state: str,
    discipline_domain: str,
    owner_profile: OwnerProfile,
    s_presence_threshold: float = 0.95,
    i_fill_threshold: float = 0.80,
) -> Dict[str, Any]:
    """Compute per-PSET data metrics (R6) and the binary Data Gate outcome.

    - Data_gate_pass is contractual acceptance for the *core PSET profile* of the stage.
    - overall_I (R5) remains continuous and is not used as the binary gate.
    """
    file_psets = get_property_sets(model)

    core_psets = owner_profile.core_psets_by_state.get(state, [])
    per_pset_rows: List[Dict[str, Any]] = []
    for pset in core_psets:
        per_pset_rows.append(
            compute_per_pset_metrics(
                file_psets=file_psets,
                pset_name=pset,
                s_presence_threshold=s_presence_threshold,
                i_fill_threshold=i_fill_threshold,
                required_fields=owner_profile.required_fields_by_pset.get(pset, []),
            )
        )

    # AND across core PSETs
    if core_psets:
        data_gate_pass = int(all(r["I_pass"] == 1 for r in per_pset_rows))
    else:
        data_gate_pass = 0

    # Optional: linear PK/Alignment check (diagnostic only, unless you treat it as a gate)
    nopk_align_flag = 0
    if str(discipline_domain).lower() == "linear":
        keywords = [k.upper() for k in owner_profile.linear_pk_align_keywords]
        all_prop_names = {str(k).upper() for p in file_psets.values() for k in p.keys()}
        has_any = any(any(kw in prop for prop in all_prop_names) for kw in keywords)
        nopk_align_flag = 0 if has_any else 1

    return {
        "per_pset_rows": per_pset_rows,
        "Data_gate_pass": data_gate_pass,
        "nopk_align_flag": nopk_align_flag,
        "n_core_psets": len(core_psets),
        "profile_name": owner_profile.name,
    }
