# PulsarDew schematic

PulsarDew is the original four-channel dew heater controller. For the expanded
product with switched DC power outlets, two heaters and a USB hub, see
**[PulsarPower](../pulsardewhub/README.md)** (formerly PulsarDew Hub).

Open `pulsardew.kicad_pro` in KiCad 10, then open its root schematic. Revision
0.2 is a connected nine-page hierarchy: system wiring, controller, current
monitor, logic supply, SHT40, and four instances of the heater driver.
Edit the `.kicad_sch` files directly in KiCad; they are the authoritative design.

## Electrical connections

The root drawing shows the protected DC supply through the 2 mΩ shunt to all
four heaters. The logic regulator branches off before the shunt. The INA226
therefore measures **combined heater current**, including gate-drive current,
not four independent currents. Its address is 0x40; the SHT40 address is 0x44.

| Signal | MCU pin | Connection |
| --- | --- | --- |
| Heater 0–3 PWM | PA0–PA3, pads 7–10 | Four independent driver inputs; active low |
| I2C SCL / SDA | PB6 / PB7, pads 30 / 31 | INA226 and SHT40, one pair of 4.7 kΩ pull-ups |
| USB D− / D+ | PA11 / PA12, pads 22 / 23 | Both corresponding USB-C pin pairs |
| USB VBUS sense | PA9, pad 19 | 100 kΩ / 100 kΩ divider |
| SWDIO / SWCLK | PA13 / PA14, pads 24 / 25 | J4 pins 2 / 3 |
| Reset | PF2/NRST, pad 6 | 100 nF to ground and J4 pin 4 |

J4 pins 1 and 5 provide target voltage reference and ground. J101, J201, J301,
and J401 are heater connectors: pin 1 is measured VIN; pin 2 is a switched
return and must not be connected directly to ground. J2 and J3 are parallel
power-input options; use one supply source.

USB is self-powered from the DC supply. USB VBUS is only sensed and is isolated
from the DC and 3.3 V rails. Firmware must disable the MCU's UCPD dead-battery
pull-down on PA9 before sensing VBUS and must enable USB attachment only while
VBUS is present. Firmware implementation is outside this schematic change.

## Repairs made in revision 0.2

- Restored qualified symbol caches and per-sheet instance references. The
  previous files loaded as missing symbols and exported no components.
- Rewired the hierarchy and component pins, with visible branches and junctions.
- Corrected the 2N7002 to gate/source/drain pads 1/2/3. The AOD4184A uses
  gate/drain/source pads 1/2/3.
- Corrected I2C to PB6/PB7; completed both USB-C orientations, reset, bypass
  capacitors, debug access, power input and heater outputs.
- Replaced the incorrectly substituted L78L33 symbol and 12 V HT7333-A part
  with a dedicated **HT7333-1** symbol: pad 1 GND, pad 2 VIN/tab, pad 3 VOUT.
  This retains the stated 12–20 V input range. Input/output bypassing is
  10 µF plus 100 nF as shown in the manufacturer's application circuit.
- Corrected resistor footprint assignments and the missing terminal-block
  library reference. New or changed components without confirmed sourcing
  have no invented LCSC number.

## Reproducible verification

From `hardware/`:

```sh
make check-pulsardew
make verify-pulsardew
make render-pulsardew
```

`verify-pulsardew` runs KiCad ERC with all severities, including exclusions,
then checks exact pin membership of all 32 connected nets and all 22 intentional
no-connects. It requires 58 uniquely referenced components and checks that
every schematic pin has a pad in its assigned footprint. This catches shorts
between rails/channels, incorrect semiconductor pin mapping, missing USB pin
pairs and bypassed shunt connections, even where ERC alone would permit them.

Verified with KiCad CLI 10.0.6: **zero ERC errors, warnings or exclusions**.
The six distinct page designs were also rendered and visually reviewed; four
heater instances share the same drawing with separate reference numbers/nets.

## PCB floorplan (revision 0.3)

The PCB now contains the 58 schematic footprints plus four board-only M3
mounting holes, within a provisional **100 × 80 mm** outline. Mount centers are
4 mm from each edge (92 × 72 mm spacing). It opens in KiCad's PCB Editor with
the schematic UUID links and all 54 named nets preserved.

The left edge carries the alternative DC inputs. Input diode, bulk capacitor,
shunt and INA226 sit together, with space for Kelvin traces from the shunt.
Four identical heater stages and their outward-facing terminals occupy the
bottom edge. The USB connector and MCU are at the top, with MCU bypassing
adjacent to its supply pins. SHT40 is at the upper-right edge, away from the
power stages; a rule area prevents routing/pours below its sensing package.
The MCU uses KiCad's ST UFQFPN-32 footprint, including segmented paste openings,
instead of the inherited footprint whose silkscreen crossed all perimeter pads.

`make verify-floorplan-pulsardew` checks placement and schematic parity. KiCad
10.0.6 reports **zero courtyard overlaps, zero schematic parity issues,
and 130 unconnected items**. The HRO USB-C replacement resolves the former
locator-hole clearance violations; the strict placement check now passes with
zero DRC violations and no exclusions. It is deliberately a floorplan: no
tracks or copper pours are routed.
Power, USB and sense net classes provide routing starting points; their widths
are not a current or controlled-impedance certification. Use an uninterrupted
ground reference under USB, keep heater returns out of the logic/sensor return
path, and derive final widths/USB geometry from the selected fabrication stackup.

## Before manufacture

Connectivity verification does not
validate land-pattern geometry, current capacity, thermal behavior, protection
or assembly sourcing. USB-C J1 now sources HRO TYPE-C-31-M-12 (C165948), using its own
project footprint; see the [connector review](../pulsardewhub/docs/usb-c-sourcing.md). Barrel J2
sources GCT DCJ200-10-A-K1-K (C5280493), matching their assigned footprints.
The old DEALON/XKB source codes did not match those land patterns.
Remaining supplier codes must be reconciled with the exact packages before ordering; the HT7333-1 orderable variant and
capacitor effective values at bias need BOM confirmation.

The inherited inverter driver defaults off only while 3.3 V is present. Loss
or delayed startup of logic power can turn a heater on. Add an independent
hardware inhibit if fail-off behavior under that condition is required. Use
slow heater PWM and validate MOSFET switching losses with this 10 kΩ pull-up
driver. Verify the input diode, connector, shunt and trace current limits;
the INA226 measurement range is not a board current rating. Check LDO
dissipation at the worst input voltage and load. USB ESD protection and input
overcurrent/transient protection remain hardware design review items.

## Pinout and circuit references

- [ST STM32G0B1 datasheet, UFQFPN32 and alternate-function tables](https://www.st.com/resource/en/datasheet/stm32g0b1me.pdf)
- [TI INA226 datasheet](https://www.ti.com/lit/ds/symlink/ina226.pdf)
- [Sensirion SHT4x datasheet](https://sensirion.com/media/documents/33FD6951/662A593A/HT_DS_Datasheet_SHT4x.pdf)
- [Holtek HT73xx-1, pin assignment and application circuit](https://www.holtek.com/webapi/116711/HT73xx-1v120.pdf)
- [Holtek HT73xx, original part's 12 V operating limit](https://www.holtek.com/webapi/116711/HT73xxv180.pdf)
- [onsemi NDS7002A / 2N7002 pinout](https://www.onsemi.com/pdf/datasheet/nds7002a-d.pdf)
- [AOS AOD4184A datasheet](https://www.aosmd.com/res/data_sheets/AOD4184A.pdf)
