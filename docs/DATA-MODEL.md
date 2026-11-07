# Data model

The plugin and the web companion share one JSON state. `model.py` normalizes it on load and save.

## Schema

```json
{
  "version": 1,
  "privateMode": true,
  "activeCharacterId": "rowan",
  "characters": [
    {
      "id": "rowan",
      "name": "Rowan Vale",
      "summary": "Three lines...",
      "history": "Lore...",
      "personality": "Personality...",
      "relationships": "Relationships...",
      "tags": ["fantasy", "ranger"],
      "referenceImage": "images/oc-abc123.png",
      "zoneExamples": {
        "skin": "images/zone-skin-def456.png",
        "hair": "images/zone-hair-ghi789.png"
      },
      "palettes": {
        "skin": [
          {
            "id": "rowan-skin-1",
            "name": "Base skin",
            "hex": "#c98d6b",
            "role": "base",
            "bodyPart": "Face & body",
            "purpose": "Base skin",
            "opacity": 100,
            "note": ""
          }
        ],
        "hair": [], "eyes": [], "outfit": [], "armor": [],
        "accessories": [], "intimate": [], "scars": []
      },
      "recipe": [
        {
          "id": "rowan-layer-1",
          "name": "LINE",
          "blend": "normal",
          "opacity": 100,
          "purpose": "Clean lineart"
        }
      ],
      "environment": {
        "name": "Pine forest at dusk",
        "time": "Dusk",
        "weather": "Light fog",
        "keyLight": "#ffb36b",
        "shadowTint": "#3a2a4d",
        "bounce": "#7a4a2a",
        "mood": "Warm, damp, backlit",
        "palette": []
      }
    }
  ]
}
```

## Fields

- **State**: `version` (1), `privateMode` (bool, default `true`), `activeCharacterId`, `characters`.
- **Character**: `id`, `name`, `summary`, `history`, `personality`, `relationships`, `tags` (max 16), `referenceImage`, `zoneExamples`, `palettes`, `recipe`, `environment`.
- **Swatch**: `id`, `name`, `hex` (`#rrggbb`), `role` (`base`, `shadow`, `light`, `accent`, `detail`), `bodyPart`, `purpose`, `opacity` 0–100, `note`.
- **Layer**: `id`, `name`, `blend` (keys of `BLENDS`), `opacity` 0–100, `purpose`.
- **Environment**: `name`, `time`, `weather`, `keyLight`, `shadowTint`, `bounce`, `mood`, `palette` (environment swatches).
- **Zones**: `skin`, `hair`, `eyes`, `outfit`, `armor`, `accessories`, `intimate`, `scars`.

## Normalization

- Invalid HEX → `#808080`; short HEX expands; stored lowercase.
- `opacity` clamps to 0–100; non-numeric falls back to 100.
- Invalid `role` → `base`; invalid `blend` → `normal`.
- Empty `bodyPart` → the zone default (`Face & body`, `Hair`, etc.).
- Empty `purpose` → `note`; empty note → `""`.
- Tags deduplicate and cap at 16.
- `referenceImage`/`zoneExamples` accept only relative paths, no `..` or absolute; normalized to `/`.
- `zoneExamples` keeps known zone keys only.
- Missing environment uses defaults (`#ffb36b`, `#3a2a4d`, `#7a4a2a`).
- New OCs get the base recipe; imported OCs without a recipe keep `[]` (the UI offers “Reset base”).

## Images

- Copied into `images/` next to the JSON with a unique name (`oc-…`, `zone-…`).
- The JSON stores relative paths (`images/…`), not binaries.
- Changing/removing a photo or example deletes the previous file.
- Backup the **JSON + `images/` folder**. Importing the JSON on another machine without the folder shows placeholders; paths are preserved.
- The web companion preserves the paths in JSON but does not display the images.

## Translations

- `translations/<code>.json` with `code`, `name`, `strings` (key = Spanish source string, value = translation).
- The plugin loads bundled `grimorio_color/translations/` first, then the user `translations/`; user overrides.
- Empty values or missing keys fall back to Spanish.
- `translation-template.json` is the template and is ignored by the loader.

## Exports

- **JSON**: full state, including image and translation paths.
- **`.gpl`**: `GIMP Palette` with `R G B\tZone · Name` per swatch. With `privateMode` on, the `intimate` zone is excluded. Native `.kpl` is not implemented.
- **Print**: the web app prints the active sheet; the plugin does not print.

## Color

`model.py` provides:

- `delta_e(a, b)` CIE76 for Color Guard and comparisons.
- `blend_multiply` / `blend_add` for the scene preview.
- `lighting_spec(character)`: SHADOW (multiply), AO (multiply), LIGHT (add), GLOW (add), BOUNCE (add) using environment colors and recipe opacities.
- `scene_preview(character)`: key colors tinted by key/shadow/bounce.
- `nearest_swatch(character, hex, include_private)`: closest swatch and ΔE.

## Versioning

`version: 1`; no migrations yet. `normalize_state` fills new fields on load, so older JSON keeps working. A corrupt JSON is renamed to `.bad-<date>` and the seed is loaded.
