# Architecture

Color Grimoire is a **PyKrita plugin** for desktop Krita. The repository also contains an optional local web companion, but the public release is the plugin; the web app is not bundled.

## Components

```text
Krita 5.3 / 6.0
  └─ GrimorioDocker (__init__.py)
       └─ GrimorioPanel (ui.py)
            ├─ model.py        pure model: JSON, normalization, color, images, GPL
            ├─ i18n.py         Spanish source + English + JSON translations
            ├─ krita_bridge.py Krita API (lazy import)
            └─ qt_compat.py    PyQt5 / PyQt6

Data
  └─ <krita-data>/grimorio-color/
       ├─ grimorio.json
       ├─ images/           OC photos and zone examples
       └─ translations/     user languages (override bundled)

Web companion (optional, not bundled)
  └─ index.html + app.js + localStorage + JSON import/export
```

## Responsibilities

- **`model.py`**: no Krita or Qt imports. Normalizes state, atomic JSON save, image copy/validation, `.gpl` export, CIE76 ΔE, color ramps, `lighting_spec`, `nearest_swatch`.
- **`ui.py`**: panel, tabs, cards, dialogs, QSS, Color Guard, OC photo, zone examples, scene preview, language menu, full UI rebuild on language change.
- **`krita_bridge.py`**: imports `krita` only inside methods. Sets foreground/background, reads the current foreground color, creates the layer stack and the lighting rig with fill layers.
- **`qt_compat.py`**: PyQt6 (Krita 6) or PyQt5 (Krita 5.3); exposes compatible enums/classes, `exec_dialog`, `QSettings`, `QInputDialog`, `QPixmap`.
- **`i18n.py`**: Spanish source strings; `EN` built-in English; JSON files add languages. Loads bundled and user folders; user wins.
- **`__init__.py`**: registers the docker with `Application.addDockWidgetFactory`.

## Plugin data flow

1. `GrimorioPanel.__init__` loads `model.load_state()` and translations.
2. Each edit mutates `self.state` and calls `model.save_state()` (temp file + `os.replace`).
3. `refresh()` rebuilds tab content; state lives in memory and in JSON.
4. `QFileSystemWatcher` reloads if the JSON changes outside the plugin (when the file existed at startup).
5. `KritaBridge` touches the active document only when the user clicks a color or creates layers/lights.

## Compatibility

- **Krita 5.3.4.1 / Qt5 / PyQt5**: tested on Linux Flatpak.
- **Krita 6.0.4.1 / Qt6 / PyQt6**: tested with the official AppImage and `kritarunner` under headless KWin Wayland.
- **Android/tablet**: Krita Android does not support Python plugins; the plugin does not apply.
- **Windows/macOS**: pure Python and `%APPDATA%` / `Application Support` paths; the ZIP is the install path. Not validated on real machines yet.

## Decisions

- **JSON, no server**: portable, inspectable and offline. The trade-off is that the web companion and the plugin do not auto-sync; the bridge is JSON export/import. Images and translations are local folders; backups must include the JSON and `images/`.
- **Clean public repository**: the public repository starts with a single 0.4.1 commit; earlier prototype history is not included. It contains only the plugin, docs, tests, screenshots and translations; the personal web companion is not published.
- **No network, accounts or telemetry**: everything is local.
