# Color Grimoire 0.1.0

First public release of the Krita docker for OC color sheets, layer recipes and environment palettes.

## Highlights

- One sheet per OC: summary, history, personality, relationships and tags.
- Eight palette zones with per-color name, HEX, role, body part, purpose, opacity and note.
- Left click = foreground, right click = background; optional swatch alpha.
- Editable layer recipe with blend modes and opacities; **Create layers in Krita** builds the group in the active document.
- Environment tab with key light, shadow tint, bounce, mood and palette.
- Private zone hidden by default.
- JSON import/export and `.gpl` palette export.
- Spanish and English UI.
- Krita 5.3 (Qt5) and Krita 6.0 (Qt6) support.

## Install

1. Download `grimorio_color-0.1.0.zip`.
2. Krita → **Tools → Scripts → Import Python Plugins** → select the ZIP.
3. Restart Krita.
4. **Settings → Configure Krita → Python Plugin Manager** → enable **Color Grimoire**.
5. Restart Krita.
6. **Settings → Dockers → Color Grimoire**.

Linux users can also run `bash install.sh` from the repository.

## Compatibility

Tested on Linux with Krita 5.3.4.1 (Qt5) and Krita 6.0.4.1 (Qt6). Windows and macOS are untested; the plugin is pure Python and uses the same Qt compatibility layer.

## Privacy

No network, no accounts, no telemetry. Everything lives in a local JSON file. The private zone is hidden in the UI, not encrypted.

## Known limitations

- **Create layers** creates blank layers; it does not paint.
- `.gpl` export, not native `.kpl`.
- No OC × environment scene mode.
- Python Plugin Manager errors are the best bug report: include the Krita version and the error text.

## License

GPL-3.0-or-later.
