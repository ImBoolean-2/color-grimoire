# Color Grimoire 0.7.0

The zones, library and migration release.

Color Grimoire keeps the colors of your characters, scenes and props inside Krita: swatches with a purpose, layer recipes and environment lighting, all in one local JSON. 0.7.0 turns the fixed eight-zone palette into something you can shape, reuse and carry from 0.4.1 without losing a single color.

## Highlights

- **Project types**: `kind` is `character` (default), `scene` or `prop`. Each type starts with its own zones and layer recipe: 8 character zones, 8 scene zones (sky, foliage, terrain, water, architecture, props, FX, light) and 5 prop zones. Changing the type keeps the current palettes as hidden extra zones.
- **Zone editor** (web + docker): add a zone, rename its label or element, reorder it, mark it private and delete it. The zone key stays stable. Deleting a zone keeps its palette as an opaque extra, so the colors survive and remain in `.gpl` exports and color counts.
- **Palette library**: a new fifth tab stores reusable `{id, name, swatches}` palettes. Create one from any project zone, import it into another zone by copy with new ids, rename it or delete it. Palettes are copied, never linked.
- **Multiple environments**: `environments` + `activeEnvironmentId` hold as many lighting setups as you need; `environment` stays as a mirror of the active one for older readers. The scene preview, lighting rig, sheet and print all follow the active environment.
- **Adaptive sheet and print**: characters show history, personality and relationships; scenes and props show a summary and the active environment. The swatch field reads “Body part” for characters and “Element” for scenes/props, and the neutral copy says “Project”.
- **Automatic v1 → v2 migration**: an old `grimorio.json` is converted on first load. The plugin writes `grimorio.json.v1.bak` before touching it, or `grimorio.json.v1-<date>.bak` when the standard backup was already old and the v1 file had changed since. Repeated loads do not duplicate it.
- **Web backup**: the web app converts its v1 `localStorage` data to v2 and keeps a one-time copy under `grimorio-color:v1-backup`.

## Upgrading from 0.4.1

Nothing is deleted and you do not need to export or convert anything: the plugin makes its own backup. Close Krita, install the 0.7.0 ZIP with **Tools → Scripts → Import Python Plugins**, restart, open the docker and check one project.

Full step-by-step guide, in English and Spanish: [MIGRATION-0.4.1-TO-0.7.0.md](https://github.com/ImBoolean-2/color-grimoire/blob/main/MIGRATION-0.4.1-TO-0.7.0.md).

If you use **Loomis Head Guide**, update both plugins (Grimoire 0.7.0 and Loomis Head Guide 0.6.1). Save in Loomis first, then in Grimoire, and do not save in both at the same time. Grimoire copies the opaque `head` block untouched.

## Install

1. Download `grimorio_color-0.7.0.zip`.
2. In Krita: **Tools → Scripts → Import Python Plugins**, select the ZIP.
3. Restart Krita.
4. **Settings → Configure Krita → Python Plugin Manager**: enable **Color Grimoire**.
5. Restart Krita again.
6. **Settings → Dockers → Color Grimoire**.

Linux users can also run `bash install.sh` from the repository. The ZIP is the cross-platform path.

## Tested

- **44 model tests** and **4 i18n tests**: schema v2, zone presets and editor, library, environments, migration and backups, Loomis `head` contract, translations.
- **140 web checks**: kinds, zones, library, environments, GPL/private mode, JSON round-trip and the v1 backup.
- **UI offscreen** with PyQt5, including the zone dialog and library controls.
- **Krita 6.0.4.1** (Qt6): real plugin entry and the UI with the real Krita API.
- **Krita 5.3.4.1** (Qt5): model, bridge, translation and UI tests; the full real run is still pending while Krita is open and locks the resource database.

## Notes

- **Downgrades are not supported.** The `.v1.bak` file is the safety net; keep it until you have checked your projects.
- Saving in Loomis and Grimoire **at the same time** can overwrite the other plugin's changes; save one, then the other.
- The web app is still not bundled in the ZIP: it uses its own `localStorage`, and moving between browsers or machines goes through Export/Import JSON.
- The ZIP is pure Python: no network, no accounts, no telemetry.

**Full changelog**: [CHANGELOG.md](https://github.com/ImBoolean-2/color-grimoire/blob/main/CHANGELOG.md) · **License**: GPL-3.0-or-later.
