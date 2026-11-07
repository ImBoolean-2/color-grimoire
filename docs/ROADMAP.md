# Roadmap

## Done

- **0.1.0**: web companion (OC sheets, palettes, recipes, environment, `.gpl`, JSON, print) and first PyKrita prototype; pre-release.
- **0.2.0**: layer order fix (LINE on top), scene preview, lighting rig with fill layers, Color Guard.
- **0.3.0**: optional OC photo, zone example image, shadow→base→light ramps, user translations, full language rebuild, hero/gradient UI.
- **0.4.0**: configurable web companion button (path/URL), no auto-sync.
- **0.4.1**: clean public repository, public release, bundled translations + `CONTRIBUTING`, template/README for contributors.

## Next candidates

1. **Recipe Capture**: read the current document layer stack and save it as the OC recipe. Natural complement to “Create layers”.
2. **Document Embed**: store the OC sheet/palette/recipe in the `.kra` annotation; offer to load it on open. `Document.setAnnotation` is available.
3. **Looks / Variants**: multiple outfits, ages or arcs per OC with palette, recipe and environment overrides.
4. **Character Sheet Export**: PNG/PDF with sheet, palette, recipe and environment; share mode without the private zone.
5. **Palette Audit**: values, contrast, duplicates, colorblind simulation, shadow/light consistency and cast comparison.
6. **Body Map**: silhouette with colored zones; click to filter the palette.
7. **Native `.kpl`**: ZIP + XML in addition to `.gpl`; parity with Krita/PaletteGenerator.
8. **Painted scene**: besides fill layers, an option to paint masks/base tones; decide with feedback.
9. **Windows/macOS validation**: test the ZIP on both platforms and document it.
10. **Full 5.3 real run**: run `test_krita_real.py` with Krita closed and update the matrix.
11. **Public web companion**: if the community wants it, host the web app (e.g. GitHub Pages) and point the button to that URL. Requires sanitizing the seed and deciding the UI language.

## Suggested priority

- First **Recipe Capture + Document Embed**: real continuity, low cost and close to the original problem.
- Then **Looks/Variants + Character Sheet Export**: OC management and commissions.
- Then **Palette Audit + Body Map**: visual quality.
- Do **not** compete on generic palette generation, moodboards or AI/cloud: other tools already own that, and it is not the moat.

## Not planned (for now)

- Accounts, cloud, telemetry or automatic sync.
- A PureRef/BeeRef-style reference board.
- AI palette generation.
- Android/tablet: Krita Android does not support PyKrita.
