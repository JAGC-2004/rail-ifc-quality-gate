#!/usr/bin/env python
import sys
from rail_ifc_quality_gate.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["sensitivity"] + sys.argv[1:]))
