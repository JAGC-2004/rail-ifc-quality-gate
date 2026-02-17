from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

try:
    import ifcopenshell  # type: ignore
except Exception:  # pragma: no cover
    ifcopenshell = None  # type: ignore


@dataclass
class IfcParseInfo:
    schema: str
    filepath: str


class IfcModel:
    """Thin wrapper around IfcOpenShell model with safe accessors.

    The implementation is intentionally lightweight to keep the pipeline 'tool-independent'
    (i.e., computable from the IFC exchange alone), while still enabling practical parsing.
    """

    def __init__(self, model: Any, info: IfcParseInfo):
        self._model = model
        self.info = info

    @property
    def model(self) -> Any:
        return self._model

    def by_type(self, ifc_class: str) -> List[Any]:
        return list(self._model.by_type(ifc_class))

    def schema(self) -> str:
        # IfcOpenShell exposes schema via .schema or .schema_identifier depending on build.
        for attr in ("schema", "schema_identifier"):
            if hasattr(self._model, attr):
                try:
                    return str(getattr(self._model, attr))
                except Exception:
                    pass
        return self.info.schema


def open_ifc(path: str | Path) -> IfcModel:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(str(p))

    if ifcopenshell is None:
        raise RuntimeError(
            "IfcOpenShell is not installed. Install with: pip install -r requirements.txt\n"
            "or: pip install 'rail-ifc-quality-gate[ifc]'."
        )

    m = ifcopenshell.open(str(p))
    schema = getattr(m, "schema", None) or getattr(m, "schema_identifier", None) or "UNKNOWN"
    return IfcModel(m, IfcParseInfo(schema=str(schema), filepath=str(p)))


def get_property_sets(model: IfcModel) -> Dict[str, Dict[str, Any]]:
    """Return a map: PsetName -> {PropName -> Value} at file-level.

    This is a *best-effort* extractor intended for file-level audits. It aggregates
    all PSETs found across elements, storing the first encountered value per property.
    For strict element-level completeness you should implement per-entity checks.
    """
    psets: Dict[str, Dict[str, Any]] = {}
    # IfcRelDefinesByProperties links elements to IfcPropertySet.
    rels = model.by_type("IfcRelDefinesByProperties")
    for rel in rels:
        try:
            prop_def = rel.RelatingPropertyDefinition
            # Handle IfcPropertySet only (skip quantity sets, etc.)
            if not prop_def or not prop_def.is_a("IfcPropertySet"):
                continue
            pset_name = str(prop_def.Name)
            if pset_name not in psets:
                psets[pset_name] = {}
            for prop in getattr(prop_def, "HasProperties", []) or []:
                try:
                    if not prop.is_a("IfcPropertySingleValue"):
                        continue
                    name = str(prop.Name)
                    val = getattr(prop, "NominalValue", None)
                    psets[pset_name].setdefault(name, val.wrappedValue if val else None)
                except Exception:
                    continue
        except Exception:
            continue
    return psets
