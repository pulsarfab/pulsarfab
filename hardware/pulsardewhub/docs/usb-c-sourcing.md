# Stocked USB-C replacement — 2026-10-03

PulsarPower J40 and PulsarDew J1 use **HRO TYPE-C-31-M-12, C165948**.
This is electrically compatible with the existing USB 2.0 circuit, but **not a
mechanical drop-in for GCT USB4105**. Both native boards and schematic sourcing
properties now select `pulsarfab:USB_C_HRO_TYPE-C-31-M-12`.

## Evidence and electrical mapping

[Manufacturer drawing via LCSC](https://datasheet.lcsc.com/datasheet/pdf/9e56b777c022540fcce7c7f67825f55e.pdf?productCode=C165948)
is dated 2020-12-08. Its pin table confirms A6/B6 = D+, A7/B7 = D−,
A5 = CC1, B5 = CC2, A8/B8 = unused SBU, A4/A9/B4/B9 = VBUS,
and A1/A12/B1/B12 = ground. Each CC retains a separate 5.1 kΩ pulldown.
Both cable orientations and all original nets remain unchanged. Shield anchors
remain on ground. This is USB2, with no SuperSpeed contacts.

The drawing specifies −30 to +80°C and 10,000 mating cycles. Signal tails are
surface mount; **four plated through-hole shell anchors** provide retention.
The connector's 5 A/20 V rating does not increase either product's USB power budget.

## Land pattern and placement

The project footprint derives from KiCad 10's named HRO TYPE-C-31-M-12 footprint,
not its GCT footprint. Retained geometry includes 8.64 mm shell-anchor span,
4.18 mm row separation, 5.78 mm locator spacing, 0.65 mm locator holes for
0.50 mm plastic posts, and the established KiCad signal lands. The manufacturer's
recommended anchor span is 8.65 mm (0.01 mm difference). The recommended front
anchor slot is 0.6 × 1.4 mm; the project enlarges KiCad's 0.6 × 1.2 mm slots to
that size and increases their copper pads to 1.0 × 1.8 mm. Rear slots remain
0.6 × 1.7 mm. All four slots are plated.

The retained KiCad signal lands are 1.45 mm long, with outer ground/VBUS centers
0.05 mm outward from the drawing's recommended lands. This is an established
alternative solder land, not an exact reproduction of the newer recommended
pattern. Its signal identities and nominal tail overlap were checked against
the drawing; first-article fit and solder inspection remain required before
production release. No connector-specific DRC waiver was added.

The drawing's PCB edge is 5.79 mm forward of the locator centers. With locator
Y = −2.60 mm, PCB edge Y = +3.19 mm locally. Both 180° connectors are placed at
board Y = 53.19 mm against the Y = 50 mm edge. Silkscreen stops inside the PCB;
the mating mouth protrudes approximately 0.46 mm. Existing board outlines and
all other component placements are preserved.

## Purchasing

[JLCPCB C165948](https://jlcpcb.com/partdetail/C165948) showed 424,757 in stock and
412,863 available to order. Price: $0.1857 at 1+, $0.1467 at 50+.
44 pieces cover 20 of each board plus 10% spares. **50 cost $7.34**, versus
$8.18 for 44; the extra six pieces lower the total. The former 44-piece GCT
preorder was $40.73, so this saves $33.39 and removes USB-C lead-time uncertainty.
The existing 22 owned C165948 are protected for NotchDeck and not allocated here.
No purchase has been submitted.

## Checks and limits

Both schematics pass strict exact-net/pad coverage and zero-error/warning ERC.
Both boards pass placement DRC and schematic parity, including elimination of
the four former GCT locator-hole clearance violations on each board. PulsarPower
still has 499 unconnected items and PulsarDew 130; neither board is routed or
ready for fabrication. This is connector qualification, not a repeated whole-board
thermal, EMC or protection review.
