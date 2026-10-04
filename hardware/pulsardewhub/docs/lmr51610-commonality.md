# LMR51610 3.3 V substitution — 2026-10-03

**Implemented in the schematic and native PCB floorplan: U30 is LMR51610XDBVR / C20539658. U20 remains LMR33630ADDAR, 5 V / 3 A.** The logic stage has a 650 mA planning budget. Electrical arithmetic and pin/net checks pass; routing, effective capacitance and prototype qualification remain open.

## Commonality and cost

The canonical shared inventory records **185 LMR51610XDBVR / C20539658**. Twenty boards plus 10% spares allocate 22, leaving 163 before other unrecorded reservations. The physical inventory balance remains 185. A search of local KiCad schematics found no existing LMR51610XDBVR circuit to copy, so this is owned-part reuse and a potential future standard, not demonstrated reuse of a qualified circuit. The original Dew uses an HT7333-1 LDO; changing that design would be a separate power-supply change.

U20 retains LMR33630ADDAR / C841384. Replacing U30 introduces a second regulator SKU here while using the shared owned pool. The trade is inventory commonality across projects versus commonality within this board.

[JLCPCB LMR33630](https://jlcpcb.com/partdetail/C841384) cart was reduced from 44 at $0.5430 ($23.90) to 22 at $0.6276 ($13.81). Using 22 owned LMR51610s avoids **$10.09 of IC purchasing**, with no additional passive purchase required. Existing 1000-piece resistor and 500-piece bypass-capacitor lots cover the changed demand; the 12 kΩ part uses owned stock. The 44-piece 220 nF cart line remains: 22 allocated to U20 and 22 shared spares. Buying new LMR51610s at $0.5479 would cost $12.05; the two purchased regulator lines would total $25.86, **$1.96 more** than the former 44-piece line. The saving depends on owned stock, not a universally cheaper IC. Public availability: 6,706 LMR51610 and 43,420 LMR33630 on this check; stock is not reserved.

## Electrical suitability and load budget

[TI SLUSEY1B](https://www.ti.com/lit/ds/symlink/lmr51610.pdf), revision B, specifies the exact XDBVR variant as **1 A, 400 kHz, PFM**, SOT-23-6, with a 0.8 V reference. Recommended junction temperature is −40 to +150°C. The datasheet says 4–65 V input while the product summary says 4.5–65 V; a 4.75–5.25 V design input band satisfies both. Startup/brownout must still be tested. It cannot replace the 3 A USB regulator.

Use this conservative planning budget on the 3.3 V rail:

| Load | Allocated current | Basis |
| --- | ---: | --- |
| USB2517 | 460 mA | Microchip DS00001598C table 8-2 maximum for seven HS ports; conservative for the five used ports, with the datasheet's measurement conditions/qualification note |
| STM32G0B1 | 50 mA | Design allowance, not a datasheet maximum; includes core, USB, ADC and GPIO activity. ST DS13560 rev 3 table 28 lists up to 9.9 mA for 64 MHz core with peripherals disabled; firmware-dependent additions remain to be measured |
| SHT40 heater pulse | 100 mA | Sensirion SHT4x table 4 maximum at highest heater setting; ordinary measurement is much lower |
| INA226, logic, pull-ups, supervisor and reserve | 25 mA | Design allowance, including simultaneous asserted pulls; verify on prototype |
| **Total / rounded design target** | **635 / 650 mA** | Leaves 350 mA nameplate headroom on a 1 A converter; not thermal qualification |

At 3.31 V, 650 mA, 4.75 V input and an assumed 85% efficiency, the logic buck draws about **0.533 A** from 5 V. Reserve **0.6 A** including direct 5 V support loads. Four USB ports at 0.5 A plus this allowance total 2.6 A, leaving about **0.4 A** of the 3 A budget. This replaces the earlier optimistic 0.4 A logic / 0.6 A margin estimate. Efficiency is an assumption, not a measured guarantee. SHT40 heater duty limits still apply.

## Implemented circuit and placement

The LMR51610 is not footprint- or pin-compatible with the HSOP-8 LMR33630. U30 now uses SOT-23-6 with the TI pin mapping: **1 CB, 2 GND, 3 FB, 4 EN, 5 VIN, 6 SW**. EN and VIN both connect to the upstream 5 V rail. C32 (old VCC bypass) is removed because this IC has no VCC pin. C33 remains 100 nF from CB to SW. C31 changes to 100 nF / 50 V beside VIN; C30 retains 10 µF / 50 V bulk input bypass. The existing rail supervisor is retained; no PG connection is required.

Feedback is **R30 = 100 kΩ above FB, R31 = 20 kΩ plus R32 = 12 kΩ in series below FB**, giving `0.8 × (1 + 100/32) = 3.300 V`. These values reuse resistor SKUs already in the shared BOM. With reference limits 0.788–0.812 V and ±2% total resistor allowance (1% initial plus temperature allowance), the calculated rail is **3.154–3.453 V**. Startup and load transients are outside that static calculation. The former 43.2 kΩ lower leg would produce only 2.652 V and is explicitly rejected by the verifier.

The native floorplan and placement generator include the new footprint, series feedback resistor and revised local bypass/inductor positions. The CB capacitor is next to the switching pins, the input bypass is beside VIN, and the feedback network is on the opposite side of the switch node. No tracks exist yet; final hot-loop area and quiet feedback routing must be checked after routing.

At nominal 5 V → 3.3 V, 400 kHz and 6.8 µH, calculated ripple is **0.413 A peak-to-peak**. At 5.25 V, 340 kHz and −20% inductance it rises to **0.663 A**. Including the rail tolerance above raises worst-case ripple to approximately 0.681 A. A 650 mA load then peaks at approximately 0.991 A, below the 1.25 A minimum high-side current limit; a full 1 A load would peak at 1.331 A and can hit that limit. Thus the existing inductor is not evidence of guaranteed full 1 A delivery with this controller. The selected 6.8 µH inductor is retained for the 650 mA budget and still needs prototype qualification. A smaller 10–15 µH inductor can be evaluated separately; it would need saturation margin above the 1.95 A maximum current limit. TI's generic 22 µH recommendation covers wider-input applications and should not be copied without checking ripple at 5 V.

The four 22 µF output capacitors are retained until effective MLCC capacitance, compensation and load-step response are checked. For illustration, TI equation 12 gives about 9.1 µF effective for a 0.3 A step, 5% excursion and 400 kHz; that simplified screen does not qualify USB-hub startup or justify deleting capacitors. Smaller passives offer potential area/cost savings, but none are included in the quoted $10.09.

## Confidence and remaining work

Datasheet-based pin mapping and arithmetic are high-confidence for the documents identified below; the total load is a conservative engineering budget, not a measured maximum. No simulator is installed (`ngspice`, `ltspice`, `xyce` absent), so no SPICE validation is claimed. Native ERC, complete net checks, footprint/pin coverage and placement DRC/parity pass. Automated schematic/PCB/EMC reports were rerun and triaged; they flag unfinished routing/planes and contain hierarchy-detection limitations, so they are not EMC qualification. Check startup at −15°C, all-port USB traffic with sensor heater pulses, load steps, ripple, brownout, temperature and conducted noise before releasing it.

Sources: [TI LMR51610](https://www.ti.com/lit/ds/symlink/lmr51610.pdf), [Microchip USB2517](https://ww1.microchip.com/downloads/en/DeviceDoc/00001598C.pdf), [ST STM32G0B1](https://www.st.com/resource/en/datasheet/stm32g0b1me.pdf), [Sensirion SHT4x](https://sensirion.com/resource/datasheet/sht4x). Local document hashes are in [datasheet-review-manifest.json](datasheet-review-manifest.json).
