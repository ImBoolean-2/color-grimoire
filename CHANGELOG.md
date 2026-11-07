# Changelog

## 0.4.1 — 2026-11-07

### Added

- **Community translations**: the plugin now loads `grimorio_color/translations/*.json` (bundled) and the user's `translations/` folder next to the JSON. User files override bundled files.
- `grimorio_color/translations/translation-template.json` and `README.md` for contributors.
- `CONTRIBUTING.md` with the translation workflow, local test paths and the test commands.

### Changed

- First public release: repository and release are public; the ZIP includes the bundled translations folder.

### Tested

- 15 model tests, 4 translation tests, 6 bridge tests.
- UI offscreen PyQt5/PyQt6 with the web button, photo, zone example and custom language.
- Krita 6.0.4.1 real plugin entry.
- Krita 5.3.4.1 model/bridge/UI; full real run pending while Krita is open.

## 0.4.0 — 2026-11-07

### Added

- **Web companion button**: a `web` button in the header and `⋯ → Open web Grimoire` open the web app in the default browser.
- **Configurable web target**: `⋯ → Set web Grimoire…` accepts a local `index.html` path or an `http(s)://`/`file://` URL. The default is `~/proyectos/grimorio-color/index.html` when it exists; otherwise the plugin asks for a path.
- **Clear data bridge**: the web app uses its own `localStorage`; the plugin JSON does not auto-sync. Use **Export JSON** in the plugin and **Import JSON** in the web app (and vice versa). The web app is not bundled in the plugin ZIP.

### Tested

- 15 model tests, 3 translation tests, 6 bridge tests.
- UI offscreen PyQt5 and PyQt6, including the web button with a simulated browser call.
- Krita 6.0.4.1 real plugin entry.
- Krita 5.3.4.1 model/bridge/UI; full real run still pending while Krita is open.

## 0.3.0 — 2026-11-07

### Added

- **Optional OC reference photo**: add, change or remove a photo from the OC sheet. The image is copied to the `images/` folder next to the JSON and shown in the Ficha hero.
- **Optional zone example image**: add a reference crop per palette zone (hair base/shadow, painted skin, etc.); it appears in the zone section. The header button is the small `▣` icon.
- **Color ramps**: every zone with enough colors gets an automatic shadow → base → light gradient, so the color relationship is visible at a glance.
- **Custom translations**: the language menu now lists `Español`, `English` and any JSON files in the `translations/` folder. The menu creates a template, opens the folder and reloads translations. Missing keys fall back to Spanish.
- **UI refresh**: Ficha hero with the OC photo, new gradient background, zone ramps, example thumbnails and a cleaner example button.
- The web app preserves `referenceImage` and `zoneExamples` in JSON round-trips.

### Changed

- `set_language` rebuilds the whole panel, so the header, footer and static labels change with the language, not only the content.
- The image files are local; back up the JSON **and** the `images/` folder. The JSON alone does not carry the images.

### Tested

- 15 model tests, 3 translation tests, 6 bridge tests.
- UI offscreen with PyQt5 (Spanish) and PyQt6 (English), including the photo, zone example and custom-language switch.
- Krita 6.0.4.1 (Qt6): full real test from 0.2.0 remains valid; the 0.3.0 UI/entry is tested with the real Krita API.
- Krita 5.3.4.1: model, bridge and UI pass; the full real run is still pending while Krita is open and locks the resource database.

## 0.2.0 — 2026-11-07

### Added

- **Scene preview** in the Environment tab: the key skin, hair and eye colors tinted by the scene's key light, shadow and bounce.
- **Create lighting rig**: a group of fill layers with SHADOW (Multiply), AO (Multiply), LIGHT (Add), GLOW (Add) and BOUNCE (Add), using the environment colors and the recipe opacities. The group inherits alpha to clip to the layers below.
- **Color Guard**: compares the current foreground color with the active OC's palette, shows the nearest swatch and ΔE, and offers a **Snap** button to correct the color. It can include or skip the private zone depending on the private mode.
- **Capture recipe** is planned for 0.3.0; this release focuses on the scene and continuity features.

### Fixed

- **Layer stack order**: `setChildNodes` receives the list bottom-up; the recipe is now reversed before creating the group, so LINE is on top and FX at the bottom (verified with Krita 6.0.4.1).

### Tested

- Krita 6.0.4.1 (Qt6): full real test with the layer stack, all blend IDs and the lighting rig.
- Krita 5.3.4.1 (Qt5): model, bridge and UI tests; the full real run is pending while Krita is open (resource database lock). The same API calls are covered by the 6.0 run.

## 0.1.0 — 2026-11-07

First public release.

### Added

- PyKrita docker with OC sheets, eight palette zones and per-color metadata: name, HEX, role, body part, purpose, opacity and note.
- Click to set the foreground color; right-click for the background; optional swatch alpha.
- Editable layer recipe with blend modes and opacities, plus a **Create layers in Krita** action that builds the group in the active document.
- Environment tab: scene, time, weather, mood, key light, shadow tint, bounce and environment palette.
- Private zone hidden by default with a **Show private** toggle.
- JSON import/export and `.gpl` palette export.
- Spanish/English UI with automatic language detection and a manual switch.
- Qt compatibility layer for Krita 5.3 (PyQt5) and Krita 6.0 (PyQt6).

### Tested

- Krita 5.3.4.1 (Qt5) on Linux.
- Krita 6.0.4.1 (Qt6) on Linux.
- Model, bridge, UI offscreen and real Krita API tests.

### Known limitations

- **Create layers** builds blank layers; it does not paint.
- Palette export is `.gpl`, not native `.kpl`.
- No scene mode (OC × environment).
- Windows and macOS are untested.
- The private zone is hidden, not encrypted.

## 0.0.1 — 2026-11-06

- Personal MVP: local web app with OC sheets, palettes, layer recipes, environment, `.gpl`/JSON export and print view.
- First PyKrita docker prototype.
