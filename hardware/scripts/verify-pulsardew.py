#!/usr/bin/env python3
"""Check the real KiCad netlist against PulsarDew's electrical intent.

Unlike ERC alone, exact pin sets catch swapped GPIOs, shunt bypasses, incorrect
MOSFET pinouts, and accidental connections between repeated sheet instances.
No third-party Python dependencies. Run with `make verify-pulsardew`.
"""

import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET


HERE = Path(__file__).resolve().parent
HARDWARE = HERE.parent
PROJECT = HARDWARE / "pulsardew"
spec = importlib.util.spec_from_file_location("sch_check", HERE / "kicad-sch-check.py")
sch_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sch_check)


def require(condition, message):
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def verify(netlist):
    root = ET.parse(netlist).getroot()
    components = root.findall("./components/comp")
    refs = [c.attrib["ref"] for c in components]
    expected_refs = set("U1 U2 U3 U4 C1 C2 C3 C10 C20 C21 C22 C23 C30 C40 "
                        "D10 J1 J2 J3 J4 R10 R11 R12 R13 R20 R21 R30".split())
    for channel in range(1, 5):
        expected_refs.update(f"{prefix}{channel}{suffix:02}" for prefix, suffix in
                             [("R", 1), ("R", 2), ("R", 3), ("Q", 1), ("Q", 2),
                              ("D", 1), ("D", 2), ("J", 1)])
    require(len(refs) == len(set(refs)), "duplicate reference designators")
    require(set(refs) == expected_refs,
            f"component inventory differs: {sorted(set(refs) ^ expected_refs)}")

    nets = {}
    pins = {}
    for net in root.findall("./nets/net"):
        name = net.attrib["name"]
        members = frozenset(f"{n.attrib['ref']}.{n.attrib['pin']}" for n in net.findall("node"))
        require(members, f"empty net {name}")
        nets[name] = members
        for pin in members:
            require(pin not in pins, f"{pin} belongs to more than one net")
            pins[pin] = name

    expected = {
        "DC input": "D10.2 J2.1 J3.1",
        "VIN_PROT": "D10.1 C10.1 C20.1 C22.1 R30.1 U2.2 U3.10",
        "VIN_HEAT": "R30.2 U3.9 U3.8 J101.1 J201.1 J301.1 J401.1 R102.1 R202.1 R302.1 R402.1",
        "3V3": "U2.3 U1.4 U3.6 U4.3 C1.1 C3.1 C21.1 C23.1 C30.1 C40.1 J4.1 R20.1 R21.1 R101.1 R201.1 R301.1 R401.1",
        "GND": "U1.5 U1.33 U2.1 U3.1 U3.2 U3.7 U4.4 C1.2 C2.2 C3.2 C10.2 C20.2 C21.2 C22.2 C23.2 C30.2 C40.2 J1.A1 J1.A12 J1.B1 J1.B12 J1.SH J2.2 J2.3 J3.2 J4.5 R10.2 R11.2 R13.2 "
               + " ".join(f"{ref}{ch}{suffix}.{pin}" for ch in range(1, 5)
                          for ref, suffix, pin in [("Q", "01", 2), ("Q", "02", 3),
                                                   ("D", "01", 2), ("D", "02", 2)]),
        "I2C SCL": "U1.30 U3.5 U4.2 R20.2",
        "I2C SDA": "U1.31 U3.4 U4.1 R21.2",
        "USB D-": "U1.22 J1.A7 J1.B7",
        "USB D+": "U1.23 J1.A6 J1.B6",
        "USB CC1": "J1.A5 R10.1",
        "USB CC2": "J1.B5 R11.1",
        "USB VBUS": "J1.A4 J1.A9 J1.B4 J1.B9 R12.1",
        "VBUS sense": "R12.2 R13.1 U1.19",
        "SWDIO": "U1.24 J4.2",
        "SWCLK": "U1.25 J4.3",
        "NRST": "U1.6 J4.4 C2.1",
    }
    for channel in range(1, 5):
        expected[f"PWM{channel - 1}"] = f"U1.{channel + 6} Q{channel}01.1 R{channel}01.2"
        expected[f"CH{channel - 1} gate clamp"] = f"Q{channel}01.3 D{channel}01.1 R{channel}02.2 R{channel}03.1"
        expected[f"CH{channel - 1} power gate"] = f"R{channel}03.2 Q{channel}02.1"
        expected[f"CH{channel - 1} switched return"] = f"Q{channel}02.2 D{channel}02.1 J{channel}01.2"

    checked = set()
    for description, members in expected.items():
        wanted = frozenset(members.split())
        seed = members.split()[0]
        require(seed in pins, f"{description}: missing {seed}")
        name = pins[seed]
        actual = nets[name]
        require(actual == wanted,
                f"{description} ({name}): missing {sorted(wanted - actual)}, unexpected {sorted(actual - wanted)}")
        require(name not in checked, f"{description}: shorted to another checked net")
        checked.add(name)

    unused = {f"U1.{p}" for p in [1, 2, 3, 11, 12, 13, 14, 15, 16, 17, 18, 20, 21, 26, 27, 28, 29, 32]}
    unused.update(["J1.A8", "J1.B8", "U3.3"])
    for pin in unused:
        require(pin in pins, f"missing intentionally unused pin {pin}")
        name = pins[pin]
        require(name.startswith("unconnected-") and nets[name] == {pin},
                f"{pin} must have its own explicit no-connect flag")
        checked.add(name)
    require(checked == set(nets), f"unreviewed nets: {sorted(set(nets) - checked)}")

    # Verify footprint files exist and every schematic pin has a matching pad.
    # This does not certify land-pattern geometry or substitute for a PCB review.
    footprint_roots = [Path(os.environ[k]) for k in ("KICAD_FOOTPRINT_DIR", "KICAD10_FOOTPRINT_DIR") if os.environ.get(k)]
    footprint_roots += [Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"),
                        Path("/usr/share/kicad/footprints"), Path("/usr/local/share/kicad/footprints")]
    for comp in components:
        ref = comp.attrib["ref"]
        footprint = comp.findtext("footprint", "")
        require(":" in footprint, f"{ref}: missing qualified footprint")
        library, name = footprint.split(":", 1)
        candidates = ([HARDWARE / "lib/footprints.pretty" / f"{name}.kicad_mod"] if library == "pulsarfab"
                      else [base / f"{library}.pretty" / f"{name}.kicad_mod" for base in footprint_roots])
        source = next((p for p in candidates if p.is_file()), None)
        require(source is not None, f"{ref}: footprint not found: {footprint}")
        pads = set(re.findall(r'\(pad\s+"([^"]+)"', source.read_text()))
        used_pins = {p.split(".", 1)[1] for p in pins if p.startswith(ref + ".")}
        require(used_pins <= pads, f"{ref}: footprint lacks pads {sorted(used_pins - pads)}")
    print(f"PASS: {len(components)} components; {len(expected)} exact connected nets; "
          f"{len(unused)} intentional no-connects; footprint pad coverage complete")


def main():
    cli = sch_check.find_cli()
    with tempfile.TemporaryDirectory(prefix="pulsardew-verify-") as temp:
        temp = Path(temp)
        sch = PROJECT / "pulsardew.kicad_sch"
        subprocess.run([cli, "sch", "export", "netlist", "--format", "kicadxml",
                        "-o", str(temp / "net.xml"), str(sch)], check=True)
        subprocess.run([cli, "sch", "erc", "--severity-all", "--exit-code-violations",
                        "--format", "json", "-o", str(temp / "erc.json"), str(sch)], check=True)
        erc = json.loads((temp / "erc.json").read_text())
        require(not any(sheet["violations"] for sheet in erc["sheets"]), "ERC has violations")
        verify(temp / "net.xml")
        print("PASS: KiCad ERC has zero errors, warnings or exclusions")


if __name__ == "__main__":
    main()
