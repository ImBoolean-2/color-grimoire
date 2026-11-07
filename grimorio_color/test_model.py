# SPDX-FileCopyrightText: 2026 The Color Grimoire Authors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Pruebas del modelo puro, sin Krita ni Qt.

Ejecutar:
    python3 -m unittest test_model.py -v
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import model


class ModelTests(unittest.TestCase):
    def test_normalize_minimal_character(self):
        state = model.normalize_state({"characters": [{"name": "X"}]})
        character = state["characters"][0]
        self.assertEqual(character["name"], "X")
        self.assertEqual(len(character["palettes"]), 8)
        self.assertEqual(character["recipe"], [])
        self.assertEqual(character["environment"]["keyLight"], "#ffb36b")
        self.assertTrue(state["privateMode"])

    def test_normalize_swatch_defaults(self):
        used = set()
        swatch = model.normalize_swatch(
            {"name": "Piel base", "hex": "c98d6b", "note": "Base cálida"},
            "skin",
            used,
        )
        self.assertEqual(swatch["hex"], "#c98d6b")
        self.assertEqual(swatch["bodyPart"], "Cara y cuerpo")
        self.assertEqual(swatch["purpose"], "Base cálida")
        self.assertEqual(swatch["opacity"], 100)
        self.assertEqual(swatch["role"], "base")

    def test_normalize_swatch_clamps_opacity(self):
        swatch = model.normalize_swatch({"opacity": 250, "role": "raro"}, "eyes", set())
        self.assertEqual(swatch["opacity"], 100)
        self.assertEqual(swatch["role"], "base")

    def test_add_character_and_swatch(self):
        state = model.empty_state()
        character = model.add_character(state, "Aria", "Resumen", ["fantasía"])
        self.assertEqual(state["activeCharacterId"], character["id"])
        self.assertEqual(len(character["recipe"]), 7)
        self.assertEqual(len(character["palettes"]["skin"]), 0)

        swatch = model.add_swatch(
            character,
            "skin",
            {
                "name": "Piel base",
                "hex": "#c98d6b",
                "bodyPart": "Cara",
                "purpose": "Base de piel",
                "opacity": 85,
                "role": "base",
            },
        )
        self.assertEqual(len(character["palettes"]["skin"]), 1)
        self.assertEqual(swatch["bodyPart"], "Cara")
        self.assertEqual(swatch["opacity"], 85)

        updated = model.update_swatch(
            character,
            "skin",
            swatch["id"],
            {"name": "Piel base 2", "purpose": "Base principal", "opacity": 70},
        )
        self.assertIsNotNone(updated)
        self.assertEqual(updated["name"], "Piel base 2")
        self.assertEqual(updated["purpose"], "Base principal")
        self.assertEqual(updated["opacity"], 70)
        self.assertTrue(model.delete_swatch(character, "skin", swatch["id"]))
        self.assertEqual(len(character["palettes"]["skin"]), 0)

    def test_layer_crud_and_move(self):
        state = model.empty_state()
        character = model.add_character(state, "Aria")
        self.assertEqual(len(character["recipe"]), 7)
        first = character["recipe"][0]["name"]
        self.assertTrue(model.move_layer(character, character["recipe"][0]["id"], "down"))
        self.assertNotEqual(character["recipe"][0]["name"], first)

        layer = model.add_layer(character, {"name": "TEST", "blend": "screen", "opacity": 40})
        self.assertEqual(character["recipe"][-1]["name"], "TEST")
        self.assertEqual(layer["blend"], "screen")
        self.assertTrue(model.update_layer(character, layer["id"], {"name": "TEST 2"}))
        self.assertEqual(character["recipe"][-1]["name"], "TEST 2")
        self.assertTrue(model.delete_layer(character, layer["id"]))

        model.reset_recipe(character)
        self.assertEqual(len(character["recipe"]), 7)
        self.assertEqual(character["recipe"][0]["name"], "LINE")

    def test_gpl_excludes_and_includes_private(self):
        state = model.empty_state()
        character = model.add_character(state, "Test OC")
        model.add_swatch(character, "skin", {"name": "Base skin", "hex": "#c98d6b"})
        model.add_swatch(character, "intimate", {"name": "Private test", "hex": "#a96f5d"})
        text = model.gpl_text(character)
        self.assertTrue(text.startswith("GIMP Palette"))
        self.assertIn("Base skin", text)
        self.assertNotIn("Private test", text)
        full = model.gpl_text(character, include_private=True)
        self.assertIn("Private test", full)

        seed = model.seed_state()
        seed_character = model.active_character(seed)
        self.assertGreater(len(model.gpl_text(seed_character).strip().splitlines()), 20)
        self.assertTrue(model.gpl_filename(seed_character).endswith(".gpl"))

    def test_json_round_trip(self):
        state = model.empty_state()
        model.add_character(state, "Aria")
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "grimorio.json"
            model.save_state(state, path)
            self.assertTrue(path.exists())
            loaded = model.load_state(path)
            self.assertEqual(loaded["characters"][0]["name"], "Aria")

    def test_import_json_rejects_invalid(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.json"
            path.write_text("no es json", encoding="utf-8")
            with self.assertRaises(ValueError):
                model.import_json(path)
            path.write_text(json.dumps({"foo": []}), encoding="utf-8")
            with self.assertRaises(ValueError):
                model.import_json(path)
            path.write_text(json.dumps({"characters": [{"name": "X"}]}), encoding="utf-8")
            state = model.import_json(path)
            self.assertEqual(state["characters"][0]["name"], "X")

    def test_seed_has_two_characters_and_key_colors(self):
        state = model.seed_state()
        self.assertEqual(len(state["characters"]), 2)
        aria = model.active_character(state)
        self.assertEqual(aria["name"], "Rowan Vale")
        self.assertEqual(len(model.key_colors(aria)), 3)
        self.assertGreater(model.count_colors(aria), 20)

    def test_delta_e_and_blends(self):
        self.assertLess(model.delta_e("#c98d6b", "#c98d6b"), 0.001)
        self.assertGreater(model.delta_e("#ff0000", "#0000ff"), 50)
        self.assertEqual(model.blend_multiply("#ffffff", "#808080", 1.0), "#808080")
        self.assertEqual(model.blend_add("#000000", "#ff0000", 1.0), "#ff0000")

    def test_lighting_spec(self):
        state = model.seed_state()
        character = model.active_character(state)
        specs = model.lighting_spec(character)
        self.assertEqual([spec["name"] for spec in specs], ["SHADOW", "AO", "LIGHT", "GLOW", "BOUNCE"])
        self.assertEqual(specs[0]["color"], character["environment"]["shadowTint"])
        self.assertEqual(specs[2]["color"], character["environment"]["keyLight"])
        self.assertEqual(specs[4]["color"], character["environment"]["bounce"])
        self.assertEqual(specs[0]["blend"], "multiply")
        self.assertEqual(specs[2]["blend"], "add")
        self.assertEqual(specs[0]["opacity"], 45)
        self.assertEqual(specs[2]["opacity"], 30)

    def test_scene_preview(self):
        state = model.seed_state()
        character = model.active_character(state)
        rows = model.scene_preview(character)
        self.assertEqual(len(rows), 3)
        self.assertNotEqual(rows[0]["base"], rows[0]["shadow"])
        self.assertNotEqual(rows[0]["base"], rows[0]["light"])
        self.assertNotEqual(rows[0]["base"], rows[0]["bounce"])

    def test_nearest_swatch(self):
        state = model.empty_state()
        character = model.add_character(state, "Test")
        model.add_swatch(character, "skin", {"name": "Skin", "hex": "#c98d6b"})
        model.add_swatch(character, "hair", {"name": "Hair", "hex": "#5b3a26"})
        model.add_swatch(character, "intimate", {"name": "Private", "hex": "#a96f5d"})
        match = model.nearest_swatch(character, "#c98d6b")
        self.assertEqual(match["swatch"]["name"], "Skin")
        self.assertLess(match["delta"], 0.01)
        hidden = model.nearest_swatch(character, "#a96f5d", include_private=False)
        self.assertNotEqual(hidden["swatch"]["name"], "Private")
        visible = model.nearest_swatch(character, "#a96f5d", include_private=True)
        self.assertEqual(visible["swatch"]["name"], "Private")

    def test_image_storage_and_refs(self):
        previous = model.DATA_FILE
        with tempfile.TemporaryDirectory() as temp:
            model.DATA_FILE = Path(temp) / "grimorio.json"
            source = Path(temp) / "source.png"
            source.write_bytes(b"\x89PNG\r\n\x1a\n")
            reference = model.store_image(source, "oc")
            self.assertTrue(reference.startswith("images/"))
            self.assertIsNotNone(model.resolve_image(reference))
            state = model.normalize_state(
                {
                    "characters": [
                        {
                            "name": "X",
                            "referenceImage": reference,
                            "zoneExamples": {"skin": reference, "bad": reference},
                        }
                    ]
                }
            )
            character = state["characters"][0]
            self.assertEqual(character["referenceImage"], reference)
            self.assertEqual(character["zoneExamples"]["skin"], reference)
            self.assertNotIn("bad", character["zoneExamples"])
            self.assertEqual(model.normalize_image_ref("../secret.png"), "")
            self.assertEqual(model.normalize_image_ref("/etc/passwd"), "")
            model.remove_image(reference)
            self.assertIsNone(model.resolve_image(reference))
        model.DATA_FILE = previous

    def test_save_state_preserves_new_fields(self):
        state = model.empty_state()
        character = model.add_character(state, "Aria")
        model.add_swatch(
            character,
            "scars",
            {
                "name": "Cicatriz",
                "hex": "#d8a58e",
                "bodyPart": "Ceja izquierda",
                "purpose": "Marca vieja",
                "opacity": 60,
                "role": "accent",
            },
        )
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "grimorio.json"
            model.save_state(state, path)
            loaded = model.load_state(path)
            swatch = loaded["characters"][0]["palettes"]["scars"][0]
            self.assertEqual(swatch["bodyPart"], "Ceja izquierda")
            self.assertEqual(swatch["purpose"], "Marca vieja")
            self.assertEqual(swatch["opacity"], 60)


if __name__ == "__main__":
    unittest.main()
