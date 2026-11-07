# Color Grimoire 0.4.1

The community-translations release.

## Highlights

- **Community translations**: the plugin loads bundled translations from `grimorio_color/translations/*.json` and user translations from the `translations/` folder next to the JSON. User files override bundled files.
- **Contributor template**: `grimorio_color/translations/translation-template.json` plus `README.md`; copy it to `<code>.json`, set `code`/`name`, translate the values and open a pull request.
- **CONTRIBUTING.md**: translation workflow, local test paths, test commands and license.
- Everything from 0.4.0: web companion button, OC photos, zone examples, color ramps, scene preview, lighting rig, Color Guard, custom translations.
- **First public release**: repository and release are public; the ZIP includes the bundled translations folder.

## Install

1. Download `grimorio_color-0.4.1.zip`.
2. Krita → **Tools → Scripts → Import Python Plugins** → select the ZIP.
3. Restart Krita.
4. **Settings → Configure Krita → Python Plugin Manager** → enable **Color Grimoire**.
5. Restart Krita.
6. **Settings → Dockers → Color Grimoire**.

Linux users can also run `bash install.sh` from the repository.

## Translating

The template has every source string. The keys are Spanish; translate the values. Empty or missing values fall back to Spanish. Test locally by copying the file to the user `translations/` folder:

- Linux Flatpak: `~/.var/app/org.kde.krita/data/krita/grimorio-color/translations/`
- Linux native: `~/.local/share/krita/grimorio-color/translations/`
- Windows: `%APPDATA%/krita/grimorio-color/translations/`
- macOS: `~/Library/Application Support/krita/grimorio-color/translations/`

Then use `⋯ → Language → Reload translations`.

## Compatibility

- **Krita 6.0.4.1 (Qt6)**: full real test for the layer stack, all blend IDs and the lighting rig; the 0.4.1 UI/entry is tested with the real Krita API.
- **Krita 5.3.4.1 (Qt5)**: model, bridge, translation and UI tests pass; the full real re-run is pending while Krita is open and locks the resource database.

Windows and macOS are untested; the ZIP is the cross-platform install path.

## License and privacy

GPL-3.0-or-later. No network, no accounts, no telemetry. The plugin JSON, images and translations are local files.
