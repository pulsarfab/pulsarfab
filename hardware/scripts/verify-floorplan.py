#!/usr/bin/env python3
"""Run placement DRC and schematic parity; report unfinished routing explicitly."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("board", type=Path)
args = parser.parse_args()
with tempfile.TemporaryDirectory(prefix="floorplan-drc-") as temp:
    report = Path(temp) / "drc.json"
    subprocess.run([os.environ.get("KICAD_CLI", "kicad-cli"), "pcb", "drc",
                    "--schematic-parity", "--severity-all", "--format", "json",
                    "-o", str(report), str(args.board)], check=True)
    result = json.loads(report.read_text())
    violations = result["violations"] + result["schematic_parity"]
    for violation in violations:
        print(f"FAIL: {violation['type']}: {violation['description']}")
    if violations:
        raise SystemExit(1)
    print("PASS: zero placement DRC violations and zero schematic parity issues")
    print(f"ROUTING INCOMPLETE: {len(result['unconnected_items'])} unconnected items; "
          "this check is not fabrication sign-off")
