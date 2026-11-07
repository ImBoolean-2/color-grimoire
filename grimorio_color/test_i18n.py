# SPDX-FileCopyrightText: 2026 The Color Grimoire Authors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Pruebas de las traducciones personalizadas."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import i18n


class TranslationTests(unittest.TestCase):
    def tearDown(self):
        i18n.CUSTOM.clear()
        i18n.CUSTOM_NAMES.clear()
        i18n.set_language("en")

    def test_builtin_languages(self):
        i18n.set_language("en")
        self.assertEqual(i18n.tr("Ficha"), "Sheet")
        i18n.set_language("es")
        self.assertEqual(i18n.tr("Ficha"), "Ficha")

    def test_custom_language_and_fallback(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            (path / "fr.json").write_text(
                json.dumps(
                    {
                        "code": "fr",
                        "name": "Français",
                        "strings": {"Ficha": "Fiche", "Paletas": "Palettes"},
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            languages = i18n.load_translations(path)
            self.assertIn(("fr", "Français"), languages)
            i18n.set_language("fr")
            self.assertEqual(i18n.tr("Ficha"), "Fiche")
            self.assertEqual(i18n.tr("Paletas"), "Palettes")
            # Sin traducción, cae al español fuente.
            self.assertEqual(i18n.tr("Capas"), "Capas")

    def test_bundled_and_user_override(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            bundled = root / "bundled"
            user = root / "user"
            bundled.mkdir()
            user.mkdir()
            (bundled / "fr.json").write_text(
                json.dumps(
                    {
                        "code": "fr",
                        "name": "Français",
                        "strings": {"Ficha": "Fiche"},
                    }
                ),
                encoding="utf-8",
            )
            (user / "fr.json").write_text(
                json.dumps(
                    {
                        "code": "fr",
                        "name": "Français",
                        "strings": {"Ficha": "Fiche utilisateur"},
                    }
                ),
                encoding="utf-8",
            )
            i18n.load_translations(user, extra_directories=[bundled])
            i18n.set_language("fr")
            self.assertEqual(i18n.tr("Ficha"), "Fiche utilisateur")
            self.assertEqual(i18n.tr("Paletas"), "Paletas")

    def test_template_and_readme(self):
        with tempfile.TemporaryDirectory() as temp:
            path = i18n.ensure_translations_dir(temp)
            template = path / "translation-template.json"
            self.assertTrue(template.exists())
            self.assertTrue((path / "README.txt").exists())
            data = json.loads(template.read_text(encoding="utf-8"))
            self.assertEqual(data["code"], "xx")
            self.assertIn("Ficha", data["strings"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
