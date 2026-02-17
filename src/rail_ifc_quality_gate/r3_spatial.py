from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd

from .ifc_io import IfcModel
from .utils import angular_deviation_deg, euclidean_distance, median_angle_deg


# Labels used in figures/legend (paper-aligned)
REGIME_PROJECTED_UTM_M = "Projected (UTM/m)"
REGIME_PROJECTED_MISMATCH = "Projected (unit/scale mismatch)"
REGIME_LOCAL = "Local (non-georeferenced)"


def _length_unit_info(model: IfcModel) -> Tuple[str, float]:
    """Return (unit_label, to_m_factor)."""
    # Default: meters
    unit_label = "m"
    factor = 1.0
    try:
        assigns = model.by_type("IfcUnitAssignment")
        if assigns:
            ua = assigns[0]
            for u in getattr(ua, "Units", []) or []:
                try:
                    if not u.is_a("IfcSIUnit"):
                        continue
                    if str(u.UnitType) != "LENGTHUNIT":
                        continue
                    prefix = getattr(u, "Prefix", None)
                    name = getattr(u, "Name", None)
                    # Name often METRE
                    if prefix and str(prefix) == "MILLI":
                        unit_label = "mm"
                        factor = 0.001
                    else:
                        unit_label = "m"
                        factor = 1.0
                    # If name isn't metre, keep factor default.
                    _ = name
                except Exception:
                    continue
    except Exception:
        pass
    return unit_label, factor


def _extract_site_lat_lon(model: IfcModel) -> Tuple[Optional[float], Optional[float]]:
    """Best-effort extraction of RefLatitude/RefLongitude from IfcSite."""
    try:
        sites = model.by_type("IfcSite")
        if not sites:
            return None, None
        s = sites[0]
        lat = getattr(s, "RefLatitude", None)
        lon = getattr(s, "RefLongitude", None)
        # IFC stores degrees/minutes/seconds in LIST[int]
        def dms_to_deg(dms):
            if not dms:
                return None
            try:
                d, m, sec, *rest = list(dms)
                sign = -1.0 if d < 0 else 1.0
                return sign * (abs(d) + m / 60.0 + sec / 3600.0)
            except Exception:
                return None

        lat_deg = dms_to_deg(lat)
        lon_deg = dms_to_deg(lon)
        return lat_deg, lon_deg
    except Exception:
        return None, None


def _extract_truenorth_angle_deg(model: IfcModel) -> float:
    """Extract TrueNorth vector from geometric context and compute angle in degrees.

    Convention: 0° means TrueNorth aligned with +Y.
    """
    try:
        ctxs = model.by_type("IfcGeometricRepresentationContext")
        for ctx in ctxs:
            tn = getattr(ctx, "TrueNorth", None)
            if tn is None:
                continue
            # TrueNorth is IfcDirection with DirectionRatios (x, y, z?)
            ratios = getattr(tn, "DirectionRatios", None)
            if not ratios:
                continue
            x = float(ratios[0])
            y = float(ratios[1]) if len(ratios) > 1 else 0.0
            # Angle between vector and +Y axis.
            ang = math.degrees(math.atan2(x, y))
            return float((ang + 360.0) % 360.0)
    except Exception:
        pass
    return float("nan")


def _extract_anchor_point_raw(model: IfcModel) -> Tuple[float, float, float]:
    """Extract a pragmatic file-level anchor from IfcSite/IfcBuilding placement.

    This is *not* a full georeferencing transform. It is a lightweight indicator for
    inter-model consistency and is intentionally software-neutral.
    """
    # Prefer IfcSite placement, then IfcBuilding, otherwise origin.
    for cls in ("IfcSite", "IfcBuilding"):
        try:
            objs = model.by_type(cls)
            if not objs:
                continue
            o = objs[0]
            pl = getattr(o, "ObjectPlacement", None)
            if not pl:
                continue
            # Navigate IfcLocalPlacement.RelativePlacement.Location.Coordinates
            rel = getattr(pl, "RelativePlacement", None)
            loc = getattr(rel, "Location", None) if rel else None
            coords = getattr(loc, "Coordinates", None) if loc else None
            if coords and len(coords) >= 2:
                x = float(coords[0])
                y = float(coords[1])
                z = float(coords[2]) if len(coords) > 2 else 0.0
                return x, y, z
        except Exception:
            continue
    return 0.0, 0.0, 0.0


def classify_georef_regime(
    unit_label: str,
    anchor_magnitude_m: float,
    has_latlon: bool,
    has_mapconv: bool,
) -> str:
    """Classify spatial scale/georeferencing regime for reporting.

    The classes are aligned to the paper's Figure 2 legend:
    - Projected (UTM/m)
    - Projected (unit/scale mismatch)
    - Local (non-georeferenced)
    """
    # If explicit mapping conversion exists, it's projected.
    if has_mapconv:
        # Still catch obvious mismatches by magnitude.
        if anchor_magnitude_m > 10_000_000:
            return REGIME_PROJECTED_MISMATCH
        return REGIME_PROJECTED_UTM_M

    # If lat/lon provided and anchor magnitude resembles projected coordinates.
    if has_latlon and anchor_magnitude_m > 100_000:
        return REGIME_PROJECTED_UTM_M

    # Detect scale mismatch by magnitude in meters.
    if anchor_magnitude_m > 10_000_000:
        return REGIME_PROJECTED_MISMATCH

    # Otherwise local/non-georeferenced.
    return REGIME_LOCAL


def compute_r3_preliminary(model: IfcModel) -> Dict[str, Any]:
    """Compute preliminary spatial indicators for one IFC file."""
    unit_label, to_m = _length_unit_info(model)
    anchor_raw = _extract_anchor_point_raw(model)
    anchor_m = (anchor_raw[0] * to_m, anchor_raw[1] * to_m, anchor_raw[2] * to_m)
    anchor_mag = float(math.sqrt(anchor_m[0] ** 2 + anchor_m[1] ** 2))

    # Map conversion presence (IFC4+)
    has_mapconv = False
    try:
        # IfcMapConversion exists in IFC4; in practice IfcOpenShell still returns empty on IFC2x3
        has_mapconv = len(model.by_type("IfcMapConversion")) > 0
    except Exception:
        has_mapconv = False

    lat, lon = _extract_site_lat_lon(model)
    has_latlon = (lat is not None and lon is not None)
    lat_lon_valid = None
    if has_latlon:
        lat_lon_valid = bool(-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0 and not (abs(lat) < 1e-9 and abs(lon) < 1e-9))

    regime = classify_georef_regime(unit_label, anchor_mag, has_latlon, has_mapconv)

    return {
        "unit_label": unit_label,
        "to_m": to_m,
        "ifcsite_present": 1 if len(model.by_type("IfcSite")) > 0 else 0,
        "ref_lat_deg": lat,
        "ref_lon_deg": lon,
        "lat_lon_valid": 1 if lat_lon_valid else 0 if lat_lon_valid is not None else np.nan,
        "truenorth_deg": _extract_truenorth_angle_deg(model),
        "anchor_x_m": anchor_m[0],
        "anchor_y_m": anchor_m[1],
        "anchor_z_m": anchor_m[2],
        "anchor_magnitude_m": anchor_mag,
        "georef_regime": regime,
    }


def postprocess_r3_group(
    df: pd.DataFrame,
    discipline_to_tau_m: Dict[str, float],
    truenorth_outlier_deg: float = 5.0,
) -> pd.DataFrame:
    """Add group-aware R3 metrics (anchor dispersion, TrueNorth outliers, Spatial_pass).

    Expects df with columns:
    - case, state, discipline
    - anchor_x_m, anchor_y_m, anchor_z_m
    - truenorth_deg
    - georef_regime
    """
    out = df.copy()

    # Compute group medians (Case×State)
    out["case_state"] = out["case"].astype(str) + "×" + out["state"].astype(str)

    med_anchor = (
        out.groupby("case_state")[["anchor_x_m", "anchor_y_m", "anchor_z_m"]]
        .median(numeric_only=True)
        .rename(columns=lambda c: f"median_{c}")
    )
    out = out.join(med_anchor, on="case_state")

    # Anchor dispersion distance to median anchor for the package
    out["anchor_dispersion_m"] = out.apply(
        lambda r: euclidean_distance(
            (float(r["anchor_x_m"]), float(r["anchor_y_m"]), float(r.get("anchor_z_m", 0.0))),
            (float(r["median_anchor_x_m"]), float(r["median_anchor_y_m"]), float(r.get("median_anchor_z_m", 0.0))),
        ),
        axis=1,
    )

    # Discipline-aware tolerance
    out["tau_m"] = out["discipline"].map(discipline_to_tau_m).fillna(np.nan)

    # TrueNorth outlier vs median angle per Case×State
    med_tn = out.groupby("case_state")["truenorth_deg"].apply(median_angle_deg).rename("median_truenorth_deg")
    out = out.join(med_tn, on="case_state")
    out["truenorth_dev_deg"] = out.apply(lambda r: angular_deviation_deg(float(r["truenorth_deg"]), float(r["median_truenorth_deg"])), axis=1)
    out["truenorth_outlier"] = (out["truenorth_dev_deg"] > truenorth_outlier_deg).astype(int)

    # Spatial pass logic (operational): fail on regime mismatch or local regime; otherwise check dispersion ≤ tau.
    out["spatial_pass"] = (
        (out["georef_regime"] == REGIME_PROJECTED_UTM_M)
        & (out["anchor_dispersion_m"] <= out["tau_m"])
        & (out["truenorth_outlier"] == 0)
    ).astype(int)

    return out
