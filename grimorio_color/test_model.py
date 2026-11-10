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


_FIXTURE_CANDIDATES = (
    Path(__file__).resolve().parents[1] / "test" / "fixtures",  # repo público/release
    Path(__file__).resolve().parents[2] / "test" / "fixtures",  # plugin/ en desarrollo
    Path(__file__).resolve().parent / "test" / "fixtures",
)
FIXTURES = next(
    (candidate for candidate in _FIXTURE_CANDIDATES if candidate.is_dir()),
    _FIXTURE_CANDIDATES[0],
)


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


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

    def test_head_preserved(self):
        head = {
            "version": 1,
            "generator": "loomis",
            "model": "loomis",
            "headSex": 1,
            "browRidge": 0.35,
            "eyeSocketDepth": 0.45,
            "eyeSocketSize": 0.6,
            "showEyeSocket": True,
            "cheekFullness": 0.65,
            "rotation": [1.0, 0.0, 0.0, 0.0],
            "futureKey": 123,
        }
        state = model.normalize_state({"characters": [{"name": "X", "head": head}]})
        normalized = state["characters"][0]["head"]
        self.assertEqual(normalized, head)
        self.assertIsNot(normalized, head)
        normalized["rotation"].append(0.5)
        self.assertEqual(len(head["rotation"]), 4)

    def test_head_absent_is_empty(self):
        state = model.normalize_state({"characters": [{"name": "X"}]})
        self.assertEqual(state["characters"][0]["head"], {})
        character = model.add_character(model.empty_state(), "Nuevo")
        self.assertEqual(character["head"], {})

    def test_legacy_light_keys_preserved(self):
        head = {
            "lightAzimuth": 45,
            "lightElevation": 30,
            "lightIntensity": 0.8,
            "showShadow": True,
            "shadowMode": "cast",
            "scale": 0.5,
        }
        state = model.normalize_state({"characters": [{"name": "X", "head": head}]})
        self.assertEqual(state["characters"][0]["head"], head)

    def test_state_roundtrip_preserves_head(self):
        head = {"headSex": 0, "eyeSocketDepth": 0.7, "futureKey": {"nested": [1, 2]}}
        state = model.empty_state()
        model.add_character(state, "Aria")
        state["characters"][0]["head"] = head
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "grimorio.json"
            model.save_state(state, path)
            loaded = model.load_state(path)
            imported = model.import_json(path)
        self.assertEqual(loaded["characters"][0]["head"], head)
        self.assertEqual(imported["characters"][0]["head"], head)

    def test_old_state_loads_without_loss(self):
        raw = load_fixture("state-0.4.1.json")
        state = model.normalize_state(raw)
        self.assertEqual(len(state["characters"]), 2)
        rowan = state["characters"][0]
        self.assertEqual(rowan["name"], "Rowan Vale")
        self.assertEqual(rowan["palettes"]["skin"][0]["hex"], "#c98d6b")
        self.assertEqual(len(rowan["recipe"]), 7)
        self.assertEqual(rowan["environment"]["name"], "Bosque al atardecer")
        self.assertEqual(rowan["head"], {})
        self.assertEqual(state["characters"][1]["name"], "Kai")

    def test_unknown_palette_zones_preserved(self):
        raw = load_fixture("state-custom-zone.json")
        original_sky = raw["characters"][0]["palettes"]["sky"]
        original_foliage = raw["characters"][0]["palettes"]["foliage"]
        state = model.normalize_state(raw)
        character = state["characters"][0]
        self.assertEqual(character["palettes"]["sky"], original_sky)
        self.assertEqual(character["palettes"]["foliage"], original_foliage)
        character["palettes"]["sky"].append({"hex": "#ffffff"})
        self.assertEqual(raw["characters"][0]["palettes"]["sky"], original_sky)
        character["palettes"]["sky"].pop()

        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "grimorio.json"
            model.save_state(state, path)
            loaded = model.load_state(path)
        self.assertEqual(loaded["characters"][0]["palettes"]["sky"], original_sky)
        self.assertEqual(loaded["characters"][0]["palettes"]["foliage"], original_foliage)

    def test_new_fields_do_not_touch_head(self):
        raw = load_fixture("state-loomis-0.6.0-legacy.json")
        head = raw["characters"][0]["head"]
        state = model.normalize_state(raw)
        self.assertEqual(state["characters"][0]["head"], head)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "grimorio.json"
            model.save_state(state, path)
            loaded = model.load_state(path)
        self.assertEqual(loaded["characters"][0]["head"], head)

    def test_gpl_includes_environment_and_extra_zone(self):
        state = model.normalize_state(load_fixture("state-custom-zone.json"))
        text = model.gpl_text(state["characters"][0])
        self.assertIn("sky", text)
        self.assertIn("Cielo", text)
        self.assertIn("Ambiente", text)
        self.assertIn("106 140 191", text)

    def test_count_colors_includes_environment_and_extra_zone(self):
        state = model.normalize_state(load_fixture("state-custom-zone.json"))
        self.assertEqual(model.count_colors(state["characters"][0]), 3)

    def test_key_colors_uses_extra_zone(self):
        state = model.normalize_state(load_fixture("state-custom-zone.json"))
        self.assertEqual(
            model.key_colors(state["characters"][0]),
            ["#6a8cbf", "#3f5a3a", "#3a3440"],
        )

    def test_recipe_presets(self):
        scene = model.make_recipe("scene")
        self.assertEqual([layer["name"] for layer in scene], ["SKY", "FAR", "MID", "FG", "ATMO", "FX"])
        self.assertTrue(model.make_recipe("prop"))
        character = model.add_character(model.empty_state(), "Escena")
        model.reset_recipe(character, "scene")
        self.assertEqual(character["recipe"][0]["name"], "SKY")
        model.reset_recipe(character)
        self.assertEqual(character["recipe"][0]["name"], "LINE")

    def test_environment_presets(self):
        self.assertEqual(model.ENVIRONMENT_PRESETS["sunset"]["keyLight"], "#ff9a5c")
        self.assertEqual(
            set(model.ENVIRONMENT_PRESETS),
            {"dawn", "day", "sunset", "night", "fog"},
        )

    def test_migrate_v1_to_v2(self):
        raw = load_fixture("state-0.4.1.json")
        state = model.normalize_state(raw)
        self.assertEqual(state["version"], 2)
        self.assertEqual(state["library"], [])
        character = state["characters"][0]
        self.assertEqual(character["kind"], "character")
        self.assertEqual(len(character["zones"]), 8)
        self.assertEqual([zone["key"] for zone in character["zones"]], list(model.ZONE_KEYS))
        intimate = next(zone for zone in character["zones"] if zone["key"] == "intimate")
        self.assertTrue(intimate["private"])
        self.assertEqual(len(character["environments"]), 1)
        environment = character["environments"][0]
        self.assertTrue(environment["id"].startswith("env-"))
        self.assertEqual(environment["name"], "Bosque al atardecer")
        self.assertEqual(character["activeEnvironmentId"], environment["id"])
        self.assertEqual(character["environment"], environment)
        # El JSON de entrada no se muta.
        self.assertEqual(raw["version"], 1)
        self.assertNotIn("kind", raw["characters"][0])
        self.assertNotIn("environments", raw["characters"][0])

    def test_load_state_creates_v1_backup(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "grimorio.json"
            original = (FIXTURES / "state-0.4.1.json").read_text(encoding="utf-8")
            path.write_text(original, encoding="utf-8")
            state = model.load_state(path)
            self.assertEqual(state["version"], 2)
            backup = path.with_name("grimorio.json.v1.bak")
            self.assertTrue(backup.exists())
            self.assertEqual(
                json.loads(backup.read_text(encoding="utf-8")),
                json.loads(original),
            )
            backup.write_text('{"sentinel": true}', encoding="utf-8")
            loaded = model.load_state(path)
            self.assertEqual(loaded["version"], 2)
            self.assertEqual(
                json.loads(backup.read_text(encoding="utf-8")),
                {"sentinel": True},
            )

    def test_kind_presets_and_add_character(self):
        self.assertEqual(
            [zone["key"] for zone in model.default_zones("scene")],
            ["sky", "foliage", "terrain", "water", "architecture", "props", "fx", "light"],
        )
        self.assertEqual(
            [zone["key"] for zone in model.default_zones("prop")],
            ["base", "shadow", "light", "accent", "detail"],
        )
        self.assertEqual(model.normalize_kind("SCENE"), "scene")
        self.assertEqual(model.normalize_kind("raro"), "character")
        zones = model.default_zones("scene")
        zones[0]["label"] = "Mutado"
        self.assertEqual(model.ZONE_PRESETS["scene"][0]["label"], "Cielo")

        state = model.empty_state()
        scene = model.add_character(state, "Bosque", kind="scene")
        self.assertEqual(scene["kind"], "scene")
        self.assertEqual(scene["zones"][0]["key"], "sky")
        self.assertEqual(scene["recipe"][0]["name"], "SKY")
        self.assertEqual(len(scene["environments"]), 1)
        self.assertEqual(scene["activeEnvironmentId"], scene["environments"][0]["id"])
        self.assertEqual(scene["environment"], scene["environments"][0])

        prop = model.add_character(state, "Espada", kind="prop")
        self.assertEqual(prop["kind"], "prop")
        self.assertEqual([zone["key"] for zone in prop["zones"]], [z["key"] for z in model.PROP_ZONES])
        self.assertEqual(prop["recipe"][0]["name"], "LINE")
        self.assertEqual(prop["palettes"]["base"], [])
        self.assertEqual(state["activeCharacterId"], prop["id"])

    def test_scene_zones_normalize(self):
        raw = {
            "characters": [
                {
                    "name": "Playa",
                    "kind": "scene",
                    "zones": [
                        {"key": "sky", "label": "Cielo"},
                        {"key": "sand", "label": "Arena", "defaultBody": "Terreno", "private": False},
                        {"key": "sky", "label": "Duplicada"},
                        {"label": "Sin clave"},
                        "no es dict",
                    ],
                }
            ]
        }
        state = model.normalize_state(raw)
        character = state["characters"][0]
        self.assertEqual(character["kind"], "scene")
        self.assertEqual([zone["key"] for zone in character["zones"]], ["sky", "sand"])
        self.assertEqual(character["zones"][0]["defaultBody"], "Cielo")
        self.assertFalse(character["zones"][0]["private"])
        self.assertEqual(character["zones"][1]["label"], "Arena")
        self.assertEqual(character["zones"][1]["defaultBody"], "Terreno")
        self.assertEqual(character["zones"][1]["private"], False)
        self.assertEqual(model.palette_zone_label(character, "sky"), "Cielo")
        self.assertEqual(model.palette_zone_label("sky", character["zones"]), "Cielo")
        self.assertEqual(model.palette_zone_label("sand", character["zones"]), "Arena")

        sky = model.add_swatch(character, "sky", {"name": "Cielo base", "hex": "#6a8cbf"})
        sand = model.add_swatch(character, "sand", {"name": "Arena base", "hex": "#d8b98a"})
        self.assertEqual(sky["bodyPart"], "Cielo")
        self.assertEqual(sand["bodyPart"], "Terreno")
        text = model.gpl_text(character)
        self.assertIn("Cielo · Cielo base", text)
        self.assertIn("Arena · Arena base", text)

    def test_environment_mirror_and_crud(self):
        state = model.empty_state()
        character = model.add_character(state, "Aria")
        first = character["environments"][0]
        self.assertTrue(first["id"].startswith("env-"))
        self.assertEqual(character["environment"], first)

        second = model.add_environment(character, {"name": "Noche", "keyLight": "#9ab8ff"})
        self.assertEqual(len(character["environments"]), 2)
        self.assertEqual(character["activeEnvironmentId"], second["id"])
        self.assertEqual(character["environment"]["name"], "Noche")
        self.assertEqual(character["environment"], second)

        updated = model.update_environment(character, first["id"], {"name": "Amanecer", "keyLight": "#ffd2a1"})
        self.assertIsNotNone(updated)
        self.assertEqual(updated["name"], "Amanecer")
        self.assertEqual(updated["keyLight"], "#ffd2a1")
        self.assertEqual(character["environment"]["name"], "Noche")
        self.assertIsNone(model.update_environment(character, "env-nope", {"name": "X"}))

        self.assertTrue(model.set_active_environment(character, first["id"]))
        self.assertEqual(character["activeEnvironmentId"], first["id"])
        self.assertEqual(character["environment"]["name"], "Amanecer")
        self.assertFalse(model.set_active_environment(character, "env-nope"))

        copy = model.duplicate_environment(character, second["id"])
        self.assertIsNotNone(copy)
        self.assertEqual(copy["name"], "Noche (copia)")
        self.assertNotEqual(copy["id"], second["id"])
        self.assertEqual(len(character["environments"]), 3)
        self.assertEqual(character["activeEnvironmentId"], copy["id"])
        self.assertEqual(model.active_environment(character), copy)
        self.assertEqual(character["environment"], copy)
        ids = [env["id"] for env in character["environments"]]
        self.assertEqual(len(ids), len(set(ids)))

        self.assertFalse(model.delete_environment(character, "env-nope"))
        self.assertTrue(model.delete_environment(character, copy["id"]))
        self.assertEqual(character["activeEnvironmentId"], character["environments"][0]["id"])
        self.assertEqual(character["environment"], character["environments"][0])

        while len(character["environments"]) > 1:
            self.assertTrue(model.delete_environment(character, character["environments"][-1]["id"]))
        self.assertFalse(model.delete_environment(character, character["environments"][0]["id"]))
        self.assertEqual(len(character["environments"]), 1)

    def test_divergent_environment_id_appended_once(self):
        raw = {
            "version": 2,
            "privateMode": False,
            "activeCharacterId": "oc-x",
            "characters": [
                {
                    "id": "oc-x",
                    "name": "X",
                    "kind": "character",
                    "zones": model.default_zones("character"),
                    "palettes": model.empty_palettes(model.default_zones("character")),
                    "environments": [{"id": "env-a", "name": "A", "palette": []}],
                    "activeEnvironmentId": "env-a",
                    "environment": {
                        "id": "env-b",
                        "name": "B",
                        "keyLight": "#112233",
                        "palette": [],
                    },
                    "head": {},
                }
            ],
            "library": [],
        }
        character = model.normalize_state(raw)["characters"][0]
        self.assertEqual([env["id"] for env in character["environments"]], ["env-a", "env-b"])
        self.assertEqual(character["environments"][1]["name"], "B")
        self.assertEqual(character["activeEnvironmentId"], "env-a")
        self.assertEqual(character["environment"]["id"], "env-a")

        wrapped = model.normalize_state({"characters": [character]})
        again = wrapped["characters"][0]
        self.assertEqual([env["id"] for env in again["environments"]], ["env-a", "env-b"])
        third = model.normalize_state({"characters": [again]})["characters"][0]
        self.assertEqual(len(third["environments"]), 2)

        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "grimorio.json"
            model.save_state({"characters": [third]}, path)
            loaded = model.load_state(path)
        self.assertEqual([env["id"] for env in loaded["characters"][0]["environments"]], ["env-a", "env-b"])

    def test_environment_swatch_uses_active(self):
        state = model.empty_state()
        character = model.add_character(state, "Aria")
        env_a = character["environments"][0]
        env_b = model.add_environment(character, {"name": "Noche"})
        swatch = model.add_swatch(character, "environment", {"name": "Luna", "hex": "#c8d8ff"})
        self.assertEqual(swatch["bodyPart"], "Ambiente")
        self.assertEqual(len(env_b["palette"]), 1)
        self.assertEqual(len(env_a["palette"]), 0)
        self.assertEqual(character["environment"]["palette"][0]["id"], swatch["id"])

        updated = model.update_swatch(character, "environment", swatch["id"], {"name": "Luna llena"})
        self.assertIsNotNone(updated)
        self.assertEqual(env_b["palette"][0]["name"], "Luna llena")
        self.assertEqual(character["environment"]["palette"][0]["name"], "Luna llena")
        self.assertEqual(env_a["palette"], [])

        self.assertTrue(model.delete_swatch(character, "environment", swatch["id"]))
        self.assertEqual(env_b["palette"], [])
        self.assertEqual(character["environment"]["palette"], [])
        self.assertEqual(model.count_colors(character), 0)

    def test_loomis_write_contract(self):
        head = {
            "version": "0.6.1",
            "generator": "loomis",
            "headSex": 1,
            "futureKey": {"nested": [1, 2]},
        }
        state = model.empty_state()
        character = model.add_character(state, "Ruinas", kind="scene")
        model.add_swatch(character, "sky", {"name": "Cielo", "hex": "#6a8cbf"})
        model.add_environment(character, {"name": "Noche", "keyLight": "#9ab8ff"})
        character["head"] = head
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "grimorio.json"
            model.save_state(state, path)

            # Loomis escribe solo el bloque head sobre el JSON tal cual.
            data = json.loads(path.read_text(encoding="utf-8"))
            new_head = {"version": "0.6.1", "generator": "loomis", "headSex": 0, "futureKey": 456}
            data["characters"][0]["head"] = new_head
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

            loaded = model.load_state(path)
            self.assertEqual(loaded["version"], 2)
            loaded_character = loaded["characters"][0]
            self.assertEqual(loaded_character["head"], new_head)
            self.assertEqual(loaded_character["kind"], "scene")
            self.assertEqual(len(loaded_character["zones"]), 8)
            self.assertEqual(len(loaded_character["environments"]), 2)
            self.assertEqual(
                loaded_character["activeEnvironmentId"],
                loaded_character["environments"][1]["id"],
            )

            model.save_state(loaded, path)
            reloaded = model.load_state(path)
        self.assertEqual(reloaded["characters"][0]["head"], new_head)
        self.assertEqual(reloaded["characters"][0]["kind"], "scene")
        self.assertEqual(reloaded["version"], 2)

    def test_v2_roundtrip(self):
        state = model.empty_state()
        character = model.add_character(state, "Ruinas", kind="scene")
        model.add_swatch(character, "sky", {"name": "Cielo", "hex": "#6a8cbf"})
        model.add_swatch(character, "terrain", {"name": "Tierra", "hex": "#8a6a4a"})
        model.add_environment(character, {"name": "Noche", "keyLight": "#9ab8ff"})
        head = {"generator": "loomis", "headSex": 1, "futureKey": [1, 2, 3]}
        character["head"] = head
        state["library"] = [
            {
                "id": "lib-1",
                "name": "Paleta",
                "swatches": [{"id": "libc-1", "name": "Piel", "hex": "#c98d6b"}],
            }
        ]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "grimorio.json"
            model.save_state(state, path)
            loaded = model.load_state(path)
            self.assertFalse(path.with_name("grimorio.json.v1.bak").exists())
        loaded_character = loaded["characters"][0]
        self.assertEqual(loaded["version"], 2)
        self.assertEqual(loaded["library"][0]["id"], "lib-1")
        self.assertEqual(loaded["library"][0]["swatches"][0]["hex"], "#c98d6b")
        self.assertEqual(loaded_character["kind"], "scene")
        self.assertEqual(
            [zone["key"] for zone in loaded_character["zones"]],
            [zone["key"] for zone in character["zones"]],
        )
        self.assertEqual(len(loaded_character["environments"]), 2)
        self.assertEqual(loaded_character["activeEnvironmentId"], character["activeEnvironmentId"])
        self.assertEqual(loaded_character["environment"], model.active_environment(loaded_character))
        self.assertEqual(loaded_character["head"], head)
        self.assertIsNot(loaded_character["head"], character["head"])

    def test_palette_zone_private(self):
        raw = {
            "characters": [
                {
                    "name": "Secreto",
                    "zones": [
                        {"key": "skin", "label": "Piel", "defaultBody": "Cara y cuerpo"},
                        {"key": "secret", "label": "Secreto", "defaultBody": "Otro", "private": True},
                    ],
                    "palettes": {
                        "skin": [{"name": "Piel base", "hex": "#c98d6b"}],
                        "secret": [{"name": "Marca oculta", "hex": "#ff00ff"}],
                    },
                }
            ]
        }
        character = model.normalize_state(raw)["characters"][0]
        self.assertTrue(model.palette_zone_private(character, "secret"))
        self.assertFalse(model.palette_zone_private(character, "skin"))
        self.assertIn("secret", model.palette_zone_keys(character))

        text = model.gpl_text(character)
        self.assertIn("Piel base", text)
        self.assertNotIn("Marca oculta", text)
        full = model.gpl_text(character, include_private=True)
        self.assertIn("Marca oculta", full)

        self.assertEqual(model.nearest_swatch(character, "#ff00ff")["swatch"]["name"], "Piel base")
        self.assertEqual(
            model.nearest_swatch(character, "#ff00ff", include_private=True)["swatch"]["name"],
            "Marca oculta",
        )
        self.assertNotIn("#ff00ff", model.key_colors(character))
        self.assertIn("#ff00ff", model.key_colors(character, include_private=True))

    def test_library_roundtrip(self):
        raw = {
            "version": 2,
            "characters": [{"id": "oc-aria", "name": "Aria"}],
            "library": [
                {
                    "id": "lib-skin",
                    "name": "Piel base",
                    "swatches": [
                        {
                            "id": "libc-base",
                            "name": "Base",
                            "hex": "#c98d6b",
                            "bodyPart": "Cara y cuerpo",
                        },
                        {
                            "id": "libc-shadow",
                            "name": "Sombra",
                            "hex": "#8f5a44",
                            "bodyPart": "Cara",
                        },
                    ],
                }
            ],
        }
        state = model.normalize_state(raw)
        self.assertIsInstance(state["library"], list)
        palette = state["library"][0]
        self.assertEqual(palette["id"], "lib-skin")
        self.assertEqual(palette["name"], "Piel base")
        self.assertEqual(
            [swatch["id"] for swatch in palette["swatches"]],
            ["libc-base", "libc-shadow"],
        )
        self.assertEqual(
            [swatch["name"] for swatch in palette["swatches"]],
            ["Base", "Sombra"],
        )
        self.assertEqual(
            [swatch["hex"] for swatch in palette["swatches"]],
            ["#c98d6b", "#8f5a44"],
        )
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "grimorio.json"
            model.save_state(state, path)
            loaded = model.load_state(path)
        self.assertEqual(loaded["library"], state["library"])

        # Los ids de personajes y biblioteca comparten espacio: no colisionan.
        clash = model.normalize_state(
            {
                "version": 2,
                "characters": [{"id": "lib-1", "name": "Aria"}],
                "library": [{"id": "lib-1", "name": "Otra", "swatches": []}],
            }
        )
        self.assertNotEqual(clash["library"][0]["id"], "lib-1")

    def test_library_add_from_zone_and_import(self):
        state = model.empty_state()
        character = model.add_character(state, "Aria")
        skin = model.add_swatch(character, "skin", {"name": "Piel base", "hex": "#c98d6b"})
        shadow = model.add_swatch(
            character,
            "skin",
            {"name": "Sombra piel", "hex": "#8f5a44", "bodyPart": "Cara"},
        )
        palette = model.library_add_from_zone(state, character, "skin")
        self.assertEqual(palette["name"], "Aria · Piel")
        self.assertEqual(len(palette["swatches"]), 2)
        self.assertEqual(state["library"], [palette])
        source_ids = {skin["id"], shadow["id"]}
        library_ids = {swatch["id"] for swatch in palette["swatches"]}
        self.assertEqual(len(library_ids), 2)
        self.assertFalse(source_ids & library_ids)
        self.assertEqual(
            [swatch["bodyPart"] for swatch in palette["swatches"]],
            ["Cara y cuerpo", "Cara"],
        )

        other = model.add_library_palette(state, "Otra", [{"name": "Dup", "hex": "#ffffff"}])
        self.assertNotEqual(other["id"], palette["id"])
        self.assertFalse({other["swatches"][0]["id"]} & library_ids)

        hair = model.import_library_palette(character, "hair", palette)
        self.assertEqual(len(hair), 2)
        self.assertEqual([swatch["bodyPart"] for swatch in hair], ["Cara y cuerpo", "Cara"])
        hair_ids = {swatch["id"] for swatch in hair}
        self.assertFalse(hair_ids & source_ids)
        self.assertFalse(hair_ids & library_ids)

        environment = model.import_library_palette(character, "environment", palette)
        self.assertEqual(len(environment), 2)
        env_ids = {swatch["id"] for swatch in environment}
        self.assertFalse(env_ids & source_ids)
        self.assertFalse(env_ids & library_ids)
        self.assertFalse(env_ids & hair_ids)
        self.assertTrue(all(swatch["bodyPart"] for swatch in environment))
        self.assertEqual(character["environments"][0]["palette"], environment)
        self.assertEqual(character["environment"]["palette"], environment)

    def test_library_rename_delete(self):
        state = model.empty_state()
        first = model.add_library_palette(state, "Primera", [{"name": "Uno", "hex": "#112233"}])
        second = model.add_library_palette(state, "Segunda", [{"name": "Dos", "hex": "#445566"}])
        renamed = model.rename_library_palette(state, first["id"], "Primera 2")
        self.assertIsNotNone(renamed)
        self.assertEqual(renamed["name"], "Primera 2")
        self.assertIsNone(model.rename_library_palette(state, "lib-nope", "X"))

        self.assertTrue(model.delete_library_palette(state, first["id"]))
        self.assertEqual([palette["id"] for palette in state["library"]], [second["id"]])
        self.assertFalse(model.delete_library_palette(state, first["id"]))
        self.assertEqual(len(state["library"]), 1)
        self.assertEqual(state["library"][0]["swatches"][0]["hex"], "#445566")

        model.rename_library_palette(state, second["id"], "   ")
        self.assertEqual(state["library"][0]["name"], "Paleta sin nombre")

    def test_zone_crud_reorder_and_delete_keeps_palette(self):
        state = model.empty_state()
        character = model.add_character(state, "Aria")
        zone = model.add_zone(character, "sky", "Cielo", "Cielo")
        self.assertIsNotNone(zone)
        self.assertEqual(zone["key"], "sky")
        self.assertEqual(zone["label"], "Cielo")
        self.assertEqual(zone["defaultBody"], "Cielo")
        self.assertFalse(zone["private"])
        self.assertIsNone(model.add_zone(character, "sky"))
        self.assertIn("sky", character["palettes"])

        swatch = model.add_swatch(character, "sky", {"name": "Azul", "hex": "#6a8cbf"})
        updated = model.update_zone(
            character, "sky", {"label": "Cielo alto", "defaultBody": "Cielo", "private": True}
        )
        self.assertIsNotNone(updated)
        self.assertEqual(updated["key"], "sky")
        self.assertEqual(updated["label"], "Cielo alto")
        self.assertTrue(model.palette_zone_private(character, "sky"))
        self.assertIsNone(model.update_zone(character, "nope", {"label": "X"}))

        order = [item["key"] for item in character["zones"]]
        self.assertEqual(order[-1], "sky")
        self.assertTrue(model.move_zone(character, "sky", "up"))
        self.assertEqual([item["key"] for item in character["zones"]][-2], "sky")
        self.assertTrue(model.move_zone(character, "sky", "down"))
        self.assertEqual([item["key"] for item in character["zones"]], order)
        self.assertFalse(model.move_zone(character, "sky", "down"))
        self.assertFalse(model.move_zone(character, "nope", "up"))

        self.assertTrue(model.delete_zone(character, "sky"))
        self.assertNotIn("sky", [item["key"] for item in character["zones"]])
        # La paleta sobrevive como extra opaco y se exporta.
        self.assertEqual(character["palettes"]["sky"], [swatch])
        self.assertIn("sky", model.palette_zone_keys(character))
        self.assertIn("Azul", model.gpl_text(character))
        self.assertFalse(model.delete_zone(character, "sky"))

        while len(character["zones"]) > 1:
            self.assertTrue(model.delete_zone(character, character["zones"][-1]["key"]))
        self.assertFalse(model.delete_zone(character, character["zones"][0]["key"]))

    def test_zone_private_in_gpl(self):
        state = model.empty_state()
        character = model.add_character(state, "Aria")
        zone = model.add_zone(character, "secret", "Secreto", "Otro", private=True)
        self.assertIsNotNone(zone)
        self.assertTrue(model.palette_zone_private(character, "secret"))
        model.add_swatch(character, "secret", {"name": "Marca oculta", "hex": "#ff00ff"})

        text = model.gpl_text(character)
        self.assertNotIn("Marca oculta", text)
        full = model.gpl_text(character, include_private=True)
        self.assertIn("Marca oculta", full)
        self.assertIn("Secreto", full)

    def test_backup_timestamped_when_stale(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "grimorio.json"
            raw = load_fixture("state-0.4.1.json")
            path.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
            model.load_state(path)

            standard = path.with_name("grimorio.json.v1.bak")
            self.assertTrue(standard.exists())
            self.assertEqual(
                json.loads(standard.read_text(encoding="utf-8"))["characters"][0]["name"],
                "Rowan Vale",
            )

            raw["characters"][0]["name"] = "Rowan Nuevo"
            path.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
            model.load_state(path)
            backups = sorted(path.parent.glob("grimorio.json.v1-*.bak"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(
                json.loads(backups[0].read_text(encoding="utf-8"))["characters"][0]["name"],
                "Rowan Nuevo",
            )

            model.load_state(path)
            self.assertEqual(
                len(sorted(path.parent.glob("grimorio.json.v1-*.bak"))),
                1,
            )
            self.assertEqual(
                json.loads(standard.read_text(encoding="utf-8"))["characters"][0]["name"],
                "Rowan Vale",
            )

    def test_library_v1_empty(self):
        state = model.normalize_state(load_fixture("state-0.4.1.json"))
        self.assertEqual(state["library"], [])


if __name__ == "__main__":
    unittest.main()
