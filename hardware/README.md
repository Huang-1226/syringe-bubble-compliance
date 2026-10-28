# 3D-printed parts

These are the STL files for the syringe hydraulic bubble-compliance setup used in the report. They are supplied for reproduction of the fixture; they are not pressure-rated components.

## Files

| File | Part | Typical quantity | Notes |
|---|---|---:|---|
| `stl/flange_clamp.stl` | Syringe flange clamp / holder | 2 | One for the input syringe and one for the output syringe. This is the measured variant; check the fit on your syringe before printing a full set. |
| `stl/slider_coupler.stl` | Slider-to-push-rod coupler | 1 | Connects the lead-screw stage to the input syringe push rod. |
| `stl/plunger_clip_5ml.stl` | Push-rod clip / stop for a 5 mL syringe | 1 | Use with the matching syringe size. |
| `stl/plunger_clip_10ml.stl` | Push-rod clip / stop for a 10 mL syringe | 1 | Input syringe in the reported experiments. |
| `stl/plunger_clip_20ml.stl` | Push-rod clip / stop for a 20 mL syringe | 1 | Output syringe in the reported experiments. |
| `stl/bar_hook.stl` | Load-bar / weight-string hook | 1–2 | Guides the string that transfers the water load to the output rod. |

All dimensions are in millimetres. The STL files contain the final printed geometry only; the parametric CAD sources are not included in this release.

## Suggested print settings

- Material: PLA or PETG. PETG is preferred for parts that clamp onto syringes for long periods.
- Layer height: 0.2 mm.
- Walls: 3 perimeters.
- Infill: 20–30% (gyroid or grid).
- Supports: only where the overhang requires them; remove them carefully from clamp slots.
- Scale: 100%; do not use "fit to bed".
- Orientation: print the clamp bodies with the flat back on the bed; print the hook with the shank vertical if your slicer allows it.

## Assembly notes

1. Check the syringe fit before printing all clamps. Syringe barrels differ slightly between manufacturers.
2. Mount the input syringe on the lead-screw stage with `flange_clamp.stl` and connect the push rod with `slider_coupler.stl`.
3. Use the matching `plunger_clip_*.stl` on the push rod. The clip is a mechanical stop for the rod clamp, not a pressure seal.
4. Mount the output syringe with the second flange clamp; attach the extension spring and the load string to the output rod. Use `bar_hook.stl` to guide the string to the water load.
5. Keep the syringe axes aligned. Side loads on the push rod increase friction and bias the measured stiffness.
6. Leak-test with air or water before applying the water weights. These parts are not designed for high pressure.

Figure 2 of the report shows the assembled hydraulic circuit and displacement measurement. Figure 1 shows the load path and the pulley.

GitHub does not render STL files in the browser; download the files and open them in your slicer. A quick visual check in the slicer is recommended before printing.

## License

The 3D-print files are licensed under the Creative Commons Attribution 4.0 International License (CC BY 4.0), the same terms as the report, figures, and measured data. See `../LICENSE-CC-BY-4.0.txt`.
