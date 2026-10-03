# Library Attributions

Custom symbols, footprints, and 3D models for PulsarFab projects.

## Sources

- Custom symbols and footprints created for this project
- 3D models from manufacturer sources (attributed per-model)

## PulsarDew Hub connector derivatives

`AMASS_XT60PW-M_Edge`, `BarrelJack_GCT_DCJ200_Edge` and
`USB_A_GCT_USB1046_Edge` derive from the corresponding AMASS XT60PW-M,
GCT DCJ200 and GCT USB1046 footprints in the KiCad 10 footprint library.
Copper pads, drill geometry and fabrication outlines are unchanged; front
silkscreen is trimmed where the mating body extends past this board's edge.
The original footprint description and manufacturer drawing links are retained.

Source: [KiCad footprint library](https://gitlab.com/kicad/libraries/kicad-footprints).
The upstream library is licensed under
[CC BY-SA 4.0 with the KiCad libraries exception](https://www.kicad.org/libraries/license/).
These footprint derivatives retain that license and exception.

The other PulsarDew Hub custom footprints were drawn from the manufacturer
documents listed in `pulsardewhub/docs/datasheet-review-manifest.json`.
They remain subject to physical pad and assembly-process review before fabrication.

## TPS25982 RGE0024M land pattern

`TI_RGE0024M_VQFN24_2EP_4x4mm` is drawn from TI drawing 4223975/B,
RGE0024M, in the TPS25982 Rev. D datasheet (land-pattern and stencil pages).
Pad 25 is input power and pad 26 is ground; they must remain separate. The
footprint has the TI example copper/paste dimensions without embedded vias.
Select plated/filled/capped thermal vias during routing and assembly review.
