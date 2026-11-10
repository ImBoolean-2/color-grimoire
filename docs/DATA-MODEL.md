# Data model

The plugin and the web companion share one JSON state. `model.py` normalizes it on load and save; unknown fields survive only where normalization accounts for them.

Since **0.6.0** the schema is **v2**: it adds `kind`, `zones`, `environments` and `activeEnvironmentId`, and keeps `environment` as a mirror of the active environment. **0.7.0** adds the palette library (`library`) and the zone editor and stays on v2. A **v1** file is migrated automatically on load; see [Migration and backup](#migration-and-backup).

## Schema v2

```json
{
  "version": 2,
  "privateMode": true,
  "activeCharacterId": "oc-rowan",
  "characters": [
    {
      "id": "oc-rowan",
      "name": "Rowan Vale",
      "kind": "character",
      "zones": [
        {"key": "skin", "label": "Skin", "defaultBody": "Face & body", "private": false},
        {"key": "hair", "label": "Hair", "defaultBody": "Hair", "private": false}
      ],
      "palettes": {
        "skin": [],
        "hair": [],
        "sky": []
      },
      "recipe": [],
      "environment": {
        "id": "env-1",
        "name": "Forest at dusk",
        "time": "Dusk",
        "weather": "Fog",
        "keyLight": "#ffb36b",
        "shadowTint": "#3a2a4d",
        "bounce": "#7a4a2a",
        "mood": "Warm",
        "palette": []
      },
      "environments": [
        {
          "id": "env-1",
          "name": "Forest at dusk",
          "time": "Dusk",
          "weather": "Fog",
          "keyLight": "#ffb36b",
          "shadowTint": "#3a2a4d",
          "bounce": "#7a4a2a",
          "mood": "Warm",
          "palette": []
        }
      ],
      "activeEnvironmentId": "env-1",
      "head": {}
    }
  ],
  "library": []
}
```

`zones` may hold the 8 character zones, the 8 scene zones (`sky`, `foliage`, `terrain`, `water`, `architecture`, `props`, `fx`, `light`) or the 5 prop zones (`base`, `shadow`, `light`, `accent`, `detail`). The example abbreviates them. `palettes` may keep extra keys such as `sky` even when they are not in `zones`; those keys behave as an opaque block.

## Fields

- **State**: `version` (2), `privateMode` (bool, default `true`), `activeCharacterId`, `characters`, `library`.
- **Project**: `id`, `name`, `kind`, `zones`, `palettes`, `recipe`, `environment`, `environments`, `activeEnvironmentId`, `head`, plus the sheet fields (`summary`, `history`, `personality`, `relationships`, `tags`, `referenceImage`, `zoneExamples`).
- **`kind`**: `character` (default), `scene` or `prop`. It defines the starter zones and recipe.
- **`zones`**: list of `{key, label, defaultBody, private}`. A missing list falls back to the 8 character zones; a scene uses 8 scene zones; a prop uses 5. `private: true` hides the zone while private mode is on.
- **Zone editor**: `add_zone`, `update_zone`, `move_zone` and `delete_zone`. `key` is stable; renaming changes only `label`/`defaultBody`. Deleting a zone does **not** delete `palettes[key]`: the palette stays as an opaque extra, visible in `.gpl` and color counts, hidden from the editor.
- **`palettes`**: object keyed by zone key. Keys outside `zones` are preserved as an opaque block (for example `sky` on a character).
- **`library`**: list of reusable `{id, name, swatches}` palettes. Importing into a zone **copies** the swatches with new ids; there are no cross-project references. A library swatch without `bodyPart` falls back to `Other`.
- **`environments`**: list of environments, each with a stable `id`. `activeEnvironmentId` selects one. On save, `environment` is synchronized with the active entry.
- **`environment`**: mirror of the active environment, with the same `id` and contents; it exists for v1 readers.
- **`head`**: opaque block written by the Loomis Head Guide plugin. Grimoire does not interpret, validate, rename or filter it: it deep-copies every key, known or unknown, so it survives JSON export/import and saves from the docker. New Loomis keys need no change in Grimoire. Do not edit it by hand.
- **Swatch**: `id`, `name`, `hex` (`#rrggbb`), `role` (`base`, `shadow`, `light`, `accent`, `detail`), `bodyPart`, `purpose`, `opacity` 0–100, `note`.
- **Layer**: `id`, `name`, `blend` (keys of `BLENDS`), `opacity` 0–100, `purpose`.
- **Environment**: `id`, `name`, `time`, `weather`, `keyLight`, `shadowTint`, `bounce`, `mood`, `palette` (environment swatches).
- **Zone presets**: character `skin`, `hair`, `eyes`, `outfit`, `armor`, `accessories`, `intimate`, `scars`; scene `sky`, `foliage`, `terrain`, `water`, `architecture`, `props`, `fx`, `light`; prop `base`, `shadow`, `light`, `accent`, `detail`.

## Normalization

- Invalid HEX → `#808080`; short HEX expands; stored lowercase.
- `opacity` clamps to 0–100; non-numeric values fall back to 100.
- Invalid `role` → `base`; invalid `blend` → `normal`.
- Empty `bodyPart` → the zone default (`Face & body`, `Hair`, etc.); empty library swatch → `Other`.
- Empty `purpose` → `note`; empty note → `""`.
- Tags deduplicate and cap at 16.
- `referenceImage`/`zoneExamples` accept only relative paths, no `..` or absolute; normalized to `/`.
- `zoneExamples` keeps only keys of the project zones.
- Missing `environment` uses the defaults (`#ffb36b`, `#3a2a4d`, `#7a4a2a`); missing `environments` is built from `environment`.
- A new project receives the zones and recipe of its `kind`; an imported project without a recipe keeps `[]` (the UI offers “Reset base”).
- Library swatches normalize like any color (`id`, `name`, `hex`, `role`, `bodyPart`, `purpose`, `opacity`, `note`); library and project ids share one space to avoid collisions.

## Migration and backup

- **v1 → v2**: loading a file with `version: 1` creates `grimorio.json.v1.bak` once, then normalizes to v2 (`kind: "character"`, 8 zones, one environment built from the old `environment`).
- **Stale standard backup**: if `grimorio.json.v1.bak` already exists and the v1 file changed since, the plugin writes `grimorio.json.v1-<date>.bak` before migrating. Repeated loads do not duplicate it.
- **Web**: the web app stores a one-time `grimorio-color:v1-backup` key in `localStorage` before converting to v2.
- **Restore**: close Krita, replace `grimorio.json` with the `.v1.bak` copy, keep the `images/` folder, reopen. The next load migrates it again.
- **Downgrade**: not supported (0.5/0.4 cannot read v2). The backup is the safety net.
- A corrupt JSON is renamed to `.bad-<date>` and the seed is loaded.

## Images

- Copied into `images/` next to the JSON with a unique name (`oc-…`, `zone-…`).
- The JSON stores relative paths (`images/…`), not binaries.
- Changing/removing a photo or example deletes the previous file.
- Back up the **JSON + `images/` folder**. Importing the JSON on another machine without the folder shows placeholders; paths are preserved.
- The web companion preserves the paths in JSON but does not display the images.

## Translations

- `translations/<code>.json` with `code`, `name`, `strings` (key = Spanish source string, value = translation).
- The plugin loads bundled `grimorio_color/translations/` first, then the user `translations/`; user files override.
- Empty values or missing keys fall back to Spanish.
- `translation-template.json` is the template and is ignored by the loader.

## Exports

- **JSON**: full state, including image and translation paths.
- **`.gpl`**: `GIMP Palette` with `R G B\tZone · Name` per swatch. The active environment palette is appended as `Environment · <name>`. With `privateMode` on, zones marked `private` are excluded. Native `.kpl` is not implemented.
- **Print**: the web app prints the active sheet; the plugin does not print.

## Color

`model.py` provides:

- `delta_e(a, b)` CIE76 for Color Guard and comparisons.
- `blend_multiply` / `blend_add` for the scene preview.
- `lighting_spec(character)`: SHADOW (multiply), AO (multiply), LIGHT (add), GLOW (add), BOUNCE (add) using the active environment colors and the recipe opacities.
- `scene_preview(character)`: key colors tinted by key/shadow/bounce.
- `nearest_swatch(character, hex, include_private)`: closest swatch and ΔE.

## Versioning

`version: 2`. v1 files are migrated on load; v2 files are normalized field by field, so a state written by a newer patch release keeps working. A corrupt JSON is renamed to `.bad-<date>` and the seed is loaded.
