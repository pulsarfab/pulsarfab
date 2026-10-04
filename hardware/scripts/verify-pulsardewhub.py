#!/usr/bin/env python3
"""Independent pin-level intent checks for PulsarDew Hub; ERC is not sufficient.

Checks every exported net (including no-connects), power-path isolation, repeated
sheet identity, exact GPIO assignment, critical ratings and footprint pin coverage.
Does not certify routing, thermal performance, firmware, or manufacturing readiness.
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
PROJECT = HARDWARE / "pulsardewhub"


def require(ok, message):
    if not ok:
        raise SystemExit("FAIL: " + message)


def expected_nets():
    nets = {}
    pins = set()
    def comp(ref, assignments):
        for number, name in assignments.items():
            pin = f"{ref}.{number}"
            require(pin not in pins, f"duplicate expected pin {pin}")
            pins.add(pin)
            nets.setdefault(name or "NC:" + pin, set()).add(pin)
    def pair(ref, a, b="GND"):
        comp(ref, {1: a, 2: b})
    def esd(ref, dp, dm, vbus):
        comp(ref, {1: dm, 6: dm, 3: dp, 4: dp, 5: vbus, 2: "GND"})
    def barrel(ref, positive):
        comp(ref, {1: positive, 2: "GND", 3: "GND"})

    # XT60 library has '+' at physical pad 2, '-' at pad 1.
    pair("J10", "GND", "XT60_IN")
    pair("F10", "XT60_IN", "VIN_RAW")
    barrel("J11", "BARREL_IN")
    pair("F11", "BARREL_IN", "VIN_RAW")
    for q in ["Q10","Q11"]:comp(q, {1: "VIN_RAW", 2: "VIN_RAW", 3: "VIN_RAW", 4: "INPUT_GATE", 5: "VIN"})
    comp("U10", {6: "VIN_RAW", 3: "VIN_RAW", 1: "VCAP", 2: "GND", 4: "VIN", 5: "INPUT_GATE"})
    pair("C10", "VCAP", "VIN_RAW")
    for ref in ["D10", "C11", "C12"]: pair(ref, "VIN")
    pair("C13","VIN_RAW")
    for base, vin, out in [(20, "VIN", "V5")]:
        sw, fb, vcc, boot = [f"{n}{base}" for n in ["SW", "FB", "VCC", "BOOT"]]
        comp(f"U{base}", {1:"GND",9:"GND",2:vin,3:vin,4:None,5:fb,6:vcc,7:boot,8:sw})
        pair(f"L{base}", sw, out)
        pair(f"R{base}", out, fb)
        pair(f"R{base+1}", fb)
        for offset, a, b in [(0,vin,"GND"),(1,vin,"GND"),(2,vcc,"GND"),(3,boot,sw)]:
            pair(f"C{base+offset}",a,b)
        for i in range(4,8):pair(f"C{base+i}",out)

    comp("U30", {1:"BOOT30",2:"GND",3:"FB30",4:"V5",5:"V5",6:"SW30"})
    pair("L30","SW30","V3");pair("R30","V3","FB30")
    pair("R31","FB30","FB_RETURN30");pair("R32","FB_RETURN30","GND")
    pair("C30","V5");pair("C31","V5");pair("C33","BOOT30","SW30")
    for i in range(34,38):pair(f"C{i}","V3")

    comp("U1", {1:"DC_EN4",2:None,3:None,4:"V3",5:"GND",6:"NRST",7:"HTR0",8:"HTR1",
                9:None,10:None,11:"IMON1",12:"IMON2",13:"IMON3",14:"IMON4",15:"DC_EN1",
                16:"DC_EN2",17:"DC_EN3",18:None,19:"USB_ATTACH",20:"DC_PG4",21:None,
                22:"MCU_DM",23:"MCU_DP",24:"SWDIO",25:"SWCLK",26:None,27:"DC_PG1",
                28:"DC_PG2",29:"DC_PG3",30:"SCL",31:"SDA",32:None,33:"GND"})
    comp("U2", {1:"SDA",2:"SCL",3:"V3",4:"GND"})
    comp("J1", {1:"V3",2:"SWDIO",3:"SWCLK",4:"NRST",5:"GND"})
    pair("R1","V3","SCL");pair("R2","V3","SDA")
    for ref in ["C1","C2","C4"]:pair(ref,"V3")
    pair("C3","NRST")

    comp("U50", {1:None,2:"HTR0",3:"GND",4:"HTR1",5:"DRIVE1",6:"V5",7:"DRIVE0",8:None})
    pair("C50","V5");pair("C51","V5")
    pair("R50","VIN","HTR_VIN")
    comp("U51",{1:"GND",2:"GND",3:None,4:"SDA",5:"SCL",6:"V3",7:"GND",8:"HTR_VIN",9:"HTR_VIN",10:"VIN"})
    pair("C52","V3")
    for i,b in enumerate([51,61]):
        gate, low, fused = f"GATE{i}",f"HEATER{i}_LOW",f"HEATER{i}_FUSED"
        pair(f"R{b}",f"HTR{i}")
        pair(f"R{b+1}",f"DRIVE{i}",gate)
        pair(f"R{b+2}",gate)
        comp(f"Q{b}",{1:gate,2:low,3:"GND"})
        pair(f"D{b}",low)
        pair(f"F{b}","HTR_VIN",fused)
        pair(f"J{b}",fused,low)

    comp("U70", {5:"V3",2:"GND",3:"UV_SHARED",4:"OV_SHARED",1:"WINDOW_OK",6:"WINDOW_OK"})
    comp("U71", {14:"V3",7:"GND",1:"DC_EN1",4:"DC_EN2",9:"DC_EN3",12:"DC_EN4",
                  2:"WINDOW_OK",5:"WINDOW_OK",10:"WINDOW_OK",13:"WINDOW_OK",
                  3:"DC_SAFE1",6:"DC_SAFE2",8:"DC_SAFE3",11:"DC_SAFE4"})
    pair("R70","VIN","UV_SHARED");pair("R71","UV_SHARED")
    pair("R72","VIN","OV_SHARED");pair("R73","OV_SHARED")
    pair("R74","V3","WINDOW_OK");pair("C70","V3");pair("C71","V3")
    for i in range(1,5):pair(f"R{74+i}",f"DC_EN{i}")
    for i in range(1,5):
        b=i*100; n=lambda suffix:f"DC{i}_{suffix}"
        # TI SLVSGG5D table 5-1: separate IN/OUT power leads, combined ILM/monitor.
        comp(f"U{b+1}",{1:n("EN_SW"),2:n("OV"),3:f"DC_PG{i}",4:n("PGTH"),
                         5:"VIN",6:n("OUT"),7:n("DVDT"),8:"GND",9:n("RAW"),10:None})
        comp(f"U{b+2}",{1:"GND",2:"GND",3:"GND",4:"VIN",5:"VIN",6:"VIN",7:"GND"})
        for off,a,z in [(1,n("OUT"),n("PGTH")),(2,n("PGTH"),"GND"),(3,"VIN",n("OV")),(4,n("OV"),"GND"),
             (5,n("EN_SW"),"GND"),(6,"V3",f"DC_PG{i}"),(7,n("RAW"),"GND"),
             (9,n("RAW"),f"IMON{i}"),(10,f"DC_SAFE{i}",n("EN_SW"))]:pair(f"R{b+off}",a,z)
        for off,a in [(1,"VIN"),(2,n("OUT")),(3,n("DVDT")),(4,f"IMON{i}")]:pair(f"C{b+off}",a)
        barrel(f"J{b+1}",n("OUT"));pair(f"D{b+1}",n("OUT"))

    for i,b in enumerate([500,600,700,800],1):
        vbus,ilim = f"USB{i}_VBUS",f"USB{i}_ILIM"
        comp(f"U{b+1}",{1:"V5",2:"GND",3:f"USB{i}_EN",4:f"USB{i}_OC",5:ilim,6:vbus})
        pair(f"R{b+1}",ilim);pair(f"R{b+2}",f"USB{i}_EN")
        pair(f"C{b+1}","V5");pair(f"C{b+2}",vbus);pair(f"C{b+3}",vbus)
        comp(f"J{b+1}",{1:vbus,2:f"USB{i}_DM",3:f"USB{i}_DP",4:"GND","SH":"GND"})
        esd(f"U{b+2}",f"USB{i}_DP",f"USB{i}_DM",vbus)

    hub={p:"V3" for p in [5,10,52,57,24,46,64]}
    hub.update({25:"V18_CORE",62:"V18_PLL",65:"GND",63:"RBIAS",61:"XTAL1",60:"XTAL2",43:"HUB_RESET",44:"VBUS_DET",59:"UP_DP",58:"UP_DM",13:"GND",19:"GND"})
    # Physical USB2517 port pins from Microchip DS00001598C, not sheet order.
    for i,(dp,dm,en,oc) in enumerate([(2,1,29,28),(4,3,26,27),(7,6,23,22),(9,8,20,21),(12,11,30,35)]):
        hub.update({dp:"MCU_DP" if i==0 else f"USB{i}_DP",dm:"MCU_DM" if i==0 else f"USB{i}_DM",
                    en:"USB_ATTACH" if i==0 else f"USB{i}_EN",oc:"V3" if i==0 else f"USB{i}_OC"})
    for p in [53,54,55,56]:hub[p]=f"DISABLE_{p}"
    straps=[41,42,45,40,34,50,48,51,49,47,33,31,17,15]
    for j,p in enumerate(straps):
        hub[p]=f"STRAP_{p}"
        pair(f"R{901+j}","V3" if p==45 else f"STRAP_{p}",f"STRAP_{p}" if p==45 else "GND")
    for j,p in enumerate([53,54,55,56]):pair(f"R{915+j}","V3",f"DISABLE_{p}")
    for p in [14,16,18,32,36,37,38,39]:hub[p]=None
    require(set(hub)==set(range(1,66)),"hub pin coverage in independent model")
    comp("U40",hub)
    pair("R919","RBIAS")
    comp("Y40",{1:"XTAL1",2:"GND",3:"XTAL2",4:"GND"})
    pair("C901","XTAL1");pair("C902","XTAL2")
    for j in range(903,912):pair(f"C{j}","V3")
    pair("C912","V18_CORE");pair("C913","V18_PLL")
    comp("U41",{1:"HUB_RESET",2:"GND",3:"V3",4:None,5:"V3",6:"V3"})
    pair("R920","V3","HUB_RESET");pair("C914","V3")
    comp("J40", {**{p:"HOST_VBUS" for p in ["A4","A9","B4","B9"]},
                 **{p:"GND" for p in ["A1","A12","B1","B12","SH"]},
                 "A6":"UP_DP","B6":"UP_DP","A7":"UP_DM","B7":"UP_DM","A5":"CC1","B5":"CC2","A8":None,"B8":None})
    pair("R921","CC1");pair("R922","CC2")
    pair("R923","HOST_VBUS","VBUS_DET");pair("R924","VBUS_DET")
    pair("C915","HOST_VBUS");esd("U42","UP_DP","UP_DM","HOST_VBUS")
    for i in range(1,5):pair(f"R{924+i}","V3",f"USB{i}_OC")
    return nets


def verify(netlist):
    root=ET.parse(netlist).getroot()
    components=root.findall("./components/comp")
    comps={c.attrib["ref"]:c for c in components}
    require(len(comps)==len(components),"duplicate references")
    actual={n.attrib["name"]:set(f"{p.attrib['ref']}.{p.attrib['pin']}" for p in n.findall("node")) for n in root.findall("./nets/net")}
    bypin={pin:name for name,members in actual.items() for pin in members}
    require(len(bypin)==sum(map(len,actual.values())),"duplicate pins across nets")
    expected=expected_nets();checked=set()
    for description,wanted in expected.items():
        seed=sorted(wanted)[0]
        require(seed in bypin,f"missing {seed}")
        name=bypin[seed];got=actual[name]
        require(got==wanted,f"{description}: missing {sorted(wanted-got)}, unexpected {sorted(got-wanted)}")
        require(name not in checked,f"short between expected nets: {description}")
        if description.startswith("NC:"):require(name.startswith("unconnected-"),f"missing NC flag: {seed}")
        checked.add(name)
    require(checked==set(actual),f"unreviewed nets: {set(actual)-checked}")
    require(set(comps)=={p.split('.')[0] for members in expected.values() for p in members},"unexpected component inventory")

    for i in range(1,5):
        b=i*100
        for ref,value in [(f"R{b+1}","100k"),(f"R{b+2}","20k"),(f"R{b+3}","150k"),(f"R{b+4}","10k"),
                (f"R{b+5}","10k"),(f"R{b+7}","1k / 1%"),
                (f"R{b+9}","10k"),(f"R{b+10}","1k"),(f"C{b+3}","4.7n / 50V"),(f"D{b+1}","SS54")]:
            require(comps[ref].findtext("value")==value,f"{ref}: changed protection/current scaling")
        require(comps[f"U{b+1}"].findtext("footprint")=="pulsarfab:TI_RPW0010A_VQFN10_2x2mm","TPS25974 footprint mismatch")
        for off,mpn,code in [(1,"TPS25974LRPWR","C3662931"),(2,"TVS1800DRVR","C2649846")]:
            f={x.attrib["name"]:x.text for x in comps[f"U{b+off}"].findall("fields/field")}
            require(f.get("MPN")==mpn and f.get("LCSC")==code,"wrong eFuse/clamp variant")
    for ref,mpn in [("U70","TPS3700DDCR"),("U71","SN74LVC08APWR"),("Q10","SIR680LDP-T1-RE3"),("Q11","SIR680LDP-T1-RE3")]:
        f={x.attrib["name"]:x.text for x in comps[ref].findall("fields/field")}
        require(f.get("MPN")==mpn,f"{ref}: qualified part mismatch")
    for ref,value in [("R70","220k"),("R71","10k"),("R72","470k"),("R73","10k"),("R74","10k"),
                      ("R75","10k"),("R76","10k"),("R77","10k"),("R78","10k"),("C10","1u / 50V")]:
        require(comps[ref].findtext("value")==value,f"{ref}: shared inhibit/gate drive value")
    require(comps["D10"].findtext("value")=="SMCJ18A","input bulk TVS")
    for b in [500,600,700,800]:
        require(comps[f"C{b+2}"].findtext("value")=="150u / 10V / 20%","USB VBUS minimum capacitance")
        require(comps[f"R{b+1}"].findtext("value")=="43.2k / 1%","USB current-limit resistor")
    require(5.7 < 5747/1000 < 5.8,"nominal breaker threshold")
    # +/-10% threshold, 1% resistor and 1% additional TCR allowance; prototype check still required.
    require(5747*.9/(1000*1.02)>5,"5 A no-trip screening")
    require(114e-6*1000*1.02*14<3.2,"ADC range screening at twice breaker setpoint")
    ov_min=.396*(1+470e3*.99/(10e3*1.01));ov_max=.404*(1+470e3*1.01/(10e3*.99))
    require(ov_min>18 and ov_max<20,"shared OV threshold tolerance")
    require(1.183*(1+150*.99/(10*1.01))>18,"local OVLO passes 18 V")
    require(1.228*(1+150*1.01/(10*.99))+.015<20.1,"local OVLO threshold")
    require(2.05*10/11>1.228 and .6<1.076,"AND gate/eFuse enable logic margins")
    require(3.1-4*20e-6*10e3>2,"shared window fan-out logic margin")
    require(24.7<28,"local flat-clamp vs eFuse input absolute max, specified pulse only")
    require(1e-6*.5>10*2*7250e-12,"gate pump capacitance with two stocked MOSFETs and 50% derating")
    require(25230/(43.2*1.01)**1.016>500,"USB current-limit minimum")

    # Regulator substitution must preserve the upstream 3 A supply and correct feedback reference.
    for ref,mpn,code in [("U20","LMR33630ADDAR","C841384"),("U30","LMR51610XDBVR","C20539658")]:
        f={x.attrib["name"]:x.text for x in comps[ref].findall("fields/field")}
        require(f.get("MPN")==mpn and f.get("LCSC")==code,f"{ref}: regulator variant mismatch")
    require(comps["U30"].findtext("footprint")=="Package_TO_SOT_SMD:SOT-23-6","LMR51610 footprint")
    for ref,value in [("R30","100k"),("R31","20k"),("R32","12k"),("C31","100n / 50V"),("C33","100n"),("L30","6.8u / 12A sat")]:
        require(comps[ref].findtext("value")==value,f"{ref}: LMR51610 support value mismatch")
    require("C32" not in comps,"LMR51610 has no VCC bypass pin")
    # Screen +/-2% total resistor allowance, including 1% tolerance and temperature drift.
    vmin=.788*(1+100*.98/(32*1.02));vmax=.812*(1+100*1.02/(32*.98))
    require(vmin>3.15 and vmax<3.6,"3.3 V rail tolerance including temperature allowance")
    ripple=max(v*(5.25-v)/(5.25*6.8e-6*.8*340e3) for v in [vmin,vmax])
    require(.65+ripple/2<1.25,"650 mA load vs minimum LMR51610 peak limit")

    # Pin-pad coverage is separate from physical land-pattern qualification.
    roots=[Path(os.environ[k]) for k in ["KICAD_FOOTPRINT_DIR","KICAD10_FOOTPRINT_DIR"] if k in os.environ]
    roots += [Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"),Path("/usr/share/kicad/footprints")]
    for ref,c in comps.items():
        f=c.findtext("footprint","");require(":" in f,f"{ref}: missing footprint")
        lib,name=f.split(":",1)
        paths=[HARDWARE/"lib/footprints.pretty"/(name+".kicad_mod")] if lib=="pulsarfab" else [r/(lib+".pretty")/(name+".kicad_mod") for r in roots]
        source=next((p for p in paths if p.is_file()),None);require(source is not None,f"{ref}: missing {f}")
        pads=set(re.findall(r'\(pad\s+"([^"]+)"',source.read_text()))
        needed={p.split(".",1)[1] for p in bypin if p.startswith(ref+".")}
        require(needed<=pads,f"{ref}: missing pads {needed-pads}")
        fields={v.attrib["name"]:v.text or "" for v in c.findall("fields/field")}
        require(fields.get("LCSC"),f"{ref}: LCSC source missing")
        require(fields.get("MPN"),f"{ref}: MPN missing")
    nc=sum(k.startswith("NC:") for k in expected)
    print(f"PASS: {len(comps)} components, {len(expected)-nc} exact connected nets, {nc} intentional no-connects; BOM and pad coverage")


def main():
    cli=os.environ.get("KICAD_CLI","kicad-cli")
    with tempfile.TemporaryDirectory(prefix="pulsardewhub-verify-") as temp:
        temp=Path(temp);sch=PROJECT/"pulsardewhub.kicad_sch"
        subprocess.run([cli,"sch","export","netlist","--format","kicadxml","-o",str(temp/"net.xml"),str(sch)],check=True)
        subprocess.run([cli,"sch","erc","--severity-all","--exit-code-violations","--format","json","-o",str(temp/"erc.json"),str(sch)],check=True)
        erc=json.loads((temp/"erc.json").read_text())
        require(not any(s["violations"] for s in erc["sheets"]),"ERC violations")
        verify(temp/"net.xml")
        print("PASS: KiCad ERC has zero errors, warnings or exclusions")


if __name__=="__main__":main()
