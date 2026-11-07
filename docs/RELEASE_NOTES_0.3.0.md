# Color Grimoire 0.3.0

The personalization release.

## Highlights

- **Optional OC photo**: add a reference photo in the sheet hero. It is copied to the local `images/` folder and shown next to the name, tags and stats. Change, remove or open it from the same card.
- **Optional zone example**: the `▣` button in each palette zone adds a reference crop (hair base/shadow, painted skin, etc.). The zone shows the thumbnail with a **Remove example** button.
- **Color ramps**: each zone with enough colors gets an automatic shadow → base → light gradient, so the color relationship is visible at a glance.
- **Custom translations**: the language menu lists Spanish, English and every `*.json` file in `translations/`. The menu creates a template, opens the folder and reloads translations. Missing keys fall back to Spanish.
- **UI refresh**: Ficha hero with the OC photo, gradient background, zone ramps, example thumbnails and a cleaner example button.

## Install

1. Download `grimorio_color-0.3.0.zip`.
2. Krita → **Tools → Scripts → Import Python Plugins** → select the ZIP.
3. Restart Krita.
4. **Settings → Configure Krita → Python Plugin Manager** → enable **Color Grimoire**.
5. Restart Krita.
6. **Settings → Dockers → Color Grimoire**.

Linux users can also run `bash install.sh` from the repository.

## Data and backup

The JSON, the `images/` folder and the `translations/` folder live together in the plugin data directory. Back up the JSON **and** the `images/` folder; the JSON alone does not carry the photos or zone examples. Use `⋯ → Open data folder` to reach them.

## Custom translations

1. `⋯ → Language → Create translation template`.
2. Copy `translation-template.json` to `<code>.json` (for example `fr.json`).
3. Set `code` and `name`; translate the values in `strings`. Keys are the Spanish source strings; empty or missing values fall back to Spanish.
4. `⋯ → Language → Reload translations` or restart Krita.

## Compatibility

- **Krita 6.0.4.1 (Qt6)**: full real test for the layer stack, all blend IDs and the lighting rig; the 0.3.0 UI/entry is tested with the real Krita API.
- **Krita 5.3.4.1 (Qt5)**: model, bridge, translation and UI tests pass; the full real re-run is pending while Krita is open and locks the resource database.

Windows and macOS are untested. The plugin is pure Python and uses the same Qt compatibility layer.

## Known limitations

- The OC photo and zone examples are local files in `images/`; the JSON alone does not carry them.
- Custom translations fall back to Spanish for missing or empty values.
- **Create lighting rig** creates fill layers, not a painted scene.
- **Color Guard** uses a fixed ΔE threshold of 3; it is a guide, not an absolute check.
- **Create layers** creates blank layers; it does not paint.
- `.gpl` export, not native `.kpl`.
- The private zone is hidden, not encrypted.

## Privacy

No network, no accounts, no telemetry. The photos and translations are local files.

## License

GPL-3.0-or-later.
