# Troubleshooting

## The plugin is not in the Python Plugin Manager

Krita discovers plugins with `pykrita/*desktop` at the **root**; it does not scan subfolders. These must exist:

```text
~/.var/app/org.kde.krita/data/krita/pykrita/grimorio_color.desktop
~/.var/app/org.kde.krita/data/krita/pykrita/grimorio_color/__init__.py
```

- If the `.desktop` is inside the folder, move it to the `pykrita` root.
- Restart Krita after copying/importing.
- Flatpak: `~/.var/app/org.kde.krita/data/krita/pykrita/`.
- Native: `~/.local/share/krita/pykrita/`.
- Windows: `%APPDATA%/krita/pykrita/`.
- macOS: `~/Library/Application Support/krita/pykrita/`.

## It appears as Broken

Select it in the Plugin Manager and read the error. Common causes:

- Mixing Krita 5.3 and 6.0 files (PyQt5 vs PyQt6). The plugin has a compatibility layer, but do not mix Krita versions.
- Missing `__init__.py` or the folder is not next to the `.desktop`.
- A partial `i18n.py`/`ui.py`: reinstall the ZIP or `bash install.sh`.

## Clicking a color does nothing

There is no active document/view. Open an image and try again; the footer status says it.

## “Create layers in Krita” does nothing

It needs an active document. Create an image and press again. The stack is created with `LINE` on top and `FX` at the bottom; layers are **blank** (it does not paint).

## “Create lighting rig” does nothing

It needs an active document and a saved environment. Save the environment first; the rig uses saved values, not the unsaved form. It creates a `Lighting — <scene>` group with SHADOW/AO/LIGHT/GLOW/BOUNCE fill layers and `inheritAlpha`.

## Updating from 0.4.1: backups and restore

Updating from 0.4.1 is automatic. The first load of a `version: 1` JSON writes `grimorio.json.v1.bak` next to it and then converts the file to v2.

- **No `.v1.bak` appears**: check the right data folder (Flatpak and native Linux use different paths), and make sure the JSON really was v1 and not already migrated. If the standard backup already existed and your file had changed since, the new copy is `grimorio.json.v1-<date>.bak`.
- **Only one backup and then no more**: that is expected; migration runs once. Repeated loads do not duplicate it.
- **Restore**: close Krita, replace `grimorio.json` with the `.v1.bak` copy (rename it), keep the `images/` folder, reopen Krita. The next load migrates it again.
- **Downgrade is not supported**: 0.5/0.4 cannot read v2. The backup is the safety net, not a way to keep two versions in parallel.
- **Web app**: v1 `localStorage` is converted to v2 and a one-time `grimorio-color:v1-backup` key is kept. That backup belongs to that browser only. To move data to another browser or machine, use **Export JSON** in the old one and **Import JSON** in the new one.
- **Loomis Head Guide**: update both plugins. Save in Loomis first, then in Grimoire; do not save in both at the same time. Grimoire copies the opaque `head` block and never interprets it.
- **Colors “missing” after deleting a zone**: they are not deleted. Deleting a zone keeps `palettes[key]` as a hidden extra: it still appears in `.gpl` exports and color counts, but not in the zone editor.
- **Library tab empty**: expected; `library` starts empty and fills only when you use **Create from zone**.

The full step-by-step guide is [`MIGRATION-0.4.1-TO-0.7.0.md`](../MIGRATION-0.4.1-TO-0.7.0.md).

## The OC photo or zone example does not appear

- The file must exist in `images/` next to the JSON. If you moved the JSON without the folder, paths break and the placeholder shows.
- Select the photo/example again; the plugin copies the file and updates the path.
- The web companion preserves the paths but does not display the images; that is expected.

## A translation does not appear in the menu

- Check `code`/`name` and that the file is valid JSON.
- It must be in the user `translations/` folder or `grimorio_color/translations/` (bundled).
- Use `⋯ → Language → Reload translations` or restart Krita.
- If the `code` is `es`/`en`/`xx`, it is ignored; use another.
- Missing keys fall back to Spanish; that is not an error.

## The web button opens nothing

- The default is `~/proyectos/grimorio-color/index.html`; if it does not exist, the plugin asks for a path.
- `⋯ → Set web Grimoire…` accepts a local path, `http(s)://` or `file://`.
- If the file does not exist, it shows “The file was not found.”
- The web app uses its own `localStorage`; it does not auto-sync. Use Export/Import JSON.

## Krita 5.3 real test is stuck

`kritarunner` shares the resource database with Krita; if Krita is open, it can wait on a “database is locked” lock. Close Krita and rerun `test_krita_real.py`. UI/model/bridge tests do not need Krita closed.

## Windows / macOS

The ZIP is the install path; `install.sh` is Linux-only. Windows data is in `%APPDATA%/krita/grimorio-color/`; macOS in `~/Library/Application Support/krita/grimorio-color/`. They are not validated on real machines; if it fails, include the Krita version and the Plugin Manager error.

## Android / tablet

Krita Android does not support Python plugins; the panel cannot load. The web companion is a browser app, but it does not integrate with Krita and does not replace the plugin.

## The web app does not save

- Some browsers block `localStorage` on `file://`; serve the folder with `python3 -m http.server 8765`.
- Check you are not in a private window.
- The real backup is **Export JSON**; if site data is cleared, the JSON is the recovery.
