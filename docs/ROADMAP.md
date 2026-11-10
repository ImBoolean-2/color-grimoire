# Roadmap

## Done

- **0.1.0**: web companion (OC sheets, palettes, recipes, environment, `.gpl`, JSON, print) and first PyKrita prototype; pre-release.
- **0.2.0**: layer order fix (LINE on top), scene preview, lighting rig with fill layers, Color Guard.
- **0.3.0**: optional OC photo, zone example image, shadow→base→light ramps, user translations, full language rebuild, hero/gradient UI.
- **0.4.0**: configurable web companion button (path/URL), no auto-sync.
- **0.4.1**: clean public repository, public release, bundled translations + `CONTRIBUTING`, template/README for contributors.
- **0.5.0**: scene-friendly opaque palette keys, environment palette in `.gpl`, recipe/environment presets, scene vocabulary, web search, print sheet, Loomis 0.6.1 `head` compatibility.
- **0.6.0**: schema v2 with project kinds (`character`/`scene`/`prop`), configurable zones and presets, multiple environments with an `environment` mirror, adaptive sheet/print, automatic v1→v2 migration.
- **0.7.0**: zone editor (add/rename/reorder/private/delete keeping the palette), palette library with copy-on-import, timestamped v1 backups, neutral “Project” copy, UX/accessibility pass.

## Next candidates

1. **Recipe Capture**: read the current document layer stack and save it as the project recipe. Natural complement to “Create layers”.
2. **Document Embed**: store the sheet/palette/recipe in the `.kra` annotation; offer to load it on open. `Document.setAnnotation` is available.
3. **Looks / Variants**: multiple outfits, ages or arcs per project with palette, recipe and environment overrides; build on the library and zone editor instead of duplicating projects.
4. **Character Sheet Export**: PNG/PDF with sheet, palette, recipe and environment; share mode without private zones and with an optional palette library import.
5. **Palette Audit**: values, contrast, duplicates, colorblind simulation, shadow/light consistency and cast comparison.
6. **Body Map**: silhouette with colored zones; click to filter the palette.
7. **Library exchange**: export/import library palettes as their own small JSON file, so a palette can travel between machines without the whole project.
8. **Native `.kpl`**: ZIP + XML in addition to `.gpl`; parity with Krita/PaletteGenerator.
9. **Painted scene**: besides fill layers, an option to paint masks/base tones; decide with feedback.
10. **Windows/macOS validation**: test the ZIP on both platforms and document it.
11. **Full 5.3 real run**: run `test_krita_real.py` with Krita closed and update the matrix.
12. **Public web companion**: if the community wants it, host the web app (e.g. GitHub Pages) and point the button to that URL. Requires sanitizing the seed and deciding the UI language.

## Suggested priority

- First **Recipe Capture + Document Embed**: real continuity, low cost and close to the original problem.
- Then **Looks/Variants + Character Sheet Export**: project management and commissions.
- Then **Palette Audit + Body Map + Library exchange**: visual quality and reuse.
- Do **not** compete on generic palette generation, moodboards or AI/cloud: other tools already own that, and it is not the moat.

## Not planned (for now)

- Accounts, cloud, telemetry or automatic sync.
- A PureRef/BeeRef-style reference board.
- AI palette generation.
- Android/tablet: Krita Android does not support PyKrita.
