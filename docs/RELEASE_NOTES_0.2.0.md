# Color Grimoire 0.2.0

The drawing release: scene lighting and color continuity.

## Highlights

- **Scene preview**: the key skin, hair and eye colors tinted by the environment's key light, shadow and bounce. Click a chip to use it.
- **Create lighting rig**: a group of fill layers with SHADOW (Multiply), AO (Multiply), LIGHT (Add), GLOW (Add) and BOUNCE (Add), using the environment colors and the recipe opacities. The group inherits alpha to clip to the layers below.
- **Color Guard**: compares the current foreground color with the active OC's palette, shows the nearest swatch and ΔE, and offers **Snap** to correct the color.
- **Layer stack order fixed**: LINE is now on top and FX at the bottom. `setChildNodes` receives the list bottom-up, so the recipe is reversed before creating the group.

## Install

1. Download `grimorio_color-0.2.0.zip`.
2. Krita → **Tools → Scripts → Import Python Plugins** → select the ZIP.
3. Restart Krita.
4. **Settings → Configure Krita → Python Plugin Manager** → enable **Color Grimoire**.
5. Restart Krita.
6. **Settings → Dockers → Color Grimoire**.

Linux users can also run `bash install.sh` from the repository.

## Compatibility

- **Krita 6.0.4.1 (Qt6)**: full real test, including the layer stack, all blend IDs and the lighting rig.
- **Krita 5.3.4.1 (Qt5)**: model, bridge and UI tests pass; the full real re-run is pending while Krita is open and locks the resource database.

Windows and macOS are untested. The plugin is pure Python and uses the same Qt compatibility layer.

## Known limitations

- **Create lighting rig** creates fill layers, not a painted scene; use them as a color wash and paint masks on top.
- The **Scene preview** is a reference, not a color-managed simulation.
- **Color Guard** uses a fixed ΔE threshold of 3; it is a guide, not an absolute check.
- **Create layers** creates blank layers; it does not paint.
- `.gpl` export, not native `.kpl`.
- The private zone is hidden, not encrypted.

## Privacy

No network, no accounts, no telemetry. Everything lives in a local JSON file.

## License

GPL-3.0-or-later.
