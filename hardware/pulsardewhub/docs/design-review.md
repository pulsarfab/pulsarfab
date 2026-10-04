# PulsarDew Hub design review (0.2-draft) — 2026-10-03

**Verdict:** connected schematic and editable placement draft; **not ready for
fabrication**. The native board has 499 unconnected items and four unresolved
USB-C hole clearances. The 5 A per-output requirement is a design target pending
routing, thermal verification and prototype tests. No enclosure has been chosen.

## Release blockers

| Finding | Evidence and next action |
| --- | --- |
| Unrouted board | Raw PCB / KiCad DRC: zero tracks and vias, no ground fills, 499 unconnected items. Route power, ground, signals and thermal vias before fabrication. |
| USB-C locating holes | KiCad DRC: four hole-to-ground-pad gaps of 0.1944 mm versus the 0.25 mm rule. Stock USB4105 geometry and GCT drawing were reviewed; reconcile the land pattern with assembly/fabricator limits. Do not suppress the errors. |
| Full-load current and heat | Inference/calculation: four 5 A TPS259827 paths dissipate roughly 0.27–0.45 W together, excluding quiescent loss before regulator/heater/input losses. Copper and enclosure cooling are not modeled. |
| Firmware differs from original | Raw schematic: two active-high heaters, four new enable/power-good/ADC interfaces and internal hub connection. Update and test firmware before applying loads. |
| Supply and load constraints | Selected 12–18 V input, 25 A shared XT60 target, 3.5 A continuous barrel target. Six 5 A loads simultaneously exceed the budget. Validate startup, overload, cable and connector temperature. |
| Procurement and assembly | Exact source candidates are populated, but stock, lifecycle, through-hole assembly availability and custom land patterns require release review. |

## What was checked

KiCad CLI 10.0.6 ERC passes with **zero errors, warnings and exclusions**.
`verify-pulsardewhub.py` independently specifies every expected component pin and
compares complete net membership: **223 components, 130 connected nets and 33
intentional no-connects**. It also checks critical resistor/capacitor choices,
source fields, and that every schematic pin exists in its assigned footprint.
This is raw-file connectivity evidence, not proof of analog behavior.

PCB DRC confirms **zero schematic parity errors, zero courtyard overlaps and
zero footprint-library mismatches**. The board has 223 schematic footprints,
four mounting holes and three fiducials. Native net assignments retain the
sheet-instance UUID links. Critical power-pin mappings, USB pairs, connector
polarity and exposed-pad geometry were manually compared with the manufacturer
documents as described below. The saved schematic PDF and rendered sheet/PCB
images were visually inspected. The new project was launched in KiCad, but a
locked Mac prevented the final native-window inspection. CLI load/export and
rendered inspection succeeded independently; GUI inspection remains a handoff item.

The independent net checker was also challenged with temporary corrupted
netlists: a missing upstream USB pin, shorted DC outlets, and reversed XT60
polarity were all rejected. In 0.2, tying exposed pad 25 to ground, selecting the
16.9 V cutoff variant, and disconnecting the OV inhibit were also rejected.
No source design files were altered by those checks.

## Manual datasheet review basis

This table describes the checked portions of the documents, not an assertion
that every specification and package tolerance has been qualified. Document
URLs and local-copy hashes are in `datasheet-review-manifest.json` and the
part-specific catalog. Some catalog URLs point to a family document.

| Components | Manufacturer document section / reviewed detail |
| --- | --- |
| U40 USB2517 | Microchip DS00001598C, pin descriptions, configuration straps, non-removable/disabled ports and 64-QFN package drawing. Ports 1–5 used; 6/7 disabled; independent 1.8 V output capacitors. |
| U101/U201/U301/U401 TPS259827ONRGET | TI SLVSEI3D Rev. D, pins, equation 4, IMON, latch-off, PG and RGE0024M drawings. Pad 25 is VIN (2.7 × 1.45 mm); pad 26 is GND (2.7 × 0.85 mm), with independent paste windows. ITIMER open; RETRY_DLY/NRETRY/LDSTRT grounded. |
| U102/U202/U302/U402 TPS3700 | TI SBVS187G pins, comparator thresholds, UVLO/POR and open-drain behavior. VDD on 3.3 V; both outputs clamp EN_SW; separate UV/OV sense dividers. |
| D10 / outlet Dxx1/Dxx2 | Jingdao SMCJ18A/SMBJ18A family tables: 18 V stand-off, 29.2 V rated pulse clamp. MDD SS54: 5 A, 40 V, 0.55 V maximum forward drop at 5 A. Input transient and negative output clamp roles checked; bench surge energy qualification is open. |
| U10 / Q10 | TI LM74700-Q1 pin functions/application circuit and CSD18540Q5B terminal diagram. Correct anode/cathode/gate path, charge-pump capacitor and physical source/drain pad mapping. |
| U20/U30 LMR33630 | TI pin functions, output-voltage design and application sections. VIN, EN, BOOT/SW, VCC, FB, ground/EP and passive network connections. Input bypasses adjacent to IC in floorplan; routing still pending. |
| U501/U601/U701/U801 TPS2553 | TI pin functions/current-limit resistor section. Active-high enable, open-drain fault, input/output and ILIM assignments; 43.2 kΩ target limit around 0.60 A. |
| U41 TPS3808G33 | TI pin functions/reset-delay section. MR, SENSE and VDD on 3.3 V, CT open, open-drain RESET pull-up. |
| U50 TC4427A / Q51/Q61 | Microchip non-inverting dual-driver terminal/function diagram; AOS AOD4184A gate/drain/source diagram. Driver inputs and MOSFET gates have pull-downs; active-high heater behavior. |
| U1/U2/U51 | ST UFQFPN32 terminal/alternate-function tables; Sensirion SHT4x pin table; TI INA226 pin functions/addressing. These build on the original design review. INA226 0x40, SHT40 0x44. |
| USBLC6 devices | ST USBLC6-2SC6 terminal/application diagrams: common data pairs 1/6 and 3/4, VBUS 5, ground 2. Final route should flow through the package without stubs. |
| J10 | AMASS XT60PW-M polarity and stock land pattern: **pad 2 positive**, pad 1 ground. Edge variant changes silk only. |
| Barrel sockets | GCT DCJ200 drawing: center-positive terminal assignment, 2.0 mm pin, 5 A / 20 V rating, slot and pad placement. |
| J40 | GCT USB4105 drawing and USB-C contact assignments. Both orientations connected, separate 5.1 kΩ CC pull-downs, SBU pins NC. Hole clearance remains open. |
| USB-A sockets | SHOU HAN AF 90 ZJWG / C456019: manufacturer drawing gives four Ø0.92 mm contact holes, two Ø2.30 mm shell holes, 13.14 mm shell pitch and 2.71 mm row offset; local footprint matches. Pin numbering follows the drawing and USB-A symbol (1 VBUS, 2 D−, 3 D+, 4 GND, SH grounded). 1.5 A rating exceeds the 500 mA port budget. Body-to-pin longitudinal registration is missing from the drawing and remains provisional; check a sample before fab/enclosure release. |
| J51/J61 / J1 | KEFA KF128 mechanical/pin layout, 5.08 mm pitch and recommended drill; XFCN 2.54 mm single-row header drawing. SWD order: 3V3, SWDIO, SWCLK, NRST, GND. |
| L20/L30 | SXN SMMS1050 dimensions/recommended land table: 8.2 µH / 6.8 µH; pad lands 4.1 mm square, 5.4 mm inner gap. Saturation/heating margin remains load/temperature dependent. |
| F10/F11/F51/F61 | SART S1032 size table and Littelfuse 451 family derating/time-current curves. 30 A input, optional 5 A barrel, 7 A heater fuses. Fuse coordination remains a prototype/release check. |
| C502/C602/C702/C802 | DMBJ RVT family 6.3 mm body/land tables; 150 µF ±20%, 10 V. Minimum nominal-tolerance capacitance 120 µF. |
| C12/R50 | AISHI 470 µF / 35 V dimensions; HoLLR2512 2 mΩ / 3 W shunt source. At 10 A, shunt dissipation is 0.2 W; Kelvin routing required. |
| Other two-pin R/C parts | Exact MPN/LCSC and nominal value/package consistency checked. Pin polarity is not applicable to unpolarized parts. Full bias, aging, temperature and substitution qualification is still open. |
| Y40 | 24 MHz, 12 pF load source candidate and 3225 pad functions checked. The 18 pF capacitors assume about 3 pF parasitic loading; oscillator drive/startup must be measured. |

The upstream USB host rail is isolated from V5 and VIN in the exact-net model.
The heater shunt cannot be bypassed in that model; all four DC OUT nets and
their ADC/enable/power-good nets are distinct. No-connects are explicit, including
unused MCU GPIO, hub ports and TPS259827 ITIMER pins. A no-connect marker is not used to silence an unexamined power pin.

## Power and signal calculations

- Buck feedback: `1 V × (1 + 100k/24.9k) = 5.016 V` and
  `1 V × (1 + 100k/43.2k) = 3.315 V`. Four 500 mA USB loads plus provisional
  0.4 A equivalent logic/support budget leave about 0.6 A below the 3 A 5 V
  regulator rating. This is an estimate; check efficiency, transient loads and
  effective output capacitance at bias.
- DC voltage window: 0.4 V × (1 + 220k/10k) = 9.2 V UV; 0.4 V ×
  (1 + 470k/10k) = 19.2 V OV. Worst-case OV is about 18.62–19.78 V with
  1% resistors and 396–404 mV threshold; input leakage adds under 8 mV.
- Enable logic: 10k series/100k pulldown gives about 3.0 V from a 3.3 V GPIO,
  above the 1.23 V maximum rising threshold. TPS3700 sinks under 0.34 mA and
  specifies VOL ≤0.25 V, below the eFuse's shutdown/reset range. Loss of V3
  makes OUTA low down to the monitor's POR region; pulldown and GPIO default-off
  behavior must still be tested through startup/brownout.
- IMON: 246 µA/A × 820 Ω = 0.20172 V/A, 1.0086 V at 5 A. At 15 A,
  253.4 µA/A × 828.2 Ω = 3.148 V is a screening calculation. The published
  gain limits apply at 3 A up to ILIM and TA ≤75°C; this does not guarantee
  monitor behavior during a short transient. The 10k/10n filter is 100 µs,
  about 1.59 kHz; ADC acquisition time must include source impedance.
- Breaker threshold: 1460/249 + 0.11 = 5.973 A nominal. There is no published
  guaranteed full-temperature min/max specifically at 249 Ω. A ±15% screening
  assumption plus 1% resistor gives approximately 5.027–6.936 A, but must not be
  presented as a guaranteed operating range. Qualification must establish 5 A
  no-trip service and bounded overload trip. ITIMER open requests the fastest
  breaker response; separate short-circuit fast trip is nominally 2.1× ILIM.
- dVdt: 4600 pF/4700 pF = 0.979 V/ms; 18 V rise takes about 18.4 ms nominal.
  Capacitive load/inrush, resistive-load dissipation during startup and SOA
  remain prototype checks. No load-handshake dependency is present.
- Heater shunt: 2 mΩ gives 20 mV and 0.2 W at 10 A. Driver supply load and
  current-monitor calibration must be included in firmware interpretation.
- USB differential impedance, skew, return paths and termination behavior have
  not been simulated; there are no routed traces to assess.

## Historical automated analysis and triage (0.1)

The following analyzer counts describe the prior TPS26631 revision only. They
were not rerun for this focused component substitution. Fresh 0.2 evidence is
the independent pin/value/BOM check, KiCad ERC/DRC/parity and rendered inspection
above. Do not treat the historical counts or MODE/PG warnings below as current.

The installed kicad-happy tools were run in addition to KiCad on 0.1:

| Analyzer | Outcome / limits |
| --- | --- |
| `analyze_schematic.py` including lifecycle | 156 findings in the lifecycle run: 8 errors, 15 warnings, 133 informational. Heuristic findings were checked against raw nets and the manual review; they are not ERC errors. |
| `analyze_pcb.py --full` | Final placement run: 160 findings, dominated by 130 unrouted nets. Three fiducials added; no routed-copper validation possible. |
| `cross_analysis.py` | Zero findings; native KiCad parity also reports zero issues. |
| `analyze_thermal.py` | Ran, but assessed only two regulators with an assumed 0.141 W total. Its 100 score / 35.5 °C maximum are **not usable thermal evidence** for this high-current design. No valid full-load thermal model exists. |
| `analyze_emc.py` | Final run: 25 findings (8 errors, 4 warnings, 13 informational). Missing planes/stitching are real routing work; no EMC compliance conclusion is possible. |
| Lifecycle audit | 53 unique populated MPNs checked; no lifecycle sources available, all 53 **unknown**. The tool's generic recommendation to replace unknown parts is not accepted as evidence of obsolescence. |
| `diff_analysis.py` | Compared earlier and final PCB/EMC runs: three fiducials added and upstream bypass moved closer to ESD. The latter proximity warning cleared. Score changes are heuristic, not compliance improvement measurements. |

Reviewed false positives and intentional conditions:

- **PP-001, V5 has no DC source:** the analyzer does not follow the buck SW pin
  through its inductor. U20/L20 supply V5; the exact-net checker traces this.
- **PR-001, I2C lacks pull-ups:** hierarchical-name matching missed R1/R2.
  Both 4.7 kΩ pull-ups connect the actual SCL/SDA nets to V3.
- **NRST / PG / MODE / GANG_EN warnings:** MCU internal reset pull-up is used;
  unused PG outputs are NC; MODE is intentionally open for latch-off; GANG_EN
  is low for individual USB power control. No external pull-up should be added
  blindly to these pins.
- **HOST_VBUS source/decoupling:** this rail is only sensed and used by ESD,
  not a bus-powered board supply. The downstream VBUS bulk is separate.
- **KO-001 at SHT40:** the rule area prohibits copper beneath the sensing
  element but explicitly permits the component and its pads. Native DRC accepts it.
- **Connector courtyard overhangs:** mating bodies face outside the board;
  copper/drills remain inside. Enclosure/cable fit still requires review.
- **SW-003 buck hot-loop warning:** the heuristic chose remote bulk capacitors
  C12/C24 instead of the local C20/C30 input bypasses. This does not clear the
  real requirement to route compact loops and measure switching behavior.
- **IO-001 DC filtering:** output TVS devices exist; this does not establish
  sufficient cable EMC filtering. Do not substitute low-current ferrites into
  5 A paths based only on the generic recommendation.
- **DS-002:** there is no in-project extracted-datasheet directory. Critical
  manufacturer PDFs were retrieved separately and manually checked. Automated
  datasheet coverage is incomplete; other passive qualification remains open.

## 0.2 change and validation scope

The user accepted the TPS25982 Rev. D −15°C lower junction limit. All four DC
outlets now use TPS259827ONRGET C2155765; positive switching and direct grounded
returns remain explicit in the independent net model. Current/thermal shutdown
latches off through grounded RETRY_DLY. PG replaces FLT on the same four MCU pads.
Each TPS3700 is a firmware-independent voltage inhibit, with automatic recovery;
this may reset a latched fault and therefore requires ENABLE deassertion in
firmware when an explicit restart policy is desired. SMCJ18A replaces the input
20 V TVS; each outlet adds a local SMBJ18A at IN and SS54 at OUT. The 29.2 V TVS
clamp versus 30 V eFuse absolute maximum needs measured overshoot/temperature
qualification. This is not a sustained-overvoltage input disconnect.

Symbol pins, two-pad footprint geometry and paste apertures were compared with
the manufacturer drawings. Board stays 180 × 110 mm, 4-layer and unrouted.
The previous four USB-C hole-clearance findings remain; no new native DRC
violations or courtyard overlaps remain. No firmware binary, routing, surge test,
thermal validation, SPICE, lifecycle audit or complete new automated analysis
suite is claimed for this change.

## Changes since the original design

The original PulsarDew remains a separate four-heater project. Its connected
schematic and 100 × 80 mm floorplan were committed before this variant.
This variant replaces its inverter-style heater drive, adds individual DC
eFuses and ADC monitoring, replaces the small logic supply with bucks, and adds
the self-powered USB hub and ESD/power protection. The original's source codes
for USB-C and barrel connectors were corrected to match the GCT footprints.

The 0.1 review corrected XT60 polarity, the prior TPS26631 exposed-pad size
and SHDN pull-down, IMON overload headroom, USB bulk capacitance, heater fuses,
and several land patterns and placement conflicts. Revision 0.2 supersedes the
TPS26631 circuit as detailed above. Earlier draft calculations are not release data.

## Review limits and next work

No SPICE simulator (`ngspice`, `ltspice`, `xyce`) was installed, so simulation was
not run. No Gerbers were generated for this unrouted revision, so Gerber analysis
is not applicable. There is no prior manufactured revision of this hub to compare.
No automated extracted-datasheet deep-review file exists; the manual checks
above provide the stated evidence, with the explicit gaps retained.

Before a board order: resolve the USB-C land clearance, choose the stackup and
final outline, complete routing/planes/thermal vias, expose suitable bring-up
test points, review solder paste/assembly rotation and source variants, and
rerun strict ERC/DRC/parity with zero unrouted connections. Prototype testing
must cover full simultaneous loads within the shared budget, connector and
switch temperatures, short circuit/overload and startup/brownout behavior, USB
enumeration and throughput under heater switching, and conducted/radiated ESD/EMC.
The placement draft is useful for this next engineering phase; it is not a
manufacturing or current-rating sign-off.
