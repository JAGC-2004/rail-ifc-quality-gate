from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional, Tuple

import numpy as np


def safe_float(x: Any, default: float = float("nan")) -> float:
    try:
        if x is None:
            return default
        return float(x)
    except Exception:
        return default


def euclidean_distance(a: Tuple[float, float, float], b: Tuple[float, float, float]) -> float:
    ax, ay, az = a
    bx, by, bz = b
    return float(math.sqrt((ax - bx) ** 2 + (ay - by) ** 2 + (az - bz) ** 2))


def median_angle_deg(values_deg: Iterable[float]) -> float:
    vals = [v for v in values_deg if not np.isnan(v)]
    if not vals:
        return float("nan")
    # circular median is overkill for small deviations; we use robust median in degrees.
    return float(np.median(vals))


def angular_deviation_deg(a_deg: float, b_deg: float) -> float:
    """Smallest absolute difference between two angles in degrees."""
    if np.isnan(a_deg) or np.isnan(b_deg):
        return float("nan")
    d = abs(a_deg - b_deg) % 360.0
    return float(min(d, 360.0 - d))


@dataclass(frozen=True)
class MetricResult:
    name: str
    value: float
    passed: Optional[bool] = None
    details: Optional[Dict[str, Any]] = None
