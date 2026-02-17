#!/usr/bin/env python
"""Build a synthetic (non-sensitive) IFC benchmark corpus.

This script generates a set of tiny IFC files with controllable properties:
- local vs projected coordinate magnitudes
- presence/absence of IfcSite and TrueNorth
- proxy ratio signals (via IfcBuildingElementProxy instances)

Note: the files are intentionally small and primarily intended to test pipeline wiring.
They are not a substitute for real-world authoring tool exports.
"""

from __future__ import annotations

import random
from pathlib import Path

TEMPLATE = """ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('ViewDefinition [CoordinationView]'),'2;1');
FILE_NAME('{name}','2026-02-13T00:00:00',('rail-ifc-quality-gate'),(''), '','', '');
FILE_SCHEMA(('IFC2X3'));
ENDSEC;
DATA;
#1=IFCPROJECT('0',$,'ToyProject',$,$,$,$,(#2),#10);
#2=IFCGEOMETRICREPRESENTATIONCONTEXT($,'Model',3,1.E-5,#3,$);
#3=IFCAXIS2PLACEMENT3D(#4,$,$);
#4=IFCCARTESIANPOINT(({x},{y},{z}));
#10=IFCUNITASSIGNMENT((#11));
#11=IFCSIUNIT(*,.LENGTHUNIT.,$,.METRE.);
#20=IFCSITE('1',$,'Site',$,$,#21,$,$,.ELEMENT.,{lat},{lon},$,$,$);
#21=IFCLOCALPLACEMENT($,#3);
#30=IFCBUILDING('2',$,'Bldg',$,$,#31,$,$,.ELEMENT.,$,$,$);
#31=IFCLOCALPLACEMENT(#21,#3);
{proxies}
ENDSEC;
END-ISO-10303-21;
"""


def make_proxy_lines(n: int, start_id: int = 100) -> str:
    lines = []
    for i in range(n):
        eid = start_id + i
        lines.append(f"#{eid}=IFCBUILDINGELEMENTPROXY('{eid}',$,'Proxy{i}',$,$,#31,$,$,.NOTDEFINED.);")

    return "\n".join(lines)


def main(out_dir: str = "examples/toy_ifc_generated", n_files: int = 5) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    for i in range(n_files):
        name = f"toy_case_{i:04d}"
        # Alternate regimes
        if i % 3 == 0:
            x, y = 700000.0, 4300000.0  # projected-like
        elif i % 3 == 1:
            x, y = 700000000.0, 4300000000.0  # mismatch-like
        else:
            x, y = 0.0, 0.0  # local-like

        z = 0.0
        lat = "(39,0,0,0)" if i % 3 != 2 else "$"  # missing for local case
        lon = "(-0,0,0,0)" if i % 3 != 2 else "$"  # missing for local case

        proxies = make_proxy_lines(n=random.randint(0, 5))
        ifc = TEMPLATE.format(name=name, x=x, y=y, z=z, lat=lat, lon=lon, proxies=proxies)

        (out / f"{name}.ifc").write_text(ifc, encoding="utf-8")

    print(f"Wrote synthetic IFCs to: {out.resolve()}")


if __name__ == "__main__":
    main()
