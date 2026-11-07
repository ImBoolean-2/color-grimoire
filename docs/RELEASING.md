# Releasing

## Current release

- **0.4.1** public: `https://github.com/ImBoolean-2/color-grimoire`
- Release: `https://github.com/ImBoolean-2/color-grimoire/releases/tag/v0.4.1`
- ZIP: `grimorio_color-0.4.1.zip` (includes `grimorio_color/translations/`).
- The public repository starts at 0.4.1; earlier prototype history is not included.

## Versioning

Semver `MAJOR.MINOR.PATCH`:

- **0.4.1**: bundled community translations; clean public repository.
- **0.4.0**: configurable web companion button.
- **0.3.0**: OC photos, zone examples, color ramps, user translations.
- **0.2.0**: scene preview, lighting rig, Color Guard, layer order fix.
- **0.1.0**: MVP; pre-release, do not use.

## Checklist

1. **Version**: `grimorio_color/__init__.py` → `__version__`.
2. **Docs**: `CHANGELOG.md`, `README.md`, `grimorio_color/Manual.html`, `docs/RELEASE_NOTES_<version>.md`, `docs/KRITA_ARTISTS_POST.md`.
3. **Source**: copy runtime/tests from the development source into `grimorio_color/`; do not hand-edit release copies.
4. **Translations**: if changed, copy `grimorio_color/translations/`; regenerate `translation-template.json` if source strings changed.
5. **Tests**: model/i18n (19), bridge (6), UI PyQt5/PyQt6, Krita 5.3/6.0 when possible, web 43 PASS.
6. **Screenshots/GIF**: regenerate and update `screenshots/`.
7. **ZIP**: include `grimorio_color/`, `grimorio_color.desktop`, `Manual.html`, `LICENSE`, `README.md` and `translations/`; exclude tests, `__pycache__`, `seed.personal.json`.
8. **Install test**: run `bash install.sh`, restart Krita, enable the plugin, open the docker.
9. **Public repo**: update the public tree, commit with the GitHub noreply email, push.
10. **Release**: `gh release create v<version> <zip> --title "Color Grimoire <version>" --notes-file docs/RELEASE_NOTES_<version>.md`.
11. **Announcement**: update the Krita Artists post, publish from the `ebano` account, and ask to be added to the *User-made Python Plugins* list in the Krita manual.
12. **Close**: record the real verification in the local changelog.

## Public repository

- The public repo contains the plugin, docs, tests, screenshots and translations.
- The personal web companion and earlier prototype history are not included.
- The public repo is the source of truth for releases; the ZIP is a release asset, not committed.
- The `.desktop` must be at the root of the ZIP and the `grimorio_color/` folder next to it. Krita finds `pykrita/*desktop`; it does not scan subfolders.

## Install from ZIP

1. Krita → **Tools → Scripts → Import Python Plugins**.
2. Select `grimorio_color-<version>.zip`.
3. Restart Krita.
4. **Settings → Configure Krita → Python Plugin Manager** → enable **Color Grimoire**.
5. Restart.
6. **Settings → Dockers → Color Grimoire**.

## Translations

Bundled translations live in `grimorio_color/translations/<code>.json`; user translations in `translations/` next to the JSON. User files override bundled. Test a PR by copying the file to the user folder and using **Reload translations**.

## Rollback

- Release: `gh release delete v<version> --yes` (and delete the tag if needed).
- Public repo: make it private (`gh repo edit ... --visibility private --accept-visibility-change-consequences`) or revert the commit.
- Local plugin: install the previous tree; the previous ZIP remains.
- Earlier prototype history is kept separately and is not part of the public repository.

## Notes

- The full 5.3 real run can remain pending if Krita is open and locks the resource database; the release must say so.
- Windows/macOS are untested; the ZIP is the install path.
- Android/tablet does not support PyKrita; do not advertise it.
