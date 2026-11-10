# Development and testing

Current version: **0.7.0** (data schema **v2**).

## Tested environment

- Linux (Fedora KDE Plasma).
- Krita **5.3.4.1** Flatpak, Python 3.13 + PyQt5 5.15.7.
- Krita **6.0.4.1** AppImage, PyQt6 6.12 (local venv for UI tests).
- `kritarunner` for real Krita API tests without a window.
- The web companion is plain HTML/CSS/JS; tested with Firefox headless.

## Repository layout

```text
grimorio_color/          plugin source (runtime + tests)
docs/                    this documentation
screenshots/             README/demo screenshots
install.sh               Linux helper
grimorio_color.desktop   plugin descriptor
```

The public repository is the plugin. The personal web companion and earlier prototype history are not part of this repo.

## Tests

### Model and translations (system Python)

```bash
python3 -m unittest test_model.py test_i18n.py -v
```

Covers normalization, CRUD, GPL, JSON, images, color, lighting, schema v2, project kinds, zone presets and editor, palette library, multiple environments, v1→v2 migration and backups, the Loomis `head` contract, bundled/user translations and the template.

### Bridge and entry point with a fake Krita (Flatpak)

```bash
flatpak run --command=python3 org.kde.krita test_bridge.py
```

Covers colors, layer stack, lighting rig, `foreground_color`, factory and docker.

### UI offscreen

With PyQt5 (Krita 5.3 Flatpak):

```bash
GRIMORIO_LANG=es flatpak run --command=python3 org.kde.krita test_ui_offscreen.py
```

With PyQt6 (venv):

```bash
python3 -m venv .venv
.venv/bin/pip install PyQt6
GRIMORIO_LANG=en .venv/bin/python test_ui_offscreen.py
```

Covers tabs, private mode, recipe, environment, Color Guard, OC photo, zone example, web button, language switch and a custom translation. Screenshots go to `~/.cache/grimorio-shots/`.

### Real Krita 5.3

Close Krita first: `kritarunner` shares the resource database and can wait on a lock if Krita is open.

```bash
flatpak run --env=QT_QPA_PLATFORM=offscreen \
  --env=QT_QPA_PLATFORMTHEME= \
  --env=PYTHONPATH="$PWD" \
  --command=kritarunner org.kde.krita \
  --script test_krita_real -f main
```

Verifies the `FX..LINE` stack (bottom-up), lighting group, `inheritAlpha`, blend modes, opacities and colors.

### Real Krita 6.0

With the official 6.0.4.1 AppImage and headless KWin Wayland:

```bash
export APPDIR=/path/to/squashfs-root   # adjust to your extraction path
export PYTHONHOME="$APPDIR/usr"
export PYTHONPATH="$PWD:$APPDIR/usr/lib/python3.13:$APPDIR/usr/lib/python3.13/site-packages"
export LD_LIBRARY_PATH="$APPDIR/usr/lib:$APPDIR/usr/lib/x86_64-linux-gnu"
export QT_PLUGIN_PATH="$APPDIR/usr/plugins"
export XDG_RUNTIME_DIR=/tmp/opencode/xdg-runtime-grimorio
export WAYLAND_DISPLAY=wayland-grimorio
export QT_QPA_PLATFORM=wayland
export XDG_SESSION_TYPE=wayland
"$APPDIR/usr/bin/kritarunner" --script test_krita_real -f main
```

`test_plugin_real.py` builds the panel with the real Krita API.

### Web

```bash
python3 -m http.server 8765
```

Open `http://127.0.0.1:8765/test/smoke.html`; expected **140 PASS**. Release screenshots are committed under `screenshots/`; maintainers regenerate them with a local script (not part of the repository).

### Matrix

| What | Command | Expected |
|---|---|---|
| Model + i18n | `python3 -m unittest test_model.py test_i18n.py` | 44 + 4 OK |
| Bridge | `flatpak run --command=python3 ... test_bridge.py` | 6 OK |
| UI PyQt5 | `GRIMORIO_LANG=es flatpak run ... test_ui_offscreen.py` | UI OK |
| UI PyQt6 | `GRIMORIO_LANG=en .venv/bin/python test_ui_offscreen.py` | UI OK |
| Krita 5.3 real | `kritarunner` (Krita closed) | STACK / LIGHT_GROUP |
| Krita 6 real | AppImage + KWin | STACK / LIGHT_GROUP |
| Web | `test/smoke.html` | 140 PASS |

## Code rules

- `model.py` imports neither Krita nor Qt; `ui.py` does not import Krita; `krita_bridge.py` imports `krita` only inside methods. Keep that separation.
- Source strings are Spanish; English lives in `i18n.EN`; community languages are JSON.
- No network, accounts or telemetry.
- UI changes: `refresh()` rebuilds content; `set_language()` rebuilds the whole panel (`_rebuild_ui`).
- Data changes: normalize and save with `model.save_state` (atomic).
- Layer changes: `setChildNodes` is bottom-up; the recipe is displayed top-down.
- Image changes: `model.store_image` copies to `images/` and returns the relative path; remove the previous file when replacing.

## Adding a feature

1. Data: field + normalization + defaults + model tests.
2. Krita: method in `krita_bridge.py` + fake bridge test.
3. UI: widget, ES/EN strings, offscreen test and screenshot.
4. Web: `app.js`/`styles.css`, smoke test and `docs/WEB.md` (personal repo).
5. Update `CHANGELOG.md`, `README.md`, `Manual.html` and release notes.
6. Test Krita 5.3 and 6.0; if you cannot, say so in the release.

## License

GPL-3.0-or-later. By contributing you agree to the same license.
