# Community translations

Copy `translation-template.json` to `<code>.json` (for example `fr.json`), set `code` and `name`, and translate the values in `strings`. The keys are the Spanish source strings; empty or missing values fall back to Spanish.

The plugin loads translations from this folder **and** from the user's `translations/` folder next to the JSON. The user's files override the bundled ones.

Please open a pull request with the new file. Keep the JSON valid and do not rename the keys.
