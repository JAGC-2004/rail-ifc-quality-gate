from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import yaml


@dataclass(frozen=True)
class ReportingUnit:
    case: str
    state: str
    discipline: str
    domain: str  # building / linear / mep / electrification / interface / unknown

    def case_state(self) -> str:
        return f"{self.case}×{self.state}"

    def case_state_discipline(self) -> str:
        return f"{self.case}×{self.state}×{self.discipline}"


STATE_ALIASES = {
    "EX": "EX",
    "Existing": "EX",
    "PC": "PC",
    "Projected": "PC",
    "EW": "EW",
    "Executed": "EW",
    "Executed works": "EW",
    "DESIGN": "LEGACY",
    "Project (design)": "LEGACY",
    "legacy": "LEGACY",
}


def load_discipline_domains(mapping_path: str | Path) -> Dict[str, Dict[str, str]]:
    """Load discipline domain mapping from YAML."""
    p = Path(mapping_path)
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    return data.get("disciplines", {})


def infer_from_filename(
    filepath: str | Path,
    discipline_domains: Optional[Dict[str, Dict[str, str]]] = None,
) -> ReportingUnit:
    """Infer Case/State/Discipline from an IFC filename.

    This is intentionally pragmatic: projects often embed metadata in filenames.
    The mapping can be overridden via configuration.
    """
    p = Path(filepath)
    name = p.stem

    # Case inference (very lightweight): pick first token with letters+digits (e.g., L3, L10)
    # Allow custom case tags (Depot_A, Depot_B).
    case = "UNKNOWN"
    m = re.search(r"\b(Depot_[A-Z]|L\d+)\b", name, flags=re.IGNORECASE)
    if m:
        case = m.group(1)
        case = case.replace("depot_", "Depot_").replace("DEPOT_", "Depot_")
        case = case.upper() if case.startswith("L") else case

    # State inference
    state = "UNKNOWN"
    for token in ["EX", "PC", "EW", "LEGACY", "Existing", "Projected", "Executed works", "design"]:
        if re.search(rf"\b{re.escape(token)}\b", name, flags=re.IGNORECASE):
            state = STATE_ALIASES.get(token, token)
            break

    # Discipline inference: last uppercase chunk like VIA/URB/ICO...
    discipline = "UNK"
    m2 = re.search(r"\b([A-Z]{2,5})(?:[-_][A-Z]{2,5})?\b", name)
    if m2:
        discipline = m2.group(1)

    domain = "unknown"
    if discipline_domains and discipline in discipline_domains:
        domain = discipline_domains[discipline].get("domain", "unknown")

    return ReportingUnit(case=case, state=state, discipline=discipline, domain=domain)
