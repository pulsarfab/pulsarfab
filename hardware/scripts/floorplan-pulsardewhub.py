#!/usr/bin/env python3
"""Seed the UNROUTED 180 x 110 mm, four-layer PulsarDew Hub floorplan.

Run using KiCad's Python (pcbnew required). Refuses to overwrite an existing
board unless --replace is supplied; never use --replace after routing begins.
The editable .kicad_pcb is the authoritative layout after this initial placement.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import pcbnew as p

BASE=Path(__file__).resolve().parents[2]
PROJECT=BASE/"hardware/pulsardewhub"
LIB=Path(os.environ.get("KICAD_FOOTPRINT_DIR","/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"))
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("--replace",action="store_true")
args=parser.parse_args()
output=PROJECT/"pulsardewhub.kicad_pcb"
if output.exists() and not args.replace:raise SystemExit("Board exists; edit in KiCad, or explicitly --replace the initial floorplan.")
if output.exists() and len(p.LoadBoard(str(output)).GetTracks()):raise SystemExit("Refusing to erase routed copper.")
with tempfile.TemporaryDirectory() as td:
    net=Path(td)/"net.xml"
    subprocess.run([os.environ.get("KICAD_CLI","kicad-cli"),"sch","export","netlist","--format","kicadxml","-o",str(net),str(PROJECT/"pulsardewhub.kicad_sch")],check=True)
    root=ET.parse(net).getroot()

board=p.BOARD();board.SetCopperLayerCount(4)
def pt(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
netmap={};pinnets={}
for net in root.findall("./nets/net"):
    item=p.NETINFO_ITEM(board,net.attrib["name"].replace("/","{slash}") if net.attrib["name"].startswith("unconnected-") else net.attrib["name"],int(net.attrib["code"]))
    board.Add(item);netmap[net.attrib["name"]]=item
    for pin in net.findall("node"):pinnets[(pin.attrib["ref"],pin.attrib["pin"])]=(item,pin.attrib)
footprints={}
for comp in root.findall("./components/comp"):
    ref=comp.attrib["ref"];lib,name=comp.findtext("footprint").split(":",1)
    folder=BASE/"hardware/lib/footprints.pretty" if lib=="pulsarfab" else LIB/(lib+".pretty")
    f=p.FootprintLoad(str(folder),name)
    if f is None:raise RuntimeError("Missing footprint: "+lib+":"+name)
    f.SetFPID(p.LIB_ID(lib,name));f.SetReference(ref);f.SetValue(comp.findtext("value"))
    fields={x.attrib["name"]:x.text or "" for x in comp.findall("fields/field")}
    f.SetFields(fields)
    f.SetPath(p.KIID_PATH(comp.find("sheetpath").attrib["tstamps"]+comp.findtext("tstamps")))
    properties={x.attrib["name"]:x.attrib.get("value","") for x in comp.findall("property")}
    f.SetSheetname(comp.find("sheetpath").attrib["names"]);f.SetSheetfile(properties.get("Sheetfile",""))
    f.SetDNP(ref in ["J11","F11"])
    for pad in f.Pads():
        key=(ref,pad.GetNumber())
        if key in pinnets:
            item,a=pinnets[key];pad.SetNet(item);pad.SetPinFunction(a.get("pinfunction",""));pad.SetPinType(a.get("pintype",""))
    for field in f.GetFields():
        if field.GetName() not in ["Reference","Value"]:field.SetVisible(False)
    f.Value().SetVisible(False);board.Add(f);footprints[ref]=f

place={
 "J10":(66,112,90),"J11":(64,132,270),"F10":(78,109,0),"F11":(77,130,0),
 "Q10":(92,111,90),"U10":(86,119,0),"C10":(83.5,119,90),
 "D10":(95,123,90),"C11":(97,116,0),"C12":(104,122,0),
 "U1":(130,96,0),"C1":(130,100.5,0),"C2":(127,100.5,0),"C3":(134.5,98,90),
 "R1":(135,92,0),"R2":(135,94,0),"J1":(203,99,90),"U2":(222,78,0),"C4":(224.5,78,90),
 "U50":(89,137,0),"C50":(89,132,0),"C51":(92,132,0),"R50":(114,123,0),
 "U51":(115,117,90),"C52":(119,117,90),
 "J51":(76,154.7,0),"J61":(99,154.7,0),
 "Q51":(78.5,141,0),"Q61":(101.5,141,0),"F51":(79,128,0),"F61":(102,133,0),
 "R51":(85,139,90),"R61":(93,139,90),"R52":(83.5,142,0),"R62":(96.5,142,0),
 "R53":(83.5,144.5,0),"R63":(96.5,144.5,0),"D51":(85,149,90),"D61":(108,149,90),
 "J40":(96,53.4,180),"U42":(96,61,180),"R921":(91,59,90),"R922":(101,59,90),
 "C915":(104,61,0),"R923":(106,59,90),"R924":(108,59,90),
 "U40":(157,85,0),"Y40":(155.5,75,0),"C901":(152.5,75,90),"C902":(159,75,90),
 "U41":(178,97,0),"R920":(182,96,90),"C914":(178,100.5,0),"R919":(156,78.5,90),
 "C903":(151,82,0),"C904":(151,85,0),"C905":(159,79,90),"C906":(156.5,79,90),
 "C907":(156,91,90),"C908":(163,81,0),"C909":(152,79,90),
 "C910":(150,88,0),"C911":(164,86,0),"C912":(158.5,91,90),"C913":(154,79,90),
}
# Buck loops: input/boot/VCC capacitors close to the IC; large inductors on SW side.
for b,y in [(20,73),(30,93)]:
    place.update({f"U{b}":(76,y,0),f"L{b}":(90,y-2,0),f"C{b}":(68,y-1,90),
        f"C{b+1}":(71,y-.635,90),f"C{b+2}":(80.5,y+.635,0),f"C{b+3}":(80.5,y-2.5,90),
        f"R{b}":(80,y+5,0),f"R{b+1}":(76,y+5,0)})
    for j in range(4):place[f"C{b+4+j}"]=(102+j*3.2,y-2,90)
# Outlet blocks: eFuse with distinct VIN/GND exposed pads, local clamps and voltage monitor.
for i,x in enumerate([128,156,184,212],1):
    b=100*i
    place.update({f"J{b+1}":(x,146.3,0),f"U{b+1}":(x,133,0),f"U{b+2}":(x-8,137,0),
        f"D{b+1}":(x+8,140,90),f"D{b+2}":(x-1,125,0),
        f"C{b+1}":(x-4,130,90),f"C{b+2}":(x+4,130,90),f"C{b+3}":(x+4,134,90),
        f"C{b+4}":(x+10,128,90),f"C{b+5}":(x-8,140,0)})
    coords=[(-11,130),(-11,133),(-8,130),(-8,133),(-4,137),(8,132),(-1,137),(5,137),(10,125),(-4,140)]
    for off,(dx,yy) in enumerate(coords,1):place[f"R{b+off}"]=(x+dx,yy,90 if off in [1,2,3,4,5,6,8,9] else 0)
# Four downstream USB ports. ESD is just behind data tails; VBUS switch/bulk to the side.
for i,x in enumerate([124,148,172,196]):
    b=500+i*100
    place.update({f"J{b+1}":(x,62,180),f"U{b+2}":(x,66,180),f"U{b+1}":(x+8,75,0),
        f"C{b+1}":(x+11.5,75,90),f"C{b+2}":(x+8,68,90),f"C{b+3}":(x+4,63,90),
        f"R{b+1}":(x+8,78.5,0),f"R{b+2}":(x+4.5,77,90)})
# Reset straps and disabled-port resistors are outside the USB fanout region.
for j in range(14):place[f"R{901+j}"]=(145+(j%7)*3.4,97+(j//7)*3,0)
for j in range(4):place[f"R{915+j}"]=(167+j*3.3,92,90)
for j in range(4):place[f"R{925+j}"]=(141+j*4,103.5,0)
# Resolve clearances after viewing native courtyard and copper checks.
place.update({"F11":(77,123,0),"R52":(70.5,138,0),"R53":(70.5,141,0),
 "R62":(94,136,0),"R63":(93,145,0),"R61":(94,142,0),"D51":(88,149,90),"D61":(111,149,90),
 "C915":(99.5,64,0),"C22":(81.5,73.635,90),"C32":(81.5,93.635,90)})
place.update({"U40":(157,93,0),"Y40":(155.5,81.5,0),"C901":(152.5,81.5,90),"C902":(159,81.5,90),
 "R919":(147,85.5,90),"C903":(149.5,90,0),"C904":(149.5,93,0),
 "C905":(159,85.5,90),"C906":(156.5,85.5,90),"C913":(154,85.5,90),"C909":(151.5,85.5,90),
 "C907":(156,100.5,90),"C912":(158.5,100.5,90),"C908":(164.5,89,0),"C910":(149.5,96,0),"C911":(164.5,94,0)})
for j in range(14):place[f"R{901+j}"]=(145+(j%7)*3.4,105+(j//7)*3,0)
for j in range(4):place[f"R{915+j}"]=(183+j*3.3,89,90)
for j in range(4):place[f"R{925+j}"]=(141+j*4,111.5,0)
for i,x in enumerate([124,148,172,196]):
 b=500+i*100
 place.update({f"C{b+2}":(x+8,70,90),f"C{b+3}":(x+4,65.5,90),
     f"U{b+1}":(x+14,76,0),f"C{b+1}":(x+17.5,76,90),
     f"R{b+1}":(x+14,79.5,0),f"R{b+2}":(x+10.5,78,90)})
place.update({"R50":(116,123,0),"C10":(82.5,119,90),"R51":(84.3,140,90),
 "R62":(94.3,136,0),"R61":(93.5,142,0),"R921":(90.5,61.5,90),"R922":(102,60.5,90)})
for i,x in enumerate([124,148,172,196]):place[f"C{503+100*i}"]=(x+3,70,90)
assert set(place)==set(footprints),(set(footprints)-set(place),set(place)-set(footprints))
for ref,f in footprints.items():
    x,y,a=place[ref];f.SetOrientationDegrees(a);f.SetPosition(pt(x,y))
    r=f.Reference();r.SetTextSize(pt(.8,.8));r.SetTextThickness(p.FromMM(.12));r.SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T));r.SetKeepUpright(True)
    # Passive references remain available in the fabrication overlay, keeping silk readable.
    if ref.startswith(("R","C","D")) or ref in ["U102","U202","U302","U402"]:r.SetLayer(p.F_Fab)
    box=f.GetBoundingBox(False,False);r.SetPosition(p.VECTOR2I(box.GetCenter().x,box.GetTop()-p.FromMM(.8)))
    if ref.startswith("J"):r.SetLayer(p.F_Fab)
    if ref in ["U502","U602","U702","U802"]:r.SetPosition(pt(x,y+2.8))
    if ref=="U40":r.SetPosition(pt(166,98))

for x1,y1,x2,y2 in [(50,50,230,50),(230,50,230,160),(230,160,50,160),(50,160,50,50)]:
    shape=p.PCB_SHAPE();shape.SetShape(p.SHAPE_T_SEGMENT);shape.SetStart(pt(x1,y1));shape.SetEnd(pt(x2,y2));shape.SetLayer(p.Edge_Cuts);shape.SetWidth(p.FromMM(.05));board.Add(shape)
for i,(x,y) in enumerate([(54,54),(226,54),(54,156),(226,156)],1):
    f=p.FootprintLoad(str(LIB/"MountingHole.pretty"),"MountingHole_3.2mm_M3")
    f.SetReference(f"H{i}");f.SetValue("M3");f.SetPosition(pt(x,y));f.SetAttributes(p.FP_BOARD_ONLY|p.FP_EXCLUDE_FROM_BOM|p.FP_EXCLUDE_FROM_POS_FILES);f.Reference().SetVisible(False);f.Value().SetVisible(False);board.Add(f)
for i,(x,y) in enumerate([(60,59),(220,60),(220,153)],1):
    f=p.FootprintLoad(str(LIB/"Fiducial.pretty"),"Fiducial_1mm_Mask2mm")
    f.SetReference(f"FID{i}");f.SetValue("Fiducial");f.SetPosition(pt(x,y))
    f.SetAttributes(p.FP_BOARD_ONLY|p.FP_EXCLUDE_FROM_BOM|p.FP_EXCLUDE_FROM_POS_FILES)
    f.Reference().SetVisible(False);f.Value().SetVisible(False);board.Add(f)
def text(s,x,y,size=1,layer=p.F_SilkS):
    t=p.PCB_TEXT(board);t.SetText(s);t.SetPosition(pt(x,y));t.SetTextSize(pt(size,size));t.SetTextThickness(p.FromMM(.15));t.SetLayer(layer);board.Add(t)
text("PulsarDew Hub 0.2",191,109,1.8)
text("2 HEATERS / 4 DC / USB 2.0",191,112,1)
text("12-18V IN",60,88,1)
text("FIT ONE INPUT",65,96,.8)
text("BARREL: 5A TOTAL",64,144,.8)
text("SHT40",222,83,.8)
text("SWD",209,104,.8)
text("HOST",96,65,.8)
for i,x in enumerate([124,148,172,196],1):text(f"USB {i}",x,52,.8)
for i,x in enumerate([128,156,184,212],1):text(f"DC {i}",x,143.8,.9)
for i,x in enumerate([78,101],1):text(f"HEAT {i}",x,158,.8)
text("UNROUTED FLOORPLAN - NOT FOR FABRICATION",145,118,1.3,p.Dwgs_User)
text("Reserve VIN + GND copper corridor; 25A shared target",161,122,1,p.Dwgs_User)
text("Keep USB over continuous L2 ground",177,107,.9,p.Dwgs_User)
# SHT40: no copper between sensor pads (including inner layers).
z=p.ZONE(board);z.SetIsRuleArea(True);z.SetLayerSet(p.LSET.AllCuMask());z.SetDoNotAllowZoneFills(True);z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowPads(False);z.SetDoNotAllowFootprints(False);z.SetZoneName("SHT40 no copper beneath sensing element")
poly=z.Outline();poly.NewOutline()
for x,y in [(221.5,77.3),(222.5,77.3),(222.5,78.7),(221.5,78.7)]:poly.Append(p.FromMM(x),p.FromMM(y))
board.Add(z)
board.GetTitleBlock().SetTitle("PulsarDew Hub - unrouted prototype floorplan")
board.GetTitleBlock().SetRevision("0.2-draft");board.GetTitleBlock().SetCompany("PulsarFab")
board.GetDesignSettings().m_HoleClearance=p.FromMM(.25)
# pcbnew SaveBoard may rewrite project settings with its default in-memory values.
# Preserve the separately maintained netclasses, clearances and exclusion policy.
pro=output.with_suffix(".kicad_pro")
settings=pro.read_bytes() if pro.exists() else None
try:
    board.SetFileName(str(output));p.SaveBoard(str(output),board)
finally:
    if settings is not None:pro.write_bytes(settings)
print(f"Saved {len(footprints)} schematic footprints + 4 mounting holes + 3 fiducials; zero tracks/vias.")
