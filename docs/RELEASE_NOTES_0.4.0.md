# Color Grimoire 0.4.0

The web companion release.

## Highlights

- **Web button**: the header now has a `web` button (and `⋯ → Open web Grimoire`) that opens the web app in the default browser.
- **Configurable target**: `⋯ → Set web Grimoire…` accepts a local `index.html`, an `http(s)://` URL or a `file://` URL. The default is `~/proyectos/grimorio-color/index.html` when it exists; otherwise the plugin asks for a path.
- **Clear data bridge**: the web app has its own `localStorage`; the plugin JSON does not auto-sync. Use **Export JSON** in the plugin and **Import JSON** in the web app (and the reverse). The web app is not bundled in the plugin ZIP.
- **Image fields survive the round-trip**: the web app preserves `referenceImage` and `zoneExamples` in the JSON, although it does not display the image files.

## Install

1. Download `grimorio_color-0.4.0.zip`.
2. Krita → **Tools → Scripts → Import Python Plugins** → select the ZIP.
3. Restart Krita.
4. **Settings → Configure Krita → Python Plugin Manager** → enable **Color Grimoire**.
5. Restart Krita.
6. **Settings → Dockers → Color Grimoire**.

Linux users can also run `bash install.sh` from the repository.

## Compatibility

- **Krita 6.0.4.1 (Qt6)**: full real test for the layer stack, all blend IDs and the lighting rig; the 0.4.0 UI/entry is tested with the real Krita API.
- **Krita 5.3.4.1 (Qt5)**: model, bridge, translation and UI tests pass; the full real re-run is pending while Krita is open and locks the resource database.

Windows and macOS are untested; the ZIP is the cross-platform install path. The web button accepts a local path or a hosted URL.

## Known limitations

- The web app is not bundled; the button opens whatever path/URL you configure.
- The plugin JSON and the web app's `localStorage` are separate; use export/import.
- The OC photo and zone examples are local files in `images/`; the JSON alone does not carry them.
- Custom translations fall back to Spanish for missing or empty values.
- **Create lighting rig** creates fill layers, not a painted scene.
- **Color Guard** uses a fixed ΔE threshold of 3.
- **Create layers** creates blank layers; it does not paint.
- `.gpl` export, not native `.kpl`.
- The private zone is hidden, not encrypted.

## Privacy

No network, no accounts, no telemetry. The web app is a local file or a URL you choose; the plugin only hands the URL to your browser.

## License

GPL-3.0-or-later.
