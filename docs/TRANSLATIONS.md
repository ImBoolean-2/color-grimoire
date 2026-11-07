# Translations

The plugin is not limited to Spanish/English: anyone can add a language with a JSON file. Source strings are Spanish; built-in English lives in `i18n.py`; JSON files add the rest.

## Where they live

- **Bundled**: `grimorio_color/translations/<code>.json`, shipped in the ZIP.
- **User**: `translations/<code>.json` next to the plugin JSON.
- **Priority**: the user folder loads after the bundled folder and overrides the same `code`.
- **Template**: `translations/translation-template.json`; ignored by the loader.

User paths:

- Linux Flatpak: `~/.var/app/org.kde.krita/data/krita/grimorio-color/translations/`
- Linux native: `~/.local/share/krita/grimorio-color/translations/`
- Windows: `%APPDATA%/krita/grimorio-color/translations/`
- macOS: `~/Library/Application Support/krita/grimorio-color/translations/`

## Format

```json
{
  "code": "fr",
  "name": "Français",
  "strings": {
    "Grimorio de Color": "Grimoire de Couleur",
    "Ficha": "Fiche",
    "Paletas": "Palettes"
  }
}
```

- `code`: short Qt/Krita language code (`fr`, `de`, `pt_BR`…).
- `name`: label in the language menu.
- `strings`: key = Spanish source string; value = translation. Do not rename keys.
- Empty values or missing keys fall back to Spanish, so partial translations are fine.

## Add a language

1. Copy `grimorio_color/translations/translation-template.json` to `<code>.json`.
2. Change `code`, `name`, and translate the values.
3. Test locally by copying the file to the user folder and using `⋯ → Language → Reload translations` (or restarting Krita).
4. Open a pull request with the file in `grimorio_color/translations/`. See `CONTRIBUTING.md`.
5. The next release ships it in the ZIP; no rebuild is needed for users.

## Loader behavior

- `GrimorioPanel.__init__` calls `i18n.ensure_translations_dir()` (creates the user template/README) and `i18n.load_translations(user_dir, extra_directories=[bundled_dir])`.
- `i18n.load_translations` clears and reads bundled first, user last; user wins.
- `i18n.tr(text)`:
  - `es` → source text.
  - `en` → `EN`.
  - other → `CUSTOM[code].get(text)`, or source text if missing.
- `available_languages()` feeds the `⋯ → Language` menu.
- `set_language(code)` stores the choice in `QSettings` and rebuilds the whole panel (`_rebuild_ui`) so the header, tabs and footer switch too.
- `reload_translations` re-reads bundled + user and rebuilds the menu/panel.

## Development

- Add a new string: write it in Spanish and wrap it with `tr("...")`; add the entry to `EN` in `i18n.py`.
- Template keys come from `EN`; after adding a string, regenerate the template with `i18n.write_template(...)`.
- `test_i18n.py` covers built-in, custom JSON, fallback, template/README and bundled/user override.

## Limits

- The web companion does not use this system; its UI is Spanish.
- Translations do not translate OC content (names, lore, notes): that is user data.
- An invalid `code` or broken JSON is ignored; the language does not appear.
