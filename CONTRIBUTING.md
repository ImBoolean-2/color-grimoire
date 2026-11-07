# Contributing

Thanks for helping Color Grimoire. The most useful contribution right now is a **translation**.

## Translate the plugin

1. Open `grimorio_color/translations/translation-template.json`.
2. Copy it to `grimorio_color/translations/<code>.json` (for example `fr.json`, `de.json`, `pt_BR.json`).
3. Set:
   - `"code"` to the language code used by Krita/Qt (for example `fr`).
   - `"name"` to the name shown in the language menu (for example `Français`).
4. Translate the **values** in `"strings"`. The keys are the Spanish source strings; do not rename them.
5. Leave a value empty if you are not sure: the plugin falls back to Spanish.
6. Validate the JSON and open a pull request with the new file.

The plugin loads translations from `grimorio_color/translations/` (bundled) and from the user's `translations/` folder next to the JSON. User files override bundled files, so a translator can test without rebuilding the plugin.

See [docs/TRANSLATIONS.md](docs/TRANSLATIONS.md) for the loader details.

### Test a translation locally

Copy your `<code>.json` to the user folder:

- Linux Flatpak: `~/.var/app/org.kde.krita/data/krita/grimorio-color/translations/`
- Linux native: `~/.local/share/krita/grimorio-color/translations/`
- Windows: `%APPDATA%/krita/grimorio-color/translations/`
- macOS: `~/Library/Application Support/krita/grimorio-color/translations/`

Then use `⋯ → Language → Reload translations` (or restart Krita). If the language does not appear, check the JSON `code`, `name` and the folder.

## Code contributions

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for the environment, test matrix and code rules.

- The plugin is pure Python and supports Krita 5.3 (PyQt5) and Krita 6.0 (PyQt6). Keep the Qt compatibility layer in `qt_compat.py`.
- Run the tests before opening a pull request:

```bash
python3 -m unittest test_model.py test_i18n.py
flatpak run --command=python3 org.kde.krita test_bridge.py
GRIMORIO_LANG=en python3 test_ui_offscreen.py   # or the Flatpak Python for PyQt5
```

- Keep user-facing strings in Spanish in the source; add the English value to `i18n.py`. Custom languages live in JSON, not in the source.
- Do not add network calls, accounts or telemetry. The plugin is local by design.

## License

By contributing you agree that your contribution is licensed under GPL-3.0-or-later, the same license as the project.
