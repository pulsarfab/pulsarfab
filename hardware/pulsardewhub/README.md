# PulsarPower — power distribution, dew control and USB hub

**PulsarPower** is the expanded power product derived from the original
**[PulsarDew](../pulsardew/README.md)** dew heater controller. It combines four
switched DC outlets, two dew heaters and a four-port USB 2.0 hub. Earlier design
documents call it **PulsarDew Hub**; the directory, KiCad filenames and Makefile
targets currently retain `pulsardewhub` as their internal project identifier.

Revision **0.2-draft**, reviewed with KiCad 10.0.6 on 2026-10-03. Open
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
| Input | **12–18 V nominal**, as selected for this revision |
| XT60 configuration | Fit J10 + F10; **25 A shared continuous target**, pending thermal/copper validation |
| Barrel configuration | Fit J11 + F11 instead; **5 A absolute total ceiling**, **3.5 A provisional continuous budget** after fuse derating |
| DC outlets | Four center-positive **2.0 mm** barrel sockets, 5 A service target each; independent high-side switch, analog current monitor and power-good signal |
| Heater outputs | Two screw terminals, 5 A target each; fused positive pin 1 and PWM switched return pin 2 |
| USB | Four USB-A downstream ports, 500 mA service per port; USB-C upstream data connection |

The **5 V regulator is rated for 3 A total**. Four USB ports reserve 2 A at
500 mA each; a provisional 0.4 A equivalent budget for onboard logic/support
leaves about 0.6 A margin. This is a design budget pending thermal and transient
testing, not an additional external 5 V output rating.

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
| Power input | Alternative fused inputs, LM74700 + CSD18540 reverse-polarity/reverse-current stage, SMCJ18A TVS, 470 µF bulk |
| DC supplies | LMR33630 bucks: input to approximately 5.02 V, then 5 V to approximately 3.31 V |
| Controller | STM32G0B1KBU6, SWD/reset, SHT40, I2C pull-ups, ADC filters and GPIO connections |
| Heaters | TC4427A active-high gate driver, two AOD4184A switches, individual fuses/clamps, combined-current INA226 and 2 mΩ shunt |
| DC outlet ×4 | TPS259827ONRGET circuit breaker, TPS3700 hardware UV/OV inhibit, IMON filter, latch-off, PG pull-up, input TVS and output Schottky clamp |
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
than 18 V nominal; the TVS is for transients, not sustained excess input voltage.
DC output switches have no external reverse-blocking FET, so **do not backfeed
the DC outlets**. Heater return pins must not be connected directly to ground.

## MCU interface and firmware changes

| Function | STM32 signal / physical pad |
| --- | --- |
| Heater 0 / 1 | PA0 / PA1, pads 7 / 8, active-high PWM |
| DC enable 1 / 2 / 3 / 4 | PB0 / PB1 / PB2 / PB9, pads 15 / 16 / 17 / 1; static GPIO only |
| DC current ADC 1–4 | PA4–PA7, pads 11–14 |
| DC power-good 1 / 2 / 3 / 4 | PB3 / PB4 / PB5 / PC6, pads 27 / 28 / 29 / 20; high = output ready |
| USB D− / D+ | PA11 / PA12, pads 22 / 23, internal hub port 1 |
| USB attach permission | PA9, pad 19, hub port 1 PWR output |
| I2C SCL / SDA | PB6 / PB7, pads 30 / 31; INA226 0x40, SHT40 0x44 |
| SWDIO / SWCLK / NRST | PA13 / PA14 / PF2, pads 24 / 25 / 6 |

The original firmware is not a drop-in image: heater polarity and channel count,
ADC inputs, outlet GPIO and hub attachment behavior have changed. Disable the
MCU UCPD dead-battery function on PA9, and detach USB whenever USB_ATTACH is low.
Initialize heater and DC enables low. Overcurrent/thermal faults latch off until
reset through the enable signal; do not repeatedly retry a short circuit.
`DC_PG1..4` replaces the former `DC_FLT1..4` labels on the same MCU pins. PG low
also means disabled, starting, or voltage-inhibited. Qualify PG against the
commanded state and allow startup settling. The voltage window is an automatic
hardware inhibit: recovery can re-enable a still-asserted GPIO and can reset a
latched fault by pulling EN low. Firmware should deassert ENABLE after an
unexpected PG loss if an explicit user restart is required.

Heater inputs and gates have pull-downs, and the new non-inverting driver
addresses the original driver's dependence on a live 3.3 V rail for default-off
behavior. Validate startup, brownout and loss of each rail on hardware; this is
not a certified safety shutdown. The INA226 measures **combined heater current**;
the four DC currents are measured independently through TPS259827 IMON outputs.

With an 820 Ω IMON resistor, the nominal ADC slope is **0.20172 V/A**
(**1.009 V at 5 A**). The 10 kΩ / 10 nF filter has a nominal 100 µs time constant;
include the monitor source impedance in ADC acquisition-time settings. TI
specifies gain limits of 238.6–253.4 µA/A for 3 A to the set limit and ambient
up to 75°C; low-current accuracy and calibration need prototype validation.

A 249 Ω, 1% ILIM resistor gives **5.97 A nominal** using TI equation 4. This is
an overload trip threshold for a **5 A service target**, not a precise 5 A clamp.
TI publishes full-temperature threshold limits at selected resistor values,
not 249 Ω; the 5 A minimum no-trip margin is **not yet guaranteed**. Measure it
across supply and temperature before release. ITIMER is open for the fastest
normal overload response. Severe shorts use a separate fast trip around 2.1×
the setpoint. RETRY_DLY, NRETRY and LDSTRT are grounded; load handshake is disabled
and overcurrent/thermal shutdown latches off. The 4.7 nF slew capacitor targets
about 0.979 V/ms, or 18.4 ms at 18 V; verify startup with actual capacitive loads.

Each TPS3700 monitors VIN independently of firmware and clamps the switch enable
through open-drain outputs. Nominal thresholds are **9.2 V rising UV** and
**19.2 V rising OV**, using 220 kΩ/10 kΩ and 470 kΩ/10 kΩ dividers. OV tolerances
are approximately 18.62–19.78 V including 1% resistors and comparator threshold
limits; input leakage adds less than 8 mV. The 10 kΩ GPIO series resistor avoids
output contention; 100 kΩ at the switch enable requests OFF during reset.
This inhibits the DC outputs; it does not disconnect VIN from the ICs, bucks or
heaters, and is not protection against arbitrary sustained excess input voltage.

**−15°C minimum switch junction temperature is accepted for this design.** The
TPS25982 Rev. D datasheet changed this limit in May 2026. Upper junction limit is
125°C; board ambient limits still require thermal qualification. Do not substitute
a TPS259822/3/4 variant: their fixed overvoltage cutoff is below the full 18 V range.

## PCB floorplan and routing intent

The floorplan contains 223 schematic footprints, four M3 holes and three
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
vias and pours at the four TPS259827 devices, power FETs and bucks. Route the
actual buck input hot loops compactly, away from crystal, USB and ADC wiring.
For TPS259827, **pad 25 is VIN; pad 26 is GND**. The large pad must not be tied
to the ground plane. Keep both pads thermally coupled and use VIN-connected vias
on pad 25. Place the SMBJ18A and SS54 close to the protected IN/OUT pins.

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
It independently checks all **130 connected nets, 33 intentional no-connects,
223 component identities**, critical values, rail isolation, GPIO assignments
and footprint pad coverage. KiCad PCB parity reports zero mismatches and there
are zero courtyard overlaps. See [review details](docs/design-review.md).

The strict floorplan check currently **fails** on four USB-C mounting-hole to
ground-pad clearances: **0.1944 mm actual versus 0.25 mm required**. These are
within the stock GCT USB4105 footprint and require connector/land-pattern and
fabricator reconciliation. No DRC exclusions hide them. There are also **499
unconnected PCB items**. `make jlc-pulsardewhub` is blocked by strict ERC, DRC,
parity and routing checks, so this draft cannot accidentally generate a package
through that target.

At 5 A, each TPS259827 dissipates about **0.0675 W typical / 0.1125 W using
maximum hot on-resistance**, or about 0.27–0.45 W across four switches, excluding
quiescent loss. These are conduction calculations, not measured temperatures.
Thermal validation, current-carrying copper, USB signal integrity, EMC/ESD,
connector temperatures, assembly pad geometry and firmware remain release work.
SMCJ18A/SMBJ18A have a 29.2 V specified pulse clamp versus the eFuse's 30 V
absolute maximum: layout inductance, temperature and pulse energy leave little
margin and must be checked on hardware. SS54 clamps negative output transients;
its pulse energy/current capability also needs load-specific validation.
No SPICE or physical testing has been performed.

## Sourcing and footprint review

[JLCPCB BOM](jlcpcb_bom.csv) includes the default 221 populated schematic parts.
[Full review BOM](parts-review.csv) also includes the two DNP input-option parts.
[Parts catalog](parts-catalog.json) records 54 exact LCSC codes, MPNs and datasheet
links. These are sourcing candidates, not reserved stock or confirmation that
every through-hole part is supported by a particular JLC assembly tier.
USB1046 connector availability deserves early rechecking. The original 0.1
lifecycle audit returned unknown for all 53 populated unique parts. It is historical evidence, not a current lifecycle audit. Check lifecycle
and stock before procurement. TPS259827ONRGET is C2155765; JLCPCB showed 665
available without preorder on 2026-10-03, not reserved inventory.

Custom footprints in `../lib/footprints.pretty` include the TI RGE0024M two-pad
QFN (**pad 25: 2.7 × 1.45 mm VIN; pad 26: 2.7 × 0.85 mm GND**), S1032 fuse,
SMMS1050 inductors, RVT 6.3 mm capacitor
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
- [TI TPS25982 Rev. D](https://www.ti.com/lit/ds/symlink/tps25982.pdf), [TPS3700](https://www.ti.com/lit/ds/symlink/tps3700.pdf), [TPS2553](https://www.ti.com/lit/ds/symlink/tps2553.pdf)
- [TI LM74700-Q1](https://www.ti.com/lit/ds/symlink/lm74700-q1.pdf), [CSD18540Q5B](https://www.ti.com/lit/ds/symlink/csd18540q5b.pdf)
- [TI LMR33630](https://www.ti.com/lit/ds/symlink/lmr33630.pdf), [TPS3808](https://www.ti.com/lit/ds/symlink/tps3808.pdf), [INA226](https://www.ti.com/lit/ds/symlink/ina226.pdf)
- [ST STM32G0B1](https://www.st.com/resource/en/datasheet/stm32g0b1me.pdf), [USBLC6-2](https://www.st.com/resource/en/datasheet/usblc6-2.pdf)
- [GCT USB4105 drawing](https://gct.co/files/drawings/usb4105.pdf), [DCJ200 drawing](https://gct.co/files/drawings/dcj200.pdf)
- [Reviewed document hashes and catalog links](docs/datasheet-review-manifest.json)

The installed [kicad-happy skills](https://github.com/aklofas/kicad-happy) were
used for KiCad analysis, exact LCSC lookups, datasheet retrieval and JLCPCB review.
