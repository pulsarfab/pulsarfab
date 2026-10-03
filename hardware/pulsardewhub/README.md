# PulsarDew Hub — connected schematic and PCB floorplan

Revision **0.1-draft**, reviewed with KiCad 10.0.6 on 2026-10-03. Open
`pulsardewhub.kicad_pro` in KiCad. This is a separate design derived from
PulsarDew, with **two PWM heaters, four individually switched and current-monitored
DC outlets, and four external USB 2.0 ports**. DC outlets use static on/off GPIO;
they must not be PWM controlled.

The schematic is electrically connected and the native PCB is a placed,
**unrouted 180 × 110 mm four-layer floorplan**. It is not ready for fabrication.
There are no tracks, vias or copper fills. No enclosure is assumed.

Review the [14-page schematic PDF](docs/schematic.pdf) and
[annotated footprint placement](docs/pcb-placement.png) without opening KiCad.

![PCB floorplan](docs/pcb-floorplan.png)

## Ratings and assembly options

| Item | Design target / constraint |
| --- | --- |
| Input | **12–20 V nominal**, provisionally retained from the original design |
| XT60 configuration | Fit J10 + F10; **25 A shared continuous target**, pending thermal/copper validation |
| Barrel configuration | Fit J11 + F11 instead; **5 A absolute total ceiling**, **3.5 A provisional continuous budget** after fuse derating |
| DC outlets | Four center-positive **2.0 mm** barrel sockets, 5 A service target each; independent high-side switch, analog current monitor and fault signal |
| Heater outputs | Two screw terminals, 5 A target each; fused positive pin 1 and PWM switched return pin 2 |
| USB | Four USB-A downstream ports, 500 mA service per port; USB-C upstream data connection |

**Populate one input path only. Do not fit/connect both inputs.** J11 and F11
are DNP in the default XT60 assembly. There is no isolation between the two
input connector paths. The barrel option cannot support four loaded 5 A outlets.
At 20 A of DC outlet load, the XT60 target leaves about 5 A of input current for
the heaters, USB conversion and logic together. Six simultaneous 5 A loads are
outside this design budget. The external supply must be current limited and
the wiring/fuses must be coordinated with the final assembly.

F10 is a 30 A S1032 fuse; F11 is a 5 A Littelfuse 451. Heater fuses are 7 A
Littelfuse 451 devices to allow a 5 A service target after room-temperature
derating. Fuse markings are not continuous board-current ratings; ambient
temperature, enclosure, cable ratings and time/current curves still govern.

## Connected hierarchy

There are 14 schematic pages in eight source files. Root-sheet wires connect
the system rails, I2C, heater control, four DC interfaces and USB data/control.
Repeated sheets have distinct references and net identities.

| Sheet | Circuit |
| --- | --- |
| Power input | Alternative fused inputs, LM74700 + CSD18540 reverse-polarity/reverse-current stage, SMCJ20A TVS, 470 µF bulk |
| DC supplies | LMR33630 bucks: input to approximately 5.02 V, then 5 V to approximately 3.31 V |
| Controller | STM32G0B1KBU6, SWD/reset, SHT40, I2C pull-ups, ADC filters and GPIO connections |
| Heaters | TC4427A active-high gate driver, two AOD4184A switches, individual fuses/clamps, combined-current INA226 and 2 mΩ shunt |
| DC outlet ×4 | TPS26631, UV/OV dividers, current limit, IMON filter, latch-off control, fault pull-up and output clamp |
| USB hub | USB2517, 24 MHz crystal, reset supervisor, configuration straps, protected USB-C upstream connection |
| USB port ×4 | TPS2553 current-limited VBUS switch, USBLC6 ESD, USB-A socket, 150 µF bulk and ceramic bypass |

The seven-port USB2517 uses port 1 for the onboard STM32 and ports 2–5 for the
four external sockets. Ports 6 and 7 are disabled by straps. The hub is
self-powered, with individual downstream power control. Its two internal 1.8 V
regulator outputs each have their own capacitor and are not tied together.
Host VBUS is used only for detection and upstream ESD protection, with no
connection to the board's 5 V supply. The selected 150 µF ±20% downstream
capacitors retain at least 120 µF at nominal tolerance.

The LM74700 input circuit is not an overvoltage disconnect. Do not apply more
than 20 V nominal; the TVS is for transients, not sustained excess input voltage.
DC output switches have no external reverse-blocking FET, so **do not backfeed
the DC outlets**. Heater return pins must not be connected directly to ground.

## MCU interface and firmware changes

| Function | STM32 signal / physical pad |
| --- | --- |
| Heater 0 / 1 | PA0 / PA1, pads 7 / 8, active-high PWM |
| DC enable 1 / 2 / 3 / 4 | PB0 / PB1 / PB2 / PB9, pads 15 / 16 / 17 / 1; static GPIO only |
| DC current ADC 1–4 | PA4–PA7, pads 11–14 |
| DC fault 1 / 2 / 3 / 4 | PB3 / PB4 / PB5 / PC6, pads 27 / 28 / 29 / 20; active low |
| USB D− / D+ | PA11 / PA12, pads 22 / 23, internal hub port 1 |
| USB attach permission | PA9, pad 19, hub port 1 PWR output |
| I2C SCL / SDA | PB6 / PB7, pads 30 / 31; INA226 0x40, SHT40 0x44 |
| SWDIO / SWCLK / NRST | PA13 / PA14 / PF2, pads 24 / 25 / 6 |

The original firmware is not a drop-in image: heater polarity and channel count,
ADC inputs, outlet GPIO and hub attachment behavior have changed. Disable the
MCU UCPD dead-battery function on PA9, and detach USB whenever USB_ATTACH is low.
Initialize heater and DC enables low. DC faults latch off until explicitly
reset through the enable signal; do not repeatedly auto-retry a short circuit.

Heater inputs and gates have pull-downs, and the new non-inverting driver
addresses the original driver's dependence on a live 3.3 V rail for default-off
behavior. Validate startup, brownout and loss of each rail on hardware; this is
not a certified safety shutdown. The INA226 measures **combined heater current**;
the four DC currents are measured independently through TPS26631 IMON outputs.

With an 8.2 kΩ IMON resistor, the nominal ADC slope is approximately
**0.2288 V/A** (1.144 V at 5 A). Use calibration and fault status; the monitor has
finite accuracy and is not a precision power meter. The 3.3 kΩ ILIM resistor
sets approximately **5.45 A nominal**, with an estimated **5.02–5.90 A** range
including IC and resistor tolerances. TPS26631 permits a timed approximately
2× overload pulse: it is not an instantaneous 5 A clamp. The ADC divider choice
preserves headroom during this overload behavior.

## PCB floorplan and routing intent

The floorplan contains 215 schematic footprints, four M3 holes and three
fiducials. Mount centers are 4 mm from the edges (172 × 102 mm spacing).
USB connectors occupy the top edge; their switches, ESD devices and bulk caps
are nearby. The hub is behind the downstream ports with the MCU to its left.
DC switches and their output connectors occupy four regions along the bottom.
The two heater stages occupy the lower-left region. Input protection and bucks
sit at the left. SHT40 is at the right edge, with a copper keepout beneath the
sensing element and separation from the major heat sources.

Use L2 as a continuous ground reference. Reserve the lower central corridor
for wide input/return copper and keep high-current returns out of signal/ADC
paths. Use Kelvin connections at the heater shunt. Add exposed-pad thermal
vias and pours at the four TPS26631 devices, power FETs and bucks. Route the
actual buck input hot loops compactly, away from crystal, USB and ADC wiring.

The netclasses are **starting geometry**, not validated ratings: 8 mm input
bus, 3 mm DC/heater routes, 0.6 mm low-voltage power, 0.2 mm sense and provisional
0.25 mm / 0.2 mm USB pair width/gap. High-current paths will require broad pours
and likely multiple copper layers. A provisional 2 oz outer / 1 oz inner copper
target must be reconciled with an orderable JLCPCB stackup; it is not specified
as a verified fabrication stackup in this project. Derive 90 Ω differential
USB geometry from that actual stackup and maintain a continuous return plane.
Connector mating bodies intentionally extend past the outline; verify enclosure
and cable clearances before locking the outline.

## Verification and open findings

From `hardware/`:

```sh
make verify-pulsardewhub
make verify-floorplan-pulsardewhub
make bom-pulsardewhub
```

The electrical check passes with **zero ERC errors, warnings or exclusions**.
It independently checks all **130 connected nets, 45 intentional no-connects,
215 component identities**, critical values, rail isolation, GPIO assignments
and footprint pad coverage. KiCad PCB parity reports zero mismatches and there
are zero courtyard overlaps. See [review details](docs/design-review.md).

The strict floorplan check currently **fails** on four USB-C mounting-hole to
ground-pad clearances: **0.1944 mm actual versus 0.25 mm required**. These are
within the stock GCT USB4105 footprint and require connector/land-pattern and
fabricator reconciliation. No DRC exclusions hide them. There are also **499
unconnected PCB items**. `make jlc-pulsardewhub` is blocked by strict ERC, DRC,
parity and routing checks, so this draft cannot accidentally generate a package
through that target.

At 5 A, each TPS26631 dissipates about 0.78 W using its typical 31 mΩ on-resistance,
or about 1.25 W at 50 mΩ. Four loaded outlets alone can dissipate several watts.
Thermal validation, current-carrying copper, USB signal integrity, EMC/ESD,
connector temperatures, assembly pad geometry and firmware behavior remain
release work. No SPICE or physical testing has been performed.

## Sourcing and footprint review

[JLCPCB BOM](jlcpcb_bom.csv) includes the default 213 populated schematic parts.
[Full review BOM](parts-review.csv) also includes the two DNP input-option parts.
[Parts catalog](parts-catalog.json) records 54 exact LCSC codes, MPNs and datasheet
links. These are sourcing candidates, not reserved stock or confirmation that
every through-hole part is supported by a particular JLC assembly tier.
USB1046 connector availability deserves early rechecking. Automated lifecycle
lookup returned unknown for all 53 populated unique parts; it is not evidence
of active production. Check lifecycle and stock before procurement.

Custom footprints in `../lib/footprints.pretty` include the TI PWP0020T exposed
pad (**2.96 × 2.96 mm**), S1032 fuse, SMMS1050 inductors, RVT 6.3 mm capacitor
and KF128 5.08 mm terminal. Dimensions and pin mappings were checked against
manufacturer documents; record a second footprint review before fabrication.
The three `*_Edge` connector footprints derive from the KiCad 10 library: AMASS
XT60PW-M, GCT DCJ200 and GCT USB1046. They retain the original copper, drills and
fabrication outlines, with front silkscreen trimmed at the board edge. KiCad
library attribution/license is recorded in [library notes](../lib/ATTRIBUTIONS.md).
XT60 positive is physical **pad 2**, negative pad 1.

The native schematic and board are editable. `make gen-pulsardewhub` explicitly
replaces the schematic from `scripts/pulsardewhub.schgen.py`; capture GUI changes
there before regeneration. The initial placement script requires KiCad's
`pcbnew` Python and refuses to overwrite a board without `--replace`; it also
refuses to erase a board containing tracks. It preserves project routing rules.
Use KiCad directly for subsequent routing and treat the native PCB as authoritative.

## Primary references

- [Microchip USB2517 datasheet](https://ww1.microchip.com/downloads/en/DeviceDoc/00001598C.pdf)
- [TI TPS2663 family](https://www.ti.com/lit/ds/symlink/tps2663.pdf), [TPS2553](https://www.ti.com/lit/ds/symlink/tps2553.pdf)
- [TI LM74700-Q1](https://www.ti.com/lit/ds/symlink/lm74700-q1.pdf), [CSD18540Q5B](https://www.ti.com/lit/ds/symlink/csd18540q5b.pdf)
- [TI LMR33630](https://www.ti.com/lit/ds/symlink/lmr33630.pdf), [TPS3808](https://www.ti.com/lit/ds/symlink/tps3808.pdf), [INA226](https://www.ti.com/lit/ds/symlink/ina226.pdf)
- [ST STM32G0B1](https://www.st.com/resource/en/datasheet/stm32g0b1me.pdf), [USBLC6-2](https://www.st.com/resource/en/datasheet/usblc6-2.pdf)
- [GCT USB4105 drawing](https://gct.co/files/drawings/usb4105.pdf), [DCJ200 drawing](https://gct.co/files/drawings/dcj200.pdf)
- [Reviewed document hashes and catalog links](docs/datasheet-review-manifest.json)

The installed [kicad-happy skills](https://github.com/aklofas/kicad-happy) were
used for KiCad analysis, exact LCSC lookups, datasheet retrieval and JLCPCB review.
