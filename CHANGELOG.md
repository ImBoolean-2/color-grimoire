# Changelog

## 0.7.0 — 2026-11-10

### Added

- **Zone editor** (web + docker): add, rename label/element, reorder, mark private and delete zones. Deleting a zone keeps its palette as an opaque extra, so colors survive and remain in `.gpl`/counts; the key stays stable.
- **Palette library**: `library` stores reusable `{id, name, swatches}` palettes. Create from a project zone, import into any zone by copy with new ids, rename and delete. Available as a fifth tab in the web app and the docker.
- **Fresh migration backup**: if `grimorio.json.v1.bak` already exists but the v1 file changed, a `grimorio.json.v1-<timestamp>.bak` copy is created before migrating. Repeated loads do not duplicate it.

### Changed

- **Upgrade from 0.4.1**: v1 `grimorio.json` files migrate automatically to v2 with a `.v1.bak` (or a timestamped `.v1-<date>.bak` when the standard backup is stale); the web localStorage v1 is backed up as `grimorio-color:v1-backup`. Loomis Head Guide 0.6.1 writes only `character.head` and preserves the v2 fields; both plugins stay independent.
- **UX pass**: neutral “Proyecto/Project” copy across the web app and docker, compact responsive zone rows, sticky dialog actions, accessible zone-field labels and specific save/import/rename/delete status feedback.
- `docs/MODELO-DATOS.md` documents the library schema, zone editor/key stability, delete-keeps-palette and the timestamped v1 backup.
- `docs/WEB.md` documents the zone editor and Biblioteca tab.

### Tested

- 44 model tests, 4 i18n tests, 140 web checks, UI offscreen PyQt5 with ZoneDialog and library controls.

## 0.6.0 — 2026-11-10

### Added

- **Project kinds**: `kind` is `character` (default), `scene` or `prop`. Each kind gets default zones and a starter recipe (character 8 zones/LINE…FX, scene 8 zones/sky…light + SKY…FX, prop 5 zones/LINE…FX). Changing kind keeps the old palettes as hidden opaque zones.
- **Configurable zones**: `zones` stores `{key, label, defaultBody, private}` per project; scene and prop presets included. Custom zones are rendered by the web app and the docker.
- **Multiple environments**: `environments` + `activeEnvironmentId` with add, duplicate, delete and switch; `environment` remains a mirror of the active one for v1 readers. Environment swatches edit the active environment and sync the mirror.
- **Schema v2 migration**: loading a `version: 1` file creates `grimorio.json.v1.bak` once and normalizes to v2 (kind `character`, 8 zones, one environment). The web app stores a one-time `grimorio-color:v1-backup` in localStorage.
- **Adaptive sheet/print**: character shows history/personality/relationships; scene and prop show summary + active environment. Key-color chips use the first zones of the project.
- **Dynamic body-part label**: “Parte del cuerpo” for characters, “Elemento” for scenes/props; the JSON key remains `bodyPart`.
- **Loomis contract**: the opaque `head` block is still deep-copied and survives v2 migration, save/load and export/import; legacy light keys and unknown keys are preserved.

### Changed

- State `version` is now `2`; `library` is reserved as an empty list for 0.7.
- `docs/MODELO-DATOS.md` documents the v2 schema, zone presets, environments, migration/backup and the Loomis contract.
- `docs/WEB.md` documents kinds, multiple environments, adaptive sheets and the localStorage backup.

### Tested

- 37 model tests, 4 i18n tests, 106 web checks, UI offscreen PyQt5 with kind/zone/environment controls, and the v1→v2 + Loomis `head` contract.

## 0.5.0 — 2026-11-10

### Added

- **Scene-friendly palettes**: palette keys outside the eight character zones (`sky`, `foliage`, `rocks`…) are preserved as an opaque deep copy in the plugin and the web app; they survive save/load and are included in `.gpl` exports and color counts.
- **Environment palette in `.gpl`**: the active environment palette is appended with the `Ambiente · <name>` label and counted in the sheet/sidebar totals.
- **Recipe presets**: Personaje / Entorno / Prop presets (model, web and docker) with confirmation; the existing character recipe remains the default.
- **Environment presets**: Amanecer / Día / Atardecer / Noche / Niebla fill the environment fields; the docker previews the values without saving until “Guardar ambiente”.
- **Scene vocabulary**: the swatch field label is now “Elemento / parte del cuerpo” and the datalist includes sky, water, vegetation, terrain, rock, wood, metal, glass, cloth and FX (the JSON key remains `bodyPart`).
- **Web search**: filter by swatch name, HEX, `bodyPart`, zone label and environment fields.
- **Print sheet**: environment summary and extra palette zones.
- **Loomis 0.6.1 compatibility**: the plugin preserves the opaque `head` block written by Loomis Head Guide 0.6.1 (`normalize_character` deep-copies it; new OCs include `"head": {}`), and the web sheet shows `headSex`, `eyeSocketDepth`, `browRidge` and `cheekFullness` with the 0.6.0 fields as fallback. No import of Loomis code; both plugins remain independent.

### Changed

- `docs/MODELO-DATOS.md` documents the opaque palette keys, the environment `.gpl` export and the Loomis 0.6.1 keys/legacy light keys.
- `docs/WEB.md` documents recipe/environment presets, the extended search and the environment `.gpl` export.

### Tested

- 27 model tests (19 previous + 8 scene/compatibility), 4 i18n tests, 61 web checks, UI offscreen PyQt5 with recipe/environment presets, and the Loomis `head` contract.

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
