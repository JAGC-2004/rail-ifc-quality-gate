from __future__ import annotations

from typing import Any, Dict

import numpy as np

from .ifc_io import IfcModel


def compute_r4_metrics(model: IfcModel, proxy_threshold_pct: float = 50.0) -> Dict[str, Any]:
    """Compute semantic proxy ratio and semantic gate outcome.

    Definition (paper-aligned):
        proxy_pct = count(IfcBuildingElementProxy) / count(IfcElement) * 100
    """
    try:
        n_elements = len(model.by_type("IfcElement"))
    except Exception:
        n_elements = 0

    try:
        n_proxy = len(model.by_type("IfcBuildingElementProxy"))
    except Exception:
        n_proxy = 0

    proxy_pct = float(n_proxy / n_elements * 100.0) if n_elements > 0 else float("nan")
    semantic_pass = int(proxy_pct < proxy_threshold_pct) if not np.isnan(proxy_pct) else 0

    return {
        "n_ifcelement": n_elements,
        "n_proxy": n_proxy,
        "proxy_pct": proxy_pct,
        "semantic_pass": semantic_pass,
        "proxy_threshold_pct": proxy_threshold_pct,
    }
